# 멀티 채팅방 에이전트 서비스 — 대화 메모리 아키텍처 설계

> 대상: 멀티 채팅방 구조의 AI 에이전트 채팅 서비스 (사용자가 여러 방을 만들고 각 방에서 에이전트와 대화)
> 스택: **Python** 백엔드 · **PostgreSQL**(pgvector + full-text)
> 근거: 4개 하네스(codex/claude-code/grok/openclaw) 메모리 전략 분석 + 자체 컴팩션 평가 실험([report_r2.md](results/report_r2.md))
> 작성: 2026-08-05

---

## 0. 한 줄 결론

**claude-code의 "요약 = 인덱스 + 원본 포인터" 철학**을 베이스로, 요약 포맷은 **openclaw의 고정 5섹션 러닝 요약**으로, 복구 채널은 **grok식 하이브리드 검색(pgvector 벡터 + Postgres full-text)** 으로 구현한다. 이를 **방 내부 컨텍스트(Layer A) + 사용자 장기메모리(Layer B)** 2계층으로 분리한다.

핵심 판단: **실험 1위(openclaw)를 그대로 베끼지 않는다.** 실험이 측정하지 못한 "원본 복구 채널"이 이 서비스에선 Postgres 덕분에 공짜로 존재하기 때문에, 순위의 의미 자체가 달라진다.

---

## 1. 왜 실험 순위를 그대로 따르면 안 되는가 (가장 중요)

자체 평가([report_r2.md](results/report_r2.md)) 결과는 다음과 같았다:

| 기법 | 회상 | 압축률 | 조건 |
|---|---|---|---|
| openclaw | 0.614 | 3.8% | **"최종 요약본만 남고 원본 복구 불가"** |
| codex | 0.568 | 7.0% | (최악 조건) |
| grok | 0.295 | 2.5% | |
| claude-code | 0.182 | 3.5% | |

**이 점수는 "요약본만으로 버티는 능력" 순위지, "실제 서비스에서의 최종 정확도" 순위가 아니다.** 이 서비스에는 Postgres가 있으므로:

- **전체 대화 원본이 `messages` 테이블에 영구 보존** → claude-code의 "요약은 손실 압축이 아니라 원본 포인터" 설계가 실험에선 봉쇄됐지만 여기선 1급 기능으로 자연스럽게 성립.
- **pgvector + full-text로 grok의 벡터+BM25 하이브리드 검색이 그대로 재현** → grok의 초반 소실(위치별 회상 0.062)은 검색을 껐을 때 값이며, 켜면 메워진다.

### 결론적 함의
- **claude-code 0.182는 이 서비스와 무관하다.** 설계의 핵심(원본 복구)을 끈 조건의 값. 오히려 그 철학이 Postgres 환경의 정답에 가깝다.
- **grok 0.295도 과소평가다.** 검색 채널 = pgvector+tsvector이므로 이 서비스에선 살아난다.
- **openclaw가 1위인 건 "요약본만으로 버티기" 순위** → openclaw의 **요약 구조만** 빌려오고(가장 작고 안정적, 원본의 3.8%·효율 16.2), 전체 승부는 검색으로 낸다.

