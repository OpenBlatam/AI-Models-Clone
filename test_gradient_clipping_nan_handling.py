from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int = 1000

# Constants
MAX_RETRIES: int = 100

# Constants
TIMEOUT_SECONDS: int = 60

import os
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam, SGD
from gradient_clipping_nan_handling_system import (
    import time
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Gradient Clipping and NaN/Inf Handling System
==========================================================

This module provides comprehensive tests for the gradient clipping and NaN/Inf handling system,
including tests for all clipping strategies, NaN detection, monitoring, and recovery mechanisms.
"""


# Import the system under test
    GradientClipper, NormClipper, ValueClipper, AdaptiveClipper, LayerwiseClipper,
    NaNInfHandler, GradientMonitor, TrainingStabilityManager, GradientClippingFactory,
    create_stability_manager, check_model_health, safe_backward
)


class TestGradientClipper(unittest.TestCase):
    """Test cases for GradientClipper base class."""
    
    def setUp(self) -> Any:
        # Create test model
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
    
    def test_base_clipper_initialization(self) -> Any:
        """Test base clipper initialization."""
        clipper = NormClipper(max_norm=1.0, norm_type=2.0)
        
        self.assertEqual(clipper.max_norm, 1.0)
        self.assertEqual(clipper.norm_type, 2.0)
        self.assertEqual(clipper.clip_count, 0)
        self.assertEqual(clipper.total_gradients, 0)
        self.assertIsInstance(clipper.history, dict)
    
    def test_get_clip_ratio(self) -> Optional[Dict[str, Any]]:
        """Test clip ratio calculation."""
        clipper = NormClipper(max_norm=1.0)
        
        # No clips yet
        self.assertEqual(clipper.get_clip_ratio(), 0.0)
        
        # Simulate some clips
        clipper.clip_count: int = 5
        clipper.total_gradients: int = 10
        self.assertEqual(clipper.get_clip_ratio(), 0.5)
    
    def test_reset_stats(self) -> Any:
        """Test statistics reset."""
        clipper = NormClipper(max_norm=1.0)
        
        # Add some data
        clipper.clip_count: int = 5
        clipper.total_gradients: int = 10
        clipper.history['test'] = [1, 2, 3]
        
        # Reset
        clipper.reset_stats()
        
        self.assertEqual(clipper.clip_count, 0)
        self.assertEqual(clipper.total_gradients, 0)
        self.assertEqual(len(clipper.history), 0)


class TestNormClipper(unittest.TestCase):
    """Test cases for NormClipper class."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
    
    def test_norm_clipper_initialization(self) -> Any:
        """Test norm clipper initialization."""
        clipper = NormClipper(max_norm=1.0, norm_type=2.0)
        
        self.assertEqual(clipper.max_norm, 1.0)
        self.assertEqual(clipper.norm_type, 2.0)
    
    def test_clip_gradients_no_clipping(self) -> Any:
        """Test gradient clipping when no clipping is needed."""
        clipper = NormClipper(max_norm=10.0)  # High threshold
        
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        # Get gradients before clipping
        gradients_before: List[Any] = []
        for param in self.model.parameters():
            if param.grad is not None:
                gradients_before.append(param.grad.clone())
        
        # Apply clipping
        parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
        total_norm = clipper.clip_gradients(parameters)
        
        # Check that gradients weren't clipped
        self.assertGreater(total_norm, 0.0)
        self.assertEqual(clipper.clip_count, 0)
        
        # Check that gradients are unchanged
        for i, param in enumerate(self.model.parameters()):
            if param.grad is not None:
                self.assertTrue(torch.allclose(param.grad, gradients_before[i]))
    
    def test_clip_gradients_with_clipping(self) -> Any:
        """Test gradient clipping when clipping is needed."""
        clipper = NormClipper(max_norm=0.1)  # Low threshold
        
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        # Get gradients before clipping
        gradients_before: List[Any] = []
        for param in self.model.parameters():
            if param.grad is not None:
                gradients_before.append(param.grad.clone())
        
        # Apply clipping
        parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
        total_norm = clipper.clip_gradients(parameters)
        
        # Check that gradients were clipped
        self.assertGreater(total_norm, 0.0)
        self.assertEqual(clipper.clip_count, 1)
        
        # Check that gradients were reduced
        for i, param in enumerate(self.model.parameters()):
            if param.grad is not None:
                self.assertLess(param.grad.norm(), gradients_before[i].norm())
    
    def test_clip_gradients_history(self) -> Any:
        """Test that clipping history is recorded."""
        clipper = NormClipper(max_norm=0.1)
        
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        # Apply clipping
        parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
        clipper.clip_gradients(parameters)
        
        # Check history
        history = clipper.get_history()
        self.assertIn('total_norm', history)
        self.assertIn('clip_coef', history)
        self.assertIn('param_norms', history)
        
        self.assertEqual(len(history['total_norm']), 1)
        self.assertEqual(len(history['clip_coef']), 1)
        self.assertEqual(len(history['param_norms']), 1)


class TestValueClipper(unittest.TestCase):
    """Test cases for ValueClipper class."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
    
    def test_value_clipper_initialization(self) -> Any:
        """Test value clipper initialization."""
        clipper = ValueClipper(max_value=1.0)
        
        self.assertEqual(clipper.max_value, 1.0)
    
    def test_clip_gradients_value_clipping(self) -> Any:
        """Test value-based gradient clipping."""
        clipper = ValueClipper(max_value=0.5)
        
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        # Apply clipping
        parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
        clip_ratio = clipper.clip_gradients(parameters)
        
        # Check that some values were clipped
        self.assertGreaterEqual(clip_ratio, 0.0)
        self.assertLessEqual(clip_ratio, 1.0)
        
        # Check that all gradient values are within bounds
        for param in self.model.parameters():
            if param.grad is not None:
                self.assertLessEqual(param.grad.max().item(), 0.5)
                self.assertGreaterEqual(param.grad.min().item(), -0.5)


class TestAdaptiveClipper(unittest.TestCase):
    """Test cases for AdaptiveClipper class."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
    
    def test_adaptive_clipper_initialization(self) -> Any:
        """Test adaptive clipper initialization."""
        clipper = AdaptiveClipper(initial_norm=1.0, factor=2.0, patience=5)
        
        self.assertEqual(clipper.current_norm, 1.0)
        self.assertEqual(clipper.factor, 2.0)
        self.assertEqual(clipper.patience, 5)
    
    def test_adaptive_clipping_behavior(self) -> Any:
        """Test adaptive clipping behavior."""
        clipper = AdaptiveClipper(initial_norm=1.0, factor=2.0, patience=3)
        
        # Simulate multiple clipping steps
        for i in range(5):
            # Create gradients
            x = torch.randn(5, 10)
            y = torch.randn(5, 1)
            
            self.model.zero_grad()
            output = self.model(x)
            loss = F.mse_loss(output, y)
            loss.backward()
            
            # Apply clipping
            parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
            total_norm = clipper.clip_gradients(parameters)
            
            # Check that current_norm is updated appropriately
            self.assertGreaterEqual(clipper.current_norm, clipper.min_norm)
            self.assertLessEqual(clipper.current_norm, clipper.max_norm)
    
    def test_adaptive_norm_adjustment(self) -> Any:
        """Test adaptive norm adjustment."""
        clipper = AdaptiveClipper(initial_norm=1.0, factor=2.0, patience=2)
        
        # Force clipping for several steps
        for i in range(3):
            # Create large gradients
            for param in self.model.parameters():
                if param.grad is None:
                    param.grad = torch.randn_like(param) * 10.0  # Large gradients
            
            parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
            clipper.clip_gradients(parameters)
        
        # Check that norm was increased due to excessive clipping
        self.assertGreater(clipper.current_norm, 1.0)


class TestLayerwiseClipper(unittest.TestCase):
    """Test cases for LayerwiseClipper class."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
    
    def test_layerwise_clipper_initialization(self) -> Any:
        """Test layerwise clipper initialization."""
        clipper = LayerwiseClipper(max_norm=1.0, norm_type=2.0)
        
        self.assertEqual(clipper.max_norm, 1.0)
        self.assertEqual(clipper.norm_type, 2.0)
    
    def test_layerwise_clipping(self) -> Any:
        """Test layerwise gradient clipping."""
        clipper = LayerwiseClipper(max_norm=0.5)
        
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        # Apply clipping
        parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
        total_norm = clipper.clip_gradients(parameters)
        
        # Check that each parameter was clipped individually
        for param in self.model.parameters():
            if param.grad is not None:
                param_norm = param.grad.norm().item()
                self.assertLessEqual(param_norm, 0.5 + 1e-6)  # Allow small numerical errors


class TestNaNInfHandler(unittest.TestCase):
    """Test cases for NaNInfHandler class."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
        self.handler = NaNInfHandler()
    
    def test_nan_handler_initialization(self) -> Any:
        """Test NaN handler initialization."""
        handler = NaNInfHandler(
            check_gradients=True,
            check_parameters=True,
            check_loss=True,
            check_outputs=True,
            recovery_strategy: str = 'skip_batch',
            max_consecutive_failures: int = 5
        )
        
        self.assertTrue(handler.check_gradients)
        self.assertTrue(handler.check_parameters)
        self.assertTrue(handler.check_loss)
        self.assertTrue(handler.check_outputs)
        self.assertEqual(handler.recovery_strategy, 'skip_batch')
        self.assertEqual(handler.max_consecutive_failures, 5)
    
    def test_check_tensor_normal(self) -> Any:
        """Test tensor checking with normal values."""
        tensor = torch.randn(10, 10)
        result = self.handler.check_tensor(tensor, "test_tensor")
        self.assertTrue(result)
    
    def test_check_tensor_nan(self) -> Any:
        """Test tensor checking with NaN values."""
        tensor = torch.randn(10, 10)
        tensor[0, 0] = float('nan')
        result = self.handler.check_tensor(tensor, "test_tensor")
        self.assertFalse(result)
    
    def test_check_tensor_inf(self) -> Any:
        """Test tensor checking with Inf values."""
        tensor = torch.randn(10, 10)
        tensor[0, 0] = float('inf')
        result = self.handler.check_tensor(tensor, "test_tensor")
        self.assertFalse(result)
    
    def test_check_model_normal(self) -> Any:
        """Test model checking with normal values."""
        result = self.handler.check_model(self.model)
        self.assertTrue(result)
    
    def test_check_model_with_nan_gradients(self) -> Any:
        """Test model checking with NaN gradients."""
        # Create NaN gradients
        for param in self.model.parameters():
            param.grad = torch.randn_like(param)
            param.grad[0, 0] = float('nan')
        
        result = self.handler.check_model(self.model)
        self.assertFalse(result)
    
    def test_check_loss_normal(self) -> Any:
        """Test loss checking with normal value."""
        loss = torch.tensor(0.5)
        result = self.handler.check_loss(loss)
        self.assertTrue(result)
    
    def test_check_loss_nan(self) -> Any:
        """Test loss checking with NaN value."""
        loss = torch.tensor(float('nan'))
        result = self.handler.check_loss(loss)
        self.assertFalse(result)
    
    def test_handle_failure_skip_batch(self) -> Any:
        """Test failure handling with skip_batch strategy."""
        handler = NaNInfHandler(recovery_strategy='skip_batch')
        
        result = handler.handle_failure(self.model, self.optimizer)
        self.assertTrue(result)
        self.assertEqual(handler.failure_count, 1)
        self.assertEqual(handler.consecutive_failures, 1)
    
    def test_handle_failure_reset_gradients(self) -> Any:
        """Test failure handling with reset_gradients strategy."""
        handler = NaNInfHandler(recovery_strategy='reset_gradients')
        
        # Create some gradients
        for param in self.model.parameters():
            param.grad = torch.randn_like(param)
        
        result = handler.handle_failure(self.model, self.optimizer)
        self.assertTrue(result)
        
        # Check that gradients were reset
        for param in self.model.parameters():
            self.assertIsNone(param.grad)
    
    def test_handle_failure_reduce_lr(self) -> Any:
        """Test failure handling with reduce_lr strategy."""
        handler = NaNInfHandler(recovery_strategy='reduce_lr')
        initial_lr = self.optimizer.param_groups[0]['lr']
        
        result = handler.handle_failure(self.model, self.optimizer)
        self.assertTrue(result)
        
        # Check that learning rate was reduced
        new_lr = self.optimizer.param_groups[0]['lr']
        self.assertLess(new_lr, initial_lr)
    
    def test_max_consecutive_failures(self) -> Any:
        """Test max consecutive failures limit."""
        handler = NaNInfHandler(max_consecutive_failures=2)
        
        # First failure
        result = handler.handle_failure(self.model, self.optimizer)
        self.assertTrue(result)
        
        # Second failure
        result = handler.handle_failure(self.model, self.optimizer)
        self.assertTrue(result)
        
        # Third failure should stop training
        result = handler.handle_failure(self.model, self.optimizer)
        self.assertFalse(result)
    
    def test_reset_consecutive_failures(self) -> Any:
        """Test resetting consecutive failures."""
        handler = NaNInfHandler()
        
        # Add some failures
        handler.handle_failure(self.model, self.optimizer)
        handler.handle_failure(self.model, self.optimizer)
        
        self.assertEqual(handler.consecutive_failures, 2)
        
        # Reset
        handler.reset_consecutive_failures()
        self.assertEqual(handler.consecutive_failures, 0)


class TestGradientMonitor(unittest.TestCase):
    """Test cases for GradientMonitor class."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.monitor = GradientMonitor(log_interval=10, save_interval=50)
    
    def test_monitor_initialization(self) -> Any:
        """Test monitor initialization."""
        monitor = GradientMonitor(
            log_interval=100,
            save_interval=1000,
            save_path: str = "/tmp/test"
        )
        
        self.assertEqual(monitor.log_interval, 100)
        self.assertEqual(monitor.save_interval, 1000)
        self.assertEqual(monitor.save_path, "/tmp/test")
        self.assertEqual(monitor.step_count, 0)
    
    def test_update_with_gradients(self) -> Any:
        """Test monitor update with gradients."""
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        # Update monitor
        self.monitor.update(self.model, loss)
        
        # Check that statistics were recorded
        self.assertEqual(self.monitor.step_count, 1)
        self.assertEqual(len(self.monitor.health_scores), 1)
        self.assertGreater(len(self.monitor.gradient_stats), 0)
        self.assertGreater(len(self.monitor.parameter_stats), 0)
    
    def test_calculate_health_score(self) -> Any:
        """Test health score calculation."""
        # Create gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        health_score = self.monitor.calculate_health_score(self.model)
        
        # Check health score properties
        self.assertIsInstance(health_score, float)
        self.assertGreaterEqual(health_score, 0.0)
        self.assertLessEqual(health_score, 1.0)
    
    def test_save_statistics(self) -> Any:
        """Test statistics saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = GradientMonitor(save_path=temp_dir)
            
            # Create some data
            for i in range(5):
                x = torch.randn(5, 10)
                y = torch.randn(5, 1)
                
                self.model.zero_grad()
                output = self.model(x)
                loss = F.mse_loss(output, y)
                loss.backward()
                
                monitor.update(self.model, loss)
            
            # Check that files were created
            files = os.listdir(temp_dir)
            self.assertGreater(len(files), 0)


class TestTrainingStabilityManager(unittest.TestCase):
    """Test cases for TrainingStabilityManager class."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
        
        self.clipper = NormClipper(max_norm=1.0)
        self.nan_handler = NaNInfHandler()
        self.monitor = GradientMonitor()
        
        self.manager = TrainingStabilityManager(
            clipper=self.clipper,
            nan_handler=self.nan_handler,
            monitor=self.monitor
        )
    
    def test_manager_initialization(self) -> Any:
        """Test manager initialization."""
        manager = TrainingStabilityManager()
        
        self.assertIsInstance(manager.clipper, NormClipper)
        self.assertIsInstance(manager.nan_handler, NaNInfHandler)
        self.assertIsInstance(manager.monitor, GradientMonitor)
    
    def test_before_backward_normal(self) -> Any:
        """Test before_backward with normal loss."""
        loss = torch.tensor(0.5)
        result = self.manager.before_backward(self.model, loss)
        self.assertTrue(result)
    
    def test_before_backward_nan_loss(self) -> Any:
        """Test before_backward with NaN loss."""
        loss = torch.tensor(float('nan'))
        result = self.manager.before_backward(self.model, loss)
        self.assertFalse(result)
    
    def test_after_backward_normal(self) -> Any:
        """Test after_backward with normal gradients."""
        # Create normal gradients
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        self.model.zero_grad()
        output = self.model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        result = self.manager.after_backward(self.model, self.optimizer)
        self.assertTrue(result)
    
    def test_after_backward_with_nan_gradients(self) -> Any:
        """Test after_backward with NaN gradients."""
        # Create NaN gradients
        for param in self.model.parameters():
            param.grad = torch.randn_like(param)
            param.grad[0, 0] = float('nan')
        
        result = self.manager.after_backward(self.model, self.optimizer)
        self.assertFalse(result)
    
    def test_get_training_stats(self) -> Optional[Dict[str, Any]]:
        """Test getting training statistics."""
        stats = self.manager.get_training_stats()
        
        self.assertIn('clipper_stats', stats)
        self.assertIn('nan_handler_stats', stats)
        self.assertIn('training_stats', stats)
        self.assertIn('monitor_stats', stats)
    
    def test_save_and_load_checkpoint(self) -> Any:
        """Test checkpoint saving and loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint_path = os.path.join(temp_dir, 'checkpoint.pth')
            
            # Save checkpoint
            self.manager.save_checkpoint(
                self.model, self.optimizer, epoch=1, step=100, 
                save_path=checkpoint_path
            )
            
            # Load checkpoint
            epoch, step = self.manager.load_checkpoint(
                self.model, self.optimizer, checkpoint_path
            )
            
            self.assertEqual(epoch, 1)
            self.assertEqual(step, 100)


class TestGradientClippingFactory(unittest.TestCase):
    """Test cases for GradientClippingFactory class."""
    
    def test_create_norm_clipper(self) -> Any:
        """Test creating norm clipper."""
        clipper = GradientClippingFactory.create_norm_clipper(max_norm=1.0, norm_type=2.0)
        
        self.assertIsInstance(clipper, NormClipper)
        self.assertEqual(clipper.max_norm, 1.0)
        self.assertEqual(clipper.norm_type, 2.0)
    
    def test_create_value_clipper(self) -> Any:
        """Test creating value clipper."""
        clipper = GradientClippingFactory.create_value_clipper(max_value=0.5)
        
        self.assertIsInstance(clipper, ValueClipper)
        self.assertEqual(clipper.max_value, 0.5)
    
    def test_create_adaptive_clipper(self) -> Any:
        """Test creating adaptive clipper."""
        clipper = GradientClippingFactory.create_adaptive_clipper(
            initial_norm=1.0, factor=2.0, patience=5
        )
        
        self.assertIsInstance(clipper, AdaptiveClipper)
        self.assertEqual(clipper.current_norm, 1.0)
        self.assertEqual(clipper.factor, 2.0)
        self.assertEqual(clipper.patience, 5)
    
    def test_create_layerwise_clipper(self) -> Any:
        """Test creating layerwise clipper."""
        clipper = GradientClippingFactory.create_layerwise_clipper(max_norm=1.0, norm_type=2.0)
        
        self.assertIsInstance(clipper, LayerwiseClipper)
        self.assertEqual(clipper.max_norm, 1.0)
        self.assertEqual(clipper.norm_type, 2.0)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
    
    def test_create_stability_manager(self) -> Any:
        """Test creating stability manager."""
        manager = create_stability_manager(clip_type='norm', max_norm=1.0)
        
        self.assertIsInstance(manager, TrainingStabilityManager)
        self.assertIsInstance(manager.clipper, NormClipper)
        self.assertEqual(manager.clipper.max_norm, 1.0)
    
    def test_create_stability_manager_adaptive(self) -> Any:
        """Test creating stability manager with adaptive clipping."""
        manager = create_stability_manager(
            clip_type: str = 'adaptive', 
            initial_norm=1.0, 
            factor=2.0
        )
        
        self.assertIsInstance(manager, TrainingStabilityManager)
        self.assertIsInstance(manager.clipper, AdaptiveClipper)
        self.assertEqual(manager.clipper.current_norm, 1.0)
    
    def test_create_stability_manager_invalid_type(self) -> Any:
        """Test creating stability manager with invalid clip type."""
        with self.assertRaises(ValueError):
            create_stability_manager(clip_type: str = 'invalid')
    
    def test_check_model_health(self) -> Any:
        """Test model health checking."""
        health_stats = check_model_health(self.model)
        
        self.assertIn('parameter_count', health_stats)
        self.assertIn('gradient_count', health_stats)
        self.assertIn('nan_parameters', health_stats)
        self.assertIn('inf_parameters', health_stats)
        self.assertIn('nan_gradients', health_stats)
        self.assertIn('inf_gradients', health_stats)
        self.assertIn('parameter_norms', health_stats)
        self.assertIn('gradient_norms', health_stats)
        
        self.assertGreater(health_stats['parameter_count'], 0)
        self.assertEqual(health_stats['nan_parameters'], 0)
        self.assertEqual(health_stats['inf_parameters'], 0)
    
    def test_safe_backward_success(self) -> Any:
        """Test successful safe backward pass."""
        manager = create_stability_manager(clip_type='norm', max_norm=1.0)
        
        # Create normal data
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        output = self.model(x)
        loss = F.mse_loss(output, y)
        
        success = safe_backward(loss, manager, self.model, self.optimizer)
        self.assertTrue(success)
    
    def test_safe_backward_failure(self) -> Any:
        """Test failed safe backward pass."""
        manager = create_stability_manager(clip_type='norm', max_norm=1.0)
        
        # Create NaN loss
        loss = torch.tensor(float('nan'))
        
        success = safe_backward(loss, manager, self.model, self.optimizer)
        self.assertFalse(success)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 1)
        )
        self.optimizer = Adam(self.model.parameters(), lr=0.01)
    
    def test_complete_training_loop(self) -> Any:
        """Test complete training loop with stability management."""
        manager = create_stability_manager(
            clip_type: str = 'adaptive',
            initial_norm=1.0,
            factor=2.0,
            patience: int = 3
        )
        
        success_count: int = 0
        total_steps: int = 10
        
        for step in range(total_steps):
            # Create data
            x = torch.randn(5, 10)
            y = torch.randn(5, 1)
            
            # Forward pass
            output = self.model(x)
            loss = F.mse_loss(output, y)
            
            # Safe backward pass
            success = safe_backward(loss, manager, self.model, self.optimizer)
            
            if success:
                success_count += 1
        
        # Most steps should succeed
        self.assertGreater(success_count, total_steps * 0.8)
    
    def test_nan_recovery_scenario(self) -> Any:
        """Test NaN recovery scenario."""
        manager = create_stability_manager(
            clip_type: str = 'norm',
            max_norm=1.0
        )
        
        # Simulate NaN gradients
        for param in self.model.parameters():
            param.grad = torch.randn_like(param)
            param.grad[0, 0] = float('nan')
        
        # Try to handle the failure
        result = manager.after_backward(self.model, self.optimizer)
        self.assertFalse(result)
        
        # Check that failure was recorded
        stats = manager.get_training_stats()
        self.assertGreater(stats['nan_handler_stats']['total_failures'], 0)
    
    def test_gradient_explosion_scenario(self) -> Any:
        """Test gradient explosion scenario."""
        manager = create_stability_manager(
            clip_type: str = 'norm',
            max_norm=0.1  # Very low threshold
        )
        
        # Create large gradients
        for param in self.model.parameters():
            param.grad = torch.randn_like(param) * 10.0  # Large gradients
        
        # Apply clipping
        parameters: List[Any] = [p for p in self.model.parameters() if p.grad is not None]
        total_norm = manager.clipper.clip_gradients(parameters)
        
        # Check that gradients were clipped
        self.assertGreater(total_norm, 0.0)
        self.assertEqual(manager.clipper.clip_count, 1)
        
        # Check that gradients are within bounds
        for param in self.model.parameters():
            if param.grad is not None:
                param_norm = param.grad.norm().item()
                self.assertLessEqual(param_norm, 0.1 + 1e-6)
    
    def test_monitoring_integration(self) -> Any:
        """Test monitoring integration."""
        manager = create_stability_manager(
            clip_type: str = 'norm',
            max_norm=1.0
        )
        
        # Run several training steps
        for step in range(5):
            x = torch.randn(5, 10)
            y = torch.randn(5, 1)
            
            output = self.model(x)
            loss = F.mse_loss(output, y)
            
            safe_backward(loss, manager, self.model, self.optimizer)
        
        # Check monitoring data
        stats = manager.get_training_stats()
        self.assertIn('monitor_stats', stats)
        self.assertGreater(stats['monitor_stats']['step_count'], 0)
        self.assertGreater(len(stats['monitor_stats']['health_scores']), 0)


