"""
Sistema de Integración Modular para Acumulación de Gradientes
Integra todos los módulos modulares en un sistema unificado
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import yaml
from pathlib import Path

# Importar módulos modulares
from modular_optimizer import ModularOptimizer
from modular_config import ConfigBuilder, ConfigManager
from modular_monitoring import MonitoringSystem, MetricFactory

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuración para el sistema de integración."""
    enable_optimization: bool = True
    enable_monitoring: bool = True
    enable_config_management: bool = True
    auto_reload_config: bool = True
    config_file: str = "integration_config.yaml"
    log_level: str = "INFO"
    metrics_interval: float = 1.0
    optimization_interval: float = 5.0

class IntegrationEvent:
    """Evento de integración del sistema."""
    
    def __init__(self, event_type: str, data: Dict[str, Any], timestamp: float = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or asyncio.get_event_loop().time()
    
    def __str__(self):
        return f"IntegrationEvent({self.event_type}, {self.data}, {self.timestamp})"

class IntegrationObserver(ABC):
    """Observador abstracto para eventos de integración."""
    
    @abstractmethod
    async def on_integration_event(self, event: IntegrationEvent):
        """Manejar evento de integración."""
        pass

class IntegrationLogger(IntegrationObserver):
    """Logger para eventos de integración."""
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = logging.getLogger(f"IntegrationLogger")
        self.logger.setLevel(getattr(logging, log_level.upper()))
    
    async def on_integration_event(self, event: IntegrationEvent):
        """Loggear evento de integración."""
        self.logger.info(f"Integration Event: {event.event_type} - {event.data}")

class IntegrationMetrics(IntegrationObserver):
    """Métricas para eventos de integración."""
    
    def __init__(self):
        self.event_counts = {}
        self.event_timestamps = []
    
    async def on_integration_event(self, event: IntegrationEvent):
        """Registrar métricas del evento."""
        if event.event_type not in self.event_counts:
            self.event_counts[event.event_type] = 0
        self.event_counts[event.event_type] += 1
        self.event_timestamps.append(event.timestamp)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas actuales."""
        return {
            'event_counts': self.event_counts.copy(),
            'total_events': len(self.event_timestamps),
            'latest_event': max(self.event_timestamps) if self.event_timestamps else None
        }

class ModularIntegrationSystem:
    """Sistema principal de integración modular."""
    
    def __init__(self, config: IntegrationConfig = None):
        self.config = config or IntegrationConfig()
        self.optimizer: Optional[ModularOptimizer] = None
        self.monitoring: Optional[MonitoringSystem] = None
        self.config_manager: Optional[ConfigManager] = None
        
        # Sistema de eventos
        self.observers: List[IntegrationObserver] = []
        self.event_queue = asyncio.Queue()
        self.running = False
        
        # Configurar logging
        logging.getLogger().setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Inicializar componentes
        self._initialize_components()
        self._setup_default_observers()
    
    def _initialize_components(self):
        """Inicializar componentes modulares."""
        logger.info("🔧 Inicializando componentes modulares...")
        
        # Inicializar sistema de optimización
        if self.config.enable_optimization:
            self.optimizer = ModularOptimizer()
            logger.info("✅ Sistema de optimización inicializado")
        
        # Inicializar sistema de monitoreo
        if self.config.enable_monitoring:
            self.monitoring = MonitoringSystem()
            logger.info("✅ Sistema de monitoreo inicializado")
        
        # Inicializar gestor de configuración
        if self.config.enable_config_management:
            self.config_manager = ConfigManager()
            logger.info("✅ Gestor de configuración inicializado")
    
    def _setup_default_observers(self):
        """Configurar observadores por defecto."""
        self.add_observer(IntegrationLogger(self.config.log_level))
        self.add_observer(IntegrationMetrics())
        logger.info("✅ Observadores por defecto configurados")
    
    def add_observer(self, observer: IntegrationObserver):
        """Agregar observador de integración."""
        self.observers.append(observer)
        logger.info(f"✅ Observador agregado: {observer.__class__.__name__}")
    
    async def _notify_observers(self, event: IntegrationEvent):
        """Notificar a todos los observadores."""
        for observer in self.observers:
            try:
                await observer.on_integration_event(event)
            except Exception as e:
                logger.error(f"Error notificando observador {observer.__class__.__name__}: {e}")
    
    async def _event_processor(self):
        """Procesador de eventos de integración."""
        while self.running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._notify_observers(event)
                self.event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error procesando evento: {e}")
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emitir evento de integración."""
        event = IntegrationEvent(event_type, data)
        await self.event_queue.put(event)
        logger.debug(f"Evento emitido: {event}")
    
    async def start(self):
        """Iniciar sistema de integración."""
        if self.running:
            logger.warning("⚠️ Sistema ya está ejecutándose")
            return
        
        logger.info("🚀 Iniciando sistema de integración modular...")
        self.running = True
        
        # Iniciar procesador de eventos
        asyncio.create_task(self._event_processor())
        
        # Iniciar sistema de monitoreo
        if self.monitoring:
            self.monitoring.start()
            await self.emit_event("monitoring_started", {"status": "active"})
        
        # Iniciar tareas de optimización
        if self.optimizer:
            asyncio.create_task(self._optimization_loop())
            await self.emit_event("optimization_started", {"status": "active"})
        
        # Iniciar gestión de configuración
        if self.config_manager and self.config.auto_reload_config:
            asyncio.create_task(self._config_watcher())
            await self.emit_event("config_watcher_started", {"status": "active"})
        
        logger.info("✅ Sistema de integración iniciado exitosamente")
        await self.emit_event("system_started", {"status": "active"})
    
    async def stop(self):
        """Detener sistema de integración."""
        if not self.running:
            logger.warning("⚠️ Sistema ya está detenido")
            return
        
        logger.info("🛑 Deteniendo sistema de integración modular...")
        self.running = False
        
        # Detener sistema de monitoreo
        if self.monitoring:
            self.monitoring.stop()
            await self.emit_event("monitoring_stopped", {"status": "inactive"})
        
        # Esperar a que se procesen todos los eventos
        await self.event_queue.join()
        
        logger.info("✅ Sistema de integración detenido exitosamente")
        await self.emit_event("system_stopped", {"status": "inactive"})
    
    async def _optimization_loop(self):
        """Bucle de optimización continua."""
        while self.running:
            try:
                # Obtener contexto actual del sistema
                context = await self._get_system_context()
                
                # Aplicar optimizaciones si es necesario
                if context.get('needs_optimization', False):
                    result = self.optimizer.optimize(context)
                    await self.emit_event("optimization_applied", {
                        "context": context,
                        "result": result
                    })
                
                # Esperar hasta la próxima iteración
                await asyncio.sleep(self.config.optimization_interval)
                
            except Exception as e:
                logger.error(f"Error en bucle de optimización: {e}")
                await asyncio.sleep(1.0)
    
    async def _config_watcher(self):
        """Observador de cambios de configuración."""
        config_file = Path(self.config.config_file)
        last_modified = config_file.stat().st_mtime if config_file.exists() else 0
        
        while self.running:
            try:
                if config_file.exists():
                    current_modified = config_file.stat().st_mtime
                    if current_modified > last_modified:
                        logger.info(f"📝 Archivo de configuración modificado: {self.config.config_file}")
                        await self._reload_config()
                        last_modified = current_modified
                        await self.emit_event("config_reloaded", {"file": str(config_file)})
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error en observador de configuración: {e}")
                await asyncio.sleep(5.0)
    
    async def _reload_config(self):
        """Recargar configuración del sistema."""
        try:
            if self.config_manager:
                # Recargar configuración
                await self.emit_event("config_reload_started", {"status": "reloading"})
                
                # Aquí se implementaría la lógica de recarga
                # Por ahora solo emitimos el evento
                
                await self.emit_event("config_reload_completed", {"status": "reloaded"})
                
        except Exception as e:
            logger.error(f"Error recargando configuración: {e}")
            await self.emit_event("config_reload_failed", {"error": str(e)})
    
    async def _get_system_context(self) -> Dict[str, Any]:
        """Obtener contexto actual del sistema."""
        context = {
            'timestamp': asyncio.get_event_loop().time(),
            'system_status': 'running' if self.running else 'stopped'
        }
        
        # Agregar métricas del sistema si están disponibles
        if self.monitoring:
            try:
                # Obtener métricas del sistema de monitoreo
                # Por ahora usamos métricas simuladas
                context.update({
                    'memory_usage': 0.75,  # Simulado
                    'cpu_usage': 0.60,     # Simulado
                    'gpu_usage': 0.80,     # Simulado
                    'needs_optimization': True  # Simulado
                })
            except Exception as e:
                logger.warning(f"No se pudieron obtener métricas del sistema: {e}")
        
        return context
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado actual del sistema."""
        return {
            'running': self.running,
            'components': {
                'optimizer': self.optimizer is not None,
                'monitoring': self.monitoring is not None,
                'config_manager': self.config_manager is not None
            },
            'observers_count': len(self.observers),
            'config': {
                'enable_optimization': self.config.enable_optimization,
                'enable_monitoring': self.config.enable_monitoring,
                'enable_config_management': self.config.enable_config_management,
                'auto_reload_config': self.config.auto_reload_config
            }
        }
    
    async def apply_optimization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Aplicar optimización manual."""
        if not self.optimizer:
            raise RuntimeError("Sistema de optimización no disponible")
        
        try:
            result = self.optimizer.optimize(context)
            await self.emit_event("manual_optimization_applied", {
                "context": context,
                "result": result
            })
            return result
        except Exception as e:
            logger.error(f"Error aplicando optimización manual: {e}")
            await self.emit_event("optimization_failed", {"error": str(e)})
            raise
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema."""
        metrics = {
            'timestamp': asyncio.get_event_loop().time(),
            'system_status': self.get_system_status()
        }
        
        # Agregar métricas de observadores
        for observer in self.observers:
            if hasattr(observer, 'get_metrics'):
                try:
                    observer_metrics = observer.get_metrics()
                    metrics[f"{observer.__class__.__name__}_metrics"] = observer_metrics
                except Exception as e:
                    logger.warning(f"No se pudieron obtener métricas de {observer.__class__.__name__}: {e}")
        
        return metrics

# Funciones de utilidad para el sistema de integración

async def create_integration_system(config_file: str = None) -> ModularIntegrationSystem:
    """Crear sistema de integración desde archivo de configuración."""
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Crear configuración desde datos del archivo
            config = IntegrationConfig(**config_data)
            logger.info(f"✅ Configuración cargada desde: {config_file}")
            
        except Exception as e:
            logger.error(f"Error cargando configuración desde {config_file}: {e}")
            config = IntegrationConfig()
    else:
        config = IntegrationConfig()
    
    return ModularIntegrationSystem(config)

async def run_integration_demo():
    """Ejecutar demostración del sistema de integración."""
    logger.info("🎯 Iniciando demostración del sistema de integración modular...")
    
    # Crear sistema de integración
    system = await create_integration_system()
    
    try:
        # Iniciar sistema
        await system.start()
        
        # Simular algunas operaciones
        await asyncio.sleep(2)
        
        # Obtener estado del sistema
        status = system.get_system_status()
        logger.info(f"Estado del sistema: {status}")
        
        # Aplicar optimización manual
        context = {'memory_pressure': 0.9, 'computation_load': 0.8}
        result = await system.apply_optimization(context)
        logger.info(f"Optimización aplicada: {result}")
        
        # Obtener métricas del sistema
        metrics = await system.get_system_metrics()
        logger.info(f"Métricas del sistema: {metrics}")
        
        # Mantener sistema ejecutándose por un tiempo
        await asyncio.sleep(10)
        
    finally:
        # Detener sistema
        await system.stop()
    
    logger.info("✅ Demostración del sistema de integración completada")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(run_integration_demo())
