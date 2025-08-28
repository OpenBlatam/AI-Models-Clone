from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Set, Optional, Tuple, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from collections import defaultdict, deque
import json
import statistics
from datetime import datetime, timedelta
import weakref
import threading
from concurrent.futures import ThreadPoolExecutor
import functools
from typing import Any, List, Dict, Optional
"""
Async utility functions for high-throughput scanning and enumeration.
Provides connection pooling, rate limiting, performance monitoring, and async helpers.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PerformanceMetrics:
    """Performance metrics for async operations."""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    last_operation_time: datetime = field(default_factory=datetime.now)
    
    def add_operation(self, success: bool, response_time: float):
        """Add operation result to metrics."""
        self.total_operations += 1
        self.total_response_time += response_time
        self.response_times.append(response_time)
        self.last_operation_time = datetime.now()
        
        if success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1
        
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_operations == 0:
            return 0.0
        return self.successful_operations / self.total_operations
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        if self.total_operations == 0:
            return 0.0
        return self.total_response_time / self.total_operations
    
    @property
    def median_response_time(self) -> float:
        """Calculate median response time."""
        if not self.response_times:
            return 0.0
        return statistics.median(self.response_times)
    
    @property
    def operations_per_second(self) -> float:
        """Calculate operations per second."""
        duration = (datetime.now() - self.start_time).total_seconds()
        if duration == 0:
            return 0.0
        return self.total_operations / duration
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": self.success_rate,
            "average_response_time": self.average_response_time,
            "median_response_time": self.median_response_time,
            "min_response_time": self.min_response_time if self.min_response_time != float('inf') else 0.0,
            "max_response_time": self.max_response_time,
            "operations_per_second": self.operations_per_second,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds()
        }


class AsyncRateLimiter:
    """Advanced rate limiter with token bucket algorithm."""
    
    def __init__(self, rate_per_second: int, burst_size: int = None):
        
    """__init__ function."""
self.rate_per_second = rate_per_second
        self.burst_size = burst_size or rate_per_second
        self.tokens = self.burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens from the rate limiter."""
        async with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            self.tokens = min(
                self.burst_size,
                self.tokens + time_passed * self.rate_per_second
            )
            
            if self.tokens < tokens:
                # Need to wait
                wait_time = (tokens - self.tokens) / self.rate_per_second
                self.tokens = 0
                self.last_update = now + wait_time
                return wait_time
            
            self.tokens -= tokens
            self.last_update = now
            return 0.0
    
    async def wait_if_needed(self, tokens: int = 1):
        """Wait if rate limit is exceeded."""
        wait_time = await self.acquire(tokens)
        if wait_time > 0:
            await asyncio.sleep(wait_time)


class AsyncConnectionPool:
    """Generic async connection pool with automatic cleanup."""
    
    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 10):
        
    """__init__ function."""
