"""
Logging System

Comprehensive logging for the cybersecurity toolkit.
"""

import logging
import json
import sys
import os
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
import traceback
import threading
from pathlib import Path
import asyncio

# ============================================================================
# LOG LEVELS AND FORMATS
# ============================================================================

class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat(str, Enum):
    """Log formats."""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"

# ============================================================================
# LOG CONTEXT AND METADATA
# ============================================================================

@dataclass
class LogContext:
    """Context for log entries."""
    operation: str
    module: str
    function: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    target: Optional[str] = None
    duration: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "operation": self.operation,
            "module": self.module,
            "function": self.function,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "target": self.target,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class LogMetadata:
    """Metadata for log entries."""
    severity: str = "info"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "severity": self.severity,
            "category": self.category,
            "tags": self.tags,
            "source_ip": self.source_ip,
            "user_agent": self.user_agent,
            "correlation_id": self.correlation_id,
            "custom_fields": self.custom_fields
        }

# ============================================================================
# LOG CONFIGURATION
# ============================================================================

@dataclass
class LogConfig:
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.STRUCTURED
    output_file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_syslog: bool = False
    syslog_address: Optional[str] = None
    include_timestamp: bool = True
    include_context: bool = True
    include_metadata: bool = True
    thread_safe: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

# ============================================================================
# CUSTOM LOG HANDLERS
# ============================================================================

class StructuredFormatter(logging.Formatter):
    """Structured log formatter."""
    
    def __init__(self, include_context: bool = True, include_metadata: bool = True):
        super().__init__()
        self.include_context = include_context
        self.include_metadata = include_metadata
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add context if available
        if hasattr(record, 'context') and self.include_context:
            log_entry["context"] = record.context.to_dict()
        
        # Add metadata if available
        if hasattr(record, 'metadata') and self.include_metadata:
            log_entry["metadata"] = record.metadata.to_dict()
        
        # Add exception info
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry, default=str)

class SecurityFileHandler(logging.handlers.RotatingFileHandler):
    """Security-focused file handler with rotation."""
    
    def __init__(self, filename: str, max_bytes: int = 10 * 1024 * 1024, 
                 backup_count: int = 5):
        # Ensure log directory exists
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count)
        self.setFormatter(StructuredFormatter())
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record with security checks."""
        # Add security metadata
        if not hasattr(record, 'metadata'):
            record.metadata = LogMetadata()
        
        # Add source information
        record.metadata.source_ip = getattr(record, 'source_ip', None)
        record.metadata.user_agent = getattr(record, 'user_agent', None)
        
        super().emit(record)

class SecuritySyslogHandler(logging.handlers.SysLogHandler):
    """Security-focused syslog handler."""
    
    def __init__(self, address: Optional[str] = None):
        if address:
            super().__init__(address)
        else:
            super().__init__()
        
        self.setFormatter(StructuredFormatter())
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record to syslog."""
        # Add security context
        if not hasattr(record, 'context'):
            record.context = LogContext(
                operation="syslog",
                module=record.module,
                function=record.funcName
            )
        
        super().emit(record)

# ============================================================================
# SECURITY LOGGER
# ============================================================================

