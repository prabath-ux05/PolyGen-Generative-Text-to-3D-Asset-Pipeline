
"""Image processing utilities for generated textures."""

from PIL import Image


SUPPORTED_MODES = {"RGB", "RGBA", "L"}


def resize_texture(
    image: Image.Image,
    size: tuple[int, int],
) -> Image.Image:
    """Resize a texture to the requested width and height."""

    if not isinstance(image, Image.Image):
        raise TypeError("Expected a PIL Image object.")

    if len(size) != 2 or any(
        not isinstance(value, int) or isinstance(value, bool) or value <= 0
        for value in size
    ):
        raise ValueError("Size must contain two positive integers.")

    return image.resize(size, Image.Resampling.LANCZOS)


def convert_texture_mode(
    image: Image.Image,
    mode: str = "RGBA",
) -> Image.Image:
    """Convert a texture to RGB, RGBA, or grayscale."""

    if not isinstance(image, Image.Image):
        raise TypeError("Expected a PIL Image object.")

    if mode not in SUPPORTED_MODES:
        raise ValueError(
            f"Unsupported color mode: {mode}. "
            "Use RGB, RGBA, or L."
        )

    return image.convert(mode)


def create_thumbnail(
    image: Image.Image,
    size: tuple[int, int] = (256, 256),
) -> Image.Image:
    """Create a thumbnail while preserving the original aspect ratio."""

    if not isinstance(image, Image.Image):
        raise TypeError("Expected a PIL Image object.")

    if len(size) != 2 or any(
        not isinstance(value, int) or isinstance(value, bool) or value <= 0
        for value in size
    ):
        raise ValueError("Size must contain two positive integers.")

    thumbnail = image.copy()
    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)

    return thumbnail
