
"""Tests for texture image validation."""

from PIL import Image

from texture_engine.texture_validator import validate_texture


def test_valid_png_texture(tmp_path):
    path = tmp_path / "texture.png"
    Image.new("RGB", (512, 512)).save(path)

    report = validate_texture(path)

    assert report["is_valid"] is True
    assert report["image_format"] == "PNG"
    assert report["dimensions"] == [512, 512]
    assert report["color_mode"] == "RGB"


def test_valid_rgba_texture(tmp_path):
    path = tmp_path / "texture.png"
    Image.new("RGBA", (256, 256)).save(path)

    report = validate_texture(path)

    assert report["is_valid"] is True
    assert report["color_mode"] == "RGBA"


def test_valid_jpeg_texture(tmp_path):
    path = tmp_path / "texture.jpg"
    Image.new("RGB", (128, 128)).save(path, format="JPEG")

    report = validate_texture(path)

    assert report["is_valid"] is True
    assert report["image_format"] == "JPEG"


def test_missing_texture_file(tmp_path):
    report = validate_texture(tmp_path / "missing.png")

    assert report["is_valid"] is False
    assert any("does not exist" in w for w in report["warnings"])


def test_corrupted_texture_file(tmp_path):
    path = tmp_path / "corrupted.png"
    path.write_text("Not a valid image", encoding="utf-8")

    report = validate_texture(path)

    assert report["is_valid"] is False
    assert any("corrupted or unreadable" in w
               for w in report["warnings"])


def test_unsupported_extension(tmp_path):
    path = tmp_path / "texture.bmp"
    Image.new("RGB", (64, 64)).save(path)

    report = validate_texture(path)

    assert report["is_valid"] is False
    assert any("Unsupported texture file extension" in w
               for w in report["warnings"])


def test_unsupported_color_mode(tmp_path):
    path = tmp_path / "texture.jpg"
    Image.new("CMYK", (128, 128)).save(path, format="JPEG")

    report = validate_texture(path)

    assert report["is_valid"] is False
    assert any("Unsupported color mode" in w
               for w in report["warnings"])


def test_extension_format_mismatch(tmp_path):
    path = tmp_path / "texture.png"
    Image.new("RGB", (128, 128)).save(path, format="JPEG")

    report = validate_texture(path)

    assert report["is_valid"] is False
    assert any("does not match" in w for w in report["warnings"])


def test_grayscale_texture(tmp_path):
    path = tmp_path / "texture.png"
    Image.new("L", (128, 128)).save(path)

    report = validate_texture(path)

    assert report["is_valid"] is True
    assert report["color_mode"] == "L"
