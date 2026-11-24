"""Centralized application configuration and metadata."""

import os

APP_NAME: str = "PolyGen API"
APP_DESCRIPTION: str = "Generative Text-to-3D Asset Pipeline"
API_VERSION: str = "0.1.0"

# Default allowed frontend origins for CORS (e.g. React/Vite/Next development servers)
DEFAULT_CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]


def get_cors_origins() -> list[str]:
    """Retrieve allowed frontend origins from environment or sensible defaults.

    Reads ALLOWED_ORIGINS as a comma-separated list of origins.
    Wildcard ('*') origins with credentials enabled are strictly prevented.
    """
    raw_origins = os.getenv("ALLOWED_ORIGINS")
    if raw_origins:
        parsed = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
        if parsed:
            return parsed
    return list(DEFAULT_CORS_ORIGINS)


# Pipeline adapter mode configuration:
# "none" -> unintegrated (returns 503 per Day 4/10 contracts)
# "synthetic" -> isolated deterministic geometry generation (Stage 2)
# "neural" -> live neural inference
DEFAULT_PIPELINE_ADAPTER: str = "none"


def get_pipeline_adapter() -> str:
    """Retrieve active pipeline adapter from environment or default."""
    return os.getenv("POLYGEN_PIPELINE_ADAPTER", DEFAULT_PIPELINE_ADAPTER).strip().lower()

