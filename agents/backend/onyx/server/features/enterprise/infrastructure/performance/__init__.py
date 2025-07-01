"""
Performance Optimization Layer
=============================

Ultra-high performance optimizations for enterprise API:
- Ultra-fast serialization (orjson, msgpack)
- Multi-level caching (L1/L2/L3)
- Response compression (Brotli, Gzip)
- Connection pooling
- Memory optimization
- Database query optimization
- CDN integration
- Async performance boosters
"""

from .ultra_serializer import (
    UltraSerializer,
    FastJSONSerializer,
    MsgPackSerializer,
    ProtobufSerializer
)

from .multi_cache import (
    MultiLevelCache,
    L1MemoryCache,
    L2RedisCache,
    L3DiskCache,
    CacheStrategy
)

from .compression import (
    ResponseCompressor,
    BrotliCompressor,
    GzipCompressor,
    LZ4Compressor
)

from .connection_pool import (
    ConnectionPoolManager,
    RedisConnectionPool,
    DatabaseConnectionPool,
    HTTPConnectionPool
)

from .memory_optimizer import (
    MemoryOptimizer,
    ObjectPoolManager,
    GarbageCollectionOptimizer
)

from .async_optimizer import (
    AsyncOptimizer,
    UVLoopOptimizer,
    BatchProcessor,
    ConcurrencyLimiter
)

from .database_optimizer import (
    DatabaseOptimizer,
    QueryOptimizer,
    IndexManager,
    ReadReplicaManager
)

from .cdn_integration import (
    CDNManager,
    CloudflareIntegration,
    AWSCloudFrontIntegration
)

from .profiler import (
    PerformanceProfiler,
    MemoryProfiler,
    QueryProfiler,
    ResponseTimeTracker
)

__all__ = [
    # Serialization
    "UltraSerializer",
    "FastJSONSerializer", 
    "MsgPackSerializer",
    "ProtobufSerializer",
    
    # Caching
    "MultiLevelCache",
    "L1MemoryCache",
    "L2RedisCache", 
    "L3DiskCache",
    "CacheStrategy",
    
    # Compression
    "ResponseCompressor",
    "BrotliCompressor",
    "GzipCompressor",
    "LZ4Compressor",
    
    # Connection Pooling
    "ConnectionPoolManager",
    "RedisConnectionPool",
    "DatabaseConnectionPool",
    "HTTPConnectionPool",
    
    # Memory Optimization
    "MemoryOptimizer",
    "ObjectPoolManager",
    "GarbageCollectionOptimizer",
    
    # Async Optimization
    "AsyncOptimizer",
    "UVLoopOptimizer",
    "BatchProcessor",
    "ConcurrencyLimiter",
    
    # Database Optimization
    "DatabaseOptimizer",
    "QueryOptimizer",
    "IndexManager",
    "ReadReplicaManager",
    
    # CDN Integration
    "CDNManager",
    "CloudflareIntegration",
    "AWSCloudFrontIntegration",
    
    # Profiling
    "PerformanceProfiler",
    "MemoryProfiler",
    "QueryProfiler",
    "ResponseTimeTracker",
] 