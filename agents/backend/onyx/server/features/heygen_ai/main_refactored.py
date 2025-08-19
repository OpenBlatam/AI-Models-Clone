from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import structlog
from config import get_settings
from infrastructure.database import DatabaseManager
from infrastructure.cache import CacheManager
from infrastructure.external_apis import ExternalAPIManager
from presentation.api import create_api_router
from presentation.middleware import setup_middleware
from presentation.exception_handlers import setup_exception_handlers
from typing import Any, List, Dict, Optional
import logging
"""
Refactored Main Application Entry Point

Clean architecture implementation with proper separation of concerns,
dependency injection, and unified configuration management.
"""



# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our clean architecture components

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class ApplicationManager:
    """
    Manages the application lifecycle and dependencies.
    
    Coordinates startup and shutdown of all application components.
    """
    
    def __init__(self) -> Any:
        self.settings = get_settings()
        self.database_manager: DatabaseManager = None
        self.cache_manager: CacheManager = None
        self.external_api_manager: ExternalAPIManager = None
        self._shutdown_event = asyncio.Event()
    
    async def startup(self) -> None:
        """Initialize all application components."""
        logger.info(
            "Starting HeyGen AI application",
            environment=self.settings.environment,
            version=self.settings.app_version
        )
        
        try:
            # Initialize infrastructure components
            await self._initialize_database()
            await self._initialize_cache()
            await self._initialize_external_apis()
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            logger.info("Application startup completed successfully")
            
        except Exception as e:
            logger.error("Application startup failed", error=str(e), exc_info=True)
            raise
    
    async def shutdown(self) -> None:
        """Cleanup all application components."""
        logger.info("Starting application shutdown")
        
        try:
            # Shutdown components in reverse order
            if self.external_api_manager:
                await self.external_api_manager.shutdown()
            
            if self.cache_manager:
                await self.cache_manager.shutdown()
            
            if self.database_manager:
                await self.database_manager.shutdown()
            
            logger.info("Application shutdown completed successfully")
            
        except Exception as e:
            logger.error("Error during application shutdown", error=str(e), exc_info=True)
    
    async def _initialize_database(self) -> None:
        """Initialize database connection and run migrations."""
        logger.info("Initializing database")
        
        self.database_manager = DatabaseManager(self.settings.database_config)
        await self.database_manager.initialize()
        
        # Run migrations if in development
        if self.settings.is_development:
            await self.database_manager.run_migrations()
        
        logger.info("Database initialized successfully")
    
    async def _initialize_cache(self) -> None:
        """Initialize cache connections."""
        logger.info("Initializing cache")
        
        self.cache_manager = CacheManager(self.settings.redis_config)
        await self.cache_manager.initialize()
        
        logger.info("Cache initialized successfully")
    
    async async def _initialize_external_apis(self) -> None:
        """Initialize external API clients."""
        logger.info("Initializing external APIs")
        
        self.external_api_manager = ExternalAPIManager(
            openrouter_api_key=self.settings.openrouter_api_key,
            openai_api_key=self.settings.openai_api_key,
            huggingface_token=self.settings.huggingface_token
        )
        await self.external_api_manager.initialize()
        
        logger.info("External APIs initialized successfully")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum: int, frame) -> None:
            logger.info(f"Received signal {signum}, initiating shutdown")
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def get_database_session(self) -> Optional[Dict[str, Any]]:
        """Get database session dependency."""
        return self.database_manager.get_session()
    
    def get_cache_client(self) -> Optional[Dict[str, Any]]:
        """Get cache client dependency."""
        return self.cache_manager.get_client()
    
    def get_external_api_client(self, service: str):
        """Get external API client dependency."""
        return self.external_api_manager.get_client(service)


# Global application manager
app_manager: ApplicationManager = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown of all application components.
    """
    global app_manager
    
    # Startup
    app_manager = ApplicationManager()
    await app_manager.startup()
    
    # Store manager in app state for dependency injection
    app.state.app_manager = app_manager
    
    yield
    
    # Shutdown
    await app_manager.shutdown()


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns a fully configured FastAPI app with all middleware,
    exception handlers, and routes.
    """
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered video generation API with clean architecture",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None
    )
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        **settings.cors_config
    )
    
    # Setup compression
    if settings.enable_gzip:
        app.add_middleware(
            GZipMiddleware,
            minimum_size=settings.gzip_minimum_size
        )
    
    # Setup custom middleware
    setup_middleware(app, settings)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Setup API routes
    api_router = create_api_router()
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": settings.app_version
        }
    
    return app


def run_development_server() -> None:
    """Run the development server with auto-reload."""
    settings = get_settings()
    
    uvicorn.run(
        "main_refactored:create_application",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        factory=True
    )


def run_production_server() -> None:
    """Run the production server."""
    settings = get_settings()
    
    uvicorn.run(
        create_application(),
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
        access_log=True,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )


def main() -> None:
    """Main application entry point."""
    settings = get_settings()
    
    logger.info(
        "Starting HeyGen AI server",
        environment=settings.environment,
        host=settings.host,
        port=settings.port,
        version=settings.app_version
    )
    
    try:
        if settings.is_development:
            run_development_server()
        else:
            run_production_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        sys.exit(1)


# Create app instance for deployment
app = create_application()


match __name__:
    case "__main__":
    main() 