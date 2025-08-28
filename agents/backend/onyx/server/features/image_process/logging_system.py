#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE LOGGING SYSTEM
==============================

Advanced logging system for the optimized image processing system
with training progress tracking, error handling, and performance monitoring.
"""

import logging
import logging.handlers
import os
import sys
import time
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from contextlib import contextmanager

# Performance monitoring
import psutil
import numpy as np
from collections import defaultdict, deque

class LogLevel(Enum):
    """Log levels for the system."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """Categories for different types of logs."""
    SYSTEM = "SYSTEM"
    PROCESSING = "PROCESSING"
    TRAINING = "TRAINING"
    PERFORMANCE = "PERFORMANCE"
    ERROR = "ERROR"
    SECURITY = "SECURITY"
    CACHE = "CACHE"
    AI = "AI"

@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    details: Dict[str, Any]
    processing_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    thread_id: Optional[int] = None
    request_id: Optional[str] = None

@dataclass
class TrainingProgress:
    """Training progress tracking."""
    epoch: int
    batch: int
    total_batches: int
    loss: float
    accuracy: float
    learning_rate: float
    time_elapsed: float
    eta: float
    memory_usage: float
    gpu_usage: Optional[float] = None

class PerformanceMetrics:
    """Performance metrics collection."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.processing_times = deque(maxlen=window_size)
        self.memory_usage = deque(maxlen=window_size)
        self.cpu_usage = deque(maxlen=window_size)
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.cache_hits = 0
        self.cache_misses = 0
        
    def add_processing_time(self, time: float):
        """Add processing time to metrics."""
        self.processing_times.append(time)
    
    def add_memory_usage(self, usage: float):
        """Add memory usage to metrics."""
        self.memory_usage.append(usage)
    
    def add_cpu_usage(self, usage: float):
        """Add CPU usage to metrics."""
        self.cpu_usage.append(usage)
    
    def add_error(self, error_type: str):
        """Add error to metrics."""
        self.error_counts[error_type] += 1
    
    def add_request(self, request_type: str):
        """Add request to metrics."""
        self.request_counts[request_type] += 1
    
    def add_cache_result(self, hit: bool):
        """Add cache result to metrics."""
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            'processing_times': {
                'count': len(self.processing_times),
                'mean': np.mean(self.processing_times) if self.processing_times else 0,
                'std': np.std(self.processing_times) if self.processing_times else 0,
                'min': min(self.processing_times) if self.processing_times else 0,
                'max': max(self.processing_times) if self.processing_times else 0,
                'p95': np.percentile(list(self.processing_times), 95) if self.processing_times else 0,
                'p99': np.percentile(list(self.processing_times), 99) if self.processing_times else 0
            },
            'memory_usage': {
                'current': self.memory_usage[-1] if self.memory_usage else 0,
                'mean': np.mean(self.memory_usage) if self.memory_usage else 0,
                'max': max(self.memory_usage) if self.memory_usage else 0
            },
            'cpu_usage': {
                'current': self.cpu_usage[-1] if self.cpu_usage else 0,
                'mean': np.mean(self.cpu_usage) if self.cpu_usage else 0,
                'max': max(self.cpu_usage) if self.cpu_usage else 0
            },
            'error_counts': dict(self.error_counts),
            'request_counts': dict(self.request_counts),
            'cache_stats': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
            }
        }
        return stats

