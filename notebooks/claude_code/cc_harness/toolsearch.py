"""ToolSearch — CC 스코어링·검색·실행 게이트웨이 이식 (레지스트리 주입형 한 벌).

cc_toolsearch_kv_cache / cc_mcp_connect_disconnect 두 노트북의 중복 구현을 통합했다.
MCP 특례(이름 가중 12/6, mcp__서버 프리픽스 매칭, 해제 서버 거부)를 포함한 MCP판이 정본 —
is_mcp 분기는 mcp__ 접두사에만 적용되므로 일반 도구 결과는 불변이다.

설계 계약: 스키마는 tool_search 결과(대화)로만 전달되고, 실행은 tool_invoke 게이트웨이로만.
tools 배열은 동결 → 검색·실행이 아무리 일어나도 KV 캐시 프리픽스가 깨지지 않는다.
"""

import json
import re

from .config import DOMINANT_RATIO, TOP_N


def name_parts(name):
    # 클로드코드 parseToolName 이식: snake_case와 CamelCase를 단어로 분해
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).replace("_", " ")
    return [p for p in spaced.lower().split() if p]


def term_matches_text(term, text):
    # 클로드코드는 단어 경계 정규식(\b)을 쓰지만 한글 조사("메시지를")에는 안 맞아서
    # 한글이 든 키워드는 substring으로 매칭한다
    if re.search(r"[가-힣]", term):
        return term in text
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None


def score_tool(terms, tool):
    # 클로드코드 searchToolsWithKeywords 스코어링 이식 — MCP 도구는 이름 가중치가 12/6으로 더 높다
    is_mcp = tool["name"].startswith("mcp__")
    w_exact, w_part = (12, 6) if is_mcp else (10, 5)
    parts = name_parts(tool["name"])
    full = " ".join(parts)
    desc = tool["description"].lower()
    hint = tool.get("search_hint", "").lower()
    score = 0
    for term in terms:
        if term in parts:
            score += w_exact     # 이름 단어 정확 일치
        elif any(term in p for p in parts):
            score += w_part      # 이름 단어 부분 포함
        if score == 0 and term in full:
            score += 3           # 이름 전체 문자열 (보조)
        if hint and term_matches_text(term, hint):
            score += 4           # 큐레이션 검색 힌트
        if term_matches_text(term, desc):
            score += 2           # 설명
    return score


def full_schema_text(names, registry):
    blocks = [
        json.dumps(
            {"name": registry[n]["name"],
             "description": registry[n]["description"],
             "parameters": registry[n]["parameters"]},
            ensure_ascii=False, indent=2)
        for n in names
    ]
    return ("도구 스키마:\n" + "\n".join(blocks)
            + "\n\n이제 tool_invoke(name=도구이름, arguments=스키마에 맞는 인자 객체)로 실행하세요.")


def _log_event(state, summary):
    # 검색이 무엇을 찾았는지 요청별 로그(search_result 열)에 기록
    if state is not None:
        state.setdefault("search_events", []).append(summary)


def deliver_schemas(names, registry, state, prefix_note=""):
    """스키마를 대화로 흘리면서 발견 집합(discovered)에 기록 — tool_invoke의 로드 게이트가 본다.
    클로드코드의 extractDiscoveredToolNames가 tool_result의 tool_reference를 스캔해 만드는 집합."""
    if state is not None:
        state.setdefault("discovered", set()).update(names)
    _log_event(state, "스키마:" + ",".join(names))
    return prefix_note + full_schema_text(names, registry)


def _no_match_message(connected):
    if connected is not None:  # MCP 세션용 문구 (연결 상태 안내 포함)
        return ("No matching deferred tools found.\n"
                f"현재 연결된 MCP 서버: {', '.join(connected) or '없음'}. "
                "조사를 뺀 다른 키워드로 다시 검색하거나, "
                "해당 서버가 연결 해제됐다면 검색을 반복하지 말고 사용자에게 알리세요.")
    return "검색 결과 없음. 조사를 뺀 다른 키워드로 다시 검색하세요. 예: '메일 전송', '일정 등록'"


