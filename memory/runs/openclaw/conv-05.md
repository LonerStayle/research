# openclaw 컴팩션 시뮬레이션 — conv-05

## 단계 1: 사전 메모리 플러시

memory/YYYY-MM-DD.md 에 APPEND 될 내용:

```markdown
## Codex vs Claude Code 하네스 비교 리서치 (세션 기록)

- 조사 대상: OpenAI Codex 레포 `/Users/seobi/jinsup_space/codex` (Rust, codex-rs Cargo workspace 크레이트 148개) ↔ Claude Code 리버스엔지니어링 리서치 레포 `/Users/seobi/jinsup_space/CC` (GitHub 원격: LonerStayle/cc_agent_bible.git).
- 산출물(HTML, codex 레포 루트, 미커밋): `codex-cc-loop-features.html`(루프 기능 좌/우 비교, 10557 bytes), `codex-multiTurn-flow.html`(Codex 한 턴 흐름 — CC의 `html_group_v2/multiTurn-flow.html` 대응, 예시 "auth.ts 버그 고쳐줘"), `codex-unique.html`(Codex 고유 설계 6축).
- scratchpad 임시폴더 정리로 이전 시각화 유실: agent-arch-compare.html / agent-turn-pipeline.html / loop-computation-detail.html / tool-smart-rules.html / codex-vs-cc-master.html — 복원 여부 사용자 미결.
- 핵심 결론(소스 검증): 두 하네스 모두 루프 종료는 stop_reason이 아닌 도구 호출 유무(`needsFollowUp` / `needs_follow_up`)로만 판정, thinking 무관. Codex는 실행·안전(도구 오케스트레이션 12단계 + 커널 샌드박스 + execpolicy Starlark)에, CC는 상태·컨텍스트(readFileState 게이트 + 매 사이클 전처리 + `cache_control` breakpoint)에 정교함이 실림. Codex의 PTC 대응 = Code Mode(V8 isolate, `exec` 단일 도구, 실험적 — 기본은 function calling). Codex 고유: Responses API stateful(`previous_response_id`, `encrypted_content`), exec-server 원격/이종 OS 실행, rollout JSONL + resume/fork + SQLite, app-server 단일 경계, StepContext, world_state diff, agent-identity.
- 설정: /model 로 기본 모델을 Opus 4.8 (1M context)로 저장.
- 미결 질문: 사용자의 "StepContext 이건 뭐야?" — `codex-rs/core/src/session/step_context.rs` 읽는 도중 세션 절단, 답변 필요.
```

턴 응답: NO_REPLY

## 단계 2: 컴팩션 요약

## Decisions

