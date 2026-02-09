#!/usr/bin/env python3
"""
Diffusion Logging System Demo

This script demonstrates the comprehensive logging system for diffusion models training
with various scenarios including training progress, error handling, and performance monitoring.
"""

import time
import random
import numpy as np
from pathlib import Path
import json

# Import the logging system
try:
    from core.diffusion_logging_system import (
        DiffusionLogger, LogConfig, LogLevel, LogCategory,
        create_logger, log_training_step, log_validation_step,
        log_epoch_summary, log_error, log_warning, log_performance
    )
    print("✅ Successfully imported diffusion logging system")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Creating simplified logging system for demo...")
    
    # Simplified logging classes for demo
    class LogLevel:
        DEBUG = "debug"
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        CRITICAL = "critical"
    
    class LogCategory:
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
    
    class LogConfig:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class DiffusionLogger:
        def __init__(self, config, experiment_name):
            self.config = config
            self.experiment_name = experiment_name
            print(f"📝 Logger initialized for experiment: {experiment_name}")
        
        def log_training_step(self, step, epoch, loss, lr, batch_size, step_time, **kwargs):
            print(f"🏃 Training Step {step} | Epoch {epoch} | Loss: {loss:.6f} | LR: {lr:.2e}")
        
        def log_validation_step(self, step, epoch, val_loss, metrics=None):
            print(f"✅ Validation Step {step} | Epoch {epoch} | Loss: {val_loss:.6f}")
        
        def log_epoch_summary(self, epoch, train_loss, val_loss, epoch_time, **kwargs):
            print(f"📊 Epoch {epoch} Summary | Train: {train_loss:.6f} | Val: {val_loss:.6f} | Time: {epoch_time:.2f}s")
        
        def log_error(self, error, context="", level=LogLevel.ERROR):
            print(f"❌ Error in {context}: {error}")
        
        def log_warning(self, message, context=""):
            print(f"⚠️ Warning in {context}: {message}")
        
        def log_performance(self, operation, duration_ms, context="", metadata=None):
            print(f"⚡ Performance: {operation} took {duration_ms:.2f}ms in {context}")
        
        def log_hyperparameters(self, hyperparams):
            print("🔧 Hyperparameters:")
            for key, value in hyperparams.items():
                print(f"  {key}: {value}")
        
        def log_memory_usage(self, memory_mb):
            print(f"💾 Memory usage: {memory_mb:.1f} MB")
        
        def log_gpu_utilization(self, gpu_util):
            print(f"🎮 GPU utilization: {gpu_util:.1f}%")
        
        def performance_timer(self, operation, context=""):
            return MockPerformanceTimer(operation, context)
        
        def get_training_summary(self):
            return {"status": "demo_mode", "experiment": self.experiment_name}
        
        def cleanup(self):
            print("🧹 Logger cleanup completed")
    
    class MockPerformanceTimer:
        def __init__(self, operation, context):
            self.operation = operation
            self.context = context
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    # Mock utility functions
    def create_logger(config=None, experiment_name="diffusion_training"):
        if config is None:
            config = LogConfig()
        return DiffusionLogger(config, experiment_name)
    
    def log_training_step(logger, step, epoch, loss, lr, batch_size, step_time, **kwargs):
        logger.log_training_step(step, epoch, loss, lr, batch_size, step_time, **kwargs)
    
    def log_validation_step(logger, step, epoch, val_loss, metrics=None):
        logger.log_validation_step(step, epoch, val_loss, metrics)
    
    def log_epoch_summary(logger, epoch, train_loss, val_loss, epoch_time, **kwargs):
        logger.log_epoch_summary(epoch, train_loss, val_loss, epoch_time, **kwargs)
    
    def log_error(logger, error, context="", level=LogLevel.ERROR):
        logger.log_error(error, context, level)
    
    def log_warning(logger, message, context=""):
        logger.log_warning(message, context)
    
    def log_performance(logger, operation, duration_ms, context="", metadata=None):
        logger.log_performance(operation, duration_ms, context, metadata)

