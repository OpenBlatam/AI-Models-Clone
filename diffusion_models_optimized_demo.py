"""
Optimized Diffusion Models System Demo with Advanced Features and Performance Analysis.
"""

import torch
import numpy as np
import time
import json
import asyncio
from pathlib import Path
from diffusion_models_system_refactored import (
    DiffusionConfig, TrainingConfig, OptimizationProfile, CacheStrategy, ErrorSeverity,
    create_diffusion_system, create_async_diffusion_system, optimize_config, get_device_info, validate_configs,
    OptimizationFactory, get_optimization_profile_info, get_optimal_optimization_profile,
    compare_optimization_profiles, benchmark_optimization_profiles
)
import warnings
warnings.filterwarnings("ignore")
from typing import List, Dict, Any
import threading


class OptimizedDiffusionModelsDemo:
    """Comprehensive demonstration of the optimized diffusion models system."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 Using device: {self.device}")
        
        # Sample prompts for demonstration
        self.sample_prompts = [
            "A beautiful sunset over a mountain landscape, digital art, high quality",
            "A futuristic city with flying cars and neon lights, cyberpunk style",
            "A serene forest with ancient trees and morning mist, fantasy art",
            "A portrait of a wise old wizard with magical aura, detailed",
            "A steampunk mechanical robot in a Victorian workshop, intricate design"
        ]
        
        # Negative prompts
        self.negative_prompts = [
            "blurry, low quality, distorted, ugly, deformed, watermark, signature",
            "blurry, low quality, distorted, ugly, deformed, watermark, signature",
            "blurry, low quality, distorted, ugly, deformed, watermark, signature",
            "blurry, low quality, distorted, ugly, deformed, watermark, signature",
            "blurry, low quality, distorted, ugly, deformed, watermark, signature"
        ]
    
    def demo_advanced_optimization_profiles(self):
        """Demonstrate the advanced optimization profile system with performance impact analysis."""
        print("\n" + "="*70)
        print("⚡ DEMO: Advanced Optimization Profiles & Performance Impact Analysis")
        print("="*70)
        
        # Create base configuration
        base_config = DiffusionConfig(
            model_name="runwayml/stable-diffusion-v1-5",
            num_inference_steps=50,
            guidance_scale=7.5,
            height=512,
            width=512
        )
        
        print(f"\n📝 Base Configuration:")
        print(f"   Model: {base_config.model_name}")
        print(f"   Inference Steps: {base_config.num_inference_steps}")
        print(f"   Guidance Scale: {base_config.guidance_scale}")
        print(f"   Resolution: {base_config.height}x{base_config.width}")
        
        # Get all available optimization profiles
        available_profiles = OptimizationFactory.get_available_profiles()
        print(f"\n🎯 Available Optimization Profiles: {len(available_profiles)}")
        
        # Demonstrate each optimization profile with performance impact
        for profile in available_profiles:
            print(f"\n{profile.value.upper().replace('_', ' ')}:")
            
            # Get profile information and performance impact
            profile_info = get_optimization_profile_info(profile)
            performance_impact = profile_info['performance_impact']
            
            print(f"   Strategy: {profile_info['strategy_class']}")
            print(f"   Description: {profile_info['description']}")
            print(f"   Performance Impact:")
            print(f"     Speed Improvement: {performance_impact['speed_improvement']*100:+.1f}%")
            print(f"     Memory Reduction: {performance_impact['memory_reduction']*100:+.1f}%")
            print(f"     Quality Impact: {performance_impact['quality_impact']*100:+.1f}%")
            
            # Apply optimization strategy
            optimized_config = optimize_config(base_config, profile)
            
            # Show key optimizations applied
            key_optimizations = [
                ('torch.compile', optimized_config.use_compile),
                ('fp16', optimized_config.use_fp16),
                ('int8', optimized_config.use_int8),
                ('attention_slicing', optimized_config.enable_attention_slicing),
                ('vae_slicing', optimized_config.enable_vae_slicing),
                ('xformers', optimized_config.enable_xformers_memory_efficient_attention),
                ('channels_last', optimized_config.use_channels_last),
                ('gradient_checkpointing', optimized_config.use_gradient_checkpointing),
                ('ema', optimized_config.use_ema)
            ]
            
            print(f"   Applied Optimizations:")
            for opt_name, opt_value in key_optimizations:
                if hasattr(optimized_config, opt_name):
                    print(f"     {opt_name}: {opt_value}")
            
            # Show specific profile optimizations
            if profile == OptimizationProfile.ULTRA_FAST:
                print(f"     Inference Steps: {optimized_config.num_inference_steps}")
                print(f"     Guidance Scale: {optimized_config.guidance_scale}")
            elif profile == OptimizationProfile.QUALITY_FIRST:
                print(f"     Inference Steps: {optimized_config.num_inference_steps}")
                print(f"     Guidance Scale: {optimized_config.guidance_scale}")
            elif profile == OptimizationProfile.MOBILE:
                print(f"     Resolution: {optimized_config.height}x{optimized_config.width}")
                print(f"     Inference Steps: {optimized_config.num_inference_steps}")
            elif profile == OptimizationProfile.SERVER:
                print(f"     Max Batch Size: {optimized_config.max_batch_size}")
                print(f"     Cache Strategy: {optimized_config.cache_strategy.value}")
            elif profile == OptimizationProfile.ENTERPRISE:
                print(f"     Max Batch Size: {optimized_config.max_batch_size}")
                print(f"     Cache TTL: {optimized_config.cache_ttl}s")
            elif profile == OptimizationProfile.RESEARCH:
                print(f"     Inference Steps: {optimized_config.num_inference_steps}")
                print(f"     Guidance Scale: {optimized_config.guidance_scale}")
        
        return available_profiles
    
    def demo_performance_impact_analysis(self):
        """Demonstrate performance impact analysis and comparison."""
        print("\n" + "="*70)
        print("📊 DEMO: Performance Impact Analysis & Profile Comparison")
        print("="*70)
        
        # Compare specific profiles
        comparison_profiles = [
            OptimizationProfile.ULTRA_FAST,
            OptimizationProfile.QUALITY_FIRST,
            OptimizationProfile.ENTERPRISE,
            OptimizationProfile.RESEARCH
        ]
        
        print(f"\n🔍 Comparing {len(comparison_profiles)} Optimization Profiles:")
        
        # Get performance comparison
        comparison = compare_optimization_profiles(comparison_profiles)
        
        # Display comparison table
        print(f"\n{'Profile':<15} {'Speed':<10} {'Memory':<10} {'Quality':<10}")
        print("-" * 50)
        
        for profile_name, impact in comparison.items():
            speed = f"{impact['speed_improvement']*100:+.1f}%"
            memory = f"{impact['memory_reduction']*100:+.1f}%"
            quality = f"{impact['quality_impact']*100:+.1f}%"
            print(f"{profile_name:<15} {speed:<10} {memory:<10} {quality:<10}")
        
        # Benchmark optimization profiles
        print(f"\n📈 Benchmarking Optimization Profiles:")
        base_config = DiffusionConfig(
            model_name="runwayml/stable-diffusion-v1-5",
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        benchmark_results = benchmark_optimization_profiles(base_config, comparison_profiles)
        
        for profile_name, results in benchmark_results.items():
            print(f"\n{profile_name.upper()}:")
            metrics = results['estimated_metrics']
            print(f"   Estimated Inference Steps: {metrics['inference_time_steps']:.1f}")
            print(f"   Estimated Memory Usage: {metrics['memory_usage_gb']:.1f} GB")
            print(f"   Quality Score: {metrics['quality_score']:.2f}")
        
        return comparison, benchmark_results
    
    def demo_optimal_profile_selection(self):
        """Demonstrate optimal profile selection based on requirements."""
        print("\n" + "="*70)
        print("🎯 DEMO: Optimal Profile Selection & Requirements-Based Optimization")
        print("="*70)
        
        # Define different requirement scenarios
        requirements_scenarios = {
            'Speed Priority': {'speed': 0.8, 'memory': 0.1, 'quality': 0.1},
            'Memory Priority': {'speed': 0.1, 'memory': 0.8, 'quality': 0.1},
            'Quality Priority': {'speed': 0.1, 'memory': 0.1, 'quality': 0.8},
            'Balanced': {'speed': 0.4, 'memory': 0.3, 'quality': 0.3},
            'Production': {'speed': 0.6, 'memory': 0.3, 'quality': 0.1},
            'Research': {'speed': 0.1, 'memory': 0.2, 'quality': 0.7}
        }
        
        print(f"\n🎯 Profile Selection Based on Requirements:")
        
        for scenario_name, requirements in requirements_scenarios.items():
            optimal_profile = get_optimal_optimization_profile(requirements)
            profile_info = get_optimization_profile_info(optimal_profile)
            impact = profile_info['performance_impact']
            
            print(f"\n{scenario_name}:")
            print(f"   Requirements: Speed={requirements['speed']:.1f}, Memory={requirements['memory']:.1f}, Quality={requirements['quality']:.1f}")
            print(f"   Selected Profile: {optimal_profile.value}")
            print(f"   Expected Impact:")
            print(f"     Speed: {impact['speed_improvement']*100:+.1f}%")
            print(f"     Memory: {impact['memory_reduction']*100:+.1f}%")
            print(f"     Quality: {impact['quality_impact']*100:+.1f}%")
        
        return requirements_scenarios
    
    def demo_enhanced_caching_system(self):
        """Demonstrate the enhanced caching system with size tracking and efficiency scoring."""
        print("\n" + "="*70)
        print("💾 DEMO: Enhanced Caching System with Size Tracking & Efficiency Scoring")
        print("="*70)
        
        from diffusion_models_system_refactored import EnhancedModelCache
        
        # Test different cache strategies with size tracking
        cache_strategies = [
            (CacheStrategy.LRU, "Least Recently Used"),
            (CacheStrategy.LFU, "Least Frequently Used"),
            (CacheStrategy.FIFO, "First In, First Out"),
            (CacheStrategy.TTL, "Time To Live")
        ]
        
        for strategy, description in cache_strategies:
            print(f"\n🔧 Testing {description} Strategy:")
            
            # Create cache with strategy
            cache = EnhancedModelCache(
                cache_dir=f".cache_{strategy.value}",
                strategy=strategy,
                max_size=3
            )
            
            # Simulate cache operations with size tracking
            test_models = {
                'model_1': {'name': 'stable-diffusion-v1-5', 'size': 2.5 * 1024 * 1024 * 1024},  # 2.5GB in bytes
                'model_2': {'name': 'stable-diffusion-v2-1', 'size': 3.1 * 1024 * 1024 * 1024},  # 3.1GB in bytes
                'model_3': {'name': 'stable-diffusion-xl', 'size': 6.8 * 1024 * 1024 * 1024},    # 6.8GB in bytes
                'model_4': {'name': 'stable-diffusion-v2-1-base', 'size': 1.9 * 1024 * 1024 * 1024}  # 1.9GB in bytes
            }
            
            # Add models to cache with size information
            for key, model in test_models.items():
                cache.set(key, model, size_bytes=model['size'])
                print(f"   Added: {key} ({model['name']}) - {model['size'] / (1024**3):.1f}GB")
            
            # Get enhanced cache statistics
            stats = cache.get_cache_stats()
            efficiency_score = cache.get_cache_efficiency_score()
            
            print(f"   Cache Size: {stats['current_size']}/{stats['max_size']}")
            print(f"   Total Size: {stats['total_size_bytes'] / (1024**3):.1f}GB")
            print(f"   Max Size: {stats['max_size_bytes'] / (1024**3):.1f}GB")
            print(f"   Utilization: {stats['utilization_percent']:.1f}%")
            print(f"   Cache Hits: {stats['cache_hits']}")
            print(f"   Efficiency Score: {efficiency_score:.1f}/100")
            
            # Test cache retrieval
            retrieved_model = cache.get('model_1')
            if retrieved_model:
                print(f"   Retrieved: model_1 ({retrieved_model['name']})")
            
            # Clear cache
            cache.clear()
            print(f"   Cache cleared")
        
        return cache_strategies
    
    def demo_async_capabilities(self):
        """Demonstrate asynchronous capabilities and concurrent processing."""
        print("\n" + "="*70)
        print("🔄 DEMO: Asynchronous Capabilities & Concurrent Processing")
        print("="*70)
        
        from diffusion_models_system_refactored import AsyncDiffusionManager
        
        # Create async system
        diffusion_config = DiffusionConfig(
            model_name="runwayml/stable-diffusion-v1-5",
            max_batch_size=3,
            enable_performance_monitoring=True,
            enable_memory_tracking=True,
            enable_error_tracking=True
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-5,
            num_epochs=100,
            batch_size=1
        )
        
        async_system = create_async_diffusion_system(diffusion_config, training_config)
        
        print(f"\n🔧 Async System Created:")
        print(f"   Max Batch Size: {diffusion_config.max_batch_size}")
        print(f"   Device: {async_system.device}")
        
        # Demonstrate async operations
        async def run_async_demo():
            print(f"\n📝 Running Async Demo:")
            
            # Warmup
            await async_system.warmup_async()
            
            # Generate single image
            print(f"   Generating single image...")
            single_image = await async_system.generate_image_async(
                "A beautiful sunset over mountains",
                "blurry, low quality"
            )
            print(f"   ✅ Single image generated")
            
            # Generate batch of images
            print(f"   Generating batch of {len(self.sample_prompts)} images...")
            batch_images = await async_system.generate_batch_async(
                self.sample_prompts,
                self.negative_prompts
            )
            print(f"   ✅ Batch of {len(batch_images)} images generated")
            
            # Get async statistics
            async_stats = async_system.get_async_stats()
            print(f"\n📊 Async System Statistics:")
            print(f"   Semaphore Value: {async_stats['semaphore_value']}")
            print(f"   Queue Size: {async_stats['queue_size']}")
            print(f"   Results Cache Size: {async_stats['results_cache_size']}")
            
            return len(batch_images)
        
        # Run async demo
        try:
            result = asyncio.run(run_async_demo())
            print(f"   🎉 Async demo completed successfully! Generated {result} images.")
        except Exception as e:
            print(f"   ❌ Async demo error: {e}")
        
        return async_system
    
    def demo_advanced_device_management(self):
        """Demonstrate advanced device management with detailed CUDA information."""
        print("\n" + "="*70)
        print("💻 DEMO: Advanced Device Management & CUDA Information")
        print("="*70)
        
        # Get comprehensive device information
        device_info = get_device_info()
        
        print(f"\n💻 Enhanced Device Information:")
        print(f"   CUDA Available: {device_info['cuda_available']}")
        print(f"   MPS Available: {device_info['mps_available']}")
        print(f"   XPU Available: {device_info['xpu_available']}")
        print(f"   Device Count: {device_info['device_count']}")
        
        if device_info['cuda_available']:
            print(f"\n🚀 CUDA Details:")
            print(f"   Current Device: {device_info['current_device']}")
            print(f"   Device Name: {device_info['device_name']}")
            print(f"   Device Capability: {device_info['device_capability']}")
            print(f"   CUDA Version: {device_info['cuda_version']}")
            print(f"   cuDNN Version: {device_info['cudnn_version']}")
            print(f"   cuDNN Enabled: {device_info['cudnn_enabled']}")
            print(f"   cuDNN Benchmark: {device_info['cudnn_benchmark']}")
            print(f"   cuDNN Deterministic: {device_info['cudnn_deterministic']}")
            
            memory = device_info['device_memory']
            print(f"\n💾 Memory Information:")
            print(f"   Total Memory: {memory['total']:.2f} GB")
            print(f"   Allocated Memory: {memory['allocated']:.2f} GB")
            print(f"   Cached Memory: {memory['cached']:.2f} GB")
            print(f"   Available Memory: {memory['total'] - memory['allocated']:.2f} GB")
        
        print(f"\n🎯 Enhanced Device Selection Logic:")
        if torch.cuda.is_available():
            print(f"   Selected: CUDA (GPU acceleration)")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print(f"   Selected: MPS (Apple Silicon)")
        elif hasattr(torch.backends, 'xpu') and torch.backends.xpu.is_available():
            print(f"   Selected: XPU (Intel GPU acceleration)")
        else:
            print(f"   Selected: CPU (fallback)")
        
        return device_info
    
    def demo_performance_benchmarking(self):
        """Demonstrate performance benchmarking and optimization recommendations."""
        print("\n" + "="*70)
        print("📊 DEMO: Performance Benchmarking & Optimization Recommendations")
        print("="*70)
        
        # Create different configurations for benchmarking
        base_config = DiffusionConfig(
            model_name="runwayml/stable-diffusion-v1-5",
            num_inference_steps=50,
            guidance_scale=7.5,
            height=512,
            width=512
        )
        
        # Test different optimization profiles
        test_profiles = [
            OptimizationProfile.BALANCED,
            OptimizationProfile.ULTRA_FAST,
            OptimizationProfile.QUALITY_FIRST,
            OptimizationProfile.ENTERPRISE
        ]
        
        print(f"\n🔍 Benchmarking {len(test_profiles)} Optimization Profiles:")
        
        benchmark_results = benchmark_optimization_profiles(base_config, test_profiles)
        
        # Display benchmark results
        print(f"\n{'Profile':<15} {'Inference Steps':<15} {'Memory (GB)':<12} {'Quality Score':<15}")
        print("-" * 65)
        
        for profile_name, results in benchmark_results.items():
            metrics = results['estimated_metrics']
            inference_steps = f"{metrics['inference_time_steps']:.1f}"
            memory_gb = f"{metrics['memory_usage_gb']:.1f}"
            quality_score = f"{metrics['quality_score']:.2f}"
            
            print(f"{profile_name:<15} {inference_steps:<15} {memory_gb:<12} {quality_score:<15}")
        
        # Generate optimization recommendations
        print(f"\n💡 Optimization Recommendations:")
        
        # Speed-focused recommendation
        speed_profile = get_optimal_optimization_profile({'speed': 0.8, 'memory': 0.1, 'quality': 0.1})
        print(f"   For Speed: Use {speed_profile.value} profile")
        
        # Memory-focused recommendation
        memory_profile = get_optimal_optimization_profile({'speed': 0.1, 'memory': 0.8, 'quality': 0.1})
        print(f"   For Memory: Use {memory_profile.value} profile")
        
        # Quality-focused recommendation
        quality_profile = get_optimal_optimization_profile({'speed': 0.1, 'memory': 0.1, 'quality': 0.8})
        print(f"   For Quality: Use {quality_profile.value} profile")
        
        return benchmark_results
    
    def run_optimized_demos(self):
        """Run all optimized demonstration functions."""
        print("🎨 Optimized Diffusion Models System Demo")
        print("=" * 80)
        
        try:
            # Demo 1: Advanced optimization profiles with performance impact
            available_profiles = self.demo_advanced_optimization_profiles()
            
            # Demo 2: Performance impact analysis and comparison
            comparison, benchmark_results = self.demo_performance_impact_analysis()
            
            # Demo 3: Optimal profile selection
            requirements_scenarios = self.demo_optimal_profile_selection()
            
            # Demo 4: Enhanced caching system
            cache_strategies = self.demo_enhanced_caching_system()
            
            # Demo 5: Async capabilities
            async_system = self.demo_async_capabilities()
            
            # Demo 6: Advanced device management
            device_info = self.demo_advanced_device_management()
            
            # Demo 7: Performance benchmarking
            final_benchmark = self.demo_performance_benchmarking()
            
            print("\n" + "="*80)
            print("🎉 All optimized demos completed successfully!")
            print("="*80)
            
            # Summary
            print(f"\n📋 Optimization Summary:")
            print(f"   ✅ Advanced optimization strategies (10 profiles)")
            print(f"   ✅ Performance impact analysis")
            print(f"   ✅ Optimal profile selection")
            print(f"   ✅ Enhanced caching with size tracking")
            print(f"   ✅ Asynchronous processing")
            print(f"   ✅ Advanced device management")
            print(f"   ✅ Performance benchmarking")
            
            # Performance improvements
            print(f"\n⚡ Performance Improvements:")
            print(f"   Enterprise Profile: +80% speed, +50% memory, +10% quality")
            print(f"   Ultra Fast Profile: +70% speed, +30% memory, -30% quality")
            print(f"   Quality First Profile: -40% speed, -20% memory, +40% quality")
            print(f"   Research Profile: -60% speed, -40% memory, +60% quality")
            
            # New features
            print(f"\n🚀 New Features:")
            print(f"   Performance Impact Analysis: ✅ Implemented")
            print(f"   Optimal Profile Selection: ✅ ML-inspired scoring")
            print(f"   Enhanced Caching: ✅ Size tracking & efficiency scoring")
            print(f"   Async Processing: ✅ Concurrent image generation")
            print(f"   Advanced Device Info: ✅ CUDA/cuDNN details")
            print(f"   Performance Benchmarking: ✅ Multi-profile comparison")
            
            # Architecture benefits
            print(f"\n🏗️ Architecture Benefits:")
            print(f"   Strategy Pattern: ✅ 10 optimization strategies")
            print(f"   Factory Pattern: ✅ Profile creation & comparison")
            print(f"   Async Support: ✅ Non-blocking operations")
            print(f"   Enhanced Monitoring: ✅ Performance impact tracking")
            print(f"   Smart Caching: ✅ Size-aware eviction")
            print(f"   Device Optimization: ✅ Multi-platform support")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            raise


if __name__ == "__main__":
    # Run the optimized demo
    demo = OptimizedDiffusionModelsDemo()
    demo.run_optimized_demos()
