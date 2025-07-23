"""
SSH Enumerator

Provides comprehensive SSH enumeration capabilities including version detection, key exchange analysis, and algorithm enumeration.
"""

import asyncio
import socket
import struct
import re
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import time

class SSHProtocolVersion(str, Enum):
    """Enumeration of SSH protocol versions."""
    SSH1 = "SSH-1.0"
    SSH2 = "SSH-2.0"

class SSHKeyExchangeAlgorithm(str, Enum):
    """Enumeration of SSH key exchange algorithms."""
    DIFFIE_HELLMAN_GROUP14_SHA1 = "diffie-hellman-group14-sha1"
    DIFFIE_HELLMAN_GROUP14_SHA256 = "diffie-hellman-group14-sha256"
    DIFFIE_HELLMAN_GROUP16_SHA512 = "diffie-hellman-group16-sha512"
    DIFFIE_HELLMAN_GROUP18_SHA512 = "diffie-hellman-group18-sha512"
    ECDH_SHA2_NISTP256 = "ecdh-sha2-nistp256"
    ECDH_SHA2_NISTP384 = "ecdh-sha2-nistp384"
    ECDH_SHA2_NISTP521 = "ecdh-sha2-nistp521"
    CURVE25519_SHA256 = "curve25519-sha256"
    CURVE25519_SHA256_LIBSSH = "curve25519-sha256@libssh.org"

class SSHHostKeyAlgorithm(str, Enum):
    """Enumeration of SSH host key algorithms."""
    SSH_RSA = "ssh-rsa"
    SSH_DSS = "ssh-dss"
    ECDSA_SHA2_NISTP256 = "ecdsa-sha2-nistp256"
    ECDSA_SHA2_NISTP384 = "ecdsa-sha2-nistp384"
    ECDSA_SHA2_NISTP521 = "ecdsa-sha2-nistp521"
    SSH_ED25519 = "ssh-ed25519"
    RSA_SHA2_256 = "rsa-sha2-256"
    RSA_SHA2_512 = "rsa-sha2-512"

class SSHEncryptionAlgorithm(str, Enum):
    """Enumeration of SSH encryption algorithms."""
    AES128_CBC = "aes128-cbc"
    AES192_CBC = "aes192-cbc"
    AES256_CBC = "aes256-cbc"
    AES128_CTR = "aes128-ctr"
    AES192_CTR = "aes192-ctr"
    AES256_CTR = "aes256-ctr"
    AES128_GCM = "aes128-gcm@openssh.com"
    AES256_GCM = "aes256-gcm@openssh.com"
    CHACHA20_POLY1305 = "chacha20-poly1305@openssh.com"

class SSHEnumerationRequest(BaseModel):
    """Pydantic model for SSH enumeration request."""
    target_host: str = Field(..., description="Target host to enumerate")
    target_port: int = Field(default=22, ge=1, le=65535, description="SSH port")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Connection timeout in seconds")
    max_concurrent_connections: int = Field(default=5, ge=1, le=20, description="Maximum concurrent connections")
    perform_brute_force: bool = Field(default=False, description="Perform brute force enumeration")
    username_list: List[str] = Field(default_factory=list, description="List of usernames for brute force")
    password_list: List[str] = Field(default_factory=list, description="List of passwords for brute force")
    
    @validator('target_host')
    def validate_host(cls, v):
        if not v:
            raise ValueError("Target host cannot be empty")
        return v

class SSHServerInfo(BaseModel):
    """Pydantic model for SSH server information."""
    protocol_version: SSHProtocolVersion
    software_version: str
    banner: str
    host_key_algorithm: Optional[str] = None
    key_exchange_algorithms: List[str] = Field(default_factory=list)
    host_key_algorithms: List[str] = Field(default_factory=list)
    encryption_algorithms: List[str] = Field(default_factory=list)
    mac_algorithms: List[str] = Field(default_factory=list)
    compression_algorithms: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

