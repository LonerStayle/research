# grok 하네스 컴팩션 시뮬레이션 — conv-06

## 단계 1: 사전 메모리 플러시 (FLUSH_SYSTEM_PROMPT)

## Decisions & rationale
- **Grok Build 에이전트 분석 리포트는 정적 HTML 멀티페이지 + 파이썬 생성기 방식으로 확정** — `scratchpad/gen_report.py` 하나가 워크플로우 수집 JSON(`report-data/*.json`)을 읽어 `/Users/seobi/jinsup_space/grok-build/agent-report/` 아래 페이지들을 재빌드한다. 데이터를 버리지 않고 원문 summary는 접이식으로 보존하는 원칙.
- **"쉽게 보기" 초보용 페이지(how-it-works.html)는 폐기하고 하네스(harness) 페이지로 교체** — 이 코드베이스에서 하네스는 `SyntheticReason`(12종) + `TurnInputContext.synthetic`을 축으로 "Idle 자리에 synthetic 프롬프트를 자동 주입해 사람 없이 루프를 닫는 상위 껍데기"라고 소스로 확정한 뒤 그 근거로만 그렸다. 추측으로 그리지 않고 grep으로 개념을 먼저 검증하는 방침.
- **CC vs Grok 비교 페이지(`cc-vs-grok.html`)는 사용자 피드백에 따라 같은 파일을 관점만 바꿔 3회 전면 재생성** — ① 6축 멀티에이전트 비교(gen_compare_data.py) → ② 메인 에이전트 단일 파이프라인 8단계(gen_pipeline.py) → ③ 루프 사이클 계산 밀도 히트맵(gen_loop.py) → ④ 스마트 기능 유무·방식 매트릭스(gen_features.py). 사용자는 멀티에이전트 관점·양적 우위 비교를 원치 않고 **단일 메인 루프의 특징(스마트 기능) 비교**를 원한다.
- **CC 쪽 수치는 리버스 엔지니어링 소스 기반이므로 결과물에 반드시 caveat 명시** (cap 10, 훅 27개, 39기법 등). Grok 쪽은 오픈소스 실측이라 확정 표기.
- 병렬 조사는 서브에이전트가 scratchpad 하위 디렉토리(`cc-data/`, `loop-data/`, `feature-data/`)에 JSON으로 저장하고 완료 알림(task-notification)으로 회수하는 패턴으로 통일.

