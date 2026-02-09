"""
Authentication utilities following functional patterns
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.errors import handle_unauthorized_error, handle_forbidden_error
from app.models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise handle_unauthorized_error("Invalid token")


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


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def check_user_permissions(user: User, required_permissions: list) -> bool:
    """Check if user has required permissions."""
    if user.is_superuser:
        return True
    
    # Add more permission logic here based on your requirements
    return True


def validate_user_access(user: User) -> None:
    """Validate user access and raise appropriate errors."""
    if not user.is_active:
        raise handle_forbidden_error("Inactive user")
    
    if not user.is_verified:
        raise handle_forbidden_error("Unverified user")


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
        org_query = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == document.organization_id,
            OrganizationMember.is_active == True
        )
        org_result = await db.execute(org_query)
        if org_result.scalar_one_or_none():
            return True
    
    # Check document shares
    share_query = select(DocumentShare).where(
        DocumentShare.document_id == document_id,
        DocumentShare.shared_with == user_id,
        DocumentShare.is_active == True
    )
    share_result = await db.execute(share_query)
    share = share_result.scalar_one_or_none()
    
    if share:
        if required_permission == "view" and share.permission in ["view", "comment", "edit"]:
            return True
        elif required_permission == "comment" and share.permission in ["comment", "edit"]:
            return True
        elif required_permission == "edit" and share.permission == "edit":
            return True
    
    return False




