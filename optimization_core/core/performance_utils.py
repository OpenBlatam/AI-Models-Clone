"""
Performance and profiling utilities for optimization_core.

Centralizes benchmarking, profiling, and optimization helpers that were
previously duplicated across multiple modules.
"""

from __future__ import annotations

import gc
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover - torch may be optional
    TORCH_AVAILABLE = False
    nn = None  # type: ignore

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:  # pragma: no cover - psutil may be optional
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ════════════════════════════════════════════════════════════════════════════════


@dataclass
class PerformanceMetrics:
    """Container for runtime performance metrics."""

    inference_time: float
    memory_usage: float
    throughput: float
    latency: float
    gpu_utilization: Optional[float] = None
    cpu_utilization: Optional[float] = None


@dataclass
class BenchmarkResult:
    """Result of a benchmarking session."""

    model_name: str
    metrics: PerformanceMetrics
    configuration: Dict[str, Any]
    timestamp: float


@dataclass
class FunctionCallStats:
    """Aggregated statistics for a function call."""

    call_count: int = 0
    total_time: float = 0.0
    min_time: float = field(default_factory=lambda: float("inf"))
    max_time: float = 0.0

    def add(self, duration: float) -> None:
        self.call_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)

    def to_dict(self) -> Dict[str, float]:
        if self.call_count == 0:
            return {}
        return {
            "call_count": self.call_count,
            "total_time": self.total_time,
            "avg_time": self.total_time / self.call_count,
            "min_time": 0.0 if self.min_time == float("inf") else self.min_time,
            "max_time": self.max_time,
        }


# ════════════════════════════════════════════════════════════════════════════════
# FUNCTION PROFILER
# ════════════════════════════════════════════════════════════════════════════════


class FunctionProfiler:
    """
    Lightweight profiler for counting function calls and aggregating durations.
    """

    def __init__(self) -> None:
        self._stats: Dict[str, FunctionCallStats] = {}

    def record_call(self, function_name: str, duration: float) -> None:
        if function_name not in self._stats:
            self._stats[function_name] = FunctionCallStats()
        self._stats[function_name].add(duration)

    def get_stats(self, function_name: str) -> Dict[str, float]:
        if function_name not in self._stats:
            return {}
        return self._stats[function_name].to_dict()

    def summary(self) -> Dict[str, Dict[str, float]]:
        return {name: stats.to_dict() for name, stats in self._stats.items()}

    def reset(self) -> None:
        self._stats.clear()


# ════════════════════════════════════════════════════════════════════════════════
# MODEL PROFILING & BENCHMARKING
# ════════════════════════════════════════════════════════════════════════════════


class PerformanceProfiler:
    """Profiler for measuring model-level performance metrics."""

    def __init__(self, device: Optional[Union[torch.device, str]] = None) -> None:
        if TORCH_AVAILABLE:
            if device is None:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            elif isinstance(device, str):
                device = torch.device(device)
        self.device = device if TORCH_AVAILABLE else None
        self.results: List[BenchmarkResult] = []

    def profile_model(
        self,
        model: nn.Module,
        input_shape: Tuple[int, ...],
        num_runs: int = 100,
        warmup_runs: int = 10,
        batch_size: int = 1,
    ) -> BenchmarkResult:
        if not TORCH_AVAILABLE:
            raise ImportError("torch is required for model profiling")

        model = model.to(self.device)
        model.eval()
        input_tensor = torch.randn(batch_size, *input_shape, device=self.device)

        with torch.no_grad():
            for _ in range(warmup_runs):
                _ = model(input_tensor)

        if self.device and self.device.type == "cuda":
            torch.cuda.synchronize()

        run_times: List[float] = []
        memory_usage: List[float] = []

        with torch.no_grad():
            for _ in range(num_runs):
                if self.device and self.device.type == "cuda":
                    torch.cuda.empty_cache()

                start_time = time.time()
                _ = model(input_tensor)
                if self.device and self.device.type == "cuda":
                    torch.cuda.synchronize()
                end_time = time.time()

                run_times.append(end_time - start_time)

                if self.device and self.device.type == "cuda":
                    memory_usage.append(torch.cuda.memory_allocated(self.device) / 1024 / 1024)
                elif PSUTIL_AVAILABLE:
                    memory_usage.append(psutil.Process().memory_info().rss / 1024 / 1024)
                else:
                    memory_usage.append(0.0)

        avg_time = sum(run_times) / len(run_times)
        avg_memory = sum(memory_usage) / len(memory_usage)
        throughput = (batch_size or 1) / avg_time
        latency = avg_time * 1000.0

        metrics = PerformanceMetrics(
            inference_time=avg_time,
            memory_usage=avg_memory,
            throughput=throughput,
            latency=latency,
        )

        result = BenchmarkResult(
            model_name=model.__class__.__name__,
            metrics=metrics,
            configuration={
                "input_shape": input_shape,
                "batch_size": batch_size,
                "num_runs": num_runs,
                "device": str(self.device),
            },
            timestamp=time.time(),
        )

        self.results.append(result)
        return result

    def compare_models(
        self,
        models: Dict[str, nn.Module],
        input_shape: Tuple[int, ...],
        num_runs: int = 100,
        warmup_runs: int = 10,
        batch_size: int = 1,
    ) -> Dict[str, BenchmarkResult]:
        return {
            name: self.profile_model(model, input_shape, num_runs, warmup_runs, batch_size)
            for name, model in models.items()
        }

    def summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}
        return {
            "total_benchmarks": len(self.results),
            "models_tested": sorted({r.model_name for r in self.results}),
            "average_inference_time": sum(r.metrics.inference_time for r in self.results) / len(self.results),
            "average_memory_usage": sum(r.metrics.memory_usage for r in self.results) / len(self.results),
            "average_throughput": sum(r.metrics.throughput for r in self.results) / len(self.results),
            "average_latency": sum(r.metrics.latency for r in self.results) / len(self.results),
        }


