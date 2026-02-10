"""
Data Synchronization System
===========================

Sistema de sincronización de datos.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Estado de sincronización."""
    IDLE = "idle"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class SyncDirection(Enum):
    """Dirección de sincronización."""
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"


@dataclass
class SyncEndpoint:
    """Endpoint de sincronización."""
    endpoint_id: str
    name: str
    endpoint: str
    credentials: Dict[str, str] = field(default_factory=dict)
    last_sync: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncRule:
    """Regla de sincronización."""
    rule_id: str
    name: str
    source_endpoint: str
    target_endpoint: str
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    sync_interval: float = 60.0  # segundos
    conflict_resolution: str = "source_wins"  # source_wins, target_wins, manual
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncResult:
    """Resultado de sincronización."""
    sync_id: str
    rule_id: str
    status: SyncStatus
    items_synced: int = 0
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None


class DataSynchronizationManager:
    """
    Gestor de sincronización de datos.
    
    Gestiona sincronización bidireccional entre endpoints.
    """
    
    def __init__(self):
        """Inicializar gestor de sincronización."""
        self.endpoints: Dict[str, SyncEndpoint] = {}
        self.rules: Dict[str, SyncRule] = {}
        self.sync_results: List[SyncResult] = []
        self.max_results = 10000
        self.sync_tasks: Dict[str, Any] = {}  # rule_id -> task
    
    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        credentials: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registrar endpoint de sincronización.
        
        Args:
            name: Nombre del endpoint
            endpoint: URL del endpoint
            credentials: Credenciales
            metadata: Metadata adicional
            
        Returns:
            ID del endpoint
        """
        endpoint_id = str(uuid.uuid4())
        
        sync_endpoint = SyncEndpoint(
            endpoint_id=endpoint_id,
            name=name,
            endpoint=endpoint,
            credentials=credentials or {},
            metadata=metadata or {}
        )
        
        self.endpoints[endpoint_id] = sync_endpoint
        logger.info(f"Registered sync endpoint: {name} ({endpoint_id})")
        
        return endpoint_id
    
    def create_sync_rule(
        self,
        name: str,
        source_endpoint: str,
        target_endpoint: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        sync_interval: float = 60.0,
        conflict_resolution: str = "source_wins",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crear regla de sincronización.
        
        Args:
            name: Nombre de la regla
            source_endpoint: ID del endpoint fuente
            target_endpoint: ID del endpoint objetivo
            direction: Dirección de sincronización
            sync_interval: Intervalo de sincronización en segundos
            conflict_resolution: Estrategia de resolución de conflictos
            metadata: Metadata adicional
            
        Returns:
            ID de la regla
        """
        if source_endpoint not in self.endpoints:
            raise ValueError(f"Source endpoint not found: {source_endpoint}")
        if target_endpoint not in self.endpoints:
            raise ValueError(f"Target endpoint not found: {target_endpoint}")
        
        rule_id = str(uuid.uuid4())
        
        rule = SyncRule(
            rule_id=rule_id,
            name=name,
            source_endpoint=source_endpoint,
            target_endpoint=target_endpoint,
            direction=direction,
            sync_interval=sync_interval,
            conflict_resolution=conflict_resolution,
            metadata=metadata or {}
        )
        
        self.rules[rule_id] = rule
        logger.info(f"Created sync rule: {name} ({rule_id})")
        
        return rule_id
    
    async def sync(
        self,
        rule_id: str,
        force: bool = False
    ) -> SyncResult:
        """
        Sincronizar según regla.
        
        Args:
            rule_id: ID de la regla
            force: Forzar sincronización incluso si no es tiempo
            
        Returns:
            Resultado de la sincronización
        """
        if rule_id not in self.rules:
            raise ValueError(f"Rule not found: {rule_id}")
        
        rule = self.rules[rule_id]
        
        if not rule.enabled:
            raise ValueError(f"Rule {rule_id} is disabled")
        
        sync_id = str(uuid.uuid4())
        sync_result = SyncResult(
            sync_id=sync_id,
            rule_id=rule_id,
            status=SyncStatus.SYNCING
        )
        
        try:
            source = self.endpoints[rule.source_endpoint]
            target = self.endpoints[rule.target_endpoint]
            
            if rule.direction in [SyncDirection.BIDIRECTIONAL, SyncDirection.SOURCE_TO_TARGET]:
                # Sincronizar de fuente a objetivo
                result = await self._sync_direction(source, target, rule)
                sync_result.items_synced += result.get("items_synced", 0)
                sync_result.conflicts.extend(result.get("conflicts", []))
            
            if rule.direction in [SyncDirection.BIDIRECTIONAL, SyncDirection.TARGET_TO_SOURCE]:
                # Sincronizar de objetivo a fuente
                result = await self._sync_direction(target, source, rule)
                sync_result.items_synced += result.get("items_synced", 0)
                sync_result.conflicts.extend(result.get("conflicts", []))
            
            if sync_result.conflicts:
                sync_result.status = SyncStatus.CONFLICT
            else:
                sync_result.status = SyncStatus.COMPLETED
            
            sync_result.completed_at = datetime.now().isoformat()
            
            # Actualizar último sync
            source.last_sync = datetime.now().isoformat()
            target.last_sync = datetime.now().isoformat()
            
        except Exception as e:
            sync_result.status = SyncStatus.FAILED
            sync_result.error = str(e)
            sync_result.completed_at = datetime.now().isoformat()
            logger.error(f"Error syncing rule {rule_id}: {e}", exc_info=True)
        
        self.sync_results.append(sync_result)
        if len(self.sync_results) > self.max_results:
            self.sync_results = self.sync_results[-self.max_results:]
        
        return sync_result
    
    async def _sync_direction(
        self,
        source: SyncEndpoint,
        target: SyncEndpoint,
        rule: SyncRule
    ) -> Dict[str, Any]:
        """
        Sincronizar en una dirección.
        
        Args:
            source: Endpoint fuente
            target: Endpoint objetivo
            rule: Regla de sincronización
            
        Returns:
            Resultado de la sincronización
        """
        import aiohttp
        
        try:
            # Obtener datos del fuente
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{source.endpoint}/data",
                    headers=source.credentials,
                    timeout=aiohttp.ClientTimeout(total=30.0)
                ) as response:
                    source_data = await response.json()
            
            # Enviar datos al objetivo
            conflicts = []
            items_synced = 0
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{target.endpoint}/sync",
                    json={"data": source_data},
                    headers=target.credentials,
                    timeout=aiohttp.ClientTimeout(total=30.0)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        items_synced = result.get("items_synced", 0)
                        conflicts = result.get("conflicts", [])
                    elif response.status == 409:  # Conflict
                        conflicts = await response.json()
                    else:
                        raise Exception(f"Sync failed with status {response.status}")
            
            return {
                "items_synced": items_synced,
                "conflicts": conflicts
            }
        except Exception as e:
            logger.error(f"Error syncing from {source.name} to {target.name}: {e}", exc_info=True)
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de sincronización."""
        status_counts = {}
        for result in self.sync_results:
            status_counts[result.status.value] = status_counts.get(result.status.value, 0) + 1
        
        total_items = sum(r.items_synced for r in self.sync_results)
        total_conflicts = sum(len(r.conflicts) for r in self.sync_results)
        
        return {
            "total_endpoints": len(self.endpoints),
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "total_syncs": len(self.sync_results),
            "status_counts": status_counts,
            "total_items_synced": total_items,
            "total_conflicts": total_conflicts
        }


# Instancia global
_data_synchronization_manager: Optional[DataSynchronizationManager] = None


def get_data_synchronization_manager() -> DataSynchronizationManager:
    """Obtener instancia global del gestor de sincronización."""
    global _data_synchronization_manager
    if _data_synchronization_manager is None:
        _data_synchronization_manager = DataSynchronizationManager()
    return _data_synchronization_manager


