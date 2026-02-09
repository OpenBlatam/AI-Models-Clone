"""
Ultra-Fast Performance Optimization Module
Enterprise-grade performance optimizations for maximum speed
"""

from .async_optimizer import AsyncOptimizer, get_async_optimizer, async_cache, parallelize
from .serialization_optimizer import SerializationOptimizer, get_serializer
from .response_optimizer import ResponseOptimizer, get_response_optimizer
from .connection_pool import ConnectionPoolManager, get_connection_pool
from .request_batcher import RequestBatcher, get_request_batcher
from .memory_optimizer import MemoryOptimizer, get_memory_optimizer

__all__ = [
    "AsyncOptimizer",
    "get_async_optimizer",
    "async_cache",
    "parallelize",
    "SerializationOptimizer",
    "get_serializer",
    "ResponseOptimizer",
    "get_response_optimizer",
    "ConnectionPoolManager",
    "get_connection_pool",
    "RequestBatcher",
    "get_request_batcher",
    "MemoryOptimizer",
    "get_memory_optimizer",
]















