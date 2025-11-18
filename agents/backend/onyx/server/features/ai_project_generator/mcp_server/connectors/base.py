"""
Base Connector - Clase base para conectores MCP
===============================================
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..contracts import ContextFrame


class BaseConnector(ABC):
    """
    Clase base abstracta para todos los conectores MCP
    
    Cada conector debe implementar:
    - execute(): ejecuta operaciones sobre el recurso
    - validate_operation(): valida si una operación es soportada
    """
    
    @abstractmethod
    async def execute(
        self,
        resource_id: str,
        operation: str,
        parameters: Dict[str, Any],
        context: Optional[ContextFrame] = None,
    ) -> Any:
        """
        Ejecuta una operación sobre el recurso
        
        Args:
            resource_id: ID del recurso
            operation: Operación a realizar (read, write, query, etc.)
            parameters: Parámetros de la operación
            context: Frame de contexto adicional
            
        Returns:
            Resultado de la operación
        """
        pass
    
    @abstractmethod
    def validate_operation(self, operation: str) -> bool:
        """
        Valida si una operación es soportada por este conector
        
        Args:
            operation: Nombre de la operación
            
        Returns:
            True si la operación es soportada
        """
        pass
    
    @abstractmethod
    def get_supported_operations(self) -> list[str]:
        """
        Retorna lista de operaciones soportadas
        
        Returns:
            Lista de nombres de operaciones
        """
        pass

