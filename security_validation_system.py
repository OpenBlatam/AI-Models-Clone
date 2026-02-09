#!/usr/bin/env python3
"""
Security Validation System
Comprehensive security validation with input sanitization, authentication, and encryption
"""

import os
import re
import hashlib
import hmac
import base64
import secrets
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
from loguru import logger

class SecurityLevel(Enum):
    """Security levels for validation."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

class ValidationType(Enum):
    """Types of security validation."""
    INPUT_SANITIZATION = "input_sanitization"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    RATE_LIMITING = "rate_limiting"
    SQL_INJECTION = "sql_injection"
    XSS_PROTECTION = "xss_protection"
    CSRF_PROTECTION = "csrf_protection"

@dataclass
class SecurityConfig:
    """Configuration for security validation."""
    security_level: SecurityLevel = SecurityLevel.STRICT
    max_input_length: int = 1000
    min_password_length: int = 12
    password_complexity: bool = True
    session_timeout: int = 3600
    max_login_attempts: int = 5
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    allowed_file_types: List[str] = field(default_factory=lambda: [".txt", ".pdf", ".doc", ".docx"])
    max_file_size: int = 10 * 1024 * 1024  # 10MB

class SecurityValidator:
    """Comprehensive security validation system."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.rate_limit_store: Dict[str, List[float]] = {}
        self.failed_login_attempts: Dict[str, List[float]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize encryption
        if not config.encryption_key:
            config.encryption_key = Fernet.generate_key().decode()
        self.cipher = Fernet(config.encryption_key.encode())
        
        # Initialize JWT secret
        if not config.jwt_secret:
            config.jwt_secret = secrets.token_urlsafe(32)
    
    def sanitize_input(self, input_data: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """Sanitize input data to prevent injection attacks."""
        if isinstance(input_data, str):
            return self._sanitize_string(input_data)
        elif isinstance(input_data, dict):
            return {k: self.sanitize_input(v) for k, v in input_data.items()}
        elif isinstance(input_data, list):
            return [self.sanitize_input(item) for item in input_data]
        else:
            return input_data
    
    def _sanitize_string(self, input_str: str) -> str:
        """Sanitize a string input."""
        if len(input_str) > self.config.max_input_length:
            raise ValueError(f"Input too long. Maximum length: {self.config.max_input_length}")
        
        # Remove null bytes
        sanitized = input_str.replace('\x00', '')
        
        # HTML encoding for XSS protection
        html_entities = {
            '<': '&lt;',
            '>': '&gt;',
            '&': '&amp;',
            '"': '&quot;',
            "'": '&#x27;'
        }
        
        for char, entity in html_entities.items():
            sanitized = sanitized.replace(char, entity)
        
        # SQL injection protection
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\b\s+['\"].*['\"])",
            r"(--|#|/\*|\*/)",
            r"(\b(WAITFOR|DELAY)\b)",
            r"(\b(SLEEP|BENCHMARK)\b)",
        ]
        
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, r"\\\1", sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        errors = []
        
        if len(password) < self.config.min_password_length:
            errors.append(f"Password must be at least {self.config.min_password_length} characters long")
        
        if self.config.password_complexity:
            if not re.search(r"[A-Z]", password):
                errors.append("Password must contain at least one uppercase letter")
            if not re.search(r"[a-z]", password):
                errors.append("Password must contain at least one lowercase letter")
            if not re.search(r"\d", password):
                errors.append("Password must contain at least one digit")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength_score": self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength score (0-100)."""
        score = 0
        
        # Length bonus
        score += min(len(password) * 4, 40)
        
        # Character variety bonus
        if re.search(r"[A-Z]", password):
            score += 10
        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"\d", password):
            score += 10
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 10
        
        # Complexity bonus
        unique_chars = len(set(password))
        score += min(unique_chars * 2, 20)
        
        return min(score, 100)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def generate_jwt_token(self, user_id: str, payload: Dict[str, Any]) -> str:
        """Generate JWT token."""
        payload.update({
            "user_id": user_id,
            "exp": time.time() + self.config.session_timeout,
            "iat": time.time()
        })
        return jwt.encode(payload, self.config.jwt_secret, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=["HS256"])
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"valid": False, "error": "Invalid token"}
    
    def check_rate_limit(self, identifier: str) -> Dict[str, Any]:
        """Check rate limiting for an identifier."""
        current_time = time.time()
        
        if identifier not in self.rate_limit_store:
            self.rate_limit_store[identifier] = []
        
        # Remove old requests outside the window
        window_start = current_time - self.config.rate_limit_window
        self.rate_limit_store[identifier] = [
            req_time for req_time in self.rate_limit_store[identifier]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.rate_limit_store[identifier]) >= self.config.rate_limit_requests:
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": window_start + self.config.rate_limit_window
            }
        
        # Add current request
        self.rate_limit_store[identifier].append(current_time)
        
        return {
            "allowed": True,
            "remaining": self.config.rate_limit_requests - len(self.rate_limit_store[identifier]),
            "reset_time": current_time + self.config.rate_limit_window
        }
    
    def check_login_attempts(self, username: str) -> Dict[str, Any]:
        """Check login attempts for rate limiting."""
        current_time = time.time()
        
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []
        
        # Remove old attempts outside the window
        window_start = current_time - 300  # 5 minutes
        self.failed_login_attempts[username] = [
            attempt_time for attempt_time in self.failed_login_attempts[username]
            if attempt_time > window_start
        ]
        
        attempts_remaining = self.config.max_login_attempts - len(self.failed_login_attempts[username])
        
        return {
            "allowed": attempts_remaining > 0,
            "attempts_remaining": max(0, attempts_remaining),
            "lockout_until": window_start + 300 if attempts_remaining <= 0 else None
        }
    
    def record_failed_login(self, username: str):
        """Record a failed login attempt."""
        if username not in self.failed_login_attempts:
            self.failed_login_attempts[username] = []
        self.failed_login_attempts[username].append(time.time())
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def validate_file_upload(self, filename: str, file_size: int, content_type: str) -> Dict[str, Any]:
        """Validate file upload security."""
        errors = []
        
        # Check file size
        if file_size > self.config.max_file_size:
            errors.append(f"File size exceeds maximum allowed size of {self.config.max_file_size} bytes")
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.config.allowed_file_types:
            errors.append(f"File type {file_ext} is not allowed")
        
        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            errors.append("Invalid filename detected")
        
        # Check content type
        allowed_content_types = [
            "text/plain", "application/pdf", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        if content_type not in allowed_content_types:
            errors.append(f"Content type {content_type} is not allowed")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token."""
        return secrets.token_urlsafe(32)
    
    def verify_csrf_token(self, token: str, stored_token: str) -> bool:
        """Verify CSRF token."""
        return hmac.compare_digest(token, stored_token)
    
    def create_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": time.time(),
            "last_activity": time.time()
        }
        return session_id
    
    def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate session."""
        if session_id not in self.sessions:
            return {"valid": False, "error": "Session not found"}
        
        session = self.sessions[session_id]
        current_time = time.time()
        
        # Check session timeout
        if current_time - session["last_activity"] > self.config.session_timeout:
            del self.sessions[session_id]
            return {"valid": False, "error": "Session expired"}
        
        # Update last activity
        session["last_activity"] = current_time
        
        return {
            "valid": True,
            "user_id": session["user_id"],
            "user_data": session["user_data"]
        }
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session["last_activity"] > self.config.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics."""
        return {
            "active_sessions": len(self.sessions),
            "rate_limited_identifiers": len([
                identifier for identifier, requests in self.rate_limit_store.items()
                if len(requests) >= self.config.rate_limit_requests
            ]),
            "locked_out_users": len([
                username for username, attempts in self.failed_login_attempts.items()
                if len(attempts) >= self.config.max_login_attempts
            ]),
            "security_level": self.config.security_level.value,
            "encryption_enabled": bool(self.config.encryption_key),
            "jwt_enabled": bool(self.config.jwt_secret)
        }

# Security validator instance
security_validator = SecurityValidator(SecurityConfig())

def get_security_validator() -> SecurityValidator:
    """Get the security validator instance."""
    return security_validator

def sanitize_input(input_data: Union[str, Dict, List]) -> Union[str, Dict, List]:
    """Sanitize input data."""
    return security_validator.sanitize_input(input_data)

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength."""
    return security_validator.validate_password(password)

def hash_password(password: str) -> str:
    """Hash password."""
    return security_validator.hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password."""
    return security_validator.verify_password(password, hashed_password)

def generate_jwt_token(user_id: str, payload: Dict[str, Any]) -> str:
    """Generate JWT token."""
    return security_validator.generate_jwt_token(user_id, payload)

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token."""
    return security_validator.verify_jwt_token(token)

def check_rate_limit(identifier: str) -> Dict[str, Any]:
    """Check rate limiting."""
    return security_validator.check_rate_limit(identifier)

def validate_file_upload(filename: str, file_size: int, content_type: str) -> Dict[str, Any]:
    """Validate file upload."""
    return security_validator.validate_file_upload(filename, file_size, content_type) 