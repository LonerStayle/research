# openclaw 컴팩션 시뮬레이션 — conv-03

## 단계 1: 사전 메모리 플러시 (silent 턴)

`memory/YYYY-MM-DD.md` 에 APPEND 되는 내용 (기존 항목 무변경 · MEMORY.md/DREAMS.md/SOUL.md/TOOLS.md/AGENTS.md 등 부트스트랩 파일은 읽기 전용 유지 · 타임스탬프 변형 파일명 미사용):

```markdown
## 리서치 세션 — CLAUDE.md 스코프 정리 + 미니 클로드코드 플랜 v2 + tool_eval 5종
- CLAUDE.md 재배치: GPT 미니 하네스 규약 본문은 `notebooks/claude_code/CLAUDE.md`(하위, 온디맨드 로드)로 이동, root `CLAUDE.md`는 8줄 포인터로 슬림화. 규약은 `notebooks/claude_code/` 에만 적용 (`notebooks/claude/` 등 적용 금지).
- GPT 도구 규약: 도구를 "언제 쓸지"는 시스템 프롬프트에, 도구 `description`에는 "무엇을 하는지"만. 예외: 띵킹 툴은 description에 상세. 근거: OpenAI GPT-4.1 Prompting Guide + Function calling 공식 문서.
- `notebooks/claude_code/cc_frontend_plan.md` = v2 로깅 중심 개정판. 미드턴 유저 주입은 `<system-reminder>` 래핑 + "The user sent a new message while you were working..." 문구(isMeta 없이 화면 표시). 캐시(cache_read/cache_creation)는 매 API 경계 1급 로그. 3채널 원칙(⏺/⎿ + 상태색, 모델 전용 채널 ⟦sr⟧ dim). HITL/승인 완전 제거 — 상태머신 3종(IDLE/THINKING/TOOL_RUNNING), 파이프라인 1형식→2값→7실행→8변환, 명령어 /status·/log·/mcp 만. MCP는 시뮬레이션만.
- tool_eval 노트북 5개 완성 (`notebooks/tool_eval/`, 자체완결 ipynb, nbformat v4.5): tool_eval / tool_consolidation_eval / tool_chain_depth_eval / tool_namespace_eval / tool_confusable_eval. 결과는 results/ 에 01_~05_ 접두사(새 실행은 06_부터).
- 실측 결론(gpt-5-nano 한정): 효율(토큰·호출·지연)은 통합/좁은 네임스페이스가 구조적으로 유리(통합 토큰 −46%, 체인깊이 ≈5배, 네임스페이스 3.6배/2.4배). 정확도는 과제 명확+엄격 검증기면 안 갈림(전부 100%). 느슨한 검증기가 N3 과환불(RFND-CHG-2)을 거짓 통과시킨 교훈 → 검증기는 must_include+must_exclude, TRIALS=3.
- 약한 모델 하네스 호환 확인: gpt-4o-mini · gpt-4.1-nano · gpt-3.5-turbo. 능력 순서: gpt-3.5-turbo < gpt-4o-mini ≈ gpt-4.1-nano < gpt-4.1-mini < gpt-5-nano < gpt-5-mini.
- 미결: 약한 모델로 04(네임스페이스)·05(혼동) 재실행 여부 — 사용자 결정 대기.
```

턴 응답: NO_REPLY

## 단계 2: 컴팩션 요약 (customInstructions 적용 산출물)

