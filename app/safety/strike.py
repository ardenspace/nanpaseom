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
    """성희롱/혐오 감지를 strike 로 등록. 호출 전 verdict.category != 'clean' 가정."""
    rules = load_safety_rules()
    term = verdict.matched_term or ""

    repo.ensure_session(conn, session_uuid)
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
