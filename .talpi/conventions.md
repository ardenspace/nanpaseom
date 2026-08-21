# Conventions

## Baseline (applies unless overridden)

- Repeated literals (colors, spacing, paths, magic numbers) live in one
  named home — never inlined in two places. 이번 런의 배치: 쿠키 상수는
  `app/api/session_cookie.py`, 서버 튜닝 값(레이트리밋 횟수/윈도우)은
  rules YAML, 프론트 튜닝 값(넛지 임계값)은 프론트 톤 홈.
- Logic appearing a second time is extracted into the shared layer and
  registered under Shared Utilities below.
- User-visible failure wording follows one tone, defined in one place
  (서버 발신 문구는 rules YAML, 프론트는 tone 모듈 — Failure Behavior
  참조). 테스트도 이 상수를 import 해서 단언한다 — 한글 리터럴 인라인
  금지(하드코딩 게이트가 테스트 파일도 스캔한다).
- A file growing past ~300 lines triggers a split review. Staying
  single-file is a legitimate outcome — record why under Layout &
  Naming. Review trigger, not a hard limit.

레포 룰 승계 (CLAUDE.md와 병행 유효 — talpi 파이프라인이라고 면제되지
않음):

- 권한 경계: 같은 사실은 한 spec 문서에만. 메커니즘/인프라 변경 시
  mechanic-spec 갱신, 메커니즘이면 mapping-spec 정렬 확인.
- 새 락인 결정은 ADR (`docs/adr/NNNN-*.md`, 4자리 시퀀셜, ADR당 1커밋)
  후 spec/YAML 갱신.
- NPC 대사/서버 발신 안전·시스템 메시지 하드코딩 금지 — frontend 포함
  (`scripts/check_no_hardcoded_dialogue.py`, tone 모듈 단일 예외).
  YAML 변경 시 `python3 scripts/check_yaml.py`.
- git: logical unit per commit, 한국어 커밋 메시지에 결정 이유,
  `--no-verify`/`--no-gpg-sign` 금지.
- 테스트: `.venv/bin/pytest` 게이트는 결정적(stub llm) — `-m live` 는
  off-gate. 신규 계약 테스트도 이 구분을 따른다.

## Design Tokens

이번 런은 새 시각 체계 없음 — 기존 유지: `frontend/src/tokens.css`
(CSS custom properties) 단일 홈. `--color-abyss`(배경) /
`--color-sand`(본문·말풍선) / `--color-rust`(액센트) /
`--color-system`(warning/ban/오류 등 프레임 깨는 시스템 문구 전용 — NPC
말풍선 색과 절대 공유 금지). spacing/radius/type scale 같은 파일.
컴포넌트에 리터럴 색/픽셀 금지.

이번 런의 신규 UI(회전 확인, 갈아타기 탈출구, 넛지)는 전부 기존 토큰과
기존 오버레이/버튼 클래스를 재사용한다. 넛지는 시스템 발화이므로
`--color-system` 계열 — NPC 말풍선처럼 보이면 안 된다.

## Shared Utilities

기존 (재사용 대상):

- `tests/api/conftest.py` — 공유 `client` fixture(migrations + truncate,
  `llm_client.call` + `summarize_call` 스텁), `make_stub_reply()`,
  `known_session(turns=0)`, `session_cookie_headers()` /
  `session_cookie_value()`, `db_conn()` / `db_save_code(sid)`,
  `raising_llm(monkeypatch)`. 신규 API 테스트는 이걸 쓴다.
- `frontend/src/api.ts` — `postJson<T>` 공유 클라이언트(fetch + JSON +
  네트워크 실패 정규화 `ApiResult<T>`; 한국어 리터럴/상태 로직 없음).
- `frontend/src/protocol.ts` — 서버 응답 wire shape 단일 홈.
  `has_save_code` 는 여기 `BootstrapData` 에 추가된다(= `RedeemData`
  별칭이 자동 승계 — 이 공유가 B2b 계약의 근거).
- `frontend/src/tone.ts` — 프론트 발신 문구 단일 홈(하드코딩 게이트의
  유일한 예외 파일). 넛지 임계값·신규 문구가 여기 산다.
- `app/api/session_cookie.py` — 쿠키 이름/Max-Age/INSECURE env 이름 +
  발급 단일 경로 `set_session_cookie()`. 쿠키 발급은 반드시 이 함수 경유.
- `app/api/identity.py` — `resolve_session(conn, request)` 신원 해석
  단일 지점(세션 생성 절대 없음). 신규 엔드포인트(rotate)도 이걸 경유.
- `app/store/repo.py` — 세션/턴/세이브 코드 저장 접근 단일 홈.
- `app/save_code.py` — 코드 알파벳/형식 상수 + 생성.
- `rules/identity.yaml` / `rules/save_code.yaml` / `rules/opening.yaml` —
  서버 발신 문구의 유일한 홈.

이번 런에서 생긴 것:

- `tests/api/conftest.py` — `cookie_attrs(header)` Set-Cookie 속성 파서
  (기존 `test_identity_contracts.py` 사설 `_cookie_attrs` 승격). 쿠키
  속성 단언은 이걸 쓴다.
- `tests/api/conftest.py` — `CONTRACT_COOKIE_MAX_AGE = 15552000` (B6
  Max-Age 계약 리터럴의 **테스트 쪽** 단일 홈; 구현 상수 import 는
  동어반복이라 일부러 안 한다) + `assert_cookie_attrs_except_secure(attrs)`
  — Secure 를 뺀 속성 4종(HttpOnly / SameSite=Lax / Max-Age / Path=/)
  공유 단언. Secure 유무는 호출부가 각자 단언한다(발급 표면 = 항상 있다,
  env 매트릭스 = 있냐 없냐가 관찰 대상).

