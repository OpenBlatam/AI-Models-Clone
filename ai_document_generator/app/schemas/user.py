"""
User schemas for API validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
import uuid


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=50)
    language: str = Field(default="en", max_length=10)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserInDB(UserBase):
    """Schema for user data in database."""
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    notification_settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user response."""
    pass


class UserProfile(User):
    """Schema for user profile with additional information."""
    organization_memberships: List["OrganizationMember"] = []
    document_count: int = 0
    collaboration_count: int = 0


class UserSessionBase(BaseModel):
    """Base schema for user session."""
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class UserSessionCreate(UserSessionBase):
    """Schema for creating user session."""
    pass


class UserSession(UserSessionBase):
    """Schema for user session response."""
    id: uuid.UUID
    user_id: uuid.UUID
    session_token: str
    is_active: bool
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    
    class Config:
        from_attributes = True


class OrganizationMemberBase(BaseModel):
    """Base schema for organization membership."""
    role: str = Field(..., max_length=50)
    permissions: Dict[str, Any] = Field(default_factory=dict)


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for creating organization membership."""
    user_id: uuid.UUID
    organization_id: uuid.UUID


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating organization membership."""
    role: Optional[str] = Field(None, max_length=50)
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationMember(OrganizationMemberBase):
    """Schema for organization membership response."""
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    is_active: bool
    joined_at: datetime
    updated_at: datetime
    user: Optional[User] = None
    organization: Optional["Organization"] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[uuid.UUID] = None
    session_id: Optional[uuid.UUID] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str
    remember_me: bool = False


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    token: str


# Update forward references
UserProfile.model_rebuild()
OrganizationMember.model_rebuild()




