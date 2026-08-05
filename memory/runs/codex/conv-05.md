# codex 컴팩션 시뮬레이션 — conv-05

## 단계 1: 요약 생성 (SUMMARIZATION_PROMPT 적용 결과)

# CONTEXT CHECKPOINT COMPACTION — Handoff Summary

## Task Overview
The user is doing a source-level architecture study of OpenAI Codex (Rust repo at `/Users/seobi/jinsup_space/codex`, engine in `codex-rs/`) and comparing it against a Claude Code reverse-engineering research project (`/Users/seobi/jinsup_space/CC`, TypeScript `src/` + Korean docs `md_group/`). Deliverables are visual, diagram-heavy Korean HTML pages.

## User Preferences & Constraints
- User writes in Korean; respond in Korean. Strongly prefers visuals (diagrams/tables/SVG) over prose HTML ("텍스트보단 비주얼").
- Established design language across all HTML artifacts: Codex = teal, Claude Code (CC) = coral; dark theme; fonts Gothic A1 / IBM Plex Sans KR / JetBrains Mono.
- User twice corrected course: (1) compare the SINGLE main-agent turn pipeline, not multi-agent; (2) compare qualitative smart features/heuristics, not quantitative step counts ("양으로 우위 비교하지 말고 특징을 비교해").
- Model was set to Opus 4.8 (1M context) via /model mid-session.
- Two long-lived background subagents hold deep context and can be resumed via SendMessage:
  - `a866be613de0d7112` — CC query-loop investigator (read `CC/src` extensively)
  - `ac9d5f4b9caa7652b` — Codex turn-loop investigator (read `codex-rs/core` extensively)

## Progress & Key Verified Findings (all source-verified with file:line)

### 1. Codex overall architecture
- `codex-rs` = Cargo workspace, 148 crates. Single engine `codex-core` wrapped by `app-server` (JSON-RPC Thread/Turn/Item — the only official boundary); `tui`/`cli`, VSCode ext, TS/Python SDKs, and npm `codex-cli` are thin wrappers spawning the Rust binary. MCP is bidirectional (client via `codex-mcp`, server via `mcp-server`). Persistence: rollout JSONL + SQLite.
- Harness location (user asked "하네스 로직 어딨냐"): all in `codex-rs/core/src/` — `session/handlers.rs` (`submission_loop`), `session/turn.rs` (`run_turn` → `run_sampling_request` → `try_run_sampling_request`) ★ heart, `tasks/regular.rs` (`RegularTask::run`), `client.rs` (Responses API streaming), `tools/{router,parallel,orchestrator}.rs`. Language: 100% Rust (codex-cli JS is launcher only).
- Multi-agent (v2): `core/src/agent/` (control.rs, registry.rs w/ spawn-depth limit, role.rs TOML role layers, builtins like awaiter.toml) + tools `spawn_agent`/`send_message`/`followup_task`/`wait`/`interrupt`/`list_agents` — persistent bidirectional peer "society" (mailbox, `Op::InterAgentCommunication`) vs CC's one-shot fire-and-forget delegation tree returning a single final text.

### 2. Single main-agent turn loop (both systems)
- Both loops terminate identically: they do NOT trust `stop_reason`; continuation is purely "does the response contain tool calls" — Codex `needs_follow_up = model_needs_follow_up || has_pending_input` (`turn.rs:328`, also `end_turn: Some(false)` forces re-call), CC `needsFollowUp` (`query.ts:823-825`, `:1053`). Thinking/reasoning is NOT involved in loop control on either side (corrected a user misconception).
- Codex = Rust state machine loop + event-channel emits; CC = async generator `while(true)` + yield (`query.ts:305`). Codex uses OpenAI Responses API; CC uses Anthropic Messages API.

