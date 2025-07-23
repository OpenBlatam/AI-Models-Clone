"""
Crypto Helpers

Provides cryptographic utility functions for security operations.
"""

import asyncio
import hashlib
import hmac
import os
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator
from enum import Enum
import time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.backends import default_backend
import aiofiles

class HashAlgorithm(str, Enum):
    """Enumeration of hash algorithms."""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"
    SHA3_256 = "sha3_256"
    SHA3_512 = "sha3_512"

class EncryptionAlgorithm(str, Enum):
    """Enumeration of encryption algorithms."""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    AES_128_GCM = "aes_128_gcm"
    AES_128_CBC = "aes_128_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"

class CryptoOperation(str, Enum):
    """Enumeration of cryptographic operations."""
    HASH = "hash"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    KEY_GENERATION = "key_generation"
    KEY_DERIVATION = "key_derivation"

class CryptoRequest(BaseModel):
    """Pydantic model for crypto request."""
    operation: CryptoOperation = Field(..., description="Cryptographic operation")
    data: Union[str, bytes] = Field(..., description="Data to process")
    algorithm: Optional[Union[HashAlgorithm, EncryptionAlgorithm]] = Field(None, description="Algorithm to use")
    key: Optional[Union[str, bytes]] = Field(None, description="Encryption/decryption key")
    salt: Optional[Union[str, bytes]] = Field(None, description="Salt for key derivation")
    iterations: int = Field(default=100000, ge=1000, le=1000000, description="PBKDF2 iterations")
    
    @validator('data')
    def validate_data(cls, v):
        if not v:
            raise ValueError("Data cannot be empty")
        return v

class CryptoResult(BaseModel):
    """Pydantic model for crypto result."""
    operation: CryptoOperation
    algorithm: Optional[Union[HashAlgorithm, EncryptionAlgorithm]]
    input_data: Union[str, bytes]
    output_data: Union[str, bytes]
    success: bool
    error_message: Optional[str] = None
    operation_duration: float
    operation_completed_at: float

