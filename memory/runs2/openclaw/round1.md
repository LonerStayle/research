## Decisions

- 사용자가 "클로드코드 전체파악해봐라"고 요청 → 프로젝트 CLAUDE.md 지침에 따라 탐색은 Explore 서브에이전트에 위임. 서브에이전트가 /Users/seobi/jinsup_space/CC 워크스페이스(md_group 140개 파일/51,351줄, html_group_v2 138개 파일, src/ 1,904개 파일/301개 디렉토리)를 전수 탐색해 4계층 아키텍처(엔트리 main.tsx → 엔진 query.ts/QueryEngine.ts → 도구 10단계 파이프라인 → Ink/React TUI), 12개 문서 주제군, 10가지 핵심 발견을 담은 종합 보고서를 반환. 최신 커밋은 2222679(문서 홈 경로 `~` 중립화), md 135개 전량 재검증 완료(2026-07-07 기준, 89개 파일·296건 교정).
- "배치 병렬의 3조 요건"(4번 발견)을 사용자에게 재설명: ①모델이 한 응답에 여러 tool_use를 emit ②각 도구의 `isConcurrencySafe` 판정 ③하네스의 `partitionToolCalls`가 배치로 묶어 dispatch.
- 사용자 질문(Read,Read,Grep,Edit,Write 예시)에 대해 "배치1=[Read,Read,Grep] 병렬 / 배치2=[Edit] 단독 / 배치3=[Write] 단독"이 맞다고 확인.
- 사용자 요청으로 소스코드 기반 증명 수행: `src/services/tools/toolOrchestration.ts`의 `partitionToolCalls`(reduce 로직, safe && 직전배치도 safe일 때만 병합, 아니면 무조건 새 배치)와 각 도구의 `isConcurrencySafe` 값(Read/Grep=true, Edit/Write는 override 없어 `Tool.ts`의 기본값 false 적용)을 grep/Read로 확인. node -e 로 파티션 로직을 그대로 재현 실행해 다음 결과를 얻음:
  - `["Read","Read","Grep","Edit","Write"]` => 병렬["Read","Read","Grep"] → 단독["Edit"] → 단독["Write"]
  - `["Read","Edit","Read","Grep"]` => 병렬["Read"] → 단독["Edit"] → 병렬["Read","Grep"]
- 사용자가 두 번째 케이스(Read→Edit→Read,Grep)의 재병합 이유를 "같은 파일이라서?"로 추측 → 소스 확인 결과 **파일 경로는 전혀 보지 않음**. 순서는 순수하게 "모델이 assistant message content에서 tool_use를 emit한 순서"(`query.ts:820-824`, filter가 순서 보존)이며, 하네스는 재배열하지 않음. `partitionToolCalls`가 참조하는 정보는 도구 이름과 파싱된 입력뿐, 이웃 호출 간 파일 겹침 비교 로직은 존재하지 않음.
- 위 내용을 "분리(separation)"가 아니라 "단독(solo)" 개념으로 교정하는 문서 `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md`를 신규 작성(`배치-세계-전수도감.md`의 자매 문서, 같은 루트 위치, `~` 중립 경로 표기 관례 따름). 구성: §00 오해 vs 실제, §01~04 소스 증거 4개, §05 실행 시연(node 재현), §06 파일 겹침 무관 표, §07 요약+검증 이력(2026-07-10).
- 사용자 질문("0번 유저프롬프트에 CLAUDE.md와 스킬목록이 같이 들어가나?")에 대해 조사 후 **절반만 맞다**고 정정:
  - CLAUDE.md는 맞음: `src/utils/api.ts`의 `prependUserContext`(449-474줄)가 `getUserContext()`(`src/context.ts:155-189`, 반환 키는 `claudeMd` + `currentDate` 둘뿐, 이 재구성 소스 기준 `userEmail` 키는 없음)를 매 API 호출마다(`src/query.ts:655`) 메시지 배열 맨 앞(index 0)에 즉석 재생성하여 붙임. 대화 이력에는 저장되지 않는 "매번 재생성되는 프리픽스".
  - 스킬 목록은 틀림: 별도의 `skill_listing` 어태치먼트로, 완전히 다른 파이프라인(`src/utils/attachments.ts:875` `getSkillListingAttachments`(정의 2661-2751줄) → `src/utils/messages.ts:3728-3738`에서 렌더링). CLAUDE.md와 달리 어태치먼트로 이력 스트림에 1회 삽입되어 실제로 남는 메시지이며, 델타 방식(`sentSkillNames`로 이미 보낸 스킬 추적, attachments.ts:2718), `--resume` 시 억제(`suppressNextSkillListing`, attachments.ts:2633), 컴팩트 후 재주입 안 함(~4K 토큰 절약, attachments.ts:2610-2611), Skill 도구 있는 에이전트만 대상(attachments.ts:2668-2673), 스킬서치 활성 시 bundled+MCP만 필터링·30개 초과 시 bundled만(`FILTERED_LISTING_MAX=30`, attachments.ts:2641).