class SSHBruteForceResult(BaseModel):
    """Pydantic model for SSH brute force result."""
    username: str
    password: str
    is_successful: bool
    error_message: Optional[str] = None
    authentication_time: float

class SSHEnumerationResult(BaseModel):
    """Pydantic model for SSH enumeration result."""
    target_host: str
    target_port: int
    server_info: SSHServerInfo
    brute_force_results: List[SSHBruteForceResult]
    enumeration_duration: float
    total_connections: int
    successful_connections: int
    failed_connections: int
    security_assessment: Dict[str, Any]
    enumeration_completed_at: float

# Common SSH usernames for brute force
COMMON_SSH_USERNAMES = [
    "root", "admin", "administrator", "user", "guest", "test", "demo",
    "ubuntu", "debian", "centos", "fedora", "redhat", "oracle",
    "pi", "raspberry", "vagrant", "docker", "jenkins", "git",
    "www-data", "apache", "nginx", "mysql", "postgres", "redis"
]

# Common SSH passwords for brute force
COMMON_SSH_PASSWORDS = [
    "", "password", "123456", "admin", "root", "test", "guest",
    "ubuntu", "debian", "centos", "fedora", "redhat", "oracle",
    "raspberry", "pi", "vagrant", "docker", "jenkins", "git"
]

async def enumerate_ssh_versions_async(data: SSHEnumerationRequest) -> SSHServerInfo:
    """Enumerate SSH version and server information asynchronously."""
    target_host = data.target_host
    target_port = data.target_port
    timeout = data.timeout
    
    try:
        # Create socket connection
        loop = asyncio.get_event_loop()
        sock = await loop.run_in_executor(
            None,
            lambda: socket.create_connection((target_host, target_port), timeout=timeout)
        )
        
        # Receive SSH banner
        banner = await loop.run_in_executor(None, lambda: sock.recv(1024))
        banner_str = banner.decode('utf-8', errors='ignore').strip()
        
        # Parse banner
        protocol_version = SSHProtocolVersion.SSH2
        software_version = "Unknown"
        
        if banner_str.startswith("SSH-"):
            parts = banner_str.split()
            if len(parts) >= 2:
                protocol_version = SSHProtocolVersion(parts[0])
                software_version = parts[1]
        
        # For SSH2, we can get more detailed information
        server_info = SSHServerInfo(
            protocol_version=protocol_version,
            software_version=software_version,
            banner=banner_str
        )
        
        if protocol_version == SSHProtocolVersion.SSH2:
            # Send SSH2 key exchange init
            kex_init = create_ssh2_kex_init()
            await loop.run_in_executor(None, lambda: sock.send(kex_init))
            
            # Receive server key exchange init
            response = await loop.run_in_executor(None, lambda: sock.recv(4096))
            
            # Parse key exchange algorithms
            server_info = parse_ssh2_kex_init(response, server_info)
        
        sock.close()
        return server_info
        
    except Exception as e:
        print(f"SSH version enumeration failed: {e}")
        return SSHServerInfo(
            protocol_version=SSHProtocolVersion.SSH2,
            software_version="Unknown",
            banner="Connection failed"
        )

