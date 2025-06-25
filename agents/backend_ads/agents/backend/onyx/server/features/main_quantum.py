"""
Onyx Quantum Main - Refactored quantum-optimized FastAPI application.

This is the main entry point for the quantum-optimized Onyx application
with a clean, modular architecture and maximum performance.
"""

import asyncio
import time
import signal
import gc
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
import uvicorn
import structlog

# Import refactored core modules
from core import (
    config, 
    quantum_optimizer, 
    detector,
    QuantumMiddleware,
    QuantumMonitor
)

# Prometheus metrics
from prometheus_client import generate_latest, Counter, Histogram, Gauge, start_http_server

# Configure quantum logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(10),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Quantum metrics
REQUEST_COUNT = Counter('onyx_quantum_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('onyx_quantum_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
QUANTUM_SCORE = Gauge('onyx_quantum_score', 'Quantum optimization score')
THROUGHPUT = Gauge('onyx_quantum_throughput_rps', 'Requests per second')

# Global state
startup_time = 0.0
request_counter = 0
quantum_monitor = None

@asynccontextmanager
async def quantum_lifespan(app: FastAPI):
    """Quantum application lifespan management."""
    global startup_time, quantum_monitor
    
    start = time.time()
    logger.info("🌌 Starting Onyx Quantum Refactored", 
                version=config.VERSION,
                quantum_score=detector.quantum_score)
    
    # Setup quantum event loop
    if detector.available_libraries.get('uvloop'):
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("⚡ Quantum UVLoop enabled")
        except Exception as e:
            logger.warning("UVLoop setup failed", error=str(e))
    
    # Optimize garbage collection
    gc.set_threshold(200, 3, 3)
    
    # Start metrics server
    if config.ENABLE_METRICS:
        try:
            start_http_server(config.METRICS_PORT)
            logger.info(f"📊 Quantum metrics server started on port {config.METRICS_PORT}")
        except Exception as e:
            logger.warning("Metrics server failed", error=str(e))
    
    # Initialize quantum monitoring
    if config.ENABLE_MONITORING:
        quantum_monitor = QuantumMonitor()
        asyncio.create_task(quantum_monitor.start_monitoring())
    
    # Set quantum score metric
    QUANTUM_SCORE.set(detector.quantum_score)
    
    startup_time = time.time() - start
    logger.info("🎉 Quantum system ready!", 
                startup_time=f"{startup_time:.3f}s",
                quantum_score=f"{detector.quantum_score:.1f}x",
                workers=config.WORKERS)
    
    yield
    
    logger.info("🌌 Shutting down Quantum system")
    if quantum_monitor:
        await quantum_monitor.stop_monitoring()
    quantum_optimizer.cleanup()

# Create quantum FastAPI application
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    description="Quantum-optimized production API with refactored architecture",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    lifespan=quantum_lifespan,
    default_response_class=ORJSONResponse if detector.available_libraries.get('orjson') else None
)

# Quantum middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=256)

# Add quantum performance middleware
quantum_middleware = QuantumMiddleware(
    request_counter_callback=lambda: globals().update(request_counter=request_counter + 1),
    metrics_callback=lambda method, endpoint, status, duration: (
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc(),
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    )
)

app.add_middleware(type(quantum_middleware), quantum_middleware=quantum_middleware)

# ============================================================================
# QUANTUM API ENDPOINTS
# ============================================================================

@app.get("/health")
async def quantum_health():
    """Quantum health check with comprehensive analysis."""
    uptime = time.time() - startup_time
    
    health_data = {
        "status": "quantum",
        "version": config.VERSION,
        "environment": config.ENVIRONMENT,
        "uptime_seconds": uptime,
        "uptime_human": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
        "quantum_score": f"{detector.quantum_score:.1f}x",
        "requests_processed": request_counter,
        "avg_rps": request_counter / max(uptime, 1),
        "quantum_optimizations": {
            name: lib.available for name, lib in detector.QUANTUM_LIBRARIES.items()
        }
    }
    
    # Add system info if available
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
async def quantum_metrics():
    """Quantum Prometheus metrics."""
    return generate_latest()

