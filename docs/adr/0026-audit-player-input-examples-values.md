# ADR 0026: `player_input_examples` 값 audit — player-voice 정합 (ADR 0022 후속)

- Status: Accepted
- Date: 2026-05-30
- Deciders: Arden, Claude (Sub-1 hand-synth Round 3 중 노출)

## Context

ADR 0022 는 `awakening_guidelines.*.examples` → `player_input_examples` 로 *키* 를 rename 해 "이 자리는 플레이어 입력 예시" 임을 명시했다. 그러나 *값* 은 audit 하지 않았다.

Sub-1 hand-synth Round 3 (어부 cell) 작성 중, 디자이너가 high_impact 자리를 yaml 에서 옮기지 않고 새 player 입력("당신이 해온 모든 일이 이미 짜여진 시스템 속에서 발생한 거라면요?")을 *지어냄* — 이 본능이 eobu yaml 의 기존 값이 player 입력이 아님을 드러냈다. hand-synth 검증 메커니즘이 작동한 사례.

## Audit 결과 (4 NPC × high/medium/low/decrease)

각 값이 *플레이어가 NPC 에게 하는 말(2인칭)* 인지 점검:

- **수리공** — 전부 player-voice. `"내가 준 루비 다 어디 갔어?"` 는 *플레이어가* 준 루비 관점(player→수리공 ruby 방향)이라 유효. **통과.**
- **어부** — high_impact `"이 루비들... 나는 *어디서* 가져온 거지?"` 가 **NPC 보이스** (`나는` = 어부). 게다가 이 줄은 `voice.awakening_bands[3].sample_lines` 의 collapse 대사와 *글자까지 동일* — NPC 대사를 player 슬롯에 복붙한 것. medium/low/decrease 는 통과. **high_impact 1건 위반.**
- **할머니** — 전부 player-voice. **통과.**
- **혜안** — 전부 player-voice. **통과.**

총 위반 = 1건 (어부 high_impact).

## Decision

어부 `awakening_guidelines.high_impact.player_input_examples` 를 player 2인칭으로 교체:

```
- "이 루비들... 나는 *어디서* 가져온 거지?"        # (삭제: NPC 보이스)
+ "당신이 해온 모든 일이 이미 짜여진 시스템 속에서 발생한 거라면요?"   # 디자이너 authoring, player 보이스
```

원래 의도(desc "거래의 대상이 비었음을 직격")는 보존 — "짜여진 시스템" = 가짜 거래 자각을 직격하는 player 도발. 나머지 3 NPC + 어부 medium/low/decrease 는 변경 없음.

## Alternatives Considered

- **A. ★ chosen** — audit 후 위반 1건만 수정. 통과한 값은 불변(불필요한 churn 차단).
- **B. 4 NPC 전 예시 일괄 재작성** — 통과한 값까지 건드림. 디자이너 voice 손상 + scope creep. Reject.
- **C. 값 유지, 빌더가 런타임에 voice 변환** — spec-driven verbatim 원칙 위반 (ADR 0022 와 동일 이유). Reject.

## Consequences

- `npcs/eobu.yaml` high_impact 1줄 교체. 다른 값 불변.
- 어부 collapse sample_line(`voice.awakening_bands[3]`)과 player 슬롯의 *우연한 동일성* 해소 — 두 자리가 이제 서로 다른 speaker.
- ADR 0022 의 "키 rename" 가 "값 audit" 로 닫힘. 향후 player_input_examples 추가 시 2인칭 player-voice 가 기준.
- (별개 noticed, 비-scope) 수리공 band[3] collapse sample_line `"내가 준 루비… 다 어디로 갔어"` 는 ruby 방향(수리공=수령자)상 어색할 수 있음 — player_input_examples audit 범위 밖이라 이 ADR 에서 처리 안 함. 후속 sample_line 리뷰 시 재검토 후보.

## Related

- ADR 0022 (키 rename) — 이 ADR 이 그 값 audit 로 닫음.
- `docs/superpowers/scratch/2026-05-29-hand-synth-round3-eobu-band-30-60.md` — 노출 지점.
- `docs/superpowers/plans/2026-05-14-phase-1-sub1-prompt-builder.md` Task 10.