### 3. 8-axis "computational meticulousness" comparison (user's 8-step CC loop model verified)
1. Per-cycle preprocessing: CC 5-stage active pipeline each iteration (boundary slice → tool-result budget → snip → microcompact → autocompact → hard block, `query.ts:362-632`); Codex lighter per-cycle (pending-input drain → hooks → reminders → StepContext → `for_prompt`) with compaction placed AFTER sampling (`turn.rs:314-382`) — equal rigor, different position.
2. Withhold pattern — REVERSAL: CC eager-emits tool results in order during the stream (`StreamingToolExecutor.getCompletedResults`, write tools act as order barrier); the true hold-then-batch is Codex (`in_flight: FuturesOrdered` collected during stream, executed in `drain_in_flight` after `Completed`, `turn.rs:1907/2143/2493`). CC's `withheld` variable is for error recovery (prompt-too-long etc., `query.ts:790-816`), not tool results — user misconception corrected.
3. Smart batching: CC static `partitionToolCalls` (consecutive concurrency-safe tools batched, write tool breaks batch; max concurrency 10); Codex dynamic per-tool `RwLock` gate (read = parallel, write = exclusive, `parallel.rs:133-137`), no batches at all.
4. Tool pipeline: CC 10 steps (zod → validateInput → backfill → PreToolUse hook → permission chain → call → result mapping → PostToolUse → assembly, `toolExecution.ts`); Codex 12 steps incl. approval → sandbox select → attempt → on `SandboxErr::Denied` re-approval → escalated retry (`orchestrator.rs:137-469`).
5. Reminder injection: CC rich attachment types (edited_text_file, todo_reminder, plan_mode, critical_system_reminder, compaction_reminder, relevant_memories… `attachments.ts`); Codex injects independent `ContextualUserFragment` items (time_reminder, world_state diff, token budget).
6. Next-cycle reassembly: CC concat `[...messages, ...assistant, ...toolResults]`; Codex `clone_history().for_prompt()` — equal.
7. KV caching — the ONE real gap: CC plants `cache_control: ephemeral` breakpoints client-side on 3 fronts (system-prompt block boundaries, last tool schema, exactly 1 message marker on last message + `cache_reference` on prior tool_results; `claude.ts:3063/3213`); Codex plants none — only `prompt_cache_key = session_id` (`client.rs:888,469-473`), delegating to Responses API server-side prefix caching. API-design difference, not laziness.
8. Continue-or-stop: both deterministic tool-presence checks; identical.
Verdict: overall parity; Codex denser on tool-exec/safety (axes 2,3,4), CC denser on context/caching (axes 5,7).

### 4. Smart rules / heuristics (feature comparison, not counts)
- Read→Edit enforcement: CC has a REAL hard state gate — `readFileState` checked in `FileEditTool.validateInput` (`FileEditTool.ts:275-287`, errorCode 6 "read it first"; mtime staleness check `:290-311` errorCode 7; same in FileWriteTool/NotebookEditTool) + soft prompt rule. Codex has NO such state gate (no mtime/last_read tracking at all): `apply_patch` re-reads the file each time and validates patch context via `seek_sequence` 4-stage fuzzy matching (exact → rstrip → trim → Unicode punctuation normalization, `apply-patch/src/seek_sequence.rs:12,76-107`); mismatch = hard rejection. Framing: CC asks "did you read it?", Codex asks "do you know it exactly?".
- Conversation-based tool skipping/dedup: NEITHER system has it in code — purely model judgment (soft). Confirmed by grep on both sides.
- Codex-unique smarts: execpolicy Starlark DSL (`Decision::{Allow,Prompt,Forbidden}`, prefix/network rules), session + persistent approval caching (disk amendments to `default.rules`), sandbox escalation with re-approval, MCP `read_only_hint`-aware parallelism, Unicode fuzzy patch matching, auto-amendment blocked on complex shell parsing, record-time output truncation.
- CC-unique smarts: readFileState gate + changed-file auto reminders (`getChangedFiles` → edited_text_file diff attachments), AI permission classifier in auto mode (side_query), Plan mode hard gate, Bash dynamic `isConcurrencySafe` (parses command: `ls` parallel / write serial), `backfillObservableInput` path expansion (security + state-key consistency), PreToolUse hook input mutation, permission priority chain deny→ask→tool→bypass→alwaysAllow.

### 5. PTC / Code Mode
Codex's PTC equivalent = "Code Mode" (experimental): single `exec` tool takes raw JavaScript (not JSON; Lark-parsed), runs in a fresh V8 isolate (no Node/fs/network/console), all tools exposed as `await tools.*` with auto-generated TypeScript declarations; `store/load` cross-call state, `yield_control()` + `wait`, `text()/image()` emit helpers. Crates: `code-mode`, `code-mode-host`, `code-mode-protocol`, `core/src/tools/code_mode/`. Default remains function calling — `code_mode_only` flag gates exclusivity; Code Mode is a layer over the same tool dispatch.

