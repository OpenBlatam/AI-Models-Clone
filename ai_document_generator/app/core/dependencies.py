"""
FastAPI dependencies following functional patterns
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth_utils import decode_token, get_user_by_id, validate_user_access
from app.core.errors import handle_unauthorized_error
from app.schemas.user import User

# JWT token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise handle_unauthorized_error()
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise handle_unauthorized_error()
        
        user = await get_user_by_id(db, user_id)
        if not user:
            raise handle_unauthorized_error()
        
        validate_user_access(user)
        return user
    
    except HTTPException:
        raise
    except Exception:
        raise handle_unauthorized_error()


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if not user_id:
            return None
        
        user = await get_user_by_id(db, user_id)
        if not user or not user.is_active:
            return None
        
        return user
    
    except Exception:
        return None




