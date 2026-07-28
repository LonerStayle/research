"""컨텍스트 전처리 ① applyToolResultBudget — 직전 사이클 도구결과 묶음 오프로드.

CC 흐름 3계층: 대화 턴 ⊃ ReAct 사이클 ⊃ 10단계 파이프라인.
전처리는 사이클마다 맨 위(모델 호출 직전) 딱 1번, '직전 사이클이 뱉은 도구결과 묶음'을 정리한다.

전처리 5단계 중 ①만 이식 (②snipCompact ③microcompact ④contextCollapse ⑤autocompact 자리는 비움):
  mode="budget"      — CC 충실: 묶음 총합 > 200,000자일 때만 큰 결과부터 오프로드
  mode="edit_forced" — 데모 변형: edit_file 결과를 무조건 오프로드 (200KB를 못 넘기는 데모용)

캐시 안전의 핵심: 대상은 오직 '직전 사이클 묶음'(아직 모델에 한 번도 안 보낸 fresh 출력)뿐 —
안정 프리픽스(시스템 프롬프트 + tools + 그 이전 사이클들)는 절대 건드리지 않는다.

smoosh 상호작용 규칙(통합에서만 드러나는 문제): 인루프 리마인더가 tool_result 꼬리에 합체한
<system-reminder>는 오프로드 시 분리 보존 후 교체 메시지 뒤에 재부착한다 — 안 그러면 사라진다.
"""

from .config import BUDGET_CHARS, PREVIEW_BYTES

SR_TAIL_MARK = "\n\n<system-reminder>"


def _split_sr_tail(output):
    """smoosh로 합체된 <system-reminder> 꼬리를 분리 (본문, 꼬리) — 꼬리 없으면 ("", ...)."""
    idx = output.find(SR_TAIL_MARK)
    if idx == -1:
        return output, ""
    return output[:idx], output[idx:]


def _preview(doc):
    head = doc[:PREVIEW_BYTES]
    return head + ("\n...(잘림 — 전문은 포인터로)" if len(doc) > PREVIEW_BYTES else "")


def persisted_message(pointer, doc, kind="Edit"):
    """컨텍스트에 잔류할 교체 메시지 — 원본 CC buildLargeToolResultMessage 축소판.
    (CC 원문 형식: "Full output saved to: …" / "Preview (first 2KB):")"""
    return (
        "<persisted-output>\n"
        f"{kind} 결과를 문서로 이관했습니다(컨텍스트 예산 보호). 전문 저장: {pointer}\n\n"
        f"Preview (first {PREVIEW_BYTES}B):\n{_preview(doc)}\n"
        "</persisted-output>"
    )


