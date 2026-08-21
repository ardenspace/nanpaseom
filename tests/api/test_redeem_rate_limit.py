"""B3 redeem 시도 제한 계약 pin (Phase 2 step 2, 실패 상태로 커밋).

계약 요약 (spec.md 동결 원문 기준):

- IP 당 시도 제한. IP 는 **직결 연결의 원격 주소**(``request.client.host`` 상당) —
  ``X-Forwarded-For`` 등 클라이언트 제공 헤더는 신뢰하지 않는다.
- 초과 → ``429 {status:"error", message}``, message 는 rules YAML 문구.
- 집계 규칙: 엔드포인트로 들어온 **모든 시도**가 집계된다 — 형식 위반, 404, 성공 모두.
  성공은 카운터를 리셋하지 않는다 (유효 코드 1개를 쥔 공격자의 무한 우회 차단).
- 제한 수치(횟수/윈도우)는 rules YAML — 이 파일은 숫자를 인라인하지 않고
  ``load_save_code_rules()`` 에서 읽는다. 튜닝해도 pin 이 살아남게 하기 위함.

기존 redeem 계약(404 문구, 밴 비재바인딩, 성공 재바인딩)은 test_save_code.py 가 pin —
여기서는 제한 층만 다룬다.

**미구현 시드**: 카운터의 결정적 초기화 seam (``app.api.rate_limit.reset()``) 과
rules 키 3종(``redeem_rate_limit_attempts`` / ``redeem_rate_limit_window_seconds`` /
``redeem_rate_limited_message``) 은 다음 스텝이 만든다. 그 전까지 이 파일은 전부 실패한다.

**미pin 항목**: "윈도우가 지난 기록은 정리된다"(메모리 무한 증가 방지)는 시간 seam
없이는 결정적으로 관측할 수 없어 여기서 pin 하지 않는다 — 시간 seam 은 구현에 위임돼
있으므로, 구현 스텝이 seam 과 함께 그 테스트를 추가한다 (flaky sleep 테스트 금지).
"""

import pytest
from fastapi.testclient import TestClient

from app.save_code import load_save_code_rules
from tests.api.conftest import (
    IP_A,
    UNKNOWN_CODE,
    ip_client,
    known_session,
    session_cookie_headers,
    set_save_code,
)

REDEEM_URL = "/save-code/redeem"

GOOD_CODE = "ABCD-EFGH"      # 실제 세션에 매인 유효 코드
MALFORMED_CODE = "not-a-code"  # 형식 위반 → DB 조회 없이 404

# 두 번째 직결 원격 주소 — "IP 당 예산" 을 재는 이 파일에서만 쓴다 (IP_A 는 conftest).
IP_B = "203.0.113.11"


@pytest.fixture()
def limits():
    """제한 수치/문구의 단일 홈은 rules/save_code.yaml — 테스트는 숫자를 인라인 안 함."""
    return load_save_code_rules()


@pytest.fixture()
def fresh_limiter():
    """시도 카운터를 테스트 경계에서 결정적으로 비운다 (테스트 간 오염 금지)."""
    from app.api import rate_limit

    rate_limit.reset()
    yield rate_limit
    rate_limit.reset()


def _redeem(c: TestClient, code: str, **kwargs):
    return c.post(REDEEM_URL, json={"code": code}, **kwargs)


# --------------------------------------------------- rules YAML 이 수치의 단일 홈

def test_limit_values_and_message_live_in_rules_yaml(limits):
    """횟수/윈도우/문구가 코드가 아닌 YAML 에 있다 — 튜닝은 YAML 수정 (CLAUDE.md)."""
    assert limits.redeem_rate_limit_attempts >= 1
    assert limits.redeem_rate_limit_window_seconds >= 1
    assert limits.redeem_rate_limited_message


# ------------------------------------------------------------- 초과 시 429 계약

def test_attempts_beyond_the_limit_are_429_with_the_rules_message(
    client, fresh_limiter, limits
):
    c = ip_client(IP_A)
    for _ in range(limits.redeem_rate_limit_attempts):
        assert _redeem(c, UNKNOWN_CODE).status_code == 404  # 예산 안 = 기존 계약 그대로

    r = _redeem(c, UNKNOWN_CODE)

    assert r.status_code == 429
    body = r.json()
    assert body["status"] == "error"
    assert body["message"] == limits.redeem_rate_limited_message
    assert session_cookie_headers(r) == []  # 차단 응답은 아무것도 재바인딩 안 함


# ------------------------------------------------ 집계 규칙: 모든 시도가 집계된다

def test_malformed_code_attempts_count_toward_the_limit(client, fresh_limiter, limits):
    """형식 위반은 DB 조회 없이 404 지만, 엔드포인트에 들어온 시도이므로 집계된다."""
    c = ip_client(IP_A)
    for _ in range(limits.redeem_rate_limit_attempts):
        assert _redeem(c, MALFORMED_CODE).status_code == 404

    assert _redeem(c, UNKNOWN_CODE).status_code == 429


def test_successful_redeems_count_toward_the_limit(client, fresh_limiter, limits):
    """성공도 집계 대상 — 유효 코드 1개로 제한을 무한 우회할 수 없다."""
    sid = known_session(turns=1)
    set_save_code(sid, GOOD_CODE)
    c = ip_client(IP_A)

    for _ in range(limits.redeem_rate_limit_attempts):
        r = _redeem(c, GOOD_CODE)
        assert r.status_code == 200
        assert r.json()["status"] == "resumed"

    assert _redeem(c, GOOD_CODE).status_code == 429


def test_a_success_does_not_reset_the_counter(client, fresh_limiter, limits):
    """실패 누적 뒤의 성공이 예산을 되돌려주지 않는다."""
    sid = known_session(turns=1)
    set_save_code(sid, GOOD_CODE)
    c = ip_client(IP_A)

    for _ in range(limits.redeem_rate_limit_attempts - 1):
        assert _redeem(c, UNKNOWN_CODE).status_code == 404
    assert _redeem(c, GOOD_CODE).status_code == 200  # 마지막 예산 한 칸을 성공이 쓴다

    assert _redeem(c, UNKNOWN_CODE).status_code == 429


# ------------------------------------------- IP 판정: 직결 주소만, XFF 는 불신

def test_spoofed_forwarded_for_does_not_buy_a_separate_budget(
    client, fresh_limiter, limits
):
    """헤더를 매 요청 바꿔 달아도 같은 직결 주소면 같은 예산을 쓴다."""
    c = ip_client(IP_A)
    for i in range(limits.redeem_rate_limit_attempts):
        r = _redeem(c, UNKNOWN_CODE, headers={"X-Forwarded-For": f"198.51.100.{i}"})
        assert r.status_code == 404

    r = _redeem(c, UNKNOWN_CODE, headers={"X-Forwarded-For": "198.51.100.250"})
    assert r.status_code == 429


def test_each_direct_remote_address_gets_its_own_budget(client, fresh_limiter, limits):
    """제한은 IP 당 — 한 IP 의 소진이 다른 IP 를 막지 않는다 (공유 전역 카운터 아님)."""
    a, b = ip_client(IP_A), ip_client(IP_B)
    for _ in range(limits.redeem_rate_limit_attempts):
        assert _redeem(a, UNKNOWN_CODE).status_code == 404
    assert _redeem(a, UNKNOWN_CODE).status_code == 429

    assert _redeem(b, UNKNOWN_CODE).status_code == 404
