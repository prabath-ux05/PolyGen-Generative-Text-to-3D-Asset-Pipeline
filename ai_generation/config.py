"""Central configuration for the PolyGen generation engine."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class GenerationConfig:
    """Store validated settings for text-to-3D generation."""

    output_dir: Path = Path("artifacts/generated")
    metadata_dir: Path = Path("artifacts/metadata")
    default_format: str = "obj"
    min_prompt_length: int = 3
    max_prompt_length: int = 500
    device: Optional[str] = None

    def __post_init__(self):
        object.__setattr__(self, "output_dir", Path(self.output_dir))
        object.__setattr__(self, "metadata_dir", Path(self.metadata_dir))

        selected_format = self.default_format.lower().strip()
        if selected_format not in {"obj", "glb"}:
            raise ValueError("Default format must be obj or glb")

        object.__setattr__(self, "default_format", selected_format)

        if self.min_prompt_length < 1:
            raise ValueError("Minimum prompt length must be positive")

        if self.max_prompt_length < self.min_prompt_length:
            raise ValueError("Maximum prompt length must be >= minimum")

        if self.device not in {None, "cpu", "cuda"}:
            raise ValueError("Device must be cpu, cuda, or None")

    @classmethod
    def from_env(cls):
        """Build configuration from POLYGEN environment variables."""

        raw_device = os.getenv("POLYGEN_DEVICE", "auto").strip().lower()
        device = None if raw_device in {"", "auto"} else raw_device

        return cls(
            output_dir=os.getenv(
                "POLYGEN_OUTPUT_DIR",
                "artifacts/generated",
            ),
            metadata_dir=os.getenv(
                "POLYGEN_METADATA_DIR",
                "artifacts/metadata",
            ),
            default_format=os.getenv("POLYGEN_DEFAULT_FORMAT", "obj"),
            min_prompt_length=int(
                os.getenv("POLYGEN_MIN_PROMPT_LENGTH", "3")
            ),
            max_prompt_length=int(
                os.getenv("POLYGEN_MAX_PROMPT_LENGTH", "500")
            ),
            device=device,
        )

    def create_directories(self):
        """Create configured output directories."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        return self.output_dir, self.metadata_dir

    def to_dict(self):
        """Return JSON-friendly configuration values."""

        return {
            "output_dir": str(self.output_dir),
            "metadata_dir": str(self.metadata_dir),
            "default_format": self.default_format,
            "min_prompt_length": self.min_prompt_length,
            "max_prompt_length": self.max_prompt_length,
            "device": self.device or "auto",
        }
