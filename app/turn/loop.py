"""turn loop — Sub-2 slice 의 오케스트레이션.

build_prompt(Sub-1) → messages → llm_call(json_schema) → Layer 4 → clamp → persist.
llm_call 은 의존성 주입 (gate 테스트는 stub, 프로덕션은 app.llm.client.call).
"""

from dataclasses import dataclass

from app.llm import client as llm_client
from app.models import NpcState, TurnResponse
from app.prompt_builder.loader import load_npc, load_rules
from app.prompt_builder.renderer import build_prompt, resolve_band
from app.safety import input_filter, output_validator
from app.store import repo
from app.turn import summarizer

# 낚시/루비 economy 는 out-of-scope (spec edge case) — build_prompt 필수 hook 을 0 으로 stub.
RUBY_HOOK_STUB = {"player_total_rubies_given_to_this_npc": 0}
SUMMARIZE_EVERY = 10  # exchanges (mechanic-spec "Context Window Management")


@dataclass
class TurnContext:
    """한 턴의 프롬프트 컨텍스트 — run_turn 과 run_opening(bootstrap) 이 공유."""
    npc: object
    rules: object
    state: NpcState
    band: object
    band_npc: object
    system: str


def build_turn_context(conn, session_uuid: str, npc_id: str) -> TurnContext:
    """yaml + runtime state → (band, band_npc, system prompt) 조립."""
    npc = load_npc(npc_id)
    rules = load_rules()
    state = repo.load_npc_state(conn, session_uuid, npc_id)
    band = resolve_band(state.awareness, rules.awareness_bands.bands)
    band_npc = next(b for b in npc.voice.awakening_bands if b.range == band.range)
    system = build_prompt(npc_id, state.awareness, state.memory_tags, RUBY_HOOK_STUB, summary=state.summary)
    return TurnContext(npc=npc, rules=rules, state=state, band=band, band_npc=band_npc, system=system)


def _maybe_summarize(conn, sid, npc_id, prior_summary, summarize_call) -> None:
    """10 exchange 마다 rolling 요약. best-effort post-step — 어떤 실패도(LLM·DB 등)
    turn 무영향 (요약은 turn 영속화 이후 실행, ADR 0032). 실패 시 기존 summary 유지."""
    try:
        count = repo.count_exchanges(conn, sid, npc_id)
        if count == 0 or count % SUMMARIZE_EVERY != 0:
            return
        # 2x: 직전 10 exchange = 최근 20 chat row (rolling delta)
        delta = repo.load_recent_turns(conn, sid, npc_id, limit=SUMMARIZE_EVERY * 2)
        new_summary = summarizer.summarize(prior_summary, delta, llm_call=summarize_call)
        repo.save_summary(conn, sid, npc_id, new_summary)
    except Exception:
        return  # 기존 summary 유지 — 대화 무영향


def merge_memory_tags(existing: list[str], new: list[str], vocab: list[str], max_per_turn: int = 3) -> list[str]:
    """vocab 필터 + 턴당 max 3 + append-only dedupe (mechanic-spec line 130)."""
    filtered = [t for t in new if t in vocab][:max_per_turn]
    out = list(existing)
    for t in filtered:
        if t not in out:
            out.append(t)
    return out


def _log_exchange(conn, sid, npc_id, player_input, npc_reply, reply_raw):
    ti = repo.next_turn_index(conn, sid, npc_id)
    repo.append_chat_log(conn, sid, npc_id, ti, "user", player_input)
    repo.append_chat_log(conn, sid, npc_id, ti + 1, "assistant", npc_reply, reply_raw)


def run_turn(conn, session_uuid: str, npc_id: str, player_input: str, *, llm_call=None, summarize_call=None) -> TurnResponse:
    if llm_call is None:
        llm_call = llm_client.call
    if summarize_call is None:
        summarize_call = llm_client.summarize_call

    ctx = build_turn_context(conn, session_uuid, npc_id)
    rules, state = ctx.rules, ctx.state
    fallback_line = ctx.npc.diegetic_fallback

    # Layer 1 — 차단 시 turn 무효 (로그/상태 변화 없음).
    if input_filter.check(player_input).blocked:
        return TurnResponse(reply=fallback_line, choices=[], session_uuid=session_uuid)

    window = repo.load_recent_turns(conn, session_uuid, npc_id, limit=8)
    system = ctx.system
    messages = window + [{"role": "user", "content": player_input}]

    # LLM 호출 — API/timeout 에러는 diegetic fallback (turn_index 진행, awareness 불변).
    try:
        reply = llm_call(system, messages)
    except llm_client.LLMError:
        _log_exchange(conn, session_uuid, npc_id, player_input, fallback_line, None)
        return TurnResponse(reply=fallback_line, choices=[], session_uuid=session_uuid)

    # Layer 4 — HARD violation 시 diegetic fallback (delta 미적용, turn 로그).
    result = output_validator.validate(reply, ctx.band, ctx.band_npc.sample_lines)
    if not result.ok:
        _log_exchange(conn, session_uuid, npc_id, player_input, fallback_line, None)
        return TurnResponse(reply=fallback_line, choices=[], session_uuid=session_uuid)

    # 정상 — clamp + 영속.
    delta = max(-10, min(10, reply.awareness_delta))
    new_awareness = max(0, min(100, state.awareness + delta))
    new_tags = merge_memory_tags(state.memory_tags, reply.memory_tags, rules.memory_tags.vocabulary)
    repo.save_npc_state(conn, session_uuid, npc_id, new_awareness, new_tags)
    _log_exchange(conn, session_uuid, npc_id, player_input, reply.reply, reply.model_dump())
    _maybe_summarize(conn, session_uuid, npc_id, state.summary, summarize_call)

    return TurnResponse(reply=reply.reply, choices=reply.choices, session_uuid=session_uuid)
