# ADR 0015: Hyean as the Unforgetting One

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

기존 PRD에서 4 NPC 중 혜안만 *진짜 이름*이고 나머지 셋(수리공/어부/할머니)은 *트로프 직함*. 이 비대칭이 새 망각의 섬 lore (ADR 0014)와 충돌하는지 평가 필요.

초기 brainstorming에서 *혜안 → 사이비 archetype 교체*를 검토 (디자인 일관성 회복 목적). Arden이 강력한 반박: **"혜안만 진짜 이름이라는 비대칭은 디자인 bug가 아니라 lore feature"**.

## Decision

혜안을 *그대로 유지*. lore를 재해석:

- 다른 셋 = *호칭만 남은 자* (망각이 깊을수록 이름이 사라지고 기능만 남음)
- 혜안 = *이름밖에 안 남은 자* (망각 완전 실패 — 본 것의 무게에 짓눌려 도망 왔지만 섬조차 그녀의 눈을 못 막음)

혜안의 awakening = **수긍하는 깨어남** ("역시 그랬구나"). 다른 셋의 *기억하는 깨어남*과 종류가 다름. 4-corner symmetric matrix가 아니라 *3 + 1 메타* 구조.

PRD ADR 0011 4-band escalation의 85+ 라인 *교체*:
- 기존: "파도가 진짜라면 이렇게 반복될 리 없어. 우리... 어디에 있는 거야?" (세계 자각)
- 신규: **"이미 알고 있었어. 처음부터. 그저… 더 보고 싶지 않았던 거야."** (자기 자각)

0-30 / 30-60 / 60-85 라인은 *대사 유지*, 톤 라벨만 *체념 + 발견 progression*으로 명시.

NPC YAML에 `identity.name_status: "given"` + `identity.current_display_name: "혜안"` 명시.

## Alternatives Considered

- (a) 혜안 → 사이비 archetype 교체 — 초기 추천. Arden이 강한 reasoning으로 반박.
- (b) ★ chosen — 혜안 유지 + lore 재해석.
- (c) 5번째 NPC로 사이비 추가 (v1 5명) — solo dev scope 폭주 (ADR 0013, 0017).

## Consequences

- 혜안의 모든 톤 차이 (시적/차가운 대사, 등 돌린 자세, audio-loop 인지)가 lore-justified됨.
- Boat moment에서 혜안만 *이름 의미 전환* — ADR 0016 framework의 instance.
- 사이비 archetype은 v1.1 deferral (ADR 0017).
- 혜안의 `memory_tag_affinity` 유지 (pattern, fear, loss, home).

## Related

- ADR 0011 (audio-independent — 85+ 라인 교체로 partial supersession).
- ADR 0016 (boat moment name beats framework — 이 ADR의 혜안 instance가 framework로 일반화).
- ADR 0017 (사이비 v1.1 deferral — 거울 관계).
- `npcs/hyean.yaml` (산출물).
- `docs/world-spec.md` "혜안" 섹션.
