"""
Validation Dependencies
"""

from fastapi import HTTPException, status


def validate_request_id(request_id: str) -> str:
    """Validate request ID format."""
    if not request_id or len(request_id) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID format"
        )
    return request_id 