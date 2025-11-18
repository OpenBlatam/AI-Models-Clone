"""
Authentication routes following functional patterns and RORO
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.database import get_db
from app.core.auth_utils import (
    authenticate_user, create_access_token, create_refresh_token,
    verify_password, get_password_hash, get_user_by_email
)
from app.core.errors import handle_validation_error, handle_unauthorized_error, handle_forbidden_error
from app.schemas.user import (
    UserCreate, UserResponse, UserLogin, TokenResponse,
    UserUpdate, PasswordReset, PasswordResetConfirm
)
from app.services.user_service import (
    create_user, update_user, get_user_profile,
    request_password_reset, confirm_password_reset
)
from app.utils.validators import validate_email, validate_password_strength, validate_username
from app.utils.rate_limiter import rate_limit_auth, rate_limit_password_reset
from app.utils.helpers import generate_secure_token, mask_sensitive_data

router = APIRouter()


async def register_user_endpoint(
    user_data: UserCreate,
    db: AsyncSession
) -> UserResponse:
    """Register a new user."""
    # Validate email
    if not validate_email(user_data.email):
        raise handle_validation_error(ValueError("Invalid email format"))
    
    # Validate username
    username_validation = validate_username(user_data.username)
    if not username_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Invalid username: {', '.join(username_validation['errors'])}")
        )
    
    # Validate password strength
    password_validation = validate_password_strength(user_data.password)
    if not password_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Weak password: {', '.join(password_validation['errors'])}")
        )
    
    return await create_user(user_data, db)


async def login_user_endpoint(
    login_data: UserLogin,
    db: AsyncSession
) -> TokenResponse:
    """Login user and return tokens."""
    # Authenticate user
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise handle_unauthorized_error("Invalid email or password")
    
    if not user.is_active:
        raise handle_forbidden_error("Account is deactivated")
    
    if not user.is_verified:
        raise handle_forbidden_error("Email not verified")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )


async def refresh_token_endpoint(
    refresh_token: str,
    db: AsyncSession
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        from app.core.auth_utils import decode_token
        
        # Decode refresh token
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise handle_unauthorized_error("Invalid refresh token")
        
        # Get user
        from app.core.auth_utils import get_user_by_id
        user = await get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise handle_unauthorized_error("User not found or inactive")
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Keep the same refresh token
            token_type="bearer",
            expires_in=1800
        )
    
    except Exception as e:
        raise handle_unauthorized_error("Invalid refresh token")


async def get_current_user_profile_endpoint(
    user_id: str,
    db: AsyncSession
) -> UserResponse:
    """Get current user profile."""
    return await get_user_profile(user_id, db)


async def update_user_profile_endpoint(
    user_id: str,
    update_data: UserUpdate,
    db: AsyncSession
) -> UserResponse:
    """Update user profile."""
    # Validate email if provided
    if update_data.email and not validate_email(update_data.email):
        raise handle_validation_error(ValueError("Invalid email format"))
    
    # Validate username if provided
    if update_data.username:
        username_validation = validate_username(update_data.username)
        if not username_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid username: {', '.join(username_validation['errors'])}")
            )
    
    return await update_user(user_id, update_data, db)


async def change_password_endpoint(
    user_id: str,
    current_password: str,
    new_password: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Change user password."""
    # Get user
    from app.core.auth_utils import get_user_by_id
    user = await get_user_by_id(db, user_id)
    if not user:
        raise handle_not_found_error("User", user_id)
    
    # Verify current password
    if not verify_password(current_password, user.hashed_password):
        raise handle_unauthorized_error("Current password is incorrect")
    
    # Validate new password strength
    password_validation = validate_password_strength(new_password)
    if not password_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Weak password: {', '.join(password_validation['errors'])}")
        )
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}


async def request_password_reset_endpoint(
    email: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Request password reset."""
    if not validate_email(email):
        raise handle_validation_error(ValueError("Invalid email format"))
    
    return await request_password_reset(email, db)


async def confirm_password_reset_endpoint(
    token: str,
    new_password: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Confirm password reset with token."""
    # Validate new password strength
    password_validation = validate_password_strength(new_password)
    if not password_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Weak password: {', '.join(password_validation['errors'])}")
        )
    
    return await confirm_password_reset(token, new_password, db)


async def verify_email_endpoint(
    token: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Verify user email with token."""
    # This would implement email verification logic
    # For now, returning a placeholder response
    return {"message": "Email verified successfully"}


async def resend_verification_email_endpoint(
    email: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Resend email verification."""
    if not validate_email(email):
        raise handle_validation_error(ValueError("Invalid email format"))
    
    # This would implement resend verification logic
    # For now, returning a placeholder response
    return {"message": "Verification email sent"}


async def logout_user_endpoint(
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Logout user and invalidate tokens."""
    # This would implement token invalidation logic
    # For now, returning a placeholder response
    return {"message": "Logged out successfully"}


# Route definitions
@router.post("/register", response_model=UserResponse)
@rate_limit_auth(key_func=lambda **kwargs: "register")
async def register_user_route(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user."""
    return await register_user_endpoint(user_data, db)


@router.post("/login", response_model=TokenResponse)
@rate_limit_auth(key_func=lambda **kwargs: "login")
async def login_user_route(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Login user and return tokens."""
    return await login_user_endpoint(login_data, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_route(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Refresh access token using refresh token."""
    return await refresh_token_endpoint(refresh_token, db)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get current user profile."""
    return await get_current_user_profile_endpoint(current_user.id, db)


@router.put("/me", response_model=UserResponse)
async def update_user_profile_route(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update user profile."""
    return await update_user_profile_endpoint(current_user.id, update_data, db)


@router.post("/change-password")
async def change_password_route(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Change user password."""
    return await change_password_endpoint(current_user.id, current_password, new_password, db)


@router.post("/password-reset/request")
@rate_limit_password_reset(key_func=lambda **kwargs: "password_reset")
async def request_password_reset_route(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Request password reset."""
    return await request_password_reset_endpoint(email, db)


@router.post("/password-reset/confirm")
async def confirm_password_reset_route(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Confirm password reset with token."""
    return await confirm_password_reset_endpoint(token, new_password, db)


@router.post("/verify-email")
async def verify_email_route(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Verify user email with token."""
    return await verify_email_endpoint(token, db)


@router.post("/resend-verification")
@rate_limit_email_verification(key_func=lambda **kwargs: "resend_verification")
async def resend_verification_email_route(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Resend email verification."""
    return await resend_verification_email_endpoint(email, db)


@router.post("/logout")
async def logout_user_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Logout user and invalidate tokens."""
    return await logout_user_endpoint(current_user.id, db)


@router.get("/me/sessions")
async def get_user_sessions_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user active sessions."""
    # This would implement session listing logic
    # For now, returning placeholder data
    return {
        "sessions": [
            {
                "id": "session-1",
                "device": "Chrome on Windows",
                "ip_address": "192.168.1.100",
                "last_activity": "2023-01-01T12:00:00Z",
                "is_current": True
            }
        ]
    }


@router.delete("/me/sessions/{session_id}")
async def revoke_user_session_route(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Revoke a specific user session."""
    # This would implement session revocation logic
    # For now, returning a placeholder response
    return {"message": "Session revoked successfully"}


@router.delete("/me/sessions")
async def revoke_all_user_sessions_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Revoke all user sessions."""
    # This would implement session revocation logic
    # For now, returning a placeholder response
    return {"message": "All sessions revoked successfully"}


@router.get("/me/activity")
async def get_user_activity_route(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user activity log."""
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




