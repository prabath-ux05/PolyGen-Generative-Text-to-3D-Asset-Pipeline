"""Manage available text-to-3D models and their configuration."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ModelProvider(str, Enum):
    SHAP_E = "shap_e"

class ModelStatus(str, Enum):
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    FAILED = "failed"

@dataclass(frozen=True)
class ModelConfig:
    """Configuration for a supported text-to-3D model."""

    name: str
    provider: ModelProvider
    model_id: str
    device: str = "cpu"
    enabled: bool = True
    description: str = ""

class ModelManager:
    """Select models and track their loading status."""

    def __init__(self, device: Optional[str] = None):
        self.device = device or self.detect_device()

        self._models = {
            "shap-e": ModelConfig(
                name="Shap-E",
                provider=ModelProvider.SHAP_E,
                model_id="text300M",
                device=self.device,
                description=(
                    "Research model for generating 3D assets "
                    "from text prompts."
                ),
            )
        }

        self._active_model = None
        self._statuses = {
            name: ModelStatus.NOT_LOADED
            for name in self._models
        }

    @staticmethod
    def detect_device() -> str:
        """Use CUDA when available; otherwise use CPU."""
        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass

        return "cpu"

    def list_models(self) -> list:
        """Return all registered model configurations."""
        return list(self._models.values())

    def get_model(self, name: str) -> ModelConfig:
        """Return a model configuration by name."""
        key = name.lower()

        if key not in self._models:
            raise ValueError(f"Unsupported model: {name}")

        return self._models[key]

    def select_model(self, name: str) -> ModelConfig:
        """Select an enabled model for generation."""
        config = self.get_model(name)

        if not config.enabled:
            raise ValueError(f"Model is disabled: {name}")

        self._active_model = name.lower()
        return config

    def get_active_model(self) -> Optional[ModelConfig]:
        """Return the currently selected model."""
        if self._active_model is None:
            return None

        return self._models[self._active_model]

    def update_status(self, name: str, status: ModelStatus) -> None:
        """Update the loading status of a registered model."""
        key = name.lower()

        if key not in self._models:
            raise ValueError(f"Unsupported model: {name}")

        self._statuses[key] = status

    def get_status(self, name: str) -> ModelStatus:
        """Get the current status of a model."""
        key = name.lower()

        if key not in self._statuses:
            raise ValueError(f"Unsupported model: {name}")

        return self._statuses[key]

    def get_device(self) -> str:
        """Return the device selected for model execution."""
        return self.device
