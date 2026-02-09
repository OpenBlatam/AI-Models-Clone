#!/usr/bin/env python3
"""
🚀 Unified Database Manager - Consolidated Database Connection System
====================================================================

Consolidates all database connections into a single, optimized system
that eliminates connection conflicts and provides consistent connection
management across all database types.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum, auto
from contextlib import asynccontextmanager
import structlog
from datetime import datetime, timedelta

# Database drivers
try:
    import aioredis
    from aioredis import Redis, ConnectionPool
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

try:
    import motor.motor_asyncio
    from pymongo import MongoClient
    HAS_MONGODB = True
except ImportError:
    HAS_MONGODB = False

try:
    import asyncpg
    from asyncpg import Pool, Connection
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

try:
    import aiomysql
    from aiomysql import Pool as MySQLPool
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

try:
    import aiosqlite
    HAS_SQLITE = True
except ImportError:
    HAS_SQLITE = False

logger = structlog.get_logger()

# =============================================================================
# Database Types and Configuration
# =============================================================================

class DatabaseType(Enum):
    """Supported database types."""
    REDIS = "redis"
    POSTGRES = "postgres"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    SQLITE = "sqlite"

class ConnectionStatus(Enum):
    """Connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    POOL_FULL = "pool_full"

@dataclass
class DatabaseConfig:
    """Database configuration."""
    database_type: DatabaseType
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Redis specific
    redis_db: int = 0
    redis_decode_responses: bool = True
    
    # MongoDB specific
    mongodb_auth_source: str = "admin"
    
    # PostgreSQL specific
    postgres_ssl_mode: str = "prefer"
    
    # MySQL specific
    mysql_charset: str = "utf8mb4"

@dataclass
class ConnectionMetrics:
    """Connection performance metrics."""
    total_connections: int
    active_connections: int
    idle_connections: int
    connection_errors: int
    avg_response_time_ms: float
    last_used: datetime
    created_at: datetime = field(default_factory=datetime.now)

# =============================================================================
# Connection Pool Base
# =============================================================================

T = TypeVar('T')

class BaseConnectionPool(Generic[T]):
    """Base class for connection pools."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[T] = None
        self.status = ConnectionStatus.DISCONNECTED
        self.metrics = ConnectionMetrics(
            total_connections=0,
            active_connections=0,
            idle_connections=0,
            connection_errors=0,
            avg_response_time_ms=0.0,
            last_used=datetime.now()
        )
        self.connection_times: List[float] = []
        self.error_count = 0
        self.last_error: Optional[Exception] = None
    
    async def initialize(self) -> bool:
        """Initialize the connection pool."""
        try:
            self.status = ConnectionStatus.CONNECTING
            await self._create_pool()
            self.status = ConnectionStatus.CONNECTED
            logger.info(f"Database pool initialized: {self.config.database_type.value}")
            return True
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = e
            self.error_count += 1
            logger.error(f"Failed to initialize database pool: {e}")
            return False
    
    async def _create_pool(self):
        """Create the connection pool. Override in subclasses."""
        raise NotImplementedError
    
    async def get_connection(self):
        """Get a connection from the pool. Override in subclasses."""
        raise NotImplementedError
    
    async def return_connection(self, connection):
        """Return a connection to the pool. Override in subclasses."""
        raise NotImplementedError
    
    async def close(self):
        """Close the connection pool."""
        if self.pool:
            await self._close_pool()
            self.status = ConnectionStatus.DISCONNECTED
            logger.info(f"Database pool closed: {self.config.database_type.value}")
    
    async def _close_pool(self):
        """Close the pool. Override in subclasses."""
        raise NotImplementedError
    
    def update_metrics(self, response_time_ms: float, error: bool = False):
        """Update connection metrics."""
        self.metrics.last_used = datetime.now()
        self.connection_times.append(response_time_ms)
        
        if error:
            self.metrics.connection_errors += 1
            self.error_count += 1
        
        # Keep only last 100 measurements
        if len(self.connection_times) > 100:
            self.connection_times = self.connection_times[-100:]
        
        # Update average response time
        if self.connection_times:
            self.metrics.avg_response_time_ms = sum(self.connection_times) / len(self.connection_times)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get pool health status."""
        return {
            "status": self.status.value,
            "config": {
                "type": self.config.database_type.value,
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database
            },
            "metrics": {
                "total_connections": self.metrics.total_connections,
                "active_connections": self.metrics.active_connections,
                "idle_connections": self.metrics.idle_connections,
                "connection_errors": self.metrics.connection_errors,
                "avg_response_time_ms": self.metrics.avg_response_time_ms,
                "last_used": self.metrics.last_used.isoformat(),
                "created_at": self.metrics.created_at.isoformat()
            },
            "errors": {
                "count": self.error_count,
                "last_error": str(self.last_error) if self.last_error else None
            }
        }

