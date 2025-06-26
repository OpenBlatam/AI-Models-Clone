"""
MODULAR ADS - Cache Module
========================

Sistema de cache modular multi-nivel para ads.
Cache inteligente con L1, L2, Campaign y Distributed levels.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from ..types import CacheLevel, AdType, AdPriority, Timestamp
from ..models import CacheEntry
from ..config import get_config
from ..engine import get_engine
from ..utils import TimeUtils, HashUtils

logger = logging.getLogger(__name__)

class CacheStats:
    """Estadísticas de cache modular"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Resetear estadísticas"""
        self.l1_hits = 0
        self.l2_hits = 0
        self.campaign_hits = 0
        self.distributed_hits = 0
        self.misses = 0
        self.sets = 0
        self.evictions = 0
        self.errors = 0
        self.total_requests = 0
        
        # Métricas de tiempo
        self.total_get_time = 0.0
        self.total_set_time = 0.0
        self.start_time = time.time()
    
    def record_hit(self, cache_level: CacheLevel, response_time: float = 0.0):
        """Registrar hit de cache"""
        self.total_requests += 1
        self.total_get_time += response_time
        
        if cache_level == CacheLevel.L1_MEMORY:
            self.l1_hits += 1
        elif cache_level == CacheLevel.L2_COMPRESSED:
            self.l2_hits += 1
        elif cache_level == CacheLevel.L3_CAMPAIGN:
            self.campaign_hits += 1
        elif cache_level == CacheLevel.L4_DISTRIBUTED:
            self.distributed_hits += 1
    
    def record_miss(self, response_time: float = 0.0):
        """Registrar miss de cache"""
        self.total_requests += 1
        self.total_get_time += response_time
        self.misses += 1
    
    def record_set(self, response_time: float = 0.0):
        """Registrar operación set"""
        self.sets += 1
        self.total_set_time += response_time
    
    def record_eviction(self):
        """Registrar eviction"""
        self.evictions += 1
    
    def record_error(self):
        """Registrar error"""
        self.errors += 1
    
    def get_hit_rate(self) -> float:
        """Calcular hit rate total"""
        total_hits = self.l1_hits + self.l2_hits + self.campaign_hits + self.distributed_hits
        if self.total_requests == 0:
            return 0.0
        return (total_hits / self.total_requests) * 100.0
    
    def get_level_hit_rates(self) -> Dict[str, float]:
        """Calcular hit rates por nivel"""
        if self.total_requests == 0:
            return {level.value: 0.0 for level in CacheLevel}
        
        return {
            CacheLevel.L1_MEMORY.value: (self.l1_hits / self.total_requests) * 100.0,
            CacheLevel.L2_COMPRESSED.value: (self.l2_hits / self.total_requests) * 100.0,
            CacheLevel.L3_CAMPAIGN.value: (self.campaign_hits / self.total_requests) * 100.0,
            CacheLevel.L4_DISTRIBUTED.value: (self.distributed_hits / self.total_requests) * 100.0,
        }
    
    def get_avg_response_times(self) -> Dict[str, float]:
        """Calcular tiempos promedio"""
        return {
            "avg_get_time_ms": (self.total_get_time / max(self.total_requests, 1)) * 1000,
            "avg_set_time_ms": (self.total_set_time / max(self.sets, 1)) * 1000,
        }

class BaseCacheLayer(ABC):
    """Clase base para capas de cache"""
    
    def __init__(self, level: CacheLevel, max_size: int = 1000):
        self.level = level
        self.max_size = max_size
        self.stats = CacheStats()
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[float] = None, **kwargs) -> bool:
        """Almacenar valor en cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Obtener tamaño actual del cache"""
        pass
    
    @abstractmethod
    async def clear(self):
        """Limpiar todo el cache"""
        pass

