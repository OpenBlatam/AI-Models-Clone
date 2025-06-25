import io
import json
import os
import re
import uuid
from typing import Any, NamedTuple, Sequence
from pathlib import Path

# Optimized constants for production
IMAGE_MEDIA_TYPES = frozenset([
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff"
])

MAX_IMAGE_SIZE_MB = 50
SUPPORTED_FORMATS = frozenset(['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff'])


class ExtractionResult(NamedTuple):
    """Structured result from text and image extraction from various file types."""

    text_content: str
    embedded_images: Sequence[tuple[bytes, str]]
    metadata: dict[str, Any]


class ImageExtractionError(Exception):
    """Custom exception for image extraction errors."""
    pass


def is_valid_image_file(file_path: str | Path) -> bool:
    """
    Validate if a file is a supported image format.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        bool: True if valid image format
        
    Raises:
        ImageExtractionError: If file validation fails
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False
            
        suffix = path.suffix.lower().lstrip('.')
        return suffix in SUPPORTED_FORMATS
    except Exception as e:
        raise ImageExtractionError(f"File validation failed: {e}")


def get_file_size_mb(file_path: str | Path) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: File size in MB
    """
    try:
        return Path(file_path).stat().st_size / (1024 * 1024)
    except Exception:
        return 0.0


def validate_image_size(file_path: str | Path, max_size_mb: int = MAX_IMAGE_SIZE_MB) -> bool:
    """
    Validate image file size.
    
    Args:
        file_path: Path to the image file
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        bool: True if size is within limits
    """
    return get_file_size_mb(file_path) <= max_size_mb
