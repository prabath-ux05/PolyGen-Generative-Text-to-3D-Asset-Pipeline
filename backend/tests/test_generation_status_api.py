"""API tests for the Generation Job Status Update endpoint (PATCH /api/v1/generations/{job_id}/status)."""

import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.main import app
from backend.app.schemas.generation import OutputFormat
from backend.app.schemas.generation_job import GenerationJobStatus
from backend.app.services.generation_job_service import generation_job_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_job_store():
    """Ensure in-memory job store is isolated and clean for each test."""
    generation_job_service.clear()
    yield
    generation_job_service.clear()


# --- Valid Lifecycle Transitions ---


def test_transition_pending_to_processing():
    """Verify valid transition from PENDING to PROCESSING returns 200 and updated status."""
    created = generation_job_service.create_job(prompt="A futuristic flying car")
    original_updated_at = created.updated_at

    response = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "processing"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == str(created.job_id)
    assert data["status"] == "processing"
    assert data["error_message"] is None
    assert data["prompt"] == "A futuristic flying car"
    assert data["output_format"] == "glb"
    assert data["updated_at"] >= str(original_updated_at)


def test_transition_processing_to_completed():
    """Verify valid transition from PROCESSING to COMPLETED returns 200."""
    created = generation_job_service.create_job(prompt="A medieval treasure chest")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)

    response = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "completed"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["error_message"] is None


def test_transition_processing_to_failed_with_error_message():
    """Verify valid transition from PROCESSING to FAILED stores the error message."""
    created = generation_job_service.create_job(prompt="A high-poly dragon statue")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)

    error_detail = "CUDA out of memory during mesh decimation."
    response = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "failed", "error_message": error_detail},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_message"] == error_detail


# --- Invalid Lifecycle Transitions (HTTP 409 Conflict) ---


def test_invalid_transition_pending_to_completed():
    """Verify direct transition from PENDING to COMPLETED is rejected with 409 Conflict."""
    created = generation_job_service.create_job(prompt="A stone archway")

    response = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "completed"},
    )

    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert "Cannot transition" in data["detail"]


def test_invalid_transition_pending_to_failed():
    """Verify direct transition from PENDING to FAILED is rejected with 409 Conflict."""
    created = generation_job_service.create_job(prompt="A wooden barrel")

    response = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "failed", "error_message": "Immediate failure"},
    )

    assert response.status_code == 409
    assert "Cannot transition" in response.json()["detail"]


def test_invalid_transition_processing_to_pending():
    """Verify backward transition from PROCESSING to PENDING is rejected with 409 Conflict."""
    created = generation_job_service.create_job(prompt="A crystal potion")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)

    response = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "pending"},
    )

    assert response.status_code == 409
    assert "Cannot transition" in response.json()["detail"]


def test_invalid_transition_from_terminal_completed():
    """Verify COMPLETED is terminal and rejects any further transitions with 409 Conflict."""
    created = generation_job_service.create_job(prompt="A gold coin")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.COMPLETED)

    for target in ["pending", "processing", "completed", "failed"]:
        response = client.patch(
            f"/api/v1/generations/{created.job_id}/status",
            json={"status": target},
        )
        assert response.status_code == 409
        assert "Cannot transition" in response.json()["detail"]


def test_invalid_transition_from_terminal_failed():
    """Verify FAILED is terminal and rejects any further transitions with 409 Conflict."""
    created = generation_job_service.create_job(prompt="A rusty sword")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.FAILED, error_message="Failed")

    for target in ["pending", "processing", "completed", "failed"]:
        response = client.patch(
            f"/api/v1/generations/{created.job_id}/status",
            json={"status": target},
        )
        assert response.status_code == 409
        assert "Cannot transition" in response.json()["detail"]


def test_same_state_transition_rejected():
    """Verify transitioning to the same current state is rejected with 409 Conflict."""
    created = generation_job_service.create_job(prompt="A magic staff")

    response = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "pending"},
    )

    assert response.status_code == 409
    assert "Cannot transition" in response.json()["detail"]


# --- Error Handling: 404 & 422 ---


def test_unknown_job_id_returns_404():
    """Verify unknown job ID returns 404 Not Found."""
    unknown_id = uuid.uuid4()
    response = client.patch(
        f"/api/v1/generations/{unknown_id}/status",
        json={"status": "processing"},
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert str(unknown_id) in data["detail"]
    assert "not found" in data["detail"].lower()


def test_invalid_uuid_returns_422():
    """Verify invalid UUID path parameter returns 422 Unprocessable Content."""
    for bad_id in ["not-a-uuid", "12345", "invalid-uuid-syntax"]:
        response = client.patch(
            f"/api/v1/generations/{bad_id}/status",
            json={"status": "processing"},
        )
        assert response.status_code == 422
        assert "detail" in response.json()


def test_invalid_status_value_returns_422():
    """Verify invalid status string in payload returns 422 Unprocessable Content."""
    created = generation_job_service.create_job(prompt="A test asset")

    for bad_status in ["queued", "running", "cancelled", "unknown", ""]:
        response = client.patch(
            f"/api/v1/generations/{created.job_id}/status",
            json={"status": bad_status},
        )
        assert response.status_code == 422
        assert "detail" in response.json()


# --- Endpoint Consistency & Preservation ---


def test_get_retrieves_updated_status():
    """Verify that GET /api/v1/generations/{job_id} reflects changes made by PATCH."""
    created = generation_job_service.create_job(prompt="A glowing rune stone")

    # PATCH to processing
    patch_resp = client.patch(
        f"/api/v1/generations/{created.job_id}/status",
        json={"status": "processing"},
    )
    assert patch_resp.status_code == 200

    # GET verification
    get_resp = client.get(f"/api/v1/generations/{created.job_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "processing"


def test_post_generations_still_returns_503():
    """Verify that POST /api/v1/generations remains untouched and returns 503."""
    response = client.post(
        "/api/v1/generations",
        json={"prompt": "A test asset", "output_format": "glb"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Text-to-3D generation engine is not yet integrated."
