
"""Tests for PBR material construction."""

import pytest
import trimesh
from PIL import Image

from texture_engine.material_builder import build_pbr_material


def test_build_default_material():
    material = build_pbr_material()

    assert isinstance(material, trimesh.visual.material.PBRMaterial)
    assert material.name == "PolyGen_Material"
    assert material.metallicFactor == 0.0
    assert material.roughnessFactor == 1.0


def test_build_custom_material():
    material = build_pbr_material(
        name="Metal_Material",
        metallic_factor=1.0,
        roughness_factor=0.25,
    )

    assert material.name == "Metal_Material"
    assert material.metallicFactor == 1.0
    assert material.roughnessFactor == 0.25


def test_build_material_with_base_color_texture():
    texture = Image.new("RGB", (64, 64), "red")

    material = build_pbr_material(
        base_color_texture=texture
    )

    assert material.baseColorTexture is texture


def test_build_material_with_custom_color():
    material = build_pbr_material(
        base_color_factor=(255, 0, 0, 255)
    )

    assert list(material.baseColorFactor) == [255, 0, 0, 255]


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_metallic_factor(value):
    with pytest.raises(ValueError, match="Metallic"):
        build_pbr_material(metallic_factor=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_roughness_factor(value):
    with pytest.raises(ValueError, match="Roughness"):
        build_pbr_material(roughness_factor=value)


def test_invalid_base_color_factor():
    with pytest.raises(ValueError, match="Base color"):
        build_pbr_material(base_color_factor=(255, 0, 0))


def test_invalid_texture_type():
    with pytest.raises(TypeError, match="PIL Image"):
        build_pbr_material(base_color_texture="texture.png")


def test_empty_material_name():
    with pytest.raises(ValueError, match="name"):
        build_pbr_material(name="   ")


def test_double_sided_material():
    material = build_pbr_material(double_sided=True)

    assert material.doubleSided is True