class L1MemoryCache(BaseCacheLayer):
    """Cache L1 - Memoria ultra-rápida"""
    
    def __init__(self, max_size: int = 3000):
        super().__init__(CacheLevel.L1_MEMORY, max_size)
        self.data: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # LRU tracking
        logger.info(f"L1MemoryCache inicializado (max_size={max_size})")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get ultra-rápido de memoria"""
        start_time = time.time()
        
        try:
            if key not in self.data:
                self.stats.record_miss((time.time() - start_time) * 1000)
                return None
            
            entry = self.data[key]
            
            # Verificar expiración
            if entry.is_expired():
                await self.delete(key)
                self.stats.record_miss((time.time() - start_time) * 1000)
                return None
            
            # Actualizar acceso
            entry.update_access()
            
            # Mover al final para LRU
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            response_time = (time.time() - start_time) * 1000
            self.stats.record_hit(self.level, response_time)
            
            return entry.value
        
        except Exception as e:
            logger.error(f"Error en L1 get: {e}")
            self.stats.record_error()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None, priority: AdPriority = AdPriority.MEDIUM, **kwargs) -> bool:
        """Set optimizado en memoria"""
        start_time = time.time()
        
        try:
            # Evict si es necesario
            while len(self.data) >= self.max_size:
                await self._evict_lru()
            
            # Crear entrada
            entry = CacheEntry(
                key=key,
                value=value,
                cache_level=self.level,
                priority=priority,
                ttl=ttl
            )
            
            # Almacenar
            self.data[key] = entry
            
            # Actualizar access_order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            response_time = (time.time() - start_time) * 1000
            self.stats.record_set(response_time)
            
            return True
        
        except Exception as e:
            logger.error(f"Error en L1 set: {e}")
            self.stats.record_error()
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar de memoria"""
        try:
            if key in self.data:
                del self.data[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                return True
            return False
        except Exception as e:
            logger.error(f"Error en L1 delete: {e}")
            return False
    
    async def _evict_lru(self):
        """Evict LRU con consideración de prioridad"""
        if not self.access_order:
            return
        
        # Buscar candidato con menor prioridad
        candidates = []
        for key in self.access_order:
            if key in self.data:
                entry = self.data[key]
                score = entry.priority.value + (entry.access_count * 0.1)
                candidates.append((key, score))
        
        if candidates:
            # Evict el de menor score
            candidates.sort(key=lambda x: x[1])
            key_to_evict = candidates[0][0]
            await self.delete(key_to_evict)
            self.stats.record_eviction()
    
    def size(self) -> int:
        """Tamaño actual"""
        return len(self.data)
    
    async def clear(self):
        """Limpiar todo"""
        self.data.clear()
        self.access_order.clear()

class L2CompressedCache(BaseCacheLayer):
    """Cache L2 - Comprimido para ads grandes"""
    
    def __init__(self, max_size: int = 5000):
        super().__init__(CacheLevel.L2_COMPRESSED, max_size)
        self.data: Dict[str, bytes] = {}  # Datos comprimidos
        self.metadata: Dict[str, CacheEntry] = {}  # Metadata sin comprimir
        self.engine = get_engine()
        logger.info(f"L2CompressedCache inicializado (max_size={max_size})")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get con descompresión automática"""
        start_time = time.time()
        
        try:
            if key not in self.data or key not in self.metadata:
                self.stats.record_miss((time.time() - start_time) * 1000)
                return None
            
            entry = self.metadata[key]
            
            # Verificar expiración
            if entry.is_expired():
                await self.delete(key)
                self.stats.record_miss((time.time() - start_time) * 1000)
                return None
            
            # Descomprimir
            compressed_data = self.data[key]
            compression_handler = self.engine.get_handler("compression")
            json_handler = self.engine.get_handler("json")
            
            decompressed = compression_handler["decompress"](compressed_data)
            value = json_handler["loads"](decompressed.decode())
            
            # Actualizar acceso
            entry.update_access()
            
            response_time = (time.time() - start_time) * 1000
            self.stats.record_hit(self.level, response_time)
            
            return value
        
        except Exception as e:
            logger.error(f"Error en L2 get: {e}")
            self.stats.record_error()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None, priority: AdPriority = AdPriority.MEDIUM, **kwargs) -> bool:
        """Set con compresión automática"""
        start_time = time.time()
        
        try:
            # Serializar y comprimir
            json_handler = self.engine.get_handler("json")
            compression_handler = self.engine.get_handler("compression")
            
            json_data = json_handler["dumps"](value).encode()
            compressed_data = compression_handler["compress"](json_data)
            
            # Verificar eficiencia de compresión
            compression_ratio = len(compressed_data) / len(json_data)
            if compression_ratio > 0.9:  # No vale la pena comprimir
                return False
            
            # Evict si es necesario
            while len(self.data) >= self.max_size:
                await self._evict_oldest()
            
            # Crear metadata
            entry = CacheEntry(
                key=key,
                value=None,  # No almacenar el valor en metadata
                cache_level=self.level,
                priority=priority,
                ttl=ttl
            )
            entry.metadata["original_size"] = len(json_data)
            entry.metadata["compressed_size"] = len(compressed_data)
            entry.metadata["compression_ratio"] = compression_ratio
            
            # Almacenar
            self.data[key] = compressed_data
            self.metadata[key] = entry
            
            response_time = (time.time() - start_time) * 1000
            self.stats.record_set(response_time)
            
            return True
        
        except Exception as e:
            logger.error(f"Error en L2 set: {e}")
            self.stats.record_error()
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar datos comprimidos"""
        try:
            deleted_data = key in self.data
            deleted_meta = key in self.metadata
            
            if deleted_data:
                del self.data[key]
            if deleted_meta:
                del self.metadata[key]
            
            return deleted_data or deleted_meta
        except Exception as e:
            logger.error(f"Error en L2 delete: {e}")
            return False
    
    async def _evict_oldest(self):
        """Evict entrada más antigua"""
        if not self.metadata:
            return
        
        oldest_key = min(self.metadata.keys(), 
                        key=lambda k: self.metadata[k].created_at)
        await self.delete(oldest_key)
        self.stats.record_eviction()
    
    def size(self) -> int:
        """Tamaño actual"""
        return len(self.data)
    
    async def clear(self):
        """Limpiar todo"""
        self.data.clear()
        self.metadata.clear()

class L3CampaignCache(BaseCacheLayer):
    """Cache L3 - Específico por campaña y tipo de ad"""
    
    def __init__(self, max_size: int = 2000):
        super().__init__(CacheLevel.L3_CAMPAIGN, max_size)
        self.data: Dict[str, Dict[str, CacheEntry]] = {}  # campaign_id -> {key: entry}
        self.campaign_stats: Dict[str, Dict[str, int]] = {}
        logger.info(f"L3CampaignCache inicializado (max_size={max_size})")
    
    def _get_campaign_key(self, ad_type: AdType, campaign_id: Optional[str] = None) -> str:
        """Generar clave de campaña"""
        if campaign_id:
            return f"{ad_type.value}:{campaign_id}"
        return f"{ad_type.value}:default"
    
    async def get(self, key: str, ad_type: AdType = AdType.FACEBOOK, campaign_id: Optional[str] = None) -> Optional[Any]:
        """Get específico por campaña"""
        start_time = time.time()
        campaign_key = self._get_campaign_key(ad_type, campaign_id)
        
        try:
            if campaign_key not in self.data or key not in self.data[campaign_key]:
                self.stats.record_miss((time.time() - start_time) * 1000)
                return None
            
            entry = self.data[campaign_key][key]
            
            # Verificar expiración
            if entry.is_expired():
                await self.delete(key, ad_type, campaign_id)
                self.stats.record_miss((time.time() - start_time) * 1000)
                return None
            
            # Actualizar acceso
            entry.update_access()
            
            # Actualizar stats de campaña
            if campaign_key not in self.campaign_stats:
                self.campaign_stats[campaign_key] = {"hits": 0, "sets": 0}
            self.campaign_stats[campaign_key]["hits"] += 1
            
            response_time = (time.time() - start_time) * 1000
            self.stats.record_hit(self.level, response_time)
            
            return entry.value
        
        except Exception as e:
            logger.error(f"Error en L3 get: {e}")
            self.stats.record_error()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None, 
                 ad_type: AdType = AdType.FACEBOOK, campaign_id: Optional[str] = None, 
                 priority: AdPriority = AdPriority.MEDIUM, **kwargs) -> bool:
        """Set específico por campaña"""
        start_time = time.time()
        campaign_key = self._get_campaign_key(ad_type, campaign_id)
        
        try:
            # Inicializar campaña si no existe
            if campaign_key not in self.data:
                self.data[campaign_key] = {}
                self.campaign_stats[campaign_key] = {"hits": 0, "sets": 0}
            
            # Verificar límite total
            total_entries = sum(len(campaign_data) for campaign_data in self.data.values())
            while total_entries >= self.max_size:
                await self._evict_from_least_used_campaign()
                total_entries = sum(len(campaign_data) for campaign_data in self.data.values())
            
            # Crear entrada
            entry = CacheEntry(
                key=key,
                value=value,
                cache_level=self.level,
                priority=priority,
                ttl=ttl
            )
            entry.metadata["ad_type"] = ad_type.value
            entry.metadata["campaign_id"] = campaign_id
            
            # Almacenar
            self.data[campaign_key][key] = entry
            self.campaign_stats[campaign_key]["sets"] += 1
            
            response_time = (time.time() - start_time) * 1000
            self.stats.record_set(response_time)
            
            return True
        
        except Exception as e:
            logger.error(f"Error en L3 set: {e}")
            self.stats.record_error()
            return False
    
    async def delete(self, key: str, ad_type: AdType = AdType.FACEBOOK, campaign_id: Optional[str] = None) -> bool:
        """Eliminar específico por campaña"""
        campaign_key = self._get_campaign_key(ad_type, campaign_id)
        
        try:
            if campaign_key in self.data and key in self.data[campaign_key]:
                del self.data[campaign_key][key]
                
                # Limpiar campaña vacía
                if not self.data[campaign_key]:
                    del self.data[campaign_key]
                    if campaign_key in self.campaign_stats:
                        del self.campaign_stats[campaign_key]
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error en L3 delete: {e}")
            return False
    
    async def _evict_from_least_used_campaign(self):
        """Evict de la campaña menos usada"""
        if not self.campaign_stats:
            return
        
        # Encontrar campaña con menor ratio hits/sets
        least_used_campaign = min(
            self.campaign_stats.keys(),
            key=lambda k: self.campaign_stats[k]["hits"] / max(self.campaign_stats[k]["sets"], 1)
        )
        
        # Evict una entrada de esa campaña
        if least_used_campaign in self.data and self.data[least_used_campaign]:
            oldest_key = min(
                self.data[least_used_campaign].keys(),
                key=lambda k: self.data[least_used_campaign][k].created_at
            )
            del self.data[least_used_campaign][oldest_key]
            self.stats.record_eviction()
    
    def size(self) -> int:
        """Tamaño total"""
        return sum(len(campaign_data) for campaign_data in self.data.values())
    
    async def clear(self):
        """Limpiar todo"""
        self.data.clear()
        self.campaign_stats.clear()
    
    def get_campaign_stats(self) -> Dict[str, Dict[str, int]]:
        """Obtener estadísticas por campaña"""
        return self.campaign_stats.copy()