class AdvancedLogger:
    """Advanced logging system with comprehensive features."""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: LogLevel = LogLevel.INFO,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_json: bool = True,
                 enable_performance_monitoring: bool = True):
        
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_json = enable_json
        self.enable_performance_monitoring = enable_performance_monitoring
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize performance metrics
        if self.enable_performance_monitoring:
            self.performance_metrics = PerformanceMetrics()
        
        # Initialize loggers
        self._setup_loggers()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Request tracking
        self._request_counter = 0
        
        # Log startup
        self.log_system_startup()
    
    def _setup_loggers(self):
        """Setup different loggers for different purposes."""
        self.loggers = {}
        
        # Main logger
        self.loggers['main'] = self._create_logger('main', 'main.log')
        
        # Category-specific loggers
        for category in LogCategory:
            self.loggers[category.value.lower()] = self._create_logger(
                category.value.lower(), 
                f"{category.value.lower()}.log"
            )
        
        # Training logger
        self.loggers['training'] = self._create_logger('training', 'training.log')
        
        # Performance logger
        self.loggers['performance'] = self._create_logger('performance', 'performance.log')
        
        # Error logger
        self.loggers['error'] = self._create_logger('error', 'error.log')
    
    def _create_logger(self, name: str, filename: str) -> logging.Logger:
        """Create a logger with file and console handlers."""
        logger = logging.getLogger(f"image_processor.{name}")
        logger.setLevel(getattr(logging, self.log_level.value))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        json_formatter = self._create_json_formatter()
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.log_level.value))
            console_handler.setFormatter(detailed_formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if self.enable_file:
            file_path = self.log_dir / filename
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count
            )
            file_handler.setLevel(getattr(logging, self.log_level.value))
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        
        # JSON handler
        if self.enable_json:
            json_path = self.log_dir / f"{name}_json.log"
            json_handler = logging.handlers.RotatingFileHandler(
                json_path,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count
            )
            json_handler.setLevel(getattr(logging, self.log_level.value))
            json_handler.setFormatter(json_formatter)
            logger.addHandler(json_handler)
        
        return logger
    
    def _create_json_formatter(self):
        """Create a JSON formatter for structured logging."""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno,
                    'thread_id': record.thread,
                    'process_id': record.process
                }
                
                # Add extra fields if present
                if hasattr(record, 'category'):
                    log_entry['category'] = record.category
                if hasattr(record, 'processing_time'):
                    log_entry['processing_time'] = record.processing_time
                if hasattr(record, 'memory_usage'):
                    log_entry['memory_usage'] = record.memory_usage
                if hasattr(record, 'request_id'):
                    log_entry['request_id'] = record.request_id
                
                return json.dumps(log_entry)
        
        return JSONFormatter()
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'memory_usage_mb': memory_info.rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(),
                'thread_count': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections())
            }
        except Exception as e:
            return {
                'memory_usage_mb': 0,
                'cpu_percent': 0,
                'thread_count': 0,
                'open_files': 0,
                'connections': 0,
                'error': str(e)
            }
    
    def _log_with_metrics(self, 
                         logger: logging.Logger,
                         level: LogLevel,
                         message: str,
                         category: LogCategory = LogCategory.SYSTEM,
                         details: Dict[str, Any] = None,
                         processing_time: float = None,
                         request_id: str = None):
        """Log message with performance metrics."""
        with self._lock:
            # Get system metrics
            system_metrics = self._get_system_metrics()
            
            # Update performance metrics
            if self.enable_performance_monitoring:
                if processing_time is not None:
                    self.performance_metrics.add_processing_time(processing_time)
                self.performance_metrics.add_memory_usage(system_metrics['memory_usage_mb'])
                self.performance_metrics.add_cpu_usage(system_metrics['cpu_percent'])
            
            # Create log record
            record = logger.makeRecord(
                logger.name,
                getattr(logging, level.value),
                '',
                0,
                message,
                (),
                None
            )
            
            # Add custom attributes
            record.category = category.value
            record.processing_time = processing_time
            record.memory_usage = system_metrics['memory_usage_mb']
            record.request_id = request_id
            
            # Log the record
            logger.handle(record)
            
            # Log to category-specific logger
            if category.value.lower() in self.loggers:
                category_logger = self.loggers[category.value.lower()]
                category_record = category_logger.makeRecord(
                    category_logger.name,
                    getattr(logging, level.value),
                    '',
                    0,
                    message,
                    (),
                    None
                )
                category_record.category = category.value
                category_record.processing_time = processing_time
                category_record.memory_usage = system_metrics['memory_usage_mb']
                category_record.request_id = request_id
                category_logger.handle(category_record)
    
    def log_system_startup(self):
        """Log system startup information."""
        startup_info = {
            'version': '1.0.0',
            'python_version': sys.version,
            'platform': sys.platform,
            'log_level': self.log_level.value,
            'log_dir': str(self.log_dir),
            'enable_performance_monitoring': self.enable_performance_monitoring
        }
        
        self.info("🚀 Image Processing System Starting", 
                 category=LogCategory.SYSTEM,
                 details=startup_info)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, 
             details: Dict[str, Any] = None, processing_time: float = None,
             request_id: str = None):
        """Log info message."""
        self._log_with_metrics(
            self.loggers['main'],
            LogLevel.INFO,
            message,
            category,
            details,
            processing_time,
            request_id
        )
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM,
                details: Dict[str, Any] = None, processing_time: float = None,
                request_id: str = None):
        """Log warning message."""
        self._log_with_metrics(
            self.loggers['main'],
            LogLevel.WARNING,
            message,
            category,
            details,
            processing_time,
            request_id
        )
    
    def error(self, message: str, category: LogCategory = LogCategory.ERROR,
              details: Dict[str, Any] = None, processing_time: float = None,
              request_id: str = None, exception: Exception = None):
        """Log error message."""
        if exception:
            details = details or {}
            details['exception_type'] = type(exception).__name__
            details['exception_message'] = str(exception)
            details['traceback'] = traceback.format_exc()
        
        self._log_with_metrics(
            self.loggers['main'],
            LogLevel.ERROR,
            message,
            category,
            details,
            processing_time,
            request_id
        )
        
        # Also log to error logger
        self._log_with_metrics(
            self.loggers['error'],
            LogLevel.ERROR,
            message,
            category,
            details,
            processing_time,
            request_id
        )
        
        # Update error metrics
        if self.enable_performance_monitoring:
            error_type = details.get('exception_type', 'unknown') if details else 'unknown'
            self.performance_metrics.add_error(error_type)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM,
              details: Dict[str, Any] = None, processing_time: float = None,
              request_id: str = None):
        """Log debug message."""
        self._log_with_metrics(
            self.loggers['main'],
            LogLevel.DEBUG,
            message,
            category,
            details,
            processing_time,
            request_id
        )
    
    def critical(self, message: str, category: LogCategory = LogCategory.ERROR,
                 details: Dict[str, Any] = None, processing_time: float = None,
                 request_id: str = None, exception: Exception = None):
        """Log critical message."""
        if exception:
            details = details or {}
            details['exception_type'] = type(exception).__name__
            details['exception_message'] = str(exception)
            details['traceback'] = traceback.format_exc()
        
        self._log_with_metrics(
            self.loggers['main'],
            LogLevel.CRITICAL,
            message,
            category,
            details,
            processing_time,
            request_id
        )
        
        # Also log to error logger
        self._log_with_metrics(
            self.loggers['error'],
            LogLevel.CRITICAL,
            message,
            category,
            details,
            processing_time,
            request_id
        )
    
    def log_processing_start(self, task_type: str, image_size: tuple, 
                           request_id: str = None) -> str:
        """Log the start of image processing."""
        if request_id is None:
            self._request_counter += 1
            request_id = f"req_{self._request_counter:06d}"
        
        details = {
            'task_type': task_type,
            'image_size': f"{image_size[0]}x{image_size[1]}",
            'pixel_count': image_size[0] * image_size[1]
        }
        
        self.info(f"🔄 Starting {task_type} processing",
                 category=LogCategory.PROCESSING,
                 details=details,
                 request_id=request_id)
        
        return request_id
    
    def log_processing_complete(self, task_type: str, success: bool,
                               processing_time: float, request_id: str,
                               result_details: Dict[str, Any] = None):
        """Log the completion of image processing."""
        details = {
            'task_type': task_type,
            'success': success,
            'processing_time': processing_time
        }
        
        if result_details:
            details.update(result_details)
        
        if success:
            self.info(f"✅ {task_type} processing completed",
                     category=LogCategory.PROCESSING,
                     details=details,
                     processing_time=processing_time,
                     request_id=request_id)
        else:
            self.error(f"❌ {task_type} processing failed",
                      category=LogCategory.PROCESSING,
                      details=details,
                      processing_time=processing_time,
                      request_id=request_id)
    
    def log_training_progress(self, progress: TrainingProgress):
        """Log training progress."""
        message = (f"📊 Epoch {progress.epoch}/{progress.batch}/{progress.total_batches} | "
                  f"Loss: {progress.loss:.4f} | Acc: {progress.accuracy:.4f} | "
                  f"LR: {progress.learning_rate:.6f} | Time: {progress.time_elapsed:.1f}s")
        
        details = asdict(progress)
        
        self._log_with_metrics(
            self.loggers['training'],
            LogLevel.INFO,
            message,
            LogCategory.TRAINING,
            details
        )
    
    def log_training_start(self, model_name: str, dataset_size: int, 
                          epochs: int, batch_size: int, learning_rate: float):
        """Log training start."""
        details = {
            'model_name': model_name,
            'dataset_size': dataset_size,
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'start_time': datetime.now().isoformat()
        }
        
        self.info(f"🎯 Starting training for {model_name}",
                 category=LogCategory.TRAINING,
                 details=details)
    
    def log_training_complete(self, model_name: str, total_time: float,
                             final_loss: float, final_accuracy: float):
        """Log training completion."""
        details = {
            'model_name': model_name,
            'total_time': total_time,
            'final_loss': final_loss,
            'final_accuracy': final_accuracy,
            'end_time': datetime.now().isoformat()
        }
        
        self.info(f"🎉 Training completed for {model_name}",
                 category=LogCategory.TRAINING,
                 details=details)
    
    def log_performance_metrics(self):
        """Log current performance metrics."""
        if not self.enable_performance_monitoring:
            return
        
        stats = self.performance_metrics.get_statistics()
        
        message = (f"📈 Performance Stats | "
                  f"Avg Time: {stats['processing_times']['mean']:.3f}s | "
                  f"Memory: {stats['memory_usage']['current']:.1f}MB | "
                  f"Cache Hit: {stats['cache_stats']['hit_rate']:.2%}")
        
        self._log_with_metrics(
            self.loggers['performance'],
            LogLevel.INFO,
            message,
            LogCategory.PERFORMANCE,
            stats
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool,
                           processing_time: float = None):
        """Log cache operations."""
        details = {
            'operation': operation,
            'key': key,
            'hit': hit
        }
        
        if self.enable_performance_monitoring:
            self.performance_metrics.add_cache_result(hit)
        
        message = f"💾 Cache {'HIT' if hit else 'MISS'} for {operation}: {key}"
        
        self.debug(message,
                  category=LogCategory.CACHE,
                  details=details,
                  processing_time=processing_time)
    
    def log_ai_operation(self, operation: str, model_name: str, 
                        confidence: float, processing_time: float,
                        details: Dict[str, Any] = None):
        """Log AI operations."""
        ai_details = {
            'operation': operation,
            'model_name': model_name,
            'confidence': confidence
        }
        
        if details:
            ai_details.update(details)
        
        message = f"🧠 AI {operation} using {model_name} (conf: {confidence:.2f})"
        
        self.info(message,
                 category=LogCategory.AI,
                 details=ai_details,
                 processing_time=processing_time)
    
    @contextmanager
    def log_operation(self, operation_name: str, category: LogCategory = LogCategory.PROCESSING,
                     request_id: str = None):
        """Context manager for logging operations with timing."""
        start_time = time.time()
        
        if request_id is None:
            self._request_counter += 1
            request_id = f"req_{self._request_counter:06d}"
        
        self.info(f"🔄 Starting {operation_name}",
                 category=category,
                 request_id=request_id)
        
        try:
            yield request_id
            processing_time = time.time() - start_time
            self.info(f"✅ {operation_name} completed",
                     category=category,
                     details={'processing_time': processing_time},
                     processing_time=processing_time,
                     request_id=request_id)
        except Exception as e:
            processing_time = time.time() - start_time
            self.error(f"❌ {operation_name} failed",
                      category=category,
                      details={'processing_time': processing_time, 'error': str(e)},
                      processing_time=processing_time,
                      request_id=request_id,
                      exception=e)
            raise
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        if not self.enable_performance_monitoring:
            return {}
        
        return self.performance_metrics.get_statistics()
    
    def export_logs(self, output_file: str, start_time: datetime = None, 
                   end_time: datetime = None, categories: List[LogCategory] = None):
        """Export logs to a file."""
        if start_time is None:
            start_time = datetime.now() - timedelta(days=1)
        if end_time is None:
            end_time = datetime.now()
        if categories is None:
            categories = list(LogCategory)
        
        exported_logs = []
        
        for category in categories:
            log_file = self.log_dir / f"{category.value.lower()}.log"
            if log_file.exists():
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            # Parse timestamp from log line
                            timestamp_str = line.split(' | ')[0]
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            
                            if start_time <= timestamp <= end_time:
                                exported_logs.append(line.strip())
                        except:
                            continue
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(exported_logs))
        
        self.info(f"📤 Exported {len(exported_logs)} log entries to {output_file}",
                 category=LogCategory.SYSTEM,
                 details={'start_time': start_time.isoformat(),
                         'end_time': end_time.isoformat(),
                         'categories': [c.value for c in categories]})

