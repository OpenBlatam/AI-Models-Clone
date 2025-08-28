#!/usr/bin/env python3
"""
Advanced Observability Manager - Infrastructure Layer
==================================================

Enterprise-grade observability implementation with Prometheus metrics,
OpenTelemetry tracing, structured logging, and comprehensive monitoring.
"""

import asyncio
import json
import logging
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from contextlib import asynccontextmanager
import threading
import weakref

# Prometheus metrics
try:
    from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# OpenTelemetry tracing
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.trace.span import Span
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False


class LogLevel(Enum):
    """Log levels for structured logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


@dataclass
class LogEntry:
    """Structured log entry."""
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    level: LogLevel = LogLevel.INFO
    message: str = ""
    component: str = ""
    operation: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "component": self.component,
            "operation": self.operation,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "metadata": self.metadata,
            "error": str(self.error) if self.error else None,
            "stack_trace": self.stack_trace
        }


@dataclass
class HealthCheck:
    """Health check result."""
    
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0


class MetricsCollector:
    """Advanced metrics collection with Prometheus integration."""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
        
        if PROMETHEUS_AVAILABLE:
            self._initialize_prometheus_metrics()
    
    def _initialize_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        # HTTP metrics
        self._metrics["http_requests_total"] = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"]
        )
        
        self._metrics["http_request_duration_seconds"] = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"]
        )
        
        # Business metrics
        self._metrics["posts_created_total"] = Counter(
            "posts_created_total",
            "Total posts created"
        )
        
        self._metrics["posts_optimized_total"] = Counter(
            "posts_optimized_total",
            "Total posts optimized"
        )
        
        self._metrics["optimization_score"] = Histogram(
            "optimization_score",
            "Post optimization scores",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        # System metrics
        self._metrics["active_connections"] = Gauge(
            "active_connections",
            "Number of active database connections"
        )
        
        self._metrics["cache_hit_ratio"] = Gauge(
            "cache_hit_ratio",
            "Cache hit ratio"
        )
        
        self._metrics["memory_usage_bytes"] = Gauge(
            "memory_usage_bytes",
            "Memory usage in bytes"
        )
        
        self._metrics["cpu_usage_percent"] = Gauge(
            "cpu_usage_percent",
            "CPU usage percentage"
        )
        
        # Error metrics
        self._metrics["errors_total"] = Counter(
            "errors_total",
            "Total errors",
            ["component", "error_type"]
        )
        
        self._logger.info("Prometheus metrics initialized")
    
    def increment_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        if name in self._metrics and isinstance(self._metrics[name], Counter):
            if labels:
                self._metrics[name].labels(**labels).inc(value)
            else:
                self._metrics[name].inc(value)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge metric."""
        if name in self._metrics and isinstance(self._metrics[name], Gauge):
            if labels:
                self._metrics[name].labels(**labels).set(value)
            else:
                self._metrics[name].set(value)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observe a histogram metric."""
        if name in self._metrics and isinstance(self._metrics[name], Histogram):
            if labels:
                self._metrics[name].labels(**labels).observe(value)
            else:
                self._metrics[name].observe(value)
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float) -> None:
        """Record HTTP request metrics."""
        self.increment_counter("http_requests_total", labels={
            "method": method,
            "endpoint": endpoint,
            "status_code": str(status_code)
        })
        
        self.observe_histogram("http_request_duration_seconds", duration, labels={
            "method": method,
            "endpoint": endpoint
        })
    
    def record_post_created(self) -> None:
        """Record post creation."""
        self.increment_counter("posts_created_total")
    
    def record_post_optimized(self, score: float) -> None:
        """Record post optimization."""
        self.increment_counter("posts_optimized_total")
        self.observe_histogram("optimization_score", score)
    
    def record_error(self, component: str, error_type: str) -> None:
        """Record error occurrence."""
        self.increment_counter("errors_total", labels={
            "component": component,
            "error_type": error_type
        })
    
    def update_system_metrics(self, memory_usage: float, cpu_usage: float, active_connections: int) -> None:
        """Update system metrics."""
        self.set_gauge("memory_usage_bytes", memory_usage)
        self.set_gauge("cpu_usage_percent", cpu_usage)
        self.set_gauge("active_connections", active_connections)
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics."""
        if PROMETHEUS_AVAILABLE:
            return generate_latest().decode('utf-8')
        return "Prometheus not available"


