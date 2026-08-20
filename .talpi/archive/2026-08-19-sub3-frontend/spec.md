status: approved
# Spec: 난파섬 프론트엔드 + 이어하기 (Phase 1.0 Sub-3)

## Product Picture

**누구를 위해:** 디자이너 본인(Arden)이 첫 플레이어. 지금은 curl/pytest로만
수리공과 대화할 수 있다 — 개발자 모자를 벗고 플레이어로 앉아볼 방법이 없다.

**핵심 경험:** 몰입. 수리공과의 대화가 자연스럽게 흘러가고, awareness가
오르면서 변해가는 진행감이 UI로 체감된다 (선택지 3→2→1→0 축소 —
기존 mechanic-spec band 매핑 그대로, 메커니즘 변경 없음).

**Smoke 시나리오:** 브라우저를 열고 → 타이틀 화면에서 [시작하기] →
수리공이 먼저 말을 걸어온다 (서버 생성 오프닝) → 선택지 버튼으로 여러 턴
주고받으며 태도 변화를 알아챈다 → 브라우저를 닫고 → 나중에 다시 오면
쿠키로 이어진다 (최근 턴 + 현재 선택지 복원) → 세이브 코드를 발급받아
다른 기기에서 입력하면 같은 대화가 이어진다.

## Requirements

각각 독립적으로 검증 가능:

1. 타이틀 화면: [시작하기] + [세이브 코드 입력]. 쿠키에 기존 세션이 있으면
   이어하기로 진입.
2. 채팅 화면: 수리공 대사 + 응답의 `choices`를 버튼으로 렌더.
   자유 입력 모드 판정은 **`kind: "npc"` 응답의 `choices`에만** 기반한다
   (비면 자유 입력 — awareness 85+ band, 기존 spec). warning/ban 응답의
   빈 `choices`는 UI 모드를 바꾸지 않는다 — warning 후에는 직전 npc 응답의
   선택지가 유지된다.
3. 첫 진입: 서버가 수리공의 첫 대사 + 선택지를 자동 생성해서 보여준다
   (플레이어가 먼저 입력하지 않음).
4. 재방문 복원: 쿠키 기반으로 최근 N턴 대화 + 현재 선택지가 복원된다
   (전체 스크롤백 아님 — 의식적 결정).
5. 세이브 코드: 게임 중 발급 가능, 타이틀 화면에서 입력하면 그 세션으로
   쿠키가 재바인딩되어 다른 기기에서 이어하기 가능. 입력하는 기기에
   기존 진행 세션이 있으면 재바인딩 전 확인 다이얼로그를 띄운다
   ("이 기기의 진행이 대체됩니다" 취지 — 문구는 시스템 톤 모듈).
6. warning/ban 응답은 수리공 말풍선과 구분되는 시스템 톤으로 렌더.
   `kind: "ban"` 응답을 받은 즉시 차단 화면으로 전환 (이전 선택지 비활성).
   밴된 세션으로 재방문해도 대화 대신 차단 화면.
7. 프론트는 React + Vite (bun). 빌드 산출물은 FastAPI가 정적 서빙,
   dev는 Vite dev 서버.
8. 디자인 테마: 딥블루 · 모래 · 녹슨 철 · 어둑한 바다 · 몽환적.
9. 인프라 실패(서버/네트워크 다운) 문구는 솔직한 시스템 톤, 한 곳에서 정의.
10. 기존 pytest 게이트 전부 그린 유지 + 신규 boundary 계약마다 테스트.

## Out of Scope (v1)

- 나머지 3 NPC (어부/할머니/혜안) 활성화
- tap-to-talk 섬 풍경 화면 (4 NPC 씬), ambient mutter
- sprite state A/B 전환 (캐릭터 이미지는 NPC당 1장 고정)
- 엔딩 연출 (85+ 엔딩 게이트 발동, 보트 엔딩), 엔딩 저널, 다회차(새 회차/전체 초기화)
- ESC 메뉴 풀 구성 (사운드 등) — 세이브 코드 발급 진입점만 있으면 됨
- ML 모더레이션 checker, 4k budget cap 하드닝
- Cloudflare Tunnel / failover / 공개 배포 (이번 런은 로컬 실행만)
- 3D (React 선택의 장기 이유일 뿐, 이번 런과 무관)

