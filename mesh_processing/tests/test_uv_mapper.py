"""Tests for UV coordinate generation."""

import numpy as np
import pytest
import trimesh

from mesh_processing.uv_mapper import generate_uv


def test_generate_uv_for_box():
    mesh = trimesh.creation.box()

    mapped_mesh = generate_uv(mesh)

    uv = mapped_mesh.visual.uv

    assert uv is not None
    assert uv.shape == (len(mesh.vertices), 2)
    assert np.all(uv >= 0)
    assert np.all(uv <= 1)


def test_generated_uv_coordinates_are_normalized():
    mesh = trimesh.creation.box(extents=[2, 4, 6])

    mapped_mesh = generate_uv(mesh)
    uv = mapped_mesh.visual.uv

    assert np.allclose(uv.min(axis=0), [0, 0])
    assert np.allclose(uv.max(axis=0), [1, 1])


def test_original_mesh_is_not_modified():
    mesh = trimesh.creation.box()

    original_visual = mesh.visual
    original_uv = getattr(mesh.visual, "uv", None)

    mapped_mesh = generate_uv(mesh)

    assert mapped_mesh is not mesh
    assert mesh.visual is original_visual
    assert getattr(mesh.visual, "uv", None) is original_uv


def test_generate_uv_for_flat_mesh():
    mesh = trimesh.creation.box(extents=[2, 2, 0])

    mapped_mesh = generate_uv(mesh)
    uv = mapped_mesh.visual.uv

    assert uv is not None
    assert np.isfinite(uv).all()
    assert np.all(uv >= 0)
    assert np.all(uv <= 1)


def test_generate_uv_for_empty_mesh():
    mesh = trimesh.Trimesh(
        vertices=np.empty((0, 3)),
        faces=np.empty((0, 3), dtype=int),
    )

    with pytest.raises(ValueError, match="empty mesh"):
        generate_uv(mesh)


def test_generate_uv_with_invalid_input():
    with pytest.raises(TypeError, match="Trimesh"):
        generate_uv("not a mesh")


def test_generate_uv_with_non_finite_vertices():
    mesh = trimesh.creation.box()
    mesh.vertices[0] = [np.nan, 0, 0]

    with pytest.raises(ValueError, match="non-finite"):
        generate_uv(mesh)