## 단계 1: 사전 메모리 플러시 (FLUSH_SYSTEM_PROMPT 적용 산출물)

## Decisions & rationale
- **Comparison framing pivoted twice at user request**: started with Codex multi-agent architecture, but the user demanded (a) comparison on the basis of a *single main-agent turn pipeline* (not multi-agent), and later (b) *feature/characteristic* comparison of smart rules instead of quantitative "who has more steps" comparison. Future comparisons should lead with qualitative mechanism contrasts.
- **Visual-first deliverables**: user consistently wants diagram/table-heavy HTML ("택스트보단" 비주얼), produced via the `visual-explainer` and `/draw-arch` skills. Established design system: Codex = teal, Claude Code = coral, dark theme, Korean labels; draw-arch files must support light/dark auto.
- **Output location**: deliverable HTML files are kept at the codex repo root (`/Users/seobi/jinsup_space/codex/`), not in the session scratchpad — scratchpad temp files were lost to cleanup mid-session. Files are left uncommitted (they show as new files in `git status`).
- **Avoid CC-centric framing**: user explicitly worried that questions were too shaped by Claude Code's interface; Codex-unique designs (Responses API statefulness, kernel sandbox stack, exec-server, rollout/fork, StepContext, agent-identity) should be presented on their own terms.

## Technical context
- **Repos**: Codex = `/Users/seobi/jinsup_space/codex` (Rust, `codex-rs/` Cargo workspace of 148 crates; `codex-cli` npm launcher is a thin JS wrapper; `app-server` JSON-RPC Thread/Turn/Item boundary; persistence = rollout JSONL + SQLite). Claude Code research repo = `/Users/seobi/jinsup_space/CC` (reverse-engineering project, GitHub `LonerStayle/cc_agent_bible.git`, TS sources in `src/`, Korean docs in `md_group/`, reference HTML in `html_group_v2/`).
- **Codex harness location**: all in `codex-core` — `session/handlers.rs` (submission_loop), `session/turn.rs` (`run_turn` → `run_sampling_request` → `try_run_sampling_request`), `tasks/regular.rs` (`RegularTask::run`), `client.rs` (Responses API), `tools/{router,parallel,orchestrator}.rs`. CC counterpart is concentrated in `CC/src/query.ts` (`queryLoop`, async generator `while(true)`).
- **Loop termination (both systems)**: neither trusts `stop_reason`; continuation is decided purely by presence of tool calls — CC `needsFollowUp` (`query.ts:823-825`, `:1053`), Codex `needs_follow_up = model_needs_follow_up || has_pending_input` (`turn.rs:328`, plus `end_turn: Some(false)` forcing re-call). Thinking/reasoning is NOT involved in loop control in either system.
- **Tool result flow**: CC `StreamingToolExecutor` is *eager-emit-in-order* (starts tools mid-stream, emits results as they finish; the `withheld` variable at `query.ts:790-816` is error-recovery, not result batching). Codex is the actual *hold-then-batch*: tool calls are queued in `in_flight: FuturesOrdered` during streaming and executed/recorded in `drain_in_flight` after `Completed` (`turn.rs:1907/2493`, `stream_events_utils.rs:350-357`).
- **Parallelism**: CC = static partition (`partitionToolCalls`, `toolOrchestration.ts:91`; batches = single write tool or run of read-only tools; max concurrency 10; Bash judged dynamically via `isConcurrencySafe = isReadOnly(input)`, `BashTool.tsx:434`). Codex = no batches; per-tool `tokio::spawn` + shared `Arc<RwLock<()>>` gate (`parallel.rs:131-137`, read lock = parallel, write lock = exclusive); parallelism is a static per-tool declaration (`shell` always `true` at `shell_command.rs:152` regardless of command content; MCP tools honor `read_only_hint`, `handlers/mcp.rs:76-86`). Risk is handled at execution stage (execpolicy + kernel sandbox), not at partition stage.
- **Tool pipeline**: CC ~10 steps in `toolExecution.ts` (zod → validateInput → backfill → PreToolUse hooks → permission chain → call → result mapping → PostToolUse hooks → assembly). Codex 12 steps in `orchestrator.rs:137` (approval → sandbox select → attempt → on `SandboxErr::Denied` re-approval → escalated retry).
- **Edit safety**: CC = state gate (`readFileState`: "File has not been read yet" errorCode 6 at `FileEditTool.ts:275-287`; mtime staleness errorCode 7 at `:290-311`; auto `edited_text_file` reminders via `getChangedFiles`, `attachments.ts:2063`). Codex = no freshness/mtime tracking at all; `apply_patch` content matching via `seek_sequence` 4-stage fuzzy match (exact → rstrip → trim → Unicode punctuation normalization; `apply-patch/src/lib.rs:606,681,736,791`, `seek_sequence.rs:12,76-107`).
- **Context preprocessing**: CC runs a 5-layer pass every cycle (compact-boundary slice → `applyToolResultBudget` → snip → microcompact → autocompact, `query.ts:362-449`). Codex per-cycle does only normalization + reminders (`for_prompt`/`normalize_history`, `history.rs:141/359`: pair integrity + image strip); tool outputs are truncated ONCE at record time (`record_items`, `history.rs:121` → `truncate_function_output_payload`); LLM-summarization compaction only on token limit (`should_roll_over` `turn.rs:348`; `run_pre_sampling_compact:815`, `run_auto_compact:971`, `compact.rs`). No microcompact/snip equivalents.
- **Prompt/KV caching**: CC plants `cache_control: ephemeral` breakpoints client-side on 3 fronts (system prompt blocks `claude.ts:3213-3234`, last tool schema `:1388`, exactly one message-level marker on the last message `addCacheBreakpoints` `:3063/3089`, plus `cache_reference` on tool_results `:3187-3206`). Codex plants NO breakpoints — only `prompt_cache_key = session_id` (`client.rs:888/903/469-473`), relying on OpenAI server-side prefix caching; cache survives because history is append-only (record-time truncation + interval-gated `time_reminder.rs:71` appends); prefix breaks only on events: auto_compact full replace, post-compact `BeforeLastUserMessage` injection, image strip/normalize, rollback/fork, tool-list changes.
- **PTC equivalent**: Codex "Code Mode" (experimental; crates `code-mode`, `code-mode-host`, `code-mode-protocol`, `v8-poc`; `core/src/tools/code_mode/`). Single `exec` tool, model writes JavaScript run in a fresh V8 isolate (no Node/fs/net/console), tools exposed as global `tools.*` with auto-generated TS type declarations, `store/load` cross-call state, `yield_control()` + `wait`, `@exec` pragma. Default remains function calling (`code_mode_only: bool` flag).
- **Codex-unique designs (no CC counterpart)**: stateful Responses API (`previous_response_id`, encrypted reasoning), kernel sandbox stack (Seatbelt/Landlock/bwrap + Starlark execpolicy + network-proxy egress MITM), exec-server (remote/heterogeneous-OS tool execution), rollout JSONL + resume/fork + SQLite mirror, app-server single boundary, `StepContext` (atomic per-sampling-call snapshot of tools/env/AGENTS.md — `session/step_context.rs`), world_state diff injection, agent-identity (cryptographic subagent identity), tool_search + deferred tools (`handlers/tool_search.rs`, `ResponseItem::ToolSearchCall`).
- **Approval caching (Codex)**: session-scope `tool_approvals` store (`sandboxing.rs:71-114`) + persistent execpolicy amendment written to `default.rules` on disk (`exec_policy.rs:409-440`, `persist_execpolicy_amendment`), with `ApprovedCommandPrefixSaved` fragment; auto-amendment blocked for complex-parsed commands (`exec_policy.rs:291`).

