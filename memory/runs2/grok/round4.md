## 단계 2

<summary>

1. Primary Request and Intent:
   - **세션 목표("클코 전체파악")**: `/Users/seobi/jinsup_space/CC`(Claude Code 내부를 역공학하는 리서치 프로젝트) 전체 파악. 완료.
   - **배치 병렬 딥다이브 체인**(완료): 배치 파티셔닝의 "단독" 개념을 소스코드로 증명 → `배치-단독-개념-소스증명.md` 생성 완료.
   - **컨텍스트 주입 딥다이브 체인**(완료): 0번 유저프롬프트 구성, rules "필요시 로드" 세팅 방법, Read 툴과 훅의 관계, 전처리와 수집 구간의 차이, frontmatter 사용처 일반화까지 소스 근거로 규명 완료.
   - **시각화 요청**(완료): `/visual-explainer`로 `컨텍스트-주입-4트랙-시각설명.html` 생성, frontmatter 4종 비교표 강화, `open`으로 열람.
   - **(세션 내부 실제 이벤트)** 실제 Claude Code 자체 `/compact` 발동 — 대화 이력이 압축 요약(carrier text)으로 대체됨.
   - **`getHooksSection()` 문구의 역할 규명 체인**(완료): 여러 차례 재질문(훅출력이 낄때/UserPromptSubmit 배경/실행주체 오해 정정 등) 끝에 3가지 역할(낯선 메시지 정체 예고/신뢰 등급 부여/차단 시 행동 규칙)로 확정. 호출 사슬까지 추적 완료.
   - **MCP 지시 + 캐시 경계 질문**(완료): 조립 코드 + 실물 예시 제시, 구형(uncached) vs 델타 모드 2가지 배달 방식 비교, `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`로 global/per-session 캐시 분리 로직 규명.
   - **`/login` 실행**(세션 내부 이벤트) — userEmail이 `axtech@goldenplanet.co.kr` → `admin@jinju-ict.com`으로 변경.
   - **세션 인풋 전문 스냅샷 MD 요청**(완료): 모델 자기관찰 방식으로 `세션인풋-시스템프롬프트-도구-전문.md`(Part1~4) 작성.
   - **src-대조 마킹 요청**(완료): 🟢🟡🔴⚪ 4색 마커 + 범례 + 부록-2(도구 12종 대조표) 삽입. 사용자의 최종 재검증 요청("없는거 md에 잘적은거 맞지?")도 **이번 구간 첫머리에서 완료** — `grep -n "🔴"` + `sed`로 마커가 섹션 제목 바로 아래(3중: 본문/부록-2/범례)에 정확히 붙어 있음을 확인, 1509행의 🔴는 마커가 아니라 Part4 대화기록 속 과거 답변 원문 이모지라는 오탐 가능성까지 짚어 정상 보고.
   - **파일명 변경 + HTML 시각화**(완료): "2027-07-11로 이름바꾸고 /visual-explainer로 html도 만들어줘" → 어시스턴트가 오늘 날짜(2026-07-11)와 불일치하는 "2027"을 오타로 판단해 **`2026-07-11-시스템프롬프트및도구내용-최신본.md`**로 정정 제안하며 `mv`, 이어서 `/visual-explainer`로 **`2026-07-11-시스템프롬프트및도구내용-최신본.html`**(청사진 도면 컨셉) 생성, `open`.
   - **ToolSearch 로직 상세 요청**(완료): "도구의 toolsSerach에 대한 로직을 상세히 알려줘" → src 전수 조사(ToolSearchTool.ts/prompt.ts, utils/toolSearch.ts, services/api/claude.ts, utils/api.ts, utils/attachments.ts, utils/messages.ts)로 5단계 생애주기(분류→고지→검색→영수증→재조립) 전체 규명. 이어 "md로도 만들어주고 /visual-explainer로도 만들어주라" → `toolsearch-생애주기-소스분석.md` + `.html`(폐가식 서고 메타포) 생성, `open`.
   - **후속 심화 질문 체인 (ToolSearch, 전부 완료)**:
     - "툴서치 쓸때마다 system-reminder가 들어오나?" → 아니오, ToolSearch 호출과 무관, 델타(풀 변화분) 있을 때만 수집 지점에서 발행.
     - "첫번째 프롬프트에 들어가나?" → 네, 첫 턴엔 고지 이력=0이라 델타=전체 목록. messages 배치 순서(0번유령→유저프롬프트→deferred_tools_delta→skill_listing→...)까지 소스로 확인.
     - "나중에 mcp추가하면 최신 메시지에 들어가?" → 네, 다음 수집 지점(턴 머리 또는 진행 중 턴의 사이클 꼬리)에 자동 삽입, 유저 엔터 불필요할 수 있음(사이클 꼬리 케이스는 이 세션에서 실측).
     - "로스트인더미들로 까먹는거 아닌가" → 리스크 인정, 4중 안전망(입구표지판/키워드검색/bare-name fast path/실패시 재시도유도) + compact의 역설적 리프레시 효과 제시, 단 소스상 미확인 구간은 정직 표기.
     - "1번 무슨말인지 모르겠네.. tools에는 검색될 목록 안들어가잖니" → 사용자 지적이 정확함을 인정, tools 배열엔 ToolSearch 자신+설명문만 있고 목록은 대화 이력에만 있음으로 정정.
     - "그럼 여전히 로스트인더미들 문제는 있는거 아니야?" → 네, 구조적으로 남음. 설계는 문제를 "제거"가 아니라 "침묵 실패→회복 가능한 검색 실패"로 실패 모드를 바꾼 것. 진짜 급소는 "그런 도구가 있다는 발상 자체를 못 하는" unknown unknowns.
     - "좀쉽게 플로우 위주로" → 3가지 흐름(정상/까먹었지만 회복/진짜 구멍)으로 재설명.
     - "흐름2에서 한단어만 들어가?" → 아니오, 여러 단어 + 이름/설명문/힌트 3면 검색이라 그물은 넓음. 단 어휘매칭이라 동의어·한국어는 안 잡히고, 모델이 단어를 바꿔 재시도하는 것으로 보완.
     - "새 mcp세팅시 엔터쳐야 시스템리마인더 들어가? 자동이야? 키워드검색은 BM25야?" → 케이스A(대화 유휴 중, 엔터가 방아쇠)/케이스B(모델 턴 진행 중, 사이클 꼬리에서 자동) 구분, BM25 아님을 표로 확정(TF/IDF/길이정규화 없음, 필드가중치만 하드코딩).
     - "필드별가중치는 뭐였지" → 점수표 재정리(이름조각정확 12/10, 부분포함 6/5, hint 4, 이름폴백 3, 설명 2).
   - **최신 내용 md/html 반영 + 새 질문 (진행 중, 미완)**: "위에 추가된 내용 다 md와 html에 반영해줘 그리고 새로운질문 ReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?" — 어시스턴트가 새 질문부터 src 조사(task-notification 큐 메커니즘)를 시작했고, 이어 md에 "§08 추가 Q&A 보강" 섹션을 Edit으로 삽입, html에도 "07 추가 Q&A" 섹션 Edit 삽입을 진행하다가 **html Edit 내용이 완성되지 않은 채(마지막 Edit 문자열이 중간에 끊김) `open` 명령까지만 호출되고 그 결과 확인 전에 구간이 종료**됨. 새 질문("엔터 예외") 자체에 대한 최종 답변은 사용자에게 아직 전달되지 않음.
   - **불변 제약 (전체 세션 유지)**: 항상 한국어로 응답. 모든 주장은 반드시 grep/Read로 소스 검증 후 답할 것 — 프로젝트 CLAUDE.md 지침("주장은 반드시 소스 코드 기반으로 검증", "추측·과장 금지, 미확인 부분은 '소스에서 확인 못함'으로 표기"). 문서에는 `~` 중립/상대 경로 사용(단, 세션인풋 계열 MD는 일회성 스냅샷이라 예외이며 그 사실을 문서 머리에 명시). HTML에 유저 PC 절대경로 하드코딩 금지.

