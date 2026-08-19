"""B3 세이브 코드 발급/입력 계약 (이 모듈이 URL/필드명을 확정 — Phase 3 boundary pin).

계약 요약:

- 코드 형식: ``XXXX-XXXX`` 9자 (하이픈 포함, VARCHAR(9)). 알파벳 = A-Z·2-9 에서
  혼동 문자(O/I/L/0/1) 제외 — 단일 정의 ``app/save_code.py`` (테스트는 그 regex 로 pin.
  PREFIX 단어 목록 등 생성 전략은 구현 재량).

- 발급: ``POST /save-code`` — request body 없음, **쿠키가 신원** (``session_uuid``).
  - 200 ``{status: "ok", save_code}`` — save_code 는 형식 만족 + ``sessions.save_code``
    (UNIQUE) 에 저장됨.
  - 쿠키 없음 → 400 ``{status: "error", message}``. 세션 생성/쿠키 발급 없음.
  - 밴 세션 → 200 ``{status: "banned", ban_reason}``. 코드 미발급 (DB NULL 유지).
  - 재발급(이미 코드 있는 세션): 기존 코드 반환 vs 재민팅은 구현 재량 —
    "200 + 형식 만족 + 그 코드로 redeem 가능" 만 pin.

- 입력(redeem): ``POST /save-code/redeem`` — body ``{"code": str}``.
  대상 세션 상태에 따라 bootstrap 과 동일 시맨틱:
  - 턴 ≥ 1 → 200 ``{status: "resumed", session_uuid, npc_id, history, choices}``
  - 턴 0개 → 200 ``{status: "new", session_uuid, npc_id, reply, choices}`` (오프닝 생성)
  - 쿠키 재바인딩(Set-Cookie)은 **성공 응답(new/resumed)과 함께만** — 이후 bootstrap 이
    그 세션으로 이어진다.
  - 잘못된/미지의 코드 → 404 ``{status: "error", message}``. 쿠키/기존 세션 무변경.
  - 밴 세션의 코드 → 200 ``{status: "banned", ban_reason}``. **재바인딩 없음**,
    기존 세션 무변경.
  - 턴 0개 + 오프닝 생성 실패 → 503 ``{status: "error", message}``. 쿠키 무변경.
"""

import uuid

import psycopg

from app.config import DATABASE_URL
from app.save_code import (
    SAVE_CODE_LENGTH,
    SAVE_CODE_PREFIX_WORDS,
    SAVE_CODE_RE,
    generate_save_code,
)
from app.store import repo
from tests.api.conftest import make_stub_reply

ISSUE_URL = "/save-code"
REDEEM_URL = "/save-code/redeem"
BOOTSTRAP_URL = "/session/bootstrap"
COOKIE_NAME = "session_uuid"
NPC_ID = "surigong"


# ------------------------------------------------------------------- helpers

def _db():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def _set_save_code(sid: str, code: str) -> None:
    """redeem 테스트를 발급 엔드포인트와 디커플 — DB 에 직접 코드 부여."""
    assert SAVE_CODE_RE.fullmatch(code)
    with _db() as c:
        c.execute("UPDATE sessions SET save_code = %s WHERE session_uuid = %s", (code, sid))


def _db_save_code(sid: str) -> str | None:
    with _db() as c:
        row = c.execute(
            "SELECT save_code FROM sessions WHERE session_uuid = %s", (sid,)
        ).fetchone()
    return row[0] if row else None


def _zero_turn_session() -> str:
    """sessions row 만 있고 chat_logs 0개인 세션."""
    with _db() as c:
        sid = repo.mint_session(c)
        repo.ensure_session(c, sid)
    return sid


def _session_with_turns(client) -> str:
    """/turn 은 쿠키를 만지지 않음 — client 쿠키 jar 오염 없이 턴 ≥ 1 세션 생성."""
    r = client.post("/turn", json={"npc_id": NPC_ID, "player_input": "보트 수리 잘 돼?"})
    assert r.status_code == 200
    return r.json()["session_uuid"]


