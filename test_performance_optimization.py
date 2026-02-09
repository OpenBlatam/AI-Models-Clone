#!/usr/bin/env python3
"""
Comprehensive test suite for performance optimization features.
Tests all components: MemoryManager, BatchProcessor, ModelOptimizer, 
PerformanceMonitor, CacheManager, and PerformanceOptimizer.
"""

import unittest
import torch
import torch.nn as nn
import numpy as np
import time
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the performance optimization classes
from enhanced_ui_demos_with_validation import (
    PerformanceConfig, MemoryManager, BatchProcessor, ModelOptimizer,
    PerformanceMonitor, CacheManager, PerformanceOptimizer
)

class TestPerformanceConfig(unittest.TestCase):
    """Test PerformanceConfig dataclass."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = PerformanceConfig()
        
        # Memory management defaults
        self.assertTrue(config.enable_memory_optimization)
        self.assertEqual(config.max_memory_usage_mb, 2048.0)
        self.assertTrue(config.enable_garbage_collection)
        self.assertEqual(config.memory_cleanup_threshold, 0.8)
        
        # Batch processing defaults
        self.assertTrue(config.enable_batch_processing)
        self.assertEqual(config.default_batch_size, 32)
        self.assertEqual(config.max_batch_size, 128)
        self.assertTrue(config.enable_parallel_processing)
        self.assertEqual(config.max_workers, 4)
        
        # Model optimization defaults
        self.assertTrue(config.enable_model_optimization)
        self.assertTrue(config.enable_mixed_precision)
        self.assertFalse(config.enable_torch_compile)
        self.assertFalse(config.enable_quantization)
        self.assertFalse(config.enable_pruning)
        
        # Performance monitoring defaults
        self.assertTrue(config.enable_performance_monitoring)
        self.assertEqual(config.performance_history_size, 1000)
        self.assertTrue(config.enable_real_time_monitoring)
        self.assertEqual(config.monitoring_interval, 1.0)
        
        # Caching defaults
        self.assertTrue(config.enable_caching)
        self.assertEqual(config.cache_size_limit, 100)
        self.assertEqual(config.cache_ttl_seconds, 3600)
        self.assertFalse(config.enable_disk_caching)
        self.assertEqual(config.cache_directory, "./cache")
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = PerformanceConfig(
            enable_memory_optimization=False,
            max_memory_usage_mb=4096.0,
            enable_batch_processing=False,
            default_batch_size=64,
            enable_model_optimization=False,
            enable_caching=False
        )
        
        self.assertFalse(config.enable_memory_optimization)
        self.assertEqual(config.max_memory_usage_mb, 4096.0)
        self.assertFalse(config.enable_batch_processing)
        self.assertEqual(config.default_batch_size, 64)
        self.assertFalse(config.enable_model_optimization)
        self.assertFalse(config.enable_caching)

class TestMemoryManager(unittest.TestCase):
    """Test MemoryManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PerformanceConfig(
            enable_memory_optimization=True,
            max_memory_usage_mb=1024.0,
            enable_real_time_monitoring=False  # Disable for testing
        )
        self.memory_manager = MemoryManager(self.config)
    
    def test_initialization(self):
        """Test MemoryManager initialization."""
        self.assertIsNotNone(self.memory_manager)
        self.assertEqual(self.memory_manager.config, self.config)
        self.assertEqual(len(self.memory_manager.memory_pool), 0)
        self.assertEqual(len(self.memory_manager.memory_usage_history), 0)
    
    def test_get_current_memory_usage(self):
        """Test memory usage detection."""
        memory_usage = self.memory_manager._get_current_memory_usage()
        self.assertIsInstance(memory_usage, float)
        self.assertGreaterEqual(memory_usage, 0.0)
    
    def test_memory_allocation_safety(self):
        """Test memory allocation safety checks."""
        # Test safe allocation
        safe = self.memory_manager.allocate_memory(100.0, "test")
        self.assertTrue(safe)
        
        # Test unsafe allocation (exceeds limit)
        unsafe = self.memory_manager.allocate_memory(2000.0, "test")
        self.assertFalse(unsafe)
    
    def test_memory_optimization(self):
        """Test memory optimization functionality."""
        # Mock GPU availability
        with patch('torch.cuda.is_available', return_value=False):
            self.memory_manager._optimize_memory()
            # Should complete without errors
    
    def test_memory_stats(self):
        """Test memory statistics generation."""
        stats = self.memory_manager.get_memory_stats()
        
        self.assertIn('current_memory_mb', stats)
        self.assertIn('max_memory_mb', stats)
        self.assertIn('memory_usage_percent', stats)
        self.assertIn('pool_size', stats)
        self.assertIn('history_size', stats)
        self.assertIn('gpu_available', stats)
        self.assertIn('optimization_enabled', stats)
        
        self.assertIsInstance(stats['current_memory_mb'], float)
        self.assertIsInstance(stats['max_memory_mb'], float)
        self.assertIsInstance(stats['memory_usage_percent'], float)

