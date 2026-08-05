## 단계 1

### Current progress and key decisions made

- **Session goal (unchanged)**: 사용자가 `/Users/seobi/jinsup_space/CC` (Claude Code 내부를 리버스엔지니어링하는 리서치 레포: `md_group/` 분석 문서, `html_group_v2/` HTML 시각화, `src/` 재구성 소스)를 대상으로 세부 메커니즘을 하나씩 깊게 파고드는 세션. 이번이 **6번째 컴팩션 사이클**.

- **Chain 1~6 (전부 완전 종결, 재론 불필요 — 이전 요약본 수준 압축 유지)**:
  - Chain1 — 배치 병렬/파티셔닝: `partitionToolCalls`가 `isConcurrencySafe` per-tool 선언만으로 병렬/단독 배치 분리. 산출물 `배치-단독-개념-소스증명.md`.
  - Chain2 — 컨텍스트 주입 4트랙: 0번 유령 메시지 vs skill_listing vs conditional rules vs frontmatter. 산출물 `컨텍스트-주입-4트랙-시각설명.html`.
  - Chain3 — UserPromptSubmit훅/`getHooksSection()`: 무조건 시스템프롬프트 포함, 훅은 하네스가 `spawn`으로 직접실행. MCP지시 2배달모드. 캐시경계 `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`.
  - Chain4 — 세션인풋 전문 스냅샷 문서화(자기전사). Chain6에서 리네임됨.
  - Chain5 — src vs 실서비스 diff 마커 grep검증 CLOSED.
  - Chain6 — "2027"→2026 오타정정 + `/visual-explainer` 청사진 HTML. 산출물 `2026-07-11-시스템프롬프트및도구내용-최신본.md`/`.html`.

- **Chain7 — ToolSearch 지연로딩 5단계 생애주기 완전규명 (완결)**: 분류→모드게이트→고지(`deferred_tools_delta`)→검색(**BM25 아님** — TF/IDF·문서길이정규화 없이 필드가중치 하드코딩 불리언매칭+합산정렬)→로드/재조립. 카드목록 발행은 ToolSearch 호출과 무관, 어태치먼트 파이프라인이 수집지점마다 발행. 로스트인더미들 4중 안전망. 산출물 `toolsearch-생애주기-소스분석.md`/`.html` — **완결.**

- **Chain8~9 — 큐웨이크(엔터 없는 진입) 완전규명, "4개→6개" 자기정정 (완결)**: 대화를 전진시키는 문 3개(유저엔터/사이클꼬리/큐웨이크) 중 큐웨이크가 최종 **6개 도어**로 확정 — ①백그라운드완료 ②Stop훅차단 ③원격입력 ④스케줄(isMeta) ⑤비동기에이전트 결과 숨은프롬프트 재진입(스케줄 배관의 실체) ⑥고아권한응답. 산출물 `큐웨이크-엔터없는-진입-소스분석.md` — **완결.**

- **Chain10 — "왜 XML 아니라 MD로 시스템프롬프트를 구성했나" (완결, 문서화 안 됨 — 순수 채팅)**: 실제론 MD/XML 역할분담(산문지시=MD, 경계·출처표시 화물=XML). "왜 본문이 MD인가" 최종 근거서열: 1위 **내용충돌**(본문이 XML태그를 리터럴 언급 — 자기완결 XML조각으로 바꿔도 이 문제는 여전히 발생, MD헤더는 안 부딪힘) > 2위 태그희소성=신호강도 > 3위 토큰/유지보수. 역산추론이라는 정직표기 유지.

- **Chain11 — "0번째 유저프롬프트"(유령메시지) 다회전 심화, 10라운드 (완전 종결 — 이번 세그먼트 Chain12에서 마지막 총정리 답변 전달 + 문서화까지 완료)**: 핵심 확정사실만 압축 보존(상세는 `시스템리마인더-isMeta-신분증-총정리.md`에 전량 이관됨) —
  - 유령메시지(`prependUserContext`, api.ts:449-474)는 API호출부(`query.ts:655`)에 **인라인**으로 박혀 사이클마다 재실행되나, `getUserContext`가 `memoize`(`context.ts:155`)돼 있어 **세션 첫 호출 1회만** 디스크에서 읽힘. 캐시 무효화는 전수 확인 결과 **3곳뿐**: `/clear`(`caches.ts:52`), `/compact`(`compact.ts:63,117,203`), auto-compact 정리(`postCompactCleanup.ts:59`). 설계철학: "stale wins"(`constants/common.ts:17-23` 주석) — 0번은 얼리고 변경분은 꼬리 델타로.
  - 유령 리턴값은 `{claudeMd, currentDate(+userEmail)}`뿐, 스킬/도구/에이전트 목록은 전부 별도 어태치먼트 채널(변할 수 있는 것=꼬리델타 원칙).
  - `getSkillListingAttachments`(attachments.ts:2661-2751): 기본시나리오=첫엔터에 전체발행, 단서 3개(Skill툴없는에이전트스킵/--resume시 suppressNext/예산1%+250자컷).
  - CLAUDE.md가 시스템프롬프트 대신 0번 유저메시지에 있는 이유(추론, 근거강도순): ①권위계층분리(참고자료 어조로 프롬프트인젝션 벡터 격리, 단 "OVERRIDE" 문구로 권위는 승격) ②서브에이전트 모듈성(`runAgent.ts:381`, 시스템프롬프트는 에이전트별 교체·유령은 공유) ③글로벌캐시 조각방지(부분적) ④채널일관성.
  - `messages.ts` 렌더링 전수(62곳 wrap호출): system-reminder 예외 3개(ToolSearch결과/`queued_command`은 조건부isMeta일뿐 래핑은 항상/스킬본문은 안 감쌈).
  - **1차 census 47종 6계열은 messages.ts 어태치먼트 스위치 하나만 훑은 것이었고, 사용자 재지적으로 3개 추가 층위(인라인/선포장/특수직조립) 발견** — 이 3계열 발견이 Chain12~15의 씨앗이 됨.
  - **자기정정 3회 발생**(큐웨이크4→6, CLAUDE.md 반영시점 오답 정정, 47종census의 3계열 누락) — round5에서 이미 "다음세션 유의사항"으로 등록됨, 이번 세그먼트에서도 재확인(아래 행동시그널 참조).

- **Chain12 — Chain11 "총정리" 답변 전달 + md/html 문서화 (신규, 완결)**: 사용자의 마지막 요청("system-reminder 진입것들=어태치먼트뭉뚱그림+나머지개별나열 / 아닌데 isMeta=true인것도")에 통합표로 답변 후, md 먼저 작성 → `/visual-explainer`로 HTML 빌드. 신규 산출물: `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html`("컨텍스트 세관 — 출입증 검문소" 메타포, 4분면 매트릭스+SR구역+isMeta단독구역+모델전용증명). 구조: Ⅰ.SR로 들어가는것(어태치먼트47종일괄 + 비어태치먼트7종3층위) / Ⅱ.SR없는 isMeta=true(스킬본문·이미지PDF·슬래시확장+비동기재진입·기타합성) / Ⅲ.2×2매트릭스(SR+isMeta=하네스방송 / SR+~isMeta=포장된유저육성 / ~SR+isMeta=숨은정식입력).

- **Chain13 — "인라인/선포장/직조립" 용어를 택배 비유로 재설명 + 문서 반영 (신규, 완결)**: 사용자가 Chain12 용어를 이해 못 함("하나~~도모루ㅡ겠어") → 택배 비유로 재설명: 어태치먼트=공장일괄포장(렌더러, 출고직전) / 인라인=본문에 인쇄된 경고문(포장자체가 없음, tool_result 문자열 일부, FileReadTool.ts:706-707/730) / 선포장=집에서미리싸서우체통에(`enqueuePendingNotification({value: wrapInSystemReminder(...)})`, hooks.ts:238, 큐진입 전 이미 포장) / 직조립=그자리에서싸서그자리에서전달(`sideQuestion.ts:61`, 큐도 파이프라인도 안 거침). 사용자 "반영해" → md(1-B 머리에 용어안내표)·html(02섹션 위 B-0 범례) 양쪽에 편입 완료, 재오픈.

- **Chain14 — ReAct 사이클 전용 SR 지도 (신규, 완결)**: "엔터 못 치는 ReAct 구간에서 어태치먼트 말고 또 SR 보내는 거 있나?"에 답 — 사이클 중 SR 배달 **3채널**: ⓐ유령재인쇄(API직전 매호출, `query.ts:655`, 내용은 동결이라 새정보 아님) ⓑ**tool_result 인라인(★ReAct 전용 — 도구 실행 중에만 존재 가능, 빈파일경고·멀웨어지침·메모리신선도경고)** ⓒ사이클꼬리 어태치먼트일괄(델타·알림·훅산출물·`next`큐드레인 포함, 아는 채널). 헷갈리는 경계 2개 명시(미드턴메시지·훅출력은 결국 ⓒ로 배달).

