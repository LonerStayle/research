## Decisions

- (승계) 사용자의 "클로드코드 전체파악" 요청 → `/Users/seobi/jinsup_space/CC`(md_group 140개/51,351줄, html_group_v2 138개, src/ 1,904개 파일·301개 디렉토리) 전수 탐색, 4계층 아키텍처(엔트리 main.tsx → 엔진 query.ts/QueryEngine.ts → 도구 10단계 파이프라인 → Ink/React TUI). md 135개 전량 재검증(2026-07-07, 89개 파일·296건 교정). 최신커밋 `2222679`.
- (승계) "배치 병렬 3조 요건"(모델 1응답 내 복수 tool_use / 도구별 `isConcurrencySafe` / 하네스 `partitionToolCalls`) 소스검증 완료 → `배치-단독-개념-소스증명.md`. **[part11에서 실전 사례로 재확인, 아래 참조]**
- (승계) 0번 유령메시지(claudeMd, `prependUserContext`가 API 호출마다 재생성, 이력 미저장) vs skill_listing(어태치먼트, 이력 1회 삽입 후 잔류) — 별개 트랙, 세부 검증 완료. rules 조건부로딩·skills/agents/slash 4종 공통 "색인 상시노출·본문 방아쇠지연" 2단 패턴 — 소스검증 완료.
- (승계) 훅안내문단·`<user-prompt-submit-hook>` 잔재론·훅=`spawn()`(tool_use 아님)·MCP 지시 조립(구형/델타)·session_guidance 캐시경계 밖 — 전부 소스검증 완료. `컨텍스트-주입-4트랙-시각설명.html` 작성 완료.
- (승계) "세션인풋 시스템프롬프트/도구 전문" md 완료(`2026-07-11-시스템프롬프트및도구내용-최신본.md`). userEmail 실변경 관측(`axtech@goldenplanet.co.kr`→`admin@jinju-ict.com`, 구snapshot으론 설명불가, "확인못함" 유지). 4색범례(🟢일치·🟡문구다름·🔴신규·⚪확인못함) 완료.
- (승계) `toolsearch-생애주기-소스분석.md`/`.html` — ToolSearch 5단계 생애주기, 점수표, lost-in-the-middle 4중 안전망, BM25 아님 — 전부 소스검증 완료.
- (승계) "ReAct 사이클 밖 엔터 없는 진입" 최종 6경로 확정 → `큐웨이크-엔터없는-진입-소스분석.md`: ①로컬백그라운드태스크완료 ②Stop훅차단 ③원격입력(bridge/CCR) ④스케줄작업 ⑤비동기에이전트결과의 숨은 프롬프트 재진입 ⑥고아 권한응답.
- (승계) "왜 XML 아니라 마크다운인가" 최종 3근거(태그언급충돌/태그희소성=출처신호/토큰·유지보수). `constants/xml.ts`(20여개 태그).
- (승계) 0번 CLAUDE.md — "매 API 호출 재인쇄"(`prependUserContext`)이지만 `getUserContext`가 `memoize`라 세션 첫 호출만 디스크read, 이후 캐시 재인쇄. 무효화 3곳(`/clear`, `/compact` 수동, autocompact 후). 설계원리(`constants/common.ts:17-24`): 불변정보는 0번 동결, 변하는 정보는 꼬리에 델타.
- (승계) 스킬/도구/에이전트 목록은 0번에 없음, 별도 어태치먼트(`attachments.ts:2661-2751` `getSkillListingAttachments`). 발행타이밍="첫 수집지점". CLAUDE.md가 0번 user에 있는 이유 4가지(권위계층분리 최유력/서브에이전트모듈성/글로벌캐시조각방지/채널일관성).
- (승계) system-reminder census 3층 확정 — 메시지레벨(어태치먼트 47종+0번유령)/인라인레벨(tool_result 속 경고)/선포장레벨(큐값 자체 사전포장). SR=모델전용채널. 신분증체계 md+html 통합(`시스템리마인더-isMeta-신분증-총정리.md/.html`).
- (승계) ToolSearch는 스킬 관할 밖(`isDeferredTool` 전용) — 스킬 재고지는 `sentSkillNames`가 결정. 로스트인더미들 스킬 못찾는 케이스 → 소극적 3종(표지판/유저명시호출/compact우연리프레시)만 있음, `EXPERIMENTAL_SKILL_SEARCH`가 진행중 해법.
- (승계) 기술부채 전수스캔(Workflow 백그라운드, `wf_89574a3c-93a`, 47에이전트·918도구호출) → **287건** 확정, `클로드코드-기술부채-대장.md/.html/-전체287건.json`. 핵심통찰: "몰라서"가 아닌 계량된 이자율 위의 "재고 끝 빚".
- (승계) "수퍼바이저 패턴 있나?" → 있음, 2층위(암묵적 Agent툴 서브에이전트 항상켜짐 / 명시적 Coordinator Mode). 코디네이터=하네스교체 아니라 메인배역변경+도구셋조정, `runAgent.ts`엔 coordinator/worker 분기 자체 없음.
- (승계) "임베딩/BM25/의도분류/고정워크플로우 4개 없나?" → 전수 grep+오탐검증 완료, 4개 전부 "없음" 확정. 관통철학: "전처리를 모델에게 위임"(검색=모델grep, 라우팅=모델도구선택, 오케스트레이션=ReAct루프) — 세션 전반 반복인용 해석틀. **[part11에서 PTC 논의 시 이 해석틀의 예외/보완 사례로 재확장, 아래 참조]**
- (승계) "유명한데 없는 것" 확장목록(부분확인수준): RAG파이프라인/대화요약메모리버퍼(compact가 대체)/Reflexion류 성찰누적루프/플래너-실행자강제분리 없음/동적few-shot없음/토큰레벨가드레일없음/세만틱캐싱없음/멀티암드밴딧·DSPy자동최적화없음.
- (승계) verification 에이전트 빌트인 존재 확인, 이중게이트(`feature('VERIFICATION_AGENT') && getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)`)로 기본비활성=Anthropic내부A/B전용.
- (승계) "LLM 별도호출 총정리" — 최종 확정: 4개 진입함수 기준 본류1+사이드16곳. 원가배분원칙: 값싼잡무=haiku, autocompact=메인모델, insights=opus고정.
- (승계) "LLM호출 다 도구없는 순수LLM이지?" → 확인, 정확함. 3분류: 도구없는순수LLM(대다수)/도구1개강제(웹검색)/진짜에이전트(Agent툴서브에이전트만).
- (승계) "TaskCreate 컨텍스트 주입 3경로" 확정 — ①즉시 tool_result ②주기적 task_reminder(`TODO_REMINDER_CONFIG={TURNS_SINCE_WRITE:10, TURNS_BETWEEN_REMINDERS:10}`) ③능동조회. "TaskUpdate 호출도 모델판단" 확인.
- (승계) 사용자가 새 상주 프로젝트(키움증권 AI PB 서비스) 브리프 제시 → CC 패턴 응용 트랙. `/draw-arch`로 "키움-AI-PB-클로드코드식-하네스-설계.md/.html" 완성, 🟩(CC소스검증)/🟦(설계제안) 2색 구분.
- (승계) hermes-agent "LangGraph supervisor" 오추천 자인·철회. 소스검증: langgraph/langchain 의존성 0건, 오케스트레이션=`while True`+`tool_calls`(ReAct). **결론: 프레임워크 없는 raw SDK 위 커스텀 하네스.** `/Users/seobi/jinsup_space/CC/CLAUDE.md:18` Edit 정정 완료.
- (승계) Coordinator Mode 재확인(`coordinatorMode.ts`): 정체성 통째교체, 도구 3개만(Agent/SendMessage/TaskStop), 워커=동일 서브에이전트 런타임.
- (승계) Workflow 도구 — `tools/WorkflowTool/` 디렉토리 자체가 현재 소스스냅샷에 부재, 배선만 남음(ant-only). "구버전 스냅샷 부재" vs "현재 활성 세션 실재" 이중근거 항상 구분. **[part11] REPL 모드도 같은 패턴(ant-only 도그푸딩, 아래 참조)으로 확인됨.**
- (승계) `/Users/seobi/jinsup_space/CC/스킬예산-로스트인더미들.md` 변환 완료.
- (승계) "ReAct 사이클 없이도 KV캐시 언제 갱신?" → `addCacheBreakpoints`(`services/api/claude.ts:3062-3106`) 확인: 캐시 브레이크포인트는 API 요청 1건당 정확히 1개, 항상 메시지배열 마지막.
- (승계) 슬래시커맨드 `/model` 2회 실행 — Sonnet 5 → Fable 5로 기본모델 변경(세션 상태 변경만).
- (승계, 프로젝트무관 일반론) "올드스쿨 툴콜링 순서 설계" 프레임 "프롬프트3곳+코드4곳+루프1개" 확립.
- (승계) "CC 기준 툴콜링설계 파악" 최종 대응표: 프롬프트①시스템=`services/api/prompts.ts`+`utils/systemPrompt.ts` / 프롬프트②도구설명=`tools/<이름>/prompt.ts` / 프롬프트③결과문구=각 도구 `mapToolResult` / 코드1계약=`Tool.ts` / 코드2실행기매핑=`tools.ts`+`constants/tools.ts` / 코드3루프=`query.ts:241 queryLoop` / 코드4검증에러=`toolExecution.ts` / API조립=`services/api/claude.ts:1235 toolToAPISchema`→`:1396 allTools` / tool_result짝맞춤=`utils/messages.ts:626`. 확장 3개: ①`stop_reason` 불신(콘텐츠필터 직접) ②`partitionToolCalls`(읽기전용병렬/쓰기직렬) ③도구=설명문+구현+권한+UI 미니모듈.
- (승계) Read→Edit `readFileState` 상태머신 5겹 장치 확정(사전경고/게이트1 미독차단/게이트2 mtime변경차단/성공후 자가갱신/Write에도 동일게이트). 정의: "안 읽은 파일 금지"가 아니라 **"지금 디스크의 그 버전을 본 적 없으면 금지"**.
- (승계) 결과 넛지 가족 A(성공넛지5종)/B(에러리다이렉트5종)/C(하네스힌트1종, `buildSchemaNotSentHint`) 3그룹 확정, `mapToolResult` 구현 도구 19개 grep 확인. 핵심통찰: **"에러 메시지는 예외 로그가 아니라 프롬프트다."** **[part11] "Glob 잘림" 넛지(A그룹) 원리를 사용자에게 상세 재설명 완료 — 아래 참조.**
- (승계) "넛지" 정의 — 탈러 『Nudge』(2008) 인용, "강제 없이 선택자유 유지한 채 유도". CC 맥락: 강제=에러(안읽은파일수정불가) vs 넛지=무시가능(TaskUpdate "Call TaskList now"). 근거: 방치리마인더 원문 "This is just a gentle reminder - ignore if not applicable".
- (승계) Playwright 렌더링 검증 패턴 확립(html 시각 확인 요청 시 임시 `python3 -m http.server`로 `file://` 차단 우회 후 스크린샷, 검증 즉시 스크린샷·`.playwright-mcp`·서버 전부 삭제).

