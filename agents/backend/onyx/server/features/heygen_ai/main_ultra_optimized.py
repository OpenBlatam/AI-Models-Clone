#!/usr/bin/env python3
"""
Ultra-Optimized HeyGen AI FastAPI Main Entry Point
Enhanced performance with advanced optimizations, connection pooling, and resource management.
"""

import asyncio
import os
import signal
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
import uvicorn
from fastapi import FastAPI

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# Optimized Constants
# =============================================================================

class AppConstants:
    """Application constants with optimized values."""
    MAX_CONNECTIONS = 1000
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 60
    BUFFER_SIZE = 8192  # Increased for better performance
    DEFAULT_CACHE_TTL = 300
    MAX_CONCURRENT_REQUESTS = 1000
    WORKER_TIMEOUT = 30
    GRACEFUL_SHUTDOWN_TIMEOUT = 30

# =============================================================================
# Enhanced Logging Configuration
# =============================================================================

def configure_optimized_logging() -> structlog.BoundLogger:
    """Configure structured logging with performance optimizations."""
    try:
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
        return structlog.get_logger()
    except Exception:
        # Fallback to basic logging
        import logging
        logging.basicConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return structlog.wrap_logger(logging.getLogger("heygen_ai"))

logger = configure_optimized_logging()

# =============================================================================
# Ultra-Optimized Environment Configuration
# =============================================================================

class UltraOptimizedEnvironmentConfig:
    """Ultra-optimized environment configuration with intelligent caching."""
    
    _cache: Dict[str, Any] = {}
    _cache_timestamps: Dict[str, float] = {}
    _cache_ttl = 300  # 5 minutes cache TTL
    
    @classmethod
    def _is_cache_valid(cls, key: str) -> bool:
        """Check if cached value is still valid."""
        if key not in cls._cache_timestamps:
            return False
        return (datetime.now().timestamp() - cls._cache_timestamps[key]) < cls._cache_ttl
    
    @classmethod
    def get_env(cls, key: str, default: Optional[str] = None, cast_type: type = str) -> Any:
        """Get environment variable with intelligent caching and type casting."""
        if key in cls._cache and cls._is_cache_valid(key):
            return cls._cache[key]
        
        value = os.getenv(key, default)
        
        # Type casting with error handling
        try:
            if cast_type == int:
                result = int(value) if value else default
            elif cast_type == bool:
                result = value.lower() == "true" if value else default
            elif cast_type == float:
                result = float(value) if value else default
            else:
                result = value
        except (ValueError, TypeError):
            logger.warning(f"Failed to cast {key} to {cast_type.__name__}, using default", 
                         key=key, value=value, default=default)
            result = default
        
        # Cache the result
        cls._cache[key] = result
        cls._cache_timestamps[key] = datetime.now().timestamp()
        
        return result
    
    @classmethod
    def get_environment(cls) -> str:
        return cls.get_env("ENVIRONMENT", "development").lower()
    
    @classmethod
    def get_host(cls) -> str:
        return cls.get_env("HOST", "0.0.0.0")
    
    @classmethod
    def get_port(cls) -> int:
        return cls.get_env("PORT", "8000", int)
    
    @classmethod
    def get_workers(cls) -> int:
        return cls.get_env("WORKERS", "1", int)
    
    @classmethod
    def get_log_level(cls) -> str:
        return cls.get_env("LOG_LEVEL", "info").lower()
    
    @classmethod
    def get_reload(cls) -> bool:
        return cls.get_env("RELOAD", "false", bool)
    
    @classmethod
    def get_redis_url(cls) -> Optional[str]:
        return cls.get_env("REDIS_URL", None)
    
    @classmethod
    def get_database_url(cls) -> str:
        return cls.get_env("DATABASE_URL", "sqlite+aiosqlite:///./heygen_ai.db")
    
    @classmethod
    def get_optimization_level(cls) -> str:
        return cls.get_env("OPTIMIZATION_LEVEL", "ultra").lower()

# =============================================================================
# Ultra-Optimized Application Manager
# =============================================================================

