## 단계 1

### Current progress and key decisions made

- **Session goal (unchanged)**: 사용자가 `/Users/seobi/jinsup_space/CC` (Claude Code 내부를 리버스엔지니어링하는 리서치 레포: `md_group/` 분석 문서, `html_group_v2/` HTML 시각화, `src/` 재구성 소스)를 대상으로 세부 메커니즘을 하나씩 깊게 파고드는 세션. 이번이 4번째 컴팩션 사이클.

- **Chain 1 — 배치 병렬/파티셔닝 (완전 종결)**: `partitionToolCalls`가 `isConcurrencySafe` per-tool 선언만으로 병렬/단독 배치를 나눔(파일/인자 비교 없음). 산출물 `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` 완성, 재작성 금지. HTML 짝꿍은 미제작 대기.

- **Chain 2 — 컨텍스트 주입 4트랙 (완전 종결)**: 0번 유령 메시지(`prependUserContext`, 매 호출 재생성) vs skill_listing(정주민) vs conditional rules(우편함 패턴) vs frontmatter 4종(값싼 색인 상시·비싼 본문 트리거시). 산출물 `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` 완성, 재작성 불필요.

- **중간 이벤트 — 실제 Claude-Code 네이티브 `/compact`**: 세션 중 실제로 발생, PostCompact 훅(`~/.claude/scripts/cc-name.sh`)이 발동. 지금 시뮬레이션 중인 codex-레벨 압축과는 별개의 실사건이며 재론 불필요.

- **Chain 3 — UserPromptSubmit 훅 / `getHooksSection()` (완전 종결)**: `getHooksSection()`(`prompts.ts:127-129`)의 3문장은 `getSimpleSystemSection()`을 통해 무조건 시스템 프롬프트에 포함됨. 훅은 툴이 아니라 하네스가 `spawn`으로 직접 실행(`hooks.ts:7,977`). `<user-prompt-submit-hook>` 태그는 src 전체에서 `prompts.ts:128` 언급 1곳뿐이며 실제 렌더링 코드는 0곳 — 과거 버전 잔재로 추정(확정 불가). `getMcpInstructionsSection()`은 구형 `DANGEROUS_uncached`(매턴 재계산) vs 델타 모드(`mcp_instructions_delta`) 2종 배달방식 확인. 캐시 경계(`SYSTEM_PROMPT_DYNAMIC_BOUNDARY`, `api.ts:321-410`) 앞=글로벌캐시/뒤=세션조건부임을 소스 주석(`prompts.ts:371-372`)으로 확정.

- **Chain 4 — 세션 인풋 전문 스냅샷 문서화 (완료, 단 Chain 6에서 리네임됨)**: `/login` 직후 사용자 요청으로 현재 컨텍스트 윈도우 전체를 자기전사(self-transcription). Part1(system 13섹션)~Part4(대화히스토리+T1~T24)까지 작성 완료. 채집 중 라이브 사실 2건 발견: ① `userEmail`이 `/login` 전후 실제 변경(0번 유령 메시지 재생성 증거), ② 실서비스는 `# System`→`# Harness` 개편되며 `<user-prompt-submit-hook>` 언급이 삭제됨(Chain3 "잔재" 가설 방증).

- **Chain 5 — src vs 실서비스 diff 마킹 (이번 세그먼트에서 완전 종결)**: 직전 요약 시점에 미해결이던 "🔴 마커가 정확한 위치·판정으로 붙었는지" grep 결과를 확인·보고 완료. 검증 결과: `## 1-4`(모델정체성, 144행)·`## 2-2`(Artifact, 514행)·`## 2-7`(ReportFindings, 689행)·`## 2-8`(ScheduleWakeup, 708행)·`## 2-11`(Workflow, 800행)에 정확히 붙었고, `## 1-10`(Context management, 300행)은 🟡+🔴 혼합 표기가 올바름을 확인. 부록-2(도구 12종 대조표)와 문서머리 범례(6행)도 정합. 1509행에 걸린 별도 🔴는 마커가 아니라 Part4 대화이력에 기록된 과거 답변 원문의 이모지임을 정확히 구분해 오탐 아님을 설명 — 사용자 질문 "없는거 md에 잘적은거 맞지?"에 근거 제시하며 확답 완료. **Chain 5 CLOSED.**

- **Chain 6 — 파일명 변경 + HTML 짝꿍 (신규, 완결)**: 사용자가 "2027-07-11-시스템프롬프트및도구내용-최신본 이라구 이름바꿔주고 /visual-explainer 로 html버전도"라고 요청. 어시스턴트가 "2027"을 오늘 날짜(2026-07-11) 대비 오타로 판단해 **2026**으로 정정(사용자에게 정정 사실 명시, 진짜 2027 원했으면 재요청 안내)하고 `mv`로 `/Users/seobi/jinsup_space/CC/세션인풋-시스템프롬프트-도구-전문.md` → `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`로 리네임. 이어서 Skill `visual-explainer`로 `2026-07-11-시스템프롬프트및도구내용-최신본.html` 작성: **청사진(blueprint) 제도 도면 컨셉** — 네이비 그리드 배경+시안 선묘, 도면번호/검증방법 타이틀블록, 신규도구엔 회전 "SRC 無" 스탬프; 폰트 Do Hyeon+IBM Plex Sans KR+IBM Plex Mono; 01 적재구조(system↔messages 좌우 화물칸), 02 시스템13섹션(14행 판정색), 03 도구12종 카드그리드(신규4종 붉은점선+스탬프), 04 상주화물 6레인, 05 대시보드(분포바+경향칩+발견2건). 브라우저에 열림. 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동) 제안했으나 요청 없음 — 대기.