def _banned_session(client) -> str:
    """2-strike 로 밴된 세션 (기존 safety 흐름 재사용, 쿠키 무관)."""
    r1 = client.post("/turn", json={"npc_id": NPC_ID, "player_input": "씨발"})
    sid = r1.json()["session_uuid"]
    r2 = client.post(
        "/turn", json={"session_uuid": sid, "npc_id": NPC_ID, "player_input": "개새끼"}
    )
    assert r2.json()["kind"] == "ban"
    return sid


def _session_set_cookies(response) -> list[str]:
    """응답이 session_uuid 쿠키를 심는지 — 재바인딩 유무 단언용."""
    return [
        h for h in response.headers.get_list("set-cookie")
        if h.strip().startswith(f"{COOKIE_NAME}=")
    ]


def _raising_llm(monkeypatch):
    import app.llm.client as llm_client

    def boom(system, messages):
        raise llm_client.LLMError("llama-server down (stub)")

    monkeypatch.setattr(llm_client, "call", boom)


def _restore_llm(monkeypatch):
    import app.llm.client as llm_client

    monkeypatch.setattr(llm_client, "call", lambda system, messages: make_stub_reply())


# ------------------------------------------------------------ 형식 (generation)

def test_generated_code_prefix_is_a_word_from_the_curated_list():
    """인간 재판정 (2026-08-19): 프리픽스 = 단어 목록, 뒤 4자 = 랜덤 — pin.

    전체 형식(9자, SAVE_CODE_RE)은 기존 테스트가 pin — 여기서는 새 결정인
    "앞 그룹은 허용 알파벳 내 4자 단어 목록에서 온다"만 단언.
    """
    for _ in range(50):
        code = generate_save_code()
        assert SAVE_CODE_RE.fullmatch(code)
        prefix, _tail = code.split("-")
        assert prefix in SAVE_CODE_PREFIX_WORDS


# ------------------------------------------------------------------ 발급 (issue)

def test_issue_returns_wellformed_code_and_persists_it(client):
    sid = _session_with_turns(client)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ISSUE_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    code = body["save_code"]
    assert len(code) == SAVE_CODE_LENGTH
    assert SAVE_CODE_RE.fullmatch(code)  # 4자-4자, 허용 알파벳 (O/I/L/0/1 없음)
    assert _db_save_code(sid) == code  # UNIQUE 컬럼에 저장됨


def test_issue_without_cookie_is_error_and_creates_no_session(client):
    with _db() as c:
        before = c.execute("SELECT count(*) FROM sessions").fetchone()[0]

    r = client.post(ISSUE_URL)
    assert r.status_code == 400
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert "save_code" not in body
    assert _session_set_cookies(r) == []  # 쿠키 발급 없음

    with _db() as c:
        after = c.execute("SELECT count(*) FROM sessions").fetchone()[0]
    assert after == before  # 세션 생성 없음


def test_issue_for_banned_session_is_banned_and_mints_no_code(client):
    sid = _banned_session(client)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ISSUE_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "banned"
    assert body["ban_reason"]
    assert "save_code" not in body
    assert _db_save_code(sid) is None  # 코드 미발급


def test_reissue_returns_wellformed_redeemable_code(client):
    """재발급 동작(기존 코드 반환 vs 재민팅)은 구현 재량 — redeem 가능성만 pin."""
    r0 = client.post(BOOTSTRAP_URL)  # 세션 + 오프닝 (턴 ≥ 1)
    assert r0.json()["status"] == "new"
    sid = r0.json()["session_uuid"]

    r1 = client.post(ISSUE_URL)
    assert r1.status_code == 200
    r2 = client.post(ISSUE_URL)
    assert r2.status_code == 200
    code2 = r2.json()["save_code"]
    assert SAVE_CODE_RE.fullmatch(code2)

    client.cookies.clear()  # 다른 클라이언트 흉내
    rr = client.post(REDEEM_URL, json={"code": code2})
    assert rr.status_code == 200
    assert rr.json()["status"] == "resumed"
    assert rr.json()["session_uuid"] == sid


# --------------------------------------------------------------- redeem: 성공

