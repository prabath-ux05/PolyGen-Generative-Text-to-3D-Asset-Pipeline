import pytest

from ai_generation.models.model_loader import (
    ShapEModelLoader,
    ModelLoadError,
)


def test_loader_starts_unloaded():
    loader = ShapEModelLoader(device="cpu")

    assert loader.is_loaded is False
    assert loader.get_components() is None


def test_loader_uses_cpu():
    loader = ShapEModelLoader(device="cpu")

    assert loader.device == "cpu"


def test_load_components_with_mock():
    calls = []

    def fake_loader(model_name, device):
        calls.append((model_name, device))
        return f"fake-{model_name}"

    loader = ShapEModelLoader(device="cpu")
    components = loader.load_components(fake_loader)

    assert loader.is_loaded is True
    assert components.text_model == "fake-text300M"
    assert components.transmitter == "fake-transmitter"
    assert components.device == "cpu"
    assert len(calls) == 2


def test_loaded_components_are_cached():
    call_count = 0

    def fake_loader(model_name, device):
        nonlocal call_count
        call_count += 1
        return model_name

    loader = ShapEModelLoader()
    first = loader.load_components(fake_loader)
    second = loader.load_components(fake_loader)

    assert first is second
    assert call_count == 2


def test_loader_wraps_loading_errors():
    def failing_loader(model_name, device):
        raise RuntimeError("Test loading failure")

    loader = ShapEModelLoader()

    with pytest.raises(ModelLoadError, match="Failed to load"):
        loader.load_components(failing_loader)

    assert loader.is_loaded is False


def test_unload_clears_components():
    loader = ShapEModelLoader()
    loader.load_components(
        lambda model_name, device: model_name
    )

    loader.unload()

    assert loader.is_loaded is False
    assert loader.get_components() is None
