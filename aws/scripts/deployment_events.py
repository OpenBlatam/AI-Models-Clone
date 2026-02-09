#!/usr/bin/env python3
"""
Deployment Event Stream
Event streaming for deployment events
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path


logger = logging.getLogger(__name__)


class EventType(Enum):
    """Deployment event types"""
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    DEPLOYMENT_FAILED = "deployment_failed"
    DEPLOYMENT_ROLLED_BACK = "deployment_rolled_back"
    HEALTH_CHECK_PASSED = "health_check_passed"
    HEALTH_CHECK_FAILED = "health_check_failed"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    SCALING_TRIGGERED = "scaling_triggered"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"


@dataclass
class DeploymentEvent:
    """Deployment event"""
    event_type: EventType
    deployment_id: str
    timestamp: str
    data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class EventStream:
    """Manages deployment event streaming"""
    
    def __init__(self, events_file: str = '/var/lib/deployment-events/events.json'):
        self.events_file = Path(events_file)
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        self.subscribers: List[Callable[[DeploymentEvent], None]] = []
        self.events: List[DeploymentEvent] = []
    
    def subscribe(self, callback: Callable[[DeploymentEvent], None]):
        """Subscribe to events"""
        self.subscribers.append(callback)
        logger.info(f"New event subscriber registered: {callback.__name__}")
    
    def publish(self, event: DeploymentEvent):
        """Publish an event"""
        logger.debug(f"Publishing event: {event.event_type.value} for deployment {event.deployment_id}")
        
        # Store event
        self.events.append(event)
        
        # Keep only last 1000 events in memory
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
        
        # Save to file
        self._save_events()
        
        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(f"Event subscriber error: {e}")
    
    def _save_events(self):
        """Save events to file"""
        try:
            # Keep only last 1000 events in file
            recent_events = self.events[-1000:]
            
            data = {
                'events': [asdict(event) for event in recent_events],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.events_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save events: {e}")
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        deployment_id: Optional[str] = None,
        limit: int = 100
    ) -> List[DeploymentEvent]:
        """Get events with optional filtering"""
        events = self.events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if deployment_id:
            events = [e for e in events if e.deployment_id == deployment_id]
        
        return events[-limit:]
    
    def get_event_stream(self, deployment_id: str) -> List[DeploymentEvent]:
        """Get all events for a specific deployment"""
        return [e for e in self.events if e.deployment_id == deployment_id]
