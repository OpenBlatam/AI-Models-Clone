"""
Arquitectura de Microservicios para Sistema de Acumulación de Gradientes
Implementa patrones de microservicios con comunicación asíncrona y escalabilidad
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import uuid
import time
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Estados de los microservicios."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class ServiceType(Enum):
    """Tipos de microservicios."""
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"
    CONFIGURATION = "configuration"
    GRADIENT_ACCUMULATION = "gradient_accumulation"
    MEMORY_MANAGEMENT = "memory_management"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ALERTING = "alerting"
    METRICS_STORAGE = "metrics_storage"

@dataclass
class ServiceConfig:
    """Configuración de microservicio."""
    service_id: str
    service_type: ServiceType
    host: str = "localhost"
    port: int = 8000
    health_check_interval: float = 5.0
    max_retries: int = 3
    timeout: float = 30.0
    dependencies: List[str] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)

@dataclass
class ServiceMessage:
    """Mensaje entre microservicios."""
    message_id: str
    source_service: str
    target_service: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float
    correlation_id: Optional[str] = None
    priority: int = 0

class ServiceRegistry:
    """Registro de servicios para descubrimiento."""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.health_status: Dict[str, ServiceStatus] = {}
        self.service_endpoints: Dict[str, str] = {}
    
    def register_service(self, service_config: ServiceConfig):
        """Registrar un nuevo servicio."""
        self.services[service_config.service_id] = service_config
        self.health_status[service_config.service_id] = ServiceStatus.STARTING
        endpoint = f"http://{service_config.host}:{service_config.port}"
        self.service_endpoints[service_config.service_id] = endpoint
        logger.info(f"✅ Servicio registrado: {service_config.service_id} en {endpoint}")
    
    def unregister_service(self, service_id: str):
        """Desregistrar un servicio."""
        if service_id in self.services:
            del self.services[service_id]
            del self.health_status[service_id]
            del self.service_endpoints[service_id]
            logger.info(f"❌ Servicio desregistrado: {service_id}")
    
    def get_service_endpoint(self, service_id: str) -> Optional[str]:
        """Obtener endpoint de un servicio."""
        return self.service_endpoints.get(service_id)
    
    def update_health_status(self, service_id: str, status: ServiceStatus):
        """Actualizar estado de salud de un servicio."""
        if service_id in self.health_status:
            self.health_status[service_id] = status
            logger.debug(f"Estado de salud actualizado: {service_id} -> {status.value}")
    
    def get_healthy_services(self, service_type: ServiceType = None) -> List[str]:
        """Obtener servicios saludables."""
        healthy = []
        for service_id, status in self.health_status.items():
            if status in [ServiceStatus.RUNNING, ServiceStatus.HEALTHY]:
                if service_type is None or self.services[service_id].service_type == service_type:
                    healthy.append(service_id)
        return healthy

class MessageBroker:
    """Broker de mensajes para comunicación entre servicios."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.processing_task = None
    
    async def start(self):
        """Iniciar broker de mensajes."""
        if self.running:
            return
        
        self.running = True
        self.processing_task = asyncio.create_task(self._process_messages())
        logger.info("🚀 Broker de mensajes iniciado")
    
    async def stop(self):
        """Detener broker de mensajes."""
        if not self.running:
            return
        
        self.running = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Broker de mensajes detenido")
    
    def subscribe(self, message_type: str, callback: Callable):
        """Suscribirse a un tipo de mensaje."""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []
        self.subscribers[message_type].append(callback)
        logger.debug(f"Suscripción agregada: {message_type} -> {callback.__name__}")
    
    def unsubscribe(self, message_type: str, callback: Callable):
        """Desuscribirse de un tipo de mensaje."""
        if message_type in self.subscribers and callback in self.subscribers[message_type]:
            self.subscribers[message_type].remove(callback)
            logger.debug(f"Suscripción removida: {message_type} -> {callback.__name__}")
    
    async def publish(self, message: ServiceMessage):
        """Publicar un mensaje."""
        await self.message_queue.put(message)
        logger.debug(f"Mensaje publicado: {message.message_type} de {message.source_service}")
    
    async def _process_messages(self):
        """Procesar mensajes en cola."""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Notificar a suscriptores
                if message.message_type in self.subscribers:
                    for callback in self.subscribers[message.message_type]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(message)
                            else:
                                callback(message)
                        except Exception as e:
                            logger.error(f"Error en callback {callback.__name__}: {e}")
                
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")

