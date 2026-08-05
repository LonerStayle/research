## 단계 2

<summary>

1. Primary Request and Intent:
   - **세션 대주제(누적)**: `/Users/seobi/jinsup_space/CC`(Claude Code 내부를 소스코드로 역공학하는 리서치 프로젝트) 전체 파악. 배치 파티셔닝 → 컨텍스트 주입 4트랙 → 훅/MCP지시/캐시경계 → ToolSearch 지연로딩 → 큐 웨이크 → XML vs 마크다운 → 0번 유령메시지·CLAUDE.md 캐싱·스킬목록 타이밍 → **system-reminder 태그 전수 조사(완료, md+html 산출)** → **ReAct 사이클 전용 SR/비SR 지도(완료)** → **스킬 lost-in-the-middle 대처 규명(완료, 구두)** → **기술부채(design debt) 전수 스캔 워크플로우(완료, md+html+json 산출)** → **Coordinator Mode/수퍼바이저 패턴 규명(완료)** → **(미완, 세그먼트 마지막) 클로드코드에 없는 유명 기술 4종 검증**으로 이어지는 연쇄 딥다이브. 전 구간 "주장은 grep/Read로 소스 검증" 규율 일관 적용.
   - **(직전 요약 시점 미완이었던 마지막 요청, 이번 구간 첫머리에서 완료)**: "총정리해주라 시스템 리마인드에 들어가는것들(어태치먼트는 뭉뚱그려) + 안들어가지만 isMeta==true인것들" → Ⅰ.SR로 들어가는 것(어태치먼트 일괄+비어태치먼트 7종 표) / Ⅱ.SR없이 isMeta=true(4종 표) / Ⅲ.SR×isMeta 2축 3개 조합 정리로 답변 — **완료**.
   - **md+html 문서화 요청**(완료): "대화 텍스트상은 짧을거아냐 md와 /visual-explainer html 두개의 버전으로 잘 넣어줘" → `시스템리마인더-isMeta-신분증-총정리.md`/`.html` 신규 작성(§00~§02, "컨텍스트 세관" 메타포).
   - **용어 이해 안 됨 → 재설명 요청**(완료): "인라인레벨, 선포장, 직조립 이게 뭔말인지 하나도모루겠어" → 택배 비유(공장일괄포장/책귀퉁이경고문/미리싸서우체통/그자리조립)로 재설명 → "반영해" → md/html 양쪽에 택배비유 범례 표 Edit 반영.
   - **ReAct 사이클 전용 SR 질문**(완료): "엔터 못치는 구간인데 SR이 어태치먼트 말고 또 보내는거 있나? ReAct전용 설명 필요" → 3채널(유령재인쇄/tool_result인라인★전용/사이클꼬리) 답변.
   - **ReAct 사이클 전용 비SR 질문**(완료): "시스템리마인더 아니더라도 자동으로 보내는 메시지 더 있나?" → query.ts 미확인 2곳(출력한도 회복 메시지, 토큰예산 넛지) 소스 확인 후 3계열(tool_result채널/SR없는isMeta 5종/전처리 개조) 답변 → "위 두개둘다 md/html 반영해주라" → md에 §03 신설(기존 §03은 §04로 이동), html에 05 섹션 신설, 둘 다 반영 완료.
   - **스킬 lost-in-the-middle 우려**(완료, 다회 왕복): "Skill도 도중 추가되면 ToolSearch처럼 로스트인더미들에 밀리면 못찾나?" → ToolSearch는 스킬 관할 밖(`isDeferredTool`만 검색), compact 후 `sentSkillNames` 의도적 미리셋(구버전 주석) 확인 → 사용자 반박("대처없다는거야? compact하면 스킬목록 날아간다고? 새세션 재갱신되니 문제없는거아냐?") → 어시스턴트 과장 인정, 3시나리오(신규세션=문제없음/resume=소실아님/동일세션compact=위험구간이나 이 세션 실측상 재고지됨 관측)로 재정리 → 사용자 재질문("compact 전, 대화 밀린 상태에서 로스트인더미들로 못찾는 그 경우는 하네스가 어떻게 대처했나?") → "소극적 3종"(표지판/유저명시호출/compact우연리프레시)뿐, 능동복구 없음 = "인정된 빚"이라는 최종 결론 — **완료, 문서화 요청은 없었음(구두 답변만)**.
   - **기술부채(design debt) 전수 스캔 요청**(완료): "이러한 빚이 뭐가있는지 워크플로우로 전체 소스코드 싹다 스캔해서 찾아줄래? md와 /visual-explainer html로 만들게 전체 크게 돌고와라" → `Workflow` 도구로 13샤드 병렬 스캔+검증 백그라운드 실행 → 완료 후(287건 확정) `클로드코드-기술부채-대장.md`/`.html`/`-전체287건.json` 3종 산출 — **완료**.
   - **(세션 내부 이벤트)** `/compact` 재발동 — 실제 컴팩션, 유저 발화 아님.
   - **수퍼바이저 패턴 질문**(완료): "클로드코드의 수퍼바이저 패턴이 있어?" → `src/coordinator/coordinatorMode.ts` 발견, 2층위(암묵적 상시 vs 플래그게이트 Coordinator Mode) + Swarm/Team 인프라로 답변.
   - **공통 하네스 여부 질문**(완료): "Coordinator Mode 쓰더라도 서브에이전트 하네스가 바뀌진않지? 전체적으로 공통하네스쓰지?" → `isCoordinatorMode()` 소비처 전수 확인, `runAgent.ts`엔 분기 자체가 없음(워커=일반 서브에이전트와 동일 경로) 확인 → "하네스는 하나, 배역만 여럿" 결론.
   - **(진행 중, 미완료 — 세션 최종 미해결 요청)**: "임베딩 검색 없음 / BM25 없음 / 의도 분류 없음 / 고정된 에이전트 워크플로우 없음 — 클로드코드에 위 4개 없는거 맞아? 그리고 유명 기술이지만 없는거 또 뭐가있지?" — 이 구간 마지막 유저 메시지. 어시스턴트가 "4개를 하나씩 소스로 검증하고, 없는 것들을 더 찾아보겠습니다"라고 착수 선언만 한 채, 실제 grep/Read 없이 구간 종료.
   - **불변 제약(전체 세션 유지)**: 항상 한국어 응답. 모든 주장은 grep/Read 소스 검증 후 답변(프로젝트 CLAUDE.md 지침). 추측·과장 금지, 미확인은 "소스에서 확인 못함" 표기. 문서는 `~` 중립/상대경로(세션인풋 계열 MD만 예외). HTML에 유저 PC 절대경로 하드코딩 금지.

