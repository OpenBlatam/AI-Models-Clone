"""
AWS Lambda Handler
==================

Handler optimizado para AWS Lambda con FastAPI usando Mangum.
Incluye optimizaciones para cold start reduction.
"""

import logging
import os
from typing import Optional, Callable, Any
from fastapi import FastAPI

logger = logging.getLogger(__name__)

# Mangum para adaptar FastAPI a Lambda
try:
    from mangum import Mangum
    MANGUM_AVAILABLE = True
except ImportError:
    MANGUM_AVAILABLE = False
    Mangum = None


class LambdaHandler:
    """Handler optimizado para AWS Lambda"""
    
    def __init__(self, app: FastAPI, lifespan: str = "off"):
        """
        Inicializa el handler Lambda
        
        Args:
            app: Aplicación FastAPI
            lifespan: "off", "on", o "auto" para lifespan events
        """
        if not MANGUM_AVAILABLE:
            raise ImportError(
                "Mangum no está disponible. Instala con: pip install mangum"
            )
        
        self.app = app
        self.handler = Mangum(app, lifespan=lifespan)
        self._optimize_for_lambda()
    
    def _optimize_for_lambda(self):
        """Optimizaciones específicas para Lambda"""
        # Configurar variables de entorno para Lambda
        os.environ.setdefault("LAMBDA_TASK_ROOT", "/var/task")
        os.environ.setdefault("AWS_LAMBDA_RUNTIME_API", "localhost:9001")
        
        # Optimizar logging
        logging.getLogger().setLevel(logging.INFO)
        
        logger.info("Lambda handler optimizado")
    
    def __call__(self, event: dict, context: Any) -> dict:
        """Invoca el handler Lambda"""
        return self.handler(event, context)
    
    @property
    def handler_function(self) -> Callable:
        """Retorna la función handler para Lambda"""
        return self.handler


def create_lambda_handler(
    app: FastAPI,
    lifespan: str = "off",
    enable_cors: bool = True,
    enable_compression: bool = True
) -> Callable:
    """
    Crea un handler Lambda optimizado
    
    Args:
        app: Aplicación FastAPI
        lifespan: Manejo de lifespan events
        enable_cors: Habilitar CORS
        enable_compression: Habilitar compresión
        
    Returns:
        Función handler para Lambda
    """
    # Configurar CORS si es necesario
    if enable_cors:
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Crear handler
    lambda_handler = LambdaHandler(app, lifespan=lifespan)
    
    return lambda_handler.handler_function


# Template para lambda_function.py
LAMBDA_FUNCTION_TEMPLATE = '''"""
Lambda Function para AWS
========================

Handler para desplegar FastAPI en AWS Lambda.
"""

from mangum import Mangum
from {module_path} import app

# Crear handler
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """Handler principal de Lambda"""
    return handler(event, context)
'''