## Debugging techniques & tools
- **Background subagent reuse via SendMessage**: after ToolSearch `select:SendMessage`, previously-run investigation agents (CC agent id `a866be613de0d7112`, Codex agent id `ac9d5f4b9caa7652b`) were resumed from transcript with follow-up questions instead of spawning fresh agents — preserving their loaded code context across three successive investigation rounds. Outputs land in `/private/tmp/claude-501/.../tasks/<id>.output` with `<task-notification>` on completion.
- **Absence proof by grep**: confirming a feature does NOT exist by grepping for its vocabulary (`mtime|stale|last_read|has_been_read` → no freshness tracking in Codex; `cache_control|CacheControl|addCacheBreakpoint` → no client-side cache breakpoints; `dedup|duplicate|skip` → no conversation-based tool skipping in either system).
- **Verification tags in subagent reports**: [확정] (source line directly confirmed) vs [추론] markers keep claims honest across large multi-file investigations.

## Problems & solutions
- **User misconception corrections (CC loop)**: (1) "withhold then batch-release of tool results" is wrong for CC — it eager-emits in order; the real `withheld` variable is error-message recovery; ironically the hold-then-batch behavior belongs to Codex (`drain_in_flight`). (2) "thinking decides whether to continue" is wrong — only tool_use presence (`needsFollowUp`) controls the loop.
- **Rejected subagent call**: an early Agent spawn was rejected by the user mid-flight; recovered by reading Codex agent files directly in the main session after the user switched model (/model → Opus 4.8 1M) and said "이어서해".
- **Generated-HTML typos**: `--muted:#8persist;` CSS corruption in agent-arch-compare.html and `stroke="#3a4counter"` + duplicate rect in loop-computation-detail.html — both fixed by targeted Edit.
- **Scratchpad volatility**: 4 of 5 scratchpad HTMLs (multi-agent compare / turn pipeline / 8-axis computation / master synthesis) vanished when the temp folder was cleaned; only the latest survived and was moved to the repo root. Fix: write deliverables directly to `/Users/seobi/jinsup_space/codex/` from then on.
- **"Truncation breaks KV cache?" concern resolved**: no — Codex truncates once at append time (the truncated item immediately becomes stable prefix), never re-cutting past items; re-cutting history mid-stream (CC's per-cycle budget pass) is the cache-hostile pattern, which CC mitigates via explicit cache_control management.

## 단계 1b: 증분 플러시

(해당 없음 — 이 세션의 첫 플러시이므로 FLUSH_DELTA_SYSTEM_PROMPT는 적용되지 않음.)

## 단계 2: 풀 리플레이스 컴팩션 (구조화 요약 프롬프트 산출물)

<summary>
1. Primary Request and Intent:
The user is investigating the OpenAI Codex repository (`/Users/seobi/jinsup_space/codex`, Rust) and comparing it against a Claude Code reverse-engineering research repo (`/Users/seobi/jinsup_space/CC`, TypeScript), in Korean, with strong preference for visual/diagram-heavy HTML deliverables over text. The request evolved through these phases:
- Initial: explain Codex's overall architecture, then its agent (sub-agent/multi-agent) logic, comparing against Claude Code with `/visual-explainer`.
- Major correction #1: "제발 멀티에이전트기준으로 얘기하지말고.. 하나의 메인에이전트 파이프라인 기준으로 비교해봐" — compare on the basis of a single main-agent turn pipeline, not multi-agent.
- Then: verify whether Codex's loop is as "계산적" (mechanically calculated) as the user's 8-step mental model of Claude Code's loop (전처리 → 위드홀드 → 스마트배치 → 10단계 도구 파이프라인 → tool_results+어태치먼트 묶음 → 다음 사이클 전처리 → system-reminder 과다 전송+KV캐싱 → thinking 판단); visualize all results without omission.
- Major correction #2: stop quantitative "who has more steps" comparison; compare functional *characteristics* of smart rules/heuristics (e.g., CC's Read→Edit hard rule, soft tool-ordering rules, conversation-aware skipping), then synthesize everything into one visual-heavy master HTML.
- Identity/clarification questions: is Codex a frontend? where is the harness logic? what language? does Codex have PTC (programmatic tool calling)? is it not function-calling based?
- Via `/draw-arch`: check whether Codex has 툴서치/도구스마트배치/도구10단계파이프라인/컨텍스트전처리/시스템리마인더/KV캐싱준수, plus concepts existing in only one system; move the resulting HTML to the repo root.
- Deep-dives: how `for_prompt` + `auto_compact` work vs CC's 5-stage preprocessing; recreate CC's `multiTurn-flow.html` as a Codex version; does Codex have equivalent smart batching; walk through a concrete `Read, Edit, Read, Read, Write` tool sequence in both systems; does Codex's KV caching break often; does Codex do context preprocessing at all; what "기록 시점" (record time) means; whether record-time truncation breaks KV caching.
- Reframing request: the user worried the questions were too CC-interface-shaped and asked for Codex-unique concepts ("코덱스만의 무언가"), then asked to render those as a diagram-first HTML.
- Latest: "StepContext 이건 뭐야? 스텝 컨테스트? 한번의 모델 호출?" — explain what StepContext is.
Constraints/preferences: answer in Korean; visual > text; no invented claims (source-verified with file:line); deliverables at codex repo root; don't force everything through Claude Code's frame.

2. Key Technical Concepts:
- Codex: `codex-rs` 148-crate Cargo workspace; `codex-core` engine; `app-server` JSON-RPC (Thread/Turn/Item) single boundary; TUI(ratatui)/CLI shells; rollout JSONL + SQLite persistence; resume/fork.
- Main loop: `Op::UserInput` → `RegularTask` → `run_turn` loop → `run_sampling_request` → `try_run_sampling_request`; Rust state machine + event channel emit; vs CC `queryLoop` async generator `while(true)` + yield (`query.ts`).
- Loop continuation: both ignore `stop_reason`; CC `needsFollowUp` (tool_use presence only), Codex `needs_follow_up = model_needs_follow_up || has_pending_input` (+ `end_turn: Some(false)` force re-call); thinking/reasoning NOT involved in either.
- Tool-result timing: CC eager-emit-in-order (`StreamingToolExecutor`; `withheld` var = error recovery, not batching); Codex hold-then-batch (`in_flight: FuturesOrdered` → `drain_in_flight` after stream `Completed`).
- Parallelism: CC static partition (`partitionToolCalls`, batches of consecutive read-only tools, max 10, Bash dynamic `isConcurrencySafe`); Codex dynamic `Arc<RwLock<()>>` gate (read=parallel/write=exclusive), per-tool static declaration (`shell` always parallel), MCP `read_only_hint`.
- Tool pipeline: CC ~10 steps (zod → validateInput → backfill → PreToolUse hook → permission chain → call → result mapping → PostToolUse hook → assembly); Codex 12 steps (approval → sandbox selection → attempt → denied → re-approval → escalated retry) in `ToolOrchestrator::run`.
- Edit safety: CC `readFileState` state gate (not-read errorCode 6 / mtime-stale errorCode 7) + `edited_text_file` auto reminders; Codex `apply_patch` `seek_sequence` 4-stage content matching (exact → rstrip → trim → Unicode normalization), no freshness tracking.
- Context management: CC per-cycle 5-layer (boundary slice → tool-result budget → snip → microcompact → autocompact); Codex `for_prompt` normalization only + record-time truncation (`TruncationPolicy`) + threshold-only LLM `auto_compact` (pre-turn and mid-turn; local/remote/remote_v2).
- Prompt/KV caching: CC client-side `cache_control: ephemeral` breakpoints on 3 fronts + `cache_reference`; Codex `prompt_cache_key = session_id` only, server-side automatic prefix caching, append-only history keeps prefix stable; break events = auto_compact replace, post-compact injection, normalize/image strip, rollback/fork, tool-list changes.
- System reminders: CC attachments (`edited_text_file`, `todo_reminder`, `task_reminder`, `plan_mode*`, `critical_system_reminder`, `verify_plan_reminder`, `compaction_reminder`, `relevant_memories`) + `<system-reminder>` wrap; Codex `ContextualUserFragment` independent items (time_reminder interval-gated, world_state diff, token budget reminders).
- Safety: Codex kernel sandbox (Seatbelt/Landlock/bwrap) + execpolicy Starlark DSL (`Decision::{Allow,Prompt,Forbidden}`, PrefixRule/HeuristicsRule/NetworkRule) + network-proxy egress + approval caching (session + persistent `default.rules` amendment); CC permission chain (deny → ask → tool.checkPermissions → bypass → alwaysAllow), dontAsk/auto modes (auto = AI classifier side_query), Plan mode gate, hooks.
- PTC: Codex "Code Mode" (experimental) — single `exec` tool, model-written JavaScript in fresh V8 isolate (no Node/fs/net/console), global `tools.*` with TS type declarations, `store/load`, `yield_control()` + `wait`, `@exec` pragma; default remains function calling (`code_mode_only` flag).
- Codex-unique: stateful Responses API (`previous_response_id`, encrypted reasoning), exec-server remote/heterogeneous-OS execution, StepContext atomic snapshot, world_state diff, agent-identity, tool_search + deferred tools, Code Mode.
- Multi-agent (early phase): Codex peer "society" with first-class bidirectional mailbox (`Op::InterAgentCommunication`; send_message/followup_task/wait/interrupt/list_agents; role TOML config layers; spawn depth limits) vs CC one-shot unidirectional delegation (Task tool, final text return; SendMessage = opt-in file mailbox layer).
- Harness skills used: `visual-explainer`, `/draw-arch`; design system teal(Codex)/coral(CC); background agent reuse via `SendMessage` after `ToolSearch`.

3. Files and Code Sections:
Codex sources examined directly (all under `/Users/seobi/jinsup_space/codex/codex-rs/`):
- `core/src/agent/{mod.rs, registry.rs, agent_resolver.rs, status.rs, role.rs, control.rs}`, `core/src/agent/builtins/awaiter.toml`, `core/src/session/multi_agents.rs` — multi-agent v2 subsystem (AgentControl, spawn depth limit, role config layering, status-from-event derivation).
- `core/src/tools/handlers/multi_agents_v2/{spawn.rs, message_tool.rs, interrupt_agent.rs, wait.rs, list_agents.rs}` — v2 agent tools; send_message/followup_task share one submission path.
- `core/src/session/turn.rs` — harness heart: `run_turn` preprocessing order (:227-298), `needs_follow_up` (:328), `should_roll_over` (:348), `run_pre_sampling_compact` (:815), `run_auto_compact` (:971), `drain_in_flight` (:1907/:2493).
- `core/src/context_manager/history.rs` — `for_prompt` (:141), `normalize_history` (:359), `record_items` (:121-135, record-time truncation).
- `core/src/compact.rs` — LLM summarization compaction (SUMMARIZATION_PROMPT, history replace).
- `core/src/session/time_reminder.rs` — `take_reminder_due` (:71): interval-gated, append-only time reminders.
- `core/src/tools/parallel.rs` — `ToolCallRuntime`, RwLock gate; core pattern:
```rust
tokio::spawn(async {
    let _guard = if supports_parallel { lock.read().await }   // parallel
                 else { lock.write().await };                 // exclusive
    router.dispatch(...)
});
```
- `core/src/tools/handlers/shell/shell_command.rs` — `fn supports_parallel_tool_calls(&self) -> bool { true }` (:152) — static, command-content-blind.
- `core/src/tools/code_mode/execute_spec.rs`, `code-mode/src/lib.rs`, `code-mode-protocol/src/description.rs` — Code Mode ("Run JavaScript code to orchestrate/compose tool calls", `code_mode_only: bool`).
- `core/src/session/step_context.rs` — StepContext; read begun at conversation cutoff (imports observed: `LoadedAgentsMd`, `TurnEnvironmentSnapshot`, `McpRuntimeSnapshot`, `TurnContext`, `ResolvedSelectedCapabilityRoot`, `codex_mcp::ToolInfo`).
- `core/src/client.rs` — `prompt_cache_key` (:888/:903, key fn :469-473 = override or `responses_metadata.session_id`), WebSocket session caching.
Codex sources verified via subagents: `tools/orchestrator.rs` (12-step run, :137, escalation :294-469), `tools/sandboxing.rs` (:71-114 approval cache), `core/src/exec_policy.rs` (:280-440), `apply-patch/src/lib.rs` (:606/:681/:736/:791) + `apply-patch/src/seek_sequence.rs` (:12/:76-107), `stream_events_utils.rs` (:346/:350-357), `session/token_budget.rs`, `tools/router.rs` (:99), `tools/registry.rs` (:271/:385), `handlers/mcp.rs` (:76-86), `handlers/tool_search.rs`.
CC sources verified via subagents (under `/Users/seobi/jinsup_space/CC/src/`): `query.ts` (loop :305, preprocessing :362-449/:632, withheld :790-816, needsFollowUp :823-825/:1053, reassembly :1704), `claude.ts` (getCacheControl :358-374, addCacheBreakpoints :3063-3206, buildSystemPromptBlocks :3213), `toolOrchestration.ts` (:8-152), `toolExecution.ts` (:337-1568), `StreamingToolExecutor.ts` (:412/:436-438), `FileEditTool.ts` (:275-311/:520), `FileReadTool.ts` (:842-844), `FileWriteTool.ts` (:198-203/:332), `NotebookEditTool.ts` (:221-226), `permissions.ts` (:1158-1296/:400-524), `messages.ts` (:1481/:2069-2286), `attachments.ts` (:452-672/:2063-2122/:2937), `prompts.ts` (:301-310/:438/:770), `BashTool.tsx` (:434).
Reference file: `/Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html` (structural template for the Codex version).
Files created (HTML deliverables, all Korean, dark/teal-coral design):
- Lost to scratchpad cleanup (previously at `/private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/scratchpad/`): `agent-arch-compare.html` (multi-agent mesh vs tree), `agent-turn-pipeline.html` (single-turn pipeline), `loop-computation-detail.html` (8-axis computation), `codex-vs-cc-master.html` (master synthesis), `tool-smart-rules.html` (smart-rule features).
- Surviving at repo root: `/Users/seobi/jinsup_space/codex/codex-cc-loop-features.html` (draw-arch 좌/우, 6 loop features + one-side-only concepts; moved from scratchpad, 10,557 bytes), `/Users/seobi/jinsup_space/codex/codex-multiTurn-flow.html` (Codex INIT→LOOP→심화→RESULT→REF flow, "auth.ts 버그 고쳐줘" example), `/Users/seobi/jinsup_space/codex/codex-unique.html` (6 Codex-unique axes). All uncommitted.
Background agent outputs: `/private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/tasks/{a866be613de0d7112,ac9d5f4b9caa7652b}.output` (CC agent, Codex agent — resumable via SendMessage).

4. Errors and Fixes:
- Early `Agent` spawn for sub-agent investigation was rejected by the user ("The user doesn't want to proceed with this tool use... STOP") and the request interrupted; the user then ran `/model` (set to Opus 4.8, 1M context) and said "이어서해". Fix: read Codex agent files directly in the main session instead of the rejected subagent.
- CSS typo `--muted:#8persist;` left in `agent-arch-compare.html` → fixed with a targeted Edit.
- SVG typo `stroke="#3a4counter"` + duplicated rect in `loop-computation-detail.html` → fixed with a targeted Edit.
- zsh glob "no matches found: /Users/seobi/jinsup_space/codex/*.html" when checking for existing root HTMLs → interpreted as "no HTML at root", proceeded with `mv`.
- Scratchpad temp cleanup deleted 4 earlier HTML deliverables (only the newest survived); acknowledged to the user with an offer to recreate; subsequent deliverables written directly to the repo root.
- User-feedback corrections (treated as course corrections, verbatim): "제발 멀티에이전트기준으로 얘기하지말고.. 하나의 메인에이전트 파이프라인 기준으로 비교해봐 ㅠㅜ"; "각 단계 파이프라인을.. 뭔가 양으로 우위 비교하지말구... 특징을 비교해야지"; "내가 클로드코드 기준으로 얘기했지만 너무 그인터페이스에 맞춰서 질문한거 같아서 걱정이야 코덱스만의 무언가는 뭐없나?".
- Corrections of the user's mental model (delivered as findings): CC's "withhold then batch" is actually eager-emit-in-order (the real `withheld` var is error recovery for prompt-too-long/max-output-tokens); loop continuation is decided by `needsFollowUp`/tool_use presence only, never by thinking.

5. Problem Solving:
- Established, source-verified, that both harnesses share the same skeleton (assemble → call → parse → tools → append → re-call; terminate when no tool calls) while differing in flesh: Codex = Rust state machine, OpenAI Responses API, kernel-sandbox safety; CC = TS async generator, Anthropic Messages API, policy/hook safety.
- 8-axis "computational sophistication" verdict: 4 axes equal; tool pipeline (12 vs 10) and parallel gating denser in Codex; attachments variety and KV-caching client control denser in CC; the only fundamental gap is caching (client `cache_control` breakpoints vs server-side `prompt_cache_key`), an API-design difference. Two reversals surfaced: hold-then-batch belongs to Codex, not CC; Codex's tool pipeline is longer.
- Smart-rule characterization: CC embeds intelligence in *state tracking* (readFileState/mtime gate, AI permission classifier, Bash command parsing, path backfill), Codex in *content/policy verification* (seek_sequence patch matching, Starlark execpolicy, sandbox escalation, persistent approval amendment); neither has conversation-based tool skipping/dedup (confirmed by grep).
- Concrete `Read, Edit, Read, Read, Write` walk-through: CC produces 4 static batches `[Read][Edit][Read‖Read][Write]`; Codex's dynamic locks yield the same schedule for this case; divergence案 shown: replace Edit with `Bash("git push")` — CC isolates it, Codex runs it in parallel and relies on execpolicy/sandbox.
- KV-cache stability analysis: Codex's append-only history + record-time single truncation keeps prefix stable (cache breaks only on compact/fork/tool-list events); resolved the user's worry that record-time truncation would break caching (it is precisely what protects it).
- Codex-unique axes identified and visualized to escape the CC frame: stateful Responses API, 3-layer execution isolation, exec-server, rollout+resume/fork, app-server boundary, StepContext/world_state/agent-identity/Code Mode.
- In progress: explaining StepContext from `session/step_context.rs` (read begun; earlier characterized as "'한 번의 모델 호출'에 도구·환경·AGENTS.md를 원자 스냅샷으로 고정").

6. All User Messages:
- "코덱스 아키텍처가 어떻게돼?"
- "에이전트 로직이 어떻게 되는데?"
- "[Request interrupted by user for tool use]"
- "[슬래시커맨드 /model]" (+ stdout: Set model to Opus 4.8 (1M context) and saved as default)
- "이어서해"
- "제발 멀티에이전트기준으로 얘기하지말고.. 하나의 메인에이전트 파이프라인 기준으로 비교해봐 ㅠㅜ"
- "❯ 루프적인 모습을봐야지 클로드코드는 전처리 -> 위드홀드패턴 + (LLM호출) -> 도구 스마트배치 세팅 -> 도구 10단계 파이프라인 진행 -> 전체 배치완료 후 tool_results 묶음, 적절한 어태치먼트 삽입 -> 다음 사이클 컨텍스트전처리 -> 전체적인 tool_results + 어태치먼트및 시스템리마인드 과다 전송(이때 KV캐싱 구성) -> 이어서할지말지 thinking 에서 판단 / 이렇단 말야 그록도 이렇게 엄청 디테일하게 루프가 계산적이냐구;"
- "방금 결과들 빠짐없이 /visual-explainer 로 줘"
- "음... 각 단계 파이프라인을.. 뭔가 양으로 우위 비교하지말구... 흐...흠... 특징을 비교해야지  클로드코드의 도구 배치 세팅할때 그 Read -> Edit 강제 하드규칙이나 그외 툴콜링순서 소프트규칙이있기도하고 그러거든.. 클로크돜드가 대화세션보고 뛰어넘길때도 있고 .. 아무튼 이러한 스마트 기능들이있는지 알고싶어"
- "구 얘기로 한건 예를든건데 아무튼 다양한 스마트특징들과 이전 대화에서 내가 요청한클로드코드 비교 대조해서  잘 비교를해봐 가능하면 html을 비주얼쪽으로 작성잘해줘 택스트보단.."
- "/draw-arch" (slash command)
- "Codex는 프론트엔드야?"
- "아니 하네스로직이 어딨냐구"
- "언어는 뭔데?"
- "코덱스에 PTC를 호출하는게 있어? 프로그래매틱 도구 호출"
- "펑션콜링 기반 에이전트가 아니었구나?"
- "코덱스에도 툴서치, 도구스마트배치, 도구10단계파이프라인, 컨텍스트전처리, 시스템 리마인더,KV캐싱준수  같은게 있어? 비교해주고 그 그리고 클로드코드외에 없는 개념도 알려주러 /draw-arch"
- "루트로 옮겨줘"
- "for_prompt + auto_compact 이건 어떻게 하고있대? cc 는 전처리 5단계있잖아"
- "클로드코드에 @/Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html 이거처럼 코덱스도 한번 정리해볼래?"
- "스마트 배치가 같은게 있어?"
- "어... 예시를 좀더들어주라 뭐 도구가 Read, Edit, Read,Read, Write  이렇게 모델이 내뱉었을때 어떤식으로 각각 되는지?"
- "그리고 코덱스는 KV캐싱이 깨지는구간이 많아?"
- "코덱스는 그리고 그 컨텍스트전처리는 안해?"
- "기록 시점 이라는게 뭐지?"
- "도구결과 절단 저렇게 하면 KV캐싱 깨지지않니? ㄷㄷ 그리고 내가 클로드코드 기준으로 얘기했지만 너무 그인터페이스에 맞춰서 질문한거 같아서 걱정이야 코덱스만의 무언가는 뭐없나?"
- "그걸 최대한 도표나 이미지 위주로 html으로 만들어줘"
- "StepContext 이건 뭐야? 스텝 컨테스트? 한번의 모델 호출?"
(Task-notification messages carrying background-agent results are tool results and are excluded.)

7. Pending Tasks:
- Answer the user's latest question: explain what `StepContext` is (whether it corresponds to "one model call"), based on `codex-rs/core/src/session/step_context.rs`.
- (Standing, implicit) Offers not yet accepted — recreating the 4 lost scratchpad HTMLs, an index page binding the deliverables, deeper single-axis dives — should not be acted on without user confirmation.

8. Current Work:
Immediately before this summary, the user asked "StepContext 이건 뭐야? 스텝 컨테스트? 한번의 모델 호출?" (a follow-up to `codex-unique.html`, which listed StepContext as a Codex-unique concept described as "'한 번의 모델 호출'에 도구·환경·AGENTS.md를 원자 스냅샷으로 고정"). I replied "StepContext, 정확히 코드로 확인해서 답하겠습니다." and issued a Read of `/Users/seobi/jinsup_space/codex/codex-rs/core/src/session/step_context.rs`. Only the head of the file arrived before cutoff — imports visible: `crate::agents_md::LoadedAgentsMd`, `crate::environment_selection::TurnEnvironmentSnapshot`, `crate::session::McpRuntimeSnapshot`, `crate::session::turn_context::TurnContext`, `codex_exec_server::ResolvedSelectedCapabilityRoot`, `codex_mcp::ToolInfo`. Known related context: `capture_step_context` runs in `run_turn` preprocessing (`turn.rs:250-253`, reusing `next_step_context` when present), and the sampling input is assembled from it.

9. Optional Next Step:
Finish reading `codex-rs/core/src/session/step_context.rs` and answer the user's question — define StepContext precisely (what it snapshots: tools/MCP runtime, environment, AGENTS.md, exec-server capability roots, per-sampling-request scope; whether "한 번의 모델 호출" per the user's guess is accurate; when it is captured vs reused in `run_turn`). Direct quotes anchoring the resumption point: user — "StepContext 이건 뭐야? 스텝 컨테스트? 한번의 모델 호출?"; my last words — "StepContext, 정확히 코드로 확인해서 답하겠습니다." with the Read of `step_context.rs` already issued.
</summary>

