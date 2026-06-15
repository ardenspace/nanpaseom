from app.prompt_builder.renderer import build_prompt
from app.turn.loop import RUBY_HOOK_STUB


def test_summary_none_renders_unchanged():
    # summary 미전달 == summary=None == 기존 출력
    assert build_prompt("surigong", 10, [], RUBY_HOOK_STUB) == build_prompt(
        "surigong", 10, [], RUBY_HOOK_STUB, summary=None
    )


def test_summary_present_is_injected():
    out = build_prompt("surigong", 10, [], RUBY_HOOK_STUB, summary="- 플레이어는 떠남을 물었다")
    assert "- 플레이어는 떠남을 물었다" in out
    assert "기억 요약" in out


def test_summary_present_adds_lines_over_none():
    none_out = build_prompt("surigong", 10, [], RUBY_HOOK_STUB, summary=None)
    sum_out = build_prompt("surigong", 10, [], RUBY_HOOK_STUB, summary="- x")
    assert len(sum_out) > len(none_out)