def handle_tool_search(query, registry, state=None, connected=None):
    """CC ToolSearch 이식 — select:(프리픽스 매칭 포함) / fast path / 키워드(+필수) 검색.

    registry: 현재 '보이는' 레지스트리 dict (MCP면 연결된 서버의 도구만)
    connected: MCP 연결 서버 이름 목록 (no-match 문구용; MCP 미사용이면 None)
    """
    query = (query or "").strip()

    # 모드 A — select: 정확한 이름 조회 (부분 성공 허용, mcp__서버 프리픽스면 그 서버 몽땅)
    if query.lower().startswith("select:"):
        names = [n.strip() for n in query[len("select:"):].split(",") if n.strip()]
        found, missing = [], []
        for n in names:
            if n in registry:
                found.append(n)
            else:
                prefix_hits = [k for k in registry if k.startswith(n + "__")]
                if prefix_hits:
                    found += prefix_hits
                else:
                    missing.append(n)
        if not found:
            _log_event(state, "결과없음")
            if connected is not None:
                return ("No matching deferred tools found.\n"
                        f"없는 이름: {', '.join(missing)}. "
                        f"현재 연결된 MCP 서버: {', '.join(connected) or '없음'}. "
                        "해당 서버가 연결 해제됐다면 검색을 반복하지 말고 사용자에게 알리세요.")
            return f"ERROR: 없는 도구 이름 {missing}. 키워드로 다시 검색하세요."
        note = f"\n\n(없는 이름이라 제외됨: {', '.join(missing)})" if missing else ""
        return deliver_schemas(found, registry, state) + note

    q = query.lower()

    # fast path — 쿼리 전체가 도구 이름이면 즉시 스키마, mcp__ 프리픽스면 그 서버 몽땅
    if q in registry:
        return deliver_schemas([q], registry, state)
    if q.startswith("mcp__"):
        prefix_hits = [k for k in registry if k.startswith(q)]
        if prefix_hits:
            return deliver_schemas(prefix_hits, registry, state)

    # 모드 B — 키워드 검색. "+키워드"는 필수 조건
    raw_terms = [t for t in re.split(r"\s+", q) if t]
    required = [t[1:] for t in raw_terms if t.startswith("+") and len(t) > 1]
    optional = [t for t in raw_terms if not t.startswith("+")]
    terms = required + optional if required else raw_terms

    candidates = list(registry.values())
    if required:
        candidates = [t for t in candidates
                      if all(score_tool([r], t) > 0 for r in required)]

    scored = sorted(((score_tool(terms, t), t) for t in candidates), key=lambda x: -x[0])
    scored = [(s, t) for s, t in scored if s > 0]
    if not scored:
        _log_event(state, "결과없음")
        return _no_match_message(connected)

    top = scored[:TOP_N]
    # 숏컷 — 압도적 1위면 고르기 생략 (CC엔 없음: 서버측 스키마 확장이 없는 OpenAI 이식판 전용)
    if len(top) == 1 or top[0][0] >= DOMINANT_RATIO * top[1][0]:
        name = top[0][1]["name"]
        return deliver_schemas([name], registry, state,
                               "1위 점수가 압도적이라 바로 스키마를 리턴합니다.\n\n")

    _log_event(state, "후보:" + ",".join(t["name"] for _, t in top))
    cards = "\n".join(f"{i + 1}. {t['name']} — {t['description']} (점수 {s})"
                      for i, (s, t) in enumerate(top))
    return ("후보 도구 목록 (점수순):\n" + cards
            + "\n\n필요한 도구를 모두 골라 tool_search(query=\"select:이름1,이름2\")로 다시 호출하세요."
            + "\n맞는 것이 없으면 다른 키워드로 재검색하세요.")


# ── tool_invoke — 검증하고 실행 (규칙 대신 반응형 에러 힌트) ────────
TYPE_CHECK = {"string": str, "integer": int, "number": (int, float),
              "boolean": bool, "array": list, "object": dict}


def validate_args(parameters, args):
    errors = []
    props = parameters.get("properties", {})
    for required in parameters.get("required", []):
        if required not in args:
            errors.append(f"필수 인자 '{required}' 누락")
    for key, value in args.items():
        if key not in props:
            errors.append(f"스키마에 없는 인자 '{key}'")
        elif not isinstance(value, TYPE_CHECK.get(props[key]["type"], object)):
            errors.append(f"'{key}'는 {props[key]['type']} 타입이어야 함")
    return errors


def handle_tool_invoke(name, arguments, registry, state=None, all_pool=None):
    """실행 게이트웨이 — 서버 strict 검증을 못 쓰는 대가로 클라이언트가 직접 검증한다.

    all_pool: 전체 도구 풀 (registry에 없지만 여기 있으면 '해제된 서버' 판정 — MCP 전용)
    """
    tool = registry.get(name)
    if tool is None:
        if all_pool and name in all_pool:
            server = name.split("__")[1]
            return (f"ERROR: '{name}'의 MCP 서버 '{server}'가 연결 해제되어 실행할 수 없습니다. "
                    "재시도하지 말고 사용자에게 알리세요.")
        return f"ERROR: '{name}' 도구는 없습니다. tool_search로 먼저 조회하세요."
    if state is not None and name not in state.get("discovered", set()):
        # 클로드코드 buildSchemaNotSentHint(toolExecution.ts:578-598) 이식 — 프롬프트 규칙 대신 반응형 힌트
        return (f"ERROR: '{name}'의 스키마가 아직 로드되지 않았습니다. "
                f"먼저 tool_search(query=\"select:{name}\")로 스키마를 로드한 뒤 이 호출을 다시 시도하세요.")
    if isinstance(arguments, str):  # 모델이 객체 대신 JSON 문자열로 보낸 경우
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            return "ERROR: arguments가 올바른 JSON 객체가 아닙니다. 스키마에 맞춰 다시 호출하세요."
    errors = validate_args(tool["parameters"], arguments)
    if errors:
        return "ERROR: 인자 검증 실패 — " + "; ".join(errors) + ". 스키마에 맞춰 다시 호출하세요."
    return tool["handler"](arguments)


def registry_notice(names):
    """시스템 프롬프트용 고지 — 레지스트리 도구는 '이름만' 공개된다 (MCP는 델타 고지가 담당).

    `# 도구 사용 정책`의 하위 섹션으로 들어가는 마크다운 조각 (prompts.build_system_prompt).
    """
    return ("## 도구 레지스트리\n"
            f"- 다음 도구들은 레지스트리에만 있어 직접 호출할 수 없습니다: {', '.join(names)}.\n"
            "- 필요하면 tool_search로 스키마를 조회한 뒤, tool_invoke(name=도구이름, "
            "arguments=스키마에 맞는 인자 객체)로 실행하세요.")
