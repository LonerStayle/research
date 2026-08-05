## Decisions

- (승계) 사용자의 "클로드코드 전체파악" 요청 → `/Users/seobi/jinsup_space/CC`(md_group 140개/51,351줄, html_group_v2 138개, src/ 1,904개 파일·301개 디렉토리) 전수 탐색, 4계층 아키텍처(엔트리 main.tsx → 엔진 query.ts/QueryEngine.ts → 도구 10단계 파이프라인 → Ink/React TUI). md 135개 전량 재검증(2026-07-07, 89개 파일·296건 교정). 최신커밋 `2222679`.
- (승계) "배치 병렬 3조 요건"(모델 1응답 내 복수 tool_use / 도구별 `isConcurrencySafe` / 하네스 `partitionToolCalls`) 소스검증 완료 → `배치-단독-개념-소스증명.md`.
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
- (승계) "임베딩/BM25/의도분류/고정워크플로우 4개 없나?" → 전수 grep+오탐검증 완료, 4개 전부 "없음" 확정. 관통철학: "전처리를 모델에게 위임"(검색=모델grep, 라우팅=모델도구선택, 오케스트레이션=ReAct루프) — 세션 전반 반복인용 해석틀.
- (승계) "유명한데 없는 것" 확장목록(부분확인수준): RAG파이프라인/대화요약메모리버퍼(compact가 대체)/Reflexion류 성찰누적루프/플래너-실행자강제분리 없음/동적few-shot없음/토큰레벨가드레일없음/세만틱캐싱없음/멀티암드밴딧·DSPy자동최적화없음.
- (승계) verification 에이전트 빌트인 존재 확인, 이중게이트(`feature('VERIFICATION_AGENT') && getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)`)로 기본비활성=Anthropic내부A/B전용.
- (승계) "LLM 별도호출 총정리" — 최종 확정: 4개 진입함수 기준 본류1+사이드16곳. 원가배분원칙: 값싼잡무=haiku, autocompact=메인모델, insights=opus고정.
- (승계) "LLM호출 다 도구없는 순수LLM이지?" → 확인, 정확함. 3분류: 도구없는순수LLM(대다수)/도구1개강제(웹검색)/진짜에이전트(Agent툴서브에이전트만).
- (승계) "TaskCreate 컨텍스트 주입 3경로" 확정 — ①즉시 tool_result ②주기적 task_reminder(`TODO_REMINDER_CONFIG={TURNS_SINCE_WRITE:10, TURNS_BETWEEN_REMINDERS:10}`) ③능동조회. "TaskUpdate 호출도 모델판단" 확인.
- (승계) 사용자가 새 상주 프로젝트(키움증권 AI PB 서비스) 브리프 제시 → CC 패턴 응용 트랙. `/draw-arch`로 "키움-AI-PB-클로드코드식-하네스-설계.md/.html" 완성, 🟩(CC소스검증)/🟦(설계제안) 2색 구분.
- (승계) hermes-agent "LangGraph supervisor" 오추천 자인·철회. 소스검증: langgraph/langchain 의존성 0건, 오케스트레이션=`while True`+`tool_calls`(ReAct). **결론: 프레임워크 없는 raw SDK 위 커스텀 하네스.** `/Users/seobi/jinsup_space/CC/CLAUDE.md:18` Edit 정정 완료.
- (승계) Coordinator Mode 재확인(`coordinatorMode.ts`): 정체성 통째교체, 도구 3개만(Agent/SendMessage/TaskStop), 워커=동일 서브에이전트 런타임.
- (승계) Workflow 도구 — `tools/WorkflowTool/` 디렉토리 자체가 현재 소스스냅샷에 부재, 배선만 남음(ant-only). "구버전 스냅샷 부재" vs "현재 활성 세션 실재" 이중근거 항상 구분.
- (승계) `/Users/seobi/jinsup_space/CC/스킬예산-로스트인더미들.md` 변환 완료.
- (승계) "ReAct 사이클 없이도 KV캐시 언제 갱신?" → `addCacheBreakpoints`(`services/api/claude.ts:3062-3106`) 확인: 캐시 브레이크포인트는 API 요청 1건당 정확히 1개, 항상 메시지배열 마지막.
- (승계) 슬래시커맨드 `/model` 2회 실행 — Sonnet 5 → Fable 5로 기본모델 변경(세션 상태 변경만).
- (승계, 프로젝트무관 일반론) "올드스쿨 툴콜링 순서 설계" 프레임 "프롬프트3곳+코드4곳+루프1개" 확립.
- (승계) "CC 기준 툴콜링설계 파악" 최종 대응표: 프롬프트①시스템=`services/api/prompts.ts`+`utils/systemPrompt.ts` / 프롬프트②도구설명=`tools/<이름>/prompt.ts` / 프롬프트③결과문구=각 도구 `mapToolResult` / 코드1계약=`Tool.ts` / 코드2실행기매핑=`tools.ts`+`constants/tools.ts` / 코드3루프=`query.ts:241 queryLoop` / 코드4검증에러=`toolExecution.ts` / API조립=`services/api/claude.ts:1235 toolToAPISchema`→`:1396 allTools` / tool_result짝맞춤=`utils/messages.ts:626`. 확장 3개: ①`stop_reason` 불신(콘텐츠필터 직접) ②`partitionToolCalls`(읽기전용병렬/쓰기직렬) ③도구=설명문+구현+권한+UI 미니모듈.
- (승계) Read→Edit `readFileState` 상태머신 5겹 장치 확정(사전경고/게이트1 미독차단/게이트2 mtime변경차단/성공후 자가갱신/Write에도 동일게이트). 정의: "안 읽은 파일 금지"가 아니라 **"지금 디스크의 그 버전을 본 적 없으면 금지"**.
- (승계) 결과 넛지 가족 A(성공넛지5종)/B(에러리다이렉트5종)/C(하네스힌트1종, `buildSchemaNotSentHint`) 3그룹 확정, `mapToolResult` 구현 도구 19개 grep 확인. 핵심통찰: **"에러 메시지는 예외 로그가 아니라 프롬프트다."**
- (승계) "넛지" 정의 — 탈러 『Nudge』(2008) 인용, "강제 없이 선택자유 유지한 채 유도". CC 맥락: 강제=에러(안읽은파일수정불가) vs 넛지=무시가능(TaskUpdate "Call TaskList now"). 근거: 방치리마인더 원문 "This is just a gentle reminder - ignore if not applicable".
- (승계) Playwright 렌더링 검증 패턴 확립(html 시각 확인 요청 시 임시 `python3 -m http.server`로 `file://` 차단 우회 후 스크린샷, 검증 즉시 스크린샷·`.playwright-mcp`·서버 전부 삭제).

