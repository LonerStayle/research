<!--
grok-build 컴팩션 시뮬레이션 — 대상: memory/data/conv-04.txt
수행 단계: 단계 1(사전 메모리 플러시) → 단계 2(풀 리플레이스 컴팩션).
단계 1b는 이 세션의 첫 플러시이므로 미해당(이전 플러시 내용 없음). 단계 2 대안은 short-prompt 하네스 전용이라 미수행.
단계 3은 LLM 산출물이 아닌 하네스 조립 텍스트({cleaned}/{loc} 치환부 — 무시 지시), 단계 4(dream)는 세션 종료 후 별도 패스라 미수행.
{user_context_section}은 빈 문자열로 취급.
-->

## 단계 1

## Decisions & rationale

- Comparison framing was corrected twice by the user and settled as: (1) compare Codex vs Claude Code at the **single main-agent turn-loop level**, not the multi-agent layer; (2) compare **qualitative smart-rule characteristics**, not quantitative step counts ("몇 단계 우위" framing rejected); (3) deliverables should be **diagram-heavy HTML with minimal text**.
- Unified visual design system across all artifacts: Codex = teal (mesh network / gear emblem), Claude Code = coral (delegation tree / braces emblem); dark theme, Gothic A1 + IBM Plex Sans KR + JetBrains Mono fonts.
- HTML artifacts were first written to the session scratchpad to avoid polluting the codex git repo; later moved to `/Users/seobi/jinsup_space/codex/` at the user's explicit request ("루트로 옮겨줘").

## Technical context

