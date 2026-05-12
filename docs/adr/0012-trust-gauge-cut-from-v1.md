# ADR 0012: Trust Gauge — Cut from v1

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

초기 PRD 안: awareness (0-100) + trust (0-100) 두 게이지 per NPC. trust = NPC가 player를 얼마나 신뢰하는지 (depth of opening vs depth of awakening, 두 직교 축).

## Decision

**Trust gauge 컷 from v1.** (awareness, memory_tags) 두 변수만으로 ending variety.

이유:
- LLM이 *다수 orthogonal scalar* 일관 출력 어려움. trust_delta가 awareness_delta와 동기화/충돌 케이스 빈번.
- 노이즈 증가 (LLM 출력에 변수 추가됨 = 검증 부담 증가).
- ending variety는 *awareness ending type × memory_tag 조합* + *boat outcome 5분기 × awakened subset combinatorial*로 이미 풍부.

v1.1 deferral: post-launch ending variety 분석 후 *너무 수렴*하면 trust 복귀.

## Alternatives Considered

- Trust 유지 — 위 LLM 일관성 / 노이즈 문제.
- 더 많은 게이지 (curiosity, fear, hope 등) — 솔로 dev scope 폭주.
- Trust를 *binary opening state*로 단순화 — 메커니즘 모호함.

## Consequences

- LLM JSON 출력 schema 단순 (awareness_delta + memory_tags + choices만).
- 시스템 프롬프트 짧음 (한 게이지만 설명).
- v1.1에서 trust 복귀 시 새 ADR + schema migration.

## Related

- ADR 0006 (memory_tags 10-vocab — ending variety의 두 번째 축).
- \`docs/mechanic-spec.md\` awakening mechanism 섹션.
