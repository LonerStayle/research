"""KV 캐시 계측 — usage 기록·표 출력·프리픽스 안정성 검증 (전 메커니즘 공용 자산).

OpenAI 프롬프트 캐싱 규칙: 요청 앞부분이 이전 요청과 완전히 같아야 재사용.
1024토큰 이상부터, 128토큰 단위. 적중은 best-effort — 미스의 '개수'가 아니라
'위치와 성격'(장착 직후 결정적 미스 vs 무작위 서버 노이즈)을 본다.
"""

import json


def norm_item(item):
    """input_list 항목(dict 또는 SDK 객체)을 결정론적 JSON 문자열로 — 프리픽스 비교용."""
    obj = item if isinstance(item, dict) else item.model_dump()
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)


class UsageLog:
    def __init__(self):
        self.rows = []
        self.snapshots = []       # 각 요청이 실제 보낸 input_list 직렬화 (프리픽스 검증용)
        self.offload_by_req = {}  # 요청 번호 -> 그 직전 전처리 오프로드 건수

    def snapshot(self, input_list, offloaded=0):
        self.snapshots.append([norm_item(it) for it in input_list])
        if offloaded:
            self.offload_by_req[len(self.snapshots)] = offloaded

    def record(self, response, elapsed=0.0, turn=0):
        usage = response.usage
        cached = getattr(getattr(usage, "input_tokens_details", None), "cached_tokens", 0) or 0
        cycle = sum(1 for r in self.rows if r["turn"] == turn) + 1  # 턴 내 몇 번째 사이클인지
        row = {"req": len(self.rows) + 1, "turn": turn, "cycle": cycle,
               "input": usage.input_tokens, "cached": cached,
               "output": usage.output_tokens, "search": "-", "sec": round(elapsed, 1)}
        self.rows.append(row)
        mark = "✅ HIT" if cached > 0 else "❌ MISS"
        print(f"    [요청 {row['req']:>2} · 사이클 {cycle}] input={row['input']:>6}  "
              f"cached={cached:>6}  {mark}  ({row['sec']}초)")
        return row

    def note_events(self, events):
        # 이번 요청에서 검색·실행된 도구를 해당 행의 search_result로 기록
        if self.rows and events:
            self.rows[-1]["search"] = " · ".join(events)

    def print_log(self, title):
        print(f"═══ {title} ═══")
        print(f"{'요청':>3} {'턴':>3} {'사이클':>3} {'input':>7} {'cached':>7} {'적중률':>5} {'초':>6}  search_result")
        for r in self.rows:
            rate = f"{r['cached'] / r['input'] * 100:.0f}%" if r["input"] else "-"
            sr = r.get("search", "-")
            if len(sr) > 52:
                sr = sr[:52] + "…"
            print(f"{r['req']:>4} {r['turn']:>3} {r['cycle']:>5} {r['input']:>7} "
                  f"{r['cached']:>7} {rate:>6} {r['sec']:>6}  {sr}")
        total_input = sum(r["input"] for r in self.rows)
        total_cached = sum(r["cached"] for r in self.rows)
        misses = sum(1 for r in self.rows if r["cached"] == 0)
        if total_input:
            print(f"합계: 요청 {len(self.rows)}회 | 입력 {total_input:,} 토큰 | "
                  f"캐시에서 재사용 {total_cached:,} 토큰 ({total_cached / total_input * 100:.0f}%) | "
                  f"미스 {misses}회")

    def print_prefix_check(self):
        """프리픽스 안정성 (결정론적) — req N 전체가 req N+1의 접두어로 불변인지."""
        snaps = self.snapshots
        print("프리픽스 안정성 검증 (req N 전체가 req N+1의 접두어로 불변인가):")
        all_ok = True
        for i in range(len(snaps) - 1):
            prev, cur = snaps[i], snaps[i + 1]
            ok = cur[:len(prev)] == prev  # 직전 요청 전체가 현재 요청 접두어와 정확 일치
            all_ok &= ok
            tag = ""
            off = self.offload_by_req.get(i + 2)
            if off:
                tag = (f"   ← 이 사이클 맨 위에서 {off}건 in-place 오프로드 "
                       "(그런데도 불변인 게 핵심)")
            print(f"  요청 {i + 1}→{i + 2}: 직전 {len(prev):>2}개 항목 "
                  f"{'불변 ✓' if ok else '깨짐 ✗'}{tag}")
        print("\n결론:",
              "클라이언트 전송 항목 기준 안정 프리픽스 불변 — 우리가 깰 수 있는 캐시는 안 깨짐 ✓\n"
              "(주의: 이 검증은 클라이언트가 보낸 항목까지다. 턴 경계에서 input 토큰이 직전보다 '줄어드는'\n"
              " 행이 있다면 서버가 이전 턴 reasoning 항목을 드랍한 것 — 그 지점 MISS에는 구조적 성분이\n"
              " 섞일 수 있어 무작위 노이즈로 단정할 수 없다. 턴 내부 MISS만 노이즈로 귀속 가능.)"
              if all_ok else "프리픽스가 깨진 지점 존재 ✗")
        return all_ok
