"""
🔌 INTERFACES - Contracts
=========================

Interfaces y contratos del sistema.
"""

from .contracts import (
    IOptimizer,
    ICache,
    INLPAnalyzer
)

__all__ = [
    'IOptimizer',
    'ICache', 
    'INLPAnalyzer'
]

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from ..entities import (
    TextInput, AnalysisResult, BatchResult, PerformanceMetrics, 
    SystemStatus, AnalysisType, OptimizationTier
)


class ISerializer(ABC):
    """Interface para serialización."""
    
    @abstractmethod
    def serialize(self, data: Any) -> bytes:
        """Serializar datos."""
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Deserializar datos."""
        pass
    
    @abstractmethod
    def get_compression_ratio(self) -> float:
        """Obtener ratio de compresión."""
        pass


class IMonitor(ABC):
    """Interface para monitoreo."""
    
    @abstractmethod
    async def record_request(self, processing_time_ms: float, success: bool) -> None:
        """Registrar request."""
        pass
    
    @abstractmethod
    def get_metrics(self) -> PerformanceMetrics:
        """Obtener métricas actuales."""
        pass
    
    @abstractmethod
    def get_system_status(self) -> SystemStatus:
        """Obtener estado del sistema."""
        pass


class IConfigurationProvider(ABC):
    """Interface para configuración."""
    
    @abstractmethod
    def get_optimization_tier(self) -> OptimizationTier:
        """Obtener tier de optimización."""
        pass
    
    @abstractmethod
    def get_cache_config(self) -> Dict[str, Any]:
        """Obtener configuración de cache."""
        pass
    
    @abstractmethod
    def get_performance_config(self) -> Dict[str, Any]:
        """Obtener configuración de rendimiento."""
        pass
    
    @abstractmethod
    def is_feature_enabled(self, feature: str) -> bool:
        """Verificar si feature está habilitado."""
        pass


class IHealthChecker(ABC):
    """Interface para health checks."""
    
    @abstractmethod
    async def check_health(self) -> SystemStatus:
        """Verificar salud del sistema."""
        pass
    
    @abstractmethod
    async def check_dependencies(self) -> Dict[str, bool]:
        """Verificar dependencias."""
        pass
    
    @abstractmethod
    async def run_diagnostic(self) -> Dict[str, Any]:
        """Ejecutar diagnóstico completo."""
        pass


class IFactory(ABC):
    """Interface para factories."""
    
    @abstractmethod
    def create_optimizer(self, tier: OptimizationTier) -> IOptimizer:
        """Crear optimizador."""
        pass
    
    @abstractmethod
    def create_cache(self, config: Dict[str, Any]) -> ICache:
        """Crear sistema de cache."""
        pass
    
    @abstractmethod
    def create_serializer(self, format_type: str) -> ISerializer:
        """Crear serializador."""
        pass


class IRepository(ABC):
    """Interface para persistencia."""
    
    @abstractmethod
    async def save_result(self, result: AnalysisResult) -> bool:
        """Guardar resultado."""
        pass
    
    @abstractmethod
    async def get_results(
        self, 
        filters: Dict[str, Any]
    ) -> List[AnalysisResult]:
        """Obtener resultados."""
        pass
    
    @abstractmethod
    async def save_metrics(self, metrics: PerformanceMetrics) -> bool:
        """Guardar métricas."""
        pass 