#!/usr/bin/env python3
"""
Event-Driven Architecture - Infrastructure Layer
==============================================

Advanced event bus system with event sourcing, event handlers,
and enterprise-grade event processing capabilities.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union
from contextlib import asynccontextmanager
import weakref

T = TypeVar('T')


class EventType(Enum):
    """Event types for categorization."""
    DOMAIN = "domain"
    INTEGRATION = "integration"
    SYSTEM = "system"
    AUDIT = "audit"
    PERFORMANCE = "performance"
    SECURITY = "security"


class EventPriority(Enum):
    """Event priorities for processing order."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class DomainEvent:
    """Base class for all domain events."""
    
    # Event identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = field(default="domain")
    event_name: str = field(default="")
    
    # Event metadata
    aggregate_id: Optional[str] = None
    aggregate_version: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    # Event data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    processed: bool = False
    processing_time_ms: float = 0.0
    
    def __post_init__(self):
        """Initialize event after creation."""
        if not self.event_name:
            self.event_name = self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'event_name': self.event_name,
            'aggregate_id': self.aggregate_id,
            'aggregate_version': self.aggregate_version,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'data': self.data,
            'metadata': self.metadata,
            'priority': self.priority.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'processed': self.processed,
            'processing_time_ms': self.processing_time_ms
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create event from dictionary."""
        event = cls()
        event.event_id = data.get('event_id', str(uuid.uuid4()))
        event.event_type = data.get('event_type', 'domain')
        event.event_name = data.get('event_name', '')
        event.aggregate_id = data.get('aggregate_id')
        event.aggregate_version = data.get('aggregate_version', 1)
        event.timestamp = datetime.fromisoformat(data['timestamp']) if isinstance(data.get('timestamp'), str) else data.get('timestamp', datetime.utcnow())
        event.correlation_id = data.get('correlation_id')
        event.causation_id = data.get('causation_id')
        event.data = data.get('data', {})
        event.metadata = data.get('metadata', {})
        event.priority = EventPriority(data.get('priority', 2))
        event.retry_count = data.get('retry_count', 0)
        event.max_retries = data.get('max_retries', 3)
        event.processed = data.get('processed', False)
        event.processing_time_ms = data.get('processing_time_ms', 0.0)
        return event


class EventHandler(ABC):
    """Base class for event handlers."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle an event."""
        pass
    
    @property
    @abstractmethod
    def event_types(self) -> List[str]:
        """Get the event types this handler can process."""
        pass
    
    @property
    def priority(self) -> int:
        """Get handler priority (lower = higher priority)."""
        return 100
    
    @property
    def async_processing(self) -> bool:
        """Whether this handler should be processed asynchronously."""
        return True


