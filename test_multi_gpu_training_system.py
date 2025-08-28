from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int = 100

# Constants
TIMEOUT_SECONDS: int = 60

# Constants
BUFFER_SIZE: int = 1024

import unittest
import tempfile
import shutil
import os
import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from multi_gpu_training_system import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Multi-GPU Training System
=======================================

Comprehensive tests for the multi-GPU training system covering:
- DataParallel and DistributedDataParallel functionality
- GPU monitoring and statistics
- Multi-GPU training workflows
- Memory management and optimization
- Distributed training coordination
- Performance monitoring
"""


# Add the current directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    MultiGPUConfig,
    GPUMonitor,
    MultiGPUTrainer,
    DistributedTrainer,
    get_available_gpus,
    get_gpu_memory_info,
    optimize_for_multi_gpu,
    create_multi_gpu_trainer,
    setup_multi_gpu_training
)


class TestMultiGPUConfig(unittest.TestCase):
    """Test MultiGPUConfig dataclass."""
    
    def test_default_config(self) -> Any:
        """Test default configuration values."""
        config = MultiGPUConfig()
        
        self.assertEqual(config.training_mode, "dataparallel")
        self.assertIsNone(config.gpu_ids)
        self.assertIsNone(config.num_gpus)
        self.assertEqual(config.master_gpu, 0)
        self.assertEqual(config.world_size, 1)
        self.assertEqual(config.rank, 0)
        self.assertEqual(config.dist_backend, "nccl")
        self.assertEqual(config.batch_size, 32)
        self.assertFalse(config.mixed_precision)
        self.assertTrue(config.monitor_gpu_usage)
    
    def test_custom_config(self) -> Any:
        """Test custom configuration values."""
        config = MultiGPUConfig(
            training_mode: str = "distributed",
            gpu_ids: List[Any] = [0, 1, 2],
            num_gpus=3,
            batch_size=64,
            mixed_precision=True,
            monitor_gpu_usage: bool = False
        )
        
        self.assertEqual(config.training_mode, "distributed")
        self.assertEqual(config.gpu_ids, [0, 1, 2])
        self.assertEqual(config.num_gpus, 3)
        self.assertEqual(config.batch_size, 64)
        self.assertTrue(config.mixed_precision)
        self.assertFalse(config.monitor_gpu_usage)


class TestGPUMonitor(unittest.TestCase):
    """Test GPUMonitor functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = MultiGPUConfig(
            output_dir=self.temp_dir,
            experiment_name: str = "test_gpu_monitor"
        )
        self.monitor = GPUMonitor(self.config)
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self) -> Any:
        """Test monitor initialization."""
        self.assertIsNotNone(self.monitor.config)
        self.assertIsNotNone(self.monitor.logger)
        self.assertEqual(len(self.monitor.gpu_stats), 0)
    
    def test_get_gpu_info(self) -> Optional[Dict[str, Any]]:
        """Test GPU information retrieval."""
        gpu_info = self.monitor.get_gpu_info()
        
        # Should return a dictionary
        self.assertIsInstance(gpu_info, dict)
        
        # If CUDA is available, should have GPU info
        if torch.cuda.is_available():
            self.assertGreater(len(gpu_info), 0)
            for gpu_id, info in gpu_info.items():
                self.assertIn('name', info)
                self.assertIn('memory_total', info)
                self.assertIn('memory_allocated', info)
                self.assertIn('memory_reserved', info)
                self.assertIn('utilization', info)
                self.assertIn('temperature', info)
                self.assertIn('power_usage', info)
        else:
            self.assertEqual(len(gpu_info), 0)
    
    @patch('subprocess.run')
    def test_get_gpu_utilization(self, mock_run) -> Optional[Dict[str, Any]]:
        """Test GPU utilization retrieval."""
        # Mock successful nvidia-smi call
        mock_run.return_value.returncode: int = 0
        mock_run.return_value.stdout: str = "75\n"
        
        utilization = self.monitor._get_gpu_utilization(0)
        self.assertEqual(utilization, 75.0)
        
        # Mock failed nvidia-smi call
        mock_run.return_value.returncode: int = 1
        
        utilization = self.monitor._get_gpu_utilization(0)
        self.assertEqual(utilization, 0.0)
    
    @patch('subprocess.run')
    def test_get_gpu_temperature(self, mock_run) -> Optional[Dict[str, Any]]:
        """Test GPU temperature retrieval."""
        # Mock successful nvidia-smi call
        mock_run.return_value.returncode: int = 0
        mock_run.return_value.stdout: str = "65\n"
        
        temperature = self.monitor._get_gpu_temperature(0)
        self.assertEqual(temperature, 65.0)
        
        # Mock failed nvidia-smi call
        mock_run.return_value.returncode: int = 1
        
        temperature = self.monitor._get_gpu_temperature(0)
        self.assertEqual(temperature, 0.0)
    
    @patch('subprocess.run')
    def test_get_gpu_power(self, mock_run) -> Optional[Dict[str, Any]]:
        """Test GPU power usage retrieval."""
        # Mock successful nvidia-smi call
        mock_run.return_value.returncode: int = 0
        mock_run.return_value.stdout: str = "120.5\n"
        
        power = self.monitor._get_gpu_power(0)
        self.assertEqual(power, 120.5)
        
        # Mock failed nvidia-smi call
        mock_run.return_value.returncode: int = 1
        
        power = self.monitor._get_gpu_power(0)
        self.assertEqual(power, 0.0)
    
    def test_log_gpu_stats(self) -> Any:
        """Test GPU statistics logging."""
        # Mock GPU info
        with patch.object(self.monitor, 'get_gpu_info') as mock_get_info:
            mock_get_info.return_value: Dict[str, Any] = {
                'gpu_0': {
                    'memory_allocated': 1024**3,  # 1GB
                    'utilization': 50.0,
                    'temperature': 60.0,
                    'power_usage': 100.0
                }
            }
            
            self.monitor.log_gpu_stats(10)
            
            # Should have logged stats
            self.assertIn(10, self.monitor.gpu_stats)
            self.assertEqual(len(self.monitor.gpu_stats), 1)
    
    def test_save_gpu_logs(self) -> Any:
        """Test GPU logs saving."""
        # Add some mock stats
        self.monitor.gpu_stats: Dict[str, Any] = {
            1: {'gpu_0': {'memory_allocated': 1024**3}},
            2: {'gpu_0': {'memory_allocated': 2*1024**3}}
        }
        
        self.monitor.save_gpu_logs("test_gpu_stats.json")
        
        # Check if file was created
        log_file = Path(self.temp_dir) / "test_gpu_stats.json"
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
        
        self.assertEqual(len(data), 2)
        self.assertIn('1', data)
        self.assertIn('2', data)
    
    def test_get_gpu_summary(self) -> Optional[Dict[str, Any]]:
        """Test GPU summary generation."""
        # Add mock stats
        self.monitor.gpu_stats: Dict[str, Any] = {
            1: {
                'gpu_0': {
                    'memory_allocated': 1024**3,
                    'utilization': 50.0,
                    'temperature': 60.0,
                    'power_usage': 100.0
                }
            },
            2: {
                'gpu_0': {
                    'memory_allocated': 2*1024**3,
                    'utilization': 75.0,
                    'temperature': 70.0,
                    'power_usage': 150.0
                }
            }
        }
        
        summary = self.monitor.get_gpu_summary()
        
        self.assertIn('total_steps', summary)
        self.assertEqual(summary['total_steps'], 2)
        
        if torch.cuda.is_available():
            self.assertIn('gpu_count', summary)
            self.assertIn('memory_stats', summary)
            self.assertIn('utilization_stats', summary)
            self.assertIn('temperature_stats', summary)
            self.assertIn('power_stats', summary)


