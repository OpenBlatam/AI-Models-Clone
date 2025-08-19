from typing_extensions import Literal, TypedDict
from typing import Any, Dict, List, Optional, Tuple, Union
# Constants
MAX_RETRIES = 100

import asyncio
import socket
from dataclasses import dataclass
from datetime import datetime
import logging
"""
Port Scanner Module
==================

A modular port scanner implementation following lowercase_underscores naming convention.
"""


@dataclass(frozen=True)
class PortScanResult:
    """Result of a port scan operation."""
    target_host: str
    target_port: int
    is_port_open: bool
    service_name: Optional[str] = None
    response_time: Optional[float] = None
    scan_timestamp: datetime = None
    error_message: Optional[str] = None

class AsyncPortScanner:
    """Asynchronous port scanner with descriptive naming."""

    def __init__(self, max_concurrent_scans: int = 100, timeout_seconds: float = 5.0):
        """Initialize scanner with concurrency and timeout settings."""
        self.max_concurrent_scans = max_concurrent_scans
        self.timeout_seconds = timeout_seconds
        self.scan_semaphore = asyncio.Semaphore(max_concurrent_scans)
        
        # Common service ports mapping
        self.service_port_mapping = {
            21: "ftp",
            22: "ssh", 
            23: "telnet",
            25: "smtp",
            53: "dns",
            80: "http",
            110: "pop3",
            143: "imap",
            443: "https",
            993: "imaps",
            995: "pop3s",
            3306: "mysql",
            5432: "postgresql",
            6379: "redis",
            8080: "http_alt",
            8443: "https_alt"
        }
    
    async def scan_single_port(self, target_host: str, target_port: int) -> PortScanResult:
        """Scan a single port asynchronously."""
        async with self.scan_semaphore:
            scan_start_time = asyncio.get_event_loop().time()
            
            try:
                # Create connection with timeout
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target_host, target_port),
                    timeout=self.timeout_seconds
                )
                
                # Calculate response time
                response_time = asyncio.get_event_loop().time() - scan_start_time
                
                # Get service name
                service_name = self.service_port_mapping.get(target_port, "unknown")
                
                # Close connection
                writer.close()
                await writer.wait_closed()
                
                return PortScanResult(
                    target_host=target_host,
                    target_port=target_port,
                    is_port_open=True,
                    service_name=service_name,
                    response_time=response_time,
                    scan_timestamp=datetime.utcnow()
                )
                
            except asyncio.TimeoutError:
                return PortScanResult(
                    target_host=target_host,
                    target_port=target_port,
                    is_port_open=False,
                    scan_timestamp=datetime.utcnow(),
                    error_message="Connection timeout"
                )
            except ConnectionRefusedError:
                return PortScanResult(
                    target_host=target_host,
                    target_port=target_port,
                    is_port_open=False,
                    scan_timestamp=datetime.utcnow(),
                    error_message="Connection refused"
                )
            except Exception as e:
                return PortScanResult(
                    target_host=target_host,
                    target_port=target_port,
                    is_port_open=False,
                    scan_timestamp=datetime.utcnow(),
                    error_message=str(e)
                )
    
    async def scan_port_range(
        self, 
        target_host: str, 
        start_port: int, 
        end_port: int
    ) -> List[PortScanResult]:
        """Scan a range of ports concurrently."""
        scan_tasks = []
        
        for port in range(start_port, end_port + 1):
            task = self.scan_single_port(target_host, port)
            scan_tasks.append(task)
        
        scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in scan_results:
            if isinstance(result, Exception):
                # Handle task exceptions
                continue
            valid_results.append(result)
        
        return valid_results
    
    async def scan_common_ports(self, target_host: str) -> List[PortScanResult]:
        """Scan commonly used ports."""
        common_ports = list(self.service_port_mapping.keys())
        return await self.scan_port_range(target_host, min(common_ports), max(common_ports))
    
    def filter_open_ports(self, scan_results: List[PortScanResult]) -> List[PortScanResult]:
        """Filter results to show only open ports."""
        return [result for result in scan_results if result.is_port_open]
    
    def group_by_service(self, scan_results: List[PortScanResult]) -> Dict[str, List[PortScanResult]]:
        """Group scan results by service name."""
        service_groups = {}
        
        for result in scan_results:
            if result.service_name:
                if result.service_name not in service_groups:
                    service_groups[result.service_name] = []
                service_groups[result.service_name].append(result)
        
        return service_groups

# Usage example
async def main():
    """Example usage of the port scanner."""
    port_scanner = AsyncPortScanner(max_concurrent_scans=50, timeout_seconds=3.0)
    
    # Scan common ports on localhost
    target_host = "127.0.0.1"
    scan_results = await port_scanner.scan_common_ports(target_host)
    
    # Filter open ports
    open_ports = port_scanner.filter_open_ports(scan_results)
    
    # Group by service
    service_groups = port_scanner.group_by_service(open_ports)
    
    print(f"Scan completed for {target_host}")
    print(f"Found {len(open_ports)} open ports")
    
    for service_name, ports in service_groups.items():
        print(f"\n{service_name.upper()} ports:")
        for port_result in ports:
            print(f"  - Port {port_result.target_port} (Response time: {port_result.response_time:.3f}s)")

# Run: asyncio.run(main()) 