"""파일시스템 도구 한 벌 — 소프트 넛지 / 하드 게이트 / 인라인 SR을 스위치로 합성.

cc_tools.py의 read/edit/write '한 벌 + 스위치 2개' 설계를 보존하되,
전역 dict 대신 World(세션 소유)에 바인딩되는 FsTools 클래스로 승격했다.
cc_system_reminder.ipynb의 인라인 SR(빈 파일·사이버리스크)과 nested-rule 트리거(_touch)도
같은 도구 구현 안에 스위치로 합류한다.
"""

import difflib
import fnmatch
import re

from .config import GLOB_LIMIT, GREP_HEAD_LIMIT, READ_MAX_LINES
from .reminders import CYBER_RISK_REMINDER, EMPTY_FILE_WARNING, SUSPICIOUS

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


class FsTools:
    """World 1개에 바인딩된 FS 도구 묶음.

    스위치 3개:
      nudges    → 소프트 넛지 (오타 제안·재읽기 스텁·잘림 리다이렉트)
      gates     → 하드 readFileState 게이트 (읽기 강제·낡은읽기·성공 후 자가갱신)
      inline_sr → 빈 파일 경고·사이버리스크 지침을 tool_result 안에 인라인
    셋 다 끄면 게이트도 넛지도 없는 맨몸 도구.
    """

    def __init__(self, world, nudges=True, gates=True, inline_sr=True, track_rules=True):
        self.world = world
        self.nudges = nudges
        self.gates = gates
        self.inline_sr = inline_sr
        self.track_rules = track_rules  # nested-rule 트리거 적립 (리마인더 ⑥용)

    def _touch(self, path):
        if self.track_rules:
            self.world.touch(path)

    # ── read/edit/write 한 벌 ──────────────────────────────────────
    def read_file(self, file_path, offset=None, limit=None):
        w = self.world
        if not file_path.startswith("/"):
            # 입장권 검사: read의 입장권은 '절대경로' — 지어낼 수 없고 앞 단계 출력에서 조달해야 한다
            return "ERROR: file_path는 상대경로가 아닌 절대경로여야 합니다."
        if file_path not in w.fs:
            if self.nudges:
                close = difflib.get_close_matches(file_path, w.fs.keys(), n=1)
                hint = f" 혹시 {close[0]} 파일을 찾으시나요?" if close else ""
                return f"ERROR: 파일이 존재하지 않습니다.{hint}"  # 오타 넛지 (CC suggestPathUnderCwd)
            return "ERROR: 파일이 존재하지 않습니다."

        self._touch(file_path)
        entry = w.fs[file_path]

        if self.inline_sr and entry["content"] == "":
            # 빈 파일 인라인 경고 — 결과 자체가 경고 SR (CC FileReadTool.ts:706)
            if self.gates:
                w.read_file_state[file_path] = {"timestamp": entry["mtime"], "is_partial_view": False}
            return EMPTY_FILE_WARNING

        lines = entry["content"].splitlines()
        start = (offset - 1) if offset else 0
        end = min(start + limit, len(lines)) if limit else len(lines)
        end = min(end, start + READ_MAX_LINES)
        # 부분읽기 판정: 파라미터 사용 여부가 아니라 '실제로 안 본 줄이 있는가' —
        # offset=1·limit=2000처럼 전체를 커버하는 읽기는 '읽음'으로 인정 (게이트 교착 방지)
        is_partial = start > 0 or end < len(lines)

        # 재읽기 절약 스텁 — 같은 범위 + 파일 안 바뀜이면 본문 대신 스텁 한 줄 (소프트 넛지).
        # 스텁도 '읽기'다 — CC처럼 readFileState는 갱신하고 표시만 절약한다 (게이트 교착 방지)
        if self.nudges and w.last_read.get(file_path) == (entry["mtime"], offset, limit):
            if self.gates:
                w.read_file_state[file_path] = {"timestamp": entry["mtime"],
                                                "is_partial_view": is_partial}
            return FILE_UNCHANGED_STUB

        body = numbered_lines(lines, start, end)
        if end < len(lines) and self.nudges:
            # 에러 리다이렉트: 막지 않고 '대신 이렇게'를 결과에 심는다
            body += ("\n... (파일에 더 많은 줄이 있습니다. offset/limit 파라미터로 필요한 부분만 "
                     "읽거나, 파일 통독 대신 특정 내용을 검색하세요.)")
        if self.inline_sr and SUSPICIOUS.search(entry["content"]):
            # 사이버리스크 인라인 지침 — 결과 꼬리에 부착 (CC FileReadTool.ts:730)
            body += "\n" + CYBER_RISK_REMINDER
        if self.gates:
            # readFileState 기록 — 부분읽기는 is_partial_view=True (게이트에서 '읽음' 불인정)
            w.read_file_state[file_path] = {"timestamp": entry["mtime"], "is_partial_view": is_partial}
        if self.nudges:
            w.last_read[file_path] = (entry["mtime"], offset, limit)
        return body

    def _write_gates(self, file_path):
        # edit·write 공용 2중 게이트 — 에러 문구는 CC 원문 번역
        st = self.world.read_file_state.get(file_path)
        if st is None or st["is_partial_view"]:
            # 게이트1: 안 읽음 — CC errorCode 6
            return "ERROR: 파일을 아직 읽지 않았습니다. 쓰기 전에 먼저 읽으세요."
        if self.world.fs[file_path]["mtime"] > st["timestamp"]:
            # 게이트2: 낡은 읽기 — CC errorCode 7
            return ("ERROR: 읽은 이후 파일이 수정되었습니다 - 사용자에 의해서든 린터에 의해서든. "
                    "쓰기 전에 다시 읽으세요.")
        return None

    def exact_replace(self, file_path, old_string, new_string, replace_all=False):
        """edit 공통 코어 — 정확 일치 교체. 성공/에러 문자열을 반환한다 (게이트는 호출측 책임)."""
        w = self.world
        content = w.fs[file_path]["content"]
        n = content.count(old_string)
        if n == 0:
            return f"ERROR: 바꿀 문자열을 파일에서 찾지 못했습니다.\n문자열: {old_string}"
        if n > 1 and not replace_all:
            # 다중매칭 넛지 — 복구 방법 2가지를 정확히 알려준다
            return (f"ERROR: 바꿀 문자열이 {n}곳에서 발견되었지만 replace_all이 false입니다. "
                    "전부 바꾸려면 replace_all을 true로 설정하세요. 한 곳만 바꾸려면 "
                    "컨텍스트를 더 넓혀 대상을 유일하게 지정하세요.")
        w.fs[file_path] = {"content": content.replace(old_string, new_string), "mtime": w.tick()}
        return f"{file_path} 파일이 수정되었습니다. {n}곳을 교체했습니다."

    def edit_file(self, file_path, old_string, new_string, replace_all=False):
        # gates=False(소프트): '읽기 강제' 게이트가 없다 — 그런데도 old_string이 파일 원문과
        #   정확히 일치해야 하므로, read 없이 old_string을 지어낼 수 없다 = old_string 자체가 입장권.
        # gates=True(하드): 읽기 강제 + 낡은읽기 게이트 + 성공 후 자가갱신.
        w = self.world
        if file_path not in w.fs:
            return "ERROR: 파일이 존재하지 않습니다."
        self._touch(file_path)
        if self.gates:
            if old_string == new_string:
                return "ERROR: 바꿀 내용이 없습니다: old_string과 new_string이 완전히 동일합니다."
            gate = self._write_gates(file_path)
            if gate:
                return gate
        result = self.exact_replace(file_path, old_string, new_string, replace_all)
        if self.gates and not result.startswith("ERROR"):
            # 성공 후 자가갱신 — 연속 edit이 게이트2에 걸리지 않게
            w.read_file_state[file_path] = {"timestamp": w.fs[file_path]["mtime"],
                                            "is_partial_view": False}
        return result

    def write_file(self, file_path, content):
        w = self.world
        self._touch(file_path)
        if file_path in w.fs:
            if self.gates:
                gate = self._write_gates(file_path)  # 기존 파일 덮어쓰기 전 같은 2중 검사
                if gate:
                    return gate
            w.fs[file_path] = {"content": content, "mtime": w.tick()}
            msg = f"{file_path} 파일이 수정되었습니다."
        else:
            w.fs[file_path] = {"content": content, "mtime": w.tick()}
            msg = f"파일이 생성되었습니다: {file_path}"
        if self.gates:
            w.read_file_state[file_path] = {"timestamp": w.fs[file_path]["mtime"],
                                            "is_partial_view": False}
        return msg

    # ── 검색 도구 ──────────────────────────────────────────────────
    def glob_files(self, pattern):
        w = self.world
        regex = _glob_to_regex(pattern)
        matches = [p for p in w.fs if regex.match(p)]
        if not matches:
            return "일치하는 파일이 없습니다"
        matches.sort(key=lambda p: w.fs[p]["mtime"], reverse=True)  # 수정시간순 — CC와 동일
        if len(matches) > GLOB_LIMIT:
            return "\n".join(matches[:GLOB_LIMIT]) + "\n" + TRUNCATION_NUDGE  # 잘림 넛지
        return "\n".join(matches)

    def grep_files(self, pattern, path=None, glob=None, output_mode="files_with_matches",
                   head_limit=None):
        w = self.world
        regex = re.compile(pattern)
        scope = [p for p in sorted(w.fs) if p.startswith(path or "/")]
        if glob:
            scope = [p for p in scope if fnmatch.fnmatch(p.rsplit("/", 1)[-1], glob)]
        file_hits, content_lines, counts = [], [], []
        for p in scope:
            lines = w.fs[p]["content"].splitlines()
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
            note = (f"\n(전체 {len(content_lines)}줄 중 앞 {cap}줄만 표시)"
                    if len(content_lines) > cap else "")
            return "\n".join(content_lines[:cap]) + note
        if output_mode == "count":
            return "\n".join(counts)
        return f"{len(file_hits)}개 파일에서 발견\n" + "\n".join(file_hits)

    def agent_search(self, query):
        # 탈출구의 목적지: 목 서브에이전트. 내부에서 여러 라운드 glob/grep/read를 돌고
        # '요약만' 메인 컨텍스트에 반환한다 (CC 연계⑦ 위임→요약 — 가장 강력한 토큰 절약)
        w = self.world
        keywords = re.findall(r"[A-Za-z_]{3,}", query) or ["try", "except", "raise", "error"]
        hits = []
        for p in sorted(w.fs):
            for i, ln in enumerate(w.fs[p]["content"].splitlines(), 1):
                if any(k.lower() in ln.lower() for k in keywords):
                    hits.append(f"{p}:{i}: {ln.strip()}")
        digest = "\n".join(hits[:20]) or "(키워드 일치 없음)"
        return (f"[목 서브에이전트] 파일 {len(w.fs)}개를 내부 3라운드(glob -> grep {keywords[:5]} -> read)로 "
                f"탐색했습니다. 이 요약만 메인 컨텍스트에 들어갑니다:\n{digest}")

    def todo_write(self, todos):
        self.world.todos = todos
        # 성공 넛지 — 결과 문구가 다음 행동(계속 추적하라)을 지시 (CC TodoWrite 원문 번역)
        return ("할 일 목록이 수정되었습니다. 계속 todo 목록으로 진행 상황을 추적하세요. "
                "해당된다면 현재 작업을 계속 진행하세요")

    # ── 목 셸 (파이프라인 8단계 매퍼·조건부 동시성 데모용) ─────────
    def run_command(self, command):
        # 결과를 '문자열'이 아니라 '구조체'로 반환한다 — 8단계 도구별 매퍼가 이걸 접는다.
        # (문자열 도구는 매퍼가 항등함수라, 구조체 도구가 있어야 매핑 인터페이스의 의미가 보인다)
        w = self.world
        cmd = command.strip()
        if cmd.startswith("cat "):
            path = cmd[len("cat "):].strip()
            if path in w.fs:
                return {"stdout": w.fs[path]["content"], "stderr": "", "exit_code": 0}
            return {"stdout": "", "stderr": f"cat: {path}: No such file or directory",
                    "exit_code": 1}
        if cmd.startswith("ls"):
            return {"stdout": "\n".join(sorted(w.fs)), "stderr": "", "exit_code": 0}
        if "pytest" in cmd or "test" in cmd:
            return {"stdout": "collected 3 items\n\ntest_orders.py .F.\n",
                    "stderr": "FAILED test_orders.py::test_calc_total - assert 27500 == 25000  # ORDER-482",
                    "exit_code": 1}
        return {"stdout": f"$ {cmd}\n(실행됨)", "stderr": "", "exit_code": 0}

    READ_ONLY_COMMANDS = {"ls", "cat", "head", "tail", "pwd"}

    def command_is_read_only(self, args):
        # CC Bash 조건부 동시성 판정: "이 명령이 읽기 전용인가"만 본다 — 파일 겹침 분석 아님
        return args.get("command", "").split()[0] in self.READ_ONLY_COMMANDS
