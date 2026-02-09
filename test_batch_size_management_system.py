from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
BUFFER_SIZE: int: int = 1024

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
from batch_size_management_system import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Batch Size Management System
==========================================

Comprehensive tests for the batch size management system covering:
- Memory profiling and analysis
- Performance profiling and optimization
- Batch size optimization strategies
- Adaptive batch size management
- Gradient accumulation
- Multi-GPU coordination
"""


# Add the current directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    BatchSizeConfig,
    MemoryProfiler,
    PerformanceProfiler,
    BatchSizeOptimizer,
    MemoryOptimizedBatchSize,
    SpeedOptimizedBatchSize,
    BalancedBatchSize,
    AdaptiveBatchSize,
    GradientAccumulationManager,
    MultiGPUBatchSizeCoordinator,
    calculate_optimal_batch_size,
    create_batch_size_manager,
    setup_adaptive_batch_size
)


class TestBatchSizeConfig(unittest.TestCase):
    """Test BatchSizeConfig dataclass."""
    
    def test_default_config(self) -> Any:
        """Test default configuration values."""
        config = BatchSizeConfig()
        
        self.assertEqual(config.initial_batch_size, 32)
        self.assertEqual(config.min_batch_size, 1)
        self.assertEqual(config.max_batch_size, 1024)
        self.assertTrue(config.enable_dynamic_batch_size)
        self.assertTrue(config.adaptive_batch_size)
        self.assertEqual(config.memory_threshold, 0.9)
        self.assertTrue(config.optimize_for_memory)
        self.assertTrue(config.optimize_for_speed)
        self.assertFalse(config.optimize_for_accuracy)
    
    def test_custom_config(self) -> Any:
        """Test custom configuration values."""
        config = BatchSizeConfig(
            initial_batch_size=64,
            min_batch_size=8,
            max_batch_size=512,
            enable_dynamic_batch_size=False,
            optimize_for_memory=False,
            optimize_for_speed: bool = True
        )
        
        self.assertEqual(config.initial_batch_size, 64)
        self.assertEqual(config.min_batch_size, 8)
        self.assertEqual(config.max_batch_size, 512)
        self.assertFalse(config.enable_dynamic_batch_size)
        self.assertFalse(config.optimize_for_memory)
        self.assertTrue(config.optimize_for_speed)


class TestMemoryProfiler(unittest.TestCase):
    """Test MemoryProfiler functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = BatchSizeConfig()
        self.profiler = MemoryProfiler(self.config)
    
    def test_initialization(self) -> Any:
        """Test profiler initialization."""
        self.assertIsNotNone(self.profiler.config)
        self.assertEqual(len(self.profiler.memory_history), 0)
        self.assertEqual(self.profiler.peak_memory, 0)
    
    def test_get_memory_usage(self) -> Optional[Dict[str, Any]]:
        """Test memory usage retrieval."""
        memory_info = self.profiler.get_memory_usage()
        
        # Check system memory info
        self.assertIn('system_total', memory_info)
        self.assertIn('system_available', memory_info)
        self.assertIn('system_used', memory_info)
        self.assertIn('system_percent', memory_info)
        
        # Check CUDA memory info if available
        if torch.cuda.is_available():
            self.assertIn('cuda_allocated', memory_info)
            self.assertIn('cuda_reserved', memory_info)
            self.assertIn('cuda_max_allocated', memory_info)
            self.assertIn('cuda_max_reserved', memory_info)
            self.assertIn('cuda_free', memory_info)
    
    def test_track_memory(self) -> Any:
        """Test memory tracking functionality."""
        memory_info = self.profiler.track_memory(32, 10)
        
        # Check tracking info
        self.assertEqual(memory_info['batch_size'], 32)
        self.assertEqual(memory_info['step'], 10)
        self.assertIn('timestamp', memory_info)
        
        # Check history
        self.assertEqual(len(self.profiler.memory_history), 1)
        self.assertEqual(self.profiler.memory_history[0]['batch_size'], 32)
    
    def test_estimate_memory_for_batch_size(self) -> Any:
        """Test memory estimation for different batch sizes."""
        # Add some memory history first
        self.profiler.track_memory(32, 1)
        
        # Estimate memory for different batch size
        estimated_memory = self.profiler.estimate_memory_for_batch_size(32, 64)
        
        # Should return a positive value
        self.assertGreater(estimated_memory, 0)
        
        # Should scale approximately linearly
        estimated_memory_128 = self.profiler.estimate_memory_for_batch_size(32, 128)
        self.assertGreater(estimated_memory_128, estimated_memory)
    
    def test_get_optimal_batch_size_for_memory(self) -> Optional[Dict[str, Any]]:
        """Test optimal batch size calculation for memory."""
        # Add memory history
        self.profiler.track_memory(32, 1)
        
        # Calculate optimal batch size for 8GB memory
        optimal_batch_size = self.profiler.get_optimal_batch_size_for_memory(8.0)
        
        # Should be within bounds
        self.assertGreaterEqual(optimal_batch_size, self.config.min_batch_size)
        self.assertLessEqual(optimal_batch_size, self.config.max_batch_size)
    
    def test_is_memory_safe(self) -> Any:
        """Test memory safety check."""
        # Add memory history
        self.profiler.track_memory(32, 1)
        
        # Test with safe batch size
        is_safe = self.profiler.is_memory_safe(16)
        self.assertIsInstance(is_safe, bool)
        
        # Test with very large batch size
        is_safe_large = self.profiler.is_memory_safe(10000)
        self.assertIsInstance(is_safe_large, bool)


