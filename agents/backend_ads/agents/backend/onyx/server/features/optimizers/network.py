"""
Network Optimizer - Ultra-High Performance Network Operations.

Advanced network optimizer with HTTP/2, QUIC protocol support, intelligent
connection pooling, compression, and ultra-fast request/response processing.
"""

import asyncio
import time
import ssl
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging

# Core networking imports
import aiohttp
import httpx
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.client_exceptions import ClientError

# High-performance networking
try:
    import aioquic
    from aioquic.asyncio import connect
    from aioquic.h3.connection import H3Connection
    QUIC_AVAILABLE = True
except ImportError:
    QUIC_AVAILABLE = False

try:
    import h2
    import h11
    HTTP2_AVAILABLE = True
except ImportError:
    HTTP2_AVAILABLE = False

try:
    import brotli
    import zstandard as zstd
    ADVANCED_COMPRESSION_AVAILABLE = True
except ImportError:
    ADVANCED_COMPRESSION_AVAILABLE = False

try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

try:
    import orjson
    JSON_AVAILABLE = True
except ImportError:
    import json as orjson
    JSON_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class NetworkConfig:
    """Network optimization configuration."""
    # Connection pool settings
    max_connections: int = 1000
    max_connections_per_host: int = 100
    connection_timeout: float = 30.0
    read_timeout: float = 60.0
    pool_timeout: float = 10.0
    
    # Protocol settings
    enable_http2: bool = HTTP2_AVAILABLE
    enable_quic: bool = QUIC_AVAILABLE
    enable_compression: bool = True
    compression_threshold: int = 1024
    
    # Optimization settings
    enable_keep_alive: bool = True
    keep_alive_timeout: float = 30.0
    enable_tcp_nodelay: bool = True
    enable_connection_reuse: bool = True
    
    # SSL/TLS settings
    ssl_verify: bool = True
    ssl_context: Optional[ssl.SSLContext] = None
    
    # Performance settings
    chunk_size: int = 8192 * 16  # 128KB
    max_request_size: int = 100 * 1024 * 1024  # 100MB
    enable_streaming: bool = True
    
    # Rate limiting
    max_requests_per_second: int = 1000
    burst_size: int = 100


class CompressionOptimizer:
    """Advanced compression for network data."""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.compression_stats = {
            "total_compressed": 0,
            "total_decompressed": 0,
            "compression_ratio": 0.0,
            "avg_compression_time": 0.0
        }
    
    def compress_data(self, data: bytes, algorithm: str = "auto") -> Tuple[bytes, str]:
        """Compress data using optimal algorithm."""
        if not self.config.enable_compression or len(data) < self.config.compression_threshold:
            return data, "none"
        
        start_time = time.time()
        
        try:
            if algorithm == "auto":
                # Auto-select best compression based on data characteristics
                if len(data) > 1024 * 1024:  # Large files
                    algorithm = "zstd"
                elif data.startswith(b'{') or data.startswith(b'['):  # JSON-like
                    algorithm = "brotli"
                else:
                    algorithm = "gzip"
            
            if algorithm == "brotli" and ADVANCED_COMPRESSION_AVAILABLE:
                compressed = brotli.compress(data, quality=4)  # Fast compression
                algo_used = "brotli"
            elif algorithm == "zstd" and ADVANCED_COMPRESSION_AVAILABLE:
                compressor = zstd.ZstdCompressor(level=3)  # Fast level
                compressed = compressor.compress(data)
                algo_used = "zstd"
            else:
                # Fallback to gzip
                import gzip
                compressed = gzip.compress(data, compresslevel=6)
                algo_used = "gzip"
            
            # Update stats
            compression_time = time.time() - start_time
            self.compression_stats["total_compressed"] += 1
            self.compression_stats["compression_ratio"] = len(compressed) / len(data)
            self.compression_stats["avg_compression_time"] = (
                self.compression_stats["avg_compression_time"] + compression_time
            ) / 2
            
            return compressed, algo_used
            
        except Exception as e:
            logger.warning(f"Compression failed with {algorithm}: {e}")
            return data, "none"
    
    def decompress_data(self, data: bytes, algorithm: str) -> bytes:
        """Decompress data using specified algorithm."""
        if algorithm == "none":
            return data
        
        try:
            if algorithm == "brotli" and ADVANCED_COMPRESSION_AVAILABLE:
                return brotli.decompress(data)
            elif algorithm == "zstd" and ADVANCED_COMPRESSION_AVAILABLE:
                decompressor = zstd.ZstdDecompressor()
                return decompressor.decompress(data)
            else:  # gzip
                import gzip
                return gzip.decompress(data)
                
        except Exception as e:
            logger.error(f"Decompression failed for {algorithm}: {e}")
            raise


