import json

import pytest
import trimesh

from ai_generation.generator import (
    TextTo3DGenerator,
    GenerationError,
)
from ai_generation.model_manager import ModelManager, ModelStatus
from ai_generation.exporter import MeshExporter


class FakeModelLoader:
    """Provide model components without downloading real weights."""

    def __init__(self):
        self.loaded = False

    def load_components(self):
        self.loaded = True
        return {"model": "fake-shap-e", "device": "cpu"}


@pytest.fixture
def setup_generator(tmp_path):
    loader = FakeModelLoader()
    manager = ModelManager(device="cpu")
    exporter = MeshExporter(tmp_path / "generated")

    def fake_generation(prompt, components):
        assert isinstance(prompt, str)
        assert components["model"] == "fake-shap-e"
        return trimesh.creation.box()

    generator = TextTo3DGenerator(
        model_manager=manager,
        model_loader=loader,
        exporter=exporter,
        metadata_directory=tmp_path / "metadata",
        generation_fn=fake_generation,
    )

    return generator, manager, loader, tmp_path


def test_successful_generation(setup_generator):
    generator, manager, loader, _ = setup_generator

    result = generator.generate("A wooden chair")

    assert result.output_path.exists()
    assert result.output_path.suffix == ".obj"
    assert loader.loaded
    assert manager.get_status("shap-e") == ModelStatus.READY


def test_prompt_is_processed_before_generation(setup_generator):
    generator, _, _, _ = setup_generator

    result = generator.generate("  A   wooden   chair  ")

    assert result.processed_prompt.cleaned_prompt == "A wooden chair"


def test_glb_generation(setup_generator):
    generator, _, _, _ = setup_generator

    result = generator.generate(
        "A modern table",
        file_format="glb",
    )

    assert result.output_path.suffix == ".glb"
    assert result.output_path.exists()


def test_custom_filename(setup_generator):
    generator, _, _, _ = setup_generator

    result = generator.generate(
        "A wooden chair",
        filename="custom_chair",
    )

    assert result.output_path.name == "custom_chair.obj"


def test_generation_metadata_is_saved(setup_generator):
    generator, _, _, tmp_path = setup_generator

    result = generator.generate("A wooden chair")

    metadata_file = (
        tmp_path / "metadata" / f"{result.metadata.run_id}.json"
    )

    assert metadata_file.exists()

    saved_data = json.loads(
        metadata_file.read_text(encoding="utf-8")
    )

    assert saved_data["prompt"] == "A wooden chair"
    assert saved_data["status"] == "success"


def test_generation_result_contains_performance(setup_generator):
    generator, _, _, _ = setup_generator

    result = generator.generate("A wooden chair")

    assert result.performance.elapsed_seconds >= 0
    assert result.performance.success is True
    assert result.performance.peak_memory_mb >= 0


def test_result_can_be_converted_to_dictionary(setup_generator):
    generator, _, _, _ = setup_generator

    result = generator.generate("A wooden chair")
    data = result.to_dict()

    assert "output_path" in data
    assert "metadata" in data
    assert "performance" in data


def test_invalid_prompt_fails(setup_generator):
    generator, _, _, _ = setup_generator

    with pytest.raises(GenerationError):
        generator.generate("")


def test_invalid_mesh_fails(setup_generator):
    generator, manager, _, _ = setup_generator

    generator.generation_fn = lambda prompt, components: "invalid mesh"

    with pytest.raises(GenerationError):
        generator.generate("A wooden chair")

    assert manager.get_status("shap-e") == ModelStatus.FAILED


def test_generation_function_error_is_handled(setup_generator):
    generator, manager, _, _ = setup_generator

    def failing_generation(prompt, components):
        raise RuntimeError("Model inference failed")

    with pytest.raises(GenerationError):
        generator.generate(
            "A wooden chair",
            generation_fn=failing_generation,
        )

    assert manager.get_status("shap-e") == ModelStatus.FAILED


def test_missing_generation_function_fails(tmp_path):
    generator = TextTo3DGenerator(
        model_manager=ModelManager(device="cpu"),
        model_loader=FakeModelLoader(),
        exporter=MeshExporter(tmp_path / "generated"),
        metadata_directory=tmp_path / "metadata",
    )

    with pytest.raises(GenerationError):
        generator.generate("A wooden chair")


def test_unsupported_format_fails(setup_generator):
    generator, manager, _, _ = setup_generator

    with pytest.raises(GenerationError):
        generator.generate(
            "A wooden chair",
            file_format="unsupported",
        )

    assert manager.get_status("shap-e") == ModelStatus.FAILED


def test_model_loader_failure_is_handled(setup_generator):
    generator, manager, loader, _ = setup_generator

    def failing_loader():
        raise RuntimeError("Model loading failed")

    loader.load_components = failing_loader

    with pytest.raises(GenerationError):
        generator.generate("A wooden chair")

    assert manager.get_status("shap-e") == ModelStatus.FAILED


def test_generation_creates_unique_files(setup_generator):
    generator, _, _, _ = setup_generator

    first = generator.generate(
        "A wooden chair",
        filename="chair",
    )

    second = generator.generate(
        "A wooden chair",
        filename="chair",
    )

    assert first.output_path != second.output_path
    assert first.output_path.exists()
    assert second.output_path.exists()


def test_generation_function_receives_clean_prompt(setup_generator):
    generator, _, _, _ = setup_generator
    received = {}

    def capture_generation(prompt, components):
        received["prompt"] = prompt
        return trimesh.creation.box()

    generator.generate(
        "  A   wooden chair ",
        generation_fn=capture_generation,
    )

    assert received["prompt"] == "A wooden chair"