**이하 part10 — round9 마지막 최우선 Open TODO(html 섹션제목 수정 확인메시지 미보고)를 이어서 완료, 이후 같은 문서(`도구호출-순서설계-하드소프트.md/.html`)에 대한 대규모 구조 재편·정정 다수, part10도 동일 패턴(마지막 Edit 완료 후 확인메시지 없이 종료)으로 마감.**

- **[신규, part10, 완료]** round9 최우선 TODO 해소 — part10 시작 즉시 html Edit 1건("전수는 아래 ⑤" → "전수는 바로 아래 \"③ 심화\"에")과 재오픈 완료 후, 사용자에게 3행 표(전/후)로 확인 메시지 전달. round9 넘어온 미보고 상태 완전 해소.
- **[신규, part10]** 사용자가 "L3 소프트 B" 트리(정적 안내=표지판 vs 동적 넛지=옆구리찌르기, ①대체지침·②탈출구·③결과넛지·④리마인더)를 직접 그려 제시 → md/html 양쪽 §04(소프트B) 도입부에 반영, "소프트 A(입장권설계 전신인 깔때기)도 같은 방식으로" 요청받아 3갈래 트리(비용경사/입출력사슬/니치선언) 신설. (이 시점 트리는 이후 두 차례 더 정정됨, 아래 참조.)
- **[신규, part10, 정정1]** 사용자 지적 "비용 경사 — 이렇게 비용 계산한게 어딨는데" → grep 검증(`cost|expensive|cheap|budget` in GlobTool/GrepTool/FileReadTool = 0건, FileReadTool의 `readImageWithTokenBudget`은 이미지 토큰버짓이라 무관) → "비용 경사" 표현 철회, **"출력 부피 경사"**로 정정. 실재하는 것은 출력량 상한: Glob 100개 잘림(`GlobTool.ts:50`) / Grep head_limit 기본상한(`GrepTool.ts:104-107`) / Read 2000줄+토큰상한(`FileReadTool.ts:181`). md·html 본문+SVG 라벨+변경이력 전부 반영.
- **[신규, part10]** 위 정정 직후, 사용자가 "설명문(description)이 대체 어디 있냐"는 혼란을 겪을 것을 예상해 어시스턴트가 **description의 정체 도해**를 자발 제공: `tools/*/prompt.ts`는 개발자 보관 장소일 뿐, `toolToAPISchema`(`claude.ts:1235`)가 매 API 요청의 `tools` 배열에 실어 모델에게 전달("매 요청의 메뉴판" 비유). 표로 4요소 분류: 니치선언·입력계약=description(+input_schema)에 있어 "읽어서 앎" / 출력 부피 상한=구현코드에 있어 "겪어서 앎" / 출력→입력 연결=**어디에도 안 적혀있음**, 모델이 tool_result 보고 스스로 추론. "깔때기 설계"의 정확한 의미를 "순서를 적어놓은 게 아니라 각 도구 니치·입력조건·반환물 모양을 깎아놔서 합리적 모델이면 그 순서로 이을 수밖에 없게 만든 것"으로 재정의(레고 블록 비유).
- **[신규, part10, 대규모 재편]** 사용자 지적 "레이어1 물리 층은 아예 존재를 없애라;; 저건 당연한소리를 하고있어" → **물리·하드·소프트 3층 → 하드·소프트 2층**으로 문서 전체 재편(md+html 수십 건 Edit). 제목("도구 호출 순서 설계 — 물리·하드·소프트 3층 규칙"→"…하드·소프트 2층 규칙"), h1("벽·차단기·표지판"→"차단기·표지판"), §00 스펙트럼표(물리 행 삭제), 코디네이터·디퍼드로딩 섹션 통삭제(디퍼드는 §03-1 하네스힌트 배경설명 한 줄로만 잔존), §번호 전체 재정렬(L3소프트A §03→§02, L3소프트B §04→§03, §04-1→§03-1), 결정 흐름 2분기로 축소("아예 못쓰게"분기 삭제, "사고면 하드/비효율이면 소프트"만 잔존), 키움 표에서 물리 행 삭제(어시스턴트 자체 요약 보고 기준).
- **[신규, part10, 정정2]** 물리층 삭제 정리 도중 어시스턴트가 **자발적으로** Grep 스키마 원문(`GrepTool.ts:40-102`)을 재확인하다가 발견 — "Glob 출력 → Grep의 glob 파라미터로 연결"이라는 기존 서술이 오류임을 스스로 포착(사용자 지적 아님). 확인: Grep의 `glob` 파라미터는 `"Glob pattern to filter files (e.g. \"*.js\") - maps to rg --glob"` — **패턴 문법**이지 Glob 도구의 출력이 아님. Grep은 Glob 없이 완전 독립 동작(`path` 기본값=cwd). "3단 사슬(Glob→Grep→Read)"을 **Y자 합류**(Glob 출력·Grep 출력 둘 다 → Read의 `file_path`로만 합류, Glob→Grep 배선은 없음)로 정정. md·html 전체 반영 + 변경이력 기록.
- **[신규, part10]** 사용자 질문 "깔때기 설계라고 하기엔 이름이 애매한데.. grep은 은은하게 뭐가 필요하다고 적혀있는거지?" → 3도구 필수 파라미터 확인(`GrepTool.ts:35-40` pattern만 필수/나머지 optional, `GlobTool.ts:28` pattern만 필수, `FileReadTool.ts:229` file_path 절대경로 필수) → 정정: **Grep엔 "은은한 요구"가 없음**(무전제 도구, pattern은 모델이 지어냄) — 은은한 요구가 적힌 건 **Read**(`file_path`="이미 경로를 알고 있어야 한다"는 함의, 경로는 지어낼 수 없어 검색 출력에서만 조달 가능, 여기서 순서가 창발). `AskUserQuestion`으로 "소프트A — 깔때기 설계" 개명안 질의(옵션: 입장권 설계(추천)/조달 난이도 계단/무전제→유전제 배치/깔때기 유지+주석) → 사용자 **"입장권 설계 (추천)"** 선택. md·html 전수(grep으로 "깔때기" 전 위치 확인 후) **"입장권 설계"**로 개명, 정의문 신설: "입장권=각 도구의 필수 파라미터. 공짜 입장권(모델이 지어낼 수 있는 패턴) 도구부터, 비싼 입장권(조달해야 하는 절대경로) 도구로 계단이 놓여 순서가 저절로 나온다." 근거 라인 명시(`GrepTool.ts:35-40`·`GlobTool.ts:28`·`FileReadTool.ts:229`). 변경이력 "(개명)" 기록.
- **[신규, part10]** 사용자가 자기 이해를 직접 문장으로 제시("소프트 규칙 - 자연스럽게 연결로 각자 도구 설명을 적어서 다른 도구를 언급하지 않고… LLM이 판단해서 사용하게끔") → 어시스턴트 "거의 정확" 확인 + 한 군데 다듬음: "다른 도구를 언급하지 않고"는 절반만 사실 — 순서 지시는 0건이나, **탈출구**("열린 탐색이면 Agent로")와 **우회금지**("NEVER invoke grep via Bash")는 있음. 최종 정의문: "각 도구 설명은 자기 니치와 필수 입력만 선언한다. 순서 언급은 없고, 입력 조달처는 LLM이 스스로 판단해 연결한다 — 다른 도구 언급이 있어도 순서가 아니라 탈출구/우회금지 안내다."
- **[신규, part10, 재분류]** 사용자 질문 "소프트 B에 있는 대체지침이란 표현이 맞나?" → 어시스턴트가 "① 대체지침"과 "② 탈출구"가 **같은 정책의 두 톤**(시스템프롬프트=권장형 "instead of" / 도구설명문=금지형 "NEVER")임을 발견, 개명안 `AskUserQuestion` 질의(Bash 대체 지침(추천)/전용도구 유도/유지+관계만 명시) → **사용자가 이 tool_use를 거부**("The user doesn't want to proceed... rejected")하고 대신 직접 재프레이밍 제시: "그럼 저건 소프트 규칙에서 제외해서 별도의 기준으로 잡아야되지않나.. 도구 주의사항? 같은?" → 어시스턴트 즉시 수용, **"대체지침"을 소프트 B에서 완전 제외**하고 **신규 §04 "(별도 기준) 도구 주의사항 — 순서가 아니라 수단 선택"** 섹션으로 분리 이동(md 먼저 완료, html 진행 중 transcript 종료 — 아래 Open TODO 참조). 소프트 B는 **3갈래(탈출구/결과넛지/리마인더)로 축소**. §번호 재조정: §04(도구주의사항, 신규)→§05(결정흐름, 재배치)→§06(프롬프트 한국어 대역, 원래 §05였던 것). html에서도 "① SUBSTITUTE 대체 지침" 패널 삭제, "④ REMINDER"→"③ REMINDER", "③ 심화 — 결과 넛지 가족 전수"→"② 심화 — …"로 번호 당김.
- **[신규, part10, 미완료]** 위 재분류 작업 도중 html의 신규 §05 "도구 주의사항" 섹션 삽입(구 "06 결정 흐름" 주석/헤더 자리를 재사용) 및 SVG 라벨 텍스트("입장권 설계 + 대체/탈출구/넛지/리마인더" → "…+ 탈출구/넛지/리마인더") Edit 2건이 도구결과 레벨에서 완료됐으나, **어시스턴트가 사용자에게 완료 확인/보고 메시지를 주지 않은 채 transcript 종료**(round9과 동일한 컷오프 패턴 재발). html에서 "결정 흐름" 섹션 자체의 새 num/헤더가 온전히 재삽입됐는지, §06(프롬프트 대역) 쪽 html 섹션 주석 번호가 최종적으로 어떻게 정리됐는지는 트랜스크립트 truncation으로 **미확인** — 다음 라운드에서 파일을 직접 grep/Read해 실제 최종 상태부터 재확인할 것.

