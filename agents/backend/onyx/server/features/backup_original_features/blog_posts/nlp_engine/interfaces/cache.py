"""
🔌 CACHE INTERFACES - Contratos para Cache y Repositorios
========================================================

Interfaces para sistemas de cache y repositorios de datos.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from ..core.entities import AnalysisResult


class ICacheRepository(ABC):
    """Interface para repositorio de cache."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[AnalysisResult]:
        """
        Obtener resultado del cache.
        
        Args:
            key: Clave del cache
            
        Returns:
            AnalysisResult si existe, None si no
        """
        pass
    
    @abstractmethod
    async def set(
        self, 
        key: str, 
        result: AnalysisResult, 
        ttl: Optional[int] = None
    ) -> None:
        """
        Guardar resultado en cache.
        
        Args:
            key: Clave del cache
            result: Resultado a guardar
            ttl: Tiempo de vida en segundos (opcional)
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Eliminar entrada del cache.
        
        Args:
            key: Clave a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        pass
    
    @abstractmethod
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidar keys que coincidan con patrón.
        
        Args:
            pattern: Patrón para matching (ej: "nlp:*")
            
        Returns:
            Número de keys invalidadas
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Verificar si existe una clave.
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si existe
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del cache.
        
        Returns:
            Diccionario con estadísticas
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Limpiar completamente el cache."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar salud del cache.
        
        Returns:
            Estado de salud del cache
        """
        pass


class IDistributedCache(ICacheRepository):
    """Interface para cache distribuido."""
    
    @abstractmethod
    async def get_node_info(self) -> Dict[str, Any]:
        """
        Obtener información del nodo en cluster.
        
        Returns:
            Información del nodo
        """
        pass
    
    @abstractmethod
    async def get_cluster_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del cluster.
        
        Returns:
            Estadísticas del cluster
        """
        pass
    
    @abstractmethod
    async def replicate_to_nodes(self, key: str, result: AnalysisResult) -> int:
        """
        Replicar datos a otros nodos.
        
        Args:
            key: Clave a replicar
            result: Resultado a replicar
            
        Returns:
            Número de nodos que recibieron la réplica
        """
        pass


class ICacheKeyGenerator(ABC):
    """Interface para generación de claves de cache."""
    
    @abstractmethod
    def generate_key(
        self, 
        text_hash: str, 
        analysis_types: List[str], 
        tier: str,
        **kwargs
    ) -> str:
        """
        Generar clave determinística para cache.
        
        Args:
            text_hash: Hash del texto
            analysis_types: Tipos de análisis
            tier: Tier de procesamiento
            **kwargs: Parámetros adicionales
            
        Returns:
            Clave de cache única
        """
        pass
    
    @abstractmethod
    def extract_components(self, key: str) -> Dict[str, Any]:
        """
        Extraer componentes de una clave de cache.
        
        Args:
            key: Clave a descomponer
            
        Returns:
            Diccionario con componentes
        """
        pass
    
    @abstractmethod
    def validate_key(self, key: str) -> bool:
        """
        Validar formato de clave.
        
        Args:
            key: Clave a validar
            
        Returns:
            True si es válida
        """
        pass


class ICacheEvictionPolicy(ABC):
    """Interface para políticas de eviction."""
    
    @abstractmethod
    def should_evict(
        self, 
        cache_size: int, 
        max_size: int, 
        access_times: Dict[str, float]
    ) -> List[str]:
        """
        Determinar qué claves evict.
        
        Args:
            cache_size: Tamaño actual del cache
            max_size: Tamaño máximo
            access_times: Tiempos de acceso por clave
            
        Returns:
            Lista de claves a evict
        """
        pass
    
    @abstractmethod
    def get_policy_name(self) -> str:
        """
        Obtener nombre de la política.
        
        Returns:
            Nombre de la política (LRU, LFU, etc.)
        """
        pass


class ICacheSerializer(ABC):
    """Interface para serialización de cache."""
    
    @abstractmethod
    def serialize(self, result: AnalysisResult) -> bytes:
        """
        Serializar resultado para almacenamiento.
        
        Args:
            result: Resultado a serializar
            
        Returns:
            Datos serializados
        """
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> AnalysisResult:
        """
        Deserializar datos del cache.
        
        Args:
            data: Datos serializados
            
        Returns:
            AnalysisResult deserializado
        """
        pass
    
    @abstractmethod
    def get_format(self) -> str:
        """
        Obtener formato de serialización.
        
        Returns:
            Formato utilizado (json, pickle, msgpack, etc.)
        """
        pass 