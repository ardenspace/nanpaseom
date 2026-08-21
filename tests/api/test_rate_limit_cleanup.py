"""B3 시도 제한의 **윈도우 만료 기록 정리** pin (계약 마지막 절, 시간 seam 포함).

test_redeem_rate_limit.py 가 pin 하지 못하고 구현에 위임한 절:
"윈도우가 지난 기록은 정리된다 — IP 를 바꿔가며 두드려도 메모리가 무한정 자라지
않는다."

시간 seam = ``app.api.rate_limit.now()`` (모듈 레벨 단조 시계 함수) 를 monkeypatch.
sleep 은 쓰지 않는다 — 윈도우가 3600초라 sleep 테스트는 불가능하고, 짧은 윈도우로
바꿔 재는 flaky 테스트도 만들지 않는다.
"""

import pytest

from app.api import rate_limit
from app.save_code import load_save_code_rules
from tests.api.conftest import IP_A, UNKNOWN_CODE, ip_client

WINDOW = 60.0  # 이 파일의 유닛 테스트가 쓰는 임의 윈도우 (엔드포인트 수치는 YAML)
LIMIT = 3


class FakeClock:
    """호출 가능한 가짜 단조 시계 — ``rate_limit.now`` 자리에 그대로 꽂힌다."""

    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


@pytest.fixture()
def clock(monkeypatch):
    c = FakeClock()
    monkeypatch.setattr(rate_limit, "now", c)
    rate_limit.reset()
    yield c
    rate_limit.reset()


# ------------------------------------------------ 메모리: 만료 기록은 남지 않는다

def test_records_from_expired_windows_are_dropped(clock):
    """IP 를 바꿔가며 두드린 뒤 윈도우가 지나면 보관 키가 남지 않는다."""
    for i in range(50):
        assert rate_limit.allow(f"198.51.100.{i}", limit=LIMIT, window_seconds=WINDOW)
    assert rate_limit.tracked_key_count() == 50

    clock.advance(WINDOW + 1)
    assert rate_limit.allow("203.0.113.99", limit=LIMIT, window_seconds=WINDOW)

    # 새로 들어온 IP 하나만 남는다 — 50개의 만료 기록은 정리됐다.
    assert rate_limit.tracked_key_count() == 1


def test_long_running_hammering_does_not_grow_without_bound(clock):
    """윈도우를 여러 번 넘겨가며 새 IP 로 계속 두드려도 보관량이 누적되지 않는다."""
    peak = 0
    for round_no in range(10):
        for i in range(20):
            rate_limit.allow(f"198.51.100.{round_no}.{i}", limit=LIMIT, window_seconds=WINDOW)
        peak = max(peak, rate_limit.tracked_key_count())
        clock.advance(WINDOW + 1)

    # 라운드마다 20개씩 200번 두드렸지만, 어느 시점에도 두 윈도우 분량을 넘지 않는다.
    assert peak <= 40


# --------------------------------------- 행동: 윈도우가 지나면 예산이 돌아온다

def test_budget_returns_once_the_window_passes(clock):
    for _ in range(LIMIT):
        assert rate_limit.allow(IP_A, limit=LIMIT, window_seconds=WINDOW)
    assert not rate_limit.allow(IP_A, limit=LIMIT, window_seconds=WINDOW)

    clock.advance(WINDOW + 1)

    assert rate_limit.allow(IP_A, limit=LIMIT, window_seconds=WINDOW)


def test_blocked_attempts_do_not_extend_the_window(clock):
    """차단된 시도는 기록되지 않는다 — 계속 두드려도 회복 시점이 밀리지 않는다."""
    for _ in range(LIMIT):
        assert rate_limit.allow(IP_A, limit=LIMIT, window_seconds=WINDOW)

    for _ in range(5):  # 윈도우 안에서 계속 두드린다
        clock.advance(WINDOW / 10)
        assert not rate_limit.allow(IP_A, limit=LIMIT, window_seconds=WINDOW)

    clock.advance(WINDOW / 2)  # 최초 허용 시점으로부터 윈도우 경과
    assert rate_limit.allow(IP_A, limit=LIMIT, window_seconds=WINDOW)


# --------------------------------------------- 엔드포인트도 같은 시계를 탄다

def test_redeem_is_usable_again_after_the_rules_window(client, clock):
    """429 를 받은 사람은 YAML 윈도우가 지나면 다시 시도할 수 있다 (영구 잠금 아님)."""
    limits = load_save_code_rules()
    c = ip_client(IP_A)

    for _ in range(limits.redeem_rate_limit_attempts):
        assert c.post("/save-code/redeem", json={"code": UNKNOWN_CODE}).status_code == 404
    assert c.post("/save-code/redeem", json={"code": UNKNOWN_CODE}).status_code == 429

    clock.advance(limits.redeem_rate_limit_window_seconds + 1)

    assert c.post("/save-code/redeem", json={"code": UNKNOWN_CODE}).status_code == 404
