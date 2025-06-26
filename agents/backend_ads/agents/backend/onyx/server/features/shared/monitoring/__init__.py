"""
Shared Monitoring Services

Provides centralized monitoring functionality for all modules including:
- Metrics collection and aggregation
- Health checks and service monitoring
- Performance tracking
- Alerting and notifications
- System resource monitoring
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: Union[int, float]
    type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

@dataclass
class HealthCheck:
    """Health check configuration"""
    name: str
    check_func: Callable
    interval: int = 60  # seconds
    timeout: int = 30   # seconds
    critical: bool = False
    
@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class MetricsCollector:
    """Metrics collection and aggregation"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def increment(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self._lock:
            self.counters[name] += value
            metric = Metric(name=name, value=value, type=MetricType.COUNTER, tags=tags or {})
            self.metrics[name].append(metric)
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        with self._lock:
            self.gauges[name] = value
            metric = Metric(name=name, value=value, type=MetricType.GAUGE, tags=tags or {})
            self.metrics[name].append(metric)
    
    def timer(self, name: str):
        """Timer context manager"""
        return TimerContext(self, name)
    
    def record_time(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record timing metric"""
        with self._lock:
            self.timers[name].append(duration)
            # Keep only recent timings
            if len(self.timers[name]) > 1000:
                self.timers[name] = self.timers[name][-500:]
            
            metric = Metric(name=name, value=duration, type=MetricType.TIMER, tags=tags or {})
            self.metrics[name].append(metric)
    
    def get_metrics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get current metrics"""
        with self._lock:
            if name:
                return {
                    'counter': self.counters.get(name, 0),
                    'gauge': self.gauges.get(name, 0.0),
                    'timer_avg': sum(self.timers.get(name, [])) / len(self.timers.get(name, [1])),
                    'history': list(self.metrics.get(name, []))
                }
            
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'timers': {k: {
                    'count': len(v),
                    'avg': sum(v) / len(v) if v else 0,
                    'min': min(v) if v else 0,
                    'max': max(v) if v else 0
                } for k, v in self.timers.items()},
                'total_metrics': sum(len(q) for q in self.metrics.values())
            }

class TimerContext:
    """Timer context manager for measuring execution time"""
    
    def __init__(self, collector: MetricsCollector, name: str):
        self.collector = collector
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.record_time(self.name, duration)