- **Chain 7 — ToolSearch 도구 지연로딩 시스템 완전 규명 (이번 세그먼트의 핵심, 대부분 완결 · 문서반영 일부 미확인)**:
  - 사용자 질문 "도구의 toolsSearch에 대한 로직을 상세히 알려줘"에 대해 src 전체(`ToolSearchTool.ts`, `prompt.ts`, `toolSearch.ts` 756줄, `api.ts`, `claude.ts`)를 추적해 **5단계 생애주기**로 규명:
    1. **분류** `isDeferredTool()`(prompt.ts:62-108) — `alwaysLoad:true` 최우선 opt-out → MCP도구 무조건 defer → ToolSearch 자신은 절대 defer 안 함 → FORK_SUBAGENT 실험시 Agent 예외 → Brief 통신채널 예외 → 나머지는 `shouldDefer:true`만.
    2. **모드 게이트** (toolSearch.ts:172-198,385-473) — `ENABLE_TOOL_SEARCH` 3모드: `tst`(기본, 항상defer) / `tst-auto`(토큰총량이 컨텍스트 N% 초과시만, 토큰카운팅API→char휴리스틱 폴백) / `standard`(구식 전부인라인). 추가 게이트: 킬스위치, 모델의 tool_reference 지원여부(haiku계열 미지원 기본패턴).
    3. **고지** `deferred_tools_delta`(toolSearch.ts:629-706) — 이미 고지한 이름 집합을 이력 스캔으로 재구성 후 차집합만 어태치먼트로 발행. "defer 풀렸지만 여전히 존재"는 removed로 보고 안 함(거짓방지, :641-644).
    4. **검색** `call()`(ToolSearchTool.ts:328-434) — A) `select:` 경로(콤마다중, 기로드도구 select해도 성공, 0건시 연결중서버 안내) B) 키워드 경로 3단폴백(exact-name fast path → mcp__프리픽스 → 스코어링). 스코어표: 이름조각정확 MCP12/일반10, 이름조각부분 MCP6/일반5, searchHint4, 설명문word-boundary2, fullname폴백3(0점때만). 여러단어 합산, `+term` 필수텀 지원.
    5. **로드/재조립**(claude.ts:1150-1187) — 검색결과는 `tool_reference` 블록으로 tool_result에 실림(텍스트 아님). 요청조립규칙: 비deferred=항상전송/ToolSearch자신=항상전송/deferred+미발견=tools배열에서 아예제외/deferred+발견=defer_loading:true로 전송. "발견" 판정은 별도상태 아니라 **대화이력 자체를 스캔**(`extractDiscoveredToolNames`, toolSearch.ts:545-592)해서 재구성 — 대화가 곧 영수증. compact_boundary 마커에 `preCompactDiscoveredTools`로 이월돼 compact를 넘어도 복원됨. 스키마 확장 자체는 API서버가 수행(베타헤더 필수).
  - 사용자 요청("md로도 만들어주고 /visual-explainer로도")에 따라 2종 산출물 작성: `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`(§00 큰그림~§06 실측+검증이력) 및 `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html`(**폐가식 서고+대출시스템 메타포**, 웜다크아카데미아 세피아+황동, Gowun Batang/Gothic A1/IBM Plex Mono, 01~06 섹션). 브라우저에 열림.
  - 이후 사용자가 **연쇄 재질문 9라운드**를 던졌고 매번 소스 재검증(attachments.ts:836-875,1440-1485 / ToolSearchTool.ts:194-198,266-291 / toolSearch.ts:606-706 / messageQueueManager.ts 등) 후 답변, 핵심 결론:
    - 카드 목록(`deferred_tools_delta`)은 **ToolSearch 호출과 무관** — 어태치먼트 파이프라인이 수집지점(턴시작+사이클꼬리)마다 "풀 변화 있을 때만" 발행(getDeferredToolsDelta, 차이없으면 null:677). 델타 4형제(deferred_tools_delta:836/agent_listing_delta:851/mcp_instructions_delta:854/skill_listing:875)가 같은 `maybe()` 목록에 등록.
    - 세션 첫 턴엔 "이미 고지 집합=0"이라 델타=전체 목록 → 사실상 첫 프롬프트와 함께 감(단, 프롬프트 "안"이 아니라 "옆"에 별도 isMeta 메시지로). compact 후도 동일 원리로 재발행 — **compact가 리프레시 역할**.
    - MCP 신규연결은 연결 즉시가 아니라 **다음 수집지점**에 삽입 — 유저가 대기중이면 엔터가 트리거(턴시작 수집), 모델이 작업중이면 사이클꼬리(query.ts:1569)에서 **엔터 없이 자동** 삽입. 이 세션에서 실측(figma/supabase/vercel 연결이 작업중 턴에 무입력으로 끼어듦; Atlassian/Gmail 등 61개 해제 공지는 유저 프롬프트 턴에 동반).
    - **로스트인더미들 문제**: 하네스 상태는 프로그램적 스캔이라 절대 안 잃음, 취약한 건 모델 attention. 4중 안전망 — ① ToolSearch 자신의 설명문은 tools배열에 매 요청 fresh하게 실림("표지판"은 안 묻힘) ② 키워드검색(암기 불필요) ③ bare-name fast path(주석: "seen from subagents/post-compaction" — 기억열화 실측 기반 방어선) ④ 실패시 명시적 "No matching" 반환→재시도유도. compact가 옛 고지를 쓸어내 prior=0을 만들어 전체 재발행되는 것도 방어선. **그러나 정직한 잔여 리스크**: "그런 도구가 있다는 발상 자체를 못 하는" unknown-unknowns 구간은 소스상 추가 재주입 장치 없음 — 표지판은 "검색법"만 알려주지 "뭘 검색할지"는 못 알려줌. 완화 요인(우연): 유저가 보통 단어를 직접 언급, MCP지침이 의미적 라우팅 힌트 제공, compact가 대개 그 지경 전에 옴.
    - **키워드검색 알고리즘 = BM25 아님** — TF/IDF/문서길이정규화 전부 없음, 필드가중치만 하드코딩(위 스코어표). "필드가중치를 손으로 박은 불리언매칭+합산정렬". 근거: 검색대상이 수백건 미니목록(코퍼스통계 무의미) + 쿼리작성자가 LLM이라 실패시 재시도(재시도루프의 두뇌=모델). 한국어/동의어는 매치 안 됨(임베딩 없음, 순수 어휘매칭) — "지라 이슈" 검색 실패 → "jira issue" 재시도로 극복하는 구조.
  - **세그먼트 마지막 턴**: 사용자가 "위에 추가된 내용 다 md와 html에 반영해줘 그리고 새로운질문\nReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?"로 **두 가지 지시를 동시에** 던짐 — (a) 상기 Q&A 전체를 두 산출물에 반영, (b) 신규 질문(비-ReAct 사이클 자동주입 예외). 어시스턴트는 (b)부터 src 검증 착수 → Chain 8로 이어짐.

