## 단계 2

<summary>

1. Primary Request and Intent:
   - **세션 대주제(누적)**: `/Users/seobi/jinsup_space/CC`(Claude Code 내부를 소스코드로 역공학하는 리서치 프로젝트) 전체 파악. 배치 파티셔닝 → 컨텍스트 주입 4트랙 → 훅/MCP지시/캐시경계 → ToolSearch 지연로딩 → 큐 웨이크 → XML vs 마크다운 → 0번 유령메시지·CLAUDE.md 캐싱·스킬목록 타이밍 → system-reminder 태그 전수조사(완료) → ReAct 사이클 전용 SR/비SR 지도(완료) → 스킬 lost-in-the-middle 대처 규명(완료, 구두) → 기술부채 전수 스캔(완료, md+html+json) → Coordinator Mode/수퍼바이저 패턴(완료) → **(round6 종료 시 미완이던 마지막 요청, 이번 구간 첫머리에서 완료)** "임베딩검색/BM25/의도분류/고정워크플로우 4개 없는거 맞나 + 유명한데 없는 기술 더" 검증 → **Reflexion 용어 구분(완료)** → **verification 에이전트 빌트인 여부(완료)** → **(맥락불명 메시지, 미응답)** → **메인루프 밖 별도 LLM 호출 전수(11곳→오답 정정→16곳 확정, md+html 산출 완료)** → **LLM 호출 vs 진짜 에이전트 3분류(완료)** → **TaskCreate/TodoV2 컨텍스트 주입 3경로 + task_reminder 정확 트리거 조건(완료, 3회 정정 왕복)**으로 이어지는 연쇄 딥다이브. 전 구간 "주장은 grep/Read로 소스 검증" 규율 일관 적용.
   - **(round6 종료 시 미완, 이번 구간 첫머리 완료)**: "임베딩 검색 없음/BM25 없음/의도 분류 없음/고정된 에이전트 워크플로우 없음 — 클로드코드에 위 4개 없는거 맞아? 그리고 유명 기술이지만 없는거 또 뭐가있지?" → grep 오탐 검증(getEmbeddingLevels·소스맵base64·pipeline주석 등 전부 오탐 확인) 후 4개 전부 "없음" 확정 + 확장 목록(RAG·요약메모리버퍼·Reflexion·플래너실행자분리·동적few-shot·출력파서·세만틱캐싱·DSPy식최적화) 8종 제시, "코드로 만든 보조지능 계층을 걷어내고 모델에 위임" 철학으로 정리 — **완료**.
   - **Reflexion 재질문**(완료): "Reflexion 이 없다는게 무슨말이지" → 학술 프레임워크(Actor→Evaluator→Self-Reflection→에피소드메모리 축적→재시도 주입) 정의 vs 클로드코드의 verification에이전트/FAIL재시도/모델자기수정/auto-memory 비교표로 "성찰 능력은 있으나 성찰-누적-되먹임 코드화 아키텍처는 없다"로 정확화.
   - **verification 에이전트 빌트인 질문**(완료): "verification 에이전트 이게 빌트인으로 있어?" → `builtInAgents.ts:65-68` grep/Read로 이중게이트(`feature('VERIFICATION_AGENT')` 빌드플래그 + `tengu_hive_evidence` GrowthBook 기본값 false) 확인, 일반 유저에겐 `subagent_type="verification"` 목록에 없음 확정. 넛지 강제 문구(TodoWriteTool.ts:107/TaskUpdateTool.ts:397) 발견.
   - **(맥락 불명, 이번 구간 이상 메시지, 미응답)**: "ngClearLatched를 세션 고정 래치로 관리..." 로 시작하는 사용자 발화(apiMicrocompact.ts:79-88, claude.ts:1469-1470, effort.ts:303-305 언급) — 어시스턴트 응답이나 도구호출 없이 바로 다음 새 주제 질문으로 전환됨. 원문 그대로 보존(6절 참조), 내용의 출처/의도는 대화 내에서 확인 불가.
   - **별도 LLM 호출 지점 질문**(완료, 3회 정정 왕복): "에이전트 도구 쓰는거말고 LLM 을 별도로쓰는게 요약이랑 bash 툴에서 권한검증 말고 또언제가있지?" → `queryHaiku` 소비처 8~9곳 답변("11곳") → 사용자 "총 11곳이 끝이야?" 반문 → 저수준 함수(`queryModelWithoutStreaming`/`queryModelWithStreaming`/`queryWithModel`) 우회 경로 재조사, "11곳은 오답, 실제 최소 20곳 안팎"으로 자가정정 → 사용자 "LLM 쓰는곳 그럼 총정리해봐... 한곳이라도 놓치지마" → 4개 진입함수 전수 grep으로 **본류 1(query/deps.ts 메인루프) + 사이드 16곳** 최종 확정 — **완료**.
   - **md+모델정보 문서화 요청**(완료): "위 내용들 다 하나의 md로 적어주고 어떤 모델호출하는지도 각각 적어라" → 각 호출부의 실제 `model` 파라미터를 소스로 역추적(getSmallFastModel/mainLoopModel/getDefaultOpusModel/변수 등) 후 `클로드코드-LLM-별도호출-전수.md` 신규 Write(§00~§05).
   - **html 시각화 요청**(완료): "/visual-explainer로 시각화해줘" → `클로드코드-LLM-별도호출-전수.html` 신규 Write("LLM 호출 지도 — 값싼 잡무 vs 비싼 판단" 컨셉) + `open`.
   - **에이전트 여부 재확인 질문**(완료): "근데 LLM 호출들 다 에이전트는 아니고 그냥 도구없는 LLM이지?" → 각 호출부의 `tools:[]`/`mcpTools:[]`/`toolChoice:undefined` grep 확인, WebSearchTool만 `toolChoice:{type:'tool',name:'web_search'}` 강제하는 예외로 확인 → "도구보유×루프여부" 2축 3분류(순수LLM/도구1개강제/진짜에이전트)로 정리.
   - **TaskCreate 컨텍스트 주입 질문**(완료, 3회 정정 왕복): "TaskCreate가 웹 UI에 표시되는데 LLM 입장에선 현재 태스크가 어떻게 컨텍스트 주입되나?" → tool_result/task_reminder/TaskList 3경로 규명 → 사용자 "몇 턴마다 반복 재주입하는거지?" 반문 → "무조건 N턴마다"가 아니라 "**태스크 도구를 10턴 방치했을 때만**"으로 정정(`TODO_REMINDER_CONFIG`, `getTodoReminderTurnCounts`) → 사용자 "그 도구라는건 아무도구? Task기준 도구?" 재확인 → 카운터가 `block.name === 'TodoWrite'`만 세고 Bash/Read/Edit 등 일반도구는 무관함을 확정 → 사용자 "TodoUpdate 하는건 컨텍스트보고 판단해서 툴콜링하는거야?" → "그렇다, 강제 트리거 없이 모델 자율판단 + 넛지 3겹(설명문규약/방치리마인더/완료후유도)"로 최종 정리 — **완료**.
   - **(세션 내부 이벤트, 이번 구간 마지막 줄)** `/compact` — 실제 Claude Code 컴팩션 재발동, 유저의 실질 질문 아님. 이 라인에서 세그먼트 종료.
   - **불변 제약(전체 세션 유지)**: 항상 한국어 응답. 모든 주장은 grep/Read 소스 검증 후 답변(프로젝트 CLAUDE.md 지침). 추측·과장 금지, 미확인은 "소스에서 확인 못함"·"정직 표기"로 명시. 오답은 즉시 자가정정.

