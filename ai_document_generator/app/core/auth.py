"""
Authentication and authorization utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserSession
from app.schemas.user import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode access token and return payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise AuthenticationError("Invalid token")


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID from database."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email from database."""
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username from database."""
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(db, token_data.user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


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


async def create_user_session(
    db: AsyncSession,
    user_id: str,
    session_token: str,
    refresh_token: Optional[str] = None,
    device_info: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> UserSession:
    """Create a new user session."""
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    session = UserSession(
        user_id=user_id,
        session_token=session_token,
        refresh_token=refresh_token,
        device_info=device_info,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        last_activity=datetime.utcnow()
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


async def get_user_session(
    db: AsyncSession,
    session_token: str
) -> Optional[UserSession]:
    """Get user session by token."""
    query = select(UserSession).where(
        UserSession.session_token == session_token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user_session_activity(
    db: AsyncSession,
    session_id: str
) -> None:
    """Update user session last activity."""
    query = select(UserSession).where(UserSession.id == session_id)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if session:
        session.last_activity = datetime.utcnow()
        await db.commit()


async def revoke_user_session(
    db: AsyncSession,
    session_token: str
) -> None:
    """Revoke a user session."""
    query = select(UserSession).where(UserSession.session_token == session_token)
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if session:
        session.is_active = False
        await db.commit()


async def revoke_all_user_sessions(
    db: AsyncSession,
    user_id: str
) -> None:
    """Revoke all sessions for a user."""
    query = select(UserSession).where(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    )
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    for session in sessions:
        session.is_active = False
    
    await db.commit()


def check_permissions(user: User, required_permissions: list) -> bool:
    """Check if user has required permissions."""
    # Simplified permission check
    # In production, this would check against user roles and permissions
    if user.is_superuser:
        return True
    
    # Add more permission logic here
    return True


def require_permissions(required_permissions: list):
    """Decorator to require specific permissions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not check_permissions(current_user, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(required_role: str):
    """Decorator to require specific role."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check user role (simplified)
            # In production, this would check against user's organization roles
            if not current_user.is_superuser and required_role == "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin role required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def verify_organization_access(
    db: AsyncSession,
    user_id: str,
    organization_id: str,
    required_role: Optional[str] = None
) -> bool:
    """Verify user has access to organization."""
    from app.models.organization import OrganizationMember
    
    query = select(OrganizationMember).where(
        OrganizationMember.user_id == user_id,
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.is_active == True
    )
    result = await db.execute(query)
    membership = result.scalar_one_or_none()
    
    if not membership:
        return False
    
    if required_role and membership.role != required_role:
        return False
    
    return True


async def verify_document_access(
    db: AsyncSession,
    user_id: str,
    document_id: str,
    required_permission: str = "view"
) -> bool:
    """Verify user has access to document."""
    from app.models.document import Document, DocumentShare
    from app.models.organization import OrganizationMember
    
    # Get document
    query = select(Document).where(Document.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        return False
    
    # Check if user is owner
    if document.owner_id == user_id:
        return True
    
    # Check if document is public and user has view permission
    if document.is_public and required_permission == "view":
        return True
    
    # Check organization membership
    if document.organization_id:
        has_org_access = await verify_organization_access(
            db, user_id, document.organization_id
        )
        if has_org_access:
            return True
    
    # Check document shares
    query = select(DocumentShare).where(
        DocumentShare.document_id == document_id,
        DocumentShare.shared_with == user_id,
        DocumentShare.is_active == True
    )
    result = await db.execute(query)
    share = result.scalar_one_or_none()
    
    if share:
        if required_permission == "view" and share.permission in ["view", "comment", "edit"]:
            return True
        elif required_permission == "comment" and share.permission in ["comment", "edit"]:
            return True
        elif required_permission == "edit" and share.permission == "edit":
            return True
    
    return False




