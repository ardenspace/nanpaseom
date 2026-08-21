# Conventions

## Baseline (applies unless overridden)

- Repeated literals (colors, spacing, paths, magic numbers) live in one
  named home — never inlined in two places. 이번 런의 배치: 쿠키 상수는
  `app/api/session_cookie.py`, 서버 튜닝 값(레이트리밋 횟수/윈도우)은
  rules YAML, 프론트 튜닝 값(넛지 임계값)은 프론트 톤 홈.
- Logic appearing a second time is extracted into the shared layer and
  registered under Shared Utilities below.
- User-visible failure wording follows one tone, defined in one place
  (서버 발신 문구는 rules YAML, 프론트는 tone 모듈 — Failure Behavior
  참조). 테스트도 이 상수를 import 해서 단언한다 — 한글 리터럴 인라인
  금지(하드코딩 게이트가 테스트 파일도 스캔한다).
- A file growing past ~300 lines triggers a split review. Staying
  single-file is a legitimate outcome — record why under Layout &
  Naming. Review trigger, not a hard limit.

레포 룰 승계 (CLAUDE.md와 병행 유효 — talpi 파이프라인이라고 면제되지
않음):

- 권한 경계: 같은 사실은 한 spec 문서에만. 메커니즘/인프라 변경 시
  mechanic-spec 갱신, 메커니즘이면 mapping-spec 정렬 확인.
- 새 락인 결정은 ADR (`docs/adr/NNNN-*.md`, 4자리 시퀀셜, ADR당 1커밋)
  후 spec/YAML 갱신.
- NPC 대사/서버 발신 안전·시스템 메시지 하드코딩 금지 — frontend 포함
  (`scripts/check_no_hardcoded_dialogue.py`, tone 모듈 단일 예외).
  YAML 변경 시 `python3 scripts/check_yaml.py`.
- git: logical unit per commit, 한국어 커밋 메시지에 결정 이유,
  `--no-verify`/`--no-gpg-sign` 금지.
- 테스트: `.venv/bin/pytest` 게이트는 결정적(stub llm) — `-m live` 는
  off-gate. 신규 계약 테스트도 이 구분을 따른다.

## Design Tokens

이번 런은 새 시각 체계 없음 — 기존 유지: `frontend/src/tokens.css`
(CSS custom properties) 단일 홈. `--color-abyss`(배경) /
`--color-sand`(본문·말풍선) / `--color-rust`(액센트) /
`--color-system`(warning/ban/오류 등 프레임 깨는 시스템 문구 전용 — NPC
말풍선 색과 절대 공유 금지). spacing/radius/type scale 같은 파일.
컴포넌트에 리터럴 색/픽셀 금지.

이번 런의 신규 UI(회전 확인, 갈아타기 탈출구, 넛지)는 전부 기존 토큰과
기존 오버레이/버튼 클래스를 재사용한다. 넛지는 시스템 발화이므로
`--color-system` 계열 — NPC 말풍선처럼 보이면 안 된다.

## Shared Utilities

기존 (재사용 대상):

- `tests/api/conftest.py` — 공유 `client` fixture(migrations + truncate,
  `llm_client.call` + `summarize_call` 스텁), `make_stub_reply()`,
  `known_session(turns=0)`, `session_cookie_headers()` /
  `session_cookie_value()`, `db_conn()` / `db_save_code(sid)`,
  `raising_llm(monkeypatch)`. 신규 API 테스트는 이걸 쓴다.
- `frontend/src/api.ts` — `postJson<T>` 공유 클라이언트(fetch + JSON +
  네트워크 실패 정규화 `ApiResult<T>`; 한국어 리터럴/상태 로직 없음).
- `frontend/src/protocol.ts` — 서버 응답 wire shape 단일 홈.
  `has_save_code` 는 여기 `BootstrapData` 에 추가된다(= `RedeemData`
  별칭이 자동 승계 — 이 공유가 B2b 계약의 근거).
- `frontend/src/tone.ts` — 프론트 발신 문구 단일 홈(하드코딩 게이트의
  유일한 예외 파일). 넛지 임계값·신규 문구가 여기 산다.
- `app/api/session_cookie.py` — 쿠키 이름/Max-Age/INSECURE env 이름 +
  발급 단일 경로 `set_session_cookie()`. 쿠키 발급은 반드시 이 함수 경유.
