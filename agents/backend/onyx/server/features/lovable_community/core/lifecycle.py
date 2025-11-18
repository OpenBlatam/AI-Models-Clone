"""
Application lifecycle management

Handles startup and shutdown procedures for the FastAPI application.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

from ..config import settings
from .database import (
    init_database,
    verify_database_connection,
    DatabaseManager
)
from ..utils.logging_config import StructuredLogger

logger = StructuredLogger(__name__)

# Global database manager instance
_db_manager: DatabaseManager = DatabaseManager()


def startup_handler() -> None:
    """
    Handle application startup procedures.
    
    Performs:
    - Database initialization
    - Connection verification
    - Performance optimizations
    - Logging of startup information
    """
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug
    )
    
    try:
        # Initialize database
        _db_manager.initialize()
        logger.info("Database initialized successfully")
        
        # Verify connection
        if _db_manager.verify_connection():
            logger.info("Database connection verified")
        else:
            logger.warning(
                "Database connection verification failed",
                database_url=settings.database_url.split("@")[-1] if "@" in settings.database_url else "local"
            )
        
        # Configure performance optimizations
        try:
            from .performance_config import configure_pytorch_performance
            configure_pytorch_performance()
            
            # Additional CUDA optimizations
            from ...utils import optimize_cuda_settings, enable_tensor_cores
            optimize_cuda_settings()
            enable_tensor_cores()
        except ImportError:
            logger.debug("PyTorch not available, skipping performance config")
        except Exception as e:
            logger.warning("Failed to configure performance", error=str(e))
            
    except Exception as e:
        logger.exception("Error during startup", error=str(e))
        raise


def shutdown_handler() -> None:
    """
    Handle application shutdown procedures.
    
    Performs cleanup operations.
    """
    logger.info(
        "Shutting down application",
        app_name=settings.app_name
    )
    # Add any cleanup operations here if needed
    logger.info("Shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.
    
    Handles:
    - Startup procedures
    - Resource initialization
    - Shutdown cleanup
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Control is yielded to the application
    """
    # Startup
    startup_handler()
    
    yield
    
    # Shutdown
    shutdown_handler()


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: Global database manager instance
    """
    return _db_manager

