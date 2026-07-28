"""도구 스키마 — 니치 선언·탈출구·사전경고 문구를 config 스위치에 따라 고른다.

read/edit의 소프트판·하드판 description은 cc_tools.py 원문과 문장 구성이 달라서
합성하지 않고 **각각 바이트 그대로 분기 보존**한다 (감사에서 드리프트 확인 후 원문 복원).
glob/grep은 소프트 원문 + 탈출구 문장만 dispatcher 스위치로 탈부착 (원문과 일치 확인됨).
tool_search/tool_invoke의 긴 description은 toolsearch·MCP 노트북판(정본)을 쓴다.
"""

LINE_PREFIX_WARNING = (
    "주의: read_file 결과 각 줄 앞의 '줄번호+탭'은 표시용이지 파일 내용이 아니므로 "
    "old_string에 절대 포함하지 마세요.")

READ_FILE_PARAMS = {
    "type": "object",
    "properties": {
        "file_path": {"type": "string", "description": "파일의 절대경로"},
        "offset": {"type": "integer", "description": "1부터 시작하는 시작 줄 번호"},
        "limit": {"type": "integer", "description": "읽을 줄 수"},
    },
    "required": ["file_path"],
    "additionalProperties": False,
}

EDIT_FILE_PARAMS = {
    "type": "object",
    "properties": {
        "file_path": {"type": "string", "description": "파일의 절대경로"},
        "old_string": {"type": "string", "description": "교체할 정확한 원문"},
        "new_string": {"type": "string", "description": "교체 후 텍스트"},
        "replace_all": {"type": "boolean", "description": "모든 일치 항목을 교체할지 여부"},
    },
    "required": ["file_path", "old_string", "new_string", "replace_all"],
    "additionalProperties": False,
}

# 탈출구 문구 (CC 원문 번역) — agent_search가 레지스트리에 있을 때만 붙는다
ESCAPE_HATCH = ("여러 라운드의 glob과 grep이 필요할 수 있는 열린 탐색이라면 "
                "이 도구 대신 agent_search 도구를 사용하세요.")


def glob_tool(dispatcher=True):
    desc = ("빠른 파일 패턴 매칭 도구입니다. '/project/**/*.py' 같은 glob 패턴을 지원합니다. "
            "매칭된 파일 경로를 수정 시간순으로 반환합니다. "
            "이름 패턴으로 파일을 찾아야 할 때 이 도구를 사용하세요. ")   # 니치 선언
    if dispatcher:
        desc += ESCAPE_HATCH                                              # 탈출구
    return {
        "type": "function", "name": "glob_files", "strict": False,
        "description": desc.strip(),
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "glob 패턴, 예: '/project/src/*.py'"},
            },
            "required": ["pattern"],  # 입장권: 패턴 하나 = 공짜
            "additionalProperties": False,
        },
    }


def grep_tool(dispatcher=True):
    desc = ("정규식 기반의 강력한 내용 검색 도구입니다. "
            "파일의 내용(CONTENT)을 검색해야 할 때 이 도구를 사용하세요. "   # 니치 선언
            "기본 output_mode 'files_with_matches'는 파일 경로만 반환합니다. "
            "매칭된 줄을 보려면 'content'로 바꾸세요. ")
    if dispatcher:
        desc += ESCAPE_HATCH                                              # 탈출구
    return {
        "type": "function", "name": "grep_files", "strict": False,
        "description": desc.strip(),
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "검색할 정규식"},
                "path": {"type": "string", "description": "검색할 디렉토리"},
                "glob": {"type": "string", "description": "'*.py' 같은 파일명 필터"},
                "output_mode": {"type": "string", "enum": ["files_with_matches", "content", "count"]},
                "head_limit": {"type": "integer", "description": "content 모드 최대 출력 줄 수"},
            },
            "required": ["pattern"],  # 입장권: 역시 패턴 하나 = 공짜 (나머지 전부 optional)
            "additionalProperties": False,
        },
    }


def read_tool(hard_gates=True):
    if hard_gates:  # cc_tools.py HARD_TOOLS 원문 (사전경고 겹1 포함)
        desc = ("파일시스템에서 파일을 읽습니다. "
                "file_path 파라미터는 상대경로가 아닌 절대경로(ABSOLUTE)여야 합니다. "
                "특정 부분만 읽으려면 offset/limit을 사용하세요. "
                "참고: 부분읽기는 편집을 위한 '읽음'으로 인정되지 않습니다.")
    else:           # cc_tools.py SOFT_TOOLS 원문 (조달 입장권)
        desc = ("파일시스템에서 파일을 읽습니다. "
                "file_path 파라미터는 상대경로가 아닌 절대경로(ABSOLUTE)여야 합니다. "
                "기본적으로 최대 2000줄을 읽습니다. 특정 부분만 읽으려면 offset/limit을 사용하세요.")
    return {"type": "function", "name": "read_file", "strict": False,
            "description": desc, "parameters": READ_FILE_PARAMS}


def edit_tool(hard_gates=True):
    if hard_gates:  # cc_tools.py HARD_TOOLS 원문 (사전경고 겹1 포함)
        desc = ("파일 안의 문자열을 정확 일치로 교체합니다. "
                "편집하기 전에 이 대화에서 read_file 도구를 최소 한 번 사용해야 합니다. "
                "파일을 읽지 않고 편집을 시도하면 이 도구는 에러를 냅니다. "
                "old_string은 파일 내용과 정확히 일치해야 하며, replace_all이 true가 아니라면 유일해야 합니다. "
                + LINE_PREFIX_WARNING)
    else:           # cc_tools.py SOFT_TOOLS 원문 (old_string 조달 경로 명시)
        desc = ("파일 안의 문자열을 정확 일치로 교체합니다. "
                "old_string은 파일 내용과 정확히(EXACTLY) 일치해야 하며(read_file 결과에서 복사), "
                "replace_all이 true가 아니라면 파일 안에서 유일해야 합니다. " + LINE_PREFIX_WARNING)
    return {"type": "function", "name": "edit_file", "strict": True,  # 변이 도구만 strict — 하이브리드 배치
            "description": desc, "parameters": EDIT_FILE_PARAMS}


