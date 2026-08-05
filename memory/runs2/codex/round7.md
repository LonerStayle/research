## 단계 1

### Current progress and key decisions made

- **Session goal (unchanged)**: 사용자가 `/Users/seobi/jinsup_space/CC` (Claude Code 내부를 리버스엔지니어링하는 리서치 레포: `md_group/` 분석 문서, `html_group_v2/` HTML 시각화, `src/` 재구성 소스)를 대상으로 세부 메커니즘을 하나씩 깊게 파고드는 세션. 이번이 **7번째 컴팩션 사이클** (전체 11회 중).

- **Chain1~9 (완전 종결, 이번 사이클에서 한 줄로 초압축 — 상세는 round5/round6 요약에 이관됨)**:
  - Chain1 배치파티셔닝(`isConcurrencySafe` per-tool 선언) / Chain2 컨텍스트주입4트랙(유령메시지·skill_listing·conditional rules·frontmatter) / Chain3 UserPromptSubmit훅·MCP지시2배달·캐시경계 / Chain4 세션인풋 스냅샷(Chain6서 리네임) / Chain5 src↔실서비스 diff마커 CLOSED / Chain6 "2027→2026" 오타정정+청사진HTML.
  - Chain7 ToolSearch 5단계 생애주기(분류→모드게이트→고지→검색[**BM25아님**, 필드가중 불리언+합산정렬]→로드/재조립), 로스트인더미들 4중안전망.
  - Chain8~9 큐웨이크(엔터없는진입) **6개 도어** 확정(①백그라운드완료②Stop훅차단③원격입력④스케줄⑤비동기에이전트결과숨은재진입⑥고아권한응답), "4개→6개" 자기정정.

- **Chain10~19 (완전 종결, 압축 유지 — round6 대비 추가 압축)**:
  - Chain10 — MD/XML 역할분담(산문=MD, 경계/화물=XML) 재확인. 문서화 안 됨.
  - Chain11 — "0번째 유저프롬프트"(유령메시지) 10라운드 종결: `prependUserContext`(api.ts:449-474)는 매 사이클 인라인이지만 `getUserContext` `memoize`(context.ts:155)로 **세션 첫 호출 1회만** 디스크읽음. 캐시무효화 3곳뿐(`/clear`·`/compact`·auto-compact정리). 설계철학 "stale wins". 유령 리턴값={claudeMd,currentDate,userEmail}뿐, 스킬/도구목록은 별도 델타채널. CLAUDE.md가 0번 유저메시지에 있는 이유 4가지(권위계층분리>서브에이전트모듈성>캐시조각방지>채널일관성, 역산추론 정직표기). SR census 47종의 "3계열 누락"(인라인/선포장/직조립) 사용자 재지적 → Chain12~15의 씨앗.
  - Chain12 — Chain11 총정리 답변 md+html 문서화. 산출물 `시스템리마인더-isMeta-신분증-총정리.md`/`.html`("컨텍스트 세관" 메타포, §00~04).
  - Chain13 — 인라인/선포장/직조립을 택배비유로 재설명(어태치먼트=공장일괄포장/인라인=본문인쇄경고문/선포장=미리싸서우체통/직조립=그자리조립) → md·html 양쪽 반영.
  - Chain14 — ReAct 사이클 전용 SR 3채널(ⓐ유령재인쇄 ⓑ★tool_result인라인[ReAct전용] ⓒ사이클꼬리어태치먼트) 규명 → §03 삽입.
  - Chain15 — ReAct 중 비SR 자동메시지 3계열(A.tool_result채널 B.SR없는isMeta 5종[스킬본문·이미지PDF·★출력한도회복메시지 query.ts:1213-1218·★토큰예산넛지 query.ts:1314-1317·대화복구] C.메시지개조[autocompact/microcompact/applyToolResultBudget]) → html §05(사이클타임라인) 신설.
  - Chain16 — 스킬 vs ToolSearch 로스트인더미들 비대칭 3라운드: ToolSearch는 도구전용(스킬 관할밖), compact후 `sentSkillNames` 의도적 미리셋(compact.ts:524-529 주석), resume은 `suppressNextSkillListing`(fire-once latch). 하네스 대처="소극적 3종뿐"(표지판/유저명시호출/compact우연리프레시) — "**기본모드의 인정된 구멍**", `EXPERIMENTAL_SKILL_SEARCH`(turn-0 discovery)가 메우는 중. 사용자가 어시스턴트의 알람성 프레이밍에 반문→①새세션②resume③compact 3케이스로 재정리한 자기교정 포함. 문서화 안 됨.
  - Chain17 — "기술부채 대장" Workflow 전체소스스캔(src 1,884파일, 13샤드 병렬, 47에이전트/918도구호출/26분) **287건 확정**. byCategory: 미완공사63·버그42·호환성34·플랫폼한계33·UX타협28·성능타협27·보안게이트19·캐시절약19·기타22. 핵심통찰: "몰라서"가 아니라 BQ실측/인시던트번호로 계량된 "재고끝에 남긴" 빚, 상환회피 3패턴(탐지대체/킬스위치담보/기능축소봉합). 산출물 `클로드코드-기술부채-대장.md`(222줄)/`.html`/`-전체287건.json`.
  - Chain18 — Coordinator Mode(전용 수퍼바이저 배역) 발굴: `isCoordinatorMode()`+`getCoordinatorSystemPrompt()`가 메인 시스템프롬프트 통째교체, AgentTool/SendMessageTool/TaskStopTool 지휘도구, Swarm/Team(`INTERNAL_WORKER_TOOLS`)까지. 문서화 안 됨.
  - Chain19 — Coordinator Mode도 `runAgent.ts`엔 분기 없음(워커스폰=Explore/Plan과 동일경로) 확인 → "하네스는 하나, 배역만 여럿" 결론. 문서화 안 됨.

- **Chain20 — "임베딩/BM25/의도분류/고정에이전트워크플로우 없음" 4주장 검증 + 유명기술 확장리스트 (완결, round6에서 ★미착수였던 것이 이번 세그먼트 서두에 완료됨)**:
  - grep 전수(embedding/cosine/vector.?search/faiss/hnsw/semantic·bm25/tfidf/okapi/lunr·intent.?class/classifier/router·langgraph/workflow/graph 등) → 모든 히트 **오탐 확인**(`getEmbeddingLevels`=유니코드bidi텍스트, `string-embedding`=주석, `SearchBox.tsx`매치=base64소스맵 우연일치, `PowerShellTool`/`RemoteSessionDetailDialog`=무관). **의도 분류는 grep 0건**(문자열조차 없음).
  - 확정표: 임베딩/벡터❌(모델이 grep/glob 검색어를 직접 짬) · BM25/tf-idf❌(ToolSearch=필드가중불리언, HistorySearchDialog=fuzzy부분일치) · 의도분류❌(라우팅없음, 모델이 컨텍스트보고 스스로 도구/스킬선택) · 고정에이전트워크플로우❌(LangGraph식 상태그래프없음, `queryLoop` while루프 하나가 전부).
  - 관통철학: "전처리를 모델에게 위임"(검색→모델이 쿼리생성, 라우팅→모델판단, 오케스트레이션→ReAct루프).
  - **유명하지만 없는 것 확장리스트**(전수는 아니고 부분확인, 정직표기됨): RAG파이프라인(청킹·리랭킹·retrieval — 벡터스토어 자체없음) · 대화요약메모리버퍼(LangChain ConversationSummaryMemory류 — compact가 임계초과시 1회 요약교체뿐) · 리플렉션/자기비판루프(Reflexion — verification에이전트는 1회성 판정일 뿐) · 플래너-실행자분리(Plan-and-Execute — Plan은 그냥 서브에이전트, 강제 안 함) · 동적few-shot예제선택(정적예제만) · 토큰레벨가드레일/출력파서(Guardrails류 — zod는 입력검증만, 출력은 자유텍스트) · 세만틱캐싱(바이트단위 정확일치 프리픽스캐시만) · 멀티암드밴딧/DSPy식 프롬프트최적화(손튜닝뿐).

