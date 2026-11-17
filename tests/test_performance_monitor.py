import time
import pytest

from ai_generation.performance_monitor import PerformanceMonitor


def test_monitor_starts():
    monitor = PerformanceMonitor()
    monitor.start()

    assert monitor.is_running
    monitor.stop()


def test_monitor_measures_elapsed_time():
    monitor = PerformanceMonitor()
    monitor.start()
    time.sleep(0.02)

    metrics = monitor.stop()

    assert metrics.elapsed_seconds >= 0.01


def test_monitor_records_memory_usage():
    monitor = PerformanceMonitor()
    monitor.start()

    data = bytearray(1024 * 100)
    metrics = monitor.stop()

    assert metrics.peak_memory_mb > 0
    assert len(data) == 1024 * 100


def test_successful_operation_is_recorded():
    monitor = PerformanceMonitor()
    monitor.start()

    metrics = monitor.stop()

    assert metrics.success is True
    assert metrics.error is None


def test_failed_operation_is_recorded():
    monitor = PerformanceMonitor()
    monitor.start()

    metrics = monitor.stop(error=ValueError("Generation failed"))

    assert metrics.success is False
    assert metrics.error == "Generation failed"


def test_double_start_is_rejected():
    monitor = PerformanceMonitor()
    monitor.start()

    with pytest.raises(RuntimeError):
        monitor.start()

    monitor.stop()


def test_stop_before_start_is_rejected():
    monitor = PerformanceMonitor()

    with pytest.raises(RuntimeError):
        monitor.stop()


def test_monitor_can_be_reused():
    monitor = PerformanceMonitor()

    first = monitor.start().stop()
    second = monitor.start().stop()

    assert first is not second
    assert monitor.is_running is False


def test_context_manager_records_metrics():
    with PerformanceMonitor() as monitor:
        values = [number * 2 for number in range(100)]

    assert len(values) == 100
    assert monitor.metrics.success is True


def test_context_manager_records_errors():
    monitor = PerformanceMonitor()

    with pytest.raises(ValueError):
        with monitor:
            raise ValueError("Test failure")

    assert monitor.metrics.success is False
    assert monitor.metrics.error == "Test failure"


def test_metrics_can_be_converted_to_dict():
    monitor = PerformanceMonitor()
    monitor.start()
    metrics = monitor.stop()

    data = metrics.to_dict()

    assert "elapsed_seconds" in data
    assert "peak_memory_mb" in data
    assert "success" in data
