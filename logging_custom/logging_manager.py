"""
Logging Manager for Instagram Captions API v10.0
Centralized logging configuration and management.
"""
import logging
import logging.handlers
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import threading
from collections import defaultdict, deque
from .advanced_logger import AdvancedLogger, StructuredFormatter, TextFormatter

class LogEntry:
    """Represents a log entry with metadata."""
    
    def __init__(self, timestamp: datetime, level: str, logger: str, message: str,
                 extra: Optional[Dict[str, Any]] = None):
        self.timestamp = timestamp
        self.level = level
        self.logger = logger
        self.message = message
        self.extra = extra or {}
        self.request_id = self.extra.get('request_id')
        self.user_id = self.extra.get('user_id')
        self.session_id = self.extra.get('session_id')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'logger': self.logger,
            'message': self.message,
            'extra': self.extra,
            'request_id': self.request_id,
            'user_id': self.user_id,
            'session_id': self.session_id
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)

class LoggingManager:
    """Centralized logging management system."""
    
    def __init__(self, base_path: str = ".", max_log_entries: int = 10000):
        self.base_path = Path(base_path)
        self.max_log_entries = max_log_entries
        self.logs_dir = self.base_path / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # In-memory log storage
        self.log_entries: deque = deque(maxlen=max_log_entries)
        self.log_lock = threading.Lock()
        
        # Logger instances
        self.loggers: Dict[str, AdvancedLogger] = {}
        self.default_logger: Optional[AdvancedLogger] = None
        
        # Statistics
        self.stats = {
            'total_logs': 0,
            'logs_by_level': defaultdict(int),
            'logs_by_logger': defaultdict(int),
            'logs_by_hour': defaultdict(int),
            'last_log_time': None
        }
        
        self._setup_default_logging()
    
    def _setup_default_logging(self):
        """Setup default logging configuration."""
        # Create default logger
        self.default_logger = self.create_logger("default")
        
        # Add file handlers
        self.default_logger.add_file_handler(
            str(self.logs_dir / "app.log"),
            level=logging.INFO
        )
        
        self.default_logger.add_json_file_handler(
            str(self.logs_dir / "app.json"),
            level=logging.INFO
        )
        
        # Add error log file
        self.default_logger.add_file_handler(
            str(self.logs_dir / "errors.log"),
            level=logging.ERROR,
            formatter=TextFormatter(include_context=True)
        )
        
        # Add security log file
        self.default_logger.add_file_handler(
            str(self.logs_dir / "security.log"),
            level=logging.INFO,
            formatter=StructuredFormatter()
        )
        
        # Add performance log file
        self.default_logger.add_file_handler(
            str(self.logs_dir / "performance.log"),
            level=logging.INFO,
            formatter=StructuredFormatter()
        )
        
        # Add business log file
        self.default_logger.add_file_handler(
            str(self.logs_dir / "business.log"),
            level=logging.INFO,
            formatter=StructuredFormatter()
        )
        
        self.default_logger.info("Logging system initialized")
    
    def create_logger(self, name: str, level: int = logging.INFO) -> AdvancedLogger:
        """Create a new logger instance."""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = AdvancedLogger(name, level)
        self.loggers[name] = logger
        
        # Add custom handler to capture all logs
        custom_handler = CustomLogHandler(self)
        logger.logger.addHandler(custom_handler)
        
        return logger
    
    def get_logger(self, name: str) -> AdvancedLogger:
        """Get an existing logger or create a new one."""
        if name not in self.loggers:
            return self.create_logger(name)
        return self.loggers[name]
    
    def add_log_entry(self, record: logging.LogRecord):
        """Add a log entry to the in-memory storage."""
        with self.log_lock:
            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created),
                level=record.levelname,
                logger=record.name,
                message=record.getMessage(),
                extra=getattr(record, 'extra', {})
            )
            
            # Add to storage
            self.log_entries.append(log_entry)
            
            # Update statistics
            self.stats['total_logs'] += 1
            self.stats['logs_by_level'][record.levelname] += 1
            self.stats['logs_by_logger'][record.name] += 1
            
            hour_key = log_entry.timestamp.strftime('%Y-%m-%d %H:00')
            self.stats['logs_by_hour'][hour_key] += 1
            
            self.stats['last_log_time'] = log_entry.timestamp
    
    def get_recent_logs(self, limit: int = 100, 
                        level: Optional[str] = None,
                        logger: Optional[str] = None,
                        since: Optional[datetime] = None) -> List[LogEntry]:
        """Get recent log entries with optional filtering."""
        with self.log_lock:
            logs = list(self.log_entries)
        
        # Apply filters
        if level:
            logs = [log for log in logs if log.level == level]
        
        if logger:
            logs = [log for log in logs if log.logger == logger]
        
        if since:
            logs = [log for log in logs if log.timestamp >= since]
        
        # Return most recent logs
        return logs[-limit:] if limit > 0 else logs
    
    def search_logs(self, query: str, limit: int = 100) -> List[LogEntry]:
        """Search logs by text query."""
        with self.log_lock:
            logs = list(self.log_entries)
        
        matching_logs = []
        query_lower = query.lower()
        
        for log in reversed(logs):  # Search from most recent
            if (query_lower in log.message.lower() or
                query_lower in log.logger.lower() or
                any(query_lower in str(value).lower() for value in log.extra.values())):
                
                matching_logs.append(log)
                if len(matching_logs) >= limit:
                    break
        
        return matching_logs
    
    def get_logs_by_request(self, request_id: str) -> List[LogEntry]:
        """Get all logs for a specific request."""
        with self.log_lock:
            logs = list(self.log_entries)
        
        return [log for log in logs if log.request_id == request_id]
    
    def get_logs_by_user(self, user_id: str, limit: int = 100) -> List[LogEntry]:
        """Get logs for a specific user."""
        with self.log_lock:
            logs = list(self.log_entries)
        
        user_logs = [log for log in logs if log.user_id == user_id]
        return user_logs[-limit:] if limit > 0 else user_logs
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        with self.log_lock:
            stats = self.stats.copy()
        
        # Add current log count
        stats['current_log_count'] = len(self.log_entries)
        
        # Add loggers info
        stats['active_loggers'] = list(self.loggers.keys())
        
        # Add recent activity
        if stats['last_log_time']:
            time_since_last = datetime.now() - stats['last_log_time']
            stats['seconds_since_last_log'] = time_since_last.total_seconds()
        
        return stats
    
    def export_logs(self, file_path: str, format: str = "json",
                    level: Optional[str] = None,
                    logger: Optional[str] = None,
                    since: Optional[datetime] = None,
                    limit: Optional[int] = None) -> bool:
        """Export logs to file."""
        try:
            logs = self.get_recent_logs(
                limit=limit or self.max_log_entries,
                level=level,
                logger=logger,
                since=since
            )
            
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([log.to_dict() for log in logs], f, 
                             ensure_ascii=False, indent=2, default=str)
            
            elif format.lower() == "csv":
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if logs:
                        writer = csv.DictWriter(f, fieldnames=logs[0].to_dict().keys())
                        writer.writeheader()
                        for log in logs:
                            writer.writerow(log.to_dict())
            
            elif format.lower() == "txt":
                with open(file_path, 'w', encoding='utf-8') as f:
                    for log in logs:
                        f.write(f"{log.timestamp} [{log.level:8}] [{log.logger}] {log.message}\n")
                        if log.extra:
                            f.write(f"  Extra: {json.dumps(log.extra, indent=2)}\n")
                        f.write("\n")
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return True
            
        except Exception as e:
            if self.default_logger:
                self.default_logger.error(f"Failed to export logs: {e}")
            return False
    
    def clear_logs(self, older_than: Optional[timedelta] = None):
        """Clear logs, optionally keeping recent ones."""
        with self.log_lock:
            if older_than is None:
                # Clear all logs
                self.log_entries.clear()
                self.stats['total_logs'] = 0
                self.stats['logs_by_level'].clear()
                self.stats['logs_by_logger'].clear()
                self.stats['logs_by_hour'].clear()
            else:
                # Clear old logs
                cutoff_time = datetime.now() - older_than
                old_logs = [log for log in self.log_entries if log.timestamp < cutoff_time]
                
                for log in old_logs:
                    self.log_entries.remove(log)
                    self.stats['total_logs'] -= 1
                    self.stats['logs_by_level'][log.level] -= 1
                    self.stats['logs_by_logger'][log.logger] -= 1
                    
                    hour_key = log.timestamp.strftime('%Y-%m-%d %H:00')
                    self.stats['logs_by_hour'][hour_key] -= 1
    
    def rotate_log_files(self):
        """Rotate log files."""
        try:
            # Get all log files
            log_files = list(self.logs_dir.glob("*.log"))
            
            for log_file in log_files:
                if log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
                    # Create backup
                    backup_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    backup_path = self.logs_dir / backup_name
                    
                    # Move current file to backup
                    log_file.rename(backup_path)
                    
                    # Create new empty file
                    log_file.touch()
                    
                    if self.default_logger:
                        self.default_logger.info(f"Rotated log file: {log_file.name} -> {backup_name}")
        
        except Exception as e:
            if self.default_logger:
                self.default_logger.error(f"Failed to rotate log files: {e}")
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get a comprehensive log summary."""
        with self.log_lock:
            current_logs = list(self.log_entries)
        
        summary = {
            'total_logs': len(current_logs),
            'loggers': list(self.loggers.keys()),
            'recent_activity': {},
            'error_summary': {},
            'performance_summary': {}
        }
        
        if current_logs:
            # Recent activity (last hour)
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_logs = [log for log in current_logs if log.timestamp >= one_hour_ago]
            
            summary['recent_activity'] = {
                'logs_last_hour': len(recent_logs),
                'errors_last_hour': len([log for log in recent_logs if log.level in ['ERROR', 'CRITICAL']]),
                'warnings_last_hour': len([log for log in recent_logs if log.level == 'WARNING'])
            }
            
            # Error summary
            error_logs = [log for log in current_logs if log.level in ['ERROR', 'CRITICAL']]
            summary['error_summary'] = {
                'total_errors': len(error_logs),
                'errors_by_logger': defaultdict(int),
                'recent_errors': [log.to_dict() for log in error_logs[-10:]]  # Last 10 errors
            }
            
            for log in error_logs:
                summary['error_summary']['errors_by_logger'][log.logger] += 1
            
            # Performance summary
            perf_logs = [log for log in current_logs if log.extra.get('event_type') == 'performance_metric']
            if perf_logs:
                summary['performance_summary'] = {
                    'total_metrics': len(perf_logs),
                    'metrics_by_name': defaultdict(list)
                }
                
                for log in perf_logs:
                    metric_name = log.extra.get('metric_name', 'unknown')
                    value = log.extra.get('value', 0)
                    summary['performance_summary']['metrics_by_name'][metric_name].append(value)
        
        return summary

class CustomLogHandler(logging.Handler):
    """Custom handler to capture all logs for the manager."""
    
    def __init__(self, manager: LoggingManager):
        super().__init__()
        self.manager = manager
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record."""
        try:
            self.manager.add_log_entry(record)
        except Exception:
            # Prevent infinite recursion if logging fails
            pass






