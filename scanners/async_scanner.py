from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

# Constants
BUFFER_SIZE = 1024

import asyncio
import aiohttp
import asyncssh
import socket
import ssl
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
import time
from collections import defaultdict
import json
from typing import Any, List, Dict, Optional
"""
High-throughput async scanner with connection pooling for network enumeration.
Implements asyncio-based scanning with connection reuse and rate limiting.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScanTarget:
    """Represents a target for scanning operations."""
    host: str
    port: Optional[int] = None
    protocol: str = "tcp"
    timeout: float = 5.0
    retries: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResult:
    """Represents the result of a scan operation."""
    target: ScanTarget
    is_open: bool
    response_time: float
    service: Optional[str] = None
    banner: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pooling."""
    max_connections: int = 100
    max_connections_per_host: int = 10
    connection_timeout: float = 10.0
    keepalive_timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit_per_second: int = 100
    rate_limit_burst: int = 50


class AsyncConnectionPool:
    """High-performance connection pool for async scanning operations."""
    
    def __init__(self, config: ConnectionPoolConfig):
        
    """__init__ function."""
self.config = config
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.ssh_connections: Dict[str, asyncssh.SSHClientConnection] = {}
        self.tcp_connections: Dict[str, asyncio.StreamWriter] = {}
        self.connection_semaphores: Dict[str, asyncio.Semaphore] = defaultdict(
            lambda: asyncio.Semaphore(config.max_connections_per_host)
        )
        self.rate_limiter = asyncio.Semaphore(config.rate_limit_per_second)
        self.last_request_time = defaultdict(float)
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "connection_reuses": 0,
            "new_connections": 0
        }
    
    async def __aenter__(self) -> Any:
        """Async context manager entry."""
        await self.initialize_pool()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Any:
        """Async context manager exit with cleanup."""
        await self.cleanup_pool()
    
    async def initialize_pool(self) -> Any:
        """Initialize the connection pool."""
        connector = aiohttp.TCPConnector(
            limit=self.config.max_connections,
            limit_per_host=self.config.max_connections_per_host,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=True,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.connection_timeout)
        self.http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "AsyncScanner/1.0"}
        )
        
        logger.info(f"Connection pool initialized with {self.config.max_connections} max connections")
    
    async def cleanup_pool(self) -> Any:
        """Clean up all connections in the pool."""
        if self.http_session:
            await self.http_session.close()
        
        # Close SSH connections
        for conn in self.ssh_connections.values():
            conn.close()
        self.ssh_connections.clear()
        
        # Close TCP connections
        for writer in self.tcp_connections.values():
            writer.close()
            await writer.wait_closed()
        self.tcp_connections.clear()
        
        logger.info("Connection pool cleaned up")
    
    async async def get_http_session(self) -> aiohttp.ClientSession:
        """Get the HTTP session from the pool."""
        if not self.http_session or self.http_session.closed:
            await self.initialize_pool()
        return self.http_session
    
    async def get_ssh_connection(self, host: str, port: int = 22, 
                               username: str = "root", password: Optional[str] = None,
                               key_file: Optional[str] = None) -> asyncssh.SSHClientConnection:
        """Get or create an SSH connection from the pool."""
        connection_key = f"{host}:{port}:{username}"
        
        if connection_key in self.ssh_connections:
            conn = self.ssh_connections[connection_key]
            if not conn.is_closing():
                self.stats["connection_reuses"] += 1
                return conn
        
        async with self.connection_semaphores[host]:
            try:
                conn_kwargs = {
                    "host": host,
                    "port": port,
                    "username": username,
                    "known_hosts": None,  # Disable host key checking for scanning
                    "connect_timeout": self.config.connection_timeout
                }
                
                if password:
                    conn_kwargs["password"] = password
                elif key_file:
                    conn_kwargs["client_keys"] = [key_file]
                
                conn = await asyncssh.connect(**conn_kwargs)
                self.ssh_connections[connection_key] = conn
                self.stats["new_connections"] += 1
                
                logger.debug(f"New SSH connection established to {host}:{port}")
                return conn
                
            except Exception as e:
                logger.error(f"Failed to establish SSH connection to {host}:{port}: {e}")
                raise
    
    async def get_tcp_connection(self, host: str, port: int) -> asyncio.StreamWriter:
        """Get or create a TCP connection from the pool."""
        connection_key = f"{host}:{port}"
        
        if connection_key in self.tcp_connections:
            writer = self.tcp_connections[connection_key]
            if not writer.is_closing():
                self.stats["connection_reuses"] += 1
                return writer
        
        async with self.connection_semaphores[host]:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=self.config.connection_timeout
                )
                self.tcp_connections[connection_key] = writer
                self.stats["new_connections"] += 1
                
                logger.debug(f"New TCP connection established to {host}:{port}")
                return writer
                
            except Exception as e:
                logger.error(f"Failed to establish TCP connection to {host}:{port}: {e}")
                raise
    
    async def rate_limit(self, host: str):
        """Apply rate limiting per host."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time[host]
        
        if time_since_last < 1.0 / self.config.rate_limit_per_second:
            await asyncio.sleep(1.0 / self.config.rate_limit_per_second - time_since_last)
        
        self.last_request_time[host] = time.time()
        await self.rate_limiter.acquire()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return {
            **self.stats,
            "active_ssh_connections": len(self.ssh_connections),
            "active_tcp_connections": len(self.tcp_connections),
            "pool_config": self.config.__dict__
        }


class AsyncPortScanner:
    """High-throughput async port scanner with connection pooling."""
    
    def __init__(self, pool_config: ConnectionPoolConfig):
        
    """__init__ function."""
self.pool_config = pool_config
        self.common_ports = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
            80: "http", 110: "pop3", 143: "imap", 443: "https", 993: "imaps",
            995: "pop3s", 3306: "mysql", 5432: "postgresql", 6379: "redis",
            8080: "http-proxy", 8443: "https-alt", 27017: "mongodb"
        }
    
    async def scan_port(self, target: ScanTarget, pool: AsyncConnectionPool) -> ScanResult:
        """Scan a single port asynchronously."""
        start_time = time.time()
        
        try:
            await pool.rate_limit(target.host)
            
            if target.protocol.lower() == "tcp":
                result = await self._scan_tcp_port(target, pool)
            elif target.protocol.lower() == "udp":
                result = await self._scan_udp_port(target, pool)
            else:
                raise ValueError(f"Unsupported protocol: {target.protocol}")
            
            result.response_time = time.time() - start_time
            return result
            
        except Exception as e:
            return ScanResult(
                target=target,
                is_open=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def _scan_tcp_port(self, target: ScanTarget, pool: AsyncConnectionPool) -> ScanResult:
        """Scan a TCP port with connection reuse."""
        try:
            # Try to get existing connection from pool
            try:
                writer = await pool.get_tcp_connection(target.host, target.port)
                banner = await self._get_banner(target.host, target.port, pool)
                
                return ScanResult(
                    target=target,
                    is_open=True,
                    response_time=0.0,
                    service=self.common_ports.get(target.port, "unknown"),
                    banner=banner
                )
                
            except (ConnectionRefusedError, asyncio.TimeoutError):
                return ScanResult(
                    target=target,
                    is_open=False,
                    response_time=0.0
                )
                
        except Exception as e:
            raise Exception(f"TCP scan failed for {target.host}:{target.port}: {e}")
    
    async def _scan_udp_port(self, target: ScanTarget, pool: AsyncConnectionPool) -> ScanResult:
        """Scan a UDP port."""
        try:
            # UDP scanning is more complex and requires different approach
            # For now, we'll use a simple socket-based approach
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(target.timeout)
            
            try:
                sock.sendto(b"", (target.host, target.port))
                data, addr = sock.recvfrom(1024)
                sock.close()
                
                return ScanResult(
                    target=target,
                    is_open=True,
                    response_time=0.0,
                    service=self.common_ports.get(target.port, "unknown"),
                    banner=data.decode('utf-8', errors='ignore')[:100]
                )
                
            except socket.timeout:
                sock.close()
                return ScanResult(
                    target=target,
                    is_open=False,
                    response_time=0.0
                )
                
        except Exception as e:
            raise Exception(f"UDP scan failed for {target.host}:{target.port}: {e}")
    
    async def _get_banner(self, host: str, port: int, pool: AsyncConnectionPool) -> Optional[str]:
        """Get service banner from open port."""
        try:
            session = await pool.get_http_session()
            
            if port in [80, 443, 8080, 8443]:
                protocol = "https" if port in [443, 8443] else "http"
                url = f"{protocol}://{host}:{port}"
                
                async with session.get(url, timeout=5) as response:
                    server_header = response.headers.get("Server", "")
                    return f"HTTP/{response.version} {response.status} {server_header}"
            
            # For other ports, try to get basic banner
            writer = await pool.get_tcp_connection(host, port)
            writer.write(b"\r\n")
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            await writer.drain()
            
            # Note: This is simplified - real banner grabbing would need more sophisticated handling
            return "Service detected"
            
        except Exception:
            return None
    
    async def scan_host(self, host: str, ports: List[int], 
                       pool: AsyncConnectionPool) -> List[ScanResult]:
        """Scan multiple ports on a single host."""
        targets = [ScanTarget(host=host, port=port) for port in ports]
        return await self.scan_targets(targets, pool)
    
    async def scan_targets(self, targets: List[ScanTarget], 
                          pool: AsyncConnectionPool) -> List[ScanResult]:
        """Scan multiple targets concurrently with connection pooling."""
        semaphore = asyncio.Semaphore(100)  # Limit concurrent scans
        
        async def scan_with_semaphore(target: ScanTarget) -> ScanResult:
            async with semaphore:
                return await self.scan_port(target, pool)
        
        tasks = [scan_with_semaphore(target) for target in targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to ScanResult
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scan task failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results


class AsyncWebEnumerator:
    """High-throughput async web enumeration with connection pooling."""
    
    def __init__(self, pool_config: ConnectionPoolConfig):
        
    """__init__ function."""
self.pool_config = pool_config
        self.common_paths = [
            "/", "/admin", "/login", "/api", "/robots.txt", "/sitemap.xml",
            "/.well-known/security.txt", "/.git/config", "/.env", "/backup",
            "/phpinfo.php", "/test", "/health", "/status", "/metrics"
        ]
    
    async def enumerate_paths(self, base_url: str, paths: List[str], 
                            pool: AsyncConnectionPool) -> List[Dict[str, Any]]:
        """Enumerate web paths asynchronously."""
        session = await pool.get_http_session()
        results = []
        
        async def check_path(path: str) -> Dict[str, Any]:
            try:
                await pool.rate_limit(base_url)
                url = f"{base_url.rstrip('/')}{path}"
                
                async with session.head(url, allow_redirects=True) as response:
                    return {
                        "url": url,
                        "status_code": response.status,
                        "content_length": response.headers.get("Content-Length", "0"),
                        "content_type": response.headers.get("Content-Type", ""),
                        "server": response.headers.get("Server", ""),
                        "exists": response.status < 400
                    }
                    
            except Exception as e:
                return {
                    "url": url,
                    "status_code": 0,
                    "error": str(e),
                    "exists": False
                }
        
        # Create tasks for all paths
        tasks = [check_path(path) for path in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        return valid_results
    
    async def scan_subdomains(self, domain: str, subdomains: List[str], 
                            pool: AsyncConnectionPool) -> List[Dict[str, Any]]:
        """Scan for subdomain existence asynchronously."""
        session = await pool.get_http_session()
        results = []
        
        async def check_subdomain(subdomain: str) -> Dict[str, Any]:
            try:
                await pool.rate_limit(domain)
                url = f"http://{subdomain}.{domain}"
                
                async with session.head(url, timeout=5, allow_redirects=True) as response:
                    return {
                        "subdomain": subdomain,
                        "url": url,
                        "status_code": response.status,
                        "exists": response.status < 400,
                        "server": response.headers.get("Server", ""),
                        "ip": response.connection.transport.get_extra_info("peername")[0]
                    }
                    
            except Exception as e:
                return {
                    "subdomain": subdomain,
                    "url": url,
                    "status_code": 0,
                    "exists": False,
                    "error": str(e)
                }
        
        # Create tasks for all subdomains
        tasks = [check_subdomain(subdomain) for subdomain in subdomains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]
        return valid_results


class AsyncNetworkScanner:
    """High-throughput async network scanner with connection pooling."""
    
    def __init__(self, pool_config: ConnectionPoolConfig):
        
    """__init__ function."""
self.pool_config = pool_config
        self.port_scanner = AsyncPortScanner(pool_config)
        self.web_enumerator = AsyncWebEnumerator(pool_config)
    
    async def comprehensive_scan(self, targets: List[str], 
                               ports: List[int] = None,
                               web_paths: List[str] = None) -> Dict[str, Any]:
        """Perform comprehensive network scanning with connection pooling."""
        if ports is None:
            ports = list(self.port_scanner.common_ports.keys())
        
        if web_paths is None:
            web_paths = self.web_enumerator.common_paths
        
        async with AsyncConnectionPool(self.pool_config) as pool:
            # Phase 1: Port scanning
            logger.info(f"Starting port scan for {len(targets)} targets")
            port_targets = []
            for target in targets:
                for port in ports:
                    port_targets.append(ScanTarget(host=target, port=port))
            
            port_results = await self.port_scanner.scan_targets(port_targets, pool)
            
            # Phase 2: Web enumeration for HTTP/HTTPS ports
            logger.info("Starting web enumeration")
            web_targets = []
            for result in port_results:
                if result.is_open and result.target.port in [80, 443, 8080, 8443]:
                    protocol = "https" if result.target.port in [443, 8443] else "http"
                    base_url = f"{protocol}://{result.target.host}:{result.target.port}"
                    web_targets.append(base_url)
            
            web_results = []
            for base_url in web_targets:
                paths_result = await self.web_enumerator.enumerate_paths(
                    base_url, web_paths, pool
                )
                web_results.extend(paths_result)
            
            # Compile results
            return {
                "scan_timestamp": datetime.now().isoformat(),
                "targets_scanned": len(targets),
                "ports_scanned": len(ports),
                "port_results": [result.__dict__ for result in port_results],
                "web_results": web_results,
                "pool_stats": pool.get_stats(),
                "summary": {
                    "open_ports": len([r for r in port_results if r.is_open]),
                    "web_services": len(web_targets),
                    "discovered_paths": len([r for r in web_results if r.get("exists", False)])
                }
            }


# Example usage and testing functions
async def demonstrate_high_throughput_scanning():
    """Demonstrate high-throughput scanning capabilities."""
    
    # Configuration for high-performance scanning
    config = ConnectionPoolConfig(
        max_connections=200,
        max_connections_per_host=20,
        connection_timeout=5.0,
        keepalive_timeout=60.0,
        retry_attempts=2,
        rate_limit_per_second=200,
        rate_limit_burst=100
    )
    
    # Sample targets for demonstration
    targets = [
        "example.com",
        "google.com", 
        "github.com",
        "stackoverflow.com"
    ]
    
    scanner = AsyncNetworkScanner(config)
    
    logger.info("Starting high-throughput network scan...")
    start_time = time.time()
    
    try:
        results = await scanner.comprehensive_scan(targets)
        
        scan_duration = time.time() - start_time
        logger.info(f"Scan completed in {scan_duration:.2f} seconds")
        logger.info(f"Pool stats: {results['pool_stats']}")
        logger.info(f"Summary: {results['summary']}")
        
        # Print some key findings
        open_ports = [r for r in results['port_results'] if r['is_open']]
        logger.info(f"Found {len(open_ports)} open ports")
        
        web_findings = [r for r in results['web_results'] if r.get('exists', False)]
        logger.info(f"Found {len(web_findings)} accessible web paths")
        
        return results
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_high_throughput_scanning()) 