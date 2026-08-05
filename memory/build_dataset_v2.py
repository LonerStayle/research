"""라운드 2: 실전 스케일(~800K자) 대화 1건 선별 + 청크 분할.

라운드 1 대비 변경:
- 절단 없음 (캡 800k자), 도구결과 절단 완화 300→2000자 (실제 컴팩션 입력에 근접)
- 가장 큰 한국어 세션 1건 선별, ~70k자 청크로 턴 경계 분할 → conv2-01.partN.txt
- 결과: memory/data2/
"""
import json, os, glob, importlib.util

spec = importlib.util.spec_from_file_location("v1", os.path.join(os.path.dirname(__file__), "build_dataset.py"))
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)
v1.TOOL_RESULT_CAP = 2000   # 라운드 2: 도구 결과를 더 많이 보존
v1.TOOL_CALL_CAP = 500

OUT_DIR = "/Users/seobi/jinsup_space/research/memory/data2"
CHUNK = 70_000
MIN_CHARS = 300_000
CAP = 800_000
TARGET = 1


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    candidates = []
    for path in glob.glob(os.path.join(v1.PROJ_ROOT, "*", "*.jsonl")):
        if "/subagents/" in path or "/memory/" in path:
            continue
        if os.path.splitext(os.path.basename(path))[0] == v1.EXCLUDE_SESSION:
            continue
        if os.path.getsize(path) < 2_000_000:
            continue
        turns = v1.parse_session(path)
        if not turns:
            continue
        text, dchars, h, l = v1.render(turns)
        if (h + l) == 0 or len(text) < MIN_CHARS:
            continue
        ratio = h / (h + l)
        if ratio < v1.MIN_HANGUL_RATIO:
            continue
        candidates.append(dict(path=path, project=os.path.basename(os.path.dirname(path)),
                               text=text, hangul_ratio=round(ratio, 3)))

    candidates.sort(key=lambda c: -len(c["text"]))
    print("후보 (정규화 크기순):")
    for c in candidates[:10]:
        print(f"  {len(c['text']):>9,}자  한글 {c['hangul_ratio']:.2f}  {c['project']}  {os.path.basename(c['path'])}")
    if not candidates:
        print("후보 없음 — 기준 완화 필요")
        return

    meta = []
    for i, c in enumerate(candidates[:TARGET], 1):
        cid = f"conv2-{i:02d}"
        text = c["text"][:0] + c["text"]
        if len(text) > CAP:
            cut = text.rfind("\n\n[", 0, CAP)
            text = text[: cut if cut > 0 else CAP]
        parts, pos = [], 0
        while pos < len(text):
            end = len(text) if len(text) - pos <= CHUNK else text.rfind("\n\n[", pos, pos + CHUNK)
            if end <= pos:
                end = pos + CHUNK
            parts.append(text[pos:end])
            pos = end
        part_files = []
        for j, p in enumerate(parts, 1):
            f = os.path.join(OUT_DIR, f"{cid}.part{j}.txt")
            open(f, "w", encoding="utf-8").write(p)
            part_files.append(dict(file=f, chars=len(p)))
        meta.append(dict(id=cid, source=c["path"], project=c["project"], hangul_ratio=c["hangul_ratio"],
                         total_chars=len(text), n_chunks=len(parts), parts=part_files))
        print(f"\n선정: {cid}  {len(text):>9,}자  {len(parts)}청크  {c['project']}")

    json.dump(meta, open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
