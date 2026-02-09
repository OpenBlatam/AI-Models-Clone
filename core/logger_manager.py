"""
Enhanced Centralized Logging Management System
============================================

Advanced logging system with:
- Multiple log handlers and formatters
- Structured JSON logging
- Colored console output
- Log rotation and compression
- Performance monitoring
- Specialized logging functions
- Integration with monitoring systems
"""

import logging
import logging.handlers
import json
import sys
import time
import os
import gzip
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
import threading
from functools import wraps
import traceback
import hashlib

# Import configuration
try:
    from .config_manager import get_config
except ImportError:
    # Fallback for testing
    def get_config():
        class MockConfig:
            class System:
                log_file = "logs/heygen_ai.log"
                max_log_size = 100 * 1024 * 1024  # 100MB
                backup_logs = 5
                debug = False
            class Monitoring:
                log_level = "INFO"
                enable_metrics = True
            system = System()
            monitoring = Monitoring()
        return MockConfig()


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for machine-readable logs"""
    
    def __init__(self):
        super().__init__()
    
    def format(self, record):
        """Format log record as structured JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add custom fields based on log level
        if record.levelno >= logging.WARNING:
            log_data["severity"] = "high"
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for human-readable logs"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.platform != 'win32'
    
    def format(self, record):
        """Format log record with colors"""
        # Get color for level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format message
        if self.use_colors:
            formatted = f"{color}{record.levelname:8}{reset} | {timestamp} | {record.name} | {record.getMessage()}"
        else:
            formatted = f"{record.levelname:8} | {timestamp} | {record.name} | {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class CompressedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Rotating file handler with compression support"""
    
    def __init__(self, filename: str, max_bytes: int = 0, backup_count: int = 0, 
                 encoding: str = 'utf-8', compress: bool = True):
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding)
        self.compress = compress
        self.backup_count = backup_count
    
    def doRollover(self):
        """Perform rollover with compression"""
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Rotate existing backup files
        for i in range(self.backup_count - 1, 0, -1):
            sfn = f"{self.baseFilename}.{i}"
            dfn = f"{self.baseFilename}.{i + 1}"
            if os.path.exists(sfn):
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)
        
        # Rename current file to .1
        dfn = f"{self.baseFilename}.1"
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        
        # Compress if enabled
        if self.compress:
            self._compress_file(dfn)
        
        # Create new file
        self.mode = 'w'
        self.stream = self._open()
    
    def _compress_file(self, filename: str):
        """Compress a log file using gzip"""
        try:
            with open(filename, 'rb') as f_in:
                with gzip.open(f"{filename}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Remove uncompressed file
            os.remove(filename)
        except Exception as e:
            # Log error but don't fail rollover
            print(f"Failed to compress {filename}: {e}")


class LoggerManager:
    """Enhanced centralized logger manager"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.logs_dir = Path(self.config.system.log_file).parent
        self.handlers: Dict[str, logging.Handler] = {}
        self.loggers: Dict[str, logging.Logger] = {}
        self.performance_logger = None
        self.api_logger = None
        self.security_logger = None
        self.database_logger = None
        self.cache_logger = None
        self.error_logger = None
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup root logger
        self._setup_root_logger()
        
        # Setup specialized loggers
        self._setup_specialized_loggers()
        
        logger.info("Logger manager initialized successfully")
    
    def _setup_root_logger(self):
        """Setup root logger with handlers"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.monitoring.log_level.upper()))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler with colored formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter())
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
        self.handlers['console'] = console_handler
        
        # File handler with structured formatter
        file_handler = CompressedRotatingFileHandler(
            filename=self.config.system.log_file,
            maxBytes=self.config.system.max_log_size,
            backupCount=self.config.system.backup_logs,
            compress=True
        )
        file_handler.setFormatter(StructuredFormatter())
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        self.handlers['file'] = file_handler
        
        # Error file handler
        error_log_file = self.logs_dir / "errors.log"
        error_handler = CompressedRotatingFileHandler(
            filename=str(error_log_file),
            maxBytes=self.config.system.max_log_size,
            backupCount=self.config.system.backup_logs,
            compress=True
        )
        error_handler.setFormatter(StructuredFormatter())
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)
        self.handlers['error'] = error_handler
    
    def _setup_specialized_loggers(self):
        """Setup specialized loggers for different purposes"""
        # Performance logger
        self.performance_logger = self._create_specialized_logger(
            "performance", 
            self.logs_dir / "performance.log",
            StructuredFormatter()
        )
        
        # API logger
        self.api_logger = self._create_specialized_logger(
            "api", 
            self.logs_dir / "api.log",
            StructuredFormatter()
        )
        
        # Security logger
        self.security_logger = self._create_specialized_logger(
            "security", 
            self.logs_dir / "security.log",
            StructuredFormatter()
        )
        
        # Database logger
        self.database_logger = self._create_specialized_logger(
            "database", 
            self.logs_dir / "database.log",
            StructuredFormatter()
        )
        
        # Cache logger
        self.cache_logger = self._create_specialized_logger(
            "cache", 
            self.logs_dir / "cache.log",
            StructuredFormatter()
        )
        
        # Error logger
        self.error_logger = self._create_specialized_logger(
            "error", 
            self.logs_dir / "detailed_errors.log",
            StructuredFormatter()
        )
    
    def _create_specialized_logger(self, name: str, log_file: Path, formatter: logging.Formatter) -> logging.Logger:
        """Create a specialized logger with its own handler"""
        logger_instance = logging.getLogger(name)
        logger_instance.setLevel(logging.DEBUG)
        logger_instance.propagate = False  # Don't propagate to root logger
        
        # Create handler for this logger
        handler = CompressedRotatingFileHandler(
            filename=str(log_file),
            maxBytes=self.config.system.max_log_size,
            backupCount=self.config.system.backup_logs,
            compress=True
        )
        handler.setFormatter(formatter)
        logger_instance.addHandler(handler)
        
        # Store in loggers dict
        self.loggers[name] = logger_instance
        
        return logger_instance
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the specified name"""
        if name not in self.loggers:
            logger_instance = logging.getLogger(name)
            self.loggers[name] = logger_instance
        
        return self.loggers[name]
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """Log performance metrics"""
        if self.performance_logger:
            extra_fields = {
                "operation": operation,
                "duration_ms": duration * 1000,
                "duration_seconds": duration,
                **kwargs
            }
            self.performance_logger.info(f"Performance: {operation} took {duration:.3f}s", 
                                       extra={'extra_fields': extra_fields})
    
    def log_api_request(self, method: str, path: str, status_code: int, 
                       duration: float, user_id: Optional[str] = None):
        """Log API request details"""
        if self.api_logger:
            extra_fields = {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration * 1000,
                "user_id": user_id
            }
            self.api_logger.info(f"API Request: {method} {path} -> {status_code} ({duration:.3f}s)", 
                                extra={'extra_fields': extra_fields})
    
    def log_security_event(self, event_type: str, description: str, 
                          user_id: Optional[str] = None, ip_address: Optional[str] = None):
        """Log security events"""
        if self.security_logger:
            extra_fields = {
                "event_type": event_type,
                "description": description,
                "user_id": user_id,
                "ip_address": ip_address
            }
            self.security_logger.warning(f"Security Event: {event_type} - {description}", 
                                       extra={'extra_fields': extra_fields})
    
    def log_database_operation(self, operation: str, table: str, duration: float, 
                              rows_affected: Optional[int] = None):
        """Log database operations"""
        if self.database_logger:
            extra_fields = {
                "operation": operation,
                "table": table,
                "duration_ms": duration * 1000,
                "rows_affected": rows_affected
            }
            self.database_logger.info(f"Database: {operation} on {table} took {duration:.3f}s", 
                                    extra={'extra_fields': extra_fields})
    
    def log_cache_operation(self, operation: str, key: str, hit: bool, duration: float):
        """Log cache operations"""
        if self.cache_logger:
            extra_fields = {
                "operation": operation,
                "key": key,
                "hit": hit,
                "duration_ms": duration * 1000
            }
            status = "HIT" if hit else "MISS"
            self.cache_logger.info(f"Cache {operation}: {key} -> {status} ({duration:.3f}s)", 
                                 extra={'extra_fields': extra_fields})
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any], 
                              logger_name: str = "error"):
        """Log error with additional context"""
        if self.error_logger:
            extra_fields = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "traceback": traceback.format_exc()
            }
            self.error_logger.error(f"Error: {type(error).__name__}: {error}", 
                                  extra={'extra_fields': extra_fields})
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            "total_loggers": len(self.loggers),
            "total_handlers": len(self.handlers),
            "log_level": self.config.monitoring.log_level,
            "log_file": str(self.config.system.log_file),
            "max_log_size": self.config.system.max_log_size,
            "backup_logs": self.config.system.backup_logs,
            "environment": self.config.system.environment.value,
            "debug_mode": self.config.system.debug,
            "logs_directory": str(self.logs_dir),
            "handlers": list(self.handlers.keys()),
            "specialized_loggers": list(self.loggers.keys())
        }
        
        # Add file sizes if available
        try:
            if os.path.exists(self.config.system.log_file):
                stats["main_log_size"] = os.path.getsize(self.config.system.log_file)
            
            # Check specialized log files
            for name, logger_instance in self.loggers.items():
                log_file = self.logs_dir / f"{name}.log"
                if log_file.exists():
                    stats[f"{name}_log_size"] = log_file.stat().st_size
        except Exception:
            pass
        
        return stats
    
    def cleanup_old_logs(self, max_age_days: int = 30):
        """Clean up old log files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            cleaned_count = 0
            
            for log_file in self.logs_dir.glob("*.log*"):
                if log_file.is_file():
                    file_age = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_age < cutoff_date:
                        log_file.unlink()
                        cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old log files")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
    
    def rotate_logs(self):
        """Manually trigger log rotation"""
        try:
            for handler in self.handlers.values():
                if hasattr(handler, 'doRollover'):
                    handler.doRollover()
            
            logger.info("Manual log rotation completed")
            
        except Exception as e:
            logger.error(f"Failed to rotate logs: {e}")


