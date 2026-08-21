"""B6 배포 env 계약 — ``NANPASEOM_INSECURE_COOKIE`` 허용목록 판정 (Phase 1 pin).

계약 (spec.md 동결 원문):

    허용목록 계약: ``"1"`` / ``"true"`` (대소문자 무시)만 "켜짐"(= Secure 생략).
    빈값·``"0"``·``"false"``·오타·기타 모든 값은 "꺼짐"(= Secure 유지).
    falsy 목록 방식 폐지.

왜 파일을 나눴나 — env 판정은 세션 쿠키 *발급 표면* 계약(B6 속성 4종,
test_identity_contracts.py)과 다른 축이다. 매트릭스가 길어 한 파일에 합치면
test_identity_contracts.py 가 400 줄을 넘어 분할 리뷰 대상이 된다.

판정은 발급 표면 하나(bootstrap)로만 관찰한다 — 판정 함수는 구현 내부이고,
계약은 "Secure 속성이 붙느냐"라는 관찰 가능한 결과다. 나머지 표면(redeem 등)이
같은 발급 경로를 쓴다는 사실은 test_identity_contracts.py 가 이미 박제한다.

주의(의미 반전): ``"yes"`` / ``"on"`` / 오타(``"ture"``) 는 falsy 목록 시절
**켜짐**이었다. 허용목록으로 바뀌면서 꺼짐이 된다 — 이 파일이 그 반전을 박제.
"""

import pytest

from tests.api.conftest import cookie_attrs, session_cookie_headers

BOOTSTRAP_URL = "/session/bootstrap"
INSECURE_COOKIE_ENV = "NANPASEOM_INSECURE_COOKIE"
SESSION_COOKIE_MAX_AGE = 15552000  # 180일 — B6 계약 리터럴

# 허용목록 — 이 값들만 "켜짐" (대소문자 무시).
ALLOWLIST_ON_VALUES = ["1", "true", "True", "TRUE", "tRuE"]

# 꺼짐. 두 갈래를 한 목록에 둔다 — 허용목록 계약에서는 구분이 없기 때문이다.
OFF_VALUES = [
    # (구) falsy 6종 — 계약이 바뀌어도 Secure 유지는 그대로.
    "0", "false", "False", "FALSE", "", "  0  ",
    # (신) 허용목록 밖 — falsy 목록 시절엔 켜짐이던 값들. 의미 반전 지점.
    "yes", "Yes", "on", "ON", "y", "enabled", "no",
    "ture", "treu", "tru", "true1", "1true", "truthy",
    "2", "-1", "01", "1.0",
    # 공백이 붙은 값도 허용목록 밖 — 정규화는 대소문자 하나뿐 (fail-closed).
    " 1", "1 ", "  1  ", " true ",
]


def _bootstrap_cookie_attrs(client) -> list[dict[str, str | None]]:
    """bootstrap 응답의 session_uuid Set-Cookie 속성들 (최소 1개 보장)."""
    headers = session_cookie_headers(client.post(BOOTSTRAP_URL))
    assert headers, "session_uuid Set-Cookie 가 없다"
    return [cookie_attrs(h) for h in headers]


def _assert_other_attrs_intact(attrs: dict[str, str | None]) -> None:
    """env 플래그는 Secure 하나만 건드린다 — 나머지 속성은 어느 분기에서도 동일."""
    assert "httponly" in attrs
    assert (attrs.get("samesite") or "").lower() == "lax"
    assert attrs.get("max-age") == str(SESSION_COOKIE_MAX_AGE)
    assert attrs.get("path") == "/"


@pytest.mark.parametrize("flag_value", ALLOWLIST_ON_VALUES)
def test_allowlisted_values_omit_only_secure(client, monkeypatch, flag_value):
    """허용목록 값("1"/"true", 대소문자 무시)만 로컬 dev 예외를 켠다 — Secure 만 생략."""
    monkeypatch.setenv(INSECURE_COOKIE_ENV, flag_value)
    for attrs in _bootstrap_cookie_attrs(client):
        assert "secure" not in attrs
        _assert_other_attrs_intact(attrs)


@pytest.mark.parametrize("flag_value", OFF_VALUES)
def test_non_allowlisted_values_keep_secure(client, monkeypatch, flag_value):
    """허용목록 밖 값은 전부 꺼진 것 — 오타/"yes"/"on"/공백 포함 (배포 env 함정 방지)."""
    monkeypatch.setenv(INSECURE_COOKIE_ENV, flag_value)
    for attrs in _bootstrap_cookie_attrs(client):
        assert "secure" in attrs
        _assert_other_attrs_intact(attrs)


def test_unset_env_keeps_secure(client, monkeypatch):
    """플래그 미설정(= 배포 기본값)은 언제나 Secure — 허용목록의 기본 분기."""
    monkeypatch.delenv(INSECURE_COOKIE_ENV, raising=False)
    for attrs in _bootstrap_cookie_attrs(client):
        assert "secure" in attrs
        _assert_other_attrs_intact(attrs)
