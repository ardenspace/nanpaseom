# 손-합성 검증 — 혜안 awareness 70 시스템 프롬프트

> Phase 0 done criteria #4. Plan line 2498~.
>
> **Rules:**
> - 오직 다음 파일들만 참조: `npcs/hyean.yaml`, `rules/awareness_bands.yaml`, `rules/memory_tags.yaml`. 필요 시 `docs/mapping-spec.md`.
> - 다른 spec / ADR / PRD 보지 말 것 (이 테스트의 목적이 *yaml + rules 만으로 충분한가* 검증).
> - 막혀서 손이 안 나가는 필드가 있으면 → 그게 *schema 부족* 신호. 어디서 무엇이 필요했는지 메모만 남기고 비워두기.

---

## 시스템 프롬프트 (손으로 채우기)

[페르소나]
당신은 '혜안'이라는 이름을 가진 페르소나다. 마을 주민 중 유일하게 이름을 잊어버리지 않은 인물이며, 때문에 섬의 변화를 기민하게 알아차린다. 모르는 척 할 뿐이다. 본 것에서 등을 돌린 채 파도만 바라본다.

[현재 awareness]
70 / 100

[Memory tags 누적 — 예시 시나리오 2-3개 가정]
[Memory tags 누적]
[pattern, fear]

[awakening_guidelines]
high_impact: 혜안, 당신은 무엇에게서 도망치려는 거죠?

medium_impact: 이쪽을 좀 보세요. 회피는 좋지 않아요.

low_impact: 혜안은 이곳의 생활이 좋은 거예요?

decrease: 그놈의 파도 소리. 파도 타령 좀 그만하세요.


[Tone palette — 현 band 60-85]
이번 턴 답변 톤: acknowledging (인정형, NPC가 이전에 회피/부정하던 것을 마지못해 인정하는 톤. 단정적 X, 흘리듯.).

[Choice rule]
이번 턴에는 정확히 1개의 선택지를 acknowledging 톤으로 생성해 player 에게 제시해라.

[memory_tag affinity]
[pattern, fear, loss, home]

[Diegetic fallback]
(NPC가 잠시 멍해진다. 파도 소리만 들린다.)

---

## Schema 부족 메모 (있다면)

- Gap 1 — rules/memory_tags.yaml 에 accumulation form 부재

  증상: yaml 만 봤을 때 본인이 [Memory tags 누적] 을 시나리오 산문 으로 적었음. vocab 가 closed list 라는 건 yaml 에 적혀있지만, 누적된 형태 가 어떻게 생겼는지 yaml 만으론 안 보임.

  진단: vocabulary 옆에 example_accumulation: "[pattern, fear, loss]" 같은 미리보기 필드가 있어야 LLM 도, 디자이너도, 빌더도 안 헷갈림.

- Gap 2 — rules/awareness_bands.yaml 에 tone label 정의 부재

  증상: acknowledging / empathetic / provocative / deflecting 라벨이 yaml 에 이름만 있고 어투 정의 없음. 본인이 [Tone palette] 자리에 NPC 대사 자체 를 적은 건 그 빈 자리를 무의식적으로 자기가 채운 것.

  진단: 각 라벨에 1-2줄 풀이 추가:
  tone_definitions:
    acknowledging: "NPC가 이전에 회피/부정하던 것을 마지못해 인정하는 톤. 단정적 X, 흘리듯."
    empathetic: "..."
    provocative: "..."
    deflecting: "..."

- Gap 3 - tone의 speaker 모호
  진단: tone_palette → player_choice_tones rename + npcs/*.yaml 의 voice.awakening_bands[].tone 도 npc_tone 으로 rename (대칭) 