"""
🚀 ULTRA-EXTREME V4 - MAIN APPLICATION
======================================

Ultra-extreme main application with:
- FastAPI integration
- Dependency injection
- Service orchestration
- Performance monitoring
- Health checks
- API documentation
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog
from prometheus_client import make_asgi_app

# Import our ultra-extreme modules
from .core.config.settings import settings, get_settings
from .core.exceptions.base import UltraExtremeException, handle_exception
from .core.interfaces.repositories import RepositoryFactory
from .core.interfaces.cache import CacheFactory
from .core.interfaces.monitoring import PerformanceMonitor

# Import domain entities
from .domain.entities.content import UltraContent
from .domain.entities.optimization import UltraOptimization
from .domain.entities.ai import UltraAI

# Import application use cases
from .application.use_cases.content.generate_content import GenerateContentUseCase
from .application.use_cases.content.optimize_content import OptimizeContentUseCase
from .application.use_cases.content.analyze_content import AnalyzeContentUseCase
from .application.use_cases.optimization.optimize_system import OptimizeSystemUseCase
from .application.use_cases.optimization.optimize_performance import OptimizePerformanceUseCase
from .application.use_cases.optimization.optimize_cache import OptimizeCacheUseCase
from .application.use_cases.ai.generate_ai import GenerateAIUseCase
from .application.use_cases.ai.optimize_ai import OptimizeAIUseCase
from .application.use_cases.ai.analyze_ai import AnalyzeAIUseCase

# Import infrastructure services
from .infrastructure.database.repositories.content_repository import PostgreSQLContentRepository
from .infrastructure.database.repositories.optimization_repository import PostgreSQLOptimizationRepository
from .infrastructure.database.repositories.ai_repository import PostgreSQLAIRepository
from .infrastructure.cache.redis_cache import RedisCacheService
from .infrastructure.cache.memory_cache import MemoryCacheService
from .infrastructure.cache.disk_cache import DiskCacheService
from .infrastructure.cache.predictive_cache import PredictiveCacheService
from .infrastructure.external.openai_service import OpenAIService
from .infrastructure.external.anthropic_service import AnthropicService
from .infrastructure.external.huggingface_service import HuggingFaceService
from .infrastructure.monitoring.prometheus_monitor import PrometheusPerformanceMonitor
from .infrastructure.monitoring.sentry_monitor import SentryMonitor
from .infrastructure.monitoring.health_checker import HealthChecker
from .infrastructure.messaging.event_publisher import EventPublisher
from .infrastructure.messaging.event_subscriber import EventSubscriber
from .infrastructure.messaging.message_queue import MessageQueue
from .infrastructure.ai.openai_service import OpenAIUltraService
from .infrastructure.ai.anthropic_service import AnthropicUltraService
from .infrastructure.ai.huggingface_service import HuggingFaceUltraService
from .infrastructure.ai.local_ai_service import LocalAIUltraService

# Import presentation layer
from .presentation.api.v1.content_routes import content_router
from .presentation.api.v1.optimization_routes import optimization_router
from .presentation.api.v1.ai_routes import ai_router
from .presentation.api.health_routes import health_router
from .presentation.middleware.auth_middleware import AuthMiddleware
from .presentation.middleware.rate_limit_middleware import RateLimitMiddleware
from .presentation.middleware.logging_middleware import LoggingMiddleware
from .presentation.middleware.monitoring_middleware import MonitoringMiddleware

# Import shared utilities
from .shared.decorators.performance_decorator import performance_monitor
from .shared.decorators.cache_decorator import cache_result
from .shared.decorators.monitoring_decorator import monitor_function


class UltraExtremeApp:
    """Ultra-extreme application class"""
    
    def __init__(self):
        self.settings = get_settings()
        self.app = None
        self.repository_factory = RepositoryFactory()
        self.cache_factory = CacheFactory()
        self.performance_monitor = None
        self.health_checker = None
        self.event_publisher = None
        self.message_queue = None
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize services
        self._initialize_services()
        
        # Create FastAPI app
        self._create_fastapi_app()
    
    def _setup_logging(self):
        """Setup structured logging"""
        logging_config = self.settings.get_logging_config()
        
        if logging_config["structured"]:
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
        
        # Set log level
        logging.basicConfig(
            level=getattr(logging, logging_config["level"]),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" if not logging_config["structured"] else None,
            handlers=[
                logging.FileHandler(logging_config["file"]) if logging_config["file"] else logging.StreamHandler()
            ]
        )
        
        self.logger = structlog.get_logger(__name__)
        self.logger.info("Logging configured successfully")
    
    def _initialize_services(self):
        """Initialize all services"""
        self.logger.info("Initializing ultra-extreme services")
        
        # Initialize cache services
        self._initialize_cache_services()
        
        # Initialize database repositories
        self._initialize_repositories()
        
        # Initialize external services
        self._initialize_external_services()
        
        # Initialize monitoring services
        self._initialize_monitoring_services()
        
        # Initialize messaging services
        self._initialize_messaging_services()
        
        # Initialize AI services
        self._initialize_ai_services()
        
        self.logger.info("All services initialized successfully")
    
    def _initialize_cache_services(self):
        """Initialize cache services"""
        self.logger.info("Initializing cache services")
        
        # Create individual cache services
        memory_cache = MemoryCacheService(
            max_size=self.settings.MEMORY_CACHE_SIZE,
            ttl=self.settings.MEMORY_CACHE_TTL
        )
        
        redis_cache = RedisCacheService(
            redis_url=self.settings.REDIS_URL,
            pool_size=self.settings.REDIS_POOL_SIZE,
            max_connections=self.settings.REDIS_MAX_CONNECTIONS,
            timeout=self.settings.REDIS_TIMEOUT
        )
        
        disk_cache = DiskCacheService(
            cache_dir=self.settings.DISK_CACHE_DIR,
            max_size=self.settings.DISK_CACHE_SIZE
        ) if self.settings.DISK_CACHE_ENABLED else None
        
        # Register cache services
        self.cache_factory.register_cache("memory", memory_cache)
        self.cache_factory.register_cache("redis", redis_cache)
        if disk_cache:
            self.cache_factory.register_cache("disk", disk_cache)
        
        # Create multi-level cache
        caches = {
            "memory": memory_cache,
            "redis": redis_cache,
        }
        if disk_cache:
            caches["disk"] = disk_cache
        
        multi_level_cache = self.cache_factory.create_multi_level_cache(caches)
        self.cache_factory.register_cache("multi_level", multi_level_cache)
        
        # Create predictive cache
        predictive_cache = self.cache_factory.create_predictive_cache(multi_level_cache)
        self.cache_factory.register_cache("predictive", predictive_cache)
        
        self.logger.info("Cache services initialized successfully")
    
    def _initialize_repositories(self):
        """Initialize database repositories"""
        self.logger.info("Initializing database repositories")
        
        # Get cache service for repositories
        cache_service = self.cache_factory.get_cache("multi_level")
        
        # Create repositories
        content_repository = PostgreSQLContentRepository(
            database_url=self.settings.DATABASE_URL,
            cache_service=cache_service
        )
        
        optimization_repository = PostgreSQLOptimizationRepository(
            database_url=self.settings.DATABASE_URL,
            cache_service=cache_service
        )
        
        ai_repository = PostgreSQLAIRepository(
            database_url=self.settings.DATABASE_URL,
            cache_service=cache_service
        )
        
        # Register repositories
        self.repository_factory.register_repository("content", content_repository)
        self.repository_factory.register_repository("optimization", optimization_repository)
        self.repository_factory.register_repository("ai", ai_repository)
        
        self.logger.info("Database repositories initialized successfully")
    
    def _initialize_external_services(self):
        """Initialize external services"""
        self.logger.info("Initializing external services")
        
        # OpenAI service
        openai_service = OpenAIService(
            api_key=self.settings.OPENAI_API_KEY.get_secret_value(),
            model=self.settings.OPENAI_MODEL,
            max_tokens=self.settings.OPENAI_MAX_TOKENS,
            temperature=self.settings.OPENAI_TEMPERATURE,
            timeout=self.settings.OPENAI_TIMEOUT
        )
        
        # Anthropic service (if configured)
        anthropic_service = None
        if self.settings.ANTHROPIC_API_KEY:
            anthropic_service = AnthropicService(
                api_key=self.settings.ANTHROPIC_API_KEY.get_secret_value(),
                model=self.settings.ANTHROPIC_MODEL,
                max_tokens=self.settings.ANTHROPIC_MAX_TOKENS,
                temperature=self.settings.ANTHROPIC_TEMPERATURE,
                timeout=self.settings.ANTHROPIC_TIMEOUT
            )
        
        # HuggingFace service (if configured)
        huggingface_service = None
        if self.settings.HUGGINGFACE_TOKEN:
            huggingface_service = HuggingFaceService(
                token=self.settings.HUGGINGFACE_TOKEN.get_secret_value(),
                model=self.settings.HUGGINGFACE_MODEL,
                cache_dir=self.settings.HUGGINGFACE_CACHE_DIR,
                timeout=self.settings.HUGGINGFACE_TIMEOUT
            )
        
        # Store services for later use
        self.openai_service = openai_service
        self.anthropic_service = anthropic_service
        self.huggingface_service = huggingface_service
        
        self.logger.info("External services initialized successfully")
    
    def _initialize_monitoring_services(self):
        """Initialize monitoring services"""
        self.logger.info("Initializing monitoring services")
        
        # Prometheus monitor
        self.performance_monitor = PrometheusPerformanceMonitor()
        
        # Sentry monitor (if configured)
        self.sentry_monitor = None
        if self.settings.SENTRY_DSN:
            self.sentry_monitor = SentryMonitor(
                dsn=self.settings.SENTRY_DSN,
                environment=self.settings.SENTRY_ENVIRONMENT,
                traces_sample_rate=self.settings.SENTRY_TRACES_SAMPLE_RATE
            )
        
        # Health checker
        self.health_checker = HealthChecker(
            enabled=self.settings.HEALTH_CHECK_ENABLED,
            interval=self.settings.HEALTH_CHECK_INTERVAL,
            timeout=self.settings.HEALTH_CHECK_TIMEOUT
        )
        
        self.logger.info("Monitoring services initialized successfully")
    
    def _initialize_messaging_services(self):
        """Initialize messaging services"""
        self.logger.info("Initializing messaging services")
        
        # Event publisher
        self.event_publisher = EventPublisher()
        
        # Event subscriber
        self.event_subscriber = EventSubscriber()
        
        # Message queue
        self.message_queue = MessageQueue()
        
        self.logger.info("Messaging services initialized successfully")
    
    def _initialize_ai_services(self):
        """Initialize AI services"""
        self.logger.info("Initializing AI services")
        
        # OpenAI ultra service
        self.openai_ultra_service = OpenAIUltraService(
            openai_service=self.openai_service,
            cache_service=self.cache_factory.get_cache("predictive")
        )
        
        # Anthropic ultra service (if available)
        self.anthropic_ultra_service = None
        if self.anthropic_service:
            self.anthropic_ultra_service = AnthropicUltraService(
                anthropic_service=self.anthropic_service,
                cache_service=self.cache_factory.get_cache("predictive")
            )
        
        # HuggingFace ultra service (if available)
        self.huggingface_ultra_service = None
        if self.huggingface_service:
            self.huggingface_ultra_service = HuggingFaceUltraService(
                huggingface_service=self.huggingface_service,
                cache_service=self.cache_factory.get_cache("predictive")
            )
        
        # Local AI service (if enabled)
        self.local_ai_service = None
        if self.settings.LOCAL_AI_ENABLED:
            self.local_ai_service = LocalAIUltraService(
                model_path=self.settings.LOCAL_AI_MODEL_PATH,
                device=self.settings.LOCAL_AI_DEVICE,
                batch_size=self.settings.LOCAL_AI_BATCH_SIZE,
                cache_service=self.cache_factory.get_cache("predictive")
            )
        
        self.logger.info("AI services initialized successfully")
    
    def _create_fastapi_app(self):
        """Create FastAPI application"""
        self.logger.info("Creating FastAPI application")
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info("Starting ultra-extreme application")
            
            # Start health checker
            if self.health_checker:
                await self.health_checker.start()
            
            # Start performance monitoring
            if self.performance_monitor:
                await self.performance_monitor.start()
            
            yield
            
            # Shutdown
            self.logger.info("Shutting down ultra-extreme application")
            
            # Stop health checker
            if self.health_checker:
                await self.health_checker.stop()
            
            # Stop performance monitoring
            if self.performance_monitor:
                await self.performance_monitor.stop()
        
        # Create FastAPI app
        self.app = FastAPI(
            title=self.settings.APP_NAME,
            description=self.settings.APP_DESCRIPTION,
            version=self.settings.APP_VERSION,
            debug=self.settings.DEBUG,
            lifespan=lifespan
        )
        
        # Add middleware
        self._add_middleware()
        
        # Add exception handlers
        self._add_exception_handlers()
        
        # Add routes
        self._add_routes()
        
        # Add Prometheus metrics
        if self.settings.PROMETHEUS_ENABLED:
            metrics_app = make_asgi_app()
            self.app.mount("/metrics", metrics_app)
        
        self.logger.info("FastAPI application created successfully")
    
    def _add_middleware(self):
        """Add middleware to FastAPI app"""
        # CORS middleware
        if self.settings.CORS_ENABLED:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.settings.CORS_ORIGINS,
                allow_credentials=True,
                allow_methods=self.settings.CORS_METHODS,
                allow_headers=self.settings.CORS_HEADERS,
            )
        
        # Gzip middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Custom middleware
        self.app.add_middleware(LoggingMiddleware)
        self.app.add_middleware(MonitoringMiddleware)
        
        if self.settings.RATE_LIMIT_ENABLED:
            self.app.add_middleware(RateLimitMiddleware)
        
        if self.settings.AUTH_ENABLED:
            self.app.add_middleware(AuthMiddleware)
    
    def _add_exception_handlers(self):
        """Add exception handlers to FastAPI app"""
        
        @self.app.exception_handler(UltraExtremeException)
        async def ultra_extreme_exception_handler(request: Request, exc: UltraExtremeException):
            """Handle ultra-extreme exceptions"""
            self.logger.error(
                "Ultra-extreme exception occurred",
                error_code=exc.error_code,
                message=exc.message,
                category=exc.category.value,
                severity=exc.severity.value
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": exc.error_code,
                        "message": exc.message,
                        "category": exc.category.value,
                        "retryable": exc.retryable
                    }
                }
            )
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Handle validation exceptions"""
            self.logger.error("Validation error", errors=exc.errors())
            
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request validation failed",
                        "details": exc.errors()
                    }
                }
            )
        
        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            """Handle HTTP exceptions"""
            self.logger.error("HTTP exception", status_code=exc.status_code, detail=exc.detail)
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": f"HTTP_{exc.status_code}",
                        "message": exc.detail
                    }
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions"""
            self.logger.error("Unexpected error", error=str(exc), exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred"
                    }
                }
            )
    
    def _add_routes(self):
        """Add routes to FastAPI app"""
        # Include routers
        self.app.include_router(health_router, prefix="/health", tags=["health"])
        self.app.include_router(content_router, prefix="/api/v1/content", tags=["content"])
        self.app.include_router(optimization_router, prefix="/api/v1/optimization", tags=["optimization"])
        self.app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
        
        # Root endpoint
        @self.app.get("/", tags=["root"])
        async def root():
            """Root endpoint"""
            return {
                "name": self.settings.APP_NAME,
                "version": self.settings.APP_VERSION,
                "description": self.settings.APP_DESCRIPTION,
                "status": "running",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def start(self):
        """Start the application"""
        self.logger.info("Starting ultra-extreme application")
        
        # Start background tasks
        await self._start_background_tasks()
        
        # Start the server
        config = uvicorn.Config(
            app=self.app,
            host=self.settings.HOST,
            port=self.settings.PORT,
            workers=self.settings.WORKERS,
            log_level=self.settings.LOG_LEVEL.lower(),
            access_log=True,
            use_colors=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def _start_background_tasks(self):
        """Start background tasks"""
        self.logger.info("Starting background tasks")
        
        # Start health monitoring
        if self.health_checker:
            asyncio.create_task(self.health_checker.run())
        
        # Start performance monitoring
        if self.performance_monitor:
            asyncio.create_task(self.performance_monitor.run())
        
        # Start event processing
        if self.event_subscriber:
            asyncio.create_task(self.event_subscriber.run())
        
        # Start message queue processing
        if self.message_queue:
            asyncio.create_task(self.message_queue.run())
        
        self.logger.info("Background tasks started successfully")
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application"""
        return self.app


# Global application instance
app_instance = None


def get_app() -> FastAPI:
    """Get the FastAPI application instance"""
    global app_instance
    if app_instance is None:
        app_instance = UltraExtremeApp()
    return app_instance.get_app()


# For direct execution
if __name__ == "__main__":
    # Create and start the application
    ultra_app = UltraExtremeApp()
    
    try:
        asyncio.run(ultra_app.start())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1) 