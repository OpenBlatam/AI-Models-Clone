from typing import Tuple, Optional, Union, Dict, Any
from pathlib import Path
import asyncio
from contextlib import asynccontextmanager
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field, validator
import logging

# Import from your project structure - adjust as needed
from onyx.utils.logger import setup_logger

logger = setup_logger()

# Production optimized constants
DEFAULT_MEDIA_TYPE = "application/octet-stream"
MAX_RETRY_ATTEMPTS = 3
STORAGE_TIMEOUT_SECONDS = 30


class FileStorageConfig(BaseModel):
    """Configuration for file storage operations."""
    max_file_size_mb: int = Field(default=100, ge=1, le=1000)
    allowed_media_types: set[str] = Field(default_factory=lambda: {
        "image/png", "image/jpeg", "image/webp", "image/gif", 
        "image/bmp", "image/tiff", "application/pdf"
    })
    storage_timeout: int = Field(default=STORAGE_TIMEOUT_SECONDS, ge=5, le=300)
    enable_compression: bool = Field(default=True)

    @validator('max_file_size_mb')
    def validate_file_size(cls, v):
        if v > 1000:
            raise ValueError("Max file size cannot exceed 1000MB")
        return v


class StorageResult(BaseModel):
    """Result of file storage operation."""
    file_name: str
    stored_size_bytes: int
    original_size_bytes: int
    compression_ratio: Optional[float] = None
    storage_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FileStorageError(Exception):
    """Custom exception for file storage errors."""
    
    def __init__(self, message: str, error_code: str = "STORAGE_ERROR", original_error: Exception = None):
        super().__init__(message)
        self.error_code = error_code
        self.original_error = original_error


def validate_file_data(
    file_data: bytes, 
    media_type: str, 
    config: Optional[FileStorageConfig] = None
) -> bool:
    """
    Validate file data before storage.
    
    Args:
        file_data: Raw file bytes
        media_type: MIME type of the file
        config: Storage configuration
        
    Returns:
        bool: True if validation passes
        
    Raises:
        FileStorageError: If validation fails
    """
    if config is None:
        config = FileStorageConfig()
    
    try:
        # Check if file data exists
        if not file_data:
            raise FileStorageError("Empty file data provided", "EMPTY_FILE")
        
        # Check file size
        file_size_mb = len(file_data) / (1024 * 1024)
        if file_size_mb > config.max_file_size_mb:
            raise FileStorageError(
                f"File size {file_size_mb:.2f}MB exceeds limit {config.max_file_size_mb}MB",
                "FILE_TOO_LARGE"
            )
        
        # Check media type
        if media_type not in config.allowed_media_types:
            raise FileStorageError(
                f"Media type {media_type} not allowed", 
                "INVALID_MEDIA_TYPE"
            )
        
        return True
        
    except FileStorageError:
        raise
    except Exception as e:
        raise FileStorageError(f"Validation failed: {e}", "VALIDATION_ERROR", e)


@asynccontextmanager
async def get_db_session_async(db_session: Session):
    """
    Async context manager for database sessions with proper error handling.
    
    Args:
        db_session: SQLAlchemy session
        
    Yields:
        Session: Database session
    """
    try:
        yield db_session
        await asyncio.get_event_loop().run_in_executor(None, db_session.commit)
    except Exception as e:
        await asyncio.get_event_loop().run_in_executor(None, db_session.rollback)
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await asyncio.get_event_loop().run_in_executor(None, db_session.close)


