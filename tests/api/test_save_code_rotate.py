"""B1 회전 계약 pin — ``POST /save-code/rotate`` (Phase 2 step 2, 실패 상태로 커밋).

이 파일이 회전 액션의 URL/필드명/부작용을 확정한다. 구현은 다음 스텝.

계약 요약 (spec.md 동결 원문 기준):

- 신원: 해석기(``resolve_session``) 통과분만. 거부(쿠키 없음/형식 불량/모르는 세션)
  → ``401 {status:"error", message}`` — 문구는 발급 401 과 같은 결이라
  ``rules/identity.yaml no_session_message`` 재사용. 세션 생성/쿠키 발급 없음.
- 밴 세션 → ``200 {status:"banned", ban_reason}`` (발급과 동일 결). 회전 없음.
- 성공 → ``200 {status:"ok", save_code}`` — 새 코드. 형식 정의는 ``app/save_code.py`` 불변.
- 관측 계약: 응답 이후 이전 코드는 redeem 404, 새 코드는 redeem 성공. 두 코드가
  동시에 유효한 순간은 없다 (세션당 코드는 ``sessions.save_code`` 한 칸).
- 연속 호출은 매번 새 코드 — **idempotent 아님** (발급과 구분되는 지점).
- ``save_code`` 가 NULL 인 세션의 회전은 에러가 아니라 첫 코드 민팅.
- 무효화된 코드 문자열은 소각되지 않는다 — 이후 민팅에서 재사용될 수 있다.

- B2 회귀: 회전 도입 후에도 발급(``POST /save-code``)의 idempotency 는 깨지지 않는다
  (발급은 여전히 "현재 코드가 있으면 그대로, 없으면 민팅").

프론트 어포던스(채팅 화면에서 회전에 도달 + "이전 코드는 못 쓴다" 명시)는
``frontend/src/App.saveCode.test.tsx`` 가 pin 한다.
스테일 표시(다른 기기/탭에 떠 있는 옛 코드)는 계약이 명시적으로 감수 — 테스트 없음.
"""

import uuid

import pytest

from app.api.identity import load_identity_rules
from app.save_code import SAVE_CODE_RE
from app.store import repo
from tests.api.conftest import (
    banned_session,
    count_sessions,
    db_conn,
    db_save_code,
    known_session,
    session_cookie_headers,
    session_cookie_value,
    set_save_code,
)

ROTATE_URL = "/save-code/rotate"
ISSUE_URL = "/save-code"
REDEEM_URL = "/save-code/redeem"
COOKIE_NAME = "session_uuid"

# 테스트가 심는 알려진 옛 코드 — 형식은 SAVE_CODE_RE 를 만족해야 한다.
OLD_CODE = "ABCD-EFGH"


# ------------------------------------------------------- 신원: 거부는 401, 부작용 0

@pytest.mark.parametrize("cookie", [None, "not-a-uuid", "unknown-uuid"])
def test_rotate_with_rejected_identity_is_401_and_has_no_side_effects(client, cookie):
    """해석기 거부 3종 → 401. 세션 생성도 쿠키 발급도 없다 (발급 401 과 같은 결)."""
    ghost = str(uuid.uuid4())
    if cookie is not None:
        client.cookies.set(COOKIE_NAME, ghost if cookie == "unknown-uuid" else cookie)
    before = count_sessions()

    r = client.post(ROTATE_URL)

    assert r.status_code == 401
    body = r.json()
    assert body["status"] == "error"
    assert body["message"] == load_identity_rules().no_session_message
    assert "save_code" not in body
    assert session_cookie_headers(r) == []  # 쿠키 발급 없음
    assert count_sessions() == before  # 세션 생성 없음


# ---------------------------------------------------------------- 밴: 회전 없음

def test_rotate_for_banned_session_is_banned_and_keeps_the_code(client):
    sid = banned_session()
    set_save_code(sid, OLD_CODE)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ROTATE_URL)

    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "banned"
    assert body["ban_reason"]
    assert "save_code" not in body
    assert db_save_code(sid) == OLD_CODE  # 회전 없음


# ------------------------------------------------------------------- 성공 계약

def test_rotate_returns_a_new_wellformed_code_and_persists_it(client):
    sid = known_session(turns=1)
    set_save_code(sid, OLD_CODE)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ROTATE_URL)

    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    new_code = body["save_code"]
    assert SAVE_CODE_RE.fullmatch(new_code)  # 형식 정의는 불변
    assert new_code != OLD_CODE
    assert db_save_code(sid) == new_code


