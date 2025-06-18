"""
Event Mixin - Onyx Integration
Event handling functionality for models.
"""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from .base_types import EventType, EventStatus

@dataclass
class Event:
    """Event data class."""
    type: EventType
    status: EventStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class EventMixin:
    """Mixin for event handling functionality."""
    
    _event_handlers: Dict[EventType, Set[Callable]] = {}
    _event_history: List[Event] = []
    _max_history_size: int = 1000
    
    def register_event_handler(self, event_type: EventType, handler: Callable) -> None:
        """Register an event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = set()
        self._event_handlers[event_type].add(handler)
    
    def unregister_event_handler(self, event_type: EventType, handler: Callable) -> None:
        """Unregister an event handler."""
        if event_type in self._event_handlers:
            self._event_handlers[event_type].discard(handler)
    
    def emit_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None) -> Event:
        """Emit an event."""
        event = Event(
            type=event_type,
            status=EventStatus.PENDING,
            data=data or {},
            metadata=metadata or {}
        )
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Notify handlers
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    event.status = EventStatus.FAILED
                    event.metadata['error'] = str(e)
                    continue
        
        event.status = EventStatus.COMPLETED
        return event
    
    def get_event_history(self, event_type: Optional[EventType] = None, limit: Optional[int] = None) -> List[Event]:
        """Get event history."""
        history = self._event_history
        if event_type:
            history = [e for e in history if e.type == event_type]
        if limit:
            history = history[-limit:]
        return history
    
    def clear_event_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def get_event_handlers(self, event_type: Optional[EventType] = None) -> Dict[EventType, Set[Callable]]:
        """Get event handlers."""
        if event_type:
            return {event_type: self._event_handlers.get(event_type, set())}
        return self._event_handlers.copy() 