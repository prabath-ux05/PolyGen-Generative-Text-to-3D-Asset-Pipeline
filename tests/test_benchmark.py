import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ai_generation.benchmark import BenchmarkRunner


class FakeGenerator:
    def generate(self, prompt, file_format=None):
        if prompt == "broken prompt":
            raise RuntimeError("Generation failed")

        return SimpleNamespace(
            output_path=Path("artifacts") / f"{prompt.replace(' ', '_')}.{file_format or 'obj'}"
        )


def test_benchmark_success_and_failure():
    report = BenchmarkRunner(FakeGenerator()).run(
        ["red chair", "broken prompt", "blue table"]
    )

    assert report.total == 3
    assert report.successful == 2
    assert report.failed == 1
    assert len(report.results) == 3


def test_success_rate():
    report = BenchmarkRunner(FakeGenerator()).run(
        ["red chair", "broken prompt"]
    )
    assert report.success_rate == 0.5


def test_output_path_recorded():
    report = BenchmarkRunner(FakeGenerator()).run(["red chair"])
    assert report.results[0].output_path.endswith("red_chair.obj")


def test_failure_message_recorded():
    report = BenchmarkRunner(FakeGenerator()).run(["broken prompt"])
    assert report.results[0].error == "Generation failed"


def test_elapsed_metrics():
    report = BenchmarkRunner(FakeGenerator()).run(["red chair"])
    assert report.results[0].elapsed_seconds >= 0
    assert report.average_seconds >= 0
    assert report.fastest_seconds >= 0
    assert report.slowest_seconds >= report.fastest_seconds


def test_report_saved_as_json(tmp_path):
    destination = tmp_path / "reports" / "benchmark.json"
    report = BenchmarkRunner(FakeGenerator()).run(
        ["red chair"], report_path=destination
    )

    data = json.loads(destination.read_text(encoding="utf-8"))
    assert data["total"] == 1
    assert data["successful"] == 1
    assert report.total == 1


def test_empty_prompt_list_rejected():
    with pytest.raises(ValueError):
        BenchmarkRunner(FakeGenerator()).run([])


def test_invalid_generator_rejected():
    with pytest.raises(TypeError):
        BenchmarkRunner(object())


def test_format_passed_to_generator():
    class FormatGenerator:
        def generate(self, prompt, file_format=None):
            assert file_format == "glb"
            return SimpleNamespace(output_path=Path("model.glb"))

    report = BenchmarkRunner(FormatGenerator()).run(
        ["red chair"], file_format="glb"
    )
    assert report.successful == 1