class SecurityLogger:
    """Security-focused logger with structured logging."""
    
    def __init__(self, name: str, config: Optional[LogConfig] = None):
        self.name = name
        self.config = config or LogConfig()
        self.logger = logging.getLogger(name)
        self._setup_logger()
        self._lock = threading.Lock() if self.config.thread_safe else None
    
    def _setup_logger(self) -> None:
        """Setup logger with handlers and formatters."""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        self.logger.setLevel(getattr(logging, self.config.level.value))
        
        # Create formatter
        if self.config.format == LogFormat.JSON:
            formatter = StructuredFormatter()
        elif self.config.format == LogFormat.STRUCTURED:
            formatter = StructuredFormatter(
                include_context=self.config.include_context,
                include_metadata=self.config.include_metadata
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if self.config.enable_file and self.config.output_file:
            file_handler = SecurityFileHandler(
                self.config.output_file,
                self.config.max_file_size,
                self.config.backup_count
            )
            self.logger.addHandler(file_handler)
        
        # Syslog handler
        if self.config.enable_syslog:
            syslog_handler = SecuritySyslogHandler(self.config.syslog_address)
            self.logger.addHandler(syslog_handler)
    
    def _log_with_context(self, level: int, message: str, context: Optional[LogContext] = None,
                         metadata: Optional[LogMetadata] = None, **kwargs) -> None:
        """Log message with context and metadata."""
        if self._lock:
            with self._lock:
                self._do_log(level, message, context, metadata, **kwargs)
        else:
            self._do_log(level, message, context, metadata, **kwargs)
    
    def _do_log(self, level: int, message: str, context: Optional[LogContext] = None,
                metadata: Optional[LogMetadata] = None, **kwargs) -> None:
        """Actually perform the logging."""
        # Create log record
        record = self.logger.makeRecord(
            self.name, level, "", 0, message, (), None
        )
        
        # Add context
        if context:
            record.context = context
        
        # Add metadata
        if metadata:
            record.metadata = metadata
        
        # Add additional fields
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        # Log the record
        self.logger.handle(record)
    
    def debug(self, message: str, context: Optional[LogContext] = None,
              metadata: Optional[LogMetadata] = None, **kwargs) -> None:
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, context, metadata, **kwargs)
    
    def info(self, message: str, context: Optional[LogContext] = None,
             metadata: Optional[LogMetadata] = None, **kwargs) -> None:
        """Log info message."""
        self._log_with_context(logging.INFO, message, context, metadata, **kwargs)
    
    def warning(self, message: str, context: Optional[LogContext] = None,
                metadata: Optional[LogMetadata] = None, **kwargs) -> None:
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, context, metadata, **kwargs)
    
    def error(self, message: str, context: Optional[LogContext] = None,
              metadata: Optional[LogMetadata] = None, **kwargs) -> None:
        """Log error message."""
        self._log_with_context(logging.ERROR, message, context, metadata, **kwargs)
    
    def critical(self, message: str, context: Optional[LogContext] = None,
                 metadata: Optional[LogMetadata] = None, **kwargs) -> None:
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, context, metadata, **kwargs)
    
    def security_event(self, event_type: str, message: str, severity: str = "info",
                       context: Optional[LogContext] = None, **kwargs) -> None:
        """Log security event."""
        metadata = LogMetadata(
            severity=severity,
            category="security",
            tags=["security_event", event_type],
            **kwargs
        )
        
        self.info(f"[SECURITY] {event_type}: {message}", context, metadata)
    
    def audit_event(self, action: str, resource: str, user_id: Optional[str] = None,
                    context: Optional[LogContext] = None, **kwargs) -> None:
        """Log audit event."""
        metadata = LogMetadata(
            severity="info",
            category="audit",
            tags=["audit", action],
            custom_fields={
                "action": action,
                "resource": resource,
                "user_id": user_id
            }
        )
        
        self.info(f"[AUDIT] {action} on {resource}", context, metadata)
    
    def performance_metric(self, operation: str, duration: float, 
                          context: Optional[LogContext] = None, **kwargs) -> None:
        """Log performance metric."""
        metadata = LogMetadata(
            severity="info",
            category="performance",
            tags=["performance", operation],
            custom_fields={
                "operation": operation,
                "duration": duration,
                "duration_ms": duration * 1000
            }
        )
        
        self.debug(f"[PERFORMANCE] {operation} took {duration:.3f}s", context, metadata)

# ============================================================================
# STRUCTURED LOGGER
# ============================================================================

