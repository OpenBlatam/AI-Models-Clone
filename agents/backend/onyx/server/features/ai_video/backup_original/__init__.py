"""
AI Video System - Production Ready

A comprehensive, production-ready AI video generation system with advanced
plugin architecture, robust workflow management, and extensive monitoring.

This module provides the main API for the AI Video System.
"""

__version__ = "1.0.0"
__author__ = "AI Video Team"
__description__ = "Production-ready AI video generation system"

# Core exports
from .main import AIVideoSystem, quick_generate, batch_generate
from .integrated_workflow import IntegratedVideoWorkflow, create_integrated_workflow
from .config import AIVideoConfig, load_config, ConfigManager
from .models import AIVideo

# Plugin system exports
from .plugins import PluginManager, ManagerConfig, ValidationLevel
from .plugins.integration import create_plugin_integration

# Workflow exports
from .video_workflow import VideoWorkflow, WorkflowState, WorkflowStatus

# Utility exports
from .metrics import record_extraction_metrics, record_generation_metrics, record_workflow_metrics

__all__ = [
    # Main system
    "AIVideoSystem",
    "quick_generate", 
    "batch_generate",
    
    # Workflow
    "IntegratedVideoWorkflow",
    "create_integrated_workflow",
    "VideoWorkflow",
    "WorkflowState", 
    "WorkflowStatus",
    
    # Configuration
    "AIVideoConfig",
    "load_config",
    "ConfigManager",
    
    # Models
    "AIVideo",
    
    # Plugin system
    "PluginManager",
    "ManagerConfig", 
    "ValidationLevel",
    "create_plugin_integration",
    
    # Metrics
    "record_extraction_metrics",
    "record_generation_metrics", 
    "record_workflow_metrics",
    
    # Version info
    "__version__",
    "__author__",
    "__description__"
] 