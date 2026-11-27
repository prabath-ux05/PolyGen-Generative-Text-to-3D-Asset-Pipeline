"""Pipeline orchestrator coordinating end-to-end Text-to-3D asset generation."""

import logging
import threading
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from ai_generation.exporter import MeshExporter
from ai_generation.generation_validator import MeshValidator
from backend.app.schemas.generation import OutputFormat
from backend.app.schemas.generation_job import GenerationJobStatus
from backend.app.services.generation_job_service import (
    GenerationJobService,
    generation_job_service,
)
from backend.app.services.synthetic_adapter import SyntheticGeometryAdapter
from mesh_processing.mesh_inspector import inspect_mesh
from mesh_processing.uv_mapper import generate_uv
from texture_engine.material_builder import build_pbr_material

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = Path("artifacts/generated")


class PipelineExecutionError(Exception):
    """Raised when an error occurs during pipeline orchestration."""

    pass


def sanitize_pipeline_error(exc: Exception) -> str:
    """Convert an internal pipeline exception into a safe, client-facing error message.

    Ensures internal filesystem paths, stack trace artifacts, or sensitive system details
    are not exposed to API clients.
    """
    msg = str(exc)

    if "Only GLB format is supported" in msg or "not yet supported" in msg:
        return "Requested 3D format is not supported for textured pipeline export."

    if "not currently available or configured" in msg or "unsupported" in msg:
        return "The configured generation adapter is unavailable or unsupported."

    from ai_generation.generation_validator import MeshValidationError

    if isinstance(exc, MeshValidationError):
        return "Generated 3D geometry failed mesh quality validation."

    if "CUDA out of memory" in msg or "out of memory" in msg.lower():
        return "3D asset generation ran out of GPU memory. Please try again with a simpler prompt."

    if "Shap-E is not installed" in msg or "not installed" in msg.lower():
        return "The neural generation engine is not available on this server."

    return "An internal error occurred during 3D asset generation."


class GenerationPipelineOrchestrator:
    """Orchestrates end-to-end 3D asset generation across modular pipeline stages."""

    def __init__(
        self,
        job_service: GenerationJobService | None = None,
        output_dir: Path | str | None = None,
        neural_adapter: Any | None = None,
        exporter: Any | None = None,
    ):
        self.job_service = job_service or generation_job_service
        self.output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.mesh_validator = MeshValidator()
        self._exporter: Any | None = exporter
        self._neural_adapter = neural_adapter
        self._inference_lock = threading.Lock()

    @property
    def exporter(self) -> Any:
        """Return the mesh exporter, dynamically respecting output_dir or custom exporter."""
        if self._exporter is not None:
            return self._exporter
        return MeshExporter(output_dir=self.output_dir)

    @exporter.setter
    def exporter(self, val: Any) -> None:
        self._exporter = val

    @property
    def neural_adapter(self) -> Any:
        """Lazily initialize and return the neural inference adapter."""
        if self._neural_adapter is None:
            from ai_generation.models.shap_e_adapter import ShapEInferenceAdapter

            self._neural_adapter = ShapEInferenceAdapter()
        return self._neural_adapter

    def run_pipeline(
        self,
        job_id: UUID | str,
        prompt: str,
        output_format: OutputFormat = OutputFormat.GLB,
        adapter_name: str = "synthetic",
    ) -> Path:
        """Execute the end-to-end generation, inspection, UV mapping, material, and export workflow.

        Args:
            job_id: Unique UUID of the generation job.
            prompt: Text prompt describing the target asset.
            output_format: Target 3D file format (defaults to GLB).
            adapter_name: Generation adapter ("synthetic" or "neural").

        Returns:
            The Path to the exported 3D asset file.

        Raises:
            PipelineExecutionError: If any pipeline stage fails.
        """
        parsed_id = UUID(str(job_id))

        # 1. Transition job to PROCESSING
        try:
            self.job_service.update_job_status(
                job_id=parsed_id,
                new_status=GenerationJobStatus.PROCESSING,
            )
        except Exception as exc:
            logger.error(f"Failed to transition job {parsed_id} to PROCESSING: {exc}")
            raise PipelineExecutionError(f"Job state transition failed: {exc}") from exc

        try:
            # 2. Format validation check (Stage 2 supports GLB)
            if output_format != OutputFormat.GLB:
                raise PipelineExecutionError(
                    f"Format '{output_format.value}' is not yet supported for textured pipeline export. "
                    "Only GLB format is supported in this stage."
                )

            # 3. Adapter selection
            if adapter_name == "synthetic":
                raw_mesh = SyntheticGeometryAdapter.generate(prompt=prompt)
            elif adapter_name == "neural":
                # Strictly serialize neural inference to protect GPU VRAM (RTX 2050 4GB budget)
                with self._inference_lock:
                    if hasattr(self.neural_adapter, "generate") and callable(
                        self.neural_adapter.generate
                    ):
                        raw_mesh = self.neural_adapter.generate(prompt=prompt)
                    else:
                        raw_mesh = self.neural_adapter(prompt=prompt)
            else:
                raise PipelineExecutionError(
                    f"Adapter '{adapter_name}' is not currently available or configured."
                )

            # 4. Geometry validation
            self.mesh_validator.validate_or_raise(raw_mesh)

            # 5. Mesh quality inspection
            _ = inspect_mesh(raw_mesh)

            # 6. UV mapping projection
            uv_mesh = generate_uv(raw_mesh)

            # 7. PBR material synthesis and attachment
            material = build_pbr_material(
                name=f"PolyGen_Mat_{parsed_id.hex[:8]}",
                base_color_factor=(210, 195, 175, 255),
                metallic_factor=0.2,
                roughness_factor=0.6,
                double_sided=False,
            )
            uv_mesh.visual.material = material

            # 8. GLB mesh export
            export_path = self.exporter.export(
                mesh=uv_mesh,
                file_format=output_format.value,
                filename=str(parsed_id),
            )

            # 9. Formulate asset URL for client retrieval
            model_url = f"/api/v1/generations/{parsed_id}/asset"

            # 10. Transition job to COMPLETED
            self.job_service.update_job_status(
                job_id=parsed_id,
                new_status=GenerationJobStatus.COMPLETED,
                model_url=model_url,
            )

            return export_path

        except Exception as exc:
            # Log full exception with traceback securely on the server
            logger.exception(f"Generation pipeline failed for job {parsed_id}: {exc}")

            # Store sanitized message safe for client exposure
            safe_message = sanitize_pipeline_error(exc)
            try:
                self.job_service.update_job_status(
                    job_id=parsed_id,
                    new_status=GenerationJobStatus.FAILED,
                    error_message=safe_message,
                )
            except Exception as update_err:
                logger.error(f"Failed to record failure status for job {parsed_id}: {update_err}")

            raise PipelineExecutionError(safe_message) from exc


# Shared global instance
pipeline_orchestrator = GenerationPipelineOrchestrator()
