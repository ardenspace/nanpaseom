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

## Prior work this phase (Phase 2 — 회전과 추측 방어)

- step 1: vitest 도입 — `frontend/vite.config.ts` 에 `test` 블록(jsdom,
  `src/**/*.test.ts(x)`, setup 파일, `globals:false`). 프로덕션 빌드와
  같은 Vite 파이프라인을 쓴다(별도 config 없음 → 플러그인/해석 드리프트
  방지). `frontend/src/test/setup.ts` (신규 공유 — 전 테스트가 경유),
  `frontend/src/playedHint.test.ts` (러너 실증 pin 3건).
  스크립트: `bun run test` / `test:watch`. `build` 불변.
  의존성: vitest 4.1.11, jsdom 30.0.1, @testing-library/react 16.3.2,
  @testing-library/dom 10.4.1. RTL 을 지금 넣은 이유: B1 의 "회전 도달
  가능 + 문구 명시"는 렌더 수준 사실이라 가짜 seam 을 만들어 pin 하면
  허구를 pin 하게 된다.
- step 2: 계약 pin — `tests/api/test_save_code_rotate.py`(B1 서버 12건 +
  B2 회귀), `tests/api/test_redeem_rate_limit.py`(B3 7건, 수치는 rules
  에서 읽어 하드코딩 없음), `frontend/src/App.saveCode.test.tsx`(B1
  어포던스 3건). `tests/api/conftest.py` 에 `set_save_code(sid, code)` /
  `banned_session(turns=1)` 승격. `frontend/src/test/setup.ts` 에
  `scrollIntoView` no-op 추가(jsdom 미구현 — 컴포넌트 테스트 필수).
  tone 신규: `SAVE_CODE_ROTATE`, `SAVE_CODE_ROTATE_WARNING`,
  `RETIRED_IMMUTABLE_CODE_CLAIM`(회귀 가드용 — 렌더 안 함).
  **다음 스텝이 반드시 제공할 seam**: `app/api/rate_limit.py` 모듈 레벨
  `reset()`, `rules/save_code.yaml` 키 3종(`redeem_rate_limit_attempts` /
  `redeem_rate_limit_window_seconds` / `redeem_rate_limited_message`) +
  `SaveCodeRules` 필드(extra=forbid 라 모델도 같이).
  **오염 주의**: 리미터는 프로세스 전역이고 기존 redeem 테스트가 전부
  같은 IP(`testclient`)를 쓴다 → `reset()` 을 공유 `client` fixture 에
  반드시 배선. 안 하면 기존 redeem 계약 테스트가 누적 카운트로 깨진다.
  **미pin 1건**: B3 "윈도우 만료 기록 정리" — 결정적 관찰에 시간 seam 이
  필요해, 구현 스텝이 seam 과 그 테스트를 함께 만든다.
- step 3: `POST /save-code/rotate` 구현. **신규 공유 유틸**:
  `app/save_code.py` 의 `mint_save_code(conn, session_uuid, *, avoid=None)`
  + `SAVE_CODE_MINT_ATTEMPTS` + `SaveCodeMintError` (기존 `main.py` 사설
  `_mint_save_code` 승격 — 발급/회전 공용, 도메인 모듈이라 HTTPException
  대신 도메인 예외). `avoid` 는 계약 요구: 회전이 우연히 같은 코드를
  재생성하면 옛 코드가 계속 통해버린다. `main.py` 에 `_mint` 얇은 어댑터
  (도메인 예외→500), `_no_session_response()` / `_banned_response(sess)`
  공유 응답 헬퍼(각각 3번째 사용처가 생겨 승격). 회전 성공은 Set-Cookie
  없음(세션 불변 — 오케스트레이터 결정). rules YAML 무변경(회전 전용
  서버 문구 없음, 401 은 identity.yaml 재사용).
  `app/api/main.py` 296줄 — 300줄 트리거 미만이라 단일 파일 유지.
  340 passed (기존 329 + rotate 11).
- step 4: redeem 시도 제한. **신규 공유 유틸**: `app/api/rate_limit.py`
  — `allow(key, *, limit, window_seconds)`, `client_ip(request)`
  (`request.client.host` 만 — XFF 절대 안 봄, client 없으면 `"-"` 공유
  버킷), `reset()`(테스트 경계 초기화 — 공유 `client` fixture 에 배선됨),
  **`now()` 시간 seam**(`time.monotonic` 래퍼 — 테스트는
  `monkeypatch.setattr(rate_limit, "now", fake_clock)` 로 시계를 민다.
  엔드포인트 시계도 같이 움직여 sleep 없이 윈도우 만료를 관찰).
  허용된 시도만 기록(차단이 윈도우를 연장하지 않음 → 영구 잠금 없음),
  청소는 윈도우당 1회 amortized sweep.
  수치: **10회 / 3600초** (rules/save_code.yaml). 사람 오타는 2–3회라
  3배 여유, 공격자는 하루 240 추측 → 유효 코드 1000개 가정에도 단일 IP
  기대 ~58일. 성공이 예산을 환급하지 않으므로 유효 코드 보유가 우회
  수단이 되지 않는다.
  `tests/api/test_rate_limit_cleanup.py` 신규(미pin 이었던 만료 정리 +
  윈도우 복구를 시간 seam 으로 pin). 352 passed.
  **프론트 인계**: redeem 오류 경로가 이미 `data.message` 를 그대로
  띄우므로 429 문구는 서버(rules)가 소유한다 — tone 에 중복 상수를
  만들지 말 것(같은 사실 한 홈).
