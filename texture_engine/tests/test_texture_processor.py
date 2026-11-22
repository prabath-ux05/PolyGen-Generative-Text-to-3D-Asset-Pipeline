
"""Tests for texture processing utilities."""

import pytest
from PIL import Image

from texture_engine.texture_processor import (
    resize_texture,
    convert_texture_mode,
    create_thumbnail,
)


def test_resize_texture():
    image = Image.new("RGB", (100, 100), "red")

    result = resize_texture(image, (256, 128))

    assert result.size == (256, 128)
    assert image.size == (100, 100)


def test_resize_invalid_dimensions():
    image = Image.new("RGB", (100, 100))

    with pytest.raises(ValueError):
        resize_texture(image, (0, 100))


def test_resize_rejects_boolean_dimensions():
    image = Image.new("RGB", (100, 100))

    with pytest.raises(ValueError):
        resize_texture(image, (True, 100))


def test_convert_to_rgba():
    image = Image.new("RGB", (64, 64), "red")

    result = convert_texture_mode(image, "RGBA")

    assert result.mode == "RGBA"
    assert result.size == image.size


def test_convert_to_grayscale():
    image = Image.new("RGB", (64, 64), "blue")

    result = convert_texture_mode(image, "L")

    assert result.mode == "L"


def test_unsupported_color_mode():
    image = Image.new("RGB", (64, 64))

    with pytest.raises(ValueError):
        convert_texture_mode(image, "CMYK")


def test_create_thumbnail_preserves_aspect_ratio():
    image = Image.new("RGB", (800, 400), "green")

    result = create_thumbnail(image, (200, 200))

    assert result.size == (200, 100)
    assert image.size == (800, 400)


def test_thumbnail_does_not_enlarge_small_image():
    image = Image.new("RGB", (100, 50), "blue")

    result = create_thumbnail(image, (256, 256))

    assert result.size == (100, 50)


def test_thumbnail_invalid_dimensions():
    image = Image.new("RGB", (100, 100))

    with pytest.raises(ValueError):
        create_thumbnail(image, (256, -1))


def test_functions_reject_invalid_image():
    with pytest.raises(TypeError):
        resize_texture("not an image", (100, 100))

    with pytest.raises(TypeError):
        convert_texture_mode("not an image", "RGB")

    with pytest.raises(TypeError):
        create_thumbnail("not an image")
