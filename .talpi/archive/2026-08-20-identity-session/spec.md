status: approved
# Spec: 난파섬 공개 배포 준비 — 신원/세션 정리 묶음

## Product Picture

**누구를 위해**: 링크를 받은 지인 몇 명 — 잘 되면 커뮤니티 공개까지.
지금은 개발자 로컬 머신에서만 돌아서 이들은 플레이 자체를 못 한다.

**핵심 경험**: 같은 브라우저로 돌아오면 하루든 한 달이든 "아무것도 안
해도 내 섬이 그대로" 이어진다. 기기를 바꾸면 세이브 코드가 유일한 문.
절대 일어나면 안 되는 두 가지: 진행 유실, 남의 세션이 보이는 것.
(의식적으로 수용한 드문 예외들은 Reversibility Ledger 참조 — 서버 DB
유실 시 조용한 새 시작, redeem의 기존 세션 덮어쓰기.)

**스모크 시나리오**: 지인이 폰으로 링크 열고 → 수리공과 몇 턴 대화 →
탭 닫고 다음날 다시 열면 그대로 이어짐 → 세이브 코드로 다른 기기에서
같은 섬 복원 → 그 사이 다른 지인이 요청 본문에 어떤 세션 번호를 실어
보내도 남의 섬이 열리지 않음. (쿠키 값 자체는 bearer — Reversibility
Ledger의 의식적 수용 참조. 엔트로피+HttpOnly+Secure가 방어선.)

**이번 런의 끝**: 코드가 배포-준비 완료인 상태 (a). 신원/세션 구멍을
막아 아무 서버에나 올리면 되는 상태까지. 실제 배포(서버/도메인/HTTPS
셋업)는 다음 런.

## Requirements

각각 독립 검증 가능:

1. `POST /turn` 은 요청 본문에서 세션 신원을 받지 않는다 — 신원은
   쿠키에서만. 본문에 세션 번호 필드(구 `session_uuid` — 무시 계약
   테스트의 대상 필드)가 와도 **무시**된다 (거부 아님 — 신원에
   사용되지 않는 것이 계약).
   (from knowledge.md — 신원 소스 불일치 오픈 질문의 해소)
2. 쿠키가 없거나 서버가 모르는 세션이면 `POST /turn` 은 401로 거부하고
   세션을 만들지 않는다.
3. 유효한 쿠키 + 아는 세션이면 `POST /turn` 의 대화 동작은 기존과 동일
   (밴 게이트 → strike → run_turn 오케스트레이션 무변경).
4. 서버가 내보내는 모든 `Set-Cookie` 는 B6의 속성 세트를 따른다 (속성
   목록의 단일 권한은 B6). 로컬 개발 예외는 B6에 정의된 env 분기 하나뿐.
5. 세션 번호(UUID)는 **서버만 생성**한다. 서버가 모르는 UUID가 쿠키로
   와도 그 값이 세션 행이 되는 일은 없다.
6. `POST /save-code` 는 서버가 모르는 쿠키에 대해 401로 거부하고 세션을
   만들지 않는다. (from knowledge.md — 스테일 쿠키 민팅 오픈 질문의 해소)
7. `POST /save-code` 는 아는 비(非)밴 세션이면 0턴(대화 전)이라도
   코드를 발급한다 (기존 idempotent 재발급 유지). 밴 세션은 기존 동작
   유지 — 코드 없이 `{"status":"banned"}`.
8. 세션 행을 새로 만드는 경로는 `POST /session/bootstrap` 하나뿐이다.
9. `GET /assets/*` 는 확장자 화이트리스트 밖 파일에 404를 준다 —
   `README.md` 류 문서는 더 이상 공개 URL로 서빙되지 않고, 기존
   이미지/폰트/빌드 산출물 서빙은 유지된다. 경로 탈출(`../`)은 차단.
   (from knowledge.md — assets README 오픈 질문의 해소)
10. 프론트엔드는 `/turn` 본문에 세션 번호를 싣지 않고, 401을 받으면
    bootstrap을 다시 타서 이어간다. 자동 재bootstrap은 1회 — 그래도
    401이면 솔직한 시스템 톤 오류 표시 (무한 루프 금지). 스모크
    시나리오가 끝-끝으로 통과.
11. API 응답 본문은 세션 번호(`session_uuid`)를 싣지 않는다 — 프론트가
    더 이상 쓰지 않으므로 제거. bearer 값이 JS 가시 영역에 남지 않는
    것이 계약 (HttpOnly 방어선 유지 — 패널 재검증 지적의 해소).
