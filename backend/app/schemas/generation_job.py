"""Pydantic schemas for text-to-3D generation job management."""

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field, field_validator

from backend.app.schemas.generation import (
    MAX_PROMPT_LENGTH,
    MIN_PROMPT_LENGTH,
    OutputFormat,
)


class GenerationJobStatus(str, Enum):
    """Lifecycle status of a 3D asset generation job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def _missing_(cls, value: Any) -> "GenerationJobStatus | None":
        if isinstance(value, str):
            normalized = value.strip().lower()
            for member in cls:
                if member.value == normalized:
                    return member
        return None


class GenerationJobResponse(BaseModel):
    """Standardized representation of a Text-to-3D generation job."""

    job_id: UUID = Field(
        ...,
        description="Unique identifier for the generation job.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    prompt: str = Field(
        ...,
        min_length=MIN_PROMPT_LENGTH,
        max_length=MAX_PROMPT_LENGTH,
        description="Original text prompt used for 3D asset generation.",
        examples=["A low-poly medieval wooden shield with iron rim"],
    )
    output_format: OutputFormat = Field(
        ...,
        description="Target 3D asset format (e.g., glb, obj).",
        examples=[OutputFormat.GLB],
    )
    status: GenerationJobStatus = Field(
        ...,
        description="Current lifecycle status of the generation job.",
        examples=[GenerationJobStatus.PENDING],
    )
    created_at: AwareDatetime = Field(
        ...,
        description="Timestamp when the job was created (timezone-aware).",
    )
    updated_at: AwareDatetime = Field(
        ...,
        description="Timestamp when the job was last updated (timezone-aware).",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message detailing the failure reason if the job status is failed.",
        examples=["Generation timed out during mesh synthesis."],
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
