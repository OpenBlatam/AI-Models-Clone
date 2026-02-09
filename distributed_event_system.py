"""
Sistema de Eventos Distribuidos para Arquitectura Modular
Implementa comunicación basada en eventos distribuida y escalable
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set
import aiohttp
import websockets
from websockets.server import serve
import threading
from concurrent.futures import ThreadPoolExecutor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Prioridades de eventos."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class EventStatus(Enum):
    """Estados de eventos."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Event:
    """Representación de un evento distribuido."""
    event_id: str
    event_type: str
    source_node: str
    target_nodes: List[str]
    payload: Dict[str, Any]
    timestamp: float
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    ttl: Optional[float] = None  # Time to live en segundos
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EventResult:
    """Resultado del procesamiento de un evento."""
    event_id: str
    success: bool
    result: Optional[Any] = None
    error_message: Optional[str] = None
    processing_time: float
    node_id: str
    timestamp: float

class EventHandler(ABC):
    """Manejador abstracto de eventos."""
    
    @abstractmethod
    async def handle_event(self, event: Event) -> EventResult:
        """Manejar un evento específico."""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Verificar si puede manejar un tipo de evento."""
        pass

class EventProcessor:
    """Procesador de eventos con prioridades."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.event_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.processing = False
        self.stats = {
            'events_processed': 0,
            'events_failed': 0,
            'total_processing_time': 0.0
        }
    
    def register_handler(self, event_type: str, handler: EventHandler):
        """Registrar un manejador de eventos."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(f"✅ Manejador registrado para evento: {event_type}")
    
    def unregister_handler(self, event_type: str, handler: EventHandler):
        """Desregistrar un manejador de eventos."""
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            logger.info(f"❌ Manejador desregistrado para evento: {event_type}")
    
    async def submit_event(self, event: Event):
        """Enviar evento para procesamiento."""
        # Calcular prioridad (mayor número = mayor prioridad)
        priority = (event.priority.value, time.time())
        await self.event_queue.put((priority, event))
        logger.debug(f"Evento enviado para procesamiento: {event.event_id}")
    
    async def start_processing(self):
        """Iniciar procesamiento de eventos."""
        if self.processing:
            return
        
        self.processing = True
        logger.info("🚀 Procesador de eventos iniciado")
        
        while self.processing:
            try:
                # Obtener evento de la cola
                priority, event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Procesar evento
                await self._process_event(event)
                
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error en procesamiento de eventos: {e}")
    
    async def stop_processing(self):
        """Detener procesamiento de eventos."""
        self.processing = False
        logger.info("🛑 Procesador de eventos detenido")
    
    async def _process_event(self, event: Event):
        """Procesar un evento específico."""
        start_time = time.time()
        
        try:
            # Verificar TTL
            if event.ttl and (time.time() - event.timestamp) > event.ttl:
                logger.warning(f"Evento {event.event_id} expiró")
                return
            
            # Buscar manejadores
            handlers = self.handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"No hay manejadores para evento: {event.event_type}")
                return
            
            # Ejecutar manejadores
            results = []
            for handler in handlers:
                if handler.can_handle(event.event_type):
                    try:
                        result = await handler.handle_event(event)
                        results.append(result)
                        
                        if result.success:
                            self.stats['events_processed'] += 1
                        else:
                            self.stats['events_failed'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error en manejador {handler.__class__.__name__}: {e}")
                        self.stats['events_failed'] += 1
            
            # Actualizar estadísticas
            processing_time = time.time() - start_time
            self.stats['total_processing_time'] += processing_time
            
            logger.debug(f"Evento {event.event_id} procesado en {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Error procesando evento {event.event_id}: {e}")
            self.stats['events_failed'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del procesador."""
        avg_time = 0.0
        if self.stats['events_processed'] > 0:
            avg_time = self.stats['total_processing_time'] / self.stats['events_processed']
        
        return {
            'node_id': self.node_id,
            'events_processed': self.stats['events_processed'],
            'events_failed': self.stats['events_failed'],
            'average_processing_time': avg_time,
            'queue_size': self.event_queue.qsize()
        }