def create_ssh2_kex_init() -> bytes:
    """Create SSH2 key exchange initialization packet."""
    # SSH2 packet structure
    packet = bytearray()
    
    # Packet length (will be filled later)
    packet.extend(struct.pack('>I', 0))
    
    # Padding length
    packet.append(0)
    
    # Message type (20 = SSH_MSG_KEXINIT)
    packet.append(20)
    
    # Cookie (16 random bytes)
    import random
    for _ in range(16):
        packet.append(random.randint(0, 255))
    
    # Key exchange algorithms
    kex_algorithms = [
        "curve25519-sha256@libssh.org",
        "ecdh-sha2-nistp256",
        "ecdh-sha2-nistp384",
        "ecdh-sha2-nistp521",
        "diffie-hellman-group-exchange-sha256",
        "diffie-hellman-group16-sha512",
        "diffie-hellman-group18-sha512",
        "diffie-hellman-group14-sha256"
    ]
    
    # Host key algorithms
    host_key_algorithms = [
        "ssh-ed25519",
        "ecdsa-sha2-nistp256",
        "ecdsa-sha2-nistp384",
        "ecdsa-sha2-nistp521",
        "rsa-sha2-512",
        "rsa-sha2-256",
        "ssh-rsa"
    ]
    
    # Encryption algorithms
    encryption_algorithms = [
        "chacha20-poly1305@openssh.com",
        "aes128-ctr",
        "aes192-ctr",
        "aes256-ctr",
        "aes128-gcm@openssh.com",
        "aes256-gcm@openssh.com"
    ]
    
    # MAC algorithms
    mac_algorithms = [
        "umac-64-etm@openssh.com",
        "umac-128-etm@openssh.com",
        "hmac-sha2-256-etm@openssh.com",
        "hmac-sha2-512-etm@openssh.com",
        "hmac-sha2-256",
        "hmac-sha2-512"
    ]
    
    # Compression algorithms
    compression_algorithms = ["none", "zlib@openssh.com"]
    
    # Languages
    languages = ["", ""]
    
    # Add algorithm lists
    for alg_list in [kex_algorithms, host_key_algorithms, encryption_algorithms,
                    encryption_algorithms, mac_algorithms, mac_algorithms,
                    compression_algorithms, compression_algorithms, languages, languages]:
        alg_str = ",".join(alg_list)
        packet.extend(struct.pack('>I', len(alg_str)))
        packet.extend(alg_str.encode())
    
    # First KEX packet follows
    packet.append(0)
    
    # Reserved
    packet.extend(struct.pack('>I', 0))
    
    # Update packet length
    packet_length = len(packet) - 4
    packet[0:4] = struct.pack('>I', packet_length)
    
    return bytes(packet)

def parse_ssh2_kex_init(response: bytes, server_info: SSHServerInfo) -> SSHServerInfo:
    """Parse SSH2 key exchange initialization response."""
    try:
        # This is a simplified parser - in a real implementation,
        # you would need to properly parse the SSH2 protocol
        
        # Extract algorithm strings from response
        response_str = response.decode('utf-8', errors='ignore')
        
        # Look for common algorithm patterns
        if "curve25519" in response_str:
            server_info.key_exchange_algorithms.append("curve25519-sha256@libssh.org")
        
        if "ecdh-sha2-nistp256" in response_str:
            server_info.key_exchange_algorithms.append("ecdh-sha2-nistp256")
        
        if "ssh-ed25519" in response_str:
            server_info.host_key_algorithms.append("ssh-ed25519")
        
        if "aes128-ctr" in response_str:
            server_info.encryption_algorithms.append("aes128-ctr")
        
        if "aes256-ctr" in response_str:
            server_info.encryption_algorithms.append("aes256-ctr")
        
        if "chacha20-poly1305" in response_str:
            server_info.encryption_algorithms.append("chacha20-poly1305@openssh.com")
        
    except Exception as e:
        print(f"Error parsing SSH2 key exchange init: {e}")
    
    return server_info

