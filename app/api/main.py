"""FastAPI — POST /turn (ban 게이트 → 2-strike → run_turn) + POST /session/bootstrap (B2)
+ GET / 정적 서빙 (B4)."""

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.models import TurnResponse
from app.safety import strike
from app.safety.moderation import denylist_checker, detect
from app.safety.rules import load_safety_rules
from app.store import db, repo
from app.turn.loop import run_turn
from app.turn.opening import OpeningError, load_opening_rules, run_opening

app = FastAPI(title="난파섬 Sub-2b slice")

# B2: 쿠키가 신원. 이번 런은 수리공 단독 — npc 는 서버가 결정.
COOKIE_NAME = "session_uuid"
BOOTSTRAP_NPC_ID = "surigong"

# B4: Vite 빌드 산출물. env 는 request 시점 resolve (test_static 계약).
STATIC_DIR_ENV = "NANPASEOM_STATIC_DIR"
DEFAULT_STATIC_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"


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


def _cookie_session_uuid(request: Request) -> str | None:
    """쿠키의 session_uuid — 유효한 UUID 가 아니면 무시 (신규 취급)."""
    raw = request.cookies.get(COOKIE_NAME)
    if raw is None:
        return None
    try:
        uuid.UUID(raw)
    except ValueError:
        return None
    return raw


def _bootstrap_response(payload: dict, session_uuid: str, status_code: int = 200) -> JSONResponse:
    """B2 응답 + 쿠키 발급/재발급. 503 에도 쿠키를 심어 재시도 시 같은 세션 재사용."""
    resp = JSONResponse(status_code=status_code, content=payload)
    resp.set_cookie(COOKIE_NAME, session_uuid, httponly=True, samesite="lax")
    return resp


@app.post("/session/bootstrap")
def bootstrap(request: Request) -> JSONResponse:
    """B2 — 쿠키가 신원. new(오프닝 생성) / resumed(LLM 콜 없음) / banned / 503 error."""
    npc_id = BOOTSTRAP_NPC_ID
    with db.connect() as conn:
        session_uuid = _cookie_session_uuid(request) or repo.mint_session(conn)
        repo.ensure_session(conn, session_uuid)

        sess = repo.load_session(conn, session_uuid)
        if sess.banned:
            return _bootstrap_response(
                {"status": "banned", "session_uuid": session_uuid, "npc_id": npc_id,
                 "ban_reason": sess.ban_reason or ""},
                session_uuid,
            )

        history = repo.load_recent_turns(conn, session_uuid, npc_id, limit=8)
        if history:  # 턴 ≥ 1 → resumed (LLM 호출 없음)
            return _bootstrap_response(
                {"status": "resumed", "session_uuid": session_uuid, "npc_id": npc_id,
                 "history": history,
                 "choices": repo.load_last_reply_choices(conn, session_uuid, npc_id)},
                session_uuid,
            )

        # 턴 0개 (신규 / 미지의 쿠키 / 이전 오프닝 실패) → 같은 세션으로 오프닝 (재)시도.
        try:
            opening = run_opening(conn, session_uuid, npc_id)
        except OpeningError:
            return _bootstrap_response(
                {"status": "error", "message": load_opening_rules().error_message},
                session_uuid, status_code=503,
            )
        return _bootstrap_response(
            {"status": "new", "session_uuid": session_uuid, "npc_id": npc_id,
             "reply": opening.reply,
             "choices": [c.model_dump() for c in opening.choices]},
            session_uuid,
        )


@app.get("/")
def index() -> FileResponse:
    """B4 — 빌드 산출물 index.html 서빙. 디렉토리는 request 시점 env resolve."""
    static_dir = Path(os.environ.get(STATIC_DIR_ENV) or DEFAULT_STATIC_DIR)
    index_html = static_dir / "index.html"
    if not index_html.is_file():
        raise HTTPException(status_code=404, detail="static build not found")
    return FileResponse(index_html)


@app.get("/assets/{asset_path:path}")
def assets(asset_path: str) -> FileResponse:
    """B4 — 빌드 번들(js/css) + public 에셋 서빙.

    StaticFiles mount 는 디렉토리를 import 시점에 고정하므로 쓰지 않고,
    index 와 같은 request-시점 env resolve 패턴 유지 (test_static 계약).
    """
    static_dir = Path(os.environ.get(STATIC_DIR_ENV) or DEFAULT_STATIC_DIR)
    assets_dir = (static_dir / "assets").resolve()
    target = (assets_dir / asset_path).resolve()
    # 경로 탈출(../) 방지 — assets_dir 밖이면 무조건 404.
    if not target.is_relative_to(assets_dir) or not target.is_file():
        raise HTTPException(status_code=404, detail="asset not found")
    return FileResponse(target)
