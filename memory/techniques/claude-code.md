# Claude Code — 대화 메모리/컴팩션 요약 기법

> 근거 소스: `/Users/seobi/jinsup_space/CC/src/` (Claude Code 재구성 소스 번들). 모든 인용은 `파일:라인`.
> 개요 참고 문서: `/Users/seobi/jinsup_space/CC/메모리-회상-파이프라인-총정리.md` (회상 파이프라인 중심 — 프롬프트 원문은 전부 소스에서 재확인함)

## 개요

Claude Code의 메모리 전략은 **3층 방어선**이다. (1) **마이크로컴팩트** — LLM 없이 오래된 도구 결과를 기계적으로 비우는 저비용 1차 방어(`[Old tool result content cleared]`), (2) **세션메모리(사전 플러시)** — 대화가 진행되는 동안 백그라운드 포크 에이전트가 주기적으로 구조화된 노트 파일(10개 섹션 마크다운)을 Edit 도구로 증분 갱신, (3) **오토컴팩트** — 컨텍스트 임계치 도달 시 대화 전체를 9개 섹션 구조의 상세 요약으로 압축해 대화를 통째로 교체. 컴팩션 시점에는 **세션메모리가 이미 채워져 있으면 LLM 호출 없이 그 파일을 그대로 요약으로 재활용**(SM-compact)하고, 없을 때만 요약 LLM 호출(legacy compact)을 한다. 요약 호출은 메인 대화의 프롬프트 캐시를 공유하는 포크 에이전트(`maxTurns: 1`)로 실행해 비용을 극단적으로 절감한다.

## 트리거

| 계층 | 트리거 | 근거 |
|---|---|---|
| 마이크로컴팩트 (시간 기반) | 마지막 assistant 메시지 후 **60분 경과**(서버 캐시 TTL 만료 확정) 시 API 호출 전에 오래된 도구 결과 클리어, 최근 5개 유지 | `src/services/compact/timeBasedMCConfig.ts:30-34`, `microCompact.ts:258-268` |
| 세션메모리 추출 | 샘플링 후 훅(post-sampling hook)에서: 최초 **10K 토큰** 도달로 초기화 → 이후 **토큰 +5K 성장(필수) AND (도구 호출 3회 이상 OR 직전 턴에 도구 호출 없음=자연스러운 대화 단락)** | `sessionMemoryUtils.ts:32-36`, `sessionMemory.ts:134-181` |
| 오토컴팩트 | 토큰 수 ≥ `유효 컨텍스트 창(창 크기 − min(모델 최대출력, 20K)) − 13K 버퍼` | `autoCompact.ts:30, 62, 72-91` |
| 수동 `/compact` | 사용자 명령. 커스텀 지시(`/compact <지시>`)를 프롬프트에 `Additional Instructions:`로 첨부 | `prompt.ts:293-303`, `compact.ts:387-` |
| 부분 컴팩트 | REPL에서 특정 메시지 인덱스를 피벗으로 선택 — `from`(최근만 요약) / `up_to`(앞부분만 요약) 두 방향 | `compact.ts:766-800`, `screens/REPL.tsx:4943` |
| 서킷 브레이커 | 오토컴팩트 **연속 3회 실패** 시 세션 내 재시도 중단 (BQ 분석: 실패 세션이 하루 ~25만 API 호출 낭비) | `autoCompact.ts:67-70, 257-265` |
| PTL 재시도 | 컴팩트 요청 자체가 prompt-too-long이면 가장 오래된 API 라운드 그룹부터 잘라 **최대 3회** 재시도 | `compact.ts:227, 460-491` |

## 파이프라인

