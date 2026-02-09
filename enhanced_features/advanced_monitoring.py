#!/usr/bin/env python3
"""
📊 ADVANCED MONITORING MODULE - Blaze AI System
Distributed tracing, custom metrics, and intelligent alerting
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid
from datetime import datetime, timedelta
import traceback
import psutil
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Alert severity enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class TraceStatus(Enum):
    """Trace status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class Metric:
    """Custom metric definition."""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str]
    timestamp: float
    description: str

@dataclass
class TraceSpan:
    """Distributed tracing span."""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    name: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    status: TraceStatus
    tags: Dict[str, Any]
    events: List[Dict[str, Any]]
    error: Optional[str]

@dataclass
class Alert:
    """Alert definition."""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class MonitoringConfig:
    """Advanced monitoring configuration."""
    enable_distributed_tracing: bool = True
    enable_custom_metrics: bool = True
    enable_intelligent_alerting: bool = True
    trace_sampling_rate: float = 0.1  # 10% of requests
    metrics_retention_days: int = 30
    alert_cooldown_minutes: int = 5
    performance_thresholds: Dict[str, float] = None
    custom_alert_rules: List[Dict[str, Any]] = None

class AdvancedMonitoring:
    """Advanced monitoring system with distributed tracing and intelligent alerting."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.traces: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.alerts: List[Alert] = []
        self.alert_handlers: Dict[str, Callable] = {}
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.global_metrics: Dict[str, float] = defaultdict(float)
        self._init_time = time.time()
        self._lock = threading.Lock()
        
        # Initialize performance thresholds
        if not self.config.performance_thresholds:
            self.config.performance_thresholds = {
                'cpu_usage': 80.0,
                'memory_usage': 85.0,
                'disk_usage': 90.0,
                'response_time_p95': 2.0,
                'error_rate': 5.0
            }
        
        # Initialize custom alert rules
        if not self.config.custom_alert_rules:
            self.config.custom_alert_rules = [
                {
                    'name': 'High CPU Usage',
                    'condition': 'cpu_usage > 80',
                    'severity': AlertSeverity.WARNING,
                    'message': 'CPU usage is above 80%'
                },
                {
                    'name': 'High Memory Usage',
                    'condition': 'memory_usage > 85',
                    'severity': AlertSeverity.WARNING,
                    'message': 'Memory usage is above 85%'
                },
                {
                    'name': 'High Error Rate',
                    'condition': 'error_rate > 5',
                    'severity': AlertSeverity.ERROR,
                    'message': 'Error rate is above 5%'
                }
            ]
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background monitoring tasks."""
        def background_monitor():
            while True:
                try:
                    # Collect system metrics
                    self._collect_system_metrics()
                    
                    # Check performance thresholds
                    self._check_performance_thresholds()
                    
                    # Clean up old data
                    self._cleanup_old_data()
                    
                    time.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error in background monitoring: {e}")
                    time.sleep(60)  # Wait longer on error
        
        thread = threading.Thread(target=background_monitor, daemon=True)
        thread.start()
        logger.info("Background monitoring started")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._add_metric('system_cpu_usage', MetricType.GAUGE, cpu_percent, {'type': 'system'})
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self._add_metric('system_memory_usage', MetricType.GAUGE, memory_percent, {'type': 'system'})
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self._add_metric('system_disk_usage', MetricType.GAUGE, disk_percent, {'type': 'system'})
            
            # Network I/O
            network = psutil.net_io_counters()
            self._add_metric('system_network_bytes_sent', MetricType.COUNTER, network.bytes_sent, {'type': 'system'})
            self._add_metric('system_network_bytes_recv', MetricType.COUNTER, network.bytes_recv, {'type': 'system'})
            
            # Update global metrics
            self.global_metrics['cpu_usage'] = cpu_percent
            self.global_metrics['memory_usage'] = memory_percent
            self.global_metrics['disk_usage'] = disk_percent
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _check_performance_thresholds(self):
        """Check performance thresholds and trigger alerts."""
        try:
            for metric_name, threshold in self.config.performance_thresholds.items():
                current_value = self.global_metrics.get(metric_name, 0.0)
                
                if current_value > threshold:
                    # Check if we should alert (avoid spam)
                    if self._should_alert(metric_name, current_value):
                        self._create_alert(
                            name=f"High {metric_name.replace('_', ' ').title()}",
                            severity=AlertSeverity.WARNING,
                            message=f"{metric_name.replace('_', ' ').title()} is {current_value:.1f}% (threshold: {threshold}%)",
                            source="performance_monitor",
                            metadata={'metric': metric_name, 'value': current_value, 'threshold': threshold}
                        )
            
        except Exception as e:
            logger.error(f"Error checking performance thresholds: {e}")
    
    def _should_alert(self, metric_name: str, current_value: float) -> bool:
        """Check if we should create an alert (avoid spam)."""
        try:
            # Check if we have a recent alert for this metric
            recent_alerts = [
                alert for alert in self.alerts
                if (alert.source == "performance_monitor" and
                    alert.metadata.get('metric') == metric_name and
                    (datetime.now() - alert.timestamp).total_seconds() < self.config.alert_cooldown_minutes * 60)
            ]
            
            return len(recent_alerts) == 0
            
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
            return True
    
    def _cleanup_old_data(self):
        """Clean up old metrics and traces."""
        try:
            current_time = time.time()
            cutoff_time = current_time - (self.config.metrics_retention_days * 24 * 3600)
            
            # Clean up old metrics
            for metric_name in list(self.metrics.keys()):
                self.metrics[metric_name] = [
                    metric for metric in self.metrics[metric_name]
                    if metric.timestamp > cutoff_time
                ]
            
            # Clean up old traces
            for trace_id in list(self.traces.keys()):
                self.traces[trace_id] = [
                    span for span in self.traces[trace_id]
                    if span.start_time > cutoff_time
                ]
                
                # Remove empty traces
                if not self.traces[trace_id]:
                    del self.traces[trace_id]
            
            # Clean up old alerts (keep last 1000)
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-1000:]
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def _add_metric(self, name: str, metric_type: MetricType, value: float, labels: Dict[str, str]):
        """Add a new metric."""
        try:
            metric = Metric(
                name=name,
                type=metric_type,
                value=value,
                labels=labels,
                timestamp=time.time(),
                description=f"Auto-generated metric for {name}"
            )
            
            with self._lock:
                self.metrics[name].append(metric)
                
                # Keep only recent metrics
                if len(self.metrics[name]) > 1000:
                    self.metrics[name] = self.metrics[name][-1000:]
                    
        except Exception as e:
            logger.error(f"Error adding metric: {e}")
    
    @asynccontextmanager
    async def trace_span(self, name: str, trace_id: Optional[str] = None, 
                        parent_span_id: Optional[str] = None, **tags):
        """Context manager for distributed tracing."""
        if not self.config.enable_distributed_tracing:
            yield None
            return
        
        # Generate trace ID if not provided
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        # Generate span ID
        span_id = str(uuid.uuid4())
        
        # Create span
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=name,
            start_time=time.time(),
            end_time=None,
            duration=None,
            status=TraceStatus.SUCCESS,
            tags=tags,
            events=[],
            error=None
        )
        
        try:
            # Add span to traces
            with self._lock:
                if trace_id not in self.traces:
                    self.traces[trace_id] = []
                self.traces[trace_id].append(span)
            
            yield span
            
        except Exception as e:
            # Mark span as error
            span.status = TraceStatus.ERROR
            span.error = str(e)
            span.events.append({
                'timestamp': time.time(),
                'name': 'error',
                'attributes': {'error': str(e), 'traceback': traceback.format_exc()}
            })
            raise
        
        finally:
            # Complete span
            span.end_time = time.time()
            span.duration = span.end_time - span.start_time
    
    def add_trace_event(self, span: TraceSpan, event_name: str, **attributes):
        """Add an event to a trace span."""
        if span:
            span.events.append({
                'timestamp': time.time(),
                'name': event_name,
                'attributes': attributes
            })
    
    def add_trace_tag(self, span: TraceSpan, key: str, value: Any):
        """Add a tag to a trace span."""
        if span:
            span.tags[key] = value
    
    async def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE, 
                           labels: Optional[Dict[str, str]] = None, description: str = ""):
        """Record a custom metric."""
        if not self.config.enable_custom_metrics:
            return
        
        try:
            if labels is None:
                labels = {}
            
            metric = Metric(
                name=name,
                type=metric_type,
                value=value,
                labels=labels,
                timestamp=time.time(),
                description=description
            )
            
            with self._lock:
                self.metrics[name].append(metric)
                
                # Keep only recent metrics
                if len(self.metrics[name]) > 1000:
                    self.metrics[name] = self.metrics[name][-1000:]
                    
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    async def increment_counter(self, name: str, value: float = 1.0, 
                              labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        await self.record_metric(name, value, MetricType.COUNTER, labels, f"Counter for {name}")
    
    async def set_gauge(self, name: str, value: float, 
                       labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        await self.record_metric(name, value, MetricType.GAUGE, labels, f"Gauge for {name}")
    
    async def record_histogram(self, name: str, value: float, 
                             labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric."""
        await self.record_metric(name, value, MetricType.HISTOGRAM, labels, f"Histogram for {name}")
    
    def _create_alert(self, name: str, severity: AlertSeverity, message: str, 
                     source: str, metadata: Optional[Dict[str, Any]] = None):
        """Create a new alert."""
        try:
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                name=name,
                severity=severity,
                message=message,
                timestamp=datetime.now(),
                source=source,
                metadata=metadata or {}
            )
            
            with self._lock:
                self.alerts.append(alert)
            
            # Trigger alert handlers
            self._trigger_alert_handlers(alert)
            
            logger.warning(f"Alert created: {name} - {message}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def _trigger_alert_handlers(self, alert: Alert):
        """Trigger registered alert handlers."""
        try:
            for handler_name, handler in self.alert_handlers.items():
                try:
                    if asyncio.iscoroutinefunction(handler):
                        # Async handler
                        asyncio.create_task(handler(alert))
                    else:
                        # Sync handler
                        handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler {handler_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error triggering alert handlers: {e}")
    
    def register_alert_handler(self, name: str, handler: Callable):
        """Register an alert handler."""
        try:
            self.alert_handlers[name] = handler
            logger.info(f"Alert handler registered: {name}")
        except Exception as e:
            logger.error(f"Error registering alert handler: {e}")
    
    def unregister_alert_handler(self, name: str):
        """Unregister an alert handler."""
        try:
            if name in self.alert_handlers:
                del self.alert_handlers[name]
                logger.info(f"Alert handler unregistered: {name}")
        except Exception as e:
            logger.error(f"Error unregistering alert handler: {e}")
    
    async def get_metrics(self, metric_name: Optional[str] = None, 
                         time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get metrics data."""
        try:
            current_time = time.time()
            if time_range:
                cutoff_time = current_time - time_range.total_seconds()
            else:
                cutoff_time = 0
            
            if metric_name:
                # Return specific metric
                if metric_name in self.metrics:
                    metrics = [
                        metric for metric in self.metrics[metric_name]
                        if metric.timestamp >= cutoff_time
                    ]
                    return {
                        'metric_name': metric_name,
                        'metrics': [asdict(metric) for metric in metrics],
                        'count': len(metrics)
                    }
                else:
                    return {'error': f'Metric {metric_name} not found'}
            else:
                # Return all metrics
                result = {}
                for name, metric_list in self.metrics.items():
                    filtered_metrics = [
                        metric for metric in metric_list
                        if metric.timestamp >= cutoff_time
                    ]
                    result[name] = {
                        'count': len(filtered_metrics),
                        'latest_value': filtered_metrics[-1].value if filtered_metrics else None,
                        'latest_timestamp': filtered_metrics[-1].timestamp if filtered_metrics else None
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {'error': str(e)}
    
    async def get_traces(self, trace_id: Optional[str] = None, 
                        time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get trace data."""
        try:
            current_time = time.time()
            if time_range:
                cutoff_time = current_time - time_range.total_seconds()
            else:
                cutoff_time = 0
            
            if trace_id:
                # Return specific trace
                if trace_id in self.traces:
                    spans = [
                        span for span in self.traces[trace_id]
                        if span.start_time >= cutoff_time
                    ]
                    return {
                        'trace_id': trace_id,
                        'spans': [asdict(span) for span in spans],
                        'span_count': len(spans)
                    }
                else:
                    return {'error': f'Trace {trace_id} not found'}
            else:
                # Return all traces
                result = {}
                for tid, span_list in self.traces.items():
                    filtered_spans = [
                        span for span in span_list
                        if span.start_time >= cutoff_time
                    ]
                    result[tid] = {
                        'span_count': len(filtered_spans),
                        'duration': sum(span.duration or 0 for span in filtered_spans),
                        'status_distribution': self._get_status_distribution(filtered_spans)
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting traces: {e}")
            return {'error': str(e)}
    
    def _get_status_distribution(self, spans: List[TraceSpan]) -> Dict[str, int]:
        """Get status distribution for spans."""
        distribution = defaultdict(int)
        for span in spans:
            distribution[span.status.value] += 1
        return dict(distribution)
    
    async def get_alerts(self, severity: Optional[AlertSeverity] = None, 
                        acknowledged: Optional[bool] = None, 
                        resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get alerts data."""
        try:
            filtered_alerts = self.alerts
            
            if severity:
                filtered_alerts = [alert for alert in filtered_alerts if alert.severity == severity]
            
            if acknowledged is not None:
                filtered_alerts = [alert for alert in filtered_alerts if alert.acknowledged == acknowledged]
            
            if resolved is not None:
                filtered_alerts = [alert for alert in filtered_alerts if alert.resolved == resolved]
            
            return [asdict(alert) for alert in filtered_alerts]
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        try:
            with self._lock:
                for alert in self.alerts:
                    if alert.alert_id == alert_id:
                        alert.acknowledged = True
                        logger.info(f"Alert acknowledged: {alert_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        try:
            with self._lock:
                for alert in self.alerts:
                    if alert.alert_id == alert_id:
                        alert.resolved = True
                        logger.info(f"Alert resolved: {alert_id}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary."""
        try:
            current_time = time.time()
            
            # Calculate metrics summary
            total_metrics = sum(len(metrics) for metrics in self.metrics.values())
            active_metrics = len(self.metrics)
            
            # Calculate traces summary
            total_spans = sum(len(spans) for spans in self.traces.values())
            active_traces = len(self.traces)
            
            # Calculate alerts summary
            active_alerts = len([alert for alert in self.alerts if not alert.resolved])
            critical_alerts = len([alert for alert in self.alerts 
                                if alert.severity == AlertSeverity.CRITICAL and not alert.resolved])
            
            # Calculate performance summary
            performance_summary = {
                'cpu_usage': self.global_metrics.get('cpu_usage', 0.0),
                'memory_usage': self.global_metrics.get('memory_usage', 0.0),
                'disk_usage': self.global_metrics.get('disk_usage', 0.0)
            }
            
            return {
                'uptime': current_time - self._init_time,
                'metrics': {
                    'total_count': total_metrics,
                    'active_metrics': active_metrics
                },
                'tracing': {
                    'total_spans': total_spans,
                    'active_traces': active_traces
                },
                'alerts': {
                    'total_alerts': len(self.alerts),
                    'active_alerts': active_alerts,
                    'critical_alerts': critical_alerts
                },
                'performance': performance_summary,
                'config': {
                    'distributed_tracing': self.config.enable_distributed_tracing,
                    'custom_metrics': self.config.enable_custom_metrics,
                    'intelligent_alerting': self.config.enable_intelligent_alerting
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting monitoring summary: {e}")
            return {'error': str(e)}

# Utility functions
def create_advanced_monitoring(config: MonitoringConfig) -> AdvancedMonitoring:
    """Create and configure an advanced monitoring instance."""
    return AdvancedMonitoring(config)

# Example usage
async def main():
    """Example usage of the advanced monitoring system."""
    config = MonitoringConfig(
        enable_distributed_tracing=True,
        enable_custom_metrics=True,
        enable_intelligent_alerting=True
    )
    
    monitoring = create_advanced_monitoring(config)
    
    # Example: Record some metrics
    await monitoring.record_metric('api_requests_total', 1, MetricType.COUNTER, {'endpoint': '/api/users'})
    await monitoring.set_gauge('active_connections', 25, {'service': 'database'})
    
    # Example: Distributed tracing
    async with monitoring.trace_span('api_request', tags={'endpoint': '/api/users', 'method': 'GET'}) as span:
        if span:
            monitoring.add_trace_tag(span, 'user_id', '12345')
            monitoring.add_trace_event(span, 'database_query', query='SELECT * FROM users')
        
        # Simulate some work
        await asyncio.sleep(0.1)
        
        if span:
            monitoring.add_trace_event(span, 'response_sent', status_code=200)
    
    # Get monitoring summary
    summary = await monitoring.get_monitoring_summary()
    print(f"Monitoring Summary: {json.dumps(summary, indent=2)}")
    
    # Get metrics
    metrics = await monitoring.get_metrics()
    print(f"Metrics: {json.dumps(metrics, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