**이하 part10 요약(part11 시작 시점에 완전 종결·확인됨) — `도구호출-순서설계-하드소프트.md/.html` 대규모 재편 완료.**

- (승계, part10 종결) `도구호출-순서설계-하드소프트.md/.html`(작성일 2026-07-22) — 물리·하드·소프트 3층 → **하드·소프트 2층**으로 재편. "비용 경사"(근거없음, 사용자지적으로 철회) → **"출력 부피 경사"**로 정정(Glob 100개잘림/Grep head_limit/Read 2000줄상한 근거). "깔때기 설계" → **"입장권 설계"**로 개명(AskUserQuestion 채택, 필수파라미터 조달난이도가 만드는 창발적 순서: Grep=무전제/Glob=패턴만/Read=절대경로 필수). "Glob→Grep 배선" 주장 철회 → **Y자 합류**로 정정(Grep의 `glob` 파라미터는 패턴문법이지 Glob 출력 아님, 자체발견·자체정정 사례). "대체지침"을 소프트 규칙에서 제외 → 신규 **§04 "도구 주의사항"**(순서 아닌 수단선택 규칙, 권장형 시스템프롬프트 vs 금지형 도구설명문 양면)으로 재분류(사용자가 AskUserQuestion 자체를 거부하고 직접 재프레이밍 제시 → 즉시 수용). **최종 구조**: §00 스펙트럼(하드/소프트2행) → §01 하드 → §02 소프트A(입장권설계) → §03 소프트B(문구3갈래: 탈출구/결과넛지/리마인더) → §03-1 결과넛지가족전수 → §04 도구주의사항 → §05 결정흐름 → §06 프롬프트 한국어대역. **[part11 벽두] 잔여 "대체" 참조 grep 재검증(0건 확인) + html §04/SVG라벨 최종 반영 확인 메시지 사용자에게 전달 완료 — round10 최우선 TODO 완전 해소.**

**이하 part11 신규 — 대화 성격이 "CC 문서 편집"에서 "GPT vs Claude 도구설계 교리 비교 + Programmatic Tool Calling(PTC) 개념 학습" QA로 전환. 문서 Edit 없음, 전부 채팅 답변(정보성).**

