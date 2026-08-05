<analysis>
이 요약은 [이전 컴팩션(1회차) 요약본] + [그 이후 새로 쌓인 대화 구간(conv2-01.part2.txt)] 전체를 커버해야 한다. 시간 순으로 정리한다.

**(구간 A) 1회차 컴팩션 요약본에 담긴 내용 — 승계**
사용자가 `/Users/seobi/jinsup_space/CC`(Claude Code 내부 동작을 역공학하는 리서치 워크스페이스) 전체 파악을 요청 → Explore 서브에이전트가 md_group/html_group_v2/src 구조와 12개 주제군을 보고. 이후 "배치 병렬의 3조 요건"을 깊이 파는 Q&A 체인(모델 multi-tool_use emit × 도구별 isConcurrencySafe 선언 × 하네스 partitionToolCalls)이 이어졌고, 사용자가 "소스코드로 증명해봐"라고 요구하자 `toolOrchestration.ts`(partitionToolCalls reduce 병합규칙), `Tool.ts`(TOOL_DEFAULTS 기본값 false), `FileReadTool.ts`/`GrepTool.ts`(isConcurrencySafe true 선언), `query.ts:820-824`(모델 emit 순서 보존, 파일 경로 비교 로직 없음)를 grep/Read로 확인하고 node.js로 파티션 로직을 재현 실행까지 했다. 사용자가 "분리가 아니라 단독이라는 개념이구나, 테스트한 것까지 md로 만들어달라"고 요청 → `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md` 신규 작성. 이어서 사용자가 "0번 유저프롬프트에 CLAUDE.md와 스킬목록이 같이 들어가냐"는 자신의 가설을 검증해달라 요청 → `prependUserContext`(api.ts:449-474, claudeMd+currentDate만 담아 매 호출 재생성/index 0/이력 미저장)와 `skill_listing`(별도 어태치먼트, 1회 삽입 후 이력 잔류, 델타추적/resume억제/컴팩트후 미재주입)이 완전히 다른 메커니즘임을 소스로 규명 — "절반만 맞다"로 정정. 사용자가 마지막으로 "그 rules로 하면 필요한 상황일 때 그걸로 가져와쓰잖아 그건 어떻게 세팅한거지"를 질문한 시점에서 1회차 구간이 끝났고(조사 착수, 결과 미확보), 이 질문에 답하는 것이 2회차(현재 요약 대상 구간)의 출발점이 된다.

