"""
Onyx Video Workflow

A comprehensive video generation workflow system using Onyx's infrastructure,
providing modular, extensible, and high-performance video generation capabilities.
"""

# Core components
from .core import (
    OnyxVideoStep,
    OnyxVideoContext,
    WorkflowExecutionResult,
    StepExecutionResult,
    WorkflowStatus,
    GeneratorStatus,
    OnyxVideoWorkflow
)

# Main generator
from .generator import OnyxVideoGenerator

# Workflow steps
from .steps import (
    get_default_workflow_steps,
    get_vision_workflow_steps,
    get_quick_workflow_steps,
    get_advanced_workflow_steps,
    get_workflow_steps_by_type
)

# Utility functions
from .utils import (
    initialize_onyx_video_system,
    generate_onyx_video,
    generate_onyx_video_with_vision,
    get_onyx_video_status,
    switch_workflow_type,
    get_available_workflow_types,
    cleanup_onyx_video_system,
    create_video_request,
    batch_generate_videos,
    get_generator_instance,
    health_check,
    get_system_statistics
)

__version__ = "1.0.0"
__author__ = "Onyx Team"

__all__ = [
    # Core components
    "OnyxVideoStep",
    "OnyxVideoContext",
    "WorkflowExecutionResult",
    "StepExecutionResult", 
    "WorkflowStatus",
    "GeneratorStatus",
    "OnyxVideoWorkflow",
    
    # Main generator
    "OnyxVideoGenerator",
    
    # Workflow steps
    "get_default_workflow_steps",
    "get_vision_workflow_steps",
    "get_quick_workflow_steps",
    "get_advanced_workflow_steps",
    "get_workflow_steps_by_type",
    
    # Utility functions
    "initialize_onyx_video_system",
    "generate_onyx_video",
    "generate_onyx_video_with_vision",
    "get_onyx_video_status",
    "switch_workflow_type",
    "get_available_workflow_types",
    "cleanup_onyx_video_system",
    "create_video_request",
    "batch_generate_videos",
    "get_generator_instance",
    "health_check",
    "get_system_statistics"
] 