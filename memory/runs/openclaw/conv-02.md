# OpenClaw 컴팩션 시뮬레이션 — conv-02

> 적용 프롬프트: `memory/techniques/openclaw-prompt.md` (주석 헤더 제외 본문) · 대상 대화: `memory/data/conv-02.txt`
> 치환부(YYYY-MM-DD, {previousSummary}, {reasons}, Current time 등)는 규칙에 따라 무시(리터럴 유지).

## 단계 1 (+1b): 사전 메모리 플러시

대상 파일: `memory/YYYY-MM-DD.md` (신규 생성 → 이후엔 APPEND only, 타임스탬프 변형 파일명 금지. MEMORY.md/DREAMS.md/SOUL.md/TOOLS.md/AGENTS.md는 read-only). 아래가 append되는 내용 전문.

```markdown
## 세션 메모 — 클로드코드 내부 구조 검증 + hermes-agent 툴콜 루프

### 확정 사실 — 클로드코드 (로컬 재구성 소스 /Users/seobi/jinsup_space/CC)
- 스킬 목록 예산: 고정 8,000자가 아니라 컨텍스트 윈도우의 1% (`SKILL_BUDGET_CONTEXT_PERCENT = 0.01`, src/tools/SkillTool/prompt.ts:21). 200K 윈도우 = 8,000자, 폴백 `DEFAULT_CHAR_BUDGET = 8_000` (prompt.ts:23), env `SLASH_COMMAND_TOOL_CHAR_BUDGET` 우선. 예산은 목록 총량이고 개당 설명 컷은 250자(`MAX_LISTING_DESC_CHARS`, prompt.ts:29). 초과 시 bundled 설명 보존 + 나머지 균등 절단, 20자 미만이면 이름만 — 이름은 절대 목록에서 누락 안 됨(prompt.ts:211).
- 공식 문서(code.claude.com/docs/en/skills) 현행 버전 차이: 개당 컷 1,536자(`skillListingMaxDescChars`), 절단 순서는 "가장 덜 invoke한 스킬부터". 예산 1%는 동일, `skillListingBudgetFraction`으로 조정 가능. 컴팩션 후 invoke했던 스킬 재부착: 스킬당 5,000토큰/합산 25,000토큰.
- lost-in-the-middle 해법: `EXPERIMENTAL_SKILL_SEARCH` 게이트의 skill discovery — getTurnZeroSkillDiscovery(attachments.ts:803-813), filterToBundledAndMcp(attachments.ts:2662-2674, 상한 30 `FILTERED_LISTING_MAX`), stripReinjectedAttachments(compact.ts:211-223). 기본 빌드는 compact 후 skill_listing 재주입 안 함(compact.ts:524-529). 구현체 skillSearch/prefetch.ts는 외부 빌드에 없음.
- CC에 없는 유명 기술(grep 검증): 임베딩 검색·BM25/TF-IDF·벡터DB·RAG(rerank/retrieval)·고정 워크플로우 그래프·리플렉션(self-critique)·ToT/MCTS/beam/self-consistency·멀티에이전트 debate/judge·코드베이스 사전 인덱싱·시맨틱 캐싱·프롬프트 압축·파인튜닝/학습 라우터·moderation 엔드포인트. bash 권한 분류기는 개념상 존재하나 ANT-ONLY 스텁(utils/permissions/bashClassifier.ts).
- 메모리 회상: 임베딩 대신 Sonnet LLM 셀렉터 sideQuery(파일명+description manifest 전달, 최대 5개 선택, max_tokens 256, src/memdir/findRelevantMemories.ts). 발사는 사용자 턴당 1회(query.ts:299, 툴콜 루프 밖), 주입은 툴콜 루프 안 도구 결과 뒤(query.ts:1587-1602, settledAt 폴링, 논블로킹). LLM 개입은 파이프라인 중 ④셀렉터 딱 한 곳.
- "이미 보여줬다" 판정: 장부 없이 대화 메시지 스캔(collectSurfacedMemories, attachments.ts:2250-2265) — 컴팩션으로 첨부가 사라지면 기준도 자동 리셋. 생존 조건 AND: `!readFileState.has(m.path) && !alreadySurfaced.has(m.path)` (attachments.ts:2230). 후보 0개면 Sonnet 호출 생략(findRelevantMemories.ts:46-51).
- 한도: 턴당 5개, 파일당 4KB(`MAX_MEMORY_BYTES` 4096)/200줄(`MAX_MEMORY_LINES`), 세션 누적 60KB 스로틀(`MAX_SESSION_BYTES`, prod ~26K토큰/세션 관측이 도입 배경), 스캔 최대 200파일. 나이 헤더("47 days ago" + 낡음 경고)는 주입 시 1회만 계산 — 재계산하면 프롬프트 캐시 파괴(attachments.ts:505-512).
- frontmatter 파서(src/utils/frontmatterParser.ts): 앞 30줄만 읽고 정규식 `/^---\s*\n([\s\S]*?)---\s*\n?/`(:123) → YAML 1차 → `quoteProblematicValues` 자동 따옴표 보정 2차(:85-121) → 실패 시 빈 {} 폴백. 스킬/커맨드/에이전트 정의와 파서 공유.
- 셀렉터 비용: 메모리 200개 × 100턴 이론 상한 ~$2.9 (호출당 ~$0.03, Sonnet $3/$15 per MTok), 현실 <$1 (60KB 스로틀·목록 축소·스킵 조건). 요청이 `Query: <질문>` 선두 구조라 프롬프트 캐시 못 씀(findRelevantMemories.ts:105).
- 커맨드=스킬 통합: `.claude/commands/`는 `commands_DEPRECATED`(commands.ts:574-576), 이름+설명은 세션 시작부터 skill_listing에 상주·본문은 invoke 시에만 로드. `disable-model-invocation: true`만 목록에서 완전 제외(유저 전용). 공식 문서 원문 "Custom commands have been merged into skills." 로 확정.

### 확정 사실 — hermes-agent (~/jinsup_space/hermes-agent)
- 메인 루프 run_conversation(run_agent.py:10774, max_iterations 기본 90 + 서브에이전트 50 `IterationBudget:273`), 디스패처 _execute_tool_calls:9632 → _invoke_tool:9674, assistant(tool_calls 포함) 먼저 append(13725). 내부 포맷은 OpenAI 스타일(role:"tool", tool_call_id), anthropic_adapter.py가 변환 — 연속 tool_result 한 user 메시지로 병합(1544-1548), orphan tool_use/tool_result 제거(1568-1600, "Anthropic rejects these with a 400.").
- 도구 에러는 배치를 안 멈춤: try/except가 `Error executing tool '{function_name}': {tool_error}` 문자열로 흡수(9956-9967) 후 정상 tool 메시지로 반환, _detect_tool_failure(display.py:804)는 is_error 태그만. 중단은 유저 인터럽트(10171-10184)와 가드레일 halt(13742-13750)뿐.
- LLM용 에러 설명은 일반적으로 큐레이션 없음(제네릭 템플릿/도구별 ad hoc). error_classifier.py의 FailoverReason 분류는 코드용(재시도/크리덴셜 교체/failover) — LLM에게 안 감. 예외: tools/file_tools.py read_file은 자가복구 안내 큐레이션(10만 자 한도 시 "Use offset and limit to read a smaller range" + total_lines 제공, 바이너리는 vision_analyze 지목).
- 병렬 함수콜링: 3사 API 모두 기본 ON. 끄기/통제 — Anthropic `tool_choice: {disable_parallel_tool_use: true}`, OpenAI `parallel_tool_calls: false`, Gemini는 토글 없음(`toolConfig.functionCallingConfig.mode` AUTO/ANY/NONE + `allowedFunctionNames`).
- 도구 순서(2→1) 은은한 유도: ① description에 의존성 서술 + ② input_schema required 인자로 선행 도구 출력 요구 조합 추천. 하네스 강제는 _execute_tool_calls_sequential(10165) + _NEVER_PARALLEL_TOOLS.

### 산출물 (이 세션에서 작성)
- /Users/seobi/jinsup_space/CC/스킬예산-로스트인더미들.html (visual-explainer, 다크 잉크 + 앰버/시안)
- /Users/seobi/jinsup_space/CC/메모리-회상-파이프라인-총정리.md + .html (장서각 메타포; 이후 증보: 조기 종료 분기, [코드]/[LLM] 태그, 발사vs주입 2레인 타임라인, frontmatter 부록 §2.5, 제외 조건 진리표)

### 사용자 컨텍스트
- 한국어 대화. 어려운 개념은 비유(진동벨=Promise, 도서관/장부, 바코드=임베딩)로 재설명을 자주 요구 — 처음부터 쉬운 설명 선호.
- 도구 순서 유도 질문의 실제 상황(도구 1·2 간 실데이터 의존 여부) 답변 대기 중.
- 세션 중 Fable 5 크레딧 소진 → /model로 Sonnet 5 → Opus 4.8 전환(기본 저장), /login 수행.
```

