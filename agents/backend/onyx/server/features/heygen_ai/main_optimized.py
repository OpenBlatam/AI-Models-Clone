from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import os
import sys
import asyncio
import signal
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime, timezone
    from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
import structlog
from api.routes.__main__ import create_app, create_development_app, create_production_app
from api.optimization.performance_optimizer import PerformanceOptimizer, OptimizationLevel
from api.optimization.connection_pooling import ConnectionPoolManager
from api.middleware.performance_middleware import create_performance_middleware
        import logging
                import redis.asyncio as redis
from typing import Any, List, Dict, Optional
#!/usr/bin/env python3
"""
Optimized HeyGen AI FastAPI Main Entry Point
Enhanced performance with connection pooling, async optimizations, and resource management.
"""


try:
    load_dotenv()
except ImportError:
    pass


# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# =============================================================================
# Enhanced Logging Configuration
# =============================================================================
def configure_logging():
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
        logging.basicConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("heygen_ai")

logger = configure_logging()

# =============================================================================
# Optimized Environment Configuration
# =============================================================================
class EnvironmentConfig:
    """Optimized environment configuration with caching."""
    
    _cache: Dict[str, Any] = {}
    
    @classmethod
    def get_env(cls, key: str, default: Optional[str] = None, cast_type: type = str) -> Optional[Dict[str, Any]]:
        """Get environment variable with caching and type casting."""
        if key not in cls._cache:
            value = os.getenv(key, default)
            match cast_type:
    case int:
                cls._cache[key] = int(value) if value else default
            elmatch cast_type:
    case bool:
                cls._cache[key] = value.lower() == "true" if value else default
            else:
                cls._cache[key] = value
        return cls._cache[key]
    
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
    def get_optimization_level(cls) -> OptimizationLevel:
        level = cls.get_env("OPTIMIZATION_LEVEL", "standard").lower()
        return OptimizationLevel(level)

# =============================================================================
# Optimized Application Configuration
# =============================================================================
class OptimizedApplicationManager:
    """Manages application lifecycle with performance optimizations."""
    
    def __init__(self) -> Any:
        self.app: Optional[FastAPI] = None
        self.performance_optimizer: Optional[PerformanceOptimizer] = None
        self.connection_pool_manager: Optional[ConnectionPoolManager] = None
        self.startup_time: Optional[datetime] = None
    
    async def initialize_optimizations(self) -> Any:
        """Initialize performance optimizations."""
        try:
            # Initialize connection pool manager
            self.connection_pool_manager = ConnectionPoolManager(
                database_url=EnvironmentConfig.get_database_url(),
                redis_url=EnvironmentConfig.get_redis_url(),
                max_connections=EnvironmentConfig.get_env("MAX_DB_CONNECTIONS", "50", int),
                pool_timeout=EnvironmentConfig.get_env("POOL_TIMEOUT", "30", int)
            )
            await self.connection_pool_manager.initialize()
            
            # Initialize performance optimizer
            self.performance_optimizer = PerformanceOptimizer(
                redis_url=EnvironmentConfig.get_redis_url(),
                database_url=EnvironmentConfig.get_database_url(),
                optimization_level=EnvironmentConfig.get_optimization_level(),
                memory_cache_size=EnvironmentConfig.get_env("MEMORY_CACHE_SIZE", "1000", int),
                database_pool_size=EnvironmentConfig.get_env("DB_POOL_SIZE", "20", int)
            )
            
            logger.info("Performance optimizations initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize optimizations", error=str(e))
            raise
    
    def configure_application(self) -> FastAPI:
        """Configure FastAPI application with optimizations."""
        environment = EnvironmentConfig.get_environment()
        
        if environment == "production":
            self.app = create_production_app()
        elif environment == "development":
            self.app = create_development_app()
        else:
            self.app = create_app()
        
        # Add performance middleware
        if self.app:
            redis_client = None
            if EnvironmentConfig.get_redis_url():
                redis_client = redis.from_url(EnvironmentConfig.get_redis_url())
            
            performance_middleware = create_performance_middleware(
                redis_client=redis_client,
                enable_caching=True,
                enable_compression=True,
                enable_rate_limiting=True,
                enable_metrics=True,
                cache_ttl=EnvironmentConfig.get_env("CACHE_TTL", "300", int),
                slow_request_threshold_ms=EnvironmentConfig.get_env("SLOW_REQUEST_THRESHOLD", "1000", float),
                exclude_paths=["/health", "/metrics", "/docs", "/openapi.json"],
                exclude_methods=["OPTIONS"]
            )
            
            self.app.add_middleware(performance_middleware.__class__, **{
                k: v for k, v in performance_middleware.__dict__.items() 
                if not k.startswith('_')
            })
        
        return self.app
    
    async def startup(self) -> Any:
        """Application startup with optimizations."""
        self.startup_time = datetime.now(timezone.utc)
        await self.initialize_optimizations()
        logger.info("Application startup completed", startup_time=self.startup_time.isoformat())
    
    async def shutdown(self) -> Any:
        """Application shutdown with cleanup."""
        try:
            if self.connection_pool_manager:
                await self.connection_pool_manager.close()
            
            if self.performance_optimizer:
                # Log final performance statistics
                stats = self.performance_optimizer.get_performance_report()
                logger.info("Final performance statistics", stats=stats)
            
            uptime = (datetime.now(timezone.utc) - self.startup_time).total_seconds() if self.startup_time else 0
            logger.info("Application shutdown completed", uptime_seconds=uptime)
            
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))