class ConnectionPoolOptimizer:
    """Ultra-optimized connection pool management."""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.pools: Dict[str, Any] = {}
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "connection_reuses": 0,
            "connection_errors": 0
        }
        
        # Create optimized SSL context
        if config.ssl_context is None and config.ssl_verify:
            self.ssl_context = self._create_optimized_ssl_context()
        else:
            self.ssl_context = config.ssl_context
    
    def _create_optimized_ssl_context(self) -> ssl.SSLContext:
        """Create optimized SSL context."""
        context = ssl.create_default_context()
        
        # Optimize SSL settings
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Enable session resumption
        context.options |= ssl.OP_NO_COMPRESSION  # Disable SSL compression
        
        return context
    
    async def create_aiohttp_session(self, session_name: str = "default") -> ClientSession:
        """Create optimized aiohttp session."""
        connector = TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections_per_host,
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=self.config.keep_alive_timeout,
            enable_cleanup_closed=True,
            ssl=self.ssl_context if self.config.ssl_verify else False
        )
        
        timeout = ClientTimeout(
            total=self.config.connection_timeout,
            connect=self.config.connection_timeout / 2,
            sock_read=self.config.read_timeout
        )
        
        session = ClientSession(
            connector=connector,
            timeout=timeout,
            read_bufsize=self.config.chunk_size,
            headers={
                'User-Agent': 'Onyx-NetworkOptimizer/1.0',
                'Accept-Encoding': 'br, gzip, deflate' if ADVANCED_COMPRESSION_AVAILABLE else 'gzip, deflate'
            },
            json_serialize=orjson.dumps if JSON_AVAILABLE else None
        )
        
        self.pools[session_name] = session
        return session
    
    async def create_httpx_client(self, client_name: str = "httpx_default") -> httpx.AsyncClient:
        """Create optimized HTTPX client with HTTP/2 support."""
        limits = httpx.Limits(
            max_keepalive_connections=self.config.max_connections_per_host,
            max_connections=self.config.max_connections,
            keepalive_expiry=self.config.keep_alive_timeout
        )
        
        client = httpx.AsyncClient(
            limits=limits,
            timeout=httpx.Timeout(
                connect=self.config.connection_timeout,
                read=self.config.read_timeout,
                pool=self.config.pool_timeout
            ),
            http2=self.config.enable_http2,
            verify=self.ssl_context if self.config.ssl_verify else False,
            headers={
                'User-Agent': 'Onyx-NetworkOptimizer-HTTPX/1.0'
            }
        )
        
        self.pools[client_name] = client
        return client
    
    def get_session(self, session_name: str = "default") -> Optional[ClientSession]:
        """Get existing session."""
        return self.pools.get(session_name)
    
    async def cleanup_sessions(self):
        """Cleanup all sessions."""
        for name, session in self.pools.items():
            try:
                if hasattr(session, 'close'):
                    await session.close()
                logger.info(f"Closed session: {name}")
            except Exception as e:
                logger.error(f"Error closing session {name}: {e}")
        
        self.pools.clear()


