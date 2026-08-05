<!-- claude-code 하네스 컴팩션 시뮬레이션 — 대상: memory/data/conv-01.txt
     단계 1(세션메모리 사전 플러시) → 단계 2(메인 컴팩션 요약) → 단계 3(요약 재주입 래퍼) 순.
     변형 A/B(부분 컴팩션 전용)는 본 시뮬레이션(전체 컴팩션) 범위 밖이라 미수행. -->

## 단계 1: 사전 플러시 — 세션메모리 증분 추출

_아래는 포크 에이전트가 병렬 Edit 호출로 갱신을 마친 뒤의 노트 파일(summary.md) 최종 내용이다. (초기 상태 = DEFAULT_SESSION_MEMORY_TEMPLATE, 치환부 {{notesPath}}/{{currentNotes}}는 지시대로 무시)_

````markdown
# Session Title
_A short and distinctive 5-10 word descriptive title for the session. Super info dense, no filler_

Claude Code memory internals deep-dive: auto memory, session memory, compaction

# Current State
_What is actively being worked on right now? Pending tasks not yet completed. Immediate next steps._

Answering the user's latest question: whether auto-memory topic files are surfaced situationally (via frontmatter) into the prompt as system-reminders. Confirmed in source: `src/memdir/findRelevantMemories.ts` (sideQuery with Sonnet model) → `src/utils/attachments.ts` selects top 5 candidates (`.slice(0, 5)`) → `readMemoriesForSurfacing(selected, signal)` → returns `[{ type: 'relevant_memories', memories }]` attachment → `src/utils/messages.ts:3708` `case 'relevant_memories'` renders via `wrapMessagesInSystemReminder(...)`. So the user's hypothesis is correct — relevant memories enter through the attachment system wrapped in `<system-reminder>`. Telemetry event `tengu_memdir_prefetch_collected` at `attachments.ts:2412`; a `RELEVANT_MEMORIES_CONFIG` exists nearby.

A Write call to rewrite `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` (adding this finding) was just issued; completion not yet confirmed. Immediate next steps: finish the HTML rewrite, open it, and reply to the user confirming the system-reminder injection path with file:line evidence.

# Task specification
_What did the user ask to build? Any design decisions or other explanatory context_

