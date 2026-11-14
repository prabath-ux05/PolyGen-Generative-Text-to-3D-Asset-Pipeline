import pytest

from ai_generation.model_manager import (
    ModelManager,
    ModelStatus,
    ModelProvider,
)


def test_manager_detects_cpu():
    manager = ModelManager(device="cpu")
    assert manager.get_device() == "cpu"


def test_shap_e_is_registered():
    manager = ModelManager()
    models = manager.list_models()

    assert len(models) == 1
    assert models[0].name == "Shap-E"
    assert models[0].provider == ModelProvider.SHAP_E


def test_get_model():
    manager = ModelManager()
    config = manager.get_model("shap-e")

    assert config.model_id == "text300M"


def test_model_name_is_case_insensitive():
    manager = ModelManager()
    assert manager.get_model("SHAP-E").name == "Shap-E"


def test_unknown_model_raises_error():
    manager = ModelManager()

    with pytest.raises(ValueError):
        manager.get_model("unknown")


def test_select_model():
    manager = ModelManager()
    config = manager.select_model("shap-e")

    assert config.name == "Shap-E"
    assert manager.get_active_model() == config


def test_no_active_model_initially():
    manager = ModelManager()
    assert manager.get_active_model() is None


def test_initial_model_status():
    manager = ModelManager()
    assert manager.get_status("shap-e") == ModelStatus.NOT_LOADED


def test_update_model_status():
    manager = ModelManager()
    manager.update_status("shap-e", ModelStatus.READY)

    assert manager.get_status("shap-e") == ModelStatus.READY


def test_invalid_status_lookup():
    manager = ModelManager()

    with pytest.raises(ValueError):
        manager.get_status("unknown")


def test_invalid_status_update():
    manager = ModelManager()

    with pytest.raises(ValueError):
        manager.update_status("unknown", ModelStatus.READY)
