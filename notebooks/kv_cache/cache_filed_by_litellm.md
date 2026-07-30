# LiteLLM은 모델별로 어떤 키를 쓰는가

---

## 1. LiteLLM 경유 — `response.usage` 키 사용 현황

범례: **●** 값이 들어옴 · **○** 키는 있으나 값이 `None` · **—** 키 자체가 없음

| 키 경로 | `gpt-5.6-*`<br>(luna/sol/terra) | `gpt-5.5` 이하<br>(5.4-mini 등) | `claude-opus-4-8` | `gemini-3.6-flash` |
|---|:---:|:---:|:---:|:---:|
| `prompt_tokens_details.cached_tokens` | ● **read** | ● **read** | ● **read** | ●/○ **read**<br>(미스 시 `None`) |
| `prompt_tokens_details.cache_write_tokens` | ● **write** | — | — | — |
| `prompt_tokens_details.cache_creation_tokens` | — | — | ● **write** | — |
| `prompt_tokens_details.cache_creation_token_details`<br>`.ephemeral_5m_input_tokens` / `.ephemeral_1h_input_tokens` | — | — | ● TTL 분해 | — |
| `cache_read_input_tokens` (최상위) | — | — | ● read **(중복)** | ●/○ read **(중복)** |
| `cache_creation_input_tokens` (최상위) | — | — | ● write **(중복)** | — |

**세 줄 요약**

1. **읽기는 `prompt_tokens_details.cached_tokens` 하나로 통일**됩니다 — 4모델 전부 여기로 옵니다.
2. **쓰기는 이름이 제각각**입니다 — `cache_write_tokens`(GPT 5.6) vs `cache_creation_tokens`(Anthropic). 나머지는 쓰기 개념 자체가 없습니다.
3. **Anthropic·Gemini 는 같은 값을 다른 필드에 중복**으로 줍니다. 

---

## 2. 과금 구조 

| | 읽기 단가 | 쓰기 단가 | 손익분기 |
|---|---|---|---|
| **GPT 5.6+** | 입력가 × 0.1 | **입력가 × 1.25** | 같은 프리픽스 **약 1.3회 이상** 재사용 |
| GPT 5.5 이하 | 입력가 × 0.1 | 무료 | 항상 이득 |
| **Anthropic** | 입력가 × 0.1 | **입력가 × 1.25** (5분)<br>× 2 (1시간) | 같은 프리픽스 **약 1.3회 이상** 재사용 |
| Gemini (암시적) | 입력가 × 0.1 | 무료 | 항상 이득 |

**GPT 5.6 과 Claude 는 회계 구조가 동일합니다** — 턴1 에 전량 write, 이후 read + 증분 write.

### 캐시 입자도 (같은 프리픽스에서 얼마나 잡히나)

| 모델 | 입자도 | 예 |
|---|---|---|
| `gpt-5.6-*` | 거의 전량 | 16,289 / 16,292 (99.98%) |
| `gpt-5.4-mini` | **128 토큰 블록** | 16,128 = 128 × 126 |
| `claude-opus-4-8` | 거의 전량 | 30,572 / 30,614 (99.86%) |
| `gemini-3.6-flash` | **~8,125 토큰 블록** | 8,125 → 16,250 (2배 점프, 중간값 없음) |

### Gemini 는 조건이 따로 있다

20턴 멀티턴 실측 — **7턴째(프리픽스 10,424)부터** 붙기 시작:

```
턴 1~6   prompt  4,748→ 9,477   cached=None      ← 임계 미달
턴 7     prompt 10,424          cached= 8,125    77.9%
턴 8~15  prompt 11,368→18,097   cached= 8,125    71.5%→44.9%   ← 캐시 고정, 분모만 증가
턴 16    prompt 19,059          cached=16,250    85.3%         ← 2블록째
턴 17~20 prompt 20,020→22,912   cached=16,250    70.9%
```

- 문서상 최소 요건은 1024 토큰이지만 **실제로 잡히려면 ~10K** 필요
- 동일 프리픽스 15회 반복 시 **1회차만 미스, 2~15회차 전부 적중**(57.1% 고정) — 조건만 맞으면 안정적
- 호출 간격이 벌어지면 evict (무료 티어 13초 스로틀에서 적중률이 흔들렸던 원인)

---

## 3. 프로바이더별 주의사항

**Anthropic — `cache_control` 을 안 붙이면 캐시가 아예 안 걸립니다.**
멀티턴에서는 **매 턴 마지막 user 블록으로 이동**시켜야 이전 대화까지 캐시가 확장됩니다
(breakpoint 최대 4개라 직전 턴의 것은 제거). 자동이 아닙니다.

**OpenAI — 자동입니다.** `prompt_cache_key` 는 같은 캐시로 라우팅시키는 키 (백엔드는 필수)
TTL 은 5.6 이 `prompt_cache_options.ttl="30m"`(유일값·기본, 최소 30분 보장),
5.5 이하는 `prompt_cache_retention`

**Gemini — 암시적 캐싱은 끌 수 없고 설정 필요 없습니다.**

---