def write_tool(hard_gates=True):
    desc = "파일을 씁니다. 이미 존재하면 덮어씁니다. "
    if hard_gates:
        desc += ("기존(EXISTING) 파일을 덮어쓰려면 먼저 읽어야 합니다 - 아니면 이 도구는 "
                 "에러를 냅니다. ")                                               # 사전경고 (겹1)
    desc += "부분 수정에는 edit_file을 사용하세요."
    return {
        "type": "function", "name": "write_file", "strict": True,
        "description": desc,
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "파일의 절대경로"},
                "content": {"type": "string", "description": "파일에 쓸 전체 내용"},
            },
            "required": ["file_path", "content"],
            "additionalProperties": False,
        },
    }


def run_command_tool():
    return {
        "type": "function", "name": "run_command", "strict": True,
        "description": "셸 명령을 실행하고 stdout, stderr, 종료 코드(exit code)를 반환한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "실행할 셸 명령 전체 문자열"},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    }


# ── 디스패처 동결 도구 2개 — description이 곧 사용법 지식의 거처 ─────
# (CLAUDE.md 규약의 명시 예외: ToolSearch 계열은 쿼리 형식까지 description에 길게 쓴다)
def tool_search_def(mcp=False):
    desc = ("사용 가능한 도구를 검색해 스키마를 로드한다. "
            "일부 도구는 tools에 미리 선언되지 않는다(deferred)")
    if mcp:
        # MCP 델타 고지가 켜진 세션용 문장 (cc_mcp_connect_disconnect 노트북판)
        desc += (" — 대화 중간의 <system-reminder> 고지에 이름만 나타난다. "
                 "스키마를 로드하기 전에는 이름만 알 뿐 파라미터를 모르므로 실행할 수 없다 — "
                 "먼저 이 도구로 스키마를 받은 다음에만 tool_invoke로 실행할 수 있다. "
                 "'no longer available' 고지에 나온 도구는 검색해도 no match를 돌려준다. ")
    else:
        desc += (" — 스키마를 로드하기 전에는 파라미터를 모르므로 실행할 수 없고, "
                 "먼저 이 도구로 스키마를 받은 다음에만 tool_invoke로 실행할 수 있다. "
                 "작업에 필요한 도구가 tools에 보이지 않으면 반드시 이 도구로 먼저 검색한다. ")
    desc += ("쿼리 형식: (1) 'select:이름1,이름2' — 정확한 이름 직조회, 쉼표로 여러 개. "
             "(2) 일반 키워드 — 조사를 뺀 명사를 공백으로 구분해 후보 검색. 예: '슬랙 메시지 전송'. "
             "(3) '+키워드' — 반드시 매칭돼야 하는 필수 키워드.")
    return {
        "type": "function", "name": "tool_search", "strict": False,
        "description": desc,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": ("정확한 이름을 알면 'select:도구이름' (쉼표로 여러 개 가능). "
                                          "모르면 조사를 뺀 명사 키워드를 공백으로 구분해 입력. "
                                          "예: '슬랙 메시지 전송'")},
            },
            "required": ["query"],
        },
    }


def tool_invoke_def():
    return {
        "type": "function", "name": "tool_invoke", "strict": False,
        "description": ("tool_search로 스키마를 확인한 도구를 실제로 실행한다. "
                        "모든 deferred 도구 실행은 이 통로로만 한다. "
                        "스키마를 로드하지 않은 도구를 호출하면 에러와 함께 로드 방법이 안내된다."),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "실행할 도구 이름"},
                "arguments": {"type": "object", "description": "그 도구의 스키마에 맞춘 인자 객체"},
            },
            "required": ["name", "arguments"],
        },
    }


# ── 레지스트리(디퍼드) 도구 2개 — tools 배열에 안 실린다 ────────────
AGENT_SEARCH_TOOL = {
    "type": "function", "name": "agent_search", "strict": False,
    "description": (
        "열린 탐색을 위한 자율 검색 에이전트입니다. 알고 싶은 것을 설명하면 "
        "내부에서 여러 라운드의 glob·grep·read를 수행하고 요약만 반환합니다. "
        "검색 패턴 하나로는 답이 나오지 않는 질문, 특히 프로젝트 전반을 훑어 "
        "요약해야 하는 질문에 가장 적합합니다."),   # 탈출구의 목적지 — 위임→요약
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "조사할 내용 (영문 키워드로 작성)"},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}

TODO_WRITE_TOOL = {
    "type": "function", "name": "todo_write", "strict": False,
    "description": (
        "작업 todo 목록을 생성하거나 갱신합니다. 여러 단계 작업의 진행 상황을 추적할 때 "
        "사용하세요(시작 시 in_progress, 완료 시 completed)."),
    "parameters": {
        "type": "object",
        "properties": {
            "todos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "status": {"type": "string",
                                   "enum": ["pending", "in_progress", "completed"]},
                    },
                    "required": ["content", "status"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["todos"],
        "additionalProperties": False,
    },
}


def freeze_tools(tools):
    """캐시 보존 규약을 한 곳에 명문화 — 이름순 정렬(결정론적 직렬화) 후 반환.
    반환된 배열은 세션 내내 불변이어야 한다 (OpenAI 캐시는 exact prefix match)."""
    return sorted(tools, key=lambda t: t["name"])
