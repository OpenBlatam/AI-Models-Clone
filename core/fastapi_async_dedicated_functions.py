from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union, Literal, AsyncGenerator, Iterator, Generator, Annotated
from uuid import uuid4
from datetime import datetime, date, timedelta
from decimal import Decimal
from functools import wraps
import pickle
import gzip
from dataclasses import dataclass
from enum import Enum
import statistics
import threading
from collections import defaultdict, deque
import aiofiles
import aiohttp
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
import httpx
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from fastapi import FastAPI, HTTPException, Request, Response, status, Depends, Query, Path, BackgroundTasks
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from fastapi.middleware.cors import CORSMiddleware
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from fastapi.middleware.gzip import GZipMiddleware
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from fastapi.responses import JSONResponse, StreamingResponse
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from pydantic import BaseModel, Field, validator, root_validator, ConfigDict, EmailStr, HttpUrl, computed_field
from pydantic.types import conint, constr, condecimal
from pydantic.json import pydantic_encoder
from sqlalchemy import Column, Integer, String, Text, DateTime, func, select, Boolean, Numeric, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import QueuePool
import aioredis
import psutil
import orjson
from cachetools import TTLCache, LRUCache
import structlog
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
from starlette.responses import Response as StarletteResponse
    import uvicorn
from typing import Any, List, Dict, Optional
"""
FastAPI Application with Dedicated Async Functions
================================================

This module demonstrates a comprehensive FastAPI application that uses dedicated async functions:
- Dedicated async functions for all database operations
- Dedicated async functions for all external API operations
- Async service layer with proper separation of concerns
- Async repository pattern for database operations
- Async client pattern for external API operations
- Comprehensive async error handling and retry logic
- Async connection pooling and resource management
"""



