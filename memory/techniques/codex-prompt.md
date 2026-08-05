<!--
출처 (verbatim, 이스케이프 해제 불필요 — 원본이 .md 템플릿 파일):
- 단계 1: /Users/seobi/jinsup_space/codex/codex-rs/prompts/templates/compact/prompt.md
  (SUMMARIZATION_PROMPT — codex-rs/prompts/src/compact.rs:1 에서 include_str!,
   core/src/compact.rs:119-124 자동 컴팩션 / core/src/tasks/compact.rs:66-76 수동 /compact 에서
   대화 히스토리 끝에 user 메시지로 append 되어 요약을 생성시킨다)
- 단계 2: /Users/seobi/jinsup_space/codex/codex-rs/prompts/templates/compact/summary_prefix.md
  (SUMMARY_PREFIX — core/src/compact.rs:351 에서 `{SUMMARY_PREFIX}\n{요약본문}` 형태로
   교체 히스토리의 마지막 user 메시지 앞에 붙는다)
치환부 없음. 만약 {{...}} / ${...} 형태가 보이면 시뮬레이션 시 무시.
-->

## 단계 1: 요약 생성 프롬프트 (SUMMARIZATION_PROMPT — 히스토리 끝에 user 메시지로 주입)

You are performing a CONTEXT CHECKPOINT COMPACTION. Create a handoff summary for another LLM that will resume the task.

Include:
- Current progress and key decisions made
- Important context, constraints, or user preferences
- What remains to be done (clear next steps)
- Any critical data, examples, or references needed to continue

Be concise, structured, and focused on helping the next LLM seamlessly continue the work.

## 단계 2: 요약 재주입 프리픽스 (SUMMARY_PREFIX — 생성된 요약 본문 바로 앞에 붙여 user 메시지로 저장)

Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:
