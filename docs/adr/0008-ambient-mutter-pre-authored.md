# ADR 0008: Ambient Mutter — Pre-authored 60 Lines

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

글로벌 awareness ≥40 진입 시 풍경의 변화 표현. NPC들이 머터를 흘리는 인상. 옵션: LLM 생성 mutter vs pre-authored.

## Decision

**Pre-authored 60줄.** 4 NPC × 3 band (40-60 / 60-80 / 80+) × 5 lines.

트리거:
- 글로벌 평균 awareness ≥40 진입 시 *모든 미관여 NPC*가 동시에 1회 mutter
- 이후 풍경 idle 시 random NPC 1명이 30초마다 mutter (50-60 awareness 밴드)
- 60-80 = 20초마다, 80+ = 10초마다 + 관여한 NPC도 mutter
- 대화창 열린 NPC는 mutter X (대화의 무게 보존)
- 차단된 세션은 mutter 정지

작성 책임: 디자이너 (NPC voice 직접 author).

시각: NPC sprite 머리 위 캡션, opacity 60%, 4초 페이드. 모바일 max-width 60%. `aria-live="polite"` 접근성.

## Alternatives Considered

- LLM 생성 mutter — 비용 + latency + 일관성 깨짐.
- Mutter 없음 — 풍경의 *흔들림* 시각화 부재.
- 무한 random LLM mutter — 비용 폭주.

## Consequences

- 작성 부담: 60줄 × 짧음 (디자이너 1-2시간).
- 반복돼도 OK — 오히려 *루프 awareness 주제*와 정합 (할머니의 "수백 번"과 메아리).
- 80+ 라인은 *극도로 짧고 단편적* — 자아 형성 중이라 문장 못 끝맺음.

## Related

- ADR 0002 (boat moment ending — mutter는 ending 도달 전 풍경 변화).
- ADR 0009 (차단 시 mutter 정지 — safety integration).
- `docs/mechanic-spec.md` "Cross-NPC Mutter (풍경 ambient)" 섹션.