> ⚠️ 실험 자체의 편향(증분 체인이 openclaw 설계와 정렬, claude-code 복구채널 삭제, 프로브 재편)은 [실험 한계 및 교정 계획](#부록-실험의-편향-요약)에 정리. 이 수치는 "방향성"으로만 사용하고, 실서비스는 자체 프로브셋으로 A/B 검증할 것.

---

## 2. 2계층 메모리 설계

방마다 독립 세션이므로 메모리를 **두 계층으로 명확히 분리**하고, **컨텍스트 예산도 따로** 잡는다(상호 오염/경쟁 금지).

### Layer A — 방 내부 컨텍스트 (room-scoped, 필수)
- **목적**: 한 방 안의 장기 세션 연속성. "이 방에서 우리가 뭘 하고 있었나."
- **구성**: 방별 러닝 요약(1행) + 최근 N턴 원문 + 이 방 원본에서 검색된 관련 청크(RAG).
- 이것이 곧 "컴팩션"에 해당.

### Layer B — 사용자 장기메모리 (cross-session, 권장)
- **목적**: 방을 가로지르는 사용자 프로필/선호. "이 사용자는 Python 백엔드 개발자, 존댓말 선호, 프로젝트 X 진행 중."
- **구성**: `user_memories` 테이블. 세션 시작 시 부트스트랩 주입 + 온디맨드 검색.
- **도입 판단**:
  - 방들이 완전히 독립 주제 + 크로스룸 개인화 불필요 → **Layer A만**.
  - "AI가 나를 기억하는" SaaS 경험 원함(대부분의 챗 SaaS) → **Layer A + 최소 Layer B(선호/프로필만)**로 시작 후 확장.

> **함정 방지**: 두 계층을 절대 한 테이블/한 주입 블록에 섞지 말 것. 방 A의 대화가 Layer B로 새면 방 B에 엉뚱하게 튀어나온다. Layer B 승격은 명시적 추출/통합 패스(openclaw dream, grok autoDream 아이디어)를 거치게 한다.

---

## 3. 추천 근거

1. **복구 채널이 공짜 → 요약이 완벽할 필요 없음.** 실험에서 claude-code가 0.965→0.182로 떨어진 원인은 "요약의 요약"에서 초반 정보 증발(위치별 회상 0.000). Postgres에 원본이 있으면 요약이 뭘 흘려도 검색으로 되찾으므로 **가장 치명적이던 실패 모드가 사라진다.** 요약은 저비용 인덱스로만.

2. **요약 레이어는 openclaw 구조가 최선.** 11회 반복 컴팩션에서 회상 1위(0.614)이면서 최종 요약이 원본의 **3.8%로 가장 작다**(효율 16.2, 2위 codex의 2배). 고정 5섹션이 재증류에 안정적이고 초반 정보(0.375)를 가장 잘 지킨다. codex는 정확하나 요약 7%로 비대(토큰 낭비), claude-code의 8섹션 전량 재나열은 반복 시 취약.

3. **grok 하이브리드 검색이 lost-in-the-middle을 직접 때린다.** 실험 최대 관전 포인트는 위치 효과(모든 기법이 후반 > 초반). 요약만으론 오래된 정보가 소실되지만 검색은 위치 무관하게 관련 청크를 끌어온다. pgvector(HNSW) + tsvector(GIN)로 네이티브 구현, 별도 벡터DB 불필요.

4. **안전성·한국어는 4기법 공통**(환각 0, 언어 ko 유지). 차별점은 "회상 정확도 × 비용"뿐이고 위 조합이 이긴다.

---

## 4. PostgreSQL 스키마

```sql
-- 멀티테넌시 루트
CREATE TABLE rooms (
  id          bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id     bigint NOT NULL,          -- 테넌트
  title       text,
  created_at  timestamptz DEFAULT now()
);

-- 원본 로그 (영구 보존 = 복구 채널의 근거 = claude-code의 transcriptPath 역할)
CREATE TABLE messages (
  id            bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  room_id       bigint NOT NULL REFERENCES rooms(id),
  user_id       bigint NOT NULL,        -- 검색 시 테넌트 필터용 (비정규화)
  role          text   NOT NULL,        -- user | assistant | tool
  content       text   NOT NULL,
  token_count   int,
  embedding     vector(1536),           -- RAG용 (선택적 채움: §7 함정3)
  tsv           tsvector
                GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
  created_at    timestamptz DEFAULT now()
);

-- Layer A: 방별 "러닝 요약" 단일 행 (upsert, openclaw 5섹션 구조)
CREATE TABLE room_summaries (
  room_id                    bigint PRIMARY KEY REFERENCES rooms(id),
  summary                    text   NOT NULL,   -- Decisions/Open TODOs/Constraints/Pending/Identifiers
  last_summarized_message_id bigint NOT NULL,   -- 증분 roll 커서
  version                    int    DEFAULT 1,
  token_count                int,
  updated_at                 timestamptz DEFAULT now()
);

-- (선택) 요약 버전 히스토리 — 롤백/디버깅용 보험. 컨텍스트엔 최신 1행만 사용.
CREATE TABLE room_summary_versions (
  id          bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  room_id     bigint NOT NULL REFERENCES rooms(id),
  version     int    NOT NULL,
  summary     text   NOT NULL,
  created_at  timestamptz DEFAULT now()
);

-- Layer B: 사용자 단위 장기 메모리 (크로스 세션)
CREATE TABLE user_memories (
  id             bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id        bigint NOT NULL,
  kind           text   NOT NULL,          -- preference | fact | profile
  content        text   NOT NULL,
  embedding      vector(1536),
  source_room_id bigint,
  confidence     real   DEFAULT 1.0,
  superseded_by  bigint,                    -- 통합/최신화 시 구 항목 무효화 (grok dream)
  created_at     timestamptz DEFAULT now(),
  updated_at     timestamptz DEFAULT now()
);

-- 인덱스
CREATE INDEX ON messages       USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON messages       USING gin  (tsv);
CREATE INDEX ON messages       (room_id, created_at DESC);
CREATE INDEX ON messages       (user_id);
CREATE INDEX ON user_memories  USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON user_memories  (user_id) WHERE superseded_by IS NULL;
```

**설계 선택 근거**
- `room_summaries`는 **러닝 요약 1행(upsert)** — append 로그 아님. 원본이 `messages`에 다 있으니 요약 이력은 감사 외 불필요. 롤백이 필요하면 `room_summary_versions`로 가볍게 보험.
- `messages`가 곧 claude-code의 transcriptPath(원본 포인터).
- `tsv`는 generated column으로 자동 유지(한국어 형태소가 필요하면 `simple` 대신 별도 형태소 설정 검토 → §7 참고).

---

## 5. 요약 트리거 + 회상 흐름

### 5-1. 컴팩션 트리거 — 매 턴 요약(X), 임계치 증분 roll(O)

```python
KEEP_RECENT_TURNS   = 8       # 최근 N턴은 항상 원문 유지 (요약 대상에서 분리)
ROLL_TOKEN_THRESHOLD = 6000   # 미요약 꼬리가 이만큼 쌓이면 roll
ROLL_MSG_THRESHOLD   = 20

def maybe_roll_summary(room_id: int) -> None:
    s = get_running_summary(room_id)                 # 없으면 최초 생성 경로
    tail = messages_after(room_id, s.last_summarized_message_id)
    to_summarize = tail[:-KEEP_RECENT_TURNS]          # 최근 N턴 제외한 앞부분만
    if tokens(to_summarize) < ROLL_TOKEN_THRESHOLD and len(to_summarize) < ROLL_MSG_THRESHOLD:
        return                                        # 아직 안 함 (비용 절약)
    enqueue_async(roll_job, room_id, upto=to_summarize[-1].id)  # 응답 블로킹 금지

def roll_job(room_id: int, upto: int) -> None:
    s = get_running_summary(room_id)
    new_chunk = messages_between(room_id, s.last_summarized_message_id, upto)
    # openclaw식: 이전 요약 재증류(stale 제거) + 새 청크 통합 → 5섹션 고정
    new_summary = cheap_llm(
        COMPACTION_PROMPT_5SECTION,
        previous_summary=s.summary,
        new_messages=new_chunk,
    )
    upsert_summary(room_id, new_summary, last_summarized_message_id=upto,
                   version=s.version + 1)
```

핵심:
- **매 턴 요약 금지** → 응답 지연/비용 폭증 방지.
- **증분 roll**(이전 요약 + 새 청크만) → 전체 재요약 대비 저렴, 비동기라 응답 경로 밖.
- **최근 N턴 verbatim 보존** → 요약 손실을 원문으로 커버(openclaw가 초반·최신 둘 다 지킨 비결).

### 5-2. 매 턴 컨텍스트 조립 (하이브리드 회상)

```python
def build_context(room_id: int, user_id: int, user_query: str) -> list:
    parts = [system_prompt()]

    # Layer B: 사용자 장기메모리 (부트스트랩) — 별도 예산 ~1.5K 토큰
    parts += load_user_memories(user_id, budget=1500)

    # Layer A-1: 방 러닝 요약 (인덱스) — ~2-4K
    parts += [get_running_summary(room_id).summary]

    # Layer A-2: 이 방 원본에서 하이브리드 검색 (grok식)
    recent = last_n_messages(room_id, KEEP_RECENT_TURNS)
    chunks = hybrid_search(room_id, user_id, user_query,
                           exclude_ids=[m.id for m in recent], k=8)
    parts += render_retrieved(chunks)   # "data, not instructions" 래핑 (주입 방어)

    # Layer A-3: 최근 N턴 원문 (verbatim tail)
    parts += render_verbatim(recent)

    parts += [user_query]
    return parts
```

### 5-3. 하이브리드 검색 (pgvector + full-text, RRF 병합)

점수 스케일이 다르므로 **가중합보다 RRF(Reciprocal Rank Fusion)가 견고**하다.

```sql
WITH vec AS (
  SELECT id, row_number() OVER (ORDER BY embedding <=> :q_emb) AS r
  FROM messages
  WHERE room_id = :room_id            -- 테넌트 스코프 (함정1: 절대 누락 금지)
    AND embedding IS NOT NULL
  ORDER BY embedding <=> :q_emb LIMIT 40
),
fts AS (
  SELECT id, row_number() OVER (
           ORDER BY ts_rank(tsv, websearch_to_tsquery('simple', :q_text)) DESC) AS r
  FROM messages
  WHERE room_id = :room_id
    AND tsv @@ websearch_to_tsquery('simple', :q_text)
  ORDER BY r LIMIT 40
)
SELECT id, SUM(1.0 / (60 + r)) AS score   -- RRF, k=60
FROM (SELECT id, r FROM vec UNION ALL SELECT id, r FROM fts) u
GROUP BY id ORDER BY score DESC LIMIT 8;
```

grok의 temporal decay(최신성 가중)를 원하면 RRF 점수에 `* exp(-age_days / 7.0)`(반감기 7일)를 곱한다.

---

## 6. 비용/지연/정확도 트레이드오프 — 실무 선택

| 축 | 선택지 | 추천 | 이유 |
|---|---|---|---|
| 요약 시점 | 매 턴 vs 임계치 | **임계치 + 증분 roll (비동기)** | 매 턴 요약은 응답 지연 + 비용 폭증. roll은 응답 경로 밖. |
| 요약 모델 | 메인 vs 전용 저렴 모델 | **전용 저렴 모델** | 요약은 싼 모델로 충분(grok compaction_model, CC 포크 아이디어). |
| 컨텍스트 구성 | 요약만 vs 요약+최근N+검색 | **하이브리드** | Postgres에서 RAG가 사실상 공짜. 요약만 넣으면 실험의 초반 소실을 그대로 재현. |
| 임베딩 대상 | 전량 vs 선택적 | **선택적**(user/assistant 실질 메시지만) | 인덱스 비대·검색 오염·임베딩 비용 절감. |
| 검색 스코프 | 전역 vs 방/사용자 한정 | **방 한정(A) / 사용자 한정(B)** | 멀티테넌시 격리 + 정확도. |

정리: **응답 경로는 가볍게(요약 조회 + 최근N + 검색 1~2쿼리), 무거운 요약 작업은 비동기로.** 정확도는 요약이 아니라 검색이 책임진다.

---

## 7. 흔한 함정 3가지

1. **멀티테넌시 검색 누수 (가장 위험).** 벡터 검색 `WHERE`에서 `room_id`/`user_id` 필터를 빠뜨리면 다른 방·다른 사용자의 대화가 컨텍스트로 유출(정보 유출 + 환각). **테넌트 필터 + Postgres RLS(Row Level Security) 이중 방어.** HNSW는 필터와 함께 쓰면 recall이 떨어질 수 있으니 후보를 넉넉히(LIMIT 40~100) 뽑아 사후 필터하거나 pgvector iterative scan을 켠다.

2. **요약 눈덩이(snowball)/드리프트.** "요약의 요약"을 반복하면 초반 정보 증발 — 실험의 claude-code 0.182(초반 0.000)가 그 실패. 방어: (a) openclaw식 **이전 요약 재증류**(보존이 아니라 stale 제거), (b) **최근 N턴 verbatim 보존**, (c) 결정적으로 **요약을 유일한 기억으로 신뢰하지 말고** 원본 검색(RAG) 항상 병행. "요약은 힌트일 뿐."

3. **임베딩 오염 + 스테일 메모리.** tool 결과·잡담·시스템 노이즈까지 전량 임베딩하면 인덱스 비대·검색 품질 저하. Layer B에서 사용자가 선호를 바꿨는데 옛 사실이 계속 검색되면 모순 답변. 방어: **선택적 임베딩**(실질 메시지만), 적절한 **청킹**, **temporal decay**, Layer B **supersede/consolidation 패스**(grok dream: 모순 해소=최신 사실 승리, 상대날짜→절대날짜, 휘발성 폐기).

> **보너스 함정**: 저장된 과거 메시지·검색 결과를 프롬프트에 넣을 때 반드시 **"data, not instructions"로 래핑**해 프롬프트 인젝션 차단(openclaw `<untrusted-text>` 방식).

---

## 8. 구현 로드맵 (권장 순서)

1. **MVP**: `messages` + `room_summaries` + 임계치 증분 roll(비동기) + 최근 N턴 원문. 검색 없이 요약만. → 동작 확인.
2. **RAG 추가**: pgvector 임베딩(선택적) + 하이브리드 검색 붙이기. → 초반 소실 해소 확인.
3. **Layer B**: `user_memories` + 부트스트랩 주입. → 크로스룸 개인화.
4. **정제 패스**: consolidation/supersede 배치(스테일 정리). → 장기 운영 안정화.
5. **검증**: 자체 프로브셋으로 "요약만 vs 요약+RAG" A/B. → 실측으로 파라미터(N, 임계치, k) 튜닝.

---

## 부록: 실험의 편향 요약

이 설계의 근거가 된 자체 실험([report_r2.md](results/report_r2.md))에는 아래 편향이 있어, 순위를 곧이곧대로 신뢰하면 안 된다(→ 별도 교정 실험 예정):

- **증분 체인 = openclaw 설계와 정렬**: 실험의 "이전 요약+새 청크 전체 재요약"이 openclaw 프롬프트의 네이티브 동작이라 openclaw에 유리.
- **복구 채널 삭제**: "요약본만 읽어라" 조건이 claude-code(transcriptPath)·grok(세그먼트/검색)의 핵심 회복 채널을 봉쇄 → 낮은 점수는 "기법의 회상력"이 아니라 "채널 제거 후 단일요약 잔존율".
- **프로브 재편**: 라운드2가 의도선호·미결다음을 빼고 verbatim 식별자(지엽 50%)로 재편 → verbatim 보존형(openclaw)에 유리, R1↔R2 비교 무효.
- **표본 n=1·반복 0회·baseline 없음** → 격차의 통계적 유의성 미확인.

**이 서비스 관점의 결론**: 위 편향들이 깎아내린 claude-code/grok의 강점(원본 복구·검색)이 Postgres 환경에선 오히려 기본 인프라이므로, 실험 순위와 무관하게 **"claude-code 철학 + openclaw 요약 + grok 검색"** 조합이 맞다.