- **Chain21 — "Reflexion 없다는게 무슨말이지" 용어 정밀화 (완결, 신규)**: 사용자가 Chain20의 "리플렉션 없음" 표현에 재질문 → Reflexion(2023 논문, Actor→Evaluator→Self-Reflection→에피소드메모리축적→재시도주입 루프)이라는 **특정 학술 프레임워크**를 가리킨 것임을 명확화. 클로드코드엔 "성찰하는 능력"(verification에이전트 1회판정/FAIL시재시도/모델의 자연스런자기수정/auto-memory)은 있지만, "성찰을 강제하고 메모리에 축적해 되먹이는 코드화된 아키텍처"는 없음. "약한 모델을 외부루프로 보강하는 기법인데 클로드코드는 강한 프런티어모델을 전제해 그 스캐폴딩을 안 짠 것"(추론 표기).

- **Chain22 — verification 에이전트 빌트인 여부 조사 (완결, 신규)**: `VERIFICATION_AGENT` **빌트인 정의는 있으나 이중 잠금으로 기본 비활성**: ①`feature('VERIFICATION_AGENT')`(빌드플래그, 외부배포시DCE가능) ②`getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)`(GrowthBook 원격플래그, 기본값false) — 둘 다 참이어야 `builtInAgents.ts:65-68`에서 목록등록. 일반유저는 `subagent_type="verification"` 자체가 존재 안 함(사내A/B코호트 전용으로 추정). 게이트 열리면 **회피불가 넛지**: "3개 이상 태스크 끝내고도 검증 안 했으면 verification에이전트 스폰 전엔 요약금지, 스스로 PARTIAL 자가판정 불가"(TodoWriteTool.ts:107/TaskUpdateTool.ts:397 동일조건). Reflexion 답변과 연결: "이건 (a)기본비활성 (b)설령켜져도 Reflexion식 성찰-누적-되먹임이 아니라 독립검증관의 1회성 판정"으로 재확정. 이 verification에이전트는 세션에서 쓴 `js-super:code-reviewer`/`verifying-spec` 스킬(사용자/플러그인레벨)과는 별개(하네스 빌트인 vs 유저설치)라는 구분도 명시.

- **[정보 조각, 맥락 불명]** — verification 질문 답변 직후, 사용자가 별다른 전후맥락 없이 다음 텍스트를 입력함(이후 어시스턴트 응답 없이 곧바로 새 주제로 전환됨 — 대화에 실제 존재하는 원문이나 어떤 조사·질문의 산물인지 이 세그먼트만으로는 불명): `ngClearLatched`를 세션 고정 래치로 관리한다는 내용, 주석 인용 "Only latch from agentic queries so a classifier call doesn't flip the main thread's context_management mid-turn"(사이드쿼리가 메인스레드 설정을 뒤집던 사고), 좌표 `apiMicrocompact.ts:79-88`(평상시 `keep:'all'`, 래치시만 `keep:{thinking_turns:1}`) / `claude.ts:1469-1470`("Pass latched header values, not live state" 텔레메트리 사후조치) / "② effort 다운그레이드(3/4 high→medium → 4/7 복원), `effort.ts:303-305`에 사고 후 추가". **재요청 시에만 맥락 확인 후 처리, 임의 해석·확장 금지.**

