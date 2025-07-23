"""
Onyx AI Video System - CLI Module

Command-line interface module for the Onyx AI Video system.
"""

from .cli import OnyxAIVideoCLI
from .commands import (
    start_system, show_status, show_metrics, handle_config,
    generate_video, handle_plugins, run_tests, health_check
)
from .display import (
    show_startup_info, print_status_table, print_metrics_table,
    print_config_table, print_plugins_table, print_plugin_status_table
)
from .parser import create_parser

__all__ = [
    # Main CLI class
    "OnyxAIVideoCLI",
    
    # Commands
    "start_system",
    "show_status", 
    "show_metrics",
    "handle_config",
    "generate_video",
    "handle_plugins",
    "run_tests",
    "health_check",
    
    # Display functions
    "show_startup_info",
    "print_status_table",
    "print_metrics_table", 
    "print_config_table",
    "print_plugins_table",
    "print_plugin_status_table",
    
    # Parser
    "create_parser"
] 