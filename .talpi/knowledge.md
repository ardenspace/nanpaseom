# Knowledge

## Decisions

- quote: 스택: React + Vite, 패키지 매니저 bun (3D 확장 대비 — 사용자 결정)
  source: archive/2026-08-19-sub3-frontend/spec.md Reversibility Ledger
  date: 2026-08-19
- quote: PREFIX = 가독 단어(허용 알파벳 내 4자 단어 목록) + 랜덤 4자 — `MAST-7X2K` 류
  source: docs/adr/0036-save-code-word-prefix-format.md (백필 ADR)
  date: 2026-08-19
- quote: 자유 입력 해제: awareness 85+ (기존 spec 유지 — "85가 더 극적" 사용자 재확인)
  source: archive/2026-08-19-sub3-frontend/spec.md Reversibility Ledger
  date: 2026-08-19
- quote: 인프라 실패 문구: 솔직한 시스템 톤
  source: archive/2026-08-19-sub3-frontend/spec.md Reversibility Ledger
  date: 2026-08-19
- quote: 복원: 최근 N턴만, 전체 스크롤백 없음 (개인 프로젝트 트레이드오프 의식적 수용)
  source: archive/2026-08-19-sub3-frontend/spec.md Reversibility Ledger
  date: 2026-08-19
- quote: 신원 모델 = 쿠키 단일 소스. 계정/로그인 없음, 기기 이동은 세이브
  source: spec.md Reversibility Ledger (ADR 0033)
  date: 2026-08-20
- quote: 세션 번호는 서버만 생성 — bootstrap이 클라이언트 지정 UUID를 세션
  source: spec.md Reversibility Ledger (ADR 0033)
  date: 2026-08-20
- quote: 쿠키 속성 4종: HttpOnly / Secure / SameSite=Lax / Max-Age 180일.
  source: spec.md Reversibility Ledger (ADR 0034, 0037)
  date: 2026-08-20
- quote: 쿠키 값 = 서명 없는 bearer UUID (패널 `[BLOCKING]` 지적을 사람이
  source: spec.md Reversibility Ledger (ADR 0034 — 커뮤 공개 전 재검토)
  date: 2026-08-20
- quote: 세이브 코드 무차별 대입 = 의식적 수용. 유출 시 코드 무효화/회전
  source: spec.md Reversibility Ledger (ADR 0034 — 커뮤 공개 전 재검토)
  date: 2026-08-20
- quote: 대화 기록 무기한 보존, 플레이어 측 삭제 경로 없음 = 의식적 수용
  source: spec.md Reversibility Ledger (ADR 0034 — 커뮤 공개 전 재검토)
  date: 2026-08-20
- quote: 조용한 덮어쓰기 = 의식적 수용 (패널 재검증 `[BLOCKING]` 을 사람이
  source: spec.md Reversibility Ledger (ADR 0034 — "쿠키는 편의, 코드가 열쇠")
  date: 2026-08-20
- quote: acceptance declined: 런 리뷰 NOTE 4건 정리 요청 (strike 잔재, 낡은 주석, INSECURE_COOKIE 값 판정, dist README 위생)
  source: journal.md
  date: 2026-08-20

## Verified facts

- fact: pytest 게이트 전부 그린 (296 passed, 2 live deselected)
  command: .venv/bin/pytest -q 2>&1 | tail -1
  expect: 296 passed
  scope: app tests migrations rules scripts frontend/src
  as of: 150a84a
- fact: 모든 YAML 파싱 OK (check_yaml 게이트)
  command: python3 scripts/check_yaml.py
  expect: All yaml parsed OK.
  scope: rules npcs scripts/check_yaml.py
  as of: 150a84a
- fact: NPC 대사/한국어 리터럴 하드코딩 게이트 클린 (frontend 포함, tone.ts 단일 예외)
  command: python3 scripts/check_no_hardcoded_dialogue.py && echo PASS
  expect: PASS
  scope: app frontend/src frontend/index.html scripts/check_no_hardcoded_dialogue.py npcs
  as of: 150a84a
- fact: 세이브 코드 단어 프리픽스 목록 15개 (허용 알파벳 내 4자, 모듈 assert 강제)
  command: .venv/bin/python -c "from app.save_code import SAVE_CODE_PREFIX_WORDS; print('words:', len(SAVE_CODE_PREFIX_WORDS))"
  expect: words: 15
  scope: app/save_code.py
  as of: 150a84a
- fact: 세션 쿠키 Max-Age 180일 상수 = 15552000 (session_cookie 단일 홈)
  command: .venv/bin/python -c "from app.api.session_cookie import SESSION_COOKIE_MAX_AGE; print(SESSION_COOKIE_MAX_AGE)"
  expect: 15552000
  scope: app/api/session_cookie.py
  as of: 150a84a
- fact: ensure_session 호출부는 bootstrap 경로 1곳뿐 (세션 생성 문 단일 — Req 8)
  command: grep -rn "ensure_session(" app/ --include="*.py" | grep -v "def ensure_session" | wc -l | tr -d ' '
  expect: 1
  scope: app
  as of: 150a84a
- fact: FastAPI 자동 문서 비활성화 (docs_url=None)
  command: grep -c "docs_url=None" app/api/main.py
  expect: 1
  scope: app/api/main.py
  as of: 150a84a
- fact: 신원 해석기 단일 지점 존재 (resolve_session — 세션 생성 없음)
  command: .venv/bin/python -c "from app.api.identity import resolve_session; print('ok')"
  expect: ok
  scope: app/api/identity.py
  as of: 150a84a

## Open questions

- question: "커뮤 공개 전 재검토 목록"(ADR 0034: bearer 쿠키, 세이브 코드 무차별 대입/회전 불가, 익명 대량 민팅+밴 우회, 무기한 보존, 조용한 덮어쓰기)은 어떤 트리거/시점에 재검토하는가?
- question: 실제 배포(서버/도메인/HTTPS/프로세스 매니저)는 다음 런 — 어디에 올릴 것인가?
- question: NANPASEOM_INSECURE_COOKIE 판정을 truthy 허용목록("1"/"true"만 켜짐)으로 뒤집을 것인가 (런 리뷰 NOTE, 수락 시 보류 — 현재는 falsy 3종만 차단)?
- question: strike.register가 전제(존재 확인된 세션) 위반 시 조용한 무동작 대신 시끄러운 assert로 죽게 바꿀 것인가 (런 리뷰 NOTE, 수락 시 보류)?
- question: App.tsx(534줄)의 다음 분리 절단선은 applyTurn+sendTurn 훅 추출 — 언제 실행하는가?
- question: warning 응답 시 서버가 이전 choices를 echo하도록 계약을 바꿀 것인가 (이전 런부터 승계, 이번 런 범위 밖 유지)?
- question: 실제 캐릭터/배경 이미지(surigong.png, bg.png)는 언제 frontend/public/assets/에 드롭인되는가 (규약 서식지는 frontend/ASSETS.md로 이전됨)?
