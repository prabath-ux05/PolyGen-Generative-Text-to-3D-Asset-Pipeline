"""Apply validated textures and PBR materials to 3D meshes."""

from pathlib import Path

from PIL import Image
import trimesh

from mesh_processing.uv_mapper import generate_uv
from mesh_processing.uv_validator import validate_uv
from texture_engine.material_builder import build_pbr_material
from texture_engine.texture_validator import validate_texture


def apply_texture(
    mesh: trimesh.Trimesh,
    texture_path: str | Path,
    name: str = "PolyGen_Textured_Material",
    metallic_factor: float = 0.0,
    roughness_factor: float = 1.0,
) -> tuple[trimesh.Trimesh, dict]:
    """
    Apply a validated texture and PBR material to a mesh.

    Generates UV coordinates if the mesh does not already contain them.
    The original mesh is not modified.

    Returns:
        A textured mesh and an integration report.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("Expected a trimesh.Trimesh object.")

    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("Cannot texture an empty mesh.")

    # Validate the texture before attempting to load it.
    texture_report = validate_texture(texture_path)

    if not texture_report["is_valid"]:
        raise ValueError(
            "Invalid texture: "
            + "; ".join(texture_report["warnings"])
        )

    # Work on a copy of the original mesh.
    result_mesh = mesh.copy()

    # Check whether the mesh already has UV coordinates.
    uv_report = validate_uv(result_mesh)

    if not uv_report["has_uv"]:
        result_mesh = generate_uv(result_mesh)
        uv_generated = True
    elif not uv_report["is_valid"]:
        raise ValueError(
            "Mesh contains invalid UV coordinates: "
            + "; ".join(uv_report["warnings"])
        )
    else:
        uv_generated = False

    # Validate the UV coordinates after preparation.
    final_uv_report = validate_uv(result_mesh)

    if not final_uv_report["is_valid"]:
        raise ValueError(
            "UV preparation failed: "
            + "; ".join(final_uv_report["warnings"])
        )

    # Load the texture into memory.
    with Image.open(texture_path) as image:
        texture_image = image.convert("RGBA")

    # Build the PBR material using the existing utility.
    material = build_pbr_material(
        name=name,
        base_color_texture=texture_image,
        metallic_factor=metallic_factor,
        roughness_factor=roughness_factor,
    )

    # Apply the material to the mesh.
    result_mesh.visual.material = material

    report = {
        "success": True,
        "mesh_vertices": len(result_mesh.vertices),
        "mesh_faces": len(result_mesh.faces),
        "uv_generated": uv_generated,
        "uv_valid": final_uv_report["is_valid"],
        "texture_file": texture_report["file_name"],
        "texture_format": texture_report["image_format"],
        "texture_dimensions": texture_report["dimensions"],
        "material_name": material.name,
        "metallic_factor": material.metallicFactor,
        "roughness_factor": material.roughnessFactor,
        "warnings": [],
    }

    return result_mesh, report