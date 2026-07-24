# 미니 클로드코드 — 뷰/관측 레이어 기획서 (v2 · 로깅 중심 개정)

> **대상**: 강의용 "미니 클로드코드"의 **출력(로깅) + 입력(키보드)** 레이어.
> 이 미니 CC는 `notebooks/claude_code/`의 기법 8종을 하나로 합친 것 — ① system-reminder 주입 ② 툴 실행 파이프라인 ③ 하드·소프트 순서규칙 ④ 배치 스케줄링 ⑤ 멀티 함수호출 ⑥ ToolSearch KV캐시 ⑦ MCP connect/disconnect KV캐시 ⑧ 목 파일시스템 — 여기에 **⑨ 컨텍스트 전처리(신규·아직 미구현)** 를 더한다.
> **전제**: 에이전트 루프·툴 실행·LLM 호출·각 기법의 코어 로직은 노트북에 이미 있다. **이 문서의 일은 그 기법들의 내부 이벤트를 로그로 "보이게" 만드는 것.**
> **제약**: TUI 프레임워크 없음(표준 `print`/`sys.stdin`/ANSI만). 강의용이라 디테일 기능(**인터랙티브 승인/HITL**, Ctrl+C 세분화, 스킬 추가, 로그 회전, 플랫폼 분기)은 **비목표**. MCP는 실제 프로토콜 없이 **시뮬레이션**(등록 고지 + 가짜 도구설명·파라미터·서버설명 전달)만 한다.

> **개정(v2) 요지** — 초안은 CC 내부 로직을 모르는 상태로 작성돼 "일반 에이전트 로그"에 머물렀다. 정작 이 미니 CC가 가르치려는 기법들이 로그에 안 드러났다. 이번 개정:
> 1. 로그를 **기법 관측 중심**으로 재설계 — §4.4 "기법별 로그 이벤트 카탈로그"가 새 중심축.
> 2. 미드턴 유저 주입을 오리지널 실제 메커니즘(`<system-reminder>` 래핑 + 지정 문구, 화면 표시)으로 **정정**(§3.3).
> 3. **매 API 경계의 프롬프트 캐시(cache_read/creation) + 깨짐 사유**와 **컨텍스트 전처리 5단**을 1급 로그로 승격(§4.5).
> 4. 오리지널 시각 문법(`⏺`/`⎿`, 상태색)과 **3채널 원칙**(모델 전용 채널 dim 노출) 도입(§0, §4.1~4.2).
> 5. Ctrl+C/플랫폼/로그회전 등 강의 비핵심 축소.

---

## 0. 핵심 관점 — 로그 = 기법 관측 계층

미니 CC의 목적은 "동작하는 에이전트"가 아니라 **"내부에서 어떤 기법이 언제 발동하는지 눈에 보이는 에이전트"** 다. 로그는 사후 디버깅용이 아니라 **강의 교보재**다.

### 3채널 원칙

오리지널 CC의 핵심 통찰: 대화에는 *사람이 보는 것* 과 *모델만 보는 것* 이 섞여 있고, 그 경계가 안 보이면 내부가 안 보인다. 미니 CC 로그는 이걸 세 채널로 분리해 인코딩한다.

| 채널 | 내용 | 표기 | 오리지널 근거 |
|---|---|---|---|
| **A. 사람 발화/결과** | 어시스턴트 텍스트, 툴콜, 툴 결과 | `⏺` 머리불릿 / `⎿` 자식줄 + 상태색 | `figures.ts`, `MessageResponse.tsx` |
| **B. 모델 전용(SR·isMeta)** | `<system-reminder>`, 0번 유령메시지, 델타 고지, 메모리 회상 | **dim / 접힘으로 반드시 노출** ← "내부가 보인다"의 핵심 | `시스템리마인더-isMeta-신분증` |
| **C. API 경계 계측** | cache_read/creation, 캐시 깨짐 사유, 컨텍스트 전처리 발동 | `[cache]` / `[preprocess]` 접두 dim 줄 | `cost-tracker.ts`, `query.ts:364-463` |

> 초안의 로그는 채널 A만 있었다. **채널 B·C가 이 미니 CC의 존재 이유**다 — 8개 기법은 대부분 B·C에 자기 이벤트를 남긴다(§4.4 매핑).

---

## 1. 배경과 목표

