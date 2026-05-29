# ADR 0022: Rename `awakening_guidelines.*.examples` → `player_input_examples`

- Status: Accepted
- Date: 2026-05-14
- Deciders: Arden, Claude (Sub-1 brainstorming session)

## Context

`npcs/*.yaml` 의 `awakening_guidelines.{high_impact,medium_impact,low_impact,decrease}.examples` 필드 가 *플레이어 입력 예시* (LLM 이 보고 awareness_delta 산정 가이드) 인데, 필드명 `examples` 는 모호. Phase 0 Round 1 손-합성 에서 합성자 가 NPC 대사 예시 로 오해함 (`docs/superpowers/scratch/2026-05-12-hand-synth-hyean-awareness70.md` 의 자리 확인). 빌더 시스템 프롬프트 의 라벨 도 yaml 키 따라 정해질 가능성 — 모호함 이 LLM 까지 전파 risk.

ADR 0021 의 `tone_palette` → `player_choice_tones` / `tone` → `npc_tone` 대칭 rename 패턴 과 동일 종류 의 speaker 명시화 gap.

## Decision

`npcs/*.yaml` 4 파일 × 4 sub-section (`high_impact` / `medium_impact` / `low_impact` / `decrease`) = 16 자리 의 `examples` 키 → `player_input_examples` 로 rename. 시맨틱 의미 변경 없음, 키 이름 만 speaker 명시화.

## Alternatives Considered

- **A. ★ chosen** — yaml 키 rename. ADR 0021 패턴 과 일관성.
- **B. yaml 키 유지, 빌더 코드 가 시스템 프롬프트 에 `Player input examples:` 라벨 변환** — spec-driven 의 verbatim 원칙 ("빌더 가 yaml string 을 paraphrase X") 위반. 라벨 가 yaml 안 에 박혀 있어야 함.
- **C. `awakening_guidelines` 컨테이너 자체 rename** (e.g., `player_input_impact_guide`) — scope creep. 컨테이너 자체는 모호 없음.

## Consequences

- 4 NPC yaml 파일 일괄 rename. 16 자리.
- 빌더 (Sub-1) 는 새 키 (`player_input_examples`) 로 코드 작성.
- `docs/mechanic-spec.md` / `world-spec.md` / `mapping-spec.md` 본문은 yaml 키 직접 인용 안 함 → 영향 없음.
- 후속 spec / 손-합성 작성 시 새 이름 기준.

## Related

- ADR 0021 (schema gaps from hand-synth) — 동일 speaker 명시 rename 패턴.
- `docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md` "Decision 1".
- `docs/superpowers/scratch/2026-05-12-hand-synth-hyean-awareness70.md` — 오해 의 audit trail.