턴 응답: NO_REPLY

## 단계 2: 컴팩션 요약 (safeguard 기본 customInstructions 적용)

## Decisions

- 사용자의 "스킬 디스크립션 총량 8,000자" 주장은 정정하여 합의: 고정값이 아니라 **컨텍스트 윈도우의 1%**이며 8,000자는 200K 윈도우 기준값이자 폴백(`DEFAULT_CHAR_BUDGET = 8_000`). "짤림"은 스킬이 목록에서 빠지는 게 아니라 설명만 깎이는 방식(균등 절단 → 극단 시 이름만, bundled 설명은 보존, 이름은 항상 포함).
- 8,000자는 **목록 총량** 예산, 250자(`MAX_LISTING_DESC_CHARS`)는 **개당** 설명 상한으로 구분 확정.
- 공식 문서 대조 결과 로컬 소스와 버전 차이 2건 확인 — 개당 컷은 현행 1,536자(`skillListingMaxDescChars`), 절단 순서는 균등 절단이 아니라 "가장 덜 invoke한 스킬부터". 최신 기준으로는 1,536자로 말하는 게 맞다고 결론.
- lost-in-the-middle 해결 코드 = `EXPERIMENTAL_SKILL_SEARCH` 피처 플래그 아래 skill discovery 시스템으로 확정 (정적 turn-0 `skill_listing` → 턴별 `skill_discovery` 재주입 전환; 3요소 = getTurnZeroSkillDiscovery / filterToBundledAndMcp / stripReinjectedAttachments). 일반 빌드 기본 동작은 여전히 turn 0 1회 주입 + compact 후 재주입 안 함.
- 클로드코드에 임베딩 검색·BM25·벡터DB·RAG(rerank)·고정 워크플로우 그래프·리플렉션 부재를 grep으로 전부 확인. 추가 부재: ToT/MCTS/beam/self-consistency, 멀티에이전트 debate/judge, 코드베이스 사전 인덱싱, 시맨틱 캐싱, 프롬프트 압축, 파인튜닝/학습 라우터/DSPy, moderation 엔드포인트. "의도 분류"만 뉘앙스 — bash 권한 분류기는 존재하나 ANT-ONLY 스텁이라 외부 기준 "없음"이 맞음.
- 메모리 회상은 임베딩이 아니라 **Sonnet LLM 셀렉터**(sideQuery)로 동작: 매 사용자 턴 백그라운드 prefetch 1회, manifest(파일명+한 줄 설명) 전체를 Sonnet에게 주고 최대 5개 선택(JSON, max_tokens 256). 파이프라인 8지점 중 LLM 개입은 ④셀렉터 한 곳뿐(나머지는 일반 코드/파일시스템).
- ② 서고 스캔은 질문과 무관한 전수 조사(`scanMemoryFiles(memoryDir, signal)` — query 인자 없음); 질문은 ④ 셀렉터에서 처음 등장.
- "이미 보여줬다" 기준은 별도 장부가 아니라 **대화 메시지 스캔**(collectSurfacedMemories): relevant_memories 첨부의 path 수집 → 컴팩션으로 첨부가 사라지면 기준 자동 리셋("보여줬다" = "모델이 지금 기억하고 있다"). 후보 생존은 AND 조건 `!readFileState.has(m.path) && !alreadySurfaced.has(m.path)`, 후보 0개면 Sonnet 호출 없이 조기 종료.
- 발사 vs 주입 분리 확정: 발사는 턴당 1회(툴콜 루프 밖), 주입은 툴콜 루프 안에서 도구 결과 뒤에 실려 다음 API 요청에 포함(settledAt 폴링, consumedOnIteration). 스킬 discovery 프리페치는 반대로 매 반복 발사.
- 메모리 나이 헤더는 주입 시 1회만 계산(재계산 시 "3 days ago"→"4 days ago" 바이트 변화로 프롬프트 캐시 파괴). 2일 이상이면 낡음 경고문 전문 부착, 신선하면 괄호 표기만.
- 셀렉터 비용 추정: 메모리 200개 × 100턴 이론 상한 ~$2.9(호출당 ~$0.03, Sonnet $3/$15 per MTok), 현실 <$1 (60KB 세션 스로틀·목록 축소·스킵 조건). 셀렉터 요청은 `Query: <질문>`이 선두라 프롬프트 캐시를 구조적으로 못 씀 — 메인 대화는 반대로 캐시 최적화 철저.
- 커맨드와 스킬은 내부적으로 동일 `Command` 타입으로 통합(`commands_DEPRECATED`): 이름+설명은 세션 시작부터 상주, 본문은 invoke 시에만 로드, `disable-model-invocation: true`만 완전 제외. 공식 문서 "Custom commands have been merged into skills."로 재확정.
- 산출물은 md+html 쌍으로 레포 루트에 저장하는 기존 관례 유지, 모든 섹션에 `파일:line` 출처 표기, 미확인 항목은 별도 표기.
- 올드스쿨 툴콜 루프 설명(4조각: 도구 정의/system/디스패처/while 루프 + 함정 3개: assistant content 통째 보존, tool_use_id 매칭, 병렬 결과 한 user 메시지)은 hermes-agent 실코드로 전부 검증되어 정확 판정. hermes는 내부 OpenAI 포맷 + 프로바이더별 어댑터 변환 구조이며, 어댑터가 3함정을 자동 방어.
- 도구 호출 순서(2→1) 은은한 유도는 ① description 의존성 서술 + ② 스키마 required 인자 조합 추천 (③ 병렬 끄기+시스템 프롬프트, ④ 하네스 강제는 대안).
- 3사 API 병렬(멀티) 함수콜링은 전부 기본 ON — 활성화가 아니라 통제가 설계 포인트 (Anthropic `disable_parallel_tool_use` / OpenAI `parallel_tool_calls: false` / Gemini는 토글 없이 `mode` enum).
- hermes에서 도구 에러는 배치를 멈추지 않음: 예외를 에러 문자열 결과로 흡수해 정상 tool 메시지로 반환, 10개면 10개 다 실행. 중단은 유저 인터럽트와 가드레일 halt 2가지뿐.
- LLM용 에러 설명은 일반적으로 큐레이션 없음(제네릭 템플릿 1개 + 도구별 ad hoc). 정교한 분류(error_classifier의 FailoverReason)는 하네스 제어용이라 LLM에 안 감. 예외적으로 read_file 도구만 자가복구 안내를 손으로 설계(한도 초과 시 offset/limit 안내 + 총 줄 수, 바이너리는 vision_analyze 지목) — 갈림 기준은 "모델 실수의 손해 크기".

