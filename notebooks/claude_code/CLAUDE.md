# `notebooks/claude_code/` — GPT 미니 하네스 규약

> 이 파일은 **`notebooks/claude_code/` 폴더 작업 시에만 온디맨드로 로드**되는 하위 CLAUDE.md 입니다.
> 여기 규약은 **이 폴더에만** 적용됩니다. `notebooks/claude/`(Claude/Anthropic API 기초 노트북) 등 다른 폴더에는 적용하지 마세요 — 다른 폴더는 각자의 컨텍스트(주로 Anthropic SDK)를 따릅니다.

## 이 폴더는 무엇인가

`~/jinsup_space/CC`(= Claude Code, "클로드코드")의 **에이전트 아키텍처를 GPT(OpenAI) 버전으로 재구현한 미니 하네스(mini-harness)** 입니다.

즉, 클로드코드 내부에서 벌어지는 메커니즘(시스템 리마인더 주입, 도구 파이프라인, 하드/소프트 도구 순서 규칙, 배치 스케줄링, ToolSearch·MCP connect/disconnect 의 KV 캐시 영향 등)을 **OpenAI 모델 + 목(mock) 파일시스템**으로 얇게 재현해서, "클로드코드가 왜 이렇게 동작하는가"를 GPT 하네스 위에서 실험·검증하는 것이 목적입니다.

- 분석 원본(정본): `~/jinsup_space/CC` 및 그 `md_group/` 문서
- 여기(`claude_code/`): 그 아키텍처를 **GPT로 옮긴 실험용 미니 재현본**
- 대표 노트북/모듈: `cc_system_reminder`, `cc_tool_pipeline`, `cc_tool_sequence_{hard,soft}_rules`, `cc_tool_batch_scheduling`, `cc_multi_function_calling`, `cc_toolsearch_kv_cache`, `cc_mcp_connect_disconnect_kv_cache`, 공용 `cc_tools.py` / `cc_mock_fs.py`

## 핵심 설계 규약 — GPT 는 "도구를 언제 쓸지"를 **시스템 프롬프트**에 넣는다

이 미니 하네스에서 도구를 붙일 때는 아래 원칙을 지킵니다.

> **적용 범위 — 이 규약은 GPT(OpenAI) 모델 사용에 한정된다.** 근거가 전부 OpenAI GPT-4.1 프롬프팅/함수호출 가이드에서 나온 OpenAI 측 베스트프랙티스이기 때문이다. 오리지널 클로드코드(Anthropic/Claude 모델)는 오히려 **반대로** 간다 — 실제 CC 도구들은 `description` 안에 "언제/언제는 쓰지 마라" 같은 사용 정책을 풍부하게 싣는다. 따라서 이 규약은 "GPT로 재현할 때 도구를 어떻게 설계하는가"에만 적용하고, 오리지널 CC의 설계를 해석·평가할 때는 적용하지 않는다.

- **"언제/왜 이 도구를 쓰는가(사용 정책·조건·순서)"** 는 **시스템(developer) 프롬프트**에 적는다.
  도구의 `description` 필드에 "이럴 땐 쓰고 저럴 땐 쓰지 마라" 같은 정책을 욱여넣지 않는다.
- 도구의 `description` 필드는 **그 도구가 무엇을 하는지 + 각 파라미터가 무엇인지**를 *thorough but concise* 하게만 적는다. 사용 예시가 필요하면 `description` 이 아니라 시스템 프롬프트의 `# Examples` 섹션에 둔다.

### 🔸 예외: 띵킹 툴(thinking tool)

일반 규칙과 달리, **띵킹 툴만은 `description` 안에 사용 지침이 상세히 들어간다.**
즉 "언제/어떻게 생각을 전개할지"에 대한 내용을 (시스템 프롬프트가 아니라) 도구 설명서 자체에 풍부하게 기술하는 것을 허용한다. 나머지 일반 도구는 위의 "정책은 시스템 프롬프트로" 원칙을 따른다.

