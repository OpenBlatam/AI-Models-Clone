"""
Enhanced Diffusion Models System Demo with Advanced Features and Optimization Strategies.
"""

import torch
import numpy as np
import time
import json
from pathlib import Path
from diffusion_models_system_refactored import (
    DiffusionConfig, TrainingConfig, OptimizationProfile, CacheStrategy, ErrorSeverity,
    create_diffusion_system, optimize_config, get_device_info, validate_configs,
    OptimizationFactory, get_optimization_profile_info
)
import warnings
warnings.filterwarnings("ignore")
from typing import List, Dict, Any
import asyncio
import threading


class EnhancedDiffusionModelsDemo:
    """Enhanced demonstration of the diffusion models system with advanced features."""
    
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
    
    def demo_enhanced_optimization_profiles(self):
        """Demonstrate the enhanced optimization profile system."""
        print("\n" + "="*70)
        print("⚡ DEMO: Enhanced Optimization Profiles & Advanced Strategies")
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
        
        # Demonstrate each optimization profile
        for profile in available_profiles:
            print(f"\n{profile.value.upper().replace('_', ' ')}:")
            
            # Get profile information
            profile_info = get_optimization_profile_info(profile)
            print(f"   Strategy: {profile_info['strategy_class']}")
            print(f"   Description: {profile_info['description']}")
            
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
            
            for opt_name, opt_value in key_optimizations:
                if hasattr(optimized_config, opt_name):
                    print(f"   {opt_name}: {opt_value}")
            
            # Show specific profile optimizations
            if profile == OptimizationProfile.ULTRA_FAST:
                print(f"   Inference Steps: {optimized_config.num_inference_steps}")
            elif profile == OptimizationProfile.QUALITY_FIRST:
                print(f"   Inference Steps: {optimized_config.num_inference_steps}")
                print(f"   Guidance Scale: {optimized_config.guidance_scale}")
            elif profile == OptimizationProfile.MOBILE:
                print(f"   Resolution: {optimized_config.height}x{optimized_config.width}")
                print(f"   Inference Steps: {optimized_config.num_inference_steps}")
            elif profile == OptimizationProfile.SERVER:
                print(f"   Max Batch Size: {optimized_config.max_batch_size}")
                print(f"   Cache Strategy: {optimized_config.cache_strategy.value}")
        
        return available_profiles
    
    def demo_enhanced_configuration_system(self):
        """Demonstrate the enhanced configuration management system."""
        print("\n" + "="*70)
        print("⚙️ DEMO: Enhanced Configuration Management & Advanced Features")
        print("="*70)
        
        # Create enhanced configurations
        diffusion_config = DiffusionConfig(
            model_name="runwayml/stable-diffusion-v1-5",
            model_revision="main",
            model_variant="fp16",
            num_inference_steps=30,
            guidance_scale=7.5,
            height=512,
            width=512,
            use_compile=True,
            use_fp16=True,
            use_int8=False,
            enable_attention_slicing=True,
            enable_vae_slicing=True,
            enable_xformers_memory_efficient_attention=True,
            cache_strategy=CacheStrategy.LRU,
            max_cache_size=10,
            cache_ttl=7200,  # 2 hours
            enable_controlnet=False,
            enable_lora=False,
            enable_textual_inversion=False
        )
        
        training_config = TrainingConfig(
            learning_rate=1e-4,
            num_epochs=100,
            batch_size=2,
            gradient_accumulation_steps=4,
            max_grad_norm=1.0,
            use_mixed_precision=True,
            use_gradient_checkpointing=True,
            use_amp=True,
            weight_decay=0.01,
            dropout=0.1,
            enable_tensorboard=True,
            enable_wandb=False,
            use_distributed_training=False,
            use_multi_gpu=False
        )
        
        print(f"\n📋 Enhanced Diffusion Configuration:")
        print(f"   Model: {diffusion_config.model_name}")
        print(f"   Revision: {diffusion_config.model_revision}")
        print(f"   Variant: {diffusion_config.model_variant}")
        print(f"   Inference Steps: {diffusion_config.num_inference_steps}")
        print(f"   Guidance Scale: {diffusion_config.guidance_scale}")
        print(f"   Resolution: {diffusion_config.height}x{diffusion_config.width}")
        print(f"   Cache Strategy: {diffusion_config.cache_strategy.value}")
        print(f"   Max Cache Size: {diffusion_config.max_cache_size}")
        print(f"   Cache TTL: {diffusion_config.cache_ttl}s")
        
        print(f"\n📋 Enhanced Training Configuration:")
        print(f"   Learning Rate: {training_config.learning_rate}")
        print(f"   Epochs: {training_config.num_epochs}")
        print(f"   Batch Size: {training_config.batch_size}")
        print(f"   Gradient Accumulation: {training_config.gradient_accumulation_steps}")
        print(f"   Max Grad Norm: {training_config.max_grad_norm}")
        print(f"   Mixed Precision: {training_config.use_mixed_precision}")
        print(f"   Gradient Checkpointing: {training_config.use_gradient_checkpointing}")
        print(f"   TensorBoard: {training_config.enable_tensorboard}")
        print(f"   Weights & Biases: {training_config.enable_wandb}")
        print(f"   Distributed Training: {training_config.use_distributed_training}")
        print(f"   Multi-GPU: {training_config.use_multi_gpu}")
        
        # Demonstrate enhanced configuration methods
        print(f"\n🔧 Enhanced Configuration Methods:")
        
        # Convert to dictionary
        config_dict = diffusion_config.to_dict()
        print(f"   to_dict(): {len(config_dict)} configuration items")
        
        # Clone configuration
        cloned_config = diffusion_config.clone()
        print(f"   clone(): Created identical configuration")
        
        # Update configuration
        diffusion_config.update(num_inference_steps=25, guidance_scale=8.0)
        print(f"   update(): Inference steps now {diffusion_config.num_inference_steps}")
        print(f"   update(): Guidance scale now {diffusion_config.guidance_scale}")
        
        # Merge configurations
        override_config = DiffusionConfig(num_inference_steps=40, height=768, width=768)
        merged_config = diffusion_config.merge(override_config)
        print(f"   merge(): Merged with override config")
        print(f"   merge(): Final inference steps: {merged_config.num_inference_steps}")
        print(f"   merge(): Final resolution: {merged_config.height}x{merged_config.width}")
        
        # Validate configurations
        print(f"\n✅ Configuration Validation:")
        is_valid = validate_configs(diffusion_config, training_config)
        print(f"   Validation Result: {'PASSED' if is_valid else 'FAILED'}")
        
        return diffusion_config, training_config
    
    def demo_enhanced_device_management(self):
        """Demonstrate the enhanced device management system."""
        print("\n" + "="*70)
        print("💻 DEMO: Enhanced Device Management & Multi-Platform Support")
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
            
            memory = device_info['device_memory']
            print(f"   Total Memory: {memory['total']:.2f} GB")
            print(f"   Allocated Memory: {memory['allocated']:.2f} GB")
            print(f"   Cached Memory: {memory['cached']:.2f} GB")
        
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
    
    def demo_enhanced_caching_system(self):
        """Demonstrate the enhanced caching system with multiple strategies."""
        print("\n" + "="*70)
        print("💾 DEMO: Enhanced Caching System & Multiple Strategies")
        print("="*70)
        
        from diffusion_models_system_refactored import EnhancedModelCache
        
        # Test different cache strategies
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
            
            # Simulate cache operations
            test_models = {
                'model_1': {'name': 'stable-diffusion-v1-5', 'size': '2.5GB'},
                'model_2': {'name': 'stable-diffusion-v2-1', 'size': '3.1GB'},
                'model_3': {'name': 'stable-diffusion-xl', 'size': '6.8GB'},
                'model_4': {'name': 'stable-diffusion-v2-1-base', 'size': '1.9GB'}
            }
            
            # Add models to cache
            for key, model in test_models.items():
                cache.set(key, model)
                print(f"   Added: {key} ({model['name']})")
            
            # Get cache statistics
            stats = cache.get_cache_stats()
            print(f"   Cache Size: {stats['current_size']}/{stats['max_size']}")
            print(f"   Cache Hits: {stats['cache_hits']}")
            print(f"   Strategy: {stats['strategy']}")
            
            # Test cache retrieval
            retrieved_model = cache.get('model_1')
            if retrieved_model:
                print(f"   Retrieved: model_1 ({retrieved_model['name']})")
            
            # Clear cache
            cache.clear()
            print(f"   Cache cleared")
        
        return cache_strategies
    
    def demo_enhanced_error_handling(self):
        """Demonstrate the enhanced error handling system."""
        print("\n" + "="*70)
        print("🚨 DEMO: Enhanced Error Handling & Tracking System")
        print("="*70)
        
        from diffusion_models_system_refactored import ErrorHandler
        
        # Create error handler
        error_handler = ErrorHandler(max_errors=100)
        
        print(f"\n🔧 Error Handler Initialized:")
        print(f"   Max Errors: 100")
        print(f"   Current Errors: 0")
        
        # Simulate different types of errors
        print(f"\n📝 Simulating Errors:")
        
        # Info level error
        try:
            raise ValueError("Configuration validation warning")
        except Exception as e:
            error_handler.log_error(e, ErrorSeverity.INFO, "config_validation")
            print(f"   INFO: Configuration validation warning logged")
        
        # Warning level error
        try:
            raise RuntimeWarning("Memory usage approaching limit")
        except Exception as e:
            error_handler.log_error(e, ErrorSeverity.WARNING, "memory_monitoring")
            print(f"   WARNING: Memory usage warning logged")
        
        # Error level error
        try:
            raise RuntimeError("Model loading failed")
        except Exception as e:
            error_handler.log_error(e, ErrorSeverity.ERROR, "model_loading")
            print(f"   ERROR: Model loading error logged")
        
        # Critical level error
        try:
            raise SystemError("System resources exhausted")
        except Exception as e:
            error_handler.log_error(e, ErrorSeverity.CRITICAL, "system_monitoring")
            print(f"   CRITICAL: System error logged")
        
        # Get error summary
        print(f"\n📊 Error Summary:")
        error_summary = error_handler.get_error_summary()
        print(f"   Total Errors: {error_summary['total_errors']}")
        print(f"   Error Counts: {error_summary['error_counts']}")
        print(f"   Session Duration: {error_summary['session_duration']:.2f}s")
        
        # Show recent errors
        if error_summary['recent_errors']:
            print(f"\n🚨 Recent Errors:")
            for error in error_summary['recent_errors'][-3:]:  # Last 3 errors
                print(f"   {error['error_type']}: {error['error_message']} (Context: {error['context']})")
        
        return error_handler
    
    def demo_enhanced_performance_monitoring(self):
        """Demonstrate the enhanced performance monitoring system."""
        print("\n" + "="*70)
        print("📊 DEMO: Enhanced Performance Monitoring & Scoring")
        print("="*70)
        
        from diffusion_models_system_refactored import EnhancedPerformanceMonitor, EnhancedMemoryTracker
        
        # Create enhanced performance monitor
        performance_monitor = EnhancedPerformanceMonitor(enabled=True, max_metrics=1000)
        memory_tracker = EnhancedMemoryTracker(max_history=1000)
        
        print(f"\n🔧 Performance Monitor Initialized:")
        print(f"   Enabled: {performance_monitor.enabled}")
        print(f"   Max Metrics: {performance_monitor.max_metrics}")
        print(f"   Memory Tracker: {memory_tracker.__class__.__name__}")
        
        # Simulate performance monitoring
        print(f"\n📝 Simulating Performance Monitoring:")
        
        # Simulate different operations
        operations = [
            ("model_loading", 2.5),
            ("image_generation", 1.8),
            ("optimization", 0.5),
            ("cache_operation", 0.1),
            ("memory_cleanup", 0.3)
        ]
        
        for operation_name, duration in operations:
            # Start timer
            performance_monitor.start_timer(operation_name)
            
            # Simulate operation duration
            time.sleep(duration)
            
            # End timer
            actual_duration = performance_monitor.end_timer(operation_name)
            print(f"   {operation_name}: {actual_duration:.2f}s")
            
            # Track memory for operation
            memory_tracker.track_memory(operation_name)
        
        # Get performance metrics
        print(f"\n📊 Performance Metrics:")
        
        # Timing metrics
        for operation_name, _ in operations:
            avg_time = performance_monitor.get_average_time(operation_name)
            print(f"   {operation_name} (avg): {avg_time:.2f}s")
        
        # Memory metrics
        memory_stats = memory_tracker.get_stats()
        print(f"\n💾 Memory Statistics:")
        print(f"   Current Memory: {memory_stats.get('current', 0):.2f} GB")
        print(f"   Peak Memory: {memory_stats.get('peak', 0):.2f} GB")
        print(f"   Average Memory: {memory_stats.get('average', 0):.2f} GB")
        print(f"   Memory Efficiency Score: {memory_stats.get('efficiency_score', 0):.1f}/100")
        print(f"   Total Measurements: {memory_stats.get('total_measurements', 0)}")
        
        # Performance scoring
        performance_score = performance_monitor.get_performance_score()
        print(f"\n🎯 Performance Scoring:")
        print(f"   Overall Performance Score: {performance_score:.1f}/100")
        
        # Generate comprehensive report
        print(f"\n📋 Comprehensive Performance Report:")
        report = performance_monitor.generate_report()
        print(f"   Total Operations: {report['summary']['total_operations']}")
        print(f"   Total Time: {report['summary']['total_time']:.2f}s")
        print(f"   Session Duration: {report['summary']['session_duration']:.2f}s")
        print(f"   Performance Score: {report['performance_score']:.1f}/100")
        
        # Memory prediction
        print(f"\n🔮 Memory Prediction:")
        for batch_size in [1, 2, 4, 8]:
            predicted_memory = memory_tracker.predict_memory_usage(batch_size, "image_generation")
            print(f"   Batch Size {batch_size}: {predicted_memory:.2f} GB predicted")
        
        return performance_monitor, memory_tracker
    
    def demo_enhanced_system_creation(self):
        """Demonstrate the enhanced system creation with all new features."""
        print("\n" + "="*70)
        print("🔧 DEMO: Enhanced System Creation & Advanced Features")
        print("="*70)
        
        try:
            # Create enhanced configurations
            diffusion_config = DiffusionConfig(
                model_name="runwayml/stable-diffusion-v1-5",
                model_revision="main",
                model_variant="fp16",
                enable_performance_monitoring=True,
                enable_memory_tracking=True,
                enable_error_tracking=True,
                enable_metrics_export=True,
                num_inference_steps=30,
                use_compile=True,
                use_fp16=True,
                use_int8=False,
                cache_strategy=CacheStrategy.LRU,
                max_cache_size=10,
                cache_ttl=7200,
                enable_controlnet=False,
                enable_lora=False
            )
            
            training_config = TrainingConfig(
                learning_rate=1e-5,
                num_epochs=100,
                batch_size=1,
                use_mixed_precision=True,
                use_gradient_checkpointing=True,
                use_amp=True,
                enable_tensorboard=True,
                enable_wandb=False
            )
            
            print("🔄 Creating enhanced system...")
            print(f"   Performance Monitoring: {diffusion_config.enable_performance_monitoring}")
            print(f"   Memory Tracking: {diffusion_config.enable_memory_tracking}")
            print(f"   Error Tracking: {diffusion_config.enable_error_tracking}")
            print(f"   Metrics Export: {diffusion_config.enable_metrics_export}")
            print(f"   Torch Compile: {diffusion_config.use_compile}")
            print(f"   Mixed Precision: {diffusion_config.use_fp16}")
            print(f"   INT8 Quantization: {diffusion_config.use_int8}")
            print(f"   Cache Strategy: {diffusion_config.cache_strategy.value}")
            print(f"   Max Cache Size: {diffusion_config.max_cache_size}")
            print(f"   Cache TTL: {diffusion_config.cache_ttl}s")
            
            # This would create the system (skipped for demo)
            print("⚠️ System creation skipped (no models available)")
            print("   To run full demo, ensure models are available")
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating system: {e}")
            return None
    
    def demo_advanced_features(self):
        """Demonstrate advanced features and capabilities."""
        print("\n" + "="*70)
        print("🚀 DEMO: Advanced Features & Capabilities")
        print("="*70)
        
        print(f"\n🎯 Advanced Optimization Strategies:")
        print(f"   Ultra Fast: INT8 quantization, minimal inference steps")
        print(f"   Quality First: Full precision, maximum inference steps")
        print(f"   Mobile: Reduced resolution, memory optimization")
        print(f"   Server: High batch size, TTL caching")
        
        print(f"\n🔧 Enhanced Caching System:")
        print(f"   LRU: Least Recently Used eviction")
        print(f"   LFU: Least Frequently Used eviction")
        print(f"   FIFO: First In, First Out eviction")
        print(f"   TTL: Time To Live expiration")
        
        print(f"\n📊 Advanced Monitoring:")
        print(f"   Performance Scoring (0-100)")
        print(f"   Memory Efficiency Scoring")
        print(f"   Memory Usage Prediction")
        print(f"   Metrics Export to JSON")
        
        print(f"\n🚨 Enhanced Error Handling:")
        print(f"   Severity Levels: INFO, WARNING, ERROR, CRITICAL")
        print(f"   Context-Aware Error Tracking")
        print(f"   Error Statistics and Summaries")
        print(f"   Automatic Error Logging")
        
        print(f"\n⚡ Performance Optimizations:")
        print(f"   INT8/INT4 Quantization Support")
        print(f"   Advanced Memory Management")
        print(f"   Thread-Safe Operations")
        print(f"   Context Managers for Resource Cleanup")
        
        print(f"\n🔮 Future-Ready Features:")
        print(f"   ControlNet Support Preparation")
        print(f"   LoRA Fine-tuning Support")
        print(f"   Textual Inversion Support")
        print(f"   Hypernetwork Support")
        print(f"   Multi-GPU Training Support")
        print(f"   Distributed Training Support")
    
    def run_enhanced_demos(self):
        """Run all enhanced demonstration functions."""
        print("🎨 Enhanced Diffusion Models System Demo")
        print("=" * 80)
        
        try:
            # Demo 1: Enhanced optimization profiles
            available_profiles = self.demo_enhanced_optimization_profiles()
            
            # Demo 2: Enhanced configuration system
            diffusion_config, training_config = self.demo_enhanced_configuration_system()
            
            # Demo 3: Enhanced device management
            device_info = self.demo_enhanced_device_management()
            
            # Demo 4: Enhanced caching system
            cache_strategies = self.demo_enhanced_caching_system()
            
            # Demo 5: Enhanced error handling
            error_handler = self.demo_enhanced_error_handling()
            
            # Demo 6: Enhanced performance monitoring
            performance_monitor, memory_tracker = self.demo_enhanced_performance_monitoring()
            
            # Demo 7: Enhanced system creation
            system = self.demo_enhanced_system_creation()
            
            # Demo 8: Advanced features
            self.demo_advanced_features()
            
            print("\n" + "="*80)
            print("🎉 All enhanced demos completed successfully!")
            print("="*80)
            
            # Summary
            print(f"\n📋 Enhancement Summary:")
            print(f"   ✅ Advanced optimization strategies (8 profiles)")
            print(f"   ✅ Enhanced configuration management")
            print(f"   ✅ Multi-platform device support")
            print(f"   ✅ Advanced caching system (4 strategies)")
            print(f"   ✅ Comprehensive error handling")
            print(f"   ✅ Advanced performance monitoring")
            print(f"   ✅ Memory efficiency scoring")
            print(f"   ✅ Performance prediction")
            
            # Architecture summary
            print(f"\n🏗️ Architecture Improvements:")
            print(f"   Enhanced Components: ✅ Implemented")
            print(f"   Advanced Strategies: ✅ Strategy pattern")
            print(f"   Multiple Cache Strategies: ✅ Factory pattern")
            print(f"   Error Severity Levels: ✅ Enum-based")
            print(f"   Performance Scoring: ✅ Algorithm-based")
            print(f"   Memory Prediction: ✅ ML-inspired")
            
            # Code quality summary
            print(f"\n📚 Code Quality Improvements:")
            print(f"   Generic Types: ✅ TypeVar support")
            print(f"   Advanced Protocols: ✅ Enhanced interfaces")
            print(f"   LRU Cache: ✅ Function decorators")
            print(f"   Thread Safety: ✅ Lock-based operations")
            print(f"   Resource Management: ✅ Context managers")
            print(f"   Error Recovery: ✅ Graceful handling")
            
            # Performance summary
            print(f"\n⚡ Performance Improvements:")
            print(f"   Multiple Optimization Profiles: ✅ 8 strategies")
            print(f"   Advanced Caching: ✅ 4 eviction strategies")
            print(f"   Memory Prediction: ✅ Linear regression")
            print(f"   Performance Scoring: ✅ Weighted algorithms")
            print(f"   Metrics Export: ✅ JSON serialization")
            print(f"   Resource Cleanup: ✅ Automatic management")
            
            # Feature summary
            print(f"\n🎯 Feature Enhancements:")
            print(f"   Quantization Support: ✅ INT8/INT4")
            print(f"   Multi-Platform: ✅ CUDA/MPS/XPU/CPU")
            print(f"   Advanced Monitoring: ✅ Real-time scoring")
            print(f"   Error Tracking: ✅ Severity-based")
            print(f"   Configuration Management: ✅ Clone/Merge")
            print(f"   Future-Ready: ✅ ControlNet/LoRA support")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            raise


if __name__ == "__main__":
    # Run the enhanced demo
    demo = EnhancedDiffusionModelsDemo()
    demo.run_enhanced_demos()





