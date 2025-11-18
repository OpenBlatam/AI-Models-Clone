"""
User service following functional patterns
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import uuid

from app.core.logging import get_logger
from app.core.errors import handle_not_found_error, handle_conflict_error, handle_internal_error
from app.core.auth_utils import get_password_hash, get_user_by_email, get_user_by_username
from app.models.user import User, UserSession, UserInvitation
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin,
    PasswordReset, PasswordResetConfirm
)
from app.utils.validators import validate_email, validate_username
from app.utils.helpers import generate_secure_token, create_slug
from app.utils.cache import cache_user_data, get_cached_user_data, invalidate_user_cache

logger = get_logger(__name__)


async def create_user(
    user_data: UserCreate,
    db: AsyncSession
) -> UserResponse:
    """Create a new user."""
    try:
        # Check if email already exists
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            raise handle_conflict_error("Email already registered")
        
        # Check if username already exists
        existing_username = await get_user_by_username(db, user_data.username)
        if existing_username:
            raise handle_conflict_error("Username already taken")
        
        # Create user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=True,
            is_verified=False,  # Email verification required
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Cache user data
        cache_user_data(str(user.id), user)
        
        logger.info(f"User created: {user.id} ({user.email})")
        
        return UserResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create user: {e}")
        raise handle_internal_error(f"Failed to create user: {str(e)}")


async def get_user_profile(
    user_id: str,
    db: AsyncSession
) -> UserResponse:
    """Get user profile by ID."""
    try:
        # Check cache first
        cached_user = get_cached_user_data(user_id)
        if cached_user:
            return UserResponse.from_orm(cached_user)
        
        # Get from database
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        
        if not user:
            raise handle_not_found_error("User", user_id)
        
        # Cache user data
        cache_user_data(user_id, user)
        
        return UserResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise handle_internal_error(f"Failed to get user profile: {str(e)}")


async def update_user(
    user_id: str,
    update_data: UserUpdate,
    db: AsyncSession
) -> UserResponse:
    """Update user profile."""
    try:
        # Get user
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        
        if not user:
            raise handle_not_found_error("User", user_id)
        
        # Check email uniqueness if changing email
        if update_data.email and update_data.email != user.email:
            existing_user = await get_user_by_email(db, update_data.email)
            if existing_user:
                raise handle_conflict_error("Email already registered")
        
        # Check username uniqueness if changing username
        if update_data.username and update_data.username != user.username:
            existing_username = await get_user_by_username(db, update_data.username)
            if existing_username:
                raise handle_conflict_error("Username already taken")
        
        # Update fields
        if update_data.email is not None:
            user.email = update_data.email
            user.is_verified = False  # Require re-verification
        
        if update_data.username is not None:
            user.username = update_data.username
        
        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        
        if update_data.bio is not None:
            user.bio = update_data.bio
        
        if update_data.avatar_url is not None:
            user.avatar_url = update_data.avatar_url
        
        if update_data.timezone is not None:
            user.timezone = update_data.timezone
        
        if update_data.language is not None:
            user.language = update_data.language
        
        if update_data.notification_preferences is not None:
            user.notification_preferences = update_data.notification_preferences
        
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        # Invalidate cache
        invalidate_user_cache(user_id)
        
        logger.info(f"User updated: {user_id}")
        
        return UserResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update user: {e}")
        raise handle_internal_error(f"Failed to update user: {str(e)}")


async def deactivate_user(
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Deactivate user account."""
    try:
        # Get user
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        
        if not user:
            raise handle_not_found_error("User", user_id)
        
        # Deactivate user
        user.is_active = False
        user.deactivated_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Invalidate cache
        invalidate_user_cache(user_id)
        
        logger.info(f"User deactivated: {user_id}")
        
        return {"message": "User account deactivated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to deactivate user: {e}")
        raise handle_internal_error(f"Failed to deactivate user: {str(e)}")


