"""
Redis Utilities - Onyx Integration
Utility functions for Redis operations in Onyx.
"""
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
import json
import pickle
from datetime import datetime, timedelta
import redis
from functools import wraps
import logging
from pydantic import BaseModel
import time
from .redis_config import RedisConfig, get_config

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class RedisUtils:
    """Utility functions for Redis operations."""
    
    def __init__(self, config: Optional[RedisConfig] = None):
        """Initialize Redis utilities with configuration."""
        self.config = config or get_config()
        self.redis = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password,
            max_connections=self.config.max_connections,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.socket_connect_timeout,
            decode_responses=True
        )
    
    def _retry_operation(self, operation: callable, *args, **kwargs) -> Any:
        """Retry a Redis operation with exponential backoff."""
        for attempt in range(self.config.max_retries):
            try:
                return operation(*args, **kwargs)
            except redis.RedisError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                delay = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"Redis operation failed, retrying in {delay}s: {e}")
                time.sleep(delay)
    
    def _serialize(self, data: Any) -> str:
        """Serialize data for Redis storage."""
        if isinstance(data, BaseModel):
            return data.model_dump_json()
        return json.dumps(data, cls=DateTimeEncoder)
    
    def _deserialize(self, data: str, model_class: Optional[type[T]] = None) -> Any:
        """Deserialize data from Redis storage."""
        if not data:
            return None
        if model_class:
            return model_class.model_validate_json(data)
        return json.loads(data)
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a Redis key with prefix and identifier."""
        return f"onyx:{prefix}:{identifier}"
    
    def cache_data(self, data: Any, prefix: str, identifier: str, 
                  expire: Optional[int] = None) -> None:
        """Cache data in Redis with retry mechanism."""
        key = self._generate_key(prefix, identifier)
        try:
            serialized_data = self._serialize(data)
            self._retry_operation(
                self.redis.set,
                key,
                serialized_data,
                ex=expire or self.config.default_expire
            )
            logger.debug(f"Cached data {prefix}:{identifier}")
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            raise
    
    def get_cached_data(self, prefix: str, identifier: str, 
                       model_class: Optional[type[T]] = None) -> Optional[Any]:
        """Retrieve cached data from Redis with retry mechanism."""
        key = self._generate_key(prefix, identifier)
        try:
            data = self._retry_operation(self.redis.get, key)
            if data:
                return self._deserialize(data, model_class)
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached data: {e}")
            return None
    
    def cache_batch(self, data_dict: Dict[str, Any], prefix: str, 
                   expire: Optional[int] = None) -> None:
        """Cache multiple data items in Redis with pipeline."""
        try:
            with self.redis.pipeline() as pipe:
                for identifier, data in data_dict.items():
                    key = self._generate_key(prefix, identifier)
                    serialized_data = self._serialize(data)
                    pipe.set(key, serialized_data)
                    if expire:
                        pipe.expire(key, expire)
                pipe.execute()
            logger.debug(f"Cached batch data for {prefix}")
        except Exception as e:
            logger.error(f"Error caching batch data: {e}")
            raise
    
    def get_cached_batch(self, prefix: str, identifiers: List[str], 
                        model_class: Optional[type[T]] = None) -> Dict[str, Any]:
        """Retrieve multiple cached data items from Redis with pipeline."""
        try:
            with self.redis.pipeline() as pipe:
                for identifier in identifiers:
                    key = self._generate_key(prefix, identifier)
                    pipe.get(key)
                results = pipe.execute()
            
            return {
                identifier: self._deserialize(data, model_class)
                for identifier, data in zip(identifiers, results)
                if data is not None
            }
        except Exception as e:
            logger.error(f"Error retrieving batch data: {e}")
            return {}
    
    def delete_batch(self, prefix: str, identifiers: List[str]) -> None:
        """Delete multiple keys from Redis with pipeline."""
        try:
            with self.redis.pipeline() as pipe:
                for identifier in identifiers:
                    key = self._generate_key(prefix, identifier)
                    pipe.delete(key)
                pipe.execute()
            logger.debug(f"Deleted batch keys for {prefix}")
        except Exception as e:
            logger.error(f"Error deleting batch keys: {e}")
            raise
    
    def scan_keys(self, prefix: str, pattern: str = "*") -> List[str]:
        """Scan Redis keys with a specific prefix and pattern."""
        try:
            cursor = 0
            keys = []
            while True:
                cursor, found_keys = self._retry_operation(
                    self.redis.scan,
                    cursor,
                    match=f"onyx:{prefix}:{pattern}"
                )
                keys.extend(found_keys)
                if cursor == 0:
                    break
            return keys
        except Exception as e:
            logger.error(f"Error scanning keys: {e}")
            return []
    
    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics from Redis."""
        try:
            info = self._retry_operation(self.redis.info, "memory")
            return {
                "used_memory": info["used_memory"],
                "used_memory_peak": info["used_memory_peak"],
                "used_memory_lua": info["used_memory_lua"],
                "used_memory_scripts": info["used_memory_scripts"]
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics."""
        try:
            info = self._retry_operation(self.redis.info)
            return {
                "clients": info["clients"],
                "memory": info["memory"],
                "stats": info["stats"],
                "replication": info["replication"]
            }
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {}
    
    def delete_key(self, prefix: str, identifier: str) -> None:
        """Delete a single key from Redis."""
        key = self._generate_key(prefix, identifier)
        try:
            self._retry_operation(self.redis.delete, key)
            logger.debug(f"Deleted key {prefix}:{identifier}")
        except Exception as e:
            logger.error(f"Error deleting key: {e}")
            raise

# Global Redis utilities instance
redis_utils = RedisUtils()

# Example usage:
"""
# Cache data
redis_utils.cache_data(
    data={'user_id': '123', 'preferences': {'theme': 'dark'}},
    prefix='user_data',
    identifier='user_123',
    expire=3600  # 1 hour
)

# Get cached data
cached_data = redis_utils.get_cached_data(
    prefix='user_data',
    identifier='user_123'
)

# Cache batch data
redis_utils.cache_batch(
    data_dict={
        'user_123': {'name': 'John'},
        'user_456': {'name': 'Jane'}
    },
    prefix='user_data',
    expire=3600
)

# Get cached batch data
cached_batch = redis_utils.get_cached_batch(
    prefix='user_data',
    identifiers=['user_123', 'user_456']
)

# Delete batch keys
redis_utils.delete_batch(
    prefix='user_data',
    identifiers=['user_123', 'user_456']
)

# Scan keys
keys = redis_utils.scan_keys(
    prefix='user_data',
    pattern='user_*'
)

# Get memory usage
memory_usage = redis_utils.get_memory_usage()

# Get Redis stats
stats = redis_utils.get_stats()
""" 