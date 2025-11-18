"""
API Connector - Conector para APIs externas
============================================
"""

import httpx
import logging
from typing import Any, Dict, Optional

from .base import BaseConnector
from ..contracts import ContextFrame

logger = logging.getLogger(__name__)


class APIConnector(BaseConnector):
    """
    Conector para acceso a APIs externas
    
    Operaciones soportadas:
    - get: GET request
    - post: POST request
    - put: PUT request
    - delete: DELETE request
    - patch: PATCH request
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Inicializa el conector de API
        
        Args:
            base_url: URL base para requests (opcional)
            timeout: Timeout en segundos
        """
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._supported_operations = {
            "get", "post", "put", "delete", "patch", "request"
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea cliente HTTP"""
        if not self._client:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client
    
    async def execute(
        self,
        resource_id: str,
        operation: str,
        parameters: Dict[str, Any],
        context: Optional[ContextFrame] = None,
    ) -> Any:
        """Ejecuta operación sobre API"""
        
        if not self.validate_operation(operation):
            raise ValueError(f"Operation {operation} not supported")
        
        client = await self._get_client()
        
        url = parameters.get("url", resource_id)
        headers = parameters.get("headers", {})
        params = parameters.get("params", {})
        data = parameters.get("data")
        json_data = parameters.get("json")
        
        try:
            if operation == "get":
                response = await client.get(url, headers=headers, params=params)
            elif operation == "post":
                response = await client.post(url, headers=headers, params=params, data=data, json=json_data)
            elif operation == "put":
                response = await client.put(url, headers=headers, params=params, data=data, json=json_data)
            elif operation == "delete":
                response = await client.delete(url, headers=headers, params=params)
            elif operation == "patch":
                response = await client.patch(url, headers=headers, params=params, data=data, json=json_data)
            elif operation == "request":
                method = parameters.get("method", "GET").upper()
                response = await client.request(method, url, headers=headers, params=params, data=data, json=json_data)
            else:
                raise ValueError(f"Operation {operation} not implemented")
            
            response.raise_for_status()
            
            # Intentar parsear JSON, si falla retornar texto
            try:
                content = response.json()
            except Exception:
                content = response.text
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": content,
                "url": str(response.url),
            }
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in API connector: {e}")
            raise ValueError(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error in API connector: {e}")
            raise
    
    def validate_operation(self, operation: str) -> bool:
        """Valida si operación es soportada"""
        return operation.lower() in self._supported_operations
    
    def get_supported_operations(self) -> list[str]:
        """Retorna operaciones soportadas"""
        return list(self._supported_operations)
    
    async def close(self):
        """Cierra cliente HTTP"""
        if self._client:
            await self._client.aclose()
            self._client = None