### 1.1 왜 프레임워크를 안 쓰는가
전체화면 TUI는 alternate screen을 점유해 스크롤백이 사라지고 `| tee`·`> log` 리다이렉션이 깨진다. 코딩 에이전트는 **로그를 뒤로 스크롤해 다시 읽는 행위**가 핵심 UX이므로 일반 스크롤백에 이어 쓰는 방식이 맞다. 강의에서도 "로그를 위로 굴려 기법 발동 순간을 되짚는" 용도가 중요하다.

### 1.2 목표 (재정의)
- **G1 — 기법 가시화**: 8+1개 기법이 발동하는 순간을 각각 식별 가능한 로그 이벤트로 노출한다. (이 문서의 최우선)
- **G2 — 실행 중 개입**: 툴 실행 중에도 사용자가 끼어들어, 진행 중 툴 호출이 끝나는 즉시 메시지가 반영된다.

### 1.3 비목표 (강의 범위 밖)
- **인터랙티브 승인/휴먼인더루프**(툴 실행 전 y/n 게이트)·중단(`/stop`)·툴 파이프라인 6단계(권한 게이트)
- Ctrl+C 상태별 세분화, 스킬 시스템, 자동완성/멀티라인 편집기, 화면 분할/마우스
- 로그 파일 회전·보관 정책, Windows/구형터미널 분기
- 타이핑 중 로그 끼어듦의 완전 해결 (§7.1 — 최소 완화만)
- **MCP 실제 프로토콜** — 등록 시뮬레이션만(§5)

---

## 2. 실행 모델

### 2.1 stdin은 단 하나의 소유자를 갖는다
평소엔 메인이 `input()`, 툴 실행 중엔 리더 스레드가 stdin을 읽는 구조는 두 소비자가 같은 fd를 경쟁해 비결정적이 된다. **따라서: 리더 스레드가 프로세스 생명주기 내내 stdin을 독점한다. 메인은 `input()`을 절대 호출하지 않는다.** 이 리더 스레드가 있어야 **툴 실행 중에도 사용자 입력을 받아 큐에 넣을 수 있다**(P1의 전제).

```
  stdin ──> [리더 스레드(daemon)] ──> Queue[str] ──> [라우터] ──┬─ 유틸 명령 즉시 실행 (/log, /mcp, /status)
                                        (현재 상태 보고 분기)     └─ 일반 텍스트 → 대화 큐 적재 (다음 주입 지점까지 보관)
```

### 2.2 상태 정의
라우터는 메인이 노출하는 단일 상태 값을 읽기만 한다(라이터 하나 → 락 불필요).

| 상태 | 의미 | 일반 텍스트 입력 처리 |
|---|---|---|
| `IDLE` | 프롬프트 대기 | 즉시 새 턴 시작 |
| `THINKING` | API 스트리밍 중 | 대화 큐 적재 |
| `TOOL_RUNNING` | 툴 실행 중 | 대화 큐 적재 |

### 2.3 명령 vs 대화 입력
분기는 단순하다 — **유틸 슬래시 명령(`/log`·`/mcp`·`/status`)은 상태 무관 즉시 실행**, 그 외 일반 텍스트는 대화 입력이라 `IDLE`이면 새 턴, 툴 실행 중이면 대화 큐에 적재된다(§3). 지연 명령·중단(`/stop`)·인터랙티브 승인은 전부 비목표라 별도 부류가 없다.

---

## 3. P1 — 툴 실행 중 사용자 입력

### 3.1 시나리오
```
❯ 인증 모듈 리팩터링해줘

⏺ auth 관련 파일부터 찾아볼게요.
⏺ grep(class.*Auth)
  ⎿ src/auth/session.py:12  (+4건)
⏺ bash(pytest tests/test_auth.py -q)          ← 실행 중(3초). 여기서 타이핑 + 엔터
  ⏎ 대기열 1: "JWT 만료는 3시간이야"
  ⎿ ok  3.4s  exit=0                          ← 이 툴 호출이 끝나는 시점
  ⏎ 대기 메시지 1건 주입 (system-reminder로 래핑)
⏺ 알겠습니다. 만료 3시간 기준으로 보면 session.py의 ...
```
엔터 시점과 실제 주입 시점 사이의 간격 = **진행 중이던 툴 호출의 잔여 실행 시간**뿐. 작업은 중단되지 않고, 에이전트는 다음 API 호출부터 그 정보를 반영한다.

