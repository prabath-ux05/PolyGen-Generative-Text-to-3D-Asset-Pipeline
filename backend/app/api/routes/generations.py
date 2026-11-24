"""Text-to-3D generation API endpoints."""

from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.responses import FileResponse

from backend.app.core.config import get_pipeline_adapter
from backend.app.schemas.generation import (
    ErrorResponse,
    GenerationRequest,
    OutputFormat,
    ServiceUnavailableResponse,
)
from backend.app.schemas.generation_job import (
    GenerationJobResponse,
    GenerationJobStatus,
    GenerationJobStatusUpdateRequest,
)
from backend.app.services.generation_job_service import (
    InvalidJobTransitionError,
    JobNotFoundError,
    generation_job_service,
)
from backend.app.services.pipeline_orchestrator import pipeline_orchestrator

router = APIRouter(prefix="/generations", tags=["generations"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=GenerationJobResponse,
    summary="Submit Text-to-3D generation request",
    description=(
        "Submit a Text-to-3D generation request. Returns 202 Accepted when a generation "
        "adapter is active, or 503 Service Unavailable when the engine is unintegrated."
    ),
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": GenerationJobResponse,
            "description": "Generation job created and queued for processing.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ServiceUnavailableResponse,
            "description": "Generation engine is not yet integrated or format is unsupported.",
        },
    },
)
@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=GenerationJobResponse,
    include_in_schema=False,
)
def create_generation(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    adapter: str = Depends(get_pipeline_adapter),
) -> GenerationJobResponse:
    """Handle text-to-3D generation request.

    If the generation engine adapter is 'none' or format is OBJ, informs caller that
    the engine is not yet integrated. Otherwise, creates a job in PENDING state and
    queues background orchestration.
    """
    if adapter == "none":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-3D generation engine is not yet integrated.",
        )

    # In Stage 2, only GLB is supported for textured pipeline output
    if request.output_format == OutputFormat.OBJ:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-3D generation engine is not yet integrated for OBJ output format.",
        )

    # 1. Create job with PENDING status
    job = generation_job_service.create_job(
        prompt=request.prompt,
        output_format=request.output_format,
    )

    # 2. Queue background pipeline execution
    background_tasks.add_task(
        pipeline_orchestrator.run_pipeline,
        job_id=job.job_id,
        prompt=job.prompt,
        output_format=job.output_format,
        adapter_name=adapter,
    )

    response.status_code = status.HTTP_202_ACCEPTED
    return job


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
        request: Target status, optional error message, and optional model_url.

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
            model_url=request.model_url,
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


@router.get(
    "/{job_id}/asset",
    summary="Download generated 3D asset",
    description="Stream the generated 3D asset file (GLB) for a completed generation job.",
    responses={
        status.HTTP_200_OK: {
            "description": "3D asset file stream (model/gltf-binary).",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Job or asset file not found.",
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Asset is not ready or generation failed.",
        },
    },
)
@router.get(
    "/{job_id}/download",
    include_in_schema=False,
)
def get_generation_asset(job_id: UUID) -> FileResponse:
    """Serve the generated GLB asset file securely, preventing directory traversal.

    Args:
        job_id: The UUID of the generation job.

    Returns:
        FileResponse containing the binary 3D asset.
    """
    job = generation_job_service.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job with ID '{job_id}' not found.",
        )

    if job.status == GenerationJobStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Generation job '{job_id}' failed: {job.error_message or 'Unknown error'}",
        )

    if job.status != GenerationJobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asset for generation job '{job_id}' is not ready (current status: '{job.status.value}').",
        )

    base_dir = pipeline_orchestrator.output_dir.resolve()
    target_file = (base_dir / f"{job_id}.glb").resolve()

    # Directory traversal prevention
    try:
        target_file.relative_to(base_dir)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Invalid file path.",
        )

    if not target_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset file for job '{job_id}' not found on disk.",
        )

    return FileResponse(
        path=str(target_file),
        media_type="model/gltf-binary",
        filename=f"{job_id}.glb",
        headers={"Access-Control-Allow-Origin": "*"},
    )
