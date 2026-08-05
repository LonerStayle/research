# openclaw 컴팩션 시뮬레이션 — conv-06

## 단계 1: 사전 메모리 플러시 (silent 턴)

기록 대상: `memory/YYYY-MM-DD.md` (append only, 부트스트랩 파일 MEMORY.md/DREAMS.md/SOUL.md/TOOLS.md/AGENTS.md 는 read-only 유지)

```markdown
## Grok Build 에이전트 아키텍처 리포트 세션 (grok-build ↔ Claude Code 비교)

- 산출물 위치: /Users/seobi/jinsup_space/grok-build/agent-report/ (git 미추적 로컬 폴더).
  페이지: index / agent-core / shell-agent / subagent-system / tool-system / context-mgmt /
  integration / safety-config / tui-entry / prompt-flow / harness / cc-vs-grok /
  arch-cc-vs-grok (.html). how-it-works.html 은 방향 오판으로 생성 후 삭제됨.
- 생성 스크립트/데이터: /private/tmp/claude-501/-Users-seobi-jinsup-space-grok-build/e43b9dd8-0646-4fce-bb5a-a90ce1d59622/scratchpad/
  의 gen_report.py · gen_compare_data.py · gen_pipeline.py · gen_loop.py · gen_features.py ·
  gen_arch.py, 데이터는 report-data/ · cc-data/ · loop-data/ · feature-data/ 의 JSON.
- 사용자 선호(반복 확인됨): 텍스트 산문보다 도표·플로우 중심 시각화, 멀티에이전트 관점 말고
  메인 에이전트 단일 파이프라인 관점, 양적 우위 비교 말고 기능 특징(유무·방식) 비교.
  cc-vs-grok.html 은 이 피드백에 따라 4회 재구성됨(6축 비교 → 파이프라인 8단계 → 루프 계산
  밀도 → 스마트 기능 매트릭스).
- 확정 정정 2건: (a) "Grok 도구 순차 실행"은 오류 — 실제는 순차 권한 게이트 후
  FuturesUnordered 병렬 dispatch + per-path Mutex(file_locks) (tool_calls.rs
  execute_tool_calls). (b) "계속 여부를 thinking 이 판단"은 CC도 사실 아님 — CC
  needsFollowUp = tool_use 블록 유무, Grok = tool_calls.is_empty(), 둘 다 기계적 게이트.
- 핵심 대비(소스 확정): Read→Edit 강제 = CC 런타임 하드 게이트(readFileState, errorCode 6/7,
  FileEditTool.ts:275-306) vs Grok 없음(설정타임 skip_read_before_edit 요구 + 소프트 규칙);
  하네스 = CC pull(유휴+빈 큐면 완전 정지) vs Grok push(SyntheticReason 12종 synthetic 주입);
  메모리 = CC LLM 셀렉터(벡터 의도적 거부) vs Grok SQLite BM25+벡터 하이브리드;
  위드홀드(모델 출력 잘림 8k→64k, tengu_otk_slot_v1)는 CC 고유(Grok grep 0건).
- Grok Build 정체: 프론트엔드 아님 — grok CLI 전체 제품. TUI(xai-grok-pager) ↔ ACP 인메모리
  채널 ↔ 에이전트 런타임(xai-grok-shell 의 MvpAgent/SessionActor). 전부 Rust(edition 2024,
  tokio, ratatui, 64개 크레이트). CC 는 TypeScript/Node 단일 이벤트루프 + Ink.
- 주의: CC 쪽 수치(cap 10, 39기법, 훅 27 등)는 /Users/seobi/jinsup_space/CC 리버스 엔지니어링
  소스 기반이라 실제 최신 구현과 다를 수 있음. Grok 쪽은 오픈소스 실측.
- 작업 절차 메모: Playwright 는 file: 프로토콜 차단 → python3 -m http.server(127.0.0.1) 로
  서빙 후 검증, 검증용 jpeg 와 서버는 사용 후 정리.
```

턴 응답: NO_REPLY

## 단계 2: 컴팩션 요약

