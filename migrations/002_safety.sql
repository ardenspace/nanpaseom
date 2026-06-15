CREATE TABLE IF NOT EXISTS sessions (
    session_uuid      UUID PRIMARY KEY,
    warning_count     INT  NOT NULL DEFAULT 0,
    first_strike_term TEXT,
    banned_at         TIMESTAMPTZ,
    ban_reason        TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS safety_events (
    id           BIGSERIAL PRIMARY KEY,
    session_uuid UUID NOT NULL,
    category     TEXT NOT NULL,
    matched_term TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
