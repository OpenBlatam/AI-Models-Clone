"""
Database Optimizer - Ultra-High Performance Database Operations.

Specialized optimizer for database operations with advanced connection pooling,
query optimization, caching, and ultra-fast data access patterns.
"""

import asyncio
import time
import hashlib
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
import logging

# Core database imports
import asyncpg
import aioredis
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import text

# High-performance imports
try:
    import orjson
    JSON_AVAILABLE = True
except ImportError:
    import json as orjson
    JSON_AVAILABLE = False

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database optimization configuration."""
    # Connection pool settings
    pool_size: int = 20
    max_overflow: int = 50
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    
    # Query optimization
    enable_query_cache: bool = True
    cache_ttl_seconds: int = 300
    enable_prepared_statements: bool = True
    
    # Async settings
    connection_timeout: float = 30.0
    command_timeout: float = 60.0
    server_settings: Dict[str, str] = None
    
    # Performance settings
    fetch_size: int = 10000
    enable_compression: bool = True
    enable_streaming: bool = True
    
    def __post_init__(self):
        if self.server_settings is None:
            self.server_settings = {
                'jit': 'on',
                'shared_preload_libraries': 'pg_stat_statements',
                'track_activity_query_size': '16384',
                'wal_compression': 'on'
            }


class QueryCache:
    """Ultra-fast query result cache."""
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        self.redis_client = redis_client
        self.local_cache: Dict[str, Tuple[Any, float]] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def _generate_cache_key(self, query: str, params: Dict = None) -> str:
        """Generate optimized cache key."""
        if XXHASH_AVAILABLE:
            key_data = f"{query}:{params}" if params else query
            return f"query:{xxhash.xxh64(key_data.encode()).hexdigest()}"
        else:
            key_data = f"{query}:{params}".encode() if params else query.encode()
            return f"query:{hashlib.md5(key_data).hexdigest()}"
    
    async def get(self, query: str, params: Dict = None, ttl: int = 300) -> Optional[Any]:
        """Get cached query result."""
        cache_key = self._generate_cache_key(query, params)
        
        # Try Redis first
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    self.cache_stats["hits"] += 1
                    return orjson.loads(cached_data) if JSON_AVAILABLE else orjson.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis cache get failed: {e}")
        
        # Fallback to local cache
        if cache_key in self.local_cache:
            result, timestamp = self.local_cache[cache_key]
            if time.time() - timestamp < ttl:
                self.cache_stats["hits"] += 1
                return result
            else:
                # Expired
                del self.local_cache[cache_key]
                self.cache_stats["evictions"] += 1
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set(self, query: str, result: Any, params: Dict = None, ttl: int = 300):
        """Cache query result."""
        cache_key = self._generate_cache_key(query, params)
        
        # Store in Redis
        if self.redis_client:
            try:
                serialized = orjson.dumps(result) if JSON_AVAILABLE else orjson.dumps(result)
                await self.redis_client.setex(cache_key, ttl, serialized)
            except Exception as e:
                logger.warning(f"Redis cache set failed: {e}")
        
        # Store in local cache (with size limit)
        if len(self.local_cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(self.local_cache.keys())[:100]
            for key in oldest_keys:
                del self.local_cache[key]
                self.cache_stats["evictions"] += 1
        
        self.local_cache[cache_key] = (result, time.time())


class ConnectionPoolOptimizer:
    """Advanced database connection pool optimizer."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pools: Dict[str, Any] = {}
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "pool_hits": 0,
            "pool_misses": 0
        }
    
    async def create_asyncpg_pool(self, dsn: str) -> asyncpg.Pool:
        """Create optimized asyncpg connection pool."""
        return await asyncpg.create_pool(
            dsn,
            min_size=self.config.pool_size // 4,
            max_size=self.config.pool_size,
            max_queries=50000,  # Maximum queries per connection
            max_inactive_connection_lifetime=self.config.pool_recycle,
            timeout=self.config.connection_timeout,
            command_timeout=self.config.command_timeout,
            server_settings=self.config.server_settings
        )
    
    def create_sqlalchemy_engine(self, dsn: str) -> sqlalchemy.engine.Engine:
        """Create optimized SQLAlchemy engine."""
        return create_async_engine(
            dsn,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_pre_ping=self.config.pool_pre_ping,
            pool_recycle=self.config.pool_recycle,
            echo=False,  # Disable for performance
            future=True,
            execution_options={
                "isolation_level": "READ_COMMITTED",
                "compiled_cache": {}  # Enable query compilation cache
            }
        )
    
    async def get_connection(self, pool_name: str):
        """Get optimized database connection."""
        if pool_name not in self.pools:
            raise ValueError(f"Pool {pool_name} not found")
        
        pool = self.pools[pool_name]
        
        try:
            if hasattr(pool, 'acquire'):  # asyncpg pool
                connection = await pool.acquire()
                self.connection_stats["pool_hits"] += 1
                self.connection_stats["active_connections"] += 1
                return connection
            else:  # SQLAlchemy engine
                session = AsyncSession(pool)
                self.connection_stats["pool_hits"] += 1
                return session
        except Exception as e:
            self.connection_stats["pool_misses"] += 1
            logger.error(f"Failed to acquire connection from pool {pool_name}: {e}")
            raise


