# Handoff — Phase 0 close → next steps

> Created: 2026-05-14 (Phase 0 완료 직후, PR #1 open). 다음 세션 시작 시 이 파일만 읽으면 바로 진행 가능.

## 현재 상태 한 줄

Phase 0 완료. `phase-0-spec-driven-setup` 브랜치 38 commits, PR #1 open ( https://github.com/ardenspace/nanpaseom/pull/1 ). main 으로 merge 만 남음.

## 무엇이 들어있나 (요약)

- 21 ADR (13 historical + 7 today + 1 schema-gap audit) — `docs/adr/`
- 3 spec (mechanic / world / mapping) — `docs/`
- 3 rule YAML + 4 NPC YAML — `rules/`, `npcs/`
- `scripts/check_yaml.py` (Phase 0 enforcement)
- 손-합성 audit 2 round — `docs/superpowers/scratch/`
- CLAUDE.md (spec-driven repo rule)

Phase 0 done criteria 4/4 통과. 손-합성 Round 1 → gap 3개 발견 → ADR 0021 fix → Round 2 verbatim 9/9 (gap 0).

## 추천 다음 순서

| # | 단계 | 상태 |
|---|---|---|
| 1 | 머리 식히기 (이번 세션 끝) | 본인 영역 |
| 2 | PR #1 셀프 리뷰 + merge | 다음 세션 시작점 |
| 3 | 회고 (`docs/superpowers/retro-2026-05-14-phase-0.md`) | merge 후 |
| 4 | Phase 1.0 plan 작성 | 회고 후 |

## 단계별 다음 세션 프롬프트 (복붙용)

### Step 2 — PR #1 셀프 리뷰 + merge

```
@docs/superpowers/handoff-2026-05-14-phase-0-close.md 읽고 PR #1 (https://github.com/ardenspace/nanpaseom/pull/1) 셀프 리뷰 도와줘. main 머지 전 빠뜨린 것 있는지 점검 후 squash 또는 merge commit 으로 land 하자.
```

세션에서 점검할 것:
- 모든 commit 메시지가 결정 *이유* 명시 (CLAUDE.md git 룰)
- ADR 21개 + spec 3개 cross-link 작동
- `python3 scripts/check_yaml.py` green
- 손-합성 scratch 2 round 둘 다 commit 됨

merge 옵션:
- **Merge commit** — 38 commit 의 audit trail 보존. spec-driven 학습 vehicle 의 성격상 적합. *추천*.
- **Squash** — main history 깔끔, 그러나 ADR 별 commit 흩어짐. audit trail 약함.

### Step 3 — 회고

```
@docs/superpowers/handoff-2026-05-14-phase-0-close.md 읽고 Phase 0 회고 작성 도와줘. docs/superpowers/retro-2026-05-14-phase-0.md 에 다음 4 질문 응답 + 자유 단상:
1. 어느 단계가 가장 학습 가치 있었나?
2. ADR 작성 흐름이 자연스러웠나, 강제로 느껴졌나?
3. 손-합성 검증에서 발견된 schema 부족이 있었나? (있었음 — ADR 0021)
4. Phase 1.0 빌더 진입 전 보강할 spec / YAML 필드?
```

회고는 *문서가 아니라 *프로세스 회고*. 다음 phase 에 가져갈 패턴 + 버릴 패턴 식별이 목적.

### Step 4 — Phase 1.0 plan 작성

```
@docs/superpowers/handoff-2026-05-14-phase-0-close.md + @docs/superpowers/retro-2026-05-14-phase-0.md 읽고 Phase 1.0 spec / plan 작성 시작하자. brainstorming → spec → plan 흐름. 시스템 프롬프트 빌더 + FastAPI + Postgres + 수리공 단독 end-to-end 가 범위.
```

Phase 1.0 의 범위 (spec design doc + 메커닉 spec line 어딘가 + 이 handoff 의 합의):
1. **System prompt builder** (`app/prompt_builder/`)
   - Python + Jinja2 + pyyaml
   - 입력: `npcs/<name>.yaml` + `rules/*.yaml` + 현재 awareness 정수 + memory_tags 누적 + recent_transitions (할머니용)
   - 출력: LLM API 에 보낼 system prompt string (손-합성 Round 2 와 동일 구조)
   - Test: 4 NPC × 4 band = 16 케이스 합성 결과가 손-합성과 일치 (snapshot test)
2. **FastAPI + Postgres + Cloudflare Tunnel** (PRD Approach C 그대로)
3. **수리공 단독 awareness 파이프라인 end-to-end** — PRD Week 2 spike
4. **YAML 스키마 검증** (pydantic / jsonschema) — 빌더 fail-fast layer
5. **Phase 1.0 enforcement** (CLAUDE.md 의 "Phase 1.0" 섹션) 활성화
   - "코드 내 NPC 대사 하드코딩 금지" pre-commit grep
   - `mapping-spec.md` PR 체크리스트
   - 시스템 프롬프트 누설 키워드 차단 (PRD Layer 4)

빌더 짜기 전 *반드시* 회고에서 발견된 schema 보강이 반영돼야 함 (있다면).

## 기억해둘 spec-driven 원칙 (Phase 1.0 에서 *반드시* 적용)

1. **Closed vocabulary**: 데이터 필드 값은 vocab literal 만. 산문 X.
2. **지시 vs 결과**: 빌더는 yaml 의 *지시* 를 LLM 에 넘김. *결과* 생성은 LLM 의 일.
3. **Verbatim**: 빌더가 yaml string 을 시스템 프롬프트에 박을 때 paraphrase X. 표현 바꾸려면 yaml 부터.

이 3개가 손-합성 Round 1 에서 본인이 위반했다가 Round 2 에서 체득한 원칙. 빌더 코드에 박힐 룰.

## ADR audit trail 룰 (계속)

- 새 결정 → ADR (NNNN-topic.md, 시퀀셜)
- ADR 0022+ 자리 비어있음
- 결정 *이유* 가 commit 메시지에 들어가야 함 (한국어 OK)

## 발견된 잠재 future-ADR 후보 (기록만)

- **빌더 spec 에서 `awakening_guidelines.examples` 의 이름 모호 가능성** — Round 1 손-합성에서 합성자가 NPC 대사로 오해. `player_input_examples` 로 rename 검토 (ADR 0022 후보).
- **빌더가 시스템 프롬프트에 `sample_lines` + `npc_tone` 함께 주입해야 하는지** 의 행동 명세 부재 — Phase 1.0 builder spec 작성 시 결정.

이 두 가지는 *지금* 처리하지 않음. Phase 1.0 plan 작성 시 결정 트리거.

## Branch / PR 상태

- Branch: `phase-0-spec-driven-setup` (origin 푸시됨)
- Main: 38 commits behind
- PR #1: open, 본 handoff 추가 후 1 commit 더
- Merge 옵션 위 단계 2 에 명시

## 마지막 — 본인 톤 (다음 세션 Claude 가 알아야 할 것)

- `~/.claude/projects/-Users-arden-Documents-ardensdevspace-nanpaseom/memory/MEMORY.md` 의 4개 memory 파일이 본인 collaboration 스타일을 정리해둠. 다음 세션 Claude 는 자동으로 로드함.
- 핵심: 강한 pushback 환영, 다중-선택지 + 추천, 새 워크플로우는 *교정 모드* 로 가르치기 (paraphrase 금지, 정확히 무엇이 틀렸는지 말하기).
