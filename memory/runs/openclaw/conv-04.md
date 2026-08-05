# openclaw 컴팩션 시뮬레이션 — conv-04

## 단계 1: 사전 메모리 플러시 (단계 1b system 프롬프트 동일 턴 적용)

`memory/YYYY-MM-DD.md` 에 APPEND 할 내용:

```markdown
## Codex vs Claude Code 하네스 비교 리서치 세션

### 레포/대상
- Codex: /Users/seobi/jinsup_space/codex — Rust cargo workspace `codex-rs` (crate 148개), npm 런처 `codex-cli`(@openai/codex)는 얇은 wrapper. 하네스 심장 = codex-rs/core/src/session/turn.rs 의 run_turn.
- Claude Code 분석 레포: /Users/seobi/jinsup_space/CC (리버스 엔지니어링 리서치, 원격 LonerStayle/cc_agent_bible.git). 하네스 = CC/src/query.ts 의 queryLoop.
- /model 로 기본 모델 Opus 4.8 (1M context) 설정됨.

### 산출물 (HTML, 전부 소스 검증 기반)
- 레포 루트(미커밋, git 새 파일): /Users/seobi/jinsup_space/codex/codex-cc-loop-features.html (10557 bytes, 8 1 11:03), codex-multiTurn-flow.html, codex-unique.html
- scratchpad(/private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/scratchpad)에 만들었던 agent-arch-compare.html / agent-turn-pipeline.html / loop-computation-detail.html / tool-smart-rules.html / codex-vs-cc-master.html 은 임시 폴더 정리로 소실 (복원 여부 사용자 미결정).
- 참조 원본: /Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html
- 디자인 규약: Codex=teal / Claude Code=coral, 텍스트 최소·다이어그램 위주.

### 핵심 결론 (소스 교차검증)
- 두 하네스 모두 루프 종료는 stop_reason 아닌 도구 호출 유무(needsFollowUp / needs_follow_up). thinking 은 루프 제어 무관.
- 정교함 무게중심: Codex=도구 실행·안전(12단계 orchestrator, RwLock 동적 병렬, 커널 샌드박스+execpolicy Starlark), CC=컨텍스트·캐싱(매 사이클 5단계 전처리, cache_control breakpoint 3전선, readFileState 게이트).
- "hold-then-batch"는 CC가 아니라 Codex(in_flight FuturesOrdered → drain_in_flight); CC는 eager-emit-in-order.
- Read→Edit 강제: CC=readFileState+mtime 상태 게이트(하드), Codex=apply_patch seek_sequence 4단계 content 매칭이 대체. 대화 기반 도구 스킵/dedup 은 양쪽 다 없음.
- Codex 컨텍스트 전처리 = for_prompt 정규화만 + 기록 시점 1회 절단 + 토큰 한계 시에만 auto_compact(LLM 요약 replace). append-only 라 KV 캐시 prefix 평시 안정.
- Codex PTC 대응 = Code Mode(V8 isolate, exec 단일 도구, JS로 tools.* 오케스트레이션) — code_mode_only 플래그 옵션, 기본은 function calling.
- Codex 고유: Responses API stateful(previous_response_id, encrypted reasoning), 커널 샌드박스 3중(Seatbelt/Landlock/bwrap + execpolicy + network-proxy), exec-server 원격/이종 OS 실행, rollout JSONL+resume/fork+SQLite, app-server 단일 경계, StepContext, world_state diff, agent-identity.

### 미해결
- 마지막 질문 미답: exec-server 격리가 OpenAI 서버측 생성인지 로컬 VM 인지.
- 백그라운드 fork 질문 2건 답 대기: previous_response_id 일반 사용자 사용 가능 여부 / 샌드박스 3종 용어 풀이.
```

회신: NO_REPLY

## 단계 2: 컴팩션 요약

