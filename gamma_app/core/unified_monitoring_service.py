"""
Unified Monitoring Service - Advanced monitoring and observability
Implements comprehensive monitoring with Prometheus, Grafana, and custom metrics
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import time
import psutil
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import aiohttp
import websockets
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info, Enum as PromEnum,
    start_http_server, generate_latest, CONTENT_TYPE_LATEST
)
import threading
import queue
import signal
import sys

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric Types for Prometheus metrics.
    
    Defines the available types of metrics that can be registered
    in the monitoring service.
    """
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    INFO = "info"
    ENUM = "enum"

class AlertLevel(Enum):
    """Alert severity levels.
    
    Defines the severity levels for alerts that can be triggered
    by the monitoring system.
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class HealthStatus(Enum):
    """Health status values for system and component checks.
    
    Represents the possible states of health for monitored components.
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class MetricDefinition:
    """Metric Definition for Prometheus metrics.
    
    :ivar name: Name of the metric
    :ivar description: Description of what the metric measures
    :ivar metric_type: Type of metric (counter, gauge, histogram, etc.)
    :ivar labels: Optional list of label names for the metric
    :ivar buckets: Optional list of buckets for histogram metrics
    :ivar quantiles: Optional list of quantiles for summary metrics
    :ivar states: Optional list of states for enum metrics
    """
    name: str
    description: str
    metric_type: MetricType
    labels: Optional[List[str]] = None
    buckets: Optional[List[float]] = None
    quantiles: Optional[List[float]] = None
    states: Optional[List[str]] = None

@dataclass
class AlertRule:
    """Alert Rule definition.
    
    :ivar name: Name of the alert rule
    :ivar description: Description of what the alert monitors
    :ivar metric_name: Name of the metric to monitor
    :ivar condition: Condition operator (gt, lt, eq, gte, lte)
    :ivar threshold: Threshold value to trigger the alert
    :ivar level: Alert severity level
    :ivar duration: Duration in seconds before alert triggers (0 = immediate)
    :ivar enabled: Whether the alert rule is enabled
    """
    name: str
    description: str
    metric_name: str
    condition: str
    threshold: float
    level: AlertLevel
    duration: int = 0
    enabled: bool = True

@dataclass
class HealthCheck:
    """Health Check definition.
    
    :ivar name: Name of the health check
    :ivar check_function: Async function that performs the health check
    :ivar interval: Interval in seconds between health check runs
    :ivar timeout: Timeout in seconds for the health check
    :ivar enabled: Whether the health check is enabled
    :ivar last_check: Timestamp of the last health check execution
    :ivar last_status: Result of the last health check
    :ivar last_error: Error message from the last failed health check
    """
    name: str
    check_function: Callable
    interval: int = 30
    timeout: int = 10
    enabled: bool = True
    last_check: Optional[datetime] = None
    last_status: HealthStatus = HealthStatus.UNKNOWN
    last_error: Optional[str] = None

@dataclass
class SystemMetrics:
    """System Metrics snapshot.
    
    :ivar timestamp: Timestamp when metrics were collected
    :ivar cpu_percent: CPU usage percentage
    :ivar memory_percent: Memory usage percentage
    :ivar memory_used: Memory used in bytes
    :ivar memory_total: Total memory in bytes
    :ivar disk_percent: Disk usage percentage
    :ivar disk_used: Disk space used in bytes
    :ivar disk_total: Total disk space in bytes
    :ivar network_sent: Network bytes sent
    :ivar network_recv: Network bytes received
    :ivar load_average: System load average (1m, 5m, 15m)
    :ivar process_count: Number of running processes
    """
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    disk_percent: float
    disk_used: int
    disk_total: int
    network_sent: int
    network_recv: int
    load_average: List[float]
    process_count: int

