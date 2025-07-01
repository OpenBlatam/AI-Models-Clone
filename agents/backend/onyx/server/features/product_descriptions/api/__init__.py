"""
API module for Product Descriptions Generator
=============================================

Contains web services, REST API endpoints, and external interfaces.
"""

from .service import ProductDescriptionService
from .gradio_interface import ProductDescriptionGradioApp

__all__ = ["ProductDescriptionService", "ProductDescriptionGradioApp"] 