class UltraOptimizedApplicationManager:
    """Ultra-optimized application lifecycle manager."""
    
    def __init__(self) -> None:
        self.app: Optional[FastAPI] = None
        self.startup_time: Optional[datetime] = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize_optimizations(self) -> None:
        """Initialize ultra-optimized performance features."""
        try:
            # Import here to avoid circular imports
            from api.optimization.performance_optimizer import PerformanceOptimizer
            from api.optimization.connection_pooling import ConnectionPoolManager
            
            # Initialize connection pool manager with optimized settings
            connection_pool_manager = ConnectionPoolManager(
                database_url=UltraOptimizedEnvironmentConfig.get_database_url(),
                redis_url=UltraOptimizedEnvironmentConfig.get_redis_url(),
                max_connections=UltraOptimizedEnvironmentConfig.get_env("MAX_DB_CONNECTIONS", "100", int),
                pool_timeout=UltraOptimizedEnvironmentConfig.get_env("POOL_TIMEOUT", "30", int)
            )
            await connection_pool_manager.initialize()
            
            # Initialize performance optimizer
            performance_optimizer = PerformanceOptimizer(
                redis_url=UltraOptimizedEnvironmentConfig.get_redis_url(),
                database_url=UltraOptimizedEnvironmentConfig.get_database_url(),
                optimization_level="ultra",
                memory_cache_size=UltraOptimizedEnvironmentConfig.get_env("MEMORY_CACHE_SIZE", "2000", int),
                database_pool_size=UltraOptimizedEnvironmentConfig.get_env("DB_POOL_SIZE", "50", int)
            )
            
            logger.info("Ultra-optimized performance features initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize ultra-optimizations", error=str(e), exc_info=True)
            # Continue without optimizations rather than failing
    
    def configure_application(self) -> FastAPI:
        """Configure FastAPI application with ultra-optimizations."""
        environment = UltraOptimizedEnvironmentConfig.get_environment()
        
        try:
            # Import here to avoid circular imports
            from api.routes.__main__ import create_app, create_development_app, create_production_app
            
            if environment == "production":
                self.app = create_production_app()
            elif environment == "development":
                self.app = create_development_app()
            else:
                self.app = create_app()
            
            # Add ultra-optimized middleware
            if self.app:
                self._add_ultra_optimized_middleware()
            
            return self.app
            
        except ImportError as e:
            logger.warning(f"Could not import route modules: {e}")
            # Create a basic FastAPI app as fallback
            self.app = FastAPI(
                title="HeyGen AI Ultra-Optimized",
                description="Ultra-optimized HeyGen AI API",
                version="2.0.0"
            )
            return self.app
    
    def _add_ultra_optimized_middleware(self) -> None:
        """Add ultra-optimized middleware to the application."""
        try:
            import redis.asyncio as redis
            from api.middleware.performance_middleware import create_performance_middleware
            
            redis_client = None
            if UltraOptimizedEnvironmentConfig.get_redis_url():
                redis_client = redis.from_url(UltraOptimizedEnvironmentConfig.get_redis_url())
            
            performance_middleware = create_performance_middleware(
                redis_client=redis_client,
                enable_caching=True,
                enable_compression=True,
                enable_rate_limiting=True,
                enable_metrics=True,
                cache_ttl=UltraOptimizedEnvironmentConfig.get_env("CACHE_TTL", "300", int),
                slow_request_threshold_ms=UltraOptimizedEnvironmentConfig.get_env("SLOW_REQUEST_THRESHOLD", "500", float),
                exclude_paths=["/health", "/metrics", "/docs", "/openapi.json"],
                exclude_methods=["OPTIONS"]
            )
            
            self.app.add_middleware(performance_middleware.__class__, **{
                k: v for k, v in performance_middleware.__dict__.items() 
                if not k.startswith('_')
            })
            
        except Exception as e:
            logger.warning(f"Could not add ultra-optimized middleware: {e}")
    
    async def startup(self) -> None:
        """Ultra-optimized application startup."""
        self.startup_time = datetime.now(timezone.utc)
        await self.initialize_optimizations()
        logger.info("Ultra-optimized application startup completed", 
                   startup_time=self.startup_time.isoformat())
    
    async def shutdown(self) -> None:
        """Ultra-optimized application shutdown with cleanup."""
        try:
            self._shutdown_event.set()
            
            # Log final statistics
            uptime = (datetime.now(timezone.utc) - self.startup_time).total_seconds() if self.startup_time else 0
            logger.info("Ultra-optimized application shutdown completed", uptime_seconds=uptime)
            
        except Exception as e:
            logger.error("Error during ultra-optimized shutdown", error=str(e), exc_info=True)
    
    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()

