#!/usr/bin/env python3
"""
Server startup script for HeyGen AI API
Handles initialization, configuration, and graceful shutdown.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Import application components
from config import settings, setup_configuration, get_cors_config
from database import init_database, close_database
from main import app

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ServerManager:
    """Manages server lifecycle and graceful shutdown."""
    
    def __init__(self):
        self.app = app
        self.server = None
        self.shutdown_event = asyncio.Event()
    
    async def startup(self):
        """Initialize application on startup."""
        logger.info("🚀 Starting HeyGen AI API Server...")
        
        try:
            # Setup configuration
            setup_configuration()
            logger.info("✓ Configuration setup completed")
            
            # Initialize database
            await init_database()
            logger.info("✓ Database initialized")
            
            # Add middleware
            self._setup_middleware()
            logger.info("✓ Middleware configured")
            
            # Setup signal handlers
            self._setup_signal_handlers()
            logger.info("✓ Signal handlers configured")
            
            logger.info("✅ Server startup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            raise
    
    async def shutdown(self):
        """Cleanup on shutdown."""
        logger.info("🛑 Shutting down HeyGen AI API Server...")
        
        try:
            # Close database connections
            await close_database()
            logger.info("✓ Database connections closed")
            
            # Additional cleanup
            await self._cleanup_resources()
            logger.info("✓ Resources cleaned up")
            
            logger.info("✅ Server shutdown completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Server shutdown error: {e}")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware."""
        # CORS middleware
        cors_config = get_cors_config()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config["allow_origins"],
            allow_credentials=cors_config["allow_credentials"],
            allow_methods=cors_config["allow_methods"],
            allow_headers=cors_config["allow_headers"],
        )
        
        # Gzip middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Additional middleware can be added here
        # self.app.add_middleware(RateLimitMiddleware)
        # self.app.add_middleware(AuthMiddleware)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _cleanup_resources(self):
        """Cleanup application resources."""
        # Close any open connections
        # Clear caches
        # Stop background tasks
        pass
    
    async def run_server(self):
        """Run the server with proper lifecycle management."""
        config = uvicorn.Config(
            app=self.app,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.lower(),
            access_log=True,
            workers=settings.workers if not settings.reload else 1
        )
        
        self.server = uvicorn.Server(config)
        
        try:
            await self.server.serve()
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await self.shutdown()


async def main():
    """Main application entry point."""
    server_manager = ServerManager()
    
    try:
        # Startup
        await server_manager.startup()
        
        # Run server
        await server_manager.run_server()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        # Shutdown
        await server_manager.shutdown()


def run_development():
    """Run server in development mode."""
    logger.info("🔧 Running in development mode")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=True
    )


def run_production():
    """Run server in production mode."""
    logger.info("🚀 Running in production mode")
    
    # Use asyncio for production
    asyncio.run(main())


def run_testing():
    """Run server in testing mode."""
    logger.info("🧪 Running in testing mode")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
        access_log=False
    )


if __name__ == "__main__":
    # Determine run mode based on environment
    environment = settings.debug
    
    if settings.reload:
        # Development mode with auto-reload
        run_development()
    elif environment:
        # Development mode without auto-reload
        run_development()
    else:
        # Production mode
        run_production() 