class TestBatchProcessor(unittest.TestCase):
    """Test BatchProcessor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PerformanceConfig(
            enable_batch_processing=True,
            enable_parallel_processing=True,
            max_workers=2
        )
        self.batch_processor = BatchProcessor(self.config)
    
    def test_initialization(self):
        """Test BatchProcessor initialization."""
        self.assertIsNotNone(self.batch_processor)
        self.assertEqual(self.batch_processor.config, self.config)
    
    def test_batch_processing_disabled(self):
        """Test batch processing when disabled."""
        config = PerformanceConfig(enable_batch_processing=False)
        processor = BatchProcessor(config)
        
        data = list(range(10))
        results = processor.process_batch(data, lambda x: x * 2)
        
        self.assertEqual(len(results), 10)
        self.assertEqual(results, [x * 2 for x in data])
    
    def test_batch_processing_enabled(self):
        """Test batch processing when enabled."""
        data = list(range(100))
        results = self.batch_processor.process_batch(data, lambda x: x * 2)
        
        self.assertEqual(len(results), 100)
        self.assertEqual(results, [x * 2 for x in data])
    
    def test_custom_batch_size(self):
        """Test custom batch size processing."""
        data = list(range(50))
        results = self.batch_processor.process_batch(data, lambda x: x * 2, batch_size=10)
        
        self.assertEqual(len(results), 50)
        self.assertEqual(results, [x * 2 for x in data])
    
    def test_batch_size_limits(self):
        """Test batch size limits."""
        data = list(range(200))
        # Should respect max_batch_size limit
        results = self.batch_processor.process_batch(data, lambda x: x * 2, batch_size=200)
        
        self.assertEqual(len(results), 200)
        self.assertEqual(results, [x * 2 for x in data])
    
    def test_cleanup(self):
        """Test BatchProcessor cleanup."""
        self.batch_processor.cleanup()
        # Should complete without errors

class TestModelOptimizer(unittest.TestCase):
    """Test ModelOptimizer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PerformanceConfig(
            enable_model_optimization=True,
            enable_mixed_precision=True,
            enable_torch_compile=False,
            enable_quantization=False,
            enable_pruning=False
        )
        self.model_optimizer = ModelOptimizer(self.config)
        
        # Create a simple test model
        self.test_model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )
    
    def test_initialization(self):
        """Test ModelOptimizer initialization."""
        self.assertIsNotNone(self.model_optimizer)
        self.assertEqual(self.model_optimizer.config, self.config)
        self.assertEqual(len(self.model_optimizer.optimized_models), 0)
    
    def test_model_optimization_disabled(self):
        """Test model optimization when disabled."""
        config = PerformanceConfig(enable_model_optimization=False)
        optimizer = ModelOptimizer(config)
        
        optimized_model = optimizer.optimize_model(self.test_model, "test")
        self.assertEqual(optimized_model, self.test_model)
    
    def test_mixed_precision_optimization(self):
        """Test mixed precision optimization."""
        optimized_model = self.model_optimizer.optimize_model(self.test_model, "test")
        
        # Check if model was stored
        self.assertIn("test", self.model_optimizer.optimized_models)
        
        # Check if mixed precision was applied
        for param in optimized_model.parameters():
            self.assertEqual(param.dtype, torch.float16)
    
    def test_torch_compile_optimization(self):
        """Test torch compile optimization."""
        config = PerformanceConfig(
            enable_model_optimization=True,
            enable_torch_compile=True
        )
        optimizer = ModelOptimizer(config)
        
        # Mock torch.compile availability
        with patch('torch.compile', return_value=self.test_model):
            optimized_model = optimizer.optimize_model(self.test_model, "test")
            self.assertIn("test", optimizer.optimized_models)
    
    def test_quantization_optimization(self):
        """Test quantization optimization."""
        config = PerformanceConfig(
            enable_model_optimization=True,
            enable_quantization=True
        )
        optimizer = ModelOptimizer(config)
        
        # Mock CUDA availability (should use CPU quantization)
        with patch('torch.cuda.is_available', return_value=False):
            with patch('torch.quantization.quantize_dynamic', return_value=self.test_model):
                optimized_model = optimizer.optimize_model(self.test_model, "test")
                self.assertIn("test", optimizer.optimized_models)
    
    def test_pruning_optimization(self):
        """Test pruning optimization."""
        config = PerformanceConfig(
            enable_model_optimization=True,
            enable_pruning=True
        )
        optimizer = ModelOptimizer(config)
        
        # Mock pruning functions
        with patch('torch.nn.utils.prune.random_unstructured'):
            optimized_model = optimizer.optimize_model(self.test_model, "test")
            self.assertIn("test", optimizer.optimized_models)
    
    def test_optimization_stats(self):
        """Test optimization statistics generation."""
        stats = self.model_optimizer.get_optimization_stats()
        
        self.assertIn('optimized_models_count', stats)
        self.assertIn('mixed_precision_enabled', stats)
        self.assertIn('torch_compile_enabled', stats)
        self.assertIn('quantization_enabled', stats)
        self.assertIn('pruning_enabled', stats)
        
        self.assertEqual(stats['mixed_precision_enabled'], True)
        self.assertEqual(stats['torch_compile_enabled'], False)