@app.get("/quantum/status")
async def quantum_status():
    """Comprehensive quantum system status."""
    return {
        "application": {
            "name": config.APP_NAME,
            "version": config.VERSION,
            "environment": config.ENVIRONMENT,
            "uptime_seconds": time.time() - startup_time,
            "quantum_score": detector.quantum_score
        },
        "performance": {
            "requests_processed": request_counter,
            "gc_collections": gc.get_count(),
            "quantum_features": detector.get_quantum_features()
        },
        "configuration": config.to_dict(),
        "library_status": detector.get_status_report()
    }

@app.get("/quantum/optimization-info")
async def quantum_optimization_info():
    """Detailed quantum optimization information."""
    return {
        "quantum_score": detector.quantum_score,
        "optimization_report": detector.get_status_report(),
        "recommendations": detector.get_optimization_recommendations(),
        "category_coverage": detector.get_category_coverage(),
        "quantum_features": detector.get_quantum_features()
    }

@app.post("/api/quantum/serialize")
async def quantum_serialize_endpoint(data: Dict[str, Any]):
    """Quantum serialization endpoint."""
    start = time.perf_counter()
    
    # Use quantum optimizer
    serialized = quantum_optimizer.quantum_serialize(data)
    compressed = quantum_optimizer.quantum_compress(serialized)
    
    duration = (time.perf_counter() - start) * 1000
    
    best_serializer = detector.get_best_library("serialization")
    
    return {
        "quantum_success": True,
        "original_size": len(str(data)),
        "serialized_size": len(serialized),
        "compressed_size": len(compressed),
        "compression_ratio": len(compressed) / len(serialized) if serialized else 1,
        "processing_time_ms": duration,
        "library_used": best_serializer.name if best_serializer else "json",
        "performance_gain": f"{best_serializer.performance_factor:.1f}x" if best_serializer else "1x"
    }

@app.post("/api/quantum/hash")
async def quantum_hash_endpoint(data: str):
    """Quantum hashing endpoint."""
    start = time.perf_counter()
    
    hash_result = quantum_optimizer.quantum_hash(data)
    
    duration = (time.perf_counter() - start) * 1000
    
    best_hasher = detector.get_best_library("hashing")
    
    return {
        "quantum_success": True,
        "hash": hash_result,
        "algorithm": best_hasher.name if best_hasher else "sha256",
        "input_size": len(data),
        "processing_time_ms": duration,
        "quantum_features": best_hasher.quantum_features if best_hasher else []
    }

@app.post("/api/quantum/process-data")
async def quantum_process_data_endpoint(data: List[Dict[str, Any]], background_tasks: BackgroundTasks):
    """Quantum data processing endpoint."""
    if not data:
        raise HTTPException(status_code=400, detail="No quantum data provided")
    
    result = await quantum_optimizer.quantum_process_data(data)
    
    # Add cleanup task
    background_tasks.add_task(gc.collect)
    
    best_processor = detector.get_best_library("dataframes")
    
    return {
        "quantum_success": True,
        "input_records": len(data),
        "processing_result": result,
        "library_used": best_processor.name if best_processor else "standard",
        "performance_gain": f"{best_processor.performance_factor:.1f}x" if best_processor else "1x",
        "quantum_features": best_processor.quantum_features if best_processor else []
    }

