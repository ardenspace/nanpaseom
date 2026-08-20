"""FastAPI — POST /turn (ban 게이트 → 2-strike → run_turn) + POST /session/bootstrap (B2)
+ GET / 정적 서빙 (B4)."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from app.api.identity import load_identity_rules, resolve_session
from app.api.session_cookie import set_session_cookie
from app.models import TurnResponse
from app.save_code import SAVE_CODE_RE, generate_save_code, load_save_code_rules
from app.safety import strike
from app.safety.moderation import denylist_checker, detect
from app.safety.rules import load_safety_rules
from app.store import db, repo
from app.turn.loop import run_turn
from app.turn.opening import OpeningError, load_opening_rules, run_opening

# Req 12: 자동 문서(/docs, /redoc, /openapi.json) 비활성화 — 공개 표면에서 스키마 노출 차단.
app = FastAPI(title="난파섬 Sub-2b slice", docs_url=None, redoc_url=None, openapi_url=None)

# B1/B2: 쿠키가 신원 (이름/수명/속성은 app/api/session_cookie.py 단일 홈).
# 런타임에 배선된 NPC 목록 단일 홈 — yaml 존재만으로는 불충분 (eobu.yaml 이 있어도 404).
# 이번 런은 수리공 단독 — bootstrap npc 도 서버가 여기서 결정.
WIRED_NPC_IDS = ("surigong",)
BOOTSTRAP_NPC_ID = WIRED_NPC_IDS[0]

# B4: Vite 빌드 산출물. env 는 request 시점 resolve (test_static 계약).
STATIC_DIR_ENV = "NANPASEOM_STATIC_DIR"
DEFAULT_STATIC_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"

# B5: /assets 확장자 화이트리스트 — 이미지 + 폰트 + 빌드 산출물만.
# 그 외 확장자·무확장자(문서류 md/txt 포함)는 실파일이 있어도 404.
# 판정은 resolve 된 실파일 suffix 기준 + 소문자 정규화 (심링크 우회 차단).
ASSET_EXT_WHITELIST = frozenset({
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico",  # 이미지
    ".woff", ".woff2",                                          # 폰트
    ".js", ".css", ".map",                                      # 빌드 산출물
})


class TurnRequest(BaseModel):
    """B1 — 본문은 {npc_id, player_input} 뿐. 세션 번호 필드가 와도 무시
    (pydantic 기본 extra 무시 — 신원은 쿠키 단일, 본문은 신원에 사용되지 않는다)."""
    npc_id: str
    player_input: str


@app.post("/turn")
def turn(req: TurnRequest, request: Request):
    with db.connect() as conn:
        # 0) 신원 판정이 npc_id 검증보다 먼저 — 무인증에 404 로 NPC 목록을 노출하지 않는다.
        session_uuid = resolve_session(conn, request)
        if session_uuid is None:
            # 쿠키 없음 / UUID 형식 아님 / 모르는 세션 → 401, 세션 생성 없음.
            return JSONResponse(
                status_code=401,
                content={"status": "error",
                         "message": load_identity_rules().no_session_message},
            )

        # 1) npc_id — 런타임 배선 목록 검증 (yaml 존재만으로는 불충분).
        if req.npc_id not in WIRED_NPC_IDS:
            return JSONResponse(
                status_code=404,
                content={"status": "error",
                         "message": load_identity_rules().unknown_npc_message},
            )

        # 2) ban 게이트 — 차단된 세션은 모든 호출 차단.
        sess = repo.load_session(conn, session_uuid)
        if sess.banned:
            return TurnResponse(kind="ban", reply=sess.ban_reason or "", choices=[]).model_dump()

        # 3) strike 평가 (결정적 디니리스트).
        rules = load_safety_rules()
        verdict = detect(req.player_input, [denylist_checker(rules.harassment_denylist)])
        if verdict.category != "clean":
            result = strike.register(conn, session_uuid, verdict)
            return TurnResponse(
                kind=result.kind,
                reply=result.message,
                choices=[],
                matched_term=result.matched_term,
            ).model_dump()

        # 4) clean → 기존 NPC 턴 (Layer 1 길이/페르소나 + LLM + Layer 4).
        resp = run_turn(conn, session_uuid, req.npc_id, req.player_input)
        return resp.model_dump()


def _bootstrap_response(payload: dict, session_uuid: str, status_code: int = 200) -> JSONResponse:
    """B2 응답 + 쿠키 발급/재발급. 503 에도 쿠키를 심어 재시도 시 같은 세션 재사용."""
    resp = JSONResponse(status_code=status_code, content=payload)
    set_session_cookie(resp, session_uuid)
    return resp


def _resumed_payload(conn, session_uuid: str, npc_id: str) -> dict | None:
    """턴 ≥ 1 세션의 resumed 응답 body (LLM 콜 없음). 턴 0개면 None.

    B6: 자격증명 session_uuid 는 응답 본문에 싣지 않는다 — 신원은 쿠키로만 오간다.
    """
    history = repo.load_recent_turns(conn, session_uuid, npc_id, limit=8)
    if not history:
        return None
    return {"status": "resumed", "npc_id": npc_id,
            "history": history,
            "choices": repo.load_last_reply_choices(conn, session_uuid, npc_id)}


def _new_payload(conn, session_uuid: str, npc_id: str) -> dict:
    """턴 0개 세션 → 오프닝 생성 + new 응답 body. 실패 시 OpeningError 전파."""
    opening = run_opening(conn, session_uuid, npc_id)
    return {"status": "new", "npc_id": npc_id,
            "reply": opening.reply,
            "choices": [c.model_dump() for c in opening.choices]}


@app.post("/session/bootstrap")
def bootstrap(request: Request) -> JSONResponse:
    """B2 — 쿠키가 신원. new(오프닝 생성) / resumed(LLM 콜 없음) / banned / 503 error.

    유일한 세션 생성 문: 해석기 거부(쿠키 없음/형식 불량/모르는 세션)면 클라이언트
    값은 버리고 서버가 새 UUID 를 민팅한다 — 클라이언트가 고른 값이 세션 행이
    되는 일은 없다 (스테일 쿠키 채택 폐지).
    """
    npc_id = BOOTSTRAP_NPC_ID
    with db.connect() as conn:
        session_uuid = resolve_session(conn, request)
        if session_uuid is None:
            session_uuid = repo.mint_session(conn)
            repo.ensure_session(conn, session_uuid)

        sess = repo.load_session(conn, session_uuid)
        if sess.banned:
            return _bootstrap_response(
                {"status": "banned", "npc_id": npc_id, "ban_reason": sess.ban_reason or ""},
                session_uuid,
            )

        payload = _resumed_payload(conn, session_uuid, npc_id)
        if payload is None:
            # 턴 0개 (신규 / 미지의 쿠키 / 이전 오프닝 실패) → 같은 세션으로 오프닝 (재)시도.
            try:
                payload = _new_payload(conn, session_uuid, npc_id)
            except OpeningError:
                return _bootstrap_response(
                    {"status": "error", "message": load_opening_rules().error_message},
                    session_uuid, status_code=503,
                )
        return _bootstrap_response(payload, session_uuid)


# --------------------------------------------------------------- B3 세이브 코드

SAVE_CODE_MINT_ATTEMPTS = 20  # 31^8 공간 — 충돌 자체가 희귀, 상한은 안전장치


class RedeemRequest(BaseModel):
    code: str


def _mint_save_code(conn, session_uuid: str) -> str:
    """UNIQUE 충돌 시 재시도하며 세션에 새 코드 부여."""
    for _ in range(SAVE_CODE_MINT_ATTEMPTS):
        code = generate_save_code()
        try:
            repo.set_save_code(conn, session_uuid, code)
        except UniqueViolation:
            continue
        return code
    raise HTTPException(status_code=500, detail="save code minting exhausted retries")


@app.post("/save-code")
def issue_save_code(request: Request) -> JSONResponse:
    """B3 발급 — 신원은 해석기(B7) 통과분만. 거부 시 401 + 세션 생성/쿠키 발급 없음.

    거부(쿠키 없음/형식 불량/모르는 세션)는 /turn 401 과 같은 결 — 문구도
    rules/identity.yaml no_session_message 재사용 (같은 사실 한 곳).
    재발급은 기존 코드 반환 (idempotent — 이미 적어 둔 코드가 계속 유효).
    """
    with db.connect() as conn:
        session_uuid = resolve_session(conn, request)
        if session_uuid is None:
            return JSONResponse(
                status_code=401,
                content={"status": "error",
                         "message": load_identity_rules().no_session_message},
            )
        sess = repo.load_session(conn, session_uuid)
        if sess.banned:
            return JSONResponse(content={"status": "banned", "ban_reason": sess.ban_reason or ""})
        code = repo.get_save_code(conn, session_uuid) or _mint_save_code(conn, session_uuid)
        return JSONResponse(content={"status": "ok", "save_code": code})


def _redeem_not_found() -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"status": "error",
                 "message": load_save_code_rules().redeem_not_found_message},
    )


@app.post("/save-code/redeem")
def redeem_save_code(req: RedeemRequest) -> JSONResponse:
    """B3 redeem — 코드로 세션 복원. 쿠키 재바인딩은 성공(new/resumed) 응답에만."""
    if not SAVE_CODE_RE.fullmatch(req.code):
        return _redeem_not_found()  # 형식 위반 = 미지의 코드와 동일 404 (DB 조회 불필요)
    with db.connect() as conn:
        session_uuid = repo.find_session_by_save_code(conn, req.code)
        if session_uuid is None:
            return _redeem_not_found()

        sess = repo.load_session(conn, session_uuid)
        if sess.banned:  # 재바인딩 없음 — 밴 세션으로 갈아타지 않는다.
            return JSONResponse(content={"status": "banned", "ban_reason": sess.ban_reason or ""})

        npc_id = BOOTSTRAP_NPC_ID
        payload = _resumed_payload(conn, session_uuid, npc_id)
        if payload is None:
            try:
                payload = _new_payload(conn, session_uuid, npc_id)
            except OpeningError:
                # bootstrap 503 과 달리 쿠키를 심지 않는다 — 기존 세션 유지.
                return JSONResponse(
                    status_code=503,
                    content={"status": "error", "message": load_opening_rules().error_message},
                )
        return _bootstrap_response(payload, session_uuid)  # 성공 → 쿠키 재바인딩


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
    # B5: 확장자 화이트리스트 — resolve 된 실파일 suffix 기준(심링크 우회 차단), 대소문자 무시.
    if target.suffix.lower() not in ASSET_EXT_WHITELIST:
        raise HTTPException(status_code=404, detail="asset not found")
    return FileResponse(target)
