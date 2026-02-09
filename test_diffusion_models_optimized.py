#!/usr/bin/env python3
"""
Comprehensive Test Suite for Optimized Diffusion Models System.
Tests all optimization features, performance analysis, async capabilities, and advanced caching.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import torch
import numpy as np

# Import the optimized system components
from diffusion_models_system_refactored import (
    DiffusionConfig, TrainingConfig, OptimizationProfile, CacheStrategy, ErrorSeverity,
    OptimizationStrategy, OptimizationFactory, EnhancedModelCache, AsyncDiffusionManager,
    create_diffusion_system, create_async_diffusion_system, optimize_config,
    get_device_info, validate_configs, get_optimization_profile_info,
    get_optimal_optimization_profile, compare_optimization_profiles,
    benchmark_optimization_profiles
)


class TestOptimizationProfiles(unittest.TestCase):
    """Test optimization profile system and strategies."""
    
    def setUp(self):
        """Set up test configurations."""
        self.base_config = DiffusionConfig(
            model_name="test-model",
            num_inference_steps=50,
            guidance_scale=7.5,
            height=512,
            width=512
        )
    
    def test_optimization_profile_enum(self):
        """Test that all optimization profiles are available."""
        expected_profiles = [
            'BALANCED', 'INFERENCE', 'TRAINING', 'MEMORY',
            'ULTRA_FAST', 'QUALITY_FIRST', 'MOBILE', 'SERVER',
            'ENTERPRISE', 'RESEARCH'
        ]
        
        available_profiles = OptimizationFactory.get_available_profiles()
        profile_names = [profile.value for profile in available_profiles]
        
        for expected in expected_profiles:
            self.assertIn(expected, profile_names)
    
    def test_optimization_strategy_application(self):
        """Test that optimization strategies can be applied to configurations."""
        for profile in OptimizationProfile:
            try:
                optimized_config = optimize_config(self.base_config, profile)
                self.assertIsInstance(optimized_config, DiffusionConfig)
                self.assertNotEqual(optimized_config, self.base_config)
            except Exception as e:
                self.fail(f"Failed to apply {profile.value} strategy: {e}")
    
    def test_performance_impact_analysis(self):
        """Test performance impact analysis for optimization profiles."""
        for profile in OptimizationProfile:
            profile_info = get_optimization_profile_info(profile)
            
            # Check required fields
            self.assertIn('strategy_class', profile_info)
            self.assertIn('description', profile_info)
            self.assertIn('performance_impact', profile_info)
            
            # Check performance impact structure
            impact = profile_info['performance_impact']
            self.assertIn('speed_improvement', impact)
            self.assertIn('memory_reduction', impact)
            self.assertIn('quality_impact', impact)
            
            # Validate impact values are between -1 and 1
            for value in impact.values():
                self.assertGreaterEqual(value, -1.0)
                self.assertLessEqual(value, 1.0)
    
    def test_ultra_fast_optimization(self):
        """Test ULTRA_FAST optimization profile."""
        config = optimize_config(self.base_config, OptimizationProfile.ULTRA_FAST)
        
        # Check specific optimizations
        self.assertTrue(config.use_int8)
        self.assertLess(config.num_inference_steps, 50)
        self.assertLess(config.guidance_scale, 7.5)
    
    def test_quality_first_optimization(self):
        """Test QUALITY_FIRST optimization profile."""
        config = optimize_config(self.base_config, OptimizationProfile.QUALITY_FIRST)
        
        # Check specific optimizations
        self.assertFalse(config.use_compile)
        self.assertFalse(config.use_fp16)
        self.assertGreater(config.num_inference_steps, 50)
        self.assertGreater(config.guidance_scale, 7.5)
    
    def test_mobile_optimization(self):
        """Test MOBILE optimization profile."""
        config = optimize_config(self.base_config, OptimizationProfile.MOBILE)
        
        # Check specific optimizations
        self.assertEqual(config.height, 256)
        self.assertEqual(config.width, 256)
        self.assertTrue(config.use_int8)
        self.assertLess(config.num_inference_steps, 50)
    
    def test_server_optimization(self):
        """Test SERVER optimization profile."""
        config = optimize_config(self.base_config, OptimizationProfile.SERVER)
        
        # Check specific optimizations
        self.assertEqual(config.max_batch_size, 8)
        self.assertEqual(config.cache_strategy, CacheStrategy.TTL)
        self.assertTrue(config.enable_sequential_cpu_offload)
    
    def test_enterprise_optimization(self):
        """Test ENTERPRISE optimization profile."""
        config = optimize_config(self.base_config, OptimizationProfile.ENTERPRISE)
        
        # Check specific optimizations
        self.assertEqual(config.max_batch_size, 16)
        self.assertEqual(config.cache_ttl, 7200)  # 2 hours
        self.assertTrue(config.enable_metrics_export)
    
    def test_research_optimization(self):
        """Test RESEARCH optimization profile."""
        config = optimize_config(self.base_config, OptimizationProfile.RESEARCH)
        
        # Check specific optimizations
        self.assertGreater(config.num_inference_steps, 50)
        self.assertGreater(config.guidance_scale, 7.5)
        self.assertTrue(config.enable_error_tracking)


class TestPerformanceAnalysis(unittest.TestCase):
    """Test performance impact analysis and comparison."""
    
    def test_profile_comparison(self):
        """Test comparison of multiple optimization profiles."""
        profiles = [
            OptimizationProfile.ULTRA_FAST,
            OptimizationProfile.QUALITY_FIRST,
            OptimizationProfile.ENTERPRISE
        ]
        
        comparison = compare_optimization_profiles(profiles)
        
        # Check comparison structure
        self.assertIsInstance(comparison, dict)
        self.assertEqual(len(comparison), 3)
        
        for profile_name, impact in comparison.items():
            self.assertIn('speed_improvement', impact)
            self.assertIn('memory_reduction', impact)
            self.assertIn('quality_impact', impact)
    
    def test_optimal_profile_selection(self):
        """Test optimal profile selection based on requirements."""
        # Speed-focused requirements
        speed_requirements = {'speed': 0.8, 'memory': 0.1, 'quality': 0.1}
        optimal_profile = get_optimal_optimization_profile(speed_requirements)
        self.assertIsInstance(optimal_profile, OptimizationProfile)
        
        # Quality-focused requirements
        quality_requirements = {'speed': 0.1, 'memory': 0.1, 'quality': 0.8}
        optimal_profile = get_optimal_optimization_profile(quality_requirements)
        self.assertIsInstance(optimal_profile, OptimizationProfile)
        
        # Balanced requirements
        balanced_requirements = {'speed': 0.4, 'memory': 0.3, 'quality': 0.3}
        optimal_profile = get_optimal_optimization_profile(balanced_requirements)
        self.assertIsInstance(optimal_profile, OptimizationProfile)
    
    def test_benchmark_optimization_profiles(self):
        """Test benchmarking of optimization profiles."""
        base_config = DiffusionConfig(
            model_name="test-model",
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        profiles = [
            OptimizationProfile.BALANCED,
            OptimizationProfile.ULTRA_FAST,
            OptimizationProfile.QUALITY_FIRST
        ]
        
        benchmark_results = benchmark_optimization_profiles(base_config, profiles)
        
        # Check benchmark structure
        self.assertIsInstance(benchmark_results, dict)
        self.assertEqual(len(benchmark_results), 3)
        
        for profile_name, results in benchmark_results.items():
            self.assertIn('estimated_metrics', results)
            metrics = results['estimated_metrics']
            self.assertIn('inference_time_steps', metrics)
            self.assertIn('memory_usage_gb', metrics)
            self.assertIn('quality_score', metrics)


class TestEnhancedCaching(unittest.TestCase):
    """Test enhanced caching system with size tracking."""
    
    def setUp(self):
        """Set up test cache directory."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    def test_cache_strategies(self):
        """Test all cache strategies."""
        strategies = [
            CacheStrategy.LRU,
            CacheStrategy.LFU,
            CacheStrategy.FIFO,
            CacheStrategy.TTL
        ]
        
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                cache = EnhancedModelCache(
                    cache_dir=f"{self.test_dir}/cache_{strategy.value}",
                    strategy=strategy,
                    max_size=3
                )
                
                # Test basic operations
                cache.set("key1", "value1", size_bytes=1024)
                cache.set("key2", "value2", size_bytes=2048)
                
                # Test retrieval
                value1 = cache.get("key1")
                self.assertEqual(value1, "value1")
                
                # Test cache stats
                stats = cache.get_cache_stats()
                self.assertIn('current_size', stats)
                self.assertIn('max_size', stats)
                self.assertIn('total_size_bytes', stats)
                self.assertIn('cache_hits', stats)
                
                # Test efficiency scoring
                efficiency = cache.get_cache_efficiency_score()
                self.assertGreaterEqual(efficiency, 0)
                self.assertLessEqual(efficiency, 100)
    
    def test_size_tracking(self):
        """Test cache size tracking functionality."""
        cache = EnhancedModelCache(
            cache_dir=f"{self.test_dir}/size_test",
            strategy=CacheStrategy.LRU,
            max_size=2
        )
        
        # Add items with known sizes
        cache.set("item1", "data1", size_bytes=1024)  # 1KB
        cache.set("item2", "data2", size_bytes=2048)  # 2KB
        
        stats = cache.get_cache_stats()
        self.assertEqual(stats['total_size_bytes'], 3072)  # 3KB
        
        # Add third item to trigger eviction
        cache.set("item3", "data3", size_bytes=1024)  # 1KB
        
        # Check that eviction occurred
        stats = cache.get_cache_stats()
        self.assertLessEqual(stats['total_size_bytes'], 3072)
    
    def test_cache_efficiency_scoring(self):
        """Test cache efficiency scoring system."""
        cache = EnhancedModelCache(
            cache_dir=f"{self.test_dir}/efficiency_test",
            strategy=CacheStrategy.LRU,
            max_size=5
        )
        
        # Add items and access them
        for i in range(5):
            cache.set(f"item{i}", f"data{i}", size_bytes=1024)
        
        # Access some items multiple times to improve efficiency
        for _ in range(10):
            cache.get("item0")
            cache.get("item1")
        
        efficiency = cache.get_cache_efficiency_score()
        self.assertGreaterEqual(efficiency, 0)
        self.assertLessEqual(efficiency, 100)
        
        # Higher hit rate should result in better efficiency
        self.assertGreater(efficiency, 50)


