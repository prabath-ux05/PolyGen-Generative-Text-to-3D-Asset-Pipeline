"""Focused integration tests for the Text-to-3D pipeline orchestrator and asset delivery."""

import sys
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import get_pipeline_adapter
from backend.app.main import app
from backend.app.schemas.generation import OutputFormat
from backend.app.schemas.generation_job import (
    GenerationJobResponse,
    GenerationJobStatus,
)
from backend.app.services.generation_job_service import generation_job_service
from backend.app.services.pipeline_orchestrator import (
    GenerationPipelineOrchestrator,
    PipelineExecutionError,
    pipeline_orchestrator,
    sanitize_pipeline_error,
)
from backend.app.services.synthetic_adapter import SyntheticGeometryAdapter

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_job_store_and_overrides():
    """Ensure in-memory job store and dependency overrides are reset for each test."""
    generation_job_service.clear()
    app.dependency_overrides.clear()
    yield
    generation_job_service.clear()
    app.dependency_overrides.clear()


# ==============================================================================
# 1. Synthetic Geometry Adapter Unit Tests
# ==============================================================================


def test_synthetic_adapter_properties_and_generation():
    """Verify SyntheticGeometryAdapter metadata and primitive generation."""
    assert SyntheticGeometryAdapter.IS_SYNTHETIC is True
    assert SyntheticGeometryAdapter.ADAPTER_NAME == "synthetic_geometry_adapter"

    # Default box
    mesh_box = SyntheticGeometryAdapter.generate("A wooden storage crate")
    assert mesh_box is not None
    assert len(mesh_box.vertices) > 0
    assert len(mesh_box.faces) > 0
    assert mesh_box.is_watertight

    # Sphere keyword
    mesh_sphere = SyntheticGeometryAdapter.generate("A magical crystal orb")
    assert mesh_sphere is not None
    assert len(mesh_sphere.vertices) > 0

    # Cylinder keyword
    mesh_cyl = SyntheticGeometryAdapter.generate("An ancient Greek pillar")
    assert mesh_cyl is not None
    assert len(mesh_cyl.vertices) > 0


# ==============================================================================
# 2. Pipeline Orchestrator Unit & Integration Tests (Safe Error Handling)
# ==============================================================================


def test_pipeline_orchestrator_successful_execution(tmp_path):
    """Verify successful end-to-end orchestration: pending -> processing -> completed."""
    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
    )

    job = generation_job_service.create_job(
        prompt="A low-poly medieval wooden cart",
        output_format=OutputFormat.GLB,
    )
    assert job.status == GenerationJobStatus.PENDING
    assert job.model_url is None

    # Run pipeline with synthetic adapter
    exported_path = orchestrator.run_pipeline(
        job_id=job.job_id,
        prompt=job.prompt,
        output_format=job.output_format,
        adapter_name="synthetic",
    )

    # Asset verification
    assert exported_path.exists()
    assert exported_path.suffix == ".glb"
    assert exported_path.stat().st_size > 0

    # Job status verification
    updated_job = generation_job_service.get_job(job.job_id)
    assert updated_job is not None
    assert updated_job.status == GenerationJobStatus.COMPLETED
    assert updated_job.error_message is None
    assert updated_job.model_url == f"/api/v1/generations/{job.job_id}/asset"


def test_pipeline_orchestrator_failure_handling_and_safe_error_message(tmp_path):
    """Verify that errors transition job to FAILED with sanitized error message (no leaks)."""
    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
    )

    job = generation_job_service.create_job(
        prompt="A fantasy shield",
        output_format=OutputFormat.GLB,
    )

    # Run pipeline with invalid adapter
    with pytest.raises(PipelineExecutionError) as exc_info:
        orchestrator.run_pipeline(
            job_id=job.job_id,
            prompt=job.prompt,
            output_format=job.output_format,
            adapter_name="nonexistent_neural_model",
        )

    updated_job = generation_job_service.get_job(job.job_id)
    assert updated_job is not None
    assert updated_job.status == GenerationJobStatus.FAILED
    assert updated_job.error_message is not None

    # Verify sanitized, categorized error message without filesystem paths or stack traces
    assert updated_job.error_message == "The configured generation adapter is unavailable or unsupported."
    assert "C:\\" not in updated_job.error_message
    assert "nonexistent_neural_model" not in updated_job.error_message
    assert str(exc_info.value) == updated_job.error_message


def test_pipeline_orchestrator_unsupported_format_fails_safely(tmp_path):
    """Verify requesting OBJ format in Stage 2 cleanly transitions to FAILED with safe message."""
    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
    )

    job = generation_job_service.create_job(
        prompt="A textured potion bottle",
        output_format=OutputFormat.OBJ,
    )

    with pytest.raises(PipelineExecutionError):
        orchestrator.run_pipeline(
            job_id=job.job_id,
            prompt=job.prompt,
            output_format=job.output_format,
            adapter_name="synthetic",
        )

    updated_job = generation_job_service.get_job(job.job_id)
    assert updated_job.status == GenerationJobStatus.FAILED
    assert updated_job.error_message == "Requested 3D format is not supported for textured pipeline export."


def test_sanitize_pipeline_error_edge_cases():
    """Verify error sanitization across various exception types."""
    # Custom exception with filesystem paths
    file_err = OSError("Failed to open C:\\Users\\secret\\model.glb: Permission denied")
    sanitized = sanitize_pipeline_error(file_err)
    assert "C:\\" not in sanitized
    assert "secret" not in sanitized
    assert sanitized == "An internal error occurred during 3D asset generation."


# ==============================================================================
# 3. Server-Controlled Adapter Selection & Security Tests
# ==============================================================================