- **Codex repo**: `/Users/seobi/jinsup_space/codex` — `codex-rs` Rust Cargo workspace (148 crates) is the engine; `codex-cli` (npm) and `sdk/typescript`·`sdk/python` are thin launchers that spawn the Rust binary; `app-server` (JSON-RPC Thread/Turn/Item over stdio/ws/uds) is the only official boundary; persistence = rollout JSONL (streamed append) + SQLite mirror.
- **Codex harness path**: `core/src/session/handlers.rs` (`submission_loop`) → `tasks/regular.rs` (`RegularTask::run`) → `session/turn.rs` `run_turn` (main loop) → `run_sampling_request` → `try_run_sampling_request` → `client.rs` (OpenAI Responses API streaming) → `tools/{router,parallel,orchestrator}.rs`. All harness logic is Rust; `codex-cli` JS is launcher-only.
- **Claude Code research repo**: `/Users/seobi/jinsup_space/CC` — reverse-engineered TS source (`src/`) + Korean analysis docs (`md_group/`), remote `LonerStayle/cc_agent_bible.git`; harness = `src/query.ts` `queryLoop` `while(true)` async generator.
- **8-axis loop comparison (all source-verified)**: both loops terminate purely on absence of tool calls (`needsFollowUp` / `needs_follow_up`; `stop_reason` distrusted; thinking uninvolved in loop control). CC's tool-result handling is **eager-emit-in-order** (the `withheld` variable at `query.ts:790` is error-recovery only, for prompt-too-long/max-output-tokens); the true hold-then-batch pattern belongs to **Codex** (`in_flight: FuturesOrdered` queued during streaming → `drain_in_flight` after `Completed`, `turn.rs:1907/2493`). Tool pipeline: CC ~10 steps (zod → validateInput → PreToolUse hooks → canUseTool → call → PostToolUse → assembly, `toolExecution.ts`) vs Codex 12 steps (approval → sandbox select → attempt → denial → re-approval → escalated retry, `orchestrator.rs:137`).
- **KV/prompt caching**: CC plants `cache_control: ephemeral` breakpoints client-side (`claude.ts:3063 addCacheBreakpoints` — system-prompt boundary blocks, last tool schema, exactly 1 message-level marker on the last message, `cache_reference: tool_use_id` on earlier tool_results). Codex plants **none** — only `prompt_cache_key = session_id` (`client.rs:888, 469-473`), delegating to Responses API server-side automatic prefix caching; `cache_control` is absent from the entire codebase (grep-verified). Codex stays cache-friendly by being **append-only**: cache breaks are event-driven only (auto_compact history replace, post-compact initial-context reinjection `BeforeLastUserMessage`, image strip/normalize, history rollback/fork, tool-list change).
- **Context preprocessing**: CC runs a 5-stage pipeline every cycle (compact-boundary slice → `applyToolResultBudget` → snip → microcompact → autocompact). Codex per-cycle does **normalization only** (`for_prompt` → `normalize_history`, `history.rs:141/359`: dangling call↔output pair cleanup + image strip); tool output is truncated **once at record time** (`record_items` → `truncate_function_output_payload`, `history.rs:121`, TruncationPolicy); LLM-summary compaction fires **only on token-limit hit** (`run_pre_sampling_compact` `turn.rs:815` pre-turn; `run_auto_compact` `turn.rs:971` mid-turn via `should_roll_over` `turn.rs:348`). CC has no Codex counterpart for microcompact/snip; Codex has no per-cycle re-budgeting.
- **Parallelism/batching**: CC `partitionToolCalls` builds static batches (single write tool OR consecutive read-only run; concurrency cap 10); Bash judges dynamically via `isConcurrencySafe = isReadOnly(input)`. Codex builds **no batches** — each tool `tokio::spawn`s and takes a shared `RwLock` (`parallel.rs:133-137`: read = parallel, write = exclusive); flags are per-tool static (`shell` unconditionally `supports_parallel_tool_calls = true`, `shell_command.rs:152`; `apply_patch` false; MCP tools honor `read_only_hint`). For `Read→Edit→Read→Read→Write` both yield the same schedule `[Read]→[Edit]→[Read‖Read]→[Write]`; they diverge when the write is a shell command (CC isolates it into its own batch, Codex runs it in parallel and relies on execpolicy+sandbox).
- **Edit-safety rules**: CC Read→Edit is a real hard gate — `readFileState` check in `FileEditTool.ts:275-311` (errorCode 6 "File has not been read yet", errorCode 7 mtime "modified since read"), enforced before `tool.call` at `toolExecution.ts:683-687`; plus per-turn changed-file diff attachments (`attachments.ts:2063 getChangedFiles`). Codex has **no read-state/mtime tracking** — `apply_patch` re-reads the file and requires context-line match via `seek_sequence` 4-stage fuzzy matching (exact → rstrip → trim → Unicode punctuation normalization, `apply-patch/src/seek_sequence.rs:12,76-107`). Neither system skips/dedups tool executions based on conversation content (both grep-confirmed absent).
- **Codex-only mechanisms**: execpolicy Starlark DSL (`default.rules`, Decision::{Allow,Prompt,Forbidden}), approval persistence to disk (prefix-rule amendment + `ApprovedCommandPrefixSaved` fragment), sandbox-denial escalation with re-approval, kernel sandbox stack (Seatbelt/Landlock/bwrap + network egress proxy), exec-server remote/cross-OS tool relay, stateful Responses API (`previous_response_id`, encrypted reasoning), StepContext atomic per-call snapshot, world_state diff injection, agent-identity (cryptographic subagent identity), rollout resume/fork. CC-only: AI permission classifier (auto mode side_query), Plan mode gate, rich attachment taxonomy (edited_text_file/todo/plan_mode/critical_system_reminder/relevant_memories…), client-controlled cache breakpoints.
- **Code Mode = Codex's PTC** (experimental, default remains function calling): single `exec` tool accepts raw JS (Lark grammar parsed), runs in a fresh V8 isolate (no Node/fs/network/console), all tools exposed as global `tools.*` with auto-generated TypeScript declarations, `store/load` cross-call state, `yield_control()` + `wait` for long scripts, `text()/image()/notify()/exit()` emit helpers. Crates: `code-mode`, `code-mode-host`, `code-mode-protocol` (+ `core/src/tools/code_mode/execute_spec.rs`, `code_mode_only` flag). Codex also has `tool_search` + deferred tools (`core/src/tools/handlers/tool_search.rs`, `ResponseItem::ToolSearchCall`).
- Codex has **no dedicated file-read tool** — reads via `shell` (cat/sed/rg), edits via `apply_patch`.
- Multi-agent contrast (earlier phase): Codex = persistent bidirectional mailbox society (`Op::InterAgentCommunication`; send_message/followup_task/wait/interrupt/list_agents; roles as TOML config layers; fork_turns history inheritance); CC = one-shot unidirectional delegation (Task/query() recursion, .md frontmatter roles, no nesting).

