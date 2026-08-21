"""2-strike 상태머신 + B7 내부 계약 하드닝 pin.

B7 (spec.md 동결 원문): register 는 **존재 확인된 세션만** 받는다. 위반(미지의
세션) 시 조용한 무동작 대신 **즉시 실패한다 — 실제 예외로**. bare ``assert`` 는
금지: ``python -O`` 가 지워 버리면 하드닝이 조용한 무동작으로 되돌아가 계약
자체가 사라진다. 그래서 여기서는 (a) 예외 타입이 AssertionError 가 아님과
(b) ``-O`` 하위 프로세스에서도 여전히 실패함을 둘 다 박제한다.

이 실패가 플레이어에게 보이지 않는다는 쪽(기존 호출부에서 도달 불가)은
tests/api/test_identity_contracts.py 의 B7 섹션 소관.
"""

import subprocess
import sys
import textwrap
import uuid
from pathlib import Path

import pytest

from app.safety.moderation import SafetyVerdict
from app.safety import strike
from app.safety.rules import load_safety_rules
from app.store import repo

REPO_ROOT = Path(__file__).resolve().parents[2]


def _verdict(term):
    return SafetyVerdict(category="harassment", matched_term=term)


def _denylist_term(index: int = 0) -> str:
    """디니리스트 항목 — 안전 어휘의 서식지는 rules/safety.yaml (하드코딩 금지)."""
    return load_safety_rules().harassment_denylist[index]


def _existing_session(conn) -> str:
    """bootstrap 민팅 시뮬레이트 — register 는 존재 확인된 세션만 받는다 (Req 8)."""
    sid = str(uuid.uuid4())
    repo.ensure_session(conn, sid)
    return sid


def test_first_strike_is_warning(conn):
    sid = _existing_session(conn)
    res = strike.register(conn, sid, _verdict("씨발"))
    assert res.kind == "warning"
    assert res.matched_term == "씨발"
    assert "씨발" in res.message  # 템플릿 {term} 치환
    s = repo.load_session(conn, sid)
    assert s.warning_count == 1
    assert s.first_strike_term == "씨발"
    assert s.banned is False


def test_second_strike_is_ban_with_both_terms(conn):
    sid = _existing_session(conn)
    strike.register(conn, sid, _verdict("씨발"))
    res = strike.register(conn, sid, _verdict("개새끼"))
    assert res.kind == "ban"
    assert "씨발" in res.message and "개새끼" in res.message  # 1회/2회 단어
    s = repo.load_session(conn, sid)
    assert s.banned is True
    assert s.ban_reason == res.message


def test_each_strike_logs_safety_event(conn):
    sid = _existing_session(conn)
    strike.register(conn, sid, _verdict("씨발"))
    strike.register(conn, sid, _verdict("개새끼"))
    rows = conn.execute(
        "SELECT category, matched_term FROM safety_events WHERE session_uuid = %s ORDER BY id", (sid,)
    ).fetchall()
    assert rows == [("harassment", "씨발"), ("harassment", "개새끼")]


# ------------------------------------- B7: 미지의 세션 = 즉시 실패 (조용한 무동작 금지)

def test_register_with_unknown_session_raises(conn):
    """B7 — 전제(존재 확인된 세션) 위반은 조용히 넘어가지 않고 즉시 실패한다.

    구 계약은 "조용한 무동작"이었다: 미지의 uuid 를 넘기면 sessions 행도 안 생기고
    경고도 안 나면서 아무 신호가 없었다. 그 침묵이 버그를 삼킨다 — 이제 예외.
    """
    sid = str(uuid.uuid4())
    with pytest.raises(Exception) as excinfo:
        strike.register(conn, sid, _verdict(_denylist_term()))

    # bare assert 금지 계약 — AssertionError 는 `python -O` 에서 통째로 사라지는
    # 종류라 타입 자체를 배제한다 (실제 예외로 실패할 것).
    assert not isinstance(excinfo.value, AssertionError), (
        "bare assert 로는 안 된다 — python -O 에서 조용한 무동작으로 되돌아간다"
    )


def test_register_with_unknown_session_still_creates_no_session_row(conn):
    """Req 8 유지 — 실패하더라도 세션을 만들지는 않는다.

    세션 생성 문은 bootstrap 유일. 하드닝이 "없으면 만든다"(방어적 ensure_session
    잔재)로 흘러가는 것을 막는다.
    """
    sid = str(uuid.uuid4())
    with pytest.raises(Exception):
        strike.register(conn, sid, _verdict(_denylist_term()))
    assert repo.session_exists(conn, sid) is False


def test_register_hardening_survives_python_dash_O(conn):
    """B7 핵심 — ``python -O`` 하위 프로세스에서도 여전히 실패한다.

    bare ``assert`` 구현이면 -O 가 지워 버려 SILENT_NOOP 이 찍힌다 = 하드닝 소멸.
    DB 는 실제로 붙되(계약이 DB 조회에 걸려 있으므로) 격리를 위해 랜덤 uuid 만 쓰고,
    실패 전에 기록됐을 수 있는 safety_events 는 하위 프로세스가 직접 치운다.
    """
    sid = str(uuid.uuid4())
    script = textwrap.dedent(
        f"""
        import psycopg
        from app.config import DATABASE_URL
        from app.safety import strike
        from app.safety.moderation import SafetyVerdict
        from app.safety.rules import load_safety_rules

        sid = {sid!r}
        term = load_safety_rules().harassment_denylist[0]
        with psycopg.connect(DATABASE_URL, autocommit=True) as c:
            try:
                strike.register(c, sid, SafetyVerdict(category="harassment", matched_term=term))
            except BaseException as exc:
                print("RAISED", type(exc).__name__)
            else:
                print("SILENT_NOOP")
            c.execute("DELETE FROM safety_events WHERE session_uuid = %s", (sid,))
        """
    )
    proc = subprocess.run(
        [sys.executable, "-O", "-c", script],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"하위 프로세스가 죽었다:\n{proc.stderr}"
    outcome = proc.stdout.strip().splitlines()[-1]
    assert outcome.startswith("RAISED"), (
        f"-O 에서 하드닝이 사라졌다 (기대: RAISED, 실제: {outcome!r})"
    )
    assert not outcome.endswith("AssertionError"), (
        "명시적 raise AssertionError 도 금지 — assert 계열은 -O 신뢰 불가 신호"
    )
