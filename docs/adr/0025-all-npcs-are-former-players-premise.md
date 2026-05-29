# ADR 0025: 난파섬 전제 락-인 — 모든 NPC는 과거 플레이어, 플레이어→NPC 루프 (authoring 캐논, 모호성 유지)

- Status: Accepted
- Date: 2026-05-29
- Deciders: Arden, Claude (Sub-1 persona authoring 중 노출)

## Context

Phase 1.0 Sub-1 의 persona authoring (plan Task 6-8) 중, 할머니 `system_prompt_persona_intro` 에 "사실은 가장 오래 머무른 플레이어" + 상실 대상 사람→외부 세계 변경이 들어옴. 표면상 `world-spec.md` 할머니 ecology (line 60 "시간이 사람을 데려가는 것을 본 자") 와 drift 로 보였음.

그러나 권한 문서 검토 결과, 기존 캐논이 이미 전제의 절반 이상을 담고 있었음:

- **Premise (world-spec line 7):** "도착한 자는 점차 자아를 잃고 자기 행위만 반복하는 NPC가 된다." → *도착 → 망각 → NPC화* 가 이미 캐논. 4 NPC 공통.
- **플레이어 (line 15):** "풍랑을 만나 죽기 직전 반포기 상태에서 흘러옴. **자기도 망각의 대상이었으나**, NPC와 대화하며 자기 자신의 깨어남도 동시 진행." → 플레이어와 NPC 가 *같은 계열*(흘러온 망각 대상)임을 이미 명시.

미명시였던 것 (이 ADR 이 락-인):
1. 도착자들이 구체적으로 *과거 플레이어 계열* 이라는 점.
2. 현 플레이어가 동일 계열의 *최신 도착자* 이며, 깨어나 떠나지 못하면 NPC 가 되어 다음 플레이어를 맞는 *루프가 닫힌다* 는 점.
3. 혜안의 *유지된 이름* 이 이 루프 구조를 드러내는 *핵심 힌트* 라는 점 (ADR 0015 비대칭의 메타-구조적 의미).

동시에 world-spec **line 17** 은 "마지막에 현실인지 꿈인지 모호함이 thematic layer 로 남는다 (**binary reveal X**)" 를 설계로 고정 — 이 전제가 *디제틱 노출* 되는지 *authoring 층 진실* 인지의 분기 발생.

## Decision

**1. 전제 락-인 (전체 NPC 범위).** 난파섬(원제 *망각의 섬*)의 도착자 = (대체로) 과거 플레이어. 4 NPC 전원이 섬을 떠나지 못하고 망각해 NPC 가 된 과거 플레이어다. 현 플레이어도 같은 계열의 최신 도착자이며, 깨어나 떠나지 못하면 NPC 가 된다 — *루프가 닫힌다*.

**2. 혜안의 이름 = 루프의 핵심 힌트.** 망각에 완전 실패한 자만이 "이름 가진 자아였다" 는 흔적을 남겨 구조를 드러낸다. ADR 0015 의 "혜안만 진짜 이름" 비대칭을 *메타-구조 단서* 로 승격.

**3. 할머니 = 가장 오래 머무른 도착자.** 가장 많은 도착/이탈을 관찰 → time-loop awareness 의 origin (ADR 0010 cross-NPC 관찰 역할과 정합). world-spec line 60 "시간이 사람을 데려가는 것을 본 자" 는 폐기 X, *재해석*: 오랜 세월 다른 도착자(플레이어)들이 떠나거나 사라지는 것을 지켜본 자 + 외부 세계와의 단절. 상실 대상 = 외부 세계 / 떠나간 자들 (core_wound `loss` 유지).

**4. 층위 = authoring/design 캐논, 모호성 유지.** 이 전제는 세계 안에서 *진실* 이며 작가/디자이너의 authoring 을 가이드한다. 그러나 게임은 이를 binary 로 노출하지 않는다 (line 17 유지). 디제틱 노출 금지 — 혜안의 이름, 할머니의 언질, 풍경 mutter 등은 *힌트* 수준에 머문다. 엔딩의 "꿈/현실 모호" 유지.

## Alternatives Considered

- **A. ★ chosen** — 전체 NPC + authoring 캐논 + 모호성 유지.
- **B. 할머니만 과거 플레이어** (Claude 초기 추천) — Premise(line 7) / 플레이어(line 15) 가 이미 *전원* becoming-NPC 를 담고 있음을 간과한 보수적 판단. 비대칭을 인위적으로 좁힘. Reject.
- **C. 전체 NPC, 디제틱 binary reveal** — line 17 의 "binary reveal X" thematic 설계 위반. 엔딩의 꿈/현실 모호성 파괴. Reject.
- **D. yaml 만 수정해 drift 봉합** (할머니 상실 대상을 사람으로 되돌림) — 캐논을 데이터에서 거꾸로 깎는 권한-경계 위반. 전제 손상. Reject.

## Consequences

- `docs/world-spec.md` Premise / 플레이어 / 할머니 섹션 갱신 — 도착자 = 과거 플레이어 계열 명시, 루프 close, 혜안 = 힌트 메타 역할, 할머니 재해석. 본문은 ecology / rationale 만, operational data 중복 금지 (world-spec line 3).
- 할머니 yaml (`system_prompt_persona_intro` / `forgotten_life.profession` / `backstory_summary`) 현행 유지 — 이제 world-spec 과 정합.
- 다른 3 NPC (수리공/어부/혜안) persona 는 *트로프 안에 머문 채로 유지* 가 올바름 — 그들은 잊었으므로 자신이 과거 플레이어였음을 모른다. 전제는 latent.
- 엔딩 설계 (보트 모먼트, 메타 모놀로그) 는 이 전제를 *힌트* 로만 활용. binary reveal 금지 재확인.
- 향후 NPC / 엔딩 / mutter 작성 시 이 전제가 톤 가이드. 디제틱 노출을 검토하게 되면 이 ADR 재방문.

## Related

- `docs/world-spec.md` Premise (line 7) / 플레이어 (line 15) / 모호성 (line 17) / 이름의 무게 (line 28-38).
- ADR 0014 (world-spec layer 신설), 0015 (혜안 unforgetting — 이 ADR 이 메타-힌트로 승격), 0016 (boat moment name beats), 0010 (할머니 cross-NPC hint — 가장 오래 머문 자 관찰 역할 정합).
- `docs/superpowers/plans/2026-05-14-phase-1-sub1-prompt-builder.md` Task 6-8 (이 결정의 트리거).
