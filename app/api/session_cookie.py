"""B6 — 세션 쿠키 단일 홈: 이름 / 수명 / 속성 / 로컬 dev env 플래그.

발급은 ``set_session_cookie`` 단일 경로 — 속성 4종
(``HttpOnly; Secure; SameSite=Lax; Max-Age=180일``) + ``Path=/`` 를 항상 싣는다.
Secure 는 env 플래그 ``NANPASEOM_INSECURE_COOKIE`` 가 켜진 경우에만 생략
(로컬 http 개발 예외 하나). 기본값(플래그 없음)은 항상 Secure.

판정은 허용목록 — ``"1"`` / ``"true"`` (대소문자 무시)만 켜짐이고, 그 외
모든 값(빈값 / ``"0"`` / ``"false"`` / 오타 / 공백이 붙은 값)은 꺼짐 =
Secure 유지. 배포 env 에서 알 수 없는 값이 들어오면 안전한 쪽으로 닫힌다.
"""

import os

from fastapi.responses import Response

COOKIE_NAME = "session_uuid"
# 브라우저 완전 종료 후에도 세션 유지 — 장수 쿠키 (session cookie 금지).
SESSION_COOKIE_MAX_AGE = 180 * 24 * 3600  # 15552000 = 180일 (B6 계약 리터럴)
# request 시점 env resolve (기존 NANPASEOM_STATIC_DIR 패턴) — 프로세스 재기동 불필요.
INSECURE_COOKIE_ENV = "NANPASEOM_INSECURE_COOKIE"
# 켜짐으로 인정하는 값 전부 (대소문자만 정규화) — 목록 밖은 예외 없이 꺼짐.
INSECURE_COOKIE_ON_VALUES = frozenset({"1", "true"})


def _insecure_cookie_enabled() -> bool:
    """env 플래그 허용목록 판정 — 목록 밖 값은 전부 꺼진 것(= Secure 유지).

    공백 trim 도 하지 않는다: `" 1"` 같은 값은 배포 env 오타에 가깝고,
    Secure 를 벗기는 판정은 모호할 때 닫히는 편이 안전하다.
    """
    value = os.environ.get(INSECURE_COOKIE_ENV, "")
    return value.lower() in INSECURE_COOKIE_ON_VALUES


def set_session_cookie(response: Response, session_uuid: str) -> None:
    """세션 쿠키 발급 단일 경로 — B6 속성 4종 + Path=/."""
    response.set_cookie(
        COOKIE_NAME,
        session_uuid,
        max_age=SESSION_COOKIE_MAX_AGE,
        httponly=True,
        secure=not _insecure_cookie_enabled(),
        samesite="lax",
        path="/",
    )
