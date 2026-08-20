"""B3 발급 게이트 + B5 /assets 화이트리스트 + Req 12 자동 문서 비활성 (Phase 2 boundary pin).

계약 요약 (spec.md 동결 원문 기준):

- B3 ``POST /save-code`` 발급 게이트: 발급은 **아는 세션에만**.
  - 쿠키 없음 / 형식 불량 / 모르는 세션 → ``401 {status:"error", message}`` —
    /turn 401 과 같은 결 (문구 서식지는 rules YAML — 내용은 단언하지 않음).
    세션 생성 없음 + 쿠키 발급 없음 (구 "빈 세션 민팅 후 발급" 폐지 — 미생성은
    Phase 1 구현 완료, **400 → 401 전환이 이번 변경분**).
  - 아는 비밴 세션 → 발급. **0턴 세션도 OK**. 재요청은 기존 코드 반환 (idempotent).
  - 밴 세션 → 200 ``{status:"banned"}`` — test_save_code.py 가 이미 pin (중복 박제 금지).
  - B4 redeem 의 404/503/banned/rebind 속성 칸도 기존 테스트가 전부 pin — 이 파일엔 없음.

- B5 ``GET /assets/*`` 확장자 화이트리스트: 허용 = 이미지(png jpg jpeg webp gif
  svg ico) + 폰트(woff woff2) + 빌드 산출물(js css map). 그 외 확장자·무확장자 →
  404 — **문서류(md/txt)가 새지 않는 것이 핵심** (README.md 케이스).
  판정은 resolve 된 실파일 기준 + 대소문자 무시. 실경로가 assets 루트 밖이면
  허용 확장자여도 404 (기존 탈출 방어 유지 — 인코딩 변형은 test_static.py 가 pin).

- Req 12: FastAPI 자동 문서 ``/docs``, ``/redoc``, ``/openapi.json`` → 404 (비활성화).
"""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.config import DATABASE_URL
from app.save_code import SAVE_CODE_RE
from tests.api.conftest import known_session, session_cookie_headers

ISSUE_URL = "/save-code"
COOKIE_NAME = "session_uuid"
STATIC_DIR_ENV = "NANPASEOM_STATIC_DIR"


# ------------------------------------------------------------------- helpers

def _db():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def _count_sessions() -> int:
    with _db() as c:
        return c.execute("SELECT count(*) FROM sessions").fetchone()[0]


def _session_row_exists(sid: str) -> bool:
    with _db() as c:
        row = c.execute(
            "SELECT 1 FROM sessions WHERE session_uuid = %s", (sid,)
        ).fetchone()
    return row is not None


def _db_save_code(sid: str) -> str | None:
    with _db() as c:
        row = c.execute(
            "SELECT save_code FROM sessions WHERE session_uuid = %s", (sid,)
        ).fetchone()
    return row[0] if row else None


def _assert_issue_401(response) -> None:
    """B3 거부 응답 계약 — /turn 401 과 같은 결 + 부작용 없음(쿠키 미발급)."""
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert body["message"]  # 문구 서식지는 rules YAML — 내용은 단언하지 않음
    assert "save_code" not in body
    assert session_cookie_headers(response) == []  # 401 은 쿠키를 심지 않는다


# ------------------------------------------- B3: 발급은 아는 세션에만 (401 게이트)

def test_issue_without_cookie_is_401_and_creates_no_session(client):
    before = _count_sessions()
    r = client.post(ISSUE_URL)
    _assert_issue_401(r)
    assert _count_sessions() == before  # 세션 생성 없음


def test_issue_with_malformed_cookie_is_401_and_creates_no_session(client):
    before = _count_sessions()
    client.cookies.set(COOKIE_NAME, "not-a-uuid")
    _assert_issue_401(client.post(ISSUE_URL))
    assert _count_sessions() == before


def test_issue_with_unknown_session_cookie_is_401_and_no_session_row(client):
    ghost = str(uuid.uuid4())  # UUID 형식은 유효, 서버가 모르는 세션
    client.cookies.set(COOKIE_NAME, ghost)
    _assert_issue_401(client.post(ISSUE_URL))
    assert not _session_row_exists(ghost)  # 빈 세션 민팅 후 발급 — 폐지


def test_issue_for_known_zero_turn_session_returns_code(client):
    """0턴 세션도 발급 OK — 발급 조건은 "아는 세션"이지 "진행된 세션"이 아니다."""
    sid = known_session(turns=0)
    client.cookies.set(COOKIE_NAME, sid)

    r = client.post(ISSUE_URL)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert SAVE_CODE_RE.fullmatch(body["save_code"])
    assert _db_save_code(sid) == body["save_code"]


