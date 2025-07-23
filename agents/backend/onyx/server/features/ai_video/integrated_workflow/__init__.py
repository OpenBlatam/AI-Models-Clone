"""
Integrated Workflow - Main Module

Integrated AI video workflow system that combines video workflow with plugin system.
"""

# Core components
from .core import (
    IntegratedVideoWorkflow,
    IntegratedWorkflowStatus,
    PluginWorkflowState,
    IntegratedWorkflowHooks,
    WorkflowConfiguration,
    WorkflowStatistics,
    HealthReport
)

# Components
from .components import (
    IntegratedExtractor,
    IntegratedSuggestionEngine,
    IntegratedVideoGenerator,
    ExtractorManager,
    SuggestionEngineManager,
    VideoGeneratorManager
)

# Utilities
from .utils import (
    create_integrated_workflow,
    quick_video_generation,
    batch_video_generation,
    load_config_from_file,
    save_config_to_file,
    create_default_plugin_config,
    create_default_workflow_config,
    validate_workflow_state,
    get_workflow_summary,
    format_duration,
    create_workflow_report
)

__version__ = "1.0.0"
__author__ = "AI Video Team"

__all__ = [
    # Core
    'IntegratedVideoWorkflow',
    'IntegratedWorkflowStatus',
    'PluginWorkflowState',
    'IntegratedWorkflowHooks',
    'WorkflowConfiguration',
    'WorkflowStatistics',
    'HealthReport',
    
    # Components
    'IntegratedExtractor',
    'IntegratedSuggestionEngine',
    'IntegratedVideoGenerator',
    'ExtractorManager',
    'SuggestionEngineManager',
    'VideoGeneratorManager',
    
    # Utilities
    'create_integrated_workflow',
    'quick_video_generation',
    'batch_video_generation',
    'load_config_from_file',
    'save_config_to_file',
    'create_default_plugin_config',
    'create_default_workflow_config',
    'validate_workflow_state',
    'get_workflow_summary',
    'format_duration',
    'create_workflow_report'
] 