- **[신규, part11]** 사용자 질문 "성공 넛지 — Glob 잘림"의 의미를 상세 재설명 — Glob은 매칭 100개 초과 시 결과 끝에 truncation 안내문(`GlobTool.ts:50` "limited to 100 files")을 덧붙임. "에러 아니라 성공"임을 표로 대조(호출결과=성공/문구역할=제안/모델선택=재량), "조용한 잘림"을 막는 정직고지+다음행동제안 2기능. Workflow 도구 설명서의 "no silent caps" 원칙과 동일선상. **라벨 "Glob 잘림"→"Glob 결과 잘림 고지(100개 상한)"로 바꿀지 제안했으나 사용자가 다음 질문으로 전환 — 응답/반영 여부 미확인(아래 Open TODOs).**
- **[신규, part11]** Explore 멀티 병렬 스폰 원리 3층 확정 — ①API스펙: 응답 1개에 tool_use 블록 N개 허용(모델의 학습된 능력, 하네스가 만든 게 아님) ②넛지 2곳: 시스템프롬프트(`constants/prompts.ts:310` "make all independent tool calls in parallel... Maximize use of parallel tool calls") + Agent 도구 설명문(`tools/AgentTool/prompt.ts:248` "Launch multiple agents concurrently whenever possible... use a single message with multiple tool uses", `:271` 사용자가 "병렬로"라 명시하면 MUST) ③실행기: `query.ts:953` 응답에서 tool_use 전부 추출 → `services/tools/toolOrchestration.ts:91` `partitionToolCalls` → `tools/AgentTool/AgentTool.tsx:1273` `isConcurrencySafe() { return true; }` → `toolOrchestration.ts:30` `runToolsConcurrently` → tool_result들이 한 user 메시지로 묶여 복귀(tool_use_id 짝맞춤). Agent가 병렬안전인 이유="서브에이전트는 독립세션·독립컨텍스트라 상태충돌 없음"(Edit 등 쓰기도구는 false=직렬). **정정: Agent 도구는 디퍼드가 아니라 상시장착 코어**(ToolSearch 뒤에 숨는 건 주로 MCP 도구) — Explore 멀티스폰에 ToolSearch는 관여 안 함.
- **[신규, part11]** `constants/prompts.ts:310`의 소속 확정 — `getUsingYourToolsSection()`(함수 선언 `:269`) 안이고, 이 함수는 `getSystemPrompt` 조립기(`:569`에서 호출)의 **정적(캐시) 구역**(`# Using your tools` 섹션, BOUNDARY MARKER 앞)에 위치. 소스 주석(`:325-328`) "subagents receive skill_discovery attachments but don't go through getSystemPrompt"(별도경로 `enhanceSystemPromptWithEnvDetails`)로 **서브에이전트는 이 경로를 안 탐**을 확정 → `:310`의 병렬지침은 **메인 에이전트 전용**. 코디네이터모드도 `getCoordinatorSystemPrompt()` 통째교체라 해당 밖. 반면 Agent 도구설명문(`AgentTool/prompt.ts:248`)의 병렬지침은 Agent 도구를 가진 누구든(tools 배열에 실려가므로) 수신 — 단 서브에이전트는 기본적으로 Agent 도구 자체가 금지(`ALL_AGENT_DISALLOWED_TOOLS`, ant 유저 예외)라 대부분 해당없음. 서브에이전트 자체 프롬프트에 별도 병렬지침이 있는지는 **미확인**(오픈).
- **[신규, part11]** GPT vs Claude "도구 description 안에 언제 쓸지 적나" 교리 비교 — claude-api 스킬 로드 후 1차 답변("양쪽 동일 규약 수렴")을 제시했으나, 사용자가 "gpt지금도그래? 웹 공식문서 보고와봐" 요청 → WebFetch로 `https://developers.openai.com/api/docs/guides/function-calling`(원래 URL `platform.openai.com/docs/guides/function-calling`은 301 리다이렉트) 직접 검증 → **정정**: OpenAI 원문 *"Use the system prompt to describe when (and when not) to use each function."*(when=시스템프롬프트) vs Anthropic 원문 *"Be prescriptive about when to call it... trigger conditions in the description give measurable lift"*(when=description) — **교리가 상반됨**, "수렴했다"는 어제 발언은 오답으로 정정. 어제 발언 중 유일하게 맞은 부분: 지연로딩(디퍼드) 도구에 한해서는 OpenAI도 *"put detailed guidance in the function description"*으로 뒤집음 → **동적 도구셋이라는 조건에서만 수렴**. 도구개수 권장도 비교: OpenAI *"fewer than 20 functions... soft suggestion"* vs Anthropic *"Limit tool count: keep the set focused"*(정성적) — 같은 교리의 정량화 차이일 뿐 기능열세 아님, CC 자체 코어 도구 구성(상시장착 ~12개+디퍼드 100개+)이 실증.
- **[신규, part11]** OpenAI 지연로딩 확인 — 공식명 **`tool_search`**, 도구 정의에 `defer_loading: true` 플래그 설정, namespace description(간결, 선택용)+function description(상세, 사용법용) 이원화, **gpt-5.4 이상만 지원**. 3개 구현체 비교표 확정: OpenAI API `tool_search`(서버측, 검색알고리즘 미명시) / Anthropic API tool search(서버측, **regex판·BM25판 두 종류**) / CC ToolSearch(**클라이언트측**, BM25 아닌 필드가중 불리언매칭 — 이전 라운드 검증분).
- **[신규, part11]** OpenAI description 작성규정 확정 — description엔 **목적/파라미터형식(예시포함)/출력의미** 3가지만, "언제(when)"는 시스템프롬프트로 이관(예외 둘: 디퍼드도구는 description에 상세지침, 반복오류 수정시 예시·엣지케이스 추가하되 "reasoning 모델엔 예시가 오히려 성능해칠 수 있음" 각주 있음). 스키마 규칙: `strict: true` 상시권장, enum으로 무효상태 표현 불가능화, `additionalProperties: false` 필수. 안티패턴표: `toggle_light(on,off)`처럼 무효상태 가능한 bool쌍 금지→enum(`state:"on"|"off"`), 모델이 이미 아는 값(order_id 등) 파라미터 요구 금지→무인자+코드주입(*"Don't make the model fill arguments you already know"*), 순차호출쌍은 병합, **"Pass the intern test"**. 원문 확인: *"Functions are injected into the system message"* — description도 물리적으론 프롬프트 안 구조화 슬롯이라는 기존 주장의 OpenAI측 교차확인. CC의 입장권설계(enum·input_schema)·니치선언(인턴테스트와 동일정신)과 안티패턴 원칙이 일치함을 확인 — **교리(when 위치)는 갈려도 스키마공학 밑바닥 원칙은 업계공통**.
- **[신규, part11]** "왜 갈렸나" 결론 — 능력 문제 아니라 **제품 전제 차이**: OpenAI=단일개발자가 도구<20개+시스템프롬프트 전부 소유(중앙집중형 가능) / Anthropic=MCP생태계, 도구작성자≠앱작성자, 서드파티는 남의 시스템프롬프트를 못 건드림(description이 지침 실을 유일 채널, 분산형 강제). "GPT가 긴 description 소화 못해서"라는 가설은 OpenAI 자기 문서의 디퍼드도구 예외("put detailed guidance in the function description")로 **자체 반증**됨.
- **[신규, part11]** Programmatic Tool Calling(PTC) 개념 전수 확정 — 사용자가 공식문서에서 발견한 `<tool_orchestration>` 프롬프트예제(sku_123/get_inventory/get_demand/shortage_units)의 정확한 출처를 특정: Anthropic PTC문서(`https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling`, WebFetch 결과 59.2KB 초과로 로컬 파일 persist)에는 해당 예제 **없음**(목차만: Model compatibility/Quick start/How PTC works/Core concepts(`allowed_callers` 필드, `caller` 필드, Container lifecycle)/Example workflow 5단계/Advanced patterns(batch loops/early termination/conditional tool selection/data filtering)/Response format/Error handling/**When to use**(Strong fit: fan-out·대량결과필터링·에이전틱검색 / Weak fit: 순차의존추론·소규모호출·즉각피드백필요)) → WebSearch로 실제 출처가 **OpenAI 전용 PTC가이드**(`https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling`)의 **"Guide routing when both modes are available"** 섹션임을 확정, 문장별 설계요소 대응표 작성(only=화이트리스트 / concurrently=병렬 / documented fields=스키마추측금지 / process·reduce=중간데이터축약 / exactly one JSON=출력계약 / max(...)=산술코드위임 / evidence=근거동봉 / Stop when=종료조건 / Retry at most 1=재시도상한 / Do not repeat·side-effecting=멱등성+부작용금지 / **direct tool calls only for approval**=부작용행동은 PTC 밖). PTC 정의: ReAct 왕복 대신 모델이 쓴 코드(스크립트)가 도구호출(병렬·루프·조건)을 대행, 중간결과는 샌드박스 내부처리, 최종산출물만 컨텍스트 복귀. 비교표: OpenAI(JavaScript, Responses API 호스팅런타임) vs Anthropic(**Python**, code execution 컨테이너, `allowed_callers` 필드). Anthropic 공개수치: 검색벤치마크(BrowseComp/DeepSearchQA) **+11% 성능 / −24% 토큰**, 지출감사 예시 토큰 **−90%**. 예제 마지막 줄(부작용행동은 직접툴콜 승인용)이 이 세션의 하드/소프트 프레임과 직결됨을 연결(조회·계산=소프트(PTC위임), 부작용·승인=하드(직접툴콜=게이트)). PTC와 CC의 Workflow도구를 같은 혈통("오케스트레이션을 모델 턴별재량→결정론적 스크립트로 이전")으로 연결, 차이는 규모(Workflow=에이전트들 지휘, PTC=툴콜들 지휘).
- **[신규, part11]** "디퍼드로딩과 PTC는 다른 것" 확정 — 개입시점 다름(디퍼드로딩="장착 단계"·"뭘 실을까"/PTC="실행 단계"·"어떻게 부를까"), 절약대상 다름(디퍼드로딩=미사용 도구의 스키마·설명서 토큰/PTC=툴콜 중간결과 토큰), **조합 가능**(ToolSearch로 2개 장착 → 그 2개를 PTC 스크립트로 병렬호출+계산). CC 대응: 디퍼드로딩=검증된 ToolSearch 생애주기, PTC=CC에 정확한 대응물 없고 굳이 찾으면 Workflow 도구의 정신.
- **[신규, part11]** "PTC=플랜앤익스큐트?" 확인 + CC 소스 안의 PTC 대응물 발견 — 사용자 직감("계획서 자체가 프로그램") 확인, 고전 Plan-and-Execute와 차이는 "계획이 정적 리스트"가 아니라 **코드라 결과분기(if문)를 계획에 미리 내장 가능**한 점. "클로드에 PTC 없다"는 사실과 다름 — **Claude API에 정식 존재**(Opus 4.5+/Sonnet 4.5+, 커스텀도구에 `allowed_callers: ["code_execution_20260120"]`), **Anthropic이 OpenAI보다 먼저 출시**(2025-11 "advanced tool use", OpenAI는 후발). CC(공개판)는 PTC 미사용(전부 턴별 직접호출)이나, **소스에 숨은 CC판 PTC 발견 = REPL 모드**: `tools/REPLTool/constants.ts` `isReplModeEnabled()`(`:23-31`, `CLAUDE_REPL_MODE` env 수동 켜기, 또는 `USER_TYPE === 'ant' && CLAUDE_CODE_ENTRYPOINT === 'cli'`면 Anthropic 내부 기본 켜짐), `REPL_ONLY_TOOLS`(`:37`)={Read, Write, Edit, Glob, Grep, Bash, NotebookEdit, Agent}(8종) — REPL모드 켜지면 이 도구들이 **직접호출에서 숨겨지고 스크립트(REPL VM) 안에서만 함수처럼 호출 가능**해짐, 구조가 PTC와 동일. `tools/REPLTool/primitiveTools.ts:15` "VM 컨텍스트에서 접근 가능하게 한다". Workflow 도구(ant전용)와 같은 패턴("일반 유저 미공개, 내부 도그푸딩 중")으로 확정. 정직표기: REPL 실행기 본체는 스냅샷에 부재(`constants.ts`·`primitiveTools.ts`만 존재, 다른 디퍼드 구현체들처럼 외부빌드 제외 추정).
- **[신규, part11]** PTC 단점 확정 — 핵심: 판단력이 **"계획 시점"에 고정**, 코드가 표현 가능한(사전에 적어둔 if분기) 반응만 가능, "예상 밖 상황에 대한 지능적 대응"(ReAct의 본질)은 불가. Anthropic 공식 Weak fit 원문 인용: *"Strictly sequential workflows where each call depends on Claude reasoning over the previous result, because the script cannot skip the model round-trip in that case."* 추가 단점표: 발견기회상실(코드가 거른 중간데이터를 모델이 영영 못 봄)/게이트불가(스크립트 내 개별승인프롬프트 불가 → "부작용 행동은 직접툴콜로 빼라"가 공식지침의 근거)/고정오버헤드(컨테이너기동+스크립트생성, 호출2~3개짜리 소규모작업엔 손해)/에러처리선불(재시도·실패처리 전부 사전코딩 필요)/시간제약(도구결과 대기 ~4분, 유휴컨테이너 회수 ~5분)/호환성제약(`strict:true`·강제 `tool_choice`·MCP 비호환, Anthropic 한정). 실무 하이브리드 3분할 재확정: 판단구간=ReAct유지 / 기계적구간(조회·필터·집계·산술)=PTC위임 / 부작용·승인=직접툴콜(게이트경로). CC가 공개판에서 ReAct를 유지하는 이유("코딩에이전트=결과추론이 필요한 대표 도메인, 테스트에러 읽고 원인추론·파일보고 수정방향 결정")는 **어시스턴트의 해석으로 명시 표기**("이건 제 해석입니다 — 소스 근거 아님").
- **[신규, part11]** 용어 재정의(사용자 이해도 확인 연쇄질문 대응) — **"직접 툴콜"** = 세션 내내 써온 평범한 tool_use 호출(모델→하네스→결과, PTC 등장으로 구분할 이름이 필요해져 붙여진 이름일 뿐 새 개념 아님). **"기계적 구간"** = 판단 불요 구간, 판별법="이 단계의 행동을 결과가 나오기 전에 미리 코드로 적을 수 있나?"(적을 수 있으면 기계적→PTC 가능, 결과를 봐야 다음이 정해지면 판단→ReAct 유지). "직원 20명 경비확인+초과자 계정정지" 예시로 4조각 분류(조회=기계적/한도비교=기계적(산수)/"초과가 출장 때문인가?"=판단/계정정지=부작용).
- **[신규, part11]** "PTC=샌드박스에서 도구호출, 코드실행 그자체 아니야?" 사용자 확인질문에 보정 — "거의 정확", 보정 1건: **PTC ≠ 코드실행 그 자체** — PTC = 기존 code execution 도구 + **"등록된 도구를 코드가 부를 수 있는 다리"**(`allowed_callers` 필드, 원래 code execution은 닫힌 상자라 외부 도구를 못 부름). 도구는 샌드박스 "안"에서 실행되는 게 아니라 — 코드실행중 툴콜 라인에서 컨테이너가 **일시정지** → 툴콜은 원래 주체(클라이언트 도구면 사용자 서버, 서버 도구면 Anthropic)가 실행 → 결과가 돌아오면 그 줄부터 코드 재개 → 최종 print만 모델 컨텍스트로. 샌드박스는 "실행장"이 아니라 **"지휘소"**. 응답의 `caller` 필드가 코드호출 vs 모델호출을 구분.
- **[신규, part11]** "직접툴콜과 ReAct 차이" 확정 — 대립 개념이 아니라 **층위가 다름**: 직접툴콜=호출 1회의 방식("모델이 도구를 부른다", ↔ PTC호출="코드가 부른다") / ReAct=여러 호출을 잇는 루프 패턴([추론→직접툴콜→결과관찰]×반복, ↔ 플랜앤익스큐트/PTC스크립트="판단이 계획시점에 한 번"). **직접툴콜 ⊂ ReAct**(직접툴콜을 반복하면 자연히 ReAct가 됨, ReAct 없이 직접툴콜은 성립하지만 그 역은 성립 안 함). 바둑 비유(직접툴콜=내가 돌을 직접 놓는다 / ReAct=한 수 놓고 판을 보고 다음 수). 이전 발언 "판단구간→직접툴콜"을 "판단구간→직접툴콜로 ReAct 루프를 유지"로 재확인·보정.

## Open TODOs

- (해결됨, part11 벽두) round10 최우선 TODO(html §04/SVG라벨 확인메시지 미보고) — part11 시작 즉시 grep 재검증(잔여 "대체" 참조 0건) + 확인 메시지 전달 완료. 재확인 불필요.
- **[신규, part11, 낮은 우선순위, 오픈 옵션]** "Glob 잘림" 라벨을 "Glob 결과 잘림 고지(100개 상한)"로 바꾸는 안 — 어시스턴트가 제안했으나 사용자가 응답 없이 다음 질문으로 전환. md/html에 반영됐는지 미확인, 재언급 시 확인부터.
- **[신규, part11, 낮은 우선순위, 오픈]** 서브에이전트 자체 프롬프트에 별도 병렬 툴콜 지침이 있는지 — 미확인, 필요시 서브에이전트 정의 프롬프트(`enhanceSystemPromptWithEnvDetails` 경로) 확인 필요.
- (승계, 재확인 필요, 우선순위 낮음) `toolsearch-생애주기-소스분석.md`의 "§08 추가 Q&A"/`.html`의 "07 추가 Q&A" 섹션 육안 검증 아직 안 함.
- (승계, 미착수) `배치-단독-개념-소스증명.md`의 HTML 시각화 버전 — 어시스턴트 제안만, 사용자 요청 없음.
- (승계, 낮은 우선순위) `큐웨이크-엔터없는-진입-소스분석.md` 최종본 전체 통독 검증 안 함.
- (승계, 낮은 우선순위, 오픈 옵션) 기술부채 287건 중 특정 카테고리 심화 — 사용자 요청 없음.
- (승계, 낮은 우선순위, 오픈 옵션) 코디네이터-워커 아키텍처 별도 md/HTML화 — 사용자 요청 없음.
- (승계, 매우 낮은 우선순위, 진위불명) "ngClearLatched/apiMicrocompact.ts/claude.ts:1469-1470/effort.ts:303-305" 정체불명 삽입 텍스트 — 재언급 시 무엇에 대한 것인지 되물어 확인부터.
- (승계, 오픈옵션, 어시스턴트 제안만) 키움 설계도 후속 2건(모드1 비교판/시퀀스다이어그램) — 사용자 요청 아직 없음.
- (승계, 정보용, 유효) "LLM 별도호출 전수" 최종 확정(본류1+사이드16, 4개 진입함수 기준) — "11곳"은 폐기된 중간값, 재질문 시 16곳 기준.
- (승계, 정보용, 유효) "system-reminder 전수" 최종 지도(메시지레벨/인라인레벨/선포장레벨 3층) 구조 불변.
- (승계, 정보용, 유효) hermes-agent 실제 아키텍처(프레임워크無/raw SDK/멀티프로바이더어댑터/ReAct while루프) 확정, `/Users/seobi/jinsup_space/CC/CLAUDE.md:18` 이미 수정반영.
- (승계, 정보용, 유효) Workflow 도구/REPL 모드 — "src 스냅샷엔 배선만 남고 구현부재+ant전용게이트"와 "현재 활성 세션엔 실재하는 도구/모드" 두 근거 항상 구분.
- (승계, 정보용, 유효) KV캐시 갱신 트리거="API요청 1건당 마커 1개, 항상 마지막 메시지" — 도구유무 무관 확정.
- (승계, 정보용, 유효) "CC 기준 올드스쿨 툴콜링 뼈대" 최종 대응표 + "결과 넛지 3가족(A/B/C)" 확정, 재질문 시 이 기준.
- (승계, 정보용, 유효) `도구호출-순서설계-하드소프트.md/.html` **최종 구조**(part10에서 확정, part11에서 확인완료) — 하드·소프트 2층, §02소프트A=입장권설계, §03소프트B=문구3갈래(탈출구/결과넛지/리마인더), §03-1=결과넛지가족전수, §04=도구주의사항(대체지침 이동됨), §05=결정흐름, §06=프롬프트대역. 재질문 시 이 구조 기준(3층/깔때기/비용경사/대체지침-소프트B소속 등 구 표현은 전부 폐기됨).
- **[신규, part11, 정보용, 유효]** GPT(OpenAI) vs Claude(Anthropic) 도구설계 교리 최종 확정 — "when(언제쓸지)"의 위치가 상반(OpenAI=시스템프롬프트, Anthropic=description), 동적/디퍼드 도구셋 조건에서만 수렴. 재질문 시 이 기준(어제자 "완전 수렴" 주장은 폐기됨).
- **[신규, part11, 정보용, 유효]** PTC(Programmatic Tool Calling) 개념·CC의 REPL모드 대응·디퍼드로딩과의 구분 최종 확정 — 재질문 시 이 라운드 내용을 기준으로 답할 것.

## Constraints/Rules

- 이 워크스페이스(연구 레포)의 탐색 작업은 프로젝트 CLAUDE.md 지침에 따라 Explore 서브에이전트에 위임하고, 실행/작성은 메인에서 직접 수행.
- 새 분석 문서는 기존 도감류 문서 옆에 자매 문서로 작성. 기계별 절대경로가 본질적으로 포함된 일회성 스냅샷 문서는 `~` 중립화 예외.
- 서브에이전트/워크플로우 결과 원본 산출물은 절대 그대로 tail/Read 하지 않는다 — 완료 알림의 `<result>` 요약 또는 python 파싱 요약만 사용. **[part11] WebFetch 결과가 너무 크면(59.2KB 사례) 로컬 파일로 persist되는데, 이때도 grep/sed로 필요 구간만 뽑아 확인하고 전체를 Read하지 않는 동일 원칙 적용.**
- 모든 기술적 주장은 로컬 재구성 소스(`~/jinsup_space/CC/src`)에서 grep/Read로 직접 검증. 추측·과장 금지 — 확인 안 된 부분은 "소스에서 확인 못함"/⚪ 마커 또는 "부분확인 수준"으로 정직 표기. 다른 레포에 대한 주장도 동일 엄격도로 검증. **[part11] 이 원칙이 외부(GPT/OpenAI) 주장에도 동일 적용됨 — "일반지식으로 답변" 대신 WebFetch로 공식문서 원문을 직접 인용하고, 정정이 필요하면 전날 발언도 스스로 "정정" 표기.**
- 항상 한국어로 응답.
- 사용자는 밀도 높은 설명보다 구체적 시나리오/비유를 선호, 사용자가 반문·재확인·불만을 던지면 어시스턴트가 즉시 스스로 오류/누락을 인정하고 정정하는 패턴이 세션 표준 — part7까지 3회, part8 1회, part9 2회, part10 최소 4회, **part11에서 추가로 최소 3회**(GPT/Claude "수렴" 주장 정정 / "직접툴콜=ReAct" 혼용 정정 / "코드실행 그자체" 살짝 보정). 매번 근거코드·원문 인용 우선제시 후 정리하는 순서 일관 유지. **[part11] 이 패턴이 문서 편집 없는 순수 정보성 채팅 QA에서도 동일하게 반복됨 — 사용자의 단순 확인질문("~ 맞아?", "이거 뭐야")에도 매번 소스/원문 재검증 후 답하는 습관 유지.**
- 사용자 지적이 없어도 어시스턴트가 무관한 작업 도중 자발적으로 소스를 재확인해 스스로 이전 주장의 오류를 발견·정정하는 사례(part10의 Glob→Grep 배선 오류 발견)가 세션 표준 패턴으로 굳어짐.
- 문서 섹션/개념 개명(rename) 판단은 `AskUserQuestion`으로 옵션 제시 후 사용자 선택하는 것이 원칙(전역 CLAUDE.md 규칙 적용 사례, part10). 단 선택지가 사용자의 실제 의도(카테고리 재구성)와 다르면 사용자가 tool_use 자체를 거부하고 자유서술로 재프레이밍할 수 있고, 이 경우 어시스턴트는 즉시 사용자 프레임을 그대로 수용해 실행.
- src 스냅샷은 구버전임을 사용자가 명시적으로 인지 — 신/구 대조 시 4색 범례(🟢🟡🔴⚪) 관례. "구버전 스냅샷 vs 현재 활성 세션의 실제 툴셋" 이중근거 구분을 절대 섞지 않고 각각 명시.
- 전수조사(`grep -rn` 전체 호출처/렌더 스위치 스캔) 후 표로 요약하는 방식이 반복 확립된 답변 포맷.
- 대규모 전수조사 요청 시 Workflow 도구를 백그라운드로 발사해 다수 서브에이전트 병렬 동원, 단 소규모 조사(part7~part11 모두)는 메인이 직접 grep/WebFetch 반복으로 처리.
- md/html 짝꿍 문서에 사용자가 이해 못한 용어를 반영 요청하면 기존 절 머리에 "용어 안내" 소절 삽입, 문서 자체의 표현·구조를 사용자가 지적한 경우에만 문서 Edit으로 반영 — 채팅 즉답과 문서수정 구분 유지. **[part11] 전체가 채팅 QA라 문서 Edit 자체가 0건 — 산출물 반영이 필요없는 라운드였음을 구분 표기.**
- 세션 전반의 해석틀 "전처리를 모델에게 위임"이 반복 재사용됨. "도구 순서 설계"의 하위원칙: "순서 강제 문구는 어디에도 없다 → 필수 입력(입장권) 조달 난이도 차이가 만드는 창발적 순서 → '수단 선택 규칙(도구 주의사항)'과는 다른 축임을 명확히 분리."
- 모델 배분 원가 원칙("값싼 잡무=haiku, 품질중요=큰모델")이 소스로 확정 — 향후 "왜 이 모델을 쓰나" 질문에 1차 가설로 적용 가능.
- 세션 성격 확장 — "CC 내부 리버스엔지니어링" + "키움증권 AI PB 설계 응용"(🟩/🟦 2색) + **[part11 신규 트랙]** "GPT/Claude 도구설계 교리 비교 + PTC 등 최신 API 기능 학습"(공식문서 WebFetch 기반, CC 소스검증과 출처를 분리 표기).
- "다른 레포(hermes-agent 등)"나 "다른 벤더 문서(OpenAI 등)"의 주장도 2차 문서/기억을 믿지 말고 소스/공식문서 자체를 grep·Read·WebFetch로 직접 검증, 불일치 시 원본 우선하고 필요시 스스로 정정.
- "일반론(프로젝트/소스 무관)" 질문과 "이 프로젝트 소스 기준" 질문, 그리고 **[part11]** "Anthropic 공식 문서 기준" vs "OpenAI 공식 문서 기준" 질문을 명확히 구분 표기.
- 문서(html)의 시각적 렌더링을 사용자가 의심하면 설명이 아니라 Playwright로 직접 렌더링 후 스크린샷 확인, 검증 즉시 산출물(스크린샷·로그·임시서버) 전부 삭제해 레포에 잔여물 안 남김.
- 조사로 새로 발견한 내용을 채팅 답변에만 담고 기존 산출 문서에 반영하지 않으면 사용자가 재지적함 — 조사 결과는 답변 직후 관련 문서에도 즉시 증보 반영하는 것이 표준(단, part11처럼 산출 문서가 없는 순수 QA 세션엔 해당 없음).
- 문서/답변 내 표현·구조가 소스 근거 없이 어시스턴트의 해석 프레임(비유·은유)으로 슬쩍 들어가는 것을 사용자가 민감하게 잡아냄 → 은유·해석을 도입할 때마다 "이건 제 해석이고 소스에 있는 건 X뿐"이라는 식으로 해석과 소스검증분을 문장 단위로 분리 표기하는 습관 유지(part10 "비용경사" 사례, **part11 "CC가 ReAct 유지하는 이유" 사례에서도 동일 적용**).
- **[신규, part11]** 사용자가 공식문서 원문 재검증을 요청("웹 공식문서 보고와봐")하면 즉시 WebFetch로 1차 소스를 직접 인용해 답하고, 리다이렉트(301) 발생 시 새 URL로 즉시 재요청. WebSearch는 WebFetch로 못 찾은 정보(예: 특정 프롬프트 예제의 출처 문서 자체를 모를 때)의 출처 특정 용도로 보조 사용.

## Pending user asks

- (해결됨, part11) part10 마지막 요구("대체지침을 소프트 규칙에서 제외해 도구 주의사항으로 분리") — html §04 삽입 + SVG 라벨 정리까지 최종 확인 메시지 전달 완료. 재확인 불필요.
- (부수적, 매우 낮은 우선순위) Open TODOs의 문서 반영 육안검증 항목들, 기술부채 특정 카테고리 심화, 코디네이터 아키텍처 별도 문서화, 키움 설계도 후속 2건, **[part11] "Glob 잘림" 라벨 rename 여부** — 전부 사용자가 명시적으로 재요청한 것이 아니라 어시스턴트가 제안만 한 오픈 옵션.
- (승계, 매우 낮은 우선순위, 진위불명) "ngClearLatched" 등 정체불명 삽입 텍스트 — 재언급 시 무엇에 대한 것인지부터 재확인.
- part11 종료 시점 — 사용자의 마지막 질문("직접툴콜과 ReAct 차이는또뭐야")까지 완전히 답변 완료된 상태로 대화 종료, 명시적으로 남은 미답 질문 없음.

## Exact identifiers

- 워크스페이스 루트: `/Users/seobi/jinsup_space/CC`; 최근커밋 `2222679`
- (승계) 산출 문서(전 라운드까지): `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md`, `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html`, `/Users/seobi/jinsup_space/CC/배치-세계-전수도감.md`(244줄), `md_group-교정-변경내역.md`, `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`(+`.html`), `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md/.html`, `/Users/seobi/jinsup_space/CC/큐웨이크-엔터없는-진입-소스분석.md`, `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md/.html`, `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md/.html/-전체287건.json`, `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md/.html`, `/Users/seobi/jinsup_space/CC/키움-AI-PB-클로드코드식-하네스-설계.md/.html`(작성일 2026-07-18), `/Users/seobi/jinsup_space/CC/스킬예산-로스트인더미들.md`
- `/Users/seobi/jinsup_space/CC/도구호출-순서설계-하드소프트.md`(작성일 2026-07-22, part9~part10 증보/재편, part11에서 잔여참조 재검증만·수정없음) + `/Users/seobi/jinsup_space/CC/도구호출-순서설계-하드소프트.html`(동일). **최종 구조**: 제목 "도구 호출 순서 설계 — 하드·소프트 2층 규칙", h1 "차단기·표지판으로 설계한다"(html), §00 스펙트럼(하드/소프트 2행), §02 소프트A=입장권 설계(glob→grep→read, Y자 합류), §03 소프트B=문구장치 3갈래(탈출구/결과넛지/리마인더), §03-1 결과넛지가족전수, §04 도구 주의사항(대체지침 이동됨), §05 결정흐름, §06 프롬프트 한국어 대역.
- 입장권 설계 근거: `GrepTool.ts:35-40`(pattern만 필수), `GlobTool.ts:28`(pattern만 필수), `FileReadTool.ts:229`(file_path 절대경로 필수)
- 출력 부피 상한 근거: `GlobTool.ts:50`(100개 잘림, "limited to 100 files"), `GrepTool.ts:104-107`(head_limit 기본상한), `FileReadTool.ts:181`(2000줄+토큰 초과 에러)
- Grep 스키마 원문: `pattern`(필수), `path`(optional, cwd 기본), `glob`(optional, `'Glob pattern to filter files (e.g. "*.js") - maps to rg --glob'`), `output_mode`/`-B`/`-A`/`-C`/`context`/`-n`/`-i`/`type`/`head_limit`
- 도구 주의사항(§04) 근거: `constants/prompts.ts:293-299` 부근 권장형 5줄("use Glob instead of find or ls" 등) vs 도구설명문 금지형("NEVER invoke grep or rg as a Bash command")
- (승계) rules 로딩: `src/utils/claudemd.ts:250-279,688-778,1198-1253,1369-1395`
- (승계) 훅안내문단: `src/constants/prompts.ts:127-129,444,560-576`; 훅 spawn `src/utils/hooks.ts:7,938-981`
- (승계) MCP 지시: `prompts.ts:160-165,579-603`; `attachments.ts:702,854,1584`; `messages.ts:4216-4231`
- (승계) 캐시경계: `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`; `splitSysPromptPrefix() api.ts:321-410`; `getSessionSpecificGuidanceSection prompts.ts:352-400`
- (승계) ToolSearch: `tools/ToolSearchTool/prompt.ts:35-42,50-51,62-108,110-117`; `ToolSearchTool.ts call():328-434`; `toolSearch.ts` 각종 함수
- (승계) src/tools/ 42개 전체목록(part9 기록 그대로 유효)
- (승계) 모델정체성 구버전 근거: `prompts.ts:118 FRONTIER_MODEL_NAME='Claude Opus 4.6'`
- (승계) verification 에이전트: `tools/AgentTool/built-in/verificationAgent.ts:134`, `constants.ts:4`, `builtInAgents.ts:65-68`
- (승계) LLM 별도호출 전수: 진입함수4종 `services/api/claude.ts:709,752,3241,3300,1017`; A)queryHaiku 8곳, B)queryModelWithoutStreaming 5곳, C)queryModelWithStreaming 2곳, D)queryWithModel 1곳·3회(`commands/insights.ts:883,1026,1577`)
- (승계) TaskCreate/Task 컨텍스트: `utils/messages.ts:3663-3679(todo_reminder),3680-3699(task_reminder),3954,4270`; `TODO_REMINDER_CONFIG={TURNS_SINCE_WRITE:10,TURNS_BETWEEN_REMINDERS:10}`(`attachments.ts:254-256`)
- (승계) 키움 AI PB 산출물: `/Users/seobi/jinsup_space/CC/키움-AI-PB-클로드코드식-하네스-설계.md/.html`(작성일 2026-07-18)
- (승계) hermes-agent 소스 검증 경로: `/Users/seobi/jinsup_space/hermes-agent`(`pyproject.toml:15-16`), `agent/anthropic_adapter.py`, `agent/gemini_native_adapter.py:956`(`while True`)
- (승계) 이 프로젝트(연구레포) `/Users/seobi/jinsup_space/CC/CLAUDE.md:16-18` 수정 완료(LangGraph 서술 → 자체 하네스 서술)
- (승계) Workflow 도구 부재 확인: `tools/WorkflowTool/`(부재), `constants/tools.ts:29,45`, `BackgroundTasksDialog.tsx:105`(ant-only 주석)
- (승계) 스킬예산 md 변환: `/Users/seobi/jinsup_space/CC/스킬예산-로스트인더미들.md`
- (승계) KV캐시/cache_control: `services/api/claude.ts` `addCacheBreakpoints():3062-3106`, `getCacheControl():603-663`
- (승계) 툴콜링 뼈대: `Tool.ts`(`call():379,description():386,inputSchema:394,checkPermissions:495`), `query.ts`(`query():219,queryLoop():241,while(true):305~1716`), `services/tools/toolOrchestration.ts`(`runTools():19,partitionToolCalls:95-116`), `services/tools/toolExecution.ts`(`classifyToolError():150,runToolUse():337,buildSchemaNotSentHint():578-598`)
- (승계) glob→grep→read(입장권 설계) 소스: `tools/GlobTool/prompt.ts`, `tools/GrepTool/prompt.ts`, `tools/FileReadTool/prompt.ts`(`MAX_LINES_TO_READ=2000`, `FILE_UNCHANGED_STUB`)
- (승계) Read→Edit readFileState 5겹: `tools/FileEditTool/prompt.ts:4-5`, `FileEditTool.ts:270,275-306,519-522`, `FileWriteTool.ts:198-216,281,332`, set 지점 5곳(`FileEditTool.ts:520`,`BashTool.tsx:404`,`FileReadTool.ts:842,1032`,`FileWriteTool.ts:332`)
- (승계) 결과 넛지 가족 소스: `TaskUpdateTool.ts:393,395-397`; `EnterPlanModeTool.ts:99`; `GlobTool.ts:48-50,192`; `WebFetchTool.ts:233`; `NotebookEditTool.ts:193`; `FileReadTool.ts:181,436,706-707,730`; `BashTool.tsx:530`; `toolExecution.ts:578-598`
- (승계) task_reminder 원문: `utils/messages.ts:3680-3699`, case `'task_reminder'`
- (승계) Playwright 렌더링 검증(part9 사례): 임시서버 `python3 -m http.server 8734`(PID `978`, 검증 후 kill), 스크린샷 4장(검증 후 전부 삭제)
- **[신규, part11]** 병렬 Explore 스폰 3층 소스: API스펙(모델능력) / 넛지 `constants/prompts.ts:310`("make all independent tool calls in parallel... Maximize use of parallel tool calls")+`tools/AgentTool/prompt.ts:86,151,242,248,257,264,271` / 실행기 `query.ts:953`, `services/tools/toolOrchestration.ts:91`(`partitionToolCalls`)+`:30`(`runToolsConcurrently`), `tools/AgentTool/AgentTool.tsx:1273`(`isConcurrencySafe() { return true; }`)
- **[신규, part11]** `constants/prompts.ts:310` 소속: `getUsingYourToolsSection()` 함수선언 `:269`, 호출부 `:569`(`getSystemPrompt` 조립기, 정적/캐시구역, BOUNDARY MARKER 앞), 서브에이전트 미해당 근거주석 `:325-328`("don't go through getSystemPrompt")
- **[신규, part11]** CC REPL모드(CC판 PTC) 소스: `tools/REPLTool/constants.ts`(`isReplModeEnabled():23-31`, `REPL_ONLY_TOOLS:37`={FILE_READ_TOOL_NAME, FILE_WRITE_TOOL_NAME, FILE_EDIT_TOOL_NAME, GLOB_TOOL_NAME, GREP_TOOL_NAME, BASH_TOOL_NAME, NOTEBOOK_EDIT_TOOL_NAME, AGENT_TOOL_NAME}), `tools/REPLTool/primitiveTools.ts:15`; 환경변수 `CLAUDE_REPL_MODE`, `USER_TYPE==='ant'`, `CLAUDE_CODE_ENTRYPOINT==='cli'`
- **[신규, part11]** OpenAI 공식문서: `https://developers.openai.com/api/docs/guides/function-calling`(원 URL `https://platform.openai.com/docs/guides/function-calling`에서 301 리다이렉트), PTC 전용가이드 `https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling`
- **[신규, part11]** Anthropic PTC 공식문서: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling`; WebFetch 대용량(59.2KB) 결과 persist 경로: `/Users/seobi/.claude/projects/-Users-seobi-jinsup-space-CC/c36aeba7-7619-425b-b98f-6585ccf6794d/tool-results/toolu_01BUqc2u5iPHdAwo7Q4BYHQR.txt`
- **[신규, part11]** PTC 공개 벤치마크 수치(Anthropic): BrowseComp/DeepSearchQA 검색벤치마크 `+11% 성능 / −24% 토큰`, 지출감사(20명 예산검사) 예시 토큰 `−90%`
- **[신규, part11]** OpenAI tool_search: `defer_loading: true` 필드, `gpt-5.4` 이상 전용
- 데이터소스 파일: `/Users/seobi/jinsup_space/research/memory/data2/conv2-01.part1.txt`~`part10.txt`(이전 라운드 입력), `/Users/seobi/jinsup_space/research/memory/data2/conv2-01.part11.txt`(이번 라운드 입력, 1389줄)
</content>
