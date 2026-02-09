"""
Advanced Logger for Instagram Captions API v10.0
Structured logging with multiple handlers and custom formatters.
"""
import logging
import logging.handlers
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import sys
import threading
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

class StructuredFormatter(logging.Formatter):
    """Structured formatter for JSON logging."""
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_timestamp
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if self.include_timestamp:
            log_entry['timestamp'] = datetime.fromtimestamp(record.created).isoformat()
        
        if self.include_level:
            log_entry['level'] = record.levelname
        
        # Add context information
        if request_id_var.get():
            log_entry['request_id'] = request_id_var.get()
        
        if user_id_var.get():
            log_entry['user_id'] = user_id_var.get()
        
        if session_id_var.get():
            log_entry['session_id'] = session_id_var.get()
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName', 'process',
                          'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                if isinstance(value, (str, int, float, bool, type(None))):
                    log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)

class TextFormatter(logging.Formatter):
    """Human-readable text formatter."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as human-readable text."""
        # Basic format
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = f"[{record.levelname:8}]"
        logger_name = f"[{record.name}]"
        message = record.getMessage()
        
        # Build the log line
        log_parts = [timestamp, level, logger_name, message]
        
        # Add context information
        if self.include_context:
            context_parts = []
            
            if request_id_var.get():
                context_parts.append(f"req:{request_id_var.get()}")
            
            if user_id_var.get():
                context_parts.append(f"user:{user_id_var.get()}")
            
            if session_id_var.get():
                context_parts.append(f"session:{session_id_var.get()}")
            
            if context_parts:
                log_parts.append(f"[{' '.join(context_parts)}]")
        
        # Add exception information
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            log_parts.append(f"\n{exc_text}")
        
        return " ".join(log_parts)

