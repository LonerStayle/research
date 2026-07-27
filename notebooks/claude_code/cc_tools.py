"""cc_tool_sequence_{soft,hard}_rules 노트북 공용 — 소프트/하드 도구·세션 한 파일.

두 노트북(소프트=입장권·넛지, 하드=readFileState 5겹 게이트)이 **같은 이 파일**을 쓴다.
read/edit/write는 한 벌뿐이고, 스위치 2개로 소프트/하드가 갈린다:
  - nudges=True   → 소프트 넛지(오타·재읽기 스텁·잘림 리다이렉트)
  - state=<dict>  → 하드 readFileState 게이트(읽기 강제·낡은읽기·성공 후 자가갱신)
tool_search·tool_invoke 디스패처도 여기 한 벌(레지스트리 도구는 tools에 안 싣고 tool_invoke 경유).

노트북에서 (별칭으로 소프트/하드 심볼만 골라 쓴다):
    소프트: from cc_tools import SoftSession as Session, SOFT_TOOLS as TOOLS, ...
    하드:   from cc_tools import HardSession as Session, HARD_TOOLS as TOOLS, ...
"""

import difflib
import fnmatch
import json
import re
from functools import partial

from cc_mock_fs import FS as _SOURCE_FS

# ═════════════════════════════════════════════════════════════════════
# 공통 — 목 파일시스템, read/edit/write 한 벌, 디스패처, BaseSession
# ═════════════════════════════════════════════════════════════════════
_CLOCK = 0


def _tick():
    global _CLOCK
    _CLOCK += 1
    return _CLOCK


FS = {}  # path -> {"content": str, "mtime": int}


def _seed(path, content):
    FS[path] = {"content": content.strip("\n") + "\n", "mtime": _tick()}


def reset_fs():
    """공통 목 코드베이스(orderhub, 40파일)로 FS를 초기화한다. 시드된 파일 수를 반환."""
    FS.clear()
    for path, content in _SOURCE_FS.items():
        _seed(path, content)
    return len(FS)


def external_modify(path, content):
    """모델 모르게 파일이 바뀌는 상황(사용자 편집·린터) 시뮬레이션 — 하드 게이트2 실습용."""
    FS[path] = {"content": content.strip("\n") + "\n", "mtime": _tick()}
    print(f"⚡ (외부 수정 발생) {path} — mtime {FS[path]['mtime']}")


reset_fs()

# ── 출력 상한 (CC 원값) + 넛지 문구 ─────────────────────────────────
GLOB_LIMIT = 100          # CC GlobTool: 100개에서 잘림
GREP_HEAD_LIMIT = 250     # CC GrepTool: content 모드 기본 head_limit
READ_MAX_LINES = 2000     # CC FileReadTool: 기본 2000줄

TRUNCATION_NUDGE = "(결과가 잘렸습니다. 더 구체적인 경로나 패턴을 사용해 보세요.)"
FILE_UNCHANGED_STUB = (
    "마지막으로 읽은 이후 파일이 변하지 않았습니다. 이 대화의 앞선 read_file 결과 내용이 "
    "여전히 유효합니다 - 다시 읽지 말고 그것을 참조하세요."
)


def _glob_to_regex(pattern):
    # fnmatch는 '**'를 모르고 '*'가 '/'를 넘어가 버림 → 진짜 glob 의미론으로 번역
    # '**/' = 0개 이상의 디렉토리, '*' = '/' 제외 임의 문자열
    out, i = "", 0
    while i < len(pattern):
        if pattern[i:i + 3] == "**/":
            out += "(?:.*/)?"
            i += 3
        elif pattern[i:i + 2] == "**":
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile("^" + out + "$")


def numbered_lines(lines, start, end):
    # read 결과의 '줄번호+탭' 표시 — 표시용일 뿐 파일 내용이 아니다 (edit description 경고와 한 쌍)
    return "\n".join(f"{i + 1:6}\t{lines[i]}" for i in range(start, end))


