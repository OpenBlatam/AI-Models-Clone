"""
AI Video System - Utilities

Production-ready utility functions for the AI Video System.
"""

import os
import re
import hashlib
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urlparse, urljoin
import asyncio
import time
from datetime import datetime, timedelta

from .exceptions import ValidationError, StorageError
from .constants import VALIDATION_RULES, MAX_FILE_SIZE, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


# URL validation and processing
def validate_url(url: str) -> bool:
    """
    Validate URL format and security.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string", field="url", value=url)
    
    if len(url) > VALIDATION_RULES["url"]["max_length"]:
        raise ValidationError(
            f"URL too long (max {VALIDATION_RULES['url']['max_length']} characters)",
            field="url",
            value=url
        )
    
    try:
        parsed = urlparse(url)
        
        # Check required fields
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("URL must have scheme and netloc", field="url", value=url)
        
        # Check allowed schemes
        if parsed.scheme not in VALIDATION_RULES["url"]["allowed_schemes"]:
            raise ValidationError(
                f"URL scheme must be one of {VALIDATION_RULES['url']['allowed_schemes']}",
                field="url",
                value=url
            )
        
        return True
        
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}", field="url", value=url)


def sanitize_url(url: str) -> str:
    """
    Sanitize URL for safe use.
    
    Args:
        url: URL to sanitize
        
    Returns:
        str: Sanitized URL
    """
    # Remove whitespace
    url = url.strip()
    
    # Ensure proper scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        str: Domain name
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return "unknown"


# File and path utilities
def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system use.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove forbidden characters
    for char in VALIDATION_RULES["filename"]["forbidden_chars"]:
        filename = filename.replace(char, "_")
    
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    
    # Limit length
    if len(filename) > VALIDATION_RULES["filename"]["max_length"]:
        name, ext = os.path.splitext(filename)
        max_name_length = VALIDATION_RULES["filename"]["max_length"] - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename


def safe_filename(filename: str) -> str:
    """
    Alias for sanitize_filename for backward compatibility.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    return sanitize_filename(filename)


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get file extension from file path.
    
    Args:
        file_path: Path to file
        
    Returns:
        str: File extension (including dot)
    """
    path = Path(file_path)
    return path.suffix.lower()


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        int: File size in bytes
        
    Raises:
        StorageError: If file doesn't exist or can't be accessed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise StorageError(f"File does not exist: {file_path}", storage_path=str(path))
        
        return path.stat().st_size
        
    except Exception as e:
        if isinstance(e, StorageError):
            raise
        raise StorageError(f"Error getting file size: {e}", storage_path=str(file_path))


def validate_file_size(file_path: Union[str, Path], max_size: Optional[int] = None) -> bool:
    """
    Validate file size.
    
    Args:
        file_path: Path to file
        max_size: Maximum allowed size (defaults to MAX_FILE_SIZE)
        
    Returns:
        bool: True if file size is valid
        
    Raises:
        ValidationError: If file is too large
    """
    max_size = max_size or MAX_FILE_SIZE
    file_size = get_file_size(file_path)
    
    if file_size > max_size:
        raise ValidationError(
            f"File too large ({file_size} bytes, max {max_size} bytes)",
            field="file_size",
            value=file_size
        )
    
    return True


def create_temp_file(prefix: str = "ai_video_", suffix: str = ".tmp") -> Path:
    """
    Create a temporary file.
    
    Args:
        prefix: File prefix
        suffix: File suffix
        
    Returns:
        Path: Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(
        prefix=prefix,
        suffix=suffix,
        delete=False
    )
    temp_file.close()
    return Path(temp_file.name)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path: Path object for directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def cleanup_old_files(directory: Union[str, Path], max_age_days: int = 7) -> int:
    """
    Clean up old files in directory.
    
    Args:
        directory: Directory to clean
        max_age_days: Maximum age in days
        
    Returns:
        int: Number of files cleaned up
    """
    directory = Path(directory)
    if not directory.exists():
        return 0
    
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    cleaned_count = 0
    
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to clean up file {file_path}: {e}")
    
    return cleaned_count


# ID and hash utilities
def generate_workflow_id() -> str:
    """
    Generate unique workflow ID.
    
    Returns:
        str: Unique workflow ID
    """
    timestamp = int(time.time() * 1000)
    random_part = os.urandom(4).hex()
    return f"wf_{timestamp}_{random_part}"


def generate_video_id() -> str:
    """
    Generate unique video ID.
    
    Returns:
        str: Unique video ID
    """
    timestamp = int(time.time() * 1000)
    random_part = os.urandom(4).hex()
    return f"vid_{timestamp}_{random_part}"


