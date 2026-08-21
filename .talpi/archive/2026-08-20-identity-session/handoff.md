# Handoff — 공개 배포 신원/세션 런

## Where the run stands

**run done — 2026-08-20 사람 수락 완료, knowledge 증류 완료 (check/
replay 게이트 클린).** 빌드할 것 없음. 다음 세션은 새 런(talpispec)
으로 시작 — 유력 후보는 "실제 배포" 런 (knowledge.md Open questions
참조).

## What this run shipped

난파섬 코드 기준 공개 배포 가능 상태: 쿠키 단일 신원(무신원 401,
서버 전용 민팅, 응답 본문 무 session_uuid), 세이브 코드 발급 문단속,
/assets 화이트리스트 + /docs 봉인, 프론트 정합(401 자동 복구 1회),
ADR 0033–0037. 페이즈 4개(3 + acceptance-fixes), 게이트 296 passed.

## For the next run

- .talpi/knowledge.md 가 증류본 (decisions/facts/open questions) —
  다음 talpispec이 게이트 후 상속.
- 이전 런 아카이브: .talpi/archive/2026-08-19-sub3-frontend/. 이번 런
  아티팩트(spec/plan/conventions/manual-check)는 다음 런 시작 시 같은
  패턴으로 archive/2026-08-20-identity-session/ 으로 이동 권장.
- journal.md 는 append-only 영속 (아카이브 금지 — knowledge 인용
  대상). 주의: status.sh 는 journal 의 마지막 run done/halted 로
  라우팅하므로, 새 런 시작 시 이전 런의 'run done' 이 새 런을 가림 —
  이번 런은 정직한 halt/resume 마커 2줄로 해소했음 (journal
  2026-08-20T04:13 참조), 다음 런도 같은 처리 필요.
