"""API tests for the Generation Job Retrieval endpoint (GET /api/v1/generations/{job_id})."""

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


def test_get_job_successful_retrieval():
    """Verify that an existing job is successfully retrieved with status 200 and expected payload."""
    created = generation_job_service.create_job(
        prompt="A stylized wooden barrel",
        output_format=OutputFormat.GLB,
    )

    response = client.get(f"/api/v1/generations/{created.job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == str(created.job_id)
    assert data["prompt"] == "A stylized wooden barrel"
    assert data["output_format"] == "glb"
    assert data["status"] == "pending"
    assert data["error_message"] is None
    assert "created_at" in data
    assert "updated_at" in data


def test_get_job_pending_status():
    """Verify retrieval of a job in PENDING status."""
    created = generation_job_service.create_job(
        prompt="A low-poly medieval house",
        output_format=OutputFormat.OBJ,
    )

    response = client.get(f"/api/v1/generations/{created.job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["output_format"] == "obj"
    assert data["error_message"] is None


def test_get_job_processing_status():
    """Verify retrieval of a job in PROCESSING status."""
    created = generation_job_service.create_job(prompt="A sci-fi combat drone")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)

    response = client.get(f"/api/v1/generations/{created.job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["error_message"] is None


def test_get_job_completed_status():
    """Verify retrieval of a job in COMPLETED status."""
    created = generation_job_service.create_job(prompt="An ornate treasure chest")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.COMPLETED)

    response = client.get(f"/api/v1/generations/{created.job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["error_message"] is None


def test_get_job_failed_status():
    """Verify retrieval of a job in FAILED status includes the error message."""
    created = generation_job_service.create_job(prompt="A complex robotic dragon")
    generation_job_service.update_job_status(created.job_id, GenerationJobStatus.PROCESSING)
    generation_job_service.update_job_status(
        created.job_id,
        GenerationJobStatus.FAILED,
        error_message="GPU memory exceeded during mesh synthesis.",
    )

    response = client.get(f"/api/v1/generations/{created.job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_message"] == "GPU memory exceeded during mesh synthesis."


def test_get_job_unknown_id_returns_404():
    """Verify that requesting an unknown UUID returns 404 with a clear error detail."""
    unknown_id = uuid.uuid4()
    response = client.get(f"/api/v1/generations/{unknown_id}")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert str(unknown_id) in data["detail"]
    assert "not found" in data["detail"].lower()


def test_get_job_invalid_uuid_returns_422():
    """Verify that non-UUID path parameters fail path validation with 422 Unprocessable Entity."""
    invalid_ids = ["not-a-uuid", "12345", "uuid-with-invalid-chars-xyz!@#"]

    for invalid_id in invalid_ids:
        response = client.get(f"/api/v1/generations/{invalid_id}")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


def test_post_generations_remains_503_unaffected():
    """Verify that POST /api/v1/generations remains unaffected and continues to return 503."""
    response = client.post(
        "/api/v1/generations",
        json={"prompt": "A test low-poly asset", "output_format": "glb"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Text-to-3D generation engine is not yet integrated."
