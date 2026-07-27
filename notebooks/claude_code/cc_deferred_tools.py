"""ToolSearch 계열 노트북 공용 — tool_search로 검색되는 도구(deferred) 스키마 레지스트리.

tools 배열에는 tool_search / tool_invoke 2개만 싣고(동결 → KV 캐시 미스 0), 실제 업무
도구들은 여기 레지스트리에만 둔다. 모델은 tool_search로 스키마를 조회한 뒤 tool_invoke로만
실행한다. 레지스트리는 리스트라 새 도구를 계속 append로 붙일 수 있다("어팬드하는 느낌").

FS 도구(read/edit/write)는 성격이 달라 cc_tools.py에 따로 있다 — 이 파일은 업무 도구 전용.

노트북에서:
    cc_toolsearch_kv_cache:            from cc_deferred_tools import make_tool, REGISTRY
    cc_mcp_connect_disconnect_kv_cache: from cc_deferred_tools import make_tool, MCP_SERVERS, ALL_MCP_TOOLS

내보내는 것:
    GENERIC_TOOLS   — 일반 업무 도구 24개 (슬랙·캘린더·메일·지라·깃허브·노션·날씨·번역·환율·DB·파일·리마인더)
    AGENT_SEARCH    — 열린 탐색 위임용 자율 검색 도구 1개
    MCP_SERVERS     — 서버별로 묶은 MCP 도구 (연결 상태에 따라 검색 노출이 바뀌는 노트북용)
    ALL_MCP_TOOLS   — MCP 도구 평면 딕셔너리
    GENERIC_REGISTRY— GENERIC_TOOLS + AGENT_SEARCH 평면 딕셔너리 (25개)
    REGISTRY        — 위 전부를 합친 평면 딕셔너리 (36개). 중복 이름은 먼저 온 것 하나만.
"""

import json


def make_tool(name, description, params, handler=None, hint=""):
    """레지스트리 항목 생성. params = {인자이름: (타입, 설명)}, 전부 필수 인자로 취급.
    hint는 클로드코드의 searchHint에 해당하는 큐레이션 검색 힌트 (선택)."""
    properties = {k: {"type": t, "description": d} for k, (t, d) in params.items()}

    def default_handler(args, _name=name):
        return f"[가짜 실행 결과] {_name} 실행 완료 — 입력: {json.dumps(args, ensure_ascii=False)}"

    return {
        "name": name,
        "description": description,
        "search_hint": hint,
        "parameters": {"type": "object", "properties": properties, "required": list(params)},
        "handler": handler or default_handler,
    }