사용자가 /Users/seobi/jinsup_space/grok-build (xAI Grok Build, Rust 터미널 코딩 에이전트)를 에이전트 중심으로 분석시켜 다중 페이지 HTML 리포트를 만들게 했고, 이어서 /Users/seobi/jinsup_space/CC (Claude Code 리버스 엔지니어링 리서치 프로젝트)와의 비교 페이지를 관점을 바꿔가며 4회 재구성시켰다. 마지막 요청인 /draw-arch 6개 루프 기능 비교 페이지는 생성·검증까지 끝났으나 최종 정리·보고 직전에 대화가 절단됐다.

## Decisions

- Grok Build 탐색은 병렬 리더 7개 워크플로우(agent-core / shell-agent / subagent-system / tool-system / context-mgmt / integration / tui-entry) + 통합점검 gap-fill(safety-config)로 수행 (Workflow Task ID w1my0wxpx).
- 산출물은 git 미추적 로컬 폴더 /Users/seobi/jinsup_space/grok-build/agent-report/ 의 정적 HTML 리포트로 확정. 디자인은 다크 "회로 스키매틱" — Black Han Sans(제목) + Gothic A1(본문) + IBM Plex Mono(경로), 스크롤 리빌, 상단 고정 내비 + 이전/다음 페이지네이션.
- 렌더 검증 절차: Playwright 가 file: 프로토콜을 차단하므로 python3 -m http.server(127.0.0.1) 서빙 → navigate/evaluate/fullPage 스크린샷 → 서버 pkill + 검증 jpeg 삭제. 초기 빌드에서 파싱 버그 2건(shell-agent 흐름 7단계 유실, tui-entry 한국어 서수 분리 실패)과 레이아웃 버그 1건(통계 그리드 미적용)을 이 절차로 잡아 수정.
- prompt-flow.html(질문 하나의 여정 16단계, PHASE A~E) 추가. 초보용 how-it-works.html 은 방향 오판으로 삭제하고 harness.html 로 교체 — 코드 근거(SyntheticReason enum, TurnInputContext.synthetic, "harness produced the turn")로 "하네스 = Idle 자리에 synthetic 프롬프트를 자동 주입해 사람 없이 루프를 이어가는 바깥 껍데기"로 정의. SyntheticReason 12종은 깨우기(WAKE) 5 / 조향(STEER) 4 / 맥락(CONTEXT) 3 으로 분류.
- CC 비교는 4개 병렬 분석 에이전트(코어루프+서브에이전트 / 도구+권한안전 / 컨텍스트+메모리+압축 / 하네스+독특기술)가 cc-data/*.json 으로 저장한 결과로 구성. cc-vs-grok.html 은 사용자 피드백에 따라 4회 덮어쓰기 재구성: ① 6축 멀티에이전트 비교(35701 bytes) → ② 메인 에이전트 단일 파이프라인 8단계(16228 bytes, ①프롬프트 접수→②컨텍스트 조립→③토큰·압축→④모델 호출→⑤ReAct 분기→⑥권한→⑦도구 실행→⑧재주입 루프백) → ③ 루프 한 사이클 계산 밀도 히트맵(19294 bytes, 8단계 중 6개 대등 판정) → ④ 스마트 기능 매트릭스(20778 bytes, 7카테고리 26기능, 범례 ●하드/◐소프트/▲다른방식/○없음).
- 공식 정정 2건: (a) 앞서 말한 "Grok 도구 순차 실행"은 오류 — 실제는 순차 권한 게이트로 approved 수집 후 FuturesUnordered 병렬 dispatch + 파일 경로별 Mutex(file_locks)로 같은 파일 쓰기만 직렬화 (tool_calls.rs execute_tool_calls, ~12단계 prepare 파이프라인); (b) "계속 여부를 thinking 에서 판단"은 CC조차 사실 아님 — CC needsFollowUp = tool_use 블록 유무(msgToolUseBlocks.length > 0), Grok = tool_calls.is_empty(), 둘 다 기계적 게이트.
- 확정 판정 요지: Read→Edit 강제는 CC 런타임 하드 게이트(readFileState/FileStateCache 조회, errorCode 6 "File has not been read yet", mtime 변경 시 errorCode 7, FileEditTool.ts:275-306) vs Grok 런타임 게이트 없음(설정타임 skip_read_before_edit=false 시 Read 도구 필수 + 소프트 규칙 + 디스크 old_string 매칭); 하네스는 CC pull(유휴+빈 큐면 완전 정지, isMeta+system-reminder 2비트) vs Grok push(SyntheticReason 12종 자동 주입, goal 분류기 되돌림 GoalClassifierNudge); 메모리는 CC LLM 셀렉터(벡터 의도적 거부, Sonnet 사이드쿼리 ≤5개 선택) vs Grok SQLite BM25+sqlite-vec KNN 하이브리드; 압축은 CC 절대 토큰 버퍼(윈도우−요약예약−13K, 200K≈83.5% / 1M≈96.7%) vs Grok 고정 85%; 위드홀드(모델 출력 잘림 8k→64k 에스컬, 플래그 tengu_otk_slot_v1 기본 off, 이어쓰기 ≤3회)는 CC 고유(Grok 소스 전역 grep 0건); KV캐시(CC 39기법·프리픽스 바이트 불변·cache-editing microcompact vs Grok 히스테리시스·skip-if-present)와 스마트배치(CC partitionToolCalls isConcurrencySafe 연속 병합 cap 10 barrier vs Grok FuturesUnordered+경로락)는 방식 다르나 대등.
- CC만의 장치: Read→Edit 하드 강제 + 쓰기 신선도 검증, 출력 잘림 이어쓰기(위드홀드), FILE_UNCHANGED_STUB 재읽기 dedup(~18% 절감), global KV 프롬프트 캐시. Grok만의 장치: 목표 달성 검증 루프(goal_classifier, skeptic/refuter), 유니코드 confusable 파일명 자동 복구, plan 모드가 yolo 포함 전 모드 쓰기 차단, wait 도구 biased select 인터럽트 우선순위, 도구명/파라미터 randomize+remap.
- Grok Build 정체 문답: 프론트엔드 아님 — grok CLI 전체 제품, TUI(xai-grok-pager) ↔ ACP(Agent Client Protocol) 인메모리 채널 ↔ 에이전트 런타임(xai-grok-shell 의 MvpAgent/SessionActor) 이 같은 프로세스에 공존, 헤드리스 grok -p / grok agent stdio 로도 동일 에이전트 구동. 언어는 전부 Rust(workspace edition 2024, tokio, ratatui — xai-ratatui-inline, xai-ratatui-textarea, crates/ 아래 64개 크레이트) vs CC 는 TypeScript(Node 단일 이벤트루프, Ink).
- /draw-arch 최종 건은 모드 1(좌/우 비교)로 확정, 질문된 6개 기능(툴서치·도구 스마트배치·도구 10단계 파이프라인·컨텍스트 전처리·시스템 리마인더·KV캐싱 준수) 전부 Grok에도 존재(방식만 다름)로 판정하고 arch-cc-vs-grok.html 별도 페이지 생성.
- 세션 모델은 /model 로 Opus 4.8 (1M context) 를 기본값 설정(2회).

## Open TODOs

- 마지막 턴 미완: arch-cc-vs-grok.html (10014 bytes) 생성·Playwright 스크린샷 확인("깔끔하게 나왔습니다")까지 완료, 남은 마무리 = http.server 8493 종료 + arch-check.jpeg 삭제 + 브라우저 open + 사용자 최종 보고 — 이 지점에서 대화 절단됨.
- 사용자 미응답 제안들: 특정 페이지 다이어그램 추가/수정, 라이트 테마 버전, Artifact 게시(공유 URL); "Grok Build 내부 = 프론트엔드(TUI) ↔ ACP ↔ 에이전트 런타임" 모드 2 단일 아키텍처 그리기 제안.
- CC 쪽 수치(cap 10, 훅 27, 39기법, 10단계 등)는 리버스 엔지니어링 기반 — 특정 수치가 중요해지면 그 부분만 재검증하기로 함.

## Constraints/Rules

- 사용자 선호(누적 피드백): 텍스트 산문보다 도표·플로우 중심 시각화; 멀티에이전트 기준 말고 메인 에이전트 단일 파이프라인 기준; 양(밀도) 우위 비교 말고 스마트 기능의 유무·특징·방식 비교.
- 모든 판정은 실제 소스 근거로 확인하고 각 섹션에 출처 표기; 미확인 항목은 정직하게 표기 (CC snipCompact·contextCollapse 소스 미확인, "Do NOT re-read" 불릿 src 무매치, CC wait 인터럽트는 ○ 없음 처리).
- CC 데이터는 리버스 엔지니어링 소스 기반이라 실제 Claude Code 최신 구현과 세부가 다를 수 있음을 사용자에게 고지 유지; Grok 쪽은 오픈소스 실측.
- CC 프로젝트 규칙(CLAUDE.md): 분석 산출물 참조는 가급적 md_group/ 마크다운 사용 (html_group_v2/ 는 동일 내용의 사람용 시각화 HTML).
- Playwright 는 file: 프로토콜 접근 차단 → 로컬 http.server(127.0.0.1) 경유 필수; sleep+poll 대기 명령은 차단됨(Monitor until-loop 사용); 서브에이전트 완료는 task-notification 으로 자동 통지됨.
- 도구결과 내부 메타데이터의 agentId 는 사용자 응대에 인용 금지.
- agent-report/ 는 git 미추적 로컬 폴더; 검증용 스크린샷 jpeg 과 임시 http.server 는 사용 후 삭제/종료.

## Pending user asks

- (진행 중, 미전달) /draw-arch 요청: "그록빌드에도 툴서치, 도구스마트배치, 도구10단계파이프라인, 컨텍스트전처리, 시스템 리마인더, KV캐싱준수 같은게 있어? 비교해주고 그리고 클로드코드외에 없는 개념도 알려주러" — 비교 페이지(arch-cc-vs-grok.html)는 만들어 시각 검증까지 마쳤으나 최종 정리·브라우저 열기·결과 보고가 절단되어 사용자에게 전달되지 않음.
- 그 외 미해결 ask 없음 — "그록빌드는 프론트엔드야?", "언어는뭔데?" 등 이전 질문은 모두 답변 완료.

## Exact identifiers

- 프로젝트 경로: /Users/seobi/jinsup_space/grok-build, /Users/seobi/jinsup_space/CC
- 리포트 폴더: /Users/seobi/jinsup_space/grok-build/agent-report/ — index.html, agent-core.html, shell-agent.html, subagent-system.html, tool-system.html, context-mgmt.html, integration.html, safety-config.html, tui-entry.html, prompt-flow.html, harness.html, cc-vs-grok.html, arch-cc-vs-grok.html (how-it-works.html 은 생성 후 삭제)
- scratchpad: /private/tmp/claude-501/-Users-seobi-jinsup-space-grok-build/e43b9dd8-0646-4fce-bb5a-a90ce1d59622/scratchpad/ — gen_report.py, harness_section.py, gen_compare.py, gen_compare_data.py, gen_pipeline.py, gen_loop.py, gen_features.py, gen_arch.py, grok-compare-facts.json; report-data/{agent-core,shell-agent,subagent-system,tool-system,context-mgmt,integration,safety-config}.json; cc-data/{core-subagent,tools-safety,context-memory,harness-distinctive}.json; loop-data/{cc-loop,grok-loop}.json; feature-data/{cc-features,grok-features}.json
- 워크플로우: Task ID w1my0wxpx (meta name: grok-build-agent-map), 출력 /private/tmp/claude-501/-Users-seobi-jinsup-space-grok-build/e43b9dd8-0646-4fce-bb5a-a90ce1d59622/tasks/w1my0wxpx.output, 전사 dir /Users/seobi/.claude/projects/-Users-seobi-jinsup-space-grok-build/e43b9dd8-0646-4fce-bb5a-a90ce1d59622/subagents/workflows/wf_9a26a79c-a27
- 백그라운드 셸 ID: b2tn2403v, bx62ly25t
- 분석 에이전트 task-id: a8752bd93066646e8 (CC 코어루프+서브에이전트), a23dc997f1afe2da0 (CC 도구+권한안전), a9f7727a4db2afea5 (CC 컨텍스트+메모리+압축), a6fb92bc393f47a98 (CC 하네스+자율실행+독특기술), a2c4dc12728bc0d87 (Grok 루프 사이클 계산밀도), a3ebca5e90db84411 (CC 루프 8단계 정밀 검증), a607e99639be5c466 (CC 스마트 기능 카탈로그), a2e9b7c9b93b3a9dc (Grok 스마트 기능 카탈로그)
- 포트(전부 127.0.0.1): 8477, 8478, 8479, 8481, 8483, 8485, 8487, 8489, 8491, 8493
- Grok 소스: crates/codegen/xai-grok-sampling-types/src/conversation.rs (SyntheticReason enum), turn_input.rs, turn_lifecycle.rs, turn.rs, dispatch/mod.rs, tool_calls.rs (execute_tool_calls), request_builder.rs, goal_classifier.rs, description.rs, run_search_replace, crates/codegen/xai-grok-pager-bin/src/main.rs, crates/codegen/xai-grok-workspace/src/permission/manager…, crates/common/xai-tool-types; 크레이트: xai-grok-agent, xai-agent-lifecycle, xai-grok-shell, xai-grok-subagent-resolution, xai-chat-state, xai-grok-compaction, xai-grok-memory, xai-acp-lib (agent-client-protocol v0.10.4), xai-grok-mcp, xai-grok-pager, xai-ratatui-inline, xai-ratatui-textarea
- Grok 식별자: FuturesUnordered, file_locks, HARD_CLEAR, prune_conversation, dedup_duplicate_tool_results, repair_dangling_tool_calls, skip_read_before_edit, update_goal(completed:true), GoalClassifierNudge, TurnInputContributor, TurnLifecycleContributor, TurnInputContext.synthetic, MvpAgent, SessionActor, run_stdio_agent, run_headless, run_leader, run_agent_server, AgentDefinition, AgentBuilder, ToolBridge, TurnOutcome, AccessKind, PermissionHandle, ConversationItem, ChatStateActor, TodoGate
- CC 소스/식별자: FileEditTool.ts:275-306, query.ts:364-463, readFileState, FileStateCache, errorCode 6, errorCode 7, FILE_UNCHANGED_STUB, partitionToolCalls, isConcurrencySafe, isReadOnly, needsFollowUp, msgToolUseBlocks.length > 0, checkPermissionsAndCallTool, toAutoClassifierInput, applyToolResultBudget, snipCompact, contextCollapse, tengu_otk_slot_v1, DYNAMIC_BOUNDARY, createSubagentContext, queryLoop, query(), Terminal{completed/aborted_tools/hook_stopped/max_turns}, isMeta, system-reminder, md_group/, html_group_v2/
- 수치 리터럴: cc-vs-grok.html 35701 → 16228 → 19294 → 20778 bytes; arch-cc-vs-grok.html 10014 bytes; 병렬 리더 7개 + gap-fill 1; prompt-flow 16단계; SyntheticReason 12종(WAKE 5 / STEER 4 / CONTEXT 3); 파이프라인 8단계; CC 도구 파이프라인 10단계 vs Grok ~12단계; cap 10; KV캐시 5전략 39기법; 훅 CC 27 vs Grok 14; 권한 CC ~9단 vs Grok 7단; 압축 Grok 85% 고정 vs CC 절대버퍼(윈도우−요약예약−13K, 200K≈83.5%, 1M≈96.7%); per-message 200K 예산; 위드홀드 8k→64k, continuation ≤3회; 요약 클래식 9섹션 / SM 10섹션 + tail 1만~4만 토큰; 이미지 토큰 CC 2000 vs Grok 765; 토큰 추정 CC JSON bytes/2 vs Grok bytes/4; FILE_UNCHANGED_STUB ~18% 절감; 기능 매트릭스 7카테고리 26기능(카탈로그 CC 28 / Grok 27, cc_unique 5); 64개 Rust 크레이트; workspace edition 2024
- 모델: Opus 4.8 (1M context) — /model 로 기본값 저장

## 단계 3~7: 미적용 (조건 미충족)

- 단계 3(이전 요약 재증류 래퍼): 이전 컴팩션 요약이 존재하지 않아 미적용.
- 단계 4(부분 요약 병합): 히스토리를 여러 파트로 쪼개지 않고 단일 요약으로 처리해 미적용.
- 단계 5(split-turn 프리픽스 요약): 턴 중간 절단 요약이 필요하지 않아 미적용.
- 단계 6(품질 가드 재시도): 필수 섹션 5개 전부 포함·식별자 원문 보존으로 재시도 트리거 없음.
- 단계 7(컴팩션 직후 컨텍스트 리프레시): AGENTS.md 치환부(Session Startup / Red Lines)가 이 시뮬레이션 범위 밖 파일이라 고정 문구만 해당 — 산출 생략.
