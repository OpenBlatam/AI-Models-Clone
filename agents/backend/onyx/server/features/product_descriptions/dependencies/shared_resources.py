"""
Shared Resources Dependencies

This module provides dependency injection for shared resources including:
- Network sessions (HTTP, WebSocket, gRPC)
- Cryptographic backends (encryption, hashing, signing)
- Connection pools
- Resource managers
- Configuration providers

Features:
- Singleton pattern for resource management
- Async context managers for proper cleanup
- Configuration-driven resource initialization
- Health checks and monitoring
- Graceful degradation and fallbacks
- Resource pooling and connection reuse
"""

import asyncio
import os
import ssl
import time
from typing import Optional, Dict, Any, List, Union, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta

import aiohttp
import httpx
import websockets
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.pool import QueuePool

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
import structlog

# Import existing managers
from ..async_io_manager import AsyncIOManager
from ..caching_manager import CachingManager
from ..performance_metrics import PerformanceMonitor

# Configure logging
logger = structlog.get_logger(__name__)

# =============================================================================
# Configuration Models
# =============================================================================

class ResourceType(str, Enum):
    """Types of shared resources."""
    HTTP_SESSION = "http_session"
    WEBSOCKET_SESSION = "websocket_session"
    GRPC_SESSION = "grpc_session"
    CRYPTO_BACKEND = "crypto_backend"
    DATABASE_POOL = "database_pool"
    CACHE_POOL = "cache_pool"
    REDIS_POOL = "redis_pool"

class CryptoAlgorithm(str, Enum):
    """Supported cryptographic algorithms."""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    SHA_256 = "sha_256"
    SHA_512 = "sha_512"
    HMAC_SHA256 = "hmac_sha256"

class NetworkProtocol(str, Enum):
    """Supported network protocols."""
    HTTP = "http"
    HTTPS = "https"
    WS = "ws"
    WSS = "wss"
    GRPC = "grpc"

@dataclass
class ResourceConfig:
    """Configuration for a shared resource."""
    name: str
    resource_type: ResourceType
    max_connections: int = 100
    max_retries: int = 3
    timeout: float = 30.0
    keepalive_timeout: float = 60.0
    pool_timeout: float = 10.0
    enable_compression: bool = True
    enable_ssl_verification: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    health_check_interval: float = 30.0
    health_check_timeout: float = 5.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0

@dataclass
class CryptoConfig:
    """Configuration for cryptographic operations."""
    algorithm: CryptoAlgorithm
    key_size: int = 256
    salt_length: int = 32
    iterations: int = 100000
    enable_hardware_acceleration: bool = True
    key_rotation_interval: Optional[timedelta] = None

class SharedResourceConfig(BaseModel):
    """Global configuration for shared resources."""
    resources: Dict[str, ResourceConfig] = Field(default_factory=dict)
    crypto_configs: Dict[str, CryptoConfig] = Field(default_factory=dict)
    global_timeout: float = 30.0
    global_max_retries: int = 3
    enable_monitoring: bool = True
    enable_health_checks: bool = True
    resource_cleanup_interval: float = 300.0  # 5 minutes

    @validator('resources')
    def validate_resources(cls, v):
        """Validate resource configurations."""
        for name, config in v.items():
            if not isinstance(config, ResourceConfig):
                raise ValueError(f"Invalid resource config for {name}")
        return v

# =============================================================================
# Resource Health and Status
# =============================================================================

@dataclass
class ResourceHealth:
    """Health status of a resource."""
    is_healthy: bool
    last_check: datetime
    response_time: float
    error_count: int = 0
    last_error: Optional[str] = None
    uptime: float = 0.0

