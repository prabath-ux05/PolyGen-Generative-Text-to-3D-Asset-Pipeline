"""End-to-end mesh texturing and export pipeline."""

from pathlib import Path

from mesh_processing.mesh_loader import load_mesh
from mesh_processing.mesh_inspector import inspect_mesh
from mesh_processing.mesh_exporter import export_mesh
from mesh_processing.uv_validator import validate_uv
from texture_engine.texture_applier import apply_texture


def process_asset(
    mesh_path: str | Path,
    texture_path: str | Path,
    output_path: str | Path,
    metallic_factor: float = 0.0,
    roughness_factor: float = 1.0,
) -> dict:
    """
    Process a mesh, apply a texture and PBR material, and export a GLB.

    Workflow:
        1. Load mesh
        2. Inspect mesh
        3. Validate original UV coordinates
        4. Apply texture and material
        5. Validate final UV coordinates
        6. Export GLB
        7. Return processing report
    """

    # Step 1: Load the input mesh.
    load_result = load_mesh(mesh_path)
    mesh = load_result.mesh

    # Step 2: Inspect the original mesh.
    mesh_report = inspect_mesh(mesh)

    # Step 3: Check existing UV coordinates.
    original_uv_report = validate_uv(mesh)

    # Step 4: Apply texture and PBR material.
    textured_mesh, texture_report = apply_texture(
        mesh=mesh,
        texture_path=texture_path,
        metallic_factor=metallic_factor,
        roughness_factor=roughness_factor,
    )

    # Step 5: Validate the final UV mapping.
    final_uv_report = validate_uv(textured_mesh)

    if not final_uv_report["is_valid"]:
        raise RuntimeError(
            "Final UV validation failed: "
            + "; ".join(final_uv_report["warnings"])
        )

    # Step 6: Export and verify the final model.
    export_report = export_mesh(
        mesh=textured_mesh,
        output_path=output_path,
    )

    # Step 7: Build a complete processing report.
    return {
        "success": True,
        "input_mesh": load_result.metadata,
        "mesh_inspection": mesh_report,
        "original_uv_validation": original_uv_report,
        "texture_application": texture_report,
        "final_uv_validation": final_uv_report,
        "export": export_report,
        "output_file": export_report["file_path"],
        "warnings": mesh_report["warnings"],
    }