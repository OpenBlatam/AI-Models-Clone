"""
Centralized file type validation utilities optimized for production.
"""

from enum import Enum
from typing import Set, Optional, Union, Dict, Any
from pathlib import Path
import mimetypes
import magic
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

# Production-optimized constants using frozenset for better performance
IMAGE_MIME_TYPES = frozenset([
    "image/png",
    "image/jpeg", 
    "image/jpg",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "image/avif",
    "image/heic",
    "image/heif"
])

# Vision LLM supported formats
VISION_LLM_SUPPORTED = frozenset([
    "image/png",
    "image/jpeg",
    "image/jpg", 
    "image/webp"
])

# Image types that should be excluded from processing
EXCLUDED_IMAGE_TYPES = frozenset([
    "image/svg+xml",  # Vector format, not suitable for vision processing
    "image/x-icon",   # Icons typically too small
    "image/vnd.microsoft.icon"
])

# File size limits (in bytes)
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB
MAX_VISION_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB for vision processing


class ImageFormat(Enum):
    """Enumeration of supported image formats."""
    PNG = "image/png"
    JPEG = "image/jpeg"
    JPG = "image/jpg" 
    WEBP = "image/webp"
    GIF = "image/gif"
    BMP = "image/bmp"
    TIFF = "image/tiff"
    AVIF = "image/avif"
    HEIC = "image/heic"
    HEIF = "image/heif"


class ValidationConfig(BaseModel):
    """Configuration for file validation."""
    max_file_size_mb: int = Field(default=100, ge=1, le=1000)
    max_vision_file_size_mb: int = Field(default=20, ge=1, le=100)
    allowed_formats: Set[str] = Field(default_factory=lambda: IMAGE_MIME_TYPES.copy())
    vision_formats: Set[str] = Field(default_factory=lambda: VISION_LLM_SUPPORTED.copy())
    excluded_formats: Set[str] = Field(default_factory=lambda: EXCLUDED_IMAGE_TYPES.copy())
    strict_validation: bool = Field(default=True)
    use_magic_bytes: bool = Field(default=True)

    @validator('max_vision_file_size_mb')
    def validate_vision_size(cls, v, values):
        max_size = values.get('max_file_size_mb', 100)
        if v > max_size:
            raise ValueError("Vision file size cannot exceed general max file size")
        return v


class ValidationResult(BaseModel):
    """Result of file validation."""
    is_valid: bool
    mime_type: Optional[str] = None
    detected_format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_size_mb: Optional[float] = None
    is_vision_compatible: bool = False
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR", details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


def detect_mime_type_advanced(file_data: bytes, filename: Optional[str] = None) -> Optional[str]:
    """
    Advanced MIME type detection using multiple methods.
    
    Args:
        file_data: Raw file bytes
        filename: Optional filename for extension-based detection
        
    Returns:
        str: Detected MIME type or None
    """
    detected_types = []
    
    try:
        # Method 1: Magic bytes detection (most reliable)
        mime_type = magic.from_buffer(file_data, mime=True)
        if mime_type and mime_type != 'application/octet-stream':
            detected_types.append(mime_type)
    except Exception as e:
        logger.debug(f"Magic bytes detection failed: {e}")
    
    # Method 2: File extension detection
    if filename:
        try:
            extension_type, _ = mimetypes.guess_type(filename)
            if extension_type:
                detected_types.append(extension_type)
        except Exception as e:
            logger.debug(f"Extension detection failed: {e}")
    
    # Method 3: Simple header signature detection
    try:
        if file_data.startswith(b'\x89PNG\r\n\x1a\n'):
            detected_types.append('image/png')
        elif file_data.startswith(b'\xff\xd8\xff'):
            detected_types.append('image/jpeg')
        elif file_data.startswith(b'RIFF') and b'WEBP' in file_data[:12]:
            detected_types.append('image/webp')
        elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):
            detected_types.append('image/gif')
    except Exception as e:
        logger.debug(f"Header signature detection failed: {e}")
    
    # Return most common detection or first valid one
    if detected_types:
        return max(set(detected_types), key=detected_types.count)
    
    return None


