#!/usr/bin/env python3
"""
Ultra-Optimized Core Module for HeyGen AI
==========================================

This module provides the core functionality with:
- High-performance data processing using Polars and Vaex
- Advanced caching with Redis and in-memory optimization
- Async-first architecture with connection pooling
- Performance monitoring and profiling
- Modern Python features and optimizations
"""

import asyncio
import functools
import logging
import time
import warnings
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import weakref

# Performance-focused imports
import polars as pl
import vaex
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import structlog
from loguru import logger
import psutil
import asyncio_mqtt as aiomqtt
from redis.asyncio import Redis
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Performance monitoring
try:
    import py_spy
    PY_SPY_AVAILABLE = True
except ImportError:
    PY_SPY_AVAILABLE = False

try:
    from memory_profiler import profile as memory_profile
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False

try:
    from pyinstrument import Profiler
    PYINSTRUMENT_AVAILABLE = True
except ImportError:
    PYINSTRUMENT_AVAILABLE = False

# =============================================================================
# Configuration Classes
# =============================================================================

class PerformanceConfig(BaseSettings):
    """Performance configuration with environment variable support."""
    
    # Cache settings
    cache_ttl: int = Field(default=300, env="CACHE_TTL")
    max_cache_size: int = Field(default=10000, env="MAX_CACHE_SIZE")
    enable_redis_cache: bool = Field(default=True, env="ENABLE_REDIS_CACHE")
    
    # Database settings
    max_db_connections: int = Field(default=20, env="MAX_DB_CONNECTIONS")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    # Processing settings
    max_workers: int = Field(default=os.cpu_count(), env="MAX_WORKERS")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    enable_parallel_processing: bool = Field(default=True, env="ENABLE_PARALLEL_PROCESSING")
    
    # Monitoring settings
    enable_profiling: bool = Field(default=False, env="ENABLE_PROFILING")
    enable_memory_profiling: bool = Field(default=False, env="ENABLE_MEMORY_PROFILING")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# =============================================================================
# Performance Monitoring
# =============================================================================

class PerformanceMonitor:
    """High-performance monitoring and profiling."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
        
    @contextmanager
    def profile(self, name: str):
        """Context manager for profiling code blocks."""
        if not self.config.enable_profiling:
            yield
            return
            
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            if name not in self.metrics:
                self.metrics[name] = []
            
            self.metrics[name].append(duration)
            
            logger.info(f"Profile: {name}", 
                       duration=f"{duration:.4f}s", 
                       memory_delta=f"{memory_delta:.2f}MB")
    
    def start_timer(self, name: str):
        """Start a timer for a named operation."""
        self.start_times[name] = time.perf_counter()
    
    def end_timer(self, name: str) -> float:
        """End a timer and return duration."""
        if name not in self.start_times:
            return 0.0
        
        duration = time.perf_counter() - self.start_times[name]
        del self.start_times[name]
        
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)
        
        return duration
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a named operation."""
        if name not in self.metrics:
            return {}
        
        values = self.metrics[name]
        return {
            "count": len(values),
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "total": np.sum(values)
        }

# =============================================================================
# High-Performance Cache
# =============================================================================

