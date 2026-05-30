"""llama-server json_schema 호출 wrapper.

system + messages → /v1/chat/completions (response_format=json_schema) → TurnReply.
서버 에러/timeout/schema-위반 = LLMError (turn loop 이 diegetic fallback).
"""

import json

import httpx

from app.config import LLAMA_SERVER_URL, MODEL
from app.llm.tool_schema import EMIT_TURN_SCHEMA
from app.models import TurnReply


class LLMError(Exception):
    pass


def call(system: str, messages: list[dict]) -> TurnReply:
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, *messages],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "emit_turn", "schema": EMIT_TURN_SCHEMA, "strict": True},
        },
        "temperature": 0.7,  # mechanic-spec: 약간의 자연 변동 허용
        "max_tokens": 1024,
    }
    try:
        resp = httpx.post(f"{LLAMA_SERVER_URL}/v1/chat/completions", json=payload, timeout=120)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:  # 연결/타임아웃/HTTP 에러
        raise LLMError(str(e)) from e

    try:  # json_schema 제약이 있어 이론상 드묾
        return TurnReply.model_validate(json.loads(content))
    except Exception as e:
        raise LLMError(f"emit_turn output invalid: {e}") from e
