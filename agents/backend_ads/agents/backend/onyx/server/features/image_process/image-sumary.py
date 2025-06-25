import base64
import asyncio
from io import BytesIO
from typing import Optional, Union
from pathlib import Path

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from PIL import Image, ImageOps
from pydantic import BaseModel, Field, validator
import logging

# Configure logging for production
logger = logging.getLogger(__name__)

# Production optimized constants
MAX_IMAGE_SIZE_MB = 20
OPTIMAL_MAX_DIMENSION = 1024
JPEG_QUALITY = 85
WEBP_QUALITY = 80


class ImageProcessingConfig(BaseModel):
    """Configuration for image processing operations."""
    max_size_mb: int = Field(default=MAX_IMAGE_SIZE_MB, ge=1, le=100)
    max_dimension: int = Field(default=OPTIMAL_MAX_DIMENSION, ge=256, le=4096)
    jpeg_quality: int = Field(default=JPEG_QUALITY, ge=1, le=100)
    webp_quality: int = Field(default=WEBP_QUALITY, ge=1, le=100)

    @validator('max_size_mb')
    def validate_max_size(cls, v):
        if v > 100:
            raise ValueError("Max size cannot exceed 100MB")
        return v


class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass


def _encode_image_for_llm_prompt(image_data: bytes, format_type: str = "jpeg") -> str:
    """
    Encode image data to base64 string optimized for LLM prompts.
    
    Args:
        image_data: Raw image bytes
        format_type: Output format (jpeg, png, webp)
        
    Returns:
        str: Base64 encoded data URI
        
    Raises:
        ImageProcessingError: If encoding fails
    """
    try:
        if not image_data:
            raise ImageProcessingError("Empty image data provided")
            
        base64_encoded_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:image/{format_type};base64,{base64_encoded_data}"
        
    except Exception as e:
        logger.error(f"Failed to encode image for LLM: {e}")
        raise ImageProcessingError(f"Image encoding failed: {e}")


def _optimize_image_format(image: Image.Image, target_format: str = "JPEG") -> Image.Image:
    """
    Optimize image format and settings for better compression.
    
    Args:
        image: PIL Image object
        target_format: Target format (JPEG, PNG, WEBP)
        
    Returns:
        Image.Image: Optimized image
    """
    try:
        # Convert RGBA to RGB for JPEG
        if target_format == "JPEG" and image.mode in ("RGBA", "P"):
            # Create white background for transparent images
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background
            
        # Auto-orient image using EXIF data
        image = ImageOps.exif_transpose(image)
        
        return image
        
    except Exception as e:
        logger.warning(f"Image optimization failed, using original: {e}")
        return image


def _resize_image_if_needed(
    image_data: bytes, 
    config: Optional[ImageProcessingConfig] = None
) -> bytes:
    """
    Resize image if it's larger than the specified max size, using optimized compression.
    
    Args:
        image_data: Raw image bytes
        config: Configuration object with processing parameters
        
    Returns:
        bytes: Processed image data
        
    Raises:
        ImageProcessingError: If image processing fails
    """
    if config is None:
        config = ImageProcessingConfig()
    
    try:
        max_size_bytes = config.max_size_mb * 1024 * 1024
        
        # If already under size limit, return as-is
        if len(image_data) <= max_size_bytes:
            return image_data
            
        with Image.open(BytesIO(image_data)) as img:
            # Optimize the image format first
            img = _optimize_image_format(img)
            
            # Calculate optimal dimensions maintaining aspect ratio
            original_width, original_height = img.size
            if max(original_width, original_height) > config.max_dimension:
                img.thumbnail((config.max_dimension, config.max_dimension), Image.Resampling.LANCZOS)
            
            # Try different compression strategies
            output = BytesIO()
            
            # First try WebP for better compression
            try:
                img.save(output, format="WEBP", quality=config.webp_quality, optimize=True)
                compressed_data = output.getvalue()
                
                if len(compressed_data) <= max_size_bytes:
                    return compressed_data
            except Exception:
                logger.debug("WebP compression failed, falling back to JPEG")
            
            # Fallback to JPEG with progressive compression
            output = BytesIO()
            img.save(
                output, 
                format="JPEG", 
                quality=config.jpeg_quality, 
                optimize=True,
                progressive=True
            )
            compressed_data = output.getvalue()
            
            # If still too large, reduce quality further
            if len(compressed_data) > max_size_bytes:
                for quality in range(config.jpeg_quality - 10, 20, -10):
                    output = BytesIO()
                    img.save(output, format="JPEG", quality=quality, optimize=True)
                    compressed_data = output.getvalue()
                    
                    if len(compressed_data) <= max_size_bytes:
                        break
            
            logger.info(f"Image compressed from {len(image_data)} to {len(compressed_data)} bytes")
            return compressed_data
            
    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        raise ImageProcessingError(f"Failed to resize image: {e}")


async def process_image_async(
    image_data: bytes, 
    config: Optional[ImageProcessingConfig] = None
) -> tuple[bytes, str]:
    """
    Asynchronously process image data for optimal LLM usage.
    
    Args:
        image_data: Raw image bytes
        config: Processing configuration
        
    Returns:
        tuple: (processed_image_data, base64_encoded_string)
        
    Raises:
        ImageProcessingError: If processing fails
    """
    try:
        # Run CPU-intensive operations in thread pool
        loop = asyncio.get_event_loop()
        
        # Resize in thread pool to avoid blocking
        processed_data = await loop.run_in_executor(
            None, _resize_image_if_needed, image_data, config
        )
        
        # Encode in thread pool
        encoded_string = await loop.run_in_executor(
            None, _encode_image_for_llm_prompt, processed_data
        )
        
        return processed_data, encoded_string
        
    except Exception as e:
        logger.error(f"Async image processing failed: {e}")
        raise ImageProcessingError(f"Async processing failed: {e}")


# Maintain backward compatibility
def resize_image_if_needed(image_data: bytes, max_size_mb: int = MAX_IMAGE_SIZE_MB) -> bytes:
    """Legacy function for backward compatibility."""
    config = ImageProcessingConfig(max_size_mb=max_size_mb)
    return _resize_image_if_needed(image_data, config)


def validate_image_data(image_data: bytes) -> bool:
    """
    Validate that the provided data is a valid image.
    
    Args:
        image_data: Raw image bytes to validate
        
    Returns:
        bool: True if valid image data
    """
    try:
        if not image_data or len(image_data) == 0:
            return False
            
        with Image.open(BytesIO(image_data)) as img:
            # Try to load the image to verify it's valid
            img.load()
            return img.format in {'JPEG', 'PNG', 'WEBP', 'HEIF', 'AVIF'}
            
    except Exception:
        return False


def get_image_metadata(image_data: bytes) -> dict:
    """
    Extract metadata from image data.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        dict: Image metadata including format, size, etc.
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                'file_size_bytes': len(image_data),
                'file_size_mb': len(image_data) / (1024 * 1024)
            }
    except Exception:
        return {}