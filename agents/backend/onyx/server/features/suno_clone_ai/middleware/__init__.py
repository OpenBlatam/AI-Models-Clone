"""Middleware para Suno Clone AI"""

from .auth_middleware import (
    AuthMiddleware,
    get_current_user,
    require_auth,
    require_role
)

__all__ = [
    "AuthMiddleware",
    "get_current_user",
    "require_auth",
    "require_role",
]

