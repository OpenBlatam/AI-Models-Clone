"""
Modular SEO System - Enterprise-Grade Architecture
A completely modular, microservice-based SEO analysis system
"""

__version__ = "2.0.0"
__author__ = "Enhanced SEO Team"
__description__ = "Modular SEO analysis system with microservices architecture"

from .core import SEOEngine
from .config import SystemConfig
from .factories import EngineFactory

__all__ = ["SEOEngine", "SystemConfig", "EngineFactory"]
