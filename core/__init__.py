"""
Core Diffusion Models Package
==============================

Comprehensive diffusion models system with advanced features including:
- Modular dependency management
- Service lifecycle management
- Health monitoring
- Plugin system
- Metrics collection
- Dynamic configuration
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"
__license__ = "Proprietary"
__description__ = "Comprehensive diffusion models system with advanced features"

# Modular dependency management system - ONLY import working modules
try:
    from .dependency_structures import *
    from .service_lifecycle import *
    from .dependency_resolver import *
    from .health_monitor import *
    from .dependency_manager_modular import *
    from .plugin_manager import *
    from .metrics_collector import *
    from .dynamic_config import *
    MODULAR_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Modular system not fully available: {e}")
    MODULAR_SYSTEM_AVAILABLE = False

# Core systems - only import if they exist and work
try:
    from .config_manager import *
    from .logger_manager import *
    CORE_SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Core systems not fully available: {e}")
    CORE_SYSTEMS_AVAILABLE = False

# Optional imports - only if they exist
try:
    from .diffusion_models_system import *
except ImportError:
    pass

try:
    from .diffusion_processes_core import *
except ImportError:
    pass

try:
    from .diffusion_logging_system import *
except ImportError:
    pass

try:
    from .diffusion_performance_optimizer import *
except ImportError:
    pass

try:
    from .gradient_accumulation_system import *
except ImportError:
    pass

# Gradio interfaces - only if they exist
try:
    from .gradio_interactive_demos import *
except ImportError:
    pass

try:
    from .gradio_error_handling import *
except ImportError:
    pass

# User friendly interfaces - only if they exist
try:
    from .user_friendly_interfaces import *
except ImportError:
    pass

__all__ = [
    # Modular dependency management system
    "dependency_structures",
    "service_lifecycle", 
    "dependency_resolver",
    "health_monitor",
    "dependency_manager_modular",
    "plugin_manager",
    "metrics_collector",
    "dynamic_config",
    "MODULAR_SYSTEM_AVAILABLE",
    
    # Core systems
    "config_manager",
    "logger_manager",
    "CORE_SYSTEMS_AVAILABLE",
    
    # Optional systems (only if available)
    "diffusion_models_system",
    "diffusion_processes_core",
    "diffusion_logging_system",
    "diffusion_performance_optimizer",
    "gradient_accumulation_system",
    "gradio_interactive_demos",
    "gradio_error_handling",
    "user_friendly_interfaces",
]