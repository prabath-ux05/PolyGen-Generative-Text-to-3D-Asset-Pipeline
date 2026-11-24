"""Tests for texture generation."""

from pathlib import Path

from PIL import Image
import pytest

from ai_generation.fallback_texture import generate_fallback_texture


def test_generate_fallback_texture(tmp_path):
    output_path = tmp_path / "wood.png"

    result = generate_fallback_texture(
        prompt="oak wood surface",
        output_path=output_path,
    )

    assert result["success"] is True
    assert output_path.exists()
    assert result["width"] == 512
    assert result["height"] == 512
    assert result["model"] == "procedural-fallback"

    image = Image.open(output_path)
    assert image.size == (512, 512)


def test_fallback_rejects_empty_prompt(tmp_path):
    with pytest.raises(ValueError):
        generate_fallback_texture(
            prompt="",
            output_path=tmp_path / "invalid.png",
        )


def test_fallback_custom_size(tmp_path):
    output_path = tmp_path / "custom.png"

    result = generate_fallback_texture(
        prompt="stone texture",
        output_path=output_path,
        size=(256, 256),
    )

    assert result["width"] == 256
    assert result["height"] == 256
    assert output_path.exists()