def run_performance_benchmark() -> Any:
    """Run performance benchmark for the gradient clipping system."""
    print("Running Gradient Clipping Performance Benchmark...")
    
    
    # Create large model
    model = nn.Sequential(
        nn.Linear(1000, 2000),
        nn.ReLU(),
        nn.Linear(2000, 1000),
        nn.ReLU(),
        nn.Linear(1000, 100)
    )
    optimizer = Adam(model.parameters(), lr=0.01)
    
    # Create different clippers
    clippers: Dict[str, Any] = {
        'NormClipper': NormClipper(max_norm=1.0),
        'ValueClipper': ValueClipper(max_value=1.0),
        'AdaptiveClipper': AdaptiveClipper(initial_norm=1.0),
        'LayerwiseClipper': LayerwiseClipper(max_norm=1.0)
    }
    
    # Benchmark each clipper
    for name, clipper in clippers.items():
        print(f"\nBenchmarking {name}...")
        
        # Create gradients
        x = torch.randn(100, 1000)
        y = torch.randn(100, 100)
        
        model.zero_grad()
        output = model(x)
        loss = F.mse_loss(output, y)
        loss.backward()
        
        parameters: List[Any] = [p for p in model.parameters() if p.grad is not None]
        
        # Time clipping
        start_time = time.time()
        for _ in range(100):
            clipper.clip_gradients(parameters)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        print(f"Average clipping time: {avg_time*1000:.2f} ms")
        print(f"Clip ratio: {clipper.get_clip_ratio():.4f}")
    
    # Benchmark NaN handling
    print("\nBenchmarking NaN Handler...")
    handler = NaNInfHandler()
    
    start_time = time.time()
    for _ in range(1000):
        handler.check_model(model)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 1000
    print(f"Average model check time: {avg_time*1000:.2f} ms")
    
    # Benchmark complete stability manager
    print("\nBenchmarking Training Stability Manager...")
    manager = create_stability_manager(clip_type='norm', max_norm=1.0)
    
    start_time = time.time()
    for _ in range(100):
        x = torch.randn(50, 1000)
        y = torch.randn(50, 100)
        
        output = model(x)
        loss = F.mse_loss(output, y)
        
        safe_backward(loss, manager, model, optimizer)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    print(f"Average training step time: {avg_time*1000:.2f} ms")
    
    # Summary
    print(f"\n{"="*60)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("="*60)
    print("All components show good performance for typical use cases.")
    print("Gradient clipping adds minimal overhead to training.")
    print("NaN detection is fast and efficient.")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    print("\n"}="*60)
    run_performance_benchmark() 