class TestPerformanceMonitor(unittest.TestCase):
    """Test PerformanceMonitor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PerformanceConfig(
            enable_performance_monitoring=True,
            performance_history_size=100
        )
        self.monitor = PerformanceMonitor(self.config)
    
    def test_initialization(self):
        """Test PerformanceMonitor initialization."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.config, self.config)
        self.assertEqual(len(self.monitor.performance_history), 0)
        self.assertIn('inference_times', self.monitor.metrics)
        self.assertIn('memory_usage', self.monitor.metrics)
        self.assertIn('throughput', self.monitor.metrics)
        self.assertIn('error_rates', self.monitor.metrics)
    
    def test_metric_recording(self):
        """Test metric recording functionality."""
        # Record some test metrics
        self.monitor.record_metric('inference_times', 0.5, {'model': 'test'})
        self.monitor.record_metric('memory_usage', 100.0, {'operation': 'test'})
        self.monitor.record_metric('throughput', 1000.0, {'unit': 'ops/sec'})
        
        # Check if metrics were recorded
        self.assertEqual(len(self.monitor.performance_history), 3)
        self.assertEqual(len(self.monitor.metrics['inference_times']), 1)
        self.assertEqual(len(self.monitor.metrics['memory_usage']), 1)
        self.assertEqual(len(self.monitor.metrics['throughput']), 1)
        
        # Check metric values
        self.assertEqual(self.monitor.metrics['inference_times'][0], 0.5)
        self.assertEqual(self.monitor.metrics['memory_usage'][0], 100.0)
        self.assertEqual(self.monitor.metrics['throughput'][0], 1000.0)
    
    def test_history_size_limiting(self):
        """Test performance history size limiting."""
        # Add more metrics than the limit
        for i in range(150):
            self.monitor.record_metric('test_metric', float(i))
        
        # Check if history is limited
        self.assertLessEqual(len(self.monitor.performance_history), self.config.performance_history_size)
        self.assertLessEqual(len(self.monitor.metrics['test_metric']), self.config.performance_history_size)
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        # Add some test metrics
        for i in range(10):
            self.monitor.record_metric('test_metric', float(i))
        
        summary = self.monitor.get_performance_summary()
        
        self.assertIn('uptime_seconds', summary)
        self.assertIn('total_metrics_recorded', summary)
        self.assertIn('metrics_by_type', summary)
        
        self.assertEqual(summary['total_metrics_recorded'], 10)
        self.assertIn('test_metric', summary['metrics_by_type'])
        
        metric_stats = summary['metrics_by_type']['test_metric']
        self.assertEqual(metric_stats['count'], 10)
        self.assertEqual(metric_stats['min'], 0.0)
        self.assertEqual(metric_stats['max'], 9.0)
        self.assertEqual(metric_stats['latest'], 9.0)
    
    def test_performance_chart_creation(self):
        """Test performance chart creation."""
        # Add some test metrics
        for i in range(5):
            self.monitor.record_metric('test_metric', float(i))
        
        fig = self.monitor.create_performance_chart()
        
        # Check if chart was created
        self.assertIsNotNone(fig)
        # Basic chart validation
        self.assertTrue(hasattr(fig, 'data'))
        self.assertTrue(hasattr(fig, 'layout'))

