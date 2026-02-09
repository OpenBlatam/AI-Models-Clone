"""
Logging Service for HeyGen AI
=============================

Provides comprehensive logging capabilities with:
- Structured JSON logging
- Log rotation and archival
- Multiple log levels and handlers
- Integration with monitoring systems
- Performance metrics logging
"""

import json
import logging
import logging.handlers
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import traceback
import asyncio
from contextlib import contextmanager
import functools

# Third-party imports
try:
    import structlog
    from structlog import get_logger, configure
    from structlog.stdlib import LoggerFactory
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

try:
    import opentelemetry.trace as trace
    from opentelemetry import trace as otel_trace
    from opentelemetry.trace import Status, StatusCode
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

try:
    import prometheus_client as prometheus
    from prometheus_client import Counter, Histogram, Gauge, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class LogLevel(str):
    """Custom log level class with validation"""
    
    VALID_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def __init__(self, level: str):
        if level.upper() not in self.VALID_LEVELS:
            raise ValueError(f"Invalid log level: {level}. Valid levels: {self.VALID_LEVELS}")
        self.level = level.upper()
    
    def __str__(self) -> str:
        return self.level


class LogFormat(str):
    """Custom log format class with validation"""
    
    VALID_FORMATS = ["json", "text", "structured"]
    
    def __init__(self, format_type: str):
        if format_type.lower() not in self.VALID_FORMATS:
            raise ValueError(f"Invalid log format: {format_type}. Valid formats: {self.VALID_FORMATS}")
        self.format_type = format_type.lower()
    
    def __str__(self) -> str:
        return self.format_type


class PerformanceMetrics:
    """Performance metrics collection for logging"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation"""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.metrics[operation] = duration
            del self.start_times[operation]
            return duration
        return 0.0
    
    def add_metric(self, name: str, value: Any) -> None:
        """Add a custom metric"""
        self.metrics[name] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self.metrics.copy()
    
    def clear_metrics(self) -> None:
        """Clear all metrics"""
        self.metrics.clear()
        self.start_times.clear()


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def __init__(self, format_type: str = "json"):
        super().__init__()
        self.format_type = format_type
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured data"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "getMessage", "exc_info", "exc_text",
                          "stack_info", "msg", "args"]:
                log_data[key] = value
        
        if self.format_type == "json":
            return json.dumps(log_data, default=str, ensure_ascii=False)
        else:
            # Text format
            parts = [
                f"[{log_data['timestamp']}]",
                f"[{log_data['level']}]",
                f"[{log_data['logger']}]",
                log_data['message']
            ]
            
            if "exception" in log_data:
                parts.append(f"\nException: {log_data['exception']['type']}: {log_data['exception']['message']}")
            
            return " ".join(parts)