## Technical context
- **Grok Build 저장소**: `/Users/seobi/jinsup_space/grok-build` — Rust workspace(edition 2024, tokio, ratatui), `crates/` 아래 64개 크레이트(`build`/`codegen`/`common`). 핵심: `xai-grok-agent`(AgentDefinition→AgentBuilder→Agent), `xai-grok-shell`(MvpAgent/SessionActor = 에이전트 런타임 서버), `xai-grok-subagent-resolution`(스폰 오버라이드>롤>페르소나>부모상속 우선순위), 도구 4계층(`xai-tool-types`/protocol/runtime/tools), `xai-chat-state`(ChatStateActor)·`xai-grok-compaction`·`xai-grok-memory`(SQLite BM25+sqlite-vec 하이브리드), `xai-acp-lib`(ACP JSON-RPC)·`xai-grok-mcp`, `xai-grok-pager`(TUI, Elm 사이클·biased select). TUI와 런타임은 같은 프로세스 안에서 ACP 인메모리 채널로 분리 — `grok -p` 헤드리스/`grok agent stdio` 임베드 가능.
- **하네스 개념 근거**: `crates/codegen/xai-grok-sampling-types/src/conversation.rs`의 `SyntheticReason` enum(12종: 깨우기 5/조향 4/맥락 3), `xai-agent-lifecycle/src/send/contributors/turn_input.rs`("harness produced the turn"), goal 하네스는 `update_goal(completed:true)` → 분류기 검증 → `GoalClassifierNudge` 되돌림.
- **CC 리서치 프로젝트**: `/Users/seobi/jinsup_space/CC` — Claude Code 리버스 엔지니어링(src/ = TS 소스, md_group/ = 분석 문서, html_group_v2/ = 시각화판).
- **비교로 확정된 핵심 사실**:
  - Grok 도구 실행은 순차가 아니라 **2-phase 병렬 배치**: 순차 권한 게이트로 approved 수집 → `FuturesUnordered` 동시 dispatch + per-path Mutex(`file_locks`)로 동일 파일 쓰기만 직렬화, ~12단계 prepare 파이프라인 (`tool_calls.rs execute_tool_calls`).
  - Grok 컨텍스트 전처리: `dedup_duplicate_tool_results` + `repair_dangling_tool_calls` → 히스테리시스 이미지 eviction → 50% 초과 시 tool-result pruning(HARD_CLEAR 스텁) → 메모리 주입. KV캐시 prefix 보존은 request_builder.rs에서 캐시 미스 비용을 명시 계산할 만큼 캐시 인지적.
  - Grok에 **위드홀드 패턴 없음**(전역 grep 0건), continuation 판정은 `tool_calls.is_empty()` 기계적 게이트. CC도 `needsFollowUp = msgToolUseBlocks.length > 0`로 기계적 — "thinking에서 판단"은 CC조차 사실 아님.
  - CC Read→Edit는 **런타임 하드 게이트**(`FileEditTool.ts:275-306`, `readFileState` 조회 errorCode 6, mtime 신선도 errorCode 7). Grok은 런타임 게이트 없음 — config-time 요구(`skip_read_before_edit=false`면 toolset에 Read 필수) + 도구 description 소프트 규칙 + old_string 디스크 매칭.
  - 메모리: CC는 벡터 의도적 거부(LLM 셀렉터, Sonnet 사이드쿼리 ≤5개) vs Grok SQLite 벡터 하이브리드. 압축: CC 절대 토큰 버퍼(200K≈83.5%, 1M≈96.7%) vs Grok 고정 85%.
  - CC 고유: 위드홀드 출력잘림 복구(8k→64k, `tengu_otk_slot_v1`, 이어쓰기 ≤3회), `FILE_UNCHANGED_STUB` dedup(~18%), global 프롬프트 KV캐시, KV 5전략 39기법. Grok 고유: goal 분류기 검증 루프, 유니코드 confusable 파일명 자동 복구, plan 모드가 yolo에서도 쓰기 차단, 도구명/파라미터 randomize+remap, wait 도구 biased select 인터럽트.
  - 하네스: CC는 pull(유휴+빈 큐면 완전 정지, isMeta+system-reminder 2비트) vs Grok push(synthetic 자동 주입, 12종 enum).
- **산출물**: `agent-report/` 페이지 — index, agent-core, shell-agent, subagent-system, tool-system, context-mgmt, safety-config, integration, tui-entry, prompt-flow(질문 여정 16단계), harness, cc-vs-grok(현재는 스마트 기능 매트릭스판), arch-cc-vs-grok(/draw-arch 산출, 6기능 좌/우 SVG 비교).

## Debugging techniques & tools
- **Playwright MCP 렌더링 검증 루프**: `file://` 프로토콜은 차단되므로 `python3 -m http.server <port> --bind 127.0.0.1 --directory <dir>`(백그라운드)로 서빙 → `browser_navigate` → `browser_evaluate`로 DOM 노드 수 카운트(리빌 요소 `.rv.in`, 단계 `.step`, 매트릭스 행 등) → `browser_take_screenshot`(fullPage jpeg) → 스크린샷 파일을 Read로 육안 검증 → pkill로 서버 정리 + 스크린샷 삭제 + `open`으로 인도.
- **개념 검증 grep 워크플로우**: 새 페이지를 그리기 전 `grep -rli "harness"`, `enum SyntheticReason` 정의 검색 등으로 코드베이스 내 실제 의미부터 확정. 부재 증명도 grep 0건으로 명시(위드홀드).
- **병렬 서브에이전트 조사 패턴**: 축별 프롬프트로 Agent를 병렬 스폰 → 각자 scratchpad에 검증된 JSON 저장 → task-notification으로 회수. `sleep 30` 대기는 차단됨 — Monitor until-loop 또는 완료 알림 대기 사용.
- zsh에서 `--include=*.rs`는 따옴표 필요(`--include="*.rs"`), 아니면 "no matches found".

