"""Pydantic schemas for text-to-3D generation requests."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

MIN_PROMPT_LENGTH: int = 1
MAX_PROMPT_LENGTH: int = 1000


class OutputFormat(str, Enum):
    """Supported 3D asset output formats."""

    OBJ = "obj"
    GLB = "glb"

    @classmethod
    def _missing_(cls, value: Any) -> "OutputFormat | None":
        if isinstance(value, str):
            normalized = value.strip().lower()
            for member in cls:
                if member.value == normalized:
                    return member
        return None


class GenerationRequest(BaseModel):
    """Input payload contract for initiating 3D asset generation."""

    prompt: str = Field(
        ...,
        min_length=MIN_PROMPT_LENGTH,
        max_length=MAX_PROMPT_LENGTH,
        description="Descriptive natural language prompt for 3D asset generation.",
        examples=["A low-poly medieval wooden shield with iron rim"],
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.GLB,
        description="Target 3D file format. Supported options: 'glb', 'obj'.",
        examples=[OutputFormat.GLB],
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate that the prompt is not empty or composed solely of whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Prompt cannot be empty or contain only whitespace.")
        if len(stripped) > MAX_PROMPT_LENGTH:
            raise ValueError(
                f"Prompt cannot exceed {MAX_PROMPT_LENGTH} characters."
            )
        return stripped