## Prior work this phase (Phase 6 — Acceptance fixes)

- step 1: `tests/api/test_identity_contracts.py` 의 사설
  `_set_save_code` 제거 → conftest 의 `set_save_code` 사용(호출부 4곳).
  grep 결과 세 번째 복사본은 없었고 나머지 4개 모듈은 이미 공유본을
  쓰고 있었다 — 이 파일이 마지막 홀드아웃.
  부수 효과(안전한 방향): conftest 판은 쓰기 전에 `SAVE_CODE_RE` 를
  단언하는 상위집합이라, 이 모듈의 코드 4개도 이제 형식 검증을 거친다
  (전부 통과 — 앞으로 오타는 조용히 쓰이지 않고 시끄럽게 실패).
  364 passed (수 불변).
- step 2: 프론트 fetch 스텁 통합. **신규 공유 유틸**:
  `frontend/src/test/stubServer.ts` — `stubServer(routes, options?)
  → string[]`(호출 경로 기록), `json(status, body)` / `jsonOk(body)`,
  `sticky(replies)`(마지막 응답이 계속 답함 — 언마운트 후 재진입 흉내),
  타입 `StubReply`("unreachable" 포함) / `StubRoute` / `StubRouteSpec`.
  라우트는 상수/큐/함수(RequestInit 접근) 3형태, 미지의 경로는 throw,
  큐 소진 정책은 `options.whenExhausted`(기본 throw).
  setup.ts 와 달리 자동 로드가 아니라 각 테스트가 import 한다.
  네 파일이 필요로 한 능력의 합집합이 설계를 정했다: turn401 은 큐 +
  호출 시퀀스 기록 + 소진 시 401 응답(throw 가 아니라 — 클라이언트
  처리를 계속 관측해야 하므로), replaceConfirm 은 같은 큐에 반대 소진
  정책, saveCode 는 상수 라우트, saveCodeNudge 는 sticky + 요청 본문을
  읽는 함수 라우트.
  단언은 전부 불변(호출 시퀀스 pin 은 바이트 동일). 구현자가 변이
  검사로 시퀀스 pin 이 공허하지 않음을 확인(재시도 응답 제거 → 정확히
  그 지점에서 실패). 45 passed / 6 files (수 불변).
- step 3: 백드롭 클릭이 in-flight 중 `busy` 를 남기던 버그 수정.
  리뷰어 서술이 정확히 확인됨(`App.tsx:441`). 기전: `rescueSaveCode` 가
  `busy=true` 로 두고 await 하는 동안 백드롭 클릭 → 다이얼로그는 닫히고
  `busy` 는 요청이 끝날 때까지 남는다 → 타이틀 버튼 2개가 죽은 채
  이유를 설명하는 화면이 없음. 늦게 온 `setRescue` 는 다음에 열 때
  되살아난다(`submitCode` 가 `rescue` 를 리셋하지 않으므로).
  **선택: 백드롭을 버튼과 같은 방식으로 가드**(닫기 자체를 막음). 이유:
  다른 두 해제 경로가 이미 `disabled={busy}` 라 예외 없이 일관되고,
  다이얼로그의 '연결 중…' 라벨이 곧 설명이 된다. 대안(닫고 전부 리셋)은
  늦은 결과를 버릴 epoch/ref 와 이른 `setBusy(false)` 가 필요해 동시성
  창을 새로 연다.
  **가드는 호출부에** 둬야 한다 — `redeemCode()` 가 `busy` 인 채로
  일부러 `closeConfirm()` 을 부르므로 함수 안에 가드를 넣으면 redeem 이
  깨진다(코드 주석에 기록).
  **같은 결함이 채팅 세이브 코드 패널 백드롭에도 있었고 더 심각**:
  회전 중 누르면 채팅 전체(헤더/선택지/자유입력)가 얼고 NPC 타이핑
  표시가 진행 중이 아닌 턴을 진행 중인 것처럼 보여준다 — 화면이 거짓말을
  한다. 같은 방식으로 수정 + pin.
  **신규 공유 유틸**: `frontend/src/test/overlay.ts` — `clickBackdrop()`
  (백드롭은 role/이름이 없어 클래스 질의가 필요, 두 번째 사용처에서 추출).
  두 pin 다 변이 검사로 비공허 확인(수정 전 실패 재현).
  **47 passed** (45 + 지시된 pin 1 + 2번째 오버레이 pin 1).
  **미조치(설계 결정 필요 — 최종 보고 인계)**: 가드 때문에 요청 중
  백드롭 클릭이 아무 피드백 없이 삼켜진다. 버튼은 회색+'연결 중…' 이
  설명을 주지만 백드롭엔 그런 어포던스가 없다. 값싼 완화는
  `cursor: default` 같은 순수 스타일 변경.
