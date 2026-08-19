# Handoff — 난파섬 프론트엔드 + 이어하기 (Phase 1.0 Sub-3)

상태: Phase 1 완료·리포트됨 (verifier 5 FIX 수정 포함, 221 passed).
Phase 2 (닫았다 다시 와도 이어진다) 진입 시점 — step 1 미착수.

## 어디까지 왔나

- Phase 1 (base 819dca3): 브라우저 첫 플레이 전체 랜딩. 커밋 f3598a2 →
  0d42227. B1/B2/B4 그린. 조기 랜딩: B4 정적 라우트(step 2에서),
  resumed 렌더(step 4 App.tsx에서).
- Phase 2 계약 없음 — B2 시맨틱에 대한 frontend conformance 페이즈.
  남은 실질 작업: 타이틀 이어하기 분기(쿠키 세션 존재 시 문구/UX),
  밴 세션 재방문 차단 화면 확인, 복원 UX 폴리시(최근 N턴 + 선택지/
  자유입력 모드) — 상당 부분 App.tsx에 이미 있어 conformance 확인+폴리시
  성격.
- Phase 3: 세이브 코드 (B3, B5) — migration 003, 발급/redeem, UI.

## 컨텍스트 포인터

- 유저(Arden)와 Telegram으로 소통 중 (chat_id 7656702539). 페이즈
  리포트는 Telegram reply로 보냄.
- 실행: uvicorn 8765 + vite 5173 (또는 빌드 후 8765 단독). llama-server
  8080 상시 실행 중 (죽이지 말 것). DB: docker compose db (5432).
- 게이트: `.venv/bin/pytest` (221 passed, 2 live deselected),
  `python3 scripts/check_yaml.py`, `python3 scripts/check_no_hardcoded_dialogue.py`.
- 미결 참고: warning 시 "이전 선택지 유지" 규칙은 클라이언트 보유 —
  서버 echo가 더 견고하나 계약 변경이라 보류 (유저에게 고지됨, phase 1
  리포트). 이미지(surigong.png/bg.png)는 유저가 나중에 제공 — 드롭인.
- manual-check.md에 Phase 1 눈검증 6항목 — 최종 수락 때 유저가 걸음.