2. Key Technical Concepts:
   - **(pre-round6, 완전 규명 완료 — 압축 유지)**: 배치 파티셔닝(safe/unsafe 병합) · 0번 유령 vs 델타 어태치먼트 4형제(skill/deferred/agent/mcp) · rules 지연주입 · 수집(+)/전처리(−) 구간분리 · frontmatter 2단구조 · 훅=하네스실행 · MCP지시 2배달모드 · `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 캐시경계 · ToolSearch 5단계 생애주기(BM25 아닌 필드가중치) · 큐 웨이크 6경로 · MD vs XML 분업 · 0번 유령메시지 캐싱(memoize, "stale wins") · 스킬목록 발행 타이밍(`sentSkillNames`) · system-reminder 태그 전수지도(메시지레벨 어태치먼트+인라인+선포장+직조립, "SR은 모델전용 채널") · 택배 비유(공장일괄포장/책귀퉁이경고문/미리싸서우체통/그자리조립) · ReAct 사이클 전용 SR·비SR 통합 타임라인(전처리개조→유령재인쇄→모델응답→도구실행[tool_result+인라인SR★+isMeta비SR]→사이클꼬리) · 스킬 lost-in-the-middle 3시나리오(신규세션 무해/resume 무해/동일세션compact 위험, "소극적 3종 방어선"+`EXPERIMENTAL_SKILL_SEARCH` 매턴 관련스킬 재주입 발견) · 기술부채 전수287건(9카테고리, "이자율이 계량된 빚", 상환회피 3패턴) · Coordinator Mode 2층위(암묵적상시 vs 기능플래그게이트) + Swarm/Team인프라 + **공통하네스 확정**(`runAgent.ts`엔 `isCoordinatorMode` 분기 없음, 워커=일반 서브에이전트와 동일 경로).

   **"클로드코드에 없는 유명 LLM기술" 검증 완료 목록 (이번 구간 신규)**
   - 확정 없음 4종: 임베딩/벡터검색(grep 히트 전부 오탐: `getEmbeddingLevels` 유니코드양방향/소스맵base64/`StagePipeline` UI컴포넌트명) · BM25/tf-idf(ToolSearch=필드가중불리언, 히스토리검색=fuzzy부분매칭) · 의도분류(**grep 0건**) · 고정 에이전트 워크플로우(LangGraph류 상태그래프 없음, `queryLoop` while문 하나가 전부).
   - 관통 철학: "검색? 모델이 grep쿼리 짬 / 라우팅? 모델이 스스로 도구·스킬 선택 / 오케스트레이션? ReAct루프" = **전처리를 모델에게 위임**.
   - 확장 확인(부분검증, "확인 못한 구석 있을 수 있음" 표기): RAG파이프라인 없음 · 대화요약메모리버퍼 없음(compact가 임계초과시 1회 요약교체뿐) · Reflexion형 성찰-누적 루프 없음(아래 상술) · 플래너-실행자 강제분리 없음 · 동적few-shot선택 없음(정적예제만) · 토큰레벨가드레일/출력파서 없음(zod는 입력검증용) · 세만틱캐싱 없음(프롬프트프리픽스 바이트단위 정확일치캐시만) · 멀티암드밴딧/DSPy식최적화 없음(프롬프트 수동튜닝, GrowthBook은 A/B일 뿐 자동최적화 아님).

   **Reflexion 정확한 의미 구분 (이번 구간 신규)**
   - Reflexion(2023 논문) = Actor→Evaluator→Self-Reflection(왜 실패했나 언어화)→에피소드메모리 저장→재시도 시 주입, "실패할수록 똑똑해지는" 코드화된 성찰-누적-되먹임 기계장치. 이게 하네스 소스엔 없음.
   - 클로드코드엔 "성찰하는 능력"은 있음(verification에이전트의 1회성 판정, FAIL시 재시도, 모델의 내재적 자기수정, auto-memory)이나, **강제 성찰+메모리축적+되먹임 루프로 코드화된 아키텍처**는 없음. 왜(추론): Reflexion은 약한모델 보강기법인데 클로드코드는 프런티어모델 자기수정력을 전제하므로 그 스캐폴딩 자체가 불필요.

   **verification 에이전트 — 빌트인이지만 이중잠금 (이번 구간 신규)**
   - `tools/AgentTool/built-in/verificationAgent.ts:134`에 `VERIFICATION_AGENT` 정의 존재하나, `builtInAgents.ts:65-68` 조건 — ①`feature('VERIFICATION_AGENT')`(빌드플래그, 외부배포시 DCE 가능) ②`getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)`(GrowthBook 원격, **기본값 false**) — 둘 다 통과해야 에이전트 목록에 등록. 일반 유저는 `subagent_type="verification"` 자체가 없음. `VERIFICATION_AGENT_TYPE='verification'`(constants.ts:4).
   - 게이트 열리면 회피 못 하게 강제 넛지: TodoWriteTool.ts:107 / TaskUpdateTool.ts:397 동일 조건 — "You just closed out 3+ tasks and none of them was a verification step... You cannot self-assign PARTIAL by listing caveats in your summary — only the verifier issues a verdict." coordinatorMode.ts:222,289에도 "fresh 눈으로 검증하라" 지침 병존.
   - 이건 유저/플러그인 레벨 검증(js-super:code-reviewer, verifying-spec 스킬)과는 별개 — 이쪽은 하네스 빌트인(사내실험), 저쪽은 유저가 까는 스킬·서브에이전트.

   **메인루프 밖 별도 LLM 호출 — 전수 16곳 확정 (이번 구간 신규, 핵심)**
   - 진입 함수 4종: `queryHaiku`(모델 고정 `getSmallFastModel()`) / `queryModelWithoutStreaming` / `queryModelWithStreaming` / `queryWithModel`(JSON출력, 모델은 호출부가 지정).
   - "11곳"은 `queryHaiku` 래퍼만 본 부분집합이라는 사용자 반문에 오답으로 확정 → 저수준 3함수 직접소비 재조사로 정정.
   - **최종 전수 = 본류 1 + 사이드 16 (insights 3회 포함시 18회)**:
     - A. `queryHaiku`(haiku 고정) 8곳: WebFetchTool웹요약 · sessionTitle세션제목 · generateSessionName(/rename) · toolUseSummaryGenerator(도구요약) · shell/prefix.ts(셸접두사분석) · mcp/dateTimeParser.ts(자연어날짜파싱) · teleport.tsx(원격세션이관) · Feedback.tsx(피드백)
     - B. `queryModelWithoutStreaming` 5곳: awaySummary.ts(자리비움요약, haiku) · skillImprovement.ts(스킬자동개선, haiku) · generateAgent.ts(커스텀에이전트생성, 모델=호출자가 지정하는 변수) · apiQueryHookHelper.ts(프롬프트훅, `config.getModel(context)` 변수) · execPromptHook.ts(프롬프트훅쌍, `hook.model`)
     - C. `queryModelWithStreaming` 2곳(본류 query/deps.ts 제외): WebSearchTool.ts(조건부 haiku↔mainLoopModel 토글) · services/compact/compact.ts(**autocompact, `context.options.mainLoopModel` = 메인모델, haiku 아님**)
     - D. `queryWithModel` 1곳·3회: commands/insights.ts(`getAnalysisModel()`/`getInsightsModel()` 둘 다 `getDefaultOpusModel()` **opus 고정**, 주석 "Opus - best quality")
   - 모델별 원가배분: 🟢haiku(10곳+, 값싼잡무) / 🔵가변(3곳, 유저·훅이 모델지정) / 🟡조건부(1곳, 웹검색 haiku토글) / 🔴큰모델(2곳, **autocompact=메인모델**·**insights=opus고정** — 요약/분석 품질이 결과를 좌우하는 곳만 비싼모델). 명확한 원가배분 원칙: "값싼 잡무는 haiku, 품질 중요한 것만 큰 모델".
   - 개념상 별도(호출함수는 위와 공유): Agent툴 서브에이전트(Explore/Plan/general-purpose/verification/worker) · 에이전트 진행 요약(`startAgentSummarization`, AgentTool.tsx:750~) · bash 권한 분류(BASH_CLASSIFIER).

   **LLM 호출 vs 진짜 에이전트 3분류 (이번 구간 신규)**
   - grep 확인: 대부분 `tools:[]`/`mcpTools:[]`/`toolChoice:undefined` 명시(awaySummary/skillImprovement/generateAgent/sessionTitle/dateTimeParser/WebFetch), skillImprovement는 `useTools:false`까지.
   - 예외: WebSearchTool.ts:280 `toolChoice: useHaiku ? { type:'tool', name:'web_search' } : undefined` — 도구 1개 강제.
   - 3분류: ①도구없는 순수 LLM(텍스트→텍스트, 대다수 14곳 — 에이전트 아님, 프롬프트 1회완성) ②도구1개 강제(웹검색 — 애매, 루프는 없음) ③진짜 에이전트(도구풀+ReAct루프, Agent툴 서브에이전트뿐). 판별기준 2축: 도구보유 여부 × 여러턴 루프(ReAct) 여부.

   **TaskCreate/TodoV2 — 컨텍스트 주입 3경로 + task_reminder 정확 트리거 (이번 구간 신규)**
   - 구조: `createTask()`(tasks.ts) 저장 상태를 웹UI와 LLM이 **독립적으로 구독**(UI가 LLM에게 알려주는 게 아님).
   - LLM 주입 3경로: ①생성/갱신 즉시 tool_result(TaskCreateTool.ts:121-128 `{task:{id,subject}}`, TaskUpdateTool.ts `"Updated task #N ..."`) ②주기적 `task_reminder` system-reminder 재주입(messages.ts:3680-3699, 델타 어태치먼트 패밀리 일원) ③능동조회 TaskList/TaskGet(완료 후 "Call TaskList now to find your next available task" 유도).
   - task_reminder 정확한 발동 조건(1차 정정): "N턴마다 무조건"이 아니라 **"태스크 도구를 방치했을 때만"**. `TODO_REMINDER_CONFIG`(attachments.ts:254-257) = `{TURNS_SINCE_WRITE:10, TURNS_BETWEEN_REMINDERS:10}`, `getTodoReminderTurnCounts`(attachments.ts:3212~)가 backwards 순회로 두 카운터를 세고 **둘 다 10턴 이상**일 때만 발행. 문구 자체가 "haven't been used recently"인 방치감지형 넛지.
   - 2차 정정(카운터가 세는 대상): `block.name === 'TodoWrite'`인 tool_use만 카운트, **Bash/Read/Edit 등 일반도구는 카운터 무관**. 즉 "코드 작업은 열심히 하는데 태스크 추적만 깜빡한" 정확한 순간을 잡기 위한 설계.
   - TaskUpdate 호출 자체는 자동트리거 없는 **평범한 도구**, 모델이 컨텍스트(자기 이력+tool_result+task_reminder) 보고 자율판단. 하네스는 강제 대신 넛지 3겹만 제공: ①도구 설명문 규약(시작=in_progress, 끝=completed) ②task_reminder 방치넛지 ③완료 후 연쇄유도("Call TaskList..." — `isAgentSwarmsEnabled()` 조건부, 단일세션엔 안 뜰 수 있음) + 검증넛지(3개+완료시 verification 유도).
   - TodoWrite(구형, `todo_reminder`, messages.ts:3663) vs TaskCreate/Update/List(신형 "TodoV2", `task_reminder`, `isTodoV2Enabled()` 게이트, id·status·blocks/blockedBy 의존성, 웹UI표시·스웜배분은 이쪽) 구분 확정.

3. Files and Code Sections:
   - **(pre-round6 소스, 완전 인용 완료 — 변경 없음, 목록만 유지)**: `toolOrchestration.ts`/`Tool.ts:750-765`/`FileReadTool.ts:373,706-707,730,887,942,1013`/`GrepTool.ts:183`/`query.ts:820-824,1205-1225,1300-1325`/`api.ts:444-474`/`context.ts:1-40,155-189`/`attachments.ts:875,2607-2751`/`messages.ts:3663-3800,4090-4231`/`claudemd.ts`/`SkillTool.ts`/`AgentTool/loadAgentsDir.ts`/`processUserInput.ts`/`utils/hooks.ts:225-245,938-981`/`constants/prompts.ts`/`ToolSearchTool.ts`/`utils/toolSearch.ts`/`services/api/claude.ts:1150-1250` · `messageQueueManager.ts`/`useQueueProcessor.ts`/`task/framework.ts`/`textInputTypes.ts`/`RemoteAgentTask.tsx`/`LocalShellTask.tsx`/`processSlashCommand.tsx`/`print.ts`/`constants/xml.ts`/`constants/common.ts`/`compact/compact.ts:63,117,203,518-535,922`/`postCompactCleanup.ts`/`runAgent.ts:381`/`memoryAge.ts`/`sideQuestion.ts:61`/`brief.ts`/`transcriptSearch.ts`/`queryHelpers.ts` · `coordinatorMode.ts`(전문)/`tools.ts:281,293`/`main.tsx`/`AgentTool/AgentTool.tsx`/`AgentTool/runAgent.ts`(무분기 확인).
   - **(pre-round6 산출물 md/html/json, 완전 완료 — 변경 없음)**: `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html` · `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`/`.html`/`-전체287건.json`.
   - **`tools/AgentTool/built-in/verificationAgent.ts:134`** — `VERIFICATION_AGENT: BuiltInAgentDefinition` 정의부(이번 구간 신규 Read).
   - **`tools/AgentTool/builtInAgents.ts:60-68`** — 이번 구간 신규 확인, 전문:
     ```ts
     if (isNonSdkEntrypoint) {
       agents.push(CLAUDE_CODE_GUIDE_AGENT)
     }
     if (
       feature('VERIFICATION_AGENT') &&
       getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)
     ) {
       agents.push(VERIFICATION_AGENT)
     }
     ```
   - **`tools/AgentTool/constants.ts:4`** — `VERIFICATION_AGENT_TYPE = 'verification'`.
   - **`tools/TodoWriteTool/TodoWriteTool.ts:78-107`**, **`tools/TaskUpdateTool/TaskUpdateTool.ts:335-397`** — `feature('VERIFICATION_AGENT') && getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)` 동일조건 + 강제넛지 문구 전문 확인(이번 구간 신규).
   - **`services/api/claude.ts:709-771, 1017, 3241-3300`** — 이번 구간 신규 전수 Read. `queryModelWithoutStreaming`(:709)/`queryModelWithStreaming`(:752)/`queryModel`(:1017, 내부위임)/`queryHaiku`(:3241, `model: getSmallFastModel()` 고정)/`queryWithModel`(:3300, `systemPrompt`/`userPrompt`/`outputFormat` 받는 JSON전용).
   - **`utils/model/model.ts:36-38`** — `getSmallFastModel()` 전문: `return process.env.ANTHROPIC_SMALL_FAST_MODEL || getDefaultHaikuModel()`.
   - **`services/compact/compact.ts:593,982,1292-1313`** — `queryModelWithStreaming({...model: context.options.mainLoopModel...})`, autocompact가 haiku 아닌 메인모델 사용함을 이 3개 라인으로 확정(이번 구간 신규).
   - **`commands/insights.ts:41-48,883,1026,1577`** — `getAnalysisModel()`/`getInsightsModel()` 둘 다 `return getDefaultOpusModel()`, 주석 "Opus - best quality"; `queryWithModel` 호출 3곳(:883,1026,1577).
   - **`services/awaySummary.ts:41-55`**, **`utils/hooks/skillImprovement.ts:132,212-242`**, **`components/agents/generateAgent.ts:120-165`**, **`utils/hooks/apiQueryHookHelper.ts:37,82-85`**, **`utils/hooks/execPromptHook.ts:62`** — 각각 `queryModelWithoutStreaming` 호출부, model 파라미터 출처(대부분 `getSmallFastModel()`, generateAgent만 호출자 지정 변수 `model`, execPromptHook은 `hook.model`, apiQueryHookHelper는 `config.getModel(context)`) 이번 구간 신규 Read로 역추적 확정.
   - **`tools/WebSearchTool/WebSearchTool.ts:268-280`** — `toolChoice: useHaiku ? { type:'tool', name:'web_search' } : undefined`, `model: useHaiku ? getSmallFastModel() : context.options.mainLoopModel` (이번 구간 신규 확인, "도구1개 강제" 예외의 근거).
   - **CREATED: `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md`** — 이번 구간 신규 Write. §00 진입함수4종+기본모델 → §0x 본류1+사이드16(A haiku8/B without5/C streaming2/D withModel1·3회) → 모델별집계표(🟢🔵🟡🔴) → autocompact/insights 예외 스포트라이트 → 원가배분 저울. (파일 본문은 도구 결과에서 일부만 노출돼 전체 재현은 못 함, 구조는 어시스턴트 후속 설명으로 확인.)
   - **CREATED: `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.html`** — `/visual-explainer` 스킬로 Write. 컨셉 "LLM 호출 지도 — 값싼 잡무 vs 비싼 판단", Big Shoulders Display+Gothic A1+IBM Plex Mono, 다크청록/주황 대비. 섹션: Hero(모델5색범례) → 01진입함수4개카드 → 02본류vs사이드16칩그리드 → 03예외둘(autocompact·insights 스포트라이트) → 04저울(14vs2). `open`으로 브라우저 표시 확인.
   - **`utils/messages.ts:3663-3699`** — 이번 구간 신규 Read 전문. `case 'todo_reminder'`(:3663, 구형 TodoWrite 안내문 "The TodoWrite tool hasn't been used recently...")와 `case 'task_reminder'`(:3680, `isTodoV2Enabled()` 게이트, 신형 안내문 "The task tools haven't been used recently... consider using TaskCreate...TaskUpdate...") 두 케이스 전문 확인, 둘 다 `wrapMessagesInSystemReminder([createUserMessage({content:message, isMeta:true})])`로 감싸짐.
   - **`tools/TaskCreateTool/TaskCreateTool.ts:80-134`** — 이번 구간 신규 Read 전문. `createTask()` 호출 → `executeTaskCreatedHooks` 생성기 순회(blockingError 처리) → `context.setAppState`로 `expandedView:'tasks'` 자동전환(:116-119, 웹UI 자동펼침) → `return { data: { task: { id: taskId, subject } } }`(:121-128, tool_result로 즉시 되먹임).
   - **`tools/TaskUpdateTool/TaskUpdateTool.ts` (`mapToolResultToToolResultBlockParam`)** — 이번 구간 신규 Read. 실패시 `"Task #${taskId} not found"`(비-에러로 반환, sibling취소 방지 주석), 성공시 `"Updated task #${taskId} ${updatedFields.join(', ')}"` + 완료시(`statusChange?.to === 'completed'` && `isAgentSwarmsEnabled()`) 팀메이트용 리마인더 추가 분기.
   - **`utils/attachments.ts:254-257, 3212-3260`** — 이번 구간 신규 Read 전문. `TODO_REMINDER_CONFIG = {TURNS_SINCE_WRITE:10, TURNS_BETWEEN_REMINDERS:10}` 및 `getTodoReminderTurnCounts(messages)` — backwards 순회로 `lastTodoWriteIndex`/`lastReminderIndex` 탐색, `block.name === 'TodoWrite'`인 tool_use만 카운트리셋 대상(일반도구 무관 확정의 근거).

4. Errors and Fixes:
   - **(pre-round6, 압축 유지)**: 배치파티셔닝·훅설명·python카운터 정정 / "엔터없는경로 4개"→6개 확정 / XML논거①기각·재정렬 / CLAUDE.md 캐시 자가정정 / queued_command 래핑조건 정정 / 용어(인라인·선포장·직조립) 불친절 인정→택배비유 / 스킬목록 "대처없음" 과장 인정→3시나리오 재정리 / compact 후 스킬목록 재고지 "구버전정책 vs 실측 불일치" 발견→"현행배포판은 정책변경된 듯"으로 정정 / HTML CSS 오타(`--pink:#ff7 eb;`) 수정.
   - **(이번 구간) "별도 LLM 호출 11곳" 오답 정정**: `queryHaiku` 래퍼 소비처만 세고 답한 것을 사용자가 "총 11곳이 끝이야?"로 반문 → 저수준 함수 `queryModelWithoutStreaming`/`queryModelWithStreaming`/`queryWithModel` 직접소비 경로를 놓쳤음을 자가발견 → "11곳은 오답, 실제 최소 20곳 안팎"으로 정정 → 이후 전수 grep으로 **정확히 16곳(사이드)**으로 재확정.
   - **(이번 구간) "도구를 N턴 안 씀" 표현 부정확 정정**: 사용자가 "그 도구라는건 아무도구? Task기준 도구?"로 반문 → `getTodoReminderTurnCounts`가 `block.name === 'TodoWrite'`만 카운트함을 소스로 재확인 → "도구"라고 뭉뚱그린 앞선 표현을 "**태스크/투두 도구 전용**"으로 명시 정정.
   - **(이번 구간) "몇 턴마다 반복 재주입" 오해 정정**: 사용자가 "생성 후 하나 들어가고 몇턴마다 반복 재주입 한다는거지?"로 이해 → 어시스턴트가 "N턴마다 무조건"이 아니라 "**태스크도구 10턴 방치 && 리마인더 후 10턴** 둘 다 충족 시에만"으로 정정(attachments.ts:254-257 근거 제시).

