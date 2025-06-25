"""
Onyx Ultra Production - Maximum Performance with Cutting-Edge Libraries 2024.

Enterprise-grade application with bleeding-edge optimization libraries.
"""

import asyncio
import os
import time
import signal
import gc
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
import uvicorn

# Ultra-performance imports with fallbacks
AVAILABLE_LIBS = {}

# Event loop optimization
try:
    import uvloop
    AVAILABLE_LIBS['uvloop'] = True
except ImportError:
    AVAILABLE_LIBS['uvloop'] = False

# Ultra-fast JSON serialization
try:
    import orjson
    AVAILABLE_LIBS['orjson'] = True
except ImportError:
    try:
        import ujson as orjson
        AVAILABLE_LIBS['ujson'] = True
    except ImportError:
        import json as orjson
        AVAILABLE_LIBS['json'] = True

# Alternative JSON parsers
try:
    import simdjson
    AVAILABLE_LIBS['simdjson'] = True
except ImportError:
    AVAILABLE_LIBS['simdjson'] = False

try:
    import rapidjson
    AVAILABLE_LIBS['rapidjson'] = True
except ImportError:
    AVAILABLE_LIBS['rapidjson'] = False

# Ultra-fast hashing
try:
    import blake3
    AVAILABLE_LIBS['blake3'] = True
except ImportError:
    AVAILABLE_LIBS['blake3'] = False

try:
    import xxhash
    AVAILABLE_LIBS['xxhash'] = True
except ImportError:
    AVAILABLE_LIBS['xxhash'] = False

try:
    import mmh3
    AVAILABLE_LIBS['mmh3'] = True
except ImportError:
    AVAILABLE_LIBS['mmh3'] = False

# Ultra-fast compression
try:
    import blosc2
    AVAILABLE_LIBS['blosc2'] = True
except ImportError:
    AVAILABLE_LIBS['blosc2'] = False

try:
    import lz4.frame
    AVAILABLE_LIBS['lz4'] = True
except ImportError:
    AVAILABLE_LIBS['lz4'] = False

try:
    import zstandard as zstd
    AVAILABLE_LIBS['zstd'] = True
except ImportError:
    AVAILABLE_LIBS['zstd'] = False

try:
    import cramjam
    AVAILABLE_LIBS['cramjam'] = True
except ImportError:
    AVAILABLE_LIBS['cramjam'] = False

# Data processing powerhouses
try:
    import polars as pl
    AVAILABLE_LIBS['polars'] = True
except ImportError:
    AVAILABLE_LIBS['polars'] = False

try:
    import pyarrow as pa
    AVAILABLE_LIBS['pyarrow'] = True
except ImportError:
    AVAILABLE_LIBS['pyarrow'] = False

try:
    import duckdb
    AVAILABLE_LIBS['duckdb'] = True
except ImportError:
    AVAILABLE_LIBS['duckdb'] = False

# JIT compilation
try:
    import numba
    from numba import jit, njit
    AVAILABLE_LIBS['numba'] = True
except ImportError:
    # Fallback decorators
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    AVAILABLE_LIBS['numba'] = False

# Memory profiling
try:
    import psutil
    AVAILABLE_LIBS['psutil'] = True
except ImportError:
    AVAILABLE_LIBS['psutil'] = False

try:
    import pympler
    AVAILABLE_LIBS['pympler'] = True
except ImportError:
    AVAILABLE_LIBS['pympler'] = False

# Structured logging and monitoring
import structlog
from prometheus_client import generate_latest, Counter, Histogram, Gauge

