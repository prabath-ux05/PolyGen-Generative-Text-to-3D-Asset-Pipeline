"""Centralized error classification for the text-to-3D pipeline."""

from enum import Enum
from uuid import uuid4
import logging

from ai_generation.prompt_processor import PromptValidationError
from ai_generation.models.model_loader import ModelLoadError
from ai_generation.generation_validator import MeshValidationError
from ai_generation.exporter import MeshExportError
from ai_generation.generation_metadata import MetadataError


logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    INVALID_PROMPT = "invalid_prompt"
    MODEL_LOAD_FAILED = "model_load_failed"
    INFERENCE_FAILED = "inference_failed"
    INVALID_MESH = "invalid_mesh"
    EXPORT_FAILED = "export_failed"
    METADATA_FAILED = "metadata_failed"
    CONFIGURATION_ERROR = "configuration_error"
    UNEXPECTED_ERROR = "unexpected_error"


class GenerationError(RuntimeError):
    """Structured exception raised by the generation pipeline."""

    def __init__(
        self,
        message,
        code=ErrorCode.UNEXPECTED_ERROR,
        stage="unknown",
        retryable=False,
        context=None,
        error_id=None,
    ):
        super().__init__(message)
        self.code = ErrorCode(code)
        self.stage = stage
        self.retryable = bool(retryable)
        self.context = dict(context or {})
        self.error_id = error_id or uuid4().hex

    def to_dict(self):
        """Return structured, JSON-friendly error information."""
        return {
            "error_id": self.error_id,
            "error_type": type(self).__name__,
            "code": self.code.value,
            "message": str(self),
            "stage": self.stage,
            "retryable": self.retryable,
            "context": self.context,
        }


class ErrorHandler:
    """Convert internal exceptions into consistent pipeline errors."""

    ERROR_RULES = (
        (
            PromptValidationError,
            ErrorCode.INVALID_PROMPT,
            "The input prompt is invalid",
            False,
        ),
        (
            ModelLoadError,
            ErrorCode.MODEL_LOAD_FAILED,
            "The 3D model could not be loaded",
            True,
        ),
        (
            MeshValidationError,
            ErrorCode.INVALID_MESH,
            "The generated mesh failed validation",
            False,
        ),
        (
            MeshExportError,
            ErrorCode.EXPORT_FAILED,
            "The mesh could not be exported",
            False,
        ),
        (
            MetadataError,
            ErrorCode.METADATA_FAILED,
            "Generation metadata could not be saved",
            True,
        ),
    )

    def handle(self, exception, stage="unknown", context=None):
        """Classify an exception and return a GenerationError."""
        if isinstance(exception, GenerationError):
            return exception

        details = str(exception).strip() or type(exception).__name__

        for exception_type, code, message, retryable in self.ERROR_RULES:
            if isinstance(exception, exception_type):
                error = GenerationError(
                    f"{message}: {details}",
                    code=code,
                    stage=stage,
                    retryable=retryable,
                    context=context,
                )
                logger.error(
                    "Generation error %s at %s: %s",
                    code.value,
                    stage,
                    details,
                )
                return error

        if stage == "model_inference":
            code = ErrorCode.INFERENCE_FAILED
            message = "3D model inference failed"
        elif stage == "configuration":
            code = ErrorCode.CONFIGURATION_ERROR
            message = "Generation configuration is invalid"
        else:
            code = ErrorCode.UNEXPECTED_ERROR
            message = "An unexpected generation error occurred"

        logger.error(
            "Unexpected generation error at %s: %s",
            stage,
            details,
            exc_info=(
                type(exception),
                exception,
                exception.__traceback__,
            ),
        )

        return GenerationError(
            f"{message}: {details}",
            code=code,
            stage=stage,
            retryable=False,
            context=context,
        )
