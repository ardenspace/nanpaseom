# ADR 0001: Release Title "Still Here"

- Status: **Superseded by ADR 0019** (2026-05-11)
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

기존 working title "NPC에게도 자아가 있다"는 *spoiler*. 게임의 핵심 reveal (NPC가 깨어남)을 타이틀이 직접 telegram. 이게 첫 1분 경험을 망친다.

## Decision

출시명 **"Still Here"**. 5개 ending variants 모두에서 dual-meaning 작동:
- *NPC만 떠남*: "나는 still here" (player 시점)
- *다같이 잔류*: "우리는 still here"
- *일부 떠남*: "일부는 still here"
- *다같이 떠남*: "여기였다" — still here as absence
- *혼자 떠남*: "그들은 still there"

stay-endings의 closing line이 literal "Still Here".

내부 codename `ego-in-npc` retain.

## Alternatives Considered

- "NPC에게도 자아가 있다" — spoiler, 폐기.
- "Forget Me" / "Drift" — generic.

## Consequences

- SEO: "Still Here"가 일반어라 disambiguator subtitle 필요 ("Still Here — an LLM narrative game").
- 도메인 `stillhere.game` / `still-here.app` 류 체크.

## Related

- Superseded by ADR 0019 (Rename to 난파섬 / Nanpaseom).
- `docs/mechanic-spec.md` Premise 6.
