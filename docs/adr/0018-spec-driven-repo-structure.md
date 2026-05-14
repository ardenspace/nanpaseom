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
