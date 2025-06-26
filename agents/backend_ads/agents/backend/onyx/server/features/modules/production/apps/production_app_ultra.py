"""
Ultra-Optimized Production Application - Enterprise Grade.

Complete production-ready application with all optimization libraries integrated,
ultra-fast performance, comprehensive monitoring, and enterprise features.
"""

import asyncio
import os
import time
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional, Union
import logging
from pathlib import Path

# FastAPI and ASGI
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
from fastapi.exception_handlers import http_exception_handler
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

# Monitoring and observability
import structlog
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Load balancing and process management
try:
    import gunicorn
    GUNICORN_AVAILABLE = True
except ImportError:
    GUNICORN_AVAILABLE = False

# Our optimized modules
from .optimizers import (
    MasterOptimizer, 
    OptimizationLevel,
    create_master_optimizer,
    DATABASE_OPTIMIZER_AVAILABLE,
    NETWORK_OPTIMIZER_AVAILABLE,
    ML_OPTIMIZER_AVAILABLE
)

from .monitoring import (
    setup_sentry, 
    comprehensive_health_check,
    track_performance,
    monitor_operation,
    request_count,
    request_duration,
    performance_tracker
)

from .exceptions import (
    OnyxBaseException,
    ValidationError,
    ServiceError,
    handle_exceptions,
    setup_exception_handlers
)

from .config import get_config, Environment
from .utils import generate_correlation_id, safe_json_serialize

# Configure ultra-fast structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer() if os.getenv("DEBUG") else structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class ProductionConfig:
    """Ultra-optimized production configuration."""
    
    def __init__(self):
        self.app_name = "Onyx-Ultra-Production"
        self.version = "2.0.0"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "production")
        
        # Server settings
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.workers = int(os.getenv("WORKERS", str(min(32, os.cpu_count() * 4))))
        
        # Performance settings
        self.optimization_level = OptimizationLevel.ULTRA
        self.enable_uvloop = UVLOOP_AVAILABLE and not self.debug
        self.enable_http2 = True
        self.max_request_size = 100 * 1024 * 1024  # 100MB
        
        # Database settings
        self.database_configs = {
            "primary": os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db"),
            "replica": os.getenv("DATABASE_REPLICA_URL", ""),
            "cache": os.getenv("REDIS_URL", "redis://localhost:6379/0")
        }
        
        # Monitoring
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.enable_metrics = True
        self.enable_tracing = True
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Security
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT", "10000"))
        
        # Features
        self.enable_caching = True
        self.enable_compression = True
        self.enable_ml_features = ML_OPTIMIZER_AVAILABLE
        self.enable_advanced_networking = NETWORK_OPTIMIZER_AVAILABLE


