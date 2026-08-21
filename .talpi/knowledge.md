# Knowledge

## Decisions

- quote: 활성 코드는 세션당 정확히 1개. 회전 시 이전 코드 즉시 무효, 유예
  source: spec.md Reversibility Ledger (ADR 0038)
  date: 2026-08-21
- quote: 무조건 대체 확인을 유지한다(지난 런 설계 재확인).
  source: spec.md Reversibility Ledger (B4)
  date: 2026-08-21
- quote: 갈아타기 경고의 강제 지점은 클라이언트(배포된 UI)다.
  source: spec.md Reversibility Ledger
  date: 2026-08-21
- quote: 넛지 판정의 권위는 서버다 — 세션 진입 응답(bootstrap + redeem 공유
  source: spec.md Reversibility Ledger (ADR 0040)
  date: 2026-08-21
- quote: 넛지는 best-effort다 — "코드 보유"는 "코드를 실제로 적어뒀다"가
  source: spec.md Reversibility Ledger (ADR 0040)
  date: 2026-08-21
- quote: 넛지 임계값·문구는 프론트 톤 홈이 소유한다.
  source: spec.md Reversibility Ledger
  date: 2026-08-21
- quote: 회전은 추가 유출 차단이지 침입자 축출이 아니다 — 의식적 수용.
  source: spec.md Reversibility Ledger (ADR 0038 — 재검토 트리거: 계정 도입 런)
  date: 2026-08-21
- quote: redeem 시도 제한은 직결 IP 기준, XFF 불신뢰, 단일 프로세스 메모리.
  source: spec.md Reversibility Ledger (ADR 0039 — 배포 런 재검토 필수)
  date: 2026-08-21
- quote: INSECURE_COOKIE 허용목록 반전은 기존 env 값의 의미를 바꾼다
  source: spec.md Reversibility Ledger (ADR 0034 clause 2)
  date: 2026-08-21
- quote: 신원 = 쿠키 단일 소스, 무계정·무로그인 — 유지. 단, 코드 관리 부담이
  source: spec.md Reversibility Ledger (ADR 0033 재확인)
  date: 2026-08-21
- quote: 세이브 코드는 credential이다. HTTPS 전제는 배포 런에서 완성 — 그
  source: spec.md Reversibility Ledger
  date: 2026-08-21
- quote: acceptance declined: 런 리뷰 NOTE 4건 전부 수정 요청 (테스트 헬퍼 중복 2건, 백드롭 busy 잔류, mechanic-spec 낡은 노트)
  source: journal.md
  date: 2026-08-21
- quote: acceptance declined: 백드롭 피드백 완화, docs/retros 편입, ESC 메뉴를 v1 목표로 명시
  source: journal.md
  date: 2026-08-21

## Verified facts

- fact: pytest 게이트 전부 그린 (364 passed, 2 live deselected)
  command: .venv/bin/pytest -q 2>&1 | tail -1
  expect: 364 passed
  scope: app tests migrations rules scripts
  as of: 095ca92
- fact: 프론트 vitest 게이트 그린 (49 passed / 6 files)
  command: cd frontend && bun run test 2>&1 | grep -E "^ *Tests +[0-9]"
  expect: 49 passed
  scope: frontend/src frontend/vite.config.ts
  as of: 095ca92
- fact: 모든 YAML 파싱 OK (check_yaml 게이트)
  command: python3 scripts/check_yaml.py
  expect: All yaml parsed OK.
  scope: rules npcs scripts/check_yaml.py
  as of: 095ca92
- fact: NPC 대사/한국어 리터럴 하드코딩 게이트 클린 (테스트 파일 포함, tone.ts 단일 예외)
  command: .venv/bin/python scripts/check_no_hardcoded_dialogue.py && echo PASS
  expect: PASS
  scope: app frontend/src scripts/check_no_hardcoded_dialogue.py npcs
  as of: 095ca92
- fact: 세이브 코드 회전 엔드포인트 존재 (POST /save-code/rotate)
  command: grep -c '"/save-code/rotate"' app/api/main.py
  expect: 1
  scope: app/api/main.py
  as of: 095ca92
- fact: 회전 민팅은 현재 코드를 avoid 로 넘긴다 (같은 문자열 재생성 시 옛 코드가 살아남는 경로 차단)
  command: grep -c "avoid=current" app/api/main.py
  expect: 1
  scope: app/api/main.py app/save_code.py
  as of: 095ca92
- fact: redeem 시도 제한 수치는 rules YAML 단일 홈 (10회 / 3600초)
  command: grep -E "redeem_rate_limit_(attempts|window_seconds)" rules/save_code.yaml
  expect: redeem_rate_limit_attempts
  scope: rules/save_code.yaml app/save_code.py app/api/rate_limit.py
  as of: 095ca92
- fact: 레이트리밋 키는 직결 연결의 원격 주소다 (XFF 를 읽는 코드 없음 — 46줄은 안 본다는 주석)
  command: grep -c "client.host" app/api/rate_limit.py
  expect: 1
  scope: app/api/rate_limit.py
  as of: 095ca92
- fact: has_save_code 삽입 지점은 _entry_response 하나 — 정의 1 + 호출 2 (bootstrap, redeem)
  command: grep -c "_entry_response(" app/api/main.py
  expect: 3
  scope: app/api/main.py app/store/repo.py
  as of: 095ca92
- fact: 스키마 변경 없음 — migration 은 이전 런의 3개 그대로
  command: ls migrations/ | wc -l | tr -d ' '
  expect: 3
  scope: migrations
  as of: 095ca92
- fact: INSECURE_COOKIE 는 허용목록 판정 ('1'/'true' 만 켜짐)
  command: .venv/bin/python -c "from app.api.session_cookie import INSECURE_COOKIE_ON_VALUES; print(sorted(INSECURE_COOKIE_ON_VALUES))"
  expect: ['1', 'true']
  scope: app/api/session_cookie.py
  as of: 095ca92
- fact: strike.register 는 bare assert 가 아니라 실제 예외로 죽는다 (python -O 생존)
  command: .venv/bin/python -c "from app.safety.strike import UnknownSessionError; print(issubclass(UnknownSessionError, AssertionError))"
  expect: False
  scope: app/safety/strike.py
  as of: 095ca92
- fact: 넛지 판정은 컴포넌트 밖 순수 함수 (테스트 가능한 seam)
  command: grep -c "export function shouldShowSaveCodeNudge" frontend/src/saveCodeNudge.ts
  expect: 1
  scope: frontend/src/saveCodeNudge.ts
  as of: 095ca92
- fact: 넛지 임계값은 프론트 톤 홈 단일 소유 (rules YAML 아님)
  command: grep -c "SAVE_CODE_NUDGE_AFTER_TURNS" frontend/src/tone.ts
  expect: 1
  scope: frontend/src/tone.ts
  as of: 095ca92
- fact: 오버레이 백드롭은 in-flight 중 닫히지 않는다 (두 곳 모두 가드)
  command: grep -c "busy ? undefined :" frontend/src/App.tsx
  expect: 2
  scope: frontend/src/App.tsx
  as of: 095ca92
- fact: 이번 런의 ADR 3건 존재 (0038 회전 / 0039 시도 제한 / 0040 has_save_code+넛지)
  command: ls docs/adr/ | grep -c -E "^00(38|39|40)-"
  expect: 3
  scope: docs/adr
  as of: 095ca92

## Open questions

- question: 배포에서 Cloudflare Tunnel 을 쓰면 cloudflared 가 localhost 로 붙어 전 트래픽의 직결 IP 가 127.0.0.1 이 된다 — 10회/시간이 전 플레이어 공용 예산이 되어 redeem 이 불통이 되는데, 배포 런에서 어떤 게이트(부팅 assert? 프록시 앞단일 때 필수 env?)로 막을 것인가?
- question: 실제 배포(서버/도메인/HTTPS/프로세스 매니저)는 어디에 올릴 것인가 — 이전 런부터 승계된 미결?
- question: 서버가 기동 시 마이그레이션을 적용하지 않는다(`apply_migrations` 는 테스트/수동 경로 전용) — 배포 런의 런북에서 어떻게 다룰 것인가?
- question: iOS Safari 에서 백드롭 `:active` 가 실제로 걸리는가 — React 19 가 `#root` 에 위임 리스너를 달아 조상 체인 조건을 만족한다고 추론했을 뿐 실기기 확인은 못 했다?
- question: 복귀 시 진입 응답이 최근 8턴만 실어(`load_recent_turns(limit=8)`) 오프닝이 화면에서 사라지는데, "며칠 뒤" 돌아온 플레이어에게 진행 상실로 읽히지 않는가?
- question: `/turn` 401 복구가 `new` 로 끝나면 방금 보낸 플레이어 입력이 시스템 안내 없이 사라진다 — 삼켜진 것처럼 읽히는데 안내를 넣을 것인가?
- question: `/turn` 비-401 실패는 서버 문구를 무시하고 GENERIC_ERROR 를 쓰는데 bootstrap 실패는 서버 문구를 선호한다 — 같은 실패류에 다른 안내를 통일할 것인가?
- question: App.tsx(~690줄)의 다음 절단선은 `SaveCodePanel` + `ReplaceConfirmDialog` 추출(~350줄로 감량) — 언제 실행하는가?
- question: `app/api/main.py`(328줄)를 save-code 라우터로 쪼개려면 `redeem` 과 `bootstrap` 이 공유하는 페이로드 빌더를 세 번째 모듈로 빼야 하는데, 그 구조 변경을 자체 스텝으로 언제 할 것인가?
- question: mechanic-spec 의 타이틀 엔딩 저널 리스트와 `### 엔딩 저널` 블록은 미구현인데, ESC 메뉴와 같은 판정(여전히 v1 목표인가)을 언제 내릴 것인가?
- question: 밴 시 "세이브 코드 무효화" 는 컬럼을 비우는 게 아니라 redeem 거부로 성립하는데, 훗날 전체 초기화 기능이 생기면 같은 질문(컬럼을 비울 것인가 게이트로 막을 것인가)을 어떻게 답할 것인가?
- question: warning 응답 시 서버가 이전 choices 를 echo 하도록 계약을 바꿀 것인가 (두 런째 승계 중인 범위 밖 항목)?
- question: 실제 캐릭터/배경 이미지(surigong.png, bg.png)는 언제 frontend/public/assets/ 에 드롭인되는가 (규약은 frontend/ASSETS.md)?
