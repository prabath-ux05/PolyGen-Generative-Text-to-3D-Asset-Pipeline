"""API contract, schema conformance, and error handling tests for PolyGen generation endpoints."""

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
from backend.app.schemas.generation import (
    ErrorResponse,
    MAX_PROMPT_LENGTH,
    OutputFormat,
    ServiceUnavailableResponse,
)
from backend.app.schemas.generation_job import (
    GenerationJobResponse,
    GenerationJobStatus,
)
from backend.app.services.generation_job_service import generation_job_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_job_store():
    """Ensure in-memory job store is isolated and reset for each test."""
    generation_job_service.clear()
    yield
    generation_job_service.clear()


# ==============================================================================
# 1. OpenAPI Specification & Contract Validation
# ==============================================================================


def test_openapi_schema_generation_and_routes():
    """Verify that OpenAPI documentation compiles correctly and lists all endpoints."""
    schema = app.openapi()
    assert schema["info"]["title"] == "PolyGen API"

    paths = schema["paths"]
    assert "/" in paths
    assert "/health" in paths
    assert "/api/v1/generations" in paths
    assert "/api/v1/generations/{job_id}" in paths
    assert "/api/v1/generations/{job_id}/status" in paths


# ==============================================================================
# 2. POST /api/v1/generations — Contract & Error Handling
# ==============================================================================


def test_post_generations_missing_body():
    """Verify missing request body returns HTTP 422 with structured validation error."""
    response = client.post("/api/v1/generations")
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)


def test_post_generations_missing_prompt_field():
    """Verify payload missing required 'prompt' field returns 422."""
    response = client.post("/api/v1/generations", json={"output_format": "glb"})
    assert response.status_code == 422
    data = response.json()
    assert any("prompt" in err["loc"] for err in data["detail"])


def test_post_generations_non_string_prompt():
    """Verify non-string prompt types (integer, dict, list, boolean, null) return 422."""
    for invalid_prompt in [12345, {"text": "sword"}, ["sword"], True, None]:
        response = client.post("/api/v1/generations", json={"prompt": invalid_prompt})
        assert response.status_code == 422
        assert any("prompt" in err["loc"] for err in response.json()["detail"])


def test_post_generations_prompt_boundary_lengths():
    """Verify prompt length contract boundaries (min 1, max 1000)."""
    # Empty string
    assert client.post("/api/v1/generations", json={"prompt": ""}).status_code == 422

    # Whitespace only
    assert client.post("/api/v1/generations", json={"prompt": "   \n\t"}).status_code == 422

    # Exactly max length (1000 chars) -> passes validation, returns 503
    max_prompt = "a" * MAX_PROMPT_LENGTH
    resp_max = client.post("/api/v1/generations", json={"prompt": max_prompt})
    assert resp_max.status_code == 503

    # Exceeding max length (1001 chars) -> rejected with 422
    over_max = "a" * (MAX_PROMPT_LENGTH + 1)
    resp_over = client.post("/api/v1/generations", json={"prompt": over_max})
    assert resp_over.status_code == 422


def test_post_generations_unsupported_formats():
    """Verify unsupported 3D output formats return 422."""
    for unsupported in ["stl", "fbx", "step", "ply", "blend", 123, None]:
        response = client.post(
            "/api/v1/generations",
            json={"prompt": "A test asset", "output_format": unsupported},
        )
        assert response.status_code == 422
        assert any("output_format" in err["loc"] for err in response.json()["detail"])


def test_post_generations_503_response_matches_schema():
    """Verify valid requests return 503 whose payload strictly matches ServiceUnavailableResponse."""
    response = client.post(
        "/api/v1/generations",
        json={"prompt": "A stylized low-poly fox", "output_format": "glb"},
    )
    assert response.status_code == 503
    data = response.json()

    # Validate against Pydantic schema
    validated = ServiceUnavailableResponse(**data)
    assert validated.detail == "Text-to-3D generation engine is not yet integrated."


# ==============================================================================
# 3. GET /api/v1/generations/{job_id} — Contract & Error Handling
# ==============================================================================


def test_get_job_invalid_uuid_contract():
    """Verify malformed and non-UUID values return HTTP 422 with validation errors."""
    for invalid_uuid in ["not-a-uuid", "12345", "xyz-abc", "11111111-2222-3333-4444-55555555555g"]:
        response = client.get(f"/api/v1/generations/{invalid_uuid}")
        assert response.status_code == 422
        assert "detail" in response.json()


