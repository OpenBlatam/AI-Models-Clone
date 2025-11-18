"""
Common helper functions

Utility functions for common operations like ID generation and timestamps.
"""

import uuid
from datetime import datetime


def generate_id() -> str:
    """
    Generate a new UUID as string.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """
    Get current UTC timestamp.
    
    Returns:
        Current UTC datetime
    """
    return datetime.utcnow()