- **Chain15 — ReAct 사이클 중 비SR 자동메시지 규명 (신규, 완결)**: "SR 아니어도 사이클 중 자동으로 보내는 메시지 더 있나?"에 답하려 `query.ts:1205-1225`, `1300-1325` Read로 기존 미확인 2곳 정체 확정. 결과 3계열: **A) tool_result 채널**(정상결과/합성에러/형제중단결과/tool_reference블록) **B) SR없는 isMeta user메시지 5종**(①스킬본문 ②이미지PDF동반메시지 ③★신규확정 출력한도회복메시지 — `query.ts:1213-1218`, "Output token limit hit. Resume directly — no apology, no recap... Pick up mid-thought" ④★신규확정 토큰예산넛지 — `query.ts:1314-1317` ⑤대화복구메시지) **C) 메시지 개조**(전처리 5단의 autocompact·microcompact·applyToolResultBudget — 새 메시지가 아니라 기존 대화 변형). "모델이 잘렸다가 사과없이 이어말하는 현상"=③이 작동한 순간이라고 사용자 체감으로 번역. **Chain14+15 모두 사용자 "둘다 md/html 반영해" 요청으로 문서에 편입 완료** — md에 새 §03 "ReAct 사이클 전용 지도"(3-A/3-B/3-C, 기존 한줄요약은 §04로 밀림) 삽입, html에 05섹션(사이클타임라인 7단계단 + 자기회복장치 적색배지) 신설, 재오픈.

- **Chain16 — 스킬 vs ToolSearch "로스트인더미들" 검색복구 비대칭, 3라운드 심화 (신규, 완결 — 문서화 안 됨)**:
  1. 사용자 지적: "Skill도 도중 추가되면 목록에 델타로 들어가는데, 대화가 밀려 로스트인더미들 되면? ToolSearch같은 검색복구가 스킬엔 있나?" → 조사: **ToolSearch는 `tools.filter(isDeferredTool)` — 도구 전용, 스킬 관할 밖.** compact 후 `sentSkillNames` **의도적으로 리셋 안 함**(compact.ts:524-529 주석 원문: "Intentionally NOT resetting sentSkillNames: re-injecting the full skill_listing (~4K tokens) post-compact is pure cache_creation with marginal benefit. The model still has SkillTool in its schema and invoked_skills attachment preserves used-skill content."). resume도 `suppressNextSkillListing`으로 억제(conversationRecovery.ts:390-401, fire-once latch). 방어선 3개(invoked_skills 어태치먼트=쓴것만/유저 `/이름` 명시호출/Skill툴 표지판=목록있다고만 알림, 재검색은 못 시킴) — 구멍: 미사용+미언급 스킬은 존재소멸. **해법 공사 중**: `EXPERIMENTAL_SKILL_SEARCH`(attachments.ts:2685-2697) — `getTurnZeroSkillDiscovery`가 매 턴 시작에 유저입력↔스킬 매칭해 관련 스킬만 그때그때 주입, 원격스킬용 `DiscoverSkills` 도구(SkillTool.ts:389)도 별도 존재. 대비구도: "도구=모델주도검색(ToolSearch) / 스킬=하네스가 매턴 대신 검색(turn-0 discovery, 한 세대 진화형)".
  2. 사용자가 어시스턴트의 알람성 프레이밍에 반문("대처가없다는거야? compact하면 스킬목록 날아간다고?? 다음세션 첫메시지땐 전체 재갱신되니 문제없는거아냐?") → **어시스턴트 자기정정**: 3상황 명확히 분리 — ①**새 세션**: 문제없음(프로세스메모리 장부 리셋→전체재고지, 사용자 말이 맞음) ②**resume**: 소실 아님(옛 트랜스크립트에 목록 그대로 있음, 재고지만 억제) ③**같은 세션 내 compact**: 장부는 프로세스메모리라 살아있는데 대화만 요약으로 교체돼 재고지 안 됨(구버전 정책 기준)이 유일한 위험구간. **실측 반전**: 이 세션에서 사용자가 실제로 `/compact` 실행 직후 전체 스킬목록이 어시스턴트 컨텍스트에 재고지된 것을 관측 — 현행 배포판은 구버전 스냅샷의 "의도적 미재주입" 정책과 다른 것으로 보임(③의 공포 상당히 완화). "대처가 없다"의 정확한 의미를 "소실이 아니라 도구엔 있는 능동 검색복구로가 스킬엔 없다는 뜻"으로 표현 정정.
  3. 사용자가 원래 시나리오(대화 밀려 묻힌 스킬)로 재요청 → 최종 정리: 하네스 대처는 "**소극적 3종**"뿐 — ①표지판(상시, "목록에 없는건 추측말라"지만 재검색은 못 시킴) ②유저 명시호출(완전우회, 사실상 유저에게 떠넘김) ③compact 리프레시(간접·우연, 설계된 대처 아님). 없는 것: 주기적재고지✗·스킬검색도구✗·자동매칭✗(기본모드). 결론: "**기본 모드의 인정된 구멍**" — EXPERIMENTAL_SKILL_SEARCH가 정확히 이 구멍을 메우려는 실험.

- **Chain17 — "기술부채 대장" 전체 소스 Workflow 스캔, 287건 확정 (신규, 완결, 대형 산출물 3건)**: 사용자가 "이러한 빚이 뭐가 더 있는지 워크플로우로 전체 소스코드 싹다 스캔해서 찾아줄래... 크게 돌고와라"라고 명시적으로 Workflow 요청 → `debt-hunt` 워크플로우(Run ID `wf_89574a3c-93a`, Task ID `w6qkc6gs7`)를 src 1,884파일/33MB 전체에 13개 샤드 병렬 Scan(부채마커 30여종: Intentionally/trade-off/for now/stopgap/stale wins/marginal benefit/workaround/TOCTOU/silently drop 등) + 12건 배치 Verify(적대적판정+카테고리교정+흥미도1~5) 2-phase로 백그라운드 발사. **완료 결과(큐웨이크①번 완료알림으로 자동 기동)**: 총 **287건**, byCategory: 미완공사63·알려진버그42·호환성잔재34·플랫폼한계33·UX타협28·성능타협27·보안게이트19·캐시절약19·기타22. 47에이전트, 918도구호출, 2,631,759 서브에이전트토큰, 1,539,682ms(~26분). interest분포: 5=22건·4=92·3=121·2=46·1=6.
  - **핵심 통찰**(사용자에게 전달됨): 이 코드베이스의 빚은 대부분 BigQuery 실측치나 인시던트 번호로 "무엇을 포기하면 얼마를 아끼는지" 계량돼 있음 — "몰라서"가 아니라 "재고 끝에 남긴" 빚. **반복 상환회피 3패턴**: ①탐지로 대체(버그 대신 BQ 감시) ②킬스위치로 담보 ③기능축소로 봉합.
  - **compact/스킬 논의(Chain11·16)와 직결된 발견**: `memdir.ts:329`(자정 후 날짜를 일부러 스테일 방치 — date_change 꼬리첨부가 이걸 보정), `Tool.ts:294`(포크 서브에이전트가 부모 프롬프트캐시 재활용 위해 최신 프롬프트 반영 포기), `attachments.ts:1408`(messages[0] 날짜 안 갱신, 캐시 무효화 방지).
  - 사용자가 체감할 만한 것 3개: cron 예약 7일 뒤 조용히 증발 / resume 시 다른 크기의 대화 로드 / Windows 실시간 스트리밍 전면 비활성.
  - 산출물: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`(222줄, 카테고리9종×흥미도4~5 정제 96건 표), `.html`(`/visual-explainer`, "부채 장부" 컨셉, CSS 오타 `--pink:#ff7 eb` 수정), `-전체287건.json`(원본 287건 전량, scratchpad `debt_findings.json`에서 복사). 전부 브라우저 오픈 완료.
  - 한계 정직표기(사용자에게 전달됨): grep 마커 기반이라 마커 없는 침묵형 빚은 놓쳤을 수 있음, 흥미도·카테고리는 검증관 LLM 판정.

- **Chain18 — Coordinator Mode(명시적 수퍼바이저 패턴) 발굴 (신규, 완결 — 문서화 안 됨)**: 사용자 질문 "클로드코드의 수퍼바이저 패턴이 있어?"(세션 중 사용자가 실제 `/compact` 명령을 1회 실행한 직후 새 주제로 전환됨) → grep으로 `src/coordinator/coordinatorMode.ts` 전용 모듈 발견. **2개 층위**: 층위1=항상 있는 암묵적 수퍼바이저(Agent 툴 기반 서브에이전트 위임, task-notification 콜백 — 이번 세션의 debt-hunt Workflow가 확장형). 층위2=**전용 Coordinator Mode**(`isCoordinatorMode()`, `COORDINATOR_MODE` feature flag + `CLAUDE_CODE_COORDINATOR_MODE` env). `getCoordinatorSystemPrompt()`(coordinatorMode.ts:111-175)가 메인의 시스템프롬프트를 통째로 교체: "You are Claude Code, an AI assistant that orchestrates software engineering tasks across multiple workers. You are a coordinator." 도구: AgentTool(워커스폰)/SendMessageTool(기존워커후속지시)/TaskStopTool(워커중단)/subscribe_pr_activity. 지휘규칙 인용: "워커로 다른 워커 감시 금지"·"사소한 일에 워커 쓰지 말기"·"워커 결과 예측·조작 금지"·"매 메시지는 유저에게". Swarm/Team 확장(`INTERNAL_WORKER_TOOLS`: TeamCreate/TeamDelete/SendMessage/SyntheticOutput, `utils/swarm/inProcessRunner.ts`)까지 있어 워커간 상호통신도 가능한 진짜 멀티에이전트 오케스트레이션.