## Open TODOs

- **[신규, 최우선, 미완료]** part10 마지막 시점 — html §05 "도구 주의사항" 섹션 삽입 + SVG 라벨 정리 Edit 2건은 도구결과상 완료됐으나, 어시스턴트가 사용자에게 완료 확인 메시지를 주지 않은 채 대화 종료. 다음 라운드는 이 확인 메시지부터 시작하되, 먼저 `grep -n "L1\|L2\|L3\|물리\|3층\|깔때기\|비용 경사\|대체지침" /Users/seobi/jinsup_space/CC/도구호출-순서설계-하드소프트.html /Users/seobi/jinsup_space/CC/도구호출-순서설계-하드소프트.md`로 잔여 stale 참조·§번호 정합성을 재검증한 뒤 보고할 것 (round9 TODO는 part10에서 이미 해소·재확인 불필요).
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
- (승계, 정보용, 유효) Workflow 도구 — "src 스냅샷엔 배선만 남고 구현부재+ant전용게이트"와 "현재 활성 세션엔 실재하는 도구" 두 근거 항상 구분.
- (승계, 정보용, 유효) KV캐시 갱신 트리거="API요청 1건당 마커 1개, 항상 마지막 메시지" — 도구유무 무관 확정.
- (승계, 정보용, 유효) "CC 기준 올드스쿨 툴콜링 뼈대" 최종 대응표 + "결과 넛지 3가족(A/B/C)" 확정, 재질문 시 이 기준.
- **[갱신, part10, 정보용, 유효]** `도구호출-순서설계-하드소프트.md/.html`의 최종(part10 종료 시점) 구조 — **하드·소프트 2층**(물리층 삭제), §02소프트A=**입장권 설계**(구 깔때기, glob→grep→read는 Y자 합류이지 3단 사슬 아님), §03소프트B=문구장치 3갈래(탈출구/결과넛지/리마인더, 대체지침 제외됨), §03-1=결과넛지가족전수, §04(신규)=도구 주의사항(순서 아닌 수단선택, 대체지침이 여기로 이동), §05=결정흐름, §06=프롬프트 한국어 대역. 재질문 시 이 최신 구조 기준으로 답할 것(3층/깔때기/비용경사 등 구 표현은 전부 폐기됨).
- (승계, 정보용, 유효) "소프트B와 넛지의 관계" — 넛지는 소프트B의 부분집합(정적안내 vs 동적넛지, 구분기준=타이밍)으로 확정 — 단, part10에서 소프트B 갈래 수 자체가 4→3으로 줄었으므로(대체지침 제외) 이 구분이 현재도 "탈출구=정적" "결과넛지+리마인더=동적"으로 유지되는지는 html 최종본 재확인 필요(위 최우선 TODO에 포함).