## Simplicity Zones

- 화면은 사실상 2개 (타이틀 / 채팅) — 라우터·상태관리 라이브러리 없이
  React 기본 상태로 충분
- 캐릭터/배경 이미지는 플레이스홀더로 시작 (CSS 그라디언트 등).
  실제 이미지는 디자이너가 나중에 제공 — `frontend/public/assets/` 하위
  고정 파일명에 덮어쓰면 반영되는 드롭인 계약 (파일명 규약은
  conventions.md에 기록)
- 세이브 코드는 v1 plain 저장 (mechanic-spec 락인), 로테이션/무효화 없음
- 쿠키 외 인증 없음, 계정/로그인 없음
- 프론트 로직은 얇게 — 계약 검증은 pytest(API 레벨)가 담당, 프론트 자체
  테스트는 최소한

## Boundary Contracts

### B1: POST /turn (기존 — 무변경)

요청 `{session_uuid?: str, npc_id: str, player_input: str}` →
응답 `{kind: "npc"|"warning"|"ban", reply: str, choices: [{tone, text}],
session_uuid: str, matched_term?: str}`.
이번 런에서 이 계약은 변경하지 않는다. 기존 테스트 전부 그린 유지가 회귀 계약.
프론트는 bootstrap에서 받은 session_uuid를 명시적으로 실어 보낸다.
/turn이 쿠키를 검증하지 않는 것(body UUID = bearer)은 Reversibility Ledger의
의식적 수용 항목 — 공개 배포 전 필수 재방문.

### B2: 세션 bootstrap (신규)

쿠키가 신원. 정확한 URL/필드명은 Delegated이되, 계약은:

- 쿠키 없음/미지의 세션 → 서버가 세션 생성 + 쿠키 발급(속성은 Delegated) +
  수리공 오프닝 턴 생성. 응답 `status: new`, 오프닝 대사와 비어있지 않은
  choices 포함.
- 오프닝 생성 실패 시: HTTP 503 + `{status: "error", message}` (message는
  시스템 톤, 대화 데이터/choices 미포함). 턴이 0개인 세션은 재진입 시
  신규와 동일하게 취급 — 같은 세션/쿠키를 재사용해 오프닝을 다시 시도한다.
  "0턴인데 resumed" 상태는 계약상 존재하지 않는다.
- 유효한 쿠키 + 턴 ≥ 1 → `status: resumed`. 최근 N턴 `[{role, content}]` +
  마지막 npc 응답의 choices (비어 있으면 자유 입력 모드) 포함.
- 밴된 세션 → `status: banned` + ban_reason. 대화 데이터 미포함.
- `status`가 error가 아닌 모든 응답(new/resumed/banned)은 `session_uuid`를
  포함한다 — B1의 /turn 호출이 이 값을 사용한다. npc_id는 이번 런에서
  수리공 고정이며 서버가 결정한다 (응답에 `npc_id` 포함).
- 크로스 라인: session_uuid(쿠키), 대화 텍스트(개인 자유 입력 포함 가능),
  선택지. 비밀/외부 서비스 없음 (LLM은 로컬 llama-server).

### B3: 세이브 코드 발급/입력 (신규)

- 코드 형식: 9자 `XXXX-XXXX` (하이픈 포함 — `VARCHAR(9)`와 일치).
  알파벳 = A-Z·2-9에서 혼동 문자(O/I/L/0/1) 제외. 발급과 검증이 같은
  알파벳 정의 한 곳을 참조한다. PREFIX 단어 목록은 Delegated.
- 발급: 유효한 세션 쿠키 필수 — 없으면 오류 (세션 생성 없음). 밴된
  세션은 발급 불가 (banned 응답). 성공 시 `sessions.save_code`(UNIQUE)에
  민팅, 응답에 코드 문자열.
- 입력(redeem): 코드 제출 → 대상 세션 상태에 따라 B2 bootstrap과 동일한
  시맨틱 — 턴 ≥ 1 → resumed, 턴 0개 → 신규와 동일 (오프닝 생성, status: new).
