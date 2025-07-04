"""
Authentication Utilities
"""

from typing import List, Optional


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode JWT token (simplified for demo)."""
    # Simplified JWT decoding - in production use proper JWT library
    if token == "demo-token":
        return {
            "sub": "demo_user",
            "permissions": ["video:create", "video:read", "template:read", "template:use", "avatar:create", "avatar:read"]
        }
    return None


def validate_permissions(user_permissions: List[str], required_permissions: List[str]) -> bool:
    """Validate user has required permissions."""
    return all(perm in user_permissions for perm in required_permissions) 