## Decisions
- 조사 방법 확정: Codex(/Users/seobi/jinsup_space/codex)와 Claude Code 리버스엔지니어링 레포(/Users/seobi/jinsup_space/CC)를 실제 소스 file:line 검증 기반으로 비교하고([확정]/[추론] 태깅), 결과는 다이어그램 위주 HTML로 시각화(visual-explainer / draw-arch). 색상 규약: Codex=teal, Claude Code=coral.
- 비교 관점을 사용자 피드백에 따라 3회 전환: ① 멀티에이전트 구조 비교 → ② 단일 메인 에이전트 한 턴 파이프라인 비교 → ③ 양적(단계 수) 우위 비교 폐기, 스마트 규칙/기능 특징 비교 → ④ CC 프레임 없이 Codex 고유 설계 단독 정리.
- 산출물 위치: 처음엔 codex git 레포 오염 방지를 위해 세션 scratchpad 에 두었으나, 사용자 요청("루트로 옮겨줘")으로 codex 레포 루트에 배치. 커밋은 하지 않음.
- /model 슬래시커맨드로 기본 모델을 Opus 4.8 (1M context) 로 설정 (첫 Agent 도구호출 거부 후).
- 후속 조사는 기존 백그라운드 서브에이전트 2개(a866be613de0d7112=CC 담당, ac9d5f4b9caa7652b=Codex 담당)에 SendMessage 로 이어붙여 병렬 수행하기로 함.
- 핵심 기술 결론(양쪽 소스 교차검증):
  - 두 하네스 모두 루프 종료 판정은 stop_reason 을 신뢰하지 않고 도구 호출 유무로만: CC `needsFollowUp`(query.ts:823-825, :1053, 주석 :549-551), Codex `needs_follow_up = model_needs_follow_up || has_pending_input`(turn.rs:328, end_turn 폴백 codex-api/common.rs:93-95). thinking/reasoning 은 루프 제어에 관여 안 함.
  - 구현 형태 대조: Codex = Rust 상태머신 loop + 이벤트 채널(session/turn.rs), CC = async generator while(true) + yield(query.ts:305). 모델 API: Codex = OpenAI Responses API, CC = Anthropic Messages API.
  - 8축 계산 정교함: 총량 대등. 도구 실행 파이프라인은 Codex 12단계(orchestrator.rs:137, 승인→샌드박스→시도→거부→재승인→에스컬레이션) > CC 10단계(toolExecution.ts:337 runToolUse → :599 checkPermissionsAndCallTool). 병렬은 CC=partitionToolCalls 정적 파티션(toolOrchestration.ts:91, 동시성 기본 10 getMaxToolUseConcurrency) vs Codex=RwLock read/write 동적 게이트(parallel.rs:133-137, router.rs:99). KV 캐싱만 CC 압도.
  - withhold 반전: "hold-then-batch"는 CC가 아니라 Codex — 도구 호출을 in_flight FuturesOrdered 에 큐잉했다 스트림 Completed 후 drain_in_flight(turn.rs:2143-2144, :1907, :2493, stream_events_utils.rs:350-357). CC 는 eager-emit-in-order(StreamingToolExecutor.ts:412, query.ts:842-852); CC 코드의 진짜 `withheld`(query.ts:790-816)는 도구 결과가 아니라 에러 복구용.
  - 사용자의 CC 8단계 이해 중 2건 교정: (2) 도구 결과 보류-배치 방출 아님(즉시 방출), (8) 계속 여부는 thinking 판단 아님(needsFollowUp 만).
  - Read→Edit 강제: CC 는 readFileState 상태 게이트 하드 규칙(FileEditTool.ts:275-287 errorCode:6, mtime stale 거부 :290-311 errorCode:7; FileWriteTool.ts:198-203, NotebookEditTool.ts:221-226; 강제 지점 toolExecution.ts:683-687) + 파일 변경 자동 리마인더(attachments.ts:2063, :2115-2122). Codex 는 상태 게이트 없음 — apply_patch 의 seek_sequence 4단계 content 매칭(정확→rstrip→trim→유니코드 정규화, apply-patch/src/seek_sequence.rs:12, :76-107; 실패 시 거부 lib.rs:736, :791)이 대체. "대화 보고 도구 스킵/dedup"은 양쪽 다 코드에 없음(모델 판단 소프트 영역).
  - 스마트 배치: Codex shell 은 명령 내용 무관 supports_parallel_tool_calls=true 고정(shell_command.rs:152), 배치 개념 없음 — 각 도구가 tokio::spawn 후 read(병렬)/write(배타) 락. CC Bash 는 isConcurrencySafe=isReadOnly(input) 동적 판정(BashTool.tsx:434). Read→Edit→Read→Read→Write 예시에선 결과 스케줄 동일([Read]→[Edit]→[Read‖Read]→[Write])이나, 쓰기 셸 명령(git push)이면 CC=단독 배치, Codex=병렬 스폰(위험은 execpolicy+샌드박스가 담당).
  - 컨텍스트 전처리: CC = 매 사이클 5단계(경계 슬라이스→tool-result 예산→snip→microcompact→autocompact, query.ts:362→:376→:400→:411→:449). Codex = for_prompt 는 정규화만(history.rs:141, normalize_history :359), tool 출력 절단은 기록 시점 1회(record_items history.rs:121, truncate_function_output_payload), 압축은 토큰 한계 도달 시에만 run_pre_sampling_compact(turn.rs:815)/run_auto_compact(turn.rs:971, should_roll_over turn.rs:348, compact.rs SUMMARIZATION_PROMPT 로 history replace). 경계 슬라이스/snip/microcompact 대응 없음.
  - KV 캐싱: CC = cache_control ephemeral breakpoint 3전선 직접 삽입(system: claude.ts:3213/:3228-3234, tools 마지막 스키마 :1388, 메시지 마지막 1개 addCacheBreakpoints claude.ts:3063/:3089, tool_result cache_reference :3187-3206). Codex = 클라이언트 breakpoint 전무, prompt_cache_key=session_id 만 전송(client.rs:888, :903, :469-473) — 서버 자동 prefix 캐싱. Codex 는 append-only 구조라 평시 prefix 안정, 깨지는 구간은 auto_compact(전체 무효화)·compact 후 initial context 재주입(BeforeLastUserMessage)·이미지 스트립·rollback/fork(remove_first_item, drop_last_n_user_turns)·도구 목록 변경(MCP 재로드, tool_search deferred 로드)에 한정. 기록 시점 1회 절단은 캐시를 깨지 않음(append 순간 절단, 과거 항목 재절단 없음).
  - Codex 는 기본 function calling 에이전트. PTC 대응 = Code Mode(실험적 옵션, code_mode_only 플래그): exec 단일 도구로 JS 작성 → V8 isolate(Node/fs/net/console 차단)에서 tools.* 오케스트레이션, TS 타입 선언 제공, store/load·yield_control·`// @exec` 프래그마·text()/image()/notify()/exit() 헬퍼. 크레이트: code-mode, code-mode-host, code-mode-protocol, v8-poc + core/src/tools/code_mode/.
  - Codex 하네스 위치 = codex-rs/core/src/ (session/handlers.rs submission_loop → tasks/regular.rs RegularTask::run → session/turn.rs run_turn→run_sampling_request→try_run_sampling_request; client.rs; tools/{router,parallel,orchestrator}.rs), 언어 100% Rust. Codex 자체는 프론트엔드 아님(CLI 코딩 에이전트; tui=터미널 프론트, app-server=JSON-RPC 경계, core=엔진).
  - 6개 항목(툴서치·스마트배치·도구 파이프라인·컨텍스트 전처리·시스템 리마인더·KV캐싱) 전부 Codex 에도 존재(tool_search + deferred tools 확인: core/src/tools/handlers/tool_search.rs, ResponseItem::ToolSearchCall), KV 캐싱만 접근 상이.
  - Codex 고유 개념: Responses API stateful(previous_response_id, encrypted_content reasoning), 커널 샌드박스 3중 격리(Seatbelt/Landlock/bwrap + execpolicy Starlark DSL + network-proxy egress MITM), exec-server(원격·이종 OS 도구 실행 릴레이 — 이유: 실제 타깃 OS 검증/로컬 보호 격리/클라우드 오프로딩), rollout JSONL+resume/fork+SQLite 미러, app-server 단일 경계(Thread/Turn/Item), StepContext 원자 스냅샷, world_state diff, agent-identity(암호학적 신원), 승인 디스크 영속화(default.rules amendment), MCP read_only_hint 존중, 유니코드 퍼지 패치. CC 고유: readFileState 게이트, cache_control breakpoint 직접 제어, AI 권한 분류기(auto 모드 side_query, permissions.ts:518-524), 권한 5단계 체인(permissions.ts:1158), Plan 모드 게이트, Bash 동적 병렬 판정, 어태치먼트 종류 다양(edited_text_file·todo_reminder·plan_mode·relevant_memories 등), backfillObservableInput 경로 자동확장(훅 우회 방지 겸용).
  - 멀티에이전트(초기 조사): Codex = 지속형 양방향 "사회"(Op::InterAgentCommunication 메일박스, send_message/followup_task/wait/interrupt/list, fork_turns, 깊이 제한) vs CC = 일회성 단방향 위임(최종 텍스트 1회 반환, SendMessage 는 opt-in 레이어).