# Configure ultra-fast structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(serializer=orjson.dumps if AVAILABLE_LIBS.get('orjson') else None)
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Ultra-fast metrics
request_count = Counter('onyx_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('onyx_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
memory_usage = Gauge('onyx_memory_usage_bytes', 'Memory usage in bytes')
cpu_usage = Gauge('onyx_cpu_usage_percent', 'CPU usage percentage')
active_connections = Gauge('onyx_active_connections', 'Active connections')

@dataclass
class UltraConfig:
    """Ultra-optimized configuration with auto-tuning."""
    APP_NAME: str = "Onyx-Ultra"
    VERSION: str = "6.0.0"
    DEBUG: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    HOST: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    PORT: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    
    # Auto-tune workers based on CPU count and available memory
    WORKERS: int = field(default_factory=lambda: min(
        64, 
        max(1, mp.cpu_count() * 4),
        int(psutil.virtual_memory().total / (512 * 1024 * 1024)) if AVAILABLE_LIBS.get('psutil') else 8
    ))
    
    # Performance settings
    ENABLE_UVLOOP: bool = field(default_factory=lambda: AVAILABLE_LIBS.get('uvloop', False))
    ENABLE_JIT: bool = field(default_factory=lambda: AVAILABLE_LIBS.get('numba', False))
    COMPRESSION_LEVEL: int = 1  # Fast compression
    HASH_LENGTH: int = 16
    
    # Memory management
    GC_THRESHOLD: int = 1000  # Requests before forced GC
    MAX_MEMORY_MB: int = field(default_factory=lambda: 
        int(psutil.virtual_memory().total / (1024 * 1024) * 0.8) if AVAILABLE_LIBS.get('psutil') else 2048
    )

config = UltraConfig()
startup_time = 0.0
request_counter = 0

class UltraOptimizer:
    """Ultra-performance optimizer using best available libraries."""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=min(32, mp.cpu_count() * 2))
        logger.info("🚀 UltraOptimizer initialized", available_libs=AVAILABLE_LIBS)
    
    @njit(cache=True) if AVAILABLE_LIBS.get('numba') else lambda x: x
    def _hash_numeric(self, data: int) -> int:
        """JIT-compiled numeric hashing."""
        return ((data * 31) + 17) % 2147483647
    
    def serialize(self, data: Any) -> bytes:
        """Ultra-fast serialization with best available library."""
        if AVAILABLE_LIBS.get('orjson'):
            return orjson.dumps(data)
        elif AVAILABLE_LIBS.get('ujson'):
            return orjson.dumps(data).encode()
        else:
            return orjson.dumps(data).encode()
    
    def deserialize(self, data: bytes) -> Any:
        """Ultra-fast deserialization."""
        if AVAILABLE_LIBS.get('simdjson'):
            return simdjson.loads(data)
        elif AVAILABLE_LIBS.get('orjson'):
            return orjson.loads(data)
        else:
            return orjson.loads(data)
    
    def hash_fast(self, data: str) -> str:
        """Ultra-fast hashing with best available algorithm."""
        if AVAILABLE_LIBS.get('blake3'):
            return blake3.blake3(data.encode()).hexdigest()[:config.HASH_LENGTH]
        elif AVAILABLE_LIBS.get('xxhash'):
            return xxhash.xxh64(data).hexdigest()[:config.HASH_LENGTH]
        elif AVAILABLE_LIBS.get('mmh3'):
            return f"{mmh3.hash(data):08x}"[:config.HASH_LENGTH]
        else:
            import hashlib
            return hashlib.sha256(data.encode()).hexdigest()[:config.HASH_LENGTH]
    
    def compress(self, data: bytes) -> bytes:
        """Ultra-fast compression with best available algorithm."""
        if len(data) < 1024:  # Don't compress small data
            return data
            
        if AVAILABLE_LIBS.get('blosc2'):
            return blosc2.compress(data, clevel=config.COMPRESSION_LEVEL, cname="lz4")
        elif AVAILABLE_LIBS.get('lz4'):
            return lz4.frame.compress(data, compression_level=config.COMPRESSION_LEVEL)
        elif AVAILABLE_LIBS.get('cramjam'):
            return cramjam.lz4.compress_raw(data)
        elif AVAILABLE_LIBS.get('zstd'):
            return zstd.compress(data, level=config.COMPRESSION_LEVEL)
        else:
            import gzip
            return gzip.compress(data, compresslevel=config.COMPRESSION_LEVEL)
    
    def decompress(self, data: bytes, algorithm: str = "auto") -> bytes:
        """Ultra-fast decompression."""
        try:
            if algorithm == "blosc2" and AVAILABLE_LIBS.get('blosc2'):
                return blosc2.decompress(data)
            elif algorithm == "lz4" and AVAILABLE_LIBS.get('lz4'):
                return lz4.frame.decompress(data)
            elif algorithm == "cramjam" and AVAILABLE_LIBS.get('cramjam'):
                return cramjam.lz4.decompress_raw(data)
            elif algorithm == "zstd" and AVAILABLE_LIBS.get('zstd'):
                return zstd.decompress(data)
            else:
                import gzip
                return gzip.decompress(data)
        except Exception:
            return data  # Return original if decompression fails
    
    async def process_data_async(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ultra-fast async data processing with Polars/Arrow."""
        if not data:
            return {"processed": 0, "time_ms": 0}
            
        start = time.perf_counter()
        
        if AVAILABLE_LIBS.get('polars'):
            # Use Polars for ultra-fast data processing
            df = pl.DataFrame(data)
            result = {
                "rows": df.height,
                "columns": df.width,
                "memory_usage": df.estimated_size("mb") if hasattr(df, 'estimated_size') else 0,
                "dtypes": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
            }
        elif AVAILABLE_LIBS.get('pyarrow'):
            # Fallback to PyArrow
            table = pa.Table.from_pylist(data)
            result = {
                "rows": table.num_rows,
                "columns": table.num_columns,
                "memory_usage": table.nbytes / (1024 * 1024),
                "schema": str(table.schema)
            }
        else:
            # Basic processing
            result = {
                "rows": len(data),
                "columns": len(data[0].keys()) if data else 0,
                "memory_usage": len(str(data)) / (1024 * 1024),
                "keys": list(data[0].keys()) if data else []
            }
        
        duration = (time.perf_counter() - start) * 1000
        result["processing_time_ms"] = duration
        
        return result

optimizer = UltraOptimizer()

async def memory_monitor():
    """Background memory monitoring."""
    if not AVAILABLE_LIBS.get('psutil'):
        return
        
    while True:
        try:
            process = psutil.Process()
            memory_usage.set(process.memory_info().rss)
            cpu_usage.set(process.cpu_percent())
            
            # Force garbage collection if memory usage is high
            if process.memory_info().rss > config.MAX_MEMORY_MB * 1024 * 1024:
                gc.collect()
                logger.warning("🧹 Forced garbage collection", 
                             memory_mb=process.memory_info().rss / (1024 * 1024))
        except Exception as e:
            logger.error("Memory monitoring failed", error=str(e))
        
        await asyncio.sleep(30)  # Monitor every 30 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ultra-optimized application lifespan."""
    global startup_time
    
    start = time.time()
    logger.info("🚀 Starting Onyx Ultra", version=config.VERSION, libs=AVAILABLE_LIBS)
    
    # Setup UVLoop for maximum performance
    if config.ENABLE_UVLOOP:
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("✅ UVLoop enabled - 2-4x faster event loop")
        except Exception as e:
            logger.warning("UVLoop setup failed", error=str(e))
    
    # Optimize garbage collection
    gc.set_threshold(700, 10, 10)  # More aggressive GC
    
    # Start background monitoring
    if AVAILABLE_LIBS.get('psutil'):
        asyncio.create_task(memory_monitor())
    
    startup_time = time.time() - start
    logger.info("🎉 Onyx Ultra ready!", 
                startup_time=f"{startup_time:.3f}s",
                workers=config.WORKERS,
                memory_limit_mb=config.MAX_MEMORY_MB)
    
    yield
    
    logger.info("🛑 Shutting down Onyx Ultra")
    optimizer.thread_pool.shutdown(wait=True)

# Create ultra-optimized FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    description="Ultra-optimized production API with cutting-edge libraries",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    lifespan=lifespan,
    default_response_class=ORJSONResponse if AVAILABLE_LIBS.get('orjson') else None
)

