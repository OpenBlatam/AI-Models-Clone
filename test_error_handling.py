#!/usr/bin/env python3
"""
Test script for Gradio error handling and input validation
"""

import unittest
import numpy as np
from PIL import Image
import tempfile
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gradio_error_handling import (
        GradioInputValidator, 
        GradioErrorHandler, 
        GradioInputSanitizer,
        GradioPerformanceMonitor
    )
except ImportError as e:
    print(f"Warning: Could not import error handling modules: {e}")
    # Create mock classes for testing
    class GradioInputValidator:
        @staticmethod
        def validate_image_array(image):
            return True, "Mock validation", image
    
    class GradioErrorHandler:
        def __init__(self):
            pass
        def handle_error(self, func):
            return func
    
    class GradioInputSanitizer:
        @staticmethod
        def sanitize_image_input(image_input):
            return image_input
    
    class GradioPerformanceMonitor:
        def __init__(self):
            pass

class TestGradioErrorHandling(unittest.TestCase):
    """Test cases for Gradio error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = GradioInputValidator()
        self.error_handler = GradioErrorHandler()
        self.sanitizer = GradioInputSanitizer()
        self.performance_monitor = GradioPerformanceMonitor()
        
        # Create test image
        self.test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        self.test_pil_image = Image.fromarray(self.test_image)
    
    def test_validate_image_array_valid(self):
        """Test validation of valid image array"""
        is_valid, msg, image = self.validator.validate_image_array(self.test_image)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "Image array is valid")
        self.assertIsNotNone(image)
    
    def test_validate_image_array_none(self):
        """Test validation of None image"""
        is_valid, msg, image = self.validator.validate_image_array(None)
        self.assertFalse(is_valid)
        self.assertIn("None", msg)
        self.assertIsNone(image)
    
    def test_validate_image_array_invalid_type(self):
        """Test validation of invalid image type"""
        is_valid, msg, image = self.validator.validate_image_array("not an image")
        self.assertFalse(is_valid)
        self.assertIn("numpy array", msg)
        self.assertIsNone(image)
    
    def test_validate_image_array_too_small(self):
        """Test validation of too small image"""
        small_image = np.random.randint(0, 255, (16, 16, 3), dtype=np.uint8)
        is_valid, msg, image = self.validator.validate_image_array(small_image)
        self.assertFalse(is_valid)
        self.assertIn("too small", msg)
        self.assertIsNone(image)
    
    def test_validate_image_array_too_large(self):
        """Test validation of too large image"""
        large_image = np.random.randint(0, 255, (10000, 10000, 3), dtype=np.uint8)
        is_valid, msg, image = self.validator.validate_image_array(large_image)
        self.assertFalse(is_valid)
        self.assertIn("too large", msg)
        self.assertIsNone(image)
    
    def test_validate_pil_image_valid(self):
        """Test validation of valid PIL image"""
        is_valid, msg, image = self.validator.validate_pil_image(self.test_pil_image)
        self.assertTrue(is_valid)
        self.assertIn("converted successfully", msg)
        self.assertIsNotNone(image)
    
    def test_validate_pil_image_none(self):
        """Test validation of None PIL image"""
        is_valid, msg, image = self.validator.validate_pil_image(None)
        self.assertFalse(is_valid)
        self.assertIn("None", msg)
        self.assertIsNone(image)
    
    def test_validate_processing_config_valid(self):
        """Test validation of valid processing config"""
        config = {
            'processing_type': 'enhancement',
            'enhancement_factor': 1.5,
            'quality_threshold': 0.8,
            'batch_size': 10,
            'device': 'auto'
        }
        is_valid, msg, validated_config = self.validator.validate_processing_config(config)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "Configuration is valid")
        self.assertIsNotNone(validated_config)
    
    def test_validate_processing_config_invalid_type(self):
        """Test validation of invalid processing type"""
        config = {'processing_type': 'invalid_type'}
        is_valid, msg, validated_config = self.validator.validate_processing_config(config)
        self.assertFalse(is_valid)
        self.assertIn("Invalid processing type", msg)
        self.assertEqual(validated_config, {})
    
    def test_validate_processing_config_invalid_factor(self):
        """Test validation of invalid enhancement factor"""
        config = {'enhancement_factor': 25.0}
        is_valid, msg, validated_config = self.validator.validate_processing_config(config)
        self.assertFalse(is_valid)
        self.assertIn("between 0.1 and 20.0", msg)
        self.assertEqual(validated_config, {})
    
    def test_sanitize_image_input_numpy(self):
        """Test sanitization of numpy array input"""
        result = self.sanitizer.sanitize_image_input(self.test_image)
        self.assertIsNotNone(result)
        self.assertTrue(np.array_equal(result, self.test_image))
    
    def test_sanitize_image_input_pil(self):
        """Test sanitization of PIL image input"""
        result = self.sanitizer.sanitize_image_input(self.test_pil_image)
        self.assertIsNotNone(result)
        self.assertTrue(np.array_equal(result, self.test_image))
    
    def test_sanitize_image_input_none(self):
        """Test sanitization of None input"""
        result = self.sanitizer.sanitize_image_input(None)
        self.assertIsNone(result)
    
    def test_sanitize_config_input(self):
        """Test sanitization of config input"""
        config = {
            'string_val': '  test  ',
            'int_val': 42,
            'float_val': 3.14,
            'bool_val': True,
            'list_val': ['  item1  ', 'item2'],
            'none_val': None
        }
        result = self.sanitizer.sanitize_config_input(config)
        
        self.assertEqual(result['string_val'], 'test')
        self.assertEqual(result['int_val'], 42)
        self.assertEqual(result['float_val'], 3.14)
        self.assertEqual(result['bool_val'], True)
        self.assertEqual(result['list_val'], ['item1', 'item2'])
        self.assertNotIn('none_val', result)
    
    def test_error_handler_decorator(self):
        """Test error handler decorator"""
        @self.error_handler.handle_error
        def test_function(should_fail=False):
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # Test successful execution
        result = test_function(should_fail=False)
        self.assertEqual(result, "success")
        
        # Test error handling
        result = test_function(should_fail=True)
        self.assertIsNone(result[0])
        self.assertIn("Test error", result[1])
        self.assertIsNone(result[2])
    
    def test_error_handler_summary(self):
        """Test error handler summary"""
        @self.error_handler.handle_error
        def failing_function():
            raise RuntimeError("Test runtime error")
        
        # Trigger an error
        failing_function()
        
        # Get summary
        summary = self.error_handler.get_error_summary()
        self.assertGreater(summary['total_errors'], 0)
        self.assertIn('RuntimeError', summary['error_type_distribution'])
    
    def test_performance_monitor(self):
        """Test performance monitor"""
        @self.performance_monitor.monitor_operation("test_operation")
        def test_operation():
            import time
            time.sleep(0.1)  # Simulate work
            return "done"
        
        # Execute operation
        result = test_operation()
        self.assertEqual(result, "done")
        
        # Check performance summary
        summary = self.performance_monitor.get_performance_summary()
        self.assertIn("test_operation", summary)
        self.assertGreater(summary["test_operation"]["avg_time"], 0)

def run_tests():
    """Run all tests"""
    print("Running Gradio Error Handling Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGradioErrorHandling)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {len(result.failures)} tests failed, {len(result.errors)} tests had errors")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
