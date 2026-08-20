import uuid

from app.safety.moderation import SafetyVerdict
from app.safety import strike
from app.store import repo


def _verdict(term):
    return SafetyVerdict(category="harassment", matched_term=term)


def _existing_session(conn) -> str:
    """bootstrap 민팅 시뮬레이트 — register 는 존재 확인된 세션만 받는다 (Req 8)."""
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    return sid


def test_first_strike_is_warning(conn):
    sid = _existing_session(conn)
    res = strike.register(conn, sid, _verdict("씨발"))
    assert res.kind == "warning"
    assert res.matched_term == "씨발"
    assert "씨발" in res.message  # 템플릿 {term} 치환
    s = repo.load_session(conn, sid)
    assert s.warning_count == 1
    assert s.first_strike_term == "씨발"
    assert s.banned is False


def test_second_strike_is_ban_with_both_terms(conn):
    sid = _existing_session(conn)
    strike.register(conn, sid, _verdict("씨발"))
    res = strike.register(conn, sid, _verdict("개새끼"))
    assert res.kind == "ban"
    assert "씨발" in res.message and "개새끼" in res.message  # 1회/2회 단어
    s = repo.load_session(conn, sid)
    assert s.banned is True
    assert s.ban_reason == res.message


def test_each_strike_logs_safety_event(conn):
    sid = _existing_session(conn)
    strike.register(conn, sid, _verdict("씨발"))
    strike.register(conn, sid, _verdict("개새끼"))
    rows = conn.execute(
        "SELECT category, matched_term FROM safety_events WHERE session_uuid = %s ORDER BY id", (sid,)
    ).fetchall()
    assert rows == [("harassment", "씨발"), ("harassment", "개새끼")]


def test_register_does_not_create_session_row(conn):
    """Req 8 pin — 세션 생성 문은 bootstrap 유일. register 에 미존재 uuid 를 넘겨도
    sessions 행이 생기지 않는다 (방어적 ensure_session 잔재 재유입 방지)."""
    sid = str(uuid.uuid4())
    strike.register(conn, sid, _verdict("씨발"))
    assert repo.session_exists(conn, sid) is False
