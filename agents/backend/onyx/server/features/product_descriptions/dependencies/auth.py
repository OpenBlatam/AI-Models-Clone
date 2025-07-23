"""
Authentication Dependencies

This module provides authentication and authorization dependency functions
for user management, role checking, and permission validation.
"""

from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging
from datetime import datetime, timedelta

# Import schemas and models
from ..schemas.base import User, UserPermissions
from ..dependencies.core import get_current_user
from ..utils.logging import get_logger

# Logger
logger = get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# JWT configuration (should be in config)
JWT_SECRET = "your-secret-key"  # Should be from environment
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(hours=24)

# User roles and permissions
USER_ROLES = {
    "admin": {
        "permissions": ["read", "write", "delete", "admin"],
        "description": "Full system access"
    },
    "user": {
        "permissions": ["read", "write"],
        "description": "Standard user access"
    },
    "viewer": {
        "permissions": ["read"],
        "description": "Read-only access"
    }
}

class AuthService:
    """Authentication service for user management."""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + JWT_EXPIRATION
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            return None
    
    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """Get user permissions based on role."""
        role_permissions = USER_ROLES.get(user.role, {}).get("permissions", [])
        return role_permissions
    
    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        permissions = AuthService.get_user_permissions(user)
        return permission in permissions

# FastAPI dependency functions
async def get_authenticated_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Get authenticated user.
    
    This dependency requires a valid JWT token and returns
    the authenticated user or raises an HTTP 401 error.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token
    payload = AuthService.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from token payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # TODO: Fetch user from database using user_id
    # For now, use the current_user if it matches
    if current_user and current_user.id == user_id:
        return current_user
    
    # Create user from token payload (temporary)
    user = User(
        id=user_id,
        email=payload.get("email", "user@example.com"),
        username=payload.get("username", "user"),
        role=payload.get("role", "user"),
        is_active=payload.get("is_active", True),
        is_admin=payload.get("is_admin", False),
        created_at=datetime.fromisoformat(payload.get("created_at", datetime.utcnow().isoformat()))
    )
    
    return user

async def get_admin_user(
    authenticated_user: User = Depends(get_authenticated_user)
) -> User:
    """
    Get admin user.
    
    This dependency requires admin privileges and returns
    the admin user or raises an HTTP 403 error.
    """
    if not authenticated_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return authenticated_user

async def get_user_permissions(
    authenticated_user: User = Depends(get_authenticated_user)
) -> UserPermissions:
    """
    Get user permissions.
    
    This dependency returns the user's permissions
    based on their role and custom permissions.
    """
    permissions = AuthService.get_user_permissions(authenticated_user)
    
    return UserPermissions(
        user_id=authenticated_user.id,
        role=authenticated_user.role,
        permissions=permissions,
        is_admin=authenticated_user.is_admin
    )

# Permission-based dependencies
def require_permission(permission: str):
    """
    Create a dependency that requires a specific permission.
    
    Usage:
        @router.get("/admin/users")
        async def get_users(user: User = Depends(require_permission("admin"))):
            ...
    """
    async def _require_permission(
        authenticated_user: User = Depends(get_authenticated_user)
    ) -> User:
        if not AuthService.has_permission(authenticated_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return authenticated_user
    
    return _require_permission

def require_role(role: str):
    """
    Create a dependency that requires a specific role.
    
    Usage:
        @router.get("/admin/users")
        async def get_users(user: User = Depends(require_role("admin"))):
            ...
    """
    async def _require_role(
        authenticated_user: User = Depends(get_authenticated_user)
    ) -> User:
        if authenticated_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        return authenticated_user
    
    return _require_role

# Utility functions
def create_user_token(user: User) -> str:
    """Create JWT token for user."""
    payload = {
        "sub": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat()
    }
    return AuthService.create_access_token(payload)

def validate_user_access(user: User, resource_owner_id: str) -> bool:
    """
    Validate if user can access a resource.
    
    Admins can access all resources, users can only access their own.
    """
    if user.is_admin:
        return True
    return user.id == resource_owner_id

# Rate limiting dependencies
class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # user_id -> [timestamps]
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to make a request."""
        now = datetime.utcnow()
        user_requests = self.requests.get(user_id, [])
        
        # Remove old requests outside the window
        user_requests = [
            req_time for req_time in user_requests
            if (now - req_time).seconds < self.window_seconds
        ]
        
        # Check if user has exceeded limit
        if len(user_requests) >= self.max_requests:
            return False
        
        # Add current request
        user_requests.append(now)
        self.requests[user_id] = user_requests
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

async def check_rate_limit(
    authenticated_user: User = Depends(get_authenticated_user)
) -> User:
    """
    Check rate limit for user.
    
    This dependency checks if the user has exceeded their rate limit
    and raises an HTTP 429 error if they have.
    """
    if not rate_limiter.is_allowed(authenticated_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return authenticated_user 