"""스마트 배치 스케줄링 — CC partitionToolCalls + runTools 이식.

핵심은 "분리"가 아니라 "단독(solo)". 규칙 4가지 (전부 소스 검증분):
1. 도구 단위 isConcurrencySafe 선언 — 파일 겹침 분석은 존재하지 않음 (Tool.ts:757-760 기본 false)
2. 연속 safe만 병합, unsafe는 서로 이웃해도 각자 단독 (toolOrchestration.ts:109, :112)
3. 배치 간 직렬, 배치 내 병렬 — 동시성 한도 기본 10 (toolOrchestration.ts:26-81)
4. 모델 emit 순서 그대로 — 재배열 없음, 짝짓기는 call_id (query.ts:820-824)

partitionToolCalls 주석 원문 (toolOrchestration.ts:86-90):
    Partition tool calls into batches where each batch is either:
    1. A single non-read-only tool, or          ← unsafe = "단독 1개"
    2. Multiple consecutive read-only tools     ← safe = "연속"일 때만 병합
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import SimpleNamespace

from .config import MAX_TOOL_USE_CONCURRENCY


def partition_tool_calls(function_calls, safety_of):
    """CC partitionToolCalls (toolOrchestration.ts:95-115) 재현.

    safety_of(name) -> (args -> bool) | None. 판정 실패는 전부 보수적 false:
    인자 파싱(Zod safeParse) 실패 → false, 판정 함수가 throw → false."""
    batches = []
    for call in function_calls:
        judge = safety_of(call.name)
        try:
            parsed = json.loads(call.arguments)  # Zod safeParse 대응
            safe = bool(judge(parsed)) if judge else False
        except Exception:
            safe = False  # 검증 실패 / 판정 중 throw → 보수적 false
        if safe and batches and batches[-1]["isConcurrencySafe"]:
            batches[-1]["blocks"].append(call)  # safe + 직전 배치도 safe → 합류 (:109)
        else:
            batches.append({"isConcurrencySafe": safe, "blocks": [call]})  # 아니면 무조건 새 배치 (:112)
    return batches


def brief(call):
    args = json.loads(call.arguments) if call.arguments else {}
    first = next(iter(args.values()), "")
    return f"{call.name}({str(first)[:24]})"


def print_partition(batches):
    parts = []
    for b in batches:
        tag = "🟢병렬" if b["isConcurrencySafe"] else "🔴단독"
        parts.append(tag + "[" + ", ".join(brief(c) for c in b["blocks"]) + "]")
    print("📦 파티션:", " → ".join(parts))


# ── 오프라인 파티션 테스트용 가짜 function_call 팩토리 ──────────────
_seq = 0


def fake(name, **args):
    global _seq
    _seq += 1
    return SimpleNamespace(name=name, arguments=json.dumps(args), call_id=f"tu_{_seq}")


def execute_batches(function_calls, run_fn, safety_of, concurrency=MAX_TOOL_USE_CONCURRENCY,
                    trace=True, latency_fn=None):
    """CC runTools 구조 재현 — 배치 간 직렬 · 배치 내 병렬 · 방출은 emit 순서 고정.

    run_fn(call) -> {"label", "output", ...} — 호출 1건 실행 (파이프라인 등).
    latency_fn(name, args) -> 초 — 모의 지연 (완료 순서 뒤섞기 시연용, 기본 없음).
    반환: emit 순서 그대로의 결과 리스트 (짝짓기는 call_id)."""
    batches = partition_tool_calls(function_calls, safety_of)
    if trace:
        print_partition(batches)
    t0 = time.perf_counter()
    results_by_id = {}

    def run_one(call):
        started = time.perf_counter() - t0
        if latency_fn:
            try:
                time.sleep(latency_fn(call.name, json.loads(call.arguments)))
            except Exception:
                pass
        r = dict(run_fn(call))
        r["call"] = call
        r["started"] = started
        r["ended"] = time.perf_counter() - t0
        return r

    for i, batch in enumerate(batches, 1):
        blocks = batch["blocks"]
        if batch["isConcurrencySafe"]:
            if trace:
                print(f"  🟢 배치 {i} — CONCURRENT ({len(blocks)}건 동시 착수)")
            finish_order = []
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                futures = [pool.submit(run_one, c) for c in blocks]
                for fut in as_completed(futures):
                    r = fut.result()
                    results_by_id[r["call"].call_id] = r
                    finish_order.append(brief(r["call"]))
            if trace and len(blocks) > 1:
                print("     ⏱ 완료 순서(뒤죽박죽 가능):", " → ".join(finish_order))
        else:
            if trace:
                print(f"  🔴 배치 {i} — SERIAL (단독, 앞 배치 완료까지 대기)")
            for c in blocks:
                r = run_one(c)
                results_by_id[r["call"].call_id] = r

    if trace and latency_fn:
        print("  ⏱ 타임라인 (턴 시작 기준):")
        for c in function_calls:
            r = results_by_id[c.call_id]
            print(f"     {brief(c):<36} {r['started']:.2f}s → {r['ended']:.2f}s")

    # 방출: 완료 순서와 무관하게 모델이 부른 순서(emit 순서) 그대로 — call_id 로 짝지음
    return [results_by_id[c.call_id] for c in function_calls]
