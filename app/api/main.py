"""FastAPI — POST /turn. ban 게이트 → 2-strike → (clean) run_turn 오케스트레이션."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.models import TurnResponse
from app.safety import strike
from app.safety.moderation import denylist_checker, detect
from app.safety.rules import load_safety_rules
from app.store import db, repo
from app.turn.loop import run_turn

app = FastAPI(title="난파섬 Sub-2b slice")


class TurnRequest(BaseModel):
    session_uuid: str | None = None
    npc_id: str
    player_input: str


@app.post("/turn")
def turn(req: TurnRequest) -> dict:
    with db.connect() as conn:
        session_uuid = req.session_uuid or repo.mint_session(conn)
        repo.ensure_session(conn, session_uuid)

        # 1) ban 게이트 — 차단된 세션은 모든 호출 차단.
        sess = repo.load_session(conn, session_uuid)
        if sess.banned:
            return TurnResponse(
                kind="ban", reply=sess.ban_reason or "", choices=[], session_uuid=session_uuid
            ).model_dump()

        # 2) strike 평가 (결정적 디니리스트).
        rules = load_safety_rules()
        verdict = detect(req.player_input, [denylist_checker(rules.harassment_denylist)])
        if verdict.category != "clean":
            result = strike.register(conn, session_uuid, verdict)
            return TurnResponse(
                kind=result.kind,
                reply=result.message,
                choices=[],
                session_uuid=session_uuid,
                matched_term=result.matched_term,
            ).model_dump()

        # 3) clean → 기존 NPC 턴 (Layer 1 길이/페르소나 + LLM + Layer 4).
        resp = run_turn(conn, session_uuid, req.npc_id, req.player_input)
        return resp.model_dump()
