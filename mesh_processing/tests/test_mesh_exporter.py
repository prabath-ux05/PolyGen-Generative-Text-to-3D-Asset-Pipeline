"""Tests for GLB mesh exporting."""

import pytest
import trimesh

from mesh_processing.mesh_exporter import export_mesh


def test_export_mesh_creates_valid_glb(tmp_path):
    mesh = trimesh.creation.box()
    output_path = tmp_path / "box.glb"

    report = export_mesh(mesh, output_path)

    assert report["success"] is True
    assert report["verified"] is True
    assert report["file_format"] == "glb"
    assert report["file_name"] == "box.glb"
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_exported_glb_can_be_reloaded(tmp_path):
    mesh = trimesh.creation.box()
    output_path = tmp_path / "reload_test.glb"

    export_mesh(mesh, output_path)

    loaded = trimesh.load(output_path, force="scene")

    assert isinstance(loaded, trimesh.Scene)
    assert len(loaded.geometry) > 0


def test_export_preserves_geometry(tmp_path):
    mesh = trimesh.creation.box()
    output_path = tmp_path / "geometry_test.glb"

    export_mesh(mesh, output_path)

    loaded = trimesh.load(output_path, force="scene")
    exported_mesh = loaded.to_geometry()

    assert len(exported_mesh.vertices) == len(mesh.vertices)
    assert len(exported_mesh.faces) == len(mesh.faces)


def test_export_creates_missing_output_directory(tmp_path):
    mesh = trimesh.creation.box()
    output_path = tmp_path / "nested" / "exports" / "model.glb"

    report = export_mesh(mesh, output_path)

    assert report["success"] is True
    assert output_path.exists()


def test_export_rejects_invalid_extension(tmp_path):
    mesh = trimesh.creation.box()
    output_path = tmp_path / "model.obj"

    with pytest.raises(ValueError, match="Only .glb export is supported"):
        export_mesh(mesh, output_path)


def test_export_rejects_empty_mesh(tmp_path):
    mesh = trimesh.Trimesh()
    output_path = tmp_path / "empty.glb"

    with pytest.raises(ValueError, match="Cannot export an empty mesh"):
        export_mesh(mesh, output_path)


def test_export_rejects_invalid_input_type(tmp_path):
    output_path = tmp_path / "invalid.glb"

    with pytest.raises(TypeError, match="Expected a trimesh.Trimesh object"):
        export_mesh("not_a_mesh", output_path)