## Open TODOs

- (제안 상태, 사용자 응답 대기) `스킬예산-로스트인더미들.html`에 이 세션 실제 truncation 사례 재현 추가 / 라이트 테마 버전 / `md_group/tools_info/tools_detail/SkillTool.md`에 HTML 링크 추가.
- (제안 상태, 사용자 응답 대기) `메모리-회상-파이프라인-총정리` md/html의 `md_group/`·`html_group_v2/` 복사본 배치, 섹션 추가/수정.
- (제안 상태) HTML 섹션 04 다이어그램이 안 읽히면 블록에 턴 번호 부여 또는 스캔 과정 애니메이션 단계 분해로 재작성.
- 도구 순서(2→1) 유도: 사용자의 실제 상황 확인 대기 — 두 도구 간 실데이터 의존이 없으면 ②(스키마 의존) 불가라 다른 접근 필요.
- 툴콜 루프 후속 심화 지점 선택 대기(도구 설명 범위 / 루프 상태 전달 / hermes 코드 대조, 또는 병렬·결과 형식).
- 미해결 확인 불가 사항: `EXPERIMENTAL_SKILL_SEARCH`의 검색 구현체 `skillSearch/prefetch.ts`가 내부적으로 임베딩을 쓰는지 (외부 빌드에 파일 자체가 없어 소스 확인 불가).