12. FastAPI 자동 문서 엔드포인트(`/docs`, `/redoc`, `/openapi.json`)는
    비활성화한다 (정보 위생 — assets 화이트리스트와 같은 계열).
13. `POST /turn` 의 `npc_id` 는 아는 NPC 목록으로 검증 — 미지/불량
    값은 404, 파일 경로 결합에 도달하지 않는다 (현행: 무처리 500 +
    `../` 류 값이 경로가 됨).
14. 이번 런의 신규 락인 결정들 + 지난 런 백필 2건(세이브 코드 형식,
    180일 쿠키)이 `docs/adr/NNNN-*.md` 로 기록된다 (ADR당 1커밋).
    (from knowledge.md — ADR 오픈 질문의 해소)
15. 기존 게이트 전부 그린 유지: `.venv/bin/pytest`(결정적),
    `python3 scripts/check_yaml.py`,
    `python3 scripts/check_no_hardcoded_dialogue.py`.

## Out of Scope (v1)

- 실제 배포 행위 — 서버/도메인/HTTPS/프로세스 매니저 셋업 (다음 런)
- 계정/로그인 시스템 (영구 계정, 이메일 등)
- 레이트 리밋 (세이브 코드 무차별 대입 방어, 익명 세션 대량 민팅 방어
  포함 — Reversibility Ledger의 의식적 수용 항목 참조)
- 서명/회전 가능한 세션 토큰 (쿠키 값은 bearer UUID로 유지 — Ledger 참조)
- 대화 기록 보존기한/삭제 경로 (무기한 보존 의식적 수용 — Ledger 참조)
- ML 모더레이션, Cloudflare/failover (from knowledge.md — 기존 defer 유지)
- 나머지 NPC 3종, FastAPI 외 프론트/모바일
- warning 응답 시 서버가 이전 choices를 echo하는 계약 변경
  (from knowledge.md — 오픈 질문, 이번 런 아님)
- 캐릭터/배경 실이미지 드롭인 (from knowledge.md — 오픈 질문, 이번 런 아님)

## Simplicity Zones

- 신원은 끝까지 쿠키 하나 — 토큰 갱신, 다중 기기 동시 세션 관리,
  "내 기기 목록" 없음. 기기 이동은 세이브 코드가 전부.
- 단일 서버 전제 — 세션 저장소는 지금 Postgres 그대로, 분산/캐시 계층
  없음.
- 거부/실패 문구는 기존 "솔직한 시스템 톤" 재사용, 새 문구 체계 없음.
  (from knowledge.md — 기존 결정 유지)
- 어드민/운영 도구 없음 — 밴 해제·세션 조회는 사람이 DB 직접 쿼리.

## Boundary Contracts

이 게임의 개인정보 표면: 익명 세션 UUID에 묶인 사용자 입력 대화
텍스트가 전부다. 계정/이메일/실명 없음. DB 접속 정보는 env로만
(레포에 시크릿 없음). 아래 계약들이 그 대화 텍스트의 소유 경계다.

이번 런이 바꾸지 않는 기타 접점 (완전성 기록): `GET /` 는 index.html을
기존대로 서빙; llama-server(`LLAMA_SERVER_URL`·`NANPASEOM_MODEL` env)는
내부 LLM 접점으로 기존 계약 무변경 (bootstrap/redeem의 503은 이 접점의
실패 의미); `NANPASEOM_STATIC_DIR` env가 정적 루트를 결정 (기존
테스트가 pin); 프론트 localStorage 재방문 힌트는 표시용일 뿐 신원이
아니다. FastAPI 기본 422(본문 검증 실패)와 HTTPException detail 형태는
프레임워크 기본값 그대로 (오류 공통 형태 `{status:"error", message}` 는
이 스펙이 정의하는 401 등 앱 발신 오류에만 적용).

### B1: POST /turn — 쿠키 단일 신원

- 요청 본문: `{npc_id, player_input}` — 세션 번호 필드 없음. 본문에
  세션 번호류가 와도 무시되며 신원에 사용되지 않는다.
- 신원: 쿠키 `session_uuid` 만. 쿠키 없음 / UUID 형식 아님 / 서버가
  모르는 세션 → `401 {status:"error", message}` (솔직한 시스템 톤),
  세션 생성 없음. 401 message 문구의 서식지는 rules YAML (서버 발신
  메시지 하드코딩 금지 룰의 기존 패턴).
