import psycopg
import pytest
from fastapi.testclient import TestClient

from app.config import DATABASE_URL
from app.models import Choice, TurnReply
from app.store import db


@pytest.fixture()
def client(monkeypatch):
    # migration + truncate
    c = psycopg.connect(DATABASE_URL, autocommit=True)
    db.apply_migrations(c)
    c.execute("TRUNCATE npc_state, chat_logs, sessions, safety_events")
    c.close()

    # 엔드포인트는 llm_call 을 명시 주입하지 않으므로 client.call 을 stub.
    import app.llm.client as llm_client

    def stub_call(system, messages):
        return TurnReply(
            reply="망치질은 멈추지 않아.", awareness_delta=5, reason="r", memory_tags=["purpose"],
            choices=[Choice(tone="empathetic", text="그래"),
                     Choice(tone="provocative", text="진짜?"),
                     Choice(tone="deflecting", text="딴 얘기")],
        )

    monkeypatch.setattr(llm_client, "call", stub_call)
    from app.api.main import app
    return TestClient(app)


def test_post_turn_mints_session_and_returns_reply(client):
    r = client.post("/turn", json={"npc_id": "surigong", "player_input": "넌 항상 여기 있구나"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"]
    assert len(body["choices"]) == 3
    assert body["session_uuid"]


def test_post_turn_reuses_session(client):
    r1 = client.post("/turn", json={"npc_id": "surigong", "player_input": "a"})
    sid = r1.json()["session_uuid"]
    r2 = client.post("/turn", json={"session_uuid": sid, "npc_id": "surigong", "player_input": "b"})
    assert r2.json()["session_uuid"] == sid
