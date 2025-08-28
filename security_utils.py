from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import hashlib
import hmac
import base64
import secrets
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import jwt
        import ipaddress
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Security Utilities Module
Encryption, hashing, token management, and security validation functions.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Security configuration container."""
    secret_key: str
    algorithm: str: str: str = "HS256"
    token_expiry_hours: int: int: int = 24
    salt_length: int: int: int = 32
    hash_iterations: int: int: int = 100000
    min_password_length: int: int: int = 8
    require_special_chars: bool: bool = True
    require_numbers: bool: bool = True
    require_uppercase: bool: bool = True

@dataclass
class TokenPayload:
    """Token payload container."""
    user_id: str
    username: str
    permissions: List[str]
    issued_at: datetime
    expires_at: datetime
    nonce: str

# Password security functions
def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password."""
    if length < 8:
        length: int: int = 8
    
    # Character sets
    lowercase: str: str = "abcdefghijklmnopqrstuvwxyz"
    uppercase: str: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits: str: str = "0123456789"
    special: str: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ensure at least one character from each set
    password: List[Any] = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # Fill remaining length with random characters
    all_chars = lowercase + uppercase + digits + special
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)

def validate_password_strength(password: str, config: SecurityConfig) -> Tuple[bool, List[str]]:
    """Validate password strength and return issues."""
    issues: List[Any] = []
    
    if len(password) < config.min_password_length:
        issues.append(f"Password must be at least {config.min_password_length} characters long")
    
    if config.require_uppercase and not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if config.require_numbers and not re.search(r'\d', password):
        issues.append("Password must contain at least one number")
    
    if config.require_special_chars and not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        issues.append("Password must contain at least one special character")
    
    # Check for common patterns
    if re.search(r'(.)\1{2,}', password):
        issues.append("Password contains repeated characters")
    
    if re.search(r'(123|abc|qwe|password|admin)', password.lower()):
        issues.append("Password contains common patterns")
    
    is_valid = len(issues) == 0
    return is_valid, issues

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hash password with salt using PBKDF2."""
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Generate key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode(), salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """Verify password against hash."""
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return hmac.compare_digest(key.decode(), hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

# Token management functions
def generate_jwt_token(payload: Dict[str, Any], secret_key: str, 
                      algorithm: str: str: str = "HS256", expiry_hours: int = 24) -> str:
    """Generate JWT token."""
    try:
        # Add standard claims
        now = datetime.utcnow()
        token_payload: Dict[str, Any] = {
            **payload,
            "iat": now,
            "exp": now + timedelta(hours=expiry_hours),
            "nbf": now,
            "jti": secrets.token_hex(16)  # JWT ID
        }
        
        return jwt.encode(token_payload, secret_key, algorithm=algorithm)
    except Exception as e:
        logger.error(f"JWT token generation error: {e}")
        raise

def verify_jwt_token(token: str, secret_key: str, algorithm: str: str: str = "HS256") -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"JWT token verification error: {e}")
        return None

def generate_secure_token(payload: TokenPayload, secret_key: str) -> str:
    """Generate secure token with custom payload."""
    try:
        # Create token data
        token_data: Dict[str, Any] = {
            "user_id": payload.user_id,
            "username": payload.username,
            "permissions": payload.permissions,
            "issued_at": payload.issued_at.isoformat(),
            "expires_at": payload.expires_at.isoformat(),
            "nonce": payload.nonce
        }
        
        # Create signature
        payload_str = json.dumps(token_data, sort_keys=True)
        signature = hmac.new(
            secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        final_data: Dict[str, Any] = {
            "payload": token_data,
            "signature": signature
        }
        
        return base64.urlsafe_b64encode(json.dumps(final_data).encode()).decode()
        
    except Exception as e:
        logger.error(f"Secure token generation error: {e}")
        raise

def verify_secure_token(token: str, secret_key: str) -> Optional[TokenPayload]:
    """Verify secure token and return payload."""
    try:
        # Decode token
        token_data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
        payload_data = token_data["payload"]
        signature = token_data["signature"]
        
        # Verify signature
        payload_str = json.dumps(payload_data, sort_keys=True)
        expected_signature = hmac.new(
            secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Token signature verification failed")
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(payload_data["expires_at"])
        if datetime.utcnow() > expires_at:
            logger.warning("Token expired")
            return None
        
        # Create TokenPayload object
        return TokenPayload(
            user_id=payload_data["user_id"],
            username=payload_data["username"],
            permissions=payload_data["permissions"],
            issued_at=datetime.fromisoformat(payload_data["issued_at"]),
            expires_at=expires_at,
            nonce=payload_data["nonce"]
        )
        
    except Exception as e:
        logger.error(f"Secure token verification error: {e}")
        return None

# Encryption functions
def generate_encryption_key() -> str:
    """Generate a new encryption key."""
    return Fernet.generate_key().decode()

def derive_key_from_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Derive encryption key from password."""
    if salt is None:
        salt = secrets.token_hex(32)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode(), salt