class EventBus:
    """
    Advanced event bus with enterprise-grade features.
    
    Features:
    - Event publishing and subscription
    - Event sourcing and persistence
    - Event replay capabilities
    - Event correlation and causation
    - Retry mechanisms with exponential backoff
    - Event filtering and routing
    - Performance monitoring
    - Dead letter queue
    """
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._event_store: List[DomainEvent] = []
        self._dead_letter_queue: List[DomainEvent] = []
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._processing_tasks: Set[asyncio.Task] = set()
        self._logger = logging.getLogger(__name__)
        self._metrics = {
            'events_published': 0,
            'events_processed': 0,
            'events_failed': 0,
            'events_retried': 0,
            'processing_time_avg': 0.0,
            'queue_size': 0
        }
        self._running = False
        self._max_workers = 10
        self._retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
    
    async def start(self) -> None:
        """Start the event bus."""
        if self._running:
            return
        
        self._running = True
        self._logger.info("Starting event bus...")
        
        # Start processing workers
        for _ in range(self._max_workers):
            task = asyncio.create_task(self._process_events())
            self._processing_tasks.add(task)
        
        self._logger.info(f"Event bus started with {self._max_workers} workers")
    
    async def stop(self) -> None:
        """Stop the event bus."""
        if not self._running:
            return
        
        self._running = False
        self._logger.info("Stopping event bus...")
        
        # Cancel all processing tasks
        for task in self._processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._processing_tasks:
            await asyncio.gather(*self._processing_tasks, return_exceptions=True)
        
        self._processing_tasks.clear()
        self._logger.info("Event bus stopped")
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The event type to subscribe to
            handler: The event handler
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        # Insert handler in priority order
        handlers = self._handlers[event_type]
        handlers.append(handler)
        handlers.sort(key=lambda h: h.priority)
        
        self._logger.info(f"Subscribed handler {handler.__class__.__name__} to event type {event_type}")
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: The event type to unsubscribe from
            handler: The event handler to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
            
            if not self._handlers[event_type]:
                del self._handlers[event_type]
            
            self._logger.info(f"Unsubscribed handler {handler.__class__.__name__} from event type {event_type}")
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to the event bus.
        
        Args:
            event: The event to publish
        """
        # Store event
        self._event_store.append(event)
        
        # Add to processing queue
        await self._processing_queue.put(event)
        
        # Update metrics
        self._metrics['events_published'] += 1
        self._metrics['queue_size'] = self._processing_queue.qsize()
        
        self._logger.debug(f"Published event: {event.event_name} (ID: {event.event_id})")
    
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple events in batch.
        
        Args:
            events: List of events to publish
        """
        for event in events:
            await self.publish(event)
        
        self._logger.info(f"Published batch of {len(events)} events")
    
    async def replay_events(self, event_types: Optional[List[str]] = None, 
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> None:
        """
        Replay events from the event store.
        
        Args:
            event_types: Filter by event types
            start_time: Start time for replay
            end_time: End time for replay
        """
        self._logger.info("Starting event replay...")
        
        filtered_events = []
        for event in self._event_store:
            # Apply filters
            if event_types and event.event_type not in event_types:
                continue
            
            if start_time and event.timestamp < start_time:
                continue
            
            if end_time and event.timestamp > end_time:
                continue
            
            filtered_events.append(event)
        
        # Replay events in chronological order
        sorted_events = sorted(filtered_events, key=lambda e: e.timestamp)
        
        for event in sorted_events:
            await self._process_event(event)
        
        self._logger.info(f"Replayed {len(sorted_events)} events")
    
    def get_events(self, event_types: Optional[List[str]] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  limit: Optional[int] = None) -> List[DomainEvent]:
        """
        Get events from the event store with filtering.
        
        Args:
            event_types: Filter by event types
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of events to return
        
        Returns:
            List of filtered events
        """
        filtered_events = []
        
        for event in self._event_store:
            # Apply filters
            if event_types and event.event_type not in event_types:
                continue
            
            if start_time and event.timestamp < start_time:
                continue
            
            if end_time and event.timestamp > end_time:
                continue
            
            filtered_events.append(event)
        
        # Sort by timestamp (newest first)
        sorted_events = sorted(filtered_events, key=lambda e: e.timestamp, reverse=True)
        
        if limit:
            sorted_events = sorted_events[:limit]
        
        return sorted_events
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus performance metrics."""
        return {
            'events_published': self._metrics['events_published'],
            'events_processed': self._metrics['events_processed'],
            'events_failed': self._metrics['events_failed'],
            'events_retried': self._metrics['events_retried'],
            'processing_time_avg': self._metrics['processing_time_avg'],
            'queue_size': self._processing_queue.qsize(),
            'total_events_stored': len(self._event_store),
            'dead_letter_queue_size': len(self._dead_letter_queue),
            'active_handlers': sum(len(handlers) for handlers in self._handlers.values()),
            'running': self._running
        }
    
    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self._processing_queue.get(), timeout=1.0)
                
                # Process the event
                await self._process_event(event)
                
                # Mark task as done
                self._processing_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._logger.error(f"Error in event processing worker: {e}")
    
    async def _process_event(self, event: DomainEvent) -> None:
        """Process a single event."""
        start_time = time.time()
        
        try:
            # Get handlers for this event type
            handlers = self._handlers.get(event.event_type, [])
            
            if not handlers:
                self._logger.warning(f"No handlers found for event type: {event.event_type}")
                return
            
            # Process with all handlers
            for handler in handlers:
                try:
                    if handler.async_processing:
                        await handler.handle(event)
                    else:
                        # Run in thread pool for sync handlers
                        await asyncio.get_event_loop().run_in_executor(
                            None, lambda: asyncio.run(handler.handle(event))
                        )
                    
                    self._logger.debug(f"Processed event {event.event_id} with handler {handler.__class__.__name__}")
                    
                except Exception as e:
                    self._logger.error(f"Handler {handler.__class__.__name__} failed for event {event.event_id}: {e}")
                    
                    # Retry logic
                    if event.retry_count < event.max_retries:
                        event.retry_count += 1
                        self._metrics['events_retried'] += 1
                        
                        # Calculate delay with exponential backoff
                        delay = self._retry_delays[min(event.retry_count - 1, len(self._retry_delays) - 1)]
                        
                        self._logger.info(f"Retrying event {event.event_id} in {delay}s (attempt {event.retry_count})")
                        
                        # Schedule retry
                        asyncio.create_task(self._retry_event(event, delay))
                    else:
                        # Move to dead letter queue
                        self._dead_letter_queue.append(event)
                        self._metrics['events_failed'] += 1
                        self._logger.error(f"Event {event.event_id} moved to dead letter queue after {event.max_retries} retries")
            
            # Mark as processed
            event.processed = True
            event.processing_time_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            self._metrics['events_processed'] += 1
            self._metrics['processing_time_avg'] = (
                (self._metrics['processing_time_avg'] * (self._metrics['events_processed'] - 1) + event.processing_time_ms) /
                self._metrics['events_processed']
            )
            
        except Exception as e:
            self._logger.error(f"Failed to process event {event.event_id}: {e}")
            self._metrics['events_failed'] += 1
    
    async def _retry_event(self, event: DomainEvent, delay: float) -> None:
        """Retry an event after a delay."""
        await asyncio.sleep(delay)
        await self.publish(event)


# Specific event types for the LinkedIn post system
@dataclass
class PostCreatedEvent(DomainEvent):
    """Event raised when a LinkedIn post is created."""
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "post.created"
        self.event_name = "PostCreated"


@dataclass
class PostOptimizedEvent(DomainEvent):
    """Event raised when a LinkedIn post is optimized."""
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "post.optimized"
        self.event_name = "PostOptimized"


@dataclass
class PostPublishedEvent(DomainEvent):
    """Event raised when a LinkedIn post is published."""
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "post.published"
        self.event_name = "PostPublished"


@dataclass
class OptimizationStrategyChangedEvent(DomainEvent):
    """Event raised when optimization strategy changes."""
    
    def __post_init__(self):
        super().__post_init__()
        self.event_type = "optimization.strategy_changed"
        self.event_name = "OptimizationStrategyChanged"


# Global event bus instance
event_bus = EventBus()


# Decorators for easy event handling
def event_handler(event_types: List[str], priority: int = 100):
    """Decorator to register an event handler."""
    def decorator(cls):
        class EventHandlerWrapper(EventHandler):
            def __init__(self):
                self._handler = cls()
            
            async def handle(self, event: DomainEvent) -> None:
                await self._handler.handle(event)
            
            @property
            def event_types(self) -> List[str]:
                return event_types
            
            @property
            def priority(self) -> int:
                return priority
        
        # Register with event bus
        handler = EventHandlerWrapper()
        for event_type in event_types:
            event_bus.subscribe(event_type, handler)
        
        return cls
    return decorator


def publish_event(event: DomainEvent):
    """Decorator to publish an event after method execution."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await event_bus.publish(event)
            return result
        return wrapper
    return decorator 