- step 4: `docs/mechanic-spec.md` 낡은 노트 2줄 수정. 리뷰어 서술 2건
  모두 코드 대조로 확인됨 — `ban_session()` 은 `save_code` 를 비우지
  않고, `redeem_save_code` 가 밴 세션 재바인딩을 거부하는 지점에서
  '무효화' 가 성립한다. 플레이어에게 보이는 약속("다른 디바이스에서도
  못 씀")은 참이므로 약화하지 않고, 성립 *지점*만 존재 수준으로 적고
  이유는 ADR 0038 에 위임.
  Sub-2b 노트의 "N/A" 는 지우지 않고 그 슬라이스 당시의 과거 사실로
  시제를 명확히 하고 현재는 아래 항을 보라고 가리킴(날짜 붙은 갱신
  블록이라 역사 기록의 성격).
  **미조치 2건(판단 근거 기록)**: ESC 메뉴 블록은 한 줄 교정이 아니라
  'ESC 메뉴가 여전히 v1 목표인가' 라는 디자이너 결정이 필요(다른 4개
  항목의 집도 같이 정해야 함) → 최종 보고 인계.
  Cloudflare edge 제한 3곳은 *계획* 서술이라 오늘 기준 거짓은 아니고,
  구분 문구를 넣으면 ADR 0039 의 서식지를 계획 목록에 복제하는 셈.

## Prior work — Phase 5 (완료, 참고용)

- step 1: `docs/adr/0038-save-code-rotation.md` — 회전 8개 결정(단일
  활성 코드/무유예/소각 없음/오타와 구분 안 함/축출 아님/발급과 분리/
  confirm-first/스테일 표시 감수). 0033·0034·0036·0037 은 인용만.
  네임스페이스는 `15 × 31^4 ≈ 1,385만` 로 유도식과 함께 적어 숫자가
  `SAVE_CODE_PREFIX_WORDS` 와 드리프트하지 않게 했다.
  **step 4 인계 2건**:
  (a) ADR 0034 의 재검토 목록에 "유출 시 무효화/회전 경로 없음" 이
      그대로 남아 있어 이제 거짓 — 0034 가 그 목록의 단일 서식지이므로
      거기서 "이미 들어온 자를 축출할 경로 없음(회전은 ADR 0038)" 로
      갱신해야 한다.
  (b) `app/save_code.py:61` 주석 `SAVE_CODE_MINT_ATTEMPTS = 20
      # 31^8 공간` 은 0036 이전(완전 랜덤) 근거라 낡았다 — 실제 공간은
      ~1,385만(2^23.8). 재시도 상한 20 자체는 유효.
- step 2: `docs/adr/0039-redeem-rate-limit.md` — 시도 제한 8개 조항.
  0033/0034/0036/0038 인용만. 코드에서 추가로 발견해 기록한 2건:
  `UNKNOWN_CLIENT_KEY`(ASGI client 없는 호출은 한 버킷 공유 — 우회
  방지), 429 에 Set-Cookie 없음 + 문구가 코드 유효성을 알려주지 않음
  (안 그러면 429 자체가 유효 코드 오라클이 된다).
  **최종 보고 인계**: 프록시 뒤에서는 이 제한이 약해지는 정도가 아니라
  누군가 1시간에 10회를 태우면 **전 플레이어가 동시에 잠긴다** —
  사용자 가시적이고 전면적인 실패라, 배포 런에서 목록 항목보다 강한
  게이트(부팅 assert 나 프록시 앞단일 때 필수 env 플래그)를 검토할 값어치.
- step 3: `docs/adr/0040-has-save-code-and-nudge.md` — 진입 필드 +
  넛지 11개 결정. 0033/0034/0035/0038 인용만.
  코드 대조로 교정된 2건(조용히 뭉개지 않고 기록):
  (a) banned/503 은 필드를 *금지*하는 게 아니라 계약이 침묵하는 것 —
      나중에 실어도 위반 아님.
  (b) 다이얼로그 탈출구(`rescueSaveCode`)는 `setHasSaveCode(true)` 를
      호출하지 않는다 — 무왕복 반영은 `issueSaveCode`/`rotateSaveCode`
      뿐이고, 탈출구가 민팅한 사실은 다음 진입에서 서버 진실로 나타난다.
  **step 4 인계 (c)**: 임계값이 tone.ts 에 사는 건 레포의 "튜닝은 YAML"
  결에 어긋나므로 0040 Consequences 에 재검토 항목으로 적혀 있다 —
  mechanic-spec 정렬에서 같은 말을 반복하지 말 것(권한 경계).
- step 4: 권한 문서 정렬. `docs/mechanic-spec.md` — 낡은 절("rotation /
  invalidation deferred to v1.1") 제거 + "세이브 코드 하드닝(ADR
  0038–0040)" 블록 신설(존재 사실만, 상세는 ADR 위임).
  `docs/mapping-spec.md` — 매핑 행 없음, 파일 자체 룰대로 "미매핑
  (의도적)" 목록에 1줄(이전 런의 0033–0037 항목은 그대로 두어 런별
  가독성 유지).
  `docs/adr/0034` 재검토 목록 1줄 갱신 — 무차별 대입은 "조건부 완화
  (0039 의 단일 프로세스·직결 IP 전제 안에서만)", 유출 대응은 "회전으로
  절반만 해소(0038), 이미 들어온 자를 축출할 경로는 여전히 없음".
  한 bullet 안에 두 사실이 있어 둘 다 갱신(반만 고치면 참과 거짓이
  한 줄에 붙는다).
  `app/save_code.py:61` 낡은 주석 `31^8` → `15 × 31^4 ≈ 1,385만 (ADR 0036)`.
  ADR 0040 은 0034 목록에 넣지 않음(오케스트레이터 동의) — 그 목록은
  의식적으로 수용한 *보안* 리스크의 서식지이고 넛지 best-effort 는 UX
  비용이라, 넣으면 목록의 헌장이 넓어진다. 0040 이 자체 트리거를 소유.
  364 passed, 게이트 clean.
  **최종 보고 인계(구현자가 발견, 고치지 않음)**:
  (1) mechanic-spec 2-Strike 절의 "save-code 무효화는 Sub-2b+ 전까지
      N/A" 노트가 낡음. 관련해 "밴 시 세이브 코드 무효화" 는 컬럼을
      비우는 게 아니라 redeem 에서 거부하는 방식으로 *효과상* 충족
      (ADR 0038 은 밴 세션 코드를 그대로 둔다고 명시).
  (2) ESC 메뉴 블록은 미구현 v1 UI 설계 서술이라 회전을 반영하지 않음.
  (3) 제약 줄의 "Cloudflare edge 30 msg/10min/IP" 는 미구현이고 0039 의
      앱 레벨 리미터와 다른 표면 — 독자가 혼동할 여지.

## Prior work — Phase 4 (완료, 참고용)

- step 1: B2b/B5 계약 pin.
  `tests/api/test_has_save_code.py` (12건) — bootstrap new/resumed +
  redeem 양쪽에 필드, 발급/회전 후 true, 기존 필드 불변, 본문에 세션
  식별자 없음(회귀 가드, 지금도 통과).
  `frontend/src/saveCodeNudge.test.ts` (12건, 순수 함수 단위) +
  `frontend/src/App.saveCodeNudge.test.tsx` (8건, 컴포넌트).
  **구현이 제공해야 할 모듈**: `frontend/src/saveCodeNudge.ts` —
  `shouldShowSaveCodeNudge({hasSaveCode, turnCount, dismissed})`,
  `readNudgeDismissed()`, `markNudgeDismissed()`,
  `clearNudgeDismissed()`(코드 없는 **new** 진입에서만 호출).
  현재는 throw 하는 시그니처 스텁 — 테스트가 typecheck 대상이라
  모듈이 없으면 `bun run build` 가 깨지기 때문(스텁이면 tsc 는 통과하고
  테스트는 미구현으로 실패).
  tone 신규: `SAVE_CODE_NUDGE_AFTER_TURNS = 6`(튜닝 홈),
  `SAVE_CODE_NUDGE_BODY`, `SAVE_CODE_NUDGE_DISMISS`.
  **미pin**: 회전 단독 트리거(회전은 발급 뒤에만 도달 가능 — "발급이
  세운 것을 회전이 무너뜨리지 않는다"로만 관찰), resumed 진입의
  turnCount 시드(아래 오케스트레이터 결정으로 확정).

### 오케스트레이터 결정 (step 1 질문 4건 — 전부 Ledger 위임 범위)

1. **resumed + 코드 없음 → 즉시 노출 대상**(dismissed 아니면). 이유:
   resumed 라는 사실 자체가 지킬 진행이 있다는 뜻이고, `_resumed_payload`
   의 history 는 limit=8 로 잘려 있어 거기서 턴 수를 세면 임의의 숫자를
   지어내는 것이다. 40턴 쌓고 코드 없는 복귀자가 넛지의 정확한 표적이라
   더 기다리게 하면 안 된다.
2. **임계값 6턴 유지** (신규 세션 기준). tone 홈에서 튜닝 가능.
3. **넛지에 행동 버튼을 단다** — 닫기만 있으면 플레이어가 헤더 버튼을
   스스로 찾아야 해서 넛지의 목적을 절반만 달성한다. 기존 세이브 코드
   발급 경로를 여는 컨트롤 + tone 상수 신규(step 3).
4. **banned / 503 응답에는 `has_save_code` 를 싣지 않는다** — 계약이
   성공 진입 응답으로 한정하고, 밴 세션은 넛지 대상이 아니며 503 은
   보고할 세션 상태가 없다.

- step 2: `has_save_code` 서버 구현. **신규 공유 지점**:
  `app/api/main.py` 의 `_entry_response(conn, payload, session_uuid)` —
  성공 진입 응답(new/resumed)의 단일 관문. bootstrap 과 redeem 이 둘 다
  이걸 경유하고, `_bootstrap_response` 는 쿠키 발급 헬퍼로 그대로 남아
  banned/503 경로가 계속 직접 호출한다(그래서 그 둘엔 필드가 안 붙음).
  값은 `repo.get_save_code(...) is not None` — 읽기 시점 파생이라
  독립 상태가 없어 드리프트할 수 없다. 스키마/migration/rules 무변경.
  `app/api/main.py` 313 → 328줄(단일 파일 결정 유지). 364 passed.
  **다음 스텝 인계**: `frontend/src/protocol.ts` 의 `BootstrapData` 에
  `has_save_code?: boolean` 추가 — `RedeemData` 가 별칭이라 한 번만
  고치면 두 표면이 모두 덮인다.
- step 3: 넛지 프론트 구현. 배치는 채팅 입력 바 **바로 위 시스템 배너**
  (`role="status"`, `.nudge`) — 메시지 로그에 넣으면 다음 턴에 스크롤로
  밀려 '행동할 수 있는 것'이 아니게 된다. `--color-system` 계열,
  NPC 말풍선 색 미공유.
  **신규 공유 유틸**: `frontend/src/saveCodeNudge.ts` 실구현 —
  `shouldShowSaveCodeNudge` / `readNudgeDismissed` / `markNudgeDismissed`
  / `clearNudgeDismissed`, 저장 키 `nanpaseom.saveCodeNudgeDismissed`
  (playedHint 와 같은 guarded try/catch 형태 — 프라이버시 모드에서
  throw 하지 않고 '미dismiss' 로 degrade).
  `useTurn` 의 `TurnDeps` 에 `onTurnSent` 추가(증가 지점은 `sendTurn` 의
  `pushMsg("user", …)` 직후). 401 복구 *재시도*는 같은 턴이라 다시 세지
  않고, 401→`new` 분기는 `enterChat` 을 지나 0 으로 재시드 + dismiss
  해제(결정 4). 401 회귀 6건 무손상.
  세션 시드는 `enterNudgeSession(data)` 한 곳: `new`→0,
  resumed→임계값(즉시 자격). 발급/회전 성공은 왕복 없이 `hasSaveCode`
  를 true 로 — 컴포넌트 테스트가 bootstrap 호출 1회를 단언해 pin.
  tone 신규: `SAVE_CODE_NUDGE_ACTION = "세이브 코드 받기"`(헤더 버튼
  `SAVE_CODE_BUTTON` 과 일부러 다른 문구 — 동시에 화면에 있어도 헷갈리지
  않게). 행동 버튼은 `issueSaveCode()` 재사용 = 코드 표시 표면을 하나로.
  **App.tsx 606 → 684줄.** 프론트 44/44, pytest 364 passed.
- 검증 [FIX] 2건 해소:
  (1) **B5 위반 경로**였다 — 401→`resumed` 복구 분기가 복구 bootstrap 의
  서버 권위 `has_save_code` 를 버려서, 다른 탭이 코드를 redeem 해 쿠키가
  코드 보유 세션으로 재바인딩된 경우 넛지가 뜰 수 있었다. `TurnDeps` 에
  `onEntrySaveCode(hasSaveCode)` 추가로 플래그만 존중(history 는 계속
  버린다 — 화면 유지가 그 분기의 의도이고 401 회귀 6건이 그걸 pin).
  회귀 테스트 1건 추가(45/45).
  (2) **신규 공유 유틸**: `frontend/src/localFlag.ts` —
  `localFlag(key) → { read, mark, clear }` guarded localStorage 플래그.
  `playedHint.ts` 와 `saveCodeNudge.ts` 가 공유(키는 각 모듈이 소유).
  공개 API 이름은 계약 pin 이라 그대로.
  **관찰(계약상 정상)**: `has_save_code` 가 빠진 resumed 응답은 false 로
  읽혀 넛지가 다시 열릴 수 있다 — B2b 가 모든 진입 shape 에 필드를
  보장하므로 규격 위반 응답에서만 발생.

## Prior work — Phase 3 (완료, 참고용)

- step 1: B4 계약 pin — `frontend/src/App.replaceConfirm.test.tsx` 12건.
  **회귀 절반 5건은 즉시 통과**(상시 입구 2, 무조건 확인 2, 취소 시
  입력 보존·무요청 1) = 배포된 동작 무손상 확인. **탈출구 절반 7건 red**
  (버튼 부재). 실패 분기 4종(401/밴/503/네트워크)은 각각 (a) 공통 실패
  문구 노출 + 복사 컨트롤 없음, (b) **redeem 이 계속 가능**(확인 버튼
  살아 있고 실제로 `/save-code/redeem` 이 나가 채팅 진입)까지 단언 —
  (b)가 계약의 하중 부분.
  tone 신규: `REPLACE_RESCUE_CODE` / `REPLACE_RESCUE_FAILED`.
  복사 컨트롤은 기존 `SAVE_CODE_COPY` / `SAVE_CODE_COPIED` 승계.
  **구현이 지켜야 할 pin 결정**: 실패 문구는 원인별로 나누지 않고 공통
  1개(단, 서버 `ban_reason`/`message` 를 *추가로* 렌더하는 건 허용 —
  공통 문구를 *대체*하면 안 됨). 실패 시 복사 컨트롤은 없어야 한다.
  **미pin 2건**: 탈출구가 '이 기기의' 세션 코드인지(jsdom 은 쿠키를
  안 나름 — 그건 B2 서버 계약 몫), 클립보드 *성공* 라벨 전환.
- step 2: 탈출구 구현. 다이얼로그의 경고 본문과 액션 행 *사이*에 배치
  (읽는 순서 = 잃을 것을 읽고 → 돌아올 길을 만들고 → 결정). 진행 중엔
  누른 컨트롤만 CONNECTING(확인 버튼은 라벨 유지), 성공 시 버튼 자리에
  코드 + 복사, 실패 시 공통 문구 + 서버 사유를 *아래에* 보조로. 취소/
  백드롭/닫기는 탈출구 상태를 리셋.
  **신규 공유 컴포넌트**: `frontend/src/CopyCodeButton.tsx` —
  `CopyCodeButton({ code })`, `copied` 상태를 스스로 소유. 채팅 패널과
  다이얼로그가 공유하며, 채팅 쪽은 `key={saveCode}` 로 회전 시 remount
  되어 라벨이 알아서 되돌아간다(수동 리셋 호출을 잊을 여지 제거).
  `readSaveCodeResult` 는 세 번째 호출부(발급/회전/구조)로 재사용.
  `app.css` 에 `.replace-rescue` 1개(토큰만).
  타이틀에서 받은 구조 코드는 `saveCode` 캐시에 넣지 않는다 — redeem
  성공 후 그 코드는 방금 떠난 세션의 것이라 캐시에 남으면 거짓말이 된다.
  **App.tsx 558 → 606줄.**
  **다음 런 후보(구현자 관찰)**: 절단선이 분명해졌다 — `SaveCodePanel`
  과 `ReplaceConfirmDialog` 를 빼면 App.tsx 가 ~350 아래로 떨어지고
  13개짜리 useState 뭉치가 각 다이얼로그로 흩어진다. `CopyCodeButton`
  이 그 디렉토리의 첫 입주자.

## Prior work — Phase 2 (완료, 참고용)

- step 1: vitest 도입 — `frontend/vite.config.ts` 에 `test` 블록(jsdom,
  `src/**/*.test.ts(x)`, setup 파일, `globals:false`). 프로덕션 빌드와
  같은 Vite 파이프라인을 쓴다(별도 config 없음 → 플러그인/해석 드리프트
  방지). `frontend/src/test/setup.ts` (신규 공유 — 전 테스트가 경유),
  `frontend/src/playedHint.test.ts` (러너 실증 pin 3건).
  스크립트: `bun run test` / `test:watch`. `build` 불변.
  의존성: vitest 4.1.11, jsdom 30.0.1, @testing-library/react 16.3.2,
  @testing-library/dom 10.4.1. RTL 을 지금 넣은 이유: B1 의 "회전 도달
  가능 + 문구 명시"는 렌더 수준 사실이라 가짜 seam 을 만들어 pin 하면
  허구를 pin 하게 된다.
- step 2: 계약 pin — `tests/api/test_save_code_rotate.py`(B1 서버 12건 +
  B2 회귀), `tests/api/test_redeem_rate_limit.py`(B3 7건, 수치는 rules
  에서 읽어 하드코딩 없음), `frontend/src/App.saveCode.test.tsx`(B1
  어포던스 3건). `tests/api/conftest.py` 에 `set_save_code(sid, code)` /
  `banned_session(turns=1)` 승격. `frontend/src/test/setup.ts` 에
  `scrollIntoView` no-op 추가(jsdom 미구현 — 컴포넌트 테스트 필수).
  tone 신규: `SAVE_CODE_ROTATE`, `SAVE_CODE_ROTATE_WARNING`,
  `RETIRED_IMMUTABLE_CODE_CLAIM`(회귀 가드용 — 렌더 안 함).
  **다음 스텝이 반드시 제공할 seam**: `app/api/rate_limit.py` 모듈 레벨
  `reset()`, `rules/save_code.yaml` 키 3종(`redeem_rate_limit_attempts` /
  `redeem_rate_limit_window_seconds` / `redeem_rate_limited_message`) +
  `SaveCodeRules` 필드(extra=forbid 라 모델도 같이).
  **오염 주의**: 리미터는 프로세스 전역이고 기존 redeem 테스트가 전부
  같은 IP(`testclient`)를 쓴다 → `reset()` 을 공유 `client` fixture 에
  반드시 배선. 안 하면 기존 redeem 계약 테스트가 누적 카운트로 깨진다.
  **미pin 1건**: B3 "윈도우 만료 기록 정리" — 결정적 관찰에 시간 seam 이
  필요해, 구현 스텝이 seam 과 그 테스트를 함께 만든다.
- step 3: `POST /save-code/rotate` 구현. **신규 공유 유틸**:
  `app/save_code.py` 의 `mint_save_code(conn, session_uuid, *, avoid=None)`
  + `SAVE_CODE_MINT_ATTEMPTS` + `SaveCodeMintError` (기존 `main.py` 사설
  `_mint_save_code` 승격 — 발급/회전 공용, 도메인 모듈이라 HTTPException
  대신 도메인 예외). `avoid` 는 계약 요구: 회전이 우연히 같은 코드를
  재생성하면 옛 코드가 계속 통해버린다. `main.py` 에 `_mint` 얇은 어댑터
  (도메인 예외→500), `_no_session_response()` / `_banned_response(sess)`
  공유 응답 헬퍼(각각 3번째 사용처가 생겨 승격). 회전 성공은 Set-Cookie
  없음(세션 불변 — 오케스트레이터 결정). rules YAML 무변경(회전 전용
  서버 문구 없음, 401 은 identity.yaml 재사용).
  `app/api/main.py` 296줄 — 300줄 트리거 미만이라 단일 파일 유지.
  340 passed (기존 329 + rotate 11).
- step 4: redeem 시도 제한. **신규 공유 유틸**: `app/api/rate_limit.py`
  — `allow(key, *, limit, window_seconds)`, `client_ip(request)`
  (`request.client.host` 만 — XFF 절대 안 봄, client 없으면 `"-"` 공유
  버킷), `reset()`(테스트 경계 초기화 — 공유 `client` fixture 에 배선됨),
  **`now()` 시간 seam**(`time.monotonic` 래퍼 — 테스트는
  `monkeypatch.setattr(rate_limit, "now", fake_clock)` 로 시계를 민다.
  엔드포인트 시계도 같이 움직여 sleep 없이 윈도우 만료를 관찰).
  허용된 시도만 기록(차단이 윈도우를 연장하지 않음 → 영구 잠금 없음),
  청소는 윈도우당 1회 amortized sweep.
  수치: **10회 / 3600초** (rules/save_code.yaml). 사람 오타는 2–3회라
  3배 여유, 공격자는 하루 240 추측 → 유효 코드 1000개 가정에도 단일 IP
  기대 ~58일. 성공이 예산을 환급하지 않으므로 유효 코드 보유가 우회
  수단이 되지 않는다.
  `tests/api/test_rate_limit_cleanup.py` 신규(미pin 이었던 만료 정리 +
  윈도우 복구를 시간 seam 으로 pin). 352 passed.
  **프론트 인계**: redeem 오류 경로가 이미 `data.message` 를 그대로
  띄우므로 429 문구는 서버(rules)가 소유한다 — tone 에 중복 상수를
  만들지 말 것(같은 사실 한 홈).
- step 5: 훅 추출(동작 보존) + 401 회귀 pin. **신규 공유 유틸**:
  `frontend/src/useTurn.ts` — `useTurn(deps): { sendTurn(text) }`,
  `TurnDeps = { busy, setBusy, npcId, pushMsg, setChoices, showBanned,
  enterChat }`. `applyTurn` 은 훅 내부 비공개(다른 호출부 없음).
  `Msg` 타입의 홈도 여기(훅이 로그의 유일한 append 지점). 상태는 훅에
  두지 않음 — `busy` 를 타이틀/redeem/발급 경로가 공유하므로 App 소유.
  동작 델타는 밴 분기 2곳을 `showBanned(reason)` 로 합친 것뿐(`start()`
  는 choices 를 안 비우므로 일부러 제외).
  `frontend/src/App.turn401.test.tsx` — 401 복구 6건(호출 시퀀스까지
  단언해 '무한 루프 없음'을 pin).
  **App.tsx 534 → 476줄.**
- step 6: 회전 UI — 기존 세이브 코드 오버레이 안의 2상태 패널(신규
  오버레이 없음). 기본 상태[코드 복사/새 코드로 바꾸기/닫기] → 확인
  상태(코드는 그대로 보이고 note 자리에 경고, 서버 호출은 확인 누른
  뒤에만). **confirm-first** 선택 이유: 옛 코드를 쥔 쪽에게 회전은
  되돌릴 수 없으니 경고는 결과와 나란히가 아니라 *바꾸기 전에* 나와야
  한다. 성공 후 패널 유지(새 코드 표시, 복사 라벨 리셋) — 회전 직후가
  코드를 적어야 하는 순간이라 닫으면 필요한 걸 감춘다.
  **신규 공유 유틸**: `App.tsx` 모듈 스코프 `readSaveCodeResult(r)` —
  발급/회전이 unreachable/ok/banned/401 분기 읽기를 공유(오류를 어디
  띄우냐만 다름). `protocol.ts` 는 `SaveCodeIssueData` 재사용(유사
  중복 타입 안 만듦). `app.css` 에 `.overlay__body--warning` /
  `.overlay__error` / actions `flex-wrap`(버튼 3개) — 토큰만 사용.
  tone: `SAVE_CODE_ISSUED_NOTE` 개정(아래), 신규 상수 불필요.
  **App.tsx 476 → 558줄** (UI 추가분).
  **Phase 5 인계(중요)**: mechanic-spec/mapping-spec 에 세이브 코드
  회전 행이 없다 — 엔드포인트를 추가하고 권한 문서를 안 고친 상태라
  수락 때 drift 로 읽힌다. Phase 5 ADR/정렬 스텝에서 반드시 처리.

## Prior work — Phase 1 (완료, 참고용)

- step 1: `tests/api/test_cookie_env_flag.py` (신규) — B6 허용목록 판정
  매트릭스(ON 5 / OFF 21 / unset), 발급 표면(Set-Cookie)으로 관찰.
  `tests/safety/test_strike.py` — B7 예외 pin + `python -O` 생존 pin.
  `tests/api/test_identity_contracts.py` — B7 도달 불가(호출부 전제) pin.
  `tests/api/conftest.py` — `cookie_attrs` 승격.
- step 2: `app/api/session_cookie.py` — `INSECURE_COOKIE_ON_VALUES =
  frozenset({"1","true"})` 허용목록 판정(`_FALSY_ENV_VALUES` 폐지,
  `.strip()` 제거 → 공백 포함 값은 OFF). B6 33/33 green.
  **Phase 5 인계**: ADR 0034 clause 2("플래그가 켜진 경우에만 Secure
  생략")가 "켜짐"을 정의하지 않으므로 개정/보충 필요 — 이 반전의 단일
  홈을 ADR 0034 개정으로 할지 신규 ADR로 할지 Phase 5에서 결정.
  레포 전역 grep 결과 `.env.example`/compose/배포 스크립트에 이 env
  참조 없음(= 손으로 세팅한 dev env 외 영향 없음).
- step 3: `app/safety/strike.py` — `UnknownSessionError(RuntimeError)` +
  `repo.session_exists` 선행 검사(부작용 전에 죽음). `/turn` 호출부는
  step 0 `resolve_session` 401 게이트 덕에 도달 불가 — 가드 추가 불필요.
  전 스위트 329 passed. 관찰: `scripts/check_no_hardcoded_dialogue.py`
  는 실행 비트 없음 — 인터프리터 경유로 호출해야 함.
- step 4 (검증 [FIX] 2건, 테스트 위생 전용 — 프로덕션 무변경):
  `tests/api/conftest.py` 에 `CONTRACT_COOKIE_MAX_AGE` +
  `assert_cookie_attrs_except_secure` 승격. `test_cookie_env_flag.py` /
  `test_identity_contracts.py` 는 env 이름을 `app.api.session_cookie`
  에서 import 하고(리터럴 인라인 제거), 속성 4종 단언을 공유 헬퍼로
  위임. `test_identity_contracts.py` 의 `COOKIE_NAME` 사설 리터럴도
  같은 이유로 프로덕션 import 로 교체. 329 passed (수 불변).

이번 런에서 생길 것 (구현자가 만들면서 여기에 등록):

- 세이브 코드 민팅 재시도 로직 — 발급과 회전이 공유해야 한다(현재
  `_mint_save_code` 가 `main.py` 사설. 두 번째 사용처가 생기는 순간
  공유층 승격 대상).
- redeem 시도 카운터 — 단일 홈 모듈. 테스트가 결정적으로 초기화할 수
  있는 진입점을 노출한다(TestClient 는 모든 테스트가 같은 호스트로
  잡히므로, 초기화 없이는 기존 redeem 계약 테스트가 오염된다).
- 프론트 넛지 판정 순수 함수 — 컴포넌트 밖(테스트 가능 seam).
- vitest 셋업 파일/헬퍼 — 신규 프론트 테스트는 이걸 쓴다.

## Layout & Naming

- Python: 기존 구조 유지 — `app/api`(endpoint), `app/store`(repo),
  `app/safety`, `app/turn`, `migrations/NNN_*.sql` 시퀀셜. 이번 런은
  스키마 변경 없음(`sessions.save_code` 단일 컬럼 유지) — 새 migration
  이 필요하다고 느껴지면 그건 spec 을 벗어난 신호다.
- `app/api/main.py` **313줄 — 300줄 리뷰 완료, 단일 파일 유지 결정**:
  자연스러운 절단선은 save-code 라우터인데 `redeem` 이 `bootstrap` 과
  `_bootstrap_response` / `_resumed_payload` / `_new_payload` /
  `BOOTSTRAP_NPC_ID` 를 공유한다 → 분리하면 세 번째 공유 모듈
  (`session_payload` 류)이 강제된다. 이건 리미터 추가와 직교하는 구조
  변경이라 자체 스텝을 가질 자격이 있고, 레이트리밋 커밋에 얹혀 가면 안
  된다. (다음 런 후보.)
- `frontend/src/App.tsx` **476줄** (훅 추출 완료 — 534에서 감량).
  300줄 트리거는 여전히 넘지만 유지: 남은 부피는 화면 3개(타이틀/밴/채팅)
  렌더 트리 + 세이브 코드 발급/redeem/복사 핸들러이고, 다음 절단선은
  화면 단위 컴포넌트 분리다(이번 런 범위 밖 — UI 를 더 얹는 페이즈가
  남아 있어 지금 자르면 두 번 자르게 된다).
- **기존 `/turn` 401 복구 경로의 관찰 사항** (step 5에서 발견, 고치지
  않고 기록 — 이번 런 범위 밖):
  1. 재시도가 복구 bootstrap 의 `npc_id` 대신 401 이전 클로저 값을 쓴다.
  2. `resumed` 복구 시 서버가 준 history/choices 를 버리고 화면을 그대로
     둔다(같은 세션이면 무해, 다른 세션이면 조용히 어긋남).
  3. `new` 복구 시 방금 보낸 플레이어 입력이 시스템 안내 없이 사라진다 —
     삼켜진 것처럼 읽힌다. (넛지 재노출이 키로 삼는 바로 그 seam.)
  4. "1회 복구"는 페이지 로드가 아니라 턴 단위 — 사용자 행동당 유계.
  5. `/turn` 비-401 실패는 서버 문구를 무시하고 GENERIC_ERROR 를 쓰는데
     bootstrap 실패는 서버 문구를 선호한다(같은 실패류에 다른 안내).
- 프론트 테스트 파일 배치·명명은 위임 — 단 하드코딩 게이트 스캔 대상
  (`frontend/**/*.ts(x)`)이므로 문구는 반드시 tone 홈에서 import.
- **프론트 테스트 이름은 영어로 쓴다.** 하드코딩 게이트는 *문자열
  리터럴*을 잡으므로 `it("힌트가 없으면…")` 자체가 위반이다. 한글
  주석은 따옴표로 감싸지만 않으면 통과. 사용자 문구 단언은 `tone.ts`
  에서 import (게이트가 설계대로 작동하는 것).
- 프론트 테스트 환경 주의: Node 25 는 `globalThis.localStorage` 를 이미
  갖고 있어 vitest jsdom 환경이 이를 건너뛴다 → `setup.ts` 가
  jsdom 실물 storage 로 재지정한다. 스토리지를 쓰는 테스트(넛지
  dismiss 플래그 등)는 이 setup 을 신뢰해도 된다.
- dev 포트: backend **8765**(uvicorn), frontend **5173**(vite proxy →
  8765). 머신 상시 점유 포트(8080 llama-server, 8000, 8081, 5433, 5000,
  7000, 7265, 6463) 회피.

## Environment (이 머신 — 반드시 지킬 것)

- **죽이지 말 것**: `8080` llama-server(로컬 LLM — 이 프로젝트의 LLM
  백엔드), `8000` docker app-chak-backend, `8081` docker forps-backend,
  `5433` docker forps-postgres. 포트가 잡혀 있으면 먼저 확인
  (`lsof -nP -iTCP:<port> -sTCP:LISTEN`) — 무작정 kill 금지.
- `5000`/`7000` 은 macOS Control Center(AirPlay) 점유 — dev 포트로 쓰지
  말 것.
- 이 프로젝트 DB: `docker compose up -d db` 로 띄운다.
- Python 은 레포 `.venv` 사용 (`.venv/bin/pytest`, `.venv/bin/python`).
  프론트는 bun.

## Commit convention (레포 룰 — talpi 기본형보다 우선)

- 메시지: `talpi: phase <n> step <k>: <한국어 요약 — 결정 이유 포함>`.
  한국어 본문에 *왜* 그렇게 했는지가 들어가야 한다(CLAUDE.md).
- ADR 커밋은 ADR당 1커밋 (Phase 5).
- `--no-verify` / `--no-gpg-sign` 절대 금지.

## Failure Behavior

- 오류 응답 공통 형태: `{status:"error", message}` (+ HTTP 4xx/5xx) —
  앱 발신 오류에만 적용. FastAPI 기본 422/HTTPException detail 은
  프레임워크 기본값 그대로.
- 신규 429(시도 제한): 같은 형태 + 솔직한 시스템 톤, 문구는 rules YAML.
  "왜 막혔는지"를 숨기지 않되 공격자에게 유효 코드 정보를 주지 않는다.
- 404(미지/형식 위반/무효화된 코드): **하나의 문구로 통일** — 죽은 코드와
  오타를 구분하지 않는다(코드 히스토리가 없으므로 구분 자체가 불가).
- 401(무신원/모르는 세션): recoverable — 프론트는 자동 재bootstrap 1회,
  재실패 시 솔직한 시스템 톤, 무한 루프 금지.
- 탈출구 실패(401/밴/500/네트워크): recoverable — 코드를 못 받았다는
  사실만 솔직히 알리고, 갈아타기 자체는 계속 진행 가능해야 한다.
  탈출구 실패가 redeem 을 막으면 그게 회귀다.
- 인프라 실패(503 등): 솔직한 시스템 톤 — NPC를 흉내내지 않는다.
- 밴: fatal — HTTP 200 `{status:"banned"}`(오류 아닌 상태), 차단 화면,
  입력 봉인. 회전도 밴 세션에는 동작하지 않는다.
- `strike.register` 전제 위반: fatal(예외) — 단, 기존 호출부에서는
  **도달 불가**여야 한다. 도달하면 그것이 버그 신호이며, 플레이어가
  `/turn` 중 500 을 보는 상황은 회귀로 취급한다.
