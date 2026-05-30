from app.llm.tool_schema import EMIT_TURN_SCHEMA


def test_emit_turn_schema_required_fields():
    assert set(EMIT_TURN_SCHEMA["required"]) == {
        "reply", "awareness_delta", "reason", "memory_tags", "choices",
    }
    props = EMIT_TURN_SCHEMA["properties"]
    assert props["awareness_delta"]["type"] == "integer"
    assert props["choices"]["items"]["required"] == ["tone", "text"]
    assert EMIT_TURN_SCHEMA["additionalProperties"] is False
