"""
Helper utilities following functional patterns
"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import hashlib
import secrets
import string
import json
import uuid


def generate_random_string(length: int = 32) -> str:
    """Generate a random string of specified length."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_secure_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string using specified algorithm."""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def create_slug(text: str) -> str:
    """Create a URL-friendly slug from text."""
    import re
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text."""
    import re
    pattern = r'@(\w+)'
    return re.findall(pattern, text)


def extract_hashtags(text: str) -> List[str]:
    """Extract #hashtags from text."""
    import re
    pattern = r'#(\w+)'
    return re.findall(pattern, text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    import re
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(pattern, text)


def clean_html(html_text: str) -> str:
    """Remove HTML tags from text."""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text)


def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def count_characters(text: str) -> int:
    """Count characters in text."""
    return len(text) if text else 0


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes."""
    word_count = count_words(text)
    return max(1, word_count // words_per_minute)


def generate_short_id() -> str:
    """Generate a short unique ID."""
    return str(uuid.uuid4())[:8]


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data showing only last few characters."""
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    import re
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))


def parse_json_safely(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string."""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def to_json_safely(obj: Any, default: str = "{}") -> str:
    """Safely convert object to JSON string."""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def filter_dict(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filter dictionary to include only specified keys."""
    return {k: v for k, v in d.items() if k in keys}


def exclude_dict(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filter dictionary to exclude specified keys."""
    return {k: v for k, v in d.items() if k not in keys}


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """Flatten a list of lists."""
    return [item for sublist in nested_list for item in sublist]


def remove_duplicates(lst: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order."""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]


def group_by(lst: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group list of dictionaries by specified key."""
    groups = {}
    for item in lst:
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups


def sort_by_key(lst: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """Sort list of dictionaries by specified key."""
    return sorted(lst, key=lambda x: x.get(key, 0), reverse=reverse)


def get_nested_value(obj: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get nested value from dictionary using dot notation."""
    keys = key_path.split('.')
    current = obj
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(obj: Dict[str, Any], key_path: str, value: Any) -> None:
    """Set nested value in dictionary using dot notation."""
    keys = key_path.split('.')
    current = obj
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string."""
    return timestamp.strftime(format_str)


def parse_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse timestamp string to datetime."""
    try:
        return datetime.strptime(timestamp_str, format_str)
    except ValueError:
        return None


def get_time_ago(timestamp: datetime) -> str:
    """Get human-readable time ago string."""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"


def is_expired(timestamp: datetime, expiry_duration: timedelta) -> bool:
    """Check if timestamp is expired."""
    return datetime.utcnow() > timestamp + expiry_duration


def get_expiry_time(duration: timedelta) -> datetime:
    """Get expiry time from current time plus duration."""
    return datetime.utcnow() + duration