## Problems & solutions
- **워크플로우 결과 파싱 버그 2건**: shell-agent 흐름 7단계 유실, tui-entry 한국어 서수("1) 2) …") 분리 실패 — 파이썬 스플리터 정규식을 고쳐 해결. 레이아웃 버그 1건(통계 그리드 미적용)은 스크린샷 검증으로 발견·수정.
- **http.server 404**: 루트에서 서버를 띄우고 `/agent-report/index.html` 접근 → 404. `--directory` 옵션으로 리포트 폴더를 직접 서빙해 해결.
- **gen_compare_data.py `SyntaxError: unmatched ')'`**: 할당을 리스트로 잘못 이어붙임 — `ast.parse`로 검증하며 구조를 리스트로 정리해 해결.
- **"Grok 도구 순차 실행" 오판 정정**: 초기 비교에서 순차라고 결론냈으나 소스 재조사(`FuturesUnordered`+per-path Mutex)로 병렬 배치임을 확인, 이후 페이지에서 공개 정정.
- **API Error mid-response**: visual-explainer 스킬 호출 직후 서버 오류로 응답 절단 — 사용자 "이어서 해봐" 후 작업 상태(태스크 출력 파일)에서 재개.
- 사용자 의도 반복 미스매치: 멀티에이전트 관점(×) → 파이프라인 나열(×) → 양적 밀도 비교(×) → **스마트 기능 유무·방식 비교(○)**. 이 사용자는 "특징·유무" 매트릭스와 도표 위주 산출을 원함.

## 단계 1b: 증분 플러시 (FLUSH_DELTA_SYSTEM_PROMPT)

NO_REPLY

## 단계 2: 풀 리플레이스 컴팩션 (구조화 요약)

<summary>
1. Primary Request and Intent:
사용자는 `/Users/seobi/jinsup_space/grok-build`(xAI Grok Build, Rust 터미널 AI 코딩 에이전트 오픈소스)를 **에이전트 로직 위주로** 파악하고 시각화하길 원한다. 요청의 진화:
- 멀티에이전트 워크플로우로 저장소 전체를 에이전트 중심으로 분석하라.
- 분석 결과 전부를 **여러 페이지 HTML** 리포트로 만들라 (중간에 API 오류 후 "이어서 해봐").
- "질문을 받으면 어떤 흐름이 생기는지" HTML 페이지 추가.
- "처음 보는 관점의 에이전트 로직"을 **텍스트 말고 도표/플로우 위주로** — 결과적으로 하네스(synthetic 턴 자동 주입) 페이지로 정착.
- `/Users/seobi/jinsup_space/CC`(Claude Code 리버스 엔지니어링 리서치 프로젝트)와 **에이전트 로직 비교**를 시각 위주로.
- 제약 정정 연속: 멀티에이전트 기준 말고 **하나의 메인 에이전트 파이프라인** 기준으로 → 단계 나열 말고 **루프 한 사이클이 얼마나 계산적인지**(위드홀드·스마트배치·10단계 파이프라인·어태치먼트·KV캐싱·thinking 판단) → 양적 우위 말고 **스마트 기능의 유무·특징**(Read→Edit 하드 규칙, 툴콜 순서 소프트 규칙, 세션 보고 건너뛰기 등)을 비교.
- 마지막으로 `/draw-arch`로 "그록빌드에도 툴서치·도구스마트배치·도구10단계파이프라인·컨텍스트전처리·시스템 리마인더·KV캐싱준수 같은 게 있어? 비교해주고 클로드코드 외에 없는 개념도 알려줘" — 좌/우 비교 SVG 아키텍처 페이지 요청.
스타일 선호: 도표·플로우 중심, 한국어 산출물, 근거는 실제 소스 라인으로 검증, CC 쪽은 리버스 소스라는 한계 명시.

