"""
GPU Utilities Module

This module contains GPU-specific utilities and CUDA kernel optimizations.
"""

from __future__ import annotations

import importlib

__all__ = [
    'GPUUtils',
    'CUDAOptimizations',
    'OptimizedLayerNorm',
    'OptimizedRMSNorm',
    'EnhancedCUDAOptimizations',
]

_LAZY_IMPORTS = {
    'GPUUtils': 'optimization_core.modules.acceleration.gpu.gpu_utils',
    'CUDAOptimizations': 'optimization_core.modules.acceleration.gpu.cuda_kernels',
    'OptimizedLayerNorm': 'optimization_core.modules.acceleration.gpu.cuda_kernels',
    'OptimizedRMSNorm': 'optimization_core.modules.acceleration.gpu.cuda_kernels',
    'EnhancedCUDAOptimizations': 'optimization_core.modules.acceleration.gpu.enhanced_kernels',
}

_import_cache = {}


def __getattr__(name: str):
    """Lazy import system for GPU utility modules."""
    if name.startswith('_'):
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    if name in _import_cache:
        return _import_cache[name]
    
    module_path = _LAZY_IMPORTS[name]
    try:
        # Use absolute imports to avoid __package__ ambiguity
        module = importlib.import_module(module_path)
        obj = getattr(module, name)
        _import_cache[name] = obj
        return obj
    except (ImportError, AttributeError) as e:
        raise AttributeError(
            f"module '{__name__}' has no attribute '{name}'. "
            f"Failed to import: {e}"
        ) from e



