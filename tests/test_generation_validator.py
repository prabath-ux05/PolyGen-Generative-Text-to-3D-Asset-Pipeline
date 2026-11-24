import numpy as np
import pytest
import trimesh

from ai_generation.generation_validator import (
    MeshValidator,
    MeshValidationError,
)


@pytest.fixture
def validator():
    return MeshValidator()


@pytest.fixture
def valid_mesh():
    return trimesh.creation.box()


def test_valid_box_mesh_passes(validator, valid_mesh):
    report = validator.validate(valid_mesh)

    assert report.valid is True
    assert report.errors == ()


def test_valid_mesh_report_has_counts(validator, valid_mesh):
    report = validator.validate(valid_mesh)

    assert report.vertex_count == len(valid_mesh.vertices)
    assert report.face_count == len(valid_mesh.faces)


def test_valid_box_is_watertight(validator, valid_mesh):
    report = validator.validate(valid_mesh)

    assert report.is_watertight is True


def test_non_mesh_input_fails(validator):
    report = validator.validate("not a mesh")

    assert report.valid is False
    assert "trimesh.Trimesh" in report.errors[0]


def test_empty_mesh_fails(validator):
    report = validator.validate(trimesh.Trimesh())

    assert report.valid is False
    assert "Mesh is empty" in report.errors


def test_empty_mesh_raises_error(validator):
    with pytest.raises(MeshValidationError):
        validator.validate_or_raise(trimesh.Trimesh())


def test_non_finite_vertices_are_detected():
    mesh = trimesh.creation.box()
    mesh.vertices[0] = [np.nan, 0, 0]

    report = MeshValidator().validate(mesh)

    assert report.valid is False
    assert any("non-finite" in error for error in report.errors)


def test_minimum_vertex_configuration():
    with pytest.raises(ValueError):
        MeshValidator(min_vertices=2)


def test_minimum_face_configuration():
    with pytest.raises(ValueError):
        MeshValidator(min_faces=0)


def test_open_mesh_is_warning_by_default():
    mesh = trimesh.creation.box()
    mesh.update_faces(np.arange(len(mesh.faces) - 1))

    report = MeshValidator().validate(mesh)

    assert report.valid is True
    assert any("watertight" in warning for warning in report.warnings)


def test_open_mesh_fails_in_strict_mode():
    mesh = trimesh.creation.box()
    mesh.update_faces(np.arange(len(mesh.faces) - 1))

    report = MeshValidator(
        require_watertight=True
    ).validate(mesh)

    assert report.valid is False
    assert any("watertight" in error for error in report.errors)


def test_disconnected_components_are_reported():
    first = trimesh.creation.box()
    second = trimesh.creation.box()
    second.apply_translation([3, 0, 0])

    combined = trimesh.util.concatenate([first, second])
    report = MeshValidator().validate(combined)

    assert report.valid is True
    assert any("disconnected components" in warning
               for warning in report.warnings)


def test_degenerate_faces_are_reported():
    mesh = trimesh.Trimesh(
        vertices=[
            [0, 0, 0],
            [1, 0, 0],
            [2, 0, 0],
        ],
        faces=[[0, 1, 2]],
        process=False,
    )

    report = MeshValidator().validate(mesh)

    assert any("degenerate" in warning for warning in report.warnings)


def test_report_can_be_converted_to_dictionary(validator, valid_mesh):
    data = validator.validate(valid_mesh).to_dict()

    assert "valid" in data
    assert "errors" in data
    assert "warnings" in data
    assert "is_watertight" in data


def test_validator_returns_report(validator, valid_mesh):
    report = validator.validate(valid_mesh)

    assert report.valid is True
    assert report.vertex_count > 0
    assert report.face_count > 0
