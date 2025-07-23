"""
Monitoring System

Comprehensive monitoring for the cybersecurity toolkit.
"""

import asyncio
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, deque
import json

from .logging import SecurityLogger, LogContext, LogMetadata

# ============================================================================
# MONITORING TYPES
# ============================================================================

class MetricType(str, Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class AlertLevel(str, Enum):
    """Alert levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(str, Enum):
    """Alert channels."""
    LOG = "log"
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"

# ============================================================================
# PERFORMANCE MONITOR
# ============================================================================

@dataclass
class PerformanceMetric:
    """Performance metric data."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "metadata": self.metadata
        }

class PerformanceMonitor:
    """Performance monitoring system."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.summaries: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._lock = threading.Lock()
        self.logger = SecurityLogger("performance_monitor")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                     labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric."""
        with self._lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                metric_type=metric_type,
                labels=labels or {},
                metadata=metadata or {}
            )
            
            self.metrics[name].append(metric)
            
            # Update specific metric type storage
            if metric_type == MetricType.COUNTER:
                self.counters[name] += int(value)
            elif metric_type == MetricType.GAUGE:
                self.gauges[name] = value
            elif metric_type == MetricType.HISTOGRAM:
                self.histograms[name].append(value)
            elif metric_type == MetricType.SUMMARY:
                self._update_summary(name, value)
    
    def _update_summary(self, name: str, value: float) -> None:
        """Update summary statistics."""
        if name not in self.summaries:
            self.summaries[name] = {
                "count": 0,
                "sum": 0.0,
                "min": float('inf'),
                "max": float('-inf')
            }
        
        summary = self.summaries[name]
        summary["count"] += 1
        summary["sum"] += value
        summary["min"] = min(summary["min"], value)
        summary["max"] = max(summary["max"], value)
        summary["avg"] = summary["sum"] / summary["count"]
    
    def get_metric(self, name: str, window: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """Get metrics for a specific name within a time window."""
        with self._lock:
            if name not in self.metrics:
                return []
            
            metrics = list(self.metrics[name])
            
            if window:
                cutoff = datetime.now() - window
                metrics = [m for m in metrics if m.timestamp >= cutoff]
            
            return metrics
    
    def get_counter(self, name: str) -> int:
        """Get counter value."""
        with self._lock:
            return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value."""
        with self._lock:
            return self.gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        with self._lock:
            if name not in self.histograms or not self.histograms[name]:
                return {}
            
            values = self.histograms[name]
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std": statistics.stdev(values) if len(values) > 1 else 0.0
            }
    
    def get_summary(self, name: str) -> Dict[str, float]:
        """Get summary statistics."""
        with self._lock:
            return self.summaries.get(name, {}).copy()
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics data."""
        with self._lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {name: self.get_histogram_stats(name) for name in self.histograms},
                "summaries": dict(self.summaries)
            }
    
    def clear_metrics(self, name: Optional[str] = None) -> None:
        """Clear metrics."""
        with self._lock:
            if name:
                if name in self.metrics:
                    del self.metrics[name]
                if name in self.counters:
                    del self.counters[name]
                if name in self.gauges:
                    del self.gauges[name]
                if name in self.histograms:
                    del self.histograms[name]
                if name in self.summaries:
                    del self.summaries[name]
            else:
                self.metrics.clear()
                self.counters.clear()
                self.gauges.clear()
                self.histograms.clear()
                self.summaries.clear()

# ============================================================================
# HEALTH CHECKER
# ============================================================================

@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    check_function: Callable
    interval: float = 30.0  # seconds
    timeout: float = 10.0   # seconds
    critical: bool = False
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthStatus:
    """Health status information."""
    name: str
    status: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "duration": self.duration,
            "metadata": self.metadata
        }

