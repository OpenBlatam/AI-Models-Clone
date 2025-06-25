"""
Application Factory - Modular FastAPI Application Creation.

Centralized application factory with clean separation of concerns,
middleware configuration, and optimized production settings.
"""

import asyncio
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse

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
    JSON_AVAILABLE = False

import structlog

from ..optimizers import MasterOptimizer, create_master_optimizer
from ..monitoring import setup_sentry, comprehensive_health_check
from ..exceptions import setup_exception_handlers
from .config import AppConfig
from .middleware import setup_middleware
from .routes import register_all_routes

logger = structlog.get_logger(__name__)


class ApplicationState:
    """Global application state management."""
    
    def __init__(self):
        self.master_optimizer: Optional[MasterOptimizer] = None
        self.startup_time: float = 0
        self.config: Optional[AppConfig] = None
        self.initialized: bool = False


# Global state
app_state = ApplicationState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Optimized application lifespan with comprehensive initialization."""
    startup_start = time.time()
    
    logger.info("🚀 Starting Onyx Production Application", 
               version=app_state.config.version,
               environment=app_state.config.environment)
    
    # Setup event loop optimization
    if app_state.config.enable_uvloop and UVLOOP_AVAILABLE:
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("✅ UVLoop enabled")
        except Exception as e:
            logger.warning("⚠️ UVLoop setup failed", error=str(e))
    
    # Initialize master optimizer
    try:
        app_state.master_optimizer = create_master_optimizer(app_state.config.optimization_level)
        
        init_params = {}
        if app_state.config.database_configs.get("primary"):
            init_params["database_configs"] = {
                k: v for k, v in app_state.config.database_configs.items() if v
            }
        
        optimization_results = await app_state.master_optimizer.initialize_all(**init_params)
        
        successful = sum(1 for r in optimization_results.values() 
                        if isinstance(r, dict) and not r.get("error"))
        
        logger.info("🎯 Optimizers initialized", 
                   successful=successful, total=len(optimization_results))
        
    except Exception as e:
        logger.error("❌ Optimizer initialization failed", error=str(e))
        app_state.master_optimizer = None
    
    # Setup monitoring
    if app_state.config.sentry_dsn:
        try:
            setup_sentry(app_state.config.sentry_dsn, app_state.config.environment)
            logger.info("📊 Monitoring enabled")
        except Exception as e:
            logger.warning("⚠️ Monitoring setup failed", error=str(e))
    
    # Health check
    try:
        health_status = await comprehensive_health_check()
        healthy = sum(1 for h in health_status.values() if h.healthy)
        logger.info("🏥 Health check completed", healthy=healthy, total=len(health_status))
    except Exception as e:
        logger.error("❌ Health check failed", error=str(e))
    
    app_state.startup_time = time.time() - startup_start
    app_state.initialized = True
    
    logger.info("🎉 Application ready", startup_time=f"{app_state.startup_time:.2f}s")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application")
    
    if app_state.master_optimizer:
        try:
            await app_state.master_optimizer.cleanup_all()
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error("❌ Cleanup failed", error=str(e))


def create_application(config: AppConfig = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        config: Application configuration
        
    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = AppConfig()
    
    app_state.config = config
    
    # Create FastAPI app
    app = FastAPI(
        title=config.app_name,
        description=config.description,
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
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,
        compresslevel=6
    )
    
    # Setup custom middleware
    setup_middleware(app, config)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Register routes
    register_all_routes(app)
    
    logger.info("📦 Application created", 
               name=config.app_name,
               version=config.version,
               optimization_level=config.optimization_level.value)
    
    return app


def get_app_state() -> ApplicationState:
    """Get current application state."""
    return app_state


__all__ = ['create_application', 'get_app_state', 'ApplicationState'] 