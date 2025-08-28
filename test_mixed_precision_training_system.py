from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int = 100

import unittest
import tempfile
import shutil
import os
import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from mixed_precision_training_system import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Mixed Precision Training System
=============================================

Comprehensive tests for the mixed precision training system covering:
- Mixed precision configuration and setup
- AMP training workflows
- Gradient scaling and monitoring
- Performance profiling
- Precision policies
- Memory management
- Training stability
"""


# Add the current directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    MixedPrecisionConfig,
    AMPMonitor,
    CustomGradScaler,
    MixedPrecisionTrainer,
    PrecisionPolicy,
    DefaultPrecisionPolicy,
    ConservativePrecisionPolicy,
    AggressivePrecisionPolicy,
    create_mixed_precision_trainer,
    setup_mixed_precision_training,
    benchmark_mixed_precision
)


class TestMixedPrecisionConfig(unittest.TestCase):
    """Test MixedPrecisionConfig dataclass."""
    
    def test_default_config(self) -> Any:
        """Test default configuration values."""
        config = MixedPrecisionConfig()
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.dtype, torch.float16)
        self.assertEqual(config.device_type, "cuda")
        self.assertEqual(config.init_scale, 2.0**16)
        self.assertEqual(config.growth_factor, 2.0)
        self.assertEqual(config.backoff_factor, 0.5)
        self.assertTrue(config.enabled_loss_scaling)
        self.assertTrue(config.clip_grad_norm)
        self.assertTrue(config.monitor_memory_usage)
        self.assertTrue(config.log_amp_stats)
    
    def test_custom_config(self) -> Any:
        """Test custom configuration values."""
        config = MixedPrecisionConfig(
            enabled=False,
            dtype=torch.bfloat16,
            init_scale=2.0**15,
            max_grad_norm=2.0,
            use_fp16_optimizer=True,
            use_fp16_ema: bool = True
        )
        
        self.assertFalse(config.enabled)
        self.assertEqual(config.dtype, torch.bfloat16)
        self.assertEqual(config.init_scale, 2.0**15)
        self.assertEqual(config.max_grad_norm, 2.0)
        self.assertTrue(config.use_fp16_optimizer)
        self.assertTrue(config.use_fp16_ema)


class TestAMPMonitor(unittest.TestCase):
    """Test AMPMonitor functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = MixedPrecisionConfig(
            output_dir=self.temp_dir,
            experiment_name: str = "test_amp_monitor"
        )
        self.monitor = AMPMonitor(self.config)
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self) -> Any:
        """Test monitor initialization."""
        self.assertIsNotNone(self.monitor.config)
        self.assertIsNotNone(self.monitor.logger)
        self.assertEqual(len(self.monitor.scaling_history), 0)
        self.assertEqual(len(self.monitor.performance_history), 0)
        self.assertEqual(len(self.monitor.memory_history), 0)
    
    def test_log_scaling_event(self) -> Any:
        """Test scaling event logging."""
        self.monitor.log_scaling_event(10, 2.0**16, "scale_increase")
        
        self.assertEqual(len(self.monitor.scaling_history), 1)
        self.assertEqual(self.monitor.scaling_history[0]['step'], 10)
        self.assertEqual(self.monitor.scaling_history[0]['scale'], 2.0**16)
        self.assertEqual(self.monitor.scaling_history[0]['event_type'], "scale_increase")
    
    def test_log_performance_stats(self) -> Any:
        """Test performance statistics logging."""
        self.monitor.log_performance_stats(
            step=10,
            forward_time=0.1,
            backward_time=0.2,
            total_time=0.3,
            loss=0.5,
            scale=2.0**16
        )
        
        self.assertEqual(len(self.monitor.performance_history), 1)
        performance = self.monitor.performance_history[0]
        self.assertEqual(performance['step'], 10)
        self.assertEqual(performance['forward_time'], 0.1)
        self.assertEqual(performance['backward_time'], 0.2)
        self.assertEqual(performance['total_time'], 0.3)
        self.assertEqual(performance['loss'], 0.5)
        self.assertEqual(performance['scale'], 2.0**16)
    
    def test_log_memory_usage(self) -> Any:
        """Test memory usage logging."""
        self.monitor.log_memory_usage(10, 4.5, 6.0)
        
        self.assertEqual(len(self.monitor.memory_history), 1)
        memory = self.monitor.memory_history[0]
        self.assertEqual(memory['step'], 10)
        self.assertEqual(memory['memory_allocated'], 4.5)
        self.assertEqual(memory['memory_reserved'], 6.0)
    
    def test_get_amp_summary(self) -> Optional[Dict[str, Any]]:
        """Test AMP summary generation."""
        # Add some test data
        self.monitor.log_scaling_event(1, 2.0**16, "step")
        self.monitor.log_performance_stats(1, 0.1, 0.2, 0.3, 0.5, 2.0**16)
        self.monitor.log_memory_usage(1, 4.5, 6.0)
        
        summary = self.monitor.get_amp_summary()
        
        self.assertIn('total_steps', summary)
        self.assertIn('scaling_events', summary)
        self.assertIn('memory_events', summary)
        self.assertIn('performance_stats', summary)
        self.assertIn('scaling_stats', summary)
        self.assertIn('memory_stats', summary)
        
        self.assertEqual(summary['total_steps'], 1)
        self.assertEqual(summary['scaling_events'], 1)
        self.assertEqual(summary['memory_events'], 1)
    
    def test_save_amp_logs(self) -> Any:
        """Test AMP logs saving."""
        # Add some test data
        self.monitor.log_scaling_event(1, 2.0**16, "step")
        self.monitor.log_performance_stats(1, 0.1, 0.2, 0.3, 0.5, 2.0**16)
        
        self.monitor.save_amp_logs("test_amp_logs.json")
        
        # Check if file was created
        log_file = Path(self.temp_dir) / "test_amp_logs.json"
        self.assertTrue(log_file.exists())
        
        # Check file content
        with open(log_file, 'r') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            data = json.load(f)
        
        self.assertIn('config', data)
        self.assertIn('scaling_history', data)
        self.assertIn('performance_history', data)
        self.assertIn('memory_history', data)
        self.assertIn('summary', data)


