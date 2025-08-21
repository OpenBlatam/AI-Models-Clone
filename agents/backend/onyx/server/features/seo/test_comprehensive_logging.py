#!/usr/bin/env python3
"""
Comprehensive Test Suite for Comprehensive Logging System
Tests all logging functionality, error handling, and integration
"""

import unittest
import tempfile
import shutil
import os
import sys
import time
import json
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
import warnings

# Suppress warnings for cleaner test output
warnings.filterwarnings("ignore")

# Add the current directory to the path to import the logging module
sys.path.append(str(Path(__file__).parent))

class TestComprehensiveLogging(unittest.TestCase):
    """Test suite for the comprehensive logging system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test logs
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Import the logging module
        try:
            from comprehensive_logging import (
                setup_logging, LoggingConfig, ComprehensiveLogger,
                TrainingMetricsLogger, ErrorTracker, SystemMonitor
            )
            self.setup_logging = setup_logging
            self.LoggingConfig = LoggingConfig
            self.ComprehensiveLogger = ComprehensiveLogger
            self.TrainingMetricsLogger = TrainingMetricsLogger
            self.ErrorTracker = ErrorTracker
            self.SystemMonitor = SystemMonitor
        except ImportError as e:
            self.skipTest(f"Could not import comprehensive_logging: {e}")
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values."""
        config = self.LoggingConfig()
        
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.log_dir, "./logs")
        self.assertEqual(config.max_file_size, 10 * 1024 * 1024)
        self.assertEqual(config.backup_count, 5)
        self.assertTrue(config.enable_console)
        self.assertTrue(config.enable_file)
        self.assertTrue(config.enable_json)
        self.assertTrue(config.log_training_metrics)
        self.assertTrue(config.log_system_metrics)
        self.assertTrue(config.enable_async_logging)
        self.assertTrue(config.enable_thread_safety)
    
    def test_logging_config_custom(self):
        """Test LoggingConfig with custom values."""
        config = self.LoggingConfig(
            log_level="DEBUG",
            log_dir=self.log_dir,
            enable_console=False,
            enable_file=True,
            log_training_metrics=False
        )
        
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.log_dir, self.log_dir)
        self.assertFalse(config.enable_console)
        self.assertTrue(config.enable_file)
        self.assertFalse(config.log_training_metrics)
    
    def test_comprehensive_logger_initialization(self):
        """Test ComprehensiveLogger initialization."""
        config = self.LoggingConfig(log_dir=self.log_dir)
        logger = self.ComprehensiveLogger("test_logger", config)
        
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.config, config)
        self.assertIsNotNone(logger.logger)
        self.assertIsNotNone(logger.training_logger)
        self.assertIsNotNone(logger.error_tracker)
        self.assertIsNotNone(logger.system_monitor)
        
        # Cleanup
        logger.cleanup()
    
    def test_basic_logging_functionality(self):
        """Test basic logging functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_console=False,  # Disable console for testing
            enable_file=True,
            enable_json=True
        )
        logger = self.ComprehensiveLogger("test_basic", config)
        
        # Test different log levels
        logger.log_info("Test info message", {"context": "test"})
        logger.log_warning("Test warning message", {"context": "test"})
        logger.log_debug("Test debug message", {"context": "test"})
        
        # Check that log files were created
        log_file = self.log_dir / "application.log"
        json_file = self.log_dir / "application.jsonl"
        
        self.assertTrue(log_file.exists())
        self.assertTrue(json_file.exists())
        
        # Cleanup
        logger.cleanup()
    
    def test_training_metrics_logging(self):
        """Test training metrics logging functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            log_training_metrics=True
        )
        logger = self.ComprehensiveLogger("test_training", config)
        
        # Log training steps
        for epoch in range(2):
            for step in range(3):
                logger.log_training_step(
                    epoch=epoch,
                    step=step,
                    loss=0.5 + epoch * 0.1 + step * 0.01,
                    accuracy=0.8 - epoch * 0.05 - step * 0.01,
                    learning_rate=0.001,
                    gradient_norm=1.0 + step * 0.1
                )
        
        # Log epoch summaries
        for epoch in range(2):
            logger.log_epoch_summary(
                epoch=epoch,
                train_loss=0.5 + epoch * 0.1,
                val_loss=0.6 + epoch * 0.1,
                train_accuracy=0.8 - epoch * 0.05,
                val_accuracy=0.75 - epoch * 0.05
            )
        
        # Check that training metrics files were created
        metrics_file = self.log_dir / "training_metrics.jsonl"
        progress_file = self.log_dir / "training_progress.csv"
        
        self.assertTrue(metrics_file.exists())
        self.assertTrue(progress_file.exists())
        
        # Check CSV format
        df = pd.read_csv(progress_file)
        self.assertEqual(len(df), 6)  # 2 epochs * 3 steps
        self.assertIn('epoch', df.columns)
        self.assertIn('step', df.columns)
        self.assertIn('loss', df.columns)
        self.assertIn('accuracy', df.columns)
        
        # Check metrics summary
        summary = logger.training_logger.get_metrics_summary()
        self.assertEqual(summary['total_epochs'], 1)  # 0-indexed
        self.assertEqual(summary['total_steps'], 2)   # 0-indexed
        self.assertEqual(summary['metrics_count'], 8)  # 6 steps + 2 summaries
        
        # Cleanup
        logger.cleanup()
    
    def test_error_tracking(self):
        """Test error tracking functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            log_errors=True
        )
        logger = self.ComprehensiveLogger("test_errors", config)
        
        # Test error logging
        test_error = ValueError("Test error message")
        logger.log_error(
            error=test_error,
            context={"operation": "test", "step": 1},
            severity="ERROR",
            recovery_attempted=False
        )
        
        # Test another error
        test_error2 = RuntimeError("Another test error")
        logger.log_error(
            error=test_error2,
            context={"operation": "test2", "step": 2},
            severity="WARNING",
            recovery_attempted=True
        )
        
        # Test recovery success
        logger.error_tracker.track_recovery_success(
            error_type="ValueError",
            recovery_method="automatic_restart"
        )
        
        # Check that error files were created
        errors_file = self.log_dir / "errors.jsonl"
        error_summary_file = self.log_dir / "error_summary.json"
        
        self.assertTrue(errors_file.exists())
        self.assertTrue(error_summary_file.exists())
        
        # Check error analysis
        analysis = logger.error_tracker.get_error_analysis()
        self.assertEqual(analysis['total_errors'], 2)
        self.assertEqual(analysis['error_counts']['ValueError'], 1)
        self.assertEqual(analysis['error_counts']['RuntimeError'], 1)
        self.assertEqual(len(analysis['most_common_errors']), 2)
        
        # Check recovery rate
        self.assertGreater(analysis['recovery_success_rate'], 0)
        
        # Cleanup
        logger.cleanup()
    
    def test_system_monitoring(self):
        """Test system monitoring functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            log_system_metrics=True
        )
        logger = self.ComprehensiveLogger("test_system", config)
        
        # Start monitoring
        logger.system_monitor.start_monitoring(interval=0.1)
        
        # Wait for some metrics to be collected
        time.sleep(0.5)
        
        # Stop monitoring
        logger.system_monitor.stop_monitoring()
        
        # Check that system metrics file was created
        metrics_file = self.log_dir / "system_metrics.jsonl"
        self.assertTrue(metrics_file.exists())
        
        # Check that metrics contain expected data
        with open(metrics_file, 'r') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0)
            
            # Parse first line
            first_metrics = json.loads(lines[0])
            self.assertIn('timestamp', first_metrics)
            self.assertIn('cpu_percent', first_metrics)
            self.assertIn('memory_percent', first_metrics)
        
        # Cleanup
        logger.cleanup()
    
    def test_performance_tracking(self):
        """Test performance tracking functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            log_performance=True
        )
        logger = self.ComprehensiveLogger("test_performance", config)
        
        # Test context manager
        with logger.performance_tracking("test_operation"):
            time.sleep(0.1)  # Simulate work
        
        # Test manual performance logging
        logger.log_performance(
            "manual_operation",
            0.2,
            operation_type="test",
            data_size=1000
        )
        
        # Check that performance was logged
        # This would be in the main log files
        log_file = self.log_dir / "application.log"
        self.assertTrue(log_file.exists())
        
        # Cleanup
        logger.cleanup()
    
    def test_logging_summary(self):
        """Test logging summary functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            log_training_metrics=True,
            log_errors=True,
            log_system_metrics=True
        )
        logger = self.ComprehensiveLogger("test_summary", config)
        
        # Generate some logs
        logger.log_training_step(epoch=0, step=0, loss=0.5)
        logger.log_info("Test message")
        
        try:
            raise ValueError("Test error")
        except Exception as e:
            logger.log_error(e, context={"test": True})
        
        # Get summary
        summary = logger.get_logging_summary()
        
        # Check summary structure
        self.assertIn('training_metrics', summary)
        self.assertIn('error_analysis', summary)
        self.assertIn('log_files', summary)
        self.assertIn('config', summary)
        
        # Check log files
        log_files = summary['log_files']
        self.assertIn('application_log', log_files)
        self.assertIn('training_metrics', log_files)
        self.assertIn('errors', log_files)
        self.assertIn('system_metrics', log_files)
        
        # Cleanup
        logger.cleanup()
    
    def test_async_logging(self):
        """Test async logging functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_async_logging=True,
            max_queue_size=100
        )
        logger = self.ComprehensiveLogger("test_async", config)
        
        # Log many messages quickly
        for i in range(50):
            logger.log_info(f"Message {i}", {"index": i})
        
        # Wait for async processing
        time.sleep(0.5)
        
        # Check that logs were written
        log_file = self.log_dir / "application.log"
        self.assertTrue(log_file.exists())
        
        # Cleanup
        logger.cleanup()
    
    def test_thread_safety(self):
        """Test thread safety functionality."""
        import threading
        
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_thread_safety=True
        )
        logger = self.ComprehensiveLogger("test_threads", config)
        
        # Create multiple threads logging simultaneously
        def log_from_thread(thread_id):
            for i in range(10):
                logger.log_info(f"Thread {thread_id} message {i}", {"thread": thread_id, "message": i})
                time.sleep(0.01)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_from_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Wait for async processing
        time.sleep(0.5)
        
        # Check that logs were written
        log_file = self.log_dir / "application.log"
        self.assertTrue(log_file.exists())
        
        # Cleanup
        logger.cleanup()
    
    def test_log_rotation(self):
        """Test log rotation functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            max_file_size=1024,  # 1KB for testing
            backup_count=3
        )
        logger = self.ComprehensiveLogger("test_rotation", config)
        
        # Write enough logs to trigger rotation
        large_message = "X" * 100  # 100 character message
        
        for i in range(20):  # This should trigger rotation
            logger.log_info(f"{large_message} - Message {i}", {"index": i})
        
        # Wait for async processing
        time.sleep(0.5)
        
        # Check that rotation occurred
        log_files = list(self.log_dir.glob("application.log*"))
        self.assertGreater(len(log_files), 1)  # Should have rotated files
        
        # Cleanup
        logger.cleanup()
    
    def test_integration_with_seo_system(self):
        """Test integration with SEO evaluation system."""
        # Mock the SEO system components
        with patch('comprehensive_logging.torch') as mock_torch:
            mock_torch.cuda.is_available.return_value = True
            mock_torch.cuda.device_count.return_value = 2
            mock_torch.cuda.get_device_name.return_value = "Test GPU"
            mock_torch.cuda.memory_allocated.return_value = 1024 * 1024 * 1024  # 1GB
            
            config = self.LoggingConfig(
                log_dir=self.log_dir,
                log_gpu_metrics=True
            )
            logger = self.ComprehensiveLogger("test_seo", config)
            
            # Simulate SEO training
            logger.log_training_step(
                epoch=0,
                step=0,
                loss=0.5,
                accuracy=0.8,
                learning_rate=0.001,
                gradient_norm=1.0,
                memory_usage=1.0  # 1GB
            )
            
            # Check that GPU metrics were collected
            system_metrics = logger.system_monitor._collect_system_metrics()
            self.assertIn('gpu_count', system_metrics)
            self.assertEqual(system_metrics['gpu_count'], 2)
            
            # Cleanup
            logger.cleanup()
    
    def test_error_recovery_scenarios(self):
        """Test various error recovery scenarios."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            log_errors=True
        )
        logger = self.ComprehensiveLogger("test_recovery", config)
        
        # Test different error types
        error_types = [
            (ValueError("Invalid input"), "ERROR"),
            (RuntimeError("Runtime issue"), "WARNING"),
            (MemoryError("Out of memory"), "CRITICAL"),
            (FileNotFoundError("File not found"), "ERROR")
        ]
        
        for error, severity in error_types:
            logger.log_error(
                error=error,
                context={"operation": "test", "error_type": type(error).__name__},
                severity=severity,
                recovery_attempted=True
            )
            
            # Simulate recovery
            logger.error_tracker.track_recovery_success(
                error_type=type(error).__name__,
                recovery_method="automatic_recovery"
            )
        
        # Check recovery statistics
        analysis = logger.error_tracker.get_error_analysis()
        self.assertEqual(analysis['total_errors'], 4)
        self.assertEqual(analysis['recovery_success_rate'], 1.0)  # All recovered
        
        # Cleanup
        logger.cleanup()
    
    def test_configuration_validation(self):
        """Test configuration validation and edge cases."""
        # Test with minimal configuration
        minimal_config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_console=False,
            enable_file=False,
            enable_json=False,
            log_training_metrics=False,
            log_system_metrics=False
        )
        
        logger = self.ComprehensiveLogger("test_minimal", minimal_config)
        
        # Should still work with minimal config
        self.assertIsNotNone(logger)
        
        # Test logging (should not fail)
        logger.log_info("Test message")
        
        # Cleanup
        logger.cleanup()
    
    def test_cleanup_functionality(self):
        """Test cleanup functionality."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            log_system_metrics=True
        )
        logger = self.ComprehensiveLogger("test_cleanup", config)
        
        # Start monitoring
        logger.system_monitor.start_monitoring(interval=0.1)
        
        # Verify monitoring is running
        self.assertTrue(logger.system_monitor.monitoring)
        
        # Cleanup
        logger.cleanup()
        
        # Verify monitoring stopped
        self.assertFalse(logger.system_monitor.monitoring)