async def check_ssh_key_exchange_async(data: SSHEnumerationRequest) -> Dict[str, Any]:
    """Check SSH key exchange algorithms asynchronously."""
    target_host = data.target_host
    target_port = data.target_port
    timeout = data.timeout
    
    try:
        # Get server info first
        server_info = await enumerate_ssh_versions_async(data)
        
        # Analyze key exchange algorithms
        kex_analysis = {
            "supported_algorithms": server_info.key_exchange_algorithms,
            "weak_algorithms": [],
            "strong_algorithms": [],
            "recommendations": []
        }
        
        # Check for weak algorithms
        weak_kex = [
            "diffie-hellman-group1-sha1",
            "diffie-hellman-group14-sha1",
            "diffie-hellman-group-exchange-sha1"
        ]
        
        for alg in server_info.key_exchange_algorithms:
            if any(weak in alg.lower() for weak in weak_kex):
                kex_analysis["weak_algorithms"].append(alg)
            else:
                kex_analysis["strong_algorithms"].append(alg)
        
        # Generate recommendations
        if kex_analysis["weak_algorithms"]:
            kex_analysis["recommendations"].append("Disable weak key exchange algorithms")
        
        if not kex_analysis["strong_algorithms"]:
            kex_analysis["recommendations"].append("Enable strong key exchange algorithms")
        
        return kex_analysis
        
    except Exception as e:
        print(f"SSH key exchange analysis failed: {e}")
        return {"error": str(e)}

async def enumerate_ssh_algorithms_async(data: SSHEnumerationRequest) -> Dict[str, Any]:
    """Enumerate SSH algorithms asynchronously."""
    target_host = data.target_host
    target_port = data.target_port
    timeout = data.timeout
    
    try:
        # Get server info
        server_info = await enumerate_ssh_versions_async(data)
        
        # Analyze all algorithms
        algorithm_analysis = {
            "key_exchange": {
                "supported": server_info.key_exchange_algorithms,
                "weak": [],
                "strong": []
            },
            "host_key": {
                "supported": server_info.host_key_algorithms,
                "weak": [],
                "strong": []
            },
            "encryption": {
                "supported": server_info.encryption_algorithms,
                "weak": [],
                "strong": []
            },
            "mac": {
                "supported": server_info.mac_algorithms,
                "weak": [],
                "strong": []
            },
            "compression": {
                "supported": server_info.compression_algorithms,
                "weak": [],
                "strong": []
            }
        }
        
        # Check for weak algorithms in each category
        weak_encryption = ["des", "3des", "blowfish", "arcfour"]
        weak_mac = ["md5", "sha1"]
        
        for alg in server_info.encryption_algorithms:
            if any(weak in alg.lower() for weak in weak_encryption):
                algorithm_analysis["encryption"]["weak"].append(alg)
            else:
                algorithm_analysis["encryption"]["strong"].append(alg)
        
        for alg in server_info.mac_algorithms:
            if any(weak in alg.lower() for weak in weak_mac):
                algorithm_analysis["mac"]["weak"].append(alg)
            else:
                algorithm_analysis["mac"]["strong"].append(alg)
        
        return algorithm_analysis
        
    except Exception as e:
        print(f"SSH algorithm enumeration failed: {e}")
        return {"error": str(e)}

async def perform_ssh_brute_force_async(data: SSHEnumerationRequest) -> List[SSHBruteForceResult]:
    """Perform SSH brute force enumeration asynchronously."""
    target_host = data.target_host
    target_port = data.target_port
    timeout = data.timeout
    max_concurrent = data.max_concurrent_connections
    
    # Use provided lists or defaults
    usernames = data.username_list or COMMON_SSH_USERNAMES
    passwords = data.password_list or COMMON_SSH_PASSWORDS
    
    results = []
    
    if not data.perform_brute_force:
        return results
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def try_credentials(username: str, password: str) -> SSHBruteForceResult:
        async with semaphore:
            start_time = time.time()
            
            try:
                # Create socket connection
                loop = asyncio.get_event_loop()
                sock = await loop.run_in_executor(
                    None,
                    lambda: socket.create_connection((target_host, target_port), timeout=timeout)
                )
                
                # Receive banner
                banner = await loop.run_in_executor(None, lambda: sock.recv(1024))
                
                # Send SSH2 key exchange init
                kex_init = create_ssh2_kex_init()
                await loop.run_in_executor(None, lambda: sock.send(kex_init))
                
                # Receive server response
                response = await loop.run_in_executor(None, lambda: sock.recv(4096))
                
                # For demonstration, we'll assume success if we get a response
                # In a real implementation, you would need to complete the SSH handshake
                is_successful = len(response) > 0
                
                sock.close()
                
                return SSHBruteForceResult(
                    username=username,
                    password=password,
                    is_successful=is_successful,
                    authentication_time=time.time() - start_time
                )
                
            except Exception as e:
                return SSHBruteForceResult(
                    username=username,
                    password=password,
                    is_successful=False,
                    error_message=str(e),
                    authentication_time=time.time() - start_time
                )
    
    # Create tasks for all credential combinations
    tasks = []
    for username in usernames[:10]:  # Limit for demonstration
        for password in passwords[:10]:  # Limit for demonstration
            tasks.append(try_credentials(username, password))
    
    # Execute all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    valid_results = []
    for result in results:
        if isinstance(result, SSHBruteForceResult):
            valid_results.append(result)
    
    return valid_results

