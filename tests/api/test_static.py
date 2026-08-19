"""B4 정적 서빙 계약 (Phase 1 boundary pin).

- 프로덕션 모드: FastAPI 가 Vite 빌드 산출물을 서빙 — ``GET /`` → 200 + text/html.
- 빌드 디렉토리는 env ``NANPASEOM_STATIC_DIR`` 로 지정 (기본 ``frontend/dist``).
  **request 시점에 resolve** 해야 한다 — 빌드 산출물이 없는 테스트 환경에서도
  setenv + 더미 index.html 디렉토리로 검증 가능해야 함 (이 테스트가 그 방식).
- dev 프록시/포트는 테스트 대상 아님.
"""

import pytest
from fastapi.testclient import TestClient

STATIC_DIR_ENV = "NANPASEOM_STATIC_DIR"


@pytest.fixture()
def static_client(monkeypatch, tmp_path):
    """더미 빌드 산출물 디렉토리를 가리키는 TestClient. DB/LLM 불필요."""
    (tmp_path / "index.html").write_text(
        "<!doctype html><title>nanpaseom-static-fixture</title>", encoding="utf-8"
    )
    monkeypatch.setenv(STATIC_DIR_ENV, str(tmp_path))
    from app.api.main import app
    return TestClient(app)


def test_root_serves_index_html(static_client):
    r = static_client.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    # 서빙된 내용이 지정 디렉토리의 index.html 인지 (fixture 가 쓴 더미 내용).
    assert "nanpaseom-static-fixture" in r.text