### 3.2 주입 시점 — B안
| 안 | 주입 지점 | 지연 | 정합성 위험 | 평가 |
|---|---|---|---|---|
| A | 즉시 (진행 중 툴 취소) | 최소 | 높음 (`function_call_output` 누락 처리) | 비목표(취소·중단 없음) |
| **B** | **진행 중 툴 호출이 끝나는 즉시** | 툴 1회분 | 없음 | **채택** |
| C | 턴 전체 종료 후 | 최대 | 없음 | 너무 느림 |

**병렬 호출 예외**: 한 응답이 `function_call`을 N개 담으면 API가 N개 전부의 `function_call_output`을 **같은 user 메시지**에 요구한다(부분 전송 불가). → 순차(1개)는 그 툴 끝나는 즉시, 병렬(N개)은 전부 끝난 직후 주입. 병렬 대기가 길면 첫 툴 완료 시 `⏎ 대기 중 — 병렬 3건 중 1건 완료, 전부 끝나면 주입` 안내 라인.

### 3.3 주입 방식 — ⚠️ 오리지널 메커니즘으로 정정
> **초안 오류**: 초안은 사용자 입력을 `text` 블록에 `[작업 중 사용자 추가 입력]` 접두어만 붙였다. 오리지널은 다르다.

오리지널 CC는 미드턴 유저 입력을 **`<system-reminder>`로 래핑**하되, `isMeta`를 붙이지 **않아 화면에는 남긴다**(= 채널 B이면서 사람에게도 보이는 특수 케이스). 실제 문구(`utils/messages.ts:5510`):
```
<system-reminder>
The user sent a new message while you were working:
{원본 입력}

IMPORTANT: After completing your current task, you MUST address the user's message.
</system-reminder>
```
같은 user 메시지 안에서 **`function_call_output` 블록들이 전부 앞, SR-래핑 텍스트가 맨 뒤** (API 순서 요구). 이 규약을 시스템 프롬프트에도 명시해 모델이 "툴 결과의 일부"가 아니라 "사람의 개입"으로 인식하게 한다.

로그: `queue_inject{count, wrap:"system-reminder", visible:true}` (채널 B, 화면엔 dim SR로 표시).

### 3.4 큐 정책 (강의용 최소)
| 항목 | 정책 |
|---|---|
| 여러 줄 누적 | 순서대로 개행 결합 → SR-래핑 단일 블록 |
| 큐 상한 | 20줄 / 4000자, 초과 시 오래된 것부터 폐기 + 경고 |
| 빈 엔터 | 무시하되 `⏎ (빈 입력)` 한 줄 (접수 여부 불안 방지) |
| 턴 종료 시 잔여 큐 | `end_turn`이면 큐 내용으로 자동 다음 턴, `❯ (대기열에서)` 표시 |

---

## 4. P2 — 로깅 (이 문서의 중심)

### 4.1 2채널 출력 + 3채널 인코딩
물리적으로는 **화면(stdout, 사람용 요약)** 과 **파일(JSONL, 전문·무삭제)** 2채널. 그 위에 §0의 3채널(A/B/C)을 색·마커로 인코딩한다. JSONL로 하는 이유: `jq` 필터·집계가 되기 때문.
```bash
jq -r 'select(.evt=="request_usage" and .cache_status=="MISS") | "\(.req_no): \(.miss_reason)"' session.jsonl
jq -r 'select(.evt=="edit_gate_result" and .gate!="pass") | "\(.path): \(.gate)"' session.jsonl
```

### 4.2 오리지널 시각 문법
| 요소 | 표기 | 근거 |
|---|---|---|
| 발화·툴콜 머리 | `⏺` (없으면 `●`) + 툴명 bold | `figures.ts:4` |
| 툴 결과/자식 줄 | `  ⎿  ` 2칸 들여쓰기 dim | `MessageResponse.tsx:22` |
| 실행 상태 | 불릿 색: **무채=실행중 / 초록=성공 / 빨강=실패** | `ToolUseLoader.tsx:19` |
| 큐잉된(대기) 툴콜 | dim `⏺` | `AssistantToolUseMessage.tsx:186` |
| 채널 B (모델 전용 SR) | dim + `⟦sr⟧` 접두, 접힘 가능 | isMeta/SR 분리 |
| 채널 C (API 경계) | dim + `[cache]`/`[preprocess]` 접두 | cost-tracker/query.ts |

