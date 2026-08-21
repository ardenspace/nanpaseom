# Conventions

## Baseline (applies unless overridden)

- Repeated literals (colors, spacing, paths, magic numbers) live in one
  named home — frontend는 디자인 토큰 파일, Python은 상수 모듈 — never
  inlined in two places. 이번 런 적용 사례: 쿠키 이름/속성/Max-Age 등
  세션 상수는 한 모듈에 모은다.
- Logic appearing a second time is extracted into the shared layer and
  registered under Shared Utilities below.
- User-visible failure wording follows one tone, defined in one place
  (서버 발신 문구는 rules YAML, frontend는 tone 모듈 — Failure
  Behavior 참조).
- A file growing past ~300 lines triggers a split review. Staying
  single-file is a legitimate outcome — record why under Layout &
  Naming. Review trigger, not a hard limit.

레포 룰 승격 (CLAUDE.md와 병행 유효 — talpi 파이프라인이라고 면제되지
않음):

- 권한 경계: 같은 사실은 한 spec 문서에만. 메커니즘/인프라 변경 시
  mechanic-spec 갱신, 메커니즘이면 mapping-spec 정렬 확인.
- 새 락인 결정은 ADR (`docs/adr/NNNN-*.md`, 4자리 시퀀셜, ADR당
  1커밋) 후 spec/YAML 갱신.
- NPC 대사/서버 발신 안전·시스템 메시지 하드코딩 금지 — frontend 포함
  (`scripts/check_no_hardcoded_dialogue.py`, tone 모듈 단일 예외).
  서버 발신 신규 문구(401 등)는 rules YAML에. YAML 변경 시
  `python3 scripts/check_yaml.py`.
- git: logical unit per commit, 한국어 커밋 메시지에 결정 이유,
  `--no-verify`/`--no-gpg-sign` 금지.
- 테스트: `.venv/bin/pytest` 게이트는 결정적(stub llm) — `-m live`는
  off-gate. 신규 계약 테스트도 이 구분을 따른다. 테스트 환경의 Secure
  쿠키 처리(http TestClient 재전송 문제)는 env 플래그든 헤더 직접
  단언이든 게이트 그린이 기준 (spec Delegated).

## Design Tokens

이번 런은 시각 변경 없음 — 기존 체계 유지: 테마 딥블루 · 모래 · 녹슨
철 · 어둑한 바다 · 몽환, `frontend/src/tokens.css` (CSS custom
properties) 단일 홈. `--color-abyss`(배경) / `--color-sand`(본문·말풍선)
/ `--color-rust`(액센트) / `--color-system`(warning/ban/오류 등 프레임
깨는 시스템 문구 전용 — NPC 말풍선 색과 절대 공유 금지).
spacing/radius/type scale 같은 파일. 컴포넌트에 리터럴 색/픽셀 금지.

## Shared Utilities

기존 (재사용 대상):

- `tests/api/conftest.py` — 공유 `client` fixture (migrations +
  truncate, `llm_client.call` + `summarize_call` 스텁) +
  `make_stub_reply()`. 신규 API 테스트는 이걸 쓴다.
- `frontend/src/api.ts` — `postJson<T>` 공유 클라이언트 (fetch + JSON +
  네트워크 실패 정규화 `ApiResult<T>`; 한국어 리터럴/상태 로직 없음).
- `app/turn/loop.py` — `build_turn_context()` + `TurnContext`.
- `app/store/repo.py` — 세션/턴/세이브 코드 저장 접근 단일 홈.
- `app/save_code.py` — 세이브 코드 알파벳/형식 상수 + 생성.
- `rules/opening.yaml` / `rules/save_code.yaml` — bootstrap/세이브 코드
  관련 서버 발신 문구의 유일한 홈 (401 신규 문구도 rules YAML에).

이번 런에서 생긴 것:

- `app/api/session_cookie.py` — 세션 쿠키 단일 홈: `COOKIE_NAME`,
  `SESSION_COOKIE_MAX_AGE`(15552000), `INSECURE_COOKIE_ENV =
  "NANPASEOM_INSECURE_COOKIE"`, 발급 단일 경로
  `set_session_cookie(response, session_uuid)` (HttpOnly/Secure/
  SameSite=Lax/Max-Age/Path=/, Secure는 request 시점 env resolve로
  플래그 켜진 경우에만 생략). 쿠키 발급은 반드시 이 함수 경유.
- 테스트 환경 Secure 방침: tests/api/conftest.py 공유 client fixture가
  `NANPASEOM_INSECURE_COOKIE=1` setenv (http TestClient 재전송 문제).
  Secure 단언 계약 테스트는 test 본문 delenv로 override.
- `app/api/identity.py` — B7 신원 해석기: `parse_session_cookie(request)`
  (파싱+UUID 형식만), `resolve_session(conn, request)` (파싱→검증→존재
  확인, 통과 시 uuid / 거부 시 None, **세션 생성 절대 없음** — 거부
  처리는 호출자 소관). 쿠키 신원 판정은 반드시 이걸 경유.
- `app/store/repo.py` — `session_exists(conn, uuid)` 추가 (조회만).
- `rules/identity.yaml` — 401 `no_session_message` / 404
  `unknown_npc_message` 의 유일한 홈 (`app/api/identity.py` 의
  `load_identity_rules()`, pydantic extra=forbid).
- `app/api/main.py` — `WIRED_NPC_IDS = ("surigong",)` 배선 NPC 목록
  단일 홈 (BOOTSTRAP_NPC_ID 파생).
