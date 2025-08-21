"""
Metrics and performance monitoring utilities for the Blaze AI module.

This module provides utilities for timing operations, tracking performance metrics,
and monitoring system health.
"""

from __future__ import annotations

import time
import threading
from contextlib import contextmanager
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import psutil
import os


@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Timer:
    """
    High-precision timer for measuring execution time.
    
    Features:
    - Context manager support
    - High-precision timing
    - Automatic start/stop
    - Multiple timing modes
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed: Optional[float] = None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.perf_counter()
        self.end_time = None
        self.elapsed = None
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time."""
        if self.start_time is None:
            raise RuntimeError("Timer not started")
        
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        return self.elapsed
    
    def reset(self) -> None:
        """Reset the timer."""
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    @property
    def is_running(self) -> bool:
        """Check if timer is currently running."""
        return self.start_time is not None and self.end_time is None


class MetricsCollector:
    """
    Collects and manages performance metrics.
    
    Features:
    - Automatic metric collection
    - Statistical analysis
    - Rolling windows
    - Thread-safe operations
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._lock = threading.RLock()
    
    def record(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value."""
        with self._lock:
            metric_point = MetricPoint(
                name=name,
                value=value,
                timestamp=time.time(),
                tags=tags or {}
            )
            self._metrics[name].append(metric_point)
    
    def get_metric(self, name: str) -> List[MetricPoint]:
        """Get all recorded values for a metric."""
        with self._lock:
            return list(self._metrics.get(name, []))
    
    def get_statistics(self, name: str, window_seconds: Optional[float] = None) -> Dict[str, float]:
        """Get statistical summary for a metric."""
        with self._lock:
            points = self._metrics.get(name, [])
            
            if window_seconds:
                cutoff_time = time.time() - window_seconds
                points = [p for p in points if p.timestamp >= cutoff_time]
            
            if not points:
                return {}
            
            values = [p.value for p in points]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0,
                "latest": values[-1] if values else 0.0
            }
    
    def get_all_metrics(self) -> Dict[str, List[MetricPoint]]:
        """Get all recorded metrics."""
        with self._lock:
            return {name: list(points) for name, points in self._metrics.items()}
    
    def clear(self, name: Optional[str] = None) -> None:
        """Clear metrics."""
        with self._lock:
            if name:
                self._metrics[name].clear()
            else:
                self._metrics.clear()


class PerformanceMonitor:
    """
    System performance monitoring.
    
    Features:
    - CPU and memory monitoring
    - Process-specific metrics
    - Automatic background monitoring
    - Alerting capabilities
    """
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.metrics_collector = MetricsCollector()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def start_monitoring(self) -> None:
        """Start background performance monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop background performance monitoring."""
        if not self._monitoring:
            return
        
        self._monitoring = False
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join()
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while not self._stop_event.is_set():
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                self.metrics_collector.record("cpu_percent", cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.metrics_collector.record("memory_percent", memory.percent)
                self.metrics_collector.record("memory_available_gb", memory.available / (1024**3))
                
                # Process-specific metrics
                process = psutil.Process()
                self.metrics_collector.record("process_cpu_percent", process.cpu_percent())
                self.metrics_collector.record("process_memory_mb", process.memory_info().rss / (1024**2))
                
                # Disk usage
                disk = psutil.disk_usage('/')
                self.metrics_collector.record("disk_percent", disk.percent)
                
            except Exception:
                # Continue monitoring even if some metrics fail
                pass
            
            # Wait for next interval or stop signal
            if self._stop_event.wait(self.interval):
                break
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Process
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "percent": disk.percent
                },
                "process": {
                    "cpu_percent": process.cpu_percent(),
                    "memory_mb": process_memory.rss / (1024**2),
                    "threads": process.num_threads()
                }
            }
        except Exception as e:
            return {"error": str(e)}


class MetricsRegistry:
    """
    Global metrics registry for the application.
    
    Features:
    - Centralized metric collection
    - Automatic aggregation
    - Export capabilities
    - Integration with monitoring systems
    """
    
    def __init__(self):
        self.collector = MetricsCollector()
        self.monitor = PerformanceMonitor()
        self._custom_metrics: Dict[str, Callable] = {}
    
    def register_custom_metric(self, name: str, collector: Callable[[], float]) -> None:
        """Register a custom metric collector function."""
        self._custom_metrics[name] = collector
    
    def collect_custom_metrics(self) -> None:
        """Collect all registered custom metrics."""
        for name, collector in self._custom_metrics.items():
            try:
                value = collector()
                self.collector.record(name, value)
            except Exception:
                # Continue collecting other metrics if one fails
                pass
    
    def get_summary(self, window_seconds: Optional[float] = None) -> Dict[str, Any]:
        """Get a comprehensive metrics summary."""
        summary = {
            "system": self.monitor.get_system_stats(),
            "metrics": {}
        }
        
        # Get statistics for all recorded metrics
        for metric_name in self.collector._metrics.keys():
            stats = self.collector.get_statistics(metric_name, window_seconds)
            if stats:
                summary["metrics"][metric_name] = stats
        
        return summary
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for metric_name, points in self.collector.get_all_metrics().items():
            if not points:
                continue
            
            # Get latest value
            latest = points[-1]
            
            # Format metric name
            prometheus_name = metric_name.replace('.', '_').replace('-', '_')
            
            # Format tags
            tags_str = ""
            if latest.tags:
                tag_pairs = [f'{k}="{v}"' for k, v in latest.tags.items()]
                tags_str = "{" + ",".join(tag_pairs) + "}"
            
            # Add metric line
            lines.append(f"{prometheus_name}{tags_str} {latest.value}")
        
        return "\n".join(lines)


# Global metrics registry instance
_global_registry: Optional[MetricsRegistry] = None

def get_metrics_registry() -> MetricsRegistry:
    """Get the global metrics registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = MetricsRegistry()
    return _global_registry


@contextmanager
def timed_operation(name: str, tags: Optional[Dict[str, str]] = None):
    """
    Context manager for timing operations and automatically recording metrics.
    
    Args:
        name: Name of the operation
        tags: Optional tags for the metric
    """
    registry = get_metrics_registry()
    with Timer() as timer:
        yield timer
    
    registry.collector.record(f"{name}_duration", timer.elapsed or 0.0, tags)


def record_metric(name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
    """Record a metric value in the global registry."""
    registry = get_metrics_registry()
    registry.collector.record(name, value, tags)


# Export main classes and functions
__all__ = [
    "Timer",
    "MetricsCollector", 
    "PerformanceMonitor",
    "MetricsRegistry",
    "get_metrics_registry",
    "timed_operation",
    "record_metric"
]


