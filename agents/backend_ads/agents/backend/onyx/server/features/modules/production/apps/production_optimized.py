"""
Production Optimized System - Ultra-High Performance Onyx Features.

Complete production-ready system with cutting-edge optimization libraries
for maximum performance, scalability, and efficiency.
"""

import asyncio
import os
import time
import gc
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

# Ultra-fast core imports
import orjson  # 2-3x faster JSON than standard
import xxhash  # Ultra-fast hashing
import msgpack  # Fast binary serialization
import numpy as np
import psutil
import structlog

# Optional ultra-performance libraries
try:
    import blake3  # Fastest hash algorithm
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    import uvloop  # High-performance event loop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

try:
    import numba
    from numba import jit, njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

try:
    import blosc2  # Ultra-fast compression
    BLOSC2_AVAILABLE = True
except ImportError:
    BLOSC2_AVAILABLE = False

try:
    import polars as pl  # Rust-based ultra-fast DataFrames
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

try:
    import pyarrow as pa  # Columnar data format
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

# FastAPI and async imports
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

logger = structlog.get_logger(__name__)


@dataclass
class ProductionConfig:
    """Production optimization configuration."""
    # Performance levels
    enable_ultra_optimizations: bool = True
    enable_jit_compilation: bool = NUMBA_AVAILABLE
    enable_gpu_acceleration: bool = False
    
    # Concurrency settings
    max_workers: int = min(64, os.cpu_count() * 4)
    max_concurrent_requests: int = 1000
    request_timeout_seconds: float = 30.0
    
    # Memory settings
    memory_limit_percent: float = 85.0
    enable_memory_mapping: bool = True
    gc_threshold: int = 700
    
    # Serialization settings
    use_orjson: bool = True
    use_msgpack_fallback: bool = True
    compression_enabled: bool = BLOSC2_AVAILABLE
    
    # Hash settings
    hash_algorithm: str = "blake3" if BLAKE3_AVAILABLE else "xxhash"
    
    # Event loop settings
    use_uvloop: bool = UVLOOP_AVAILABLE
    
    def get_feature_report(self) -> Dict[str, Any]:
        """Get available features report."""
        return {
            "ultra_optimizations": self.enable_ultra_optimizations,
            "libraries_available": {
                "blake3": BLAKE3_AVAILABLE,
                "uvloop": UVLOOP_AVAILABLE,
                "numba": NUMBA_AVAILABLE,
                "blosc2": BLOSC2_AVAILABLE,
                "polars": POLARS_AVAILABLE,
                "pyarrow": ARROW_AVAILABLE
            },
            "effective_config": {
                "hash_algorithm": self.hash_algorithm,
                "max_workers": self.max_workers,
                "jit_enabled": self.enable_jit_compilation and NUMBA_AVAILABLE,
                "compression_enabled": self.compression_enabled,
                "uvloop_enabled": self.use_uvloop and UVLOOP_AVAILABLE
            }
        }


class UltraFastSerializer:
    """Ultra-fast serialization using the best available libraries."""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.use_orjson = config.use_orjson
        self.use_msgpack = config.use_msgpack_fallback
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize with maximum speed."""
        try:
            if self.use_orjson:
                return orjson.dumps(obj, option=orjson.OPT_FAST_SERIALIZE)
            elif self.use_msgpack:
                return msgpack.packb(obj, use_bin_type=True)
            else:
                import pickle
                return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.warning("Serialization fallback", error=str(e))
            import pickle
            return pickle.dumps(obj)
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize with maximum speed."""
        try:
            if self.use_orjson:
                return orjson.loads(data)
            elif self.use_msgpack:
                return msgpack.unpackb(data, raw=False)
            else:
                import pickle
                return pickle.loads(data)
        except Exception as e:
            logger.warning("Deserialization fallback", error=str(e))
            import pickle
            return pickle.loads(data)


class UltraFastHasher:
    """Ultra-fast hashing using the fastest algorithms."""
    
    def __init__(self, config: ProductionConfig):
        self.algorithm = config.hash_algorithm
    
    def hash_fast(self, data: Union[str, bytes], seed: int = 0) -> str:
        """Hash with maximum speed."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            if self.algorithm == "blake3" and BLAKE3_AVAILABLE:
                return blake3.blake3(data).hexdigest()
            else:
                return xxhash.xxh64(data, seed=seed).hexdigest()
        except Exception:
            import hashlib
            return hashlib.sha256(data).hexdigest()
    
    def hash_int(self, data: Union[str, bytes], seed: int = 0) -> int:
        """Fast integer hash."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return xxhash.xxh64(data, seed=seed).intdigest()