### 4.3 로그 레벨 (`/log <level>`, 재시작 불필요)
| 레벨 | 노출 | 용도 |
|---|---|---|
| `quiet` | 어시스턴트 텍스트만 | 시연 |
| `normal` | + 툴콜 한 줄 요약, 턴 요약, **캐시 HIT/MISS 한 줄** | 기본값 |
| `verbose` | + 채널 B(SR 주입 전부), 인자·결과 전문, 파이프라인 단계, 배치 분할, 전처리 발동 | **강의 기본** |
| `trace` | + 이력 스캔 결과, tools 배열 스냅샷, 델타 차집합 계산 내역 | 기법 해부 |

> 강의는 `verbose`를 기본으로 켠다 — 채널 B·C가 이 레벨부터 보인다.

### 4.4 기법별 로그 이벤트 카탈로그 ★ (핵심)
각 기법이 "지금 발동했다"를 보여줄 **대표(hero) 이벤트**만 추린다. 필드는 JSONL 키. 화면엔 요약, 파일엔 전문.

**① system-reminder 주입** (채널 B)
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `sr_injected` | 수집 2지점(턴 시작/툴 라운드 꼬리) | `label`(at_mentioned_file·todo_reminder·date_change·queued_command·relevant_memories·nested_memory), `where`(user_turn\|in_loop), `delivery`(smoosh\|separate), `isMeta` | "어떤 SR이 언제 왜" — 6종 트리거 식별 |
| `ghost_message_rebuilt` | 매 API 호출 최상단 | `parts`(claudeMd·date·email) | 0번 유령이 매번 재생성·이력 미저장임 |
| `spoofing_neutralized` | 유저 입력에 가짜 `<system-reminder>` 있을 때 | `count` | `<`→중화 방어 |
| `memory_recalled` | 회상 트리거 | `name`, `age_days` | 신선도 경고(오래된 기억) |

**② 툴 실행 파이프라인** (채널 A + 게이트는 B) — *권한 게이트(오리지널 6단계)는 비목표라 생략: 1형식→2값→7실행→8변환*
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `pipeline_stage` | 1형식→2값→7실행→8변환 각 단계 | `stage_num`, `stage_name`, `verdict`(PASS\|FAIL), `reason` | **되돌릴 수 없는 실행(7) 전에 어디서 걸렀나** |
| `gate_blocked` | 형식·값 검사 FAIL | `stage`, `message`(모델로 되돌아가는 복구 프롬프트) | 실패가 `<tool_use_error>`로 자가수정 유도 |
| `result_truncated` | 8단계 상한 초과 | `original_chars`, `preview_chars`, `saved_path` | 큰 결과 디스크 격리 |

**③ 하드/소프트 순서규칙 + 디스패처** (채널 B)
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `edit_gate_result` | edit/write 시도 | `path`, `gate`(gate1_not_read\|gate2_stale\|pass), `st_timestamp`, `file_mtime` | **"지금 디스크 버전 본 적 없으면 금지"** 5겹 게이트 |
| `state_self_updated` | 편집 성공 | `path`, `new_timestamp` | readFileState 자가갱신 |
| `nudge_emitted` | 소프트 모드 | `type`(truncation\|typo_suggest\|reread_stub\|read_redirect\|multi_match), `detail` | 게이트 없이 넛지로 유도(안 따라도 동작) |
| `tool_search_called` / `tool_invoke_called` | 디스패처 | `query`/`name`, `mode`, `arg_validation` | **검색→실행 2단이 구조적으로 강제됨** |

**④ 배치 스케줄링** (채널 A)
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `partition_computed` | 툴 배치 분할 | `batches`[{`safe`, `tools`}] | **unsafe=단독 / 연속 read-only=병합** |
| `batch_start` | 각 배치 | `index`, `mode`(CONCURRENT\|SERIAL), `size` | 배치 간 직렬·배치 내 병렬(한도 10) |
| `tool_finish` | 툴 완료 | `tool`, `started_s`, `ended_s` | **완료 순서 ≠ emit 순서** (emit 순서는 보존) |

**⑤ 멀티 함수호출** (채널 A)
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `parallel_calls_emitted` | 한 응답에 다중 `function_call` | `count`, `names` | 한 턴 다중 호출 |
| `tool_call` / `tool_result` | 각 호출/결과 | `call_id`, `arguments` / `output_or_error` | `call_id`로 호출↔결과 조인 |
| `loop_terminated` | `function_call` 없음 | `reason` | `output_text`가 최종답 |

