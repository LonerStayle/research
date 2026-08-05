<!--
시뮬레이션: openclaw 컴팩션 파이프라인 (techniques/openclaw-prompt.md) × data/conv-01.txt
적용 단계: 단계 1(사전 메모리 플러시) → 단계 2(컴팩션 요약).
단계 3(이전 요약 재증류)·4(부분 요약 병합)·5(split-turn)·6(품질 가드 재시도)·7(post-compaction refresh)은 발동 조건 미충족으로 미적용 (하단 참조).
치환부(YYYY-MM-DD, {previousSummary}, {reasons}, Current time)는 지시대로 무시.
-->

## 단계 1: 사전 메모리 플러시

대상 파일: `memory/YYYY-MM-DD.md` (append, 기존 항목 덮어쓰기 금지 / MEMORY.md·DREAMS.md·SOUL.md·TOOLS.md·AGENTS.md 는 read-only)

기록(append) 내용:

### 클로드코드 메모리 시스템 리서치 세션

- 작업 프로젝트: `/Users/seobi/jinsup_space/CC` — 클로드코드 원본 TypeScript 소스 미러(`src/`, 1,902파일 / 512,670줄) + 분석 문서(`md_group/` 약 135개, 전량 교정 완료) + 시각화(`html_group_v2/` 138개)의 3축 리서치 레포.
- 이번 세션 주제: 메모리 3축 소스 검증 딥다이브 — 자동 메모리(`src/memdir/`), 세션 메모리(`src/services/SessionMemory/`), 컴팩션(`src/services/compact/`).
- 세션 산출물:
  - `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html` (1차 작성 후 대화 반영 전면 재작성, 9섹션)
  - `/Users/seobi/jinsup_space/CC/md_group/클로드코드-메모리-시스템.md` (10장 정본, §2.5 "지침 8섹션과 측정된 효과" 추가 완료)
  - `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html` (1차 완성, 마지막 재작성 Write 도중 대화 절단)
- 문서 갭 발견: 메모리 전담 분석 문서는 `md_group/system_info/prompts/09-loadMemoryPrompt-analysis.md` 1개뿐(자동 메모리만) — SessionMemory / sessionMemoryCompact / findRelevantMemories 는 분석 문서 없음.
- 버전 차이 발견: 라이브 클로드코드 시스템 프롬프트에는 `[[name]]` 위키링크(red link) 지침이 있으나 미러 `src/memdir/`에는 없음 — 미러 스냅샷 이후 위키화 진행된 것. 프로젝트에 기록할 가치 있음.
- 이 머신 실측: `~/.claude/projects/` 전체에 `session-memory/` 디렉토리 0개 → `tengu_session_memory` 게이트 OFF 상태.
- 사용자 성향: 클로드코드 내부 동작을 리서치 중. 짧은 확인형 질문을 연달아 던지고, 자기 요약을 채점받는 방식으로 이해를 굳힘. 비유+표 방식 설명에 잘 반응. `/visual-explainer`로 대화 내용을 시각화해 남기는 습관.
- 미해결 질문(대화 절단 시점): "관련 메모리가 frontmatter 기반으로 system-reminder 채널로 주입되는가" — 근거 수집은 완료(`attachments.ts` relevant_memories 첨부 → `messages.ts:3708` wrapMessagesInSystemReminder), 최종 답변과 HTML 반영이 미완.

턴 응답: NO_REPLY

---

## 단계 2: 컴팩션 요약

이 세션은 `/Users/seobi/jinsup_space/CC`(클로드코드 소스 미러 + 분석 문서 리서치 레포)에서 진행됐다. 사용자의 "프로젝트 전체 파악" 지시로 Explore 서브에이전트 2개를 병렬 실행해 전체 구조를 파악한 뒤, 클로드코드의 메모리 3축(자동 메모리 / 세션 메모리 / 컴팩션)을 소스 grep/Read로 검증하며 사용자의 연속 질문에 답했고, 시각화 HTML 2개와 md 정본 1개를 산출했다. 대화는 마지막 질문(관련 메모리의 system-reminder 주입 여부) 조사 후 `자동메모리-딥다이브.html` 재작성 Write 도중 절단됐다.

## Decisions