class AsyncLogHandler(logging.Handler):
    """Asynchronous log handler for high-performance logging"""
    
    def __init__(self, level: int = logging.NOTSET):
        super().__init__(level)
        self.log_queue: asyncio.Queue = asyncio.Queue()
        self.worker_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record to async queue"""
        try:
            # Put record in queue (non-blocking)
            self.log_queue.put_nowait(record)
        except asyncio.QueueFull:
            # Queue is full, log synchronously as fallback
            super().emit(record)
    
    async def start_worker(self) -> None:
        """Start the async log worker"""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
    
    async def stop_worker(self) -> None:
        """Stop the async log worker"""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
    
    async def _worker(self) -> None:
        """Async worker for processing log records"""
        while self.is_running:
            try:
                # Get record from queue with timeout
                record = await asyncio.wait_for(self.log_queue.get(), timeout=1.0)
                
                # Process the record
                await self._process_record(record)
                
                # Mark task as done
                self.log_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error in processing (fallback to stderr)
                print(f"Error in async log worker: {e}", file=sys.stderr)
    
    async def _process_record(self, record: logging.LogRecord) -> None:
        """Process a log record asynchronously"""
        # This is where you would implement async logging logic
        # For now, we'll just print to stderr as an example
        formatted_record = self.format(record)
        print(formatted_record, file=sys.stderr)


class LoggingService:
    """
    Comprehensive logging service for HeyGen AI.
    
    Provides structured logging, performance metrics, and integration
    with monitoring and tracing systems.
    """
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_format: str = "json",
        log_file: Optional[str] = None,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB
        backup_count: int = 5,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_async: bool = False,
        enable_metrics: bool = True,
        enable_tracing: bool = True
    ):
        """
        Initialize the logging service.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Log format (json, text, structured)
            log_file: Path to log file
            max_file_size: Maximum log file size in bytes
            backup_count: Number of backup files to keep
            enable_console: Enable console logging
            enable_file: Enable file logging
            enable_async: Enable async logging
            enable_metrics: Enable performance metrics
            enable_tracing: Enable OpenTelemetry tracing
        """
        self.log_level = LogLevel(log_level)
        self.log_format = LogFormat(log_format)
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_async = enable_async
        self.enable_metrics = enable_metrics
        self.enable_tracing = enable_tracing
        
        # Performance metrics
        self.performance_metrics = PerformanceMetrics()
        
        # Initialize logging
        self._setup_logging()
        
        # Setup monitoring if available
        if self.enable_metrics and PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
        
        # Setup tracing if available
        if self.enable_tracing and OPENTELEMETRY_AVAILABLE:
            self._setup_tracing()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level.level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = StructuredFormatter(str(self.log_format))
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.log_level.level))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.enable_file and self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count
            )
            file_handler.setLevel(getattr(logging, self.log_level.level))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Async handler
        if self.enable_async:
            async_handler = AsyncLogHandler()
            async_handler.setLevel(getattr(logging, self.log_level.level))
            async_handler.setFormatter(formatter)
            root_logger.addHandler(async_handler)
            
            # Start async worker
            asyncio.create_task(async_handler.start_worker())
        
        # Setup structlog if available
        if STRUCTLOG_AVAILABLE:
            configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        
        logger.info("Logging service initialized", extra={
            "log_level": self.log_level.level,
            "log_format": self.log_format.format_type,
            "log_file": self.log_file,
            "enable_console": self.enable_console,
            "enable_file": self.enable_file,
            "enable_async": self.enable_async
        })
    
    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics for logging"""
        try:
            # Log level counters
            self.log_counters = {
                "debug": Counter("heygen_ai_logs_total", "Total log entries", ["level"]),
                "info": Counter("heygen_ai_logs_total", "Total log entries", ["level"]),
                "warning": Counter("heygen_ai_logs_total", "Total log entries", ["level"]),
                "error": Counter("heygen_ai_logs_total", "Total log entries", ["level"]),
                "critical": Counter("heygen_ai_logs_total", "Total log entries", ["level"])
            }
            
            # Log processing duration
            self.log_duration = Histogram(
                "heygen_ai_log_processing_duration_seconds",
                "Log processing duration in seconds",
                ["level"]
            )
            
            logger.info("Prometheus metrics enabled for logging")
            
        except Exception as e:
            logger.warning(f"Failed to setup Prometheus metrics: {e}")
    
    def _setup_tracing(self) -> None:
        """Setup OpenTelemetry tracing for logging"""
        try:
            # Create tracer
            self.tracer = trace.get_tracer(__name__)
            logger.info("OpenTelemetry tracing enabled for logging")
            
        except Exception as e:
            logger.warning(f"Failed to setup OpenTelemetry tracing: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """
        Log performance metrics.
        
        Args:
            operation: Operation name
            duration: Operation duration in seconds
            **kwargs: Additional metrics
        """
        if not self.enable_metrics:
            return
        
        # Update internal metrics
        self.performance_metrics.add_metric(operation, duration)
        
        # Log performance data
        logger.info(f"Performance: {operation}", extra={
            "operation": operation,
            "duration_seconds": duration,
            "metrics": kwargs
        })
        
        # Update Prometheus metrics if available
        if PROMETHEUS_AVAILABLE and hasattr(self, 'log_duration'):
            try:
                self.log_duration.labels(level="info").observe(duration)
            except Exception as e:
                logger.warning(f"Failed to update Prometheus metrics: {e}")
    
    @contextmanager
    def performance_timer(self, operation: str):
        """
        Context manager for timing operations.
        
        Args:
            operation: Operation name to time
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.log_performance(operation, duration)
    
    def log_error(self, error: Exception, context: str = "", **kwargs) -> None:
        """
        Log an error with context.
        
        Args:
            error: Exception to log
            context: Error context
            **kwargs: Additional context information
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
        error_data.update(kwargs)
        
        logger.error(f"Error in {context}: {error}", extra=error_data)
        
        # Update Prometheus metrics if available
        if PROMETHEUS_AVAILABLE and hasattr(self, 'log_counters'):
            try:
                self.log_counters["error"].labels(level="error").inc()
            except Exception as e:
                logger.warning(f"Failed to update Prometheus metrics: {e}")
    
    def log_security_event(self, event_type: str, user_id: Optional[str] = None, **kwargs) -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            user_id: User ID involved
            **kwargs: Additional event information
        """
        security_data = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "ip_address": kwargs.get("ip_address"),
            "user_agent": kwargs.get("user_agent"),
            "session_id": kwargs.get("session_id")
        }
        security_data.update(kwargs)
        
        logger.warning(f"Security event: {event_type}", extra=security_data)
    
    def log_business_event(self, event_type: str, user_id: Optional[str] = None, **kwargs) -> None:
        """
        Log a business event.
        
        Args:
            event_type: Type of business event
            user_id: User ID involved
            **kwargs: Additional event information
        """
        business_data = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": kwargs
        }
        
        logger.info(f"Business event: {event_type}", extra=business_data)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.get_metrics()
    
    def clear_performance_metrics(self) -> None:
        """Clear performance metrics."""
        self.performance_metrics.clear_metrics()
    
    def set_log_level(self, level: str) -> None:
        """
        Change log level dynamically.
        
        Args:
            level: New log level
        """
        try:
            new_level = LogLevel(level)
            self.log_level = new_level
            
            # Update all handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers:
                handler.setLevel(getattr(logging, new_level.level))
            
            logger.info(f"Log level changed to: {new_level.level}")
            
        except ValueError as e:
            logger.error(f"Invalid log level: {e}")
    
    def rotate_logs(self) -> None:
        """Manually trigger log rotation."""
        if self.enable_file and self.log_file:
            for handler in logging.getLogger().handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.doRollover()
                    logger.info("Log files rotated")
                    break
    
    async def shutdown(self) -> None:
        """Shutdown the logging service."""
        logger.info("Shutting down logging service...")
        
        # Stop async handlers
        if self.enable_async:
            for handler in logging.getLogger().handlers:
                if isinstance(handler, AsyncLogHandler):
                    await handler.stop_worker()
        
        # Flush all handlers
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        logger.info("Logging service shutdown complete")


