"""
Onyx Features Module - Production optimized implementation.

This module provides optimized services for image processing and key messages
with enterprise-grade performance, monitoring, and error handling.
"""

from typing import Optional
import logging
from pathlib import Path

# Configure module-level logging
logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"
__author__ = "Onyx Development Team"

# Module imports for easier access
try:
    from .image_process.validation import (
        ValidationConfig,
        ValidationResult,
        validate_file_comprehensive,
        is_valid_image_type,
        is_supported_by_vision_llm
    )
    from .image_process.extract import (
        ExtractionResult,
        ImageExtractionError,
        is_valid_image_file
    )
    from .image_process import *
    
    from .key_messages.service import (
        KeyMessageService,
        KeyMessage,
        MessageType,
        MessagePriority,
        create_key_message_service
    )
    
    # Import optimization modules
    from .optimization import (
        FastSerializer, FastHasher, VectorizedProcessor,
        AsyncOptimizer, MemoryOptimizer, ProfilerOptimizer,
        optimize_performance, OPTIMIZATION_CONFIG
    )
    
    from .performance_optimizers import (
        PerformanceOrchestrator, OptimizationConfig,
        create_performance_orchestrator, ultra_optimize
    )
    
    from .data_processing import (
        HighPerformanceDataProcessor, ProcessingConfig,
        create_data_processor, process_json_data_fast
    )
    
    IMAGE_PROCESSING_AVAILABLE = True
    KEY_MESSAGES_AVAILABLE = True
    OPTIMIZATION_AVAILABLE = True
    
except ImportError as e:
    logger.warning(f"Some features may not be available: {e}")
    IMAGE_PROCESSING_AVAILABLE = False
    KEY_MESSAGES_AVAILABLE = False
    OPTIMIZATION_AVAILABLE = False

# Export main components
__all__ = [
    # Version info
    "__version__",
    "__author__",
    
    # Availability flags
    "IMAGE_PROCESSING_AVAILABLE",
    "KEY_MESSAGES_AVAILABLE",
    "OPTIMIZATION_AVAILABLE",
    
    # Image processing
    "ValidationConfig",
    "ValidationResult", 
    "validate_file_comprehensive",
    "is_valid_image_type",
    "is_supported_by_vision_llm",
    "ExtractionResult",
    "ImageExtractionError",
    "is_valid_image_file",
    
    # Key messages
    "KeyMessageService",
    "KeyMessage",
    "MessageType",
    "MessagePriority", 
    "create_key_message_service",
    
    # Optimization components
    "FastSerializer",
    "FastHasher",
    "VectorizedProcessor",
    "AsyncOptimizer",
    "MemoryOptimizer",
    "ProfilerOptimizer",
    "optimize_performance",
    "OPTIMIZATION_CONFIG",
    
    # Performance optimizers
    "PerformanceOrchestrator",
    "OptimizationConfig",
    "create_performance_orchestrator",
    "ultra_optimize",
    
    # Data processing
    "HighPerformanceDataProcessor",
    "ProcessingConfig",
    "create_data_processor",
    "process_json_data_fast",
    
    # Factory functions
    "create_features_config",
    "get_feature_status"
]


def create_features_config() -> dict:
    """
    Create default configuration for all features.
    
    Returns:
        dict: Default configuration
    """
    return {
        "image_processing": {
            "max_file_size_mb": 100,
            "max_vision_file_size_mb": 20,
            "strict_validation": True,
            "use_magic_bytes": True
        },
        "key_messages": {
            "max_message_length": 10000,
            "max_messages_per_batch": 100,
            "cache_ttl": 3600,
            "enable_compression": True
        },
        "optimization": {
            "enable_jit": True,
            "enable_vectorization": True,
            "enable_gpu": False,
            "max_workers": 4,
            "compression_algorithm": "lz4",
            "serialization_format": "msgpack"
        },
        "general": {
            "log_level": "INFO",
            "enable_monitoring": True,
            "enable_caching": True
        }
    }


def get_feature_status() -> dict:
    """
    Get the status of all features.
    
    Returns:
        dict: Feature availability status
    """
    return {
        "image_processing": IMAGE_PROCESSING_AVAILABLE,
        "key_messages": KEY_MESSAGES_AVAILABLE,
        "optimization": OPTIMIZATION_AVAILABLE,
        "version": __version__,
        "module_path": str(Path(__file__).parent),
        "performance_features": {
            "jit_compilation": OPTIMIZATION_AVAILABLE,
            "vectorized_processing": OPTIMIZATION_AVAILABLE,
            "async_optimization": OPTIMIZATION_AVAILABLE,
            "memory_optimization": OPTIMIZATION_AVAILABLE,
            "data_processing": OPTIMIZATION_AVAILABLE
        }
    }


# Initialize module
logger.info(f"Onyx Features Module v{__version__} initialized")
logger.info(f"Image Processing: {'✓' if IMAGE_PROCESSING_AVAILABLE else '✗'}")
logger.info(f"Key Messages: {'✓' if KEY_MESSAGES_AVAILABLE else '✗'}")
logger.info(f"Optimization: {'✓' if OPTIMIZATION_AVAILABLE else '✗'}") 