@app.get("/api/quantum/benchmark")
async def quantum_benchmark_endpoint(iterations: int = 50000):
    """Quantum performance benchmark."""
    if iterations > 500000:
        raise HTTPException(status_code=400, detail="Too many quantum iterations")
    
    test_data = {
        "quantum": True,
        "data": "benchmark_data" * 200,
        "numbers": list(range(500)),
        "nested": {"quantum": {"performance": {"test": "data"}}},
        "timestamp": time.time()
    }
    
    benchmarks = {}
    
    # Serialization benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        quantum_optimizer.quantum_serialize(test_data)
    serialization_time = time.perf_counter() - start
    
    best_serializer = detector.get_best_library("serialization")
    benchmarks["serialization"] = {
        "total_time_s": serialization_time,
        "ops_per_second": iterations / serialization_time,
        "library": best_serializer.name if best_serializer else "json",
        "performance_factor": best_serializer.performance_factor if best_serializer else 1.0
    }
    
    # Hashing benchmark
    test_str = str(test_data)
    start = time.perf_counter()
    for _ in range(iterations):
        quantum_optimizer.quantum_hash(test_str)
    hashing_time = time.perf_counter() - start
    
    best_hasher = detector.get_best_library("hashing")
    benchmarks["hashing"] = {
        "total_time_s": hashing_time,
        "ops_per_second": iterations / hashing_time,
        "library": best_hasher.name if best_hasher else "sha256",
        "performance_factor": best_hasher.performance_factor if best_hasher else 1.0
    }
    
    # Compression benchmark
    test_bytes = quantum_optimizer.quantum_serialize(test_data)
    start = time.perf_counter()
    for _ in range(min(iterations, 5000)):
        quantum_optimizer.quantum_compress(test_bytes)
    compression_time = time.perf_counter() - start
    
    best_compressor = detector.get_best_library("compression")
    benchmarks["compression"] = {
        "total_time_s": compression_time,
        "ops_per_second": min(iterations, 5000) / compression_time,
        "library": best_compressor.name if best_compressor else "gzip",
        "performance_factor": best_compressor.performance_factor if best_compressor else 1.0
    }
    
    return {
        "quantum_success": True,
        "iterations": iterations,
        "quantum_benchmarks": benchmarks,
        "overall_quantum_score": detector.quantum_score,
        "system_info": {
            "available_optimizations": len(detector.available_libraries),
            "total_optimizations": len(detector.QUANTUM_LIBRARIES),
            "quantum_features": detector.get_quantum_features()
        }
    }

# ============================================================================
# QUANTUM SERVER
# ============================================================================

async def run_quantum_server():
    """Run quantum-optimized server."""
    server_config = uvicorn.Config(
        app=app,
        host=config.HOST,
        port=config.PORT,
        workers=1,
        loop="uvloop" if detector.available_libraries.get('uvloop') else "asyncio",
        http="httptools",
        log_level="info" if not config.DEBUG else "debug",
        access_log=config.DEBUG,
        server_header=False,
        date_header=False,
        backlog=config.BACKLOG,
        limit_concurrency=config.MAX_CONNECTIONS,
        timeout_keep_alive=120,
        timeout_graceful_shutdown=60,
    )
    
    server = uvicorn.Server(server_config)
    
    def quantum_signal_handler(signum, frame):
        logger.info(f"Quantum signal {signum} received, graceful shutdown...")
        server.should_exit = True
    
    signal.signal(signal.SIGTERM, quantum_signal_handler)
    signal.signal(signal.SIGINT, quantum_signal_handler)
    
    logger.info("🌌 Starting Quantum Server", 
                host=config.HOST, 
                port=config.PORT,
                quantum_score=f"{detector.quantum_score:.1f}x")
    
    await server.serve()

def main():
    """Quantum main entry point."""
    try:
        # Global quantum UVLoop installation
        if detector.available_libraries.get('uvloop'):
            import uvloop
            uvloop.install()
            logger.info("🌌 Quantum UVLoop installed globally")
        
        # Run quantum server
        asyncio.run(run_quantum_server())
        
    except KeyboardInterrupt:
        logger.info("Quantum server stopped by user")
    except Exception as e:
        logger.error("Quantum server failed", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    main()

# Export for quantum ASGI servers
application = app 