- **Chain19 — Coordinator Mode도 공통 단일 하네스 확인 (신규, 완결 — 문서화 안 됨)**: 사용자 질문 "Coordinator Mode 쓰더라도 서브에이전트 하네스는 안 바뀌지? 전체 공통하네스쓰지?" → `isCoordinatorMode()` 전체 소비처 grep 전수(tools.ts:281,293 / main.tsx:2198,3768,4590 / resumeAgent.ts:251 / forkSubagent.ts:34 / AgentTool/prompt.ts:68,216 / AgentTool.tsx:223-224,252,553,567,750) — **`runAgent.ts`엔 분기가 아예 없음**(worker/coordinator 키워드는 tool pool 주석 2줄뿐), 즉 워커 스폰은 Explore·Plan과 완전히 같은 `runAgent` 경로. 갈리는 건 전부 "메인" 한 명뿐: 시스템프롬프트 교체·지휘도구 추가·워커 async 강제 실행·model파라미터 무시·fork비활성·proactive끔. **결론(사용자에게 전달)**: "코디네이터 모드 = 하네스 교체가 아니라 메인의 배역 변경 + 도구셋 조정. 하네스는 하나, 배역만 여럿." — Chain11-⑥의 "서브에이전트는 시스템프롬프트만 갈아끼우고 유령메시지·어태치먼트 배관은 공유"(`runAgent.ts:381`)와 같은 설계 원칙의 연장으로 연결지음.

- **Chain20 — "임베딩검색/BM25/의도분류/고정에이전트워크플로우 없음" 4주장 검증 + "유명기술인데 없는거 또" (신규, ★미착수 — 세그먼트가 여기서 끊김)**: 마지막 사용자 메시지: "임베딩 검색 없음 / BM25 없음 / 의도 분류 없음 / 고정된 에이전트 워크플로우 없음 — 클로드코드에 위에 4개 없는거 맞아? 그리고 유명 기술이지만 없는거 또 뭐가있지?" 어시스턴트는 "좋은 질문이에요. 4개를 하나씩 소스로 검증하고, 없는 것들을 더 찾아보겠습니다."라고만 응답하고 **세그먼트 종료 — grep/Read 등 어떤 도구 호출도 아직 실행되지 않음.**

### Important context, constraints, and user preferences
- 대상 레포: `/Users/seobi/jinsup_space/CC` (현재 `research` 레포와는 별개, `research/notebooks/claude_code`의 GPT-하네스 규약 미적용).
- 사용자 전역 선호(개인 지침, 전 프로젝트 공통): 탐색/분석은 `Explore`, 플래닝은 `Plan` 서브에이전트에 위임하고 실행은 메인에서 직접; 결정/선택 필요시 `AskUserQuestion` 사용, prose로 풀어 묻지 않기.
- 레포 고유 규약(전 세그먼트 통틀어 계속 준수): Claude Code 내부에 대한 모든 비자명한 주장은 `~/jinsup_space/CC/src`를 직접 `grep`/`Read`로 검증하고 "확인 못함" 라벨을 정직하게 씀; 루트 `.md`는 관례상 `html_group_v2/`에 짝꿍 HTML을 두지만 이번 세션 신규 산출물들은 전부 레포 루트에 위치(정식 이동은 재요청시에만); 경로표기는 `~`-상대가 기본, 세션인풋 스냅샷 문서만 절대경로 예외; 새 문서는 기존 톤/구조(번호섹션, file:line 근거, 검증이력) 따름.
- 사용자의 질문 스타일: 좁은 메커니즘 하나를 재질문으로 계속 파고드는 패턴 지속. 이해가 막히면 더 구체적인 시나리오/표/플로우/비유(이번 세그먼트의 "택배 비유" 요청이 대표적)로 재설명을 요구.
- **행동 시그널(반복 재확인, 이번까지 누적 4회 관측)** — 사용자가 어시스턴트의 일반화·누락·과잉확신·과잉알람을 즉시 지적하고, 어시스턴트는 방어 없이 즉시 인정 후 소스로 재검증/표현정정하는 패턴:
  1. 큐웨이크 "4개→6개" 정정 (Chain9).
  2. CLAUDE.md 반영시점 자기정정 — memoize 캐시 발견 (Chain11).
  3. SR census 47종의 3계열 누락 발견 (Chain11).
  4. **[신규]** Chain16 — 어시스턴트가 "스킬 복구 수단이 없다"는 톤을 과하게 알람조로 전달하자, 사용자가 "다음 세션엔 재갱신되니 문제없는거아냐?"라고 반문해 스스로 균형을 잡음 → 어시스턴트가 "①새세션 ②resume ③compact" 3케이스로 명확히 쪼개고 "대처없음"을 "검색수단의 비대칭"으로 표현 정정.
  → **다음 세션 유의사항(갱신)**: 이 사용자는 (a) "다 찾았다"류 완전성 주장을 재검증 압박하는 스타일, (b) 어시스턴트가 위험을 과장하면 반문으로 교정하려는 스타일 — 두 성향 모두, 결론을 내리기 전에 스스로 한 번 더 회의적으로/균형있게 재검토할 것.
- **신규 관찰(이번 세그먼트)**: (1) "반영해"라는 짧은 명령 하나로 직전 채팅 답변 전체를 기존 문서(md+html)에 편입시키길 기대하는 패턴이 Chain13·14/15에서 재확인됨 — 문서 구조·언어를 유지한 채 신규 섹션을 삽입하는 식으로 응답. (2) "전체를 스캔해서 찾아줄래... 워크플로우로... 크게 돌고와라"처럼 대규모 조사에는 명시적으로 `Workflow` 도구(병렬 다중 서브에이전트) 사용을 스스로 요청함(Chain17) — 앞으로도 유사 규모 요청엔 Workflow 우선 고려.
- 날짜/파일명 오타정정 관행(Chain6, "2027"→"2026") — 사용자 확답 아직 못 받음, 낮은 우선순위로 잔존.
- 세션 중 사용자가 실제로 `/compact` 슬래시커맨드를 1회 실행함(Chain16→17 경계 지점) — 이 사실 자체가 Chain16②의 "compact 직후 스킬목록 재고지 관측" 증거로 이미 소진되어 활용됨, 별도 후속조치 불필요.
- 모든 응답은 한국어(세션 초반부터의 지속 제약).

### What remains to be done (next steps)
1. **★최우선**: Chain20 착수 — 사용자의 4가지 "없다" 주장을 각각 `~/jinsup_space/CC/src`에서 grep/Read로 검증:
   - **임베딩 검색** — `embedding`/`vector`/`cosine`/`similarity` 등 키워드 전수 grep, ToolSearch·스킬검색·메모리회상 등 기존에 확인된 검색경로들이 전부 키워드/불리언 매칭임을 재확인하는 방향으로 수렴할 가능성 있음.
   - **BM25** — **이미 부분 검증됨**(Chain7): ToolSearch 스코어링은 "BM25 아님, TF/IDF·문서길이정규화 없이 필드가중치만 하드코딩한 불리언매칭+합산정렬"로 확인 완료. 다른 검색경로(스킬 매칭, 메모리 회상 등)에도 BM25가 없는지 추가 확인만 하면 됨.
   - **의도 분류** — `intent`/`classify`/`classifier`/`router` 등 키워드 grep. 단 `utils/bash/ast.ts`(BASH_CLASSIFIER, Chain17 발견)처럼 "classifier"라는 이름이 붙은 게 이미 존재하므로 "의도 분류가 전혀 없다"는 사용자 전제와 배치될 가능성 — 정직하게 구분해서 답할 것(bash 안전성 분류 ≠ 유저 발화 의도 분류).
   - **고정된 에이전트 워크플로우** — `coordinatorMode.ts`(Chain18)의 코디네이터-워커 지휘규칙, Workflow 도구(Chain17에서 실사용) 등이 "고정 파이프라인"에 해당하는지 재검토 필요 — Workflow는 사용자가 스크립트로 직접 짜는 것이므로 "하네스 내장 고정 워크플로우"와는 다를 수 있음, 구분해서 답할 것.
   - 이어서 "유명 기술이지만 없는 거 또 뭐가 있나" 추가 리스트업 요청에도 답할 것 — Chain17 기술부채 스캔에서 이미 확보한 "설계상 의도적으로 안 쓴 것들" 관련 지식(예: allowlist-not-blocklist 채택, tree-sitter 파서 외부 미공개 등)을 참고자료로 활용 가능.
