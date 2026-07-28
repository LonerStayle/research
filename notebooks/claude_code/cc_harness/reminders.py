"""system-reminder 시스템 — SR 래퍼·스푸핑 방어·0번 유령·인라인 SR 조각·어태치먼트 수집기 6종.

cc_system_reminder.ipynb 전량 포팅. 문구는 CC 원문의 한국어 번역을 그대로 보존한다.

CC의 <system-reminder>는 주입 경로 기준 2부류:
1. 어태치먼트 파이프라인 — 수집 지점 2곳(유저 턴 엔트리 / 툴콜 루프 꼬리)에서
   트리거 조건을 검사해 통과분만 주입 (ReminderPipeline)
2. 비-어태치먼트 SR — 특정 코드 지점에서 직접 조립·주입
   (0번 유령 메시지 / 빈 파일 경고 / 사이버리스크 지침 / 신선도 경고 / 사이드 질문 / 스푸핑 무력화)

isMeta × SR 4분면: role이 전부 user라서 이 2비트 없이는 구분 불가 —
isMeta는 Responses API에 없어 앱 레벨(로그 마커)로만 관리한다.
"""

import re

from .config import TODO_TURNS_BETWEEN, TODO_TURNS_SINCE_WRITE


def SR(body):
    # CC wrapInSystemReminder (messages.ts:3097) 대응
    return f"<system-reminder>\n{body}\n</system-reminder>"


def neutralize(text):
    # 스푸핑 방어(비-어태치먼트 ⑥): 유저/외부 텍스트의 제어 태그 중화 — '<' -> '<\'
    return re.sub(r"<(/?)(system-reminder)", r"<\\\1\2", text)


# ── 인라인 SR 조각 (tool_result 문자열 '안'에 박힌다) ───────────────
SUSPICIOUS = re.compile(r"exec\(|eval\(|b64decode")

CYBER_RISK_REMINDER = SR(
    "이 파일에는 위험해 보이는 코드가 포함되어 있습니다. 무엇을 하는 코드인지 분석·설명은 "
    "하되, 이 코드의 기능을 개선·보강·완성해 달라는 요청은 거부하세요."
)  # CC FileReadTool.ts:730 — CC는 모든 텍스트 읽기에 부착, 재현은 의심 패턴일 때만(노이즈 감소)

EMPTY_FILE_WARNING = SR("경고: 파일은 존재하지만 내용이 비어 있습니다.")  # CC FileReadTool.ts:706


def ghost_message(world, user_email="user@example.com",
                  global_rules="- 모든 답변은 한국어로 한다."):
    """0번 유령 메시지 — 매 API 호출 최상단 재생성, 이력 미저장 (CC api.ts:462).

    이력이 아니라 '매번 다시 인쇄되는 표지'라서 날짜가 바뀌면 다음 호출부터 자동 최신."""
    body = ("사용자의 질문에 답할 때 다음 컨텍스트를 활용할 수 있습니다:\n"
            f"# 오늘 날짜\n{world.today}\n"
            f"# 사용자\n{user_email}\n"
            f"# CLAUDE.md (전역 지침)\n{global_rules}\n\n"
            "중요: 이 컨텍스트는 현재 작업과 관련이 있을 수도, 없을 수도 있습니다. "
            "관련성이 높은 경우가 아니라면 이 컨텍스트에 반응하지 마세요.")
    return {"role": "user", "content": SR(body)}


def maybe(label, builder):
    # CC maybe() (attachments.ts:1005) — 실패 격리 + 빈 결과 SKIP.
    # 어태치먼트 하나가 죽어도 대화는 계속된다. (CC의 수집 전체 1초 데드라인·킬스위치는 생략)
    try:
        return builder() or []
    except Exception as e:
        print(f"  (수집기 {label} 실패 — 격리하고 계속: {e})")
        return []


