"""
Main Application Entry Point - Refactored Production Application.

Clean, modular entry point using the new architecture with
separated concerns and optimized configuration.
"""

import asyncio
import os
import sys
import signal
from typing import Optional

import uvicorn
import structlog

# High-performance event loop
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

from .core import create_application, load_config, Environment
from .core.config import AppConfig

# Configure logging
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


def create_app() -> "FastAPI":
    """Application factory for ASGI servers."""
    config = load_config()
    app = create_application(config)
    return app


async def run_server(config: Optional[AppConfig] = None):
    """Run the application server with optimal configuration."""
    if config is None:
        config = load_config()
    
    # Create application
    app = create_application(config)
    
    # Configure uvicorn
    server_config = uvicorn.Config(
        app=app,
        host=config.host,
        port=config.port,
        workers=1,  # Single worker for async app
        loop="uvloop" if config.enable_uvloop and UVLOOP_AVAILABLE else "asyncio",
        http="httptools",
        log_level=config.monitoring.log_level.lower(),
        access_log=config.debug,
        server_header=False,
        date_header=False,
        reload=config.debug,
        reload_dirs=["agents/backend_ads/agents/backend/onyx/server/features"] if config.debug else None
    )
    
    server = uvicorn.Server(server_config)
    
    # Setup graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        server.should_exit = True
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Log startup info
    logger.info("🚀 Starting Onyx Production Server",
               config=config.get_summary())
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        raise


def main():
    """Main entry point."""
    try:
        # Load configuration
        config = load_config()
        
        # Setup event loop optimization
        if config.enable_uvloop and UVLOOP_AVAILABLE:
            uvloop.install()
            logger.info("✅ UVLoop installed for maximum performance")
        
        # Run application
        asyncio.run(run_server(config))
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error("Application startup failed", error=str(e), exc_info=True)
        sys.exit(1)


def dev_server():
    """Development server with hot reload."""
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "true"
    main()


def prod_server():
    """Production server with full optimizations."""
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DEBUG"] = "false"
    main()


if __name__ == "__main__":
    main()


# Export for ASGI servers
app = create_app()

__all__ = ['app', 'create_app', 'main', 'dev_server', 'prod_server'] 