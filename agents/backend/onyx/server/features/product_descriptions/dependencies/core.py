"""
Core Dependencies

This module provides core dependency injection functions for database,
cache, monitoring, and async I/O operations.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from contextvars import ContextVar
import logging
from datetime import datetime

# Import managers and services
from ..async_database_api_operations import AsyncDatabaseManager, AsyncAPIManager
from ..caching_manager import CachingManager
from ..performance_metrics import PerformanceMonitor
from ..error_handling_middleware import ErrorMonitor
from ..async_io_manager import AsyncIOManager

# Import schemas and models
from ..schemas.base import User, DatabaseSession
from ..utils.logging import get_logger

# Logger
logger = get_logger(__name__)

# Context variables
current_user_var: ContextVar[Optional[User]] = ContextVar("current_user", default=None)
db_session_var: ContextVar[Optional[DatabaseSession]] = ContextVar("db_session", default=None)

# Global instances (singleton pattern)
_db_manager: Optional[AsyncDatabaseManager] = None
_api_manager: Optional[AsyncAPIManager] = None
_cache_manager: Optional[CachingManager] = None
_performance_monitor: Optional[PerformanceMonitor] = None
_error_monitor: Optional[ErrorMonitor] = None
_async_io_manager: Optional[AsyncIOManager] = None

def get_db_manager() -> AsyncDatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = AsyncDatabaseManager()
        logger.info("Database manager initialized")
    return _db_manager

def get_api_manager() -> AsyncAPIManager:
    """Get or create API manager instance."""
    global _api_manager
    if _api_manager is None:
        _api_manager = AsyncAPIManager()
        logger.info("API manager initialized")
    return _api_manager

def get_cache_manager() -> CachingManager:
    """Get or create cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CachingManager()
        logger.info("Cache manager initialized")
    return _cache_manager

def get_performance_monitor() -> PerformanceMonitor:
    """Get or create performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
        logger.info("Performance monitor initialized")
    return _performance_monitor

def get_error_monitor() -> ErrorMonitor:
    """Get or create error monitor instance."""
    global _error_monitor
    if _error_monitor is None:
        _error_monitor = ErrorMonitor()
        logger.info("Error monitor initialized")
    return _error_monitor

def get_async_io_manager() -> AsyncIOManager:
    """Get or create async I/O manager instance."""
    global _async_io_manager
    if _async_io_manager is None:
        _async_io_manager = AsyncIOManager()
        logger.info("Async I/O manager initialized")
    return _async_io_manager

# FastAPI dependency functions
async def get_current_user() -> Optional[User]:
    """
    Get current user from context or authentication.
    
    This dependency can be used in routes that don't require authentication.
    Returns None if no user is authenticated.
    """
    # Check if user is already in context
    current_user = current_user_var.get()
    if current_user:
        return current_user
    
    # TODO: Implement actual authentication logic
    # For now, return a mock user
    mock_user = User(
        id="mock_user_id",
        email="user@example.com",
        username="mock_user",
        is_active=True,
        is_admin=False,
        created_at=datetime.utcnow()
    )
    
    # Set in context for this request
    current_user_var.set(mock_user)
    return mock_user

async def get_db_session() -> DatabaseSession:
    """
    Get database session with connection pooling.
    
    This dependency provides a database session that can be used
    for database operations with automatic connection management.
    """
    db_manager = get_db_manager()
    session = await db_manager.get_session()
    
    # Set in context for this request
    db_session_var.set(session)
    return session

async def get_cache_manager_dep() -> CachingManager:
    """
    Get cache manager dependency.
    
    This dependency provides access to the caching system
    for storing and retrieving cached data.
    """
    return get_cache_manager()

async def get_performance_monitor_dep() -> PerformanceMonitor:
    """
    Get performance monitor dependency.
    
    This dependency provides access to performance monitoring
    and metrics collection.
    """
    return get_performance_monitor()

async def get_error_monitor_dep() -> ErrorMonitor:
    """
    Get error monitor dependency.
    
    This dependency provides access to error monitoring
    and alerting capabilities.
    """
    return get_error_monitor()

async def get_async_io_manager_dep() -> AsyncIOManager:
    """
    Get async I/O manager dependency.
    
    This dependency provides access to async I/O operations
    for database and external API calls.
    """
    return get_async_io_manager()

# Alias for backward compatibility
get_cache_manager = get_cache_manager_dep
get_performance_monitor = get_performance_monitor_dep
get_error_monitor = get_error_monitor_dep
get_async_io_manager = get_async_io_manager_dep

# Utility functions
def set_current_user(user: User):
    """Set current user in context."""
    current_user_var.set(user)

def get_current_user_from_context() -> Optional[User]:
    """Get current user from context."""
    return current_user_var.get()

def set_db_session(session: DatabaseSession):
    """Set database session in context."""
    db_session_var.set(session)

def get_db_session_from_context() -> Optional[DatabaseSession]:
    """Get database session from context."""
    return db_session_var.get()

# Cleanup functions
async def cleanup_resources():
    """Cleanup all resources and connections."""
    global _db_manager, _api_manager, _cache_manager, _performance_monitor, _error_monitor, _async_io_manager
    
    if _db_manager:
        await _db_manager.close()
        _db_manager = None
    
    if _api_manager:
        await _api_manager.close()
        _api_manager = None
    
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None
    
    if _performance_monitor:
        await _performance_monitor.close()
        _performance_monitor = None
    
    if _error_monitor:
        await _error_monitor.close()
        _error_monitor = None
    
    if _async_io_manager:
        await _async_io_manager.close()
        _async_io_manager = None
    
    logger.info("All resources cleaned up") 