class TestCustomGradScaler(unittest.TestCase):
    """Test CustomGradScaler functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = MixedPrecisionConfig()
        self.monitor = AMPMonitor(self.config)
        self.scaler = CustomGradScaler(self.config, self.monitor)
    
    def test_initialization(self) -> Any:
        """Test scaler initialization."""
        self.assertIsNotNone(self.scaler.config)
        self.assertIsNotNone(self.scaler.monitor)
        self.assertEqual(self.scaler.step_count, 0)
        self.assertEqual(self.scaler.get_scale(), self.config.init_scale)
    
    def test_step(self) -> Any:
        """Test scaler step with monitoring."""
        # Create dummy optimizer
        model = nn.Linear(10, 5)
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        # Create dummy loss
        loss = torch.tensor(1.0, requires_grad=True)
        
        # Mock the step method
        with patch.object(torch.cuda.amp.GradScaler, 'step') as mock_step:
            mock_step.return_value = None
            self.scaler.step(optimizer)
            
            # Check if step was called
            mock_step.assert_called_once_with(optimizer)
            
            # Check if step count increased
            self.assertEqual(self.scaler.step_count, 1)
    
    def test_update(self) -> Any:
        """Test scaler update with monitoring."""
        old_scale = self.scaler.get_scale()
        
        # Mock the update method
        with patch.object(torch.cuda.amp.GradScaler, 'update') as mock_update:
            mock_update.return_value: bool = True
            result = self.scaler.update()
            
            # Check if update was called
            mock_update.assert_called_once()
            
            # Check result
            self.assertTrue(result)


class TestMixedPrecisionTrainer(unittest.TestCase):
    """Test MixedPrecisionTrainer functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = MixedPrecisionConfig(
            output_dir=self.temp_dir,
            enabled: bool = True
        )
        self.trainer = MixedPrecisionTrainer(self.config)
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 2)
        )
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self) -> Any:
        """Test trainer initialization."""
        self.assertIsNotNone(self.trainer.config)
        self.assertIsNotNone(self.trainer.monitor)
        self.assertIsNotNone(self.trainer.scaler)
        self.assertIsNotNone(self.trainer.autocast)
    
    def test_setup_model(self) -> Any:
        """Test model setup."""
        model = self.trainer.setup_model(self.model)
        
        self.assertEqual(model, self.model)
        self.assertEqual(self.trainer.model, self.model)
    
    def test_setup_optimizer(self) -> Any:
        """Test optimizer setup."""
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        trainer_optimizer = self.trainer.setup_optimizer(optimizer)
        
        self.assertEqual(trainer_optimizer, optimizer)
        self.assertEqual(self.trainer.optimizer, optimizer)
    
    def test_setup_criterion(self) -> Any:
        """Test criterion setup."""
        criterion = nn.CrossEntropyLoss()
        trainer_criterion = self.trainer.setup_criterion(criterion)
        
        self.assertEqual(trainer_criterion, criterion)
        self.assertEqual(self.trainer.criterion, criterion)
    
    def test_train_step_amp(self) -> Any:
        """Test AMP training step."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Create sample data
        data = torch.randn(8, 10)
        target = torch.randint(0, 2, (8,))
        
        # Training step
        metrics = self.trainer.train_step(data, target, step=1)
        
        # Check metrics
        self.assertIn('loss', metrics)
        self.assertIn('scale', metrics)
        self.assertIn('forward_time', metrics)
        self.assertIn('backward_time', metrics)
        self.assertIn('total_time', metrics)
        
        self.assertIsInstance(metrics['loss'], float)
        self.assertIsInstance(metrics['scale'], float)
        self.assertGreater(metrics['loss'], 0)
        self.assertGreater(metrics['scale'], 0)
    
    def test_train_step_fp32(self) -> Any:
        """Test FP32 training step (fallback)."""
        # Disable AMP
        self.config.enabled: bool = False
        trainer = MixedPrecisionTrainer(self.config)
        
        # Setup components
        trainer.setup_model(self.model)
        trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Create sample data
        data = torch.randn(8, 10)
        target = torch.randint(0, 2, (8,))
        
        # Training step
        metrics = trainer.train_step(data, target, step=1)
        
        # Check metrics
        self.assertIn('loss', metrics)
        self.assertIn('scale', metrics)
        self.assertEqual(metrics['scale'], 1.0)  # No scaling in FP32
    
    def test_validate(self) -> bool:
        """Test validation with mixed precision."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Create sample data loader
        data = torch.randn(16, 10)
        target = torch.randint(0, 2, (16,))
        dataset = torch.utils.data.TensorDataset(data, target)
        data_loader = torch.utils.data.DataLoader(dataset, batch_size=8)
        
        # Validation
        val_metrics = self.trainer.validate(data_loader)
        
        # Check metrics
        self.assertIn('val_loss', val_metrics)
        self.assertIn('val_accuracy', val_metrics)
        self.assertIsInstance(val_metrics['val_loss'], float)
        self.assertIsInstance(val_metrics['val_accuracy'], float)
        self.assertGreater(val_metrics['val_loss'], 0)
        self.assertGreaterEqual(val_metrics['val_accuracy'], 0)
        self.assertLessEqual(val_metrics['val_accuracy'], 100)
    
    def test_get_amp_info(self) -> Optional[Dict[str, Any]]:
        """Test AMP information retrieval."""
        amp_info = self.trainer.get_amp_info()
        
        self.assertIn('enabled', amp_info)
        self.assertIn('dtype', amp_info)
        self.assertIn('device_type', amp_info)
        self.assertIn('loss_scaling_enabled', amp_info)
        self.assertIn('gradient_clipping', amp_info)
        self.assertIn('use_fp16_optimizer', amp_info)
        self.assertIn('use_fp16_ema', amp_info)
        
        self.assertTrue(amp_info['enabled'])
        self.assertEqual(amp_info['dtype'], 'torch.float16')
        self.assertEqual(amp_info['device_type'], 'cuda')
    
    def test_save_checkpoint(self) -> Any:
        """Test checkpoint saving."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Save checkpoint
        self.trainer.save_checkpoint(epoch=1, step=100, filename="test_checkpoint.pth")
        
        # Check if file was created
        checkpoint_path = Path(self.temp_dir) / "test_checkpoint.pth"
        self.assertTrue(checkpoint_path.exists())
        
        # Check checkpoint content
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        self.assertIn('epoch', checkpoint)
        self.assertIn('step', checkpoint)
        self.assertIn('model_state_dict', checkpoint)
        self.assertIn('optimizer_state_dict', checkpoint)
        self.assertIn('scaler_state_dict', checkpoint)
        self.assertIn('config', checkpoint)
    
    def test_load_checkpoint(self) -> Any:
        """Test checkpoint loading."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Save checkpoint first
        self.trainer.save_checkpoint(epoch=1, step=100, filename="test_checkpoint.pth")
        
        # Load checkpoint
        checkpoint_path = str(Path(self.temp_dir) / "test_checkpoint.pth")
        loaded_checkpoint = self.trainer.load_checkpoint(checkpoint_path)
        
        # Check loaded checkpoint
        self.assertIn('epoch', loaded_checkpoint)
        self.assertIn('step', loaded_checkpoint)
        self.assertEqual(loaded_checkpoint['epoch'], 1)
        self.assertEqual(loaded_checkpoint['step'], 100)
    
    def test_cleanup(self) -> Any:
        """Test cleanup functionality."""
        # Add some monitoring data
        self.trainer.monitor.log_scaling_event(1, 2.0**16, "step")
        self.trainer.monitor.log_performance_stats(1, 0.1, 0.2, 0.3, 0.5, 2.0**16)
        
        # Run cleanup
        self.trainer.cleanup()
        
        # Check if summary was saved
        summary_path = Path(self.temp_dir) / "amp_summary.json"
        self.assertTrue(summary_path.exists())


