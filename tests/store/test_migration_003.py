"""B5 — migration 003_save_code.sql 계약 pin (Phase 3 boundary).

계약:
- ``sessions.save_code VARCHAR(9) NULL`` + UNIQUE (NULL 은 다중 허용).
- 기존 데이터가 있는 DB 에 무손실 적용 — 001/002 스키마 불변, 재적용(idempotent)에도
  기존 row/값 보존.
- 신규 컬럼은 save_code **하나뿐** — choices 복원은 기존 스키마(chat_logs)로 가능해야
  하므로 003 이 다른 컬럼/테이블을 추가하지 않는다.

주의: tests fixture(``conn``)가 migrations/*.sql 을 전부 적용하므로 이 테스트는
003 파일이 존재하는 순간부터 통과한다 (migration 자체가 계약 artifact).
"""

import uuid
from pathlib import Path

import psycopg
import pytest

MIGRATION_003 = Path(__file__).resolve().parents[2] / "migrations" / "003_save_code.sql"

# 002 까지의 sessions 컬럼 + save_code — 003 이 이 외의 컬럼을 추가하면 계약 위반.
EXPECTED_SESSIONS_COLUMNS = {
    "session_uuid",
    "warning_count",
    "first_strike_term",
    "banned_at",
    "ban_reason",
    "created_at",
    "save_code",
}


def _column_info(conn, table: str, column: str):
    return conn.execute(
        "SELECT data_type, character_maximum_length, is_nullable "
        "FROM information_schema.columns "
        "WHERE table_name = %s AND column_name = %s",
        (table, column),
    ).fetchone()


def test_save_code_column_is_varchar9_nullable(conn):
    row = _column_info(conn, "sessions", "save_code")
    assert row is not None, "sessions.save_code 컬럼이 없음 (migration 003 미적용)"
    data_type, max_len, is_nullable = row
    assert data_type == "character varying"
    assert max_len == 9
    assert is_nullable == "YES"


def test_save_code_is_unique(conn):
    conn.execute(
        "INSERT INTO sessions (session_uuid, save_code) VALUES (%s, %s)",
        (str(uuid.uuid4()), "ABCD-EFGH"),
    )
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(
            "INSERT INTO sessions (session_uuid, save_code) VALUES (%s, %s)",
            (str(uuid.uuid4()), "ABCD-EFGH"),
        )


def test_save_code_null_allowed_for_multiple_rows(conn):
    # 코드 미발급 세션이 여럿 — UNIQUE 가 NULL 다중을 막으면 안 됨.
    conn.execute("INSERT INTO sessions (session_uuid) VALUES (%s)", (str(uuid.uuid4()),))
    conn.execute("INSERT INTO sessions (session_uuid) VALUES (%s)", (str(uuid.uuid4()),))
    n = conn.execute("SELECT count(*) FROM sessions WHERE save_code IS NULL").fetchone()[0]
    assert n == 2


def test_reapplying_003_preserves_existing_rows(conn):
    """무손실 적용 시뮬레이션 — 기존 세션/코드가 있는 상태에서 003 재적용해도 데이터 보존."""
    sid_old = str(uuid.uuid4())  # save_code 없는 '기존' row (pre-003 데이터 흉내)
    sid_new = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO sessions (session_uuid, warning_count, first_strike_term) "
        "VALUES (%s, 1, %s)",
        (sid_old, "욕설"),
    )
    conn.execute(
        "INSERT INTO sessions (session_uuid, save_code) VALUES (%s, %s)",
        (sid_new, "WXYZ-2345"),
    )

    conn.execute(MIGRATION_003.read_text())  # idempotent 재적용

    row_old = conn.execute(
        "SELECT warning_count, first_strike_term, save_code FROM sessions "
        "WHERE session_uuid = %s",
        (sid_old,),
    ).fetchone()
    assert row_old == (1, "욕설", None)
    row_new = conn.execute(
        "SELECT save_code FROM sessions WHERE session_uuid = %s", (sid_new,)
    ).fetchone()
    assert row_new == ("WXYZ-2345",)


def test_003_adds_only_save_code_column(conn):
    """choices 복원은 기존 스키마로 — 003 의 신규 컬럼은 save_code 하나뿐."""
    cols = {
        r[0]
        for r in conn.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'sessions'"
        ).fetchall()
    }
    assert cols == EXPECTED_SESSIONS_COLUMNS
