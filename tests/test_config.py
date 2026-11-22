from pathlib import Path

import pytest
from ai_generation.config import GenerationConfig


def test_default_config():
    config = GenerationConfig()
    assert config.default_format == "obj"
    assert config.min_prompt_length == 3
    assert config.max_prompt_length == 500


def test_format_normalization():
    assert GenerationConfig(default_format=" GLB ").default_format == "glb"


def test_invalid_format():
    with pytest.raises(ValueError):
        GenerationConfig(default_format="fbx")


def test_invalid_minimum_length():
    with pytest.raises(ValueError):
        GenerationConfig(min_prompt_length=0)


def test_invalid_maximum_length():
    with pytest.raises(ValueError):
        GenerationConfig(min_prompt_length=10, max_prompt_length=5)


def test_invalid_device():
    with pytest.raises(ValueError):
        GenerationConfig(device="tpu")


def test_environment_configuration(monkeypatch):
    monkeypatch.setenv("POLYGEN_OUTPUT_DIR", "custom/output")
    monkeypatch.setenv("POLYGEN_METADATA_DIR", "custom/metadata")
    monkeypatch.setenv("POLYGEN_DEFAULT_FORMAT", "glb")
    monkeypatch.setenv("POLYGEN_DEVICE", "cpu")

    config = GenerationConfig.from_env()

    assert config.output_dir == Path("custom/output")
    assert config.metadata_dir == Path("custom/metadata")
    assert config.default_format == "glb"
    assert config.device == "cpu"


def test_auto_device_from_environment(monkeypatch):
    monkeypatch.setenv("POLYGEN_DEVICE", "auto")
    assert GenerationConfig.from_env().device is None


def test_create_directories(tmp_path):
    config = GenerationConfig(
        output_dir=tmp_path / "generated",
        metadata_dir=tmp_path / "metadata",
    )
    output, metadata = config.create_directories()

    assert output.is_dir()
    assert metadata.is_dir()


def test_config_dictionary():
    data = GenerationConfig(device=None).to_dict()
    assert data["device"] == "auto"
    assert data["default_format"] == "obj"
