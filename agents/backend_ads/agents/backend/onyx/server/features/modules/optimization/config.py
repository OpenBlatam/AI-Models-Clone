"""
Optimization Configuration Module.

Centralized configuration for high-performance system optimization.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
import os

from pydantic import BaseSettings, Field, validator
from decouple import config


class OptimizationLevel(str, Enum):
    """Optimization levels from basic to quantum performance."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ULTRA = "ultra"
    QUANTUM = "quantum"


class SerializationFormat(str, Enum):
    """Supported serialization formats."""
    JSON = "json"
    ORJSON = "orjson"
    MSGPACK = "msgpack"
    AUTO = "auto"


class OptimizationSettings(BaseSettings):
    """Comprehensive optimization settings."""
    
    # Core settings
    optimization_level: OptimizationLevel = Field(default=OptimizationLevel.ADVANCED)
    max_workers: int = Field(default=min(32, os.cpu_count() * 2))
    
    # Serialization
    serialization_format: SerializationFormat = Field(default=SerializationFormat.AUTO)
    enable_compression: bool = Field(default=True)
    compression_level: int = Field(default=1)
    
    # Cache settings
    enable_caching: bool = Field(default=True)
    l1_cache_size: int = Field(default=10000)
    l2_cache_size: int = Field(default=100000)
    cache_ttl: int = Field(default=3600)
    redis_url: Optional[str] = Field(default=None)
    
    # Database settings
    db_pool_size: int = Field(default=50)
    db_timeout: float = Field(default=5.0)
    enable_query_caching: bool = Field(default=True)
    
    # Network settings
    max_connections: int = Field(default=1000)
    connection_timeout: float = Field(default=30.0)
    enable_http2: bool = Field(default=True)
    
    # Memory settings
    memory_pool_size_mb: int = Field(default=2048)
    memory_threshold_percent: float = Field(default=85.0)
    enable_gc_optimization: bool = Field(default=True)
    
    # Performance settings
    enable_jit: bool = Field(default=True)
    enable_gpu: bool = Field(default=False)
    enable_monitoring: bool = Field(default=True)
    monitoring_interval: float = Field(default=1.0)
    
    # Thresholds
    max_response_time_ms: float = Field(default=1000.0)
    max_cpu_usage_percent: float = Field(default=90.0)
    
    @validator('max_workers')
    def validate_max_workers(cls, v):
        if v < 1 or v > 256:
            raise ValueError("max_workers must be between 1 and 256")
        return v
    
    @validator('memory_threshold_percent')
    def validate_memory_threshold(cls, v):
        if not 50.0 <= v <= 95.0:
            raise ValueError("memory_threshold_percent must be between 50.0 and 95.0")
        return v
    
    def get_effective_config(self) -> Dict[str, Any]:
        """Get effective configuration based on available libraries."""
        # Check library availability
        try:
            import orjson
            orjson_available = True
        except ImportError:
            orjson_available = False
        
        try:
            import msgpack
            msgpack_available = True
        except ImportError:
            msgpack_available = False
        
        try:
            import xxhash
            xxhash_available = True
        except ImportError:
            xxhash_available = False
        
        try:
            import numba
            numba_available = True
        except ImportError:
            numba_available = False
        
        # Determine effective serialization
        effective_serialization = self.serialization_format
        if effective_serialization == SerializationFormat.AUTO:
            if orjson_available:
                effective_serialization = SerializationFormat.ORJSON
            elif msgpack_available:
                effective_serialization = SerializationFormat.MSGPACK
            else:
                effective_serialization = SerializationFormat.JSON
        
        return {
            "optimization_level": self.optimization_level.value,
            "effective_serialization": effective_serialization.value,
            "libraries_available": {
                "orjson": orjson_available,
                "msgpack": msgpack_available,
                "xxhash": xxhash_available,
                "numba": numba_available
            },
            "performance_settings": {
                "max_workers": self.max_workers,
                "memory_pool_mb": self.memory_pool_size_mb,
                "db_pool_size": self.db_pool_size
            }
        }
    
    class Config:
        env_prefix = "OPT_"
        env_file = ".env"


# Export main components
__all__ = [
    "OptimizationSettings",
    "OptimizationLevel",
    "SerializationFormat"
] 