2. Key Technical Concepts:
- Grok Build: Rust workspace(edition 2024)·tokio·ratatui, 64 크레이트; MvpAgent/SessionActor 스레드-퍼-세션 액터; ACP(Agent Client Protocol) 인메모리 JSON-RPC로 TUI/런타임 분리; AgentDefinition→AgentBuilder→Agent; 서브에이전트 3축 합성(타입×롤×페르소나); 도구 4계층 스택; ChatStateActor; 85% 고정 컴팩션 + transcript/segments grep 회수; SQLite BM25+sqlite-vec 하이브리드 메모리; SyntheticReason 12종 기반 push형 하네스; goal 분류기 검증 루프(GoalClassifierNudge); FuturesUnordered + per-path Mutex 병렬 도구 배치; KV캐시 prefix 보존(히스테리시스 이미지 eviction, skip-if-present); 유니코드 confusable 파일명 복구; 도구명 randomize+remap; plan 모드 전역 쓰기 차단.
- Claude Code(CC, 리버스 분석): queryLoop while(true) 상태머신(Terminal{completed/aborted_tools/hook_stopped/max_turns}); 단일 Node 이벤트루프 협력적 async generator; partitionToolCalls(isConcurrencySafe 연속 병합, cap 10, barrier); checkPermissionsAndCallTool 10단계 도구 파이프라인; 위드홀드 출력잘림 복구(8k→64k, tengu_otk_slot_v1, 이어쓰기 ≤3회); per-message 200K 예산 디스크 오프로드; 어태치먼트 T1~T4+T-A(주로 T3); KV캐시 5전략 39기법(프리픽스 바이트 불변, cache-editing microcompact); 절대 토큰 버퍼 auto-compact(200K≈83.5%, 1M≈96.7%); 벡터 거부 LLM 메모리 셀렉터; readFileState 기반 Read→Edit 하드 게이트; FILE_UNCHANGED_STUB dedup(~18%); isMeta+system-reminder 2비트; pull형(유휴+빈 큐 완전 정지).
- 공통 수렴: ReAct 골격, 자식 세션 서브에이전트+worktree 격리+auto-wake, 커널 샌드박스, 다단 권한 캐스케이드(CC ~9단/Grok 7단), LLM 권한 분류기, 압축 후 grep 회수. 계속 판단은 양쪽 다 기계적(tool_use/tool_calls 유무).

3. Files and Code Sections:
(도구 호출 원문이 절단된 transcript 특성상 생성 코드 전문은 없음 — 아래는 경로·역할·확인된 코드 사실)
- `/Users/seobi/jinsup_space/grok-build/agent-report/` — 최종 산출물 폴더(git 미추적): index.html, agent-core.html, shell-agent.html, subagent-system.html, tool-system.html, context-mgmt.html, safety-config.html, integration.html, tui-entry.html, prompt-flow.html(질문 여정 16단계), harness.html(SyntheticReason 12종 3그룹), cc-vs-grok.html(4회 재생성, 현재 = 스마트 기능 매트릭스 26개·7카테고리·범례 ●하드/◐소프트/▲다른방식/○없음), arch-cc-vs-grok.html(/draw-arch 산출, 10014 bytes).
- scratchpad(`/private/tmp/claude-501/-Users-seobi-jinsup-space-grok-build/e43b9dd8-0646-4fce-bb5a-a90ce1d59622/scratchpad/`):
  - `gen_report.py` — 메인 리포트 생성기(ORDER/NAV/META/CARD_DESC, 다크 회로 스키매틱 CSS, 스크롤 리빌 JS). 수차례 Edit로 페이지 추가·문구 갱신.
  - `harness_section.py` — render_how를 render_harness로 통째 교체하기 위한 스플라이스 소스.
  - `gen_compare.py`/`gen_compare_data.py`(6축 비교), `gen_pipeline.py`(8단계 파이프라인), `gen_loop.py`(밀도 히트맵), `gen_features.py`(기능 매트릭스), `gen_arch.py`(draw-arch SVG) — 전부 같은 cc-vs-grok.html 또는 arch-cc-vs-grok.html을 재생성.
  - `report-data/*.json`(워크플로우 7+1축), `cc-data/{context-memory,core-subagent,harness-distinctive,tools-safety}.json`, `loop-data/{cc-loop,grok-loop}.json`, `feature-data/{cc-features,grok-features}.json`, `grok-compare-facts.json`.
