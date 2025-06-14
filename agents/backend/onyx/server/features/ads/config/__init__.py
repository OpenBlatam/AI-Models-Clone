"""
Configuration initialization for the ads module.
"""
from .settings import settings
from .providers import providers_config
from .storage import storage_settings
from .monitoring import monitoring_settings
from .api import api_settings

__all__ = [
    'settings',
    'providers_config',
    'storage_settings',
    'monitoring_settings',
    'api_settings'
] 