- `npc_id` 는 아는 NPC 목록 검증 → 미지/불량 값 404 (Req 13). "아는
  NPC" = 런타임에 배선된 NPC (현재 수리공 단독 — yaml 존재만으로는
  불충분). 신원 판정이 npc_id 검증보다 먼저 — 무인증 요청은 npc_id가
  뭐든 401 (미인증 npc 탐색 차단).
- 유효 신원일 때의 응답 계약(밴/strike/정상 턴)은 기존과 동일 —
  이번 런은 신원 게이트만 바꾼다. 단 응답 본문에서 `session_uuid` 는
  제거 (Req 11).

### B2: POST /session/bootstrap — 유일한 세션 생성 문, 서버만 민팅

- 유효 쿠키 + 아는 세션 → 복원(resumed). 밴 세션 → banned (기존 유지).
- 쿠키 없음 / 형식 불량 / **서버가 모르는 세션** → 클라이언트가 실어
  보낸 값은 버리고 서버가 새 UUID를 민팅 → 신규(new). 클라이언트가
  고른 값이 세션 행이 되는 일은 없다 (기존의 "스테일 쿠키 채택" 동작
  폐지 — 패널 지적으로 사람이 결정).
- 아는 세션 + 턴 0개(직전 오프닝 503 후 재시도 등) → 오프닝 (재)시도,
  status "new" (현행 유지 — resumed/new 두 칸 사이의 셋째 칸 명시).
- 오프닝 실패 503 → 민팅된 세션 행은 존속하고 `Set-Cookie` 도 심는다
  (현행 유지 — 다음 bootstrap이 위 "턴 0개" 칸으로 재시도). banned 칸
  포함 모든 status 응답에 `Set-Cookie` (현행 유지).
- 세션 행을 만드는 유일한 경로. 응답의 `Set-Cookie` 는 B6을 따른다.
  응답 본문에 `session_uuid` 없음 (Req 11).

### B3: POST /save-code — 발급은 아는 세션에만

- 쿠키 없음 → 401. 쿠키는 있으나 서버가 모르는 세션 → 401, 세션 생성
  없음 (기존의 "빈 세션 민팅 후 발급" 동작 폐지).
- 아는 비밴 세션 → 코드 발급. 0턴 세션도 OK. 재요청은 기존 코드 반환
  (idempotent, 기존 유지). 밴 세션 → 코드 없이 HTTP 200
  `{"status":"banned"}` (기존 유지 — 밴은 fatal이되 오류가 아닌 상태).

### B4: POST /save-code/redeem — 기존 계약 유지 + 새 쿠키 속성

- 본문 `{code}`. unknown/malformed → 404 (기존). 성공 시 쿠키 재바인딩
  `Set-Cookie` 는 B6을 따른다. rebind는 new/resumed에만, 503엔 금지,
  밴 세션은 rebind 없이 banned (기존 유지).
- 무차별 대입 방어는 이번 런에 없음 — Reversibility Ledger의 의식적
  수용 항목.

### B5: GET /assets/* — 확장자 화이트리스트

- 허용: 이미지(`png jpg jpeg webp gif svg ico`), 폰트(`woff woff2`),
  빌드 산출물(`js css map`). 그 외 확장자·무확장자 → 404.
- 경로 탈출: 해석된 실경로가 assets 루트 밖이면 404 (기존 방어 유지,
  계약으로 명시). 확장자 판정도 resolve된 실파일 기준 + 대소문자 무시
  (요청 문자열 기준 판정의 우회 여지 차단).
- 빌드 산출물에 실제로 필요한 확장자가 더 있으면 화이트리스트 확장은
  빌더 재량 (문서류 `md txt` 류가 새지 않는 것이 계약의 핵심).
- svg는 액티브 콘텐츠(스크립트 실행 가능) — 현재는 빌드 산출물뿐이라
  허용하되, 외부 제작 실이미지 드롭인 시 재검토 딱지.

### B6: 세션 쿠키 계약 (속성의 단일 권한)

- 이름 `session_uuid`, 값은 서버가 민팅한 UUID 문자열.
- 속성: `HttpOnly; Secure; SameSite=Lax; Max-Age=15552000(180일);
  Path=/`.
