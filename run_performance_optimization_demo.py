#!/usr/bin/env python3
"""
Performance Optimization Demo for Diffusion Models

This script demonstrates the comprehensive performance optimization capabilities
of the diffusion models system, including memory optimization, training acceleration,
and performance monitoring.
"""

import torch
import torch.nn as nn
import numpy as np
import time
import psutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_diffusion_model():
    """Create a mock diffusion model for demonstration."""
    class MockDiffusionModel(nn.Module):
        def __init__(self, hidden_size=768, num_layers=12):
            super().__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            
            # Simulate UNet-like architecture
            self.input_proj = nn.Conv2d(3, hidden_size, 3, padding=1)
            self.layers = nn.ModuleList([
                nn.TransformerEncoderLayer(
                    d_model=hidden_size,
                    nhead=8,
                    dim_feedforward=hidden_size * 4,
                    dropout=0.1
                ) for _ in range(num_layers)
            ])
            self.output_proj = nn.Conv2d(hidden_size, 3, 3, padding=1)
            
        def forward(self, x, timesteps=None, text_embeddings=None):
            # Simulate diffusion model forward pass
            x = self.input_proj(x)
            x = x.flatten(2).transpose(1, 2)  # (B, H*W, C)
            
            for layer in self.layers:
                x = layer(x)
            
            x = x.transpose(1, 2).reshape(x.shape[0], self.hidden_size, 
                                         int(np.sqrt(x.shape[1])), int(np.sqrt(x.shape[1])))
            x = self.output_proj(x)
            return x
    
    return MockDiffusionModel()

def create_mock_dataset(batch_size=4, image_size=64):
    """Create mock dataset for demonstration."""
    images = torch.randn(batch_size, 3, image_size, image_size)
    timesteps = torch.randint(0, 1000, (batch_size,))
    text_embeddings = torch.randn(batch_size, 77, 768)
    
    return {
        'images': images,
        'timesteps': timesteps,
        'text_embeddings': text_embeddings
    }

def demonstrate_basic_optimization():
    """Demonstrate basic performance optimization."""
    logger.info("🚀 Demonstrating Basic Performance Optimization")
    logger.info("=" * 60)
    
    try:
        from core.diffusion_performance_optimizer import (
            DiffusionPerformanceOptimizer, 
            PerformanceConfig, 
            OptimizationLevel
        )
        
        # Create basic configuration
        config = PerformanceConfig(
            optimization_level=OptimizationLevel.BASIC,
            enable_performance_monitoring=True,
            enable_cudnn_benchmark=True,
            enable_tf32=True
        )
        
        # Create optimizer
        optimizer = DiffusionPerformanceOptimizer(config)
        
        # Get optimization recommendations
        recommendations = optimizer.get_optimization_recommendations()
        logger.info("📋 Optimization Recommendations:")
        for rec in recommendations:
            logger.info(f"  {rec}")
        
        # Cleanup
        optimizer.cleanup()
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import performance optimizer: {e}")
        logger.info("  This is expected if the core modules are not available")

def demonstrate_advanced_optimization():
    """Demonstrate advanced performance optimization."""
    logger.info("\n🔧 Demonstrating Advanced Performance Optimization")
    logger.info("=" * 60)
    
    try:
        from core.diffusion_performance_optimizer import (
            DiffusionPerformanceOptimizer, 
            PerformanceConfig, 
            OptimizationLevel,
            MemoryOptimization,
            TrainingAcceleration
        )
        
        # Create advanced configuration
        config = PerformanceConfig(
            optimization_level=OptimizationLevel.ADVANCED,
            memory_optimizations=[
                MemoryOptimization.GRADIENT_CHECKPOINTING,
                MemoryOptimization.ATTENTION_SLICING,
                MemoryOptimization.VAE_SLICING
            ],
            training_accelerations=[
                TrainingAcceleration.MIXED_PRECISION,
                TrainingAcceleration.COMPILE_MODEL,
                TrainingAcceleration.GRADIENT_ACCUMULATION
            ],
            enable_performance_monitoring=True,
            performance_logging_interval=50,
            memory_profiling_interval=25
        )
        
        # Create optimizer
        optimizer = DiffusionPerformanceOptimizer(config)
        
        # Create mock model
        model = create_mock_diffusion_model()
        
        # Apply optimizations
        optimized_model = optimizer.optimize_model(model)
        logger.info(f"✅ Model optimized: {type(optimized_model)}")
        
        # Cleanup
        optimizer.cleanup()
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import performance optimizer: {e}")
        logger.info("  This is expected if the core modules are not available")