2. Key Technical Concepts:
   - **(pre-round5, 완전 규명 완료 — 압축 유지)**: 배치 파티셔닝(safe/unsafe 병합) · 0번 유령 vs 델타 어태치먼트 4형제(skill/deferred/agent/mcp) · rules 지연주입(frontmatter `paths:`→사이클꼬리→`nested_memory`) · 수집(+)/전처리(−) 구간분리 · frontmatter 2단구조 · 훅=하네스실행(`getHooksSection()`, `<user-prompt-submit-hook>`는 소스에 실체 없는 구버전 잔재) · MCP지시 2배달모드 · `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 캐시경계 · ToolSearch 5단계 생애주기(3모드게이트/필드가중치 점수표-BM25아님/`tool_reference`영수증/lost-in-the-middle 4중안전망+잔여구멍) · src대조 4색마커.
   - **(round5, 압축 유지)**: 큐 웨이크 — 엔터 없는 진입 6경로(①백그라운드완료·진행중경고·원격상태변화 3갈래 ②Stop훅차단 ③원격기기입력 ④스케줄 ⑤비동기에이전트결과 재진입 ⑥고아권한응답), 문 3개(엔터/사이클꼬리/큐웨이크) · MD vs XML 분업(내용충돌회피 1위로 재정렬, `constants/xml.ts`) · 0번 유령메시지 캐싱(`prependUserContext` 매호출 실행이지만 `getUserContext`가 `memoize`돼 세션 첫호출만 I/O, 무효화는 `/clear`·`/compact`·auto-compact 후처리 3곳뿐 — `constants/common.ts:17-23` "stale wins" 철학) · 스킬목록 발행 타이밍(첫 수집지점, `sentSkillNames` 프로세스메모리 Set, `suppressNext`, 예산 1%+250자/스킬) · CLAUDE.md가 0번에 있는 이유(권위계층분리 등 4가지) · **system-reminder 태그 전수 지도**(메시지레벨 어태치먼트 ~47종/6계열 + 인라인레벨 2종 + 선포장레벨 1종 + 특수직조립 4곳 + 태그제거 소비자들 = "SR은 모델전용 채널").

   **택배 비유 — SR 포장 방식 4종의 재설명 (이번 구간 신규)**
   - 어태치먼트(기준) = **공장 일괄 포장**: 렌더러(messages.ts)가 출고 직전 일괄 포장, 별도 메시지 ⭕
   - 인라인 = **책 페이지 귀퉁이 경고문**: 포장 없음, tool_result 문자열 본문의 일부(FileReadTool.ts:706-707, :730)
   - 선포장 = **집에서 미리 싸서 우체통에**: 큐에 넣기 전 이미 `wrapInSystemReminder`로 포장 완료(hooks.ts:238 Stop훅 차단에러), 별도 메시지 ⭕(배달만 나중)
   - 직조립 = **그 자리에서 싸서 그 자리에서 전달**: 큐도 공장도 안 거침, 손으로 직접 문자열 조립(sideQuestion.ts:61)
   - 핵심: 모델 입장에선 넷 다 동일한 `<system-reminder>...`로 보임 — 차이는 순전히 **하네스 내부에서 누가/언제 포장 테이프를 붙였는가**뿐.

   **ReAct 사이클 전용 SR·비SR 통합 지도 (이번 구간 신규 규명)**
   - SR 배달 3채널: ⓐ **유령 재인쇄**(`prependUserContext`, query.ts:655, 매 사이클 API 호출마다, 내용은 memoize로 동결) ⓑ **tool_result 인라인** — ★ReAct 전용(도구 실행 중에만 존재하는 그릇: 빈파일/오프셋경고·멀웨어지침·메모리신선도경고) ⓒ **사이클 꼬리 어태치먼트 일괄**(델타·알림·훅산출물·`next`큐드레인이 `queued_command` 어태치먼트로 변환돼 여기 편입 — 미드턴 유저메시지·선포장 훅에러도 결국 이 채널로 배달됨).
   - 비SR 자동 주입 3계열: **A) tool_result 채널**(정상결과/합성에러결과[권한거부·훅차단·타임아웃]/형제중단결과[배치 중 하나 abort시 나머지 자동취소]/`tool_reference`블록) **B) SR없는 isMeta user메시지 5종**(①스킬본문 ②이미지/PDF동반 ③★신규확정 출력한도 회복메시지 — query.ts:1213-1218, "Output token limit hit. Resume directly — no apology, no recap... Pick up mid-thought..." ④★신규확정 토큰예산 넛지메시지 — query.ts:1314-1317, `decision.nudgeMessage`/budget continuation count ⑤대화복구메시지, conversationRecovery.ts:214, 위치만 확인) **C) 메시지 "개조"(신규 주입 아님)**: 전처리 5단의 autocompact(전체를 인수인계요약 1개로 교체)/microcompact(오래된 tool_result 비움)/applyToolResultBudget(직전묶음 디스크로).
   - 통합 타임라인: ①전처리개조(비SR) → ②유령재인쇄(SR) → ③모델응답 → ④도구실행[tool_result본체+합성에러/형제취소(비SR) + 인라인경고(SR★전용) + 스킬본문/이미지동반(비SR isMeta)] → ④′이상상황[출력한도회복·예산넛지·대화복구](비SR isMeta) → ⑤사이클꼬리[어태치먼트일괄+큐드레인](SR).
   - 통찰: "긴 작업이 갑자기 끊겼다가 사과 없이 이어지는 현상 = 하네스가 유저 메시지를 위조해 재촉하는 자기회복 장치(③④′)가 작동한 것".

   **스킬 lost-in-the-middle — 3시나리오 구분 및 대처 없음의 정확한 의미 (이번 구간 신규 규명)**
   - ToolSearch는 스킬 관할 밖(`tools.filter(isDeferredTool)` — 도구 전용 필터). 스킬엔 ToolSearch에 대응하는 "검색 복구" 수단이 기본 모드에 없음.
   - `sentSkillNames`(attachments.ts:2607)는 **프로세스 로컬 Map<agentKey, Set>**. compact 시 구버전 스냅샷 주석(compact.ts:524-529)은 "**Intentionally NOT resetting** sentSkillNames: re-injecting the full skill_listing(~4K tokens) post-compact is pure cache_creation with marginal benefit"이라 미리셋을 명시적으로 선택 — 즉 compact 후에도 장부가 살아있어 "이미 다 보냄" 상태로 남고, 미사용/미언급 스킬 이름은 재고지되지 않음(구버전 기준).
   - **3시나리오**: ① 새 세션(프로세스 새로 뜸) → 장부 빈 상태 → 전체 재고지, **문제없음**(사용자 직관 정확) ② resume(`--resume`) → 소실 아님, 옛 트랜스크립트에 목록 메시지 그대로 존재, `suppressNextSkillListing`(conversationRecovery.ts:390-401)으로 중복 방지용 억제일 뿐 ③ **같은 세션 내 compact** → 대화는 요약으로 교체돼 목록 메시지는 사라지는데 장부는 살아있어 재고지 안 됨(구버전 정책) — **이 세션 실측**: `/compact` 직후 어시스턴트 컨텍스트에 전체 스킬목록이 **실제로 재주입됨** 관측 → 현행 배포판은 구버전 스냅샷의 "의도적 미재주입" 정책이 바뀐 것으로 추정.
   - "대처가 없다"의 정확한 의미: 목록이 통째로 사라진다는 뜻이 아니라, **도구엔 있는 능동 검색 복구로(ToolSearch)가 스킬엔 없다**는 뜻. 남는 방어선은 소극적 3종: ①Skill 도구 설명문 표지판(목록 존재만 알림, 못찾아줌) ②유저 명시 `/이름` 호출(하네스 아닌 유저 책임) ③compact 우연 리프레시(설계된 대처 아닌 부수효과, 현행에서 관측됨).
   - 하네스가 이 구멍을 인지하고 있다는 증거: **`EXPERIMENTAL_SKILL_SEARCH`**(attachments.ts:2685-2697) — 상주 목록을 bundled+MCP 스킬만 남기고, 유저/프로젝트/플러그인 스킬은 `getTurnZeroSkillDiscovery(input, messages, context)`가 **매 턴 시작에 유저 입력과 매칭해 관련 스킬만 그때그때 주입**(모델이 검색을 발상해야 하는 ToolSearch보다 한 세대 진화 — 하네스가 대신 생각해줌). 원격 스킬용 **DiscoverSkills** 도구도 별도 존재(SkillTool.ts:389).

   **기술부채(design debt) 전수 스캔 — Workflow 결과 (이번 구간 신규)**
   - `Workflow` 도구로 src 1,884파일(utils564·components389·commands189·tools184·services130 등) 13샤드 병렬 스캔(부채 마커 30여종 grep: Intentionally/trade-off/for now/workaround/stopgap/silently drop 등) + 배치별 적대적 검증(진짜 인지된 빚인가 판정+카테고리교정+흥미도1~5) 2단계 파이프라인.
   - **결과: 287건 확정**(47 에이전트, 918 도구호출, ~26분). 카테고리 분포: 🚧미완공사63·🐛알려진버그42·🧟호환성잔재34·🧱플랫폼한계33·🎚️UX타협28·⚡성능타협27·🔒보안게이트19·💰캐시절약19·🔧기타22. 흥미도 분포 {5:22, 4:92, 3:121, 2:46, 1:6}.
   - **핵심 통찰**: 이 코드베이스의 빚은 대부분 "이자율이 계량돼" 있음 — 주석마다 BigQuery 실측이나 인시던트 번호로 트레이드오프가 정량화됨(Read압축=fleet미캐시2.18%, cron만료=p99업타임61분→53h, resume드리프트=397K→1.65M토큰, 자정날짜스테일=세션당920K토큰 절약). "몰라서"가 아니라 "재고 끝에 남긴" 빚.
   - **반복되는 상환회피 3패턴**: ①탐지로 대체(버그 대신 BQ 텔레메트리 감시) ②킬스위치로 담보("문제생기면 끈다", GrowthBook 원격 off) ③기능축소로 봉합(고치기 어려운 경로 통째 비활성/필터링).
   - **사용자 체감 가능 3개**: cron 예약 7일 뒤 조용히 증발 / resume 시 다른 크기 대화 로드 / Windows 실시간 스트리밍 전면 비활성.
   - **compact/스킬 논의와 직결되는 형제 발견**: `memdir.ts:329`(자정 후 날짜 일부러 스테일 방치 — date_change 꼬리첨부 구조의 근거) · `Tool.ts:294`(포크 서브에이전트 부모 프롬프트캐시 재활용 위해 최신프롬프트 반영 포기) · `attachments.ts:1408`(messages[0] 날짜 미갱신, 캐시전체무효화 방지).
   - 한계 자기표기: grep마커 기반이라 마커 없는 침묵형 빚은 놓쳤을 수 있음, 흥미도/카테고리는 LLM 검증관 판정.

   **Coordinator Mode(수퍼바이저 패턴) — 존재·구조·공통하네스 확인 (이번 구간 신규 규명)**
   - 2층위: **층위1** 항상 있는 암묵적 수퍼바이저(Agent 툴 기반 메인→서브에이전트, task-notification으로 결과 회수, 이번 세션의 debt-hunt Workflow가 확장형 예) / **층위2** 전용 **Coordinator Mode** — 기능플래그(`feature('COORDINATOR_MODE')`) + 환경변수(`CLAUDE_CODE_COORDINATOR_MODE`)로 게이트, `src/coordinator/coordinatorMode.ts` 단일 파일 모듈.
   - `getCoordinatorSystemPrompt()`: 메인 스레드의 시스템 프롬프트를 통째로 "You are Claude Code, an AI assistant that orchestrates software engineering tasks across multiple workers. You are a **coordinator**." 로 교체. 지휘 도구는 Agent(스폰)/SendMessage(기존워커에 후속지시)/TaskStop(중단)/subscribe_pr_activity(단, merge conflict 전이는 GitHub이 webhook 안 함 — `gh pr view N --json mergeable` 폴링 필요). 규칙: 워커로 다른 워커 감시 금지·사소한 일에 워커쓰기 금지·워커 model파라미터 지정 금지·워커 결과 예측/조작 금지·워커 메시지에 감사/응답 금지(모든 메시지는 유저용).
   - **Swarm/Team 인프라**: `INTERNAL_WORKER_TOOLS = {TEAM_CREATE_TOOL_NAME, TEAM_DELETE_TOOL_NAME, SEND_MESSAGE_TOOL_NAME, SYNTHETIC_OUTPUT_TOOL_NAME}`, `utils/swarm/inProcessRunner.ts`(인프로세스 다중에이전트 실행기), `teammate-message` XML태그(워커간 통신).
   - **공통 하네스 확인(핵심 결론)**: `isCoordinatorMode()` 소비처 전수 확인 결과 전부 하네스 교체가 아니라 파라미터 조정뿐(메인 시스템프롬프트 교체/메인 도구풀 확장/워커 강제 async/워커 model파라미터 무시/fork 비활성/proactive 비활성). **결정적으로 `runAgent.ts`엔 `isCoordinatorMode` 분기가 전혀 없음** — 워커는 그냥 `subagent_type:"worker"`인 일반 서브에이전트, Explore/Plan과 토씨 하나 다르지 않은 스폰 경로. 결론: "코디네이터 모드 = 하네스 교체가 아니라 메인의 배역 변경 + 도구셋 조정. 하네스(queryLoop·전처리·SR주입·배치·compact·큐)는 전원 공유." 이전에 규명한 "서브에이전트는 시스템프롬프트만 갈아끼우고 유령메시지(`getUserContext()`)는 공유"(runAgent.ts:381)와 동일 틀.

3. Files and Code Sections:
   - **(pre-round5 소스, 완전 인용 완료 — 변경 없음, 목록만 유지)**: `toolOrchestration.ts`/`Tool.ts:750-765`/`FileReadTool.ts:373`/`GrepTool.ts:183`/`query.ts:820-824`/`api.ts:449-474`/`context.ts:155-189`/`attachments.ts:875,2661-2751`/`messages.ts:3700-3738` · `claudemd.ts`/`QueryEngine.ts:370,518`/`query.ts:1540-1579` · `SkillTool.ts:1055-1119`/`AgentTool/loadAgentsDir.ts:312-324`/`processUserInput.ts:140-209`/`utils/hooks.ts:938-981`/`constants/prompts.ts:127-576`/`utils/attachments.ts:702,854,1584`/`utils/messages.ts:4090-4231`/`utils/api.ts:318-421` · `ToolSearchTool.ts`(전문)/`utils/toolSearch.ts`(756줄)/`services/api/claude.ts:1150-1250`.
   - **(round5 소스, 압축 유지)**: `messageQueueManager.ts(120-193)` · `useQueueProcessor.ts`(전문) · `task/framework.ts(1-70,190-295)` · `hooks.ts:225-245` · `textInputTypes.ts:178-320` · `RemoteAgentTask.tsx` · `LocalShellTask.tsx:89,166` · `processSlashCommand.tsx:120-160` · `print.ts:5270-5298` · `constants/xml.ts` · `api.ts:444-474` `prependUserContext` 전문 · `context.ts:1-40,155-189` `getUserContext=memoize` · `common.ts:1-34` "stale wins" 주석 · 캐시무효화 3지점(`clear/caches.ts:52`, `compact/compact.ts:63,117,203`, `postCompactCleanup.ts:59`) · `attachments.ts:2661-2751` `getSkillListingAttachments` · `messages.ts:3695-3800,4178-4207` · `runAgent.ts:381` · `FileReadTool.ts:706-707,730,887,942,1013` · `memoryAge.ts:45-52`/`sideQuestion.ts:61`/`brief.ts:108-114` · `transcriptSearch.ts:117-125`/`queryHelpers.ts:432`.
   - **`/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`** — round5에서 Write, 이번 구간 2회 Edit: ①§01 1-B 머리에 "용어 안내(택배 비유)" 표 삽입 ②§03 "ReAct 사이클 전용 지도"(3-A/3-B/3-C) 신설 + 기존 §03 한줄요약을 §04로 이동 + 검증이력 갱신. 최종 구조: §00 핵심 2비트 신분증 → §01 SR구역(1-A 어태치먼트 일괄/1-B 비어태치먼트 7종+택배비유/1-C 태그제거자) → §02 isMeta단독 4종 → §03 ReAct사이클지도(신규) → §04 한줄요약 → 검증이력.
   - **`/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.html`** — round5에서 visual-explainer로 Write("컨텍스트 세관—출입증 검문소" 메타포, Song Myung+Gothic A1+IBM Plex Mono, 그래파이트다크+황동배지, 회전 검인스탬프; 섹션 01~04). 이번 구간 2회 Edit: ①02 섹션 위에 "B-0. 용어안내(택배비유)" 범례 4행 삽입 ②footer 앞에 신규 "05 ReAct 사이클 전용 지도" 섹션 삽입(7단 계단 타임라인, 인라인채널 황금테두리 ★강조, 자기회복행 붉은테두리, 요약배지 2장). 매 Edit 후 `open` 재실행으로 브라우저 갱신.
   - **`src/query.ts:1205-1225, 1300-1325`** — 이번 구간 신규 Read/확인. `recoveryMessage`(출력한도 회복, `MAX_OUTPUT_TOKENS_RECOVERY_LIMIT` 체크, isMeta:true) / budget continuation 넛지(`decision.nudgeMessage`, isMeta:true) 전문 확인.
   - **`src/utils/attachments.ts:2607-2703`** — `sentSkillNames = new Map<string, Set<string>>()`(:2607, module-scope/process-local 주석 :2622), `.clear()`(:2613), `sent = sentSkillNames.get(agentKey)`(:2700-2703).
   - **`src/services/compact/compact.ts:518-535, 922`** — "Intentionally NOT resetting sentSkillNames: re-injecting the full skill_listing(~4K tokens) post-compact is pure cache_creation with marginal benefit... Ants with EXPERIMENTAL_SKILL_SEARCH already skip re-injection" 전문 확인(구버전 정책).
   - **`src/utils/conversationRecovery.ts:390-405`** — resume 시 `addInvokedSkill` + `suppressNextSkillListing()`("A prior process already injected the skills-available reminder... Fire-once latch").
   - **`src/tools/SkillTool/SkillTool.ts`** — `DISCOVER_SKILLS_TOOL_NAME`/Discover 관련 라인(:139,170,385,389,393,661,693,975), :389 "Use DiscoverSkills to find remote skills first" 확인.
   - **CREATED: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`** — python으로 그룹핑 데이터 기반 생성, 222줄. 카테고리 9종(이모지: 💰🐛🔒🧱🎚️🧟⚡🚧🔧) × 흥미도4~5 정제 96건 표(위치·트레이드오프·체감).
   - **CREATED: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.html`** — visual-explainer로 생성("Claude Code 기술 부채 대장 — 계량된 빚 287건", Bebas Neue+Gothic A1). CSS 변수 오타 `--pink:#ff7 eb;` 발견 → Edit으로 `--pink` 변수 자체 제거하여 수정.
   - **CREATED: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장-전체287건.json`** — scratchpad의 `debt_findings.json`(원본 287건 전량, 영문 quote 포함)을 프로젝트 폴더로 cp.
   - **(휘발성, scratchpad — 미보존)**: `/private/tmp/claude-501/-Users-seobi-jinsup-space-CC/c36aeba7-7619-425b-b98f-6585ccf6794d/scratchpad/debt_findings.json`, `debt_grouped.json` — Workflow 원본 산출물 가공용, 프로젝트 폴더로 복사된 것만 durable.
   - **Workflow 산출물 메타**: Run ID `wf_89574a3c-93a`, Task ID `w6qkc6gs7`, 스크립트 파일 `/Users/seobi/.claude/projects/-Users-seobi-jinsup-space-CC-src/c36aeba7-7619-425b-b98f-6585ccf6794d/workflows/scripts/debt-hunt-wf_89574a3c-93a.js`(재편집·재호출 가능), 전체 텍스트 출력 `/private/tmp/claude-501/-Users-seobi-jinsup-space-CC/dd11fb8a-1577-4c24-87dc-918c64250ce1/tasks/w6qkc6gs7.output`(357,603 bytes).
   - **`src/coordinator/coordinatorMode.ts`(전문 Read, 특히 :1-40, :88-175)** — `isScratchpadGateEnabled()`(`tengu_scratch` statsig gate, circular-dep 회피 위해 filesystem.ts에서 중복 정의), `INTERNAL_WORKER_TOOLS`(:31), `isCoordinatorMode()`(`feature('COORDINATOR_MODE') && isEnvTruthy(CLAUDE_CODE_COORDINATOR_MODE)`), `getCoordinatorSystemPrompt()`(:111-175, 전문 확인).
   - **`isCoordinatorMode()` 소비처 전수**: `tools.ts:281,293`(도구풀) · `main.tsx:2198`(proactive 비활성) · `main.tsx:3768`(saveMode) · `main.tsx:4590`(analytics `is_coordinator`) · `AgentTool/resumeAgent.ts:251` · `AgentTool/forkSubagent.ts:34`(fork 비활성) · `AgentTool/prompt.ts:68,216` · `AgentTool/AgentTool.tsx:223-224,252,553,567,750`(model무시/워커async강제/enableSummarization). **`AgentTool/runAgent.ts`엔 해당 분기 없음**(worker/coordinator 키워드는 tool pool 주석 2줄뿐, :292-294) — 워커 스폰이 일반 서브에이전트와 동일 경로임을 이 부재 자체로 확인.

4. Errors and Fixes:
   - **(pre-round5/round5, 압축 유지)**: 배치파티셔닝·훅설명·python카운터·"tools에 검색될목록 있다" 뉘앙스 정정 / "엔터없는경로 4개"→전수재조사로 6개 확정 / XML논거①(조립안전성) 사용자반박으로 기각·재정렬 / "CLAUDE.md 수정시 다음호출부터 반영"→자가정정(memoize 캐시 확인) / "queued_command는 안감싼다"→래핑은 항상하되 isMeta만 조건부로 정정.
   - **(이번 구간) 용어 불친절 인정**: "인라인/선포장/직조립"이란 신조어를 설명 없이 던진 것에 대해 즉시 사과, 택배 비유로 재설명 후 문서 반영.
   - **(이번 구간) 스킬목록 "대처 없음" 표현 과장 인정**: 사용자가 "결론은 대처없다는거야? compact하면 스킬목록 날아간다고? 새세션 재갱신되니 문제없는거아냐?"라고 반박 → 어시스턴트가 "제가 겁을 과하게 줬네요"라고 인정하고, 신규세션/resume/동일세션compact 3시나리오로 재정리(전자 둘은 사용자 직관이 맞음을 확인, 위험은 ③에 국한).
   - **(이번 구간) compact 후 스킬목록 재고지 여부 — 구버전 정책 vs 실측 불일치 발견**: 구버전 스냅샷 주석(compact.ts:524-529)은 "의도적으로 재주입 안 함"이라 명시하는데, 이 세션에서 실제 `/compact` 직후 전체 스킬목록이 재주입되는 것을 관측 → "현행 배포판은 그 정책이 변경된 것으로 보인다"고 정정된 결론 제시(대표님 직관 쪽이 현행 기준 맞음).
   - **(이번 구간) HTML CSS 오타**: `클로드코드-기술부채-대장.html` 작성 직후 `--pink:#ff7 eb;`(공백이 들어가 파싱 깨짐) 발견 → Edit으로 `--pink` 변수 라인 자체를 제거해 수정, 이후 정상 오픈.