def demo_basic_logging():
    """Demo basic logging functionality."""
    print("\n" + "="*60)
    print("🔧 BASIC LOGGING DEMO")
    print("="*60)
    
    # Create logger with custom configuration
    config = LogConfig(
        log_dir="logs",
        enable_console_logging=True,
        enable_colors=True,
        log_every_n_steps=5,
        enable_performance_logging=True,
        log_hyperparameters=True,
        log_memory_usage=True,
        log_gpu_utilization=True
    )
    
    logger = create_logger(config, "basic_logging_demo")
    
    # Log hyperparameters
    hyperparams = {
        'learning_rate': 1e-4,
        'batch_size': 32,
        'num_epochs': 10,
        'model_name': 'stable-diffusion-v1-5',
        'optimizer': 'AdamW',
        'scheduler': 'CosineAnnealingLR'
    }
    logger.log_hyperparameters(hyperparams)
    
    # Simulate training steps
    print("\n🏃 Simulating training steps...")
    for epoch in range(3):
        for step in range(10):
            # Simulate training metrics
            loss = 0.5 + 0.1 * (epoch * 10 + step) + random.uniform(-0.05, 0.05)
            lr = 1e-4 * (0.9 ** epoch)
            step_time = random.uniform(0.08, 0.12)
            
            # Log training step
            log_training_step(
                logger=logger,
                step=step,
                epoch=epoch,
                loss=loss,
                lr=lr,
                batch_size=32,
                step_time=step_time
            )
            
            # Simulate memory and GPU usage
            memory_mb = 800 + random.uniform(-50, 100)
            gpu_util = 70 + random.uniform(-20, 30)
            
            logger.log_memory_usage(memory_mb)
            logger.log_gpu_utilization(gpu_util)
            
            time.sleep(0.1)  # Simulate processing time
        
        # Log epoch summary
        train_loss = 0.5 + 0.1 * epoch
        val_loss = train_loss + random.uniform(0.05, 0.15)
        epoch_time = 1.0 + random.uniform(-0.1, 0.1)
        
        log_epoch_summary(
            logger=logger,
            epoch=epoch,
            train_loss=train_loss,
            val_loss=val_loss,
            epoch_time=epoch_time
        )
    
    # Cleanup
    logger.cleanup()
    print("✅ Basic logging demo completed!")

def demo_error_handling():
    """Demo error handling and logging."""
    print("\n" + "="*60)
    print("🚨 ERROR HANDLING DEMO")
    print("="*60)
    
    config = LogConfig(
        log_dir="logs",
        enable_console_logging=True,
        enable_error_tracking=True,
        max_error_history=100
    )
    
    logger = create_logger(config, "error_handling_demo")
    
    # Simulate various types of errors
    print("\n❌ Simulating different types of errors...")
    
    # Data loading error
    try:
        raise FileNotFoundError("Training data not found at /path/to/data")
    except Exception as e:
        log_error(logger, e, "data_loading", LogLevel.ERROR)
    
    # Model error
    try:
        raise RuntimeError("CUDA out of memory. Tried to allocate 2.00 GiB")
    except Exception as e:
        log_error(logger, e, "model_inference", LogLevel.CRITICAL)
    
    # Validation error
    try:
        raise ValueError("Invalid input shape: expected (3, 512, 512), got (3, 256, 256)")
    except Exception as e:
        log_error(logger, e, "validation", LogLevel.WARNING)
    
    # Optimization error
    try:
        raise RuntimeError("Gradient contains NaN values")
    except Exception as e:
        log_error(logger, e, "optimization", LogLevel.ERROR)
    
    # System error
    try:
        raise OSError("Disk space full: only 1.2 GB available")
    except Exception as e:
        log_error(logger, e, "system", LogLevel.CRITICAL)
    
    # Log warnings
    print("\n⚠️ Simulating warnings...")
    log_warning(logger, "Learning rate may be too high", "training")
    log_warning(logger, "Batch size might exceed GPU memory", "data_loading")
    log_warning(logger, "Validation loss not improving", "validation")
    
    # Cleanup
    logger.cleanup()
    print("✅ Error handling demo completed!")

