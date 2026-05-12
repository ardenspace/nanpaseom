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
