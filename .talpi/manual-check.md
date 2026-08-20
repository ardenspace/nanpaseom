# 사람 눈 확인 체크리스트 — 세션/세이브코드 슬라이스 (Phase 3)

브라우저 UX 눈 확인용. 코드 안 읽고 이 문서만 보고 걸을 수 있게 작성.
걷는 사람: 아덴. 예상 소요: 10–15분 (LLM 턴당 수십 초 걸릴 수 있음).

## 0. 준비 (터미널)

```bash
cd /Users/arden/code/nanpaseom
docker compose up -d db          # postgres (이미 떠 있으면 no-op)
# llama-server 는 8080 에 이미 떠 있어야 함 (건드리지 말 것)
cd frontend && bun run build && cd ..
NANPASEOM_INSECURE_COOKIE=1 NANPASEOM_STATIC_DIR=frontend/dist \
  .venv/bin/uvicorn app.api.main:app --port 8765
```

- `NANPASEOM_INSECURE_COOKIE=1` 은 http 로컬용 — Secure 플래그를 끈다.
  배포 기본은 Secure 켜짐 (계약 테스트가 pin). 로컬에서 이 플래그 없이 http 로 열면
  브라우저가 쿠키를 재전송하지 않아 매번 새 세션이 되는 게 "정상 오동작"이니 헷갈리지 말 것.

## 1. 첫 방문 → 대화

- [ ] 브라우저에서 http://localhost:8765 열기 → 게임 타이틀/오프닝 화면이 뜬다 (빈 페이지/에러 아님)
- [ ] 수리공의 오프닝 대사 + 선택지 3개(공감/도발/딴청 톤)가 보인다 (오프닝 생성에 수십 초 걸릴 수 있음)
- [ ] 선택지 클릭 또는 자유 입력으로 2–3턴 대화 → 매 턴 수리공 응답이 돌아온다

## 2. 쿠키 속성 (개발자도구)

- [ ] 개발자도구 → Application → Cookies → http://localhost:8765 에 `session_uuid` 쿠키가 있다
- [ ] HttpOnly 체크 표시 있음, SameSite = Lax, Max-Age/Expires ≈ 180일 뒤
- [ ] Secure 는 **없음이 정상** (INSECURE_COOKIE=1 로컬이라서. 배포 기본은 켜짐)

## 3. 세션 번호 비노출 (개발자도구 Network)

- [ ] Network 탭 열고 메시지 하나 전송 → `/turn` 요청 클릭
- [ ] Request Payload 에 `npc_id` 와 `player_input` 뿐 — 세션 번호(UUID) 필드 없음
- [ ] Response 본문에도 `session_uuid` 없음 (`kind`/`reply`/`choices` 뿐)
- [ ] 신원은 요청 헤더의 Cookie 로만 오간다

## 4. 재방문 복원 (탭 닫고 다시)

- [ ] 탭을 완전히 닫는다 → 새 탭으로 http://localhost:8765 다시 열기
- [ ] 새 오프닝이 아니라 **직전 대화 히스토리가 그대로** 이어진다 (내가 보낸 말 포함)
- [ ] 마지막 선택지도 복원된다

## 5. 세이브 코드 → 다른 기기 복원

- [ ] 화면의 세이브 코드 UI 로 코드 발급 → `단어-4자` 형태 코드가 보인다 (예: `EAST-V5RN`)
- [ ] 같은 코드를 다시 발급해도 **같은 코드** (재발급이 코드를 갈아치우지 않음)
- [ ] **시크릿 창**(= 다른 기기 시뮬)에서 http://localhost:8765 열기 → 새 오프닝이 뜸 (다른 섬)
- [ ] 시크릿 창에서 세이브 코드 입력(redeem) → 확인 다이얼로그 → **원래 창의 대화가 그대로** 복원된다
- [ ] 이후 시크릿 창에서 보낸 메시지가 원래 창 재방문 시에도 보인다 (같은 섬이 됨)

## 6. 401 복구 (쿠키 삭제 후 자연 재시작)

- [ ] Application → Cookies 에서 `session_uuid` 삭제
- [ ] 그 상태로 메시지 전송 → 빨간 에러 화면이 아니라 **새 세션으로 자연스럽게 재진입** (새 오프닝 시작)
- [ ] 이전 섬은 세이브 코드가 있으면 redeem 으로 되찾을 수 있다

## 7. 공개 표면 위생 (주소창으로)

- [ ] http://localhost:8765/docs → 404 (API 문서 미노출)
- [ ] http://localhost:8765/openapi.json → 404
- [ ] http://localhost:8765/assets/README.md → 404 (문서류 에셋 차단)

## 8. 정리

```bash
# uvicorn Ctrl-C 로 종료. db/llama-server 는 그대로 둔다.
```