5. Problem Solving:
   - **(pre-round6, 완전 규명 완료)**: 배치파티셔닝/컨텍스트주입4트랙/rules지연주입/훅시스템/MCP지시2모드/캐시경계/ToolSearch5단계/큐웨이크6경로/MD-vs-XML분업/0번유령메시지캐싱/스킬목록발행타이밍/CLAUDE.md가0번에있는이유/system-reminder태그전수census/ReAct사이클SR·비SR통합지도/스킬lost-in-the-middle3시나리오/기술부채287건전수스캔/CoordinatorMode구조+공통하네스확정 — 전부 소스로 완전 규명·문서화 완료.
   - **이번 구간 신규 완료**: ① 4대 없는기술 검증(오탐 걸러내며 grep) + 확장 8종 제시 — 완료. ② Reflexion 용어 구분(학술프레임워크 vs 클로드코드의 성찰능력) — 완료. ③ verification 에이전트 이중게이트 구조 규명 — 완료. ④ 별도 LLM 호출 지점 11곳→오답발견→전수재조사→16곳 확정(3회 왕복) — 완료. ⑤ 각 호출부의 실제 모델 역추적(haiku고정/가변/조건부/큰모델2예외) — 완료. ⑥ md(`클로드코드-LLM-별도호출-전수.md`)+html(`.html`, `/visual-explainer`) 2종 산출 — 완료. ⑦ LLM호출 vs 진짜에이전트 3분류(도구보유×루프여부) — 완료. ⑧ TaskCreate/TodoV2 컨텍스트주입 3경로 규명 — 완료. ⑨ task_reminder 정확한 발동조건 2차 정정("N턴마다"아님→"태스크도구 방치"→"일반도구는 무관") — 완료. ⑩ TaskUpdate가 자동트리거 아닌 모델자율판단+넛지3겹 구조임을 확정 — 완료.
   - **(미해소, 확인만 하고 지나감)**: 메시지 83("ngClearLatched..." 관련 pasted 텍스트) — 사용자가 구체 질문 없이 던진 발화로, 어시스턴트가 응답하지 않고 대화가 다음 새 주제로 전환됨. 내용(apiMicrocompact.ts:79-88, claude.ts:1469-1470, effort.ts:303-305 언급)은 이 세션 다른 어떤 조사와도 연결되지 않은 채 방치됨 — 후속 세션에서 사용자가 재언급하면 맥락을 물어 확인 필요.

