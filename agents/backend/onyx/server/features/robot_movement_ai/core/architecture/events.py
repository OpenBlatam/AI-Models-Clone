"""
Event-Driven Architecture
==========================

Sistema de eventos para comunicación desacoplada.
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos."""
    TRAINING_STARTED = "training_started"
    TRAINING_COMPLETED = "training_completed"
    TRAINING_ERROR = "training_error"
    INFERENCE_STARTED = "inference_started"
    INFERENCE_COMPLETED = "inference_completed"
    INFERENCE_ERROR = "inference_error"
    ROUTE_REQUESTED = "route_requested"
    ROUTE_FOUND = "route_found"
    ROUTE_ERROR = "route_error"


@dataclass
class Event:
    """Evento base."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        """Inicializar timestamp si no está presente."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TrainingEvent(Event):
    """Evento de entrenamiento."""
    pass


@dataclass
class InferenceEvent(Event):
    """Evento de inferencia."""
    pass


class EventHandler:
    """Manejador de eventos."""
    
    def __init__(self, callback: Callable[[Event], None]):
        """
        Inicializar handler.
        
        Args:
            callback: Función callback
        """
        self.callback = callback
    
    def handle(self, event: Event):
        """
        Manejar evento.
        
        Args:
            event: Evento
        """
        try:
            self.callback(event)
        except Exception as e:
            logger.error(f"Error en handler de evento: {e}")


class EventBus:
    """
    Bus de eventos para comunicación desacoplada.
    """
    
    def __init__(self):
        """Inicializar bus."""
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._event_history: List[Event] = []
        self._max_history: int = 1000
    
    def subscribe(self, event_type: str, handler: EventHandler):
        """
        Suscribirse a un tipo de evento.
        
        Args:
            event_type: Tipo de evento
            handler: Handler
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler suscrito a '{event_type}'")
    
    def subscribe_all(self, handler: EventHandler):
        """
        Suscribirse a todos los eventos.
        
        Args:
            handler: Handler
        """
        self.subscribe("*", handler)
    
    def unsubscribe(self, event_type: str, handler: EventHandler):
        """
        Desuscribirse de un tipo de evento.
        
        Args:
            event_type: Tipo de evento
            handler: Handler
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
    
    def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emitir evento.
        
        Args:
            event_type: Tipo de evento
            data: Datos del evento
        """
        event = Event(type=event_type, data=data)
        
        # Agregar a historial
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Notificar handlers específicos
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            handler.handle(event)
        
        # Notificar handlers de todos los eventos
        all_handlers = self._handlers.get("*", [])
        for handler in all_handlers:
            handler.handle(event)
        
        logger.debug(f"Evento emitido: {event_type}")
    
    def get_history(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Obtener historial de eventos.
        
        Args:
            event_type: Filtrar por tipo (opcional)
            limit: Límite de resultados
            
        Returns:
            Lista de eventos
        """
        events = self._event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events[-limit:]
    
    def clear_history(self):
        """Limpiar historial."""
        self._event_history.clear()
    
    def get_handler_count(self, event_type: Optional[str] = None) -> int:
        """
        Contar handlers.
        
        Args:
            event_type: Tipo de evento (opcional)
            
        Returns:
            Número de handlers
        """
        if event_type:
            return len(self._handlers.get(event_type, []))
        return sum(len(handlers) for handlers in self._handlers.values())

