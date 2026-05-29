# ADR 0023: Builder injects `sample_lines` + `npc_tone` of current band, with "anchor only" instruction

- Status: Accepted
- Date: 2026-05-14
- Deciders: Arden, Claude (Sub-1 brainstorming session)

## Context

handoff line 98 의 미결정 — 빌더 가 awareness 70 (band 60-85) 시점 system prompt 에 무엇 박나? Round 2 손-합성 은 `npc_tone` 만 박았으나 (`docs/superpowers/scratch/2026-05-14-hand-synth-hyean-awareness70-round2.md`), `npcs/*.yaml` 의 `voice.awakening_bands[].sample_lines` 도 *operational data* — 빌더 가 무시 하면 yaml 정의 가 죽음. 동시에 LLM 이 sample_lines 를 *template* 으로 오해 → verbatim 복사 시 NPC 대사 반복 risk.

## Decision

빌더 = 현 band 의 `sample_lines` + `npc_tone` 둘 다 system prompt 에 박음. 동봉 instruction (모든 NPC 공통, `rules/prompt_skeleton.yaml` 에 위치):

> "이 sample_lines 는 NPC 보이스 의 *anchor* 다. tone calibration 용 — verbatim 복사 금지."

검증: snapshot test 가 sample_lines 박힘 verbatim 검사. Sub-2 의 LLM 출력 회귀 테스트 (Sub-2 plan 에서) 가 verbatim 복사 회귀 (NPC 가 sample_line 그대로 말함) 탐지.

## Alternatives Considered

- **A. ★ chosen** — 둘 다 + "anchor only" instruction.
- **B. `npc_tone` 만 박기** — yaml `sample_lines` operational data 무시. yaml 의 자기-충족성 위반.
- **C. 둘 다, instruction 없이** — LLM 의 verbatim 복사 risk 무방어.
- **D. Config flag 로 두고 Sub-2 empirical 결정** — spec 모호함 을 코드 if-then 으로 떠넘김. spec-driven 위반.

## Consequences

- `rules/prompt_skeleton.yaml` 의 Jinja template 에 sample_lines section + "anchor only" instruction 모두 포함.
- Property test 16 cell 마다 `assert all(line in output for line in npc.voice.awakening_bands[band_idx].sample_lines)` 검증.
- Sub-2 의 LLM 출력 회귀 테스트 spec 에 "NPC 발화 sample_lines verbatim 복사 ≤ N회/대화" invariant 추가 (Sub-2 plan 시 결정).

## Related

- handoff line 98 (이 결정 의 트리거)
- ADR 0021 (sample_lines 의 speaker 가 NPC 임을 명시 한 rename) — 이 결정 이 그 의미 활용.
- `docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md` "Decision 2".