## Debugging techniques & tools

- Long investigations delegated to **persistent background subagents**: `SendMessage` to a finished agent id resumes it from transcript in the background; results arrive as `<task-notification>` with output files under `tasks/<id>.output`. The same two agents were re-queried three times with progressively refined lenses (multi-agent → 8-axis loop mechanics → smart-rule features).
- **Negative-evidence greps** to prove feature absence: `mtime|stale|last_read|has_been_read` (no read-state tracking in Codex), `cache_control|CacheControl` (no client-side cache breakpoints in Codex), `dedup|duplicate` (no tool-execution dedup in either system).

## Problems & solutions

- Generated-HTML typos from large Write calls: CSS `--muted:#8persist;` (agent-arch-compare.html) and SVG `stroke="#3a4counter"` + duplicated rect (loop-computation-detail.html) — both fixed with targeted Edits immediately after creation.
- Session scratchpad was cleaned up mid-session: 4 of 5 earlier comparison HTMLs vanished; only the newest survived and was moved to the repo root. Lesson: move keep-worthy deliverables out of the ephemeral scratchpad promptly.
- User misconceptions corrected via source verification: CC "withhold-then-batch" is actually eager-emit-in-order (real `withheld` is error recovery); loop continuation is never decided in thinking — only `tool_use` presence; the imagined hold-then-batch behavior is Codex's `drain_in_flight`.
- A subagent dispatch was rejected by the user mid-conversation (tool-use rejection + `/model` switch to Opus 4.8 1M); recovered by reading the Codex agent sources directly, then re-introducing subagents later.

## 단계 2

<summary>
1. Primary Request and Intent:
The user (working in Korean) is reverse-engineering how the OpenAI Codex CLI works internally and comparing it against Claude Code (a reverse-engineered research copy at /Users/seobi/jinsup_space/CC). Their requests evolved through explicit corrections:
- Initially: "코덱스 아키텍처가 어떻게돼?" then "에이전트 로직이 어떻게 되는데?" — overall architecture and agent logic of the Codex repo (/Users/seobi/jinsup_space/codex).
- Correction 1: stop talking about multi-agent; compare on the basis of **a single main agent's turn pipeline** ("제발 멀티에이전트기준으로 얘기하지말고.. 하나의 메인에이전트 파이프라인 기준으로 비교해봐 ㅠㅜ").
- Asked whether Codex's loop is as "computational/mechanical" as their 8-step mental model of Claude Code's loop (전처리 → 위드홀드패턴 → 스마트배치 → 10단계 도구 파이프라인 → tool_results+어태치먼트 묶음 → 다음 사이클 전처리 → system-reminder 과다 전송+KV캐싱 → thinking 판단), and wanted every result visualized via /visual-explainer ("방금 결과들 빠짐없이 /visual-explainer 로 줘").
- Correction 2: do not compare by quantity/step counts; compare **functional smart features** — e.g. CC's Read→Edit hard rule, soft tool-ordering rules, whether either system skips tools based on conversation ("양으로 우위 비교하지말구... 특징을 비교해야지").
- Wanted a comprehensive visual master comparison, "html을 비주얼쪽으로 작성잘해줘 택스트보단.."
- Invoked /draw-arch twice; asked clarifying questions (is Codex a frontend? where is the harness logic? what language? is it function-calling based? does it have PTC?).
- Asked for a left/right draw-arch comparing 6 loop features (툴서치, 도구스마트배치, 도구10단계파이프라인, 컨텍스트전처리, 시스템 리마인더, KV캐싱준수) plus concepts unique to each side; then "루트로 옮겨줘" (move HTML files to the codex repo root).
- Follow-up deep dives: how for_prompt + auto_compact work vs CC's 5-stage preprocessing; a Codex version of CC's multiTurn-flow.html; whether Codex has an equivalent of smart batching; a concrete walk-through of a Read→Edit→Read→Read→Write tool sequence in both systems; whether Codex's KV cache breaks often; what "기록 시점" (record-time truncation) means; whether record-time truncation breaks KV caching; and — worried they had been framing everything through CC's interface — what is uniquely Codex ("코덱스만의 무언가는 뭐없나?"), visualized diagram-first ("그걸 최대한 도표나 이미지 위주로 html으로 만들어줘").
- Finally: conceptual questions about exec-server remote/cross-OS execution (why run tools on another OS?) and, last, where the isolation is created — OpenAI's servers or a local VM.
Constraints/preferences: Korean communication; visuals over text; no quantitative-superiority framing; keep artifacts source-verified with file:line evidence; deliverables in the codex repo root.

