"""User models"""

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation model"""
    password: str

class UserResponse(UserBase):
    """User response model"""
    id: int
    
    class Config:
        from_attributes = True
