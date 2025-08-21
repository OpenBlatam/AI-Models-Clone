from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Protocol
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from datetime import datetime
from typing import Any, List, Dict, Optional
import asyncio
"""
🏗️ BLATAM AI CORE MODULE v5.0.0
==============================

Módulo core con interfaces base y configuraciones centralizadas:
- 🔧 Base interfaces y abstract classes
- ⚙️ Configuraciones centralizadas y tipadas
- 🏭 Factory patterns y dependency injection
- 📊 Métricas y monitoring base
- 🔄 Event system y observers
- 🎯 Constants y enums
"""


logger = logging.getLogger(__name__)

# =============================================================================
# 🎯 SYSTEM ENUMS & CONSTANTS
# =============================================================================

class SystemMode(Enum):
    """Modos de operación del sistema."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class OptimizationLevel(Enum):
    """Niveles de optimización."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ULTRA = "ultra"
    QUANTUM = "quantum"

class ComponentStatus(Enum):
    """Estados de componentes."""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    OPTIMIZING = "optimizing"
    ERROR = "error"
    STOPPED = "stopped"

# =============================================================================
# 🔧 BASE INTERFACES
# =============================================================================

class BlatamComponent(ABC):
    """Interface base para todos los componentes del sistema."""
    
    @abstractmethod
    async def initialize(self, **kwargs) -> bool:
        """Inicializa el componente."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verifica la salud del componente."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del componente."""
        pass
    
    @property
    @abstractmethod
    def status(self) -> ComponentStatus:
        """Estado actual del componente."""
        pass

class OptimizableComponent(BlatamComponent):
    """Interface para componentes optimizables."""
    
    @abstractmethod
    async def optimize(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza el componente basado en métricas."""
        pass
    
    @abstractmethod
    async def record_performance(self, operation: str, duration_ms: float, success: bool):
        """Registra métricas de rendimiento."""
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

# =============================================================================
# 📊 METRICS & MONITORING
# =============================================================================

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento estandarizadas."""
    response_time_ms: float = 0.0
    throughput_rps: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    cache_hit_rate: float = 0.0
    accuracy: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class SystemHealth:
    """Estado de salud del sistema."""
    overall_status: ComponentStatus = ComponentStatus.READY
    components: Dict[str, ComponentStatus] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.now)
    uptime_seconds: float = 0.0

class MetricsCollector:
    """Recolector centralizado de métricas."""
    
    def __init__(self) -> Any:
        self.metrics_history: List[PerformanceMetrics] = []
        self.component_metrics: Dict[str, List[PerformanceMetrics]] = {}
    
    def record_metrics(self, component: str, metrics: PerformanceMetrics):
        """Registra métricas de un componente."""
        if component not in self.component_metrics:
            self.component_metrics[component] = []
        
        self.component_metrics[component].append(metrics)
        self.metrics_history.append(metrics)
        
        # Mantener solo últimas 10000 métricas
        if len(self.metrics_history) > 10000:
            self.metrics_history = self.metrics_history[-10000:]
    
    def get_average_metrics(self, component: str, last_n: int = 100) -> Optional[PerformanceMetrics]:
        """Obtiene métricas promedio de un componente."""
        if component not in self.component_metrics:
            return None
        
        recent_metrics = self.component_metrics[component][-last_n:]
        if not recent_metrics:
            return None
        
        return PerformanceMetrics(
            response_time_ms=sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics),
            throughput_rps=sum(m.throughput_rps for m in recent_metrics) / len(recent_metrics),
            error_rate=sum(m.error_rate for m in recent_metrics) / len(recent_metrics),
            cpu_usage=sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            memory_usage_mb=sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics),
            cache_hit_rate=sum(m.cache_hit_rate for m in recent_metrics) / len(recent_metrics),
            accuracy=sum(m.accuracy for m in recent_metrics) / len(recent_metrics)
        )

# =============================================================================
# 🔄 EVENT SYSTEM
# =============================================================================

class EventType(Enum):
    """Tipos de eventos del sistema."""
    COMPONENT_INITIALIZED = "component_initialized"
    OPTIMIZATION_STARTED = "optimization_started"
    OPTIMIZATION_COMPLETED = "optimization_completed"
    PERFORMANCE_DEGRADED = "performance_degraded"
    ERROR_OCCURRED = "error_occurred"
    LEARNING_COMPLETED = "learning_completed"
    SELF_HEALING_TRIGGERED = "self_healing_triggered"

@dataclass
class SystemEvent:
    """Evento del sistema."""
    event_type: EventType
    component: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class EventObserver(ABC):
    """Observer para eventos del sistema."""
    
    @abstractmethod
    async def handle_event(self, event: SystemEvent):
        """Maneja un evento del sistema."""
        pass

