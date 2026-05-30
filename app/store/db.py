"""psycopg3 연결 + migration 적용 헬퍼."""

from pathlib import Path

import psycopg

from app.config import DATABASE_URL

MIGRATION = Path(__file__).resolve().parents[2] / "migrations" / "001_init.sql"


def connect():
    """autocommit 연결. slice 는 turn 당 단일 연결, 트랜잭션 경계는 단순화."""
    return psycopg.connect(DATABASE_URL, autocommit=True)


def apply_migrations(conn) -> None:
    conn.execute(MIGRATION.read_text())