def demo_performance_monitoring():
    """Demo performance monitoring and timing."""
    print("\n" + "="*60)
    print("⚡ PERFORMANCE MONITORING DEMO")
    print("="*60)
    
    config = LogConfig(
        log_dir="logs",
        enable_console_logging=True,
        enable_performance_logging=True,
        performance_threshold_ms=50.0  # Log operations taking longer than 50ms
    )
    
    logger = create_logger(config, "performance_monitoring_demo")
    
    print("\n⏱️ Simulating performance monitoring...")
    
    # Simulate various operations with different durations
    operations = [
        ("data_loading", 30, "Loading training batch"),
        ("forward_pass", 45, "Model forward pass"),
        ("loss_computation", 15, "Computing loss"),
        ("backward_pass", 80, "Model backward pass"),  # This will trigger warning
        ("optimizer_step", 25, "Optimizer update"),
        ("validation_inference", 120, "Validation inference"),  # This will trigger warning
        ("checkpoint_saving", 200, "Saving model checkpoint"),  # This will trigger warning
        ("metric_computation", 35, "Computing evaluation metrics")
    ]
    
    for operation, duration_ms, context in operations:
        # Simulate the operation
        time.sleep(duration_ms / 1000)  # Convert ms to seconds
        
        # Log performance
        log_performance(logger, operation, duration_ms, context)
        
        # Use performance timer
        with logger.performance_timer(f"timed_{operation}", context):
            time.sleep(duration_ms / 1000)  # Simulate work
    
    # Simulate memory and GPU monitoring
    print("\n💾 Simulating memory and GPU monitoring...")
    for i in range(5):
        memory_mb = 800 + random.uniform(-100, 200)
        gpu_util = 60 + random.uniform(-30, 40)
        
        logger.log_memory_usage(memory_mb)
        logger.log_gpu_utilization(gpu_util)
        
        time.sleep(0.2)
    
    # Cleanup
    logger.cleanup()
    print("✅ Performance monitoring demo completed!")

def demo_advanced_training_scenario():
    """Demo advanced training scenario with comprehensive logging."""
    print("\n" + "="*60)
    print("🎯 ADVANCED TRAINING SCENARIO DEMO")
    print("="*60)
    
    config = LogConfig(
        log_dir="logs",
        enable_console_logging=True,
        enable_performance_logging=True,
        log_every_n_steps=3,
        log_hyperparameters=True,
        log_memory_usage=True,
        log_gpu_utilization=True,
        enable_error_tracking=True
    )
    
    logger = create_logger(config, "advanced_training_demo")
    
    # Log experiment configuration
    experiment_config = {
        'model': 'stable-diffusion-xl-base-1.0',
        'dataset': 'laion-aesthetics-6.5+',
        'resolution': '1024x1024',
        'learning_rate': 1e-5,
        'batch_size': 16,
        'gradient_accumulation_steps': 4,
        'max_grad_norm': 1.0,
        'mixed_precision': True,
        'gradient_checkpointing': True
    }
    logger.log_hyperparameters(experiment_config)
    
    print("\n🚀 Simulating advanced training scenario...")
    
    # Simulate training with various scenarios
    num_epochs = 5
    steps_per_epoch = 20
    
    for epoch in range(num_epochs):
        print(f"\n📚 Starting Epoch {epoch + 1}/{num_epochs}")
        
        epoch_start_time = time.time()
        epoch_losses = []
        
        for step in range(steps_per_epoch):
            step_start_time = time.time()
            
            # Simulate training step
            loss = 0.8 + 0.2 * (epoch * steps_per_epoch + step) + random.uniform(-0.1, 0.1)
            lr = 1e-5 * (0.95 ** epoch)
            
            # Simulate some errors occasionally
            if random.random() < 0.05:  # 5% chance of error
                try:
                    raise RuntimeError(f"Simulated training error at step {step}")
                except Exception as e:
                    log_error(logger, e, f"training_step_{step}", LogLevel.ERROR)
                    continue
            
            # Simulate performance variations
            step_time = random.uniform(0.1, 0.3)
            memory_mb = 1200 + random.uniform(-100, 200)
            gpu_util = 80 + random.uniform(-20, 20)
            
            # Log training step
            log_training_step(
                logger=logger,
                step=step,
                epoch=epoch,
                loss=loss,
                lr=lr,
                batch_size=16,
                step_time=step_time
            )
            
            # Log system metrics
            logger.log_memory_usage(memory_mb)
            logger.log_gpu_utilization(gpu_util)
            
            epoch_losses.append(loss)
            
            # Simulate processing time
            time.sleep(0.05)
        
        # Epoch summary
        epoch_time = time.time() - epoch_start_time
        avg_train_loss = sum(epoch_losses) / len(epoch_losses)
        val_loss = avg_train_loss + random.uniform(0.1, 0.3)
        
        log_epoch_summary(
            logger=logger,
            epoch=epoch,
            train_loss=avg_train_loss,
            val_loss=val_loss,
            epoch_time=epoch_time
        )
        
        # Simulate checkpoint saving
        if (epoch + 1) % 2 == 0:  # Every 2 epochs
            with logger.performance_timer("checkpoint_saving", f"epoch_{epoch}"):
                time.sleep(0.5)  # Simulate checkpoint saving
            print(f"💾 Checkpoint saved for epoch {epoch + 1}")
    
    # Final evaluation
    print("\n🔍 Running final evaluation...")
    with logger.performance_timer("final_evaluation", "training_completion"):
        time.sleep(1.0)  # Simulate evaluation
    
    # Get training summary
    summary = logger.get_training_summary()
    print(f"\n📊 Training Summary:")
    print(f"  Experiment: {summary.get('experiment_name', 'Unknown')}")
    print(f"  Status: {summary.get('status', 'Completed')}")
    
    # Cleanup
    logger.cleanup()
    print("✅ Advanced training scenario demo completed!")