class HealthChecker:
    """Health checking system."""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, HealthStatus] = {}
        self.running = False
        self._lock = threading.Lock()
        self.logger = SecurityLogger("health_checker")
    
    def add_health_check(self, name: str, check_function: Callable, 
                        interval: float = 30.0, timeout: float = 10.0,
                        critical: bool = False, dependencies: Optional[List[str]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a health check."""
        with self._lock:
            self.health_checks[name] = HealthCheck(
                name=name,
                check_function=check_function,
                interval=interval,
                timeout=timeout,
                critical=critical,
                dependencies=dependencies or [],
                metadata=metadata or {}
            )
    
    def remove_health_check(self, name: str) -> None:
        """Remove a health check."""
        with self._lock:
            if name in self.health_checks:
                del self.health_checks[name]
            if name in self.health_status:
                del self.health_status[name]
    
    async def run_health_check(self, health_check: HealthCheck) -> HealthStatus:
        """Run a single health check."""
        start_time = time.time()
        
        try:
            # Check dependencies first
            for dep in health_check.dependencies:
                if dep in self.health_status:
                    dep_status = self.health_status[dep]
                    if dep_status.status != "healthy":
                        return HealthStatus(
                            name=health_check.name,
                            status="unhealthy",
                            message=f"Dependency '{dep}' is {dep_status.status}",
                            duration=time.time() - start_time,
                            metadata=health_check.metadata
                        )
            
            # Run the health check
            if asyncio.iscoroutinefunction(health_check.check_function):
                result = await asyncio.wait_for(
                    health_check.check_function(),
                    timeout=health_check.timeout
                )
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, health_check.check_function
                )
            
            duration = time.time() - start_time
            
            if result is True or (isinstance(result, dict) and result.get("healthy", False)):
                status = "healthy"
                message = "Health check passed"
                if isinstance(result, dict):
                    message = result.get("message", message)
            else:
                status = "unhealthy"
                message = str(result) if result else "Health check failed"
            
            return HealthStatus(
                name=health_check.name,
                status=status,
                message=message,
                duration=duration,
                metadata=health_check.metadata
            )
        
        except asyncio.TimeoutError:
            return HealthStatus(
                name=health_check.name,
                status="unhealthy",
                message=f"Health check timed out after {health_check.timeout}s",
                duration=health_check.timeout,
                metadata=health_check.metadata
            )
        except Exception as e:
            return HealthStatus(
                name=health_check.name,
                status="unhealthy",
                message=f"Health check failed with exception: {e}",
                duration=time.time() - start_time,
                metadata=health_check.metadata
            )
    
    async def run_all_health_checks(self) -> Dict[str, HealthStatus]:
        """Run all health checks."""
        with self._lock:
            checks = list(self.health_checks.values())
        
        results = {}
        tasks = []
        
        for check in checks:
            task = asyncio.create_task(self.run_health_check(check))
            tasks.append((check.name, task))
        
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
                
                with self._lock:
                    self.health_status[name] = result
                
                # Log health check result
                if result.status == "healthy":
                    self.logger.info(f"Health check '{name}' passed", metadata=LogMetadata(
                        category="health_check",
                        tags=["health_check", "passed"]
                    ))
                else:
                    self.logger.warning(f"Health check '{name}' failed: {result.message}", metadata=LogMetadata(
                        category="health_check",
                        tags=["health_check", "failed"]
                    ))
            
            except Exception as e:
                self.logger.error(f"Health check '{name}' error: {e}", metadata=LogMetadata(
                    category="health_check",
                    tags=["health_check", "error"]
                ))
        
        return results
    
    def get_health_status(self, name: Optional[str] = None) -> Union[HealthStatus, Dict[str, HealthStatus]]:
        """Get health status."""
        with self._lock:
            if name:
                return self.health_status.get(name)
            else:
                return dict(self.health_status)
    
    def get_overall_health(self) -> str:
        """Get overall health status."""
        with self._lock:
            if not self.health_status:
                return "unknown"
            
            statuses = [status.status for status in self.health_status.values()]
            
            if "unhealthy" in statuses:
                return "unhealthy"
            elif "degraded" in statuses:
                return "degraded"
            else:
                return "healthy"
    
    async def start_monitoring(self) -> None:
        """Start health check monitoring."""
        self.running = True
        self.logger.info("Health check monitoring started")
        
        while self.running:
            try:
                await self.run_all_health_checks()
                
                # Wait for next check cycle
                await asyncio.sleep(30)  # Default interval
            except Exception as e:
                self.logger.error(f"Health check monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    def stop_monitoring(self) -> None:
        """Stop health check monitoring."""
        self.running = False
        self.logger.info("Health check monitoring stopped")

# ============================================================================
# METRICS COLLECTOR
# ============================================================================

class MetricsCollector:
    """System metrics collector."""
    
    def __init__(self, collection_interval: float = 60.0):
        self.collection_interval = collection_interval
        self.running = False
        self.monitor = PerformanceMonitor()
        self.logger = SecurityLogger("metrics_collector")
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            metrics = {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "process": {
                    "memory_rss": process_memory.rss,
                    "memory_vms": process_memory.vms,
                    "cpu_percent": process_cpu
                }
            }
            
            # Record metrics
            self.monitor.record_metric("cpu_percent", cpu_percent, MetricType.GAUGE)
            self.monitor.record_metric("memory_percent", memory.percent, MetricType.GAUGE)
            self.monitor.record_metric("disk_percent", metrics["disk"]["percent"], MetricType.GAUGE)
            self.monitor.record_metric("process_memory_rss", process_memory.rss, MetricType.GAUGE)
            self.monitor.record_metric("process_cpu_percent", process_cpu, MetricType.GAUGE)
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    async def start_collection(self) -> None:
        """Start metrics collection."""
        self.running = True
        self.logger.info("Metrics collection started")
        
        while self.running:
            try:
                await self.collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)
    
    def stop_collection(self) -> None:
        """Stop metrics collection."""
        self.running = False
        self.logger.info("Metrics collection stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return self.monitor.get_all_metrics()

# ============================================================================
# ALERT MANAGER
# ============================================================================

@dataclass
class Alert:
    """Alert definition."""
    id: str
    title: str
    message: str
    level: AlertLevel
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metadata": self.metadata
        }

class AlertManager:
    """Alert management system."""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_handlers: Dict[AlertChannel, Callable] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.max_alerts = 1000
        self.logger = SecurityLogger("alert_manager")
    
    def add_alert_handler(self, channel: AlertChannel, handler: Callable) -> None:
        """Add an alert handler."""
        self.alert_handlers[channel] = handler
    
    def add_alert_rule(self, name: str, condition: Callable, level: AlertLevel,
                      channels: List[AlertChannel], **kwargs) -> None:
        """Add an alert rule."""
        self.alert_rules[name] = {
            "condition": condition,
            "level": level,
            "channels": channels,
            **kwargs
        }
    
    def create_alert(self, title: str, message: str, level: AlertLevel = AlertLevel.INFO,
                    source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """Create and send an alert."""
        alert = Alert(
            id=f"alert_{int(time.time())}_{len(self.alerts)}",
            title=title,
            message=message,
            level=level,
            source=source,
            metadata=metadata or {}
        )
        
        # Add to alerts list
        self.alerts.append(alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)
        
        # Send to handlers
        self._send_alert(alert)
        
        # Log alert
        self.logger.security_event(
            "alert_created",
            f"Alert '{alert.title}' created",
            alert.level.value,
            metadata=LogMetadata(
                category="alert",
                tags=["alert", alert.level.value],
                custom_fields=alert.metadata
            )
        )
        
        return alert
    
    def _send_alert(self, alert: Alert) -> None:
        """Send alert to all configured channels."""
        for channel, handler in self.alert_handlers.items():
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error sending alert to {channel}: {e}")
    
    def get_alerts(self, level: Optional[AlertLevel] = None, 
                  since: Optional[datetime] = None) -> List[Alert]:
        """Get alerts with optional filtering."""
        alerts = self.alerts
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if since:
            alerts = [a for a in alerts if a.timestamp >= since]
        
        return alerts
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
        self.logger.info("All alerts cleared")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def track_performance(operation: str, **kwargs):
    """Decorator for tracking performance."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_success", 1, MetricType.COUNTER)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_errors", 1, MetricType.COUNTER)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_success", 1, MetricType.COUNTER)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_errors", 1, MetricType.COUNTER)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def check_health(name: str, check_function: Callable, **kwargs):
    """Decorator for health checks."""
    def decorator(func):
        checker = HealthChecker()
        checker.add_health_check(name, check_function, **kwargs)
        return func
    return decorator

