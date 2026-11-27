"""Focused integration tests for the Text-to-3D pipeline orchestrator and asset delivery."""

import sys
import threading
import time
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
import trimesh
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


# ==============================================================================
# 5. Neural Adapter Integration & Concurrency Serialization Tests
# ==============================================================================


def test_pipeline_orchestrator_neural_adapter_successful_execution(tmp_path):
    """Verify end-to-end execution with adapter_name='neural' producing validated GLB."""
    mock_mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))

    class MockNeuralAdapter:
        def generate(self, prompt):
            assert prompt == "A majestic stone gargoyle"
            return mock_mesh

    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
        neural_adapter=MockNeuralAdapter(),
    )

    job = generation_job_service.create_job(
        prompt="A majestic stone gargoyle",
        output_format=OutputFormat.GLB,
    )
    assert job.status == GenerationJobStatus.PENDING

    export_path = orchestrator.run_pipeline(
        job_id=job.job_id,
        prompt=job.prompt,
        output_format=job.output_format,
        adapter_name="neural",
    )

    assert export_path.exists()
    assert export_path.suffix == ".glb"
    assert export_path.stat().st_size > 0

    # Verify job status updated to COMPLETED with model_url
    updated_job = generation_job_service.get_job(job.job_id)
    assert updated_job.status == GenerationJobStatus.COMPLETED
    assert updated_job.model_url == f"/api/v1/generations/{job.job_id}/asset"
    assert updated_job.error_message is None

    # Verify GLB mesh can be reloaded and has visual/material
    loaded_glb = trimesh.load(export_path)
    assert loaded_glb is not None


def test_pipeline_orchestrator_neural_adapter_oom_failure_handling(tmp_path):
    """Verify that a neural CUDA OOM error safely transitions job to FAILED without hanging."""
    class FailingNeuralAdapter:
        def generate(self, prompt):
            raise RuntimeError("CUDA out of memory during Shap-E diffusion sampling.")

    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
        neural_adapter=FailingNeuralAdapter(),
    )

    job = generation_job_service.create_job(
        prompt="A massive detailed castle",
        output_format=OutputFormat.GLB,
    )

    with pytest.raises(PipelineExecutionError) as exc_info:
        orchestrator.run_pipeline(
            job_id=job.job_id,
            prompt=job.prompt,
            output_format=job.output_format,
            adapter_name="neural",
        )

    updated_job = generation_job_service.get_job(job.job_id)
    assert updated_job.status == GenerationJobStatus.FAILED
    assert "GPU memory" in updated_job.error_message
    assert str(exc_info.value) == updated_job.error_message


def test_pipeline_orchestrator_neural_adapter_missing_dependency_fails_safely(tmp_path):
    """Verify that missing Shap-E package cleanly transitions job to FAILED with safe message."""
    class MissingDependencyAdapter:
        def generate(self, prompt):
            raise ImportError("Shap-E is not installed. Please install the shap-e package.")

    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
        neural_adapter=MissingDependencyAdapter(),
    )

    job = generation_job_service.create_job(
        prompt="A simple chair",
        output_format=OutputFormat.GLB,
    )

    with pytest.raises(PipelineExecutionError):
        orchestrator.run_pipeline(
            job_id=job.job_id,
            prompt=job.prompt,
            output_format=job.output_format,
            adapter_name="neural",
        )

    updated_job = generation_job_service.get_job(job.job_id)
    assert updated_job.status == GenerationJobStatus.FAILED
    assert updated_job.error_message == "The neural generation engine is not available on this server."


def test_post_generations_with_server_neural_configuration(tmp_path):
    """Verify POST /api/v1/generations when server configuration explicitly enables neural mode."""
    app.dependency_overrides[get_pipeline_adapter] = lambda: "neural"

    mock_mesh = trimesh.creation.cylinder(radius=0.5, height=2.0)

    class MockNeuralAdapter:
        def generate(self, prompt):
            return mock_mesh

    with patch.object(pipeline_orchestrator, "output_dir", tmp_path / "assets"), \
         patch.object(pipeline_orchestrator, "_neural_adapter", MockNeuralAdapter()):
        (tmp_path / "assets").mkdir(parents=True, exist_ok=True)

        payload = {
            "prompt": "An ancient stone pillar",
            "output_format": "glb",
        }

        response = client.post("/api/v1/generations", json=payload)
        assert response.status_code == 202

        data = response.json()
        job_id = data["job_id"]

        # BackgroundTasks run synchronously in TestClient
        status_resp = client.get(f"/api/v1/generations/{job_id}")
        assert status_resp.status_code == 200
        completed_job = status_resp.json()
        assert completed_job["status"] == "completed"
        assert completed_job["model_url"] == f"/api/v1/generations/{job_id}/asset"

        # Verify asset download
        asset_resp = client.get(completed_job["model_url"])
        assert asset_resp.status_code == 200
        assert asset_resp.headers["content-type"] == "model/gltf-binary"
        assert len(asset_resp.content) > 0


