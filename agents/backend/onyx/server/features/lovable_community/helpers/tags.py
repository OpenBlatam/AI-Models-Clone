"""
Tag-related helper functions

Functions for parsing, formatting, and extracting tags.
"""

import re
from typing import Optional, List


def parse_tags_string(tags_str: Optional[str]) -> Optional[List[str]]:
    """
    Parses a comma-separated tags string to a list.
    
    Optimized to avoid unnecessary operations.
    
    Args:
        tags_str: String with comma-separated tags
        
    Returns:
        List of sanitized tags or None
    """
    if not tags_str:
        return None
    
    stripped = tags_str.strip()
    if not stripped:
        return None
    
    tags = [tag.strip().lower() for tag in stripped.split(",") if tag.strip()]
    return tags if tags else None


def format_tags_list(tags: Optional[List[str]]) -> Optional[str]:
    """
    Formats a list of tags to a comma-separated string.
    
    Args:
        tags: List of tags
        
    Returns:
        String with comma-separated tags or None
    """
    if not tags:
        return None
    
    # Sanitize and join tags
    sanitized = [tag.strip().lower() for tag in tags if tag and tag.strip()]
    return ",".join(sanitized) if sanitized else None


def extract_tags_from_text(text: str) -> List[str]:
    """
    Extracts possible tags from text.
    
    Searches for words starting with # and extracts them as tags.
    
    Args:
        text: Text from which to extract tags
        
    Returns:
        List of extracted tags
    """
    if not text:
        return []
    
    # Find words starting with #
    tags = re.findall(r'#(\w+)', text.lower())
    # Remove duplicates while maintaining order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag and tag not in seen and len(tag) <= 50:
            seen.add(tag)
            unique_tags.append(tag)
    
    return unique_tags[:10]  # Maximum 10 tags



