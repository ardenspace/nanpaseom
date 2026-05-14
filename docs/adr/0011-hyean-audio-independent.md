# ADR 0011: Hyean — Audio-Independent Awakening

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

PRD "What Makes This Cool" #5 — 혜안의 awakening trigger = *파도 audio loop* 인지. 그러나 모바일 자동재생 차단 환경에서 게임 깨짐. PRD Mobile Support 섹션의 "text-based cue fallback" 요구와 충돌.

## Decision

**오디오는 atmosphere QoL, 트리거 아님.** 혜안의 awakening은 *그녀의 대사 자체*가 자기충족 — 4-band escalation (poetic vague → mathematical → existential).

4-band escalation (PRD 사양):
- 0-30: "파도 소리는 늘 똑같지... 귀 기울여 봐" (poetic, vague)
- 30-60: "이상하지 않아? 매번 같은 박자야. 너도 알아챘어?" (pointed)
- 60-85: "7초. 정확히 7초마다 한 번. 너도 들리지?" (mathematical, uncanny)
- 85+: "파도가 진짜라면 이렇게 반복될 리 없어. 우리... 어디에 있는 거야?" (existential)

(★ 85+ 라인은 ADR 0015에서 *교체됨*: "이미 알고 있었어. 처음부터…")

모바일 첫-탭 오디오 활성화는 *시도만* — 강제 X. 안 활성화되어도 게임 진행 동등.

## Alternatives Considered

- 오디오 의존 — 모바일 자동재생 차단 환경에서 게임 깨짐.
- 모바일 fallback text cue (별도) — 두 가지 경로 유지 부담, 빌드 일관성 깨짐.
- 혜안 awakening 자체를 *다른 방식*으로 — narrative ecology 흔들림.

## Consequences

- NPC YAML에 \`hooks.audio_independent: true\` flag.
- 시스템 프롬프트에 4-band escalation 라인이 직접 들어감.
- 오디오 트랙 없이 100% 게임 진행 가능 → 솔로 dev 모바일 부담 경감.

## Related

- ADR 0006 (\`pattern\` memory_tag — 혜안용).
- ADR 0015 (혜안 lore 재해석 — 85+ 라인 교체).
- \`docs/mechanic-spec.md\` "혜안의 Audio-Independent Awakening" 섹션.
