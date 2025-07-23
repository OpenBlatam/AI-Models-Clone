#!/usr/bin/env python3
"""
Test Suite for PyTorch Debugging Tools

Demonstrates comprehensive usage of PyTorch's built-in debugging tools including
autograd.detect_anomaly() and other debugging utilities.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
import time
import json
from typing import Dict, List, Optional, Tuple
import traceback
import os
from pathlib import Path

# Import PyTorch debugging tools
try:
    from pytorch_debugging_tools import PyTorchDebugger, DebugConfig, DebugTrainer
    DEBUGGING_AVAILABLE = True
except ImportError:
    DEBUGGING_AVAILABLE = False

# Import optimization demo components
try:
    from optimization_demo import OptimizedNeuralNetwork, ModelConfig
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestPyTorchDebugging:
    """Comprehensive test suite for PyTorch debugging tools."""
    
    def __init__(self):
        self.test_results = {}
        self.debugger = None
        
        if DEBUGGING_AVAILABLE:
            self.debugger = PyTorchDebugger()
    
    def test_anomaly_detection(self):
        """Test autograd anomaly detection."""
        logger.info("=== Testing Anomaly Detection ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Create a model that might cause anomalies
            model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 1)
            )
            
            # Create data
            data = torch.randn(4, 10)
            targets = torch.randn(4, 1)
            
            # Test normal training without anomalies
            with self.debugger.anomaly_detection():
                model.train()
                optimizer = torch.optim.Adam(model.parameters())
                criterion = nn.MSELoss()
                
                # Forward pass
                outputs = model(data)
                loss = criterion(outputs, targets)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            logger.info("✅ Anomaly detection test (normal case) successful")
            
            # Test with potential anomaly (NaN in data)
            try:
                with self.debugger.anomaly_detection():
                    # Create data with NaN
                    data_with_nan = data.clone()
                    data_with_nan[0, 0] = float('nan')
                    
                    outputs = model(data_with_nan)
                    loss = criterion(outputs, targets)
                    loss.backward()
                
                logger.warning("⚠️ Expected anomaly not detected")
                return False
                
            except Exception as e:
                logger.info(f"✅ Anomaly detection caught issue: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection test failed: {e}")
            return False
    
    def test_gradient_checking(self):
        """Test gradient checking functionality."""
        logger.info("=== Testing Gradient Checking ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Create model
            model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 1)
            )
            
            # Create data
            data = torch.randn(4, 10)
            targets = torch.randn(4, 1)
            
            # Test gradient checking
            with self.debugger.grad_check(model):
                model.train()
                optimizer = torch.optim.Adam(model.parameters())
                criterion = nn.MSELoss()
                
                outputs = model(data)
                loss = criterion(outputs, targets)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            logger.info("✅ Gradient checking test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Gradient checking test failed: {e}")
            return False
    
    def test_memory_tracking(self):
        """Test memory tracking functionality."""
        logger.info("=== Testing Memory Tracking ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Create model
            model = nn.Sequential(
                nn.Linear(1000, 500),
                nn.ReLU(),
                nn.Linear(500, 100)
            )
            
            # Test memory tracking
            with self.debugger.memory_tracking():
                # Create large tensors
                data = torch.randn(100, 1000)
                targets = torch.randn(100, 100)
                
                # Forward pass
                outputs = model(data)
                loss = F.mse_loss(outputs, targets)
                
                # Backward pass
                loss.backward()
            
            # Check if memory snapshots were created
            assert len(self.debugger.memory_snapshots) > 0
            logger.info("✅ Memory tracking test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Memory tracking test failed: {e}")
            return False
    
    def test_profiling(self):
        """Test PyTorch profiling functionality."""
        logger.info("=== Testing Profiling ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Create model
            model = nn.Sequential(
                nn.Linear(100, 50),
                nn.ReLU(),
                nn.Linear(50, 10)
            )
            
            # Test profiling
            with self.debugger.profiling():
                data = torch.randn(32, 100)
                targets = torch.randint(0, 10, (32,))
                
                model.train()
                optimizer = torch.optim.Adam(model.parameters())
                criterion = nn.CrossEntropyLoss()
                
                for _ in range(10):  # Multiple iterations for profiling
                    outputs = model(data)
                    loss = criterion(outputs, targets)
                    
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
            
            # Check if profiling data was collected
            assert len(self.debugger.profiling_data) > 0
            logger.info("✅ Profiling test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Profiling test failed: {e}")
            return False
    
    def test_tensor_debugging(self):
        """Test tensor debugging functionality."""
        logger.info("=== Testing Tensor Debugging ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Test normal tensor
            normal_tensor = torch.randn(10, 5)
            self.debugger.debug_tensor(normal_tensor, "normal_tensor")
            
            # Test tensor with NaN
            nan_tensor = torch.randn(10, 5)
            nan_tensor[0, 0] = float('nan')
            self.debugger.debug_tensor(nan_tensor, "nan_tensor")
            
            # Test tensor with Inf
            inf_tensor = torch.randn(10, 5)
            inf_tensor[0, 0] = float('inf')
            self.debugger.debug_tensor(inf_tensor, "inf_tensor")
            
            # Test large tensor
            large_tensor = torch.randn(10, 5) * 1e8
            self.debugger.debug_tensor(large_tensor, "large_tensor")
            
            logger.info("✅ Tensor debugging test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Tensor debugging test failed: {e}")
            return False
    
    def test_model_debugging(self):
        """Test model debugging functionality."""
        logger.info("=== Testing Model Debugging ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Create model
            model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 1)
            )
            
            # Debug model
            self.debugger.debug_model(model)
            
            # Test with gradients
            data = torch.randn(4, 10)
            targets = torch.randn(4, 1)
            
            model.train()
            optimizer = torch.optim.Adam(model.parameters())
            criterion = nn.MSELoss()
            
            outputs = model(data)
            loss = criterion(outputs, targets)
            loss.backward()
            
            # Debug gradients
            self.debugger.debug_gradients(model)
            
            logger.info("✅ Model debugging test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Model debugging test failed: {e}")
            return False
    
    def test_common_issues_detection(self):
        """Test detection of common training issues."""
        logger.info("=== Testing Common Issues Detection ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Create model
            model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 1)
            )
            
            # Test normal case
            data = torch.randn(4, 10)
            targets = torch.randn(4, 1)
            
            model.train()
            optimizer = torch.optim.Adam(model.parameters())
            criterion = nn.MSELoss()
            
            outputs = model(data)
            loss = criterion(outputs, targets)
            
            # Check for issues
            issues = self.debugger.check_for_common_issues(model, loss)
            logger.info(f"Normal case issues: {issues}")
            
            # Test with NaN loss
            nan_loss = torch.tensor(float('nan'))
            issues = self.debugger.check_for_common_issues(model, nan_loss)
            logger.info(f"NaN loss issues: {issues}")
            
            # Test with Inf loss
            inf_loss = torch.tensor(float('inf'))
            issues = self.debugger.check_for_common_issues(model, inf_loss)
            logger.info(f"Inf loss issues: {issues}")
            
            logger.info("✅ Common issues detection test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Common issues detection test failed: {e}")
            return False
    
    def test_debug_trainer(self):
        """Test DebugTrainer integration."""
        logger.info("=== Testing DebugTrainer ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Create model
            model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 1)
            )
            
            # Create debug trainer
            debug_trainer = DebugTrainer(model, self.debugger)
            
            # Create data
            data = torch.randn(4, 10)
            targets = torch.randn(4, 1)
            
            # Training components
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters())
            
            # Training step with debugging
            result = debug_trainer.training_step(data, targets, criterion, optimizer)
            
            logger.info(f"Training step result: {result}")
            logger.info("✅ DebugTrainer test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ DebugTrainer test failed: {e}")
            return False
    
    def test_integration_with_optimization_demo(self):
        """Test integration with optimization demo."""
        logger.info("=== Testing Integration with Optimization Demo ===")
        
        if not DEBUGGING_AVAILABLE or not OPTIMIZATION_AVAILABLE:
            logger.warning("Required systems not available")
            return False
        
        try:
            # Create configuration
            config = ModelConfig(batch_size=4, num_epochs=2)
            
            # Create model
            model = OptimizedNeuralNetwork(config)
            
            # Create debugger with specific config
            debug_config = DebugConfig(
                enable_anomaly_detection=True,
                enable_grad_check=True,
                enable_memory_tracking=True,
                enable_profiling=True,
                enable_tensor_debugging=True
            )
            debugger = PyTorchDebugger(debug_config)
            
            # Create debug trainer
            debug_trainer = DebugTrainer(model, debugger)
            
            # Create dummy dataset
            data_tensor = torch.randn(20, config.input_size)
            target_tensor = torch.randint(0, config.output_size, (20,))
            
            # Training components
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.Adam(model.parameters())
            
            # Training step with debugging
            for step in range(3):
                result = debug_trainer.training_step(data_tensor, target_tensor, criterion, optimizer)
                logger.info(f"Step {step + 1}: Loss = {result['loss']:.4f}")
                
                if result.get('issues'):
                    logger.warning(f"Issues: {result['issues']}")
            
            # Debug model state
            debug_trainer.debug_model_state()
            
            logger.info("✅ Integration test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            return False
    
    def test_debug_configuration(self):
        """Test different debug configurations."""
        logger.info("=== Testing Debug Configuration ===")
        
        if not DEBUGGING_AVAILABLE:
            logger.warning("PyTorch debugging tools not available")
            return False
        
        try:
            # Test different configurations
            configs = [
                DebugConfig(enable_anomaly_detection=True, enable_grad_check=False),
                DebugConfig(enable_anomaly_detection=False, enable_grad_check=True),
                DebugConfig(enable_memory_tracking=True, enable_profiling=False),
                DebugConfig(enable_tensor_debugging=True, enable_profiling=True)
            ]
            
            for i, config in enumerate(configs):
                logger.info(f"Testing config {i + 1}: {config}")
                debugger = PyTorchDebugger(config)
                
                # Test basic functionality
                model = nn.Linear(10, 1)
                data = torch.randn(4, 10)
                targets = torch.randn(4, 1)
                
                with debugger.anomaly_detection():
                    with debugger.grad_check(model):
                        with debugger.memory_tracking():
                            model.train()
                            optimizer = torch.optim.Adam(model.parameters())
                            criterion = nn.MSELoss()
                            
                            outputs = model(data)
                            loss = criterion(outputs, targets)
                            
                            optimizer.zero_grad()
                            loss.backward()
                            optimizer.step()
            
            logger.info("✅ Debug configuration test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Debug configuration test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all PyTorch debugging tests."""
        logger.info("Starting comprehensive PyTorch debugging tests")
        
        tests = [
            ("Anomaly Detection", self.test_anomaly_detection),
            ("Gradient Checking", self.test_gradient_checking),
            ("Memory Tracking", self.test_memory_tracking),
            ("Profiling", self.test_profiling),
            ("Tensor Debugging", self.test_tensor_debugging),
            ("Model Debugging", self.test_model_debugging),
            ("Common Issues Detection", self.test_common_issues_detection),
            ("DebugTrainer", self.test_debug_trainer),
            ("Integration Test", self.test_integration_with_optimization_demo),
            ("Debug Configuration", self.test_debug_configuration)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Running: {test_name}")
                logger.info(f"{'='*60}")
                
                result = test_func()
                results[test_name] = result
                
                if result:
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                results[test_name] = False
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("TEST SUMMARY")
        logger.info(f"{'='*60}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All PyTorch debugging tests passed!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed")
        
        return results

def main():
    """Main test function."""
    logger.info("=== PyTorch Debugging Tools Test Suite ===")
    
    if not DEBUGGING_AVAILABLE:
        logger.error("PyTorch debugging tools not available. Please install required dependencies.")
        return
    
    # Create test suite
    test_suite = TestPyTorchDebugging()
    
    # Run all tests
    results = test_suite.run_all_tests()
    
    # Print final summary
    logger.info(f"\n{'='*60}")
    logger.info("FINAL SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    logger.info(f"Tests Passed: {passed}/{total}")
    logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        logger.info("🎉 All PyTorch debugging tests completed successfully!")
    else:
        logger.warning(f"⚠️ {total - passed} tests failed. Check logs for details.")
    
    logger.info("=== Test Suite Completed ===")

if __name__ == "__main__":
    main() 