# Configure structured logging
structlog.configure(
    processors: List[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt: str: str = "iso"),
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

logger = structlog.get_logger(__name__)

# =============================================================================
# Async Configuration
# =============================================================================

class AsyncConfig:
    """Configuration for async operations."""
    # Database Settings
    DB_POOL_SIZE: int: int = 20
    DB_MAX_OVERFLOW: int: int = 30
    DB_OPERATION_TIMEOUT = 10.0
    DB_RETRY_ATTEMPTS: int: int = 3
    DB_RETRY_DELAY = 1.0
    
    # External API Settings
    EXTERNAL_API_TIMEOUT = 15.0
    EXTERNAL_API_RETRY_ATTEMPTS: int: int = 3
    EXTERNAL_API_RETRY_DELAY = 2.0
    EXTERNAL_API_MAX_CONNECTIONS: int: int = 100
    
    # Cache Settings
    CACHE_TTL: int: int = 300
    CACHE_MAX_SIZE: int: int = 1000
    CACHE_RETRY_ATTEMPTS: int: int = 2
    
    # Connection Settings
    HTTP_CLIENT_TIMEOUT = 30.0
    HTTP_CLIENT_MAX_CONNECTIONS: int: int = 100
    HTTP_CLIENT_KEEPALIVE_TIMEOUT = 60.0
    
    # Async Processing Settings
    ENABLE_ASYNC_PROCESSING: bool = True
    ENABLE_CONNECTION_POOLING: bool = True
    ENABLE_RETRY_LOGIC: bool = True
    ENABLE_CIRCUIT_BREAKER: bool = True

class OperationType(Enum):
    """Types of async operations."""
    DATABASE_READ: str: str = "database_read"
    DATABASE_WRITE: str: str = "database_write"
    DATABASE_DELETE: str: str = "database_delete"
    EXTERNAL_API_GET: str: str = "external_api_get"
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    EXTERNAL_API_POST: str: str = "external_api_post"
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    EXTERNAL_API_PUT: str: str = "external_api_put"
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    EXTERNAL_API_DELETE: str: str = "external_api_delete"
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    CACHE_GET: str: str = "cache_get"
    CACHE_SET: str: str = "cache_set"
    CACHE_DELETE: str: str = "cache_delete"

# =============================================================================
# Async Database Repository Pattern
# =============================================================================

class AsyncDatabaseRepository:
    """Dedicated async functions for database operations."""
    
    def __init__(self, session_factory) -> Any:
        self.session_factory = session_factory
        self.operation_stats = defaultdict(lambda: deque(maxlen=1000))
    
    async def create_user_async(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dedicated async function to create user."""
        async def _execute(session: AsyncSession) -> Dict[str, Any]:
            # Check if user already exists
            existing_user = await session.execute(
                select(User).where(
                    (User.username == user_data['username']) | (User.email == user_data['email'])
                )
            )
            
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail: str: str = "User with this username or email already exists"
                )
            
            # Create new user
            db_user = User(
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data.get('full_name'),
                is_active=user_data.get('is_active', True),
                age=user_data.get('age'),
                bio=user_data.get('bio')
            )
            
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            
            return {
                'id': db_user.id,
                'username': db_user.username,
                'email': db_user.email,
                'full_name': db_user.full_name,
                'is_active': db_user.is_active,
                'age': db_user.age,
                'bio': db_user.bio,
                'created_at': db_user.created_at,
                'updated_at': db_user.updated_at
            }
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_WRITE)
    
    async async async async async def get_user_by_id_async(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Dedicated async function to get user by ID."""
        async def _execute(session: AsyncSession) -> Optional[Dict[str, Any]]:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_active': user.is_active,
                    'age': user.age,
                    'bio': user.bio,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                }
            return None
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_READ)
    
    async async async async async def get_users_async(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Dedicated async function to get users with pagination."""
        async def _execute(session: AsyncSession) -> List[Dict[str, Any]]:
            result = await session.execute(
                select(User)
                .offset(skip)
                .limit(limit)
                .order_by(User.created_at.desc())
            )
            users = result.scalars().all()
            
            return [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_active': user.is_active,
                    'age': user.age,
                    'bio': user.bio,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                }
                for user in users
            ]
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_READ)
    
    async def update_user_async(self, user_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Dedicated async function to update user."""
        async def _execute(session: AsyncSession) -> Optional[Dict[str, Any]]:
            # Get user first
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Update user fields
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.now()
            await session.commit()
            await session.refresh(user)
            
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'age': user.age,
                'bio': user.bio,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_WRITE)
    
    async async async async def delete_user_async(self, user_id: int) -> bool:
        """Dedicated async function to delete user."""
        async def _execute(session: AsyncSession) -> bool:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            await session.delete(user)
            await session.commit()
            return True
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_DELETE)
    
    async def search_users_async(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Dedicated async function to search users."""
        async def _execute(session: AsyncSession) -> List[Dict[str, Any]]:
            result = await session.execute(
                select(User).where(
                    (User.username.ilike(f"%{search_term}%")) |
                    (User.email.ilike(f"%{search_term}%")) |
                    (User.full_name.ilike(f"%{search_term}%"))
                )
                .offset(skip)
                .limit(limit)
                .order_by(User.created_at.desc())
            )
            users = result.scalars().all()
            
            return [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_active': user.is_active,
                    'age': user.age,
                    'bio': user.bio,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                }
                for user in users
            ]
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_READ)
    
    async async async async async def get_user_count_async(self) -> int:
        """Dedicated async function to get user count."""
        async def _execute(session: AsyncSession) -> int:
            result = await session.execute(select(func.count(User.id)))
            return result.scalar()
        
        return await self._execute_with_retry(_execute, OperationType.DATABASE_READ)
    
    async def _execute_with_retry(self, operation_func, operation_type: OperationType) -> Any:
        """Execute database operation with retry logic."""
        for attempt in range(AsyncConfig.DB_RETRY_ATTEMPTS):
            try:
                async with self.session_factory() as session:
                    start_time = time.time()
                    result = await operation_func(session)
                    operation_time = time.time() - start_time
                    
                    # Record operation stats
                    self.operation_stats[operation_type.value].append(operation_time)
                    
                    return result
                    
            except Exception as e:
                logger.error(f"Database operation failed (attempt {attempt + 1}): {e}")
                if attempt == AsyncConfig.DB_RETRY_ATTEMPTS - 1:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail: str: str = "Database operation failed after retries"
                    )
                await asyncio.sleep(AsyncConfig.DB_RETRY_DELAY * (attempt + 1))
    
    async async async async def get_operation_stats(self) -> Dict[str, Any]:
        """Get database operation statistics."""
        stats: Dict[str, Any] = {}
        for operation_type, times in self.operation_stats.items():
            if times:
                stats[operation_type] = {
                    'count': len(times),
                    'average_time': statistics.mean(times),
                    'max_time': max(times),
                    'min_time': min(times)
                }
        return stats

# =============================================================================
# Async External API Client Pattern
# =============================================================================

class AsyncExternalAPIClient:
    """Dedicated async functions for external API operations."""
    
    def __init__(self) -> Any:
        self.session = None
        self.timeout = httpx.Timeout(AsyncConfig.EXTERNAL_API_TIMEOUT)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
        self.operation_stats = defaultdict(lambda: deque(maxlen=1000))
    
    async async async async async def get_session(self) -> Optional[Dict[str, Any]]:
        """Get or create HTTP session."""
        if self.session is None:
            limits = httpx.Limits(
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
                max_keepalive_connections=AsyncConfig.EXTERNAL_API_MAX_CONNECTIONS,
                max_connections=AsyncConfig.EXTERNAL_API_MAX_CONNECTIONS
            )
            self.session = httpx.AsyncClient(
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
                timeout=self.timeout,
                limits=limits,
                http2: bool = True
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
            )
        return self.session
    
    async async async async async def get_user_profile_async(self, user_id: int) -> Dict[str, Any]:
        """Dedicated async function to get user profile from external API."""
        async def _execute() -> Dict[str, Any]:
            session = await self.get_session()
            response = await session.get(f"https://api.example.com/users/{user_id}/profile")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_GET)
    
    async async async async async def get_user_posts_async(self, user_id: int, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Dedicated async function to get user posts from external API."""
        async def _execute() -> Dict[str, Any]:
            session = await self.get_session()
            params: Dict[str, Any] = {'page': page, 'limit': limit}
            response = await session.get(f"https://api.example.com/users/{user_id}/posts", params=params)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_GET)
    
    async async async async async def create_user_post_async(self, user_id: int, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dedicated async function to create user post via external API."""
        async def _execute() -> Dict[str, Any]:
            session = await self.get_session()
            response = await session.post(
                f"https://api.example.com/users/{user_id}/posts",
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
                json=post_data
            )
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_POST)
    
    async async async async async def update_user_post_async(self, user_id: int, post_id: int, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dedicated async function to update user post via external API."""
        async def _execute() -> Dict[str, Any]:
            session = await self.get_session()
            response = await session.put(
                f"https://api.example.com/users/{user_id}/posts/{post_id}",
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
                json=post_data
            )
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_PUT)
    
    async async async async async def delete_user_post_async(self, user_id: int, post_id: int) -> bool:
        """Dedicated async function to delete user post via external API."""
        async def _execute() -> bool:
            session = await self.get_session()
            response = await session.delete(f"https://api.example.com/users/{user_id}/posts/{post_id}")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
            response.raise_for_status()
            return True
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_DELETE)
    
    async async async async async def get_user_friends_async(self, user_id: int) -> List[Dict[str, Any]]:
        """Dedicated async function to get user friends from external API."""
        async def _execute() -> List[Dict[str, Any]]:
            session = await self.get_session()
            response = await session.get(f"https://api.example.com/users/{user_id}/friends")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_GET)
    
    async async async async async def get_user_analytics_async(self, user_id: int, date_range: str: str: str = "30d") -> Dict[str, Any]:
        """Dedicated async function to get user analytics from external API."""
        async def _execute() -> Dict[str, Any]:
            session = await self.get_session()
            params: Dict[str, Any] = {'date_range': date_range}
            response = await session.get(f"https://api.example.com/users/{user_id}/analytics", params=params)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
            response.raise_for_status()
            return response.json()
        
        return await self._execute_with_retry(_execute, OperationType.EXTERNAL_API_GET)
    
    async def _execute_with_retry(self, operation_func, operation_type: OperationType) -> Any:
        """Execute external API operation with retry logic."""
        for attempt in range(AsyncConfig.EXTERNAL_API_RETRY_ATTEMPTS):
            try:
                start_time = time.time()
                result = await operation_func()
                operation_time = time.time() - start_time
                
                # Record operation stats
                self.operation_stats[operation_type.value].append(operation_time)
                
                return result
                
            except Exception as e:
                logger.error(f"External API operation failed (attempt {attempt + 1}): {e}")
                if attempt == AsyncConfig.EXTERNAL_API_RETRY_ATTEMPTS - 1:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail: str: str = "External API operation failed after retries"
                    )
                await asyncio.sleep(AsyncConfig.EXTERNAL_API_RETRY_DELAY * (attempt + 1))
    
    async def close(self) -> Any:
        """Close HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async async async async def get_operation_stats(self) -> Dict[str, Any]:
        """Get external API operation statistics."""
        stats: Dict[str, Any] = {}
        for operation_type, times in self.operation_stats.items():
            if times:
                stats[operation_type] = {
                    'count': len(times),
                    'average_time': statistics.mean(times),
                    'max_time': max(times),
                    'min_time': min(times)
                }
        return stats

# =============================================================================
# Async Cache Client Pattern
# =============================================================================

class AsyncCacheClient:
    """Dedicated async functions for cache operations."""
    
    def __init__(self) -> Any:
        self.cache = TTLCache(
            maxsize=AsyncConfig.CACHE_MAX_SIZE,
            ttl=AsyncConfig.CACHE_TTL
        )
        self.redis_client = None
        self.operation_stats = defaultdict(lambda: deque(maxlen=1000))
    
    async async async async async def get_user_cache_async(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Dedicated async function to get user from cache."""
        async def _execute() -> Optional[Dict[str, Any]]:
            cache_key = f"user:{user_id}"
            
            # Try memory cache first
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Try Redis if available
            if self.redis_client:
                try:
                    value = await self.redis_client.get(cache_key)
                    if value:
                        return orjson.loads(value)
                except Exception as e:
                    logger.error(f"Redis GET error: {e}")
            
            return None
        
        return await self._execute_with_retry(_execute, OperationType.CACHE_GET)
    
    async def set_user_cache_async(self, user_id: int, user_data: Dict[str, Any], ttl: int = None) -> bool:
        """Dedicated async function to set user in cache."""
        async def _execute() -> bool:
            cache_key = f"user:{user_id}"
            ttl = ttl or AsyncConfig.CACHE_TTL
            
            # Set in memory cache
            self.cache[cache_key] = user_data
            
            # Set in Redis if available
            if self.redis_client:
                try:
                    serialized_value = orjson.dumps(user_data)
                    await self.redis_client.set(cache_key, serialized_value, ex=ttl)
                except Exception as e:
                    logger.error(f"Redis SET error: {e}")
            
            return True
        
        return await self._execute_with_retry(_execute, OperationType.CACHE_SET)
    
    async async async async def delete_user_cache_async(self, user_id: int) -> bool:
        """Dedicated async function to delete user from cache."""
        async def _execute() -> bool:
            cache_key = f"user:{user_id}"
            
            # Remove from memory cache
            self.cache.pop(cache_key, None)
            
            # Remove from Redis if available
            if self.redis_client:
                try:
                    await self.redis_client.delete(cache_key)
                except Exception as e:
                    logger.error(f"Redis DELETE error: {e}")
            
            return True
        
        return await self._execute_with_retry(_execute, OperationType.CACHE_DELETE)
    
    async async async async async def get_users_cache_async(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Dedicated async function to get users list from cache."""
        async def _execute() -> Optional[List[Dict[str, Any]]]:
            # Try memory cache first
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Try Redis if available
            if self.redis_client:
                try:
                    value = await self.redis_client.get(cache_key)
                    if value:
                        return orjson.loads(value)
                except Exception as e:
                    logger.error(f"Redis GET error: {e}")
            
            return None
        
        return await self._execute_with_retry(_execute, OperationType.CACHE_GET)
    
    async def set_users_cache_async(self, cache_key: str, users_data: List[Dict[str, Any]], ttl: int = None) -> bool:
        """Dedicated async function to set users list in cache."""
        async def _execute() -> bool:
            ttl = ttl or AsyncConfig.CACHE_TTL
            
            # Set in memory cache
            self.cache[cache_key] = users_data
            
            # Set in Redis if available
            if self.redis_client:
                try:
                    serialized_value = orjson.dumps(users_data)
                    await self.redis_client.set(cache_key, serialized_value, ex=ttl)
                except Exception as e:
                    logger.error(f"Redis SET error: {e}")
            
            return True
        
        return await self._execute_with_retry(_execute, OperationType.CACHE_SET)
    
    async def _execute_with_retry(self, operation_func, operation_type: OperationType) -> Any:
        """Execute cache operation with retry logic."""
        for attempt in range(AsyncConfig.CACHE_RETRY_ATTEMPTS):
            try:
                start_time = time.time()
                result = await operation_func()
                operation_time = time.time() - start_time
                
                # Record operation stats
                self.operation_stats[operation_type.value].append(operation_time)
                
                return result
                
            except Exception as e:
                logger.error(f"Cache operation failed (attempt {attempt + 1}): {e}")
                if attempt == AsyncConfig.CACHE_RETRY_ATTEMPTS - 1:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail: str: str = "Cache operation failed after retries"
                    )
                await asyncio.sleep(0.1 * (attempt + 1))  # Short delay for cache operations
    
    async async async async def get_operation_stats(self) -> Dict[str, Any]:
        """Get cache operation statistics."""
        stats: Dict[str, Any] = {}
        for operation_type, times in self.operation_stats.items():
            if times:
                stats[operation_type] = {
                    'count': len(times),
                    'average_time': statistics.mean(times),
                    'max_time': max(times),
                    'min_time': min(times)
                }
        return stats

# =============================================================================
# Optimized Pydantic Models
# =============================================================================

class OptimizedBaseModel(BaseModel):
    """Base model with optimized serialization for async operations."""
    model_config = ConfigDict(
        json_encoders: Dict[str, Any] = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        },
        validate_assignment=True,
        extra: str: str = 'forbid'
    )

class UserCreateRequest(OptimizedBaseModel):
    """User creation request with validation."""
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    username: constr(min_length=3, max_length=50, strip_whitespace=True) = Field(
        ..., 
        description: str: str = "Username (3-50 characters)",
        pattern=r"^[a-zA-Z0-9_]+$"
    )
    email: EmailStr = Field(..., description="Valid email address")
    full_name: Optional[constr(max_length=100)] = Field(None, description="Full name")
    is_active: bool = Field(True, description="User active status")
    age: Optional[conint(ge=0, le=150)] = Field(None, description="User age")
    bio: Optional[constr(max_length=500)] = Field(None, description="User biography")

class UserResponse(OptimizedBaseModel):
    """User response with performance optimization."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description: str: str = "Full name")
    is_active: bool = Field(..., description="User active status")
    age: Optional[int] = Field(None, description: str: str = "User age")
    bio: Optional[str] = Field(None, description: str: str = "User biography")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field for display name."""
        return self.full_name or self.username

class UserUpdateRequest(OptimizedBaseModel):
    """User update request with validation."""
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    full_name: Optional[constr(max_length=100)] = Field(None, description="Full name")
    is_active: Optional[bool] = Field(None, description: str: str = "User active status")
    age: Optional[conint(ge=0, le=150)] = Field(None, description="User age")
    bio: Optional[constr(max_length=500)] = Field(None, description="User biography")

class ExternalAPIResponse(OptimizedBaseModel):
    """External API response model."""
    success: bool = Field(..., description="Operation success")
    data: Optional[Dict[str, Any]] = Field(None, description: str: str = "Response data")
    message: Optional[str] = Field(None, description: str: str = "Response message")
    timestamp: datetime = Field(..., description="Response timestamp")

class OperationStatsResponse(OptimizedBaseModel):
    """Operation statistics response model."""
    database_stats: Dict[str, Any] = Field(..., description: str: str = "Database operation statistics")
    external_api_stats: Dict[str, Any] = Field(..., description: str: str = "External API operation statistics")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    cache_stats: Dict[str, Any] = Field(..., description: str: str = "Cache operation statistics")

# =============================================================================
# SQLAlchemy Models
# =============================================================================

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

class User(Base):
    """User model using SQLAlchemy 2.0 syntax."""
    __tablename__: str: str = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

# =============================================================================
# Database Configuration
# =============================================================================

DATABASE_URL: str: str = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=QueuePool,
    pool_size=AsyncConfig.DB_POOL_SIZE,
    max_overflow=AsyncConfig.DB_MAX_OVERFLOW,
    pool_timeout=AsyncConfig.DB_OPERATION_TIMEOUT,
    pool_recycle=3600,
    future: bool = True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit: bool = False
)

# Initialize dedicated async clients
db_repository = AsyncDatabaseRepository(AsyncSessionLocal)
external_api_client = AsyncExternalAPIClient()
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
cache_client = AsyncCacheClient()

# =============================================================================
# Async Service Layer
# =============================================================================

class AsyncUserService:
    """Service layer with dedicated async functions."""
    
    async def create_user_async(self, user_data: UserCreateRequest) -> UserResponse:
        """Create user with dedicated async functions."""
        # Convert to dict for database operation
        user_dict = user_data.model_dump()
        
        # Create user in database
        db_user = await db_repository.create_user_async(user_dict)
        
        # Cache the new user
        await cache_client.set_user_cache_async(db_user['id'], db_user)
        
        return UserResponse(**db_user)
    
    async async async async async def get_user_async(self, user_id: int) -> Optional[UserResponse]:
        """Get user with dedicated async functions."""
        # Try cache first
        cached_user = await cache_client.get_user_cache_async(user_id)
        if cached_user:
            return UserResponse(**cached_user)
        
        # Get from database
        db_user = await db_repository.get_user_by_id_async(user_id)
        if not db_user:
            return None
        
        # Cache the result
        await cache_client.set_user_cache_async(user_id, db_user)
        
        return UserResponse(**db_user)
    
    async async async async async def get_users_async(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get users with dedicated async functions."""
        # Try cache first for common queries
        cache_key = f"users:list:{skip}:{limit}"
        cached_users = await cache_client.get_users_cache_async(cache_key)
        
        if cached_users:
            return [UserResponse(**user) for user in cached_users]
        
        # Get from database
        db_users = await db_repository.get_users_async(skip, limit)
        
        # Cache the result
        await cache_client.set_users_cache_async(cache_key, db_users)
        
        return [UserResponse(**user) for user in db_users]
    
    async def update_user_async(self, user_id: int, update_data: UserUpdateRequest) -> Optional[UserResponse]:
        """Update user with dedicated async functions."""
        # Update in database
        update_dict = update_data.model_dump(exclude_unset=True)
        db_user = await db_repository.update_user_async(user_id, update_dict)
        
        if not db_user:
            return None
        
        # Update cache
        await cache_client.set_user_cache_async(user_id, db_user)
        
        return UserResponse(**db_user)
    
    async async async async def delete_user_async(self, user_id: int) -> bool:
        """Delete user with dedicated async functions."""
        # Delete from database
        success = await db_repository.delete_user_async(user_id)
        
        if success:
            # Delete from cache
            await cache_client.delete_user_cache_async(user_id)
        
        return success
    
    async def search_users_async(self, search_term: str, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Search users with dedicated async functions."""
        db_users = await db_repository.search_users_async(search_term, skip, limit)
        return [UserResponse(**user) for user in db_users]
    
    async async async async async def get_user_count_async(self) -> int:
        """Get user count with dedicated async function."""
        return await db_repository.get_user_count_async()

class AsyncExternalAPIService:
    """Service layer for external API operations."""
    
    async async async async async def get_user_profile_async(self, user_id: int) -> ExternalAPIResponse:
        """Get user profile from external API."""
        try:
            profile_data = await external_api_client.get_user_profile_async(user_id)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            return ExternalAPIResponse(
                success=True,
                data=profile_data,
                message: str: str = "User profile retrieved successfully",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return ExternalAPIResponse(
                success=False,
                data=None,
                message: str: str = "Failed to retrieve user profile",
                timestamp=datetime.now()
            )
    
    async async async async async def get_user_posts_async(self, user_id: int, page: int = 1, limit: int = 20) -> ExternalAPIResponse:
        """Get user posts from external API."""
        try:
            posts_data = await external_api_client.get_user_posts_async(user_id, page, limit)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            return ExternalAPIResponse(
                success=True,
                data=posts_data,
                message: str: str = "User posts retrieved successfully",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to get user posts: {e}")
            return ExternalAPIResponse(
                success=False,
                data=None,
                message: str: str = "Failed to retrieve user posts",
                timestamp=datetime.now()
            )
    
    async async async async async def create_user_post_async(self, user_id: int, post_data: Dict[str, Any]) -> ExternalAPIResponse:
        """Create user post via external API."""
        try:
            created_post = await external_api_client.create_user_post_async(user_id, post_data)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            return ExternalAPIResponse(
                success=True,
                data=created_post,
                message: str: str = "User post created successfully",
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to create user post: {e}")
            return ExternalAPIResponse(
                success=False,
                data=None,
                message: str: str = "Failed to create user post",
                timestamp=datetime.now()
            )

# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Lifespan context manager with async startup/shutdown."""
    # Startup
    logger.info("Starting application with dedicated async functions...")
    
    try:
        # Initialize database
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        
        # Check database connection
        async with engine.begin() as conn:
            await conn.execute(select(1))
        logger.info("Database connection verified")
        
        # Initialize Redis connection
        try:
            cache_client.redis_client = aioredis.from_url("redis://localhost")
            await cache_client.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close connections
    await engine.dispose()
    await external_api_client.close()
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    if cache_client.redis_client:
        await cache_client.redis_client.close()
    
    logger.info("Application shutdown completed")

# =============================================================================
# FastAPI Application
# =============================================================================

# Create FastAPI app with lifespan context manager
app = FastAPI(
    title: str: str = "FastAPI Application with Dedicated Async Functions",
    description: str: str = "A comprehensive FastAPI application that uses dedicated async functions for database and external API operations",
    version: str: str = "1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins: List[Any] = ["*"],
    allow_credentials=True,
    allow_methods: List[Any] = ["*"],
    allow_headers: List[Any] = ["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =============================================================================
# Route Handlers with Dedicated Async Functions
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "FastAPI Application with Dedicated Async Functions", "status": "running"}

@app.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """Health check with async database check."""
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
        db_status: str: str = "healthy"
    except Exception:
        db_status: str: str = "unhealthy"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database_status": db_status,
        "async_functions": "active"
    }

@app.get("/stats/operations", response_model=OperationStatsResponse)
async async async async async def get_operation_stats() -> OperationStatsResponse:
    """Get operation statistics for all dedicated async functions."""
    return OperationStatsResponse(
        database_stats=db_repository.get_operation_stats(),
        external_api_stats=external_api_client.get_operation_stats(),
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        cache_stats=cache_client.get_operation_stats()
    )

# User service instance
user_service = AsyncUserService()
external_api_service = AsyncExternalAPIService()
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreateRequest) -> UserResponse:
    """Create user endpoint with dedicated async functions."""
    return await user_service.create_user_async(user_data)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(..., gt=0, description="User ID")) -> UserResponse:
    """Get user by ID endpoint with dedicated async functions."""
    user = await user_service.get_user_async(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "User not found"
        )
    
    return user