- 쿠키 재바인딩은 **성공 응답(new/resumed)과 함께만 커밋**된다. 실패 시
  (잘못된 코드, 오프닝 생성 실패 등) 쿠키·기존 세션은 변경되지 않는다.
  밴된 세션의 코드 → banned 응답 + 재바인딩 없음 (살아있는 세션을 죽은
  세션과 바꾸지 않는다). 오류 형태는 B2와 동일한 `{status: "error",
  message}` (잘못된 코드 404, 오프닝 생성 실패 503).
- 재바인딩으로 기기의 기존 세션이 대체되는 것은 UI 확인 다이얼로그를
  거친다 (Requirements 5 — 조용한 세션 상실 방지, 패널 지적 반영).
- 코드 = bearer 열쇠: 코드를 아는 사람은 그 세션 대화 전체에 접근 가능.
  v1 의식적 수용 (mechanic-spec 락인, 로테이션은 v1.1). 밴 세션 코드의
  redeem 불가가 mechanic-spec "Strike 2 = 세이브 코드 무효화"를 충족하는
  이번 런의 형태다 (별도 무효화 메커니즘 없음).

### B4: 정적 서빙 + dev 구성 (신규)

- 프로덕션 모드: FastAPI가 Vite 빌드 산출물 서빙 — `GET /` → 게임 로드.
- dev 모드: Vite dev 서버 → 백엔드 프록시. 백엔드/프론트 dev 포트는
  이 머신 점유 포트 회피 (8080=llama-server, 8000, 8081, 5433, 5000, 7000 등).
- 계약: 빌드된 프론트가 API와 same-origin으로 동작 (쿠키가 자연히 흐름).

### B5: DB migration 003 (신규)

- `sessions.save_code VARCHAR(9) UNIQUE NULL` 추가.
- 기존 데이터가 있는 DB에 무손실 적용. 기존 migration 001/002 불변.
- choices 복원은 신규 컬럼/테이블 없이 기존 스키마로 가능해야 한다
  (어떤 컬럼을 읽을지는 내부 구현 — 계약은 침묵).

### 강화 seam: 프론트는 서버 데이터만 렌더

프론트 코드에 NPC 대사/서버 발신 안전 메시지(warning/ban 문구) 문자열 금지 —
전부 서버(→ rules/npcs YAML)에서 온다. 예외는 **프론트 로컬 UI 시스템 문구**
하나의 범주뿐: 서버 왕복 없이 떠야 하는 문구(인프라 실패 문구, 세이브 코드
입력 확인 다이얼로그 등)로, 전부 프론트의 단일 tone 모듈 한 곳에 정의한다.
이 범주는 NPC 대사가 아니므로 하드코딩 금지 룰과 충돌하지 않는다.

## Reversibility Ledger

### Decided (hard to change)

- 스택: React + Vite, 패키지 매니저 bun (3D 확장 대비 — 사용자 결정)
- 프론트 위치: 같은 레포 `frontend/` 디렉토리 (모노레포)
- identity: 쿠키 = session_uuid, 계정/로그인 없음 (mechanic-spec 기존 설계)
- 세이브 코드: 9자 PREFIX-XXXX, 혼동 문자 제외, v1 plain 저장 (mechanic-spec 기존 설계).
  PREFIX = 가독 단어(허용 알파벳 내 4자 단어 목록) + 랜덤 4자 — `MAST-7X2K` 류
  (패널/검증자 에스컬레이션, 인간 재판정 2026-08-19: 완전 랜덤 아님)
- 스키마: migration 003 = `sessions.save_code`만 추가. choices 복원용
  신규 컬럼/테이블 없음 (읽기 경로는 Delegated)
- 신원 모델 (패널 BLOCKING → 인간 의식적 수용): 이번 런의 /turn은 body
  `session_uuid`를 그대로 신뢰한다 (쿠키 미검증 = UUID가 사실상 bearer).
  로컬 전용 런이므로 수용하되, **공개 배포(Cloudflare) 전 필수 해결** —
  그 시점에 /turn 쿠키 검증(또는 쿠키-온리 전환)을 결정한다.
