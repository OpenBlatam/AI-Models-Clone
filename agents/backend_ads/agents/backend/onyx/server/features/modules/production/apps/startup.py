"""
Startup Module for Onyx Features - Production Initialization.

Handles initialization of all high-performance optimizations, libraries,
and system configurations for optimal production performance.
"""

import asyncio
import sys
import os
import time
import warnings
from typing import Dict, Any, Optional
from pathlib import Path

# Core imports
import structlog
import psutil

# Try to import optimization libraries with graceful fallbacks
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False
    warnings.warn("uvloop not available - using default event loop")

try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False
    warnings.warn("orjson not available - using standard json")

try:
    import numba
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    warnings.warn("numba not available - JIT compilation disabled")

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    warnings.warn("polars not available - using pandas for DataFrames")

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Import our modules
from .config import get_config
from .optimization import setup_event_loop_optimization, OPTIMIZATION_CONFIG
from .performance_optimizers import (
    PerformanceOrchestrator, OptimizationConfig, create_performance_orchestrator
)
from .monitoring import setup_monitoring
from .exceptions import setup_exception_handlers

# Configure logging
logger = structlog.get_logger(__name__)


class SystemOptimizer:
    """System-level optimizations and configurations."""
    
    @staticmethod
    def optimize_python_settings():
        """Optimize Python interpreter settings."""
        # Optimize garbage collection
        import gc
        gc.set_threshold(700, 10, 10)  # More aggressive GC
        
        # Set recursion limit for deep processing
        sys.setrecursionlimit(3000)
        
        # Optimize string interning
        if hasattr(sys, 'intern'):
            # Pre-intern common strings
            common_strings = ['id', 'name', 'value', 'data', 'type', 'status', 'message']
            for s in common_strings:
                sys.intern(s)
    
    @staticmethod
    def optimize_system_resources():
        """Optimize system resource usage."""
        try:
            import resource
            
            # Increase file descriptor limit
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (min(hard, 65536), hard))
            
            # Optimize memory usage
            if hasattr(resource, 'RLIMIT_AS'):
                # Set virtual memory limit to 80% of available
                available_memory = psutil.virtual_memory().available
                max_memory = int(available_memory * 0.8)
                try:
                    resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
                except (OSError, ValueError):
                    # Ignore if we can't set memory limit
                    pass
            
            logger.info("System resources optimized")
            
        except ImportError:
            logger.warning("Resource module not available for optimization")
    
    @staticmethod
    def configure_numpy_optimizations():
        """Configure NumPy optimizations."""
        try:
            import numpy as np
            
            # Use all available CPU cores for NumPy operations
            num_cores = psutil.cpu_count()
            
            # Set environment variables for optimal NumPy performance
            os.environ['OMP_NUM_THREADS'] = str(num_cores)
            os.environ['OPENBLAS_NUM_THREADS'] = str(num_cores)
            os.environ['MKL_NUM_THREADS'] = str(num_cores)
            os.environ['NUMEXPR_NUM_THREADS'] = str(num_cores)
            
            # Configure NumPy error handling
            np.seterr(divide='warn', over='warn', invalid='warn')
            
            logger.info(f"NumPy optimized for {num_cores} cores")
            
        except ImportError:
            logger.warning("NumPy not available for optimization")


class LibraryInitializer:
    """Initialize high-performance libraries with optimal settings."""
    
    @staticmethod
    async def initialize_async_libraries():
        """Initialize async libraries and event loop optimizations."""
        if UVLOOP_AVAILABLE:
            # Use uvloop for better async performance
            uvloop.install()
            logger.info("uvloop installed for enhanced async performance")
        
        # Configure asyncio settings
        if hasattr(asyncio, 'set_event_loop_policy'):
            if sys.platform != 'win32' and UVLOOP_AVAILABLE:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    @staticmethod
    def initialize_jit_compilation():
        """Initialize JIT compilation libraries."""
        if NUMBA_AVAILABLE:
            # Configure Numba for optimal performance
            os.environ['NUMBA_CACHE_DIR'] = '/tmp/numba_cache'
            os.environ['NUMBA_NUM_THREADS'] = str(psutil.cpu_count())
            
            # Pre-compile common functions to reduce first-call overhead
            try:
                import numpy as np
                from .optimization import VectorizedProcessor
                
                # Trigger compilation of common functions
                test_array = np.array([1.0, 2.0, 3.0])
                VectorizedProcessor.fast_sum(test_array)
                VectorizedProcessor.fast_mean(test_array)
                
                logger.info("Numba JIT compilation initialized and warmed up")
            except Exception as e:
                logger.warning(f"Numba warm-up failed: {e}")
    
    @staticmethod
    def initialize_data_processing():
        """Initialize data processing libraries."""
        if POLARS_AVAILABLE:
            # Configure Polars for optimal performance
            pl.Config.set_tbl_rows(100)  # Display settings
            pl.Config.set_tbl_cols(20)
            logger.info("Polars initialized for ultra-fast data processing")
        
        try:
            import pandas as pd
            # Configure pandas for better performance
            pd.set_option('compute.use_bottleneck', True)
            pd.set_option('compute.use_numexpr', True)
            logger.info("Pandas optimizations enabled")
        except ImportError:
            pass
    
    @staticmethod
    def initialize_compression():
        """Initialize compression libraries."""
        compression_libs = []
        
        try:
            import lz4
            compression_libs.append("lz4")
        except ImportError:
            pass
        
        try:
            import zstandard
            compression_libs.append("zstandard")
        except ImportError:
            pass
        
        try:
            import brotli
            compression_libs.append("brotli")
        except ImportError:
            pass
        
        if compression_libs:
            logger.info(f"Compression libraries available: {', '.join(compression_libs)}")
        else:
            logger.warning("No high-performance compression libraries available")


