"""
Main Ultra Application - Refactored production-ready FastAPI application.
"""

import asyncio
import time
import signal
import gc
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
import uvicorn
import structlog

from core.ultra_config import config
from core.library_detector import detector
from core.ultra_optimizer import optimizer

# Prometheus metrics
from prometheus_client import generate_latest, Counter, Histogram, Gauge

# Configure structured logging
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

# Metrics
request_count = Counter('onyx_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('onyx_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
memory_usage = Gauge('onyx_memory_usage_bytes', 'Memory usage')
performance_score = Gauge('onyx_performance_score', 'Performance score based on available libraries')

# Global state
startup_time = 0.0
request_counter = 0

async def memory_monitor():
    """Background memory monitoring task."""
    if not detector.available_libraries.get('psutil'):
        return
    
    import psutil
    process = psutil.Process()
    
    while True:
        try:
            memory_usage.set(process.memory_info().rss)
            
            # Force GC if memory usage is high
            if process.memory_info().rss > config.MAX_MEMORY_MB * 1024 * 1024:
                gc.collect()
                logger.warning("🧹 Forced garbage collection", 
                             memory_mb=process.memory_info().rss / (1024 * 1024))
        except Exception as e:
            logger.error("Memory monitoring failed", error=str(e))
        
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global startup_time
    
    start = time.time()
    logger.info("🚀 Starting Onyx Ultra", version=config.VERSION)
    
    # Setup UVLoop if available
    if config.ENABLE_UVLOOP and detector.available_libraries.get('uvloop'):
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("✅ UVLoop enabled - 2-4x faster event loop")
        except Exception as e:
            logger.warning("UVLoop setup failed", error=str(e))
    
    # Optimize garbage collection
    gc.set_threshold(700, 10, 10)
    
    # Set performance score metric
    performance_score.set(detector.get_performance_score())
    
    # Start background monitoring
    if config.ENABLE_MONITORING and detector.available_libraries.get('psutil'):
        asyncio.create_task(memory_monitor())
    
    startup_time = time.time() - start
    logger.info("🎉 Onyx Ultra ready!", 
                startup_time=f"{startup_time:.3f}s",
                performance_score=detector.get_performance_score(),
                optimizations=len([k for k, v in detector.available_libraries.items() if v.available]))
    
    yield
    
    logger.info("🛑 Shutting down Onyx Ultra")
    optimizer.cleanup()

# Create FastAPI application
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    description="Ultra-optimized production API with cutting-edge libraries",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    lifespan=lifespan,
    default_response_class=ORJSONResponse if detector.available_libraries.get('orjson') else None
)

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Ultra-performance middleware."""
    global request_counter
    request_counter += 1
    
    start_time = time.perf_counter()
    
    # Generate correlation ID
    correlation_id = optimizer.hash_fast(f"{request.url.path}_{start_time}_{request_counter}")
    request.state.correlation_id = correlation_id
    request.state.start_time = start_time
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.perf_counter() - start_time
    
    # Update metrics
    if config.ENABLE_METRICS:
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
    
    # Add response headers
    response.headers.update({
        "X-Correlation-ID": correlation_id,
        "X-Response-Time": f"{duration:.4f}s",
        "X-Server": config.APP_NAME,
        "X-Version": config.VERSION,
        "X-Performance-Score": str(detector.get_performance_score())
    })
    
    # Periodic garbage collection
    if request_counter % config.GC_THRESHOLD == 0:
        gc.collect()
    
    return response

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    uptime = time.time() - startup_time
    
    health_data = {
        "status": "healthy",
        "version": config.VERSION,
        "uptime_seconds": uptime,
        "uptime_human": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
        "performance_score": detector.get_performance_score(),
        "requests_processed": request_counter,
        "avg_rps": request_counter / max(uptime, 1),
        "optimizations": {
            name: info.available for name, info in detector.OPTIMIZATION_LIBRARIES.items()
        }
    }
    
    # Add system info if psutil is available
    if detector.available_libraries.get('psutil'):
        import psutil
        process = psutil.Process()
        health_data["system"] = {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / (1024 * 1024),
            "memory_percent": process.memory_percent(),
            "threads": process.num_threads()
        }
    
    return health_data

@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

@app.get("/optimization-info")
async def optimization_info():
    """Get detailed optimization information."""
    return optimizer.get_optimization_info()

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
        "compression_ratio": len(compressed) / len(serialized) if serialized else 1,
        "processing_time_ms": duration,
        "library_used": detector.get_best_library("json").name if detector.get_best_library("json") else "json"
    }

@app.post("/api/hash")
async def ultra_hash(data: str):
    """Ultra-fast hashing endpoint."""
    start = time.perf_counter()
    
    hash_result = optimizer.hash_fast(data)
    
    duration = (time.perf_counter() - start) * 1000
    
    return {
        "hash": hash_result,
        "algorithm": detector.get_best_library("hash").name if detector.get_best_library("hash") else "sha256",
        "input_size": len(data),
        "processing_time_ms": duration
    }

@app.post("/api/process-data")
async def process_data(data: List[Dict[str, Any]], background_tasks: BackgroundTasks):
    """Ultra-fast data processing."""
    if not data:
        return {"error": "No data provided"}
    
    result = await optimizer.process_data_async(data)
    
    # Add cleanup task
    background_tasks.add_task(gc.collect)
    
    return {
        "input_records": len(data),
        "result": result,
        "performance_gain": f"{detector.get_best_library('data').performance_factor}x" if detector.get_best_library('data') else "1x"
    }

@app.get("/api/benchmark")
async def comprehensive_benchmark(iterations: int = 10000):
    """Comprehensive performance benchmark."""
    test_data = {
        "string": "benchmark_data" * 100,
        "numbers": list(range(100)),
        "nested": {"level1": {"level2": {"data": "test"}}},
        "timestamp": time.time()
    }
    
    benchmarks = {}
    
    # Serialization benchmark
    benchmarks["serialization"] = optimizer.benchmark_operation(
        optimizer.serialize, test_data, iterations
    )
    benchmarks["serialization"]["library"] = detector.get_best_library("json").name if detector.get_best_library("json") else "json"
    
    # Hashing benchmark
    test_str = str(test_data)
    benchmarks["hashing"] = optimizer.benchmark_operation(
        optimizer.hash_fast, test_str, iterations
    )
    benchmarks["hashing"]["library"] = detector.get_best_library("hash").name if detector.get_best_library("hash") else "sha256"
    
    # Compression benchmark
    test_bytes = optimizer.serialize(test_data)
    benchmarks["compression"] = optimizer.benchmark_operation(
        optimizer.compress, test_bytes, min(iterations, 1000)
    )
    benchmarks["compression"]["library"] = detector.get_best_library("compression").name if detector.get_best_library("compression") else "gzip"
    
    return {
        "iterations": iterations,
        "benchmarks": benchmarks,
        "performance_score": detector.get_performance_score(),
        "recommendations": detector.get_recommendations()
    }

@app.get("/status")
async def system_status():
    """Comprehensive system status."""
    return {
        "app": config.APP_NAME,
        "version": config.VERSION,
        "environment": config.ENVIRONMENT,
        "uptime_seconds": time.time() - startup_time,
        "configuration": config.to_dict(),
        "performance": {
            "score": detector.get_performance_score(),
            "requests_processed": request_counter,
            "gc_collections": gc.get_count()
        },
        "libraries": detector.get_status_report()
    }

# ============================================================================
# SERVER RUNNER
# ============================================================================

async def run_server():
    """Run the ultra-optimized server."""
    server_config = uvicorn.Config(
        app=app,
        host=config.HOST,
        port=config.PORT,
        workers=1,
        loop="uvloop" if config.ENABLE_UVLOOP and detector.available_libraries.get('uvloop') else "asyncio",
        http="httptools",
        log_level="info",
        access_log=config.DEBUG,
        server_header=False,
        date_header=False,
        backlog=config.BACKLOG,
        limit_concurrency=config.MAX_CONNECTIONS,
        timeout_keep_alive=config.TIMEOUT_KEEP_ALIVE,
        timeout_graceful_shutdown=config.TIMEOUT_GRACEFUL_SHUTDOWN
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
                performance_score=detector.get_performance_score())
    
    await server.serve()

def main():
    """Main entry point."""
    try:
        # Install UVLoop globally if available
        if config.ENABLE_UVLOOP and detector.available_libraries.get('uvloop'):
            import uvloop
            uvloop.install()
            logger.info("🔥 UVLoop installed globally")
        
        # Run the server
        asyncio.run(run_server())
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server startup failed", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    main()

# Export for ASGI
application = app 