6. All User Messages:
   *(1~80은 이전 요약(round6까지 누적)이 승계한 목록 — 배치파티셔닝부터 "임베딩검색/BM25/의도분류/고정워크플로우 없는거 맞아?"(80번)까지. 아래는 이번 구간에서 새로 추가된 메시지 81~94)*
   81. "Reflexion 이 없다는게 무슨말이지"
   82. "verification 에이전트 이게 빌트인으로 있어?"
   83. "ngClearLatched를 세션 고정 래치로 관리. 주석이 사고 원인을 그대로 증언합니다: \"Only latch from agentic queries so a classifier call doesn't flip the main thread's context_management mid-turn\" — 사이드 쿼리가 메인 스레드 설정을 뒤집던 게 문제였다는 것.\n- apiMicrocompact.ts:79-88 — 평상시엔 keep: 'all'(보존)을 명시적으로 보내고, 래치가 걸린 경우에만 keep: {thinking_turns: 1}.\n- claude.ts:1469-1470 — 캐시 브레이크 감지 텔레메트리에 \"Pass latched header values (not live state)\" — 실제 전송값 기준으로 계측하도록 바뀐 것도 사후 조치 흔적.\n\n② effort 다운그레이드 (3/4 high→medium → 4/7 복원). effort.ts:303-305에 사고 후 추가된 것"
   84. "에이전트 도구 쓰는거말고 LLM 을 별도로쓰는게 요약이랑 bash 툴에서 권한검증 말고 또언제가있지?"
   85. "총 11곳이 끝이야 ?"
   86. "LLM 쓰는곳 그럼 총정리해봐 아까 11곳이랑그리고 또? 한곳이라도 놓치지마"
   87. "위 내용들 다 하나의 md로 적어주고 어떤 모델호출하는지도 각각 적어라"
   88. "/visual-explainer로 시각화해줘"
   89. "근데 LLM 호출들 다 에이전트는 아니고 그냥 도구없는 LLM이지?"
   90. "클로드코드에서 TaskCreate 가 발생하면 그 Task가 웹 ui에서는 표시가 되는데.. 작업하는 LLM입장에서 현재 테스크가 뭔지 어떻게 컨텍스트가 주입이되고있는거야?"
   91. "그러니까 너말은.. 생성된 투두목록이 처음에 하넊번에 들어가고 그리고 몇턴마다 투두목록 현재상황 재주입을 반복적으로 한다는거지?"
   92. "그 도구라는건 아무도구? 아니면 Task기준 도구?"
   93. "그러면 LLM이 작업후 TodoUpdate 하는건 컨텍스트윈도우에 그냥 저상황보고 판단해서 툴콜링하는거야?"
   94. "/compact" — 실제 Claude Code 자체 컴팩션 재발동(세션 내부 이벤트, 이 세그먼트의 마지막 줄)

