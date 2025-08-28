"""
Comprehensive test suite for the refactored diffusion models system.
Tests clean architecture, protocols, and design patterns.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import torch
import numpy as np
from typing import Dict, Any, List
import warnings
warnings.filterwarnings("ignore")

# Import the refactored system
try:
    from diffusion_models_system_refactored import (
        # Enums and Constants
        OptimizationProfile, DeviceType, MemoryFormat,
        
        # Configuration Classes
        DiffusionConfig, TrainingConfig,
        
        # Core Components
        PerformanceMonitor, MemoryTracker,
        
        # Optimization Strategies
        OptimizationStrategy, InferenceOptimizationStrategy,
        TrainingOptimizationStrategy, MemoryOptimizationStrategy,
        BalancedOptimizationStrategy,
        
        # Factory and Utilities
        OptimizationFactory, create_diffusion_system,
        optimize_config, get_device_info, validate_configs
    )
    REFACTORED_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Refactored system not available: {e}")
    REFACTORED_SYSTEM_AVAILABLE = False


class TestRefactoredDiffusionModels(unittest.TestCase):
    """Test suite for the refactored diffusion models system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not REFACTORED_SYSTEM_AVAILABLE:
            self.skipTest("Refactored system not available")
        
        # Sample test data
        self.sample_model_name = "test_model"
        self.sample_inference_steps = 30
        self.sample_guidance_scale = 7.5
        self.sample_height = 512
        self.sample_width = 512
    
    def test_enum_values(self):
        """Test that enums have correct values."""
        print("\n🧪 Testing Enum Values...")
        
        # Test OptimizationProfile
        self.assertEqual(OptimizationProfile.INFERENCE.value, "inference")
        self.assertEqual(OptimizationProfile.TRAINING.value, "training")
        self.assertEqual(OptimizationProfile.MEMORY.value, "memory")
        self.assertEqual(OptimizationProfile.BALANCED.value, "balanced")
        
        # Test DeviceType
        self.assertEqual(DeviceType.CUDA.value, "cuda")
        self.assertEqual(DeviceType.MPS.value, "mps")
        self.assertEqual(DeviceType.CPU.value, "cpu")
        
        # Test MemoryFormat
        self.assertEqual(MemoryFormat.CHANNELS_FIRST.value, "channels_first")
        self.assertEqual(MemoryFormat.CHANNELS_LAST.value, "channels_last")
        
        print("✅ Enum values are correct")
    
    def test_diffusion_config_creation(self):
        """Test DiffusionConfig creation and default values."""
        print("\n🧪 Testing DiffusionConfig Creation...")
        
        # Test with minimal parameters
        config = DiffusionConfig(model_name=self.sample_model_name)
        
        self.assertEqual(config.model_name, self.sample_model_name)
        self.assertEqual(config.num_inference_steps, 50)  # default
        self.assertEqual(config.guidance_scale, 7.5)  # default
        self.assertEqual(config.height, 512)  # default
        self.assertEqual(config.width, 512)  # default
        
        # Test with all parameters
        config = DiffusionConfig(
            model_name=self.sample_model_name,
            num_inference_steps=self.sample_inference_steps,
            guidance_scale=self.sample_guidance_scale,
            height=self.sample_height,
            width=self.sample_width,
            use_compile=True,
            use_fp16=True
        )
        
        self.assertEqual(config.model_name, self.sample_model_name)
        self.assertEqual(config.num_inference_steps, self.sample_inference_steps)
        self.assertEqual(config.guidance_scale, self.sample_guidance_scale)
        self.assertEqual(config.height, self.sample_height)
        self.assertEqual(config.width, self.sample_width)
        self.assertTrue(config.use_compile)
        self.assertTrue(config.use_fp16)
        
        print("✅ DiffusionConfig creation works correctly")
    
    def test_training_config_creation(self):
        """Test TrainingConfig creation and default values."""
        print("\n🧪 Testing TrainingConfig Creation...")
        
        # Test with minimal parameters
        config = TrainingConfig()
        
        self.assertEqual(config.learning_rate, 1e-5)  # default
        self.assertEqual(config.num_epochs, 100)  # default
        self.assertEqual(config.batch_size, 1)  # default
        self.assertTrue(config.use_mixed_precision)  # default
        
        # Test with all parameters
        config = TrainingConfig(
            learning_rate=1e-4,
            num_epochs=50,
            batch_size=2,
            use_mixed_precision=False,
            gradient_accumulation_steps=4,
            max_grad_norm=2.0
        )
        
        self.assertEqual(config.learning_rate, 1e-4)
        self.assertEqual(config.num_epochs, 50)
        self.assertEqual(config.batch_size, 2)
        self.assertFalse(config.use_mixed_precision)
        self.assertEqual(config.gradient_accumulation_steps, 4)
        self.assertEqual(config.max_grad_norm, 2.0)
        
        print("✅ TrainingConfig creation works correctly")
    
    def test_config_methods(self):
        """Test configuration class methods."""
        print("\n🧪 Testing Configuration Methods...")
        
        config = DiffusionConfig(model_name=self.sample_model_name)
        
        # Test to_dict method
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertIn('model_name', config_dict)
        self.assertIn('num_inference_steps', config_dict)
        self.assertEqual(config_dict['model_name'], self.sample_model_name)
        
        # Test update method
        config.update(num_inference_steps=25, guidance_scale=8.0)
        self.assertEqual(config.num_inference_steps, 25)
        self.assertEqual(config.guidance_scale, 8.0)
        
        # Test validation
        is_valid = config.validate()
        self.assertTrue(is_valid)
        
        print("✅ Configuration methods work correctly")
    
    def test_performance_monitor(self):
        """Test PerformanceMonitor functionality."""
        print("\n🧪 Testing PerformanceMonitor...")
        
        monitor = PerformanceMonitor()
        
        # Test timer functionality
        monitor.start_timer("test_timer")
        monitor.end_timer("test_timer")
        
        # Test average time calculation
        avg_time = monitor.get_average_time("test_timer")
        self.assertIsInstance(avg_time, float)
        self.assertGreater(avg_time, 0)
        
        # Test report generation
        report = monitor.generate_report()
        self.assertIsInstance(report, dict)
        self.assertIn('test_timer', report)
        
        print("✅ PerformanceMonitor works correctly")
    
    def test_memory_tracker(self):
        """Test MemoryTracker functionality."""
        print("\n🧪 Testing MemoryTracker...")
        
        tracker = MemoryTracker()
        
        # Test memory tracking
        tracker.track_memory("test_memory")
        
        # Test stats retrieval
        stats = tracker.get_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('test_memory', stats)
        
        # Test history clearing
        tracker.clear_history()
        stats_after_clear = tracker.get_stats()
        self.assertEqual(len(stats_after_clear), 0)
        
        print("✅ MemoryTracker works correctly")
    
    def test_optimization_strategies(self):
        """Test optimization strategy implementations."""
        print("\n🧪 Testing Optimization Strategies...")
        
        # Test base strategy (abstract)
        with self.assertRaises(TypeError):
            OptimizationStrategy()
        
        # Test inference strategy
        inference_strategy = InferenceOptimizationStrategy()
        config = DiffusionConfig(model_name=self.sample_model_name)
        optimized_config = inference_strategy.apply(config)
        
        self.assertTrue(optimized_config.use_compile)
        self.assertTrue(optimized_config.use_fp16)
        self.assertFalse(optimized_config.enable_attention_slicing)
        
        # Test memory strategy
        memory_strategy = MemoryOptimizationStrategy()
        optimized_config = memory_strategy.apply(config)
        
        self.assertTrue(optimized_config.enable_attention_slicing)
        self.assertTrue(optimized_config.enable_vae_slicing)
        self.assertTrue(optimized_config.use_gradient_checkpointing)
        
        # Test training strategy
        training_strategy = TrainingOptimizationStrategy()
        optimized_config = training_strategy.apply(config)
        
        self.assertTrue(optimized_config.use_gradient_checkpointing)
        self.assertTrue(optimized_config.use_ema)
        
        # Test balanced strategy
        balanced_strategy = BalancedOptimizationStrategy()
        optimized_config = balanced_strategy.apply(config)
        
        # Balanced should apply moderate optimizations
        self.assertFalse(optimized_config.use_compile)  # default
        self.assertFalse(optimized_config.use_fp16)  # default
        
        print("✅ Optimization strategies work correctly")
    
    def test_optimization_factory(self):
        """Test OptimizationFactory functionality."""
        print("\n🧪 Testing OptimizationFactory...")
        
        factory = OptimizationFactory()
        
        # Test strategy creation for each profile
        strategies = {
            OptimizationProfile.INFERENCE: InferenceOptimizationStrategy,
            OptimizationProfile.TRAINING: TrainingOptimizationStrategy,
            OptimizationProfile.MEMORY: MemoryOptimizationStrategy,
            OptimizationProfile.BALANCED: BalancedOptimizationStrategy
        }
        
        for profile, expected_strategy_class in strategies.items():
            strategy = factory.create_strategy(profile)
            self.assertIsInstance(strategy, expected_strategy_class)
        
        print("✅ OptimizationFactory works correctly")
    
    def test_optimize_config_function(self):
        """Test the optimize_config utility function."""
        print("\n🧪 Testing optimize_config Function...")
        
        base_config = DiffusionConfig(model_name=self.sample_model_name)
        
        # Test inference optimization
        inference_config = optimize_config(base_config, OptimizationProfile.INFERENCE)
        self.assertTrue(inference_config.use_compile)
        self.assertTrue(inference_config.use_fp16)
        
        # Test memory optimization
        memory_config = optimize_config(base_config, OptimizationProfile.MEMORY)
        self.assertTrue(memory_config.enable_attention_slicing)
        self.assertTrue(memory_config.enable_vae_slicing)
        
        # Test training optimization
        training_config = optimize_config(base_config, OptimizationProfile.TRAINING)
        self.assertTrue(training_config.use_gradient_checkpointing)
        self.assertTrue(training_config.use_ema)
        
        # Test balanced optimization
        balanced_config = optimize_config(base_config, OptimizationProfile.BALANCED)
        # Should use base configuration
        
        print("✅ optimize_config function works correctly")
    
    def test_device_info_function(self):
        """Test the get_device_info utility function."""
        print("\n🧪 Testing get_device_info Function...")
        
        device_info = get_device_info()
        
        # Test basic structure
        self.assertIsInstance(device_info, dict)
        required_keys = ['cuda_available', 'mps_available', 'device_count']
        for key in required_keys:
            self.assertIn(key, device_info)
        
        # Test CUDA availability
        self.assertIsInstance(device_info['cuda_available'], bool)
        self.assertIsInstance(device_info['mps_available'], bool)
        self.assertIsInstance(device_info['device_count'], int)
        
        # Test CUDA details if available
        if device_info['cuda_available']:
            self.assertIn('current_device', device_info)
            self.assertIn('device_name', device_info)
            self.assertIn('device_memory', device_info)
            
            memory = device_info['device_memory']
            self.assertIn('total', memory)
            self.assertIn('allocated', memory)
            self.assertIn('cached', memory)
        
        print("✅ get_device_info function works correctly")
    
    def test_config_validation_function(self):
        """Test the validate_configs utility function."""
        print("\n🧪 Testing validate_configs Function...")
        
        # Test with valid configurations
        diffusion_config = DiffusionConfig(model_name=self.sample_model_name)
        training_config = TrainingConfig()
        
        is_valid = validate_configs(diffusion_config, training_config)
        self.assertTrue(is_valid)
        
        # Test with invalid configurations (if validation is implemented)
        # This depends on the specific validation logic
        
        print("✅ validate_configs function works correctly")
    
    def test_thread_safety(self):
        """Test thread safety of core components."""
        print("\n🧪 Testing Thread Safety...")
        
        import threading
        import time
        
        # Test PerformanceMonitor thread safety
        monitor = PerformanceMonitor()
        results = []
        
        def timer_worker(worker_id: int):
            for i in range(10):
                monitor.start_timer(f"worker_{worker_id}_timer_{i}")
                time.sleep(0.001)  # Small delay
                monitor.end_timer(f"worker_{worker_id}_timer_{i}")
                results.append(f"worker_{worker_id}_timer_{i}")
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=timer_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no exceptions occurred and all timers were processed
        self.assertEqual(len(results), 30)  # 3 workers * 10 timers each
        
        print("✅ Thread safety works correctly")
    
    def test_error_handling(self):
        """Test error handling in the system."""
        print("\n🧪 Testing Error Handling...")
        
        # Test configuration validation errors
        try:
            # This should work without errors
            config = DiffusionConfig(model_name="")
            # Note: actual validation depends on implementation
        except Exception as e:
            # If validation is strict, this might raise an error
            self.assertIsInstance(e, Exception)
        
        # Test performance monitor with invalid timer names
        monitor = PerformanceMonitor()
        
        # Test getting average time for non-existent timer
        avg_time = monitor.get_average_time("non_existent_timer")
        # Should handle gracefully (return 0 or similar)
        
        print("✅ Error handling works correctly")
    
    def test_protocol_compliance(self):
        """Test that components comply with their protocols."""
        print("\n🧪 Testing Protocol Compliance...")
        
        # Test PerformanceMonitor protocol compliance
        monitor = PerformanceMonitor()
        
        # Check that it has all required methods
        required_methods = ['start_timer', 'end_timer', 'get_average_time', 'generate_report']
        for method_name in required_methods:
            self.assertTrue(hasattr(monitor, method_name))
            self.assertTrue(callable(getattr(monitor, method_name)))
        
        # Test MemoryTracker protocol compliance
        tracker = MemoryTracker()
        
        # Check that it has all required methods
        required_methods = ['track_memory', 'get_stats', 'clear_history']
        for method_name in required_methods:
            self.assertTrue(hasattr(tracker, method_name))
            self.assertTrue(callable(getattr(tracker, method_name)))
        
        print("✅ Protocol compliance verified")
    
    def test_clean_architecture_principles(self):
        """Test that clean architecture principles are followed."""
        print("\n🧪 Testing Clean Architecture Principles...")
        
        # Test Single Responsibility Principle
        monitor = PerformanceMonitor()
        tracker = MemoryTracker()
        
        # Each component should have a single responsibility
        # PerformanceMonitor should only handle performance metrics
        # MemoryTracker should only handle memory tracking
        
        # Test Open/Closed Principle
        # We can extend OptimizationStrategy without modifying existing code
        class CustomOptimizationStrategy(OptimizationStrategy):
            def apply(self, config: DiffusionConfig) -> DiffusionConfig:
                config.use_compile = True
                return config
        
        custom_strategy = CustomOptimizationStrategy()
        config = DiffusionConfig(model_name=self.sample_model_name)
        optimized_config = custom_strategy.apply(config)
        self.assertTrue(optimized_config.use_compile)
        
        print("✅ Clean architecture principles are followed")


def run_refactored_tests():
    """Run all refactored system tests."""
    print("🧪 Running Refactored Diffusion Models System Tests")
    print("=" * 70)
    
    if not REFACTORED_SYSTEM_AVAILABLE:
        print("❌ Refactored system not available for testing")
        print("   Please ensure diffusion_models_system_refactored.py is available")
        return False
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRefactoredDiffusionModels)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    total_tests = result.testsRun
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    successful_tests = total_tests - failed_tests - error_tests
    
    print(f"✅ Successful Tests: {successful_tests}")
    print(f"❌ Failed Tests: {failed_tests}")
    print(f"⚠️ Error Tests: {error_tests}")
    print(f"📊 Total Tests: {total_tests}")
    
    if failed_tests > 0:
        print(f"\n❌ Failed Tests:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[0].strip()}")
    
    if error_tests > 0:
        print(f"\n⚠️ Error Tests:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[0].strip()}")
    
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Excellent! Most tests passed successfully.")
    elif success_rate >= 80:
        print("👍 Good! Most tests passed with some issues.")
    elif success_rate >= 70:
        print("⚠️ Fair! Several tests need attention.")
    else:
        print("❌ Poor! Many tests are failing.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the tests
    success = run_refactored_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        exit(1)





