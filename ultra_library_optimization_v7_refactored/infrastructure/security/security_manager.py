#!/usr/bin/env python3
"""
Advanced Security Manager - Infrastructure Layer
==============================================

Enterprise-grade security implementation with JWT authentication,
RBAC, rate limiting, and comprehensive security features.
"""

import asyncio
import hashlib
import hmac
import jwt
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type
from functools import wraps
import secrets
import bcrypt

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Permission(Enum):
    """System permissions."""
    READ_POSTS = "read_posts"
    CREATE_POSTS = "create_posts"
    UPDATE_POSTS = "update_posts"
    DELETE_POSTS = "delete_posts"
    OPTIMIZE_POSTS = "optimize_posts"
    PUBLISH_POSTS = "publish_posts"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM = "manage_system"
    ADMIN = "admin"


class Role(Enum):
    """User roles with associated permissions."""
    GUEST = "guest"
    USER = "user"
    EDITOR = "editor"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class User:
    """User entity with security information."""
    
    user_id: str
    username: str
    email: str
    roles: List[Role] = field(default_factory=list)
    permissions: List[Permission] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_hash: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions
    
    def has_role(self, role: Role) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False


@dataclass
class SecurityEvent:
    """Security event for auditing."""
    
    event_id: str
    event_type: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    severity: SecurityLevel = SecurityLevel.MEDIUM
    success: bool = True


class RateLimiter:
    """Advanced rate limiter with sliding window."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
        self._logger = logging.getLogger(__name__)
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key."""
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for the key."""
        now = time.time()
        
        if key not in self.requests:
            return self.max_requests
        
        # Remove old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < self.window_seconds
        ]
        
        return max(0, self.max_requests - len(self.requests[key]))


class JWTManager:
    """JWT token management with advanced features."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self._logger = logging.getLogger(__name__)
        self._blacklisted_tokens: Set[str] = set()
    
    def create_token(self, user: User, expires_delta: timedelta = None) -> str:
        """Create a JWT token for the user."""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": user.user_id,
            "username": user.username,
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "permissions": [perm.value for perm in user.permissions],
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)  # JWT ID for blacklisting
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self._logger.info(f"Created JWT token for user {user.user_id}")
        
        return token
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token."""
        try:
            # Check if token is blacklisted
            if token in self._blacklisted_tokens:
                raise jwt.InvalidTokenError("Token is blacklisted")
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        
        except jwt.ExpiredSignatureError:
            self._logger.warning("JWT token expired")
            raise jwt.ExpiredSignatureError("Token has expired")
        
        except jwt.InvalidTokenError as e:
            self._logger.warning(f"Invalid JWT token: {e}")
            raise jwt.InvalidTokenError("Invalid token")
    
    def blacklist_token(self, token: str) -> None:
        """Add token to blacklist."""
        self._blacklisted_tokens.add(token)
        self._logger.info("Token added to blacklist")
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return token in self._blacklisted_tokens


class PasswordManager:
    """Advanced password management with security features."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength."""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password must be at least 8 characters long")
        
        # Uppercase check
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one uppercase letter")
        
        # Lowercase check
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one lowercase letter")
        
        # Digit check
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one digit")
        
        # Special character check
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one special character")
        
        # Strength assessment
        if score >= 5:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "score": score,
            "strength": strength,
            "feedback": feedback,
            "is_valid": score >= 3
        }