- 사용자 확인("어쨋든 타이밍은 배열로 들어간다는거지")에 대해: 맞음 — claudeMd와 skill_listing 둘 다 API의 `system` 파라미터가 아니라 `messages` 배열에 `createUserMessage({..., isMeta: true})`로 들어가는 일반 user 메시지. 차이는 claudeMd가 "매번 앞에 재생성되는 유령 메시지"인 반면 skill_listing은 "이력에 박혀 계속 흘러가는 실제 메시지"라는 점.

## Open TODOs

- 사용자의 마지막 질문("그리고 그 rules로 하면 필요한 상황일떄 그걸로가져와쓰잖아 그건 어떻게 세팅한거지" — "rules"가 필요한 상황에만 끌려와 쓰이는 메커니즘이 어떻게 세팅되어 있는지)에 대한 조사가 시작만 되고 미완료 상태로 대화 구간이 끝남. 마지막 도구호출은 `grep -rn "\.claude/rules\|claude/rules\|rulesDir\|ruleFiles\|loadRules" ...` 및 `nested_memory` 생성부 검색이었고, 결과는 아직 반환되지 않음(대화 로그가 이 지점에서 절단됨).
- (제안만 됨, 요청 없음) `배치-단독-개념-소스증명.md`의 HTML 시각화 버전 제작을 어시스턴트가 제안했으나 사용자는 아직 요청하지 않음.

## Constraints/Rules

- 이 워크스페이스(연구 레포)의 탐색 작업은 프로젝트 CLAUDE.md 지침에 따라 Explore 서브에이전트에 위임하고, 실행/작성은 메인에서 직접 수행.
- 새 분석 문서는 기존 도감류 문서(`배치-세계-전수도감.md`) 옆에 자매 문서로 작성하고, 레포 관례대로 경로 표기를 `~` 중립/상대 경로로 맞춤.
- 서브에이전트 결과 원본 JSONL 트랜스크립트(`.output` 파일)는 절대 Read/tail 하지 않는다(컨텍스트 오버플로 위험) — 완료 알림의 `<result>` 요약만 사용.
- 모든 기술적 주장은 로컬 재구성 소스(`~/jinsup_space/CC/src`)에서 grep/Read로 직접 검증(문서 자체 관례이자 이번 대화에서 반복 적용된 방식).

## Pending user asks

- "그리고 그 rules로 하면 필요한 상황일떄 그걸로가져와쓰잖아 그건 어떻게 세팅한거지" — 아직 답변되지 않음. (필요 시에만 로드되는 "rules" 파일 메커니즘의 세팅 방식에 대한 질문. 조사 진행 중이던 grep 결과가 대화 절단으로 유실됨 — 재개 시 이 조사를 이어서 완료해야 함.)

## Exact identifiers

