## 단계 2

<summary>

1. Primary Request and Intent:
   - **세션 대주제**: `/Users/seobi/jinsup_space/CC`(Claude Code 내부를 소스코드로 역공학하는 리서치 프로젝트) 전체 파악. 최초 요청("클로드코드 전체파악해봐라") 이후 배치 파티셔닝 → 컨텍스트 주입 4트랙 → 훅/MCP지시/캐시경계 → ToolSearch 지연로딩 → **큐 웨이크(엔터 없는 진입 경로)** → **XML vs 마크다운** → **0번 유령 메시지·CLAUDE.md 캐싱·스킬 목록 타이밍** → **system-reminder 태그 전수 조사**로 이어지는 연쇄 딥다이브. 전 구간에서 "주장은 반드시 grep/Read로 소스 검증"이라는 프로젝트 CLAUDE.md 규율을 일관 적용.
   - **(직전 요약 시점 미완이었던 항목, 이번 구간 첫머리에서 완료)**: `toolsearch-생애주기-소스분석.md`/`.html`에 최신 논의 반영 + "ReAct 사이클 아닌 경우도 엔터가 방아쇠인가?" 질문에 최종 답변 전달 — **완료**. 답: 원칙상 맞지만 예외로 "큐 웨이크"(문③)가 있다는 결론과 소스 사슬(`enqueuePendingNotification`, `messageQueueManager.ts`, `useQueueProcessor.ts`) 제시, md에 §08 6문항 Q&A 추가, html에 07 섹션(문 3개 다이어그램 등) 추가.
   - **큐 웨이크 단독 심화 요청**(완료): "그 툴서치를 떠나서 큐 웨이크에 관해서 적어주라, ReAct사이클 제외해서" → 신규 문서 `큐웨이크-엔터없는-진입-소스분석.md` 작성(처음엔 4경로: 백그라운드완료/Stop훅차단/원격입력/스케줄). 이어 "서비스 이용자 입장에서 구체 케이스 추가해줄래?" → §06(사람 체감 시나리오 4개) 추가. 이어 **"저 4경우빼고는 없는건가"** → 전수 재조사 결과 **실제로는 6개**(⑤비동기 에이전트 결과 재진입, ⑥고아 권한 응답 추가 발견 + ①이 "완료알림/진행중경고/원격상태변화" 3갈래로 세분화됨을 확인) — 문서 전체 갱신 완료.
   - **"왜 마크다운이고 XML이 아닌가?" 질문 체인**(완료, 사용자 반박으로 재정렬): 최초 답변에서 4가지 이유(①조립안전성 ②닫는태그비용 ③태그희소성=신호강도 ④출력일관성) 제시. 사용자가 "1번은 xml로 해도 문제없지않나" 반박 → 어시스턴트가 ①을 **기각 인정**, 논거를 "내용충돌회피(신) > 태그희소성 > 토큰/유지보수" 순으로 재정렬.
   - **0번 유저프롬프트 + 엔터 필요성 질문 체인**(완료, 다회 반박·정정 포함):
     - "0번에 CLAUDE.md 들어가고, 엔터 쳐야 스킬목록/도구목록 들어가나?" → 유령메시지(CLAUDE.md)는 엔터와 무관(매 API호출 재생성), 스킬/도구 목록은 "수집 지점"(턴시작+사이클꼬리) 단위이고 엔터는 그 수집을 여는 여러 문 중 하나일 뿐이라고 답변.
     - "클로드.md는 시스템프롬프트 다음 첫 유저프롬프트에만 들어가는거 아니야?" → **위치는 사용자 말이 맞음**(항상 messages[0]) 인정, 다만 "한 번 박제"가 아니라 **매 호출 같은 자리에 재인쇄**되는 것(`prependUserContext`가 `query.ts:655` API 호출 인라인에 박혀 사이클마다 재실행)이라 정정, `/login` userEmail 변화·자정 날짜 변화 2건을 재인쇄의 실측 증거로 제시.
     - "CLAUDE.md가 바뀔때마다 들어가는거였어?" → **어시스턴트 자가 정정**: 직전에 "수정하면 다음 호출부터 반영"이라 했던 것이 **틀렸음**을 인정. `getUserContext`가 `memoize`(context.ts:155)돼 있어 세션 첫 호출 때 한 번만 읽고 그 뒤론 캐시된 문자열 재인쇄. 캐시 무효화는 `/clear`·수동 `/compact`·auto-compact 후처리 3곳뿐. 근거로 `constants/common.ts:17-23` 주석("stale date after midnight vs. entire-conversation cache bust — stale wins") 인용해 "동결(0번)+꼬리델타(변경분)" 설계 철학 규명.
     - "거기에 스킬목록이라던가 그런건 안들어가지?" → 맞음, `getUserContext` return은 `claudeMd`+`currentDate`(신버전은 +userEmail)뿐(context.ts:184-188). 스킬/도구/에이전트 목록을 유령메시지에 안 넣는 이유 = 넣으면 세션 중 변경마다 0번 바이트가 바뀌어 대화 전체 KV캐시가 깨지기 때문(캐시 설계상 필연으로 결론).
     - "스킬목록은 어느타이밍에? 첫메시지 엔터치는순간?" → 기본 시나리오에선 맞음(`getSkillListingAttachments`, attachments.ts:2661-2751 확인) — 첫 수집 지점에서 `sentSkillNames`(agentId별 Set)가 비어있으면 전체 발행(`isInitial:true`), 이후는 델타만. 단서 3개: Skill툴 없는 에이전트엔 미발행/`--resume`시 `suppressNext`로 첫 발행 억제/컨텍스트 1%+스킬당 250자 예산. deferred도구는 "대화이력 스캔"으로 장부 관리, 스킬은 "프로세스메모리 Set"으로 관리한다는 설계 차이도 짚음.
   - **"CLAUDE.md는 왜 시스템프롬프트가 아니라 0번에?" 질문**(완료): 소스에 명시적 "왜" 주석 없어 근거강도순 정리 — 래퍼 문구 자체가 "참고자료" 어조라는 힌트, 이유①권위계층분리(system=제작자규칙 vs CLAUDE.md=반입콘텐츠, 인젝션벡터 방지, 가장 유력한 추론) 이유②서브에이전트 모듈성(`runAgent.ts:381`, 소스로 확인) 이유③글로벌캐시조각방지(부분적) 이유④채널일관성(전부 isMeta user 메시지).
   - **system-reminder 태그 전수 조사 체인(핵심, 진행 중)**:
     - "스킬목록·툴서치 내용은 다 system-reminder로 감싸나?" → 대부분 그렇다, messages.ts 렌더 스위치 62곳 래핑 확인. 예외 3개 최초 제시: ①ToolSearch 결과(tool_result 채널, tool_reference 블록이라 애초에 래핑 대상 아님) ②queued_command(당시엔 "안 감싼다"로 오답) ③스킬 본문(SkillTool.ts, 안 감쌈).
     - "시스템 리마인더 종류 다? + 안 감싸지만 isMeta=true인 것도?" → python으로 messages.ts 렌더 스위치 전수 스캔, **WRAP 47종/6계열** 표 작성(목록·델타/메모리·규칙/훅출력/상태알림/IDE·파일컨텍스트/모드·기타) + **plain(안 감쌈) 목록**도 나열. 이 과정에서 **queued_command 정정**: 실제론 래핑은 하되 `isMeta`만 조건부(사람이 미드턴에 친 메시지는 화면에 보이도록 isMeta 생략, 시스템생성은 isMeta:true) — 직전 답변의 "②안감싼다" 오류를 스스로 정정. 별도로 messages.ts 밖에서 `isMeta:true`를 직접 만드는 곳 전수(SkillTool.ts:1104 스킬본문/FileReadTool.ts 887,942,1013 이미지·PDF/processSlashCommand.tsx 등 슬래시커맨드 확장·비동기결과 재진입/api.ts:470 유령메시지/query.ts 등 합성메시지 — 위치만 확인) 제시.
     - **"시스템 리마인더인데 어태치먼트가 아닌것도 있지않나? 왜빠졌어"**(직전 구간 마지막에 답변 완료) → 어태치먼트 스위치 밖의 system-reminder 생성처 grep 전수 조사, **3계열 발견**: ①인라인형(tool_result 문자열 안에 직접 삽입 — FileReadTool.ts:706-707 빈파일/오프셋경고, :730 멀웨어지침 상시경고) ②큐 선포장형(hooks.ts:238, Stop훅 차단에러가 큐에 넣기 전에 이미 `wrapInSystemReminder`로 포장됨) ③특수목적 직조립형(memdir/memoryAge.ts:52 메모리 신선도경고, sideQuestion.ts:61 사이드질문포장, commands/brief.ts:108-114 brief모드 인라인랩, api.ts:463 유령메시지). 덤으로 태그를 **벗기는 소비자**(transcriptSearch.ts:117/queryHelpers.ts:432/VirtualMessageList·messageActions — "Claude context, not user-visible")도 발견해 "system-reminder는 모델전용 채널, 사람 표면에선 전부 제거됨"을 재확인. 3층 지도(메시지레벨/인라인레벨/선포장레벨)로 정리.
   - **(진행 중, 미완료 — 세션 최종 미해결 요청)**: **"총정리해주라 시스템 리마인드에 들어가는것들(어태치먼트는 그냥 묶어서 어태치먼트라 해주고) 그리고 아닌것이지만 isMeta==true인것들"** — 이 구간 마지막 유저 메시지이며, 아직 어시스턴트 응답 없이 구간 종료.
   - **불변 제약 (전체 세션 유지)**: 항상 한국어로 응답. 모든 주장은 grep/Read로 소스 검증 후 답할 것(프로젝트 CLAUDE.md 지침). 추측·과장 금지, 미확인 부분은 "소스에서 확인 못함"으로 표기. 문서는 `~` 중립/상대경로 사용(세션인풋 계열 MD만 예외, 문서 머리에 명시). HTML에 유저 PC 절대경로 하드코딩 금지.

