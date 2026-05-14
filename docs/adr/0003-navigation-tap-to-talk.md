# ADR 0003: Navigation — Tap-to-talk Fixed Scene

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

NPC와 어떻게 상호작용하는지 3-way 분기: (a) 자유 이동 맵 (b) tap-to-talk 고정 풍경 (c) 메뉴 카드 list.

솔로 dev scope + 모바일 호환 + 망각의 섬의 "공간 안의 깨어남" 시각화 요구.

## Decision

**(b) tap-to-talk 고정 풍경**.

- 한 장의 섬 풍경에 4 NPC 배치
- Tap NPC → 대화창 모달
- 대화 종료 시 풍경 복귀
- 풍경 우측 *난파선 잔해* 배치 → ≥1 NPC ending 도달 시 *수리된 보트*로 modifier 토글

자유 이동은 v1.1+ deferral.

## Alternatives Considered

- (a) 자유 이동 맵 — 솔로 dev 자산 부담 폭증, 모바일 컨트롤 까다로움.
- (c) 메뉴 카드 list — 풍경의 *살아있는 환경*감 손실.

## Consequences

- 자산 부담 최소 (1 풍경 + 4 NPC × 2 sprite).
- "풍경이 awareness와 함께 awakening한다" 메커니즘 가능 (ADR 0008 mutter).
- v1.1에 자유 이동 추가 시 데이터 모델 호환 (NPC position 필드 신설).

## Related

- ADR 0004 (visual system 8 sprite).
- ADR 0008 (ambient mutter — 풍경 살아있음).
- `docs/mechanic-spec.md` "Scene & Visual System" 섹션.