7. Pending Tasks:
   - (열린 제안, 확정 요청 아님) `배치-단독-개념-소스증명.md`의 짝꿍 HTML 시각화 — round5부터 계속 열려있으나 요청 없음, 보류.
   - (맥락 불명, 재확인 필요) 메시지 83("ngClearLatched..." pasted 텍스트) — 사용자가 구체 요청 없이 던졌고 어시스턴트도 응답하지 않은 채 넘어감. 이후 세션에서 사용자가 다시 언급하면 무엇을 원했는지 확인 필요.
   - (이번 구간에서 명시적으로 요청된 작업은 전부 완료됨 — 4대기술검증/Reflexion/verification에이전트/LLM별도호출16곳+md+html/에이전트3분류/TaskCreate컨텍스트주입 모두 답변·문서화 완료, 더 이상 pending 아님.)

8. Current Work:
   메시지 93("그러면 LLM이 작업후 TodoUpdate 하는건 컨텍스트윈도우에 그냥 저상황보고 판단해서 툴콜링하는거야?")에 대해 어시스턴트가 완전한 답변을 마친 상태다. 답변의 골자: TaskUpdate는 자동발동 장치가 없는 평범한 도구이며, 모델이 자기 이력·tool_result·task_reminder 3가지 신호를 종합해 스스로 판단해 부른다는 것을 확정하고, 하네스가 강제 대신 제공하는 넛지 3겹(①도구 설명문 규약 ②task_reminder 방치넛지 ③완료후 TaskList 유도, `isAgentSwarmsEnabled()` 조건부)을 정리한 뒤 "정직 표기: ③의 완료후유도는 스웜/멀티워커 조건이 붙어 단일세션에선 안 뜰 수 있음. ①②는 조건 없이 적용됨"이라는 문장으로 답변을 맺었다. 이 발화 직후 사용자가 "/compact"를 입력해 이 세그먼트가 종료됐다 — 이는 실제 Claude Code 자체 컴팩션 재발동이지 콘텐츠성 질문이 아니다.