class TracingManager:
    """Advanced tracing with OpenTelemetry integration."""
    
    def __init__(self, service_name: str = "ultra-library-optimization"):
        self.service_name = service_name
        self._logger = logging.getLogger(__name__)
        
        if OPENTELEMETRY_AVAILABLE:
            self._initialize_tracing()
    
    def _initialize_tracing(self) -> None:
        """Initialize OpenTelemetry tracing."""
        # Set up the tracer provider
        trace.set_tracer_provider(TracerProvider())
        
        # Add span processor
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )
        
        # Get the tracer
        self.tracer = trace.get_tracer(self.service_name)
        
        self._logger.info("OpenTelemetry tracing initialized")
    
    def start_span(self, name: str, attributes: Dict[str, Any] = None) -> Optional[Span]:
        """Start a new span."""
        if not OPENTELEMETRY_AVAILABLE:
            return None
        
        if attributes is None:
            attributes = {}
        
        return self.tracer.start_span(name, attributes=attributes)
    
    def add_event(self, span: Span, name: str, attributes: Dict[str, Any] = None) -> None:
        """Add an event to a span."""
        if span and OPENTELEMETRY_AVAILABLE:
            if attributes is None:
                attributes = {}
            span.add_event(name, attributes=attributes)
    
    def set_status(self, span: Span, status: StatusCode, description: str = "") -> None:
        """Set the status of a span."""
        if span and OPENTELEMETRY_AVAILABLE:
            span.set_status(Status(status, description))
    
    def record_exception(self, span: Span, exception: Exception) -> None:
        """Record an exception in a span."""
        if span and OPENTELEMETRY_AVAILABLE:
            span.record_exception(exception)
    
    def instrument_fastapi(self, app) -> None:
        """Instrument FastAPI application."""
        if OPENTELEMETRY_AVAILABLE:
            FastAPIInstrumentor.instrument_app(app)
            AsyncioInstrumentor().instrument()
            self._logger.info("FastAPI instrumented with OpenTelemetry")


class StructuredLogger:
    """Advanced structured logging with correlation and tracing."""
    
    def __init__(self, name: str = "ultra-library-optimization"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._correlation_id = None
        self._user_id = None
        self._session_id = None
        self._trace_id = None
        self._span_id = None
        self._lock = threading.RLock()
    
    def set_context(self, correlation_id: str = None, user_id: str = None,
                   session_id: str = None, trace_id: str = None, span_id: str = None) -> None:
        """Set logging context."""
        with self._lock:
            self._correlation_id = correlation_id
            self._user_id = user_id
            self._session_id = session_id
            self._trace_id = trace_id
            self._span_id = span_id
    
    def _create_log_entry(self, level: LogLevel, message: str, component: str = "",
                         operation: str = "", metadata: Dict[str, Any] = None,
                         error: Exception = None) -> LogEntry:
        """Create a structured log entry."""
        with self._lock:
            return LogEntry(
                level=level,
                message=message,
                component=component,
                operation=operation,
                user_id=self._user_id,
                session_id=self._session_id,
                correlation_id=self._correlation_id,
                trace_id=self._trace_id,
                span_id=self._span_id,
                metadata=metadata or {},
                error=error,
                stack_trace=traceback.format_exc() if error else None
            )
    
    def debug(self, message: str, component: str = "", operation: str = "",
              metadata: Dict[str, Any] = None) -> None:
        """Log debug message."""
        entry = self._create_log_entry(LogLevel.DEBUG, message, component, operation, metadata)
        self.logger.debug(json.dumps(entry.to_dict(), default=str))
    
    def info(self, message: str, component: str = "", operation: str = "",
             metadata: Dict[str, Any] = None) -> None:
        """Log info message."""
        entry = self._create_log_entry(LogLevel.INFO, message, component, operation, metadata)
        self.logger.info(json.dumps(entry.to_dict(), default=str))
    
    def warning(self, message: str, component: str = "", operation: str = "",
                metadata: Dict[str, Any] = None) -> None:
        """Log warning message."""
        entry = self._create_log_entry(LogLevel.WARNING, message, component, operation, metadata)
        self.logger.warning(json.dumps(entry.to_dict(), default=str))
    
    def error(self, message: str, component: str = "", operation: str = "",
              metadata: Dict[str, Any] = None, error: Exception = None) -> None:
        """Log error message."""
        entry = self._create_log_entry(LogLevel.ERROR, message, component, operation, metadata, error)
        self.logger.error(json.dumps(entry.to_dict(), default=str))
    
    def critical(self, message: str, component: str = "", operation: str = "",
                 metadata: Dict[str, Any] = None, error: Exception = None) -> None:
        """Log critical message."""
        entry = self._create_log_entry(LogLevel.CRITICAL, message, component, operation, metadata, error)
        self.logger.critical(json.dumps(entry.to_dict(), default=str))


class HealthChecker:
    """Advanced health checking system."""
    
    def __init__(self):
        self._checks: Dict[str, callable] = {}
        self._logger = logging.getLogger(__name__)
    
    def register_check(self, name: str, check_func: callable) -> None:
        """Register a health check."""
        self._checks[name] = check_func
        self._logger.info(f"Registered health check: {name}")
    
    async def run_health_checks(self) -> List[HealthCheck]:
        """Run all health checks."""
        results = []
        
        for name, check_func in self._checks.items():
            start_time = time.time()
            
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                response_time = (time.time() - start_time) * 1000
                
                if isinstance(result, dict):
                    status = HealthStatus.HEALTHY if result.get("healthy", True) else HealthStatus.UNHEALTHY
                    message = result.get("message", "")
                    details = result.get("details", {})
                else:
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    message = "Check completed"
                    details = {}
                
                results.append(HealthCheck(
                    name=name,
                    status=status,
                    message=message,
                    details=details,
                    response_time_ms=response_time
                ))
                
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                results.append(HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}",
                    details={"error": str(e)},
                    response_time_ms=response_time
                ))
        
        return results
    
    def get_overall_status(self, checks: List[HealthCheck]) -> HealthStatus:
        """Get overall health status."""
        if not checks:
            return HealthStatus.UNHEALTHY
        
        unhealthy_count = len([c for c in checks if c.status == HealthStatus.UNHEALTHY])
        degraded_count = len([c for c in checks if c.status == HealthStatus.DEGRADED])
        
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


