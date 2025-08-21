#!/usr/bin/env python3
"""
Comprehensive Test Suite for PyTorch Debugging Tools
Tests all PyTorch debugging functionality integrated with comprehensive logging
"""

import unittest
import tempfile
import shutil
import os
import sys
import time
import json
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
import warnings

# Suppress warnings for cleaner test output
warnings.filterwarnings("ignore")

# Add the current directory to the path to import the logging module
sys.path.append(str(Path(__file__).parent))

class TestPyTorchDebugTools(unittest.TestCase):
    """Test suite for PyTorch debugging tools."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test logs
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Import the logging module
        try:
            from comprehensive_logging import (
                setup_logging, LoggingConfig, PyTorchDebugTools
            )
            self.setup_logging = setup_logging
            self.LoggingConfig = LoggingConfig
            self.PyTorchDebugTools = PyTorchDebugTools
        except ImportError as e:
            self.skipTest(f"Could not import comprehensive_logging: {e}")
        
        # Create a simple test model
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        
        # Create test data
        self.x = torch.randn(32, 10)
        self.y = torch.randn(32, 1)
        self.criterion = nn.MSELoss()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_pytorch_debug_tools_initialization(self):
        """Test PyTorchDebugTools initialization."""
        config = self.LoggingConfig(
            enable_pytorch_debugging=True,
            enable_gradient_debugging=True,
            enable_memory_debugging=True,
            enable_tensor_debugging=True
        )
        
        debug_tools = self.PyTorchDebugTools(config)
        
        self.assertIsNotNone(debug_tools)
        self.assertEqual(debug_tools.config, config)
        self.assertFalse(debug_tools.anomaly_detection_enabled)
        self.assertFalse(debug_tools.profiler_active)
        self.assertEqual(len(debug_tools.gradient_history), 0)
    
    def test_anomaly_detection_control(self):
        """Test anomaly detection enable/disable."""
        config = self.LoggingConfig(enable_pytorch_debugging=True)
        debug_tools = self.PyTorchDebugTools(config)
        
        # Test enabling
        success = debug_tools.enable_anomaly_detection(True)
        self.assertTrue(success)
        self.assertTrue(debug_tools.anomaly_detection_enabled)
        
        # Test disabling
        success = debug_tools.enable_anomaly_detection(False)
        self.assertTrue(success)
        self.assertFalse(debug_tools.anomaly_detection_enabled)
    
    def test_gradient_debugging(self):
        """Test gradient debugging functionality."""
        config = self.LoggingConfig(enable_gradient_debugging=True)
        debug_tools = self.PyTorchDebugTools(config)
        
        # Forward pass
        output = self.model(self.x)
        loss = self.criterion(output, self.y)
        
        # Backward pass
        loss.backward()
        
        # Debug gradients
        debug_info = debug_tools.debug_gradients(self.model, loss)
        
        # Check debug info structure
        self.assertIn('total_grad_norm', debug_info)
        self.assertIn('param_count', debug_info)
        self.assertIn('nan_gradients', debug_info)
        self.assertIn('inf_gradients', debug_info)
        self.assertIn('loss_value', debug_info)
        
        # Check gradient history
        self.assertEqual(len(debug_tools.gradient_history), 1)
        history_entry = debug_tools.gradient_history[0]
        self.assertIn('timestamp', history_entry)
        self.assertIn('total_norm', history_entry)
    
    def test_memory_debugging(self):
        """Test memory debugging functionality."""
        config = self.LoggingConfig(enable_memory_debugging=True)
        debug_tools = self.PyTorchDebugTools(config)
        
        # Debug memory
        memory_info = debug_tools.debug_memory_usage()
        
        # Check memory info structure
        self.assertIsInstance(memory_info, dict)
        
        # If CUDA is available, check CUDA-specific info
        if torch.cuda.is_available():
            self.assertIn('cuda_memory_allocated', memory_info)
            self.assertIn('cuda_memory_reserved', memory_info)
    
    def test_tensor_debugging(self):
        """Test tensor debugging functionality."""
        config = self.LoggingConfig(enable_tensor_debugging=True)
        debug_tools = self.PyTorchDebugTools(config)
        
        # Create test tensor
        test_tensor = torch.randn(5, 10, requires_grad=True)
        
        # Debug tensor
        tensor_info = debug_tools.debug_tensor_info(test_tensor, "test_tensor")
        
        # Check tensor info structure
        self.assertIn('test_tensor_shape', tensor_info)
        self.assertIn('test_tensor_dtype', tensor_info)
        self.assertIn('test_tensor_device', tensor_info)
        self.assertIn('test_tensor_requires_grad', tensor_info)
        self.assertIn('test_tensor_has_nan', tensor_info)
        self.assertIn('test_tensor_has_inf', tensor_info)
        
        # Check specific values
        self.assertEqual(tensor_info['test_tensor_shape'], [5, 10])
        self.assertTrue(tensor_info['test_tensor_requires_grad'])
        self.assertFalse(tensor_info['test_tensor_has_nan'])
        self.assertFalse(tensor_info['test_tensor_has_inf'])
    
    def test_model_state_debugging(self):
        """Test model state debugging functionality."""
        config = self.LoggingConfig(enable_tensor_debugging=True)
        debug_tools = self.PyTorchDebugTools(config)
        
        # Debug model state
        model_info = debug_tools.debug_model_state(self.model)
        
        # Check model info structure
        self.assertIn('model_training_mode', model_info)
        self.assertIn('total_parameters', model_info)
        self.assertIn('trainable_parameters', model_info)
        self.assertIn('non_trainable_parameters', model_info)
        self.assertIn('parameters_with_nan', model_info)
        self.assertIn('parameters_with_inf', model_info)
        
        # Check specific values
        self.assertTrue(model_info['model_training_mode'])
        self.assertGreater(model_info['total_parameters'], 0)
        self.assertEqual(model_info['parameters_with_nan'], 0)
        self.assertEqual(model_info['parameters_with_inf'], 0)
    
    def test_debug_summary(self):
        """Test debug summary functionality."""
        config = self.LoggingConfig(enable_pytorch_debugging=True)
        debug_tools = self.PyTorchDebugTools(config)
        
        # Generate some debug data
        debug_tools.debug_context['test_key'] = 'test_value'
        debug_tools.memory_tracker['test_memory'] = 1024
        
        # Get summary
        summary = debug_tools.get_debug_summary()
        
        # Check summary structure
        self.assertIn('anomaly_detection_enabled', summary)
        self.assertIn('profiler_active', summary)
        self.assertIn('gradient_history', summary)
        self.assertIn('debug_context', summary)
        self.assertIn('memory_tracker', summary)
        
        # Check specific values
        self.assertFalse(summary['anomaly_detection_enabled'])
        self.assertFalse(summary['profiler_active'])
        self.assertEqual(summary['debug_context']['test_key'], 'test_value')
        self.assertEqual(summary['memory_tracker']['test_memory'], 1024)
    
    def test_cleanup_functionality(self):
        """Test cleanup functionality."""
        config = self.LoggingConfig(enable_pytorch_debugging=True)
        debug_tools = self.PyTorchDebugTools(config)
        
        # Enable anomaly detection
        debug_tools.enable_anomaly_detection(True)
        self.assertTrue(debug_tools.anomaly_detection_enabled)
        
        # Cleanup
        debug_tools.cleanup()
        
        # Check that anomaly detection was disabled
        self.assertFalse(debug_tools.anomaly_detection_enabled)

class TestComprehensiveLoggerPyTorchDebugging(unittest.TestCase):
    """Test suite for ComprehensiveLogger PyTorch debugging integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        try:
            from comprehensive_logging import setup_logging, LoggingConfig
            self.setup_logging = setup_logging
            self.LoggingConfig = LoggingConfig
        except ImportError as e:
            self.skipTest(f"Could not import comprehensive_logging: {e}")
        
        # Create test model
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        
        # Create test data
        self.x = torch.randn(32, 10)
        self.y = torch.randn(32, 1)
        self.criterion = nn.MSELoss()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_logger_with_pytorch_debugging(self):
        """Test ComprehensiveLogger with PyTorch debugging enabled."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_pytorch_debugging=True,
            enable_gradient_debugging=True,
            enable_memory_debugging=True,
            enable_tensor_debugging=True
        )
        
        logger = self.setup_logging("test_pytorch_debug", **config.__dict__)
        
        try:
            # Test PyTorch debugging methods
            output = self.model(self.x)
            loss = self.criterion(output, self.y)
            loss.backward()
            
            # Debug gradients
            gradient_debug = logger.debug_model_gradients(self.model, loss)
            self.assertIsInstance(gradient_debug, dict)
            self.assertIn('total_grad_norm', gradient_debug)
            
            # Debug memory
            memory_debug = logger.debug_model_memory()
            self.assertIsInstance(memory_debug, dict)
            
            # Debug model state
            model_debug = logger.debug_model_state(self.model)
            self.assertIsInstance(model_debug, dict)
            self.assertIn('total_parameters', model_debug)
            
        finally:
            logger.cleanup()
    
    def test_training_step_with_debug(self):
        """Test training step logging with comprehensive debugging."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_pytorch_debugging=True,
            enable_gradient_debugging=True,
            enable_memory_debugging=True,
            enable_tensor_debugging=True
        )
        
        logger = self.setup_logging("test_training_debug", **config.__dict__)
        
        try:
            # Forward pass
            output = self.model(self.x)
            loss = self.criterion(output, self.y)
            loss.backward()
            
            # Log training step with debugging
            debug_info = logger.log_training_step_with_debug(
                epoch=0,
                step=0,
                loss=loss.item(),
                model=self.model,
                accuracy=0.8
            )
            
            # Check debug info structure
            self.assertIn('gradient_debug', debug_info)
            self.assertIn('memory_debug', debug_info)
            self.assertIn('model_debug', debug_info)
            
        finally:
            logger.cleanup()
    
    def test_context_managers(self):
        """Test PyTorch debugging context managers."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_pytorch_debugging=True,
            enable_gradient_debugging=True
        )
        
        logger = self.setup_logging("test_context_managers", **config.__dict__)
        
        try:
            # Test pytorch_debugging context manager
            with logger.pytorch_debugging("test_operation", enable_anomaly_detection=True):
                # Simulate operation
                test_tensor = torch.randn(5, 5, requires_grad=True)
                test_loss = test_tensor.sum()
                test_loss.backward()
            
            # Test gradient_debugging context manager
            with logger.gradient_debugging(self.model, "test_gradient_op"):
                # Simulate operation
                output = self.model(self.x[:5])
                loss = self.criterion(output, self.y[:5])
                loss.backward()
            
        finally:
            logger.cleanup()
    
    def test_logging_summary_with_pytorch_debug(self):
        """Test logging summary includes PyTorch debugging information."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_pytorch_debugging=True
        )
        
        logger = self.setup_logging("test_summary", **config.__dict__)
        
        try:
            # Generate some debug data
            logger.debug_model_memory()
            
            # Get summary
            summary = logger.get_logging_summary()
            
            # Check that PyTorch debugging info is included
            self.assertIn('pytorch_debug', summary)
            pytorch_debug = summary['pytorch_debug']
            self.assertIn('anomaly_detection_enabled', pytorch_debug)
            self.assertIn('profiler_active', pytorch_debug)
            self.assertIn('gradient_history', pytorch_debug)
            
        finally:
            logger.cleanup()