- tests/api/conftest.py — `known_session(turns=0)` (repo 직접 생성
  세션 픽스처), `session_cookie_headers(response)` / `cookie_value(
  header)` / `session_cookie_value(response)` (Set-Cookie 관찰 유틸 —
  응답 본문엔 sid가 더 이상 없음), `db_conn()` / `count_sessions()` /
  `session_row_exists(sid)` / `db_save_code(sid)` (DB 관찰),
  `raising_llm(monkeypatch)` (LLM 실패 스텁). 신규 테스트는 이걸 쓴다.
- 신원 해석기 (쿠키 파싱 → UUID 검증 → 세션 존재 확인, 세션 생성 절대
  금지) — /turn·/save-code 공용, bootstrap의 파싱 단계 공유 여부 재량.

## Prior work this phase (Phase 4 — Acceptance fixes)

(런 리뷰 NOTE 4건 정리. 계약 없음 — 기존 pin 안의 정리.)

- step 1: strike.register ensure_session 제거 + 미생성 pin 테스트
  (tests/safety/test_strike.py). 290 passed.
- step 2: session_cookie.py `_insecure_cookie_enabled()` — falsy
  ("", "0", "false" 대소문자/공백 무시)는 Secure 유지, falsy 6종 pin.
  296 passed.
- step 3: App.tsx 주석 401 갱신, 에셋 드롭인 안내 →
  frontend/ASSETS.md (public/assets엔 .gitkeep만 — dist에 문서류 0).

## Phase 3 완료 기록 (참고)

(Phase 1–2 완료 요약: 백엔드 계약 B1–B7 전부 green. /turn·/save-code
쿠키 단일 신원(무신원 401, rules/identity.yaml 문구), 서버 전용 민팅,
쿠키 속성 4종(session_cookie.py `set_session_cookie` 단일 경로,
NANPASEOM_INSECURE_COOKIE로 Secure만 생략 가능), 응답 본문에서
session_uuid 전면 제거(프론트는 Set-Cookie로만 세션 유지), npc_id
배선 검증 404, /assets 확장자 화이트리스트, /docs 봉인. 전체 스위트
289 passed 0 failed.)

- step 1: 프론트 정합 — App.tsx sessionUuid 상태/본문 필드 제거,
  401 → 재bootstrap 1회(resumed면 보류 턴 재시도, new면 enterChat,
  재실패 시 tone.ts SESSION_RESTORE_FAILED). api.ts ApiResult에
  status 추가(전송 계층 사실만). frontend/src에 session_uuid 잔재 0.
  주의: 하드코딩 게이트는 주석 안 따옴표 한글도 잡음.
- step 2: 스모크 a–g 전부 PASS (실 LLM, 8765) — 복원/redeem/위조 차단
  /위생 실증. manual-check.md 신규(브라우저 눈 확인 8절). 관찰 1건
  (수정 안 함): frontend/public의 README.md가 dist에 복사됨 — B5가
  서빙을 404로 막아 노출은 없음, 빌드 위생 개선 후보.
- step 3: ADR 0033–0037 (신규 3 + 백필 2, ADR당 1커밋) +
  mechanic-spec Identity hardening/save-code/Public surface hygiene
  정렬(상세는 ADR 위임), mapping-spec은 매핑 행 해당 없음 — 미매핑
  의도 리스트에 1줄. "커뮤 공개 전 재검토 목록"의 단일 서식지 = ADR
  0034.

## Layout & Naming

- Python: 기존 구조 유지 — `app/api`(endpoint), `app/store`(repo),
  `app/safety`, `app/turn`, `migrations/NNN_*.sql` 시퀀셜.
- `app/api/main.py` 는 300줄 리뷰 트리거 대상 — 신원 해석기/세션 상수
  분리로 자연 감량 예상, 분리 시 라우터 단위.
- tests/api/test_identity_contracts.py 는 393줄 단일 파일 유지 (300줄
  리뷰 완료): B1·B2·B6·B7은 같은 spec 동결(쿠키 단일 신원)의 상호참조
  계약이고 테스트가 계약 경계를 넘나들어(redeem rebind의 B6 단언 등)
  분리하면 로컬 단언 헬퍼의 승격/중복만 늘고 계약 pin 모듈의
  자기완결성이 깨짐.
- frontend: App.tsx는 534줄 유지 (300줄 리뷰 재확인): 증가분은 화면
  3개가 공유하는 상태 머신 내부의 401 복구 경로(sendTurn+applyTurn) —
  분리하면 상태 setter 배선만 늘어남. 다음 절단선은 applyTurn+sendTurn
  훅 추출.
- frontend: bun + Vite + React, `frontend/src/`. App.tsx(~498줄)는 300줄
  리뷰 통과 상태(화면 3개가 세션 상태 머신 하나 공유) — 이번 런 수정
  후에도 같은 사유면 유지 OK.
- dev 포트: backend **8765**(uvicorn), frontend **5173**(vite proxy →
  8765). 이 머신 점유 포트(8080 llama-server, 8000, 8081, 5433, 5000,
  7000, 7265, 6463) 회피.

## Failure Behavior

- 오류 응답 공통 형태: `{status:"error", message}` (+ HTTP 4xx/5xx) —
  앱 발신 오류에만 적용, FastAPI 기본 422/HTTPException detail은
  프레임워크 기본값 그대로 (spec 완전성 기록).
- 401 (무신원/모르는 세션): recoverable — 프론트는 자동 재bootstrap
  1회, 재실패 시 솔직한 시스템 톤 오류 표시, 무한 루프 금지.
- 인프라 실패(503 등): 솔직한 시스템 톤 — NPC를 흉내내지 않는다.
  문구는 서버 발신이면 rules YAML, 프론트 자체 문구면 tone 모듈.
- 밴: fatal — HTTP 200 `{status:"banned"}` (오류 아닌 상태), 차단 화면,
  입력 봉인.
- LLM 출력 검증 실패의 diegetic_fallback: 기존 그대로 — 프론트는 npc
  응답으로 취급.