class TestCacheManager(unittest.TestCase):
    """Test CacheManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = PerformanceConfig(
            enable_caching=True,
            cache_size_limit=10,
            cache_ttl_seconds=60,
            enable_disk_caching=True,
            cache_directory=self.temp_dir
        )
        self.cache_manager = CacheManager(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test CacheManager initialization."""
        self.assertIsNotNone(self.cache_manager)
        self.assertEqual(self.cache_manager.config, self.config)
        self.assertEqual(len(self.cache_manager.memory_cache), 0)
        self.assertEqual(self.cache_manager.cache_stats['hits'], 0)
        self.assertEqual(self.cache_manager.cache_stats['misses'], 0)
        self.assertEqual(self.cache_manager.cache_stats['evictions'], 0)
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.cache_manager._generate_cache_key("test", "value")
        key2 = self.cache_manager._generate_cache_key("test", "value")
        key3 = self.cache_manager._generate_cache_key("test", "different")
        
        # Same inputs should generate same keys
        self.assertEqual(key1, key2)
        # Different inputs should generate different keys
        self.assertNotEqual(key1, key3)
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        # Set cache item
        success = self.cache_manager.set("test_key", "test_value")
        self.assertTrue(success)
        
        # Get cache item
        value = self.cache_manager.get("test_key")
        self.assertEqual(value, "test_value")
        
        # Check cache stats
        self.assertEqual(self.cache_manager.cache_stats['hits'], 1)
        self.assertEqual(self.cache_manager.cache_stats['misses'], 0)
    
    def test_cache_miss(self):
        """Test cache miss behavior."""
        value = self.cache_manager.get("nonexistent_key", "default")
        self.assertEqual(value, "default")
        
        # Check cache stats
        self.assertEqual(self.cache_manager.cache_stats['hits'], 0)
        self.assertEqual(self.cache_manager.cache_stats['misses'], 1)
    
    def test_cache_expiration(self):
        """Test cache item expiration."""
        # Set cache item with short TTL
        self.cache_manager.set("test_key", "test_value", ttl_seconds=0.1)
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Try to get expired item
        value = self.cache_manager.get("test_key")
        self.assertIsNone(value)
    
    def test_cache_size_limiting(self):
        """Test cache size limiting."""
        # Add more items than the cache limit
        for i in range(15):
            self.cache_manager.set(f"key_{i}", f"value_{i}")
        
        # Check if cache size is limited
        self.assertLessEqual(len(self.cache_manager.memory_cache), self.config.cache_size_limit)
        
        # Check if evictions occurred
        self.assertGreater(self.cache_manager.cache_stats['evictions'], 0)
    
    def test_disk_caching(self):
        """Test disk caching functionality."""
        # Set cache item
        self.cache_manager.set("disk_key", "disk_value")
        
        # Check if file was created
        cache_file = Path(self.temp_dir) / f"{self.cache_manager._generate_cache_key('disk_key')}.pkl"
        self.assertTrue(cache_file.exists())
    
    def test_cache_statistics(self):
        """Test cache statistics generation."""
        # Add some cache operations
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        self.cache_manager.get("key1")  # Hit
        self.cache_manager.get("key3")  # Miss
        
        stats = self.cache_manager.get_cache_stats()
        
        self.assertIn('memory_cache_size', stats)
        self.assertIn('cache_size_limit', stats)
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('evictions', stats)
        self.assertIn('hit_rate_percent', stats)
        self.assertIn('total_requests', stats)
        self.assertIn('disk_caching_enabled', stats)
        
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['total_requests'], 2)
        self.assertEqual(stats['hit_rate_percent'], 50.0)
    
    def test_cache_cleanup(self):
        """Test cache cleanup functionality."""
        # Add some items
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        
        # Clear cache
        self.cache_manager.clear_cache()
        
        # Check if cache is empty
        self.assertEqual(len(self.cache_manager.memory_cache), 0)
        self.assertEqual(self.cache_manager.cache_stats['hits'], 0)
        self.assertEqual(self.cache_manager.cache_stats['misses'], 0)
        self.assertEqual(self.cache_manager.cache_stats['evictions'], 0)

