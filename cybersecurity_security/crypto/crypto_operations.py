from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any, Literal, Union, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
        import bcrypt
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Cryptographic Operations

Provides secure cryptographic operations including key generation, encryption, and hashing.
"""


class KeyGenerationRequest(BaseModel):
    """Pydantic model for key generation request."""
    key_length: int = Field(default=32, ge=16, le=64, description="Key length in bytes")
    key_type: Literal["bytes", "hex", "urlsafe"] = Field(default="bytes", description="Key encoding type")
    
    @validator('key_length')
    def validate_key_length(cls, v) -> bool:
        if v % 8 != 0:
            raise ValueError("Key length must be divisible by 8")
        return v

class KeyGenerationResult(BaseModel):
    """Pydantic model for key generation result."""
    key: bytes
    encoded_key: str
    key_length: int
    key_type: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class EncryptionRequest(BaseModel):
    """Pydantic model for encryption request."""
    plaintext: str = Field(..., description="Text to encrypt")
    key: Union[str, bytes] = Field(..., description="Encryption key")
    encryption_type: Literal["fernet"] = Field(default="fernet", description="Encryption algorithm")
    
    @validator('plaintext')
    def validate_plaintext(cls, v) -> bool:
        if not v:
            raise ValueError("Plaintext cannot be empty")
        return v

class EncryptionResult(BaseModel):
    """Pydantic model for encryption result."""
    encrypted_data: bytes
    encoded_encrypted: str
    encryption_type: str
    original_length: int
    encrypted_length: int

class DecryptionRequest(BaseModel):
    """Pydantic model for decryption request."""
    encrypted_data: Union[str, bytes] = Field(..., description="Data to decrypt")
    key: Union[str, bytes] = Field(..., description="Decryption key")
    encryption_type: Literal["fernet"] = Field(default="fernet", description="Encryption algorithm")

class DecryptionResult(BaseModel):
    """Pydantic model for decryption result."""
    plaintext: str
    decryption_successful: bool
    encryption_type: str
    error_message: Optional[str] = None

class PasswordHashRequest(BaseModel):
    """Pydantic model for password hashing request."""
    password: str = Field(..., description="Password to hash")
    salt_length: int = Field(default=16, ge=8, le=32, description="Salt length in bytes")
    hash_algorithm: Literal["sha256", "bcrypt"] = Field(default="sha256", description="Hashing algorithm")
    
    @validator('password')
    def validate_password(cls, v) -> bool:
        if not v:
            raise ValueError("Password cannot be empty")
        return v

class PasswordHashResult(BaseModel):
    """Pydantic model for password hash result."""
    password_hash: str
    salt: str
    hash_algorithm: str
    salt_length: int

def generate_secure_key(data: KeyGenerationRequest) -> KeyGenerationResult:
    """Generate secure cryptographic key with RORO pattern."""
    key_length = data.key_length
    key_type = data.key_type
    
    if key_type == "bytes":
        key = secrets.token_bytes(key_length)
        encoded_key = base64.urlsafe_b64encode(key).decode()
    elif key_type == "hex":
        key = secrets.token_bytes(key_length)
        encoded_key = key.hex()
    else:  # urlsafe
        key = secrets.token_urlsafe(key_length).encode()
        encoded_key = key.decode()
    
    return KeyGenerationResult(
        key=key,
        encoded_key=encoded_key,
        key_length=key_length,
        key_type=key_type
    )

def encrypt_data(data: EncryptionRequest) -> EncryptionResult:
    """Encrypt data with RORO pattern."""
    plaintext = data.plaintext
    key = data.key
    encryption_type = data.encryption_type
    
    if encryption_type == "fernet":
        if isinstance(key, str):
            key = base64.urlsafe_b64decode(key)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(plaintext.encode())
        encoded_encrypted = base64.urlsafe_b64encode(encrypted_data).decode()
    
    return EncryptionResult(
        encrypted_data=encrypted_data,
        encoded_encrypted=encoded_encrypted,
        encryption_type=encryption_type,
        original_length=len(plaintext),
        encrypted_length=len(encrypted_data)
    )

def decrypt_data(data: DecryptionRequest) -> DecryptionResult:
    """Decrypt data with RORO pattern."""
    encrypted_data = data.encrypted_data
    key = data.key
    encryption_type = data.encryption_type
    
    try:
        if encryption_type == "fernet":
            if isinstance(key, str):
                key = base64.urlsafe_b64decode(key)
            if isinstance(encrypted_data, str):
                encrypted_data = base64.urlsafe_b64decode(encrypted_data)
            
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            plaintext = decrypted_data.decode()
            
            return DecryptionResult(
                plaintext=plaintext,
                decryption_successful=True,
                encryption_type=encryption_type
            )
    except Exception as e:
        return DecryptionResult(
            plaintext="",
            decryption_successful=False,
            encryption_type=encryption_type,
            error_message=str(e)
        )

def hash_password(data: PasswordHashRequest) -> PasswordHashResult:
    """Hash password with salt using RORO pattern."""
    password = data.password
    salt_length = data.salt_length
    hash_algorithm = data.hash_algorithm
    
    # Generate salt
    salt = secrets.token_hex(salt_length)
    
    # Hash password with salt
    if hash_algorithm == "sha256":
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        password_hash = hash_obj.hexdigest()
    elif hash_algorithm == "bcrypt":
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        salt = ""  # bcrypt includes salt in hash
    
    return PasswordHashResult(
        password_hash=password_hash,
        salt=salt,
        hash_algorithm=hash_algorithm,
        salt_length=salt_length
    ) 