"""
Image Processing Module - Production optimized implementation.

Provides comprehensive image processing capabilities including validation,
extraction, resizing, and format conversion optimized for production use.
"""

import logging
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# Module version
__version__ = "1.0.0"

# Import core components
try:
    from .validation import (
        ValidationConfig,
        ValidationResult,
        ImageFormat,
        FileValidationError,
        validate_file_comprehensive,
        validate_image_batch,
        is_valid_image_type,
        is_supported_by_vision_llm,
        detect_mime_type_advanced
    )
    
    from .extract import (
        ExtractionResult,
        ImageExtractionError,
        is_valid_image_file,
        get_file_size_mb,
        validate_image_size
    )
    
    try:
        from .image_sumary import (
            ImageProcessingConfig,
            ImageProcessingError,
            process_image_async,
            resize_image_if_needed
        )
        IMAGE_SUMMARY_AVAILABLE = True
    except ImportError:
        logger.warning("Image summary module not available")
        IMAGE_SUMMARY_AVAILABLE = False
    
    try:
        from .image_utils import (
            FileStorageConfig,
            StorageResult,
            FileStorageError,
            store_image_and_create_section,
            store_image_async,
            get_storage_stats
        )
        IMAGE_UTILS_AVAILABLE = True
    except ImportError:
        logger.warning("Image utils module not available")
        IMAGE_UTILS_AVAILABLE = False
    
    VALIDATION_AVAILABLE = True
    EXTRACTION_AVAILABLE = True
    
except ImportError as e:
    logger.error(f"Failed to import core image processing components: {e}")
    VALIDATION_AVAILABLE = False
    EXTRACTION_AVAILABLE = False
    IMAGE_SUMMARY_AVAILABLE = False
    IMAGE_UTILS_AVAILABLE = False

# Export components
__all__ = [
    # Core validation
    "ValidationConfig",
    "ValidationResult", 
    "ImageFormat",
    "FileValidationError",
    "validate_file_comprehensive",
    "validate_image_batch",
    "is_valid_image_type",
    "is_supported_by_vision_llm",
    "detect_mime_type_advanced",
    
    # Extraction
    "ExtractionResult",
    "ImageExtractionError",
    "is_valid_image_file",
    "get_file_size_mb",
    "validate_image_size",
    
    # Image processing (if available)
    "ImageProcessingConfig",
    "ImageProcessingError", 
    "process_image_async",
    "resize_image_if_needed",
    
    # Storage utilities (if available)
    "FileStorageConfig",
    "StorageResult",
    "FileStorageError",
    "store_image_and_create_section",
    "store_image_async",
    "get_storage_stats",
    
    # Availability flags
    "VALIDATION_AVAILABLE",
    "EXTRACTION_AVAILABLE",
    "IMAGE_SUMMARY_AVAILABLE", 
    "IMAGE_UTILS_AVAILABLE",
    
    # Factory functions
    "create_default_config",
    "get_module_status"
]


def create_default_config() -> Dict[str, Any]:
    """
    Create default configuration for image processing.
    
    Returns:
        Dict: Default configuration
    """
    config = {
        "validation": {
            "max_file_size_mb": 100,
            "max_vision_file_size_mb": 20,
            "strict_validation": True,
            "use_magic_bytes": True
        },
        "processing": {
            "max_dimension": 1024,
            "jpeg_quality": 85,
            "webp_quality": 80,
            "enable_optimization": True
        },
        "storage": {
            "max_file_size_mb": 100,
            "storage_timeout": 30,
            "enable_compression": True,
            "enable_encryption": False
        }
    }
    
    return config


def get_module_status() -> Dict[str, Any]:
    """
    Get the status of image processing module.
    
    Returns:
        Dict: Module status information
    """
    return {
        "version": __version__,
        "validation_available": VALIDATION_AVAILABLE,
        "extraction_available": EXTRACTION_AVAILABLE,
        "image_summary_available": IMAGE_SUMMARY_AVAILABLE,
        "image_utils_available": IMAGE_UTILS_AVAILABLE,
        "overall_health": all([
            VALIDATION_AVAILABLE,
            EXTRACTION_AVAILABLE
        ])
    }


# Initialize module
logger.info(f"Image Processing Module v{__version__} initialized")
logger.info(f"Validation: {'✓' if VALIDATION_AVAILABLE else '✗'}")
logger.info(f"Extraction: {'✓' if EXTRACTION_AVAILABLE else '✗'}")
logger.info(f"Summary: {'✓' if IMAGE_SUMMARY_AVAILABLE else '✗'}")
logger.info(f"Utils: {'✓' if IMAGE_UTILS_AVAILABLE else '✗'}")
