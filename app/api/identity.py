"""B7 — 신원 해석 단일 지점: 쿠키 파싱 → UUID 검증 → 세션 존재 확인.

쿠키 인증 엔드포인트(/turn, /save-code)의 신원 판정은 전부 이 모듈을 통과한다.
이 모듈은 **절대 세션을 만들지 않는다** — 모르는 세션은 그대로 거부(None).
민팅은 bootstrap 소관 (B2: 유일한 세션 생성 문).
"""

import uuid

from fastapi import Request

from app.api.session_cookie import COOKIE_NAME
from app.store import repo


def parse_session_cookie(request: Request) -> str | None:
    """쿠키 파싱 + UUID 형식 검증 — 세션 존재 확인 없음 (bootstrap 이 공유).

    쿠키 없음 / UUID 형식 아님 → None.
    """
    raw = request.cookies.get(COOKIE_NAME)
    if raw is None:
        return None
    try:
        uuid.UUID(raw)
    except ValueError:
        return None
    return raw


def resolve_session(conn, request: Request) -> str | None:
    """신원 판정 전체: 쿠키 파싱 → UUID 검증 → 세션 존재 확인.

    통과 → session_uuid, 거부(쿠키 없음/형식 불량/모르는 세션) → None.
    세션 생성은 하지 않는다 — 거부의 처리(401 등)는 호출자 소관.
    """
    sid = parse_session_cookie(request)
    if sid is None:
        return None
    return sid if repo.session_exists(conn, sid) else None