class TestPerformanceOptimizer(unittest.TestCase):
    """Test PerformanceOptimizer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PerformanceConfig(
            enable_memory_optimization=True,
            enable_batch_processing=True,
            enable_model_optimization=True,
            enable_caching=True,
            enable_performance_monitoring=True
        )
        self.optimizer = PerformanceOptimizer(self.config)
        
        # Create a simple test model
        self.test_model = nn.Sequential(
            nn.Linear(5, 10),
            nn.ReLU(),
            nn.Linear(10, 3)
        )
        
        # Create test data
        self.test_data = torch.randn(10, 5)
    
    def test_initialization(self):
        """Test PerformanceOptimizer initialization."""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.config, self.config)
        
        # Check if all components are initialized
        self.assertIsNotNone(self.optimizer.memory_manager)
        self.assertIsNotNone(self.optimizer.batch_processor)
        self.assertIsNotNone(self.optimizer.model_optimizer)
        self.assertIsNotNone(self.optimizer.performance_monitor)
        self.assertIsNotNone(self.optimizer.cache_manager)
    
    def test_optimized_inference(self):
        """Test optimized inference functionality."""
        output, optimization_info = self.optimizer.optimize_inference(
            self.test_model, self.test_data, "test_model"
        )
        
        # Check output
        self.assertIsNotNone(output)
        self.assertEqual(output.shape, (10, 3))
        
        # Check optimization info
        self.assertIn('cached', optimization_info)
        self.assertIn('optimization_applied', optimization_info)
        self.assertIn('inference_time', optimization_info)
        self.assertIn('memory_delta_mb', optimization_info)
        self.assertIn('model_optimizations', optimization_info)
        self.assertIn('cache_stats', optimization_info)
        
        # Check if optimization was applied
        self.assertTrue(optimization_info['optimization_applied'])
    
    def test_cached_inference(self):
        """Test cached inference functionality."""
        # First inference (should not be cached)
        output1, info1 = self.optimizer.optimize_inference(
            self.test_model, self.test_data, "test_model"
        )
        
        # Second inference with same data (should be cached)
        output2, info2 = self.optimizer.optimize_inference(
            self.test_model, self.test_data, "test_model"
        )
        
        # Check if second inference was cached
        self.assertTrue(info2['cached'])
        
        # Check if outputs are the same
        torch.testing.assert_close(output1, output2)
    
    def test_memory_allocation_failure(self):
        """Test memory allocation failure handling."""
        # Create large data that exceeds memory limit
        large_data = torch.randn(10000, 10000)  # Very large tensor
        
        with self.assertRaises(MemoryError):
            self.optimizer.optimize_inference(
                self.test_model, large_data, "test_model"
            )
    
    def test_performance_report(self):
        """Test performance report generation."""
        # Run some inference operations
        self.optimizer.optimize_inference(self.test_model, self.test_data, "test_model")
        
        # Get performance report
        report = self.optimizer.get_performance_report()
        
        self.assertIn('memory_stats', report)
        self.assertIn('performance_summary', report)
        self.assertIn('cache_stats', report)
        self.assertIn('optimization_stats', report)
        self.assertIn('configuration', report)
        
        # Check configuration
        config = report['configuration']
        self.assertEqual(config['memory_optimization'], True)
        self.assertEqual(config['batch_processing'], True)
        self.assertEqual(config['model_optimization'], True)
        self.assertEqual(config['caching'], True)
    
    def test_cleanup(self):
        """Test PerformanceOptimizer cleanup."""
        self.optimizer.cleanup()
        # Should complete without errors

class TestIntegration(unittest.TestCase):
    """Test integration between performance optimization components."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PerformanceConfig(
            enable_memory_optimization=True,
            enable_batch_processing=True,
            enable_model_optimization=True,
            enable_caching=True,
            enable_performance_monitoring=True
        )
        self.optimizer = PerformanceOptimizer(self.config)
    
    def test_end_to_end_optimization(self):
        """Test end-to-end performance optimization workflow."""
        # Create test model and data
        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )
        
        data = torch.randn(50, 10)
        
        # Run optimized inference
        output, info = self.optimizer.optimize_inference(model, data, "integration_test")
        
        # Verify output
        self.assertIsNotNone(output)
        self.assertEqual(output.shape, (50, 5))
        
        # Verify optimization was applied
        self.assertTrue(info['optimization_applied'])
        
        # Verify performance monitoring
        report = self.optimizer.get_performance_report()
        self.assertGreater(report['performance_summary']['total_metrics_recorded'], 0)
        
        # Verify caching
        cache_stats = report['cache_stats']
        self.assertGreater(cache_stats['total_requests'], 0)
        
        # Verify model optimization
        opt_stats = report['optimization_stats']
        self.assertGreaterEqual(opt_stats['optimized_models_count'], 0)
    
    def test_memory_optimization_integration(self):
        """Test memory optimization integration."""
        # Create multiple models to test memory management
        models = []
        for i in range(5):
            model = nn.Sequential(
                nn.Linear(100, 200),
                nn.ReLU(),
                nn.Linear(200, 100)
            )
            models.append(model)
        
        # Run inference on all models
        for i, model in enumerate(models):
            data = torch.randn(10, 100)
            output, info = self.optimizer.optimize_inference(model, data, f"model_{i}")
            self.assertIsNotNone(output)
        
        # Check memory stats
        memory_stats = self.optimizer.memory_manager.get_memory_stats()
        self.assertIsNotNone(memory_stats['current_memory_mb'])
        self.assertIsNotNone(memory_stats['memory_usage_percent'])
    
    def test_batch_processing_integration(self):
        """Test batch processing integration."""
        # Create large dataset
        large_data = torch.randn(200, 10)
        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )
        
        # Run inference with batching
        output, info = self.optimizer.optimize_inference(model, large_data, "batch_test")
        
        # Verify output
        self.assertIsNotNone(output)
        self.assertEqual(output.shape, (200, 5))
        
        # Check if batching was used
        self.assertTrue(self.config.enable_batch_processing)

def run_performance_tests():
    """Run all performance optimization tests."""
    print("🚀 Running Performance Optimization Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPerformanceConfig,
        TestMemoryManager,
        TestBatchProcessor,
        TestModelOptimizer,
        TestPerformanceMonitor,
        TestCacheManager,
        TestPerformanceOptimizer,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n⚠️ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ All tests passed successfully!")
        return True
    else:
        print(f"\n❌ Some tests failed!")
        return False

if __name__ == "__main__":
    # Run tests
    success = run_performance_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)
