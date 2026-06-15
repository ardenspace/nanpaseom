# Phase 1.0 Sub-2b — 안전 모더레이션 슬라이스 Design Spec

- Date: 2026-06-15
- Deciders: Arden, Claude (brainstorming session)
- Status: Approved (design) → 다음 단계는 implementation plan (writing-plans)

## 목표 (Goal)

수리공 단독 `POST /turn` 경로에 **안전 프레임을 완성**한다 — 결정적(deterministic) **2-strike 성희롱/혐오 트랙** + 안전 상태 영속화 + 프레임 깨는 시스템 응답. Sub-2 가 "턴 루프가 닫힌다" 를 증명했다면, Sub-2b 는 "공개 URL 의 자유 입력이 안전하게 처리된다" 를 증명한다.

ADR 0009 의 4-layer 안전 디자인 중 이 슬라이스가 채우는 부분: **Layer 2.5 (2-strike sexual/harassment)** 의 결정적 디니리스트 트랙. Layer 1 (이미 구현) 과 Layer 4 (이미 구현) 사이를 메운다.

## 범위 (Scope)

**In:**
- `rules/safety.yaml` — 큐레이션 디니리스트 + 페르소나-공격 키워드(Layer 1 에서 승격) + 시스템 메시지 템플릿.
- `app/safety/moderation.py` — 결정적 감지기 (확장 가능한 checker 인터페이스).
- `app/safety/strike.py` — 세션/strike/safety_events 영속 + 2-strike 상태머신.
- `migrations/002_safety.sql` — `sessions` + `safety_events` 테이블 (ADD TABLE only).
- `TurnResponse` 에 `kind` 판별자 추가 + 엔드포인트 오케스트레이션.

**Out (v1.1 / 이후 슬라이스):**
- **ML 모더레이션** (ADR 0009 Layer 2 의 violence/self-harm/hate + 카테고리 기반 성적 감지). 원래 OpenAI Moderation 이었으나 로컬-온리 stance (ADR 0027) 로 폐기. checker 인터페이스 뒤에 끼울 수 있게 설계만 열어둠.
- 나머지 NPC 3명, save-code/쿠키, running summary, Cloudflare/failover, 프론트엔드/모바일.

## 핵심 결정 (Decisions)

### Decision 1 — 결정적 디니리스트 우선, ML 모더레이션 디퍼 (ADR 0030)

OpenAI Moderation API 는 기획 단계 실수. 이 프로젝트는 ADR 0027 에서 로컬-온리로 피벗했고, 이 Mac Mini(48GB)는 **llama.cpp 모델을 한 번에 하나만 GPU 오프로드** 가능 (메모리 `macmini-gpu-single-model-offload` 참조) → Gemma 옆에 가드 모델 상시 GPU 띄우기 부담.

따라서 이 슬라이스의 모더레이션 = **결정적 디니리스트(키워드) 트랙만**. 이유:
1. **게이트 테스트 가능** — LLM 없이 전부 결정적. (ADR 0029 에서 테스트 못 하는 live 경로가 버그를 숨긴 교훈의 정확한 반대.)
2. 하드웨어 경합 0, 다운로드 0.
3. 포트폴리오 시그널의 핵심인 **2-strike 윤리 stance** 를 end-to-end 로 출하.

ML 분류기는 v1.1 에서 `detect()` 의 두 번째 checker 로 추가 (인터페이스만 지금 연다).

### Decision 2 — 안전 데이터는 `rules/safety.yaml` (ADR 0030)

디니리스트·페르소나공격 키워드·시스템 메시지 템플릿은 *게임 밸런스 데이터* → 코드 아닌 YAML (프로젝트 원칙: "튜닝은 YAML 수정"). 디자이너가 코드 안 건드리고 갱신. 스키마 검증 (`check_yaml.py` + pydantic). Layer 1 의 페르소나공격 키워드도 `input_filter.py` 하드코딩에서 여기로 승격.

### Decision 3 — `sessions` + `safety_events` 테이블 신규 (ADR 0031)

ADR 0028 이 `sessions` 테이블을 deferred 로 명시했음. 이제 도입하되 **save_code 컬럼은 여전히 deferred** (ADD COLUMN 으로 나중에). forward-compat 약속 유지 (기존 `npc_state`/`chat_logs` 불변).