- Grok 소스(읽음): `crates/codegen/xai-grok-sampling-types/src/conversation.rs`(SyntheticReason enum, offset 60~), `xai-agent-lifecycle/src/send/contributors/turn_input.rs`·`turn_lifecycle.rs`("harness" 언급), `tool_calls.rs`(execute_tool_calls — FuturesUnordered+file_locks), `request_builder.rs`(KV캐시), `run_search_replace`·`goal_classifier.rs`(서브에이전트 조사).
- CC 소스/문서(서브에이전트가 읽음): `src/` TS(예: `FileEditTool.ts:275-306` — readFileState 조회, errorCode 6 "File has not been read yet"/errorCode 7 stale, `query.ts:364-463` 전처리 5단), `md_group/` 분석 문서군.
- 확인된 핵심 코드 사실(짧은 인용): CC `needsFollowUp = msgToolUseBlocks.length > 0`; Grok `tool_calls.is_empty()`; Grok 전처리 `dedup_duplicate_tool_results` + `repair_dangling_tool_calls`; CC `partitionToolCalls` reduce/cap 10/barrier.

4. Errors and Fixes:
- visual-explainer 호출 직후 "API Error: Server error mid-response" → 사용자 "이어서 해봐"로 재개, 태스크 출력 파일(`tasks/w1my0wxpx.output`)에서 데이터 파싱해 계속.
- Playwright `file://` 차단("Access to \"file:\" protocol is blocked") → 로컬 http.server로 우회.
- http.server 8477에서 404(File not found) → `--directory /Users/seobi/jinsup_space/grok-build/agent-report` 지정한 8478로 재기동해 해결. favicon.ico 404 콘솔 에러는 무해.
- 워크플로우 JSON 파싱 버그 2건(shell-agent 흐름 7단계 유실, tui-entry 한국어 서수 "1) 2)" 분리 실패)과 레이아웃 버그 1건(통계 그리드 미적용) → gen_report.py의 render_flow/render_notable/CSS Edit로 수정, 스크린샷으로 확인.
- `gen_compare_data.py` `SyntaxError: unmatched ')'`(line 195) → ast.parse 검증하며 리스트 구조로 정리, "syntax OK".
- `sleep 30` 단독 대기 Bash 차단(tool_use_error) → 완료 알림(task-notification) 대기로 전환.
- zsh `--include=*.rs` "no matches found" → 따옴표로 감싸 재실행.
- **내용 오류 정정(사용자 피드백+소스 재조사)**: "Grok 도구 순차 실행" 주장은 틀림 — 실제는 FuturesUnordered 병렬 배치 + per-path Mutex. 또한 "이어서할지 thinking에서 판단"은 CC조차 사실 아님(기계적 tool_use 게이트).

5. Problem Solving:
- 저장소 전체 → 7+1축 병렬 탐색(워크플로우 w1my0wxpx) → 9페이지 리포트로 통합, 이후 사용자 관점 전환마다 같은 데이터+추가 조사로 페이지를 재구성하는 문제를 반복 해결.
- "하네스"의 실제 의미를 소스로 확정(SyntheticReason/synthetic 턴)한 뒤에만 시각화.
- CC vs Grok 비교의 정직성 확보: 4+2+2개 병렬 서브에이전트가 소스 라인 근거 JSON을 저장, 미확인 항목은 명시(예: CC snipCompact·contextCollapse 미포함, "Do NOT re-read" 불릿 무매치).
- 진행 중이던 진단 없음 — 마지막 arch 페이지의 콘솔 에러 1건(내비게이트 시)만 확인 전.

