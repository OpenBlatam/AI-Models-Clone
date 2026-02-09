from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS = 60

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Web Application Security

Provides web application security features including FastAPI integration and JWT authentication.
"""


class AppConfig(BaseModel):
    """Pydantic model for app configuration."""
    app_name: str = Field(default="SecureAPI", description="Application name")
    secret_key: str = Field(..., min_length=32, description="Secret key for JWT")
    allowed_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    
    @validator('secret_key')
    def validate_secret_key(cls, v) -> bool:
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

class JWTConfig(BaseModel):
    """Pydantic model for JWT configuration."""
    secret_key: str = Field(..., min_length=32)
    algorithm: str = Field(default="HS256", regex="^(HS256|HS384|HS512|RS256|RS384|RS512)$")
    token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    
    @validator('secret_key')
    def validate_secret_key(cls, v) -> bool:
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

class UserData(BaseModel):
    """Pydantic model for user data."""
    user_id: str = Field(..., description="User identifier")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    roles: List[str] = Field(default_factory=list, description="User roles")

class TokenData(BaseModel):
    """Pydantic model for token data."""
    token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    roles: List[str]

async def create_secure_fastapi_app(data: AppConfig) -> Dict[str, Any]:
    """Create secure FastAPI application (CPU-bound setup)."""
    app_name = data.app_name
    secret_key = data.secret_key
    allowed_origins = data.allowed_origins
    
    app = FastAPI(title=app_name)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        
    """add_security_headers function."""
response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
    
    return {
        "app": app,
        "app_name": app_name,
        "secret_key": secret_key,
        "security_headers_enabled": True,
        "cors_enabled": True
    }

def create_jwt_authentication(data: JWTConfig) -> Dict[str, Any]:
    """Create JWT authentication system (CPU-bound setup)."""
    secret_key = data.secret_key
    algorithm = data.algorithm
    token_expire_minutes = data.token_expire_minutes
    
    security = HTTPBearer()
    
    def verify_token(credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        try:
            payload = jwt.decode(credentials.credentials, secret_key, algorithms=[algorithm])
            return {
                "is_valid": True,
                "payload": payload,
                "user_id": payload.get("sub"),
                "expires_at": payload.get("exp")
            }
        except jwt.ExpiredSignatureError:
            return {"is_valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"is_valid": False, "error": "Invalid token"}
    
    def create_token(user_data: UserData) -> TokenData:
        payload = {
            "sub": user_data.user_id,
            "username": user_data.username,
            "roles": user_data.roles,
            "exp": datetime.utcnow() + timedelta(minutes=token_expire_minutes)
        }
        token = jwt.encode(payload, secret_key, algorithm=algorithm)
        
        return TokenData(
            token=token,
            expires_in=token_expire_minutes * 60,
            user_id=user_data.user_id,
            username=user_data.username,
            roles=user_data.roles
        )
    
    return {
        "verify_token": verify_token,
        "create_token": create_token,
        "security": security,
        "algorithm": algorithm,
        "token_expire_minutes": token_expire_minutes
    } 