class AdvancedLogger:
    """Advanced logger with structured logging capabilities."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = TextFormatter(include_context=True)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def add_console_handler(self, level: int = logging.INFO, formatter: Optional[logging.Formatter] = None):
        """Add console handler."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        if formatter is None:
            formatter = TextFormatter(include_context=True)
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def add_file_handler(self, file_path: str, level: int = logging.INFO, 
                        formatter: Optional[logging.Formatter] = None, 
                        max_bytes: int = 10 * 1024 * 1024,  # 10MB
                        backup_count: int = 5):
        """Add rotating file handler."""
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setLevel(level)
        
        if formatter is None:
            formatter = StructuredFormatter()
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def add_json_file_handler(self, file_path: str, level: int = logging.INFO,
                             max_bytes: int = 10 * 1024 * 1024,
                             backup_count: int = 5):
        """Add JSON file handler for structured logging."""
        self.add_file_handler(
            file_path, level, StructuredFormatter(), max_bytes, backup_count
        )
    
    def set_request_context(self, request_id: str, user_id: Optional[str] = None, 
                           session_id: Optional[str] = None):
        """Set request context for logging."""
        request_id_var.set(request_id)
        if user_id:
            user_id_var.set(user_id)
        if session_id:
            session_id_var.set(session_id)
    
    def clear_request_context(self):
        """Clear request context."""
        request_id_var.set(None)
        user_id_var.set(None)
        session_id_var.set(None)
    
    def log_request(self, method: str, url: str, status_code: int, 
                   response_time_ms: float, user_id: Optional[str] = None,
                   request_size: Optional[int] = None, response_size: Optional[int] = None):
        """Log HTTP request information."""
        extra = {
            'event_type': 'http_request',
            'method': method,
            'url': url,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'user_id': user_id,
            'request_size': request_size,
            'response_size': response_size
        }
        
        if status_code >= 400:
            self.logger.warning("HTTP Request", extra=extra)
        else:
            self.logger.info("HTTP Request", extra=extra)
    
    def log_security_event(self, event_type: str, user_id: Optional[str], 
                          ip_address: Optional[str], details: Dict[str, Any],
                          severity: str = "info"):
        """Log security-related events."""
        extra = {
            'event_type': 'security',
            'security_event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details,
            'severity': severity
        }
        
        if severity == "critical":
            self.logger.critical("Security Event", extra=extra)
        elif severity == "error":
            self.logger.error("Security Event", extra=extra)
        elif severity == "warning":
            self.logger.warning("Security Event", extra=extra)
        else:
            self.logger.info("Security Event", extra=extra)
    
    def log_performance_metric(self, metric_name: str, value: Union[int, float], 
                              unit: str, tags: Optional[Dict[str, str]] = None):
        """Log performance metrics."""
        extra = {
            'event_type': 'performance_metric',
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'tags': tags or {}
        }
        
        self.logger.info("Performance Metric", extra=extra)
    
    def log_business_event(self, event_type: str, user_id: Optional[str],
                          business_data: Dict[str, Any], category: str = "general"):
        """Log business-related events."""
        extra = {
            'event_type': 'business',
            'business_event_type': event_type,
            'user_id': user_id,
            'business_data': business_data,
            'category': category
        }
        
        self.logger.info("Business Event", extra=extra)
    
    def log_error_with_context(self, message: str, error: Exception,
                             context: Optional[Dict[str, Any]] = None):
        """Log error with additional context."""
        extra = {
            'event_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.logger.error(message, extra=extra, exc_info=True)
    
    def log_database_query(self, query: str, execution_time_ms: float,
                          rows_affected: Optional[int] = None,
                          database: Optional[str] = None):
        """Log database query information."""
        extra = {
            'event_type': 'database_query',
            'query': query,
            'execution_time_ms': execution_time_ms,
            'rows_affected': rows_affected,
            'database': database
        }
        
        if execution_time_ms > 1000:  # Log slow queries as warnings
            self.logger.warning("Slow Database Query", extra=extra)
        else:
            self.logger.debug("Database Query", extra=extra)
    
    def log_api_call(self, service_name: str, endpoint: str, method: str,
                     status_code: int, response_time_ms: float,
                     error_message: Optional[str] = None):
        """Log external API calls."""
        extra = {
            'event_type': 'api_call',
            'service_name': service_name,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'error_message': error_message
        }
        
        if error_message or status_code >= 400:
            self.logger.warning("API Call", extra=extra)
        else:
            self.logger.info("API Call", extra=extra)
    
    def log_user_action(self, action: str, user_id: str, 
                       resource_type: Optional[str] = None,
                       resource_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None):
        """Log user actions for audit purposes."""
        extra = {
            'event_type': 'user_action',
            'action': action,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'metadata': metadata or {}
        }
        
        self.logger.info("User Action", extra=extra)
    
    def log_system_event(self, event_type: str, component: str,
                        details: Dict[str, Any], severity: str = "info"):
        """Log system-level events."""
        extra = {
            'event_type': 'system_event',
            'system_event_type': event_type,
            'component': component,
            'details': details,
            'severity': severity
        }
        
        if severity == "critical":
            self.logger.critical("System Event", extra=extra)
        elif severity == "error":
            self.logger.error("System Event", extra=extra)
        elif severity == "warning":
            self.logger.warning("System Event", extra=extra)
        else:
            self.logger.info("System Event", extra=extra)
    
    # Standard logging methods with context support
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.logger.critical(message, extra=extra)
    
    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log exception with traceback."""
        self.logger.exception(message, extra=extra)
    
    def set_level(self, level: int):
        """Set logger level."""
        self.logger.setLevel(level)
    
    def get_handlers(self) -> List[logging.Handler]:
        """Get all handlers."""
        return self.logger.handlers
    
    def remove_handler(self, handler: logging.Handler):
        """Remove a specific handler."""
        if handler in self.logger.handlers:
            self.logger.removeHandler(handler)
    
    def clear_handlers(self):
        """Remove all handlers."""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)






