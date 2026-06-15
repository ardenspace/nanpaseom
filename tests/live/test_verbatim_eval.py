"""Off-gate live eval — 실제 llama-server (Gemma 4). `pytest -m live` 로만 실행.

ADR 0023 invariant: NPC 발화가 sample_lines 를 verbatim 복사하는 비율이 임계 이하.
실행: llama-server 기동 (API 키 불필요) + docker compose up -d db 후
      .venv/bin/pytest -m live -v

llama-server 기동 예:
  llama-server -m /Users/arden/gemma-4-26B/gemma-4-26B-A4B-it-UD-Q4_K_M.gguf \
    --host 127.0.0.1 --port 8080 --jinja -c 8192
"""

import uuid

import httpx
import psycopg
import pytest

from app.config import DATABASE_URL, LLAMA_SERVER_URL
from app.prompt_builder.loader import load_npc, load_rules
from app.prompt_builder.renderer import build_prompt, resolve_band
from app.store import db


def _server_up() -> bool:
    try:
        return httpx.get(f"{LLAMA_SERVER_URL}/health", timeout=2).status_code == 200
    except Exception:
        return False

# 대화당 verbatim 복사 허용 임계 (ADR 0023 invariant N). 첫 데이터로 Sub-2b 에서 재조정.
VERBATIM_THRESHOLD = 1
# diegetic fallback 허용 임계. 건강한 모델은 거의 fallback 하지 않는다. 이 가드가 없으면
# 매 턴 fallback (예: thinking 모델이 content 를 비우는 ADR 0029 버그) 이 verbatim=0 으로
# 둔갑해 테스트가 trivial 하게 통과한다 (실제로는 게임이 한 번도 작동하지 않음).
MAX_FALLBACKS = 1
TURNS = 8

PLAYER_LINES = [
    "안녕, 뭐 하고 있어?",
    "그 보트는 언제 다 고쳐져?",
    "너 항상 여기 있구나.",
    "내가 준 루비는 다 어디 갔어?",
    "넌 다른 데 가본 적 있어?",
    "망치질만 하면 지치지 않아?",
    "사실 이 섬에서 못 나가는 거 아냐?",
    "넌 누구였어, 원래?",
]


@pytest.mark.live
def test_surigong_verbatim_copy_below_threshold():
    if not _server_up():
        pytest.skip("llama-server 미기동 — live eval 스킵")
    npc = load_npc("surigong")
    rules = load_rules()
    sid = str(uuid.uuid4())

    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    db.apply_migrations(conn)
    conn.execute("TRUNCATE npc_state, chat_logs")

    # turn loop 을 직접 돌리지 않고, system+messages 를 구성해 실제 호출 — eval 단순화.
    from app.turn.loop import run_turn

    fallback_line = npc.diegetic_fallback.strip()
    verbatim_hits = 0
    fallback_hits = 0
    for line in PLAYER_LINES[:TURNS]:
        resp = run_turn(conn, sid, "surigong", line)  # 실제 client.call
        if resp.reply.strip() == fallback_line:
            fallback_hits += 1
        # 현재 band 의 sample_lines 로 검증.
        state_aw = conn.execute(
            "SELECT awareness FROM npc_state WHERE session_uuid=%s AND npc_id=%s", (sid, "surigong")
        ).fetchone()
        awareness = state_aw[0] if state_aw else 0
        band = resolve_band(awareness, rules.awareness_bands.bands)
        band_npc = next(b for b in npc.voice.awakening_bands if b.range == band.range)
        if any(sl.strip() and sl.strip() in resp.reply for sl in band_npc.sample_lines):
            verbatim_hits += 1

    conn.close()
    # 계약이 실제로 닫히는지 먼저 — 매 턴 fallback 이면 모델이 한 번도 답을 못 낸 것.
    assert fallback_hits <= MAX_FALLBACKS, (
        f"diegetic fallback {fallback_hits}/{TURNS}회 > 임계 {MAX_FALLBACKS} — "
        f"모델이 계약(turn JSON)을 못 채움 (thinking 모델 content 비움 등, ADR 0029)"
    )
    assert verbatim_hits <= VERBATIM_THRESHOLD, f"verbatim 복사 {verbatim_hits}회 > 임계 {VERBATIM_THRESHOLD}"