# ═════════════════════════════════════════════════════════════════════
# 1. 일반 업무 도구 24개 (cc_toolsearch_kv_cache 원본)
# ═════════════════════════════════════════════════════════════════════
GENERIC_TOOLS = [
    make_tool("slack_send", "슬랙 채널에 새 메시지를 보낼 때 사용. 알림, 공지, 결과 보고 전송.",
              {"channel": ("string", "채널 이름. 예: #general"), "text": ("string", "보낼 메시지 내용")},
              handler=lambda args: f"[가짜 실행 결과] {args['channel']} 채널에 메시지 전송 완료: \"{args['text']}\""),
    make_tool("slack_read", "슬랙 채널의 최근 메시지를 읽을 때 사용.",
              {"channel": ("string", "채널 이름"), "limit": ("integer", "가져올 메시지 개수")}),
    make_tool("slack_search", "슬랙 전체에서 키워드로 과거 메시지를 찾을 때 사용.",
              {"keyword": ("string", "검색 키워드")}),
    make_tool("calendar_create_event", "캘린더에 새 일정을 등록할 때 사용. 회의, 약속 생성.",
              {"title": ("string", "일정 제목"), "date": ("string", "날짜 YYYY-MM-DD"), "time": ("string", "시작 시각 HH:MM")},
              handler=lambda args: f"[가짜 실행 결과] 일정 등록 완료: {args['date']} {args['time']} \"{args['title']}\" (event_id=evt_1042)"),
    make_tool("calendar_list_events", "특정 날짜에 어떤 일정이 있는지 확인할 때 사용.",
              {"date": ("string", "날짜 YYYY-MM-DD")}),
    make_tool("calendar_delete_event", "등록된 일정을 취소할 때 사용.",
              {"event_id": ("string", "일정 ID")}),
    make_tool("gmail_send", "이메일을 보낼 때 사용.",
              {"to": ("string", "받는 사람 주소"), "subject": ("string", "제목"), "body": ("string", "본문")},
              hint="메일 이메일 전송 발송"),
    make_tool("gmail_search", "받은 메일함에서 메일을 찾을 때 사용.",
              {"query": ("string", "검색어")}),
    make_tool("gmail_read", "메일 한 통의 본문을 읽을 때 사용.",
              {"message_id": ("string", "메일 ID")}),
    make_tool("jira_create_issue", "지라에 새 이슈(티켓)를 만들 때 사용.",
              {"project": ("string", "프로젝트 키"), "title": ("string", "이슈 제목"), "description": ("string", "이슈 내용")},
              hint="지라 이슈 티켓 생성"),
    make_tool("jira_search_issues", "지라에서 이슈를 검색할 때 사용.",
              {"keyword": ("string", "검색 키워드")}),
    make_tool("jira_add_comment", "지라 이슈에 댓글을 달 때 사용.",
              {"issue_id": ("string", "이슈 ID"), "comment": ("string", "댓글 내용")}),
    make_tool("github_create_pr", "깃허브에 풀리퀘스트를 만들 때 사용.",
              {"repo": ("string", "저장소 이름"), "title": ("string", "PR 제목"), "branch": ("string", "브랜치 이름")}),
    make_tool("github_list_issues", "깃허브 저장소의 이슈 목록을 볼 때 사용.",
              {"repo": ("string", "저장소 이름")}),
    make_tool("github_merge_pr", "깃허브 풀리퀘스트를 머지할 때 사용.",
              {"repo": ("string", "저장소 이름"), "pr_number": ("integer", "PR 번호")}),
    make_tool("notion_create_page", "노션에 새 문서 페이지를 만들 때 사용.",
              {"title": ("string", "페이지 제목"), "content": ("string", "페이지 내용")}),
    make_tool("notion_search", "노션에서 문서를 검색할 때 사용.",
              {"keyword": ("string", "검색 키워드")},
              hint="노션 문서 페이지 검색"),
    make_tool("weather_get", "특정 도시의 현재 날씨를 확인할 때 사용.",
              {"city": ("string", "도시 이름. 예: 서울")},
              handler=lambda args: f"[가짜 실행 결과] {args['city']} 현재 날씨: 맑음, 기온 31도, 습도 62%",
              hint="날씨 기온 조회"),
    make_tool("translate_text", "문장을 다른 언어로 번역할 때 사용.",
              {"text": ("string", "번역할 문장"), "target_lang": ("string", "목표 언어. 예: en, ja")},
              hint="번역 언어 변환"),
    make_tool("currency_convert", "환율 기준으로 금액을 다른 통화로 바꿀 때 사용.",
              {"amount": ("number", "금액"), "from_currency": ("string", "원래 통화. 예: KRW"), "to_currency": ("string", "바꿀 통화. 예: USD")}),
    make_tool("db_query", "사내 데이터베이스에 SQL 조회를 실행할 때 사용.",
              {"sql": ("string", "실행할 SQL")},
              hint="데이터베이스 DB SQL 조회"),
    make_tool("file_read", "파일 내용을 읽을 때 사용.",
              {"path": ("string", "파일 경로")}),
    make_tool("file_write", "파일에 내용을 저장할 때 사용.",
              {"path": ("string", "파일 경로"), "content": ("string", "저장할 내용")}),
    make_tool("reminder_create", "지정한 시각에 알림을 만들 때 사용.",
              {"text": ("string", "알림 내용"), "when": ("string", "알림 시각 YYYY-MM-DD HH:MM")}),
]


# ═════════════════════════════════════════════════════════════════════
# 2. agent_search — 열린 탐색 위임용 자율 검색 도구 (검색 패턴 하나로 안 끝나는 질문용)
# ═════════════════════════════════════════════════════════════════════
def _agent_search_handler(args):
    q = args.get("query", "")
    return (f"[가짜 실행 결과] agent_search: 내부에서 slack_search·gmail_search·notion_search·"
            f"jira_search_issues를 여러 라운드 돌려 '{q}' 관련 자료를 훑었습니다. "
            "요약만 메인 컨텍스트에 반환합니다:\n"
            "- 슬랙 #general 관련 논의 2건 (지난주)\n"
            "- 노션 기획 문서 1건\n"
            "- 지라 진행 중 이슈 1건")


AGENT_SEARCH = make_tool(
    "agent_search",
    "열린 탐색을 위한 자율 검색 에이전트입니다. 알고 싶은 것을 설명하면 내부에서 여러 소스"
    "(슬랙·메일·노션·지라)를 여러 라운드 검색하고 요약만 반환합니다. 검색어 하나로는 답이 "
    "나오지 않는, 여러 소스를 훑어 종합해야 하는 조사에 가장 적합합니다.",
    {"query": ("string", "조사할 내용을 문장으로 설명")},
    handler=_agent_search_handler,
    hint="검색 조사 자율 에이전트 탐색 리서치",
)