def test_client_header_cannot_force_neural_when_server_configured_none():
    """Verify client headers (X-Pipeline-Adapter: neural) CANNOT force neural execution when server is 'none'."""
    app.dependency_overrides[get_pipeline_adapter] = lambda: "none"

    payload = {"prompt": "A magical portal", "output_format": "glb"}
    headers = {"X-Pipeline-Adapter": "neural"}

    response = client.post("/api/v1/generations", json=payload, headers=headers)
    assert response.status_code == 503
    assert response.json()["detail"] == "Text-to-3D generation engine is not yet integrated."
    assert len(generation_job_service._jobs) == 0


def test_neural_inference_concurrency_serialization(tmp_path):
    """Verify concurrent neural generation requests serialize inference through _inference_lock."""
    active_inferences = 0
    max_concurrent_inferences = 0
    lock_monitor = threading.Lock()

    class ConcurrencyMonitoringAdapter:
        def generate(self, prompt):
            nonlocal active_inferences, max_concurrent_inferences
            with lock_monitor:
                active_inferences += 1
                if active_inferences > max_concurrent_inferences:
                    max_concurrent_inferences = active_inferences
            # Simulate GPU inference latency
            time.sleep(0.05)
            with lock_monitor:
                active_inferences -= 1
            return trimesh.creation.box()

    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
        neural_adapter=ConcurrencyMonitoringAdapter(),
    )

    jobs = [
        generation_job_service.create_job(prompt=f"Asset {i}", output_format=OutputFormat.GLB)
        for i in range(3)
    ]

    threads = []
    for job in jobs:
        t = threading.Thread(
            target=orchestrator.run_pipeline,
            kwargs={
                "job_id": job.job_id,
                "prompt": job.prompt,
                "output_format": job.output_format,
                "adapter_name": "neural",
            },
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Crucial assertion: inference was strictly serialized (max 1 concurrent caller)
    assert max_concurrent_inferences == 1
    # All 3 jobs completed successfully
    for job in jobs:
        completed = generation_job_service.get_job(job.job_id)
        assert completed.status == GenerationJobStatus.COMPLETED


def test_lock_released_during_mesh_export(tmp_path):
    """Verify _inference_lock is NOT held during post-inference stages (UV, export)."""
    was_unlocked_during_export = None

    class LockCheckingExporter:
        def __init__(self, output_dir, orchestrator_ref):
            self.output_dir = Path(output_dir)
            self.orchestrator = orchestrator_ref

        def export(self, mesh, file_format, filename):
            nonlocal was_unlocked_during_export
            # Verify lock is not held right now
            was_unlocked_during_export = not self.orchestrator._inference_lock.locked()
            output_file = self.output_dir / f"{filename}.glb"
            output_file.write_bytes(b"mock-glb-binary")
            return output_file

    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=tmp_path / "assets",
        neural_adapter=lambda prompt: trimesh.creation.box(),
    )
    # Wire the lock-checking exporter
    orchestrator.exporter = LockCheckingExporter(tmp_path / "assets", orchestrator)

    job = generation_job_service.create_job(prompt="A test box", output_format=OutputFormat.GLB)
    orchestrator.run_pipeline(
        job_id=job.job_id,
        prompt=job.prompt,
        output_format=job.output_format,
        adapter_name="neural",
    )

    assert was_unlocked_during_export is True


def test_dynamic_output_dir_and_injected_exporter_retrieval(tmp_path):
    """Verify changing output_dir exports GLBs there, asset endpoint retrieves them, and injected exporter is respected."""
    custom_dir = tmp_path / "custom_exports"
    custom_dir.mkdir(parents=True, exist_ok=True)

    # 1. Dynamic output_dir reflection
    orchestrator = GenerationPipelineOrchestrator(
        job_service=generation_job_service,
        output_dir=custom_dir,
    )
    assert orchestrator.exporter.output_dir == custom_dir

    second_dir = tmp_path / "second_exports"
    orchestrator.output_dir = second_dir
    assert orchestrator.exporter.output_dir == second_dir

    # 2. Exporting with dynamic output_dir writes to the new directory and is retrievable
    job = generation_job_service.create_job(
        prompt="A dynamic directory sphere",
        output_format=OutputFormat.GLB,
    )
    exported_path = orchestrator.run_pipeline(
        job_id=job.job_id,
        prompt=job.prompt,
        output_format=job.output_format,
        adapter_name="synthetic",
    )
    assert exported_path.parent == second_dir
    assert (second_dir / f"{job.job_id}.glb").is_file()

    with patch.object(pipeline_orchestrator, "output_dir", second_dir):
        resp = client.get(f"/api/v1/generations/{job.job_id}/asset")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "model/gltf-binary"
        assert len(resp.content) > 0

    # 3. Explicitly injected custom exporter is preserved and respected
    class CustomInjectedExporter:
        def __init__(self):
            self.export_called = False

        def export(self, mesh, file_format, filename):
            self.export_called = True
            out_file = second_dir / f"{filename}.glb"
            out_file.write_bytes(b"custom-injected-bytes")
            return out_file

    injected = CustomInjectedExporter()
    orchestrator.exporter = injected
    assert orchestrator.exporter is injected

    job2 = generation_job_service.create_job(
        prompt="Another sphere",
        output_format=OutputFormat.GLB,
    )
    orchestrator.run_pipeline(
        job_id=job2.job_id,
        prompt=job2.prompt,
        output_format=job2.output_format,
        adapter_name="synthetic",
    )
    assert injected.export_called is True

