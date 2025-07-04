"""
Authentication Dependencies - Clean auth functions
"""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from ..utils.auth import decode_jwt_token, validate_permissions


security = HTTPBearer()


async def get_current_user(token: str = Depends(security)) -> dict:
    """
    Get current user from JWT token.
    
    Returns:
        User dict with sub, permissions, etc.
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = decode_jwt_token(token.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
        )


def require_permissions(required_permissions: List[str]):
    """
    Dependency factory for permission requirements.
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        Dependency function
    """
    def permission_dependency(current_user: dict = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        
        if not validate_permissions(user_permissions, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return None
    
    return permission_dependency 