2. Key Technical Concepts:
   - **(이전 라운드, 완전 규명 완료 — 압축 유지)**: 배치 파티셔닝(`partitionToolCalls` reduce, safe/unsafe 병합규칙) · 0번 유령 vs 정주민 델타 어태치먼트(skill/deferred/agent/mcp) 구분 · rules 지연주입(frontmatter `paths:` → Read트리거Set → 사이클꼬리 수집 → `nested_memory`) · 수집(사이클꼬리, +)과 전처리(다음사이클머리, budget→snip→microcompact→collapse→autocompact, −) 구간 분리 · frontmatter 2단구조(값싼색인 상시/비싼본문 방아쇠) 공통패턴 · 훅 실행주체=하네스(`getHooksSection()` 3문장 상시안내, `<user-prompt-submit-hook>` 태그는 소스 1회 언급뿐인 구버전 잔재) · MCP지시 조립+2배달모드(구형uncached/`mcp_instructions_delta`) · `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 캐시경계(앞=global, 뒤=per-session) · **ToolSearch 지연로딩 5단계 생애주기**(분류→고지→검색→영수증→재조립, `isDeferredTool`/`tst`·`tst-auto`·`standard` 3모드/점수표 BM25아님-필드가중치 손코딩/`tool_reference` 영수증/대화이력스캔 상태관리/lost-in-the-middle 4중안전망+unknown-unknowns 잔여구멍) · src-대조 4색마커(🟢🟡🔴⚪, 신규도구 4종 Workflow·Artifact·ReportFindings·ScheduleWakeup).

   **큐 웨이크 — 엔터 없이 대화가 전진하는 6개 경로 (이번 구간 확정)**
   - 대화를 여는 "문"은 3개: ①유저 엔터(턴시작 수집) ②사이클 꼬리(ReAct 진행 중 도구실행 직후, 자동) ③큐 웨이크(유휴 세션에 큐가 채워지면 `useQueueProcessor`가 `isQueryActive===false && queue not empty`일 때 자동으로 턴 시작, `useQueueProcessor.ts:48-60`).
   - `QueuePriority`(`textInputTypes.ts:178`) 3단: `now`(도구 중단·즉시)/`next`(도구 끝난 뒤 API왕복 사이, `SleepTool` 웨이크)/`later`(턴 끝난 뒤 새 쿼리로 처리). 유저입력=`next`류, 시스템알림=`later`류라 "유저 입력이 시스템 메시지에 굶주리지 않게" 설계.
   - **큐에 엔터 없이 넣는 손 6개** (`enqueue`/`enqueuePendingNotification` 전수 grep 기준): ①백그라운드 태스크 알림(1초 폴링 `POLL_INTERVAL_MS`, 완료+진행중경고("interactive prompt에 막힘")+원격상태변화 3갈래, `LocalMainSessionTask.ts:262`/`LocalShellTask.tsx:89,166`/`RemoteAgentTask.tsx` 4곳) ②Stop훅 차단(`hooks.ts:238`, exit 2 시 에러가 이미 system-reminder로 포장돼 큐잉) ③원격기기 입력(bridge/CCR, `flushGate.enqueue`) ④스케줄 작업(isMeta 시스템생성 프롬프트, `processUserInput.ts:143`) ⑤비동기 에이전트 결과의 숨은 프롬프트 재진입(`processSlashCommand.tsx:126-133`, `mode:'prompt'`+`isMeta:true`로 재큐잉 — 스케줄 작업의 실제 배관이 이 경로임도 확인) ⑥고아 권한 응답(`orphaned-permission` 모드, headless/원격 승인 UI에서 뒤늦은 승인이 멈춘 tool_use 재개, `print.ts:5270-5298`).
   - MCP 연결/해제 같은 환경변화는 스스로 큐에 못 들어감(풀 방식) — 다음 문이 열릴 때 편승만 함. 유휴+빈큐=완전정지.

   **마크다운 vs XML 분업 (이번 구간, 사용자 반박으로 재정렬)**
   - 소스 확인 사실: `constants/xml.ts`에 XML 태그 20여개 상수 관리, 산문지시=마크다운(`# System` 헤더+불릿)/경계표시필요 주입화물=XML(`<system-reminder>` `<task-notification>` `<remote-review>` 등)로 분업. 주석: "These wrap content that represents terminal activity, not actual user prompts".
   - 최초 4논거 중 **①(조립안전성)은 사용자 반박으로 기각**: 배열 원소 사이에서만 분할/필터링이 일어나므로 각 원소를 자기완결 XML조각으로 만들어도 안전성 동일. 재정렬된 최종 순위: **1위 내용충돌회피**(시스템프롬프트 본문이 XML태그를 언급하므로 섹션 자체를 XML로 감싸면 문법공간 충돌 — 세션인풋 문서 작성 시 `⟨⟩` 치환 사례가 실증) > 2위 태그희소성=출처신호(전부 XML이면 `<system-reminder>`가 벽지가 됨) > 3위 토큰/유지보수. 결론: "루트 없는 자기완결 XML 나열은 사실상 헤더문법만 다른 마크다운"이라 굳이 XML 쓸 이유가 없다는 쪽으로 정리. 전체가 소스주석 없는 역산추론임을 명시.

   **0번 유령 메시지의 캐싱 메커니즘 (이번 구간 신규 규명)**
   - `prependUserContext`(api.ts:449-474)는 **API 스트리밍 호출 인라인**(`query.ts:655`)에 박혀 사이클마다 실행 — "매 호출 재인쇄"는 맞지만, 내용물을 만드는 `getUserContext`(context.ts:155)는 `memoize`돼 있어 **세션 첫 호출 때 1회만 디스크 I/O**, 이후는 캐시된 문자열 재인쇄.
   - 캐시 무효화 지점 3곳뿐: `/clear`(`commands/clear/caches.ts:52`)·수동 `/compact`(`compact.ts:63,117,203`)·auto-compact 후처리(`postCompactCleanup.ts:59`). 즉 **CLAUDE.md 수정은 /clear·compact 전엔 반영 안 됨**.
   - 설계 철학: "변하면 안되는 것(0번, claudeMd+currentDate)은 동결해 KV캐시 프리픽스 안정화, 변하는 정보(날짜)는 0번을 안 건드리고 꼬리에 `date_change` 어태치먼트로 별도 추가" — `constants/common.ts:17-23` 주석이 이 트레이드오프("stale date ... vs entire-conversation cache bust — stale wins")를 명시. 델타 4형제(skill/deferred/agent/mcp)와 동일 철학("앞은 얼리고 변경분은 뒤에 덧붙인다").
   - `getUserContext` return값은 `claudeMd`+`currentDate`(신버전 +`userEmail`)뿐 — 스킬/도구/에이전트 목록은 **절대 포함 안 됨**(포함시 매 변경마다 0번 바이트 변경→대화 전체 캐시붕괴이므로 별도 델타 어태치먼트 트랙으로 분리한 것이 캐시설계상 필연).

   **스킬 목록 발행 타이밍 & 장부관리 (이번 구간 신규 규명)**
   - `getSkillListingAttachments`(attachments.ts:2661-2751): 기본 시나리오 = 첫 수집 지점(보통 첫 엔터)에서 `sentSkillNames`(agentId별 Set)가 비어있으면 전체 목록 발행(`isInitial:true`), 이후 변경분만 델타. Skill툴 없는 에이전트엔 미발행. `--resume`이면 `suppressNext`로 첫 발행 억제(이미 트랜스크립트에 있으므로). 예산: 컨텍스트 1%(`SKILL_BUDGET_CONTEXT_PERCENT`)+스킬당 설명 250자 컷.
   - 장부관리 차이: 스킬목록="프로세스 메모리의 Set"(resume시 증발→수동보정), deferred도구="대화이력 스캔으로 재구성"(resume에도 자동복원) — "대화가 곧 상태"인 deferred쪽이 더 견고한 설계.

   **system-reminder 태그 전수 지도 (이번 구간, 핵심·미완결)**
   - **메시지 레벨(어태치먼트)**: messages.ts 렌더 스위치에 래핑 호출 62곳. WRAP 대상 약 47개 어태치먼트 타입, 6계열 — 목록/델타(skill_listing·deferred_tools_delta·agent_listing_delta·mcp_instructions_delta) / 메모리·규칙(nested_memory·relevant_memories·output_style) / 훅출력(hook_success·hook_additional_context·hook_blocking_error·hook_stopped_continuation·async_hook_response) / 상태알림(date_change·task_status·task_reminder·todo_reminder·verify_plan_reminder·compaction_reminder·token_usage 등) / IDE·파일컨텍스트(opened_file_in_ide·selected_lines_in_ide·edited_text_file·directory·@멘션 첨부류·mcp_resource 등) / 모드·기타(plan_mode_exit·auto_mode_exit·invoked_skills·agent_mention·companion_intro·critical_system_reminder·queued_command). plain(안 감쌈) 목록도 별도 존재(already_read_file·assistant·attachment·auto_mode·bash_code_execution_tool_result 등 — 대부분 시스템 내부 메시지타입이지 사용자향 콘텐츠 래핑 대상이 아님).
   - **queued_command 정정**: 래핑은 항상 하되(`wrapMessagesInSystemReminder`), `isMeta`만 조건부 — `origin`이 있거나 `attachment.isMeta`가 true일 때만 isMeta:true(시스템생성/큐드레인), 사람이 미드턴에 친 메시지는 isMeta 없이 화면에 보이도록.
   - **인라인 레벨(어태치먼트 아님, tool_result 문자열에 직접 삽입)**: FileReadTool.ts:706-707(빈 파일/오프셋 초과 경고), :730(**멀웨어 지침 상시경고** — Read 결과마다 뒤에 자동 첨부, "분석은 되나 개선·증강은 거부하라").
   - **선포장 레벨(큐 값 자체가 이미 wrapInSystemReminder로 포장돼 들어옴)**: hooks.ts:238(Stop훅 차단에러) — census에서 "queued_command"로만 보였던 것의 실체.
   - **특수목적 직조립형**: memdir/memoryAge.ts:52(회상메모리 신선도경고) · sideQuestion.ts:61(사이드질문 포장, "You must answer this question directly in a single response") · commands/brief.ts:108-114(brief모드 인라인랩) · api.ts:463(유령메시지, 템플릿에 직접 내장).
   - **소비자(태그를 벗기는 쪽, 생산자 아님)**: transcriptSearch.ts:117("Strip <system-reminder> anywhere — Claude context, not user-visible") · queryHelpers.ts:432(정규식 제거) · VirtualMessageList/messageActions(UI 렌더링시 제거) — system-reminder가 **모델 전용 채널**이며 사람이 보는 모든 표면에서 체계적으로 제거됨을 역증.
   - **isMeta=true이지만 system-reminder로 안 감싸는 것** (messages.ts 밖에서 직접 생성, 전수): SkillTool.ts:1104(스킬 본문, "따라야 할 지시"라 참고방송 계약과 안 맞아서로 추론) · FileReadTool.ts:887,942,1013(Read의 이미지/PDF 동반주입, tool_result 대신 user메시지로) · processSlashCommand.tsx:578,861,907·processUserInput.ts:600(슬래시커맨드 확장 산출물+⑤ 비동기결과 재진입) · query.ts:1217,1316·runAgent.ts:642·plans.ts:386·conversationRecovery.ts:214·teleport.tsx:69·print.ts:1851(합성메시지들, 위치만 확인·본문 미검증).
   - 구분원리: `system-reminder⭕+isMeta` = 하네스의 참고방송(주변과 무관) / `system-reminder✗+isMeta` = 숨겨진 정식입력(따라야 할 지시·소비할 데이터) / `system-reminder⭕+isMeta✗` = 포장된 유저 육성(출처표시하되 화면엔 보임).
   - **미완료**: 사용자가 마지막으로 "어태치먼트는 뭉뚱그려 하나로, isMeta=true 비래핑 항목까지 포함한 총정리"를 요청했고 아직 답변 전달 안 됨.