- `app/api/identity.py` — `resolve_session(conn, request)` 신원 해석
  단일 지점(세션 생성 절대 없음). 신규 엔드포인트(rotate)도 이걸 경유.
- `app/store/repo.py` — 세션/턴/세이브 코드 저장 접근 단일 홈.
- `app/save_code.py` — 코드 알파벳/형식 상수 + 생성.
- `rules/identity.yaml` / `rules/save_code.yaml` / `rules/opening.yaml` —
  서버 발신 문구의 유일한 홈.

이번 런에서 생긴 것:

- `tests/api/conftest.py` — `cookie_attrs(header)` Set-Cookie 속성 파서
  (기존 `test_identity_contracts.py` 사설 `_cookie_attrs` 승격). 쿠키
  속성 단언은 이걸 쓴다.
- `tests/api/conftest.py` — `CONTRACT_COOKIE_MAX_AGE = 15552000` (B6
  Max-Age 계약 리터럴의 **테스트 쪽** 단일 홈; 구현 상수 import 는
  동어반복이라 일부러 안 한다) + `assert_cookie_attrs_except_secure(attrs)`
  — Secure 를 뺀 속성 4종(HttpOnly / SameSite=Lax / Max-Age / Path=/)
  공유 단언. Secure 유무는 호출부가 각자 단언한다(발급 표면 = 항상 있다,
  env 매트릭스 = 있냐 없냐가 관찰 대상).

## Prior work this phase (Phase 1 — 위생 2건)

- step 1: `tests/api/test_cookie_env_flag.py` (신규) — B6 허용목록 판정
  매트릭스(ON 5 / OFF 21 / unset), 발급 표면(Set-Cookie)으로 관찰.
  `tests/safety/test_strike.py` — B7 예외 pin + `python -O` 생존 pin.
  `tests/api/test_identity_contracts.py` — B7 도달 불가(호출부 전제) pin.
  `tests/api/conftest.py` — `cookie_attrs` 승격.
