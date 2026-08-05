<!-- grok-build 하네스 컴팩션 시뮬레이션 — 대상: memory/data/conv-01.txt, 프롬프트: memory/techniques/grok-prompt.md -->

## 단계 1: 사전 메모리 플러시 (FLUSH_SYSTEM_PROMPT 적용 결과)

## Decisions & rationale

- **New canonical memory analysis doc**: Created `md_group/클로드코드-메모리-시스템.md` because the workspace's ~135 analysis docs had only ONE dedicated memory doc (`md_group/system_info/prompts/09-loadMemoryPrompt-analysis.md`, auto-memory only) — SessionMemory, sessionMemoryCompact, and findRelevantMemories were an identified coverage gap. Convention followed: `md_group/` holds the LLM-readable canonical md, HTML visualizations live at project root (pairing with `html_group_v2/` offered but not requested).
- **Full rewrite over patch** for `클로드코드-메모리-시스템.html` when updating with new findings, because the section structure changed substantially (6 → 9 sections).
- **Terminology correction adopted**: auto memory has 4 *types* (user/feedback/project/reference), not sections; the 10-section template belongs to session memory; the "8 sections" are the system-prompt *instructions* for auto memory. This three-way distinction was confusing enough to warrant a dedicated table in the doc (§2.5).

## Technical context

Claude Code source mirror at `/Users/seobi/jinsup_space/CC/src/` (1,902 TS files, ~512,670 lines, original — not decompiled). Memory lives in three axes:

- **Auto memory** (`src/memdir/`): `~/.claude/projects/<slug>/memory/` — `MEMORY.md` index (200 lines / 25KB cap, `memdir.ts:34-38`) + one file per topic with frontmatter (name/description/type). Loaded into the system prompt's dynamic D2 section via `loadMemoryPrompt()` (`memdir.ts:419-507`), evaluated once per session then cached → prompt-cache friendly. Written inline by the main agent (no coded trigger — model judgment; explicit "remember this" = save immediately, `memdir.ts:243`). Second, gated background path: `src/services/extractMemories/extractMemories.ts` — stop-hook at end of a complete query loop, gate `tengu_passport_quail`, throttle `tengu_bramble_lintel`, mutual-exclusion cursor skips the fork if the main agent already wrote memory files, `maxTurns: 5`, memory-dir-only write permission.
- **Session memory** (`src/services/SessionMemory/`): forked subagent maintains `~/.claude/projects/<slug>/<sessionId>/session-memory/summary.md` (path builders in `src/utils/permissions/filesystem.ts:259-270`). Fixed 10-section template (`prompts.ts:11-41`), caps 2,000/section, 12,000 tokens total. Trigger: post-sampling hook fired after every API response (`query.ts:992`, `void` fire-and-forget) passing 4 sequential gates — main REPL thread → `tengu_session_memory` gate (default OFF) → 10K-token init threshold → +5K growth (always required) AND (≥3 tool calls OR last turn tool-less). Token measure = `tokenCountWithEstimation` (`src/utils/tokens.ts:226`), same yardstick as autocompact. Fork copies full system prompt + messages (`createCacheSafeParams`, `forkedAgent.ts:131-141`) → prompt-cache hit; locked to editing summary.md only. `/summary` bypasses gates.
- **Compaction** (`src/services/compact/`): auto threshold = context window − 20,000 (summary output reserve) − 13,000 (buffer) (`autoCompact.ts:30,62`) ≈ 167K on a 200K model; `/compact` is the manual path. Output = boundary marker (`type: 'system'`, NOT sent to API, `messages.ts:4537-4550`) + summary as a **user message flagged `isCompactSummary: true`**, appended to the append-only `<sessionId>.jsonl` transcript with a transcriptPath recovery pointer (`prompt.ts:349-351`). `sessionMemoryCompact.ts` (EXPERIMENT) replaces the LLM ad-hoc summary with the pre-saved summary.md, waiting on in-flight extraction (`waitForSessionMemoryExtraction`, `:527`), preserving 10K–40K of recent messages.
- **Relevant-memory surfacing**: `src/memdir/findRelevantMemories.ts` (sideQuery on default Sonnet) → `attachments.ts:2234-2241` selects top 5 (`.slice(0, 5)`, `readMemoriesForSurfacing`) as a `relevant_memories` attachment → `messages.ts:3708-3712` wraps it in a `<system-reminder>`. Telemetry: `tengu_memdir_prefetch_collected` (`attachments.ts:2412`).
- Auto-memory prompt = 8-section assembly (`buildMemoryLines`, `memdir.ts:236-265`) with eval scores recorded in comments (H1 verification 0/2→3/3; same content buried as bullet 0/3 — placement matters; header wording "Before recommending from memory" 3/3 vs "Trusting what you recall" 0/3; known gap: slash-command claims 0/3). §9 "Searching past context" behind `tengu_coral_fern`.
- Version drift found: live build's system prompt has `[[name]]` wiki red-link guidance; mirror source has none (`grep '\[\['` in `src/memdir/` → 0 hits).

## Debugging techniques & tools

- **Grep-first source verification**: locate mechanisms by grepping identifiers (`registerPostSamplingHook`, `isCompactSummary`, `findRelevantMemories`) across `/Users/seobi/jinsup_space/CC/src`, then Read narrow line ranges — every claim cited as `file:line`.
- **Consumer census**: grep a flag's readers (excluding definitions) to infer its purpose, e.g. `isCompactSummary` consumers in `Message.tsx:159`, `MessageSelector.tsx:780`, `sessionStorage.ts:1752`, `compact.ts:798`, `useAwaySummary.ts:19`.
- **Empirical machine checks as gate evidence**: `find ~/.claude/projects -type d -name 'session-memory'` → 0 hits proved `tengu_session_memory` is OFF for this account.
- **Mirror-vs-live diffing**: comparing the current session's own system prompt against the source mirror to detect features added after the mirror snapshot (the `[[name]]` red-link discovery).

## Problems & solutions

- `grep "export function getProjectDir"` in `src/utils/sessionStorage.ts` returned nothing → widened to repo-wide grep; definition actually in `src/utils/sessionStoragePortable.ts:329` (slug = non-alphanumeric → hyphens) and `src/utils/cachePaths.ts:21`.
- User's mental-model errors corrected with source: "자동메모리는 4개의 섹션" → 4 types (storage has no sections); "컴팩션은 /compact 사용 시" → auto-compaction is the primary trigger, `/compact` is the manual option.
- User's framing "대화 컨텍스트로 모를만한 일을 적는다" corrected to the opposite axis: auto memory stores what exists **only** in the conversation and is non-derivable via tools (grep/git/CLAUDE.md are authoritative for the rest).
- "Why only this much / why exactly 4 types": purpose sentence (`memdir.ts:241`) maps 1:1 to WHO(user)/HOW(feedback)/WHY(project)/WHERE(reference); WHAT is delegated to tools (`memoryTypes.ts:4-7`); when needs grew, Anthropic added scope/lifetime axes (TEAMMEM, KAIROS, session memory) rather than a 5th type.

## 단계 1b: 증분 플러시 (FLUSH_DELTA_SYSTEM_PROMPT)

*해당 없음 — 같은 세션 내 선행 플러시가 없으므로(1회차) 증분 플러시는 실행되지 않음.*

## 단계 2: 풀 리플레이스 컴팩션 (구조화 요약 프롬프트 적용 결과)

<summary>
1. Primary Request and Intent:

The user is researching Claude Code internals inside `/Users/seobi/jinsup_space/CC` — a workspace holding a full TypeScript source mirror (`src/`, 1,902 files) plus ~135 analysis markdown docs (`md_group/`) and paired HTML visualizations. Explicit requests, in order of evolution:

- "프로젝트 코드랑 내용 전체 파악 해 자 시작!" — comprehend the entire project (done via two parallel Explore subagents: doc catalog + source structure map).
- A sustained Socratic Q&A drilling into Claude Code's memory system, driven by short clarifying questions: what auto memory and session memory are; where each is stored; where compaction output goes; exactly when session memory triggers ("도대체 언제 트리거되는거야.."); what the "4중게이트" means; who writes session memory (main agent vs subagent); what "10K 토큰" measures; the 10 sections and injection timing/channel ("시스템리마인더로 들어가나?"); whether updates land on a strict 5K grid; what `isCompactSummary` is; how the summary enters the API message array ("배열로치면 최소 원소 2개?"); what the boundary marker is and whether the note auto-enters context when written; what "컴팩션 순간" concretely is; experimental vs official status; when auto memory updates; why auto memory's narrow scope is meaningful; why it records those things and why 4 types suffice; whether the structure is an "LLM 위키"; and finally whether frontmatter-driven relevant memories are injected into prompts as system reminders.
- Deliverables: (a) `/visual-explainer` page of the memory findings ("메모리에대한 내용들 .. 우리 나눈 대화들을 /visual-explainer 로 정리해서 남겨줘"); (b) "이 내용까지 반영해서 아까 만든 HTML 업데이트해줘"; (c) explain the auto-memory instruction sections and each section's effect; (d) fact-check the user's own 3-memory summary ("이거 설명맞는지도 알려주라"); (e) approve adding the 8-section analysis to the md doc ("...추가해 둘까요? <- 응"); (f) a second `/visual-explainer` with args "위 내용들 세세히 적어! 빠짐없이!" → dedicated auto-memory deep-dive page.
- Standing constraints: every claim must be verified against the local source mirror with `file:line` citations (workspace principle); the user prefers analogy + table explanations and interrupts builds to get concept questions answered first.

2. Key Technical Concepts:

- Auto memory (`src/memdir/`): `MEMORY.md` index + topic files with frontmatter; 4 memory types (user/feedback/project/reference); 200-line/25KB entrypoint cap; system-prompt dynamic section D2; once-per-session evaluation + prompt-cache economics; 2-tier "index always aboard, bodies on-demand via Read".
- Session Memory (`src/services/SessionMemory/`): background forked-subagent notes (`summary.md`); fixed 10-section template; caps 2,000 chars/section, 12,000 tokens total; post-sampling hook trigger; thresholds 10K init / +5K growth (mandatory) / ≥3 tool calls or tool-less turn; feature gate `tengu_session_memory` (default OFF); `/summary` manual bypass.
- Compaction (`src/services/compact/`): autoCompact threshold = context window − 20K − 13K (≈167K @200K); `/compact` manual; boundary marker (`type:'system'`, never sent to API); summary as user message with `isCompactSummary: true`; append-only `.jsonl` transcript + transcriptPath recovery pointer; `sessionMemoryCompact` EXPERIMENT (reuse summary.md instead of ad-hoc LLM summary; preserve 10K–40K recent tokens).
- Forked agents: `createCacheSafeParams` copies main system prompt + full message history → prompt-cache hit; single-file permission lock (`createMemoryFileCanUseTool`); `void` fire-and-forget + `sequential()` serialization.
- Background auto-memory extraction (`src/services/extractMemories/`): stop-hook timing (end of complete query loop, final response with no tool calls); gates `tengu_passport_quail` + throttle `tengu_bramble_lintel`; mutual-exclusion cursor vs main-agent inline writes; `maxTurns: 5`; manifest pre-injection; 60s drain.
- Relevant-memory surfacing: `findRelevantMemories` (sideQuery on default Sonnet, JSON-parsed) → `relevant_memories` attachment (top 5) → `wrapMessagesInSystemReminder` → `<system-reminder>` channel.
- Three injection channels: MEMORY.md → system prompt (always); summary.md → `isCompactSummary` user message (compaction moment only); relevant memories / status → `<system-reminder>` attachments (per-turn, situational).
- Eval-instrumented prompt engineering: hypotheses H1–H6 with scores (0/2→3/3), placement sensitivity (bullet burial → 0/3), header-wording experiments (3/3 vs 0/3), known gaps (slash commands 0/3) recorded in source comments.
- Memory-as-wiki: semantic/topic organization ("not chronologically", `teamMemPrompts.ts:38`), update-in-place, frontmatter description as search snippet, `[[name]]` red links (live build only — mirror predates it).
- GrowthBook `tengu_*` feature gates as a rollout pipeline; `tokenCountWithEstimation` (API-reported usage anchor + estimation); Explore subagents; `/visual-explainer` skill.

3. Files and Code Sections:

Examined (Claude Code source mirror — read-only evidence):
- `/Users/seobi/jinsup_space/CC/src/memdir/memdir.ts` — auto-memory core. `loadMemoryPrompt()` :419-507 (3 branches: KAIROS / TEAMMEM / normal); caps `MAX_ENTRYPOINT_LINES = 200` :35, `MAX_ENTRYPOINT_BYTES = 25_000` :38; `truncateEntrypointContent` :57; `DIR_EXISTS_GUIDANCE` :111-115 ("Claude was burning turns on ls/mkdir"); purpose sentence :241; explicit-save rule :243; instruction assembly `buildMemoryLines` :236-265 (8 sections); index rules :227/:233 ("MEMORY.md is an index, not a memory"; dedupe); `buildSearchingPastContextSection` :375-407 behind `tengu_coral_fern`.
- `/Users/seobi/jinsup_space/CC/src/memdir/memoryTypes.ts` — 4-type taxonomy header :4-7 ("NOT derivable from the current project state"); typed XML blocks :113-178; What NOT to save :183-195 (H2 eval 0/2→3/3 at :192-194); When to access :216-222 + "ignore" anti-pattern note :208-212 (branch-pollution evals #22856); Before recommending from memory :240-256 with eval records :228-244 (H1, placement, header wording, H5, slash-command gap).
- `/Users/seobi/jinsup_space/CC/src/memdir/findRelevantMemories.ts` — imports show a `sideQuery` on `getDefaultSonnetModel` with JSON-parsed output for relevance selection; feature-gated.
- `/Users/seobi/jinsup_space/CC/src/memdir/teamMemPrompts.ts` :38,55 — "Organize memory semantically by topic, not chronologically".
- `/Users/seobi/jinsup_space/CC/src/services/SessionMemory/sessionMemory.ts` — header definition :1-5; gate read :80-82; `shouldExtractMemory` / thresholds :134-181 (growth always required, "prevents excessive extractions" :165-167); `sequential()` :272; extraction flow :290-325 ("runForkedAgent for prompt caching" :315; `createMemoryFileCanUseTool` :321); `recordExtractionTokenCount` :344; `manuallyExtractSessionMemory` :387.
- `/Users/seobi/jinsup_space/CC/src/services/SessionMemory/prompts.ts` — 10-section template :11-41; `MAX_SECTION_LENGTH = 2000` :8; `MAX_TOTAL_SESSION_MEMORY_TOKENS = 12000` :9; "Always update 'Current State' … continuity after compaction" :69; do-not-mention rule :44-46; custom template/prompt paths `~/.claude/session-memory/config/` :86-120.
- `/Users/seobi/jinsup_space/CC/src/services/SessionMemory/sessionMemoryUtils.ts` — `DEFAULT_SESSION_MEMORY_CONFIG` :32 (`toolCallsBetweenUpdates: 3` :35, `minimumMessageTokensToInit: 10000` :33, `minimumTokensBetweenUpdate: 5000`); same-token-counting-as-autocompact comment :20-22; `hasMetInitializationThreshold` :173; `hasMetUpdateThreshold` :184-189.
- `/Users/seobi/jinsup_space/CC/src/services/compact/sessionMemoryCompact.ts` — "EXPERIMENT" header :1-3; `getSessionMemoryPath` use :16/:472; `createCompactionResultFromSessionMemory` :437-482 (builds `createUserMessage({ isCompactSummary: true, … })`; truncation pointer "full session memory can be viewed at: {memoryPath}" :461-474); `waitForSessionMemoryExtraction` :527; min 10K / max 40K recent-message preservation.
- `/Users/seobi/jinsup_space/CC/src/services/compact/compact.ts` — post-compaction assembly :590-624 (SessionStart hooks :592; boundary + summary creation :598-624); context-size accounting :637-642 (`boundaryMarker + summaryMessages + postCompactFileAttachments + hookMessages`); KAIROS segment files :713-717; prior-summary detection :798.
- `/Users/seobi/jinsup_space/CC/src/services/compact/prompt.ts` — `getCompactUserSummaryMessage` :337-351; transcriptPath pointer text :349-351 ("read the full transcript at: {transcriptPath}").
- `/Users/seobi/jinsup_space/CC/src/services/compact/autoCompact.ts` — `MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000` :30; `getEffectiveContextWindowSize` :33; `AUTOCOMPACT_BUFFER_TOKENS = 13_000` :62; `WARNING_THRESHOLD_BUFFER_TOKENS = 20_000` :63; `getAutoCompactThreshold` :72.
- `/Users/seobi/jinsup_space/CC/src/services/extractMemories/extractMemories.ts` — header :1-7 ("runs once at the end of each complete query loop (final response with no tool calls) via handleStopHooks"); entry conditions :531-552; throttle :374-386; mutual exclusion :345-360 ("skipping — conversation already wrote to memory files"); stash-latest-context :554-564; fork spec :415-427, :579-586, :611-615.
- `/Users/seobi/jinsup_space/CC/src/utils/permissions/filesystem.ts` :259-270 — session-memory paths:
```typescript
// Path format: {projectDir}/{sessionId}/session-memory/
export function getSessionMemoryDir(): string {
  return join(getProjectDir(getCwd()), getSessionId(), 'session-memory') + sep
}
// Path format: {projectDir}/{sessionId}/session-memory/summary.md
export function getSessionMemoryPath(): string {
  return join(getSessionMemoryDir(), 'summary.md')
}
```
- `/Users/seobi/jinsup_space/CC/src/utils/sessionStoragePortable.ts` :300-331 — `getProjectDir` slug (non-alphanumeric → hyphens) under `~/.claude/projects/`.
- `/Users/seobi/jinsup_space/CC/src/utils/tokens.ts` :226 (+ comment :218-222) — `tokenCountWithEstimation`: last API-reported usage anchor + estimation of newer items.
- `/Users/seobi/jinsup_space/CC/src/utils/messages.ts` — `compact_boundary` :4537-4550 (`type: 'system'`, "Conversation compacted" + metadata, not sent to API); `microcompact_boundary` :4569; `isCompactBoundaryMessage` :4608; `isCompactSummary` flag :465-511; `case 'relevant_memories'` :3708-3712 → `wrapMessagesInSystemReminder(...)`.
- `/Users/seobi/jinsup_space/CC/src/query.ts` :92/:992 — `void executePostSamplingHooks(...)` fired after each completed API response, before tool execution.
- `/Users/seobi/jinsup_space/CC/src/utils/forkedAgent.ts` :131-141 — `createCacheSafeParams`:
```typescript
return {
  systemPrompt: context.systemPrompt,      // 메인과 동일한 시스템 프롬프트
  forkContextMessages: context.messages,   // 메인 대화 전체를 그대로 복사
  ...
}
```
- `/Users/seobi/jinsup_space/CC/src/utils/attachments.ts` — relevant-memory surfacing :2234-2242 (`.slice(0, 5)` → `readMemoriesForSurfacing(selected, signal)` → `[{ type: 'relevant_memories', memories }]`); telemetry `tengu_memdir_prefetch_collected` :2412; callers of `findRelevantMemories` also include `collapseReadSearch.ts`, `transcriptSearch.ts`, `claudemd.ts`.
- Reference doc: `/Users/seobi/jinsup_space/CC/md_group/system_info/prompts/09-loadMemoryPrompt-analysis.md` — the only pre-existing dedicated memory analysis (auto memory / D2 / 4 types / KAIROS·TEAMMEM branches).

Created/modified (this session's work product; full file contents are not reproduced in the retained transcript — Write payloads were truncated):
- `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html` — created (7 sections, "기억의 지층" dark-archive theme), then fully rewritten to 9 sections (added: fork anatomy, 세 기억 세 채널, official-vs-experiment status board; expanded gates and isCompactSummary coverage). Opened in browser via `open`.
- `/Users/seobi/jinsup_space/CC/md_group/클로드코드-메모리-시스템.md` — created as the canonical 10-chapter analysis (three layers → auto memory → session memory → reality/gates → compaction → SM-compaction EXPERIMENT → input channels → disk map → 7 portable design patterns → full `file:line` source table). Then 3 Edits: new §2.5 "시스템 프롬프트 지침 — 8섹션 조립과 각 섹션의 '측정된' 효과" (with terminology-confusion table and all eval records), §10 source-table additions, 변경이력 entry.
- `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` — created (7 sections: 2×2 matrix, WHO/HOW/WHY/WHERE mapping, 4-type sufficiency, 2 update paths, 8-section instruction stack, eval bar charts, narrow-scope economics), opened in browser. A second full-rewrite Write (folding in the wiki/findRelevantMemories findings) was in flight when the conversation was cut off.

4. Errors and Fixes:

- `grep "export function getProjectDir"` on `src/utils/sessionStorage.ts` returned no output (definition not there). Fixed by widening to a repo-wide grep: definitions found at `src/utils/cachePaths.ts:21` and `src/utils/sessionStoragePortable.ts:329` (the portable one builds the `~/.claude/projects/<slug>` path).
- `grep -rn '\[\['` over `src/memdir/` → zero matches, conflicting with the `[[name]]` wiki-link guidance visible in the live session's system prompt. Resolved as version drift: the mirror snapshot predates the red-link feature — noted as a fact worth recording for the project.
- User interrupted a bare `/visual-explainer` invocation ([Request interrupted by user]) before the build started; fix: answered the pending conceptual question first, and the visualization was later redone via `/visual-explainer` with explicit args ("위 내용들 세세히 적어! 빠짐없이!") and completed.
- User feedback corrections (verbatim): "그니까 너의말은 대화 컨텍스트로 모를만한 일을 적ㅇ는다는건가" → corrected to the opposite: it records what exists *only* in the conversation ("대화에만 있는 일"), not what the conversation can't know. "내요지는 저정도만 기록하냐라긴보다 왜 저걸 기록하냐랄까" + "그리고 왜 4타입이면 충분하달까" → pivoted the answer from scope-economics to the WHO/HOW/WHY/WHERE ↔ 4-type mapping and the sufficiency argument (WHAT is tool-derivable; Anthropic varies scope/lifetime axes, never the type axis).
- Corrected the user's summary in the fact-check turn: 자동메모리 has 4 *types* not "4개의 섹션" (sections belong to session memory's 10-section template / the instruction stack's 8 sections); compaction fires *automatically* at threshold — `/compact` is only the manual option; the summary is not a separate file but an inserted user message recorded in `.jsonl`.
- No build/test/tool failures otherwise — analysis-only session.

5. Problem Solving:

Solved: mapped the entire CC memory landscape into three layers (auto memory / session memory / compaction) and their disk layout under `~/.claude/projects/<slug>/`; determined session-memory storage path and proved the feature gate is OFF on this machine (zero `session-memory/` dirs across `~/.claude/projects`); pinned the session-memory trigger to the post-sampling hook at `query.ts:992` with 4 sequential gates and clarified "5K is a floor, not a grid" (baseline reset via `recordExtractionTokenCount`); identified `isCompactSummary` semantics and its 5 consumer sites; established the post-compaction API message array shape (summary user message is a separate element from the real question; boundary marker never reaches the API); distinguished official vs experimental features (auto memory & compaction official; session memory `tengu_session_memory` OFF; sessionMemoryCompact "experiment within experiment"); found auto memory's dual update paths (inline model-judgment writes vs gated `extractMemories` stop-hook fork) with a mutual-exclusion cursor; articulated the narrow-scope rationale (derivable info has authoritative sources; noise harm is eval-measured; index-always-aboard economics; high leverage per byte — e.g. the real "레포 2-머신 공유 · 경로는 ~ 중립 표기" memory entry); validated the "LLM wiki" reading (topic-semantic organization, update-in-place, frontmatter-as-snippet, red links in the live build).

In progress at cutoff: confirming the user's final hypothesis — that frontmatter-driven relevant memories are injected situationally as system reminders. Evidence already gathered and pointing to "yes, via the attachment channel": `findRelevantMemories.ts` (Sonnet sideQuery) → `attachments.ts:2234-2241` top-5 `relevant_memories` attachment → `messages.ts:3708-3712` `wrapMessagesInSystemReminder`. The confirming reply to the user was not yet delivered; the deep-dive HTML rewrite embedding these findings was mid-write.

6. All User Messages:

- "프로젝트 코드랑 내용 전체 파악 해 자 시작!"
- [task-notification: Explore agent "src 소스 구조 전체 파악" completed — source map + memory code report]
- [task-notification: Explore agent "md_group 문서 전체 카탈로그" completed — doc catalog + coverage report]
- "자동 메모리, 세션 메모리 가 뭐야?"
- "세션 메모리는 어디에 저장되는데?"
- "메모리.md랑 summary.md랑 같이 있는거구나"
- "컴팩션하면 그건 어디에 저장되는데?"
- "메모리에대한 내용들 .. 우리 나눈 대화들을 /visual-explainer 로 정리해서 남겨줘"
- "세션 메모리는 도대체 언제 트리거되는거야.."
- "4중게이트가 뭔지모르겠어?"
- "그 세션메모리는 메인에이전트에서 만드는거야 ?"
- "아아 만드는 건 서브에이전트지만 메인 히스토리 기준으로 만든다는거지?"
- "그래서 어느타이밍에 작성한다구?"
- "10K 토큰 도달??"
- "그리고 여러섹션이 들어간다했는데 어떤 섹션들이고 그 메모리가 LLM에 어느타이밍에 인풋해? 시스템리마인더로 들어가나?"
- "그러면 10K -> 5K(15K) -> 5K(20K) 이렇게 5K마다 갱신인거지?"
- "isCompactSummary 이건 또 ㅜ머야.."
- "음... 저 유저 프롬프트가 엔터칠떄 같이들어가? 그럼 질문과 별개의 인풋으로들어가겟네? 배열로치면 최소 원소 2개?"
- "경계마커는 무슨말이야 아무튼 그.. 18K에서 저 세션메모리를 만들었다치자.. 만드는순간 알아서 들어가?"
- "컴팩션 순간?..?????"
- "뭐야 그냥 실험기능 정도구나?"
- "그러면 중요한게 세션메모리가 아니라 메인에이전트가 만드는 메모리곘네?"
- "자동메모리가 적힌건 항상  질문할때마다 인풋이되게네?"
- "이 내용까지 반영해서 아까 만든 HTML 업데이트해줘"
- "자동메모리 섹션에대해 잘 설명하고 그 각 섹션의 효과까지좀 알려주라"
- "자동메모리, 세션메모리, 컴팩션으로 만드는 메모리 이렇게 3개의 종류의 메모리가 있다. 자동메모리는 4개의 섹션으로 만드는 프로젝트전용이고 세션메모리는 해당 세션만을 위한 메모리다. 세션 메모리는 메인 에이전트 히스토리로 작성되나 작성은 서브에이전트가 진행하며 실험기능에 속하는 편이다. \n컴팩션은 /compact를 사용했을때 그때 완성되는 요약 내용이다. \n\n\n이거 설명맞는지도 알려주라"
- "이 내용을 md_group/클로드코드-메모리-시스템.md의 §2(자동 메모리)에 추가해 둘까요? <- 응"
- "auto memory 가 갱신되는 타이밍이언제야"
- "자동메모리가 저정도만 기록하는데.. 의미가 잇는건가? 그 이유는?"
- "/visual-explainer" (command invocation, no args)
- "[Request interrupted by user]"
- "그니까 너의말은 대화 컨텍스트로 모를만한 일을 적ㅇ는다는건가"
- "내요지는 저정도만 기록하냐라긴보다 왜 저걸 기록하냐랄까"
- "그리고 왜 4타입이면 충분하달까"
- "/visual-explainer — args: 위 내용들 세세히 적어! 빠짐없이!"
- "근데 실제 파일보니까 MEMORY.md 은인덱싱처럼 되어있고 나머지 문서로 나뉘어져 상세내용처럼되어있어 마치 LLM 위키같은건가"
- "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??"

7. Pending Tasks:

- Answer the user's final question — confirm (with `file:line` evidence) that relevant memories are surfaced via the `relevant_memories` attachment wrapped in a `<system-reminder>` — and finish the interrupted full rewrite of `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` that folds these wiki/injection-path findings into the page.

8. Current Work:

Immediately before this summary, I was verifying the user's hypothesis that auto memory works like a wiki whose frontmatter gets read and injected situationally as system reminders. Steps taken: (1) Read `/Users/seobi/jinsup_space/CC/src/memdir/findRelevantMemories.ts` in full — imports show a `sideQuery` on the default Sonnet model with JSON parsing (LLM-based relevance selection); (2) grepped callers outside memdir — `src/utils/attachments.ts`, `collapseReadSearch.ts`, `transcriptSearch.ts`, `claudemd.ts`, `components/messages/CollapsedReadSearchCon…`; (3) Read `attachments.ts:2234-2242` — selected memories capped at `.slice(0, 5)`, loaded via `readMemoriesForSurfacing(selected, signal)`, emitted as `[{ type: 'relevant_memories', memories }]`; (4) confirmed the render path at `messages.ts:3708-3712` — `case 'relevant_memories':` returns `wrapMessagesInSystemReminder(attachment.memories.map(m => { /* header stored at attachment-creation time */ … }))`; (5) found telemetry `logEvent('tengu_memdir_prefetch_collected', …)` at `attachments.ts:2412`. Conclusion (not yet delivered to the user): the hypothesis is essentially correct — relevant memories enter as `<system-reminder>` attachments, the third injection channel alongside the always-on system-prompt index and the compaction-time `isCompactSummary` user message. I had just issued a Write to fully rebuild `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` with these findings when the transcript was cut off mid-write ("[... 이후 절단됨 ...]").

9. Optional Next Step:

Finish the in-flight rewrite of `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` (re-issue the Write with the full updated page, then `open` it), and deliver the confirming answer to the user's last message — "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??" — citing `findRelevantMemories.ts` (Sonnet sideQuery selection), `attachments.ts:2234-2242` (top-5 `relevant_memories` attachment), and `messages.ts:3708-3712` (`wrapMessagesInSystemReminder`), with the one nuance that selection is LLM/description-driven and capped at 5, and the channel is the attachment system's `<system-reminder>`, not the user's own prompt text. Where I left off: my last visible action was the tool call `Write {"file_path": "/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html", …}` immediately after reading the injection-path sources.
</summary>

## 단계 2 대안: SELF_SUMMARIZATION_PROMPT

*미실행 — short-prompt 하네스 전용 대안 경로이며, 기본 파이프라인(단계 2)이 수행되었으므로 생략.*

## 단계 3: 재주입 캐리어 텍스트 (하네스 조립 결과)

This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
*({cleaned} 자리 — 위 단계 2의 `<summary>` 블록 내용이 정리되어 여기에 스플라이스됨. 치환 변수이므로 시뮬레이션에서는 본문 재복제 생략.)*

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: *({loc} — 원시 transcript 경로, 치환 변수이므로 무시)*

## 단계 4: 장기 메모리 통합 (DREAM_SYSTEM_PROMPT 적용 결과)

## Claude Code memory architecture — three layers

Claude Code (source mirror at `/Users/seobi/jinsup_space/CC/src/`) implements memory as three mechanisms with different lifetimes, writers, and injection channels:

| Layer | Lifetime | Writer | Injection channel | Status |
|---|---|---|---|---|
| Auto memory (`src/memdir/`) | Cross-session, per project | Main agent inline (model judgment); gated background fork (`extractMemories`) | System prompt dynamic section D2, every request | Official |
| Session memory (`src/services/SessionMemory/`) | One session | Forked subagent, background | `isCompactSummary` user message, only at compaction | Experiment (`tengu_session_memory`, default OFF) |
| Compaction summary (`src/services/compact/`) | Moment of compaction | LLM ad-hoc summary (or summary.md reuse, EXPERIMENT) | User message replacing old history; recorded in append-only `.jsonl` with transcriptPath recovery pointer | Official |

Disk layout: `~/.claude/projects/<slug>/memory/MEMORY.md` (+ topic files) sits at project level; `<sessionId>/session-memory/summary.md` sits inside the session UUID; `<sessionId>.jsonl` is the immutable transcript. The slug replaces non-alphanumerics with hyphens (`sessionStoragePortable.ts:329`).

## Auto memory design — narrow scope is the point

- Only 4 types are stored — user (WHO), feedback (HOW), project (WHY), reference (WHERE) — mapping 1:1 to the purpose sentence at `memdir.ts:241`. WHAT is deliberately excluded because it is derivable: grep/Read for code, `git log` for history, CLAUDE.md for conventions (`memoryTypes.ts:4-7`). Storing derivable info creates a second, staling authority; the design's first defense is not writing it, the second is recall-time verification ("Before recommending from memory": memory says X exists ≠ X exists now).
- When needs outgrew the 4 types, Anthropic added *axes*, not types: TEAMMEM (private/team scope), KAIROS (daily log), session memory (in-session continuity) — evidence the taxonomy is stable.
- MEMORY.md is an index, not a memory: 200-line/25KB cap, one-line ≤150-char pointers, semantic (topic) organization, update-in-place, dedupe-before-write. Bodies are read on demand via the Read tool. Loaded once per session into the system prompt, so it rides the prompt cache (~1/10 cost); new saves take effect next session.
- The memory prompt is an 8-section assembly (`buildMemoryLines`, `memdir.ts:236-265`) whose sentences are eval-instrumented in source comments: H1 recall-verification 0/2→3/3 but 0/3 when buried as a bullet (placement matters); header wording "Before recommending from memory" 3/3 vs "Trusting what you recall" 0/3; H2 explicit-save gate ("ask what was surprising" instead of storing PR lists) 0/2→3/3; the "ignore my memory" anti-pattern needed explicit naming (branch-pollution evals #22856); known gap: slash-command claims 0/3. Lesson: prompts are tuned by measurement, not intuition.
- The structure is effectively an LLM wiki: topic pages + index, frontmatter (name/description/type) as metadata/search snippet, and — in builds newer than the mirror — `[[name]]` red links (a link to a not-yet-written memory marks it worth writing). Relevant memories are surfaced situationally: `findRelevantMemories.ts` runs a Sonnet sideQuery over descriptions, `attachments.ts:2234-2242` caps selection at 5 and emits a `relevant_memories` attachment, `messages.ts:3708-3712` wraps it in `<system-reminder>`. So auto memory reaches the model through two channels: always-on index (system prompt) and situational top-5 bodies (system-reminder attachment).

## Session memory & compaction mechanics

- Session memory: a post-sampling hook fires after every API response (`query.ts:992`, `void` fire-and-forget). Four sequential conditions gate extraction: main REPL thread → `tengu_session_memory` ON → conversation ≥10K tokens (init) → ≥+5K growth since last extraction (always required) AND (≥3 tool calls OR last turn tool-less). 5K is a floor, not a grid — the baseline resets to the actual context size at each extraction (`recordExtractionTokenCount`). Tokens measured by `tokenCountWithEstimation` (`tokens.ts:226`), the same yardstick as autocompact.
- The writer is a fork of the main agent: `createCacheSafeParams` (`forkedAgent.ts:131-141`) copies the main system prompt + full message history (prompt-cache hit ⇒ near-free), appends one instruction, and is permission-locked to editing `summary.md` only. The main conversation never sees it. Template: 10 fixed sections (Session Title / Current State / Task specification / Files and Functions / Workflow / Errors & Corrections / Codebase and System Documentation / Learnings / Key results / Worklog), 2,000 chars/section, 12,000 tokens total. `/summary` bypasses the gates.
- Writing and reading are fully decoupled: writes are disk-only savings; the note is read exactly once, at compaction (`waitForSessionMemoryExtraction` ensures freshness) — insurance that pays out only when the context cliff hits.
- Compaction: auto threshold = context window − 20K (summary output reserve) − 13K (buffer) ≈ 167K on a 200K model (`autoCompact.ts:30,62,72`); `/compact` is the manual path. Result = boundary marker (`type:'system'`, harness-internal, never sent to the API) + the summary as a separate user message flagged `isCompactSummary: true` (consumers: UI rendering, rewind exclusion, resume-title skipping, next-compaction detection, away-summary logic). The original conversation survives in the append-only `.jsonl`, and the summary embeds a transcriptPath pointer so the model can Read its own past — lossy compression with a recovery pointer.
- Auto memory's background extraction path (`extractMemories.ts`, gates `tengu_passport_quail`/`tengu_bramble_lintel`) runs at stop-hook time (turn fully finished, no tool calls) with a mutual-exclusion cursor: if the main agent already wrote memory files, the fork is skipped — two writers, no double-writes.

## Research artifacts produced in the CC workspace

- `md_group/클로드코드-메모리-시스템.md` — new canonical 10-chapter memory analysis (with §2.5 on the 8-section instruction stack and its eval-measured effects), filling the workspace's biggest documentation gap (previously only `09-loadMemoryPrompt-analysis.md` covered memory, and only the auto-memory branch).
- `클로드코드-메모리-시스템.html` (project root, 9 sections) and `자동메모리-딥다이브.html` (7 sections) — human-facing visualizations of the same source-verified content; the deep-dive page still needs the wiki/injection-path findings folded in.
- Noted for the project: the mirror predates the `[[name]]` red-link guidance present in live builds — a recordable version-drift fact.

## Source-verification workflow

- Grep identifiers repo-wide, then Read narrow line ranges; cite every claim as `file:line`. Census a flag's consumers (grep excluding definitions) to infer purpose. Use empirical machine checks as gate evidence (zero `session-memory/` dirs under `~/.claude/projects` ⇒ `tengu_session_memory` OFF for this account). Compare the live session's own system prompt against the mirror to detect post-snapshot features.