3. Files and Code Sections:
   - **(이전 라운드 소스, 완전 인용 완료 — 이번 구간 변경 없음, 목록만 유지)**: `toolOrchestration.ts`/`Tool.ts:750-765`/`FileReadTool.ts:373`/`GrepTool.ts:183`/`query.ts:820-824`/`api.ts:449-474`/`context.ts:155-189`/`attachments.ts:875,2661-2751`/`messages.ts:3700-3738`(배치·컨텍스트주입) · `claudemd.ts`/`FileReadTool.ts:848,870,1038`/`QueryEngine.ts:370,518`/`query.ts:1540-1579`(rules지연주입) · `SkillTool.ts:1055-1119`/`AgentTool/loadAgentsDir.ts:312-324`/`processUserInput.ts:140-209`/`utils/hooks.ts:938-981`/`types/hooks.ts`/`constants/prompts.ts:127-576`/`utils/attachments.ts:702,854,1584`/`utils/messages.ts:4090-4231`/`utils/api.ts:318-421`(훅·MCP지시·캐시경계) · `src/tools/ToolSearchTool/ToolSearchTool.ts`(전문)/`prompt.ts`/`src/utils/toolSearch.ts`(756줄)/`src/services/api/claude.ts:1150-1250`/`src/utils/attachments.ts:1440-1475,800-860`/`src/utils/messages.ts:4178-4207`(ToolSearch 5단계 생애주기).
   - **`/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`, `.html`** — 이번 구간 첫머리에서 §08 추가Q&A(md)/07섹션(html) Edit으로 반영 완료(직전 라운드 미완이었던 것).
   - **CREATED: `/Users/seobi/jinsup_space/CC/큐웨이크-엔터없는-진입-소스분석.md`** — Write 1회 + Edit 다수. 구성: §00 요약(문3개) → §01~04 6경로 상세(①~⑥) → §05 한줄요약(6개로 갱신) → §06 서비스이용자 관점(시나리오 6개, "체감 포인트" 부기 + 반대케이스) → 검증이력(grep 방법론+제외판정 근거 포함).
   - **`src/utils/messageQueueManager.ts`(120-193)** — `enqueuePendingNotification`(priority 기본 `'later'`), `PRIORITY_ORDER`.
   - **`src/hooks/useQueueProcessor.ts`(전문 Read)** — `useSyncExternalStore`+`useEffect` 기반, `isQueryActive===false && queue not empty`시 자동 `processQueueIfReady` 호출(:48-60) — 큐 웨이크의 실체.
   - **`src/utils/task/framework.ts`(1-70,190-295)** — `POLL_INTERVAL_MS=1000`, `pollTasks`, "each task type handles its own completion notification" 주석(:200-201).
   - **`src/utils/hooks.ts:225-245`** — Stop훅 exit 2 시 `wrapInSystemReminder`로 포장된 에러가 `enqueuePendingNotification(mode:'task-notification')`으로 큐잉.
   - **`src/types/textInputTypes.ts:178-320`** — `QueuePriority`('now'/'next'/'later', 각 의미 주석 포함), `QueuedCommand`, `PromptInputMode`('bash'/'prompt'/'orphaned-permission'/'task-notification').
   - **`src/tasks/RemoteAgentTask/RemoteAgentTask.tsx:179,235,338,356`** — 원격 에이전트 상태변화 4곳 큐잉, `TASK_NOTIFICATION_TAG` XML 조립.
   - **`src/tasks/LocalShellTask/LocalShellTask.tsx:89,166`** — 백그라운드 명령이 interactive prompt에 막힐 때 진행중 경고 큐잉(priority `next`).
   - **`src/utils/processUserInput/processSlashCommand.tsx:120-160`** — 비동기 에이전트 결과가 `mode:'prompt'`+`isMeta:true`+`skipSlashCommands:true`로 숨은 프롬프트 재진입(스케줄작업의 실제 배관), "Scheduled tasks fire at startup..." 주석.
   - **`src/cli/print.ts:5270-5298`** — `orphaned-permission` 모드, headless/원격 승인 재개 로직(`handleOrphanedPermissionResponse`).
   - **`src/constants/xml.ts`(전문 Read)** — XML 태그 20여개 상수(TASK_NOTIFICATION_TAG 등), "not actual user prompts" 주석.
   - **`src/utils/api.ts:444-474`** — `prependUserContext` 전문(0번 유령 메시지 템플릿, `<system-reminder>...IMPORTANT: this context may or may not be relevant...</system-reminder>`).
   - **`src/query.ts:650-660`** — `prependUserContext(messagesForQuery, userContext)`가 API 스트리밍 호출 인라인(:655)에서 매 사이클 실행됨을 확인.
   - **`src/context.ts:1-40,155-189`** — `getUserContext = memoize(...)`(:155), `setSystemPromptInjection`이 캐시 clear하는 지점(:32), `getUserContext` return 구조(claudeMd+currentDate).
   - **`src/constants/common.ts:1-34`** — `getLocalISODate`, `getSessionStartDate = memoize(getLocalISODate)`(:24), 캐시안정성 주석(:17-23, "stale date ... vs entire-conversation cache bust — stale wins").
   - **캐시 무효화 3지점**: `src/commands/clear/caches.ts:52`, `src/commands/compact/compact.ts:63,117,203`, `src/services/compact/postCompactCleanup.ts:59`.
   - **`src/utils/attachments.ts:2661-2751`** — `getSkillListingAttachments` 전문(sentSkillNames, suppressNext, 예산 게이트).
   - **`src/utils/messages.ts:3695-3800,4178-4207`** — `nested_memory`/`relevant_memories`/`skill_listing`/`queued_command` 렌더 케이스, `wrapMessagesInSystemReminder` 62곳 census(python 스크립트로 case-label별 WRAP/plain 분류).
   - **`src/tools/AgentTool/runAgent.ts:381`** — 서브에이전트 스폰 시 `override?.userContext ?? getUserContext()`(시스템프롬프트는 갈아끼우되 유령메시지는 공통 승계).
   - **`src/tools/FileReadTool/FileReadTool.ts:706-707,730,887,942,1013`** — 빈파일/오프셋경고·멀웨어지침(인라인 system-reminder), 이미지/PDF 동반주입(isMeta user메시지).
   - **`src/memdir/memoryAge.ts:45-52`, `src/utils/sideQuestion.ts:61`, `src/commands/brief.ts:108-114`** — 특수목적 system-reminder 직조립 3곳.
   - **`src/utils/transcriptSearch.ts:117-125`, `src/utils/queryHelpers.ts:432`** — system-reminder 스트리핑(소비자) 확인.