**⑥ ToolSearch KV캐시** (채널 C) — *캐시 관측의 주무대*
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `request_usage` | **매 API 호출** | `req_no`, `input_tokens`, `cached_tokens`, `cache_status`(HIT\|MISS), `miss_reason` | HIT은 계단식 증가(프리픽스 생존), MISS 0낙하 원인 |
| `tools_array_len` | 매 호출 | `len`(항상 2) | **tools 불변이 캐시 생존의 이유** |
| `tool_mounted` | [대조 실험] 도구를 tools에 실음 | `name`, `new_tools_len` | **직후 결정적 MISS** — "tools 변경만 캐시를 깬다" 증명 |

> `miss_reason` 값: `cold`(요청1) / `write_lag`(쓰기 반영 지연) / `server_noise`(무작위 위치) / `prefix_broken`(tools·시스템프롬프트 변경). 앞 3개는 설계 밖 정당 사유 — 그 뒤에도 `cached_tokens` 계단이 계속 오르면 "프리픽스 살아있음"의 증거.

**⑦ MCP connect/disconnect KV캐시** (채널 B + C) — §5에서 시뮬레이션
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `mcp_connect` / `mcp_disconnect` | 등록/해제 | `server` | 상태(CONNECTED)만 변경 |
| `deferred_delta_flushed` | 수집 지점 | `added`, `removed`(or `no_op`) | 시스템 프롬프트 재작성 X, **append-only 이름 델타** |
| `announced_names_reconstructed` | 델타 계산 전 | `names` | **로드 상태 DB 없음 = 대화 이력이 상태** |
| `request_usage`(연동) | connect 다음 턴 | `cache_status` | **connect/disconnect 있어도 HIT 유지**, MISS는 connect와 무상관 |

**⑧ 목 파일시스템** (기반 신호)
| 이벤트 | 발생 | 핵심 필드 | 강의 포인트 |
|---|---|---|---|
| `file_mtime_bumped` | edit/write/external 시 | `path`, `mtime` | **하드 게이트2·소프트 재읽기 스텁의 판정 입력** |
| `external_modify` | 모델 몰래 변경(사용자·린터) | `path`, `new_mtime` | "낡은 읽기" 상황을 만드는 훅 |

### 4.5 API 경계 로그 — 캐시 + 컨텍스트 전처리 (채널 C)
매 모델 호출마다 **직전(전처리)** 과 **직후(usage)** 를 한 묶음으로 찍는다. 이게 "왜 이번 호출이 싸/비쌌나, 컨텍스트가 언제 손질됐나"를 드러낸다.

**컨텍스트 전처리 5단 (⑨ 신규·미구현)** — 오리지널 `query.ts:364-463`을 이식할 자리. ReAct 사이클마다 모델 호출 **직전** 1회, 발동한 단계만 로그:
| 단계 | 이벤트 | 발동 조건 | 로그 필드 |
|---|---|---|---|
| 1 결과 예산 | `preprocess_budget` | 직전 묶음 200K자 초과 | `moved_to_disk`, `freed_chars` |
| 3 microcompact | `preprocess_microcompact` | 오래된 `tool_result` 존재 | `cleared_count` (로컬 메시지 무변경 → 프리픽스 보존) |
| 5 autocompact | `preprocess_autocompact` | 토큰 임계 초과 | `before_tokens`, `after_tokens`, `summary_sections` |

> compact 발동 시 UI 전용 경계 마커(`── Conversation compacted ──`, 모델 미전송) + 요약은 user 메시지로 주입. 강의 포인트: **microcompact는 캐시를 보존하지만 autocompact는 프리픽스를 통째로 갈아 MISS를 유발** → 직후 `request_usage`가 MISS로 찍히는 걸 나란히 보여준다.

### 4.6 색상 팔레트 (의미 인코딩)
| 용도 | ANSI | 대상 |
|---|---|---|
| 어시스턴트 발화 | `32` 초록 `⏺` + 무색 본문 | 본문은 색 X(가독성) |
| 툴콜 | `36` 시안 `⏺` + bold 툴명 | |
| 툴 결과(정상/에러) | `90` 회색 / `31` 빨강 `⎿` | |
| **채널 B (SR/isMeta)** | `2` dim + `⟦sr⟧` | **모델 전용 채널 — 강의 핵심** |
| **캐시 HIT / MISS** | `2` dim / `33` 노랑 `⚠` | MISS는 눈에 띄게 |
| 사용자 큐 | `35` 마젠타 `⏎` | 다른 것과 안 겹치게 |
| 메타(토큰·시간) | `2` dim | |