- step 2: `app/api/session_cookie.py` — `INSECURE_COOKIE_ON_VALUES =
  frozenset({"1","true"})` 허용목록 판정(`_FALSY_ENV_VALUES` 폐지,
  `.strip()` 제거 → 공백 포함 값은 OFF). B6 33/33 green.
  **Phase 5 인계**: ADR 0034 clause 2("플래그가 켜진 경우에만 Secure
  생략")가 "켜짐"을 정의하지 않으므로 개정/보충 필요 — 이 반전의 단일
  홈을 ADR 0034 개정으로 할지 신규 ADR로 할지 Phase 5에서 결정.
  레포 전역 grep 결과 `.env.example`/compose/배포 스크립트에 이 env
  참조 없음(= 손으로 세팅한 dev env 외 영향 없음).
- step 3: `app/safety/strike.py` — `UnknownSessionError(RuntimeError)` +
  `repo.session_exists` 선행 검사(부작용 전에 죽음). `/turn` 호출부는
  step 0 `resolve_session` 401 게이트 덕에 도달 불가 — 가드 추가 불필요.
  전 스위트 329 passed. 관찰: `scripts/check_no_hardcoded_dialogue.py`
  는 실행 비트 없음 — 인터프리터 경유로 호출해야 함.
- step 4 (검증 [FIX] 2건, 테스트 위생 전용 — 프로덕션 무변경):
  `tests/api/conftest.py` 에 `CONTRACT_COOKIE_MAX_AGE` +
  `assert_cookie_attrs_except_secure` 승격. `test_cookie_env_flag.py` /
  `test_identity_contracts.py` 는 env 이름을 `app.api.session_cookie`
  에서 import 하고(리터럴 인라인 제거), 속성 4종 단언을 공유 헬퍼로
  위임. `test_identity_contracts.py` 의 `COOKIE_NAME` 사설 리터럴도
  같은 이유로 프로덕션 import 로 교체. 329 passed (수 불변).

이번 런에서 생길 것 (구현자가 만들면서 여기에 등록):

- 세이브 코드 민팅 재시도 로직 — 발급과 회전이 공유해야 한다(현재
  `_mint_save_code` 가 `main.py` 사설. 두 번째 사용처가 생기는 순간
  공유층 승격 대상).
- redeem 시도 카운터 — 단일 홈 모듈. 테스트가 결정적으로 초기화할 수
  있는 진입점을 노출한다(TestClient 는 모든 테스트가 같은 호스트로
  잡히므로, 초기화 없이는 기존 redeem 계약 테스트가 오염된다).
- 프론트 넛지 판정 순수 함수 — 컴포넌트 밖(테스트 가능 seam).
- vitest 셋업 파일/헬퍼 — 신규 프론트 테스트는 이걸 쓴다.

## Layout & Naming

- Python: 기존 구조 유지 — `app/api`(endpoint), `app/store`(repo),
  `app/safety`, `app/turn`, `migrations/NNN_*.sql` 시퀀셜. 이번 런은
  스키마 변경 없음(`sessions.save_code` 단일 컬럼 유지) — 새 migration
  이 필요하다고 느껴지면 그건 spec 을 벗어난 신호다.
- `app/api/main.py` 는 300줄 리뷰 트리거 대상 — rotate 추가로 더 커지면
  라우터 단위 분리를 검토하고, 유지한다면 이유를 여기 한 줄로 기록.
- `frontend/src/App.tsx`(534줄): 이번 런에서 applyTurn+sendTurn 훅 추출을
  **실행한다**(Phase 2). 추출 후 남는 줄 수와 판단을 여기 갱신할 것.
- 프론트 테스트 파일 배치·명명은 위임 — 단 하드코딩 게이트 스캔 대상
  (`frontend/**/*.ts(x)`)이므로 문구는 반드시 tone 홈에서 import.
- dev 포트: backend **8765**(uvicorn), frontend **5173**(vite proxy →
  8765). 머신 상시 점유 포트(8080 llama-server, 8000, 8081, 5433, 5000,
  7000, 7265, 6463) 회피.

## Environment (이 머신 — 반드시 지킬 것)

- **죽이지 말 것**: `8080` llama-server(로컬 LLM — 이 프로젝트의 LLM
  백엔드), `8000` docker app-chak-backend, `8081` docker forps-backend,
  `5433` docker forps-postgres. 포트가 잡혀 있으면 먼저 확인
  (`lsof -nP -iTCP:<port> -sTCP:LISTEN`) — 무작정 kill 금지.
- `5000`/`7000` 은 macOS Control Center(AirPlay) 점유 — dev 포트로 쓰지
  말 것.
- 이 프로젝트 DB: `docker compose up -d db` 로 띄운다.
- Python 은 레포 `.venv` 사용 (`.venv/bin/pytest`, `.venv/bin/python`).
  프론트는 bun.

## Commit convention (레포 룰 — talpi 기본형보다 우선)

- 메시지: `talpi: phase <n> step <k>: <한국어 요약 — 결정 이유 포함>`.
  한국어 본문에 *왜* 그렇게 했는지가 들어가야 한다(CLAUDE.md).
- ADR 커밋은 ADR당 1커밋 (Phase 5).
- `--no-verify` / `--no-gpg-sign` 절대 금지.

## Failure Behavior

- 오류 응답 공통 형태: `{status:"error", message}` (+ HTTP 4xx/5xx) —
  앱 발신 오류에만 적용. FastAPI 기본 422/HTTPException detail 은
  프레임워크 기본값 그대로.
- 신규 429(시도 제한): 같은 형태 + 솔직한 시스템 톤, 문구는 rules YAML.
  "왜 막혔는지"를 숨기지 않되 공격자에게 유효 코드 정보를 주지 않는다.
- 404(미지/형식 위반/무효화된 코드): **하나의 문구로 통일** — 죽은 코드와
  오타를 구분하지 않는다(코드 히스토리가 없으므로 구분 자체가 불가).
- 401(무신원/모르는 세션): recoverable — 프론트는 자동 재bootstrap 1회,
  재실패 시 솔직한 시스템 톤, 무한 루프 금지.
- 탈출구 실패(401/밴/500/네트워크): recoverable — 코드를 못 받았다는
  사실만 솔직히 알리고, 갈아타기 자체는 계속 진행 가능해야 한다.
  탈출구 실패가 redeem 을 막으면 그게 회귀다.
- 인프라 실패(503 등): 솔직한 시스템 톤 — NPC를 흉내내지 않는다.
- 밴: fatal — HTTP 200 `{status:"banned"}`(오류 아닌 상태), 차단 화면,
  입력 봉인. 회전도 밴 세션에는 동작하지 않는다.
- `strike.register` 전제 위반: fatal(예외) — 단, 기존 호출부에서는
  **도달 불가**여야 한다. 도달하면 그것이 버그 신호이며, 플레이어가
  `/turn` 중 500 을 보는 상황은 회귀로 취급한다.