# =============================================================================
# Redis Connection Pool
# =============================================================================

class RedisConnectionPool(BaseConnectionPool[Redis]):
    """Redis connection pool implementation."""
    
    async def _create_pool(self):
        """Create Redis connection pool."""
        if not HAS_REDIS:
            raise ImportError("aioredis is not installed")
        
        # Create connection pool
        pool = ConnectionPool.from_url(
            f"redis://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.redis_db}",
            max_connections=self.config.pool_size + self.config.max_overflow,
            decode_responses=self.config.redis_decode_responses,
            timeout=self.config.timeout,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        redis = Redis(connection_pool=pool)
        await redis.ping()
        await redis.close()
        
        self.pool = pool
        self.metrics.total_connections = self.config.pool_size + self.config.max_overflow
    
    async def get_connection(self) -> Redis:
        """Get Redis connection."""
        if not self.pool:
            raise RuntimeError("Redis pool not initialized")
        
        start_time = time.time()
        try:
            redis = Redis(connection_pool=self.pool)
            # Test connection
            await redis.ping()
            
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time)
            
            return redis
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time, error=True)
            raise
    
    async def return_connection(self, connection: Redis):
        """Return Redis connection to pool."""
        try:
            await connection.close()
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")
    
    async def _close_pool(self):
        """Close Redis pool."""
        if self.pool:
            await self.pool.disconnect()

# =============================================================================
# PostgreSQL Connection Pool
# =============================================================================

class PostgresConnectionPool(BaseConnectionPool[Pool]):
    """PostgreSQL connection pool implementation."""
    
    async def _create_pool(self):
        """Create PostgreSQL connection pool."""
        if not HAS_POSTGRES:
            raise ImportError("asyncpg is not installed")
        
        # Create connection pool
        self.pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            user=self.config.username,
            password=self.config.password,
            database=self.config.database,
            min_size=5,
            max_size=self.config.pool_size + self.config.max_overflow,
            command_timeout=self.config.timeout,
            server_settings={
                'ssl': self.config.postgres_ssl_mode != 'disable'
            }
        )
        
        # Test connection
        async with self.pool.acquire() as conn:
            await conn.execute('SELECT 1')
        
        self.metrics.total_connections = self.config.pool_size + self.config.max_overflow
    
    async def get_connection(self) -> Connection:
        """Get PostgreSQL connection."""
        if not self.pool:
            raise RuntimeError("PostgreSQL pool not initialized")
        
        start_time = time.time()
        try:
            connection = await self.pool.acquire()
            
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time)
            
            return connection
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time, error=True)
            raise
    
    async def return_connection(self, connection: Connection):
        """Return PostgreSQL connection to pool."""
        try:
            await self.pool.release(connection)
        except Exception as e:
            logger.warning(f"Error releasing PostgreSQL connection: {e}")
    
    async def _close_pool(self):
        """Close PostgreSQL pool."""
        if self.pool:
            await self.pool.close()

# =============================================================================
# MongoDB Connection Pool
# =============================================================================