def test_reissue_returns_the_same_existing_code(client):
    """재요청은 기존 코드 반환 (idempotent) — 이미 적어 둔 코드가 계속 유효."""
    sid = known_session(turns=1)
    client.cookies.set(COOKIE_NAME, sid)

    code1 = client.post(ISSUE_URL).json()["save_code"]
    code2 = client.post(ISSUE_URL).json()["save_code"]
    assert code2 == code1
    assert _db_save_code(sid) == code1


# ------------------------------------------------ B5: /assets 확장자 화이트리스트

BUNDLE_JS = 'console.log("nanpaseom-bundle-fixture");\n'
DOC_LEAK = "nanpaseom-doc-must-not-leak"
OUTSIDE_JS = 'console.log("nanpaseom-outside-assets");\n'

# 허용 목록 대표 표본 — 이미지 / 폰트 / 빌드 산출물 각 계열.
ALLOWED_FIXTURES = {
    "x.js": BUNDLE_JS,
    "style.css": "body{margin:0}\n",
    "x.js.map": '{"version":3}\n',
    "pic.png": "png-fixture-bytes",
    "font.woff2": "woff2-fixture-bytes",
    "icon.svg": "<svg xmlns='http://www.w3.org/2000/svg'/>\n",
}

# 비허용 — 문서류 + 무확장자. 실파일이 존재해도 404 여야 한다.
DENIED_FIXTURES = {
    "README.md": DOC_LEAK,      # 계약의 핵심 케이스
    "notes.txt": DOC_LEAK,
    "LICENSE": DOC_LEAK,        # 무확장자
    "config.yaml": DOC_LEAK,
}


@pytest.fixture()
def static_client(monkeypatch, tmp_path):
    """더미 빌드 산출물 디렉토리를 가리키는 TestClient. DB/LLM 불필요.

    구조: index.html + assets/(허용·비허용 파일들, 대문자 확장자, .md 로의 심링크)
    + (assets 밖) evil.js — 허용 확장자여도 루트 밖이면 404 검증용.
    """
    (tmp_path / "index.html").write_text(
        "<!doctype html><title>nanpaseom-static-fixture</title>", encoding="utf-8"
    )
    assets = tmp_path / "assets"
    assets.mkdir()
    for name, content in (ALLOWED_FIXTURES | DENIED_FIXTURES).items():
        (assets / name).write_text(content, encoding="utf-8")
    (assets / "logo.PNG").write_text("png-uppercase-ext", encoding="utf-8")
    # 허용 확장자 이름의 심링크 → 비허용 실파일: 판정은 resolve 된 실파일 기준.
    (assets / "linked.js").symlink_to(assets / "README.md")
    # assets 루트 *밖* 허용 확장자 파일 — 탈출은 확장자와 무관하게 404.
    (tmp_path / "evil.js").write_text(OUTSIDE_JS, encoding="utf-8")
    monkeypatch.setenv(STATIC_DIR_ENV, str(tmp_path))
    from app.api.main import app
    return TestClient(app)


@pytest.mark.parametrize("name", sorted(ALLOWED_FIXTURES))
def test_assets_whitelisted_extensions_are_served(static_client, name):
    r = static_client.get(f"/assets/{name}")
    assert r.status_code == 200
    assert r.text == ALLOWED_FIXTURES[name]


@pytest.mark.parametrize("name", sorted(DENIED_FIXTURES))
def test_assets_non_whitelisted_extension_is_404_even_for_real_file(static_client, name):
    r = static_client.get(f"/assets/{name}")
    assert r.status_code == 404
    assert DOC_LEAK not in r.text


def test_assets_extension_check_is_case_insensitive(static_client):
    r = static_client.get("/assets/logo.PNG")
    assert r.status_code == 200
    assert r.text == "png-uppercase-ext"


def test_assets_extension_judged_on_resolved_real_file(static_client):
    """.js 이름의 심링크가 .md 를 가리키면 404 — 판정은 resolve 된 실파일 기준."""
    r = static_client.get("/assets/linked.js")
    assert r.status_code == 404
    assert DOC_LEAK not in r.text


def test_assets_traversal_to_allowed_extension_outside_root_is_404(static_client):
    """허용 확장자(.js)여도 실경로가 assets 루트 밖이면 404 — 탈출 방어는 별개 층."""
    r = static_client.get("/assets/../evil.js")
    assert r.status_code == 404
    assert "nanpaseom-outside-assets" not in r.text


# ------------------------------------------------ Req 12: 자동 문서 엔드포인트 봉인

@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_fastapi_auto_docs_endpoints_are_disabled(path):
    from app.api.main import app

    r = TestClient(app).get(path)
    assert r.status_code == 404