규칙: 한 줄 최대 2색. `NO_COLOR` 또는 `not isatty()`면 전부 비활성. `--no-emoji`로 `⏺→*`, `⎿→>`.

### 4.7 verbose 화면 예시 (기법이 보이는 로그)
```
─ turn 4 ───────────────────────────────────────────────────
  ⟦sr⟧ ghost rebuilt: claudeMd·date·email          (채널 B)
  ⟦sr⟧ sr_injected: todo_reminder (in_loop, smoosh)
  [cache] req#7 read=22,800 create=0  HIT           (채널 C)

⏺ session.py 만료를 3시간으로 바꿀게요.
⏺ edit_file
  │ path        src/auth/session.py
  │ old_string  "exp = now + timedelta(hours=1)"   (1줄)
  ⎿ ✗ gate2_stale: st_ts=14 < file_mtime=17 — 다시 읽으세요   ← ③ 하드 게이트 발동
⏺ read_file(src/auth/session.py)
  ⎿ ok  (state_self_updated: ts=17)
⏺ edit_file
  ⎿ ok  0.004s  1곳 수정

  [batch] partition: [ {safe:false, tools:[bash]} ]  SERIAL   ← ④ 배치 분할
⏺ bash(pytest -q)
  ⎿ ok  3.41s  exit=0
─ turn 4 end  4.1s · in 24,102 · out 214 · cache_read 22,800 ─
```
설계 포인트: **인자는 `│` 가지로 세로 나열**(JSON 한 줄은 못 읽음), **긴 값은 잘라내되 원래 크기 표시**(`(184줄)`), **채널 B는 `⟦sr⟧` dim으로 본문과 분리**, **매 turn 머리에 `[cache]` 한 줄**(0으로 떨어지면 즉시 눈에 띔).

### 4.8 JSONL 스키마
공통 필드 `ts`·`turn`·`evt`, 나머지는 이벤트별. `call_id`로 call↔result, `req_no`로 usage 시계열 조인.
```json
{"ts":"2026-07-24T12:04:31Z","turn":4,"evt":"edit_gate_result","path":"src/auth/session.py","gate":"gate2_stale","st_timestamp":14,"file_mtime":17}
{"ts":"2026-07-24T12:04:31Z","turn":4,"evt":"request_usage","req_no":7,"input_tokens":24102,"cached_tokens":22800,"cache_status":"HIT","miss_reason":null}
{"ts":"2026-07-24T12:04:33Z","turn":4,"evt":"partition_computed","batches":[{"safe":false,"tools":["bash"]}]}
```

### 4.9 로그 파일 (강의용 최소)
- 경로: `~/.<앱명>/logs/{시작시각}.jsonl`, **세션당 1파일**. 회전·보관 정책 없음(비목표).
- `/log path`로 경로 출력 → 옆 터미널에서 `tail -f | jq`. **화면은 `verbose`, 옆 창은 전문** — 프레임워크 없이 얻는 "화면 분할".

---

## 5. MCP — 등록 시뮬레이션 (실 프로토콜 없음)

미니 CC의 MCP는 **진짜 서버에 연결하지 않는다.** `/mcp connect <server>`가 하는 일 = ⑦ 기법을 그대로 시연:
1. 클라이언트 `CONNECTED[server]=True` (상태만).
2. 미리 정의된 **가짜 도구설명·파라미터·서버설명**을 레지스트리에 추가 (`isMcp:true` → tools 배열엔 절대 안 실림, 항상 defer).
3. 수집 지점에서 **append-only `<system-reminder>` 델타**로 "`mcp__server__tool` 등록됨" 이름만 고지 → `deferred_delta_flushed{added:[...]}`.
4. 다음 턴 첫 요청의 `request_usage`가 **여전히 HIT** → "MCP 붙여도 tools·시스템프롬프트 불변이라 캐시 안 깨진다"를 로그로 증명.
5. `/mcp disconnect <server>` → `removed` 델타, 해제된 서버 도구 호출 시 `disconnected_tool_invoke` 힌트(재시도 말고 사용자 보고).

