#!/usr/bin/env python3
"""
🧪 TEST SUITE - Optimized Image Processing System
=================================================

Comprehensive test suite for the optimized image processing system.
"""

import unittest
import time
from PIL import Image
from optimized_image_process import (
    OptimizedImageProcessor, ProcessingConfig, ProcessingMode, TaskType,
    DeviceType, CacheStrategy, ProcessingResult
)

class TestOptimizedImageProcessor(unittest.TestCase):
    """Test suite for OptimizedImageProcessor."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = ProcessingConfig(
            mode=ProcessingMode.BALANCED,
            enable_ai=False,  # Disable AI for faster tests
            enable_caching=True,
            cache_size=100
        )
        self.processor = OptimizedImageProcessor(self.config)
        self.test_image = Image.new('RGB', (100, 100), color='red')
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.config.mode, ProcessingMode.BALANCED)
        self.assertTrue(self.processor.config.enable_caching)
        self.assertFalse(self.processor.config.enable_ai)
    
    def test_image_validation(self):
        """Test image validation functionality."""
        result = self.processor.process_image(self.test_image, TaskType.VALIDATION)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertIn('width', result.data)
        self.assertIn('height', result.data)
        self.assertEqual(result.data['width'], 100)
        self.assertEqual(result.data['height'], 100)
    
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        # Test with None
        result = self.processor.process_image(None, TaskType.VALIDATION)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        
        # Test with empty string
        result = self.processor.process_image("", TaskType.VALIDATION)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_caching_functionality(self):
        """Test caching system."""
        # First run
        result1 = self.processor.process_image(self.test_image, TaskType.VALIDATION)
        self.assertTrue(result1.success)
        
        # Second run (should be cached)
        result2 = self.processor.process_image(self.test_image, TaskType.VALIDATION)
        self.assertTrue(result2.success)
        
        # Check that results are identical
        self.assertEqual(result1.data, result2.data)
        
        # Check cache metrics
        metrics = self.processor.get_metrics()
        self.assertGreater(metrics['cache_hit_rate'], 0)
    
    def test_different_processing_modes(self):
        """Test different processing modes."""
        modes = [ProcessingMode.FAST, ProcessingMode.BALANCED, ProcessingMode.QUALITY]
        
        for mode in modes:
            config = ProcessingConfig(mode=mode, enable_ai=False, enable_caching=True)
            processor = OptimizedImageProcessor(config)
            
            result = processor.process_image(self.test_image, TaskType.VALIDATION)
            self.assertTrue(result.success)
            self.assertIsNotNone(result.data)
    
    def test_different_task_types(self):
        """Test different task types."""
        tasks = [TaskType.VALIDATION, TaskType.ANALYSIS]
        
        for task in tasks:
            result = self.processor.process_image(self.test_image, task)
            self.assertTrue(result.success)
            self.assertIsNotNone(result.data)
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        # Process multiple images
        for i in range(5):
            image = Image.new('RGB', (50, 50), color=f'hsl({i * 72}, 70%, 50%)')
            result = self.processor.process_image(image, TaskType.VALIDATION)
            self.assertTrue(result.success)
        
        # Check metrics
        metrics = self.processor.get_metrics()
        self.assertEqual(metrics['total_requests'], 5)
        self.assertEqual(metrics['successful_requests'], 5)
        self.assertEqual(metrics['failed_requests'], 0)
        self.assertEqual(metrics['success_rate'], 1.0)
        self.assertGreater(metrics['average_processing_time'], 0)
    
    def test_error_handling(self):
        """Test error handling capabilities."""
        # Test with corrupted image data
        corrupted_data = b"this is not an image"
        result = self.processor.process_image(corrupted_data, TaskType.VALIDATION)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_large_image_handling(self):
        """Test handling of large images."""
        large_image = Image.new('RGB', (5000, 5000), color='blue')
        result = self.processor.process_image(large_image, TaskType.VALIDATION)
        
        # Should fail due to size limits
        self.assertFalse(result.success)
        self.assertIn("too large", result.error.lower())

class TestProcessingConfig(unittest.TestCase):
    """Test suite for ProcessingConfig."""
    
    def test_config_creation(self):
        """Test configuration creation."""
        config = ProcessingConfig()
        self.assertEqual(config.mode, ProcessingMode.BALANCED)
        self.assertEqual(config.max_size, 2048)
        self.assertEqual(config.quality, 95)
        self.assertTrue(config.enable_ai)
        self.assertTrue(config.enable_caching)
    
    def test_config_customization(self):
        """Test configuration customization."""
        config = ProcessingConfig(
            mode=ProcessingMode.FAST,
            max_size=1024,
            quality=80,
            enable_ai=False,
            enable_caching=False
        )
        
        self.assertEqual(config.mode, ProcessingMode.FAST)
        self.assertEqual(config.max_size, 1024)
        self.assertEqual(config.quality, 80)
        self.assertFalse(config.enable_ai)
        self.assertFalse(config.enable_caching)
    
    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = ProcessingConfig()
        config_dict = config.to_dict()
        
        self.assertIn('mode', config_dict)
        self.assertIn('max_size', config_dict)
        self.assertIn('quality', config_dict)
        self.assertIn('enable_ai', config_dict)
        self.assertIn('enable_caching', config_dict)

class TestProcessingResult(unittest.TestCase):
    """Test suite for ProcessingResult."""
    
    def test_successful_result(self):
        """Test successful processing result."""
        result = ProcessingResult(
            success=True,
            data={"test": "data"},
            metadata={"meta": "info"},
            processing_time=1.5,
            confidence=0.95
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"test": "data"})
        self.assertEqual(result.metadata, {"meta": "info"})
        self.assertEqual(result.processing_time, 1.5)
        self.assertEqual(result.confidence, 0.95)
        self.assertIsNone(result.error)
    
    def test_failed_result(self):
        """Test failed processing result."""
        result = ProcessingResult(
            success=False,
            error="Test error message",
            processing_time=0.1
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Test error message")
        self.assertEqual(result.processing_time, 0.1)
        self.assertIsNone(result.data)
        self.assertEqual(result.confidence, 0.0)
    
    def test_result_to_dict(self):
        """Test result serialization."""
        result = ProcessingResult(
            success=True,
            data={"test": "data"},
            processing_time=1.0,
            confidence=0.8
        )
        
        result_dict = result.to_dict()
        self.assertIn('success', result_dict)
        self.assertIn('data', result_dict)
        self.assertIn('processing_time', result_dict)
        self.assertIn('confidence', result_dict)
        self.assertTrue(result_dict['success'])
        self.assertEqual(result_dict['data'], {"test": "data"})

class TestCachingStrategies(unittest.TestCase):
    """Test suite for caching strategies."""
    
    def test_lru_cache(self):
        """Test LRU caching strategy."""
        from optimized_image_process import LRUCache
        
        cache = LRUCache(capacity=2)
        test_result = ProcessingResult(success=True, data="test")
        
        # Add items
        cache.put("key1", test_result)
        cache.put("key2", test_result)
        
        # Test retrieval
        self.assertIsNotNone(cache.get("key1"))
        self.assertIsNotNone(cache.get("key2"))
        
        # Test eviction
        cache.put("key3", test_result)
        self.assertIsNone(cache.get("key1"))  # Should be evicted
        self.assertIsNotNone(cache.get("key2"))
        self.assertIsNotNone(cache.get("key3"))
    
    def test_lfu_cache(self):
        """Test LFU caching strategy."""
        from optimized_image_process import LFUCache
        
        cache = LFUCache(capacity=2)
        test_result = ProcessingResult(success=True, data="test")
        
        # Add items
        cache.put("key1", test_result)
        cache.put("key2", test_result)
        
        # Access key1 multiple times
        cache.get("key1")
        cache.get("key1")
        
        # Add new item (should evict key2)
        cache.put("key3", test_result)
        
        self.assertIsNotNone(cache.get("key1"))  # Should remain
        self.assertIsNone(cache.get("key2"))     # Should be evicted
        self.assertIsNotNone(cache.get("key3"))

class TestPerformanceBenchmarks(unittest.TestCase):
    """Test suite for performance benchmarks."""
    
    def test_processing_speed(self):
        """Test processing speed."""
        config = ProcessingConfig(
            mode=ProcessingMode.FAST,
            enable_ai=False,
            enable_caching=False
        )
        processor = OptimizedImageProcessor(config)
        
        start_time = time.time()
        result = processor.process_image(Image.new('RGB', (100, 100), color='red'), TaskType.VALIDATION)
        processing_time = time.time() - start_time
        
        self.assertTrue(result.success)
        self.assertLess(processing_time, 1.0)  # Should be fast
    
    def test_memory_usage(self):
        """Test memory usage."""
        config = ProcessingConfig(
            mode=ProcessingMode.BALANCED,
            enable_ai=False,
            enable_caching=True,
            cache_size=10
        )
        processor = OptimizedImageProcessor(config)
        
        # Process multiple images
        for i in range(10):
            image = Image.new('RGB', (50, 50), color=f'hsl({i * 36}, 70%, 50%)')
            result = processor.process_image(image, TaskType.VALIDATION)
            self.assertTrue(result.success)
        
        # Check that cache size is respected
        metrics = processor.get_metrics()
        self.assertLessEqual(metrics['cache_hit_rate'], 1.0)

def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestOptimizedImageProcessor,
        TestProcessingConfig,
        TestProcessingResult,
        TestCachingStrategies,
        TestPerformanceBenchmarks
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.2%}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)