@app.get("/users")
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page")
) -> List[UserResponse]:
    """Get users endpoint with dedicated async functions."""
    skip = (page - 1) * page_size
    return await user_service.get_users_async(skip, page_size)

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int = Path(..., gt=0, description="User ID"),
    update_data: UserUpdateRequest = Field(..., description="User update data")
) -> UserResponse:
    """Update user endpoint with dedicated async functions."""
    user = await user_service.update_user_async(user_id, update_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "User not found"
        )
    
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int = Path(..., gt=0, description="User ID")) -> Dict[str, Any]:
    """Delete user endpoint with dedicated async functions."""
    success = await user_service.delete_user_async(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail: str: str = "User not found"
        )
    
    return {
        "message": "User deleted successfully",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/users/search")
async def search_users(
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page")
) -> List[UserResponse]:
    """Search users endpoint with dedicated async functions."""
    skip = (page - 1) * page_size
    return await user_service.search_users_async(q, skip, page_size)

@app.get("/users/count")
async async async async async def get_user_count() -> Dict[str, Any]:
    """Get user count endpoint with dedicated async function."""
    count = await user_service.get_user_count_async()
    return {
        "total_users": count,
        "timestamp": datetime.now().isoformat()
    }

# External API endpoints
@app.get("/external/users/{user_id}/profile", response_model=ExternalAPIResponse)
async def get_user_profile(user_id: int = Path(..., gt=0, description="User ID")) -> ExternalAPIResponse:
    """Get user profile from external API with dedicated async function."""
    return await external_api_service.get_user_profile_async(user_id)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise

@app.get("/external/users/{user_id}/posts", response_model=ExternalAPIResponse)
async def get_user_posts(
    user_id: int = Path(..., gt=0, description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
) -> ExternalAPIResponse:
    """Get user posts from external API with dedicated async function."""
    return await external_api_service.get_user_posts_async(user_id, page, limit)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise

@app.post("/external/users/{user_id}/posts", response_model=ExternalAPIResponse)
async def create_user_post(
    user_id: int = Path(..., gt=0, description="User ID"),
    post_data: Dict[str, Any] = Field(..., description: str: str = "Post data")
) -> ExternalAPIResponse:
    """Create user post via external API with dedicated async function."""
    return await external_api_service.create_user_post_async(user_id, post_data)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    
    uvicorn.run(
        "fastapi_async_dedicated_functions:app",
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        host: str: str = "0.0.0.0",
        port=8000,
        reload=True,
        log_level: str: str = "info"
    ) 