2. Chain16(스킬 로스트인더미들 구멍), Chain18~19(Coordinator Mode) — 조사 완결됐으나 **문서화 안 됨**(순수 채팅). 재요청 시에만 md/html 작성, 선제적으로 만들지 말 것.
3. Chain1~15는 전부 완료·전달·(해당 시)문서반영까지 완료, 재론 불필요.
4. 낮은 우선순위, 재요청 시에만: `배치-단독-개념-소스증명.md` HTML 짝꿍(미제작); `2026-07-11-...-최신본.html` 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동); "2027→2026" 오타정정 확답 미회수; `클로드코드-기술부채-대장.md`의 특정 카테고리(예: 보안게이트 19건 전체) 더 깊게 파보기.

### Critical data / references needed to continue
- 레포 루트: `/Users/seobi/jinsup_space/CC`; 문서 `md_group/`, HTML 미러 `html_group_v2/`, 재구성 소스 `src/` (1,884개 `.ts`/`.tsx` 파일, 33MB — Chain17 스캔 시 확인된 규모. 디렉토리별 파일수: utils/564·components/389·commands/189·tools/184·services/130·hooks/104·ink/96·bridge/31·constants/21·skills/20 등).
- Chain1~6 근거요약(재검증 없이 인용 가능): 배치파티셔닝 `toolOrchestration.ts:95-116`; 컨텍스트4트랙 `api.ts:449-474`(prependUserContext), `context.ts:155-189`(getUserContext); UserPromptSubmit훅 `hooks.ts:7,977`, `prompts.ts:127-129`; MCP지시 `prompts.ts:160-165`; 캐시경계 `api.ts:321-410`, `prompts.ts:371-372`.
- Chain7 ToolSearch 좌표: `ToolSearchTool.ts`(472줄, call():328-434, select:363-406, 스코어링186-302); `prompt.ts`(isDeferredTool:62-108); `utils/toolSearch.ts`(756줄); `attachments.ts`(getDeferredToolsDeltaAttachment:1454-1475); `claude.ts:1150-1187`; `api.ts:100-224`(defer_loading:223-224). 산출물 `toolsearch-생애주기-소스분석.md`/`.html` — 완결.
- Chain8~9 큐웨이크 좌표(전수): `LocalMainSessionTask.ts:262`; `hooks.ts:225-245`(:238 선포장); `messageQueueManager.ts:120-193`; `useQueueProcessor.ts`(전문); `queueProcessor.ts:1-40`; `task/framework.ts:1-70,190-295`(POLL_INTERVAL_MS=1000); `textInputTypes.ts:263-320`; `LocalShellTask.tsx:89`; `RemoteAgentTask.tsx:179,235,338,356`; `processSlashCommand.tsx:126-133`; `print.ts:5270-5298`; `query.ts:1564-1621`. 산출물 `큐웨이크-엔터없는-진입-소스분석.md` — 완결.
- Chain10 좌표(문서화 안 됨): `constants/xml.ts`(전체); `prompts.ts:576`(null필터); `api.ts:380-396`(캐시경계 배열분할).
- Chain11 좌표(압축, 상세는 신규 산출물로 이관됨): `api.ts:449-474,463,470`; `query.ts:655`; `context.ts:22-34,155-189,184-188`; `constants/common.ts:1-33`(stale wins 주석); 캐시무효화3지점 `caches.ts:52`/`compact.ts:63,117,203`/`postCompactCleanup.ts:59`; `attachments.ts:2661-2751`; `runAgent.ts:381`; `messages.ts` census(62곳 wrap, 44개 WRAP케이스, 3745-3795 queued_command); SR-비어태치먼트3계열: `FileReadTool.ts:706-707,730`, `hooks.ts:238`, `memdir/memoryAge.ts:45-52`, `sideQuestion.ts:61`, `commands/brief.ts:108-114`.
- **Chain12~15 신규 산출물(완결)**: `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html` — §00(2비트 4분면매트릭스)·§01(SR구역: 1-A어태치먼트47종 + 1-B비어태치먼트7종·택배비유 용어표)·§02(isMeta단독4종)·§03(**신규** ReAct사이클전용지도: 3-A SR3채널/3-B 비SR3계열/3-C 통합타임라인)·§04(한줄요약)·검증이력. html은 04(모델전용증명) 아래 05섹션(ReAct 사이클타임라인 7단계단, 자기회복장치 적색배지) 신설. 신규 핵심 소스좌표: `query.ts:1213-1218`(출력한도회복메시지 원문), `query.ts:1314-1317`(토큰예산넛지).
- **Chain16 좌표**: `attachments.ts:2661-2751`(재확인), `compact.ts:524-529`(sentSkillNames 의도적 미리셋 주석 원문 보존 — 위 본문 참조), `conversationRecovery.ts:390-401`(suppressNextSkillListing fire-once latch), `attachments.ts:2685-2697`(EXPERIMENTAL_SKILL_SEARCH, getTurnZeroSkillDiscovery), `SkillTool.ts:389`(DiscoverSkills 원격스킬).
- **Chain17 산출물**: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`(222줄)/`.html`/`-전체287건.json`. Workflow Run ID `wf_89574a3c-93a` / Task ID `w6qkc6gs7` (scratchpad 원본출력 `/private/tmp/claude-501/-Users-seobi-jinsup-space-CC/dd11fb8a-1577-4c24-87dc-918c64250ce1/tasks/w6qkc6gs7.output`, 357,603 bytes — 세션 종속 임시경로라 다음 세션엔 소실 가능성 있음, 영구본은 레포의 `-전체287건.json`). byCategory: 미완공사63·알려진버그42·호환성잔재34·플랫폼한계33·UX타협28·성능타협27·보안게이트19·캐시절약19·기타22. interest분포 5:22·4:92·3:121·2:46·1:6. **본문에 원문 노출된 항목(세그먼트에서 실제로 확인 가능한 것만, 전체 287건 중 일부)**:
  - 캐시절약: `Tool.ts:294`(fork서브에이전트 캐시재활용), `utils/file.ts:275`(Read압축포맷, fleet미캐시 2.18%), `tools/FileReadTool/FileReadTool.ts:526`(dedup stub, fleet 2.64%), `promptSuggestion.ts:313`, `prompts.ts:344`(글로벌캐시프리픽스 배치제약), `memdir.ts:329`(자정날짜 스테일 방치).
  - 알려진버그: `utils/cronTasks.ts:336`(cron 7일만료, p99 61분→53h), `utils/messages.ts:5441`(tool_use/tool_result placeholder주입, inc-4977), `utils/sessionStorage.ts:2212`(resume드리프트 397K→1.65M, adamr-20260320), `utils/toolResultStorage.ts:280`(capybara stop-sequence, inc-4586), `tools/PowerShellTool/pathValidation.ts:276,587`(New-Item -Name/-Path 불일치·write cmdlet Read deny 미적용), `main.tsx:2010`, `utils/config.ts:781`, `hooks.ts:1850`, `utils/worktree.ts:590`.
  - 보안게이트: `utils/bash/ast.ts:1860`(PS4인젝션 allowlist, 5회우회패치), `setup.ts:419`(Desktop앱 샌드박스검증 면제), `utils/doctorDiagnostic.ts:322`, `utils/subprocessEnv.ts:11`(GITHUB_TOKEN 스크럽제외), `utils/bash/parser.ts:61`(tree-sitter 내부빌드전용), `ssrfGuard.ts:12`(루프백 허용).
  - 플랫폼한계: `tools/BashTool/bashPermissions.ts:81`(Bun DCE cliff), `tools/ScheduleCronTool/prompt.ts:105`(thundering herd 어긋난분배정), `utils/api.ts:197`, `utils/crypto.ts:7`, `src/utils/gracefulShutdown.ts:238`.
- **Chain18~19 좌표**: `coordinator/coordinatorMode.ts`(전체 — `isCoordinatorMode():849-854`, `INTERNAL_WORKER_TOOLS:31,842-847`, `getCoordinatorSystemPrompt():111-175`); 소비처 전수 `tools.ts:281,293` / `main.tsx:2198,3768,4590` / `resumeAgent.ts:251` / `forkSubagent.ts:34` / `AgentTool/prompt.ts:68,216` / `AgentTool.tsx:223-224,252,553,567,750` — `runAgent.ts`엔 분기 없음(워커=일반서브에이전트 동일경로).
- **산출물 전체 목록(재작성금지, 상태최신)**:
  - `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` — 완성.
  - `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`/`.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`/`.html` — 완결.
  - `/Users/seobi/jinsup_space/CC/큐웨이크-엔터없는-진입-소스분석.md` — 완결.
  - `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html` — **완결**(§00~§05, 브라우저 열림).
  - `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`/`.html`/`-전체287건.json` — **완결**(브라우저 열림).
  - Chain10(XML vs MD), Chain16(스킬 로스트인더미들), Chain18~19(Coordinator Mode) — **문서화 안 됨, 순수 채팅 답변만.** 재요청 시에만 작성.
- PostCompact훅 관찰(정보성, 재검증 안함): `~/.claude/scripts/cc-name.sh` → `hs -c bigAlert(...)`.

## 단계 2

Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:

### Current progress and key decisions made

- **Session goal (unchanged)**: 사용자가 `/Users/seobi/jinsup_space/CC` (Claude Code 내부를 리버스엔지니어링하는 리서치 레포: `md_group/` 분석 문서, `html_group_v2/` HTML 시각화, `src/` 재구성 소스)를 대상으로 세부 메커니즘을 하나씩 깊게 파고드는 세션. 이번이 **6번째 컴팩션 사이클**.

- **Chain 1~6 (전부 완전 종결, 재론 불필요 — 이전 요약본 수준 압축 유지)**:
  - Chain1 — 배치 병렬/파티셔닝: `partitionToolCalls`가 `isConcurrencySafe` per-tool 선언만으로 병렬/단독 배치 분리. 산출물 `배치-단독-개념-소스증명.md`.
  - Chain2 — 컨텍스트 주입 4트랙: 0번 유령 메시지 vs skill_listing vs conditional rules vs frontmatter. 산출물 `컨텍스트-주입-4트랙-시각설명.html`.
  - Chain3 — UserPromptSubmit훅/`getHooksSection()`: 무조건 시스템프롬프트 포함, 훅은 하네스가 `spawn`으로 직접실행. MCP지시 2배달모드. 캐시경계 `SYSTEM_PROMPT_DYNAMIC_BOUNDARY`.
  - Chain4 — 세션인풋 전문 스냅샷 문서화(자기전사). Chain6에서 리네임됨.
  - Chain5 — src vs 실서비스 diff 마커 grep검증 CLOSED.
  - Chain6 — "2027"→2026 오타정정 + `/visual-explainer` 청사진 HTML. 산출물 `2026-07-11-시스템프롬프트및도구내용-최신본.md`/`.html`.

- **Chain7 — ToolSearch 지연로딩 5단계 생애주기 완전규명 (완결)**: 분류→모드게이트→고지(`deferred_tools_delta`)→검색(**BM25 아님** — TF/IDF·문서길이정규화 없이 필드가중치 하드코딩 불리언매칭+합산정렬)→로드/재조립. 카드목록 발행은 ToolSearch 호출과 무관, 어태치먼트 파이프라인이 수집지점마다 발행. 로스트인더미들 4중 안전망. 산출물 `toolsearch-생애주기-소스분석.md`/`.html` — **완결.**

- **Chain8~9 — 큐웨이크(엔터 없는 진입) 완전규명, "4개→6개" 자기정정 (완결)**: 대화를 전진시키는 문 3개(유저엔터/사이클꼬리/큐웨이크) 중 큐웨이크가 최종 **6개 도어**로 확정 — ①백그라운드완료 ②Stop훅차단 ③원격입력 ④스케줄(isMeta) ⑤비동기에이전트 결과 숨은프롬프트 재진입(스케줄 배관의 실체) ⑥고아권한응답. 산출물 `큐웨이크-엔터없는-진입-소스분석.md` — **완결.**

- **Chain10 — "왜 XML 아니라 MD로 시스템프롬프트를 구성했나" (완결, 문서화 안 됨 — 순수 채팅)**: 실제론 MD/XML 역할분담(산문지시=MD, 경계·출처표시 화물=XML). "왜 본문이 MD인가" 최종 근거서열: 1위 **내용충돌**(본문이 XML태그를 리터럴 언급 — 자기완결 XML조각으로 바꿔도 이 문제는 여전히 발생, MD헤더는 안 부딪힘) > 2위 태그희소성=신호강도 > 3위 토큰/유지보수. 역산추론이라는 정직표기 유지.

- **Chain11 — "0번째 유저프롬프트"(유령메시지) 다회전 심화, 10라운드 (완전 종결 — 이번 세그먼트 Chain12에서 마지막 총정리 답변 전달 + 문서화까지 완료)**: 핵심 확정사실만 압축 보존(상세는 `시스템리마인더-isMeta-신분증-총정리.md`에 전량 이관됨) —
  - 유령메시지(`prependUserContext`, api.ts:449-474)는 API호출부(`query.ts:655`)에 **인라인**으로 박혀 사이클마다 재실행되나, `getUserContext`가 `memoize`(`context.ts:155`)돼 있어 **세션 첫 호출 1회만** 디스크에서 읽힘. 캐시 무효화는 전수 확인 결과 **3곳뿐**: `/clear`(`caches.ts:52`), `/compact`(`compact.ts:63,117,203`), auto-compact 정리(`postCompactCleanup.ts:59`). 설계철학: "stale wins"(`constants/common.ts:17-23` 주석) — 0번은 얼리고 변경분은 꼬리 델타로.
  - 유령 리턴값은 `{claudeMd, currentDate(+userEmail)}`뿐, 스킬/도구/에이전트 목록은 전부 별도 어태치먼트 채널(변할 수 있는 것=꼬리델타 원칙).
  - `getSkillListingAttachments`(attachments.ts:2661-2751): 기본시나리오=첫엔터에 전체발행, 단서 3개(Skill툴없는에이전트스킵/--resume시 suppressNext/예산1%+250자컷).
  - CLAUDE.md가 시스템프롬프트 대신 0번 유저메시지에 있는 이유(추론, 근거강도순): ①권위계층분리(참고자료 어조로 프롬프트인젝션 벡터 격리, 단 "OVERRIDE" 문구로 권위는 승격) ②서브에이전트 모듈성(`runAgent.ts:381`, 시스템프롬프트는 에이전트별 교체·유령은 공유) ③글로벌캐시 조각방지(부분적) ④채널일관성.
  - `messages.ts` 렌더링 전수(62곳 wrap호출): system-reminder 예외 3개(ToolSearch결과/`queued_command`은 조건부isMeta일뿐 래핑은 항상/스킬본문은 안 감쌈).
  - **1차 census 47종 6계열은 messages.ts 어태치먼트 스위치 하나만 훑은 것이었고, 사용자 재지적으로 3개 추가 층위(인라인/선포장/특수직조립) 발견** — 이 3계열 발견이 Chain12~15의 씨앗이 됨.
  - **자기정정 3회 발생**(큐웨이크4→6, CLAUDE.md 반영시점 오답 정정, 47종census의 3계열 누락) — round5에서 이미 "다음세션 유의사항"으로 등록됨, 이번 세그먼트에서도 재확인(아래 행동시그널 참조).

- **Chain12 — Chain11 "총정리" 답변 전달 + md/html 문서화 (신규, 완결)**: 사용자의 마지막 요청("system-reminder 진입것들=어태치먼트뭉뚱그림+나머지개별나열 / 아닌데 isMeta=true인것도")에 통합표로 답변 후, md 먼저 작성 → `/visual-explainer`로 HTML 빌드. 신규 산출물: `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html`("컨텍스트 세관 — 출입증 검문소" 메타포, 4분면 매트릭스+SR구역+isMeta단독구역+모델전용증명). 구조: Ⅰ.SR로 들어가는것(어태치먼트47종일괄 + 비어태치먼트7종3층위) / Ⅱ.SR없는 isMeta=true(스킬본문·이미지PDF·슬래시확장+비동기재진입·기타합성) / Ⅲ.2×2매트릭스(SR+isMeta=하네스방송 / SR+~isMeta=포장된유저육성 / ~SR+isMeta=숨은정식입력).

- **Chain13 — "인라인/선포장/직조립" 용어를 택배 비유로 재설명 + 문서 반영 (신규, 완결)**: 사용자가 Chain12 용어를 이해 못 함("하나~~도모루ㅡ겠어") → 택배 비유로 재설명: 어태치먼트=공장일괄포장(렌더러, 출고직전) / 인라인=본문에 인쇄된 경고문(포장자체가 없음, tool_result 문자열 일부, FileReadTool.ts:706-707/730) / 선포장=집에서미리싸서우체통에(`enqueuePendingNotification({value: wrapInSystemReminder(...)})`, hooks.ts:238, 큐진입 전 이미 포장) / 직조립=그자리에서싸서그자리에서전달(`sideQuestion.ts:61`, 큐도 파이프라인도 안 거침). 사용자 "반영해" → md(1-B 머리에 용어안내표)·html(02섹션 위 B-0 범례) 양쪽에 편입 완료, 재오픈.

- **Chain14 — ReAct 사이클 전용 SR 지도 (신규, 완결)**: "엔터 못 치는 ReAct 구간에서 어태치먼트 말고 또 SR 보내는 거 있나?"에 답 — 사이클 중 SR 배달 **3채널**: ⓐ유령재인쇄(API직전 매호출, `query.ts:655`, 내용은 동결이라 새정보 아님) ⓑ**tool_result 인라인(★ReAct 전용 — 도구 실행 중에만 존재 가능, 빈파일경고·멀웨어지침·메모리신선도경고)** ⓒ사이클꼬리 어태치먼트일괄(델타·알림·훅산출물·`next`큐드레인 포함, 아는 채널). 헷갈리는 경계 2개 명시(미드턴메시지·훅출력은 결국 ⓒ로 배달).

- **Chain15 — ReAct 사이클 중 비SR 자동메시지 규명 (신규, 완결)**: "SR 아니어도 사이클 중 자동으로 보내는 메시지 더 있나?"에 답하려 `query.ts:1205-1225`, `1300-1325` Read로 기존 미확인 2곳 정체 확정. 결과 3계열: **A) tool_result 채널**(정상결과/합성에러/형제중단결과/tool_reference블록) **B) SR없는 isMeta user메시지 5종**(①스킬본문 ②이미지PDF동반메시지 ③★신규확정 출력한도회복메시지 — `query.ts:1213-1218`, "Output token limit hit. Resume directly — no apology, no recap... Pick up mid-thought" ④★신규확정 토큰예산넛지 — `query.ts:1314-1317` ⑤대화복구메시지) **C) 메시지 개조**(전처리 5단의 autocompact·microcompact·applyToolResultBudget — 새 메시지가 아니라 기존 대화 변형). "모델이 잘렸다가 사과없이 이어말하는 현상"=③이 작동한 순간이라고 사용자 체감으로 번역. **Chain14+15 모두 사용자 "둘다 md/html 반영해" 요청으로 문서에 편입 완료** — md에 새 §03 "ReAct 사이클 전용 지도"(3-A/3-B/3-C, 기존 한줄요약은 §04로 밀림) 삽입, html에 05섹션(사이클타임라인 7단계단 + 자기회복장치 적색배지) 신설, 재오픈.

- **Chain16 — 스킬 vs ToolSearch "로스트인더미들" 검색복구 비대칭, 3라운드 심화 (신규, 완결 — 문서화 안 됨)**:
  1. 사용자 지적: "Skill도 도중 추가되면 목록에 델타로 들어가는데, 대화가 밀려 로스트인더미들 되면? ToolSearch같은 검색복구가 스킬엔 있나?" → 조사: **ToolSearch는 `tools.filter(isDeferredTool)` — 도구 전용, 스킬 관할 밖.** compact 후 `sentSkillNames` **의도적으로 리셋 안 함**(compact.ts:524-529 주석 원문: "Intentionally NOT resetting sentSkillNames: re-injecting the full skill_listing (~4K tokens) post-compact is pure cache_creation with marginal benefit. The model still has SkillTool in its schema and invoked_skills attachment preserves used-skill content."). resume도 `suppressNextSkillListing`으로 억제(conversationRecovery.ts:390-401, fire-once latch). 방어선 3개(invoked_skills 어태치먼트=쓴것만/유저 `/이름` 명시호출/Skill툴 표지판=목록있다고만 알림, 재검색은 못 시킴) — 구멍: 미사용+미언급 스킬은 존재소멸. **해법 공사 중**: `EXPERIMENTAL_SKILL_SEARCH`(attachments.ts:2685-2697) — `getTurnZeroSkillDiscovery`가 매 턴 시작에 유저입력↔스킬 매칭해 관련 스킬만 그때그때 주입, 원격스킬용 `DiscoverSkills` 도구(SkillTool.ts:389)도 별도 존재. 대비구도: "도구=모델주도검색(ToolSearch) / 스킬=하네스가 매턴 대신 검색(turn-0 discovery, 한 세대 진화형)".
  2. 사용자가 어시스턴트의 알람성 프레이밍에 반문("대처가없다는거야? compact하면 스킬목록 날아간다고?? 다음세션 첫메시지땐 전체 재갱신되니 문제없는거아냐?") → **어시스턴트 자기정정**: 3상황 명확히 분리 — ①**새 세션**: 문제없음(프로세스메모리 장부 리셋→전체재고지, 사용자 말이 맞음) ②**resume**: 소실 아님(옛 트랜스크립트에 목록 그대로 있음, 재고지만 억제) ③**같은 세션 내 compact**: 장부는 프로세스메모리라 살아있는데 대화만 요약으로 교체돼 재고지 안 됨(구버전 정책 기준)이 유일한 위험구간. **실측 반전**: 이 세션에서 사용자가 실제로 `/compact` 실행 직후 전체 스킬목록이 어시스턴트 컨텍스트에 재고지된 것을 관측 — 현행 배포판은 구버전 스냅샷의 "의도적 미재주입" 정책과 다른 것으로 보임(③의 공포 상당히 완화). "대처가 없다"의 정확한 의미를 "소실이 아니라 도구엔 있는 능동 검색복구로가 스킬엔 없다는 뜻"으로 표현 정정.
  3. 사용자가 원래 시나리오(대화 밀려 묻힌 스킬)로 재요청 → 최종 정리: 하네스 대처는 "**소극적 3종**"뿐 — ①표지판(상시, "목록에 없는건 추측말라"지만 재검색은 못 시킴) ②유저 명시호출(완전우회, 사실상 유저에게 떠넘김) ③compact 리프레시(간접·우연, 설계된 대처 아님). 없는 것: 주기적재고지✗·스킬검색도구✗·자동매칭✗(기본모드). 결론: "**기본 모드의 인정된 구멍**" — EXPERIMENTAL_SKILL_SEARCH가 정확히 이 구멍을 메우려는 실험.

- **Chain17 — "기술부채 대장" 전체 소스 Workflow 스캔, 287건 확정 (신규, 완결, 대형 산출물 3건)**: 사용자가 "이러한 빚이 뭐가 더 있는지 워크플로우로 전체 소스코드 싹다 스캔해서 찾아줄래... 크게 돌고와라"라고 명시적으로 Workflow 요청 → `debt-hunt` 워크플로우(Run ID `wf_89574a3c-93a`, Task ID `w6qkc6gs7`)를 src 1,884파일/33MB 전체에 13개 샤드 병렬 Scan(부채마커 30여종: Intentionally/trade-off/for now/stopgap/stale wins/marginal benefit/workaround/TOCTOU/silently drop 등) + 12건 배치 Verify(적대적판정+카테고리교정+흥미도1~5) 2-phase로 백그라운드 발사. **완료 결과(큐웨이크①번 완료알림으로 자동 기동)**: 총 **287건**, byCategory: 미완공사63·알려진버그42·호환성잔재34·플랫폼한계33·UX타협28·성능타협27·보안게이트19·캐시절약19·기타22. 47에이전트, 918도구호출, 2,631,759 서브에이전트토큰, 1,539,682ms(~26분). interest분포: 5=22건·4=92·3=121·2=46·1=6.
  - **핵심 통찰**(사용자에게 전달됨): 이 코드베이스의 빚은 대부분 BigQuery 실측치나 인시던트 번호로 "무엇을 포기하면 얼마를 아끼는지" 계량돼 있음 — "몰라서"가 아니라 "재고 끝에 남긴" 빚. **반복 상환회피 3패턴**: ①탐지로 대체(버그 대신 BQ 감시) ②킬스위치로 담보 ③기능축소로 봉합.
  - **compact/스킬 논의(Chain11·16)와 직결된 발견**: `memdir.ts:329`(자정 후 날짜를 일부러 스테일 방치 — date_change 꼬리첨부가 이걸 보정), `Tool.ts:294`(포크 서브에이전트가 부모 프롬프트캐시 재활용 위해 최신 프롬프트 반영 포기), `attachments.ts:1408`(messages[0] 날짜 안 갱신, 캐시 무효화 방지).
  - 사용자가 체감할 만한 것 3개: cron 예약 7일 뒤 조용히 증발 / resume 시 다른 크기의 대화 로드 / Windows 실시간 스트리밍 전면 비활성.
  - 산출물: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`(222줄, 카테고리9종×흥미도4~5 정제 96건 표), `.html`(`/visual-explainer`, "부채 장부" 컨셉, CSS 오타 `--pink:#ff7 eb` 수정), `-전체287건.json`(원본 287건 전량, scratchpad `debt_findings.json`에서 복사). 전부 브라우저 오픈 완료.
  - 한계 정직표기(사용자에게 전달됨): grep 마커 기반이라 마커 없는 침묵형 빚은 놓쳤을 수 있음, 흥미도·카테고리는 검증관 LLM 판정.

