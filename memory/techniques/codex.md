# Codex (OpenAI) — 컨텍스트 체크포인트 컴팩션 (Context Checkpoint Compaction)

> 대상 레포: `/Users/seobi/jinsup_space/codex` (실제 소스: `codex-rs/`, Rust)
> 리서치 문서: `/Users/seobi/jinsup_space/codex/codex-memory.html` (장기기억 "memories" 파이프라인 정리 — 컴팩션과는 별도 시스템)

## 개요

Codex는 긴 대화를 **"다음 LLM에게 넘기는 핸드오프(handoff) 요약"** 으로 압축한다. 컨텍스트 임계치에 도달하면 대화 히스토리 전체를 모델에게 그대로 보여주면서 "CONTEXT CHECKPOINT COMPACTION을 수행하라"는 사용자 메시지 1개를 덧붙여 요약을 생성시키고, 이후 **히스토리 전체를 [최근 사용자 메시지 일부 + 브리징 프리픽스가 붙은 요약 1개]로 통째로 교체**한다. 요약은 "다른 LLM이 작업을 이어받는다"는 프레임으로 작성되며, 재주입 시에도 "다른 언어 모델이 먼저 풀다가 남긴 요약"이라는 프리픽스(SUMMARY_PREFIX)로 감싸 넣는다. 구현체는 3종이 공존한다: (1) 로컬 컴팩션(위 프롬프트 사용), (2) 리모트 컴팩션 v1/v2(서버측 `/responses/compact` 엔드포인트가 압축된 트랜스크립트를 반환 — 프롬프트는 서버측이라 레포에 없음), (3) TokenBudget 모드(요약 없이 새 컨텍스트 윈도우로 리셋). 별도로, 세션 종료 후 백그라운드에서 rollout을 장기기억으로 추출·통합하는 "memories" 파이프라인이 있으나 이는 대화 내 컴팩션과 독립된 크로스-세션 시스템이다.

## 트리거

1. **자동(토큰 임계치)** — `context_window_token_status()`가 `token_limit_reached`를 계산 (`core/src/session/context_window.rs:77-80`). 기준: `auto_compact_token_limit`(기본 **컨텍스트 윈도우의 90%** — `protocol/src/openai_models.rs:459-469`의 `(context_window * 9) / 10`) 초과 또는 풀 컨텍스트 윈도우 도달.
   - **PreTurn**: 샘플링 시작 전 검사 (`core/src/session/turn.rs:993-1005`, `run_pre_sampling_compact`) — reason `ContextLimit`.
   - **MidTurn**: 턴 도중 툴콜 후속(follow-up)이 필요한데 한도 초과 시 (`core/src/session/turn.rs:419-441`) — 턴을 끊지 않고 인라인 컴팩션 후 계속.
   - **PreTurn 특수 사유**: 모델 전환으로 윈도우가 줄었을 때(`ModelDownshift`), 프롬프트 프리픽스 해시 변경(`CompHashChanged`) (`core/src/session/turn.rs:1080-1140`).
2. **수동(/compact 명령)** — `Op::Compact` → `CompactTask` (`core/src/session/handlers.rs:826`, `core/src/tasks/compact.rs:27-84`) — reason `UserRequested`.
3. 세션 종료 시에는 컴팩션이 발동하지 않음(종료 후에는 별도 memories 백그라운드 파이프라인이 rollout을 처리).

## 파이프라인 (로컬 컴팩션 기준, `core/src/compact.rs`)

1. **요약 생성**: 현재 히스토리 사본에 `SUMMARIZATION_PROMPT`(설정 `compact_prompt`로 오버라이드 가능)를 **user 메시지로 append**하고, 평소와 같은 base instructions로 모델을 1회 스트리밍 호출 (`compact.rs:112-142, 272-346`). 요약 생성 중에도 컨텍스트가 넘치면 **가장 오래된 히스토리 항목부터 제거**하며 재시도 (`compact.rs:310-325`).
2. **교체 히스토리 구성**: 마지막 assistant 메시지를 요약으로 취해 `SUMMARY_PREFIX + "\n" + 요약`을 만들고 (`compact.rs:348-353`), 원 히스토리에서 **실제 사용자 메시지들을 최신 순으로 최대 20,000 토큰(`COMPACT_USER_MESSAGE_MAX_TOKENS`)까지 보존**한 뒤, 그 끝에 요약을 **user 롤 메시지**로 붙인다 (`compact.rs:622-696`, `build_compacted_history`).
3. **히스토리 교체(회상 없음, 상시 노출)**: `replace_compacted_history()`로 라이브 히스토리를 통째로 교체 (`compact.rs:374-384`). 이후 모든 턴의 프롬프트에 요약이 user 메시지로 항상 포함된다 — 별도 회상(retrieval) 단계 없음.
4. **초기 컨텍스트 재주입**: PreTurn/수동은 `DoNotInject` — 다음 정규 턴에서 시스템/환경 컨텍스트를 새로 주입. MidTurn은 모델 학습 관례상 **요약이 히스토리 마지막**이어야 하므로 마지막 실제 user 메시지 바로 위에 초기 컨텍스트를 삽입 (`compact.rs:59-74, 565-620`).
5. **경고 이벤트**: 컴팩션 후 "Long threads and multiple compactions can cause the model to be less accurate..." 경고 발신 (`compact.rs:389-392`).
6. **훅**: pre/post-compact 훅이 전 구현체 공통으로 실행됨 (`hook_runtime`).

