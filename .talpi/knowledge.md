# Knowledge

## Decisions

- quote: 스택: React + Vite, 패키지 매니저 bun (3D 확장 대비 — 사용자 결정)
  source: spec.md Reversibility Ledger
  date: 2026-08-19
- quote: PREFIX = 가독 단어(허용 알파벳 내 4자 단어 목록) + 랜덤 4자 — `MAST-7X2K` 류
  source: spec.md Reversibility Ledger
  date: 2026-08-19
- quote: run resumed after human ruling (세이브 코드 단어 프리픽스 reject→재구현, 검증 CLEAN)
  source: journal.md
  date: 2026-08-19
- quote: 자유 입력 해제: awareness 85+ (기존 spec 유지 — "85가 더 극적" 사용자 재확인)
  source: spec.md Reversibility Ledger
  date: 2026-08-19
- quote: 쿠키 미검증 = UUID가 사실상 bearer
  source: spec.md Reversibility Ledger (공개 배포 전 필수 해결)
  date: 2026-08-19
- quote: 인프라 실패 문구: 솔직한 시스템 톤
  source: spec.md Reversibility Ledger
  date: 2026-08-19
- quote: 복원: 최근 N턴만, 전체 스크롤백 없음 (개인 프로젝트 트레이드오프 의식적 수용)
  source: spec.md Reversibility Ledger
  date: 2026-08-19

## Verified facts

- fact: pytest 게이트 전부 그린 (239 passed, 2 live deselected)
  command: .venv/bin/pytest -q 2>&1 | tail -1
  expect: 239 passed
  scope: app tests migrations rules scripts
  as of: f134055
- fact: 모든 YAML 파싱 OK (check_yaml 게이트)
  command: python3 scripts/check_yaml.py
  expect: All yaml parsed OK.
  scope: rules npcs scripts/check_yaml.py
  as of: f134055
- fact: NPC 대사/한국어 리터럴 하드코딩 게이트 클린 (frontend 포함, tone.ts 단일 예외)
  command: python3 scripts/check_no_hardcoded_dialogue.py && echo PASS
  expect: PASS
  scope: app frontend/src frontend/index.html scripts/check_no_hardcoded_dialogue.py npcs
  as of: f134055
- fact: 세이브 코드 단어 프리픽스 목록 15개 (허용 알파벳 내 4자, 모듈 assert 강제)
  command: .venv/bin/python -c "from app.save_code import SAVE_CODE_PREFIX_WORDS; print('words:', len(SAVE_CODE_PREFIX_WORDS))"
  expect: words: 15
  scope: app/save_code.py
  as of: f134055
- fact: 세션 쿠키는 Max-Age 180일 영속 (상수 정의 + set_cookie 사용, 발급 단일 경로)
  command: grep -c "SESSION_COOKIE_MAX_AGE" app/api/main.py
  expect: 2
  scope: app/api/main.py
  as of: f134055

## Open questions

- question: 스테일(미지) 쿠키로 /save-code 발급 시 서버가 0턴 세션을 만들어 코드를 민팅하는데, 무쿠키처럼 거부해야 하는가?
- question: /turn(body session_uuid)과 /save-code(쿠키)의 신원 소스 불일치를 공개 배포 전 어떻게 통일할 것인가 (쿠키 검증 추가 vs 쿠키-온리 전환)?
- question: 런 중 락인 2건(세이브 코드 단어 프리픽스, 180일 쿠키)을 docs/adr/에 ADR로 기록할 것인가 (레포 룰상 ADR 거리)?
- question: frontend/public/assets/README.md가 빌드에 복사되어 /assets/README.md로 공개 서빙되는 것을 막아야 하는가?
- question: warning 응답 시 서버가 이전 choices를 echo하도록 B1 계약을 바꿀 것인가 (현재 "이전 선택지 유지" 규칙은 클라이언트 보유)?
- question: 테스트 헬퍼(_raising_llm, set-cookie 헤더 파서)가 test_bootstrap.py/test_save_code.py에 중복인데 공유 conftest로 추출할 것인가?
- question: 실제 캐릭터/배경 이미지(surigong.png, bg.png)는 언제 frontend/public/assets/에 드롭인되는가?