# =============================================================================
# Optimized Server Configuration
# =============================================================================
def get_optimized_server_config() -> Dict[str, Any]:
    """Get optimized server configuration."""
    return {
        "host": EnvironmentConfig.get_host(),
        "port": EnvironmentConfig.get_port(),
        "workers": EnvironmentConfig.get_workers(),
        "log_level": EnvironmentConfig.get_log_level(),
        "reload": EnvironmentConfig.get_reload(),
        "access_log": True,
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
        "timeout_keep_alive": EnvironmentConfig.get_env("KEEP_ALIVE_TIMEOUT", "30", int),
        "timeout_graceful_shutdown": EnvironmentConfig.get_env("GRACEFUL_SHUTDOWN_TIMEOUT", "30", int),
        "limit_concurrency": EnvironmentConfig.get_env("MAX_CONCURRENT_REQUESTS", "1000", int),
        "limit_max_requests": EnvironmentConfig.get_env("MAX_REQUESTS_PER_WORKER", "10000", int),
        "backlog": EnvironmentConfig.get_env("BACKLOG_SIZE", "2048", int),
        "loop": "asyncio",
        "http": "httptools",
        "ws": "websockets"
    }

# =============================================================================
# Signal Handlers
# =============================================================================
def setup_signal_handlers(app_manager: OptimizedApplicationManager):
    """Setup graceful shutdown signal handlers."""
    
    def signal_handler(signum, frame) -> Any:
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        asyncio.create_task(app_manager.shutdown())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

# =============================================================================
# Optimized Main Function
# =============================================================================
async def main():
    """Optimized main entrypoint for HeyGen AI FastAPI server."""
    app_manager = OptimizedApplicationManager()
    
    try:
        # Setup signal handlers
        setup_signal_handlers(app_manager)
        
        # Startup
        await app_manager.startup()
        
        # Configure application
        app = app_manager.configure_application()
        
        # Get server configuration
        server_config = get_optimized_server_config()
        
        logger.info(
            "Starting optimized HeyGen AI FastAPI server",
            extra={
                "environment": EnvironmentConfig.get_environment(),
                "host": EnvironmentConfig.get_host(),
                "port": EnvironmentConfig.get_port(),
                "workers": EnvironmentConfig.get_workers(),
                "log_level": EnvironmentConfig.get_log_level(),
                "reload": EnvironmentConfig.get_reload(),
                "optimization_level": EnvironmentConfig.get_optimization_level().value,
                "redis_enabled": bool(EnvironmentConfig.get_redis_url()),
                "max_concurrent_requests": server_config.get("limit_concurrency"),
                "max_requests_per_worker": server_config.get("limit_max_requests")
            }
        )
        
        # Start server
        config = uvicorn.Config(
            app,
            **server_config
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", exc_info=True)
        sys.exit(1)
    finally:
        await app_manager.shutdown()

# =============================================================================
# Application Instance
# =============================================================================
app_manager = OptimizedApplicationManager()
app = app_manager.configure_application()

# =============================================================================
# Entry Point
# =============================================================================
match __name__:
    case "__main__":
    asyncio.run(main()) 