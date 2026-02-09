#!/usr/bin/env python3
"""
Unified Connection Pool Manager
Comprehensive database connection management with intelligent pooling
"""

import asyncio
import time
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
import aioredis
import asyncpg
import motor.motor_asyncio
from pymongo import MongoClient
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import redis
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class ConnectionType(Enum):
    """Types of database connections."""
    REDIS = "redis"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    SQLITE = "sqlite"

@dataclass
class ConnectionConfig:
    """Configuration for database connections."""
    name: str
    connection_type: ConnectionType
    host: str
    port: int
    database: str
    username: str
    password: str
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    pool_timeout: int = 30
    max_queries: int = 50000
    max_overflow: int = 10
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo: bool = False

@dataclass
class ConnectionMetrics:
    """Connection pool metrics."""
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_requests: int
    connection_errors: int
    avg_response_time: float
    last_used: float

class UnifiedConnectionPool:
    """
    Unified connection pool manager for multiple database types.
    """
    
    def __init__(self):
        self.pools: Dict[str, Any] = {}
        self.configs: Dict[str, ConnectionConfig] = {}
        self.metrics: Dict[str, ConnectionMetrics] = {}
        self.health_checkers: Dict[str, Callable] = {}
        self.connection_monitors: Dict[str, threading.Thread] = {}
        self.global_config = {
            "max_total_connections": 1000,
            "connection_timeout": 30,
            "health_check_interval": 60,
            "max_retries": 3,
            "retry_delay": 1
        }
        self._lock = threading.Lock()
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start connection monitoring."""
        for pool_name in self.pools.keys():
            self._start_pool_monitoring(pool_name)
    
    def _start_pool_monitoring(self, pool_name: str):
        """Start monitoring for a specific pool."""
        def monitor_pool():
            while pool_name in self.pools:
                try:
                    self._check_pool_health(pool_name)
                    time.sleep(self.global_config["health_check_interval"])
                except Exception as e:
                    logger.error(f"Pool monitoring error for {pool_name}: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=monitor_pool, daemon=True)
        thread.start()
        self.connection_monitors[pool_name] = thread
    
    def _check_pool_health(self, pool_name: str):
        """Check health of a connection pool."""
        try:
            pool = self.pools.get(pool_name)
            if not pool:
                return
            
            # Get pool metrics
            if hasattr(pool, 'size'):
                total = pool.size()
            elif hasattr(pool, '_pool'):
                total = len(pool._pool)
            else:
                total = 0
            
            if hasattr(pool, 'checkedin'):
                idle = pool.checkedin()
            elif hasattr(pool, '_pool'):
                idle = len([c for c in pool._pool if not c.in_use])
            else:
                idle = 0
            
            active = total - idle
            
            # Update metrics
            self.metrics[pool_name] = ConnectionMetrics(
                total_connections=total,
                active_connections=active,
                idle_connections=idle,
                waiting_requests=0,  # Would need queue monitoring
                connection_errors=0,  # Would need error tracking
                avg_response_time=0.0,  # Would need timing tracking
                last_used=time.time()
            )
            
            # Log warnings for unhealthy pools
            if active > total * 0.8:
                logger.warning(f"Pool {pool_name} is at {active/total*100:.1f}% capacity")
            
        except Exception as e:
            logger.error(f"Health check failed for pool {pool_name}: {e}")
    
    async def create_redis_pool(self, config: ConnectionConfig) -> aioredis.Redis:
        """Create Redis connection pool."""
        try:
            pool = await aioredis.from_url(
                f"redis://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}",
                max_connections=config.max_connections,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await pool.ping()
            
            self.pools[config.name] = pool
            self.configs[config.name] = config
            logger.info(f"Redis pool created: {config.name}")
            
            return pool
            
        except Exception as e:
            logger.error(f"Failed to create Redis pool {config.name}: {e}")
            raise
    
    async def create_postgresql_pool(self, config: ConnectionConfig) -> asyncpg.Pool:
        """Create PostgreSQL connection pool."""
        try:
            pool = await asyncpg.create_pool(
                host=config.host,
                port=config.port,
                user=config.username,
                password=config.password,
                database=config.database,
                min_size=config.min_connections,
                max_size=config.max_connections,
                command_timeout=config.connection_timeout
            )
            
            # Test connection
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            self.pools[config.name] = pool
            self.configs[config.name] = config
            logger.info(f"PostgreSQL pool created: {config.name}")
            
            return pool
            
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL pool {config.name}: {e}")
            raise
    
    async def create_mongodb_pool(self, config: ConnectionConfig) -> motor.motor_asyncio.AsyncIOMotorClient:
        """Create MongoDB connection pool."""
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
                f"mongodb://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}",
                maxPoolSize=config.max_connections,
                minPoolSize=config.min_connections,
                serverSelectionTimeoutMS=config.connection_timeout * 1000
            )
            
            # Test connection
            await client.admin.command('ping')
            
            self.pools[config.name] = client
            self.configs[config.name] = config
            logger.info(f"MongoDB pool created: {config.name}")
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB pool {config.name}: {e}")
            raise
    
    def create_sqlalchemy_pool(self, config: ConnectionConfig) -> QueuePool:
        """Create SQLAlchemy connection pool."""
        try:
            if config.connection_type == ConnectionType.POSTGRESQL:
                url = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            elif config.connection_type == ConnectionType.MYSQL:
                url = f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            elif config.connection_type == ConnectionType.SQLITE:
                url = f"sqlite:///{config.database}"
            else:
                raise ValueError(f"Unsupported connection type: {config.connection_type}")
            
            engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=config.max_connections,
                max_overflow=config.max_overflow,
                pool_timeout=config.pool_timeout,
                pool_recycle=config.pool_recycle,
                pool_pre_ping=config.pool_pre_ping,
                echo=config.echo
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            
            self.pools[config.name] = engine
            self.configs[config.name] = config
            logger.info(f"SQLAlchemy pool created: {config.name}")
            
            return engine
            
        except Exception as e:
            logger.error(f"Failed to create SQLAlchemy pool {config.name}: {e}")
            raise
    
    async def create_async_sqlalchemy_pool(self, config: ConnectionConfig) -> AsyncSession:
        """Create async SQLAlchemy connection pool."""
        try:
            if config.connection_type == ConnectionType.POSTGRESQL:
                url = f"postgresql+asyncpg://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            elif config.connection_type == ConnectionType.MYSQL:
                url = f"mysql+aiomysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
            else:
                raise ValueError(f"Unsupported async connection type: {config.connection_type}")
            
            engine = create_async_engine(
                url,
                pool_size=config.max_connections,
                max_overflow=config.max_overflow,
                pool_timeout=config.pool_timeout,
                pool_recycle=config.pool_recycle,
                pool_pre_ping=config.pool_pre_ping,
                echo=config.echo
            )
            
            # Test connection
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            session_factory = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            
            self.pools[config.name] = session_factory
            self.configs[config.name] = config
            logger.info(f"Async SQLAlchemy pool created: {config.name}")
            
            return session_factory
            
        except Exception as e:
            logger.error(f"Failed to create async SQLAlchemy pool {config.name}: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self, pool_name: str):
        """Get a connection from the pool with automatic cleanup."""
        pool = self.pools.get(pool_name)
        if not pool:
            raise ValueError(f"Pool {pool_name} not found")
        
        connection = None
        try:
            if isinstance(pool, aioredis.Redis):
                connection = pool
                yield connection
            elif isinstance(pool, asyncpg.Pool):
                async with pool.acquire() as conn:
                    connection = conn
                    yield connection
            elif isinstance(pool, motor.motor_asyncio.AsyncIOMotorClient):
                connection = pool
                yield connection
            elif hasattr(pool, 'connect'):
                # SQLAlchemy engine
                with pool.connect() as conn:
                    connection = conn
                    yield connection
            else:
                raise ValueError(f"Unsupported pool type: {type(pool)}")
                
        except Exception as e:
            logger.error(f"Connection error in pool {pool_name}: {e}")
            raise
        finally:
            # Update metrics
            if pool_name in self.metrics:
                self.metrics[pool_name].last_used = time.time()
    
    async def execute_query(self, pool_name: str, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a query on the specified pool."""
        async with self.get_connection(pool_name) as conn:
            if isinstance(conn, aioredis.Redis):
                # Redis query
                if query.startswith('GET'):
                    return await conn.get(params.get('key'))
                elif query.startswith('SET'):
                    return await conn.set(params.get('key'), params.get('value'))
                else:
                    return await conn.execute_command(query, *params.values() if params else [])
            
            elif hasattr(conn, 'execute'):
                # Database query
                if params:
                    return await conn.execute(query, params)
                else:
                    return await conn.execute(query)
            
            else:
                raise ValueError(f"Unsupported connection type: {type(conn)}")
    
    def get_pool_metrics(self, pool_name: str) -> Optional[ConnectionMetrics]:
        """Get metrics for a specific pool."""
        return self.metrics.get(pool_name)
    
    def get_all_metrics(self) -> Dict[str, ConnectionMetrics]:
        """Get metrics for all pools."""
        return self.metrics.copy()
    
    async def close_pool(self, pool_name: str):
        """Close a specific connection pool."""
        pool = self.pools.get(pool_name)
        if not pool:
            return
        
        try:
            if hasattr(pool, 'close'):
                await pool.close()
            elif hasattr(pool, 'dispose'):
                pool.dispose()
            
            del self.pools[pool_name]
            del self.configs[pool_name]
            if pool_name in self.metrics:
                del self.metrics[pool_name]
            
            logger.info(f"Pool {pool_name} closed")
            
        except Exception as e:
            logger.error(f"Error closing pool {pool_name}: {e}")
    
    async def close_all_pools(self):
        """Close all connection pools."""
        pool_names = list(self.pools.keys())
        for pool_name in pool_names:
            await self.close_pool(pool_name)
        
        logger.info("All connection pools closed")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get status of all pools."""
        status = {}
        for pool_name, pool in self.pools.items():
            metrics = self.metrics.get(pool_name)
            config = self.configs.get(pool_name)
            
            status[pool_name] = {
                "type": config.connection_type.value if config else "unknown",
                "host": config.host if config else "unknown",
                "database": config.database if config else "unknown",
                "total_connections": metrics.total_connections if metrics else 0,
                "active_connections": metrics.active_connections if metrics else 0,
                "idle_connections": metrics.idle_connections if metrics else 0,
                "last_used": metrics.last_used if metrics else 0
            }
        
        return status

# Global connection pool manager
connection_manager = UnifiedConnectionPool()

def get_connection_manager() -> UnifiedConnectionPool:
    """Get the global connection manager instance."""
    return connection_manager

# Decorator for connection management
def with_connection(pool_name: str):
    """Decorator to manage database connections."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with connection_manager.get_connection(pool_name) as conn:
                return await func(conn, *args, **kwargs)
        return wrapper
    return decorator 