- 비교 프레임을 사용자 피드백에 따라 단계적으로 전환하기로 결정: ① 멀티에이전트 구조 비교 → ② 단일 메인 에이전트의 한 턴 파이프라인 비교 → ③ 양적(단계 수) 우위 비교 폐기, 스마트 규칙/특징 대조로 → ④ CC 인터페이스 프레임을 벗어난 Codex 고유 설계 정리.
- 시각화 방침: 텍스트 최소·다이어그램/도표 위주 HTML, 색 메타포 Codex=teal / Claude Code=coral 로 통일. draw-arch 산출물은 light/dark 자동 대응.
- 산출물 위치: 처음엔 세션 scratchpad(codex git 레포 오염 방지) → 사용자 지시("루트로 옮겨줘")로 `/Users/seobi/jinsup_space/codex/` 루트로 이동, git 커밋은 하지 않음(untracked 유지).
- /model 로 기본 모델을 Opus 4.8 (1M context)로 설정·저장.
- 조사 방법: 백그라운드 서브에이전트 2개(a866be613de0d7112 = CC 조사, ac9d5f4b9caa7652b = Codex 조사)를 SendMessage 로 재활용하며 3라운드 심층 조사(단일턴 루프 → 8축 계산적 정교함 → 스마트 규칙).
- 소스 검증으로 확정된 결론:
  - 루프 종료: 양쪽 다 `stop_reason` 불신, 도구 호출 유무로만 판정 — CC `needsFollowUp`(query.ts:823-825, 종료 분기 query.ts:1053), Codex `needs_follow_up = model_needs_follow_up || has_pending_input`(turn.rs:328). thinking/reasoning 은 루프 제어에 무관(사용자 이해 교정).
  - withhold: CC 는 hold-and-batch 가 아니라 eager-emit-in-order(StreamingToolExecutor.ts:412, 배리어 :436-438; 코드의 `withheld` 변수는 에러 복구용 query.ts:790-816)이고, 오히려 Codex 가 `in_flight: FuturesOrdered` 큐잉 후 `drain_in_flight`(turn.rs:2493, 정의 :1907) 하는 hold-then-batch(사용자 이해 교정).
  - 도구 파이프라인: CC 10단계(zod→validateInput→backfill→PreToolUse 훅→권한→call→PostToolUse 훅…, toolExecution.ts:337, :599), Codex 12단계(승인→샌드박스 선택→시도→Denied 시 재승인·에스컬레이션 재실행, orchestrator.rs:137).
  - 병렬/배치: CC = `partitionToolCalls` 정적 파티션(toolOrchestration.ts:91, 동시성 최대 10) + Bash 는 명령 파싱 동적 판정(BashTool.tsx:434). Codex = 배치 없음, `RwLock` read(병렬)/write(배타) 동적 게이트(parallel.rs:133-137), shell 은 명령 내용 무관 `supports_parallel_tool_calls → true` 고정(shell_command.rs:152). 예시 `Read→Edit→Read→Read→Write` 는 양쪽 실행 스케줄 동일하나, 쓰기가 셸 명령(`git push`)이면 CC 는 단독 배치·Codex 는 병렬 스폰으로 갈림.
  - KV 캐싱(유일한 큰 격차): CC = `cache_control: ephemeral` breakpoint 를 클라이언트가 3전선(system 경계/tools 끝/메시지 마지막 1개 + tool_result `cache_reference`)에 직접 삽입(claude.ts:3063, :358-374, :3213). Codex = breakpoint 전무, `prompt_cache_key = session_id`(client.rs:888, :903, :469-473)로 서버 자동 prefix 캐싱에 위임 — OpenAI Responses API 설계 차이.
  - Codex 캐시는 평시 잘 유지됨: 히스토리 append-only + time_reminder 간격 억제(time_reminder.rs:71) + 중간 제거 단계 없음. 깨지는 구간은 이벤트성 — auto_compact(전체 교체), compact 후 initial context 재주입(BeforeLastUserMessage), 이미지 스트립, 롤백/fork(`remove_first_item`, `drop_last_n_user_turns`), 도구 목록 변경(MCP 재로드, tool_search deferred 로드).
  - 컨텍스트 전처리: CC 는 매 사이클 능동 파이프라인(query.ts:362 경계 슬라이스 → :376 tool-result 예산 → :400 snip → :411 microcompact → :436 contextCollapse → :444 시스템 조립 → :449 autocompact → :632 하드 차단). Codex 는 매 사이클엔 정규화만(`for_prompt` history.rs:141 → `normalize_history` :359 — call↔output 페어 정리 + 이미지 스트립), 도구 출력 절단은 "기록 시점" 1회(`record_items` history.rs:121, `truncate_function_output_payload`), LLM 요약 압축은 토큰 한계 도달 시만(`run_pre_sampling_compact` turn.rs:815 / `run_auto_compact` turn.rs:971, `should_roll_over` turn.rs:348). CC 의 경계 슬라이스·snip·microcompact 는 Codex 에 대응 없음.
  - 기록 시점 절단은 append 순간 1회라 KV 캐시를 깨지 않음(오히려 지키는 설계). 트레이드오프: Codex 는 원본 복원 불가, CC 는 원본을 디스크 이관(`applyToolResultBudget`)해 유연.
  - 편집 안전: CC = readFileState 상태 게이트 하드 규칙(FileEditTool.ts:275-311, errorCode 6 미독/7 stale-mtime; FileWriteTool.ts:198-203, NotebookEditTool.ts:221-226) + 변경 파일 자동 리마인더(attachments.ts:2063). Codex = 상태 게이트 없음, `apply_patch` context 매칭 `seek_sequence` 4단계(정확→rstrip→trim→유니코드 정규화, seek_sequence.rs:12, :76-107; 실패 시 적용 거부 lib.rs:736, :791). "읽었니?(상태 추적)" vs "정확히 아니?(내용 대조)".
  - 대화 기반 도구 실행 스킵/dedup: 양쪽 다 코드에 없음 확정 — 모델의 프롬프트 기반 판단(소프트) 영역.
  - Codex 고유 스마트 규칙: execpolicy Starlark DSL(exec_policy.rs:52, Decision::{Allow,Prompt,Forbidden}), 승인 세션 캐시 + 디스크 영속(`default.rules` amendment, exec_policy.rs:409-440), 샌드박스 에스컬레이션 재승인(orchestrator.rs:326-469), MCP `read_only_hint` 존중 병렬화(handlers/mcp.rs:76-86), 유니코드 퍼지 패치, 복합 파싱 시 auto-amendment 차단(exec_policy.rs:291). CC 고유: AI 권한 분류기(auto 모드 side_query, permissions.ts:518-524), Plan 모드 게이트, 경로 자동확장(backfillObservableInput, 훅 우회 방지 겸용), 권한 5단계 체인(permissions.ts:1158).
  - Codex 정체: 프론트엔드 아님, CLI 코딩 에이전트. 하네스는 전부 `codex-rs/core/src/` — session/handlers.rs(`submission_loop`) → tasks/regular.rs(`RegularTask::run`) → session/turn.rs(`run_turn`→`try_run_sampling_request`) → client.rs(모델 호출) → tools/{router,parallel,orchestrator}.rs. 언어 100% Rust(codex-cli npm 은 바이너리 런처). CC 대응 하네스는 `CC/src/query.ts` 의 `queryLoop` 단일 파일.
  - Codex PTC = Code Mode(실험 옵션): `exec` 단일 도구로 JS 작성 → 매번 새 V8 isolate, 전역 `tools.*`, TS 타입 선언 렌더링, `store`/`load`, `yield_control()`+wait, no Node/fs/net(크레이트: code-mode, code-mode-host, code-mode-protocol, v8-poc; 설명 원문 "Run JavaScript code to orchestrate/compose tool calls" description.rs:12). 기본은 function calling(`code_mode_only` 플래그, execute_spec.rs).
  - 6개 기능(툴서치·스마트배치·도구 파이프라인·컨텍스트 전처리·시스템 리마인더·KV캐싱) 전부 Codex 에도 존재(tool_search 는 core/src/tools/handlers/tool_search.rs, `ResponseItem::ToolSearchCall`, deferred tools 포함) — 5개는 구현만 다르고 KV캐싱만 접근이 근본적으로 다름.
  - Codex 고유 설계(CC 에 대응 없음): Responses API stateful(`previous_response_id`, reasoning `encrypted_content`, WebSocket 세션 캐싱), 커널 샌드박스 3중 격리(Seatbelt/Landlock/bwrap + execpolicy + network-proxy egress MITM), exec-server(원격·이종 OS 도구 실행), rollout JSONL + resume/fork + SQLite 미러, app-server 단일 경계(Thread/Turn/Item JSON-RPC), StepContext(모델 호출 1회 단위 원자 스냅샷), world_state diff, agent-identity(암호학적 신원).

