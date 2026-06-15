import psycopg
import pytest

from app.config import DATABASE_URL
from app.store import db


@pytest.fixture()
def conn():
    """함수 스코프 연결 — migration 적용 + 테이블 truncate 로 격리."""
    connection = psycopg.connect(DATABASE_URL, autocommit=True)
    db.apply_migrations(connection)
    connection.execute("TRUNCATE npc_state, chat_logs, sessions, safety_events")
    yield connection
    connection.close()