- **Chain 8 — "비ReAct 사이클 시스템리마인더/어태치먼트 자동주입 예외" 질문 (신규, 미해결·진행 중, 다음 세션 최우선)**:
  - 검증 진행 상황: `query.ts:1564-1566`(서브에이전트는 자기주소 task-notification만 드레인), `:1619-1621`(prompt/task-notification→어태치먼트 변환); `tasks/LocalMainSessionTask.ts:262`(`enqueuePendingNotification({mode:'task-notification'})`); `attachments.ts:760,829,1046`(`getQueuedCommandAttachments`, `maybe('queued_commands',...)` 등록); `messageQueueManager.ts:128-135`(`enqueue()` — 유저입력용, 기본 priority `'next'`) vs `:142-149`(`enqueuePendingNotification()` — 태스크알림용, 기본 priority `'later'`, 주석: "user input is never starved by system messages"), `:151-155`(`PRIORITY_ORDER` now=0/next=1/later=2, 동순위 FIFO); `queueProcessor.ts:52`(`processQueueIfReady`); **`hooks/useQueueProcessor.ts` 전문 Read 완료** — `useSyncExternalStore`로 `queryGuard`+커맨드큐 구독, `useEffect`가 `!isQueryActive && !hasActiveLocalJsxUI && queueSnapshot.length>0` 조건 충족시 `processQueueIfReady`를 **자동 호출** — 이것이 유저 키입력이 아니라 **React state 변화 자체가 트리거**가 되어 엔터 없이 큐를 드레인하는 실제 메커니즘으로 보임(결론 도출 직전); `processUserInput.ts:143`("Skip for isMeta (system-generated prompts like scheduled tasks)" 주석).
  - **아직 사용자에게 답변 전달 안 됨.** `useQueueProcessor.ts`를 다 읽은 직후, 어시스턴트가 (a) 작업(md/html 반영)으로 전환해 Edit 4건 실행: `toolsearch-생애주기-소스분석.md`에 "§08 추가 Q&A 보강" 섹션 삽입 + 검증이력 라인 갱신, `toolsearch-생애주기-소스분석.html`에 헤딩 "07" 참조 추가 + "07 추가 Q&A — 타이밍 · 망각 · 알고리즘" 섹션 삽입, 이어서 `open`으로 HTML 재오픈 Bash 호출을 실행 — **이 Bash 호출의 완료/출력이 트랜스크립트에서 확인되기 전에 세그먼트가 끝남.**
  - **(a) 반영 완전성도 미확인**: Edit 인자 문자열이 트랜스크립트 표시상 중간에 잘려(...) 있어, 삽입된 "§08/07 추가 Q&A" 섹션이 세그먼트에서 논의된 9라운드 전부(카드목록타이밍/첫프롬프트포함여부/MCP추가삽입시나리오/로스트인더미들4중안전망/흐름1~3설명/키워드검색다중단어/BM25비교표/필드가중치재정리/엔터vs자동케이스A·B)를 담았는지, 섹션 제목이 시사하는 3토픽(타이밍·망각·알고리즘)만 담았는지 불명.

### Important context, constraints, and user preferences
- 대상 레포: `/Users/seobi/jinsup_space/CC` (현재 `research` 레포와는 별개, `research/notebooks/claude_code`의 GPT-하네스 규약 미적용).
- 사용자 전역 선호(개인 지침, 전 프로젝트 공통): 탐색/분석은 `Explore`, 플래닝은 `Plan` 서브에이전트에 위임하고 실행은 메인에서 직접; 결정/선택 필요시 `AskUserQuestion` 사용, prose로 풀어 묻지 않기.
- 레포 고유 규약(전 세그먼트 통틀어 계속 준수):
  - Claude Code 내부에 대한 모든 비자명한 주장은 `~/jinsup_space/CC/src`를 직접 `grep`/`Read`로 검증. "확인 못함(⚪)" 라벨을 정직하게 씀.
  - 루트 `.md` 문서는 관례상 `html_group_v2/`에 짝꿍 HTML을 두지만, 이번 세션의 신규 산출물(Chain6/7)들은 모두 레포 루트에 md+html 페어로 위치 — `html_group_v2/`로의 정식 이동은 아직 안 됨(재요청시에만).
  - 문서 내 경로는 `~`-상대/중립 표기가 기본이나, Chain4/6 세션인풋 문서는 "일회성 스냅샷" 예외로 기계 절대경로 유지(문서 자체에 명기됨).
  - 새 분석 문서는 기존 톤/구조(번호 섹션, file:line 근거, 마무리 검증 로그)를 따름.
- 사용자의 질문 스타일: 좁은 메커니즘 하나를 재질문으로 계속 파고드는 패턴이 세션 내내 이어짐. 이해가 막히면("아니 저게 그러면...", "좀쉽게말해봐 플로우 위주로;;;") **더 구체적인 시나리오/표/플로우로 재설명**을 요구 — 추상적 재설명 대신 실제 벌어지는 순서를 단계별로 실연해야 통과됨. 이번 세그먼트(Chain7)에서 특히 뚜렷 — 9라운드 연쇄 재질문 전부 이 패턴.
- **행동 시그널(계속 유효, 이번 세그먼트에도 재확인)**: 어시스턴트가 사용자의 리터럴하고 구체적인 질문 대신 더 일반적/인접한 버전으로 답하면 사용자가 즉시 날카롭게 지적함(예: "1번 무슨말인지 모르겠네.. tools에는 검색될 도구 목록은 안들어가잖니" — 어시스턴트가 즉시 정정·사과 없이 담백하게 재설명).
- **자기검증(self-verification) 습관**: Chain5에서 어시스턴트 자신이 작성한 문서의 정확성 재확인 요구에 grep으로 근거 제시하며 확답 — 이 패턴이 이번 세그먼트에서 완결됨. 도구 출력(자체 검증 스크립트의 "inserted:0" 오탐 등)을 맹신하지 않고 실물로 재확인하는 습관 유지.
- **신규 — 복수요청 처리 패턴**: 사용자가 한 메시지에 "기존 작업 반영 + 새 질문"을 동시에 던지는 경우(Chain7 마지막 턴) 발생 — 어시스턴트는 새 질문의 소스검증을 먼저 시작했으나, 두 지시 모두 완결하지 못한 채(문서반영도 완전성 미확인, 새질문 답변도 미전달) 세그먼트가 끝남. 다음 세션은 **두 가지 모두**를 사용자에게 명시적으로 완결·보고해야 함.
- **신규 — 날짜/파일명 오타 정정 관행**: 사용자가 "2027-07-11"이라 썼을 때 어시스턴트가 오늘 날짜(2026-07-11) 기준 오타로 판단해 자체 정정하고 그 사실을 사용자에게 고지 — 확답은 아직 못 받음(사용자가 정말 2027을 원했을 가능성 낮지만 이론상 열려있음).
- 모든 응답은 한국어(세션 초반부터의 지속 제약).

### What remains to be done (next steps)
1. **최우선**: Chain 8 — 사용자의 신규 질문 "ReAct 사이클이 아닌 경우는 다 엔터쳐야 시스템리마인더/어태치먼트가 올라가는가, 예외는 있나?"에 확답. 조사는 거의 끝난 상태 — 유력 결론 후보는 "`useQueueProcessor.ts`의 React `useEffect`가 (쿼리비활성 && JSX UI 안막힘 && 큐에 항목있음) 조건에서 유저 키입력과 무관하게 자동으로 `processQueueIfReady`를 호출하며, `enqueuePendingNotification`(priority `'later'`)로 들어온 task-notification류가 이 경로로 엔터 없이 드레인된다"는 것. 필요시 `queueProcessor.ts:52` 이하 `processQueueIfReady` 본문과 `getQueuedCommandAttachments`(attachments.ts:1046~)를 추가로 Read해 마무리 확인 후, 표/플로우 형식(사용자 선호 패턴)으로 답변할 것.
2. Chain 7 (a) 반영 완전성 재확인 — `toolsearch-생애주기-소스분석.md`의 "§08 추가 Q&A 보강" 섹션과 `.html`의 "07 추가 Q&A" 섹션이 세그먼트에서 논의된 9라운드 전부를 담았는지 grep/Read로 재확인, 누락 있으면 Edit로 보강.
3. `open` Bash 호출(HTML 재오픈)의 완료 여부 확인 — 실패했다면 재실행.
4. Chain 1~6은 전부 완료·전달됨, 재론 불필요.
5. 낮은 우선순위, 재요청 시에만: `배치-단독-개념-소스증명.md` HTML 짝꿍(미제작); `2026-07-11-시스템프롬프트및도구내용-최신본.html`의 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동).

