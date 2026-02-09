#!/usr/bin/env python3
"""
Comprehensive Logging System for Diffusion Models Training

This module provides a robust, structured logging system specifically designed for
diffusion models training with comprehensive progress tracking, error handling,
and performance monitoring.
"""

import logging
import logging.handlers
import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import traceback
import threading
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

class LogLevel(Enum):
    """Log levels for different types of information."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCategory(Enum):
    """Categories for different types of logs."""
    TRAINING = "training"
    VALIDATION = "validation"
    EVALUATION = "evaluation"
    DATA_LOADING = "data_loading"
    MODEL = "model"
    OPTIMIZATION = "optimization"
    CHECKPOINT = "checkpoint"
    ERROR = "error"
    PERFORMANCE = "performance"
    SYSTEM = "system"

@dataclass
class LogConfig:
    """Configuration for the logging system."""
    # Directory settings
    log_dir: str = "logs"
    training_log_file: str = "training.log"
    validation_log_file: str = "validation.log"
    error_log_file: str = "errors.log"
    performance_log_file: str = "performance.log"
    system_log_file: str = "system.log"
    
    # Logging levels
    console_level: LogLevel = LogLevel.INFO
    file_level: LogLevel = LogLevel.DEBUG
    training_level: LogLevel = LogLevel.INFO
    validation_level: LogLevel = LogLevel.INFO
    error_level: LogLevel = LogLevel.ERROR
    performance_level: LogLevel = LogLevel.INFO
    system_level: LogLevel = LogLevel.INFO
    
    # File settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_rotation: bool = True
    enable_json_logging: bool = True
    
    # Console settings
    enable_console_logging: bool = True
    enable_colors: bool = True
    show_timestamps: bool = True
    
    # Performance settings
    enable_performance_logging: bool = True
    performance_threshold_ms: float = 100.0  # Log operations taking longer than 100ms
    
    # Error tracking
    enable_error_tracking: bool = True
    max_error_history: int = 1000
    enable_error_aggregation: bool = True
    
    # Training specific
    log_every_n_steps: int = 10
    log_every_n_epochs: int = 1
    log_hyperparameters: bool = True
    log_gradients: bool = False
    log_memory_usage: bool = True
    log_gpu_utilization: bool = True

class TrainingMetrics:
    """Container for training metrics and statistics."""
    
    def __init__(self):
        self.train_losses: List[float] = []
        self.val_losses: List[float] = []
        self.learning_rates: List[float] = []
        self.epoch_times: List[float] = []
        self.step_times: List[float] = []
        self.memory_usage: List[float] = []
        self.gpu_utilization: List[float] = []
        self.gradient_norms: List[float] = []
        self.batch_sizes: List[int] = []
        self.timestamps: List[float] = []
        
        # Performance tracking
        self.slow_operations: List[Dict[str, Any]] = []
        self.error_counts: Dict[str, int] = {}
        self.warning_counts: Dict[str, int] = []
        
        # Training state
        self.current_epoch: int = 0
        self.current_step: int = 0
        self.best_val_loss: Optional[float] = None
        self.best_epoch: Optional[int] = None
        
    def add_train_loss(self, loss: float, step: int, epoch: int):
        """Add training loss."""
        self.train_losses.append(loss)
        self.current_step = step
        self.current_epoch = epoch
        self.timestamps.append(time.time())
    
    def add_val_loss(self, loss: float, epoch: int):
        """Add validation loss."""
        self.val_losses.append(loss)
        if self.best_val_loss is None or loss < self.best_val_loss:
            self.best_val_loss = loss
            self.best_epoch = epoch
    
    def add_learning_rate(self, lr: float):
        """Add learning rate."""
        self.learning_rates.append(lr)
    
    def add_epoch_time(self, epoch_time: float):
        """Add epoch time."""
        self.epoch_times.append(epoch_time)
    
    def add_step_time(self, step_time: float):
        """Add step time."""
        self.step_times.append(step_time)
    
    def add_memory_usage(self, memory_mb: float):
        """Add memory usage."""
        self.memory_usage.append(memory_mb)
    
    def add_gpu_utilization(self, gpu_util: float):
        """Add GPU utilization."""
        self.gpu_utilization.append(gpu_util)
    
    def add_gradient_norm(self, grad_norm: float):
        """Add gradient norm."""
        self.gradient_norms.append(grad_norm)
    
    def add_batch_size(self, batch_size: int):
        """Add batch size."""
        self.batch_sizes.append(batch_size)
    
    def add_slow_operation(self, operation: str, duration_ms: float, context: str = ""):
        """Add slow operation."""
        self.slow_operations.append({
            'operation': operation,
            'duration_ms': duration_ms,
            'context': context,
            'timestamp': time.time()
        })
    
    def add_error(self, error_type: str):
        """Add error count."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def add_warning(self, warning_type: str):
        """Add warning count."""
        self.warning_counts[warning_type] = self.warning_counts.get(warning_type, 0) + 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            'total_epochs': len(self.epoch_times),
            'total_steps': len(self.train_losses),
            'best_val_loss': self.best_val_loss,
            'best_epoch': self.best_epoch,
            'avg_epoch_time': sum(self.epoch_times) / len(self.epoch_times) if self.epoch_times else 0,
            'avg_step_time': sum(self.step_times) / len(self.step_times) if self.step_times else 0,
            'avg_train_loss': sum(self.train_losses) / len(self.train_losses) if self.train_losses else 0,
            'avg_val_loss': sum(self.val_losses) / len(self.val_losses) if self.val_losses else 0,
            'error_counts': self.error_counts,
            'warning_counts': self.warning_counts,
            'slow_operations_count': len(self.slow_operations)
        }

