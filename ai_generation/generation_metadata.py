"""Store and manage metadata for generated 3D assets."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
import re


class MetadataError(Exception):
    """Raised when generation metadata is invalid or cannot be saved."""


@dataclass
class GenerationMetadata:
    """Represent information about one 3D generation run."""

    prompt: str
    model_name: str
    output_path: str = ""
    file_format: str = ""
    generation_time_seconds: float | None = None
    status: str = "success"
    error: str | None = None
    run_id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise MetadataError("Prompt must be a non-empty string")

        if not isinstance(self.model_name, str) or not self.model_name.strip():
            raise MetadataError("Model name must be a non-empty string")

        if not re.fullmatch(r"[A-Za-z0-9_-]+", self.run_id):
            raise MetadataError("Invalid run ID")

        if self.status not in {"success", "failed", "pending"}:
            raise MetadataError("Invalid generation status")

        if self.generation_time_seconds is not None:
            if self.generation_time_seconds < 0:
                raise MetadataError("Generation time cannot be negative")

        if not isinstance(self.extra, dict):
            raise MetadataError("Extra metadata must be a dictionary")

    def to_dict(self):
        """Convert metadata into a JSON-compatible dictionary."""
        return asdict(self)

    def to_json(self):
        """Return metadata as formatted JSON text."""
        try:
            return json.dumps(self.to_dict(), indent=4)
        except (TypeError, ValueError) as exc:
            raise MetadataError(
                f"Metadata cannot be converted to JSON: {exc}"
            ) from exc

    def save(self, directory="artifacts/metadata"):
        """Save metadata as a JSON file."""
        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{self.run_id}.json"

        try:
            output_file.write_text(
                self.to_json(),
                encoding="utf-8"
            )
        except OSError as exc:
            raise MetadataError(
                f"Could not save metadata: {exc}"
            ) from exc

        return output_file

    @classmethod
    def from_dict(cls, data):
        """Create metadata from a dictionary."""
        if not isinstance(data, dict):
            raise MetadataError("Metadata input must be a dictionary")

        try:
            return cls(**data)
        except (TypeError, ValueError) as exc:
            raise MetadataError(
                f"Invalid metadata data: {exc}"
            ) from exc

    @classmethod
    def load(cls, file_path):
        """Load metadata from a JSON file."""
        try:
            data = json.loads(
                Path(file_path).read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise MetadataError(
                f"Could not load metadata: {exc}"
            ) from exc

        return cls.from_dict(data)
