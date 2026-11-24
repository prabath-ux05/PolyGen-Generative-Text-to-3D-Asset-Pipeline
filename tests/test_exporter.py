import numpy as np
import pytest
import trimesh

from ai_generation.exporter import MeshExporter, MeshExportError


@pytest.fixture
def exporter(tmp_path):
    return MeshExporter(output_dir=tmp_path / "generated")


@pytest.fixture
def valid_mesh():
    return trimesh.creation.box()


def test_valid_mesh_is_accepted(exporter, valid_mesh):
    assert exporter.validate_mesh(valid_mesh) is True


def test_obj_export(exporter, valid_mesh):
    result = exporter.export(valid_mesh, "obj")
    assert result.exists()
    assert result.suffix == ".obj"
    assert result.stat().st_size > 0


def test_glb_export(exporter, valid_mesh):
    result = exporter.export(valid_mesh, "glb")
    assert result.exists()
    assert result.suffix == ".glb"
    assert result.stat().st_size > 0


def test_custom_filename(exporter, valid_mesh):
    result = exporter.export(
        valid_mesh, "obj", filename="my_model"
    )
    assert result.name == "my_model.obj"


def test_unique_filenames(exporter, valid_mesh):
    first = exporter.export(
        valid_mesh, "obj", filename="chair"
    )
    second = exporter.export(
        valid_mesh, "obj", filename="chair"
    )
    assert first != second
    assert first.exists()
    assert second.exists()


def test_empty_mesh_is_rejected(exporter):
    empty_mesh = trimesh.Trimesh()
    with pytest.raises(MeshExportError):
        exporter.validate_mesh(empty_mesh)


def test_non_mesh_input_is_rejected(exporter):
    with pytest.raises(MeshExportError):
        exporter.validate_mesh("not a mesh")


def test_unsupported_format_is_rejected(exporter, valid_mesh):
    with pytest.raises(MeshExportError):
        exporter.export(valid_mesh, "stl")


def test_format_is_case_insensitive(exporter, valid_mesh):
    result = exporter.export(valid_mesh, "OBJ")
    assert result.suffix == ".obj"


def test_output_directory_is_created(tmp_path, valid_mesh):
    output_dir = tmp_path / "new_folder" / "models"
    exporter = MeshExporter(output_dir=output_dir)

    result = exporter.export(valid_mesh, "obj")

    assert output_dir.exists()
    assert result.exists()


def test_invalid_filename_is_rejected(exporter, valid_mesh):
    with pytest.raises(MeshExportError):
        exporter.export(valid_mesh, "obj", filename="...")


def test_exported_obj_can_be_reloaded(exporter, valid_mesh):
    result = exporter.export(valid_mesh, "obj")
    loaded_mesh = trimesh.load(result, force="mesh")

    assert isinstance(loaded_mesh, trimesh.Trimesh)
    assert not loaded_mesh.is_empty


def test_exported_glb_can_be_reloaded(exporter, valid_mesh):
    result = exporter.export(valid_mesh, "glb")
    loaded_mesh = trimesh.load(result, force="mesh")

    assert isinstance(loaded_mesh, trimesh.Trimesh)
    assert not loaded_mesh.is_empty