class BaseMicroservice(ABC):
    """Clase base para microservicios."""
    
    def __init__(self, service_config: ServiceConfig, message_broker: MessageBroker, service_registry: ServiceRegistry):
        self.config = service_config
        self.broker = message_broker
        self.registry = service_registry
        self.status = ServiceStatus.STOPPED
        self.health_check_task = None
        self.running = False
        
        # Configurar suscripciones
        self._setup_subscriptions()
    
    @abstractmethod
    def _setup_subscriptions(self):
        """Configurar suscripciones a mensajes."""
        pass
    
    @abstractmethod
    async def process_message(self, message: ServiceMessage):
        """Procesar mensaje recibido."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verificar salud del servicio."""
        pass
    
    async def start(self):
        """Iniciar microservicio."""
        if self.running:
            return
        
        logger.info(f"🚀 Iniciando microservicio: {self.config.service_id}")
        self.status = ServiceStatus.STARTING
        self.running = True
        
        # Registrar en el registro de servicios
        self.registry.register_service(self.config)
        
        # Iniciar health check
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Marcar como ejecutándose
        self.status = ServiceStatus.RUNNING
        self.registry.update_health_status(self.config.service_id, ServiceStatus.RUNNING)
        
        logger.info(f"✅ Microservicio iniciado: {self.config.service_id}")
    
    async def stop(self):
        """Detener microservicio."""
        if not self.running:
            return
        
        logger.info(f"🛑 Deteniendo microservicio: {self.config.service_id}")
        self.status = ServiceStatus.STOPPING
        self.running = False
        
        # Cancelar health check
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Desregistrar del registro
        self.registry.unregister_service(self.config.service_id)
        
        self.status = ServiceStatus.STOPPED
        logger.info(f"✅ Microservicio detenido: {self.config.service_id}")
    
    async def _health_check_loop(self):
        """Bucle de verificación de salud."""
        while self.running:
            try:
                is_healthy = await self.health_check()
                
                if is_healthy:
                    self.status = ServiceStatus.HEALTHY
                    self.registry.update_health_status(self.config.service_id, ServiceStatus.HEALTHY)
                else:
                    self.status = ServiceStatus.UNHEALTHY
                    self.registry.update_health_status(self.config.service_id, ServiceStatus.UNHEALTHY)
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error en health check de {self.config.service_id}: {e}")
                self.status = ServiceStatus.ERROR
                self.registry.update_health_status(self.config.service_id, ServiceStatus.ERROR)
                await asyncio.sleep(1.0)
    
    async def send_message(self, target_service: str, message_type: str, payload: Dict[str, Any], priority: int = 0):
        """Enviar mensaje a otro servicio."""
        message = ServiceMessage(
            message_id=str(uuid.uuid4()),
            source_service=self.config.service_id,
            target_service=target_service,
            message_type=message_type,
            payload=payload,
            timestamp=time.time(),
            priority=priority
        )
        
        await self.broker.publish(message)
        logger.debug(f"Mensaje enviado: {message_type} -> {target_service}")