2. Key Technical Concepts:
   - **배치 파티셔닝**: `partitionToolCalls` reduce — safe 도구는 직전 배치도 safe일 때만 병합, unsafe는 항상 새 "단독" 배치. 병렬 3조건 = 모델의 multi-tool_use emit × 도구별 `isConcurrencySafe` 선언 × 하네스 파티션/동시실행(기본 concurrency 10). 재정렬 없음.
   - **0번 유령 메시지 vs skill_listing/deferred_tools_delta 등 정주민 메시지**: `prependUserContext`가 매 API 호출마다 index 0을 재생성(이력에 안 남음, userEmail 변경으로 실증). 나머지 델타류(스킬/에이전트/MCP지시/deferred도구)는 별개 어태치먼트 파이프라인으로 이력에 1회 삽입 후 잔류.
   - **conditional rules 지연 주입 파이프라인**: frontmatter `paths:` 유무로 무조건부/조건부 분기 → Read 도구가 트리거 Set에 경로만 등록(우편함 구조) → 같은 사이클 꼬리의 어태치먼트 수집기가 Set을 비우며 glob 매칭 → `nested_memory` 어태치먼트로 주입.
   - **수집(+) vs 전처리(−) 구간**: 어태치먼트 수집은 도구 실행 직후 **같은 사이클의 꼬리**(`query.ts:1569` 부근). 컨텍스트 전처리 5단(budget→snip→microcompact→collapse→autocompact)은 **다음 사이클의 머리**, 모델 호출 직전.
   - **frontmatter 2단 구조의 일반화(4종 공통)**: "값싼 색인은 항상 보이게, 비싼 본문은 방아쇠 당길 때만" — rules/skills/agents/slash commands 공통 패턴. **ToolSearch도 동일 패턴의 도구판**: 이름(값쌈)은 항상, 스키마(비쌈)는 영수증 생긴 뒤에만.
   - **훅(hooks)**: 실행 주체는 하네스(`child_process.spawn()` 직접 호출), 모델은 관여 안 함. 훅 이벤트 전수(types/hooks.ts 등), `getHooksSection()`은 상시 포함되는 3문장 안내(정체예고/신뢰승격/차단행동규칙), 호출 사슬은 메인루프(`queryContext.ts:64`)와 서브에이전트 스폰 경로 모두를 통과. `<user-prompt-submit-hook>` 태그는 src 전체에서 `prompts.ts:128` 1회 언급뿐 — 구버전 잔재로 결론(반증 여지 2가지 명시).
   - **MCP 서버 지시 조립 & 배달 2모드**: `## <서버이름>` 블록 나열. (a) 구형 uncached — 서버 접속/해제마다 캐시 파괴. (b) 델타 모드 — `mcp_instructions_delta` 어태치먼트로 변경분만 삽입, 캐시 보존. 현재 세션은 델타 모드 실측 확인.
   - **시스템 프롬프트 캐시 경계 마커**(`SYSTEM_PROMPT_DYNAMIC_BOUNDARY`): 마커 앞=global 캐시(세션 무관), 마커 뒤=per-session 캐시. `getSessionSpecificGuidanceSection`이 마커 뒤에 있는 이유는 그 내용이 세션 조건부라서(소스 주석: "must be post-boundary or it fragments the static prefix on session type").
   - **src-대조 4색 마커 체계**: 🟢일치 · 🟡문구다름 · 🔴신규(스냅샷에 없음) · ⚪비교불가. 도구 12종 중 4개(Workflow·Artifact·ReportFindings·ScheduleWakeup) 완전 신규 확정, 이번 구간 grep 재검증으로 3중 표기(섹션 제목 바로 아래/부록-2/범례) 위치까지 최종 확인 완료.

   **ToolSearch 지연 로딩 시스템 (이번 구간 신규 규명, 핵심)**
   - **왜 존재하나**: MCP 서버가 많으면 도구 스키마만 수만 토큰. 무거운 도구는 스키마 없이 **이름만** 고지하고, 모델이 필요할 때 검색으로 "장전"하는 구조.
   - **5단계 생애주기**: ① 분류(`isDeferredTool`) → ② 고지(`deferred_tools_delta` 어태치먼트) → ③ 검색(`ToolSearchTool.call()`) → ④ 영수증(`tool_reference` 블록) → ⑤ 재조립(다음 요청부터 스키마 포함).
   - **① 분류 우선순위**(`ToolSearchTool/prompt.ts:62-108`): `alwaysLoad:true`(MCP는 `_meta['anthropic/alwaysLoad']`) 최우선 defer 면제 → MCP 도구는 무조건 defer → ToolSearch 자신은 면제(자기 자신이 로딩 창구) → `FORK_SUBAGENT` 실험 켜지면 Agent 툴 면제(1턴부터 fork 가능해야) → Brief류 통신 채널 면제 → 나머지는 `shouldDefer:true`인 것만 defer.
   - **모드 게이트**(`utils/toolSearch.ts:172-473`): `ENABLE_TOOL_SEARCH` 환경변수로 `tst`(기본, MCP·shouldDefer 항상 defer) / `tst-auto`(deferred 토큰 총량이 컨텍스트 윈도 N% 초과할 때만, 토큰 카운팅 API 우선·실패시 chars÷4 폴백) / `standard`(전부 인라인, 구식) 3모드. `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` 킬스위치, 모델의 tool_reference 지원 여부(기본 미지원 패턴 `['haiku']`, GrowthBook 갱신) 추가 차단기.
   - **② 델타 고지**: `getDeferredToolsDelta`(toolSearch.ts:646-706) — 현재 deferred 풀 − 이미 고지한 이름 집합(과거 delta 어태치먼트 이력 재스캔으로 재구성) = 차집합만 발행, 차이 없으면 null. 렌더링 문구(`messages.ts:4178-4193`): "The following deferred tools are now available via ToolSearch: ..." / "...are no longer available (their MCP server disconnected). Do not search for them: ...". 델타 4형제(같은 attachments.ts `maybe(...)` 목록에 나란히 등록): `deferred_tools_delta`(:836) · `agent_listing_delta`(:851) · `mcp_instructions_delta`(:854) · `skill_listing`(:875).
   - **발행 발동 조건**: 수집 지점(턴 시작 + 진행 중 턴의 사이클 꼬리, `query.ts:1569`) 도래 시 델타가 있을 때만. 첫 턴은 고지 이력=0이라 델타=전체 목록(텔레메트리 주석: "prior=0 is EXPECTED — fresh conversation"). compact 직후도 동일 원리로 전체 재발행(옛 고지 메시지가 요약으로 날아가 prior=0). 발행 전 게이트 4개(`attachments.ts:1461-1471`): 델타모드 켜짐/tool search 활성/모델 tool_reference 지원/ToolSearch 도구 disallowed 아님.
   - **1턴 messages 배치 순서**: `[0]유령메시지 → [1]유저 첫 프롬프트 → [2]deferred_tools_delta → [3]skill_listing → [4]agent_listing_delta/mcp_instructions_delta`. 유저 프롬프트 텍스트에 섞이지 않고 직후에 별도 isMeta 메시지로 나란히 섬.
   - **세션 중간 MCP 추가/제거**: 서버 연결 즉시가 아니라 **다음 수집 지점**에 반영. (a) 대화 유휴 중이면 유저 엔터가 방아쇠, (b) 모델이 턴 진행 중이면 사이클 꼬리에서 **자동**(유저 입력 불필요) — 이 세션에서 (b) 실측(figma/supabase/vercel 고지가 작업 턴 중간에 끼어듦, Atlassian/Gmail 등 61개 해제 공지도 같은 방식).
   - **③ 검색**(`ToolSearchTool.ts:328-434`): A. `select:` 경로 — 정확 선택, 콤마 다중, 이미 로드된 도구도 select하면 성공 처리("harmless no-op"), 0개면 "아직 연결 중인 MCP 서버" 안내. B. 키워드 경로(`searchToolsWithKeywords`, :186-302) — fast path1(쿼리 전체가 도구명과 정확 일치, compact 후·서브에이전트에서 관찰된 bare-name 패턴 흡수) → fast path2(`mcp__` 프리픽스 매칭) → 스코어링 검색(도구명 CamelCase/언더스코어 분해, `+term` 필수텀 필터).
   - **점수표**(`ToolSearchTool.ts:266-291`): 이름 조각 정확 일치 MCP12/일반10 · 이름 조각 부분 포함 MCP6/일반5 · searchHint 4 · 이름 전체 폴백(0점일 때만) 3 · 설명문 word-boundary 매치 2. `score>0` 필터 → 내림차순 → `max_results`(기본5) 컷. **BM25 아님** — TF(빈도)·IDF(희귀도 가중)·문서길이 정규화가 전부 빠진 "필드 가중치를 손코딩한 불리언 매칭+합산"(어휘매칭이라 동의어·한국어 안 잡힘, 실패시 모델이 재시도하는 것으로 보완하는 설계).
   - **④⑤ 영수증과 재조립**: 검색 결과는 텍스트가 아니라 `tool_reference` 블록(`type:'tool_reference', tool_name`)으로 tool_result에 담김. 요청 조립부(`claude.ts:1150-1167`) 규칙 — 비deferred 항상 전송 / ToolSearch 자신 항상 전송 / deferred+미발견은 tools 배열에서 아예 제외 / deferred+발견됨은 `defer_loading:true` 플래그로 전송. "발견됨" 판정은 별도 상태가 아니라 **대화 이력 자체를 스캔**(`extractDiscoveredToolNames`, toolSearch.ts:545-592)해 재구성 — compact로 이력이 날아가도 `compact_boundary.preCompactDiscoveredTools`로 스냅숏 이월돼 발견 집합 보존. 스키마의 실제 확장은 API 서버가 함(tool_reference→full definition, 베타 헤더 필수: 1P/Foundry=advanced-tool-use, Vertex/Bedrock=tool-search-tool).
   - **lost-in-the-middle 4중 안전망**: ① ToolSearch 도구 자신의 설명문("Deferred tools appear by name in system-reminder messages...")이 매 요청 fresh하게 tools 배열에 실림(목록 자체는 없지만 "검색하는 법"이라는 표지판은 상시) ② 키워드 검색(이름 암기 불필요) ③ bare-name fast path(소스 주석: "seen from subagents/post-compaction" — 기억 열화를 실측하고 겨냥한 방어선) ④ 실패해도 명시적 재시도 유도. + **compact가 역설적 리프레시 장치**: 옛 고지가 요약으로 날아가 prior=0 → 전체 목록이 새 컨텍스트 앞쪽에 재발행. `getDeferredToolsDeltaAttachment`가 compact.ts에서도 동일 게이트로 호출되도록 export됨.
   - **남는 구멍(정직 표기)**: 안전망은 "이름을 어렴풋이 기억"하는 경우만 구제. "그런 도구가 있다는 발상 자체를 못 하는" unknown unknowns 상황(예: 유저가 "지라"란 단어를 안 쓰고 "이슈 정리해줘"만 말함)엔 검색 자체를 시도 안 해서 무력. 소스상 이를 메우는 별도 재주입/능동 힌트 장치는 확인 못 함. 완화 요인(유저가 보통 능력을 직접 언급/MCP 서버 지침의 의미적 라우팅 힌트/compact로 인한 주기적 리셋)은 있으나 해결책은 아님.
   - **(조사 중, 미완결) task-notification 큐 우선순위**: `messageQueueManager.ts` — `enqueue()`(유저 발화, 기본 priority `'next'`) vs `enqueuePendingNotification()`(시스템 알림, 기본 priority `'later'`). `PRIORITY_ORDER = {now:0, next:1, later:2}` — 유저 입력이 시스템 메시지에 굶주리지 않도록 설계. `hooks/useQueueProcessor.ts`가 React `useEffect`+`useSyncExternalStore`로 `isQueryActive===false && queue not empty`일 때 `processQueueIfReady`를 자동 호출 — 유휴 상태면 유저 엔터 없이도 큐가 자동 드레인될 가능성을 시사하나, **이 결론은 아직 사용자에게 답변으로 전달되지 않은 조사 중간 상태**임(아래 8/9 참조).

