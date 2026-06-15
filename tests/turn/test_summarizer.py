from app.turn.summarizer import load_summary_rules, summarize


def test_summary_rules_load_and_validate():
    rules = load_summary_rules()
    assert "{prior}" in rules.user_template
    assert "{conversation}" in rules.user_template
    assert rules.system_prompt.strip()


def test_summarize_passes_prior_and_conversation_to_llm():
    captured = {}

    def stub(system, user):
        captured["system"] = system
        captured["user"] = user
        return "- 요약 결과"

    out = summarize(
        "이전 기억",
        [{"role": "user", "content": "안녕"}, {"role": "assistant", "content": "어"}],
        llm_call=stub,
    )
    assert out == "- 요약 결과"
    assert "이전 기억" in captured["user"]
    assert "안녕" in captured["user"] and "어" in captured["user"]
    assert captured["system"] == load_summary_rules().system_prompt


def test_summarize_first_time_marks_no_prior():
    captured = {}

    def stub(system, user):
        captured["user"] = user
        return "x"

    summarize(None, [{"role": "user", "content": "hi"}], llm_call=stub)
    assert "첫 요약" in captured["user"]
