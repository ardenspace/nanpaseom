"""tests/api 공유 fixture/헬퍼 — DB 격리 + 결정적 LLM stub + 쿠키 신원 헬퍼.

B1 이후 /turn 은 세션을 만들지 않는다 (쿠키 신원 필수) — 세션이 필요한 테스트는
``known_session()`` (repo 직접 생성, bootstrap 민팅 시뮬레이트) 또는 bootstrap 경유로
만들고 쿠키에 싣는다. 응답의 세션 식별은 본문이 아니라 Set-Cookie 헤더
(``session_cookie_value``) — 자격증명은 어떤 응답 본문에도 없다.
"""

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.api.session_cookie import COOKIE_NAME
from app.config import DATABASE_URL
from app.models import Choice, TurnReply
from app.store import db, repo


def db_conn():
    """테스트용 DB 관찰 커넥션 (autocommit) — 부작용 없음 단언은 DB 직접 관찰로."""
    return psycopg.connect(DATABASE_URL, autocommit=True)


def count_sessions() -> int:
    with db_conn() as c:
        return c.execute("SELECT count(*) FROM sessions").fetchone()[0]


def session_row_exists(sid: str) -> bool:
    with db_conn() as c:
        row = c.execute(
            "SELECT 1 FROM sessions WHERE session_uuid = %s", (sid,)
        ).fetchone()
    return row is not None


def db_save_code(sid: str) -> str | None:
    with db_conn() as c:
        row = c.execute(
            "SELECT save_code FROM sessions WHERE session_uuid = %s", (sid,)
        ).fetchone()
    return row[0] if row else None


def raising_llm(monkeypatch):
    """llm_call 이 LLMError 를 던지는 상황 — 503 경로 단언용."""
    import app.llm.client as llm_client

    def boom(system, messages):
        raise llm_client.LLMError("llama-server down (stub)")

    monkeypatch.setattr(llm_client, "call", boom)


def make_stub_reply() -> TurnReply:
    """결정적 stub TurnReply — 테스트는 내용이 아니라 형태만 단언한다."""
    return TurnReply(
        reply="망치질은 멈추지 않아.", awareness_delta=5, reason="r", memory_tags=["purpose"],
        choices=[Choice(tone="empathetic", text="그래"),
                 Choice(tone="provocative", text="진짜?"),
                 Choice(tone="deflecting", text="딴 얘기")],
    )


def known_session(turns: int = 0, npc_id: str = "surigong") -> str:
    """서버 민팅을 흉내낸 sessions 행 (+ 선택적 chat_logs) — /turn 경유 없이 생성.

    assistant 행에는 3-choice raw 를 실어 resumed 의 load_last_reply_choices 도 동작.
    """
    with psycopg.connect(DATABASE_URL, autocommit=True) as c:
        sid = repo.mint_session(c)
        repo.ensure_session(c, sid)
        for i in range(turns):
            repo.append_chat_log(c, sid, npc_id, 2 * i, "user", f"질문 {i}")
            repo.append_chat_log(
                c, sid, npc_id, 2 * i + 1, "assistant", f"응답 {i}",
                {"choices": [{"tone": "empathetic", "text": "그래"},
                             {"tone": "provocative", "text": "진짜?"},
                             {"tone": "deflecting", "text": "딴 얘기"}]},
            )
    return sid


def session_cookie_headers(response) -> list[str]:
    """응답의 session_uuid Set-Cookie 헤더 전부 — 속성 단언/부재(`== []`) 단언용."""
    return [
        h for h in response.headers.get_list("set-cookie")
        if h.strip().startswith(f"{COOKIE_NAME}=")
    ]


def cookie_value(header: str) -> str:
    """Set-Cookie 헤더 한 줄에서 쿠키 값만 추출."""
    return header.split(";", 1)[0].split("=", 1)[1].strip()


def session_cookie_value(response) -> str | None:
    """응답 Set-Cookie 헤더에서 session_uuid 값 추출 (본문에는 더 이상 없다)."""
    headers = session_cookie_headers(response)
    return cookie_value(headers[0]) if headers else None


@pytest.fixture()
def client(monkeypatch):
    """migration + truncate 격리, llm_call/summarize_call stub 된 TestClient.

    TestClient 는 http://testserver — Secure 쿠키는 http 위에서 재전송되지 않아
    rebind→bootstrap 류 흐름이 깨진다. 로컬 dev 와 같은 예외 경로(B6 env 플래그)로
    Secure 만 생략한다. Secure 자체를 단언하는 B6 계약 테스트는 각자
    monkeypatch.delenv 로 이 플래그를 명시적으로 끈다 (같은 monkeypatch 라 test
    본문의 delenv 가 이긴다).
    """
    from app.api.session_cookie import INSECURE_COOKIE_ENV

    monkeypatch.setenv(INSECURE_COOKIE_ENV, "1")

    c = psycopg.connect(DATABASE_URL, autocommit=True)
    db.apply_migrations(c)
    c.execute("TRUNCATE npc_state, chat_logs, sessions, safety_events")
    c.close()

    import app.llm.client as llm_client

    monkeypatch.setattr(llm_client, "call", lambda system, messages: make_stub_reply())
    # bootstrap/turn 테스트는 10 exchange trigger 에 도달하지 않지만 방어적으로 stub
    # (실수로 live summarize 콜이 나가는 일 없도록).
    monkeypatch.setattr(llm_client, "summarize_call", lambda system, user: "- stub summary")

    from app.api.main import app
    return TestClient(app)
