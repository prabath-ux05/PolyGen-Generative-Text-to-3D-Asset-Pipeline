"""Service for managing the lifecycle of Text-to-3D generation jobs."""

import uuid
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from backend.app.schemas.generation import OutputFormat
from backend.app.schemas.generation_job import (
    GenerationJobResponse,
    GenerationJobStatus,
)


class JobNotFoundError(ValueError):
    """Raised when a requested generation job is not found."""

    pass


class InvalidJobTransitionError(ValueError):
    """Raised when an invalid lifecycle status transition is attempted."""

    pass


# Valid lifecycle state transition mapping
# pending -> processing -> completed / failed
VALID_TRANSITIONS: dict[GenerationJobStatus, set[GenerationJobStatus]] = {
    GenerationJobStatus.PENDING: {GenerationJobStatus.PROCESSING},
    GenerationJobStatus.PROCESSING: {
        GenerationJobStatus.COMPLETED,
        GenerationJobStatus.FAILED,
    },
    GenerationJobStatus.COMPLETED: set(),  # Terminal state
    GenerationJobStatus.FAILED: set(),     # Terminal state
}


class GenerationJobService:
    """In-memory service managing generation job creation, retrieval, and lifecycle transitions."""

    def __init__(self) -> None:
        self._jobs: dict[UUID, GenerationJobResponse] = {}

    def create_job(
        self,
        prompt: str,
        output_format: OutputFormat = OutputFormat.GLB,
    ) -> GenerationJobResponse:
        """Create and register a new generation job with status PENDING.

        Args:
            prompt: Text prompt describing the desired 3D asset.
            output_format: Target 3D file format (defaults to GLB).

        Returns:
            The created GenerationJobResponse object.
        """
        job_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        job = GenerationJobResponse(
            job_id=job_id,
            prompt=prompt,
            output_format=output_format,
            status=GenerationJobStatus.PENDING,
            created_at=now,
            updated_at=now,
            error_message=None,
        )

        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: UUID | str) -> GenerationJobResponse | None:
        """Retrieve a generation job by its UUID.

        Args:
            job_id: Unique UUID or UUID string of the job.

        Returns:
            The GenerationJobResponse if found, otherwise None.
        """
        parsed_id = self._parse_uuid(job_id)
        if parsed_id is None:
            return None
        return self._jobs.get(parsed_id)

    def update_job_status(
        self,
        job_id: UUID | str,
        new_status: GenerationJobStatus | str,
        error_message: str | None = None,
    ) -> GenerationJobResponse:
        """Update the status of an existing generation job according to lifecycle transition rules.

        Args:
            job_id: Unique UUID or UUID string of the job.
            new_status: The target GenerationJobStatus.
            error_message: Optional failure explanation if new_status is FAILED.

        Returns:
            The updated GenerationJobResponse.

        Raises:
            JobNotFoundError: If no job with the provided ID exists.
            InvalidJobTransitionError: If the status transition is not permitted.
        """
        parsed_id = self._parse_uuid(job_id)
        if parsed_id is None or parsed_id not in self._jobs:
            raise JobNotFoundError(f"Generation job with ID '{job_id}' not found.")

        # Ensure new_status is an instance of GenerationJobStatus
        if isinstance(new_status, str):
            new_status = GenerationJobStatus(new_status)

        current_job = self._jobs[parsed_id]
        current_status = current_job.status

        allowed_next = VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed_next:
            raise InvalidJobTransitionError(
                f"Cannot transition job '{parsed_id}' from '{current_status.value}' to '{new_status.value}'. "
                f"Allowed transitions from '{current_status.value}': {[s.value for s in allowed_next]}."
            )

        now = datetime.now(timezone.utc)
        resolved_error = (
            error_message if new_status == GenerationJobStatus.FAILED else None
        )

        updated_job = current_job.model_copy(
            update={
                "status": new_status,
                "updated_at": now,
                "error_message": resolved_error,
            }
        )

        self._jobs[parsed_id] = updated_job
        return updated_job

    def clear(self) -> None:
        """Clear all stored jobs (primarily for test cleanup)."""
        self._jobs.clear()

    @staticmethod
    def _parse_uuid(val: Any) -> UUID | None:
        """Safely parse input to UUID."""
        if isinstance(val, UUID):
            return val
        if isinstance(val, str):
            try:
                return UUID(val)
            except (ValueError, AttributeError):
                return None
        return None


# Global instance for shared use
generation_job_service = GenerationJobService()