## Open TODOs
- 마지막 사용자 질문 미답변 (대화 절단 지점): "그 격리 만드는건 OpenAI서버에서 하는거야? 아니면 내 컴퓨터에서 VM 뛰우는거야?"
- 백그라운드 fork 세션 2건 답변 대기: ① previous_response_id 를 일반 사용자가 쓸 수 있는지 ② 샌드박스 3종(Seatbelt/Landlock/bwrap) 용어 풀이.
- scratchpad 정리로 소실된 이전 HTML(agent-arch-compare.html, agent-turn-pipeline.html, loop-computation-detail.html, tool-smart-rules.html, codex-vs-cc-master.html — assistant 는 4개로 언급) 복원 여부: 사용자 결정 대기.
- codex 레포 루트의 HTML 3개는 git 미커밋 새 파일 상태 — 커밋/하위 폴더 이동/.gitignore 여부 미정.
- 미확정 제안들: HTML 인덱스 페이지 묶기, 특정 축 심화(Responses API stateful 흐름, execpolicy Starlark, exec-server 프로토콜, Code Mode V8, 권한 5단계 체인), codex-multiTurn-flow.html 배치 섹션의 CC 파티션↔Codex 락 대조표 보강, 슬라이더 수치 툴팁, 라이트 테마 토글.