class TestPerformanceProfiler(unittest.TestCase):
    """Test PerformanceProfiler functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = BatchSizeConfig()
        self.profiler = PerformanceProfiler(self.config)
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 2)
        )
    
    def test_initialization(self) -> Any:
        """Test profiler initialization."""
        self.assertIsNotNone(self.profiler.config)
        self.assertEqual(len(self.profiler.performance_history), 0)
        self.assertEqual(len(self.profiler.speed_measurements), 0)
    
    def test_measure_training_speed(self) -> Any:
        """Test training speed measurement."""
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        
        performance_info = self.profiler.measure_training_speed(self.model, data, target, 32)
        
        # Check performance info
        self.assertEqual(performance_info['batch_size'], 32)
        self.assertIn('avg_time_per_batch', performance_info)
        self.assertIn('samples_per_second', performance_info)
        self.assertIn('throughput', performance_info)
        self.assertIn('timestamp', performance_info)
        
        # Check history
        self.assertEqual(len(self.profiler.performance_history), 1)
        self.assertEqual(self.profiler.performance_history[0]['batch_size'], 32)
    
    def test_get_optimal_batch_size_for_speed(self) -> Optional[Dict[str, Any]]:
        """Test optimal batch size calculation for speed."""
        # Add performance history
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        
        self.profiler.measure_training_speed(self.model, data, target, 16)
        self.profiler.measure_training_speed(self.model, data, target, 32)
        self.profiler.measure_training_speed(self.model, data, target, 64)
        
        # Get optimal batch size
        optimal_batch_size = self.profiler.get_optimal_batch_size_for_speed()
        
        # Should be one of the tested batch sizes
        self.assertIn(optimal_batch_size, [16, 32, 64])
    
    def test_estimate_speed_for_batch_size(self) -> Any:
        """Test speed estimation for different batch sizes."""
        # Add performance history
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        
        self.profiler.measure_training_speed(self.model, data, target, 16)
        self.profiler.measure_training_speed(self.model, data, target, 32)
        
        # Estimate speed for different batch size
        estimated_speed = self.profiler.estimate_speed_for_batch_size(48)
        
        # Should return a positive value
        self.assertGreater(estimated_speed, 0)


class TestBatchSizeOptimizers(unittest.TestCase):
    """Test batch size optimization strategies."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = BatchSizeConfig()
        self.memory_profiler = MemoryProfiler(self.config)
        self.performance_profiler = PerformanceProfiler(self.config)
        
        # Add some history
        self.memory_profiler.track_memory(32, 1)
        
        model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 2))
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        self.performance_profiler.measure_training_speed(model, data, target, 16)
        self.performance_profiler.measure_training_speed(model, data, target, 32)
    
    def test_memory_optimized_batch_size(self) -> Any:
        """Test memory-optimized batch size strategy."""
        optimizer = MemoryOptimizedBatchSize(self.config)
        
        new_batch_size = optimizer.optimize_batch_size(
            32, self.memory_profiler, self.performance_profiler
        )
        
        # Should be within bounds
        self.assertGreaterEqual(new_batch_size, self.config.min_batch_size)
        self.assertLessEqual(new_batch_size, self.config.max_batch_size)
    
    def test_speed_optimized_batch_size(self) -> Any:
        """Test speed-optimized batch size strategy."""
        optimizer = SpeedOptimizedBatchSize(self.config)
        
        new_batch_size = optimizer.optimize_batch_size(
            32, self.memory_profiler, self.performance_profiler
        )
        
        # Should be within bounds
        self.assertGreaterEqual(new_batch_size, self.config.min_batch_size)
        self.assertLessEqual(new_batch_size, self.config.max_batch_size)
    
    def test_balanced_batch_size(self) -> Any:
        """Test balanced batch size strategy."""
        optimizer = BalancedBatchSize(self.config)
        
        new_batch_size = optimizer.optimize_batch_size(
            32, self.memory_profiler, self.performance_profiler
        )
        
        # Should be within bounds
        self.assertGreaterEqual(new_batch_size, self.config.min_batch_size)
        self.assertLessEqual(new_batch_size, self.config.max_batch_size)


