"""
Event System for Modular SEO System
Provides complete decoupling between components through event publishing and subscription
"""

import asyncio
import inspect
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from typing_extensions import Protocol

# Configure logging
logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """Base event class."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    priority: EventPriority = EventPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            self.name = self.__class__.__name__


@dataclass
class EventContext:
    """Context for event processing."""

    event: Event
    handler: Callable
    start_time: float
    priority: EventPriority
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventHandler(Protocol):
    """Protocol for event handlers."""

    async def handle_event(self, event: Event) -> None:
        """Handle an event."""
        ...


class EventFilter(Protocol):
    """Protocol for event filters."""

    def should_process(self, event: Event) -> bool:
        """Determine if an event should be processed."""
        ...


class EventTransformer(Protocol):
    """Protocol for event transformers."""

    def transform(self, event: Event) -> Event:
        """Transform an event."""
        ...


class EventValidator(Protocol):
    """Protocol for event validators."""

    def validate(self, event: Event) -> bool:
        """Validate an event."""
        ...


class EventBus:
    """Central event bus for the system."""

    def __init__(self):
        self._subscribers: Dict[str, List[EventSubscription]] = {}
        self._global_subscribers: List[EventSubscription] = []
        self._event_history: List[Event] = []
        self._max_history: int = 1000
        self._lock = asyncio.Lock()
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Event processing statistics
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_dropped": 0,
            "handlers_executed": 0,
            "errors": 0,
        }

        # Event filters, transformers, and validators
        self._filters: List[EventFilter] = []
        self._transformers: List[EventTransformer] = []
        self._validators: List[EventValidator] = []

        # Event routing rules
        self._routing_rules: Dict[str, List[str]] = {}

        # Performance monitoring
        self._performance_metrics: Dict[str, List[float]] = {}

    async def start(self):
        """Start the event bus."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._event_worker())
            logger.info("Event bus started")

    async def stop(self):
        """Stop the event bus."""
        self._shutdown_event.set()
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Event bus stopped")

    async def _event_worker(self):
        """Background worker for processing events."""
        while not self._shutdown_event.is_set():
            try:
                # Wait for events with timeout
                try:
                    event_context = await asyncio.wait_for(self._processing_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                # Process the event
                await self._process_event(event_context)

                # Mark task as done
                self._processing_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event worker: {e}")
                self._stats["errors"] += 1

    async def _process_event(self, context: EventContext):
        """Process a single event."""
        start_time = time.time()

        try:
            # Apply filters
            if not self._should_process_event(context.event):
                self._stats["events_dropped"] += 1
                return

            # Apply transformers
            transformed_event = self._transform_event(context.event)

            # Apply validators
            if not self._validate_event(transformed_event):
                self._stats["events_dropped"] += 1
                return

            # Execute handler
            if asyncio.iscoroutinefunction(context.handler):
                await context.handler(transformed_event)
            else:
                context.handler(transformed_event)

            self._stats["handlers_executed"] += 1

            # Update performance metrics
            execution_time = time.time() - start_time
            handler_name = context.handler.__name__
            if handler_name not in self._performance_metrics:
                self._performance_metrics[handler_name] = []
            self._performance_metrics[handler_name].append(execution_time)

            # Keep only last 100 measurements
            if len(self._performance_metrics[handler_name]) > 100:
                self._performance_metrics[handler_name] = self._performance_metrics[handler_name][-100:]

        except Exception as e:
            logger.error(f"Error processing event {context.event.name}: {e}")
            self._stats["errors"] += 1

    def _should_process_event(self, event: Event) -> bool:
        """Check if event should be processed based on filters."""
        for filter_obj in self._filters:
            if not filter_obj.should_process(event):
                return False
        return True

    def _transform_event(self, event: Event) -> Event:
        """Transform event using registered transformers."""
        transformed_event = event
        for transformer in self._transformers:
            transformed_event = transformer.transform(transformed_event)
        return transformed_event

    def _validate_event(self, event: Event) -> bool:
        """Validate event using registered validators."""
        for validator in self._validators:
            if not validator.validate(event):
                return False
        return True

    async def publish(self, event: Event) -> bool:
        """Publish an event to all subscribers."""
        async with self._lock:
            try:
                # Add to history
                self._event_history.append(event)
                if len(self._event_history) > self._max_history:
                    self._event_history.pop(0)

                # Update stats
                self._stats["events_published"] += 1

                # Get subscribers for this event type
                subscribers = self._subscribers.get(event.name, [])
                global_subscribers = self._global_subscribers.copy()

                # Create event contexts
                contexts = []
                for subscription in subscribers + global_subscribers:
                    if subscription.is_active and subscription.should_handle(event):
                        context = EventContext(
                            event=event,
                            handler=subscription.handler,
                            start_time=time.time(),
                            priority=subscription.priority,
                            metadata=subscription.metadata,
                        )
                        contexts.append(context)

                # Sort by priority
                contexts.sort(key=lambda x: x.priority.value, reverse=True)

                # Queue for processing
                for context in contexts:
                    await self._processing_queue.put(context)

                logger.debug(f"Published event {event.name} to {len(contexts)} subscribers")
                return True

            except Exception as e:
                logger.error(f"Failed to publish event {event.name}: {e}")
                return False

    def subscribe(
        self,
        event_name: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        filters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EventSubscription":
        """Subscribe to events of a specific type."""
        subscription = EventSubscription(
            event_name=event_name, handler=handler, priority=priority, filters=filters or {}, metadata=metadata or {}
        )

        if event_name not in self._subscribers:
            self._subscribers[event_name] = []

        self._subscribers[event_name].append(subscription)
        logger.debug(f"Added subscription for event {event_name}")

        return subscription

    def subscribe_global(
        self,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        filters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EventSubscription":
        """Subscribe to all events."""
        subscription = EventSubscription(
            event_name="*", handler=handler, priority=priority, filters=filters or {}, metadata=metadata or {}
        )

        self._global_subscribers.append(subscription)
        logger.debug("Added global subscription")

        return subscription

    def unsubscribe(self, subscription: "EventSubscription") -> bool:
        """Unsubscribe from events."""
        try:
            if subscription.event_name == "*":
                if subscription in self._global_subscribers:
                    self._global_subscribers.remove(subscription)
                    return True
            else:
                if subscription.event_name in self._subscribers:
                    if subscription in self._subscribers[subscription.event_name]:
                        self._subscribers[subscription.event_name].remove(subscription)
                        return True

            return False

        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}")
            return False

    def add_filter(self, filter_obj: EventFilter):
        """Add an event filter."""
        self._filters.append(filter_obj)

    def add_transformer(self, transformer: EventTransformer):
        """Add an event transformer."""
        self._transformers.append(transformer)

    def add_validator(self, validator: EventValidator):
        """Add an event validator."""
        self._validators.append(validator)

    def add_routing_rule(self, source_event: str, target_events: List[str]):
        """Add a routing rule for event transformation."""
        self._routing_rules[source_event] = target_events

    async def wait_for_event(
        self, event_name: str, timeout: Optional[float] = None, condition: Optional[Callable[[Event], bool]] = None
    ) -> Optional[Event]:
        """Wait for a specific event to occur."""
        future = asyncio.Future()

        def handler(event: Event):
            if not future.done():
                if condition is None or condition(event):
                    future.set_result(event)

        subscription = self.subscribe(event_name, handler)

        try:
            if timeout is not None:
                return await asyncio.wait_for(future, timeout=timeout)
            else:
                return await future
        except asyncio.TimeoutError:
            return None
        finally:
            self.unsubscribe(subscription)

    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            **self._stats,
            "queue_size": self._processing_queue.qsize(),
            "subscriber_count": sum(len(subs) for subs in self._subscribers.values()) + len(self._global_subscribers),
            "event_types": list(self._subscribers.keys()),
            "performance_metrics": {
                name: {
                    "count": len(times),
                    "avg_time": sum(times) / len(times) if times else 0,
                    "min_time": min(times) if times else 0,
                    "max_time": max(times) if times else 0,
                }
                for name, times in self._performance_metrics.items()
            },
        }

    def get_event_history(self, limit: Optional[int] = None) -> List[Event]:
        """Get event history."""
        if limit is None:
            return self._event_history.copy()
        return self._event_history[-limit:]


class EventSubscription:
    """Represents a subscription to events."""

    def __init__(
        self,
        event_name: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        filters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.event_name = event_name
        self.handler = handler
        self.priority = priority
        self.filters = filters or {}
        self.metadata = metadata or {}
        self.is_active = True
        self.created_at = time.time()
        self.handled_events = 0
        self.last_handled = None

    def should_handle(self, event: Event) -> bool:
        """Check if this subscription should handle the event."""
        if not self.is_active:
            return False

        # Check filters
        for key, value in self.filters.items():
            if key == "source" and event.source != value:
                return False
            elif key == "priority" and event.priority != value:
                return False
            elif key == "metadata" and not self._check_metadata_filter(event.metadata, value):
                return False

        return True

    def _check_metadata_filter(self, event_metadata: Dict[str, Any], filter_value: Any) -> bool:
        """Check if event metadata matches filter value."""
        if isinstance(filter_value, dict):
            for k, v in filter_value.items():
                if k not in event_metadata or event_metadata[k] != v:
                    return False
            return True
        return True

    def deactivate(self):
        """Deactivate this subscription."""
        self.is_active = False

    def activate(self):
        """Activate this subscription."""
        self.is_active = True

    def update_filters(self, new_filters: Dict[str, Any]):
        """Update subscription filters."""
        self.filters.update(new_filters)

    def __repr__(self):
        return f"EventSubscription(event={self.event_name}, handler={self.handler.__name__}, priority={self.priority})"


# Global event bus instance
event_bus = EventBus()


# Convenience functions
async def publish_event(event: Event) -> bool:
    """Publish an event using the global event bus."""
    return await event_bus.publish(event)


def subscribe_to_event(
    event_name: str,
    handler: Callable,
    priority: EventPriority = EventPriority.NORMAL,
    filters: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> EventSubscription:
    """Subscribe to events using the global event bus."""
    return event_bus.subscribe(event_name, handler, priority, filters, metadata)


def subscribe_to_all_events(
    handler: Callable,
    priority: EventPriority = EventPriority.NORMAL,
    filters: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> EventSubscription:
    """Subscribe to all events using the global event bus."""
    return event_bus.subscribe_global(handler, priority, filters, metadata)


async def wait_for_event(
    event_name: str, timeout: Optional[float] = None, condition: Optional[Callable[[Event], bool]] = None
) -> Optional[Event]:
    """Wait for an event using the global event bus."""
    return await event_bus.wait_for_event(event_name, timeout, condition)
