"""cc_harness 전역 설정 — 상한·임계값(CC 원값), 기본 모델, OpenAI 클라이언트, HarnessConfig.

수치 상수는 CC 원본 값을 그대로 보존한다. 데모 규모로 축소한 값은 주석에 원값을 남긴다.
"""

from dataclasses import dataclass

# ── 출력 상한 (CC 원값) ─────────────────────────────────────────────
GLOB_LIMIT = 100                # CC GlobTool: 100개에서 잘림
GREP_HEAD_LIMIT = 250           # CC GrepTool: content 모드 기본 head_limit
READ_MAX_LINES = 2000           # CC FileReadTool: 기본 2000줄
BASH_MAX_RESULT_CHARS = 30_000  # BashTool.tsx:424 — Bash '자신의' 한도 (전역 아님)
BASH_PREVIEW_CHARS = 2_000      # 원문 예시의 "Preview (first 2KB)"

# ── 스케줄링 (CC 원값) ──────────────────────────────────────────────
MAX_TOOL_USE_CONCURRENCY = 10   # CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY 기본값

# ── ToolSearch ──────────────────────────────────────────────────────
TOP_N = 5
DOMINANT_RATIO = 2.0            # CC엔 없음 — 서버측 스키마 확장이 없는 OpenAI 이식판의 숏컷

# ── 컨텍스트 전처리 ① ──────────────────────────────────────────────
BUDGET_CHARS = 200_000          # CC applyToolResultBudget 임계
PREVIEW_BYTES = 400             # 데모용 축소 — 실제 CC PREVIEW_SIZE_BYTES = 2000

# ── system-reminder (todo 방치) — CC 원값 10을 데모 규모로 축소 ─────
TODO_TURNS_SINCE_WRITE = 2      # CC TODO_REMINDER_CONFIG.TURNS_SINCE_WRITE = 10
TODO_TURNS_BETWEEN = 2          # CC TURNS_BETWEEN_REMINDERS = 10

MODEL = "gpt-5-nano"            # 기본 모델 — Session(model=...)으로 오버라이드

_client = None


def get_client():
    global _client
    if _client is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        _client = OpenAI()
    return _client


@dataclass
class HarnessConfig:
    """최종 미니 하네스의 기능 스위치 — 기본값 = 전부 켠 '풀 CC 사이클'.

    각 플래그를 끄면 개별 cc_* 노트북의 실험 조건이 재현된다:
      hard_gates=False              → 소프트 규칙 노트북 조건 (읽기 강제 게이트 없음)
      nudges=False, dispatcher=False → 하드 규칙 노트북 조건 (게이트만)
      pipeline=False, scheduling=False → 순차 직접 실행 (멀티 함수콜 베이스라인)
      reminders=False, ghost=False  → system-reminder 없는 맨몸 루프
    """

    model: str = None                  # None이면 config.MODEL
    # ── 도구·순서 규칙 ──
    nudges: bool = True                # 소프트 넛지 (오타·재읽기 스텁·잘림 리다이렉트)
    hard_gates: bool = True            # readFileState 게이트 (읽기 강제·낡은읽기·자가갱신)
    dispatcher: bool = True            # 디퍼드 레지스트리 + tool_search/tool_invoke
    todo_mode: bool = False            # 태스크 관리 권장 프롬프트 (방치 리마인더는 reminders가 담당)
    shell_tool: bool = True            # run_command (8단계 도구별 매퍼·조건부 동시성 데모)
    inline_sr: bool = True             # 빈 파일 경고·사이버리스크 인라인 SR
    # ── 루프 장치 ──
    reminders: bool = True             # 어태치먼트 수집기 6종 (유저턴/인루프 주입)
    ghost: bool = True                 # 0번 유령 메시지 (매 호출 재생성, 이력 미저장)
    spoof_guard: bool = True           # 유저 입력의 <system-reminder> 리터럴 중화
    preprocess: str = "budget"         # 전처리 ①: "budget"(CC 충실) | "edit_forced"(데모 변형) | None
    scheduling: bool = True            # 스마트 배치 (partition + 배치 간 직렬·내 병렬)
    pipeline: bool = True              # 도구 파이프라인 (1형식·2값·6권한·7실행·8매핑)
    permission_mode: str = "acceptAll"  # "default"(ask_fn 질문) | "acceptAll" | "dontAsk"
    mcp: bool = False                  # MCP 레지스트리 + 델타 고지
    # ── 계측·로그 ──
    track_cache: bool = False          # usage 기록 + 전송 스냅샷 (프리픽스 검증)
    prompt_cache_key: str = None
    trace_pipeline: bool = False       # 파이프라인 단계별 박스 로그
    trace_scheduling: bool = True      # 파티션·배치·타임라인 로그
    max_rounds: int = 16