## Decisions
- 루트 `CLAUDE.md` 생성 후, Anthropic 공식 권장("only matters for one part of the codebase → path-scoped/하위 스코프로 이동")에 따라 본문을 `notebooks/claude_code/CLAUDE.md`(하위, 폴더 파일을 읽을 때만 온디맨드 로드)로 이동하고 root는 레포 소개+폴더별 포인터만 남긴 슬림본(60줄→8줄)으로 교체 — 사용자 선택: "하위 CLAUDE.md로 이동".
- GPT 도구 규약(해당 폴더 한정): 도구를 **언제** 쓸지는 시스템 프롬프트에, `description`에는 무엇을 하는지만; 예외로 띵킹 툴은 description에 사용 지침 상세. 예시는 description이 아니라 시스템 프롬프트 `# Examples`에, 도구는 API `tools` 필드로 전달(수동 주입 대비 SWE-bench +2%). 출처: GPT-4.1 Prompting Guide, Function calling 가이드.
- `cc_frontend_plan.md`를 v2(로깅 중심)로 전면 개정: 로그 = 기법 관측 계층(강의 교보재). §4.4 기법별 로그 이벤트 카탈로그(sr_injected / pipeline_stage / edit_gate_result / partition_computed / request_usage+cache_status·miss_reason / tool_mounted / deferred_delta_flushed), §4.5 매 API 경계 cache HIT/MISS + 컨텍스트 전처리 5단(⑨ 신규·미구현), 오리지널 시각 문법(`⏺` 머리 불릿 / `⎿` 자식 들여쓰기 / 상태색: 무채=실행중·초록=성공·빨강=실패) + 모델 전용 채널 `⟦sr⟧` dim 노출(3채널 원칙).
- 미드턴 유저 주입 정정(초안 오류): `text` 블록+`[작업 중 사용자 추가 입력]` 접두어 → `<system-reminder>` 래핑 + "The user sent a new message while you were working... you MUST address" 문구, isMeta 없이 화면 표시.
- HITL/승인 완전 제거(사용자 추가 지시 — AskUserQuestion 선택 "제거 (자동승인+로그만)"보다 한 단계 더): 상태머신 `AWAITING_APPROVAL` 삭제 → 3종(IDLE/THINKING/TOOL_RUNNING), 툴 파이프라인 6단계(권한 게이트) 제거 → 1형식→2값→7실행→8변환, `permission_decision`·`perm_ask` 이벤트/로그 삭제.
- 명령어 최소화: `/status`·`/log`·`/mcp` 만(전부 읽기/표시 전용). `/stop`·`/queue`·`/queue clear`·`/clear`·`/model` 제거. 큐잉 동작(툴 실행 중 텍스트 입력 → 대화 큐 자동 적재)은 유지.
- MCP는 시뮬레이션만: "등록되었습니다" 고지 + 가짜 도구설명·파라미터·서버설명 전달 + KV캐시 무영향 로그 증명. 실 프로토콜 없음.
- tool_eval 산출 형식/위치: `.py` 폴더가 아니라 주피터 노트북, `notebooks/tool_eval/` (claude_code 밖, 사용자 선택). 잘못 만든 `notebooks/claude_code/tool_eval/` 은 삭제.
- 노트북 5개 완성(전부 nbformat v4.5 검증 + API 미사용 스모크 통과, 모델 `gpt-5-nano`):
  1. `tool_eval.ipynb` — 도구 eval 기본형(orderhub 목 FS, read_file/search_code/list_files, 가이드 4단계). T1 라이브 PASS: 호출 6, 토큰 in 13,795/out 5,245, 41.4s. 로그 발견: 존재하지 않는 영어 함수명(`apply_coupon|calculate_total|...`) 검색 → 0건 낭비 호출(실제 함수는 `calc_total`).
  2. `tool_consolidation_eval.ipynb` — 통합 A/B: `normalize_text`+`hash_all`(각 1파라미터) vs `digest(text, normalize, algo)`(3파라미터). 1차 12루프(따옴표 교란): 분리 67%(4/6)·토큰 6,775 vs 통합 100%·4,138 — 로그로 따옴표 복사 교란 발견. «» 경계+TRIALS=3 재실행 36루프: 둘 다 100%(18/18), 호출 1.72→1.00(−42%), 토큰 6,447→3,473(−46%), 지연 16.4s→13.7s(−16%) → 이 케이스는 통합이 지배적 우위(조합성/재사용만 분리 우위).
  3. `tool_chain_depth_eval.ipynb` — 프리미티브 8(add~negate) vs `calc(expression)` 1, 깊이 2→7(E1~E6). 24루프: 정확도 둘 다 100%(12/12) — 가설(깊을수록 분리 정확도↓) 미확인. 효율: 분리 turns 4.9/호출 4.7/토큰 18,826 vs 통합 1.7/0.7/3,787(≈5배). 통합이 도구 없이 암산한 케이스(E3·E5·E6 호출 0.5~0회) 포착 — 산술은 도구 강제력 약함.
  4. `tool_namespace_eval.ipynb` — 관련 5(find_customer→list_orders→get_charges→issue_refund→notify_customer) + 방해 15(서브에이전트 3개 병렬 작성) = full(20) vs clean(5). 8루프: 느슨 채점 둘 다 100%·오호출 0, 입력토큰 24,510 vs 6,850(≈3.6배), N3(멀티턴)은 52,065 vs 17,097. 사용자 의심("실행이 빨리 끝나 의심") → 트랜스크립트 검증: 실행은 진짜(N3 7콜·8턴), 그러나 full의 N3가 정상 청구 CHG-2까지 환불(RFND-CHG-2, 과환불)했는데 느슨한 검증기가 거짓 통과 → 엄격 재채점 full 3/4(75%) vs clean 4/4(100%) → 검증기 엄격화(과환불 must_exclude)로 노트북 재생성.
  5. `tool_confusable_eval.ipynb` — 정답 5 + 함정 3(`refund_order` 전체환불 / `get_payment_summary` 중복 숨김 / `get_order_history` stale) + 혼동 노이즈 12(서브에이전트 작성). 엄격 검증+TRIALS=3, 24루프: full·clean 둘 다 100%(12/12)·함정호출 0·오호출 0, 입력토큰 12,700 vs 5,315(≈2.4배). 정정: #4의 75%는 네임스페이스 탓이 아니라 프롬프트 애매함("중복분을 모두 환불") 아티팩트.
