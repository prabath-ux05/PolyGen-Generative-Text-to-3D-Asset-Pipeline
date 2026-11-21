import trimesh

from ai_generation.config import GenerationConfig
from ai_generation.generator import TextTo3DGenerator
from ai_generation.benchmark import BenchmarkRunner


class FakeModelLoader:
    def load_components(self):
        return {"model": "test-model"}


def make_generator(tmp_path, output_format="obj", max_length=500):
    config = GenerationConfig(
        output_dir=tmp_path / "generated",
        metadata_dir=tmp_path / "metadata",
        default_format=output_format,
        max_prompt_length=max_length,
        device="cpu",
    )

    return TextTo3DGenerator(
        model_loader=FakeModelLoader(),
        config=config,
        generation_fn=lambda prompt, components: trimesh.creation.box(),
    )


def test_generator_uses_configured_format(tmp_path):
    generator = make_generator(tmp_path, output_format="glb")
    result = generator.generate("A small red chair")

    assert result.output_path.suffix == ".glb"
    assert result.output_path.exists()


def test_generator_saves_metadata(tmp_path):
    generator = make_generator(tmp_path)
    result = generator.generate("A small wooden table")

    assert result.metadata.status == "success"
    assert result.metadata.extra["device"] == "cpu"
    assert result.validation is not None
    assert isinstance(result.validation.to_dict(), dict)


def test_benchmark_runs_generation_pipeline(tmp_path):
    generator = make_generator(tmp_path)
    report = BenchmarkRunner(generator).run(
        ["A red chair", "A blue table", "A green tree"]
    )

    assert report.total == 3
    assert report.successful == 3
    assert report.failed == 0


def test_generator_rejects_overlong_prompt(tmp_path):
    generator = make_generator(tmp_path, max_length=20)

    try:
        generator.generate("This prompt is definitely much longer than twenty characters")
    except Exception:
        pass
    else:
        raise AssertionError("Expected an overlong prompt to fail")
