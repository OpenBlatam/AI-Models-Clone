from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .main import create_app
from .routes import api_router
from .dependencies import get_current_user, get_database, get_cache
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
API Module - FastAPI Endpoints y Controladores
==============================================

Este módulo contiene todos los endpoints y controladores de la API:
- main: Aplicación FastAPI principal
- routes: Definición de rutas
- middleware: Middleware personalizado
- dependencies: Dependencias compartidas
"""


__all__ = [
    "create_app",
    "api_router",
    "get_current_user",
    "get_database", 
    "get_cache"
] 