- **Chain18 — Coordinator Mode(명시적 수퍼바이저 패턴) 발굴 (신규, 완결 — 문서화 안 됨)**: 사용자 질문 "클로드코드의 수퍼바이저 패턴이 있어?"(세션 중 사용자가 실제 `/compact` 명령을 1회 실행한 직후 새 주제로 전환됨) → grep으로 `src/coordinator/coordinatorMode.ts` 전용 모듈 발견. **2개 층위**: 층위1=항상 있는 암묵적 수퍼바이저(Agent 툴 기반 서브에이전트 위임, task-notification 콜백 — 이번 세션의 debt-hunt Workflow가 확장형). 층위2=**전용 Coordinator Mode**(`isCoordinatorMode()`, `COORDINATOR_MODE` feature flag + `CLAUDE_CODE_COORDINATOR_MODE` env). `getCoordinatorSystemPrompt()`(coordinatorMode.ts:111-175)가 메인의 시스템프롬프트를 통째로 교체: "You are Claude Code, an AI assistant that orchestrates software engineering tasks across multiple workers. You are a coordinator." 도구: AgentTool(워커스폰)/SendMessageTool(기존워커후속지시)/TaskStopTool(워커중단)/subscribe_pr_activity. 지휘규칙 인용: "워커로 다른 워커 감시 금지"·"사소한 일에 워커 쓰지 말기"·"워커 결과 예측·조작 금지"·"매 메시지는 유저에게". Swarm/Team 확장(`INTERNAL_WORKER_TOOLS`: TeamCreate/TeamDelete/SendMessage/SyntheticOutput, `utils/swarm/inProcessRunner.ts`)까지 있어 워커간 상호통신도 가능한 진짜 멀티에이전트 오케스트레이션.

