"""
Onyx Plugin Manager

A comprehensive plugin management system for Onyx AI video processing,
providing modular, extensible, and high-performance plugin architecture.
"""

# Core components
from .core import (
    OnyxPluginInfo,
    OnyxPluginContext,
    PluginStatus,
    PluginExecutionResult,
    PluginManagerStatus,
    OnyxPluginBase
)

# Main manager
from .manager import OnyxPluginManager

# Example plugins
from .plugins import (
    OnyxContentAnalyzerPlugin,
    OnyxVisualEnhancerPlugin,
    OnyxAudioProcessorPlugin,
    OnyxMetadataExtractorPlugin,
    OnyxQualityAssurancePlugin
)

# Utility functions
from .utils import (
    initialize_onyx_plugins,
    execute_onyx_plugins,
    get_onyx_plugin_status,
    enable_plugin,
    disable_plugin,
    reload_plugin,
    get_plugin_info,
    get_all_plugins_info,
    cleanup_onyx_plugins,
    create_plugin_context,
    execute_plugin_pipeline,
    validate_plugin_pipeline,
    get_plugin_statistics,
    health_check,
    onyx_plugin_manager
)

__version__ = "1.0.0"
__author__ = "Onyx Team"

__all__ = [
    # Core components
    "OnyxPluginInfo",
    "OnyxPluginContext",
    "PluginStatus", 
    "PluginExecutionResult",
    "PluginManagerStatus",
    "OnyxPluginBase",
    
    # Main manager
    "OnyxPluginManager",
    
    # Example plugins
    "OnyxContentAnalyzerPlugin",
    "OnyxVisualEnhancerPlugin",
    "OnyxAudioProcessorPlugin", 
    "OnyxMetadataExtractorPlugin",
    "OnyxQualityAssurancePlugin",
    
    # Utility functions
    "initialize_onyx_plugins",
    "execute_onyx_plugins",
    "get_onyx_plugin_status",
    "enable_plugin",
    "disable_plugin",
    "reload_plugin",
    "get_plugin_info",
    "get_all_plugins_info",
    "cleanup_onyx_plugins",
    "create_plugin_context",
    "execute_plugin_pipeline",
    "validate_plugin_pipeline",
    "get_plugin_statistics",
    "health_check",
    "onyx_plugin_manager"
] 