4. Errors and Fixes:
   - **(이전 라운드, 압축유지)**: "다음 사이클 전처리가 우편함 비움"→"같은 사이클 꼬리에서 수집"로 자가정정 / 훅 설명 밀도과다→시나리오 기반 재설명 / Python 카운터 오출력→grep -c로 정상삽입 검증 / "tools 배열에 검색될 목록 있다" 뉘앙스→사용자 지적("tools에는 검색될 도구 목록은 안들어가잖니")으로 "이름목록은 대화이력에만" 정정.
   - **(이번 구간) "엔터 없는 진입 경로는 4개" → 사용자 재확인 질문("저 4경우빼고는 없는건가")으로 전수 재조사 → 실제로는 6개**: ⑤비동기 에이전트 결과 재진입, ⑥고아 권한 응답이 누락돼 있었음을 발견해 추가, ①도 3갈래(완료알림/진행중경고/원격상태변화)로 세분화됨을 확인.
   - **(이번 구간) XML 논거 ① 기각**: 사용자 반박 "1번은 사실 xml으로 해도 문제없지않나" → 어시스턴트가 즉시 인정("맞아요, 인정합니다 — ①은 제가 과장했어요"), 논거 재정렬(내용충돌회피가 진짜 1위).
   - **(이번 구간) "CLAUDE.md는 수정하면 다음 호출부터 반영된다" → 어시스턴트 자가 정정("제가 틀린 말을 했습니다")**: 실제로는 `getUserContext`가 memoize돼 있어 `/clear`·`/compact`·auto-compact 후처리 전까지는 세션 첫 호출 시점 캐시된 내용이 계속 재인쇄됨.
   - **(이번 구간) "queued_command는 system-reminder로 안 감싼다"(직전 답변) → 스스로 재확인 후 정정**: 실제로는 항상 래핑하되 `isMeta`만 조건부(`origin`/`attachment.isMeta` 여부로 결정).