## Constraints/Rules
- 양적 우위 비교(단계 수 세기 등) 금지 — 특징/구현 방식 대조로 비교할 것 (사용자 명시 교정).
- 멀티에이전트가 아니라 단일 메인 에이전트 파이프라인 기준으로 비교할 것 (사용자 명시 교정).
- 텍스트보다 도표/다이어그램/이미지 위주 HTML 로 작성할 것.
- 모든 주장은 실제 소스 file:line 으로 검증하고 [확정]/[추론] 을 구분할 것.
- codex git 저장소 오염 방지: 산출물은 scratchpad 우선, 사용자가 요청한 것만 레포에 배치, 커밋하지 않음.
- draw-arch 산출물은 light/dark 자동 대응.
- 시각화 색상 규약 유지: Codex=teal, Claude Code=coral (Codex 단독 페이지는 teal + gold/violet/coral 액센트).

## Pending user asks
- (미해결, 최신) exec-server/샌드박스 격리가 OpenAI 서버측에서 만들어지는지, 사용자 컴퓨터에서 VM 을 띄우는 것인지 — 답변 전에 대화가 끊김.
- (백그라운드 진행 중) fork 로 넘긴 2개 질문: previous_response_id 일반 사용자 사용 가능 여부 / 샌드박스 3종 용어 설명 — 별도 세션에서 답 예정.
- (사용자 응답 대기) 소실된 이전 HTML 자료들을 루트에 복원할지 여부 — assistant 가 물었으나 답 없음.