- 공개 배포 전 재방문 묶음 (패널 NOTE 승격, 로컬 전용이라 의식적 수용):
  세이브 코드 무차별 대입 대비 레이트리밋/키공간, redeem CSRF/SameSite
  자세, 쿠키 없는 방문의 무제한 세션+LLM 민팅 (비용/어뷰즈).
- 쿠키 상실(만료/삭제) 시 코드 미발급 세션은 영구 상실 — 계정 없음 설계의
  의식적 귀결 (복구 수단 없음).
- 세이브 코드 입력의 기존 세션 대체: UI 확인 다이얼로그로 완화하고 수용
  (세션 목록/undo는 만들지 않음 — 패널 지적, 인간 결정)
- 자유 입력 해제: awareness 85+ (기존 spec 유지 — "85가 더 극적" 사용자 재확인)
- 오프닝: 첫 진입 시 서버가 수리공 첫 턴 자동 생성 (사용자 선택 b —
  "누군가 있다" 느낌)
- 복원: 최근 N턴만, 전체 스크롤백 없음 (개인 프로젝트 트레이드오프 의식적 수용)
- 인프라 실패 문구: 솔직한 시스템 톤 (diegetic 거부 이유: "인물이 대사하는 것
  같으면 세계관 붕괴" — 사용자). 백엔드 Layer 4의 diegetic_fallback은 기존대로.
- 배포: 이번 런은 로컬 실행만

### Delegated (agent's discretion)

- 컴포넌트 구조, 애니메이션/스타일 구현 디테일 (상태 관리는 Simplicity
  Zones가 소유 — 라이브러리 없이 React 기본 상태)
- 복원 턴 수 N, 쿠키 속성(수명/HttpOnly 등), dev 포트 선택, CORS 구성
- bootstrap/세이브 코드 endpoint의 정확한 URL·필드명 (계약 테스트로 고정)
- 오프닝 턴 생성 방식 (기존 run_turn 재사용 여부 등 내부 구현)
- 세이브 코드 발급 버튼의 UI 위치, 재발급 시 동작(기존 코드 반환 vs 재민팅)
- 플레이스홀더 비주얼 구현

## Conventions

베이스라인 (사용자 승인):

1. 반복 리터럴(색/간격/경로/매직넘버)은 한 곳에 — 프론트는 디자인 토큰
   파일, 파이썬은 상수 모듈
2. 두 번 나오는 로직은 공유 레이어로 추출 + conventions.md 등록
3. 사용자에게 보이는 실패 문구는 한 톤, 한 곳에서 정의
4. 파일 ~300줄 초과 시 분리 리뷰 (하드 리밋 아님, 유지 사유 기록 가능)

레포 기존 룰 승격 (CLAUDE.md — talpi 파이프라인과 병행 유효):

- 권한 경계: 같은 사실은 한 spec 문서에만. 메커니즘 변경 시
  mechanic-spec + mapping-spec 둘 다 갱신 (이번 런은 메커니즘 무변경)
- 새 락인 결정은 ADR (`docs/adr/NNNN-*.md`, 시퀀셜) 후 spec/YAML 갱신
- NPC 대사/시스템 메시지 하드코딩 금지 — 프론트엔드에도 확장 적용.
  `scripts/check_no_hardcoded_dialogue.py`를 `frontend/` 스캔까지 확장한다
  (tone 모듈 한 곳만 허용 예외)
- YAML 변경 시 `python3 scripts/check_yaml.py`
- git: logical unit per commit, 한국어 커밋 메시지에 결정 이유 명시,
  `--no-verify`/`--no-gpg-sign` 금지
- 테스트: `.venv/bin/pytest` 게이트(결정적, stub llm) + `-m live`는 off-gate

디자인 테마: 딥블루 · 모래 · 녹슨 철 · 어둑한 바다 · 몽환적인 톤.
토큰 파일에서만 색/간격을 가져온다.

실패 문구 톤: 인프라 실패는 솔직한 시스템 톤 ("서버에 연결할 수 없습니다"
류), 프론트 단일 모듈에 정의. NPC를 흉내내지 않는다.

도구: 프론트 패키지 설치/실행은 bun. 스크립트는 frontend/package.json.
