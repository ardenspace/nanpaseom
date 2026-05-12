# ADR 0013: NPC Roster — 4 Locked, 학생 Deferred to v2

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

PRD 초기 NPC 후보: 수리공, 어부, 할머니, 혜안, *학생* (5명). 학생은 *looping-dialogue* 트로프 — "오늘도 도서관 가는 길이에요"를 매일 반복.

솔로 dev 12-16주 scope + 4 × 2 sprite 자산 부담 (ADR 0004) + mutter 60줄 (ADR 0008) 고려.

## Decision

**v1 4 NPC lock: 수리공 (fetch-quest), 어부 (transactional), 할머니 (info-broker + time-loop), 혜안 (ambient + space-loop).**

학생 → **v2 deferral.**

근거:
- "looping-dialogue" 트로프는 *수리공의 fetch 루프*가 흡수 (루비 무한 루프 ≈ 동일 대화 반복).
- 할머니가 *cross-NPC hinting + 시간-루프 awareness* 둘 다 제공해서 학생의 메타-기능 자리 점령.

## Alternatives Considered

- 5 NPC (학생 추가) — sprite 10개, mutter 75줄, system prompt 5개. solo dev scope 폭주.
- 3 NPC (어부 또는 혜안 컷) — narrative ecology 빈약 (4 awakening axis 미완).

## Consequences

- v1 sprite 8개 (ADR 0004), mutter 60줄 (ADR 0008), 4 system prompt.
- 학생 archetype은 v2 후보로 보존.
- 사이비 archetype도 *같은 scope 이슈*로 v1.1 deferral (ADR 0017).

## Related

- ADR 0004 (4 × 2 = 8 sprite).
- ADR 0008 (4 × 3 × 5 = 60 mutter lines).
- ADR 0017 (사이비 v1.1 deferral — 같은 scope reasoning).
- \`docs/mechanic-spec.md\` Premise 5.
