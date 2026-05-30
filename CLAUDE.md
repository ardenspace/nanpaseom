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

**Phase 1.0 Sub-1 (현재 — 빌더 도입됨):**
- `scripts/check_yaml.py` — Phase 0 baseline 유지.
- `app/prompt_builder/` — yaml + rules + runtime state → 시스템 프롬프트 string (offline pure function). `python -m app.prompt_builder --npc <name> --awareness <0-100>` 로 확인.
- `pytest tests/prompt_builder/` — pydantic v2 schema fail-fast + 4-cell snapshot (verbatim oracle) + 16-cell property invariant.
- pydantic v2 schema 가 yaml 의 *required field* 강제 (extra=forbid). 누락/오타/enum 위반 시 빌더 boot 실패 = yaml schema 충분성 검증.
- 시스템 프롬프트는 **빌더가 `rules/prompt_skeleton.yaml` + NPC yaml 에서 생성**. 코드/스킬레톤에 NPC 대사 하드코딩 금지 (verbatim copy only).

**Phase 1.0 Sub-2 (현재 — 수리공 vertical slice 도입됨):**
- `scripts/check_no_hardcoded_dialogue.py` — `app/` 내 NPC 대사(sample_lines/diegetic_fallback) 하드코딩 금지. pre-commit/CI 연결.
- `PULL_REQUEST_TEMPLATE.md` — mapping-spec 갱신 + ADR + check_yaml + 하드코딩 grep 체크리스트.
- `app/api` + `app/turn` + `app/llm` + `app/store` + `app/safety` — 수리공 단독 `POST /turn` end-to-end (build_prompt → llama-server(Gemma 4) json_schema → Layer 1/4 → clamp → Postgres). `docker compose up -d db` 후 `pytest`.
- LLM 출력 회귀: gate = 결정적 validator + stub `llm_call` 통합, off-gate = `pytest -m live` (실제 llama-server verbatim 임계, ADR 0023).
- 시스템 프롬프트 누설 차단 = Layer 4 (`output_validator`). Layer 2(Moderation)+2.5(2-strike) 는 Sub-2b.

**Phase 1.0 Sub-2b+ (추후):**
- FastAPI 프론트엔드/모바일, save-code/쿠키, Cloudflare/failover, running summary, 나머지 3 NPC, Layer 2 Moderation + 2-strike DB.

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
