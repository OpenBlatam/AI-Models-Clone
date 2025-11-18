"""
Initialization System
=====================

Sistema de inicialización mejorado para el sistema.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from .health_check import get_health_check_system, create_basic_health_checks
from .metrics import get_metrics_collector
from .monitoring import get_monitoring_system
from .event_system import get_event_emitter
from .cache import get_cache_manager
from .extensions import get_extension_manager
from .plugin_system import get_plugin_manager
from .compatibility.compatibility import get_system_info, check_dependencies

logger = logging.getLogger(__name__)


class InitStage(Enum):
    """Etapas de inicialización."""
    CONFIG = "config"
    METRICS = "metrics"
    CACHE = "cache"
    EVENTS = "events"
    HEALTH = "health"
    MONITORING = "monitoring"
    EXTENSIONS = "extensions"
    PLUGINS = "plugins"
    COMPONENTS = "components"
    READY = "ready"


@dataclass
class InitResult:
    """Resultado de inicialización."""
    stage: InitStage
    success: bool
    message: str = ""
    duration: float = 0.0
    errors: List[str] = field(default_factory=list)


class SystemInitializer:
    """
    Inicializador del sistema.
    
    Gestiona la inicialización ordenada de todos los componentes.
    """
    
    def __init__(self):
        """Inicializar sistema de inicialización."""
        self.stages: Dict[InitStage, List[Callable]] = {}
        self.results: List[InitResult] = []
        self.initialized = False
    
    def register_stage(
        self,
        stage: InitStage,
        init_func: Callable[[], Any],
        order: int = 0
    ) -> None:
        """
        Registrar función de inicialización para etapa.
        
        Args:
            stage: Etapa de inicialización
            init_func: Función de inicialización
            order: Orden de ejecución (menor = primero)
        """
        if stage not in self.stages:
            self.stages[stage] = []
        
        self.stages[stage].append((order, init_func))
        self.stages[stage].sort(key=lambda x: x[0])
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Inicializar todo el sistema.
        
        Returns:
            Diccionario con resultados de inicialización
        """
        import time
        start_time = time.time()
        
        logger.info("=" * 60)
        logger.info("Initializing Robot Movement AI System")
        logger.info("=" * 60)
        
        # Inicializar en orden
        stages_order = [
            InitStage.CONFIG,
            InitStage.METRICS,
            InitStage.CACHE,
            InitStage.EVENTS,
            InitStage.HEALTH,
            InitStage.MONITORING,
            InitStage.EXTENSIONS,
            InitStage.PLUGINS,
            InitStage.COMPONENTS,
            InitStage.READY
        ]
        
        for stage in stages_order:
            result = await self._initialize_stage(stage)
            self.results.append(result)
            
            if not result.success:
                logger.error(f"Failed to initialize stage {stage.value}")
                if result.errors:
                    for error in result.errors:
                        logger.error(f"  - {error}")
                break
        
        total_duration = time.time() - start_time
        
        if all(r.success for r in self.results):
            self.initialized = True
            logger.info("=" * 60)
            logger.info("System initialization completed successfully!")
            logger.info(f"Total time: {total_duration:.3f}s")
            logger.info("=" * 60)
        else:
            logger.error("=" * 60)
            logger.error("System initialization failed!")
            logger.error("=" * 60)
        
        return {
            "success": self.initialized,
            "total_duration": total_duration,
            "stages": {
                r.stage.value: {
                    "success": r.success,
                    "message": r.message,
                    "duration": r.duration
                }
                for r in self.results
            }
        }
    
    async def _initialize_stage(self, stage: InitStage) -> InitResult:
        """Inicializar etapa específica."""
        import time
        start_time = time.time()
        
        logger.info(f"Initializing stage: {stage.value}")
        
        try:
            # Ejecutar funciones registradas
            if stage in self.stages:
                for _, init_func in self.stages[stage]:
                    if asyncio.iscoroutinefunction(init_func):
                        await init_func()
                    else:
                        init_func()
            
            # Inicialización por defecto según etapa
            await self._default_stage_init(stage)
            
            duration = time.time() - start_time
            logger.info(f"Stage {stage.value} initialized in {duration:.3f}s")
            
            return InitResult(
                stage=stage,
                success=True,
                message=f"Stage {stage.value} initialized successfully",
                duration=duration
            )
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error initializing stage {stage.value}: {e}")
            
            return InitResult(
                stage=stage,
                success=False,
                message=f"Error: {str(e)}",
                duration=duration,
                errors=[str(e)]
            )
    
    async def _default_stage_init(self, stage: InitStage) -> None:
        """Inicialización por defecto de etapas."""
        if stage == InitStage.METRICS:
            # Inicializar métricas
            collector = get_metrics_collector()
            collector.register_metric("system.initialization", unit="seconds")
        
        elif stage == InitStage.CACHE:
            # Inicializar cachés
            cache_manager = get_cache_manager()
            cache_manager.create_cache("default", cache_type="lru", maxsize=128)
        
        elif stage == InitStage.EVENTS:
            # Inicializar eventos
            emitter = get_event_emitter()
            # Eventos ya están listos
        
        elif stage == InitStage.HEALTH:
            # Inicializar health checks
            health_system = get_health_check_system()
            for check in create_basic_health_checks():
                health_system.register_check(check)
        
        elif stage == InitStage.MONITORING:
            # Inicializar monitoreo
            monitoring = get_monitoring_system()
            # Sistema listo
        
        elif stage == InitStage.EXTENSIONS:
            # Inicializar extensiones
            extension_manager = get_extension_manager()
            # Manager listo
        
        elif stage == InitStage.PLUGINS:
            # Inicializar plugins
            plugin_manager = get_plugin_manager()
            # Manager listo
        
        elif stage == InitStage.READY:
            # Sistema listo
            logger.info("System is ready!")
    
    def get_initialization_report(self) -> Dict[str, Any]:
        """Obtener reporte de inicialización."""
        return {
            "initialized": self.initialized,
            "stages": {
                r.stage.value: {
                    "success": r.success,
                    "message": r.message,
                    "duration": r.duration,
                    "errors": r.errors
                }
                for r in self.results
            },
            "total_stages": len(self.results),
            "successful_stages": sum(1 for r in self.results if r.success),
            "failed_stages": sum(1 for r in self.results if not r.success)
        }


# Instancia global
_system_initializer: Optional[SystemInitializer] = None


def get_system_initializer() -> SystemInitializer:
    """Obtener instancia global del inicializador."""
    global _system_initializer
    if _system_initializer is None:
        _system_initializer = SystemInitializer()
    return _system_initializer


async def initialize_system() -> Dict[str, Any]:
    """
    Inicializar todo el sistema.
    
    Returns:
        Resultado de inicialización
    """
    initializer = get_system_initializer()
    return await initializer.initialize()