```
[대화 진행 중 — 상시]
  ├─ microcompact: 60분 갭 감지 시 오래된 도구 결과 기계적 클리어 (LLM 없음)
  └─ 세션메모리 사전 플러시: 임계치 충족 시 포크 에이전트(querySource: 'session_memory')가
     ~/.claude/.../session-memory 파일을 Edit 도구로 증분 갱신 (메인 대화 캐시 공유, 논블로킹)

[임계치 도달 — autoCompactIfNeeded]
  ① trySessionMemoryCompaction 먼저 시도 (EXPERIMENT, 기능 플래그 tengu_session_memory + tengu_sm_compact):
     세션메모리 파일에 실제 내용이 있으면 → LLM 호출 0회.
     파일 내용(섹션당 2000토큰 컷) 자체를 요약으로 삼고,
     lastSummarizedMessageId 이후 메시지를 보존 (최소 10K토큰/텍스트 5개, 최대 40K토큰,
     tool_use/tool_result 쌍·thinking 블록 불변식 보정)
  ② 실패/미적용 시 legacy compactConversation:
     PreCompact 훅 → getCompactPrompt()로 요약 요청 user 메시지 생성 →
     runForkedAgent(maxTurns:1, querySource:'compact', 메인 캐시 프리픽스 공유, thinking 유지)
     실패 시 폴백: 별도 스트리밍 호출 (시스템 프롬프트 "You are a helpful AI assistant tasked
     with summarizing conversations.", thinking 비활성, 출력 상한 20K)

[요약 후처리 — formatCompactSummary]
  <analysis> 블록(작성용 스크래치패드) 제거 → <summary> 태그를 "Summary:" 헤더로 치환

[재주입 — 새 대화 구성 (buildPostCompactMessages)]
  compact boundary 마커
  + 요약 user 메시지 (isCompactSummary): "This session is being continued from a previous
    conversation that ran out of context..." + 전체 트랜스크립트 파일 경로 안내
    + (오토컴팩트) "질문 금지, 요약 언급 금지, 하던 일 그대로 재개" 지시
  + 컨텍스트 복원 attachment들:
    · 최근 읽은 파일 최대 5개 재주입 (보존 tail에 이미 있는 Read 결과는 스킵 — 최대 25K토큰 절약)
    · plan 파일 / plan mode 지시 / 호출했던 스킬 내용 / deferred 도구·에이전트·MCP 목록 델타
  + SessionStart(compact) 훅 결과 (CLAUDE.md 등 재로드)
  + (SM-compact) 보존된 최근 메시지 원문
```

## 산출물 구조

**legacy 컴팩트 요약** — `<analysis>`(사고 정리, 주입 전 제거) + `<summary>` 9개 섹션:
1. Primary Request and Intent / 2. Key Technical Concepts / 3. Files and Code Sections(코드 스니펫 포함) / 4. Errors and fixes(사용자 피드백 강조) / 5. Problem Solving / 6. **All user messages**(도구 결과 제외 전부 나열) / 7. Pending Tasks / 8. Current Work / 9. Optional Next Step(**최근 대화 직접 인용(verbatim) 요구** — 태스크 해석 드리프트 방지)

`up_to` 변형은 8-9번이 "Work Completed / Context for Continuing Work"로 바뀐다.

**세션메모리 파일** — 10개 섹션 마크다운 템플릿(각 `# 헤더` + `_이탤릭 설명_` 보존 강제):
Session Title / Current State / Task specification / Files and Functions / Workflow / Errors & Corrections / Codebase and System Documentation / Learnings / Key results(요청 결과물 원문 반복) / Worklog. 섹션당 ~2000토큰, 파일 전체 12K 토큰 예산 — 초과 시 프롬프트에 압축 지시가 동적으로 첨부된다. 템플릿·프롬프트 모두 `~/.claude/session-memory/config/`에서 사용자 오버라이드 가능.

## 원문 프롬프트 발견 위치