### Critical data / references needed to continue
- 레포 루트: `/Users/seobi/jinsup_space/CC`; 문서 `md_group/`, HTML 미러 `html_group_v2/`, 재구성 소스 `src/`.
- **Chain1~4 근거 요약(재검증 없이 인용 가능, 상세 file:line은 이전 요약본에 전량 보존)**: 배치파티셔닝 `toolOrchestration.ts:95-116`(partitionToolCalls) 등; 컨텍스트4트랙 `api.ts:449-474`(prependUserContext), `context.ts:155-189`(getUserContext) 등; UserPromptSubmit훅 `hooks.ts:7,977`(spawn 실행주체), `prompts.ts:127-129`(getHooksSection 원문, src 유일언급 `:128`) 등; MCP지시 `prompts.ts:160-165`(getMcpInstructionsSection); 캐시경계 `api.ts:321-410`(splitSysPromptPrefix, SYSTEM_PROMPT_DYNAMIC_BOUNDARY), `prompts.ts:371-372`(post-boundary 이유 주석).
- **Chain5 완결 근거**: `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`(구 `세션인풋-시스템프롬프트-도구-전문.md`) 내 마커 위치 — `## 1-4`(144행)·`## 2-2`(514)·`## 2-7`(689)·`## 2-8`(708)·`## 2-11`(800)·`## 1-10`(300, 혼합) 전부 정확 확인됨, 부록-2·범례(6행)도 정합, 1509행 건은 오탐 아님(Part4 대화이력 원문의 이모지).
- **Chain6 산출물**: `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`, `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.html`(청사진 제도도면 컨셉, Do Hyeon+IBM Plex Sans KR+IBM Plex Mono).
- **Chain7 ToolSearch 핵심 소스 좌표**:
  - `src/tools/ToolSearchTool/ToolSearchTool.ts`(472줄) — `call()` :328-434, `select:`경로 :363-406, 스코어링 `searchToolsWithKeywords` :186-302, 이름파싱 :132-161, `+term`필수텀 :236-257, 스코어표 :266-291.
  - `src/tools/ToolSearchTool/prompt.ts` — `isDeferredTool()` :62-108(alwaysLoad>MCP>ToolSearch자신>FORK_SUBAGENT>Brief>shouldDefer 순서), PROMPT_HEAD/TAIL 쿼리형식안내 :35-42("Deferred tools appear by name in system-reminder messages"), name+hint A/B실험 폐기 :110-117.
  - `src/utils/toolSearch.ts`(756줄) — `getAutoToolSearchTokenThreshold` :104, `getAutoToolSearchCharThreshold` :115, `getDeferredToolTokenCount` memoize :124-152, `isToolSearchEnabled` :385+, `extractDiscoveredToolNames` :545-592(대화이력 스캔으로 발견집합 재구성, compact_boundary의 `preCompactDiscoveredTools` 이월 :553-558), `isDeferredToolsDeltaEnabled` :629, `getDeferredToolsDelta` :646-706(차이없으면 null :677), compact_full 텔레메트리 주석 "prior=0 is EXPECTED" :606-608.
  - `src/utils/attachments.ts` — `getDeferredToolsDeltaAttachment` :1454-1475(4게이트: 델타모드on/tool search optimistic on/모델 tool_reference지원/ToolSearch도구 available), `maybe()` 등록순서 `deferred_tools_delta`:836/`agent_listing_delta`:851/`mcp_instructions_delta`:854/`skill_listing`:875, 렌더링 `messages.ts:4178-4193`.
  - `src/services/api/claude.ts:1150-1187` — `discoveredToolNames` 필터링, `filteredTools` 조립규칙(비deferred=항상/ToolSearch자신=항상/deferred+미발견=제외/deferred+발견=defer_loading:true), 베타헤더(1P/Foundry=advanced-tool-use, Vertex/Bedrock=tool-search-tool) :1174-1182.
  - `src/utils/api.ts:100-224` — `toolToAPISchema`, 세션안정 base schema 캐시(`cacheKey`, GrowthBook flip 방지 주석), `defer_loading` 필드부여 :223-224.
- **Chain7 산출물**: `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`(§00 큰그림~§06 실측+검증이력, §08 추가Q&A 삽입 — 완전성 미확인), `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html`(폐가식서고+대출시스템 메타포, 웜다크아카데미아 세피아+황동, Gowun Batang/Gothic A1/IBM Plex Mono, 01~06 + 07추가Q&A — 완전성 미확인, 마지막 `open` 결과 미확인).
- **Chain8(미해결) 조사 좌표**: `src/query.ts:1564-1566,1619-1621`; `src/tasks/LocalMainSessionTask.ts:262`(`enqueuePendingNotification({mode:'task-notification'})`); `src/utils/attachments.ts:760,829,1046`(`getQueuedCommandAttachments`); `src/utils/messageQueueManager.ts:128-135`(`enqueue`, priority `'next'`기본) vs `:142-149`(`enqueuePendingNotification`, priority `'later'`기본, "user input is never starved by system messages"), `:151-155`(`PRIORITY_ORDER` now=0/next=1/later=2); `src/utils/queueProcessor.ts:52`(`processQueueIfReady`, 아직 본문 미Read); `src/hooks/useQueueProcessor.ts`(전문 Read 완료 — `useSyncExternalStore`×2 구독, `useEffect` 자동트리거 조건 `!isQueryActive && !hasActiveLocalJsxUI && queueSnapshot.length>0`); `src/utils/processUserInput/processUserInput.ts:143`(isMeta 스케줄태스크 스킵 주석).
- **산출물 전체 목록(재작성 금지, 상태 최신화)**:
  - `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` — 완성.
  - `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` — 완성, 브라우저에 열림.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`(리네임됨, 구 `세션인풋-시스템프롬프트-도구-전문.md`는 더 이상 존재하지 않음) — 완성, src대조 검증 완료.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.html` — 완성, 브라우저에 열림.
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md` — §00~§06 완성 + §08 추가Q&A 삽입(완전성 미확인, 다음 세션 재검증 필요).
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html` — 01~06 완성 + 07 추가Q&A 삽입(완전성 미확인) + 재오픈 결과 미확인.
- **PostCompact 훅 관찰(정보성, 재검증 안 함)**: `~/.claude/scripts/cc-name.sh` → `hs -c bigAlert(...)`.