class EventBus:
    """Bus de eventos para comunicación entre nodos."""
    
    def __init__(self, node_id: str, host: str = "localhost", port: int = 8080):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.websocket_server = None
        self.connected_nodes: Set[str] = set()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        
        # Configurar servidor WebSocket
        self._setup_websocket_server()
    
    def _setup_websocket_server(self):
        """Configurar servidor WebSocket."""
        async def websocket_handler(websocket, path):
            try:
                # Registrar conexión
                node_id = await websocket.recv()
                if node_id:
                    self.connected_nodes.add(node_id)
                    logger.info(f"✅ Nodo conectado: {node_id}")
                
                # Manejar mensajes
                async for message in websocket:
                    await self._handle_websocket_message(message, websocket)
                    
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                if node_id:
                    self.connected_nodes.discard(node_id)
                    logger.info(f"❌ Nodo desconectado: {node_id}")
        
        self.websocket_handler = websocket_handler
    
    async def start(self):
        """Iniciar bus de eventos."""
        if self.running:
            return
        
        try:
            self.websocket_server = await serve(
                self.websocket_handler,
                self.host,
                self.port
            )
            
            self.running = True
            logger.info(f"🚀 Bus de eventos iniciado en {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Error iniciando bus de eventos: {e}")
    
    async def stop(self):
        """Detener bus de eventos."""
        if not self.running:
            return
        
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        self.running = False
        logger.info("🛑 Bus de eventos detenido")
    
    async def _handle_websocket_message(self, message: str, websocket):
        """Manejar mensaje WebSocket."""
        try:
            data = json.loads(message)
            
            if data.get('type') == 'event':
                event_data = data.get('event', {})
                event = Event(**event_data)
                await self._distribute_event(event)
            
        except Exception as e:
            logger.error(f"Error manejando mensaje WebSocket: {e}")
    
    async def _distribute_event(self, event: Event):
        """Distribuir evento a todos los nodos conectados."""
        # Notificar manejadores locales
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error en manejador de eventos: {e}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Suscribirse a un tipo de evento."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"✅ Suscripción agregada para evento: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Desuscribirse de un tipo de evento."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.info(f"❌ Suscripción removida para evento: {event_type}")
    
    async def publish_event(self, event: Event):
        """Publicar evento en el bus."""
        if not self.running:
            logger.warning("Bus de eventos no está ejecutándose")
            return
        
        # Enviar a todos los nodos conectados
        message = {
            'type': 'event',
            'event': {
                'event_id': event.event_id,
                'event_type': event.event_type,
                'source_node': event.source_node,
                'target_nodes': event.target_nodes,
                'payload': event.payload,
                'timestamp': event.timestamp,
                'priority': event.priority.value,
                'correlation_id': event.correlation_id,
                'parent_event_id': event.parent_event_id,
                'retry_count': event.retry_count,
                'max_retries': event.max_retries,
                'ttl': event.ttl,
                'metadata': event.metadata
            }
        }
        
        # Aquí se implementaría el envío real a los nodos conectados
        # Por ahora solo notificamos localmente
        await self._distribute_event(event)
        
        logger.debug(f"Evento publicado: {event.event_id}")

class DistributedEventNode:
    """Nodo en el sistema de eventos distribuidos."""
    
    def __init__(self, node_id: str, host: str = "localhost", port: int = 8080):
        self.node_id = node_id
        self.event_processor = EventProcessor(node_id)
        self.event_bus = EventBus(node_id, host, port)
        self.running = False
        
        # Configurar suscripciones por defecto
        self._setup_default_subscriptions()
    
    def _setup_default_subscriptions(self):
        """Configurar suscripciones por defecto."""
        # Suscribirse a eventos de sistema
        self.event_bus.subscribe("system.health_check", self._handle_health_check)
        self.event_bus.subscribe("system.status_request", self._handle_status_request)
    
    async def start(self):
        """Iniciar nodo."""
        if self.running:
            return
        
        logger.info(f"🚀 Iniciando nodo de eventos: {self.node_id}")
        
        # Iniciar bus de eventos
        await self.event_bus.start()
        
        # Iniciar procesador de eventos
        await self.event_processor.start_processing()
        
        self.running = True
        logger.info(f"✅ Nodo {self.node_id} iniciado")
    
    async def stop(self):
        """Detener nodo."""
        if not self.running:
            return
        
        logger.info(f"🛑 Deteniendo nodo: {self.node_id}")
        
        # Detener procesador
        await self.event_processor.stop_processing()
        
        # Detener bus de eventos
        await self.event_bus.stop()
        
        self.running = False
        logger.info(f"✅ Nodo {self.node_id} detenido")
    
    def register_event_handler(self, event_type: str, handler: EventHandler):
        """Registrar manejador de eventos."""
        self.event_processor.register_handler(event_type, handler)
    
    def unregister_event_handler(self, event_type: str, handler: EventHandler):
        """Desregistrar manejador de eventos."""
        self.event_processor.unregister_handler(event_type, handler)
    
    async def publish_event(self, event: Event):
        """Publicar evento desde este nodo."""
        await self.event_bus.publish_event(event)
    
    async def submit_event(self, event: Event):
        """Enviar evento para procesamiento local."""
        await self.event_processor.submit_event(event)
    
    def get_node_status(self) -> Dict[str, Any]:
        """Obtener estado del nodo."""
        return {
            'node_id': self.node_id,
            'running': self.running,
            'connected_nodes': list(self.event_bus.connected_nodes),
            'processor_stats': self.event_processor.get_stats()
        }
    
    async def _handle_health_check(self, event: Event):
        """Manejar solicitud de health check."""
        health_status = {
            'node_id': self.node_id,
            'status': 'healthy' if self.running else 'unhealthy',
            'timestamp': time.time(),
            'stats': self.event_processor.get_stats()
        }
        
        # Enviar respuesta
        response_event = Event(
            event_id=str(uuid.uuid4()),
            event_type="system.health_response",
            source_node=self.node_id,
            target_nodes=[event.source_node],
            payload=health_status,
            timestamp=time.time(),
            correlation_id=event.event_id
        )
        
        await self.publish_event(response_event)
    
    async def _handle_status_request(self, event: Event):
        """Manejar solicitud de estado."""
        status = self.get_node_status()
        
        # Enviar respuesta
        response_event = Event(
            event_id=str(uuid.uuid4()),
            event_type="system.status_response",
            source_node=self.node_id,
            target_nodes=[event.source_node],
            payload=status,
            timestamp=time.time(),
            correlation_id=event.event_id
        )
        
        await self.publish_event(response_event)