class ModularAdsCache:
    """Cache principal modular multi-nivel"""
    
    def __init__(self):
        self.config = get_config()
        
        # Inicializar capas de cache
        self.l1 = L1MemoryCache(self.config.cache.l1_max_size) if self.config.cache.enable_l1 else None
        self.l2 = L2CompressedCache(self.config.cache.l2_max_size) if self.config.cache.enable_l2 else None
        self.l3 = L3CampaignCache(self.config.cache.campaign_max_size) if self.config.cache.enable_campaign else None
        
        # Estadísticas globales
        self.global_stats = CacheStats()
        
        logger.info("ModularAdsCache inicializado con capas multi-nivel")
        self._show_cache_status()
    
    def _show_cache_status(self):
        """Mostrar estado del cache"""
        print(f"\n{'='*50}")
        print("🔄 MODULAR ADS CACHE SYSTEM")
        print(f"{'='*50}")
        
        if self.l1:
            print(f"📦 L1 Memory Cache: {self.l1.max_size} entries")
        if self.l2:
            print(f"🗜️  L2 Compressed Cache: {self.l2.max_size} entries")
        if self.l3:
            print(f"🎯 L3 Campaign Cache: {self.l3.max_size} entries")
        
        print(f"⚡ TTL Default: {self.config.cache.default_ttl}s")
        print(f"{'='*50}")
    
    async def get(self, key: str, ad_type: AdType = AdType.FACEBOOK, 
                 campaign_id: Optional[str] = None, priority: AdPriority = AdPriority.MEDIUM) -> Optional[Any]:
        """Get con fallback multi-nivel"""
        start_time = time.time()
        
        try:
            # L1: Memory cache
            if self.l1:
                result = await self.l1.get(key)
                if result is not None:
                    response_time = (time.time() - start_time) * 1000
                    self.global_stats.record_hit(CacheLevel.L1_MEMORY, response_time)
                    return result
            
            # L3: Campaign cache (antes que L2 para ads específicos)
            if self.l3:
                result = await self.l3.get(key, ad_type, campaign_id)
                if result is not None:
                    # Promover a L1 si es alta prioridad
                    if self.l1 and priority.value >= 4:
                        await self.l1.set(key, result, priority=priority)
                    
                    response_time = (time.time() - start_time) * 1000
                    self.global_stats.record_hit(CacheLevel.L3_CAMPAIGN, response_time)
                    return result
            
            # L2: Compressed cache
            if self.l2:
                result = await self.l2.get(key)
                if result is not None:
                    # Promover según prioridad
                    if self.l1 and priority.value >= 3:
                        await self.l1.set(key, result, priority=priority)
                    
                    response_time = (time.time() - start_time) * 1000
                    self.global_stats.record_hit(CacheLevel.L2_COMPRESSED, response_time)
                    return result
            
            # Miss en todos los niveles
            response_time = (time.time() - start_time) * 1000
            self.global_stats.record_miss(response_time)
            return None
        
        except Exception as e:
            logger.error(f"Error en cache get: {e}")
            self.global_stats.record_error()
            return None
    
    async def set(self, key: str, value: Any, ad_type: AdType = AdType.FACEBOOK,
                 campaign_id: Optional[str] = None, priority: AdPriority = AdPriority.MEDIUM,
                 ttl: Optional[float] = None) -> bool:
        """Set con distribución inteligente multi-nivel"""
        start_time = time.time()
        
        try:
            if ttl is None:
                ttl = self.config.cache.default_ttl
            
            # Estrategia de almacenamiento basada en tipo de ad y prioridad
            success = False
            
            # Ads críticos van a todos los niveles
            if priority == AdPriority.CRITICAL or ad_type in [AdType.FACEBOOK, AdType.GOOGLE]:
                if self.l1:
                    await self.l1.set(key, value, ttl=ttl, priority=priority)
                if self.l3:
                    await self.l3.set(key, value, ttl=ttl, ad_type=ad_type, 
                                    campaign_id=campaign_id, priority=priority)
                success = True
            
            # Ads normales van a L1 o L2 según tamaño
            else:
                # Estimar tamaño
                try:
                    engine = get_engine()
                    json_handler = engine.get_handler("json")
                    estimated_size = len(json_handler["dumps"](value))
                    
                    if estimated_size < 1024 and self.l1:  # Pequeños a L1
                        await self.l1.set(key, value, ttl=ttl, priority=priority)
                        success = True
                    elif self.l2:  # Grandes a L2 comprimido
                        success = await self.l2.set(key, value, ttl=ttl, priority=priority)
                    
                    # También en L3 si es relevante para campaña
                    if campaign_id and self.l3:
                        await self.l3.set(key, value, ttl=ttl, ad_type=ad_type,
                                        campaign_id=campaign_id, priority=priority)
                
                except Exception:
                    # Fallback a L1
                    if self.l1:
                        await self.l1.set(key, value, ttl=ttl, priority=priority)
                        success = True
            
            if success:
                response_time = (time.time() - start_time) * 1000
                self.global_stats.record_set(response_time)
            
            return success
        
        except Exception as e:
            logger.error(f"Error en cache set: {e}")
            self.global_stats.record_error()
            return False
    
    async def delete(self, key: str, ad_type: AdType = AdType.FACEBOOK, campaign_id: Optional[str] = None) -> bool:
        """Delete de todos los niveles"""
        results = []
        
        if self.l1:
            results.append(await self.l1.delete(key))
        if self.l2:
            results.append(await self.l2.delete(key))
        if self.l3:
            results.append(await self.l3.delete(key, ad_type, campaign_id))
        
        return any(results)
    
    async def clear_all(self):
        """Limpiar todos los niveles"""
        if self.l1:
            await self.l1.clear()
        if self.l2:
            await self.l2.clear()
        if self.l3:
            await self.l3.clear()
        
        self.global_stats.reset()
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas completas"""
        stats = {
            "global": {
                "hit_rate_percent": self.global_stats.get_hit_rate(),
                "total_requests": self.global_stats.total_requests,
                "level_hit_rates": self.global_stats.get_level_hit_rates(),
                "response_times": self.global_stats.get_avg_response_times(),
                "uptime_seconds": time.time() - self.global_stats.start_time
            }
        }
        
        if self.l1:
            stats["l1_memory"] = {
                "size": self.l1.size(),
                "max_size": self.l1.max_size,
                "hit_rate": self.l1.stats.get_hit_rate(),
                "evictions": self.l1.stats.evictions
            }
        
        if self.l2:
            stats["l2_compressed"] = {
                "size": self.l2.size(),
                "max_size": self.l2.max_size,
                "hit_rate": self.l2.stats.get_hit_rate(),
                "evictions": self.l2.stats.evictions
            }
        
        if self.l3:
            stats["l3_campaign"] = {
                "size": self.l3.size(),
                "max_size": self.l3.max_size,
                "hit_rate": self.l3.stats.get_hit_rate(),
                "campaign_stats": self.l3.get_campaign_stats()
            }
        
        return stats

# Instancia global del cache
_cache_instance: Optional[ModularAdsCache] = None

def get_cache() -> ModularAdsCache:
    """Obtener instancia global del cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ModularAdsCache()
    return _cache_instance

def set_cache(cache: ModularAdsCache):
    """Establecer instancia global del cache"""
    global _cache_instance
    _cache_instance = cache

__all__ = [
    'CacheStats',
    'BaseCacheLayer',
    'L1MemoryCache',
    'L2CompressedCache', 
    'L3CampaignCache',
    'ModularAdsCache',
    'get_cache',
    'set_cache',
] 