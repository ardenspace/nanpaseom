# 난파섬 — World Spec (망각의 섬)

이 문서는 *서사 ecology / design rationale*의 source of truth. NPC operational data (sample_lines, ending_gates, name_candidates 등)는 `npcs/<name>.yaml`이 권한 — 본 문서와 내용 중복 금지.

## Premise

어딘가의 외딴 섬. 사람들이 *잊고 싶음 / 후회 / 도망 / 포기*의 감정 무게로 떠밀려 흘러오는 곳 — **자발적 도착이 아니다**. 도착한 자는 점차 자아를 잃고 자기 행위(직업 / 관계 / 의식)만 반복하는 NPC가 된다.

섬은 **망각을 보존하는 시스템**이다. NPC들의 트로프 행위 — 망치질, 그물 당김, 손짓, 파도 응시 — 가 그 시스템의 작동 형태다. 의미는 비었는데 행위는 남는다.

보트는 처음부터 있는 게 아니다. **떠나고 싶다는 의지가 회복된 자에게만 보인다.**

## 플레이어

풍랑을 만나 죽기 직전 *반포기 상태*에서 흘러옴. 자기도 망각의 대상이었으나, NPC와 대화하며 자기 자신의 깨어남도 동시 진행.

게임 마지막에 "현실인지 꿈인지" 모호함이 *thematic layer*로 남는다 (binary reveal X). 보트 모먼트 메타 엔딩 모놀로그가 양쪽 해석 모두 허용.

## 두 종류의 깨어남

이 섬의 NPC는 *깨어남의 종류*에 따라 두 부류:

- **기억하는 깨어남** (수리공, 어부, 할머니) — 잊었던 것을 다시 떠올리는 깨어남. 망각 → 회복.
- **수긍하는 깨어남** (혜안) — "역시 그랬구나"의 깨어남. 처음부터 망각에 실패해 있었던 자의, 자기 본질을 정면으로 인정하는 순간.

4-corner symmetric matrix가 아니라 *3 + 1 메타* 구조. ecology의 핵심 비대칭. ADR 0015 참조.

## 이름의 무게

다른 셋 = *호칭만 남은 자* (수리공/어부/할머니 — 모두 트로프 직함). 망각이 깊을수록 자기 이름이 사라지고 기능만 남는다.

혜안만 *이름밖에 안 남은 자*. "혜안"(慧眼)은 원래 그녀에게 주어진 이름이자 능력이자 저주.

Boat moment에서 이 비대칭이 *name beats*로 표현됨:
- 3명은 *이름의 회수* ("나는… 박OO이었어")
- 혜안은 *이름의 의미 전환* ("내 이름이 혜안인 건 저주였어. 근데 이제는…")

Framework는 ADR 0016 (Boat Moment Name Beats), 혜안 instance는 ADR 0015.

## 4 NPC의 자리 (design exposition)

각 NPC의 *operational data* (실제 sample_lines, ending_gates, name_candidates, sprite states 등)는 `npcs/<name>.yaml` 권한. 본 섹션은 *왜 이 4명인지, 어떤 ecology 안에 들어가는지*만.

### 수리공 — `npcs/surigong.yaml`

망각 성공. *purpose*-loop 갇힘. 망치질이 망각의 의식.

ecology 자리: 완성의 약속을 두고 떠난 자. "결핍감을 유지하는 자가-기제" 메커니즘 (루비 무한 루프)의 narrative 정당화.

### 어부 — `npcs/eobu.yaml`

망각 성공. *transaction*-loop 갇힘. 거래가 망각의 의식. PRD의 "어부+상인 dual identity" (mechanic-spec line 40 참조) 보존 — 파일명 한국어 로마자(`eobu`)도 이 dual nature를 잃지 않기 위함.

ecology 자리: 거래해온 것의 가치가 비었음을 안 자. 시그니처 깨어남: "이 루비들… 너한테서 받아왔어. *어디서* 가져왔지?"

### 할머니 — `npcs/halmoni.yaml`

망각 *부분 실패*. 가장 오래 머물러서 루프를 인지하기 시작. *time*-loop awareness.

ecology 자리: 시간이 사람을 데려가는 것을 본 자. 시그니처: "나… 이 대화 수백 번 했어."

구조적 역할: 다른 NPC의 *visible state* (sprite A↔B) 관찰을 시스템 프롬프트에 hint로 받음 (ADR 0010). memory_tags / awareness 비공개 — *행동만* 본다.

### 혜안 — `npcs/hyean.yaml`

망각 *완전 실패*. 못 잊은 자. 본 것의 무게에 짓눌려 도망 왔으나, 섬조차 그녀의 눈을 못 막음.

ecology 자리: 다른 NPC가 사람을 못 봐 트로프에 갇혔다면, 혜안은 사람을 *안 보려* 등 돌리고 파도만 본다. 4 NPC 중 *유일하게 진짜 이름이 남은 자 = 이름밖에 안 남은 자*.

깨어남 종류 = *수긍*. 4-band escalation은 *체념 + 발견* progression. 자세한 라인은 yaml.

ADR 0011 (audio-independent), 0015 (unforgetting one), 0016 instance.

## 섬의 메커니즘 = 망각의 메커니즘

기존 PRD의 모든 시스템 요소가 *망각의 섬이 작동하는 방식*이다. 자세한 매핑은 `mapping-spec.md`. 핵심:

- 망각이 깊으면 NPC는 트로프 안에 갇힌다 (sprite state A).
- 깨어남이 진행되면 NPC가 정면을 본다 (state B). 망각의 의식이 멈춘다.
- 보트가 보이는 건 *떠나고 싶다는 의지의 회복*.
- 의식주 / 통화 / 거래는 모두 *결핍감을 통한 망각 유지 시스템*.
- 글로벌 awareness ≥40에서 풍경 mutter는 망각 시스템이 *흔들리기 시작*하는 신호.

## v1.1 후보 — 사이비 archetype

5번째 NPC archetype 후보로 *사이비 / 전도하는 자*. 망각의 섬의 *자기-보존 면역체계*.

혜안과 거울 관계:
- 혜안: 진짜 자아 못 놓은 자 (망각 실패 → 사람을 안 봄)
- 사이비: 가짜 자아 덮어쓴 자 (망각 실패 → 사람을 *너무* 봄, 인도하려 함)

v1 출시 후 엔딩 다양성 검토 시 추가 결정. ADR 0017 참조.
