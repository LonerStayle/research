"""디퍼드 도구 레지스트리 — 데이터는 이웃 모듈 cc_deferred_tools.py(단일 진실)를 재사용.

레지스트리 항목 표준 포맷 (cc_deferred_tools.make_tool):
    {"name", "description", "search_hint", "parameters", "handler"}
handler는 args dict 하나를 받는 함수. OpenAI 스키마+kwargs 구현 쌍은
from_openai_schema() 어댑터로 이 포맷으로 변환한다.

이름 주의: 여기 REGISTRY의 agent_search(슬랙·메일·노션을 훑는 업무 비서용 목)와
cc_harness 기본 디퍼드 레지스트리의 agent_search(코드베이스를 훑는 목 서브에이전트)는
서로 다른 도구다 — 한 레지스트리에 함께 실리지 않는다(기본 세션은 후자만 사용).
"""

import os
import sys

_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from cc_deferred_tools import (  # noqa: F401  (re-export)
    ALL_MCP_TOOLS,
    AGENT_SEARCH,
    GENERIC_REGISTRY,
    GENERIC_TOOLS,
    MCP_SERVERS,
    REGISTRY,
    make_tool,
)


def from_openai_schema(tool_def, impl, hint=""):
    """OpenAI 도구 정의 + kwargs 구현 → 레지스트리 항목 포맷 어댑터."""
    return {
        "name": tool_def["name"],
        "description": tool_def["description"],
        "search_hint": hint,
        "parameters": tool_def["parameters"],
        "handler": lambda args, _impl=impl: _impl(**args),
    }