class UnifiedMonitoringService:
    """Unified Monitoring Service - Advanced monitoring and observability.
    
    Implements comprehensive monitoring with Prometheus metrics, alerts,
    health checks, and system metrics collection.
    
    :ivar config: Configuration dictionary for the monitoring service
    :ivar prometheus_port: Port number for Prometheus metrics server
    :ivar grafana_port: Port number for Grafana (if used)
    :ivar metrics: Dictionary mapping metric names to Prometheus metric objects
    :ivar metric_definitions: Dictionary mapping metric names to definitions
    :ivar alert_rules: Dictionary mapping alert rule names to AlertRule instances
    :ivar active_alerts: Dictionary of currently active alerts
    :ivar alert_history: Deque containing alert history (max 1000 entries)
    :ivar health_checks: Dictionary mapping health check names to HealthCheck instances
    :ivar health_status: Dictionary mapping health check names to their status
    :ivar system_metrics_history: Deque containing system metrics history (max 1000 entries)
    :ivar last_system_metrics: Most recent system metrics snapshot
    :ivar monitoring_tasks: List of active monitoring async tasks
    :ivar running: Boolean flag indicating if monitoring is running
    :ivar prometheus_server: Prometheus HTTP server instance
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the Unified Monitoring Service.
        
        :param config: Configuration dictionary with monitoring settings
        :type config: Dict[str, Any]
        :raises ValueError: If config is not a valid dictionary
        """
        # Validate config is a dictionary
        if not isinstance(config, dict):
            raise ValueError(f"Config must be a dictionary, got {type(config)}")
        
        self.config = config
        self.prometheus_port = config.get("prometheus_port", 9090)
        self.grafana_port = config.get("grafana_port", 3000)
        
        # Validate port numbers
        if not isinstance(self.prometheus_port, int) or not (1 <= self.prometheus_port <= 65535):
            logger.warning(f"Invalid prometheus_port: {self.prometheus_port}, using default 9090")
            self.prometheus_port = 9090
        
        if not isinstance(self.grafana_port, int) or not (1 <= self.grafana_port <= 65535):
            logger.warning(f"Invalid grafana_port: {self.grafana_port}, using default 3000")
            self.grafana_port = 3000
        
        # Metrics storage
        self.metrics: Dict[str, Any] = {}
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        
        # Alerts
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # Health checks
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, HealthStatus] = {}
        
        # System metrics
        self.system_metrics_history: deque = deque(maxlen=1000)
        self.last_system_metrics: Optional[SystemMetrics] = None
        
        # Monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.running = False
        
        # Prometheus server
        self.prometheus_server = None
        
        logger.info("UnifiedMonitoringService initialized")
    
    async def initialize(self) -> None:
        """Initialize monitoring service.
        
        Starts Prometheus server, registers default metrics and health checks,
        and starts monitoring tasks.
        
        :raises Exception: If initialization fails
        """
        try:
            # Start Prometheus server
            await self._start_prometheus_server()
            
            # Register default metrics
            await self._register_default_metrics()
            
            # Register default health checks
            await self._register_default_health_checks()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            self.running = True
            logger.info("Monitoring service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing monitoring service: {e}")
            raise
    
    async def _start_prometheus_server(self) -> None:
        """Start Prometheus metrics server.
        
        Starts the HTTP server for Prometheus metrics scraping.
        
        :raises Exception: If server startup fails
        """
        try:
            self.prometheus_server = start_http_server(self.prometheus_port)
            logger.info(f"Prometheus server started on port {self.prometheus_port}")
            
        except Exception as e:
            logger.error(f"Error starting Prometheus server: {e}")
            raise
    
    async def _register_default_metrics(self) -> None:
        """Register default metrics.
        
        Registers system and application metrics including CPU, memory,
        disk, load average, requests, and errors.
        
        :raises Exception: If metric registration fails
        """
        try:
            # Define default metrics using list comprehension for better organization
            default_metrics = [
                # System metrics
                MetricDefinition(
                    name="system_cpu_percent",
                    description="CPU usage percentage",
                    metric_type=MetricType.GAUGE
                ),
                MetricDefinition(
                    name="system_memory_percent",
                    description="Memory usage percentage",
                    metric_type=MetricType.GAUGE
                ),
                MetricDefinition(
                    name="system_disk_percent",
                    description="Disk usage percentage",
                    metric_type=MetricType.GAUGE
                ),
                MetricDefinition(
                    name="system_load_average",
                    description="System load average",
                    metric_type=MetricType.GAUGE,
                    labels=["period"]
                ),
                # Application metrics
                MetricDefinition(
                    name="app_requests_total",
                    description="Total number of requests",
                    metric_type=MetricType.COUNTER,
                    labels=["method", "endpoint", "status"]
                ),
                MetricDefinition(
                    name="app_request_duration_seconds",
                    description="Request duration in seconds",
                    metric_type=MetricType.HISTOGRAM,
                    labels=["method", "endpoint"],
                    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
                ),
                MetricDefinition(
                    name="app_active_connections",
                    description="Number of active connections",
                    metric_type=MetricType.GAUGE
                ),
                MetricDefinition(
                    name="app_errors_total",
                    description="Total number of errors",
                    metric_type=MetricType.COUNTER,
                    labels=["error_type", "severity"]
                )
            ]
            
            # Register all metrics using asyncio.gather for parallel execution
            await asyncio.gather(*[
                self.register_metric(metric) 
                for metric in default_metrics
            ], return_exceptions=True)
            
            # Count successfully registered metrics
            registered_count = len([
                m for m in default_metrics 
                if m.name in self.metrics
            ])
            
            logger.info(f"Default metrics registered: {registered_count}/{len(default_metrics)}")
            
        except Exception as e:
            logger.error(f"Error registering default metrics: {e}")
    
    async def _register_default_health_checks(self) -> None:
        """Register default health checks.
        
        Registers health checks for CPU, memory, and disk usage.
        
        :raises Exception: If health check registration fails
        """
        try:
            # System health checks
            await self.register_health_check(HealthCheck(
                name="system_cpu",
                check_function=self._check_cpu_usage,
                interval=30
            ))
            
            await self.register_health_check(HealthCheck(
                name="system_memory",
                check_function=self._check_memory_usage,
                interval=30
            ))
            
            await self.register_health_check(HealthCheck(
                name="system_disk",
                check_function=self._check_disk_usage,
                interval=60
            ))
            
            logger.info("Default health checks registered")
            
        except Exception as e:
            logger.error(f"Error registering default health checks: {e}")
    
    async def _start_monitoring_tasks(self) -> None:
        """Start monitoring tasks.
        
        Creates and starts async tasks for system metrics collection,
        health checks, and alert evaluation.
        
        :raises Exception: If task creation fails
        """
        try:
            # Define tasks to start using list comprehension
            task_functions = [
                self._collect_system_metrics,
                self._run_health_checks,
                self._evaluate_alerts
            ]
            
            # Create and start all tasks
            tasks = [
                asyncio.create_task(func()) 
                for func in task_functions
            ]
            
            # Ensure monitoring_tasks is a list
            if not isinstance(self.monitoring_tasks, list):
                self.monitoring_tasks = []
            
            self.monitoring_tasks.extend(tasks)
            
            logger.info(f"Monitoring tasks started: {len(tasks)} tasks")
            
        except Exception as e:
            logger.error(f"Error starting monitoring tasks: {e}")
            raise
    
    async def register_metric(self, definition: MetricDefinition) -> None:
        """Register a new metric.
        
        Creates and registers a Prometheus metric based on the definition.
        
        :param definition: Metric definition with name, type, and configuration
        :type definition: MetricDefinition
        :raises ValueError: If metric type is unsupported or definition is invalid
        :raises Exception: If registration fails
        """
        try:
            # Validate definition is a MetricDefinition instance
            if not isinstance(definition, MetricDefinition):
                raise ValueError(f"Definition must be a MetricDefinition instance, got {type(definition)}")
            
            # Validate metric name
            if not definition.name or not isinstance(definition.name, str):
                raise ValueError(f"Metric name must be a non-empty string, got {type(definition.name)}")
            
            if definition.name in self.metrics:
                logger.warning(f"Metric {definition.name} already registered")
                return
            
            # Handle non-iterable labels
            labels = definition.labels if isinstance(definition.labels, list) else []
            
            # Validate label names are strings
            if labels:
                labels = [str(label) for label in labels if isinstance(label, (str, int, float))]
            
            # Create Prometheus metric based on type
            metric = self._create_prometheus_metric(definition, labels)
            
            if metric is None:
                raise ValueError(f"Unsupported metric type: {definition.metric_type}")
            
            # Ensure metrics is a dict
            if not isinstance(self.metrics, dict):
                self.metrics = {}
            
            self.metrics[definition.name] = metric
            self.metric_definitions[definition.name] = definition
            
            logger.info(f"Metric {definition.name} registered")
            
        except Exception as e:
            logger.error(f"Error registering metric {definition.name}: {e}")
            raise
    
    def _create_prometheus_metric(
        self, 
        definition: MetricDefinition, 
        labels: List[str]
    ) -> Optional[Any]:
        """Create Prometheus metric instance.
        
        :param definition: Metric definition
        :type definition: MetricDefinition
        :param labels: List of label names
        :type labels: List[str]
        :return: Prometheus metric instance or None if type unsupported
        :rtype: Optional[Any]
        """
        try:
            if definition.metric_type == MetricType.COUNTER:
                return Counter(definition.name, definition.description, labels)
            elif definition.metric_type == MetricType.GAUGE:
                return Gauge(definition.name, definition.description, labels)
            elif definition.metric_type == MetricType.HISTOGRAM:
                buckets = definition.buckets if isinstance(definition.buckets, list) else None
                return Histogram(definition.name, definition.description, labels, buckets=buckets)
            elif definition.metric_type == MetricType.SUMMARY:
                quantiles = definition.quantiles if isinstance(definition.quantiles, list) else None
                return Summary(definition.name, definition.description, labels, quantiles=quantiles)
            elif definition.metric_type == MetricType.INFO:
                return Info(definition.name, definition.description)
            elif definition.metric_type == MetricType.ENUM:
                states = definition.states if isinstance(definition.states, list) else []
                return PromEnum(definition.name, definition.description, states)
            else:
                return None
        except Exception as e:
            logger.error(f"Error creating Prometheus metric: {e}")
            return None
    
    async def increment_counter(
        self, 
        name: str, 
        value: float = 1, 
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.
        
        :param name: Name of the counter metric
        :type name: str
        :param value: Value to increment by (default: 1)
        :type value: float
        :param labels: Optional dictionary of label values
        :type labels: Optional[Dict[str, str]]
        """
        try:
            if name not in self.metrics:
                logger.warning(f"Metric {name} not found")
                return
            
            metric = self.metrics[name]
            
            # Handle non-iterable labels
            if labels is not None and not isinstance(labels, dict):
                logger.warning(f"Labels must be a dict, got {type(labels)}")
                labels = None
            
            if hasattr(metric, 'labels'):
                if labels:
                    metric.labels(**labels).inc(value)
                else:
                    metric.inc(value)
            else:
                metric.inc(value)
                
        except Exception as e:
            logger.error(f"Error incrementing counter {name}: {e}")
    
    async def set_gauge(
        self, 
        name: str, 
        value: float, 
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Set a gauge metric value.
        
        :param name: Name of the gauge metric
        :type name: str
        :param value: Value to set
        :type value: float
        :param labels: Optional dictionary of label values
        :type labels: Optional[Dict[str, str]]
        """
        try:
            if name not in self.metrics:
                logger.warning(f"Metric {name} not found")
                return
            
            metric = self.metrics[name]
            
            # Handle non-iterable labels
            if labels is not None and not isinstance(labels, dict):
                logger.warning(f"Labels must be a dict, got {type(labels)}")
                labels = None
            
            if hasattr(metric, 'labels'):
                if labels:
                    metric.labels(**labels).set(value)
                else:
                    metric.set(value)
            else:
                metric.set(value)
                
        except Exception as e:
            logger.error(f"Error setting gauge {name}: {e}")
    
    async def observe_histogram(
        self, 
        name: str, 
        value: float, 
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Observe a histogram metric.
        
        :param name: Name of the histogram metric
        :type name: str
        :param value: Value to observe
        :type value: float
        :param labels: Optional dictionary of label values
        :type labels: Optional[Dict[str, str]]
        """
        try:
            if name not in self.metrics:
                logger.warning(f"Metric {name} not found")
                return
            
            metric = self.metrics[name]
            
            # Handle non-iterable labels
            if labels is not None and not isinstance(labels, dict):
                logger.warning(f"Labels must be a dict, got {type(labels)}")
                labels = None
            
            if hasattr(metric, 'labels'):
                if labels:
                    metric.labels(**labels).observe(value)
                else:
                    metric.observe(value)
            else:
                metric.observe(value)
                
        except Exception as e:
            logger.error(f"Error observing histogram {name}: {e}")
    
    async def register_health_check(self, health_check: HealthCheck) -> None:
        """Register a health check.
        
        :param health_check: Health check definition with check function
        :type health_check: HealthCheck
        :raises ValueError: If health_check is invalid
        :raises Exception: If registration fails
        """
        try:
            # Validate health_check is a HealthCheck instance
            if not isinstance(health_check, HealthCheck):
                raise ValueError(f"Health check must be a HealthCheck instance, got {type(health_check)}")
            
            # Validate name
            if not health_check.name or not isinstance(health_check.name, str):
                raise ValueError(f"Health check name must be a non-empty string")
            
            # Validate check_function is callable
            if not callable(health_check.check_function):
                raise ValueError(f"Health check function must be callable")
            
            # Ensure health_checks is a dict
            if not isinstance(self.health_checks, dict):
                self.health_checks = {}
            if not isinstance(self.health_status, dict):
                self.health_status = {}
            
            self.health_checks[health_check.name] = health_check
            self.health_status[health_check.name] = HealthStatus.UNKNOWN
            logger.info(f"Health check {health_check.name} registered")
            
        except Exception as e:
            logger.error(f"Error registering health check {health_check.name}: {e}")
            raise
    
    async def register_alert_rule(self, rule: AlertRule) -> None:
        """Register an alert rule.
        
        :param rule: Alert rule definition with conditions and thresholds
        :type rule: AlertRule
        :raises ValueError: If rule is invalid
        :raises Exception: If registration fails
        """
        try:
            # Validate rule is an AlertRule instance
            if not isinstance(rule, AlertRule):
                raise ValueError(f"Rule must be an AlertRule instance, got {type(rule)}")
            
            # Validate name
            if not rule.name or not isinstance(rule.name, str):
                raise ValueError(f"Alert rule name must be a non-empty string")
            
            # Validate condition
            valid_conditions = ["gt", "lt", "eq", "gte", "lte"]
            if rule.condition not in valid_conditions:
                raise ValueError(f"Condition must be one of {valid_conditions}, got {rule.condition}")
            
            # Validate threshold is numeric
            if not isinstance(rule.threshold, (int, float)):
                raise ValueError(f"Threshold must be a number, got {type(rule.threshold)}")
            
            # Ensure alert_rules is a dict
            if not isinstance(self.alert_rules, dict):
                self.alert_rules = {}
            
            self.alert_rules[rule.name] = rule
            logger.info(f"Alert rule {rule.name} registered")
            
        except Exception as e:
            logger.error(f"Error registering alert rule {rule.name}: {e}")
            raise
    
    async def _collect_system_metrics(self) -> None:
        """Collect system metrics periodically.
        
        Continuously collects system metrics (CPU, memory, disk, network)
        and updates Prometheus metrics. Runs until service is stopped.
        """
        try:
            while self.running:
                try:
                    system_metrics = await self._gather_system_metrics()
                    
                    if system_metrics:
                        # Store metrics
                        self.system_metrics_history.append(system_metrics)
                        self.last_system_metrics = system_metrics
                        
                        # Update Prometheus metrics
                        await self._update_prometheus_system_metrics(system_metrics)
                    
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("System metrics collection cancelled")
    
    async def _gather_system_metrics(self) -> Optional[SystemMetrics]:
        """Gather system metrics from psutil.
        
        :return: SystemMetrics instance or None if collection fails
        :rtype: Optional[SystemMetrics]
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
            
            # Ensure load_avg is iterable
            if not isinstance(load_avg, (list, tuple)):
                load_avg = [0.0, 0.0, 0.0]
            
            # Get process count safely
            try:
                process_count = len(psutil.pids())
            except (AttributeError, TypeError):
                process_count = 0
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_total=memory.total,
                disk_percent=disk.percent,
                disk_used=disk.used,
                disk_total=disk.total,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                load_average=list(load_avg),
                process_count=process_count
            )
        except Exception as e:
            logger.error(f"Error gathering system metrics: {e}")
            return None
    
    async def _update_prometheus_system_metrics(self, metrics: SystemMetrics) -> None:
        """Update Prometheus metrics with system metrics.
        
        :param metrics: System metrics to update
        :type metrics: SystemMetrics
        """
        try:
            # Update basic system metrics using dict for efficiency
            gauge_updates = {
                "system_cpu_percent": metrics.cpu_percent,
                "system_memory_percent": metrics.memory_percent,
                "system_disk_percent": metrics.disk_percent
            }
            
            # Update all gauges using list comprehension for async operations
            await asyncio.gather(*[
                self.set_gauge(name, value)
                for name, value in gauge_updates.items()
            ], return_exceptions=True)
            
            # Handle non-iterable load_average
            load_avg = metrics.load_average if isinstance(metrics.load_average, (list, tuple)) else [0.0, 0.0, 0.0]
            
            # Update load average metrics using list comprehension
            if len(load_avg) >= 3:
                load_periods = ["1m", "5m", "15m"]
                await asyncio.gather(*[
                    self.set_gauge("system_load_average", load_avg[i], {"period": period})
                    for i, period in enumerate(load_periods)
                ], return_exceptions=True)
        except Exception as e:
            logger.error(f"Error updating Prometheus system metrics: {e}")
    
    async def _run_health_checks(self) -> None:
        """Run health checks periodically.
        
        Continuously runs registered health checks at their configured
        intervals. Runs until service is stopped.
        """
        try:
            while self.running:
                # Handle non-iterable health_checks
                if not isinstance(self.health_checks, dict):
                    await asyncio.sleep(10)
                    continue
                
                # Use list comprehension to filter enabled health checks
                enabled_checks = [
                    (name, health_check)
                    for name, health_check in self.health_checks.items()
                    if health_check.enabled and self._should_run_health_check(health_check)
                ]
                
                for name, health_check in enabled_checks:
                    await self._execute_health_check(name, health_check)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except asyncio.CancelledError:
            logger.info("Health checks cancelled")
    
    def _should_run_health_check(self, health_check: HealthCheck) -> bool:
        """Check if health check should run based on interval.
        
        :param health_check: Health check to evaluate
        :type health_check: HealthCheck
        :return: True if health check should run, False otherwise
        :rtype: bool
        """
        if not health_check.last_check:
            return True
        
        time_since_last = datetime.now() - health_check.last_check
        return time_since_last >= timedelta(seconds=health_check.interval)
    
    async def _execute_health_check(self, name: str, health_check: HealthCheck) -> None:
        """Execute a single health check.
        
        :param name: Name of the health check
        :type name: str
        :param health_check: Health check to execute
        :type health_check: HealthCheck
        """
        try:
            start_time = time.time()
            status = await asyncio.wait_for(
                health_check.check_function(),
                timeout=health_check.timeout
            )
            duration = time.time() - start_time
            
            # Update health check
            health_check.last_check = datetime.now()
            health_check.last_status = status
            health_check.last_error = None
            self.health_status[name] = status
            
            logger.debug(f"Health check {name}: {status.value} (took {duration:.2f}s)")
            
        except asyncio.TimeoutError:
            health_check.last_status = HealthStatus.UNHEALTHY
            health_check.last_error = "Timeout"
            self.health_status[name] = HealthStatus.UNHEALTHY
            logger.warning(f"Health check {name} timed out")
            
        except Exception as e:
            health_check.last_status = HealthStatus.UNHEALTHY
            health_check.last_error = str(e)
            self.health_status[name] = HealthStatus.UNHEALTHY
            logger.error(f"Health check {name} failed: {e}")
    
    async def _evaluate_alerts(self) -> None:
        """Evaluate alert rules periodically.
        
        Continuously evaluates all enabled alert rules and triggers
        or resolves alerts based on metric values. Runs until service is stopped.
        """
        try:
            while self.running:
                # Handle non-iterable alert_rules
                if not isinstance(self.alert_rules, dict):
                    await asyncio.sleep(30)
                    continue
                
                # Use list comprehension to filter enabled rules
                enabled_rules = [
                    (name, rule)
                    for name, rule in self.alert_rules.items()
                    if rule.enabled
                ]
                
                for name, rule in enabled_rules:
                    await self._evaluate_single_alert(name, rule)
                
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("Alert evaluation cancelled")
    
    async def _evaluate_single_alert(self, name: str, rule: AlertRule) -> None:
        """Evaluate a single alert rule.
        
        :param name: Name of the alert rule
        :type name: str
        :param rule: Alert rule to evaluate
        :type rule: AlertRule
        """
        try:
            # Get metric value
            metric_value = await self._get_metric_value(rule.metric_name)
            if metric_value is None:
                return
            
            # Evaluate condition using helper method
            alert_triggered = self._check_alert_condition(rule.condition, metric_value, rule.threshold)
            
            # Handle alert
            if alert_triggered:
                await self._trigger_alert(rule, metric_value)
            else:
                await self._resolve_alert(rule)
                
        except Exception as e:
            logger.error(f"Error evaluating alert rule {name}: {e}")
    
    def _check_alert_condition(self, condition: str, value: float, threshold: float) -> bool:
        """Check if alert condition is met.
        
        :param condition: Condition operator (gt, lt, eq, gte, lte)
        :type condition: str
        :param value: Current metric value
        :type value: float
        :param threshold: Threshold value to compare against
        :type threshold: float
        :return: True if condition is met, False otherwise
        :rtype: bool
        """
        condition_map = {
            "gt": value > threshold,
            "lt": value < threshold,
            "eq": value == threshold,
            "gte": value >= threshold,
            "lte": value <= threshold
        }
        return condition_map.get(condition, False)
    
    async def _get_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current metric value.
        
        Attempts to retrieve the current value of a metric from Prometheus
        or system metrics. This is a simplified implementation that should
        be extended to query Prometheus API in production.
        
        :param metric_name: Name of the metric to retrieve
        :type metric_name: str
        :return: Current metric value or None if not available
        :rtype: Optional[float]
        """
        try:
            # Handle non-iterable metrics
            if not isinstance(self.metrics, dict):
                logger.warning("Metrics dictionary is not valid")
                return None
            
            # Try to get from Prometheus metrics
            if metric_name in self.metrics:
                metric = self.metrics[metric_name]
                # This is a simplified approach - in practice, you'd query Prometheus
                # For now, return None to indicate we need to query Prometheus API
                return None
            
            # Try to get from system metrics
            if not self.last_system_metrics:
                return None
            
            metric_map = {
                "system_cpu_percent": self.last_system_metrics.cpu_percent,
                "system_memory_percent": self.last_system_metrics.memory_percent,
                "system_disk_percent": self.last_system_metrics.disk_percent
            }
            
            return metric_map.get(metric_name)
            
        except Exception as e:
            logger.error(f"Error getting metric value {metric_name}: {e}")
            return None
    
    async def _trigger_alert(self, rule: AlertRule, value: float) -> None:
        """Trigger an alert.
        
        Creates and stores an alert if it doesn't already exist for the rule.
        
        :param rule: Alert rule that triggered
        :type rule: AlertRule
        :param value: Current metric value that triggered the alert
        :type value: float
        """
        try:
            # Check if alert already exists for this rule
            existing_alert = self._find_active_alert_for_rule(rule.name)
            if existing_alert:
                return  # Alert already active
            
            alert_id = f"{rule.name}_{int(time.time())}"
            alert = {
                "id": alert_id,
                "rule_name": rule.name,
                "description": rule.description,
                "level": rule.level.value,
                "metric_name": rule.metric_name,
                "threshold": rule.threshold,
                "current_value": value,
                "triggered_at": datetime.now(),
                "resolved_at": None
            }
            
            # Handle non-iterable active_alerts
            if not isinstance(self.active_alerts, dict):
                self.active_alerts = {}
            
            self.active_alerts[alert_id] = alert
            
            # Handle non-iterable alert_history
            if not isinstance(self.alert_history, deque):
                self.alert_history = deque(maxlen=1000)
            
            self.alert_history.append(alert)
            
            logger.warning(f"Alert triggered: {rule.name} - {rule.description}")
            
            # Send alert notification
            await self._send_alert_notification(alert)
                
        except Exception as e:
            logger.error(f"Error triggering alert {rule.name}: {e}")
    
    def _find_active_alert_for_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """Find active alert for a rule.
        
        :param rule_name: Name of the alert rule
        :type rule_name: str
        :return: Active alert dictionary or None if not found
        :rtype: Optional[Dict[str, Any]]
        """
        if not isinstance(self.active_alerts, dict):
            return None
        
        # Use list comprehension to find matching alerts
        matching_alerts = [
            alert for alert in self.active_alerts.values()
            if isinstance(alert, dict) and alert.get("rule_name") == rule_name
        ]
        
        return matching_alerts[0] if matching_alerts else None
    
    async def _resolve_alert(self, rule: AlertRule) -> None:
        """Resolve an alert.
        
        Finds and resolves all active alerts for the given rule.
        
        :param rule: Alert rule to resolve alerts for
        :type rule: AlertRule
        """
        try:
            # Handle non-iterable active_alerts
            if not isinstance(self.active_alerts, dict):
                return
            
            # Use list comprehension to find alerts to resolve
            alerts_to_resolve = [
                (alert_id, alert)
                for alert_id, alert in self.active_alerts.items()
                if isinstance(alert, dict) and alert.get("rule_name") == rule.name
            ]
            
            for alert_id, alert in alerts_to_resolve:
                alert["resolved_at"] = datetime.now()
                del self.active_alerts[alert_id]
                
                logger.info(f"Alert resolved: {rule.name}")
                
                # Send resolution notification
                await self._send_alert_resolution(alert)
                    
        except Exception as e:
            logger.error(f"Error resolving alert {rule.name}: {e}")
    
    async def _send_alert_notification(self, alert: Dict[str, Any]) -> None:
        """Send alert notification.
        
        Sends notification when an alert is triggered. This is a placeholder
        that should be extended to send to Slack, email, PagerDuty, etc.
        
        :param alert: Alert dictionary with alert information
        :type alert: Dict[str, Any]
        """
        try:
            # Validate alert is a dict
            if not isinstance(alert, dict):
                logger.warning(f"Alert must be a dict, got {type(alert)}")
                return
            
            # Placeholder for alert notification
            # In practice, this would send to Slack, email, PagerDuty, etc.
            description = alert.get('description', 'Unknown alert')
            logger.info(f"Alert notification sent: {description}")
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
    
    async def _send_alert_resolution(self, alert: Dict[str, Any]) -> None:
        """Send alert resolution notification.
        
        Sends notification when an alert is resolved. This is a placeholder
        that should be extended to send to Slack, email, PagerDuty, etc.
        
        :param alert: Alert dictionary with alert information
        :type alert: Dict[str, Any]
        """
        try:
            # Validate alert is a dict
            if not isinstance(alert, dict):
                logger.warning(f"Alert must be a dict, got {type(alert)}")
                return
            
            # Placeholder for alert resolution notification
            description = alert.get('description', 'Unknown alert')
            logger.info(f"Alert resolution sent: {description}")
            
        except Exception as e:
            logger.error(f"Error sending alert resolution: {e}")
    
    # Health check functions
    async def _check_cpu_usage(self) -> HealthStatus:
        """Check CPU usage health.
        
        Evaluates CPU usage and returns health status based on thresholds:
        - > 90%: UNHEALTHY
        - > 80%: DEGRADED
        - Otherwise: HEALTHY
        
        :return: Health status based on CPU usage
        :rtype: HealthStatus
        """
        try:
            if not self.last_system_metrics:
                return HealthStatus.UNKNOWN
            
            cpu_percent = self.last_system_metrics.cpu_percent
            
            if cpu_percent > 90:
                return HealthStatus.UNHEALTHY
            elif cpu_percent > 80:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
                
        except Exception as e:
            logger.error(f"Error checking CPU usage: {e}")
            return HealthStatus.UNHEALTHY
    
    async def _check_memory_usage(self) -> HealthStatus:
        """Check memory usage health.
        
        Evaluates memory usage and returns health status based on thresholds:
        - > 90%: UNHEALTHY
        - > 80%: DEGRADED
        - Otherwise: HEALTHY
        
        :return: Health status based on memory usage
        :rtype: HealthStatus
        """
        try:
            if not self.last_system_metrics:
                return HealthStatus.UNKNOWN
            
            memory_percent = self.last_system_metrics.memory_percent
            
            if memory_percent > 90:
                return HealthStatus.UNHEALTHY
            elif memory_percent > 80:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
                
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
            return HealthStatus.UNHEALTHY
    
    async def _check_disk_usage(self) -> HealthStatus:
        """Check disk usage health.
        
        Evaluates disk usage and returns health status based on thresholds:
        - > 95%: UNHEALTHY
        - > 85%: DEGRADED
        - Otherwise: HEALTHY
        
        :return: Health status based on disk usage
        :rtype: HealthStatus
        """
        try:
            if not self.last_system_metrics:
                return HealthStatus.UNKNOWN
            
            disk_percent = self.last_system_metrics.disk_percent
            
            if disk_percent > 95:
                return HealthStatus.UNHEALTHY
            elif disk_percent > 85:
                return HealthStatus.DEGRADED
            else:
                return HealthStatus.HEALTHY
                
        except Exception as e:
            logger.error(f"Error checking disk usage: {e}")
            return HealthStatus.UNHEALTHY
    
    async def get_metrics(self) -> str:
        """Get Prometheus metrics in text format.
        
        :return: Prometheus metrics in text/plain format
        :rtype: str
        """
        try:
            return generate_latest().decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return ""
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status.
        
        Calculates overall health status based on individual health checks
        and returns detailed status information.
        
        :return: Dictionary with overall status and detailed health information
        :rtype: Dict[str, Any]
        """
        try:
            # Handle non-iterable health_status
            if not isinstance(self.health_status, dict):
                return {
                    "overall_status": "unknown",
                    "error": "Health status dictionary is not valid"
                }
            
            # Calculate overall status using list comprehension logic
            overall_status = HealthStatus.HEALTHY
            
            statuses = list(self.health_status.values())
            if any(status == HealthStatus.UNHEALTHY for status in statuses):
                overall_status = HealthStatus.UNHEALTHY
            elif any(status == HealthStatus.DEGRADED for status in statuses):
                overall_status = HealthStatus.DEGRADED
            
            # Build health checks dictionary using dict comprehension
            health_checks_dict = {}
            if isinstance(self.health_checks, dict):
                health_checks_dict = {
                    name: {
                        "status": self.health_status.get(name, HealthStatus.UNKNOWN).value,
                        "last_check": (
                            health_check.last_check.isoformat()
                            if health_check.last_check
                            else None
                        ),
                        "last_error": health_check.last_error
                    }
                    for name, health_check in self.health_checks.items()
                    if name in self.health_status
                }
            
            # Handle non-iterable active_alerts
            active_alerts_count = len(self.active_alerts) if isinstance(self.active_alerts, dict) else 0
            
            return {
                "overall_status": overall_status.value,
                "health_checks": health_checks_dict,
                "active_alerts": active_alerts_count,
                "system_metrics": {
                    "cpu_percent": (
                        self.last_system_metrics.cpu_percent
                        if self.last_system_metrics
                        else None
                    ),
                    "memory_percent": (
                        self.last_system_metrics.memory_percent
                        if self.last_system_metrics
                        else None
                    ),
                    "disk_percent": (
                        self.last_system_metrics.disk_percent
                        if self.last_system_metrics
                        else None
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {"overall_status": "unknown", "error": str(e)}
    
    async def get_alerts(self) -> Dict[str, Any]:
        """Get alerts information.
        
        Returns active alerts, alert rules, and recent alert history.
        
        :return: Dictionary with alerts information
        :rtype: Dict[str, Any]
        """
        try:
            # Handle non-iterable active_alerts
            active_alerts_list = []
            if isinstance(self.active_alerts, dict):
                active_alerts_list = [
                    alert for alert in self.active_alerts.values()
                    if isinstance(alert, dict)
                ]
            
            # Handle non-iterable alert_rules
            alert_rules_list = []
            if isinstance(self.alert_rules, dict):
                alert_rules_list = [
                    {
                        "name": rule.name,
                        "description": rule.description,
                        "enabled": rule.enabled,
                        "level": rule.level.value
                    }
                    for rule in self.alert_rules.values()
                    if isinstance(rule, AlertRule)
                ]
            
            # Handle non-iterable alert_history
            alert_history_list = []
            if isinstance(self.alert_history, (deque, list)):
                history_list = list(self.alert_history)
                alert_history_list = [
                    alert for alert in history_list[-100:]
                    if isinstance(alert, dict)
                ]
            
            return {
                "active_alerts": active_alerts_list,
                "alert_rules": alert_rules_list,
                "alert_history": alert_history_list
            }
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring service.
        
        Returns the health status of the monitoring service itself,
        including status of Prometheus server and registered components.
        
        :return: Dictionary with monitoring service health information
        :rtype: Dict[str, Any]
        """
        try:
            # Handle non-iterable monitoring_tasks
            tasks_count = len(self.monitoring_tasks) if isinstance(self.monitoring_tasks, list) else 0
            
            return {
                "status": "healthy",
                "prometheus_server": self.prometheus_server is not None,
                "monitoring_tasks": tasks_count,
                "metrics_registered": len(self.metrics) if isinstance(self.metrics, dict) else 0,
                "health_checks_registered": len(self.health_checks) if isinstance(self.health_checks, dict) else 0,
                "alert_rules_registered": len(self.alert_rules) if isinstance(self.alert_rules, dict) else 0,
                "running": self.running
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown monitoring service.
        
        Stops all monitoring tasks and cleans up resources.
        """
        try:
            self.running = False
            
            # Handle non-iterable monitoring_tasks
            if not isinstance(self.monitoring_tasks, list):
                logger.warning("monitoring_tasks is not a list")
                return
            
            # Cancel monitoring tasks using list comprehension for efficiency
            tasks_to_cancel = [
                task for task in self.monitoring_tasks
                if isinstance(task, asyncio.Task) and not task.done()
            ]
            
            # Cancel all tasks
            for task in tasks_to_cancel:
                task.cancel()
            
            # Wait for tasks to complete
            if tasks_to_cancel:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            
            # Clear task list
            self.monitoring_tasks.clear()
            
            logger.info("Monitoring service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down monitoring service: {e}")

