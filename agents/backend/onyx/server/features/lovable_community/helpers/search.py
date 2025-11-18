"""
Search helper functions

Functions for normalizing and processing search queries.
"""


def normalize_search_query(query: str) -> str:
    """
    Normalizes a search query.
    
    Args:
        query: Search query
        
    Returns:
        Normalized query
    """
    if not query:
        return ""
    
    # Remove extra spaces and convert to lowercase
    normalized = " ".join(query.strip().lower().split())
    return normalized








