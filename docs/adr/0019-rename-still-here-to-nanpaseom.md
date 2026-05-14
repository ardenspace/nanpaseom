# ADR 0019: Rename "Still Here" → 난파섬 / Nanpaseom

- Status: Accepted (supersedes ADR 0001)
- Date: 2026-05-11
- Deciders: Arden

## Context

기존 PRD 출시명 **"Still Here"** (ADR 0001)는 2026-05-09 grilling 세션에서 락-인. 5개 ending 변종이 모두 "Still Here"의 literal 읽기로 수렴하는 구조.

새 망각의 섬 lore 도입 시점 (ADR 0014)에 Arden이 출시명 재검토. 결정: **난파섬** (영문 Nanpaseom 음차).

## Decision

- 한국어 출시명: **난파섬**
- 영문 출시명: **Nanpaseom** (음차)
- 코드네임: `nanpaseom` (이전 `ego-in-npc`)

이전 ADR 0001 ("Still Here")는 *Superseded*.

`docs/mechanic-spec.md`의 출시명 관련 섹션 (Premise 6, Hardening Log) 갱신은 별도 PR (Phase 0 외 housekeeping).

## Rationale

- "난파섬" = 글자 그대로 *난파된 자들의 섬*. 망각의 섬 lore와 직접 결합.
- "Still Here"는 grilling 시점에 영리한 dual-meaning이었으나, 한국어 화자에게는 영문 부제. 한국어 메인 타이틀 필요.
- "Nanpaseom"은 SEO 충돌 0. 한국어 검색에서 "난파섬"이 일반어이나 게임 컨텍스트에선 SEO 우위.

## Alternatives Considered

- (a) "Still Here" 영문 유지, 한국어만 "난파섬" — 두 언어 의미 격차.
- (b) ★ chosen — 한·영 모두 난파섬 / Nanpaseom 음차 단일화.
- (c) 영문 직역 (Wreck Island / Castaway Isle) — 음차보다 약함, generic.

## Consequences

- `docs/mechanic-spec.md` Premise 6 갱신 필요 (별도 PR — 본 ADR이 trigger).
- 모든 향후 마케팅 / 도메인 / README에서 난파섬 / Nanpaseom 사용.
- `ego-in-npc` 코드네임은 *역사적 흔적*. 새 코드네임 `nanpaseom`.

## Related

- ADR 0001 (Superseded by this).
- 상위 합의문: `docs/superpowers/specs/2026-05-11-...`.
