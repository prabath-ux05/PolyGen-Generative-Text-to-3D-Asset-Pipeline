"""AI-powered texture generation using Hugging Face."""

import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


def generate_texture(
    prompt: str,
    output_path: str | Path,
) -> dict:
    """
    Generate a texture image from a text prompt.

    Args:
        prompt: Description of the texture to generate.
        output_path: Where the generated image should be saved.

    Returns:
        Dictionary containing generation details.
    """

    token = os.getenv("HF_TOKEN")

    if not token:
        raise RuntimeError("HF_TOKEN is missing. Set it in your .env file.")

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = InferenceClient(
        provider="auto",
        api_key=token,
    )

    image = client.text_to_image(
        prompt=(
            f"{prompt}, seamless tileable PBR material texture, "
            "uniform lighting, no shadows, no perspective, "
            "high detail, realistic surface"
        ),
        model="black-forest-labs/FLUX.1-schnell",
    )

    image.save(output_path)

    return {
        "success": True,
        "prompt": prompt,
        "output_file": str(output_path.resolve()),
        "width": image.width,
        "height": image.height,
        "model": "black-forest-labs/FLUX.1-schnell",
    }