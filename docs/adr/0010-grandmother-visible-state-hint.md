# ADR 0010: Grandmother's Hint — Visible State Only

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

할머니가 다른 NPC의 변화를 인지하는 메커니즘 — "요즘 수리공이 이상해…" 류 cross-NPC hinting의 정보 source.

옵션: 풀 NPC state 공유 (memory_tags / awareness 숫자), visible state만, hint 없음.

## Decision

**다른 NPC의 *visible state* (sprite A/B) 만** system prompt hint로 주입. memory_tags / awareness 숫자 비공개.

할머니 시스템 프롬프트 빌더 (PRD 사양):
\`\`\`
[당신이 멀리서 본 풍경:]
- 수리공: {state==A ? "망치질을 하고 있다" : "망치를 놓고 너를 향해 서 있다"}
- 어부: ...
- 혜안: ...
{if any other NPC just_transitioned this turn or last:}
  ↑ 방금 변했음. 자연스럽게 한 마디 흘려도 좋다.
\`\`\`

- "방금 변했음" 부스트 = 직전 1-2턴 안.
- 할머니 자기가 state B 진입해도 다른 NPC 관찰 컨텍스트 유지.

## Alternatives Considered

- 풀 NPC state 공유 — 메타-자각 일관성 깨짐 (할머니가 *행동만 보는* 자라는 lore에 안 맞음).
- Hint 없음 — cross-NPC narrative 약함, "외로운 4 단독 캐릭터" 느낌.

## Consequences

- 메타-자각 일관성: 할머니는 *행동만* 본다, *기억을 읽지 못한다*.
- 빌더 (Phase 1.0+)가 \`visible_states_of_other_npcs\` + \`recent_transitions\` 변수 주입.
- 다른 NPC 작업 시 *할머니에게 어떻게 보일지*를 sprite state 차원에서 결정.

## Related

- ADR 0004 (visual system — sprite A/B가 정보 source).
- ADR 0011 (혜안의 audio-independent — 비슷한 "한정 정보" 원칙).
- \`docs/mechanic-spec.md\` "할머니의 Hint 메커니즘" 섹션.
