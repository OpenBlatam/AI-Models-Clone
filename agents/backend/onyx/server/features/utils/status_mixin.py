"""
Status Mixin - Onyx Integration
Status handling functionality for models.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .base_types import StatusType, StatusCategory

@dataclass
class Status:
    """Status data class."""
    type: StatusType
    category: StatusCategory
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class StatusMixin:
    """Mixin for status handling functionality."""
    
    _status_history: List[Status] = []
    _max_history_size: int = 1000
    
    def set_status(self, status_type: StatusType, category: StatusCategory, metadata: Optional[Dict[str, Any]] = None) -> Status:
        """Set a status."""
        status = Status(
            type=status_type,
            category=category,
            metadata=metadata or {}
        )
        
        self._status_history.append(status)
        if len(self._status_history) > self._max_history_size:
            self._status_history.pop(0)
        
        return status
    
    def get_current_status(self) -> Optional[Status]:
        """Get current status."""
        if not self._status_history:
            return None
        return self._status_history[-1]
    
    def get_status_history(self, status_type: Optional[StatusType] = None, category: Optional[StatusCategory] = None, limit: Optional[int] = None) -> List[Status]:
        """Get status history."""
        history = self._status_history
        
        if status_type:
            history = [s for s in history if s.type == status_type]
        
        if category:
            history = [s for s in history if s.category == category]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def clear_status_history(self) -> None:
        """Clear status history."""
        self._status_history.clear()
    
    def update_status_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update current status metadata."""
        if self._status_history:
            self._status_history[-1].metadata.update(metadata)
    
    def get_status_by_category(self, category: StatusCategory) -> Optional[Status]:
        """Get most recent status by category."""
        for status in reversed(self._status_history):
            if status.category == category:
                return status
        return None
    
    def get_status_by_type(self, status_type: StatusType) -> Optional[Status]:
        """Get most recent status by type."""
        for status in reversed(self._status_history):
            if status.type == status_type:
                return status
        return None 