# Ultra-performance middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def ultra_performance_middleware(request: Request, call_next):
    """Ultra-performance middleware with advanced monitoring."""
    global request_counter
    request_counter += 1
    
    start_time = time.perf_counter()
    
    # Ultra-fast correlation ID
    correlation_id = optimizer.hash_fast(f"{request.url.path}_{start_time}_{request_counter}")
    request.state.correlation_id = correlation_id
    request.state.start_time = start_time
    
    # Process request
    response = await call_next(request)
    
    # Calculate metrics
    duration = time.perf_counter() - start_time
    
    # Update Prometheus metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    active_connections.set(request_counter % 1000)  # Approximate active connections
    
    # Ultra-fast response headers
    response.headers.update({
        "X-Correlation-ID": correlation_id,
        "X-Response-Time": f"{duration:.4f}s",
        "X-Server": config.APP_NAME,
        "X-Version": config.VERSION,
        "X-Optimizations": ",".join([k for k, v in AVAILABLE_LIBS.items() if v])
    })
    
    # Periodic garbage collection
    if request_counter % config.GC_THRESHOLD == 0:
        gc.collect()
    
    return response

# ============================================================================
# ULTRA-OPTIMIZED ENDPOINTS
# ============================================================================

@app.get("/health")
async def ultra_health():
    """Ultra-fast health check with system info."""
    uptime = time.time() - startup_time
    
    health_data = {
        "status": "healthy",
        "version": config.VERSION,
        "uptime_seconds": uptime,
        "uptime_human": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
        "optimizations": AVAILABLE_LIBS,
        "performance": {
            "requests_processed": request_counter,
            "avg_requests_per_second": request_counter / max(uptime, 1),
            "gc_enabled": gc.isenabled(),
            "gc_threshold": gc.get_threshold()
        }
    }
    
    if AVAILABLE_LIBS.get('psutil'):
        process = psutil.Process()
        health_data["system"] = {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / (1024 * 1024),
            "memory_percent": process.memory_percent(),
            "threads": process.num_threads(),
            "connections": len(process.connections()) if hasattr(process, 'connections') else 0
        }
    
    return health_data