async def request_password_reset(
    email: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Request password reset."""
    try:
        # Get user by email
        user = await get_user_by_email(db, email)
        
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, a password reset link has been sent"}
        
        # Generate reset token
        reset_token = generate_secure_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        # Store reset token (in real implementation, this would be in a separate table)
        user.password_reset_token = reset_token
        user.password_reset_expires = reset_expires
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # In real implementation, send email here
        logger.info(f"Password reset requested for user: {user.id}")
        
        return {"message": "If the email exists, a password reset link has been sent"}
    
    except Exception as e:
        logger.error(f"Failed to request password reset: {e}")
        raise handle_internal_error(f"Failed to request password reset: {str(e)}")


async def confirm_password_reset(
    token: str,
    new_password: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Confirm password reset with token."""
    try:
        # Find user with valid reset token
        query = select(User).where(
            and_(
                User.password_reset_token == token,
                User.password_reset_expires > datetime.utcnow()
            )
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise handle_unauthorized_error("Invalid or expired reset token")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Invalidate cache
        invalidate_user_cache(str(user.id))
        
        logger.info(f"Password reset confirmed for user: {user.id}")
        
        return {"message": "Password reset successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to confirm password reset: {e}")
        raise handle_internal_error(f"Failed to confirm password reset: {str(e)}")


async def verify_email(
    token: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Verify user email with token."""
    try:
        # Find user with verification token
        query = select(User).where(
            and_(
                User.email_verification_token == token,
                User.email_verification_expires > datetime.utcnow()
            )
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise handle_unauthorized_error("Invalid or expired verification token")
        
        # Mark email as verified
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        user.verified_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Invalidate cache
        invalidate_user_cache(str(user.id))
        
        logger.info(f"Email verified for user: {user.id}")
        
        return {"message": "Email verified successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to verify email: {e}")
        raise handle_internal_error(f"Failed to verify email: {str(e)}")


async def create_user_session(
    user_id: str,
    device_info: Dict[str, Any],
    ip_address: str,
    user_agent: str,
    db: AsyncSession
) -> UserSession:
    """Create a new user session."""
    try:
        # Generate session token
        session_token = generate_secure_token()
        refresh_token = generate_secure_token()
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        # Create session
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            last_activity=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"User session created: {session.id} for user {user_id}")
        
        return session
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create user session: {e}")
        raise handle_internal_error(f"Failed to create user session: {str(e)}")


async def get_user_sessions(
    user_id: str,
    db: AsyncSession
) -> list[UserSession]:
    """Get user active sessions."""
    try:
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            )
        ).order_by(UserSession.last_activity.desc())
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        return sessions
    
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise handle_internal_error(f"Failed to get user sessions: {str(e)}")


async def revoke_user_session(
    session_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Revoke a specific user session."""
    try:
        query = select(UserSession).where(
            and_(
                UserSession.id == session_id,
                UserSession.user_id == user_id
            )
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            raise handle_not_found_error("Session", session_id)
        
        # Revoke session
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"User session revoked: {session_id}")
        
        return {"message": "Session revoked successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to revoke user session: {e}")
        raise handle_internal_error(f"Failed to revoke user session: {str(e)}")


async def revoke_all_user_sessions(
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Revoke all user sessions."""
    try:
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        )
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # Revoke all sessions
        for session in sessions:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"All user sessions revoked for user: {user_id}")
        
        return {"message": "All sessions revoked successfully"}
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to revoke all user sessions: {e}")
        raise handle_internal_error(f"Failed to revoke all user sessions: {str(e)}")


async def get_user_activity(
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get user activity log."""
    try:
        # This would implement activity logging logic
        # For now, returning placeholder data
        return {
            "activities": [
                {
                    "id": "activity-1",
                    "type": "document_created",
                    "description": "Created document 'My Document'",
                    "timestamp": "2023-01-01T12:00:00Z",
                    "metadata": {"document_id": "doc-1"}
                }
            ],
            "total": 1,
            "page": page,
            "size": size,
            "pages": 1
        }
    
    except Exception as e:
        logger.error(f"Failed to get user activity: {e}")
        raise handle_internal_error(f"Failed to get user activity: {str(e)}")


async def search_users(
    query: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search users by name, username, or email."""
    try:
        # Build search query
        search_filter = or_(
            User.full_name.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%"),
            User.email.ilike(f"%{query}%")
        )
        
        db_query = select(User).where(
            and_(
                search_filter,
                User.is_active == True,
                User.is_verified == True
            )
        ).order_by(User.full_name)
        
        # Get total count
        count_query = select(func.count()).select_from(db_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        db_query = db_query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(db_query)
        users = result.scalars().all()
        
        user_responses = [UserResponse.from_orm(user) for user in users]
        
        return {
            "users": user_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to search users: {e}")
        raise handle_internal_error(f"Failed to search users: {str(e)}")