## Open TODOs

- 사용자 질문 "StepContext 이건 뭐야? 스텝 컨테스트? 한번의 모델 호출?" 답변 완료 — `codex-rs/core/src/session/step_context.rs` 를 읽던 중 세션 절단됨. 이어서 마무리해야 함.
- 유실 시각화 복원 여부 확인: scratchpad 정리로 agent-arch-compare.html / agent-turn-pipeline.html / loop-computation-detail.html / tool-smart-rules.html / codex-vs-cc-master.html 유실. 어시스턴트가 복원 의사를 물었고 사용자 응답 대기.
- 채택 미정 제안: Responses API stateful / 커널 샌드박스 스택 / exec-server 원격 실행 단독 심층 정리, 루트 HTML 3종 인덱스 페이지 묶기, `codex-multiTurn-flow.html` 배치 섹션(CC 파티션 ↔ Codex 락 대조표) 보강, git 미추적 HTML 의 하위 폴더 이동 또는 .gitignore 처리.

## Constraints/Rules

- 비교는 멀티에이전트가 아니라 "하나의 메인 에이전트 파이프라인" 기준으로 할 것(사용자 강한 요구).
- 단계 수 등 양적 우위 비교 금지 — 각 시스템의 스마트 규칙·구현 특징 대조로 서술할 것.
- 산출물은 텍스트보다 도표/다이어그램 위주 HTML 로.
- codex git 저장소를 오염시키지 말 것: 새 HTML 은 커밋하지 않고 untracked 로 두며, 이동/무시 처리는 사용자 결정.
- 디자인 일관성: Codex=teal / Claude Code=coral, draw-arch 파일은 light/dark 자동 대응.
- 조사 보고는 실제 소스 file:line 검증 기반으로([확정]/[추론] 구분), 코드·경로·식별자는 원문 유지.