class TestPrecisionPolicies(unittest.TestCase):
    """Test precision policies."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.default_policy = DefaultPrecisionPolicy()
        self.conservative_policy = ConservativePrecisionPolicy()
        self.aggressive_policy = AggressivePrecisionPolicy()
    
    def test_default_precision_policy(self) -> Any:
        """Test default precision policy."""
        # Test linear layers
        linear = nn.Linear(10, 5)
        self.assertTrue(self.default_policy.should_use_fp16(linear, "linear"))
        
        # Test batch norm layers
        batch_norm = nn.BatchNorm1d(5)
        self.assertFalse(self.default_policy.should_use_fp16(batch_norm, "batch_norm"))
        
        # Test layer norm
        layer_norm = nn.LayerNorm(5)
        self.assertFalse(self.default_policy.should_use_fp16(layer_norm, "layer_norm"))
        
        # Test softmax
        softmax = nn.Softmax(dim=1)
        self.assertFalse(self.default_policy.should_use_fp16(softmax, "softmax"))
    
    def test_conservative_precision_policy(self) -> Any:
        """Test conservative precision policy."""
        # Test linear layers
        linear = nn.Linear(10, 5)
        self.assertTrue(self.conservative_policy.should_use_fp16(linear, "linear"))
        
        # Test conv layers
        conv2d = nn.Conv2d(3, 64, 3)
        self.assertTrue(self.conservative_policy.should_use_fp16(conv2d, "conv2d"))
        
        # Test batch norm layers
        batch_norm = nn.BatchNorm1d(5)
        self.assertFalse(self.conservative_policy.should_use_fp16(batch_norm, "batch_norm"))
        
        # Test other layers
        relu = nn.ReLU()
        self.assertFalse(self.conservative_policy.should_use_fp16(relu, "relu"))
    
    def test_aggressive_precision_policy(self) -> Any:
        """Test aggressive precision policy."""
        # Test linear layers
        linear = nn.Linear(10, 5)
        self.assertTrue(self.aggressive_policy.should_use_fp16(linear, "linear"))
        
        # Test batch norm layers
        batch_norm = nn.BatchNorm1d(5)
        self.assertFalse(self.aggressive_policy.should_use_fp16(batch_norm, "batch_norm"))
        
        # Test other layers
        relu = nn.ReLU()
        self.assertTrue(self.aggressive_policy.should_use_fp16(relu, "relu"))
        
        layer_norm = nn.LayerNorm(5)
        self.assertTrue(self.aggressive_policy.should_use_fp16(layer_norm, "layer_norm"))


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_create_mixed_precision_trainer(self) -> Any:
        """Test mixed precision trainer creation."""
        config = MixedPrecisionConfig(enabled=True)
        trainer = create_mixed_precision_trainer(config)
        
        self.assertIsInstance(trainer, MixedPrecisionTrainer)
        self.assertEqual(trainer.config, config)
    
    def test_setup_mixed_precision_training(self) -> Any:
        """Test mixed precision training setup."""
        trainer = setup_mixed_precision_training(
            enabled=True,
            dtype=torch.float16,
            init_scale=2.0**15,
            max_grad_norm=2.0,
            use_fp16_optimizer=True,
            use_fp16_ema: bool = True
        )
        
        self.assertIsInstance(trainer, MixedPrecisionTrainer)
        self.assertTrue(trainer.config.enabled)
        self.assertEqual(trainer.config.dtype, torch.float16)
        self.assertEqual(trainer.config.init_scale, 2.0**15)
        self.assertEqual(trainer.config.max_grad_norm, 2.0)
        self.assertTrue(trainer.config.use_fp16_optimizer)
        self.assertTrue(trainer.config.use_fp16_ema)
    
    def test_benchmark_mixed_precision(self) -> Any:
        """Test mixed precision benchmarking."""
        model = nn.Sequential(
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 10)
        )
        data = torch.randn(32, 100)
        target = torch.randint(0, 10, (32,))
        
        # Run benchmark with fewer runs for testing
        benchmark_results = benchmark_mixed_precision(model, data, target, num_runs=5)
        
        self.assertIn('fp32_avg_time', benchmark_results)
        self.assertIn('amp_avg_time', benchmark_results)
        self.assertIn('speedup', benchmark_results)
        self.assertIn('memory_saved_percent', benchmark_results)
        
        self.assertGreater(benchmark_results['fp32_avg_time'], 0)
        self.assertGreater(benchmark_results['amp_avg_time'], 0)
        self.assertGreater(benchmark_results['speedup'], 0)


class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = MixedPrecisionConfig(
            output_dir=self.temp_dir,
            enabled=True,
            monitor_memory_usage=True,
            monitor_performance: bool = True
        )
        self.trainer = MixedPrecisionTrainer(self.config)
        self.model = nn.Sequential(
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 10)
        )
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_training_workflow(self) -> Any:
        """Test complete mixed precision training workflow."""
        # Setup components
        model = self.trainer.setup_model(self.model)
        optimizer = self.trainer.setup_optimizer(optim.Adam(model.parameters(), lr=0.001))
        criterion = self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Training loop
        for step in range(10):
            # Create sample data
            data = torch.randn(16, 100)
            target = torch.randint(0, 10, (16,))
            
            # Training step
            metrics = self.trainer.train_step(data, target, step)
            
            # Check metrics
            self.assertIn('loss', metrics)
            self.assertIn('scale', metrics)
            self.assertIn('forward_time', metrics)
            self.assertIn('backward_time', metrics)
            self.assertIn('total_time', metrics)
            
            if step % 5 == 0:
                print(f"Step {step}: Loss: Dict[str, Any] = {metrics['loss']:.4f}, "
                      f"Scale: Dict[str, Any] = {metrics['scale']:.2e}, "
                      f"Time: Dict[str, Any] = {metrics['total_time']:.4f}s")
        
        # Get AMP information
        amp_info = self.trainer.get_amp_info()
        self.assertTrue(amp_info['enabled'])
        
        # Get AMP summary
        amp_summary = self.trainer.monitor.get_amp_summary()
        self.assertIn('total_steps', amp_summary)
        self.assertIn('performance_stats', amp_summary)
        
        # Save checkpoint
        self.trainer.save_checkpoint(epoch=1, step=10, filename="final_checkpoint.pth")
        
        # Cleanup
        self.trainer.cleanup()
    
    def test_mixed_precision_with_gradient_clipping(self) -> Any:
        """Test mixed precision training with gradient clipping."""
        config = MixedPrecisionConfig(
            enabled=True,
            max_grad_norm=1.0,
            clip_grad_norm: bool = True
        )
        trainer = MixedPrecisionTrainer(config)
        
        # Setup components
        trainer.setup_model(self.model)
        trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Training with gradient clipping
        for step in range(5):
            data = torch.randn(16, 100)
            target = torch.randint(0, 10, (16,))
            
            metrics = trainer.train_step(data, target, step)
            
            # Check that training completed successfully
            self.assertIn('loss', metrics)
            self.assertGreater(metrics['loss'], 0)
    
    def test_mixed_precision_with_ema(self) -> Any:
        """Test mixed precision training with EMA."""
        config = MixedPrecisionConfig(
            enabled=True,
            use_fp16_ema=True,
            ema_decay=0.999
        )
        trainer = MixedPrecisionTrainer(config)
        
        # Setup components
        trainer.setup_model(self.model)
        trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Training with EMA
        for step in range(5):
            data = torch.randn(16, 100)
            target = torch.randint(0, 10, (16,))
            
            metrics = trainer.train_step(data, target, step)
            
            # Check that training completed successfully
            self.assertIn('loss', metrics)
            self.assertGreater(metrics['loss'], 0)
        
        # Check if EMA model exists
        ema_model = trainer.get_ema_model()
        self.assertIsNotNone(ema_model)
    
    def test_mixed_precision_monitoring(self) -> Any:
        """Test mixed precision monitoring and logging."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Training with monitoring
        for step in range(10):
            data = torch.randn(16, 100)
            target = torch.randint(0, 10, (16,))
            
            metrics = self.trainer.train_step(data, target, step)
            
            # Check monitoring data
            if step % 5 == 0:
                # Check scaling history
                scaling_history = self.trainer.monitor.scaling_history
                self.assertGreaterEqual(len(scaling_history), 0)
                
                # Check performance history
                performance_history = self.trainer.monitor.performance_history
                self.assertGreaterEqual(len(performance_history), 0)
                
                # Check memory history
                memory_history = self.trainer.monitor.memory_history
                self.assertGreaterEqual(len(memory_history), 0)
        
        # Save logs
        self.trainer.monitor.save_amp_logs("test_integration_logs.json")
        
        # Check if logs were saved
        log_file = Path(self.temp_dir) / "test_integration_logs.json"
        self.assertTrue(log_file.exists())


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2) 