class QueryOptimizer:
    """Advanced query optimization and execution."""
    
    def __init__(self, cache: QueryCache, config: DatabaseConfig):
        self.cache = cache
        self.config = config
        self.prepared_statements: Dict[str, Any] = {}
        self.query_stats = {
            "total_queries": 0,
            "cached_queries": 0,
            "avg_query_time": 0.0,
            "slow_queries": 0
        }
    
    async def execute_optimized(
        self, 
        connection: Any, 
        query: str, 
        params: Dict = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ) -> Any:
        """Execute query with comprehensive optimizations."""
        start_time = time.time()
        self.query_stats["total_queries"] += 1
        
        # Try cache first
        if use_cache and self.config.enable_query_cache:
            cached_result = await self.cache.get(query, params, cache_ttl)
            if cached_result is not None:
                self.query_stats["cached_queries"] += 1
                return cached_result
        
        # Execute query
        try:
            if hasattr(connection, 'fetch'):  # asyncpg connection
                result = await self._execute_asyncpg(connection, query, params)
            else:  # SQLAlchemy session
                result = await self._execute_sqlalchemy(connection, query, params)
            
            # Cache result
            if use_cache and self.config.enable_query_cache:
                await self.cache.set(query, result, params, cache_ttl)
            
            # Update stats
            execution_time = time.time() - start_time
            self.query_stats["avg_query_time"] = (
                self.query_stats["avg_query_time"] + execution_time
            ) / 2
            
            if execution_time > 1.0:  # Slow query threshold
                self.query_stats["slow_queries"] += 1
                logger.warning(f"Slow query detected: {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def _execute_asyncpg(self, connection: asyncpg.Connection, query: str, params: Dict = None):
        """Execute query using asyncpg with optimizations."""
        if params:
            # Use prepared statements for parameterized queries
            if self.config.enable_prepared_statements:
                stmt_key = hashlib.md5(query.encode()).hexdigest()
                if stmt_key not in self.prepared_statements:
                    self.prepared_statements[stmt_key] = await connection.prepare(query)
                
                prepared_stmt = self.prepared_statements[stmt_key]
                return await prepared_stmt.fetch(*params.values())
            else:
                return await connection.fetch(query, *params.values())
        else:
            return await connection.fetch(query)
    
    async def _execute_sqlalchemy(self, session: AsyncSession, query: str, params: Dict = None):
        """Execute query using SQLAlchemy with optimizations."""
        stmt = text(query)
        
        if params:
            result = await session.execute(stmt, params)
        else:
            result = await session.execute(stmt)
        
        return result.fetchall()
    
    async def execute_batch_optimized(
        self, 
        connection: Any, 
        queries: List[Tuple[str, Dict]], 
        batch_size: int = 100
    ) -> List[Any]:
        """Execute multiple queries in optimized batches."""
        results = []
        
        # Process queries in batches
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            
            # Execute batch concurrently
            batch_tasks = [
                self.execute_optimized(connection, query, params, use_cache=False)
                for query, params in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
        
        return results


class DataFrameOptimizer:
    """Optimize data processing using Polars and DuckDB."""
    
    def __init__(self):
        self.use_polars = POLARS_AVAILABLE
        self.use_duckdb = DUCKDB_AVAILABLE
        
        if self.use_duckdb:
            self.duckdb_conn = duckdb.connect()
    
    def optimize_dataframe_operations(self, data: List[Dict], operations: List[str]) -> Any:
        """Optimize data processing operations."""
        if self.use_polars:
            return self._polars_operations(data, operations)
        elif self.use_duckdb:
            return self._duckdb_operations(data, operations)
        else:
            return self._pandas_fallback(data, operations)
    
    def _polars_operations(self, data: List[Dict], operations: List[str]) -> pl.DataFrame:
        """Use Polars for ultra-fast data operations."""
        df = pl.DataFrame(data)
        
        for operation in operations:
            if operation == "group_by_count":
                df = df.group_by("category").count()
            elif operation == "filter_active":
                df = df.filter(pl.col("status") == "active")
            elif operation == "sort_by_date":
                df = df.sort("created_at", descending=True)
            # Add more operations as needed
        
        return df
    
    def _duckdb_operations(self, data: List[Dict], operations: List[str]) -> Any:
        """Use DuckDB for analytical operations."""
        # Convert to DuckDB
        self.duckdb_conn.register('temp_table', data)
        
        # Build optimized query
        query = "SELECT * FROM temp_table"
        
        for operation in operations:
            if operation == "group_by_count":
                query = "SELECT category, COUNT(*) FROM temp_table GROUP BY category"
            elif operation == "filter_active":
                query += " WHERE status = 'active'"
            elif operation == "sort_by_date":
                query += " ORDER BY created_at DESC"
        
        return self.duckdb_conn.execute(query).fetchall()
    
    def _pandas_fallback(self, data: List[Dict], operations: List[str]) -> Any:
        """Fallback to pandas if specialized libraries not available."""
        import pandas as pd
        
        df = pd.DataFrame(data)
        
        for operation in operations:
            if operation == "group_by_count":
                df = df.groupby("category").size().reset_index(name='count')
            elif operation == "filter_active":
                df = df[df["status"] == "active"]
            elif operation == "sort_by_date":
                df = df.sort_values("created_at", ascending=False)
        
        return df


class DatabaseOptimizer:
    """Main database optimizer coordinating all components."""
    
    def __init__(self, config: DatabaseConfig = None, redis_client: aioredis.Redis = None):
        self.config = config or DatabaseConfig()
        self.cache = QueryCache(redis_client)
        self.pool_optimizer = ConnectionPoolOptimizer(self.config)
        self.query_optimizer = QueryOptimizer(self.cache, self.config)
        self.dataframe_optimizer = DataFrameOptimizer()
        
        self.metrics = {
            "optimization_level": "ULTRA",
            "features_enabled": {
                "query_cache": self.config.enable_query_cache,
                "prepared_statements": self.config.enable_prepared_statements,
                "polars_available": POLARS_AVAILABLE,
                "duckdb_available": DUCKDB_AVAILABLE,
                "connection_pooling": True
            }
        }
    
    async def initialize(self, database_configs: Dict[str, str]) -> Dict[str, bool]:
        """Initialize database optimizer with multiple database connections."""
        results = {}
        
        for name, dsn in database_configs.items():
            try:
                if dsn.startswith('postgresql'):
                    # AsyncPG pool for PostgreSQL
                    pool = await self.pool_optimizer.create_asyncpg_pool(dsn)
                    self.pool_optimizer.pools[f"{name}_asyncpg"] = pool
                    results[f"{name}_asyncpg"] = True
                    
                    # SQLAlchemy engine
                    engine = self.pool_optimizer.create_sqlalchemy_engine(dsn)
                    self.pool_optimizer.pools[f"{name}_sqlalchemy"] = engine
                    results[f"{name}_sqlalchemy"] = True
                else:
                    # Generic SQLAlchemy engine
                    engine = self.pool_optimizer.create_sqlalchemy_engine(dsn)
                    self.pool_optimizer.pools[name] = engine
                    results[name] = True
                    
            except Exception as e:
                logger.error(f"Failed to initialize database {name}: {e}")
                results[name] = False
        
        logger.info("Database optimizer initialized", 
                   pools=len(self.pool_optimizer.pools),
                   features=self.metrics["features_enabled"])
        
        return results
    
    @asynccontextmanager
    async def get_optimized_connection(self, pool_name: str):
        """Get optimized database connection with automatic cleanup."""
        connection = None
        
        try:
            connection = await self.pool_optimizer.get_connection(pool_name)
            yield connection
        finally:
            if connection:
                if hasattr(connection, 'close'):
                    await connection.close()
                self.pool_optimizer.connection_stats["active_connections"] -= 1
    
    async def execute_query(
        self, 
        pool_name: str, 
        query: str, 
        params: Dict = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ) -> Any:
        """Execute optimized database query."""
        async with self.get_optimized_connection(pool_name) as connection:
            return await self.query_optimizer.execute_optimized(
                connection, query, params, use_cache, cache_ttl
            )
    
    async def execute_analytics_query(
        self, 
        pool_name: str, 
        query: str, 
        params: Dict = None,
        optimize_dataframe: bool = True
    ) -> Any:
        """Execute analytical query with dataframe optimization."""
        result = await self.execute_query(pool_name, query, params, use_cache=False)
        
        if optimize_dataframe and isinstance(result, list):
            # Convert to optimized dataframe operations
            if hasattr(result[0], '_asdict'):  # Named tuple rows
                data = [row._asdict() for row in result]
            else:
                data = result
            
            return self.dataframe_optimizer.optimize_dataframe_operations(
                data, ["sort_by_date", "filter_active"]
            )
        
        return result
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            "cache_stats": self.cache.cache_stats,
            "connection_stats": self.pool_optimizer.connection_stats,
            "query_stats": self.query_optimizer.query_stats,
            "config": {
                "pool_size": self.config.pool_size,
                "cache_enabled": self.config.enable_query_cache,
                "prepared_statements": self.config.enable_prepared_statements
            },
            "features": self.metrics["features_enabled"]
        }
    
    async def cleanup(self):
        """Cleanup database resources."""
        for pool_name, pool in self.pool_optimizer.pools.items():
            try:
                if hasattr(pool, 'close'):
                    await pool.close()
                logger.info(f"Closed database pool: {pool_name}")
            except Exception as e:
                logger.error(f"Error closing pool {pool_name}: {e}")
        
        if hasattr(self.dataframe_optimizer, 'duckdb_conn'):
            self.dataframe_optimizer.duckdb_conn.close()


__all__ = [
    'DatabaseOptimizer',
    'DatabaseConfig',
    'QueryCache',
    'ConnectionPoolOptimizer',
    'QueryOptimizer',
    'DataFrameOptimizer'
] 