5. Problem Solving:
   - **(이전 라운드, 완전 규명 완료)**: 배치파티셔닝/컨텍스트주입4트랙/rules지연주입/수집·전처리 구간분리/frontmatter4종/훅시스템/MCP지시2모드/캐시경계마커/src-대조4색마킹/ToolSearch 5단계생애주기 전체(3모드게이트·점수표 BM25아님 반증·lost-in-the-middle 4중안전망과 unknown-unknowns 잔여구멍 정직표기) — 전부 소스로 완전 규명·완료.
   - **이번 구간 신규 완료**: ① ToolSearch md/html 최신화 + "ReAct 사이클 밖 엔터 필요성" 최초 답변(문3개, 큐웨이크 개념 도입) — 완료. ② 큐 웨이크 단독 문서화 + 전수재조사로 4→6경로 확정 + 사용자관점 시나리오 부기 — 완료. ③ 마크다운 vs XML 분업 구조 규명 + 사용자 반박 수용한 논거 재정렬 — 완료. ④ 0번 유령메시지의 "위치는 고정, 내용은 memoize+3곳에서만 무효화"라는 캐싱 메커니즘 완전 규명(다회 사용자 반박·자가정정 거쳐 확정) — 완료. ⑤ 스킬목록 발행 타이밍(첫 수집지점)과 deferred도구 대비 장부관리 차이 — 완료. ⑥ CLAUDE.md가 0번에 있는 이유(권위계층분리 등 4가지, 근거강도 표기) — 완료. ⑦ system-reminder 태그 census — **메시지레벨(어태치먼트 47종/6계열) + 인라인레벨(tool_result 내장경고 2종) + 선포장레벨(Stop훅) + 특수목적직조립(4곳) + 스트리핑소비자 확인**까지는 완료, **최종 통합 총정리 답변만 미전달**.
   - **(미완료, 구간 종료 시점)**: 사용자의 마지막 요청 — "system-reminder에 들어가는 것(어태치먼트는 뭉뚱그려)"과 "안 들어가지만 isMeta==true인 것"의 **최종 종합 정리표** — 조사는 이 구간에서 사실상 전부 끝났으나(위 3층 지도 + isMeta전용 목록 모두 확보됨) 사용자에게 통합된 최종 답변으로 전달되지 않은 채 구간 종료.