def exact_replace(file_path, old_string, new_string, replace_all=False):
    """edit 공통 코어 — 정확 일치 교체. 성공/에러 문자열을 반환한다 (게이트는 호출측 책임)."""
    content = FS[file_path]["content"]
    n = content.count(old_string)
    if n == 0:
        return f"ERROR: 바꿀 문자열을 파일에서 찾지 못했습니다.\n문자열: {old_string}"
    if n > 1 and not replace_all:
        # 다중매칭 넛지 — 복구 방법 2가지를 정확히 알려준다
        return (f"ERROR: 바꿀 문자열이 {n}곳에서 발견되었지만 replace_all이 false입니다. "
                "전부 바꾸려면 replace_all을 true로 설정하세요. 한 곳만 바꾸려면 "
                "컨텍스트를 더 넓혀 대상을 유일하게 지정하세요.")
    FS[file_path] = {"content": content.replace(old_string, new_string), "mtime": _tick()}
    return f"{file_path} 파일이 수정되었습니다. {n}곳을 교체했습니다."


# ── read/edit/write 한 벌 — 소프트/하드가 스위치 2개로 공유 ─────────
#   nudges=True   → 소프트 넛지(오타·재읽기 스텁·잘림 리다이렉트) 켜짐
#   state=<dict>  → 하드 readFileState 게이트 켜짐(읽기 강제·낡은읽기·성공 후 자가갱신)
#   둘 다 안 주면 게이트도 넛지도 없는 맨몸 도구.
LAST_READ = {}  # 소프트 재읽기 절약 스텁 추적 (게이트 아님): path -> (mtime, offset, limit)


def read_file(file_path, offset=None, limit=None, *, state=None, nudges=False):
    if not file_path.startswith("/"):
        # 입장권 검사: read의 입장권은 '절대경로' — 지어낼 수 없고 앞 단계 출력에서 조달해야 한다
        return "ERROR: file_path는 상대경로가 아닌 절대경로여야 합니다."
    if file_path not in FS:
        if nudges:
            close = difflib.get_close_matches(file_path, FS.keys(), n=1)
            hint = f" 혹시 {close[0]} 파일을 찾으시나요?" if close else ""
            return f"ERROR: 파일이 존재하지 않습니다.{hint}"  # 오타 넛지 (CC suggestPathUnderCwd)
        return "ERROR: 파일이 존재하지 않습니다."

    entry = FS[file_path]
    # 재읽기 절약 스텁 — 같은 범위 + 파일 안 바뀜이면 본문 대신 스텁 한 줄 (소프트 전용)
    if nudges and LAST_READ.get(file_path) == (entry["mtime"], offset, limit):
        return FILE_UNCHANGED_STUB

    lines = entry["content"].splitlines()
    start = (offset - 1) if offset else 0
    end = min(start + limit, len(lines)) if limit else len(lines)
    end = min(end, start + READ_MAX_LINES)
    body = numbered_lines(lines, start, end)
    if end < len(lines) and nudges:
        # 에러 리다이렉트: 막지 않고 '대신 이렇게'를 결과에 심는다
        body += ("\n... (파일에 더 많은 줄이 있습니다. offset/limit 파라미터로 필요한 부분만 "
                 "읽거나, 파일 통독 대신 특정 내용을 검색하세요.)")
    if state is not None:
        # readFileState 기록 — 부분읽기는 is_partial_view=True (게이트에서 '읽음' 불인정)
        is_partial = offset is not None or limit is not None or end < len(lines)
        state[file_path] = {"timestamp": entry["mtime"], "is_partial_view": is_partial}
    if nudges:
        LAST_READ[file_path] = (entry["mtime"], offset, limit)
    return body


def _write_gates(file_path, state):
    # edit·write 공용 2중 게이트 — 에러 문구는 CC 원문 번역
    st = state.get(file_path)
    if st is None or st["is_partial_view"]:
        # 게이트1: 안 읽음 — CC errorCode 6
        return "ERROR: 파일을 아직 읽지 않았습니다. 쓰기 전에 먼저 읽으세요."
    if FS[file_path]["mtime"] > st["timestamp"]:
        # 게이트2: 낡은 읽기 — CC errorCode 7
        return ("ERROR: 읽은 이후 파일이 수정되었습니다 - 사용자에 의해서든 린터에 의해서든. "
                "쓰기 전에 다시 읽으세요.")
    return None


