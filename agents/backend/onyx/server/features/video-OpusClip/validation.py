"""
Centralized file type validation utilities for video/image processing.
Enhanced with comprehensive validation and error handling.
"""

import re
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from .error_handling import (
    create_validation_error, 
    ErrorCode, 
    ValidationError
)

# =============================================================================
# CONSTANTS
# =============================================================================

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

VIDEO_MIME_TYPES = [
    "video/mp4",
    "video/webm",
    "video/avi",
    "video/mov",
    "video/mkv",
]

YOUTUBE_URL_PATTERNS = [
    r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
    r'https?://youtu\.be/[\w-]+',
    r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
]

LANGUAGE_CODES = [
    'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh',
    'en-US', 'en-GB', 'es-MX', 'es-ES', 'fr-FR', 'de-DE', 'it-IT'
]

# =============================================================================
# BASIC VALIDATION FUNCTIONS
# =============================================================================

def is_valid_image_type(mime_type: str) -> bool:
    """Check if mime_type is a valid image type."""
    if not mime_type: return False
    return mime_type.startswith("image/") and mime_type not in EXCLUDED_IMAGE_TYPES

def is_supported_by_vision_llm(mime_type: str) -> bool:
    """Check if this image type can be processed by vision LLMs."""
    return mime_type in IMAGE_MIME_TYPES

def is_valid_video_type(mime_type: str) -> bool:
    """Check if mime_type is a valid video type."""
    if not mime_type: return False
    return mime_type in VIDEO_MIME_TYPES

def is_valid_youtube_url(url: str) -> bool:
    """Validate YouTube URL format."""
    if not url or not isinstance(url, str): return False
    
    for pattern in YOUTUBE_URL_PATTERNS:
        if re.match(pattern, url): return True
    return False

def is_valid_language_code(lang: str) -> bool:
    """Validate language code format."""
    if not lang or not isinstance(lang, str): return False
    return lang in LANGUAGE_CODES or re.match(r'^[a-z]{2}(-[A-Z]{2})?$', lang)

# =============================================================================
# COMPREHENSIVE VALIDATION FUNCTIONS
# =============================================================================

def validate_youtube_url(url: str, field_name: str = "youtube_url") -> None:
    """Validate YouTube URL with comprehensive guard clauses."""
    # GUARD CLAUSE: Empty or None URL
    if not url:
        raise create_validation_error("YouTube URL is required", field_name, url, ErrorCode.INVALID_YOUTUBE_URL)
    
    # GUARD CLAUSE: Wrong data type
    if not isinstance(url, str):
        raise create_validation_error("YouTube URL must be a string", field_name, url, ErrorCode.INVALID_YOUTUBE_URL)
    
    # GUARD CLAUSE: Extremely long URL (potential DoS)
    if len(url) > 2048:
        raise create_validation_error("YouTube URL too long (max 2048 characters)", field_name, url, ErrorCode.INVALID_YOUTUBE_URL)
    
    # GUARD CLAUSE: Malicious patterns
    malicious_patterns = [
        "javascript:", "data:", "vbscript:", "file://", "ftp://",
        "eval(", "exec(", "system(", "shell_exec("
    ]
    url_lower = url.lower()
    for pattern in malicious_patterns:
        if pattern in url_lower:
            raise create_validation_error(f"Malicious URL pattern detected: {pattern}", field_name, url, ErrorCode.INVALID_YOUTUBE_URL)
    
    # GUARD CLAUSE: Standard validation
    if not is_valid_youtube_url(url):
        raise create_validation_error(f"Invalid YouTube URL format: {url}", field_name, url, ErrorCode.INVALID_YOUTUBE_URL)
    
    # HAPPY PATH: URL is valid (implicit return)

def validate_language_code(lang: str, field_name: str = "language") -> None:
    """Validate language code with comprehensive guard clauses."""
    # GUARD CLAUSE: Empty or None language
    if not lang:
        raise create_validation_error("Language code is required", field_name, lang, ErrorCode.INVALID_LANGUAGE_CODE)
    
    # GUARD CLAUSE: Wrong data type
    if not isinstance(lang, str):
        raise create_validation_error("Language code must be a string", field_name, lang, ErrorCode.INVALID_LANGUAGE_CODE)
    
    # GUARD CLAUSE: Invalid language code
    if not is_valid_language_code(lang):
        raise create_validation_error(f"Invalid language code: {lang}", field_name, lang, ErrorCode.INVALID_LANGUAGE_CODE)
    
    # HAPPY PATH: Language code is valid (implicit return)