- 프로젝트 전체 파악은 Explore 서브에이전트 2개 병렬(md_group 문서 카탈로그 + src 소스 구조)로 수행.
- `src/`는 디컴파일이 아닌 원본 TypeScript 소스 미러로 판정 (`bun:bundle` feature flag, Biome 주석, 프로덕션급 코멘트 근거).
- 리서치 초점을 메모리 3축으로 확정 — 근거는 문서 갭: 전담 분석 문서가 `09-loadMemoryPrompt-analysis.md` 1개뿐이고 SessionMemory·sessionMemoryCompact·findRelevantMemories 는 미분석.
- 산출물 컨벤션: 시각화 HTML은 프로젝트 루트, LLM 판독용 정본 md는 `md_group/`에 페어로 작성.
- 대화에서 새로 검증된 내용 반영 시 HTML은 부분 수정 대신 전면 재작성.
- `md_group/클로드코드-메모리-시스템.md`에 §2.5(자동 메모리 지침 8섹션 + eval 계측) 신설, §10 출처 표와 변경이력 갱신 — 사용자 승인("응") 후 실행 완료.
- 사용자 멘탈모델 교정 2건 확정: ① 자동 메모리는 "4개 섹션"이 아니라 4개 타입(user/feedback/project/reference)이며, 10섹션 템플릿은 세션 메모리 쪽. ② 컴팩션은 `/compact` 수동만이 아니라 자동(임계값 도달)이 주력.
- 용어 정리: "4중 게이트"는 공식 용어가 아니라 설명용 명명(if문 4개 순차 통과 구조).
- 결론 프레임: 자동 메모리(정식)와 세션 메모리(실험)는 경쟁이 아니라 다른 문제(세션 간 기억 vs 컴팩션 생존)를 푸는 장치. 세션 메모리는 "컴팩션 순간 LLM 즉석 요약"을 "미리 분산 저축한 노트 읽기"로 바꾸려는 교체 후보.
- 자동 메모리의 좁은 스코프는 약점이 아니라 설계 요체: 재파생 가능한 정보(grep/git/CLAUDE.md가 정본)는 배제하고, 대화에만 존재하는 재파생 불가 정보(WHO/HOW/WHY/WHERE = user/feedback/project/reference)만 저장. WHAT은 도구가 담당.
- MEMORY.md 구조는 "LLM 위키"로 규정 (인덱스 = 목차, 주제 파일 = 문서, frontmatter description = 검색 스니펫, 의미 기반 조직, update-in-place).

## Open TODOs

- [진행 중, 절단됨] 마지막 질문 답변 완성: frontmatter 기반 관련 메모리의 system-reminder 주입 여부 — 근거 수집 완료(`attachments.ts:2234-2242`에서 relevant_memories 첨부 생성·`.slice(0, 5)`·readMemoriesForSurfacing, `messages.ts:3708` case 'relevant_memories' → wrapMessagesInSystemReminder, 이벤트 `tengu_memdir_prefetch_collected`), 정리 답변 미출력.
- [진행 중, 절단됨] `자동메모리-딥다이브.html` 전면 재작성 Write 미완료 (위 주입 경로 내용 반영 중이던 것으로 보임).
- [제안, 미확답] 자동 메모리 딥다이브 내용(2×2 저장 축, WHO/HOW/WHY/WHERE 매핑, 4타입 충분성 논증)을 `md_group/클로드코드-메모리-시스템.md` §2에 반영.
- [제안, 미확답] extractMemories 백그라운드 경로(자동 메모리 갱신 경로 2) 내용을 md 문서 §2에 추가.
- [제안, 미확답] 지침 8섹션 내용을 `클로드코드-메모리-시스템.html`에도 반영.
- [제안, 미확답] `클로드코드-메모리-시스템.html`을 `html_group_v2/` 컨벤션 위치로 이동 또는 md 페어 생성.
- [기록 후보] 라이브 vs 미러 버전 차이(`[[name]]` red link 지침이 라이브에만 존재) 프로젝트 문서화.

## Constraints/Rules

- 모든 주장은 로컬 소스 미러(`src/`)에서 grep/Read로 직접 검증하고 `파일:line` 출처를 남긴다 (프로젝트 원칙 — 추측 배제).
- `md_group/` = LLM 판독용 정본 md, `html_group_v2/` = md와 1:1 시각화 사본, 프로젝트 루트 = 개별 주제 시각화 HTML.
- 자동 메모리 실물 규칙(이 프로젝트의 MEMORY.md): "레포 2-머신 공유 · 경로는 ~ 중립 표기" — 절대경로 하드코딩 시 머신 간 pull 충돌 재발.
- 이 머신은 `tengu_session_memory` 게이트 OFF — `session-memory/` 디렉토리 실물 0개, 세션 메모리는 한 번도 실행된 적 없음.
- 미러 소스 스냅샷과 라이브 클로드코드는 버전이 다를 수 있음(위키링크 지침 차이 확인됨) — 미러만으로 라이브 동작 단정 금지.
- 탐색은 서브에이전트, 실행은 메인 직접 (사용자 전역 지침).