@dataclass
class ResourceMetrics:
    """Metrics for a resource."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    active_connections: int = 0
    peak_connections: int = 0

# =============================================================================
# Base Resource Manager
# =============================================================================

class BaseResourceManager:
    """Base class for resource managers."""
    
    def __init__(self, config: ResourceConfig):
        self.config = config
        self.health = ResourceHealth(
            is_healthy=True,
            last_check=datetime.utcnow(),
            response_time=0.0
        )
        self.metrics = ResourceMetrics()
        self._lock = asyncio.Lock()
        self._last_cleanup = datetime.utcnow()
    
    async def health_check(self) -> ResourceHealth:
        """Perform health check on the resource."""
        raise NotImplementedError
    
    async def cleanup(self):
        """Cleanup resources."""
        raise NotImplementedError
    
    async def get_metrics(self) -> ResourceMetrics:
        """Get resource metrics."""
        return self.metrics
    
    def is_available(self) -> bool:
        """Check if resource is available."""
        return self.health.is_healthy

# =============================================================================
# Network Session Managers
# =============================================================================

class HTTPSessionManager(BaseResourceManager):
    """Manages HTTP sessions with connection pooling."""
    
    def __init__(self, config: ResourceConfig):
        super().__init__(config)
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        self._timeout: Optional[aiohttp.ClientTimeout] = None
    
    async def _initialize_session(self):
        """Initialize the HTTP session."""
        if self._session is not None:
            return
        
        # Create connector with connection pooling
        self._connector = aiohttp.TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections // 4,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=True,
            ssl=self.config.enable_ssl_verification
        )
        
        # Create timeout configuration
        self._timeout = aiohttp.ClientTimeout(
            total=self.config.timeout,
            connect=self.config.timeout / 2
        )
        
        # Create session
        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=self._timeout,
            headers=self.config.custom_headers
        )
        
        logger.info("HTTP session initialized", 
                   max_connections=self.config.max_connections,
                   timeout=self.config.timeout)
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get the HTTP session."""
        if self._session is None:
            await self._initialize_session()
        return self._session
    
    async def health_check(self) -> ResourceHealth:
        """Perform health check."""
        start_time = time.time()
        try:
            session = await self.get_session()
            async with session.get("https://httpbin.org/get", timeout=5) as response:
                if response.status == 200:
                    response_time = time.time() - start_time
                    self.health = ResourceHealth(
                        is_healthy=True,
                        last_check=datetime.utcnow(),
                        response_time=response_time
                    )
                else:
                    self.health.is_healthy = False
                    self.health.error_count += 1
        except Exception as e:
            self.health.is_healthy = False
            self.health.error_count += 1
            self.health.last_error = str(e)
            logger.error("HTTP session health check failed", error=str(e))
        
        return self.health
    
    async def cleanup(self):
        """Cleanup HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
        if self._connector:
            await self._connector.close()
            self._connector = None
        logger.info("HTTP session cleaned up")

class WebSocketSessionManager(BaseResourceManager):
    """Manages WebSocket connections."""
    
    def __init__(self, config: ResourceConfig):
        super().__init__(config)
        self._connections: Dict[str, websockets.WebSocketServerProtocol] = {}
    
    async def get_connection(self, uri: str) -> websockets.WebSocketServerProtocol:
        """Get or create WebSocket connection."""
        if uri not in self._connections:
            self._connections[uri] = await websockets.connect(uri)
        return self._connections[uri]
    
    async def health_check(self) -> ResourceHealth:
        """Perform health check."""
        # WebSocket health check implementation
        return self.health
    
    async def cleanup(self):
        """Cleanup WebSocket connections."""
        for conn in self._connections.values():
            await conn.close()
        self._connections.clear()

# =============================================================================
# Cryptographic Backend Manager
# =============================================================================

class CryptoBackendManager(BaseResourceManager):
    """Manages cryptographic operations."""
    
    def __init__(self, config: CryptoConfig):
        super().__init__(ResourceConfig(
            name="crypto_backend",
            resource_type=ResourceType.CRYPTO_BACKEND
        ))
        self.crypto_config = config
        self._private_key: Optional[rsa.RSAPrivateKey] = None
        self._public_key: Optional[rsa.RSAPublicKey] = None
        self._symmetric_key: Optional[bytes] = None
        self._key_generated_at: Optional[datetime] = None
    
    async def _generate_keys(self):
        """Generate cryptographic keys."""
        if self._private_key is None:
            self._private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.crypto_config.key_size,
                backend=default_backend()
            )
            self._public_key = self._private_key.public_key()
            self._key_generated_at = datetime.utcnow()
            
            # Generate symmetric key for AES operations
            if self.crypto_config.algorithm in [CryptoAlgorithm.AES_256_GCM, CryptoAlgorithm.AES_256_CBC]:
                self._symmetric_key = os.urandom(32)
            
            logger.info("Cryptographic keys generated", 
                       algorithm=self.crypto_config.algorithm,
                       key_size=self.crypto_config.key_size)
    
    async def encrypt(self, data: bytes) -> bytes:
        """Encrypt data."""
        await self._generate_keys()
        
        if self.crypto_config.algorithm == CryptoAlgorithm.AES_256_GCM:
            iv = os.urandom(12)
            cipher = Cipher(
                algorithms.AES(self._symmetric_key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            return iv + encryptor.tag + ciphertext
        
        elif self.crypto_config.algorithm == CryptoAlgorithm.RSA_2048:
            ciphertext = self._public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return ciphertext
        
        raise ValueError(f"Unsupported encryption algorithm: {self.crypto_config.algorithm}")
    
    async def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data."""
        await self._generate_keys()
        
        if self.crypto_config.algorithm == CryptoAlgorithm.AES_256_GCM:
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            cipher = Cipher(
                algorithms.AES(self._symmetric_key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
        
        elif self.crypto_config.algorithm == CryptoAlgorithm.RSA_2048:
            plaintext = self._private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return plaintext
        
        raise ValueError(f"Unsupported decryption algorithm: {self.crypto_config.algorithm}")
    
    async def hash(self, data: bytes) -> bytes:
        """Hash data."""
        if self.crypto_config.algorithm == CryptoAlgorithm.SHA_256:
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(data)
            return digest.finalize()
        
        elif self.crypto_config.algorithm == CryptoAlgorithm.SHA_512:
            digest = hashes.Hash(hashes.SHA512(), backend=default_backend())
            digest.update(data)
            return digest.finalize()
        
        raise ValueError(f"Unsupported hashing algorithm: {self.crypto_config.algorithm}")
    
    async def sign(self, data: bytes) -> bytes:
        """Sign data."""
        await self._generate_keys()
        
        signature = self._private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    async def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify signature."""
        await self._generate_keys()
        
        try:
            self._public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    async def health_check(self) -> ResourceHealth:
        """Perform health check."""
        start_time = time.time()
        try:
            # Test encryption/decryption
            test_data = b"health_check_test"
            encrypted = await self.encrypt(test_data)
            decrypted = await self.decrypt(encrypted)
            
            if decrypted == test_data:
                response_time = time.time() - start_time
                self.health = ResourceHealth(
                    is_healthy=True,
                    last_check=datetime.utcnow(),
                    response_time=response_time
                )
            else:
                self.health.is_healthy = False
                self.health.error_count += 1
        except Exception as e:
            self.health.is_healthy = False
            self.health.error_count += 1
            self.health.last_error = str(e)
            logger.error("Crypto backend health check failed", error=str(e))
        
        return self.health
    
    async def cleanup(self):
        """Cleanup cryptographic resources."""
        self._private_key = None
        self._public_key = None
        self._symmetric_key = None
        self._key_generated_at = None
        logger.info("Crypto backend cleaned up")

# =============================================================================
# Database Pool Manager
# =============================================================================

class DatabasePoolManager(BaseResourceManager):
    """Manages database connection pools."""
    
    def __init__(self, config: ResourceConfig, database_url: str):
        super().__init__(config)
        self.database_url = database_url
        self._engine: Optional[AsyncEngine] = None
        self._pool: Optional[QueuePool] = None
    
    async def _initialize_pool(self):
        """Initialize database connection pool."""
        if self._engine is not None:
            return
        
        self._engine = create_async_engine(
            self.database_url,
            pool_size=self.config.max_connections,
            max_overflow=self.config.max_connections // 2,
            pool_timeout=self.config.pool_timeout,
            pool_pre_ping=True,
            echo=False
        )
        
        logger.info("Database pool initialized", 
                   max_connections=self.config.max_connections,
                   database_url=self.database_url)
    
    async def get_session(self) -> AsyncSession:
        """Get database session from pool."""
        if self._engine is None:
            await self._initialize_pool()
        
        return AsyncSession(self._engine)
    
    async def health_check(self) -> ResourceHealth:
        """Perform health check."""
        start_time = time.time()
        try:
            session = await self.get_session()
            async with session.begin():
                await session.execute("SELECT 1")
            
            response_time = time.time() - start_time
            self.health = ResourceHealth(
                is_healthy=True,
                last_check=datetime.utcnow(),
                response_time=response_time
            )
        except Exception as e:
            self.health.is_healthy = False
            self.health.error_count += 1
            self.health.last_error = str(e)
            logger.error("Database pool health check failed", error=str(e))
        
        return self.health
    
    async def cleanup(self):
        """Cleanup database pool."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        logger.info("Database pool cleaned up")

# =============================================================================
# Redis Pool Manager
# =============================================================================

class RedisPoolManager(BaseResourceManager):
    """Manages Redis connection pool."""
    
    def __init__(self, config: ResourceConfig, redis_url: str):
        super().__init__(config)
        self.redis_url = redis_url
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
    
    async def _initialize_pool(self):
        """Initialize Redis connection pool."""
        if self._pool is not None:
            return
        
        self._pool = redis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=self.config.max_connections,
            retry_on_timeout=True,
            health_check_interval=self.config.health_check_interval
        )
        
        self._client = redis.Redis(connection_pool=self._pool)
        
        logger.info("Redis pool initialized", 
                   max_connections=self.config.max_connections,
                   redis_url=self.redis_url)
    
    async def get_client(self) -> redis.Redis:
        """Get Redis client from pool."""
        if self._client is None:
            await self._initialize_pool()
        return self._client
    
    async def health_check(self) -> ResourceHealth:
        """Perform health check."""
        start_time = time.time()
        try:
            client = await self.get_client()
            await client.ping()
            
            response_time = time.time() - start_time
            self.health = ResourceHealth(
                is_healthy=True,
                last_check=datetime.utcnow(),
                response_time=response_time
            )
        except Exception as e:
            self.health.is_healthy = False
            self.health.error_count += 1
            self.health.last_error = str(e)
            logger.error("Redis pool health check failed", error=str(e))
        
        return self.health
    
    async def cleanup(self):
        """Cleanup Redis pool."""
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("Redis pool cleaned up")

# =============================================================================
# Shared Resources Container
# =============================================================================

class SharedResourcesContainer:
    """Container for managing all shared resources."""
    
    def __init__(self, config: SharedResourceConfig):
        self.config = config
        self._resources: Dict[str, BaseResourceManager] = {}
        self._crypto_backends: Dict[str, CryptoBackendManager] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize all resources."""
        async with self._lock:
            # Initialize network sessions
            for name, config in self.config.resources.items():
                if config.resource_type == ResourceType.HTTP_SESSION:
                    self._resources[name] = HTTPSessionManager(config)
                elif config.resource_type == ResourceType.WEBSOCKET_SESSION:
                    self._resources[name] = WebSocketSessionManager(config)
                elif config.resource_type == ResourceType.DATABASE_POOL:
                    # This would be configured with actual database URL
                    pass
                elif config.resource_type == ResourceType.REDIS_POOL:
                    # This would be configured with actual Redis URL
                    pass
            
            # Initialize crypto backends
            for name, config in self.config.crypto_configs.items():
                self._crypto_backends[name] = CryptoBackendManager(config)
            
            # Start health check task
            if self.config.enable_health_checks:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Shared resources container initialized")
    
    async def get_resource(self, name: str) -> BaseResourceManager:
        """Get a resource by name."""
        if name not in self._resources:
            raise ValueError(f"Resource '{name}' not found")
        return self._resources[name]
    
    async def get_crypto_backend(self, name: str) -> CryptoBackendManager:
        """Get a crypto backend by name."""
        if name not in self._crypto_backends:
            raise ValueError(f"Crypto backend '{name}' not found")
        return self._crypto_backends[name]
    
    async def _health_check_loop(self):
        """Health check loop."""
        while True:
            try:
                for resource in self._resources.values():
                    await resource.health_check()
                
                for backend in self._crypto_backends.values():
                    await backend.health_check()
                
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                logger.error("Health check loop error", error=str(e))
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _cleanup_loop(self):
        """Cleanup loop."""
        while True:
            try:
                current_time = datetime.utcnow()
                if (current_time - self._last_cleanup).total_seconds() > self.config.resource_cleanup_interval:
                    await self._perform_cleanup()
                    self._last_cleanup = current_time
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error("Cleanup loop error", error=str(e))
                await asyncio.sleep(60)
    
    async def _perform_cleanup(self):
        """Perform resource cleanup."""
        for resource in self._resources.values():
            await resource.cleanup()
        
        for backend in self._crypto_backends.values():
            await backend.cleanup()
        
        logger.info("Resource cleanup performed")
    
    async def shutdown(self):
        """Shutdown all resources."""
        if self._health_check_task:
            self._health_check_task.cancel()
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        await self._perform_cleanup()
        logger.info("Shared resources container shutdown")

# =============================================================================
# Global Instance
# =============================================================================

# Global shared resources container
_shared_resources: Optional[SharedResourcesContainer] = None

def get_shared_resources() -> SharedResourcesContainer:
    """Get the global shared resources container."""
    global _shared_resources
    if _shared_resources is None:
        # Default configuration
        config = SharedResourceConfig(
            resources={
                "http_session": ResourceConfig(
                    name="http_session",
                    resource_type=ResourceType.HTTP_SESSION,
                    max_connections=100,
                    timeout=30.0
                ),
                "websocket_session": ResourceConfig(
                    name="websocket_session",
                    resource_type=ResourceType.WEBSOCKET_SESSION,
                    max_connections=50
                )
            },
            crypto_configs={
                "default": CryptoConfig(
                    algorithm=CryptoAlgorithm.AES_256_GCM,
                    key_size=256
                ),
                "rsa": CryptoConfig(
                    algorithm=CryptoAlgorithm.RSA_2048,
                    key_size=2048
                )
            }
        )
        _shared_resources = SharedResourcesContainer(config)
    return _shared_resources

# =============================================================================
# FastAPI Dependencies
# =============================================================================

async def get_http_session() -> aiohttp.ClientSession:
    """Get HTTP session dependency."""
    shared_resources = get_shared_resources()
    http_manager = await shared_resources.get_resource("http_session")
    return await http_manager.get_session()

async def get_websocket_session() -> WebSocketSessionManager:
    """Get WebSocket session manager dependency."""
    shared_resources = get_shared_resources()
    return await shared_resources.get_resource("websocket_session")

async def get_crypto_backend(name: str = "default") -> CryptoBackendManager:
    """Get crypto backend dependency."""
    shared_resources = get_shared_resources()
    return await shared_resources.get_crypto_backend(name)

async def get_database_pool() -> DatabasePoolManager:
    """Get database pool dependency."""
    shared_resources = get_shared_resources()
    return await shared_resources.get_resource("database_pool")

async def get_redis_pool() -> RedisPoolManager:
    """Get Redis pool dependency."""
    shared_resources = get_shared_resources()
    return await shared_resources.get_resource("redis_pool")

# =============================================================================
# Context Managers
# =============================================================================

@asynccontextmanager
async def http_session_context():
    """Context manager for HTTP session."""
    session = await get_http_session()
    try:
        yield session
    finally:
        # Session cleanup is handled by the manager
        pass

@asynccontextmanager
async def crypto_backend_context(name: str = "default"):
    """Context manager for crypto backend."""
    backend = await get_crypto_backend(name)
    try:
        yield backend
    finally:
        # Backend cleanup is handled by the manager
        pass

# =============================================================================
# Utility Functions
# =============================================================================

async def initialize_shared_resources(config: Optional[SharedResourceConfig] = None):
    """Initialize shared resources."""
    global _shared_resources
    if config is None:
        config = SharedResourceConfig()
    
    _shared_resources = SharedResourcesContainer(config)
    await _shared_resources.initialize()

async def shutdown_shared_resources():
    """Shutdown shared resources."""
    global _shared_resources
    if _shared_resources:
        await _shared_resources.shutdown()
        _shared_resources = None

def get_resource_health(name: str) -> Optional[ResourceHealth]:
    """Get health status of a resource."""
    if _shared_resources:
        try:
            resource = _shared_resources._resources.get(name)
            if resource:
                return resource.health
        except Exception:
            pass
    return None

def get_all_resource_health() -> Dict[str, ResourceHealth]:
    """Get health status of all resources."""
    if not _shared_resources:
        return {}
    
    health_status = {}
    for name, resource in _shared_resources._resources.items():
        health_status[name] = resource.health
    
    for name, backend in _shared_resources._crypto_backends.items():
        health_status[f"crypto_{name}"] = backend.health
    
    return health_status 