def validate_clip_length(length: int, field_name: str = "clip_length", min_length: int = 1, max_length: int = 600) -> None:
    """Validate clip length with comprehensive guard clauses."""
    # GUARD CLAUSE: Wrong data type
    if not isinstance(length, int):
        raise create_validation_error("Clip length must be an integer", field_name, length, ErrorCode.INVALID_CLIP_LENGTH)
    
    # GUARD CLAUSE: Negative values
    if length < 0:
        raise create_validation_error("Clip length cannot be negative", field_name, length, ErrorCode.INVALID_CLIP_LENGTH)
    
    # GUARD CLAUSE: Zero length
    if length == 0:
        raise create_validation_error("Clip length cannot be zero", field_name, length, ErrorCode.INVALID_CLIP_LENGTH)
    
    # GUARD CLAUSE: Extremely short clips (potential abuse)
    if length < min_length:
        raise create_validation_error(f"Clip length must be at least {min_length} seconds", field_name, length, ErrorCode.INVALID_CLIP_LENGTH)
    
    # GUARD CLAUSE: Extremely long clips (resource exhaustion)
    if length > max_length:
        raise create_validation_error(f"Clip length cannot exceed {max_length} seconds", field_name, length, ErrorCode.INVALID_CLIP_LENGTH)
    
    # GUARD CLAUSE: Unrealistic values (potential overflow)
    if length > 86400:  # 24 hours
        raise create_validation_error("Clip length exceeds maximum allowed duration (24 hours)", field_name, length, ErrorCode.INVALID_CLIP_LENGTH)
    
    # HAPPY PATH: Clip length is valid (implicit return)

def validate_viral_score(score: float, field_name: str = "viral_score") -> None:
    """Validate viral score and raise ValidationError if invalid."""
    # ERROR HANDLING: Wrong data type
    if not isinstance(score, (int, float)):
        raise create_validation_error("Viral score must be a number", field_name, score, ErrorCode.INVALID_VIRAL_SCORE)
    
    # ERROR HANDLING: Out of range
    if score < 0.0 or score > 1.0:
        raise create_validation_error("Viral score must be between 0.0 and 1.0", field_name, score, ErrorCode.INVALID_VIRAL_SCORE)
    
    # HAPPY PATH: Viral score is valid (implicit return)

def validate_caption(caption: str, field_name: str = "caption", max_length: int = 1000) -> None:
    """Validate caption and raise ValidationError if invalid."""
    # ERROR HANDLING: Empty or None caption
    if not caption:
        raise create_validation_error("Caption is required", field_name, caption, ErrorCode.INVALID_CAPTION)
    
    # ERROR HANDLING: Wrong data type
    if not isinstance(caption, str):
        raise create_validation_error("Caption must be a string", field_name, caption, ErrorCode.INVALID_CAPTION)
    
    # ERROR HANDLING: Empty after stripping
    if len(caption.strip()) == 0:
        raise create_validation_error("Caption cannot be empty", field_name, caption, ErrorCode.INVALID_CAPTION)
    
    # ERROR HANDLING: Too long
    if len(caption) > max_length:
        raise create_validation_error(f"Caption too long (max {max_length} characters)", field_name, caption, ErrorCode.INVALID_CAPTION)
    
    # HAPPY PATH: Caption is valid (implicit return)

def validate_variant_id(variant_id: str, field_name: str = "variant_id") -> None:
    """Validate variant ID and raise ValidationError if invalid."""
    # ERROR HANDLING: Empty or None variant ID
    if not variant_id:
        raise create_validation_error("Variant ID is required", field_name, variant_id, ErrorCode.INVALID_VARIANT_ID)
    
    # ERROR HANDLING: Wrong data type
    if not isinstance(variant_id, str):
        raise create_validation_error("Variant ID must be a string", field_name, variant_id, ErrorCode.INVALID_VARIANT_ID)
    
    # ERROR HANDLING: Invalid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', variant_id):
        raise create_validation_error("Variant ID contains invalid characters", field_name, variant_id, ErrorCode.INVALID_VARIANT_ID)
    
    # HAPPY PATH: Variant ID is valid (implicit return)

