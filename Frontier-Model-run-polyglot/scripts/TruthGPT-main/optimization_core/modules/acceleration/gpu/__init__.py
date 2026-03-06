"""
GPU Accelerator Package
=======================

Advanced hardware acceleration utilizing PyTorch CUDA functionality with
neural, transcendent, and quantum hooks.
"""
from typing import Any
from optimization_core.utils.dependency_manager import resolve_lazy_import
from contextlib import contextmanager

# Export classes via lazy loading where possible
_LAZY_IMPORTS = {
    'GPUAcceleratorConfig': '.config',
    'create_gpu_accelerator_config': '.config',
    'GPUDeviceManager': '.device',
    'GPUMemoryManager': '.memory',
    'CUDAOptimizer': '.optimizer',
    'GPUStreamManager': '.streams',
    'GPUPerformanceMonitor': '.monitor',
    'GPUAccelerator': '.system',
    'EnhancedGPUAccelerator': '.system',
}

def __getattr__(name: str) -> Any:
    return resolve_lazy_import(name, __package__ or 'gpu', _LAZY_IMPORTS)

def create_gpu_accelerator(config) -> 'GPUAccelerator':
    """Create basic GPU accelerator instance."""
    from .system import GPUAccelerator
    return GPUAccelerator(config)

def create_enhanced_gpu_accelerator(config) -> 'EnhancedGPUAccelerator':
    """Create enhanced GPU accelerator instance."""
    from .system import EnhancedGPUAccelerator
    return EnhancedGPUAccelerator(config)

@contextmanager
def gpu_accelerator_context(config):
    """Context manager for GPU accelerator operations."""
    accelerator = create_gpu_accelerator(config)
    try:
        yield accelerator
    finally:
        accelerator.cleanup()

@contextmanager
def enhanced_gpu_accelerator_context(config):
    """Context manager for enhanced GPU accelerator operations."""
    accelerator = create_enhanced_gpu_accelerator(config)
    try:
        yield accelerator
    finally:
        accelerator.cleanup()

def example_gpu_acceleration():
    """Example of GPU acceleration workflow."""
    import torch
    import torch.nn as nn
    from .config import create_gpu_accelerator_config
    
    # Create a simple model
    model = nn.Sequential(
        nn.Linear(1024, 512),
        nn.ReLU(),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.Linear(256, 128)
    )
    
    # Create configuration
    config = create_gpu_accelerator_config(
        device_id=0,
        enable_amp=True,
        enable_cudnn=True,
        enable_tf32=True
    )
    
    # Create accelerator context
    with gpu_accelerator_context(config) as accelerator:
        # Optimize model
        optimized_model = accelerator.optimize_model(model)
        
        # Create input tensor
        input_tensor = torch.randn(32, 1024)
        
        # Benchmark
        benchmark_results = accelerator.benchmark(optimized_model, input_tensor)
        
        print(f"✅ GPU Acceleration Example Complete!")
        print(f"📊 Average Time: {benchmark_results['average_time']*1000:.2f}ms")
        print(f"⚡ Throughput: {benchmark_results['throughput']:.2f} ops/s")
        print(f"💾 Memory Allocated: {benchmark_results.get('memory_allocated', 0)/1024**2:.2f} MB")
    
    return optimized_model

__all__ = list(_LAZY_IMPORTS.keys()) + [
    'create_gpu_accelerator',
    'create_enhanced_gpu_accelerator',
    'gpu_accelerator_context',
    'enhanced_gpu_accelerator_context',
    'example_gpu_acceleration'
]
