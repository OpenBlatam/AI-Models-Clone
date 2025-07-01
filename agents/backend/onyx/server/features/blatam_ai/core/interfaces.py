"""
🔧 BLATAM AI CORE INTERFACES v5.0.0
===================================

Interfaces base modulares para arquitectura limpia:
- 🏗️ Base component interfaces
- 🎯 Specialized behavior contracts
- 📊 Metrics and monitoring interfaces
- 🔄 Event handling interfaces
- ⚙️ Configuration interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Protocol, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import asyncio

# =============================================================================
# 🎯 CORE ENUMS
# =============================================================================

class ComponentStatus(Enum):
    """Estados de componentes."""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    OPTIMIZING = "optimizing"
    ERROR = "error"
    STOPPED = "stopped"
    DEGRADED = "degraded"

class ProcessingType(Enum):
    """Tipos de procesamiento."""
    ENTERPRISE = "enterprise"
    NLP_ANALYSIS = "nlp_analysis"
    NLP_GENERATION = "nlp_generation"
    PRODUCT_DESCRIPTION = "product_description"
    AGENT_INTERACTION = "agent_interaction"
    BATCH_PROCESSING = "batch_processing"
    AUTO_DETECT = "auto_detect"

class OptimizationStrategy(Enum):
    """Estrategias de optimización."""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    BALANCED = "balanced"
    ACCURACY = "accuracy"
    SPEED = "speed"

# =============================================================================
# 🏗️ BASE COMPONENT INTERFACES
# =============================================================================

class BlatamComponent(ABC):
    """Interface base para todos los componentes del sistema."""
    
    @property
    @abstractmethod
    def component_name(self) -> str:
        """Nombre del componente."""
        pass
    
    @property
    @abstractmethod
    def status(self) -> ComponentStatus:
        """Estado actual del componente."""
        pass
    
    @abstractmethod
    async def initialize(self, **kwargs) -> bool:
        """Inicializa el componente."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Apaga el componente limpiamente."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verifica la salud del componente."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del componente."""
        pass
    
    @abstractmethod
    async def process(self, data: Any, **kwargs) -> Any:
        """Procesa datos según la especialidad del componente."""
        pass

class ProcessingComponent(BlatamComponent):
    """Interface para componentes de procesamiento."""
    
    @abstractmethod
    def get_supported_types(self) -> List[ProcessingType]:
        """Obtiene tipos de procesamiento soportados."""
        pass
    
    @abstractmethod
    async def can_handle(self, data: Any, processing_type: ProcessingType) -> bool:
        """Determina si puede manejar el tipo de datos/procesamiento."""
        pass
    
    @abstractmethod
    async def estimate_processing_time(self, data: Any) -> float:
        """Estima tiempo de procesamiento en ms."""
        pass

