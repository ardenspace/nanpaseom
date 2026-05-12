# ADR 0004: Visual System — 4 NPC × 2 State = 8 Sprites (γ')

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

NPC의 awareness 진행을 어떻게 시각화. 옵션:
- (α) 1 sprite per NPC, 정적
- (β) 4 sprite per NPC (4밴드 미세 변화)
- (γ) 2 sprite per NPC, 60+ trigger 한 번에 전환
- (γ') γ 변형 — State B를 *플레이어를 향함*으로 명시

## Decision

**(γ') 4 NPC × 2 state = 8 sprite.**

- State A (awareness 0-60): NPC가 자기 트로프 행위 중
  - 수리공: 망치질
  - 어부: 그물 당김
  - 할머니: 앉은 채 손짓
  - 혜안: 등 돌리고 파도 응시
- State B (awareness 60+): 행위 정지 + 정면 응시 (player를 본다)
  - 수리공: 망치 놓고 정면
  - 어부: 그물 떨어뜨리고 정면
  - 할머니: 일어서거나 시선 전환
  - 혜안: 일어서서 돌아봄
- 전환 시점: awareness 60+ 도달 시 *한 번에*
- 전환 애니: 300ms cross-fade

## Alternatives Considered

- (α) 정적 1 sprite — awareness 시각화 불가.
- (β) 4 sprite per NPC — 솔로 dev 자산 부담 (32 sprite). 전/후 대비도 미세해서 *읽기 어려움*.
- (γ) State B를 *덜 구체*로 — "플레이어 향함" 명시 빠지면 모호.

## Consequences

- 자산 sourcing: CC0 픽셀 팩에서 State A baseline → 수동 픽셀 에딧으로 State B (Aseprite / Piskel). 캐릭터당 1-3시간, 4 NPC 합 약 8시간.
- Signature ending splash 5-6장은 별도 (AI 생성 활용 가능 — 캐릭터 일관성 무관 영역).

## Related

- ADR 0003 (navigation).
- ADR 0010 (할머니가 다른 NPC의 visible state = sprite A/B 만 본다).
- `docs/mechanic-spec.md` "Sprite system: (γ')" 섹션.
