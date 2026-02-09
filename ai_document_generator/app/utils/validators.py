"""
Validation utilities following functional patterns
"""
from typing import Any, Dict, List, Optional
import re
from datetime import datetime
import uuid


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength."""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "strength": calculate_password_strength(password)
    }


def calculate_password_strength(password: str) -> str:
    """Calculate password strength."""
    score = 0
    
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score <= 2:
        return "weak"
    elif score <= 4:
        return "medium"
    else:
        return "strong"


def validate_username(username: str) -> Dict[str, Any]:
    """Validate username format."""
    errors = []
    
    if len(username) < 3:
        errors.append("Username must be at least 3 characters long")
    
    if len(username) > 30:
        errors.append("Username must be no more than 30 characters long")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        errors.append("Username can only contain letters, numbers, underscores, and hyphens")
    
    if username.startswith('-') or username.endswith('-'):
        errors.append("Username cannot start or end with a hyphen")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def validate_document_title(title: str) -> Dict[str, Any]:
    """Validate document title."""
    errors = []
    
    if not title or not title.strip():
        errors.append("Title is required")
    
    if len(title) > 200:
        errors.append("Title must be no more than 200 characters long")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def validate_document_content(content: str) -> Dict[str, Any]:
    """Validate document content."""
    errors = []
    
    if len(content) > 1000000:  # 1MB limit
        errors.append("Content is too long (max 1MB)")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "word_count": len(content.split()) if content else 0,
        "character_count": len(content) if content else 0
    }


def validate_ai_prompt(prompt: str) -> Dict[str, Any]:
    """Validate AI prompt."""
    errors = []
    
    if not prompt or not prompt.strip():
        errors.append("Prompt is required")
    
    if len(prompt) > 10000:
        errors.append("Prompt must be no more than 10000 characters long")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "word_count": len(prompt.split()) if prompt else 0
    }


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_date_range(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Validate date range."""
    errors = []
    
    if start_date >= end_date:
        errors.append("Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        errors.append("Date range cannot exceed 365 days")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def validate_pagination(page: int, size: int) -> Dict[str, Any]:
    """Validate pagination parameters."""
    errors = []
    
    if page < 1:
        errors.append("Page must be greater than 0")
    
    if size < 1:
        errors.append("Size must be greater than 0")
    
    if size > 100:
        errors.append("Size cannot exceed 100")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def validate_file_upload(filename: str, content_type: str, size: int) -> Dict[str, Any]:
    """Validate file upload."""
    errors = []
    
    # Check file extension
    allowed_extensions = ['.txt', '.md', '.docx', '.pdf', '.rtf']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        errors.append(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    # Check content type
    allowed_types = [
        'text/plain',
        'text/markdown',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/pdf',
        'application/rtf'
    ]
    if content_type not in allowed_types:
        errors.append(f"Content type not allowed. Allowed types: {', '.join(allowed_types)}")
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if size > max_size:
        errors.append(f"File too large. Maximum size: {max_size // (1024 * 1024)}MB")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text


def validate_search_query(query: str) -> Dict[str, Any]:
    """Validate search query."""
    errors = []
    
    if not query or not query.strip():
        errors.append("Search query is required")
    
    if len(query) > 500:
        errors.append("Search query must be no more than 500 characters long")
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
        r'data:',
        r'vbscript:'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            errors.append("Search query contains potentially dangerous content")
            break
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "sanitized_query": sanitize_input(query)
    }


def validate_organization_name(name: str) -> Dict[str, Any]:
    """Validate organization name."""
    errors = []
    
    if not name or not name.strip():
        errors.append("Organization name is required")
    
    if len(name) > 100:
        errors.append("Organization name must be no more than 100 characters long")
    
    if not re.match(r'^[a-zA-Z0-9\s\-_&.]+$', name):
        errors.append("Organization name contains invalid characters")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key:
        return False
    
    # Check if it looks like a valid API key
    if len(api_key) < 20:
        return False
    
    # Check for common API key patterns
    patterns = [
        r'^sk-[a-zA-Z0-9]{48}$',  # OpenAI
        r'^sk-ant-[a-zA-Z0-9-]+$',  # Anthropic
        r'^[a-zA-Z0-9]{32,}$'  # Generic
    ]
    
    return any(re.match(pattern, api_key) for pattern in patterns)