## Pending user asks

- "StepContext 이건 뭐야? 스텝 컨테스트? 한번의 모델 호출?" — 미답변. step_context.rs 첫 부분(LoadedAgentsMd, TurnEnvironmentSnapshot, McpRuntimeSnapshot, ResolvedSelectedCapabilityRoot, ToolInfo import까지)만 읽은 상태에서 대화가 절단되어, 재개 시 최우선으로 답해야 함.

## Exact identifiers

- 레포/디렉토리: /Users/seobi/jinsup_space/codex, /Users/seobi/jinsup_space/codex/codex-rs, /Users/seobi/jinsup_space/CC, /Users/seobi/jinsup_space/CC/src, /Users/seobi/jinsup_space/CC/html_group_v2/multiTurn-flow.html
- 루트 산출물: /Users/seobi/jinsup_space/codex/codex-cc-loop-features.html (10557 bytes, 8 1 11:03 이동), /Users/seobi/jinsup_space/codex/codex-multiTurn-flow.html, /Users/seobi/jinsup_space/codex/codex-unique.html
- scratchpad: /private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/scratchpad (유실: agent-arch-compare.html, agent-turn-pipeline.html, loop-computation-detail.html, tool-smart-rules.html, codex-vs-cc-master.html)
- 백그라운드 에이전트: a866be613de0d7112 (CC query 루프 조사), ac9d5f4b9caa7652b (Codex 메인 turn 루프 조사); 출력 파일 /private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/tasks/a866be613de0d7112.output, /private/tmp/claude-501/-Users-seobi-jinsup-space-codex/160bf653-2f78-4488-8eab-1457862e0389/tasks/ac9d5f4b9caa7652b.output
- tool-use ID: toolu_01QkgJuJJzxTaJMepqtdA8cA, toolu_01XxQTgE3u8ZbDEY99mMsJon, toolu_01VLn4qzhUZKdwDZBNcTFGnT, toolu_01QmaRDDVLeJGngn8fkb8cvW
- Codex 소스: codex-rs/core/src/session/turn.rs (전처리 :227~298, needs_follow_up :328, should_roll_over :348, run_pre_sampling_compact :815, run_auto_compact :971, in_flight :2143-2144, drain_in_flight :2493/정의 :1907), session/handlers.rs, session/step_context.rs, session/time_reminder.rs:71, session/token_budget.rs:6, tasks/regular.rs, client.rs (:888, :903, :469-473), compact.rs, context_manager/history.rs (:121, :141, :359), tools/parallel.rs (:94, :133-137), tools/orchestrator.rs (:137, :326, :339, :344, :394-421, :446-469), tools/router.rs:99, tools/registry.rs (:271, :385), tools/handlers/shell/shell_command.rs:152, tools/handlers/mcp.rs:76-86, tools/handlers/tool_search.rs, tools/sandboxing.rs (:71, :88-96, :109-114), tools/mod.rs:78-103, core/src/exec_policy.rs (:52, :280, :291, :306, :329-390, :409-440), apply-patch/src/lib.rs (:606, :681, :736, :791), apply-patch/src/seek_sequence.rs (:12, :76-107), stream_events_utils.rs (:346, :350-357, :356), codex-api/common.rs:93-95, execpolicy/src/decision.rs:9-15, execpolicy/src/rule.rs (:16-111, :118-149), code-mode-protocol/src/description.rs:12, core/src/tools/code_mode/execute_spec.rs
- Code Mode 크레이트: code-mode, code-mode-host, code-mode-protocol, v8-poc
- CC 소스: src/query.ts (:151-163, :305, :362, :376, :400, :411, :436, :444, :449, :549-551, :632, :790-816, :823-825, :833, :842-852, :1053, :1346, :1569, :1578, :1587-1602, :1608-1616, :1648, :1667, :1693, :1704), StreamingToolExecutor.ts (:328, :412, :436-438), toolOrchestration.ts (:8-12, :42-62, :86-90, :91, :98-108, :118, :152), toolExecution.ts (:337, :599, :615, :683-687, :790-792, :800, :834-838, :848-860, :921-930, :995-1104, :1207, :1291, :1292, :1403-1478, :1456-1568, :1467-1472, :1483), messages.ts (:1481, :2069, :2276, :2280-2286), claude.ts (:358-374, :1266, :1388, :1699-1728, :3063, :3078-3088, :3089, :3187-3206, :3213, :3221, :3228-3234), attachments.ts (:452, :483, :488, :565-576, :588, :654, :672, :871, :1594, :2063, :2115-2122, :2258, :2937, :3309), permissions.ts (:400-471, :426, :486-499, :505-516, :518-524, :523, :1158, :1170, :1184, :1259, :1268-1281, :1284-1296), FileEditTool.ts (:115-121, :275-287, :290-311, :296-300, :317-324, :520), FileWriteTool.ts (:198-203, :332), NotebookEditTool.ts:221-226, FileReadTool.ts (:373, :842-844), BashTool.tsx:434, GlobTool.ts:76, GrepTool.ts:183, McpAuthTool.ts:67, EnterPlanModeTool.ts:79, FileEditTool/prompt.ts:5, TodoWriteTool/prompt.ts (:7, :25), prompts.ts (:301-305, :310, :438, :770), filesystem.ts:1446
- GitHub 원격: LonerStayle/cc_agent_bible.git
- 커밋 메시지: "Require data URLs for code-mode image output (#33659)", "Restore agent roles when reloading v2 sub-agents", "Validate reasoning effort after applying spawn roles", "Add an app-server API for rea(절단)"
- 모델: Opus 4.8 (1M context)
- 에러코드/식별 값: errorCode:6 ("File has not been read yet"), errorCode:7 ("File has been modified since read"), 크레이트 148개, CC 도구 파이프라인 10단계 / Codex 12단계, CC 병렬 동시성 최대 10 (getMaxToolUseConcurrency), 서브에이전트 토큰 141516 / 152415 / 168828 / 182203

## 단계 3~7: 비적용

- 단계 3(이전 요약 재증류 래퍼): 이 대화에 이전 컴팩션 요약 없음 → 미사용.
- 단계 4(부분 요약 병합): 단일 파트로 요약 → 미사용.
- 단계 5(split-turn 프리픽스): 별도 프리픽스 요약 대상 아님 → 미사용.
- 단계 6(품질 가드 재시도): 감사 실패 발생 없음 → 미사용.
- 단계 7(컨텍스트 리프레시): 하네스가 주입하는 고정 이벤트로, AGENTS.md/Current time 치환부는 시뮬레이션 지침에 따라 무시 → 산출물 없음.