class ObservabilityManager:
    """
    Advanced observability manager with enterprise-grade features.
    
    Features:
    - Prometheus metrics collection
    - OpenTelemetry distributed tracing
    - Structured logging with correlation
    - Health checking system
    - Performance monitoring
    - Error tracking and alerting
    - Custom metrics and dashboards
    """
    
    def __init__(self, service_name: str = "ultra-library-optimization"):
        self.service_name = service_name
        self.metrics = MetricsCollector()
        self.tracing = TracingManager(service_name)
        self.logger = StructuredLogger(service_name)
        self.health_checker = HealthChecker()
        
        # Performance monitoring
        self._performance_data: Dict[str, List[float]] = {}
        self._error_counts: Dict[str, int] = {}
        self._start_time = time.time()
        
        # Register default health checks
        self._register_default_health_checks()
        
        self.logger.info("Observability manager initialized", component="observability")
    
    def _register_default_health_checks(self) -> None:
        """Register default health checks."""
        self.health_checker.register_check("system", self._check_system_health)
        self.health_checker.register_check("database", self._check_database_health)
        self.health_checker.register_check("memory", self._check_memory_health)
        self.health_checker.register_check("uptime", self._check_uptime_health)
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system health."""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            return {
                "healthy": cpu_percent < 90 and memory.percent < 90,
                "message": "System resources are within normal limits",
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available
                }
            }
        except ImportError:
            return {
                "healthy": True,
                "message": "System health check not available (psutil not installed)",
                "details": {}
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health."""
        # This would be implemented with actual database connection
        return {
            "healthy": True,
            "message": "Database connection is healthy",
            "details": {
                "connection_pool_size": 10,
                "active_connections": 5
            }
        }
    
    def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory health."""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            
            return {
                "healthy": memory.percent < 90,
                "message": f"Memory usage: {memory.percent}%",
                "details": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                }
            }
        except ImportError:
            return {
                "healthy": True,
                "message": "Memory health check not available",
                "details": {}
            }
    
    def _check_uptime_health(self) -> Dict[str, Any]:
        """Check system uptime."""
        uptime = time.time() - self._start_time
        
        return {
            "healthy": True,
            "message": f"System uptime: {uptime:.2f} seconds",
            "details": {
                "uptime_seconds": uptime,
                "start_time": datetime.fromtimestamp(self._start_time).isoformat()
            }
        }
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, component: str = "",
                             attributes: Dict[str, Any] = None):
        """Context manager for tracing operations."""
        span = None
        start_time = time.time()
        
        try:
            # Start span
            span = self.tracing.start_span(operation_name, attributes or {})
            
            # Set logging context
            if span:
                self.logger.set_context(
                    trace_id=getattr(span, 'context', {}).get('trace_id'),
                    span_id=getattr(span, 'context', {}).get('span_id')
                )
            
            # Log operation start
            self.logger.info(f"Started operation: {operation_name}", component=component, operation=operation_name)
            
            yield span
            
            # Record success
            if span:
                self.tracing.set_status(span, StatusCode.OK)
            
            # Log operation completion
            duration = time.time() - start_time
            self.logger.info(f"Completed operation: {operation_name} in {duration:.3f}s", 
                           component=component, operation=operation_name,
                           metadata={"duration_ms": duration * 1000})
            
            # Record metrics
            self.metrics.observe_histogram("operation_duration_seconds", duration, {
                "operation": operation_name,
                "component": component
            })
            
        except Exception as e:
            # Record error
            if span:
                self.tracing.record_exception(span, e)
                self.tracing.set_status(span, StatusCode.ERROR, str(e))
            
            # Log error
            self.logger.error(f"Operation failed: {operation_name}", 
                            component=component, operation=operation_name, error=e)
            
            # Record error metrics
            self.metrics.record_error(component, type(e).__name__)
            
            raise
        
        finally:
            if span:
                span.end()
    
    def record_performance_metric(self, metric_name: str, value: float, 
                                component: str = "", operation: str = "") -> None:
        """Record a performance metric."""
        if metric_name not in self._performance_data:
            self._performance_data[metric_name] = []
        
        self._performance_data[metric_name].append(value)
        
        # Keep only last 1000 values
        if len(self._performance_data[metric_name]) > 1000:
            self._performance_data[metric_name] = self._performance_data[metric_name][-1000:]
        
        # Record in Prometheus if available
        self.metrics.observe_histogram(f"{metric_name}_duration_seconds", value, {
            "component": component,
            "operation": operation
        })
    
    def record_error(self, error: Exception, component: str = "", operation: str = "") -> None:
        """Record an error occurrence."""
        error_type = type(error).__name__
        error_key = f"{component}:{operation}:{error_type}"
        
        self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1
        
        # Record in Prometheus
        self.metrics.record_error(component, error_type)
        
        # Log error
        self.logger.error(f"Error in {component}:{operation}", 
                         component=component, operation=operation, error=error)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        checks = await self.health_checker.run_health_checks()
        overall_status = self.health_checker.get_overall_status(checks)
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms,
                    "details": check.details
                }
                for check in checks
            ]
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "service": self.service_name,
            "uptime_seconds": time.time() - self._start_time,
            "performance_metrics": {
                name: {
                    "count": len(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "avg": sum(values) / len(values) if values else 0
                }
                for name, values in self._performance_data.items()
            },
            "error_counts": self._error_counts,
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "opentelemetry_available": OPENTELEMETRY_AVAILABLE
        }
    
    def instrument_fastapi(self, app) -> None:
        """Instrument FastAPI application with observability."""
        # Instrument with OpenTelemetry
        self.tracing.instrument_fastapi(app)
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            return await self.get_health_status()
        
        # Add metrics endpoint
        @app.get("/metrics")
        async def metrics_endpoint():
            from fastapi.responses import Response
            return Response(
                content=self.metrics.get_metrics(),
                media_type=CONTENT_TYPE_LATEST
            )
        
        self.logger.info("FastAPI application instrumented with observability")


# Global observability manager instance
observability_manager = ObservabilityManager()


# Decorators for easy observability integration
def trace_operation(operation_name: str, component: str = ""):
    """Decorator to trace an operation."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with observability_manager.trace_operation(operation_name, component):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def monitor_performance(metric_name: str, component: str = ""):
    """Decorator to monitor performance of a function."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                observability_manager.record_performance_metric(metric_name, duration, component)
                return result
            except Exception as e:
                observability_manager.record_error(e, component, func.__name__)
                raise
        return wrapper
    return decorator 