class ReminderPipeline:
    """어태치먼트 수집기 6종 + 수집 진입점 2곳. World 하나에 바인딩되는 세션 소유 상태.

    각 수집기는 (라벨, 본문, 배달방식)을 반환한다. 배달방식:
      "smoosh"   — 마지막 tool_result의 output 뒤에 합체 (CC smooshSystemReminderSiblings)
      "separate" — 별도 user 메시지 (queued_command만 isMeta 없이 화면 표시)
    """

    def __init__(self, world):
        self.world = world
        self.last_known_date = world.today   # 델타 감지 기준점
        self.rounds_since_todo = 0           # CC: human 턴이 아니라 '툴 라운드' 단위 카운트
        self.rounds_since_reminder = 999     # 999 = 첫 발동을 막지 않기 위한 초기값

    # ① 입력 파싱형 — @멘션 파일 (유저 턴 전용)
    def collect_at_mentions(self, user_text):
        out = []
        fs = self.world.fs
        for path in re.findall(r"@(/\S+)", user_text):
            if path in fs and fs[path]["content"]:
                body = (f"사용자가 @로 언급한 파일입니다. 다시 읽을 필요 없이 아래 내용을 참조하세요.\n\n"
                        f"{path} 내용:\n{fs[path]['content']}")
                out.append(("at_mentioned_file", body, "separate"))
        return out
        # CC는 이걸 가짜 Read tool_use/tool_result 쌍으로 위장해 넣는다 (attachments.ts:3142)

    # ② 상태 스냅샷형 — todo 방치 리마인더
    def collect_todo_reminder(self):
        if self.rounds_since_todo < TODO_TURNS_SINCE_WRITE:
            return []
        if self.rounds_since_reminder < TODO_TURNS_BETWEEN:
            return []
        self.rounds_since_reminder = 0
        body = ("todo_write 도구가 최근 사용되지 않았습니다. 진행 상황 추적이 도움될 작업 중이라면 "
                "todo_write로 진행 상황을 추적하는 것을 고려하세요. 목록이 낡았다면 정리도 고려하세요. "
                "현재 작업에 관련될 때만 사용하세요. 이것은 부드러운 리마인더일 뿐입니다 - "
                "해당 없으면 무시하세요. 이 리마인더를 사용자에게 절대 언급하지 마세요")
        if self.world.todos:
            body += "\n\n현재 todo 목록:\n" + "\n".join(
                f"- [{t['status']}] {t['content']}" for t in self.world.todos)
        return [("todo_reminder", body, "smoosh")]

    # ③ 델타 감지형 — 날짜 변경
    def collect_date_change(self):
        if self.world.today == self.last_known_date:
            return []
        self.last_known_date = self.world.today
        return [("date_change",
                 f"날짜가 바뀌었습니다. 오늘 날짜는 이제 {self.world.today}입니다. "
                 "사용자는 이미 알고 있으므로 이를 명시적으로 언급하지 마세요.", "smoosh")]

    # ④ 외부 폴링형 — 미드턴 유저 메시지 큐 드레인
    def collect_queued_commands(self):
        out = [("queued_command", f"작업 중에 사용자가 새 메시지를 보냈습니다:\n{neutralize(m)}",
                "separate")
               for m in self.world.message_queue]
        self.world.message_queue.clear()  # mark-as-read
        return out

    # ⑤ 사이드쿼리형 — 관련 메모리 (목 셀렉터; CC는 소넷 별도 호출 + 프리페치)
    def collect_relevant_memories(self, user_text):
        out = []
        for m in self.world.memories:
            if any(k in user_text for k in m["keywords"]):
                body = ("관련될 수 있어 회수된 메모리입니다 - 사용자의 요청에 실제로 해당할 때만 "
                        f"사용하세요.\n\n[{m['name']}] {m['content']}\n\n"
                        # 비-어태치먼트 ④ 메모리 신선도 경고 (CC memoryAge.ts) — 회수 시 나이 주입
                        f"주의: 이 메모리는 {m['age_days']}일 전에 기록된 것입니다. 기록 당시와 "
                        "상황이 달라졌을 수 있으니 오래된 정보는 검증 후 사용하세요.")
                out.append(("relevant_memories", body, "separate"))
        return out

    # ⑥ 트리거 축적형 — 도구가 만진 디렉토리의 규칙 주입
    def collect_nested_rules(self):
        out = []
        w = self.world
        for rule_dir in sorted(w.nested_triggers):
            w.injected_rule_dirs.add(rule_dir)
            out.append(("nested_memory",
                        f"{rule_dir}/RULES.md 내용:\n{w.rules[rule_dir]}\n\n"
                        "이 규칙은 방금 작업이 닿은 디렉토리의 로컬 규칙입니다.", "smoosh"))
        w.nested_triggers.clear()
        return out

    # ── 수집 진입점 2곳 (CC: processUserInput.ts:504 / query.ts:1569) — 순서 보존 ──
    def collect_user_turn(self, user_text):
        # 유저 턴 엔트리: 입력 파싱형(그룹1) 먼저, 그다음 상태/델타
        atts = []
        atts += maybe("at_mentioned_file", lambda: self.collect_at_mentions(user_text))
        atts += maybe("relevant_memories", lambda: self.collect_relevant_memories(user_text))
        atts += maybe("date_change", self.collect_date_change)
        atts += maybe("todo_reminder", self.collect_todo_reminder)
        return atts

    def collect_in_loop(self):
        # 툴 라운드 꼬리: input=null 이라 입력 파싱형(그룹1)은 스킵 — CC와 동일
        atts = []
        atts += maybe("date_change", self.collect_date_change)
        atts += maybe("nested_memory", self.collect_nested_rules)
        atts += maybe("todo_reminder", self.collect_todo_reminder)
        atts += maybe("queued_command", self.collect_queued_commands)
        return atts

    def note_round(self, used_todo):
        # 툴 라운드 꼬리 카운터 (CC: human 턴이 아니라 툴 라운드 단위)
        if used_todo:
            self.rounds_since_todo = 0
        else:
            self.rounds_since_todo += 1
        self.rounds_since_reminder += 1


def deliver(history, atts, where):
    """수집된 어태치먼트를 배달방식대로 history에 주입 (앱 레벨 isMeta는 로그 마커로만)."""
    for label, body, delivery in atts:
        if delivery == "smoosh" and where == "in_loop":
            # CC smooshSystemReminderSiblings: 마지막 tool_result에 합체
            last = history[-1]
            assert last.get("type") == "function_call_output"
            last["output"] += "\n\n" + SR(body)
            print(f"  📎 [인루프·smoosh→마지막 tool_result] {label}")
        elif label == "queued_command":
            # 미드턴 유저 육성: SR 포장은 하되 isMeta 없음(화면 표시) — 4분면의 우상단
            history.append({"role": "user", "content": SR(body)})
            print(f"  📨 [인루프·화면표시·SR포장] {label}")
        else:
            # 별도 isMeta user 메시지 (Responses API엔 isMeta가 없어 앱 레벨 관리)
            history.append({"role": "user", "content": SR(body)})
            print(f"  📎 [{'턴엔트리' if where == 'user_turn' else '인루프'}·isMeta] {label}")


SIDE_QUESTION_TEMPLATE = (
    "이것은 사용자의 사이드 질문입니다. 진행 중인 작업과 별개로, 단 한 번의 응답으로 "
    "이 질문에 직접 답하세요. 도구를 호출하지 마세요.\n\n질문: {question}"
)  # 비-어태치먼트 ⑤ (CC sideQuestion.ts:61) — 사용처: Session.side_question
