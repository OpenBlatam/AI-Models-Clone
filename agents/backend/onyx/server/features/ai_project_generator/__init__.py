"""
AI Project Generator - Generador Automático de Proyectos de IA
===============================================================

Sistema que genera automáticamente la estructura completa de backend y frontend
para proyectos de IA basándose en una descripción del usuario.
Funciona de forma continua sin parar, generando proyectos automáticamente.
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

from .core.project_generator import ProjectGenerator
from .core.backend_generator import BackendGenerator
from .core.frontend_generator import FrontendGenerator
from .core.continuous_generator import ContinuousGenerator
from .core.deep_learning_generator import DeepLearningGenerator
from .api.generator_api import create_generator_app

__all__ = [
    "ProjectGenerator",
    "BackendGenerator",
    "FrontendGenerator",
    "ContinuousGenerator",
    "DeepLearningGenerator",
    "create_generator_app",
]
