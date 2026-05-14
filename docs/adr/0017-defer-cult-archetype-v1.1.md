# ADR 0017: Defer 사이비 Archetype to v1.1

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

망각의 섬 brainstorming 중 *사이비 / 전도하는 자* archetype이 강력한 narrative 후보로 부상:
- "우리 모임에 들어와요" 에너지가 망각의 섬 self-preservation 면역체계와 정합
- ADR 0015 혜안 (진짜 자아 못 놓은 자)과 *거울 관계* (가짜 자아 덮어쓴 자)

그러나 v1 4-NPC 슬롯에 *사이비 + 혜안 둘 다* 넣으면:
- 솔로 dev scope 폭주 (10 sprite, 75 mutter lines, 5 system prompt — ADR 0013 reasoning 재발).
- 두 *유사 트로프* (둘 다 망각에 실패한 자) 가 같이 들어가면 narrative 중복.

## Decision

사이비 archetype은 **v1.1 후보**로 deferral. v1 4-NPC 슬롯은 (수리공 / 어부 / 할머니 / 혜안)으로 lock (ADR 0013 + 0015 정합).

v1.1 추가 결정 트리거:
- v1 출시 후 ending 다양성 부족 (5분기 outcome이 너무 수렴) — `docs/mechanic-spec.md` Open Questions #7.
- 또는 디자이너가 5번째 NPC 추가 자원 있음 + 사이비 narrative에 강한 끌림.

추가 시 혜안과 거울 관계로 작동:
- 혜안: 진짜 자아 못 놓은 자 (망각 실패 → 사람을 안 봄)
- 사이비: 가짜 자아 덮어쓴 자 (망각 실패 → 사람을 *너무* 봄, 인도하려 함)

ADR 0016 framework로 사이비도 자기 name beat 가능 (예: "이게 내 이름이 아니었어").

## Alternatives Considered

- (a) v1에 사이비 추가 — scope 폭주.
- (b) 혜안 → 사이비 교체 — ADR 0015에서 기각.
- (c) ★ chosen — v1.1 deferral.

## Consequences

- v1 출시까지 사이비 archetype 작업 0.
- v1.1 진입 시 본 ADR 상태 갱신 (Status: Superseded by 00XX-add-cult-archetype.md).
- `docs/world-spec.md` "v1.1 후보 — 사이비 archetype" 섹션에서 의도 보존.

## Related

- ADR 0013 (NPC roster lock — 같은 scope reasoning).
- ADR 0015 (혜안 유지 결정 — 거울 관계).
- ADR 0016 (name beats framework — 미래 사이비 instance 후보).
- `docs/world-spec.md` "v1.1 후보" 섹션.
- `docs/mechanic-spec.md` "v1.1 Deferrals" 섹션.