class TestTrainingMetricsLogger(unittest.TestCase):
    """Test suite for TrainingMetricsLogger."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        try:
            from comprehensive_logging import LoggingConfig, TrainingMetricsLogger
            self.LoggingConfig = LoggingConfig
            self.TrainingMetricsLogger = TrainingMetricsLogger
        except ImportError as e:
            self.skipTest(f"Could not import TrainingMetricsLogger: {e}")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_training_metrics_logger_initialization(self):
        """Test TrainingMetricsLogger initialization."""
        config = self.LoggingConfig(log_dir=self.log_dir)
        metrics_logger = self.TrainingMetricsLogger(str(self.log_dir), config)
        
        self.assertIsNotNone(metrics_logger)
        self.assertEqual(metrics_logger.current_epoch, 0)
        self.assertEqual(metrics_logger.current_step, 0)
        self.assertEqual(len(metrics_logger.metrics_history), 0)
    
    def test_training_step_logging(self):
        """Test training step logging."""
        config = self.LoggingConfig(log_dir=self.log_dir)
        metrics_logger = self.TrainingMetricsLogger(str(self.log_dir), config)
        
        # Log training steps
        for i in range(5):
            metrics_logger.log_training_step(
                epoch=0,
                step=i,
                loss=0.5 + i * 0.1,
                accuracy=0.8 - i * 0.05,
                learning_rate=0.001,
                gradient_norm=1.0 + i * 0.1
            )
        
        # Check metrics history
        self.assertEqual(len(metrics_logger.metrics_history), 5)
        self.assertEqual(metrics_logger.current_epoch, 0)
        self.assertEqual(metrics_logger.current_step, 4)
        
        # Check files
        metrics_file = self.log_dir / "training_metrics.jsonl"
        progress_file = self.log_dir / "training_progress.csv"
        
        self.assertTrue(metrics_file.exists())
        self.assertTrue(progress_file.exists())
    
    def test_epoch_summary_logging(self):
        """Test epoch summary logging."""
        config = self.LoggingConfig(log_dir=self.log_dir)
        metrics_logger = self.TrainingMetricsLogger(str(self.log_dir), config)
        
        # Log epoch summaries
        for epoch in range(3):
            metrics_logger.log_epoch_summary(
                epoch=epoch,
                train_loss=0.5 + epoch * 0.1,
                val_loss=0.6 + epoch * 0.1,
                train_accuracy=0.8 - epoch * 0.05,
                val_accuracy=0.75 - epoch * 0.05
            )
        
        # Check metrics history
        self.assertEqual(len(metrics_logger.metrics_history), 3)
        
        # Check summary
        summary = metrics_logger.get_metrics_summary()
        self.assertEqual(summary['total_epochs'], 2)  # 0-indexed
        self.assertEqual(summary['metrics_count'], 3)

class TestErrorTracker(unittest.TestCase):
    """Test suite for ErrorTracker."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        try:
            from comprehensive_logging import LoggingConfig, ErrorTracker
            self.LoggingConfig = LoggingConfig
            self.ErrorTracker = ErrorTracker
        except ImportError as e:
            self.skipTest(f"Could not import ErrorTracker: {e}")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_error_tracker_initialization(self):
        """Test ErrorTracker initialization."""
        config = self.LoggingConfig(log_dir=self.log_dir)
        error_tracker = self.ErrorTracker(str(self.log_dir), config)
        
        self.assertIsNotNone(error_tracker)
        self.assertEqual(error_tracker.error_counts, {})
        self.assertEqual(len(error_tracker.error_timeline), 0)
        self.assertEqual(len(error_tracker.critical_errors), 0)
        self.assertEqual(len(error_tracker.recovery_attempts), 0)
    
    def test_error_tracking(self):
        """Test error tracking functionality."""
        config = self.LoggingConfig(log_dir=self.log_dir)
        error_tracker = self.ErrorTracker(str(self.log_dir), config)
        
        # Track errors
        test_error = ValueError("Test error")
        error_tracker.track_error(
            error=test_error,
            context={"operation": "test"},
            severity="ERROR",
            recovery_attempted=False
        )
        
        # Check error counts
        self.assertEqual(error_tracker.error_counts['ValueError'], 1)
        self.assertEqual(len(error_tracker.error_timeline), 1)
        
        # Track another error
        test_error2 = RuntimeError("Another error")
        error_tracker.track_error(
            error=test_error2,
            context={"operation": "test2"},
            severity="WARNING",
            recovery_attempted=True
        )
        
        # Check updated counts
        self.assertEqual(error_tracker.error_counts['ValueError'], 1)
        self.assertEqual(error_tracker.error_counts['RuntimeError'], 1)
        self.assertEqual(len(error_tracker.error_timeline), 2)
    
    def test_recovery_tracking(self):
        """Test recovery tracking functionality."""
        config = self.LoggingConfig(log_dir=self.log_dir)
        error_tracker = self.ErrorTracker(str(self.log_dir), config)
        
        # Track error with recovery
        test_error = ValueError("Test error")
        error_tracker.track_error(
            error=test_error,
            context={"operation": "test"},
            severity="ERROR",
            recovery_attempted=True
        )
        
        # Track successful recovery
        error_tracker.track_recovery_success(
            error_type="ValueError",
            recovery_method="automatic_restart"
        )
        
        # Check recovery attempts
        self.assertEqual(len(error_tracker.recovery_attempts), 2)  # Error + recovery
        
        # Check analysis
        analysis = error_tracker.get_error_analysis()
        self.assertEqual(analysis['total_errors'], 1)
        self.assertEqual(analysis['recovery_success_rate'], 1.0)