class OptimizableComponent(BlatamComponent):
    """Interface para componentes optimizables."""
    
    @abstractmethod
    async def optimize(self, strategy: OptimizationStrategy, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza el componente basado en estrategia y métricas."""
        pass
    
    @abstractmethod
    async def record_performance(self, operation: str, duration_ms: float, success: bool, metadata: Optional[Dict] = None):
        """Registra métricas de rendimiento."""
        pass
    
    @abstractmethod
    def get_optimization_targets(self) -> Dict[str, float]:
        """Obtiene targets de optimización."""
        pass
    
    @abstractmethod
    async def rollback_optimization(self, optimization_id: str) -> bool:
        """Revierte una optimización específica."""
        pass

class LearningComponent(BlatamComponent):
    """Interface para componentes que aprenden."""
    
    @abstractmethod
    async def learn_from_interaction(self, interaction_data: Dict[str, Any]):
        """Aprende de una interacción."""
        pass
    
    @abstractmethod
    async def adapt_behavior(self, feedback: Dict[str, Any]):
        """Adapta comportamiento basado en feedback."""
        pass
    
    @abstractmethod
    async def save_learned_patterns(self) -> bool:
        """Guarda patrones aprendidos."""
        pass
    
    @abstractmethod
    async def load_learned_patterns(self) -> bool:
        """Carga patrones aprendidos."""
        pass

class CacheableComponent(BlatamComponent):
    """Interface para componentes con capacidades de cache."""
    
    @abstractmethod
    async def cache_get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache."""
        pass
    
    @abstractmethod
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Establece valor en cache."""
        pass
    
    @abstractmethod
    async def cache_invalidate(self, pattern: Optional[str] = None):
        """Invalida cache."""
        pass
    
    @abstractmethod
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de cache."""
        pass

# =============================================================================
# 🤖 ENGINE INTERFACES
# =============================================================================

class AIEngine(BlatamComponent):
    """Interface base para motores AI."""
    
    @property
    @abstractmethod
    def engine_type(self) -> str:
        """Tipo de motor (speed, nlp, langchain, evolution)."""
        pass
    
    @abstractmethod
    async def warm_up(self) -> bool:
        """Precalienta el motor."""
        pass
    
    @abstractmethod
    async def scale_up(self, factor: float) -> bool:
        """Escala el motor hacia arriba."""
        pass
    
    @abstractmethod
    async def scale_down(self, factor: float) -> bool:
        """Escala el motor hacia abajo."""
        pass

class SpeedEngine(AIEngine, OptimizableComponent, CacheableComponent):
    """Interface para motor de velocidad."""
    
    @abstractmethod
    async def ultra_fast_call(self, func, *args, **kwargs) -> Any:
        """Ejecuta función con optimizaciones ultra-rápidas."""
        pass
    
    @abstractmethod
    async def parallel_process(self, tasks: List[Any]) -> List[Any]:
        """Procesa tareas en paralelo."""
        pass
    
    @abstractmethod
    async def batch_optimize(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """Optimiza operaciones en lote."""
        pass

class NLPEngine(AIEngine, LearningComponent):
    """Interface para motor de NLP."""
    
    @abstractmethod
    async def analyze_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Analiza texto."""
        pass
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Genera texto."""
        pass
    
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Obtiene embeddings."""
        pass
    
    @abstractmethod
    async def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Búsqueda semántica."""
        pass

class LangChainEngine(AIEngine, LearningComponent):
    """Interface para motor de LangChain."""
    
    @abstractmethod
    async def create_agent(self, agent_type: str, name: str, **config) -> str:
        """Crea un agente."""
        pass
    
    @abstractmethod
    async def run_agent(self, agent_name: str, input_text: str, **kwargs) -> Dict[str, Any]:
        """Ejecuta un agente."""
        pass
    
    @abstractmethod
    async def create_chain(self, chain_type: str, **config) -> str:
        """Crea una cadena."""
        pass
    
    @abstractmethod
    async def run_chain(self, chain_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una cadena."""
        pass

class EvolutionEngine(AIEngine, OptimizableComponent, LearningComponent):
    """Interface para motor de evolución."""
    
    @abstractmethod
    async def auto_optimize_system(self) -> Dict[str, Any]:
        """Optimiza automáticamente el sistema."""
        pass
    
    @abstractmethod
    async def self_heal_system(self) -> Dict[str, Any]:
        """Auto-cura del sistema."""
        pass
    
    @abstractmethod
    async def predict_system_load(self, horizon_minutes: int = 60) -> Dict[str, Any]:
        """Predice carga del sistema."""
        pass
    
    @abstractmethod
    async def evolve_parameters(self, component_name: str) -> Dict[str, Any]:
        """Evoluciona parámetros de un componente."""
        pass

# =============================================================================
# 🔧 SERVICE INTERFACES
# =============================================================================

class BlatamService(BlatamComponent):
    """Interface base para servicios."""
    
    @property
    @abstractmethod
    def service_type(self) -> str:
        """Tipo de servicio."""
        pass
    
    @abstractmethod
    async def start_service(self) -> bool:
        """Inicia el servicio."""
        pass
    
    @abstractmethod
    async def stop_service(self) -> bool:
        """Detiene el servicio."""
        pass

class ProcessingService(BlatamService):
    """Interface para servicios de procesamiento."""
    
    @abstractmethod
    async def process_enterprise_data(self, data: Any, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Procesa datos empresariales."""
        pass
    
    @abstractmethod
    async def process_batch(self, items: List[Any], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Procesa lote de datos."""
        pass

class OptimizationService(BlatamService):
    """Interface para servicios de optimización."""
    
    @abstractmethod
    async def optimize_component(self, component: OptimizableComponent, strategy: OptimizationStrategy) -> Dict[str, Any]:
        """Optimiza un componente."""
        pass
    
    @abstractmethod
    async def analyze_performance(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analiza rendimiento."""
        pass

class MonitoringService(BlatamService):
    """Interface para servicios de monitoreo."""
    
    @abstractmethod
    async def collect_metrics(self, component: BlatamComponent) -> Dict[str, Any]:
        """Recolecta métricas."""
        pass
    
    @abstractmethod
    async def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detecta anomalías."""
        pass
    
    @abstractmethod
    async def generate_alerts(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Genera alertas."""
        pass

# =============================================================================
# 🏭 FACTORY INTERFACES
# =============================================================================

T = TypeVar('T', bound=BlatamComponent)

class ComponentFactory(Generic[T], ABC):
    """Interface base para factories de componentes."""
    
    @abstractmethod
    async def create(self, config: Dict[str, Any], **kwargs) -> T:
        """Crea un componente."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configuración."""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Obtiene configuración por defecto."""
        pass

class EngineFactory(ComponentFactory[AIEngine]):
    """Interface para factories de motores."""
    
    @abstractmethod
    def get_engine_type(self) -> str:
        """Obtiene tipo de motor que crea."""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Obtiene dependencias del motor."""
        pass

class ServiceFactory(ComponentFactory[BlatamService]):
    """Interface para factories de servicios."""
    
    @abstractmethod
    def get_service_type(self) -> str:
        """Obtiene tipo de servicio que crea."""
        pass

# =============================================================================
# 📊 EVENT INTERFACES
# =============================================================================

class EventHandler(ABC):
    """Interface para manejadores de eventos."""
    
    @abstractmethod
    async def handle(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Maneja un evento."""
        pass
    
    @abstractmethod
    def get_supported_events(self) -> List[str]:
        """Obtiene eventos soportados."""
        pass

class EventPublisher(ABC):
    """Interface para publicadores de eventos."""
    
    @abstractmethod
    async def publish(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Publica un evento."""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: EventHandler) -> bool:
        """Suscribe un manejador."""
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_type: str, handler: EventHandler) -> bool:
        """Desuscribe un manejador."""
        pass

# =============================================================================
# ⚙️ CONFIGURATION INTERFACES
# =============================================================================

class ConfigurationProvider(ABC):
    """Interface para proveedores de configuración."""
    
    @abstractmethod
    async def get_config(self, key: str) -> Optional[Any]:
        """Obtiene configuración."""
        pass
    
    @abstractmethod
    async def set_config(self, key: str, value: Any) -> bool:
        """Establece configuración."""
        pass
    
    @abstractmethod
    async def reload_config(self) -> bool:
        """Recarga configuración."""
        pass
    
    @abstractmethod
    def watch_config(self, key: str, callback) -> bool:
        """Observa cambios en configuración."""
        pass

# =============================================================================
# 🌟 EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ComponentStatus", "ProcessingType", "OptimizationStrategy",
    
    # Base interfaces
    "BlatamComponent", "ProcessingComponent", "OptimizableComponent", 
    "LearningComponent", "CacheableComponent",
    
    # Engine interfaces
    "AIEngine", "SpeedEngine", "NLPEngine", "LangChainEngine", "EvolutionEngine",
    
    # Service interfaces
    "BlatamService", "ProcessingService", "OptimizationService", "MonitoringService",
    
    # Factory interfaces
    "ComponentFactory", "EngineFactory", "ServiceFactory",
    
    # Event interfaces
    "EventHandler", "EventPublisher",
    
    # Configuration interfaces
    "ConfigurationProvider"
] 