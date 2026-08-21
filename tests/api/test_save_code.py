"""B3 세이브 코드 발급/입력 계약 (이 모듈이 URL/필드명을 확정 — Phase 3 boundary pin).

계약 요약:

- 코드 형식: ``XXXX-XXXX`` 9자 (하이픈 포함, VARCHAR(9)). 알파벳 = A-Z·2-9 에서
  혼동 문자(O/I/L/0/1) 제외 — 단일 정의 ``app/save_code.py`` (테스트는 그 regex 로 pin.
  PREFIX 단어 목록 등 생성 전략은 구현 재량).

- 발급: ``POST /save-code`` — request body 없음, **쿠키가 신원** (``session_uuid``).
  - 200 ``{status: "ok", save_code}`` — save_code 는 형식 만족 + ``sessions.save_code``
    (UNIQUE) 에 저장됨.
  - 쿠키 없음/형식 불량/모르는 세션 → 401 ``{status: "error", message}``.
    세션 생성/쿠키 발급 없음 (Phase 2 B3 — 401 게이트 상세는
    test_surface_hardening.py 가 pin).
  - 밴 세션 → 200 ``{status: "banned", ban_reason}``. 코드 미발급 (DB NULL 유지).
  - 재발급(이미 코드 있는 세션): 기존 코드 반환 (idempotent — Phase 2 B3,
    test_surface_hardening.py 가 pin). 여기서는 "200 + 형식 만족 + 그 코드로
    redeem 가능" 을 pin.

- 입력(redeem): ``POST /save-code/redeem`` — body ``{"code": str}``.
  대상 세션 상태에 따라 bootstrap 과 동일 시맨틱 (B1 이후 **본문에 session_uuid
  없음** — 어느 세션으로 이어졌는지는 Set-Cookie/후속 bootstrap 으로 관찰):
  - 턴 ≥ 1 → 200 ``{status: "resumed", npc_id, history, choices}``
  - 턴 0개 → 200 ``{status: "new", npc_id, reply, choices}`` (오프닝 생성)
  - 쿠키 재바인딩(Set-Cookie)은 **성공 응답(new/resumed)과 함께만** — 이후 bootstrap 이
    그 세션으로 이어진다.
  - 잘못된/미지의 코드 → 404 ``{status: "error", message}``. 쿠키/기존 세션 무변경.
  - 밴 세션의 코드 → 200 ``{status: "banned", ban_reason}``. **재바인딩 없음**,
    기존 세션 무변경.
  - 턴 0개 + 오프닝 생성 실패 → 503 ``{status: "error", message}``. 쿠키 무변경.
"""

from app.api.session_cookie import SESSION_COOKIE_MAX_AGE
from app.save_code import (
    SAVE_CODE_LENGTH,
    SAVE_CODE_PREFIX_WORDS,
    SAVE_CODE_RE,
    generate_save_code,
)
from tests.api.conftest import (
    banned_session,
    db_conn,
    db_save_code,
    known_session,
    raising_llm,
    session_cookie_value,
    set_save_code,
)

ISSUE_URL = "/save-code"
REDEEM_URL = "/save-code/redeem"
BOOTSTRAP_URL = "/session/bootstrap"
COOKIE_NAME = "session_uuid"
NPC_ID = "surigong"


# ------------------------------------------------------------------- helpers

def _session_set_cookies(response) -> list[str]:
    """응답이 session_uuid 쿠키를 심는지 — 재바인딩 유무 단언용."""
    return [
        h for h in response.headers.get_list("set-cookie")
        if h.strip().startswith(f"{COOKIE_NAME}=")
    ]


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
    sid = known_session(turns=1)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ISSUE_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    code = body["save_code"]
    assert len(code) == SAVE_CODE_LENGTH
    assert SAVE_CODE_RE.fullmatch(code)  # 4자-4자, 허용 알파벳 (O/I/L/0/1 없음)
    assert db_save_code(sid) == code  # UNIQUE 컬럼에 저장됨


def test_issue_without_cookie_is_error_and_creates_no_session(client):
    with db_conn() as c:
        before = c.execute("SELECT count(*) FROM sessions").fetchone()[0]

    r = client.post(ISSUE_URL)
    assert r.status_code == 401
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert "save_code" not in body
    assert _session_set_cookies(r) == []  # 쿠키 발급 없음

    with db_conn() as c:
        after = c.execute("SELECT count(*) FROM sessions").fetchone()[0]
    assert after == before  # 세션 생성 없음


def test_issue_for_banned_session_is_banned_and_mints_no_code(client):
    sid = banned_session()
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ISSUE_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "banned"
    assert body["ban_reason"]
    assert "save_code" not in body
    assert db_save_code(sid) is None  # 코드 미발급


def test_reissue_returns_wellformed_redeemable_code(client):
    """재발급은 기존 코드 반환 (idempotent — test_surface_hardening.py 가 pin).
    여기서는 재발급된 코드의 redeem 가능성만 pin."""
    r0 = client.post(BOOTSTRAP_URL)  # 세션 + 오프닝 (턴 ≥ 1)
    assert r0.json()["status"] == "new"
    sid = session_cookie_value(r0)

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
    assert session_cookie_value(rr) == sid  # 그 세션으로 재바인딩


