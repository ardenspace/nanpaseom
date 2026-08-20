# ADR 0035: 공개 표면 위생 — assets 화이트리스트 / 자동 문서 봉인 / npc_id 검증

- Status: Accepted
- Date: 2026-08-20
- Deciders: Arden, Claude (공개 배포 준비 talpi 런)

## Context

아무 서버에나 올리면 되는 상태(배포-준비 완료)가 이번 런의 끝인데,
공개 URL 표면에 위생 구멍 셋이 있었다:

1. `frontend/public/assets/README.md` 가 빌드에 복사되어
   `/assets/README.md` 로 공개 서빙됨 (knowledge.md 오픈 질문) —
   `/assets` 가 확장자 무관 파일 서버였다.
2. FastAPI 자동 문서(`/docs`, `/redoc`, `/openapi.json`)가 열려 있어
   전체 API 스키마가 공개 노출.
3. `POST /turn` 의 `npc_id` 가 무검증 — 미지 값은 무처리 500, `../`
   류 값이 파일 경로 결합에 도달.

## Decision

1. **`GET /assets/*` 확장자 화이트리스트**: 이미지(`png jpg jpeg webp
   gif svg ico`) + 폰트(`woff woff2`) + 빌드 산출물(`js css map`)만
   서빙, 그 외 확장자·무확장자(문서류 `md`/`txt` 포함)는 실파일이
   있어도 404. 판정은 **resolve된 실파일 suffix 기준 + 소문자
   정규화** — 요청 문자열 기준 판정의 심링크/대소문자 우회 여지 차단.
   경로 탈출(`../`)은 resolve 실경로가 assets 루트 밖이면 404 (기존
   방어를 계약으로 명시). `svg`(액티브 콘텐츠)·`map`(소스맵 전체
   공개) 허용은 의식적 수용 — 현재 산출물이 전부 자체 빌드뿐. 외부
   제작 실이미지 드롭인 시 svg 재검토.
2. **FastAPI 자동 문서 비활성화**: `docs_url=None, redoc_url=None,
   openapi_url=None`. 공개 API가 아니라 게임 클라이언트 전용
   백엔드 — 스키마 공개는 정보 위생상 손해만 있다 (assets
   화이트리스트와 같은 계열).
3. **`npc_id` 배선 목록 검증**: `/turn` 의 npc_id는 런타임에 배선된
   NPC 목록(`WIRED_NPC_IDS`, 현재 수리공 단독 — yaml 존재만으로는
   불충분)으로 검증, 미지/불량 값은 404 — 파일 경로 결합에 도달하지
   않는다. 신원 판정(401)이 npc_id 검증(404)보다 먼저 — 무인증
   요청의 npc 탐색 차단.
4. **401/404 문구는 `rules/identity.yaml`**: 사용자 노출 시스템
   문구는 코드 아닌 YAML (서버 발신 메시지 하드코딩 금지 룰의 기존
   패턴 — 튜닝은 YAML 수정).

## Alternatives Considered

- A. ★ chosen — 화이트리스트 + 문서 봉인 + 배선 목록 404.
- B. 블랙리스트(`md txt` 만 차단) — 기각. 앞으로 추가될 파일 종류를
  예측해야 하는 구조 — 새는 쪽으로 기본값이 열려 있다. 화이트리스트는
  빌드 산출물에 확장자가 늘면 명시적으로 추가 (그게 계약의 핵심:
  문서류가 안 샌다).
- C. README.md를 빌드에서 제외 (그 파일만 처리) — 기각. 증상 하나만
  고치고 `/assets` 가 만능 파일 서버인 구조는 남는다.
- D. npc_id를 422(검증 오류)로 — 기각. 존재 여부를 묻는 값엔 404가
  의미상 정확하고, 미지 npc 열거에 스키마 힌트를 덜 준다.

## Consequences

- 화이트리스트 확장은 빌더 재량 (실제 빌드 산출물 기준) — 단 문서류가
  새지 않는 것이 계약, 테스트로 박제.
- `/openapi.json` 봉인으로 API 탐색은 소스(공개 레포) 기준 — 스키마
  자동 노출과 소스 공개는 별개 결정.

## Related

- ADR 0033 (신원 401이 npc 404보다 먼저 — 판정 순서의 근거), 0034
  (같은 런의 표면 하드닝 계열).
