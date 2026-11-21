"""Text-to-3D generation API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.generation import (
    ErrorResponse,
    GenerationRequest,
    ServiceUnavailableResponse,
)
from backend.app.schemas.generation_job import (
    GenerationJobResponse,
    GenerationJobStatusUpdateRequest,
)
from backend.app.services.generation_job_service import (
    InvalidJobTransitionError,
    JobNotFoundError,
    generation_job_service,
)

router = APIRouter(prefix="/generations", tags=["generations"])


@router.post(
    "",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    response_model=ServiceUnavailableResponse,
    summary="Submit Text-to-3D generation request",
    description=(
        "Initial API endpoint foundation for Text-to-3D generation requests. "
        "Returns 503 Service Unavailable until the generation engine is integrated."
    ),
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ServiceUnavailableResponse,
            "description": "Generation engine is not yet integrated.",
        },
    },
)
@router.post(
    "/",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    response_model=ServiceUnavailableResponse,
    include_in_schema=False,
)
def create_generation(request: GenerationRequest) -> None:
    """Handle text-to-3D generation request.

    Validates request payload and informs the caller that the generation engine
    is not yet integrated into the pipeline.
    """
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Text-to-3D generation engine is not yet integrated.",
    )


@router.get(
    "/{job_id}",
    response_model=GenerationJobResponse,
    summary="Get generation job details",
    description="Retrieve the current status, progress, and metadata of a Text-to-3D generation job by its UUID.",
    responses={
        status.HTTP_200_OK: {
            "model": GenerationJobResponse,
            "description": "Generation job details successfully retrieved.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Generation job not found.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error (invalid UUID path parameter).",
        },
    },
)
def get_generation_job(job_id: UUID) -> GenerationJobResponse:
    """Retrieve details for a specific generation job by its UUID.

    Args:
        job_id: The UUID of the generation job.

    Returns:
        The GenerationJobResponse object if found.

    Raises:
        HTTPException: 404 if no job exists with the given ID.
    """
    job = generation_job_service.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job with ID '{job_id}' not found.",
        )
    return job


@router.patch(
    "/{job_id}/status",
    response_model=GenerationJobResponse,
    summary="Update generation job status",
    description="Update the lifecycle status of a Text-to-3D generation job according to valid transition rules.",
    responses={
        status.HTTP_200_OK: {
            "model": GenerationJobResponse,
            "description": "Generation job status successfully updated.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Generation job not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Invalid lifecycle state transition.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Validation error (invalid UUID or status value).",
        },
    },
)
def update_generation_job_status(
    job_id: UUID,
    request: GenerationJobStatusUpdateRequest,
) -> GenerationJobResponse:
    """Update the lifecycle status of an existing generation job.

    Args:
        job_id: The UUID of the generation job.
        request: Target status and optional error message.

    Returns:
        The updated GenerationJobResponse object.

    Raises:
        HTTPException: 404 if the job is not found.
        HTTPException: 409 if the lifecycle transition is invalid.
    """
    try:
        return generation_job_service.update_job_status(
            job_id=job_id,
            new_status=request.status,
            error_message=request.error_message,
        )
    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidJobTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