def hash_content(content: str) -> str:
    """
    Generate hash for content.
    
    Args:
        content: Content to hash
        
    Returns:
        str: SHA-256 hash
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def hash_url(url: str) -> str:
    """
    Generate hash for URL.
    
    Args:
        url: URL to hash
        
    Returns:
        str: SHA-256 hash
    """
    return hash_content(url)


# Validation utilities
def validate_workflow_id(workflow_id: str) -> bool:
    """
    Validate workflow ID format.
    
    Args:
        workflow_id: Workflow ID to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If workflow ID is invalid
    """
    if not workflow_id or not isinstance(workflow_id, str):
        raise ValidationError("Workflow ID must be a non-empty string", field="workflow_id", value=workflow_id)
    
    if len(workflow_id) > VALIDATION_RULES["workflow_id"]["max_length"]:
        raise ValidationError(
            f"Workflow ID too long (max {VALIDATION_RULES['workflow_id']['max_length']} characters)",
            field="workflow_id",
            value=workflow_id
        )
    
    if not re.match(VALIDATION_RULES["workflow_id"]["pattern"], workflow_id):
        raise ValidationError(
            "Workflow ID contains invalid characters",
            field="workflow_id",
            value=workflow_id
        )
    
    return True


def validate_plugin_name(plugin_name: str) -> bool:
    """
    Validate plugin name format.
    
    Args:
        plugin_name: Plugin name to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If plugin name is invalid
    """
    if not plugin_name or not isinstance(plugin_name, str):
        raise ValidationError("Plugin name must be a non-empty string", field="plugin_name", value=plugin_name)
    
    if len(plugin_name) > VALIDATION_RULES["plugin_name"]["max_length"]:
        raise ValidationError(
            f"Plugin name too long (max {VALIDATION_RULES['plugin_name']['max_length']} characters)",
            field="plugin_name",
            value=plugin_name
        )
    
    if not re.match(VALIDATION_RULES["plugin_name"]["pattern"], plugin_name):
        raise ValidationError(
            "Plugin name contains invalid characters",
            field="plugin_name",
            value=plugin_name
        )
    
    return True


# Time and duration utilities
def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def parse_duration(duration_str: str) -> float:
    """
    Parse duration string to seconds.
    
    Args:
        duration_str: Duration string (e.g., "30s", "2.5m", "1h")
        
    Returns:
        float: Duration in seconds
    """
    duration_str = duration_str.lower().strip()
    
    if duration_str.endswith('s'):
        return float(duration_str[:-1])
    elif duration_str.endswith('m'):
        return float(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        return float(duration_str[:-1]) * 3600
    else:
        return float(duration_str)


# Async utilities
async def with_timeout(coro, timeout: float = DEFAULT_TIMEOUT):
    """
    Execute coroutine with timeout.
    
    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        
    Returns:
        Result of coroutine
        
    Raises:
        asyncio.TimeoutError: If timeout is exceeded
    """
    return await asyncio.wait_for(coro, timeout=timeout)


async def retry_async(
    func,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        backoff: Backoff multiplier
        exceptions: Exceptions to catch and retry
        
    Returns:
        Result of function
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                wait_time = delay * (backoff ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
    
    raise last_exception


# Configuration utilities
def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge configuration dictionaries recursively.
    
    Args:
        base_config: Base configuration
        override_config: Configuration to override with
        
    Returns:
        Dict[str, Any]: Merged configuration
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dict[str, Any]: Configuration from environment
    """
    config = {}
    
    # Map environment variables to config structure
    env_mappings = {
        "AI_VIDEO_LOG_LEVEL": ("monitoring", "log_level"),
        "AI_VIDEO_ENVIRONMENT": ("environment",),
        "AI_VIDEO_DEBUG": ("debug",),
        "AI_VIDEO_STORAGE_PATH": ("storage", "local_storage_path"),
        "AI_VIDEO_TEMP_DIR": ("storage", "temp_directory"),
        "AI_VIDEO_OUTPUT_DIR": ("storage", "output_directory"),
    }
    
    for env_var, config_path in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            # Navigate to the correct location in config
            current = config
            for path_part in config_path[:-1]:
                if path_part not in current:
                    current[path_part] = {}
                current = current[path_part]
            
            # Set the value
            current[config_path[-1]] = value
    
    return config


# Logging utilities
def setup_logging(
    level: str = "INFO",
    format_str: str = "detailed",
    log_file: Optional[str] = None
) -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Log level
        format_str: Log format
        log_file: Log file path
    """
    from .constants import LOG_FORMATS, LOG_LEVELS
    
    # Get log level
    log_level = LOG_LEVELS.get(level.upper(), LOG_LEVELS["INFO"])
    
    # Get format
    log_format = LOG_FORMATS.get(format_str, LOG_FORMATS["detailed"])
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)


# Performance utilities
def measure_time(func):
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
        
    Returns:
        Decorated function
    """
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} took {duration:.3f}s")
    
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} took {duration:.3f}s")
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage.
    
    Returns:
        Dict[str, float]: Memory usage information
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss,  # Resident Set Size
            "vms": memory_info.vms,  # Virtual Memory Size
            "percent": process.memory_percent()
        }
    except ImportError:
        return {"rss": 0, "vms": 0, "percent": 0}


def get_cpu_usage() -> float:
    """
    Get current CPU usage percentage.
    
    Returns:
        float: CPU usage percentage
    """
    try:
        import psutil
        return psutil.cpu_percent(interval=1)
    except ImportError:
        return 0.0 