5. Problem Solving:
   - **(pre-round5/round5, 완전 규명 완료)**: 배치파티셔닝/컨텍스트주입4트랙/rules지연주입/훅시스템/MCP지시2모드/캐시경계/ToolSearch 5단계생애주기/큐웨이크 6경로/MD-vs-XML 분업/0번 유령메시지 캐싱메커니즘/스킬목록 발행타이밍/CLAUDE.md가 0번에 있는 이유/system-reminder 태그 전수census(메시지레벨47종+인라인2종+선포장1종+직조립4곳+태그제거소비자) — 전부 소스로 완전 규명·문서화 완료.
   - **이번 구간 신규 완료**: ① 사용자의 마지막 미해결 요청(SR/isMeta 총정리 표) 답변 + md/html 문서화 — 완료. ② 택배 비유로 용어 재설명 + 양쪽 문서 반영 — 완료. ③ ReAct 사이클 전용 SR 3채널 규명 + 답변 — 완료. ④ ReAct 사이클 전용 비SR 3계열 규명(query.ts 미확인 2곳 정체 확정 포함) + 답변 — 완료. ⑤ ③④ 결과 md §03/html 05로 반영 — 완료. ⑥ 스킬 lost-in-the-middle 우려 규명(ToolSearch 관할 밖, sentSkillNames 프로세스로컬, compact 미재주입 구버전 정책, 3시나리오 재정리, "소극적 3종" 방어선, EXPERIMENTAL_SKILL_SEARCH 발견) — 완료(문서화는 미요청). ⑦ 기술부채 287건 전수 스캔 Workflow 실행+분석+md/html/json 3종 산출 — 완료. ⑧ Coordinator Mode 존재·구조·시스템프롬프트 규명 — 완료. ⑨ Coordinator Mode 하에서도 단일 공통 하네스임을 `isCoordinatorMode()` 소비처 전수+`runAgent.ts` 무분기로 확정 — 완료.
   - **(미완료, 구간 종료 시점)**: 사용자의 마지막 요청 — "임베딩검색/BM25/의도분류/고정된 에이전트워크플로우 4가지가 클로드코드에 정말 없는지 검증 + 그 외 유명 기술이지만 없는 것 추가 조사" — 어시스턴트가 착수 선언만 하고 실제 grep/Read 검증은 시작하지 못한 채 구간 종료.