즉 MCP는 "머머가 등록되었습니다" + 가짜 스키마 전달 + 그것이 KV캐시에 **영향 없음**을 보여주는 관측 데모다. 실제 stdio/SSE 트랜스포트·핸드셰이크는 전부 비목표.

---

## 6. 명령어 레퍼런스 (최소)
슬래시 명령은 셋뿐 — 전부 상태 무관 즉시 실행, 전부 읽기/표시 전용이라 별도 구현 부담이 없다. **일반 텍스트는 명령이 아니라 대화 입력**이며 툴 실행 중이면 자동으로 큐에 적재된다(§3).

| 명령 | 설명 |
|---|---|
| `/status` | 현재 상태·턴수·토큰·캐시 hit_rate 요약 (읽기 전용) |
| `/log <level>` `/log path` | 로그 레벨 전환 / 로그 파일 경로 출력 |
| `/mcp connect\|disconnect <server>` `/mcp list` | MCP 시뮬 등록/해제/목록 (§5) |

> 중단(`/stop`)·대화 초기화(`/clear`)·모델 변경(`/model`)·큐 관리(`/queue`)·인터랙티브 승인은 전부 비목표 — 각각 취소 라우팅·상태 리셋·HITL 구현이 필요해 강의 범위를 넘는다.

---

## 7. 알려진 한계
### 7.1 타이핑 중 로그 끼어듦
프레임워크 없이는 완전 해결 불가. **완화(1순위)**: 첫 글자 입력 감지 시 툴 로그를 잠시 버퍼링했다가 엔터 직후 방출. **최소 요구**: 큐 접수 확인 라인(`⏎ 대기열 1: "..."`)을 반드시 출력 — 입력이 접수됐는지 모르는 상태가 가장 나쁘다.
### 7.2 CJK 폭
박스·표 정렬 시 `len()`은 한글에서 어긋난다. ANSI 제거 후 `wcwidth.wcswidth()`로 셀 폭 계산. 이모지는 폭이 터미널마다 달라 **정렬 위치엔 이모지 안 씀**(줄 끝에만).

---

## 8. 구현 순서
| 마일스톤 | 범위 | 검증 기준 |
|---|---|---|
| **M1** | 실행 루프 골격 + 상태머신 3종 + 리더스레드·큐 + 오리지널 렌더(`⏺`/`⎿`, 상태색) | 툴 실행 중 엔터가 큐에 쌓이고 확인 라인 출력, 성공/실패 색 구분 |
| **M2** | **이벤트 버스 + JSONL + 3채널 인코딩 + 레벨 4종** (로깅 관측 계층) | 기법 모듈이 이벤트를 emit하면 화면/파일 양쪽에 채널별로 렌더. `/log verbose` 재시작 없이 전환 |
| **M3** | **§4.4 기법별 렌더러 배선** — 8기법 hero 이벤트 + §4.5 API 경계(캐시/전처리) | 하드 게이트·파이프라인 단계·배치 분할·cache HIT/MISS·MCP 델타가 각각 로그로 보임. `jq`로 gate FAIL만 추출 가능 |
| **M4** | P1 미드턴 주입(§3.3 SR 래핑) + MCP 시뮬(§5) + 전처리 5단(⑨ 신규) | 툴 하나 끝나는 즉시 SR-래핑 유저 메시지 전송, MCP connect 후에도 HIT 유지가 로그로 확인 |

M1·M2가 골격, **M3가 이 기획의 실질(기법 가시화)**, M4는 통합. 각 기법 코어는 노트북에 있으므로 M3는 "배선"이 핵심이지 재구현이 아니다.

---

## 9. 미결 사항
- `sr_injected` 화면 요약을 얼마나 접을지 — 6종을 매번 다 펴면 노이즈, 다 접으면 채널 B가 안 보임. 기본 접힘 + `/log verbose`에서 펼침?
- 컨텍스트 전처리(⑨)는 노트북 미구현 — autocompact 요약 섹션 스키마를 오리지널 9섹션 그대로 갈지 강의용으로 줄일지.
- `miss_reason` 자동 귀속(cold/write_lag/server_noise/prefix_broken) 판정 로직을 어디까지 흉내 낼지 — 서버 노이즈는 결정 불가라 "추정"으로 표기해야.
- 병렬 툴 호출의 완료 순서 뒤섞임(`tool_finish`)을 화면에서 어떻게 시각화할지(타임라인 바 vs 로그 줄).