def test_get_job_unknown_uuid_contract():
    """Verify non-existent UUID returns HTTP 404 matching ErrorResponse schema."""
    random_id = uuid.uuid4()
    response = client.get(f"/api/v1/generations/{random_id}")
    assert response.status_code == 404
    data = response.json()

    # Validate against ErrorResponse schema
    validated = ErrorResponse(**data)
    assert str(random_id) in validated.detail
    assert "not found" in validated.detail.lower()


def test_get_job_success_contract_across_all_statuses():
    """Verify that successful responses across all lifecycle statuses strictly match GenerationJobResponse."""
    # 1. PENDING
    job = generation_job_service.create_job(prompt="A castle tower", output_format=OutputFormat.GLB)
    resp = client.get(f"/api/v1/generations/{job.job_id}")
    assert resp.status_code == 200
    validated = GenerationJobResponse(**resp.json())
    assert validated.status == GenerationJobStatus.PENDING
    assert validated.error_message is None

    # 2. PROCESSING
    generation_job_service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)
    resp = client.get(f"/api/v1/generations/{job.job_id}")
    assert resp.status_code == 200
    validated = GenerationJobResponse(**resp.json())
    assert validated.status == GenerationJobStatus.PROCESSING
    assert validated.error_message is None

    # 3. COMPLETED
    generation_job_service.update_job_status(job.job_id, GenerationJobStatus.COMPLETED)
    resp = client.get(f"/api/v1/generations/{job.job_id}")
    assert resp.status_code == 200
    validated = GenerationJobResponse(**resp.json())
    assert validated.status == GenerationJobStatus.COMPLETED
    assert validated.error_message is None

    # 4. FAILED (new job)
    job2 = generation_job_service.create_job(prompt="A failed model")
    generation_job_service.update_job_status(job2.job_id, GenerationJobStatus.PROCESSING)
    generation_job_service.update_job_status(job2.job_id, GenerationJobStatus.FAILED, error_message="Synthesis failure")
    resp2 = client.get(f"/api/v1/generations/{job2.job_id}")
    assert resp2.status_code == 200
    validated2 = GenerationJobResponse(**resp2.json())
    assert validated2.status == GenerationJobStatus.FAILED
    assert validated2.error_message == "Synthesis failure"


# ==============================================================================
# 4. PATCH /api/v1/generations/{job_id}/status — Contract & Error Handling
# ==============================================================================


def test_patch_status_missing_and_invalid_body():
    """Verify missing body or invalid field payload returns HTTP 422."""
    job = generation_job_service.create_job(prompt="A magic staff")

    # Missing body
    assert client.patch(f"/api/v1/generations/{job.job_id}/status").status_code == 422

    # Missing 'status' key
    assert client.patch(f"/api/v1/generations/{job.job_id}/status", json={}).status_code == 422

    # Invalid status value (not in enum)
    for bad_status in ["queued", "running", "cancelled", 123, None]:
        resp = client.patch(
            f"/api/v1/generations/{job.job_id}/status",
            json={"status": bad_status},
        )
        assert resp.status_code == 422


def test_patch_status_unknown_id_contract():
    """Verify non-existent UUID returns HTTP 404 matching ErrorResponse."""
    random_id = uuid.uuid4()
    response = client.patch(
        f"/api/v1/generations/{random_id}/status",
        json={"status": "processing"},
    )
    assert response.status_code == 404
    validated = ErrorResponse(**response.json())
    assert str(random_id) in validated.detail


def test_patch_status_invalid_transition_contract_409():
    """Verify invalid transitions return HTTP 409 Conflict matching ErrorResponse schema."""
    job = generation_job_service.create_job(prompt="A test archway")

    # Direct PENDING -> COMPLETED
    resp = client.patch(f"/api/v1/generations/{job.job_id}/status", json={"status": "completed"})
    assert resp.status_code == 409
    validated = ErrorResponse(**resp.json())
    assert "Cannot transition" in validated.detail

    # Direct PENDING -> FAILED
    resp = client.patch(f"/api/v1/generations/{job.job_id}/status", json={"status": "failed"})
    assert resp.status_code == 409
    assert "Cannot transition" in ErrorResponse(**resp.json()).detail


def test_patch_status_success_contract():
    """Verify valid status updates return HTTP 200 matching GenerationJobResponse."""
    job = generation_job_service.create_job(prompt="A silver chalice")

    response = client.patch(
        f"/api/v1/generations/{job.job_id}/status",
        json={"status": "processing"},
    )
    assert response.status_code == 200
    validated = GenerationJobResponse(**response.json())
    assert validated.status == GenerationJobStatus.PROCESSING
    assert validated.updated_at >= validated.created_at
