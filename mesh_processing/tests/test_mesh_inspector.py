
"""Tests for mesh inspection and quality reporting."""

import json

import pytest
import trimesh

from mesh_processing.mesh_inspector import (
    inspect_mesh,
    save_inspection_report,
)


def test_inspect_valid_cube():
    """A normal cube should pass basic quality checks."""
    mesh = trimesh.creation.box()

    report = inspect_mesh(mesh)

    assert report["vertex_count"] == 8
    assert report["face_count"] == 12
    assert report["is_watertight"] is True
    assert report["is_winding_consistent"] is True
    assert report["surface_area"] == pytest.approx(6.0)
    assert report["volume"] == pytest.approx(1.0)
    assert report["quality_status"] == "good"
    assert report["warnings"] == []


def test_inspect_mesh_with_holes():
    """An open mesh should generate a watertightness warning."""
    mesh = trimesh.creation.box()

    # Remove one face to create an opening.
    mesh.update_faces(
        [i != 0 for i in range(len(mesh.faces))]
    )
    mesh.remove_unreferenced_vertices()

    report = inspect_mesh(mesh)

    assert report["is_watertight"] is False
    assert report["volume"] is None
    assert report["quality_status"] == "warning"
    assert any("watertight" in warning for warning in report["warnings"])


def test_inspect_empty_mesh():
    """An empty mesh should be rejected."""
    mesh = trimesh.Trimesh()

    with pytest.raises(ValueError, match="empty"):
        inspect_mesh(mesh)


def test_inspect_invalid_input():
    """Non-mesh input should be rejected."""
    with pytest.raises(TypeError, match="Trimesh"):
        inspect_mesh("not a mesh")


def test_report_contains_expected_fields():
    """Check that the inspection report has all required fields."""
    mesh = trimesh.creation.box()

    report = inspect_mesh(mesh)

    expected_fields = {
        "vertex_count",
        "face_count",
        "dimensions",
        "bounds",
        "surface_area",
        "volume",
        "is_watertight",
        "is_winding_consistent",
        "degenerate_face_count",
        "quality_status",
        "warnings",
    }

    assert expected_fields.issubset(report.keys())


def test_save_inspection_report_as_json(tmp_path):
    """The inspection report should be saved as valid JSON."""
    mesh = trimesh.creation.box()
    report = inspect_mesh(mesh)

    output_path = tmp_path / "reports" / "cube_report.json"

    saved_path = save_inspection_report(report, output_path)

    assert saved_path.exists()

    with saved_path.open("r", encoding="utf-8") as file:
        loaded_report = json.load(file)

    assert loaded_report["vertex_count"] == 8
    assert loaded_report["quality_status"] == "good"