**(구간 B) conv2-01.part2.txt 앞부분 — rules 조사 마무리 + 컨텍스트 주입 아키텍처 정리 (1회차 이어받아 진행, "위 내용들도 /visual-explainer로 작성해줘"까지)**
1. `claudemd.ts`(688-778 `processMdRules`, 1198-1238 `getManagedAndUserConditionalRules`, 250-279 `parseFrontmatterPaths`)와 `attachments.ts`(1660-1689 nestedDirs/cwdLevelDirs, 2165-2191 `getNestedMemoryAttachments`)를 grep/Read해 rules의 세팅 방법(frontmatter `paths:` 글롭 유무로 무조건부/조건부 분기)과 런타임 지연 주입 파이프라인(트리거 등록→수집→매칭→주입→중복방지 5단)을 규명. 어시스턴트가 이를 표+그림으로 정리해 답했다.
2. 사용자: "음..???? 이해가 안되네" — 설명이 너무 밀도 높았다는 피드백. 어시스턴트가 `api-rule.md`(paths: src/api/**) 하나를 예로 든 구체 시나리오 + 세션 타임라인으로 재설명, "세팅은 frontmatter paths 한 줄, 발동판정=파일접근 이벤트, 발동하면 대화 중간에 유저메시지로 끼어듦" 3요점으로 압축.
3. 사용자: "Read툴이 읽으면 마치 훅마냥 잡아서 실행해서 어태치먼트로 넣는거야?" — 어시스턴트가 "우편함(mailbox)" 비유로 정정: Read는 `FileReadTool.ts:848`에서 `context.nestedMemoryAttachmentTriggers?.add(fullFilePath)`로 "쪽지만 남기고" 끝나며, 다음 사이클 전처리(원래 표현, 이 시점엔 미확정)가 Set을 비운다고 설명. 즉시성 없음/등록메커니즘 없음(콜백X, 공유 Set 생산자-소비자)/진짜 훅 시스템(PreToolUse/PostToolUse)과 무관함을 강조.
4. 사용자: "ReAct 사이클 전처리가 도구결과 보낼떄 인건가" — 어시스턴트가 `query.ts`에서 `getAttachmentMessages` 호출 지점을 grep(`:1569` 발견)하고 `md_group/cc-context-preprocessing-timing.md`(71줄, 3계층 구조/전처리5단표)를 재확인. 결과: 직전 자기 설명("다음 사이클 전처리가 우편함을 비운다")이 부정확했음을 스스로 발견하고 정정 — 실제로는 **같은 사이클의 꼬리**(`query.ts:1569-1579`, 도구 실행 직후, `toolResults.push(attachment)`로 합류)에서 일어나며, "전처리 5단"(`query.ts:364-463`, 압축용 applyToolResultBudget→snipCompact→microcompact→contextCollapse→autocompact)은 **다음 사이클의 머리**(모델 호출 직전)라는 별개 구간이라고 명확히 구분. 수집(+, 더하기)과 전처리(−, 줄이기)의 순서(수집이 먼저)까지 정리.
5. 사용자: "프론트메타로 쓰는건 다그렇다고봐야돼? 스킬도 포함해서?" — `SkillTool.ts:1065-1107`(parseFrontmatter로 frontmatter 제거 후 `newMessages: [createUserMessage({content: finalContent, isMeta: true})]`로 본문 주입, tool_result가 아님)과 `loadAgentsDir.ts:312-324`(agent frontmatter는 name/description 필수 카탈로그 메타데이터)를 확인. 결론: "값싼 색인은 항상, 비싼 본문은 방아쇠 당길 때만"이라는 2단 구조는 rules/skills/agents/slash commands 4종 공통이지만, **발동 주체가 3갈래**(rules=하네스/문법적 글롭매칭, skills·agents=모델/의미적 판단, commands=유저/명시적 타이핑)로 다르다는 표를 제시. "frontmatter=항상 지연"은 아니라는 주의사항도 명시(paths 없는 rule은 즉시로드, skill frontmatter는 조건이 아니라 카탈로그).
6. 사용자: "위 내용들도 /visual-explainer 로 작성해줘" — `visual-explainer` 스킬 실행 → `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html` 신규 Write. 다크테마(bg #0d1015), 폰트(Black Han Sans/Gothic A1/IBM Plex Mono), 색상(앰버 claudeMd/시안 skill_listing/그린 rules/바이올렛 skill 본문/레드), 5개 섹션(01 종착지는 하나/02 유령 vs 정주민/03 rules 우편함 파이프라인/04 수집꼬리 vs 전처리머리/05 frontmatter 4종=방아쇠3종) 구성. 대화 중 사용자가 붙여넣은 frontmatter 4종 비교표를 인용하며 "특히 이거 잘작성해줘"라고 강조 요청 → 05번 섹션을 CSS(.ld/.ld-row/.stage/.tline, .fmt-wrap/.fmt, .spectrum/.zone/.zchip)와 HTML 3개 Edit으로 재작업(①2단 로딩 흐름도 ②정밀 비교표 ③방아쇠 스펙트럼). `open` 명령으로 브라우저에 띄우고 완성 요약 메시지 전달.

**(구간 C) 압축 이벤트 발생 — 2회차(1회차) 컴팩션이 실제로 트리거됨**
`part2.txt` 내부에 "This session is being continued from a previous conversation..." 로 시작하는 재주입 요약 메시지가 등장한다(이것이 바로 1회차 컴팩션 요약본, 즉 지금 이 요약 작업에서 읽은 `round1.md`의 원문과 동일). 뒤이어 `[슬래시커맨드 /compact]` 유저 메시지와 `PostCompact` 훅 alert(`hs -c bigAlert`) stdout이 나타난다 — 즉 이 구간에서 실제로 압축이 한 차례 발동했고, 지금부터가 압축 **이후** 새로 시작되는 대화다.

**(구간 D) 압축 직후 새 대화 — 유저프롬프트 구성 관찰 + UserPromptSubmit 훅 조사 (현재 미해결 상태로 종료)**
1. 사용자: "지금 유저프롬프트로 내용 뭐들어가?" — 어시스턴트가 압축 직후 첫 API 호출에 실제로 보이는 내용을 그대로 보고. 0번 유령메시지 3키(claudeMd=전역+프로젝트 CLAUDE.md+auto-memory MEMORY.md 인덱스, userEmail=`axtech@goldenplanet.co.kr`, currentDate)에 더해, 압축 직후라서 붙은 5종 특수 화물(①compact 요약문 8섹션+jsonl 경로+"요약 언급말고 이어서" 지시 ②파일 리플레이: 압축 직전 Read했던 `md_group/CLAUDE.md`,`md_group/cc-context-preprocessing-timing.md` 2개 통째 재주입 ③호출됐던 스킬 재고지: `visual-explainer` 스킬 본문 전체가 "EARLIER in this session에 호출됨, 재실행 금지" 리마인더로 재주입 ④상주 리마인더들(ToolSearch 지연도구목록/Agent타입목록/MCP서버instructions/SessionStart 훅 출력(superpowers)/날짜변경알림) ⑤방금 메시지(`/compact` stdout+실제 질문))을 정리해 보고. 특기: 1회차 요약에서 "소스에서 확인 못함"으로 정직 표기했던 `userEmail` 키가, 실제 라이브 세션에서는 실제 값으로 확인됨(실서비스와 소스스냅샷의 차이 재확인).
2. 사용자: "user-prompt-submit-hook 이건 언제씡늑너지"(오타: 언제 실행되지) — 어시스턴트가 `UserPromptSubmit` 훅의 발동 타이밍을 소스로 조사. `processUserInput.ts:140-210`(processUserInputBase → shouldQuery 판정 → `executeUserPromptSubmitHooks` → queryLoop 순서), `hooks.ts:3826-3855`(hasHookForEvent 체크, hookInput={hook_event_name:'UserPromptSubmit',prompt}, yield* executeHooks), `hooks.ts:1936-1939`(getUserPromptSubmitHookBlockingMessage), `messages.ts:4090-4139`(hook_blocking_error/hook_success[SessionStart+UserPromptSubmit만 stdout 허용]/hook_additional_context/hook_stopped_continuation 렌더링, 전부 wrapInSystemReminder+isMeta user 메시지), `constants/prompts.ts:128`(getHooksSection 원문, `<user-prompt-submit-hook>` 태그를 유저발화로 취급하라는 모델용 지시문)을 확인. 답변: 턴 입구(사이클0 이전)에 턴당 1번, 4갈래 결과표(차단/중단/주입/주입), 이 스냅샷 렌더링 코드는 `<user-prompt-submit-hook>` 태그로 직접 감싸지 않고 "hook success:" 접두사 방식이라는 점을 "확인 못함(구버전 흔적 추정)"으로 정직 표기, 타이밍 지도(UserPromptSubmit=턴입구/사이클꼬리=어태치먼트수집/사이클머리=전처리5단)로 정리.
3. 사용자가 강한 어조로 재질문: "무슨말이야? 나프롬프트 중에 [getHooksSection의 한국어 번역 문단 — hooks 설정/`<user-prompt-submit-hook>`/차단시 대응 관련 — 를 그대로 인용] 이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구....." — 즉 사용자의 실제 질문 의도는 "이 훅이 언제 발동하냐"는 일반 타이밍이 아니라, **자신이 실제로 목격한 이 특정 시스템 프롬프트 문단 자체의 정체·출처·역할**이었다. 어시스턴트가 "질문 의도를 제가 빗나갔네요"라고 명시적으로 인정하고 재조사 착수: `prompts.ts:115-139`(getHooksSection 함수 정의, 주변에 `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__`/`FRONTIER_MODEL_NAME='Claude Opus 4.6'`/`CLAUDE_4_5_OR_4_6_MODEL_IDS`/getSystemRemindersSection/getAntModelOverrideSection 확인), `grep -n "getHooksSection"`으로 호출처가 `:127`(정의)과 `:192`(호출) 단 한 곳뿐임을 확인, 이어서 그 호출 문맥을 보려고 `Read prompts.ts offset=160 limit=50`을 호출한 시점에서 **결과를 받지 못한 채 이 구간이 끝난다.**

기술적으로 중요한 패턴/개념(신규, 구간B~D): rules 지연주입 5단 파이프라인 확정(우편함 비유, 훅 시스템과 무관), 수집(사이클꼬리,+)과 전처리(다음사이클머리,−)의 명확한 구간 분리(자기정정 포함), frontmatter 2단 구조의 4종 공통성 + 3종 방아쇠 일반화, skill 본문 주입 채널(`newMessages`, isMeta user message — nested_memory와 종착지 동일), 압축 직후 실제 관찰된 화물 구성(유령메시지 실제값 + 5종 특수화물), UserPromptSubmit 훅의 발동 타이밍/4갈래 결과/렌더링 위치, `<user-prompt-submit-hook>` 태그 미확인.

에러/정정 패턴(신규): (1) 어시스턴트 자기 정정 1회(전처리 타이밍 설명 오류 → 소스로 재확인 후 정정), (2) 사용자 피드백에 의한 재설명 1회(밀도 과다 → 시나리오 기반 재설명), (3) 어시스턴트의 질문 오독 1회(UserPromptSubmit 훅의 "타이밍"으로 해석했으나 실제로는 사용자가 본 "특정 문단의 정체"를 물은 것 — 재조사 착수했으나 미해결로 구간 종료).

지금 파일이 끝나는 지점 = 다음에 이어갈 작업: `getHooksSection()`이 최종 시스템 프롬프트 조립 시 어떤 위치/조건으로 포함되는지(`prompts.ts` offset 160-210 부근)를 확인하고, 사용자가 실제로 물은 "이 문단이 왜 내 프롬프트에 나타났고 역할이 뭐냐"에 정확히 답하는 것 — 아직 Read 결과를 받지 못해 미완.
</analysis>

<summary>
1. Primary Request and Intent:
   - **(승계, 1회차) 세션 목표**: 사용자가 `/Users/seobi/jinsup_space/CC`(Claude Code 내부 동작을 역공학 분석하는 리서치 워크스페이스) 전체 파악을 요청. Explore 에이전트 보고 → 배치 병렬 처리("3조 요건") 심층 Q&A → "소스코드로 증명해봐" → `배치-단독-개념-소스증명.md` 작성 → 0번 유저프롬프트/스킬목록 진위 확인 → **"그 rules로 하면 필요한 상황일떄 그걸로가져와쓰잖아 그건 어떻게 세팅한거지"**(rules 온디맨드 로딩 조사, 2회차 구간의 출발점).
   - **(신규, 2회차) rules 조사 완료 및 재설명**: "음..???? 이해가 안되네" → 시나리오 기반 재설명 요구. "Read툴이 읽으면 마치 훅마냥 잡아서 실행해서 어태치먼트로 넣는거야?" → 메커니즘 정확화 요구. "ReAct 사이클 전처리가 도구결과 보낼떄 인건가" + "컨텍스트 전처리 하는 구간과는 다른거지?" → 타이밍 정확도 검증 요구.
   - **(신규) frontmatter 일반화 확인**: "프론트메타로 쓰는건 다그렇다고봐야돼? 스킬도 포함해서?" → rules 외 skills/agents/commands까지 같은 지연로딩 패턴인지 검증 요구.
   - **(신규) 시각화 산출물**: "위 내용들도 /visual-explainer 로 작성해줘" + 중간에 붙여넣은 frontmatter 4종 표를 가리키며 "특히 이거 잘작성해줘" → `컨텍스트-주입-4트랙-시각설명.html` 작성 및 05번 섹션 특별 강화 요구.
   - **(신규, 압축 이후) 실제 유저프롬프트 관찰**: `/compact` 실행 후 "지금 유저프롬프트로 내용 뭐들어가?" → 압축 직후 실제 API 호출에 무엇이 담기는지 실측 보고 요구.
   - **(신규) UserPromptSubmit 훅 조사**: "user-prompt-submit-hook 이건 언제씡늑너지" → 발동 타이밍 질문. 이어서 **"무슨말이야? 나프롬프트 중에 [getHooksSection 문단 인용] 이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구....."** → 실제로는 "타이밍"이 아니라 "본인이 목격한 그 시스템 프롬프트 문단 자체의 정체·역할"을 물은 것이었음을 명시적으로 지적 — **현재 진행 중, 미해결**.
   - **표준 제약(승계)**: 항상 한국어로 답변. 모든 주장은 grep/Read 기반 소스 검증 필수(프로젝트 CLAUDE.md 관례: "주장은 반드시 소스 코드 기반으로 검증", 확인 안 된 부분은 "소스에서 확인 못함"으로 정직 표기). 문서는 `~` 중립 경로 사용(레포가 여러 머신 간 공유되어 절대경로 시 pull 충돌).

2. Key Technical Concepts:
   - **(승계) 배치 파티셔닝**: `partitionToolCalls` reduce — safe 도구는 연속이고 직전 배치도 safe일 때만 병합, unsafe는 항상 새 단독 배치("분리"가 아니라 "단독"). 3색 분류(항상병렬 21+/항상단독 4/조건부 2). 모델 emit 순서 그대로 적용, 파일 경로 비교 없음. 배치 간 직렬, 배치 내(safe) 병렬(동시성 한도 기본 10).
   - **(승계) 0번 유령메시지**: `prependUserContext`가 매 API 호출마다 `<system-reminder>`로 claudeMd+currentDate를 재생성해 index 0에 삽입, 대화 이력에는 미저장 — 캐시 프리픽스 역할.
   - **(승계) skill_listing 정주민 메시지**: 별도 어태치먼트, 1회 삽입 후 이력 잔류, `sentSkillNames` 델타추적, `--resume` 시 억제, 컴팩트 후 미재주입(~4K 토큰 절약).
   - **(신규) rules 지연주입 파이프라인 확정(우편함 비유)**: ①선언(frontmatter `paths:` 글롭 — 없거나 `**`면 무조건부, 있으면 조건부) ②Read 도구가 파일 읽을 때 `context.nestedMemoryAttachmentTriggers`(Set)에 경로만 add("쪽지만 남김", 즉시 매칭/주입 없음) ③**같은 사이클 꼬리**에서 `getAttachmentMessages`(`query.ts:1569-1579`)가 Set을 순회·비우고 매칭된 rule을 `toolResults`에 합류 ④글롭 매칭은 `ignore` 라이브러리(gitignore 문법) ⑤`nested_memory` 어태치먼트("Contents of <path>: ...")로 삽입, `loadedNestedMemoryPaths`(비축출 Set)로 세션 내 중복 방지. **진짜 PreToolUse/PostToolUse 훅 시스템과는 무관**(등록메커니즘·즉시성 없음, 공유 Set 기반 생산자-소비자 구조일 뿐).
   - **(신규) 수집(collection) vs 전처리(preprocessing) 구간 분리**: 수집=사이클 **꼬리**(도구 실행 직후, `query.ts:1569`, 메시지를 **더함** — rule/파일변경알림/스킬공지 등), 전처리 5단=**다음 사이클 머리**(모델 직전, `query.ts:364-463`, 메시지를 **줄임/다듬음** — applyToolResultBudget→snipCompact→microcompact→contextCollapse→autocompact). 수집이 먼저이므로 전처리는 방금 추가된 어태치먼트까지 포함해 정리. (어시스턴트가 최초 "다음 사이클 전처리가 우편함을 비운다"고 잘못 말했다가 소스 확인 후 자기 정정.)
   - **(신규) frontmatter 2단 구조의 4종 공통 + 3종 방아쇠**: "값싼 색인은 항상 보이게, 비싼 본문은 방아쇠 당길 때만" — rules(⚙️하네스/문법적 글롭매칭, `paths` 없으면 항상 즉시로드), skills(🧠모델/의미적, 본문은 `newMessages`로 isMeta user 메시지 주입, tool_result 아님, `SkillTool.ts:1065-1107`), agents(🧠모델/의미적, body=서브에이전트 시스템프롬프트), slash commands(⌨️유저/명시적). "frontmatter=항상 지연"은 아님(paths 없는 rule은 즉시로드, skill frontmatter는 조건이 아니라 카탈로그 메타데이터).
   - **(신규) 압축 직후 실제 관찰된 유저프롬프트 구성**: 0번 유령메시지 3키(claudeMd/userEmail/currentDate — 이번엔 실제 라이브 값으로 관찰, `userEmail=axtech@goldenplanet.co.kr`도 실측 확인됨. 참고: 1회차 요약에선 이 키가 소스 스냅샷의 `getUserContext()`엔 없어 "확인 못함"으로 표기했었음 — 실서비스와 로컬 재구성 소스의 차이가 재확인된 것). 압축 직후 추가 화물 5종: ①compact 요약문(8섹션 인수인계+jsonl경로+"이어서 하라" 지시) ②파일 리플레이(직전 Read 2개 파일 통째 재주입) ③호출됐던 스킬 재고지(visual-explainer 본문 전체, "재실행 금지" 리마인더) ④상주 리마인더(ToolSearch 지연도구목록/Agent타입목록/MCP서버instructions/SessionStart훅출력/날짜변경알림) ⑤방금 메시지(/compact stdout+실제질문).
   - **(신규) UserPromptSubmit 훅**: 턴 **입구**(제출 직후, 사이클0 이전)에 **턴당 1번**(사이클마다 도는 게 아님). `processUserInput.ts:149-264`: processUserInputBase → shouldQuery 판정(false면 훅도 스킵) → `executeUserPromptSubmitHooks` → queryLoop. stdin으로 `{hook_event_name:'UserPromptSubmit', prompt}` 전달. 설정에 없으면 즉시 스킵, 무한재귀 방지(프롬프트기반훅이 재차 UserPromptSubmit 발동 안 함). 4갈래 결과: blockingError(exit2)→프롬프트 차단, preventContinuation→처리중단(프롬프트는 남김), additionalContext(JSON)→`hook_additional_context` 주입, stdout(exit0)→`hook_success`로 주입되나 **SessionStart·UserPromptSubmit 2종만** stdout이 컨텍스트에 들어가고 다른 훅 이벤트 stdout은 버려짐. 전부 `wrapInSystemReminder`+isMeta user 메시지로 렌더링 — "다섯 번째 주입 트랙"(claudeMd/skill_listing/rules/skill본문에 이어). `<user-prompt-submit-hook>` XML 태그로 직접 감싸는 렌더링 코드는 이 스냅샷에서 **확인 못함**(시스템프롬프트 문구에만 남은 구버전 흔적으로 추정) — `constants/prompts.ts:128`의 `getHooksSection()`이 그 태그명을 언급하는 모델용 지시문.
   - **(신규, 미해결)** `getHooksSection()`이 최종 시스템 프롬프트에 실제로 포함되는 조건/위치 — 정의(`:127-129`)와 유일 호출처(`:192`)까진 확인, 호출 문맥(주변 섹션 리스트)은 확인 중 구간 종료.

3. Files and Code Sections:
   - **(승계) `src/services/tools/toolOrchestration.ts`, `src/Tool.ts:750-765`, `FileReadTool.ts:373`, `GrepTool.ts:183`, `src/query.ts:820-824,1371,655`** — 배치 파티셔닝 증거(reduce 병합규칙, TOOL_DEFAULTS 기본값 false, 모델 emit 순서 보존). 상세 코드는 1회차 요약 본문에 원문 보존.
   - **(승계, 생성물) `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md`** — §00 오해vs실제 표, §01~04 소스증거, §05 node 재현 결과, §06 파일겹침 무관 표, §07 요약+검증이력.
   - **(승계) `src/utils/api.ts:449-474` `prependUserContext`, `src/context.ts:155-189` `getUserContext`, `src/utils/messages.ts:3700-3738`, `src/utils/attachments.ts:2610-2751`, `src/utils/queryContext.ts`** — 0번 메시지/skill_listing 어태치먼트 구조.
   - **(신규) `src/utils/claudemd.ts`**
     - `:688-778` `processMdRules` — `.claude/rules/*.md` 재귀 처리, `visitedDirs`로 사이클 감지, ENOENT/EACCES/ENOTDIR는 빈 배열 반환.
     - `:1198-1238` `getManagedAndUserConditionalRules(targetPath, processedPaths)` — Managed 조건부 rule + (userSettings 활성 시) User 조건부 rule 순서로 수집.
     - `:1249` `getMemoryFilesForNestedDirectory` — CWD~대상 사이 각 디렉토리의 CLAUDE.md+rules 로드.
     - `:250-279` `parseFrontmatterPaths` — frontmatter `paths` 없으면 무조건부, `/**` suffix 제거, 전부 `**`면 무조건부 취급.
   - **(신규) `src/utils/attachments.ts`**
     - `:1660-1689` — targetPath~originalCwd 사이 `nestedDirs`(하향), root~cwd 사이 `cwdLevelDirs`(상향) 목록 구성.
     - `:1698-1707` `isInstructionsMemoryType`, `:1710` `memoryFilesToAttachments`(테스트용 export, LRU 축출 재주입 방지 회귀가드).
     - `:2165-2191` `getNestedMemoryAttachments` — trigger Set 없거나 size 0이면 즉시 return, 아니면 순회 후 `.clear()`.
     - `:818,872` — 순서 보장 주석("files are added to nestedMemoryAttachmentTriggers before nested_memory processes them").
   - **(신규) `src/tools/FileReadTool/FileReadTool.ts:848,870,1038`** — `context.nestedMemoryAttachmentTriggers?.add(fullFilePath)` (Read가 파일 읽을 때마다 트리거 등록, 3개 지점).
   - **(신규) `src/QueryEngine.ts:370,518`** — `nestedMemoryAttachmentTriggers: new Set<string>()` 생성(메인+포크 경로).
   - **(신규) `md_group/cc-context-preprocessing-timing.md`(71줄)** — 3계층 구조(대화턴⊃ReAct사이클⊃10단계파이프라인), 전처리 5단계 표(①applyToolResultBudget/②snipCompact/③microcompact/④contextCollapse/⑤autocompact — ②④는 스냅샷에 파일 없어 "확인 못함" 정직표기), "사이클마다 1번, 맨 위, 모델 호출 직전" 요약.
   - **(신규) `src/query.ts:1569-1579`** — 어태치먼트 수집 루프:
     ```ts
     for await (const attachment of getAttachmentMessages(
       null, updatedToolUseContext, null, queuedCommandsSnapshot,
       [...messagesForQuery, ...assistantMessages, ...toolResults], querySource,
     )) {
       yield attachment
       toolResults.push(attachment)
     }
     ```
   - **(신규) `src/tools/SkillTool/SkillTool.ts:1055-1107`** — skill 본문 로드: `parseFrontmatter(content, skillPath)`로 frontmatter 제거 → `finalContent`(Base directory 헤더 + `${CLAUDE_SKILL_DIR}`/`${CLAUDE_SESSION_ID}` 치환) 구성 → `addInvokedSkill(...)`(compaction-preservation 등록, compact 후 스킬 재고지의 근거) → `newMessages: [createUserMessage({content: finalContent, isMeta: true})]`로 주입(tool_result 아님).
   - **(신규) `src/tools/AgentTool/loadAgentsDir.ts:312-324`** — agent frontmatter 파싱, `name`/`description` 필수, `getParseError`로 에러 메시지 생성.
   - **(신규, 생성물) `/Users/seobi/jinsup_space/CC/컨텍스트-주입-4트랙-시각설명.html`** — visual-explainer 스킬로 생성, 다크테마(bg `#0d1015`, amber `#ffb020`=claudeMd, cyan `#3fd0c9`=skill_listing, green `#7ee081`=rules, violet `#b78cff`=skill본문, red `#ff5d5d`), 폰트(Black Han Sans/Gothic A1/IBM Plex Mono). 섹션: 01종착지는하나(색상코딩 배열스택)/02유령vs정주민(VS패널+표)/03rules우편함파이프라인(rule파일목업+5스텝플로우)/04수집꼬리vs전처리머리(사이클밴드+5단칩)/05frontmatter4종=방아쇠3종(★사용자 강조요청으로 3-Edit 재작업: ①2단로딩흐름도 `.ld/.ld-row/.stage/.tline` ②정밀비교표 `.fmt-wrap/.fmt` min-width 780px overflow-x ③방아쇠스펙트럼 `.spectrum/.zone/.zchip` 자동↔수동축). IntersectionObserver staggered reveal. `open` 명령으로 브라우저 오픈 완료. 섹션별 하단 출처(`src/utils/api.ts:449-474` 등) 표기, userEmail 미검증(당시)은 footer에 정직 표기.
   - **(신규) `src/utils/processUserInput/processUserInput.ts:140-210`** — `processUserInputBase` 호출 → `shouldQuery` 판정(false면 즉시 return) → `executeUserPromptSubmitHooks` 루프 → `blockingError` 시 `createSystemMessage`로 원입력 대체.
   - **(신규) `src/utils/hooks.ts`**
     - `:3826-3855` `executeUserPromptSubmitHooks` — `hasHookForEvent('UserPromptSubmit', ...)` 없으면 즉시 return, `hookInput={...createBaseHookInput(permissionMode), hook_event_name:'UserPromptSubmit', prompt}`, `yield* executeHooks(...)`.
     - `:1936-1939` `getUserPromptSubmitHookBlockingMessage`.
   - **(신규) `src/utils/messages.ts:4090-4139`** — 훅 결과 렌더링: `hook_blocking_error`/`hook_success`(SessionStart·UserPromptSubmit만 stdout 허용, 그 외는 `[]`)/`hook_additional_context`/`hook_stopped_continuation`/`compaction_reminder` — 전부 `wrapInSystemReminder(...)` + `createUserMessage({..., isMeta:true})`.
   - **(신규) `src/constants/prompts.ts`**
     - `:115` `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` 상수(기존에 알려진 캐시 경계 마커, 위치만 재확인).
     - `:117-124` `FRONTIER_MODEL_NAME = 'Claude Opus 4.6'`, `CLAUDE_4_5_OR_4_6_MODEL_IDS`(opus/sonnet/haiku 모델ID) — 부수 발견, 이번 조사의 핵심은 아님.
     - `:127-129` `getHooksSection()`:
       ```ts
       function getHooksSection(): string {
         return `Users may configure 'hooks', shell commands that execute in response to events like tool calls, in settings. Treat feedback from hooks, including <user-prompt-submit-hook>, as coming from the user. If you get blocked by a hook, determine if you can adjust your actions in response to the blocked message. If not, ask the user to check their hooks configuration.`
       }
       ```
       사용자가 자신의 실제 프롬프트에서 목격하고 "역할이 뭐냐"고 물은 바로 그 문단.
     - `:131-134` `getSystemRemindersSection()` — `<system-reminder>` 태그 설명 + "unlimited context through automatic summarization" 문구(참고로 확인됨).
     - `:136-139` `getAntModelOverrideSection()` — `USER_TYPE==='ant'` 조건(무관하지만 인접 코드로 확인됨).
     - `:192` — `getHooksSection()`의 **유일한 호출 지점**(grep으로 확인, 정의부 `:127` 외 이곳 하나뿐).
   - **(신규, 미완료) `src/constants/prompts.ts` offset=160,limit=50 Read 요청** — `getHooksSection()` 호출부(`:192`) 주변 문맥을 보려고 발행했으나 **결과 미수신인 채로 구간 종료**.
   - **(참고, 압축으로 재주입됨) `md_group/CLAUDE.md`, `md_group/cc-context-preprocessing-timing.md`** — 압축 직전 Read했던 파일 2개가 "Called the Read tool... Result:" 형태로 압축 직후 첫 호출에 통째로 리플레이됨(파일 내용 소실 방지 메커니즘으로 관찰).

4. Errors and fixes:
   - **(신규) 자기 정정 — 전처리 타이밍 오설명**: 어시스턴트가 처음 "다음 사이클 전처리가 우편함을 비운다"고 설명했으나, `query.ts:1569` 위치를 직접 확인한 뒤 "제가 앞에서 '다음 사이클 전처리가 우편함을 비운다'고 한 표현은 부정확했어요"라고 스스로 정정 — 실제로는 같은 사이클 꼬리(수집)와 다음 사이클 머리(전처리 5단)가 별개 구간.
   - **(신규) 사용자 피드백 — 설명 밀도 과다**: "음..???? 이해가 안되네"에 대해, 파이프라인을 한 번에 5단계로 쏟아낸 게 원인으로 판단하고 구체 시나리오(`api-rule.md`+세션타임라인) 재설명으로 대응, 3요점으로 압축. 교훈: 사용자는 밀도 높은 기술설명보다 시나리오 우선 설명을 선호.
   - **(신규, 미해결) 질문 오독**: 사용자의 "user-prompt-submit-hook 이건 언제씡늑너지"를 어시스턴트가 "훅이 언제 발동하는가"(일반 타이밍 질문)로 해석해 상세 답변했으나, 사용자가 "무슨말이야? 나프롬프트 중에 [getHooksSection 문단 인용] 이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구....."라고 재질문 — 실제 의도는 "본인이 목격한 그 특정 문단(시스템 프롬프트 텍스트)의 정체/역할"이었음이 드러남. 어시스턴트가 "아 질문 의도를 제가 빗나갔네요"라고 명시적으로 인정하고 `getHooksSection()` 정의/호출부 재조사를 시작했으나 **구간 종료 시점까지 답변을 완성하지 못함**.
   - **(승계) 사용자 가설 정정 2건**: 배치분리=파일기준(X, emit순서 기준), 0번메시지=CLAUDE.md+스킬목록 동시포함(X, 스킬목록은 별도 어태치먼트).

5. Problem Solving:
   - rules 지연주입 파이프라인을 "우편함" 비유로 최종 확정하고, 진짜 훅 시스템과 무관함을 명시적으로 구분.
   - 수집(사이클 꼬리, 메시지를 더함)과 전처리(다음 사이클 머리, 메시지를 줄임)라는 두 구간을 자기 정정을 거쳐 정확히 분리.
   - frontmatter 2단 구조(색인 항상/본문 지연)가 rules/skills/agents/commands 4종에 공통이며, 발동 주체(하네스/모델/유저) 3갈래로 분화된다는 일반화된 모델을 소스 근거와 함께 확립.
   - 위 컨텍스트 주입 아키텍처 전체를 `visual-explainer` 스킬로 시각화한 `컨텍스트-주입-4트랙-시각설명.html`을 완성, 사용자가 강조 요청한 섹션을 재작업.
   - 압축(`/compact`) 직후 실제 API 호출에 담기는 화물을 실측(0번 유령메시지 실제값 + 5종 특수화물)해 이론(소스 스냅샷 기반)과 실측(라이브 세션) 사이의 간극(`userEmail` 키)을 재확인.
   - UserPromptSubmit 훅의 발동 타이밍·4갈래 결과·렌더링 위치를 소스로 규명했으나, 사용자의 실제 질문 의도(목격한 특정 문단의 정체)를 오독했음이 드러나 **진행 중, 미해결**로 이번 구간이 종료됨.

6. All user messages:
   - (승계) "클로드코드 전체파악해봐라"
   - (승계) "4번은 무슨말이지"
   - (승계) "근데 단독이면 Read,Read, Grep,Edit, Write 가 한배치에 나오면 1배치에 Read, Read, Grep 이고 2배치에 Edit 3배치에 Write 야?"
   - (승계) "이건 소스코드 보고 증명해봐"
   - (승계) "증거4 후자의 경우 Read -> Edit 하고 다시 병렬이됬잖아? 중간에 Edit이 낀 이유는 같은파일 기준이라 그래?"
   - (승계) "아 이해했다 오케이"
   - (승계) "아 저건 몰랐네.. 단독 .. 이라는 개념이구나 나 분리만하는줄 저거 너가 테스트해본거까지 md로 마들어주라"
   - (승계) "내가 알기로는 0번 유저프롬프트에 CLAUDE.md 관련내용과 함께 현재 스킬목록도 들어가는걸로 알고있어 맞아?"
   - (승계) "어쨋든 타이밍은 배열로 들어간다는거지"
   - (승계) "그리고 그 rules로 하면 필요한 상황일떄 그걸로가져와쓰잖아 그건 어떻게 세팅한거지"
   - (승계) "음..???? 이해가 안되네"
   - (승계) "Read툴이 읽으면 마치 훅마냥 잡아서 실행해서 어태치먼트로 넣는거야?"
   - (승계) "ReAct 사이클 전처리가 도구결과 보낼떄 인건가"
   - (승계, mid-work) "컨텍스트 전처리 하는 구간과는 다른거지?"
   - (승계) "프론트메타로 쓰는건 다그렇다고봐야돼? 스킬도 포함해서?"
   - (승계) "위 내용들도 /visual-explainer 로 작성해줘"
   - (승계, mid-work, frontmatter 4종 표 붙여넣음) "특히 이거 잘작성해줘"
   - **(신규)** "[슬래시커맨드 /compact]" (사용자가 직접 `/compact` 실행)
   - **(신규)** "지금 유저프롬프트로 내용 뭐들어가?"
   - **(신규)** "user-prompt-submit-hook 이건 언제씡늑너지"
   - **(신규)** "무슨말이야? 나프롬프트 중에 \n\n - 사용자는 설정에서 도구 호출 등의 이벤트에 반응하여 실행되는 셸 명령인 'hooks'를 구성할 수 있습니다. <user-prompt-submit-hook>을 포함한 hooks의 피드백은 사용자로부터 온 것으로 취급하세요. hook에 의해 차단되면, 차단된 메시지에 대응하여 행동을 조정할 수 있는지 판단하세요. 불가능하면 사용자에게 hooks 설정을 확인하도록 요청하세요.\n\n이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구....."

7. Pending Tasks:
   - **(신규, 최우선)** `getHooksSection()`이 실제 시스템 프롬프트 조립 시 어떤 위치/조건으로 포함되는지 규명하고, 사용자가 목격한 그 문단("사용자는 설정에서... hooks 설정을 확인하도록 요청하세요.")의 정체·출처·역할을 정확히 답하는 것. `prompts.ts:127-129`(정의) `:192`(호출)까지 확인됨, 호출 문맥(offset 160-210)은 미확인.
   - (승계, 여전히 미요청) `배치-단독-개념-소스증명.md`의 HTML 시각화 짝꿍 문서 — 제안만 됨, 사용자 요청 없음.
   - (승계, 여전히 미요청) `siblingAbortController` 형제 abort 및 동시성 한도 10 초과 시 큐잉 동작 추가 설명 — 사용자 관심 시 진행 예정, 현재 미요청.

8. Current Work:
   사용자의 재질문("무슨말이야? 나프롬프트 중에 [getHooksSection 문단 인용] 이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구.....")에 답하기 위해, 어시스턴트가 이미 다음을 확인했다:
   - `src/constants/prompts.ts:115-139` Read — `getHooksSection()` 함수 정의(원문 위 3번 항목에 그대로 기록) 및 인접 상수/함수(`__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__`, `FRONTIER_MODEL_NAME`, `CLAUDE_4_5_OR_4_6_MODEL_IDS`, `getSystemRemindersSection`, `getAntModelOverrideSection`) 확인.
   - `grep -n "getHooksSection" /Users/seobi/jinsup_space/CC/src -r` 실행 — 결과: `prompts.ts:127`(정의)와 `prompts.ts:192`(호출) 단 두 곳뿐.
   - 마지막 액션: `Read /Users/seobi/jinsup_space/CC/src/constants/prompts.ts offset=160 limit=50` 호출 — `getHooksSection()` 호출부(`:192`)가 어떤 리스트/조건 안에서 조립되는지 보려는 것. **이 호출의 결과를 아직 받지 못한 채 대화 구간이 끝남.**

9. Optional Next Step:
   `prompts.ts` offset=160-210 Read 결과를 확인해 `getHooksSection()`이 시스템 프롬프트 조립부의 어떤 섹션 리스트(다른 `getXxxSection()` 함수들과 나란히 배열되는 구조로 추정)에 언제나 포함되는지, 조건부인지를 규명한 뒤, 그 결과를 바탕으로 사용자의 실제 질문 — "이 문단이 왜 내 프롬프트(시스템 프롬프트)에 나왔고 역할이 뭐냐" — 에 정확히 답한다. 직접 인용 근거(사용자의 마지막 메시지): "이걸봐서 뭔가해서 물어본거야 역할이 뭐냐구....." — 이 질문에 대한 답을 완성하는 것이 다음 단계이며, 다른 화두로 넘어가지 않는다.
</summary>
