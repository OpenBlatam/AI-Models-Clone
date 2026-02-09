"""
Main FastAPI application following functional patterns and best practices
"""
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import logging
import asyncio
import psutil
from datetime import datetime

from app.core.config import settings
from app.core.database import init_db, get_db
from app.core.logging import setup_logging, get_logger
from app.core.errors import handle_internal_error, handle_validation_error
from app.api.v1.router import api_router
from app.core.middleware import (
    setup_performance_middleware,
    setup_security_middleware,
    setup_monitoring_middleware
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifespan manager with proper resource management."""
    # Startup
    startup_time = time.time()
    logger.info("🚀 Starting AI Document Generator API")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized successfully")
        
        # Initialize services
        await initialize_services()
        logger.info("✅ Services initialized successfully")
        
        # Start background tasks
        background_tasks = await start_background_tasks()
        logger.info("✅ Background tasks started")
        
        startup_duration = time.time() - startup_time
        logger.info(f"🎯 Application startup completed in {startup_duration:.3f}s")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    shutdown_time = time.time()
    logger.info("🛑 Shutting down AI Document Generator API")
    
    try:
        # Stop background tasks
        await stop_background_tasks(background_tasks)
        logger.info("✅ Background tasks stopped")
        
        # Cleanup resources
        await cleanup_resources()
        logger.info("✅ Resources cleaned up")
        
        shutdown_duration = time.time() - shutdown_time
        logger.info(f"🎯 Application shutdown completed in {shutdown_duration:.3f}s")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}", exc_info=True)


def create_app() -> FastAPI:
    """Create enhanced FastAPI application with optimized configuration."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="AI-powered document generation and collaboration platform with advanced features",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
        # Performance optimizations
        generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}" if route.tags else route.name,
        # Security headers
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "filter": True,
            "tryItOutEnabled": True
        }
    )
    
    # Add enhanced middleware
    setup_enhanced_middleware(app)
    
    # Include routers with proper organization
    setup_routers(app)
    
    # Add enhanced health checks
    setup_enhanced_health_checks(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    return app


# Enhanced middleware setup functions
async def initialize_services() -> None:
    """Initialize application services."""
    try:
        # Initialize AI services
        from app.services.ai_service import initialize_ai_services
        await initialize_ai_services()
        
        # Initialize optimization services
        from app.services.adaptive_improvement_service import initialize_adaptive_improvement
        await initialize_adaptive_improvement()
        
        # Initialize predictive services
        from app.services.predictive_optimization_service import initialize_predictive_optimization
        await initialize_predictive_optimization()
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


async def start_background_tasks() -> Dict[str, asyncio.Task]:
    """Start background tasks."""
    tasks = {}
    
    try:
        # Start performance monitoring task
        tasks["performance_monitor"] = asyncio.create_task(performance_monitoring_task())
        
        # Start cleanup task
        tasks["cleanup"] = asyncio.create_task(cleanup_task())
        
        # Start optimization task
        tasks["optimization"] = asyncio.create_task(optimization_task())
        
    except Exception as e:
        logger.error(f"Failed to start background tasks: {e}")
        raise
    
    return tasks


async def stop_background_tasks(tasks: Dict[str, asyncio.Task]) -> None:
    """Stop background tasks."""
    for task_name, task in tasks.items():
        try:
            task.cancel()
            await task
        except asyncio.CancelledError:
            logger.info(f"Background task {task_name} cancelled")
        except Exception as e:
            logger.error(f"Error stopping task {task_name}: {e}")


async def cleanup_resources() -> None:
    """Cleanup application resources."""
    try:
        # Close database connections
        from app.core.database import close_db
        await close_db()
        
        # Clear caches
        from app.utils.cache import clear_all_caches
        await clear_all_caches()
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


async def performance_monitoring_task() -> None:
    """Background task for performance monitoring."""
    while True:
        try:
            # Monitor system performance
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            if cpu_percent > 80 or memory.percent > 80:
                logger.warning(f"High resource usage: CPU {cpu_percent}%, Memory {memory.percent}%")
            
            await asyncio.sleep(60)  # Check every minute
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
            await asyncio.sleep(60)


async def cleanup_task() -> None:
    """Background task for cleanup operations."""
    while True:
        try:
            # Cleanup old logs, temporary files, etc.
            await asyncio.sleep(3600)  # Run every hour
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            await asyncio.sleep(3600)


async def optimization_task() -> None:
    """Background task for system optimization."""
    while True:
        try:
            # Run optimization algorithms
            await asyncio.sleep(1800)  # Run every 30 minutes
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Optimization task error: {e}")
            await asyncio.sleep(1800)


def setup_enhanced_middleware(app: FastAPI) -> None:
    """Setup enhanced application middleware with performance and security optimizations."""
    # GZip compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # CORS middleware with enhanced configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Request-ID"],
        max_age=3600
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # Enhanced request logging middleware
    @app.middleware("http")
    async def enhanced_log_requests(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to headers
        request.state.request_id = request_id
        
        # Log request with enhanced details
        logger.info(
            f"📥 Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response with enhanced details
        process_time = time.time() - start_time
        status_emoji = "✅" if response.status_code < 400 else "❌"
        
        logger.info(
            f"📤 Response {request_id}: {status_emoji} {response.status_code} "
            f"in {process_time:.3f}s"
        )
        
        # Add enhanced headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    # Enhanced error handling middleware
    @app.middleware("http")
    async def enhanced_error_handler(request: Request, call_next):
        try:
            return await call_next(request)
        except RequestValidationError as e:
            logger.warning(f"Validation error: {e}")
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation error",
                    "details": e.errors(),
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        except HTTPException as e:
            logger.warning(f"HTTP error: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.detail,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )


def setup_routers(app: FastAPI) -> None:
    """Setup application routers with proper organization."""
    # Main API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add additional routers for specific features
    from app.api.v1.routes import (
        adaptive_improvement_routes,
        predictive_optimization_routes
    )
    
    # Include specialized routers
    app.include_router(
        adaptive_improvement_routes.router,
        prefix=f"{settings.API_V1_STR}/adaptive-improvement",
        tags=["Adaptive Improvement"]
    )
    
    app.include_router(
        predictive_optimization_routes.router,
        prefix=f"{settings.API_V1_STR}/predictive-optimization",
        tags=["Predictive Optimization"]
    )


def setup_enhanced_health_checks(app: FastAPI) -> None:
    """Setup enhanced health check endpoints."""
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - getattr(health_check, "start_time", time.time())
        }
    
    @app.get("/health/detailed", tags=["Health"])
    async def detailed_health_check():
        """Detailed health check with system metrics."""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database health
            db_healthy = await check_database_health()
            
            # Services health
            services_healthy = await check_services_health()
            
            overall_status = "healthy" if db_healthy and services_healthy else "degraded"
            
            return {
                "status": overall_status,
                "version": settings.VERSION,
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "services": {
                    "database": "healthy" if db_healthy else "unhealthy",
                    "ai_services": "healthy" if services_healthy else "unhealthy"
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @app.get("/health/ready", tags=["Health"])
    async def readiness_check():
        """Kubernetes readiness probe."""
        try:
            # Check if all critical services are ready
            db_ready = await check_database_health()
            services_ready = await check_services_health()
            
            if db_ready and services_ready:
                return {"status": "ready"}
            else:
                return JSONResponse(
                    status_code=503,
                    content={"status": "not ready"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "error": str(e)}
            )
    
    @app.get("/health/live", tags=["Health"])
    async def liveness_check():
        """Kubernetes liveness probe."""
        return {"status": "alive"}


async def check_database_health() -> bool:
    """Check database health."""
    try:
        from app.core.database import get_db
        async for db in get_db():
            # Simple query to check database connectivity
            await db.execute("SELECT 1")
            return True
    except Exception:
        return False


async def check_services_health() -> bool:
    """Check services health."""
    try:
        # Check if critical services are initialized
        from app.services.ai_service import _ai_services
        return len(_ai_services) > 0
    except Exception:
        return False


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers."""
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not found",
                "message": "The requested resource was not found",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method not allowed",
                "message": f"Method {request.method} is not allowed for this endpoint",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(429)
    async def rate_limit_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests, please try again later"
            }
        )


# Create application instance
app = create_app()

# Set start time for uptime calculation
health_check.start_time = time.time()
