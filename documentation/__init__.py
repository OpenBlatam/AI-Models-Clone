"""
Instagram Captions API Documentation System

A comprehensive documentation generation system for the Instagram Captions API v10.0.
This system automatically generates API documentation in multiple formats including
OpenAPI specification, Markdown, and HTML.

Main Components:
- APIDocumentation: Core documentation management class
- APIEndpoint: Represents an API endpoint
- APIModel: Represents an API data model
- generate_docs: Instagram API documentation generator
- cli: Command-line interface for documentation management
"""

from .api_documentation import APIDocumentation, APIEndpoint, APIModel
from .generate_docs import create_instagram_captions_api_docs

__version__ = "10.0.0"
__author__ = "Blatam Academy Team"
__email__ = "support@blatam-academy.com"

__all__ = [
    "APIDocumentation",
    "APIEndpoint", 
    "APIModel",
    "create_instagram_captions_api_docs"
]

# Convenience function for quick documentation generation
def generate_instagram_docs(output_dir: str = "generated_docs") -> bool:
    """
    Quick function to generate Instagram Captions API documentation.
    
    Args:
        output_dir: Directory to save generated documentation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        api_docs = create_instagram_captions_api_docs()
        return api_docs.export_all_formats(output_dir)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating documentation: {e}")
        return False
