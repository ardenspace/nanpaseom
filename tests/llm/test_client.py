"""client.call 페이로드 구성 회귀 — 결정적 (네트워크 stub).

ADR 0029: gemma-4 / qwen3 는 thinking 모델. thinking 을 끄지 않으면 모델이
reasoning 으로 토큰 예산을 소진하고 `content` 를 비운 채 끝나 매 턴 fallback 한다.
client 는 thinking 을 비활성화하는 chat_template_kwargs 를 반드시 보내야 한다.
"""

import json

from app.llm import client as llm_client
from app.llm.tool_schema import EMIT_TURN_SCHEMA  # noqa: F401  (스키마 존재 보장)

_VALID_TURN = {
    "reply": "응.",
    "awareness_delta": 1,
    "reason": "r",
    "memory_tags": [],
    "choices": [{"tone": "empathetic", "text": "x"}],
}


class _FakeResp:
    def __init__(self, content):
        self._content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


def test_call_payload_disables_thinking(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):  # noqa: A002
        captured["payload"] = json
        return _FakeResp(json_dumps(_VALID_TURN))

    monkeypatch.setattr(llm_client.httpx, "post", fake_post)
    llm_client.call("sys", [{"role": "user", "content": "안녕"}])

    payload = captured["payload"]
    assert payload["chat_template_kwargs"]["enable_thinking"] is False


def json_dumps(obj):
    return json.dumps(obj)
