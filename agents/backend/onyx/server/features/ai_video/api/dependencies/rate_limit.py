"""
Rate Limiting Dependencies
"""

from fastapi import HTTPException, status


async def check_rate_limit() -> None:
    """Check rate limit for current user."""
    # Simplified rate limiting - in production use Redis
    # For demo purposes, always allow
    pass 