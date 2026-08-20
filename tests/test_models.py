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


def test_turn_response_shape_has_no_session_uuid():
    """B1/B6 — 자격증명은 응답 모델에 없다 (extra=forbid 라 실으려 하면 에러)."""
    resp = TurnResponse(reply="hi", choices=[Choice(tone="t", text="x")])
    assert "session_uuid" not in resp.model_dump()
    with pytest.raises(ValidationError):
        TurnResponse(reply="hi", choices=[], session_uuid="u")


def test_turn_response_defaults_to_npc_kind():
    from app.models import TurnResponse
    resp = TurnResponse(reply="hi", choices=[])
    assert resp.kind == "npc"
    assert resp.matched_term is None


def test_turn_response_warning_kind():
    from app.models import TurnResponse
    resp = TurnResponse(kind="warning", reply="경고", choices=[], matched_term="씨발")
    assert resp.kind == "warning"
    assert resp.matched_term == "씨발"


def test_session_state_defaults():
    from app.models import SessionState
    s = SessionState(warning_count=0, first_strike_term=None, banned=False, ban_reason=None)
    assert s.banned is False