6. All User Messages:
   *(1~64는 이전 요약(round5까지 누적)이 승계한 목록 — 배치파티셔닝부터 system-reminder 총정리 요청(64번)까지. 아래는 이번 구간에서 새로 추가된 메시지 65~80)*
   65. "대화 텍스트상은 짦을거아냐 md와 /visual-explainer html 두개의 버전으로 잘 넣어줘"
   66. "인라인레벨, 선포장 , 직조립 이게 뭔말인지 하나~~도모루ㅡ겠어"
   67. "반영해"
   68. "그리고 ReAct 사이클중 한정해서 이제 엔터는 못치는 구간인데 그 시스템리마인더가 보내는것중 어태치먼트 말고 또 보내는 거 있나? ReAct사이클 전용 설명도 필요해"
   69. "그리고 ReAct 사이클중에서 시스팀리마인더가 아니더라도 자동으로 보내는 메시지 더 있나? 그것도 알려줘"
   70. "위 두개둘다 md/html 반영해주라"
   71. "생각해보니... Skill 도 도중에 추가되면 마지막 메시지에 메타데이터로 추가됬다고 들어갈탠데 toolSerach에 경우 로스트인더미들로 밀릴 경우.. 키워드검색을했는데 추가된 Skill은 어쩌냐"
   72. "그니까 결론은 뭐.. 대처가없다는거야? 무슨말이지? 그리고 컴팩트하면 스킬목록이 날아간다고??? 엥?? 다음 세션에서 첫 메시지보낼때 전체 스킬목록 재갱신시켜주니까 문제없는거안야?"
   73. "그치 compact후 안되는게 너무 이상해 그리고 그 뭐냐.."
   74. "어쨋든 compact전에 새로 추가된 스킬이 대화 오래하다가 대화가 밀린경우 로스트인더미들로 못찾게 될확률이 클탠데 그경우는 어떻게 하네스가 대처했는지 다시 이야기해줄래?"
   75. "또 이러한 빚이 뭐가있는지 워크플로우로 전체 소스코드 싹다 스캔해서 찾아줄래? 다 가져와서 md와 /visual-explainer 로 만든 html으로 만들게 전체 크게 돌고와라"
   76. [백그라운드 태스크 완료 알림(task-notification), Task ID w6qkc6gs7] — debt-hunt 워크플로우 완료 결과 자동 전달(세션 내부 이벤트, 큐 웨이크 경로로 어시스턴트가 자동 재개)
   77. "/compact" — 실제 Claude Code 자체 컴팩션 재발동(세션 내부 이벤트)
   78. "클로드코드의 수퍼바이저 패턴이 있어?"
   79. "Coordinator Mode 를 쓰더라도 서브에이전트의 하네스가 바뀌진않지? 전체적으로 공통하네스쓰지?"
   80. "임베딩 검색 없음\nBM25 없음\n의도 분류 없음\n고정된 에이전트 워크플로우 없음\n\n클로드코드에 위에 4개없는거 맞아? 그리고 유명 기술이지만 없는거 또뭐가있지?"