class TorchModelProfiler:
    """
    Wrapper around torch.profiler for collecting low-level traces.
    """

    def __init__(self, log_dir: Optional[Union[str, Path]] = None) -> None:
        if not TORCH_AVAILABLE:
            raise ImportError("torch is required for TorchModelProfiler")

        self.log_dir = Path(log_dir) if log_dir else None
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def profile(
        self,
        model: nn.Module,
        input_shape: Tuple[int, ...],
        num_runs: int = 10,
        warmup_runs: int = 3,
        activities: Optional[List["torch.profiler.ProfilerActivity"]] = None,
    ) -> Dict[str, Any]:
        if activities is None:
            activities = [
                torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA,
            ]

        dummy_input = torch.zeros(input_shape)
        if torch.cuda.is_available():
            dummy_input = dummy_input.cuda()
            model = model.cuda()

        model.eval()
        with torch.no_grad():
            for _ in range(warmup_runs):
                _ = model(dummy_input)

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        with torch.profiler.profile(activities=activities, record_shapes=True, profile_memory=True) as prof:
            with torch.no_grad():
                for _ in range(num_runs):
                    _ = model(dummy_input)
            if torch.cuda.is_available():
                torch.cuda.synchronize()

        if self.log_dir:
            prof.export_chrome_trace(str(self.log_dir / "trace.json"))

        key_averages = prof.key_averages()
        return {
            "cpu_time_total": sum(evt.cpu_time_total for evt in key_averages),
            "cuda_time_total": sum(evt.cuda_time_total for evt in key_averages)
            if torch.cuda.is_available()
            else 0,
            "cpu_memory_usage": sum(evt.cpu_memory_usage for evt in key_averages),
            "cuda_memory_usage": sum(evt.cuda_memory_usage for evt in key_averages)
            if torch.cuda.is_available()
            else 0,
        }


# ════════════════════════════════════════════════════════════════════════════════
# CONTEXT MANAGERS & DECORATORS
# ════════════════════════════════════════════════════════════════════════════════


@contextmanager
def profile_context(output_file: Optional[Union[str, Path]] = None, sort_by: str = "cumulative", lines: int = 50):
    """
    Context manager for cProfile-based profiling.
    """
    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()

    try:
        yield profiler
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats(sort_by)
        stats.print_stats(lines)

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            stats.dump_stats(str(output_path))
            logger.info("Profile saved to %s", output_path)


def profile_function(func: Callable, *args, output_file: Optional[Union[str, Path]] = None, **kwargs) -> Any:
    """
    Profile a standalone function call.
    """
    with profile_context(output_file=output_file):
        return func(*args, **kwargs)


