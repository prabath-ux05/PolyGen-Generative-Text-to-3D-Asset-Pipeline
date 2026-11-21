import pytest

from ai_generation.error_handler import (
    ErrorCode,
    ErrorHandler,
    GenerationError,
)
from ai_generation.prompt_processor import PromptValidationError
from ai_generation.models.model_loader import ModelLoadError
from ai_generation.generation_validator import MeshValidationError
from ai_generation.exporter import MeshExportError
from ai_generation.generation_metadata import MetadataError


@pytest.fixture
def handler():
    return ErrorHandler()


@pytest.mark.parametrize(
    "exception, expected_code, expected_retryable",
    [
        (
            PromptValidationError("Empty prompt"),
            ErrorCode.INVALID_PROMPT,
            False,
        ),
        (
            ModelLoadError("Weights unavailable"),
            ErrorCode.MODEL_LOAD_FAILED,
            True,
        ),
        (
            MeshValidationError("Invalid vertices"),
            ErrorCode.INVALID_MESH,
            False,
        ),
        (
            MeshExportError("Disk write failed"),
            ErrorCode.EXPORT_FAILED,
            False,
        ),
        (
            MetadataError("Metadata write failed"),
            ErrorCode.METADATA_FAILED,
            True,
        ),
    ],
)
def test_known_errors_are_classified(
    handler, exception, expected_code, expected_retryable
):
    result = handler.handle(exception, stage="test_stage")

    assert isinstance(result, GenerationError)
    assert result.code == expected_code
    assert result.retryable is expected_retryable
    assert result.stage == "test_stage"


def test_inference_error_is_classified(handler):
    result = handler.handle(
        RuntimeError("Inference crashed"),
        stage="model_inference",
    )

    assert result.code == ErrorCode.INFERENCE_FAILED
    assert result.retryable is False


def test_configuration_error_is_classified(handler):
    result = handler.handle(
        RuntimeError("Missing adapter"),
        stage="configuration",
    )

    assert result.code == ErrorCode.CONFIGURATION_ERROR


def test_unknown_error_is_classified(handler):
    result = handler.handle(
        ValueError("Unknown problem"),
        stage="some_stage",
    )

    assert result.code == ErrorCode.UNEXPECTED_ERROR
    assert result.stage == "some_stage"


def test_error_has_unique_id(handler):
    first = handler.handle(ValueError("first"))
    second = handler.handle(ValueError("second"))

    assert first.error_id != second.error_id


def test_error_contains_context(handler):
    result = handler.handle(
        ValueError("failed"),
        stage="export",
        context={"model": "shap-e"},
    )

    assert result.context == {"model": "shap-e"}


def test_error_to_dict_contains_required_fields(handler):
    result = handler.handle(
        ValueError("failed"),
        stage="export",
    )

    data = result.to_dict()

    assert data["error_id"] == result.error_id
    assert data["code"] == ErrorCode.UNEXPECTED_ERROR.value
    assert data["stage"] == "export"
    assert data["retryable"] is False
    assert data["message"] == str(result)


def test_existing_generation_error_is_preserved(handler):
    original = GenerationError(
        "Already classified",
        code=ErrorCode.INVALID_PROMPT,
        stage="prompt_processing",
    )

    result = handler.handle(original)

    assert result is original


def test_empty_exception_message_is_supported(handler):
    result = handler.handle(ValueError(""))

    assert isinstance(result, GenerationError)
    assert result.code == ErrorCode.UNEXPECTED_ERROR


def test_error_code_accepts_string_value():
    error = GenerationError(
        "Invalid input",
        code="invalid_prompt",
        stage="prompt_processing",
    )

    assert error.code == ErrorCode.INVALID_PROMPT


def test_error_context_is_not_shared():
    original = {"model": "shap-e"}
    error = GenerationError("Failed", context=original)

    original["model"] = "changed"

    assert error.context["model"] == "shap-e"
