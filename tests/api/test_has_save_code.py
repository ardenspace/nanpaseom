"""B2b 세션 진입 응답의 ``has_save_code`` 계약 (Phase 4 step 1 boundary pin).

계약 요약:

- 세션 진입 wire shape *전체* 에 불리언 ``has_save_code`` 가 실린다 — 이 세션에
  유효한 세이브 코드가 있는지. bootstrap 과 redeem 의 성공 응답(new/resumed)은
  같은 shape 를 공유하므로 **둘 다** 싣는다.
- 가산적 변경: 기존 필드(status/npc_id/reply/choices/history)는 그대로.
- 세션 식별자는 여전히 본문에 없다 (B6 — 신원은 쿠키로만).
- 진입 응답의 값이 그 시점의 진실이다. 세션 도중 값이 바뀌는 경로는 발급(B2)과
  회전(B1) 뿐이고, 두 응답 모두 코드를 돌려주므로 클라이언트는 추가 왕복 없이
  참으로 간주한다 (그 클라이언트 규칙은 frontend/src/App.saveCodeNudge.test.tsx 소유).

미pin (의도적):

- banned / 503 error 응답 — 세션 *진입* 응답(new/resumed)이 아니므로 계약이
  이 필드를 요구하지 않는다. 실으냐 마느냐는 구현 재량.
- ``POST /save-code`` · ``POST /save-code/rotate`` 응답 shape — 이 계약의 대상이
  아니다 (그 두 경로는 save_code 자체를 돌려준다).
"""

from tests.api.conftest import (
    known_session,
    session_cookie_value,
    set_save_code,
)

BOOTSTRAP_URL = "/session/bootstrap"
ISSUE_URL = "/save-code"
ROTATE_URL = "/save-code/rotate"
REDEEM_URL = "/save-code/redeem"
COOKIE_NAME = "session_uuid"
NPC_ID = "surigong"

CODE_A = "ABCD-EFGH"
CODE_B = "PQRS-TUVW"


def _assert_no_session_identifier(response) -> None:
    """자격증명은 어떤 진입 응답 본문에도 없다 — 필드명으로도, 값으로도."""
    body = response.json()
    assert "session_uuid" not in body
    sid = session_cookie_value(response)
    if sid is not None:
        assert sid not in response.text


# ------------------------------------------------------- bootstrap: 코드 없음

def test_bootstrap_new_session_reports_no_save_code(client):
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert body["has_save_code"] is False


def test_bootstrap_resumed_session_without_code_reports_false(client):
    sid = known_session(turns=1)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "resumed"
    assert body["has_save_code"] is False


# -------------------------------------------------------- bootstrap: 코드 보유

def test_bootstrap_resumed_session_with_code_reports_true(client):
    sid = known_session(turns=1)
    set_save_code(sid, CODE_A)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "resumed"
    assert body["has_save_code"] is True


def test_bootstrap_zero_turn_session_with_code_is_new_and_reports_true(client):
    """코드 보유는 new/resumed 분기와 독립 — 0턴 세션도 코드를 가질 수 있다
    (redeem 으로 만들어진 0턴 세션이 실제로 그렇다)."""
    sid = known_session(turns=0)
    set_save_code(sid, CODE_B)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert body["has_save_code"] is True


def test_bootstrap_after_issue_reports_true(client):
    """발급 엔드포인트 경유 — 다음 진입의 값이 그 시점의 진실이다."""
    r0 = client.post(BOOTSTRAP_URL)
    assert r0.json()["has_save_code"] is False

    ri = client.post(ISSUE_URL)
    assert ri.status_code == 200
    assert ri.json()["status"] == "ok"

    r1 = client.post(BOOTSTRAP_URL)
    assert r1.status_code == 200
    assert r1.json()["has_save_code"] is True


def test_bootstrap_after_rotate_still_reports_true(client):
    """회전은 코드를 갈아끼울 뿐 — 보유 상태는 그대로 참."""
    client.post(BOOTSTRAP_URL)
    client.post(ISSUE_URL)
    rr = client.post(ROTATE_URL)
    assert rr.status_code == 200
    assert rr.json()["status"] == "ok"

    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    assert r.json()["has_save_code"] is True


# ------------------------------------------------------------------- redeem

def test_redeem_resumed_reports_true(client):
    """코드로 들어온 세션은 정의상 코드를 보유한다 — redeem 성공도 같은 필드를 싣는다."""
    set_save_code(known_session(turns=1), CODE_A)

    r = client.post(REDEEM_URL, json={"code": CODE_A})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "resumed"
    assert body["has_save_code"] is True


def test_redeem_zero_turn_new_reports_true(client):
    set_save_code(known_session(turns=0), CODE_B)

    r = client.post(REDEEM_URL, json={"code": CODE_B})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "new"
    assert body["has_save_code"] is True


# --------------------------------------------------- 가산성 (기존 필드 불변)

def test_new_payload_fields_are_unchanged(client):
    """추가는 가산적 — new 의 기존 필드는 값까지 그대로다."""
    r = client.post(BOOTSTRAP_URL)
    body = r.json()
    assert body["status"] == "new"
    assert body["npc_id"] == NPC_ID
    assert body["reply"]  # 오프닝 대사 — 내용은 단언하지 않음
    assert body["choices"]
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]
    assert "history" not in body
    assert isinstance(body["has_save_code"], bool)


def test_resumed_payload_fields_are_unchanged(client):
    sid = known_session(turns=1)
    set_save_code(sid, CODE_A)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(BOOTSTRAP_URL)
    body = r.json()
    assert body["status"] == "resumed"
    assert body["npc_id"] == NPC_ID
    assert body["history"]
    for msg in body["history"]:
        assert msg["role"] in ("user", "assistant")
        assert msg["content"]
    assert len(body["choices"]) == 3
    for ch in body["choices"]:
        assert ch["tone"] and ch["text"]
    assert "reply" not in body
    assert isinstance(body["has_save_code"], bool)


def test_redeem_payload_fields_are_unchanged(client):
    set_save_code(known_session(turns=1), CODE_A)

    r = client.post(REDEEM_URL, json={"code": CODE_A})
    body = r.json()
    assert body["status"] == "resumed"
    assert body["npc_id"] == NPC_ID
    assert body["history"]
    assert len(body["choices"]) == 3
    assert isinstance(body["has_save_code"], bool)


# -------------------------------------------- 신원은 여전히 본문에 없다 (B6)

def test_entry_responses_still_carry_no_session_identifier(client):
    # new
    r_new = client.post(BOOTSTRAP_URL)
    assert r_new.json()["status"] == "new"
    _assert_no_session_identifier(r_new)

    # resumed
    r_resumed = client.post(BOOTSTRAP_URL)
    assert r_resumed.json()["status"] == "resumed"
    _assert_no_session_identifier(r_resumed)

    # redeem 성공
    set_save_code(known_session(turns=1), CODE_A)
    r_redeem = client.post(REDEEM_URL, json={"code": CODE_A})
    assert r_redeem.json()["status"] == "resumed"
    _assert_no_session_identifier(r_redeem)
