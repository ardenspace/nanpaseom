"""B1·B2·B6·B7 신원 계약 박제 (Phase 1 boundary pin — 이 모듈이 새 계약을 확정).

계약 요약 (spec.md 동결 원문 기준):

- B1 ``POST /turn``: 요청 본문은 ``{npc_id, player_input}`` 뿐. 본문의 세션 번호
  필드(구 ``session_uuid``)는 와도 무시. 신원은 **쿠키 ``session_uuid`` 만** —
  쿠키 없음 / UUID 형식 아님 / 모르는 세션 → ``401 {status:"error", message}``,
  세션 생성 없음. 신원 판정이 npc_id 검증보다 먼저. ``npc_id`` 는 런타임에
  배선된 NPC 목록 검증(현재 수리공 단독 — yaml 존재만으로는 불충분) → 404.
  응답 본문에서 ``session_uuid`` 제거.
- B2 ``POST /session/bootstrap``: 유일한 세션 생성 문. 쿠키 없음/형식 불량/모르는
  세션 → 클라이언트 값은 버리고 **서버가 새 UUID 민팅** (스테일 쿠키 채택 폐지).
  0턴 재진입 = new + 같은 세션 재사용, 503 에도 세션 존속 + Set-Cookie, banned
  포함 모든 status 에 Set-Cookie (이상 현행 유지). 응답 본문에 session_uuid 없음.
- B6 세션 쿠키: ``HttpOnly; Secure; SameSite=Lax; Max-Age=15552000; Path=/``.
  env 플래그(이 모듈이 ``NANPASEOM_INSECURE_COOKIE`` 로 확정)가 켜진 경우에만
  Secure 생략. 발급 전 표면(bootstrap 4종 + redeem 성공 rebind) 커버.
  자격증명 session_uuid 는 **어떤 응답 본문에도 싣지 않는다** (redeem 포함).
- B7 해석기: 쿠키 인증 엔드포인트(/turn, /save-code)의 신원 판정은 세션을 절대
  만들지 않는다 — 행동 관찰로 박제 (모르는 세션 → 거부 + sessions 행 미생성).
  /save-code 의 401 게이트 자체는 Phase 2 (B3) 소관 — 여기서는 미생성만.

Max-Age 는 계약 리터럴 15552000 (180일) 을 직접 pin — 구현 상수 import 는
동어반복이라 하지 않는다.
"""

import uuid

from app.store import repo
from tests.api.conftest import (
    cookie_value,
    count_sessions,
    db_conn,
    known_session,
    raising_llm,
    session_cookie_headers,
    session_row_exists,
)

TURN_URL = "/turn"
BOOTSTRAP_URL = "/session/bootstrap"
ISSUE_URL = "/save-code"
REDEEM_URL = "/save-code/redeem"
COOKIE_NAME = "session_uuid"
NPC_ID = "surigong"
SESSION_COOKIE_MAX_AGE = 15552000  # 180일 — B6 계약 리터럴
INSECURE_COOKIE_ENV = "NANPASEOM_INSECURE_COOKIE"  # 켜진 경우에만 Secure 생략


# ------------------------------------------------------------------- helpers

def _count_chat_logs(sid: str) -> int:
    with db_conn() as c:
        return c.execute(
            "SELECT count(*) FROM chat_logs WHERE session_uuid = %s", (sid,)
        ).fetchone()[0]


def _banned_session() -> str:
    sid = known_session(turns=2)
    with db_conn() as c:
        repo.ban_session(c, sid, "누적 경고로 대화가 차단됐습니다.")
    return sid


def _set_save_code(sid: str, code: str) -> None:
    with db_conn() as c:
        c.execute("UPDATE sessions SET save_code = %s WHERE session_uuid = %s", (code, sid))


def _cookie_attrs(header: str) -> dict[str, str | None]:
    """Set-Cookie 속성을 소문자 키 dict 로 (값 없는 속성은 None)."""
    attrs: dict[str, str | None] = {}
    for part in header.split(";")[1:]:
        key, sep, val = part.strip().partition("=")
        attrs[key.lower()] = val.strip() if sep else None
    return attrs


