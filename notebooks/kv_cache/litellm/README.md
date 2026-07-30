# LiteLLM 캐시 필드 확인

`proj-in4u-bxg2.0-api` 가 쓰는 **LiteLLM 1.83.7** 경유로 4모델을 3턴 멀티턴 호출해서,
캐시 **write/read 가 어떤 필드로 표시되는지** 실측하는 노트북입니다.

## 왜

그 프로젝트의 `LiteLLMProvider` (`src/bxg/adapters/outbound/llm_provider/litellm_provider.py`) 는
응답 usage 에서 `prompt_tokens` / `completion_tokens` / `reasoning_tokens` **세 개만** 읽습니다.
**캐시 토큰은 전혀 보지 않아서**, 캐시 읽기(입력가의 10%)가 정가로 기록되고 GPT 5.6 의 쓰기(125%)는 누락됩니다.
계측을 추가하려면 먼저 필드 구성을 알아야 해서 만든 노트북입니다.

## 실행

이 노트북은 **전용 venv 커널**을 씁니다. 리서치 레포 본 환경은 `openai>=2.45` 인데
`litellm==1.83.7` 은 `openai==2.30.0` 을 핀해서 충돌하기 때문입니다.

```bash
# (최초 1회) 전용 venv + 커널 등록 — 이미 돼 있으면 건너뛰세요
uv venv .venv-litellm --python 3.12
uv pip install --python .venv-litellm "litellm==1.83.7" ipykernel python-dotenv
.venv-litellm/bin/python -m ipykernel install --user \
  --name litellm-1837 --display-name "Python (litellm 1.83.7)"

# 실행
uv run jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=litellm-1837 \
  notebooks/kv_cache/litellm/litellm_cache_fields.ipynb
```

Jupyter Lab 에서 열 때는 커널을 **"Python (litellm 1.83.7)"** 로 선택하세요.

### Gemini 장기 실험 (선택)

아래 아래쪽 "Gemini 장기 실험" 결과를 재현하는 스크립트입니다. 35회 호출이라 노트북에는 넣지 않았습니다.

```bash
.venv-litellm/bin/python notebooks/kv_cache/litellm/gemini_long_probe.py
```

A) 20턴 멀티턴에서 몇 턴째부터 캐시가 붙는지 · B) 동일 프리픽스 15회 반복 시 유지되는지를 봅니다.

`.env` 에 필요한 키: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`
(LiteLLM 의 `gemini/` 경로는 `GEMINI_API_KEY` 를 보므로 노트북이 자동으로 매핑합니다)

## 실측 결과 — LiteLLM 이 캐시를 어디에 담아주나

| 모델 | 읽기(read) | 쓰기(write) |
|---|---|---|
| `openai/gpt-5.6-luna` | `prompt_tokens_details.cached_tokens` | `prompt_tokens_details.cache_write_tokens` |
| `openai/gpt-5.4-mini` | `prompt_tokens_details.cached_tokens` | **필드 자체가 없음** |
| `anthropic/claude-opus-4-8` | `prompt_tokens_details.cached_tokens`<br>+ 최상위 `cache_read_input_tokens` | `prompt_tokens_details.cache_creation_tokens`<br>+ 최상위 `cache_creation_input_tokens` |
| `gemini/gemini-3.6-flash` | `prompt_tokens_details.cached_tokens`<br>+ 최상위 `cache_read_input_tokens`<br>(**미스 시 둘 다 `None`**) | 없음 (쓰기 개념 없음) |

## 3턴 멀티턴 실측 결과

```
GPT 5.6 luna     턴1: prompt= 5,943  read=     0  write= 5,940   적중  0.0%
                 턴2: prompt= 6,574  read= 5,940  write=   631   적중 90.4%
                 턴3: prompt= 7,228  read= 6,571  write=   654   적중 90.9%

GPT 5.4 mini     턴1: prompt= 5,943  read=     0  write=     -   적중  0.0%
                 턴2: prompt= 6,602  read= 5,376  write=     -   적중 81.4%
                 턴3: prompt= 7,253  read= 6,400  write=     -   적중 88.2%

