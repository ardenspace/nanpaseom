"""2-strike 성희롱/혐오 상태머신 (ADR 0009 Layer 2.5, ADR 0031).

register: verdict → 세션 warning_count 전이 + safety_events + 프레임 깨는 메시지 렌더.
Strike 1 = warning (LLM·awareness·chat_logs 불변, 호출 측이 보장). Strike 2 = 영구 차단.
"""

from typing import Literal, Optional

from pydantic import BaseModel

from app.safety.moderation import SafetyVerdict
from app.safety.rules import load_safety_rules
from app.store import repo


class StrikeResult(BaseModel):
    kind: Literal["warning", "ban"]
    message: str
    matched_term: Optional[str] = None


def register(conn, session_uuid: str, verdict: SafetyVerdict) -> StrikeResult:
    """성희롱/혐오 감지를 strike 로 등록. 호출 전 verdict.category != 'clean' 가정.

    세션 행은 만들지 않는다 (Req 8: 세션 생성 문은 POST /session/bootstrap 유일) —
    호출자는 존재 확인된 session_uuid 만 넘길 것 (엔드포인트 신원 게이트가 보장).
    """
    rules = load_safety_rules()
    term = verdict.matched_term or ""

    # NOTE: read-modify-write 가 autocommit 하 비원자적 — 동일 session_uuid 동시 요청 시
    # warning_count 경쟁 가능 (2-strike 가 약화). ban 이 세션 스코프 soft-ban 이라 슬라이스 범위엔
    # 수용. ban 하드닝(행 잠금/원자적 UPDATE) 은 v1.1 (IP 차단과 함께).
    repo.append_safety_event(conn, session_uuid, verdict.category, term)
    sess = repo.load_session(conn, session_uuid)

    if sess.warning_count == 0:
        repo.set_warning(conn, session_uuid, 1, term)
        message = rules.messages.warning.format(term=term)
        return StrikeResult(kind="warning", message=message, matched_term=term)

    # 이미 경고 1회 → 영구 차단.
    message = rules.messages.ban.format(term1=sess.first_strike_term or "", term2=term)
    repo.ban_session(conn, session_uuid, message)
    return StrikeResult(kind="ban", message=message)
