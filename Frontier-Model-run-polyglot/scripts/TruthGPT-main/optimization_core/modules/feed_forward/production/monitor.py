"""
Production Monitoring & Error Handling for PiMoE System

System health monitoring, metrics collection, and circuit-breaker error handling.

Thread-safety: All counters use ``threading.Lock`` so they stay consistent
when mutated from the monitoring thread **and** the request hot-path.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Any, Dict, List

import psutil

from .config import ProductionConfig
from .logger import ProductionLogger


# ------------------------------------------------------------------
# Monitoring
# ------------------------------------------------------------------


class ProductionMonitor:
    """Production monitoring system.

    Runs a background daemon thread that periodically collects system
    and process metrics and evaluates health checks.
    """

    _MAX_STORED_METRICS: int = 1_000

    def __init__(
        self,
        config: ProductionConfig,
        logger: ProductionLogger,
    ) -> None:
        self.config = config
        self.logger = logger

        self._lock = threading.Lock()
        self._metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._health_status: str = "healthy"
        self._start_time: float = time.time()
        self._request_count: int = 0
        self._error_count: int = 0
        self._circuit_breaker_count: int = 0

        # Start monitoring thread
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="pimoe-monitor",
        )
        self._monitoring_thread.start()

    # ------------------------------------------------------------------
    # Internal loop
    # ------------------------------------------------------------------

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while True:
            try:
                self._collect_metrics()
                self._check_health()
                time.sleep(self.config.metrics_interval)
            except Exception as exc:
                self.logger.log_error("Monitoring loop error", exc)
                time.sleep(1.0)

    def _collect_metrics(self) -> None:
        """Collect system metrics."""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        try:
            disk = psutil.disk_usage("/")
        except OSError:
            # Fallback for Windows where "/" may not resolve
            disk = psutil.disk_usage("C:\\")

        process = psutil.Process()
        process_memory = process.memory_info()

        with self._lock:
            uptime = time.time() - self._start_time
            request_rate = self._request_count / uptime if uptime > 0 else 0.0
            error_rate = self._error_count / max(self._request_count, 1)

        metrics: Dict[str, Dict[str, Any]] = {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_mb": disk.free / (1024 * 1024),
            },
            "process": {
                "memory_rss_mb": process_memory.rss / (1024 * 1024),
                "memory_vms_mb": process_memory.vms / (1024 * 1024),
                "cpu_percent": process.cpu_percent(),
            },
            "application": {
                "uptime_seconds": uptime,
                "request_count": self._request_count,
                "error_count": self._error_count,
                "request_rate": request_rate,
                "error_rate": error_rate,
                "health_status": self._health_status,
            },
        }

        self.logger.log_metrics(metrics)

        # Store for analysis — keep only the most recent entries
        with self._lock:
            for key in ("system", "process", "application"):
                bucket = self._metrics[key]
                bucket.append(metrics[key])
                if len(bucket) > self._MAX_STORED_METRICS:
                    self._metrics[key] = bucket[-self._MAX_STORED_METRICS :]

    def _check_health(self) -> None:
        """Evaluate system health and update status."""
        memory = psutil.virtual_memory()
        memory_used_mb = (memory.total - memory.available) / (1024 * 1024)
        cpu_percent = psutil.cpu_percent()

        new_status = "healthy"

        if memory_used_mb > self.config.memory_threshold_mb:
            new_status = "unhealthy"
            self.logger.log_warning(
                f"High memory usage: {memory_used_mb:.0f} MB "
                f"(threshold {self.config.memory_threshold_mb:.0f} MB)",
            )

        if cpu_percent > self.config.cpu_threshold_percent:
            new_status = "unhealthy"
            self.logger.log_warning(
                f"High CPU usage: {cpu_percent}% "
                f"(threshold {self.config.cpu_threshold_percent}%)",
            )

        with self._lock:
            if self._circuit_breaker_count > self.config.circuit_breaker_threshold:
                new_status = "circuit_breaker_open"
                self.logger.log_error(
                    "Circuit breaker opened due to high error rate",
                )
            self._health_status = new_status

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_request(self, success: bool = True) -> None:
        """Record a request outcome (thread-safe)."""
        with self._lock:
            self._request_count += 1
            if not success:
                self._error_count += 1
                self._circuit_breaker_count += 1
            else:
                self._circuit_breaker_count = max(
                    0, self._circuit_breaker_count - 1
                )

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status (thread-safe snapshot)."""
        with self._lock:
            return {
                "status": self._health_status,
                "uptime": time.time() - self._start_time,
                "request_count": self._request_count,
                "error_count": self._error_count,
                "error_rate": self._error_count / max(self._request_count, 1),
                "circuit_breaker_count": self._circuit_breaker_count,
            }


# ------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------


class ProductionErrorHandler:
    """Production error handling system with circuit-breaker pattern.

    Tracks per-error-type counts with a 60-second rolling window.
    Returns ``True`` from :meth:`handle_error` when the caller
    should retry.
    """

    _RESET_WINDOW_SECONDS: float = 60.0

    def __init__(
        self,
        config: ProductionConfig,
        logger: ProductionLogger,
    ) -> None:
        self.config = config
        self.logger = logger
        self._lock = threading.Lock()
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._last_error_time: Dict[str, float] = defaultdict(float)

    def handle_error(self, error: Exception, context: str = "") -> bool:
        """Handle production errors.  Returns ``True`` if caller should retry."""
        error_type = type(error).__name__
        current_time = time.time()

        with self._lock:
            # Reset counter if > RESET_WINDOW since last occurrence
            if (
                current_time - self._last_error_time[error_type]
                > self._RESET_WINDOW_SECONDS
            ):
                self._error_counts[error_type] = 0

            self._error_counts[error_type] += 1
            self._last_error_time[error_type] = current_time
            count = self._error_counts[error_type]

        self.logger.log_error(
            f"Error in {context}" if context else f"Error ({error_type})",
            error,
            error_type=error_type,
            error_count=count,
        )

        return count <= self.config.max_retries

    def should_circuit_break(self) -> bool:
        """Check if circuit breaker should be opened."""
        with self._lock:
            total_errors = sum(self._error_counts.values())
        return total_errors > self.config.circuit_breaker_threshold
