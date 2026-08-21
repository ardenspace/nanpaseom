# Handoff — 세이브 연속성 런

## Where the run stands

**빌드 완료, 사람 수락 대기 중.** 5개 페이즈 전부 끝났고 페이즈 검증도
전부 통과, 스모크 워크(실 LLM, HTTP 경로) 10/10 PASS, 전체 런 리뷰까지
돌았다. 남은 것은 사람의 수락 하나뿐 — 새로 빌드할 것은 없다.

수락 전에 사람이 할 일: `.talpi/manual-check.md` 의 브라우저 눈 확인
23항목(Phase 2/3/4)을 걷는 것. 서버 경로는 자동 스모크가 덮었지만
"경고가 언제 뜨는지 / 문구 말투 / 배너 위치" 는 화면으로만 확인된다.

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

## 사람이 수락 때 판정할 것 (런 리뷰 findings)

최종 보고에 전문이 있다. 요약:

- **[ESCALATE] 레이트리밋 × Cloudflare Tunnel 배포**: mechanic-spec 이
  이미 약속한 배포 형태(cloudflared 가 localhost 로 접속)에서는 모든
  트래픽의 `request.client.host` 가 127.0.0.1 이라, 10회/시간이 전
  플레이어 공용 예산이 되어 redeem 이 사실상 불통이 된다. Ledger 는
  이 상황을 "무의미해진다"(방어 약화)로 적었는데 실제로는 가용성
  장애다. 다음 런(배포)에서 바로 터진다.
- **[NOTE] ×4**: 테스트 헬퍼 중복 2건(`_set_save_code` 사설 복사,
  App 컴포넌트 테스트 4개의 fetch 스텁 제각각), 다이얼로그 백드롭
  클릭이 in-flight 중에 `busy` 를 남기는 문제, mechanic-spec 2-Strike
  절의 낡은 "N/A" 노트.

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
