# codex 컴팩션 시뮬레이션 — conv-04

## 단계 1: 요약 생성 (SUMMARIZATION_PROMPT 적용 산출물)

# CONTEXT CHECKPOINT COMPACTION — Handoff Summary

## Task Overview
The user (Korean speaker — all replies must be in Korean) is running a source-verified deep-dive comparing two coding-agent harnesses, producing diagram-heavy Korean HTML visualizations along the way:
- **Codex** (OpenAI, Rust): `/Users/seobi/jinsup_space/codex` — engine in `codex-rs/core/src/` (Cargo workspace, 148 crates)
- **Claude Code (CC)** (reverse-engineered TypeScript research repo): `/Users/seobi/jinsup_space/CC` (`src/` + `md_group/`)

Visual identity is fixed: **teal = Codex, coral = CC**.

## Current Progress & Key Decisions
Work proceeded through these completed phases (all claims below were verified against actual source by me or by two background subagents):

1. **Architecture survey**: Codex = single Rust engine (`codex-core`) behind `app-server` JSON-RPC boundary (Thread/Turn/Item); `codex-cli`(npm)/SDKs are thin wrappers; MCP is bidirectional; extension system is trait-based plugins.
2. **Multi-agent comparison** (first HTML): Codex = persistent bidirectional peer "mailbox" society (`Op::InterAgentCommunication`; spawn/send_message/followup_task/wait/interrupt/list under `core/src/tools/handlers/multi_agents_v2/`, `core/src/agent/{control,registry,role}.rs`, roles as TOML config layers) vs CC = one-shot fire-and-forget delegation (subagent returns one final text). User then **redirected: compare the single main-agent pipeline, not multi-agent**.
3. **Single-turn loop pipeline**: Codex `run_turn` (`core/src/session/turn.rs`) = Rust state machine + event emit; CC `queryLoop` (`src/query.ts:305`) = async-generator `while(true)` + yield. **Both terminate solely on presence of tool calls** — CC `needsFollowUp` (`query.ts:823-825`, `:1053`; stop_reason distrusted per comment `:549-551`), Codex `needs_follow_up = model_needs_follow_up || has_pending_input` (`turn.rs:328`; `end_turn` fallback `codex-api/common.rs:93-95`). Thinking/reasoning plays no role in loop control in either system.
4. **8-axis "computational meticulousness" comparison** (user's 8-step CC loop model checked): verdict = overall parity; Codex denser in tool execution/parallelism, CC denser in context/caching. Two corrections to the user's model: (a) CC's tool results are **eager-emit-in-order** (`StreamingToolExecutor.ts:412`, barrier at `:436-438`), not hold-and-batch — the real "withhold" pattern belongs to **Codex** (`in_flight: FuturesOrdered` queued during streaming, executed at `drain_in_flight` after Completed — `turn.rs:2143`, `:2493`, `:1907`); CC's `withheld` variable is error-recovery only (`query.ts:790-816`). (b) Continuation is never decided by thinking. Tool pipeline: CC 10 steps (`toolExecution.ts:337`→`:599`; zod→validateInput→backfill→PreToolUse hook→permission→call→result mapping→PostToolUse→assembly) vs Codex 12 steps (`orchestrator.rs:137`; approval→sandbox select→attempt→denied→re-approval→escalated retry).
5. **Smart rules / heuristics comparison** (user explicitly rejected quantitative "step count" framing — wants functional characteristics): 
   - **Read→Edit enforcement**: CC = hard state gate `readFileState` (`FileEditTool.ts:275-287` errorCode 6; mtime staleness `:290-311` errorCode 7; also FileWriteTool/NotebookEditTool) + changed-file auto reminders (`attachments.ts:2063`). Codex = **no state gate at all**; `apply_patch` re-reads the file and validates patch context via `seek_sequence` 4-stage fuzzy matching (exact→rstrip→trim→Unicode normalization; `apply-patch/src/seek_sequence.rs:12`, `:76-107`). Slogan used: CC asks "읽었니?" (state tracking), Codex asks "정확히 아니?" (content matching).
   - **Conversation-aware tool skipping/dedup: neither system has it in code** — purely model-side soft behavior.
   - Codex-only: execpolicy Starlark DSL (`core/src/exec_policy.rs`), approval caching session + **persistent disk amendment** (`exec_policy.rs:409-440`), sandbox-denial escalation re-approval, MCP `read_only_hint` respected for parallelism, Unicode fuzzy patch, complex-parse auto-amendment block.
   - CC-only: AI permission classifier in auto mode (`permissions.ts:518-524`), 5-step permission chain (deny→ask→tool→bypass→alwaysAllow, `permissions.ts:1158`), Plan mode gate, Bash **dynamic** `isConcurrencySafe = isReadOnly(input)` (`BashTool.tsx:434`), path backfill doubling as hook-bypass security.
6. **Smart batching detail**: CC = static partition `partitionToolCalls` (`toolOrchestration.ts:91`; batches = single write OR consecutive read-only run; concurrency cap 10). Codex = **no batches**; per-tool `tokio::spawn` + dynamic `RwLock` gate (read=parallel/write=exclusive, `parallel.rs:131-137`); shell is **statically parallel=true regardless of command content** (`shell_command.rs:152`). Worked example `Read→Edit→Read→Read→Write`: identical schedule `[Read][Edit][Read‖Read][Write]` in both — but if the write is a shell command (e.g. `git push`), CC isolates it in a solo batch while Codex runs it in parallel and relies on execpolicy+kernel sandbox for safety.
7. **Context preprocessing**: CC does a per-cycle 5-stage pipeline (boundary slice → tool-result budget → snip → microcompact → autocompact; `query.ts:362-449`). Codex per-cycle does **normalization only** (`for_prompt`→`normalize_history`, `history.rs:141`, `:359`: pair integrity + image strip; no compression) plus conditional reminders; tool outputs are truncated **once at record time** (`record_items` `history.rs:121` → `truncate_function_output_payload`; immutable afterward, originals unrecoverable — CC instead offloads overflow to disk); LLM-summarize-and-replace compaction fires **only at token limits** (`run_pre_sampling_compact` `turn.rs:815`, `run_auto_compact` `turn.rs:971`, `compact.rs`).
8. **KV caching** (the single biggest divergence): CC plants `cache_control: ephemeral` breakpoints client-side on 3 fronts (system prompt boundaries `claude.ts:3213-3234`, last tool schema `:1388`, exactly one message-level marker on the last message `addCacheBreakpoints` `:3063`, `:3089`, + `cache_reference` on tool_results). Codex plants **no breakpoints** — only `prompt_cache_key = session_id` (`client.rs:469-473`, `:888`) delegating to OpenAI Responses API server-side prefix caching. Codex history is append-only so the prefix stays stable; cache breaks only on events: auto_compact history replace, post-compact initial-context reinjection, normalize/image strip, rollback/fork, tool-list changes.
9. **PTC**: Codex has it as experimental **Code Mode** (`code-mode`, `code-mode-host`, `code-mode-protocol` crates + `core/src/tools/code_mode/`): single `exec` tool, model writes JavaScript run in a fresh V8 isolate (no Node/fs/net), tools exposed as `tools.*` with TypeScript type rendering, `store/load`, `yield_control()`+wait, `code_mode_only` flag. **Default remains function calling** for both systems.
10. **Harness location Q&A**: harness is 100% Rust in `codex-rs/core/src/` — `session/handlers.rs` (submission_loop) → `tasks/regular.rs` (RegularTask) → `session/turn.rs` (run_turn ★) → `client.rs` (Responses API streaming) → `tools/{router,parallel,orchestrator}.rs`; `tui`/`cli` are shells; CC's counterpart is concentrated in `CC/src/query.ts`.
11. **Codex-unique axes** (user worried they'd over-fit questions to CC's frame; asked for Codex-native concepts): stateful Responses API (`previous_response_id`, encrypted reasoning), 3-layer execution isolation (execpolicy Starlark → kernel sandbox Seatbelt/Landlock/bwrap → network-proxy egress MITM), **exec-server** remote/cross-OS tool execution relay, rollout JSONL + resume/fork + SQLite mirror, app-server single boundary, StepContext atomic per-request snapshot, world_state diff injection, agent-identity (cryptographic subagent identity), Code Mode. Explained exec-server rationale (target-OS parity / isolation / offload heavy work to cloud).

## Artifacts (tool state)
Surviving HTML at Codex repo root `/Users/seobi/jinsup_space/codex/` (untracked, **not committed** — user only said "move to root"):
- `codex-cc-loop-features.html` — draw-arch L/R feature comparison (6 features), light/dark aware
- `codex-multiTurn-flow.html` — Codex turn flow mirroring `/Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html` (same "auth.ts 버그 고쳐줘" scenario, teal palette)
- `codex-unique.html` — Codex-only designs, 6 diagram sections

**Lost** (session scratchpad was cleaned): `agent-arch-compare.html`, `agent-turn-pipeline.html`, `loop-computation-detail.html`, `codex-vs-cc-master.html` — user was offered rebuilds; no request yet.

Background subagents (resumable via SendMessage; both already hold deep codebase context): `a866be613de0d7112` = CC investigator, `ac9d5f4b9caa7652b` = Codex investigator. Two user questions were forked to separate background sessions and are still pending: (a) whether `previous_response_id` is usable by general API users, (b) plain-language glossary of the 3 sandbox mechanisms (Seatbelt/Landlock/bwrap).

## User Preferences & Constraints
- Reply in Korean; casual tone tolerated.
- Strong preference for **visual output** (diagrams/tables/HTML) over prose; minimize text in artifacts.
- Compare by **functional characteristics, not quantitative superiority** (was corrected twice on this).
- Focus on the **single main-agent pipeline**; multi-agent only as appendix.
- Keep teal(Codex)/coral(CC) color identity across artifacts; deliver HTML to repo root; do not commit.
- Do not force everything into CC's frame — surface Codex-native concepts too.
- `/draw-arch` skill in use for L/R comparison pages (light/dark required).

## What Remains To Be Done (next steps)
1. **Answer the pending final question** (conversation was cut here): "그 격리 만드는건 OpenAI 서버에서 하는거야? 아니면 내 컴퓨터에서 VM 띄우는거야?" — Per already-verified findings: Codex's default sandboxing is **local, kernel-level, in-process** (macOS Seatbelt / Linux Landlock/bwrap — OS mechanisms, not VMs, no OpenAI server involvement); remote isolation applies only when exec-server / Codex Cloud is used. Verify exact wording against `core/src` sandbox code before answering if needed.
2. Integrate the two forked background answers (`previous_response_id` availability; sandbox terminology) when they arrive.
3. Open offers the user may take up: deepen one Codex-unique axis (Responses API stateful flow / kernel sandbox stack / exec-server protocol) as a standalone visual; rebuild the 4 lost HTMLs; build an index page tying the 3 root HTMLs together.

## 단계 2: 요약 재주입 (SUMMARY_PREFIX + 요약 본문 — 교체 히스토리에 user 메시지로 저장되는 형태)

Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:

# CONTEXT CHECKPOINT COMPACTION — Handoff Summary

## Task Overview
The user (Korean speaker — all replies must be in Korean) is running a source-verified deep-dive comparing two coding-agent harnesses, producing diagram-heavy Korean HTML visualizations along the way:
- **Codex** (OpenAI, Rust): `/Users/seobi/jinsup_space/codex` — engine in `codex-rs/core/src/` (Cargo workspace, 148 crates)
- **Claude Code (CC)** (reverse-engineered TypeScript research repo): `/Users/seobi/jinsup_space/CC` (`src/` + `md_group/`)

Visual identity is fixed: **teal = Codex, coral = CC**.

## Current Progress & Key Decisions
Work proceeded through these completed phases (all claims below were verified against actual source by me or by two background subagents):

1. **Architecture survey**: Codex = single Rust engine (`codex-core`) behind `app-server` JSON-RPC boundary (Thread/Turn/Item); `codex-cli`(npm)/SDKs are thin wrappers; MCP is bidirectional; extension system is trait-based plugins.
2. **Multi-agent comparison** (first HTML): Codex = persistent bidirectional peer "mailbox" society (`Op::InterAgentCommunication`; spawn/send_message/followup_task/wait/interrupt/list under `core/src/tools/handlers/multi_agents_v2/`, `core/src/agent/{control,registry,role}.rs`, roles as TOML config layers) vs CC = one-shot fire-and-forget delegation (subagent returns one final text). User then **redirected: compare the single main-agent pipeline, not multi-agent**.
3. **Single-turn loop pipeline**: Codex `run_turn` (`core/src/session/turn.rs`) = Rust state machine + event emit; CC `queryLoop` (`src/query.ts:305`) = async-generator `while(true)` + yield. **Both terminate solely on presence of tool calls** — CC `needsFollowUp` (`query.ts:823-825`, `:1053`; stop_reason distrusted per comment `:549-551`), Codex `needs_follow_up = model_needs_follow_up || has_pending_input` (`turn.rs:328`; `end_turn` fallback `codex-api/common.rs:93-95`). Thinking/reasoning plays no role in loop control in either system.
4. **8-axis "computational meticulousness" comparison** (user's 8-step CC loop model checked): verdict = overall parity; Codex denser in tool execution/parallelism, CC denser in context/caching. Two corrections to the user's model: (a) CC's tool results are **eager-emit-in-order** (`StreamingToolExecutor.ts:412`, barrier at `:436-438`), not hold-and-batch — the real "withhold" pattern belongs to **Codex** (`in_flight: FuturesOrdered` queued during streaming, executed at `drain_in_flight` after Completed — `turn.rs:2143`, `:2493`, `:1907`); CC's `withheld` variable is error-recovery only (`query.ts:790-816`). (b) Continuation is never decided by thinking. Tool pipeline: CC 10 steps (`toolExecution.ts:337`→`:599`; zod→validateInput→backfill→PreToolUse hook→permission→call→result mapping→PostToolUse→assembly) vs Codex 12 steps (`orchestrator.rs:137`; approval→sandbox select→attempt→denied→re-approval→escalated retry).
5. **Smart rules / heuristics comparison** (user explicitly rejected quantitative "step count" framing — wants functional characteristics):
   - **Read→Edit enforcement**: CC = hard state gate `readFileState` (`FileEditTool.ts:275-287` errorCode 6; mtime staleness `:290-311` errorCode 7; also FileWriteTool/NotebookEditTool) + changed-file auto reminders (`attachments.ts:2063`). Codex = **no state gate at all**; `apply_patch` re-reads the file and validates patch context via `seek_sequence` 4-stage fuzzy matching (exact→rstrip→trim→Unicode normalization; `apply-patch/src/seek_sequence.rs:12`, `:76-107`). Slogan used: CC asks "읽었니?" (state tracking), Codex asks "정확히 아니?" (content matching).
   - **Conversation-aware tool skipping/dedup: neither system has it in code** — purely model-side soft behavior.
   - Codex-only: execpolicy Starlark DSL (`core/src/exec_policy.rs`), approval caching session + **persistent disk amendment** (`exec_policy.rs:409-440`), sandbox-denial escalation re-approval, MCP `read_only_hint` respected for parallelism, Unicode fuzzy patch, complex-parse auto-amendment block.
   - CC-only: AI permission classifier in auto mode (`permissions.ts:518-524`), 5-step permission chain (deny→ask→tool→bypass→alwaysAllow, `permissions.ts:1158`), Plan mode gate, Bash **dynamic** `isConcurrencySafe = isReadOnly(input)` (`BashTool.tsx:434`), path backfill doubling as hook-bypass security.
6. **Smart batching detail**: CC = static partition `partitionToolCalls` (`toolOrchestration.ts:91`; batches = single write OR consecutive read-only run; concurrency cap 10). Codex = **no batches**; per-tool `tokio::spawn` + dynamic `RwLock` gate (read=parallel/write=exclusive, `parallel.rs:131-137`); shell is **statically parallel=true regardless of command content** (`shell_command.rs:152`). Worked example `Read→Edit→Read→Read→Write`: identical schedule `[Read][Edit][Read‖Read][Write]` in both — but if the write is a shell command (e.g. `git push`), CC isolates it in a solo batch while Codex runs it in parallel and relies on execpolicy+kernel sandbox for safety.
7. **Context preprocessing**: CC does a per-cycle 5-stage pipeline (boundary slice → tool-result budget → snip → microcompact → autocompact; `query.ts:362-449`). Codex per-cycle does **normalization only** (`for_prompt`→`normalize_history`, `history.rs:141`, `:359`: pair integrity + image strip; no compression) plus conditional reminders; tool outputs are truncated **once at record time** (`record_items` `history.rs:121` → `truncate_function_output_payload`; immutable afterward, originals unrecoverable — CC instead offloads overflow to disk); LLM-summarize-and-replace compaction fires **only at token limits** (`run_pre_sampling_compact` `turn.rs:815`, `run_auto_compact` `turn.rs:971`, `compact.rs`).
8. **KV caching** (the single biggest divergence): CC plants `cache_control: ephemeral` breakpoints client-side on 3 fronts (system prompt boundaries `claude.ts:3213-3234`, last tool schema `:1388`, exactly one message-level marker on the last message `addCacheBreakpoints` `:3063`, `:3089`, + `cache_reference` on tool_results). Codex plants **no breakpoints** — only `prompt_cache_key = session_id` (`client.rs:469-473`, `:888`) delegating to OpenAI Responses API server-side prefix caching. Codex history is append-only so the prefix stays stable; cache breaks only on events: auto_compact history replace, post-compact initial-context reinjection, normalize/image strip, rollback/fork, tool-list changes.
9. **PTC**: Codex has it as experimental **Code Mode** (`code-mode`, `code-mode-host`, `code-mode-protocol` crates + `core/src/tools/code_mode/`): single `exec` tool, model writes JavaScript run in a fresh V8 isolate (no Node/fs/net), tools exposed as `tools.*` with TypeScript type rendering, `store/load`, `yield_control()`+wait, `code_mode_only` flag. **Default remains function calling** for both systems.
10. **Harness location Q&A**: harness is 100% Rust in `codex-rs/core/src/` — `session/handlers.rs` (submission_loop) → `tasks/regular.rs` (RegularTask) → `session/turn.rs` (run_turn ★) → `client.rs` (Responses API streaming) → `tools/{router,parallel,orchestrator}.rs`; `tui`/`cli` are shells; CC's counterpart is concentrated in `CC/src/query.ts`.
11. **Codex-unique axes** (user worried they'd over-fit questions to CC's frame; asked for Codex-native concepts): stateful Responses API (`previous_response_id`, encrypted reasoning), 3-layer execution isolation (execpolicy Starlark → kernel sandbox Seatbelt/Landlock/bwrap → network-proxy egress MITM), **exec-server** remote/cross-OS tool execution relay, rollout JSONL + resume/fork + SQLite mirror, app-server single boundary, StepContext atomic per-request snapshot, world_state diff injection, agent-identity (cryptographic subagent identity), Code Mode. Explained exec-server rationale (target-OS parity / isolation / offload heavy work to cloud).

## Artifacts (tool state)
Surviving HTML at Codex repo root `/Users/seobi/jinsup_space/codex/` (untracked, **not committed** — user only said "move to root"):
- `codex-cc-loop-features.html` — draw-arch L/R feature comparison (6 features), light/dark aware
- `codex-multiTurn-flow.html` — Codex turn flow mirroring `/Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html` (same "auth.ts 버그 고쳐줘" scenario, teal palette)
- `codex-unique.html` — Codex-only designs, 6 diagram sections

**Lost** (session scratchpad was cleaned): `agent-arch-compare.html`, `agent-turn-pipeline.html`, `loop-computation-detail.html`, `codex-vs-cc-master.html` — user was offered rebuilds; no request yet.

Background subagents (resumable via SendMessage; both already hold deep codebase context): `a866be613de0d7112` = CC investigator, `ac9d5f4b9caa7652b` = Codex investigator. Two user questions were forked to separate background sessions and are still pending: (a) whether `previous_response_id` is usable by general API users, (b) plain-language glossary of the 3 sandbox mechanisms (Seatbelt/Landlock/bwrap).

## User Preferences & Constraints
- Reply in Korean; casual tone tolerated.
- Strong preference for **visual output** (diagrams/tables/HTML) over prose; minimize text in artifacts.
- Compare by **functional characteristics, not quantitative superiority** (was corrected twice on this).
- Focus on the **single main-agent pipeline**; multi-agent only as appendix.
- Keep teal(Codex)/coral(CC) color identity across artifacts; deliver HTML to repo root; do not commit.
- Do not force everything into CC's frame — surface Codex-native concepts too.
- `/draw-arch` skill in use for L/R comparison pages (light/dark required).

## What Remains To Be Done (next steps)
1. **Answer the pending final question** (conversation was cut here): "그 격리 만드는건 OpenAI 서버에서 하는거야? 아니면 내 컴퓨터에서 VM 띄우는거야?" — Per already-verified findings: Codex's default sandboxing is **local, kernel-level, in-process** (macOS Seatbelt / Linux Landlock/bwrap — OS mechanisms, not VMs, no OpenAI server involvement); remote isolation applies only when exec-server / Codex Cloud is used. Verify exact wording against `core/src` sandbox code before answering if needed.
2. Integrate the two forked background answers (`previous_response_id` availability; sandbox terminology) when they arrive.
3. Open offers the user may take up: deepen one Codex-unique axis (Responses API stateful flow / kernel sandbox stack / exec-server protocol) as a standalone visual; rebuild the 4 lost HTMLs; build an index page tying the 3 root HTMLs together.