## Constraints/Rules

- 이 워크스페이스(연구 레포)의 탐색 작업은 프로젝트 CLAUDE.md 지침에 따라 Explore 서브에이전트에 위임하고, 실행/작성은 메인에서 직접 수행.
- 새 분석 문서는 기존 도감류 문서 옆에 자매 문서로 작성. 기계별 절대경로가 본질적으로 포함된 일회성 스냅샷 문서는 `~` 중립화 예외.
- 서브에이전트/워크플로우 결과 원본 산출물은 절대 그대로 tail/Read 하지 않는다 — 완료 알림의 `<result>` 요약 또는 python 파싱 요약만 사용.
- 모든 기술적 주장은 로컬 재구성 소스(`~/jinsup_space/CC/src`)에서 grep/Read로 직접 검증. 추측·과장 금지 — 확인 안 된 부분은 "소스에서 확인 못함"/⚪ 마커 또는 "부분확인 수준"으로 정직 표기. 다른 레포에 대한 주장도 동일 엄격도로 검증.
- 항상 한국어로 응답.
- 사용자는 밀도 높은 설명보다 구체적 시나리오/비유를 선호, 사용자가 반문·재확인·불만을 던지면 어시스턴트가 즉시 스스로 오류/누락을 인정하고 정정하는 패턴이 세션 표준 — part7까지 3회, part8 1회, part9 2회, **part10에서 최소 4회 추가**("비용 경사" 근거없음 인정·정정 / "L1 물리 층 당연한 소리" 인정·통삭제 / "깔때기 이름 애매" 인정·개명 / "대체지침 표현" 인정·재분류). 매번 근거코드 우선제시 후 정리하는 순서 일관 유지.
- **[신규, part10]** 사용자 지적이 없어도 어시스턴트가 무관한 작업(html 잔여참조 정리) 도중 **자발적으로 스키마 원문을 재확인해 스스로 이전 주장의 오류(Glob→Grep 배선 주장)를 발견·정정**하는 사례 등장 — 사용자 반문 없이도 소스 재검증을 습관적으로 반복하는 패턴으로 확장.
- **[신규, part10]** 문서 섹션/개념 **개명(rename)** 판단은 `AskUserQuestion`으로 옵션 제시 후 사용자 선택("입장권 설계" 채택 사례) — 전역 CLAUDE.md의 "결정/선택은 AskUserQuestion 우선" 원칙이 본 세션에서 처음 명시적으로 적용됨.
- **[신규, part10]** 단, `AskUserQuestion`의 선택지가 사용자의 실제 의도(카테고리 자체를 재구성하려는 의도)와 다르면 **사용자가 tool_use 자체를 거부**하고 자유서술로 재프레이밍할 수 있음("대체지침" 개명 질의 거부 → "도구 주의사항"이라는 새 카테고리 직접 제안) — 이 경우 어시스턴트는 즉시 사용자 프레임을 그대로 수용해 실행하는 것이 표준.
- src 스냅샷은 구버전임을 사용자가 명시적으로 인지 — 신/구 대조 시 4색 범례(🟢🟡🔴⚪) 관례. "구버전 스냅샷 vs 현재 활성 세션의 실제 툴셋" 이중근거 구분을 절대 섞지 않고 각각 명시.
- 전수조사(`grep -rn` 전체 호출처/렌더 스위치 스캔) 후 표로 요약하는 방식이 반복 확립된 답변 포맷.
- 대규모 전수조사 요청 시 Workflow 도구를 백그라운드로 발사해 다수 서브에이전트 병렬 동원, 단 소규모 조사(part7~part10 모두)는 메인이 직접 grep 반복으로 처리.
- md/html 짝꿍 문서에 사용자가 이해 못한 용어를 반영 요청하면 기존 절 머리에 "용어 안내" 소절 삽입, 문서 자체의 표현·구조를 사용자가 지적한 경우(넛지 가족 누락, 섹션번호 어색함, 비용경사 근거없음, 물리층 무의미, 깔때기 이름 애매, 대체지침 재분류)에만 문서 Edit으로 반영 — 채팅 즉답과 문서수정 구분 유지.
- 세션 전반의 해석틀 "전처리를 모델에게 위임"이 반복 재사용됨. **[part10]** "도구 순서 설계"의 하위원칙이 재차 정교화됨: "순서 강제 문구는 어디에도 없다 → 각 도구의 필수 입력(입장권) 조달 난이도 차이가 만드는 창발적 순서 → 순서 자체보다 '수단 선택 규칙(도구 주의사항)'과는 다른 축임을 명확히 분리."
- 모델 배분 원가 원칙("값싼 잡무=haiku, 품질중요=큰모델")이 소스로 확정 — 향후 "왜 이 모델을 쓰나" 질문에 1차 가설로 적용 가능.
- 세션 성격 확장 — 순수 "CC 내부 리버스엔지니어링"에 더해 "CC에서 검증한 패턴을 키움증권 AI PB 설계에 응용" 트랙 병행, 🟩/🟦 2색 구분 관례 유지.
- "다른 레포(hermes-agent 등)의 실제 구현" 주장도 2차 문서를 믿지 말고 소스 자체를 grep/Read로 직접 검증, 불일치 시 소스 우선하고 문서 수정까지 진행.
- "일반론(프로젝트/소스 무관)" 질문과 "이 프로젝트 소스 기준" 질문을 명확히 구분 표기.
- 문서(html)의 시각적 렌더링을 사용자가 의심하면 설명이 아니라 Playwright로 직접 렌더링 후 스크린샷 확인, 검증 즉시 산출물(스크린샷·로그·임시서버) 전부 삭제해 레포에 잔여물 안 남김.
- 조사로 새로 발견한 내용을 채팅 답변에만 담고 기존 산출 문서에 반영하지 않으면 사용자가 재지적함 — 조사 결과는 답변 직후 관련 문서에도 즉시 증보 반영하는 것이 표준.
- **[신규, part10]** 문서 내 표현/구조가 **소스 근거 없이 어시스턴트의 해석 프레임(비유·은유)으로 슬쩍 들어가는 것**을 사용자가 민감하게 잡아냄("비용 경사"처럼 코드에 없는 계산을 있는 것처럼 서술한 사례) → 이후 어시스턴트가 은유/프레임을 도입할 때마다 "이건 제 해석이고 코드에 있는 건 X뿐"이라는 식으로 **해석과 소스검증분을 문장 단위로 분리 표기**하는 습관이 강화됨(예: "※ 비용을 계산하는 코드는 없음 — 싸다/비싸다는 반환 토큰량에 대한 해석").