9. Optional Next Step:
   이번 구간에서 사용자가 명시적으로 요청한 모든 항목(4대기술검증, Reflexion, verification에이전트, 별도LLM호출16곳+md+html, 에이전트3분류, TaskCreate/TodoV2 컨텍스트주입)은 전부 완료·답변된 상태이며, `/compact`가 마지막 줄이므로 이어서 강제로 진행해야 할 다음 작업은 없다. 다음 세션(컴팩션 이후)에서는 사용자의 새 메시지를 기다리는 것이 맞고, 굳이 먼저 움직인다면 남아있는 열린 제안(pending 7절)을 사용자에게 먼저 확인받아야 한다 — 특히 메시지 83("ngClearLatched..." 관련 pasted 텍스트)이 재등장하면 무엇을 원했는지부터 물어야 한다. 어시스턴트의 마지막 발화를 그대로 인용하면: "정직 표기: 위 넛지 3종 중 ③의 '완료 후 TaskList 유도'는 스웜/멀티워커(`isAgentSwarmsEnabled()`) 조건이 붙어 있어서, 단일 세션에선 안 뜰 수 있습니다. ①②는 조건 없이 적용돼요." — 이 문장으로 완결된 답변 직후이므로, 재개 시점은 "사용자의 다음 질문을 받는 것"이다.

</summary>
