"""
Permission Mixin - Onyx Integration
Permission handling functionality for models.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from .base_types import PermissionType, PermissionStatus

@dataclass
class Permission:
    """Permission data class."""
    type: PermissionType
    status: PermissionStatus = PermissionStatus.ACTIVE
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class PermissionMixin:
    """Mixin for permission handling functionality."""
    
    _permissions: Dict[str, Dict[PermissionType, Permission]] = {}
    
    def grant_permission(self, entity_id: str, permission_type: PermissionType, expires_at: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None) -> Permission:
        """Grant a permission."""
        if entity_id not in self._permissions:
            self._permissions[entity_id] = {}
        
        permission = Permission(
            type=permission_type,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._permissions[entity_id][permission_type] = permission
        return permission
    
    def revoke_permission(self, entity_id: str, permission_type: PermissionType) -> None:
        """Revoke a permission."""
        if entity_id in self._permissions and permission_type in self._permissions[entity_id]:
            del self._permissions[entity_id][permission_type]
            if not self._permissions[entity_id]:
                del self._permissions[entity_id]
    
    def has_permission(self, entity_id: str, permission_type: PermissionType) -> bool:
        """Check if an entity has a permission."""
        if entity_id not in self._permissions:
            return False
        
        permission = self._permissions[entity_id].get(permission_type)
        if not permission:
            return False
        
        if permission.status != PermissionStatus.ACTIVE:
            return False
        
        if permission.expires_at and permission.expires_at < datetime.utcnow():
            return False
        
        return True
    
    def get_permissions(self, entity_id: str) -> Dict[PermissionType, Permission]:
        """Get all permissions for an entity."""
        return self._permissions.get(entity_id, {}).copy()
    
    def get_all_permissions(self) -> Dict[str, Dict[PermissionType, Permission]]:
        """Get all permissions."""
        return {entity_id: permissions.copy() for entity_id, permissions in self._permissions.items()}
    
    def clear_permissions(self, entity_id: str) -> None:
        """Clear all permissions for an entity."""
        if entity_id in self._permissions:
            del self._permissions[entity_id]
    
    def clear_all_permissions(self) -> None:
        """Clear all permissions."""
        self._permissions.clear()
    
    def update_permission_status(self, entity_id: str, permission_type: PermissionType, status: PermissionStatus) -> None:
        """Update permission status."""
        if entity_id in self._permissions and permission_type in self._permissions[entity_id]:
            self._permissions[entity_id][permission_type].status = status
    
    def update_permission_metadata(self, entity_id: str, permission_type: PermissionType, metadata: Dict[str, Any]) -> None:
        """Update permission metadata."""
        if entity_id in self._permissions and permission_type in self._permissions[entity_id]:
            self._permissions[entity_id][permission_type].metadata.update(metadata) 