class MongoDBConnectionPool(BaseConnectionPool[motor.motor_asyncio.AsyncIOMotorClient]):
    """MongoDB connection pool implementation."""
    
    async def _create_pool(self):
        """Create MongoDB connection pool."""
        if not HAS_MONGODB:
            raise ImportError("motor is not installed")
        
        # Create connection string
        if self.config.username and self.config.password:
            connection_string = f"mongodb://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?authSource={self.config.mongodb_auth_source}"
        else:
            connection_string = f"mongodb://{self.config.host}:{self.config.port}/{self.config.database}"
        
        # Create client
        self.pool = motor.motor_asyncio.AsyncIOMotorClient(
            connection_string,
            maxPoolSize=self.config.pool_size + self.config.max_overflow,
            serverSelectionTimeoutMS=self.config.timeout * 1000,
            connectTimeoutMS=self.config.timeout * 1000,
            socketTimeoutMS=self.config.timeout * 1000
        )
        
        # Test connection
        await self.pool.admin.command('ping')
        
        self.metrics.total_connections = self.config.pool_size + self.config.max_overflow
    
    async def get_connection(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        """Get MongoDB client."""
        if not self.pool:
            raise RuntimeError("MongoDB client not initialized")
        
        start_time = time.time()
        try:
            # Test connection
            await self.pool.admin.command('ping')
            
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time)
            
            return self.pool
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time, error=True)
            raise
    
    async def return_connection(self, connection: motor.motor_asyncio.AsyncIOMotorClient):
        """MongoDB connections are managed by the client."""
        pass
    
    async def _close_pool(self):
        """Close MongoDB client."""
        if self.pool:
            self.pool.close()

# =============================================================================
# MySQL Connection Pool
# =============================================================================