class StructuredLogger(SecurityLogger):
    """Enhanced structured logger with additional features."""
    
    def __init__(self, name: str, config: Optional[LogConfig] = None):
        super().__init__(name, config)
        self.correlation_id = None
        self.session_data = {}
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracing."""
        self.correlation_id = correlation_id
    
    def set_session_data(self, key: str, value: Any) -> None:
        """Set session data."""
        self.session_data[key] = value
    
    def get_session_data(self, key: str) -> Any:
        """Get session data."""
        return self.session_data.get(key)
    
    def clear_session_data(self) -> None:
        """Clear session data."""
        self.session_data.clear()
    
    def _create_context(self, operation: str, module: str, function: str, **kwargs) -> LogContext:
        """Create log context with session data."""
        context = LogContext(
            operation=operation,
            module=module,
            function=function,
            correlation_id=self.correlation_id,
            **kwargs
        )
        
        # Add session data to context metadata
        if self.session_data:
            context.metadata.update(self.session_data)
        
        return context
    
    def log_operation_start(self, operation: str, module: str, function: str, **kwargs) -> LogContext:
        """Log operation start and return context."""
        context = self._create_context(operation, module, function, **kwargs)
        self.info(f"Operation started: {operation}", context)
        return context
    
    def log_operation_end(self, context: LogContext, success: bool = True, 
                         duration: Optional[float] = None, **kwargs) -> None:
        """Log operation end."""
        context.duration = duration
        status = "completed" if success else "failed"
        self.info(f"Operation {status}: {context.operation}", context, **kwargs)
    
    def log_exception(self, exception: Exception, context: Optional[LogContext] = None,
                      metadata: Optional[LogMetadata] = None) -> None:
        """Log exception with full details."""
        if not metadata:
            metadata = LogMetadata(
                severity="error",
                category="exception",
                tags=["exception", exception.__class__.__name__]
            )
        
        self.error(
            f"Exception occurred: {exception}",
            context,
            metadata,
            exc_info=True
        )

# ============================================================================
# LOG FILTERS
# ============================================================================

class LogFilter(logging.Filter):
    """Custom log filter."""
    
    def __init__(self, name: str = "", include_levels: Optional[List[str]] = None,
                 exclude_levels: Optional[List[str]] = None,
                 include_modules: Optional[List[str]] = None,
                 exclude_modules: Optional[List[str]] = None):
        super().__init__(name)
        self.include_levels = include_levels or []
        self.exclude_levels = exclude_levels or []
        self.include_modules = include_modules or []
        self.exclude_modules = exclude_modules or []
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record."""
        # Check level filters
        if self.include_levels and record.levelname not in self.include_levels:
            return False
        
        if self.exclude_levels and record.levelname in self.exclude_levels:
            return False
        
        # Check module filters
        if self.include_modules and record.module not in self.include_modules:
            return False
        
        if self.exclude_modules and record.module in self.exclude_modules:
            return False
        
        return True

class SecurityLogFilter(LogFilter):
    """Security-focused log filter."""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.include_levels = ["WARNING", "ERROR", "CRITICAL"]
        self.include_modules = [
            "scanners", "attackers", "enumerators", "crypto", "network"
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter security-related log records."""
        # Always include security events
        if hasattr(record, 'metadata') and record.metadata.category == "security":
            return True
        
        return super().filter(record)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_logging(name: str = "security_toolkit", config: Optional[LogConfig] = None) -> SecurityLogger:
    """Setup logging for the security toolkit."""
    return SecurityLogger(name, config)

def get_logger(name: str = "security_toolkit") -> SecurityLogger:
    """Get logger instance."""
    return SecurityLogger(name)

def log_operation(operation: str, module: str, function: str, **kwargs):
    """Decorator for logging operations."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger()
            context = logger.log_operation_start(operation, module, function)
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_operation_end(context, success=True, duration=duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.log_operation_end(context, success=False, duration=duration)
                logger.log_exception(e, context)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger()
            context = logger.log_operation_start(operation, module, function)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.log_operation_end(context, success=True, duration=duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.log_operation_end(context, success=False, duration=duration)
                logger.log_exception(e, context)
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def log_security_event(event_type: str, message: str, severity: str = "info", **kwargs):
    """Log security event."""
    logger = get_logger()
    logger.security_event(event_type, message, severity, **kwargs)

def log_performance_metrics(operation: str, duration: float, **kwargs):
    """Log performance metrics."""
    logger = get_logger()
    logger.performance_metric(operation, duration, **kwargs)

# ============================================================================
# CONTEXT MANAGERS
# ============================================================================

@contextmanager
def log_context(operation: str, module: str, function: str, **kwargs):
    """Context manager for logging operations."""
    logger = get_logger()
    context = logger.log_operation_start(operation, module, function, **kwargs)
    start_time = time.time()
    
    try:
        yield context
        duration = time.time() - start_time
        logger.log_operation_end(context, success=True, duration=duration)
    except Exception as e:
        duration = time.time() - start_time
        logger.log_operation_end(context, success=False, duration=duration)
        logger.log_exception(e, context)
        raise

# ============================================================================
# IMPORTS FOR DECORATORS
# ============================================================================

import functools
import time
from contextlib import contextmanager 