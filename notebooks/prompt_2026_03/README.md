# 프롬프트 엔지니어링 테스트 노트북

강수진 X 테디노트 「2026 프롬프트 엔지니어링」 40개 팁 + 스크래치패드 기법을,
실제 `gpt-5-nano`로 **before/after를 돌려보며 검증**하는 노트북 모음입니다.

## 실행 방법

```bash
# 프로젝트 루트에서
uv run jupyter lab
```

- `.env`에 `OPENAI_API_KEY`가 있어야 합니다 (이미 설정됨).
- 각 노트북 **첫 코드 셀**이 프로젝트 루트를 자동 탐색해 `research_utils`를 로드합니다.
  위에서부터 순서대로 Run 하면 됩니다.
- 모든 셀은 **미실행 상태**로 배포됩니다 — 직접 Run 할 때만 API가 호출됩니다.

## 공용 헬퍼 (`research_utils.py`)

| 함수 | 용도 |
|---|---|
| `ask(prompt, system=None, **kw)` | 프롬프트 → 텍스트 |
| `ask_meta(...)` | 텍스트 + 토큰/지연(latency) 실측 (KPI용) |
| `ask_json(...)` | JSON 강제 출력 후 파싱 |
| `chat(messages, ...)` | Chat Completions 얇은 래퍼 |
| `keyword_hits(text, keywords)` | 정답지 키워드 채점 |
| `compare(la, ta, lb, tb)` | before/after 나란히 출력 |

**`gpt-5-nano` 실측 제약**: `temperature` 변경 불가(1 고정) · `max_tokens` 미지원(`max_completion_tokens` 사용) · `reasoning_effort`/`verbosity` 지원 · 추론 예산이 작으면 본문이 빈 문자열이 될 수 있음.

## 노트북 목록

| 노트북 | 주제 | 다루는 팁 |
|---|---|---|
| `00_openai_test` | 연결 테스트 (스타터) | — |
| `01_prompt_structure_ordering` | 프롬프트 구조·순서 | 1, 10, 11, 33 |
| `02_contract_xml_control` | 계약(Contract)·XML 태그 제어 | 7, 19, 20, 25, 35 |
| `03_fewshot_and_bias` | Few-shot 예시와 편향 | 8, 9, 23, 26 |
| `04_cot_strategies` | CoT(사고사슬) 전략 | 14, 15, 21, 30, 39 |
| `05_reasoning_output_control` | 추론·출력 형식 제어 | 13, 16, 17, 18 |
| `06_json_structured_output` | JSON 구조화 출력 | 6, 34, 36, 40 |
| `07_rag_long_context` | RAG·긴 문맥 | 2, 12, 32, 38 |
| `08_agent_orchestration_eval` | 오케스트레이션·평가·KPI | 3, 4, 5, 22, 24, 27, 28, 29, 31, 37 |
| `09_scratchpad_and_react` | 스크래치패드 & ReAct 비교 | (별도 심화) |

> 40개 팁 전부 각 1회씩 배정되어 있습니다. `09`는 스크래치패드 기법을 ReAct와 비교하며
> 별도 심화로 다룹니다 (직답 vs 스크래치패드 정확도, 레이턴시/토큰 트레이드오프, Thinking Tool 패턴, 검토 루프).
