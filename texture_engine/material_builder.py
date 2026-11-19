
"""Build physically based rendering (PBR) materials."""

from PIL import Image
import trimesh


def build_pbr_material(
    name: str = "PolyGen_Material",
    base_color_texture: Image.Image | None = None,
    base_color_factor: tuple[int, int, int, int] = (255, 255, 255, 255),
    metallic_factor: float = 0.0,
    roughness_factor: float = 1.0,
    double_sided: bool = False,
) -> trimesh.visual.material.PBRMaterial:
    """
    Create a PBR material for a 3D mesh.

    Metallic and roughness factors must be between 0 and 1.
    Base color uses RGBA values between 0 and 255.
    """

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Material name must be a non-empty string.")

    if not isinstance(metallic_factor, (int, float)) or isinstance(
        metallic_factor, bool
    ):
        raise ValueError("Metallic factor must be a number.")

    if not isinstance(roughness_factor, (int, float)) or isinstance(
        roughness_factor, bool
    ):
        raise ValueError("Roughness factor must be a number.")

    if not 0.0 <= metallic_factor <= 1.0:
        raise ValueError("Metallic factor must be between 0 and 1.")

    if not 0.0 <= roughness_factor <= 1.0:
        raise ValueError("Roughness factor must be between 0 and 1.")

    if (
        not isinstance(base_color_factor, (tuple, list))
        or len(base_color_factor) != 4
        or any(
            not isinstance(value, int)
            or isinstance(value, bool)
            or not 0 <= value <= 255
            for value in base_color_factor
        )
    ):
        raise ValueError(
            "Base color factor must contain four integer values from 0 to 255."
        )

    if base_color_texture is not None and not isinstance(
        base_color_texture, Image.Image
    ):
        raise TypeError("Base color texture must be a PIL Image.")

    if not isinstance(double_sided, bool):
        raise ValueError("double_sided must be a boolean.")

    return trimesh.visual.material.PBRMaterial(
        name=name.strip(),
        baseColorTexture=base_color_texture,
        baseColorFactor=list(base_color_factor),
        metallicFactor=float(metallic_factor),
        roughnessFactor=float(roughness_factor),
        doubleSided=double_sided,
    )
