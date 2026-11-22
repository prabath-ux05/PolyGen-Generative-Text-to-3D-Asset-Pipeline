
"""Tests for the multi-format mesh loader."""

import pytest
import trimesh

from mesh_processing.mesh_loader import load_mesh


def create_test_mesh():
    """Create a simple cube for testing."""
    return trimesh.creation.box()


def test_load_obj_file(tmp_path):
    """Test loading a valid OBJ file."""
    mesh = create_test_mesh()
    file_path = tmp_path / "cube.obj"
    mesh.export(file_path)

    result = load_mesh(file_path)

    assert result.metadata["file_format"] == "obj"
    assert result.metadata["vertex_count"] > 0
    assert result.metadata["face_count"] > 0
    assert isinstance(result.mesh, trimesh.Trimesh)


def test_load_glb_file(tmp_path):
    """Test loading a valid GLB file."""
    mesh = create_test_mesh()
    file_path = tmp_path / "cube.glb"
    mesh.export(file_path)

    result = load_mesh(file_path)

    assert result.metadata["file_format"] == "glb"
    assert result.metadata["vertex_count"] > 0
    assert result.metadata["face_count"] > 0


def test_file_not_found():
    """Test that a missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_mesh("missing_model.obj")


def test_unsupported_file_format(tmp_path):
    """Test that unsupported extensions are rejected."""
    file_path = tmp_path / "model.txt"
    file_path.write_text("not a 3D model")

    with pytest.raises(ValueError, match="Unsupported format"):
        load_mesh(file_path)


def test_empty_file(tmp_path):
    """Test that an empty mesh file is rejected."""
    file_path = tmp_path / "empty.obj"
    file_path.write_text("")

    with pytest.raises(ValueError, match="empty"):
        load_mesh(file_path)


def test_metadata_contains_mesh_dimensions(tmp_path):
    """Test that mesh metadata includes dimensions and bounds."""
    mesh = create_test_mesh()
    file_path = tmp_path / "cube.obj"
    mesh.export(file_path)

    result = load_mesh(file_path)

    assert len(result.metadata["dimensions"]) == 3
    assert len(result.metadata["bounds"]) == 2
    assert result.metadata["is_watertight"] is True



def test_load_gltf_file(tmp_path):
    """Test loading a valid GLTF file."""
    mesh = create_test_mesh()
    file_path = tmp_path / "cube.gltf"
    mesh.export(file_path)

    result = load_mesh(file_path)

    assert result.metadata["file_format"] == "gltf"
    assert result.metadata["vertex_count"] > 0
    assert result.metadata["face_count"] > 0
    assert isinstance(result.mesh, trimesh.Trimesh)



def test_scene_transformations_are_preserved(tmp_path):
    """Test that scene object positions are preserved when loading GLB."""
    scene = trimesh.Scene()

    box = trimesh.creation.box()
    transform = trimesh.transformations.translation_matrix([5, 0, 0])
    scene.add_geometry(box, transform=transform)

    file_path = tmp_path / "translated_scene.glb"
    scene.export(file_path)

    result = load_mesh(file_path)

    # The box should remain centered around x = 5, not x = 0.
    assert result.metadata["bounds"][0][0] == pytest.approx(4.5)
    assert result.metadata["bounds"][1][0] == pytest.approx(5.5)