class FeatureValidator:
    """Validate and report available optimized features."""
    
    @staticmethod
    def check_feature_availability() -> Dict[str, bool]:
        """Check availability of all optimization features."""
        features = {
            "uvloop": UVLOOP_AVAILABLE,
            "orjson": ORJSON_AVAILABLE,
            "numba": NUMBA_AVAILABLE,
            "polars": POLARS_AVAILABLE,
            "gpu_acceleration": GPU_AVAILABLE,
        }
        
        # Check additional libraries
        additional_libs = [
            "xxhash", "msgpack", "lz4", "zstandard", "pyarrow", 
            "aiohttp", "psutil", "pympler", "scipy"
        ]
        
        for lib in additional_libs:
            try:
                __import__(lib)
                features[lib] = True
            except ImportError:
                features[lib] = False
        
        return features
    
    @staticmethod
    def generate_feature_report(features: Dict[str, bool]) -> str:
        """Generate a report of available features."""
        report = ["# Onyx Features Optimization Report\n"]
        
        available = sum(features.values())
        total = len(features)
        percentage = (available / total) * 100
        
        report.append(f"**Optimization Status: {available}/{total} ({percentage:.1f}%) features available**\n\n")
        
        # Core optimizations
        core_features = {
            "uvloop": "High-performance event loop",
            "orjson": "Ultra-fast JSON serialization",
            "numba": "JIT compilation for numerical code",
            "polars": "Ultra-fast DataFrame processing",
            "gpu_acceleration": "GPU acceleration with CuPy"
        }
        
        report.append("## Core Performance Features\n")
        for feature, description in core_features.items():
            status = "✅" if features.get(feature, False) else "❌"
            report.append(f"- {status} **{feature}**: {description}\n")
        
        # Additional libraries
        report.append("\n## Additional Libraries\n")
        additional_libs = [k for k in features.keys() if k not in core_features]
        for lib in sorted(additional_libs):
            status = "✅" if features[lib] else "❌"
            report.append(f"- {status} {lib}\n")
        
        # Performance recommendations
        report.append("\n## Performance Recommendations\n")
        
        if not features.get("uvloop", False):
            report.append("- Install uvloop for 2-4x async performance improvement\n")
        
        if not features.get("orjson", False):
            report.append("- Install orjson for 2-3x JSON serialization speedup\n")
        
        if not features.get("numba", False):
            report.append("- Install numba for 10-100x numerical computation speedup\n")
        
        if not features.get("polars", False):
            report.append("- Install polars for 5-30x DataFrame processing speedup\n")
        
        if percentage >= 90:
            report.append("\n🚀 **Excellent!** Your system is highly optimized for production use.\n")
        elif percentage >= 75:
            report.append("\n✅ **Good!** Most optimizations are available.\n")
        elif percentage >= 50:
            report.append("\n⚠️ **Fair** - Consider installing missing optimization libraries.\n")
        else:
            report.append("\n❌ **Poor** - Many optimization libraries are missing.\n")
        
        return "".join(report)


