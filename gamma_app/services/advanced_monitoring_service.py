"""
Advanced Monitoring Service with Real-time Metrics and Alerting
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict, deque

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class MetricType(Enum):
    """Types of metrics to monitor"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    APPLICATION = "application"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    CUSTOM = "custom"

class AlertLevel(Enum):
    """Alert levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Metric:
    """Metric data structure"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    name: str
    description: str
    level: AlertLevel
    status: AlertStatus
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric_name: str
    condition: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: float
    level: AlertLevel
    duration: int = 0  # seconds to wait before triggering
    cooldown: int = 300  # seconds between alerts
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    collection_interval: int = 10  # seconds
    retention_days: int = 30
    max_metrics_per_type: int = 10000
    alert_cooldown: int = 300  # seconds
    enable_system_metrics: bool = True
    enable_application_metrics: bool = True
    enable_custom_metrics: bool = True
    auto_cleanup: bool = True
    cleanup_interval: int = 3600  # seconds

class AdvancedMonitoringService:
    """Advanced Monitoring Service with Real-time Metrics and Alerting"""
    
    def __init__(self):
        self.config = MonitoringConfig()
        self.metrics = defaultdict(lambda: deque(maxlen=self.config.max_metrics_per_type))
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = []
        self.metric_collectors = {}
        self.alert_handlers = []
        self.is_running = False
        self.collection_task = None
        self.cleanup_task = None
        
        # Initialize system metrics collector
        if self.config.enable_system_metrics:
            self._initialize_system_metrics()
        
        # Initialize alert rules
        self._initialize_default_alert_rules()
        
        logger.info("Advanced Monitoring Service initialized")
    
    def _initialize_system_metrics(self):
        """Initialize system metrics collection"""
        try:
            # CPU metrics
            self.metric_collectors[MetricType.CPU] = {
                'collector': self._collect_cpu_metrics,
                'interval': 5
            }
            
            # Memory metrics
            self.metric_collectors[MetricType.MEMORY] = {
                'collector': self._collect_memory_metrics,
                'interval': 5
            }
            
            # Disk metrics
            self.metric_collectors[MetricType.DISK] = {
                'collector': self._collect_disk_metrics,
                'interval': 30
            }
            
            # Network metrics
            self.metric_collectors[MetricType.NETWORK] = {
                'collector': self._collect_network_metrics,
                'interval': 10
            }
            
            logger.info("System metrics collectors initialized")
            
        except Exception as e:
            logger.error(f"Error initializing system metrics: {e}")
    
    def _initialize_default_alert_rules(self):
        """Initialize default alert rules"""
        try:
            default_rules = [
                AlertRule(
                    name="High CPU Usage",
                    metric_name="cpu_percent",
                    condition=">",
                    threshold=80.0,
                    level=AlertLevel.WARNING,
                    duration=60
                ),
                AlertRule(
                    name="Critical CPU Usage",
                    metric_name="cpu_percent",
                    condition=">",
                    threshold=95.0,
                    level=AlertLevel.CRITICAL,
                    duration=30
                ),
                AlertRule(
                    name="High Memory Usage",
                    metric_name="memory_percent",
                    condition=">",
                    threshold=85.0,
                    level=AlertLevel.WARNING,
                    duration=60
                ),
                AlertRule(
                    name="Critical Memory Usage",
                    metric_name="memory_percent",
                    condition=">",
                    threshold=95.0,
                    level=AlertLevel.CRITICAL,
                    duration=30
                ),
                AlertRule(
                    name="Low Disk Space",
                    metric_name="disk_percent",
                    condition=">",
                    threshold=90.0,
                    level=AlertLevel.WARNING,
                    duration=0
                ),
                AlertRule(
                    name="Critical Disk Space",
                    metric_name="disk_percent",
                    condition=">",
                    threshold=95.0,
                    level=AlertLevel.CRITICAL,
                    duration=0
                )
            ]
            
            for rule in default_rules:
                self.alert_rules[rule.name] = rule
            
            logger.info(f"Initialized {len(default_rules)} default alert rules")
            
        except Exception as e:
            logger.error(f"Error initializing default alert rules: {e}")
    
    async def start_monitoring(self):
        """Start the monitoring service"""
        try:
            if self.is_running:
                logger.warning("Monitoring service is already running")
                return
            
            self.is_running = True
            
            # Start metric collection
            self.collection_task = asyncio.create_task(self._metric_collection_loop())
            
            # Start cleanup task
            if self.config.auto_cleanup:
                self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Monitoring service started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring service: {e}")
            self.is_running = False
            raise
    
    async def stop_monitoring(self):
        """Stop the monitoring service"""
        try:
            if not self.is_running:
                logger.warning("Monitoring service is not running")
                return
            
            self.is_running = False
            
            # Cancel tasks
            if self.collection_task:
                self.collection_task.cancel()
                try:
                    await self.collection_task
                except asyncio.CancelledError:
                    pass
            
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Monitoring service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring service: {e}")
    
    async def _metric_collection_loop(self):
        """Main metric collection loop"""
        try:
            while self.is_running:
                start_time = time.time()
                
                # Collect metrics from all collectors
                for metric_type, collector_info in self.metric_collectors.items():
                    try:
                        collector = collector_info['collector']
                        interval = collector_info['interval']
                        
                        # Check if it's time to collect this metric
                        if hasattr(self, f'_last_collection_{metric_type.value}'):
                            last_collection = getattr(self, f'_last_collection_{metric_type.value}')
                            if time.time() - last_collection < interval:
                                continue
                        
                        # Collect metrics
                        metrics = await collector()
                        if metrics:
                            for metric in metrics:
                                self.metrics[metric_type].append(metric)
                        
                        # Update last collection time
                        setattr(self, f'_last_collection_{metric_type.value}', time.time())
                        
                    except Exception as e:
                        logger.error(f"Error collecting {metric_type.value} metrics: {e}")
                
                # Check alert rules
                await self._check_alert_rules()
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.collection_interval - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("Metric collection loop cancelled")
        except Exception as e:
            logger.error(f"Error in metric collection loop: {e}")
    
    async def _cleanup_loop(self):
        """Cleanup old metrics loop"""
        try:
            while self.is_running:
                await asyncio.sleep(self.config.cleanup_interval)
                await self.cleanup_old_metrics()
                
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
    
    async def _collect_cpu_metrics(self) -> List[Metric]:
        """Collect CPU metrics"""
        try:
            metrics = []
            timestamp = datetime.utcnow()
            
            # CPU percentage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(Metric(
                name="cpu_percent",
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                tags={"type": "system"}
            ))
            
            # CPU per core
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            for i, core_percent in enumerate(cpu_per_core):
                metrics.append(Metric(
                    name="cpu_core_percent",
                    value=core_percent,
                    unit="percent",
                    timestamp=timestamp,
                    tags={"type": "system", "core": str(i)}
                ))
            
            # CPU load average
            load_avg = psutil.getloadavg()
            for i, load in enumerate(load_avg):
                metrics.append(Metric(
                    name="cpu_load_avg",
                    value=load,
                    unit="load",
                    timestamp=timestamp,
                    tags={"type": "system", "period": str(i)}
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
            return []
    
    async def _collect_memory_metrics(self) -> List[Metric]:
        """Collect memory metrics"""
        try:
            metrics = []
            timestamp = datetime.utcnow()
            
            # Virtual memory
            virtual_memory = psutil.virtual_memory()
            metrics.append(Metric(
                name="memory_percent",
                value=virtual_memory.percent,
                unit="percent",
                timestamp=timestamp,
                tags={"type": "system"}
            ))
            
            metrics.append(Metric(
                name="memory_used",
                value=virtual_memory.used,
                unit="bytes",
                timestamp=timestamp,
                tags={"type": "system"}
            ))
            
            metrics.append(Metric(
                name="memory_available",
                value=virtual_memory.available,
                unit="bytes",
                timestamp=timestamp,
                tags={"type": "system"}
            ))
            
            # Swap memory
            swap_memory = psutil.swap_memory()
            metrics.append(Metric(
                name="swap_percent",
                value=swap_memory.percent,
                unit="percent",
                timestamp=timestamp,
                tags={"type": "system"}
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
            return []
    
    async def _collect_disk_metrics(self) -> List[Metric]:
        """Collect disk metrics"""
        try:
            metrics = []
            timestamp = datetime.utcnow()
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            metrics.append(Metric(
                name="disk_percent",
                value=(disk_usage.used / disk_usage.total) * 100,
                unit="percent",
                timestamp=timestamp,
                tags={"type": "system", "mount": "/"}
            ))
            
            metrics.append(Metric(
                name="disk_used",
                value=disk_usage.used,
                unit="bytes",
                timestamp=timestamp,
                tags={"type": "system", "mount": "/"}
            ))
            
            metrics.append(Metric(
                name="disk_free",
                value=disk_usage.free,
                unit="bytes",
                timestamp=timestamp,
                tags={"type": "system", "mount": "/"}
            ))
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics.append(Metric(
                    name="disk_read_bytes",
                    value=disk_io.read_bytes,
                    unit="bytes",
                    timestamp=timestamp,
                    tags={"type": "system"}
                ))
                
                metrics.append(Metric(
                    name="disk_write_bytes",
                    value=disk_io.write_bytes,
                    unit="bytes",
                    timestamp=timestamp,
                    tags={"type": "system"}
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
            return []
    
    async def _collect_network_metrics(self) -> List[Metric]:
        """Collect network metrics"""
        try:
            metrics = []
            timestamp = datetime.utcnow()
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                metrics.append(Metric(
                    name="network_bytes_sent",
                    value=network_io.bytes_sent,
                    unit="bytes",
                    timestamp=timestamp,
                    tags={"type": "system"}
                ))
                
                metrics.append(Metric(
                    name="network_bytes_recv",
                    value=network_io.bytes_recv,
                    unit="bytes",
                    timestamp=timestamp,
                    tags={"type": "system"}
                ))
                
                metrics.append(Metric(
                    name="network_packets_sent",
                    value=network_io.packets_sent,
                    unit="packets",
                    timestamp=timestamp,
                    tags={"type": "system"}
                ))
                
                metrics.append(Metric(
                    name="network_packets_recv",
                    value=network_io.packets_recv,
                    unit="packets",
                    timestamp=timestamp,
                    tags={"type": "system"}
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
            return []
    
    async def add_custom_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Add a custom metric"""
        try:
            metric = Metric(
                name=name,
                value=value,
                unit=unit,
                timestamp=datetime.utcnow(),
                tags=tags or {},
                metadata=metadata or {}
            )
            
            self.metrics[MetricType.CUSTOM].append(metric)
            
            logger.debug(f"Added custom metric: {name}={value} {unit}")
            
        except Exception as e:
            logger.error(f"Error adding custom metric: {e}")
    
    async def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule"""
        try:
            self.alert_rules[rule.name] = rule
            logger.info(f"Added alert rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error adding alert rule: {e}")
    
    async def remove_alert_rule(self, rule_name: str):
        """Remove an alert rule"""
        try:
            if rule_name in self.alert_rules:
                del self.alert_rules[rule_name]
                logger.info(f"Removed alert rule: {rule_name}")
            else:
                logger.warning(f"Alert rule not found: {rule_name}")
                
        except Exception as e:
            logger.error(f"Error removing alert rule: {e}")
    
    async def _check_alert_rules(self):
        """Check all alert rules"""
        try:
            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Get latest metric value
                metric_value = await self._get_latest_metric_value(rule.metric_name)
                if metric_value is None:
                    continue
                
                # Check if condition is met
                condition_met = self._evaluate_condition(metric_value, rule.condition, rule.threshold)
                
                if condition_met:
                    # Check if alert already exists
                    alert_key = f"{rule_name}_{rule.metric_name}"
                    
                    if alert_key not in self.active_alerts:
                        # Create new alert
                        alert = Alert(
                            id=alert_key,
                            name=rule.name,
                            description=f"{rule.metric_name} {rule.condition} {rule.threshold} (current: {metric_value})",
                            level=rule.level,
                            status=AlertStatus.ACTIVE,
                            metric_name=rule.metric_name,
                            threshold=rule.threshold,
                            current_value=metric_value,
                            timestamp=datetime.utcnow(),
                            tags=rule.tags
                        )
                        
                        self.active_alerts[alert_key] = alert
                        self.alert_history.append(alert)
                        
                        # Send alert
                        await self._send_alert(alert)
                        
                        logger.warning(f"Alert triggered: {rule.name} - {alert.description}")
                
                else:
                    # Check if alert should be resolved
                    alert_key = f"{rule_name}_{rule.metric_name}"
                    if alert_key in self.active_alerts:
                        alert = self.active_alerts[alert_key]
                        if alert.status == AlertStatus.ACTIVE:
                            # Resolve alert
                            alert.status = AlertStatus.RESOLVED
                            alert.resolved_at = datetime.utcnow()
                            
                            # Send resolution notification
                            await self._send_alert_resolution(alert)
                            
                            logger.info(f"Alert resolved: {rule.name}")
                
        except Exception as e:
            logger.error(f"Error checking alert rules: {e}")
    
    async def _get_latest_metric_value(self, metric_name: str) -> Optional[float]:
        """Get the latest value for a metric"""
        try:
            # Search through all metric types
            for metric_type, metrics_deque in self.metrics.items():
                for metric in reversed(metrics_deque):
                    if metric.name == metric_name:
                        return metric.value
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest metric value: {e}")
            return None
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        try:
            if condition == ">":
                return value > threshold
            elif condition == "<":
                return value < threshold
            elif condition == ">=":
                return value >= threshold
            elif condition == "<=":
                return value <= threshold
            elif condition == "==":
                return value == threshold
            elif condition == "!=":
                return value != threshold
            else:
                logger.error(f"Unknown condition: {condition}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    async def _send_alert(self, alert: Alert):
        """Send alert notification"""
        try:
            # Call all registered alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def _send_alert_resolution(self, alert: Alert):
        """Send alert resolution notification"""
        try:
            # Call all registered alert handlers
            for handler in self.alert_handlers:
                try:
                    await handler(alert, is_resolution=True)
                except Exception as e:
                    logger.error(f"Error in alert resolution handler: {e}")
            
        except Exception as e:
            logger.error(f"Error sending alert resolution: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add an alert handler"""
        try:
            self.alert_handlers.append(handler)
            logger.info("Added alert handler")
            
        except Exception as e:
            logger.error(f"Error adding alert handler: {e}")
    
    async def get_metrics(self, metric_type: Optional[MetricType] = None, limit: int = 100) -> List[Metric]:
        """Get metrics"""
        try:
            if metric_type:
                metrics = list(self.metrics[metric_type])
            else:
                metrics = []
                for metrics_deque in self.metrics.values():
                    metrics.extend(metrics_deque)
            
            # Sort by timestamp (newest first)
            metrics.sort(key=lambda x: x.timestamp, reverse=True)
            
            return metrics[:limit]
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        try:
            active_alerts = [alert for alert in self.active_alerts.values() if alert.status == AlertStatus.ACTIVE]
            return sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        try:
            return sorted(self.alert_history, key=lambda x: x.timestamp, reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = acknowledged_by
                
                logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
                
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.utcnow()
                
                logger.info(f"Alert resolved: {alert_id}")
                
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        try:
            summary = {
                'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
                'metrics_by_type': {metric_type.value: len(metrics) for metric_type, metrics in self.metrics.items()},
                'active_alerts': len([alert for alert in self.active_alerts.values() if alert.status == AlertStatus.ACTIVE]),
                'total_alerts': len(self.alert_history),
                'alert_rules': len(self.alert_rules),
                'enabled_rules': len([rule for rule in self.alert_rules.values() if rule.enabled]),
                'service_status': 'running' if self.is_running else 'stopped'
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}
    
    async def get_metric_statistics(self, metric_name: str, period_hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a specific metric"""
        try:
            # Get metrics for the specified period
            cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
            values = []
            
            for metrics_deque in self.metrics.values():
                for metric in metrics_deque:
                    if metric.name == metric_name and metric.timestamp >= cutoff_time:
                        values.append(metric.value)
            
            if not values:
                return {'error': 'No data available for the specified period'}
            
            # Calculate statistics
            import statistics
            
            stats = {
                'metric_name': metric_name,
                'period_hours': period_hours,
                'data_points': len(values),
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'percentile_95': statistics.quantiles(values, n=20)[18] if len(values) > 1 else values[0],
                'percentile_99': statistics.quantiles(values, n=100)[98] if len(values) > 1 else values[0]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting metric statistics: {e}")
            return {'error': str(e)}
    
    async def cleanup_old_metrics(self):
        """Clean up old metrics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=self.config.retention_days)
            
            for metric_type, metrics_deque in self.metrics.items():
                # Remove old metrics
                while metrics_deque and metrics_deque[0].timestamp < cutoff_time:
                    metrics_deque.popleft()
            
            # Clean up old alerts
            self.alert_history = [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
            
            logger.info("Cleaned up old metrics and alerts")
            
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
    
    async def export_metrics(self, format: str = "json", period_hours: int = 24) -> str:
        """Export metrics in specified format"""
        try:
            # Get metrics for the specified period
            cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
            export_data = []
            
            for metric_type, metrics_deque in self.metrics.items():
                for metric in metrics_deque:
                    if metric.timestamp >= cutoff_time:
                        export_data.append({
                            'name': metric.name,
                            'value': metric.value,
                            'unit': metric.unit,
                            'timestamp': metric.timestamp.isoformat(),
                            'type': metric_type.value,
                            'tags': metric.tags,
                            'metadata': metric.metadata
                        })
            
            if format.lower() == "json":
                return json.dumps(export_data, indent=2)
            elif format.lower() == "csv":
                import csv
                import io
                
                output = io.StringIO()
                if export_data:
                    writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
                    writer.writeheader()
                    writer.writerows(export_data)
                return output.getvalue()
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return ""
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Monitoring Service',
                'status': 'healthy' if self.is_running else 'stopped',
                'timestamp': datetime.utcnow().isoformat(),
                'config': {
                    'collection_interval': self.config.collection_interval,
                    'retention_days': self.config.retention_days,
                    'max_metrics_per_type': self.config.max_metrics_per_type,
                    'enable_system_metrics': self.config.enable_system_metrics,
                    'enable_application_metrics': self.config.enable_application_metrics,
                    'enable_custom_metrics': self.config.enable_custom_metrics
                },
                'metrics': {
                    'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
                    'metrics_by_type': {metric_type.value: len(metrics) for metric_type, metrics in self.metrics.items()}
                },
                'alerts': {
                    'active_alerts': len([alert for alert in self.active_alerts.values() if alert.status == AlertStatus.ACTIVE]),
                    'total_alerts': len(self.alert_history),
                    'alert_rules': len(self.alert_rules)
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Monitoring Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























