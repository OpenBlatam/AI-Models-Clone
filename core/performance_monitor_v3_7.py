"""
Enhanced Performance Monitoring Module v3.7
Integrates with the existing metrics_collector system and provides advanced monitoring capabilities.
This module follows modular architecture principles and can be easily integrated into the system.
"""

import time
import asyncio
import threading
import psutil
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json
import os
from pathlib import Path

# Import existing metrics collector
try:
    from .metrics_collector import MetricsCollector, ServiceMetrics, MetricSeries, MetricPoint
    METRICS_COLLECTOR_AVAILABLE = True
except ImportError:
    METRICS_COLLECTOR_AVAILABLE = False
    print("Warning: MetricsCollector not available, using standalone mode")

# Import existing health monitor if available
try:
    from .health_monitor import HealthMonitor
    HEALTH_MONITOR_AVAILABLE = True
except ImportError:
    HEALTH_MONITOR_AVAILABLE = False


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    operator: str = ">"  # >, <, >=, <=, ==, !=
    enabled: bool = True
    action: str = "log"  # log, alert, auto_scale, restart
    
    def check_threshold(self, value: float) -> Dict[str, Any]:
        """Check if value exceeds threshold"""
        result = {
            'threshold_name': self.metric_name,
            'current_value': value,
            'warning_threshold': self.warning_threshold,
            'critical_threshold': self.critical_threshold,
            'status': 'normal',
            'message': ''
        }
        
        if not self.enabled:
            return result
        
        # Evaluate threshold based on operator
        if self.operator == ">":
            if value > self.critical_threshold:
                result['status'] = 'critical'
                result['message'] = f'Value {value} exceeds critical threshold {self.critical_threshold}'
            elif value > self.warning_threshold:
                result['status'] = 'warning'
                result['message'] = f'Value {value} exceeds warning threshold {self.warning_threshold}'
        elif self.operator == "<":
            if value < self.critical_threshold:
                result['status'] = 'critical'
                result['message'] = f'Value {value} below critical threshold {self.critical_threshold}'
            elif value < self.warning_threshold:
                result['status'] = 'warning'
                result['message'] = f'Value {value} below warning threshold {self.warning_threshold}'
        elif self.operator == ">=":
            if value >= self.critical_threshold:
                result['status'] = 'critical'
                result['message'] = f'Value {value} meets or exceeds critical threshold {self.critical_threshold}'
            elif value >= self.warning_threshold:
                result['status'] = 'warning'
                result['message'] = f'Value {value} meets or exceeds warning threshold {self.warning_threshold}'
        elif self.operator == "<=":
            if value <= self.critical_threshold:
                result['status'] = 'critical'
                result['message'] = f'Value {value} meets or below critical threshold {self.critical_threshold}'
            elif value <= self.warning_threshold:
                result['status'] = 'warning'
                result['message'] = f'Value {value} meets or below warning threshold {self.warning_threshold}'
        elif self.operator == "==":
            if value == self.critical_threshold:
                result['status'] = 'critical'
                result['message'] = f'Value {value} equals critical threshold {self.critical_threshold}'
            elif value == self.warning_threshold:
                result['status'] = 'warning'
                result['message'] = f'Value {value} equals warning threshold {self.warning_threshold}'
        elif self.operator == "!=":
            if value != self.critical_threshold:
                result['status'] = 'critical'
                result['message'] = f'Value {value} differs from critical threshold {self.critical_threshold}'
            elif value != self.warning_threshold:
                result['status'] = 'warning'
                result['message'] = f'Value {value} differs from warning threshold {self.warning_threshold}'
        
        return result


@dataclass
class PerformanceAlert:
    """Performance alert information"""
    timestamp: float
    threshold_name: str
    status: str
    message: str
    current_value: float
    threshold_value: float
    service_name: Optional[str] = None
    severity: str = "info"


