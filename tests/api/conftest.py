"""tests/api 공유 fixture — DB 격리 + 결정적 LLM stub.

기존 test_turn_endpoint / test_safety_endpoint 는 자체 `client` fixture 를 유지
(모듈-로컬 fixture 가 이 conftest 의 것을 shadow — 동작 동일). 신규 API 테스트
모듈은 이 fixture 를 재사용한다.
"""

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.config import DATABASE_URL
from app.models import Choice, TurnReply
from app.store import db


def make_stub_reply() -> TurnReply:
    """결정적 stub TurnReply — 테스트는 내용이 아니라 형태만 단언한다."""
    return TurnReply(
        reply="망치질은 멈추지 않아.", awareness_delta=5, reason="r", memory_tags=["purpose"],
        choices=[Choice(tone="empathetic", text="그래"),
                 Choice(tone="provocative", text="진짜?"),
                 Choice(tone="deflecting", text="딴 얘기")],
    )


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
