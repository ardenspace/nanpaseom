"""턴 JSON 계약 스키마 — llama-server response_format(json_schema) 용 (ADR 0027).

mechanic-spec line 114-128 의 reply/awareness_delta/reason/memory_tags/choices.
GBNF 제약 디코딩이 이 스키마로 출력을 강제한다. additionalProperties=False 로
잉여 필드 차단 (TurnReply 의 extra=forbid 와 정합).
"""

EMIT_TURN_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "awareness_delta": {"type": "integer"},
        "reason": {"type": "string"},
        "memory_tags": {"type": "array", "items": {"type": "string"}},
        "choices": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tone": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["tone", "text"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["reply", "awareness_delta", "reason", "memory_tags", "choices"],
    "additionalProperties": False,
}