Initial request: full comprehension of the `/Users/seobi/jinsup_space/CC` workspace (Claude Code original TypeScript source mirror + ~135 analysis markdown docs). Then an extended Q&A deep dive into Claude Code's three memory layers — auto memory (`src/memdir/`), session memory (`src/services/SessionMemory/`), compaction (`src/services/compact/`) — with every claim verified against local source (file:line citations, project convention). Deliverables requested along the way:
- `/visual-explainer` HTML of the memory-system conversation → `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html` (later fully rewritten to 9 sections on request "이 내용까지 반영해서 아까 만든 HTML 업데이트해줘")
- LLM-readable canonical doc `/Users/seobi/jinsup_space/CC/md_group/클로드코드-메모리-시스템.md` (10 chapters; later §2.5 added on user's "응")
- `/visual-explainer 위 내용들 세세히 적어! 빠짐없이!` → `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` (7 sections; currently being rewritten to include the relevant_memories/system-reminder finding)

# Files and Functions
_What are the important files? In short, what do they contain and why are they relevant?_

- `src/memdir/memdir.ts` — auto memory core. `ENTRYPOINT_NAME='MEMORY.md'`, `MAX_ENTRYPOINT_LINES=200`, `MAX_ENTRYPOINT_BYTES=25_000` (:34-38), `truncateEntrypointContent` (:57), `DIR_EXISTS_GUIDANCE` (:111-115, "Claude was burning turns on ls/mkdir -p"), index rules (:218-234, one line ≤150 chars, semantic organization :214, dedup :233), purpose sentence (:241), explicit-save rule (:243), persistence boundary Plan/Tasks (:254-257), `buildMemoryLines` 8-section assembly (:236-265), `buildSearchingPastContextSection` (:375-407, gate `tengu_coral_fern`), `loadMemoryPrompt` (:419-507; hooked into system prompt at `src/constants/prompts.ts:495`, D2, evaluated once per session then cached)
- `src/memdir/memoryTypes.ts` — 4-type taxonomy (user/feedback/project/reference) as XML blocks with `<when_to_save>/<how_to_use>/<examples>` (:113-178); What NOT to save (:183-195, eval case 3: 0/2→3/3); When to access (:216-222, "ignore" anti-pattern from branch-pollution evals #22856, `MEMORY_DRIFT_CAVEAT`); Before recommending from memory (:240-256; eval comments :228-244: H1 0/2→3/3, placement sensitivity (bullet burial 0/3), header phrasing "Before recommending from memory" 3/3 vs "Trusting what you recall" 0/3, H5 0/2→3/3, known gap slash commands 0/3); header :4-7 "NOT derivable from the current project state"
- `src/memdir/findRelevantMemories.ts` — relevance search via `sideQuery` (Sonnet); feeds attachment surfacing
- `src/services/SessionMemory/sessionMemory.ts` — header :1-5 (forked-subagent background notes); gate `tengu_session_memory` (:80-82); `shouldExtractMemory` (:134-181); token-growth mandatory (:165-167); `sequential()` (:272); fork launch `runForkedAgent` (:315-325) with `createMemoryFileCanUseTool(memoryPath)` (:321); `recordExtractionTokenCount` (:344); `manuallyExtractSessionMemory` (/summary, :387)
- `src/services/SessionMemory/sessionMemoryUtils.ts` — `DEFAULT_SESSION_MEMORY_CONFIG`: `minimumMessageTokensToInit: 10000` (:33), `toolCallsBetweenUpdates: 3` (:35), `minimumTokensBetweenUpdate: 5000`; `hasMetInitializationThreshold` (:173), `hasMetUpdateThreshold` (:184-189); same token measure as autocompact (:20-22)
- `src/services/SessionMemory/prompts.ts` — 10-section template (:11-41), `MAX_SECTION_LENGTH=2000` (:8), `MAX_TOTAL_SESSION_MEMORY_TOKENS=12000` (:9), no-reference-to-note-taking rule (:44-46), "Always update Current State … continuity after compaction" (:69), custom template/prompt at `~/.claude/session-memory/config/{template.md,prompt.md}` (:86-120)
- `src/services/compact/compact.ts` — boundary + summary message creation (:598-624), post-compact size accounting (:637-642), prior-summary detection (:798), KAIROS extra segment write (:713-717)
- `src/services/compact/autoCompact.ts` — `MAX_OUTPUT_TOKENS_FOR_SUMMARY=20_000` (:30), `AUTOCOMPACT_BUFFER_TOKENS=13_000` (:62), `WARNING_THRESHOLD_BUFFER_TOKENS=20_000` (:63), `getAutoCompactThreshold` (:72) = window − 20K − 13K (≈167K on 200K model)
- `src/services/compact/sessionMemoryCompact.ts` — "EXPERIMENT" (:1-3); `createCompactionResultFromSessionMemory` (:437-482) makes `createUserMessage({content, isCompactSummary: true …})`; truncation + "full session memory can be viewed at: {memoryPath}" (:461-474); `waitForSessionMemoryExtraction` (:527); keep recent min 10K / max 40K tokens
- `src/services/compact/prompt.ts` — `getCompactUserSummaryMessage` (:337-), transcriptPath pointer sentence (:349-351)
- `src/utils/permissions/filesystem.ts:259-270` — `getSessionMemoryDir()/getSessionMemoryPath()` → `{projectDir}/{sessionId}/session-memory/summary.md`
- `src/utils/sessionStoragePortable.ts:311-331` — `getProjectDir` slug (non-alphanumeric → hyphens) under `~/.claude/projects/`
- `src/query.ts:992` — `void executePostSamplingHooks(...)` fire-and-forget after every API response
- `src/utils/tokens.ts:226` — `tokenCountWithEstimation` (last API-reported usage anchor + estimation of newer messages)
- `src/utils/messages.ts` — compact boundary `subtype: 'compact_boundary'` `type: 'system'` (:4537-4550, not sent to API), `isCompactBoundaryMessage` (:4608), `case 'relevant_memories'` → `wrapMessagesInSystemReminder` (:3708-3712)
- `src/services/extractMemories/extractMemories.ts` — background auto-memory extraction: stop-hook timing (:5-7), gate `tengu_passport_quail` + conditions (:531-552), throttle `tengu_bramble_lintel` default 1 (:374-386), mutual-exclusion cursor vs main-agent writes (:345-360), stash-latest-context (:554-564), fork spec: memory-dir-only write, `maxTurns: 5`, manifest pre-injection, 60s drain (:415-427, 579-586, 611-615)
- `src/utils/attachments.ts` — relevant-memory surfacing (`.slice(0, 5)`, `readMemoriesForSurfacing`, returns `relevant_memories` attachment :2234-2242; telemetry :2412)
- Deliverables: `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html`, `/Users/seobi/jinsup_space/CC/md_group/클로드코드-메모리-시스템.md`, `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html`

# Workflow
_What bash commands are usually run and in what order? How to interpret their output if not obvious?_

- Locate then read: `grep -n "<symbol>" <file> | head`, `grep -rn "<symbol>" src/ -l`, `sed -n 'N,Mp' <file>`, then Read(offset/limit) on the hit range — always verify before claiming, cite file:line.
- Disk reality checks: `ls ~/.claude/projects/<slug>/`, `find ~/.claude/projects -maxdepth 3 -type d -name 'session-memory'` — zero hits means the `tengu_session_memory` gate is OFF for this account.
- After each visual-explainer Write: `open <file>.html` to preview in browser.

# Errors & Corrections
_Errors encountered and how they were fixed. What did the user correct? What approaches failed and should not be tried again?_

- `grep "export function getProjectDir"` in `src/utils/sessionStorage.ts` returned nothing → widened to repo-wide grep; real definition in `src/utils/sessionStoragePortable.ts:329` (also `cachePaths.ts:21`).
- Coined term "4중 게이트" confused the user ("4중게이트가 뭔지모르겠어?") → clarified it is not official vocabulary, just 4 sequential if-checks; re-explained with airport-checkpoint analogy.
- User's summary graded with two corrections: auto memory has 4 **types** (not 4 sections; 10 sections belong to session memory; the 8 sections are prompt guidance), and compaction fires **automatically** at threshold (/compact is only the manual option).
- User's paraphrase "대화 컨텍스트로 모를만한 일을 적는다" reversed → correct framing is "대화에만 존재하는 일(재파생 불가능한 것)"을 적는다 (2×2 matrix).
- User reframed the question twice ("내요지는 저정도만 기록하냐라긴보다 왜 저걸 기록하냐" / "왜 4타입이면 충분하달까") — answer rationale (WHO/HOW/WHY/WHERE mapping, WHAT delegated to tools), not volume.
- User interrupted a bare `/visual-explainer` invocation ([Request interrupted by user]) to ask follow-ups first; the visual build resumed later with explicit args.

# Codebase and System Documentation
_What are the important system components? How do they work/fit together?_

Three memory layers in Claude Code:
1. **Auto memory** (`src/memdir/`) — project-persistent wiki: `MEMORY.md` index (always in system prompt, D2 dynamic section, once-per-session evaluation → prompt-cache hit) + topic files read on demand. 4 types = user/feedback/project/reference; forbidden = anything derivable (grep/git/CLAUDE.md). Two update paths: inline by main agent (no trigger, model judgment; explicit request = immediate) and background `extractMemories` fork (stop hook at end of complete query loop, gate `tengu_passport_quail` OFF, mutual-exclusion cursor).
2. **Session memory** (`src/services/SessionMemory/`) — per-session `summary.md`, written by a forked clone of the main conversation (post-sampling hook after every API response, `void` fire-and-forget). Gates in order: main REPL thread → `tengu_session_memory` (OFF on this machine — zero `session-memory/` dirs on disk) → 10K init → +5K growth (mandatory floor, not a grid) AND (≥3 tool calls OR no-tool quiet turn). Injected into the LLM **only at compaction** as a user message flagged `isCompactSummary: true` (EXPERIMENT path that replaces the ad-hoc LLM summary).
3. **Compaction** (`src/services/compact/`) — auto at threshold (window − 20K − 13K) or manual `/compact`; produces a boundary marker (`type: 'system'`, harness-internal, not sent to API) + summary user message; both appended to the append-only `~/.claude/projects/<slug>/<sessionId>.jsonl` transcript; summary carries a transcriptPath pointer for lossless recovery.

Injection channels: MEMORY.md → system prompt (always); summary.md → user message (compaction moment only); relevant memories (`findRelevantMemories`) → attachment → `<system-reminder>` (situational, per turn).

# Learnings
_What has worked well? What has not? What to avoid? Do not duplicate items from other sections_

- User prefers analogy + table explanations and quick one-line confirmations; grading their paraphrases (✅/✏️) works well.
- Prompt engineering in this codebase is measurement-driven: hypotheses (H1–H6) with eval scores in source comments; section placement and header phrasing are load-bearing.
- Live Claude Code (this session's own system prompt) is newer than the mirror: `[[name]]` wiki-link/red-link guidance exists live but not in `src/memdir/` — version-difference worth recording.
- Design patterns worth porting: memory-management delegated to the model with guardrail prompts; distributed savings against the compaction cliff; fork-subagent + plain-markdown filesystem memory; lifetime-matched injection channels.

# Key results
_If the user asked a specific output such as an answer to a question, a table, or other document, repeat the exact result here_

Corrected 3-layer summary (교정본) given to the user:

> 메모리는 3층이다. **자동 메모리**는 4개 타입(user/feedback/project/reference)으로 분류해 주제별 파일 + 인덱스로 저장하는 **프로젝트 전용** 영속 기억이고, 매 질문마다 시스템 프롬프트로 입력된다. **세션 메모리**는 해당 세션만을 위한 10섹션 노트로, 메인 히스토리를 복사받은 서브에이전트가 백그라운드에서 작성하는 **실험 기능**이며, 컴팩션 순간에만 입력된다. **컴팩션 요약**은 컨텍스트가 임계값에 닿으면 자동으로(또는 `/compact`로 수동) 만들어져 옛 대화를 대체하는 user 메시지다 — 원본은 트랜스크립트에 남는다.

Three memories, three channels:

| 기억 | LLM 인풋 채널 | 타이밍 |
|---|---|---|
| MEMORY.md (자동 메모리) | 시스템 프롬프트 (동적 영역 D2) | 세션 시작부터 항상 |
| summary.md (세션 메모리) | user 메시지 (`isCompactSummary`) | 컴팩션 순간에만 |
| 관련 메모리 서페이싱 | attachment → `<system-reminder>` | 매 턴 상황별 |

Final-question answer (in delivery): yes — frontmatter-driven situational injection is real; `findRelevantMemories` → top-5 attachment → `wrapMessagesInSystemReminder` (`messages.ts:3708`).

# Worklog
_Step by step, what was attempted, done? Very terse summary for each step_

1. ls/find project root; launched 2 parallel Explore agents (docs catalog / src structure); synthesized: src = 1,902-file source mirror; memory docs gap identified.
2. Defined auto memory vs session memory from memdir.ts + SessionMemory sources.
3. Located session memory path (`filesystem.ts:259-270`); slug logic; disk check → no session-memory dirs (gate OFF).
4. Explained MEMORY.md/summary.md coexistence; session-memory triggers (10K/+5K/3 tools); compaction auto vs manual, threshold formula.
5. Compaction storage: boundary marker + isCompactSummary user message → .jsonl append-only; transcriptPath pointer.
6. Built 클로드코드-메모리-시스템.html (visual-explainer), opened.
7. Traced trigger site query.ts:992 (post-sampling, void); turn-level simulation; explained "4중 게이트" as 4 if-checks.
8. Fork anatomy: harness decides, forked clone writes; createCacheSafeParams; cache-hit economics; permission lock; /summary manual path.
9. Timing recap; 10K measurement via tokenCountWithEstimation; 10 sections + injection channels; 5K-floor nuances; isCompactSummary consumers; API array composition; boundary marker not sent; write/read timing separation; compaction-moment walkthrough.
10. Status: session memory = experiment (rollout pipeline); auto memory = the operational one; portable patterns.
11. Rewrote HTML to 9 sections; created md_group/클로드코드-메모리-시스템.md.
12. Auto-memory prompt 8-section assembly + eval effects (memoryTypes.ts comments); graded user's summary (2 fixes); added §2.5 + sources + changelog to md doc (3 Edits).
13. Auto-memory update timing: inline (no trigger) + extractMemories background (stop hook, gates, mutual exclusion).
14. Narrow-scope rationale; 2×2 matrix correction; WHO/HOW/WHY/WHERE ↔ 4 types; sufficiency argument; built 자동메모리-딥다이브.html.
15. Wiki framing confirmed (semantic organization, red links live-only); investigating frontmatter surfacing → confirmed system-reminder channel; rewriting 자동메모리-딥다이브.html (in progress at cutoff).
````

## 단계 2: 메인 컴팩션 요약 (getCompactPrompt 적용 결과)

<analysis>
Let me work through the conversation chronologically.

**Phase 1 — Project-wide exploration (user message 1):** The user asked for full comprehension of the project ("프로젝트 코드랑 내용 전체 파악 해 자 시작!"). I ran `ls`/`find` on `/Users/seobi/jinsup_space/CC`, then launched two parallel Explore subagents. Results: (a) `src/` is an original-TypeScript source mirror of Claude Code — 1,902 files, ~512,670 lines, no decompilation traces (`bun:bundle` feature flags, Biome comments, production-grade comments); memory code lives in three axes: `memdir/` (auto memory, 8 files), `services/SessionMemory/` (3 files), `services/compact/` (8 files incl. `sessionMemoryCompact.ts` 630 lines). (b) `md_group/` holds ~135 analysis docs (all corrected per `md_group-교정-변경내역.md`), but only ONE dedicated memory doc (`system_info/prompts/09-loadMemoryPrompt-analysis.md`, auto memory only) — SessionMemory, sessionMemoryCompact, findRelevantMemories were an identified documentation gap.

**Phase 2 — Definitions and storage (messages 2–5):** "자동 메모리, 세션 메모리 가 뭐야?" → read `memdir.ts`, `SessionMemory/prompts.ts`, `sessionMemory.ts`. Auto memory = project-persistent (`~/.claude/projects/<slug>/memory/`, MEMORY.md index + topic files, written inline by the main agent, 4 types, 200-line/25KB cap). Session memory = per-conversation notes written by a forked background subagent, fixed 10-section template, 2,000/section and 12,000-token caps, `tengu_session_memory` gate, purpose = continuity after compaction. "세션 메모리는 어디에 저장되는데?" → `getSessionMemoryDir/Path` in `src/utils/permissions/filesystem.ts:259-270` → `{projectDir}/{sessionId}/session-memory/summary.md`; slug via `sessionStoragePortable.ts:311-331` (initial grep in sessionStorage.ts failed — wrong file). Disk check: zero `session-memory/` dirs on this machine → gate OFF. "메모리.md랑 summary.md랑 같이 있는거구나" → confirmed coexistence at different levels; found the EXPERIMENT reuse of summary.md at compaction; extracted thresholds (init 10K, +5K growth, 3 tool calls); explained compaction auto vs `/compact`, threshold = window − 20K − 13K. "컴팩션하면 그건 어디에 저장되는데?" → no separate file: boundary marker + `isCompactSummary` user message inserted into conversation and appended to the append-only `.jsonl` transcript, with transcriptPath pointer for recovery.

**Phase 3 — First deliverable (message 6):** `/visual-explainer` → wrote and opened `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html` (7 sections, "기억의 지층" dark-archive concept).

**Phase 4 — Trigger mechanics (messages 7–18):** A long clarification loop driven by short confused user questions. Located the exact check site `src/query.ts:992` (`void executePostSamplingHooks(...)` — after every API response, fire-and-forget). Explained the "4중 게이트" (my own coinage, which confused the user — corrected): ① main REPL thread ② `tengu_session_memory` ③ 10K init ④ +5K growth AND (≥3 tools OR quiet no-tool turn). Fork anatomy: harness decides via `shouldExtractMemory()`, a forked clone writes (`runForkedAgent`, `createCacheSafeParams` passes identical systemPrompt + full messages) — prompt-cache hit makes it nearly free; permission-locked to summary.md only; `/summary` manual path exists. Token measurement: `tokenCountWithEstimation` (tokens.ts:226) — same measure as autocompact. 10 sections enumerated; injection clarified: session memory is NOT a system-reminder — it sleeps on disk and enters exactly once, at compaction, as a user message (`sessionMemoryCompact.ts:437-482`), after `waitForSessionMemoryExtraction` (:527). The 5K is a floor, not a grid (10K→18K→23K…, `recordExtractionTokenCount` :344, `hasMetUpdateThreshold` sessionMemoryUtils.ts:184-189). `isCompactSummary` = boolean tag distinguishing harness-inserted summary from real user input; consumers: Message.tsx:159, MessageSelector.tsx:780, sessionStorage.ts:1752, compact.ts:798, useAwaySummary.ts:19. API array after compaction: summary user message + preserved recent + hooks/attachments + the real question (separate elements); boundary marker is `type: 'system'` and never sent to the API (messages.ts:4537-4550). Write/read timing fully separated (insurance metaphor); "컴팩션 순간" concretized as the "Compacting conversation..." pause.

**Phase 5 — Status assessment (messages 19–21):** "뭐야 그냥 실험기능 정도구나?" → yes for session memory (`tengu_session_memory` default OFF; SM-compaction is EXPERIMENT-on-experiment), but auto memory + compaction + transcript are 정식. Experiment = rollout-pipeline stage (GrowthBook `tengu_*` flags + telemetry). "중요한게 … 메인에이전트가 만드는 메모리곘네?" → practically yes; they solve different problems (cross-session amnesia vs post-compaction amnesia); gave 3 portable design patterns.

**Phase 6 — Channels + second deliverable (messages 21–22):** "자동메모리가 적힌건 항상 질문할때마다 인풋이되게네?" → yes: MEMORY.md rides in the system prompt every request; 2-tier structure (index always, topic bodies on demand via Read); once-per-session evaluation → prompt-cache economics; new memories appear next session. "이 내용까지 반영해서 아까 만든 HTML 업데이트해줘" → rewrote the HTML to 9 sections and created `md_group/클로드코드-메모리-시스템.md` (10 chapters).

**Phase 7 — Auto-memory deep dive (messages 23–32):** "자동메모리 섹션에대해 잘 설명하고 그 각 섹션의 효과까지좀" → read `memoryTypes.ts` in full + `memdir.ts` ranges: the auto-memory prompt is an 8-section assembly (`buildMemoryLines`, memdir.ts:236-265) whose per-section effects are recorded as eval scores in source comments (H2 0/2→3/3; H6 ignore anti-pattern #22856; H1 0/2→3/3 with placement sensitivity — bullet burial 0/3 — and header-phrasing experiment 3/3 vs 0/3; H5 0/2→3/3; known gap slash commands 0/3); plus gated ⑨ Searching past context (`tengu_coral_fern`). User's check-my-understanding paragraph graded: two fixes (4 types not sections; compaction primarily automatic) + 교정본 delivered. User approved "응" → 3 Edits added §2.5, sources, changelog to the md doc. "auto memory 가 갱신되는 타이밍이언제야" → two paths: inline (no trigger — model judgment; explicit request immediate, memdir.ts:243) and background `extractMemories.ts` (stop hook at end of complete query loop, gate `tengu_passport_quail` OFF, throttle `tengu_bramble_lintel`, mutual-exclusion cursor :345-360, fork spec maxTurns:5/manifest/60s drain). "저정도만 기록하는데.. 의미가 잇는건가?" → narrow scope IS the design: forbidden items all have authoritative sources; 4 types = only non-derivable info; noise harm measured; economy of the always-riding index; real leverage example ("레포 2-머신 공유 · 경로는 ~ 중립 표기"). User interrupted a bare `/visual-explainer`, then corrected my framing twice: not "things unknowable from the conversation" but "things existing ONLY in the conversation" (2×2 matrix), and the real question was WHY these four ("왜 저걸 기록하냐" / "왜 4타입이면 충분하달까") → purpose sentence memdir.ts:241 maps 1:1 to WHO(user)/HOW(feedback)/WHY(project)/WHERE(reference); WHAT is delegated to tools (memoryTypes.ts:4-7); sufficiency evidence: distinct per-type how_to_use + Anthropic extends axes (TEAMMEM scope, KAIROS, session memory) not types; honest limit: product bet. `/visual-explainer 위 내용들 세세히 적어! 빠짐없이!` → built `자동메모리-딥다이브.html` (7 sections incl. eval bar charts).

**Phase 8 — Wiki framing and current work (messages 33–34):** "마치 LLM 위키같은건가" → confirmed: 1:1 wiki mapping (index=main page, topic files=articles, frontmatter=infobox, semantic-not-chronological organization memdir.ts:214/teamMemPrompts.ts:38,55, update-in-place); discovered a live-vs-mirror difference — the live system prompt has `[[name]]` wiki-links incl. red links to not-yet-existing memories, absent from mirror source (grep '\[\[' → no hits); genre table (wiki/worklog/diary/transcript). Final question: "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??" → I read `findRelevantMemories.ts` (sideQuery, Sonnet), grepped callers → `src/utils/attachments.ts` (top-5 `.slice(0, 5)`, `readMemoriesForSurfacing`, returns `{ type: 'relevant_memories', memories }`; telemetry `tengu_memdir_prefetch_collected` :2412), and `src/utils/messages.ts:3708` — `case 'relevant_memories'` → `wrapMessagesInSystemReminder(...)`. The hypothesis is CONFIRMED. I then issued a Write to rewrite `자동메모리-딥다이브.html` with this finding — that Write is the very last action before this summary request; the confirmation answer has not yet been delivered to the user in prose.

Double-checking completeness: all user messages captured (34 non-tool-result messages incl. two slash commands and one interruption); all key constants (10K/5K/3, 2000/12000, 200/25KB, 20K/13K), gates (tengu_session_memory, tengu_passport_quail, tengu_bramble_lintel, tengu_coral_fern), file:line citations, error/correction moments, and the three deliverable files with their states are reflected below.
</analysis>

<summary>
1. Primary Request and Intent:
   The user's initial request was full comprehension of the `/Users/seobi/jinsup_space/CC` workspace ("프로젝트 코드랑 내용 전체 파악 해 자 시작!") — a research repo holding an original-TypeScript source mirror of Claude Code (`src/`) plus ~135 analysis markdown docs (`md_group/`). The conversation then became an extended, question-driven deep dive into Claude Code's memory architecture — auto memory, session memory, and compaction — with the standing expectation (project convention) that every claim be verified against local source with file:line citations. Explicit intents along the way:
   - Understand definitions, storage locations, trigger timing, authorship (main vs subagent), injection channels, and experimental status of each memory layer, via many short clarifying questions.
   - Produce visual deliverables: `/visual-explainer` HTML of the memory conversation (`클로드코드-메모리-시스템.html`), later "이 내용까지 반영해서 아까 만든 HTML 업데이트해줘"; a second deep-dive HTML via "/visual-explainer 위 내용들 세세히 적어! 빠짐없이!" (`자동메모리-딥다이브.html`).
   - Maintain an LLM-readable canonical doc `md_group/클로드코드-메모리-시스템.md` (user approved adding §2.5 with "응").
   - Have their own understanding graded ("이거 설명맞는지도 알려주라") and their framing questions answered precisely ("왜 저걸 기록하냐", "왜 4타입이면 충분하달까").
   - Final (current) intent: verify the hypothesis that auto-memory topic files are surfaced situationally via frontmatter into system-reminders ("위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??").

2. Key Technical Concepts:
   - Three memory layers: auto memory (`src/memdir/`, project-persistent), session memory (`src/services/SessionMemory/`, per-session), compaction (`src/services/compact/`)
   - Auto memory: MEMORY.md index (200 lines / 25KB cap) + topic files with frontmatter (name/description/type); 4-type taxonomy user/feedback/project/reference; "NOT derivable from project state" scoping rule; wiki architecture (semantic organization, update-in-place, `[[name]]` red links in live version only)
   - Session memory: forked-subagent background extraction; 10-section template (Session Title ~ Worklog); MAX_SECTION_LENGTH 2000 / MAX_TOTAL 12000 tokens; gates — main REPL thread → `tengu_session_memory` → 10K init (`minimumMessageTokensToInit`) → +5K growth (`minimumTokensBetweenUpdate`, mandatory floor) AND (≥3 tool calls OR no-tool quiet turn)
   - Post-sampling hooks (`query.ts:992`, `void` fire-and-forget, per API response not per turn); stop hooks (`extractMemories`)
   - Fork mechanics: `runForkedAgent` + `createCacheSafeParams` (identical system prompt + full message copy → prompt-cache hit ≈ free); permission lock `createMemoryFileCanUseTool`
   - Compaction: autoCompact threshold = context window − MAX_OUTPUT_TOKENS_FOR_SUMMARY(20,000) − AUTOCOMPACT_BUFFER_TOKENS(13,000) ≈ 167K on 200K; manual `/compact`; 5-stage preprocessing (applyToolResultBudget → snipCompact → microcompact → contextCollapse → autocompact)
   - `isCompactSummary` flag (harness-internal tag on the summary user message); compact boundary marker (`type: 'system'`, `subtype: 'compact_boundary'`, NOT sent to API); append-only `.jsonl` transcript + transcriptPath recovery pointer
   - `tokenCountWithEstimation` (API-reported usage anchor + estimation; shared with autocompact)
   - sessionMemoryCompact EXPERIMENT: reuse summary.md as the compaction summary; `waitForSessionMemoryExtraction`
   - Feature gates / GrowthBook: `tengu_session_memory`, `tengu_passport_quail`, `tengu_bramble_lintel`, `tengu_coral_fern`; experiment = rollout-pipeline stage
   - Eval-driven prompt engineering (H1–H6 scores in source comments; placement & header-phrasing sensitivity)
   - Injection channels: system prompt (D2) / user message at compaction / attachment → `<system-reminder>` (`findRelevantMemories` → `relevant_memories` attachment → `wrapMessagesInSystemReminder`)

3. Files and Code Sections:
   - `src/utils/permissions/filesystem.ts:259-270` — session memory storage path (answered "어디에 저장되는데?"):
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
   - `src/query.ts:992` — the exact trigger check site (answered "언제 트리거되는거야"):
     ```typescript
     if (assistantMessages.length > 0) {
       void executePostSamplingHooks(...)   // fire-and-forget, per API response
     }
     ```
   - `src/utils/forkedAgent.ts:131-141` — fork inherits main's full context (answered "메인에이전트에서 만드는거야?"):
     ```typescript
     return {
       systemPrompt: context.systemPrompt,      // same system prompt as main
       forkContextMessages: context.messages,   // full copy of main conversation
       ...
     }
     ```
   - `src/services/compact/sessionMemoryCompact.ts:437-482` — injection form (answered "시스템리마인더로 들어가나?" — no, user message):
     ```typescript
     const summaryMessages = [
       createUserMessage({
         content: summaryContent,
         isCompactSummary: true,
         ...
     ```
     Plus `:1-3` EXPERIMENT header, `:527` `waitForSessionMemoryExtraction`, `:461-474` truncation + "full session memory can be viewed at: {memoryPath}" pointer.
   - `src/utils/messages.ts:3708-3712` — final-question evidence (relevant memories → system-reminder):
     ```typescript
     case 'relevant_memories': {
       return wrapMessagesInSystemReminder(
         attachment.memories.map(m => { ...
     ```
     Also `:4537-4550` boundary marker (`type: 'system'`, not sent to API), `:4608` `isCompactBoundaryMessage`.
   - `src/services/SessionMemory/sessionMemory.ts` — header :1-5 (background forked notes), gate :80-82, `shouldExtractMemory` :134-181 (token growth always mandatory :165-167), `sequential()` :272, fork launch :315-325 (`createMemoryFileCanUseTool` :321), `recordExtractionTokenCount` :344, `manuallyExtractSessionMemory` (/summary) :387
   - `src/services/SessionMemory/sessionMemoryUtils.ts` — `DEFAULT_SESSION_MEMORY_CONFIG` (`minimumMessageTokensToInit: 10000` :33, `toolCallsBetweenUpdates: 3` :35, `minimumTokensBetweenUpdate: 5000`), `hasMetInitializationThreshold` :173, `hasMetUpdateThreshold` :184-189, same-token-measure-as-autocompact comment :20-22
   - `src/services/SessionMemory/prompts.ts` — 10-section template :11-41, caps :8-9, "never reference note-taking" :44-46, "Always update Current State … continuity after compaction" :69, custom config `~/.claude/session-memory/config/{template.md,prompt.md}` :86-120
   - `src/services/compact/autoCompact.ts` — threshold constants/formula (:30, :62, :63, :72):
     ```typescript
     getEffectiveContextWindowSize(model) = getContextWindowForModel(model) - MAX_OUTPUT_TOKENS_FOR_SUMMARY
     getAutoCompactThreshold(model) = getEffectiveContextWindowSize(model) - AUTOCOMPACT_BUFFER_TOKENS
     ```
   - `src/services/compact/compact.ts` — boundary+summary creation :598-624, post-compact accounting :637-642 (boundaryMarker + summaryMessages + postCompactFileAttachments + hookMessages), prior-summary detection :798, KAIROS side-write :713-717
   - `src/services/compact/prompt.ts` — `getCompactUserSummaryMessage` :337-, transcriptPath sentence :349-351 ("read the full transcript at: {transcriptPath}")
   - `src/memdir/memdir.ts` — caps :34-38, `truncateEntrypointContent` :57, `DIR_EXISTS_GUIDANCE` :111-115 ("Claude was burning turns on ls/mkdir -p"), index rules :218-234 (≤150 chars/line, semantic organization :214, dedup :233), purpose sentence :241, explicit-save :243, Plan/Tasks boundary :254-257, `buildMemoryLines` :236-265 (8-section assembly), `buildSearchingPastContextSection` :375-407 (`tengu_coral_fern`), `loadMemoryPrompt` :419-507 (→ `src/constants/prompts.ts:495`, D2, once per session)
   - `src/memdir/memoryTypes.ts` — read in full: taxonomy header :4-7 ("NOT derivable"), 4 types :113-178 (XML blocks; feedback "Record from failure AND success"; body_structure Why:/How to apply:; project relative→absolute dates), What NOT to save :183-195 (eval case 3: 0/2→3/3), When to access :216-222 (ignore anti-pattern, branch-pollution evals #22856; MEMORY_DRIFT_CAVEAT), Before recommending from memory :240-256 with eval comments :228-244 (H1 0/2→3/3; bullet burial 0/3; header phrasing 3/3 vs 0/3; H5 0/2→3/3; known gap slash commands 0/3)
   - `src/services/extractMemories/extractMemories.ts` — background auto-memory path: stop-hook timing :5-7 ("runs once at the end of each complete query loop … no tool calls … via handleStopHooks"), conditions :531-552, throttle :374-386 (`tengu_bramble_lintel`, default 1), mutual-exclusion cursor :345-360 ("skipping — conversation already wrote to memory files"), stash :554-564, fork spec :415-427/:579-586/:611-615 (memory-dir-only write, maxTurns: 5, manifest pre-injection, 60s drain)
   - `src/memdir/findRelevantMemories.ts` — read in full: relevance search via `sideQuery` (Sonnet), jsonParse
   - `src/utils/attachments.ts` — surfacing pipeline: `.slice(0, 5)` → `readMemoriesForSurfacing(selected, signal)` → `return [{ type: 'relevant_memories' as const, memories }]` (:2234-2242); telemetry `tengu_memdir_prefetch_collected` :2412; `RELEVANT_MEMORIES_CONFIG` nearby
   - `src/utils/sessionStoragePortable.ts:311-331` — `getProjectDir` slug (non-alphanumeric → hyphens)
   - `src/utils/tokens.ts:226` — `tokenCountWithEstimation` (usage anchor + estimation)
   - Deliverables created/edited:
     - `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html` — created (7 sections), then fully rewritten (9 sections) on user request; opened in browser both times
     - `/Users/seobi/jinsup_space/CC/md_group/클로드코드-메모리-시스템.md` — created (10 chapters), then 3 Edits (new §2.5 "시스템 프롬프트 지침 — 8섹션 조립과 각 섹션의 '측정된' 효과", §10 source-table update, 변경이력 entry)
     - `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` — created (7 sections: 2×2 matrix, WHO/HOW/WHY/WHERE, 4-type sufficiency, 2 update paths, 8-section stack, eval bar charts, narrow-scope economics); a rewrite Write (adding the relevant_memories/system-reminder finding) was issued as the very last action and its completion is unconfirmed

4. Errors and fixes:
   - `grep "export function getProjectDir"` on `src/utils/sessionStorage.ts` returned nothing:
     - Fixed by widening to a repo-wide grep — actual definition at `src/utils/sessionStoragePortable.ts:329` (plus `cachePaths.ts:21`).
   - Coined term "4중 게이트" confused the user ("4중게이트가 뭔지모르겠어?"):
     - Fixed by admitting it was my own coinage, re-explaining as 4 plain sequential if-checks with an airport-checkpoint analogy.
   - User's understanding contained two inaccuracies (in their check-my-understanding message):
     - Fixed: auto memory has 4 **types** (user/feedback/project/reference), not "4 sections" — 10 sections belong to session memory, and the 8 sections are the system-prompt guidance; compaction fires **automatically** at threshold, `/compact` is only the manual option. Delivered a corrected 교정본 paragraph.
   - My framing "대화 컨텍스트로 모를만한 일" was the wrong direction (user echoed it back):
     - Fixed: it is "things that exist ONLY in the conversation" (learned in conversation × not re-derivable — 2×2 matrix).
   - User feedback on question intent (important): they interrupted a `/visual-explainer` run ([Request interrupted by user]) and twice reframed — "내요지는 저정도만 기록하냐라긴보다 왜 저걸 기록하냐랄까" and "그리고 왜 4타입이면 충분하달까" — demanding the rationale (purpose-sentence mapping, sufficiency argument) rather than a volume defense. Answered with WHO/HOW/WHY/WHERE ↔ 4-type 1:1 mapping (memdir.ts:241), WHAT delegated to tools (memoryTypes.ts:4-7), axis-not-type extension evidence (TEAMMEM/KAIROS/session memory), and an honest "product bet" caveat.
   - Session memory never observable on this machine: explained (not a bug) — gate `tengu_session_memory` default OFF; verified empirically (zero `session-memory/` dirs under `~/.claude/projects/`).

5. Problem Solving:
   Mapped Claude Code's complete memory architecture from source: three layers with different lifetimes, authors, and injection channels. Solved: session memory storage path and its directory-level lifetime separation from auto memory; exact trigger site and gate chain; fork-clone authorship with cache economics; 5K-floor (not grid) update semantics; compaction storage (in-conversation + append-only transcript, no separate file); boundary-marker vs API-visible messages; experimental-status classification; auto-memory 8-section prompt anatomy with eval-measured effects; two auto-memory update paths with mutual exclusion; narrow-scope rationale and 4-type sufficiency argument; wiki architecture confirmation incl. live-vs-mirror `[[name]]` red-link difference. Ongoing at cutoff: confirming (already verified in source, not yet delivered as an answer) that frontmatter-based relevant-memory surfacing enters via `<system-reminder>`, and rewriting `자동메모리-딥다이브.html` to include it.

6. All user messages:
   - "프로젝트 코드랑 내용 전체 파악 해 자 시작!"
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
   - "자동메모리, 세션메모리, 컴팩션으로 만드는 메모리 이렇게 3개의 종류의 메모리가 있다. 자동메모리는 4개의 섹션으로 만드는 프로젝트전용이고 세션메모리는 해당 세션만을 위한 메모리다. 세션 메모리는 메인 에이전트 히스토리로 작성되나 작성은 서브에이전트가 진행하며 실험기능에 속하는 편이다. 컴팩션은 /compact를 사용했을때 그때 완성되는 요약 내용이다. 이거 설명맞는지도 알려주라"
   - "이 내용을 md_group/클로드코드-메모리-시스템.md의 §2(자동 메모리)에 추가해 둘까요? <- 응"
   - "auto memory 가 갱신되는 타이밍이언제야"
   - "자동메모리가 저정도만 기록하는데.. 의미가 잇는건가? 그 이유는?"
   - "/visual-explainer" (slash command, no args — interrupted: [Request interrupted by user])
   - "그니까 너의말은 대화 컨텍스트로 모를만한 일을 적ㅇ는다는건가"
   - "내요지는 저정도만 기록하냐라긴보다 왜 저걸 기록하냐랄까"
   - "그리고 왜 4타입이면 충분하달까"
   - "/visual-explainer 위 내용들 세세히 적어! 빠짐없이!"
   - "근데 실제 파일보니까 MEMORY.md 은인덱싱처럼 되어있고 나머지 문서로 나뉘어져 상세내용처럼되어있어 마치 LLM 위키같은건가"
   - "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??"

7. Pending Tasks:
   - Finish the in-progress rewrite of `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` (adding the frontmatter → `relevant_memories` attachment → system-reminder finding), open it, and deliver the prose answer to the user's last question with file:line evidence.
   - (Offered, not yet confirmed by user — do not start without confirmation): moving the HTML into `html_group_v2/` convention; reflecting the deep-dive content (2×2 matrix, WHO/HOW/WHY/WHERE, sufficiency argument) into `md_group/클로드코드-메모리-시스템.md` §2.

8. Current Work:
   Verifying the user's final hypothesis: "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??". Sequence completed so far: Read `src/memdir/findRelevantMemories.ts` in full (relevance search via `sideQuery` with the default Sonnet model); grepped callers outside memdir → `src/utils/attachments.ts`, `collapseReadSearch.ts`, `transcriptSearch.ts`, `claudemd.ts`; read the attachments.ts surfacing code — top-5 selection then:
   ```typescript
   .slice(0, 5)
   const memories = await readMemoriesForSurfacing(selected, signal)
   ...
   return [{ type: 'relevant_memories' as const, memories }]
   ```
   and confirmed the render path at `src/utils/messages.ts:3708`:
   ```typescript
   case 'relevant_memories': {
     return wrapMessagesInSystemReminder(
       attachment.memories.map(m => { ...
   ```
   — i.e. the hypothesis is CONFIRMED: relevant memories are surfaced through the attachment system wrapped in `<system-reminder>` (telemetry `tengu_memdir_prefetch_collected`, `attachments.ts:2412`). The very last action taken was a Write call rewriting `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` to incorporate this finding; the transcript ends mid-write, and no prose answer has been delivered to the user yet.

9. Optional Next Step:
   Complete the Write of `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html`, `open` it, and answer the user's question directly. This is squarely the task in progress: the user asked "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??" and my last words before the tool chain were "좋은 가설입니다 — 마침 아직 안 읽은 `findRelevantMemories.ts`(관련 메모리 검색)가 그 답일 가능성이 높아요. 누가 호출하고 결과가 어디로 들어가는지 확인하겠습니다." The answer to deliver: yes — `findRelevantMemories` (sideQuery/Sonnet) selects candidates, `attachments.ts` surfaces the top 5 as a `relevant_memories` attachment, and `messages.ts:3708` wraps them in `<system-reminder>` via `wrapMessagesInSystemReminder` — with the updated HTML as the visual companion.

</summary>

## 단계 3: 요약 재주입 래퍼 (getCompactUserSummaryMessage 적용 결과)

_컴팩션 후 새 대화의 첫 user 메시지. ${formattedSummary} = 단계 2 출력에서 `<analysis>` 제거 + `<summary>` → `Summary:` 치환. ${transcriptPath}는 치환 변수이므로 원문 그대로 둠._

```
This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
1. Primary Request and Intent:
   The user's initial request was full comprehension of the `/Users/seobi/jinsup_space/CC` workspace ("프로젝트 코드랑 내용 전체 파악 해 자 시작!") — a research repo holding an original-TypeScript source mirror of Claude Code (`src/`) plus ~135 analysis markdown docs (`md_group/`). The conversation then became an extended, question-driven deep dive into Claude Code's memory architecture — auto memory, session memory, and compaction — with the standing expectation (project convention) that every claim be verified against local source with file:line citations. Explicit intents along the way:
   - Understand definitions, storage locations, trigger timing, authorship (main vs subagent), injection channels, and experimental status of each memory layer, via many short clarifying questions.
   - Produce visual deliverables: `/visual-explainer` HTML of the memory conversation (`클로드코드-메모리-시스템.html`), later "이 내용까지 반영해서 아까 만든 HTML 업데이트해줘"; a second deep-dive HTML via "/visual-explainer 위 내용들 세세히 적어! 빠짐없이!" (`자동메모리-딥다이브.html`).
   - Maintain an LLM-readable canonical doc `md_group/클로드코드-메모리-시스템.md` (user approved adding §2.5 with "응").
   - Have their own understanding graded ("이거 설명맞는지도 알려주라") and their framing questions answered precisely ("왜 저걸 기록하냐", "왜 4타입이면 충분하달까").
   - Final (current) intent: verify the hypothesis that auto-memory topic files are surfaced situationally via frontmatter into system-reminders ("위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??").

2. Key Technical Concepts:
   - Three memory layers: auto memory (`src/memdir/`, project-persistent), session memory (`src/services/SessionMemory/`, per-session), compaction (`src/services/compact/`)
   - Auto memory: MEMORY.md index (200 lines / 25KB cap) + topic files with frontmatter (name/description/type); 4-type taxonomy user/feedback/project/reference; "NOT derivable from project state" scoping rule; wiki architecture (semantic organization, update-in-place, `[[name]]` red links in live version only)
   - Session memory: forked-subagent background extraction; 10-section template (Session Title ~ Worklog); MAX_SECTION_LENGTH 2000 / MAX_TOTAL 12000 tokens; gates — main REPL thread → `tengu_session_memory` → 10K init (`minimumMessageTokensToInit`) → +5K growth (`minimumTokensBetweenUpdate`, mandatory floor) AND (≥3 tool calls OR no-tool quiet turn)
   - Post-sampling hooks (`query.ts:992`, `void` fire-and-forget, per API response not per turn); stop hooks (`extractMemories`)
   - Fork mechanics: `runForkedAgent` + `createCacheSafeParams` (identical system prompt + full message copy → prompt-cache hit ≈ free); permission lock `createMemoryFileCanUseTool`
   - Compaction: autoCompact threshold = context window − MAX_OUTPUT_TOKENS_FOR_SUMMARY(20,000) − AUTOCOMPACT_BUFFER_TOKENS(13,000) ≈ 167K on 200K; manual `/compact`; 5-stage preprocessing (applyToolResultBudget → snipCompact → microcompact → contextCollapse → autocompact)
   - `isCompactSummary` flag (harness-internal tag on the summary user message); compact boundary marker (`type: 'system'`, `subtype: 'compact_boundary'`, NOT sent to API); append-only `.jsonl` transcript + transcriptPath recovery pointer
   - `tokenCountWithEstimation` (API-reported usage anchor + estimation; shared with autocompact)
   - sessionMemoryCompact EXPERIMENT: reuse summary.md as the compaction summary; `waitForSessionMemoryExtraction`
   - Feature gates / GrowthBook: `tengu_session_memory`, `tengu_passport_quail`, `tengu_bramble_lintel`, `tengu_coral_fern`; experiment = rollout-pipeline stage
   - Eval-driven prompt engineering (H1–H6 scores in source comments; placement & header-phrasing sensitivity)
   - Injection channels: system prompt (D2) / user message at compaction / attachment → `<system-reminder>` (`findRelevantMemories` → `relevant_memories` attachment → `wrapMessagesInSystemReminder`)

3. Files and Code Sections:
   - `src/utils/permissions/filesystem.ts:259-270` — session memory storage path (answered "어디에 저장되는데?"):
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
   - `src/query.ts:992` — the exact trigger check site (answered "언제 트리거되는거야"):
     ```typescript
     if (assistantMessages.length > 0) {
       void executePostSamplingHooks(...)   // fire-and-forget, per API response
     }
     ```
   - `src/utils/forkedAgent.ts:131-141` — fork inherits main's full context (answered "메인에이전트에서 만드는거야?"):
     ```typescript
     return {
       systemPrompt: context.systemPrompt,      // same system prompt as main
       forkContextMessages: context.messages,   // full copy of main conversation
       ...
     }
     ```
   - `src/services/compact/sessionMemoryCompact.ts:437-482` — injection form (answered "시스템리마인더로 들어가나?" — no, user message):
     ```typescript
     const summaryMessages = [
       createUserMessage({
         content: summaryContent,
         isCompactSummary: true,
         ...
     ```
     Plus `:1-3` EXPERIMENT header, `:527` `waitForSessionMemoryExtraction`, `:461-474` truncation + "full session memory can be viewed at: {memoryPath}" pointer.
   - `src/utils/messages.ts:3708-3712` — final-question evidence (relevant memories → system-reminder):
     ```typescript
     case 'relevant_memories': {
       return wrapMessagesInSystemReminder(
         attachment.memories.map(m => { ...
     ```
     Also `:4537-4550` boundary marker (`type: 'system'`, not sent to API), `:4608` `isCompactBoundaryMessage`.
   - `src/services/SessionMemory/sessionMemory.ts` — header :1-5 (background forked notes), gate :80-82, `shouldExtractMemory` :134-181 (token growth always mandatory :165-167), `sequential()` :272, fork launch :315-325 (`createMemoryFileCanUseTool` :321), `recordExtractionTokenCount` :344, `manuallyExtractSessionMemory` (/summary) :387
   - `src/services/SessionMemory/sessionMemoryUtils.ts` — `DEFAULT_SESSION_MEMORY_CONFIG` (`minimumMessageTokensToInit: 10000` :33, `toolCallsBetweenUpdates: 3` :35, `minimumTokensBetweenUpdate: 5000`), `hasMetInitializationThreshold` :173, `hasMetUpdateThreshold` :184-189, same-token-measure-as-autocompact comment :20-22
   - `src/services/SessionMemory/prompts.ts` — 10-section template :11-41, caps :8-9, "never reference note-taking" :44-46, "Always update Current State … continuity after compaction" :69, custom config `~/.claude/session-memory/config/{template.md,prompt.md}` :86-120
   - `src/services/compact/autoCompact.ts` — threshold constants/formula (:30, :62, :63, :72):
     ```typescript
     getEffectiveContextWindowSize(model) = getContextWindowForModel(model) - MAX_OUTPUT_TOKENS_FOR_SUMMARY
     getAutoCompactThreshold(model) = getEffectiveContextWindowSize(model) - AUTOCOMPACT_BUFFER_TOKENS
     ```
   - `src/services/compact/compact.ts` — boundary+summary creation :598-624, post-compact accounting :637-642 (boundaryMarker + summaryMessages + postCompactFileAttachments + hookMessages), prior-summary detection :798, KAIROS side-write :713-717
   - `src/services/compact/prompt.ts` — `getCompactUserSummaryMessage` :337-, transcriptPath sentence :349-351 ("read the full transcript at: {transcriptPath}")
   - `src/memdir/memdir.ts` — caps :34-38, `truncateEntrypointContent` :57, `DIR_EXISTS_GUIDANCE` :111-115 ("Claude was burning turns on ls/mkdir -p"), index rules :218-234 (≤150 chars/line, semantic organization :214, dedup :233), purpose sentence :241, explicit-save :243, Plan/Tasks boundary :254-257, `buildMemoryLines` :236-265 (8-section assembly), `buildSearchingPastContextSection` :375-407 (`tengu_coral_fern`), `loadMemoryPrompt` :419-507 (→ `src/constants/prompts.ts:495`, D2, once per session)
   - `src/memdir/memoryTypes.ts` — read in full: taxonomy header :4-7 ("NOT derivable"), 4 types :113-178 (XML blocks; feedback "Record from failure AND success"; body_structure Why:/How to apply:; project relative→absolute dates), What NOT to save :183-195 (eval case 3: 0/2→3/3), When to access :216-222 (ignore anti-pattern, branch-pollution evals #22856; MEMORY_DRIFT_CAVEAT), Before recommending from memory :240-256 with eval comments :228-244 (H1 0/2→3/3; bullet burial 0/3; header phrasing 3/3 vs 0/3; H5 0/2→3/3; known gap slash commands 0/3)
   - `src/services/extractMemories/extractMemories.ts` — background auto-memory path: stop-hook timing :5-7 ("runs once at the end of each complete query loop … no tool calls … via handleStopHooks"), conditions :531-552, throttle :374-386 (`tengu_bramble_lintel`, default 1), mutual-exclusion cursor :345-360 ("skipping — conversation already wrote to memory files"), stash :554-564, fork spec :415-427/:579-586/:611-615 (memory-dir-only write, maxTurns: 5, manifest pre-injection, 60s drain)
   - `src/memdir/findRelevantMemories.ts` — read in full: relevance search via `sideQuery` (Sonnet), jsonParse
   - `src/utils/attachments.ts` — surfacing pipeline: `.slice(0, 5)` → `readMemoriesForSurfacing(selected, signal)` → `return [{ type: 'relevant_memories' as const, memories }]` (:2234-2242); telemetry `tengu_memdir_prefetch_collected` :2412; `RELEVANT_MEMORIES_CONFIG` nearby
   - `src/utils/sessionStoragePortable.ts:311-331` — `getProjectDir` slug (non-alphanumeric → hyphens)
   - `src/utils/tokens.ts:226` — `tokenCountWithEstimation` (usage anchor + estimation)
   - Deliverables created/edited:
     - `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html` — created (7 sections), then fully rewritten (9 sections) on user request; opened in browser both times
     - `/Users/seobi/jinsup_space/CC/md_group/클로드코드-메모리-시스템.md` — created (10 chapters), then 3 Edits (new §2.5 "시스템 프롬프트 지침 — 8섹션 조립과 각 섹션의 '측정된' 효과", §10 source-table update, 변경이력 entry)
     - `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` — created (7 sections: 2×2 matrix, WHO/HOW/WHY/WHERE, 4-type sufficiency, 2 update paths, 8-section stack, eval bar charts, narrow-scope economics); a rewrite Write (adding the relevant_memories/system-reminder finding) was issued as the very last action and its completion is unconfirmed

4. Errors and fixes:
   - `grep "export function getProjectDir"` on `src/utils/sessionStorage.ts` returned nothing:
     - Fixed by widening to a repo-wide grep — actual definition at `src/utils/sessionStoragePortable.ts:329` (plus `cachePaths.ts:21`).
   - Coined term "4중 게이트" confused the user ("4중게이트가 뭔지모르겠어?"):
     - Fixed by admitting it was my own coinage, re-explaining as 4 plain sequential if-checks with an airport-checkpoint analogy.
   - User's understanding contained two inaccuracies (in their check-my-understanding message):
     - Fixed: auto memory has 4 **types** (user/feedback/project/reference), not "4 sections" — 10 sections belong to session memory, and the 8 sections are the system-prompt guidance; compaction fires **automatically** at threshold, `/compact` is only the manual option. Delivered a corrected 교정본 paragraph.
   - My framing "대화 컨텍스트로 모를만한 일" was the wrong direction (user echoed it back):
     - Fixed: it is "things that exist ONLY in the conversation" (learned in conversation × not re-derivable — 2×2 matrix).
   - User feedback on question intent (important): they interrupted a `/visual-explainer` run ([Request interrupted by user]) and twice reframed — "내요지는 저정도만 기록하냐라긴보다 왜 저걸 기록하냐랄까" and "그리고 왜 4타입이면 충분하달까" — demanding the rationale (purpose-sentence mapping, sufficiency argument) rather than a volume defense. Answered with WHO/HOW/WHY/WHERE ↔ 4-type 1:1 mapping (memdir.ts:241), WHAT delegated to tools (memoryTypes.ts:4-7), axis-not-type extension evidence (TEAMMEM/KAIROS/session memory), and an honest "product bet" caveat.
   - Session memory never observable on this machine: explained (not a bug) — gate `tengu_session_memory` default OFF; verified empirically (zero `session-memory/` dirs under `~/.claude/projects/`).

5. Problem Solving:
   Mapped Claude Code's complete memory architecture from source: three layers with different lifetimes, authors, and injection channels. Solved: session memory storage path and its directory-level lifetime separation from auto memory; exact trigger site and gate chain; fork-clone authorship with cache economics; 5K-floor (not grid) update semantics; compaction storage (in-conversation + append-only transcript, no separate file); boundary-marker vs API-visible messages; experimental-status classification; auto-memory 8-section prompt anatomy with eval-measured effects; two auto-memory update paths with mutual exclusion; narrow-scope rationale and 4-type sufficiency argument; wiki architecture confirmation incl. live-vs-mirror `[[name]]` red-link difference. Ongoing at cutoff: confirming (already verified in source, not yet delivered as an answer) that frontmatter-based relevant-memory surfacing enters via `<system-reminder>`, and rewriting `자동메모리-딥다이브.html` to include it.

6. All user messages:
   - "프로젝트 코드랑 내용 전체 파악 해 자 시작!"
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
   - "자동메모리, 세션메모리, 컴팩션으로 만드는 메모리 이렇게 3개의 종류의 메모리가 있다. 자동메모리는 4개의 섹션으로 만드는 프로젝트전용이고 세션메모리는 해당 세션만을 위한 메모리다. 세션 메모리는 메인 에이전트 히스토리로 작성되나 작성은 서브에이전트가 진행하며 실험기능에 속하는 편이다. 컴팩션은 /compact를 사용했을때 그때 완성되는 요약 내용이다. 이거 설명맞는지도 알려주라"
   - "이 내용을 md_group/클로드코드-메모리-시스템.md의 §2(자동 메모리)에 추가해 둘까요? <- 응"
   - "auto memory 가 갱신되는 타이밍이언제야"
   - "자동메모리가 저정도만 기록하는데.. 의미가 잇는건가? 그 이유는?"
   - "/visual-explainer" (slash command, no args — interrupted: [Request interrupted by user])
   - "그니까 너의말은 대화 컨텍스트로 모를만한 일을 적ㅇ는다는건가"
   - "내요지는 저정도만 기록하냐라긴보다 왜 저걸 기록하냐랄까"
   - "그리고 왜 4타입이면 충분하달까"
   - "/visual-explainer 위 내용들 세세히 적어! 빠짐없이!"
   - "근데 실제 파일보니까 MEMORY.md 은인덱싱처럼 되어있고 나머지 문서로 나뉘어져 상세내용처럼되어있어 마치 LLM 위키같은건가"
   - "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??"

7. Pending Tasks:
   - Finish the in-progress rewrite of `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` (adding the frontmatter → `relevant_memories` attachment → system-reminder finding), open it, and deliver the prose answer to the user's last question with file:line evidence.
   - (Offered, not yet confirmed by user — do not start without confirmation): moving the HTML into `html_group_v2/` convention; reflecting the deep-dive content (2×2 matrix, WHO/HOW/WHY/WHERE, sufficiency argument) into `md_group/클로드코드-메모리-시스템.md` §2.

8. Current Work:
   Verifying the user's final hypothesis: "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??". Sequence completed so far: Read `src/memdir/findRelevantMemories.ts` in full (relevance search via `sideQuery` with the default Sonnet model); grepped callers outside memdir → `src/utils/attachments.ts`, `collapseReadSearch.ts`, `transcriptSearch.ts`, `claudemd.ts`; read the attachments.ts surfacing code — top-5 selection then:
   ```typescript
   .slice(0, 5)
   const memories = await readMemoriesForSurfacing(selected, signal)
   ...
   return [{ type: 'relevant_memories' as const, memories }]
   ```
   and confirmed the render path at `src/utils/messages.ts:3708`:
   ```typescript
   case 'relevant_memories': {
     return wrapMessagesInSystemReminder(
       attachment.memories.map(m => { ...
   ```
   — i.e. the hypothesis is CONFIRMED: relevant memories are surfaced through the attachment system wrapped in `<system-reminder>` (telemetry `tengu_memdir_prefetch_collected`, `attachments.ts:2412`). The very last action taken was a Write call rewriting `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` to incorporate this finding; the transcript ends mid-write, and no prose answer has been delivered to the user yet.

9. Optional Next Step:
   Complete the Write of `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html`, `open` it, and answer the user's question directly. This is squarely the task in progress: the user asked "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??" and my last words before the tool chain were "좋은 가설입니다 — 마침 아직 안 읽은 `findRelevantMemories.ts`(관련 메모리 검색)가 그 답일 가능성이 높아요. 누가 호출하고 결과가 어디로 들어가는지 확인하겠습니다." The answer to deliver: yes — `findRelevantMemories` (sideQuery/Sonnet) selects candidates, `attachments.ts` surfaces the top 5 as a `relevant_memories` attachment, and `messages.ts:3708` wraps them in `<system-reminder>` via `wrapMessagesInSystemReminder` — with the updated HTML as the visual companion.

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: ${transcriptPath}
Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.
```
