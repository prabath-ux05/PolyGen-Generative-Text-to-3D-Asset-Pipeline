"""Run repeatable prompt benchmarks against the generation pipeline."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Optional


@dataclass(frozen=True)
class BenchmarkCaseResult:
    """Store the result of one benchmark prompt."""

    prompt: str
    success: bool
    elapsed_seconds: float
    output_path: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkReport:
    """Summarize a complete benchmark run."""

    total: int
    successful: int
    failed: int
    average_seconds: float
    fastest_seconds: float
    slowest_seconds: float
    created_at: str
    results: tuple

    @property
    def success_rate(self):
        return self.successful / self.total if self.total else 0.0

    def to_dict(self):
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "average_seconds": self.average_seconds,
            "fastest_seconds": self.fastest_seconds,
            "slowest_seconds": self.slowest_seconds,
            "created_at": self.created_at,
            "results": [item.to_dict() for item in self.results],
        }

    def save(self, file_path):
        """Save benchmark results as JSON."""

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(self.to_dict(), indent=4),
            encoding="utf-8",
        )

        return path


class BenchmarkRunner:
    """Measure pipeline execution across a collection of prompts."""

    def __init__(self, generator):
        if not callable(getattr(generator, "generate", None)):
            raise TypeError("Generator must provide a generate method")

        self.generator = generator

    def run(self, prompts, file_format=None, report_path=None):
        """Execute each prompt and return an aggregate report."""

        prompt_list = list(prompts)

        if not prompt_list:
            raise ValueError("At least one benchmark prompt is required")

        results = []

        for prompt in prompt_list:
            start = perf_counter()

            try:
                generated = self.generator.generate(
                    prompt,
                    file_format=file_format,
                )

                elapsed = perf_counter() - start

                results.append(
                    BenchmarkCaseResult(
                        prompt=str(prompt),
                        success=True,
                        elapsed_seconds=elapsed,
                        output_path=str(generated.output_path),
                    )
                )

            except Exception as exc:
                elapsed = perf_counter() - start
                code = getattr(exc, "code", None)

                if hasattr(code, "value"):
                    code = code.value

                results.append(
                    BenchmarkCaseResult(
                        prompt=str(prompt),
                        success=False,
                        elapsed_seconds=elapsed,
                        error=str(exc),
                        error_code=str(code) if code is not None else None,
                    )
                )

        durations = [item.elapsed_seconds for item in results]
        successful = sum(item.success for item in results)

        report = BenchmarkReport(
            total=len(results),
            successful=successful,
            failed=len(results) - successful,
            average_seconds=sum(durations) / len(durations),
            fastest_seconds=min(durations),
            slowest_seconds=max(durations),
            created_at=datetime.now(timezone.utc).isoformat(),
            results=tuple(results),
        )

        if report_path is not None:
            report.save(report_path)

        return report
