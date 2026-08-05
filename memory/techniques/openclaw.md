# OpenClaw — 사전 메모리 플러시 + 안전장치(Safeguard) 구조화 컴팩션

## 개요

OpenClaw(구 clawdbot, pi-coding-agent 기반 상시 구동 에이전트 하네스)의 메모리 전략은 "요약(휘발성 압축)"과 "파일 기반 장기 기억(비휘발)"을 명확히 분리한 2중 구조다. 컨텍스트가 임계치에 근접하면 **(1) 사전 메모리 플러시** — 요약으로 사라지기 전에 에이전트에게 조용한(silent) 턴을 하나 주어 중요한 내용을 워크스페이스의 `memory/YYYY-MM-DD.md` 마크다운 파일에 직접 적게 하고, 그 다음 **(2) 컴팩션** — 오래된 대화를 고정 섹션 구조(Decisions / Open TODOs / Constraints/Rules / Pending user asks / Exact identifiers)의 요약으로 압축한다. 압축 직후에는 **(3) 컨텍스트 리프레시** — "요약은 힌트일 뿐"이라며 AGENTS.md의 핵심 규칙 섹션을 재주입한다. 장기 기억은 `MEMORY.md`(장기) + 데일리 노트(단기)가 세션 시작 시 부트스트랩 파일로 항상 로드되고, `memory_search`/`memory_get` 도구로 온디맨드 회상된다. "모델은 디스크에 적힌 것만 기억한다"가 설계 철학.

## 트리거

- **사전 메모리 플러시 (자동)**: `totalTokens >= contextWindow − reserveTokensFloor − softThresholdTokens(기본 4000)` 이면 발동. 즉 오토 컴팩션 임계치보다 4000토큰 **먼저** 발동해 컴팩션 전에 디스크에 기록할 기회를 확보한다. (`src/auto-reply/reply/memory-flush.ts:69-110`)
  - 트랜스크립트 파일 크기 기반 강제 플러시도 있음: `forceFlushTranscriptBytes` 기본 2MiB (`extensions/memory-core/src/flush-plan.ts:11`)
  - 같은 컴팩션 사이클에서 중복 실행 방지: `memoryFlushCompactionCount == compactionCount` 체크 (`memory-flush.ts:117-123`)
  - 하트비트/CLI 세션은 제외. 기본 활성(enabled: true), `memoryFlush.model`로 로컬 모델 위임 가능.
- **컴팩션 (자동)**: 세션이 컨텍스트 한계에 근접하거나, 프로바이더가 context-overflow 오류(`request_too_large`, `context length exceeded` 등)를 반환하면 컴팩션 후 재시도. (docs/concepts/compaction.md)
- **컴팩션 (수동)**: `/compact [지시문]` — 지시문은 요약 커스텀 지시로 주입됨.
- **바이트 가드**: `maxActiveTranscriptBytes` 설정 시 활성 JSONL이 그 크기에 도달하면 런 전에 컴팩션 트리거.

## 파이프라인