def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    logger.info("\n📊 Demonstrating Performance Monitoring")
    logger.info("=" * 60)
    
    try:
        from core.diffusion_performance_optimizer import (
            DiffusionPerformanceOptimizer, 
            PerformanceConfig, 
            OptimizationLevel
        )
        
        # Create configuration with monitoring enabled
        config = PerformanceConfig(
            optimization_level=OptimizationLevel.BASIC,
            enable_performance_monitoring=True,
            performance_logging_interval=10,
            memory_profiling_interval=5
        )
        
        # Create optimizer
        optimizer = DiffusionPerformanceOptimizer(config)
        
        # Simulate training steps with monitoring
        logger.info("🔄 Simulating training steps with performance monitoring...")
        
        for step in range(20):
            # Simulate forward pass
            with optimizer.performance_context("Forward Pass"):
                time.sleep(0.01)  # Simulate computation
            
            # Simulate backward pass
            with optimizer.performance_context("Backward Pass"):
                time.sleep(0.015)  # Simulate computation
            
            # Monitor performance
            optimizer.monitor_performance(step, epoch=0)
        
        # Get final recommendations
        recommendations = optimizer.get_optimization_recommendations()
        logger.info("\n📋 Final Optimization Recommendations:")
        for rec in recommendations:
            logger.info(f"  {rec}")
        
        # Save performance report
        report_path = "performance_optimization_report.json"
        optimizer.save_performance_report(report_path)
        
        # Cleanup
        optimizer.cleanup()
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import performance optimizer: {e}")
        logger.info("  This is expected if the core modules are not available")