## Pending user asks

- "위키처럼 되어있다는건.. 프론트메타를 읽어서 상황에맞게 유저프롬프트에 시스템리마인더에 들어갈거 같은데 맞아??" — 세션 마지막 질문, 최종 답변 미완. 조사 결과는 가설을 지지: `findRelevantMemories.ts` 호출자 중 `attachments.ts`가 relevant_memories 첨부를 만들고(`:2234-2242`, 상위 5개 선택) `messages.ts:3708-3712`에서 wrapMessagesInSystemReminder로 감싸 주입. 이 정리 답변 출력과 HTML 반영이 남음.
- `/visual-explainer` "위 내용들 세세히 적어! 빠짐없이!" — 1차 산출물(`자동메모리-딥다이브.html`)은 완성·전달됐으나, 마지막 재작성이 절단되어 미완.

## Exact identifiers

**소스 파일:라인 (핵심 근거)**
- `src/memdir/memdir.ts:34-38, :57, :111-115, :214, :218-234, :227, :233, :236-265, :241, :243, :254-257, :263, :375-407, :419-507`
- `src/memdir/memoryTypes.ts:4-7, :113-178, :183-195, :192-194, :208-212, :216-222, :228-244, :240-256`
- `src/memdir/paths.ts:30` / `src/memdir/findRelevantMemories.ts` / `src/memdir/memoryScan.ts` / `src/memdir/memoryAge.ts` / `src/memdir/teamMemPaths.ts` / `src/memdir/teamMemPrompts.ts:38, :55`
- `src/services/SessionMemory/sessionMemory.ts:1-5, :80-82, :134-181, :165-167, :272-289, :296, :315, :318-325, :321, :344, :387`
- `src/services/SessionMemory/sessionMemoryUtils.ts:20-22, :33, :184-189`
- `src/services/SessionMemory/prompts.ts:8, :9, :11-41, :44-46, :69, :86-120`
- `src/services/compact/compact.ts:598-624, :621, :637-642, :713-717, :798`
- `src/services/compact/autoCompact.ts:30, :62, :63, :70, :72`
- `src/services/compact/sessionMemoryCompact.ts:1-3, :437-482, :461-474, :479, :527`
- `src/services/compact/prompt.ts:337-342, :349-351`
- `src/services/extractMemories/extractMemories.ts:5-7, :345-360, :374-386, :415-427, :531-552, :554-564, :579-586, :611-615`
- `src/utils/permissions/filesystem.ts:259-270` / `src/utils/sessionStoragePortable.ts:311-331` / `src/utils/tokens.ts:226`
- `src/utils/messages.ts:3708-3712, :4537-4550, :4539, :4569, :4608`
- `src/utils/attachments.ts:2234-2242, :2412`
- `src/query.ts:92, :990-1000, :992` / `src/constants/prompts.ts:495` / `src/utils/forkedAgent.ts:127-141`
- isCompactSummary 소비처: `src/components/Message.tsx:159`, `src/components/MessageSelector.tsx:780`, `src/utils/sessionStorage.ts:1752`, `src/services/compact/compact.ts:798`, `src/hooks/useAwaySummary.ts:19`
- 최대 파일: `src/main.tsx` (4,680줄 / 794KB), `src/bridge/bridgeMain.ts` (2,999줄), `src/bridge/replBridge.ts` (2,406줄)

**산출물·문서 경로**
- `/Users/seobi/jinsup_space/CC/클로드코드-메모리-시스템.html`
- `/Users/seobi/jinsup_space/CC/md_group/클로드코드-메모리-시스템.md`
- `/Users/seobi/jinsup_space/CC/자동메모리-딥다이브.html`
- `/Users/seobi/jinsup_space/CC/md_group/system_info/prompts/09-loadMemoryPrompt-analysis.md`
- `/Users/seobi/jinsup_space/CC/md_group/cc-context-preprocessing-timing.md`
- `/Users/seobi/jinsup_space/CC/md_group-교정-변경내역.md`