1. **플러시 턴** (`src/auto-reply/reply/agent-runner-memory.ts:860-970`): `trigger: "memory"`, `silentExpected: true`인 에이전틱 턴을 실행. 프롬프트는 "Pre-compaction memory flush. Store durable memories only in memory/YYYY-MM-DD.md ..." (아래 원문). 에이전트는 파일 쓰기 도구로 `memory/YYYY-MM-DD.md`에 append하고 `NO_REPLY`로 답한다. `MEMORY.md` 등 부트스트랩 파일은 이 턴 동안 read-only.
2. **컴팩션 요약 생성** (safeguard 모드, `src/agents/pi-hooks/compaction-safeguard.ts`의 `session_before_compact` 훅):
   - 런타임 컨텍스트 메시지 제거, tool_use/tool_result 페어링 수리
   - **최근 N 유저턴(기본 3, 최대 12) verbatim 보존** — 요약 대상에서 분리 (`splitPreservedRecentTurns`)
   - 히스토리가 컨텍스트의 `maxHistoryShare`(기본 0.5)를 넘으면 오래된 청크를 드랍하되, 드랍분도 별도 요약해 previousSummary로 합류
   - 청크 분할: adaptive chunk ratio(0.4 기본, 최소 0.15), 토큰 추정 오차 대비 SAFETY_MARGIN 1.2, 요약 프롬프트 오버헤드 4096토큰 예약 (`src/agents/compaction.ts`)
   - 청크를 순차 요약하며 직전 요약을 previousSummary로 넘기는 **rolling 방식**(`summarizeChunks`), 큰 히스토리는 부분 요약 후 병합(`summarizeInStages` + MERGE_SUMMARIES_INSTRUCTIONS)
   - **이전 컴팩션 요약 재증류**: 이전 요약을 `<previous-compaction-summary>` 블록으로 앞에 붙이고 "verbatim 보존이 아니라 stale/중복/대체된 내용을 쳐내라"고 지시
   - **품질 가드**(기본 활성, 재시도 1회): 필수 섹션 존재 여부, 원문 식별자(UUID/URL/경로/포트 등 자동 추출 최대 12개) 보존 여부, 최근 유저 요청 키워드 반영 여부를 감사(`auditSummaryQuality`) — 실패 시 실패 사유를 피드백으로 붙여 재생성
   - 요약 body + suffix(split-turn 컨텍스트, 보존 최근턴, `## Tool Failures`, `<read-files>/<modified-files>`, `<workspace-critical-rules>`) 조립, 총 16,000자 캡(suffix 우선 보존)
   - 실제 요약 LLM 호출의 base 프롬프트는 upstream `@mariozechner/pi-coding-agent`의 `generateSummary`(레포 외부 npm 의존성) — OpenClaw는 여기에 위 구조 지시를 customInstructions로 주입
3. **저장**: 요약은 세션 JSONL 트랜스크립트에 컴팩션 엔트리로 기록(전체 원본 히스토리는 디스크에 유지). 컴팩션 체크포인트 스냅샷 보관, `truncateAfterCompaction` 시 요약+보존턴+미요약 꼬리로 successor 트랜스크립트 생성.
4. **회상(재주입)**:
   - 다음 턴부터 모델은 [요약 + 보존된 최근 턴]을 히스토리 대신 봄
   - 컴팩션 직후 `[Post-compaction context refresh]` 시스템 이벤트로 AGENTS.md의 "Session Startup"/"Red Lines" 섹션 재주입(기본 1800자 캡) — "요약은 힌트일 뿐, 스타트업 시퀀스를 다시 실행하라" (`src/auto-reply/reply/post-compaction-context.ts:149-163`)
   - `MEMORY.md` + 오늘/어제 데일리 노트는 세션 부트스트랩으로 항상 로드, `memory_search`(하이브리드 벡터+키워드)/`memory_get`으로 온디맨드 회상
   - (옵션) Dreaming: 새벽 크론으로 단기 신호를 점수화해 `MEMORY.md`로 승격

## 산출물 구조

요약 본문은 다음 **정확한 헤딩**을 강제(품질 가드가 순서까지 검사):

```
## Decisions
## Open TODOs
## Constraints/Rules
## Pending user asks
## Exact identifiers
```

뒤에 하네스가 기계적으로 붙이는 suffix 섹션들:

- `**Turn Context (split turn):**` (턴이 쪼개진 경우)
- `## Recent turns preserved verbatim` (최근 턴 원문, 턴당 600자 캡)
- `## Tool Failures` (실패한 도구 호출 최대 8건, 각 240자)
- `<read-files>` / `<modified-files>` (파일 작업 목록, 900자/섹션 2000자 캡)
- `<workspace-critical-rules>` (AGENTS.md의 Session Startup/Red Lines, 2000자 캡)

요약할 것이 없을 때의 구조화 폴백도 같은 5개 섹션 골격으로 생성(`buildStructuredFallbackSummary`).

## 원문 프롬프트 발견 위치