class UltraCache:
    """Ultra-high-performance caching system."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.memory_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, float] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.redis_client: Optional[Redis] = None
        
        # LRU cache implementation
        self._lru_cache: Dict[str, Any] = {}
        self._lru_order: List[str] = []
        
    async def initialize_redis(self, redis_url: str):
        """Initialize Redis connection for distributed caching."""
        if self.config.enable_redis_cache:
            try:
                self.redis_client = Redis.from_url(redis_url)
                await self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis cache initialization failed: {e}")
                self.redis_client = None
    
    def _cleanup_lru_cache(self):
        """Clean up LRU cache when it exceeds max size."""
        while len(self._lru_cache) > self.config.max_cache_size:
            oldest_key = self._lru_order.pop(0)
            del self._lru_cache[oldest_key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with LRU optimization."""
        # Check memory cache first
        if key in self.memory_cache:
            if self._is_cache_valid(key):
                self.cache_hits += 1
                # Update LRU order
                if key in self._lru_order:
                    self._lru_order.remove(key)
                self._lru_order.append(key)
                return self.memory_cache[key]
            else:
                del self.memory_cache[key]
                del self.cache_timestamps[key]
        
        self.cache_misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL."""
        ttl = ttl or self.config.cache_ttl
        
        self.memory_cache[key] = value
        self.cache_timestamps[key] = time.time() + ttl
        
        # Update LRU cache
        if key in self._lru_order:
            self._lru_order.remove(key)
        self._lru_order.append(key)
        self._lru_cache[key] = value
        
        self._cleanup_lru_cache()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached value is still valid."""
        if key not in self.cache_timestamps:
            return False
        return time.time() < self.cache_timestamps[key]
    
    async def get_redis(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                self.cache_hits += 1
                return value
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
        
        self.cache_misses += 1
        return None
    
    async def set_redis(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in Redis cache."""
        if not self.redis_client:
            return
        
        ttl = ttl or self.config.cache_ttl
        
        try:
            await self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "memory_cache_size": len(self.memory_cache),
            "lru_cache_size": len(self._lru_cache)
        }

# =============================================================================
# High-Performance Data Processing
# =============================================================================

class DataProcessor:
    """High-performance data processing using Polars and Vaex."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
    
    def process_with_polars(self, data: Union[List[Dict], pd.DataFrame]) -> pl.DataFrame:
        """Process data using Polars for extreme performance."""
        if isinstance(data, list):
            # Convert list of dicts to Polars DataFrame
            df = pl.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            # Convert pandas to Polars
            df = pl.from_pandas(data)
        else:
            raise ValueError("Unsupported data type")
        
        return df
    
    def process_with_vaex(self, data: Union[List[Dict], pd.DataFrame, pl.DataFrame]) -> vaex.DataFrame:
        """Process data using Vaex for out-of-memory operations."""
        if isinstance(data, list):
            # Convert to pandas first, then to vaex
            df = pd.DataFrame(data)
        elif isinstance(data, pl.DataFrame):
            # Convert Polars to pandas, then to vaex
            df = data.to_pandas()
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("Unsupported data type")
        
        return vaex.from_pandas(df)
    
    async def process_chunked(self, data: List[Any], processor: Callable) -> List[Any]:
        """Process data in chunks with parallel execution."""
        if not self.config.enable_parallel_processing:
            return [processor(item) for item in data]
        
        chunks = [data[i:i + self.config.chunk_size] 
                 for i in range(0, len(data), self.config.chunk_size)]
        
        loop = asyncio.get_event_loop()
        tasks = []
        
        for chunk in chunks:
            task = loop.run_in_executor(self.executor, 
                                      lambda c: [processor(item) for item in c], 
                                      chunk)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]
    
    def optimize_dataframe(self, df: pl.DataFrame) -> pl.DataFrame:
        """Optimize Polars DataFrame for better performance."""
        # Use lazy evaluation for better performance
        return df.lazy().collect()
    
    def memory_efficient_processing(self, df: pl.DataFrame, 
                                  operations: List[Callable]) -> pl.DataFrame:
        """Process DataFrame with memory efficiency."""
        result = df
        
        for operation in operations:
            result = operation(result)
            # Force garbage collection periodically
            if hasattr(result, 'collect'):
                result = result.collect()
        
        return result

# =============================================================================
# Async Database Manager
# =============================================================================

class AsyncDatabaseManager:
    """High-performance async database manager."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.redis_client: Optional[Redis] = None
    
    async def initialize_postgres(self, connection_string: str):
        """Initialize PostgreSQL connection pool."""
        try:
            self.postgres_pool = await asyncpg.create_pool(
                connection_string,
                min_size=5,
                max_size=self.config.max_db_connections,
                command_timeout=self.config.db_pool_timeout
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {e}")
            raise
    
    async def initialize_mongo(self, connection_string: str):
        """Initialize MongoDB async client."""
        try:
            self.mongo_client = AsyncIOMotorClient(connection_string)
            await self.mongo_client.admin.command('ping')
            logger.info("MongoDB connection initialized")
        except Exception as e:
            logger.error(f"MongoDB initialization failed: {e}")
            raise
    
    async def initialize_redis(self, connection_string: str):
        """Initialize Redis connection."""
        try:
            self.redis_client = Redis.from_url(connection_string)
            await self.redis_client.ping()
            logger.info("Redis connection initialized")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise
    
    @asynccontextmanager
    async def get_postgres_connection(self):
        """Get PostgreSQL connection from pool."""
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL not initialized")
        
        async with self.postgres_pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> List[Dict]:
        """Execute PostgreSQL query with connection pooling."""
        async with self.get_postgres_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute_many(self, query: str, args_list: List[Tuple]) -> None:
        """Execute multiple queries efficiently."""
        async with self.get_postgres_connection() as conn:
            await conn.executemany(query, args_list)
    
    async def close(self):
        """Close all database connections."""
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.redis_client:
            await self.redis_client.close()

# =============================================================================
# Main Application Class
# =============================================================================

class HeyGenAICore:
    """Main application core with all optimizations."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.monitor = PerformanceMonitor(config)
        self.cache = UltraCache(config)
        self.data_processor = DataProcessor(config)
        self.db_manager = AsyncDatabaseManager(config)
        
        # Performance tracking
        self.start_time = time.time()
        self.operation_count = 0
    
    async def initialize(self, 
                        redis_url: Optional[str] = None,
                        postgres_url: Optional[str] = None,
                        mongo_url: Optional[str] = None):
        """Initialize all components."""
        with self.monitor.profile("initialization"):
            if redis_url:
                await self.cache.initialize_redis(redis_url)
                await self.db_manager.initialize_redis(redis_url)
            
            if postgres_url:
                await self.db_manager.initialize_postgres(postgres_url)
            
            if mongo_url:
                await self.db_manager.initialize_mongo(mongo_url)
    
    async def process_data(self, data: List[Dict]) -> pl.DataFrame:
        """Process data with full optimization pipeline."""
        with self.monitor.profile("data_processing"):
            # Check cache first
            cache_key = f"data_processing_{hash(str(data))}"
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            # Process with Polars for maximum performance
            result = self.data_processor.process_with_polars(data)
            
            # Cache the result
            self.cache.set(cache_key, result)
            
            self.operation_count += 1
            return result
    
    async def close(self):
        """Cleanup and close all resources."""
        await self.db_manager.close()
        
        # Log final statistics
        total_time = time.time() - self.start_time
        logger.info("Application shutdown", 
                   total_time=f"{total_time:.2f}s",
                   operations=self.operation_count,
                   ops_per_second=f"{self.operation_count/total_time:.2f}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            "uptime": time.time() - self.start_time,
            "operations": self.operation_count,
            "cache_stats": self.cache.get_stats(),
            "monitor_stats": {name: self.monitor.get_stats(name) 
                             for name in self.monitor.metrics.keys()}
        }

# =============================================================================
# Utility Functions
# =============================================================================

def async_retry(max_retries: int = 3, delay: float = 1.0):
    """Decorator for async retry logic."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
            
            raise last_exception
        
        return wrapper
    return decorator

def memory_efficient(func):
    """Decorator for memory-efficient function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if MEMORY_PROFILER_AVAILABLE:
            return memory_profile(func)(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper

def profile_function(name: str = None):
    """Decorator for function profiling."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if PYINSTRUMENT_AVAILABLE:
                profiler = Profiler()
                with profiler:
                    result = func(*args, **kwargs)
                profiler.print()
                return result
            return func(*args, **kwargs)
        return wrapper
    return decorator

# =============================================================================
# Main execution
# =============================================================================

async def main():
    """Main execution function."""
    config = PerformanceConfig()
    app = HeyGenAICore(config)
    
    try:
        await app.initialize()
        logger.info("HeyGen AI Core initialized successfully")
        
        # Example usage
        sample_data = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        result = await app.process_data(sample_data)
        logger.info(f"Processed {len(result)} records")
        
        # Get performance stats
        stats = app.get_performance_stats()
        logger.info("Performance stats", **stats)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        await app.close()

if __name__ == "__main__":
    asyncio.run(main())