self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.connections: Dict[str, Any] = {}
        self.connection_semaphores: Dict[str, asyncio.Semaphore] = defaultdict(
            lambda: asyncio.Semaphore(max_connections_per_host)
        )
        self.global_semaphore = asyncio.Semaphore(max_connections)
        self.cleanup_task: Optional[asyncio.Task] = None
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "connection_reuses": 0,
            "connection_errors": 0
        }
    
    async def get_connection(self, key: str, factory: Callable, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Get or create a connection from the pool."""
        async with self.global_semaphore:
            async with self.connection_semaphores[key]:
                if key in self.connections:
                    conn = self.connections[key]
                    if self._is_connection_valid(conn):
                        self.stats["connection_reuses"] += 1
                        return conn
                
                # Create new connection
                try:
                    conn = await factory(*args, **kwargs)
                    self.connections[key] = conn
                    self.stats["total_connections"] += 1
                    self.stats["active_connections"] += 1
                    return conn
                except Exception as e:
                    self.stats["connection_errors"] += 1
                    raise
    
    def _is_connection_valid(self, conn: Any) -> bool:
        """Check if connection is still valid."""
        # This is a generic implementation - subclasses should override
        try:
            if hasattr(conn, 'closed'):
                return not conn.closed
            elif hasattr(conn, 'is_closing'):
                return not conn.is_closing()
            else:
                return True
        except Exception:
            return False
    
    async def close_connection(self, key: str):
        """Close a specific connection."""
        if key in self.connections:
            conn = self.connections[key]
            try:
                if hasattr(conn, 'close'):
                    await conn.close()
                elif hasattr(conn, 'close'):
                    conn.close()
            except Exception:
                pass
            finally:
                del self.connections[key]
                self.stats["active_connections"] -= 1
    
    async def cleanup_invalid_connections(self) -> Any:
        """Clean up invalid connections."""
        invalid_keys = []
        for key, conn in self.connections.items():
            if not self._is_connection_valid(conn):
                invalid_keys.append(key)
        
        for key in invalid_keys:
            await self.close_connection(key)
    
    async def start_cleanup_task(self, interval: float = 60.0):
        """Start periodic cleanup task."""
        async def cleanup_loop():
            
    """cleanup_loop function."""
while True:
                await asyncio.sleep(interval)
                await self.cleanup_invalid_connections()
        
        self.cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def stop_cleanup_task(self) -> Any:
        """Stop periodic cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def close_all(self) -> Any:
        """Close all connections in the pool."""
        await self.stop_cleanup_task()
        
        for key in list(self.connections.keys()):
            await self.close_connection(key)
        
        self.stats["active_connections"] = 0


class AsyncTaskManager:
    """Manages async tasks with performance monitoring and error handling."""
    
    def __init__(self, max_concurrent_tasks: int = 100):
        
    """__init__ function."""
self.max_concurrent_tasks = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.metrics = PerformanceMetrics()
        self.active_tasks: Set[asyncio.Task] = set()
        self.completed_tasks: List[Dict[str, Any]] = []
    
    async def run_task(self, coro, task_name: str = None) -> Any:
        """Run a task with monitoring."""
        async with self.semaphore:
            start_time = time.time()
            task = asyncio.create_task(coro)
            self.active_tasks.add(task)
            
            try:
                result = await task
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                logger.error(f"Task {task_name} failed: {e}")
            finally:
                self.active_tasks.discard(task)
                response_time = time.time() - start_time
                self.metrics.add_operation(success, response_time)
                
                task_info = {
                    "name": task_name,
                    "success": success,
                    "response_time": response_time,
                    "error": error,
                    "timestamp": datetime.now()
                }
                self.completed_tasks.append(task_info)
            
            return result
    
    async def run_tasks(self, tasks: List[Tuple[Any, str]]) -> List[Any]:
        """Run multiple tasks concurrently."""
        coros = [self.run_task(coro, name) for coro, name in tasks]
        return await asyncio.gather(*coros, return_exceptions=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task manager statistics."""
        return {
            "metrics": self.metrics.get_summary(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks
        }


class AsyncRetryHandler:
    """Handles retries for async operations with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0):
        
    """__init__ function."""
self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    async def execute_with_retry(self, coro_func, *args, **kwargs) -> Any:
        """Execute coroutine with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    raise last_exception
                
                delay = min(
                    self.base_delay * (self.exponential_base ** attempt),
                    self.max_delay
                )
                
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
                await asyncio.sleep(delay)
        
        raise last_exception


class AsyncBatchProcessor:
    """Process items in batches with async operations."""
    
    def __init__(self, batch_size: int = 100, max_concurrent_batches: int = 10):
        
    """__init__ function."""
self.batch_size = batch_size
        self.max_concurrent_batches = max_concurrent_batches
        self.semaphore = asyncio.Semaphore(max_concurrent_batches)
        self.metrics = PerformanceMetrics()
    
    async def process_batch(self, items: List[Any], processor_func: Callable) -> List[Any]:
        """Process a batch of items."""
        async with self.semaphore:
            start_time = time.time()
            
            try:
                results = await asyncio.gather(
                    *[processor_func(item) for item in items],
                    return_exceptions=True
                )
                
                # Separate successful and failed results
                successful_results = []
                failed_results = []
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        failed_results.append((items[i], result))
                    else:
                        successful_results.append(result)
                
                response_time = time.time() - start_time
                success_rate = len(successful_results) / len(items) if items else 0
                
                self.metrics.add_operation(success_rate > 0.5, response_time)
                
                return successful_results
                
            except Exception as e:
                response_time = time.time() - start_time
                self.metrics.add_operation(False, response_time)
                raise
    
    async def process_all(self, items: List[Any], processor_func: Callable) -> List[Any]:
        """Process all items in batches."""
        all_results = []
        
        # Split items into batches
        batches = [
            items[i:i + self.batch_size] 
            for i in range(0, len(items), self.batch_size)
        ]
        
        # Process batches concurrently
        batch_tasks = [
            self.process_batch(batch, processor_func) 
            for batch in batches
        ]
        
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Combine results
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed: {result}")
            else:
                all_results.extend(result)
        
        return all_results


class AsyncCache:
    """Async cache with TTL and automatic cleanup."""
    
    def __init__(self, default_ttl: float = 300.0):
        
    """__init__ function."""
self.default_ttl = default_ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.lock = asyncio.Lock()
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self.cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: float = None):
        """Set value in cache with TTL."""
        if ttl is None:
            ttl = self.default_ttl
        
        async with self.lock:
            expiry = time.time() + ttl
            self.cache[key] = (value, expiry)
    
    async def delete(self, key: str):
        """Delete value from cache."""
        async with self.lock:
            self.cache.pop(key, None)
    
    async def clear(self) -> Any:
        """Clear all cache entries."""
        async with self.lock:
            self.cache.clear()
    
    async def cleanup_expired(self) -> Any:
        """Remove expired entries from cache."""
        current_time = time.time()
        async with self.lock:
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if current_time >= expiry
            ]
            for key in expired_keys:
                del self.cache[key]
    
    async def start_cleanup_task(self, interval: float = 60.0):
        """Start periodic cleanup task."""
        async def cleanup_loop():
            
    """cleanup_loop function."""
while True:
                await asyncio.sleep(interval)
                await self.cleanup_expired()
        
        self.cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def stop_cleanup_task(self) -> Any:
        """Stop periodic cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass


# Utility functions for common async operations
async def async_timeout(seconds: float):
    """Async timeout context manager."""
    return asyncio.timeout(seconds)


async def async_retry(max_retries: int = 3, delay: float = 1.0):
    """Async retry decorator."""
    def decorator(func) -> Any:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        raise last_exception
                    await asyncio.sleep(delay * (2 ** attempt))
            raise last_exception
        return wrapper
    return decorator


async def async_batch_process(items: List[Any], processor: Callable, 
                            batch_size: int = 100, max_concurrent: int = 10) -> List[Any]:
    """Process items in batches with async operations."""
    processor_instance = AsyncBatchProcessor(batch_size, max_concurrent)
    return await processor_instance.process_all(items, processor)


async def async_rate_limited_execution(tasks: List[Callable], 
                                     rate_per_second: int = 100) -> List[Any]:
    """Execute tasks with rate limiting."""
    rate_limiter = AsyncRateLimiter(rate_per_second)
    results = []
    
    for task in tasks:
        await rate_limiter.wait_if_needed()
        try:
            result = await task()
            results.append(result)
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            results.append(None)
    
    return results


async def async_monitor_performance(func: Callable, *args, **kwargs) -> Tuple[Any, Dict[str, Any]]:
    """Monitor performance of async function execution."""
    start_time = time.time()
    start_memory = None  # Could add memory monitoring here
    
    try:
        result = await func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    performance_data = {
        "execution_time": execution_time,
        "success": success,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }
    
    return result, performance_data


# Example usage and testing functions
async def demonstrate_async_helpers():
    """Demonstrate async helper utilities."""
    
    # Create task manager
    task_manager = AsyncTaskManager(max_concurrent_tasks=50)
    
    # Create rate limiter
    rate_limiter = AsyncRateLimiter(rate_per_second=100)
    
    # Create cache
    cache = AsyncCache(default_ttl=60.0)
    await cache.start_cleanup_task()
    
    # Example async function
    async def sample_task(task_id: int) -> str:
        await asyncio.sleep(0.1)  # Simulate work
        return f"Task {task_id} completed"
    
    # Run tasks with monitoring
    tasks = [(sample_task(i), f"task_{i}") for i in range(100)]
    results = await task_manager.run_tasks(tasks)
    
    # Get statistics
    stats = task_manager.get_stats()
    logger.info(f"Task manager stats: {stats}")
    
    # Cleanup
    await cache.stop_cleanup_task()
    
    return results, stats


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_async_helpers()) 