# Global logger manager instance
_logger_manager: Optional[LoggerManager] = None


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    return _logger_manager.get_logger(name)


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics using global logger manager"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    _logger_manager.log_performance(operation, duration, **kwargs)


def log_api_request(method: str, path: str, status_code: int, 
                   duration: float, user_id: Optional[str] = None):
    """Log API request details using global logger manager"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    _logger_manager.log_api_request(method, path, status_code, duration, user_id)


def log_security_event(event_type: str, description: str, 
                      user_id: Optional[str] = None, ip_address: Optional[str] = None):
    """Log security events using global logger manager"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    _logger_manager.log_security_event(event_type, description, user_id, ip_address)


def log_database_operation(operation: str, table: str, duration: float, 
                          rows_affected: Optional[int] = None):
    """Log database operations using global logger manager"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    _logger_manager.log_database_operation(operation, table, duration, rows_affected)


def log_cache_operation(operation: str, key: str, hit: bool, duration: float):
    """Log cache operations using global logger manager"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    _logger_manager.log_cache_operation(operation, key, hit, duration)


def log_error_with_context(error: Exception, context: Dict[str, Any], 
                          logger_name: str = "error"):
    """Log error with context using global logger manager"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    
    _logger_manager.log_error_with_context(error, context, logger_name)


def performance_logger(func):
    """Decorator to automatically log function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            log_performance(f"{func.__module__}.{func.__name__}", duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            log_performance(f"{func.__module__}.{func.__name__}", duration, error=str(e))
            raise
    
    return wrapper


if __name__ == "__main__":
    # Example usage
    logger_manager = LoggerManager()
    
    # Test different logging functions
    logger_manager.log_performance("test_operation", 0.125, table="users", rows=100)
    logger_manager.log_api_request("GET", "/api/users", 200, 0.045, user_id="123")
    logger_manager.log_security_event("login_failed", "Invalid credentials", ip_address="192.168.1.1")
    logger_manager.log_database_operation("SELECT", "users", 0.125, rows_affected=100)
    logger_manager.log_cache_operation("GET", "user:123", True, 0.001)
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger_manager.log_error_with_context(e, {"user_id": "123", "operation": "test"})
    
    # Get statistics
    stats = logger_manager.get_log_stats()
    print("Log statistics:", json.dumps(stats, indent=2))