def test_client_header_cannot_override_server_none_configuration():
    """Verify that client headers (X-Pipeline-Adapter) CANNOT enable synthetic generation.

    Server-controlled configuration is the sole authority.
    """
    # Ensure server configuration is 'none' (default)
    app.dependency_overrides[get_pipeline_adapter] = lambda: "none"

    payload = {
        "prompt": "A crystal healing potion flask",
        "output_format": "glb",
    }
    # Malicious or unauthorized client attempts to force synthetic mode
    headers = {"X-Pipeline-Adapter": "synthetic"}

    response = client.post("/api/v1/generations", json=payload, headers=headers)
    assert response.status_code == 503
    assert response.json()["detail"] == "Text-to-3D generation engine is not yet integrated."
    assert len(generation_job_service._jobs) == 0


def test_post_generations_with_server_synthetic_configuration(tmp_path):
    """Verify POST /api/v1/generations when server configuration explicitly enables synthetic mode."""
    app.dependency_overrides[get_pipeline_adapter] = lambda: "synthetic"

    with patch.object(pipeline_orchestrator, "output_dir", tmp_path / "assets"):
        (tmp_path / "assets").mkdir(parents=True, exist_ok=True)

        payload = {
            "prompt": "A crystal healing potion flask",
            "output_format": "glb",
        }

        response = client.post("/api/v1/generations", json=payload)
        assert response.status_code == 202

        data = response.json()
        job_id = data["job_id"]
        assert data["prompt"] == payload["prompt"]
        assert data["output_format"] == "glb"

        # In TestClient, BackgroundTasks run synchronously before post() returns
        status_resp = client.get(f"/api/v1/generations/{job_id}")
        assert status_resp.status_code == 200
        completed_job = status_resp.json()
        assert completed_job["status"] == "completed"
        assert completed_job["model_url"] == f"/api/v1/generations/{job_id}/asset"

        # Verify asset streaming
        asset_resp = client.get(completed_job["model_url"])
        assert asset_resp.status_code == 200
        assert asset_resp.headers["content-type"] == "model/gltf-binary"
        assert len(asset_resp.content) > 0


# ==============================================================================
# 4. Asset Delivery Route Tests (Security & State Validation)
# ==============================================================================


def test_asset_retrieval_pending_or_processing_conflict():
    """Verify GET /{job_id}/asset returns HTTP 409 Conflict when asset is not ready."""
    job = generation_job_service.create_job(
        prompt="A medieval anvil",
        output_format=OutputFormat.GLB,
    )
    # Pending state
    resp = client.get(f"/api/v1/generations/{job.job_id}/asset")
    assert resp.status_code == 409
    assert "is not ready" in resp.json()["detail"]

    # Processing state
    generation_job_service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)
    resp2 = client.get(f"/api/v1/generations/{job.job_id}/asset")
    assert resp2.status_code == 409
    assert "is not ready" in resp2.json()["detail"]


def test_asset_retrieval_failed_job_conflict():
    """Verify GET /{job_id}/asset returns HTTP 409 when the job failed."""
    job = generation_job_service.create_job(
        prompt="A broken model",
        output_format=OutputFormat.GLB,
    )
    generation_job_service.update_job_status(
        job.job_id,
        GenerationJobStatus.PROCESSING,
    )
    generation_job_service.update_job_status(
        job.job_id,
        GenerationJobStatus.FAILED,
        error_message="Mesh validation failed.",
    )

    resp = client.get(f"/api/v1/generations/{job.job_id}/asset")
    assert resp.status_code == 409
    assert "failed" in resp.json()["detail"]


def test_asset_retrieval_unknown_job_returns_404():
    """Verify GET /{job_id}/asset for nonexistent job returns HTTP 404."""
    random_id = uuid.uuid4()
    resp = client.get(f"/api/v1/generations/{random_id}/asset")
    assert resp.status_code == 404
    assert f"'{random_id}' not found" in resp.json()["detail"]


def test_asset_retrieval_missing_file_on_disk_returns_404(tmp_path):
    """Verify GET /{job_id}/asset returns 404 if file was removed from disk."""
    with patch.object(pipeline_orchestrator, "output_dir", tmp_path / "empty_dir"):
        (tmp_path / "empty_dir").mkdir(parents=True, exist_ok=True)

        job = generation_job_service.create_job(
            prompt="A ghost model",
            output_format=OutputFormat.GLB,
        )
        generation_job_service.update_job_status(
            job.job_id,
            GenerationJobStatus.PROCESSING,
        )
        generation_job_service.update_job_status(
            job.job_id,
            GenerationJobStatus.COMPLETED,
            model_url=f"/api/v1/generations/{job.job_id}/asset",
        )

        resp = client.get(f"/api/v1/generations/{job.job_id}/asset")
        assert resp.status_code == 404
        assert "not found on disk" in resp.json()["detail"]


def test_obj_format_still_returns_503_with_server_synthetic_adapter():
    """Verify OBJ format in Stage 2 returns 503 even when server has synthetic adapter enabled."""
    app.dependency_overrides[get_pipeline_adapter] = lambda: "synthetic"

    payload = {
        "prompt": "A futuristic sci-fi helmet",
        "output_format": "obj",
    }
    response = client.post("/api/v1/generations", json=payload)
    assert response.status_code == 503
    assert "not yet integrated for OBJ" in response.json()["detail"]


def test_default_without_server_synthetic_config_returns_503():
    """Verify default request without server synthetic configuration preserves 503 baseline contract."""
    payload = {"prompt": "A medieval tower", "output_format": "glb"}
    response = client.post("/api/v1/generations", json=payload)
    assert response.status_code == 503
    assert response.json()["detail"] == "Text-to-3D generation engine is not yet integrated."