def run_performance_tests():
    """Run performance tests for the logging system."""
    print("\n=== Performance Tests ===")
    
    # Test high-volume logging
    test_dir = tempfile.mkdtemp()
    log_dir = Path(test_dir) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    try:
        from comprehensive_logging import setup_logging
        
        logger = setup_logging(
            "performance_test",
            log_dir=str(log_dir),
            enable_console=False,
            enable_file=True,
            enable_json=True,
            log_training_metrics=True,
            enable_async_logging=True,
            max_queue_size=10000
        )
        
        # High-volume logging test
        start_time = time.time()
        
        for i in range(1000):
            logger.log_training_step(
                epoch=i // 100,
                step=i % 100,
                loss=0.5 + (i % 10) * 0.1,
                accuracy=0.8 - (i % 10) * 0.05
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Logged 1000 training steps in {duration:.4f}s")
        print(f"Average: {1000/duration:.0f} logs/second")
        
        # Check file sizes
        metrics_file = log_dir / "training_metrics.jsonl"
        if metrics_file.exists():
            size_kb = metrics_file.stat().st_size / 1024
            print(f"Training metrics file size: {size_kb:.1f} KB")
        
        logger.cleanup()
        
    except Exception as e:
        print(f"Performance test failed: {e}")
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    # Run unit tests
    print("Running Comprehensive Logging System Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestComprehensiveLogging))
    test_suite.addTest(unittest.makeSuite(TestTrainingMetricsLogger))
    test_suite.addTest(unittest.makeSuite(TestErrorTracker))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance tests
    if result.wasSuccessful():
        run_performance_tests()
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
