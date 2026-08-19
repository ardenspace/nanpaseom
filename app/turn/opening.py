"""세션 오프닝 턴 — POST /session/bootstrap 전용 (B2).

플레이어 입력이 없는 첫 NPC 발화. run_turn 과 달리 실패(LLM/Layer 4)는 diegetic
fallback 이 아니라 OpeningError 로 표면화한다 — 엔드포인트가 503 으로 변환.
오프닝 instruction / 오류 문구는 rules/opening.yaml (코드 하드코딩 금지).

영속화: 정상 npc 턴과 동일하게 chat_logs(assistant 행) + npc_state. 단 awareness
delta 는 미적용 — awareness 는 플레이어 상호작용에 반응하는 값이고 오프닝엔
플레이어 행동이 없다 (mechanic-spec awareness 정의와 정합).
"""

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from app.llm import client as llm_client
from app.models import TurnResponse
from app.safety import output_validator
from app.store import repo
from app.turn.loop import build_turn_context

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"


class OpeningError(Exception):
    """오프닝 생성 실패 — 엔드포인트가 503 {status: error} 로 표면화."""


class OpeningRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    instruction: str
    error_message: str


@lru_cache(maxsize=1)
def load_opening_rules() -> OpeningRules:
    raw = yaml.safe_load((RULES_DIR / "opening.yaml").read_text())
    return OpeningRules.model_validate(raw)


def run_opening(conn, session_uuid: str, npc_id: str, *, llm_call=None) -> TurnResponse:
    """서버 주도 오프닝 턴 생성 + 영속. 실패 시 OpeningError (상태 변화 없음)."""
    if llm_call is None:
        llm_call = llm_client.call

    ctx = build_turn_context(conn, session_uuid, npc_id)
    messages = [{"role": "user", "content": load_opening_rules().instruction}]

    try:
        reply = llm_call(ctx.system, messages)
    except llm_client.LLMError as e:
        raise OpeningError(str(e)) from e

    # Layer 4 — 오프닝은 fallback 하지 않고 실패로 취급 (choices 없는 "new" 는 계약 위반).
    result = output_validator.validate(reply, ctx.band, ctx.band_npc.sample_lines)
    if not result.ok:
        raise OpeningError("opening reply failed output validation")

    # 정상 npc 턴과 동일 영속 (npc_state 행 생성 + assistant chat_log). delta 미적용.
    repo.save_npc_state(conn, session_uuid, npc_id, ctx.state.awareness, ctx.state.memory_tags)
    turn_index = repo.next_turn_index(conn, session_uuid, npc_id)
    repo.append_chat_log(
        conn, session_uuid, npc_id, turn_index, "assistant", reply.reply, reply.model_dump()
    )
    return TurnResponse(reply=reply.reply, choices=reply.choices, session_uuid=session_uuid)