def _assert_full_secure_cookie(response) -> None:
    """B6 — 속성 4종 + Path + 서버 민팅 UUID 값. 발급 전 표면에 공통 적용."""
    headers = session_cookie_headers(response)
    assert headers, "session_uuid Set-Cookie 가 없다"
    for h in headers:
        uuid.UUID(cookie_value(h))  # 값 = 서버가 민팅한 UUID 문자열
        attrs = _cookie_attrs(h)
        assert "httponly" in attrs
        assert "secure" in attrs
        assert (attrs.get("samesite") or "").lower() == "lax"
        assert attrs.get("max-age") == str(SESSION_COOKIE_MAX_AGE)
        assert attrs.get("path") == "/"


def _turn(client, player_input: str = "보트 수리 잘 돼?", npc_id: str = NPC_ID, **extra):
    return client.post(TURN_URL, json={"npc_id": npc_id, "player_input": player_input, **extra})


def _assert_401_error(response) -> None:
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert body["message"]  # 솔직한 시스템 톤 — 내용은 단언하지 않음 (서식지는 rules YAML)
    assert session_cookie_headers(response) == []  # 401 은 쿠키를 심지 않는다


# --------------------------------------------------- B1: /turn 쿠키 단일 신원

def test_turn_without_cookie_is_401_and_creates_no_session(client):
    before = count_sessions()
    r = _turn(client)
    _assert_401_error(r)
    assert count_sessions() == before  # 세션 생성 없음


def test_turn_with_non_uuid_cookie_is_401_and_creates_no_session(client):
    before = count_sessions()
    client.cookies.set(COOKIE_NAME, "not-a-uuid")
    _assert_401_error(_turn(client))
    assert count_sessions() == before


def test_turn_with_unknown_session_cookie_is_401_and_no_session_row(client):
    ghost = str(uuid.uuid4())  # UUID 형식은 유효, 서버가 모르는 세션
    client.cookies.set(COOKIE_NAME, ghost)
    _assert_401_error(_turn(client))
    assert not session_row_exists(ghost)  # B7 — 해석기는 세션을 만들지 않는다


def test_turn_without_cookie_is_401_even_with_valid_body_session_uuid(client):
    """남의 세션 번호를 본문에 실어도 신원이 되지 않는다 (curl 위조 차단)."""
    victim = known_session(turns=1)
    r = _turn(client, session_uuid=victim)
    _assert_401_error(r)
    assert _count_chat_logs(victim) == 2  # 남의 세션에 턴이 적히지 않았다


def test_turn_ignores_body_session_uuid_and_uses_cookie_identity(client):
    mine = known_session()
    other = known_session()
    client.cookies.set(COOKIE_NAME, mine)

    r = _turn(client, session_uuid=other)
    assert r.status_code == 200
    assert _count_chat_logs(mine) == 2  # 턴은 쿠키 세션에 적힌다 (user+assistant)
    assert _count_chat_logs(other) == 0  # 본문 필드는 신원에 사용되지 않는다


def test_turn_identity_check_precedes_npc_validation(client):
    """무인증 요청은 npc_id 가 뭐든 401 — 404 로 NPC 목록을 노출하지 않는다."""
    r = _turn(client, npc_id="no-such-npc")
    _assert_401_error(r)


def test_turn_unknown_npc_id_is_404(client):
    client.cookies.set(COOKIE_NAME, known_session())
    r = _turn(client, npc_id="no-such-npc")
    assert r.status_code == 404


def test_turn_unwired_yaml_npc_is_404(client):
    """"아는 NPC" = 런타임에 배선된 NPC (수리공 단독) — yaml 존재만으로는 불충분."""
    client.cookies.set(COOKIE_NAME, known_session())
    r = _turn(client, npc_id="eobu")  # npcs/eobu.yaml 은 존재하지만 미배선
    assert r.status_code == 404


def test_turn_response_body_has_no_session_uuid(client):
    client.cookies.set(COOKIE_NAME, known_session())
    r = _turn(client)
    assert r.status_code == 200
    body = r.json()
    assert body["kind"] == "npc"
    assert body["reply"]
    assert "session_uuid" not in body  # B6 — 자격증명은 어떤 응답 본문에도 없다


