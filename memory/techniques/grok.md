# Grok (grok-build, xAI Rust 하네스) — 대화 메모리 / 컴팩션 기법

> 대상 레포: `/Users/seobi/jinsup_space/grok-build` (xAI Grok CLI. Rust workspace, `crates/common/xai-grok-compaction` + `crates/codegen/xai-grok-shell` + `crates/codegen/xai-grok-memory`)

## 개요

grok-build는 **"사전 플러시 → 풀 리플레이스 컴팩션 → 회상 재주입"의 3단 파이프라인**으로 긴 대화를 유지한다. 컨텍스트가 임계치에 접근하면 먼저 **메모리 플러시 턴**(도구 없는 별도 LLM 호출)이 대화에서 장기적으로 유용한 지식만 뽑아 디스크의 메모리 파일(`~/.grok/memory/`)에 기록하고, 그 다음 **풀 리플레이스 컴팩션**이 대화 전체를 9섹션 구조화 요약 하나로 갈아끼운다. 요약으로 잃어버린 세부는 (a) `<memory-context>` 재검색 주입(FTS5+벡터 하이브리드 검색), (b) 옵션인 `segments` 모드의 컴팩션 전 verbatim 마크다운 아카이브(`compaction/segment_*.md` + `INDEX.md`)로 되찾는다. 세션이 끝나면 **autoDream** 통합 패스가 쌓인 세션 로그를 장기 메모리 문서로 병합·모순 해소·정리한다. 같은 크레이트에 Grok chat(제품) 쪽의 intra(스텝 단위 tool-call 요약, tail-keep)/inter(턴 사이 청크 요약) 컴팩션도 함께 산다.

## 트리거

| 단계 | 트리거 |
|---|---|
| 사전 메모리 플러시 | 토큰 사용량 ≥ (컴팩션 임계치 − `soft_threshold_tokens` 헤드룸, 기본 4K) — 컴팩션보다 먼저 완료되도록 아래에서 발화. 컴팩션 사이클당 1회. 수동 `/flush`. (`memory_flush.rs::should_flush`) |
| 풀 리플레이스 컴팩션 | 마지막 프롬프트 토큰 / 컨텍스트 윈도우 ≥ **85%** (`DEFAULT_AUTO_COMPACT_THRESHOLD_PERCENT = 85`, env `GROK_AUTO_COMPACT_THRESHOLD_PERCENT`·설정·원격 플래그로 오버라이드). preflight 오버플로우·모델 스위치 시에도 호스트가 발화. 수동 `/compact [추가 컨텍스트]` — 추가 텍스트는 프롬프트의 `{user_context_section}`에 스플라이스됨. |
| 세션 종료 메타데이터 저장 | 세션 종료 시 LLM 호출 없이 통계 요약(메시지 수·토픽·시각)을 daily log에 기록. 3개 미만 substantive 프롬프트/50바이트 미만이면 스킵. |
| dream 통합 | 세션 종료 시 게이트 통과하면 자동: `enabled`(기본 true) + `min_hours`(4) + `min_sessions`(3). 수동 `/dream`. 입력 32K chars 캡(`MAX_DREAM_INPUT_CHARS`). |
| 회상(메모리 주입) | 세션 첫 턴(first-turn injection) + **컴팩션 직후**(요약으로 사라진 컨텍스트 복구) + 모델이 스스로 `memory_search`/`memory_get` 도구 호출. |

## 파이프라인

1. **사전 플러시** — 최근 메시지 윈도우(마지막 N개에서 User 경계까지 뒤로 확장, System 제외)에 `FLUSH_SYSTEM_PROMPT`를 붙여 도구 없이 호출. 응답 품질 게이트: 비어있음/`NO_REPLY` → 저장 안 함, `##` 헤더 없으면 거부, `max_flush_write_chars` 초과 시 잘라냄. 이어 **blake3 정확 해시 dedup + 임베딩 코사인 0.92 시맨틱 dedup**을 통과해야 daily log에 기록·인덱싱. 두 번째 이후 플러시는 `FLUSH_DELTA_SYSTEM_PROMPT`(이전 플러시 내용을 뒤에 붙여 "NEW만") 사용.
2. **요약 생성** — 대화 히스토리 끝에 요약 프롬프트를 마지막 user 메시지로 append하여 컴팩션 모델 호출(전용 `compaction_model_name` 설정 가능). 기본 `FullReplaceConfig`: 최대 3회 시도·3초 간격·호출당 120초 타임아웃. 정리 후 요약이 **500자 미만이면 degenerate**로 간주해 transient 실패처럼 재시도(`MIN_SUMMARY_SEED_CHARS = 500`).
3. **출력 정리** (`format_compact_summary`) — 선행 `<analysis>` 스크래치패드 제거, `<summary>…</summary>` → `Summary:\n…` 변환, 바디에 에코된 컨트롤 토큰(`<summary>`, `<analysis>`, `<summary_request>`)은 `<` 뒤에 zero-width space를 넣어 무력화(다음 턴이 요약 블록을 재발화하는 것 방지).
4. **히스토리 재조립** (`assemble_compacted_history`) — 컴팩션 후 히스토리는 정확히 이 순서:
   `[원본 시스템 프롬프트, <user_info> prefix, AGENTS.md <system-reminder>(요약자에 맡기지 않고 verbatim 재주입), 마지막 실제 user query(<user_query> 래핑), 마지막 user 턴 이후 최근 메시지 verbatim, "This session is being continued…" 프리앰블 + Summary(+transcript hint), <system-reminder>(활성 상태)]`
   마지막 `<system-reminder>`에는 실행 중 백그라운드 태스크·TODO 리스트·실행 중 서브에이전트(공용 3섹션, `reminder.rs`) + 호스트 전용 섹션(파일, 스킬, MCP, **메모리 검색 결과**)이 재렌더된다.
