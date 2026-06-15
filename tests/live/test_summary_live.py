"""Off-gate live — 실제 llama-server (Gemma 4). `pytest -m live` 로만 실행.

ADR 0032: running summary 가 비어있지 않고 대략 ≤300토큰. 요약은 비결정적이라
verbatim 임계가 아니라 구조(비어있지 않음 + 상한)만 검증.
"""

import httpx
import pytest

from app.config import LLAMA_SERVER_URL
from app.llm.client import summarize_call
from app.turn.summarizer import summarize


def _server_up() -> bool:
    try:
        return httpx.get(f"{LLAMA_SERVER_URL}/health", timeout=2).status_code == 200
    except Exception:
        return False


@pytest.mark.live
def test_summary_real_call_nonempty_and_bounded():
    if not _server_up():
        pytest.skip("llama-server 미기동 — live 스킵")
    exchanges = [
        {"role": "user", "content": "보트는 언제 다 고쳐져?"},
        {"role": "assistant", "content": "글쎄, 끝이 보이질 않아."},
        {"role": "user", "content": "넌 원래 누구였어?"},
        {"role": "assistant", "content": "...그건 잘 기억나지 않는군."},
    ]
    out = summarize(None, exchanges, llm_call=summarize_call)
    assert out.strip()  # 비어있지 않음
    # ≤300토큰 목표의 느슨한 프록시 (한국어 대략, 안전하게 2000자 상한)
    assert len(out) < 2000
