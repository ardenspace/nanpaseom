"""B2 세션 bootstrap 계약 (이 모듈이 URL/필드명을 확정 — Phase 1 boundary pin).

계약 요약:

- URL: ``POST /session/bootstrap`` — request body 없음. **쿠키가 신원**.
- 쿠키 이름: ``session_uuid`` (서버가 발급/재발급. HttpOnly 등 속성은
  tests/api/test_identity_contracts.py 의 B6 계약이 pin).
- 응답 200, status 판별자 (B1 이후 **본문에 session_uuid 없음** — 세션 식별은
  Set-Cookie 헤더로만):
  - ``"new"``     → ``{status, npc_id, reply, choices}``
                    reply = 수리공 오프닝 대사(비어있지 않음, 내용은 단언하지 않음),
                    choices 비어있지 않은 ``[{tone, text}]``.
  - ``"resumed"`` → ``{status, npc_id, history, choices}``
                    history = 최근 N턴 ``[{role, content}]`` (role ∈ user|assistant),
                    choices = 마지막 npc 응답의 choices (``[]`` 이면 자유 입력 모드).
                    resumed 는 LLM 호출 없이 동작한다.
  - ``"banned"``  → ``{status, npc_id, ban_reason}`` — 대화 데이터
                    (reply/history/choices) 키 미포함.
- 응답 503 (오프닝 생성 실패): ``{status: "error", message}`` — message 는 시스템 톤,
  대화 데이터/choices 키 미포함.
- npc_id 는 서버가 결정 — 이번 런은 수리공 ``"surigong"`` 고정.
- 턴 0개 세션(미지의 쿠키 포함) 재진입 = 신규 취급: 기존 세션이면 같은
  session_uuid 를 재사용해 오프닝을 다시 시도한다. "0턴인데 resumed" 는 없다.
"""

import uuid

from tests.api.conftest import known_session, make_stub_reply, session_cookie_value

BOOTSTRAP_URL = "/session/bootstrap"
TURN_URL = "/turn"
COOKIE_NAME = "session_uuid"
NPC_ID = "surigong"


def _raising_llm(monkeypatch):
    import app.llm.client as llm_client

    def boom(system, messages):
        raise llm_client.LLMError("llama-server down (stub)")

    monkeypatch.setattr(llm_client, "call", boom)


# ---------------------------------------------------------------- status: new

def test_no_cookie_creates_session_with_opening_and_sets_cookie(client):
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert body["npc_id"] == NPC_ID
    assert "session_uuid" not in body  # 자격증명은 응답 본문에 없다 (쿠키로만)
    # 오프닝 대사 — 내용은 단언하지 않음(NPC 대사 하드코딩 금지), 비어있지 않음만.
    assert body["reply"]
    assert body["choices"]  # 비어있지 않음
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]
    # 쿠키 발급 — 서버가 민팅한 UUID.
    uuid.UUID(session_cookie_value(r))


def test_unknown_cookie_is_treated_as_new(client):
    client.cookies.set(COOKIE_NAME, str(uuid.uuid4()))
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert body["npc_id"] == NPC_ID
    assert body["reply"] and body["choices"]


def test_zero_turn_session_reentry_is_new_and_reuses_session(client):
    # sessions row 는 있으나 chat_logs 0개 → 계약상 "0턴인데 resumed" 는 존재하지 않음.
    sid = known_session(turns=0)
    client.cookies.set(COOKIE_NAME, sid)
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert session_cookie_value(r) == sid  # 같은 세션/쿠키 재사용
    assert body["reply"] and body["choices"]


# ----------------------------------------------------------- 쿠키 수명 (장수)

def _session_cookie_headers(response) -> list[str]:
    return [
        h for h in response.headers.get_list("set-cookie")
        if h.strip().startswith(f"{COOKIE_NAME}=")
    ]


def test_bootstrap_cookie_is_long_lived_with_max_age(client):
    """브라우저 완전 종료 후 재방문에도 세션이 이어져야 함 — session cookie 금지 pin."""
    from app.api.session_cookie import SESSION_COOKIE_MAX_AGE

    r = client.post(BOOTSTRAP_URL)
    headers = _session_cookie_headers(r)
    assert headers
    for h in headers:
        assert f"Max-Age={SESSION_COOKIE_MAX_AGE}" in h