def is_valid_image_type(mime_type: str, config: Optional[ValidationConfig] = None) -> bool:
    """
    Check if mime_type is a valid image type with enhanced validation.

    Args:
        mime_type: The MIME type to check
        config: Validation configuration

    Returns:
        bool: True if the MIME type is a valid image type, False otherwise
    """
    if config is None:
        config = ValidationConfig()
    
    if not mime_type:
        return False
    
    # Normalize MIME type
    normalized_type = mime_type.lower().strip()
    
    # Check if excluded
    if normalized_type in config.excluded_formats:
        return False
    
    # Check if in allowed formats
    return normalized_type in config.allowed_formats


def is_supported_by_vision_llm(mime_type: str, config: Optional[ValidationConfig] = None) -> bool:
    """
    Check if this image type can be processed by vision LLMs.

    Args:
        mime_type: The MIME type to check
        config: Validation configuration

    Returns:
        bool: True if the MIME type is supported by vision LLMs, False otherwise
    """
    if config is None:
        config = ValidationConfig()
    
    if not mime_type:
        return False
    
    normalized_type = mime_type.lower().strip()
    return normalized_type in config.vision_formats


def validate_file_comprehensive(
    file_data: bytes,
    filename: Optional[str] = None,
    config: Optional[ValidationConfig] = None
) -> ValidationResult:
    """
    Comprehensive file validation with detailed results.
    
    Args:
        file_data: Raw file bytes
        filename: Optional filename
        config: Validation configuration
        
    Returns:
        ValidationResult: Detailed validation results
        
    Raises:
        FileValidationError: If validation fails critically
    """
    if config is None:
        config = ValidationConfig()
    
    result = ValidationResult(is_valid=False)
    
    try:
        # Basic checks
        if not file_data:
            result.errors.append("Empty file data")
            return result
        
        # File size validation
        file_size = len(file_data)
        result.file_size_bytes = file_size
        result.file_size_mb = file_size / (1024 * 1024)
        
        max_size_bytes = config.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            result.errors.append(f"File size {result.file_size_mb:.2f}MB exceeds limit {config.max_file_size_mb}MB")
            return result
        
        # MIME type detection
        if config.use_magic_bytes:
            detected_mime = detect_mime_type_advanced(file_data, filename)
        else:
            detected_mime = mimetypes.guess_type(filename)[0] if filename else None
        
        result.detected_format = detected_mime
        result.mime_type = detected_mime
        
        if not detected_mime:
            if config.strict_validation:
                result.errors.append("Could not detect MIME type")
                return result
            else:
                result.warnings.append("MIME type detection failed")
        
        # Image type validation
        if detected_mime and is_valid_image_type(detected_mime, config):
            result.is_valid = True
            
            # Vision LLM compatibility check
            if is_supported_by_vision_llm(detected_mime, config):
                vision_max_size = config.max_vision_file_size_mb * 1024 * 1024
                if file_size <= vision_max_size:
                    result.is_vision_compatible = True
                else:
                    result.warnings.append(f"File too large for vision processing (max {config.max_vision_file_size_mb}MB)")
            else:
                result.warnings.append("Format not supported by vision LLMs")
        else:
            result.errors.append(f"Invalid or unsupported image type: {detected_mime}")
        
        return result
        
    except Exception as e:
        logger.error(f"File validation failed: {e}")
        raise FileValidationError(f"Validation failed: {e}", "VALIDATION_ERROR", {"filename": filename})


def validate_image_batch(
    files: list[tuple[bytes, Optional[str]]],
    config: Optional[ValidationConfig] = None
) -> Dict[str, ValidationResult]:
    """
    Validate multiple files efficiently.
    
    Args:
        files: List of (file_data, filename) tuples
        config: Validation configuration
        
    Returns:
        Dict: Mapping of filenames to validation results
    """
    results = {}
    
    for i, (file_data, filename) in enumerate(files):
        file_key = filename or f"file_{i}"
        try:
            results[file_key] = validate_file_comprehensive(file_data, filename, config)
        except FileValidationError as e:
            results[file_key] = ValidationResult(
                is_valid=False,
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"Unexpected error validating {file_key}: {e}")
            results[file_key] = ValidationResult(
                is_valid=False,
                errors=[f"Unexpected error: {e}"]
            )
    
    return results


# Backward compatibility functions
def is_valid_image_type_legacy(mime_type: str) -> bool:
    """Legacy function for backward compatibility."""
    return is_valid_image_type(mime_type)


def is_supported_by_vision_llm_legacy(mime_type: str) -> bool:
    """Legacy function for backward compatibility."""
    return is_supported_by_vision_llm(mime_type)