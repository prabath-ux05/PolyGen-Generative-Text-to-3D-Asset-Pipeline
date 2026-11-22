"""Measure execution time and Python memory usage."""

from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
import tracemalloc


@dataclass(frozen=True)
class PerformanceMetrics:
    """Store measurements from one monitored operation."""

    elapsed_seconds: float
    peak_memory_mb: float
    success: bool
    error: str | None
    started_at: str
    finished_at: str

    def to_dict(self):
        """Convert metrics into a dictionary."""
        return {
            "elapsed_seconds": self.elapsed_seconds,
            "peak_memory_mb": self.peak_memory_mb,
            "success": self.success,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


class PerformanceMonitor:
    """Track elapsed time and Python memory allocations."""

    def __init__(self):
        self._start_time = None
        self._started_at = None
        self._owns_tracing = False
        self.metrics = None

    @property
    def is_running(self):
        """Return whether monitoring is currently active."""
        return self._start_time is not None

    def start(self):
        """Start measuring time and memory."""
        if self.is_running:
            raise RuntimeError("Performance monitor is already running")

        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self._owns_tracing = True
        else:
            self._owns_tracing = False
            tracemalloc.reset_peak()

        self._start_time = perf_counter()
        self._started_at = datetime.now(timezone.utc).isoformat()
        self.metrics = None

        return self

    def stop(self, error=None):
        """Stop monitoring and return the collected metrics."""
        if not self.is_running:
            raise RuntimeError("Performance monitor has not been started")

        elapsed = perf_counter() - self._start_time
        _, peak_bytes = tracemalloc.get_traced_memory()

        finished_at = datetime.now(timezone.utc).isoformat()

        if self._owns_tracing:
            tracemalloc.stop()

        self.metrics = PerformanceMetrics(
            elapsed_seconds=elapsed,
            peak_memory_mb=peak_bytes / (1024 * 1024),
            success=error is None,
            error=str(error) if error is not None else None,
            started_at=self._started_at,
            finished_at=finished_at,
        )

        self._start_time = None
        self._started_at = None
        self._owns_tracing = False

        return self.metrics

    def __enter__(self):
        """Start monitoring when entering a with block."""
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop monitoring when leaving a with block."""
        self.stop(error=exc_value)
        return False