def edit_file(file_path, old_string, new_string, replace_all=False, *, state=None):
    # state=None(소프트): '읽기 강제' 하드 게이트가 없다 — 그런데도 old_string이 파일 원문과
    #   정확히 일치해야 하므로, read 없이 old_string을 지어낼 수 없다 = old_string 자체가 입장권.
    # state=<dict>(하드): 읽기 강제 + 낡은읽기 게이트 + 성공 후 자가갱신.
    if file_path not in FS:
        return "ERROR: 파일이 존재하지 않습니다."
    if state is not None:
        if old_string == new_string:
            return "ERROR: 바꿀 내용이 없습니다: old_string과 new_string이 완전히 동일합니다."
        gate = _write_gates(file_path, state)
        if gate:
            return gate
    result = exact_replace(file_path, old_string, new_string, replace_all)
    if state is not None and not result.startswith("ERROR"):
        # 성공 후 자가갱신 — 연속 edit이 게이트2에 걸리지 않게
        state[file_path] = {"timestamp": FS[file_path]["mtime"], "is_partial_view": False}
    return result


def write_file(file_path, content, *, state=None):
    if file_path in FS:
        if state is not None:
            gate = _write_gates(file_path, state)  # 기존 파일 덮어쓰기 전 같은 2중 검사
            if gate:
                return gate
        FS[file_path] = {"content": content, "mtime": _tick()}
        msg = f"{file_path} 파일이 수정되었습니다."
    else:
        FS[file_path] = {"content": content, "mtime": _tick()}
        msg = f"파일이 생성되었습니다: {file_path}"
    if state is not None:
        state[file_path] = {"timestamp": FS[file_path]["mtime"], "is_partial_view": False}
    return msg


# ── 공용 스키마 조각 ────────────────────────────────────────────────
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

# ── tool_search·tool_invoke 디스패처 (레지스트리 공용) ──────────────
TOOL_SEARCH_TOOL = {
    "type": "function",
    "name": "tool_search",
    "strict": False,
    "description": (
        "레지스트리 도구의 스키마를 조회합니다. 정확한 도구를 알면 'select:<이름>'으로, "
        "모르면 키워드로 검색하세요. 스키마를 확인한 뒤 tool_invoke로 실행합니다."),  # CC ToolSearch 대응
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "'select:agent_search' 또는 키워드"},
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}

TOOL_INVOKE_TOOL = {
    "type": "function",
    "name": "tool_invoke",
    "strict": False,
    "description": (
        "tool_search로 스키마를 확인한 레지스트리 도구를 실제로 실행합니다. "
        "레지스트리 도구의 실행은 모두 이 통로로만 합니다."),  # 실행 게이트웨이 (디스패처)
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "실행할 도구 이름"},
            "arguments": {"type": "object", "description": "그 도구의 스키마에 맞춘 인자 객체"},
        },
        "required": ["name", "arguments"],
        "additionalProperties": False,
    },
}