## Pending user asks

- **[신규, 최우선, 사실상 완료·확인만 미보고]** part10 마지막 — 사용자의 "대체지침을 소프트 규칙에서 제외해 도구 주의사항으로 분리하자"는 요구에 따라 md는 완료(§04 신설, §번호 재정렬), html도 §05 도구주의사항 섹션 삽입 + 라벨 정리 Edit 2건을 도구결과상 완료했으나, **사용자에게 완료를 알리는 어시스턴트 텍스트 응답 없이 transcript 종료**. 다음 라운드는 이 확인 메시지(및 html 최종 상태 재검증)부터 시작.
- (해결됨, part10) round9의 "⑤ 결과 넛지 가족 전수 섹션 제목 수정 확인 메시지" 요청 — part10 시작 즉시 완료·보고. 재확인 불필요.
- (해결됨, part10) "비용 경사 근거", "L1 물리 층 삭제", "깔때기 이름 애매/입장권으로 개명", "대체지침 재분류" — 전부 사용자 요청대로 처리 완료(마지막 html 반영분만 확인 메시지 미보고, 위 최우선 항목 참조).
- (부수적, 매우 낮은 우선순위) Open TODOs의 문서 반영 육안검증 항목들, 기술부채 특정 카테고리 심화, 코디네이터 아키텍처 별도 문서화, 키움 설계도 후속 2건 — 전부 사용자가 명시적으로 재요청한 것이 아니라 어시스턴트가 제안만 한 오픈 옵션.
- (승계, 매우 낮은 우선순위, 진위불명) "ngClearLatched" 등 정체불명 삽입 텍스트 — 재언급 시 무엇에 대한 것인지부터 재확인.