class EnhancedPerformanceMonitor:
    """
    Enhanced Performance Monitoring Module v3.7
    Provides comprehensive system performance monitoring with thresholds, alerts, and auto-scaling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Performance thresholds
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.alerts: deque = deque(maxlen=1000)
        
        # System metrics
        self.system_metrics: Dict[str, MetricSeries] = {}
        self.service_metrics: Dict[str, ServiceMetrics] = {}
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_interval = self.config.get('monitoring_interval', 5.0)
        
        # Performance tracking
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.peak_values: Dict[str, float] = {}
        self.lowest_values: Dict[str, float] = {}
        
        # Auto-scaling configuration
        self.auto_scaling_enabled = self.config.get('auto_scaling_enabled', False)
        self.scaling_thresholds = self.config.get('scaling_thresholds', {})
        
        # Integration with existing systems
        self.metrics_collector: Optional[MetricsCollector] = None
        self.health_monitor: Optional[Any] = None
        
        # Initialize the module
        self._initialize()
    
    def _initialize(self):
        """Initialize the performance monitor"""
        try:
            # Try to integrate with existing metrics collector
            if METRICS_COLLECTOR_AVAILABLE:
                self.metrics_collector = MetricsCollector()
                self.logger.info("Successfully integrated with MetricsCollector")
            
            # Try to integrate with existing health monitor
            if HEALTH_MONITOR_AVAILABLE:
                self.health_monitor = HealthMonitor()
                self.logger.info("Successfully integrated with HealthMonitor")
            
            # Set up default thresholds
            self._setup_default_thresholds()
            
            # Initialize system metrics
            self._init_system_metrics()
            
            self.logger.info("Enhanced Performance Monitor v3.7 initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Performance Monitor: {e}")
    
    def _setup_default_thresholds(self):
        """Set up default performance thresholds"""
        default_thresholds = [
            PerformanceThreshold("cpu_usage", 70.0, 90.0, ">", True, "alert"),
            PerformanceThreshold("memory_usage", 80.0, 95.0, ">", True, "alert"),
            PerformanceThreshold("disk_usage", 85.0, 95.0, ">", True, "alert"),
            PerformanceThreshold("response_time", 1000.0, 5000.0, ">", True, "alert"),
            PerformanceThreshold("error_rate", 5.0, 15.0, ">", True, "alert"),
            PerformanceThreshold("throughput", 100.0, 50.0, "<", True, "auto_scale"),
        ]
        
        for threshold in default_thresholds:
            self.add_threshold(threshold)
    
    def _init_system_metrics(self):
        """Initialize system metrics"""
        system_metrics = [
            ("cpu_usage", "CPU usage percentage", "percentage"),
            ("memory_usage", "Memory usage percentage", "percentage"),
            ("disk_usage", "Disk usage percentage", "percentage"),
            ("network_io", "Network I/O bytes per second", "bytes/sec"),
            ("disk_io", "Disk I/O operations per second", "ops/sec"),
            ("process_count", "Number of active processes", "count"),
            ("thread_count", "Number of active threads", "count"),
            ("open_files", "Number of open file descriptors", "count"),
            ("load_average", "System load average", "load"),
            ("uptime", "System uptime", "seconds"),
        ]
        
        for name, description, unit in system_metrics:
            self.system_metrics[name] = MetricSeries(name, description, unit)
    
    def add_threshold(self, threshold: PerformanceThreshold):
        """Add a performance threshold"""
        self.thresholds[threshold.metric_name] = threshold
        self.logger.info(f"Added threshold: {threshold.metric_name}")
    
    def remove_threshold(self, metric_name: str):
        """Remove a performance threshold"""
        if metric_name in self.thresholds:
            del self.thresholds[metric_name]
            self.logger.info(f"Removed threshold: {metric_name}")
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            self.logger.warning("Performance monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        self.logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Check thresholds
                await self._check_thresholds()
                
                # Update performance history
                await self._update_performance_history()
                
                # Auto-scaling logic
                if self.auto_scaling_enabled:
                    await self._auto_scaling_logic()
                
                # Wait for next collection cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._record_system_metric("cpu_usage", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self._record_system_metric("memory_usage", memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self._record_system_metric("disk_usage", (disk.used / disk.total) * 100)
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = network.bytes_sent + network.bytes_recv
            self._record_system_metric("network_io", network_io)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self._record_system_metric("disk_io", disk_io.read_count + disk_io.write_count)
            
            # Process and thread count
            self._record_system_metric("process_count", len(psutil.pids()))
            self._record_system_metric("thread_count", threading.active_count())
            
            # Load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()[0]
                self._record_system_metric("load_average", load_avg)
            except (AttributeError, OSError):
                pass
            
            # Uptime
            uptime = time.time() - psutil.boot_time()
            self._record_system_metric("uptime", uptime)
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _record_system_metric(self, name: str, value: float):
        """Record a system metric"""
        if name in self.system_metrics:
            self.system_metrics[name].add_point(value)
            
            # Update peak and lowest values
            if name not in self.peak_values or value > self.peak_values[name]:
                self.peak_values[name] = value
            
            if name not in self.lowest_values or value < self.lowest_values[name]:
                self.lowest_values[name] = value
            
            # Update performance history
            self.performance_history[name].append({
                'timestamp': time.time(),
                'value': value
            })
    
    async def _check_thresholds(self):
        """Check all performance thresholds"""
        for metric_name, threshold in self.thresholds.items():
            try:
                # Get current value
                current_value = self._get_current_metric_value(metric_name)
                if current_value is None:
                    continue
                
                # Check threshold
                result = threshold.check_threshold(current_value)
                
                # Handle threshold violations
                if result['status'] in ['warning', 'critical']:
                    await self._handle_threshold_violation(result, threshold)
                
            except Exception as e:
                self.logger.error(f"Error checking threshold {metric_name}: {e}")
    
    def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric"""
        # Check system metrics first
        if metric_name in self.system_metrics:
            latest = self.system_metrics[metric_name].get_latest()
            if latest:
                return latest.value
        
        # Check service metrics
        for service_name, service_metrics in self.service_metrics.items():
            if metric_name in service_metrics.metrics:
                latest = service_metrics.metrics[metric_name].get_latest()
                if latest:
                    return latest.value
        
        # Check performance history
        if metric_name in self.performance_history and self.performance_history[metric_name]:
            return self.performance_history[metric_name][-1]['value']
        
        return None
    
    async def _handle_threshold_violation(self, result: Dict[str, Any], threshold: PerformanceThreshold):
        """Handle threshold violation"""
        # Create alert
        alert = PerformanceAlert(
            timestamp=time.time(),
            threshold_name=result['threshold_name'],
            status=result['status'],
            message=result['message'],
            current_value=result['current_value'],
            threshold_value=threshold.critical_threshold if result['status'] == 'critical' else threshold.warning_threshold,
            severity=result['status']
        )
        
        self.alerts.append(alert)
        
        # Log the alert
        log_level = logging.ERROR if result['status'] == 'critical' else logging.WARNING
        self.logger.log(log_level, f"Performance Alert: {result['message']}")
        
        # Execute threshold action
        await self._execute_threshold_action(threshold, result)
    
    async def _execute_threshold_action(self, threshold: PerformanceThreshold, result: Dict[str, Any]):
        """Execute threshold action"""
        try:
            if threshold.action == "log":
                # Already logged above
                pass
            elif threshold.action == "alert":
                # Could integrate with external alerting system
                self.logger.warning(f"Alert triggered: {result['message']}")
            elif threshold.action == "auto_scale":
                await self._trigger_auto_scaling(threshold.metric_name, result)
            elif threshold.action == "restart":
                self.logger.critical(f"Restart action triggered: {result['message']}")
                # Could implement service restart logic here
            
        except Exception as e:
            self.logger.error(f"Error executing threshold action: {e}")
    
    async def _trigger_auto_scaling(self, metric_name: str, result: Dict[str, Any]):
        """Trigger auto-scaling based on metric"""
        if not self.auto_scaling_enabled:
            return
        
        scaling_config = self.scaling_thresholds.get(metric_name, {})
        if not scaling_config:
            return
        
        try:
            # Implement auto-scaling logic here
            self.logger.info(f"Auto-scaling triggered for {metric_name}: {result['message']}")
            
            # Example: Scale up if CPU usage is high
            if metric_name == "cpu_usage" and result['status'] == 'critical':
                await self._scale_up_resources()
            
        except Exception as e:
            self.logger.error(f"Error in auto-scaling: {e}")
    
    async def _scale_up_resources(self):
        """Scale up system resources"""
        # This is a placeholder for actual scaling logic
        # Could involve:
        # - Starting additional worker processes
        # - Allocating more memory
        # - Spinning up additional containers
        # - Increasing thread pool size
        self.logger.info("Scaling up system resources")
    
    async def _update_performance_history(self):
        """Update performance history and cleanup old data"""
        current_time = time.time()
        cutoff_time = current_time - (24 * 60 * 60)  # 24 hours
        
        for metric_name, history in self.performance_history.items():
            # Remove old entries
            while history and history[0]['timestamp'] < cutoff_time:
                history.popleft()
    
    async def _auto_scaling_logic(self):
        """Main auto-scaling logic"""
        if not self.auto_scaling_enabled:
            return
        
        try:
            # Analyze current performance
            cpu_usage = self._get_current_metric_value("cpu_usage")
            memory_usage = self._get_current_metric_value("memory_usage")
            
            if cpu_usage and memory_usage:
                # Simple auto-scaling rules
                if cpu_usage > 80 and memory_usage > 80:
                    await self._scale_up_resources()
                elif cpu_usage < 20 and memory_usage < 20:
                    # Could implement scale down logic
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error in auto-scaling logic: {e}")
    
    def get_performance_summary(self, window_seconds: Optional[float] = None) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        summary = {
            'timestamp': time.time(),
            'system_metrics': {},
            'service_metrics': {},
            'thresholds': {},
            'alerts': [],
            'performance_history': {},
            'peak_values': self.peak_values.copy(),
            'lowest_values': self.lowest_values.copy(),
            'monitoring_status': {
                'is_monitoring': self.is_monitoring,
                'monitoring_interval': self.monitoring_interval,
                'auto_scaling_enabled': self.auto_scaling_enabled
            }
        }
        
        # System metrics summary
        for name, series in self.system_metrics.items():
            stats = series.get_statistics(window_seconds)
            if stats:
                summary['system_metrics'][name] = {
                    'description': series.description,
                    'unit': series.unit,
                    'statistics': stats
                }
        
        # Service metrics summary
        for service_name, service_metrics in self.service_metrics.items():
            summary['service_metrics'][service_name] = service_metrics.get_summary(window_seconds)
        
        # Thresholds summary
        for name, threshold in self.thresholds.items():
            summary['thresholds'][name] = {
                'warning_threshold': threshold.warning_threshold,
                'critical_threshold': threshold.critical_threshold,
                'operator': threshold.operator,
                'enabled': threshold.enabled,
                'action': threshold.action
            }
        
        # Recent alerts
        recent_alerts = []
        current_time = time.time()
        for alert in reversed(list(self.alerts)):
            if window_seconds is None or (current_time - alert.timestamp) <= window_seconds:
                recent_alerts.append({
                    'timestamp': alert.timestamp,
                    'threshold_name': alert.threshold_name,
                    'status': alert.status,
                    'message': alert.message,
                    'current_value': alert.current_value,
                    'severity': alert.severity
                })
        
        summary['alerts'] = recent_alerts
        
        # Performance history summary
        for metric_name, history in self.performance_history.items():
            if history:
                values = [entry['value'] for entry in history]
                summary['performance_history'][metric_name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'mean': statistics.mean(values),
                    'latest': values[-1] if values else None
                }
        
        return summary
    
    def export_metrics(self, format: str = "json", file_path: Optional[str] = None) -> str:
        """Export metrics in specified format"""
        summary = self.get_performance_summary()
        
        if format.lower() == "json":
            output = json.dumps(summary, indent=2, default=str)
        elif format.lower() == "csv":
            output = self._export_to_csv(summary)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(output)
            self.logger.info(f"Metrics exported to {file_path}")
        
        return output
    
    def _export_to_csv(self, summary: Dict[str, Any]) -> str:
        """Export summary to CSV format"""
        # This is a simplified CSV export
        # In a real implementation, you'd want more sophisticated CSV handling
        lines = []
        
        # System metrics
        lines.append("Metric,Description,Unit,Count,Min,Max,Mean,Latest")
        for name, data in summary['system_metrics'].items():
            stats = data['statistics']
            lines.append(f"{name},{data['description']},{data['unit']},{stats.get('count', 0)},{stats.get('min', 0)},{stats.get('max', 0)},{stats.get('mean', 0)},{stats.get('latest', 0)}")
        
        return "\n".join(lines)
    
    def add_service_monitoring(self, service_name: str, metrics: Dict[str, Dict[str, Any]]):
        """Add monitoring for a specific service"""
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = ServiceMetrics(service_name)
        
        service_metrics = self.service_metrics[service_name]
        
        for metric_name, metric_config in metrics.items():
            service_metrics.add_metric(
                name=metric_name,
                description=metric_config.get('description', ''),
                unit=metric_config.get('unit', ''),
                labels=metric_config.get('labels', {})
            )
        
        self.logger.info(f"Added monitoring for service: {service_name}")
    
    def record_service_metric(self, service_name: str, metric_name: str, value: float, 
                            labels: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record a metric for a specific service"""
        if service_name in self.service_metrics:
            service_metrics = self.service_metrics[service_name]
            if metric_name in service_metrics.metrics:
                service_metrics.metrics[metric_name].add_point(value, labels, metadata)
    
    def get_service_metrics(self, service_name: str) -> Optional[ServiceMetrics]:
        """Get metrics for a specific service"""
        return self.service_metrics.get(service_name)
    
    def get_alert_history(self, window_seconds: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get alert history within specified time window"""
        current_time = time.time()
        alerts = []
        
        for alert in reversed(list(self.alerts)):
            if window_seconds is None or (current_time - alert.timestamp) <= window_seconds:
                alerts.append({
                    'timestamp': alert.timestamp,
                    'threshold_name': alert.threshold_name,
                    'status': alert.status,
                    'message': alert.message,
                    'current_value': alert.current_value,
                    'threshold_value': alert.threshold_value,
                    'service_name': alert.service_name,
                    'severity': alert.severity
                })
        
        return alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.logger.info("All alerts cleared")
    
    def get_threshold_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all thresholds"""
        status = {}
        
        for name, threshold in self.thresholds.items():
            current_value = self._get_current_metric_value(name)
            threshold_result = threshold.check_threshold(current_value) if current_value is not None else None
            
            status[name] = {
                'warning_threshold': threshold.warning_threshold,
                'critical_threshold': threshold.critical_threshold,
                'operator': threshold.operator,
                'enabled': threshold.enabled,
                'action': threshold.action,
                'current_value': current_value,
                'status': threshold_result['status'] if threshold_result else 'unknown'
            }
        
        return status


# Factory function for easy integration
def create_performance_monitor(config: Optional[Dict[str, Any]] = None) -> EnhancedPerformanceMonitor:
    """Factory function to create a performance monitor instance"""
    return EnhancedPerformanceMonitor(config)


# Example usage and integration
if __name__ == "__main__":
    # Example configuration
    config = {
        'monitoring_interval': 5.0,
        'auto_scaling_enabled': True,
        'scaling_thresholds': {
            'cpu_usage': {'scale_up_threshold': 80, 'scale_down_threshold': 20},
            'memory_usage': {'scale_up_threshold': 85, 'scale_down_threshold': 30}
        }
    }
    
    # Create monitor
    monitor = create_performance_monitor(config)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Keep running
        asyncio.run(asyncio.sleep(60))
    except KeyboardInterrupt:
        print("Stopping performance monitor...")
    finally:
        monitor.stop_monitoring()
        
        # Export final metrics
        summary = monitor.get_performance_summary()
        print("Final Performance Summary:")
        print(json.dumps(summary, indent=2, default=str))