class StartupOrchestrator:
    """Main startup orchestrator for all optimizations."""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.system_optimizer = SystemOptimizer()
        self.library_initializer = LibraryInitializer()
        self.feature_validator = FeatureValidator()
        self.performance_orchestrator = None
        
    async def initialize_all(self) -> Dict[str, Any]:
        """Initialize all optimizations and return status report."""
        start_time = time.perf_counter()
        
        logger.info("🚀 Starting Onyx Features optimization initialization")
        
        # System-level optimizations
        logger.info("Optimizing Python settings...")
        self.system_optimizer.optimize_python_settings()
        
        logger.info("Optimizing system resources...")
        self.system_optimizer.optimize_system_resources()
        
        logger.info("Configuring NumPy optimizations...")
        self.system_optimizer.configure_numpy_optimizations()
        
        # Library initialization
        logger.info("Initializing async libraries...")
        await self.library_initializer.initialize_async_libraries()
        
        logger.info("Initializing JIT compilation...")
        self.library_initializer.initialize_jit_compilation()
        
        logger.info("Initializing data processing libraries...")
        self.library_initializer.initialize_data_processing()
        
        logger.info("Initializing compression libraries...")
        self.library_initializer.initialize_compression()
        
        # Performance orchestrator
        logger.info("Initializing performance orchestrator...")
        self.performance_orchestrator = create_performance_orchestrator(self.config)
        await self.performance_orchestrator.initialize()
        
        # Feature validation
        features = self.feature_validator.check_feature_availability()
        feature_report = self.feature_validator.generate_feature_report(features)
        
        initialization_time = (time.perf_counter() - start_time) * 1000
        
        # System information
        system_info = {
            "cpu_count": psutil.cpu_count(),
            "memory_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        logger.info(f"✅ Optimization initialization completed in {initialization_time:.2f}ms")
        
        return {
            "initialization_time_ms": initialization_time,
            "features_available": features,
            "feature_report": feature_report,
            "system_info": system_info,
            "optimization_config": self.config.__dict__,
            "performance_grade": self._calculate_performance_grade(features)
        }
    
    def _calculate_performance_grade(self, features: Dict[str, bool]) -> str:
        """Calculate overall performance grade."""
        core_features = ["uvloop", "orjson", "numba", "polars"]
        core_available = sum(1 for f in core_features if features.get(f, False))
        
        total_available = sum(features.values())
        total_features = len(features)
        
        # Weight core features more heavily
        weighted_score = (core_available * 2 + (total_available - core_available)) / (len(core_features) * 2 + (total_features - len(core_features)))
        
        if weighted_score >= 0.9:
            return "A+ (Excellent)"
        elif weighted_score >= 0.8:
            return "A (Very Good)"
        elif weighted_score >= 0.7:
            return "B (Good)"
        elif weighted_score >= 0.6:
            return "C (Fair)"
        else:
            return "D (Needs Improvement)"
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.performance_orchestrator:
            await self.performance_orchestrator.cleanup()


# Global startup orchestrator
_startup_orchestrator: Optional[StartupOrchestrator] = None


async def initialize_onyx_optimizations(config: Optional[OptimizationConfig] = None) -> Dict[str, Any]:
    """Initialize all Onyx optimizations."""
    global _startup_orchestrator
    
    _startup_orchestrator = StartupOrchestrator(config)
    return await _startup_orchestrator.initialize_all()


async def shutdown_onyx_optimizations():
    """Shutdown and cleanup all optimizations."""
    global _startup_orchestrator
    
    if _startup_orchestrator:
        await _startup_orchestrator.cleanup()
        _startup_orchestrator = None


def get_startup_orchestrator() -> Optional[StartupOrchestrator]:
    """Get the global startup orchestrator."""
    return _startup_orchestrator


# CLI function for testing initialization
async def main():
    """Main function for testing startup from CLI."""
    try:
        report = await initialize_onyx_optimizations()
        
        print("\n" + "="*60)
        print("ONYX FEATURES OPTIMIZATION REPORT")
        print("="*60)
        print(f"Initialization time: {report['initialization_time_ms']:.2f}ms")
        print(f"Performance grade: {report['performance_grade']}")
        print(f"System: {report['system_info']['cpu_count']} CPUs, {report['system_info']['memory_gb']:.1f}GB RAM")
        print("\n" + report['feature_report'])
        
        # Benchmark recommendation
        print("\n💡 **Tip**: Run 'python -m agents.backend.onyx.server.features.benchmark' for performance benchmarks")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    finally:
        await shutdown_onyx_optimizations()


if __name__ == "__main__":
    asyncio.run(main())


# Export components
__all__ = [
    "SystemOptimizer",
    "LibraryInitializer", 
    "FeatureValidator",
    "StartupOrchestrator",
    "initialize_onyx_optimizations",
    "shutdown_onyx_optimizations",
    "get_startup_orchestrator"
] 