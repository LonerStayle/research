"""목 코드베이스 소스 + 데모 픽스처.

orderhub 40파일 원본은 이웃 모듈 `cc_mock_fs.py`(단일 진실)를 그대로 가져온다.
여기에 노트북 셀에 흩어져 있던 데모 전용 픽스처(합성 파일 생성)를 함수로 승격해 모은다.
"""

import os
import sys

_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from cc_mock_fs import FS as SOURCE_FS  # path -> content(str), 40파일 — 순수 데이터

# system-reminder 데모 전용 소품 2개 (비-어태치먼트 SR: 빈 파일 경고 / 사이버리스크 지침)
EXTRA_FILES = {
    "/project/empty.txt": "",
    "/project/tools/obfuscated.py": (
        'import base64\n'
        'payload = "aW1wb3J0IG9zOyBvcy5zeXN0ZW0oJ2VjaG8gcHduZWQnKQ=="\n'
        'exec(base64.b64decode(payload))'
    ),
}


# ── 데모 픽스처 — 노트북 셀에 있던 합성 파일 생성 로직 승격 ─────────
def make_test_files(world, n=120):
    """glob 잘림 넛지 데모용 — tests/ 아래 합성 테스트 파일 n개."""
    for i in range(n):
        world.seed(f"/project/tests/test_{i:03}.py", f"def test_{i}():\n    assert True\n")
    return n


def cleanup_test_files(world):
    """make_test_files가 만든 합성 파일만 제거 (공통 tests/의 실제 테스트는 유지)."""
    import re
    for p in [p for p in list(world.fs) if re.search(r"/tests/test_\d{3}\.py$", p)]:
        del world.fs[p]


def make_big_log(world, lines=2500):
    """read 2000줄 리다이렉트 데모용 대용량 로그."""
    world.seed("/project/logs/big.log", "\n".join(f"line {i}" for i in range(1, lines + 1)))
    return "/project/logs/big.log"


def make_request_log(world, lines=700):
    """8단계 도구별 한도 데모용 — Bash 30,000자 한도를 넘는 요청 로그 (read는 Infinity라 안 잘림)."""
    world.seed("/project/logs/requests-2026-07-23.log", "\n".join(
        f'127.0.0.1 - "GET /orders/{1000 + i} HTTP/1.1" 200 {i * 7 % 90 + 5}.{i % 10}ms'
        for i in range(lines)))
    return "/project/logs/requests-2026-07-23.log"


def make_dup_file(world):
    """다중매칭 넛지 데모용 — 같은 줄이 2번 있는 파일."""
    world.seed("/project/tmp_dup.py", "print(x)\nprint(x)\n")
    return "/project/tmp_dup.py"


def simulate_linter(world, path):
    """하드 게이트2 데모용 — 린터가 파일을 포맷팅하는 외부 수정 시뮬레이션."""
    content = world.fs[path]["content"]
    world.external_modify(path, "# formatted by linter\n" + content)