class UltraFastCompressor:
    """Ultra-fast compression using the best available algorithms."""
    
    def __init__(self, config: ProductionConfig):
        self.enabled = config.compression_enabled
    
    def compress(self, data: bytes) -> Tuple[bytes, bool]:
        """Compress with maximum speed."""
        if not self.enabled:
            return data, False
        
        try:
            if BLOSC2_AVAILABLE:
                compressed = blosc2.compress(data, clevel=1, cname="lz4", shuffle=blosc2.SHUFFLE)
                return compressed, True
            else:
                import lz4.frame
                compressed = lz4.frame.compress(data, compression_level=1)
                return compressed, True
        except Exception:
            return data, False
    
    def decompress(self, data: bytes, was_compressed: bool) -> bytes:
        """Decompress with maximum speed."""
        if not was_compressed:
            return data
        
        try:
            if BLOSC2_AVAILABLE:
                return blosc2.decompress(data)
            else:
                import lz4.frame
                return lz4.frame.decompress(data)
        except Exception as e:
            logger.error("Decompression failed", error=str(e))
            return data


class MemoryManager:
    """Ultra-efficient memory management."""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.memory_limit = config.memory_limit_percent
        self.gc_threshold = config.gc_threshold
        self._setup_gc()
    
    def _setup_gc(self):
        """Setup aggressive garbage collection."""
        gc.set_threshold(self.gc_threshold, 10, 10)
    
    def check_memory_pressure(self) -> bool:
        """Check if memory pressure is high."""
        memory_percent = psutil.virtual_memory().percent
        return memory_percent > self.memory_limit
    
    def force_cleanup(self) -> Dict[str, Any]:
        """Force aggressive memory cleanup."""
        initial_memory = psutil.virtual_memory().percent
        
        # Aggressive garbage collection
        collected_objects = 0
        for generation in range(3):
            collected_objects += gc.collect(generation)
        
        # Force memory compaction
        gc.collect()
        gc.collect()  # Call twice for better effect
        
        final_memory = psutil.virtual_memory().percent
        
        return {
            "initial_memory_percent": initial_memory,
            "final_memory_percent": final_memory,
            "memory_freed_percent": initial_memory - final_memory,
            "objects_collected": collected_objects
        }
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get current memory statistics."""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent": memory.percent,
            "pressure": self.check_memory_pressure()
        }


class PerformanceProfiler:
    """Ultra-fast performance profiling."""
    
    def __init__(self):
        self.start_time = None
        self.metrics = []
    
    def start(self):
        """Start profiling."""
        self.start_time = time.perf_counter()
    
    def stop(self) -> float:
        """Stop profiling and return duration in milliseconds."""
        if self.start_time is None:
            return 0.0
        
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        self.metrics.append(duration_ms)
        return duration_ms
    
    def get_stats(self) -> Dict[str, float]:
        """Get performance statistics."""
        if not self.metrics:
            return {"count": 0, "avg_ms": 0, "min_ms": 0, "max_ms": 0}
        
        return {
            "count": len(self.metrics),
            "avg_ms": np.mean(self.metrics),
            "min_ms": np.min(self.metrics),
            "max_ms": np.max(self.metrics),
            "p95_ms": np.percentile(self.metrics, 95)
        }


class DataProcessor:
    """Ultra-fast data processing using optimized libraries."""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.use_polars = POLARS_AVAILABLE
        self.use_arrow = ARROW_AVAILABLE
    
    def process_json_ultra_fast(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process JSON data with maximum speed."""
        if not data:
            return {"processed": 0, "errors": 0}
        
        try:
            if self.use_polars:
                # Use Polars for ultra-fast processing
                df = pl.DataFrame(data)
                
                # Example processing: filter, aggregate, sort
                processed_df = (
                    df
                    .filter(pl.col("id").is_not_null() if "id" in df.columns else pl.lit(True))
                    .select([pl.col("*")])
                )
                
                return {
                    "processed": len(processed_df),
                    "columns": processed_df.columns,
                    "shape": processed_df.shape,
                    "sample": processed_df.head(3).to_dicts() if len(processed_df) > 0 else []
                }
            
            elif self.use_arrow:
                # Use Arrow for fast columnar processing
                table = pa.table(data)
                return {
                    "processed": len(table),
                    "columns": table.column_names,
                    "memory_usage": table.nbytes
                }
            
            else:
                # Fallback to standard processing
                processed = 0
                for item in data:
                    if isinstance(item, dict) and item:
                        processed += 1
                
                return {"processed": processed, "total": len(data)}
                
        except Exception as e:
            logger.error("Data processing failed", error=str(e))
            return {"processed": 0, "errors": 1, "error": str(e)}