2. Key Technical Concepts:
- Rust Cargo workspace (codex-rs, 148 crates), app-server JSON-RPC boundary (Thread/Turn/Item), codex-core engine
- Agentic loop: run_turn state machine (Codex) vs queryLoop while(true) async generator (CC); loop continuation via needs_follow_up / needsFollowUp (tool-call presence; stop_reason distrusted; thinking uninvolved)
- OpenAI Responses API (stateful; previous_response_id, encrypted reasoning, prompt_cache_key server-side prefix caching) vs Anthropic Messages API (stateless; cache_control: ephemeral client breakpoints)
- Tool execution: ToolOrchestrator 12-step (approval → sandbox → attempt → escalated retry) vs CC 10-step (zod → validateInput → hooks → permissions → call → PostToolUse → assembly)
- Parallelism: static partitionToolCalls batches + isConcurrencySafe (CC) vs per-tool flags + dynamic RwLock read/write gate + FuturesOrdered drain (Codex); MCP read_only_hint
- Edit safety: readFileState/mtime state gate (CC) vs apply_patch seek_sequence 4-stage fuzzy context matching (Codex)
- Context management: CC 5-stage per-cycle pipeline (boundary slice/budget/snip/microcompact/autocompact) vs Codex normalize-only for_prompt + record-time truncation + threshold-triggered run_auto_compact (LLM summarization)
- execpolicy (Starlark DSL), kernel sandbox (Seatbelt/Landlock/bwrap), network egress proxy, sandbox escalation re-approval, approval persistence (default.rules amendment)
- Code Mode (V8 isolate JS orchestration; PTC equivalent), tool_search/deferred tools, exec-server remote relay, rollout JSONL + resume/fork, StepContext, world_state diff, agent-identity
- Multi-agent: Op::InterAgentCommunication mailbox society (Codex) vs one-shot delegation (CC)
- Harness skills used: Explore/general-purpose subagents, SendMessage background resume, visual-explainer, draw-arch

