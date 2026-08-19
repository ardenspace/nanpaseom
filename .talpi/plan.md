status: approved
# Plan: 난파섬 프론트엔드 + 이어하기 (Phase 1.0 Sub-3)

## Phase 1: 브라우저 첫 플레이

이 페이즈가 끝나면: 브라우저에서 타이틀 → [시작하기] → 수리공이 먼저
말을 걸고 → 선택지 버튼으로 대화를 이어갈 수 있다.

Contracts: B1, B2, B4

- [x] 계약 테스트 pin (failing부터): B2 bootstrap — new(오프닝+비어있지
      않은 choices)/resumed/banned/error(503 형태)/0턴 재진입 재시도,
      비-error 응답의 session_uuid·npc_id 포함 — + B4 정적 서빙(200 +
      text/html) + B1 기존 /turn 스위트 그린 확인. stub llm, 결정적.
      (early-pull: resumed/banned UI는 Phase 2·차단 화면은 Phase 1 후반이지만
      B2의 전체 시맨틱은 여기서 백엔드에 랜딩한다)
- [x] backend: bootstrap endpoint 구현 — 세션 생성/쿠키 발급, 수리공
      오프닝 턴 생성(내부 구현 재량), 0턴 재시도·오류 시맨틱 → B2 테스트 그린
      (B4 정적 라우트도 조기 랜딩 — step 3는 와이어링 검증만)
- [ ] frontend scaffold: bun + Vite + React로 frontend/ 생성, 디자인 토큰
      파일 + tone 모듈(로컬 UI 시스템 문구 단일 홈), FastAPI 정적 서빙
      와이어링 + dev proxy (B4 그린), `check_no_hardcoded_dialogue.py`
      frontend/ 스캔 확장(tone 모듈만 예외)
- [ ] frontend 화면: 타이틀(“Still Here” + [시작하기]; 세이브 코드 입력은
      Phase 3 자리표시) + 채팅 화면 — 말풍선/선택지 버튼/kind=npc 빈
      choices→자유 입력 전환/warning·ban 시스템 톤 렌더 + ban 즉시 차단
      화면. 브라우저 첫 플레이 smoke.

## Phase 2: 닫았다 다시 와도 이어진다

이 페이즈가 끝나면: 브라우저를 닫고 재방문하면 최근 대화와 현재
선택지가 복원되고, 밴된 세션은 대화 대신 차단 화면을 본다.

Contracts: (없음 — Phase 1에 랜딩된 B2 시맨틱에 대한 frontend conformance)

- [ ] frontend 재방문 UX: 타이틀 이어하기 분기(쿠키 세션 존재 시),
      최근 N턴 transcript 렌더 + 선택지/자유입력 모드 복원, 밴 세션
      재방문 차단 화면 — B2 계약 대비 conformance 확인 포함, 재방문 smoke

## Phase 3: 세이브 코드로 다른 기기에서

이 페이즈가 끝나면: 게임 중 코드를 발급받아 다른 브라우저(기기)의
타이틀 화면에 입력하면 같은 대화를 이어할 수 있다.

Contracts: B3, B5

- [ ] 계약 테스트 pin (failing부터): B5 migration 003 — save_code 컬럼,
      기존 DB 무손실 — + B3 — 코드 형식/알파벳(한 곳 정의), 발급(세션
      쿠키 필수, 밴 세션 불가), redeem(세션 상태별 시맨틱, 성공 응답
      시에만 쿠키 재바인딩, 잘못된 코드 404/오프닝 실패 503, 밴 코드
      no-rebind)
- [ ] backend: migration 003 + 발급/redeem endpoint → B3/B5 테스트 그린
- [ ] frontend: 채팅 화면 세이브 코드 발급 UI + 타이틀 코드 입력 +
      기존 세션 대체 확인 다이얼로그(tone 모듈 문구) → 두 브라우저
      프로필로 크로스 디바이스 smoke
