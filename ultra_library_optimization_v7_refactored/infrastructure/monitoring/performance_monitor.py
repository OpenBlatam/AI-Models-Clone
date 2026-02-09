#!/usr/bin/env python3
"""
Advanced Performance Monitor - Infrastructure Layer
================================================

Enterprise-grade performance monitoring with APM capabilities,
distributed tracing, and real-time metrics collection.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type
from contextlib import asynccontextmanager
import threading
import weakref
import json
import statistics


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class TraceStatus(Enum):
    """Status of distributed traces."""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class Metric:
    """Base metric class."""
    
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
    unit: Optional[str] = None


@dataclass
class TraceSpan:
    """Distributed trace span."""
    
    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    name: str
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: TraceStatus = TraceStatus.STARTED
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class PerformanceAlert:
    """Performance alert configuration."""
    
    alert_id: str
    name: str
    metric_name: str
    threshold: float
    operator: str  # >, <, >=, <=, ==
    duration: timedelta
    severity: str  # low, medium, high, critical
    enabled: bool = True
    description: Optional[str] = None
    notification_channels: List[str] = field(default_factory=list)


class MetricsCollector:
    """Advanced metrics collection with aggregation and storage."""
    
    def __init__(self):
        self._metrics: Dict[str, List[Metric]] = {}
        self._aggregations: Dict[str, Dict[str, float]] = {}
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        
        # Performance thresholds
        self._thresholds = {
            'response_time_ms': 1000.0,
            'error_rate': 0.05,
            'throughput_rps': 100.0,
            'memory_usage_mb': 1024.0,
            'cpu_usage_percent': 80.0
        }
    
    def record_metric(self, metric: Metric) -> None:
        """Record a new metric."""
        with self._lock:
            if metric.name not in self._metrics:
                self._metrics[metric.name] = []
            
            self._metrics[metric.name].append(metric)
            
            # Update aggregations
            self._update_aggregations(metric.name)
    
    def record_counter(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record a counter metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            labels=labels or {}
        )
        self.record_metric(metric)
    
    def record_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record a gauge metric."""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels or {}
        )
        self.record_metric(metric)
    
    def record_timer(self, name: str, duration_ms: float, labels: Dict[str, str] = None) -> None:
        """Record a timer metric."""
        metric = Metric(
            name=name,
            value=duration_ms,
            metric_type=MetricType.TIMER,
            labels=labels or {},
            unit="ms"
        )
        self.record_metric(metric)
    
    def get_metric(self, name: str, window_minutes: int = 60) -> Optional[Metric]:
        """Get the latest metric for a given name."""
        with self._lock:
            if name not in self._metrics:
                return None
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            recent_metrics = [
                m for m in self._metrics[name]
                if m.timestamp > cutoff_time
            ]
            
            return recent_metrics[-1] if recent_metrics else None
    
    def get_aggregation(self, name: str, aggregation: str = "avg") -> Optional[float]:
        """Get aggregated metric value."""
        with self._lock:
            if name not in self._aggregations:
                return None
            
            return self._aggregations[name].get(aggregation)
    
    def get_metrics_summary(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary of all metrics in the time window."""
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            summary = {}
            
            for name, metrics in self._metrics.items():
                recent_metrics = [
                    m for m in metrics
                    if m.timestamp > cutoff_time
                ]
                
                if recent_metrics:
                    values = [m.value for m in recent_metrics]
                    summary[name] = {
                        'count': len(recent_metrics),
                        'min': min(values),
                        'max': max(values),
                        'avg': statistics.mean(values),
                        'median': statistics.median(values),
                        'latest': recent_metrics[-1].value,
                        'latest_timestamp': recent_metrics[-1].timestamp.isoformat()
                    }
            
            return summary
    
    def _update_aggregations(self, metric_name: str) -> None:
        """Update aggregations for a metric."""
        if metric_name not in self._metrics:
            return
        
        metrics = self._metrics[metric_name]
        values = [m.value for m in metrics]
        
        self._aggregations[metric_name] = {
            'count': len(values),
            'sum': sum(values),
            'avg': statistics.mean(values) if values else 0,
            'min': min(values) if values else 0,
            'max': max(values) if values else 0,
            'median': statistics.median(values) if values else 0
        }


class DistributedTracer:
    """Distributed tracing implementation."""
    
    def __init__(self):
        self._traces: Dict[str, List[TraceSpan]] = {}
        self._active_spans: Dict[str, TraceSpan] = {}
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
    
    def start_trace(self, trace_id: str, span_name: str, 
                   parent_span_id: Optional[str] = None) -> str:
        """Start a new trace span."""
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=span_name
        )
        
        with self._lock:
            if trace_id not in self._traces:
                self._traces[trace_id] = []
            
            self._traces[trace_id].append(span)
            self._active_spans[span_id] = span
        
        self._logger.debug(f"Started span {span_id} in trace {trace_id}")
        return span_id
    
    def end_span(self, span_id: str, status: TraceStatus = TraceStatus.COMPLETED,
                 error: Optional[str] = None) -> None:
        """End a trace span."""
        with self._lock:
            if span_id not in self._active_spans:
                self._logger.warning(f"Attempted to end non-existent span: {span_id}")
                return
            
            span = self._active_spans[span_id]
            span.end_time = datetime.utcnow()
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            span.error = error
            
            del self._active_spans[span_id]
        
        self._logger.debug(f"Ended span {span_id} with status {status}")
    
    def add_span_tag(self, span_id: str, key: str, value: str) -> None:
        """Add a tag to a span."""
        with self._lock:
            if span_id in self._active_spans:
                self._active_spans[span_id].tags[key] = value
    
    def add_span_log(self, span_id: str, message: str, level: str = "info",
                     **kwargs) -> None:
        """Add a log entry to a span."""
        with self._lock:
            if span_id in self._active_spans:
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': level,
                    'message': message,
                    **kwargs
                }
                self._active_spans[span_id].logs.append(log_entry)
    
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace."""
        with self._lock:
            return self._traces.get(trace_id, [])
    
    def get_active_spans(self) -> List[TraceSpan]:
        """Get all currently active spans."""
        with self._lock:
            return list(self._active_spans.values())


class PerformanceAlertManager:
    """Advanced performance alert management."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self._alerts: Dict[str, PerformanceAlert] = {}
        self._alert_history: List[Dict[str, Any]] = []
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
    
    def add_alert(self, alert: PerformanceAlert) -> None:
        """Add a new performance alert."""
        with self._lock:
            self._alerts[alert.alert_id] = alert
            self._logger.info(f"Added performance alert: {alert.name}")
    
    def remove_alert(self, alert_id: str) -> None:
        """Remove a performance alert."""
        with self._lock:
            if alert_id in self._alerts:
                del self._alerts[alert_id]
                self._logger.info(f"Removed performance alert: {alert_id}")
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all alerts and return triggered ones."""
        triggered_alerts = []
        
        with self._lock:
            for alert in self._alerts.values():
                if not alert.enabled:
                    continue
                
                # Get current metric value
                metric = self.metrics_collector.get_metric(alert.metric_name)
                if not metric:
                    continue
                
                # Check if alert should be triggered
                should_trigger = self._evaluate_alert(alert, metric.value)
                
                if should_trigger:
                    alert_event = {
                        'alert_id': alert.alert_id,
                        'name': alert.name,
                        'metric_name': alert.metric_name,
                        'current_value': metric.value,
                        'threshold': alert.threshold,
                        'severity': alert.severity,
                        'timestamp': datetime.utcnow().isoformat(),
                        'description': alert.description
                    }
                    
                    triggered_alerts.append(alert_event)
                    self._alert_history.append(alert_event)
                    
                    self._logger.warning(
                        f"Performance alert triggered: {alert.name} "
                        f"({alert.metric_name}: {metric.value} {alert.operator} {alert.threshold})"
                    )
        
        return triggered_alerts
    
    def _evaluate_alert(self, alert: PerformanceAlert, value: float) -> bool:
        """Evaluate if an alert should be triggered."""
        if alert.operator == ">":
            return value > alert.threshold
        elif alert.operator == "<":
            return value < alert.threshold
        elif alert.operator == ">=":
            return value >= alert.threshold
        elif alert.operator == "<=":
            return value <= alert.threshold
        elif alert.operator == "==":
            return value == alert.threshold
        else:
            self._logger.error(f"Unknown alert operator: {alert.operator}")
            return False
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            return [
                alert for alert in self._alert_history
                if datetime.fromisoformat(alert['timestamp']) > cutoff_time
            ]


class PerformanceMonitor:
    """
    Advanced performance monitoring system with APM capabilities.
    
    Features:
    - Real-time metrics collection and aggregation
    - Distributed tracing with spans and tags
    - Performance alerts with configurable thresholds
    - Memory and CPU monitoring
    - Request/response timing
    - Error rate tracking
    - Throughput monitoring
    - Custom metric recording
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.distributed_tracer = DistributedTracer()
        self.alert_manager = PerformanceAlertManager(self.metrics_collector)
        self._logger = logging.getLogger(__name__)
        self._start_time = datetime.utcnow()
        
        # Initialize default alerts
        self._initialize_default_alerts()
    
    def _initialize_default_alerts(self) -> None:
        """Initialize default performance alerts."""
        default_alerts = [
            PerformanceAlert(
                alert_id="high_response_time",
                name="High Response Time",
                metric_name="response_time_ms",
                threshold=1000.0,
                operator=">",
                duration=timedelta(minutes=5),
                severity="high",
                description="Response time exceeds 1 second"
            ),
            PerformanceAlert(
                alert_id="high_error_rate",
                name="High Error Rate",
                metric_name="error_rate",
                threshold=0.05,
                operator=">",
                duration=timedelta(minutes=5),
                severity="critical",
                description="Error rate exceeds 5%"
            ),
            PerformanceAlert(
                alert_id="high_memory_usage",
                name="High Memory Usage",
                metric_name="memory_usage_mb",
                threshold=1024.0,
                operator=">",
                duration=timedelta(minutes=5),
                severity="medium",
                description="Memory usage exceeds 1GB"
            )
        ]
        
        for alert in default_alerts:
            self.alert_manager.add_alert(alert)
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, trace_id: Optional[str] = None):
        """Context manager for tracing operations."""
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        
        span_id = self.distributed_tracer.start_trace(trace_id, operation_name)
        
        try:
            yield span_id
            self.distributed_tracer.end_span(span_id, TraceStatus.COMPLETED)
        except Exception as e:
            self.distributed_tracer.end_span(span_id, TraceStatus.FAILED, str(e))
            raise
    
    @asynccontextmanager
    async def time_operation(self, operation_name: str):
        """Context manager for timing operations."""
        start_time = time.time()
        
        try:
            yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.metrics_collector.record_timer(operation_name, duration_ms)
    
    def record_request(self, endpoint: str, method: str, status_code: int,
                      duration_ms: float, user_id: Optional[str] = None) -> None:
        """Record HTTP request metrics."""
        labels = {
            'endpoint': endpoint,
            'method': method,
            'status_code': str(status_code)
        }
        
        if user_id:
            labels['user_id'] = user_id
        
        # Record response time
        self.metrics_collector.record_timer('response_time_ms', duration_ms, labels)
        
        # Record request count
        self.metrics_collector.record_counter('requests_total', 1, labels)
        
        # Record error if applicable
        if status_code >= 400:
            self.metrics_collector.record_counter('errors_total', 1, labels)
    
    def record_system_metrics(self, memory_usage_mb: float, cpu_usage_percent: float) -> None:
        """Record system-level metrics."""
        self.metrics_collector.record_gauge('memory_usage_mb', memory_usage_mb)
        self.metrics_collector.record_gauge('cpu_usage_percent', cpu_usage_percent)
    
    def record_business_metric(self, name: str, value: float, 
                             labels: Dict[str, str] = None) -> None:
        """Record a business-specific metric."""
        self.metrics_collector.record_gauge(name, value, labels or {})
    
    def get_performance_summary(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        metrics_summary = self.metrics_collector.get_metrics_summary(window_minutes)
        
        # Calculate derived metrics
        total_requests = metrics_summary.get('requests_total', {}).get('sum', 0)
        total_errors = metrics_summary.get('errors_total', {}).get('sum', 0)
        
        error_rate = (total_errors / total_requests) if total_requests > 0 else 0
        throughput_rps = total_requests / (window_minutes * 60) if window_minutes > 0 else 0
        
        return {
            'metrics': metrics_summary,
            'derived_metrics': {
                'error_rate': error_rate,
                'throughput_rps': throughput_rps,
                'uptime_seconds': (datetime.utcnow() - self._start_time).total_seconds()
            },
            'active_traces': len(self.distributed_tracer.get_active_spans()),
            'alerts': self.alert_manager.check_alerts()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""
        summary = self.get_performance_summary(window_minutes=5)
        
        # Determine overall health
        error_rate = summary['derived_metrics']['error_rate']
        avg_response_time = summary['metrics'].get('response_time_ms', {}).get('avg', 0)
        
        if error_rate > 0.1 or avg_response_time > 5000:
            health_status = "critical"
        elif error_rate > 0.05 or avg_response_time > 2000:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            'status': health_status,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': summary['metrics'],
            'alerts': summary['alerts']
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        summary = self.get_performance_summary()
        
        if format.lower() == "json":
            return json.dumps(summary, indent=2, default=str)
        elif format.lower() == "prometheus":
            # Convert to Prometheus format
            lines = []
            for metric_name, metric_data in summary['metrics'].items():
                for agg_name, agg_value in metric_data.items():
                    if isinstance(agg_value, (int, float)):
                        lines.append(f"{metric_name}_{agg_name} {agg_value}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# Decorators for easy performance monitoring
def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            async with performance_monitor.time_operation(operation_name):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with performance_monitor.time_operation(operation_name):
                return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def trace_operation(operation_name: str):
    """Decorator to trace function execution."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            async with performance_monitor.trace_operation(operation_name):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with performance_monitor.trace_operation(operation_name):
                return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 