**디스크 경로 (메모리 저장소)**
- `~/.claude/projects/-Users-seobi-jinsup-space-CC/`
- `~/.claude/projects/<프로젝트-슬러그>/memory/MEMORY.md`
- `{projectDir}/{sessionId}/session-memory/summary.md`
- `~/.claude/projects/-Users-seobi-jinsup-space-CC/725702dd-7cc0-4ecd-ba6a-c64b33f9d5e9/session-memory/summary.md`
- `~/.claude/session-memory/config/template.md`, `~/.claude/session-memory/config/prompt.md`
- `/private/tmp/claude-501/-Users-seobi-jinsup-space-CC/725702dd-7cc0-4ecd-ba6a-c64b33f9d5e9/tasks/a49f8b31bd7266cd8.output`
- `/private/tmp/claude-501/-Users-seobi-jinsup-space-CC/725702dd-7cc0-4ecd-ba6a-c64b33f9d5e9/tasks/a577a1911a4c18655.output`

**세션·에이전트·툴 ID**
- 세션 UUID: `725702dd-7cc0-4ecd-ba6a-c64b33f9d5e9`, `3d3ea6d7-5686-4c61-a57d-e80e969e4323`, `3e27f25a-a016-45ab-b9b7-c815b9da51d8`, `4a3cff0b-2a37-446a-b3eb-248a95130b05`, `c36aeba7-7619-425d-b98f-6585ccf6794d`
- Explore 에이전트: `a577a1911a4c18655` (md_group 카탈로그), `a49f8b31bd7266cd8` (src 구조)
- tool-use-id: `toolu_01ApwcgNtdE4mUBTp6cQX1cu`, `toolu_019SzqLAWh666v66AQh97ivB`

**feature flag / 이벤트**
- `tengu_session_memory` (기본 OFF), `tengu_passport_quail` (기본 OFF), `tengu_bramble_lintel` (기본 1 = 매 턴), `tengu_coral_fern` (기본 OFF), `KAIROS`, `TEAMMEM`
- 텔레메트리 이벤트: `tengu_session_memory_extraction`, `tengu_memdir_prefetch_collected`

**상수·수치**
- `ENTRYPOINT_NAME = 'MEMORY.md'`, `MAX_ENTRYPOINT_LINES = 200`, `MAX_ENTRYPOINT_BYTES = 25_000`
- `MAX_SECTION_LENGTH = 2000`, `MAX_TOTAL_SESSION_MEMORY_TOKENS = 12000`
- `minimumMessageTokensToInit` = 10,000 / `minimumTokensBetweenUpdate` = 5000 / `toolCallsBetweenUpdates` = 3
- `MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000`, `AUTOCOMPACT_BUFFER_TOKENS = 13_000`, `WARNING_THRESHOLD_BUFFER_TOKENS = 20_000`, `MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3`
- 자동 컴팩션 임계값 ≈ 167K (200K 모델: 컨텍스트 윈도우 − 20,000 − 13,000)
- extractMemories 포크: `maxTurns: 5`, 종료 드레인 60초
- src 규모: 1,902 파일 / 512,670줄 (메모리 관련 6,722줄); 문서 135개(89개 파일 296건 교정); `html_group_v2/` 138개
- 세션 메모리 10섹션: Session Title / Current State / Task specification / Files and Functions / Workflow / Errors & Corrections / Codebase and System Documentation / Learnings / Key results / Worklog
- eval 계측: H1 0/2→3/3 (불릿 배치 시 0/3; 헤더 "Before recommending from memory" 3/3 vs "Trusting what you recall" 0/3), H2(eval case 3) 0/2→3/3, H5 0/2→3/3, known gap(슬래시 커맨드) 0/3, branch-pollution evals #22856, PR #18525
- 날짜: 2026-07-10 (md 정본 최초 작성), 2026-03-10 (BQ 주석: "1,279 sessions had 50+ consecutive failures"), 2026-03-05 (상대→절대 날짜 변환 예시)
- 마커·플래그·타입: `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__`, `isCompactSummary`, `isVisibleInTranscriptOnly`, subtype `'compact_boundary'` / `'microcompact_boundary'`, attachment type `'relevant_memories'`, `querySource !== 'repl_main_thread'`

---

## 단계 3~7: 미적용

- 단계 3 (이전 요약 재증류 래퍼): 이전 컴팩션 요약 없음 → 미적용.
- 단계 4 (부분 요약 병합): 히스토리를 파트로 분할하지 않음 → 미적용.
- 단계 5 (split-turn 프리픽스 요약): 턴 중간 절단 컴팩션 아님 → 미적용.
- 단계 6 (품질 가드 재시도): 요약 감사 실패 이벤트 없음 → 미적용.
- 단계 7 (post-compaction context refresh): 요약 다음 턴에 주입되는 시스템 이벤트 템플릿으로, 요약 산출물이 아니며 치환부(AGENTS.md 섹션, Current time)가 전부라 시뮬레이션 대상 아님.
