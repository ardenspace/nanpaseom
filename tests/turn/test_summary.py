import uuid

from app.llm.client import LLMError
from app.models import Choice, TurnReply
from app.store import repo
from app.turn.loop import run_turn


def _reply():
    return TurnReply(
        reply="망치질은 멈추지 않아.", awareness_delta=1, reason="r", memory_tags=[],
        choices=[Choice(tone="empathetic", text="a"), Choice(tone="provocative", text="b"),
                 Choice(tone="deflecting", text="c")],
    )


def _llm(system, messages):
    return _reply()


def _drive(conn, sid, n, summarize_call):
    for i in range(n):
        run_turn(conn, sid, "surigong", f"입력 {i}", llm_call=_llm, summarize_call=summarize_call)


def test_summary_triggers_on_10th_exchange(conn):
    sid = str(uuid.uuid4())
    calls = []

    def stub(system, user):
        calls.append(user)
        return "- 플레이어는 보트에 관심이 있다"

    _drive(conn, sid, 10, stub)
    assert len(calls) == 1
    assert repo.load_npc_state(conn, sid, "surigong").summary == "- 플레이어는 보트에 관심이 있다"


def test_no_summary_before_10th(conn):
    sid = str(uuid.uuid4())

    def stub(system, user):
        raise AssertionError("10 exchange 전엔 요약 안 함")

    _drive(conn, sid, 9, stub)
    assert repo.load_npc_state(conn, sid, "surigong").summary is None


def test_summary_injected_into_next_prompt(conn):
    sid = str(uuid.uuid4())

    def stub(system, user):
        return "- 기억된 사실"

    _drive(conn, sid, 10, stub)

    captured = {}

    def capturing(system, messages):
        captured["system"] = system
        return _reply()

    run_turn(conn, sid, "surigong", "다음", llm_call=capturing, summarize_call=stub)
    assert "- 기억된 사실" in captured["system"]


def test_summary_failure_keeps_old_and_turn_succeeds(conn):
    sid = str(uuid.uuid4())

    def failing(system, user):
        raise LLMError("summary timeout")

    resp = None
    for i in range(10):
        resp = run_turn(conn, sid, "surigong", f"x{i}", llm_call=_llm, summarize_call=failing)
    assert resp.reply  # 턴 정상 반환
    assert repo.load_npc_state(conn, sid, "surigong").summary is None  # 갱신 안 됨


def test_rolling_passes_prior_summary_on_20th(conn):
    sid = str(uuid.uuid4())
    seen = []

    def stub(system, user):
        seen.append(user)
        return f"summary-{len(seen)}"

    _drive(conn, sid, 20, stub)
    assert len(seen) == 2
    # 2번째 요약 입력에 1번째 요약(prior)이 통합됨 (rolling)
    assert "summary-1" in seen[1]
