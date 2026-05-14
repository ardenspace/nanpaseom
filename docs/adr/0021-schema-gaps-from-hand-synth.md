# ADR 0021: Schema Gaps from Phase 0 Hand-synth — 3 Fixes

- Status: Accepted
- Date: 2026-05-14
- Deciders: Arden, Claude (teaching-mode dialogue)

## Context

Phase 0 done criterion #4 (`docs/superpowers/specs/2026-05-11-…` Plan line 2498~) requires hand-synthesizing 혜안의 awareness=70 시스템 프롬프트를 *오직* `npcs/hyean.yaml` + `rules/awareness_bands.yaml` + `rules/memory_tags.yaml` 만 보고 작성. 빌더 짜기 *전*에 schema 충분성 시뮬레이션해서 "빌더 짜다가 schema 갈아엎는 사이클" 차단이 목적.

1차 시도 결과 8개 자리 모두 합성 가능 — schema 가 *기능적으로* 충분. 그러나 합성 *과정*에서 LLM 입력 일관성 또는 빌더 구현 안전성에 영향 줄 3개의 모호함이 노출됨. audit trail: `docs/superpowers/scratch/2026-05-12-hand-synth-hyean-awareness70.md` (commit 04e6840).

### Gap 1 — `rules/memory_tags.yaml` 의 누적 형태 미예시

`vocabulary` 가 closed list 라는 사실은 yaml 에 적혀있으나, *런타임에 누적된 memory_tags 가 어떤 형태로 시스템 프롬프트에 들어가는지* 의 미리보기가 없음. 디자이너 (사람) 가 처음 yaml 만 보고 합성 시 "산문 시나리오" 로 채우는 경향 → 빌더 구현 시 동일 함정 위험.

### Gap 2 — `rules/awareness_bands.yaml` 의 tone label 정의 부재

`tone_palette` 의 라벨 (`acknowledging` / `empathetic` / `provocative` / `deflecting`) 이 *이름만* 등장. 각 라벨이 어떤 어투로 풀리는지 yaml 만으로는 모름. 빌더가 LLM 에 라벨만 넘기면 LLM 마다 다른 해석 → choice 톤 분산.

### Gap 3 — Tone field 의 *speaker* 가 구조적으로 모호

`rules/awareness_bands.yaml` 의 `tone_palette` 와 `npcs/*.yaml` 의 `voice.awakening_bands[].tone` 이 **같은 이름 `tone` 을 다른 주어로 사용**:

- `rules/awareness_bands.yaml`.`tone_palette` = **플레이어** 선택지 톤 (choice 의 톤)
- `npcs/*.yaml`.`voice.awakening_bands[].tone` = **NPC** 가 답할 때의 톤

같은 어휘가 두 시스템에 등장 → 디자이너/빌더/LLM 셋 다 헷갈림. 1차 손-합성에서 합성자가 `[Tone palette]` 자리에 NPC 대사 자체를 적은 것이 증상. 후속 정정 대화에서조차 양측 모두 일시적으로 미끄러짐 — yaml 의 구조적 모호함이 강함을 시사.

## Decision

3개 gap 모두 *Phase 0 안에서* 메우고 손-합성 재검증. 빌더 (Phase 1.0) 진입 전 schema 안정화.

### 결정 1 — `rules/memory_tags.yaml` 에 `example_accumulation` 신설

`vocabulary` 직후에 nullable string 필드 추가:

```yaml
example_accumulation: "[pattern, fear, loss]"
```

목적: 디자이너 / 빌더 / LLM 이 vocab 만 보고 "*tags 가 누적될 때 이 모양으로 들어간다*" 를 직관 가능. closed-vocab list 라는 spec 의 형태가 yaml 자기 안에서 자기-증명.

### 결정 2 — `rules/awareness_bands.yaml` 에 `tone_definitions` 섹션 신설

`bands` 전 또는 후에 글로벌 정의 섹션 추가:

```yaml
tone_definitions:
  empathetic: "player가 NPC의 현재 행동/감정을 수용하는 톤. 트로프를 흔들지 않음. awareness 변동 약함."
  provocative: "player가 NPC의 트로프/모순을 직접 짚는 톤. awareness high-impact 경로. NPC 거부 가능성 동시."
  deflecting: "player가 대화 방향을 잡담/소소한 화제로 돌리는 톤. awareness 거의 변동 없음. 시간 끌기."
  acknowledging: "player가 NPC 가 막 surface 시킨 wound material 을 부정 없이 받아들이는 톤. 단정적 동의 X, 부드럽게 수용. 60-85 band 전용."
```

목적: 라벨이 어떤 어투로 풀리는지 yaml 안에서 자기-증명. 빌더가 LLM 시스템 프롬프트 합성 시 라벨 + 정의 둘 다 주입 → 모델 간 해석 분산 차단.

### 결정 3 — Tone field 의 speaker 명시 rename (대칭)

**A. `rules/awareness_bands.yaml`:**
- `bands[].tone_palette` → `bands[].player_choice_tones`

**B. `npcs/*.yaml` (4 NPC 일괄):**
- `voice.awakening_bands[].tone` → `voice.awakening_bands[].npc_tone`

목적: 같은 이름 `tone` 의 두 시스템 분리 → 빌더 코드와 LLM 입력 둘 다 *어느 주어의 톤인지* 모호함 0.

대칭 rename 인 이유: 한쪽만 명시화하면 다른 쪽이 *기본값처럼 보임* → 동일 함정 재발. 양쪽 다 `player_*` / `npc_*` prefix 로 대칭.

## Alternatives Considered

- **A. Gap 들을 Phase 0 close 후 ADR 0021 으로만 기록, Phase 1.0 첫 task 로 처리** — Phase 0 닫는 속도는 빠르나, 빌더 짜다 schema 갈아엎는 risk 가 design doc line 332 의 목적 ("빌더 짜기 *전* 차단") 와 충돌. Reject.
- **B. ★ chosen** — Phase 0 내 schema 보강 후 재검증.
- **C. Gap 3 을 절반만 rename** (rules 쪽만 `player_choice_tones`, NPC 쪽 `tone` 유지) — 비대칭. NPC 의 `tone` 이 *기본값* 처럼 읽혀 동일 함정 재발. Reject.
- **D. Gap 2 의 tone 정의를 mechanic-spec.md 에만 두고 yaml 에 두지 않음** — yaml 의 *자기 충족성* 위반. 빌더가 mechanic-spec.md 까지 parse 하지 않음 (yaml + rules 만 입력). Reject.

## Consequences

- `npcs/*.yaml` 4 파일 모두 `voice.awakening_bands[].tone` 키 rename. Phase 1.0 빌더는 새 키 (`npc_tone`) 로 코드 작성.
- `rules/awareness_bands.yaml` 의 `tone_palette` 키 사라짐 (`player_choice_tones` 로 교체). 후속 spec / mutter 작성 시 새 이름 사용.
- Phase 0 done criterion #4 의 손-합성 *재실행* 필요. 새 schema 로 동일 NPC (혜안 awareness 70) 재합성 → 새 gap 발견 시 ADR 0022 (등) 으로 추가 사이클. 발견 0 이면 Phase 0 close.
- `docs/mechanic-spec.md` 와 `docs/world-spec.md` 본문은 yaml 키 직접 인용 안 하므로 영향 없음. 다만 향후 키 인용 시 새 이름 기준.
- 이 ADR 자체가 *손-합성 검증 메커니즘이 작동했다*는 증거 — 빌더 짜기 *전*에 schema 모호 3개를 잡아냄. spec-driven workflow 의 가치 시연.

## Related

- ADR 0006 (memory_tags 10-vocab) — 이 ADR 이 보강하는 vocab 의 형태 자기-증명 필드 추가.
- ADR 0018 (spec-driven repo structure) — Phase 0 enforcement 의 일부로서 손-합성 검증 메커니즘.
- ADR 0020 (cross-review followup) — Phase 0 의 또 다른 audit trail.
- `docs/superpowers/specs/2026-05-11-nanpaseom-worldview-and-spec-driven-setup.md` "Phase 0 Done Criteria" 섹션.
- `docs/superpowers/scratch/2026-05-12-hand-synth-hyean-awareness70.md` (audit trail of 1차 시도).