- 5실험 관통 결론: 효율(토큰·호출·지연)은 항상 좁은/통합 도구가 구조적 우위; gpt-5-nano에선 과제가 명확하고 도구 설명이 정직하면 정확도·오호출이 안 갈림(전부 100%); 정확도를 실제로 가르려면 더 약한 모델·정말 애매한 과제·설명이 거짓말하는 함정이 필요.
- eval 방법론 채택: 검증기는 처음부터 엄격(must_include+must_exclude, 과환불·함정 흔적 검출), TRIALS=3 반복, 교란 통제(따옴표 대신 «» 경계 + 시스템 프롬프트에 경계 명시), 집계 숫자와 원본 로그(JSONL) 병행 판독.
- `results/` 파일명: 오래된 순 `01_`~`05_` 접두사(jsonl·summary 쌍 동일 번호), 이미 번호 붙은 파일은 스킵, 새 실행은 `06_`부터.
- 모델: 전 실행 `gpt-5-nano`(셋업 셀 `MODEL = "gpt-5-nano"`, 레포 관례 기본값). 약한 모델 호환 확인: `gpt-4o-mini`·`gpt-4.1-nano`·`gpt-3.5-turbo` 셋 다 Responses API 하네스에서 정상 툴콜(add 1콜). 능력 순서: gpt-3.5-turbo < gpt-4o-mini ≈ gpt-4.1-nano < gpt-4.1-mini < gpt-5-nano < gpt-5-mini (gpt-5-mini는 gpt-5-nano보다 강함 — divergence 목적엔 반대 방향).

## Open TODOs
- (대기) 약한 모델(gpt-4o-mini 또는 gpt-4.1-nano/gpt-3.5-turbo)로 04(네임스페이스)·05(혼동) A/B 재실행 — 마지막 턴 AskUserQuestion 진행 중 대화 절단, 사용자 응답 없음.
- (제안만) 엄격 검증기 반영된 #4를 TRIALS=3으로 재실행해 75% vs 100% divergence가 진짜인지 재검증.
- (제안만) 5개 실험 결과 1장 요약(정확도·토큰·오호출 비교표 + 결론).
- (제안만, 플랜 v2 마무리 시점) §4.4 카탈로그를 노트북 실제 심볼(`READ_FILE_STATE`, `FROZEN_TOOLS` 등)에 1:1 매핑, 또는 특정 기법 하나의 로그 렌더러 예시 코드.
- 미니 클로드코드 구현 자체(M1~M4)와 §9 판단거리(sr_injected 화면 접기 수준, autocompact 9섹션 요약 스키마 유지 여부, miss_reason의 server_noise "추정" 표기)는 미착수.
- 새 results 파일 생기면 `06_`부터 번호 이어붙이기.

## Constraints/Rules
- GPT 미니 하네스 규약은 `notebooks/claude_code/` 에만 적용 — `notebooks/claude/`(Anthropic SDK 기초) 등 다른 폴더 적용 금지.
- 미니 CC는 강의용: TUI 프레임워크 금지(표준 `print`/`sys.stdin`/ANSI만). 비목표: 인터랙티브 승인/HITL, 중단(`/stop`), 툴 파이프라인 6단계(권한 게이트), Ctrl+C 세분화, 스킬 시스템, 로그 회전, 플랫폼 분기.
- MCP는 실 프로토콜 없이 시뮬레이션만(등록 고지 + 가짜 도구설명·파라미터·서버설명).
- 실제 LLM 실행(OpenAI 크레딧 소모) 전에는 사용자 확인 후 진행, 긴 실행은 백그라운드로 돌리고 완료 알림 후 보고.
- `.env` 키(OPENAI_API_KEY/ANTHROPIC_API_KEY)는 커밋 금지(.gitignore 처리). 노트북 LLM 셀은 `if client:` 가드로 키 없으면 자동 스킵.
- 노트북은 자체완결(별도 `.py` 의존 없음), 목 FS는 `claude_code/cc_mock_fs` 자동 경로 탐색 import, nbformat 4.5 규격(셀 `id` 필수).
- eval 검증기는 엄격(must_include+must_exclude), TRIALS=3, 교란 통제(«» 경계), 집계+원본 로그 병행 판독.
- results jsonl·summary 쌍은 같은 번호 공유; 이미 번호 붙은 파일은 건너뜀.

