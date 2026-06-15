"""psycopg3 연결 + migration 적용 헬퍼."""

from pathlib import Path

import psycopg

from app.config import DATABASE_URL

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


def connect():
    """autocommit 연결. slice 는 turn 당 단일 연결, 트랜잭션 경계는 단순화."""
    return psycopg.connect(DATABASE_URL, autocommit=True)


def apply_migrations(conn) -> None:
    """migrations/*.sql 을 파일명 순서대로 적용 (001, 002, ...). 전부 idempotent (IF NOT EXISTS)."""
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        conn.execute(path.read_text())
