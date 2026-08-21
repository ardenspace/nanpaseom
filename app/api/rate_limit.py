"""시도 제한 — 키(=직결 IP) 당 슬라이딩 윈도우 카운터, 프로세스 메모리 단일 홈.

B3 redeem 의 코드 추측 방어. 수치/문구는 여기가 아니라 rules YAML 이 소유하고,
이 모듈은 "몇 번을 얼마 동안" 을 인자로 받아 판정만 한다 (튜닝은 YAML 수정).

기록된 한계 (Simplicity Zone — 이번 런의 해결 대상 아님):
- 프로세스 메모리 → 서버 재시작 시 리셋, 워커가 여러 개면 워커마다 별개 예산.
- 분산 공격(다수 IP)에는 약하다. 리버스 프록시 뒤에서는 직결 주소가 프록시가
  되므로 사실상 무의미해진다 (그때는 프록시 층에서 제한하는 것이 옳다).

시간 seam: 모듈 레벨 ``now()``. 테스트는 이 함수를 monkeypatch 해 sleep 없이
윈도우를 넘긴다 (``tests/api/test_rate_limit_cleanup.py``).
"""

import time
from collections import deque

from fastapi import Request

# 직결 주소를 못 읽는 호출(ASGI scope 에 client 없음)의 공유 버킷 —
# 신원 불명은 하나의 예산을 나눠 쓴다 (제한 우회 구멍을 만들지 않는다).
UNKNOWN_CLIENT_KEY = "-"

_hits: dict[str, deque[float]] = {}
_last_sweep: float = 0.0


def now() -> float:
    """단조 시계 seam — 실제 시간 흐름의 유일한 출처 (테스트가 갈아끼운다)."""
    return time.monotonic()


def reset() -> None:
    """모든 기록을 비운다 — 카운터가 프로세스 전역이므로 테스트 경계의 결정적 초기화.

    테스트 스위트가 공유 fixture(tests/api/conftest.py ``client``)에서 호출한다.
    """
    global _last_sweep
    _hits.clear()
    _last_sweep = now()


def client_ip(request: Request) -> str:
    """제한 키 = **직결 연결의 원격 주소**.

    ``X-Forwarded-For`` 등 클라이언트가 붙여 보낼 수 있는 헤더는 보지 않는다 —
    헤더를 매 요청 바꿔 다는 것만으로 새 예산을 살 수 있으면 제한이 아니다.
    """
    return request.client.host if request.client else UNKNOWN_CLIENT_KEY


def _prune(hits: deque[float], cutoff: float) -> None:
    """윈도우를 벗어난 앞쪽 기록 제거 (deque 는 시간 오름차순)."""
    while hits and hits[0] <= cutoff:
        hits.popleft()


def _sweep(cutoff: float) -> None:
    """전 키를 훑어 만료 기록을 버리고 빈 키를 지운다 — 메모리 무한 증가 방지.

    윈도우당 1회로 상각(amortize)한다: IP 를 계속 바꿔가며 두드려도 남는 키는
    최근 두 윈도우 안에 실제로 요청한 IP 뿐이고, 요청당 비용은 O(1) 에 수렴한다.
    """
    for key in list(_hits):
        _prune(_hits[key], cutoff)
        if not _hits[key]:
            del _hits[key]


def allow(key: str, *, limit: int, window_seconds: float) -> bool:
    """이번 시도를 허용할지 판정하고, 허용이면 기록한다.

    허용된 시도만 기록한다 — 차단된 시도가 윈도우를 밀어내지 않으므로, 두드리기를
    멈추지 않는 공격자도 결국 ``limit / window`` 이상은 못 쓰고, 예산을 소진한
    사람은 가장 오래된 기록이 만료되는 대로 다시 시도할 수 있다.
    """
    global _last_sweep
    t = now()
    cutoff = t - window_seconds

    if t - _last_sweep >= window_seconds:
        _sweep(cutoff)
        _last_sweep = t

    hits = _hits.setdefault(key, deque())
    _prune(hits, cutoff)
    if len(hits) >= limit:
        return False
    hits.append(t)
    return True


def tracked_key_count() -> int:
    """현재 보관 중인 키 수 — 정리 동작의 관측점 (테스트/진단용)."""
    return len(_hits)