# ═════════════════════════════════════════════════════════════════════
# 3. MCP 서버별 도구 (cc_mcp_connect_disconnect_kv_cache 원본) — 서버 그룹 보존
# ═════════════════════════════════════════════════════════════════════
MCP_SERVERS = {
    "slack": [
        make_tool("mcp__slack__send_message", "슬랙 채널에 새 메시지를 보낼 때 사용. 알림, 공지, 결과 보고 전송.",
                  {"channel": ("string", "채널 이름. 예: #dev"), "text": ("string", "보낼 메시지 내용")},
                  handler=lambda args: f"[가짜 실행 결과] {args['channel']} 채널에 메시지 전송 완료: \"{args['text']}\"",
                  hint="슬랙 메시지 전송 공지"),
        make_tool("mcp__slack__read_channel", "슬랙 채널의 최근 메시지를 읽을 때 사용.",
                  {"channel": ("string", "채널 이름"), "limit": ("integer", "가져올 메시지 개수")}),
        make_tool("mcp__slack__search_messages", "슬랙 전체에서 키워드로 과거 메시지를 찾을 때 사용.",
                  {"keyword": ("string", "검색 키워드")}),
    ],
    "github": [
        make_tool("mcp__github__create_pr", "깃허브에 풀리퀘스트를 만들 때 사용.",
                  {"repo": ("string", "저장소 이름"), "title": ("string", "PR 제목"), "branch": ("string", "브랜치 이름")}),
        make_tool("mcp__github__list_issues", "깃허브 저장소의 열린 이슈 목록을 볼 때 사용.",
                  {"repo": ("string", "저장소 이름")},
                  handler=lambda args: f"[가짜 실행 결과] {args['repo']} 열린 이슈 3건: #12 로그인 버그, #15 다크모드 요청, #18 배포 스크립트 개선"),
        make_tool("mcp__github__merge_pr", "깃허브 풀리퀘스트를 머지할 때 사용.",
                  {"repo": ("string", "저장소 이름"), "pr_number": ("integer", "PR 번호")}),
    ],
    "figma": [
        make_tool("mcp__figma__search_files", "피그마에서 디자인 파일을 검색할 때 사용.",
                  {"keyword": ("string", "검색 키워드")},
                  handler=lambda args: f"[가짜 실행 결과] '{args['keyword']}' 검색 결과 2건: fig_101 \"로그인 화면 v2\", fig_087 \"로그인 화면 (구버전)\"",
                  hint="피그마 디자인 파일 검색"),
        make_tool("mcp__figma__get_design", "피그마 디자인 파일의 상세 내용을 가져올 때 사용.",
                  {"file_key": ("string", "파일 키. 예: fig_101")}),
        make_tool("mcp__figma__export_asset", "피그마 디자인을 이미지 파일로 내보낼 때 사용.",
                  {"file_key": ("string", "파일 키"), "format": ("string", "내보낼 형식. 예: png, svg")}),
    ],
    "supabase": [
        make_tool("mcp__supabase__run_sql", "수파베이스 데이터베이스에 SQL을 실행할 때 사용.",
                  {"sql": ("string", "실행할 SQL")},
                  hint="데이터베이스 DB SQL 조회"),
        make_tool("mcp__supabase__list_tables", "수파베이스 데이터베이스의 테이블 목록을 볼 때 사용.",
                  {"schema_name": ("string", "스키마 이름. 예: public")}),
    ],
}

ALL_MCP_TOOLS = {t["name"]: t for tools in MCP_SERVERS.values() for t in tools}


# ═════════════════════════════════════════════════════════════════════
# 4. 병합 레지스트리 — 중복 이름은 먼저 온 것 하나만 (first-wins)
# ═════════════════════════════════════════════════════════════════════
def _merge(*tool_lists):
    reg = {}
    for tools in tool_lists:
        for t in tools:
            reg.setdefault(t["name"], t)  # 중복 키는 하나만
    return reg


# 일반 도구 + agent_search (툴서치 노트북의 기본 검색 범위)
GENERIC_REGISTRY = _merge(GENERIC_TOOLS, [AGENT_SEARCH])

# 전부 합친 공용 풀 (일반 + agent_search + MCP 전부) — 36개
REGISTRY = _merge(GENERIC_TOOLS, [AGENT_SEARCH], list(ALL_MCP_TOOLS.values()))


if __name__ == "__main__":
    print(f"GENERIC_TOOLS: {len(GENERIC_TOOLS)}개")
    print(f"AGENT_SEARCH: {AGENT_SEARCH['name']}")
    print(f"MCP_SERVERS: 서버 {len(MCP_SERVERS)}개, 도구 {len(ALL_MCP_TOOLS)}개")
    print(f"GENERIC_REGISTRY: {len(GENERIC_REGISTRY)}개")
    print(f"REGISTRY(전체 병합): {len(REGISTRY)}개")
    print()
    print("REGISTRY 이름:")
    print(", ".join(REGISTRY))