- **Chain23 — 메인루프 밖 "별도 LLM 호출" 지점 전수조사, 2회 자기정정 끝에 확정 (완결, 신규)**: 사용자 질문("에이전트 도구 쓰는거말고 LLM을 별도로쓰는게 요약이랑 bash툴 권한검증 말고 또 언제 있지?")에서 출발.
  1. 1차: `queryHaiku` 소비처 8곳 grep → 기존에 아는 2곳(요약, bash권한분류)과 합쳐 "11곳" 제시.
  2. 사용자 "총 11곳이 끝이야?" 반문 → 재조사: `queryHaiku`는 `queryModelWithoutStreaming` 위의 래퍼일 뿐이고, 저수준 진입함수가 4개(`queryHaiku`/`queryModelWithoutStreaming`/`queryModelWithStreaming`/`queryWithModel`, 전부 `services/api/claude.ts`)임을 발견 → `queryModelWithoutStreaming` 직접소비 5곳(스킬개선/프롬프트훅2종/커스텀에이전트생성/away요약) 추가 확인 → **"아니요, 11곳이 아니었습니다"** 명시적 정정, "최소 20곳 안팎" 잠정치.
  3. 사용자 "LLM쓰는곳 총정리해봐...한곳이라도 놓치지마" → 4개 진입함수 전체 소비처를 기계적으로 grep, 최종 **확정**: 본류 1(query/deps.ts 메인ReAct루프) + **사이드 16지점**(A.queryHaiku계열 8곳: WebFetch요약/teleport/shell접두사분석/세션제목/날짜파싱/피드백/rename/도구요약 · B.queryModelWithoutStreaming 5곳: away요약/스킬개선/커스텀에이전트생성/프롬프트훅2종 · C.queryModelWithStreaming 2곳: 웹검색/**autocompact** · D.queryWithModel 1개소·3회: insights).
  - 사용자 "위 내용 다 md로 적고 어떤 모델호출하는지도 각각 적어라" → 모델 역추적(각 소비처의 `model:` 파라미터 Read) 후 **`/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md`** 작성. 핵심 발견: **autocompact는 haiku가 아니라 메인모델**(`compact.ts:1313 mainLoopModel`, 요약품질 중요) / **insights는 opus 고정**(`insights.ts:41-48`, "Opus - best quality" 주석) — "값싼 잡무=haiku, 품질중요=큰모델" 명확한 원가배분 확인.

- **Chain24 — Chain23 시각화 (완결, 신규)**: 사용자 "/visual-explainer로 시각화해줘" → `visual-explainer` 스킬 호출 → **`/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.html`** 작성(Hero+01진입함수4종+02본류1vs사이드16그리드+03예외둘[autocompact/insights]+04원가배분저울, 다크청록/주황, Big Shoulders Display+Gothic A1+IBM Plex Mono), 브라우저 오픈 완료.

- **Chain25 — "LLM호출들 다 에이전트는 아니고 도구없는 LLM이지?" 검증 (완결, 신규)**: grep으로 각 소비처가 `tools`/`toolChoice`/`mcpTools`를 실제로 넘기는지 확인 → 사용자 직관 확인: **대다수가 `tools:[]`+`toolChoice:undefined`+`mcpTools:[]` 명시**(skillImprovement는 `useTools:false`까지). **예외 1개** — `WebSearchTool.ts:280`만 `toolChoice: useHaiku ? {type:'tool',name:'web_search'} : undefined`로 **도구 1개를 강제**. 3분류 확정: ①도구없는순수LLM(14곳대부분, 함수호출에가까움) ②도구1개강제·단발(웹검색, 미니에이전트에가까우나루프없음) ③진짜에이전트(Agent툴 서브에이전트, 도구풀+ReAct루프). "에이전트냐"를 가르는 기준=도구보유+멀티턴루프 2가지로 정리.

- **Chain26 — TaskCreate(웹UI 표시)가 LLM 컨텍스트로 어떻게 되먹임되는지, 2회 정정 (완결, 신규)**: 사용자 질문("TaskCreate 발생하면 웹UI엔 표시되는데, LLM입장에선 현재태스크가 뭔지 어떻게 컨텍스트주입되나?")에서 출발.
  - 조사 결과: **상태는 하나(`createTask`, tasks.ts), 소비자는 둘**(웹UI 렌더링 / LLM 텍스트주입) — UI가 원본 아니고 공유상태를 독립구독. LLM 주입경로 **3가지**: ①생성즉시 tool_result(`TaskCreateTool.ts:121-128`, 태스크id·제목 즉시확인) ②주기적재주입 **task_reminder 어태치먼트**(`messages.ts:3680-3699`, "task tools haven't been used recently..." 넛지+전체리스트, ★핵심채널) ③능동조회 TaskList/TaskGet(모델이 직접호출, 완료시 "Call TaskList now to find your next available task" 유도문구도 있음). TodoWrite(구형, in-context)와 TaskCreate/Update/List(신형 "TodoV2", `isTodoV2Enabled()` 게이트, id·status·blocks/blockedBy, 웹UI표시는 이쪽) 구분도 명시.
  - **정정①**: 사용자 "처음에 한번들어가고 몇턴마다 반복재주입하는거지?" → "몇 턴마다 무조건"이 **아니라** "**도구를 10턴 안 쓰고 방치했을 때만**"으로 정정. 근거 `attachments.ts:254-256`(`TODO_REMINDER_CONFIG: TURNS_SINCE_WRITE=10, TURNS_BETWEEN_REMINDERS=10`), `getTodoReminderTurnCounts`(attachments.ts:3213-3260)가 backwards로 두 카운터 추적. 리마인더 문구 자체가 "haven't been used recently"라는 **방치감지형 넛지**이지 정기보고가 아님을 확인.
  - **정정②**: 사용자 "그 도구라는건 아무도구? 아니면 Task기준 도구?" → 카운터가 `block.name === 'TodoWrite'`(태스크계열)**만** 세고 Bash/Read/Edit 등 일반도구는 안 셈을 확인 → "도구"라고 뭉뚱그린 것을 "태스크/투두 도구 기준"으로 명시 정정. 설계의도 해석: 일반도구로 코드작업은 계속하면서 태스크추적만 게을리한 정확한 순간을 잡기 위함.
  - 마지막 질문 "그러면 TaskUpdate 하는건 컨텍스트윈도우보고 판단해서 툴콜링하는거야?" → **확인**: 별도 자동트리거 없음, 100% 모델판단. 다만 넛지 3겹(①도구설명문의 사용규약②task_reminder방치리마인더③완료후연쇄유도 "Call TaskList now..." — ③은 `isAgentSwarmsEnabled()` 조건부, 단일세션엔 안 뜰 수 있음 정직표기) 확인. "판단은 모델, 하네스는 옆에서 넛지만" 원칙 재확인.

- **세그먼트 종료**: 마지막 사용자 입력이 `/compact` 슬래시커맨드 — 이 컴팩션(round7) 트리거 지점. Chain20~26 모두 완결 상태로 핸드오프, 미해결 질문 없음.

### Important context, constraints, and user preferences
- 대상 레포: `/Users/seobi/jinsup_space/CC` (현재 `research` 레포와는 별개, `research/notebooks/claude_code`의 GPT-하네스 규약 미적용).
- 사용자 전역 선호(개인 지침, 전 프로젝트 공통): 탐색/분석은 `Explore`, 플래닝은 `Plan` 서브에이전트에 위임하고 실행은 메인에서 직접; 결정/선택 필요시 `AskUserQuestion` 사용, prose로 풀어 묻지 않기.
- 레포 고유 규약(전 세그먼트 통틀어 계속 준수): Claude Code 내부에 대한 모든 비자명한 주장은 `~/jinsup_space/CC/src`를 직접 `grep`/`Read`로 검증하고 "확인 못함" 라벨을 정직하게 씀; 루트 `.md`는 관례상 `html_group_v2/`에 짝꿍 HTML을 두지만 이번 세션 신규 산출물들은 전부 레포 루트에 위치(정식 이동은 재요청시에만); 경로표기는 `~`-상대가 기본, 세션인풋 스냅샷 문서만 절대경로 예외; 새 문서는 기존 톤/구조(번호섹션, file:line 근거, 검증이력) 따름.
- 사용자의 질문 스타일: 좁은 메커니즘 하나를 재질문으로 계속 파고드는 패턴 지속. 이해가 막히면 더 구체적인 시나리오/표/플로우/비유로 재설명을 요구(택배비유 등). "정확한 전수/완전성"에 대한 재검증 압박이 이번 세그먼트에서도 두드러짐(Chain23 "11곳이 끝이야?"/"한곳도 놓치지마").
- **행동 시그널(반복 재확인, 누적 8회 관측)** — 사용자가 어시스턴트의 일반화·누락·과잉확신·과잉알람을 즉시 지적하고, 어시스턴트는 방어 없이 즉시 인정 후 소스로 재검증/표현정정하는 패턴:
  1. 큐웨이크 "4개→6개" 정정 (Chain9). 2. CLAUDE.md 반영시점 자기정정(Chain11). 3. SR census 47종의 3계열 누락(Chain11). 4. 스킬복구 "대처없음" 알람과잉 → 3케이스분리 정정(Chain16).
  5. **[신규]** "11곳"이 `queryHaiku`래퍼만 본 부분집합이었음을 사용자 "총 11곳이 끝이야?" 반문에 인정·재검증(Chain23-1차).
  6. **[신규]** "한곳이라도 놓치지마" 압박에 4개진입함수 전수로 최종 16곳 확정, "11곳이 아니었습니다" 명시적 자기정정(Chain23-2차).
  7. **[신규]** "몇턴마다 반복재주입"이라는 사용자 이해를 "10턴 방치시에만"으로 정정(Chain26-1차).
  8. **[신규]** "그 도구는 아무도구?"라는 질문에 "일반도구가 아니라 Task계열 도구만 카운트"로 앞선 답변("도구") 부정확성 인정·정정(Chain26-2차).
  → **다음 세션 유의사항(갱신)**: 이 사용자는 (a) "다 찾았다"류 완전성 주장을 재검증 압박하는 스타일 — 특히 "N곳입니다"식 확정 수치를 낼 때 grep 함수명/키워드 기준 부분집합일 가능성을 스스로 먼저 의심하고 "이 기준으로 전수"라고 한정해 말할 것, (b) "몇턴마다"/"아무거나" 같은 사용자의 일반화된 재진술은 무심코 "맞다"고 넘기지 말고 조건문 정확도(카운터가 정확히 뭘 세는지)까지 소스로 재확인 후 답할 것.
- **신규 관찰(이번 세그먼트)**: (1) "반영해"류 짧은 명령으로 직전 채팅 답변 전체를 기존 문서(md+html)에 편입시키길 기대하는 패턴은 이번 세그먼트엔 재등장 안 함(Chain23~24는 새 문서를 처음부터 작성). (2) "/visual-explainer로 시각화해줘"처럼 스킬명을 직접 지정해 명시 호출하는 패턴 재확인(Chain24). (3) 사용자가 "그러니까 너말은 ~~라는거지?" 형태로 자기 이해를 재진술해 확인받는 화법을 반복 사용(Chain26) — 이때 사용자의 재진술이 부정확하면 바로 인정하고 정정하는 응답이 유효했음.
- 날짜/파일명 오타정정 관행(Chain6, "2027"→"2026") — 사용자 확답 아직 못 받음, 낮은 우선순위로 잔존.
- 모든 응답은 한국어(세션 초반부터의 지속 제약).

### What remains to be done (next steps)
1. **문서화 백로그** — 아래 챗-only 조사 내용은 완결됐으나 md/html 미작성. **재요청 시에만** 작성, 선제적으로 만들지 말 것:
   - Chain10(XML vs MD), Chain16(스킬 로스트인더미들), Chain18~19(Coordinator Mode) — round6부터 이월.
   - **[신규]** Chain20(임베딩/BM25/의도분류/고정워크플로우 4주장 검증 + 유명기술확장리스트), Chain21(Reflexion 용어정밀화), Chain22(verification 에이전트 이중게이트), Chain25(LLM호출 vs 에이전트 3분류), Chain26(TaskCreate 컨텍스트주입 3경로+task_reminder 조건).
2. **정보 조각 처리 보류** — "ngClearLatched/apiMicrocompact/effort다운그레이드" 파편은 맥락 불명. 사용자가 다시 언급하면 그때 원출처(아마 Chain17 기술부채 스캔의 미노출 항목이거나 별도 인시던트 자료)를 확인해서 답할 것 — 임의로 의미를 채워 넣지 말 것.
3. Chain1~19는 전부 완료·전달·(해당 시)문서반영까지 완료, 재론 불필요. Chain20~26도 전부 완료·전달 완료(문서화는 위 1번 백로그 참조).
4. 낮은 우선순위, 재요청 시에만: `배치-단독-개념-소스증명.md` HTML 짝꿍(미제작); `2026-07-11-...-최신본.html` 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동); "2027→2026" 오타정정 확답 미회수; `클로드코드-기술부채-대장.md`의 특정 카테고리(예: 보안게이트 19건 전체) 더 깊게 파보기.
5. 이 세그먼트가 사용자의 `/compact` 실행으로 종료됐을 뿐, 명시적으로 남겨진 미답변 질문은 없음 — 다음 세그먼트는 사용자의 새 질문으로 자유롭게 시작될 것으로 예상.

### Critical data / references needed to continue
- 레포 루트: `/Users/seobi/jinsup_space/CC`; 문서 `md_group/`, HTML 미러 `html_group_v2/`, 재구성 소스 `src/` (1,884개 `.ts`/`.tsx` 파일, 33MB). 디렉토리별 파일수: utils/564·components/389·commands/189·tools/184·services/130·hooks/104·ink/96·bridge/31·constants/21·skills/20 등.
- Chain1~9 근거(재검증없이 인용가능, round6 이관): 배치파티셔닝 `toolOrchestration.ts:95-116`; 컨텍스트4트랙 `api.ts:449-474`/`context.ts:155-189`; UserPromptSubmit훅 `hooks.ts:7,977`/`prompts.ts:127-129`; MCP지시 `prompts.ts:160-165`; 캐시경계 `api.ts:321-410`/`prompts.ts:371-372`; ToolSearch `ToolSearchTool.ts`(472줄)/`prompt.ts`(isDeferredTool:62-108)/`utils/toolSearch.ts`(756줄)/`attachments.ts:1454-1475`/`claude.ts:1150-1187`/`api.ts:100-224`; 큐웨이크 6도어 `LocalMainSessionTask.ts:262`/`hooks.ts:225-245`/`messageQueueManager.ts:120-193`/`task/framework.ts`(POLL_INTERVAL_MS=1000)/`query.ts:1564-1621` 등.
- Chain10~11 좌표(압축): `constants/xml.ts`; `api.ts:449-474,463,470`; `query.ts:655`; `context.ts:22-34,155-189,184-188`; `constants/common.ts:1-33`(stale wins); 캐시무효화 `caches.ts:52`/`compact.ts:63,117,203`/`postCompactCleanup.ts:59`; `attachments.ts:2661-2751`(getSkillListingAttachments); `runAgent.ts:381`.
- Chain12~15 산출물: `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html`(§00~05). 신규핵심좌표: `query.ts:1213-1218`(출력한도회복메시지), `query.ts:1314-1317`(토큰예산넛지).
- Chain16 좌표: `attachments.ts:2661-2751,2685-2697`(EXPERIMENTAL_SKILL_SEARCH); `compact.ts:524-529`(sentSkillNames 의도적 미리셋); `conversationRecovery.ts:390-401`(suppressNextSkillListing); `SkillTool.ts:389`(DiscoverSkills).
- Chain17 산출물: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`(222줄)/`.html`/`-전체287건.json`. Workflow Run `wf_89574a3c-93a`/Task `w6qkc6gs7`(원본출력 scratchpad, 세션종속이라 소실가능 — 영구본은 레포 json). byCategory/interest분포는 위 본문 참조. 주요좌표: `memdir.ts:329`/`Tool.ts:294`/`attachments.ts:1408`(캐시절약 3건, compact/스킬논의 직결); `cronTasks.ts:336`/`utils/messages.ts:5441`/`sessionStorage.ts:2212`/`toolResultStorage.ts:280`(알려진버그); `bash/ast.ts:1860`/`setup.ts:419`/`subprocessEnv.ts:11`/`bash/parser.ts:61`/`ssrfGuard.ts:12`(보안게이트).
- Chain18~19 좌표: `coordinator/coordinatorMode.ts`(전체 — `isCoordinatorMode():849-854`, `INTERNAL_WORKER_TOOLS:31,842-847`, `getCoordinatorSystemPrompt():111-175`); 소비처 전수 `tools.ts:281,293`/`main.tsx:2198,3768,4590`/`resumeAgent.ts:251`/`forkSubagent.ts:34`/`AgentTool/prompt.ts:68,216`/`AgentTool.tsx:223-224,252,553,567,750`.
- **Chain20 좌표(신규)**: grep 오탐 확인지점 — `ink/bidi.ts:67`(getEmbeddingLevels)/`utils/bash/ast.ts:706`(string-embedding 주석)/`components/SearchBox.tsx:72`(base64 소스맵 우연매치)/`tools/PowerShellTool`·`RemoteSessionDetailDialog`(workflow/graph 오탐). 의도분류 grep 0건.
- **Chain21~22 좌표(신규)**: `tools/AgentTool/built-in/verificationAgent.ts:134`(VERIFICATION_AGENT 정의); `tools/AgentTool/builtInAgents.ts:65-68`(이중게이트: `feature('VERIFICATION_AGENT')` + `getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)`); `tools/AgentTool/constants.ts:4`(VERIFICATION_AGENT_TYPE='verification'); `tools/TaskUpdateTool/TaskUpdateTool.ts:335-336,397`/`tools/TodoWriteTool/TodoWriteTool.ts:78-79,107`(회피불가 넛지 원문); `constants/prompts.ts:393`; `coordinatorMode.ts:222,289`(fresh-eyes 검증지침).
- **Chain23~24 좌표(신규, 산출물 완결)**: 진입함수 4종 전부 `services/api/claude.ts`(`queryHaiku:3241`/`queryModelWithoutStreaming:709`/`queryModelWithStreaming:752`/`queryWithModel:3300`); `utils/model/model.ts:36`(getSmallFastModel). **A.haiku 8곳**: WebFetchTool/utils.ts:503, teleport.tsx:107, shell/prefix.ts:220, sessionTitle.ts:87, mcp/dateTimeParser.ts:68, Feedback.tsx:449, rename/generateSessionName.ts:20, toolUseSummary/toolUseSummaryGenerator.ts:69. **B.withoutStreaming 5곳**: services/awaySummary.ts:41, hooks/skillImprovement.ts:212, components/agents/generateAgent.ts:149, hooks/apiQueryHookHelper.ts:85, hooks/execPromptHook.ts:62. **C.withStreaming 사이드 2곳**: WebSearchTool.ts:268/280, services/compact/compact.ts:1292(model:1313 `mainLoopModel`). **D.withModel 1개소·3회**: commands/insights.ts:883,1026,1577(`getAnalysisModel`/`getInsightsModel` = opus 고정, insights.ts:41-48). 산출물: `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md`, `.html`(브라우저 오픈 완료).
- **Chain25 좌표(신규)**: 도구비움 확인 지점 — awaySummary/skillImprovement/generateAgent `tools:[]`+`toolChoice:undefined`; sessionTitle/dateTimeParser/WebFetch `mcpTools:[]`; skillImprovement `useTools:false`(:132). 예외: `WebSearchTool.ts:280`(`toolChoice: useHaiku ? {type:'tool',name:'web_search'} : undefined`).
- **Chain26 좌표(신규)**: `tools/TaskCreateTool/TaskCreateTool.ts:80-134`(call본문, tool_result:121-128, `expandedView:'tasks'` 자동펼침:116-119); `tools/TaskUpdateTool/TaskUpdateTool.ts`(mapToolResultToToolResultBlockParam, "Call TaskList now..." 유도, `isAgentSwarmsEnabled()` 조건부); `utils/messages.ts:3663-3699`(`todo_reminder`/`task_reminder` case, "haven't been used recently" 원문); `utils/attachments.ts:254-256`(`TODO_REMINDER_CONFIG`: TURNS_SINCE_WRITE=10, TURNS_BETWEEN_REMINDERS=10); `utils/attachments.ts:3213-3260`(`getTodoReminderTurnCounts`, `block.name === 'TodoWrite'`만 카운트 — 일반도구 미포함); `isTodoV2Enabled()` 게이트(TodoWrite구형 vs TaskCreate/Update/List신형 TodoV2 구분).
- **[정보조각 좌표, 맥락불명 — 재확인 전 사용 금지]**: `apiMicrocompact.ts:79-88`, `claude.ts:1469-1470`, `effort.ts:303-305`. "ngClearLatched" 세션고정래치, context_management mid-turn flip 사고 관련으로 추정되나 이 세그먼트만으로 원출처·질문 불명.
- **산출물 전체 목록(재작성금지, 상태최신)**:
  - `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` — 완성.
  - `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`/`.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`/`.html` — 완결.
  - `/Users/seobi/jinsup_space/CC/큐웨이크-엔터없는-진입-소스분석.md` — 완결.
  - `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html` — 완결(§00~§05).
  - `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`/`.html`/`-전체287건.json` — 완결.
  - **[신규]** `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md`/`.html` — **완결**(브라우저 열림, Chain23~24).
  - Chain10(XML vs MD), Chain16(스킬 로스트인더미들), Chain18~19(Coordinator Mode), **Chain20~22·25~26(신규)** — 전부 문서화 안 됨, 순수 채팅 답변만. 재요청 시에만 작성.
- PostCompact훅 관찰(정보성, 재검증 안함): `~/.claude/scripts/cc-name.sh` → `hs -c bigAlert(...)`.

## 단계 2

Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:

### Current progress and key decisions made

- **Session goal (unchanged)**: 사용자가 `/Users/seobi/jinsup_space/CC` (Claude Code 내부를 리버스엔지니어링하는 리서치 레포: `md_group/` 분석 문서, `html_group_v2/` HTML 시각화, `src/` 재구성 소스)를 대상으로 세부 메커니즘을 하나씩 깊게 파고드는 세션. 이번이 **7번째 컴팩션 사이클** (전체 11회 중).

- **Chain1~9 (완전 종결, 이번 사이클에서 한 줄로 초압축 — 상세는 round5/round6 요약에 이관됨)**:
  - Chain1 배치파티셔닝(`isConcurrencySafe` per-tool 선언) / Chain2 컨텍스트주입4트랙(유령메시지·skill_listing·conditional rules·frontmatter) / Chain3 UserPromptSubmit훅·MCP지시2배달·캐시경계 / Chain4 세션인풋 스냅샷(Chain6서 리네임) / Chain5 src↔실서비스 diff마커 CLOSED / Chain6 "2027→2026" 오타정정+청사진HTML.
  - Chain7 ToolSearch 5단계 생애주기(분류→모드게이트→고지→검색[**BM25아님**, 필드가중 불리언+합산정렬]→로드/재조립), 로스트인더미들 4중안전망.
  - Chain8~9 큐웨이크(엔터없는진입) **6개 도어** 확정(①백그라운드완료②Stop훅차단③원격입력④스케줄⑤비동기에이전트결과숨은재진입⑥고아권한응답), "4개→6개" 자기정정.

- **Chain10~19 (완전 종결, 압축 유지 — round6 대비 추가 압축)**:
  - Chain10 — MD/XML 역할분담(산문=MD, 경계/화물=XML) 재확인. 문서화 안 됨.
  - Chain11 — "0번째 유저프롬프트"(유령메시지) 10라운드 종결: `prependUserContext`(api.ts:449-474)는 매 사이클 인라인이지만 `getUserContext` `memoize`(context.ts:155)로 **세션 첫 호출 1회만** 디스크읽음. 캐시무효화 3곳뿐(`/clear`·`/compact`·auto-compact정리). 설계철학 "stale wins". 유령 리턴값={claudeMd,currentDate,userEmail}뿐, 스킬/도구목록은 별도 델타채널. CLAUDE.md가 0번 유저메시지에 있는 이유 4가지(권위계층분리>서브에이전트모듈성>캐시조각방지>채널일관성, 역산추론 정직표기). SR census 47종의 "3계열 누락"(인라인/선포장/직조립) 사용자 재지적 → Chain12~15의 씨앗.
  - Chain12 — Chain11 총정리 답변 md+html 문서화. 산출물 `시스템리마인더-isMeta-신분증-총정리.md`/`.html`("컨텍스트 세관" 메타포, §00~04).
  - Chain13 — 인라인/선포장/직조립을 택배비유로 재설명(어태치먼트=공장일괄포장/인라인=본문인쇄경고문/선포장=미리싸서우체통/직조립=그자리조립) → md·html 양쪽 반영.
  - Chain14 — ReAct 사이클 전용 SR 3채널(ⓐ유령재인쇄 ⓑ★tool_result인라인[ReAct전용] ⓒ사이클꼬리어태치먼트) 규명 → §03 삽입.
  - Chain15 — ReAct 중 비SR 자동메시지 3계열(A.tool_result채널 B.SR없는isMeta 5종[스킬본문·이미지PDF·★출력한도회복메시지 query.ts:1213-1218·★토큰예산넛지 query.ts:1314-1317·대화복구] C.메시지개조[autocompact/microcompact/applyToolResultBudget]) → html §05(사이클타임라인) 신설.
  - Chain16 — 스킬 vs ToolSearch 로스트인더미들 비대칭 3라운드: ToolSearch는 도구전용(스킬 관할밖), compact후 `sentSkillNames` 의도적 미리셋(compact.ts:524-529 주석), resume은 `suppressNextSkillListing`(fire-once latch). 하네스 대처="소극적 3종뿐"(표지판/유저명시호출/compact우연리프레시) — "**기본모드의 인정된 구멍**", `EXPERIMENTAL_SKILL_SEARCH`(turn-0 discovery)가 메우는 중. 사용자가 어시스턴트의 알람성 프레이밍에 반문→①새세션②resume③compact 3케이스로 재정리한 자기교정 포함. 문서화 안 됨.
  - Chain17 — "기술부채 대장" Workflow 전체소스스캔(src 1,884파일, 13샤드 병렬, 47에이전트/918도구호출/26분) **287건 확정**. byCategory: 미완공사63·버그42·호환성34·플랫폼한계33·UX타협28·성능타협27·보안게이트19·캐시절약19·기타22. 핵심통찰: "몰라서"가 아니라 BQ실측/인시던트번호로 계량된 "재고끝에 남긴" 빚, 상환회피 3패턴(탐지대체/킬스위치담보/기능축소봉합). 산출물 `클로드코드-기술부채-대장.md`(222줄)/`.html`/`-전체287건.json`.
  - Chain18 — Coordinator Mode(전용 수퍼바이저 배역) 발굴: `isCoordinatorMode()`+`getCoordinatorSystemPrompt()`가 메인 시스템프롬프트 통째교체, AgentTool/SendMessageTool/TaskStopTool 지휘도구, Swarm/Team(`INTERNAL_WORKER_TOOLS`)까지. 문서화 안 됨.
  - Chain19 — Coordinator Mode도 `runAgent.ts`엔 분기 없음(워커스폰=Explore/Plan과 동일경로) 확인 → "하네스는 하나, 배역만 여럿" 결론. 문서화 안 됨.

- **Chain20 — "임베딩/BM25/의도분류/고정에이전트워크플로우 없음" 4주장 검증 + 유명기술 확장리스트 (완결, round6에서 ★미착수였던 것이 이번 세그먼트 서두에 완료됨)**:
  - grep 전수(embedding/cosine/vector.?search/faiss/hnsw/semantic·bm25/tfidf/okapi/lunr·intent.?class/classifier/router·langgraph/workflow/graph 등) → 모든 히트 **오탐 확인**(`getEmbeddingLevels`=유니코드bidi텍스트, `string-embedding`=주석, `SearchBox.tsx`매치=base64소스맵 우연일치, `PowerShellTool`/`RemoteSessionDetailDialog`=무관). **의도 분류는 grep 0건**(문자열조차 없음).
  - 확정표: 임베딩/벡터❌(모델이 grep/glob 검색어를 직접 짬) · BM25/tf-idf❌(ToolSearch=필드가중불리언, HistorySearchDialog=fuzzy부분일치) · 의도분류❌(라우팅없음, 모델이 컨텍스트보고 스스로 도구/스킬선택) · 고정에이전트워크플로우❌(LangGraph식 상태그래프없음, `queryLoop` while루프 하나가 전부).
  - 관통철학: "전처리를 모델에게 위임"(검색→모델이 쿼리생성, 라우팅→모델판단, 오케스트레이션→ReAct루프).
  - **유명하지만 없는 것 확장리스트**(전수는 아니고 부분확인, 정직표기됨): RAG파이프라인(청킹·리랭킹·retrieval — 벡터스토어 자체없음) · 대화요약메모리버퍼(LangChain ConversationSummaryMemory류 — compact가 임계초과시 1회 요약교체뿐) · 리플렉션/자기비판루프(Reflexion — verification에이전트는 1회성 판정일 뿐) · 플래너-실행자분리(Plan-and-Execute — Plan은 그냥 서브에이전트, 강제 안 함) · 동적few-shot예제선택(정적예제만) · 토큰레벨가드레일/출력파서(Guardrails류 — zod는 입력검증만, 출력은 자유텍스트) · 세만틱캐싱(바이트단위 정확일치 프리픽스캐시만) · 멀티암드밴딧/DSPy식 프롬프트최적화(손튜닝뿐).

- **Chain21 — "Reflexion 없다는게 무슨말이지" 용어 정밀화 (완결, 신규)**: 사용자가 Chain20의 "리플렉션 없음" 표현에 재질문 → Reflexion(2023 논문, Actor→Evaluator→Self-Reflection→에피소드메모리축적→재시도주입 루프)이라는 **특정 학술 프레임워크**를 가리킨 것임을 명확화. 클로드코드엔 "성찰하는 능력"(verification에이전트 1회판정/FAIL시재시도/모델의 자연스런자기수정/auto-memory)은 있지만, "성찰을 강제하고 메모리에 축적해 되먹이는 코드화된 아키텍처"는 없음. "약한 모델을 외부루프로 보강하는 기법인데 클로드코드는 강한 프런티어모델을 전제해 그 스캐폴딩을 안 짠 것"(추론 표기).

- **Chain22 — verification 에이전트 빌트인 여부 조사 (완결, 신규)**: `VERIFICATION_AGENT` **빌트인 정의는 있으나 이중 잠금으로 기본 비활성**: ①`feature('VERIFICATION_AGENT')`(빌드플래그, 외부배포시DCE가능) ②`getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)`(GrowthBook 원격플래그, 기본값false) — 둘 다 참이어야 `builtInAgents.ts:65-68`에서 목록등록. 일반유저는 `subagent_type="verification"` 자체가 존재 안 함(사내A/B코호트 전용으로 추정). 게이트 열리면 **회피불가 넛지**: "3개 이상 태스크 끝내고도 검증 안 했으면 verification에이전트 스폰 전엔 요약금지, 스스로 PARTIAL 자가판정 불가"(TodoWriteTool.ts:107/TaskUpdateTool.ts:397 동일조건). Reflexion 답변과 연결: "이건 (a)기본비활성 (b)설령켜져도 Reflexion식 성찰-누적-되먹임이 아니라 독립검증관의 1회성 판정"으로 재확정. 이 verification에이전트는 세션에서 쓴 `js-super:code-reviewer`/`verifying-spec` 스킬(사용자/플러그인레벨)과는 별개(하네스 빌트인 vs 유저설치)라는 구분도 명시.

- **[정보 조각, 맥락 불명]** — verification 질문 답변 직후, 사용자가 별다른 전후맥락 없이 다음 텍스트를 입력함(이후 어시스턴트 응답 없이 곧바로 새 주제로 전환됨 — 대화에 실제 존재하는 원문이나 어떤 조사·질문의 산물인지 이 세그먼트만으로는 불명): `ngClearLatched`를 세션 고정 래치로 관리한다는 내용, 주석 인용 "Only latch from agentic queries so a classifier call doesn't flip the main thread's context_management mid-turn"(사이드쿼리가 메인스레드 설정을 뒤집던 사고), 좌표 `apiMicrocompact.ts:79-88`(평상시 `keep:'all'`, 래치시만 `keep:{thinking_turns:1}`) / `claude.ts:1469-1470`("Pass latched header values, not live state" 텔레메트리 사후조치) / "② effort 다운그레이드(3/4 high→medium → 4/7 복원), `effort.ts:303-305`에 사고 후 추가". **재요청 시에만 맥락 확인 후 처리, 임의 해석·확장 금지.**

- **Chain23 — 메인루프 밖 "별도 LLM 호출" 지점 전수조사, 2회 자기정정 끝에 확정 (완결, 신규)**: 사용자 질문("에이전트 도구 쓰는거말고 LLM을 별도로쓰는게 요약이랑 bash툴 권한검증 말고 또 언제 있지?")에서 출발.
  1. 1차: `queryHaiku` 소비처 8곳 grep → 기존에 아는 2곳(요약, bash권한분류)과 합쳐 "11곳" 제시.
  2. 사용자 "총 11곳이 끝이야?" 반문 → 재조사: `queryHaiku`는 `queryModelWithoutStreaming` 위의 래퍼일 뿐이고, 저수준 진입함수가 4개(`queryHaiku`/`queryModelWithoutStreaming`/`queryModelWithStreaming`/`queryWithModel`, 전부 `services/api/claude.ts`)임을 발견 → `queryModelWithoutStreaming` 직접소비 5곳(스킬개선/프롬프트훅2종/커스텀에이전트생성/away요약) 추가 확인 → **"아니요, 11곳이 아니었습니다"** 명시적 정정, "최소 20곳 안팎" 잠정치.
  3. 사용자 "LLM쓰는곳 총정리해봐...한곳이라도 놓치지마" → 4개 진입함수 전체 소비처를 기계적으로 grep, 최종 **확정**: 본류 1(query/deps.ts 메인ReAct루프) + **사이드 16지점**(A.queryHaiku계열 8곳: WebFetch요약/teleport/shell접두사분석/세션제목/날짜파싱/피드백/rename/도구요약 · B.queryModelWithoutStreaming 5곳: away요약/스킬개선/커스텀에이전트생성/프롬프트훅2종 · C.queryModelWithStreaming 2곳: 웹검색/**autocompact** · D.queryWithModel 1개소·3회: insights).
  - 사용자 "위 내용 다 md로 적고 어떤 모델호출하는지도 각각 적어라" → 모델 역추적(각 소비처의 `model:` 파라미터 Read) 후 **`/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md`** 작성. 핵심 발견: **autocompact는 haiku가 아니라 메인모델**(`compact.ts:1313 mainLoopModel`, 요약품질 중요) / **insights는 opus 고정**(`insights.ts:41-48`, "Opus - best quality" 주석) — "값싼 잡무=haiku, 품질중요=큰모델" 명확한 원가배분 확인.

- **Chain24 — Chain23 시각화 (완결, 신규)**: 사용자 "/visual-explainer로 시각화해줘" → `visual-explainer` 스킬 호출 → **`/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.html`** 작성(Hero+01진입함수4종+02본류1vs사이드16그리드+03예외둘[autocompact/insights]+04원가배분저울, 다크청록/주황, Big Shoulders Display+Gothic A1+IBM Plex Mono), 브라우저 오픈 완료.

- **Chain25 — "LLM호출들 다 에이전트는 아니고 도구없는 LLM이지?" 검증 (완결, 신규)**: grep으로 각 소비처가 `tools`/`toolChoice`/`mcpTools`를 실제로 넘기는지 확인 → 사용자 직관 확인: **대다수가 `tools:[]`+`toolChoice:undefined`+`mcpTools:[]` 명시**(skillImprovement는 `useTools:false`까지). **예외 1개** — `WebSearchTool.ts:280`만 `toolChoice: useHaiku ? {type:'tool',name:'web_search'} : undefined`로 **도구 1개를 강제**. 3분류 확정: ①도구없는순수LLM(14곳대부분, 함수호출에가까움) ②도구1개강제·단발(웹검색, 미니에이전트에가까우나루프없음) ③진짜에이전트(Agent툴 서브에이전트, 도구풀+ReAct루프). "에이전트냐"를 가르는 기준=도구보유+멀티턴루프 2가지로 정리.

- **Chain26 — TaskCreate(웹UI 표시)가 LLM 컨텍스트로 어떻게 되먹임되는지, 2회 정정 (완결, 신규)**: 사용자 질문("TaskCreate 발생하면 웹UI엔 표시되는데, LLM입장에선 현재태스크가 뭔지 어떻게 컨텍스트주입되나?")에서 출발.
  - 조사 결과: **상태는 하나(`createTask`, tasks.ts), 소비자는 둘**(웹UI 렌더링 / LLM 텍스트주입) — UI가 원본 아니고 공유상태를 독립구독. LLM 주입경로 **3가지**: ①생성즉시 tool_result(`TaskCreateTool.ts:121-128`, 태스크id·제목 즉시확인) ②주기적재주입 **task_reminder 어태치먼트**(`messages.ts:3680-3699`, "task tools haven't been used recently..." 넛지+전체리스트, ★핵심채널) ③능동조회 TaskList/TaskGet(모델이 직접호출, 완료시 "Call TaskList now to find your next available task" 유도문구도 있음). TodoWrite(구형, in-context)와 TaskCreate/Update/List(신형 "TodoV2", `isTodoV2Enabled()` 게이트, id·status·blocks/blockedBy, 웹UI표시는 이쪽) 구분도 명시.
  - **정정①**: 사용자 "처음에 한번들어가고 몇턴마다 반복재주입하는거지?" → "몇 턴마다 무조건"이 **아니라** "**도구를 10턴 안 쓰고 방치했을 때만**"으로 정정. 근거 `attachments.ts:254-256`(`TODO_REMINDER_CONFIG: TURNS_SINCE_WRITE=10, TURNS_BETWEEN_REMINDERS=10`), `getTodoReminderTurnCounts`(attachments.ts:3213-3260)가 backwards로 두 카운터 추적. 리마인더 문구 자체가 "haven't been used recently"라는 **방치감지형 넛지**이지 정기보고가 아님을 확인.
  - **정정②**: 사용자 "그 도구라는건 아무도구? 아니면 Task기준 도구?" → 카운터가 `block.name === 'TodoWrite'`(태스크계열)**만** 세고 Bash/Read/Edit 등 일반도구는 안 셈을 확인 → "도구"라고 뭉뚱그린 것을 "태스크/투두 도구 기준"으로 명시 정정. 설계의도 해석: 일반도구로 코드작업은 계속하면서 태스크추적만 게을리한 정확한 순간을 잡기 위함.
  - 마지막 질문 "그러면 TaskUpdate 하는건 컨텍스트윈도우보고 판단해서 툴콜링하는거야?" → **확인**: 별도 자동트리거 없음, 100% 모델판단. 다만 넛지 3겹(①도구설명문의 사용규약②task_reminder방치리마인더③완료후연쇄유도 "Call TaskList now..." — ③은 `isAgentSwarmsEnabled()` 조건부, 단일세션엔 안 뜰 수 있음 정직표기) 확인. "판단은 모델, 하네스는 옆에서 넛지만" 원칙 재확인.

- **세그먼트 종료**: 마지막 사용자 입력이 `/compact` 슬래시커맨드 — 이 컴팩션(round7) 트리거 지점. Chain20~26 모두 완결 상태로 핸드오프, 미해결 질문 없음.

### Important context, constraints, and user preferences
- 대상 레포: `/Users/seobi/jinsup_space/CC` (현재 `research` 레포와는 별개, `research/notebooks/claude_code`의 GPT-하네스 규약 미적용).
- 사용자 전역 선호(개인 지침, 전 프로젝트 공통): 탐색/분석은 `Explore`, 플래닝은 `Plan` 서브에이전트에 위임하고 실행은 메인에서 직접; 결정/선택 필요시 `AskUserQuestion` 사용, prose로 풀어 묻지 않기.
- 레포 고유 규약(전 세그먼트 통틀어 계속 준수): Claude Code 내부에 대한 모든 비자명한 주장은 `~/jinsup_space/CC/src`를 직접 `grep`/`Read`로 검증하고 "확인 못함" 라벨을 정직하게 씀; 루트 `.md`는 관례상 `html_group_v2/`에 짝꿍 HTML을 두지만 이번 세션 신규 산출물들은 전부 레포 루트에 위치(정식 이동은 재요청시에만); 경로표기는 `~`-상대가 기본, 세션인풋 스냅샷 문서만 절대경로 예외; 새 문서는 기존 톤/구조(번호섹션, file:line 근거, 검증이력) 따름.
- 사용자의 질문 스타일: 좁은 메커니즘 하나를 재질문으로 계속 파고드는 패턴 지속. 이해가 막히면 더 구체적인 시나리오/표/플로우/비유로 재설명을 요구(택배비유 등). "정확한 전수/완전성"에 대한 재검증 압박이 이번 세그먼트에서도 두드러짐(Chain23 "11곳이 끝이야?"/"한곳도 놓치지마").
- **행동 시그널(반복 재확인, 누적 8회 관측)** — 사용자가 어시스턴트의 일반화·누락·과잉확신·과잉알람을 즉시 지적하고, 어시스턴트는 방어 없이 즉시 인정 후 소스로 재검증/표현정정하는 패턴:
  1. 큐웨이크 "4개→6개" 정정 (Chain9). 2. CLAUDE.md 반영시점 자기정정(Chain11). 3. SR census 47종의 3계열 누락(Chain11). 4. 스킬복구 "대처없음" 알람과잉 → 3케이스분리 정정(Chain16).
  5. **[신규]** "11곳"이 `queryHaiku`래퍼만 본 부분집합이었음을 사용자 "총 11곳이 끝이야?" 반문에 인정·재검증(Chain23-1차).
  6. **[신규]** "한곳이라도 놓치지마" 압박에 4개진입함수 전수로 최종 16곳 확정, "11곳이 아니었습니다" 명시적 자기정정(Chain23-2차).
  7. **[신규]** "몇턴마다 반복재주입"이라는 사용자 이해를 "10턴 방치시에만"으로 정정(Chain26-1차).
  8. **[신규]** "그 도구는 아무도구?"라는 질문에 "일반도구가 아니라 Task계열 도구만 카운트"로 앞선 답변("도구") 부정확성 인정·정정(Chain26-2차).
  → **다음 세션 유의사항(갱신)**: 이 사용자는 (a) "다 찾았다"류 완전성 주장을 재검증 압박하는 스타일 — 특히 "N곳입니다"식 확정 수치를 낼 때 grep 함수명/키워드 기준 부분집합일 가능성을 스스로 먼저 의심하고 "이 기준으로 전수"라고 한정해 말할 것, (b) "몇턴마다"/"아무거나" 같은 사용자의 일반화된 재진술은 무심코 "맞다"고 넘기지 말고 조건문 정확도(카운터가 정확히 뭘 세는지)까지 소스로 재확인 후 답할 것.
- **신규 관찰(이번 세그먼트)**: (1) "반영해"류 짧은 명령으로 직전 채팅 답변 전체를 기존 문서(md+html)에 편입시키길 기대하는 패턴은 이번 세그먼트엔 재등장 안 함(Chain23~24는 새 문서를 처음부터 작성). (2) "/visual-explainer로 시각화해줘"처럼 스킬명을 직접 지정해 명시 호출하는 패턴 재확인(Chain24). (3) 사용자가 "그러니까 너말은 ~~라는거지?" 형태로 자기 이해를 재진술해 확인받는 화법을 반복 사용(Chain26) — 이때 사용자의 재진술이 부정확하면 바로 인정하고 정정하는 응답이 유효했음.
- 날짜/파일명 오타정정 관행(Chain6, "2027"→"2026") — 사용자 확답 아직 못 받음, 낮은 우선순위로 잔존.
- 모든 응답은 한국어(세션 초반부터의 지속 제약).

### What remains to be done (next steps)
1. **문서화 백로그** — 아래 챗-only 조사 내용은 완결됐으나 md/html 미작성. **재요청 시에만** 작성, 선제적으로 만들지 말 것:
   - Chain10(XML vs MD), Chain16(스킬 로스트인더미들), Chain18~19(Coordinator Mode) — round6부터 이월.
   - **[신규]** Chain20(임베딩/BM25/의도분류/고정워크플로우 4주장 검증 + 유명기술확장리스트), Chain21(Reflexion 용어정밀화), Chain22(verification 에이전트 이중게이트), Chain25(LLM호출 vs 에이전트 3분류), Chain26(TaskCreate 컨텍스트주입 3경로+task_reminder 조건).
2. **정보 조각 처리 보류** — "ngClearLatched/apiMicrocompact/effort다운그레이드" 파편은 맥락 불명. 사용자가 다시 언급하면 그때 원출처(아마 Chain17 기술부채 스캔의 미노출 항목이거나 별도 인시던트 자료)를 확인해서 답할 것 — 임의로 의미를 채워 넣지 말 것.
3. Chain1~19는 전부 완료·전달·(해당 시)문서반영까지 완료, 재론 불필요. Chain20~26도 전부 완료·전달 완료(문서화는 위 1번 백로그 참조).
4. 낮은 우선순위, 재요청 시에만: `배치-단독-개념-소스증명.md` HTML 짝꿍(미제작); `2026-07-11-...-최신본.html` 추가수정 3안(호버툴팁/판정필터버튼/html_group_v2 이동); "2027→2026" 오타정정 확답 미회수; `클로드코드-기술부채-대장.md`의 특정 카테고리(예: 보안게이트 19건 전체) 더 깊게 파보기.
5. 이 세그먼트가 사용자의 `/compact` 실행으로 종료됐을 뿐, 명시적으로 남겨진 미답변 질문은 없음 — 다음 세그먼트는 사용자의 새 질문으로 자유롭게 시작될 것으로 예상.

### Critical data / references needed to continue
- 레포 루트: `/Users/seobi/jinsup_space/CC`; 문서 `md_group/`, HTML 미러 `html_group_v2/`, 재구성 소스 `src/` (1,884개 `.ts`/`.tsx` 파일, 33MB). 디렉토리별 파일수: utils/564·components/389·commands/189·tools/184·services/130·hooks/104·ink/96·bridge/31·constants/21·skills/20 등.
- Chain1~9 근거(재검증없이 인용가능, round6 이관): 배치파티셔닝 `toolOrchestration.ts:95-116`; 컨텍스트4트랙 `api.ts:449-474`/`context.ts:155-189`; UserPromptSubmit훅 `hooks.ts:7,977`/`prompts.ts:127-129`; MCP지시 `prompts.ts:160-165`; 캐시경계 `api.ts:321-410`/`prompts.ts:371-372`; ToolSearch `ToolSearchTool.ts`(472줄)/`prompt.ts`(isDeferredTool:62-108)/`utils/toolSearch.ts`(756줄)/`attachments.ts:1454-1475`/`claude.ts:1150-1187`/`api.ts:100-224`; 큐웨이크 6도어 `LocalMainSessionTask.ts:262`/`hooks.ts:225-245`/`messageQueueManager.ts:120-193`/`task/framework.ts`(POLL_INTERVAL_MS=1000)/`query.ts:1564-1621` 등.
- Chain10~11 좌표(압축): `constants/xml.ts`; `api.ts:449-474,463,470`; `query.ts:655`; `context.ts:22-34,155-189,184-188`; `constants/common.ts:1-33`(stale wins); 캐시무효화 `caches.ts:52`/`compact.ts:63,117,203`/`postCompactCleanup.ts:59`; `attachments.ts:2661-2751`(getSkillListingAttachments); `runAgent.ts:381`.
- Chain12~15 산출물: `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html`(§00~05). 신규핵심좌표: `query.ts:1213-1218`(출력한도회복메시지), `query.ts:1314-1317`(토큰예산넛지).
- Chain16 좌표: `attachments.ts:2661-2751,2685-2697`(EXPERIMENTAL_SKILL_SEARCH); `compact.ts:524-529`(sentSkillNames 의도적 미리셋); `conversationRecovery.ts:390-401`(suppressNextSkillListing); `SkillTool.ts:389`(DiscoverSkills).
- Chain17 산출물: `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`(222줄)/`.html`/`-전체287건.json`. Workflow Run `wf_89574a3c-93a`/Task `w6qkc6gs7`(원본출력 scratchpad, 세션종속이라 소실가능 — 영구본은 레포 json). byCategory/interest분포는 위 본문 참조. 주요좌표: `memdir.ts:329`/`Tool.ts:294`/`attachments.ts:1408`(캐시절약 3건, compact/스킬논의 직결); `cronTasks.ts:336`/`utils/messages.ts:5441`/`sessionStorage.ts:2212`/`toolResultStorage.ts:280`(알려진버그); `bash/ast.ts:1860`/`setup.ts:419`/`subprocessEnv.ts:11`/`bash/parser.ts:61`/`ssrfGuard.ts:12`(보안게이트).
- Chain18~19 좌표: `coordinator/coordinatorMode.ts`(전체 — `isCoordinatorMode():849-854`, `INTERNAL_WORKER_TOOLS:31,842-847`, `getCoordinatorSystemPrompt():111-175`); 소비처 전수 `tools.ts:281,293`/`main.tsx:2198,3768,4590`/`resumeAgent.ts:251`/`forkSubagent.ts:34`/`AgentTool/prompt.ts:68,216`/`AgentTool.tsx:223-224,252,553,567,750`.
- **Chain20 좌표(신규)**: grep 오탐 확인지점 — `ink/bidi.ts:67`(getEmbeddingLevels)/`utils/bash/ast.ts:706`(string-embedding 주석)/`components/SearchBox.tsx:72`(base64 소스맵 우연매치)/`tools/PowerShellTool`·`RemoteSessionDetailDialog`(workflow/graph 오탐). 의도분류 grep 0건.
- **Chain21~22 좌표(신규)**: `tools/AgentTool/built-in/verificationAgent.ts:134`(VERIFICATION_AGENT 정의); `tools/AgentTool/builtInAgents.ts:65-68`(이중게이트: `feature('VERIFICATION_AGENT')` + `getFeatureValue_CACHED_MAY_BE_STALE('tengu_hive_evidence', false)`); `tools/AgentTool/constants.ts:4`(VERIFICATION_AGENT_TYPE='verification'); `tools/TaskUpdateTool/TaskUpdateTool.ts:335-336,397`/`tools/TodoWriteTool/TodoWriteTool.ts:78-79,107`(회피불가 넛지 원문); `constants/prompts.ts:393`; `coordinatorMode.ts:222,289`(fresh-eyes 검증지침).
- **Chain23~24 좌표(신규, 산출물 완결)**: 진입함수 4종 전부 `services/api/claude.ts`(`queryHaiku:3241`/`queryModelWithoutStreaming:709`/`queryModelWithStreaming:752`/`queryWithModel:3300`); `utils/model/model.ts:36`(getSmallFastModel). **A.haiku 8곳**: WebFetchTool/utils.ts:503, teleport.tsx:107, shell/prefix.ts:220, sessionTitle.ts:87, mcp/dateTimeParser.ts:68, Feedback.tsx:449, rename/generateSessionName.ts:20, toolUseSummary/toolUseSummaryGenerator.ts:69. **B.withoutStreaming 5곳**: services/awaySummary.ts:41, hooks/skillImprovement.ts:212, components/agents/generateAgent.ts:149, hooks/apiQueryHookHelper.ts:85, hooks/execPromptHook.ts:62. **C.withStreaming 사이드 2곳**: WebSearchTool.ts:268/280, services/compact/compact.ts:1292(model:1313 `mainLoopModel`). **D.withModel 1개소·3회**: commands/insights.ts:883,1026,1577(`getAnalysisModel`/`getInsightsModel` = opus 고정, insights.ts:41-48). 산출물: `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md`, `.html`(브라우저 오픈 완료).
- **Chain25 좌표(신규)**: 도구비움 확인 지점 — awaySummary/skillImprovement/generateAgent `tools:[]`+`toolChoice:undefined`; sessionTitle/dateTimeParser/WebFetch `mcpTools:[]`; skillImprovement `useTools:false`(:132). 예외: `WebSearchTool.ts:280`(`toolChoice: useHaiku ? {type:'tool',name:'web_search'} : undefined`).
- **Chain26 좌표(신규)**: `tools/TaskCreateTool/TaskCreateTool.ts:80-134`(call본문, tool_result:121-128, `expandedView:'tasks'` 자동펼침:116-119); `tools/TaskUpdateTool/TaskUpdateTool.ts`(mapToolResultToToolResultBlockParam, "Call TaskList now..." 유도, `isAgentSwarmsEnabled()` 조건부); `utils/messages.ts:3663-3699`(`todo_reminder`/`task_reminder` case, "haven't been used recently" 원문); `utils/attachments.ts:254-256`(`TODO_REMINDER_CONFIG`: TURNS_SINCE_WRITE=10, TURNS_BETWEEN_REMINDERS=10); `utils/attachments.ts:3213-3260`(`getTodoReminderTurnCounts`, `block.name === 'TodoWrite'`만 카운트 — 일반도구 미포함); `isTodoV2Enabled()` 게이트(TodoWrite구형 vs TaskCreate/Update/List신형 TodoV2 구분).
- **[정보조각 좌표, 맥락불명 — 재확인 전 사용 금지]**: `apiMicrocompact.ts:79-88`, `claude.ts:1469-1470`, `effort.ts:303-305`. "ngClearLatched" 세션고정래치, context_management mid-turn flip 사고 관련으로 추정되나 이 세그먼트만으로 원출처·질문 불명.
- **산출물 전체 목록(재작성금지, 상태최신)**:
  - `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` — 완성.
  - `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/2026-07-11-시스템프롬프트및도구내용-최신본.md`/`.html` — 완성.
  - `/Users/seobi/jinsup_space/CC/toolsearch-생애주기-소스분석.md`/`.html` — 완결.
  - `/Users/seobi/jinsup_space/CC/큐웨이크-엔터없는-진입-소스분석.md` — 완결.
  - `/Users/seobi/jinsup_space/CC/시스템리마인더-isMeta-신분증-총정리.md`/`.html` — 완결(§00~§05).
  - `/Users/seobi/jinsup_space/CC/클로드코드-기술부채-대장.md`/`.html`/`-전체287건.json` — 완결.
  - `/Users/seobi/jinsup_space/CC/클로드코드-LLM-별도호출-전수.md`/`.html` — 완결(브라우저 열림, Chain23~24).
  - Chain10(XML vs MD), Chain16(스킬 로스트인더미들), Chain18~19(Coordinator Mode), Chain20~22·25~26 — 전부 문서화 안 됨, 순수 채팅 답변만. 재요청 시에만 작성.
- PostCompact훅 관찰(정보성, 재검증 안함): `~/.claude/scripts/cc-name.sh` → `hs -c bigAlert(...)`.