Claude Opus 4.8  턴1: prompt=10,022  read=     0  write=10,020   적중  0.0%
                 턴2: prompt=11,097  read=10,020  write= 1,075   적중 90.3%
                 턴3: prompt=12,156  read=11,095  write= 1,059   적중 91.3%

Gemini 3.6 flash 턴1~3: read=0  ← 3턴 내내 캐시가 전혀 안 걸림
```

**읽어야 할 것**

- **GPT 5.6 은 Anthropic 과 정확히 같은 패턴**입니다. 턴1 에 전량 write → 이후 턴은 **이전 턴을 read 하고 새로 늘어난 만큼만 write**(631 / 654 토큰). 증분 캐싱이 제대로 도는 모습입니다.
- **GPT 5.4 mini 는 write 가 아예 없고** read 만 계단식으로 늘어납니다(5,376 → 6,400 — 128 의 배수). 쓰기가 무료라 리포트할 게 없는 것입니다.
- **Gemini 는 3턴 내내 read=0** 입니다. 다만 이유는 "불안정해서"가 아니라 **프리픽스가 아직 작아서** 입니다 — 아래 장기 실험에서 밝혀졌습니다.
- 턴1 의 read=0 은 어느 모델이든 정상입니다 — 캐시에 아직 아무것도 없습니다.

### Gemini 장기 실험 — 캐시는 ~8,125 토큰 **블록 단위**로 잡힌다

3턴으로는 안 잡혀서 20턴까지 늘려봤습니다.

```
턴 1~6   prompt  4,748→ 9,477   cached=None       ← 미적중
턴 7     prompt 10,424          cached= 8,125     77.9%   ← 첫 적중
턴 8~15  prompt 11,368→18,097   cached= 8,125     71.5%→44.9%
턴 16    prompt 19,059          cached=16,250     85.3%   ← 정확히 2배로 점프
턴 17~20 prompt 20,020→22,912   cached=16,250     81.2%→70.9%
```

- **캐시는 ~8,125 토큰 단위로만 늘어납니다.** 프리픽스가 커져도 캐시량은 고정돼 있다가 다음 블록 경계에서 한 계단 점프합니다(8,125 → 16,250).
- 7~15턴에서 적중률이 떨어지는 건 캐시가 줄어서가 아니라 **분모(prompt)만 커졌기 때문**입니다.
- GPT 5.4-mini 는 128토큰, GPT 5.6·Claude 는 거의 전량 캐싱인 것과 비교하면 **입자도가 압도적으로 거칩니다.**
- 문서상 최소 요건은 1024 토큰이지만, **실제로 잡히려면 ~10K 는 되어야 합니다.**

### 안정성 — 조건만 맞으면 안정적이다

같은 14K 프리픽스를 15회 연속 반복:

```
1회차:    cached=None
2~15회차: cached=8,173  적중 57.1%   ← 14/15회, 흔들림 없음
```

`gemini36/` 폴더의 단발 노트북에서 `[0%, 84%, 0%, 0%]` 처럼 들쭉날쭉했던 것은
**무료 티어 스로틀로 호출 간격이 13초씩 벌어졌던 탓**으로 보입니다.
간격을 두지 않고 연속 호출하면 1회 워밍업 후 안정적으로 적중합니다.

**정리**: Gemini 암시적 캐싱은 "보장되지 않아 불안정한 것"이라기보다
**① 프리픽스가 ~10K 이상이어야 하고 ② 8K 단위로만 늘고 ③ 호출 간격이 벌어지면 evict 된다** 로 이해하는 게 정확합니다.
컨텍스트가 작은 에이전트 턴에서는 기대하기 어렵고, 컨텍스트가 크고 연속 호출되면 잘 걸립니다.

### Gemini 히트 샘플은 따로 확보해야 한다 (노트북 ③-b 셀)

멀티턴만으로는 Gemini 캐시 필드에 값이 들어온 모습을 볼 수 없어서, **같은 큰 프리픽스(~14K)를 반복 호출**하는 셀을 따로 뒀습니다.

```
[콜드 상태 — 처음 돌릴 때]
1~3회차: details.cached_tokens=None  top.cache_read_input_tokens=None
4~6회차: details.cached_tokens=8173  top.cache_read_input_tokens=8173   적중 57.1%