6. All User Messages:
   *(1~49는 이전 요약이 승계한 목록 — 배치/컨텍스트주입/rules/훅/MCP지시/캐시경계/src대조마킹/ToolSearch 심화질문까지, 49번이 이번 구간 시작 직전 마지막 요청)*
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
   21. "무슨말이야? 나프롬프트 중에... <user-prompt-submit-hook>을 포함한 hooks의 피드백은 사용자로부터 온 것으로 취급하세요... 이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구....."
   22. "훅출력이 낄때가있다고 무슨말이야 ?"
   23. "UserPromptSubmit 이게 도대체 뭔데 ㅋㅋ 무슨훅을 말하는거야 배경부터 설명해야지"
   24. "내가 지정한 셀 스크립트를 자동 실행하라는건 에이전트상 어떤 툴을 실행한다는건데 뭘실행한거야"
   25. "아니 저게 그러면 무슨말이야......"
   26. "<user-prompt-submit-hook> 이라는건 여기 소스코드 어디에 나오는말이야"
   27. "getHooksSection() 은 어디안에서쓰는데?"
   28. "사실상 <user-prompt-submit-hook>라는 태그는 따로 없구나 이거 개발자가 작업하다 안지운 가능성이 큰거네"
   29. "시스템프롬프트의 mcp 서버지시의 실제 예시는 어떻게 될까?"
   30. [슬래시커맨드 /login] — 실제 로그인 이벤트(세션 내부 이벤트)
   31. "<local-command-stdout>Login successful</local-command-stdout>"
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
   49. "위에 추가된 내용 다 md와 html에 반영해줘 그리고 새로운질문 ReAct사이클이 아닌경우는 다 시스템리마인드나 어태치먼트는 사용자가 엔터쳐야 올라가 예외는있나?"

   *(50~64는 이번(직전) 구간에서 새로 추가된 메시지)*
   50. "그 툴서치를 떠나서 방금 그 .. 큐 웨이크에 관해서 적어주라 그니까.. 어떤경우에만 엔터 안치고도 들어가는지? ReAct사이클 제외해서 말야"
   51. "맨아래에 그.. 서비스 이용입장? 에서 ? 구체적으로 어떤 케이스인지..? 추가해줄래? 무슨말인지알아?"
   52. "저 4경우빼고는 없는건가"
   53. "클로드코드는 왜 xml이 아니라 마크다운으로 시스템프롬프트가 구성되어있을까?"
   54. "1번은 사실 .. xml으로 해도 문제없지않나"
   55. "그 0번째 유저프롬프트 에 대한질문인데 그때 CLAUDE.md 내용들어가거 그리고 사용자가 뭔가 엔터를 쳐야만 스킬목록이나 도구 검색 가능 목록등이 들어가나?"
   56. "아니 클로드.md는 시스템 프롬프트 다음 첫 유저프롬프트에만 들어가는거 아니야?"
   57. "그리고 CLAUDE.md가 바뀔떄마다 들어가는거였어?"
   58. "거기에 스킬목록이라던가 그런건 안들어가지?"
   59. "그러면 스킬목록은 어느타이밍에 들어갈까? 사용자가 첫메시지 엔터치는순간?"
   60. "CLAUDE.md는 왜 시스템프롬프트에 안넣고 저렇게 0번째에 넣었을까?"
   61. "그 궁금한게 스킬목록과 툴서치 등 내용은 다 시스템리마인더라는 태그로 감싸서 들어가려나"
   62. "시스템 리마인더에 들어가는 종류가 뭐뭐가있지 그리고 시스템 리마인더없이 들어가는 isMeta =true 인건 또 뭐가이쏙?"
   63. "시스템 리마인더인데 어태치먼트가 아닌거가 들어가느것도 있지않나? 그건 왜빠졌어"
   64. "총정리해주라 시스템 리마인드에 들어가는것들 (어태치먼트는 그냥 묶어서 어태치먼트라해주고) 그리고 아닌것이지만 isMeta==true 인것들"