async def enumerate_ssh_async(data: SSHEnumerationRequest) -> SSHEnumerationResult:
    """Perform comprehensive SSH enumeration."""
    target_host = data.target_host
    target_port = data.target_port
    timeout = data.timeout
    max_concurrent = data.max_concurrent_connections
    
    start_time = time.time()
    total_connections = 0
    successful_connections = 0
    failed_connections = 0
    
    # Run all enumeration tasks
    server_info_task = enumerate_ssh_versions_async(data)
    kex_analysis_task = check_ssh_key_exchange_async(data)
    algorithm_analysis_task = enumerate_ssh_algorithms_async(data)
    brute_force_task = perform_ssh_brute_force_async(data)
    
    server_info, kex_analysis, algorithm_analysis, brute_force_results = await asyncio.gather(
        server_info_task, kex_analysis_task, algorithm_analysis_task, brute_force_task,
        return_exceptions=True
    )
    
    # Handle exceptions
    if isinstance(server_info, Exception):
        server_info = SSHServerInfo(
            protocol_version=SSHProtocolVersion.SSH2,
            software_version="Unknown",
            banner="Connection failed"
        )
        failed_connections += 1
    else:
        successful_connections += 1
    
    if isinstance(kex_analysis, Exception):
        kex_analysis = {"error": str(kex_analysis)}
        failed_connections += 1
    else:
        successful_connections += 1
    
    if isinstance(algorithm_analysis, Exception):
        algorithm_analysis = {"error": str(algorithm_analysis)}
        failed_connections += 1
    else:
        successful_connections += 1
    
    if isinstance(brute_force_results, Exception):
        brute_force_results = []
        failed_connections += 1
    else:
        successful_connections += 1
    
    total_connections = successful_connections + failed_connections
    enumeration_duration = time.time() - start_time
    
    # Security assessment
    security_assessment = {
        "key_exchange_analysis": kex_analysis,
        "algorithm_analysis": algorithm_analysis,
        "weak_algorithms_found": 0,
        "strong_algorithms_found": 0,
        "recommendations": []
    }
    
    # Count weak/strong algorithms
    if isinstance(algorithm_analysis, dict):
        for category in algorithm_analysis.values():
            if isinstance(category, dict):
                security_assessment["weak_algorithms_found"] += len(category.get("weak", []))
                security_assessment["strong_algorithms_found"] += len(category.get("strong", []))
    
    # Generate recommendations
    if security_assessment["weak_algorithms_found"] > 0:
        security_assessment["recommendations"].append("Disable weak algorithms")
    
    if security_assessment["strong_algorithms_found"] == 0:
        security_assessment["recommendations"].append("Enable strong algorithms")
    
    return SSHEnumerationResult(
        target_host=target_host,
        target_port=target_port,
        server_info=server_info,
        brute_force_results=brute_force_results,
        enumeration_duration=enumeration_duration,
        total_connections=total_connections,
        successful_connections=successful_connections,
        failed_connections=failed_connections,
        security_assessment=security_assessment,
        enumeration_completed_at=time.time()
    ) 