## 단계 2

Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:

### Current progress and key decisions made

- **Session goal (unchanged)**: 사용자가 `/Users/seobi/jinsup_space/CC` (Claude Code 내부를 리버스엔지니어링하는 리서치 레포: `md_group/` 분석 문서, `html_group_v2/` HTML 시각화, `src/` 재구성 소스)를 대상으로 세부 메커니즘을 하나씩 깊게 파고드는 세션. 이번이 4번째 컴팩션 사이클.

- **Chain 1 — 배치 병렬/파티셔닝 (완전 종결)**: `partitionToolCalls`가 `isConcurrencySafe` per-tool 선언만으로 병렬/단독 배치를 나눔(파일/인자 비교 없음). 산출물 `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` 완성, 재작성 금지. HTML 짝꿍은 미제작 대기.

- **Chain 2 — 컨텍스트 주입 4트랙 (완전 종결)**: 0번 유령 메시지(`prependUserContext`, 매 호출 재생성) vs skill_listing(정주민) vs conditional rules(우편함 패턴) vs frontmatter 4종(값싼 색인 상시·비싼 본문 트리거시). 산출물 `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` 완성, 재작성 불필요.

- **중간 이벤트 — 실제 Claude-Code 네이티브 `/compact`**: 세션 중 실제로 발생, PostCompact 훅(`~/.claude/scripts/cc-name.sh`)이 발동. 지금 시뮬레이션 중인 codex-레벨 압축과는 별개의 실사건이며 재론 불필요.

- **Chain 3 — UserPromptSubmit 훅 / `getHooksSection()` (완전 종결)**: `getHooksSection()`(`prompts.ts:127-129`)의 3문장은 `getSimpleSystemSection()`을 통해 무조건 시스템 프롬프트에 포함됨. 훅은 툴이 아니라 하네스가 `spawn`으로 직접 실행(`hooks.ts:7,977`). `<user-prompt-submit-hook>` 태그는 src 전체에서 `prompts.ts:128` 언급 1곳뿐이며 실제 렌더링 코드는 0곳 — 과거 버전 잔재로 추정(확정 불가). `getMcpInstructionsSection()`은 구형 `DANGEROUS_uncached`(매턴 재계산) vs 델타 모드(`mcp_instructions_delta`) 2종 배달방식 확인. 캐시 경계(`SYSTEM_PROMPT_DYNAMIC_BOUNDARY`, `api.ts:321-410`) 앞=글로벌캐시/뒤=세션조건부임을 소스 주석(`prompts.ts:371-372`)으로 확정.

- **Chain 4 — 세션 인풋 전문 스냅샷 문서화 (완료, 단 Chain 6에서 리네임됨)**: `/login` 직후 사용자 요청으로 현재 컨텍스트 윈도우 전체를 자기전사(self-transcription). Part1(system 13섹션)~Part4(대화히스토리+T1~T24)까지 작성 완료. 채집 중 라이브 사실 2건 발견: ① `userEmail`이 `/login` 전후 실제 변경(0번 유령 메시지 재생성 증거), ② 실서비스는 `# System`→`# Harness` 개편되며 `<user-prompt-submit-hook>` 언급이 삭제됨(Chain3 "잔재" 가설 방증).

- **Chain 5 — src vs 실서비스 diff 마킹 (이번 세그먼트에서 완전 종결)**: 직전 요약 시점에 미해결이던 "🔴 마커가 정확한 위치·판정으로 붙었는지" grep 결과를 확인·보고 완료. 검증 결과: `## 1-4`(모델정체성, 144행)·`## 2-2`(Artifact, 514행)·`## 2-7`(ReportFindings, 689행)·`## 2-8`(ScheduleWakeup, 708행)·`## 2-11`(Workflow, 800행)에 정확히 붙었고, `## 1-10`(Context management, 300행)은 🟡+🔴 혼합 표기가 올바름을 확인. 부록-2(도구 12종 대조표)와 문서머리 범례(6행)도 정합. 1509행에 걸린 별도 🔴는 마커가 아니라 Part4 대화이력에 기록된 과거 답변 원문의 이모지임을 정확히 구분해 오탐 아님을 설명 — 사용자 질문 "없는거 md에 잘적은거 맞지?"에 근거 제시하며 확답 완료. **Chain 5 CLOSED.**

- **Chain 6 — 파일명 변경 + HTML 짝꿍 (신규, 완결)**: 사용자가 "2027-07-11-시스템프롬프트및도구내용-최신본 이라구 이름바꿔주고 /visual-explainer 로 html버전도"라고 요청. 어시스턴트가 "2027"을 오늘 날짜(2026-07-11) 대비 오타로 판단해 **2026**으로 정정(사용자에게 정정 사실 명시, 진짜 2027 원했으면 재요청 안내)하고 `mv`로 `/Users/seobi/jinsup_space/CC/세션인풋-시스템프롬프트-도구-전문.md` → `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`로 리네임. 이어서 Skill `visual-explainer`로 `2026-07-11-시스템프롬프트및도구내용-최신본.html` 작성: **청사진(blueprint) 제도 도면 컨셉** — 네이비 그리드 배경+시안 선묘, 도면번호/검증방법 타이틀블록, 신규도구엔 회전 "SRC 無" 스탬프; 폰트 Do Hyeon+IBM Plex Sans KR+IBM Plex Mono; 01 적재구조(system↔messages 좌우 화물칸), 02 시스템13섹션(14행 판정색), 03 도구12종 카드그리드(신규4종 붉은점선+스탬프), 04 상주화물 6레인, 05 대시보드(분포바+경향칩+발견2건). 브라우저에 열림. 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동) 제안했으나 요청 없음 — 대기.