def demonstrate_memory_optimization():
    """Demonstrate memory optimization techniques."""
    logger.info("\n💾 Demonstrating Memory Optimization")
    logger.info("=" * 60)
    
    try:
        from core.diffusion_performance_optimizer import (
            DiffusionPerformanceOptimizer, 
            PerformanceConfig, 
            OptimizationLevel,
            MemoryOptimization
        )
        
        # Create configuration focused on memory optimization
        config = PerformanceConfig(
            optimization_level=OptimizationLevel.ADVANCED,
            memory_optimizations=[
                MemoryOptimization.GRADIENT_CHECKPOINTING,
                MemoryOptimization.ATTENTION_SLICING,
                MemoryOptimization.MODEL_OFFLOADING
            ],
            enable_performance_monitoring=True,
            memory_profiling_interval=1
        )
        
        # Create optimizer
        optimizer = DiffusionPerformanceOptimizer(config)
        
        # Create large model to demonstrate memory optimization
        large_model = create_mock_diffusion_model(hidden_size=1024, num_layers=24)
        
        logger.info(f"📦 Large model created with {sum(p.numel() for p in large_model.parameters()):,} parameters")
        
        # Apply memory optimizations
        optimized_model = optimizer.optimize_model(large_model)
        
        # Monitor memory usage
        if torch.cuda.is_available():
            logger.info("💾 GPU Memory Usage:")
            logger.info(f"  Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
            logger.info(f"  Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
        
        # Cleanup
        optimizer.cleanup()
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import performance optimizer: {e}")
        logger.info("  This is expected if the core modules are not available")

def demonstrate_training_acceleration():
    """Demonstrate training acceleration techniques."""
    logger.info("\n⚡ Demonstrating Training Acceleration")
    logger.info("=" * 60)
    
    try:
        from core.diffusion_performance_optimizer import (
            DiffusionPerformanceOptimizer, 
            PerformanceConfig, 
            OptimizationLevel,
            TrainingAcceleration
        )
        
        # Create configuration focused on training acceleration
        config = PerformanceConfig(
            optimization_level=OptimizationLevel.AGGRESSIVE,
            training_accelerations=[
                TrainingAcceleration.MIXED_PRECISION,
                TrainingAcceleration.COMPILE_MODEL,
                TrainingAcceleration.GRADIENT_ACCUMULATION
            ],
            enable_performance_monitoring=True,
            performance_logging_interval=5
        )
        
        # Create optimizer
        optimizer = DiffusionPerformanceOptimizer(config)
        
        # Create model and data
        model = create_mock_diffusion_model()
        batch = create_mock_dataset()
        
        # Apply optimizations
        optimized_model = optimizer.optimize_model(model)
        
        # Simulate training with acceleration
        logger.info("🔄 Simulating accelerated training...")
        
        for step in range(10):
            with optimizer.performance_context("Accelerated Training Step"):
                # Simulate forward pass
                with optimizer.performance_context("Forward Pass"):
                    time.sleep(0.005)
                
                # Simulate backward pass
                with optimizer.performance_context("Backward Pass"):
                    time.sleep(0.008)
                
                # Monitor performance
                optimizer.monitor_performance(step, epoch=0)
        
        # Cleanup
        optimizer.cleanup()
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import performance optimizer: {e}")
        logger.info("  This is expected if the core modules are not available")

def demonstrate_benchmarking():
    """Demonstrate model performance benchmarking."""
    logger.info("\n🏁 Demonstrating Model Performance Benchmarking")
    logger.info("=" * 60)
    
    try:
        from core.diffusion_performance_optimizer import benchmark_model_performance
        
        # Create model
        model = create_mock_diffusion_model()
        
        # Benchmark performance
        input_shape = (4, 3, 64, 64)  # Batch size 4, 3 channels, 64x64 images
        
        logger.info(f"🔍 Benchmarking model with input shape: {input_shape}")
        
        # Benchmark without optimization
        baseline_results = benchmark_model_performance(model, input_shape, num_runs=50, warmup_runs=5)
        
        logger.info("📊 Baseline Performance Results:")
        logger.info(f"  Average time: {baseline_results['avg_time']:.6f}s")
        logger.info(f"  Throughput: {baseline_results['throughput']:.2f} samples/second")
        logger.info(f"  Total time: {baseline_results['total_time']:.4f}s")
        
        # Benchmark with different input sizes
        input_sizes = [(1, 3, 32, 32), (2, 3, 64, 64), (4, 3, 128, 128)]
        
        logger.info("\n📏 Performance vs Input Size:")
        for shape in input_sizes:
            results = benchmark_model_performance(model, shape, num_runs=20, warmup_runs=3)
            logger.info(f"  {shape}: {results['avg_time']:.6f}s, {results['throughput']:.2f} samples/s")
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import benchmarking function: {e}")
        logger.info("  This is expected if the core modules are not available")

def demonstrate_system_analysis():
    """Demonstrate system resource analysis."""
    logger.info("\n🔍 Demonstrating System Resource Analysis")
    logger.info("=" * 60)
    
    # CPU information
    logger.info("🖥️ CPU Information:")
    logger.info(f"  Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
    logger.info(f"  Usage: {psutil.cpu_percent(interval=1):.1f}%")
    
    # Memory information
    memory = psutil.virtual_memory()
    logger.info("💾 Memory Information:")
    logger.info(f"  Total: {memory.total / (1024**3):.1f} GB")
    logger.info(f"  Available: {memory.available / (1024**3):.1f} GB")
    logger.info(f"  Used: {memory.percent:.1f}%")
    
    # GPU information
    if torch.cuda.is_available():
        logger.info("🎮 GPU Information:")
        logger.info(f"  Device: {torch.cuda.get_device_name(0)}")
        logger.info(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
        logger.info(f"  CUDA Version: {torch.version.cuda}")
        
        # Current GPU memory usage
        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        logger.info(f"  Current Allocated: {allocated:.2f} GB")
        logger.info(f"  Current Reserved: {reserved:.2f} GB")
    else:
        logger.info("🎮 GPU: Not available (CUDA)")
    
    # PyTorch information
    logger.info("🔥 PyTorch Information:")
    logger.info(f"  Version: {torch.__version__}")
    logger.info(f"  CUDA Available: {torch.cuda.is_available()}")
    logger.info(f"  MPS Available: {torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False}")

def main():
    """Main demonstration function."""
    logger.info("🚀 Starting Performance Optimization Demo")
    logger.info("=" * 80)
    
    # System information
    demonstrate_system_analysis()
    
    # Performance optimization demonstrations
    demonstrate_basic_optimization()
    demonstrate_advanced_optimization()
    demonstrate_performance_monitoring()
    demonstrate_memory_optimization()
    demonstrate_training_acceleration()
    demonstrate_benchmarking()
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Performance Optimization Demo completed!")
    logger.info("\n💡 Key takeaways:")
    logger.info("  - Performance optimization can significantly improve training speed")
    logger.info("  - Memory optimization enables training larger models")
    logger.info("  - Performance monitoring helps identify bottlenecks")
    logger.info("  - Different optimization levels for different needs")
    logger.info("  - System-aware optimization recommendations")

if __name__ == "__main__":
    main()