class Dispatcher:
    """레지스트리 도구용 디스패처 — 스키마는 대화로, 실행은 게이트웨이로만.

    deferred_tools: tools 배열에 싣지 않는 도구 스키마 목록 (레지스트리)
    impls: 이름 -> 구현 함수
    """

    def __init__(self, deferred_tools, impls):
        self.deferred_tools = deferred_tools
        self.impls = impls

    def registry_notice(self):
        # 시스템 프롬프트용 고지 — 레지스트리 도구는 '이름만' 공개된다
        names = ", ".join(t["name"] for t in self.deferred_tools)
        return (f"다음 도구들은 레지스트리에만 있어 직접 호출할 수 없습니다: {names}. "
                "필요하면 tool_search로 스키마를 조회한 뒤, tool_invoke(name=도구이름, "
                "arguments=스키마에 맞는 인자 객체)로 실행하세요.")

    def search(self, query):
        # CC ToolSearch 2모드 대응: 'select:이름' 정확 조회 / 키워드 검색 — 스키마는 대화로만 전달
        q = (query or "").strip()
        if q.startswith("select:"):
            names = [s.strip() for s in q[len("select:"):].split(",")]
            found = [t for t in self.deferred_tools if t["name"] in names]
        else:
            words = [w for w in re.split(r"\W+", q.lower()) if w]
            found = [t for t in self.deferred_tools
                     if any(w in (t["name"] + " " + t["description"]).lower() for w in words)]
        if not found:
            avail = ", ".join(t["name"] for t in self.deferred_tools)
            return f"일치하는 도구가 없습니다. 사용 가능한 레지스트리 도구: {avail}"
        schemas = json.dumps([{k: t[k] for k in ("name", "description", "parameters")} for t in found],
                             ensure_ascii=False)
        return ("도구 스키마:\n" + schemas
                + "\n\n이제 tool_invoke(name=도구이름, arguments=스키마에 맞는 인자 객체)로 실행하세요.")

    def invoke(self, name, arguments):
        # 실행 게이트웨이 — 서버 strict 검증이 없는 대가로 클라이언트가 직접 검증
        tool = next((t for t in self.deferred_tools if t["name"] == name), None)
        if tool is None:
            return f"ERROR: '{name}' 도구는 레지스트리에 없습니다. tool_search로 먼저 조회하세요."
        if isinstance(arguments, str):  # 모델이 객체 대신 JSON 문자열로 보낸 경우
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                return "ERROR: arguments가 올바른 JSON 객체가 아닙니다. 스키마에 맞춰 다시 호출하세요."
        params = tool["parameters"]
        errors = [f"필수 인자 '{r}' 누락" for r in params.get("required", []) if r not in arguments]
        errors += [f"스키마에 없는 인자 '{k}'" for k in arguments if k not in params["properties"]]
        if errors:
            return "ERROR: 인자 검증 실패 — " + "; ".join(errors) + ". 스키마에 맞춰 다시 호출하세요."
        return self.impls[name](**arguments)


# ── 시스템 프롬프트 조각 — 도구 '순서'에 대한 지시는 한 줄도 없다 ──
PROMPT_INTRO = (
    "당신은 사용자의 프로젝트에서 일하는 코딩 에이전트입니다. "
    "프로젝트 파일은 /project 아래에 있으며 모든 경로는 절대경로입니다.")

PROMPT_SR_CHANNEL = (  # CC prompts.ts:190 대응 — <system-reminder> 채널 정의
    "도구 결과와 사용자 메시지에는 <system-reminder> 태그나 다른 태그가 포함될 수 "
    "있습니다. 태그 안의 정보는 사용자가 아니라 시스템이 주입한 것이며, 태그가 등장한 "
    "도구 결과나 사용자 메시지와 직접적인 관련이 없을 수 있습니다.")

PROMPT_PARALLEL = (
    "한 응답에서 여러 도구를 호출할 수 있습니다. 호출들 사이에 의존성이 없다면 "
    "독립적인 도구 호출을 모두 병렬로 하세요. 단, 어떤 호출이 앞선 호출의 결과값에 "
    "의존한다면 병렬로 호출하지 말고 순차적으로 호출하세요.")

PROMPT_LANGUAGE = "한국어로 답하세요."


def build_system_prompt(*middle_sections):
    """공통 프롬프트 골격에 노트북별 정책 단락을 끼워 조립한다 (intro·SR / …정책… / 병렬·언어)."""
    parts = [PROMPT_INTRO, PROMPT_SR_CHANNEL, *middle_sections, PROMPT_PARALLEL, PROMPT_LANGUAGE]
    return "\n\n".join(parts)


# ── 에이전트 루프 ───────────────────────────────────────────────────
MODEL = "gpt-5-nano"  # 기본 모델 — 노트북에서 cts.MODEL = "..." 로 교체 가능

_client = None


def get_client():
    global _client
    if _client is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        _client = OpenAI()
    return _client