- **Chain 7 — ToolSearch 도구 지연로딩 시스템 완전 규명 (이번 세그먼트의 핵심, 대부분 완결 · 문서반영 일부 미확인)**:
  - 사용자 질문 "도구의 toolsSearch에 대한 로직을 상세히 알려줘"에 대해 src 전체(`ToolSearchTool.ts`, `prompt.ts`, `toolSearch.ts` 756줄, `api.ts`, `claude.ts`)를 추적해 **5단계 생애주기**로 규명:
    1. **분류** `isDeferredTool()`(prompt.ts:62-108) — `alwaysLoad:true` 최우선 opt-out → MCP도구 무조건 defer → ToolSearch 자신은 절대 defer 안 함 → FORK_SUBAGENT 실험시 Agent 예외 → Brief 통신채널 예외 → 나머지는 `shouldDefer:true`만.
    2. **모드 게이트** (toolSearch.ts:172-198,385-473) — `ENABLE_TOOL_SEARCH` 3모드: `tst`(기본, 항상defer) / `tst-auto`(토큰총량이 컨텍스트 N% 초과시만, 토큰카운팅API→char휴리스틱 폴백) / `standard`(구식 전부인라인). 추가 게이트: 킬스위치, 모델의 tool_reference 지원여부(haiku계열 미지원 기본패턴).
    3. **고지** `deferred_tools_delta`(toolSearch.ts:629-706) — 이미 고지한 이름 집합을 이력 스캔으로 재구성 후 차집합만 어태치먼트로 발행. "defer 풀렸지만 여전히 존재"는 removed로 보고 안 함(거짓방지, :641-644).
    4. **검색** `call()`(ToolSearchTool.ts:328-434) — A) `select:` 경로(콤마다중, 기로드도구 select해도 성공, 0건시 연결중서버 안내) B) 키워드 경로 3단폴백(exact-name fast path → mcp__프리픽스 → 스코어링). 스코어표: 이름조각정확 MCP12/일반10, 이름조각부분 MCP6/일반5, searchHint4, 설명문word-boundary2, fullname폴백3(0점때만). 여러단어 합산, `+term` 필수텀 지원.
    5. **로드/재조립**(claude.ts:1150-1187) — 검색결과는 `tool_reference` 블록으로 tool_result에 실림(텍스트 아님). 요청조립규칙: 비deferred=항상전송/ToolSearch자신=항상전송/deferred+미발견=tools배열에서 아예제외/deferred+발견=defer_loading:true로 전송. "발견" 판정은 별도상태 아니라 **대화이력 자체를 스캔**(`extractDiscoveredToolNames`, toolSearch.ts:545-592)해서 재구성 — 대화가 곧 영수증. compact_boundary 마커에 `preCompactDiscoveredTools`로 이월돼 compact를 넘어도 복원됨. 스키마 확장 자체는 API서버가 수행(베타헤더 필수).
  - 사용자 요청("md로도 만들어주고 /visual-explainer로도")에 따라 2종 산출물 작성: `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`(§00 큰그림~§06 실측+검증이력) 및 `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html`(**폐가식 서고+대출시스템 메타포**, 웜다크아카데미아 세피아+황동, Gowun Batang/Gothic A1/IBM Plex Mono, 01~06 섹션). 브라우저에 열림.
  - 이후 사용자가 **연쇄 재질문 9라운드**를 던졌고 매번 소스 재검증(attachments.ts:836-875,1440-1485 / ToolSearchTool.ts:194-198,266-291 / toolSearch.ts:606-706 / messageQueueManager.ts 등) 후 답변, 핵심 결론:
    - 카드 목록(`deferred_tools_delta`)은 **ToolSearch 호출과 무관** — 어태치먼트 파이프라인이 수집지점(턴시작+사이클꼬리)마다 "풀 변화 있을 때만" 발행(getDeferredToolsDelta, 차이없으면 null:677). 델타 4형제(deferred_tools_delta:836/agent_listing_delta:851/mcp_instructions_delta:854/skill_listing:875)가 같은 `maybe()` 목록에 등록.
    - 세션 첫 턴엔 "이미 고지 집합=0"이라 델타=전체 목록 → 사실상 첫 프롬프트와 함께 감(단, 프롬프트 "안"이 아니라 "옆"에 별도 isMeta 메시지로). compact 후도 동일 원리로 재발행 — **compact가 리프레시 역할**.
    - MCP 신규연결은 연결 즉시가 아니라 **다음 수집지점**에 삽입 — 유저가 대기중이면 엔터가 트리거(턴시작 수집), 모델이 작업중이면 사이클꼬리(query.ts:1569)에서 **엔터 없이 자동** 삽입. 이 세션에서 실측(figma/supabase/vercel 연결이 작업중 턴에 무입력으로 끼어듦; Atlassian/Gmail 등 61개 해제 공지는 유저 프롬프트 턴에 동반).
    - **로스트인더미들 문제**: 하네스 상태는 프로그램적 스캔이라 절대 안 잃음, 취약한 건 모델 attention. 4중 안전망 — ① ToolSearch 자신의 설명문은 tools배열에 매 요청 fresh하게 실림("표지판"은 안 묻힘) ② 키워드검색(암기 불필요) ③ bare-name fast path(주석: "seen from subagents/post-compaction" — 기억열화 실측 기반 방어선) ④ 실패시 명시적 "No matching" 반환→재시도유도. compact가 옛 고지를 쓸어내 prior=0을 만들어 전체 재발행되는 것도 방어선. **그러나 정직한 잔여 리스크**: "그런 도구가 있다는 발상 자체를 못 하는" unknown-unknowns 구간은 소스상 추가 재주입 장치 없음 — 표지판은 "검색법"만 알려주지 "뭘 검색할지"는 못 알려줌. 완화 요인(우연): 유저가 보통 단어를 직접 언급, MCP지침이 의미적 라우팅 힌트 제공, compact가 대개 그 지경 전에 옴.
    - **키워드검색 알고리즘 = BM25 아님** — TF/IDF/문서길이정규화 전부 없음, 필드가중치만 하드코딩(위 스코어표). "필드가중치를 손으로 박은 불리언매칭+합산정렬". 근거: 검색대상이 수백건 미니목록(코퍼스통계 무의미) + 쿼리작성자가 LLM이라 실패시 재시도(재시도루프의 두뇌=모델). 한국어/동의어는 매치 안 됨(임베딩 없음, 순수 어휘매칭) — "지라 이슈" 검색 실패 → "jira issue" 재시도로 극복하는 구조.
  - **세그먼트 마지막 턴**: 사용자가 "위에 추가된 내용 다 md와 html에 반영해줘 그리고 새로운질문\nReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?"로 **두 가지 지시를 동시에** 던짐 — (a) 상기 Q&A 전체를 두 산출물에 반영, (b) 신규 질문(비-ReAct 사이클 자동주입 예외). 어시스턴트는 (b)부터 src 검증 착수 → Chain 8로 이어짐.

