"""Unit tests for GenerationJobService lifecycle management."""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.schemas.generation import OutputFormat
from backend.app.schemas.generation_job import (
    GenerationJobResponse,
    GenerationJobStatus,
)
from backend.app.services.generation_job_service import (
    GenerationJobService,
    InvalidJobTransitionError,
    JobNotFoundError,
)


@pytest.fixture
def service():
    """Fixture providing an isolated GenerationJobService instance for each test."""
    return GenerationJobService()


def test_job_creation(service):
    """Verify job creation generates a UUID, PENDING status, and valid timestamps."""
    prompt = "A high-detail sci-fi rover"
    job = service.create_job(prompt=prompt, output_format=OutputFormat.GLB)

    assert isinstance(job, GenerationJobResponse)
    assert isinstance(job.job_id, uuid.UUID)
    assert job.prompt == prompt
    assert job.output_format == OutputFormat.GLB
    assert job.status == GenerationJobStatus.PENDING
    assert job.error_message is None
    assert job.created_at.tzinfo == timezone.utc
    assert job.updated_at.tzinfo == timezone.utc
    assert job.created_at == job.updated_at


def test_job_creation_default_output_format(service):
    """Verify job creation defaults output_format to GLB."""
    job = service.create_job(prompt="A simple wooden crate")
    assert job.output_format == OutputFormat.GLB


def test_job_creation_with_obj_format(service):
    """Verify job creation with OBJ format."""
    job = service.create_job(prompt="A stone pillar", output_format=OutputFormat.OBJ)
    assert job.output_format == OutputFormat.OBJ


def test_job_retrieval_by_id(service):
    """Verify retrieval by UUID and string UUID representation."""
    job = service.create_job(prompt="A medieval sword")

    # Retrieval using UUID object
    retrieved = service.get_job(job.job_id)
    assert retrieved is not None
    assert retrieved.job_id == job.job_id
    assert retrieved.prompt == "A medieval sword"

    # Retrieval using string representation
    retrieved_str = service.get_job(str(job.job_id))
    assert retrieved_str is not None
    assert retrieved_str.job_id == job.job_id


def test_unknown_job_id_retrieval_returns_none(service):
    """Verify retrieving an unknown job returns None."""
    random_id = uuid.uuid4()
    assert service.get_job(random_id) is None
    assert service.get_job(str(random_id)) is None
    assert service.get_job("invalid-uuid-string") is None


def test_unknown_job_id_update_raises_error(service):
    """Verify updating a non-existent job raises JobNotFoundError."""
    random_id = uuid.uuid4()
    with pytest.raises(JobNotFoundError) as exc_info:
        service.update_job_status(random_id, GenerationJobStatus.PROCESSING)
    assert "not found" in str(exc_info.value)

    with pytest.raises(JobNotFoundError):
        service.update_job_status("non-existent-uuid", GenerationJobStatus.PROCESSING)


def test_valid_transition_pending_to_processing(service):
    """Verify valid transition from PENDING to PROCESSING updates status and timestamp."""
    job = service.create_job(prompt="A potion vial")
    original_updated_at = job.updated_at

    updated = service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)

    assert updated.status == GenerationJobStatus.PROCESSING
    assert updated.updated_at >= original_updated_at
    assert updated.error_message is None

    # Verify retrieval reflects new status
    fetched = service.get_job(job.job_id)
    assert fetched.status == GenerationJobStatus.PROCESSING


def test_valid_transition_processing_to_completed(service):
    """Verify valid transition from PROCESSING to COMPLETED."""
    job = service.create_job(prompt="A fantasy castle")
    service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)

    completed = service.update_job_status(job.job_id, GenerationJobStatus.COMPLETED)
    assert completed.status == GenerationJobStatus.COMPLETED
    assert completed.error_message is None


def test_valid_transition_processing_to_failed(service):
    """Verify valid transition from PROCESSING to FAILED with error message."""
    job = service.create_job(prompt="A complex dragon statue")
    service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)

    error_msg = "CUDA out of memory during mesh decimation."
    failed = service.update_job_status(
        job.job_id,
        GenerationJobStatus.FAILED,
        error_message=error_msg,
    )
    assert failed.status == GenerationJobStatus.FAILED
    assert failed.error_message == error_msg


def test_invalid_transitions_from_pending(service):
    """Verify invalid direct transitions from PENDING to COMPLETED or FAILED are rejected."""
    job = service.create_job(prompt="A low-poly tree")

    # Cannot skip directly to completed
    with pytest.raises(InvalidJobTransitionError) as exc_info:
        service.update_job_status(job.job_id, GenerationJobStatus.COMPLETED)
    assert "Cannot transition" in str(exc_info.value)

    # Cannot skip directly to failed
    with pytest.raises(InvalidJobTransitionError):
        service.update_job_status(job.job_id, GenerationJobStatus.FAILED)

    # Cannot re-transition to pending
    with pytest.raises(InvalidJobTransitionError):
        service.update_job_status(job.job_id, GenerationJobStatus.PENDING)


def test_invalid_transitions_from_processing(service):
    """Verify invalid transition from PROCESSING back to PENDING is rejected."""
    job = service.create_job(prompt="A treasure chest")
    service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)

    with pytest.raises(InvalidJobTransitionError):
        service.update_job_status(job.job_id, GenerationJobStatus.PENDING)

    with pytest.raises(InvalidJobTransitionError):
        service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)


def test_terminal_state_completed_rejects_all_transitions(service):
    """Verify COMPLETED is a terminal state that rejects any subsequent transition."""
    job = service.create_job(prompt="A crystal orb")
    service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)
    service.update_job_status(job.job_id, GenerationJobStatus.COMPLETED)

    for target_status in [
        GenerationJobStatus.PENDING,
        GenerationJobStatus.PROCESSING,
        GenerationJobStatus.COMPLETED,
        GenerationJobStatus.FAILED,
    ]:
        with pytest.raises(InvalidJobTransitionError) as exc_info:
            service.update_job_status(job.job_id, target_status)
        assert "Cannot transition" in str(exc_info.value)


def test_terminal_state_failed_rejects_all_transitions(service):
    """Verify FAILED is a terminal state that rejects any subsequent transition."""
    job = service.create_job(prompt="An alien spaceship")
    service.update_job_status(job.job_id, GenerationJobStatus.PROCESSING)
    service.update_job_status(job.job_id, GenerationJobStatus.FAILED, error_message="Engine failed")

    for target_status in [
        GenerationJobStatus.PENDING,
        GenerationJobStatus.PROCESSING,
        GenerationJobStatus.COMPLETED,
        GenerationJobStatus.FAILED,
    ]:
        with pytest.raises(InvalidJobTransitionError) as exc_info:
            service.update_job_status(job.job_id, target_status)
        assert "Cannot transition" in str(exc_info.value)


def test_service_clear(service):
    """Verify service clear removes all in-memory jobs."""
    job1 = service.create_job(prompt="Job 1")
    job2 = service.create_job(prompt="Job 2")

    assert service.get_job(job1.job_id) is not None
    assert service.get_job(job2.job_id) is not None

    service.clear()

    assert service.get_job(job1.job_id) is None
    assert service.get_job(job2.job_id) is None
