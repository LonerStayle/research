"""도구 실행 파이프라인 — CC checkPermissionsAndCallTool() 10단계 중 1·2·6·7·8 이식 (축소판).

| 단계 | 이름 | 여기 |
|---|---|---|
| 1 | 형식 체크 (Zod safeParse) | stage1_schema_check |
| 2 | 값 체크 (validateInput) | ToolRecord.validator |
| 3 | 투기 분류기 (Bash 전용 LLM) | 생략 |
| 4 | 입력 정규화 (backfill) | 생략 |
| 5 | Pre훅 | 생략 |
| 6 | 권한 (canUseTool) | stage6_check_permission |
| 7 | 실행 (tool.call) | ToolRecord.impl |
| 8 | 결과 변환 (mapToolResultToToolResultBlockParam) | ToolRecord.mapper |
| 9 | 텔레메트리 | 생략 (trace print가 대행) |
| 10 | Post훅 | 생략 |

핵심 설계: 7단계(되돌릴 수 없는 실행)에 도달하기 전에, 되돌릴 수 있는 검사(1·2·6)로
최대한 걸러낸다. 게이트에서 죽으면 <tool_use_error> 문자열을 function_call_output으로
돌려줘서 모델이 스스로 수정·재시도하게 한다.

CC 개발자 주석: "surprisingly, the model is not great at generating valid input."
"""

import fnmatch
import json
import re
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from .config import BASH_MAX_RESULT_CHARS, BASH_PREVIEW_CHARS

PY_TYPES = {
    "string": str, "integer": int, "number": (int, float),
    "boolean": bool, "object": dict, "array": list,
}


@dataclass
class ToolRecord:
    """도구 1레코드에 파이프라인·스케줄링 메타를 전부 부착 (통합 지점).

    definition        — OpenAI 도구 정의 (1단계 스키마 + tools 배열 소스)
    impl              — kwargs 구현 (7단계)
    validator         — 2단계 값 체크: args -> 에러문자열 | None (파일 열어봐야 아는 검증)
    read_only         — 6단계: 읽기 전용이면 자동 allow
    mapper            — 8단계: 원시 결과 -> tool_result 문자열 (도구별 자체 크기 한도 포함)
    concurrency_safe  — 파티션: bool 또는 args->bool (CC isConcurrencySafe — 기본값 "assume not safe")
    """

    definition: dict
    impl: object
    validator: object = None
    read_only: bool = False
    mapper: object = None
    concurrency_safe: object = False

    @property
    def name(self):
        return self.definition["name"]

    def is_safe(self, args):
        s = self.concurrency_safe
        return bool(s(args)) if callable(s) else bool(s)

    def map_result(self, raw):
        if self.mapper:
            return self.mapper(raw)
        return raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)


def map_bash_result(raw):
    """CC BashTool 매핑 이식: stdout·stderr·exit code를 filter(Boolean).join. 빈 stderr는 생략,
    성공(exit 0)이면 exit code도 생략 — 에러일 때만 "Exit code N"이 stdout 뒤에 붙는다.
    대용량 축소도 이 매핑 함수 '안'에 있다 — Bash 자신의 한도 30,000자 (FileRead=Infinity, Grep=20,000)."""
    parts = [raw.get("stdout", ""), raw.get("stderr", "")]
    if raw.get("exit_code", 0) != 0:
        parts.append(f"Exit code {raw['exit_code']}")
    text = "\n".join(p for p in parts if p)
    if len(text) <= BASH_MAX_RESULT_CHARS:
        return text
    path = Path(tempfile.gettempdir()) / f"tool_result_{uuid.uuid4().hex[:8]}.txt"
    path.write_text(text, encoding="utf-8")
    return (
        f"Output too large ({len(text):,} chars). Full output saved to: {path}\n"
        f"Preview (first {BASH_PREVIEW_CHARS} chars):\n{text[:BASH_PREVIEW_CHARS]}"
    )


