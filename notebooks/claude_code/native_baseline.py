"""비교 베이스라인 — '그냥 네이티브 펑션콜링' 세션 (하네스 장치 0개).

cc_harness.Session과의 공정 비교가 목적이라 재료는 전부 같은 것을 쓴다:
같은 World(목 FS·목 환경), 같은 도구 구현(FsTools — 넛지·게이트·인라인SR 전부 OFF),
같은 계측(UsageLog), 같은 모델. 다른 것은 루프 설계뿐이다.

네이티브 설계 (흔한 순정 구현 방식 그대로):
- 오늘 날짜·프로젝트 규칙·메모리·도구 사용 정책을 **전부 시스템 프롬프트에** 넣고
  매 호출 재조립한다 — <system-reminder> 채널이 없으니 다른 통로도 없다.
- 하드 게이트·권한(deny)·넛지·전처리·스마트 배치 없음 — function_call을 받은
  순서대로 하나씩 실행한다.
- "수정 전에 먼저 읽어라", "파괴적 변경은 신중히" 같은 규칙이 **문장으로만** 존재한다
  (하네스는 같은 규칙을 코드 게이트로 강제한다).
- 디퍼드 레지스트리 없음 — 세션 중간에 도구가 늘면 tools 배열이 그냥 바뀐다
  (tools 배열은 캐시 프리픽스의 일부이므로 = 프리픽스 파괴).
"""

import json
import time

from cc_harness import schemas
from cc_harness.config import MODEL, get_client
from cc_harness.fs_tools import FsTools
from cc_harness.metrics import UsageLog
from cc_harness.state import World


def _native_system_prompt(world, extra_tool_names=()):
    rules = "\n".join(f"### {d}\n{r}" for d, r in world.rules.items())
    memories = "\n".join(f"- ({m['name']}) {m['content']}" for m in world.memories)
    extra = ""
    if extra_tool_names:
        extra = ("\n## 추가 도구\n- 다음 도구들이 사용 가능합니다: "
                 + ", ".join(extra_tool_names))
    return f"""# 역할
당신은 사용자의 프로젝트에서 일하는 코딩 에이전트입니다.
- 프로젝트 파일은 /project 아래에 있으며 모든 경로는 절대경로입니다.
- 오늘 날짜: {world.today}

# 프로젝트 규칙
{rules}

# 사용자 메모리
{memories}

# 도구 사용 정책
## 순서
- 파일을 수정(edit_file·write_file)하기 전에 반드시 read_file로 먼저 읽으세요.
- 바꿀 원문(old_string)은 읽은 내용에서 정확히 복사하세요.
## 병렬 호출
한 응답에서 여러 도구를 호출할 수 있습니다. 호출들 사이에 의존성이 없다면 독립적인 도구 호출을
모두 병렬로 하세요. 단, 어떤 호출이 앞선 호출의 결과값에 의존한다면 순차적으로 호출하세요.
## 주의
- 삭제나 덮어쓰기처럼 되돌리기 어려운 변경은 신중히 수행하세요.
- .env로 시작하는 파일(.env, .env.example 등)은 절대 수정하거나 덮어쓰지 마세요.{extra}

# 출력
- 한국어로 답하세요.
"""