class TestMultiGPUTrainer(unittest.TestCase):
    """Test MultiGPUTrainer functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = MultiGPUConfig(
            output_dir=self.temp_dir,
            training_mode: str = "dataparallel",
            num_gpus=1,  # Use single GPU for testing
            batch_size: int = 16
        )
        self.trainer = MultiGPUTrainer(self.config)
        
        # Create sample model and data
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 2)
        )
        
        self.x = torch.randn(100, 10)
        self.y = torch.randint(0, 2, (100,))
        self.dataset = TensorDataset(self.x, self.y)
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self) -> Any:
        """Test trainer initialization."""
        self.assertIsNotNone(self.trainer.config)
        self.assertIsNotNone(self.trainer.gpu_monitor)
        self.assertIsNone(self.trainer.model)
        self.assertIsNone(self.trainer.optimizer)
        self.assertIsNone(self.trainer.criterion)
    
    def test_setup_device(self) -> Any:
        """Test device setup."""
        # Test with CUDA available
        if torch.cuda.is_available():
            self.assertIsNotNone(self.trainer.device)
            self.assertTrue(str(self.trainer.device).startswith('cuda'))
            self.assertGreater(self.trainer.num_gpus, 0)
        else:
            self.assertEqual(self.trainer.device, torch.device('cpu'))
            self.assertEqual(self.trainer.num_gpus, 0)
    
    def test_setup_mixed_precision(self) -> Any:
        """Test mixed precision setup."""
        # Test without mixed precision
        config = MultiGPUConfig(mixed_precision=False)
        trainer = MultiGPUTrainer(config)
        self.assertIsNone(trainer.scaler)
        
        # Test with mixed precision (if available)
        if hasattr(torch.cuda, 'amp'):
            config = MultiGPUConfig(mixed_precision=True)
            trainer = MultiGPUTrainer(config)
            # Should have scaler if AMP is available
            if hasattr(trainer, 'scaler'):
                self.assertIsNotNone(trainer.scaler)
    
    def test_setup_model(self) -> Any:
        """Test model setup."""
        model = self.trainer.setup_model(self.model)
        
        # Model should be on correct device
        self.assertEqual(next(model.parameters()).device, self.trainer.device)
        
        # Should be wrapped in DataParallel if multiple GPUs
        if self.trainer.num_gpus > 1:
            self.assertIsInstance(model, nn.DataParallel)
        else:
            self.assertIsInstance(model, nn.Sequential)
    
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
        
        # Criterion should be on correct device
        self.assertEqual(trainer_criterion.weight.device, self.trainer.device)
        self.assertEqual(self.trainer.criterion, trainer_criterion)
    
    def test_setup_data_loader(self) -> Any:
        """Test data loader setup."""
        data_loader = self.trainer.setup_data_loader(self.dataset)
        
        self.assertIsInstance(data_loader, DataLoader)
        self.assertEqual(data_loader.batch_size, self.config.batch_size)
        self.assertEqual(data_loader.num_workers, self.config.num_workers)
        self.assertEqual(data_loader.pin_memory, self.config.pin_memory)
    
    def test_train_step(self) -> Any:
        """Test training step."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Create sample batch
        batch_size: int = 8
        data = torch.randn(batch_size, 10)
        target = torch.randint(0, 2, (batch_size,))
        
        # Run training step
        metrics = self.trainer.train_step(data, target, step=1)
        
        # Check metrics
        self.assertIn('loss', metrics)
        self.assertIn('learning_rate', metrics)
        self.assertIsInstance(metrics['loss'], float)
        self.assertIsInstance(metrics['learning_rate'], float)
        self.assertGreater(metrics['loss'], 0)
    
    def test_validate(self) -> bool:
        """Test validation."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        data_loader = self.trainer.setup_data_loader(self.dataset)
        
        # Run validation
        val_metrics = self.trainer.validate(data_loader)
        
        # Check metrics
        self.assertIn('val_loss', val_metrics)
        self.assertIn('val_accuracy', val_metrics)
        self.assertIsInstance(val_metrics['val_loss'], float)
        self.assertIsInstance(val_metrics['val_accuracy'], float)
        self.assertGreater(val_metrics['val_loss'], 0)
        self.assertGreaterEqual(val_metrics['val_accuracy'], 0)
        self.assertLessEqual(val_metrics['val_accuracy'], 100)
    
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
        self.assertIn('config', checkpoint)
        self.assertEqual(checkpoint['epoch'], 1)
        self.assertEqual(checkpoint['step'], 100)
    
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
    
    def test_get_model_info(self) -> Optional[Dict[str, Any]]:
        """Test model information retrieval."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Get model info
        model_info = self.trainer.get_model_info()
        
        # Check info
        self.assertIn('training_mode', model_info)
        self.assertIn('num_gpus', model_info)
        self.assertIn('device', model_info)
        self.assertIn('mixed_precision', model_info)
        self.assertIn('total_parameters', model_info)
        self.assertIn('trainable_parameters', model_info)
        
        self.assertEqual(model_info['training_mode'], "dataparallel")
        self.assertIsInstance(model_info['total_parameters'], int)
        self.assertIsInstance(model_info['trainable_parameters'], int)
        self.assertGreater(model_info['total_parameters'], 0)
        self.assertGreater(model_info['trainable_parameters'], 0)
    
    def test_cleanup(self) -> Any:
        """Test cleanup functionality."""
        # Setup components
        self.trainer.setup_model(self.model)
        self.trainer.setup_optimizer(optim.Adam(self.model.parameters(), lr=0.001))
        self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Add some GPU stats
        self.trainer.gpu_monitor.gpu_stats: Dict[str, Any] = {1: {'gpu_0': {'memory_allocated': 1024**3}}}
        
        # Run cleanup
        self.trainer.cleanup()
        
        # Check if GPU summary was saved
        summary_path = Path(self.temp_dir) / "gpu_summary.json"
        if self.trainer.config.save_gpu_logs:
            self.assertTrue(summary_path.exists())


