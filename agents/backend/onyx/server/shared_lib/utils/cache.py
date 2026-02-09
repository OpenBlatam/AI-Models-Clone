"""
Advanced Caching
================

Sistema de caching avanzado con TTL, invalidación, y múltiples backends.
"""

import asyncio
import time
import hashlib
import json
import logging
from typing import Any, Optional, Callable, Dict
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuración de cache"""
    ttl: float = 3600.0  # Time to live en segundos
    key_prefix: str = "cache"
    serialize: bool = True
    compress: bool = False


class CacheBackend:
    """Interface para backends de cache"""
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache"""
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Guarda valor en cache"""
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """Elimina valor del cache"""
        raise NotImplementedError
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Limpia cache (opcionalmente por patrón)"""
        raise NotImplementedError


class InMemoryCache(CacheBackend):
    """Cache en memoria"""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry)
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            
            # Verificar expiración
            if time.time() > expiry:
                del self._cache[key]
                return None
            
            return value
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        async with self._lock:
            expiry = time.time() + (ttl or 3600.0)
            self._cache[key] = (value, expiry)
            return True
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        async with self._lock:
            if pattern:
                # Simple pattern matching
                keys_to_delete = [
                    k for k in self._cache.keys()
                    if pattern in k
                ]
                for key in keys_to_delete:
                    del self._cache[key]
                return len(keys_to_delete)
            else:
                count = len(self._cache)
                self._cache.clear()
                return count


class Cache:
    """
    Sistema de caching avanzado
    
    Ejemplo:
        cache = Cache(InMemoryCache(), CacheConfig(ttl=3600))
        
        @cache.cached(ttl=1800)
        async def expensive_operation(param: str):
            # Operación costosa
            return result
        
        # O manualmente
        await cache.set("key", value, ttl=3600)
        value = await cache.get("key")
    """
    
    def __init__(
        self,
        backend: CacheBackend,
        config: Optional[CacheConfig] = None
    ):
        self.backend = backend
        self.config = config or CacheConfig()
    
    def _make_key(self, *args, **kwargs) -> str:
        """Genera key única de los argumentos"""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{self.config.key_prefix}:{key_hash}"
    
    def cached(
        self,
        ttl: Optional[float] = None,
        key_func: Optional[Callable] = None
    ):
        """
        Decorator para cachear resultados de funciones
        
        Args:
            ttl: Time to live en segundos (override config)
            key_func: Función para generar key personalizada
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                # Generar key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._make_key(func.__name__, *args, **kwargs)
                
                # Intentar obtener del cache
                cached_value = await self.backend.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Ejecutar función
                logger.debug(f"Cache miss: {cache_key}")
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Guardar en cache
                cache_ttl = ttl if ttl is not None else self.config.ttl
                await self.backend.set(cache_key, result, ttl=cache_ttl)
                
                return result
            
            return wrapper
        
        return decorator
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache"""
        return await self.backend.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Guarda valor en cache"""
        cache_ttl = ttl if ttl is not None else self.config.ttl
        return await self.backend.set(key, value, ttl=cache_ttl)
    
    async def delete(self, key: str) -> bool:
        """Elimina valor del cache"""
        return await self.backend.delete(key)
    
    async def invalidate(self, pattern: Optional[str] = None) -> int:
        """Invalida cache por patrón"""
        return await self.backend.clear(pattern)
    
    async def get_or_set(
        self,
        key: str,
        func: Callable,
        ttl: Optional[float] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Obtiene del cache o ejecuta función y guarda
        
        Ejemplo:
            value = await cache.get_or_set(
                "user:123",
                fetch_user,
                123,
                ttl=3600
            )
        """
        # Intentar obtener
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Ejecutar función
        if asyncio.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        
        # Guardar
        await self.set(key, result, ttl=ttl)
        
        return result


# Instancia global
default_cache = Cache(InMemoryCache())