- **Chain19 — Coordinator Mode도 공통 단일 하네스 확인 (신규, 완결 — 문서화 안 됨)**: 사용자 질문 "Coordinator Mode 쓰더라도 서브에이전트 하네스는 안 바뀌지? 전체 공통하네스쓰지?" → `isCoordinatorMode()` 전체 소비처 grep 전수(tools.ts:281,293 / main.tsx:2198,3768,4590 / resumeAgent.ts:251 / forkSubagent.ts:34 / AgentTool/prompt.ts:68,216 / AgentTool.tsx:223-224,252,553,567,750) — **`runAgent.ts`엔 분기가 아예 없음**(worker/coordinator 키워드는 tool pool 주석 2줄뿐), 즉 워커 스폰은 Explore·Plan과 완전히 같은 `runAgent` 경로. 갈리는 건 전부 "메인" 한 명뿐: 시스템프롬프트 교체·지휘도구 추가·워커 async 강제 실행·model파라미터 무시·fork비활성·proactive끔. **결론(사용자에게 전달)**: "코디네이터 모드 = 하네스 교체가 아니라 메인의 배역 변경 + 도구셋 조정. 하네스는 하나, 배역만 여럿." — Chain11-⑥의 "서브에이전트는 시스템프롬프트만 갈아끼우고 유령메시지·어태치먼트 배관은 공유"(`runAgent.ts:381`)와 같은 설계 원칙의 연장으로 연결지음.

