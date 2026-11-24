"""CORS and integration readiness tests for frontend compatibility."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import (
    DEFAULT_CORS_ORIGINS,
    get_cors_origins,
)
from backend.app.main import app

client = TestClient(app)


def test_cors_default_origins_configuration():
    """Verify default CORS origins contain standard frontend development ports."""
    origins = get_cors_origins()
    assert "http://localhost:3000" in origins
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:3000" in origins
    assert "http://127.0.0.1:5173" in origins
    # Ensure wildcard is not present in default origins
    assert "*" not in origins


def test_cors_environment_variable_override(monkeypatch):
    """Verify ALLOWED_ORIGINS env var overrides default origins."""
    custom_origins = "https://polygen.example.com, http://localhost:4000"
    monkeypatch.setenv("ALLOWED_ORIGINS", custom_origins)

    parsed = get_cors_origins()
    assert parsed == ["https://polygen.example.com", "http://localhost:4000"]


def test_cors_allowed_origin_response_header():
    """Verify that requests from an allowed origin receive the Access-Control-Allow-Origin header."""
    for origin in ["http://localhost:3000", "http://127.0.0.1:5173"]:
        response = client.get("/health", headers={"Origin": origin})
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == origin
        assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_disallowed_origin_does_not_receive_header():
    """Verify that requests from unauthorized origins do not receive allow-origin header."""
    response = client.get("/health", headers={"Origin": "http://unauthorized-domain.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_options_request():
    """Verify that HTTP OPTIONS preflight requests succeed with appropriate headers."""
    response = client.options(
        "/api/v1/generations",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allow_methods
    assert "PATCH" in allow_methods
    assert "GET" in allow_methods


def test_cors_preflight_patch_status_endpoint():
    """Verify preflight requests for PATCH /api/v1/generations/{id}/status succeed."""
    dummy_uuid = "550e8400-e29b-41d4-a716-446655440000"
    response = client.options(
        f"/api/v1/generations/{dummy_uuid}/status",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