def test_turn_strike_and_ban_responses_have_no_session_uuid(client):
    client.cookies.set(COOKIE_NAME, known_session())
    r1 = _turn(client, player_input="이 씨발아")
    assert r1.json()["kind"] == "warning"
    assert "session_uuid" not in r1.json()

    r2 = _turn(client, player_input="개새끼")
    assert r2.json()["kind"] == "ban"
    assert "session_uuid" not in r2.json()


# ----------------------------------------- B2: bootstrap 서버 전용 세션 민팅

def test_bootstrap_unknown_cookie_is_discarded_and_server_mints_new(client):
    """클라이언트가 고른 값이 세션 행이 되는 일은 없다 — 스테일 쿠키 채택 폐지."""
    forged = str(uuid.uuid4())
    client.cookies.set(COOKIE_NAME, forged)
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    assert r.json()["status"] == "new"

    headers = session_cookie_headers(r)
    assert headers
    minted = cookie_value(headers[0])
    uuid.UUID(minted)
    assert minted != forged  # 클라이언트 값은 버려진다
    assert session_row_exists(minted)
    assert not session_row_exists(forged)  # 위조 값으로 행이 생기지 않는다


def test_bootstrap_malformed_cookie_is_discarded_and_server_mints_new(client):
    client.cookies.set(COOKIE_NAME, "totally-not-a-uuid")
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    assert r.json()["status"] == "new"
    minted = cookie_value(session_cookie_headers(r)[0])
    uuid.UUID(minted)  # 서버 민팅 UUID
    assert session_row_exists(minted)


def test_bootstrap_zero_turn_known_session_reenters_as_new_reusing_session(client):
    """현행 유지 pin — 아는 세션 + 턴 0개 → 오프닝 (재)시도, 같은 세션 재사용."""
    sid = known_session(turns=0)
    client.cookies.set(COOKIE_NAME, sid)
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    assert r.json()["status"] == "new"
    assert cookie_value(session_cookie_headers(r)[0]) == sid


def test_bootstrap_503_keeps_session_row_and_sets_cookie(client, monkeypatch):
    """현행 유지 pin — 오프닝 실패 503 에도 민팅된 세션은 존속 + Set-Cookie."""
    raising_llm(monkeypatch)
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 503
    assert r.json()["status"] == "error"
    headers = session_cookie_headers(r)
    assert headers
    assert session_row_exists(cookie_value(headers[0]))  # 재시도 시 같은 세션 재사용


def test_bootstrap_banned_status_still_sets_cookie(client):
    """현행 유지 pin — banned 칸 포함 모든 status 응답에 Set-Cookie."""
    client.cookies.set(COOKIE_NAME, _banned_session())
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 200
    assert r.json()["status"] == "banned"
    assert session_cookie_headers(r)


def test_bootstrap_new_body_has_no_session_uuid(client):
    r = client.post(BOOTSTRAP_URL)
    body = r.json()
    assert body["status"] == "new"
    assert body["reply"] and body["choices"]
    assert "session_uuid" not in body


def test_bootstrap_resumed_body_has_no_session_uuid(client):
    client.cookies.set(COOKIE_NAME, known_session(turns=1))
    r = client.post(BOOTSTRAP_URL)
    body = r.json()
    assert body["status"] == "resumed"
    assert body["history"]
    assert "session_uuid" not in body


def test_bootstrap_banned_body_has_no_session_uuid(client):
    client.cookies.set(COOKIE_NAME, _banned_session())
    body = client.post(BOOTSTRAP_URL).json()
    assert body["status"] == "banned"
    assert body["ban_reason"]
    assert "session_uuid" not in body


def test_bootstrap_503_body_has_no_session_uuid(client, monkeypatch):
    raising_llm(monkeypatch)
    body = client.post(BOOTSTRAP_URL).json()
    assert body["status"] == "error"
    assert "session_uuid" not in body


# ------------------------------- B6: 쿠키 속성 4종 — 발급 전 표면 conformance

def test_bootstrap_new_cookie_has_all_security_attributes(client, monkeypatch):
    monkeypatch.delenv(INSECURE_COOKIE_ENV, raising=False)  # 기본값 = 항상 Secure
    _assert_full_secure_cookie(client.post(BOOTSTRAP_URL))


