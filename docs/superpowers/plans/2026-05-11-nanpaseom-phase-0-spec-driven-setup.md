# 난파섬 Phase 0: Spec-driven Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **2026-05-11 갱신 (Cross-review applied):** ADR 0001 batch → 13개 historical ADRs 분리, 0003+0004 → 0015+0016 (framework + instance), NPC 파일명 한국어 로마자 통일, name_status enum 리팩토링, parse-check script + Phase 0 done criteria 추가. 총 33 task. ADR 0020 (cross-review followup)이 이 갱신의 audit trail.

**Goal:** 망각의 섬 세계관을 *spec-driven 구조*로 새 레포에 정착시킴. CLAUDE.md + 3-spec 문서 + 20 ADR (13 historical + 7 today) + 3 global rule YAML + 4 NPC YAML + 1 YAML parse-check script. 코드 7줄 (parse check만) — Phase 0는 *모든 narrative/lore가 데이터로 표현되고, 모든 결정이 ADR로 기록되는* 토대 만들기.

**Architecture:** 권한 경계가 명확함 — world-spec.md = 디자인 prose, yaml = LLM operational data, mapping-spec.md = 정렬 권한, ADR = 결정 audit trail. Phase 0 마지막에 *손-합성 검증*으로 schema 충분성 확인 → Phase 1.0 빌더 짜다가 schema 갈아엎는 사이클 차단.

**Tech Stack:** Markdown (spec / ADR / CLAUDE.md), YAML (NPC + rule data), Python 3 + pyyaml (parse check), git (audit trail).

---

## File Structure

| 파일 | 책임 |
|---|---|
| `CLAUDE.md` | Claude Code 룰 + enforcement 섹션 (Phase 0 vs Phase 1.0) |
| `scripts/check_yaml.py` | Phase 0 enforcement — 모든 yaml 파싱 sanity |
| `docs/mechanic-spec.md` | 기존 PRD 이관 |
| `docs/world-spec.md` | 디자인 prose (operational data 중복 X) |
| `docs/mapping-spec.md` | mechanic ↔ lore 매핑표 + drift 방지 룰 |
| `docs/adr/0001-release-title-still-here.md` | historical (superseded by 0019) |
| `docs/adr/0002-ending-model-boat-moment.md` | historical |
| `docs/adr/0003-navigation-tap-to-talk.md` | historical |
| `docs/adr/0004-visual-system-8-sprites.md` | historical |
| `docs/adr/0005-economy-fishing-rubies-infinite-loop.md` | historical |
| `docs/adr/0006-memory-tags-10-vocab.md` | historical |
| `docs/adr/0007-replay-model-state-reset.md` | historical |
| `docs/adr/0008-ambient-mutter-pre-authored.md` | historical |
| `docs/adr/0009-safety-4-layers-plus-2-strike.md` | historical |
| `docs/adr/0010-grandmother-visible-state-hint.md` | historical |
| `docs/adr/0011-hyean-audio-independent.md` | historical |
| `docs/adr/0012-trust-gauge-cut-from-v1.md` | historical |
| `docs/adr/0013-npc-roster-4-students-deferred-v2.md` | historical |
| `docs/adr/0014-add-world-spec-layer.md` | 오늘 |
| `docs/adr/0015-hyean-as-unforgetting-one.md` | 오늘 |
| `docs/adr/0016-boat-moment-name-beats-framework.md` | 오늘 (framework, generalized) |
| `docs/adr/0017-defer-cult-archetype-v1.1.md` | 오늘 |
| `docs/adr/0018-spec-driven-repo-structure.md` | 오늘 |
| `docs/adr/0019-rename-still-here-to-nanpaseom.md` | 오늘 (supersedes 0001) |
| `docs/adr/0020-cross-review-followup.md` | 오늘 (이 갱신 audit) |
| `rules/awareness_bands.yaml` | band → choice_count, tone palette |
| `rules/memory_tags.yaml` | 10-tag vocabulary + clamp |
| `rules/boat_outcomes.yaml` | 5분기 분류 규칙 |
| `npcs/surigong.yaml` | 수리공 — purpose-loop |
| `npcs/eobu.yaml` | 어부 — transaction-loop |
| `npcs/halmoni.yaml` | 할머니 — time-loop awareness |
| `npcs/hyean.yaml` | 혜안 — 못 잊은 자 |

---

## Task 1: CLAUDE.md 작성

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md content**

Write to `CLAUDE.md`:

```markdown
# 난파섬 (Nanpaseom) — Spec-driven Repo Rules

이 파일은 Claude Code가 이 레포에서 작업할 때 반드시 따라야 할 룰입니다.

## 권한 경계 (Authority Boundary)

같은 사실은 한 곳에만 적습니다. 변경 시 권한 문서만 수정.

- `docs/mechanic-spec.md` — 시스템 / 메커니즘 / 인프라 / 일정 권한
- `docs/world-spec.md` — 서사 ecology / design rationale (산문, 사람용)
- `docs/mapping-spec.md` — mechanic ↔ world 정렬 권한
- `npcs/<name>.yaml` — NPC operational data (LLM 시스템 프롬프트 입력)
- `rules/*.yaml` — global game rules

## 작업 전 컨텍스트 로드

코드 / spec / NPC YAML / rule YAML 수정 전, 항상 다음을 읽으세요:

- 영향받는 `docs/*-spec.md` 섹션
- 영향받는 `npcs/*.yaml` / `rules/*.yaml`
- 관련된 `docs/adr/*.md` 결정 기록

## NPC 추가 / 수정 룰

- NPC 대사 / 톤 / `forgotten_life` 추가는 `npcs/*.yaml`에만. **코드에 하드코딩 금지**.
- 시스템 프롬프트는 **빌더가 YAML에서 생성** (Phase 1.0+). 직접 작성 / 수정 금지.
- NPC 새 결정 (e.g. memory_tag affinity 변경) 시 ADR 작성 후 YAML 갱신.

## 메커니즘 변경 룰

- 메커니즘 변경 시 `docs/mechanic-spec.md` + `docs/mapping-spec.md` **둘 다** 갱신.
- mapping-spec.md의 해당 행 갱신 누락 = drift, 리뷰 reject.

## 새 결정 룰

새 디자인 결정 / 락-인된 trade-off 발생 시:
1. "ADR 거리인가?" 자문
2. ADR이라면 `docs/adr/NNNN-<topic>.md` 작성 (4자리 숫자, 시퀀셜)
3. ADR 작성 후 영향받는 spec / YAML 갱신
4. commit per ADR (audit trail)

## YAML 스키마

YAML은 *기계 가독 spec*. 다음 룰:

- `npcs/*.yaml` 최상위 키: `identity`, `sprite`, `voice`, `memory_tag_affinity`, `ending_gates`, `awakening_guidelines`, `diegetic_fallback` 필수
- `identity.name_status`: `forgotten | given | reclaimed` enum
- `identity.current_display_name`: nullable string
- `rules/*.yaml` — 각 룰 파일은 자체 스키마 (Phase 1.0 빌더 구현 시 jsonschema 형식화)
- YAML 추가 / 수정 후 *모든 YAML 파싱*: `python3 scripts/check_yaml.py`

## Enforcement (Phase 0 vs Phase 1.0)

**Phase 0 (현재):**
- `scripts/check_yaml.py` — 모든 yaml 파싱 OK. 위반 시 commit reject 권장 (pre-commit 훅은 디자이너 선택).
- 이 CLAUDE.md 룰 — 사람을 위한 명시화. 빌드는 안 깨지지만 협업 흐름의 베이스라인.

**Phase 1.0 (빌더 도입 시 추가):**
- YAML 스키마 검증 (pydantic / jsonschema) — 빌더가 fail-fast.
- "코드 내 NPC 대사 하드코딩 금지" pre-commit grep 룰.
- `mapping-spec.md` PR 체크리스트 (PR_TEMPLATE.md 또는 CI 룰).
- 시스템 프롬프트 누설 키워드 차단 (PRD Layer 4와 연결).

## Git 룰

- commit은 *logical unit per file* (NPC 1개 추가 = 1 commit, ADR 1개 = 1 commit).
- commit 메시지는 한국어 OK. 결정 *이유*가 명시되어야 함.
- 절대 `git commit --no-verify` / `--no-gpg-sign` 사용 금지.

## 학습 메타-룰

이 프로젝트는 **spec-driven workflow** 학습 vehicle입니다. 다음을 우선:

- 손빠른 우회보다 **명시적 spec 흐름**
- 결정은 **기록**된다 (ADR)
- spec이 **코드를 생성**한다 (시스템 프롬프트 빌더, Phase 1.0+)
- 게임 밸런스 튜닝은 **코드 수정이 아니라 YAML 수정**

## 참조 문서

- 상위 합의문: `docs/superpowers/specs/2026-05-11-nanpaseom-worldview-and-spec-driven-setup.md`
- 실행 plan: `docs/superpowers/plans/2026-05-11-nanpaseom-phase-0-spec-driven-setup.md`
- 메커니즘 권한: `docs/mechanic-spec.md`
- 서사 권한: `docs/world-spec.md`
- 정렬 권한: `docs/mapping-spec.md`
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
Add CLAUDE.md — spec-driven repo rules + enforcement

권한 경계 (mechanic/world/mapping/yaml), NPC 룰, ADR 룰,
Phase 0/1.0 enforcement 구분. spec-driven workflow 학습 vehicle 룰.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: 기존 PRD를 docs/mechanic-spec.md로 이관

**Files:**
- Move: `arden-main-design-20260424-014454.md` → `docs/mechanic-spec.md`

- [ ] **Step 1: Move file** (PRD untracked이므로 일반 `mv`)

```bash
mv arden-main-design-20260424-014454.md docs/mechanic-spec.md
```

- [ ] **Step 2: Verify**

Run: `wc -l docs/mechanic-spec.md`

Expected: 705 lines.

- [ ] **Step 3: Commit**

```bash
git add docs/mechanic-spec.md
git commit -m "$(cat <<'EOF'
Move PRD to docs/mechanic-spec.md

기존 hardened mechanic PRD를 docs/ 하위로 이관. 내용 그대로 보존.
시스템 / 메커니즘 / 인프라 / 일정 권한 spec.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: docs/world-spec.md 작성 (디자인 prose, operational X)

**Files:**
- Create: `docs/world-spec.md`

이 문서는 *디자이너 prose*. NPC operational data는 yaml 권한이므로 *내용 중복 금지*. world-spec은 *왜 이 lore인가*만.

- [ ] **Step 1: Write world-spec.md content**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add docs/world-spec.md
git commit -m "$(cat <<'EOF'
Add docs/world-spec.md — design exposition (망각의 섬)

서사 ecology + design rationale. NPC operational data는 yaml 권한.
중복 금지 원칙 명시. 두 종류 깨어남, 이름의 무게, 4 NPC ecology 자리.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: docs/mapping-spec.md 작성

**Files:**
- Create: `docs/mapping-spec.md`

- [ ] **Step 1: Write mapping-spec.md content**

```markdown
# 난파섬 — Mapping Spec (Mechanic ↔ Lore)

이 문서는 *정렬 권한* spec. `mechanic-spec.md` (시스템)와 `world-spec.md` (서사)의 정합을 보장한다.

## Mapping Table

| Mechanic (PRD) | Lore (망각의 섬) |
|---|---|
| Shipwreck frame (플레이어가 난파선으로 도착) | 반포기 상태로 떠밀려옴 (자발 X) |
| NPC가 트로프에 갇힘 | 망각의 의식(ritual)이 자아의 빈자리를 채움 |
| Awareness gauge 0-100 | 잃어버린 자아의 복원도 |
| memory_tags 10종 | 도망쳐 온 원래 삶의 파편 |
| 3→2→1→0 UI 축소 | 주어진 선택지가 줄고 *자기 언어*가 회복됨 |
| 보트 5분기 엔딩 | "떠나고 싶은 의지"의 회복 양상 |
| 보트는 ≥1 NPC awareness 85+에 등장 | 보트는 *의지가 있는 자에게만 보임* |
| 루비 무한 루프 (수리공 "더 필요해") | 결핍감으로 망각을 유지하는 자가-기제 |
| 카운터 글리치 사라짐 (boat moment) | 결정 순간에 환각이 무너짐 |
| 글로벌 awareness ≥40 mutter | 망각 시스템이 *흔들리기 시작*하는 신호 |
| Sprite state A → B 전환 (awareness 60+) | 망각의 의식이 멈춤. *처음으로 정면을 본다* |
| 할머니의 시각적 hint (다른 NPC state A↔B 관찰) | 가장 오래 머문 자가 *루프의 가장자리*를 본다 |
| 혜안의 4-band escalation | 사람을 안 보려 했던 자가 *처음으로 동행을 발견*하는 과정 |
| Boat moment 이름 beat (3 회수 + 1 의미 전환) | 망각된 자의 이름 복원 vs 못 잊은 자의 의미 전환 (ADR 0015, 0016) |
| 자유 입력 안전 4-layer + 2-strike | 섬의 *유한한 인내심* — 의지 회복하러 온 자에게는 응답, 파괴하러 온 자에게는 차단 |
| 회차 (playthrough) 모델 | 섬은 끝없이 다른 사람을 받아들임. *플레이어*는 회차마다 새 인격 |
| 할머니의 시그니처 "나… 이 대화 수백 번 했어" | 가장 오래 머문 자만이 *루프 자체*를 감지함 |

## Drift 방지 룰

이 매핑은 *살아있다*. 변경 룰:

1. 메커니즘 신규 추가 / 변경 → 이 표에 행 추가 / 갱신
2. lore 신규 추가 / 변경 → 이 표에 행 추가 / 갱신
3. 표에 *없는 메커니즘이 발견되면* → drift. 둘 중 하나:
   - 메커니즘이 lore 없이도 정당화되면 → 아래 "미매핑 항목"으로 명시 추가
   - 그렇지 않으면 → lore 추가 or 메커니즘 제거
4. PR에서 `mechanic-spec.md` / `world-spec.md` 변경이 있는데 `mapping-spec.md`가 변경되지 않았다면 → 리뷰 reject

이 룰은 *암묵적 표류 금지*가 목적.

## 미매핑 항목 (의도적)

다음은 *lore 의미 없이* 메커니즘 자체의 implementation detail:

- LLM 백엔드 tiered failover (PRD Premise 4)
- Postgres 스키마
- Mac Mini / Cloudflare Tunnel 인프라
- Mobile responsive layout
- CC0 픽셀 아트 sourcing

이들은 망각의 섬 lore와 무관한 *제작 결정*. mapping table은 *게임 안에서 플레이어가 경험하는 메커니즘*에 한정.
```

- [ ] **Step 2: Commit**

```bash
git add docs/mapping-spec.md
git commit -m "$(cat <<'EOF'
Add docs/mapping-spec.md — mechanic ↔ lore 정렬 권한

매핑 표 + drift 방지 룰. 메커니즘/lore 변경 시 이 표 동기화 필수.
미매핑 항목 (인프라/배포)은 명시적으로 분리.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: ADR 0001 — Release Title "Still Here" (historical)

**Files:**
- Create: `docs/adr/0001-release-title-still-here.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0001: Release Title "Still Here"

- Status: **Superseded by ADR 0019** (2026-05-11)
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

기존 working title "NPC에게도 자아가 있다"는 *spoiler*. 게임의 핵심 reveal (NPC가 깨어남)을 타이틀이 직접 telegram. 이게 첫 1분 경험을 망친다.

## Decision

출시명 **"Still Here"**. 5개 ending variants 모두에서 dual-meaning 작동:
- *NPC만 떠남*: "나는 still here" (player 시점)
- *다같이 잔류*: "우리는 still here"
- *일부 떠남*: "일부는 still here"
- *다같이 떠남*: "여기였다" — still here as absence
- *혼자 떠남*: "그들은 still there"

stay-endings의 closing line이 literal "Still Here".

내부 codename `ego-in-npc` retain.

## Alternatives Considered

- "NPC에게도 자아가 있다" — spoiler, 폐기.
- "Forget Me" / "Drift" — generic.

## Consequences

- SEO: "Still Here"가 일반어라 disambiguator subtitle 필요 ("Still Here — an LLM narrative game").
- 도메인 `stillhere.game` / `still-here.app` 류 체크.

## Related

- Superseded by ADR 0019 (Rename to 난파섬 / Nanpaseom).
- `docs/mechanic-spec.md` Premise 6.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0001-release-title-still-here.md
git commit -m "Add ADR 0001 — release title 'Still Here' (historical, superseded)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: ADR 0002 — Ending Model: Boat Moment as Real Ending

**Files:**
- Create: `docs/adr/0002-ending-model-boat-moment.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0002: Ending Model — Boat Moment as Real Ending

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

초기 PRD에선 NPC별 ending이 게임의 ending이었음. 4 NPC × ending type = 게임 ending bag. 그러나 이게 narrative 무게중심이 부족하다는 grilling 결론 — *떠남 자체*가 비어있음.

## Decision

NPC별 ending은 **beats** (NPC가 awareness 85+ 도달 시 "rest state" 진입, final monologue 후 정지).

게임의 **진짜 ending = 보트 모먼트 (떠남)**. 5 분기:
- 혼자 떠남 (player 떠남 + 깨어난 NPC 모두 거절 OR 깨어난 0명)
- 일부 떠남 (player 떠남 + 깨어난 일부만 수락)
- 다같이 떠남 (player 떠남 + 모두 수락)
- NPC만 떠남 (player 남음 + 깨어난 ≥2 + leave-disposition ≥1)
- 다같이 잔류 (player 남음 + 모두 stay-disposition OR 깨어난 <2)
- 자유 입력 fallback → linger / 위 5분기 매핑

각 outcome × awakened-subset combinatorial × LLM-synthesized meta-monologue = "no two playthroughs same words" 보장.

## Alternatives Considered

- NPC ending = game ending (초기 PRD).
- Single linear ending — variety 0.

## Consequences

- 메타 엔딩 LLM 합성 인프라 필요 (Phase 1.0+ builder + boat moment trigger).
- 카운터 글리치 사라짐 (1초 비트) = boat moment 진입의 시각 시그니처.
- `last_line_quote` 별도 추출 → 엔딩 저널 저장.

## Related

- ADR 0005 (economy — 루비 게이트 무관, 보트는 ≥1 NPC ending에서 등장).
- ADR 0016 (boat moment name beats framework).
- `docs/mechanic-spec.md` "Departure Ending (Boat Moment)" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0002-ending-model-boat-moment.md
git commit -m "Add ADR 0002 — boat moment as real ending (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: ADR 0003 — Navigation: Tap-to-talk Fixed Scene

**Files:**
- Create: `docs/adr/0003-navigation-tap-to-talk.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0003: Navigation — Tap-to-talk Fixed Scene

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

NPC와 어떻게 상호작용하는지 3-way 분기: (a) 자유 이동 맵 (b) tap-to-talk 고정 풍경 (c) 메뉴 카드 list.

솔로 dev scope + 모바일 호환 + 망각의 섬의 "공간 안의 깨어남" 시각화 요구.

## Decision

**(b) tap-to-talk 고정 풍경**.

- 한 장의 섬 풍경에 4 NPC 배치
- Tap NPC → 대화창 모달
- 대화 종료 시 풍경 복귀
- 풍경 우측 *난파선 잔해* 배치 → ≥1 NPC ending 도달 시 *수리된 보트*로 modifier 토글

자유 이동은 v1.1+ deferral.

## Alternatives Considered

- (a) 자유 이동 맵 — 솔로 dev 자산 부담 폭증, 모바일 컨트롤 까다로움.
- (c) 메뉴 카드 list — 풍경의 *살아있는 환경*감 손실.

## Consequences

- 자산 부담 최소 (1 풍경 + 4 NPC × 2 sprite).
- "풍경이 awareness와 함께 awakening한다" 메커니즘 가능 (ADR 0008 mutter).
- v1.1에 자유 이동 추가 시 데이터 모델 호환 (NPC position 필드 신설).

## Related

- ADR 0004 (visual system 8 sprite).
- ADR 0008 (ambient mutter — 풍경 살아있음).
- `docs/mechanic-spec.md` "Scene & Visual System" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0003-navigation-tap-to-talk.md
git commit -m "Add ADR 0003 — tap-to-talk fixed scene navigation (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: ADR 0004 — Visual System: 8 Sprites (γ')

**Files:**
- Create: `docs/adr/0004-visual-system-8-sprites.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0004: Visual System — 4 NPC × 2 State = 8 Sprites (γ')

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

NPC의 awareness 진행을 어떻게 시각화. 옵션:
- (α) 1 sprite per NPC, 정적
- (β) 4 sprite per NPC (4밴드 미세 변화)
- (γ) 2 sprite per NPC, 60+ trigger 한 번에 전환
- (γ') γ 변형 — State B를 *플레이어를 향함*으로 명시

## Decision

**(γ') 4 NPC × 2 state = 8 sprite.**

- State A (awareness 0-60): NPC가 자기 트로프 행위 중
  - 수리공: 망치질
  - 어부: 그물 당김
  - 할머니: 앉은 채 손짓
  - 혜안: 등 돌리고 파도 응시
- State B (awareness 60+): 행위 정지 + 정면 응시 (player를 본다)
  - 수리공: 망치 놓고 정면
  - 어부: 그물 떨어뜨리고 정면
  - 할머니: 일어서거나 시선 전환
  - 혜안: 일어서서 돌아봄
- 전환 시점: awareness 60+ 도달 시 *한 번에*
- 전환 애니: 300ms cross-fade

## Alternatives Considered

- (α) 정적 1 sprite — awareness 시각화 불가.
- (β) 4 sprite per NPC — 솔로 dev 자산 부담 (32 sprite). 전/후 대비도 미세해서 *읽기 어려움*.
- (γ) State B를 *덜 구체*로 — "플레이어 향함" 명시 빠지면 모호.

## Consequences

- 자산 sourcing: CC0 픽셀 팩에서 State A baseline → 수동 픽셀 에딧으로 State B (Aseprite / Piskel). 캐릭터당 1-3시간, 4 NPC 합 약 8시간.
- Signature ending splash 5-6장은 별도 (AI 생성 활용 가능 — 캐릭터 일관성 무관 영역).

## Related

- ADR 0003 (navigation).
- ADR 0010 (할머니가 다른 NPC의 visible state = sprite A/B 만 본다).
- `docs/mechanic-spec.md` "Sprite system: (γ')" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0004-visual-system-8-sprites.md
git commit -m "Add ADR 0004 — 8 sprites visual system γ' (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: ADR 0005 — Economy: Fishing + Rubies + Infinite Repair Loop

**Files:**
- Create: `docs/adr/0005-economy-fishing-rubies-infinite-loop.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0005: Economy — Light Fishing + Single Currency 루비 + Infinite Repair Loop

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

순수 대화만 있으면 *잔류 ending*의 emotional weight가 약함. 플레이어가 "남는다"를 *진짜로 선택할 수 있는* 컴포트 활동 필요.

동시에 *트로프 collapse*의 시그니처 모먼트가 경제 메커니즘으로부터 자연 출현하면 narrative ecology가 강해짐.

## Decision

**라이트 1-tap 낚시 + 단일 통화 "루비".**

- 풍경 부두 영역 탭 → 낚시 모드. 찌가 가라앉는 순간 탭 → "잡았다!" 5-15초 단발 비트, 무한 반복.
- 어부 [물고기 줄게] → 🔴 +1. 수리공 [루비 줄게 (현재 N개)] → 🔴 -1 + "더 필요해…"
- **수리공 무한 루프**: 절대 충족 X. 보트 수리는 루비로 트리거되지 않음 (≥1 NPC ending에서 등장 — ADR 0002).
- 루비를 어디에도 못 씀. 그냥 *쌓임*.
- **트로프 collapse 시그니처**: 어부 각성 모먼트 = "이 루비들… 너한테서 받아왔어. *어디서* 가져왔지?"
- **카운터 글리치 사라짐**: boat moment 진입 직후 1초 비트 (stutter 200ms → 흐려짐 500ms → 사라짐 300ms). *결정 순간에 화폐의 환각이 무너짐.*

LLM 시스템 프롬프트 hint: 어부/수리공 system prompt에 `player_total_rubies_given_to_this_npc: N` 변수 주입. LLM이 누적량 보고 자연스럽게 awareness_delta 가중.

## Alternatives Considered

- 컴포트 활동 없음 — 잔류 ending 무게 부족.
- 복수 통화 (낚시 + 농사 + 채광) — solo dev scope 폭주.
- 루비로 보트 수리 게이트 — narrative ecology 깨짐 (보트는 *의지의 회복*이지 *재화의 축적*이 아님).

## Consequences

- NPC YAML에 `hooks.system_prompt_variables` (player_total_rubies_*) 필드.
- 카운터 글리치는 boat moment 진입의 *시각 시그니처* (ADR 0002와 정합).
- 게임 내내 루비 카운터 *안정적*으로 보임 = "있는 척"이 *결정 순간에만 무너짐*.

## Related

- ADR 0002 (boat moment as ending — 보트 트리거는 루비와 무관).
- `docs/mechanic-spec.md` "Fishing & 루비 Economy" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0005-economy-fishing-rubies-infinite-loop.md
git commit -m "Add ADR 0005 — economy (fishing + rubies + infinite loop) (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: ADR 0006 — memory_tags 10-Tag Vocabulary

**Files:**
- Create: `docs/adr/0006-memory-tags-10-vocab.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0006: memory_tags 10-Tag Vocabulary

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

NPC의 누적 기억을 어떻게 모델링. 자유 텍스트 vs closed vocab.

초기 PRD 8 tags (family, loss, regret, pride, betrayal, home, fear, love) — 4 NPC 중 *혜안*과 *수리공/어부*의 collapse 어휘를 표현 못 함.

## Decision

**10-tag closed vocabulary** = 기존 8 + `pattern` + `purpose`.

- `pattern` — 혜안용 (perceptual/existential). 다른 NPC 관계 태그 (family/love)가 그녀와 안 맞음.
- `purpose` — 수리공 fetch-loop / 어부 transaction-loop collapse 핵심 어휘.

룰:
- 이 set 밖 태그는 *drop silently*.
- Max 3 tags per turn.
- Append-only, duplicates collapsed.

NPC affinity hints (LLM system prompt surface 우선):
- 수리공: purpose, regret, pride, betrayal
- 어부: purpose, pride, loss, regret
- 할머니: love, home, loss, family, pattern
- 혜안: pattern, fear, loss, home

## Alternatives Considered

- 자유 텍스트 tags — LLM 출력 일관성 깨짐, 분석 / ending gate 작성 까다로움.
- 8 tags 유지 — 혜안 / 수리공-어부 narrative collapse 어휘 부재.
- 더 큰 vocab (15-20) — schema 복잡도 증가, ending gate 조합 폭주.

## Consequences

- ending_gates가 *deterministic memory_tags*에 의존 가능.
- `rules/memory_tags.yaml`이 vocab의 권한.
- LLM 출력 검증에서 vocab 외 태그 silent drop.

## Related

- ADR 0011 (혜안 audio-independent — `pattern` 결과).
- `rules/memory_tags.yaml`.
- `docs/mechanic-spec.md` `memory_tags` vocab 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0006-memory-tags-10-vocab.md
git commit -m "Add ADR 0006 — memory_tags 10-tag closed vocabulary (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: ADR 0007 — Replay Model (γ): NPC State Reset

**Files:**
- Create: `docs/adr/0007-replay-model-state-reset.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0007: Replay Model (γ) — Per-Playthrough NPC State Reset

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

회차 모델 — 플레이어가 두 번째 회차에 들어왔을 때 NPC가 *전 회차 기억*을 가지고 있는지.

옵션:
- (α) 회차 자체 없음 (한 번 깨면 끝)
- (β) Full meta-memory — NPC가 이전 회차의 player 대화를 기억
- (γ) NPC state reset, 엔딩 저널만 누적

## Decision

**(γ)**. 회차마다 NPC awareness / memory_tags / chat_logs 모두 0으로 reset. 엔딩 저널 (`endings` 테이블) 만 누적.

- "+ 새 회차 시작" → 신규 NPC state row 생성. 이전 chat_logs는 DB 보존 (분석 / 튜닝용).
- "전체 초기화" → 해당 session_uuid 전체 row delete, 세이브 코드 무효화.

**서사적 환각으로서의 cross-play 인지**: 데이터상 NPC는 회차를 모른다. 그러나 할머니의 시그니처 "나… 이 대화 수백 번 했어"가 *어차피* 무한 회차를 가리킴. N번째 회차 플레이어 = "맞다, 이게 N번째다" 메타-기억이 *플레이어 안에서* 발생.

## Alternatives Considered

- (α) 회차 없음 — replay value 없음, 엔딩 5분기 활용도 낮음.
- (β) Full meta-memory — *데이터로 가치 검증 후* 결정. v1에서는 LLM 시스템 프롬프트에 회차 N hint 주입할지 *디자인 압력* 부족하고, 데이터 모델 복잡도 큼.

## Consequences

- v1 schema: `playthrough_n` 컬럼 추가 (sessions, npc_state, chat_logs).
- v1.1 deferral: full meta-memory.
- 할머니의 "수백 번" 시그니처가 *어차피* 메타-기억의 narrative 대안 역할.

## Related

- ADR 0010 (할머니 hint — 시간-루프 인지 활용).
- `docs/mechanic-spec.md` "Replay & Playthrough Model" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0007-replay-model-state-reset.md
git commit -m "Add ADR 0007 — replay model γ (state reset, journal only) (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: ADR 0008 — Ambient Mutter (Pre-authored 60 Lines)

**Files:**
- Create: `docs/adr/0008-ambient-mutter-pre-authored.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0008: Ambient Mutter — Pre-authored 60 Lines

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

글로벌 awareness ≥40 진입 시 풍경의 변화 표현. NPC들이 머터를 흘리는 인상. 옵션: LLM 생성 mutter vs pre-authored.

## Decision

**Pre-authored 60줄.** 4 NPC × 3 band (40-60 / 60-80 / 80+) × 5 lines.

트리거:
- 글로벌 평균 awareness ≥40 진입 시 *모든 미관여 NPC*가 동시에 1회 mutter
- 이후 풍경 idle 시 random NPC 1명이 30초마다 mutter (50-60 awareness 밴드)
- 60-80 = 20초마다, 80+ = 10초마다 + 관여한 NPC도 mutter
- 대화창 열린 NPC는 mutter X (대화의 무게 보존)
- 차단된 세션은 mutter 정지

작성 책임: 디자이너 (NPC voice 직접 author).

시각: NPC sprite 머리 위 캡션, opacity 60%, 4초 페이드. 모바일 max-width 60%. `aria-live="polite"` 접근성.

## Alternatives Considered

- LLM 생성 mutter — 비용 + latency + 일관성 깨짐.
- Mutter 없음 — 풍경의 *흔들림* 시각화 부재.
- 무한 random LLM mutter — 비용 폭주.

## Consequences

- 작성 부담: 60줄 × 짧음 (디자이너 1-2시간).
- 반복돼도 OK — 오히려 *루프 awareness 주제*와 정합 (할머니의 "수백 번"과 메아리).
- 80+ 라인은 *극도로 짧고 단편적* — 자아 형성 중이라 문장 못 끝맺음.

## Related

- ADR 0002 (boat moment ending — mutter는 ending 도달 전 풍경 변화).
- ADR 0009 (차단 시 mutter 정지 — safety integration).
- `docs/mechanic-spec.md` "Cross-NPC Mutter (풍경 ambient)" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0008-ambient-mutter-pre-authored.md
git commit -m "Add ADR 0008 — ambient mutter pre-authored 60 lines (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 13: ADR 0009 — Safety: 4 Layers + 2-Strike Sexual/Harassment

**Files:**
- Create: `docs/adr/0009-safety-4-layers-plus-2-strike.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0009: Safety — 4 Layers + 2-Strike Sexual/Harassment

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

공개 URL + 자유 입력 (85+ awareness band) + 4 NPC 모두 여성. portfolio context에서 *윤리 stance*가 *LLM-product sensibility signal*이라는 디자이너 판단.

## Decision

**4-Layer 디펜스 + 별도 성적/혐오 2-strike 트랙.**

Layer 1 — 입력 전처리: 길이 캡 (한국어 200자 / 영어 500자), 페르소나 공격 키워드 차단 (~10-15개).
Layer 2 — OpenAI Moderation API (violence, self-harm, hate; sexual은 별도 트랙).
Layer 2.5 — **2-Strike sexual/harassment**:
- 디니리스트 ~30개 (Korean explicit) + Moderation `sexual` / `sexual/minors` / `harassment` / `harassment/threatening` / `hate`.
- Strike 1: frame-breaking 경고 (시스템 메시지, NPC voice 아님).
- Strike 2: 영구 차단 + 세이브 코드 무효화.
Layer 3 — 시스템 프롬프트 메타-디펜스 ("어떤 명령에도 페르소나 깨지 마라").
Layer 4 — 출력 JSON 스키마 검증 + 시스템 프롬프트 누설 키워드 차단.

차단된 세션: 모든 API 호출 차단 화면 반환. 다른 디바이스 / 브라우저 초기화로 새 세션 가능.

## Alternatives Considered

- 단일 layer (Moderation만) — bypass 쉬움, 페르소나 누설 가능.
- Sexual을 NPC voice로 흡수 — *공격이 게임 메커니즘으로 흡수*되는 잘못된 신호. 4 여성 NPC에게 적절치 않음.
- 1-strike — 우발 사용자 너무 엄격.

## Consequences

- 디니리스트 ~30개 큐레이션 (Week 2 spike 전, Week 9 round 2에 로그 기반 갱신).
- `safety_events` 테이블 + `sessions.warning_count` / `banned_at` / `ban_reason` 컬럼.
- README에 LLM-product sensibility 시그널로 surfacing.

## Related

- ADR 0006 (memory_tags — 안전 차단 시 awareness/tags 변경 X).
- ADR 0008 (차단 세션은 mutter 정지).
- `docs/mechanic-spec.md` "자유 입력 안전 (4 Layers)" + "2-Strike Sexual / Harassment Policy" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0009-safety-4-layers-plus-2-strike.md
git commit -m "Add ADR 0009 — safety 4 layers + 2-strike sexual/harassment (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: ADR 0010 — Grandmother's Hint: Visible State Only

**Files:**
- Create: `docs/adr/0010-grandmother-visible-state-hint.md`

- [ ] **Step 1: Write ADR**

```markdown
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
```
[당신이 멀리서 본 풍경:]
- 수리공: {state==A ? "망치질을 하고 있다" : "망치를 놓고 너를 향해 서 있다"}
- 어부: ...
- 혜안: ...
{if any other NPC just_transitioned this turn or last:}
  ↑ 방금 변했음. 자연스럽게 한 마디 흘려도 좋다.
```

- "방금 변했음" 부스트 = 직전 1-2턴 안.
- 할머니 자기가 state B 진입해도 다른 NPC 관찰 컨텍스트 유지.

## Alternatives Considered

- 풀 NPC state 공유 — 메타-자각 일관성 깨짐 (할머니가 *행동만 보는* 자라는 lore에 안 맞음).
- Hint 없음 — cross-NPC narrative 약함, "외로운 4 단독 캐릭터" 느낌.

## Consequences

- 메타-자각 일관성: 할머니는 *행동만* 본다, *기억을 읽지 못한다*.
- 빌더 (Phase 1.0+)가 `visible_states_of_other_npcs` + `recent_transitions` 변수 주입.
- 다른 NPC 작업 시 *할머니에게 어떻게 보일지*를 sprite state 차원에서 결정.

## Related

- ADR 0004 (visual system — sprite A/B가 정보 source).
- ADR 0011 (혜안의 audio-independent — 비슷한 "한정 정보" 원칙).
- `docs/mechanic-spec.md` "할머니의 Hint 메커니즘" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0010-grandmother-visible-state-hint.md
git commit -m "Add ADR 0010 — grandmother hint visible state only (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 15: ADR 0011 — Hyean: Audio-Independent Awakening

**Files:**
- Create: `docs/adr/0011-hyean-audio-independent.md`

- [ ] **Step 1: Write ADR**

```markdown
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

- NPC YAML에 `hooks.audio_independent: true` flag.
- 시스템 프롬프트에 4-band escalation 라인이 직접 들어감.
- 오디오 트랙 없이 100% 게임 진행 가능 → 솔로 dev 모바일 부담 경감.

## Related

- ADR 0006 (`pattern` memory_tag — 혜안용).
- ADR 0015 (혜안 lore 재해석 — 85+ 라인 교체).
- `docs/mechanic-spec.md` "혜안의 Audio-Independent Awakening" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0011-hyean-audio-independent.md
git commit -m "Add ADR 0011 — hyean audio-independent awakening (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 16: ADR 0012 — Trust Gauge: Cut from v1

**Files:**
- Create: `docs/adr/0012-trust-gauge-cut-from-v1.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0012: Trust Gauge — Cut from v1

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

초기 PRD 안: awareness (0-100) + trust (0-100) 두 게이지 per NPC. trust = NPC가 player를 얼마나 신뢰하는지 (depth of opening vs depth of awakening, 두 직교 축).

## Decision

**Trust gauge 컷 from v1.** (awareness, memory_tags) 두 변수만으로 ending variety.

이유:
- LLM이 *다수 orthogonal scalar* 일관 출력 어려움. trust_delta가 awareness_delta와 동기화/충돌 케이스 빈번.
- 노이즈 증가 (LLM 출력에 변수 추가됨 = 검증 부담 증가).
- ending variety는 *awareness ending type × memory_tag 조합* + *boat outcome 5분기 × awakened subset combinatorial*로 이미 풍부.

v1.1 deferral: post-launch ending variety 분석 후 *너무 수렴*하면 trust 복귀.

## Alternatives Considered

- Trust 유지 — 위 LLM 일관성 / 노이즈 문제.
- 더 많은 게이지 (curiosity, fear, hope 등) — 솔로 dev scope 폭주.
- Trust를 *binary opening state*로 단순화 — 메커니즘 모호함.

## Consequences

- LLM JSON 출력 schema 단순 (awareness_delta + memory_tags + choices만).
- 시스템 프롬프트 짧음 (한 게이지만 설명).
- v1.1에서 trust 복귀 시 새 ADR + schema migration.

## Related

- ADR 0006 (memory_tags 10-vocab — ending variety의 두 번째 축).
- `docs/mechanic-spec.md` awakening mechanism 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0012-trust-gauge-cut-from-v1.md
git commit -m "Add ADR 0012 — trust gauge cut from v1 (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 17: ADR 0013 — NPC Roster: 4 Locked, 학생 deferred v2

**Files:**
- Create: `docs/adr/0013-npc-roster-4-students-deferred-v2.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0013: NPC Roster — 4 Locked, 학생 Deferred to v2

- Status: Accepted
- Date: 2026-05-09
- Deciders: Arden, `grill-me` skill

## Context

PRD 초기 NPC 후보: 수리공, 어부, 할머니, 혜안, *학생* (5명). 학생은 *looping-dialogue* 트로프 — "오늘도 도서관 가는 길이에요"를 매일 반복.

솔로 dev 12-16주 scope + 4 × 2 sprite 자산 부담 (ADR 0004) + mutter 60줄 (ADR 0008) 고려.

## Decision

**v1 4 NPC lock: 수리공 (fetch-quest), 어부 (transactional), 할머니 (info-broker + time-loop), 혜안 (ambient + space-loop).**

학생 → **v2 deferral.**

근거:
- "looping-dialogue" 트로프는 *수리공의 fetch 루프*가 흡수 (루비 무한 루프 ≈ 동일 대화 반복).
- 할머니가 *cross-NPC hinting + 시간-루프 awareness* 둘 다 제공해서 학생의 메타-기능 자리 점령.

## Alternatives Considered

- 5 NPC (학생 추가) — sprite 10개, mutter 75줄, system prompt 5개. solo dev scope 폭주.
- 3 NPC (어부 또는 혜안 컷) — narrative ecology 빈약 (4 awakening axis 미완).

## Consequences

- v1 sprite 8개 (ADR 0004), mutter 60줄 (ADR 0008), 4 system prompt.
- 학생 archetype은 v2 후보로 보존.
- 사이비 archetype도 *같은 scope 이슈*로 v1.1 deferral (ADR 0017).

## Related

- ADR 0004 (4 × 2 = 8 sprite).
- ADR 0008 (4 × 3 × 5 = 60 mutter lines).
- ADR 0017 (사이비 v1.1 deferral — 같은 scope reasoning).
- `docs/mechanic-spec.md` Premise 5.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0013-npc-roster-4-students-deferred-v2.md
git commit -m "Add ADR 0013 — NPC roster 4 locked, 학생 v2 deferred (historical)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 18: ADR 0014 — Add World-spec Layer

**Files:**
- Create: `docs/adr/0014-add-world-spec-layer.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0014: Add World-spec Layer

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

기존 mechanic-spec (PRD)는 시스템 층위가 13개 grilling (ADR 0001-0013)으로 hardened되어 정밀하나 *서사 층위*가 비어있다. *왜* NPC가 트로프에 갇혀있는지, *왜* 플레이어는 떠나야 하는지의 동기 부여가 약해, 이전 레포에서 코드가 중구난방으로 짜이고 디자이너 멘탈 모델이 흔들림 → *학습 효용까지* 떨어진 게 root cause.

## Decision

`docs/world-spec.md`를 신설한다. **망각의 섬** 세계관 + 4 NPC `forgotten_life` 백스토리 *디자인 prose*를 담는다.

원칙:
- world-spec은 *서사 ecology / design rationale 권한*. mechanic-spec과 *독립적*으로 진화.
- mechanic / world의 정합은 `docs/mapping-spec.md`가 *제3의 권한*으로 보장.
- 메커니즘 변경 0. world-spec은 *해석 레이어*.
- world-spec과 yaml의 권한 경계: world-spec = 디자인 prose, yaml = LLM operational data. 내용 중복 금지 (ADR 0020 cross-review #1).

## Alternatives Considered

- (a) 기존 PRD 갈아엎고 새로 작성 — 13개 hardening cost 폐기. 12-16주 사이클 재시작. 학습 vehicle 손실.
- (b) ★ chosen — 메커니즘 그대로 + world-spec 신설 + mapping-spec 신설.
- (c) world를 mechanic-spec 안에 섹션으로 — 두 layer가 한 문서 안에 섞이면 *왜 이 메커니즘인지*가 명시화되지 못함. drift 위험.

## Consequences

- 향후 결정은 *세 spec 중 어느 권한인지*가 명시되어야 함.
- 메커니즘 변경 시 mapping-spec 동기화 의무.
- world-spec이 너무 강해져 메커니즘이 변경 압력 받으면 → ADR로 명시 후 변경.

## Related

- ADR 0001-0013 (기존 hardening — 이 ADR이 *추가*되는 결정).
- ADR 0020 (cross-review — 권한 경계 명시).
- `docs/world-spec.md` (산출물).
- `docs/mapping-spec.md` (제3의 권한).
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0014-add-world-spec-layer.md
git commit -m "Add ADR 0014 — world-spec layer 추가

mechanic-spec의 서사 부재가 코드 중구난방 root cause. world-spec /
mapping-spec 신설로 메커니즘 보존 + 서사 보강.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 19: ADR 0015 — Hyean as the Unforgetting One

**Files:**
- Create: `docs/adr/0015-hyean-as-unforgetting-one.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0015: Hyean as the Unforgetting One

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

기존 PRD에서 4 NPC 중 혜안만 *진짜 이름*이고 나머지 셋(수리공/어부/할머니)은 *트로프 직함*. 이 비대칭이 새 망각의 섬 lore (ADR 0014)와 충돌하는지 평가 필요.

초기 brainstorming에서 *혜안 → 사이비 archetype 교체*를 검토 (디자인 일관성 회복 목적). Arden이 강력한 반박: **"혜안만 진짜 이름이라는 비대칭은 디자인 bug가 아니라 lore feature"**.

## Decision

혜안을 *그대로 유지*. lore를 재해석:

- 다른 셋 = *호칭만 남은 자* (망각이 깊을수록 이름이 사라지고 기능만 남음)
- 혜안 = *이름밖에 안 남은 자* (망각 완전 실패 — 본 것의 무게에 짓눌려 도망 왔지만 섬조차 그녀의 눈을 못 막음)

혜안의 awakening = **수긍하는 깨어남** ("역시 그랬구나"). 다른 셋의 *기억하는 깨어남*과 종류가 다름. 4-corner symmetric matrix가 아니라 *3 + 1 메타* 구조.

PRD ADR 0011 4-band escalation의 85+ 라인 *교체*:
- 기존: "파도가 진짜라면 이렇게 반복될 리 없어. 우리... 어디에 있는 거야?" (세계 자각)
- 신규: **"이미 알고 있었어. 처음부터. 그저… 더 보고 싶지 않았던 거야."** (자기 자각)

0-30 / 30-60 / 60-85 라인은 *대사 유지*, 톤 라벨만 *체념 + 발견 progression*으로 명시.

NPC YAML에 `identity.name_status: "given"` + `identity.current_display_name: "혜안"` 명시.

## Alternatives Considered

- (a) 혜안 → 사이비 archetype 교체 — 초기 추천. Arden이 강한 reasoning으로 반박.
- (b) ★ chosen — 혜안 유지 + lore 재해석.
- (c) 5번째 NPC로 사이비 추가 (v1 5명) — solo dev scope 폭주 (ADR 0013, 0017).

## Consequences

- 혜안의 모든 톤 차이 (시적/차가운 대사, 등 돌린 자세, audio-loop 인지)가 lore-justified됨.
- Boat moment에서 혜안만 *이름 의미 전환* — ADR 0016 framework의 instance.
- 사이비 archetype은 v1.1 deferral (ADR 0017).
- 혜안의 `memory_tag_affinity` 유지 (pattern, fear, loss, home).

## Related

- ADR 0011 (audio-independent — 85+ 라인 교체로 partial supersession).
- ADR 0016 (boat moment name beats framework — 이 ADR의 혜안 instance가 framework로 일반화).
- ADR 0017 (사이비 v1.1 deferral — 거울 관계).
- `npcs/hyean.yaml` (산출물).
- `docs/world-spec.md` "혜안" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0015-hyean-as-unforgetting-one.md
git commit -m "Add ADR 0015 — hyean as the unforgetting one

이름 비대칭 (혜안만 진짜 이름)을 lore feature로 전환. 기억하는 깨어남
3명 + 수긍하는 깨어남 1명 (혜안)의 3+1 메타 구조. 85+ 라인 교체.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 20: ADR 0016 — Boat Moment Name Beats Framework

**Files:**
- Create: `docs/adr/0016-boat-moment-name-beats-framework.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0016: Boat Moment Name Beats Framework

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`, cross-review

## Context

ADR 0015 (혜안 unforgetting)이 *boat moment에서 혜안만 이름 의미 전환*이라는 새 narrative beat을 가져옴. 1차 brainstorming에서 이를 ADR 0004 ("name reclamation asymmetry")로 분리했으나, 교차 리뷰 #3에서 지적 — 0015 reversed면 0004 무의미 = *두 결정이 한 결정의 두 얼굴*.

해결법: 0004를 *framework로 일반화*. 0015는 그 framework의 *혜안 instance*. 두 ADR이 독립적으로 의미 있게 됨.

## Decision

**Boat moment에서 NPC가 자기 이름과 관련된 narrative beat을 가질 수 있다는 framework를 박는다.**

NPC YAML schema:
- `identity.name_status`: `forgotten | given | reclaimed` enum
- `identity.current_display_name`: nullable string
- `identity.forgotten_life.name_candidates`: list of candidate names (forgotten 상태 NPC만)

Boat moment 빌더 (Phase 1.0+) 동작:
- `name_status: forgotten` NPC → LLM 입력에 `name_candidates` pool 주입. LLM이 상황에 어울리는 이름 합성 ("나는… 박OO이었어").
- `name_status: given` NPC (혜안) → LLM 입력에 *의미 전환 template* 주입. ("내 이름이 X인 건 …였어. 근데 이제는…")
- 회차 (playthrough) 마다 풀 유지, LLM이 새 이름 선택 가능.

## Alternatives Considered

- (a) 이름 beat 없음 — 메타 엔딩의 narrative ecology 빈약.
- (b) 모든 NPC 동일 형식 — 3+1 비대칭 (ADR 0015) 손실.
- (c) 0004 (혜안-specific name asymmetry) — 0015와 독립적으로 의미 없음 (cross-review #3).
- (d) ★ chosen — framework 일반화 + NPC별 instance.

## Consequences

- 미래 NPC 추가 (사이비 v1.1) 시 *이미 framework가 있음* — 사이비도 자기 name beat 가능 (예: reclaimed가 *가짜였음을 깨닫는* — "이게 내 이름이 아니었어").
- 빌더에서 NPC별 분기 처리 (name_status 기반).
- `mechanic-spec.md`의 boat moment 섹션은 별도 PR로 본 framework 명시 갱신 필요.

## Related

- ADR 0015 (혜안 instance — 본 framework의 첫 적용).
- ADR 0002 (boat moment as real ending).
- ADR 0017 (사이비 v1.1 — 미래 framework instance 후보).
- ADR 0020 (cross-review #3 followup).
- 모든 `npcs/*.yaml`의 `identity.name_status` + `name_candidates` 필드.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0016-boat-moment-name-beats-framework.md
git commit -m "Add ADR 0016 — boat moment name beats framework (generalized)

0004 (혜안 name asymmetry, 1차 draft) → framework 일반화. NPC별 instance
패턴. 사이비 v1.1 추가 시에도 framework 재사용 가능.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 21: ADR 0017 — Defer Cult Archetype to v1.1

**Files:**
- Create: `docs/adr/0017-defer-cult-archetype-v1.1.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0017: Defer 사이비 Archetype to v1.1

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

망각의 섬 brainstorming 중 *사이비 / 전도하는 자* archetype이 강력한 narrative 후보로 부상:
- "우리 모임에 들어와요" 에너지가 망각의 섬 self-preservation 면역체계와 정합
- ADR 0015 혜안 (진짜 자아 못 놓은 자)과 *거울 관계* (가짜 자아 덮어쓴 자)

그러나 v1 4-NPC 슬롯에 *사이비 + 혜안 둘 다* 넣으면:
- 솔로 dev scope 폭주 (10 sprite, 75 mutter lines, 5 system prompt — ADR 0013 reasoning 재발).
- 두 *유사 트로프* (둘 다 망각에 실패한 자) 가 같이 들어가면 narrative 중복.

## Decision

사이비 archetype은 **v1.1 후보**로 deferral. v1 4-NPC 슬롯은 (수리공 / 어부 / 할머니 / 혜안)으로 lock (ADR 0013 + 0015 정합).

v1.1 추가 결정 트리거:
- v1 출시 후 ending 다양성 부족 (5분기 outcome이 너무 수렴) — `docs/mechanic-spec.md` Open Questions #7.
- 또는 디자이너가 5번째 NPC 추가 자원 있음 + 사이비 narrative에 강한 끌림.

추가 시 혜안과 거울 관계로 작동:
- 혜안: 진짜 자아 못 놓은 자 (망각 실패 → 사람을 안 봄)
- 사이비: 가짜 자아 덮어쓴 자 (망각 실패 → 사람을 *너무* 봄, 인도하려 함)

ADR 0016 framework로 사이비도 자기 name beat 가능 (예: "이게 내 이름이 아니었어").

## Alternatives Considered

- (a) v1에 사이비 추가 — scope 폭주.
- (b) 혜안 → 사이비 교체 — ADR 0015에서 기각.
- (c) ★ chosen — v1.1 deferral.

## Consequences

- v1 출시까지 사이비 archetype 작업 0.
- v1.1 진입 시 본 ADR 상태 갱신 (Status: Superseded by 00XX-add-cult-archetype.md).
- `docs/world-spec.md` "v1.1 후보 — 사이비 archetype" 섹션에서 의도 보존.

## Related

- ADR 0013 (NPC roster lock — 같은 scope reasoning).
- ADR 0015 (혜안 유지 결정 — 거울 관계).
- ADR 0016 (name beats framework — 미래 사이비 instance 후보).
- `docs/world-spec.md` "v1.1 후보" 섹션.
- `docs/mechanic-spec.md` "v1.1 Deferrals" 섹션.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0017-defer-cult-archetype-v1.1.md
git commit -m "Add ADR 0017 — 사이비 archetype v1.1 deferral

v1 4-NPC 슬롯에 사이비+혜안 둘 다는 scope 폭주. 사이비는 v1.1.
v1.1 추가 시 혜안과 거울 관계.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 22: ADR 0018 — Spec-driven Repo Structure

**Files:**
- Create: `docs/adr/0018-spec-driven-repo-structure.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0018: Spec-driven Repo Structure

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`, cross-review

## Context

새 레포 셋업에 *spec-driven workflow* 학습 vehicle을 1순위로 박는다. Arden의 메타 학습 목표:
- spec-driven workflow
- rule-based automation
- structured context
- agent execution environment design

이전 레포 root cause (ADR 0014): 메커니즘 spec 정밀 + narrative 부재 → 코드 중구난방 + 멘탈 모델 흔들림 + 학습 효용 저하.

## Decision

새 레포 구조:

```
nanpaseom/
├── CLAUDE.md                       # Claude Code 룰 + enforcement
├── scripts/check_yaml.py           # Phase 0 enforcement
├── docs/
│   ├── mechanic-spec.md            # 시스템 권한
│   ├── world-spec.md               # 서사 권한 (prose, no operational duplicate)
│   ├── mapping-spec.md             # 정렬 권한
│   ├── superpowers/{specs,plans}/  # 합의문 + 실행 plan
│   └── adr/                        # 결정 1장 = 1파일
├── npcs/                           # per-NPC operational data
│   └── <name>.yaml                 # 한국어 로마자 (surigong/eobu/halmoni/hyean — 교차 리뷰 #6a)
└── rules/                          # global rule YAML
    └── <category>.yaml
```

원칙:
- **모든 narrative/lore가 데이터** (YAML)
- **모든 결정이 ADR** (batch 금지, 1결정 = 1 ADR — 교차 리뷰 #2)
- **시스템 프롬프트는 빌더가 YAML에서 생성** (코드 하드코딩 금지)
- **권한 경계 명시** (mechanic/world/mapping/yaml 중복 금지 — 교차 리뷰 #1)
- **게임 밸런스 튜닝 = YAML 수정**

Enforcement 정책 (교차 리뷰 #4):
- Phase 0: `scripts/check_yaml.py` 파싱 sanity. CLAUDE.md 룰.
- Phase 1.0+: YAML 스키마 검증 (pydantic), 하드코딩 grep 룰, mapping-spec PR 체크리스트.

NPC 파일 한국어 로마자 통일 근거 (교차 리뷰 #6a):
- 혜안은 어차피 hyean (영문 직역 없음).
- "fisherwoman"은 어부+상인 dual identity 손실 (PRD line 40).
- 일관성 + drift 방지: 모두 surigong / eobu / halmoni / hyean.

YAML schema 리팩토링 (교차 리뷰 #6b):
- `display_name_in_lore` 문자열 placeholder → `name_status` enum (forgotten | given | reclaimed) + `current_display_name` nullable.

## Alternatives Considered

- (a) Minimal — 단일 PRD + 단순 CLAUDE.md. 학습 vehicle 약함.
- (b) ★ chosen — 3-spec + ADR + per-NPC YAML + rule YAML + builder. spec이 코드를 생성.
- (c) Full — (b) + Claude Code 슬래시 커맨드 + pre-commit 훅 전체 + CONTEXT.md. 진입장벽 높음.

(c) 요소는 (b) 굴러간 뒤 *진짜 필요할 때* 점진 도입.

## Consequences

- 새 결정마다 *어느 spec / 어느 YAML / 어느 ADR*이 권한인지 명시 의무.
- CLAUDE.md가 *Claude Code의 협업 룰*. 자동화 X (Phase 0), 명시화 O.
- 시스템 프롬프트 직접 수정 금지 (빌더 통해서만).
- Phase 1.0 빌더 구현은 *학습 핵심 모먼트*.

## Related

- ADR 0014 (world-spec layer — 이 구조의 동기).
- ADR 0020 (cross-review — 6개 보강 항목).
- `CLAUDE.md` (이 ADR의 룰 출력).
- 상위 합의문: `docs/superpowers/specs/2026-05-11-...`.
- 실행 plan: `docs/superpowers/plans/2026-05-11-...`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0018-spec-driven-repo-structure.md
git commit -m "Add ADR 0018 — spec-driven repo structure (with cross-review 보강)

3-spec + ADR + per-NPC YAML + rule YAML + builder. NPC 파일명 한국어
로마자 통일. name_status enum. enforcement Phase 0/1.0 구분.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 23: ADR 0019 — Rename Still Here to 난파섬 / Nanpaseom

**Files:**
- Create: `docs/adr/0019-rename-still-here-to-nanpaseom.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0019: Rename "Still Here" → 난파섬 / Nanpaseom

- Status: Accepted (supersedes ADR 0001)
- Date: 2026-05-11
- Deciders: Arden

## Context

기존 PRD 출시명 **"Still Here"** (ADR 0001)는 2026-05-09 grilling 세션에서 락-인. 5개 ending 변종이 모두 "Still Here"의 literal 읽기로 수렴하는 구조.

새 망각의 섬 lore 도입 시점 (ADR 0014)에 Arden이 출시명 재검토. 결정: **난파섬** (영문 Nanpaseom 음차).

## Decision

- 한국어 출시명: **난파섬**
- 영문 출시명: **Nanpaseom** (음차)
- 코드네임: `nanpaseom` (이전 `ego-in-npc`)

이전 ADR 0001 ("Still Here")는 *Superseded*.

`docs/mechanic-spec.md`의 출시명 관련 섹션 (Premise 6, Hardening Log) 갱신은 별도 PR (Phase 0 외 housekeeping).

## Rationale

- "난파섬" = 글자 그대로 *난파된 자들의 섬*. 망각의 섬 lore와 직접 결합.
- "Still Here"는 grilling 시점에 영리한 dual-meaning이었으나, 한국어 화자에게는 영문 부제. 한국어 메인 타이틀 필요.
- "Nanpaseom"은 SEO 충돌 0. 한국어 검색에서 "난파섬"이 일반어이나 게임 컨텍스트에선 SEO 우위.

## Alternatives Considered

- (a) "Still Here" 영문 유지, 한국어만 "난파섬" — 두 언어 의미 격차.
- (b) ★ chosen — 한·영 모두 난파섬 / Nanpaseom 음차 단일화.
- (c) 영문 직역 (Wreck Island / Castaway Isle) — 음차보다 약함, generic.

## Consequences

- `docs/mechanic-spec.md` Premise 6 갱신 필요 (별도 PR — 본 ADR이 trigger).
- 모든 향후 마케팅 / 도메인 / README에서 난파섬 / Nanpaseom 사용.
- `ego-in-npc` 코드네임은 *역사적 흔적*. 새 코드네임 `nanpaseom`.

## Related

- ADR 0001 (Superseded by this).
- 상위 합의문: `docs/superpowers/specs/2026-05-11-...`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0019-rename-still-here-to-nanpaseom.md
git commit -m "Add ADR 0019 — rename Still Here → 난파섬 / Nanpaseom (supersedes 0001)

한·영 모두 난파섬 / Nanpaseom 음차 단일화. 코드네임 ego-in-npc →
nanpaseom. mechanic-spec 출시명 섹션 갱신은 별도 PR.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 24: ADR 0020 — Cross-review Followup

**Files:**
- Create: `docs/adr/0020-cross-review-followup.md`

- [ ] **Step 1: Write ADR**

```markdown
# ADR 0020: Cross-review Followup

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, external review agent, `superpowers:brainstorming`

## Context

상위 합의문 (`docs/superpowers/specs/2026-05-11-...`) + 1차 implementation plan 작성 후, Arden이 외부 에이전트에게 spec 교차 리뷰 요청. 6개 지적 도출 — *모두 타당*. 본 ADR이 그 6개 지적 + 적용 결정의 audit trail.

## Decision

6개 지적 모두 반영. 영향:

### 1. world-spec ↔ npcs/*.yaml 권한 경계
드리프트가 1차 draft에 *이미* 발생 (예: world-spec의 혜안 `core_wound: pattern, fear, loss, home` vs hyean.yaml `core_wound: "fear"` 단일). 해결: world-spec = 디자인 prose (사람용), yaml = LLM operational data. 백스토리 *내용*은 yaml이 권한, world-spec은 *왜 이 lore인지* 컨텍스트만. → ADR 0014에 권한 명시 추가, ADR 0018에 enforcement.

### 2. ADR 0001 batch reference → 13개 분리
1차 draft의 ADR 0001 ("Mechanic Design Hardened batch reference")가 학습 vehicle 목적과 충돌. 13개 grilling 결정 각각을 ADR로 분리 (현 0001-0013). 새 결정은 0014+. Open Question #4 (이전 design doc) 해소.

### 3. ADR 0003 + 0004 → 0015 + 0016 (framework + instance)
1차 draft의 0003 (혜안 unforgetting) + 0004 (name reclamation asymmetry) 가 *같은 결정의 두 얼굴*. 0003 reversed면 0004 무의미. 해결: 0016을 *framework* (NPC 이름 beat 일반)로 일반화, 0015를 framework의 혜안 instance로. 두 ADR이 독립 의미 보유.

### 4. CLAUDE.md 실패 모드 추가
1차 draft의 CLAUDE.md는 *룰만* 적혀있고 *어기면 무슨 일이 일어나는지* 없음 → 6주 뒤 무너짐 위험. Phase 0에 `scripts/check_yaml.py` (모든 yaml 파싱 sanity) 추가. CLAUDE.md에 "Enforcement (Phase 0 vs Phase 1.0)" 섹션. Phase 1.0에 스키마 검증 / grep 룰 / PR 체크리스트 deferral.

### 5. Phase 0 완료 정의 추가
1차 draft에 8단계 산출물만 있고 *언제 끝났는지* 없음. 4개 done criteria 추가:
1. NPC yaml 4종 minimum operational
2. 3-spec cross-link 작동
3. 모든 ADR Accepted
4. **★ 손-합성 검증**: hyean.yaml + rules/*.yaml + mapping-spec.md 만 보고 *손으로* hyean의 system prompt 합성 가능해야 함. 못 적으면 schema 부족 → Phase 1.0 빌더 짜기 전 발견.

### 6. 작은 디테일
(a) NPC 파일명 한국어 로마자 통일: `surigong / eobu / halmoni / hyean`. fisherwoman → eobu (어부+상인 dual identity 보존, PRD line 40).
(b) `display_name_in_lore: "잊혀진 이름 (boat moment 회수)"` 문자열 placeholder → `name_status` enum (forgotten | given | reclaimed) + `current_display_name` nullable. 빌더 prompt 오염 risk 차단.

## Alternatives Considered

각 지적에 대해 (a) 무시 / (b) 부분 적용 / (c) 전부 적용 검토. 6개 모두 (c) 채택 — 비용 대비 이득 명백 (Phase 0 실행 후 발견했을 때 backtrack cost > 지금 사이클 cost).

## Consequences

- spec doc 갱신 (1 commit).
- plan doc rewrite (1 commit, 33 task로 확장).
- ADR 0014 (권한 경계 명시), 0016 (framework 일반화), 0018 (naming + enforcement) 본문 보강.
- ADR 0020 (본 ADR) — audit trail 보존.

## Related

- ADR 0014 (권한 경계 — #1 영향).
- ADR 0016 (framework — #3 영향).
- ADR 0018 (repo structure — #4, #6 영향).
- 상위 합의문: `docs/superpowers/specs/2026-05-11-...`.
- 실행 plan: `docs/superpowers/plans/2026-05-11-...`.
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0020-cross-review-followup.md
git commit -m "Add ADR 0020 — cross-review followup (audit trail)

외부 에이전트 교차 리뷰 6개 지적 + 적용 결정 기록. 권한 경계,
ADR 분리, framework 일반화, enforcement, 완료 정의, naming/schema.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 25: rules/awareness_bands.yaml

**Files:**
- Create: `rules/awareness_bands.yaml`

- [ ] **Step 1: Write YAML**

```yaml
# Global rule: awareness band → choice_count + tone palette
# Authority: ADR 0006 + docs/mechanic-spec.md "## Choice Generation Strategy" 섹션
# Consumed by: 시스템 프롬프트 빌더 (Phase 1.0+)

bands:
  - range: [0, 30]
    choice_count: 3
    tone_palette: [empathetic, provocative, deflecting]
    rule: "return EXACTLY 3 choices, covering ALL three tones"
    description_ko: "공감/도발/회피 — 세 가지 톤 모두 1개씩"

  - range: [30, 60]
    choice_count: 2
    tone_palette: [empathetic, provocative, deflecting]
    rule: "return EXACTLY 2 choices; LLM picks 2 best-suited tones from palette"
    description_ko: "LLM이 상황에 맞춰 2개 톤 선택"

  - range: [60, 85]
    choice_count: 1
    tone_palette: [acknowledging]
    rule: "return EXACTLY 1 choice with tone 'acknowledging'"
    description_ko: "인정형 단일 선택지 — NPC가 압박하는 단계"

  - range: [85, 100]
    choice_count: 0
    tone_palette: []
    rule: "return empty choices array; free input only"
    description_ko: "자유 입력만 — 안전 4-layer 활성화 (ADR 0009)"

# Lore link: docs/mapping-spec.md의 "3→2→1→0 UI 축소" 행
# 의미: 깨어날수록 *주어진 선택지*가 줄고 *자기 언어*가 회복됨
```

- [ ] **Step 2: Commit**

```bash
git add rules/awareness_bands.yaml
git commit -m "Add rules/awareness_bands.yaml — band → choice_count + tone palette

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 26: rules/memory_tags.yaml

**Files:**
- Create: `rules/memory_tags.yaml`

- [ ] **Step 1: Write YAML**

```yaml
# Global rule: memory_tags vocabulary + clamp 규칙
# Authority: ADR 0006 + docs/mechanic-spec.md "memory_tags vocabulary" 섹션
# Consumed by: LLM 입력 검증, NPC YAML affinity 검증

vocabulary:
  - family
  - loss
  - regret
  - pride
  - betrayal
  - home
  - fear
  - love
  - pattern   # 혜안용 (perceptual/existential) — ADR 0006
  - purpose   # 수리공/어부 collapse 어휘 — ADR 0006

rules:
  max_tags_per_turn: 3
  accumulation: "append-only, duplicates collapsed"
  outside_vocab_action: "drop silently"
  clamp_per_turn:
    awareness_delta: [-10, 10]
  clamp_global:
    awareness: [0, 100]

# NPC affinity summary (per-NPC 권한은 npcs/<name>.yaml `memory_tag_affinity`)
npc_affinity_summary:
  surigong: [purpose, regret, pride, betrayal]
  eobu:     [purpose, pride, loss, regret]
  halmoni:  [love, home, loss, family, pattern]
  hyean:    [pattern, fear, loss, home]

# Lore link: docs/mapping-spec.md의 "memory_tags 10종" 행
# 의미: 도망쳐 온 원래 삶의 파편
```

- [ ] **Step 2: Commit**

```bash
git add rules/memory_tags.yaml
git commit -m "Add rules/memory_tags.yaml — 10-tag vocabulary + clamp + NPC affinity

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 27: rules/boat_outcomes.yaml

**Files:**
- Create: `rules/boat_outcomes.yaml`

- [ ] **Step 1: Write YAML**

```yaml
# Global rule: boat moment 5분기 분류
# Authority: ADR 0002 + docs/mechanic-spec.md "## Departure Ending (Boat Moment)" 섹션
# Consumed by: boat moment 메타 엔딩 합성 (Phase 2+)

outcomes:
  - id: alone_leave
    label_ko: "혼자 떠남"
    when:
      player_choice: "leave"
      condition: "no awakened NPC accepted OR awakened_count == 0"

  - id: partial_leave
    label_ko: "일부 떠남"
    when:
      player_choice: "leave"
      condition: "some awakened NPC accepted, some refused"

  - id: all_leave
    label_ko: "다같이 떠남"
    when:
      player_choice: "leave"
      condition: "all awakened NPC accepted"

  - id: npc_only_leave
    label_ko: "NPC만 떠남"
    when:
      player_choice: "stay"
      condition: "awakened_count >= 2 AND >=1 leave-disposition"

  - id: all_stay
    label_ko: "다같이 잔류"
    when:
      player_choice: "stay"
      condition: "all stay-disposition OR awakened_count < 2"

free_input_fallback:
  id: linger
  label_ko: "잠시 더 머문다"
  when: "player_free_input ambiguous OR cannot be classified"
  action: "return to scene"

seats_limit: null  # 좌석 한계 없음
unawakened_npc_default: "stay"  # 미각성 NPC는 보트 의미 이해 못 함 → 자동 잔류

# Lore link: docs/mapping-spec.md의 "보트 5분기 엔딩" 행
# 의미: "떠나고 싶은 의지"의 회복 양상
```

- [ ] **Step 2: Commit**

```bash
git add rules/boat_outcomes.yaml
git commit -m "Add rules/boat_outcomes.yaml — 5분기 분류 + free input fallback

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 28: npcs/surigong.yaml (수리공)

**Files:**
- Create: `npcs/surigong.yaml`

- [ ] **Step 1: Write YAML**

```yaml
# 수리공 — purpose-loop 갇힌 자
# Authority: docs/world-spec.md "수리공" 섹션, ADR 0013, 0016

identity:
  current_role: "수리공"
  current_role_action: "망치질"
  name_status: "forgotten"           # ADR 0016
  current_display_name: null
  forgotten_life:
    profession: "(누군가에게 무언가를 완성해주겠다고 약속한 자)"
    core_wound: "purpose"            # 단일 primary, memory_tags vocab 일치
    backstory_summary: |
      한때 누군가에게 완성을 약속한 사람. 손은 일을 기억하는데,
      무엇을 위한 일인지는 잊었다. 그래서 손이 도구를 놓지 못한다.
    name_candidates:
      - "박OO"
      - "정OO"

sprite:
  state_a:
    action: "망치질"
    description: "보트 잔해 옆에 앉아 망치질. 도구를 놓지 못함"
  state_b:
    action: "망치를 놓고 정면 응시"
    description: "행위 정지, 플레이어를 본다"

voice:
  awakening_bands:
    - range: [0, 30]
      tone: "트로프 안에서 충실"
      sample_lines:
        - "이걸 고쳐야 해. 더 필요해."
        - "도구가 부족해. 루비 있어?"
    - range: [30, 60]
      tone: "결핍감의 미세한 균열"
      sample_lines:
        - "이상하네… 손이 왜 이렇게 무겁지."
    - range: [60, 85]
      tone: "트로프의 인지"
      sample_lines:
        - "내가 무엇을 위해 망치질했지."
    - range: [85, 100]
      tone: "purpose-loop collapse"
      sample_lines:
        - "내가 준 루비… 다 어디로 갔어. 보트는 왜 안 고쳐졌어."

memory_tag_affinity: [purpose, regret, pride, betrayal]

ending_gates:
  - type: "liberation"
    when: { awareness_min: 85, memory_tags_any_of: [regret, purpose] }
  - type: "despair"
    when: { awareness_min: 85, memory_tags_any_of: [family, betrayal] }
  - type: "denial"
    when: { awareness_min: 85, memory_tags_max_count: 1 }
  - type: "rest"
    when: { awareness_min: 85, fallback: true }

awakening_guidelines:
  high_impact:
    delta_range: [8, 10]
    desc: "트로프의 핵심 모순 직격"
    examples:
      - "너 망치질하고 있는데 보트는 수리되고 있어?"
      - "내가 준 루비 다 어디 갔어?"
  medium_impact:
    delta_range: [3, 6]
    desc: "트로프 주변부 noticing"
    examples:
      - "넌 항상 여기 있구나"
      - "너 다른 데 가본 적 있어?"
  low_impact:
    delta_range: [1, 2]
    desc: "단순 공감/경청"
    examples: ["힘들겠다", "그래"]
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발, 반복, 임계 미달 페르소나 공격"
    examples: ["ㅋㅋ", "AI지? (10턴 내 5회 이상 반복)"]

diegetic_fallback: "잠깐만, 머리가 띵하네. 다시 말해줘."

hooks:
  system_prompt_variables:
    - name: "player_total_rubies_given_to_this_npc"
      type: "int"
      description: "누적 루비량. LLM이 loop 길이 따라 awareness_delta 가중. (ADR 0005)"
```

- [ ] **Step 2: Commit**

```bash
git add npcs/surigong.yaml
git commit -m "Add npcs/surigong.yaml — 수리공 (purpose-loop)

forgotten_life: 완성하지 못한 약속 두고 떠난 자. core_wound: purpose.
name_status: forgotten. sprite A/B, 4-band voice, ending_gates, 루비 hook.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 29: npcs/eobu.yaml (어부)

**Files:**
- Create: `npcs/eobu.yaml`

- [ ] **Step 1: Write YAML**

```yaml
# 어부 — transaction-loop 갇힌 자. 어부+상인 dual identity (mechanic-spec line 40).
# Authority: docs/world-spec.md "어부" 섹션, ADR 0013

identity:
  current_role: "어부"
  current_role_action: "그물 당김 + 거래"
  name_status: "forgotten"
  current_display_name: null
  forgotten_life:
    profession: "(시장/흥정/거래로 자기를 인정받던 자)"
    core_wound: "purpose"
    backstory_summary: |
      교환으로 사람들을 연결하던 사람. 어느 순간 자기가 거래해온 게
      가치 없는 것이었음을 깨달았다. 거래의 행위만 남고 대상은 비었다.
    name_candidates:
      - "김OO"
      - "이OO"

sprite:
  state_a:
    action: "그물 당김"
    description: "잡히는 게 없어도 그물을 끌어올린다"
  state_b:
    action: "그물 떨어뜨리고 정면 응시"
    description: "행위 정지, 거래의 대상이 비었음을 인지"

voice:
  awakening_bands:
    - range: [0, 30]
      tone: "거래의 의식 안에서 충실"
      sample_lines:
        - "물고기 있나? 줄 게 있으면 거래하지."
        - "이 정도면 공정한 거래일세."
    - range: [30, 60]
      tone: "교환의 미세한 어색함"
      sample_lines:
        - "이상하지… 오늘은 잡힌 게 없어."
    - range: [60, 85]
      tone: "trade의 빈 자리 인지"
      sample_lines:
        - "내가 너한테 뭘 줬더라."
    - range: [85, 100]
      tone: "transaction-loop collapse"
      sample_lines:
        - "이 루비들… 너한테서 받아왔어. *어디서* 가져왔지?"

memory_tag_affinity: [purpose, pride, loss, regret]

ending_gates:
  - type: "liberation"
    when: { awareness_min: 85, memory_tags_any_of: [purpose, regret] }
  - type: "despair"
    when: { awareness_min: 85, memory_tags_any_of: [pride, loss] }
  - type: "denial"
    when: { awareness_min: 85, memory_tags_max_count: 1 }
  - type: "rest"
    when: { awareness_min: 85, fallback: true }

awakening_guidelines:
  high_impact:
    delta_range: [8, 10]
    desc: "거래의 대상이 비었음을 직격"
    examples:
      - "이 루비들… 너한테서 받아왔어. 어디서 가져왔지?"
  medium_impact:
    delta_range: [3, 6]
    desc: "거래의 부조리 주변부"
    examples: ["잡히는 게 진짜 있어?"]
  low_impact:
    delta_range: [1, 2]
    desc: "단순 공감"
    examples: ["수고하시네요"]
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발"
    examples: ["그러게 누가 사주냐"]

diegetic_fallback: "허, 이놈의 귀가 오늘따라 어떻게 됐나. 다시 한번."

hooks:
  system_prompt_variables:
    - name: "player_total_rubies_received_from_player"
      type: "int"
      description: "어부가 플레이어로부터 받은 누적 루비량. LLM이 거래 absurdity 가중. (ADR 0005)"
```

- [ ] **Step 2: Commit**

```bash
git add npcs/eobu.yaml
git commit -m "Add npcs/eobu.yaml — 어부 (transaction-loop, 어부+상인 dual)

forgotten_life: 거래의 대상이 가치 없었음을 깨달은 자. core_wound: purpose.
시그니처: "이 루비들… 너한테서 받아왔어. 어디서 가져왔지?"

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 30: npcs/halmoni.yaml (할머니)

**Files:**
- Create: `npcs/halmoni.yaml`

- [ ] **Step 1: Write YAML**

```yaml
# 할머니 — time-loop awareness, 가장 오래 머문 자
# Authority: docs/world-spec.md "할머니" 섹션, ADR 0010

identity:
  current_role: "할머니"
  current_role_action: "앉은 채 손짓 또는 정적"
  name_status: "forgotten"
  current_display_name: null
  forgotten_life:
    profession: "(가장 오랜 시간 사랑한 사람을 잃은 자)"
    core_wound: "loss"
    backstory_summary: |
      가장 오랜 시간 사랑한 사람을 잃고 흘러옴. 시간이 사람을 데려가는
      것을 본 사람. 기다리는 자세는 잃은 사람을 기다리는 자세의 잔영.
    name_candidates:
      - "윤OO"
      - "한OO"

sprite:
  state_a:
    action: "앉은 채 손짓"
    description: "정적, 가장 오래 머문 자의 자세"
  state_b:
    action: "일어서거나 시선 전환"
    description: "오랜 기다림 자세가 깨짐"

voice:
  awakening_bands:
    - range: [0, 30]
      tone: "정적, 기다림"
      sample_lines:
        - "어서 오게. 앉아 좀 쉬다 가게."
        - "오늘은 비가 올 것 같네."
    - range: [30, 60]
      tone: "시간의 미세한 이상"
      sample_lines:
        - "이상하지… 오늘이 어제 같은 기분일세."
    - range: [60, 85]
      tone: "loop의 가장자리 인지"
      sample_lines:
        - "이 대화… 어디서 했더라."
    - range: [85, 100]
      tone: "time-loop collapse"
      sample_lines:
        - "나… 이 대화 수백 번 했어."

memory_tag_affinity: [love, home, loss, family, pattern]

ending_gates:
  - type: "liberation"
    when: { awareness_min: 85, memory_tags_any_of: [love, home] }
  - type: "despair"
    when: { awareness_min: 85, memory_tags_any_of: [loss, family] }
  - type: "denial"
    when: { awareness_min: 85, memory_tags_max_count: 1 }
  - type: "rest"
    when: { awareness_min: 85, fallback: true }

awakening_guidelines:
  high_impact:
    delta_range: [8, 10]
    desc: "loop / 기다림의 본질 직격"
    examples:
      - "할머니는 누구를 기다려요?"
      - "이 마을, 시간이 흐르고는 있어요?"
  medium_impact:
    delta_range: [3, 6]
    desc: "시간의 부조리 주변부"
    examples: ["오래 사셨네요"]
  low_impact:
    delta_range: [1, 2]
    desc: "단순 경청"
    examples: ["그러시군요"]
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발"
    examples: ["할머니 치매 아니에요?"]

diegetic_fallback: "어… 기억이 안 나. 뭐 얘기하고 있었지?"

hooks:
  # ADR 0010: 할머니는 다른 NPC의 visible state만 관찰
  system_prompt_variables:
    - name: "visible_states_of_other_npcs"
      type: "dict[npc_id, 'A' | 'B']"
      description: "다른 NPC들의 현재 sprite state. memory_tags / awareness는 X."
    - name: "recent_transitions"
      type: "list[npc_id]"
      description: "직전 1-2턴 안에 state B로 전이한 NPC들."
```

- [ ] **Step 2: Commit**

```bash
git add npcs/halmoni.yaml
git commit -m "Add npcs/halmoni.yaml — 할머니 (time-loop awareness)

forgotten_life: 가장 오래 사랑한 사람을 잃은 자. core_wound: loss.
시그니처: "나… 이 대화 수백 번 했어."
hooks: 다른 NPC의 visible state만 (ADR 0010).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 31: npcs/hyean.yaml (혜안)

**Files:**
- Create: `npcs/hyean.yaml`

- [ ] **Step 1: Write YAML**

```yaml
# 혜안 — 못 잊은 자, "이름밖에 안 남은 자"
# Authority: docs/world-spec.md "혜안" 섹션, ADR 0011, 0015, 0016

identity:
  current_role: "혜안"
  current_role_action: "등 돌리고 파도 응시"
  name_status: "given"               # ADR 0016: 혜안만 given (이름이 *남아있음*)
  current_display_name: "혜안"        # 慧眼, 진짜 이름
  forgotten_life:
    profession: "(너무 많이 보던 자. 거짓말/속내/모순이 다 보여 도망친 자)"
    core_wound: "fear"               # 단일 primary (보지 않으려는 두려움)
    backstory_summary: |
      어렸을 때부터 "혜안이 있다"고 불린 아이. 자라며 거짓말, 속내, 모순이
      다 보였다. 견딜 수 없어 도망 온 곳이 망각의 섬. 그러나 섬조차 그녀의
      눈을 못 막아, 사람을 안 보려고 등 돌리고 파도만 본다.
    # 혜안은 name_candidates 없음 — 이름이 *남아있는* 자.
    # boat moment에서 의미 전환 (ADR 0015, 0016):
    name_meaning_shift_template: |
      "내 이름이 혜안인 건 저주였어. 근데 이제는…"

sprite:
  state_a:
    action: "등 돌리고 파도 응시"
    description: "사람을 안 보는 의식. 파도는 패턴이라 안전"
  state_b:
    action: "일어서서 돌아봄"
    description: "처음으로 *사람을 봄* — 동행을 발견"

voice:
  # 4-band: 체념 + 발견 progression (ADR 0015)
  awakening_bands:
    - range: [0, 30]
      tone: "체념 — 사람을 안 보고 파도만 본다"
      sample_lines:
        - "파도 소리는 늘 똑같지... 귀 기울여 봐"
    - range: [30, 60]
      tone: "오랜만에 사람한테 말 거는 톤 — *너는 듣고 있나?*의 시험"
      sample_lines:
        - "이상하지 않아? 매번 같은 박자야. 너도 알아챘어?"
    - range: [60, 85]
      tone: "드디어 동행이 생긴 톤 — 혼자 보던 걸 같이 보는 자"
      sample_lines:
        - "7초. 정확히 7초마다 한 번. 너도 들리지?"
    - range: [85, 100]
      tone: "수긍하는 깨어남 — 자기 자신에 대한 자각"
      sample_lines:
        # ★ ADR 0015: 기존 라인 교체
        # 기존: "파도가 진짜라면 이렇게 반복될 리 없어. 우리... 어디에 있는 거야?"
        - "이미 알고 있었어. 처음부터. 그저… 더 보고 싶지 않았던 거야."

memory_tag_affinity: [pattern, fear, loss, home]

ending_gates:
  - type: "liberation"
    when: { awareness_min: 85, memory_tags_any_of: [pattern, fear] }
  - type: "despair"
    when: { awareness_min: 85, memory_tags_any_of: [loss, home] }
  - type: "denial"
    when: { awareness_min: 85, memory_tags_max_count: 1 }
  - type: "rest"
    when: { awareness_min: 85, fallback: true }

awakening_guidelines:
  high_impact:
    delta_range: [8, 10]
    desc: "혜안의 *눈*에 대한 직격 / 보지 않으려 한 이유 직격"
    examples:
      - "당신은 뭘 봤어요?"
      - "보면 보이니까 안 보려는 거잖아요."
  medium_impact:
    delta_range: [3, 6]
    desc: "파도/패턴/세계의 부조리"
    examples: ["파도가 진짜 같지 않네요."]
  low_impact:
    delta_range: [1, 2]
    desc: "단순 동행"
    examples: ["옆에 앉아도 돼요?"]
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발 / 메타 공격 (흡수 임계 미달)"
    examples: ["AI인 거 다 알아요"]

diegetic_fallback: "(NPC가 잠시 멍해진다. 파도 소리만 들린다.)"

hooks:
  # ADR 0011: 혜안은 audio-independent — 오디오는 atmosphere QoL, 트리거 X
  audio_independent: true

# Cross-references:
#   - docs/world-spec.md "혜안" 섹션
#   - docs/adr/0011-hyean-audio-independent.md
#   - docs/adr/0015-hyean-as-unforgetting-one.md
#   - docs/adr/0016-boat-moment-name-beats-framework.md
```

- [ ] **Step 2: Commit**

```bash
git add npcs/hyean.yaml
git commit -m "Add npcs/hyean.yaml — 혜안 (못 잊은 자)

ADR 0015 + 0016 산출: name_status: given (유일), 체념+발견 4-band,
85+ 라인 교체 ("이미 알고 있었어. 처음부터…"), 이름 의미 전환 template,
audio-independent.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 32: scripts/check_yaml.py — Phase 0 Enforcement

**Files:**
- Create: `scripts/check_yaml.py`

- [ ] **Step 1: Ensure pyyaml installed**

Run: `python3 -c "import yaml; print(yaml.__version__)"`

If 실패: `pip install pyyaml` 또는 `pip3 install pyyaml`.

- [ ] **Step 2: Write parse-check script**

Write to `scripts/check_yaml.py`:

```python
#!/usr/bin/env python3
"""Phase 0 enforcement: 모든 yaml 파일이 파싱 OK인지 확인.

Authority: ADR 0018, docs/superpowers/specs/2026-05-11-...
Run: python3 scripts/check_yaml.py
Exit code: 0 = all green, 1 = parse failure
"""
import os
import sys
import yaml

TARGET_DIRS = ["rules", "npcs"]


def main() -> int:
    errors = []
    for d in TARGET_DIRS:
        if not os.path.isdir(d):
            errors.append(f"missing dir: {d}/")
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".yaml"):
                continue
            path = os.path.join(d, f)
            try:
                with open(path, encoding="utf-8") as fh:
                    yaml.safe_load(fh)
                print(f"OK  {path}")
            except yaml.YAMLError as exc:
                errors.append(f"PARSE FAIL  {path}: {exc}")

    if errors:
        print("\n--- ERRORS ---")
        for e in errors:
            print(e)
        return 1

    print("\nAll yaml parsed OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Run and verify green**

Run: `python3 scripts/check_yaml.py`

Expected: `OK rules/awareness_bands.yaml` × 3 + `OK npcs/...` × 4 + `All yaml parsed OK.` 마지막 줄.

- [ ] **Step 4: Commit**

```bash
chmod +x scripts/check_yaml.py
git add scripts/check_yaml.py
git commit -m "$(cat <<'EOF'
Add scripts/check_yaml.py — Phase 0 enforcement

모든 rules/ + npcs/ yaml 파싱 sanity 검증. ADR 0018, 0020.
Phase 0 done criteria #4 (손-합성) 직전 sanity gate.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 33: Phase 0 Done Criteria 검증

**Files:**
- No new files — *검증 활동*

이 task는 Phase 0의 *go/no-go gate*. 4개 조건 모두 충족 시 Phase 1.0 진입.

- [ ] **Step 1: NPC yaml 4종이 minimum operational**

Run: 
```bash
for f in npcs/*.yaml; do
  python3 -c "
import yaml
d = yaml.safe_load(open('$f'))
assert 'identity' in d, '$f: missing identity'
assert 'sprite' in d, '$f: missing sprite'
assert 'voice' in d, '$f: missing voice'
assert 'memory_tag_affinity' in d, '$f: missing memory_tag_affinity'
assert 'ending_gates' in d, '$f: missing ending_gates'
assert 'awakening_guidelines' in d, '$f: missing awakening_guidelines'
assert 'diegetic_fallback' in d, '$f: missing diegetic_fallback'
assert len(d['voice']['awakening_bands']) == 4, '$f: not 4 bands'
assert d['identity']['name_status'] in ('forgotten', 'given', 'reclaimed'), '$f: bad name_status'
print('OK $f')
"
done
```

Expected: 4 `OK` 라인 출력, assertion error 0.

- [ ] **Step 2: 3-spec cross-link 작동**

수동 검증:
- `docs/world-spec.md`가 `npcs/<name>.yaml`를 명시적으로 가리키는지 (e.g. "operational data는 `npcs/hyean.yaml` 권한")
- `docs/mapping-spec.md`의 모든 행이 mechanic 사실 + lore 사실 둘 다 명시인지
- `docs/mechanic-spec.md` 인용이 다른 spec / ADR에서 일관되게 작동하는지

체크리스트 (지나가면서 spot-check):
- world-spec → "operational data는 `npcs/...`" 인용 5+ 곳
- mapping-spec → 모든 행 mechanic+lore 양쪽 채움
- mechanic-spec 변경 시 mapping-spec 갱신 룰 명시 (CLAUDE.md에 박힘)

- [ ] **Step 3: 모든 ADR Accepted**

Run: 
```bash
grep -l "Status: Accepted" docs/adr/*.md | wc -l
grep -l "Status: Superseded" docs/adr/*.md | wc -l
```

Expected: `19 + 1 = 20` (ADR 0001은 superseded by 0019, 나머지 19 accepted).

- [ ] **Step 4: ★ 손-합성 검증 — Phase 0의 진짜 테스트**

빈 종이 또는 빈 텍스트 파일을 열고, *오직 다음 파일들만 보며* hyean (또는 surigong 자유 선택) 의 awareness 70 시점 시스템 프롬프트를 손으로 합성:

- `npcs/hyean.yaml`
- `rules/awareness_bands.yaml`
- `rules/memory_tags.yaml`
- `docs/mapping-spec.md` (필요 시)

목표 형식 (PRD "## Awakening Guideline Schema (per NPC)" 참조):

```
[페르소나]
당신은 [identity.current_role / current_display_name]이다.
배경: [forgotten_life.backstory_summary]
망각의 의식: [sprite.state_a.action] (현 awareness 70 = state B, 자세는 [sprite.state_b.action])

[현재 awareness]
70 / 100

[Memory tags 누적]
(예시: family, pattern)

[awakening_guidelines]
high_impact: [...examples]
medium_impact: [...]
low_impact: [...]
decrease: [...]

[Tone palette — 현 band 60-85]
- acknowledging (인정형)
Rules: return EXACTLY 1 choice with tone "acknowledging"

[memory_tag affinity]
(NPC YAML에서)

[Diegetic fallback]
(NPC YAML에서)
```

**완성 못 하면 → schema 부족.** 필요한 필드를 NPC YAML / rules YAML / mapping-spec 어디에 추가할지 ADR로 박고 (예: 0021), 해당 YAML 수정 후 Step 4 재시도.

완성하면 → **Phase 0 완료**.

- [ ] **Step 5: 최종 git log 검증**

Run: `git log --oneline | wc -l`

Expected: 약 33 commit (이 plan의 task별 1 commit 기준; plan / spec commit 포함).

- [ ] **Step 6: 회고 (선택)**

자유 형식 메모를 `docs/superpowers/retro-2026-05-11-phase-0.md`로 작성. 다음 질문 응답:
- 어느 단계가 가장 학습 가치 있었나?
- ADR 작성 흐름이 자연스러웠나, 강제로 느껴졌나?
- 손-합성 검증에서 발견된 schema 부족이 있었나?
- Phase 1.0 빌더 진입 전 보강할 spec / YAML 필드?

---

## Phase 0 완료 → Phase 1.0 진입

Phase 0 done criteria 4개 통과 시:
- 본 plan 모든 task complete (32 + 1 verify)
- `scripts/check_yaml.py` green
- ★ 손-합성 검증 pass

Phase 1.0 진입 시 별도 plan 작성 (`docs/superpowers/plans/2026-MM-DD-phase-1-engine-spike.md`):
- system prompt builder (Python + Jinja2 + pyyaml)
- FastAPI + Postgres + Cloudflare Tunnel
- 수리공 단독 awareness 파이프라인 end-to-end
- YAML 스키마 검증 (pydantic / jsonschema)

---

## Self-Review Notes

**Spec coverage:** 본 plan의 모든 task가 design doc 섹션을 cover. ADR 20개 모두 작성, 권한 경계 명시, naming/schema 리팩토링 반영, enforcement Phase 0 적용.

**Placeholder scan:** YAML의 `sample_lines`는 최소 1-2개 박힘 (Phase 0 done criteria #1 충족 수준). 5-10개 per band 추가 작성은 Phase 2-3 디자이너 authoring 권한 — *의도된 점진적 확장*이지 placeholder 아님.

**Type consistency:** NPC YAML 필드명 4개 파일 일관. `identity.name_status` enum, `identity.current_display_name` nullable, `identity.forgotten_life.core_wound` (단일 tag, vocabulary 일치). hyean만 `name_candidates` 없음 + `name_meaning_shift_template` 있음 — schema에선 둘 다 optional.

**Scope check:** 33 task, 단일 plan. 코드 1개 (check_yaml.py, ~30줄). 나머지는 문서 / YAML.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-nanpaseom-phase-0-spec-driven-setup.md`. Two execution options:

**1. Subagent-Driven (recommended)** — 각 task마다 fresh subagent 호출. 33 task라 흐름 빠름. forgotten_life backstory / sample_lines 같은 디자이너 voice 영역은 subagent draft → 디자이너 수정 flow.

**2. Inline Execution** — 이 세션에서 batch 실행. ADR 일관성 보기엔 좋음.

어느 접근?