3. Files and Code Sections:
Codex sources examined directly (why: verifying harness/agent/loop/caching behavior; snippets not retained verbatim in context except key lines noted):
- codex-rs/core/src/agent/{mod.rs, registry.rs, agent_resolver.rs, status.rs, role.rs, control.rs, builtins/awaiter.toml}, core/src/session/multi_agents.rs, core/src/tools/handlers/multi_agents_v2/{spawn.rs, message_tool.rs, interrupt_agent.rs, wait.rs, list_agents.rs} — multi-agent phase.
- codex-rs/core/src/session/turn.rs (loop preamble ~227-298; post-sampling ~300-400; run_pre_sampling_compact:815; run_auto_compact:971; needs_follow_up:328/348) — main loop.
- codex-rs/core/src/context_manager/history.rs (for_prompt:141, normalize_history:359, record_items:121 → truncate_function_output_payload) — record-time truncation vs emission-time normalization.
- codex-rs/core/src/compact.rs (SUMMARIZATION_PROMPT-driven history replace), core/src/session/time_reminder.rs (take_reminder_due interval-suppressed append), core/src/tools/parallel.rs (RwLock gate :48,106,133-137), core/src/tools/handlers/shell/shell_command.rs (supports_parallel_tool_calls → true, :152), core/src/client.rs (prompt_cache_key :469-473,888).
- Code Mode: codex-rs/core/src/tools/code_mode/execute_spec.rs (code_mode_only flag), code-mode/src/lib.rs, code-mode-protocol/src/description.rs ("Run JavaScript code to orchestrate/compose tool calls").
CC sources verified via persistent subagents (file:line cited in findings): src/query.ts (queryLoop:305; preprocessing order :362-632; withheld :790-816; needsFollowUp :823-825,1053; messages concat :1704), toolOrchestration.ts (partitionToolCalls:91, concurrency cap :8-12), toolExecution.ts (10-step pipeline :599-1568), StreamingToolExecutor.ts (eager emit :412,436-438), FileEditTool.ts (:275-311 readFileState/mtime gates, backfillObservableInput :115-121), FileWriteTool.ts/NotebookEditTool.ts/FileReadTool.ts (:842-844), claude.ts (getCacheControl :358-374, buildSystemPromptBlocks :3213, addCacheBreakpoints :3063-3206), messages.ts (normalizeMessagesForAPI :2069+), attachments.ts (getChangedFiles :2063; attachment taxonomy), permissions.ts (5-step chain :1158-1296), prompts.ts (soft rules :301-310), BashTool.tsx (:434 isConcurrencySafe).
Reference template: /Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html.
HTML artifacts created (full markup not reproducible from context; structure known):
- Scratchpad (session /private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653.../scratchpad/, later wiped): agent-arch-compare.html (multi-agent mesh vs tree; CSS typo fixed via Edit), agent-turn-pipeline.html (single-turn 8-stage lanes), loop-computation-detail.html (8-axis gauge; SVG typo fixed via Edit), tool-smart-rules.html (smart-rule feature matrix), codex-vs-cc-master.html (master synthesis). All lost except the last-created draw-arch file.
- Surviving, moved/created in repo root: /Users/seobi/jinsup_space/codex/codex-cc-loop-features.html (draw-arch left/right, 6 loop features + unique concepts; light/dark), /Users/seobi/jinsup_space/codex/codex-multiTurn-flow.html (Codex version of CC's multiTurn-flow: INIT → LOOP → 심화 → RESULT, teal, same "auth.ts 버그 고쳐줘" scenario), /Users/seobi/jinsup_space/codex/codex-unique.html (6 Codex-unique axes, diagram-first: Responses API stateful / 3-layer sandbox / exec-server / rollout+resume/fork / app-server / Code Mode+etc). All untracked new files in the codex git repo (not committed).

4. Errors and Fixes:
- Second subagent dispatch (multi-agent deep dive) was rejected: "The user doesn't want to proceed with this tool use... STOP what you are doing" + [Request interrupted by user for tool use]. User then ran /model (→ "Set model to Opus 4.8 (1M context) (default)") and said "이어서해". Fix: read Codex agent files directly instead of dispatching, resuming subagent usage later.
- CSS typo in agent-arch-compare.html (`--muted:#8persist;`) — fixed with Edit after Write.
- SVG typo in loop-computation-detail.html (`stroke="#3a4counter"` + duplicate rect) — fixed with Edit.
- Bash exit code 1 during code-mode crate listing ((eval):1 zsh glob artifact) — harmless; needed data still returned.
- "no matches found: /Users/seobi/jinsup_space/codex/*.html" — expected (no HTML in root before move).
- Scratchpad cleanup silently deleted 4 of 5 earlier HTMLs; only codex-cc-loop-features.html survived and was moved to the repo root; user was told recreation is possible.
- User-feedback corrections (verbatim): "제발 멀티에이전트기준으로 얘기하지말고.. 하나의 메인에이전트 파이프라인 기준으로 비교해봐 ㅠㅜ" (framing fix), "음... 각 단계 파이프라인을.. 뭔가 양으로 우위 비교하지말구... 흐...흠... 특징을 비교해야지" (no quantitative framing).
- User-model misconception fixes from source verification: (a) CC's "withhold-then-batch" is wrong — StreamingToolExecutor emits results eagerly in order; the real `withheld` (query.ts:790) is error-recovery holdback; (b) "thinking decides continuation" is wrong — only tool_use presence (needsFollowUp) decides; Codex likewise uses needs_follow_up only.

5. Problem Solving:
Solved: full Codex repo architecture map; Codex multi-agent model vs CC delegation; single-turn loop pipelines of both engines source-verified; 8-axis "computational rigor" verdict (4 equal, tool-exec/parallelism denser in Codex including 12-step orchestrator, attachments/KV-caching stronger in CC; the only fundamental gap is caching — client cache_control breakpoints vs server-side prompt_cache_key, an API-design difference); smart-rule feature inventory (CC state-tracking rules vs Codex content/policy rules; no conversation-based tool skipping in either); Code Mode identified as Codex's PTC (optional layer over default function calling); Codex context handling = normalize-only per cycle + record-time truncation + threshold-only auto_compact; KV cache stability analysis (append-only keeps prefix stable; breaks are event-driven: auto_compact, initial-context reinjection, image strip, rollback/fork, tool-list change); Read→Edit→Read→Read→Write batching walk-through (same schedule, different mechanisms; divergence when the write is a shell command); record-time truncation explained and shown to be cache-preserving; Codex-unique concept set compiled; exec-server rationale explained (target-OS fidelity, isolation, offloading).
In progress: the user's final question — whether the isolation environment is created on OpenAI servers or as a local VM — was asked but not yet answered (conversation cut off). Two forked background questions were also mentioned as running in separate sessions (previous_response_id availability for general users; the three sandbox terms), independent of this thread.

6. All User Messages:
(4 task-notification messages and one local-command-stdout are omitted as tool/system results.)
1. "코덱스 아키텍처가 어떻게돼?"
2. "에이전트 로직이 어떻게 되는데?"
3. [Request interrupted by user for tool use]
4. [슬래시커맨드 /model] (model set to Opus 4.8 (1M context))
5. "이어서해"
6. "제발 멀티에이전트기준으로 얘기하지말고.. 하나의 메인에이전트 파이프라인 기준으로 비교해봐 ㅠㅜ"
7. "❯ 루프적인 모습을봐야지 클로드코드는 전처리 -> 위드홀드패턴 + (LLM호출) -> 도구 스마트배치 세팅 -> 도구 10단계 파이프라인 진행 -> 전체 배치완료 후 tool_results 묶음, 적절한 어태치먼트 삽입 -> 다음 사이클 컨텍스트전처리 -> 전체적인 tool_results + 어태치먼트및 시스템리마인드 과다 전송(이때 KV캐싱 구성) -> 이어서할지말지 thinking 에서 판단 / 이렇단 말야 그록도 이렇게 엄청 디테일하게 루프가 계산적이냐구;"
8. "방금 결과들 빠짐없이 /visual-explainer 로 줘"
9. "음... 각 단계 파이프라인을.. 뭔가 양으로 우위 비교하지말구... 흐...흠... 특징을 비교해야지  클로드코드의 도구 배치 세팅할때 그 Read -> Edit 강제 하드규칙이나 그외 툴콜링순서 소프트규칙이있기도하고 그러거든.. 클로크돜드가 대화세션보고 뛰어넘길때도 있고 .. 아무튼 이러한 스마트 기능들이있는지 알고싶어"
10. "구 얘기로 한건 예를든건데 아무튼 다양한 스마트특징들과 이전 대화에서 내가 요청한클로드코드 비교 대조해서  잘 비교를해봐 가능하면 html을 비주얼쪽으로 작성잘해줘 택스트보단.."
11. [슬래시커맨드 /draw-arch]
12. "Codex는 프론트엔드야?"
13. "아니 하네스로직이 어딨냐구"
14. "언어는 뭔데?"
15. "코덱스에 PTC를 호출하는게 있어? 프로그래매틱 도구 호출"
16. "펑션콜링 기반 에이전트가 아니었구나?"
17. "코덱스에도 툴서치, 도구스마트배치, 도구10단계파이프라인, 컨텍스트전처리, 시스템 리마인더,KV캐싱준수  같은게 있어? 비교해주고 그 그리고 클로드코드외에 없는 개념도 알려주러 /draw-arch"
18. "루트로 옮겨줘"
19. "for_prompt + auto_compact 이건 어떻게 하고있대? cc 는 전처리 5단계있잖아"
20. "클로드코드에 @/Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html 이거처럼 코덱스도 한번 정리해볼래?"
21. "스마트 배치가 같은게 있어?"
22. "어... 예시를 좀더들어주라 뭐 도구가 Read, Edit, Read,Read, Write  이렇게 모델이 내뱉었을때 어떤식으로 각각 되는지?"
23. "그리고 코덱스는 KV캐싱이 깨지는구간이 많아?"
24. "코덱스는 그리고 그 컨텍스트전처리는 안해?"
25. "기록 시점 이라는게 뭐지?"
26. "도구결과 절단 저렇게 하면 KV캐싱 깨지지않니? ㄷㄷ 그리고 내가 클로드코드 기준으로 얘기했지만 너무 그인터페이스에 맞춰서 질문한거 같아서 걱정이야 코덱스만의 무언가는 뭐없나?"
27. "그걸 최대한 도표나 이미지 위주로 html으로 만들어줘"
28. "도구를 원격·다른 OS에서 실행 (릴레이 프로토콜) — 로컬 Mac에서 원격 Windows 셸 실행 라는게 뭔말이야? 왜 다른 OS에서 실행이 필요하지?"
29. "그 격리 만드는건 OpenAI서버에서 하는거야? 아니면 내 컴퓨터에서 VM 뛰우는거야?"

7. Pending Tasks:
- Answer the user's last question: whether Codex's isolation/execution environment is created on OpenAI's servers or as a VM on the local machine.
- (Offered but not requested: recreating the 4 lost scratchpad HTMLs; merging the HTML artifacts into an index page; deeper single-axis dives. Do not treat these as tasks unless the user asks.)

8. Current Work:
Immediately before this summary, I was answering conceptual follow-ups about exec-server: I had just created /Users/seobi/jinsup_space/codex/codex-unique.html (6 diagram-first sections on Codex-unique design: stateful Responses API, 3-layer kernel sandbox, exec-server, rollout+resume/fork, app-server single boundary, Code Mode/StepContext/world_state/agent-identity), opened it in the browser, and explained why cross-OS remote execution exists (target-OS fidelity for build/test, protecting the local machine via disposable remote environments, offloading heavy work to cloud — with the diagram "[내 Mac] 에이전트가 생각 → 릴레이 → [원격 Windows] npm run build 실행"). The user then asked: "그 격리 만드는건 OpenAI서버에서 하는거야? 아니면 내 컴퓨터에서 VM 뛰우는거야?" — no answer has been given yet.

9. Optional Next Step:
Answer the pending question directly, distinguishing the layers already verified in source: Seatbelt/Landlock/bwrap are local OS-kernel sandboxes running on the user's own machine (no VM, no server), while exec-server is an optional relay to a remote machine and Codex Cloud is the OpenAI-hosted variant — verifying specifics in codex-rs (exec-server crate, sandbox setup code) if needed before asserting. This continues the exchange that ended with the user's verbatim question: "그 격리 만드는건 OpenAI서버에서 하는거야? 아니면 내 컴퓨터에서 VM 뛰우는거야?", immediately following my exec-server explanation "에이전트는 계속 Mac에서 돌지만, `build` 명령만 **원격 Windows로 보내서** 거기 결과를 받아옵니다."
</summary>
