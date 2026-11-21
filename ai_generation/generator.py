"""Coordinate the complete text-to-3D generation workflow."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from ai_generation.model_manager import ModelManager, ModelStatus
from ai_generation.models.model_loader import ShapEModelLoader
from ai_generation.prompt_processor import PromptProcessor
from ai_generation.exporter import MeshExporter
from ai_generation.generation_metadata import GenerationMetadata
from ai_generation.performance_monitor import PerformanceMonitor
from ai_generation.generation_validator import MeshValidator
from ai_generation.config import GenerationConfig
from ai_generation.error_handler import (
    ErrorCode,
    ErrorHandler,
    GenerationError,
)


@dataclass(frozen=True)
class GenerationResult:
    """Contain the output and details of a generation operation."""

    output_path: Path
    metadata: GenerationMetadata
    performance: object
    processed_prompt: object
    validation: object

    def to_dict(self):
        """Convert the generation result into a dictionary."""
        return {
            "output_path": str(self.output_path),
            "metadata": self.metadata.to_dict(),
            "performance": self.performance.to_dict(),
            "processed_prompt": self.processed_prompt.to_dict(),
            "validation": self.validation.to_dict(),
        }


class TextTo3DGenerator:
    """Integrate generation, validation, export and error handling."""

    MODEL_NAME = "shap-e"

    def __init__(
        self,
        model_manager: Optional[ModelManager] = None,
        model_loader: Optional[ShapEModelLoader] = None,
        prompt_processor: Optional[PromptProcessor] = None,
        exporter: Optional[MeshExporter] = None,
        performance_monitor: Optional[PerformanceMonitor] = None,
        metadata_directory=None,
        generation_fn: Optional[Callable] = None,
        mesh_validator: Optional[MeshValidator] = None,
        error_handler: Optional[ErrorHandler] = None,
        config: Optional[GenerationConfig] = None,
    ):
        self.config = config or GenerationConfig.from_env()
        self.model_manager = model_manager or ModelManager(
            device=self.config.device
        )

        self.model_loader = model_loader or ShapEModelLoader(
            device=self.model_manager.get_device()
        )

        self.prompt_processor = prompt_processor or PromptProcessor(
            min_length=self.config.min_prompt_length,
            max_length=self.config.max_prompt_length,
        )
        self.exporter = exporter or MeshExporter(
            output_dir=self.config.output_dir
        )
        self.performance_monitor = (
            performance_monitor or PerformanceMonitor()
        )
        self.mesh_validator = mesh_validator or MeshValidator()
        self.error_handler = error_handler or ErrorHandler()

        self.metadata_directory = Path(
            metadata_directory
            if metadata_directory is not None
            else self.config.metadata_dir
        )
        self.generation_fn = generation_fn

    def generate(
        self,
        prompt,
        file_format=None,
        filename=None,
        generation_fn=None,
    ):
        """Generate a mesh and convert failures into structured errors."""
        if file_format is None:
            file_format = self.config.default_format

        selected = False
        stage = "prompt_processing"

        self.performance_monitor.start()

        try:
            processed = self.prompt_processor.process_prompt(prompt)

            stage = "model_selection"
            self.model_manager.select_model(self.MODEL_NAME)
            selected = True

            self.model_manager.update_status(
                self.MODEL_NAME,
                ModelStatus.LOADING,
            )

            stage = "model_loading"
            components = self.model_loader.load_components()

            stage = "model_inference"
            generator_function = generation_fn or self.generation_fn

            if generator_function is None:
                raise GenerationError(
                    "No generation function configured. "
                    "Provide a Shap-E inference adapter.",
                    code=ErrorCode.CONFIGURATION_ERROR,
                    stage="configuration",
                )

            mesh = generator_function(
                processed.cleaned_prompt,
                components,
            )

            stage = "mesh_validation"
            validation = self.mesh_validator.validate_or_raise(mesh)

            stage = "mesh_export"
            output_path = self.exporter.export(
                mesh,
                file_format=file_format,
                filename=filename,
            )

            stage = "model_status_update"
            self.model_manager.update_status(
                self.MODEL_NAME,
                ModelStatus.READY,
            )

            stage = "performance_monitoring"
            metrics = self.performance_monitor.stop()

            stage = "metadata_creation"
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
                    "validation": validation.to_dict(),
                },
            )

            stage = "metadata_saving"
            metadata.save(self.metadata_directory)

            return GenerationResult(
                output_path=output_path,
                metadata=metadata,
                performance=metrics,
                processed_prompt=processed,
                validation=validation,
            )

        except Exception as exc:
            if self.performance_monitor.is_running:
                try:
                    self.performance_monitor.stop(error=exc)
                except Exception:
                    pass

            if selected:
                try:
                    self.model_manager.update_status(
                        self.MODEL_NAME,
                        ModelStatus.FAILED,
                    )
                except Exception:
                    pass

            error = self.error_handler.handle(
                exc,
                stage=stage,
                context={"model": self.MODEL_NAME},
            )

            if error is exc:
                raise

            raise error from exc
