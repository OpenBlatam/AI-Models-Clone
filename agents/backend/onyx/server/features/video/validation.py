"""
Centralized file type validation utilities for video/image processing.
"""
IMAGE_MIME_TYPES = [
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
]
EXCLUDED_IMAGE_TYPES = [
    "image/bmp",
    "image/tiff",
    "image/gif",
    "image/svg+xml",
    "image/avif",
]
def is_valid_image_type(mime_type: str) -> bool:
    """Check if mime_type is a valid image type."""
    if not mime_type:
        return False
    return mime_type.startswith("image/") and mime_type not in EXCLUDED_IMAGE_TYPES
def is_supported_by_vision_llm(mime_type: str) -> bool:
    """Check if this image type can be processed by vision LLMs."""
    return mime_type in IMAGE_MIME_TYPES 