async def perform_hash_async(data: Union[str, bytes], algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> CryptoResult:
    """Perform hash operation asynchronously."""
    start_time = time.time()
    
    try:
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        # Select hash algorithm
        if algorithm == HashAlgorithm.MD5:
            hash_obj = hashlib.md5()
        elif algorithm == HashAlgorithm.SHA1:
            hash_obj = hashlib.sha1()
        elif algorithm == HashAlgorithm.SHA256:
            hash_obj = hashlib.sha256()
        elif algorithm == HashAlgorithm.SHA512:
            hash_obj = hashlib.sha512()
        elif algorithm == HashAlgorithm.BLAKE2B:
            hash_obj = hashlib.blake2b()
        elif algorithm == HashAlgorithm.BLAKE2S:
            hash_obj = hashlib.blake2s()
        elif algorithm == HashAlgorithm.SHA3_256:
            hash_obj = hashlib.sha3_256()
        elif algorithm == HashAlgorithm.SHA3_512:
            hash_obj = hashlib.sha3_512()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        # Run hash operation in thread pool
        loop = asyncio.get_event_loop()
        hash_result = await loop.run_in_executor(
            None,
            lambda: hash_obj.update(data_bytes) or hash_obj.hexdigest()
        )
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.HASH,
            algorithm=algorithm,
            input_data=data,
            output_data=hash_result,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.HASH,
            algorithm=algorithm,
            input_data=data,
            output_data=b"",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def perform_encryption_async(
    data: Union[str, bytes],
    key: Union[str, bytes],
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
) -> CryptoResult:
    """Perform encryption operation asynchronously."""
    start_time = time.time()
    
    try:
        # Convert inputs to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = key
        
        # Run encryption in thread pool
        loop = asyncio.get_event_loop()
        
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_128_GCM]:
            # GCM mode encryption
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                cipher_key = key_bytes[:32]  # 256 bits
            else:
                cipher_key = key_bytes[:16]  # 128 bits
            
            iv = os.urandom(12)  # 96 bits for GCM
            cipher = Cipher(algorithms.AES(cipher_key), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            ciphertext = await loop.run_in_executor(
                None,
                lambda: encryptor.update(data_bytes) + encryptor.finalize()
            )
            
            tag = encryptor.tag
            result = base64.b64encode(iv + tag + ciphertext).decode('utf-8')
            
        elif algorithm in [EncryptionAlgorithm.AES_256_CBC, EncryptionAlgorithm.AES_128_CBC]:
            # CBC mode encryption
            if algorithm == EncryptionAlgorithm.AES_256_CBC:
                cipher_key = key_bytes[:32]  # 256 bits
            else:
                cipher_key = key_bytes[:16]  # 128 bits
            
            iv = os.urandom(16)  # 128 bits for CBC
            cipher = Cipher(algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Pad data to block size
            padded_data = data_bytes + b'\x00' * (16 - len(data_bytes) % 16)
            
            ciphertext = await loop.run_in_executor(
                None,
                lambda: encryptor.update(padded_data) + encryptor.finalize()
            )
            
            result = base64.b64encode(iv + ciphertext).decode('utf-8')
            
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.ENCRYPT,
            algorithm=algorithm,
            input_data=data,
            output_data=result,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.ENCRYPT,
            algorithm=algorithm,
            input_data=data,
            output_data=b"",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def perform_decryption_async(
    encrypted_data: Union[str, bytes],
    key: Union[str, bytes],
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
) -> CryptoResult:
    """Perform decryption operation asynchronously."""
    start_time = time.time()
    
    try:
        # Convert inputs to bytes
        if isinstance(encrypted_data, str):
            encrypted_bytes = base64.b64decode(encrypted_data)
        else:
            encrypted_bytes = encrypted_data
        
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
        else:
            key_bytes = key
        
        # Run decryption in thread pool
        loop = asyncio.get_event_loop()
        
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_128_GCM]:
            # GCM mode decryption
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                cipher_key = key_bytes[:32]  # 256 bits
            else:
                cipher_key = key_bytes[:16]  # 128 bits
            
            iv = encrypted_bytes[:12]  # 96 bits for GCM
            tag = encrypted_bytes[12:28]  # 128 bits tag
            ciphertext = encrypted_bytes[28:]
            
            cipher = Cipher(algorithms.AES(cipher_key), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            
            plaintext = await loop.run_in_executor(
                None,
                lambda: decryptor.update(ciphertext) + decryptor.finalize()
            )
            
            result = plaintext.decode('utf-8').rstrip('\x00')
            
        elif algorithm in [EncryptionAlgorithm.AES_256_CBC, EncryptionAlgorithm.AES_128_CBC]:
            # CBC mode decryption
            if algorithm == EncryptionAlgorithm.AES_256_CBC:
                cipher_key = key_bytes[:32]  # 256 bits
            else:
                cipher_key = key_bytes[:16]  # 128 bits
            
            iv = encrypted_bytes[:16]  # 128 bits for CBC
            ciphertext = encrypted_bytes[16:]
            
            cipher = Cipher(algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            plaintext = await loop.run_in_executor(
                None,
                lambda: decryptor.update(ciphertext) + decryptor.finalize()
            )
            
            result = plaintext.decode('utf-8').rstrip('\x00')
            
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.DECRYPT,
            algorithm=algorithm,
            input_data=encrypted_data,
            output_data=result,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.DECRYPT,
            algorithm=algorithm,
            input_data=encrypted_data,
            output_data=b"",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def generate_key_async(algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> CryptoResult:
    """Generate cryptographic key asynchronously."""
    start_time = time.time()
    
    try:
        loop = asyncio.get_event_loop()
        
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
            key_size = 32  # 256 bits
        elif algorithm in [EncryptionAlgorithm.AES_128_GCM, EncryptionAlgorithm.AES_128_CBC]:
            key_size = 16  # 128 bits
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_size = 32  # 256 bits
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            # Generate RSA key pair
            key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
            
            private_key = await loop.run_in_executor(
                None,
                lambda: rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size,
                    backend=default_backend()
                )
            )
            
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = await loop.run_in_executor(
                None,
                lambda: private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
            
            public_pem = await loop.run_in_executor(
                None,
                lambda: public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )
            
            result = {
                "private_key": private_pem.decode('utf-8'),
                "public_key": public_pem.decode('utf-8'),
                "key_size": key_size
            }
            
        else:
            # Generate symmetric key
            key = await loop.run_in_executor(None, lambda: os.urandom(key_size))
            result = base64.b64encode(key).decode('utf-8')
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.KEY_GENERATION,
            algorithm=algorithm,
            input_data="",
            output_data=result,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.KEY_GENERATION,
            algorithm=algorithm,
            input_data="",
            output_data="",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def derive_key_from_password_async(
    password: str,
    salt: Optional[Union[str, bytes]] = None,
    iterations: int = 100000,
    key_length: int = 32
) -> CryptoResult:
    """Derive key from password using PBKDF2."""
    start_time = time.time()
    
    try:
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt if not provided
        if salt is None:
            salt_bytes = os.urandom(16)
        elif isinstance(salt, str):
            salt_bytes = salt.encode('utf-8')
        else:
            salt_bytes = salt
        
        # Run PBKDF2 in thread pool
        loop = asyncio.get_event_loop()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt_bytes,
            iterations=iterations,
            backend=default_backend()
        )
        
        key = await loop.run_in_executor(None, lambda: kdf.derive(password_bytes))
        
        result = {
            "key": base64.b64encode(key).decode('utf-8'),
            "salt": base64.b64encode(salt_bytes).decode('utf-8'),
            "iterations": iterations,
            "key_length": key_length
        }
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.KEY_DERIVATION,
            algorithm=None,
            input_data=password,
            output_data=result,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.KEY_DERIVATION,
            algorithm=None,
            input_data=password,
            output_data="",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def create_digital_signature_async(
    data: Union[str, bytes],
    private_key_pem: str
) -> CryptoResult:
    """Create digital signature using RSA private key."""
    start_time = time.time()
    
    try:
        # Convert data to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # Run signature creation in thread pool
        loop = asyncio.get_event_loop()
        
        signature = await loop.run_in_executor(
            None,
            lambda: private_key.sign(
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        )
        
        result = base64.b64encode(signature).decode('utf-8')
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.SIGN,
            algorithm=EncryptionAlgorithm.RSA_2048,
            input_data=data,
            output_data=result,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.SIGN,
            algorithm=EncryptionAlgorithm.RSA_2048,
            input_data=data,
            output_data="",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def verify_signature_async(
    data: Union[str, bytes],
    signature: Union[str, bytes],
    public_key_pem: str
) -> CryptoResult:
    """Verify digital signature using RSA public key."""
    start_time = time.time()
    
    try:
        # Convert data to bytes
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        # Convert signature to bytes
        if isinstance(signature, str):
            signature_bytes = base64.b64decode(signature)
        else:
            signature_bytes = signature
        
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        # Run signature verification in thread pool
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(
                None,
                lambda: public_key.verify(
                    signature_bytes,
                    data_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            )
            verification_result = True
        except Exception:
            verification_result = False
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.VERIFY,
            algorithm=EncryptionAlgorithm.RSA_2048,
            input_data=data,
            output_data=verification_result,
            success=verification_result,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.VERIFY,
            algorithm=EncryptionAlgorithm.RSA_2048,
            input_data=data,
            output_data=False,
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def generate_random_bytes_async(length: int = 32) -> CryptoResult:
    """Generate cryptographically secure random bytes."""
    start_time = time.time()
    
    try:
        loop = asyncio.get_event_loop()
        random_bytes = await loop.run_in_executor(None, lambda: os.urandom(length))
        
        result = base64.b64encode(random_bytes).decode('utf-8')
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.KEY_GENERATION,
            algorithm=None,
            input_data="",
            output_data=result,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.KEY_GENERATION,
            algorithm=None,
            input_data="",
            output_data="",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def encrypt_file_async(
    file_path: str,
    key: Union[str, bytes],
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
) -> CryptoResult:
    """Encrypt a file asynchronously."""
    start_time = time.time()
    
    try:
        # Read file content
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()
        
        # Encrypt content
        encryption_result = await perform_encryption_async(file_content, key, algorithm)
        
        if not encryption_result.success:
            return encryption_result
        
        # Write encrypted content to new file
        encrypted_file_path = f"{file_path}.encrypted"
        async with aiofiles.open(encrypted_file_path, 'w') as f:
            await f.write(encryption_result.output_data)
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.ENCRYPT,
            algorithm=algorithm,
            input_data=file_path,
            output_data=encrypted_file_path,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.ENCRYPT,
            algorithm=algorithm,
            input_data=file_path,
            output_data="",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def decrypt_file_async(
    encrypted_file_path: str,
    key: Union[str, bytes],
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
) -> CryptoResult:
    """Decrypt a file asynchronously."""
    start_time = time.time()
    
    try:
        # Read encrypted content
        async with aiofiles.open(encrypted_file_path, 'r') as f:
            encrypted_content = await f.read()
        
        # Decrypt content
        decryption_result = await perform_decryption_async(encrypted_content, key, algorithm)
        
        if not decryption_result.success:
            return decryption_result
        
        # Write decrypted content to new file
        decrypted_file_path = encrypted_file_path.replace('.encrypted', '.decrypted')
        async with aiofiles.open(decrypted_file_path, 'wb') as f:
            await f.write(decryption_result.output_data.encode('utf-8'))
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.DECRYPT,
            algorithm=algorithm,
            input_data=encrypted_file_path,
            output_data=decrypted_file_path,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.DECRYPT,
            algorithm=algorithm,
            input_data=encrypted_file_path,
            output_data="",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def hash_file_async(
    file_path: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256
) -> CryptoResult:
    """Hash a file asynchronously."""
    start_time = time.time()
    
    try:
        # Read file content
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()
        
        # Hash content
        hash_result = await perform_hash_async(file_content, algorithm)
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.HASH,
            algorithm=algorithm,
            input_data=file_path,
            output_data=hash_result.output_data,
            success=True,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.HASH,
            algorithm=algorithm,
            input_data=file_path,
            output_data="",
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )

async def verify_file_integrity_async(
    file_path: str,
    expected_hash: str,
    algorithm: HashAlgorithm = HashAlgorithm.SHA256
) -> CryptoResult:
    """Verify file integrity by comparing hashes."""
    start_time = time.time()
    
    try:
        # Hash file
        hash_result = await hash_file_async(file_path, algorithm)
        
        if not hash_result.success:
            return hash_result
        
        # Compare hashes
        actual_hash = hash_result.output_data
        integrity_valid = actual_hash.lower() == expected_hash.lower()
        
        operation_duration = time.time() - start_time
        
        return CryptoResult(
            operation=CryptoOperation.VERIFY,
            algorithm=algorithm,
            input_data=file_path,
            output_data=integrity_valid,
            success=integrity_valid,
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        )
        
    except Exception as e:
        operation_duration = time.time() - start_time
        return CryptoResult(
            operation=CryptoOperation.VERIFY,
            algorithm=algorithm,
            input_data=file_path,
            output_data=False,
            success=False,
            error_message=str(e),
            operation_duration=operation_duration,
            operation_completed_at=time.time()
        ) 