### 6. Context preprocessing & KV-cache behavior (Codex)
- `for_prompt` (`history.rs:141` → `normalize_history:359`) = normalization ONLY (dangling call/output pair cleanup + image strip) — no slicing/budget/compaction per cycle.
- Tool-output truncation happens ONCE at record time (`record_items` `history.rs:121` → `truncate_function_output_payload`); "기록 시점" = the moment a result is first stored in history; truncated version is permanent (original unrecoverable — trade-off vs CC's disk offload).
- Compaction only at token limit: `run_pre_sampling_compact` (`turn.rs:815`, once pre-turn) and `run_auto_compact` (`turn.rs:971`, mid-turn via `should_roll_over`, `turn.rs:348`) — LLM summarization replacing history. CC's boundary-slice/snip/microcompact have NO Codex counterpart.
- KV cache: Codex history is append-only (reminders appended, throttled), so prefix stays stable — record-time truncation does NOT break cache (append+truncate at tail). Breakage is event-based: auto_compact history replace (biggest), post-compact initial-context reinjection (BeforeLastUserMessage mid-insert), image strip/normalize edits, rollback/fork, tool-list changes (MCP reload / tool_search deferred load).

### 7. Batching worked example (Read→Edit→Read→Read→Write)
- CC static partition: 4 batches `[Read][Edit][Read‖Read][Write]` (fragmentation rule: only consecutive safe tools merge).
- Codex dynamic locks yield the same schedule here (Read=shell cat read-lock, Edit/Write=apply_patch write-lock), BUT diverges if the write op is a shell command (e.g. `git push`): CC parses & isolates it serially; Codex `shell` is statically `supports_parallel_tool_calls = true` (`shell_command.rs:152`) regardless of command — runs it in parallel and relies on execpolicy + kernel sandbox for safety.

### 8. Codex-unique concepts (no CC counterpart)
Responses API stateful paradigm (`previous_response_id`, encrypted_content reasoning, server-held state — the root reason no client cache breakpoints are needed); 3-layer execution isolation (execpolicy Starlark → kernel sandbox Seatbelt/Landlock/bwrap → network-proxy egress MITM); `exec-server` remote/cross-OS tool execution; rollout JSONL streaming append + resume/fork + SQLite mirror; app-server single JSON-RPC boundary; StepContext atomic per-model-call snapshot; world_state diff injection (DeferredExecutor); agent-identity cryptographic signing; tool_search + deferred tools (exists in Codex too). Also noted: Codex has NO dedicated file-read tool — reads via `shell` (cat/sed/rg), edits via `apply_patch`.

## Artifacts Produced
Current files at `/Users/seobi/jinsup_space/codex/` (repo root, untracked in git, user asked for them there):
- `codex-cc-loop-features.html` — draw-arch L/R comparison of 6 loop features (tool search / batching / pipeline / preprocessing / reminders / KV caching) + unique-to-each lists; light/dark.
- `codex-multiTurn-flow.html` — Codex single-turn flow (INIT→LOOP→deep-dive→RESULT) mirroring `CC/html_group_v2/multiTurn-flow.html`, same "auth.ts 버그 고쳐줘" scenario, teal palette.
- `codex-unique.html` — Codex-only designs, 6 sections (Responses API stateful / 3-layer sandbox / exec-server / rollout+resume/fork / app-server / Code Mode+StepContext+world_state+agent-identity cards).
LOST (temp scratchpad was cleaned): agent-arch-compare.html, agent-turn-pipeline.html, loop-computation-detail.html, codex-vs-cc-master.html — user was offered regeneration; not yet requested.

## What Remains To Be Done (next step first)
1. IN PROGRESS: user's last question — "StepContext 이건 뭐야? 한번의 모델 호출?" The assistant had just started reading `/Users/seobi/jinsup_space/codex/codex-rs/core/src/session/step_context.rs` (imports seen: LoadedAgentsMd, TurnEnvironmentSnapshot, McpRuntimeSnapshot, TurnContext, ResolvedSelectedCapabilityRoot, codex_mcp::ToolInfo). Finish reading that file and answer in Korean: StepContext = the atomic snapshot (tools, environment, AGENTS.md, MCP runtime) fixed for one sampling request within a turn (captured via `capture_step_context`, `turn.rs:250-253`; reused as `next_step_context`). Verify details from the file before answering.
2. Open offers the user may pick up: regenerate the 4 lost HTMLs; deep-dive one Codex-unique axis (Responses API stateful flow, exec-server protocol, execpolicy Starlark, Code Mode V8) standalone; index page linking the HTML artifacts; draw-arch of the Codex harness structure (entry → run_turn loop → tools).
3. Keep using the two background subagents via SendMessage for further code verification instead of re-reading from scratch.

## 단계 2: 요약 재주입 (SUMMARY_PREFIX + 요약 본문 — 교체 히스토리에 user 메시지로 저장되는 형태)

Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:

# CONTEXT CHECKPOINT COMPACTION — Handoff Summary

## Task Overview
The user is doing a source-level architecture study of OpenAI Codex (Rust repo at `/Users/seobi/jinsup_space/codex`, engine in `codex-rs/`) and comparing it against a Claude Code reverse-engineering research project (`/Users/seobi/jinsup_space/CC`, TypeScript `src/` + Korean docs `md_group/`). Deliverables are visual, diagram-heavy Korean HTML pages.

## User Preferences & Constraints
- User writes in Korean; respond in Korean. Strongly prefers visuals (diagrams/tables/SVG) over prose HTML ("텍스트보단 비주얼").
- Established design language across all HTML artifacts: Codex = teal, Claude Code (CC) = coral; dark theme; fonts Gothic A1 / IBM Plex Sans KR / JetBrains Mono.
- User twice corrected course: (1) compare the SINGLE main-agent turn pipeline, not multi-agent; (2) compare qualitative smart features/heuristics, not quantitative step counts ("양으로 우위 비교하지 말고 특징을 비교해").
- Model was set to Opus 4.8 (1M context) via /model mid-session.
- Two long-lived background subagents hold deep context and can be resumed via SendMessage:
  - `a866be613de0d7112` — CC query-loop investigator (read `CC/src` extensively)
  - `ac9d5f4b9caa7652b` — Codex turn-loop investigator (read `codex-rs/core` extensively)

## Progress & Key Verified Findings (all source-verified with file:line)

### 1. Codex overall architecture
- `codex-rs` = Cargo workspace, 148 crates. Single engine `codex-core` wrapped by `app-server` (JSON-RPC Thread/Turn/Item — the only official boundary); `tui`/`cli`, VSCode ext, TS/Python SDKs, and npm `codex-cli` are thin wrappers spawning the Rust binary. MCP is bidirectional (client via `codex-mcp`, server via `mcp-server`). Persistence: rollout JSONL + SQLite.
- Harness location (user asked "하네스 로직 어딨냐"): all in `codex-rs/core/src/` — `session/handlers.rs` (`submission_loop`), `session/turn.rs` (`run_turn` → `run_sampling_request` → `try_run_sampling_request`) ★ heart, `tasks/regular.rs` (`RegularTask::run`), `client.rs` (Responses API streaming), `tools/{router,parallel,orchestrator}.rs`. Language: 100% Rust (codex-cli JS is launcher only).
- Multi-agent (v2): `core/src/agent/` (control.rs, registry.rs w/ spawn-depth limit, role.rs TOML role layers, builtins like awaiter.toml) + tools `spawn_agent`/`send_message`/`followup_task`/`wait`/`interrupt`/`list_agents` — persistent bidirectional peer "society" (mailbox, `Op::InterAgentCommunication`) vs CC's one-shot fire-and-forget delegation tree returning a single final text.

### 2. Single main-agent turn loop (both systems)
- Both loops terminate identically: they do NOT trust `stop_reason`; continuation is purely "does the response contain tool calls" — Codex `needs_follow_up = model_needs_follow_up || has_pending_input` (`turn.rs:328`, also `end_turn: Some(false)` forces re-call), CC `needsFollowUp` (`query.ts:823-825`, `:1053`). Thinking/reasoning is NOT involved in loop control on either side (corrected a user misconception).
- Codex = Rust state machine loop + event-channel emits; CC = async generator `while(true)` + yield (`query.ts:305`). Codex uses OpenAI Responses API; CC uses Anthropic Messages API.

### 3. 8-axis "computational meticulousness" comparison (user's 8-step CC loop model verified)
1. Per-cycle preprocessing: CC 5-stage active pipeline each iteration (boundary slice → tool-result budget → snip → microcompact → autocompact → hard block, `query.ts:362-632`); Codex lighter per-cycle (pending-input drain → hooks → reminders → StepContext → `for_prompt`) with compaction placed AFTER sampling (`turn.rs:314-382`) — equal rigor, different position.
2. Withhold pattern — REVERSAL: CC eager-emits tool results in order during the stream (`StreamingToolExecutor.getCompletedResults`, write tools act as order barrier); the true hold-then-batch is Codex (`in_flight: FuturesOrdered` collected during stream, executed in `drain_in_flight` after `Completed`, `turn.rs:1907/2143/2493`). CC's `withheld` variable is for error recovery (prompt-too-long etc., `query.ts:790-816`), not tool results — user misconception corrected.
3. Smart batching: CC static `partitionToolCalls` (consecutive concurrency-safe tools batched, write tool breaks batch; max concurrency 10); Codex dynamic per-tool `RwLock` gate (read = parallel, write = exclusive, `parallel.rs:133-137`), no batches at all.
4. Tool pipeline: CC 10 steps (zod → validateInput → backfill → PreToolUse hook → permission chain → call → result mapping → PostToolUse → assembly, `toolExecution.ts`); Codex 12 steps incl. approval → sandbox select → attempt → on `SandboxErr::Denied` re-approval → escalated retry (`orchestrator.rs:137-469`).
5. Reminder injection: CC rich attachment types (edited_text_file, todo_reminder, plan_mode, critical_system_reminder, compaction_reminder, relevant_memories… `attachments.ts`); Codex injects independent `ContextualUserFragment` items (time_reminder, world_state diff, token budget).
6. Next-cycle reassembly: CC concat `[...messages, ...assistant, ...toolResults]`; Codex `clone_history().for_prompt()` — equal.
7. KV caching — the ONE real gap: CC plants `cache_control: ephemeral` breakpoints client-side on 3 fronts (system-prompt block boundaries, last tool schema, exactly 1 message marker on last message + `cache_reference` on prior tool_results; `claude.ts:3063/3213`); Codex plants none — only `prompt_cache_key = session_id` (`client.rs:888,469-473`), delegating to Responses API server-side prefix caching. API-design difference, not laziness.
8. Continue-or-stop: both deterministic tool-presence checks; identical.
Verdict: overall parity; Codex denser on tool-exec/safety (axes 2,3,4), CC denser on context/caching (axes 5,7).

### 4. Smart rules / heuristics (feature comparison, not counts)
- Read→Edit enforcement: CC has a REAL hard state gate — `readFileState` checked in `FileEditTool.validateInput` (`FileEditTool.ts:275-287`, errorCode 6 "read it first"; mtime staleness check `:290-311` errorCode 7; same in FileWriteTool/NotebookEditTool) + soft prompt rule. Codex has NO such state gate (no mtime/last_read tracking at all): `apply_patch` re-reads the file each time and validates patch context via `seek_sequence` 4-stage fuzzy matching (exact → rstrip → trim → Unicode punctuation normalization, `apply-patch/src/seek_sequence.rs:12,76-107`); mismatch = hard rejection. Framing: CC asks "did you read it?", Codex asks "do you know it exactly?".
- Conversation-based tool skipping/dedup: NEITHER system has it in code — purely model judgment (soft). Confirmed by grep on both sides.
- Codex-unique smarts: execpolicy Starlark DSL (`Decision::{Allow,Prompt,Forbidden}`, prefix/network rules), session + persistent approval caching (disk amendments to `default.rules`), sandbox escalation with re-approval, MCP `read_only_hint`-aware parallelism, Unicode fuzzy patch matching, auto-amendment blocked on complex shell parsing, record-time output truncation.
- CC-unique smarts: readFileState gate + changed-file auto reminders (`getChangedFiles` → edited_text_file diff attachments), AI permission classifier in auto mode (side_query), Plan mode hard gate, Bash dynamic `isConcurrencySafe` (parses command: `ls` parallel / write serial), `backfillObservableInput` path expansion (security + state-key consistency), PreToolUse hook input mutation, permission priority chain deny→ask→tool→bypass→alwaysAllow.

### 5. PTC / Code Mode
Codex's PTC equivalent = "Code Mode" (experimental): single `exec` tool takes raw JavaScript (not JSON; Lark-parsed), runs in a fresh V8 isolate (no Node/fs/network/console), all tools exposed as `await tools.*` with auto-generated TypeScript declarations; `store/load` cross-call state, `yield_control()` + `wait`, `text()/image()` emit helpers. Crates: `code-mode`, `code-mode-host`, `code-mode-protocol`, `core/src/tools/code_mode/`. Default remains function calling — `code_mode_only` flag gates exclusivity; Code Mode is a layer over the same tool dispatch.

### 6. Context preprocessing & KV-cache behavior (Codex)
- `for_prompt` (`history.rs:141` → `normalize_history:359`) = normalization ONLY (dangling call/output pair cleanup + image strip) — no slicing/budget/compaction per cycle.
- Tool-output truncation happens ONCE at record time (`record_items` `history.rs:121` → `truncate_function_output_payload`); "기록 시점" = the moment a result is first stored in history; truncated version is permanent (original unrecoverable — trade-off vs CC's disk offload).
- Compaction only at token limit: `run_pre_sampling_compact` (`turn.rs:815`, once pre-turn) and `run_auto_compact` (`turn.rs:971`, mid-turn via `should_roll_over`, `turn.rs:348`) — LLM summarization replacing history. CC's boundary-slice/snip/microcompact have NO Codex counterpart.
- KV cache: Codex history is append-only (reminders appended, throttled), so prefix stays stable — record-time truncation does NOT break cache (append+truncate at tail). Breakage is event-based: auto_compact history replace (biggest), post-compact initial-context reinjection (BeforeLastUserMessage mid-insert), image strip/normalize edits, rollback/fork, tool-list changes (MCP reload / tool_search deferred load).

### 7. Batching worked example (Read→Edit→Read→Read→Write)
- CC static partition: 4 batches `[Read][Edit][Read‖Read][Write]` (fragmentation rule: only consecutive safe tools merge).
- Codex dynamic locks yield the same schedule here (Read=shell cat read-lock, Edit/Write=apply_patch write-lock), BUT diverges if the write op is a shell command (e.g. `git push`): CC parses & isolates it serially; Codex `shell` is statically `supports_parallel_tool_calls = true` (`shell_command.rs:152`) regardless of command — runs it in parallel and relies on execpolicy + kernel sandbox for safety.

### 8. Codex-unique concepts (no CC counterpart)
Responses API stateful paradigm (`previous_response_id`, encrypted_content reasoning, server-held state — the root reason no client cache breakpoints are needed); 3-layer execution isolation (execpolicy Starlark → kernel sandbox Seatbelt/Landlock/bwrap → network-proxy egress MITM); `exec-server` remote/cross-OS tool execution; rollout JSONL streaming append + resume/fork + SQLite mirror; app-server single JSON-RPC boundary; StepContext atomic per-model-call snapshot; world_state diff injection (DeferredExecutor); agent-identity cryptographic signing; tool_search + deferred tools (exists in Codex too). Also noted: Codex has NO dedicated file-read tool — reads via `shell` (cat/sed/rg), edits via `apply_patch`.

## Artifacts Produced
Current files at `/Users/seobi/jinsup_space/codex/` (repo root, untracked in git, user asked for them there):
- `codex-cc-loop-features.html` — draw-arch L/R comparison of 6 loop features (tool search / batching / pipeline / preprocessing / reminders / KV caching) + unique-to-each lists; light/dark.
- `codex-multiTurn-flow.html` — Codex single-turn flow (INIT→LOOP→deep-dive→RESULT) mirroring `CC/html_group_v2/multiTurn-flow.html`, same "auth.ts 버그 고쳐줘" scenario, teal palette.
- `codex-unique.html` — Codex-only designs, 6 sections (Responses API stateful / 3-layer sandbox / exec-server / rollout+resume/fork / app-server / Code Mode+StepContext+world_state+agent-identity cards).
LOST (temp scratchpad was cleaned): agent-arch-compare.html, agent-turn-pipeline.html, loop-computation-detail.html, codex-vs-cc-master.html — user was offered regeneration; not yet requested.

## What Remains To Be Done (next step first)
1. IN PROGRESS: user's last question — "StepContext 이건 뭐야? 한번의 모델 호출?" The assistant had just started reading `/Users/seobi/jinsup_space/codex/codex-rs/core/src/session/step_context.rs` (imports seen: LoadedAgentsMd, TurnEnvironmentSnapshot, McpRuntimeSnapshot, TurnContext, ResolvedSelectedCapabilityRoot, codex_mcp::ToolInfo). Finish reading that file and answer in Korean: StepContext = the atomic snapshot (tools, environment, AGENTS.md, MCP runtime) fixed for one sampling request within a turn (captured via `capture_step_context`, `turn.rs:250-253`; reused as `next_step_context`). Verify details from the file before answering.
2. Open offers the user may pick up: regenerate the 4 lost HTMLs; deep-dive one Codex-unique axis (Responses API stateful flow, exec-server protocol, execpolicy Starlark, Code Mode V8) standalone; index page linking the HTML artifacts; draw-arch of the Codex harness structure (entry → run_turn loop → tools).
3. Keep using the two background subagents via SendMessage for further code verification instead of re-reading from scratch.
