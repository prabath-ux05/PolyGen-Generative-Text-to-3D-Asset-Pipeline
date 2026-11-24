"""Prompt cleaning and validation for text-to-3D generation."""

import unicodedata
from dataclasses import asdict, dataclass


class PromptValidationError(ValueError):
    """Raised when a text-to-3D prompt is invalid."""


@dataclass(frozen=True)
class ProcessedPrompt:
    """Structured result returned after prompt processing."""

    original_prompt: str
    cleaned_prompt: str
    word_count: int
    character_count: int

    def to_dict(self) -> dict:
        """Convert the result into a dictionary."""
        return asdict(self)


class PromptProcessor:
    """Clean and validate user prompts before model inference."""

    def __init__(self, min_length: int = 3, max_length: int = 500):
        if min_length < 1:
            raise ValueError("min_length must be at least 1")

        if max_length < min_length:
            raise ValueError(
                "max_length must be greater than or equal to min_length"
            )

        self.min_length = min_length
        self.max_length = max_length

    def clean_prompt(self, prompt: str) -> str:
        """Normalize Unicode and remove unnecessary whitespace."""
        if not isinstance(prompt, str):
            raise PromptValidationError("Prompt must be a string")

        normalized = unicodedata.normalize("NFKC", prompt)
        return " ".join(normalized.split())

    def validate_prompt(self, prompt: str) -> str:
        """Validate a prompt and return its cleaned form."""
        if not isinstance(prompt, str):
            raise PromptValidationError("Prompt must be a string")

        if "\x00" in prompt:
            raise PromptValidationError(
                "Prompt cannot contain null characters"
            )

        cleaned = self.clean_prompt(prompt)

        if not cleaned:
            raise PromptValidationError("Prompt cannot be empty")

        if len(cleaned) < self.min_length:
            raise PromptValidationError(
                f"Prompt must contain at least {self.min_length} characters"
            )

        if len(cleaned) > self.max_length:
            raise PromptValidationError(
                f"Prompt cannot exceed {self.max_length} characters"
            )

        return cleaned

    def process_prompt(self, prompt: str) -> ProcessedPrompt:
        """Return a validated and structured prompt."""
        cleaned = self.validate_prompt(prompt)

        return ProcessedPrompt(
            original_prompt=prompt,
            cleaned_prompt=cleaned,
            word_count=len(cleaned.split()),
            character_count=len(cleaned),
        )
