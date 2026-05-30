# ADR 0024: `identity.system_prompt_persona_intro` yaml 필드 신설 + `rules/prompt_skeleton.yaml` 신설

- Status: Accepted
- Date: 2026-05-14
- Deciders: Arden, Claude (Sub-1 brainstorming session)

## Context

Round 2 손-합성 (`docs/superpowers/scratch/2026-05-14-hand-synth-hyean-awareness70-round2.md`) 의 [페르소나] section 안 prose 는 `npcs/hyean.yaml` 어디 에도 없음. 합성자 가 `current_display_name` + `name_status` + `state_a.description` + `backstory_summary` + 메타-게임 instruction ("플레이어 의 언행이 떠남 여부 결정") 을 *조립* 한 결과. 빌더 가 deterministic 으로 그 prose 를 재생산 하려면 *기계 가독 source* 필요.

또한 그 prose 안에 두 종류 정보 가 섞임:
- NPC-specific characterization (변함 — 혜안 의 시적 톤, 수리공 의 건조 톤 등)
- 게임 메타 instruction (모든 NPC 공통 — "플레이어 언행 ↔ 떠남")

Round 2 의 "마을 주민 중 유일하게 자신의 이름을 잊지 않았지만" 은 다른 NPC 의 `name_status` 와 의 비교 정보 — `hyean.yaml` 만 봐서는 도출 불가. 합성자 가 외부 컨텍스트 끌어옴.

## Decision

두 종류 정보 를 분리해 각자 의 권한 출처 에 둠.

**A. NPC-specific prose → `npcs/<name>.yaml` 의 `identity.system_prompt_persona_intro` 필드 신설** (verbatim string, 3-5 문장, 디자이너 authoring). 빌더 는 이 필드 를 prompt 에 *복붙* 만.

**B. 메타 instruction + Layer 3 메타-디펜스 + 시스템 프롬프트 sections order → `rules/prompt_skeleton.yaml` 신설** (Jinja2 template + literal instruction. 모든 NPC 공통). 빌더 는 이 skeleton 의 template variable 자리에 NPC yaml 필드 박음.

**C. 빌더 자체 는 어떤 prose 도 합성 X** — concat / verbatim copy 만. paraphrase 금지.

연관 작업 (별도 task — Phase B/C):
- 혜안 prose: Round 2 scratch 의 [페르소나] section 그대로 yaml 이관 (`hyean.yaml` 의 `identity.system_prompt_persona_intro`).
- 수리공/어부/할머니 prose: 신규 디자이너 authoring 필요 (Sub-1 plan 의 Phase B).
- Round 3 hand-synth 3 cell (수리공@0-30, 어부@30-60, 할머니@85+): persona_intro 사용 후 oracle 작성 (Phase C).

## Alternatives Considered

- **A. ★ chosen** — yaml 필드 + rules skeleton 분리.
- **B. 빌더 가 기존 필드 (`current_role_action` + `state_a.description` + `backstory_summary` 등) 로 template assemble** — paraphrase by builder. spec-driven 의 verbatim 원칙 위반. NPC 별 시적 톤 의 미묘함 손상.
- **C. 모두 `rules/prompt_skeleton.yaml` 안 Jinja template 에 변수 채움 식** — NPC 별 prose 톤 다양성 손상 (혜안 시적, 수리공 건조 등은 *prose 구조* 자체가 다름, 변수 substitution 으로 표현 어려움).

## Consequences

- 4 NPC yaml 모두 `identity.system_prompt_persona_intro` 필드 추가 (혜안 = Round 2 이관, 3 NPC = 신규 authoring).
- `rules/prompt_skeleton.yaml` 신설. Jinja2 template + Layer 3 메타-디펜스 + 메타-게임 instruction.
- 빌더 = skeleton + NPC yaml concat. 새 prose 합성 코드 X.
- 향후 5번째 NPC (사이비, v1.1) 추가 시 메타 instruction 자동 상속, NPC prose 만 신규.
- Round 3 hand-synth 3 cell 이 Sub-1 plan 의 첫 user-block phase 가 됨.

## Related

- `docs/superpowers/specs/2026-05-14-phase-1-sub1-prompt-builder-design.md` "Decision 3".
- `docs/superpowers/scratch/2026-05-14-hand-synth-hyean-awareness70-round2.md` — 혜안 prose 의 source.
- ADR 0015 / 0016 — 혜안 name_status 비대칭 의 배경 (메타 instruction "마을 주민 중 유일하게" 의 lore 근거).
- `docs/mechanic-spec.md` line 459 — Layer 3 메타-디펜스 mandate (skeleton 에 포함될 instruction).
