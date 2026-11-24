"""Local fallback texture generation for development and testing."""

from pathlib import Path

from PIL import Image, ImageDraw


def generate_fallback_texture(
    prompt: str,
    output_path: str | Path,
    size: tuple[int, int] = (512, 512),
) -> dict:
    """Generate a procedural texture locally without an AI API."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", size, (130, 100, 70))
    draw = ImageDraw.Draw(image)

    # Add subtle texture variations.
    for y in range(0, size[1], 8):
        shade = max(50, min(220, 130 + (y % 60) - 30))
        draw.line(
            [(0, y), (size[0], y)],
            fill=(shade, shade - 20, shade - 40),
            width=3,
        )

    image.save(output_path)

    return {
        "success": True,
        "prompt": prompt,
        "output_file": str(output_path.resolve()),
        "width": image.width,
        "height": image.height,
        "model": "procedural-fallback",
    }