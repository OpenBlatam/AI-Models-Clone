"""
Configuration Module - Optimizer Configuration and Feature Detection.

Centralized configuration for all optimization components with automatic
feature detection and performance tuning.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional

# Feature detection
try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

try:
    import blosc2
    BLOSC2_AVAILABLE = True
except ImportError:
    BLOSC2_AVAILABLE = False

try:
    import polars
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

try:
    import pyarrow
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

try:
    import cupy
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import numexpr
    import bottleneck
    ADVANCED_MATH_AVAILABLE = True
except ImportError:
    ADVANCED_MATH_AVAILABLE = False


class OptimizationLevel(Enum):
    """Optimization levels from basic to experimental."""
    BASIC = "basic"
    ADVANCED = "advanced" 
    ULTRA = "ultra"
    EXPERIMENTAL = "experimental"


@dataclass
class OptimizationConfig:
    """Unified configuration for all optimizers."""
    
    # Core settings
    level: OptimizationLevel = OptimizationLevel.ADVANCED
    max_workers: int = min(32, os.cpu_count() * 2)
    enable_async: bool = True
    
    # Feature flags (auto-detected by default)
    enable_jit: bool = NUMBA_AVAILABLE
    enable_gpu: bool = GPU_AVAILABLE
    enable_uvloop: bool = UVLOOP_AVAILABLE
    enable_advanced_math: bool = ADVANCED_MATH_AVAILABLE
    
    # Memory settings
    memory_threshold_percent: float = 85.0
    memory_pool_size_mb: int = 1024
    enable_memory_mapping: bool = True
    gc_threshold: int = 700
    
    # Concurrency settings
    max_concurrent_tasks: int = 100
    request_timeout_seconds: float = 30.0
    
    # Serialization settings
    serialization_format: str = "orjson"  # orjson, msgpack, pickle
    enable_compression: bool = BLOSC2_AVAILABLE
    compression_algorithm: str = "blosc2" if BLOSC2_AVAILABLE else "lz4"
    
    # Hashing settings
    hash_algorithm: str = "blake3" if BLAKE3_AVAILABLE else "xxhash"
    
    # Data processing settings
    use_polars: bool = POLARS_AVAILABLE
    use_arrow: bool = ARROW_AVAILABLE
    
    # Performance thresholds
    max_response_time_ms: float = 1000.0
    max_cpu_usage_percent: float = 90.0
    
    # I/O settings
    io_buffer_size: int = 8192 * 16  # 128KB
    
    def get_feature_report(self) -> Dict[str, Any]:
        """Get comprehensive feature availability report."""
        return {
            "level": self.level.value,
            "libraries_available": {
                "blake3": BLAKE3_AVAILABLE,
                "uvloop": UVLOOP_AVAILABLE,
                "numba": NUMBA_AVAILABLE,
                "blosc2": BLOSC2_AVAILABLE,
                "polars": POLARS_AVAILABLE,
                "pyarrow": ARROW_AVAILABLE,
                "cupy": GPU_AVAILABLE,
                "advanced_math": ADVANCED_MATH_AVAILABLE
            },
            "enabled_features": {
                "jit_compilation": self.enable_jit and NUMBA_AVAILABLE,
                "gpu_acceleration": self.enable_gpu and GPU_AVAILABLE,
                "uvloop_eventloop": self.enable_uvloop and UVLOOP_AVAILABLE,
                "compression": self.enable_compression and BLOSC2_AVAILABLE,
                "advanced_math": self.enable_advanced_math and ADVANCED_MATH_AVAILABLE,
                "fast_data_processing": self.use_polars and POLARS_AVAILABLE
            },
            "performance_config": {
                "max_workers": self.max_workers,
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "hash_algorithm": self.hash_algorithm,
                "serialization_format": self.serialization_format,
                "compression_algorithm": self.compression_algorithm
            }
        }
    
    def auto_tune(self) -> "OptimizationConfig":
        """Auto-tune configuration based on system capabilities."""
        # Auto-detect optimal worker count
        cpu_count = os.cpu_count()
        if cpu_count >= 16:
            self.max_workers = min(64, cpu_count * 4)
            self.max_concurrent_tasks = 500
        elif cpu_count >= 8:
            self.max_workers = min(32, cpu_count * 3)
            self.max_concurrent_tasks = 200
        else:
            self.max_workers = min(16, cpu_count * 2)
            self.max_concurrent_tasks = 100
        
        # Auto-tune memory settings based on available RAM
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            if memory_gb >= 32:
                self.memory_pool_size_mb = 2048
                self.memory_threshold_percent = 80.0
            elif memory_gb >= 16:
                self.memory_pool_size_mb = 1024
                self.memory_threshold_percent = 85.0
            else:
                self.memory_pool_size_mb = 512
                self.memory_threshold_percent = 90.0
        except ImportError:
            pass
        
        # Auto-select best algorithms
        if BLAKE3_AVAILABLE:
            self.hash_algorithm = "blake3"
        
        if BLOSC2_AVAILABLE:
            self.compression_algorithm = "blosc2"
            self.enable_compression = True
        
        if POLARS_AVAILABLE:
            self.use_polars = True
        
        if UVLOOP_AVAILABLE:
            self.enable_uvloop = True
        
        return self
    
    @classmethod
    def for_production(cls) -> "OptimizationConfig":
        """Create production-optimized configuration."""
        config = cls(
            level=OptimizationLevel.ULTRA,
            enable_jit=NUMBA_AVAILABLE,
            enable_gpu=False,  # Conservative for production
            enable_uvloop=UVLOOP_AVAILABLE,
            memory_threshold_percent=80.0,
            max_response_time_ms=500.0,
            max_concurrent_tasks=1000
        )
        return config.auto_tune()
    
    @classmethod 
    def for_development(cls) -> "OptimizationConfig":
        """Create development-friendly configuration."""
        return cls(
            level=OptimizationLevel.ADVANCED,
            max_workers=min(8, os.cpu_count()),
            max_concurrent_tasks=50,
            memory_threshold_percent=90.0,
            enable_compression=False  # Faster for development
        )
    
    @classmethod
    def for_testing(cls) -> "OptimizationConfig":
        """Create testing configuration with minimal overhead."""
        return cls(
            level=OptimizationLevel.BASIC,
            max_workers=2,
            max_concurrent_tasks=10,
            enable_jit=False,
            enable_compression=False,
            enable_memory_mapping=False
        )


# Global feature flags for easy access
FEATURES = {
    "BLAKE3_AVAILABLE": BLAKE3_AVAILABLE,
    "UVLOOP_AVAILABLE": UVLOOP_AVAILABLE,
    "NUMBA_AVAILABLE": NUMBA_AVAILABLE,
    "BLOSC2_AVAILABLE": BLOSC2_AVAILABLE,
    "POLARS_AVAILABLE": POLARS_AVAILABLE,
    "ARROW_AVAILABLE": ARROW_AVAILABLE,
    "GPU_AVAILABLE": GPU_AVAILABLE,
    "ADVANCED_MATH_AVAILABLE": ADVANCED_MATH_AVAILABLE
}


def get_optimization_recommendations() -> Dict[str, str]:
    """Get recommendations for missing optimization libraries."""
    recommendations = []
    
    if not BLAKE3_AVAILABLE:
        recommendations.append("Install blake3 for fastest hashing: pip install blake3")
    
    if not UVLOOP_AVAILABLE:
        recommendations.append("Install uvloop for faster event loop: pip install uvloop")
    
    if not NUMBA_AVAILABLE:
        recommendations.append("Install numba for JIT compilation: pip install numba")
    
    if not BLOSC2_AVAILABLE:
        recommendations.append("Install blosc2 for ultra-fast compression: pip install blosc2")
    
    if not POLARS_AVAILABLE:
        recommendations.append("Install polars for ultra-fast data processing: pip install polars")
    
    if not ARROW_AVAILABLE:
        recommendations.append("Install pyarrow for columnar data: pip install pyarrow")
    
    return {
        "missing_libraries": len(recommendations),
        "recommendations": recommendations,
        "install_all": "pip install blake3 uvloop numba blosc2 polars pyarrow"
    }


__all__ = [
    "OptimizationConfig",
    "OptimizationLevel", 
    "FEATURES",
    "get_optimization_recommendations"
] 