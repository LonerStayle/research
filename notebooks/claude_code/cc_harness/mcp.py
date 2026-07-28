"""MCP 등록·해제 — tools 배열을 안 건드리는 델타 고지 (cc_mcp_connect_disconnect 노트북 이식).

세 장치:
1. MCP 도구는 tools 배열에 절대 안 넣는다 (isMcp → 무조건 defer, MCPTool.ts:28)
2. 등록/해제는 대화 꼬리에 append되는 <system-reminder> 델타 메시지(이름만)로 알린다
3. 로드 상태 DB가 없다 — 대화 이력에 남은 델타 메시지 자체가 상태다
   (매번 이력을 스캔해 고지 집합을 재구성, 차집합만 새로 흘린다 — toolSearch.ts:646-706)

append-only라서 프리픽스가 바이트 단위로 불변 → 캐시가 안 깨진다.
"""

import re

from .registry import ALL_MCP_TOOLS, MCP_SERVERS

# 델타 헤더 — CC 영문 원문 그대로 보존 (messages.ts:4178-4193). 번역 금지.
ADDED_HEADER = "The following deferred tools are now available via ToolSearch"
REMOVED_HEADER = "The following deferred tools are no longer available (their MCP server disconnected)"
NAME_RE = re.compile(r"^mcp__[A-Za-z0-9_]+$")
# ↑ 한계: 델타 고지 대상이 mcp__ 이름으로 한정된다. 일반 deferred 도구까지 고지하려면
#   정규식을 레지스트리에서 받은 이름 집합 매칭으로 바꿔야 한다 (현재는 CC 재현 범위 유지).


def render_delta(added, removed):
    # 클로드코드 messages.ts:4178-4193 렌더링 문구 보존
    parts = []
    if added:
        parts.append(ADDED_HEADER + ". Their schemas are NOT loaded — "
                     "call tool_search with query \"select:<name>\" before use:\n" + "\n".join(added))
    if removed:
        parts.append(REMOVED_HEADER + ". Do not search for them — tool_search will return no match:\n"
                     + "\n".join(removed))
    return "<system-reminder>\n" + "\n\n".join(parts) + "\n</system-reminder>"


def announced_names(input_list):
    """이력의 델타 메시지들을 순서대로 재생해 '이미 고지한 이름 집합'을 재구성 (toolSearch.ts:655-663)."""
    announced = set()
    for item in input_list:
        if not (isinstance(item, dict) and item.get("role") == "user"):
            continue  # 모델 출력(reasoning, function_call 등)은 dict가 아니라서 자동으로 걸러진다
        text = item.get("content", "")
        if not isinstance(text, str) or "<system-reminder>" not in text:
            continue
        mode = None
        for line in text.splitlines():
            line = line.strip()
            if line.startswith(ADDED_HEADER):
                mode = "add"
            elif line.startswith(REMOVED_HEADER):
                mode = "remove"
            elif NAME_RE.match(line):
                if mode == "add":
                    announced.add(line)
                elif mode == "remove":
                    announced.discard(line)
    return announced


class MCPRegistry:
    """연결 상태는 클라이언트에만 있다 — connect/disconnect는 이 dict만 바꾼다.
    모델에게 알리는 일은 다음 수집 지점의 델타 고지(delta_message)가 맡는다."""

    def __init__(self, servers=None):
        self.servers = servers or MCP_SERVERS
        self.connected = {}
        self.all_pool = {t["name"]: t for tools in self.servers.values() for t in tools}

    def connect(self, server):
        self.connected[server] = True
        print(f"🔌 MCP 서버 '{server}' 연결 — 도구 {len(self.servers[server])}개")

    def disconnect(self, server):
        self.connected.pop(server, None)
        print(f"🔌 MCP 서버 '{server}' 연결 해제")

    def visible(self):
        """현재 연결된 서버들의 도구만 모은 뷰. tool_search / tool_invoke는 항상 이것만 본다."""
        return {t["name"]: t for s in self.connected for t in self.servers[s]}

    def delta_message(self, input_list):
        """수집 지점에서 호출 — 차집합 델타 SR 메시지를 반환 (없으면 None). append는 호출측이."""
        current = set(self.visible())
        announced = announced_names(input_list)
        added = sorted(current - announced)
        removed = sorted(announced - current)
        if not added and not removed:
            return None
        if added:
            print(f"    📎 델타 고지(등록): {', '.join(added)}")
        if removed:
            print(f"    📎 델타 고지(해제): {', '.join(removed)}")
        return {"role": "user", "content": render_delta(added, removed)}
