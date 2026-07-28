"""세션 소유 가변 상태 — World 하나에 봉인.

기존 cc_* 모듈·노트북의 전역 가변 상태(FS/LAST_READ/READ_FILE_STATE/TODOS,
MOCK_TODAY/RULES/MEMORIES/MESSAGE_QUEUE)를 전부 인스턴스로 승격했다.
→ 세션 여러 개를 동시에 띄워도 상태가 섞이지 않고, 노트북 재실행에도 안전하다.
"""

from .mock_fs import SOURCE_FS, EXTRA_FILES

# 디렉토리 규칙 — CC nested CLAUDE.md/rules 대응 (트리거 축적형 수집기용)
DEFAULT_RULES = {
    "/project/src": "- src의 파이썬 함수를 수정할 때 타입힌트를 유지한다.\n- 함수명은 snake_case로 짓는다.",
}

# 메모리 저장소 — 사이드쿼리형 수집기용 (CC는 소넷 별도 호출, 여기선 키워드 목)
DEFAULT_MEMORIES = [
    {"name": "deploy-checklist", "keywords": ["배포"], "age_days": 3,
     "content": "배포 전에는 반드시 /project/src/app/config.py의 DEBUG를 False로 바꾼다."},
    {"name": "style-guide", "keywords": ["스타일", "컨벤션"], "age_days": 40,
     "content": "이 프로젝트의 문자열은 작은따옴표를 쓴다."},
]


class World:
    """목 파일시스템(mtime 포함) + 목 환경(날짜·규칙·메모리·메시지 큐) — 세션 1개가 소유."""

    def __init__(self, today="2026-07-23", seed_extras=True):
        self.clock = 0
        self.fs = {}                     # path -> {"content": str, "mtime": int}
        self.read_file_state = {}        # 하드 게이트: path -> {"timestamp", "is_partial_view"}
        self.last_read = {}              # 소프트 재읽기 스텁 추적: path -> (mtime, offset, limit)
        self.todos = []
        # ── 리마인더용 목 환경 ──
        self.today = today
        self.rules = dict(DEFAULT_RULES)
        self.nested_triggers = set()     # 도구가 만진 새 규칙 디렉토리 적립
        self.injected_rule_dirs = set()  # 이미 주입한 디렉토리
        self.memories = [dict(m) for m in DEFAULT_MEMORIES]
        self.message_queue = []          # 미드턴 유저 메시지 큐
        self.reset_fs(seed_extras)

    # ── 목 파일시스템 ──
    def tick(self):
        self.clock += 1
        return self.clock

    def seed(self, path, content):
        # 빈 파일은 빈 그대로 (빈 파일 인라인 경고 데모용)
        self.fs[path] = {"content": content.strip("\n") + "\n" if content else "",
                         "mtime": self.tick()}

    def reset_fs(self, seed_extras=True):
        """공통 목 코드베이스(orderhub, 40파일)로 FS를 초기화한다. 시드된 파일 수를 반환."""
        self.fs.clear()
        for path, content in SOURCE_FS.items():
            self.seed(path, content)
        if seed_extras:
            for path, content in EXTRA_FILES.items():
                self.seed(path, content)
        return len(self.fs)

    def external_modify(self, path, content):
        """모델 모르게 파일이 바뀌는 상황(사용자 편집·린터) 시뮬레이션 — 하드 게이트2 실습용."""
        self.fs[path] = {"content": content.strip("\n") + "\n", "mtime": self.tick()}
        print(f"⚡ (외부 수정 발생) {path} — mtime {self.fs[path]['mtime']}")

    # ── 외부 사건 시뮬레이션 (리마인더 트리거) ──
    def advance_date(self, new_date):
        self.today = new_date
        print(f"⚡ (외부 사건) 날짜가 {new_date}로 바뀜")

    def queue_user_message(self, text):
        self.message_queue.append(text)
        print(f"⚡ (외부 사건) 작업 중 사용자 메시지 도착: {text!r}")

    def touch(self, path):
        # 도구 실행부가 경로를 만질 때 호출 — CC nestedMemoryAttachmentTriggers 대응
        for rule_dir in self.rules:
            if path.startswith(rule_dir) and rule_dir not in self.injected_rule_dirs:
                self.nested_triggers.add(rule_dir)
