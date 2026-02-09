"""
Utilities Module
================

Utilidades avanzadas para resiliencia, performance y seguridad.
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerState
from .retry import retry, RetryConfig, ExponentialBackoff
from .rate_limiter import RateLimiter, TokenBucket, SlidingWindow
from .health_check import HealthChecker, HealthStatus
from .graceful_shutdown import GracefulShutdown, shutdown_handler
from .connection_pool import ConnectionPool, PoolConfig
from .cache import Cache, CacheBackend, InMemoryCache, CacheConfig
from .metrics import MetricsCollector, MetricType, Metric, default_metrics
from .batching import BatchProcessor, RequestBatcher, BatchConfig
from .distributed_lock import DistributedLock, LockBackend, RedisLockBackend
from .feature_flags import FeatureFlagManager, FeatureFlag, FeatureFlagType, default_feature_flags

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerState",
    "retry",
    "RetryConfig",
    "ExponentialBackoff",
    "RateLimiter",
    "TokenBucket",
    "SlidingWindow",
    "HealthChecker",
    "HealthStatus",
    "GracefulShutdown",
    "shutdown_handler",
    "ConnectionPool",
    "PoolConfig",
    "Cache",
    "CacheBackend",
    "InMemoryCache",
    "CacheConfig",
    "MetricsCollector",
    "MetricType",
    "Metric",
    "default_metrics",
    "BatchProcessor",
    "RequestBatcher",
    "BatchConfig",
    "DistributedLock",
    "LockBackend",
    "RedisLockBackend",
    "FeatureFlagManager",
    "FeatureFlag",
    "FeatureFlagType",
    "default_feature_flags",
]