## 단계 2 대안: 짧은 자기요약 (SELF_SUMMARIZATION_PROMPT)

(수행 안 함 — short-prompt 하네스 전용 대체 경로로, grok-build 기본 경로는 단계 2의 구조화 요약 프롬프트를 사용함.)

## 단계 3: 재주입 캐리어 텍스트 (하네스 조립 결과)

This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
(단계 2의 `<summary>` 본문이 여기에 스플라이스됨 — 치환 변수 `{cleaned}` 자리)

(transcript/segments 모드 힌트의 `{loc}` 치환 변수는 시뮬레이션 규칙에 따라 무시함.)

## 단계 4: 장기 메모리 통합 (DREAM_SYSTEM_PROMPT 산출물)

## Codex vs Claude Code — engine identity
Codex (`/Users/seobi/jinsup_space/codex`) is a Rust CLI coding agent: 148-crate `codex-rs` Cargo workspace, `codex-core` engine behind an `app-server` JSON-RPC (Thread/Turn/Item) boundary, TUI(ratatui)/CLI shells, `codex-cli` npm package is only a thin JS binary launcher, persistence via rollout JSONL + SQLite with resume/fork. Claude Code's harness (per the reverse-engineering repo `/Users/seobi/jinsup_space/CC`, GitHub `LonerStayle/cc_agent_bible.git`) concentrates in `src/query.ts` (`queryLoop`). Codex speaks the stateful OpenAI Responses API; Claude Code speaks the stateless Anthropic Messages API — many downstream design differences trace to this split.

