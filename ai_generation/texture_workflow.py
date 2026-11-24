"""Text-driven texture generation and mesh processing workflow."""

from pathlib import Path

from ai_generation.texture_generator import generate_texture
from texture_engine.pipeline import process_asset


def generate_and_texture_asset(
    mesh_path: str | Path,
    prompt: str,
    output_path: str | Path,
    texture_path: str | Path = "generated_textures/generated_texture.png",
    use_fallback: bool = False,
) -> dict:
    """
    Generate a texture from a prompt and apply it to a mesh.

    Supports AI generation or a local procedural fallback.
    """

    texture_path = Path(texture_path)

    # Step 1: Generate the texture.
    if use_fallback:
        from ai_generation.fallback_texture import generate_fallback_texture

        texture_report = generate_fallback_texture(
            prompt=prompt,
            output_path=texture_path,
        )
    else:
        texture_report = generate_texture(
            prompt=prompt,
            output_path=texture_path,
        )

    # Step 2: Process the mesh with the generated texture.
    asset_report = process_asset(
        mesh_path=mesh_path,
        texture_path=texture_path,
        output_path=output_path,
    )

    # Step 3: Return a combined report.
    return {
        "success": True,
        "texture_generation": texture_report,
        "asset_processing": asset_report,
        "output_file": asset_report["output_file"],
    }