### 🔸 예외: ToolSearch(`tool_search`)

**ToolSearch도 길게 쓴다.** `tool_search`의 `description`에는 "언제 이 도구를 쓰는가"뿐 아니라 쿼리 형식(`select:이름` / 키워드 / `+필수키워드`)까지 상세히 적는다 — 시스템 프롬프트로 옮기지 않는다.
이유: `cc_toolsearch_kv_cache` · `cc_mcp_connect_disconnect_kv_cache` 두 노트북의 논지 자체가 "시스템 프롬프트(동결 프리픽스)를 안 건드려야 KV 캐시가 산다"이기 때문에, 도구 사용법 지식을 일부러 시스템 프롬프트 밖(도구 `description` · 델타 고지 문구 · 반응형 힌트)에 심는 것이 설계 의도다. 이 두 노트북과 그 레지스트리(`cc_deferred_tools.py`)에서 검색되는 deferred 도구들(agent_search 포함)의 description도 같은 이유로 "언제 쓰는가"를 포함해도 된다.

## 도구 `description` ↔ 시스템 프롬프트 역할 분배 (OpenAI 공식 문서 근거)

| 구분 | 도구 `description` / 파라미터 설명에 넣는 것 | 시스템(developer) 프롬프트에 넣는 것 |
|---|---|---|
| **성격** | 이 도구가 *무엇을 하는가* (정적 사양) | 이 도구를 *언제/왜/어떤 순서로 쓰는가* (동적 정책) |
| **내용** | 함수의 목적, 각 파라미터의 의미·포맷(예: `"City and country e.g. Bogotá, Colombia"`), 출력이 무엇을 뜻하는지 | 언제 호출하고 언제 호출하지 말지, 도구 간 우선순위/순서, 태스크 전반 지시 |
| **분량** | *thorough but relatively concise* — 상세하되 장황하지 않게 | 정책·조건·주의사항은 여기서 충분히 길어도 됨 |
| **예시(examples)** | 넣지 않는다 (설명 필드가 지저분해짐) | 복잡한 도구의 사용 예시는 `# Examples` 섹션에 둔다 |

### 근거가 되는 OpenAI 가이드 원칙

- **도구는 API `tools` 필드로 전달한다** — 시스템 프롬프트에 스키마를 손으로 주입하지 말 것.
  > "We encourage developers to exclusively use the tools field to pass tools, rather than manually injecting tool descriptions into your prompt." — API 파싱 방식이 수동 주입 대비 **SWE-bench Verified pass rate 약 2%↑** 관측.
- **도구 이름은 목적이 드러나게, 설명은 명확·상세하게.**
  > "Developers should name tools clearly to indicate their purpose and add a clear, detailed description in the 'description' field of the tool." / 파라미터도 "lean on good naming and descriptions."
- **예시는 `description` 이 아니라 시스템 프롬프트의 `# Examples` 로.**
  > "…we recommend that you create an `# Examples` section in your system prompt and place the examples there, rather than adding them into the 'description' field, which should remain thorough but relatively concise."
- **"언제 쓸지"는 시스템 프롬프트에서 지시한다.**
  > "Use the system prompt to describe when (and when not) to use each function. Generally, tell the model *exactly* what to do."
- **함수 사양은 '인턴 테스트'를 통과하게** — 주어진 정보만으로 사람이 이해 가능해야 하고, enum·구조로 잘못된 상태를 애초에 못 만들게 설계한다.
- **주의(추론 모델):** 예시 추가가 표준 모델엔 도움되지만, **reasoning 모델에는 성능을 해칠 수 있다**("Adding examples may hurt performance for reasoning models") — 띵킹/추론 계열에는 예시 남발을 피한다.

### 출처
- OpenAI GPT-4.1 Prompting Guide — <https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide>
- OpenAI Function calling 가이드 — <https://developers.openai.com/api/docs/guides/function-calling>
