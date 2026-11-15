"""Text-to-3D generation API endpoints."""

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.generation import GenerationRequest, ServiceUnavailableResponse

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