- 로컬 개발 예외는 하나: env 플래그(이름은 빌더 재량)가 켜진 경우에만
  `Secure` 를 생략. 기본값(플래그 없음)은 항상 Secure — 배포 환경에서
  플래그를 켜지 않는 한 Req 4가 무조건 성립.
- 프론트 JS는 쿠키를 읽지 않는다 — 상태(status/npc_id/history 등)는
  bootstrap/redeem 응답 본문으로 받되, 자격증명인 `session_uuid` 는
  어떤 응답 본문에도 싣지 않는다 (Req 11).

### B7: 신원 해석 이음새 (내부 경화 — 인터뷰에서 사람이 지정)

- 쿠키 인증이 필요한 엔드포인트(/turn, /save-code)의 신원 판정(쿠키
  파싱 → UUID 검증 → 세션 존재 확인 → 통과/거부)은 단일 공유 지점을
  통과한다. 이 지점은 절대 세션을 만들지 않는다 (민팅은 bootstrap 소관).
- 계약 테스트로 박제한다. 박제 테스트의 구체 형태와 공유 지점의
  위치/이름/시그니처는 빌더 재량 (Delegated 참조).

## Reversibility Ledger

### Decided (hard to change)

- 신원 모델 = 쿠키 단일 소스. 계정/로그인 없음, 기기 이동은 세이브
  코드만.
- 쿠키 값 = 서명 없는 bearer UUID (패널 `[BLOCKING]` 지적을 사람이
  검토 후 의식적 수용): 값을 아는 자가 곧 주인이며, 방어선은 UUID
  엔트로피 + HttpOnly + Secure 세 겹이 전부. 서명/회전 토큰은 도입하지
  않음. **커뮤 공개 전 재검토.**
- 세션 번호는 서버만 생성 — bootstrap이 클라이언트 지정 UUID를 세션
  행으로 채택하던 기존 동작 폐지 (패널 지적으로 사람이 결정).
- `POST /turn` 요청 본문에서 세션 번호 제거 — API 파괴적 변경, 프론트
  동시 수정으로 흡수.
- 세션 생성 문은 bootstrap 하나뿐.
- 쿠키 속성 4종: HttpOnly / Secure / SameSite=Lax / Max-Age 180일.
  SameSite=Lax + 쿠키 단일 신원은 "프론트와 API가 same-origin"이라는
  배포 형태를 함의 (별도 CDN 도메인에서 API를 부르는 구조는 이 결정과
  함께 재검토 대상).
- 세이브 코드 무차별 대입 = 의식적 수용. 유출 시 코드 무효화/회전
  경로가 없다는 점(idempotent 영구 자격증명)도 함께 수용. **커뮤 공개
  전 재검토.** (레이트 리밋 아웃 결정과 함께 사람이 내린 결정)
- 익명 세션 대량 민팅(bootstrap은 무인증 + LLM 오프닝 비용) = 레이트
  리밋 아웃 결정에 포함된 의식적 수용. 파생 두 갈래도 함께 수용:
  (1) 0턴 코드 발급과 결합하면 유효 세이브 코드 모집단을 부풀릴 수
  있음, (2) 밴이 세션 단위라 쿠키 삭제 + 재bootstrap으로 밴 우회 가능
  (2-strike는 새 세션에서 다시 작동). **커뮤 공개 전 재검토.**
- 대화 기록 무기한 보존, 플레이어 측 삭제 경로 없음 = 의식적 수용
  (패널 `[BLOCKING]` 지적을 사람이 검토 후 결정). 보존기한/삭제는
  **커뮤 공개 전 재검토.**
- ADR 기록: 이번 런 신규 결정들 + 백필 2건(세이브 코드 단어 프리픽스
  형식, 180일 쿠키). (from knowledge.md — 오픈 질문의 해소)
- 조용한 덮어쓰기 = 의식적 수용 (패널 재검증 `[BLOCKING]` 을 사람이
  검토 후 결정): 서버가 세션을 모르면 bootstrap이 묻지 않고 새 번호로
  쿠키를 덮는다 (대화 중 401 → 자동 재bootstrap 경로 포함 — redeem의
  확인 다이얼로그와 달리 무확인). 발생 조건이 서버 DB 유실/복구뿐이라
  극히 드물고,
  그 경우 진짜 복구 열쇠는 세이브 코드 — "쿠키는 편의, 코드가 열쇠".
  묻고-리셋 UI는 도입하지 않음.
- 본문 세션 필드는 "거부"가 아닌 "무시" (Req 1) — 나중에 reject로
  조이는 것이 파괴적 변경이 되는 관용 락인임을 알고 선택.
