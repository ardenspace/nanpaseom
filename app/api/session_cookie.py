"""B6 — 세션 쿠키 단일 홈: 이름 / 수명 / 속성 / 로컬 dev env 플래그.

발급은 ``set_session_cookie`` 단일 경로 — 속성 4종
(``HttpOnly; Secure; SameSite=Lax; Max-Age=180일``) + ``Path=/`` 를 항상 싣는다.
Secure 는 env 플래그 ``NANPASEOM_INSECURE_COOKIE`` 가 켜진 경우에만 생략
(로컬 http 개발 예외 하나). 기본값(플래그 없음)은 항상 Secure.
"""

import os

from fastapi.responses import Response

COOKIE_NAME = "session_uuid"
# 브라우저 완전 종료 후에도 세션 유지 — 장수 쿠키 (session cookie 금지).
SESSION_COOKIE_MAX_AGE = 180 * 24 * 3600  # 15552000 = 180일 (B6 계약 리터럴)
# request 시점 env resolve (기존 NANPASEOM_STATIC_DIR 패턴) — 프로세스 재기동 불필요.
INSECURE_COOKIE_ENV = "NANPASEOM_INSECURE_COOKIE"


def set_session_cookie(response: Response, session_uuid: str) -> None:
    """세션 쿠키 발급 단일 경로 — B6 속성 4종 + Path=/."""
    response.set_cookie(
        COOKIE_NAME,
        session_uuid,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        secure=not os.environ.get(INSECURE_COOKIE_ENV),
        samesite="lax",
        path="/",
    )