class SecurityManager:
    """
    Advanced security manager with enterprise-grade features.
    
    Features:
    - JWT authentication and authorization
    - Role-based access control (RBAC)
    - Advanced rate limiting
    - Password security
    - Security event logging
    - Account lockout protection
    - Token blacklisting
    - Comprehensive auditing
    """
    
    def __init__(self, jwt_secret: str):
        self.jwt_manager = JWTManager(jwt_secret)
        self.password_manager = PasswordManager()
        self.rate_limiter = RateLimiter()
        self._users: Dict[str, User] = {}
        self._security_events: List[SecurityEvent] = []
        self._logger = logging.getLogger(__name__)
        
        # Security configuration
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_timeout = timedelta(hours=24)
        
        # Initialize default roles and permissions
        self._initialize_roles()
    
    def _initialize_roles(self) -> None:
        """Initialize default roles and permissions."""
        role_permissions = {
            Role.GUEST: [Permission.READ_POSTS],
            Role.USER: [
                Permission.READ_POSTS,
                Permission.CREATE_POSTS,
                Permission.OPTIMIZE_POSTS
            ],
            Role.EDITOR: [
                Permission.READ_POSTS,
                Permission.CREATE_POSTS,
                Permission.UPDATE_POSTS,
                Permission.OPTIMIZE_POSTS,
                Permission.PUBLISH_POSTS
            ],
            Role.MANAGER: [
                Permission.READ_POSTS,
                Permission.CREATE_POSTS,
                Permission.UPDATE_POSTS,
                Permission.DELETE_POSTS,
                Permission.OPTIMIZE_POSTS,
                Permission.PUBLISH_POSTS,
                Permission.VIEW_ANALYTICS
            ],
            Role.ADMIN: [
                Permission.READ_POSTS,
                Permission.CREATE_POSTS,
                Permission.UPDATE_POSTS,
                Permission.DELETE_POSTS,
                Permission.OPTIMIZE_POSTS,
                Permission.PUBLISH_POSTS,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_USERS
            ],
            Role.SUPER_ADMIN: [
                Permission.READ_POSTS,
                Permission.CREATE_POSTS,
                Permission.UPDATE_POSTS,
                Permission.DELETE_POSTS,
                Permission.OPTIMIZE_POSTS,
                Permission.PUBLISH_POSTS,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_USERS,
                Permission.MANAGE_SYSTEM,
                Permission.ADMIN
            ]
        }
        
        self.role_permissions = role_permissions
    
    def register_user(self, username: str, email: str, password: str, 
                     roles: List[Role] = None) -> User:
        """Register a new user."""
        # Validate password strength
        password_validation = self.password_manager.validate_password_strength(password)
        if not password_validation["is_valid"]:
            raise ValueError(f"Password too weak: {password_validation['feedback']}")
        
        # Check if user already exists
        if any(u.username == username or u.email == email for u in self._users.values()):
            raise ValueError("Username or email already exists")
        
        # Create user
        user_id = secrets.token_urlsafe(16)
        password_hash = self.password_manager.hash_password(password)
        
        if roles is None:
            roles = [Role.USER]
        
        # Get permissions for roles
        permissions = []
        for role in roles:
            if role in self.role_permissions:
                permissions.extend(self.role_permissions[role])
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=list(set(permissions)),  # Remove duplicates
            password_hash=password_hash
        )
        
        self._users[user_id] = user
        
        # Log security event
        self._log_security_event(
            "user_registered",
            user_id=user_id,
            success=True,
            details={"username": username, "email": email, "roles": [r.value for r in roles]}
        )
        
        self._logger.info(f"Registered new user: {username}")
        return user
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None) -> Optional[str]:
        """Authenticate a user and return JWT token."""
        # Find user
        user = None
        for u in self._users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user:
            self._log_security_event(
                "login_failed",
                ip_address=ip_address,
                success=False,
                details={"username": username, "reason": "user_not_found"}
            )
            return None
        
        # Check if account is locked
        if user.is_locked():
            self._log_security_event(
                "login_failed",
                user_id=user.user_id,
                ip_address=ip_address,
                success=False,
                details={"reason": "account_locked"}
            )
            raise ValueError("Account is locked due to too many failed attempts")
        
        # Verify password
        if not self.password_manager.verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.locked_until = datetime.utcnow() + self.lockout_duration
                self._log_security_event(
                    "account_locked",
                    user_id=user.user_id,
                    ip_address=ip_address,
                    success=False,
                    details={"failed_attempts": user.failed_login_attempts}
                )
            
            self._log_security_event(
                "login_failed",
                user_id=user.user_id,
                ip_address=ip_address,
                success=False,
                details={"failed_attempts": user.failed_login_attempts}
            )
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        
        # Create JWT token
        token = self.jwt_manager.create_token(user, self.session_timeout)
        
        # Log security event
        self._log_security_event(
            "login_successful",
            user_id=user.user_id,
            ip_address=ip_address,
            success=True
        )
        
        self._logger.info(f"User {username} authenticated successfully")
        return token
    
    def validate_token(self, token: str) -> Optional[User]:
        """Validate JWT token and return user."""
        try:
            payload = self.jwt_manager.decode_token(token)
            user_id = payload.get("sub")
            
            if user_id not in self._users:
                return None
            
            user = self._users[user_id]
            
            # Check if user is still active
            if not user.is_active:
                return None
            
            return user
        
        except jwt.InvalidTokenError:
            return None
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return user.has_permission(permission)
    
    def check_role(self, user: User, role: Role) -> bool:
        """Check if user has a specific role."""
        return user.has_role(role)
    
    def rate_limit_check(self, key: str) -> bool:
        """Check rate limiting for a key."""
        return self.rate_limiter.is_allowed(key)
    
    def logout(self, token: str) -> None:
        """Logout user by blacklisting token."""
        self.jwt_manager.blacklist_token(token)
        self._log_security_event(
            "logout",
            success=True,
            details={"token_blacklisted": True}
        )
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password."""
        if user_id not in self._users:
            return False
        
        user = self._users[user_id]
        
        # Verify old password
        if not self.password_manager.verify_password(old_password, user.password_hash):
            self._log_security_event(
                "password_change_failed",
                user_id=user_id,
                success=False,
                details={"reason": "incorrect_old_password"}
            )
            return False
        
        # Validate new password strength
        password_validation = self.password_manager.validate_password_strength(new_password)
        if not password_validation["is_valid"]:
            self._log_security_event(
                "password_change_failed",
                user_id=user_id,
                success=False,
                details={"reason": "weak_password", "feedback": password_validation["feedback"]}
            )
            return False
        
        # Update password
        user.password_hash = self.password_manager.hash_password(new_password)
        
        self._log_security_event(
            "password_changed",
            user_id=user_id,
            success=True
        )
        
        self._logger.info(f"Password changed for user {user_id}")
        return True
    
    def update_user_roles(self, user_id: str, roles: List[Role]) -> bool:
        """Update user roles."""
        if user_id not in self._users:
            return False
        
        user = self._users[user_id]
        old_roles = user.roles.copy()
        
        # Update roles
        user.roles = roles
        
        # Update permissions
        permissions = []
        for role in roles:
            if role in self.role_permissions:
                permissions.extend(self.role_permissions[role])
        
        user.permissions = list(set(permissions))
        
        self._log_security_event(
            "roles_updated",
            user_id=user_id,
            success=True,
            details={
                "old_roles": [r.value for r in old_roles],
                "new_roles": [r.value for r in roles]
            }
        )
        
        self._logger.info(f"Roles updated for user {user_id}")
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self._users.values())
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if user_id not in self._users:
            return False
        
        user = self._users[user_id]
        del self._users[user_id]
        
        self._log_security_event(
            "user_deleted",
            user_id=user_id,
            success=True,
            details={"username": user.username, "email": user.email}
        )
        
        self._logger.info(f"User {user_id} deleted")
        return True
    
    def _log_security_event(self, event_type: str, user_id: str = None,
                           ip_address: str = None, success: bool = True,
                           details: Dict[str, Any] = None) -> None:
        """Log a security event."""
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            success=success,
            details=details or {}
        )
        
        self._security_events.append(event)
        
        # Log to logger
        if success:
            self._logger.info(f"Security event: {event_type} - {details}")
        else:
            self._logger.warning(f"Security event: {event_type} - {details}")
    
    def get_security_events(self, user_id: str = None, 
                           event_type: str = None,
                           start_time: datetime = None,
                           end_time: datetime = None) -> List[SecurityEvent]:
        """Get security events with filtering."""
        events = self._security_events
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        return sorted(events, key=lambda e: e.timestamp, reverse=True)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get security metrics."""
        total_users = len(self._users)
        active_users = len([u for u in self._users.values() if u.is_active])
        locked_users = len([u for u in self._users.values() if u.is_locked()])
        
        recent_events = [
            e for e in self._security_events
            if e.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        failed_logins = len([e for e in recent_events 
                           if e.event_type == "login_failed"])
        successful_logins = len([e for e in recent_events 
                               if e.event_type == "login_successful"])
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "locked_users": locked_users,
            "recent_events": len(recent_events),
            "failed_logins_24h": failed_logins,
            "successful_logins_24h": successful_logins,
            "blacklisted_tokens": len(self.jwt_manager._blacklisted_tokens)
        }


# FastAPI integration
security = HTTPBearer()


def get_current_user(token: HTTPAuthorizationCredentials = Depends(security),
                    security_manager: SecurityManager = None) -> User:
    """FastAPI dependency to get current user from JWT token."""
    if not security_manager:
        raise HTTPException(status_code=500, detail="Security manager not configured")
    
    user = security_manager.validate_token(token.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    return user


def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented in the actual FastAPI route
            # For now, just return the function
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """Decorator to require specific role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented in the actual FastAPI route
            # For now, just return the function
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Decorator to apply rate limiting."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would be implemented in the actual FastAPI route
            # For now, just return the function
            return await func(*args, **kwargs)
        return wrapper
    return decorator 