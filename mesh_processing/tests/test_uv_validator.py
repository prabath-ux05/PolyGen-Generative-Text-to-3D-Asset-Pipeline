
"""Tests for UV coordinate validation."""

import numpy as np
import pytest
import trimesh

from mesh_processing.uv_validator import validate_uv


def create_mesh_with_uv():
    """Create a cube with valid UV coordinates."""
    mesh = trimesh.creation.box()

    # Assign one UV coordinate to each vertex.
    uv = np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [0.25, 0.25],
        [0.75, 0.25],
        [0.75, 0.75],
        [0.25, 0.75],
    ])

    mesh.visual = trimesh.visual.TextureVisuals(uv=uv)

    return mesh


def test_valid_uv_coordinates():
    """A mesh with valid UV coordinates should pass."""
    mesh = create_mesh_with_uv()

    report = validate_uv(mesh)

    assert report["has_uv"] is True
    assert report["is_valid"] is True
    assert report["uv_count"] == len(mesh.vertices)
    assert report["quality_status"] == "good"
    assert report["warnings"] == []


def test_missing_uv_coordinates():
    """A mesh without UV coordinates should fail validation."""
    mesh = trimesh.creation.box()

    report = validate_uv(mesh)

    assert report["has_uv"] is False
    assert report["is_valid"] is False
    assert report["quality_status"] == "warning"
    assert any("does not contain UV" in warning
               for warning in report["warnings"])


def test_uv_outside_valid_range():
    """UV values outside 0 to 1 should generate a warning."""
    mesh = create_mesh_with_uv()
    uv = mesh.visual.uv.copy()
    uv[0] = [-0.5, 1.5]

    mesh.visual = trimesh.visual.TextureVisuals(uv=uv)

    report = validate_uv(mesh)

    assert report["is_valid"] is False
    assert any("outside" in warning for warning in report["warnings"])


def test_uv_with_non_finite_values():
    """NaN or infinite UV values should be rejected."""
    mesh = create_mesh_with_uv()
    uv = mesh.visual.uv.copy()
    uv[0] = [np.nan, 0.5]

    mesh.visual = trimesh.visual.TextureVisuals(uv=uv)

    report = validate_uv(mesh)

    assert report["is_valid"] is False
    assert any("non-finite" in warning for warning in report["warnings"])


def test_invalid_mesh_input():
    """Non-mesh input should raise TypeError."""
    with pytest.raises(TypeError, match="Trimesh"):
        validate_uv("invalid mesh")


def test_empty_mesh():
    """An empty mesh should raise ValueError."""
    mesh = trimesh.Trimesh()

    with pytest.raises(ValueError, match="empty"):
        validate_uv(mesh)