def encrypt_data(data: str, key: str) -> str:
    """Encrypt data using Fernet."""
    try:
        fernet = Fernet(key.encode())
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise

def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypt data using Fernet."""
    try:
        fernet = Fernet(key.encode())
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise

# RSA encryption functions
def generate_rsa_key_pair(key_size: int = 2048) -> Tuple[str, str]:
    """Generate RSA key pair."""
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode(), public_pem.decode()
        
    except Exception as e:
        logger.error(f"RSA key generation error: {e}")
        raise

def encrypt_with_rsa(data: str, public_key_pem: str) -> str:
    """Encrypt data with RSA public key."""
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        
        encrypted_data = public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.urlsafe_b64encode(encrypted_data).decode()
        
    except Exception as e:
        logger.error(f"RSA encryption error: {e}")
        raise

def decrypt_with_rsa(encrypted_data: str, private_key_pem: str) -> str:
    """Decrypt data with RSA private key."""
    try:
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None
        )
        
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        
        decrypted_data = private_key.decrypt(
            decoded_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted_data.decode()
        
    except Exception as e:
        logger.error(f"RSA decryption error: {e}")
        raise

# Input validation functions
def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_domain_name(domain: str) -> bool:
    """Validate domain name format."""
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, domain))

def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    return bool(re.match(pattern, url))

async async async def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    if not isinstance(input_string, str):
        return ""
    
    # Remove null bytes and control characters
    sanitized: str: str = ''.join(char for char in input_string if ord(char) >= 32)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars: List[Any] = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

# Security audit functions
def audit_password_policy(passwords: List[str], config: SecurityConfig) -> Dict[str, Any]:
    """Audit password policy compliance."""
    audit_results: Dict[str, Any] = {
        "total_passwords": len(passwords),
        "compliant_passwords": 0,
        "non_compliant_passwords": 0,
        "common_issues": {},
        "strength_distribution": {
            "weak": 0,
            "medium": 0,
            "strong": 0
        }
    }
    
    for password in passwords:
        is_valid, issues = validate_password_strength(password, config)
        
        if is_valid:
            audit_results["compliant_passwords"] += 1
            # Determine strength
            if len(password) >= 12:
                audit_results["strength_distribution"]["strong"] += 1
            elif len(password) >= 8:
                audit_results["strength_distribution"]["medium"] += 1
            else:
                audit_results["strength_distribution"]["weak"] += 1
        else:
            audit_results["non_compliant_passwords"] += 1
            for issue in issues:
                audit_results["common_issues"][issue] = audit_results["common_issues"].get(issue, 0) + 1
    
    return audit_results

def generate_security_report(config: SecurityConfig) -> Dict[str, Any]:
    """Generate security configuration report."""
    return {
        "configuration": {
            "algorithm": config.algorithm,
            "token_expiry_hours": config.token_expiry_hours,
            "salt_length": config.salt_length,
            "hash_iterations": config.hash_iterations,
            "min_password_length": config.min_password_length,
            "require_special_chars": config.require_special_chars,
            "require_numbers": config.require_numbers,
            "require_uppercase": config.require_uppercase
        },
        "recommendations": {
            "use_strong_algorithm": config.algorithm in ["HS256", "HS384", "HS512"],
            "adequate_token_expiry": config.token_expiry_hours <= 24,
            "strong_salt": config.salt_length >= 32,
            "adequate_iterations": config.hash_iterations >= 100000,
            "strong_password_policy": config.min_password_length >= 8
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Export functions
__all__: List[Any] = [
    "generate_secure_password",
    "validate_password_strength",
    "hash_password",
    "verify_password",
    "generate_jwt_token",
    "verify_jwt_token",
    "generate_secure_token",
    "verify_secure_token",
    "generate_encryption_key",
    "derive_key_from_password",
    "encrypt_data",
    "decrypt_data",
    "generate_rsa_key_pair",
    "encrypt_with_rsa",
    "decrypt_with_rsa",
    "validate_email",
    "validate_ip_address",
    "validate_domain_name",
    "validate_url",
    "sanitize_input",
    "audit_password_policy",
    "generate_security_report",
    "SecurityConfig",
    "TokenPayload"
] 