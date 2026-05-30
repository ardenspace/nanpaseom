CREATE TABLE IF NOT EXISTS npc_state (
    session_uuid UUID NOT NULL,
    npc_id       TEXT NOT NULL,
    awareness    INT  NOT NULL DEFAULT 0,
    memory_tags  TEXT[] NOT NULL DEFAULT '{}',
    summary      TEXT,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (session_uuid, npc_id)
);

CREATE TABLE IF NOT EXISTS chat_logs (
    id             BIGSERIAL PRIMARY KEY,
    session_uuid   UUID NOT NULL,
    npc_id         TEXT NOT NULL,
    turn_index     INT  NOT NULL,
    role           TEXT NOT NULL,
    content        TEXT NOT NULL,
    reply_json_raw JSONB,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_logs_lookup
    ON chat_logs (session_uuid, npc_id, turn_index);
