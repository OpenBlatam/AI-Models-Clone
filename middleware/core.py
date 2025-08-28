from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import asyncio
import functools
import inspect
import json
import logging
import time
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from enum import Enum
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from typing import Any, List, Dict, Optional
"""
Core middleware for centralized logging, metrics, and exception handling.
Uses functional programming patterns and RORO (Receive Object, Return Object) pattern.
"""




class LogLevel(Enum):
    """Log levels for structured logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics for monitoring."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"


@dataclass
class LogContext:
    """Context for structured logging."""
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricContext:
    """Context for metrics collection."""
    operation: str
    component: str
    labels: Dict[str, str] = field(default_factory=dict)
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class ExceptionContext:
    """Context for exception handling."""
    exception_type: str
    exception_message: str
    stack_trace: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    severity: str = "error"


# =============================================================================
# LOGGING MIDDLEWARE
# =============================================================================

def setup_structured_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    include_timestamp: bool = True
) -> structlog.BoundLogger:
    """
    Setup structured logging with configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, console)
        include_timestamp: Whether to include timestamps
    
    Returns:
        Configured structured logger
    """
    processors = []
    
    if include_timestamp:
        processors.append(structlog.stdlib.filter_by_level)
        processors.append(structlog.stdlib.add_logger_name)
        processors.append(structlog.stdlib.add_log_level)
        processors.append(structlog.stdlib.PositionalArgumentsFormatter())
        processors.append(structlog.processors.TimeStamper(fmt="iso"))
    
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def create_log_context(
    request_id: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    operation: Optional[str] = None,
    component: Optional[str] = None,
    **metadata
) -> LogContext:
    """
    Create logging context with metadata.
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        session_id: Session identifier
        operation: Operation being performed
        component: Component name
        **metadata: Additional metadata
    
    Returns:
        LogContext object
    """
    return LogContext(
        request_id=request_id,
        user_id=user_id,
        session_id=session_id,
        operation=operation,
        component=component,
        metadata=metadata
    )


def log_operation(
    logger: structlog.BoundLogger,
    context: LogContext,
    message: str,
    level: LogLevel = LogLevel.INFO,
    **kwargs
) -> None:
    """
    Log operation with structured context.
    
    Args:
        logger: Structured logger instance
        context: Logging context
        message: Log message
        level: Log level
        **kwargs: Additional log fields
    """
    log_data = {
        "request_id": context.request_id,
        "user_id": context.user_id,
        "session_id": context.session_id,
        "operation": context.operation,
        "component": context.component,
        **context.metadata,
        **kwargs
    }
    
    log_method = getattr(logger, level.value)
    log_method(message, **log_data)


# =============================================================================
# METRICS MIDDLEWARE
# =============================================================================

class MetricsRegistry:
    """Registry for Prometheus metrics."""
    
    def __init__(self) -> Any:
        self.counters: Dict[str, Counter] = {}
        self.histograms: Dict[str, Histogram] = {}
        self.gauges: Dict[str, Gauge] = {}
    
    def register_counter(
        self,
        name: str,
        description: str,
        labels: List[str]
    ) -> Counter:
        """Register a counter metric."""
        if name not in self.counters:
            self.counters[name] = Counter(name, description, labels)
        return self.counters[name]
    
    def register_histogram(
        self,
        name: str,
        description: str,
        labels: List[str],
        buckets: Optional[List[float]] = None
    ) -> Histogram:
        """Register a histogram metric."""
        if name not in self.histograms:
            self.histograms[name] = Histogram(
                name, description, labels, buckets=buckets
            )
        return self.histograms[name]
    
    def register_gauge(
        self,
        name: str,
        description: str,
        labels: List[str]
    ) -> Gauge:
        """Register a gauge metric."""
        if name not in self.gauges:
            self.gauges[name] = Gauge(name, description, labels)
        return self.gauges[name]


# Global metrics registry
metrics_registry = MetricsRegistry()


def create_metric_context(
    operation: str,
    component: str,
    **labels
) -> MetricContext:
    """
    Create metrics context.
    
    Args:
        operation: Operation name
        component: Component name
        **labels: Metric labels
    
    Returns:
        MetricContext object
    """
    return MetricContext(
        operation=operation,
        component=component,
        labels=labels,
        start_time=time.time()
    )


def record_metric(
    context: MetricContext,
    metric_type: MetricType,
    value: float = 1.0,
    **additional_labels
) -> None:
    """
    Record a metric with context.
    
    Args:
        context: Metrics context
        metric_type: Type of metric
        value: Metric value
        **additional_labels: Additional labels
    """
    all_labels = {**context.labels, **additional_labels}
    
    if metric_type == MetricType.COUNTER:
        metric_name = f"{context.component}_{context.operation}_total"
        counter = metrics_registry.register_counter(
            metric_name,
            f"Total count of {context.operation} operations",
            list(all_labels.keys())
        )
        counter.labels(**all_labels).inc(value)
    
    elif metric_type == MetricType.HISTOGRAM:
        metric_name = f"{context.component}_{context.operation}_duration_seconds"
        histogram = metrics_registry.register_histogram(
            metric_name,
            f"Duration of {context.operation} operations",
            list(all_labels.keys())
        )
        histogram.labels(**all_labels).observe(value)
    
    elif metric_type == MetricType.GAUGE:
        metric_name = f"{context.component}_{context.operation}_current"
        gauge = metrics_registry.register_gauge(
            metric_name,
            f"Current value of {context.operation}",
            list(all_labels.keys())
        )
        gauge.labels(**all_labels).set(value)


# =============================================================================
# EXCEPTION HANDLING MIDDLEWARE
# =============================================================================

class SecurityException(Exception):
    """Base exception for security-related errors."""
    pass


class ValidationException(Exception):
    """Base exception for validation errors."""
    pass


class NetworkException(Exception):
    """Base exception for network-related errors."""
    pass


class ConfigurationException(Exception):
    """Base exception for configuration errors."""
    pass


EXCEPTION_MAPPING = {
    SecurityException: {
        "status_code": 403,
        "user_message": "Access denied",
        "severity": "warning"
    },
    ValidationException: {
        "status_code": 400,
        "user_message": "Invalid input",
        "severity": "info"
    },
    NetworkException: {
        "status_code": 503,
        "user_message": "Service temporarily unavailable",
        "severity": "error"
    },
    ConfigurationException: {
        "status_code": 500,
        "user_message": "Internal server error",
        "severity": "critical"
    }
}


def create_exception_context(
    exception: Exception,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    operation: Optional[str] = None,
    component: Optional[str] = None
) -> ExceptionContext:
    """
    Create exception context for logging.
    
    Args:
        exception: The exception that occurred
        request_id: Request identifier
        user_id: User identifier
        operation: Operation being performed
        component: Component name
    
    Returns:
        ExceptionContext object
    """
    exception_info = EXCEPTION_MAPPING.get(
        type(exception),
        {
            "status_code": 500,
            "user_message": "An unexpected error occurred",
            "severity": "error"
        }
    )
    
    return ExceptionContext(
        exception_type=type(exception).__name__,
        exception_message=str(exception),
        stack_trace=traceback.format_exc(),
        request_id=request_id,
        user_id=user_id,
        operation=operation,
        component=component,
        severity=exception_info["severity"]
    )


def handle_exception(
    logger: structlog.BoundLogger,
    context: ExceptionContext,
    include_stack_trace: bool = False
) -> Dict[str, Any]:
    """
    Handle exception with structured logging.
    
    Args:
        logger: Structured logger
        context: Exception context
        include_stack_trace: Whether to include stack trace in response
    
    Returns:
        Error response dictionary
    """
    log_data = {
        "exception_type": context.exception_type,
        "exception_message": context.exception_message,
        "request_id": context.request_id,
        "user_id": context.user_id,
        "operation": context.operation,
        "component": context.component,
        "severity": context.severity
    }
    
    if include_stack_trace:
        log_data["stack_trace"] = context.stack_trace
    
    log_method = getattr(logger, context.severity)
    log_method("Exception occurred", **log_data)
    
    exception_info = EXCEPTION_MAPPING.get(
        context.exception_type,
        {"status_code": 500, "user_message": "An unexpected error occurred"}
    )
    
    return {
        "error": exception_info["user_message"],
        "status_code": exception_info["status_code"],
        "request_id": context.request_id
    }


# =============================================================================
# DECORATORS
# =============================================================================

def with_logging(
    operation: str,
    component: str,
    log_level: LogLevel = LogLevel.INFO
):
    """
    Decorator for automatic logging of function calls.
    
    Args:
        operation: Operation name
        component: Component name
        log_level: Log level for the operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            logger = structlog.get_logger()
            request_id = kwargs.get("request_id", "unknown")
            
            context = create_log_context(
                request_id=request_id,
                operation=operation,
                component=component
            )
            
            log_operation(
                logger, context,
                f"Starting {operation}",
                level=log_level
            )
            
            try:
                result = await func(*args, **kwargs)
                log_operation(
                    logger, context,
                    f"Completed {operation}",
                    level=log_level
                )
                return result
            except Exception as e:
                exception_context = create_exception_context(
                    e, request_id, operation=operation, component=component
                )
                handle_exception(logger, exception_context)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            logger = structlog.get_logger()
            request_id = kwargs.get("request_id", "unknown")
            
            context = create_log_context(
                request_id=request_id,
                operation=operation,
                component=component
            )
            
            log_operation(
                logger, context,
                f"Starting {operation}",
                level=log_level
            )
            
            try:
                result = func(*args, **kwargs)
                log_operation(
                    logger, context,
                    f"Completed {operation}",
                    level=log_level
                )
                return result
            except Exception as e:
                exception_context = create_exception_context(
                    e, request_id, operation=operation, component=component
                )
                handle_exception(logger, exception_context)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def with_metrics(
    operation: str,
    component: str,
    metric_type: MetricType = MetricType.HISTOGRAM
):
    """
    Decorator for automatic metrics collection.
    
    Args:
        operation: Operation name
        component: Component name
        metric_type: Type of metric to record
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            context = create_metric_context(operation, component)
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - context.start_time
                record_metric(context, metric_type, duration)
                return result
            except Exception as e:
                duration = time.time() - context.start_time
                record_metric(context, MetricType.COUNTER, 1, error="true")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            context = create_metric_context(operation, component)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - context.start_time
                record_metric(context, metric_type, duration)
                return result
            except Exception as e:
                duration = time.time() - context.start_time
                record_metric(context, MetricType.COUNTER, 1, error="true")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def with_exception_handling(
    logger: Optional[structlog.BoundLogger] = None,
    include_stack_trace: bool = False
):
    """
    Decorator for centralized exception handling.
    
    Args:
        logger: Logger instance (uses default if not provided)
        include_stack_trace: Whether to include stack trace in error response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            log_instance = logger or structlog.get_logger()
            request_id = kwargs.get("request_id", "unknown")
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                exception_context = create_exception_context(
                    e, request_id=request_id
                )
                error_response = handle_exception(
                    log_instance, exception_context, include_stack_trace
                )
                return error_response
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            log_instance = logger or structlog.get_logger()
            request_id = kwargs.get("request_id", "unknown")
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                exception_context = create_exception_context(
                    e, request_id=request_id
                )
                error_response = handle_exception(
                    log_instance, exception_context, include_stack_trace
                )
                return error_response
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# =============================================================================
# FASTAPI MIDDLEWARE
# =============================================================================

