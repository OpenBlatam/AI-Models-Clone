"""
Resource Manifest Models - Modelos Pydantic para manifiestos
============================================================
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator


class ResourceType(str, Enum):
    """Tipos de recursos soportados"""
    FILESYSTEM = "filesystem"
    DATABASE = "database"
    API = "api"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    CUSTOM = "custom"


class ResourcePermissions(BaseModel):
    """Permisos de un recurso"""
    read: bool = Field(default=False, description="Permiso de lectura")
    write: bool = Field(default=False, description="Permiso de escritura")
    delete: bool = Field(default=False, description="Permiso de eliminación")
    admin: bool = Field(default=False, description="Permiso de administración")
    
    def to_scopes(self) -> List[str]:
        """Convierte permisos a lista de scopes"""
        scopes = []
        if self.read:
            scopes.append("read")
        if self.write:
            scopes.append("write")
        if self.delete:
            scopes.append("delete")
        if self.admin:
            scopes.append("admin")
        return scopes


class ResourceManifest(BaseModel):
    """
    Manifest de un recurso MCP
    
    Describe completamente un recurso disponible a través del servidor MCP.
    """
    
    resource_id: str = Field(..., description="ID único del recurso")
    name: str = Field(..., description="Nombre descriptivo del recurso")
    type: ResourceType = Field(..., description="Tipo de recurso")
    connector_type: str = Field(..., description="Tipo de conector a usar")
    
    description: Optional[str] = Field(None, description="Descripción del recurso")
    version: str = Field(default="1.0.0", description="Versión del recurso")
    
    # Configuración de acceso
    permissions: ResourcePermissions = Field(
        default_factory=lambda: ResourcePermissions(read=True),
        description="Permisos por defecto del recurso"
    )
    required_scopes: List[str] = Field(
        default_factory=list,
        description="Scopes requeridos para acceder"
    )
    
    # Endpoints y configuración
    endpoint: Optional[str] = Field(None, description="Endpoint específico (si aplica)")
    connection_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuración de conexión específica"
    )
    
    # Schema de datos
    data_schema: Optional[Dict[str, Any]] = Field(
        None,
        description="Schema JSON del formato de datos"
    )
    
    # Operaciones soportadas
    supported_operations: List[str] = Field(
        default_factory=list,
        description="Lista de operaciones soportadas"
    )
    
    # Límites y restricciones
    max_context_size: Optional[int] = Field(
        None,
        description="Tamaño máximo de contexto en tokens"
    )
    rate_limit: Optional[Dict[str, Any]] = Field(
        None,
        description="Límites de rate (requests per minute, etc.)"
    )
    
    # Metadata adicional
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata adicional del recurso"
    )
    
    @validator("resource_id")
    def validate_resource_id(cls, v):
        """Valida que resource_id sea válido"""
        if not v or not v.strip():
            raise ValueError("resource_id cannot be empty")
        if " " in v or "/" in v:
            raise ValueError("resource_id cannot contain spaces or slashes")
        return v.strip().lower()
    
    @validator("name")
    def validate_name(cls, v):
        """Valida que name sea válido"""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte manifest a diccionario"""
        return self.dict(exclude_none=True)
    
    def to_json(self) -> str:
        """Convierte manifest a JSON string"""
        import json
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceManifest":
        """Crea manifest desde diccionario"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ResourceManifest":
        """Crea manifest desde JSON string"""
        import json
        return cls.from_dict(json.loads(json_str))