## Pending user asks
- 약한 모델로 04(네임스페이스)·05(혼동) A/B 재실행 여부 결정 — 어시스턴트가 AskUserQuestion 호출(1차 InputValidationError 후 재시도) 중 대화가 절단되어 **미응답** 상태. 후속 세션에서 이 선택지를 다시 물어야 함.

## Exact identifiers
- 리포/문서: `/Users/seobi/jinsup_space/research/CLAUDE.md`, `/Users/seobi/jinsup_space/research/notebooks/claude_code/CLAUDE.md`, `notebooks/claude_code/cc_frontend_plan.md`, `notebooks/claude_code/cc_tools.py`(761줄), `notebooks/claude_code/cc_mock_fs.py`, `~/jinsup_space/CC`, `~/Desktop/도구-eval-가이드.md`, 삭제됨: `notebooks/claude_code/tool_eval/`
- 노트북: `notebooks/tool_eval/tool_eval.ipynb`, `notebooks/tool_eval/tool_consolidation_eval.ipynb`, `notebooks/tool_eval/tool_chain_depth_eval.ipynb`, `notebooks/tool_eval/tool_namespace_eval.ipynb`, `notebooks/tool_eval/tool_confusable_eval.ipynb`
- 결과 파일(`notebooks/tool_eval/results/`): `20260725-174359.jsonl`, `01_consolidation-full-20260725-184408.jsonl`, `02_consolidation-clean-20260725-190128.jsonl`(+`.summary.txt`), `03_chaindepth-…191951.jsonl`(+summary), `04_namespace-20260725-194142.jsonl`(+summary), `05_confusable-…200204.jsonl`(+summary), `results/consolidation-clean-20260725-190128.jsonl`, `results/namespace-20260725-194142.jsonl`
- 스크래치(`/private/tmp/claude-501/-Users-seobi-jinsup-space-research/fb908921-b1b4-488e-93c5-eed88108ed8d/scratchpad/`): `original_cc_ui.md`, `techniques_extract.md`, `build_nb.py`, `build_nb2.py`, `build_nb3.py`, `build_nb4.py`, `build_nb5.py`, `run_clean.py`, `run_depth.py`, `run_ns.py`, `run_conf.py`
- 백그라운드 작업 ID: `b4bwwb1oh`(consolidation clean 36루프), `bnb6rb7kz`(체인깊이 24루프), `bq6nuouya`(네임스페이스 8루프), `b3rhn9doa`(혼동 24루프)
- 서브에이전트 작업 ID: `a9e416ab852e44f87`(기법 추출), `a42cff3c22dfee6b2`(오리지널 CC UI 조사), `ad4be00bd6b1b8a5d`(D1), `a0e2561e65a5be9a2`(D2), `a7c4ebaf9860074cd`(D3), `a67744245652b55ea`(혼동 12)
- tool_use ID: `toolu_013JKRX8zRZ5rvD12ZpdLbcj`, `toolu_01LQpwJukDQ8ckBfjuKt1XBA`, `toolu_018yBPTyx7mFs1BSmzZYHHQB`, `toolu_011yB8YiP1GvZnhxapojnYeN`, `toolu_01LyUa4Ymzj4Y9Z7Sv1y84WB`, `toolu_01Jr6pGgsXTxBB4Gi3LvAEBJ`, `toolu_01VU2ZYiyjsBn7G5tr6S1fcB`, `toolu_01MVhLiVo5cN83kW699cCF74`, `toolu_01FUH5wdCTJu6yh6LX3zAcz2`
- 모델/버전: `gpt-5-nano`, `gpt-4o-mini`, `gpt-4.1-nano`, `gpt-3.5-turbo`, `gpt-4.1-mini`, `gpt-5-mini`, `chatgpt-image-latest`, `ft:gpt-3.5-turbo-1106:personal::9b0AEDp5:ckpt-step-80`(외 ft 계열: `9b0AEEWg:ckpt-step-90`, `9b0AEwEz`, `9b10dRbY:ckpt-step-100`, `9b10eCzN:c…`잘림), `openai 2.47.0`, Python `3.12.11`, nbformat `v4.5`
- 도구명 — (기본형) `read_file`·`search_code`·`list_files` / (통합 A/B) `normalize_text`·`hash_all`·`digest` / (체인깊이) `add`·`subtract`·`multiply`·`divide`·`power`·`sqrt`·`modulo`·`negate`·`calc` / (관련 5) `find_customer`·`list_orders`·`get_charges`·`issue_refund`·`notify_customer` / (방해 D1) `get_weather_forecast`·`search_flights`·`convert_currency`·`lookup_dns_records`·`translate_text` / (방해 D2) `analyze_food_nutrition`·`generate_chord_progression`·`get_soil_moisture_reading`·`get_moon_phase`·`calculate_income_tax` / (방해 D3 — 이름 일부만 확인: `suggest_ingredient_substitute`, `git_blame_lin…`잘림; 요리·git·법률·단위·운동 도메인 5개) / (혼동 12) `search_users`·`get_account`·`get_customer_profile`·`list_invoices`·`list_transactions`·`fetch_payments`·`cancel_charge`·`reverse_transaction`·`notify_user`·`send_email`·`create_ticket`·`get_shipping_status` / (함정 3) `refund_order`·`get_payment_summary`·`get_order_history`
- 데이터/과제 ID: orderhub(40파일, FastAPI+SQLAlchemy), `ORDER-482`, `ORDER-517`, 쿠폰 `WELCOME5`, `CUST-1`, `ORD-1001`, `ORD-1002`, `CHG-2`·`CHG-3`·`CHG-4`, `RFND-CHG-2`·`RFND-CHG-3`·`RFND-CHG-4`, `RO-ORD-1002`; 과제 `T1-coupon-shipping`·`T2-duplicate-coupon`, `C1`~`C6`, `E1`~`E6`(깊이 2~7, 정답 3005·12981·24796·-110·3775·7211), `N1`(57000)·`N2`(CHG-3,CHG-4)·`N3`(RFND-CHG-3/4 워크플로)·`N4`(30000)
- 해시/식 리터럴: `sha256('hello world') = b94d27b9934d3e08…`(잘림), `calc_expr('(312*47)-(5049/3)') = 12981`, 오답 md5 `ca606db0547239392f66cac3f5311ec7`, 기대 md5 `41995c70055e…`(잘림), sha1 `aad55d4eca76856c765569805ca20f32a3d2e2c…`(잘림)
- URL: `https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide`, `https://developers.openai.com/api/docs/guides/function-calling`, `https://code.claude.com/docs/en/memory`, `https://code.claude.com/docs/llms.txt`, `https://www.anthropic.com/engineering/claude-code-best-practices`, `https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c`, `https://www.firecrawl.dev/blog/claude-code-token-efficiency`
- CC 소스 근거(플랜 v2 인용): `figures.ts:4`, `MessageResponse.tsx:22`, `AssistantTextMessage.tsx:232`, `AssistantToolUseMessage.tsx:186,200,210,228`, `ToolUseLoader.tsx:19`, `SystemTextMessage.tsx:103,378,387`, `transcriptSearch.ts:117`, `queryHelpers.ts:432`, `utils/messages.ts:5510`(+`:5504,5506`), `messages.ts:4530`, `api.ts:449-474`, `cost-tracker.ts`, `claude.ts:1207`, `claude.ts:3127`, `promptCacheBreakDetection.ts`, `microCompact.ts`, `query.ts:364-463`, `query.ts:1569`, `query.ts:1213,1314`, `CompactBoundaryMessage.tsx`, `useCanUseTool.tsx:32`, `interactiveHandler.ts:57`, `useQueueProcessor.ts:48-60`
- 실행 타임스탬프: `20260725-174359`, `20260725-184408`, `20260725-190128`, `20260725-194142` (05 confusable 은 `…200204` 로만 표기됨)

## 단계 3~7: 미적용 (조건 불충족)
- 단계 3(이전 요약 재증류 래퍼): 이 대화에는 이전 컴팩션 요약이 없음 → 미적용.
- 단계 4(부분 요약 병합): 단일 파트로 요약 → 병합 불필요.
- 단계 5(split-turn 프리픽스 요약): 프리픽스 전용 요약 상황 아님 → 미적용.
- 단계 6(품질 가드 재시도): 요약 감사 실패 발생 없음 → 미적용.
- 단계 7(컴팩션 직후 컨텍스트 리프레시): 대화 내용에서 생성되는 산출물이 아닌 고정 주입문(AGENTS.md 치환부 포함)이므로 시뮬레이션 생략.
