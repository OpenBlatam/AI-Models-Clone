"""
Advanced metrics collection system for the modular dependency management system.
Provides comprehensive performance monitoring and analytics.
"""

import time
import asyncio
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json
import logging
from pathlib import Path

from .dependency_structures import ServiceStatus


@dataclass
class MetricPoint:
    """A single metric data point"""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """A series of metric data points"""
    name: str
    description: str
    unit: str
    data_points: deque = field(default_factory=lambda: deque(maxlen=1000))
    labels: Dict[str, str] = field(default_factory=dict)
    
    def add_point(self, value: float, labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add a new data point to the series"""
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels or {},
            metadata=metadata or {}
        )
        self.data_points.append(point)
    
    def get_latest(self) -> Optional[MetricPoint]:
        """Get the latest data point"""
        return self.data_points[-1] if self.data_points else None
    
    def get_statistics(self, window_seconds: Optional[float] = None) -> Dict[str, float]:
        """Get statistics for the metric series"""
        if not self.data_points:
            return {}
        
        # Filter by time window if specified
        if window_seconds:
            cutoff_time = time.time() - window_seconds
            recent_points = [p for p in self.data_points if p.timestamp >= cutoff_time]
        else:
            recent_points = list(self.data_points)
        
        if not recent_points:
            return {}
        
        values = [p.value for p in recent_points]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'latest': values[-1],
            'oldest': values[0]
        }


@dataclass
class ServiceMetrics:
    """Metrics for a specific service"""
    service_name: str
    metrics: Dict[str, MetricSeries] = field(default_factory=dict)
    
    def add_metric(self, name: str, value: float, description: str = "", unit: str = "", 
                   labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add a metric to the service"""
        if name not in self.metrics:
            self.metrics[name] = MetricSeries(
                name=name,
                description=description,
                unit=unit,
                labels=labels or {}
            )
        
        self.metrics[name].add_point(value, labels, metadata)
    
    def get_metric(self, name: str) -> Optional[MetricSeries]:
        """Get a specific metric series"""
        return self.metrics.get(name)
    
    def get_summary(self, window_seconds: Optional[float] = None) -> Dict[str, Any]:
        """Get a summary of all metrics for this service"""
        summary = {
            'service_name': self.service_name,
            'metrics': {}
        }
        
        for name, series in self.metrics.items():
            stats = series.get_statistics(window_seconds)
            if stats:
                summary['metrics'][name] = {
                    'description': series.description,
                    'unit': series.unit,
                    'statistics': stats
                }
        
        return summary


class MetricsCollector:
    """Advanced metrics collection and analysis system"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.services: Dict[str, ServiceMetrics] = {}
        self.global_metrics: Dict[str, MetricSeries] = {}
        self.collectors: List[Callable] = []
        self.storage_path = Path(storage_path) if storage_path else Path("metrics")
        self.storage_path.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.performance_timers: Dict[str, float] = {}
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.error_counts: Dict[str, int] = defaultdict(int)
        
        # Auto-collection settings
        self.auto_collect = True
        self.collection_interval = 30.0  # seconds
        self.collection_task: Optional[asyncio.Task] = None
        
        # Initialize default metrics
        self._init_default_metrics()
    
    def _init_default_metrics(self):
        """Initialize default global metrics"""
        self.add_global_metric(
            "system_uptime",
            "System uptime in seconds",
            "seconds"
        )
        self.add_global_metric(
            "active_services",
            "Number of active services",
            "count"
        )
        self.add_global_metric(
            "total_operations",
            "Total number of operations performed",
            "count"
        )
        self.add_global_metric(
            "error_rate",
            "Error rate as percentage",
            "percentage"
        )
    
    def add_service_metrics(self, service_name: str) -> ServiceMetrics:
        """Add metrics tracking for a service"""
        if service_name not in self.services:
            self.services[service_name] = ServiceMetrics(service_name)
        return self.services[service_name]
    
    def add_global_metric(self, name: str, description: str, unit: str, labels: Optional[Dict[str, str]] = None):
        """Add a global metric"""
        self.global_metrics[name] = MetricSeries(
            name=name,
            description=description,
            unit=unit,
            labels=labels or {}
        )
    
    def record_service_metric(self, service_name: str, metric_name: str, value: float, 
                            description: str = "", unit: str = "", 
                            labels: Optional[Dict[str, str]] = None, 
                            metadata: Optional[Dict[str, Any]] = None):
        """Record a metric for a specific service"""
        service_metrics = self.add_service_metrics(service_name)
        service_metrics.add_metric(metric_name, value, description, unit, labels, metadata)
    
    def record_global_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, 
                           metadata: Optional[Dict[str, Any]] = None):
        """Record a global metric"""
        if name in self.global_metrics:
            self.global_metrics[name].add_point(value, labels, metadata)
    
    def start_timer(self, operation_name: str):
        """Start a performance timer"""
        self.performance_timers[operation_name] = time.time()
    
    def end_timer(self, operation_name: str, service_name: Optional[str] = None):
        """End a performance timer and record the duration"""
        if operation_name in self.performance_timers:
            duration = time.time() - self.performance_timers[operation_name]
            
            if service_name:
                self.record_service_metric(
                    service_name,
                    f"{operation_name}_duration",
                    duration,
                    f"Duration of {operation_name}",
                    "seconds"
                )
            else:
                self.record_global_metric(f"{operation_name}_duration", duration)
            
            del self.performance_timers[operation_name]
    
    def increment_operation_count(self, operation_name: str, service_name: Optional[str] = None):
        """Increment operation count"""
        self.operation_counts[operation_name] += 1
        
        if service_name:
            self.record_service_metric(
                service_name,
                f"{operation_name}_count",
                self.operation_counts[operation_name],
                f"Count of {operation_name} operations",
                "count"
            )
        else:
            self.record_global_metric(f"{operation_name}_count", self.operation_counts[operation_name])
    
    def record_error(self, error_type: str, service_name: Optional[str] = None, error_details: Optional[str] = None):
        """Record an error occurrence"""
        self.error_counts[error_type] += 1
        
        if service_name:
            self.record_service_metric(
                service_name,
                f"{error_type}_errors",
                self.error_counts[error_type],
                f"Count of {error_type} errors",
                "count"
            )
        else:
            self.record_global_metric(f"{error_type}_errors", self.error_counts[error_type])
    
    def add_collector(self, collector_func: Callable):
        """Add a custom metrics collector function"""
        self.collectors.append(collector_func)
    
    async def collect_metrics(self):
        """Collect all metrics from registered collectors"""
        for collector in self.collectors:
            try:
                if asyncio.iscoroutinefunction(collector):
                    await collector(self)
                else:
                    collector(self)
            except Exception as e:
                self.logger.error(f"Error in metrics collector: {e}")
    
    async def start_auto_collection(self):
        """Start automatic metrics collection"""
        if self.collection_task:
            return
        
        self.auto_collect = True
        
        async def collection_loop():
            while self.auto_collect:
                try:
                    await self.collect_metrics()
                    await asyncio.sleep(self.collection_interval)
                except Exception as e:
                    self.logger.error(f"Error in auto collection: {e}")
                    await asyncio.sleep(self.collection_interval)
        
        self.collection_task = asyncio.create_task(collection_loop())
    
    async def stop_auto_collection(self):
        """Stop automatic metrics collection"""
        self.auto_collect = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
            self.collection_task = None
    
    def get_service_metrics(self, service_name: str, window_seconds: Optional[float] = None) -> Dict[str, Any]:
        """Get metrics for a specific service"""
        if service_name not in self.services:
            return {}
        
        return self.services[service_name].get_summary(window_seconds)
    
    def get_global_metrics(self, window_seconds: Optional[float] = None) -> Dict[str, Any]:
        """Get global metrics summary"""
        summary = {
            'global_metrics': {},
            'system_summary': {
                'total_services': len(self.services),
                'total_metrics': len(self.global_metrics),
                'collection_interval': self.collection_interval,
                'auto_collect': self.auto_collect
            }
        }
        
        for name, series in self.global_metrics.items():
            stats = series.get_statistics(window_seconds)
            if stats:
                summary['global_metrics'][name] = {
                    'description': series.description,
                    'unit': series.unit,
                    'statistics': stats
                }
        
        return summary
    
    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            # Get error rates
            total_operations = sum(self.operation_counts.values())
            total_errors = sum(self.error_counts.values())
            
            if total_operations == 0:
                return 100.0
            
            error_rate = (total_errors / total_operations) * 100
            
            # Get service health
            active_services = 0
            total_services = len(self.services)
            
            for service_name, service_metrics in self.services.items():
                # Check if service has recent activity
                latest_metric = None
                for metric_series in service_metrics.metrics.values():
                    latest = metric_series.get_latest()
                    if latest and latest.timestamp > time.time() - 300:  # 5 minutes
                        latest_metric = latest
                        break
                
                if latest_metric:
                    active_services += 1
            
            service_health = (active_services / total_services * 100) if total_services > 0 else 100
            
            # Calculate overall score
            health_score = (100 - error_rate) * 0.7 + service_health * 0.3
            
            return max(0.0, min(100.0, health_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 50.0
    
    def export_metrics(self, file_path: Optional[str] = None) -> str:
        """Export metrics to JSON file"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.storage_path / f"metrics_export_{timestamp}.json"
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'system_health_score': self.get_system_health_score(),
            'global_metrics': self.get_global_metrics(),
            'services': {}
        }
        
        for service_name in self.services:
            export_data['services'][service_name] = self.get_service_metrics(service_name)
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return str(file_path)
    
    def clear_old_metrics(self, days: int = 7):
        """Clear metrics older than specified days"""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        # Clear old global metrics
        for series in self.global_metrics.values():
            series.data_points = deque(
                [p for p in series.data_points if p.timestamp >= cutoff_time],
                maxlen=series.data_points.maxlen
            )
        
        # Clear old service metrics
        for service_metrics in self.services.values():
            for series in service_metrics.metrics.values():
                series.data_points = deque(
                    [p for p in series.data_points if p.timestamp >= cutoff_time],
                    maxlen=series.data_points.maxlen
                )


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return metrics_collector


def record_service_metric(service_name: str, metric_name: str, value: float, **kwargs):
    """Record a service metric using the global collector"""
    metrics_collector.record_service_metric(service_name, metric_name, value, **kwargs)


def record_global_metric(name: str, value: float, **kwargs):
    """Record a global metric using the global collector"""
    metrics_collector.record_global_metric(name, value, **kwargs)


def start_timer(operation_name: str):
    """Start a performance timer using the global collector"""
    metrics_collector.start_timer(operation_name)


def end_timer(operation_name: str, service_name: Optional[str] = None):
    """End a performance timer using the global collector"""
    metrics_collector.end_timer(operation_name, service_name)


def increment_operation_count(operation_name: str, service_name: Optional[str] = None):
    """Increment operation count using the global collector"""
    metrics_collector.increment_operation_count(operation_name, service_name)


def record_error(error_type: str, service_name: Optional[str] = None, error_details: Optional[str] = None):
    """Record an error using the global collector"""
    metrics_collector.record_error(error_type, service_name, error_details)
