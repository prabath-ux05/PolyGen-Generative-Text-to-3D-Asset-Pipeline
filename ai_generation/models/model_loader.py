"""Lazy loading interface for Shap-E model components."""

from dataclasses import dataclass
from typing import Any, Callable, Optional

class ModelLoadError(RuntimeError):
    """Raised when a model cannot be loaded."""

@dataclass
class ModelComponents:
    """Holds the components required by Shap-E."""

    text_model: Any
    transmitter: Any
    device: str

class ShapEModelLoader:
    """Load Shap-E components only when explicitly requested."""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self._components: Optional[ModelComponents] = None

    @property
    def is_loaded(self) -> bool:
        """Check whether model components are available."""
        return self._components is not None

    def load_components(
        self,
        load_model_fn: Optional[Callable] = None,
    ) -> ModelComponents:
        """
        Load the Shap-E text model and transmitter.

        A custom loader function can be supplied for testing.
        No model weights are downloaded during object creation.
        """
        if self._components is not None:
            return self._components

        if load_model_fn is None:
            try:
                from shap_e.models.download import load_model
                load_model_fn = load_model
            except ImportError as exc:
                raise ModelLoadError(
                    "Shap-E is not installed. Install the Shap-E "
                    "package before loading model weights."
                ) from exc

        try:
            text_model = load_model_fn(
                "text300M",
                device=self.device,
            )

            transmitter = load_model_fn(
                "transmitter",
                device=self.device,
            )

            self._components = ModelComponents(
                text_model=text_model,
                transmitter=transmitter,
                device=self.device,
            )

            return self._components

        except Exception as exc:
            self._components = None
            raise ModelLoadError(
                f"Failed to load Shap-E components: {exc}"
            ) from exc

    def get_components(self) -> Optional[ModelComponents]:
        """Return loaded components, or None if not loaded."""
        return self._components

    def unload(self) -> None:
        """Release references to loaded model components."""
        self._components = None