class BaseSession:
    """Responses API 에이전트 루프 공통 골격.

    - tools는 세션 내내 동결 (OpenAI 캐시는 exact prefix match — tools 변경 = 전체 미스)
    - 배치 내 도구는 받은 순서대로 순차 실행
    - 게이트·넛지·검증 에러도 정상 결과와 같은 채널(function_call_output)로 — 복구 프롬프트
    - 서브클래스 훅: _execute(호출 1건 실행, label·output 반환) / _after_round(라운드 말미)
    """

    def __init__(self, system_prompt, tools, impls, model=None):
        self.system_prompt = system_prompt
        self.tools = tools
        self.impls = impls
        self.model = model or MODEL
        self.input_list = [{"role": "developer", "content": system_prompt}]

    def _execute(self, name, args):
        try:
            output = self.impls[name](**args)
        except TypeError as e:
            # 인자 검증 게이트 — CC 도구검증 1단계 대응: 검증 실패도 에러 tool_result로 돌려 자기교정
            output = f"ERROR: 잘못된 인자입니다. 도구 스키마에 맞춰 다시 호출하세요. ({e})"
        return name, output

    def _after_round(self):
        pass

    def ask(self, question, max_rounds=200):
        print(f"💬 {question}\n")
        self.input_list.append({"role": "user", "content": question})
        for _ in range(max_rounds):
            response = get_client().responses.create(
                model=self.model, input=self.input_list, tools=self.tools)
            self.input_list += response.output
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                print(f"\n🤖 {response.output_text}")
                return response.output_text
            for call in calls:  # 받은 순서대로 순차 실행
                args = json.loads(call.arguments)
                label, output = self._execute(call.name, args)
                mark = "⛔" if output.startswith("ERROR") else "🔧"
                head = output.splitlines()[0]
                print(f"  {mark} {label}({json.dumps(args, ensure_ascii=False)[:100]})")
                print(f"     → {head[:140]}{' …' if len(output) > len(head) else ''}")
                self.input_list.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": output,
                })
            self._after_round()
        print("⚠️ 최대 라운드 초과 — 데모를 여기서 멈춥니다.")
        return None


# ═════════════════════════════════════════════════════════════════════
# 소프트 규칙 — 입장권 설계 + 문구 장치 (게이트 없음)
# ═════════════════════════════════════════════════════════════════════
# read/edit: 공통 1벌을 소프트 스위치로 고정 (넛지 O, 게이트 X)
soft_read_file = partial(read_file, nudges=True)   # 오타·재읽기 스텁·잘림 리다이렉트 켜짐
soft_edit_file = edit_file                          # state 없음 = 읽기 강제 게이트 없음


def glob_files(pattern):
    regex = _glob_to_regex(pattern)
    matches = [p for p in FS if regex.match(p)]
    if not matches:
        return "일치하는 파일이 없습니다"
    matches.sort(key=lambda p: FS[p]["mtime"], reverse=True)  # 수정시간순 — CC와 동일
    if len(matches) > GLOB_LIMIT:
        return "\n".join(matches[:GLOB_LIMIT]) + "\n" + TRUNCATION_NUDGE  # 잘림 넛지
    return "\n".join(matches)


def grep_files(pattern, path=None, glob=None, output_mode="files_with_matches", head_limit=None):
    regex = re.compile(pattern)
    scope = [p for p in sorted(FS) if p.startswith(path or "/")]
    if glob:
        scope = [p for p in scope if fnmatch.fnmatch(p.rsplit("/", 1)[-1], glob)]
    file_hits, content_lines, counts = [], [], []
    for p in scope:
        lines = FS[p]["content"].splitlines()
        hits = [(i + 1, ln) for i, ln in enumerate(lines) if regex.search(ln)]
        if hits:
            file_hits.append(p)
            counts.append(f"{p}: {len(hits)}")
            content_lines += [f"{p}:{n}:{ln}" for n, ln in hits]
    if not file_hits:
        return "일치하는 내용이 없습니다"
    # 기본 output_mode가 files_with_matches — "어느 파일인지 먼저, 상세는 그다음"
    # 순서를 처방 문구가 아니라 '기본값'이 만든다 (CC 연계⑤: 그런 처방 문구는 실제로 없음)
    if output_mode == "content":
        cap = head_limit or GREP_HEAD_LIMIT
        note = f"\n(전체 {len(content_lines)}줄 중 앞 {cap}줄만 표시)" if len(content_lines) > cap else ""
        return "\n".join(content_lines[:cap]) + note
    if output_mode == "count":
        return "\n".join(counts)
    return f"{len(file_hits)}개 파일에서 발견\n" + "\n".join(file_hits)


