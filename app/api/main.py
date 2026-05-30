"""FastAPI — POST /turn. slice 는 단일 엔드포인트, 인증/쿠키 없음."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.store import db, repo
from app.turn.loop import run_turn

app = FastAPI(title="난파섬 Sub-2 slice")


class TurnRequest(BaseModel):
    session_uuid: str | None = None
    npc_id: str
    player_input: str


@app.post("/turn")
def turn(req: TurnRequest) -> dict:
    with db.connect() as conn:
        session_uuid = req.session_uuid or repo.mint_session(conn)
        resp = run_turn(conn, session_uuid, req.npc_id, req.player_input)
        return resp.model_dump()
