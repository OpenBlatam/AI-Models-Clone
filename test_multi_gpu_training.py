#!/usr/bin/env python3
"""
🧪 Test Suite for Multi-GPU Training Implementation

This script provides comprehensive testing for the multi-GPU training functionality
including DataParallel, DistributedDataParallel, and automatic strategy selection.
"""

import unittest
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import sys
import os
import logging

# Add the current directory to the path to import the enhanced UI demos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_ui_demos_with_validation import (
    MultiGPUConfig, 
    MultiGPUTrainer,
    EnhancedUIDemosWithValidation
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMultiGPUConfig(unittest.TestCase):
    """Test cases for MultiGPUConfig dataclass."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = MultiGPUConfig()
        
        self.assertEqual(config.training_mode, "auto")
        self.assertTrue(config.enable_data_parallel)
        self.assertFalse(config.enable_distributed)
        self.assertEqual(config.backend, "nccl")
        self.assertEqual(config.batch_size_per_gpu, 32)
        self.assertTrue(config.use_mixed_precision)
        self.assertEqual(config.gradient_accumulation_steps, 1)
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = MultiGPUConfig(
            training_mode="distributed",
            enable_data_parallel=False,
            enable_distributed=True,
            backend="gloo",
            batch_size_per_gpu=64,
            use_mixed_precision=False,
            gradient_accumulation_steps=4
        )
        
        self.assertEqual(config.training_mode, "distributed")
        self.assertFalse(config.enable_data_parallel)
        self.assertTrue(config.enable_distributed)
        self.assertEqual(config.backend, "gloo")
        self.assertEqual(config.batch_size_per_gpu, 64)
        self.assertFalse(config.use_mixed_precision)
        self.assertEqual(config.gradient_accumulation_steps, 4)

class TestMultiGPUTrainer(unittest.TestCase):
    """Test cases for MultiGPUTrainer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = MultiGPUConfig()
        self.trainer = MultiGPUTrainer(self.config)
        
        # Create a simple test model
        self.test_model = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 5)
        )
    
    def test_initialization(self):
        """Test trainer initialization."""
        self.assertIsNotNone(self.trainer)
        self.assertEqual(self.trainer.config, self.config)
        self.assertFalse(self.trainer.is_distributed)
        self.assertFalse(self.trainer.is_data_parallel)
    
    def test_gpu_info(self):
        """Test GPU information retrieval."""
        gpu_info = self.trainer.get_gpu_info()
        
        # Check required keys
        required_keys = ['cuda_available', 'gpu_count']
        for key in required_keys:
            self.assertIn(key, gpu_info)
        
        # Check data types
        self.assertIsInstance(gpu_info['cuda_available'], bool)
        self.assertIsInstance(gpu_info['gpu_count'], int)
        
        # Check GPU count is non-negative
        self.assertGreaterEqual(gpu_info['gpu_count'], 0)
    
    def test_auto_detect_training_mode(self):
        """Test automatic training mode detection."""
        # Test single GPU case
        self.trainer.gpu_count = 1
        self.trainer._auto_detect_training_mode()
        self.assertEqual(self.trainer.config.training_mode, "single_gpu")
        self.assertFalse(self.trainer.config.enable_data_parallel)
        self.assertFalse(self.trainer.config.enable_distributed)
        
        # Test DataParallel case
        self.trainer.gpu_count = 3
        self.trainer._auto_detect_training_mode()
        self.assertEqual(self.trainer.config.training_mode, "data_parallel")
        self.assertTrue(self.trainer.config.enable_data_parallel)
        self.assertFalse(self.trainer.config.enable_distributed)
        
        # Test DistributedDataParallel case
        self.trainer.gpu_count = 8
        self.trainer._auto_detect_training_mode()
        self.assertEqual(self.trainer.config.training_mode, "distributed")
        self.assertFalse(self.trainer.config.enable_data_parallel)
        self.assertTrue(self.trainer.config.enable_distributed)
    
    def test_data_parallel_setup(self):
        """Test DataParallel setup."""
        if torch.cuda.is_available() and torch.cuda.device_count() >= 2:
            # Test successful setup
            model, success = self.trainer.setup_data_parallel(self.test_model)
            self.assertTrue(success)
            self.assertTrue(self.trainer.is_data_parallel)
            self.assertIsInstance(model, torch.nn.DataParallel)
            
            # Test with specific device IDs
            device_ids = [0, 1]
            model, success = self.trainer.setup_data_parallel(self.test_model, device_ids)
            self.assertTrue(success)
        else:
            # Test fallback for insufficient GPUs
            model, success = self.trainer.setup_data_parallel(self.test_model)
            self.assertFalse(success)
            self.assertFalse(self.trainer.is_data_parallel)
    
    def test_distributed_data_parallel_setup(self):
        """Test DistributedDataParallel setup."""
        if torch.cuda.is_available() and torch.cuda.device_count() >= 2:
            # Test successful setup
            model, success = self.trainer.setup_distributed_data_parallel(
                self.test_model, 
                backend='nccl',
                world_size=2,
                rank=0
            )
            self.assertTrue(success)
            self.assertTrue(self.trainer.is_distributed)
            self.assertIsInstance(model, torch.nn.parallel.DistributedDataParallel)
        else:
            # Test fallback for insufficient GPUs
            model, success = self.trainer.setup_distributed_data_parallel(self.test_model)
            self.assertFalse(success)
            self.assertFalse(self.trainer.is_distributed)
    
    def test_multi_gpu_setup(self):
        """Test multi-GPU setup with automatic strategy selection."""
        if torch.cuda.is_available() and torch.cuda.device_count() >= 2:
            # Test auto strategy
            model, success, gpu_info = self.trainer.setup_multi_gpu(
                self.test_model, 
                strategy='auto'
            )
            self.assertTrue(success)
            self.assertIn('gpu_count', gpu_info)
            
            # Test DataParallel strategy
            model, success, gpu_info = self.trainer.setup_multi_gpu(
                self.test_model, 
                strategy='DataParallel'
            )
            self.assertTrue(success)
            
            # Test DistributedDataParallel strategy
            model, success, gpu_info = self.trainer.setup_multi_gpu(
                self.test_model, 
                strategy='DistributedDataParallel'
            )
            self.assertTrue(success)
        else:
            # Test fallback for insufficient GPUs
            model, success, gpu_info = self.trainer.setup_multi_gpu(self.test_model)
            self.assertFalse(success)
    
    def test_training_with_multi_gpu(self):
        """Test complete multi-GPU training workflow."""
        # Create test data
        X = torch.randn(100, 10)
        y = torch.randint(0, 5, (100,))
        dataset = TensorDataset(X, y)
        train_loader = DataLoader(dataset, batch_size=16, shuffle=True)
        
        # Create optimizer and criterion
        optimizer = optim.Adam(self.test_model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()
        
        # Test training
        results = self.trainer.train_with_multi_gpu(
            model=self.test_model,
            train_loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            num_epochs=2,
            strategy='auto',
            use_mixed_precision=False,
            gradient_accumulation_steps=1
        )
        
        # Check results structure
        required_keys = ['final_loss', 'total_epochs', 'multi_gpu_enabled']
        for key in required_keys:
            self.assertIn(key, results)
        
        # Check data types
        self.assertIsInstance(results['final_loss'], float)
        self.assertIsInstance(results['total_epochs'], int)
        self.assertIsInstance(results['multi_gpu_enabled'], bool)
        
        # Check values are reasonable
        self.assertGreaterEqual(results['final_loss'], 0.0)
        self.assertEqual(results['total_epochs'], 2)
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        # Setup some training state
        if torch.cuda.is_available() and torch.cuda.device_count() >= 2:
            self.trainer.setup_data_parallel(self.test_model)
            self.assertTrue(self.trainer.is_data_parallel)
        
        # Test cleanup
        self.trainer.cleanup()
        self.assertFalse(self.trainer.is_distributed)
        self.assertFalse(self.trainer.is_data_parallel)

class TestEnhancedUIDemosWithValidation(unittest.TestCase):
    """Test cases for EnhancedUIDemosWithValidation with multi-GPU training."""
    
    def setUp(self):
        """Set up test environment."""
        self.multi_gpu_config = MultiGPUConfig(
            training_mode="auto",
            enable_data_parallel=True,
            enable_distributed=True
        )
        
        self.demos = EnhancedUIDemosWithValidation(
            multi_gpu_config=self.multi_gpu_config
        )
    
    def test_initialization(self):
        """Test initialization with multi-GPU configuration."""
        self.assertIsNotNone(self.demos.multi_gpu_trainer)
        self.assertEqual(self.demos.multi_gpu_config, self.multi_gpu_config)
        self.assertIsInstance(self.demos.multi_gpu_trainer, MultiGPUTrainer)
    
    def test_multi_gpu_training_interface_creation(self):
        """Test creation of multi-GPU training interface."""
        try:
            interface = self.demos.create_multi_gpu_training_interface()
            self.assertIsNotNone(interface)
        except Exception as e:
            self.fail(f"Failed to create multi-GPU training interface: {e}")
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        try:
            self.demos.cleanup()
            # Should not raise any exceptions
        except Exception as e:
            self.fail(f"Cleanup failed: {e}")

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete multi-GPU training system."""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end multi-GPU training workflow."""
        # Create configuration
        config = MultiGPUConfig(
            training_mode="auto",
            enable_data_parallel=True,
            enable_distributed=True,
            batch_size_per_gpu=16,
            use_mixed_precision=True,
            gradient_accumulation_steps=2
        )
        
        # Initialize trainer
        trainer = MultiGPUTrainer(config)
        
        # Create model and data
        model = nn.Sequential(
            nn.Linear(20, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 10)
        )
        
        X = torch.randn(200, 20)
        y = torch.randint(0, 10, (200,))
        dataset = TensorDataset(X, y)
        train_loader = DataLoader(dataset, batch_size=16, shuffle=True)
        
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()
        
        # Run training
        results = trainer.train_with_multi_gpu(
            model=model,
            train_loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            num_epochs=3,
            strategy='auto',
            use_mixed_precision=True,
            gradient_accumulation_steps=2
        )
        
        # Verify results
        self.assertIn('final_loss', results)
        self.assertIn('multi_gpu_enabled', results)
        self.assertIn('strategy_used', results)
        
        # Cleanup
        trainer.cleanup()

def run_performance_tests():
    """Run performance tests to measure multi-GPU training benefits."""
    print("\n🚀 Running Performance Tests...")
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available, skipping performance tests")
        return
    
    gpu_count = torch.cuda.device_count()
    print(f"📊 Testing with {gpu_count} GPU(s)")
    
    # Create test model and data
    model = nn.Sequential(
        nn.Linear(100, 512),
        nn.ReLU(),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.Linear(256, 100)
    )
    
    X = torch.randn(1000, 100)
    y = torch.randn(1000, 100)
    dataset = TensorDataset(X, y)
    
    # Test different batch sizes
    batch_sizes = [16, 32, 64, 128]
    
    for batch_size in batch_sizes:
        if batch_size * gpu_count > 1000:
            continue
            
        train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.MSELoss()
        
        # Time training
        import time
        start_time = time.time()
        
        config = MultiGPUConfig(batch_size_per_gpu=batch_size)
        trainer = MultiGPUTrainer(config)
        
        results = trainer.train_with_multi_gpu(
            model=model,
            train_loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            num_epochs=2,
            strategy='auto',
            use_mixed_precision=True,
            gradient_accumulation_steps=1
        )
        
        end_time = time.time()
        training_time = end_time - start_time
        
        print(f"  Batch size {batch_size}: {training_time:.2f}s, Loss: {results['final_loss']:.4f}")
        
        trainer.cleanup()

def main():
    """Main test runner."""
    print("🧪 Multi-GPU Training Test Suite")
    print("=" * 50)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
