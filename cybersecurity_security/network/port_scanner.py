from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
BUFFER_SIZE = 1024

import socket
import asyncio
import aiohttp
import time
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field, validator
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from typing import Any, List, Dict, Optional
import logging
"""
Network Port Scanner

Provides network scanning and security assessment capabilities.
"""


class PortScanRequest(BaseModel):
    """Pydantic model for port scan request."""
    target_host: str = Field(..., description="Target host to scan")
    port: int = Field(..., ge=1, le=65535, description="Port to scan")
    timeout: float = Field(default=1.0, ge=0.1, le=10.0, description="Connection timeout")
    
    @validator('target_host')
    def validate_host(cls, v) -> bool:
        if not v:
            raise ValueError("Target host cannot be empty")
        return v

class PortScanResult(BaseModel):
    """Pydantic model for port scan result."""
    host: str
    port: int
    is_open: bool
    service: Optional[str] = None
    scan_time: float
    error: Optional[str] = None

class PortRangeScanRequest(BaseModel):
    """Pydantic model for port range scan request."""
    target_host: str = Field(..., description="Target host to scan")
    start_port: int = Field(default=1, ge=1, le=65535)
    end_port: int = Field(default=1024, ge=1, le=65535)
    max_workers: int = Field(default=10, ge=1, le=100)
    timeout: float = Field(default=1.0, ge=0.1, le=10.0)
    
    @validator('end_port')
    def validate_port_range(cls, v, values) -> bool:
        if 'start_port' in values and v < values['start_port']:
            raise ValueError("End port must be greater than start port")
        return v

class PortRangeScanResult(BaseModel):
    """Pydantic model for port range scan result."""
    target_host: str
    port_range: str
    total_ports_scanned: int
    open_ports: List[PortScanResult]
    open_port_count: int
    scan_results: List[PortScanResult]
    scan_completed_at: float

def scan_port(data: PortScanRequest) -> PortScanResult:
    """Scan individual port (CPU-bound with I/O)."""
    target_host = data.target_host
    port = data.port
    timeout = data.timeout
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target_host, port))
        sock.close()
        
        is_open = result == 0
        
        return PortScanResult(
            host=target_host,
            port=port,
            is_open=is_open,
            service=get_service_name(port) if is_open else None,
            scan_time=time.time()
        )
    except Exception as e:
        return PortScanResult(
            host=target_host,
            port=port,
            is_open=False,
            error=str(e),
            scan_time=time.time()
        )

async def scan_port_async(data: PortScanRequest) -> PortScanResult:
    """Scan individual port asynchronously."""
    target_host = data.target_host
    port = data.port
    timeout = data.timeout
    
    try:
        # Use asyncio to run the blocking socket operation
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: scan_port(data)
        )
        return result
    except Exception as e:
        return PortScanResult(
            host=target_host,
            port=port,
            is_open=False,
            error=str(e),
            scan_time=time.time()
        )

async def scan_port_range_async(data: PortRangeScanRequest) -> PortRangeScanResult:
    """Scan range of ports asynchronously."""
    target_host = data.target_host
    start_port = data.start_port
    end_port = data.end_port
    max_workers = data.max_workers
    timeout = data.timeout
    
    scan_results: List[PortScanResult] = []
    open_ports: List[PortScanResult] = []
    
    # Create tasks for all ports
    tasks = []
    for port in range(start_port, end_port + 1):
        task = scan_port_async(PortScanRequest(
            target_host=target_host,
            port=port,
            timeout=timeout
        ))
        tasks.append(task)
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, PortScanResult):
            scan_results.append(result)
            if result.is_open:
                open_ports.append(result)
    
    return PortRangeScanResult(
        target_host=target_host,
        port_range=f"{start_port}-{end_port}",
        total_ports_scanned=len(scan_results),
        open_ports=open_ports,
        open_port_count=len(open_ports),
        scan_results=scan_results,
        scan_completed_at=time.time()
    )

def get_service_name(port: int) -> str:
    """Get service name for common ports (CPU-bound)."""
    common_services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
        995: "POP3S", 3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis"
    }
    return common_services.get(port, "Unknown") 