3. Files and Code Sections:
   - **배치/컨텍스트주입 4트랙 관련 소스**(`toolOrchestration.ts`, `Tool.ts:750-765`, `FileReadTool.ts:373`, `GrepTool.ts:183`, `query.ts:820-824`, `api.ts:449-474`, `context.ts:155-189`, `attachments.ts:875/2661-2751`, `messages.ts:3700-3738`) — 이전 라운드 상세 인용, 변경 없음.
   - **`/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md`**, **`/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html`** — 이전 라운드 생성, 변경 없음.
   - **`src/utils/claudemd.ts`, `attachments.ts`(nestedDirs/memoryFilesToAttachments/getNestedMemoryAttachments), `FileReadTool.ts:848,870,1038`, `QueryEngine.ts:370,518`, `query.ts:1540-1579`** — rules 지연주입 파이프라인, 변경 없음.
   - **`SkillTool.ts:1055-1119`, `AgentTool/loadAgentsDir.ts:312-324`, `processUserInput/processUserInput.ts:140-209`, `utils/hooks.ts:3826-3855`, `utils/messages.ts:4090-4139`, `src/constants/prompts.ts:127-129/160-441/444-576`, `src/utils/hooks.ts:7,938-981`, `src/types/hooks.ts`, `src/utils/attachments.ts:702,854,1584`, `src/utils/messages.ts:4208-4231`, `src/utils/api.ts:318-421`** — 훅/MCP지시/캐시경계 관련 전체 소스, 이전 라운드 상세 인용 완료, 변경 없음.
   - **`/Users/seobi/jinsup_space/CC/세션인풋-시스템프롬프트-도구-전문.md`** → **이번 구간에서 `mv`로 개명**: **`/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`**(파일 내용 자체는 변경 없음, src-대조 마킹 상태 유지).
   - **CREATED: `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.html`** — `/visual-explainer`로 생성, "청사진(blueprint) 제도 도면" 컨셉(네이비 도면 그리드+시안 선묘+도면 타이틀 블록, 신규 도구엔 회전 "SRC 無" 검수 스탬프), Do Hyeon+IBM Plex Sans KR+IBM Plex Mono. 5개 섹션(01 적재구조 좌우화물칸/02 시스템13섹션 판정색테두리/03 도구12종 카드그리드/04 상주화물 6레인/05 대시보드), 섹션마다 `› source` 근거, ⚪ 항목은 "비교 불가" 정직 표기, 기계 절대경로 미포함.
   - **CREATED: `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`** — Write 1회 + Edit 3회(FAQ 섹션 추가, §08 추가 Q&A 보강, 검증이력 갱신). 구성: §00 큰그림 5단계 → §01 분류사다리 → §02 모드게이트(tst/auto/standard) → §03 고지델타+FAQ → §04 검색알고리즘·점수표 → §05 영수증·재조립 4행규칙 → §06 이 세션 실측(61개 해제 공지) → §08 추가 Q&A(카드목록 타이밍/lost-in-the-middle/BM25아님) → 검증이력. 짝꿍: `.html`, `2026-07-11-시스템프롬프트및도구내용-최신본.md`(Part 2-10).
   - **CREATED: `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html`** — `/visual-explainer`로 생성, "폐가식 서고 + 대출 시스템" 메타포, 웜 다크 아카데미아(세피아+황동), Gowun Batang/Gothic A1/IBM Plex Mono. 구성: 01 생애주기 5노드 체인 → 02 분류 사다리 → 03 대표님 질문 전용 섹션(카드목록 vs 봉인스키마 좌우분리) → 04 select/키워드 2경로+점수막대 → 05 4행규칙+영수증스탬프 → 06 3모드+실측 → **07 추가 Q&A(구간 종료 시점에 Edit 진행 중, 완성 여부 미확인)**.
   - **`src/tools/ToolSearchTool/ToolSearchTool.ts`(전문 Read)** — `inputSchema`(query/max_results), `outputSchema`(matches/query/total_deferred_tools/pending_mcp_servers), `getDeferredToolsCacheKey`, 검색/스코어링 본체(:186-434).
   - **`src/tools/ToolSearchTool/prompt.ts`** — `PROMPT_HEAD`, `isDeferredTool()`(:62-108, 판정 우선순위 전문), `getToolLocationHint()`.
   - **`src/utils/toolSearch.ts`(756줄, 여러 구간 Read)** — `getAutoToolSearchTokenThreshold/CharThreshold`(:104-117), `getDeferredToolTokenCount`(memoize, :124-152), `isToolSearchEnabled`(:385-473, 모델지원체크+로그), `extractDiscoveredToolNames`(:545-592, compact_boundary 이월 로직 포함), `isDeferredToolsDeltaEnabled/getDeferredToolsDelta`(:629-706).
   - **`src/services/api/claude.ts:1150-1250`** — deferred 도구 필터링 규칙(비deferred 항상전송/ToolSearch자신 항상전송/deferred+미발견 제외/deferred+발견 defer_loading true 전송), tool search 베타헤더 부착 로직(:1174-1182).
   - **`src/utils/api.ts:100-224`** — `toolToAPISchema`(세션-stable base schema 캐시, cacheKey에 inputJSONSchema 포함 이유 주석 — PR#25424 참조 err rate 5.4%→51% 사례), `deferLoading` per-request overlay(:211-224), FGTS(`eager_input_streaming`) 게이팅(:194-206).
   - **`src/utils/attachments.ts:1440-1475`** — `getDeferredToolsDeltaAttachment`(:1454-1475, compact.ts와 게이트 동일성 주석), **`:800-860`** — 델타 4형제 `maybe(...)` 등록 순서.
   - **`src/utils/messages.ts:4178-4207`** — `deferred_tools_delta`/`agent_listing_delta` 렌더링 원문(system-reminder 문구).
   - **`src/query.ts`(task-notification 관련), `src/tasks/LocalMainSessionTask.ts:262`, `src/utils/messageQueueManager.ts:120-175`, `src/utils/queueProcessor.ts:1-40`, `src/hooks/useQueueProcessor.ts`(전문 Read), `src/utils/QueryGuard.ts`** — (미완결 조사) `enqueue`(priority `'next'`) vs `enqueuePendingNotification`(priority `'later'`), `PRIORITY_ORDER`, `useQueueProcessor` 훅의 `useSyncExternalStore`+`useEffect` 기반 유휴 자동 드레인 후보 메커니즘. **최종 결론 도출 전 구간 종료.**

4. Errors and Fixes:
   - (이전 라운드) 부정확한 설명 자가 정정 — "다음 사이클 전처리가 우편함을 비운다" → "같은 사이클 꼬리에서 수집됨"으로 교정.
   - (이전 라운드) 훅 관련 사용자 혼란 재발 → 밀도 높은 설명 대신 구체적 시나리오로 재설명해 해결.
   - (이전 라운드) Python 스크립트 카운터 버그("inserted: 0 markers" 오출력) → `grep -c` 직접 확인으로 실제 정상 삽입이었음을 검증.
   - **(이번 구간) 설명 오도 → 사용자 지적으로 정정**: "lost-in-the-middle 4중 안전망" 설명 중 ①번을 "tools 배열에 (검색될 도구) 목록이 있다"는 뉘앙스로 서술 → 사용자가 "tools에는 검색될 도구 목록은 안들어가잖니"로 정확히 지적 → 어시스턴트가 "제가 모호하게 말했다"고 인정하며 정정: tools 배열엔 **ToolSearch 자신과 그 설명문**만 있고, 실제 도구 이름 목록은 **대화 이력의 system-reminder에만** 존재한다는 것으로 명확히 재정리. 사용자 피드백 원문: "1번 무슨말인지 모르겠네.. tools에는 검색될 도구 목록은 안들어가잖니".

5. Problem Solving:
   - (이전 라운드, 변경 없음) rules 지연주입, 수집(+)/전처리(−) 구간 분리, frontmatter 4종 공통구조, `/visual-explainer` 활용, compact 직후 프롬프트 구성, 훅 시스템 전체, `<user-prompt-submit-hook>` 정체, MCP 지시 2모드, 캐시 경계 마커 — 전부 소스로 완전 규명·완료.
   - **src-대조 마킹 최종 재검증 완료**: `grep -n "🔴"` + `sed` 위치 대조로 4개 신규 도구(Workflow·Artifact·ReportFindings·ScheduleWakeup) + 모델정체성문단 + 자율행동문단이 3중(본문/부록-2/범례)으로 정확히 표기됐음을 확인, 사용자 재검증 질문에 완전 답변.
   - **ToolSearch 시스템 전체를 소스로 완전 규명**: 5단계 생애주기, 분류 우선순위, 3모드 게이트, 델타 고지 메커니즘과 4형제 어태치먼트, select/키워드 2경로, 점수표(BM25 아님을 명시적으로 반증), tool_reference 영수증과 대화-이력-기반 상태 관리, compact 경계 이월. 이어지는 10여 개 후속 심화 질문(카드목록 타이밍/첫 프롬프트 포함 여부/세션 중 MCP 추가 반영/lost-in-the-middle 4중 안전망과 잔여 구멍/필드가중치)까지 전부 소스 근거로 답변 완료.
   - **lost-in-the-middle의 정직한 한계 인정**: "설계가 문제를 없앤 게 아니라 실패 모드를 바꿨다"는 결론과, "unknown unknowns" 구간엔 안전망이 무력하다는 점을 감추지 않고 명시 — CLAUDE.md의 "미확인 부분은 확인 못함으로 표기" 원칙을 충실히 적용한 사례.
   - **(미완료, 구간 종료 시점)**: ① 최신 대화 내용을 md/html에 반영하는 작업 — md는 §08 Q&A 섹션과 검증이력 갱신까지 Edit 완료됐으나, html의 "07 추가 Q&A" 섹션 Edit이 완성됐는지 확인 전 상태(마지막 Edit 호출의 new_string이 문장 중간에서 끊긴 채 표시됨). 이어진 `open` 명령의 실행 결과도 확인되지 않은 채 구간 종료. ② 사용자의 새 질문("ReAct사이클이 아닌 경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?")에 대한 조사는 진행됐으나(task-notification 큐 priority 구조, `useQueueProcessor`의 유휴 자동 드레인 후보 메커니즘까지 확인) **최종 종합 답변은 아직 사용자에게 전달되지 않음**.

6. All User Messages:
   1. "클로드코드 전체파악해봐라"
   2. "4번은 무슨말이지"
   3. "근데 단독이면 Read,Read, Grep,Edit, Write 가 한배치에 나오면 1배치에 Read, Read, Grep 이고 2배치에 Edit 3배치에 Write 야?"
   4. "이건 소스코드 보고 증명해봐"
   5. "증거4 후자의 경우 Read -> Edit 하고 다시 병렬이됬잖아? 중간에 Edit이 낀 이유는 같은파일 기준이라 그래?"
   6. "아 이해했다 오케이"
   7. "아 저건 몰랐네.. 단독 .. 이라는 개념이구나 나 분리만하는줄 저거 너가 테스트해본거까지 md로 마들어주라"
   8. "내가 알기로는 0번 유저프롬프트에 CLAUDE.md 관련내용과 함께 현재 스킬목록도 들어가는걸로 알고있어 맞아?"
   9. "어쨋든 타이밍은 배열로 들어간다는거지"
   10. "그리고 그 rules로 하면 필요한 상황일떄 그걸로가져와쓰잖아 그건 어떻게 세팅한거지"
   11. "음..???? 이해가 안되네"
   12. "Read툴이 읽으면 마치 훅마냥 잡아서 실행해서 어태치먼트로 넣는거야?"
   13. "ReAct 사이클 전처리가 도구결과 보낼떄 인건가"
   14. "컨텍스트 전처리 하는 구간과는 다른거지?"
   15. "프론트메타로 쓰는건 다그렇다고봐야돼? 스킬도 포함해서?"
   16. "위 내용들도 /visual-explainer 로 작성해줘"
   17. (frontmatter 4종 비교표를 붙여넣으며) "특히 이거 잘작성해줘"
   18. [슬래시커맨드 /compact] — 실제 Claude Code 자체 컴팩션 발동(세션 내부 이벤트)
   19. "지금 유저프롬프트로 내용 뭐들어가?"
   20. "user-prompt-submit-hook 이건 언제씡늑너지"
   21. "무슨말이야? 나프롬프트 중에\n\n - 사용자는 설정에서 도구 호출 등의 이벤트에 반응하여 실행되는 셸 명령인 'hooks'를 구성할 수 있습니다. <user-prompt-submit-hook>을 포함한 hooks의 피드백은 사용자로부터 온 것으로 취급하세요. hook에 의해 차단되면, 차단된 메시지에 대응하여 행동을 조정할 수 있는지 판단하세요. 불가능하면 사용자에게 hooks 설정을 확인하도록 요청하세요.\n\n이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구....."
   22. "훅출력이 낄때가있다고 무슨말이야 ?"
   23. "UserPromptSubmit 이게 도대체 뭔데 ㅋㅋ 무슨훅을 말하는거야 배경부터 설명해야지"
   24. "내가 지정한 셀 스크립트를 자동 실행하라는건 에이전트상 어떤 툴을 실행한다는건데 뭘실행한거야"
   25. "아니 저게 그러면 무슨말이야......"
   26. "<user-prompt-submit-hook> 이라는건 여기 소스코드 어디에 나오는말이야"
   27. "getHooksSection() 은 어디안에서쓰는데?"
   28. "사실상 <user-prompt-submit-hook>라는 태그는 따로 없구나 이거 개발자가 작업하다 안지운 가능성이 큰거네"
   29. "시스템프롬프트의 mcp 서버지시의 실제 예시는 어떻게 될까?"
   30. [슬래시커맨드 /login] — 실제 로그인 이벤트(세션 내부 이벤트)
   31. "<local-command-stdout>Login successful</local-command-stdout>" — 슬래시커맨드 실행 결과 stdout
   32. "지금 현재 세션에 인풋되는 시스템프롬프트랑 도구 설정 내용들 싹다 md로 만들어줄래?"
   33. "시스템프롬프트랑 툴 정리란에 혹시 소스코드랑 다른내용들있나 내가 가진 소스코드가 구버전이라.. 옛날거긴해 그것들 다르다고 표시를 잘해줄수잇니?"
   34. "없는거 md에 잘적은거 맞지?"
   35. "2027-07-11-시스템프롬프트및도구내용-최신본 이라구 이름바꿔주고 그리고 /visual-explainer 로 html버전도 만들어줄래?"
   36. "도구의 toolsSerach에 대한 로직을 상세히 알려줘"
   37. [슬래시커맨드 /visual-explainer] (인자 없음)
   38. "md로도 만들어주고 /visual-explainer로도 만들어주라"
   39. "툴서치 쓸때마다 그때 인풋으로 system-reminder가 항상들어오는거야?? 어느타이밍을 말하는거지"
   40. "system-reminder로 유저 첫번째 프롬프트에 들어가나?"
   41. "그러면 그..나중에 mcp추가하면 그때 최신 메시지에 어태치먼트로 들어가?"
   42. "근데 대화가 길어지다보면 중간에 껴서 로스트인더미들로 까먹는거 아닌가"
   43. "1번 무슨말인지 모르겠네.. tools에는 검색될 도구 목록은 안들어가잖니"
   44. "아아 찾는방법만 리마인드하는구나 그럼 여전히 로스트인더미들 문제는있는거 아니야?"
   45. "좀쉽게말해봐 플로우 위주로;;;"
   46. "흐름2에서 한단어만들어가? 키워드검색이? 그럼 진짜놓치기 쉬워보이는데"
   47. "궁금한게 그.. 만약에 새로운 mcp세팅하면 그때도 다시 추가됬다고 알려줄거 잖아? 그때 유저가 엔터쳐야 시스템리마인더가 함께 들어가? 아니면 자동이야? 그리고 키워드검색 알고리즘은 BM25야?"
   48. "필드별가중치는 뭐였지"
   49. "위에 추가된 내용 다 md와 html에 반영해줘 그리고 새로운질문\nReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?"

7. Pending Tasks:
   - 사용자의 새 질문("ReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?")에 대한 **직접적·종합적 답변 전달** — 조사(task-notification 큐 priority 구조, `useQueueProcessor` 유휴 자동 드레인 메커니즘)는 완료됐으나 사용자에게 아직 답변하지 않음. **미완료.**
   - "위에 추가된 내용 다 md와 html에 반영해줘" 요청의 완료 확인 — md(`toolsearch-생애주기-소스분석.md`)의 §08 섹션과 검증이력 Edit은 완료 확인됐으나, html(`toolsearch-생애주기-소스분석.html`)의 "07 추가 Q&A" 섹션 Edit이 실제로 온전히 삽입됐는지, 그리고 마지막 `open` 호출이 정상 실행됐는지 **미확인**.
   - (열린 제안, 확정 요청 아님) `배치-단독-개념-소스증명.md`의 짝꿍 HTML 시각화 문서 제작 여부 — 여전히 요청 없음, 보류.

8. Current Work:
   사용자가 마지막으로 보낸 복합 요청("위에 추가된 내용 다 md와 html에 반영해줘 그리고 새로운질문 ReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?")을 처리하던 중이었다. 어시스턴트는 먼저 새 질문 검증을 위해 `grep -rn "task-notification\|task_notification"`, `enqueuePendingNotification` 정의(`messageQueueManager.ts:120-149`), `processQueueIfReady`/`useQueueProcessor.ts`(전문 Read)를 조사해 **"유저 발화는 priority `'next'`, 시스템 알림(task-notification 등)은 priority `'later'`이며, `useQueueProcessor` 훅이 `isQueryActive===false`이고 큐가 비어있지 않을 때 `useEffect`로 자동으로 `processQueueIfReady`를 호출한다"**는 사실까지 확인했다. 이어서 첫 번째 요청(md/html 반영)으로 전환해 `toolsearch-생애주기-소스분석.md`에 Edit 2회(§08 추가 Q&A 보강 섹션 삽입, 검증이력 라인 갱신)를 완료했고, `toolsearch-생애주기-소스분석.html`에도 Edit 2회를 시도했다 — 첫 Edit(스코어링 섹션 소제목에 "BM25 아님 → 07" 태그 추가)은 완료됐으나, 두 번째 Edit(footer 직전에 "07 추가 Q&A" 전체 섹션을 삽입하는 대형 HTML 블록)은 도구 호출 자체는 성공 결과를 반환했지만 **그 new_string 내용이 로그 상 문장 중간("Q. 카드 목록 고지는 언제 실리나 — 푸시가 아니라 \" )에서 끊긴 채로 표시**되어 있어 실제로 완성된 문장으로 삽입됐는지 확인이 필요한 상태다. 마지막으로 `open "toolsearch-생애주기-소스분석.html"` Bash 명령을 호출했으나, **그 결과가 이 대화 구간에 도착하기 전에 구간이 종료**됐다.

9. Optional Next Step:
   방금 호출한 `open "/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html"`의 실행 결과를 확인한 뒤, html의 "07 추가 Q&A" 섹션이 온전한 문장/마크업으로 삽입됐는지 `Read`나 `grep`으로 재검증하고, 그다음 사용자의 새 질문(직전 발화 그대로 인용: "ReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?")에 대해 이미 확인한 조사 결과(유저입력=priority `'next'` vs 시스템알림=priority `'later'`, `useQueueProcessor`의 유휴 자동 드레인 메커니즘, 그리고 이 세션에서 이미 실측한 "사이클 꼬리 자동 삽입" 사례)를 종합해 "엔터 없이도 시스템리마인더/어태치먼트가 올라가는 예외 케이스가 실제로 존재한다"는 방향으로 답변을 완성해 전달해야 한다.

</summary>