class TestAsyncCapabilities(unittest.TestCase):
    """Test asynchronous processing capabilities."""
    
    def setUp(self):
        """Set up test configurations."""
        self.diffusion_config = DiffusionConfig(
            model_name="test-model",
            max_batch_size=3,
            enable_performance_monitoring=True,
            enable_memory_tracking=True,
            enable_error_tracking=True
        )
        
        self.training_config = TrainingConfig(
            learning_rate=1e-5,
            num_epochs=100,
            batch_size=1
        )
    
    @patch('diffusion_models_system_refactored.DiffusionModelManager')
    def test_async_system_creation(self, mock_manager_class):
        """Test creation of async diffusion system."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        async_system = create_async_diffusion_system(
            self.diffusion_config,
            self.training_config
        )
        
        self.assertIsInstance(async_system, AsyncDiffusionManager)
        self.assertEqual(async_system.device, torch.device('cpu'))
    
    def test_async_manager_interface(self):
        """Test AsyncDiffusionManager interface."""
        # Create mock async manager
        async_manager = AsyncDiffusionManager(
            device=torch.device('cpu'),
            max_batch_size=3
        )
        
        # Test interface methods exist
        self.assertTrue(hasattr(async_manager, 'generate_image_async'))
        self.assertTrue(hasattr(async_manager, 'generate_batch_async'))
        self.assertTrue(hasattr(async_manager, 'warmup_async'))
        self.assertTrue(hasattr(async_manager, 'get_async_stats'))
        
        # Test async stats
        stats = async_manager.get_async_stats()
        self.assertIn('semaphore_value', stats)
        self.assertIn('queue_size', stats)
        self.assertIn('results_cache_size', stats)
    
    @patch('diffusion_models_system_refactored.DiffusionModelManager')
    async def test_async_operations(self, mock_manager_class):
        """Test async operations."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        async_system = create_async_diffusion_system(
            self.diffusion_config,
            self.training_config
        )
        
        # Test warmup
        await async_system.warmup_async()
        
        # Test single image generation
        result = await async_system.generate_image_async(
            "test prompt",
            "test negative prompt"
        )
        
        # Test batch generation
        prompts = ["prompt1", "prompt2"]
        negative_prompts = ["neg1", "neg2"]
        
        batch_result = await async_system.generate_batch_async(
            prompts,
            negative_prompts
        )
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertIsNotNone(batch_result)


