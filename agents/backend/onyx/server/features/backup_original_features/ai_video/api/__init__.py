"""
APIS, SERVICIOS WEB Y ENDPOINTS
==============================

APIs, servicios web y endpoints

Estructura del módulo:
- fastapi_microservice.py: Microservicio FastAPI principal
- services.py: Servicios web y lógica de negocio
- utils_api.py: Utilidades para APIs
- utils_batch.py: Utilidades para procesamiento por lotes
- aws_lambda_handler.py: Handler para AWS Lambda
"""

# Importaciones automáticas
import os
from pathlib import Path

# Metadata del módulo
__module_name__ = "api"
__description__ = "APIs, servicios web y endpoints"
__version__ = "1.0.0"

# Path del módulo
MODULE_PATH = Path(__file__).parent

# Auto-discovery de archivos Python
__all__ = []
for file_path in MODULE_PATH.glob("*.py"):
    if file_path.name != "__init__.py":
        module_name = file_path.stem
        __all__.append(module_name)

def get_module_info():
    """Obtener información del módulo."""
    return {
        "name": __module_name__,
        "description": __description__,
        "version": __version__,
        "path": str(MODULE_PATH),
        "files": __all__
    }

def list_files():
    """Listar archivos en el módulo."""
    return [f.name for f in MODULE_PATH.glob("*.py")]

# Importaciones principales para facilitar el uso
try:
    from . import fastapi_microservice
    from . import services
    from . import utils_api
    from . import utils_batch
    from . import aws_lambda_handler
except ImportError as e:
    import logging
    logging.warning(f"No se pudieron importar algunos módulos de API: {e}") 