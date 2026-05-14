# ADR 0007: Replay Model (γ) — Per-Playthrough NPC State Reset

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

회차 모델 — 플레이어가 두 번째 회차에 들어왔을 때 NPC가 *전 회차 기억*을 가지고 있는지.

옵션:
- (α) 회차 자체 없음 (한 번 깨면 끝)
- (β) Full meta-memory — NPC가 이전 회차의 player 대화를 기억
- (γ) NPC state reset, 엔딩 저널만 누적

## Decision

**(γ)**. 회차마다 NPC awareness / memory_tags / chat_logs 모두 0으로 reset. 엔딩 저널 (`endings` 테이블) 만 누적.

- "+ 새 회차 시작" → 신규 NPC state row 생성. 이전 chat_logs는 DB 보존 (분석 / 튜닝용).
- "전체 초기화" → 해당 session_uuid 전체 row delete, 세이브 코드 무효화.

**서사적 환각으로서의 cross-play 인지**: 데이터상 NPC는 회차를 모른다. 그러나 할머니의 시그니처 "나… 이 대화 수백 번 했어"가 *어차피* 무한 회차를 가리킴. N번째 회차 플레이어 = "맞다, 이게 N번째다" 메타-기억이 *플레이어 안에서* 발생.

## Alternatives Considered

- (α) 회차 없음 — replay value 없음, 엔딩 5분기 활용도 낮음.
- (β) Full meta-memory — *데이터로 가치 검증 후* 결정. v1에서는 LLM 시스템 프롬프트에 회차 N hint 주입할지 *디자인 압력* 부족하고, 데이터 모델 복잡도 큼.

## Consequences

- v1 schema: `playthrough_n` 컬럼 추가 (sessions, npc_state, chat_logs).
- v1.1 deferral: full meta-memory.
- 할머니의 "수백 번" 시그니처가 *어차피* 메타-기억의 narrative 대안 역할.

## Related

- ADR 0010 (할머니 hint — 시간-루프 인지 활용).
- `docs/mechanic-spec.md` "Replay & Playthrough Model" 섹션.