## Constraints/Rules

- 주장은 소스로 직접 검증 후 답한다 (이 프로젝트 원칙 — `md_group/` 분석 문서 + `src/` 실측, 공식 문서 대조 병행).
- 문서 산출물은 md+html 쌍으로 `/Users/seobi/jinsup_space/CC` 레포 루트에 저장(기존 관례), 모든 섹션에 `파일:line` 근거 표기, 소스로 확인 못한 항목은 별도 표기.
- 사용자에게는 쉬운 비유 중심 재설명 필요(진동벨=Promise, 도서관/장부, 바코드=임베딩 등) — 어려운 설명 반복 시 되물음이 옴.
- 클로드코드 스킬 목록 규칙: 예산 = 윈도우의 1%(총량), 개당 설명 컷(로컬 소스 250자/현행 문서 1,536자), 이름은 항상 포함, 본문은 invoke 시에만 로드, `disable-model-invocation: true`만 완전 제외.
- 메모리 주입 한도: 턴당 5개, 파일당 4KB/200줄, 세션 누적 60KB 스로틀, 스캔 최대 200파일, 셀렉터 출력 256토큰. 스킵 게이트: 기능 off / 한 단어 질문 / 메모리 없음 / 전부 이미 노출.
- hermes 툴콜 규약: assistant(tool_calls) 먼저 append → tool_result를 tool_use_id로 짝지어 반환, 병렬 결과는 한 user 메시지 병합, orphan은 제거(400 방지). 에러도 결과의 한 종류로 모델에 보고.
- 세션 모델 상태: Fable 5 크레딧 부족 발생 → `/model`로 Sonnet 5 → Opus 4.8 전환(기본 저장), `/login` 재수행 완료.

