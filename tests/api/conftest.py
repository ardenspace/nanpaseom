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

# B6 Max-Age 계약 리터럴의 테스트 쪽 단일 홈 (180일).
# 구현 상수(app.api.session_cookie.SESSION_COOKIE_MAX_AGE)를 import 하지 않는 것은
# 의도적이다 — 계약 pin 은 구현과 독립된 숫자여야 동어반복이 아니다. 대신 테스트
# 전체가 이 한 곳을 본다 (같은 리터럴을 두 파일에 인라인하지 않는다).
CONTRACT_COOKIE_MAX_AGE = 15552000

# 형식은 유효하지만 어떤 세션에도 매이지 않은 코드 → redeem 404.
# 시도 제한을 재는 테스트들의 "예산 한 칸을 쓰되 상태는 안 건드리는" 표준 노크.
UNKNOWN_CODE = "ZZZZ-ZZZZ"

# 직결 원격 주소 — ``ip_client`` 로 TestClient 에 주입한다 (문서용 TEST-NET-3 대역).
IP_A = "203.0.113.10"


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


def set_save_code(sid: str, code: str) -> None:
    """세션에 세이브 코드를 직접 부여 — 코드를 쓰는 테스트를 발급 엔드포인트와 디커플.

    (redeem/회전 계약을 발급 경로 경유 없이 세팅하기 위한 공유 헬퍼.)
    """
    from app.save_code import SAVE_CODE_RE

    assert SAVE_CODE_RE.fullmatch(code)
    with db_conn() as c:
        c.execute("UPDATE sessions SET save_code = %s WHERE session_uuid = %s", (code, sid))


def banned_session(turns: int = 1, npc_id: str = "surigong") -> str:
    """밴된 세션 — repo 직접 생성 (B1 이후 /turn 은 쿠키 신원 필수라 우회하지 않는다)."""
    sid = known_session(turns=turns, npc_id=npc_id)
    with db_conn() as c:
        repo.ban_session(c, sid, "누적 경고로 대화가 차단됐습니다.")
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


def cookie_attrs(header: str) -> dict[str, str | None]:
    """Set-Cookie 헤더 한 줄의 속성을 소문자 키 dict 로 (값 없는 속성은 None).

    B6 속성 단언의 공유 파서 — Secure/HttpOnly 유무, SameSite/Max-Age/Path 값.
    """
    attrs: dict[str, str | None] = {}
    for part in header.split(";")[1:]:
        key, sep, val = part.strip().partition("=")
        attrs[key.lower()] = val.strip() if sep else None
    return attrs


def assert_cookie_attrs_except_secure(attrs: dict[str, str | None]) -> None:
    """B6 속성 중 Secure 를 뺀 4종: HttpOnly / SameSite=Lax / Max-Age(180일) / Path=/.

    Secure 유무는 호출부가 각자 단언한다 — 발급 표면 계약에서는 "항상 있다"이고,
    env 플래그 매트릭스에서는 있냐 없냐가 곧 관찰 대상(계약의 축)이기 때문이다.
    나머지 4종은 어느 분기에서도 동일해야 하므로 여기 한 곳에 산다.
    """
    assert "httponly" in attrs
    assert (attrs.get("samesite") or "").lower() == "lax"
    assert attrs.get("max-age") == str(CONTRACT_COOKIE_MAX_AGE)
    assert attrs.get("path") == "/"


def session_cookie_value(response) -> str | None:
    """응답 Set-Cookie 헤더에서 session_uuid 값 추출 (본문에는 더 이상 없다)."""
    headers = session_cookie_headers(response)
    return cookie_value(headers[0]) if headers else None


def ip_client(ip: str) -> TestClient:
    """주어진 직결 원격 주소로 보이는 클라이언트 (DB/LLM 세팅은 client fixture 소유).

    IP 당 시도 제한을 재려면 요청마다 원격 주소가 달라 보여야 하는데, 기본
    TestClient 는 전부 ``testclient`` 한 주소로 보인다 — 그래서 client=(host, port).
    """
    from app.api.main import app

    return TestClient(app, client=(ip, 40000))


@pytest.fixture()
def client(monkeypatch):
    """migration + truncate 격리, llm_call/summarize_call stub 된 TestClient.

    redeem 시도 제한 카운터(app.api.rate_limit)는 DB 가 아니라 프로세스 메모리에
    살고 TestClient 는 전부 같은 직결 주소(``testclient``)로 보인다 — truncate 로는
    안 지워지므로 여기서 함께 비운다. 안 하면 redeem 을 쓰는 테스트들이 서로의
    시도를 물려받아 429 로 새기 시작한다 (DB 격리와 같은 결의 테스트 격리).

    TestClient 는 http://testserver — Secure 쿠키는 http 위에서 재전송되지 않아
    rebind→bootstrap 류 흐름이 깨진다. 로컬 dev 와 같은 예외 경로(B6 env 플래그)로
    Secure 만 생략한다. Secure 자체를 단언하는 B6 계약 테스트는 각자
    monkeypatch.delenv 로 이 플래그를 명시적으로 끈다 (같은 monkeypatch 라 test
    본문의 delenv 가 이긴다).
    """
    from app.api import rate_limit
    from app.api.session_cookie import INSECURE_COOKIE_ENV

    monkeypatch.setenv(INSECURE_COOKIE_ENV, "1")
    rate_limit.reset()

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
