"""Coordinate the complete text-to-3D generation workflow."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import trimesh

from ai_generation.model_manager import ModelManager, ModelStatus
from ai_generation.models.model_loader import ShapEModelLoader
from ai_generation.prompt_processor import PromptProcessor
from ai_generation.exporter import MeshExporter
from ai_generation.generation_metadata import GenerationMetadata
from ai_generation.performance_monitor import PerformanceMonitor


class GenerationError(RuntimeError):
    """Raised when the generation pipeline fails."""


@dataclass(frozen=True)
class GenerationResult:
    """Contain the output and details of a generation operation."""

    output_path: Path
    metadata: GenerationMetadata
    performance: object
    processed_prompt: object

    def to_dict(self):
        """Convert the generation result into a dictionary."""
        return {
            "output_path": str(self.output_path),
            "metadata": self.metadata.to_dict(),
            "performance": self.performance.to_dict(),
            "processed_prompt": self.processed_prompt.to_dict(),
        }


class TextTo3DGenerator:
    """Integrate prompt processing, model loading, export and monitoring."""

    MODEL_NAME = "shap-e"

    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        model_loader: Optional[ShapEModelLoader] = None,
        prompt_processor: Optional[PromptProcessor] = None,
        exporter: Optional[MeshExporter] = None,
        performance_monitor: Optional[PerformanceMonitor] = None,
        metadata_directory="artifacts/metadata",
        generation_fn: Optional[Callable] = None,
    ):
        self.model_manager = model_manager or ModelManager()

        self.model_loader = model_loader or ShapEModelLoader(
            device=self.model_manager.get_device()
        )

        self.prompt_processor = prompt_processor or PromptProcessor()
        self.exporter = exporter or MeshExporter()
        self.performance_monitor = performance_monitor or PerformanceMonitor()

        self.metadata_directory = Path(metadata_directory)
        self.generation_fn = generation_fn

    def generate(
        self,
        prompt,
        file_format="obj",
        filename=None,
        generation_fn=None,
    ):
        """Generate, validate, export and record a 3D mesh.

        The generation function receives:
            cleaned_prompt: Processed text prompt.
            components: Loaded model components.

        It must return a trimesh.Trimesh object.
        """
        selected = False
        metrics = None

        self.performance_monitor.start()

        try:
            # Step 1: Process and validate the prompt.
            processed = self.prompt_processor.process_prompt(prompt)

            # Step 2: Select the configured model.
            self.model_manager.select_model(self.MODEL_NAME)
            selected = True

            self.model_manager.update_status(
                self.MODEL_NAME,
                ModelStatus.LOADING,
            )

            # Step 3: Load model components.
            components = self.model_loader.load_components()

            # Step 4: Run the generation adapter.
            generator_function = generation_fn or self.generation_fn

            if generator_function is None:
                raise GenerationError(
                    "No generation function configured. "
                    "Provide a Shap-E inference adapter."
                )

            mesh = generator_function(
                processed.cleaned_prompt,
                components,
            )

            # Step 5: Validate the generated mesh.
            self.exporter.validate_mesh(mesh)

            # Step 6: Export the mesh.
            output_path = self.exporter.export(
                mesh,
                file_format=file_format,
                filename=filename,
            )

            # Step 7: Mark the model as ready.
            self.model_manager.update_status(
                self.MODEL_NAME,
                ModelStatus.READY,
            )

            # Step 8: Stop performance monitoring.
            metrics = self.performance_monitor.stop()

            # Step 9: Create generation metadata.
            metadata = GenerationMetadata(
                prompt=processed.cleaned_prompt,
                model_name=self.MODEL_NAME,
                output_path=str(output_path),
                file_format=file_format.lower(),
                generation_time_seconds=metrics.elapsed_seconds,
                status="success",
                extra={
                    "device": self.model_manager.get_device(),
                    "word_count": processed.word_count,
                    "character_count": processed.character_count,
                    "performance": metrics.to_dict(),
                },
            )

            # Step 10: Save metadata.
            metadata.save(self.metadata_directory)

            return GenerationResult(
                output_path=output_path,
                metadata=metadata,
                performance=metrics,
                processed_prompt=processed,
            )

        except Exception as exc:
            # Record failure information.
            if self.performance_monitor.is_running:
                metrics = self.performance_monitor.stop(error=exc)

            if selected:
                try:
                    self.model_manager.update_status(
                        self.MODEL_NAME,
                        ModelStatus.FAILED,
                    )
                except Exception:
                    pass

            if isinstance(exc, GenerationError):
                raise

            raise GenerationError(
                f"Text-to-3D generation failed: {exc}"
            ) from exc