7. Pending Tasks:
   - **(최우선, 미완료)** 사용자의 마지막 요청(메시지 64) — system-reminder로 감싸지는 항목 총정리(어태치먼트는 하나로 뭉뚱그림) + system-reminder 없이 isMeta==true인 항목 총정리 — 조사는 끝났으나 통합된 최종 답변이 아직 사용자에게 전달되지 않음.
   - (열린 제안, 확정 요청 아님) `배치-단독-개념-소스증명.md`의 짝꿍 HTML 시각화 문서 제작 여부 — 여전히 요청 없음, 보류.
   - (이전 라운드 미완이었던 항목들은 이번 구간 첫머리에서 전부 완료 확인됨 — 더 이상 pending 아님: toolsearch md/html 반영, "ReAct 사이클 밖 엔터 예외" 질문 답변.)

8. Current Work:
   어시스턴트는 사용자의 "시스템 리마인더인데 어태치먼트가 아닌 것도 있지않나? 왜빠졌어"(메시지 63) 질문에 답하기 위해 `grep -rn "wrapInSystemReminder|<system-reminder>"`로 `messages.ts` 밖의 생성처를 전수 검색했고, 3개 계열(①tool_result 인라인형: FileReadTool.ts의 빈파일/오프셋경고·멀웨어지침 / ②큐 선포장형: hooks.ts의 Stop훅 차단에러가 큐잉 전 이미 포장됨 / ③특수목적 직조립형: memoryAge.ts·sideQuestion.ts·brief.ts·api.ts 유령메시지)을 찾아 답변으로 정리했다. 동시에 태그를 **벗기는** 소비자들(transcriptSearch.ts, queryHelpers.ts, UI 컴포넌트들)도 발견해 "system-reminder는 모델전용 채널이며 사람이 보는 모든 표면에서 제거된다"는 부수 결론을 제시했고, "system-reminder의 3개 서식 층위"(메시지레벨/인라인레벨/선포장레벨) 지도로 마무리했다. 이 답변 직후, 사용자가 **"총정리해주라 시스템 리마인드에 들어가는것들(어태치먼트는 그냥 묶어서 어태치먼트라해주고) 그리고 아닌것이지만 isMeta==true 인것들"**(메시지 64)을 보냈고, 이 요청에 대한 응답이 시작되기 전에 구간이 종료됐다. 이 구간 동안 어떤 파일도 새로 Write/Edit되지 않았다 — 전부 grep/Read 기반 구두 답변이었다(단, `큐웨이크-엔터없는-진입-소스분석.md`는 이 구간 초반 큐웨이크 6경로 확정 시점에 Edit으로 갱신 완료된 상태).

