"""
Sistema de cache para respuestas HTTP (optimizado)

Incluye cache en memoria para reducir carga en la base de datos.
"""

import time
import hashlib
import json
from typing import Optional, Dict, Any, Callable
from functools import wraps
from collections import OrderedDict

try:
    import orjson
    JSON_ENCODER = orjson
except ImportError:
    import json
    JSON_ENCODER = json

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except ImportError:
    pass


class LRUCache:
    """Cache LRU simple en memoria"""
    
    def __init__(self, max_size: int = 128):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        if key in self.cache:
            # Mover al final (más reciente)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Establece un valor en el cache"""
        # Si el cache está lleno, eliminar el más antiguo
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        cache_entry = {
            "value": value,
            "expires_at": time.time() + ttl if ttl else None
        }
        
        self.cache[key] = cache_entry
        self.cache.move_to_end(key)
    
    def _is_expired(self, key: str) -> bool:
        """Verifica si una entrada ha expirado"""
        if key not in self.cache:
            return True
        
        entry = self.cache[key]
        if entry.get("expires_at") is None:
            return False
        
        return time.time() > entry["expires_at"]
    
    def get_with_expiry_check(self, key: str) -> Optional[Any]:
        """Obtiene un valor verificando expiración"""
        if key not in self.cache:
            return None
        
        if self._is_expired(key):
            del self.cache[key]
            return None
        
        return self.get(key)
    
    def clear(self) -> None:
        """Limpia el cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2)
        }


# Cache global
_response_cache = LRUCache(max_size=256)


def generate_cache_key(
    path: str,
    query_params: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Genera una clave de cache única.
    
    Args:
        path: Ruta del endpoint
        query_params: Parámetros de query
        user_id: ID del usuario (opcional)
        
    Returns:
        Clave de cache
    """
    key_parts = [path]
    
    if query_params:
        # Ordenar parámetros para consistencia
        sorted_params = sorted(query_params.items())
        key_parts.append(str(sorted_params))
    
    if user_id:
        key_parts.append(f"user:{user_id}")
    
    key_string = "|".join(key_parts)
    
    # Hash para reducir tamaño
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_response(ttl: float = 60.0, key_func: Optional[Callable] = None):
    """
    Decorador para cachear respuestas HTTP.
    
    Args:
        ttl: Tiempo de vida del cache en segundos
        key_func: Función personalizada para generar la clave (opcional)
        
    Returns:
        Decorador
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave de cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Intentar extraer path y query params del request
                request = None
                for arg in args:
                    if hasattr(arg, 'url'):
                        request = arg
                        break
                if not request:
                    request = kwargs.get('request')
                
                if request:
                    query_params = dict(request.query_params)
                    user_id = kwargs.get('current_user_id') or kwargs.get('user_id')
                    cache_key = generate_cache_key(
                        request.url.path,
                        query_params,
                        user_id
                    )
                else:
                    # Sin request, no cachear
                    return await func(*args, **kwargs)
            
            # Intentar obtener del cache
            cached = _response_cache.get_with_expiry_check(cache_key)
            if cached is not None:
                if logger:
                    logger.debug(f"Cache hit for key: {cache_key}")
                return cached["value"]
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            
            _response_cache.set(cache_key, result, ttl=ttl)
            
            if logger:
                logger.debug(f"Cache miss for key: {cache_key}, cached result")
            
            return result
        
        return wrapper
    return decorator


def clear_response_cache(pattern: Optional[str] = None) -> int:
    """
    Limpia el cache de respuestas.
    
    Args:
        pattern: Patrón para limpiar específicamente (opcional)
        
    Returns:
        Número de entradas eliminadas
    """
    if pattern:
        # Limpiar solo entradas que coincidan con el patrón
        keys_to_remove = [
            key for key in _response_cache.cache.keys()
            if pattern in key
        ]
        for key in keys_to_remove:
            _response_cache.cache.pop(key, None)
        return len(keys_to_remove)
    else:
        # Limpiar todo
        count = len(_response_cache.cache)
        _response_cache.clear()
        return count


def get_cache_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del cache.
    
    Returns:
        Diccionario con estadísticas
    """
    return _response_cache.get_stats()