class ContextBudget:
    """전처리 ① — 문서화 저장소(doc_store)는 디스크 오프로드 흉내 (mem:// 포인터).
    실제 CC는 ~/.claude/projects/<proj>/<session>/tool-results/<id>.txt 에 전문을 쓴다."""

    def __init__(self, world, mode="budget"):
        self.world = world
        self.mode = mode                # "budget" | "edit_forced"
        self.doc_store = {}             # 포인터 -> 전문
        self.call_tool_name = {}        # call_id -> 도구 이름
        self.edit_meta = {}             # call_id -> {file_path, old_string, new_string, round}
        self.processed = set()          # 이미 오프로드한 call_id (멱등 — 원본 flag:'wx' 대응)
        self.last_offloaded = 0

    def note_call(self, call_id, name, args, round_no):
        """도구 실행 직후 세션이 호출 — edit 판별·문서화 메타 기록."""
        self.call_tool_name[call_id] = name
        if name == "edit_file" and isinstance(args, dict):
            self.edit_meta[call_id] = {
                "file_path": args.get("file_path"),
                "old_string": args.get("old_string"),
                "new_string": args.get("new_string"),
                "round": round_no,
            }

    def build_document(self, call_id, raw_output):
        """결과를 '문서화' — 실제 CC라면 tool-results/<id>.txt 로 갈 전문."""
        meta = self.edit_meta.get(call_id)
        if meta:
            fp = meta["file_path"]
            snapshot = self.world.fs[fp]["content"] if fp in self.world.fs else "(파일 없음)"
            return (
                f"[EDIT 문서화 · call_id={call_id} · 사이클 {meta['round']}]\n"
                f"파일: {fp}\n"
                f"교체(before→after):\n"
                f"- old: {meta['old_string']!r}\n"
                f"+ new: {meta['new_string']!r}\n"
                f"도구 결과 원문: {raw_output}\n"
                f"── 편집 후 파일 전문 스냅샷 ──\n{snapshot}"
            )
        name = self.call_tool_name.get(call_id, "?")
        return f"[TOOL 결과 문서화 · call_id={call_id} · 도구 {name}]\n{raw_output}"

    def _select_targets(self, fresh, total):
        pending = [it for it in fresh if it["call_id"] not in self.processed]
        if self.mode == "edit_forced":
            return [it for it in pending
                    if self.call_tool_name.get(it["call_id"]) == "edit_file"]
        # budget 모드 (CC 충실): 총합이 임계 이하면 아무것도 안 한다.
        if total <= BUDGET_CHARS:
            return []
        # 큰 결과부터 오프로드해 묶음을 임계 아래로 내린다
        targets = []
        for it in sorted(pending, key=lambda x: -len(x["output"])):
            if total <= BUDGET_CHARS:
                break
            targets.append(it)
            total -= len(it["output"])
        return targets

    def apply(self, fresh, trace=True):
        """사이클 맨 위, 모델 호출 직전 — 직전 사이클 묶음(fresh)만 in-place 치환한다."""
        self.last_offloaded = 0
        total = sum(len(it["output"]) for it in fresh)
        cmp = "＜" if total < BUDGET_CHARS else "≥"
        targets = self._select_targets(fresh, total)
        if trace and (fresh or self.mode == "edit_forced"):
            print(f"  ┌─ 전처리 ① applyToolResultBudget · 직전 묶음 {len(fresh)}건 "
                  f"총 {total:,}자 {cmp} 임계 {BUDGET_CHARS:,}자")
            if not fresh:
                print("  └─ 직전 사이클 없음 → no-op\n")
            elif not targets:
                print("  └─ 오프로드 대상 없음 → no-op\n")
            elif self.mode == "edit_forced" and total < BUDGET_CHARS:
                print("  │  (크기는 임계 미달이지만, 이 모드는 Edit 결과를 무조건 오프로드)")
        if not targets:
            return 0
        for it in targets:
            cid = it["call_id"]
            base, sr_tail = _split_sr_tail(it["output"])   # smoosh SR 꼬리 분리 보존
            is_edit = cid in self.edit_meta
            doc = self.build_document(cid, base)
            pointer = (f"mem://edit-docs/{cid}.txt" if is_edit
                       else f"mem://tool-results/{cid}.txt")
            self.doc_store[pointer] = doc                  # 문서화 = 변수 저장
            replaced = persisted_message(pointer, doc, kind="Edit" if is_edit else "도구")
            if sr_tail:
                replaced += sr_tail                        # 리마인더 SR 재부착 (보존 규칙)
            if trace:
                label = self.edit_meta.get(cid, {}).get("file_path") or self.call_tool_name.get(cid, "?")
                print(f"  │  🗂  {label}  전문 {len(doc):,}자 → 미리보기 {len(replaced):,}자  ·  {pointer}"
                      + ("  (SR 꼬리 보존)" if sr_tail else ""))
            it["output"] = replaced                        # input_list 안의 dict를 제자리 치환
            self.processed.add(cid)
        self.last_offloaded = len(targets)
        if trace:
            print(f"  └─ 결과 {len(targets)}건 오프로드 완료\n")
        return len(targets)

    def recall(self, pointer):
        """포인터로 전문 복구 — READ WINDOW가 열려 있는 동안만 가능 (닫히면 경로째 소실)."""
        return self.doc_store.get(pointer, f"ERROR: {pointer} 문서를 찾을 수 없습니다.")