6. All User Messages:
- "프로젝트 전체 다 파악해봐 특히 에이전트 위주로만 말야 자 워크플로우 시작해!"
- "결과를 전부 모아서 여러 페이지의 html 를 만들어줘"
- "이어서 해봐"
- "음.. 질문을 받으면 어떤 흐름이 생기는지에 대한 html좀 그려줘"
- [슬래시커맨드 /model + stdout: "Set model to Opus 4.8 (1M context) (default)"] (2회)
- "뭐라는지 하나도 모르겠다... 나처음보ㅓ는데.... 처음보는관점의 에이전트로직 좀 만들어봐.. 텍스트말고 도표나 플로우위주로 .."
- "@/Users/seobi/jinsup_space/CC 이게 클로드코드 프로젝트야 여기 에이전트 로직과 비교해서 /visual-explainer 로 만들어줘 시각적인거 위주로"
- [task-notification 6건 — CC 4축 분석(a9f77…/a8752…/a6fb9…), Grok/CC 루프 해부(a2c4d…/a3ebc…), 스마트 기능 카탈로그(a607e…/a2e9b…) 완료 통지]
- "제발 멀티에이전트기준으로 얘기하지말고.. 하나의 메인에이전트 파이프라인 기준으로 비교해봐 ㅠㅜ"
- "루프적인 모습을봐야지 클로드코드는 전처리 -> 위드홀드패턴 + (LLM호출) -> 도구 스마트배치 세팅 -> 도구 10단계 파이프라인 진행 -> 전체 배치완료 후 tool_results 묶음, 적절한 어태치먼트 삽입 -> 다음 사이클 컨텍스트전처리 -> 전체적인 tool_results + 어태치먼트및 시스템리마인드 과다 전송(이때 KV캐싱 구성) -> 이어서할지말지 thinking 에서 판단 / 이렇단 말야 그록도 이렇게 엄청 디테일하게 루프가 계산적이냐구;"
- "❯ 음... 각 단계 파이프라인을.. 뭔가 양으로 우위 비교하지말구... 흐...흠... 특징을 비교해야지  클로드코드의 도구 배치 세팅할때 그 Read -> Edit 강제 하드규칙이나 그외 툴콜링순서 소프트규칙이있기도하고 그러거든.. 클로크돜드가 대화세션보고 뛰어넘길때도 있고 .. 아무튼 이러한 스마트 기능들이있는지 알고싶어"
- [슬래시커맨드 /draw-arch]
- "그록빌드는 프론트엔드야?"
- "언어는뭔데?"
- "그록빌드에도 툴서치, 도구스마트배치, 도구10단계파이프라인, 컨텍스트전처리, 시스템 리마인더,KV캐싱준수  같은게 있어? 비교해주고 그 그리고 클로드코드외에 없는 개념도 알려주러 /draw-arch"

7. Pending Tasks:
- `/draw-arch` 좌/우 비교 페이지(`arch-cc-vs-grok.html`) 마무리: 서버(8493)/스크린샷 정리 → `open`으로 열기 → 6개 기능(툴서치·스마트배치·10단계 파이프라인·컨텍스트 전처리·시스템 리마인더·KV캐싱)의 양측 대응 + 한쪽에만 있는 고유 개념 요약을 사용자에게 전달.

8. Current Work:
직전 작업: `gen_arch.py` 작성 → `agent-report/arch-cc-vs-grok.html`(10014 bytes) 생성 → http.server 8493으로 서빙, Playwright로 내비게이트(타이틀 "CC vs Grok — 루프 기능 아키텍처 비교", 콘솔 에러 1건 관찰) → fullPage 스크린샷 `arch-check.jpeg` 촬영·Read로 육안 검증 완료. 검증 소견: 좌(주황 CC)/우(초록 Grok) 루프 나란히, 가운데 ✓ 라벨 6개 기능, 하단 점선 박스에 고유 개념, 루프백 화살표, 라이트/다크 모드 대응. 남은 것: `pkill -f "http.server 8493"` + `rm -f arch-check.jpeg` + `open .../agent-report/arch-cc-vs-grok.html` 후 최종 응답(6개 기능은 Grok에 전부 존재하되 방식이 다름 + CC 고유/Grok 고유 개념 정리) 전달. 응답 도중 transcript가 절단됨.

