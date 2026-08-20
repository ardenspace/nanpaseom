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

이번 런에서 생길 것 (구현자가 만들며 여기 등록):

- 세션 상수 모듈 (쿠키 이름/속성/Max-Age/dev env 플래그) — 위치 재량.
- 신원 해석기 (쿠키 파싱 → UUID 검증 → 세션 존재 확인, 세션 생성 절대
  금지) — /turn·/save-code 공용, bootstrap의 파싱 단계 공유 여부 재량.

## Layout & Naming

- Python: 기존 구조 유지 — `app/api`(endpoint), `app/store`(repo),
  `app/safety`, `app/turn`, `migrations/NNN_*.sql` 시퀀셜.
- `app/api/main.py` 는 300줄 리뷰 트리거 대상 — 신원 해석기/세션 상수
  분리로 자연 감량 예상, 분리 시 라우터 단위.
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
