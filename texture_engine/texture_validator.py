
"""Validate generated texture image files."""

from pathlib import Path

from PIL import Image, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_FORMATS = {"PNG", "JPEG", "WEBP"}
SUPPORTED_MODES = {"RGB", "RGBA", "L"}

MAX_DIMENSION = 8192


def validate_texture(image_path: str | Path) -> dict:
    """Validate texture format, dimensions, and color mode."""

    path = Path(image_path)
    warnings = []

    if not path.exists():
        warnings.append("Texture file does not exist.")
        return {
            "file_name": path.name,
            "is_valid": False,
            "image_format": None,
            "dimensions": None,
            "color_mode": None,
            "quality_status": "warning",
            "warnings": warnings,
        }

    if not path.is_file():
        warnings.append("The provided path is not a file.")
        return {
            "file_name": path.name,
            "is_valid": False,
            "image_format": None,
            "dimensions": None,
            "color_mode": None,
            "quality_status": "warning",
            "warnings": warnings,
        }

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        warnings.append("Unsupported texture file extension.")

    image_format = None
    dimensions = None
    color_mode = None

    try:
        with Image.open(path) as image:
            image_format = image.format
            dimensions = list(image.size)
            color_mode = image.mode
            image.verify()

    except (UnidentifiedImageError, OSError, ValueError):
        warnings.append("Image file is corrupted or unreadable.")

    if image_format is not None:
        if image_format not in SUPPORTED_FORMATS:
            warnings.append("Unsupported image format.")

        expected_formats = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".webp": "WEBP",
        }

        expected_format = expected_formats.get(path.suffix.lower())

        if expected_format and image_format != expected_format:
            warnings.append("File extension does not match image format.")

    if dimensions is not None:
        width, height = dimensions

        if width <= 0 or height <= 0:
            warnings.append("Image dimensions must be greater than zero.")

        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            warnings.append(
                f"Image dimensions must not exceed {MAX_DIMENSION} pixels."
            )

    if color_mode is not None and color_mode not in SUPPORTED_MODES:
        warnings.append(
            "Unsupported color mode. Use RGB, RGBA, or grayscale (L)."
        )

    is_valid = len(warnings) == 0

    return {
        "file_name": path.name,
        "is_valid": is_valid,
        "image_format": image_format,
        "dimensions": dimensions,
        "color_mode": color_mode,
        "quality_status": "good" if is_valid else "warning",
        "warnings": warnings,
    }
