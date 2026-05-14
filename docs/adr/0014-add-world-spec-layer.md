# ADR 0014: Add World-spec Layer

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

기존 mechanic-spec (PRD)는 시스템 층위가 13개 grilling (ADR 0001-0013)으로 hardened되어 정밀하나 *서사 층위*가 비어있다. *왜* NPC가 트로프에 갇혀있는지, *왜* 플레이어는 떠나야 하는지의 동기 부여가 약해, 이전 레포에서 코드가 중구난방으로 짜이고 디자이너 멘탈 모델이 흔들림 → *학습 효용까지* 떨어진 게 root cause.

## Decision

`docs/world-spec.md`를 신설한다. **망각의 섬** 세계관 + 4 NPC `forgotten_life` 백스토리 *디자인 prose*를 담는다.

원칙:
- world-spec은 *서사 ecology / design rationale 권한*. mechanic-spec과 *독립적*으로 진화.
- mechanic / world의 정합은 `docs/mapping-spec.md`가 *제3의 권한*으로 보장.
- 메커니즘 변경 0. world-spec은 *해석 레이어*.
- world-spec과 yaml의 권한 경계: world-spec = 디자인 prose, yaml = LLM operational data. 내용 중복 금지 (ADR 0020 cross-review #1).

## Alternatives Considered

- (a) 기존 PRD 갈아엎고 새로 작성 — 13개 hardening cost 폐기. 12-16주 사이클 재시작. 학습 vehicle 손실.
- (b) ★ chosen — 메커니즘 그대로 + world-spec 신설 + mapping-spec 신설.
- (c) world를 mechanic-spec 안에 섹션으로 — 두 layer가 한 문서 안에 섞이면 *왜 이 메커니즘인지*가 명시화되지 못함. drift 위험.

## Consequences

- 향후 결정은 *세 spec 중 어느 권한인지*가 명시되어야 함.
- 메커니즘 변경 시 mapping-spec 동기화 의무.
- world-spec이 너무 강해져 메커니즘이 변경 압력 받으면 → ADR로 명시 후 변경.

## Related

- ADR 0001-0013 (기존 hardening — 이 ADR이 *추가*되는 결정).
- ADR 0020 (cross-review — 권한 경계 명시).
- `docs/world-spec.md` (산출물).
- `docs/mapping-spec.md` (제3의 권한).
