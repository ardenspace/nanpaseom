"""npc_state + chat_logs 영속화 (psycopg3 sync)."""

import json
import uuid

from app.models import NpcState


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