def validate_audience_profile(profile: Dict[str, Any], field_name: str = "audience_profile") -> None:
    """Validate audience profile and raise ValidationError if invalid."""
    # ERROR HANDLING: Wrong data type
    if not isinstance(profile, dict):
        raise create_validation_error("Audience profile must be a dictionary", field_name, profile, ErrorCode.INVALID_AUDIENCE_PROFILE)
    
    # ERROR HANDLING: Missing required fields
    required_fields = ['age', 'interests']
    for field in required_fields:
        if field not in profile:
            raise create_validation_error(f"Audience profile missing required field: {field}", field_name, profile, ErrorCode.INVALID_AUDIENCE_PROFILE)
    
    # ERROR HANDLING: Wrong interests type
    if not isinstance(profile.get('interests'), list):
        raise create_validation_error("Audience interests must be a list", field_name, profile, ErrorCode.INVALID_AUDIENCE_PROFILE)
    
    # HAPPY PATH: Audience profile is valid (implicit return)

def validate_batch_size(size: int, field_name: str = "batch_size", min_size: int = 1, max_size: int = 100) -> None:
    """Validate batch size and raise ValidationError if invalid."""
    # ERROR HANDLING: Wrong data type
    if not isinstance(size, int):
        raise create_validation_error("Batch size must be an integer", field_name, size, ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Negative values
    if size < 0:
        raise create_validation_error("Batch size cannot be negative", field_name, size, ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Zero batch size
    if size == 0:
        raise create_validation_error("Batch size cannot be zero", field_name, size, ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Extremely small batches (inefficient)
    if size < min_size:
        raise create_validation_error(f"Batch size must be at least {min_size}", field_name, size, ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Extremely large batches (resource exhaustion)
    if size > max_size:
        raise create_validation_error(f"Batch size cannot exceed {max_size}", field_name, size, ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Unrealistic batch sizes (potential DoS)
    if size > 1000:
        raise create_validation_error("Batch size exceeds maximum allowed limit (1000)", field_name, size, ErrorCode.INVALID_BATCH_SIZE)
    
    # HAPPY PATH: Batch size is valid (implicit return)

# =============================================================================
# COMPOSITE VALIDATION FUNCTIONS
# =============================================================================

def validate_video_request_data(
    youtube_url: str,
    language: str,
    max_clip_length: Optional[int] = None,
    min_clip_length: Optional[int] = None,
    audience_profile: Optional[Dict[str, Any]] = None
) -> None:
    """Validate all video request data at once with early error handling."""
    # ERROR HANDLING: Check for None/empty required parameters first
    if not youtube_url or not youtube_url.strip():
        raise create_validation_error("YouTube URL is required and cannot be empty", "youtube_url", youtube_url, ErrorCode.INVALID_YOUTUBE_URL)
    
    if not language or not language.strip():
        raise create_validation_error("Language is required and cannot be empty", "language", language, ErrorCode.INVALID_LANGUAGE_CODE)
    
    # ERROR HANDLING: Validate data types first
    if not isinstance(youtube_url, str):
        raise create_validation_error("YouTube URL must be a string", "youtube_url", youtube_url, ErrorCode.INVALID_YOUTUBE_URL)
    
    if not isinstance(language, str):
        raise create_validation_error("Language must be a string", "language", language, ErrorCode.INVALID_LANGUAGE_CODE)
    
    # ERROR HANDLING: Validate optional parameters if provided
    if max_clip_length is not None:
        if not isinstance(max_clip_length, int):
            raise create_validation_error("max_clip_length must be an integer", "max_clip_length", max_clip_length, ErrorCode.INVALID_CLIP_LENGTH)
        if max_clip_length <= 0:
            raise create_validation_error("max_clip_length must be positive", "max_clip_length", max_clip_length, ErrorCode.INVALID_CLIP_LENGTH)
    
    if min_clip_length is not None:
        if not isinstance(min_clip_length, int):
            raise create_validation_error("min_clip_length must be an integer", "min_clip_length", min_clip_length, ErrorCode.INVALID_CLIP_LENGTH)
        if min_clip_length <= 0:
            raise create_validation_error("min_clip_length must be positive", "min_clip_length", min_clip_length, ErrorCode.INVALID_CLIP_LENGTH)
    
    if audience_profile is not None:
        if not isinstance(audience_profile, dict):
            raise create_validation_error("audience_profile must be a dictionary", "audience_profile", audience_profile, ErrorCode.INVALID_AUDIENCE_PROFILE)
    
    # ERROR HANDLING: Validate logical constraints
    if max_clip_length is not None and min_clip_length is not None:
        if max_clip_length < min_clip_length:
            raise create_validation_error("max_clip_length cannot be less than min_clip_length", "max_clip_length", max_clip_length, ErrorCode.INVALID_CLIP_LENGTH)
    
    # HAPPY PATH: Validate individual fields
    validate_youtube_url(youtube_url)
    validate_language_code(language)
    
    if max_clip_length is not None:
        validate_clip_length(max_clip_length, "max_clip_length")
    if min_clip_length is not None:
        validate_clip_length(min_clip_length, "min_clip_length")
    if audience_profile is not None:
        validate_audience_profile(audience_profile)

def validate_viral_variant_data(
    start: float,
    end: float,
    caption: str,
    viral_score: float,
    variant_id: str
) -> None:
    """Validate viral variant data at once with early error handling."""
    # ERROR HANDLING: Check for None/empty required parameters first
    if caption is None or not caption.strip():
        raise create_validation_error("Caption is required and cannot be empty", "caption", caption, ErrorCode.INVALID_CAPTION)
    
    if variant_id is None or not variant_id.strip():
        raise create_validation_error("Variant ID is required and cannot be empty", "variant_id", variant_id, ErrorCode.INVALID_VARIANT_ID)
    
    # ERROR HANDLING: Validate data types first
    if not isinstance(caption, str):
        raise create_validation_error("Caption must be a string", "caption", caption, ErrorCode.INVALID_CAPTION)
    
    if not isinstance(variant_id, str):
        raise create_validation_error("Variant ID must be a string", "variant_id", variant_id, ErrorCode.INVALID_VARIANT_ID)
    
    if not isinstance(start, (int, float)):
        raise create_validation_error("Start time must be a number", "start", start, ErrorCode.INVALID_CLIP_LENGTH)
    
    if not isinstance(end, (int, float)):
        raise create_validation_error("End time must be a number", "end", end, ErrorCode.INVALID_CLIP_LENGTH)
    
    if not isinstance(viral_score, (int, float)):
        raise create_validation_error("Viral score must be a number", "viral_score", viral_score, ErrorCode.INVALID_VIRAL_SCORE)
    
    # ERROR HANDLING: Validate numeric constraints first
    if start < 0:
        raise create_validation_error("Start time must be non-negative", "start", start, ErrorCode.INVALID_CLIP_LENGTH)
    
    if end < 0:
        raise create_validation_error("End time must be non-negative", "end", end, ErrorCode.INVALID_CLIP_LENGTH)
    
    if viral_score < 0.0 or viral_score > 1.0:
        raise create_validation_error("Viral score must be between 0.0 and 1.0", "viral_score", viral_score, ErrorCode.INVALID_VIRAL_SCORE)
    
    # ERROR HANDLING: Validate logical constraints
    if start >= end:
        raise create_validation_error("Start time must be less than end time", "start", start, ErrorCode.INVALID_CLIP_LENGTH)
    
    # ERROR HANDLING: Validate string constraints
    if len(caption.strip()) == 0:
        raise create_validation_error("Caption cannot be empty", "caption", caption, ErrorCode.INVALID_CAPTION)
    
    if len(caption) > 1000:  # Reasonable limit
        raise create_validation_error("Caption too long (max 1000 characters)", "caption", caption, ErrorCode.INVALID_CAPTION)
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', variant_id):
        raise create_validation_error("Variant ID contains invalid characters", "variant_id", variant_id, ErrorCode.INVALID_VARIANT_ID)
    
    # HAPPY PATH: Validate individual fields (redundant but for completeness)
    validate_caption(caption)
    validate_viral_score(viral_score)
    validate_variant_id(variant_id)

def validate_batch_request_data(
    requests: List[Dict[str, Any]],
    batch_size: Optional[int] = None
) -> None:
    """Validate batch request data with early error handling."""
    # ERROR HANDLING: Check for None/empty requests list first
    if not requests:
        raise create_validation_error("Requests list cannot be empty", "requests", requests, ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Validate data type first
    if not isinstance(requests, list):
        raise create_validation_error("Requests must be a list", "requests", requests, ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Check for reasonable batch size limits
    if len(requests) > 1000:  # Absolute maximum
        raise create_validation_error("Batch size exceeds maximum limit of 1000", "batch_size", len(requests), ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Validate batch size parameter if provided
    if batch_size is not None:
        if not isinstance(batch_size, int):
            raise create_validation_error("batch_size must be an integer", "batch_size", batch_size, ErrorCode.INVALID_BATCH_SIZE)
        
        if batch_size <= 0:
            raise create_validation_error("batch_size must be positive", "batch_size", batch_size, ErrorCode.INVALID_BATCH_SIZE)
        
        if len(requests) != batch_size:
            raise create_validation_error(f"Expected {batch_size} requests, got {len(requests)}", "batch_size", len(requests), ErrorCode.INVALID_BATCH_SIZE)
    
    # ERROR HANDLING: Validate each request structure first
    for i, request in enumerate(requests):
        # Check for None requests
        if request is None:
            raise create_validation_error(f"Request at index {i} cannot be None", f"requests[{i}]", None, ErrorCode.INVALID_YOUTUBE_URL)
        
        # Check data type
        if not isinstance(request, dict):
            raise create_validation_error(f"Request at index {i} must be a dictionary", f"requests[{i}]", request, ErrorCode.INVALID_YOUTUBE_URL)
        
        # Check for required fields early
        youtube_url = request.get('youtube_url')
        language = request.get('language')
        
        if not youtube_url or not youtube_url.strip():
            raise create_validation_error(f"YouTube URL is required for request at index {i}", f"requests[{i}].youtube_url", youtube_url, ErrorCode.INVALID_YOUTUBE_URL)
        
        if not language or not language.strip():
            raise create_validation_error(f"Language is required for request at index {i}", f"requests[{i}].language", language, ErrorCode.INVALID_LANGUAGE_CODE)
        
        # Check data types early
        if not isinstance(youtube_url, str):
            raise create_validation_error(f"YouTube URL must be a string for request at index {i}", f"requests[{i}].youtube_url", youtube_url, ErrorCode.INVALID_YOUTUBE_URL)
        
        if not isinstance(language, str):
            raise create_validation_error(f"Language must be a string for request at index {i}", f"requests[{i}].language", language, ErrorCode.INVALID_LANGUAGE_CODE)
    
    # HAPPY PATH: Validate individual fields for each request
    for i, request in enumerate(requests):
        validate_video_request_data(**request)

# =============================================================================
# VALIDATION DECORATORS
# =============================================================================

def validate_video_request(func):
    """Decorator to validate video request parameters."""
    def wrapper(*args, **kwargs):
        # Extract request object (assuming it's the first argument after self)
        request = args[1] if len(args) > 1 else kwargs.get('request')
        if request:
            validate_video_request_data(
                youtube_url=request.youtube_url,
                language=request.language,
                max_clip_length=getattr(request, 'max_clip_length', None),
                min_clip_length=getattr(request, 'min_clip_length', None),
                audience_profile=getattr(request, 'audience_profile', None)
            )
        return func(*args, **kwargs)
    return wrapper

def validate_batch_request(func):
    """Decorator to validate batch request parameters."""
    def wrapper(*args, **kwargs):
        # Extract batch request object
        batch_request = args[1] if len(args) > 1 else kwargs.get('batch_request')
        if batch_request:
            validate_batch_request_data(
                requests=batch_request.requests,
                batch_size=getattr(batch_request, 'batch_size', None)
            )
        return func(*args, **kwargs)
    return wrapper

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def sanitize_youtube_url(url: str) -> str:
    """Sanitize and normalize YouTube URL."""
    if not url: return url
    
    # Remove extra whitespace
    url = url.strip()
    
    # Ensure HTTPS
    if url.startswith('http://'): url = url.replace('http://', 'https://', 1)
    
    # Remove tracking parameters
    parsed = urlparse(url)
    query_params = parsed.query.split('&')
    clean_params = [param for param in query_params if not param.startswith(('utm_', 'fbclid', 'gclid'))]
    
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if clean_params: clean_url += f"?{'&'.join(clean_params)}"
    
    return clean_url

def extract_youtube_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    if not is_valid_youtube_url(url): return None
    
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([\w-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match: return match.group(1)
    
    return None

def validate_and_sanitize_url(url: str, field_name: str = "url") -> str:
    """Validate and sanitize URL in one operation."""
    validate_youtube_url(url, field_name)
    return sanitize_youtube_url(url)

# =============================================================================
# SYSTEM HEALTH MONITORING
# =============================================================================

def check_system_resources() -> Dict[str, Any]:
    """Check system resources and return health status."""
    import psutil
    import os
    
    health_status = {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "network_status": "healthy"
    }
    
    # Check for critical resource levels
    if health_status["memory_usage"] > 90:
        health_status["memory_critical"] = True
        health_status["warnings"] = health_status.get("warnings", []) + ["High memory usage"]
    
    if health_status["disk_usage"] > 95:
        health_status["disk_critical"] = True
        health_status["warnings"] = health_status.get("warnings", []) + ["Critical disk space"]
    
    if health_status["cpu_usage"] > 95:
        health_status["cpu_critical"] = True
        health_status["warnings"] = health_status.get("warnings", []) + ["High CPU usage"]
    
    return health_status

def validate_system_health() -> None:
    """Validate system health and raise CriticalSystemError if unhealthy."""
    from .error_handling import create_critical_system_error, ErrorCode
    
    health_status = check_system_resources()
    
    # Check for critical conditions
    if health_status.get("memory_critical"):
        raise create_critical_system_error(
            "Critical memory usage detected",
            "memory",
            {"usage_percent": health_status["memory_usage"]},
            ErrorCode.GPU_MEMORY_EXHAUSTED
        )
    
    if health_status.get("disk_critical"):
        raise create_critical_system_error(
            "Critical disk space detected",
            "disk",
            {"usage_percent": health_status["disk_usage"]},
            ErrorCode.DISK_SPACE_CRITICAL
        )
    
    if health_status.get("cpu_critical"):
        raise create_critical_system_error(
            "Critical CPU usage detected",
            "cpu",
            {"usage_percent": health_status["cpu_usage"]},
            ErrorCode.CPU_OVERLOADED
        )

def check_gpu_availability() -> Dict[str, Any]:
    """Check GPU availability and status."""
    try:
        import torch
        
        gpu_status = {
            "available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
            "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None
        }
        
        if gpu_status["available"]:
            gpu_status["device_name"] = torch.cuda.get_device_name(0)
            gpu_status["memory_allocated"] = torch.cuda.memory_allocated(0) / 1024**3  # GB
            gpu_status["memory_reserved"] = torch.cuda.memory_reserved(0) / 1024**3  # GB
            gpu_status["memory_total"] = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            
            # Check for critical GPU memory usage
            if gpu_status["memory_allocated"] / gpu_status["memory_total"] > 0.95:
                gpu_status["memory_critical"] = True
                gpu_status["warnings"] = gpu_status.get("warnings", []) + ["Critical GPU memory usage"]
        
        return gpu_status
        
    except ImportError:
        return {"available": False, "error": "PyTorch not available"}
    except Exception as e:
        return {"available": False, "error": str(e)}

def validate_gpu_health() -> None:
    """Validate GPU health and raise ResourceError if unhealthy."""
    from .error_handling import create_resource_error, ErrorCode
    
    gpu_status = check_gpu_availability()
    
    if not gpu_status["available"]:
        raise create_resource_error(
            "GPU not available for processing",
            "gpu",
            "CPU only",
            "CUDA GPU required",
            ErrorCode.GPU_NOT_AVAILABLE
        )
    
    if gpu_status.get("memory_critical"):
        raise create_resource_error(
            "GPU memory exhausted",
            "gpu_memory",
            f"{gpu_status['memory_allocated']:.2f}GB",
            f"{gpu_status['memory_total']:.2f}GB",
            ErrorCode.GPU_MEMORY_EXHAUSTED
        ) 