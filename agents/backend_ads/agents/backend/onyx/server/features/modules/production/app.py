"""
Production Application Module.

Consolidated FastAPI application from all legacy production files.
"""

import time
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
import structlog

from .config import ProductionSettings
from .monitoring import setup_monitoring, ProductionMonitor
from .middleware import ProductionMiddleware
from .exceptions import setup_exception_handlers

logger = structlog.get_logger(__name__)


class ProductionApp:
    """Enterprise-grade production application."""
    
    def __init__(self, config: ProductionSettings):
        self.config = config
        self.app = None
        self.monitor = ProductionMonitor(config)
        self.startup_time = 0.0
        
    async def initialize(self, database_url: Optional[str] = None, redis_url: Optional[str] = None):
        """Initialize the production application."""
        start_time = time.time()
        
        # Setup event loop optimization
        if self.config.enable_uvloop:
            try:
                import uvloop
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                logger.info("✅ UVLoop enabled for maximum performance")
            except ImportError:
                logger.warning("⚠️ UVLoop not available")
        
        # Initialize monitoring
        await self.monitor.initialize()
        
        self.startup_time = time.time() - start_time
        logger.info("🎉 Production app initialized", startup_time=f"{self.startup_time:.2f}s")
    
    async def cleanup(self):
        """Cleanup application resources."""
        if self.monitor:
            await self.monitor.cleanup()
        logger.info("✅ Production app cleaned up")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production application lifespan management."""
    logger.info("🚀 Starting production application")
    
    # Setup optimizations
    if hasattr(app.state, 'config') and app.state.config.enable_uvloop:
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass
    
    yield
    
    logger.info("🛑 Shutting down production application")


def create_production_app(config: ProductionSettings) -> ProductionApp:
    """
    Factory function to create a production FastAPI application.
    
    Args:
        config: Production configuration
        
    Returns:
        ProductionApp: Configured application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        description=config.app_description,
        docs_url="/docs" if config.debug else None,
        redoc_url="/redoc" if config.debug else None,
        lifespan=lifespan,
        default_response_class=ORJSONResponse
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=config.cors_methods,
        allow_headers=["*"]
    )
    
    if config.enable_compression:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add production middleware
    app.add_middleware(ProductionMiddleware, config=config)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Add routes
    _setup_production_routes(app, config)
    
    # Create ProductionApp wrapper
    prod_app = ProductionApp(config)
    prod_app.app = app
    app.state.config = config
    app.state.prod_app = prod_app
    
    logger.info("Production FastAPI app created",
               level=config.production_level.value,
               environment=config.environment.value)
    
    return prod_app


def _setup_production_routes(app: FastAPI, config: ProductionSettings):
    """Setup production API routes."""
    
    @app.get("/health")
    async def health_check():
        """Production health check."""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": config.app_version,
            "environment": config.environment.value
        }
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        try:
            from prometheus_client import generate_latest
            return generate_latest()
        except ImportError:
            raise HTTPException(status_code=503, detail="Metrics not available")
    
    @app.get("/api/status")
    async def production_status():
        """Comprehensive production status."""
        return {
            "application": {
                "name": config.app_name,
                "version": config.app_version,
                "environment": config.environment.value,
                "production_level": config.production_level.value
            },
            "configuration": {
                "workers": config.workers,
                "max_connections": config.max_connections,
                "features_enabled": len([k for k, v in config.get_enabled_features().items() if v])
            },
            "performance": config.get_performance_config()
        }
    
    @app.post("/api/optimize/benchmark")
    async def production_benchmark(iterations: int = 1000):
        """Production performance benchmark."""
        start_time = time.perf_counter()
        
        # Simulate work
        for i in range(iterations):
            pass
        
        duration = (time.perf_counter() - start_time) * 1000
        
        return {
            "iterations": iterations,
            "duration_ms": duration,
            "ops_per_second": iterations / (duration / 1000),
            "level": config.production_level.value
        }


# Export main components
__all__ = [
    "ProductionApp",
    "create_production_app",
    "lifespan"
] 