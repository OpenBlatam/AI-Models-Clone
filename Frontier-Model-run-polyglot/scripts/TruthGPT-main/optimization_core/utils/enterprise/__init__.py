"""
Enterprise Utilities Module

This module contains enterprise-grade utilities for authentication, caching,
monitoring, and cloud integration.
"""

from __future__ import annotations

import importlib

__all__ = [
    'EnterpriseAuth',
    'EnterpriseCache',
    'EnterpriseMonitor',
    'EnterpriseMetrics',
    'EnterpriseCloudIntegration',
    'EnterpriseTruthGPTAdapter',
]

_LAZY_IMPORTS = {
    'EnterpriseAuth': 'optimization_core.modules.enterprise.auth',
    'EnterpriseCache': 'optimization_core.modules.enterprise.cache',
    'EnterpriseMonitor': 'optimization_core.modules.enterprise.monitor',
    'EnterpriseMetrics': 'optimization_core.modules.enterprise.metrics',
    'EnterpriseCloudIntegration': 'optimization_core.modules.enterprise.cloud_integration',
    'EnterpriseTruthGPTAdapter': 'optimization_core.adapters.enterprise_truthgpt_adapter',
}

_import_cache = {}


def __getattr__(name: str):
    """Lazy import system for enterprise utility modules."""
    if name.startswith('_'):
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    if name in _import_cache:
        return _import_cache[name]
    
    module_path = _LAZY_IMPORTS[name]
    try:
        # Use absolute imports to avoid __package__ ambiguity
        module = importlib.import_module(module_path)
        obj = getattr(module, name)
        _import_cache[name] = obj
        return obj
    except (ImportError, AttributeError) as e:
        raise AttributeError(
            f"module '{__name__}' has no attribute '{name}'. "
            f"Failed to import: {e}"
        ) from e



