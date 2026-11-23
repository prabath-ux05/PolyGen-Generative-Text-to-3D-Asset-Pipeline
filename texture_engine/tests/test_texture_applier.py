"""Tests for texture and mesh integration."""

import numpy as np
import pytest
import trimesh
from PIL import Image

from texture_engine.texture_applier import apply_texture


@pytest.fixture
def texture_file(tmp_path):
    """Create a valid temporary texture."""
    path = tmp_path / "test_texture.png"
    Image.new("RGB", (64, 64), "red").save(path)
    return path


def test_apply_texture_to_mesh(texture_file):
    mesh = trimesh.creation.box()

    textured_mesh, report = apply_texture(mesh, texture_file)

    assert isinstance(textured_mesh, trimesh.Trimesh)
    assert report["success"] is True
    assert report["uv_valid"] is True
    assert report["uv_generated"] is True
    assert report["texture_file"] == "test_texture.png"


def test_material_is_applied(texture_file):
    mesh = trimesh.creation.box()

    textured_mesh, report = apply_texture(
        mesh,
        texture_file,
        metallic_factor=0.5,
        roughness_factor=0.3,
    )

    material = textured_mesh.visual.material

    assert material.name == "PolyGen_Textured_Material"
    assert material.metallicFactor == 0.5
    assert material.roughnessFactor == 0.3


def test_uv_is_generated_when_missing(texture_file):
    mesh = trimesh.creation.box()

    textured_mesh, report = apply_texture(mesh, texture_file)

    assert report["uv_generated"] is True
    assert textured_mesh.visual.uv is not None


def test_existing_valid_uv_is_preserved(texture_file):
    mesh = trimesh.creation.box()

    original_uv = np.zeros((len(mesh.vertices), 2))
    original_uv[:, 0] = np.linspace(0, 1, len(mesh.vertices))

    mesh.visual = trimesh.visual.TextureVisuals(uv=original_uv.copy())

    textured_mesh, report = apply_texture(mesh, texture_file)

    assert report["uv_generated"] is False
    assert np.allclose(textured_mesh.visual.uv, original_uv)


def test_original_mesh_is_not_modified(texture_file):
    mesh = trimesh.creation.box()

    original_vertices = mesh.vertices.copy()
    original_visual = mesh.visual

    apply_texture(mesh, texture_file)

    assert np.array_equal(mesh.vertices, original_vertices)
    assert mesh.visual is original_visual


def test_invalid_texture_is_rejected(tmp_path):
    mesh = trimesh.creation.box()
    invalid_texture = tmp_path / "broken.png"
    invalid_texture.write_text("not an image")

    with pytest.raises(ValueError, match="Invalid texture"):
        apply_texture(mesh, invalid_texture)


def test_missing_texture_is_rejected(tmp_path):
    mesh = trimesh.creation.box()
    missing_texture = tmp_path / "missing.png"

    with pytest.raises(ValueError, match="Invalid texture"):
        apply_texture(mesh, missing_texture)


def test_invalid_mesh_input_is_rejected(texture_file):
    with pytest.raises(TypeError, match="Trimesh"):
        apply_texture("not a mesh", texture_file)


def test_empty_mesh_is_rejected(texture_file):
    empty_mesh = trimesh.Trimesh(
        vertices=np.empty((0, 3)),
        faces=np.empty((0, 3), dtype=int),
    )

    with pytest.raises(ValueError, match="empty mesh"):
        apply_texture(empty_mesh, texture_file)