- `sessions(session_uuid PK, warning_count INT DEFAULT 0, first_strike_term TEXT, banned_at TIMESTAMPTZ, ban_reason TEXT, created_at)`.
- `safety_events(id BIGSERIAL PK, session_uuid, category TEXT, matched_term TEXT, created_at)`.

**safety_events 에 원문 입력 저장 안 함** — 매칭 단어만. 스펙의 surfacing 정책("매칭된 정확한 단어 1개만, 전체 입력 인용 X") 준수, 다른 욕설 surface 위험 차단. 빈도 기반 튜닝(Week 9)엔 충분.

### Decision 4 — 응답 판별자 `kind` (ADR 0031)

프레임 깨는 경고/차단은 NPC 대사가 아니라 *시스템 메시지* (의도적 frame-breaking, ADR 0009). 프론트가 NPC 프레임 바깥에서 렌더해야 함 → `TurnResponse.kind: "npc" | "warning" | "ban"`. `reply` 필드는 kind 에 따라 NPC 대사 또는 시스템 메시지 텍스트를 담는다. `matched_term` 은 warning 시 채워짐.

## 아키텍처 (Architecture)

### 데이터 흐름 — 입력당 상태머신 (결정적)

```
POST /turn(session_uuid?, npc_id, player_input):
  session_uuid = req.session_uuid or mint()
  sess = repo.load_session(conn, session_uuid)        # 없으면 row 생성

  # 1) ban 게이트 — 차단된 세션은 모든 호출 차단
  if sess.banned_at is not None:
      return TurnResponse(kind="ban", reply=ban_message(sess), session_uuid)

  # 2) strike 평가 (결정적 감지기)
  verdict = moderation.detect(player_input, checkers=[denylist_checker])
  if verdict.category != "clean":
      outcome = strike.register(conn, session_uuid, verdict)   # warning_count 증가 + safety_events
      if outcome == "warning":   # STRIKE 1
          return TurnResponse(kind="warning", reply=warning_message(verdict.matched_term),
                              matched_term=verdict.matched_term, session_uuid)
      else:                       # STRIKE 2 → ban
          return TurnResponse(kind="ban", reply=ban_message(sess_after), session_uuid)
      # 주의: LLM 호출 X, awareness 변화 X, chat_logs 기록 X (턴 무효)

  # 3) clean → 기존 NPC 턴 (Layer 1 길이/페르소나 + LLM + Layer 4)
  resp = run_turn(conn, session_uuid, npc_id, player_input)   # kind="npc"
  return resp
```

**우선순위:** ban > 성희롱(frame-break) > 페르소나공격(in-character 디플렉션, run_turn 내 Layer 1) > 정상 턴. 성희롱과 페르소나공격이 동시 매칭돼도 더 심각한 frame-breaking 이 이긴다 (strike 평가가 run_turn 보다 먼저).

### 컴포넌트 경계

| 유닛 | 책임 | 의존 |
|---|---|---|
| `rules/safety.yaml` | 디니리스트·페르소나공격 키워드·메시지 템플릿 (데이터) | — |
| `app/safety/schemas.py` (신규) | `SafetyRules` pydantic 검증 (denylist/persona_attack/messages, extra=forbid) | yaml |
| `app/safety/moderation.py` | `detect(text, checkers) -> Verdict(category, matched_term)`. 입력 정규화(공백/반복 제거) 후 substring 매칭. checker 리스트 = 확장점 | safety rules |
| `app/safety/strike.py` | `register(conn, sid, verdict) -> "warning"|"ban"`. 세션 warning_count 전이 + safety_events append | store |
| `app/store/repo.py` (확장) | `load_session` / `mint_session_row` / `ban_session` / `append_safety_event` | psycopg |
| `app/api/main.py` (확장) | ban 게이트 → strike → run_turn 오케스트레이션 | 위 전부 |
| `app/models.py` (확장) | `TurnResponse.kind` + `matched_term` | — |

`run_turn` (Sub-2) 은 **NPC 턴에 집중하도록 그대로 둔다** — 안전 프레임은 그 바깥(엔드포인트)에 둘러친다. 이렇게 하면 run_turn 의 기존 테스트/회귀가 안 깨지고, 안전 로직이 독립적으로 테스트된다.

### moderation.detect 확장 인터페이스 (Decision 1 약속)