5. **회상 재주입** — `format_memory_reminder`가 검색 결과를 `<memory-context>` 태그 블록(`## Relevant Memory from Past Sessions`, 결과별 score/source/파일경로/라인범위/staleness note, 스니펫 500자 캡)으로 포맷해 주입. 검색은 하이브리드: 벡터 0.7 + BM25 0.3 가중, min score 0.35, 세션 청크만 temporal decay(반감기 7일), MMR 재랭킹 옵트인.
6. **로시 요약 보완 채널** (`CompactionMode`) — `summary`(기본, 포인터 없음) / `transcript`(원시 `updates.jsonl` 경로 힌트) / `segments`(컴팩션 전 verbatim 마크다운 세그먼트를 `compaction/segment_*.md` + `INDEX.md`(목차)로 보존하고, 요약 끝에 "read_file/grep으로 세부를 복구하라"는 힌트 문구를 붙임).
7. **dream 통합** — 게이트 통과 시 세션 로그(+기존 메모리 문서)를 `DREAM_SYSTEM_PROMPT`로 병합: 관련 정보 merge, 모순 해소(최신 사실만), 상대 날짜→절대 날짜 변환, 휘발성 정보 폐기, 결정·근거·아키텍처·문제/해결 보존. 성공 시 처리된 세션 로그 삭제 + 인덱스 정리.

## 산출물 구조 (풀 리플레이스 구조화 프롬프트, 9섹션)

`<summary>…</summary>` 단일 블록, 빈 섹션도 헤딩 유지("None"):

1. Primary Request and Intent
2. Key Technical Concepts
3. Files and Code Sections (최근 편집은 코드 전문 포함)
4. Errors and Fixes (사용자 피드백 발 수정은 verbatim)
5. Problem Solving
6. All User Messages (tool result 제외 전부 — 이 컴팩션 지시 자체는 제외하라고 명시)
7. Pending Tasks
8. Current Work
9. Optional Next Step (최근 메시지 verbatim 인용 필수, 완료된 작업이면 사용자 확인 우선)

상한: "aim for at most a few thousand words". 재주입 캐리어: `This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.\n\nSummary:\n…`

Grok chat 쪽 산출물: inter/history 프롬프트는 7섹션(Primary Request and Intent / Key Technical Concepts / Tool Usage & Verification / Files, Attachments, Images, Render Results & Code Artifacts / Errors and Fixes / Problem Solving / All User Messages), intra/steps 프롬프트는 6섹션(Task and Intent / Key Findings / Files and Code / Errors and Fixes / Actions Taken / Current Progress).

## 원문 프롬프트 발견 위치