def agent_search(query):
    # 탈출구의 목적지: 목 서브에이전트. 내부에서 여러 라운드 glob/grep/read를 돌고
    # '요약만' 메인 컨텍스트에 반환한다 (CC 연계⑦ 위임→요약 — 가장 강력한 토큰 절약)
    keywords = re.findall(r"[A-Za-z_]{3,}", query) or ["try", "except", "raise", "error"]
    hits = []
    for p in sorted(FS):
        for i, ln in enumerate(FS[p]["content"].splitlines(), 1):
            if any(k.lower() in ln.lower() for k in keywords):
                hits.append(f"{p}:{i}: {ln.strip()}")
    digest = "\n".join(hits[:20]) or "(키워드 일치 없음)"
    return (f"[목 서브에이전트] 파일 {len(FS)}개를 내부 3라운드(glob -> grep {keywords[:5]} -> read)로 "
            f"탐색했습니다. 이 요약만 메인 컨텍스트에 들어갑니다:\n{digest}")


TODOS = []


def todo_write(todos):
    global TODOS
    TODOS = todos
    # 성공 넛지 — 결과 문구가 다음 행동(계속 추적하라)을 지시 (CC TodoWrite 원문 번역)
    return ("할 일 목록이 수정되었습니다. 계속 todo 목록으로 진행 상황을 추적하세요. "
            "해당된다면 현재 작업을 계속 진행하세요")


# ── 소프트 동결 도구 배열 (6개) — 세션 내내 불변 = 캐시 미스 0 ─────
SOFT_TOOLS = [
    {
        "type": "function",
        "name": "glob_files",
        "strict": False,
        "description": (
            "빠른 파일 패턴 매칭 도구입니다. '/project/**/*.py' 같은 glob 패턴을 지원합니다. "
            "매칭된 파일 경로를 수정 시간순으로 반환합니다. "
            "이름 패턴으로 파일을 찾아야 할 때 이 도구를 사용하세요. "              # 니치 선언
            "여러 라운드의 glob과 grep이 필요할 수 있는 열린 탐색이라면 "
            "이 도구 대신 agent_search 도구를 사용하세요."),                      # 탈출구 (CC 원문 번역)
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "glob 패턴, 예: '/project/src/*.py'"},
            },
            "required": ["pattern"],  # 입장권: 패턴 하나 = 공짜
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "grep_files",
        "strict": False,
        "description": (
            "정규식 기반의 강력한 내용 검색 도구입니다. "
            "파일의 내용(CONTENT)을 검색해야 할 때 이 도구를 사용하세요. "         # 니치 선언
            "기본 output_mode 'files_with_matches'는 파일 경로만 반환합니다. "
            "매칭된 줄을 보려면 'content'로 바꾸세요. "
            "여러 라운드의 glob과 grep이 필요할 수 있는 열린 탐색이라면 "
            "이 도구 대신 agent_search 도구를 사용하세요."),                      # 탈출구 (CC 원문 번역)
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
    },
    {
        "type": "function",
        "name": "read_file",
        "strict": False,
        "description": (
            "파일시스템에서 파일을 읽습니다. "
            "file_path 파라미터는 상대경로가 아닌 절대경로(ABSOLUTE)여야 합니다. "  # 조달 입장권
            "기본적으로 최대 2000줄을 읽습니다. 특정 부분만 읽으려면 offset/limit을 사용하세요."),
        "parameters": READ_FILE_PARAMS,
    },
    {
        "type": "function",
        "name": "edit_file",
        "strict": True,  # 변이 도구만 strict — 서버가 스키마를 강제 (하이브리드 배치)
        "description": (
            "파일 안의 문자열을 정확 일치로 교체합니다. "
            "old_string은 파일 내용과 정확히(EXACTLY) 일치해야 하며(read_file 결과에서 복사), "
            "replace_all이 true가 아니라면 파일 안에서 유일해야 합니다. "
            + LINE_PREFIX_WARNING),
        "parameters": EDIT_FILE_PARAMS,
    },
    TOOL_SEARCH_TOOL,
    TOOL_INVOKE_TOOL,
]

# 캐시 보존: 동결 배열은 6개 — 세션 내내 불변 = 캐시 미스 0
SOFT_TOOLS.sort(key=lambda t: t["name"])

