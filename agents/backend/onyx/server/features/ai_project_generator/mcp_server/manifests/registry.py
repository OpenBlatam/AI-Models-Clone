"""
Manifest Registry - Registro de manifiestos de recursos
========================================================
"""

from typing import Dict, Optional, List
from .models import ResourceManifest


class ManifestRegistry:
    """
    Registro centralizado de manifiestos de recursos
    
    Permite registrar, obtener y listar recursos disponibles.
    """
    
    def __init__(self):
        self._manifests: Dict[str, ResourceManifest] = {}
    
    def register(self, manifest: ResourceManifest):
        """
        Registra un manifest de recurso
        
        Args:
            manifest: Manifest del recurso
        """
        self._manifests[manifest.resource_id] = manifest
    
    def get(self, resource_id: str) -> Optional[ResourceManifest]:
        """
        Obtiene un manifest por resource_id
        
        Args:
            resource_id: ID del recurso
            
        Returns:
            Manifest o None si no existe
        """
        return self._manifests.get(resource_id)
    
    def get_all(self) -> List[ResourceManifest]:
        """
        Obtiene todos los manifests registrados
        
        Returns:
            Lista de todos los manifests
        """
        return list(self._manifests.values())
    
    def list_resource_ids(self) -> List[str]:
        """
        Lista todos los resource_ids registrados
        
        Returns:
            Lista de resource_ids
        """
        return list(self._manifests.keys())
    
    def unregister(self, resource_id: str) -> bool:
        """
        Elimina un manifest del registro
        
        Args:
            resource_id: ID del recurso
            
        Returns:
            True si se eliminó, False si no existía
        """
        if resource_id in self._manifests:
            del self._manifests[resource_id]
            return True
        return False
    
    def clear(self):
        """Limpia todos los manifests"""
        self._manifests.clear()