## Pending user asks

- 미해결 없음 — 마지막 질문("Use offset and limit parameters to read specific portions..." / "Please use appropriate tools for binary file analysis" 문자열이 3층 에러 구조 중 어디로 가는가)까지 답변 완료 (②층, LLM 직행, file_tools.py의 큐레이션된 자가복구 안내로 판명).
- 단, assistant가 되물어 사용자 답이 아직 없는 것 2건: ① 도구 1·2가 실제 데이터 의존이 없는 상황인지(순서 유도 방법 선택에 필요), ② 툴콜 루프에서 더 파고들 지점 선택.

## Exact identifiers

- 레포/디렉토리: `/Users/seobi/jinsup_space/CC`, `~/jinsup_space/hermes-agent`, `~/.claude/projects/<프로젝트>/memory/`, `.claude/commands/`, `.claude/skills/`, `md_group/`, `html_group_v2/`
- CC 스킬 예산: `src/tools/SkillTool/prompt.ts` — `SKILL_BUDGET_CONTEXT_PERCENT = 0.01`(:21), `DEFAULT_CHAR_BUDGET = 8_000`(:23), `MAX_LISTING_DESC_CHARS`=250(:29), `getCharBudget`(:31-41), `formatCommandsWithinBudget`(:70-171, :84-88), :178, :211 "All commands are always included (descriptions may be truncated to fit budget)"; env `SLASH_COMMAND_TOOL_CHAR_BUDGET`; 설정 `skillListingBudgetFraction`(예 0.02), `skillListingMaxDescChars`(1,536), `skillOverrides` "name-only"; `/doctor`, `/context`(v2.1.196+); 컴팩션 재부착 스킬당 5,000토큰/합산 25,000토큰
- skill discovery: `EXPERIMENTAL_SKILL_SEARCH`, `getTurnZeroSkillDiscovery`(attachments.ts:803-813), `filterToBundledAndMcp`(attachments.ts:2662-2674), `FILTERED_LISTING_MAX`=30, `stripReinjectedAttachments`(compact.ts:211-223, 주석 :203-206), compact.ts:524-529(~4K 토큰 cache_creation), `skillSearch/prefetch.ts`(외부 빌드 부재, attachments.ts:2753-2755), `skill_listing`, `skill_discovery`, `invoked_skills`, `subagent_spawn`(attachments.ts:2686-2688), postCompactCleanup.ts:63-65
- CC 메모리 회상: `src/memdir/findRelevantMemories.ts`(:39-141, :46-51, :53-58, :105, :108 `max_tokens: 256`, :130 `filter(f => validFilenames.has(f))`, 프롬프트 :18-24), `src/memdir/memoryScan.ts`(:49-55, :57-63, `formatMemoryManifest` :84-95, 이슈 #25372), `src/memdir/memoryAge.ts`(:6 `memoryAgeDays`, :11-13, :23-24), `src/utils/frontmatterParser.ts`(:123 정규식 `/^---\s*\n([\s\S]*?)---\s*\n?/`, `quoteProblematicValues` :85-121, :147-169), `src/utils/attachments.ts` — `MAX_MEMORY_LINES`=200(:269), `MAX_MEMORY_BYTES`=4096(:277), `RELEVANT_MEMORIES_CONFIG`/`MAX_SESSION_BYTES` 60KB(:279-281, prod ~26K토큰 관측), `relevant_memories`(:500), :505-512, :873, `findRelevantMemories` 호출(:2217), "Sonnet spends its 5-slot budget"(:2228-2234), :2230 `!readFileState.has(m.path) && !alreadySurfaced.has(m.path)`, `collectSurfacedMemories`(:2243-2265, :2250-2265), `memoryHeader`(:2324-2332), `startRelevantMemoryPrefetch`(:2361-2381, :2388-2424), `filterDuplicateMemoryAttachments`(:2519-2543); `src/query.ts`(:63, :299, :1587-1602), `settledAt`, `consumedOnIteration`, `hidden_by_first_iteration`, `sideQuery`, `getDefaultSonnetModel()`; manifest 예시 `- [project] repo-shared-two-machines.md (2026-07-11T02:33:12.000Z): ...`; 메모리 타입 `user/feedback/project/reference`; `MEMORY.md`
- CC 커맨드/스킬 통합: `src/commands.ts`(:552-559, :561-579, :569 `!cmd.disableModelInvocation`, :573-578, :574-576 `commands_DEPRECATED`), `disable-model-invocation: true`, `user-invocable: false`, `getSkillToolCommands`, SkillTool 에러 코드 4; 부재 검증 관련 `utils/permissions/bashClassifier.ts`("Stub for external builds - classifier permissions feature is ANT-ONLY"), `classifyBashCommand`, `Tool.ts:551`, `bashSecurity.ts:114`(tree-sitter), git 플래그 `--no-rerank`
- 산출 파일: `/Users/seobi/jinsup_space/CC/스킬예산-로스트인더미들.html`, `/Users/seobi/jinsup_space/CC/메모리-회상-파이프라인-총정리.md`, `/Users/seobi/jinsup_space/CC/메모리-회상-파이프라인-총정리.html`(작성일 표기 2026-07-17), 기존 `md_group/tools_info/tools_detail/SkillTool.md`(:181, :185, :187)
- 공식 문서 URL: `https://code.claude.com/docs/en/slash-commands.md`, `https://code.claude.com/docs/en/skills.md`; WebFetch persisted output: `/Users/seobi/.claude/projects/-Users-seobi-jinsup-space-CC/5d6cda93-807c-44fa-bd16-c40f8c1fa391/tool-results/toolu_01A7SHxhKryo8NTZYecVvC9g.txt`, `.../toolu_012hrYwgmR8YDBPkE5NBiu8M.txt`
- 가격/모델: Sonnet 입력 $3 / 출력 $15 per MTok, 호출당 ~$0.03, 100턴 이론 상한 ~$2.9(현실 <$1), 입력 ~8,500–8,800토큰/호출; `Sonnet 4.6`, `Sonnet 5 (default)`, `Opus 4.8`, `Fable 5`; 슬래시커맨드 `/model`, `/login`, `/usage-credits`
- hermes-agent: `run_agent.py` — `run_conversation`(:10774), `_execute_tool_calls`(:9632), `_invoke_tool`(:9674), `_execute_tool_calls_sequential`(:10165), `_execute_tool_calls_concurrent`(:9784), `_should_parallelize_tool_batch`(:377), `IterationBudget`(:273, 부모 90/서브에이전트 50), `_run_tool`(:9917, :9956-9967 `Error executing tool '{function_name}': {tool_error}`), 인터럽트(:10171-10184), assistant append(:13725), 가드레일 halt(:13742-13750, `_tool_guardrail_halt_decision`), `_NEVER_PARALLEL_TOOLS`; `agent/anthropic_adapter.py`(:1489, :1544-1548 병합, :1568-1600 orphan 제거, "Anthropic rejects these with a 400."); `agent/error_classifier.py`(`classify_api_error`, `FailoverReason`: `rate_limited`, `server_error`, `timeout`, `context_too_long`, `image_too_large`, `oauth_long_context_beta_forbidden`, `llama_cpp_grammar_pattern`); `agent/display.py:804` `_detect_tool_failure`; `tools/file_tools.py`(:553, :557-569, :563 "Use offset and limit to read a smaller range.", :583, :1031 "Cannot read images or binary files — use vision_analyze for images", `_hint` :581-585, 한도 100,000 chars); `prompt_builder.py`(import :152, `build_skills_system_prompt`, `TOOL_USE_ENFORCEMENT_GUIDANCE`); `agent/codex_responses_adapter.py`(:677, :708-709 `parallel_tool_calls` passthrough); `agent/gemini_native_adapter.py`(:361 `mode: "ANY"`, :368 `allowedFunctionNames`)
- API 파라미터: `tool_choice: {disable_parallel_tool_use: true}`, `parallel_tool_calls: false`, `toolConfig.functionCallingConfig.mode`(`AUTO`/`ANY`/`NONE`), `allowedFunctionNames`, `tool_choice: any`/`required`, `tool_use`/`tool_result`/`tool_use_id` vs `role:"tool"`/`tool_call_id`, `stop_reason == "end_turn"`/`"tool_use"`, `is_error: true`

## 단계 3: 이전 컴팩션 요약 재증류 래퍼 — 미적용

이 대화에 이전 컴팩션 요약이 없어 `<previous-compaction-summary>` 래퍼를 삽입하지 않음.

## 단계 4: 부분 요약 병합 — 미적용

히스토리를 여러 파트로 쪼개지 않고 단일 요약으로 처리했으므로 병합 단계 없음.

## 단계 5: split-turn 프리픽스 요약 — 미적용

턴 중간 절단 없이 전체 대화를 대상으로 요약했으므로 해당 없음.

## 단계 6: 품질 가드 재시도 — 미발동

요구 5개 섹션(## Decisions / ## Open TODOs / ## Constraints/Rules / ## Pending user asks / ## Exact identifiers) 모두 존재, 불투명 식별자(경로·라인·상수·URL·수치) 원문 보존 확인 → 감사 통과, 재생성 없음.

## 단계 7: 컴팩션 직후 컨텍스트 리프레시 — 시뮬레이션 범위 외

요약 다음 턴에 시스템 이벤트로 주입되는 단계이며, 본문이 AGENTS.md의 "Session Startup"/"Red Lines" 치환부와 Current time 라인으로 구성됨 — 치환부 무시 규칙에 따라 산출물 생성하지 않음.
