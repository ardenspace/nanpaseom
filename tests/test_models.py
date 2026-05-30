import pytest
from pydantic import ValidationError

from app.models import Choice, NpcState, TurnReply, TurnResponse


def test_turn_reply_parses_tool_input():
    r = TurnReply.model_validate(
        {
            "reply": "망치질은 계속돼.",
            "awareness_delta": 5,
            "reason": "trope_question",
            "memory_tags": ["purpose"],
            "choices": [{"tone": "empathetic", "text": "그래"}],
        }
    )
    assert r.awareness_delta == 5
    assert r.choices[0].tone == "empathetic"


def test_turn_reply_rejects_extra_field():
    with pytest.raises(ValidationError):
        TurnReply.model_validate(
            {
                "reply": "x", "awareness_delta": 1, "reason": "y",
                "memory_tags": [], "choices": [], "bogus": 1,
            }
        )


def test_npc_state_defaults():
    s = NpcState(awareness=0, memory_tags=[])
    assert s.summary is None


def test_turn_response_shape():
    resp = TurnResponse(reply="hi", choices=[Choice(tone="t", text="x")], session_uuid="u")
    assert resp.session_uuid == "u"
