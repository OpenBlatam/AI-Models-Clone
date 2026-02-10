"""
Data Replication System
=======================

Sistema de replicación de datos.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ReplicationStatus(Enum):
    """Estado de replicación."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ReplicationTarget:
    """Objetivo de replicación."""
    target_id: str
    name: str
    endpoint: str
    connection_string: Optional[str] = None
    credentials: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicationJob:
    """Trabajo de replicación."""
    job_id: str
    source: str
    targets: List[str]
    data_type: str
    status: ReplicationStatus = ReplicationStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataReplicationManager:
    """
    Gestor de replicación de datos.
    
    Gestiona replicación de datos a múltiples destinos.
    """
    
    def __init__(self):
        """Inicializar gestor de replicación."""
        self.targets: Dict[str, ReplicationTarget] = {}
        self.jobs: Dict[str, ReplicationJob] = {}
        self.replication_history: List[Dict[str, Any]] = []
        self.max_history = 10000
    
    def register_target(
        self,
        name: str,
        endpoint: str,
        connection_string: Optional[str] = None,
        credentials: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Registrar objetivo de replicación.
        
        Args:
            name: Nombre del objetivo
            endpoint: Endpoint del objetivo
            connection_string: String de conexión
            credentials: Credenciales
            metadata: Metadata adicional
            
        Returns:
            ID del objetivo
        """
        target_id = str(uuid.uuid4())
        
        target = ReplicationTarget(
            target_id=target_id,
            name=name,
            endpoint=endpoint,
            connection_string=connection_string,
            credentials=credentials or {},
            metadata=metadata or {}
        )
        
        self.targets[target_id] = target
        logger.info(f"Registered replication target: {name} ({target_id})")
        
        return target_id
    
    def create_replication_job(
        self,
        source: str,
        targets: List[str],
        data_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Crear trabajo de replicación.
        
        Args:
            source: Fuente de datos
            targets: Lista de IDs de objetivos
            data_type: Tipo de datos
            metadata: Metadata adicional
            
        Returns:
            ID del trabajo
        """
        job_id = str(uuid.uuid4())
        
        # Validar objetivos
        for target_id in targets:
            if target_id not in self.targets:
                raise ValueError(f"Target not found: {target_id}")
        
        job = ReplicationJob(
            job_id=job_id,
            source=source,
            targets=targets,
            data_type=data_type,
            metadata=metadata or {}
        )
        
        self.jobs[job_id] = job
        logger.info(f"Created replication job: {job_id}")
        
        return job_id
    
    async def execute_replication(
        self,
        job_id: str,
        data: Any,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Ejecutar replicación.
        
        Args:
            job_id: ID del trabajo
            data: Datos a replicar
            progress_callback: Callback de progreso
            
        Returns:
            Resultado de la replicación
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self.jobs[job_id]
        job.status = ReplicationStatus.IN_PROGRESS
        job.started_at = datetime.now().isoformat()
        
        results = {}
        errors = []
        
        try:
            total_targets = len(job.targets)
            
            for i, target_id in enumerate(job.targets):
                target = self.targets[target_id]
                
                try:
                    # Replicar a objetivo
                    result = await self._replicate_to_target(target, data, job.data_type)
                    results[target_id] = result
                    
                    # Actualizar progreso
                    job.progress = (i + 1) / total_targets * 100.0
                    if progress_callback:
                        await progress_callback(job.progress)
                    
                    logger.info(f"Replicated to {target.name}: {target_id}")
                except Exception as e:
                    error_msg = f"Error replicating to {target.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg, exc_info=True)
                    results[target_id] = {"error": str(e)}
            
            if errors:
                job.status = ReplicationStatus.FAILED
                job.error = "; ".join(errors)
            else:
                job.status = ReplicationStatus.COMPLETED
            
            job.completed_at = datetime.now().isoformat()
            
            # Registrar en historial
            self.replication_history.append({
                "job_id": job_id,
                "source": job.source,
                "targets": job.targets,
                "status": job.status.value,
                "duration_seconds": (
                    datetime.fromisoformat(job.completed_at) -
                    datetime.fromisoformat(job.started_at)
                ).total_seconds(),
                "timestamp": datetime.now().isoformat()
            })
            
            if len(self.replication_history) > self.max_history:
                self.replication_history = self.replication_history[-self.max_history:]
            
            return {
                "job_id": job_id,
                "status": job.status.value,
                "results": results,
                "errors": errors
            }
        except Exception as e:
            job.status = ReplicationStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now().isoformat()
            logger.error(f"Error executing replication job {job_id}: {e}", exc_info=True)
            raise
    
    async def _replicate_to_target(
        self,
        target: ReplicationTarget,
        data: Any,
        data_type: str
    ) -> Dict[str, Any]:
        """
        Replicar a objetivo específico.
        
        Args:
            target: Objetivo
            data: Datos
            data_type: Tipo de datos
            
        Returns:
            Resultado de la replicación
        """
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{target.endpoint}/replicate",
                    json={
                        "data": data,
                        "data_type": data_type
                    },
                    headers=target.credentials,
                    timeout=aiohttp.ClientTimeout(total=60.0)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Replication failed with status {response.status}")
        except Exception as e:
            logger.error(f"Error replicating to {target.name}: {e}", exc_info=True)
            raise
    
    def get_job(self, job_id: str) -> Optional[ReplicationJob]:
        """Obtener trabajo por ID."""
        return self.jobs.get(job_id)
    
    def get_target(self, target_id: str) -> Optional[ReplicationTarget]:
        """Obtener objetivo por ID."""
        return self.targets.get(target_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de replicación."""
        status_counts = {}
        for job in self.jobs.values():
            status_counts[job.status.value] = status_counts.get(job.status.value, 0) + 1
        
        successful = sum(1 for h in self.replication_history if h.get("status") == "completed")
        failed = sum(1 for h in self.replication_history if h.get("status") == "failed")
        
        return {
            "total_targets": len(self.targets),
            "total_jobs": len(self.jobs),
            "status_counts": status_counts,
            "total_replications": len(self.replication_history),
            "successful_replications": successful,
            "failed_replications": failed
        }


# Instancia global
_data_replication_manager: Optional[DataReplicationManager] = None


def get_data_replication_manager() -> DataReplicationManager:
    """Obtener instancia global del gestor de replicación."""
    global _data_replication_manager
    if _data_replication_manager is None:
        _data_replication_manager = DataReplicationManager()
    return _data_replication_manager


