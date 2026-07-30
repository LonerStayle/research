"""Gemini 3.6 flash — LiteLLM 경유로 캐시가 붙을 때까지 길게 돌린다.

실험 2종:
  A) 긴 멀티턴 (턴마다 컨텍스트 누적) — 몇 턴째부터 cached_tokens 가 붙나?
  B) 같은 프리픽스 장기 반복 — 붙은 뒤 계속 유지되나, 아니면 들쭉날쭉한가?
"""
import os, re, sys, time
from dotenv import load_dotenv

load_dotenv("/Users/user/jinsup_space/research/.env")
os.environ.setdefault("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
import litellm

litellm.suppress_debug_info = True

MODEL = "gemini/gemini-3.6-flash"
N_TURNS = 20        # A: 멀티턴 길이
N_REPEAT = 15       # B: 동일 프리픽스 반복 횟수


def call(messages, max_tokens=48, tries=5):
    """429 면 서버가 준 retryDelay 만큼 대기 후 재시도. 일일 한도면 즉시 중단."""
    for attempt in range(1, tries + 1):
        try:
            return litellm.completion(model=MODEL, messages=messages, max_tokens=max_tokens)
        except Exception as e:
            s = str(e)
            if "429" not in s and "RESOURCE_EXHAUSTED" not in s:
                raise
            if "PerDay" in s:
                print("  ❌ 일일 한도 소진 — 재시도해도 안 풀립니다. 중단.")
                raise SystemExit(1)
            if attempt == tries:
                raise
            m = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+(?:\.\d+)?)s", s)
            d = float(m.group(1)) + 2 if m else 20.0
            print(f"    (429 분당한도 — {d:.0f}s 대기)")
            time.sleep(d)


def cache_of(resp):
    u = resp.usage.model_dump() if hasattr(resp.usage, "model_dump") else dict(resp.usage)
    det = u.get("prompt_tokens_details") or {}
    return u.get("prompt_tokens") or 0, det.get("cached_tokens"), u.get("cache_read_input_tokens")


# ---------------------------------------------------------------- A: 긴 멀티턴
_RULE = (
    "Operational rule: every deployment must be preceded by a configuration snapshot so that "
    "before/after comparison is possible. Staging must reproduce the change and pass regression "
    "tests first. Production changes follow the four-eyes principle and are applied only inside a "
    "scheduled maintenance window. P1 incidents require initial response within 15 minutes. "
)
SYSTEM = ("You are an SRE assistant for the 'orderhub' service. Answer from the runbook below "
          "in one short sentence.\n\n" + _RULE * 60)   # ~4K 토큰

_LOG = ("[12:{t:02d}:{i:02d}] svc=order-api level=warn msg=\"retry scheduled\" attempt={n} "
        "latency_ms={lat} consumer=inbox-worker partition={p} idempotency_key=ord-{n:06d} ")


def user_text(turn):
    log = "".join(_LOG.format(t=turn, i=i, n=turn * 100 + i, lat=120 + i * 7, p=i % 4)
                  for i in range(16))
    return f"[log turn {turn}]\n{log}\n\nQ{turn}: 한 문장으로 답해줘. 재시도 원인이 뭘까?"


print(f"=== A) 긴 멀티턴 {N_TURNS}턴 — 몇 턴째부터 캐시가 붙나 ===")
print(f"{'턴':>3} | {'prompt':>8} | {'cached':>8} | {'적중률':>7} | {'top필드':>8}")
print("-" * 52)
messages = [{"role": "system", "content": SYSTEM}]
first_hit_turn = None
mt_rows = []
for turn in range(1, N_TURNS + 1):
    messages.append({"role": "user", "content": user_text(turn)})
    try:
        resp = call(messages)
    except Exception as e:
        print(f"  턴{turn} 실패: {type(e).__name__}: {str(e)[:120]}")
        break
    p, cached, top = cache_of(resp)
    rate = (cached or 0) / p if p else 0
    if first_hit_turn is None and cached:
        first_hit_turn = turn
    mt_rows.append((turn, p, cached, rate))
    print(f"{turn:>3} | {p:>8,} | {str(cached):>8} | {rate:>6.1%} | {str(top):>8}")
    messages.append({"role": "assistant", "content": resp.choices[0].message.content or "(빈 응답)"})

if first_hit_turn:
    print(f"\n→ 멀티턴 첫 적중: {first_hit_turn}턴째")
    hits = sum(1 for _, _, c, _ in mt_rows if c)
    print(f"→ 전체 {len(mt_rows)}턴 중 {hits}턴 적중")
else:
    print(f"\n→ {len(mt_rows)}턴 내내 한 번도 적중 안 함")

# ------------------------------------------------- B: 동일 프리픽스 장기 반복
print(f"\n=== B) 동일 프리픽스 {N_REPEAT}회 반복 — 붙은 뒤 유지되나 ===")
UNIT = ("The distributed order-processing service uses idempotency keys and an inbox table to guarantee "
        "that redelivered messages do not duplicate side effects. Under at-least-once delivery the consumer "
        "must be idempotent: derive the key from the message id and insert it in the same transaction. ")
PREFIX = UNIT * 260   # ~14K
fixed = [{"role": "user", "content": PREFIX + "\n\nSay OK."}]
seq = []
for i in range(1, N_REPEAT + 1):
    try:
        resp = call(fixed, max_tokens=8)
    except Exception as e:
        print(f"  {i}회차 실패: {str(e)[:120]}")
        break
    p, cached, top = cache_of(resp)
    rate = (cached or 0) / p if p else 0
    seq.append(round(rate * 100))
    print(f"  {i:>2}회차: prompt={p:,} cached={str(cached):>6} 적중 {rate:>5.1%}")

if seq:
    hits = sum(1 for x in seq if x > 0)
    print(f"\n→ 적중 패턴: {seq}")
    print(f"→ {hits}/{len(seq)}회 적중")