class EventOrchestrator:
    """Orquestador del sistema de eventos distribuidos."""
    
    def __init__(self):
        self.nodes: Dict[str, DistributedEventNode] = {}
        self.running = False
    
    async def add_node(self, node_id: str, host: str = "localhost", port: int = 8080) -> DistributedEventNode:
        """Agregar nodo al sistema."""
        if node_id in self.nodes:
            logger.warning(f"Nodo {node_id} ya existe")
            return self.nodes[node_id]
        
        # Crear nodo
        node = DistributedEventNode(node_id, host, port)
        self.nodes[node_id] = node
        
        # Iniciar nodo si el orquestador está ejecutándose
        if self.running:
            await node.start()
        
        logger.info(f"✅ Nodo {node_id} agregado al sistema")
        return node
    
    async def remove_node(self, node_id: str):
        """Remover nodo del sistema."""
        if node_id not in self.nodes:
            logger.warning(f"Nodo {node_id} no encontrado")
            return
        
        node = self.nodes[node_id]
        
        # Detener nodo
        if node.running:
            await node.stop()
        
        # Remover del sistema
        del self.nodes[node_id]
        
        logger.info(f"❌ Nodo {node_id} removido del sistema")
    
    async def start(self):
        """Iniciar orquestador."""
        if self.running:
            return
        
        logger.info("🚀 Iniciando orquestador de eventos distribuidos...")
        
        # Iniciar todos los nodos
        for node in self.nodes.values():
            await node.start()
        
        self.running = True
        logger.info("✅ Orquestador iniciado")
    
    async def stop(self):
        """Detener orquestador."""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo orquestador...")
        
        # Detener todos los nodos
        for node in self.nodes.values():
            if node.running:
                await node.stop()
        
        self.running = False
        logger.info("✅ Orquestador detenido")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema."""
        return {
            'orchestrator_running': self.running,
            'nodes': {
                node_id: node.get_node_status()
                for node_id, node in self.nodes.items()
            }
        }
    
    async def publish_event_to_all(self, event: Event):
        """Publicar evento a todos los nodos."""
        for node in self.nodes.values():
            if node.running:
                await node.publish_event(event)

async def run_distributed_event_demo():
    """Ejecutar demostración del sistema de eventos distribuidos."""
    logger.info("🎯 Iniciando demostración del sistema de eventos distribuidos...")
    
    # Crear orquestador
    orchestrator = EventOrchestrator()
    
    try:
        # Agregar nodos
        node1 = await orchestrator.add_node("node_1", "localhost", 8081)
        node2 = await orchestrator.add_node("node_2", "localhost", 8082)
        
        # Iniciar orquestador
        await orchestrator.start()
        
        # Simular operaciones
        await asyncio.sleep(2)
        
        # Obtener estado del sistema
        status = orchestrator.get_system_status()
        logger.info(f"Estado del sistema: {json.dumps(status, indent=2)}")
        
        # Publicar evento de prueba
        test_event = Event(
            event_id=str(uuid.uuid4()),
            event_type="test.event",
            source_node="orchestrator",
            target_nodes=["node_1", "node_2"],
            payload={"message": "Hello from orchestrator!"},
            timestamp=time.time(),
            priority=EventPriority.HIGH
        )
        
        await orchestrator.publish_event_to_all(test_event)
        
        # Mantener sistema ejecutándose
        await asyncio.sleep(10)
        
    finally:
        # Detener orquestador
        await orchestrator.stop()
    
    logger.info("✅ Demostración del sistema de eventos distribuidos completada")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(run_distributed_event_demo())