# Global configuration and services
config = ProductionConfig()
master_optimizer: Optional[MasterOptimizer] = None
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ultra-optimized application lifespan management."""
    global master_optimizer, startup_time
    
    startup_start = time.time()
    logger.info("🚀 Starting Ultra-Optimized Production Application", 
               version=config.version,
               environment=config.environment,
               optimization_level=config.optimization_level.value)
    
    # Setup event loop optimization
    if config.enable_uvloop and UVLOOP_AVAILABLE:
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("✅ UVLoop enabled for maximum performance")
        except Exception as e:
            logger.warning("⚠️  UVLoop setup failed", error=str(e))
    
    # Initialize master optimizer
    try:
        master_optimizer = create_master_optimizer(config.optimization_level)
        
        # Prepare initialization parameters
        init_params = {}
        if config.database_configs["primary"]:
            init_params["database_configs"] = {
                k: v for k, v in config.database_configs.items() if v
            }
        
        # Initialize all optimizers
        optimization_results = await master_optimizer.initialize_all(**init_params)
        
        successful_optimizers = sum(
            1 for result in optimization_results.values() 
            if isinstance(result, dict) and not result.get("error")
        )
        
        logger.info("🎯 Optimizers initialized", 
                   successful=successful_optimizers,
                   total=len(optimization_results),
                   details=optimization_results)
        
    except Exception as e:
        logger.error("❌ Master optimizer initialization failed", error=str(e))
        # Continue with limited functionality
        master_optimizer = None
    
    # Setup monitoring
    if config.sentry_dsn:
        try:
            setup_sentry(config.sentry_dsn, config.environment)
            logger.info("📊 Sentry monitoring enabled")
        except Exception as e:
            logger.warning("⚠️  Sentry setup failed", error=str(e))
    
    # Comprehensive startup health check
    try:
        health_status = await comprehensive_health_check()
        healthy_services = sum(1 for h in health_status.values() if h.healthy)
        total_services = len(health_status)
        
        logger.info("🏥 Health check completed",
                   healthy=healthy_services,
                   total=total_services,
                   health_ratio=f"{healthy_services}/{total_services}")
        
        if healthy_services < total_services:
            logger.warning("⚠️  Some services are unhealthy", 
                          unhealthy=[k for k, v in health_status.items() if not v.healthy])
    
    except Exception as e:
        logger.error("❌ Health check failed", error=str(e))
    
    startup_time = time.time() - startup_start
    logger.info("🎉 Application startup completed", 
               startup_time_seconds=f"{startup_time:.2f}",
               optimization_level=config.optimization_level.value,
               workers=config.workers)
    
    yield
    
    # Shutdown
    shutdown_start = time.time()
    logger.info("🛑 Shutting down Ultra-Optimized Application")
    
    # Cleanup optimizers
    if master_optimizer:
        try:
            await master_optimizer.cleanup_all()
            logger.info("✅ Optimizers cleanup completed")
        except Exception as e:
            logger.error("❌ Optimizers cleanup failed", error=str(e))
    
    shutdown_time = time.time() - shutdown_start
    logger.info("👋 Application shutdown completed", 
               shutdown_time_seconds=f"{shutdown_time:.2f}")


# Create ultra-optimized FastAPI application
app = FastAPI(
    title=config.app_name,
    description="Ultra-high performance enterprise application with comprehensive optimizations",
    version=config.version,
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
    openapi_url="/openapi.json" if config.debug else None,
    lifespan=lifespan,
    default_response_class=ORJSONResponse if JSON_AVAILABLE else None
)

# Ultra-optimized middleware stack
if config.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=86400  # 24 hours cache
    )

# Intelligent compression middleware
app.add_middleware(
    GZipMiddleware, 
    minimum_size=1000,
    compresslevel=6  # Balanced compression
)

# Setup comprehensive exception handlers
setup_exception_handlers(app)


@app.middleware("http")
async def ultra_performance_middleware(request: Request, call_next):
    """Ultra-high performance request middleware with comprehensive optimization."""
    # Start performance tracking
    start_time = time.perf_counter()
    request_size = int(request.headers.get("content-length", 0))
    
    # Generate ultra-fast correlation ID
    correlation_id = None
    if master_optimizer and master_optimizer.hashing:
        correlation_id = master_optimizer.hashing.fast_hash(
            f"{request.url.path}_{start_time}_{id(request)}"
        )[:16]
    else:
        correlation_id = generate_correlation_id()[:16]
    
    request.state.correlation_id = correlation_id
    request.state.start_time = start_time
    
    # Setup structured logging context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        correlation_id=correlation_id,
        method=request.method,
        path=request.url.path,
        user_agent=request.headers.get("user-agent", "")[:100]
    )
    
    # Memory optimization check
    memory_before = None
    if master_optimizer and master_optimizer.core and master_optimizer.core.memory:
        try:
            memory_before = master_optimizer.core.memory.get_memory_usage()
        except:
            pass
    
    # Process request with error handling
    response = None
    error_occurred = False
    
    try:
        # Execute request
        response = await call_next(request)
        
        # Post-process response
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Server"] = config.app_name
        response.headers["X-Version"] = config.version
        
    except Exception as e:
        error_occurred = True
        logger.error("Request processing failed", 
                    error=str(e),
                    path=request.url.path,
                    method=request.method)
        
        # Create error response
        response = ORJSONResponse(
            status_code=500,
            content={"error": "Internal server error", "correlation_id": correlation_id}
        )
        response.headers["X-Correlation-ID"] = correlation_id
    
    # Calculate comprehensive metrics
    duration = time.perf_counter() - start_time
    status_code = response.status_code if response else 500
    
    # Memory usage delta
    memory_delta = 0
    if memory_before and master_optimizer and master_optimizer.core and master_optimizer.core.memory:
        try:
            memory_after = master_optimizer.core.memory.get_memory_usage()
            memory_delta = memory_after.get("percent", 0) - memory_before.get("percent", 0)
        except:
            pass
    
    # Record metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=status_code,
        feature="production_api"
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path,
        feature="production_api"
    ).observe(duration)
    
    # Enhanced response headers
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    response.headers["X-Request-Size"] = str(request_size)
    response.headers["X-Memory-Delta"] = f"{memory_delta:.2f}%"
    
    # Log performance if needed
    if duration > 1.0:  # Slow request threshold
        logger.warning("🐌 Slow request detected", 
                      duration=f"{duration:.3f}s",
                      endpoint=request.url.path,
                      method=request.method,
                      status_code=status_code,
                      memory_delta=f"{memory_delta:.2f}%")
    elif config.debug:
        logger.info("✅ Request completed", 
                   duration=f"{duration:.3f}s",
                   status_code=status_code)
    
    return response


# ============================================================================
# HEALTH AND MONITORING ENDPOINTS
# ============================================================================

@app.get("/health", tags=["monitoring"], response_class=ORJSONResponse)
@track_performance("health_check", "monitoring")
async def ultra_health_check():
    """Comprehensive health check with detailed system information."""
    try:
        health_status = await comprehensive_health_check()
        
        # Add optimizer-specific health checks
        optimizer_health = {}
        if master_optimizer:
            try:
                optimizer_metrics = master_optimizer.get_comprehensive_metrics()
                optimizer_health = {
                    "master_optimizer": {
                        "healthy": True,
                        "available_optimizers": optimizer_metrics["master"]["available_optimizers"],
                        "successful_initializations": optimizer_metrics["master"]["successful_initializations"]
                    }
                }
            except Exception as e:
                optimizer_health = {
                    "master_optimizer": {
                        "healthy": False,
                        "error": str(e)
                    }
                }
        
        overall_healthy = (
            all(status.healthy for status in health_status.values()) and
            optimizer_health.get("master_optimizer", {}).get("healthy", True)
        )
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": health_status["system"].timestamp.isoformat(),
            "version": config.version,
            "environment": config.environment,
            "uptime_seconds": time.time() - startup_time,
            "services": {
                name: {
                    "healthy": status.healthy,
                    "message": status.message,
                    "details": status.details
                }
                for name, status in health_status.items()
            },
            "optimizers": optimizer_health
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.get("/metrics", response_class=PlainTextResponse, tags=["monitoring"])
async def prometheus_metrics():
    """Ultra-fast Prometheus metrics endpoint."""
    try:
        return generate_latest()
    except Exception as e:
        logger.error("Metrics generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Metrics unavailable")


@app.get("/metrics/detailed", tags=["monitoring"])
@track_performance("detailed_metrics", "monitoring")
async def detailed_performance_metrics():
    """Comprehensive performance metrics dashboard."""
    try:
        metrics = {
            "timestamp": time.time(),
            "uptime_seconds": time.time() - startup_time,
            "app_info": {
                "name": config.app_name,
                "version": config.version,
                "environment": config.environment,
                "optimization_level": config.optimization_level.value
            }
        }
        
        # Add optimizer metrics
        if master_optimizer:
            try:
                optimizer_metrics = master_optimizer.get_comprehensive_metrics()
                metrics["optimizers"] = optimizer_metrics
            except Exception as e:
                metrics["optimizers"] = {"error": str(e)}
        
        # Add performance tracker metrics
        try:
            performance_stats = {}
            for operation in performance_tracker._metrics.keys():
                performance_stats[operation] = performance_tracker.get_stats(operation)
            metrics["performance_tracker"] = performance_stats
        except Exception as e:
            metrics["performance_tracker"] = {"error": str(e)}
        
        return metrics
        
    except Exception as e:
        logger.error("Detailed metrics generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Detailed metrics unavailable")


# ============================================================================
# ULTRA-OPTIMIZED API ENDPOINTS
# ============================================================================

@app.post("/api/v2/optimize/serialize", tags=["optimization"])
@handle_exceptions
@track_performance("ultra_serialize", "optimization")
async def ultra_serialize_data(
    data: Dict[Any, Any],
    format: str = "orjson",
    compress: bool = True
):
    """Ultra-fast data serialization with compression."""
    if not master_optimizer or not master_optimizer.serialization:
        raise ServiceError("Serialization optimizer not available")
    
    try:
        start_time = time.perf_counter()
        
        # Serialize using optimal format
        serialized = master_optimizer.serialization.serialize(data, format)
        
        result = {
            "status": "success",
            "original_size": len(str(data)),
            "serialized_size": len(serialized),
            "format_used": format,
            "processing_time_ms": (time.perf_counter() - start_time) * 1000
        }
        
        if compress and master_optimizer.core and master_optimizer.core.compression:
            compressed, compression_algo = master_optimizer.core.compression.compress(serialized)
            result.update({
                "compressed_size": len(compressed),
                "compression_ratio": len(compressed) / len(serialized),
                "compression_algorithm": compression_algo
            })
        
        return result
        
    except Exception as e:
        logger.error("Serialization failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Serialization failed: {str(e)}")


@app.post("/api/v2/optimize/hash", tags=["optimization"])
@handle_exceptions  
@track_performance("ultra_hash", "optimization")
async def ultra_hash_data(
    data: Union[str, Dict[str, Any]],
    algorithm: str = "auto",
    return_multiple: bool = False
):
    """Ultra-fast data hashing with multiple algorithms."""
    if not master_optimizer or not master_optimizer.hashing:
        raise ServiceError("Hashing optimizer not available")
    
    try:
        start_time = time.perf_counter()
        
        # Convert to string if needed
        if isinstance(data, dict):
            data_str = orjson.dumps(data).decode() if JSON_AVAILABLE else str(data)
        else:
            data_str = str(data)
        
        if return_multiple:
            # Return multiple hash algorithms
            hashes = {}
            available_algos = ["blake3", "xxhash", "sha256"]
            
            for algo in available_algos:
                try:
                    hash_result = master_optimizer.hashing.hash(data_str, algorithm=algo)
                    hashes[algo] = hash_result
                except:
                    continue
            
            result = {
                "status": "success",
                "input_size": len(data_str),
                "hashes": hashes,
                "processing_time_ms": (time.perf_counter() - start_time) * 1000
            }
        else:
            # Single hash
            hash_result = master_optimizer.hashing.hash(data_str, algorithm=algorithm)
            result = {
                "status": "success",
                "hash": hash_result,
                "algorithm_used": algorithm,
                "input_size": len(data_str),
                "processing_time_ms": (time.perf_counter() - start_time) * 1000
            }
        
        return result
        
    except Exception as e:
        logger.error("Hashing failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Hashing failed: {str(e)}")


@app.get("/api/v2/optimize/benchmark", tags=["optimization"])
@handle_exceptions
@track_performance("ultra_benchmark", "optimization")
async def ultra_performance_benchmark(
    iterations: int = 1000,
    data_size_kb: int = 10
):
    """Ultra-comprehensive performance benchmark."""
    if not master_optimizer:
        raise ServiceError("Master optimizer not available")
    
    try:
        # Generate test data
        test_data = {"test": "x" * (data_size_kb * 1024)}
        results = {
            "benchmark_config": {
                "iterations": iterations,
                "data_size_kb": data_size_kb,
                "optimization_level": config.optimization_level.value
            },
            "results": {}
        }
        
        # Serialization benchmark
        if master_optimizer.serialization:
            start_time = time.perf_counter()
            for _ in range(iterations):
                master_optimizer.serialization.serialize(test_data)
            
            serialization_time = time.perf_counter() - start_time
            results["results"]["serialization"] = {
                "total_time_seconds": serialization_time,
                "ops_per_second": iterations / serialization_time,
                "avg_time_ms": (serialization_time / iterations) * 1000
            }
        
        # Hashing benchmark
        if master_optimizer.hashing:
            test_string = str(test_data)
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                master_optimizer.hashing.fast_hash(test_string)
            
            hashing_time = time.perf_counter() - start_time
            results["results"]["hashing"] = {
                "total_time_seconds": hashing_time,
                "ops_per_second": iterations / hashing_time,
                "avg_time_ms": (hashing_time / iterations) * 1000
            }
        
        # Memory benchmark
        if master_optimizer.core and master_optimizer.core.memory:
            memory_before = master_optimizer.core.memory.get_memory_usage()
            
            # Simulate memory-intensive operations
            temp_data = []
            for i in range(iterations // 10):  # Fewer iterations for memory test
                temp_data.append({"data": test_data, "index": i})
            
            memory_after = master_optimizer.core.memory.get_memory_usage()
            
            results["results"]["memory"] = {
                "memory_before_percent": memory_before.get("percent", 0),
                "memory_after_percent": memory_after.get("percent", 0),
                "memory_delta_percent": memory_after.get("percent", 0) - memory_before.get("percent", 0),
                "objects_created": len(temp_data)
            }
            
            # Cleanup
            del temp_data
        
        results["total_benchmark_time_seconds"] = time.perf_counter() - start_time
        return results
        
    except Exception as e:
        logger.error("Benchmark failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {str(e)}")


# ============================================================================
# SPECIALIZED OPTIMIZER ENDPOINTS
# ============================================================================

@app.post("/api/v2/network/request", tags=["network"])
@handle_exceptions
@track_performance("optimized_request", "network")
async def ultra_optimized_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0
):
    """Ultra-optimized network request with advanced features."""
    if not master_optimizer or not master_optimizer.network:
        raise ServiceError("Network optimizer not available")
    
    try:
        # Prepare request parameters
        kwargs = {}
        if headers:
            kwargs["headers"] = headers
        if data:
            kwargs["json"] = data
        if timeout != 30.0:
            kwargs["timeout"] = timeout
        
        # Execute optimized request
        response_data, metadata = await master_optimizer.network.request(
            method, url, **kwargs
        )
        
        return {
            "status": "success",
            "response_data": response_data,
            "metadata": metadata,
            "optimization_features": master_optimizer.network.get_performance_metrics()["features"]
        }
        
    except Exception as e:
        logger.error("Optimized request failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")


@app.post("/api/v2/ml/inference", tags=["machine_learning"])
@handle_exceptions
@track_performance("ml_inference", "ml")
async def ultra_ml_inference(
    model_name: str,
    input_data: List[float],
    use_cache: bool = True,
    use_batching: bool = True
):
    """Ultra-fast ML inference with optimization."""
    if not master_optimizer or not master_optimizer.ml:
        raise ServiceError("ML optimizer not available")
    
    try:
        import numpy as np
        
        # Convert input to numpy array
        input_array = np.array(input_data, dtype=np.float32)
        
        # Execute optimized inference
        result = await master_optimizer.ml.inference(
            model_name=model_name,
            input_data=input_array,
            use_cache=use_cache,
            use_batching=use_batching
        )
        
        return {
            "status": "success",
            "model_name": model_name,
            "input_shape": input_array.shape,
            "result": result.tolist() if hasattr(result, 'tolist') else result,
            "ml_metrics": master_optimizer.ml.get_performance_metrics()["inference_stats"]
        }
        
    except Exception as e:
        logger.error("ML inference failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"ML inference failed: {str(e)}")


# ============================================================================
# SYSTEM ADMINISTRATION ENDPOINTS
# ============================================================================

@app.post("/admin/optimize/memory", tags=["admin"])
@handle_exceptions
async def optimize_system_memory():
    """Trigger comprehensive memory optimization."""
    if not master_optimizer or not master_optimizer.core:
        raise ServiceError("Core optimizer not available")
    
    try:
        memory_before = master_optimizer.core.memory.get_memory_usage()
        
        # Trigger memory optimization
        optimization_result = master_optimizer.core.memory.optimize_memory_usage()
        
        memory_after = master_optimizer.core.memory.get_memory_usage()
        
        return {
            "status": "success",
            "memory_before": memory_before,
            "memory_after": memory_after,
            "optimization_result": optimization_result,
            "memory_freed_percent": memory_before.get("percent", 0) - memory_after.get("percent", 0)
        }
        
    except Exception as e:
        logger.error("Memory optimization failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Memory optimization failed: {str(e)}")


@app.get("/admin/system/info", tags=["admin"])
@handle_exceptions
async def get_system_information():
    """Get comprehensive system information."""
    try:
        import psutil
        
        system_info = {
            "application": {
                "name": config.app_name,
                "version": config.version,
                "environment": config.environment,
                "uptime_seconds": time.time() - startup_time,
                "optimization_level": config.optimization_level.value
            },
            "system": {
                "cpu_count": os.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total_gb": psutil.virtual_memory().total / (1024**3),
                    "available_gb": psutil.virtual_memory().available / (1024**3),
                    "percent_used": psutil.virtual_memory().percent
                },
                "disk": {
                    "total_gb": psutil.disk_usage('/').total / (1024**3),
                    "free_gb": psutil.disk_usage('/').free / (1024**3),
                    "percent_used": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
                }
            },
            "features": {
                "uvloop_enabled": config.enable_uvloop,
                "json_optimization": JSON_AVAILABLE,
                "database_optimizer": DATABASE_OPTIMIZER_AVAILABLE,
                "network_optimizer": NETWORK_OPTIMIZER_AVAILABLE,
                "ml_optimizer": ML_OPTIMIZER_AVAILABLE
            }
        }
        
        # Add optimizer metrics if available
        if master_optimizer:
            try:
                system_info["optimizer_metrics"] = master_optimizer.get_comprehensive_metrics()
            except Exception as e:
                system_info["optimizer_metrics"] = {"error": str(e)}
        
        return system_info
        
    except Exception as e:
        logger.error("System info retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"System info unavailable: {str(e)}")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(OnyxBaseException)
async def onyx_exception_handler(request: Request, exc: OnyxBaseException):
    """Handle custom Onyx exceptions."""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error("Onyx exception occurred",
                correlation_id=correlation_id,
                exception_type=type(exc).__name__,
                error=str(exc))
    
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "type": type(exc).__name__,
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with comprehensive logging."""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error("Unhandled exception occurred",
                correlation_id=correlation_id,
                exception_type=type(exc).__name__,
                error=str(exc),
                path=request.url.path,
                method=request.method,
                exc_info=True)
    
    return ORJSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }
    )


# ============================================================================
# APPLICATION FACTORY AND RUNNER
# ============================================================================

def create_production_app() -> FastAPI:
    """Create production-ready application instance."""
    return app


async def run_production_server():
    """Run production server with optimal configuration."""
    server_config = uvicorn.Config(
        app=app,
        host=config.host,
        port=config.port,
        workers=1,  # Use 1 worker for async app, scale with external load balancer
        loop="uvloop" if config.enable_uvloop else "asyncio",
        http="httptools",
        log_level=config.log_level.lower(),
        access_log=config.debug,
        server_header=False,
        date_header=False,
        reload=config.debug,
        reload_dirs=["agents/backend_ads/agents/backend/onyx/server/features"] if config.debug else None
    )
    
    server = uvicorn.Server(server_config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        server.should_exit = True
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start server
    logger.info("🚀 Starting ultra-optimized production server", 
               host=config.host,
               port=config.port,
               optimization_level=config.optimization_level.value)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        raise


if __name__ == "__main__":
    try:
        if config.enable_uvloop and UVLOOP_AVAILABLE:
            uvloop.install()
        
        asyncio.run(run_production_server())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        sys.exit(1) 