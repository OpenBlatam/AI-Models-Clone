"""
Connector Registry - Registro de conectores disponibles
========================================================
"""

from typing import Dict, Optional
from .base import BaseConnector


class ConnectorRegistry:
    """
    Registro centralizado de conectores MCP
    
    Permite registrar y obtener conectores por tipo.
    """
    
    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}
    
    def register(self, connector_type: str, connector: BaseConnector):
        """
        Registra un conector
        
        Args:
            connector_type: Tipo del conector (filesystem, database, api, etc.)
            connector: Instancia del conector
        """
        self._connectors[connector_type.lower()] = connector
    
    def get(self, connector_type: str) -> Optional[BaseConnector]:
        """
        Obtiene un conector por tipo
        
        Args:
            connector_type: Tipo del conector
            
        Returns:
            Conector o None si no existe
        """
        return self._connectors.get(connector_type.lower())
    
    def list_connectors(self) -> list[str]:
        """
        Lista todos los tipos de conectores registrados
        
        Returns:
            Lista de tipos de conectores
        """
        return list(self._connectors.keys())
    
    def unregister(self, connector_type: str) -> bool:
        """
        Elimina un conector del registro
        
        Args:
            connector_type: Tipo del conector
            
        Returns:
            True si se eliminó, False si no existía
        """
        if connector_type.lower() in self._connectors:
            del self._connectors[connector_type.lower()]
            return True
        return False