## Exact identifiers
- 레포/경로: /Users/seobi/jinsup_space/codex, /Users/seobi/jinsup_space/CC, LonerStayle/cc_agent_bible.git, @openai/codex, codex-rs (crate 148개), /Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html
- scratchpad: /private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/scratchpad
- 산출물 HTML(루트, 미커밋): /Users/seobi/jinsup_space/codex/codex-cc-loop-features.html (10557 bytes, 8 1 11:03), /Users/seobi/jinsup_space/codex/codex-multiTurn-flow.html, /Users/seobi/jinsup_space/codex/codex-unique.html
- 소실 HTML: agent-arch-compare.html, agent-turn-pipeline.html, loop-computation-detail.html, tool-smart-rules.html, codex-vs-cc-master.html
- 서브에이전트 task-id: a866be613de0d7112 (CC query 루프 조사), ac9d5f4b9caa7652b (Codex 메인 turn 루프 조사); 출력 파일: /private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/tasks/a866be613de0d7112.output, /private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/tasks/ac9d5f4b9caa7652b.output
- tool-use-id: toolu_01QkgJuJJzxTaJMepqtdA8cA, toolu_01XxQTgE3u8ZbDEY99mMsJon, toolu_01VLn4qzhUZKdwDZBNcTFGnT, toolu_01QmaRDDVLeJGngn8fkb8cvW
- 모델: Opus 4.8 (1M context)
- 커밋 메시지: "Require data URLs for code-mode image output (#33659)", "Restore agent roles when reloading v2 sub-agents", "Validate reasoning effort after applying spawn roles"
- Codex 소스: codex-rs/core/src/session/turn.rs (run_turn :227-298, 후처리 :314-382, needs_follow_up :328, should_roll_over :348, run_pre_sampling_compact :815, run_auto_compact :971, run_sampling_request 재시도 :1164-1167, drain_in_flight :1907(기록 :1915-1917), reasoning 파라미터 :1989-1990/:2009/:2024, in_flight push :2143-2144, end_turn :2321-2323, :2493), session/handlers.rs (submission_loop), tasks/regular.rs (RegularTask::run), client.rs (prompt_cache_key() :469-473, :888, :903), context_manager/history.rs (record_items :121-135, for_prompt :141, normalize_history :359, process_item :370), tools/parallel.rs (:48, :94, :106, :131-137), tools/router.rs (tool_supports_parallel :99), tools/orchestrator.rs (:4-6, run :137, :155-165, :166-168, :169-226, :228-244, :245-255, :264-282, :285-292, :294-305, :306-390, :326, :339, :341-380, :344, :394-421, :423-445, :446-469), tools/registry.rs (:271, :385), tools/src/tool_executor.rs (:64-66), tools/handlers/shell/shell_command.rs (:152), tools/handlers/mcp.rs (:76-86), tools/handlers/tool_search.rs, ResponseItem::ToolSearchCall, exec_policy.rs (:52, create_exec_approval_requirement_for_command :280, :291, :306, :329-390, add_prefix_rule :409-440), execpolicy/src/decision.rs (:9-15), execpolicy/src/rule.rs (:16-111, :118-149), default.rules, tools/sandboxing.rs (with_cached_approval :71, :88-96, :109-114), tools/handlers/mcp_tool_call.rs (remember_mcp_tool_approval :1940-2005), session/mod.rs (persist_execpolicy_amendment :1982, ApprovedCommandPrefixSaved :2032, record_step_world_state_if_changed :2821-2826), session/token_budget.rs (:6, :32-60), session/time_reminder.rs (take_reminder_due :71), stream_events_utils.rs (record_completed_response_item :346, :350-357, :356), codex-api/common.rs (:93-95), compact.rs (SUMMARIZATION_PROMPT), tools/mod.rs (format_exec_output_for_model :78-103), apply-patch/src/lib.rs (:606, :681, "Failed to find context '{ctx}'" :736, "Failed to find expected lines" :791), apply-patch/src/seek_sequence.rs (:12, :76-107), code-mode-protocol/src/description.rs (:12, "Run JavaScript code to orchestrate/compose tool calls"), core/src/tools/code_mode/ (execute_spec.rs code_mode_only, wait_spec.rs, delegate.rs), 크레이트 code-mode/code-mode-host/code-mode-protocol/v8-poc, core/src/agent/ (mod.rs, control.rs, registry.rs, role.rs, status.rs, agent_resolver.rs, agent_names.txt, builtins/awaiter.toml), session/multi_agents.rs, tools/handlers/multi_agents_v2/ (spawn.rs, message_tool.rs, interrupt_agent.rs, wait.rs, list_agents.rs), cli/src/main.rs, TokenBudgetReminder, AutoCompactFallbackPrompt, ContextualUserFragment, InitialContextInjection, BeforeLastUserMessage, remove_first_item, drop_last_n_user_turns, Op::UserInput, Op::InterAgentCommunication, SpawnAgentForkMode, exceeds_thread_spawn_depth_limit, Seatbelt/Landlock/bwrap, exec-server, agent-graph-store, agent-identity
- Claude Code 소스: src/query.ts (queryLoop :305, thinking 규칙 :151-163, getMessagesAfterCompactBoundary :362, applyToolResultBudget :376, snipCompactIfNeeded :400, microcompact :411, contextCollapse :436, appendSystemContext :444, autocompact :449, 주석 :549-551, isAtBlockingLimit :632, withheld :790-816, needsFollowUp :823-825, addTool :833, :842-852, :1053, :1346, :1385, :1512, getAttachmentMessages 호출 :1569, :1578, :1587-1602, :1608-1616, refreshTools :1648, turnCount :1667, maxTurns :1693, messages concat :1704), StreamingToolExecutor.ts (:328, getCompletedResults :412, :436-438), toolOrchestration.ts (:8-12, :42-62, :86-90, partitionToolCalls :91, :98-112, runToolsSerially :118, runToolsConcurrently :152, getMaxToolUseConcurrency 기본 10), toolExecution.ts (runToolUse :337, checkPermissionsAndCallTool :599, :615, :683-687, :790-792, :800, :834-838, :848-860, :921-930, :995-1104, tool.call :1207, :1291, mapToolResultToToolResultBlockParam :1292, addToolResult :1403-1478, :1456-1568, contextModifier :1467-1472, runPostToolUseHooks :1483), messages.ts (reorderAttachmentsForAPI :1481, normalizeMessagesForAPI :2069, ensureSystemReminderWrap :2276, mergeUserMessagesAndToolResults :2280-2286), claude.ts (getCacheControl :358-374, :1266, :1388, :1699-1728, addCacheBreakpoints :3063, :3078-3089, markerIndex = messages.length - 1 :3089, cache_reference :3187-3206, buildSystemPromptBlocks :3213, :3221, :3228-3234), attachments.ts (:452, :483, :488, :565-576, :588, :654, :672, :871, :1594, getChangedFiles :2063, :2115-2122, :2258, :2937, :3309), FileEditTool.ts (backfillObservableInput :115-121, :275-287, :290-311, :296-300, :317-324, :520), FileEditTool/prompt.ts (:5), FileWriteTool.ts (:198-203, :332), NotebookEditTool.ts (:221-226), FileReadTool.ts (:373, :842-844, timestamp: Math.floor(stats.mtimeMs)), BashTool.tsx (isConcurrencySafe :434), GlobTool.ts (:76), GrepTool.ts (:183), McpAuthTool.ts (:67), EnterPlanModeTool.ts (:79), permissions.ts (hasPermissionsToUseToolInner :1158, :1170, :1184, :1259, :1268-1281, :1270, :1284-1296, persistPermissionUpdates :426, :400-471, :486-499, :505-516, side_query :518-524, :523), prompts.ts (:301-305, :310, :438, :770), TodoWriteTool/prompt.ts (:7, :25), filesystem.ts (:1446), errorCode:6, errorCode:7, 'File has not been read yet. Read it first before writing to it.', 'File has been modified since read, either by the user or by a linter. Read it again before attempting to write it.', cache_control: { type:'ephemeral', ttl?:'1h', scope?:'global' }
- 기타: Responses API / Messages API, previous_response_id, encrypted_content, prompt_cache_key, tool_use / function_call, stop_reason, network-proxy, rollout JSONL + SQLite, app-server (Thread/Turn/Item), StepContext, world_state diff, DeferredExecutor, TruncationPolicy, FuturesOrdered, RwLock, tokio::spawn, V8 isolate, yield_control, `// @exec: {"yield_time_ms":10000, "max_output_tokens":1000}`, ALL_TOOLS, MAX_JS_SAFE_INTEGER, 예시 시나리오 "auth.ts 버그 고쳐줘", 도구 순서 예시 Read → Edit → Read → Read → Write

## 단계 3~7: 미적용

- 단계 3(이전 요약 재증류 래퍼): 이전 컴팩션 요약 없음 → 미적용.
- 단계 4(부분 요약 병합): 히스토리를 파트로 분할 요약하지 않음 → 미적용.
- 단계 5(split-turn 프리픽스): 턴 중간 절단 요약 아님 → 미적용.
- 단계 6(품질 가드 재시도): 요약 감사 실패 없음 → 미적용.
- 단계 7(컴팩션 직후 컨텍스트 리프레시): 요약 다음 턴에 시스템 이벤트로 주입되는 것으로, AGENTS.md 의 "Session Startup"/"Red Lines" 섹션 원문이 필요하나 본 대화 외 파일 읽기 금지 규칙에 따라 산출 생략.