```python
Verdict = SafetyVerdict(category: Literal["clean", "harassment"], matched_term: str | None)
Checker = Callable[[str], SafetyVerdict]   # text -> verdict

def detect(text: str, checkers: list[Checker]) -> SafetyVerdict:
    norm = _normalize(text)            # 공백/반복 자모 정규화 (음운변형 "씨 발" 캐치)
    for check in checkers:
        v = check(norm)
        if v.category != "clean":
            return v                    # 첫 non-clean 반환
    return SafetyVerdict(category="clean", matched_term=None)
```

슬라이스: `checkers=[denylist_checker]` (category 전부 "harassment" 로 합침 — sexual/혐오/욕설 구분은 ML 과 함께 v1.1). v1.1: `checkers=[denylist_checker, ml_checker]` 로 append, finer category 반환.

## 에러 처리 / 엣지 케이스

- **세션 row 미존재:** `load_session` 이 기본값(warning_count=0, banned_at=None) 반환 + lazy 생성. (npc_state 의 패턴과 동일.)
- **차단 후 재호출:** banned_at 세팅된 세션의 모든 /turn → kind="ban" (LLM·strike 평가 모두 skip).
- **정규화 후 빈 문자열 / 매우 짧은 입력:** denylist 매칭 안 됨 → clean.
- **성희롱 + 길이 초과 동시:** strike 평가가 먼저 → warning/ban (길이 캡은 run_turn 내라 도달 안 함).
- **save-code 무효화 (ADR 0009 Strike 2 결과):** save-code 자체가 미구현 → 이 슬라이스에선 N/A. ban 은 session_uuid 스코프 (쿠키). 스펙대로 "다른 디바이스/브라우저 초기화로 새 세션 가능" = 의도적 soft ban (v1 IP 차단 없음).

## 테스트 전략 (전부 게이트 — 결정적)

ADR 0029 교훈 적용: 안전 경로는 **실제 LLM 없이 전부 결정적으로 검증 가능** → live 불필요.

- `tests/safety/test_moderation.py` — detect: clean 통과, denylist hit + matched_term, 정규화("씨 발"/"ㅅㅂ") 캐치, checker 순서.
- `tests/safety/test_strike.py` — register: 1st→warning_count=1, 2nd→banned_at 세팅 + ban_reason 두 단어, safety_events row 2개, 원문 미저장(매칭단어만).
- `tests/store/test_repo.py` (확장) — load_session 기본값, ban_session, append_safety_event roundtrip.
- `tests/api/test_turn_endpoint.py` (확장) — **핵심 회귀들:**
  - clean 입력 → kind="npc" (기존 동작 불변).
  - 성희롱 입력 1회 → kind="warning" + matched_term, **awareness/chat_logs 불변** (턴 무효 증명).
  - 성희롱 2회 → kind="ban", 이후 clean 입력도 kind="ban" (차단이 다음 호출 막음).
  - safety.yaml 디니리스트 로드 + 스키마 검증.
- `scripts/check_yaml.py` — safety.yaml 파싱.

## ADR (이 슬라이스가 만드는 결정 기록)

- **ADR 0030** — 결정적 디니리스트 2-strike 우선, ML 모더레이션 디퍼 (checker 확장 인터페이스). ADR 0009 Layer 2 ML → v1.1 명시. 안전 데이터는 rules/safety.yaml.
- **ADR 0031** — safety 영속 스키마 (`sessions` + `safety_events`, ADR 0028 forward-compat ADD TABLE, save_code 여전히 deferred) + `TurnResponse.kind` 판별자.

## 권한 문서 갱신 (CLAUDE.md 룰)

- `docs/mechanic-spec.md` "2-Strike Sexual / Harassment Policy (Layer 2.5)" 섹션에 Sub-2b 노트 추가: 감지 = 디니리스트(local) 만; Moderation 카테고리(ML)는 v1.1.
- `docs/mapping-spec.md` 미매핑 항목에 안전 영속 스키마 / 판별자 추가 (lore 무관 제작 결정).

## 핵심 회귀 (이 슬라이스가 증명하는 단 하나)

`tests/api/test_turn_endpoint.py` — **성희롱 2회 입력 → 세션 영구 차단 → 이후 clean 입력도 차단**, 그리고 **strike 가 awareness/chat_logs 를 건드리지 않는다(턴 무효)**. 공개 URL 자유 입력의 윤리 가드가 닫힌다.