class MySQLConnectionPool(BaseConnectionPool[MySQLPool]):
    """MySQL connection pool implementation."""
    
    async def _create_pool(self):
        """Create MySQL connection pool."""
        if not HAS_MYSQL:
            raise ImportError("aiomysql is not installed")
        
        # Create connection pool
        self.pool = await aiomysql.create_pool(
            host=self.config.host,
            port=self.config.port,
            user=self.config.username,
            password=self.config.password,
            db=self.config.database,
            charset=self.config.mysql_charset,
            autocommit=True,
            maxsize=self.config.pool_size + self.config.max_overflow,
            minsize=5,
            echo=False
        )
        
        # Test connection
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute('SELECT 1')
        
        self.metrics.total_connections = self.config.pool_size + self.config.max_overflow
    
    async def get_connection(self) -> Any:
        """Get MySQL connection."""
        if not self.pool:
            raise RuntimeError("MySQL pool not initialized")
        
        start_time = time.time()
        try:
            connection = await self.pool.acquire()
            
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time)
            
            return connection
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time, error=True)
            raise
    
    async def return_connection(self, connection: Any):
        """Return MySQL connection to pool."""
        try:
            self.pool.release(connection)
        except Exception as e:
            logger.warning(f"Error releasing MySQL connection: {e}")
    
    async def _close_pool(self):
        """Close MySQL pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

# =============================================================================
# SQLite Connection Pool
# =============================================================================

class SQLiteConnectionPool(BaseConnectionPool[aiosqlite.Connection]):
    """SQLite connection pool implementation."""
    
    async def _create_pool(self):
        """Create SQLite connection pool."""
        if not HAS_SQLITE:
            raise ImportError("aiosqlite is not installed")
        
        # SQLite doesn't need a traditional pool, but we'll create a connection
        # and manage it as a single connection for simplicity
        self.pool = await aiosqlite.connect(self.config.database)
        
        # Test connection
        async with self.pool.execute('SELECT 1'):
            pass
        
        self.metrics.total_connections = 1
    
    async def get_connection(self) -> aiosqlite.Connection:
        """Get SQLite connection."""
        if not self.pool:
            raise RuntimeError("SQLite connection not initialized")
        
        start_time = time.time()
        try:
            # Test connection
            async with self.pool.execute('SELECT 1'):
                pass
            
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time)
            
            return self.pool
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.update_metrics(response_time, error=True)
            raise
    
    async def return_connection(self, connection: aiosqlite.Connection):
        """SQLite connections are managed by the connection object."""
        pass
    
    async def _close_pool(self):
        """Close SQLite connection."""
        if self.pool:
            await self.pool.close()

# =============================================================================
# Unified Database Manager
# =============================================================================

class UnifiedDatabaseManager:
    """
    🚀 Unified Database Manager - Single source of truth for database connections.
    
    Consolidates all database connections and eliminates the scattered
    implementations that were causing connection conflicts.
    """
    
    def __init__(self):
        self.pools: Dict[DatabaseType, BaseConnectionPool] = {}
        self.configs: Dict[DatabaseType, DatabaseConfig] = {}
        self.initialized = False
        self.health_check_interval = 60  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
    
    async def add_database(self, config: DatabaseConfig) -> bool:
        """Add a database configuration and initialize its pool."""
        try:
            # Create appropriate pool based on database type
            if config.database_type == DatabaseType.REDIS:
                pool = RedisConnectionPool(config)
            elif config.database_type == DatabaseType.POSTGRES:
                pool = PostgresConnectionPool(config)
            elif config.database_type == DatabaseType.MONGODB:
                pool = MongoDBConnectionPool(config)
            elif config.database_type == DatabaseType.MYSQL:
                pool = MySQLConnectionPool(config)
            elif config.database_type == DatabaseType.SQLITE:
                pool = SQLiteConnectionPool(config)
            else:
                raise ValueError(f"Unsupported database type: {config.database_type}")
            
            # Initialize the pool
            success = await pool.initialize()
            if success:
                self.pools[config.database_type] = pool
                self.configs[config.database_type] = config
                logger.info(f"Database added successfully: {config.database_type.value}")
                return True
            else:
                logger.error(f"Failed to add database: {config.database_type.value}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding database {config.database_type.value}: {e}")
            return False
    
    async def get_connection(self, database_type: DatabaseType):
        """Get a connection from the specified database pool."""
        if database_type not in self.pools:
            raise ValueError(f"Database {database_type.value} not configured")
        
        pool = self.pools[database_type]
        return await pool.get_connection()
    
    async def return_connection(self, database_type: DatabaseType, connection):
        """Return a connection to the specified database pool."""
        if database_type not in self.pools:
            logger.warning(f"Attempting to return connection to unconfigured database: {database_type.value}")
            return
        
        pool = self.pools[database_type]
        await pool.return_connection(connection)
    
    @asynccontextmanager
    async def get_connection_context(self, database_type: DatabaseType):
        """Context manager for database connections."""
        connection = None
        try:
            connection = await self.get_connection(database_type)
            yield connection
        finally:
            if connection:
                await self.return_connection(database_type, connection)
    
    async def execute_query(self, database_type: DatabaseType, query: str, params: tuple = None) -> Any:
        """Execute a query on the specified database."""
        async with self.get_connection_context(database_type) as conn:
            if database_type == DatabaseType.REDIS:
                # Redis specific query execution
                if params:
                    return await conn.execute(query, *params)
                else:
                    return await conn.execute(query)
            
            elif database_type == DatabaseType.POSTGRES:
                # PostgreSQL specific query execution
                if params:
                    return await conn.fetch(query, *params)
                else:
                    return await conn.fetch(query)
            
            elif database_type == DatabaseType.MONGODB:
                # MongoDB specific query execution
                # This is a simplified example - you'd need to implement based on your needs
                db = conn[self.configs[database_type].database]
                return await db.command(query)
            
            elif database_type == DatabaseType.MYSQL:
                # MySQL specific query execution
                async with conn.cursor() as cur:
                    if params:
                        await cur.execute(query, params)
                    else:
                        await cur.execute(query)
                    return await cur.fetchall()
            
            elif database_type == DatabaseType.SQLITE:
                # SQLite specific query execution
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                return await cursor.fetchall()
    
    async def start_health_monitoring(self):
        """Start health monitoring for all database pools."""
        if self.health_check_task:
            return
        
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Database health monitoring started")
    
    async def stop_health_monitoring(self):
        """Stop health monitoring."""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
            logger.info("Database health monitoring stopped")
    
    async def _health_check_loop(self):
        """Health check loop for all database pools."""
        while True:
            try:
                for db_type, pool in self.pools.items():
                    try:
                        # Test connection
                        async with self.get_connection_context(db_type) as conn:
                            if db_type == DatabaseType.REDIS:
                                await conn.ping()
                            elif db_type == DatabaseType.POSTGRES:
                                await conn.execute('SELECT 1')
                            elif db_type == DatabaseType.MONGODB:
                                await conn.admin.command('ping')
                            elif db_type == DatabaseType.MYSQL:
                                async with conn.cursor() as cur:
                                    await cur.execute('SELECT 1')
                            elif db_type == DatabaseType.SQLITE:
                                await conn.execute('SELECT 1')
                        
                        # Update pool status
                        if pool.status != ConnectionStatus.CONNECTED:
                            pool.status = ConnectionStatus.CONNECTED
                            logger.info(f"Database {db_type.value} connection restored")
                    
                    except Exception as e:
                        pool.status = ConnectionStatus.ERROR
                        pool.last_error = e
                        logger.warning(f"Database {db_type.value} health check failed: {e}")
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(10)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all database pools."""
        status = {
            "manager_status": "healthy" if self.initialized else "initializing",
            "total_databases": len(self.pools),
            "databases": {}
        }
        
        for db_type, pool in self.pools.items():
            status["databases"][db_type.value] = pool.get_health_status()
        
        return status
    
    async def close_all(self):
        """Close all database connections."""
        logger.info("Closing all database connections...")
        
        # Stop health monitoring
        await self.stop_health_monitoring()
        
        # Close all pools
        for db_type, pool in self.pools.items():
            try:
                await pool.close()
                logger.info(f"Closed {db_type.value} pool")
            except Exception as e:
                logger.error(f"Error closing {db_type.value} pool: {e}")
        
        self.pools.clear()
        self.configs.clear()
        self.initialized = False
        logger.info("All database connections closed")

