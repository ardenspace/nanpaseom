# Conventions

## Baseline (applies unless overridden)

- Repeated literals (colors, spacing, paths, magic numbers) live in one
  named home — frontend는 디자인 토큰 파일, Python은 상수 모듈 — never
  inlined in two places.
- Logic appearing a second time is extracted into the shared layer and
  registered under Shared Utilities below.
- User-visible failure wording follows one tone, defined in one place
  (frontend tone 모듈 — Failure Behavior 참조).
- A file growing past ~300 lines triggers a split review. Staying
  single-file is a legitimate outcome — record why under Layout &
  Naming. Review trigger, not a hard limit.

레포 룰 승격 (CLAUDE.md와 병행 유효 — talpi 파이프라인이라고 면제되지 않음):

- 권한 경계: 같은 사실은 한 spec 문서에만. 메커니즘 변경 시
  mechanic-spec + mapping-spec 둘 다 갱신 (이번 런은 메커니즘 무변경 —
  band→UI 매핑은 기존 spec 소비만 한다).
- 새 락인 결정은 ADR (`docs/adr/NNNN-*.md`, 4자리 시퀀셜) 후 spec/YAML 갱신.
- NPC 대사/서버 발신 안전 메시지 하드코딩 금지 — frontend 포함.
  `scripts/check_no_hardcoded_dialogue.py`를 `frontend/` 스캔까지 확장
  (tone 모듈 한 곳만 허용 예외). YAML 변경 시 `python3 scripts/check_yaml.py`.
- git: logical unit per commit, 한국어 커밋 메시지에 결정 이유,
  `--no-verify`/`--no-gpg-sign` 금지.
- 테스트: `.venv/bin/pytest` 게이트는 결정적(stub llm) — `-m live`는
  off-gate. 신규 계약 테스트도 이 구분을 따른다.

## Design Tokens

테마: 딥블루 · 모래 · 녹슨 철 · 어둑한 바다 · 몽환. 초기값은 빌드 중
정제하되 이름과 홈은 고정 — `frontend/src/tokens.css` (CSS custom
properties) 한 곳:

- `--color-abyss` 계열: 딥블루/어둑한 바다 배경 (거의 검정에 가까운 남색)
- `--color-sand` 계열: 모래 — 본문 텍스트/말풍선 밝은 면
- `--color-rust` 계열: 녹슨 철 — 액센트, 시스템 톤 경고 계열과 구분
- `--color-system` 계열: warning/ban/오류 등 프레임 깨는 시스템 문구 전용
  (NPC 말풍선 색과 절대 공유하지 않음 — 시스템 톤 구분이 게임 디자인 요구)
- spacing/radius/type scale도 같은 파일. 컴포넌트에 리터럴 색/픽셀 금지.
- 몽환적 무드는 애니메이션(페이드/부유)으로 — 구현 재량, 토큰만 공유.

## Shared Utilities

- `tests/api/conftest.py` — 공유 `client` fixture (migrations + truncate,
  `llm_client.call` + `summarize_call` 스텁) + `make_stub_reply()`.
  신규 API 테스트는 이걸 쓴다 (기존 모듈들의 로컬 fixture는 shadow — 불변).
- `frontend/src/api.ts` — `postJson<T>` 공유 클라이언트 (fetch + JSON +
  네트워크 실패 정규화 `ApiResult<T>`; 한국어 리터럴/상태 로직 없음).
  프론트의 모든 endpoint 호출은 이걸 쓴다.
- `app/turn/loop.py` — `build_turn_context()` + `TurnContext` dataclass:
  npc/rules/state/band/시스템 프롬프트 조립 공유 (run_turn·run_opening 공용).
- `app/store/repo.py` — `load_last_reply_choices()`: 마지막 assistant 턴의
  choices (NULL raw = fallback 턴 → `[]` = 자유 입력 모드).
- `rules/opening.yaml` — 오프닝 pseudo-user 지시문 + 503 시스템 톤 문구
  (bootstrap 관련 문자열의 유일한 홈).

## Prior work this phase (Phase 3)

(이전 페이즈 요약: 백엔드 — POST /session/bootstrap(쿠키=신원) +
run_opening + GET /·/assets 정적 서빙. 프론트 — App.tsx(타이틀/채팅/차단
+ 재방문 복원, 278줄), api.ts(postJson), protocol.ts, playedHint.ts,
tone.ts, tokens.css, app.css. 테스트: test_bootstrap.py(9),
test_static.py(7), 공유 conftest. 게이트 221 passed, 2 deselected.)

- step 1: migrations/003_save_code.sql (idempotent ALTER + UNIQUE 인덱스),
  app/save_code.py (알파벳/형식 상수+regex 단일 소스 — 함수 없음),
  tests/store/test_migration_003.py (B5, 그린), tests/api/test_save_code.py
  (B3 10개, 404 failing). URL 확정: POST /save-code (쿠키 필수, 무쿠키 400
  + 세션 민팅 금지), POST /save-code/redeem {code} (unknown/malformed 404,
  rebind Set-Cookie는 new/resumed에만 — bootstrap의 "503에도 쿠키" 패턴
  redeem에선 금지, 오프닝 실패 503 시 rebind 커밋 금지).

## Layout & Naming

- `frontend/` — bun + Vite + React. `frontend/src/` 아래 컴포넌트,
  `frontend/public/assets/` — 캐릭터/배경 이미지 드롭인 홈 (파일명 규약:
  `<npc_id>.png`, `bg.png` — 디자이너가 같은 이름으로 덮어쓰면 반영).
- Python 쪽은 기존 구조 유지: `app/api`(endpoint), `app/store`(repo),
  `migrations/NNN_*.sql` 시퀀셜.
- 신규 endpoint는 기존 `POST /turn`처럼 `app/api/main.py`에서 시작,
  300줄 리뷰 트리거 시 라우터 분리.
- app.css는 단일 파일 유지(~359줄, 300줄 리뷰 완료): 타이틀/채팅/차단
  화면이 하나의 시각 어휘(btn/bubble/system-msg/rise-in)를 공유하고 독립
  소비자가 없어 분리하면 항상 같이 로드되는 응집 테마 코드가 흩어짐.
- dev 포트: 이 머신 점유 포트(8080 llama-server, 8000, 8081, 5433,
  5000, 7000, 7265, 6463) 회피. 선택: backend dev **8765** (uvicorn),
  frontend dev 5173 (vite, proxy → 8765).

## Failure Behavior

- 인프라 실패(서버/네트워크 다운, 503): 솔직한 시스템 톤 — NPC를 흉내내지
  않는다 ("인물이 대사하는 것 같으면 세계관 붕괴" — 스펙 결정). 문구는
  frontend tone 모듈 한 곳.
- 서버 발신 시스템 메시지(warning/ban)는 서버가 주는 텍스트를 그대로
  렌더 — frontend는 스타일만 입힌다 (시스템 톤 시각 구분, `--color-system`).
- LLM 출력 검증 실패(Layer 4)의 diegetic_fallback은 기존 백엔드 설계
  그대로 — frontend는 구분하지 않고 npc 응답으로 취급.
- 오류 응답 공통 형태: `{status: "error", message}` (+ HTTP 4xx/5xx).
  frontend는 message를 시스템 톤으로 표시, 대화 상태는 유지.
- fatal vs recoverable: 밴(fatal — 차단 화면, 입력 봉인) / 그 외 오류는
  recoverable — 재시도 가능, 진행 중 대화를 잃지 않는다.