- **Chain 8 — "비ReAct 사이클 시스템리마인더/어태치먼트 자동주입 예외" 질문 (신규, 미해결·진행 중, 다음 세션 최우선)**:
  - 검증 진행 상황: `query.ts:1564-1566`(서브에이전트는 자기주소 task-notification만 드레인), `:1619-1621`(prompt/task-notification→어태치먼트 변환); `tasks/LocalMainSessionTask.ts:262`(`enqueuePendingNotification({mode:'task-notification'})`); `attachments.ts:760,829,1046`(`getQueuedCommandAttachments`, `maybe('queued_commands',...)` 등록); `messageQueueManager.ts:128-135`(`enqueue()` — 유저입력용, 기본 priority `'next'`) vs `:142-149`(`enqueuePendingNotification()` — 태스크알림용, 기본 priority `'later'`, 주석: "user input is never starved by system messages"), `:151-155`(`PRIORITY_ORDER` now=0/next=1/later=2, 동순위 FIFO); `queueProcessor.ts:52`(`processQueueIfReady`); **`hooks/useQueueProcessor.ts` 전문 Read 완료** — `useSyncExternalStore`로 `queryGuard`+커맨드큐 구독, `useEffect`가 `!isQueryActive && !hasActiveLocalJsxUI && queueSnapshot.length>0` 조건 충족시 `processQueueIfReady`를 **자동 호출** — 이것이 유저 키입력이 아니라 **React state 변화 자체가 트리거**가 되어 엔터 없이 큐를 드레인하는 실제 메커니즘으로 보임(결론 도출 직전); `processUserInput.ts:143`("Skip for isMeta (system-generated prompts like scheduled tasks)" 주석).
  - **아직 사용자에게 답변 전달 안 됨.** `useQueueProcessor.ts`를 다 읽은 직후, 어시스턴트가 (a) 작업(md/html 반영)으로 전환해 Edit 4건 실행: `toolsearch-생애주기-소스분석.md`에 "§08 추가 Q&A 보강" 섹션 삽입 + 검증이력 라인 갱신, `toolsearch-생애주기-소스분석.html`에 헤딩 "07" 참조 추가 + "07 추가 Q&A — 타이밍 · 망각 · 알고리즘" 섹션 삽입, 이어서 `open`으로 HTML 재오픈 Bash 호출을 실행 — **이 Bash 호출의 완료/출력이 트랜스크립트에서 확인되기 전에 세그먼트가 끝남.**
  - **(a) 반영 완전성도 미확인**: Edit 인자 문자열이 트랜스크립트 표시상 중간에 잘려(...) 있어, 삽입된 "§08/07 추가 Q&A" 섹션이 세그먼트에서 논의된 9라운드 전부(카드목록타이밍/첫프롬프트포함여부/MCP추가삽입시나리오/로스트인더미들4중안전망/흐름1~3설명/키워드검색다중단어/BM25비교표/필드가중치재정리/엔터vs자동케이스A·B)를 담았는지, 섹션 제목이 시사하는 3토픽(타이밍·망각·알고리즘)만 담았는지 불명.

### Important context, constraints, and user preferences
- 대상 레포: `/Users/seobi/jinsup_space/CC` (현재 `research` 레포와는 별개, `research/notebooks/claude_code`의 GPT-하네스 규약 미적용).
- 사용자 전역 선호(개인 지침, 전 프로젝트 공통): 탐색/분석은 `Explore`, 플래닝은 `Plan` 서브에이전트에 위임하고 실행은 메인에서 직접; 결정/선택 필요시 `AskUserQuestion` 사용, prose로 풀어 묻지 않기.
- 레포 고유 규약(전 세그먼트 통틀어 계속 준수):
  - Claude Code 내부에 대한 모든 비자명한 주장은 `~/jinsup_space/CC/src`를 직접 `grep`/`Read`로 검증. "확인 못함(⚪)" 라벨을 정직하게 씀.
  - 루트 `.md` 문서는 관례상 `html_group_v2/`에 짝꿍 HTML을 두지만, 이번 세션의 신규 산출물(Chain6/7)들은 모두 레포 루트에 md+html 페어로 위치 — `html_group_v2/`로의 정식 이동은 아직 안 됨(재요청시에만).
  - 문서 내 경로는 `~`-상대/중립 표기가 기본이나, Chain4/6 세션인풋 문서는 "일회성 스냅샷" 예외로 기계 절대경로 유지(문서 자체에 명기됨).
  - 새 분석 문서는 기존 톤/구조(번호 섹션, file:line 근거, 마무리 검증 로그)를 따름.
- 사용자의 질문 스타일: 좁은 메커니즘 하나를 재질문으로 계속 파고드는 패턴이 세션 내내 이어짐. 이해가 막히면("아니 저게 그러면...", "좀쉽게말해봐 플로우 위주로;;;") **더 구체적인 시나리오/표/플로우로 재설명**을 요구 — 추상적 재설명 대신 실제 벌어지는 순서를 단계별로 실연해야 통과됨. 이번 세그먼트(Chain7)에서 특히 뚜렷 — 9라운드 연쇄 재질문 전부 이 패턴.
- **행동 시그널(계속 유효, 이번 세그먼트에도 재확인)**: 어시스턴트가 사용자의 리터럴하고 구체적인 질문 대신 더 일반적/인접한 버전으로 답하면 사용자가 즉시 날카롭게 지적함(예: "1번 무슨말인지 모르겠네.. tools에는 검색될 도구 목록은 안들어가잖니" — 어시스턴트가 즉시 정정·사과 없이 담백하게 재설명).
- **자기검증(self-verification) 습관**: Chain5에서 어시스턴트 자신이 작성한 문서의 정확성 재확인 요구에 grep으로 근거 제시하며 확답 — 이 패턴이 이번 세그먼트에서 완결됨. 도구 출력(자체 검증 스크립트의 "inserted:0" 오탐 등)을 맹신하지 않고 실물로 재확인하는 습관 유지.
- **신규 — 복수요청 처리 패턴**: 사용자가 한 메시지에 "기존 작업 반영 + 새 질문"을 동시에 던지는 경우(Chain7 마지막 턴) 발생 — 어시스턴트는 새 질문의 소스검증을 먼저 시작했으나, 두 지시 모두 완결하지 못한 채(문서반영도 완전성 미확인, 새질문 답변도 미전달) 세그먼트가 끝남. 다음 세션은 **두 가지 모두**를 사용자에게 명시적으로 완결·보고해야 함.
- **신규 — 날짜/파일명 오타 정정 관행**: 사용자가 "2027-07-11"이라 썼을 때 어시스턴트가 오늘 날짜(2026-07-11) 기준 오타로 판단해 자체 정정하고 그 사실을 사용자에게 고지 — 확답은 아직 못 받음(사용자가 정말 2027을 원했을 가능성 낮지만 이론상 열려있음).
- 모든 응답은 한국어(세션 초반부터의 지속 제약).

### What remains to be done (next steps)
1. **최우선**: Chain 8 — 사용자의 신규 질문 "ReAct 사이클이 아닌 경우는 다 엔터쳐야 시스템리마인더/어태치먼트가 올라가는가, 예외는 있나?"에 확답. 조사는 거의 끝난 상태 — 유력 결론 후보는 "`useQueueProcessor.ts`의 React `useEffect`가 (쿼리비활성 && JSX UI 안막힘 && 큐에 항목있음) 조건에서 유저 키입력과 무관하게 자동으로 `processQueueIfReady`를 호출하며, `enqueuePendingNotification`(priority `'later'`)로 들어온 task-notification류가 이 경로로 엔터 없이 드레인된다"는 것. 필요시 `queueProcessor.ts:52` 이하 `processQueueIfReady` 본문과 `getQueuedCommandAttachments`(attachments.ts:1046~)를 추가로 Read해 마무리 확인 후, 표/플로우 형식(사용자 선호 패턴)으로 답변할 것.
2. Chain 7 (a) 반영 완전성 재확인 — `toolsearch-생애주기-소스분석.md`의 "§08 추가 Q&A 보강" 섹션과 `.html`의 "07 추가 Q&A" 섹션이 세그먼트에서 논의된 9라운드 전부를 담았는지 grep/Read로 재확인, 누락 있으면 Edit로 보강.
3. `open` Bash 호출(HTML 재오픈)의 완료 여부 확인 — 실패했다면 재실행.
4. Chain 1~6은 전부 완료·전달됨, 재론 불필요.
5. 낮은 우선순위, 재요청 시에만: `배치-단독-개념-소스증명.md` HTML 짝꿍(미제작); `2026-07-11-시스템프롬프트및도구내용-최신본.html`의 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동).