# ── 레지스트리 도구: tools에 싣지 않는다 — 스키마는 tool_search 결과(대화)로, 실행은 tool_invoke로 ──
AGENT_SEARCH_TOOL = {
    "type": "function",
    "name": "agent_search",
    "strict": False,
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
    "type": "function",
    "name": "todo_write",
    "strict": False,
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
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
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

DEFERRED_TOOLS = [AGENT_SEARCH_TOOL, TODO_WRITE_TOOL]

SOFT_TOOL_IMPLS = {
    "glob_files": glob_files,
    "grep_files": grep_files,
    "read_file": soft_read_file,
    "edit_file": soft_edit_file,
    "agent_search": agent_search,
    "todo_write": todo_write,
}

# 레지스트리 도구(agent_search·todo_write)만 디스패처가 다룬다 — 실행은 tool_invoke 게이트웨이로만
dispatcher = Dispatcher(DEFERRED_TOOLS, SOFT_TOOL_IMPLS)

# 레지스트리 고지는 디스패처가 생성 (agent_search, todo_write는 이름만 공개)
_SOFT_DELEGATION_POLICY = (
    "프로젝트 전반을 훑어야 하는 열린 조사는 검색 도구를 여러 번 반복하지 말고, "
    "조사를 통째로 맡길 수 있는 도구가 있으면 그쪽에 위임하세요.")
SOFT_SYSTEM_PROMPT = build_system_prompt(dispatcher.registry_notice(), _SOFT_DELEGATION_POLICY)

TODO_SYSTEM_EXTRA = (
    "\n\n여러 단계로 이루어진 작업은 시작할 때 todo_write로 계획을 먼저 기록하고, 각 단계를 "
    "시작할 때 in_progress로, 마칠 때 completed로 부지런히 갱신하세요.")
# ↑ CC 시스템 프롬프트의 태스크 관리 섹션(todo 사용의 주 동력) 대응 — todo 모드에서만 주입

REMINDER_THRESHOLD = 2  # CC는 10턴 (TURNS_SINCE_WRITE:10) — 데모라 2로 축소


def neglect_reminder():
    body = ("todo 도구가 최근 사용되지 않았습니다. 진행 상황 추적이 도움될 작업 중이라면 todo_write로 "
            "태스크를 추가하고 상태를 갱신하는 것을 고려하세요(시작 시 in_progress, 완료 시 completed). "
            "현재 작업에 관련될 때만 사용하세요. 이것은 부드러운 리마인더일 뿐입니다 - 해당 없으면 "
            "무시하세요.")
    if TODOS:
        # CC와 동일: 목록이 비어 있어도 발동하되(빈 체크 없음), 있으면 현재 목록을 함께 첨부
        body += "\n\n현재 todo 목록:\n" + "\n".join(f"- [{t['status']}] {t['content']}" for t in TODOS)
    return f"<system-reminder>\n{body}\n</system-reminder>"


class SoftSession(BaseSession):
    """소프트 규칙 세션 — 디스패처 경유 실행 + (todo 모드) 방치 리마인더."""

    def __init__(self, todo_mode=False, model=None):
        global TODOS
        TODOS = []              # todo 목록은 세션 단위
        LAST_READ.clear()       # 재읽기 스텁 추적은 세션 단위 — 새 세션의 첫 read가 스텁이 되면 안 됨
        self.todo_mode = todo_mode  # 데모 4 전용: 태스크 관리 권장 + 방치 리마인더
        prompt = SOFT_SYSTEM_PROMPT + (TODO_SYSTEM_EXTRA if todo_mode else "")
        super().__init__(prompt, SOFT_TOOLS, SOFT_TOOL_IMPLS, model=model)  # tools 동결 — 캐시 미스 0
        self.rounds_since_todo = 0
        self.reminder_sent = False
        self._used_todo_this_round = False

    def _execute(self, name, args):
        # 디스패처 특수 처리 — 레지스트리 도구는 tool_search 조회 후 tool_invoke 게이트웨이로만
        if name == "tool_search":
            return name, dispatcher.search(args.get("query", ""))  # 스키마는 대화로만 전달
        if name == "tool_invoke":
            target = args.get("name", "")
            output = dispatcher.invoke(target, args.get("arguments", {}))
            if target == "todo_write" and not output.startswith("ERROR"):
                self._used_todo_this_round = True
            return f"tool_invoke→{target or '?'}", output
        return super()._execute(name, args)

    def _after_round(self):
        # ── 방치 리마인더 (todo 모드 전용): 방치가 '감지된 라운드'에만 주입 ──
        if not self.todo_mode:
            return
        if self._used_todo_this_round:
            self.rounds_since_todo = 0
        else:
            self.rounds_since_todo += 1
        self._used_todo_this_round = False
        if self.rounds_since_todo >= REMINDER_THRESHOLD and not self.reminder_sent:
            self.input_list.append({"role": "developer", "content": neglect_reminder()})
            self.reminder_sent = True
            print("  📎 (todo 방치 감지 → system-reminder 주입)")


# ═════════════════════════════════════════════════════════════════════
# 하드 규칙 — Read→Edit readFileState 5겹 게이트
# ═════════════════════════════════════════════════════════════════════
# path -> {"timestamp": 읽은 시점의 mtime, "is_partial_view": bool}
READ_FILE_STATE = {}

# read/edit/write: 공통 1벌을 하드 스위치로 고정 (게이트 켜짐, 넛지 X)
hard_read_file = partial(read_file, state=READ_FILE_STATE)    # 읽음 기록(부분읽기 불인정)
hard_edit_file = partial(edit_file, state=READ_FILE_STATE)    # 읽기 강제 + 낡은읽기 + 자가갱신
hard_write_file = partial(write_file, state=READ_FILE_STATE)  # 기존 파일 덮어쓰기 전 같은 2중 검사

HARD_TOOLS = [
    {
        "type": "function",
        "name": "read_file",
        "strict": False,
        "description": (
            "파일시스템에서 파일을 읽습니다. "
            "file_path 파라미터는 상대경로가 아닌 절대경로(ABSOLUTE)여야 합니다. "
            "특정 부분만 읽으려면 offset/limit을 사용하세요. "
            "참고: 부분읽기는 편집을 위한 '읽음'으로 인정되지 않습니다."),
        "parameters": READ_FILE_PARAMS,
    },
    {
        "type": "function",
        "name": "edit_file",
        "strict": True,
        "description": (
            "파일 안의 문자열을 정확 일치로 교체합니다. "
            "편집하기 전에 이 대화에서 read_file 도구를 최소 한 번 사용해야 합니다. "
            "파일을 읽지 않고 편집을 시도하면 이 도구는 에러를 냅니다. "             # 사전경고 (겹1)
            "old_string은 파일 내용과 정확히 일치해야 하며, replace_all이 true가 아니라면 유일해야 합니다. "
            + LINE_PREFIX_WARNING),
        "parameters": EDIT_FILE_PARAMS,
    },
    {
        "type": "function",
        "name": "write_file",
        "strict": True,
        "description": (
            "파일을 씁니다. 이미 존재하면 덮어씁니다. "
            "기존(EXISTING) 파일을 덮어쓰려면 먼저 읽어야 합니다 - 아니면 이 도구는 "
            "에러를 냅니다. 부분 수정에는 edit_file을 사용하세요."),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "파일의 절대경로"},
                "content": {"type": "string", "description": "파일에 쓸 전체 내용"},
            },
            "required": ["file_path", "content"],
            "additionalProperties": False,
        },
    },
]

HARD_TOOLS.sort(key=lambda t: t["name"])  # 캐시 보존: 결정론적 직렬화 + 세션 내 동결

HARD_TOOL_IMPLS = {
    "read_file": hard_read_file,
    "edit_file": hard_edit_file,
    "write_file": hard_write_file,
}

# 하드 노트북은 병렬·SR 채널·언어만 — 디스패처/위임 정책 없음
HARD_SYSTEM_PROMPT = build_system_prompt()


class HardSession(BaseSession):
    """하드 규칙 세션 — readFileState는 세션 단위 상태로 리셋된다 (CC와 동일)."""

    def __init__(self, model=None):
        READ_FILE_STATE.clear()  # readFileState는 세션 단위 상태 (CC와 동일)
        super().__init__(HARD_SYSTEM_PROMPT, HARD_TOOLS, HARD_TOOL_IMPLS, model=model)

    def ask(self, question, max_rounds=8):
        return super().ask(question, max_rounds=max_rounds)