class TestDeviceManagement(unittest.TestCase):
    """Test advanced device management and detection."""
    
    def test_device_info_structure(self):
        """Test device information structure."""
        device_info = get_device_info()
        
        # Check required fields
        required_fields = [
            'cuda_available', 'mps_available', 'xpu_available',
            'device_count', 'device_memory'
        ]
        
        for field in required_fields:
            self.assertIn(field, device_info)
    
    def test_cuda_information(self):
        """Test CUDA-specific information."""
        device_info = get_device_info()
        
        if device_info['cuda_available']:
            # Check CUDA-specific fields
            cuda_fields = [
                'current_device', 'device_name', 'device_capability',
                'cuda_version', 'cudnn_version', 'cudnn_enabled',
                'cudnn_benchmark', 'cudnn_deterministic'
            ]
            
            for field in cuda_fields:
                self.assertIn(field, device_info)
    
    def test_device_memory_information(self):
        """Test device memory information."""
        device_info = get_device_info()
        memory = device_info['device_memory']
        
        # Check memory fields
        memory_fields = ['total', 'allocated', 'cached']
        for field in memory_fields:
            self.assertIn(field, memory)
            self.assertGreaterEqual(memory[field], 0)


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation and management."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid configuration
        valid_config = DiffusionConfig(
            model_name="test-model",
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        # Should not raise exception
        validate_configs(valid_config)
    
    def test_config_clone_and_merge(self):
        """Test configuration cloning and merging."""
        config1 = DiffusionConfig(
            model_name="model1",
            num_inference_steps=50
        )
        
        config2 = DiffusionConfig(
            model_name="model2",
            guidance_scale=10.0
        )
        
        # Test cloning
        cloned_config = config1.clone()
        self.assertEqual(cloned_config.model_name, config1.model_name)
        self.assertEqual(cloned_config.num_inference_steps, config1.num_inference_steps)
        
        # Test merging
        merged_config = config1.merge(config2)
        self.assertEqual(merged_config.model_name, "model2")
        self.assertEqual(merged_config.num_inference_steps, 50)
        self.assertEqual(merged_config.guidance_scale, 10.0)
    
    def test_training_config_validation(self):
        """Test training configuration validation."""
        # Valid training configuration
        valid_training_config = TrainingConfig(
            learning_rate=1e-5,
            num_epochs=100,
            batch_size=32
        )
        
        # Should not raise exception
        validate_configs(valid_training_config)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and management system."""
    
    def test_error_severity_levels(self):
        """Test error severity enum."""
        severities = list(ErrorSeverity)
        expected_severities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for severity in severities:
            self.assertIn(severity.value, expected_severities)
    
    def test_error_handler_interface(self):
        """Test error handler interface."""
        from diffusion_models_system_refactored import ErrorHandler
        
        error_handler = ErrorHandler()
        
        # Test error handling methods
        self.assertTrue(hasattr(error_handler, 'handle_error'))
        self.assertTrue(hasattr(error_handler, 'log_error'))
        self.assertTrue(hasattr(error_handler, 'get_error_summary'))
        self.assertTrue(hasattr(error_handler, 'clear_errors'))
        
        # Test error handling
        error_handler.handle_error("Test error", ErrorSeverity.INFO)
        summary = error_handler.get_error_summary()
        self.assertIn('total_errors', summary)
        self.assertIn('errors_by_severity', summary)


class TestIntegration(unittest.TestCase):
    """Test integration of all components."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    @patch('diffusion_models_system_refactored.DiffusionModelManager')
    def test_system_creation_integration(self, mock_manager_class):
        """Test integration of system creation."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        config = DiffusionConfig(
            model_name="test-model",
            optimization_profile=OptimizationProfile.ULTRA_FAST
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-5,
            num_epochs=100
        )
        
        # Create system
        system = create_diffusion_system(config, training_config)
        
        # Verify system creation
        self.assertIsNotNone(system)
        mock_manager_class.assert_called_once()
    
    def test_optimization_workflow(self):
        """Test complete optimization workflow."""
        # 1. Create base configuration
        base_config = DiffusionConfig(
            model_name="test-model",
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        # 2. Select optimization profile
        requirements = {'speed': 0.8, 'memory': 0.1, 'quality': 0.1}
        optimal_profile = get_optimal_optimization_profile(requirements)
        
        # 3. Apply optimization
        optimized_config = optimize_config(base_config, optimal_profile)
        
        # 4. Validate optimization
        self.assertNotEqual(base_config, optimized_config)
        
        # 5. Get performance impact
        profile_info = get_optimization_profile_info(optimal_profile)
        impact = profile_info['performance_impact']
        
        # 6. Verify performance improvements
        self.assertGreater(impact['speed_improvement'], 0)
        self.assertGreater(impact['memory_reduction'], 0)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Test performance benchmarking capabilities."""
    
    def test_benchmark_accuracy(self):
        """Test accuracy of performance benchmarks."""
        base_config = DiffusionConfig(
            model_name="test-model",
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        # Benchmark single profile
        profiles = [OptimizationProfile.ULTRA_FAST]
        benchmark_results = benchmark_optimization_profiles(base_config, profiles)
        
        # Verify benchmark structure
        self.assertIn('ULTRA_FAST', benchmark_results)
        result = benchmark_results['ULTRA_FAST']
        
        # Check metrics
        metrics = result['estimated_metrics']
        self.assertIn('inference_time_steps', metrics)
        self.assertIn('memory_usage_gb', metrics)
        self.assertIn('quality_score', metrics)
        
        # Verify metric values are reasonable
        self.assertGreater(metrics['inference_time_steps'], 0)
        self.assertGreater(metrics['memory_usage_gb'], 0)
        self.assertGreater(metrics['quality_score'], 0)
        self.assertLessEqual(metrics['quality_score'], 1.0)
    
    def test_benchmark_comparison(self):
        """Test benchmark comparison functionality."""
        base_config = DiffusionConfig(
            model_name="test-model",
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        # Compare multiple profiles
        profiles = [
            OptimizationProfile.BALANCED,
            OptimizationProfile.ULTRA_FAST,
            OptimizationProfile.QUALITY_FIRST
        ]
        
        comparison = compare_optimization_profiles(profiles)
        
        # Verify comparison results
        for profile_name, impact in comparison.items():
            # Check that speed improvements are reasonable
            self.assertGreaterEqual(impact['speed_improvement'], -1.0)
            self.assertLessEqual(impact['speed_improvement'], 1.0)
            
            # Check that memory reductions are reasonable
            self.assertGreaterEqual(impact['memory_reduction'], -1.0)
            self.assertLessEqual(impact['memory_reduction'], 1.0)
            
            # Check that quality impacts are reasonable
            self.assertGreaterEqual(impact['quality_impact'], -1.0)
            self.assertLessEqual(impact['quality_impact'], 1.0)


def run_performance_tests():
    """Run performance-focused tests."""
    print("🚀 Running Performance Tests...")
    
    # Test optimization profile performance
    print("  Testing optimization profiles...")
    for profile in OptimizationProfile:
        profile_info = get_optimization_profile_info(profile)
        impact = profile_info['performance_impact']
        print(f"    {profile.value}: Speed {impact['speed_improvement']*100:+.1f}%, "
              f"Memory {impact['memory_reduction']*100:+.1f}%, "
              f"Quality {impact['quality_impact']*100:+.1f}%")
    
    # Test profile comparison
    print("  Testing profile comparison...")
    profiles = [OptimizationProfile.ULTRA_FAST, OptimizationProfile.QUALITY_FIRST]
    comparison = compare_optimization_profiles(profiles)
    for profile_name, impact in comparison.items():
        print(f"    {profile_name}: {impact}")
    
    # Test optimal profile selection
    print("  Testing optimal profile selection...")
    requirements = {'speed': 0.8, 'memory': 0.1, 'quality': 0.1}
    optimal = get_optimal_optimization_profile(requirements)
    print(f"    Optimal for speed: {optimal.value}")
    
    print("✅ Performance tests completed!")


if __name__ == "__main__":
    # Run performance tests first
    run_performance_tests()
    
    # Run comprehensive test suite
    print("\n🧪 Running Comprehensive Test Suite...")
    unittest.main(verbosity=2)