# Decorators for easy logging
def log_function_call(logger_name: str = None):
    """
    Decorator to log function calls with performance timing.
    
    Args:
        logger_name: Name of the logger to use
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            start_time = time.time()
            
            try:
                logger.debug(f"Calling {func.__name__}", extra={
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.debug(f"Completed {func.__name__}", extra={
                    "function": func.__name__,
                    "duration_seconds": duration
                })
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {func.__name__}", extra={
                    "function": func.__name__,
                    "duration_seconds": duration,
                    "error": str(e)
                })
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            start_time = time.time()
            
            try:
                logger.debug(f"Calling {func.__name__}", extra={
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })
                
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.debug(f"Completed {func.__name__}", extra={
                    "function": func.__name__,
                    "duration_seconds": duration
                })
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {func.__name__}", extra={
                    "function": func.__name__,
                    "duration_seconds": duration,
                    "error": str(e)
                })
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_performance(operation: str):
    """
    Decorator to log performance metrics for functions.
    
    Args:
        operation: Operation name for logging
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                logger = logging.getLogger(func.__module__)
                logger.info(f"Performance: {operation}", extra={
                    "operation": operation,
                    "duration_seconds": duration
                })
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                logger = logging.getLogger(func.__module__)
                logger.info(f"Performance: {operation}", extra={
                    "operation": operation,
                    "duration_seconds": duration
                })
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global logging service instance
_logging_service: Optional[LoggingService] = None


def get_logging_service() -> LoggingService:
    """Get or create the global logging service."""
    global _logging_service
    
    if _logging_service is None:
        _logging_service = LoggingService()
    
    return _logging_service


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return get_logging_service().get_logger(name)
