# Handoff — 공개 배포 신원/세션 런

## Where the run stands

- Phase 1–3 전부 완료·검증됨 (plan.md 체크박스 + git log가 근거).
  계약 B1–B7 green, 전체 스위트 289 passed 0 failed, 게이트 3종 그린.
- 스모크 런: Phase 3 step 2에서 실기동으로 a–g 전부 PASS (실 llama-
  server 턴 포함, 이후 변경은 docs/ADR뿐이라 completion 스모크로 유효).
- 현재 위치: **completion 단계 — 런 전체 리뷰어(fresh) 실행 후 최종
  리포트/수락 대기로 이행 예정**. journal의 마지막 완료 이벤트가
  기준: `run review (through <hash>)` 라인이 있으면 리뷰까지 끝난 것,
  `final report sent, awaiting acceptance`가 있으면 사람 수락만 남은 것.
- 소통 채널: 사람(아덴)과 Telegram으로 대화 중 (chat_id 7656702539).
  페이즈 리포트 3건 발송됨.

## Key state

- state.md: building / 4 / 3 (cur > total = completion 신호).
- run base: ba3818a (phase 1 base). 페이즈 base: P1 ba3818a, P2
  72c691c, P3 8c4dd05.
- manual-check.md: 브라우저 눈 확인 8절 — 최종 수락 요청 때 사람에게
  건넬 것.
- 수락 대기 중 남길 [NOTE] 후보: frontend/public/README.md가 dist에
  복사됨 (B5가 서빙 404로 차단, 빌드 위생 개선 후보 — P3S2 관찰).
  + 런 리뷰어가 낸 [NOTE]들 (journal 이후 기록 참조).

## Environment

- 로컬 LLM llama-server: 포트 8080 — 절대 죽이지 말 것.
- dev: backend 8765 (uvicorn, NANPASEOM_INSECURE_COOKIE=1 +
  NANPASEOM_STATIC_DIR=frontend/dist), frontend vite 5173.
- 테스트: `docker compose up -d db` 후 `.venv/bin/pytest`.

## On acceptance / rejection

절차는 현행 talpirun 스킬 텍스트를 따를 것 (여기 요약하지 않음 —
스킬이 진실). 수락 시 knowledge 증류 대상 후보: ADR 0033–0037 인용,
게이트 커맨드들(pytest/check_yaml/hardcoded/bun build), 신원 해석기·
session_cookie 단일 홈 사실, 열린 질문(README dist 위생, App.tsx
분리 절단선, /save-code 401 프론트 처리 등).