async def logging_middleware(request: Request, call_next):
    """FastAPI middleware for request/response logging."""
    logger = structlog.get_logger()
    start_time = time.time()
    
    # Extract request information
    request_id = request.headers.get("X-Request-ID", "unknown")
    user_id = request.headers.get("X-User-ID")
    
    context = create_log_context(
        request_id=request_id,
        user_id=user_id,
        operation=f"{request.method} {request.url.path}",
        component="api"
    )
    
    # Log request
    log_operation(
        logger, context,
        "Incoming request",
        level=LogLevel.INFO,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    # Process request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log response
        log_operation(
            logger, context,
            "Request completed",
            level=LogLevel.INFO,
            status_code=response.status_code,
            duration=duration
        )
        
        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(duration)
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        exception_context = create_exception_context(
            e, request_id, user_id, f"{request.method} {request.url.path}", "api"
        )
        error_response = handle_exception(logger, exception_context)
        
        return JSONResponse(
            status_code=error_response["status_code"],
            content=error_response,
            headers={"X-Request-ID": request_id}
        )


async def metrics_middleware(request: Request, call_next):
    """FastAPI middleware for metrics collection."""
    start_time = time.time()
    
    # Record request metrics
    context = create_metric_context(
        operation="http_request",
        component="api",
        method=request.method,
        path=request.url.path
    )
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record success metrics
        record_metric(context, MetricType.HISTOGRAM, duration, status_code=str(response.status_code))
        record_metric(context, MetricType.COUNTER, 1, status_code=str(response.status_code))
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Record error metrics
        record_metric(context, MetricType.HISTOGRAM, duration, error="true")
        record_metric(context, MetricType.COUNTER, 1, error="true")
        raise


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_metrics() -> str:
    """Get Prometheus metrics as string."""
    return generate_latest()


def setup_middleware_stack(app) -> None:
    """Setup complete middleware stack for FastAPI app."""
    app.middleware("http")(metrics_middleware)
    app.middleware("http")(logging_middleware)


@asynccontextmanager
async def operation_context(
    operation: str,
    component: str,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Context manager for operation logging and metrics.
    
    Args:
        operation: Operation name
        component: Component name
        request_id: Request identifier
        user_id: User identifier
    """
    logger = structlog.get_logger()
    
    log_context = create_log_context(
        request_id=request_id or "unknown",
        user_id=user_id,
        operation=operation,
        component=component
    )
    
    metric_context = create_metric_context(operation, component)
    
    log_operation(logger, log_context, f"Starting {operation}")
    
    try:
        yield log_context
        log_operation(logger, log_context, f"Completed {operation}")
        record_metric(metric_context, MetricType.HISTOGRAM, time.time() - metric_context.start_time)
    except Exception as e:
        exception_context = create_exception_context(
            e, request_id, user_id, operation, component
        )
        handle_exception(logger, exception_context)
        record_metric(metric_context, MetricType.COUNTER, 1, error="true")
        raise 