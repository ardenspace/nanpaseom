import uuid

from app.safety.moderation import SafetyVerdict
from app.safety import strike
from app.store import repo


def _verdict(term):
    return SafetyVerdict(category="harassment", matched_term=term)


def test_first_strike_is_warning(conn):
    sid = str(uuid.uuid4())
    res = strike.register(conn, sid, _verdict("씨발"))
    assert res.kind == "warning"
    assert res.matched_term == "씨발"
    assert "씨발" in res.message  # 템플릿 {term} 치환
    s = repo.load_session(conn, sid)
    assert s.warning_count == 1
    assert s.first_strike_term == "씨발"
    assert s.banned is False


def test_second_strike_is_ban_with_both_terms(conn):
    sid = str(uuid.uuid4())
    strike.register(conn, sid, _verdict("씨발"))
    res = strike.register(conn, sid, _verdict("개새끼"))
    assert res.kind == "ban"
    assert "씨발" in res.message and "개새끼" in res.message  # 1회/2회 단어
    s = repo.load_session(conn, sid)
    assert s.banned is True
    assert s.ban_reason == res.message


def test_each_strike_logs_safety_event(conn):
    sid = str(uuid.uuid4())
    strike.register(conn, sid, _verdict("씨발"))
    strike.register(conn, sid, _verdict("개새끼"))
    rows = conn.execute(
        "SELECT category, matched_term FROM safety_events WHERE session_uuid = %s ORDER BY id", (sid,)
    ).fetchall()
    assert rows == [("harassment", "씨발"), ("harassment", "개새끼")]
