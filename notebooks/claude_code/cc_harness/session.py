"""통합 Session — CC 에이전트 루프 1턴 사이클의 척추.

    사용자 질문
       ↓ [유저턴 리마인더 수집·주입]                    (reminders)
    ┌─ 사이클 반복 ──────────────────────────────────┐
    │ [전처리 ① applyToolResultBudget]                (context)
    │ [MCP 델타 고지 flush]                           (mcp)
    │ thinking — input = [developer] + [유령] + history
    │ [스마트 배치: partition → 배치 간 직렬·내 병렬]  (scheduling)
    │   각 호출 → [파이프라인 1·2·6·7·8]              (pipeline)
    │ [인루프 리마인더 수집 → smoosh/별도 메시지]      (reminders)
    └─ function_call 0개 → 최종 답변 ────────────────┘

각 화살표가 곧 모듈 경계다. 어느 장치든 HarnessConfig 플래그로 끄면
해당 cc_* 노트북 이전의 조건이 재현된다.

캐시 계약: tools 배열은 freeze_tools로 동결(이름순·세션 내 불변),
전처리·smoosh는 '직전 사이클 fresh 묶음'만 건드림 → 안정 프리픽스 불변.
"""

import dataclasses
import json
import time

from . import prompts, schemas
from .config import MODEL, HarnessConfig, get_client
from .context import ContextBudget
from .fs_tools import FsTools
from .mcp import MCPRegistry
from .metrics import UsageLog
from .pipeline import Pipeline, ToolRecord, map_bash_result
from .registry import from_openai_schema
from .reminders import (SIDE_QUESTION_TEMPLATE, SR, ReminderPipeline, deliver,
                        ghost_message, neutralize)
from .scheduling import execute_batches
from .state import World
from .toolsearch import handle_tool_invoke, handle_tool_search, registry_notice


def _is_error(output):
    return output.startswith("ERROR") or output.startswith("<tool_use_error>")


