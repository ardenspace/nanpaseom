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


class UnknownSessionError(RuntimeError):
    """B7 — register 의 전제(존재 확인된 세션) 위반. 내부 계약 위반 신호.

    플레이어에게 보이는 오류가 아니다: 유일한 호출부(/turn 안전 트랙)는 신원
    게이트(resolve_session) 뒤에 있어 미지의 세션은 401 에서 끝난다. 이 예외가
    실제로 오르면 그건 호출부가 깨졌다는 버그 신호 (tests/api/test_identity_contracts.py
    B7 섹션이 도달 불가를 박제).

    AssertionError 를 상속하지 않는다 — assert 계열은 ``python -O`` 에서 지워져
    하드닝이 조용한 무동작으로 되돌아간다.
    """


# 개발자용 진단 문구 — 플레이어 발신 문구가 아니므로 rules/safety.yaml 이 아니라 여기.
_UNKNOWN_SESSION_DETAIL = (
    "strike.register requires a session row that already exists "
    "(minting belongs to POST /session/bootstrap); unknown session_uuid={uuid}"
)


def register(conn, session_uuid: str, verdict: SafetyVerdict) -> StrikeResult:
    """성희롱/혐오 감지를 strike 로 등록. 호출 전 verdict.category != 'clean' 가정.

    세션 행은 만들지 않는다 (Req 8: 세션 생성 문은 POST /session/bootstrap 유일) —
    호출자는 존재 확인된 session_uuid 만 넘길 것 (엔드포인트 신원 게이트가 보장).
    전제가 깨지면 조용히 넘어가지 않고 UnknownSessionError 로 즉시 실패한다 (B7):
    부작용(safety_events 기록) 전에 검사하므로 실패한 호출은 흔적을 남기지 않는다.
    """
    if not repo.session_exists(conn, session_uuid):
        raise UnknownSessionError(_UNKNOWN_SESSION_DETAIL.format(uuid=session_uuid))

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