def collect_metrics(interval: float = 60.0):
    """Decorator for metrics collection."""
    def decorator(func):
        collector = MetricsCollector(interval)
        return func
    return decorator

def send_alert(title: str, message: str, level: AlertLevel = AlertLevel.INFO, **kwargs):
    """Send an alert."""
    manager = AlertManager()
    return manager.create_alert(title, message, level, **kwargs)

def monitor_operation(operation: str, **kwargs):
    """Decorator for comprehensive operation monitoring."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record performance metrics
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_success", 1, MetricType.COUNTER)
                
                # Check for performance alerts
                if duration > 5.0:  # Alert if operation takes more than 5 seconds
                    send_alert(
                        f"Slow Operation: {operation}",
                        f"Operation '{operation}' took {duration:.2f} seconds",
                        AlertLevel.WARNING,
                        metadata={"operation": operation, "duration": duration}
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_errors", 1, MetricType.COUNTER)
                
                # Send error alert
                send_alert(
                    f"Operation Failed: {operation}",
                    f"Operation '{operation}' failed: {e}",
                    AlertLevel.ERROR,
                    metadata={"operation": operation, "error": str(e)}
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record performance metrics
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_success", 1, MetricType.COUNTER)
                
                # Check for performance alerts
                if duration > 5.0:
                    send_alert(
                        f"Slow Operation: {operation}",
                        f"Operation '{operation}' took {duration:.2f} seconds",
                        AlertLevel.WARNING,
                        metadata={"operation": operation, "duration": duration}
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                monitor.record_metric(f"{operation}_duration", duration, MetricType.HISTOGRAM)
                monitor.record_metric(f"{operation}_errors", 1, MetricType.COUNTER)
                
                # Send error alert
                send_alert(
                    f"Operation Failed: {operation}",
                    f"Operation '{operation}' failed: {e}",
                    AlertLevel.ERROR,
                    metadata={"operation": operation, "error": str(e)}
                )
                
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# ============================================================================
# IMPORTS FOR DECORATORS
# ============================================================================

import functools 