| 프롬프트 | 위치 |
|---|---|
| 메모리 플러시 user 프롬프트 `DEFAULT_MEMORY_FLUSH_PROMPT` | `extensions/memory-core/src/flush-plan.ts:25-32` (조각: 13-23) |
| 메모리 플러시 system 프롬프트 `DEFAULT_MEMORY_FLUSH_SYSTEM_PROMPT` | `extensions/memory-core/src/flush-plan.ts:34-41` |
| `NO_REPLY` 토큰 (`SILENT_REPLY_TOKEN`) | `src/auto-reply/tokens.ts:4` |
| 요약 섹션 구조 지시 `buildCompactionStructureInstructions` + `REQUIRED_SUMMARY_SECTIONS` | `src/agents/pi-hooks/compaction-safeguard-quality.ts:10-20, 52-74` |
| 기본 컴팩션 지시 `DEFAULT_COMPACTION_INSTRUCTIONS` (언어/사실성 보존) | `src/agents/pi-hooks/compaction-instructions.ts:13-17` |
| 식별자 보존 지시 `IDENTIFIER_PRESERVATION_INSTRUCTIONS` | `src/agents/compaction.ts:39-41` |
| 부분 요약 병합 지시 `MERGE_SUMMARIES_INSTRUCTIONS` | `src/agents/compaction.ts:25-38` |
| 이전 요약 재증류 프리픽스 `PREVIOUS_SUMMARY_REDISTILL_PREFIX` | `src/agents/pi-hooks/compaction-safeguard.ts:71-73, 78-89` |
| split-turn 프리픽스 지시 `TURN_PREFIX_INSTRUCTIONS` | `src/agents/pi-hooks/compaction-safeguard.ts:57-59` |
| 품질 가드 재시도 피드백 | `src/agents/pi-hooks/compaction-safeguard.ts:1252-1262` |
| 컴팩션 직후 리프레시 프롬프트 | `src/auto-reply/reply/post-compaction-context.ts:149-163` |
| (부가) 쿼터 핸드오프 지시 `HANDOFF_INSTRUCTIONS` | `src/agents/compaction.ts:43-57` |
| untrusted 블록 래퍼 형식 | `src/agents/sanitize-for-prompt.ts:26-50` |

주의: 요약 LLM 호출의 **base 시스템 프롬프트**는 npm 의존성 `@mariozechner/pi-coding-agent@0.73.0`의 `generateSummary` 내부에 있으며 이 레포(및 로컬 node_modules 미설치 상태)에는 없다. 위 표의 프롬프트들은 모두 그 위에 customInstructions로 주입되는 OpenClaw 측 원문이며 소스에서 verbatim으로 확보했다.

## 특이점

1. **요약 전 "메모리 플러시" 에이전틱 턴**: 요약(손실 압축)에 맡기기 전에 에이전트 스스로 파일에 쓰게 하는 선행 단계. 컴팩션 임계치보다 4000토큰 먼저 발동하는 소프트 임계치, 사이클당 1회 가드, 전용 소형 모델 위임 옵션까지 갖춘 독립 서브시스템 — 다른 하네스와 가장 구별되는 지점.
2. **요약 ≠ 기억**: 요약은 세션 연속성용 휘발 레이어, 진짜 기억은 사람이 읽을 수 있는 마크다운 파일(MEMORY.md/데일리 노트). 요약이 망가져도 기억은 남는다.
3. **자동 품질 가드**: 생성된 요약을 코드가 감사(필수 섹션·식별자 보존·최근 요청 반영)하고 실패 사유를 피드백으로 붙여 재생성 — 요약을 "믿고 끝"이 아니라 검증 대상으로 취급.
4. **식별자 보존 정책**(strict/off/custom): UUID·해시·URL·경로·포트를 원문 그대로 보존하라는 명시 지시 + 사후 검증. `## Exact identifiers` 전용 섹션까지 강제.
5. **이전 요약 재증류**: 요약의 요약이 눈덩이처럼 커지는 것을 막기 위해 이전 요약을 "재증류하되 stale한 것은 버려라"고 명시.
6. **프롬프트 인젝션 방어가 요약 파이프라인에 내장**: /compact 사용자 지시·품질 피드백·커스텀 정책 텍스트를 전부 `<untrusted-text>` 블록("data, not instructions")으로 감싸고 제어문자 strip + `<`/`>` 이스케이프.
7. **요약 직후 불신 원칙**: "요약은 힌트일 뿐(hint, NOT a substitute)" — AGENTS.md 핵심 규칙을 다시 주입하고 스타트업 시퀀스 재실행을 지시.
8. **최근 턴 verbatim 보존 + suffix 우선 truncation**: 잘릴 때 요약 body를 자르고 진단 suffix(규칙·파일 목록)를 지킨다.
9. **플러그블**: 컴팩션 프로바이더(플러그인) / 요약 전용 모델 / 메모리 백엔드(SQLite·QMD·Honcho·LanceDB) 모두 교체 가능.
10. **다국어 인지**: "요약 본문은 대화의 주 언어로 쓰되 코드·경로·식별자는 번역 금지" — 한국어 대화 시뮬레이션에 유리한 명시 규칙.