def test_rotate_on_session_without_a_code_mints_the_first_one(client):
    """코드 미발급(NULL) 세션의 회전은 에러가 아니다 — 무효화할 이전 코드가 없을 뿐."""
    sid = known_session(turns=1)
    assert db_save_code(sid) is None
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ROTATE_URL)

    assert r.status_code == 200
    code = r.json()["save_code"]
    assert SAVE_CODE_RE.fullmatch(code)
    assert db_save_code(sid) == code


# --------------------------------------------------- 관측 계약: 무효화 / 도달 가능성

def test_previous_code_stops_redeeming_and_the_new_one_redeems(client):
    sid = known_session(turns=1)
    set_save_code(sid, OLD_CODE)
    client.cookies.set(COOKIE_NAME, sid)

    new_code = client.post(ROTATE_URL).json()["save_code"]

    client.cookies.clear()  # 다른 클라이언트 흉내 — 코드만으로 판정
    r_old = client.post(REDEEM_URL, json={"code": OLD_CODE})
    assert r_old.status_code == 404
    assert session_cookie_headers(r_old) == []  # 무효화된 코드는 아무것도 재바인딩 안 함

    r_new = client.post(REDEEM_URL, json={"code": new_code})
    assert r_new.status_code == 200
    assert r_new.json()["status"] == "resumed"
    assert session_cookie_value(r_new) == sid  # 같은 세션으로 이어진다


def test_old_and_new_code_are_never_valid_at_the_same_time(client):
    """세션당 유효 코드는 정확히 하나 — 응답 시점에 옛 코드는 이미 어디에도 안 매인다."""
    sid = known_session(turns=1)
    set_save_code(sid, OLD_CODE)
    client.cookies.set(COOKIE_NAME, sid)

    new_code = client.post(ROTATE_URL).json()["save_code"]

    with db_conn() as c:
        assert repo.find_session_by_save_code(c, OLD_CODE) is None
        assert repo.find_session_by_save_code(c, new_code) == sid
        live = c.execute(
            "SELECT count(*) FROM sessions WHERE save_code IN (%s, %s)",
            (OLD_CODE, new_code),
        ).fetchone()[0]
    assert live == 1


def test_consecutive_rotations_return_different_codes(client):
    """회전은 idempotent 가 아니다 — 매 호출이 새 코드 (발급과의 구분점)."""
    sid = known_session(turns=1)
    client.cookies.set(COOKIE_NAME, sid)

    codes = [client.post(ROTATE_URL).json()["save_code"] for _ in range(3)]

    assert len(set(codes)) == 3
    assert db_save_code(sid) == codes[-1]
    client.cookies.clear()
    for stale in codes[:-1]:  # 앞선 코드는 전부 무효
        assert client.post(REDEEM_URL, json={"code": stale}).status_code == 404


def test_invalidated_code_string_is_not_burned(client):
    """무효화는 소각이 아니다 — 그 문자열은 이후 다른 세션의 코드가 될 수 있다."""
    sid_a = known_session(turns=1)
    set_save_code(sid_a, OLD_CODE)
    client.cookies.set(COOKIE_NAME, sid_a)
    client.post(ROTATE_URL)

    sid_b = known_session(turns=1)
    set_save_code(sid_b, OLD_CODE)  # 소각 목록이 있었다면 여기서 막혀야 한다

    client.cookies.clear()
    r = client.post(REDEEM_URL, json={"code": OLD_CODE})
    assert r.status_code == 200
    assert session_cookie_value(r) == sid_b  # 이제 그 문자열은 B 의 코드


# ---------------------------------------------- B2 회귀: 발급 idempotency 는 유지

def test_issue_stays_idempotent_across_a_rotation(client):
    """발급은 회전 후에도 "현재 코드 그대로" — 회전만이 코드를 바꾼다."""
    sid = known_session(turns=1)
    client.cookies.set(COOKIE_NAME, sid)

    first = client.post(ISSUE_URL).json()["save_code"]
    assert client.post(ISSUE_URL).json()["save_code"] == first  # 회전 전 idempotent

    rotated = client.post(ROTATE_URL).json()["save_code"]
    assert rotated != first

    assert client.post(ISSUE_URL).json()["save_code"] == rotated  # 회전 후에도 idempotent
    assert client.post(ISSUE_URL).json()["save_code"] == rotated
    assert db_save_code(sid) == rotated