- **Chain20 — "임베딩검색/BM25/의도분류/고정에이전트워크플로우 없음" 4주장 검증 + "유명기술인데 없는거 또" (신규, ★미착수 — 세그먼트가 여기서 끊김)**: 마지막 사용자 메시지: "임베딩 검색 없음 / BM25 없음 / 의도 분류 없음 / 고정된 에이전트 워크플로우 없음 — 클로드코드에 위에 4개 없는거 맞아? 그리고 유명 기술이지만 없는거 또 뭐가있지?" 어시스턴트는 "좋은 질문이에요. 4개를 하나씩 소스로 검증하고, 없는 것들을 더 찾아보겠습니다."라고만 응답하고 **세그먼트 종료 — grep/Read 등 어떤 도구 호출도 아직 실행되지 않음.**

### Important context, constraints, and user preferences
- 대상 레포: `/Users/seobi/jinsup_space/CC` (현재 `research` 레포와는 별개, `research/notebooks/claude_code`의 GPT-하네스 규약 미적용).
- 사용자 전역 선호(개인 지침, 전 프로젝트 공통): 탐색/분석은 `Explore`, 플래닝은 `Plan` 서브에이전트에 위임하고 실행은 메인에서 직접; 결정/선택 필요시 `AskUserQuestion` 사용, prose로 풀어 묻지 않기.
- 레포 고유 규약(전 세그먼트 통틀어 계속 준수): Claude Code 내부에 대한 모든 비자명한 주장은 `~/jinsup_space/CC/src`를 직접 `grep`/`Read`로 검증하고 "확인 못함" 라벨을 정직하게 씀; 루트 `.md`는 관례상 `html_group_v2/`에 짝꿍 HTML을 두지만 이번 세션 신규 산출물들은 전부 레포 루트에 위치(정식 이동은 재요청시에만); 경로표기는 `~`-상대가 기본, 세션인풋 스냅샷 문서만 절대경로 예외; 새 문서는 기존 톤/구조(번호섹션, file:line 근거, 검증이력) 따름.
- 사용자의 질문 스타일: 좁은 메커니즘 하나를 재질문으로 계속 파고드는 패턴 지속. 이해가 막히면 더 구체적인 시나리오/표/플로우/비유(이번 세그먼트의 "택배 비유" 요청이 대표적)로 재설명을 요구.
- **행동 시그널(반복 재확인, 이번까지 누적 4회 관측)** — 사용자가 어시스턴트의 일반화·누락·과잉확신·과잉알람을 즉시 지적하고, 어시스턴트는 방어 없이 즉시 인정 후 소스로 재검증/표현정정하는 패턴:
  1. 큐웨이크 "4개→6개" 정정 (Chain9).
  2. CLAUDE.md 반영시점 자기정정 — memoize 캐시 발견 (Chain11).
  3. SR census 47종의 3계열 누락 발견 (Chain11).
  4. **[신규]** Chain16 — 어시스턴트가 "스킬 복구 수단이 없다"는 톤을 과하게 알람조로 전달하자, 사용자가 "다음 세션엔 재갱신되니 문제없는거아냐?"라고 반문해 스스로 균형을 잡음 → 어시스턴트가 "①새세션 ②resume ③compact" 3케이스로 명확히 쪼개고 "대처없음"을 "검색수단의 비대칭"으로 표현 정정.
  → **다음 세션 유의사항(갱신)**: 이 사용자는 (a) "다 찾았다"류 완전성 주장을 재검증 압박하는 스타일, (b) 어시스턴트가 위험을 과장하면 반문으로 교정하려는 스타일 — 두 성향 모두, 결론을 내리기 전에 스스로 한 번 더 회의적으로/균형있게 재검토할 것.
- **신규 관찰(이번 세그먼트)**: (1) "반영해"라는 짧은 명령 하나로 직전 채팅 답변 전체를 기존 문서(md+html)에 편입시키길 기대하는 패턴이 Chain13·14/15에서 재확인됨 — 문서 구조·언어를 유지한 채 신규 섹션을 삽입하는 식으로 응답. (2) "전체를 스캔해서 찾아줄래... 워크플로우로... 크게 돌고와라"처럼 대규모 조사에는 명시적으로 `Workflow` 도구(병렬 다중 서브에이전트) 사용을 스스로 요청함(Chain17) — 앞으로도 유사 규모 요청엔 Workflow 우선 고려.
- 날짜/파일명 오타정정 관행(Chain6, "2027"→"2026") — 사용자 확답 아직 못 받음, 낮은 우선순위로 잔존.
- 세션 중 사용자가 실제로 `/compact` 슬래시커맨드를 1회 실행함(Chain16→17 경계 지점) — 이 사실 자체가 Chain16②의 "compact 직후 스킬목록 재고지 관측" 증거로 이미 소진되어 활용됨, 별도 후속조치 불필요.
- 모든 응답은 한국어(세션 초반부터의 지속 제약).

### What remains to be done (next steps)
1. **★최우선**: Chain20 착수 — 사용자의 4가지 "없다" 주장을 각각 `~/jinsup_space/CC/src`에서 grep/Read로 검증:
   - **임베딩 검색** — `embedding`/`vector`/`cosine`/`similarity` 등 키워드 전수 grep, ToolSearch·스킬검색·메모리회상 등 기존에 확인된 검색경로들이 전부 키워드/불리언 매칭임을 재확인하는 방향으로 수렴할 가능성 있음.
   - **BM25** — **이미 부분 검증됨**(Chain7): ToolSearch 스코어링은 "BM25 아님, TF/IDF·문서길이정규화 없이 필드가중치만 하드코딩한 불리언매칭+합산정렬"로 확인 완료. 다른 검색경로(스킬 매칭, 메모리 회상 등)에도 BM25가 없는지 추가 확인만 하면 됨.
   - **의도 분류** — `intent`/`classify`/`classifier`/`router` 등 키워드 grep. 단 `utils/bash/ast.ts`(BASH_CLASSIFIER, Chain17 발견)처럼 "classifier"라는 이름이 붙은 게 이미 존재하므로 "의도 분류가 전혀 없다"는 사용자 전제와 배치될 가능성 — 정직하게 구분해서 답할 것(bash 안전성 분류 ≠ 유저 발화 의도 분류).
   - **고정된 에이전트 워크플로우** — `coordinatorMode.ts`(Chain18)의 코디네이터-워커 지휘규칙, Workflow 도구(Chain17에서 실사용) 등이 "고정 파이프라인"에 해당하는지 재검토 필요 — Workflow는 사용자가 스크립트로 직접 짜는 것이므로 "하네스 내장 고정 워크플로우"와는 다를 수 있음, 구분해서 답할 것.
   - 이어서 "유명 기술이지만 없는 거 또 뭐가 있나" 추가 리스트업 요청에도 답할 것 — Chain17 기술부채 스캔에서 이미 확보한 "설계상 의도적으로 안 쓴 것들" 관련 지식(예: allowlist-not-blocklist 채택, tree-sitter 파서 외부 미공개 등)을 참고자료로 활용 가능.
