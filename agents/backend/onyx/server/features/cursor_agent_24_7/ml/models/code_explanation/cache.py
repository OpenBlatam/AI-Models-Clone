"""
Cache management for code explanations
"""

import hashlib
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ExplanationCache:
    """Manages caching of code explanations"""
    
    def __init__(self, enabled: bool = True, ttl: float = 3600.0, cache_instance: Optional[Any] = None):
        """Initialize explanation cache
        
        Args:
            enabled: Enable caching
            ttl: Time-to-live in seconds
            cache_instance: External cache instance (optional)
        """
        self.enabled = enabled
        self.ttl = ttl
        self._cache = cache_instance
    
    def _generate_key(self, code: str, **kwargs: Any) -> str:
        """Generate cache key from code and parameters
        
        Args:
            code: Code to explain
            **kwargs: Additional parameters
            
        Returns:
            SHA-256 hash of the key data
        """
        key_data = f"{code}|{kwargs}"
        return hashlib.sha256(key_data.encode('utf-8')).hexdigest()
    
    def get(self, code: str, **kwargs: Any) -> Optional[str]:
        """Get cached explanation
        
        Args:
            code: Code to explain
            **kwargs: Generation parameters
            
        Returns:
            Cached explanation or None
        """
        if not self.enabled or self._cache is None:
            return None
        
        try:
            cache_key = self._generate_key(code, **kwargs)
            if hasattr(self._cache, 'get'):
                result = self._cache.get(cache_key)
                if result is not None:
                    logger.debug("Cache hit for code explanation")
                    return result
        except Exception as e:
            logger.warning(f"Cache get error (continuing without cache): {e}")
        
        return None
    
    def set(self, code: str, explanation: str, **kwargs: Any) -> bool:
        """Cache explanation
        
        Args:
            code: Code that was explained
            explanation: Generated explanation
            **kwargs: Generation parameters
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled or self._cache is None or not explanation:
            return False
        
        try:
            cache_key = self._generate_key(code, **kwargs)
            if hasattr(self._cache, 'set'):
                self._cache.set(cache_key, explanation, ttl=self.ttl)
                return True
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")
        
        return False
    
    def clear(self) -> int:
        """Clear cache
        
        Returns:
            Number of entries cleared
        """
        if self._cache is None:
            return 0
        
        try:
            if hasattr(self._cache, "clear"):
                self._cache.clear()
                return 1
            elif hasattr(self._cache, "delete_all"):
                return self._cache.delete_all()
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
        
        return 0