class TestAdaptiveBatchSize(unittest.TestCase):
    """Test AdaptiveBatchSize functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = BatchSizeConfig(
            output_dir=self.temp_dir,
            experiment_name: str: str = "test_adaptive_batch_size"
        )
        self.batch_manager = AdaptiveBatchSize(self.config)
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 2)
        )
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self) -> Any:
        """Test batch manager initialization."""
        self.assertIsNotNone(self.batch_manager.config)
        self.assertIsNotNone(self.batch_manager.memory_profiler)
        self.assertIsNotNone(self.batch_manager.performance_profiler)
        self.assertIsNotNone(self.batch_manager.logger)
        self.assertEqual(self.batch_manager.current_batch_size, self.config.initial_batch_size)
    
    def test_get_current_batch_size(self) -> Optional[Dict[str, Any]]:
        """Test current batch size retrieval."""
        batch_size = self.batch_manager.get_current_batch_size()
        self.assertEqual(batch_size, self.config.initial_batch_size)
    
    def test_update_batch_size(self) -> Any:
        """Test batch size update."""
        old_batch_size = self.batch_manager.current_batch_size
        new_batch_size: int: int = 64
        
        self.batch_manager.update_batch_size(new_batch_size, 10)
        
        # Check current batch size
        self.assertEqual(self.batch_manager.current_batch_size, new_batch_size)
        
        # Check history
        self.assertEqual(len(self.batch_manager.batch_size_history), 1)
        self.assertEqual(self.batch_manager.batch_size_history[0]['old_batch_size'], old_batch_size)
        self.assertEqual(self.batch_manager.batch_size_history[0]['new_batch_size'], new_batch_size)
        self.assertEqual(self.batch_manager.batch_size_history[0]['step'], 10)
    
    def test_optimize_batch_size(self) -> Any:
        """Test batch size optimization."""
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        
        new_batch_size = self.batch_manager.optimize_batch_size(1, self.model, data, target)
        
        # Should be within bounds
        self.assertGreaterEqual(new_batch_size, self.config.min_batch_size)
        self.assertLessEqual(new_batch_size, self.config.max_batch_size)
    
    def test_get_batch_size_for_memory(self) -> Optional[Dict[str, Any]]:
        """Test batch size calculation for memory."""
        batch_size = self.batch_manager.get_batch_size_for_memory(8.0)
        
        # Should be within bounds
        self.assertGreaterEqual(batch_size, self.config.min_batch_size)
        self.assertLessEqual(batch_size, self.config.max_batch_size)
    
    def test_get_batch_size_for_speed(self) -> Optional[Dict[str, Any]]:
        """Test batch size calculation for speed."""
        # Add performance history first
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        self.batch_manager.performance_profiler.measure_training_speed(self.model, data, target, 32)
        
        batch_size = self.batch_manager.get_batch_size_for_speed()
        self.assertEqual(batch_size, 32)
    
    def test_estimate_memory_usage(self) -> Any:
        """Test memory usage estimation."""
        # Add memory history first
        self.batch_manager.memory_profiler.track_memory(32, 1)
        
        estimated_memory = self.batch_manager.estimate_memory_usage(64)
        self.assertIsInstance(estimated_memory, float)
        self.assertGreaterEqual(estimated_memory, 0)
    
    def test_estimate_training_speed(self) -> Any:
        """Test training speed estimation."""
        # Add performance history first
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        self.batch_manager.performance_profiler.measure_training_speed(self.model, data, target, 32)
        
        estimated_speed = self.batch_manager.estimate_training_speed(64)
        self.assertIsInstance(estimated_speed, float)
        self.assertGreaterEqual(estimated_speed, 0)
    
    def test_get_batch_size_summary(self) -> Optional[Dict[str, Any]]:
        """Test batch size summary generation."""
        # Add some batch size changes
        self.batch_manager.update_batch_size(64, 1)
        self.batch_manager.update_batch_size(128, 2)
        
        summary = self.batch_manager.get_batch_size_summary()
        
        self.assertIn('total_changes', summary)
        self.assertIn('current_batch_size', summary)
        self.assertIn('initial_batch_size', summary)
        self.assertIn('batch_size_stats', summary)
        self.assertIn('memory_usage', summary)
        self.assertIn('performance_history', summary)
        
        self.assertEqual(summary['total_changes'], 2)
        self.assertEqual(summary['current_batch_size'], 128)
        self.assertEqual(summary['initial_batch_size'], self.config.initial_batch_size)
    
    def test_save_batch_size_logs(self) -> Any:
        """Test batch size logs saving."""
        # Add some batch size changes
        self.batch_manager.update_batch_size(64, 1)
        self.batch_manager.update_batch_size(128, 2)
        
        self.batch_manager.save_batch_size_logs("test_batch_size_logs.json")
        
        # Check if file was created
        log_file = Path(self.temp_dir) / "test_batch_size_logs.json"
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
        logger.info(f"Error: {e}")  # Super logging
            data = json.load(f)
        
        self.assertIn('config', data)
        self.assertIn('batch_size_history', data)
        self.assertIn('memory_history', data)
        self.assertIn('performance_history', data)
        self.assertIn('summary', data)


class TestGradientAccumulationManager(unittest.TestCase):
    """Test GradientAccumulationManager functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = BatchSizeConfig(
            enable_gradient_accumulation=True,
            accumulation_steps: int: int = 4
        )
        self.manager = GradientAccumulationManager(self.config)
    
    def test_initialization(self) -> Any:
        """Test manager initialization."""
        self.assertEqual(self.manager.accumulation_steps, 4)
        self.assertEqual(self.manager.current_step, 0)
        self.assertEqual(self.manager.effective_batch_size, None)
    
    def test_should_accumulate(self) -> Any:
        """Test accumulation decision."""
        # Should accumulate for steps 1, 2, 3
        self.manager.current_step: int: int = 1
        self.assertTrue(self.manager.should_accumulate())
        
        self.manager.current_step: int: int = 2
        self.assertTrue(self.manager.should_accumulate())
        
        self.manager.current_step: int: int = 3
        self.assertTrue(self.manager.should_accumulate())
        
        # Should not accumulate for step 4
        self.manager.current_step: int: int = 4
        self.assertFalse(self.manager.should_accumulate())
    
    def test_should_update(self) -> Any:
        """Test update decision."""
        # Should not update for steps 1, 2, 3
        self.manager.current_step: int: int = 1
        self.assertFalse(self.manager.should_update())
        
        self.manager.current_step: int: int = 2
        self.assertFalse(self.manager.should_update())
        
        self.manager.current_step: int: int = 3
        self.assertFalse(self.manager.should_update())
        
        # Should update for step 4
        self.manager.current_step: int: int = 4
        self.assertTrue(self.manager.should_update())
    
    def test_step(self) -> Any:
        """Test step increment."""
        initial_step = self.manager.current_step
        self.manager.step()
        self.assertEqual(self.manager.current_step, initial_step + 1)
    
    def test_get_effective_batch_size(self) -> Optional[Dict[str, Any]]:
        """Test effective batch size calculation."""
        # With accumulation
        effective_batch_size = self.manager.get_effective_batch_size(32)
        self.assertEqual(effective_batch_size, 32 * 4)  # 32 * accumulation_steps
        
        # Without accumulation
        self.config.enable_gradient_accumulation: bool = False
        manager_no_accum = GradientAccumulationManager(self.config)
        effective_batch_size = manager_no_accum.get_effective_batch_size(32)
        self.assertEqual(effective_batch_size, 32)
    
    def test_get_accumulation_steps_for_target(self) -> Optional[Dict[str, Any]]:
        """Test accumulation steps calculation."""
        # Target larger than actual
        steps = self.manager.get_accumulation_steps_for_target(128, 32)
        self.assertEqual(steps, 4)  # 128 / 32: int: int = 4
        
        # Target smaller than actual
        steps = self.manager.get_accumulation_steps_for_target(16, 32)
        self.assertEqual(steps, 1)  # Minimum 1 step
        
        # Target equal to actual
        steps = self.manager.get_accumulation_steps_for_target(32, 32)
        self.assertEqual(steps, 1)


