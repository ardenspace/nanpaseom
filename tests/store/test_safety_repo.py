import uuid

from app.models import SessionState
from app.store import repo


def test_load_missing_session_returns_defaults(conn):
    s = repo.load_session(conn, str(uuid.uuid4()))
    assert s == SessionState(warning_count=0, first_strike_term=None, banned=False, ban_reason=None)


def test_ensure_then_set_warning(conn):
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    repo.set_warning(conn, sid, 1, "씨발")
    s = repo.load_session(conn, sid)
    assert s.warning_count == 1
    assert s.first_strike_term == "씨발"
    assert s.banned is False


def test_ban_session(conn):
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    repo.ban_session(conn, sid, "사유 텍스트")
    s = repo.load_session(conn, sid)
    assert s.banned is True
    assert s.ban_reason == "사유 텍스트"


def test_append_safety_event_stores_no_raw_input(conn):
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    repo.append_safety_event(conn, sid, "harassment", "씨발")
    rows = conn.execute(
        "SELECT category, matched_term FROM safety_events WHERE session_uuid = %s", (sid,)
    ).fetchall()
    assert rows == [("harassment", "씨발")]
    cols = conn.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'safety_events'"
    ).fetchall()
    assert "input" not in {c[0] for c in cols}