class OptimizationMicroservice(BaseMicroservice):
    """Microservicio de optimización."""
    
    def _setup_subscriptions(self):
        """Configurar suscripciones."""
        self.broker.subscribe("optimization_request", self.process_message)
        self.broker.subscribe("performance_metrics", self.process_message)
    
    async def process_message(self, message: ServiceMessage):
        """Procesar mensaje de optimización."""
        if message.message_type == "optimization_request":
            await self._handle_optimization_request(message)
        elif message.message_type == "performance_metrics":
            await self._handle_performance_metrics(message)
    
    async def _handle_optimization_request(self, message: ServiceMessage):
        """Manejar solicitud de optimización."""
        try:
            context = message.payload.get('context', {})
            
            # Aplicar optimizaciones basadas en el contexto
            optimization_result = await self._apply_optimizations(context)
            
            # Enviar resultado
            await self.send_message(
                message.source_service,
                "optimization_result",
                {
                    'request_id': message.message_id,
                    'result': optimization_result,
                    'timestamp': time.time()
                }
            )
            
            logger.info(f"Optimización aplicada para {message.source_service}")
            
        except Exception as e:
            logger.error(f"Error en optimización: {e}")
            await self.send_message(
                message.source_service,
                "optimization_error",
                {
                    'request_id': message.message_id,
                    'error': str(e),
                    'timestamp': time.time()
                }
            )
    
    async def _handle_performance_metrics(self, message: ServiceMessage):
        """Manejar métricas de rendimiento."""
        metrics = message.payload.get('metrics', {})
        
        # Analizar métricas y determinar si se necesita optimización
        if self._needs_optimization(metrics):
            await self.send_message(
                message.source_service,
                "optimization_recommendation",
                {
                    'reason': 'performance_threshold_exceeded',
                    'metrics': metrics,
                    'timestamp': time.time()
                }
            )
    
    async def _apply_optimizations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Aplicar optimizaciones basadas en el contexto."""
        optimizations = []
        
        # Optimización de memoria
        if context.get('memory_pressure', 0) > 0.8:
            optimizations.append({
                'type': 'memory_optimization',
                'action': 'garbage_collection',
                'priority': 'high'
            })
        
        # Optimización de GPU
        if context.get('gpu_usage', 0) > 0.9:
            optimizations.append({
                'type': 'gpu_optimization',
                'action': 'memory_cleanup',
                'priority': 'critical'
            })
        
        # Optimización de cómputo
        if context.get('cpu_usage', 0) > 0.85:
            optimizations.append({
                'type': 'computation_optimization',
                'action': 'batch_size_reduction',
                'priority': 'medium'
            })
        
        return {
            'optimizations_applied': optimizations,
            'context': context,
            'timestamp': time.time()
        }
    
    def _needs_optimization(self, metrics: Dict[str, Any]) -> bool:
        """Determinar si se necesita optimización basada en métricas."""
        memory_pressure = metrics.get('memory_pressure', 0)
        cpu_usage = metrics.get('cpu_usage', 0)
        gpu_usage = metrics.get('gpu_usage', 0)
        
        return memory_pressure > 0.8 or cpu_usage > 0.85 or gpu_usage > 0.9
    
    async def health_check(self) -> bool:
        """Verificar salud del servicio de optimización."""
        # Verificar que el servicio puede procesar mensajes
        return self.running and self.status in [ServiceStatus.RUNNING, ServiceStatus.HEALTHY]

class MonitoringMicroservice(BaseMicroservice):
    """Microservicio de monitoreo."""
    
    def _setup_subscriptions(self):
        """Configurar suscripciones."""
        self.broker.subscribe("metrics_collection", self.process_message)
        self.broker.subscribe("health_check_request", self.process_message)
    
    async def process_message(self, message: ServiceMessage):
        """Procesar mensaje de monitoreo."""
        if message.message_type == "metrics_collection":
            await self._handle_metrics_collection(message)
        elif message.message_type == "health_check_request":
            await self._handle_health_check_request(message)
    
    async def _handle_metrics_collection(self, message: ServiceMessage):
        """Manejar recolección de métricas."""
        try:
            metrics = message.payload.get('metrics', {})
            service_id = message.source_service
            
            # Procesar y almacenar métricas
            processed_metrics = await self._process_metrics(metrics, service_id)
            
            # Enviar métricas procesadas
            await self.send_message(
                message.source_service,
                "metrics_processed",
                {
                    'original_metrics': metrics,
                    'processed_metrics': processed_metrics,
                    'timestamp': time.time()
                }
            )
            
            # Verificar si se necesitan alertas
            if self._should_alert(processed_metrics):
                await self.send_message(
                    "alerting",
                    "alert_triggered",
                    {
                        'service_id': service_id,
                        'metrics': processed_metrics,
                        'alert_level': 'warning',
                        'timestamp': time.time()
                    }
                )
            
            logger.debug(f"Métricas procesadas para {service_id}")
            
        except Exception as e:
            logger.error(f"Error procesando métricas: {e}")
    
    async def _handle_health_check_request(self, message: ServiceMessage):
        """Manejar solicitud de health check."""
        try:
            service_id = message.payload.get('service_id')
            health_status = self.registry.health_status.get(service_id, ServiceStatus.UNKNOWN)
            
            await self.send_message(
                message.source_service,
                "health_check_response",
                {
                    'service_id': service_id,
                    'status': health_status.value,
                    'timestamp': time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Error en health check: {e}")
    
    async def _process_metrics(self, metrics: Dict[str, Any], service_id: str) -> Dict[str, Any]:
        """Procesar métricas del servicio."""
        processed = {
            'service_id': service_id,
            'timestamp': time.time(),
            'raw_metrics': metrics,
            'calculated_metrics': {}
        }
        
        # Calcular métricas derivadas
        if 'memory_usage' in metrics:
            processed['calculated_metrics']['memory_efficiency'] = 1.0 - metrics['memory_usage']
        
        if 'cpu_usage' in metrics:
            processed['calculated_metrics']['cpu_efficiency'] = 1.0 - metrics['cpu_usage']
        
        if 'gpu_usage' in metrics:
            processed['calculated_metrics']['gpu_efficiency'] = 1.0 - metrics['gpu_usage']
        
        return processed
    
    def _should_alert(self, metrics: Dict[str, Any]) -> bool:
        """Determinar si se debe generar una alerta."""
        raw_metrics = metrics.get('raw_metrics', {})
        
        memory_usage = raw_metrics.get('memory_usage', 0)
        cpu_usage = raw_metrics.get('cpu_usage', 0)
        gpu_usage = raw_metrics.get('gpu_usage', 0)
        
        return memory_usage > 0.9 or cpu_usage > 0.9 or gpu_usage > 0.95
    
    async def health_check(self) -> bool:
        """Verificar salud del servicio de monitoreo."""
        return self.running and self.status in [ServiceStatus.RUNNING, ServiceStatus.HEALTHY]

class MicroservicesOrchestrator:
    """Orquestador de microservicios."""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.broker = MessageBroker()
        self.services: Dict[str, BaseMicroservice] = {}
        self.running = False
    
    async def start(self):
        """Iniciar orquestador."""
        if self.running:
            return
        
        logger.info("🚀 Iniciando orquestador de microservicios...")
        
        # Iniciar broker de mensajes
        await self.broker.start()
        
        # Crear e iniciar microservicios
        await self._create_services()
        await self._start_services()
        
        self.running = True
        logger.info("✅ Orquestador de microservicios iniciado")
    
    async def stop(self):
        """Detener orquestador."""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo orquestador de microservicios...")
        
        # Detener servicios
        await self._stop_services()
        
        # Detener broker
        await self.broker.stop()
        
        self.running = False
        logger.info("✅ Orquestador de microservicios detenido")
    
    async def _create_services(self):
        """Crear instancias de microservicios."""
        # Servicio de optimización
        optimization_config = ServiceConfig(
            service_id="optimization_service",
            service_type=ServiceType.OPTIMIZATION,
            port=8001,
            health_check_interval=3.0
        )
        
        # Servicio de monitoreo
        monitoring_config = ServiceConfig(
            service_id="monitoring_service",
            service_type=ServiceType.MONITORING,
            port=8002,
            health_check_interval=2.0
        )
        
        # Crear servicios
        self.services["optimization_service"] = OptimizationMicroservice(
            optimization_config, self.broker, self.registry
        )
        
        self.services["monitoring_service"] = MonitoringMicroservice(
            monitoring_config, self.broker, self.registry
        )
        
        logger.info(f"✅ {len(self.services)} microservicios creados")
    
    async def _start_services(self):
        """Iniciar todos los servicios."""
        for service in self.services.values():
            await service.start()
    
    async def _stop_services(self):
        """Detener todos los servicios."""
        for service in self.services.values():
            await service.stop()
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtener estado de todos los servicios."""
        status = {
            'orchestrator_running': self.running,
            'services': {}
        }
        
        for service_id, service in self.services.items():
            status['services'][service_id] = {
                'status': service.status.value,
                'running': service.running,
                'config': {
                    'service_type': service.config.service_type.value,
                    'host': service.config.host,
                    'port': service.config.port
                }
            }
        
        return status
    
    async def send_message_to_service(self, service_id: str, message_type: str, payload: Dict[str, Any]):
        """Enviar mensaje a un servicio específico."""
        if service_id in self.services:
            await self.services[service_id].send_message(service_id, message_type, payload)
        else:
            logger.warning(f"Servicio no encontrado: {service_id}")