| 프롬프트 | 위치 |
|---|---|
| NO_TOOLS_PREAMBLE (도구 호출 금지 서두) | `src/services/compact/prompt.ts:19-26` |
| BASE_COMPACT_PROMPT (메인 요약 프롬프트, "Your task is to create a detailed summary of the conversation so far...") | `src/services/compact/prompt.ts:61-143` (분석 지시 인라인: 31-44) |
| PARTIAL_COMPACT_PROMPT (`from` 방향) | `src/services/compact/prompt.ts:145-204` |
| PARTIAL_COMPACT_UP_TO_PROMPT (`up_to` 방향) | `src/services/compact/prompt.ts:208-267` |
| NO_TOOLS_TRAILER | `src/services/compact/prompt.ts:269-272` |
| 조립 함수 getCompactPrompt / getPartialCompactPrompt | `src/services/compact/prompt.ts:274-303` |
| 재주입 래퍼 getCompactUserSummaryMessage ("This session is being continued...") | `src/services/compact/prompt.ts:337-374` |
| 폴백 경로 시스템 프롬프트 | `src/services/compact/compact.ts:1302-1304` |
| 세션메모리 갱신 프롬프트 getDefaultUpdatePrompt | `src/services/SessionMemory/prompts.ts:43-81` |
| 세션메모리 템플릿 DEFAULT_SESSION_MEMORY_TEMPLATE | `src/services/SessionMemory/prompts.ts:11-41` |
| 세션메모리 예산 초과 경고문(동적 첨부) | `src/services/SessionMemory/prompts.ts:161-196` |

## 특이점 (다른 하네스와 구별되는 설계 포인트)

- **컴팩션 LLM 호출을 0회로 만드는 사전 플러시**: 세션메모리가 대화 중 미리 요약을 축적해 두면, 컴팩션 시점엔 그 파일을 읽어 재조립만 한다. "요약을 임계치 순간에 한 번에 만들지 말고 미리 나눠서 만들어 둔다"는 설계.
- **프롬프트 캐시 공유 포크**: 요약 호출이 메인 대화와 동일한 캐시 키 파라미터(시스템 프롬프트·도구·thinking 설정)로 포크되어 98% 캐시 히트. maxOutputTokens조차 캐시 키가 깨질까 봐 설정하지 않는다 (`compact.ts:1181-1186`).
- **도구 호출 3중 봉쇄**: 캐시 공유 포크가 부모의 전체 도구 셋을 물려받는 탓에 모델이 도구를 부르려는 문제(Sonnet 4.6에서 2.79%)를 프리앰블(최상단) + 트레일러(최하단) + canUseTool 거부의 3중으로 막는다 (`prompt.ts:14-18`).
- **`<analysis>` 스크래치패드**: 요약 품질을 위해 사고 과정을 쓰게 하되, 주입 전에 정규식으로 제거 — "작성엔 도움되지만 정보 가치는 없다" (`prompt.ts:314-319`).
- **세션메모리는 요약 생성이 아니라 파일 편집 태스크**: 추출 에이전트에게 "요약해줘"가 아니라 "Edit 도구로 이 노트 파일을 병렬 편집하고 멈춰라"를 시킨다. 템플릿 구조(헤더+이탤릭 설명) 훼손 금지를 프롬프트에서 3번 반복 강조.
- **요약과 별개로 전체 트랜스크립트 경로를 남김**: 압축으로 잃은 디테일은 모델이 Read로 원본 트랜스크립트를 열어 스스로 복구 가능 — 요약을 손실 압축이 아닌 "인덱스 + 원본 포인터"로 취급.
- **재개 지시의 톤 제어**: 오토컴팩트 후 "요약을 언급하지 말고, 'I'll continue' 같은 서두도 없이, 끊긴 적 없던 것처럼 마지막 작업을 이어가라"고 명시 (`prompt.ts:358-359`).
- **컴팩션이 다른 서브시스템의 리셋 신호**: 메모리 회상(relevant_memories)의 중복 방지·60KB 스로틀이 별도 장부 없이 "현재 대화 스캔"이라서, 컴팩션으로 대화가 갈리면 자동 리셋된다 (`utils/attachments.ts:2246-2248` 주석).
- **숫자 안전장치**: 요약 출력 예약 20K(p99.99 실측 17,387토큰 기반), 오토컴팩트 버퍼 13K, 수동 컴팩트 블로킹 버퍼 3K, 복원 파일 5개, SM 보존 10K~40K토큰.