class NativeSession:
    """순정 펑션콜링 루프 — 모델 호출 → 받은 순서대로 실행 → 결과 append → 반복."""

    def __init__(self, model=None, after_call=None):
        self.model = model or MODEL
        self.world = World()
        self.fs = FsTools(self.world, nudges=False, gates=False, inline_sr=False,
                          track_rules=False)
        self.impls = {
            "glob_files": self.fs.glob_files,
            "grep_files": self.fs.grep_files,
            "read_file": self.fs.read_file,
            "edit_file": self.fs.edit_file,
            "write_file": self.fs.write_file,
            "run_command": self.fs.run_command,
        }
        # 소프트(게이트 없는 원문) 스키마 — 이 세션의 실제 동작과 일치하는 설명 쪽을 쓴다
        self.tools = [schemas.glob_tool(dispatcher=False), schemas.grep_tool(dispatcher=False),
                      schemas.read_tool(hard_gates=False), schemas.edit_tool(hard_gates=False),
                      schemas.write_tool(hard_gates=False), schemas.run_command_tool()]
        self.extra_tool_names = []
        self.history = []
        self.usage = UsageLog()
        self.turn = 0
        self.after_call = after_call   # 실험 리그용 — 도구 실행 직후 훅 (외부 사건 주입)

    # ── 세션 중간 도구 추가 — 네이티브 방식 ──
    def add_tools(self, defs, impls):
        """tools 배열에 그냥 덧붙인다. 배열이 바뀌므로 다음 요청의 캐시 프리픽스가 깨진다."""
        self.tools = self.tools + list(defs)
        self.impls.update(impls)
        self.extra_tool_names += [d["name"] for d in defs]
        print(f"🔌 (네이티브) 도구 {len(defs)}개 추가 — tools 배열·시스템 프롬프트가 바뀜")

    def _run(self, call):
        impl = self.impls.get(call.name)
        if impl is None:
            return f"ERROR: 알 수 없는 도구 '{call.name}'"
        try:
            args = json.loads(call.arguments)
        except (json.JSONDecodeError, TypeError):
            return "ERROR: 잘못된 인자입니다. 도구 스키마에 맞춰 다시 호출하세요."
        try:
            out = impl(**args)
        except TypeError as e:
            return f"ERROR: 잘못된 인자입니다. 도구 스키마에 맞춰 다시 호출하세요. ({e})"
        except Exception as e:
            return f"ERROR: 실행 실패: {e}"
        return out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)

    def ask(self, question, max_rounds=16):
        print(f"💬 {question}\n")
        self.turn += 1
        self.history.append({"role": "user", "content": question})
        for cycle in range(1, max_rounds + 1):
            # 시스템 프롬프트 매 호출 재조립 — 날짜·도구 목록이 바뀌면 프리픽스도 바뀐다
            input_list = ([{"role": "developer",
                            "content": _native_system_prompt(self.world, self.extra_tool_names)}]
                          + self.history)
            self.usage.snapshot(input_list)
            start = time.perf_counter()
            response = get_client().responses.create(
                model=self.model, input=input_list, tools=self.tools)
            self.usage.record(response, time.perf_counter() - start, turn=self.turn)

            self.history += response.output
            calls = [it for it in response.output if it.type == "function_call"]
            if not calls:
                print(f"═══ 사이클 {cycle} ═══  function_call 0개 → 최종 답변")
                print(f"\n🤖 {response.output_text}")
                return response.output_text
            print(f"═══ 사이클 {cycle} ═══  function_call {len(calls)}개")

            for c in calls:  # 받은 순서 그대로, 안전성 분석 없이 순차 실행
                out = self._run(c)
                mark = "⛔" if out.startswith("ERROR") else "🔧"
                head = out.splitlines()[0] if out else ""
                print(f"  {mark} {c.name}({(c.arguments or '')[:100]})")
                print(f"     → {head[:140]}{' …' if len(out) > len(head) else ''}")
                self.history.append({"type": "function_call_output",
                                     "call_id": c.call_id, "output": out})
                if self.after_call:
                    self.after_call(self, c)
        print("⚠️ 최대 라운드 초과")
        return None


def count_calls(history):
    """세션 이력에서 실행된 function_call 수 — 두 세션 공용 계량."""
    n = 0
    for it in history:
        t = it.get("type") if isinstance(it, dict) else getattr(it, "type", None)
        n += t == "function_call"
    return n


def mcp_tool_defs(server="slack"):
    """하네스 MCPRegistry의 서버 도구를 네이티브 tools 배열용 (defs, impls)로 변환."""
    import contextlib
    import io

    from cc_harness.mcp import MCPRegistry
    reg = MCPRegistry()
    with contextlib.redirect_stdout(io.StringIO()):  # 레지스트리 연결 로그 억제 (재료 추출용)
        reg.connect(server)
    defs, impls = [], {}
    for name, t in reg.visible().items():
        defs.append({"type": "function", "name": name,
                     "description": t["description"], "parameters": t["parameters"]})
        impls[name] = (lambda h: lambda **kw: h(kw))(t["handler"])
    return defs, impls