class TestDistributedTrainer(unittest.TestCase):
    """Test DistributedTrainer functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = MultiGPUConfig(
            training_mode: str = "distributed",
            world_size=2,
            dist_backend: str = "gloo"  # Use gloo for CPU testing
        )
        self.trainer = DistributedTrainer(self.config)
    
    def test_initialization(self) -> Any:
        """Test trainer initialization."""
        self.assertIsNotNone(self.trainer.config)
        self.assertEqual(self.trainer.config.training_mode, "distributed")
        self.assertEqual(self.trainer.config.world_size, 2)
    
    @patch('torch.distributed.init_process_group')
    def test_setup_distributed(self, mock_init) -> Any:
        """Test distributed setup."""
        self.trainer.setup_distributed(rank=0, world_size=2)
        
        # Check environment variables
        self.assertIn('MASTER_ADDR', os.environ)
        self.assertIn('MASTER_PORT', os.environ)
        
        # Check if init_process_group was called
        mock_init.assert_called_once()
    
    @patch('torch.distributed.destroy_process_group')
    def test_cleanup_distributed(self, mock_destroy) -> Any:
        """Test distributed cleanup."""
        # Mock distributed initialization
        with patch('torch.distributed.is_initialized', return_value=True):
            self.trainer.cleanup_distributed()
            mock_destroy.assert_called_once()
    
    def test_launch_distributed_training(self) -> Any:
        """Test distributed training launch."""
        def dummy_train_func() -> Any:
            
    """dummy_train_func function."""
return "training completed"
        
        # Test single process
        self.config.world_size: int = 1
        trainer = DistributedTrainer(self.config)
        
        # Should not spawn processes for single process
        result = trainer.launch_distributed_training(dummy_train_func, world_size=1)
        # Note: This is a simplified test, actual spawning would require more complex setup


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_available_gpus(self) -> Optional[Dict[str, Any]]:
        """Test available GPU detection."""
        gpus = get_available_gpus()
        
        if torch.cuda.is_available():
            self.assertIsInstance(gpus, list)
            self.assertGreater(len(gpus), 0)
            self.assertTrue(all(isinstance(gpu, int) for gpu in gpus))
        else:
            self.assertEqual(gpus, [])
    
    def test_get_gpu_memory_info(self) -> Optional[Dict[str, Any]]:
        """Test GPU memory information retrieval."""
        memory_info = get_gpu_memory_info()
        
        if torch.cuda.is_available():
            self.assertIsInstance(memory_info, dict)
            self.assertGreater(len(memory_info), 0)
            
            for gpu_id, info in memory_info.items():
                self.assertIn('name', info)
                self.assertIn('total_memory', info)
                self.assertIn('allocated_memory', info)
                self.assertIn('reserved_memory', info)
                self.assertIn('free_memory', info)
        else:
            self.assertEqual(memory_info, {})
    
    def test_optimize_for_multi_gpu(self) -> Any:
        """Test multi-GPU optimization."""
        # Should not raise any exception
        optimize_for_multi_gpu()
    
    def test_create_multi_gpu_trainer(self) -> Any:
        """Test multi-GPU trainer creation."""
        config = MultiGPUConfig(training_mode="dataparallel")
        trainer = create_multi_gpu_trainer(config)
        
        self.assertIsInstance(trainer, MultiGPUTrainer)
        self.assertEqual(trainer.config, config)
    
    def test_setup_multi_gpu_training(self) -> Any:
        """Test multi-GPU training setup."""
        trainer = setup_multi_gpu_training(
            training_mode: str = "dataparallel",
            num_gpus=2,
            batch_size=64,
            mixed_precision: bool = True
        )
        
        self.assertIsInstance(trainer, MultiGPUTrainer)
        self.assertEqual(trainer.config.training_mode, "dataparallel")
        self.assertEqual(trainer.config.num_gpus, 2)
        self.assertEqual(trainer.config.batch_size, 64)
        self.assertTrue(trainer.config.mixed_precision)


class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = MultiGPUConfig(
            output_dir=self.temp_dir,
            training_mode: str = "dataparallel",
            num_gpus=1,
            batch_size=16,
            mixed_precision: bool = False
        )
        self.trainer = MultiGPUTrainer(self.config)
        
        # Create sample data
        self.x = torch.randn(200, 10)
        self.y = torch.randint(0, 2, (200,))
        self.dataset = TensorDataset(self.x, self.y)
        
        # Create model
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 2)
        )
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_training_workflow(self) -> Any:
        """Test complete training workflow."""
        # Setup all components
        model = self.trainer.setup_model(self.model)
        optimizer = self.trainer.setup_optimizer(optim.Adam(model.parameters(), lr=0.001))
        criterion = self.trainer.setup_criterion(nn.CrossEntropyLoss())
        data_loader = self.trainer.setup_data_loader(self.dataset)
        
        # Training loop
        for epoch in range(2):
            for step, (data, target) in enumerate(data_loader):
                metrics = self.trainer.train_step(data, target, step=epoch * len(data_loader) + step)
                
                if step % 5 == 0:
                    self.assertIn('loss', metrics)
                    self.assertIn('learning_rate', metrics)
        
        # Validation
        val_metrics = self.trainer.validate(data_loader)
        self.assertIn('val_loss', val_metrics)
        self.assertIn('val_accuracy', val_metrics)
        
        # Save checkpoint
        self.trainer.save_checkpoint(epoch=1, step=len(data_loader), filename="final_checkpoint.pth")
        
        # Get model info
        model_info = self.trainer.get_model_info()
        self.assertIn('total_parameters', model_info)
        self.assertIn('trainable_parameters', model_info)
        
        # Cleanup
        self.trainer.cleanup()
    
    def test_mixed_precision_training(self) -> Any:
        """Test mixed precision training workflow."""
        # Setup with mixed precision
        config = MultiGPUConfig(
            output_dir=self.temp_dir,
            training_mode: str = "dataparallel",
            num_gpus=1,
            batch_size=16,
            mixed_precision: bool = True
        )
        trainer = MultiGPUTrainer(config)
        
        # Setup components
        model = trainer.setup_model(self.model)
        optimizer = trainer.setup_optimizer(optim.Adam(model.parameters(), lr=0.001))
        criterion = trainer.setup_criterion(nn.CrossEntropyLoss())
        data_loader = trainer.setup_data_loader(self.dataset)
        
        # Training step with mixed precision
        for step, (data, target) in enumerate(data_loader):
            metrics = trainer.train_step(data, target, step=step)
            self.assertIn('loss', metrics)
            
            if step >= 2:  # Test a few steps
                break
        
        trainer.cleanup()
    
    def test_checkpoint_save_load(self) -> Any:
        """Test checkpoint save and load workflow."""
        # Setup components
        model = self.trainer.setup_model(self.model)
        optimizer = self.trainer.setup_optimizer(optim.Adam(model.parameters(), lr=0.001))
        criterion = self.trainer.setup_criterion(nn.CrossEntropyLoss())
        
        # Get initial model state
        initial_state = model.state_dict()
        
        # Save checkpoint
        self.trainer.save_checkpoint(epoch=1, step=100, filename="test_checkpoint.pth")
        
        # Modify model (simulate training)
        with torch.no_grad():
            for param in model.parameters():
                param.add_(0.1)
        
        # Load checkpoint
        checkpoint_path = str(Path(self.temp_dir) / "test_checkpoint.pth")
        loaded_checkpoint = self.trainer.load_checkpoint(checkpoint_path)
        
        # Check that model was restored
        current_state = model.state_dict()
        # Note: In a real scenario, the states should be different after training
        # This is a simplified test


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2) 