7. Pending Tasks:
   - **(최우선, 미완료)** 사용자의 마지막 요청(메시지 80) — "임베딩 검색 없음 / BM25 없음 / 의도 분류 없음 / 고정된 에이전트 워크플로우 없음" 4개 주장을 소스로 검증하고, 그 외 클로드코드에 없는 유명 기술을 추가로 찾아 답변해야 함. 조사 미착수.
   - (열린 제안, 확정 요청 아님) `배치-단독-개념-소스증명.md`의 짝꿍 HTML 시각화 — 여전히 요청 없음, 보류.
   - (이전 라운드 미완이었던 항목은 이번 구간 첫머리에서 전부 완료 확인됨 — 더 이상 pending 아님: SR/isMeta 총정리 답변+문서화.)

8. Current Work:
   어시스턴트는 사용자의 메시지 80("임베딩 검색 없음 / BM25 없음 / 의도 분류 없음 / 고정된 에이전트 워크플로우 없음 — 클로드코드에 위 4개 없는거 맞아? 그리고 유명 기술이지만 없는거 또뭐가있지?")에 대해 "좋은 질문이에요. 4개를 하나씩 소스로 검증하고, 없는 것들을 더 찾아보겠습니다."라는 착수 선언 한 줄만 출력한 상태다. 이 발화가 파일의 마지막 줄이며, 이 시점까지 관련 grep/Read/Bash 호출은 아직 하나도 실행되지 않았다. 직전 작업이었던 Coordinator Mode/공통하네스 규명(메시지 78-79)은 소스 확인(coordinatorMode.ts 전문 Read + isCoordinatorMode 소비처 grep)까지 완전히 마치고 답변까지 전달된 상태다.