- step 5: 훅 추출(동작 보존) + 401 회귀 pin. **신규 공유 유틸**:
  `frontend/src/useTurn.ts` — `useTurn(deps): { sendTurn(text) }`,
  `TurnDeps = { busy, setBusy, npcId, pushMsg, setChoices, showBanned,
  enterChat }`. `applyTurn` 은 훅 내부 비공개(다른 호출부 없음).
  `Msg` 타입의 홈도 여기(훅이 로그의 유일한 append 지점). 상태는 훅에
  두지 않음 — `busy` 를 타이틀/redeem/발급 경로가 공유하므로 App 소유.
  동작 델타는 밴 분기 2곳을 `showBanned(reason)` 로 합친 것뿐(`start()`
  는 choices 를 안 비우므로 일부러 제외).
  `frontend/src/App.turn401.test.tsx` — 401 복구 6건(호출 시퀀스까지
  단언해 '무한 루프 없음'을 pin).
  **App.tsx 534 → 476줄.**
- step 6: 회전 UI — 기존 세이브 코드 오버레이 안의 2상태 패널(신규
  오버레이 없음). 기본 상태[코드 복사/새 코드로 바꾸기/닫기] → 확인
  상태(코드는 그대로 보이고 note 자리에 경고, 서버 호출은 확인 누른
  뒤에만). **confirm-first** 선택 이유: 옛 코드를 쥔 쪽에게 회전은
  되돌릴 수 없으니 경고는 결과와 나란히가 아니라 *바꾸기 전에* 나와야
  한다. 성공 후 패널 유지(새 코드 표시, 복사 라벨 리셋) — 회전 직후가
  코드를 적어야 하는 순간이라 닫으면 필요한 걸 감춘다.
  **신규 공유 유틸**: `App.tsx` 모듈 스코프 `readSaveCodeResult(r)` —
  발급/회전이 unreachable/ok/banned/401 분기 읽기를 공유(오류를 어디
  띄우냐만 다름). `protocol.ts` 는 `SaveCodeIssueData` 재사용(유사
  중복 타입 안 만듦). `app.css` 에 `.overlay__body--warning` /
  `.overlay__error` / actions `flex-wrap`(버튼 3개) — 토큰만 사용.
  tone: `SAVE_CODE_ISSUED_NOTE` 개정(아래), 신규 상수 불필요.
  **App.tsx 476 → 558줄** (UI 추가분).
  **Phase 5 인계(중요)**: mechanic-spec/mapping-spec 에 세이브 코드
  회전 행이 없다 — 엔드포인트를 추가하고 권한 문서를 안 고친 상태라
  수락 때 drift 로 읽힌다. Phase 5 ADR/정렬 스텝에서 반드시 처리.

## Prior work — Phase 1 (완료, 참고용)

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
- `app/api/main.py` **313줄 — 300줄 리뷰 완료, 단일 파일 유지 결정**:
  자연스러운 절단선은 save-code 라우터인데 `redeem` 이 `bootstrap` 과
  `_bootstrap_response` / `_resumed_payload` / `_new_payload` /
  `BOOTSTRAP_NPC_ID` 를 공유한다 → 분리하면 세 번째 공유 모듈
  (`session_payload` 류)이 강제된다. 이건 리미터 추가와 직교하는 구조
  변경이라 자체 스텝을 가질 자격이 있고, 레이트리밋 커밋에 얹혀 가면 안
  된다. (다음 런 후보.)
- `frontend/src/App.tsx` **476줄** (훅 추출 완료 — 534에서 감량).
  300줄 트리거는 여전히 넘지만 유지: 남은 부피는 화면 3개(타이틀/밴/채팅)
  렌더 트리 + 세이브 코드 발급/redeem/복사 핸들러이고, 다음 절단선은
  화면 단위 컴포넌트 분리다(이번 런 범위 밖 — UI 를 더 얹는 페이즈가
  남아 있어 지금 자르면 두 번 자르게 된다).
- **기존 `/turn` 401 복구 경로의 관찰 사항** (step 5에서 발견, 고치지
  않고 기록 — 이번 런 범위 밖):
  1. 재시도가 복구 bootstrap 의 `npc_id` 대신 401 이전 클로저 값을 쓴다.
  2. `resumed` 복구 시 서버가 준 history/choices 를 버리고 화면을 그대로
     둔다(같은 세션이면 무해, 다른 세션이면 조용히 어긋남).
  3. `new` 복구 시 방금 보낸 플레이어 입력이 시스템 안내 없이 사라진다 —
     삼켜진 것처럼 읽힌다. (넛지 재노출이 키로 삼는 바로 그 seam.)
  4. "1회 복구"는 페이지 로드가 아니라 턴 단위 — 사용자 행동당 유계.
  5. `/turn` 비-401 실패는 서버 문구를 무시하고 GENERIC_ERROR 를 쓰는데
     bootstrap 실패는 서버 문구를 선호한다(같은 실패류에 다른 안내).
- 프론트 테스트 파일 배치·명명은 위임 — 단 하드코딩 게이트 스캔 대상
  (`frontend/**/*.ts(x)`)이므로 문구는 반드시 tone 홈에서 import.
- **프론트 테스트 이름은 영어로 쓴다.** 하드코딩 게이트는 *문자열
  리터럴*을 잡으므로 `it("힌트가 없으면…")` 자체가 위반이다. 한글
  주석은 따옴표로 감싸지만 않으면 통과. 사용자 문구 단언은 `tone.ts`
  에서 import (게이트가 설계대로 작동하는 것).
- 프론트 테스트 환경 주의: Node 25 는 `globalThis.localStorage` 를 이미
  갖고 있어 vitest jsdom 환경이 이를 건너뛴다 → `setup.ts` 가
  jsdom 실물 storage 로 재지정한다. 스토리지를 쓰는 테스트(넛지
  dismiss 플래그 등)는 이 setup 을 신뢰해도 된다.
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
