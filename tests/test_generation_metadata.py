import json
import pytest

from ai_generation.generation_metadata import (
    GenerationMetadata,
    MetadataError,
)


@pytest.fixture
def metadata():
    return GenerationMetadata(
        prompt="A wooden chair",
        model_name="Shap-E",
        output_path="artifacts/chair.obj",
        file_format="obj",
        generation_time_seconds=12.5,
    )


def test_metadata_creation(metadata):
    assert metadata.prompt == "A wooden chair"
    assert metadata.model_name == "Shap-E"
    assert metadata.status == "success"


def test_run_id_is_generated(metadata):
    assert metadata.run_id
    assert len(metadata.run_id) == 32


def test_each_run_has_unique_id():
    first = GenerationMetadata(prompt="Chair", model_name="Shap-E")
    second = GenerationMetadata(prompt="Table", model_name="Shap-E")
    assert first.run_id != second.run_id


def test_metadata_to_dict(metadata):
    data = metadata.to_dict()
    assert data["prompt"] == "A wooden chair"
    assert data["file_format"] == "obj"


def test_metadata_to_json(metadata):
    data = json.loads(metadata.to_json())
    assert data["model_name"] == "Shap-E"


def test_metadata_save_and_load(metadata, tmp_path):
    saved_file = metadata.save(tmp_path)
    loaded = GenerationMetadata.load(saved_file)

    assert loaded.run_id == metadata.run_id
    assert loaded.prompt == metadata.prompt
    assert loaded.output_path == metadata.output_path


def test_metadata_save_creates_directory(metadata, tmp_path):
    folder = tmp_path / "new" / "metadata"
    saved_file = metadata.save(folder)

    assert folder.exists()
    assert saved_file.exists()


def test_empty_prompt_is_rejected():
    with pytest.raises(MetadataError):
        GenerationMetadata(prompt="", model_name="Shap-E")


def test_empty_model_name_is_rejected():
    with pytest.raises(MetadataError):
        GenerationMetadata(prompt="Chair", model_name="")


def test_invalid_status_is_rejected():
    with pytest.raises(MetadataError):
        GenerationMetadata(
            prompt="Chair",
            model_name="Shap-E",
            status="unknown",
        )


def test_negative_generation_time_is_rejected():
    with pytest.raises(MetadataError):
        GenerationMetadata(
            prompt="Chair",
            model_name="Shap-E",
            generation_time_seconds=-1,
        )


def test_invalid_run_id_is_rejected():
    with pytest.raises(MetadataError):
        GenerationMetadata(
            prompt="Chair",
            model_name="Shap-E",
            run_id="../invalid",
        )


def test_extra_metadata_is_preserved():
    item = GenerationMetadata(
        prompt="Chair",
        model_name="Shap-E",
        extra={"seed": 42, "version": "1.0"},
    )
    assert item.to_dict()["extra"]["seed"] == 42


def test_from_dict(metadata):
    restored = GenerationMetadata.from_dict(metadata.to_dict())
    assert restored.prompt == metadata.prompt
    assert restored.run_id == metadata.run_id


def test_invalid_dictionary_is_rejected():
    with pytest.raises(MetadataError):
        GenerationMetadata.from_dict({"unknown": "value"})


def test_invalid_json_file_is_rejected(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(MetadataError):
        GenerationMetadata.load(bad_file)
