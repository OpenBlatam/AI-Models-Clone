"""
Cache System - Sistema de Cache Inteligente
Sistema de cache con invalidación automática y estrategias de almacenamiento
"""

import asyncio
import logging
import json
import pickle
import hashlib
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os
import threading
from collections import OrderedDict
import gzip

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Entrada del cache"""
    key: str
    value: Any
    created_at: float
    expires_at: Optional[float]
    access_count: int = 0
    last_accessed: float = 0
    size_bytes: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_accessed == 0:
            self.last_accessed = self.created_at

class CacheSystem:
    """
    Sistema de cache inteligente con múltiples estrategias de almacenamiento
    """
    
    def __init__(self, max_memory_size: int = 100 * 1024 * 1024,  # 100MB
                 max_disk_size: int = 1024 * 1024 * 1024,  # 1GB
                 default_ttl: int = 3600):  # 1 hora
        self.max_memory_size = max_memory_size
        self.max_disk_size = max_disk_size
        self.default_ttl = default_ttl
        
        # Cache en memoria (LRU)
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_memory_size = 0
        
        # Cache en disco
        self.disk_cache_dir = "cache_disk"
        self.current_disk_size = 0
        
        # Estadísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "disk_writes": 0,
            "disk_reads": 0,
            "compressions": 0
        }
        
        # Lock para operaciones thread-safe
        self.lock = threading.RLock()
        
        # Inicializar directorio de cache
        self._initialize_disk_cache()
        
        # Hilo para limpieza automática
        self.cleanup_thread = None
        self.running = False
    
    def _initialize_disk_cache(self):
        """Inicializar directorio de cache en disco"""
        try:
            if not os.path.exists(self.disk_cache_dir):
                os.makedirs(self.disk_cache_dir)
            
            # Calcular tamaño actual del cache en disco
            self._calculate_disk_size()
            
        except Exception as e:
            logger.error(f"Error inicializando cache en disco: {e}")
    
    def start_cleanup_thread(self):
        """Iniciar hilo de limpieza automática"""
        if self.cleanup_thread is None or not self.cleanup_thread.is_alive():
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            logger.info("Hilo de limpieza de cache iniciado")
    
    def stop_cleanup_thread(self):
        """Detener hilo de limpieza"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Hilo de limpieza de cache detenido")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor del cache"""
        try:
            with self.lock:
                # Buscar en cache de memoria primero
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    
                    # Verificar si ha expirado
                    if entry.expires_at and time.time() > entry.expires_at:
                        await self.delete(key)
                        self.stats["misses"] += 1
                        return default
                    
                    # Actualizar estadísticas de acceso
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    
                    # Mover al final (LRU)
                    self.memory_cache.move_to_end(key)
                    
                    self.stats["hits"] += 1
                    logger.debug(f"Cache hit en memoria: {key}")
                    return entry.value
                
                # Buscar en cache de disco
                disk_entry = await self._get_from_disk(key)
                if disk_entry:
                    # Verificar si ha expirado
                    if disk_entry.expires_at and time.time() > disk_entry.expires_at:
                        await self.delete(key)
                        self.stats["misses"] += 1
                        return default
                    
                    # Mover a cache de memoria si hay espacio
                    if self._can_fit_in_memory(disk_entry):
                        await self._move_to_memory(disk_entry)
                    
                    self.stats["hits"] += 1
                    self.stats["disk_reads"] += 1
                    logger.debug(f"Cache hit en disco: {key}")
                    return disk_entry.value
                
                self.stats["misses"] += 1
                logger.debug(f"Cache miss: {key}")
                return default
                
        except Exception as e:
            logger.error(f"Error obteniendo del cache: {e}")
            self.stats["misses"] += 1
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  tags: List[str] = None, compress: bool = False) -> bool:
        """Establecer valor en el cache"""
        try:
            with self.lock:
                # Calcular TTL
                expires_at = None
                if ttl is not None:
                    expires_at = time.time() + ttl
                elif self.default_ttl:
                    expires_at = time.time() + self.default_ttl
                
                # Calcular tamaño
                size_bytes = self._calculate_size(value)
                
                # Comprimir si se solicita y es beneficioso
                if compress and size_bytes > 1024:  # Solo comprimir si es mayor a 1KB
                    value = await self._compress_value(value)
                    size_bytes = self._calculate_size(value)
                    self.stats["compressions"] += 1
                
                # Crear entrada del cache
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=time.time(),
                    expires_at=expires_at,
                    size_bytes=size_bytes,
                    tags=tags or []
                )
                
                # Intentar almacenar en memoria primero
                if self._can_fit_in_memory(entry):
                    await self._store_in_memory(entry)
                else:
                    # Almacenar en disco
                    await self._store_in_disk(entry)
                
                logger.debug(f"Valor almacenado en cache: {key}")
                return True
                
        except Exception as e:
            logger.error(f"Error estableciendo en cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        try:
            with self.lock:
                deleted = False
                
                # Eliminar de memoria
                if key in self.memory_cache:
                    entry = self.memory_cache[key]
                    self.current_memory_size -= entry.size_bytes
                    del self.memory_cache[key]
                    deleted = True
                
                # Eliminar de disco
                disk_path = self._get_disk_path(key)
                if os.path.exists(disk_path):
                    try:
                        file_size = os.path.getsize(disk_path)
                        os.remove(disk_path)
                        self.current_disk_size -= file_size
                        deleted = True
                    except Exception as e:
                        logger.error(f"Error eliminando archivo de disco: {e}")
                
                if deleted:
                    logger.debug(f"Valor eliminado del cache: {key}")
                
                return deleted
                
        except Exception as e:
            logger.error(f"Error eliminando del cache: {e}")
            return False
    
    async def delete_by_tags(self, tags: List[str]) -> int:
        """Eliminar entradas por tags"""
        try:
            with self.lock:
                deleted_count = 0
                
                # Eliminar de memoria
                keys_to_delete = []
                for key, entry in self.memory_cache.items():
                    if any(tag in entry.tags for tag in tags):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    if await self.delete(key):
                        deleted_count += 1
                
                # Eliminar de disco
                if os.path.exists(self.disk_cache_dir):
                    for filename in os.listdir(self.disk_cache_dir):
                        if filename.endswith('.cache'):
                            try:
                                file_path = os.path.join(self.disk_cache_dir, filename)
                                with open(file_path, 'rb') as f:
                                    entry = pickle.load(f)
                                
                                if any(tag in entry.tags for tag in tags):
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    self.current_disk_size -= file_size
                                    deleted_count += 1
                                    
                            except Exception as e:
                                logger.error(f"Error procesando archivo de cache: {e}")
                
                logger.info(f"Eliminadas {deleted_count} entradas por tags: {tags}")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error eliminando por tags: {e}")
            return 0
    
    async def clear(self) -> bool:
        """Limpiar todo el cache"""
        try:
            with self.lock:
                # Limpiar memoria
                self.memory_cache.clear()
                self.current_memory_size = 0
                
                # Limpiar disco
                if os.path.exists(self.disk_cache_dir):
                    for filename in os.listdir(self.disk_cache_dir):
                        if filename.endswith('.cache'):
                            file_path = os.path.join(self.disk_cache_dir, filename)
                            try:
                                os.remove(file_path)
                            except Exception as e:
                                logger.error(f"Error eliminando archivo: {e}")
                
                self.current_disk_size = 0
                self._calculate_disk_size()
                
                logger.info("Cache completamente limpiado")
                return True
                
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
            return False
    
    async def get_or_set(self, key: str, factory: Callable, ttl: Optional[int] = None,
                        tags: List[str] = None) -> Any:
        """Obtener del cache o calcular y almacenar"""
        try:
            # Intentar obtener del cache
            value = await self.get(key)
            if value is not None:
                return value
            
            # Calcular valor usando factory
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
            
            # Almacenar en cache
            await self.set(key, value, ttl, tags)
            
            return value
            
        except Exception as e:
            logger.error(f"Error en get_or_set: {e}")
            # Intentar usar factory como fallback
            try:
                if asyncio.iscoroutinefunction(factory):
                    return await factory()
                else:
                    return factory()
            except Exception as factory_error:
                logger.error(f"Error en factory: {factory_error}")
                raise
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidar entradas que coincidan con un patrón"""
        try:
            import fnmatch
            
            with self.lock:
                deleted_count = 0
                
                # Invalidar en memoria
                keys_to_delete = []
                for key in self.memory_cache:
                    if fnmatch.fnmatch(key, pattern):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    if await self.delete(key):
                        deleted_count += 1
                
                # Invalidar en disco
                if os.path.exists(self.disk_cache_dir):
                    for filename in os.listdir(self.disk_cache_dir):
                        if filename.endswith('.cache'):
                            cache_key = filename[:-6]  # Remover .cache
                            if fnmatch.fnmatch(cache_key, pattern):
                                file_path = os.path.join(self.disk_cache_dir, filename)
                                try:
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    self.current_disk_size -= file_size
                                    deleted_count += 1
                                except Exception as e:
                                    logger.error(f"Error eliminando archivo: {e}")
                
                logger.info(f"Invalidadas {deleted_count} entradas con patrón: {pattern}")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error invalidando patrón: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        try:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "memory_entries": len(self.memory_cache),
                "memory_size_mb": self.current_memory_size / (1024 * 1024),
                "memory_size_limit_mb": self.max_memory_size / (1024 * 1024),
                "disk_size_mb": self.current_disk_size / (1024 * 1024),
                "disk_size_limit_mb": self.max_disk_size / (1024 * 1024),
                "hit_rate_percent": round(hit_rate, 2),
                "total_hits": self.stats["hits"],
                "total_misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "disk_writes": self.stats["disk_writes"],
                "disk_reads": self.stats["disk_reads"],
                "compressions": self.stats["compressions"]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def _can_fit_in_memory(self, entry: CacheEntry) -> bool:
        """Verificar si una entrada puede caber en memoria"""
        return (self.current_memory_size + entry.size_bytes) <= self.max_memory_size
    
    async def _store_in_memory(self, entry: CacheEntry):
        """Almacenar entrada en memoria"""
        try:
            # Si no cabe, hacer espacio
            while not self._can_fit_in_memory(entry) and self.memory_cache:
                await self._evict_lru()
            
            # Almacenar entrada
            self.memory_cache[entry.key] = entry
            self.current_memory_size += entry.size_bytes
            
        except Exception as e:
            logger.error(f"Error almacenando en memoria: {e}")
    
    async def _store_in_disk(self, entry: CacheEntry):
        """Almacenar entrada en disco"""
        try:
            # Verificar límite de disco
            if self.current_disk_size + entry.size_bytes > self.max_disk_size:
                await self._cleanup_disk_space(entry.size_bytes)
            
            # Almacenar en disco
            disk_path = self._get_disk_path(entry.key)
            with open(disk_path, 'wb') as f:
                pickle.dump(entry, f)
            
            self.current_disk_size += entry.size_bytes
            self.stats["disk_writes"] += 1
            
        except Exception as e:
            logger.error(f"Error almacenando en disco: {e}")
    
    async def _get_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Obtener entrada del disco"""
        try:
            disk_path = self._get_disk_path(key)
            if os.path.exists(disk_path):
                with open(disk_path, 'rb') as f:
                    entry = pickle.load(f)
                
                # Actualizar estadísticas de acceso
                entry.access_count += 1
                entry.last_accessed = time.time()
                
                # Guardar entrada actualizada
                with open(disk_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                return entry
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo del disco: {e}")
            return None
    
    async def _move_to_memory(self, entry: CacheEntry):
        """Mover entrada del disco a memoria"""
        try:
            # Almacenar en memoria
            await self._store_in_memory(entry)
            
            # Eliminar del disco
            disk_path = self._get_disk_path(entry.key)
            if os.path.exists(disk_path):
                file_size = os.path.getsize(disk_path)
                os.remove(disk_path)
                self.current_disk_size -= file_size
            
        except Exception as e:
            logger.error(f"Error moviendo a memoria: {e}")
    
    async def _evict_lru(self):
        """Eliminar entrada menos recientemente usada"""
        try:
            if self.memory_cache:
                # Obtener la entrada menos recientemente usada
                key, entry = self.memory_cache.popitem(last=False)
                
                # Intentar mover a disco
                if entry.size_bytes < self.max_disk_size:
                    await self._store_in_disk(entry)
                else:
                    # Si es muy grande, simplemente eliminar
                    pass
                
                self.current_memory_size -= entry.size_bytes
                self.stats["evictions"] += 1
                
        except Exception as e:
            logger.error(f"Error en evicción LRU: {e}")
    
    async def _cleanup_disk_space(self, required_space: int):
        """Limpiar espacio en disco"""
        try:
            # Obtener archivos ordenados por fecha de acceso
            cache_files = []
            for filename in os.listdir(self.disk_cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.disk_cache_dir, filename)
                    try:
                        stat = os.stat(file_path)
                        cache_files.append((file_path, stat.st_atime, stat.st_size))
                    except Exception:
                        continue
            
            # Ordenar por fecha de acceso (más antiguos primero)
            cache_files.sort(key=lambda x: x[1])
            
            # Eliminar archivos hasta tener suficiente espacio
            freed_space = 0
            for file_path, _, file_size in cache_files:
                if freed_space >= required_space:
                    break
                
                try:
                    os.remove(file_path)
                    freed_space += file_size
                    self.current_disk_size -= file_size
                except Exception as e:
                    logger.error(f"Error eliminando archivo: {e}")
            
        except Exception as e:
            logger.error(f"Error limpiando espacio en disco: {e}")
    
    def _get_disk_path(self, key: str) -> str:
        """Obtener ruta del archivo en disco"""
        # Usar hash del key para evitar caracteres problemáticos
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.disk_cache_dir, f"{key_hash}.cache")
    
    def _calculate_size(self, value: Any) -> int:
        """Calcular tamaño de un valor"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            else:
                return len(pickle.dumps(value))
        except Exception:
            return 1024  # Tamaño estimado por defecto
    
    async def _compress_value(self, value: Any) -> bytes:
        """Comprimir valor"""
        try:
            if isinstance(value, str):
                return gzip.compress(value.encode())
            else:
                serialized = pickle.dumps(value)
                return gzip.compress(serialized)
        except Exception as e:
            logger.error(f"Error comprimiendo valor: {e}")
            return value
    
    async def _decompress_value(self, compressed_value: bytes) -> Any:
        """Descomprimir valor"""
        try:
            decompressed = gzip.decompress(compressed_value)
            # Intentar deserializar como pickle, si falla devolver como string
            try:
                return pickle.loads(decompressed)
            except:
                return decompressed.decode()
        except Exception as e:
            logger.error(f"Error descomprimiendo valor: {e}")
            return compressed_value
    
    def _calculate_disk_size(self):
        """Calcular tamaño actual del cache en disco"""
        try:
            total_size = 0
            if os.path.exists(self.disk_cache_dir):
                for filename in os.listdir(self.disk_cache_dir):
                    if filename.endswith('.cache'):
                        file_path = os.path.join(self.disk_cache_dir, filename)
                        try:
                            total_size += os.path.getsize(file_path)
                        except Exception:
                            continue
            
            self.current_disk_size = total_size
            
        except Exception as e:
            logger.error(f"Error calculando tamaño de disco: {e}")
    
    def _cleanup_loop(self):
        """Loop de limpieza automática"""
        while self.running:
            try:
                time.sleep(300)  # Limpiar cada 5 minutos
                
                if not self.running:
                    break
                
                # Limpiar entradas expiradas
                current_time = time.time()
                expired_keys = []
                
                with self.lock:
                    for key, entry in self.memory_cache.items():
                        if entry.expires_at and current_time > entry.expires_at:
                            expired_keys.append(key)
                
                for key in expired_keys:
                    asyncio.run_coroutine_threadsafe(
                        self.delete(key), 
                        asyncio.get_event_loop()
                    )
                
                # Limpiar archivos expirados en disco
                if os.path.exists(self.disk_cache_dir):
                    for filename in os.listdir(self.disk_cache_dir):
                        if filename.endswith('.cache'):
                            file_path = os.path.join(self.disk_cache_dir, filename)
                            try:
                                with open(file_path, 'rb') as f:
                                    entry = pickle.load(f)
                                
                                if entry.expires_at and current_time > entry.expires_at:
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    self.current_disk_size -= file_size
                                    
                            except Exception as e:
                                logger.error(f"Error limpiando archivo expirado: {e}")
                
                logger.debug("Limpieza automática de cache completada")
                
            except Exception as e:
                logger.error(f"Error en loop de limpieza: {e}")
                time.sleep(60)  # Esperar un minuto antes de reintentar


























