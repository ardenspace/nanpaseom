import uuid

from app.models import NpcState
from app.store import repo


def test_load_missing_state_returns_defaults(conn):
    s = repo.load_npc_state(conn, str(uuid.uuid4()), "surigong")
    assert s == NpcState(awareness=0, memory_tags=[], summary=None)


def test_save_then_load_roundtrip(conn):
    sid = str(uuid.uuid4())
    repo.save_npc_state(conn, sid, "surigong", 23, ["purpose", "regret"])
    s = repo.load_npc_state(conn, sid, "surigong")
    assert s.awareness == 23
    assert s.memory_tags == ["purpose", "regret"]


def test_save_is_upsert(conn):
    sid = str(uuid.uuid4())
    repo.save_npc_state(conn, sid, "surigong", 10, ["purpose"])
    repo.save_npc_state(conn, sid, "surigong", 18, ["purpose", "pride"])
    s = repo.load_npc_state(conn, sid, "surigong")
    assert s.awareness == 18
    assert s.memory_tags == ["purpose", "pride"]


def test_chat_log_window_and_turn_index(conn):
    sid = str(uuid.uuid4())
    assert repo.next_turn_index(conn, sid, "surigong") == 0
    repo.append_chat_log(conn, sid, "surigong", 0, "user", "안녕")
    repo.append_chat_log(conn, sid, "surigong", 1, "assistant", "응", {"reply": "응"})
    assert repo.next_turn_index(conn, sid, "surigong") == 2
    window = repo.load_recent_turns(conn, sid, "surigong", limit=8)
    assert window == [
        {"role": "user", "content": "안녕"},
        {"role": "assistant", "content": "응"},
    ]


def test_window_limit_keeps_latest_in_order(conn):
    sid = str(uuid.uuid4())
    for i in range(10):
        repo.append_chat_log(conn, sid, "surigong", i, "user", f"m{i}")
    window = repo.load_recent_turns(conn, sid, "surigong", limit=8)
    assert [m["content"] for m in window] == [f"m{i}" for i in range(2, 10)]