async def run_microservices_demo():
    """Ejecutar demostración de microservicios."""
    logger.info("🎯 Iniciando demostración de arquitectura de microservicios...")
    
    # Crear orquestador
    orchestrator = MicroservicesOrchestrator()
    
    try:
        # Iniciar orquestador
        await orchestrator.start()
        
        # Simular operaciones
        await asyncio.sleep(2)
        
        # Obtener estado del sistema
        status = orchestrator.get_service_status()
        logger.info(f"Estado del sistema: {json.dumps(status, indent=2)}")
        
        # Simular solicitud de optimización
        await orchestrator.send_message_to_service(
            "optimization_service",
            "optimization_request",
            {
                'context': {
                    'memory_pressure': 0.85,
                    'cpu_usage': 0.75,
                    'gpu_usage': 0.92
                }
            }
        )
        
        # Simular recolección de métricas
        await orchestrator.send_message_to_service(
            "monitoring_service",
            "metrics_collection",
            {
                'metrics': {
                    'memory_usage': 0.88,
                    'cpu_usage': 0.78,
                    'gpu_usage': 0.94
                }
            }
        )
        
        # Mantener sistema ejecutándose
        await asyncio.sleep(10)
        
    finally:
        # Detener orquestador
        await orchestrator.stop()
    
    logger.info("✅ Demostración de microservicios completada")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(run_microservices_demo())