## Single-turn agentic loop
Both harnesses share one skeleton: assemble prompt → call model → parse stream → run tools → append results → re-call; both terminate solely on the absence of tool calls (CC `needsFollowUp`, Codex `needs_follow_up` + `end_turn` signal) and neither trusts `stop_reason` nor consults thinking/reasoning for loop control. Implementation contrast: Codex = Rust state machine with event-channel emits (`session/turn.rs` `run_turn` → `try_run_sampling_request`); CC = async generator `while(true)` + yield. Tool-result timing is reversed from intuition: CC eager-emits results in order during streaming (its `withheld` variable is error recovery, not batching), while Codex queues calls in `FuturesOrdered` and executes/records them in `drain_in_flight` after the stream completes — the true hold-then-batch.

## Tool execution and parallelism
CC: static pre-partition (`partitionToolCalls`) into batches (single write tool or run of consecutive read-only tools), max concurrency 10, Bash judged per-command via `isConcurrencySafe = isReadOnly(input)`; ~10-step per-tool pipeline (zod → validateInput → backfill → PreToolUse hooks → permission chain deny→ask→tool→bypass→alwaysAllow → call → result mapping → PostToolUse hooks → assembly); auto permission mode uses an AI classifier (side_query). Codex: no batches — each tool spawns and takes a shared RwLock (read = parallel, write = exclusive); parallel capability is a static per-tool declaration (`shell` always true, content-blind; MCP tools honor `read_only_hint`); 12-step `ToolOrchestrator::run` adds approval → kernel sandbox selection → attempt → denied → re-approval → escalated retry. Philosophy: CC front-loads safety at partition time; Codex lets tools run loose and contains risk at execution time (execpolicy + sandbox). Neither system skips or dedups tool calls based on conversation content (grep-confirmed absent in both).