리모트 v2 (`core/src/compact_remote_v2.rs`): 히스토리를 서버 `/responses/compact`로 보내 압축 트랜스크립트를 받아 설치. 유지 메시지 예산 64,000 토큰, agent 메시지당 10,000 토큰 (`compact_remote_v2.rs:57-60`). 반환물에서 developer 메시지·세션 프리픽스 래퍼는 드롭 (`compact_remote.rs:302-345`). TokenBudget 모드 (`core/src/compact_token_budget.rs`): 모델/서버 요약을 **생략**하고 새 컨텍스트 윈도우 설치만 수행.

## 산출물 구조

- 요약 자체는 **자유 서식**(고정 섹션 헤더 없음). 프롬프트가 요구하는 4가지 포함 항목만 지정: ① 현재 진행 상황·핵심 결정 ② 중요한 맥락·제약·사용자 선호 ③ 남은 일(다음 단계) ④ 계속하는 데 필요한 핵심 데이터·예시·참조.
- 최종 저장 형태: `user` 롤 메시지 1개 = `SUMMARY_PREFIX`(1문단, "다른 언어 모델이 만든 요약이니 중복 작업을 피하고 이어서 하라") + 개행 + 모델이 생성한 요약 본문. 이 프리픽스는 요약 메시지 식별자 역할도 한다 (`is_summary_message`, `compact.rs:551-553`).
- 요약이 비면 `"(no summary available)"` 폴백 (`compact.rs:681-685`).

## 원문 프롬프트 발견 위치

| 프롬프트 | 파일 | 사용처 |
|---|---|---|
| SUMMARIZATION_PROMPT (요약 생성 지시) | `codex-rs/prompts/templates/compact/prompt.md` (전체 9줄) | `codex-rs/prompts/src/compact.rs:1` (include_str), `codex-rs/core/src/compact.rs:119-124` (자동), `codex-rs/core/src/tasks/compact.rs:66-76` (수동) |
| SUMMARY_PREFIX (요약 재주입 프리픽스) | `codex-rs/prompts/templates/compact/summary_prefix.md` (1줄) | `codex-rs/prompts/src/compact.rs:2`, `codex-rs/core/src/compact.rs:351` |

두 파일 모두 소스 템플릿에서 원문 그대로 복사함 (verbatim, 치환 변수 없음). 사용자 설정 `compact_prompt` / `experimental_compact_prompt_file`(`config/src/config_toml.rs:239,507`)로 교체 가능.

## 특이점 (다른 하네스와의 차별점)

1. **핸드오프 프레임**: "당신의 컨텍스트를 압축하라"가 아니라 "**다른 LLM에게 넘길 인수인계 요약을 써라**"는 프레임. 재주입 프리픽스도 "다른 모델이 먼저 풀다 남긴 요약"이라고 서술해, 모델이 요약을 자기 발화가 아닌 외부 증거로 취급하게 한다.
2. **프롬프트가 극단적으로 짧다** (426자). 고정 출력 스키마·섹션 템플릿·예시가 전혀 없다 (Claude Code류의 8~9섹션 구조화 요약과 대조적).
3. **원본 사용자 메시지 보존**: 요약만 남기지 않고 최근 user 메시지들을 최대 2만 토큰까지 원문 그대로 함께 보존 — 사용자 의도의 lossy 압축을 완화.
4. **요약이 user 롤로 저장**됨 (assistant/system 아님). 프리픽스 문자열 매칭으로 요약 메시지를 식별.
5. **3중 구현 공존**: 로컬(프롬프트) / 리모트(서버측 `/responses/compact`, 프롬프트 비공개) / TokenBudget(무요약 리셋). 프로바이더·피처 플래그로 선택 (`core/src/session/turn.rs:1146-1225`).
6. **MidTurn 인라인 컴팩션**: 툴콜 루프 도중에도 턴을 끊지 않고 압축 후 계속 진행. 컴팩션 요약의 위치(히스토리 마지막)까지 모델 학습 관례에 맞춰 관리.
7. **컴팩션과 장기기억의 분리**: 대화 내 압축(compact)과 크로스-세션 기억(memories: Phase1 추출 `memories/write/templates/memories/stage_one_system.md` → Phase2 통합 `consolidation.md` → grep 기반 회상 `ext/memories/templates/memories/read_path.md`)이 완전히 별개 파이프라인. 컴팩션은 회상 단계가 없는 단방향 교체다.