| 프롬프트 | 위치 |
|---|---|
| 풀 리플레이스 구조화 요약 (grok-build 기본) | `crates/common/xai-grok-compaction/src/code_compaction/templates/full_replace_summary_prompt.txt` (전문, 19줄) — 빌더 `code_compaction/prompt.rs:15-26`. 쉘 인라인 사본 `crates/codegen/xai-grok-shell/src/session/helpers/session_compact.rs:191,225` |
| `SELF_SUMMARIZATION_PROMPT` (짧은 변형) | `crates/common/xai-grok-compaction/src/code_compaction/prompt.rs:34-45` (= `xai-grok-shell/src/session/helpers/session_compact.rs:25-36`) |
| `FLUSH_SYSTEM_PROMPT` / `FLUSH_DELTA_SYSTEM_PROMPT` | `crates/codegen/xai-grok-shell/src/session/helpers/memory_flush.rs:84-102 / 108-128` |
| `DREAM_SYSTEM_PROMPT` | `crates/codegen/xai-grok-memory/src/dream.rs:88-112` |
| Grok chat intra(steps) system/user | `crates/common/xai-grok-compaction/src/templates/intra_compaction_system.txt` / `intra_compaction_user.txt` (빌더 `steps/prompt.rs:14-19`) |
| Grok chat inter(history) developer/user (동일 내용 이중 주입) | `crates/common/xai-grok-compaction/src/templates/compaction_developer_prompt.txt` = `compaction_user_prompt.txt` (빌더 `history/prompt.rs`, 동일성 테스트로 고정) |
| 재주입 프리앰블 / `<user_query>` 래핑 | `crates/common/xai-grok-compaction/src/code_compaction/summary.rs:130-146` |
| transcript/segments 힌트 문구 | `crates/codegen/xai-chat-state/src/compaction_mode.rs:59-78` |
| 재조립 순서 | `crates/common/xai-grok-compaction/src/code_compaction/assemble.rs:62-102` |
| 임계치/재시도 상수 | `crates/common/xai-grok-compaction/src/code_compaction/config.rs:13,20,33-41` |

참고 문서(개요용): 루트 `mem-recipes.png`, `agent-report/memory-4way.html`, `agent-report/grok-memory-dream.html`, `crates/codegen/xai-grok-pager/docs/user-guide/13-memory.md` — 프롬프트 원문은 전부 위 소스에서 재확인함.

## 특이점 (다른 하네스와 구별되는 설계)

- **사전 플러시 + 컴팩션 2단 구조**: 컴팩션 임계치보다 소프트 헤드룸(기본 4K 토큰)만큼 낮은 지점에서 먼저 "기억할 것"을 디스크로 빼낸 뒤 요약한다. 요약 프롬프트 하나에 모든 것을 걸지 않는다. 플러시 결과는 blake3 + 임베딩(코사인 0.92) 이중 dedup을 거쳐야 저장.
- **요약자를 신뢰하지 않는 구조적 재주입**: AGENTS.md(프로젝트 지침), 마지막 user query, 활성 상태(<system-reminder>: TODO·백그라운드 태스크·서브에이전트)는 요약에 맡기지 않고 하네스가 verbatim으로 재조립한다.
- **요약 출력에 대한 방어 엔지니어링**: `<analysis>` 스크래치패드 스트리핑, 바디에 에코된 컨트롤 태그를 zero-width space로 무력화, 500자 미만 degenerate 요약 재시도 — 요약 실패·자기 재발화 루프를 코드로 막는다.
- **lossy 요약의 보완 채널이 1급 기능**: `segments` 모드는 컴팩션 전 대화를 verbatim 마크다운 아카이브(+INDEX.md 목차)로 남기고 요약에 "필요하면 read_file/grep으로 복구하라" 힌트를 붙인다. 요약 프롬프트에는 반대로 "그 파일들은 미래 에이전트용이니 지금 읽지 말라(도구 호출 금지)"는 가드 문단이 들어있다.
- **요약 모델 분리**: `compaction_model_name`으로 컴팩션 전용(더 싼) 모델 지정 가능.
- **한 크레이트, 세 가지 컴팩션 스타일**: grok-build의 full-replace / Grok chat의 intra(스텝 단위, tail-keep — 최근 턴은 남기고 오래된 tool-call 히스토리만 요약으로 교체) / inter(턴 사이 청크 요약). inter는 developer/user 프롬프트를 **동일 내용으로 이중 주입**하며 동일성을 테스트로 강제.
- **연쇄 컴팩션 인지**: 세 프롬프트 모두 "이전 컴팩션 요약이 히스토리에 있으면 그 내용을 전부 새 요약에 승계하라"를 명시(구조화 프롬프트는 CRITICAL, intra user 프롬프트는 "ConversationCompaction" 마커 언급).
- **intra 프롬프트의 언어 미러링**: "대화가 주로 중국어면 요약도 중국어로(기술 용어·경로·코드는 영어 유지)" — 다국어 사용자를 요약 단계에서 명시적으로 배려.
- **dream(수면 은유) 오프라인 통합**: 시간·세션 수 게이트 기반의 배치 패스가 세션 로그를 병합하며 모순 해소(최신 사실 승리), 상대 날짜→절대 날짜 변환, 휘발성 정보 폐기를 수행. `NO_REPLY` 이스케이프 해치를 플러시/드림 모두에 둬 "쓸 게 없으면 쓰지 마라"를 강제(저장 편향 억제).
- 별개로 goal 모드 종료 시 read-only 서브에이전트가 사용자용 마무리 요약(80단어/4불릿 하드캡)을 만드는 `goal_summarizer`도 있으나, 이는 대화 기억이 아니라 UX용 클로징 요약이다.
