"""Unit tests for GenerationJobResponse and GenerationJobStatus schemas."""

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

# Ensure root directory is on sys.path for direct pytest invocation
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.schemas.generation import OutputFormat
from backend.app.schemas.generation_job import (
    GenerationJobResponse,
    GenerationJobStatus,
)


@pytest.fixture
def base_job_data():
    """Fixture providing valid baseline parameters for a generation job."""
    now = datetime.now(timezone.utc)
    return {
        "job_id": uuid.uuid4(),
        "prompt": "A medieval fantasy castle tower",
        "output_format": OutputFormat.GLB,
        "status": GenerationJobStatus.PENDING,
        "created_at": now,
        "updated_at": now,
    }


def test_valid_pending_job_response(base_job_data):
    """Test 1: Verify valid pending job response."""
    base_job_data["status"] = GenerationJobStatus.PENDING
    job = GenerationJobResponse(**base_job_data)

    assert job.status == GenerationJobStatus.PENDING
    assert job.status.value == "pending"
    assert job.error_message is None
    assert job.prompt == "A medieval fantasy castle tower"
    assert job.output_format == OutputFormat.GLB


def test_valid_processing_job_response(base_job_data):
    """Test 2: Verify valid processing job response."""
    base_job_data["status"] = GenerationJobStatus.PROCESSING
    job = GenerationJobResponse(**base_job_data)

    assert job.status == GenerationJobStatus.PROCESSING
    assert job.status.value == "processing"
    assert job.error_message is None


def test_valid_completed_job_response(base_job_data):
    """Test 3: Verify valid completed job response."""
    base_job_data["status"] = GenerationJobStatus.COMPLETED
    job = GenerationJobResponse(**base_job_data)

    assert job.status == GenerationJobStatus.COMPLETED
    assert job.status.value == "completed"
    assert job.error_message is None


def test_valid_failed_job_response(base_job_data):
    """Test 4: Verify valid failed job response with error message."""
    base_job_data["status"] = GenerationJobStatus.FAILED
    base_job_data["error_message"] = "GPU out of memory during mesh synthesis."
    job = GenerationJobResponse(**base_job_data)

    assert job.status == GenerationJobStatus.FAILED
    assert job.status.value == "failed"
    assert job.error_message == "GPU out of memory during mesh synthesis."


def test_uuid_validation(base_job_data):
    """Test 5: Verify UUID parsing and validation."""
    # Valid UUID string format
    uuid_str = "550e8400-e29b-41d4-a716-446655440000"
    base_job_data["job_id"] = uuid_str
    job = GenerationJobResponse(**base_job_data)
    assert job.job_id == uuid.UUID(uuid_str)

    # Invalid UUID string
    base_job_data["job_id"] = "not-a-valid-uuid"
    with pytest.raises(ValidationError) as exc_info:
        GenerationJobResponse(**base_job_data)
    assert any("job_id" in err["loc"] for err in exc_info.value.errors())

    # Invalid UUID type
    base_job_data["job_id"] = 12345
    with pytest.raises(ValidationError) as exc_info:
        GenerationJobResponse(**base_job_data)
    assert any("job_id" in err["loc"] for err in exc_info.value.errors())


def test_invalid_job_status_rejection(base_job_data):
    """Test 6: Verify that invalid status values are rejected."""
    invalid_statuses = ["queued", "running", "cancelled", "unknown", ""]
    for status in invalid_statuses:
        base_job_data["status"] = status
        with pytest.raises(ValidationError) as exc_info:
            GenerationJobResponse(**base_job_data)
        assert any("status" in err["loc"] for err in exc_info.value.errors())


def test_invalid_output_format_rejection(base_job_data):
    """Test 7: Verify that invalid output formats are rejected."""
    invalid_formats = ["stl", "fbx", "blend", "ply", "invalid"]
    for fmt in invalid_formats:
        base_job_data["output_format"] = fmt
        with pytest.raises(ValidationError) as exc_info:
            GenerationJobResponse(**base_job_data)
        assert any("output_format" in err["loc"] for err in exc_info.value.errors())

    # Ensure valid formats are accepted
    for valid_fmt in ["obj", "glb", "OBJ", "GLB"]:
        base_job_data["output_format"] = valid_fmt
        job = GenerationJobResponse(**base_job_data)
        assert job.output_format in (OutputFormat.OBJ, OutputFormat.GLB)


def test_optional_error_message_behavior(base_job_data):
    """Test 8: Verify optional error_message default and explicit values."""
    # Default when error_message is not provided
    base_job_data.pop("error_message", None)
    job_default = GenerationJobResponse(**base_job_data)
    assert job_default.error_message is None

    # Explicit None
    base_job_data["error_message"] = None
    job_none = GenerationJobResponse(**base_job_data)
    assert job_none.error_message is None

    # Explicit string
    base_job_data["error_message"] = "Pipeline stage failed"
    job_str = GenerationJobResponse(**base_job_data)
    assert job_str.error_message == "Pipeline stage failed"


def test_timezone_aware_timestamp_validation(base_job_data):
    """Test 9: Verify timezone-aware datetime validation."""
    # Aware datetime (UTC) succeeds
    aware_dt = datetime.now(timezone.utc)
    base_job_data["created_at"] = aware_dt
    base_job_data["updated_at"] = aware_dt
    job = GenerationJobResponse(**base_job_data)
    assert job.created_at.tzinfo is not None
    assert job.updated_at.tzinfo is not None

    # Aware ISO string succeeds
    base_job_data["created_at"] = "2026-11-16T10:00:00Z"
    base_job_data["updated_at"] = "2026-11-16T10:05:00+00:00"
    job_iso = GenerationJobResponse(**base_job_data)
    assert job_iso.created_at.tzinfo is not None
    assert job_iso.updated_at.tzinfo is not None

    # Naive datetime (without tzinfo) fails
    naive_dt = datetime.now()
    base_job_data["created_at"] = naive_dt
    with pytest.raises(ValidationError) as exc_info:
        GenerationJobResponse(**base_job_data)
    assert any("created_at" in err["loc"] for err in exc_info.value.errors())

    # Naive ISO string fails
    base_job_data["created_at"] = aware_dt
    base_job_data["updated_at"] = "2026-11-16T10:00:00"
    with pytest.raises(ValidationError) as exc_info:
        GenerationJobResponse(**base_job_data)
    assert any("updated_at" in err["loc"] for err in exc_info.value.errors())