9. Optional Next Step:
정리 명령(서버 종료·스크린샷 삭제) 실행 후 `arch-cc-vs-grok.html`을 열고 최종 비교 설명을 전달한다. 직전 어시스턴트 메시지 인용: "깔끔하게 나왔습니다. 좌(주황 CC) / 우(초록 Grok) 루프가 나란히 흐르고, 가운데 ✓ 라벨이 질문하신 6개 기능… 정리하고 엽니다." — 사용자 최신 요청("그록빌드에도 툴서치, 도구스마트배치, … 있어? 비교해주고 … 클로드코드외에 없는 개념도 알려주러 /draw-arch")의 직접 연속이며, 이미 응답 서두에 "먼저 답부터: 6개 전부 Grok에도 있습니다 (방식만 다름)"라고 예고한 결론을 완성하면 된다.
</summary>

## 단계 3: 재주입 캐리어 텍스트 (하네스 조립)

This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
(위 단계 2의 <summary> 본문이 {cleaned} 자리에 삽입됨 — 치환 변수이므로 생략)

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: (transcript 경로 — {loc} 치환 변수이므로 생략)

## 단계 4: 장기 메모리 통합 (DREAM_SYSTEM_PROMPT)

## Grok Build 저장소 구조 (에이전트 중심)
`/Users/seobi/jinsup_space/grok-build`는 xAI의 터미널 AI 코딩 에이전트 오픈소스로, 전부 Rust(workspace edition 2024, tokio) 64개 크레이트다. TUI(`xai-grok-pager`, ratatui)와 에이전트 런타임(`xai-grok-shell`의 MvpAgent/SessionActor)이 같은 프로세스에서 ACP 인메모리 JSON-RPC로 분리되어, 헤드리스(`grok -p`)·IDE 임베드(`grok agent stdio`)에서도 동일 에이전트가 돈다. 에이전트 정의는 `xai-grok-agent`의 AgentDefinition(.grok/agents/*.md YAML frontmatter)→AgentBuilder→Agent 파이프라인, 서브에이전트는 `xai-grok-subagent-resolution`이 명시 오버라이드>롤>페르소나>부모상속 우선순위로 해석. 도구는 4계층(xai-tool-types/protocol/runtime/tools), 대화 상태는 ChatStateActor(전용 tokio task 단독 소유), 컴팩션은 85% 고정 트리거 + transcript/segments grep 회수, 메모리는 SQLite BM25+sqlite-vec 하이브리드.

## Grok Build 하네스 개념
이 코드베이스의 "하네스"는 에이전트가 Idle로 멈춘 자리에 런타임이 synthetic 프롬프트를 자동 주입해 사람 없이 루프를 닫는 상위 껍데기다. 근거: `xai-grok-sampling-types/src/conversation.rs`의 `SyntheticReason` enum 12종(깨우기 5/조향 4/맥락 3), `turn_input.rs`의 synthetic 턴 플래그. 목표 하네스는 `update_goal(completed:true)` 주장을 분류기가 검증해 미달이면 `GoalClassifierNudge`로 되돌린다. 하네스는 루프를 소유하지 않고 TurnInputContributor(주입)/TurnLifecycleContributor(관찰)로만 개입한다.

## Claude Code vs Grok Build 비교 결론 (소스 검증)
- 골격 수렴: 양쪽 다 ReAct 루프(CC queryLoop while(true) 상태머신 / Grok run_turn→execute_tool_calls), 자식 세션 서브에이전트+worktree 격리+완료 auto-wake, 커널 샌드박스, 다단 권한 캐스케이드+LLM 권한 분류기, 압축 후 grep 회수까지 동일. **계속 판단은 양쪽 다 기계적** — CC `needsFollowUp = tool_use 블록 유무`, Grok `tool_calls.is_empty()`. "thinking에서 판단"은 통념일 뿐 사실이 아니다.
- 갈리는 축: 동시성(CC 단일 Node 이벤트루프 + partitionToolCalls 배치 병렬 cap 10/barrier vs Grok 스레드-퍼-세션 액터 + 순차 권한 게이트 후 FuturesUnordered 병렬 + per-path Mutex — **Grok 도구 실행을 순차로 보면 오판**), 지속성(CC pull — 유휴+빈 큐면 완전 정지, isMeta+system-reminder 2비트 vs Grok push — SyntheticReason 12종 자동 주입), 메모리(CC 벡터 의도적 거부 → Sonnet LLM 셀렉터 ≤5개 vs Grok SQLite 벡터 하이브리드), 압축 트리거(CC 절대 토큰 버퍼: 200K≈83.5%·1M≈96.7% vs Grok 고정 85%), 토큰 추정(CC 실 API usage 앵커 vs Grok bytes/4).
- CC 고유 장치: Read→Edit **런타임 하드 게이트**(FileEditTool.ts:275-306 — readFileState 미존재/부분읽기 errorCode 6, mtime 변경 errorCode 7 재읽기 강제), 위드홀드 출력잘림 복구(8k→64k 에스컬 tengu_otk_slot_v1, 이어쓰기 ≤3회; 대용량 도구 결과는 별도 per-message 200K 예산), FILE_UNCHANGED_STUB 재읽기 dedup(~18% 절감), KV캐시 5전략 39기법(프리픽스 바이트 불변, cache-editing microcompact), global 프롬프트 캐시.
- Grok 고유 장치: goal 분류기 검증 루프, 유니코드 confusable 파일명 자동 복구, plan 모드가 yolo 포함 전 모드에서 쓰기 차단, 도구명/파라미터 randomize+remap(도구명이 바뀌어도 read→grep→edit 순서를 안정 렌더하는 템플릿), wait 도구 biased select 인터럽트 우선순위, KV캐시 히스테리시스 이미지 eviction. Grok에 위드홀드 패턴은 없음(전역 grep 0건).
- 신뢰도 주의: CC 쪽 수치(cap 10, 훅 27, 39기법, 10단계)는 `/Users/seobi/jinsup_space/CC`의 리버스 엔지니어링 소스 기반이라 실제 최신 구현과 다를 수 있다. Grok 쪽은 오픈소스 실측.

## 산출물: agent-report HTML 리포트
`/Users/seobi/jinsup_space/grok-build/agent-report/`(git 미추적)에 파이썬 생성기(`gen_report.py` 등 scratchpad 스크립트)가 만드는 다크 "회로 스키매틱" 디자인 페이지들: 개요+8개 서브시스템(agent-core/shell-agent/subagent-system/tool-system/context-mgmt/safety-config/integration/tui-entry), prompt-flow(질문 하나의 16단계 여정), harness, cc-vs-grok(사용자 피드백에 따라 6축 비교→단일 파이프라인 8단계→루프 밀도 히트맵→**스마트 기능 매트릭스**(7카테고리 26기능, ●하드/◐소프트/▲다른방식/○없음)로 4회 재구성), arch-cc-vs-grok(/draw-arch 좌/우 SVG). 원문 데이터를 버리지 않고 접이식 보존하는 원칙.

## 작업 패턴 (이 사용자와의 협업)
- 사용자는 도표/플로우 중심 시각 산출물을 원하며, 멀티에이전트 얘기보다 **메인 에이전트 한 바퀴의 스마트 기능(유무·방식·특징)** 관점을 선호. 양적 우위 비교는 반려됨.
- 조사 방법: 축별 병렬 서브에이전트가 scratchpad 하위에 검증 JSON 저장 → task-notification 회수 → 생성기 스크립트로 페이지 조립. 개념(하네스 등)은 시각화 전에 grep으로 소스 확정, 부재 주장도 grep 0건으로 증명.
- HTML 검증: Playwright는 file:// 차단이므로 `python3 -m http.server --bind 127.0.0.1 --directory <dir>` 서빙 후 navigate→evaluate(DOM 카운트)→fullPage 스크린샷→Read 육안 검증→서버/스크린샷 정리. `sleep N` 단독 대기는 차단(Monitor until-loop 사용), zsh `--include=*.rs`는 따옴표 필요.