# --------------------------------------------------------------- redeem: 성공

def test_redeem_session_with_turns_resumes_and_rebinds_cookie(client):
    sid_a = known_session(turns=1)
    set_save_code(sid_a, "ABCD-EFGH")

    # 다른 쿠키를 가진 클라이언트 — 재바인딩이 기존 쿠키를 덮어써야 함.
    rb = client.post(BOOTSTRAP_URL)
    sid_b = session_cookie_value(rb)
    assert sid_b != sid_a

    r = client.post(REDEEM_URL, json={"code": "ABCD-EFGH"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "resumed"
    assert body["npc_id"] == NPC_ID
    assert "session_uuid" not in body  # 자격증명은 응답 본문에 없다
    assert body["history"]
    for msg in body["history"]:
        assert msg["role"] in ("user", "assistant")
        assert msg["content"]
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]
    rebind_cookies = _session_set_cookies(r)
    assert rebind_cookies  # 성공 → 재바인딩
    assert session_cookie_value(r) == sid_a
    for h in rebind_cookies:  # 재바인딩 쿠키도 장수 (session cookie 금지)
        assert f"Max-Age={SESSION_COOKIE_MAX_AGE}" in h

    # 재바인딩 확인 — 이후 bootstrap 이 그 세션으로 이어진다.
    rb2 = client.post(BOOTSTRAP_URL)
    assert rb2.json()["status"] == "resumed"
    assert session_cookie_value(rb2) == sid_a


def test_redeem_zero_turn_session_is_new_with_opening_and_rebinds(client):
    sid = known_session(turns=0)
    set_save_code(sid, "PQRS-TUVW")

    r = client.post(REDEEM_URL, json={"code": "PQRS-TUVW"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert body["npc_id"] == NPC_ID
    assert "session_uuid" not in body
    assert body["reply"]  # 오프닝 생성 — 내용은 단언하지 않음
    assert body["choices"]
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]
    rebind_cookies = _session_set_cookies(r)
    assert rebind_cookies  # 성공 → 재바인딩
    assert session_cookie_value(r) == sid
    for h in rebind_cookies:  # 재바인딩 쿠키도 장수 (session cookie 금지)
        assert f"Max-Age={SESSION_COOKIE_MAX_AGE}" in h

    rb = client.post(BOOTSTRAP_URL)
    assert rb.json()["status"] == "resumed"
    assert session_cookie_value(rb) == sid


# --------------------------------------------------------------- redeem: 실패

def test_redeem_unknown_code_is_404_and_keeps_existing_session(client):
    rb = client.post(BOOTSTRAP_URL)
    sid_b = session_cookie_value(rb)

    r = client.post(REDEEM_URL, json={"code": "ZZZZ-ZZZZ"})  # 형식은 유효, 미지의 코드
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert _session_set_cookies(r) == []  # 쿠키 변경 없음

    rb2 = client.post(BOOTSTRAP_URL)  # 기존 세션 유지
    assert rb2.json()["status"] == "resumed"
    assert session_cookie_value(rb2) == sid_b


def test_redeem_malformed_code_is_404_error(client):
    r = client.post(REDEEM_URL, json={"code": "not-a-code"})
    assert r.status_code == 404
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert _session_set_cookies(r) == []


def test_redeem_banned_session_code_is_banned_without_rebinding(client):
    sid_a = banned_session()
    set_save_code(sid_a, "JKMN-2345")

    rb = client.post(BOOTSTRAP_URL)
    sid_b = session_cookie_value(rb)

    r = client.post(REDEEM_URL, json={"code": "JKMN-2345"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "banned"
    assert body["ban_reason"]
    for key in ("reply", "choices", "history", "session_uuid"):
        assert key not in body
    assert _session_set_cookies(r) == []  # 재바인딩 없음

    rb2 = client.post(BOOTSTRAP_URL)  # 기존 세션 무변경
    assert rb2.json()["status"] == "resumed"
    assert session_cookie_value(rb2) == sid_b


def test_redeem_zero_turn_opening_failure_is_503_and_keeps_cookie(client, monkeypatch):
    sid_a = known_session(turns=0)
    set_save_code(sid_a, "WXYZ-6789")

    rb = client.post(BOOTSTRAP_URL)  # 기존 세션 B (턴 ≥ 1)
    sid_b = session_cookie_value(rb)

    raising_llm(monkeypatch)
    r = client.post(REDEEM_URL, json={"code": "WXYZ-6789"})
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "error"
    assert body["message"]
    assert _session_set_cookies(r) == []  # 쿠키 무변경

    # resumed 는 LLM 없이 동작 — 기존 세션 B 그대로.
    rb2 = client.post(BOOTSTRAP_URL)
    assert rb2.json()["status"] == "resumed"
    assert session_cookie_value(rb2) == sid_b