2. Chain16(스킬 로스트인더미들 구멍), Chain18~19(Coordinator Mode) — 조사 완결됐으나 **문서화 안 됨**(순수 채팅). 재요청 시에만 md/html 작성, 선제적으로 만들지 말 것.
3. Chain1~15는 전부 완료·전달·(해당 시)문서반영까지 완료, 재론 불필요.
4. 낮은 우선순위, 재요청 시에만: `배치-단독-개념-소스증명.md` HTML 짝꿍(미제작); `2026-07-11-...-최신본.html` 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동); "2027→2026" 오타정정 확답 미회수; `클로드코드-기술부채-대장.md`의 특정 카테고리(예: 보안게이트 19건 전체) 더 깊게 파보기.

### Critical data / references needed to continue
- 레포 루트: `/Users/seobi/jinsup_space/CC`; 문서 `md_group/`, HTML 미러 `html_group_v2/`, 재구성 소스 `src/` (1,884개 `.ts`/`.tsx` 파일, 33MB — Chain17 스캔 시 확인된 규모. 디렉토리별 파일수: utils/564·components/389·commands/189·tools/184·services/130·hooks/104·ink/96·bridge/31·constants/21·skills/20 등).
- Chain1~6 근거요약(재검증 없이 인용 가능): 배치파티셔닝 `toolOrchestration.ts:95-116`; 컨텍스트4트랙 `api.ts:449-474`(prependUserContext), `context.ts:155-189`(getUserContext); UserPromptSubmit훅 `hooks.ts:7,977`, `prompts.ts:127-129`; MCP지시 `prompts.ts:160-165`; 캐시경계 `api.ts:321-410`, `prompts.ts:371-372`.
- Chain7 ToolSearch 좌표: `ToolSearchTool.ts`(472줄, call():328-434, select:363-406, 스코어링186-302); `prompt.ts`(isDeferredTool:62-108); `utils/toolSearch.ts`(756줄); `attachments.ts`(getDeferredToolsDeltaAttachment:1454-1475); `claude.ts:1150-1187`; `api.ts:100-224`(defer_loading:223-224). 산출물 `toolsearch-생애주기-소스분석.md`/`.html` — 완결.
- Chain8~9 큐웨이크 좌표(전수): `LocalMainSessionTask.ts:262`; `hooks.ts:225-245`(:238 선포장); `messageQueueManager.ts:120-193`; `useQueueProcessor.ts`(전문); `queueProcessor.ts:1-40`; `task/framework.ts:1-70,190-295`(POLL_INTERVAL_MS=1000); `textInputTypes.ts:263-320`; `LocalShellTask.tsx:89`; `RemoteAgentTask.tsx:179,235,338,356`; `processSlashCommand.tsx:126-133`; `print.ts:5270-5298`; `query.ts:1564-1621`. 산출물 `큐웨이크-엔터없는-진입-소스분석.md` — 완결.
- Chain10 좌표(문서화 안 됨): `constants/xml.ts`(전체); `prompts.ts:576`(null필터); `api.ts:380-396`(캐시경계 배열분할).
- Chain11 좌표(압축, 상세는 신규 산출물로 이관됨): `api.ts:449-474,463,470`; `query.ts:655`; `context.ts:22-34,155-189,184-188`; `constants/common.ts:1-33`(stale wins 주석); 캐시무효화3지점 `caches.ts:52`/`compact.ts:63,117,203`/`postCompactCleanup.ts:59`; `attachments.ts:2661-2751`; `runAgent.ts:381`; `messages.ts` census(62곳 wrap, 44개 WRAP케이스, 3745-3795 queued_command); SR-비어태치먼트3계열: `FileReadTool.ts:706-707,730`, `hooks.ts:238`, `memdir/memoryAge.ts:45-52`, `sideQuestion.ts:61`, `commands/brief.ts:108-114`.
- **Chain12~15 신규 산출물(완결)**: `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html` — §00(2비트 4분면매트릭스)·§01(SR구역: 1-A어태치먼트47종 + 1-B비어태치먼트7종·택배비유 용어표)·§02(isMeta단독4종)·§03(**신규** ReAct사이클전용지도: 3-A SR3채널/3-B 비SR3계열/3-C 통합타임라인)·§04(한줄요약)·검증이력. html은 04(모델전용증명) 아래 05섹션(ReAct 사이클타임라인 7단계단, 자기회복장치 적색배지) 신설. 신규 핵심 소스좌표: `query.ts:1213-1218`(출력한도회복메시지 원문), `query.ts:1314-1317`(토큰예산넛지).
- **Chain16 좌표**: `attachments.ts:2661-2751`(재확인), `compact.ts:524-529`(sentSkillNames 의도적 미리셋 주석 원문 보존 — 위 본문 참조), `conversationRecovery.ts:390-401`(suppressNextSkillListing fire-once latch), `attachments.ts:2685-2697`(EXPERIMENTAL_SKILL_SEARCH, getTurnZeroSkillDiscovery), `SkillTool.ts:389`(DiscoverSkills 원격스킬).
- **Chain17 산출물**: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`(222줄)/`.html`/`-전체287건.json`. Workflow Run ID `wf_89574a3c-93a` / Task ID `w6qkc6gs7` (scratchpad 원본출력 `/private/tmp/claude-501/-Users-seobi-jinsup-space-CC/dd11fb8a-1577-4c24-87dc-918c64250ce1/tasks/w6qkc6gs7.output`, 357,603 bytes — 세션 종속 임시경로라 다음 세션엔 소실 가능성 있음, 영구본은 레포의 `-전체287건.json`). byCategory: 미완공사63·알려진버그42·호환성잔재34·플랫폼한계33·UX타협28·성능타협27·보안게이트19·캐시절약19·기타22. interest분포 5:22·4:92·3:121·2:46·1:6. **본문에 원문 노출된 항목(세그먼트에서 실제로 확인 가능한 것만, 전체 287건 중 일부)**:
  - 캐시절약: `Tool.ts:294`(fork서브에이전트 캐시재활용), `utils/file.ts:275`(Read압축포맷, fleet미캐시 2.18%), `tools/FileReadTool/FileReadTool.ts:526`(dedup stub, fleet 2.64%), `promptSuggestion.ts:313`, `prompts.ts:344`(글로벌캐시프리픽스 배치제약), `memdir.ts:329`(자정날짜 스테일 방치).
  - 알려진버그: `utils/cronTasks.ts:336`(cron 7일만료, p99 61분→53h), `utils/messages.ts:5441`(tool_use/tool_result placeholder주입, inc-4977), `utils/sessionStorage.ts:2212`(resume드리프트 397K→1.65M, adamr-20260320), `utils/toolResultStorage.ts:280`(capybara stop-sequence, inc-4586), `tools/PowerShellTool/pathValidation.ts:276,587`(New-Item -Name/-Path 불일치·write cmdlet Read deny 미적용), `main.tsx:2010`, `utils/config.ts:781`, `hooks.ts:1850`, `utils/worktree.ts:590`.
  - 보안게이트: `utils/bash/ast.ts:1860`(PS4인젝션 allowlist, 5회우회패치), `setup.ts:419`(Desktop앱 샌드박스검증 면제), `utils/doctorDiagnostic.ts:322`, `utils/subprocessEnv.ts:11`(GITHUB_TOKEN 스크럽제외), `utils/bash/parser.ts:61`(tree-sitter 내부빌드전용), `ssrfGuard.ts:12`(루프백 허용).
  - 플랫폼한계: `tools/BashTool/bashPermissions.ts:81`(Bun DCE cliff), `tools/ScheduleCronTool/prompt.ts:105`(thundering herd 어긋난분배정), `utils/api.ts:197`, `utils/crypto.ts:7`, `src/utils/gracefulShutdown.ts:238`.
- **Chain18~19 좌표**: `coordinator/coordinatorMode.ts`(전체 — `isCoordinatorMode():849-854`, `INTERNAL_WORKER_TOOLS:31,842-847`, `getCoordinatorSystemPrompt():111-175`); 소비처 전수 `tools.ts:281,293` / `main.tsx:2198,3768,4590` / `resumeAgent.ts:251` / `forkSubagent.ts:34` / `AgentTool/prompt.ts:68,216` / `AgentTool.tsx:223-224,252,553,567,750` — `runAgent.ts`엔 분기 없음(워커=일반서브에이전트 동일경로).
- **산출물 전체 목록(재작성금지, 상태최신)**:
  - `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` — 완성.
  - `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`/`.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`/`.html` — 완결.
  - `/Users/seobi/jinsup_space/CC/큐웨이크-엔터없는-진입-소스분석.md` — 완결.
  - `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html` — **완결**(§00~§05, 브라우저 열림).
  - `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`/`.html`/`-전체287건.json` — **완결**(브라우저 열림).
  - Chain10(XML vs MD), Chain16(스킬 로스트인더미들), Chain18~19(Coordinator Mode) — **문서화 안 됨, 순수 채팅 답변만.** 재요청 시에만 작성.
- PostCompact훅 관찰(정보성, 재검증 안함): `~/.claude/scripts/cc-name.sh` → `hs -c bigAlert(...)`.
