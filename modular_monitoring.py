#!/usr/bin/env python3
"""
Modular Monitoring System

Advanced monitoring with:
- Observer pattern for metric collection
- Factory pattern for metric types
- Strategy pattern for data processing
- Chain of responsibility for alerting
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics."""
    MEMORY = "memory"
    PERFORMANCE = "performance"
    TRAINING = "training"
    SYSTEM = "system"

@dataclass
class Metric:
    """Base metric class."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp,
            'tags': self.tags
        }

class MetricCollector(ABC):
    """Abstract metric collector."""
    
    @abstractmethod
    def collect(self) -> Metric:
        """Collect a metric."""
        pass
    
    @abstractmethod
    def can_collect(self) -> bool:
        """Check if this collector can collect metrics."""
        pass

class MemoryMetricCollector(MetricCollector):
    """Memory metric collector."""
    
    def __init__(self):
        self.name = "memory_usage"
        self.metric_type = MetricType.MEMORY
    
    def can_collect(self) -> bool:
        return True
    
    def collect(self) -> Metric:
        try:
            import psutil
            memory = psutil.virtual_memory()
            value = memory.percent / 100.0
            
            return Metric(
                name=self.name,
                value=value,
                metric_type=self.metric_type,
                tags={'unit': 'percentage'}
            )
        except ImportError:
            return Metric(
                name=self.name,
                value=0.0,
                metric_type=self.metric_type,
                tags={'unit': 'percentage', 'error': 'psutil_not_available'}
            )

class PerformanceMetricCollector(MetricCollector):
    """Performance metric collector."""
    
    def __init__(self):
        self.name = "step_time"
        self.metric_type = MetricType.PERFORMANCE
        self.last_step_time = None
    
    def can_collect(self) -> bool:
        return self.last_step_time is not None
    
    def collect(self) -> Metric:
        if self.last_step_time is None:
            return Metric(
                name=self.name,
                value=0.0,
                metric_type=self.metric_type,
                tags={'unit': 'seconds', 'error': 'no_data'}
            )
        
        return Metric(
            name=self.name,
            value=self.last_step_time,
            metric_type=self.metric_type,
            tags={'unit': 'seconds'}
        )
    
    def record_step_time(self, step_time: float):
        """Record step time for collection."""
        self.last_step_time = step_time

class MetricProcessor(ABC):
    """Abstract metric processor."""
    
    @abstractmethod
    def process(self, metric: Metric) -> Metric:
        """Process a metric."""
        pass

class NormalizationProcessor(MetricProcessor):
    """Normalize metric values."""
    
    def __init__(self, min_val: float = 0.0, max_val: float = 1.0):
        self.min_val = min_val
        self.max_val = max_val
    
    def process(self, metric: Metric) -> Metric:
        if self.max_val > self.min_val:
            normalized_value = (metric.value - self.min_val) / (self.max_val - self.min_val)
            normalized_value = max(0.0, min(1.0, normalized_value))
        else:
            normalized_value = metric.value
        
        return Metric(
            name=f"{metric.name}_normalized",
            value=normalized_value,
            metric_type=metric.metric_type,
            timestamp=metric.timestamp,
            tags={**metric.tags, 'processed': 'normalized'}
        )

class AggregationProcessor(MetricProcessor):
    """Aggregate multiple metrics."""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.metrics_buffer: List[Metric] = []
    
    def process(self, metric: Metric) -> Metric:
        self.metrics_buffer.append(metric)
        
        if len(self.metrics_buffer) > self.window_size:
            self.metrics_buffer.pop(0)
        
        if len(self.metrics_buffer) < 2:
            return metric
        
        # Calculate statistics
        values = [m.value for m in self.metrics_buffer]
        mean_value = sum(values) / len(values)
        max_value = max(values)
        min_value = min(values)
        
        return Metric(
            name=f"{metric.name}_aggregated",
            value=mean_value,
            metric_type=metric.metric_type,
            timestamp=metric.timestamp,
            tags={
                **metric.tags,
                'processed': 'aggregated',
                'window_size': str(self.window_size),
                'max': str(max_value),
                'min': str(min_value)
            }
        )

class AlertRule(ABC):
    """Abstract alert rule."""
    
    def __init__(self, name: str, threshold: float):
        self.name = name
        self.threshold = threshold
    
    @abstractmethod
    def should_alert(self, metric: Metric) -> bool:
        """Check if alert should be triggered."""
        pass
    
    @abstractmethod
    def get_alert_message(self, metric: Metric) -> str:
        """Get alert message."""
        pass

class ThresholdAlertRule(AlertRule):
    """Threshold-based alert rule."""
    
    def __init__(self, name: str, threshold: float, operator: str = ">"):
        super().__init__(name, threshold)
        self.operator = operator
    
    def should_alert(self, metric: Metric) -> bool:
        if self.operator == ">":
            return metric.value > self.threshold
        elif self.operator == "<":
            return metric.value < self.threshold
        elif self.operator == ">=":
            return metric.value >= self.threshold
        elif self.operator == "<=":
            return metric.value <= self.threshold
        elif self.operator == "==":
            return metric.value == self.threshold
        else:
            return False
    
    def get_alert_message(self, metric: Metric) -> str:
        return f"Alert: {metric.name} = {metric.value} {self.operator} {self.threshold}"

class MetricObserver(ABC):
    """Abstract metric observer."""
    
    @abstractmethod
    def on_metric_collected(self, metric: Metric):
        """Called when a metric is collected."""
        pass
    
    @abstractmethod
    def on_metric_processed(self, metric: Metric):
        """Called when a metric is processed."""
        pass

class MetricLogger(MetricObserver):
    """Log metrics to console."""
    
    def on_metric_collected(self, metric: Metric):
        logger.info(f"📊 Metric collected: {metric.name} = {metric.value}")
    
    def on_metric_processed(self, metric: Metric):
        logger.info(f"🔧 Metric processed: {metric.name} = {metric.value}")

class AlertManager(MetricObserver):
    """Manage and trigger alerts."""
    
    def __init__(self):
        self.alert_rules: List[AlertRule] = []
        self.alert_history: List[Dict[str, Any]] = []
    
    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.alert_rules.append(rule)
    
    def on_metric_collected(self, metric: Metric):
        """Check for alerts when metric is collected."""
        for rule in self.alert_rules:
            if rule.should_alert(metric):
                alert = {
                    'rule': rule.name,
                    'metric': metric.name,
                    'value': metric.value,
                    'threshold': rule.threshold,
                    'message': rule.get_alert_message(metric),
                    'timestamp': time.time()
                }
                
                self.alert_history.append(alert)
                logger.warning(f"🚨 ALERT: {alert['message']}")
    
    def on_metric_processed(self, metric: Metric):
        """Check for alerts when metric is processed."""
        self.on_metric_collected(metric)
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """Get alert history."""
        return self.alert_history.copy()

class MetricFactory:
    """Factory for creating metric collectors."""
    
    _collectors = {
        MetricType.MEMORY: MemoryMetricCollector,
        MetricType.PERFORMANCE: PerformanceMetricCollector
    }
    
    @classmethod
    def create_collector(cls, metric_type: MetricType) -> MetricCollector:
        """Create a collector for the specified metric type."""
        if metric_type not in cls._collectors:
            raise ValueError(f"Unknown metric type: {metric_type}")
        
        collector_class = cls._collectors[metric_type]
        return collector_class()
    
    @classmethod
    def create_all_collectors(cls) -> List[MetricCollector]:
        """Create all available collectors."""
        return [cls.create_collector(metric_type) for metric_type in MetricType]

class MonitoringSystem:
    """Main monitoring system."""
    
    def __init__(self):
        self.collectors: List[MetricCollector] = []
        self.processors: List[MetricProcessor] = []
        self.observers: List[MetricObserver] = []
        self.metrics_queue = queue.Queue()
        self.running = False
        self.collection_thread = None
    
    def add_collector(self, collector: MetricCollector):
        """Add a metric collector."""
        self.collectors.append(collector)
    
    def add_processor(self, processor: MetricProcessor):
        """Add a metric processor."""
        self.processors.append(processor)
    
    def add_observer(self, observer: MetricObserver):
        """Add a metric observer."""
        self.observers.append(observer)
    
    def start(self):
        """Start the monitoring system."""
        if self.running:
            return
        
        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        logger.info("Monitoring system started")
    
    def stop(self):
        """Stop the monitoring system."""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join()
        logger.info("Monitoring system stopped")
    
    def _collection_loop(self):
        """Main collection loop."""
        while self.running:
            try:
                # Collect metrics from all collectors
                for collector in self.collectors:
                    if collector.can_collect():
                        metric = collector.collect()
                        self.metrics_queue.put(metric)
                
                # Process metrics from queue
                while not self.metrics_queue.empty():
                    metric = self.metrics_queue.get_nowait()
                    
                    # Notify observers of collected metric
                    for observer in self.observers:
                        observer.on_metric_collected(metric)
                    
                    # Process metric through all processors
                    processed_metric = metric
                    for processor in self.processors:
                        processed_metric = processor.process(processed_metric)
                    
                    # Notify observers of processed metric
                    for observer in self.observers:
                        observer.on_metric_processed(processed_metric)
                
                time.sleep(1)  # Collect every second
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)

# Example usage
if __name__ == "__main__":
    # Create monitoring system
    monitoring = MonitoringSystem()
    
    # Create and add collectors
    factory = MetricFactory()
    collectors = factory.create_all_collectors()
    for collector in collectors:
        monitoring.add_collector(collector)
    
    # Create and add processors
    monitoring.add_processor(NormalizationProcessor())
    monitoring.add_processor(AggregationProcessor(window_size=5))
    
    # Create and add observers
    monitoring.add_observer(MetricLogger())
    
    alert_manager = AlertManager()
    alert_manager.add_alert_rule(ThresholdAlertRule("high_memory", 0.9, ">"))
    monitoring.add_observer(alert_manager)
    
    # Start monitoring
    monitoring.start()
    
    try:
        # Simulate some activity
        time.sleep(5)
        
        # Get alert history
        alerts = alert_manager.get_alert_history()
        if alerts:
            print(f"Generated {len(alerts)} alerts")
        
    finally:
        monitoring.stop()