class Pipeline:
    """checkPermissionsAndCallTool 축소판 오케스트레이터 (0 레지스트리 → 1 → 2 → 6 → 7 → 8)."""

    def __init__(self, records, deny_rules=None, permission_mode="acceptAll",
                 ask_fn=None, trace=False):
        self.records = records                       # name -> ToolRecord
        # deny 규칙이 항상 최우선 — 환경변수 파일 쓰기 금지 (원본: [("write_note", "*.env*")])
        self.deny_rules = deny_rules if deny_rules is not None else [
            ("write_file", "*.env*"), ("edit_file", "*.env*")]
        self.permission_mode = permission_mode       # "default" | "acceptAll" | "dontAsk"
        # default 모드의 Y/N 질문 — 노트북 커널 밖에서도 쓰도록 콜백 주입형 (기본은 input())
        self.ask_fn = ask_fn or (lambda prompt: input(prompt).strip().lower())
        self.trace = trace

    # ── [1] 형식 체크 (Zod safeParse 흉내) — JSON '종이'만 심사, I/O 없음 ──
    def stage1_schema_check(self, name, raw_arguments):
        schema = self.records[name].definition["parameters"]
        try:
            args = json.loads(raw_arguments)
        except json.JSONDecodeError as e:
            return None, f"JSON 파싱 실패: {e}"
        if not isinstance(args, dict):
            return None, f"객체가 아님: {args!r}"
        unknown = set(args) - set(schema["properties"])
        if unknown:  # strictObject — 미지 키 거부 (내부 전용 필드 몰래 끼우기 차단)
            return None, f"허용되지 않은 키: {sorted(unknown)}"
        missing = set(schema.get("required", [])) - set(args)
        if missing:
            return None, f"필수 키 누락: {sorted(missing)}"
        for key, value in args.items():
            expected = schema["properties"][key].get("type")
            if expected in PY_TYPES and not isinstance(value, PY_TYPES[expected]):
                return None, f"'{key}'는 {expected} 타입이어야 함 (받은 값: {value!r})"
        return args, None

    # ── [6] 권한 (canUseTool) — deny 규칙 최우선 → 읽기 전용 allow → 모드별 분기 ──
    def stage6_check_permission(self, name, args):
        target = args.get("file_path") or args.get("filename") or args.get("path") or ""
        for rule_tool, pattern in self.deny_rules:
            if name == rule_tool and fnmatch.fnmatch(target, pattern):
                return "deny", f"deny 규칙 매칭: {rule_tool}({pattern})"
        if self.records[name].read_only:
            return "allow", "읽기 전용 도구"
        if self.permission_mode == "acceptAll":
            return "allow", "acceptAll 모드"
        if self.permission_mode == "dontAsk":
            return "deny", "dontAsk 모드 — 쓰기 도구 자동 거부"
        # default 모드: 사용자에게 직접 묻는다 (CC 터미널의 [Y] Allow / [N] Deny)
        answer = self.ask_fn(f"쓰기 도구 실행을 허용할까요? {name}({args}) [y/n] ")
        if answer == "y":
            return "allow", "사용자 승인"
        return "deny", "사용자 거부"

    def run(self, name, raw_arguments):
        """function_call 하나를 1→2→6→7→8 게이트에 통과시키고,
        모델에게 돌려줄 output 문자열을 반환한다."""
        trace = self.trace
        if trace:
            print(f"┌─ {name} {raw_arguments[:120]}")

        def blocked(stage, message):
            if trace:
                print(f"│ [{stage}] FAIL — {message}")
                print("└─ 게이트 차단 (7단계 실행 안 됨)")
            return f"<tool_use_error>{message}</tool_use_error>"  # CC 실제 표기

        if name not in self.records:
            return blocked("0 레지스트리", f"등록되지 않은 도구: {name}")
        record = self.records[name]

        # [1] 형식 체크
        args, error = self.stage1_schema_check(name, raw_arguments)
        if error:
            return blocked("1 형식체크", f"InputValidationError: {error}")
        if trace:
            print("│ [1 형식체크] PASS")

        # [2] 값 체크 — 파일시스템 현장실사 (읽기만, 수정 안 함)
        if record.validator:
            error = record.validator(args)
            if error:
                # 에러 채널 규약: 파이프라인 게이트 = <tool_use_error> 태그만, 도구 내부 = "ERROR:" 접두.
                # 게이트 문구를 validator로 재사용할 때 접두를 떼서 이중 마킹을 막는다.
                return blocked("2 값체크", re.sub(r"^ERROR:\s*", "", error))
        if trace:
            print("│ [2 값체크] PASS")

        # [6] 권한
        decision, reason = self.stage6_check_permission(name, args)
        if decision == "deny":
            return blocked("6 권한", f"권한 거부 ({reason})")
        if trace:
            print(f"│ [6 권한] allow — {reason}")

        # [7] 실행 — 여기서부터는 되돌릴 수 없다
        try:
            start = time.perf_counter()
            raw = record.impl(**args)
            duration_ms = (time.perf_counter() - start) * 1000
        except Exception as e:
            return blocked("7 실행", f"실행 실패: {e}")
        if trace:
            print(f"│ [7 실행] 완료 ({duration_ms:.2f}ms)")

        # [8] 도구별 매핑 — 각 도구가 자기 결과를 tool_result 문자열로 접고, 자기 한도로 스스로 축소
        output = record.map_result(raw)
        if trace:
            note = "도구 자체 한도 초과 → 디스크 오프로드" if output.startswith("Output too large") else "그대로 통과"
            print(f"│ [8 매핑] {name} 결과({type(raw).__name__}) → {len(output):,}자 ({note})")
            print("└─ OK")
        return output
