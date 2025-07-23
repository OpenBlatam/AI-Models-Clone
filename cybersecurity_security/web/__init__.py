"""
Web Application Security Module

Provides web application security features including FastAPI integration and JWT authentication.
"""

from .web_security import (
    AppConfig,
    JWTConfig,
    UserData,
    TokenData,
    create_secure_fastapi_app,
    create_jwt_authentication
)

__all__ = [
    "AppConfig",
    "JWTConfig",
    "UserData",
    "TokenData",
    "create_secure_fastapi_app",
    "create_jwt_authentication"
] 