# =============================================================================
# Ultra-Optimized Server Configuration
# =============================================================================

def get_ultra_optimized_server_config() -> Dict[str, Any]:
    """Get ultra-optimized server configuration."""
    return {
        "host": UltraOptimizedEnvironmentConfig.get_host(),
        "port": UltraOptimizedEnvironmentConfig.get_port(),
        "workers": UltraOptimizedEnvironmentConfig.get_workers(),
        "log_level": UltraOptimizedEnvironmentConfig.get_log_level(),
        "reload": UltraOptimizedEnvironmentConfig.get_reload(),
        "access_log": True,
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
        "timeout_keep_alive": AppConstants.WORKER_TIMEOUT,
        "timeout_graceful_shutdown": AppConstants.GRACEFUL_SHUTDOWN_TIMEOUT,
        "limit_concurrency": AppConstants.MAX_CONCURRENT_REQUESTS,
        "limit_max_requests": UltraOptimizedEnvironmentConfig.get_env("MAX_REQUESTS_PER_WORKER", "20000", int),
        "backlog": UltraOptimizedEnvironmentConfig.get_env("BACKLOG_SIZE", "4096", int),
        "loop": "asyncio",
        "http": "httptools",
        "ws": "websockets",
        "use_colors": False,  # Disable colors for better performance
        "date_header": False,  # Disable date header for better performance
    }

# =============================================================================
# Signal Handlers
# =============================================================================

def setup_ultra_optimized_signal_handlers(app_manager: UltraOptimizedApplicationManager) -> None:
    """Setup ultra-optimized graceful shutdown signal handlers."""
    
    def signal_handler(signum: int, frame: Any) -> None:
        logger.info(f"Received signal {signum}, initiating ultra-optimized graceful shutdown")
        asyncio.create_task(app_manager.shutdown())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

# =============================================================================
# Ultra-Optimized Main Function
# =============================================================================

async def ultra_optimized_main() -> None:
    """Ultra-optimized main entrypoint for HeyGen AI FastAPI server."""
    app_manager = UltraOptimizedApplicationManager()
    
    try:
        # Setup signal handlers
        setup_ultra_optimized_signal_handlers(app_manager)
        
        # Startup
        await app_manager.startup()
        
        # Configure application
        app = app_manager.configure_application()
        
        # Get server configuration
        server_config = get_ultra_optimized_server_config()
        
        logger.info(
            "Starting ultra-optimized HeyGen AI FastAPI server",
            extra={
                "environment": UltraOptimizedEnvironmentConfig.get_environment(),
                "host": UltraOptimizedEnvironmentConfig.get_host(),
                "port": UltraOptimizedEnvironmentConfig.get_port(),
                "workers": UltraOptimizedEnvironmentConfig.get_workers(),
                "log_level": UltraOptimizedEnvironmentConfig.get_log_level(),
                "reload": UltraOptimizedEnvironmentConfig.get_reload(),
                "optimization_level": UltraOptimizedEnvironmentConfig.get_optimization_level(),
                "redis_enabled": bool(UltraOptimizedEnvironmentConfig.get_redis_url()),
                "max_concurrent_requests": server_config.get("limit_concurrency"),
                "max_requests_per_worker": server_config.get("limit_max_requests"),
                "backlog_size": server_config.get("backlog")
            }
        )
        
        # Start server
        config = uvicorn.Config(app, **server_config)
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Ultra-optimized server stopped by user")
    except Exception as e:
        logger.error("Ultra-optimized server error", exc_info=True)
        sys.exit(1)
    finally:
        await app_manager.shutdown()

# =============================================================================
# Application Instance
# =============================================================================

app_manager = UltraOptimizedApplicationManager()
app = app_manager.configure_application()

# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    asyncio.run(ultra_optimized_main())