- redeem 성공 시 쿠키 재바인딩은 redeem한 기기의 기존 세션 자격증명을
  덮는다 (기존 계약) — 그 섬은 세이브 코드를 미리 받아뒀을 때만 복구
  가능. 의식적 수용.
- /assets의 `svg`(액티브 콘텐츠)·`map`(소스맵 전체 공개) 허용 = 의식적
  수용 (개인 프로젝트, 현재 산출물은 자체 빌드뿐). 외부 제작 이미지
  드롭인 시 svg 재검토.
- 상속 유지 (from knowledge.md): 스택 React+Vite+bun, 세이브 코드 형식
  (단어 프리픽스+랜덤 4자), 자유 입력 해제 awareness 85+, 복원은 최근
  N턴만, 인프라 실패 문구는 솔직한 시스템 톤.
- "쿠키 미검증 = UUID가 사실상 bearer" (from knowledge.md): 이번 런은
  이 중 "미검증"(본문 신원, 스테일 쿠키 채택)을 해소한다. "bearer"
  자체는 위의 의식적 수용으로 존속 — 완전한 졸업이 아님을 명시.

### Delegated (agent's discretion)

- 신원 해석 지점의 위치/이름/시그니처 (FastAPI dependency든 헬퍼든),
  그리고 B7 박제 테스트의 구체 형태. bootstrap의 쿠키 파싱이 같은
  지점의 파싱 단계를 공유할지(세션 존재 확인 없이)도 빌더 재량.
- 테스트 환경에서의 Secure 쿠키 처리 (http TestClient의 쿠키 재전송
  문제 — env 플래그 사용이든 헤더 직접 단언이든 게이트가 그린이면 됨).
- 401 응답의 세부 형태 — `{status:"error", message}` 틀 안에서.
- 프론트 api.ts 수정 방식, 401 → 재bootstrap 흐름의 구현.
- 테스트 헬퍼 중복 정리 — _raising_llm / set-cookie 파서의 conftest
  추출 여부. (from knowledge.md — 오픈 질문의 위임 처리)
- Secure 생략용 로컬 개발 env 플래그의 이름.
- ADR 문서의 문구/번호 배정.
- /assets 화이트리스트의 정확한 최종 확장자 목록 (B5 취지 안에서).

## Conventions

지난 런 conventions.md 베이스라인 상속 (사람 승인):

- 반복 리터럴은 한 홈에 — frontend는 디자인 토큰 파일, Python은 상수
  모듈. 두 곳에 인라인 금지.
- 두 번 나온 로직은 공유 계층으로 추출, conventions.md에 등록.
- 사용자 노출 실패 문구는 한 톤, 한 곳 (frontend tone 모듈).
- ~300줄 넘으면 분리 리뷰 (하드 리밋 아님, 유지 사유 기록 가능).

레포 룰 승격 (CLAUDE.md 병행 유효): 새 락인 결정은 ADR 후 spec/YAML
갱신; NPC 대사/서버 발신 안전 메시지 하드코딩 금지 (frontend 포함,
tone 모듈 단일 예외); YAML 변경 시 check_yaml; git은 logical unit per
commit + 한국어 커밋 메시지에 결정 이유 + `--no-verify`/`--no-gpg-sign`
금지; pytest 게이트는 결정적(stub llm), `-m live` 는 off-gate.

이번 런 추가: 쿠키 이름/속성/Max-Age 등 세션 상수는 한 모듈에 모은다
(리터럴 단일 홈 룰의 적용 사례 — 이 문장이 이 규칙의 유일한 서식지).

기존 공유 유틸 재사용: `tests/api/conftest.py` (client fixture),
`frontend/src/api.ts` (postJson), 오류 공통 형태
`{status:"error", message}` + 시스템 톤 렌더, fatal(밴)/recoverable
구분 — 401은 recoverable로, 재bootstrap 후 대화를 이어간다. 신규
세션으로 시작되는 경우는 쿠키가 사라졌거나 서버가 그 세션을 더 이상
모를 때이며(예: DB 초기화), 이때 localStorage 재방문 힌트가 남아
있어도 힌트는 표시용일 뿐 세션 복원을 약속하지 않는다.

dev 포트 규약 유지: backend dev 8765(uvicorn), frontend dev 5173(vite,
proxy → 8765). 8080(llama-server)/8000/8081/5433/5000/7000 회피.