[웜 상태 — 직전에 같은 프리픽스를 쓴 뒤 다시 돌릴 때]
1~6회차: details.cached_tokens=8173  top.cache_read_input_tokens=8173   적중 57.1%
```

- **적중 시작 회차는 실행할 때마다 다릅니다.** 콜드에서는 4회차쯤부터, 캐시가 이미 데워져 있으면 1회차부터 걸립니다. 암시적 캐싱은 보장되지 않으므로 이 셀 결과는 재실행마다 달라지는 게 정상입니다.
- 히트하면 **Gemini 도 최상위 `cache_read_input_tokens` 에 같은 값을 중복 제공**합니다. Anthropic 과 마찬가지로 둘 다 더하면 이중 계산입니다.
- 적중률은 **57%** 로 부분 캐싱입니다 — 프리픽스 전량이 잡히지 않습니다.

**핵심 3가지**

1. **읽기는 통일, 쓰기는 아님.** LiteLLM 은 읽기를 `cached_tokens` 로 정규화하지만, 쓰기는 프로바이더 이름을 그대로 둡니다(`cache_write_tokens` vs `cache_creation_tokens`).
2. **"값 없음"이 세 형태.** 키 부재(`gpt-5.4-mini`) / `None`(Gemini 미스) / `0`(5.6 웜). **Gemini 의 `None` 을 그냥 더하면 `TypeError`** 입니다.
3. **Anthropic 은 같은 값을 두 군데에 줍니다.** 최상위와 `prompt_tokens_details` 양쪽 — 둘 다 더하면 이중 계산입니다.

## 프로젝트 반영 시 검토할 것

- **`_extract_cache_tokens` 헬퍼 추가** — 노트북 ④ 셀에 기존 `_usage_int` 스타일로 작성해 뒀습니다.
- **캐시 단가 컬럼** — `llm_models` 에는 `input_price_per_million` / `output_price_per_million` 만 있습니다. `litellm.model_cost` 에 `cache_read_input_token_cost` / `cache_creation_input_token_cost` 가 이미 있으므로 `model_catalog.py` 의 `_litellm_pricing` 을 확장하면 자동으로 채울 수 있습니다.
- **⚠️ Anthropic 멀티턴 캐싱이 안 걸리고 있을 가능성** — `cache_control` 을 매 턴 마지막 user 블록으로 옮겨야 이전 대화까지 캐시가 확장되는데, 현재 `_msg_to_dict` / `_render_content` 는 `cache_control` 을 붙이지 않습니다. Bedrock/Vertex 경유 Claude 도 동일하며 비용에 직접 영향을 줍니다.

## 참고 — 이 노트북이 직접 프로바이더를 쓰는 이유

`proj-in4u-bxg2.0-api` 는 운영에서 직접 API 를 쓰지 않고 전부 엔터프라이즈 클라우드(`azure_ai/`, `bedrock/`, `vertex_ai/`, `databricks/`)를 경유합니다. 다만 **캐시 필드 구성은 LiteLLM 이 어느 백엔드 응답을 옮겨 담느냐에 따라 정해지므로**, 모델 계열(OpenAI / Anthropic / Gemini)이 같으면 필드도 같습니다. 그래서 키만 있으면 되는 직접 경로로 확인했습니다.

경로별로 값이 다를 수 있는 부분은 **캐시가 실제로 걸리는지 여부**입니다(예: Bedrock Claude 는 리전·모델별로 prompt caching 지원이 갈립니다). 운영 경로에서 최종 확인이 필요하면 노트북의 `MODELS` 를 `bedrock/...` / `azure_ai/...` 로 바꾸고 해당 자격증명을 넣으면 그대로 돌아갑니다.