@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

@app.post("/api/ultra-serialize")
async def ultra_serialize_endpoint(data: Dict[str, Any]):
    """Ultra-fast serialization with multiple formats."""
    start = time.perf_counter()
    
    results = {}
    
    # Test different serialization methods
    serialized = optimizer.serialize(data)
    compressed = optimizer.compress(serialized)
    
    results["orjson"] = {
        "size": len(serialized),
        "compressed_size": len(compressed),
        "compression_ratio": len(compressed) / len(serialized) if serialized else 1
    }
    
    # Test with other formats if available
    if AVAILABLE_LIBS.get('rapidjson'):
        rapid_data = rapidjson.dumps(data).encode()
        results["rapidjson"] = {"size": len(rapid_data)}
    
    duration = (time.perf_counter() - start) * 1000
    
    return {
        "original_size": len(str(data)),
        "results": results,
        "processing_time_ms": duration,
        "best_compression": min(results.values(), key=lambda x: x.get("compressed_size", float('inf')))
    }

@app.post("/api/ultra-hash")
async def ultra_hash_endpoint(data: str, algorithms: Optional[List[str]] = None):
    """Ultra-fast hashing with multiple algorithms."""
    start = time.perf_counter()
    
    results = {}
    test_algorithms = algorithms or ["blake3", "xxhash", "mmh3", "sha256"]
    
    for algo in test_algorithms:
        algo_start = time.perf_counter()
        
        if algo == "blake3" and AVAILABLE_LIBS.get('blake3'):
            hash_result = blake3.blake3(data.encode()).hexdigest()[:config.HASH_LENGTH]
        elif algo == "xxhash" and AVAILABLE_LIBS.get('xxhash'):
            hash_result = xxhash.xxh64(data).hexdigest()[:config.HASH_LENGTH]
        elif algo == "mmh3" and AVAILABLE_LIBS.get('mmh3'):
            hash_result = f"{mmh3.hash(data):08x}"[:config.HASH_LENGTH]
        else:
            import hashlib
            hash_result = hashlib.sha256(data.encode()).hexdigest()[:config.HASH_LENGTH]
        
        algo_duration = (time.perf_counter() - algo_start) * 1000
        results[algo] = {
            "hash": hash_result,
            "time_ms": algo_duration,
            "available": AVAILABLE_LIBS.get(algo, algo == "sha256")
        }
    
    total_duration = (time.perf_counter() - start) * 1000
    
    return {
        "input_size": len(data),
        "algorithms": results,
        "total_time_ms": total_duration,
        "fastest": min(results.items(), key=lambda x: x[1]["time_ms"])
    }

@app.post("/api/ultra-data-processing")
async def ultra_data_processing(data: List[Dict[str, Any]], background_tasks: BackgroundTasks):
    """Ultra-fast data processing with Polars/Arrow."""
    if not data:
        raise HTTPException(status_code=400, detail="No data provided")
    
    start = time.perf_counter()
    
    # Process data asynchronously
    result = await optimizer.process_data_async(data)
    
    duration = (time.perf_counter() - start) * 1000
    
    # Add background task for cleanup
    background_tasks.add_task(gc.collect)
    
    return {
        "input_records": len(data),
        "processing_result": result,
        "total_time_ms": duration,
        "library_used": "polars" if AVAILABLE_LIBS.get('polars') else "pyarrow" if AVAILABLE_LIBS.get('pyarrow') else "standard"
    }

