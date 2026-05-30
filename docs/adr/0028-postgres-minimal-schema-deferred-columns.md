# ADR 0028: Sub-2 slice 는 Postgres 최소 스키마 — deferred 컬럼/테이블 명시

- Status: Accepted
- Date: 2026-05-30
- Deciders: Arden, Claude (Sub-2 brainstorming session)

## Context

mechanic-spec Approach C (line 96-100) 는 4 테이블 (`sessions` / `npc_state` / `global_state` / `chat_logs`) + save_code / playthrough / safety 컬럼을 명세. Sub-2 slice 는 수리공 단독 turn loop 증명만 범위 — 전체 스키마는 over-build.

## Decision

slice 스키마 = turn loop 가 쓰는 최소만:
- `npc_state (session_uuid, npc_id, awareness, memory_tags text[], summary, updated_at)` PK `(session_uuid, npc_id)`.
- `chat_logs (id, session_uuid, npc_id, turn_index, role, content, reply_json_raw, created_at)`.

**Deferred (Sub-2b, 추가만 — 기존 컬럼 변경 X):** `sessions` 테이블 + `save_code`, `global_state` 테이블, `npc_state`/`chat_logs` 의 `playthrough_n`, `sessions.warning_count`/`banned_at`/`ban_reason`, `safety_events`. Approach C 스키마와 forward-compatible (ADD COLUMN/TABLE 로만 확장).

session_uuid 는 엔드포인트가 `uuid4()` 로 발급 (쿠키/save-code 없음). text[] 는 Postgres 네이티브 — SQLite stub 회피 (contract drift 방지).

## Alternatives Considered

- **A. ★ chosen** — 최소 스키마, deferral 명시.
- **B. Approach C 전체 스키마** — slice 범위 초과, 미사용 컬럼 다수.
- **C. SQLite/in-memory** — text[] 등가물 없음, throwaway + drift.

## Consequences

- `migrations/001_init.sql` = 2 테이블만.
- Sub-2b 가 ADD COLUMN/TABLE 로 확장 (이 ADR 의 forward-compat 약속).

## Related

- `docs/superpowers/specs/2026-05-30-phase-1-sub2-surigong-vertical-slice-design.md` Decision 2.
- mechanic-spec line 96-100 (전체 스키마), 565-573 (playthrough 마이그레이션 — Sub-2b).
