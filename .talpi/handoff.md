# Handoff — 세이브 연속성 런

## Where the run stands

**run done — 2026-08-21 사람 수락 완료, knowledge 증류 완료 (check/replay
게이트 클린).** 빌드할 것 없음. 다음 세션은 새 런(talpispec)으로 시작 —
유력 후보는 "실제 배포" 런 (knowledge.md Open questions 첫 항목이 그 런의
첫 작업 후보다).

수락 이력: 1차 거절(런 리뷰 NOTE 4건 수정 요청) → Phase 6 → 2차 거절
(백드롭 피드백/retro 편입/ESC 메뉴 판정) → Phase 7 → 3차 수락.

## What this run shipped

세이브 연속성의 세 가장자리를 메웠다.

1. **회전** (`POST /save-code/rotate`) — 유출된 코드를 죽이고 새 코드를
   받는 경로. 확인 먼저, 성공 후 새 코드를 계속 표시. ADR 0038.
2. **탈출구** — 대체 확인 다이얼로그 안에서 갈아타기 *전에* 현재 진행의
   코드를 받는 경로. 실패해도 갈아타기를 막지 않는다.
3. **넛지** — 코드 없는 세션에 진행이 쌓이면(신규 6턴 / 코드 없는
   resumed 는 즉시) 입력 바 위 시스템 배너로 권유 + 행동 버튼.
   판정 권위는 서버 `has_save_code`(ADR 0040).
4. **redeem 시도 제한** — 직결 IP당 10회/1시간, 초과 시 429. ADR 0039.
5. 지난 런이 남긴 위생 2건 — INSECURE_COOKIE 허용목록 반전(fail-closed),
   strike.register 예외화(python -O 생존).
6. 프론트 테스트 러너 도입(vitest+jsdom+RTL, 45 tests) + App.tsx
   applyTurn/sendTurn 훅 추출.

게이트: pytest 364, vitest 45, check_yaml OK, 하드코딩 게이트 clean,
`bun run build` green. 스키마 변경 없음, 신규 런타임 의존성 없음.

## 남은 것 (사람 몫)

- `.talpi/manual-check.md` 의 브라우저 눈 확인 28항목 — 서버 경로는 자동
  스모크가 4회 걸었지만 화면은 사람만 볼 수 있다. 가장 확인 가치가 높은
  것은 **iOS 실기기에서 백드롭 `:active` 가 걸리는지** (추론만 했고
  실기기 미검증).
- **[배포 런 첫 작업] 레이트리밋 × Cloudflare Tunnel**: cloudflared 가
  localhost 로 붙으면 전 트래픽의 직결 IP 가 127.0.0.1 이라 10회/시간이
  전 플레이어 공용 예산이 된다 — 방어 약화가 아니라 redeem 가용성 장애.
  knowledge.md Open questions 첫 항목.

## For the next run

- 유력 후보는 **배포 런**(서버/도메인/HTTPS/프로세스 매니저). 위
  [ESCALATE] 가 그 런의 첫 작업 후보다.
- App.tsx(684줄) 절단선이 분명해졌다: `SaveCodePanel` +
  `ReplaceConfirmDialog` 추출 → ~350줄. `CopyCodeButton.tsx` 가 그
  디렉토리의 첫 입주자.
- 훅 추출 중 발견한 기존 `/turn` 401 복구 경로 관찰 5건이
  conventions.md 에 있다(그중 하나는 플레이어 체감: `new` 복구 시 방금
  보낸 입력이 안내 없이 사라진다).
- `docs/retros/` 는 의도적으로 untracked 상태 — 레포에 넣을지는 사람 몫.
- journal.md 는 append-only 영속(아카이브 금지). 다음 런 시작 시 이번
  런 아티팩트(spec/plan/conventions/manual-check/handoff)를
  `archive/2026-08-21-save-continuity/` 로 옮기고, status.sh 가 이전 런의
  `run done` 으로 라우팅하지 않도록 `run started over done run` 을
  저널에 남길 것(talpispec 가드가 처리한다).