9. Optional Next Step:
   사용자의 마지막 발화("총정리해주라 시스템 리마인드에 들어가는것들 (어태치먼트는 그냥 묶어서 어태치먼트라해주고) 그리고 아닌것이지만 isMeta==true 인것들")에 직접 답해, 이번 구간에서 이미 확보한 조사 결과를 하나의 통합 표/목록으로 종합해야 한다: (a) **system-reminder로 감싸지는 것** = 어태치먼트 전체(하나의 카테고리로 뭉뚱그림, ~47종/6계열이었다는 내역은 참고로만 남김) + 0번 유령메시지(템플릿 내장) + tool_result 인라인 경고 2종(빈파일/오프셋, 멀웨어지침) + 큐 선포장형(Stop훅 차단에러) + 특수목적 직조립 3곳(메모리 신선도경고·sideQuestion 포장·brief 인라인랩); (b) **system-reminder 없이 isMeta==true인 것** = 스킬 본문(SkillTool.ts:1104) + Read의 이미지/PDF 동반주입(FileReadTool.ts:887,942,1013) + 슬래시커맨드 확장 산출물 및 비동기 결과 재진입(processSlashCommand.tsx 등) + 합성 메시지들(query.ts·runAgent.ts·plans.ts 등, 위치만 확인된 것은 그 사실을 명시). 새로운 grep/Read가 추가로 필요한지 여부는 이미 이번 구간에서 두 목록 모두 소스 근거를 확보했으므로 원칙적으로 불필요하며, 종합·정리 작업이 다음 단계다.

</summary>