class TestPyTorchDebuggingIntegration(unittest.TestCase):
    """Test suite for PyTorch debugging integration with SEO system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        try:
            from comprehensive_logging import setup_logging, LoggingConfig
            self.setup_logging = setup_logging
            self.LoggingConfig = LoggingConfig
        except ImportError as e:
            self.skipTest(f"Could not import comprehensive_logging: {e}")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_seo_training_integration(self):
        """Test PyTorch debugging integration with SEO training simulation."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_pytorch_debugging=True,
            enable_gradient_debugging=True,
            enable_memory_debugging=True,
            enable_tensor_debugging=True
        )
        
        logger = self.setup_logging("test_seo_integration", **config.__dict__)
        
        try:
            # Simulate SEO training with debugging
            model = nn.Sequential(
                nn.Linear(100, 200),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(200, 100),
                nn.ReLU(),
                nn.Linear(100, 10)
            )
            
            # Create SEO-like data
            seo_features = torch.randn(64, 100)
            seo_labels = torch.randint(0, 10, (64,))
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            
            # Training loop with debugging
            for epoch in range(2):
                for step in range(3):
                    optimizer.zero_grad()
                    
                    # Forward pass
                    output = model(seo_features)
                    loss = criterion(output, seo_labels)
                    
                    # Backward pass
                    loss.backward()
                    
                    # Debug before optimization
                    gradient_debug = logger.debug_model_gradients(model, loss, epoch=epoch, step=step)
                    memory_debug = logger.debug_model_memory(epoch=epoch, step=step)
                    model_debug = logger.debug_model_state(model, epoch=epoch, step=step)
                    
                    # Optimizer step
                    optimizer.step()
                    
                    # Log with debugging
                    logger.log_training_step_with_debug(
                        epoch=epoch,
                        step=step,
                        loss=loss.item(),
                        model=model,
                        accuracy=0.8,
                        learning_rate=optimizer.param_groups[0]['lr']
                    )
                
                # Log epoch summary
                logger.log_epoch_summary(
                    epoch=epoch,
                    train_loss=0.5,
                    val_loss=0.6,
                    train_accuracy=0.8,
                    val_accuracy=0.75
                )
            
            # Get comprehensive summary
            summary = logger.get_logging_summary()
            
            # Verify PyTorch debugging info
            self.assertIn('pytorch_debug', summary)
            pytorch_debug = summary['pytorch_debug']
            self.assertIn('gradient_history', pytorch_debug)
            
            # Check training metrics
            training_metrics = summary['training_metrics']
            self.assertGreater(training_metrics['total_steps'], 0)
            
        finally:
            logger.cleanup()
    
    def test_error_handling_with_debugging(self):
        """Test error handling with PyTorch debugging enabled."""
        config = self.LoggingConfig(
            log_dir=self.log_dir,
            enable_pytorch_debugging=True,
            enable_gradient_debugging=True
        )
        
        logger = self.setup_logging("test_error_handling", **config.__dict__)
        
        try:
            # Simulate an error during training
            try:
                # Create problematic model
                model = nn.Sequential(
                    nn.Linear(10, 20),
                    nn.ReLU(),
                    nn.Linear(20, 1)
                )
                
                # Create data with NaN
                x = torch.randn(32, 10)
                x[0, 0] = float('nan')  # Introduce NaN
                y = torch.randn(32, 1)
                
                # This should trigger an error
                output = model(x)
                loss = nn.MSELoss()(output, y)
                loss.backward()
                
            except Exception as e:
                # Log error with debugging context
                logger.log_error(
                    error=e,
                    context={
                        "operation": "seo_training",
                        "model_state": logger.debug_model_state(model),
                        "memory_state": logger.debug_model_memory()
                    },
                    severity="ERROR"
                )
                
                # Verify error was logged
                summary = logger.get_logging_summary()
                self.assertGreater(summary['error_analysis']['total_errors'], 0)
            
        finally:
            logger.cleanup()

