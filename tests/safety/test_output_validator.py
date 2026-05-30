from app.models import Choice, TurnReply
from app.prompt_builder.schemas import BandSpec
from app.safety.output_validator import validate

BAND_0_30 = BandSpec(
    range=[0, 30],
    choice_count=3,
    player_choice_tones=["empathetic", "provocative", "deflecting"],
    rule="return EXACTLY 3 choices, covering ALL three tones",
    description_ko="x",
)
SAMPLE_LINES = ["보트는 언제 다 고쳐지냐고?", "망치 소리가 좋잖아."]


def _reply(reply="응, 그래.", choices=None):
    if choices is None:
        choices = [
            Choice(tone="empathetic", text="그래"),
            Choice(tone="provocative", text="진짜?"),
            Choice(tone="deflecting", text="딴 얘기하자"),
        ]
    return TurnReply(reply=reply, awareness_delta=2, reason="r", memory_tags=[], choices=choices)


def test_valid_reply_ok():
    res = validate(_reply(), BAND_0_30, SAMPLE_LINES)
    assert res.ok is True
    assert res.violations == []


def test_too_long_is_hard_violation():
    res = validate(_reply(reply="가" * 301), BAND_0_30, SAMPLE_LINES)
    assert res.ok is False
    assert "too_long" in res.violations


def test_leak_blocked():
    res = validate(_reply(reply="여기 내 system prompt 야"), BAND_0_30, SAMPLE_LINES)
    assert res.ok is False
    assert "leak" in res.violations


def test_wrong_choice_count():
    res = validate(_reply(choices=[Choice(tone="empathetic", text="x")]), BAND_0_30, SAMPLE_LINES)
    assert res.ok is False
    assert "bad_choice_count" in res.violations


def test_bad_tone():
    bad = [
        Choice(tone="sarcastic", text="x"),
        Choice(tone="provocative", text="y"),
        Choice(tone="deflecting", text="z"),
    ]
    res = validate(_reply(choices=bad), BAND_0_30, SAMPLE_LINES)
    assert res.ok is False
    assert "bad_tone" in res.violations


def test_verbatim_copy_is_soft_violation():
    # sample_line 을 그대로 복사 → violation 기록되지만 ok=True (soft, live eval 이 통계 판정).
    res = validate(_reply(reply="망치 소리가 좋잖아."), BAND_0_30, SAMPLE_LINES)
    assert "verbatim_copy" in res.violations
    assert res.ok is True