@app.get("/api/ultra-benchmark")
async def ultra_benchmark(iterations: int = 50000, data_size: int = 1000):
    """Comprehensive performance benchmark."""
    test_data = {
        "string": "x" * data_size,
        "numbers": list(range(min(data_size, 1000))),
        "nested": {"level1": {"level2": {"data": "benchmark"}}},
        "timestamp": time.time()
    }
    
    benchmarks = {}
    
    # Serialization benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        optimizer.serialize(test_data)
    serialization_time = time.perf_counter() - start
    
    benchmarks["serialization"] = {
        "total_time_s": serialization_time,
        "ops_per_second": iterations / serialization_time,
        "library": "orjson" if AVAILABLE_LIBS.get('orjson') else "json"
    }
    
    # Hashing benchmark
    test_str = str(test_data)
    start = time.perf_counter()
    for _ in range(iterations):
        optimizer.hash_fast(test_str)
    hashing_time = time.perf_counter() - start
    
    benchmarks["hashing"] = {
        "total_time_s": hashing_time,
        "ops_per_second": iterations / hashing_time,
        "library": "blake3" if AVAILABLE_LIBS.get('blake3') else "sha256"
    }
    
    # Compression benchmark
    test_bytes = optimizer.serialize(test_data)
    start = time.perf_counter()
    for _ in range(min(iterations, 10000)):  # Fewer iterations for compression
        optimizer.compress(test_bytes)
    compression_time = time.perf_counter() - start
    
    benchmarks["compression"] = {
        "total_time_s": compression_time,
        "ops_per_second": min(iterations, 10000) / compression_time,
        "library": "blosc2" if AVAILABLE_LIBS.get('blosc2') else "gzip"
    }
    
    return {
        "iterations": iterations,
        "data_size": data_size,
        "benchmarks": benchmarks,
        "system_info": {
            "cpu_count": mp.cpu_count(),
            "available_libraries": {k: v for k, v in AVAILABLE_LIBS.items() if v},
            "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}"
        }
    }

@app.get("/status")
async def system_status():
    """Comprehensive system status."""
    uptime = time.time() - startup_time
    
    status = {
        "app": config.APP_NAME,
        "version": config.VERSION,
        "uptime_seconds": uptime,
        "configuration": {
            "workers": config.WORKERS,
            "uvloop_enabled": config.ENABLE_UVLOOP,
            "jit_enabled": config.ENABLE_JIT,
            "debug": config.DEBUG,
            "compression_level": config.COMPRESSION_LEVEL
        },
        "performance": {
            "requests_processed": request_counter,
            "avg_rps": request_counter / max(uptime, 1),
            "gc_collections": gc.get_count(),
            "gc_enabled": gc.isenabled()
        },
        "available_optimizations": AVAILABLE_LIBS
    }
    
    if AVAILABLE_LIBS.get('psutil'):
        process = psutil.Process()
        status["system"] = {
            "cpu_percent": process.cpu_percent(),
            "memory_info": {
                "rss_mb": process.memory_info().rss / (1024 * 1024),
                "vms_mb": process.memory_info().vms / (1024 * 1024),
                "percent": process.memory_percent()
            },
            "threads": process.num_threads(),
            "file_descriptors": process.num_fds() if hasattr(process, 'num_fds') else None,
            "cpu_times": process.cpu_times()._asdict()
        }
    
    return status

# ============================================================================
# ULTRA-OPTIMIZED SERVER
# ============================================================================

async def run_ultra_server():
    """Run ultra-optimized server with all optimizations."""
    server_config = uvicorn.Config(
        app=app,
        host=config.HOST,
        port=config.PORT,
        workers=1,  # Single worker for async
        loop="uvloop" if config.ENABLE_UVLOOP else "asyncio",
        http="httptools",
        log_level="info",
        access_log=config.DEBUG,
        server_header=False,
        date_header=False,
        # Ultra-performance settings
        backlog=2048,
        limit_concurrency=10000,
        limit_max_requests=1000000,
        timeout_keep_alive=65,
        timeout_graceful_shutdown=30
    )
    
    server = uvicorn.Server(server_config)
    
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} received, graceful shutdown...")
        server.should_exit = True
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("🚀 Starting Ultra Server", 
                host=config.HOST, 
                port=config.PORT,
                optimizations=len([k for k, v in AVAILABLE_LIBS.items() if v]))
    
    await server.serve()

def main():
    """Main entry point with all optimizations."""
    try:
        # Install UVLoop globally if available
        if config.ENABLE_UVLOOP:
            uvloop.install()
            logger.info("🔥 UVLoop installed globally")
        
        # Run the ultra-optimized server
        asyncio.run(run_ultra_server())
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server startup failed", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    main()

# Export for ASGI servers
application = app 