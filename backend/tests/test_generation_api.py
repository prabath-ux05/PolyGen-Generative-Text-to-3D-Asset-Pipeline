"""Tests for the Text-to-3D Generation API endpoints."""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app

client = TestClient(app)

ENDPOINT_URL = "/api/v1/generations"


def test_valid_request_reaches_endpoint_and_returns_503():
    """Verify that a valid request reaches the endpoint and returns 503 Service Unavailable."""
    payload = {"prompt": "A low-poly medieval wooden cart"}
    response = client.post(ENDPOINT_URL, json=payload)

    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Text-to-3D generation engine is not yet integrated."


def test_valid_obj_format_accepted_by_validation():
    """Verify that OBJ output format passes validation and reaches the endpoint."""
    payload = {
        "prompt": "A futuristic sci-fi helmet",
        "output_format": "obj",
    }
    response = client.post(ENDPOINT_URL, json=payload)

    assert response.status_code == 503
    data = response.json()
    assert data["detail"] == "Text-to-3D generation engine is not yet integrated."


def test_valid_glb_format_accepted_by_validation():
    """Verify that GLB output format passes validation and reaches the endpoint."""
    payload = {
        "prompt": "A crystal healing potion bottle",
        "output_format": "glb",
    }
    response = client.post(ENDPOINT_URL, json=payload)

    assert response.status_code == 503
    data = response.json()
    assert data["detail"] == "Text-to-3D generation engine is not yet integrated."


def test_missing_prompt_rejected():
    """Verify that omitting the required prompt results in 422 Unprocessable Entity."""
    payload = {"output_format": "glb"}
    response = client.post(ENDPOINT_URL, json=payload)

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any(err["loc"][-1] == "prompt" for err in data["detail"])


def test_empty_prompt_rejected():
    """Verify that an empty string prompt is rejected with 422."""
    payload = {"prompt": ""}
    response = client.post(ENDPOINT_URL, json=payload)

    assert response.status_code == 422
    data = response.json()
    assert any("prompt" in err["loc"] for err in data["detail"])


def test_whitespace_only_prompt_rejected():
    """Verify that a whitespace-only prompt is rejected with 422."""
    for ws in ["   ", "\t", "\n\n   \t"]:
        payload = {"prompt": ws}
        response = client.post(ENDPOINT_URL, json=payload)

        assert response.status_code == 422
        data = response.json()
        assert any("prompt" in err["loc"] for err in data["detail"])


def test_unsupported_output_format_rejected():
    """Verify that unsupported 3D asset formats are rejected with 422."""
    unsupported_formats = ["stl", "fbx", "blend", "ply", "invalid_fmt"]
    for fmt in unsupported_formats:
        payload = {"prompt": "A test asset", "output_format": fmt}
        response = client.post(ENDPOINT_URL, json=payload)

        assert response.status_code == 422
        data = response.json()
        assert any("output_format" in err["loc"] for err in data["detail"])


def test_endpoint_with_trailing_slash():
    """Verify that calling the endpoint with a trailing slash also reaches the endpoint."""
    payload = {"prompt": "A dragon statue"}
    response = client.post(f"{ENDPOINT_URL}/", json=payload)

    assert response.status_code == 503
    assert response.json()["detail"] == "Text-to-3D generation engine is not yet integrated."


def test_engine_unavailable_error_structure():
    """Verify that 503 error payload conforms to the documented error contract."""
    payload = {"prompt": "An ornate treasure chest", "output_format": "glb"}
    response = client.post(ENDPOINT_URL, json=payload)

    assert response.status_code == 503
    data = response.json()
    assert isinstance(data, dict)
    assert "detail" in data
    assert "not yet integrated" in data["detail"].lower()
    # Ensure it doesn't falsely claim to be queued or started
    assert "queued" not in data["detail"].lower()
    assert "started" not in data["detail"].lower()