# Global logger instance
_global_logger = None

def get_logger() -> AdvancedLogger:
    """Get the global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = AdvancedLogger()
    return _global_logger

def setup_logger(**kwargs) -> AdvancedLogger:
    """Setup the global logger with custom configuration."""
    global _global_logger
    _global_logger = AdvancedLogger(**kwargs)
    return _global_logger

# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message using global logger."""
    get_logger().info(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Log warning message using global logger."""
    get_logger().warning(message, **kwargs)

def log_error(message: str, **kwargs):
    """Log error message using global logger."""
    get_logger().error(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Log debug message using global logger."""
    get_logger().debug(message, **kwargs)

def log_critical(message: str, **kwargs):
    """Log critical message using global logger."""
    get_logger().critical(message, **kwargs)

if __name__ == "__main__":
    # Example usage
    logger = setup_logger(log_level=LogLevel.DEBUG)
    
    # Test different logging scenarios
    logger.info("🚀 System initialized successfully")
    
    with logger.log_operation("image_processing", LogCategory.PROCESSING) as request_id:
        logger.log_ai_operation("classification", "resnet50", 0.95, 0.5)
        logger.log_cache_operation("get", "image_hash_123", True, 0.01)
    
    # Log training progress
    progress = TrainingProgress(
        epoch=1,
        batch=100,
        total_batches=1000,
        loss=0.1234,
        accuracy=0.9876,
        learning_rate=0.001,
        time_elapsed=3600.0,
        eta=7200.0,
        memory_usage=2048.0
    )
    logger.log_training_progress(progress)
    
    # Log performance metrics
    logger.log_performance_metrics()
    
    print("✅ Logging system test completed!")





