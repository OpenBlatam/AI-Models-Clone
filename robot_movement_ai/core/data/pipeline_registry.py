"""
Pipeline Registry
================

Registro centralizado y gestión de pipelines con metadatos y versionado.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Estado del pipeline."""
    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ERROR = "error"


@dataclass
class PipelineMetadata:
    """Metadatos de un pipeline."""
    name: str
    pipeline_type: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: PipelineStatus = PipelineStatus.REGISTERED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    last_used: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario."""
        return {
            'name': self.name,
            'pipeline_type': self.pipeline_type,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'usage_count': self.usage_count,
            'last_used': self.last_used,
            'config': self.config,
            'performance_metrics': self.performance_metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineMetadata':
        """Crear desde diccionario."""
        data = data.copy()
        data['status'] = PipelineStatus(data['status'])
        return cls(**data)


class PipelineRegistry:
    """
    Registro centralizado de pipelines con metadatos.
    """
    
    def __init__(self, persist_path: Optional[str] = None):
        """
        Inicializar registro.
        
        Args:
            persist_path: Ruta para persistir el registro (opcional)
        """
        self.pipelines: Dict[str, Any] = {}
        self.metadata: Dict[str, PipelineMetadata] = {}
        self.persist_path = Path(persist_path) if persist_path else None
        
        # Cargar desde disco si existe
        if self.persist_path and self.persist_path.exists():
            self._load_from_disk()
    
    def register(
        self,
        name: str,
        pipeline: Any,
        pipeline_type: str = "modular",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registrar pipeline con metadatos.
        
        Args:
            name: Nombre del pipeline
            pipeline: Instancia del pipeline
            pipeline_type: Tipo de pipeline
            metadata: Metadatos adicionales
        """
        # Crear o actualizar metadatos
        if name in self.metadata:
            meta = self.metadata[name]
            meta.updated_at = datetime.now().isoformat()
            if metadata:
                for key, value in metadata.items():
                    if hasattr(meta, key):
                        setattr(meta, key, value)
        else:
            meta = PipelineMetadata(
                name=name,
                pipeline_type=pipeline_type,
                **(metadata or {})
            )
            self.metadata[name] = meta
        
        # Registrar pipeline
        self.pipelines[name] = pipeline
        
        # Persistir si está configurado
        if self.persist_path:
            self._save_to_disk()
        
        logger.info(f"Pipeline registrado: {name} (v{meta.version})")
    
    def get(self, name: str) -> Optional[Any]:
        """
        Obtener pipeline.
        
        Args:
            name: Nombre del pipeline
            
        Returns:
            Pipeline o None
        """
        if name in self.pipelines:
            # Actualizar uso
            if name in self.metadata:
                self.metadata[name].usage_count += 1
                self.metadata[name].last_used = datetime.now().isoformat()
            return self.pipelines[name]
        return None
    
    def get_metadata(self, name: str) -> Optional[PipelineMetadata]:
        """
        Obtener metadatos de pipeline.
        
        Args:
            name: Nombre del pipeline
            
        Returns:
            Metadatos o None
        """
        return self.metadata.get(name)
    
    def list_pipelines(
        self,
        pipeline_type: Optional[str] = None,
        status: Optional[PipelineStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Listar pipelines con filtros.
        
        Args:
            pipeline_type: Filtrar por tipo
            status: Filtrar por estado
            tags: Filtrar por tags
            
        Returns:
            Lista de información de pipelines
        """
        results = []
        
        for name, meta in self.metadata.items():
            # Aplicar filtros
            if pipeline_type and meta.pipeline_type != pipeline_type:
                continue
            
            if status and meta.status != status:
                continue
            
            if tags:
                if not any(tag in meta.tags for tag in tags):
                    continue
            
            results.append(meta.to_dict())
        
        return results
    
    def update_metadata(
        self,
        name: str,
        **kwargs
    ) -> None:
        """
        Actualizar metadatos de pipeline.
        
        Args:
            name: Nombre del pipeline
            **kwargs: Campos a actualizar
        """
        if name not in self.metadata:
            raise ValueError(f"Pipeline '{name}' no está registrado")
        
        meta = self.metadata[name]
        for key, value in kwargs.items():
            if hasattr(meta, key):
                setattr(meta, key, value)
        
        meta.updated_at = datetime.now().isoformat()
        
        if self.persist_path:
            self._save_to_disk()
    
    def set_status(self, name: str, status: PipelineStatus) -> None:
        """
        Establecer estado de pipeline.
        
        Args:
            name: Nombre del pipeline
            status: Nuevo estado
        """
        self.update_metadata(name, status=status)
        logger.info(f"Estado de pipeline '{name}' actualizado a: {status.value}")
    
    def deprecate(self, name: str, reason: str = "") -> None:
        """
        Deprecar pipeline.
        
        Args:
            name: Nombre del pipeline
            reason: Razón de deprecación
        """
        self.set_status(name, PipelineStatus.DEPRECATED)
        if reason:
            self.update_metadata(name, description=f"[DEPRECATED] {reason}")
        logger.warning(f"Pipeline '{name}' deprecado: {reason}")
    
    def remove(self, name: str) -> None:
        """
        Remover pipeline del registro.
        
        Args:
            name: Nombre del pipeline
        """
        if name in self.pipelines:
            del self.pipelines[name]
        if name in self.metadata:
            del self.metadata[name]
        
        if self.persist_path:
            self._save_to_disk()
        
        logger.info(f"Pipeline removido: {name}")
    
    def search(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Buscar pipelines por query.
        
        Args:
            query: Query de búsqueda
            
        Returns:
            Lista de pipelines que coinciden
        """
        query_lower = query.lower()
        results = []
        
        for name, meta in self.metadata.items():
            # Buscar en nombre, descripción, tags
            if (query_lower in name.lower() or
                query_lower in meta.description.lower() or
                any(query_lower in tag.lower() for tag in meta.tags)):
                results.append(meta.to_dict())
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del registro.
        
        Returns:
            Diccionario con estadísticas
        """
        total = len(self.pipelines)
        by_type = {}
        by_status = {}
        
        for meta in self.metadata.values():
            by_type[meta.pipeline_type] = by_type.get(meta.pipeline_type, 0) + 1
            by_status[meta.status.value] = by_status.get(meta.status.value, 0) + 1
        
        return {
            'total_pipelines': total,
            'by_type': by_type,
            'by_status': by_status,
            'most_used': sorted(
                self.metadata.values(),
                key=lambda m: m.usage_count,
                reverse=True
            )[:5]
        }
    
    def _save_to_disk(self) -> None:
        """Guardar registro en disco."""
        if not self.persist_path:
            return
        
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'metadata': {
                    name: meta.to_dict()
                    for name, meta in self.metadata.items()
                }
            }
            
            with open(self.persist_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Registro guardado en: {self.persist_path}")
        except Exception as e:
            logger.error(f"Error guardando registro: {e}")
    
    def _load_from_disk(self) -> None:
        """Cargar registro desde disco."""
        if not self.persist_path or not self.persist_path.exists():
            return
        
        try:
            with open(self.persist_path, 'r') as f:
                data = json.load(f)
            
            for name, meta_data in data.get('metadata', {}).items():
                self.metadata[name] = PipelineMetadata.from_dict(meta_data)
            
            logger.info(f"Registro cargado desde: {self.persist_path}")
        except Exception as e:
            logger.error(f"Error cargando registro: {e}")


# Instancia global del registro
_global_registry: Optional[PipelineRegistry] = None


def get_registry(persist_path: Optional[str] = None) -> PipelineRegistry:
    """
    Obtener instancia global del registro.
    
    Args:
        persist_path: Ruta para persistencia (solo se usa en la primera llamada)
        
    Returns:
        Instancia del registro
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = PipelineRegistry(persist_path)
    
    return _global_registry

