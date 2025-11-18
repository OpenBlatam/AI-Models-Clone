"""
Utility functions for cache system
"""

import hashlib
from typing import Any


def generate_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from prefix, args, and kwargs
    
    Args:
        prefix: Key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        MD5 hash of the key string
        
    Raises:
        ValueError: If prefix is invalid
    """
    if not prefix or not isinstance(prefix, str):
        raise ValueError("prefix must be a non-empty string")
    
    key_parts = [str(prefix)]
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_parts.extend(f"{k}:{v}" for k, v in sorted_kwargs)
    
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()

