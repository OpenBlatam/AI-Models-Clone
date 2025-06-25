"""
Production Enterprise Application - Ultra-Optimized & Complete.

Enterprise-grade production application with all optimizations integrated,
modular architecture, and maximum performance.
"""

import asyncio
import os
import time
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# FastAPI and ASGI
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
import uvicorn

# High-performance imports
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

# Monitoring
import structlog
from prometheus_client import generate_latest

# Our optimizers
from .optimizers import (
    MasterOptimizer, 
    OptimizationLevel,
    create_master_optimizer,
    FEATURES
)
from .monitoring import (
    setup_sentry, 
    comprehensive_health_check,
    track_performance,
    request_count,
    request_duration
)
from .exceptions import setup_exception_handlers
from .utils import generate_correlation_id

# Configure logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(30),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class ProductionConfig:
    """Ultra-optimized production configuration."""
    # App info
    app_name: str = "Onyx-Enterprise"
    version: str = "3.0.0"
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = min(32, os.cpu_count() * 4)
    
    # Performance
    optimization_level: OptimizationLevel = OptimizationLevel.ULTRA
    enable_uvloop: bool = UVLOOP_AVAILABLE
    enable_compression: bool = True
    
    # Database
    database_url: str = ""
    redis_url: str = ""
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    
    # Security
    allowed_origins: List[str] = None
    
    def __post_init__(self):
        # Load from environment
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = Environment(os.getenv("ENVIRONMENT", "production"))
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", str(self.port)))
        self.workers = int(os.getenv("WORKERS", str(self.workers)))
        self.database_url = os.getenv("DATABASE_URL", "")
        self.redis_url = os.getenv("REDIS_URL", "")
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        
        origins = os.getenv("ALLOWED_ORIGINS", "*")
        if origins == "*":
            self.allowed_origins = ["*"]
        else:
            self.allowed_origins = [o.strip() for o in origins.split(",")]
        
        if self.debug:
            self.enable_uvloop = False
            self.optimization_level = OptimizationLevel.ADVANCED