class Session:
    """최종 미니 하네스 세션 — World(목 환경)·도구·루프 장치를 전부 소유한다."""

    def __init__(self, config=None, **overrides):
        if config is None:
            config = HarnessConfig(**overrides)
        elif overrides:
            config = dataclasses.replace(config, **overrides)
        cfg = self.cfg = config
        self.model = cfg.model or MODEL

        self.world = World()
        self.fs = FsTools(self.world, nudges=cfg.nudges, gates=cfg.hard_gates,
                          inline_sr=cfg.inline_sr, track_rules=cfg.reminders)
        self.mcp = MCPRegistry() if cfg.mcp else None
        self.search_state = {"discovered": set(), "search_events": []}

        self.records = self._build_records()
        # tools 동결 — 세션 내내 불변 (OpenAI 캐시는 exact prefix match)
        self.tools = schemas.freeze_tools([r.definition for r in self.records.values()])
        self.pipeline = (Pipeline(self.records, permission_mode=cfg.permission_mode,
                                  trace=cfg.trace_pipeline)
                         if cfg.pipeline else None)
        self.reminders = ReminderPipeline(self.world) if cfg.reminders else None
        self.context = ContextBudget(self.world, mode=cfg.preprocess) if cfg.preprocess else None
        self.usage = UsageLog() if cfg.track_cache else None

        self.system_prompt = self._build_system_prompt()
        self.history = []              # 유령 메시지는 여기 저장되지 않는다 (매 호출 재생성)
        self.turn = 0
        self.round_no = 0
        self.prev_round_outputs = []   # 직전 사이클 묶음 = 다음 전처리 대상

    # ── 구성 ───────────────────────────────────────────────────────
    def _build_records(self):
        cfg = self.cfg
        fs = self.fs
        records = {}

        def add(definition, impl, **kw):
            records[definition["name"]] = ToolRecord(definition=definition, impl=impl, **kw)

        # 파일시스템 도구 5종 — 게이트·넛지·인라인 SR은 FsTools 스위치가 담당.
        # 2단계 값 체크(validator)는 하드 게이트를 파이프라인 자리에서도 보여주는 선행 검사 —
        # 구현 내부 게이트가 백스톱이라 어느 쪽이 먼저 걸려도 같은 CC 원문 에러가 나간다.
        add(schemas.glob_tool(cfg.dispatcher), fs.glob_files,
            read_only=True, concurrency_safe=True)
        add(schemas.grep_tool(cfg.dispatcher), fs.grep_files,
            read_only=True, concurrency_safe=True)
        add(schemas.read_tool(cfg.hard_gates), fs.read_file,
            read_only=True, concurrency_safe=True)
        add(schemas.edit_tool(cfg.hard_gates), fs.edit_file,
            validator=self._edit_validator if cfg.hard_gates else None,
            concurrency_safe=False)  # 기본값 false — "assume not safe" (Tool.ts:757-760)
        add(schemas.write_tool(cfg.hard_gates), fs.write_file,
            validator=self._write_validator if cfg.hard_gates else None,
            concurrency_safe=False)

        if cfg.shell_tool:
            # CC Bash 대응 — 구조체 반환 + 8단계 자체 한도 매퍼 + 조건부 동시성 판정
            add(schemas.run_command_tool(), fs.run_command,
                mapper=map_bash_result, concurrency_safe=fs.command_is_read_only)

        if cfg.dispatcher:
            add(schemas.tool_search_def(mcp=cfg.mcp), self._tool_search_impl,
                read_only=True, concurrency_safe=True)
            add(schemas.tool_invoke_def(), self._tool_invoke_impl,
                concurrency_safe=False)  # 무엇이든 실행 가능 → 보수적 단독

        return records

    def _base_deferred(self):
        # 하네스 내장 디퍼드 도구 — tools 배열에 안 실리고 레지스트리에만 (이름만 고지)
        return {
            "agent_search": from_openai_schema(schemas.AGENT_SEARCH_TOOL, self.fs.agent_search,
                                               hint="검색 조사 자율 에이전트 탐색 리서치"),
            "todo_write": from_openai_schema(schemas.TODO_WRITE_TOOL, self.fs.todo_write,
                                             hint="할일 태스크 진행 상황 추적 todo"),
        }

    def _deferred_registry(self):
        reg = self._base_deferred()
        if self.mcp:
            reg.update(self.mcp.visible())  # 연결된 MCP 서버의 도구만 검색에 노출
        return reg

    def _build_system_prompt(self):
        # `# 도구 사용 정책` 하위 섹션 순서: 레지스트리 고지 → 위임 → 할일
        # (도구를 소개하는 섹션이 그 도구를 쓰는 정책보다 앞에 오도록)
        policy = []
        if self.cfg.dispatcher:
            policy.append(registry_notice(list(self._base_deferred())))
            policy.append(prompts.DELEGATION_POLICY)
        if self.cfg.todo_mode:
            policy.append(prompts.TODO_SYSTEM_EXTRA)
        return prompts.build_system_prompt(*policy)

    # ── 2단계 값 체크 (validateInput) — 하드 게이트가 파이프라인 자리에 앉는다 ──
    def _edit_validator(self, args):
        # 하드 원본의 검사 순서 보존: old==new 검사 → 게이트1/2 (동시 해당 시 old==new가 우선)
        if args.get("old_string") == args.get("new_string"):
            return "바꿀 내용이 없습니다: old_string과 new_string이 완전히 동일합니다."
        if args.get("file_path") in self.world.fs:
            return self.fs._write_gates(args["file_path"])
        return None

    def _write_validator(self, args):
        fp = args.get("file_path")
        if fp in self.world.fs:
            gate = self.fs._write_gates(fp)
            if gate:
                return gate
            if self.world.fs[fp]["content"] == args.get("content"):
                # 원본 파이프라인 validate_write_note의 동일내용 검사 이식
                return "기존 내용과 동일함 — 변경사항 없음."
        return None

    # ── 디스패처 구현 (tool_search / tool_invoke 레코드의 impl) ────
    def _tool_search_impl(self, query=""):
        connected = list(self.mcp.connected) if self.mcp else None
        return handle_tool_search(query, self._deferred_registry(), self.search_state, connected)

    def _tool_invoke_impl(self, name="", arguments=None):
        all_pool = self.mcp.all_pool if self.mcp else None
        return handle_tool_invoke(name, arguments or {}, self._deferred_registry(),
                                  self.search_state, all_pool)

    # ── MCP 연결/해제 (모델 고지는 다음 수집 지점의 델타가 담당) ───
    def mcp_connect(self, server):
        assert self.mcp is not None, "HarnessConfig(mcp=True)로 세션을 만들어야 합니다"
        self.mcp.connect(server)

    def mcp_disconnect(self, server):
        assert self.mcp is not None, "HarnessConfig(mcp=True)로 세션을 만들어야 합니다"
        self.mcp.disconnect(server)

    # ── 호출 1건 실행 (스케줄러의 run_fn) ──────────────────────────
    def _safety_of(self, name):
        rec = self.records.get(name)
        return (lambda args, _r=rec: _r.is_safe(args)) if rec else None

    def _run_call(self, call):
        label = call.name
        try:
            args = json.loads(call.arguments)
        except (json.JSONDecodeError, TypeError):
            args = None
        if call.name == "tool_invoke" and isinstance(args, dict):
            label = f"tool_invoke→{args.get('name') or '?'}"

        if call.name not in self.records and call.name in self._deferred_registry():
            # 레지스트리 도구 직접 호출 거부 — 원본 dispatch의 반응형 힌트 보존
            return {"label": label, "args": args,
                    "output": f"ERROR: '{call.name}'은 직접 호출할 수 없습니다. tool_invoke를 사용하세요."}

        if self.pipeline:
            output = self.pipeline.run(call.name, call.arguments)
        else:
            # 파이프라인 off — 직접 실행 (멀티 함수콜 베이스라인 경로)
            rec = self.records.get(call.name)
            if rec is None:
                output = f"ERROR: 알 수 없는 도구 '{call.name}'"
            elif args is None:
                output = "ERROR: 잘못된 인자입니다. 도구 스키마에 맞춰 다시 호출하세요."
            else:
                try:
                    output = rec.map_result(rec.impl(**args))
                except TypeError as e:
                    # 인자 검증 게이트 — 검증 실패도 에러 tool_result로 돌려 자기교정
                    output = f"ERROR: 잘못된 인자입니다. 도구 스키마에 맞춰 다시 호출하세요. ({e})"
                except Exception as e:
                    output = f"ERROR: 실행 실패: {e}"
        return {"label": label, "output": output, "args": args}

    # ── 메인 루프 ──────────────────────────────────────────────────
    def ask(self, question, max_rounds=None):
        cfg = self.cfg
        max_rounds = max_rounds or cfg.max_rounds
        print(f"💬 {question}\n")
        self.turn += 1
        if cfg.spoof_guard:
            question = neutralize(question)              # 스푸핑 방어
        if self.mcp:
            # MCP 델타 — 턴 시작 수집 지점: 델타가 유저 메시지보다 '먼저' 실린다 (CC·원본 순서 보존)
            delta = self.mcp.delta_message(self.history)
            if delta:
                self.history.append(delta)
        self.history.append({"role": "user", "content": question})
        if self.reminders:                               # 주입 지점 1 — 유저 턴 엔트리
            deliver(self.history, self.reminders.collect_user_turn(question), "user_turn")

        cycle = 0
        for _ in range(max_rounds):
            cycle += 1
            self.round_no += 1

            # [사이클 맨 위] 전처리 ① — 직전 사이클 fresh 묶음만 in-place 정리
            offloaded = self.context.apply(self.prev_round_outputs) if self.context else 0
            # MCP 델타 고지 — 인루프 수집 지점(케이스 B): 미드턴 connect/disconnect 커버 (query.ts:1569)
            if self.mcp:
                delta = self.mcp.delta_message(self.history)
                if delta:
                    self.history.append(delta)

            # 유령 메시지는 매 호출 재생성 — 이력이 아니라 '매번 다시 인쇄되는 표지'
            input_list = [{"role": "developer", "content": self.system_prompt}]
            if cfg.ghost:
                input_list.append(ghost_message(self.world))
            input_list += self.history

            if self.usage:
                self.usage.snapshot(input_list, offloaded=offloaded)
            api_kwargs = {}
            if cfg.prompt_cache_key:
                api_kwargs["prompt_cache_key"] = cfg.prompt_cache_key
            start = time.perf_counter()
            response = get_client().responses.create(
                model=self.model, input=input_list, tools=self.tools, **api_kwargs)
            if self.usage:
                self.usage.record(response, time.perf_counter() - start, turn=self.turn)

            self.history += response.output
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                print(f"═══ 사이클 {cycle} (모델 호출 #{cycle}) ═══  function_call 0개 → 최종 답변")
                print(f"\n🤖 {response.output_text}")
                return response.output_text
            print(f"═══ 사이클 {cycle} (모델 호출 #{cycle}) ═══  "
                  f"function_call {len(calls)}개{' 병렬' if len(calls) > 1 else ''}")

            # 스마트 배치: 파티션 → 배치 간 직렬·배치 내 병렬. 결과는 emit 순서로 방출.
            if cfg.scheduling and len(calls) > 1:
                results = execute_batches(calls, self._run_call, self._safety_of,
                                          trace=cfg.trace_scheduling)
                for r, c in zip(results, calls):
                    r.setdefault("call", c)
            else:
                results = []
                for c in calls:  # 받은 순서대로 순차 실행
                    r = self._run_call(c)
                    r["call"] = c
                    results.append(r)

            used_todo = False
            invoked = []
            fresh = []
            for r in results:  # emit 순서 그대로 function_call_output 추가
                call, output, args = r["call"], r["output"], r["args"]
                mark = "⛔" if _is_error(output) else "🔧"
                head = output.splitlines()[0] if output else ""
                print(f"  {mark} {r['label']}({(call.arguments or '')[:100]})")
                print(f"     → {head[:140]}{' …' if len(output) > len(head) else ''}")
                item = {"type": "function_call_output", "call_id": call.call_id, "output": output}
                self.history.append(item)
                fresh.append(item)
                if self.context:
                    self.context.note_call(call.call_id, call.name, args, self.round_no)
                target = (args.get("name") if call.name == "tool_invoke" and isinstance(args, dict)
                          else call.name)
                if call.name == "tool_invoke":
                    invoked.append("실행:" + str(target or "?"))
                if target == "todo_write" and not _is_error(output):
                    used_todo = True
            self.prev_round_outputs = fresh

            # search_events는 계측 여부와 무관하게 매 라운드 드레인 (무한 적립 방지)
            events = self.search_state.get("search_events", []) + invoked
            self.search_state["search_events"] = []
            if self.usage:
                self.usage.note_events(events)

            if self.reminders:                           # 주입 지점 2 — 툴 라운드 꼬리
                self.reminders.note_round(used_todo)
                deliver(self.history, self.reminders.collect_in_loop(), "in_loop")

        print("⚠️ 최대 라운드 초과 — 데모를 여기서 멈춥니다.")
        return None

    # ── 사이드 질문 — 비-어태치먼트 ⑤ (CC sideQuestion.ts:61) ──────
    def side_question(self, question):
        print(f"💬 (사이드 질문) {question}\n")
        body = SIDE_QUESTION_TEMPLATE.format(question=neutralize(question))
        input_list = [{"role": "developer", "content": self.system_prompt}]
        if self.cfg.ghost:
            input_list.append(ghost_message(self.world))
        input_list += self.history + [{"role": "user", "content": SR(body)}]
        # tool_choice="none" — 사이드 질문은 도구 없이 한 번의 응답으로
        response = get_client().responses.create(model=self.model, input=input_list,
                                                 tools=self.tools, tool_choice="none")
        print(f"🤖 {response.output_text}")
        return response.output_text

    # ── 상태 요약 ──────────────────────────────────────────────────
    def describe(self):
        cfg = self.cfg
        flags = {f.name: getattr(cfg, f.name) for f in dataclasses.fields(cfg)}
        print(f"cc_harness Session — model={self.model}")
        print("  config:", json.dumps(flags, ensure_ascii=False, default=str))
        print(f"  동결 tools({len(self.tools)}):", [t["name"] for t in self.tools])
        if cfg.dispatcher:
            print(f"  디퍼드 레지스트리({len(self._deferred_registry())}):",
                  list(self._deferred_registry()))
        print(f"  시스템 프롬프트 {len(self.system_prompt)}자 · 목 FS {len(self.world.fs)}파일")
