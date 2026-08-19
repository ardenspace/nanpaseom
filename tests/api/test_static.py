"""B4 정적 서빙 계약 (Phase 1 boundary pin).

- 프로덕션 모드: FastAPI 가 Vite 빌드 산출물을 서빙 — ``GET /`` → 200 + text/html,
  ``GET /assets/{path}`` → 번들 파일 (js/css/이미지).
- 빌드 디렉토리는 env ``NANPASEOM_STATIC_DIR`` 로 지정 (기본 ``frontend/dist``).
  **request 시점에 resolve** 해야 한다 — 빌드 산출물이 없는 테스트 환경에서도
  setenv + 더미 index.html 디렉토리로 검증 가능해야 함 (이 테스트가 그 방식).
- ``/assets`` 는 경로 탈출(``../``, URL-인코딩 변형 포함) 을 404 로 거부한다.
- dev 프록시/포트는 테스트 대상 아님.
"""

import pytest
from fastapi.testclient import TestClient

STATIC_DIR_ENV = "NANPASEOM_STATIC_DIR"

BUNDLE_JS = 'console.log("nanpaseom-bundle-fixture");\n'
SECRET = "nanpaseom-secret-outside-assets"


@pytest.fixture()
def static_client(monkeypatch, tmp_path):
    """더미 빌드 산출물 디렉토리를 가리키는 TestClient. DB/LLM 불필요.

    구조: index.html + assets/x.js + (assets 밖) secret.txt — 탈출 검증용.
    """
    (tmp_path / "index.html").write_text(
        "<!doctype html><title>nanpaseom-static-fixture</title>", encoding="utf-8"
    )
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "x.js").write_text(BUNDLE_JS, encoding="utf-8")
    # assets 디렉토리 *밖* 파일 — /assets/../secret.txt 로 절대 못 읽어야 함.
    (tmp_path / "secret.txt").write_text(SECRET, encoding="utf-8")
    monkeypatch.setenv(STATIC_DIR_ENV, str(tmp_path))
    from app.api.main import app
    return TestClient(app)


def test_root_serves_index_html(static_client):
    r = static_client.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    # 서빙된 내용이 지정 디렉토리의 index.html 인지 (fixture 가 쓴 더미 내용).
    assert "nanpaseom-static-fixture" in r.text


def test_assets_serves_bundle_file(static_client):
    r = static_client.get("/assets/x.js")
    assert r.status_code == 200
    # js 번들은 스크립트 content-type (플랫폼 따라 text/ 또는 application/).
    assert "javascript" in r.headers["content-type"]
    assert r.text == BUNDLE_JS


def test_assets_missing_file_is_404(static_client):
    r = static_client.get("/assets/nope.js")
    assert r.status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        # 평문 ../ — 클라이언트/프록시가 정규화해도 결과는 404 여야 함.
        "/assets/../secret.txt",
        # URL-인코딩 변형 — 라우트 param 으로 디코딩돼 도달하는 실제 공격 경로.
        "/assets/%2e%2e/secret.txt",
        "/assets/..%2fsecret.txt",
        # 이중 탈출 — 정적 디렉토리 자체 밖.
        "/assets/%2e%2e/%2e%2e/secret.txt",
    ],
)
def test_assets_traversal_is_rejected(static_client, path):
    r = static_client.get(path)
    assert r.status_code == 404
    assert SECRET not in r.text