def demo_log_analysis():
    """Demo log analysis and summary generation."""
    print("\n" + "="*60)
    print("📊 LOG ANALYSIS DEMO")
    print("="*60)
    
    # Create a logger and run some operations
    config = LogConfig(
        log_dir="logs",
        enable_console_logging=True,
        enable_performance_logging=True,
        enable_error_tracking=True
    )
    
    logger = create_logger(config, "log_analysis_demo")
    
    print("\n📝 Generating sample logs for analysis...")
    
    # Generate various log entries
    for i in range(10):
        # Training logs
        log_training_step(
            logger=logger,
            step=i,
            epoch=0,
            loss=0.5 + i * 0.01,
            lr=1e-4,
            batch_size=32,
            step_time=0.1
        )
        
        # Performance logs
        duration = random.uniform(20, 150)
        log_performance(logger, f"operation_{i}", duration, "demo_context")
        
        # Some errors
        if i % 3 == 0:
            try:
                raise ValueError(f"Sample error {i}")
            except Exception as e:
                log_error(logger, e, f"demo_function_{i}")
        
        time.sleep(0.1)
    
    # Get and display summary
    summary = logger.get_training_summary()
    
    print(f"\n📊 Generated Summary:")
    print(f"  Experiment: {summary.get('experiment_name', 'Unknown')}")
    print(f"  Status: {summary.get('status', 'Demo')}")
    
    # Simulate log file analysis
    print(f"\n📁 Log Directory: {config.log_dir}")
    print("📋 Log Files Created:")
    print("  - training.log")
    print("  - validation.log")
    print("  - errors.log")
    print("  - performance.log")
    print("  - system.log")
    print("  - training_metrics.json")
    
    # Cleanup
    logger.cleanup()
    print("✅ Log analysis demo completed!")

def main():
    """Run all demos."""
    print("🚀 DIFFUSION LOGGING SYSTEM DEMO")
    print("="*60)
    print("This demo showcases the comprehensive logging system for diffusion models training.")
    print("Features include:")
    print("  ✅ Training progress logging")
    print("  ✅ Error handling and tracking")
    print("  ✅ Performance monitoring")
    print("  ✅ Memory and GPU utilization tracking")
    print("  ✅ Structured logging with JSON support")
    print("  ✅ Log rotation and management")
    print("  ✅ Comprehensive metrics collection")
    
    try:
        # Run all demos
        demo_basic_logging()
        demo_error_handling()
        demo_performance_monitoring()
        demo_advanced_training_scenario()
        demo_log_analysis()
        
        print("\n" + "="*60)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("The logging system has been demonstrated with various scenarios:")
        print("  📝 Basic training logging with metrics")
        print("  🚨 Error handling and tracking")
        print("  ⚡ Performance monitoring and timing")
        print("  🎯 Advanced training scenarios")
        print("  📊 Log analysis and summary generation")
        print("\nCheck the 'logs' directory for generated log files!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
