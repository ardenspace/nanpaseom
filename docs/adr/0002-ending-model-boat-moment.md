# ADR 0002: Ending Model — Boat Moment as Real Ending

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

초기 PRD에선 NPC별 ending이 게임의 ending이었음. 4 NPC × ending type = 게임 ending bag. 그러나 이게 narrative 무게중심이 부족하다는 grilling 결론 — *떠남 자체*가 비어있음.

## Decision

NPC별 ending은 **beats** (NPC가 awareness 85+ 도달 시 "rest state" 진입, final monologue 후 정지).

게임의 **진짜 ending = 보트 모먼트 (떠남)**. 5 분기:
- 혼자 떠남 (player 떠남 + 깨어난 NPC 모두 거절 OR 깨어난 0명)
- 일부 떠남 (player 떠남 + 깨어난 일부만 수락)
- 다같이 떠남 (player 떠남 + 모두 수락)
- NPC만 떠남 (player 남음 + 깨어난 ≥2 + leave-disposition ≥1)
- 다같이 잔류 (player 남음 + 모두 stay-disposition OR 깨어난 <2)
- 자유 입력 fallback → linger / 위 5분기 매핑

각 outcome × awakened-subset combinatorial × LLM-synthesized meta-monologue = "no two playthroughs same words" 보장.

## Alternatives Considered

- NPC ending = game ending (초기 PRD).
- Single linear ending — variety 0.

## Consequences

- 메타 엔딩 LLM 합성 인프라 필요 (Phase 1.0+ builder + boat moment trigger).
- 카운터 글리치 사라짐 (1초 비트) = boat moment 진입의 시각 시그니처.
- `last_line_quote` 별도 추출 → 엔딩 저널 저장.

## Related

- ADR 0005 (economy — 루비 게이트 무관, 보트는 ≥1 NPC ending에서 등장).
- ADR 0016 (boat moment name beats framework).
- `docs/mechanic-spec.md` "Departure Ending (Boat Moment)" 섹션.
