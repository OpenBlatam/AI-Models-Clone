"""
Core module for Product Descriptions Generator
==============================================

Contains the main model architectures, generators, and core functionality.
"""

from .model import ProductDescriptionModel
from .generator import ProductDescriptionGenerator
from .config import ProductDescriptionConfig

__all__ = ["ProductDescriptionModel", "ProductDescriptionGenerator", "ProductDescriptionConfig"] 