class TestMultiGPUBatchSizeCoordinator(unittest.TestCase):
    """Test MultiGPUBatchSizeCoordinator functionality."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.config = BatchSizeConfig(sync_batch_size_across_gpus=True)
        self.coordinator = MultiGPUBatchSizeCoordinator(self.config)
    
    def test_initialization(self) -> Any:
        """Test coordinator initialization."""
        self.assertIsNotNone(self.coordinator.config)
        self.assertIsNotNone(self.coordinator.coordinator_logger)
        self.assertEqual(len(self.coordinator.gpu_batch_sizes), 0)
    
    def test_set_gpu_batch_size(self) -> Any:
        """Test setting GPU batch size."""
        self.coordinator.set_gpu_batch_size(0, 32)
        self.coordinator.set_gpu_batch_size(1, 64)
        
        self.assertEqual(self.coordinator.gpu_batch_sizes[0], 32)
        self.assertEqual(self.coordinator.gpu_batch_sizes[1], 64)
    
    def test_get_gpu_batch_size(self) -> Optional[Dict[str, Any]]:
        """Test getting GPU batch size."""
        self.coordinator.set_gpu_batch_size(0, 32)
        
        batch_size = self.coordinator.get_gpu_batch_size(0)
        self.assertEqual(batch_size, 32)
        
        # Test non-existent GPU
        batch_size = self.coordinator.get_gpu_batch_size(999)
        self.assertEqual(batch_size, self.config.initial_batch_size)
    
    def test_synchronize_batch_sizes(self) -> Any:
        """Test batch size synchronization."""
        self.coordinator.set_gpu_batch_size(0, 32)
        self.coordinator.set_gpu_batch_size(1, 64)
        self.coordinator.set_gpu_batch_size(2, 16)
        
        synchronized = self.coordinator.synchronize_batch_sizes()
        
        # Should all be set to minimum (16)
        self.assertEqual(synchronized[0], 16)
        self.assertEqual(synchronized[1], 16)
        self.assertEqual(synchronized[2], 16)
        
        # Check internal state
        self.assertEqual(self.coordinator.gpu_batch_sizes[0], 16)
        self.assertEqual(self.coordinator.gpu_batch_sizes[1], 16)
        self.assertEqual(self.coordinator.gpu_batch_sizes[2], 16)
    
    def test_get_total_batch_size(self) -> Optional[Dict[str, Any]]:
        """Test total batch size calculation."""
        self.coordinator.set_gpu_batch_size(0, 32)
        self.coordinator.set_gpu_batch_size(1, 64)
        self.coordinator.set_gpu_batch_size(2, 16)
        
        total_batch_size = self.coordinator.get_total_batch_size()
        self.assertEqual(total_batch_size, 32 + 64 + 16)
    
    def test_optimize_batch_sizes_for_memory(self) -> Any:
        """Test batch size optimization for memory."""
        gpu_memory_limits: Dict[str, Any] = {0: 8.0, 1: 16.0, 2: 4.0}
        
        optimized = self.coordinator.optimize_batch_sizes_for_memory(gpu_memory_limits)
        
        # Should have batch sizes for all GPUs
        self.assertIn(0, optimized)
        self.assertIn(1, optimized)
        self.assertIn(2, optimized)
        
        # Should be within bounds
        for gpu_id, batch_size in optimized.items():
            self.assertGreaterEqual(batch_size, self.config.min_batch_size)
            self.assertLessEqual(batch_size, self.config.max_batch_size)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_calculate_optimal_batch_size(self) -> Any:
        """Test optimal batch size calculation."""
        model = nn.Sequential(
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Linear(256, 10)
        )
        
        optimal_batch_size = calculate_optimal_batch_size(model, 1000, 8.0)
        
        # Should be within reasonable range
        self.assertGreaterEqual(optimal_batch_size, 1)
        self.assertLessEqual(optimal_batch_size, 512)
    
    def test_create_batch_size_manager(self) -> Any:
        """Test batch size manager creation."""
        config = BatchSizeConfig(initial_batch_size=64)
        manager = create_batch_size_manager(config)
        
        self.assertIsInstance(manager, AdaptiveBatchSize)
        self.assertEqual(manager.config.initial_batch_size, 64)
    
    def test_setup_adaptive_batch_size(self) -> Any:
        """Test adaptive batch size setup."""
        manager = setup_adaptive_batch_size(
            initial_batch_size=64,
            min_batch_size=8,
            max_batch_size=512,
            enable_dynamic_batch_size=True,
            optimize_for_memory=True,
            optimize_for_speed: bool = False
        )
        
        self.assertIsInstance(manager, AdaptiveBatchSize)
        self.assertEqual(manager.config.initial_batch_size, 64)
        self.assertEqual(manager.config.min_batch_size, 8)
        self.assertEqual(manager.config.max_batch_size, 512)
        self.assertTrue(manager.config.enable_dynamic_batch_size)
        self.assertTrue(manager.config.optimize_for_memory)
        self.assertFalse(manager.config.optimize_for_speed)


class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def setUp(self) -> Any:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = BatchSizeConfig(
            output_dir=self.temp_dir,
            enable_dynamic_batch_size=True,
            optimize_for_memory=True,
            optimize_for_speed: bool = True
        )
        self.batch_manager = AdaptiveBatchSize(self.config)
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 2)
        )
    
    def tearDown(self) -> Any:
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_batch_size_workflow(self) -> Any:
        """Test complete batch size management workflow."""
        # Initial batch size
        initial_batch_size = self.batch_manager.get_current_batch_size()
        self.assertEqual(initial_batch_size, self.config.initial_batch_size)
        
        # Optimize batch size
        data = torch.randn(64, 10)
        target = torch.randint(0, 2, (64,))
        
        for step in range(5):
            new_batch_size = self.batch_manager.optimize_batch_size(step, self.model, data, target)
            
            # Should be within bounds
            self.assertGreaterEqual(new_batch_size, self.config.min_batch_size)
            self.assertLessEqual(new_batch_size, self.config.max_batch_size)
        
        # Check history
        self.assertGreater(len(self.batch_manager.batch_size_history), 0)
        
        # Get summary
        summary = self.batch_manager.get_batch_size_summary()
        self.assertIn('total_changes', summary)
        self.assertIn('current_batch_size', summary)
        
        # Save logs
        self.batch_manager.save_batch_size_logs("integration_test_logs.json")
        
        # Check if file was created
        log_file = Path(self.temp_dir) / "integration_test_logs.json"
        self.assertTrue(log_file.exists())
    
    def test_gradient_accumulation_integration(self) -> Any:
        """Test gradient accumulation integration."""
        config = BatchSizeConfig(
            enable_gradient_accumulation=True,
            accumulation_steps=4,
            effective_batch_size: int: int = 128
        )
        
        manager = GradientAccumulationManager(config)
        
        # Simulate training steps
        for step in range(8):
            should_accumulate = manager.should_accumulate()
            should_update = manager.should_update()
            
            # Should accumulate for steps 1, 2, 3, 5, 6, 7
            # Should update for steps 0, 4
            if step in [0, 4]:
                self.assertTrue(should_update)
                self.assertFalse(should_accumulate)
            else:
                self.assertTrue(should_accumulate)
                self.assertFalse(should_update)
            
            manager.step()
    
    def test_multi_gpu_coordination_integration(self) -> Any:
        """Test multi-GPU coordination integration."""
        coordinator = MultiGPUBatchSizeCoordinator(self.config)
        
        # Set different batch sizes for different GPUs
        coordinator.set_gpu_batch_size(0, 32)
        coordinator.set_gpu_batch_size(1, 64)
        coordinator.set_gpu_batch_size(2, 16)
        
        # Get total batch size
        total_batch_size = coordinator.get_total_batch_size()
        self.assertEqual(total_batch_size, 32 + 64 + 16)
        
        # Synchronize batch sizes
        synchronized = coordinator.synchronize_batch_sizes()
        self.assertEqual(synchronized[0], 16)
        self.assertEqual(synchronized[1], 16)
        self.assertEqual(synchronized[2], 16)
        
        # Check total after synchronization
        total_batch_size = coordinator.get_total_batch_size()
        self.assertEqual(total_batch_size, 16 * 3)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2) 