# Global state
config = ProductionConfig()
master_optimizer: Optional[MasterOptimizer] = None
startup_time = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ultra-optimized application lifespan."""
    global master_optimizer, startup_time
    
    start = time.time()
    logger.info("🚀 Starting Enterprise Application", 
               version=config.version, environment=config.environment.value)
    
    # Setup UVLoop
    if config.enable_uvloop:
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("✅ UVLoop enabled")
        except Exception as e:
            logger.warning("⚠️ UVLoop failed", error=str(e))
    
    # Initialize optimizers
    try:
        master_optimizer = create_master_optimizer(config.optimization_level)
        
        init_params = {}
        if config.database_url:
            init_params["database_configs"] = {"primary": config.database_url}
        if config.redis_url:
            init_params["database_configs"] = init_params.get("database_configs", {})
            init_params["database_configs"]["cache"] = config.redis_url
        
        results = await master_optimizer.initialize_all(**init_params)
        successful = sum(1 for r in results.values() if not str(r).startswith("error"))
        
        logger.info("🎯 Optimizers ready", successful=successful, total=len(results))
        
    except Exception as e:
        logger.error("❌ Optimizer init failed", error=str(e))
        master_optimizer = None
    
    # Setup monitoring
    if config.sentry_dsn:
        try:
            setup_sentry(config.sentry_dsn, config.environment.value)
            logger.info("📊 Monitoring enabled")
        except Exception as e:
            logger.warning("⚠️ Monitoring failed", error=str(e))
    
    # Health check
    try:
        health = await comprehensive_health_check()
        healthy = sum(1 for h in health.values() if h.healthy)
        logger.info("🏥 Health check", healthy=healthy, total=len(health))
    except Exception as e:
        logger.error("❌ Health check failed", error=str(e))
    
    startup_time = time.time() - start
    logger.info("🎉 Application ready", startup_time=f"{startup_time:.2f}s")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down")
    if master_optimizer:
        try:
            await master_optimizer.cleanup_all()
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error("❌ Cleanup failed", error=str(e))


# Create FastAPI app
app = FastAPI(
    title=config.app_name,
    description="Ultra-high performance enterprise application",
    version=config.version,
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
    openapi_url="/openapi.json" if config.debug else None,
    lifespan=lifespan,
    default_response_class=ORJSONResponse if JSON_AVAILABLE else None
)

# Setup CORS
if config.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=86400
    )

# Setup compression
if config.enable_compression:
    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=6)

# Setup exception handlers
setup_exception_handlers(app)


@app.middleware("http")
async def ultra_performance_middleware(request: Request, call_next):
    """Ultra-high performance middleware."""
    start_time = time.perf_counter()
    
    # Generate correlation ID
    correlation_id = None
    if master_optimizer and hasattr(master_optimizer, 'hashing'):
        try:
            correlation_id = master_optimizer.hashing.fast_hash(
                f"{request.url.path}_{start_time}_{id(request)}"
            )[:16]
        except:
            correlation_id = generate_correlation_id()[:16]
    else:
        correlation_id = generate_correlation_id()[:16]
    
    request.state.correlation_id = correlation_id
    
    # Setup logging context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        correlation_id=correlation_id,
        method=request.method,
        path=request.url.path
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Add headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Server"] = config.app_name
        response.headers["X-Version"] = config.version
        
    except Exception as e:
        logger.error("Request failed", error=str(e))
        response = ORJSONResponse(
            status_code=500,
            content={"error": "Internal error", "correlation_id": correlation_id}
        )
    
    # Metrics
    duration = time.perf_counter() - start_time
    
    try:
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            feature="enterprise"
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
            feature="enterprise"
        ).observe(duration)
    except:
        pass
    
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    if duration > 1.0:
        logger.warning("🐌 Slow request", duration=f"{duration:.3f}s", path=request.url.path)
    
    return response


# ============================================================================
# HEALTH AND MONITORING ENDPOINTS
# ============================================================================

@app.get("/health")
@track_performance("health", "monitoring")
async def health_check():
    """Comprehensive health check."""
    try:
        health_status = await comprehensive_health_check()
        
        optimizer_health = {"healthy": False}
        if master_optimizer:
            try:
                metrics = master_optimizer.get_comprehensive_metrics()
                optimizer_health = {
                    "healthy": True,
                    "optimizers": len(metrics["master"]["available_optimizers"])
                }
            except Exception as e:
                optimizer_health = {"healthy": False, "error": str(e)}
        
        overall_healthy = (
            all(s.healthy for s in health_status.values()) and
            optimizer_health["healthy"]
        )
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": time.time(),
            "version": config.version,
            "environment": config.environment.value,
            "uptime_seconds": time.time() - startup_time,
            "services": {n: {"healthy": s.healthy, "message": s.message} 
                        for n, s in health_status.items()},
            "optimizers": optimizer_health
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    """Prometheus metrics."""
    try:
        return generate_latest()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Metrics unavailable")


@app.get("/status")
async def app_status():
    """Application status."""
    return {
        "app": config.app_name,
        "version": config.version,
        "environment": config.environment.value,
        "optimization_level": config.optimization_level.value,
        "features": {
            "uvloop": config.enable_uvloop,
            "optimizers": master_optimizer is not None,
            "available_features": FEATURES
        },
        "uptime_seconds": time.time() - startup_time
    }


# ============================================================================
# OPTIMIZATION ENDPOINTS
# ============================================================================

@app.post("/api/v2/optimize/serialize")
@track_performance("serialize", "optimization")
async def ultra_serialize(data: Dict[Any, Any], format: str = "orjson"):
    """Ultra-fast serialization."""
    if not master_optimizer:
        raise HTTPException(status_code=503, detail="Optimizer not available")
    
    try:
        start = time.perf_counter()
        
        if hasattr(master_optimizer, 'serialization'):
            result = master_optimizer.serialization.serialize(data, format)
        else:
            result = orjson.dumps(data) if JSON_AVAILABLE else str(data).encode()
        
        duration = (time.perf_counter() - start) * 1000
        
        return {
            "status": "success",
            "format": format,
            "original_size": len(str(data)),
            "serialized_size": len(result),
            "processing_time_ms": duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Serialization failed: {str(e)}")


@app.post("/api/v2/optimize/hash")
@track_performance("hash", "optimization")
async def ultra_hash(data: Union[str, Dict], algorithm: str = "auto"):
    """Ultra-fast hashing."""
    if not master_optimizer:
        raise HTTPException(status_code=503, detail="Optimizer not available")
    
    try:
        start = time.perf_counter()
        
        data_str = str(data) if not isinstance(data, str) else data
        
        if hasattr(master_optimizer, 'hashing'):
            hash_result = master_optimizer.hashing.fast_hash(data_str)
        else:
            import hashlib
            hash_result = hashlib.sha256(data_str.encode()).hexdigest()
        
        duration = (time.perf_counter() - start) * 1000
        
        return {
            "status": "success",
            "hash": hash_result,
            "algorithm": algorithm,
            "input_size": len(data_str),
            "processing_time_ms": duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hashing failed: {str(e)}")


@app.get("/api/v2/optimize/benchmark")
@track_performance("benchmark", "optimization")
async def performance_benchmark(iterations: int = 1000):
    """Performance benchmark."""
    if not master_optimizer:
        raise HTTPException(status_code=503, detail="Optimizer not available")
    
    test_data = {"test": "x" * 1024, "number": 42, "list": list(range(100))}
    results = {"iterations": iterations}
    
    # Serialization benchmark
    if hasattr(master_optimizer, 'serialization'):
        start = time.perf_counter()
        for _ in range(iterations):
            master_optimizer.serialization.serialize(test_data)
        
        duration = time.perf_counter() - start
        results["serialization"] = {
            "total_time_s": duration,
            "ops_per_second": iterations / duration,
            "avg_time_ms": (duration / iterations) * 1000
        }
    
    # Hashing benchmark
    if hasattr(master_optimizer, 'hashing'):
        test_str = str(test_data)
        start = time.perf_counter()
        
        for _ in range(iterations):
            master_optimizer.hashing.fast_hash(test_str)
        
        duration = time.perf_counter() - start
        results["hashing"] = {
            "total_time_s": duration,
            "ops_per_second": iterations / duration,
            "avg_time_ms": (duration / iterations) * 1000
        }
    
    return results


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/admin/system")
async def system_info():
    """System information."""
    try:
        import psutil
        
        info = {
            "app": {
                "name": config.app_name,
                "version": config.version,
                "environment": config.environment.value,
                "uptime_seconds": time.time() - startup_time
            },
            "system": {
                "cpu_count": os.cpu_count(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "optimization": {
                "level": config.optimization_level.value,
                "uvloop_enabled": config.enable_uvloop,
                "optimizer_available": master_optimizer is not None
            }
        }
        
        if master_optimizer:
            try:
                info["optimizer_metrics"] = master_optimizer.get_comprehensive_metrics()
            except Exception as e:
                info["optimizer_error"] = str(e)
        
        return info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System info failed: {str(e)}")


@app.post("/admin/optimize/memory")
async def optimize_memory():
    """Trigger memory optimization."""
    if not master_optimizer or not hasattr(master_optimizer, 'core'):
        raise HTTPException(status_code=503, detail="Memory optimizer not available")
    
    try:
        before = master_optimizer.core.memory.get_memory_usage()
        result = master_optimizer.core.memory.optimize_memory_usage()
        after = master_optimizer.core.memory.get_memory_usage()
        
        return {
            "status": "success",
            "memory_before": before,
            "memory_after": after,
            "optimization_result": result,
            "memory_freed_percent": before.get("percent", 0) - after.get("percent", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory optimization failed: {str(e)}")


# ============================================================================
# APPLICATION RUNNER
# ============================================================================

async def run_server():
    """Run production server."""
    server_config = uvicorn.Config(
        app=app,
        host=config.host,
        port=config.port,
        workers=1,  # Single worker for async
        loop="uvloop" if config.enable_uvloop else "asyncio",
        http="httptools",
        log_level="info",
        access_log=config.debug,
        server_header=False,
        date_header=False
    )
    
    server = uvicorn.Server(server_config)
    
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} received, shutting down...")
        server.should_exit = True
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("🚀 Starting Enterprise Server", 
               host=config.host, port=config.port,
               workers=config.workers,
               optimization=config.optimization_level.value)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")


def main():
    """Main entry point."""
    try:
        if config.enable_uvloop:
            uvloop.install()
        
        asyncio.run(run_server())
        
    except KeyboardInterrupt:
        logger.info("Application stopped")
    except Exception as e:
        logger.error("Startup failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()


# Export for ASGI servers
application = app 