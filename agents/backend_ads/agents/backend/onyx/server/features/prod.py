"""
Onyx Production - Ultra-Optimized Enterprise Application.

Maximum performance production application with best-in-class optimizations.
"""

import asyncio
import os
import time
import signal
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
import uvicorn

# Ultra-performance imports
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

try:
    import orjson
    JSON_AVAILABLE = True
except ImportError:
    import json as orjson
    JSON_AVAILABLE = False

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    import blosc2
    BLOSC_AVAILABLE = True
except ImportError:
    BLOSC_AVAILABLE = False

import structlog
from prometheus_client import generate_latest, Counter, Histogram

# Configure ultra-fast logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Ultra-fast metrics
request_count = Counter('onyx_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('onyx_request_duration_seconds', 'Request duration', ['method', 'endpoint'])

# Configuration
class Config:
    APP_NAME = "Onyx-Prod"
    VERSION = "5.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    WORKERS = int(os.getenv("WORKERS", str(min(64, os.cpu_count() * 8))))
    ENABLE_UVLOOP = UVLOOP_AVAILABLE and not DEBUG

config = Config()
startup_time = 0.0

class UltraOptimizer:
    """Ultra-fast operations using best available libraries."""
    
    @staticmethod
    def serialize(data: Any) -> bytes:
        """Ultra-fast serialization."""
        if JSON_AVAILABLE:
            return orjson.dumps(data)
        else:
            import json
            return json.dumps(data).encode()
    
    @staticmethod
    def hash_fast(data: str) -> str:
        """Ultra-fast hashing."""
        if BLAKE3_AVAILABLE:
            return blake3.blake3(data.encode()).hexdigest()[:16]
        else:
            import hashlib
            return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def compress(data: bytes) -> bytes:
        """Ultra-fast compression."""
        if BLOSC_AVAILABLE and len(data) > 1024:
            return blosc2.compress(data, clevel=1, cname="lz4")
        return data

optimizer = UltraOptimizer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ultra-optimized lifespan."""
    global startup_time
    
    start = time.time()
    logger.info("🚀 Starting Onyx Production", version=config.VERSION)
    
    # Setup UVLoop
    if config.ENABLE_UVLOOP:
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("✅ UVLoop enabled")
        except Exception as e:
            logger.warning("UVLoop failed", error=str(e))
    
    startup_time = time.time() - start
    logger.info("🎉 Ready!", startup_time=f"{startup_time:.2f}s")
    
    yield
    
    logger.info("🛑 Shutting down")

# Create ultra-optimized app
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    docs_url="/docs" if config.DEBUG else None,
    lifespan=lifespan,
    default_response_class=ORJSONResponse if JSON_AVAILABLE else None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def ultra_middleware(request: Request, call_next):
    """Ultra-performance middleware."""
    start_time = time.perf_counter()
    
    # Ultra-fast correlation ID
    correlation_id = optimizer.hash_fast(f"{request.url.path}_{start_time}")
    request.state.correlation_id = correlation_id
    
    # Process request
    response = await call_next(request)
    
    # Metrics
    duration = time.perf_counter() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    # Headers
    response.headers.update({
        "X-Correlation-ID": correlation_id,
        "X-Response-Time": f"{duration:.3f}s",
        "X-Server": config.APP_NAME,
        "X-Version": config.VERSION
    })
    
    return response

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    """Ultra-fast health check."""
    return {
        "status": "healthy",
        "version": config.VERSION,
        "uptime_seconds": time.time() - startup_time,
        "optimizations": {
            "uvloop": config.ENABLE_UVLOOP,
            "orjson": JSON_AVAILABLE,
            "blake3": BLAKE3_AVAILABLE,
            "blosc2": BLOSC_AVAILABLE
        }
    }

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics."""
    return generate_latest()

@app.post("/api/serialize")
async def ultra_serialize(data: Dict[str, Any]):
    """Ultra-fast serialization endpoint."""
    start = time.perf_counter()
    
    serialized = optimizer.serialize(data)
    compressed = optimizer.compress(serialized)
    
    duration = (time.perf_counter() - start) * 1000
    
    return {
        "original_size": len(str(data)),
        "serialized_size": len(serialized),
        "compressed_size": len(compressed),
        "compression_ratio": len(compressed) / len(serialized),
        "processing_time_ms": duration
    }

@app.post("/api/hash")
async def ultra_hash(data: str):
    """Ultra-fast hashing endpoint."""
    start = time.perf_counter()
    
    hash_result = optimizer.hash_fast(data)
    
    duration = (time.perf_counter() - start) * 1000
    
    return {
        "hash": hash_result,
        "algorithm": "blake3" if BLAKE3_AVAILABLE else "sha256",
        "input_size": len(data),
        "processing_time_ms": duration
    }

@app.get("/api/benchmark")
async def benchmark(iterations: int = 10000):
    """Performance benchmark."""
    test_data = {"test": "data" * 100, "numbers": list(range(100))}
    
    # Serialization benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        optimizer.serialize(test_data)
    serialization_time = time.perf_counter() - start
    
    # Hashing benchmark
    test_str = str(test_data)
    start = time.perf_counter()
    for _ in range(iterations):
        optimizer.hash_fast(test_str)
    hashing_time = time.perf_counter() - start
    
    return {
        "iterations": iterations,
        "serialization": {
            "total_time_s": serialization_time,
            "ops_per_second": iterations / serialization_time
        },
        "hashing": {
            "total_time_s": hashing_time,
            "ops_per_second": iterations / hashing_time
        }
    }

@app.get("/status")
async def status():
    """System status."""
    try:
        import psutil
        return {
            "app": config.APP_NAME,
            "version": config.VERSION,
            "uptime_seconds": time.time() - startup_time,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "cpu_count": os.cpu_count()
            },
            "config": {
                "workers": config.WORKERS,
                "uvloop": config.ENABLE_UVLOOP,
                "debug": config.DEBUG
            }
        }
    except ImportError:
        return {"error": "psutil not available"}

# ============================================================================
# SERVER
# ============================================================================

async def run_server():
    """Run ultra-optimized server."""
    server_config = uvicorn.Config(
        app=app,
        host=config.HOST,
        port=config.PORT,
        workers=1,
        loop="uvloop" if config.ENABLE_UVLOOP else "asyncio",
        http="httptools",
        log_level="info",
        access_log=config.DEBUG,
        server_header=False
    )
    
    server = uvicorn.Server(server_config)
    
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} received, shutting down...")
        server.should_exit = True
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("🚀 Starting server", host=config.HOST, port=config.PORT, workers=config.WORKERS)
    
    await server.serve()

def main():
    """Main entry point."""
    try:
        if config.ENABLE_UVLOOP:
            uvloop.install()
        
        asyncio.run(run_server())
        
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error("Startup failed", error=str(e))

if __name__ == "__main__":
    main()

# Export for ASGI
application = app 