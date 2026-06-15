# ADR 0031: 안전 영속 스키마(sessions/safety_events) + 응답 kind 판별자

- Status: Accepted
- Date: 2026-06-15
- Deciders: Arden, Claude (Sub-2b brainstorming)

## Context

2-strike 는 세션별 상태(warning_count, ban)를 영속해야 하고, 감사를 위해 이벤트를
남겨야 한다. ADR 0028 은 `sessions` 테이블을 deferred 로 명시. 또한 프레임 깨는 경고/
차단은 NPC 대사가 아니라 시스템 메시지(ADR 0009) — 응답에서 구분돼야 한다.

## Decision

1. **`sessions` 테이블 도입** (단, `save_code` 컬럼은 여전히 deferred — ADD COLUMN 으로
   나중에): `session_uuid PK, warning_count, first_strike_term, banned_at, ban_reason, created_at`.
2. **`safety_events` 테이블**: `id, session_uuid, category, matched_term, created_at`.
   **원문 입력 저장 안 함** — 매칭 단어만(surfacing 정책: 전체 입력 인용 X).
3. **`TurnResponse.kind: "npc" | "warning" | "ban"`** 판별자 추가. `reply` 는 kind 에 따라
   NPC 대사 또는 시스템 메시지. `matched_term` 은 warning 시 채워짐.
4. ADR 0028 forward-compat 유지: 기존 `npc_state`/`chat_logs` 불변, ADD TABLE/COLUMN 만.

## Alternatives Considered

- A. ★ chosen — sessions/safety_events 신규, kind 판별자.
- B. npc_state 에 ban 컬럼 추가 — ban 은 세션 스코프(NPC 무관)라 부적절.
- C. 응답에 kind 없이 reply 텍스트로 추론 — 프론트가 프레임 구분 불가, fragile.

## Consequences

- `migrations/002_safety.sql` 신규. `apply_migrations` 가 migrations/*.sql 전부 적용.
- 차단된 세션의 모든 /turn → kind="ban" (LLM·strike 평가 skip).
- `docs/mapping-spec.md` 미매핑 항목에 안전 스키마/판별자 추가.

## Related

- ADR 0009 (frame-breaking), 0028 (forward-compat 스키마).