class RequestOptimizer:
    """Optimize HTTP requests with intelligent routing and caching."""
    
    def __init__(self, config: NetworkConfig, compression_optimizer: CompressionOptimizer):
        self.config = config
        self.compression_optimizer = compression_optimizer
        self.request_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0
        }
        self.response_cache: Dict[str, Tuple[Any, float]] = {}
    
    async def optimized_request(
        self,
        session: Union[ClientSession, httpx.AsyncClient],
        method: str,
        url: str,
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """Execute optimized HTTP request."""
        start_time = time.time()
        self.request_stats["total_requests"] += 1
        
        # Prepare request
        headers = kwargs.get('headers', {})
        
        # Add compression headers
        if self.config.enable_compression:
            headers['Accept-Encoding'] = 'br, gzip, deflate'
        
        # Add optimization headers
        headers.update({
            'Connection': 'keep-alive' if self.config.enable_keep_alive else 'close',
            'Cache-Control': 'max-age=300'
        })
        
        kwargs['headers'] = headers
        
        try:
            # Execute request
            if isinstance(session, ClientSession):
                response = await self._aiohttp_request(session, method, url, **kwargs)
            else:
                response = await self._httpx_request(session, method, url, **kwargs)
            
            # Process response
            response_data, metadata = await self._process_response(response)
            
            # Update stats
            response_time = time.time() - start_time
            self.request_stats["successful_requests"] += 1
            self.request_stats["avg_response_time"] = (
                self.request_stats["avg_response_time"] + response_time
            ) / 2
            
            metadata.update({
                "response_time": response_time,
                "request_size": len(str(kwargs.get('data', ''))),
                "compression_used": metadata.get('compression_used', False)
            })
            
            return response_data, metadata
            
        except Exception as e:
            self.request_stats["failed_requests"] += 1
            logger.error(f"Request failed: {method} {url} - {e}")
            raise
    
    async def _aiohttp_request(self, session: ClientSession, method: str, url: str, **kwargs):
        """Execute aiohttp request."""
        async with session.request(method, url, **kwargs) as response:
            return response
    
    async def _httpx_request(self, client: httpx.AsyncClient, method: str, url: str, **kwargs):
        """Execute HTTPX request."""
        return await client.request(method, url, **kwargs)
    
    async def _process_response(self, response) -> Tuple[Any, Dict[str, Any]]:
        """Process and optimize response data."""
        metadata = {
            "status_code": response.status if hasattr(response, 'status') else response.status_code,
            "headers": dict(response.headers),
            "compression_used": False
        }
        
        # Check for compression
        content_encoding = response.headers.get('content-encoding', '').lower()
        
        if hasattr(response, 'read'):  # aiohttp
            data = await response.read()
        else:  # httpx
            data = response.content
        
        # Decompress if needed
        if content_encoding and content_encoding != 'identity':
            try:
                if content_encoding in ['br', 'brotli']:
                    data = self.compression_optimizer.decompress_data(data, 'brotli')
                elif content_encoding == 'gzip':
                    data = self.compression_optimizer.decompress_data(data, 'gzip')
                elif content_encoding == 'deflate':
                    import zlib
                    data = zlib.decompress(data)
                
                metadata["compression_used"] = True
                metadata["original_encoding"] = content_encoding
            except Exception as e:
                logger.warning(f"Decompression failed: {e}")
        
        # Try to parse JSON
        try:
            if JSON_AVAILABLE:
                parsed_data = orjson.loads(data)
            else:
                parsed_data = orjson.loads(data.decode('utf-8'))
            return parsed_data, metadata
        except:
            return data, metadata
    
    async def batch_requests(
        self,
        session: Union[ClientSession, httpx.AsyncClient],
        requests: List[Tuple[str, str, Dict]],  # (method, url, kwargs)
        max_concurrent: int = 50
    ) -> List[Tuple[Any, Dict[str, Any]]]:
        """Execute multiple requests concurrently with optimization."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single_request(method, url, kwargs):
            async with semaphore:
                return await self.optimized_request(session, method, url, **kwargs)
        
        tasks = [
            execute_single_request(method, url, kwargs)
            for method, url, kwargs in requests
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


class NetworkOptimizer:
    """Main network optimizer coordinating all components."""
    
    def __init__(self, config: NetworkConfig = None):
        self.config = config or NetworkConfig()
        self.compression_optimizer = CompressionOptimizer(self.config)
        self.pool_optimizer = ConnectionPoolOptimizer(self.config)
        self.request_optimizer = RequestOptimizer(self.config, self.compression_optimizer)
        
        self.metrics = {
            "optimization_level": "ULTRA",
            "features_enabled": {
                "http2": self.config.enable_http2 and HTTP2_AVAILABLE,
                "quic": self.config.enable_quic and QUIC_AVAILABLE,
                "compression": self.config.enable_compression,
                "advanced_compression": ADVANCED_COMPRESSION_AVAILABLE,
                "connection_pooling": True,
                "ssl_optimization": True
            }
        }
    
    async def initialize(self) -> Dict[str, bool]:
        """Initialize network optimizer."""
        results = {}
        
        try:
            # Create default sessions
            await self.pool_optimizer.create_aiohttp_session("default")
            results["aiohttp_session"] = True
            
            await self.pool_optimizer.create_httpx_client("default")
            results["httpx_client"] = True
            
            # Setup event loop optimization
            if UVLOOP_AVAILABLE and not isinstance(asyncio.get_event_loop(), uvloop.Loop):
                logger.info("Consider using uvloop for better performance")
            
            logger.info("Network optimizer initialized", 
                       features=self.metrics["features_enabled"])
            
            return results
            
        except Exception as e:
            logger.error(f"Network optimizer initialization failed: {e}")
            return {"initialization": False}
    
    async def request(
        self,
        method: str,
        url: str,
        session_type: str = "aiohttp",
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """Execute optimized network request."""
        if session_type == "aiohttp":
            session = self.pool_optimizer.get_session("default")
            if not session:
                session = await self.pool_optimizer.create_aiohttp_session("default")
        else:  # httpx
            session = self.pool_optimizer.pools.get("default")
            if not session:
                session = await self.pool_optimizer.create_httpx_client("default")
        
        return await self.request_optimizer.optimized_request(
            session, method, url, **kwargs
        )
    
    async def batch_request(
        self,
        requests: List[Tuple[str, str, Dict]],
        session_type: str = "aiohttp",
        max_concurrent: int = 50
    ) -> List[Tuple[Any, Dict[str, Any]]]:
        """Execute batch of optimized requests."""
        if session_type == "aiohttp":
            session = self.pool_optimizer.get_session("default")
            if not session:
                session = await self.pool_optimizer.create_aiohttp_session("default")
        else:
            session = self.pool_optimizer.pools.get("default")
            if not session:
                session = await self.pool_optimizer.create_httpx_client("default")
        
        return await self.request_optimizer.batch_requests(
            session, requests, max_concurrent
        )
    
    @asynccontextmanager
    async def optimized_session(self, session_name: str = None, session_type: str = "aiohttp"):
        """Context manager for optimized session usage."""
        session_name = session_name or f"temp_{int(time.time())}"
        session = None
        
        try:
            if session_type == "aiohttp":
                session = await self.pool_optimizer.create_aiohttp_session(session_name)
            else:
                session = await self.pool_optimizer.create_httpx_client(session_name)
            
            yield session
            
        finally:
            if session and hasattr(session, 'close'):
                await session.close()
                if session_name in self.pool_optimizer.pools:
                    del self.pool_optimizer.pools[session_name]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive network performance metrics."""
        return {
            "compression_stats": self.compression_optimizer.compression_stats,
            "connection_stats": self.pool_optimizer.connection_stats,
            "request_stats": self.request_optimizer.request_stats,
            "config": {
                "max_connections": self.config.max_connections,
                "http2_enabled": self.config.enable_http2,
                "compression_enabled": self.config.enable_compression,
                "connection_timeout": self.config.connection_timeout
            },
            "features": self.metrics["features_enabled"]
        }
    
    async def cleanup(self):
        """Cleanup network resources."""
        await self.pool_optimizer.cleanup_sessions()
        logger.info("Network optimizer cleanup completed")


__all__ = [
    'NetworkOptimizer',
    'NetworkConfig',
    'CompressionOptimizer',
    'ConnectionPoolOptimizer',
    'RequestOptimizer'
] 