def run_performance_tests():
    """Run performance tests for PyTorch debugging tools."""
    print("\n=== PyTorch Debugging Performance Tests ===")
    
    test_dir = tempfile.mkdtemp()
    log_dir = Path(test_dir) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    try:
        from comprehensive_logging import setup_logging
        
        logger = setup_logging(
            "performance_test",
            log_dir=str(log_dir),
            enable_pytorch_debugging=True,
            enable_gradient_debugging=True,
            enable_memory_debugging=True,
            enable_tensor_debugging=True
        )
        
        # Create test model
        model = nn.Sequential(
            nn.Linear(100, 200),
            nn.ReLU(),
            nn.Linear(200, 100),
            nn.ReLU(),
            nn.Linear(100, 10)
        )
        
        # Performance test: High-volume debugging
        start_time = time.time()
        
        for i in range(100):
            # Create test data
            x = torch.randn(32, 100)
            y = torch.randint(0, 10, (32,))
            criterion = nn.CrossEntropyLoss()
            
            # Forward pass
            output = model(x)
            loss = criterion(output, y)
            
            # Backward pass
            loss.backward()
            
            # Debug operations
            logger.debug_model_gradients(model, loss)
            logger.debug_model_memory()
            logger.debug_model_state(model)
            
            # Zero gradients
            model.zero_grad()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Processed 100 debugging operations in {duration:.4f}s")
        print(f"Average: {100/duration:.0f} operations/second")
        
        # Check file sizes
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            total_size_kb = sum(f.stat().st_size for f in log_files) / 1024
            print(f"Total log file size: {total_size_kb:.1f} KB")
        
        logger.cleanup()
        
    except Exception as e:
        print(f"Performance test failed: {e}")
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    # Run unit tests
    print("Running PyTorch Debugging Tools Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestPyTorchDebugTools))
    test_suite.addTest(unittest.makeSuite(TestComprehensiveLoggerPyTorchDebugging))
    test_suite.addTest(unittest.makeSuite(TestPyTorchDebuggingIntegration))
    
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
        print("✅ All PyTorch debugging tests passed!")
    else:
        print("❌ Some PyTorch debugging tests failed!")
        
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