def test_bootstrap_resumed_cookie_has_all_security_attributes(client, monkeypatch):
    monkeypatch.delenv(INSECURE_COOKIE_ENV, raising=False)
    client.cookies.set(COOKIE_NAME, known_session(turns=1))
    r = client.post(BOOTSTRAP_URL)
    assert r.json()["status"] == "resumed"
    _assert_full_secure_cookie(r)


def test_bootstrap_banned_cookie_has_all_security_attributes(client, monkeypatch):
    monkeypatch.delenv(INSECURE_COOKIE_ENV, raising=False)
    client.cookies.set(COOKIE_NAME, _banned_session())
    r = client.post(BOOTSTRAP_URL)
    assert r.json()["status"] == "banned"
    _assert_full_secure_cookie(r)


def test_bootstrap_503_cookie_has_all_security_attributes(client, monkeypatch):
    monkeypatch.delenv(INSECURE_COOKIE_ENV, raising=False)
    raising_llm(monkeypatch)
    r = client.post(BOOTSTRAP_URL)
    assert r.status_code == 503
    _assert_full_secure_cookie(r)


def test_redeem_resumed_rebind_cookie_has_all_security_attributes(client, monkeypatch):
    """발급 단일 경로 계약 — redeem 성공 rebind 도 같은 속성 4종을 받는다."""
    monkeypatch.delenv(INSECURE_COOKIE_ENV, raising=False)
    sid = known_session(turns=1)
    _set_save_code(sid, "QRST-2345")
    r = client.post(REDEEM_URL, json={"code": "QRST-2345"})
    assert r.status_code == 200
    assert r.json()["status"] == "resumed"
    _assert_full_secure_cookie(r)


def test_redeem_new_rebind_cookie_has_all_security_attributes(client, monkeypatch):
    monkeypatch.delenv(INSECURE_COOKIE_ENV, raising=False)
    sid = known_session(turns=0)
    _set_save_code(sid, "BCDE-FGHJ")
    r = client.post(REDEEM_URL, json={"code": "BCDE-FGHJ"})
    assert r.status_code == 200
    assert r.json()["status"] == "new"
    _assert_full_secure_cookie(r)


def test_insecure_env_flag_omits_only_secure(client, monkeypatch):
    """로컬 개발 예외 하나 — 플래그가 켜진 경우에만 Secure 생략, 나머지 속성 유지."""
    monkeypatch.setenv(INSECURE_COOKIE_ENV, "1")
    r = client.post(BOOTSTRAP_URL)
    headers = session_cookie_headers(r)
    assert headers
    for h in headers:
        attrs = _cookie_attrs(h)
        assert "secure" not in attrs
        assert "httponly" in attrs
        assert (attrs.get("samesite") or "").lower() == "lax"
        assert attrs.get("max-age") == str(SESSION_COOKIE_MAX_AGE)
        assert attrs.get("path") == "/"


def test_redeem_success_bodies_have_no_session_uuid(client):
    """자격증명은 redeem 응답 본문에도 없다 (기기 이동은 쿠키 rebind 로 이어진다)."""
    sid = known_session(turns=1)
    _set_save_code(sid, "MNPQ-6789")
    body = client.post(REDEEM_URL, json={"code": "MNPQ-6789"}).json()
    assert body["status"] == "resumed"
    assert "session_uuid" not in body

    client.cookies.clear()
    sid0 = known_session(turns=0)
    _set_save_code(sid0, "TUVW-2346")
    body0 = client.post(REDEEM_URL, json={"code": "TUVW-2346"}).json()
    assert body0["status"] == "new"
    assert "session_uuid" not in body0


# --------------------------- B7: 해석기는 세션을 만들지 않는다 (행동 관찰 박제)

def test_save_code_issue_with_unknown_cookie_creates_no_session_row(client):
    """B7 최소 박제 — /save-code 신원 판정도 세션을 만들지 않는다.

    발급 게이트의 응답 계약(401 등)은 Phase 2 (B3) 소관 — 여기서는 미생성만.
    """
    ghost = str(uuid.uuid4())
    client.cookies.set(COOKIE_NAME, ghost)
    client.post(ISSUE_URL)
    assert not session_row_exists(ghost)