def test_bootstrap_503_retry_cookie_is_long_lived_with_max_age(client, monkeypatch):
    """503 에도 쿠키를 심어 재시도 시 같은 세션 재사용 — 그 쿠키도 장수여야 함."""
    from app.api.session_cookie import SESSION_COOKIE_MAX_AGE

    _raising_llm(monkeypatch)
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 503
    headers = _session_cookie_headers(r)
    assert headers
    for h in headers:
        assert f"Max-Age={SESSION_COOKIE_MAX_AGE}" in h


# ------------------------------------------------------------- status: error

def test_opening_failure_returns_503_error_shape(client, monkeypatch):
    _raising_llm(monkeypatch)
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]  # 시스템 톤 안내 — 내용은 단언하지 않음
    for key in ("reply", "choices", "history"):
        assert key not in body


def test_failed_opening_then_retry_succeeds_as_new(client, monkeypatch):
    import app.llm.client as llm_client

    _raising_llm(monkeypatch)
    r1 = client.post(BOOTSTRAP_URL)
    assert r1.status_code == 503

    # 복구 후 같은 클라이언트(쿠키 유지) 재진입 → 신규와 동일하게 오프닝 재시도.
    monkeypatch.setattr(llm_client, "call", lambda system, messages: make_stub_reply())
    r2 = client.post(BOOTSTRAP_URL)
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "new"
    assert body["reply"] and body["choices"]


# ----------------------------------------------------------- status: resumed

def test_valid_cookie_with_turns_resumes_with_history_and_choices(client):
    sid = known_session(turns=1)  # bootstrap 민팅 시뮬레이트 — /turn 은 세션을 만들지 않는다
    client.cookies.set(COOKIE_NAME, sid)
    rb = client.post(BOOTSTRAP_URL)
    assert rb.status_code == 200
    body = rb.json()
    assert body["status"] == "resumed"
    assert body["npc_id"] == NPC_ID
    assert session_cookie_value(rb) == sid
    assert body["history"]
    for msg in body["history"]:
        assert msg["role"] in ("user", "assistant")
        assert msg["content"]
    # 마지막 npc 응답의 choices (헬퍼 raw 는 3개).
    assert len(body["choices"]) == 3
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]


def test_new_then_reenter_is_resumed_with_opening_in_history(client):
    r1 = client.post(BOOTSTRAP_URL)
    assert r1.json()["status"] == "new"
    sid = session_cookie_value(r1)

    r2 = client.post(BOOTSTRAP_URL)  # TestClient 쿠키 jar 로 재진입
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "resumed"
    assert session_cookie_value(r2) == sid
    assert body["history"]  # 오프닝 턴이 히스토리에 존재 (턴 ≥ 1)


def test_resumed_with_empty_choices_is_free_input_mode(client, monkeypatch):
    # LLM 다운 → run_turn diegetic fallback: 턴은 로그되지만 choices [] (자유 입력 모드).
    sid = known_session(turns=0)
    client.cookies.set(COOKIE_NAME, sid)
    _raising_llm(monkeypatch)
    r = client.post(TURN_URL, json={"npc_id": NPC_ID, "player_input": "안녕"})
    assert r.status_code == 200
    assert r.json()["choices"] == []

    # LLM 은 계속 raising 상태 — resumed 는 LLM 호출 없이 동작해야 함.
    rb = client.post(BOOTSTRAP_URL)
    assert rb.status_code == 200
    body = rb.json()
    assert body["status"] == "resumed"
    assert session_cookie_value(rb) == sid
    assert body["choices"] == []
    assert body["history"]


# ------------------------------------------------------------ status: banned

def test_banned_session_bootstraps_as_banned_without_conversation_data(client):
    sid = known_session(turns=0)
    client.cookies.set(COOKIE_NAME, sid)
    client.post(TURN_URL, json={"npc_id": NPC_ID, "player_input": "씨발"})
    r2 = client.post(TURN_URL, json={"npc_id": NPC_ID, "player_input": "개새끼"})
    assert r2.json()["kind"] == "ban"

    rb = client.post(BOOTSTRAP_URL)
    assert rb.status_code == 200
    body = rb.json()
    assert body["status"] == "banned"
    assert body["npc_id"] == NPC_ID
    assert session_cookie_value(rb) == sid
    assert body["ban_reason"]
    for key in ("reply", "choices", "history"):
        assert key not in body
