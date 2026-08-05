"""~/.claude/projects 세션 jsonl에서 한국어 위주 대화를 선별·정규화해 memory/data/에 저장.

선별 기준:
- 한글 비율(한글 / (한글+라틴), 대화 텍스트만) >= 0.25
- 대화 텍스트(도구 제외) >= 8,000자
- 프로젝트당 최대 2건, 총 6건
정규화: [USER]/[ASSISTANT] 턴 + 도구 호출/결과는 짧게 절단해 마커로 유지. 100k자 초과 시 턴 경계에서 절단.
"""
import json, os, glob, re

PROJ_ROOT = os.path.expanduser("~/.claude/projects")
OUT_DIR = "/Users/seobi/jinsup_space/research/memory/data"
EXCLUDE_SESSION = "ad6995a7-6490-44ca-8eea-e60192036018"  # 현재 세션

HANGUL = re.compile(r"[가-힣]")
LATIN = re.compile(r"[a-zA-Z]")
SYS_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)

TOOL_CALL_CAP = 200
TOOL_RESULT_CAP = 300
MAX_CHARS = 100_000
MIN_DIALOGUE_CHARS = 8_000
MIN_HANGUL_RATIO = 0.25
PER_PROJECT_CAP = 2
TARGET_COUNT = 6


def clean_text(t: str) -> str:
    t = SYS_REMINDER.sub("", t)
    return t.strip()


def block_texts(content):
    """content(str | list) -> (dialogue_texts, tool_markers) 순서 유지된 (kind, text) 리스트"""
    out = []
    if isinstance(content, str):
        if content.strip():
            out.append(("text", content))
        return out
    if not isinstance(content, list):
        return out
    for b in content:
        if not isinstance(b, dict):
            continue
        bt = b.get("type")
        if bt == "text":
            out.append(("text", b.get("text", "")))
        elif bt == "tool_use":
            try:
                arg = json.dumps(b.get("input", {}), ensure_ascii=False)
            except Exception:
                arg = str(b.get("input"))
            out.append(("tool_use", f"[도구호출 {b.get('name','?')}] {arg[:TOOL_CALL_CAP]}"))
        elif bt == "tool_result":
            inner = b.get("content")
            texts = []
            if isinstance(inner, str):
                texts.append(inner)
            elif isinstance(inner, list):
                for ib in inner:
                    if isinstance(ib, dict) and ib.get("type") == "text":
                        texts.append(ib.get("text", ""))
            joined = " ".join(texts).strip()
            if joined:
                out.append(("tool_result", f"[도구결과] {joined[:TOOL_RESULT_CAP]}"))
    return out


def parse_session(path):
    turns = []  # (role, kind, text)
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("isMeta"):
                    continue
                t = obj.get("type")
                if t not in ("user", "assistant"):
                    continue
                msg = obj.get("message") or {}
                for kind, text in block_texts(msg.get("content")):
                    if kind == "text":
                        text = clean_text(text)
                        if not text or text.startswith("Caveat: The messages below"):
                            continue
                        if text.startswith("<command-name>"):
                            m = re.search(r"<command-name>(.*?)</command-name>", text)
                            text = f"[슬래시커맨드 {m.group(1) if m else '?'}]"
                    if text:
                        turns.append((t, kind, text))
    except Exception:
        return None
    return turns


def render(turns):
    """정규화 텍스트, 대화(도구 제외) 문자수, 한글/라틴 수 반환"""
    parts, dialogue_chars, h, l = [], 0, 0, 0
    prev_role = None
    for role, kind, text in turns:
        if kind == "text":
            tag = "[USER]" if role == "user" else "[ASSISTANT]"
            parts.append(f"{tag} {text}")
            dialogue_chars += len(text)
            h += len(HANGUL.findall(text))
            l += len(LATIN.findall(text))
        else:
            parts.append(text)
        prev_role = role
    return "\n\n".join(parts), dialogue_chars, h, l


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    candidates = []
    for path in glob.glob(os.path.join(PROJ_ROOT, "*", "*.jsonl")):
        if "/subagents/" in path or "/memory/" in path:
            continue
        sid = os.path.splitext(os.path.basename(path))[0]
        if sid == EXCLUDE_SESSION:
            continue
        if os.path.getsize(path) < 200_000:  # 너무 짧은 세션 스킵
            continue
        turns = parse_session(path)
        if not turns:
            continue
        text, dchars, h, l = render(turns)
        if dchars < MIN_DIALOGUE_CHARS or (h + l) == 0:
            continue
        ratio = h / (h + l)
        if ratio < MIN_HANGUL_RATIO:
            continue
        project = os.path.basename(os.path.dirname(path))
        score = ratio * min(dchars, 60_000)
        candidates.append(dict(path=path, session=sid, project=project, text=text,
                               dialogue_chars=dchars, hangul_ratio=round(ratio, 3), score=score))

    candidates.sort(key=lambda c: -c["score"])
    picked, per_proj = [], {}
    for c in candidates:
        if per_proj.get(c["project"], 0) >= PER_PROJECT_CAP:
            continue
        picked.append(c)
        per_proj[c["project"]] = per_proj.get(c["project"], 0) + 1
        if len(picked) >= TARGET_COUNT:
            break

    meta = []
    for i, c in enumerate(picked, 1):
        cid = f"conv-{i:02d}"
        text = c["text"]
        truncated = False
        if len(text) > MAX_CHARS:
            cut = text.rfind("\n\n[", 0, MAX_CHARS)
            text = text[: cut if cut > 0 else MAX_CHARS] + "\n\n[... 이후 절단됨 ...]"
            truncated = True
        out = os.path.join(OUT_DIR, f"{cid}.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        meta.append(dict(id=cid, file=out, source=c["path"], project=c["project"],
                         total_chars=len(text), dialogue_chars=c["dialogue_chars"],
                         hangul_ratio=c["hangul_ratio"], truncated=truncated))
        print(f"{cid}  {c['hangul_ratio']:.2f}  {len(text):>7,}자  {c['project']}")

    with open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"\n후보 {len(candidates)}건 중 {len(picked)}건 선별 → {OUT_DIR}")


if __name__ == "__main__":
    main()
