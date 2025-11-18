"""
MCP Server - Model Context Protocol Integration Layer
======================================================

Servidor MCP que expone conectores estandarizados para:
- Sistema de archivos
- Bases de datos
- APIs externas

Proporciona una capa de integración unificada para que los modelos
puedan consultar fuentes autorizadas de contexto.
"""

__version__ = "1.0.0"

from .server import MCPServer
from .connectors import (
    FileSystemConnector,
    DatabaseConnector,
    APIConnector,
    ConnectorRegistry,
)
from .manifests import ResourceManifest, ManifestRegistry
from .security import MCPSecurityManager, Scope, AccessPolicy
from .contracts import ContextFrame, PromptFrame, FrameSerializer

__all__ = [
    "MCPServer",
    "FileSystemConnector",
    "DatabaseConnector",
    "APIConnector",
    "ConnectorRegistry",
    "ResourceManifest",
    "ManifestRegistry",
    "MCPSecurityManager",
    "Scope",
    "AccessPolicy",
    "ContextFrame",
    "PromptFrame",
    "FrameSerializer",
]

