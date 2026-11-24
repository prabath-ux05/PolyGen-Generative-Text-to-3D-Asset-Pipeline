"""Tests for the end-to-end texturing pipeline."""

from PIL import Image
import trimesh

from texture_engine.pipeline import process_asset


def test_process_asset_completes_pipeline(tmp_path):
    # Create a sample mesh.
    mesh = trimesh.creation.box()
    mesh_path = tmp_path / "sample.obj"
    mesh.export(mesh_path)

    # Create a sample texture.
    texture_path = tmp_path / "texture.png"
    Image.new("RGB", (256, 256), (120, 80, 40)).save(texture_path)

    # Run the full pipeline.
    output_path = tmp_path / "output" / "textured_model.glb"

    report = process_asset(
        mesh_path=mesh_path,
        texture_path=texture_path,
        output_path=output_path,
    )

    # Validate the pipeline report.
    assert report["success"] is True
    assert report["input_mesh"]["file_format"] == "obj"
    assert report["texture_application"]["success"] is True
    assert report["final_uv_validation"]["is_valid"] is True
    assert report["export"]["verified"] is True
    assert output_path.exists()


def test_pipeline_rejects_missing_mesh(tmp_path):
    texture_path = tmp_path / "texture.png"
    Image.new("RGB", (64, 64), (100, 100, 100)).save(texture_path)

    missing_mesh = tmp_path / "missing.obj"

    output_path = tmp_path / "output.glb"

    try:
        process_asset(missing_mesh, texture_path, output_path)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Expected FileNotFoundError for missing mesh.")


def test_pipeline_rejects_invalid_texture(tmp_path):
    mesh_path = tmp_path / "sample.obj"
    trimesh.creation.box().export(mesh_path)

    invalid_texture = tmp_path / "invalid.png"
    invalid_texture.write_text("not an image")

    output_path = tmp_path / "output.glb"

    try:
        process_asset(mesh_path, invalid_texture, output_path)
    except (ValueError, RuntimeError):
        pass
    else:
        raise AssertionError("Expected an error for invalid texture.")