- 워크스페이스 루트: `/Users/seobi/jinsup_space/CC`
- 서브에이전트 ID: `a9efccf2cb8c4f323`
- 서브에이전트 output_file: `/private/tmp/claude-501/-Users-seobi-jinsup-space-CC/c36aeba7-7619-425b-b98f-6585ccf6794d/tasks/a9efccf2cb8c4f323.output`
- 서브에이전트 tool-use-id: `toolu_01R8RH5T2ZfVZYs6MnhpED1h`
- 서브에이전트 소요: `subagent_tokens=72605`, `tool_uses=44`, `duration_ms=160938`
- 신규 작성 문서: `/Users/seobi/jinsup_space/CC/배치-단독-개념-소스증명.md`
- 참조 원본 문서: `/Users/seobi/jinsup_space/CC/배치-세계-전수도감.md` (244줄)
- 변경내역 문서: `md_group-교정-변경내역.md` (100KB, md 135개 전량 검증, 89개 파일·296건 교정)
- 최근 커밋: `2222679` (문서 홈 경로 `~` 중립화)
- 검증/작업 완료일: `2026-07-07` (md_group 최종 검증), `2026-07-10` (배치-단독-개념-소스증명.md 검증 이력)
- 소스 파일/라인:
  - `src/services/tools/toolOrchestration.ts` — `partitionToolCalls`(95-116줄), `runTools`(19-56줄+), `getMaxToolUseConcurrency`(8-12줄, 기본값 10, env `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`)
  - `src/Tool.ts` — `TOOL_DEFAULTS`(753-762줄 부근), `isConcurrencySafe: (_input?: unknown) => false`(759줄, "assume not safe")
  - `src/tools/FileReadTool/FileReadTool.ts:373` — `isConcurrencySafe() { return true }`
  - `src/tools/GrepTool/GrepTool.ts:183` — `isConcurrencySafe() { return true }`
  - `src/tools/FileEditTool/FileEditTool.ts:86` — `buildTool({...})` (isConcurrencySafe override 없음)
  - `src/tools/FileWriteTool/FileWriteTool.ts:94` — `buildTool({...})` (isConcurrencySafe override 없음)
  - `src/query.ts:820-824` — `msgToolUseBlocks = message.message.content.filter(content => content.type === 'tool_use')`, `toolUseBlocks.push(...msgToolUseBlocks)`
  - `src/query.ts:1371` — `runTools(toolUseBlocks, assistantMessages, canUseTool, toolUseContext)` 호출
  - `src/query.ts:655` — `messages: prependUserContext(messagesForQuery, userContext)`
  - `src/utils/api.ts:449-474` — `prependUserContext` 함수 정의
  - `src/utils/api.ts:463` — 문자열 ``<system-reminder>\nAs you answer the user's questions...``
  - `src/context.ts:155-189` — `getUserContext`, 반환 키: `claudeMd`, `currentDate`
  - `src/utils/messages.ts:3728-3738` — `skill_listing` 케이스, 문자열 "The following skills are available for use with the Skill tool:\n\n..."
  - `src/utils/attachments.ts:875` — `maybe('skill_listing', () => getSkillListingAttachments(context))`
  - `src/utils/attachments.ts:2661-2751` — `getSkillListingAttachments` 정의
  - `src/utils/attachments.ts:2610-2611` — 컴팩트 후 재주입 안 함 주석(~4K 토큰/이벤트 절약)
  - `src/utils/attachments.ts:2633` — `suppressNextSkillListing()`
  - `src/utils/attachments.ts:2641` — `FILTERED_LISTING_MAX = 30`
  - `src/utils/attachments.ts:2668-2673` — Skill 도구 보유 에이전트만 대상 조건
  - `src/utils/attachments.ts:2718` — `sentSkillNames` 델타 추적
  - `src/utils/queryContext.ts` — 전체 파일(1-41줄 확인), systemPrompt/userContext/systemContext가 API 캐시 키 프리픽스 구성
- 미완료 grep 명령(대화 절단 시점): `grep -rn "\.claude/rules\|claude/rules\|rulesDir\|ruleFiles\|loadRules" /Users/seobi/jinsup_space/CC/src --include="*.ts" --include="*.tsx" -l | head; echo "---nested_memory 생성부---"; grep -rn "nested_memory" /Users/seobi/jinsup_space/CC/src --include="*.ts" --include="*.tsx" | grep -v "messages.tsx\|AttachmentMessage" | head`
- 데이터소스 파일(이번 컴팩션 입력): `/Users/seobi/jinsup_space/research/memory/data2/conv2-01.part1.txt`
