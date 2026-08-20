status: approved
# Plan: 난파섬 공개 배포 준비 — 신원/세션 정리 묶음

## Phase 1: 신원 게이트 — 남의 섬이 구조적으로 안 열린다

브라우저 플레이는 기존 그대로인 채, curl로 남의 세션 번호를 본문에
실어도 무시되고(쿠키 없인 401), 쿠키는 보안 속성 4종을 달고 나가며,
세션 번호는 서버만 민팅한다.

Contracts: B1, B2, B6, B7

- [x] B1·B2·B6·B7 계약 테스트 박제 — /turn 쿠키 신원(401·본문 무시·
      npc_id 404·응답 무 session_uuid), bootstrap 서버 전용 민팅 +
      0턴/503/banned 칸, 모든 Set-Cookie 속성 4종(기존 redeem 응답
      포함 — 발급 단일 경로라 이 페이즈에서 전 표면 커버), 해석기
      우회 박제. 변경되는 동작은 failing으로 시작.
- [ ] 세션 상수 단일 모듈 + 쿠키 속성 4종 적용 (B6 구현) — set_cookie
      단일 경로에 HttpOnly/Secure/SameSite=Lax/Max-Age 180일, Secure
      생략용 로컬 dev env 플래그(이름 재량), 테스트 환경 Secure 처리
      방침 확정 (Delegated 참조).
- [ ] 신원 해석기 + bootstrap 서버 전용 민팅 (B7·B2 구현) — 쿠키 파싱
      → UUID 검증 → 세션 존재 확인의 단일 공유 지점 (세션 생성 절대
      금지), bootstrap은 모르는 쿠키를 버리고 새 UUID 민팅.
- [ ] /turn 쿠키 단일 신원 전환 (B1 구현, Req 1–3·11·13) — 본문
      session_uuid 무시, 무신원 401(신원 판정이 npc_id 검증보다 먼저),
      npc_id 배선 목록 검증 404, 응답 본문 session_uuid 제거 (payload
      헬퍼 공유라 bootstrap/redeem 응답도 이 step에서 함께). 401 문구는
      rules YAML.

## Phase 2: 공개 표면 위생 — 세이브 코드 문단속 + 노출 차단

죽은/모르는 쿠키로는 세이브 코드가 발급되지 않고(빈 세션 민팅 폐지),
/assets/README.md 와 /docs 류 문서 URL이 404가 된다.

Contracts: B3, B4, B5

- [ ] B3·B4·B5 계약 테스트 박제 — 발급 게이트(모르는 쿠키 401·민팅
      금지·0턴 발급 OK·banned 200)는 failing으로, redeem은 기존 계약 +
      새 쿠키 속성 conformance, /assets 화이트리스트(실파일 기준·
      대소문자 무시·경로 탈출)는 failing으로.
- [ ] /save-code 발급 게이트 구현 (B3) + redeem conformance 확인 (B4 —
      rebind Set-Cookie가 Phase 1 단일 경로의 속성 4종을 받는지, 503
      rebind 금지·banned 무rebind 기존 유지).
- [ ] /assets 확장자 화이트리스트 구현 + FastAPI 자동 문서 엔드포인트
      (/docs·/redoc·/openapi.json) 비활성화 (B5, Req 9·12).

## Phase 3: 프론트 정합 + 스모크 + 기록

지인이 실제로 겪을 흐름 전체가 새 계약 위에서 끝-끝으로 돌고(재방문
복원, 기기 이동, 401 복구), 이번 런의 결정들이 ADR 감사 추적으로
남는다.

Contracts: (없음 — 기존 계약의 소비자 정합 + 문서화)

- [ ] 프론트 정합 (Req 10) — /turn 본문에서 session_uuid 제거, 응답
      본문 session_uuid 미의존화, 401 → 자동 재bootstrap 1회 + 실패 시
      솔직한 시스템 톤 오류 (무한 루프 금지). 하드코딩 게이트
      (frontend 스캔) 그린 유지.
- [ ] 스모크 시나리오 끝-끝 확인 — dev(백엔드 8765, vite 5173)로 첫
      방문→대화→재방문 복원→세이브 코드 발급→다른 브라우저 컨텍스트
      redeem→본문 위조 차단까지, manual-check.md 기록 + 게이트 3종
      그린 (Req 15).
- [ ] ADR 기록 (Req 14) — 신규: 쿠키 단일 신원+서버 전용 민팅, 쿠키
      보안 속성+bearer 의식적 수용, 공개 표면 위생(assets 화이트리스트
      +docs 비활성화). 백필: 세이브 코드 단어 프리픽스 형식, 180일
      쿠키. 레포 룰(ADR당 1커밋)에 따라 이 step은 커밋 여러 개.
      mechanic-spec 인프라 섹션에 신원 모델 갱신 (해당 시 mapping-spec
      정렬 확인).