class EventBus:
    """Bus de eventos centralizado."""
    
    def __init__(self) -> Any:
        self.observers: Dict[EventType, List[EventObserver]] = {}
    
    def subscribe(self, event_type: EventType, observer: EventObserver):
        """Suscribe un observer a un tipo de evento."""
        if event_type not in self.observers:
            self.observers[event_type] = []
        self.observers[event_type].append(observer)
    
    async def publish(self, event: SystemEvent):
        """Publica un evento."""
        if event.event_type in self.observers:
            for observer in self.observers[event.event_type]:
                try:
                    await observer.handle_event(event)
                except Exception as e:
                    logger.error(f"Error in event observer: {e}")

# =============================================================================
# ⚙️ CENTRALIZED CONFIGURATION
# =============================================================================

@dataclass
class CoreConfig:
    """Configuración core del sistema."""
    system_mode: SystemMode = SystemMode.PRODUCTION
    optimization_level: OptimizationLevel = OptimizationLevel.ULTRA
    log_level: str = "INFO"
    metrics_retention_hours: int = 24
    health_check_interval_seconds: int = 60
    enable_auto_optimization: bool = True
    enable_self_healing: bool = True
    enable_continuous_learning: bool = True
    
    # Performance targets
    target_response_time_ms: float = 100.0
    target_throughput_rps: float = 1000.0
    target_error_rate: float = 0.01
    target_cpu_usage: float = 0.8
    target_memory_usage_gb: float = 8.0

@dataclass
class ComponentConfig:
    """Configuración base para componentes."""
    enabled: bool = True
    lazy_loading: bool = True
    cache_enabled: bool = True
    cache_size: int = 10000
    worker_threads: int = 4
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'enabled': self.enabled,
            'lazy_loading': self.lazy_loading,
            'cache_enabled': self.cache_enabled,
            'cache_size': self.cache_size,
            'worker_threads': self.worker_threads,
            'timeout_seconds': self.timeout_seconds,
            'retry_attempts': self.retry_attempts
        }

# =============================================================================
# 🏭 FACTORY PATTERN BASE
# =============================================================================

class ComponentFactory(ABC):
    """Factory base para componentes."""
    
    @abstractmethod
    async def create_component(self, config: ComponentConfig, **kwargs) -> BlatamComponent:
        """Crea un componente."""
        pass
    
    @abstractmethod
    def get_component_type(self) -> str:
        """Retorna el tipo de componente que crea."""
        pass

# =============================================================================
# 🎯 DEPENDENCY INJECTION
# =============================================================================

class ServiceContainer:
    """Contenedor de servicios para dependency injection."""
    
    def __init__(self) -> Any:
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, ComponentFactory] = {}
    
    def register_service(self, name: str, service: Any):
        """Registra un servicio."""
        self._services[name] = service
    
    def register_factory(self, component_type: str, factory: ComponentFactory):
        """Registra una factory."""
        self._factories[component_type] = factory
    
    def get_service(self, name: str) -> Optional[Dict[str, Any]]:
        """Obtiene un servicio."""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not found")
        return self._services[name]
    
    async def create_component(self, component_type: str, config: ComponentConfig, **kwargs) -> BlatamComponent:
        """Crea un componente usando factory."""
        if component_type not in self._factories:
            raise ValueError(f"Factory for '{component_type}' not found")
        
        factory = self._factories[component_type]
        return await factory.create_component(config, **kwargs)
    
    def list_services(self) -> List[str]:
        """Lista servicios disponibles."""
        return list(self._services.keys())
    
    def list_component_types(self) -> List[str]:
        """Lista tipos de componentes disponibles."""
        return list(self._factories.keys())

# =============================================================================
# 🔧 UTILITY FUNCTIONS
# =============================================================================

def create_default_config() -> CoreConfig:
    """Crea configuración por defecto."""
    return CoreConfig()

def create_component_config(**overrides) -> ComponentConfig:
    """Crea configuración de componente con overrides."""
    config = ComponentConfig()
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config

def format_duration_ms(duration_ms: float) -> str:
    """Formatea duración en ms."""
    if duration_ms < 1:
        return f"{duration_ms:.3f}ms"
    elif duration_ms < 1000:
        return f"{duration_ms:.1f}ms"
    else:
        return f"{duration_ms/1000:.2f}s"

def calculate_improvement_percentage(old_value: float, new_value: float) -> float:
    """Calcula porcentaje de mejora."""
    if old_value == 0:
        return 0.0
    return ((old_value - new_value) / old_value) * 100

# =============================================================================
# 🌟 EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "SystemMode", "OptimizationLevel", "ComponentStatus", "EventType",
    
    # Interfaces
    "BlatamComponent", "OptimizableComponent", "LearningComponent",
    
    # Data classes
    "PerformanceMetrics", "SystemHealth", "SystemEvent", "CoreConfig", "ComponentConfig",
    
    # Core classes
    "MetricsCollector", "EventObserver", "EventBus", "ComponentFactory", "ServiceContainer",
    
    # Utilities
    "create_default_config", "create_component_config", "format_duration_ms", "calculate_improvement_percentage"
] 