class HealthMonitor:
    """Service health monitoring"""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, HealthStatus] = {}
        self.last_check_times: Dict[str, datetime] = {}
        self.check_results: Dict[str, Any] = {}
        self._monitoring = False
        self._monitor_task = None
    
    def register_health_check(self, health_check: HealthCheck):
        """Register a health check"""
        self.health_checks[health_check.name] = health_check
        self.health_status[health_check.name] = HealthStatus.UNKNOWN
        logger.info(f"Registered health check: {health_check.name}")
    
    async def start_monitoring(self):
        """Start health monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                for name, health_check in self.health_checks.items():
                    last_check = self.last_check_times.get(name)
                    
                    # Check if it's time to run this health check
                    if (last_check is None or 
                        datetime.utcnow() - last_check >= timedelta(seconds=health_check.interval)):
                        
                        await self._run_health_check(name, health_check)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _run_health_check(self, name: str, health_check: HealthCheck):
        """Run individual health check"""
        try:
            start_time = time.time()
            
            # Run the health check with timeout
            result = await asyncio.wait_for(
                self._execute_check(health_check.check_func),
                timeout=health_check.timeout
            )
            
            execution_time = time.time() - start_time
            
            # Determine health status
            if result is True or (isinstance(result, dict) and result.get('healthy', False)):
                status = HealthStatus.HEALTHY
            elif isinstance(result, dict) and result.get('degraded', False):
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            self.health_status[name] = status
            self.check_results[name] = {
                'status': status.value,
                'result': result,
                'execution_time': execution_time,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.last_check_times[name] = datetime.utcnow()
            
        except asyncio.TimeoutError:
            logger.warning(f"Health check '{name}' timed out")
            self.health_status[name] = HealthStatus.UNHEALTHY
            self.check_results[name] = {
                'status': HealthStatus.UNHEALTHY.value,
                'error': 'Timeout',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check '{name}' failed: {e}")
            self.health_status[name] = HealthStatus.UNHEALTHY
            self.check_results[name] = {
                'status': HealthStatus.UNHEALTHY.value,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _execute_check(self, check_func: Callable):
        """Execute health check function"""
        if asyncio.iscoroutinefunction(check_func):
            return await check_func()
        else:
            return check_func()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        overall_status = HealthStatus.HEALTHY
        
        # Determine overall status
        for name, status in self.health_status.items():
            health_check = self.health_checks.get(name)
            
            if status == HealthStatus.UNHEALTHY:
                if health_check and health_check.critical:
                    overall_status = HealthStatus.UNHEALTHY
                    break
                elif overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            elif status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
        
        return {
            'overall_status': overall_status.value,
            'services': dict(self.health_status),
            'details': self.check_results,
            'timestamp': datetime.utcnow().isoformat()
        }

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.metrics_history: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self._monitoring = False
        self._monitor_task = None
    
    async def start_monitoring(self):
        """Start system monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("System monitoring stopped")
    
    async def _monitor_loop(self):
        """System monitoring loop"""
        while self._monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(60)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_percent=disk.percent,
            network_sent_mb=network.bytes_sent / 1024 / 1024 if network else 0,
            network_recv_mb=network.bytes_recv / 1024 / 1024 if network else 0
        )
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        return {
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_used_mb': latest.memory_used_mb,
            'memory_available_mb': latest.memory_available_mb,
            'disk_percent': latest.disk_percent,
            'network_sent_mb': latest.network_sent_mb,
            'network_recv_mb': latest.network_recv_mb,
            'timestamp': latest.timestamp.isoformat()
        }
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get historical metrics"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        filtered_metrics = [
            {
                'cpu_percent': m.cpu_percent,
                'memory_percent': m.memory_percent,
                'memory_used_mb': m.memory_used_mb,
                'disk_percent': m.disk_percent,
                'timestamp': m.timestamp.isoformat()
            }
            for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]
        
        return filtered_metrics

class MonitoringService:
    """Comprehensive monitoring service"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_monitor = HealthMonitor()
        self.system_monitor = SystemMonitor()
        self._initialized = False
    
    async def initialize(self):
        """Initialize monitoring service"""
        if self._initialized:
            return
        
        await self.health_monitor.start_monitoring()
        await self.system_monitor.start_monitoring()
        self._initialized = True
        logger.info("Monitoring service initialized")
    
    async def shutdown(self):
        """Shutdown monitoring service"""
        if not self._initialized:
            return
        
        await self.health_monitor.stop_monitoring()
        await self.system_monitor.stop_monitoring()
        self._initialized = False
        logger.info("Monitoring service shutdown")
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        return {
            'health': self.health_monitor.get_health_status(),
            'system': self.system_monitor.get_current_metrics(),
            'metrics': self.metrics_collector.get_metrics(),
            'monitoring_active': self._initialized,
            'timestamp': datetime.utcnow().isoformat()
        }

# Global monitoring instance
_monitoring_instance: Optional[MonitoringService] = None

def get_monitoring() -> MonitoringService:
    """Get global monitoring instance"""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = MonitoringService()
    return _monitoring_instance

def track_metric(name: str, value: Union[int, float], metric_type: str = "gauge"):
    """Track a metric"""
    monitoring = get_monitoring()
    if metric_type == "counter":
        monitoring.metrics_collector.increment(name, int(value))
    else:
        monitoring.metrics_collector.gauge(name, float(value))

def track_time(name: str):
    """Time tracking decorator/context manager"""
    monitoring = get_monitoring()
    return monitoring.metrics_collector.timer(name)

async def register_health_check(name: str, check_func: Callable, 
                               interval: int = 60, critical: bool = False):
    """Register a health check"""
    health_check = HealthCheck(
        name=name,
        check_func=check_func,
        interval=interval,
        critical=critical
    )
    
    monitoring = get_monitoring()
    monitoring.health_monitor.register_health_check(health_check)

__all__ = [
    'HealthStatus',
    'MetricType',
    'Metric',
    'HealthCheck',
    'SystemMetrics',
    'MetricsCollector',
    'HealthMonitor',
    'SystemMonitor',
    'MonitoringService',
    'get_monitoring',
    'track_metric',
    'track_time',
    'register_health_check'
] 