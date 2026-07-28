"""cc_harness — 클로드코드(CC) 에이전트 아키텍처의 최종 GPT 미니 하네스.

cc_* 노트북 8종이 각각 재현했던 메커니즘을 한 패키지로 통합했다:
  ① system-reminder (어태치먼트 6종 + 비-어태치먼트: 유령·인라인·사이드질문·스푸핑 방어)
  ② 도구 실행 파이프라인 (1형식·2값·6권한·7실행·8매핑 — 10단계 축소판)
  ③ 하드·소프트 순서규칙 (readFileState 게이트 / 입장권·니치·탈출구·넛지)
  ④ 스마트 배치 스케줄링 (partition — 연속 safe만 병합·unsafe 단독·동시성 10)
  ⑤ 멀티 function calling (Responses API 루프 원형)
  ⑥ ToolSearch 디퍼드 레지스트리 (tools 동결 → KV 캐시 미스 0)
  ⑦ MCP connect/disconnect 델타 고지 (append-only → 프리픽스 불변)
  ⑧ 목 파일시스템 (orderhub 40파일 + mtime)
  ⑨ 컨텍스트 전처리 ① applyToolResultBudget (직전 사이클 묶음 오프로드)

로직은 전부 이 패키지(.py)에 있고, 실행·관찰은 노트북(run_cc_harness.ipynb)에서 한다.
원본 노트북·모듈(cc_tools.py 등)은 리서치 기록으로 그대로 보존 — 이 패키지는 독립적이다
(단, 순수 데이터인 cc_mock_fs.py·cc_deferred_tools.py는 단일 진실로 재사용).

빠른 시작:
    from cc_harness import Session
    s = Session()                     # 풀 CC 사이클 (전 장치 ON)
    s.ask("authenticate 찾아서 verify_password로 바꿔줘")

    s = Session(hard_gates=False)     # 소프트 규칙 노트북 조건 재현
    s = Session(track_cache=True, prompt_cache_key="demo")  # KV 캐시 계측
"""

from .config import (BASH_MAX_RESULT_CHARS, BASH_PREVIEW_CHARS, BUDGET_CHARS,
                     DOMINANT_RATIO, GLOB_LIMIT, GREP_HEAD_LIMIT,
                     MAX_TOOL_USE_CONCURRENCY, MODEL, PREVIEW_BYTES,
                     READ_MAX_LINES, TOP_N, HarnessConfig, get_client)
from .context import ContextBudget, persisted_message
from .fs_tools import FILE_UNCHANGED_STUB, TRUNCATION_NUDGE, FsTools
from .mcp import ADDED_HEADER, REMOVED_HEADER, MCPRegistry, announced_names, render_delta
from .metrics import UsageLog, norm_item
from .mock_fs import (cleanup_test_files, make_big_log, make_dup_file,
                      make_request_log, make_test_files, simulate_linter)
from .pipeline import Pipeline, ToolRecord, map_bash_result
from .prompts import (ASSISTANT_INSTRUCTIONS, DELEGATION_POLICY, TODO_SYSTEM_EXTRA,
                      build_system_prompt)
from .registry import (ALL_MCP_TOOLS, GENERIC_REGISTRY, MCP_SERVERS, REGISTRY,
                       from_openai_schema, make_tool)
from .reminders import SR, ReminderPipeline, ghost_message, neutralize
from .scheduling import execute_batches, fake, partition_tool_calls, print_partition
from .schemas import freeze_tools
from .session import Session
from .state import World
from .toolsearch import (handle_tool_invoke, handle_tool_search, score_tool,
                         validate_args)

__all__ = [
    "Session", "HarnessConfig", "World", "FsTools", "Pipeline", "ToolRecord",
    "MCPRegistry", "ReminderPipeline", "ContextBudget", "UsageLog",
    # 스케줄링·검색 유틸
    "partition_tool_calls", "print_partition", "execute_batches", "fake",
    "handle_tool_search", "handle_tool_invoke", "score_tool", "validate_args",
    "freeze_tools", "from_openai_schema", "make_tool",
    # 데이터·픽스처
    "REGISTRY", "GENERIC_REGISTRY", "MCP_SERVERS", "ALL_MCP_TOOLS",
    "make_test_files", "cleanup_test_files", "make_big_log", "make_request_log",
    "make_dup_file", "simulate_linter",
    # SR·프롬프트·상수
    "SR", "neutralize", "ghost_message", "render_delta", "announced_names",
    "build_system_prompt", "ASSISTANT_INSTRUCTIONS", "DELEGATION_POLICY",
    "TODO_SYSTEM_EXTRA", "persisted_message", "map_bash_result", "norm_item",
    "ADDED_HEADER", "REMOVED_HEADER", "TRUNCATION_NUDGE", "FILE_UNCHANGED_STUB",
    "MODEL", "get_client",
    "GLOB_LIMIT", "GREP_HEAD_LIMIT", "READ_MAX_LINES", "BASH_MAX_RESULT_CHARS",
    "BASH_PREVIEW_CHARS", "MAX_TOOL_USE_CONCURRENCY", "TOP_N", "DOMINANT_RATIO",
    "BUDGET_CHARS", "PREVIEW_BYTES",
]
