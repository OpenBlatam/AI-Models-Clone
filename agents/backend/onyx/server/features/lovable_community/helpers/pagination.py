"""
Pagination helper functions

Functions for calculating pagination metadata and validating pagination parameters.
"""

from typing import Dict, Any, Tuple


def calculate_pagination_metadata(
    total: int,
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Calculates pagination metadata.
    
    Args:
        total: Total number of items
        page: Current page (1-indexed)
        page_size: Page size
        
    Returns:
        Dictionary with pagination metadata
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    has_more = (page * page_size) < total
    has_previous = page > 1
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_more": has_more,
        "has_previous": has_previous,
        "offset": (page - 1) * page_size
    }


def validate_and_calculate_pagination(
    page: int,
    page_size: int,
    max_page: int = 1000,
    max_page_size: int = 100
) -> Tuple[int, int, int]:
    """
    Validate pagination parameters and calculate skip offset.
    
    Args:
        page: Page number (1-indexed)
        page_size: Page size
        max_page: Maximum allowed page
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple of (validated_page, validated_page_size, skip)
    """
    validated_page = max(1, min(page, max_page))
    validated_page_size = max(1, min(page_size, max_page_size))
    skip = (validated_page - 1) * validated_page_size
    
    return validated_page, validated_page_size, skip