# JIT-compiled functions for maximum speed
if NUMBA_AVAILABLE:
    @njit(parallel=True, cache=True, fastmath=True)
    def ultra_fast_array_sum(arr: np.ndarray) -> float:
        """Ultra-fast parallel array sum."""
        total = 0.0
        for i in prange(len(arr)):
            total += arr[i]
        return total
    
    @njit(parallel=True, cache=True)
    def ultra_fast_array_hash(arr: np.ndarray) -> np.ndarray:
        """Ultra-fast parallel array hashing."""
        result = np.empty(len(arr), dtype=np.uint64)
        for i in prange(len(arr)):
            x = np.uint64(arr[i])
            x = ((x >> 16) ^ x) * np.uint64(0x45d9f3b)
            x = ((x >> 16) ^ x) * np.uint64(0x45d9f3b)
            x = (x >> 16) ^ x
            result[i] = x
        return result
else:
    def ultra_fast_array_sum(arr: np.ndarray) -> float:
        """Fallback array sum."""
        return np.sum(arr)
    
    def ultra_fast_array_hash(arr: np.ndarray) -> np.ndarray:
        """Fallback array hashing."""
        return np.array([hash(x) for x in arr], dtype=np.uint64)


class ProductionOptimizer:
    """Main production optimizer orchestrator."""
    
    def __init__(self, config: Optional[ProductionConfig] = None):
        self.config = config or ProductionConfig()
        
        # Initialize components
        self.serializer = UltraFastSerializer(self.config)
        self.hasher = UltraFastHasher(self.config)
        self.compressor = UltraFastCompressor(self.config)
        self.memory_manager = MemoryManager(self.config)
        self.profiler = PerformanceProfiler()
        self.data_processor = DataProcessor(self.config)
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.initialized = False
        
        logger.info("Production optimizer created", 
                   config=self.config.get_feature_report())
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the production optimizer."""
        start_time = time.perf_counter()
        
        # Setup event loop optimization
        if self.config.use_uvloop and UVLOOP_AVAILABLE:
            try:
                uvloop.install()
                logger.info("UVLoop event loop installed")
            except Exception as e:
                logger.warning("UVLoop installation failed", error=str(e))
        
        # Warmup JIT compilation
        if NUMBA_AVAILABLE and self.config.enable_jit_compilation:
            warmup_array = np.random.random(1000).astype(np.float64)
            ultra_fast_array_sum(warmup_array)
            ultra_fast_array_hash(warmup_array.astype(np.float64))
            logger.info("JIT compilation warmed up")
        
        # Initial memory optimization
        memory_stats = self.memory_manager.force_cleanup()
        
        init_time = (time.perf_counter() - start_time) * 1000
        self.initialized = True
        
        return {
            "initialization_time_ms": init_time,
            "memory_cleanup": memory_stats,
            "features": self.config.get_feature_report(),
            "ready": True
        }
    
    @asynccontextmanager
    async def request_context(self, operation_name: str):
        """Context manager for optimized request processing."""
        self.profiler.start()
        
        # Check memory pressure
        if self.memory_manager.check_memory_pressure():
            logger.warning("High memory pressure detected")
            self.memory_manager.force_cleanup()
        
        try:
            yield
        finally:
            duration_ms = self.profiler.stop()
            self.request_count += 1
            self.total_response_time += duration_ms
            
            # Log slow requests
            if duration_ms > 1000:  # > 1 second
                logger.warning("Slow request detected", 
                             operation=operation_name,
                             duration_ms=duration_ms)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "request_count": self.request_count,
            "avg_response_time_ms": avg_response_time,
            "profiler_stats": self.profiler.get_stats(),
            "memory_stats": self.memory_manager.get_memory_stats(),
            "system_stats": {
                "cpu_count": os.cpu_count(),
                "cpu_percent": psutil.cpu_percent(),
                "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        }
    
    async def cleanup(self):
        """Cleanup optimizer resources."""
        memory_stats = self.memory_manager.force_cleanup()
        logger.info("Production optimizer cleaned up", memory_stats=memory_stats)


def create_production_app(config: Optional[ProductionConfig] = None) -> Tuple[FastAPI, ProductionOptimizer]:
    """Create optimized production FastAPI application."""
    
    optimizer = ProductionOptimizer(config)
    
    # Create FastAPI app with optimizations
    app = FastAPI(
        title="Ultra-Optimized Onyx Features API",
        description="Production-ready API with cutting-edge performance optimizations",
        version="2.0.0",
        default_response_class=ORJSONResponse,  # Ultra-fast JSON responses
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add optimized middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    @app.middleware("http")
    async def ultra_fast_middleware(request: Request, call_next):
        """Ultra-fast request middleware."""
        # Generate correlation ID with fastest hasher
        correlation_id = optimizer.hasher.hash_fast(
            f"{request.url.path}_{time.time()}"
        )[:16]
        
        request.state.correlation_id = correlation_id
        
        async with optimizer.request_context(str(request.url.path)):
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
    
    @app.on_event("startup")
    async def startup_event():
        """Startup event with optimization initialization."""
        logger.info("Starting ultra-optimized application")
        init_result = await optimizer.initialize()
        logger.info("Application startup completed", init_result=init_result)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event with cleanup."""
        logger.info("Shutting down application")
        await optimizer.cleanup()
    
    # Health and metrics endpoints
    @app.get("/health")
    async def health_check():
        """Ultra-fast health check."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "optimizer_ready": optimizer.initialized,
            "features": optimizer.config.get_feature_report()
        }
    
    @app.get("/metrics")
    async def get_metrics():
        """Performance metrics endpoint."""
        return optimizer.get_performance_metrics()
    
    # Ultra-fast data processing endpoint
    @app.post("/process/data")
    async def process_data(data: List[Dict[str, Any]]):
        """Ultra-fast data processing endpoint."""
        async with optimizer.request_context("process_data"):
            result = optimizer.data_processor.process_json_ultra_fast(data)
            return {
                "status": "success",
                "result": result,
                "processed_at": time.time()
            }
    
    # Ultra-fast serialization test endpoint
    @app.post("/test/serialization")
    async def test_serialization(data: Dict[str, Any]):
        """Test ultra-fast serialization."""
        async with optimizer.request_context("test_serialization"):
            # Serialize and deserialize to test speed
            serialized = optimizer.serializer.serialize(data)
            deserialized = optimizer.serializer.deserialize(serialized)
            
            return {
                "status": "success",
                "original_size": len(str(data)),
                "serialized_size": len(serialized),
                "compression_ratio": len(serialized) / len(str(data)),
                "round_trip_success": data == deserialized
            }
    
    return app, optimizer


# Production startup function
async def run_production_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    config: Optional[ProductionConfig] = None
):
    """Run the production server with all optimizations."""
    import uvicorn
    
    app, optimizer = create_production_app(config)
    
    # Production uvicorn configuration
    uvicorn_config = {
        "host": host,
        "port": port,
        "loop": "uvloop" if UVLOOP_AVAILABLE else "asyncio",
        "http": "httptools",
        "log_level": "info",
        "access_log": True,
        "workers": 1  # Single worker for async app
    }
    
    logger.info(f"Starting production server on {host}:{port}")
    logger.info("Optimization features", features=optimizer.config.get_feature_report())
    
    # Run server
    server = uvicorn.Server(uvicorn.Config(app, **uvicorn_config))
    await server.serve()


if __name__ == "__main__":
    # Production configuration
    production_config = ProductionConfig(
        enable_ultra_optimizations=True,
        max_workers=min(64, os.cpu_count() * 4),
        max_concurrent_requests=1000,
        memory_limit_percent=85.0
    )
    
    asyncio.run(run_production_server(config=production_config))


# Export components
__all__ = [
    "ProductionConfig",
    "ProductionOptimizer", 
    "create_production_app",
    "run_production_server",
    "UltraFastSerializer",
    "UltraFastHasher",
    "UltraFastCompressor",
    "MemoryManager",
    "PerformanceProfiler",
    "DataProcessor"
] 