9. Optional Next Step:
   메시지 80에 답하기 위해 4가지 주장을 하나씩 소스(주로 `/Users/seobi/jinsup_space/CC/src`)에서 grep/Read로 검증해야 한다: ①임베딩검색(embedding/vector/cosine 유사도 관련 코드 존재 여부) ②BM25(이미 이전 구간에서 ToolSearch 채점이 "필드가중치 손코딩이지 BM25 아님"이라는 사실은 규명돼 있으므로 그 근거를 재확인·인용) ③의도분류(intent classifier 존재 여부 — 단, `bashPermissions.ts`의 `BASH_CLASSIFIER`는 bash 명령 위험도 분류기이지 유저 의도분류가 아니므로 혼동 주의) ④고정된 에이전트 워크플로우(단, 이 세션에서 실제로 쓴 `Workflow` 도구가 "동적 스크립트 생성형"인지 "고정형"인지 구분해서 답해야 함 — 사용자 주장과 상충 가능성 있는 지점). 이어서 이 4개 외에 유명하지만 클로드코드에 없는 기술(예: RAG 벡터스토어, planner/executor 분리, 셀프컨시스턴시 보팅 등)도 추가 조사해야 한다. 어시스턴트의 마지막 발화 그대로 인용: "좋은 질문이에요. 4개를 하나씩 소스로 검증하고, 없는 것들을 더 찾아보겠습니다." — 이 선언 직후부터 재개하면 된다.

</summary>