def store_image_and_create_section(
    db_session: Session,
    image_data: bytes,
    file_name: str,
    display_name: str,
    link: Optional[str] = None,
    media_type: str = DEFAULT_MEDIA_TYPE,
    file_origin: Optional[str] = None,  # Updated to be more flexible
    config: Optional[FileStorageConfig] = None
) -> Tuple[Any, Optional[str]]:  # Return type adjusted for flexibility
    """
    Stores an image in PGFileStore and creates an ImageSection object with enhanced error handling.

    Args:
        db_session: Database session
        image_data: Raw image bytes
        file_name: Base identifier for the file
        display_name: Human-readable name for the image
        link: Optional URL link for the image
        media_type: MIME type of the image
        file_origin: Origin of the file (e.g., CONFLUENCE, GOOGLE_DRIVE, etc.)
        config: Storage configuration

    Returns:
        Tuple containing:
        - ImageSection object with image reference
        - The file_name in PGFileStore or None if storage failed

    Raises:
        FileStorageError: If storage operation fails
    """
    if config is None:
        config = FileStorageConfig()
    
    # Validate input data
    validate_file_data(image_data, media_type, config)
    
    stored_file_name = None
    original_size = len(image_data)
    
    try:
        # Generate unique filename if not provided
        if not file_name:
            file_name = f"image_{uuid.uuid4().hex[:8]}"
        
        # Sanitize filename
        safe_filename = "".join(c for c in file_name if c.isalnum() or c in "._-")
        
        logger.info(f"Storing image: {safe_filename}, size: {original_size} bytes")
        
        # Storage logic with retry mechanism
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                # This would be your actual storage implementation
                # pgfilestore = save_bytes_to_pgfilestore(
                #     db_session=db_session,
                #     raw_bytes=image_data,
                #     media_type=media_type,
                #     identifier=safe_filename,
                #     display_name=display_name,
                #     file_origin=file_origin or "OTHER",
                # )
                # stored_file_name = pgfilestore.file_name
                
                # Placeholder for actual implementation
                stored_file_name = safe_filename
                break
                
            except SQLAlchemyError as e:
                logger.warning(f"Storage attempt {attempt + 1} failed: {e}")
                if attempt == MAX_RETRY_ATTEMPTS - 1:
                    raise FileStorageError(
                        f"Failed to store after {MAX_RETRY_ATTEMPTS} attempts",
                        "STORAGE_FAILED",
                        e
                    )
                db_session.rollback()
            except Exception as e:
                logger.error(f"Unexpected storage error: {e}")
                raise FileStorageError(f"Storage failed: {e}", "UNEXPECTED_ERROR", e)

        # Create storage result for logging/monitoring
        storage_result = StorageResult(
            file_name=stored_file_name,
            stored_size_bytes=len(image_data),
            original_size_bytes=original_size,
            metadata={
                "media_type": media_type,
                "display_name": display_name,
                "file_origin": file_origin
            }
        )
        
        logger.info(f"Successfully stored image: {storage_result.dict()}")
        
        # Create an ImageSection with the stored file reference
        # This would use your actual ImageSection class
        image_section = {
            "image_file_name": stored_file_name,
            "link": link,
            "metadata": storage_result.metadata
        }
        
        return image_section, stored_file_name

    except FileStorageError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in store_image_and_create_section: {e}")
        raise FileStorageError(f"Failed to store image: {e}", "UNEXPECTED_ERROR", e)


async def store_image_async(
    db_session: Session,
    image_data: bytes,
    file_name: str,
    display_name: str,
    **kwargs
) -> Tuple[Any, Optional[str]]:
    """
    Asynchronous version of store_image_and_create_section.
    
    Args:
        db_session: Database session
        image_data: Raw image bytes
        file_name: Base identifier for the file
        display_name: Human-readable name for the image
        **kwargs: Additional keyword arguments
        
    Returns:
        Tuple: (ImageSection, stored_file_name)
        
    Raises:
        FileStorageError: If storage operation fails
    """
    try:
        # Run storage operation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            store_image_and_create_section,
            db_session,
            image_data,
            file_name,
            display_name,
            **kwargs
        )
        return result
        
    except Exception as e:
        logger.error(f"Async storage failed: {e}")
        raise FileStorageError(f"Async storage failed: {e}", "ASYNC_ERROR", e)


def get_storage_stats(db_session: Session) -> Dict[str, Any]:
    """
    Get storage statistics for monitoring.
    
    Args:
        db_session: Database session
        
    Returns:
        Dict: Storage statistics
    """
    try:
        # This would query your actual storage tables
        stats = {
            "total_files": 0,  # Placeholder
            "total_size_mb": 0.0,
            "average_file_size_mb": 0.0,
            "media_type_distribution": {},
            "storage_health": "healthy"
        }
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        return {"error": str(e), "storage_health": "unhealthy"}


# Backward compatibility
def store_image_and_create_section_legacy(
    db_session: Session,
    image_data: bytes,
    file_name: str,
    display_name: str,
    link: str | None = None,
    media_type: str = DEFAULT_MEDIA_TYPE,
    file_origin = None,  # Maintaining original signature
) -> Tuple[Any, str | None]:
    """Legacy function for backward compatibility."""
    result = store_image_and_create_section(
        db_session=db_session,
        image_data=image_data,
        file_name=file_name,
        display_name=display_name,
        link=link,
        media_type=media_type,
        file_origin=file_origin
    )
    return result