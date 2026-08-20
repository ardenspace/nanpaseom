"""POST /turn 기본 동작 — B1 이후: 신원은 쿠키 단일, /turn 은 세션을 만들지 않는다.

(구 계약의 "무쿠키 200 + 민팅 + 본문 session_uuid" / "본문 session_uuid 재사용" 은
tests/api/test_identity_contracts.py 의 B1 계약으로 대체 — 여기서는 정상 턴의
응답 형태와 같은 쿠키 세션으로의 턴 누적만 pin.)
"""

import psycopg

from app.config import DATABASE_URL
from tests.api.conftest import known_session

COOKIE_NAME = "session_uuid"
NPC_ID = "surigong"


def _chat_log_count(sid: str) -> int:
    with psycopg.connect(DATABASE_URL, autocommit=True) as c:
        return c.execute(
            "SELECT count(*) FROM chat_logs WHERE session_uuid = %s", (sid,)
        ).fetchone()[0]


def test_post_turn_with_cookie_returns_reply_and_choices(client):
    sid = known_session()
    client.cookies.set(COOKIE_NAME, sid)
    r = client.post("/turn", json={"npc_id": NPC_ID, "player_input": "넌 항상 여기 있구나"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"]
    assert len(body["choices"]) == 3
    assert "session_uuid" not in body  # 자격증명은 응답 본문에 없다


def test_post_turn_accumulates_on_same_cookie_session(client):
    sid = known_session()
    client.cookies.set(COOKIE_NAME, sid)
    r1 = client.post("/turn", json={"npc_id": NPC_ID, "player_input": "a"})
    r2 = client.post("/turn", json={"npc_id": NPC_ID, "player_input": "b"})
    assert r1.status_code == r2.status_code == 200
    assert _chat_log_count(sid) == 4  # 2턴 × (user + assistant) — 같은 세션에 누적