## Exact identifiers

- 워크스페이스 루트: `/Users/seobi/jinsup_space/CC`; 최근커밋 `2222679`
- (승계) 산출 문서(전 라운드까지): `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md`, `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html`, `/Users/seobi/jinsup_space/CC/배치-세계-전수도감.md`(244줄), `md_group-교정-변경내역.md`, `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`(+`.html`), `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md/.html`, `/Users/seobi/jinsup_space/CC/큐웨이크-엔터없는-진입-소스분석.md`, `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md/.html`, `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md/.html/-전체287건.json`, `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md/.html`, `/Users/seobi/jinsup_space/CC/키움-AI-PB-클로드코드식-하네스-설계.md/.html`(작성일 2026-07-18), `/Users/seobi/jinsup_space/CC/스킬예산-로스트인더미들.md`
- **[갱신, part10]** `/Users/seobi/jinsup_space/CC/도구호출-순서설계-하드소프트.md`(작성일 2026-07-22, part9~part10 증보/재편) + `/Users/seobi/jinsup_space/CC/도구호출-순서설계-하드소프트.html`(동일 구조 visual-explainer). **최종(part10 종료 시점) 구조**: 제목 "도구 호출 순서 설계 — 하드·소프트 2층 규칙", h1 "차단기·표지판으로 설계한다"(html), §00 스펙트럼(하드/소프트 2행), §02 소프트A=**입장권 설계**(glob→grep→read, Y자 합류), §03 소프트B=문구장치 3갈래(탈출구/결과넛지/리마인더), §03-1 결과넛지가족전수, §04(신규) 도구 주의사항(순서 아닌 수단선택, 대체지침 이곳으로 이동), §05 결정흐름, §06 프롬프트 한국어 대역. 변경이력(모두 날짜 `2026-07-23`): (정정1)"비용 경사"철회→"출력 부피 경사" / (구조변경)L1 물리층 삭제→하드·소프트 2층 / (정정2)"Glob→Grep glob파라미터"배선 주장 철회→Y자 합류 / (개명)"깔때기 설계"→"입장권 설계"(AskUserQuestion 채택) / (재분류)"대체지침"을 소프트B에서 제외→§04 도구주의사항.
- 입장권 설계 근거 라인: `GrepTool.ts:35-40`(pattern만 필수, path/glob optional), `GlobTool.ts:28`(pattern만 필수), `FileReadTool.ts:229`(`file_path: "The absolute path to the file to read"`, 필수)
- 출력 부피 상한 근거: `GlobTool.ts:50`(100개 잘림), `GrepTool.ts:104-107`(head_limit 기본 상한 주석), `FileReadTool.ts:181`(2000줄+토큰 초과 에러 메시지)
- Grep 스키마 원문(`GrepTool.ts:30-102` 부근): `pattern`(필수, "The regular expression pattern to search for in file contents"), `path`(optional, "File or directory to search in (rg PATH). Defaults to current working directory."), `glob`(optional, `'Glob pattern to filter files (e.g. "*.js", "*.{ts,tsx}") - maps to rg --glob'`), `output_mode`/`-B`/`-A`/`-C`/`context`/`-n`/`-i`/`type`/`head_limit`
- cost/expensive/cheap/budget grep 결과: `tools/GlobTool/`·`tools/GrepTool/`·`tools/FileReadTool/`에 매칭 0건(단 `FileReadTool.ts:867-1136`의 `readImageWithTokenBudget`은 이미지 토큰버짓이라 도구 순서와 무관, 오탐 아님으로 별도 확인)
- 도구 주의사항(§04) 근거: 시스템프롬프트 권장형 5줄(`constants/prompts.ts:293-299` 부근, "To read files use Read instead of cat, head, tail, or sed" / "To edit files use Edit instead of sed or awk" / "To create files use Write instead of cat with heredoc or echo redirection" / "To search for files use Glob instead of find or ls" / "To search the content of files, use Grep instead of grep or rg") vs 도구설명문 금지형("NEVER invoke grep or rg as a Bash command", GrepTool 설명문)
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
- 데이터소스 파일: `/Users/seobi/jinsup_space/research/memory/data2/conv2-01.part1.txt`~`part9.txt`(이전 라운드 입력), `/Users/seobi/jinsup_space/research/memory/data2/conv2-01.part10.txt`(이번 라운드 입력, 811줄)