## Edit-safety mechanisms
Same guarantee, opposite mechanisms. CC asks "읽었니?": a `readFileState` state gate rejects Edit/Write before execution if the file wasn't Read in-conversation (errorCode 6) or changed on disk since (mtime, errorCode 7), plus automatic `edited_text_file` change reminders each turn. Codex asks "정확히 아니?": no freshness/mtime tracking exists; `apply_patch` re-reads the file every time and requires patch context to match current content via `seek_sequence`'s 4-stage fuzzy match (exact → rstrip → trim → Unicode punctuation normalization), rejecting on mismatch.

## Context management and prompt caching
CC grooms context every cycle with a 5-layer pass (compact-boundary slice → per-tool-result budget with disk spill → snip → microcompact → LLM autocompact) and plants client-side `cache_control: ephemeral` breakpoints on three fronts (system-prompt block boundaries, last tool schema, exactly one message-level marker on the last message, plus `cache_reference` on tool_results). Codex does per-cycle normalization only (`for_prompt`: call/output pair integrity + image strip), truncates tool outputs once at record time (`record_items` + TruncationPolicy — the truncated item immediately becomes stable prefix, no original retained), and compacts only at token limits via LLM summarization that replaces history (pre-turn and mid-turn variants). Codex plants no cache breakpoints — just `prompt_cache_key = session_id` for server-side prefix caching — and protects cache hits structurally by keeping history append-only (interval-gated time reminders append; nothing edits the middle). Codex cache prefix breaks only on events: auto_compact replace, post-compact context injection, normalize/image strip, history rollback/fork, tool-list changes. Record-time truncation does not hurt caching; per-cycle re-truncation of past items (CC's pattern) is what requires active cache management.

## Programmatic tool calling (Code Mode)
Codex's PTC equivalent is the experimental "Code Mode" (`code-mode`, `code-mode-host`, `code-mode-protocol`, `v8-poc` crates; `core/src/tools/code_mode/`): a single `exec` tool where the model writes JavaScript executed in a fresh V8 isolate (no Node/fs/network/console), tools exposed as global `tools.*` with auto-generated TypeScript declarations, `store/load` cross-call state, `yield_control()` + `wait` for long runs, `@exec` pragma options. Both Codex and Claude Code remain function-calling agents at the root; code-orchestration modes are optional token-saving layers (`code_mode_only` flag in Codex).

## Codex-unique designs (no CC counterpart)
Stateful Responses API usage (`previous_response_id`, encrypted reasoning content, WebSocket session reuse); 3-layer execution isolation (Starlark execpolicy → kernel sandbox Seatbelt/Landlock/bwrap → network-proxy egress MITM) with approval caching both session-scoped and persisted to `default.rules` on disk (auto-amendment blocked for complex-parsed commands); exec-server for remote/heterogeneous-OS tool execution; rollout JSONL + resume/fork with SQLite mirror; app-server as the single external boundary; `StepContext` — an atomic per-sampling-call snapshot of tools/MCP runtime/environment/AGENTS.md (`session/step_context.rs`); world_state diff injection; agent-identity (cryptographic subagent identity); `tool_search` with deferred tools. CC-unique counterweights: readFileState gate, client-controlled cache_control, AI permission classifier, Plan mode, rich attachment/reminder taxonomy.

## Multi-agent architectures
Codex implements a persistent peer "society": spawned agents are full threads with a first-class bidirectional mailbox (`Op::InterAgentCommunication`; tools send_message/followup_task/wait/interrupt/list_agents), TOML role config layers applied at spawn, and spawn-depth limits. Claude Code's default is one-shot unidirectional delegation (subagent returns a single final text); bidirectional messaging is an opt-in file-mailbox layer. Metaphor used throughout the deliverables: Codex = teal mesh network, Claude Code = coral delegation tree.

## Project deliverables and working conventions
Comparison deliverables are Korean, diagram-first HTML using a fixed teal(Codex)/coral(CC) design system, built via visual-explainer and /draw-arch. Surviving artifacts live uncommitted at the codex repo root: `codex-cc-loop-features.html` (loop-feature 좌/우 비교), `codex-multiTurn-flow.html` (Codex turn flow mirroring CC's `html_group_v2/multiTurn-flow.html`), `codex-unique.html` (Codex-only designs). Session-scratchpad HTMLs proved volatile (four earlier files were lost to temp cleanup) — write deliverables to the repo, not the scratchpad. Long investigations reuse background subagents via SendMessage resume so their loaded code context carries across follow-up rounds; nonexistence claims are established by targeted grep (e.g., no `cache_control`, no `mtime`/freshness tracking, no tool dedup in Codex).
