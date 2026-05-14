# ADR 0006: memory_tags 10-Tag Vocabulary

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

NPC의 누적 기억을 어떻게 모델링. 자유 텍스트 vs closed vocab.

초기 PRD 8 tags (family, loss, regret, pride, betrayal, home, fear, love) — 4 NPC 중 *혜안*과 *수리공/어부*의 collapse 어휘를 표현 못 함.

## Decision

**10-tag closed vocabulary** = 기존 8 + `pattern` + `purpose`.

- `pattern` — 혜안용 (perceptual/existential). 다른 NPC 관계 태그 (family/love)가 그녀와 안 맞음.
- `purpose` — 수리공 fetch-loop / 어부 transaction-loop collapse 핵심 어휘.

룰:
- 이 set 밖 태그는 *drop silently*.
- Max 3 tags per turn.
- Append-only, duplicates collapsed.

NPC affinity hints (LLM system prompt surface 우선):
- 수리공: purpose, regret, pride, betrayal
- 어부: purpose, pride, loss, regret
- 할머니: love, home, loss, family, pattern
- 혜안: pattern, fear, loss, home

## Alternatives Considered

- 자유 텍스트 tags — LLM 출력 일관성 깨짐, 분석 / ending gate 작성 까다로움.
- 8 tags 유지 — 혜안 / 수리공-어부 narrative collapse 어휘 부재.
- 더 큰 vocab (15-20) — schema 복잡도 증가, ending gate 조합 폭주.

## Consequences

- ending_gates가 *deterministic memory_tags*에 의존 가능.
- `rules/memory_tags.yaml`이 vocab의 권한.
- LLM 출력 검증에서 vocab 외 태그 silent drop.

## Related

- ADR 0011 (혜안 audio-independent — `pattern` 결과).
- `rules/memory_tags.yaml`.
- `docs/mechanic-spec.md` `memory_tags` vocab 섹션.
