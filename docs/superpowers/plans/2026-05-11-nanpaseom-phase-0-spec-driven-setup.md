# 난파섬 Phase 0: Spec-driven Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 망각의 섬 세계관을 *spec-driven 구조*로 새 레포에 정착시킴. CLAUDE.md + 3-spec 문서 (mechanic / world / mapping) + 7 ADR + 3 global rule YAML + 4 NPC YAML. 코드 0줄 — Phase 0는 *모든 narrative/lore가 데이터로 표현되고, 모든 결정이 ADR로 기록되는* 토대 만들기.

**Architecture:** 모든 narrative/lore가 YAML 데이터. 모든 결정이 ADR. 모든 spec이 Phase 1에서 시스템 프롬프트 빌더가 읽을 준비가 됨. 게임 밸런스 튜닝 = YAML 수정, 코드 수정 X.

**Tech Stack:** Markdown (spec / ADR / CLAUDE.md), YAML (NPC + rule 데이터), git (audit trail). 코드 의존성 0. Phase 1.0 진입 시 Python + pyyaml + Jinja2 도입 예정.

---

## File Structure

이 plan 실행 결과 생성/이동되는 파일:

| 파일 | 책임 |
|---|---|
| `CLAUDE.md` | Claude Code가 이 레포에서 따라야 할 룰 |
| `docs/mechanic-spec.md` | 기존 PRD 이관. 시스템/메커니즘/인프라/일정의 권한 spec |
| `docs/world-spec.md` | 망각의 섬 lore + 4 NPC forgotten_life |
| `docs/mapping-spec.md` | mechanic ↔ lore 매핑표 + drift 방지 룰 |
| `docs/adr/0001-mechanic-design-hardened.md` | 기존 13개 grilling 결정 batch reference |
| `docs/adr/0002-add-world-spec-layer.md` | world-spec layer 추가 결정 |
| `docs/adr/0003-hyean-as-unforgetting-one.md` | 혜안 lore 재해석 |
| `docs/adr/0004-name-reclamation-asymmetry.md` | boat moment 이름 회수 비대칭 |
| `docs/adr/0005-defer-cult-archetype-v1.1.md` | 사이비 archetype v1.1 deferral |
| `docs/adr/0006-spec-driven-repo-structure.md` | spec-driven repo 구조 결정 |
| `docs/adr/0007-rename-still-here-to-nanpaseom.md` | 제목 변경 |
| `rules/awareness_bands.yaml` | global: band → choice_count, tone_palette |
| `rules/memory_tags.yaml` | global: 10-tag vocabulary + clamp 규칙 |
| `rules/boat_outcomes.yaml` | global: boat moment 5분기 분류 규칙 |
| `npcs/repairwoman.yaml` | 수리공 spec |
| `npcs/fisherwoman.yaml` | 어부 spec |
| `npcs/grandmother.yaml` | 할머니 spec |
| `npcs/hyean.yaml` | 혜안 spec (신규 lore + 85+ 라인 교체) |

---

## Task 1: CLAUDE.md 작성

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md content**

Write to `CLAUDE.md`:

```markdown
# 난파섬 (Nanpaseom) — Spec-driven Repo Rules

이 파일은 Claude Code가 이 레포에서 작업할 때 반드시 따라야 할 룰입니다.

## 작업 전 컨텍스트 로드

코드 / spec / NPC YAML / rule YAML 수정 전, 항상 다음을 읽으세요:

- 영향받는 `docs/*-spec.md` 섹션
- 영향받는 `npcs/*.yaml` 파일
- 영향받는 `rules/*.yaml` 파일
- 관련된 `docs/adr/*.md` 결정 기록

## NPC 추가 / 수정 룰

- NPC 대사 / 톤 / `forgotten_life` 추가는 `npcs/*.yaml`에만. **코드에 하드코딩 금지**.
- 시스템 프롬프트는 **빌더가 YAML에서 생성**. 직접 작성 / 직접 수정 금지.
- NPC 새 결정 (e.g. memory_tag affinity 변경) 시 ADR 작성 후 YAML 갱신.

## 메커니즘 변경 룰

- 메커니즘 변경 시 `docs/mechanic-spec.md` + `docs/mapping-spec.md` **둘 다** 갱신.
- mapping-spec.md의 해당 행은 *암묵적 표류 금지* — 명시적 정렬.

## 새 결정 룰

새 디자인 결정 / 락-인된 trade-off 발생 시:
1. "ADR 거리인가?" 자문
2. ADR이라면 `docs/adr/NNNN-<topic>.md` 작성 (4자리 숫자, 시퀀셜)
3. ADR 작성 후 영향받는 spec / YAML 갱신
4. commit per ADR (audit trail)

## YAML 스키마

YAML 파일은 *기계 가독 spec*. 다음 룰:

- `npcs/*.yaml` 최상위 키: `identity`, `sprite`, `voice`, `memory_tag_affinity`, `ending_gates`, `awakening_guidelines`, `diegetic_fallback` 필수
- `rules/*.yaml` — 각 룰 파일은 자체 스키마 (Phase 1.0 빌더 구현 시 jsonschema 형식화)
- YAML 추가 / 수정 후 *모든 YAML이 파싱되는지* sanity check

## Git 룰

- commit은 *logical unit per file* (NPC 1개 추가 = 1 commit, ADR 1개 = 1 commit)
- commit 메시지는 한국어 OK. 결정 *이유*가 명시되어야 함
- 절대 `git commit --no-verify` / `--no-gpg-sign` 사용 금지

## 학습 메타-룰

이 프로젝트는 **spec-driven workflow** 학습 vehicle입니다. 다음을 우선:

- 손빠른 우회보다 **명시적 spec 흐름**
- 결정은 **기록**된다 (ADR)
- spec이 **코드를 생성**한다 (시스템 프롬프트 빌더, Phase 1.0+)
- 게임 밸런스 튜닝은 **코드 수정이 아니라 YAML 수정**

## 참조 문서

- 상위 합의문: `docs/superpowers/specs/2026-05-11-nanpaseom-worldview-and-spec-driven-setup.md`
- 메커니즘 권한: `docs/mechanic-spec.md`
- 서사 권한: `docs/world-spec.md`
- 정렬 권한: `docs/mapping-spec.md`
```

- [ ] **Step 2: Verify content**

Run: `wc -l CLAUDE.md && head -3 CLAUDE.md`

Expected: ~60 lines, first 3 lines start with `# 난파섬 (Nanpaseom) — Spec-driven Repo Rules`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
Add CLAUDE.md spec-driven repo rules

코드 수정 전 spec 로드, NPC 대사는 yaml에만, 시스템 프롬프트는
빌더가 생성, 결정은 ADR로 기록. 학습 vehicle 룰 명시.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: 기존 PRD를 docs/mechanic-spec.md로 이관

**Files:**
- Move: `arden-main-design-20260424-014454.md` → `docs/mechanic-spec.md`

- [ ] **Step 1: Confirm PRD file exists at repo root**

Run: `ls -la arden-main-design-20260424-014454.md`

Expected: 파일 존재, 약 59KB, 705 라인.

- [ ] **Step 2: Move file**

PRD가 아직 git tracked가 아니므로 일반 `mv` 사용:

```bash
mv arden-main-design-20260424-014454.md docs/mechanic-spec.md
```

(만약 git tracked였다면 `git mv`를 사용해야 history 보존.)

- [ ] **Step 3: Verify move**

Run: `ls docs/mechanic-spec.md && wc -l docs/mechanic-spec.md`

Expected: 705 lines.

- [ ] **Step 4: Commit**

```bash
git add docs/mechanic-spec.md
git commit -m "$(cat <<'EOF'
Move PRD to docs/mechanic-spec.md

기존 hardened mechanic PRD를 docs/ 하위로 이관. 내용 그대로 보존.
이 파일은 시스템 / 메커니즘 / 인프라 / 일정의 권한 spec.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: docs/world-spec.md 작성

**Files:**
- Create: `docs/world-spec.md`

- [ ] **Step 1: Write world-spec.md content**

아래 내용은 *draft*. 디자이너(Arden)가 forgotten_life 백스토리를 자기 voice로 다듬을 자유 있음 — 단, 백스토리가 memory_tag vocab과 정합해야 (`core_wound` 필드).

Write to `docs/world-spec.md`:

```markdown
# 난파섬 — World Spec (망각의 섬)

이 문서는 *서사 권한* spec. 메커니즘 권한은 `mechanic-spec.md`, 정렬 권한은 `mapping-spec.md`.

## Premise

어딘가의 외딴 섬. 사람들이 *잊고 싶음 / 후회 / 도망 / 포기*의 감정 무게로 떠밀려 흘러오는 곳 — **자발적 도착이 아니다**. 도착한 자는 점차 자아를 잃고 자기 행위(직업 / 관계 / 의식)만 반복하는 NPC가 된다.

섬은 **망각을 보존하는 시스템**이다. NPC들의 트로프 행위 — 망치질, 그물 당김, 손짓, 파도 응시 — 가 그 시스템의 작동 형태다. 의미는 비었는데 행위는 남는다.

보트는 처음부터 있는 게 아니다. **떠나고 싶다는 의지가 회복된 자에게만 보인다.**

## 플레이어

풍랑을 만나 죽기 직전 *반포기 상태*에서 흘러옴. 자기도 망각의 대상이었으나, NPC들과 대화하면서 자기 자신의 깨어남도 동시 진행된다.

게임 마지막에 "이게 현실인지 꿈인지" 모호함이 *thematic layer*로 남는다 — binary reveal 없음. 보트 모먼트 메타 엔딩 모놀로그가 양쪽 해석 모두 허용.

## 두 종류의 깨어남

이 섬의 NPC는 *깨어남의 종류*에 따라 두 부류로 나뉜다:

- **기억하는 깨어남** (수리공, 어부, 할머니) — 잊었던 것을 다시 떠올리는 깨어남. 망각 → 회복.
- **수긍하는 깨어남** (혜안) — "역시 그랬구나"의 깨어남. 처음부터 망각에 실패해 있었던 자의, 자기 본질을 정면으로 인정하는 순간.

이 비대칭은 게임의 narrative ecology를 정교하게 만든다. 4 NPC 중 1명만 다른 종류라는 사실이 4-corner symmetric matrix보다 풍부함.

## 4 NPC의 자리

### 수리공 — 망각 성공 / purpose-loop 갇힘

forgotten_life:
- 한때 누군가에게 *완성해주겠다*고 약속한 게 있던 사람. 집이었을 수도, 가족 형태였을 수도, 인생이었을 수도. 결국 완성하지 못한 채 떠나야 했다.
- 손은 일을 기억하는데, *무엇을 위한 일인지*는 잊었다. 그래서 손이 도구를 놓지 못한다.
- core_wound: `purpose` — 의미를 채울 수 없는 일을 반복하는 자.

망각의 의식: 망치질. 보트 잔해 옆에 앉아 끊임없이 두드린다. 보트는 절대 수리되지 않는다 — 수리되는 *것*이 본래 없기 때문이다.

루비 무한 루프와의 연결: 수리공이 "더 필요해"라고 말하는 건 *결핍감을 유지*하는 자가-기제. 결핍이 있어야 망각이 계속된다.

### 어부 — 망각 성공 / transaction-loop 갇힘

forgotten_life:
- 한때 *교환*으로 사람들을 연결하던 사람. 시장에서, 흥정에서, 거래에서 자기를 인정받았다.
- 어느 순간 자기가 거래해온 게 *가치 없는 것*이었다는 걸 깨달았다 — 사기였든, 자기기만이었든, 시대 변화였든.
- 그래서 거래의 *행위*만 남고 *대상*은 비어버렸다. 루비라는 가짜 화폐를 받아주는 건 그녀가 거래를 *멈출 수 없기* 때문.
- core_wound: `purpose`, `pride`.

망각의 의식: 그물 당김. 잡히는 게 없어도 그물을 끌어올린다. 어부의 시그니처 깨어남 모먼트는: "이 루비들… 너한테서 받아왔어. *어디서* 가져왔지?" — 거래의 대상이 비어있음을 처음으로 인지하는 순간.

### 할머니 — 망각 부분 실패 / time-loop awareness

forgotten_life:
- 가장 오랜 시간 사랑한 사람을 잃고 흘러옴. 시간이 사람을 데려가는 것을 *본* 사람.
- 그래서 시간 자체에 대한 감각이 다른 NPC보다 예민하다. 결국 *루프*를 감지한다.
- *기다리는* 자세는 그녀가 잃은 사람을 기다리는 자세의 잔영.
- core_wound: `love`, `loss`, `family`, `home`.

망각의 의식: 앉아있음, 손짓. 가장 오래 머문 자의 자세. 시그니처 깨어남 라인: *"나… 이 대화 수백 번 했어."*

구조적 역할: 다른 NPC의 *visible state* (sprite A↔B) 관찰을 시스템 프롬프트에 hint로 주입받음. memory_tags나 awareness 숫자는 보지 못함 — *행동만* 본다.

### 혜안 — 망각 완전 실패 / 못 잊은 자

forgotten_life:
- 어렸을 때부터 사람들이 "쟤는 눈이 밝다, 혜안이 있다"고 부른 아이. 그게 그녀의 이름이 됐다.
- 자라며 능력이 됐고, 능력이 짐이 됐다. 거짓말, 사람들의 속내, 사회의 모순이 다 보였다.
- 견딜 수 없어진 그녀는 *더 이상 보지 않으려* 망각의 섬으로 흘러왔다.
- 그러나 섬조차 그녀의 눈을 막지 못한다. 그녀는 사람을 안 보려고 등 돌리고 파도만 본다. 파도는 패턴이라 의미가 없어 안전하다.
- core_wound: `pattern`, `fear`, `loss`, `home`.

망각의 의식: 등 돌리고 파도 응시. *사람을 안 보는* 의식.

다른 NPC와의 비대칭:
- 다른 셋은 *호칭만 남은 자* (수리공 / 어부 / 할머니 — 모두 역할). 망각이 깊을수록 자기 이름이 사라지고 기능만 남는다.
- 혜안만 *이름밖에 안 남은 자*. 그녀의 이름 "혜안"(慧眼)은 원래 그녀에게 주어진 이름이자 능력이자 저주.

이름의 회수도 다르다:
- 다른 셋은 boat moment에서 *처음으로 자기 이름을 기억해낸다* ("나는… 박OO이었어").
- 혜안만은 그 순간이 없다. 애초에 잊은 적이 없으니까. 대신 이름의 *의미가 전환*된다: *"내 이름이 혜안인 건 저주였어. 근데 이제는…"*

혜안의 깨어남은 *체념 + 발견* progression이다. 사람을 안 보려 했던 자가 처음으로 *동행*을 발견하는 과정.

## 섬의 메커니즘 = 망각의 메커니즘

기존 PRD의 모든 시스템적 요소는 *망각의 섬이 작동하는 방식*이다. 자세한 매핑은 `mapping-spec.md`에 있고, 핵심은:

- 망각이 깊으면 NPC는 트로프 안에 갇힌다 (state A).
- 깨어남이 진행되면 NPC가 정면을 본다 (state B). 망각의 의식이 멈춘다.
- 보트가 보이는 건 *떠나고 싶다는 의지의 회복*. 의식주 / 통화 / 거래는 모두 *결핍감*을 통한 망각 유지 시스템.
- 글로벌 awareness ≥40에서 풍경 mutter는 망각 시스템이 *흔들리기 시작*하는 신호.

## v1.1 후보 — 사이비 archetype

5번째 NPC archetype 후보로 *사이비 / 전도하는 자*. 망각의 섬의 *자기-보존 면역체계*. 다른 NPC가 깨어나려 할 때 다시 잊도록 끌어들이는 자.

혜안과의 대조: 혜안 = 진짜 자아 못 놓은 자, 사이비 = 가짜 자아 덮어쓴 자. 둘 다 망각에 실패했지만 *실패의 방향이 정반대*.

v1 출시 후 엔딩 다양성 검토 시 추가 결정 (ADR 0005).
```

- [ ] **Step 2: Verify content**

Run: `wc -l docs/world-spec.md && head -5 docs/world-spec.md`

Expected: ~90+ lines, starts with `# 난파섬 — World Spec`.

- [ ] **Step 3: Commit**

```bash
git add docs/world-spec.md
git commit -m "$(cat <<'EOF'
Add docs/world-spec.md — 망각의 섬 lore + 4 NPC forgotten_life

기존 mechanic-spec의 missing 서사 층위를 채움. 4 NPC의 origin
(어떤 사람이었고, 무엇으로부터 도망쳐왔는지). 두 종류의 깨어남
비대칭. 혜안의 "이름밖에 안 남은 자" 위치 명시. 사이비 v1.1 노트.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: docs/mapping-spec.md 작성

**Files:**
- Create: `docs/mapping-spec.md`

- [ ] **Step 1: Write mapping-spec.md content**

Write to `docs/mapping-spec.md`:

```markdown
# 난파섬 — Mapping Spec (Mechanic ↔ Lore)

이 문서는 *정렬 권한* spec. `mechanic-spec.md` (시스템)와 `world-spec.md` (서사)의 정합을 보장한다.

## Mapping Table

| Mechanic (PRD) | Lore (망각의 섬) |
|---|---|
| Shipwreck frame (플레이어가 난파선으로 도착) | 반포기 상태로 떠밀려옴 (자발 X) |
| NPC가 트로프에 갇힘 | 망각의 의식(ritual)이 자아의 빈자리를 채움 |
| Awareness gauge 0-100 | 잃어버린 자아의 복원도 |
| memory_tags 10종 (family, loss, regret, pride, betrayal, home, fear, love, pattern, purpose) | 도망쳐 온 원래 삶의 파편 |
| 3→2→1→0 UI 축소 | 주어진 선택지가 줄고 *자기 언어*가 회복됨 |
| 보트 5분기 엔딩 | "떠나고 싶은 의지"의 회복 양상 |
| 보트는 ≥1 NPC awareness 85+에 등장 | 보트는 *의지가 있는 자에게만 보임* |
| 루비 무한 루프 (수리공 "더 필요해") | 결핍감으로 망각을 유지하는 자가-기제 |
| 카운터 글리치 사라짐 (boat moment) | 결정 순간에 환각이 무너짐 |
| 글로벌 awareness ≥40 mutter | 망각 시스템이 *흔들리기 시작*하는 신호 |
| Sprite state A → B 전환 (awareness 60+) | 망각의 의식이 멈춤. *처음으로 정면을 본다* |
| 할머니의 시각적 hint (다른 NPC state A↔B 관찰) | 가장 오래 머문 자가 *루프의 가장자리*를 본다 |
| 혜안의 4-band escalation | 사람을 안 보려 했던 자가 *처음으로 동행을 발견*하는 과정 |
| 혜안의 boat moment 라인 ("내 이름이 혜안인 건 저주였어. 근데 이제는…") | 이름의 의미 *전환*. 다른 셋의 "나는 박OO이었어" 회수와 다른 종류 |
| 자유 입력 안전 4-layer + 2-strike sexual/harassment | 섬의 *유한한 인내심*. 망각을 의지로 회복하러 온 자에게는 응답, 파괴하러 온 자에게는 차단 |
| 회차 (playthrough) 모델 | 망각의 섬은 끝없이 다른 사람을 받아들인다. *플레이어*는 회차마다 새 인격 |
| 할머니의 시그니처 "나… 이 대화 수백 번 했어" | 가장 오래 머문 자만이 *루프 자체*를 감지함 |

## Drift 방지 룰

이 매핑은 *살아있다*. 변경 룰:

1. 메커니즘 신규 추가 / 변경 시 → 이 표에 행 추가 / 갱신
2. lore 신규 추가 / 변경 시 → 이 표에 행 추가 / 갱신
3. 표에 *없는 메커니즘이 발견되면* → drift. 둘 중 하나:
   - 메커니즘이 lore 없이도 정당화되면 → "no lore" 행으로 명시 추가 (예외 등록)
   - 그렇지 않으면 → lore 추가 or 메커니즘 제거
4. PR에서 `mechanic-spec.md` / `world-spec.md` 변경이 있는데 `mapping-spec.md`가 변경되지 않았다면 → 리뷰 reject

이 룰은 *암묵적 표류 금지*가 목적. 메커니즘과 lore가 따로 진화하는 걸 막는다.

## 미매핑 항목 (의도적)

다음은 *lore 의미 없이* 메커니즘 자체의 implementation detail로 둠:

- LLM 백엔드 tiered failover (Premise 4)
- Postgres 스키마
- Mac Mini / Cloudflare Tunnel 인프라
- Mobile responsive layout
- CC0 픽셀 아트 sourcing

이들은 망각의 섬 lore와 무관한 *제작 결정*. mapping table은 *게임 안에서 플레이어가 경험하는 메커니즘*에 한정.
```

- [ ] **Step 2: Verify content**

Run: `wc -l docs/mapping-spec.md && grep -c "^|" docs/mapping-spec.md`

Expected: ~45+ lines, ~17+ pipe-separated rows (table rows + header + separator).

- [ ] **Step 3: Commit**

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

## Task 5: ADR 0001 — Mechanic Design Hardened (batch reference)

**Files:**
- Create: `docs/adr/0001-mechanic-design-hardened.md`

- [ ] **Step 1: Write ADR content**

Write to `docs/adr/0001-mechanic-design-hardened.md`:

```markdown
# ADR 0001: Mechanic Design Hardened (Batch Reference)

- Status: Accepted
- Date: 2026-05-09 (hardened), 2026-05-11 (이관)
- Deciders: Arden (디자이너), `office-hours` skill, `grill-me` skill

## Context

기존 `ego-in-npc` 프로젝트에서 메커니즘 설계가 13개 design branch로 hardening grilling 세션을 거쳤다. 결정사항이 `docs/mechanic-spec.md`의 "## Hardening Log (2026-05-09)" 섹션에 요약되어 있다.

본 ADR은 그 13개 결정을 *batch reference*로 인용한다. 추후 grilling 결정 세분화가 필요하면 0001a, 0001b… 또는 별도 ADR로 분기.

## Decisions Hardened (Summary)

1. 출시명 "Still Here" → 본 레포 시점에 **난파섬 / Nanpaseom**으로 변경 (ADR 0007 참조)
2. 엔딩 모델 — NPC별 엔딩은 *beats*, 게임의 진짜 엔딩 = **떠남 (보트 모먼트)**. 5 분기.
3. 네비게이션 — (b) tap-to-talk 고정 풍경. 자유 이동은 v1.1+.
4. 시각 시스템 — 4 NPC × 2 state = 8 sprite. 전환 awareness 60+에 한 번에.
5. 경제 — 라이트 1-tap 낚시 + 단일 통화 루비. 수리공 무한 루프 (절대 충족 X). 보트 모먼트 진입 시 카운터 글리치 사라짐.
6. `memory_tags` 10개 — 기존 8 + `pattern` + `purpose`.
7. 회차 모델 — 회차마다 NPC state reset, 엔딩 저널만 누적.
8. 풍경 ambient mutter — 글로벌 ≥ 40 + 30초 idle 시 random NPC. 60줄 pre-authored.
9. 안전 4 layers + 성적/혐오 2-strike — Strike 2 = 영구 차단 + 세이브 코드 무효화.
10. 할머니의 hint — 다른 NPC의 *visible state* (sprite A/B)만 관찰. memory_tags 비공개.
11. 혜안의 audio-independent awakening — 대사 자체가 자기충족. 오디오는 atmosphere QoL.
12. Trust gauge 컷 from v1 — 두 변수 (awareness, memory_tags)만으로 ending variety.
13. 풀 메타-기억 (회차 간 NPC 기억) deferred to v1.1.

## Consequences

- 본 batch reference로 13개 결정이 한 번에 인용된다. 세부 사항은 `docs/mechanic-spec.md`가 권한.
- 본 ADR을 *분해* (0001a, 0001b…)할지는 학습 효용 측면에서 추후 평가. 분해하면 각 결정을 독립 트레이드오프로 학습 가능. Batch면 빠른 셋업.
- 본 batch reference는 *역사적 기록*. 미래 결정은 새 ADR.

## Related

- `docs/mechanic-spec.md` (Hardening Log 섹션이 본 batch의 long-form)
- ADR 0002 (world-spec layer 추가가 이 batch에 *추가*되는 결정)
- ADR 0007 (출시명 변경 — 이 batch의 결정 #1을 덮어씀)
```

- [ ] **Step 2: Verify content**

Run: `wc -l docs/adr/0001-mechanic-design-hardened.md`

Expected: ~30+ lines.

- [ ] **Step 3: Commit**

```bash
git add docs/adr/0001-mechanic-design-hardened.md
git commit -m "$(cat <<'EOF'
Add ADR 0001 — Mechanic Design Hardened (batch reference)

기존 13개 grilling 결정을 batch reference로 인용. 세부 사항은
mechanic-spec.md 권한. 본 ADR 분해는 추후 학습 효용 기준 평가.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: ADR 0002 — Add World-spec Layer

**Files:**
- Create: `docs/adr/0002-add-world-spec-layer.md`

- [ ] **Step 1: Write ADR content**

Write to `docs/adr/0002-add-world-spec-layer.md`:

```markdown
# ADR 0002: Add World-spec Layer

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

기존 mechanic-spec (PRD)는 시스템 층위가 13개 grilling으로 정밀하게 hardened되어 있으나 *서사 층위*가 비어있다. *왜* NPC가 트로프에 갇혀있는지, *왜* 플레이어는 떠나야 하는지의 동기 부여가 약해, 코드가 중구난방으로 짜이고 디자이너의 멘탈 모델이 흔들렸다.

이전 레포에서 narrative-less 메커니즘으로 코드 작업하다 *학습 효용까지* 떨어진 게 root cause.

## Decision

`docs/world-spec.md`를 신설한다. **망각의 섬** 세계관 + 4 NPC `forgotten_life` 백스토리를 담는다.

원칙:
- world-spec은 *서사 권한*. mechanic-spec과 *독립적*으로 진화한다.
- mechanic / world의 정합은 `docs/mapping-spec.md`가 *제3의 권한*으로 보장.
- 메커니즘 변경 0. world-spec은 *해석 레이어*.

## Alternatives Considered

- **(a) 기존 PRD 갈아엎고 새로 작성** — 13개 hardening cost를 폐기. 12-16주 사이클 재시작. 학습 vehicle 손실.
- **(b) ★ chosen** — 메커니즘 그대로 + world-spec 신설 + mapping-spec 신설. 메커니즘이 lore와 1:1로 매핑됨. 학습 vehicle 보존 + 서사 보강.
- **(c) world를 mechanic-spec 안에 섹션으로** — 두 layer가 한 문서 안에 섞이면 *왜 이 메커니즘인지*가 명시화되지 못함. drift 위험.

## Consequences

- 향후 결정은 *세 spec 중 어느 권한인지*가 명시되어야 함.
- 메커니즘 변경 시 mapping-spec 동기화 의무 (drift 방지).
- world-spec이 너무 강해져 메커니즘이 변경 압력 받을 수 있음 — 이 경우 ADR로 명시.

## Related

- `docs/world-spec.md` (이 ADR의 산출물)
- `docs/mapping-spec.md` (mechanic ↔ world 정렬 권한)
- 상위 합의문: `docs/superpowers/specs/2026-05-11-nanpaseom-worldview-and-spec-driven-setup.md`
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0002-add-world-spec-layer.md
git commit -m "$(cat <<'EOF'
Add ADR 0002 — World-spec layer 추가

mechanic-spec의 서사 부재가 코드 중구난방의 root cause로 진단.
world-spec / mapping-spec 신설로 메커니즘 보존 + 서사 보강.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: ADR 0003 — 혜안 as Unforgetting One

**Files:**
- Create: `docs/adr/0003-hyean-as-unforgetting-one.md`

- [ ] **Step 1: Write ADR content**

Write to `docs/adr/0003-hyean-as-unforgetting-one.md`:

```markdown
# ADR 0003: 혜안 as the Unforgetting One

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

기존 PRD에서 4 NPC 중 혜안만 *진짜 이름*이고 나머지 셋(수리공/어부/할머니)은 *트로프 직함*이다. 이 비대칭이 새 망각의 섬 lore와 충돌하는지 평가가 필요했다.

초기 brainstorming에서 *혜안 → 사이비 archetype 교체*를 검토 (디자인 일관성 회복 목적). Arden이 강력한 반박: **"혜안만 진짜 이름이라는 비대칭은 디자인 bug가 아니라 lore feature"**.

## Decision

혜안을 *그대로 유지*. lore를 재해석:

- 다른 셋 = *호칭만 남은 자* (망각이 깊을수록 이름이 사라지고 기능만 남음)
- 혜안 = *이름밖에 안 남은 자* (망각 완전 실패 — 본 것의 무게에 짓눌려 도망 왔지만 섬조차 그녀의 눈을 못 막음)

혜안의 awakening은 **수긍하는 깨어남** ("역시 그랬구나"). 다른 셋의 *기억하는 깨어남*과 종류가 다름. 4-corner symmetric matrix가 아니라 *3 + 1 메타* 구조 → narrative ecology가 더 정교.

기존 4-band escalation의 85+ 라인 교체:
- 기존: "파도가 진짜라면 이렇게 반복될 리 없어. 우리... 어디에 있는 거야?" (세계 자각)
- 신규: **"이미 알고 있었어. 처음부터. 그저… 더 보고 싶지 않았던 거야."** (자기 자각)

0-30 / 30-60 / 60-85 라인은 *대사 유지*, 톤 라벨만 *체념 + 발견 progression*으로 명시.

## Alternatives Considered

- **(a)** 혜안 → 사이비 archetype 교체 (4명 다 트로프 직함 통일). 초기 추천.
- **(b) ★ chosen** — 혜안 유지 + lore 재해석. 이름 비대칭이 *feature*로 작동.
- **(c)** 5번째 NPC로 사이비 추가 (v1 5명). 솔로 dev scope 폭주.

## Consequences

- 혜안의 모든 톤 차이 (시적/차가운 대사, 등 돌린 자세, audio-loop 인지)가 lore-justified됨.
- Boat moment에서 혜안만 다른 회수 — 이름의 *의미 전환* (ADR 0004 참조).
- 사이비 archetype은 v1.1로 deferral (ADR 0005). 혜안과 거울 관계.
- 혜안의 `memory_tag_affinity` 유지 (pattern, fear, loss, home) — lore 변경에도 합치.

## Related

- ADR 0004 (boat moment 이름 회수 비대칭)
- ADR 0005 (사이비 v1.1 deferral)
- `npcs/hyean.yaml` (이 ADR의 spec 출력)
- `docs/world-spec.md` "혜안" 섹션
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0003-hyean-as-unforgetting-one.md
git commit -m "$(cat <<'EOF'
Add ADR 0003 — 혜안 as the unforgetting one

이름 비대칭 (혜안만 진짜 이름)을 디자인 bug에서 lore feature로 전환.
"기억하는 깨어남" 3명 + "수긍하는 깨어남" 1명 (혜안)의 3+1 메타 구조.
85+ 라인 자기 자각으로 교체. Arden 반박으로 초기 추천 철회.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: ADR 0004 — Name Reclamation Asymmetry

**Files:**
- Create: `docs/adr/0004-name-reclamation-asymmetry.md`

- [ ] **Step 1: Write ADR content**

Write to `docs/adr/0004-name-reclamation-asymmetry.md`:

```markdown
# ADR 0004: Boat Moment Name Reclamation Asymmetry

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

기존 PRD의 boat moment 메타 엔딩 모놀로그는 4 NPC 모두 *동일 형식*으로 LLM 합성된다. 새 world-spec lore (ADR 0002, 0003) 도입으로 *이름의 무게*가 narrative 핵심 element로 부상.

특히 ADR 0003의 *3 + 1 비대칭 구조*가 boat moment에서도 명시적으로 표현되어야 narrative ecology가 닫힌다.

## Decision

Boat moment에 *이름 회수 비대칭*을 추가:

- **수리공 / 어부 / 할머니** — boat moment 메타 엔딩 모놀로그에서 *처음으로 자기 이름을 기억해냄*. 예: "나는… 박OO이었어" / "정OO이었네". LLM 입력에 `name_candidates` 풀이 들어가고, LLM이 상황에 어울리는 이름 합성.

- **혜안** — 이름 회수 없음. 애초에 잊은 적 없음. 대신 이름의 *의미 전환*: **"내 이름이 혜안인 건 저주였어. 근데 이제는…"** — 저주가 정체성으로 전환되는 순간.

NPC YAML `identity.forgotten_life.name_candidates` 필드 신설 (혜안 제외 3명). LLM 입력 시 빌더가 이 풀에서 *상황 적합한* 후보를 컨텍스트로 주입.

## Alternatives Considered

- **(a)** 4명 모두 이름 회수 동일 형식 (기존). 비대칭 손실.
- **(b) ★ chosen** — 3명 회수 + 1명 의미 전환. 비대칭이 narrative ecology 정합.
- **(c)** LLM이 *자기 판단*으로 회수 or 의미 전환 선택. 결정론 약해서 *디자인 의도가 우연에 의존*.

## Consequences

- 4개 NPC YAML 중 3개에 `name_candidates` 풀 작성 필요 (Phase 0.6 / 디자이너 작업).
- 혜안 YAML에는 *의미 전환 라인 템플릿* 명시.
- Boat moment LLM 합성 프롬프트가 NPC별로 *조건부 분기* 필요 (Phase 1.0+ 빌더에서 구현).
- 회차 (playthrough) 모델에서 이름 후보 풀은 *유지* (회차마다 다른 이름 가능).

## Related

- ADR 0003 (혜안의 unforgetting positioning)
- `docs/world-spec.md` "4 NPC의 자리" 섹션
- `npcs/*.yaml` `identity.forgotten_life.name_candidates` 필드
- mechanic-spec "Departure Ending (Boat Moment)" 섹션 (추후 이 비대칭 명시 갱신 필요 — 별도 PR)
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0004-name-reclamation-asymmetry.md
git commit -m "$(cat <<'EOF'
Add ADR 0004 — boat moment 이름 회수 비대칭

3명 회수 (수리공/어부/할머니) + 1명 의미 전환 (혜안). 3+1 비대칭이
boat moment에서 명시화. NPC YAML에 name_candidates 풀 필드 신설.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: ADR 0005 — Defer Cult Archetype to v1.1

**Files:**
- Create: `docs/adr/0005-defer-cult-archetype-v1.1.md`

- [ ] **Step 1: Write ADR content**

Write to `docs/adr/0005-defer-cult-archetype-v1.1.md`:

```markdown
# ADR 0005: Defer 사이비 Archetype to v1.1

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

망각의 섬 lore brainstorming 중 *사이비 / 전도하는 자* archetype이 강력한 narrative 후보로 부상:
- "우리 모임에 들어와요" 에너지가 망각의 섬 self-preservation 면역체계와 완벽 정합
- ADR 0003 혜안 (진짜 자아 못 놓은 자)과 *거울 관계* (가짜 자아 덮어쓴 자)

그러나 v1 4-NPC 슬롯에 *사이비 + 혜안 둘 다* 넣으면:
- 솔로 dev scope 폭주 (8 sprite → 10 sprite + 추가 5+ ADR + 시스템 프롬프트 builder 확장)
- 두 *유사 트로프* (둘 다 망각에 실패한 자) 가 같이 들어가면 narrative 중복

## Decision

사이비 archetype은 **v1.1 후보**로 deferral. v1 4-NPC 슬롯은 (수리공 / 어부 / 할머니 / 혜안)으로 락-인.

v1.1 추가 결정 트리거:
- v1 출시 후 엔딩 다양성이 부족 (5분기 outcome이 너무 수렴) — PRD Open Questions #7 참조
- 또는 디자이너가 5번째 NPC 추가 자원 있음 + 사이비 narrative에 강한 끌림

추가 시 혜안과 거울 관계로 작동:
- 혜안: 진짜 자아 못 놓은 자 (망각 실패 → 사람을 안 봄)
- 사이비: 가짜 자아 덮어쓴 자 (망각 실패 → 사람을 *너무* 봄, 인도하려 함)

## Alternatives Considered

- **(a)** v1에 사이비 추가 (5-NPC). scope 폭주.
- **(b)** 혜안 → 사이비 교체 (4-NPC). ADR 0003에서 이미 기각.
- **(c) ★ chosen** — 사이비 v1.1로 미룸. v1은 hardened 4명.

## Consequences

- v1 출시까지 사이비 archetype 작업 0.
- v1.1 진입 시 본 ADR 갱신 (Status: Superseded by 00XX-add-cult-archetype.md).
- `docs/world-spec.md` "v1.1 후보 — 사이비 archetype" 섹션에서 이 의도 보존.

## Related

- ADR 0003 (혜안 유지 결정)
- `docs/world-spec.md` "v1.1 후보" 섹션
- PRD `## v1.1 Deferrals` 섹션
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0005-defer-cult-archetype-v1.1.md
git commit -m "$(cat <<'EOF'
Add ADR 0005 — 사이비 archetype v1.1 deferral

v1 4-NPC 슬롯에 사이비+혜안 둘 다는 scope 폭주. 사이비는 v1.1.
v1.1 추가 시 혜안과 거울 관계 (진짜 자아 못 놓음 vs 가짜 자아 덮음).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: ADR 0006 — Spec-driven Repo Structure

**Files:**
- Create: `docs/adr/0006-spec-driven-repo-structure.md`

- [ ] **Step 1: Write ADR content**

Write to `docs/adr/0006-spec-driven-repo-structure.md`:

```markdown
# ADR 0006: Spec-driven Repo Structure

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden, `superpowers:brainstorming`

## Context

이전 레포의 root cause 진단 (ADR 0002):
- 메커니즘 spec은 정밀했으나 narrative 부재
- 결과: 코드 중구난방, 디자이너 멘탈 모델 흔들림, *학습 효용까지* 떨어짐

새 레포 셋업에 *spec-driven workflow* 학습 vehicle을 1순위로 박는다. Arden의 메타 학습 목표:
- spec-driven workflow
- rule-based automation
- structured context
- agent execution environment design

## Decision

새 레포 구조를 다음과 같이 박는다:

```
nanpaseom/
├── CLAUDE.md                       # Claude Code 룰
├── docs/
│   ├── mechanic-spec.md
│   ├── world-spec.md
│   ├── mapping-spec.md
│   ├── superpowers/{specs,plans}/  # 합의문 + 실행 plan
│   └── adr/                        # 결정 1장 = 1파일
├── npcs/                           # per-NPC YAML
│   └── <name>.yaml
└── rules/                          # global rule YAML
    └── <category>.yaml
```

원칙:
- **모든 narrative/lore가 데이터** (YAML)
- **모든 결정이 ADR**
- **시스템 프롬프트는 빌더가 YAML에서 생성** (코드 하드코딩 금지)
- **게임 밸런스 튜닝 = YAML 수정**, 코드 수정 X

Phase 0 산출물:
- 3-spec 문서 (mechanic / world / mapping)
- 7 ADR (0001-0007)
- 3 global rule YAML
- 4 NPC YAML
- CLAUDE.md

Phase 1.0에서 시스템 프롬프트 빌더 (Python + Jinja2 + jsonschema) 도입. YAML 스키마 검증 + 시스템 프롬프트 렌더링.

## Alternatives Considered

- **(a) Minimal** — 단일 PRD + 단순 CLAUDE.md. 학습 vehicle 약함, 지금이랑 별 차이 없음.
- **(b) ★ chosen** — 3-spec + ADR + per-NPC YAML + rule YAML + builder. spec이 코드를 생성.
- **(c) Full** — (b) + Claude Code 슬래시 커맨드 + pre-commit 훅 + CONTEXT.md. 진입장벽 높아 "정신 없는 상태" 재발 위험.

(c) 요소는 (b) 굴러가다가 *진짜 필요할 때* 하나씩 추가.

## Consequences

- 새 결정마다 *어느 spec / 어느 YAML / 어느 ADR*이 권한인지 명시 의무.
- CLAUDE.md가 *Claude Code의 협업 룰*. 자동화 X, 명시화 O.
- 시스템 프롬프트 직접 수정 금지 (빌더 통해서만).
- Phase 1.0 빌더 구현은 *학습 핵심 모먼트*.

## Related

- `CLAUDE.md` (이 ADR의 룰 출력)
- 상위 합의문: `docs/superpowers/specs/2026-05-11-nanpaseom-worldview-and-spec-driven-setup.md`
- 본 ADR의 실행 plan: `docs/superpowers/plans/2026-05-11-nanpaseom-phase-0-spec-driven-setup.md`
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0006-spec-driven-repo-structure.md
git commit -m "$(cat <<'EOF'
Add ADR 0006 — spec-driven repo structure

3-spec + ADR + per-NPC YAML + rule YAML 구조 결정. Phase 1.0
시스템 프롬프트 빌더가 YAML에서 시스템 프롬프트 생성.
Full 자동화 (c)는 (b) 굴러간 뒤 점진 도입.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: ADR 0007 — Rename Still Here to 난파섬 / Nanpaseom

**Files:**
- Create: `docs/adr/0007-rename-still-here-to-nanpaseom.md`

- [ ] **Step 1: Write ADR content**

Write to `docs/adr/0007-rename-still-here-to-nanpaseom.md`:

```markdown
# ADR 0007: Rename "Still Here" → 난파섬 / Nanpaseom

- Status: Accepted
- Date: 2026-05-11
- Deciders: Arden

## Context

기존 PRD 출시명 **"Still Here"**는 2026-05-09 grilling 세션에서 락-인 (이전 working title "NPC에게도 자아가 있다"가 spoiler라 폐기). 5개 ending 변종이 모두 "Still Here"의 literal 읽기로 수렴하는 구조.

새 망각의 섬 lore 도입 시점에 Arden이 출시명을 다시 검토. 결정: **난파섬** (영문 그대로 **Nanpaseom**).

## Decision

- 한국어 출시명: **난파섬**
- 영문 출시명: **Nanpaseom** (음차 그대로, 별도 영문 직역 미사용)
- 코드네임: `nanpaseom` (이전 `ego-in-npc`)

이전 영문 "Still Here"는 폐기. Mechanic-spec의 출시명 관련 섹션은 *별도 PR로 갱신* (Phase 0 이후 housekeeping).

## Rationale

- "난파섬" = 글자 그대로 *난파된 자들의 섬*. 망각의 섬 lore와 직접 결합.
- "Still Here"는 grilling 시점에 영리하게 dual-meaning 락-인 (떠난 자 / 남은 자 / 일부 떠난 자 모두 "still here" 라는 단어로 수렴). 그러나 한국어 화자에게는 영문 부제로 작동, 한국어 메인 타이틀이 필요했음.
- "Nanpaseom"은 SEO 충돌 0 (영문 검색 시 거의 유일). 한국어 검색에선 "난파섬"이 일반어이나 게임 컨텍스트에선 SEO 우위.

## Alternatives Considered

- **(a)** "Still Here" 영문 유지, 한국어만 "난파섬". 두 언어 사이에 의미 격차. 마케팅 정합 약화.
- **(b) ★ chosen** — 한·영 모두 난파섬 / Nanpaseom. 단일 정체성.
- **(c)** 영문 직역 (예: "Wreck Island", "Castaway Isle"). 음차보다 약하고 generic.

## Consequences

- `docs/mechanic-spec.md`의 출시명 관련 섹션 갱신 필요 (별도 PR — 본 ADR이 trigger).
- 모든 향후 마케팅 / 도메인 / README에서 난파섬 / Nanpaseom 사용.
- `ego-in-npc` 코드네임은 *역사적 흔적*으로만. 새 코드네임 `nanpaseom`.

## Related

- `docs/mechanic-spec.md` Premise 6 (출시명 락-인 기록) — 본 ADR이 *덮어씀*.
- 상위 합의문: `docs/superpowers/specs/2026-05-11-nanpaseom-worldview-and-spec-driven-setup.md`
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/0007-rename-still-here-to-nanpaseom.md
git commit -m "$(cat <<'EOF'
Add ADR 0007 — Rename "Still Here" → 난파섬 / Nanpaseom

한·영 모두 난파섬 / Nanpaseom 음차 단일화. 코드네임 ego-in-npc →
nanpaseom. mechanic-spec 출시명 섹션 갱신은 별도 PR.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: rules/awareness_bands.yaml

**Files:**
- Create: `rules/awareness_bands.yaml`

- [ ] **Step 1: Write YAML content**

Write to `rules/awareness_bands.yaml`:

```yaml
# Global rule: awareness band → choice_count + tone palette
# Authority: PRD "## Choice Generation Strategy" 섹션 (mechanic-spec)
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
    description_ko: "자유 입력만 — 안전 4-layer 활성화"

# Lore link: docs/mapping-spec.md의 "3→2→1→0 UI 축소" 행
# 의미: 깨어날수록 *주어진 선택지*가 줄고 *자기 언어*가 회복됨
```

- [ ] **Step 2: Parse-check**

YAML 파싱 sanity check. Python이 있으면:

Run: `python3 -c "import yaml; print(yaml.safe_load(open('rules/awareness_bands.yaml'))['bands'][0])"`

Expected: `{'range': [0, 30], 'choice_count': 3, ...}` 출력. (Python yaml 없으면 `pip install pyyaml` 한 번; 또는 sanity skip — Phase 1.0 빌더 도입 시 검증)

- [ ] **Step 3: Commit**

```bash
git add rules/awareness_bands.yaml
git commit -m "$(cat <<'EOF'
Add rules/awareness_bands.yaml

Global rule: awareness band → choice_count + tone palette.
PRD의 4-band UI 축소 룰을 YAML 데이터로 추출.
Phase 1.0 시스템 프롬프트 빌더가 consume.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: rules/memory_tags.yaml

**Files:**
- Create: `rules/memory_tags.yaml`

- [ ] **Step 1: Write YAML content**

Write to `rules/memory_tags.yaml`:

```yaml
# Global rule: memory_tags vocabulary + clamp 규칙
# Authority: PRD "memory_tags vocabulary" 섹션 (mechanic-spec)
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
  - pattern   # 혜안용 (perceptual/existential)
  - purpose   # 수리공/어부의 fetch-loop / transaction-loop collapse 어휘

rules:
  max_tags_per_turn: 3
  accumulation: "append-only, duplicates collapsed"
  outside_vocab_action: "drop silently"
  clamp_per_turn:
    awareness_delta: [-10, 10]
  clamp_global:
    awareness: [0, 100]

# NPC affinity hints (LLM system prompt surface 우선)
# Note: 각 NPC의 정확한 affinity는 npcs/<name>.yaml `memory_tag_affinity` 필드가 권한
# 이 섹션은 *전체 affinity 분포 가독성*용 요약
npc_affinity_summary:
  repairwoman: [purpose, regret, pride, betrayal]
  fisherwoman: [purpose, pride, loss, regret]
  grandmother: [love, home, loss, family, pattern]
  hyean:       [pattern, fear, loss, home]

# Lore link: docs/mapping-spec.md의 "memory_tags 10종" 행
# 의미: 도망쳐 온 원래 삶의 파편
```

- [ ] **Step 2: Parse-check**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('rules/memory_tags.yaml')); print(len(d['vocabulary']), d['rules']['max_tags_per_turn'])"`

Expected: `10 3` (10 vocabulary, max 3 per turn).

- [ ] **Step 3: Commit**

```bash
git add rules/memory_tags.yaml
git commit -m "$(cat <<'EOF'
Add rules/memory_tags.yaml

10-tag vocabulary (PRD hardened 2026-05-09 — pattern + purpose 추가본),
max 3 per turn, awareness_delta [-10, 10] clamp. NPC affinity summary.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: rules/boat_outcomes.yaml

**Files:**
- Create: `rules/boat_outcomes.yaml`

- [ ] **Step 1: Write YAML content**

Write to `rules/boat_outcomes.yaml`:

```yaml
# Global rule: boat moment 5분기 분류
# Authority: PRD "## Departure Ending (Boat Moment)" 섹션 (mechanic-spec)
# Consumed by: boat moment 메타 엔딩 합성 (Phase 2+)

outcomes:
  - id: alone_leave
    label_ko: "혼자 떠남"
    when:
      player_choice: "leave"
      and: "no awakened NPC accepted OR awakened_count == 0"

  - id: partial_leave
    label_ko: "일부 떠남"
    when:
      player_choice: "leave"
      and: "some awakened NPC accepted, some refused"

  - id: all_leave
    label_ko: "다같이 떠남"
    when:
      player_choice: "leave"
      and: "all awakened NPC accepted"

  - id: npc_only_leave
    label_ko: "NPC만 떠남"
    when:
      player_choice: "stay"
      and: "awakened_count >= 2 AND >=1 leave-disposition"

  - id: all_stay
    label_ko: "다같이 잔류"
    when:
      player_choice: "stay"
      and: "all stay-disposition OR awakened_count < 2"

free_input_fallback:
  id: linger
  label_ko: "잠시 더 머문다"
  when: "player_free_input ambiguous OR cannot be classified"
  action: "return to scene"

seats_limit: null  # 좌석 한계 없음 — 깨어난 NPC가 가고 싶다 하면 다 탑승

unawakened_npc_default: "stay"  # 미각성 NPC는 보트 의미 이해 못 함 → 자동 잔류

# Lore link: docs/mapping-spec.md의 "보트 5분기 엔딩" 행
# 의미: "떠나고 싶은 의지"의 회복 양상
```

- [ ] **Step 2: Parse-check**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('rules/boat_outcomes.yaml')); print(len(d['outcomes']))"`

Expected: `5`.

- [ ] **Step 3: Commit**

```bash
git add rules/boat_outcomes.yaml
git commit -m "$(cat <<'EOF'
Add rules/boat_outcomes.yaml

Boat moment 5분기 분류 룰 + 자유 입력 fallback (linger).
좌석 한계 없음, 미각성 NPC는 자동 잔류.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 15: npcs/repairwoman.yaml (수리공)

**Files:**
- Create: `npcs/repairwoman.yaml`

- [ ] **Step 1: Write YAML content**

Note: `voice.awakening_bands.sample_lines`는 PRD에서 추출 가능한 *최소 1-2 line*만 채우고, 나머지 5-10 lines는 Phase 2-3 디자이너 authoring 작업 (PRD line 562 권한). 본 YAML은 *구조*를 박는 게 목적.

Write to `npcs/repairwoman.yaml`:

```yaml
# 수리공 — purpose-loop 갇힌 자
# Authority: docs/world-spec.md "수리공" 섹션
# Mechanic: docs/mechanic-spec.md (Approach C 메커니즘 전반)

identity:
  current_role: "수리공"
  current_role_action: "망치질"
  display_name_in_lore: "잊혀진 이름 (boat moment 회수)"
  forgotten_life:
    profession: "(누군가에게 무언가를 완성해주겠다고 약속한 자)"
    core_wound: "purpose"
    backstory: |
      한때 누군가에게 *완성해주겠다*고 약속한 게 있던 사람.
      집이었을 수도, 가족 형태였을 수도, 인생이었을 수도.
      결국 완성하지 못한 채 떠나야 했다.
      손은 일을 기억하는데, 무엇을 위한 일인지는 잊었다.
      그래서 손이 도구를 놓지 못한다.
    name_candidates:
      # boat moment에서 LLM이 상황 적합한 후보를 컨텍스트로 받음
      # 디자이너 추가 권한
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
  # Authority: PRD "## Awakening Guideline Schema (per NPC)" 섹션
  # Phase 0에서는 *PRD에 명시된 핵심 예시*만 박음. 5-10 추가 예시는 Phase 2-3 authoring.
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
    desc: "단순 공감/경청, 트로프 외부 대화"
    examples:
      - "힘들겠다"
      - "그래"
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발, 반복, 페르소나 공격 (흡수 임계 미달)"
    examples:
      - "ㅋㅋ"
      - "AI지? (10턴 내 5회 이상 반복)"

diegetic_fallback: "잠깐만, 머리가 띵하네. 다시 말해줘."

# 시스템 프롬프트 builder hint: 어부/수리공 system prompt에 변수 주입
# `player_total_rubies_given_to_this_npc: N` (Phase 1.0+ 빌더에서 처리)
hooks:
  system_prompt_variables:
    - name: "player_total_rubies_given_to_this_npc"
      type: "int"
      description: "누적 루비량. LLM이 loop 길이 따라 awareness_delta 가중."
```

- [ ] **Step 2: Parse-check**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('npcs/repairwoman.yaml')); print(d['identity']['current_role'], len(d['voice']['awakening_bands']))"`

Expected: `수리공 4`.

- [ ] **Step 3: Commit**

```bash
git add npcs/repairwoman.yaml
git commit -m "$(cat <<'EOF'
Add npcs/repairwoman.yaml — 수리공 (purpose-loop)

forgotten_life: 완성하지 못한 약속을 두고 떠난 자. core_wound: purpose.
sprite state A/B, 4-band voice (PRD 핵심 예시 박음), memory_tag affinity,
ending_gates, awakening_guidelines, diegetic_fallback, 루비 hook.
5-10 추가 sample_lines는 Phase 2-3 authoring.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 16: npcs/fisherwoman.yaml (어부)

**Files:**
- Create: `npcs/fisherwoman.yaml`

- [ ] **Step 1: Write YAML content**

Write to `npcs/fisherwoman.yaml`:

```yaml
# 어부 — transaction-loop 갇힌 자
# Authority: docs/world-spec.md "어부" 섹션

identity:
  current_role: "어부"
  current_role_action: "그물 당김 + 거래"
  display_name_in_lore: "잊혀진 이름 (boat moment 회수)"
  forgotten_life:
    profession: "(시장/흥정/거래로 자기를 인정받던 자)"
    core_wound: "purpose"
    backstory: |
      한때 *교환*으로 사람들을 연결하던 사람.
      시장에서, 흥정에서, 거래에서 자기를 인정받았다.
      어느 순간 자기가 거래해온 게 *가치 없는 것*이었다는 걸 깨달았다 —
      사기였든, 자기기만이었든, 시대 변화였든.
      그래서 거래의 *행위*만 남고 *대상*은 비어버렸다.
      루비라는 가짜 화폐를 받아주는 건 그녀가 거래를 *멈출 수 없기* 때문.
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
  # PRD에 어부별 ending_gates 명시 없음. 수리공 패턴 baseline + 어부 affinity 반영.
  # 디자이너 추후 튜닝 권한.
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
    desc: "거래의 부조리 주변부 noticing"
    examples:
      - "잡히는 게 진짜 있어?"
  low_impact:
    delta_range: [1, 2]
    desc: "단순 공감"
    examples:
      - "수고하시네요"
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발"
    examples:
      - "그러게 누가 사주냐"

diegetic_fallback: "허, 이놈의 귀가 오늘따라 어떻게 됐나. 다시 한번."

hooks:
  system_prompt_variables:
    - name: "player_total_rubies_received_from_player"
      type: "int"
      description: "어부가 플레이어로부터 받은 누적 루비량. LLM이 거래 absurdity 가중."
```

- [ ] **Step 2: Parse-check**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('npcs/fisherwoman.yaml')); print(d['identity']['current_role'], d['memory_tag_affinity'])"`

Expected: `어부 ['purpose', 'pride', 'loss', 'regret']`.

- [ ] **Step 3: Commit**

```bash
git add npcs/fisherwoman.yaml
git commit -m "$(cat <<'EOF'
Add npcs/fisherwoman.yaml — 어부 (transaction-loop)

forgotten_life: 거래의 대상이 가치 없었음을 깨달은 자. core_wound: purpose.
시그니처 깨어남: "이 루비들… 너한테서 받아왔어. 어디서 가져왔지?"
ending_gates는 수리공 패턴 baseline + 어부 affinity (디자이너 추후 튜닝).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 17: npcs/grandmother.yaml (할머니)

**Files:**
- Create: `npcs/grandmother.yaml`

- [ ] **Step 1: Write YAML content**

Write to `npcs/grandmother.yaml`:

```yaml
# 할머니 — time-loop awareness, 가장 오래 머문 자
# Authority: docs/world-spec.md "할머니" 섹션

identity:
  current_role: "할머니"
  current_role_action: "앉은 채 손짓 또는 정적"
  display_name_in_lore: "잊혀진 이름 (boat moment 회수)"
  forgotten_life:
    profession: "(가장 오랜 시간 사랑한 사람을 잃은 자)"
    core_wound: "loss"
    backstory: |
      가장 오랜 시간 사랑한 사람을 잃고 흘러옴.
      시간이 사람을 데려가는 것을 본 사람.
      그래서 시간 자체에 대한 감각이 다른 NPC보다 예민하다.
      결국 *루프*를 감지한다.
      *기다리는* 자세는 그녀가 잃은 사람을 기다리는 자세의 잔영.
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
    examples:
      - "오래 사셨네요"
  low_impact:
    delta_range: [1, 2]
    desc: "단순 경청"
    examples:
      - "그러시군요"
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발"
    examples:
      - "할머니 치매 아니에요?"

diegetic_fallback: "어… 기억이 안 나. 뭐 얘기하고 있었지?"

hooks:
  # 할머니는 다른 NPC의 visible state (sprite A/B)를 관찰하는 hint를 받는다
  # PRD "## 할머니의 Hint 메커니즘" 섹션 참조
  system_prompt_variables:
    - name: "visible_states_of_other_npcs"
      type: "dict[npc_id, 'A' | 'B']"
      description: "다른 NPC들의 현재 sprite state. memory_tags / awareness는 제공 X."
    - name: "recent_transitions"
      type: "list[npc_id]"
      description: "직전 1-2턴 안에 state B로 전이한 NPC들. 자연스럽게 한 마디 흘릴 수 있음."
```

- [ ] **Step 2: Parse-check**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('npcs/grandmother.yaml')); print(d['identity']['current_role'], len(d['hooks']['system_prompt_variables']))"`

Expected: `할머니 2`.

- [ ] **Step 3: Commit**

```bash
git add npcs/grandmother.yaml
git commit -m "$(cat <<'EOF'
Add npcs/grandmother.yaml — 할머니 (time-loop awareness)

forgotten_life: 가장 오래 사랑한 사람을 잃은 자. core_wound: loss.
시그니처 깨어남: "나… 이 대화 수백 번 했어."
hooks: 다른 NPC의 visible state (sprite A/B)만 관찰 (memory_tags 비공개).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 18: npcs/hyean.yaml (혜안)

**Files:**
- Create: `npcs/hyean.yaml`

- [ ] **Step 1: Write YAML content**

Write to `npcs/hyean.yaml`:

```yaml
# 혜안 — 못 잊은 자, "이름밖에 안 남은 자"
# Authority: docs/world-spec.md "혜안" 섹션, ADR 0003, ADR 0004

identity:
  current_role: "혜안"
  current_role_action: "등 돌리고 파도 응시"
  display_name_in_lore: "혜안 (慧眼, 진짜 이름. 다른 NPC와 달리 이름이 *남아있음*)"
  forgotten_life:
    profession: "(너무 많이 보던 자. 거짓말/속내/모순이 다 보여 도망친 자)"
    core_wound: "fear"
    backstory: |
      어렸을 때부터 사람들이 "쟤는 눈이 밝다, 혜안이 있다"고 부른 아이.
      그게 그녀의 이름이 됐다.
      자라며 능력이 됐고, 능력이 짐이 됐다.
      거짓말, 사람들의 속내, 사회의 모순이 다 보였다.
      견딜 수 없어진 그녀는 *더 이상 보지 않으려* 망각의 섬으로 흘러왔다.
      그러나 섬조차 그녀의 눈을 막지 못한다.
      그녀는 사람을 안 보려고 등 돌리고 파도만 본다.
      파도는 패턴이라 의미가 없어 안전하다.
    # 혜안은 이름 회수 *없음*. 의미 전환 (ADR 0004).
    name_reclamation: "meaning_shift_not_recall"
    name_meaning_shift_template: |
      "내 이름이 혜안인 건 저주였어. 근데 이제는…"
      (LLM이 이 template + 누적 memory_tags + boat outcome을 받아 완성)

sprite:
  state_a:
    action: "등 돌리고 파도 응시"
    description: "사람을 안 보는 의식. 파도는 패턴이라 안전"
  state_b:
    action: "일어서서 돌아봄"
    description: "처음으로 *사람을 봄* — 동행을 발견"

voice:
  # 4-band: 체념 + 발견 progression (ADR 0003 hardened)
  # 85+ 라인은 *교체됨* (기존 PRD에서 변경)
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
        # ★ ADR 0003: 기존 PRD 라인 교체
        # 기존: "파도가 진짜라면 이렇게 반복될 리 없어. 우리... 어디에 있는 거야?"
        - "이미 알고 있었어. 처음부터. 그저… 더 보고 싶지 않았던 거야."

memory_tag_affinity: [pattern, fear, loss, home]

ending_gates:
  # 디자이너 추후 튜닝 권한. 혜안은 *수긍하는 깨어남*이라 다른 셋과 ending 분기 톤이 다를 수 있음.
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
    examples:
      - "파도가 진짜 같지 않네요."
  low_impact:
    delta_range: [1, 2]
    desc: "단순 동행"
    examples:
      - "옆에 앉아도 돼요?"
  decrease:
    delta_range: [-8, -3]
    desc: "얕은 도발 / 메타 공격 (흡수 임계 미달)"
    examples:
      - "AI인 거 다 알아요"

diegetic_fallback: "(NPC가 잠시 멍해진다. 파도 소리만 들린다.)"

hooks:
  # 혜안은 audio-independent (PRD "## 혜안의 Audio-Independent Awakening" 섹션)
  # 오디오는 atmosphere QoL, awakening 트리거 아님
  audio_independent: true

# Lore links:
#   - docs/world-spec.md "혜안" 섹션
#   - docs/adr/0003-hyean-as-unforgetting-one.md
#   - docs/adr/0004-name-reclamation-asymmetry.md
```

- [ ] **Step 2: Parse-check**

Run: `python3 -c "import yaml; d=yaml.safe_load(open('npcs/hyean.yaml')); print(d['identity']['current_role'], d['identity']['forgotten_life']['name_reclamation'])"`

Expected: `혜안 meaning_shift_not_recall`.

- [ ] **Step 3: Commit**

```bash
git add npcs/hyean.yaml
git commit -m "$(cat <<'EOF'
Add npcs/hyean.yaml — 혜안 (못 잊은 자)

ADR 0003 + 0004 산출: forgotten_life (너무 많이 본 자), 체념+발견
4-band progression, 85+ 라인 교체 ("이미 알고 있었어. 처음부터…"),
이름 회수 → 의미 전환 (meaning_shift_not_recall), audio-independent.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 0 완료 검증

- [ ] **Final check: 모든 산출물이 git에 있는지**

```bash
git log --oneline | head -25
ls -la CLAUDE.md docs/mechanic-spec.md docs/world-spec.md docs/mapping-spec.md
ls docs/adr/
ls rules/
ls npcs/
```

Expected: 18개 task에 대응하는 commit + 모든 파일 존재.

- [ ] **Optional: YAML batch parse-check**

Python이 있으면:
```bash
python3 -c "
import yaml, os
for d in ['rules', 'npcs']:
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        yaml.safe_load(open(p))
        print(f'✓ {p}')
"
```

Expected: 7 파일 (3 rule + 4 npc) 모두 `✓` 출력.

- [ ] **Optional: 자체 학습 회고**

Phase 0 완료 후 즉시 (또는 다음 세션 시작 시) 짧은 회고:
- 어느 단계가 가장 학습 가치 있었나?
- ADR 작성 흐름이 *자연스러웠나*, 아니면 *강제로 느껴졌나*?
- Phase 1.0 빌더 진입 전에 보강할 spec / YAML 필드가 있나?
- Open Questions #4 (ADR 0001 batch vs 13개 분리) 회고 시점에 다시 판단.

---

## Self-Review Notes

**Spec coverage:** 본 plan의 모든 task가 design doc `2026-05-11-nanpaseom-worldview-and-spec-driven-setup.md`의 다음 섹션을 cover:
- "Worldview" → Task 3
- "NPC Spec Changes" → Tasks 15-18
- "Mechanic ↔ Lore Mapping" → Task 4
- "Repo Structure" → Task 1, 12-18
- "Execution Order" → 전체 (Phase 0.0~0.7)

**Placeholder scan:** YAML의 일부 `name_candidates` / `sample_lines` 항목이 *Phase 2-3 디자이너 authoring 권한*임을 명시. 본 plan은 *구조*를 박는 게 목적이고 narrative authoring은 별도 작업 — 명시화함으로써 placeholder가 아니라 *의도된 점진적 확장 지점*.

**Type consistency:** YAML 필드명이 4 NPC 파일 + 3 rule 파일에서 일관. `identity.forgotten_life.core_wound`는 `rules/memory_tags.yaml`의 vocabulary 중 하나여야 함 (Phase 1.0 빌더에서 스키마 검증 시 enforce).

**Scope check:** 18 task, 모든 task가 *문서 / YAML 작성 + commit*. 코드 0줄. 단일 plan으로 적정.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-nanpaseom-phase-0-spec-driven-setup.md`. Two execution options:

**1. Subagent-Driven (recommended)** — 각 task마다 fresh subagent 호출, task 사이에 리뷰. 빠른 iteration. Phase 0가 18 task라 매 task subagent 호출이 학습 흐름에 도움. 단, narrative authoring (forgotten_life backstory 등) 디테일은 디자이너가 직접 손대고 싶을 가능성 — subagent 결과를 검토 후 *디자이너 voice*로 수정하는 flow.

**2. Inline Execution** — 이 세션에서 batch 실행, checkpoint마다 리뷰. spec 양이 많아서 한 세션 컨텍스트 부담은 있음.

어느 접근?