### Critical data / references needed to continue
- 레포 루트: `/Users/seobi/jinsup_space/CC`; 문서 `md_group/`, HTML 미러 `html_group_v2/`, 재구성 소스 `src/`.
- **Chain1~4 근거 요약(재검증 없이 인용 가능, 상세 file:line은 이전 요약본에 전량 보존)**: 배치파티셔닝 `toolOrchestration.ts:95-116`(partitionToolCalls) 등; 컨텍스트4트랙 `api.ts:449-474`(prependUserContext), `context.ts:155-189`(getUserContext) 등; UserPromptSubmit훅 `hooks.ts:7,977`(spawn 실행주체), `prompts.ts:127-129`(getHooksSection 원문, src 유일언급 `:128`) 등; MCP지시 `prompts.ts:160-165`(getMcpInstructionsSection); 캐시경계 `api.ts:321-410`(splitSysPromptPrefix, SYSTEM_PROMPT_DYNAMIC_BOUNDARY), `prompts.ts:371-372`(post-boundary 이유 주석).
- **Chain5 완결 근거**: `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`(구 `세션인풋-시스템프롬프트-도구-전문.md`) 내 마커 위치 — `## 1-4`(144행)·`## 2-2`(514)·`## 2-7`(689)·`## 2-8`(708)·`## 2-11`(800)·`## 1-10`(300, 혼합) 전부 정확 확인됨, 부록-2·범례(6행)도 정합, 1509행 건은 오탐 아님(Part4 대화이력 원문의 이모지).
- **Chain6 산출물**: `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`, `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.html`(청사진 제도도면 컨셉, Do Hyeon+IBM Plex Sans KR+IBM Plex Mono).
- **Chain7 ToolSearch 핵심 소스 좌표**:
  - `src/tools/ToolSearchTool/ToolSearchTool.ts`(472줄) — `call()` :328-434, `select:`경로 :363-406, 스코어링 `searchToolsWithKeywords` :186-302, 이름파싱 :132-161, `+term`필수텀 :236-257, 스코어표 :266-291.
  - `src/tools/ToolSearchTool/prompt.ts` — `isDeferredTool()` :62-108(alwaysLoad>MCP>ToolSearch자신>FORK_SUBAGENT>Brief>shouldDefer 순서), PROMPT_HEAD/TAIL 쿼리형식안내 :35-42("Deferred tools appear by name in system-reminder messages"), name+hint A/B실험 폐기 :110-117.
  - `src/utils/toolSearch.ts`(756줄) — `getAutoToolSearchTokenThreshold` :104, `getAutoToolSearchCharThreshold` :115, `getDeferredToolTokenCount` memoize :124-152, `isToolSearchEnabled` :385+, `extractDiscoveredToolNames` :545-592(대화이력 스캔으로 발견집합 재구성, compact_boundary의 `preCompactDiscoveredTools` 이월 :553-558), `isDeferredToolsDeltaEnabled` :629, `getDeferredToolsDelta` :646-706(차이없으면 null :677), compact_full 텔레메트리 주석 "prior=0 is EXPECTED" :606-608.
  - `src/utils/attachments.ts` — `getDeferredToolsDeltaAttachment` :1454-1475(4게이트: 델타모드on/tool search optimistic on/모델 tool_reference지원/ToolSearch도구 available), `maybe()` 등록순서 `deferred_tools_delta`:836/`agent_listing_delta`:851/`mcp_instructions_delta`:854/`skill_listing`:875, 렌더링 `messages.ts:4178-4193`.
  - `src/services/api/claude.ts:1150-1187` — `discoveredToolNames` 필터링, `filteredTools` 조립규칙(비deferred=항상/ToolSearch자신=항상/deferred+미발견=제외/deferred+발견=defer_loading:true), 베타헤더(1P/Foundry=advanced-tool-use, Vertex/Bedrock=tool-search-tool) :1174-1182.
  - `src/utils/api.ts:100-224` — `toolToAPISchema`, 세션안정 base schema 캐시(`cacheKey`, GrowthBook flip 방지 주석), `defer_loading` 필드부여 :223-224.
- **Chain7 산출물**: `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`(§00 큰그림~§06 실측+검증이력, §08 추가Q&A 삽입 — 완전성 미확인), `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html`(폐가식서고+대출시스템 메타포, 웜다크아카데미아 세피아+황동, Gowun Batang/Gothic A1/IBM Plex Mono, 01~06 + 07추가Q&A — 완전성 미확인, 마지막 `open` 결과 미확인).
- **Chain8(미해결) 조사 좌표**: `src/query.ts:1564-1566,1619-1621`; `src/tasks/LocalMainSessionTask.ts:262`(`enqueuePendingNotification({mode:'task-notification'})`); `src/utils/attachments.ts:760,829,1046`(`getQueuedCommandAttachments`); `src/utils/messageQueueManager.ts:128-135`(`enqueue`, priority `'next'`기본) vs `:142-149`(`enqueuePendingNotification`, priority `'later'`기본, "user input is never starved by system messages"), `:151-155`(`PRIORITY_ORDER` now=0/next=1/later=2); `src/utils/queueProcessor.ts:52`(`processQueueIfReady`, 아직 본문 미Read); `src/hooks/useQueueProcessor.ts`(전문 Read 완료 — `useSyncExternalStore`×2 구독, `useEffect` 자동트리거 조건 `!isQueryActive && !hasActiveLocalJsxUI && queueSnapshot.length>0`); `src/utils/processUserInput/processUserInput.ts:143`(isMeta 스케줄태스크 스킵 주석).
- **산출물 전체 목록(재작성 금지, 상태 최신화)**:
  - `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` — 완성.
  - `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` — 완성, 브라우저에 열림.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`(리네임됨, 구 `세션인풋-시스템프롬프트-도구-전문.md`는 더 이상 존재하지 않음) — 완성, src대조 검증 완료.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.html` — 완성, 브라우저에 열림.
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md` — §00~§06 완성 + §08 추가Q&A 삽입(완전성 미확인, 다음 세션 재검증 필요).
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.html` — 01~06 완성 + 07 추가Q&A 삽입(완전성 미확인) + 재오픈 결과 미확인.
- **PostCompact 훅 관찰(정보성, 재검증 안 함)**: `~/.claude/scripts/cc-name.sh` → `hs -c bigAlert(...)`.
