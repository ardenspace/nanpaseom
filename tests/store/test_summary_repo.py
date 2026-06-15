import uuid

from app.store import repo


def test_count_exchanges_counts_pairs(conn):
    sid = str(uuid.uuid4())
    assert repo.count_exchanges(conn, sid, "surigong") == 0
    # 1 exchange = user(turn 0) + assistant(turn 1)
    repo.append_chat_log(conn, sid, "surigong", 0, "user", "a")
    repo.append_chat_log(conn, sid, "surigong", 1, "assistant", "b")
    assert repo.count_exchanges(conn, sid, "surigong") == 1
    repo.append_chat_log(conn, sid, "surigong", 2, "user", "c")
    repo.append_chat_log(conn, sid, "surigong", 3, "assistant", "d")
    assert repo.count_exchanges(conn, sid, "surigong") == 2


def test_save_summary_updates_npc_state(conn):
    sid = str(uuid.uuid4())
    repo.save_npc_state(conn, sid, "surigong", 10, [])  # 행 생성
    repo.save_summary(conn, sid, "surigong", "- 플레이어는 보트를 물었다")
    state = repo.load_npc_state(conn, sid, "surigong")
    assert state.summary == "- 플레이어는 보트를 물었다"
    assert state.awareness == 10  # 다른 필드 불변
