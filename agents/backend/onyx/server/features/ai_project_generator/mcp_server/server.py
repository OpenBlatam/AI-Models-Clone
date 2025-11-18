"""
MCP Server - Servidor principal del Model Context Protocol
==========================================================

Servidor minimal que expone conectores estandarizados para acceso
a recursos (archivos, DB, APIs) de forma segura y observable.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from .connectors import ConnectorRegistry, BaseConnector
from .manifests import ManifestRegistry, ResourceManifest
from .security import MCPSecurityManager, Scope
from .contracts import ContextFrame, FrameSerializer
from .observability import MCPObservability

logger = logging.getLogger(__name__)
security = HTTPBearer()


class MCPRequest(BaseModel):
    """Request model para llamadas MCP"""
    resource_id: str = Field(..., description="ID del recurso a consultar")
    operation: str = Field(..., description="Operación a realizar")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros de la operación")
    context: Optional[ContextFrame] = Field(None, description="Frame de contexto adicional")


class MCPResponse(BaseModel):
    """Response model para llamadas MCP"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MCPServer:
    """
    Servidor MCP principal
    
    Expone endpoints para:
    - Listar recursos disponibles
    - Consultar recursos específicos
    - Operaciones sobre recursos (read, write, query, etc.)
    """
    
    def __init__(
        self,
        connector_registry: ConnectorRegistry,
        manifest_registry: ManifestRegistry,
        security_manager: MCPSecurityManager,
        observability: Optional[MCPObservability] = None,
    ):
        self.connector_registry = connector_registry
        self.manifest_registry = manifest_registry
        self.security_manager = security_manager
        self.observability = observability or MCPObservability()
        
        self.app = FastAPI(
            title="MCP Server",
            description="Model Context Protocol Server",
            version="1.0.0",
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas del servidor MCP"""
        
        @self.app.get("/mcp/v1/resources")
        async def list_resources(
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ) -> List[Dict[str, Any]]:
            """Lista todos los recursos disponibles"""
            with self.observability.trace("list_resources"):
                # Verificar autenticación
                user = await self.security_manager.verify_token(credentials.credentials)
                
                # Filtrar recursos por permisos
                available_resources = []
                for manifest in self.manifest_registry.get_all():
                    if self.security_manager.has_access(user, manifest.resource_id, Scope.READ):
                        available_resources.append(manifest.to_dict())
                
                self.observability.record_metric("mcp_resources_listed", len(available_resources))
                return available_resources
        
        @self.app.get("/mcp/v1/resources/{resource_id}")
        async def get_resource(
            resource_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ) -> Dict[str, Any]:
            """Obtiene información de un recurso específico"""
            with self.observability.trace("get_resource"):
                user = await self.security_manager.verify_token(credentials.credentials)
                
                if not self.security_manager.has_access(user, resource_id, Scope.READ):
                    raise HTTPException(status_code=403, detail="Access denied")
                
                manifest = self.manifest_registry.get(resource_id)
                if not manifest:
                    raise HTTPException(status_code=404, detail="Resource not found")
                
                return manifest.to_dict()
        
        @self.app.post("/mcp/v1/resources/{resource_id}/query")
        async def query_resource(
            resource_id: str,
            request: MCPRequest,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ) -> MCPResponse:
            """Consulta un recurso específico"""
            with self.observability.trace("query_resource", resource_id=resource_id):
                user = await self.security_manager.verify_token(credentials.credentials)
                
                # Verificar permisos
                required_scope = self._get_scope_for_operation(request.operation)
                if not self.security_manager.has_access(user, resource_id, required_scope):
                    self.observability.record_error("access_denied", resource_id=resource_id)
                    raise HTTPException(status_code=403, detail="Access denied")
                
                # Obtener manifest y connector
                manifest = self.manifest_registry.get(resource_id)
                if not manifest:
                    raise HTTPException(status_code=404, detail="Resource not found")
                
                connector = self.connector_registry.get(manifest.connector_type)
                if not connector:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Connector {manifest.connector_type} not available"
                    )
                
                try:
                    # Ejecutar operación
                    result = await connector.execute(
                        resource_id=resource_id,
                        operation=request.operation,
                        parameters=request.parameters,
                        context=request.context,
                    )
                    
                    self.observability.record_metric(
                        "mcp_query_success",
                        1,
                        resource_id=resource_id,
                        operation=request.operation,
                    )
                    
                    return MCPResponse(
                        success=True,
                        data=result,
                        metadata={
                            "resource_id": resource_id,
                            "operation": request.operation,
                            "connector_type": manifest.connector_type,
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error querying resource {resource_id}: {e}", exc_info=True)
                    self.observability.record_error(
                        "mcp_query_error",
                        error=str(e),
                        resource_id=resource_id,
                        operation=request.operation,
                    )
                    
                    return MCPResponse(
                        success=False,
                        error=str(e),
                        metadata={
                            "resource_id": resource_id,
                            "operation": request.operation,
                        }
                    )
        
        @self.app.get("/mcp/v1/health")
        async def health_check() -> Dict[str, Any]:
            """Health check del servidor MCP"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "resources_count": len(self.manifest_registry.get_all()),
                "connectors_count": len(self.connector_registry.list_connectors()),
            }
    
    def _get_scope_for_operation(self, operation: str) -> Scope:
        """Determina el scope requerido para una operación"""
        read_ops = {"read", "query", "list", "get", "search"}
        write_ops = {"write", "create", "update", "delete", "modify"}
        
        if operation.lower() in read_ops:
            return Scope.READ
        elif operation.lower() in write_ops:
            return Scope.WRITE
        else:
            return Scope.READ  # Default seguro
    
    def get_app(self) -> FastAPI:
        """Retorna la aplicación FastAPI"""
        return self.app