def profile_decorator(output_file: Optional[Union[str, Path]] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator wrapper around ``profile_function``."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return profile_function(func, *args, output_file=output_file, **kwargs)

        return wrapper

    return decorator


@contextmanager
def profile_operation(operation_name: str, log: Optional[logging.Logger] = None):
    """General-purpose profiling context for arbitrary operations."""
    log = log or logger
    start_time = time.time()
    start_memory = (
        psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0.0
    )

    log.info("Starting operation: %s", operation_name)
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = (
            psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0.0
        )
        log.info("Completed operation: %s", operation_name)
        log.info("  Duration: %.4fs", end_time - start_time)
        if PSUTIL_AVAILABLE:
            log.info("  Memory delta: %.2f MB", end_memory - start_memory)


# ════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════


def benchmark_model(
    model: nn.Module,
    input_shape: Tuple[int, ...],
    num_runs: int = 100,
    warmup_runs: int = 10,
    batch_size: int = 1,
    device: Optional[Union[torch.device, str]] = None,
) -> BenchmarkResult:
    profiler = PerformanceProfiler(device)
    return profiler.profile_model(model, input_shape, num_runs, warmup_runs, batch_size)


def profile_model(
    model: nn.Module,
    input_shape: Tuple[int, ...],
    num_runs: int = 100,
    warmup_runs: int = 10,
    batch_size: int = 1,
    device: Optional[Union[torch.device, str]] = None,
) -> Dict[str, Any]:
    result = benchmark_model(model, input_shape, num_runs, warmup_runs, batch_size, device)
    return {
        "model_name": result.model_name,
        "inference_time": result.metrics.inference_time,
        "memory_usage": result.metrics.memory_usage,
        "throughput": result.metrics.throughput,
        "latency": result.metrics.latency,
        "configuration": result.configuration,
        "timestamp": result.timestamp,
    }


def optimize_model(
    model: nn.Module,
    optimization_level: str = "basic",
    device: Optional[Union[torch.device, str]] = None,
) -> nn.Module:
    if not TORCH_AVAILABLE:
        raise ImportError("torch is required for optimize_model")

    logger.info("Optimizing model with level: %s", optimization_level)
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elif isinstance(device, str):
        device = torch.device(device)

    model = model.to(device)
    model.eval()

    if optimization_level in {"basic", "advanced", "expert"} and device.type == "cuda":
        model = model.half()
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False

        if optimization_level == "expert":
            try:  # pragma: no cover - optional dependency
                import tensorrt  # noqa: F401

                logger.info("TensorRT optimization available")
            except ImportError:
                logger.info("TensorRT not available")

    logger.info("Model optimization completed: %s", optimization_level)
    return model


def create_optimization_report(
    results: Iterable[BenchmarkResult],
    output_file: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    entries = list(results)
    if not entries:
        return {}

    inference_times = [r.metrics.inference_time for r in entries]
    memory_usages = [r.metrics.memory_usage for r in entries]
    throughputs = [r.metrics.throughput for r in entries]
    latencies = [r.metrics.latency for r in entries]

    report = {
        "summary": {
            "total_benchmarks": len(entries),
            "models_tested": sorted({r.model_name for r in entries}),
            "time_range": f"{min(inference_times):.4f}s - {max(inference_times):.4f}s",
            "memory_range": f"{min(memory_usages):.2f}MB - {max(memory_usages):.2f}MB",
            "throughput_range": f"{min(throughputs):.2f} - {max(throughputs):.2f} samples/s",
            "latency_range": f"{min(latencies):.2f}ms - {max(latencies):.2f}ms",
        },
        "statistics": {
            "average_inference_time": sum(inference_times) / len(inference_times),
            "average_memory_usage": sum(memory_usages) / len(memory_usages),
            "average_throughput": sum(throughputs) / len(throughputs),
            "average_latency": sum(latencies) / len(latencies),
        },
        "results": [
            {
                "model_name": r.model_name,
                "inference_time": r.metrics.inference_time,
                "memory_usage": r.metrics.memory_usage,
                "throughput": r.metrics.throughput,
                "latency": r.metrics.latency,
                "configuration": r.configuration,
                "timestamp": r.timestamp,
            }
            for r in entries
        ],
    }

    if output_file:
        import json

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info("Optimization report saved to: %s", output_path)

    return report


def measure_memory_usage(func: Callable[..., Any], *args, **kwargs) -> Tuple[Any, float]:
    """Measure memory delta for a callable."""
    if not PSUTIL_AVAILABLE:
        result = func(*args, **kwargs)
        return result, 0.0

    process = psutil.Process()
    before = process.memory_info().rss / 1024 / 1024
    result = func(*args, **kwargs)
    after = process.memory_info().rss / 1024 / 1024
    return result, after - before


# ════════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ════════════════════════════════════════════════════════════════════════════════

__all__ = [
    "PerformanceMetrics",
    "BenchmarkResult",
    "FunctionProfiler",
    "PerformanceProfiler",
    "TorchModelProfiler",
    "profile_context",
    "profile_function",
    "profile_decorator",
    "profile_operation",
    "benchmark_model",
    "profile_model",
    "optimize_model",
    "create_optimization_report",
    "measure_memory_usage",
]












