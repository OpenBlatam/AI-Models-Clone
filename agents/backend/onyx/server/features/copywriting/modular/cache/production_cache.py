# -*- coding: utf-8 -*-
"""
Production Cache - Sistema de cache multi-nivel modular
========================================================

Sistema de cache robusto con múltiples niveles para máximo rendimiento.
"""

import time
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class ProductionCache:
    """Sistema de cache de producción multi-nivel"""
    
    def __init__(self, engine, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar cache de producción
        
        Args:
            engine: Motor de optimización
            config: Configuración opcional del cache
        """
        self.engine = engine
        self.config = config or {}
        
        # Cache configuration
        self.memory_cache_size = self.config.get('memory_cache_size', 1000)
        self.cache_ttl = self.config.get('cache_ttl', 3600)
        self.compression_threshold = self.config.get('compression_threshold', 1024)
        
        # Cache storage layers
        self.memory_cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
        self.compressed_cache: Dict[str, bytes] = {}
        
        # External cache (Redis)
        self.redis = engine.cache_handler
        
        # Metrics tracking
        self.metrics = {
            "memory_hits": 0,
            "compressed_hits": 0, 
            "redis_hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }
        
        logger.info(f"ProductionCache initialized: Memory + Compression + {'Redis' if self.redis else 'No Redis'}")
    
    def _generate_cache_key(self, key: str) -> str:
        """Generar clave de cache optimizada"""
        return self.engine.hash_handler["hash"](key)[:16]
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor del cache multi-nivel
        
        Args:
            key: Clave del cache
            
        Returns:
            Valor cacheado o None si no existe
        """
        cache_key = self._generate_cache_key(key)
        
        try:
            # Level 1: Memory cache (fastest)
            if cache_key in self.memory_cache:
                if time.time() - self.timestamps.get(cache_key, 0) < self.cache_ttl:
                    self.metrics["memory_hits"] += 1
                    return self.memory_cache[cache_key]
                else:
                    # Clean expired entry
                    self._remove_from_memory(cache_key)
            
            # Level 2: Compressed cache (medium speed)
            if cache_key in self.compressed_cache:
                try:
                    compressed_data = self.compressed_cache[cache_key]
                    decompressed = self.engine.compression_handler["decompress"](compressed_data)
                    value = self.engine.json_handler["loads"](decompressed.decode())
                    
                    # Promote to memory cache
                    self._store_in_memory(cache_key, value)
                    
                    self.metrics["compressed_hits"] += 1
                    return value
                except Exception as e:
                    logger.warning(f"Compressed cache decompression error: {e}")
                    del self.compressed_cache[cache_key]
            
            # Level 3: Redis cache (network speed)
            if self.redis:
                try:
                    data = await self._redis_get(cache_key)
                    if data:
                        value = self.engine.json_handler["loads"](data)
                        # Promote to higher levels
                        await self.set(key, value)
                        self.metrics["redis_hits"] += 1
                        return value
                except Exception as e:
                    logger.warning(f"Redis cache error: {e}")
            
            self.metrics["misses"] += 1
            return None
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any) -> bool:
        """
        Almacenar valor en cache multi-nivel
        
        Args:
            key: Clave del cache
            value: Valor a almacenar
            
        Returns:
            True si se almacenó correctamente
        """
        cache_key = self._generate_cache_key(key)
        
        try:
            # Store in memory (Level 1)
            self._store_in_memory(cache_key, value)
            
            # Store compressed if data is large enough (Level 2)
            await self._store_compressed(cache_key, value)
            
            # Store in Redis if available (Level 3)
            await self._store_redis(cache_key, value)
            
            self.metrics["sets"] += 1
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Cache set error: {e}")
            return False
    
    def _store_in_memory(self, cache_key: str, value: Any):
        """Almacenar en cache de memoria con LRU eviction"""
        # LRU eviction if cache is full
        if len(self.memory_cache) >= self.memory_cache_size:
            oldest_key = min(self.timestamps.keys(), key=self.timestamps.get)
            self._remove_from_memory(oldest_key)
        
        self.memory_cache[cache_key] = value
        self.timestamps[cache_key] = time.time()
    
    def _remove_from_memory(self, cache_key: str):
        """Remover entrada del cache de memoria"""
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        if cache_key in self.timestamps:
            del self.timestamps[cache_key]
    
    async def _store_compressed(self, cache_key: str, value: Any):
        """Almacenar en cache comprimido"""
        try:
            json_data = self.engine.json_handler["dumps"](value).encode()
            if len(json_data) >= self.compression_threshold:
                compressed = self.engine.compression_handler["compress"](json_data)
                self.compressed_cache[cache_key] = compressed
        except Exception as e:
            logger.warning(f"Compression error: {e}")
    
    async def _store_redis(self, cache_key: str, value: Any):
        """Almacenar en Redis"""
        if self.redis:
            try:
                data = self.engine.json_handler["dumps"](value)
                await self._redis_set(cache_key, data)
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
    
    async def _redis_get(self, cache_key: str) -> Optional[str]:
        """Obtener de Redis (compatible sync/async)"""
        if hasattr(self.redis, 'get'):
            # Sync Redis
            return self.redis.get(f"modular:{cache_key}")
        else:
            # Async Redis
            return await self.redis.get(f"modular:{cache_key}")
    
    async def _redis_set(self, cache_key: str, data: str):
        """Almacenar en Redis (compatible sync/async)"""
        if hasattr(self.redis, 'setex'):
            # Sync Redis
            self.redis.setex(f"modular:{cache_key}", self.cache_ttl, data)
        else:
            # Async Redis
            await self.redis.setex(f"modular:{cache_key}", self.cache_ttl, data)
    
    def clear(self):
        """Limpiar todos los caches"""
        self.memory_cache.clear()
        self.timestamps.clear()
        self.compressed_cache.clear()
        logger.info("All caches cleared")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de performance del cache"""
        total_requests = sum([
            self.metrics["memory_hits"],
            self.metrics["compressed_hits"], 
            self.metrics["redis_hits"],
            self.metrics["misses"]
        ])
        
        hit_rate = 0.0
        if total_requests > 0:
            total_hits = (
                self.metrics["memory_hits"] + 
                self.metrics["compressed_hits"] + 
                self.metrics["redis_hits"]
            )
            hit_rate = (total_hits / total_requests) * 100
        
        return {
            "hit_rate_percent": hit_rate,
            "total_requests": total_requests,
            "memory_cache_size": len(self.memory_cache),
            "compressed_cache_size": len(self.compressed_cache),
            "redis_available": self.redis is not None,
            "config": {
                "memory_cache_size": self.memory_cache_size,
                "cache_ttl": self.cache_ttl,
                "compression_threshold": self.compression_threshold
            },
            **self.metrics
        } 