# =============================================================================
# Global Instance and Utilities
# =============================================================================

# Global database manager instance
_database_manager: Optional[UnifiedDatabaseManager] = None

def get_database_manager() -> UnifiedDatabaseManager:
    """Get or create global database manager instance."""
    global _database_manager
    if _database_manager is None:
        _database_manager = UnifiedDatabaseManager()
    return _database_manager

async def add_database(config: DatabaseConfig) -> bool:
    """Add database to global manager."""
    return await get_database_manager().add_database(config)

async def get_database_connection(database_type: DatabaseType):
    """Get database connection from global manager."""
    return await get_database_manager().get_connection(database_type)

async def execute_database_query(database_type: DatabaseType, query: str, params: tuple = None) -> Any:
    """Execute query on global database manager."""
    return await get_database_manager().execute_query(database_type, query, params)

def get_database_health() -> Dict[str, Any]:
    """Get database health from global manager."""
    return get_database_manager().get_health_status()

# =============================================================================
# Example Usage
# =============================================================================

async def example_usage():
    """Example of how to use the unified database manager."""
    
    # Create database configurations
    redis_config = DatabaseConfig(
        database_type=DatabaseType.REDIS,
        host="localhost",
        port=6379,
        password="",
        database="",
        pool_size=10
    )
    
    postgres_config = DatabaseConfig(
        database_type=DatabaseType.POSTGRES,
        host="localhost",
        port=5432,
        username="postgres",
        password="password",
        database="mydb",
        pool_size=20
    )
    
    # Get database manager
    db_manager = get_database_manager()
    
    try:
        # Add databases
        await db_manager.add_database(redis_config)
        await db_manager.add_database(postgres_config)
        
        # Start health monitoring
        await db_manager.start_health_monitoring()
        
        # Use Redis
        async with db_manager.get_connection_context(DatabaseType.REDIS) as redis:
            await redis.set("test_key", "test_value")
            value = await redis.get("test_key")
            print(f"Redis test: {value}")
        
        # Use PostgreSQL
        async with db_manager.get_connection_context(DatabaseType.POSTGRES) as pg:
            result = await pg.fetch("SELECT version()")
            print(f"PostgreSQL version: {result[0]['version']}")
        
        # Get health status
        health = db_manager.get_health_status()
        print(f"Database health: {health}")
        
    finally:
        # Clean up
        await db_manager.close_all()

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
