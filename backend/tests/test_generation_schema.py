"""Unit tests for the Text-to-3D GenerationRequest Pydantic schema."""

import sys
from pathlib import Path
import pytest
from pydantic import ValidationError

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.schemas.generation import (
    MAX_PROMPT_LENGTH,
    GenerationRequest,
    OutputFormat,
)


def test_valid_generation_request_default_format():
    """Verify that a valid prompt succeeds and defaults to GLB format."""
    prompt_text = "A stylized low-poly wooden treasure chest"
    request = GenerationRequest(prompt=prompt_text)

    assert request.prompt == prompt_text
    assert request.output_format == OutputFormat.GLB


def test_valid_obj_format():
    """Verify that OBJ format is accepted in lowercase, uppercase, and enum member form."""
    req_lower = GenerationRequest(prompt="A sci-fi drone", output_format="obj")
    assert req_lower.output_format == OutputFormat.OBJ

    req_upper = GenerationRequest(prompt="A sci-fi drone", output_format="OBJ")
    assert req_upper.output_format == OutputFormat.OBJ

    req_enum = GenerationRequest(
        prompt="A sci-fi drone", output_format=OutputFormat.OBJ
    )
    assert req_enum.output_format == OutputFormat.OBJ


def test_valid_glb_format():
    """Verify that GLB format is accepted in lowercase, uppercase, and enum member form."""
    req_lower = GenerationRequest(prompt="A medieval anvil", output_format="glb")
    assert req_lower.output_format == OutputFormat.GLB

    req_upper = GenerationRequest(prompt="A medieval anvil", output_format="GLB")
    assert req_upper.output_format == OutputFormat.GLB

    req_enum = GenerationRequest(
        prompt="A medieval anvil", output_format=OutputFormat.GLB
    )
    assert req_enum.output_format == OutputFormat.GLB


def test_prompt_whitespace_trimming():
    """Verify that leading and trailing whitespace is stripped from prompts."""
    raw_prompt = "   A cyberpunk flying motorcycle   "
    request = GenerationRequest(prompt=raw_prompt)
    assert request.prompt == "A cyberpunk flying motorcycle"


def test_missing_prompt():
    """Verify that omitting the required prompt raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        GenerationRequest()  # type: ignore[call-arg]

    errors = exc_info.value.errors()
    assert any(err["loc"] == ("prompt",) and err["type"] == "missing" for err in errors)


def test_empty_prompt():
    """Verify that an empty string prompt raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        GenerationRequest(prompt="")

    errors = exc_info.value.errors()
    assert any("prompt" in err["loc"] for err in errors)


def test_whitespace_only_prompt():
    """Verify that a prompt composed solely of whitespace raises a ValidationError."""
    for ws in ["   ", "\t", "\n\n   \t"]:
        with pytest.raises(ValidationError) as exc_info:
            GenerationRequest(prompt=ws)

        errors = exc_info.value.errors()
        assert any("prompt" in err["loc"] for err in errors)


def test_prompt_boundary_and_exceeding_max_length():
    """Verify prompt length boundaries (at max limit passes, max + 1 fails)."""
    # Exactly at max limit should succeed
    exact_prompt = "a" * MAX_PROMPT_LENGTH
    req = GenerationRequest(prompt=exact_prompt)
    assert len(req.prompt) == MAX_PROMPT_LENGTH

    # Exceeding max limit should fail
    overflow_prompt = "a" * (MAX_PROMPT_LENGTH + 1)
    with pytest.raises(ValidationError) as exc_info:
        GenerationRequest(prompt=overflow_prompt)

    errors = exc_info.value.errors()
    assert any("prompt" in err["loc"] for err in errors)


def test_unsupported_output_format():
    """Verify that unsupported 3D formats raise a ValidationError."""
    unsupported_formats = ["stl", "fbx", "blend", "ply", "dae", "invalid_format"]
    for fmt in unsupported_formats:
        with pytest.raises(ValidationError) as exc_info:
            GenerationRequest(prompt="A test asset", output_format=fmt)  # type: ignore[arg-type]

        errors = exc_info.value.errors()
        assert any("output_format" in err["loc"] for err in errors)