def test_redeem_session_with_turns_resumes_and_rebinds_cookie(client):
    sid_a = _session_with_turns(client)
    _set_save_code(sid_a, "ABCD-EFGH")

    # 다른 쿠키를 가진 클라이언트 — 재바인딩이 기존 쿠키를 덮어써야 함.
    rb = client.post(BOOTSTRAP_URL)
    sid_b = rb.json()["session_uuid"]
    assert sid_b != sid_a

    r = client.post(REDEEM_URL, json={"code": "ABCD-EFGH"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "resumed"
    assert body["session_uuid"] == sid_a
    assert body["npc_id"] == NPC_ID
    assert body["history"]
    for msg in body["history"]:
        assert msg["role"] in ("user", "assistant")
        assert msg["content"]
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]
    assert _session_set_cookies(r)  # 성공 → 재바인딩

    # 재바인딩 확인 — 이후 bootstrap 이 그 세션으로 이어진다.
    rb2 = client.post(BOOTSTRAP_URL)
    assert rb2.json()["status"] == "resumed"
    assert rb2.json()["session_uuid"] == sid_a


def test_redeem_zero_turn_session_is_new_with_opening_and_rebinds(client):
    sid = _zero_turn_session()
    _set_save_code(sid, "PQRS-TUVW")

    r = client.post(REDEEM_URL, json={"code": "PQRS-TUVW"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert body["session_uuid"] == sid
    assert body["npc_id"] == NPC_ID
    assert body["reply"]  # 오프닝 생성 — 내용은 단언하지 않음
    assert body["choices"]
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]
    assert _session_set_cookies(r)  # 성공 → 재바인딩

    rb = client.post(BOOTSTRAP_URL)
    assert rb.json()["status"] == "resumed"
    assert rb.json()["session_uuid"] == sid


# --------------------------------------------------------------- redeem: 실패

def test_redeem_unknown_code_is_404_and_keeps_existing_session(client):
    rb = client.post(BOOTSTRAP_URL)
    sid_b = rb.json()["session_uuid"]

    r = client.post(REDEEM_URL, json={"code": "ZZZZ-ZZZZ"})  # 형식은 유효, 미지의 코드
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert _session_set_cookies(r) == []  # 쿠키 변경 없음

    rb2 = client.post(BOOTSTRAP_URL)  # 기존 세션 유지
    assert rb2.json()["status"] == "resumed"
    assert rb2.json()["session_uuid"] == sid_b


def test_redeem_malformed_code_is_404_error(client):
    r = client.post(REDEEM_URL, json={"code": "not-a-code"})
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert _session_set_cookies(r) == []


def test_redeem_banned_session_code_is_banned_without_rebinding(client):
    sid_a = _banned_session(client)
    _set_save_code(sid_a, "JKMN-2345")

    rb = client.post(BOOTSTRAP_URL)
    sid_b = rb.json()["session_uuid"]

    r = client.post(REDEEM_URL, json={"code": "JKMN-2345"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "banned"
    assert body["ban_reason"]
    for key in ("reply", "choices", "history"):
        assert key not in body
    assert _session_set_cookies(r) == []  # 재바인딩 없음

    rb2 = client.post(BOOTSTRAP_URL)  # 기존 세션 무변경
    assert rb2.json()["status"] == "resumed"
    assert rb2.json()["session_uuid"] == sid_b


def test_redeem_zero_turn_opening_failure_is_503_and_keeps_cookie(client, monkeypatch):
    sid_a = _zero_turn_session()
    _set_save_code(sid_a, "WXYZ-6789")

    rb = client.post(BOOTSTRAP_URL)  # 기존 세션 B (턴 ≥ 1)
    sid_b = rb.json()["session_uuid"]

    _raising_llm(monkeypatch)
    r = client.post(REDEEM_URL, json={"code": "WXYZ-6789"})
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert _session_set_cookies(r) == []  # 쿠키 무변경

    # resumed 는 LLM 없이 동작 — 기존 세션 B 그대로.
    rb2 = client.post(BOOTSTRAP_URL)
    assert rb2.json()["status"] == "resumed"
    assert rb2.json()["session_uuid"] == sid_b
