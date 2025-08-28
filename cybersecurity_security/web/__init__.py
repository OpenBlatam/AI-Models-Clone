from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .web_security import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Web Application Security Module

Provides web application security features including FastAPI integration and JWT authentication.
"""

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