class DiffusionLogger:
    """Main logging class for diffusion models training."""
    
    def __init__(self, config: LogConfig, experiment_name: str = "diffusion_training"):
        self.config = config
        self.experiment_name = experiment_name
        self.metrics = TrainingMetrics()
        
        # Create log directory
        self.log_dir = Path(config.log_dir) / experiment_name
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize loggers
        self._setup_loggers()
        
        # Error tracking
        self.error_history: List[Dict[str, Any]] = []
        self.error_lock = threading.Lock()
        
        # Performance tracking
        self.performance_timers: Dict[str, float] = {}
        
        # Log system initialization
        self.log_system_event("Logger initialized", LogLevel.INFO, LogCategory.SYSTEM)
    
    def _setup_loggers(self):
        """Setup all loggers with appropriate handlers and formatters."""
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        json_formatter = JsonFormatter()
        
        # Console logger
        if self.config.enable_console_logging:
            self.console_logger = self._create_console_logger(simple_formatter)
        
        # Training logger
        self.training_logger = self._create_file_logger(
            'training',
            self.config.training_log_file,
            self.config.training_level,
            detailed_formatter
        )
        
        # Validation logger
        self.validation_logger = self._create_file_logger(
            'validation',
            self.config.validation_log_file,
            self.config.validation_level,
            detailed_formatter
        )
        
        # Error logger
        self.error_logger = self._create_file_logger(
            'error',
            self.config.error_log_file,
            self.config.error_level,
            detailed_formatter
        )
        
        # Performance logger
        if self.config.enable_performance_logging:
            self.performance_logger = self._create_file_logger(
                'performance',
                self.config.performance_log_file,
                self.config.performance_level,
                json_formatter
            )
        
        # System logger
        self.system_logger = self._create_file_logger(
            'system',
            self.config.system_log_file,
            self.config.system_level,
            detailed_formatter
        )
    
    def _create_console_logger(self, formatter: logging.Formatter) -> logging.Logger:
        """Create console logger with colored output."""
        logger = logging.getLogger('console')
        logger.setLevel(self.config.console_level.value.upper())
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _create_file_logger(self, name: str, filename: str, level: LogLevel, 
                           formatter: logging.Formatter) -> logging.Logger:
        """Create file logger with rotation."""
        logger = logging.getLogger(name)
        logger.setLevel(level.value.upper())
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        if self.config.enable_rotation:
            handler = logging.handlers.RotatingFileHandler(
                self.log_dir / filename,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count
            )
        else:
            handler = logging.FileHandler(self.log_dir / filename)
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_training_step(self, step: int, epoch: int, loss: float, lr: float, 
                         batch_size: int, step_time: float, **kwargs):
        """Log training step information."""
        # Update metrics
        self.metrics.add_train_loss(loss, step, epoch)
        self.metrics.add_learning_rate(lr)
        self.metrics.add_batch_size(batch_size)
        self.metrics.add_step_time(step_time)
        
        # Log to training logger
        if step % self.config.log_every_n_steps == 0:
            message = (f"Step {step} | Epoch {epoch} | Loss: {loss:.6f} | "
                      f"LR: {lr:.2e} | Batch: {batch_size} | Time: {step_time:.3f}s")
            
            # Add additional kwargs
            for key, value in kwargs.items():
                if isinstance(value, float):
                    message += f" | {key}: {value:.4f}"
                else:
                    message += f" | {key}: {value}"
            
            self.training_logger.info(message)
            
            # Log to console if enabled
            if self.config.enable_console_logging:
                self.console_logger.info(message)
    
    def log_validation_step(self, step: int, epoch: int, val_loss: float, 
                           metrics: Optional[Dict[str, float]] = None):
        """Log validation step information."""
        # Update metrics
        self.metrics.add_val_loss(val_loss, epoch)
        
        message = f"Validation | Step {step} | Epoch {epoch} | Loss: {val_loss:.6f}"
        
        if metrics:
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, float):
                    message += f" | {metric_name}: {metric_value:.4f}"
                else:
                    message += f" | {metric_name}: {metric_value}"
        
        self.validation_logger.info(message)
        
        # Log to console if enabled
        if self.config.enable_console_logging:
            self.console_logger.info(message)
    
    def log_epoch_summary(self, epoch: int, train_loss: float, val_loss: Optional[float], 
                         epoch_time: float, **kwargs):
        """Log epoch summary."""
        # Update metrics
        self.metrics.add_epoch_time(epoch_time)
        
        message = (f"Epoch {epoch} Summary | Train Loss: {train_loss:.6f} | "
                  f"Time: {epoch_time:.2f}s")
        
        if val_loss is not None:
            message += f" | Val Loss: {val_loss:.6f}"
        
        # Add additional kwargs
        for key, value in kwargs.items():
            if isinstance(value, float):
                message += f" | {key}: {value:.4f}"
            else:
                message += f" | {key}: {value}"
        
        self.training_logger.info(message)
        
        # Log to console if enabled
        if self.config.enable_console_logging:
            self.console_logger.info(message)
    
    def log_hyperparameters(self, hyperparams: Dict[str, Any]):
        """Log hyperparameters."""
        if not self.config.log_hyperparameters:
            return
        
        message = "Hyperparameters:"
        for key, value in hyperparams.items():
            message += f"\n  {key}: {value}"
        
        self.training_logger.info(message)
        self.system_logger.info(message)
    
    def log_gradient_info(self, grad_norm: float, grad_clip: bool = False):
        """Log gradient information."""
        if not self.config.log_gradients:
            return
        
        self.metrics.add_gradient_norm(grad_norm)
        
        message = f"Gradient Norm: {grad_norm:.6f}"
        if grad_clip:
            message += " (clipped)"
        
        self.training_logger.info(message)
    
    def log_memory_usage(self, memory_mb: float):
        """Log memory usage."""
        if not self.config.log_memory_usage:
            return
        
        self.metrics.add_memory_usage(memory_mb)
        
        if memory_mb > 1000:  # More than 1GB
            self.training_logger.warning(f"High memory usage: {memory_mb:.1f} MB")
        else:
            self.training_logger.debug(f"Memory usage: {memory_mb:.1f} MB")
    
    def log_gpu_utilization(self, gpu_util: float):
        """Log GPU utilization."""
        if not self.config.log_gpu_utilization:
            return
        
        self.metrics.add_gpu_utilization(gpu_util)
        
        if gpu_util < 50:  # Less than 50%
            self.training_logger.warning(f"Low GPU utilization: {gpu_util:.1f}%")
        else:
            self.training_logger.debug(f"GPU utilization: {gpu_util:.1f}%")
    
    def log_error(self, error: Exception, context: str = "", level: LogLevel = LogLevel.ERROR):
        """Log error with context."""
        error_info = {
            'timestamp': time.time(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc(),
            'level': level.value
        }
        
        # Add to error history
        with self.error_lock:
            self.error_history.append(error_info)
            if len(self.error_history) > self.config.max_error_history:
                self.error_history.pop(0)
        
        # Update metrics
        self.metrics.add_error(error_info['error_type'])
        
        # Log to appropriate logger
        message = f"Error in {context}: {error}"
        
        if level == LogLevel.CRITICAL:
            self.error_logger.critical(message)
            self.console_logger.critical(message)
        elif level == LogLevel.ERROR:
            self.error_logger.error(message)
            self.console_logger.error(message)
        elif level == LogLevel.WARNING:
            self.error_logger.warning(message)
            self.console_logger.warning(message)
        
        # Log detailed error info
        self.error_logger.error(f"Error details: {json.dumps(error_info, indent=2)}")
    
    def log_warning(self, message: str, context: str = ""):
        """Log warning message."""
        full_message = f"Warning in {context}: {message}" if context else f"Warning: {message}"
        
        self.error_logger.warning(full_message)
        self.console_logger.warning(full_message)
        
        # Update metrics
        self.metrics.add_warning("general")
    
    def log_performance(self, operation: str, duration_ms: float, context: str = "", 
                       metadata: Optional[Dict[str, Any]] = None):
        """Log performance information."""
        if not self.config.enable_performance_logging:
            return
        
        # Check if operation is slow
        if duration_ms > self.config.performance_threshold_ms:
            self.metrics.add_slow_operation(operation, duration_ms, context)
            self.training_logger.warning(
                f"Slow operation: {operation} took {duration_ms:.2f}ms in {context}"
            )
        
        # Log to performance logger
        perf_data = {
            'operation': operation,
            'duration_ms': duration_ms,
            'context': context,
            'timestamp': time.time()
        }
        
        if metadata:
            perf_data.update(metadata)
        
        self.performance_logger.info(json.dumps(perf_data))
    
    def log_system_event(self, message: str, level: LogLevel = LogLevel.INFO, 
                        category: LogCategory = LogCategory.SYSTEM):
        """Log system event."""
        full_message = f"[{category.value.upper()}] {message}"
        
        if level == LogLevel.INFO:
            self.system_logger.info(full_message)
        elif level == LogLevel.WARNING:
            self.system_logger.warning(full_message)
        elif level == LogLevel.ERROR:
            self.system_logger.error(full_message)
        elif level == LogLevel.CRITICAL:
            self.system_logger.critical(full_message)
        elif level == LogLevel.DEBUG:
            self.system_logger.debug(full_message)
    
    def start_performance_timer(self, operation: str):
        """Start performance timer for an operation."""
        self.performance_timers[operation] = time.time()
    
    def end_performance_timer(self, operation: str, context: str = "", 
                            metadata: Optional[Dict[str, Any]] = None):
        """End performance timer and log duration."""
        if operation not in self.performance_timers:
            return
        
        start_time = self.performance_timers.pop(operation)
        duration_ms = (time.time() - start_time) * 1000
        
        self.log_performance(operation, duration_ms, context, metadata)
    
    def performance_timer(self, operation: str, context: str = ""):
        """Context manager for performance timing."""
        return PerformanceTimer(self, operation, context)
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary."""
        return {
            'experiment_name': self.experiment_name,
            'log_directory': str(self.log_dir),
            'metrics_summary': self.metrics.get_summary(),
            'error_summary': self._get_error_summary(),
            'performance_summary': self._get_performance_summary(),
            'log_files': self._get_log_files_info()
        }
    
    def _get_error_summary(self) -> Dict[str, Any]:
        """Get error summary."""
        if not self.error_history:
            return {'total_errors': 0, 'error_types': {}}
        
        error_types = {}
        for error in self.error_history:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'error_types': error_types,
            'recent_errors': self.error_history[-10:]  # Last 10 errors
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        slow_ops = self.metrics.slow_operations
        
        if not slow_ops:
            return {'slow_operations': 0, 'avg_duration': 0}
        
        avg_duration = sum(op['duration_ms'] for op in slow_ops) / len(slow_ops)
        
        return {
            'slow_operations': len(slow_ops),
            'avg_duration_ms': avg_duration,
            'slowest_operations': sorted(slow_ops, key=lambda x: x['duration_ms'], reverse=True)[:5]
        }
    
    def _get_log_files_info(self) -> Dict[str, Any]:
        """Get information about log files."""
        log_files = {}
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                log_files[log_file.name] = {
                    'size_mb': stat.st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            except Exception:
                continue
        
        return log_files
    
    def save_metrics(self, filepath: Optional[str] = None):
        """Save metrics to file."""
        if filepath is None:
            filepath = self.log_dir / "training_metrics.json"
        
        metrics_data = {
            'experiment_name': self.experiment_name,
            'timestamp': time.time(),
            'metrics': asdict(self.metrics),
            'summary': self.get_training_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2, default=str)
        
        self.system_logger.info(f"Metrics saved to {filepath}")
    
    def cleanup(self):
        """Cleanup logging resources."""
        # Close all handlers
        for logger_name in ['training', 'validation', 'error', 'performance', 'system']:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        
        # Save final metrics
        self.save_metrics()
        
        self.system_logger.info("Logger cleanup completed")

class PerformanceTimer:
    """Context manager for performance timing."""
    
    def __init__(self, logger: DiffusionLogger, operation: str, context: str = ""):
        self.logger = logger
        self.operation = operation
        self.context = context
    
    def __enter__(self):
        self.logger.start_performance_timer(self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.end_performance_timer(self.operation, self.context)

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

# Utility functions
def create_logger(config: Optional[LogConfig] = None, experiment_name: str = "diffusion_training") -> DiffusionLogger:
    """Create a logger instance with default or custom configuration."""
    if config is None:
        config = LogConfig()
    
    return DiffusionLogger(config, experiment_name)

def log_training_step(logger: DiffusionLogger, step: int, epoch: int, loss: float, 
                     lr: float, batch_size: int, step_time: float, **kwargs):
    """Convenience function for logging training step."""
    logger.log_training_step(step, epoch, loss, lr, batch_size, step_time, **kwargs)

def log_validation_step(logger: DiffusionLogger, step: int, epoch: int, val_loss: float, 
                       metrics: Optional[Dict[str, float]] = None):
    """Convenience function for logging validation step."""
    logger.log_validation_step(step, epoch, val_loss, metrics)

def log_epoch_summary(logger: DiffusionLogger, epoch: int, train_loss: float, 
                     val_loss: Optional[float], epoch_time: float, **kwargs):
    """Convenience function for logging epoch summary."""
    logger.log_epoch_summary(epoch, train_loss, val_loss, epoch_time, **kwargs)

def log_error(logger: DiffusionLogger, error: Exception, context: str = "", 
              level: LogLevel = LogLevel.ERROR):
    """Convenience function for logging errors."""
    logger.log_error(error, context, level)

def log_warning(logger: DiffusionLogger, message: str, context: str = ""):
    """Convenience function for logging warnings."""
    logger.log_warning(message, context)

def log_performance(logger: DiffusionLogger, operation: str, duration_ms: float, 
                   context: str = "", metadata: Optional[Dict[str, Any]] = None):
    """Convenience function for logging performance."""
    logger.log_performance(operation, duration_ms, context, metadata)

# Example usage
if __name__ == "__main__":
    # Create logger with custom configuration
    config = LogConfig(
        log_dir="logs",
        enable_console_logging=True,
        enable_colors=True,
        log_every_n_steps=5,
        enable_performance_logging=True
    )
    
    logger = create_logger(config, "example_training")
    
    # Log hyperparameters
    hyperparams = {
        'learning_rate': 1e-4,
        'batch_size': 32,
        'num_epochs': 100,
        'model_name': 'stable-diffusion-v1-5'
    }
    logger.log_hyperparameters(hyperparams)
    
    # Simulate training steps
    for epoch in range(3):
        for step in range(10):
            # Simulate training
            loss = 0.5 + 0.1 * (epoch * 10 + step)
            lr = 1e-4 * (0.9 ** epoch)
            
            # Log training step
            logger.log_training_step(
                step=step,
                epoch=epoch,
                loss=loss,
                lr=lr,
                batch_size=32,
                step_time=0.1
            )
        
        # Log epoch summary
        logger.log_epoch_summary(
            epoch=epoch,
            train_loss=0.5,
            val_loss=0.6,
            epoch_time=1.0
        )
    
    # Log some errors and warnings
    try:
        raise ValueError("Example error for testing")
    except Exception as e:
        logger.log_error(e, "example_function")
    
    logger.log_warning("Example warning message", "example_function")
    
    # Performance logging
    with logger.performance_timer("example_operation"):
        time.sleep(0.1)  # Simulate work
    
    # Get and print summary
    summary = logger.get_training_summary()
    print("\nTraining Summary:")
    print(json.dumps(summary, indent=2, default=str))
    
    # Cleanup
    logger.cleanup()
    
    print("✅ Logging system demo completed!")
