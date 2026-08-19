"""npc_state + chat_logs 영속화 (psycopg3 sync)."""

import json
import uuid

from app.models import NpcState, SessionState


def mint_session(conn) -> str:
    """새 session_uuid 발급. row 는 첫 save 때 생성."""
    return str(uuid.uuid4())


def load_npc_state(conn, session_uuid: str, npc_id: str) -> NpcState:
    row = conn.execute(
        "SELECT awareness, memory_tags, summary FROM npc_state "
        "WHERE session_uuid = %s AND npc_id = %s",
        (session_uuid, npc_id),
    ).fetchone()
    if row is None:
        return NpcState(awareness=0, memory_tags=[], summary=None)
    return NpcState(awareness=row[0], memory_tags=list(row[1]), summary=row[2])


def save_npc_state(conn, session_uuid: str, npc_id: str, awareness: int, memory_tags: list[str]) -> None:
    conn.execute(
        "INSERT INTO npc_state (session_uuid, npc_id, awareness, memory_tags, updated_at) "
        "VALUES (%s, %s, %s, %s, now()) "
        "ON CONFLICT (session_uuid, npc_id) DO UPDATE SET "
        "awareness = EXCLUDED.awareness, memory_tags = EXCLUDED.memory_tags, updated_at = now()",
        (session_uuid, npc_id, awareness, memory_tags),
    )


def load_recent_turns(conn, session_uuid: str, npc_id: str, limit: int = 8) -> list[dict]:
    rows = conn.execute(
        "SELECT role, content FROM chat_logs "
        "WHERE session_uuid = %s AND npc_id = %s "
        "ORDER BY turn_index DESC LIMIT %s",
        (session_uuid, npc_id, limit),
    ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def load_last_reply_choices(conn, session_uuid: str, npc_id: str) -> list[dict]:
    """마지막 assistant 턴의 choices. raw 없음(diegetic fallback 턴)/행 없음 = []
    → 자유 입력 모드 (B2 resumed 계약)."""
    row = conn.execute(
        "SELECT reply_json_raw FROM chat_logs "
        "WHERE session_uuid = %s AND npc_id = %s AND role = 'assistant' "
        "ORDER BY turn_index DESC LIMIT 1",
        (session_uuid, npc_id),
    ).fetchone()
    if row is None or row[0] is None:
        return []
    return row[0].get("choices", [])


def next_turn_index(conn, session_uuid: str, npc_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(MAX(turn_index), -1) + 1 FROM chat_logs "
        "WHERE session_uuid = %s AND npc_id = %s",
        (session_uuid, npc_id),
    ).fetchone()
    return row[0]


def append_chat_log(
    conn,
    session_uuid: str,
    npc_id: str,
    turn_index: int,
    role: str,
    content: str,
    reply_json_raw: dict | None = None,
) -> None:
    conn.execute(
        "INSERT INTO chat_logs (session_uuid, npc_id, turn_index, role, content, reply_json_raw) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (
            session_uuid,
            npc_id,
            turn_index,
            role,
            content,
            json.dumps(reply_json_raw) if reply_json_raw is not None else None,
        ),
    )


def ensure_session(conn, session_uuid: str) -> None:
    """sessions row 가 없으면 생성 (있으면 무시)."""
    conn.execute(
        "INSERT INTO sessions (session_uuid) VALUES (%s) ON CONFLICT (session_uuid) DO NOTHING",
        (session_uuid,),
    )


def load_session(conn, session_uuid: str) -> SessionState:
    row = conn.execute(
        "SELECT warning_count, first_strike_term, banned_at, ban_reason FROM sessions "
        "WHERE session_uuid = %s",
        (session_uuid,),
    ).fetchone()
    if row is None:
        return SessionState(warning_count=0, first_strike_term=None, banned=False, ban_reason=None)
    return SessionState(
        warning_count=row[0],
        first_strike_term=row[1],
        banned=row[2] is not None,
        ban_reason=row[3],
    )


def set_warning(conn, session_uuid: str, warning_count: int, first_strike_term: str) -> None:
    conn.execute(
        "UPDATE sessions SET warning_count = %s, first_strike_term = %s WHERE session_uuid = %s",
        (warning_count, first_strike_term, session_uuid),
    )


def ban_session(conn, session_uuid: str, ban_reason: str) -> None:
    conn.execute(
        "UPDATE sessions SET banned_at = now(), ban_reason = %s WHERE session_uuid = %s",
        (ban_reason, session_uuid),
    )


def append_safety_event(conn, session_uuid: str, category: str, matched_term: str | None) -> None:
    conn.execute(
        "INSERT INTO safety_events (session_uuid, category, matched_term) VALUES (%s, %s, %s)",
        (session_uuid, category, matched_term),
    )


def get_save_code(conn, session_uuid: str) -> str | None:
    """세션의 세이브 코드 (미발급/행 없음 = None)."""
    row = conn.execute(
        "SELECT save_code FROM sessions WHERE session_uuid = %s", (session_uuid,)
    ).fetchone()
    return row[0] if row else None


def set_save_code(conn, session_uuid: str, save_code: str) -> None:
    """세이브 코드 부여 — UNIQUE 인덱스 충돌 시 psycopg UniqueViolation 전파 (호출자 재시도)."""
    conn.execute(
        "UPDATE sessions SET save_code = %s WHERE session_uuid = %s",
        (save_code, session_uuid),
    )


def find_session_by_save_code(conn, save_code: str) -> str | None:
    """코드 → session_uuid (미지의 코드 = None)."""
    row = conn.execute(
        "SELECT session_uuid FROM sessions WHERE save_code = %s", (save_code,)
    ).fetchone()
    return str(row[0]) if row else None


def count_exchanges(conn, session_uuid: str, npc_id: str) -> int:
    """완료된 exchange 수. 1 exchange = user+assistant 2행 → (MAX(turn_index)+1)//2."""
    row = conn.execute(
        "SELECT (COALESCE(MAX(turn_index), -1) + 1) / 2 FROM chat_logs "
        "WHERE session_uuid = %s AND npc_id = %s",
        (session_uuid, npc_id),
    ).fetchone()
    return int(row[0])


def save_summary(conn, session_uuid: str, npc_id: str, summary: str) -> None:
    """npc_state.summary 갱신 (행은 save_npc_state 후 존재 가정)."""
    conn.execute(
        "UPDATE npc_state SET summary = %s, updated_at = now() "
        "WHERE session_uuid = %s AND npc_id = %s",
        (summary, session_uuid, npc_id),
    )
