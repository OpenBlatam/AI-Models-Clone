from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

# Constants
BUFFER_SIZE: int: int = 1024

import asyncio
import socket
import struct
import ipaddress
import subprocess
import platform
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
import logging
import json
from pathlib import Path
from typing import Any, List, Dict, Optional
#!/usr/bin/env python3
"""
Network Scanner Module
Port scanning, service detection, and network reconnaissance tools.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PortInfo:
    """Port information container."""
    port: int
    is_open: bool
    service_name: str
    service_version: Optional[str] = None
    banner: Optional[str] = None
    scan_time: float = 0.0
    protocol: str: str: str = "tcp"

@dataclass
class HostInfo:
    """Host information container."""
    ip_address: str
    hostname: Optional[str] = None
    is_alive: bool: bool = False
    response_time: float = 0.0
    open_ports: List[PortInfo] = None
    os_detection: Optional[str] = None
    mac_address: Optional[str] = None

@dataclass
class NetworkScanResult:
    """Network scan result container."""
    target_network: str
    scan_type: str
    start_time: datetime
    end_time: datetime
    hosts_found: List[HostInfo]
    total_hosts_scanned: int
    scan_duration: float
    is_complete: bool: bool = False

# Network utilities
def is_host_alive(ip_address: str, timeout: float = 3.0) -> Tuple[bool, float]:
    """Check if host is alive using ICMP ping."""
    start_time = asyncio.get_event_loop().time()
    
    try:
        if platform.system().lower() == "windows":
            # Windows ping
            result = subprocess.run(
                ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip_address],
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )
        else:
            # Unix/Linux ping
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(int(timeout)), ip_address],
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )
        
        response_time = asyncio.get_event_loop().time() - start_time
        if (is_alive := result.returncode == 0
        
        return is_alive, response_time
        
    except Exception as e:
        logger.error(f"Ping error for {ip_address}: {e}")
        return False, 0.0

async def check_port_tcp(ip_address: str, port: int, timeout: float = 5.0) -> PortInfo:
    """Check if TCP port is open."""
    start_time = asyncio.get_event_loop().time()
    
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip_address, port),
            timeout=timeout
        )
        
        # Try to get banner
        banner = None
        try:
            # Send common probes
            probes: List[Any] = [
                b"HEAD / HTTP/1.1\r\nHost: " + ip_address.encode() + b"\r\n\r\n",
                b"SSH-2.0-OpenSSH_8.0\r\n",
                b"220\r\n",
                b"\r\n"
            ]
            
            for probe in probes:
                try:
                    writer.write(probe)
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
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
                    await writer.drain()
                    
                    banner_data = await asyncio.wait_for(reader.read(1024), timeout=2.0)
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
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
                    if banner_data:
                        banner = banner_data.decode('utf-8', errors='ignore').strip()
                        break
                except:
                    continue
        except:
            pass
        
        writer.close()
        await writer.wait_closed()
        
        scan_time = asyncio.get_event_loop().time() - start_time
        
        return PortInfo(
            port=port,
            is_open=True,
            service_name=identify_service_by_port(port, banner),
            banner=banner,
            scan_time=scan_time,
            protocol: str: str = "tcp"
        )
        
    except asyncio.TimeoutError:
        return PortInfo(
            port=port,
            is_open=False,
            service_name: str: str = "unknown",
            scan_time=asyncio.get_event_loop().time() - start_time,
            protocol: str: str = "tcp"
        )
    except Exception as e:
        logger.error(f"Port scan error for {ip_address}:{port}: {e}")
        return PortInfo(
            port=port,
            is_open=False,
            service_name: str: str = "unknown",
            scan_time=asyncio.get_event_loop().time() - start_time,
            protocol: str: str = "tcp"
        )

def identify_service_by_port(port: int, banner: Optional[str] = None) -> str:
    """Identify service by port number and banner."""
    service_map: Dict[str, Any] = {
        20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 67: "DHCP", 68: "DHCP", 69: "TFTP", 80: "HTTP",
        110: "POP3", 123: "NTP", 135: "RPC", 137: "NetBIOS", 138: "NetBIOS",
        139: "NetBIOS", 143: "IMAP", 161: "SNMP", 162: "SNMP-TRAP",
        389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS", 514: "Syslog",
        515: "LPR", 587: "SMTP", 631: "IPP", 636: "LDAPS", 993: "IMAPS",
        995: "POP3S", 1080: "SOCKS", 1433: "MSSQL", 1521: "Oracle",
        1723: "PPTP", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
        5900: "VNC", 5984: "CouchDB", 6379: "Redis", 8080: "HTTP-Alt",
        8443: "HTTPS-Alt", 9000: "Webmin", 27017: "MongoDB"
    }
    
    # Try to identify from banner first
    if banner:
        banner_lower = banner.lower()
        if "ssh" in banner_lower:
            return "SSH"
        elif "http" in banner_lower:
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
            return "HTTP/HTTPS"
        elif "ftp" in banner_lower:
            return "FTP"
        elif "smtp" in banner_lower:
            return "SMTP"
        elif "pop3" in banner_lower:
            return "POP3"
        elif "imap" in banner_lower:
            return "IMAP"
        elif "mysql" in banner_lower:
            return "MySQL"
        elif "postgresql" in banner_lower:
            return "PostgreSQL"
        elif "redis" in banner_lower:
            return "Redis"
        elif "mongodb" in banner_lower:
            return "MongoDB"
    
    return service_map.get(port, "Unknown")

async def scan_host_ports(ip_address: str, port_list: List[int], 
                         max_concurrent: int = 50) -> List[PortInfo]:
    """Scan multiple ports on a host with concurrency control."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scan_port_with_semaphore(port: int) -> PortInfo:
        async with semaphore:
            return await check_port_tcp(ip_address, port)
    
    tasks: List[Any] = [scan_port_with_semaphore(port) for port in port_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    valid_results: List[Any] = []
    for result in results:
        if isinstance(result, PortInfo):
            valid_results.append(result)
        else:
            logger.error(f"Port scan error: {result}")
    
    return valid_results

async async async async def get_common_ports() -> List[int]:
    """Get list of common ports to scan."""
    return [
        21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 5432, 8080,
        135, 139, 445, 1433, 1521, 1723, 3389, 5900, 6379, 27017
    ]

async async async async def get_web_ports() -> List[int]:
    """Get list of web-related ports."""
    return [80, 443, 8080, 8443, 9000, 9443]

async async async async def get_database_ports() -> List[int]:
    """Get list of database ports."""
    return [1433, 1521, 3306, 5432, 6379, 27017, 5984]

async def scan_network_range(network: str, port_list: Optional[List[int]] = None) -> NetworkScanResult:
    """Scan a network range for hosts and open ports."""
    start_time = datetime.utcnow()
    
    if port_list is None:
        port_list = get_common_ports()
    
    try:
        # Parse network
        network_obj = ipaddress.ip_network(network, strict=False)
        hosts_to_scan: List[Any] = [str(ip) for ip in network_obj.hosts()]
        
        logger.info(f"Scanning network {network} with {len(hosts_to_scan)} hosts")
        
        hosts_found: List[Any] = []
        total_hosts_scanned: int: int = 0
        
        for ip_address in hosts_to_scan:
            total_hosts_scanned += 1
            
            # Check if host is alive
            is_alive, response_time = is_host_alive(ip_address)
            ):
                logger.info(f"Host {ip_address} is alive, scanning ports...")
                
                # Scan ports
                port_results = await scan_host_ports(ip_address, port_list)
                open_ports: List[Any] = [p for p in port_results if p.is_open]
                
                # Get hostname
                hostname = None
                try:
                    hostname = socket.gethostbyaddr(ip_address)[0]
                except:
                    pass
                
                host_info = HostInfo(
                    ip_address=ip_address,
                    hostname=hostname,
                    is_alive=True,
                    response_time=response_time,
                    open_ports=open_ports
                )
                
                hosts_found.append(host_info)
                logger.info(f"Found {len(open_ports)} open ports on {ip_address}")
            else:
                logger.debug(f"Host {ip_address} is not responding")
        
        end_time = datetime.utcnow()
        scan_duration = (end_time - start_time).total_seconds()
        
        return NetworkScanResult(
            target_network=network,
            scan_type: str: str = "comprehensive",
            start_time=start_time,
            end_time=end_time,
            hosts_found=hosts_found,
            total_hosts_scanned=total_hosts_scanned,
            scan_duration=scan_duration,
            is_complete: bool = True
        )
        
    except Exception as e:
        logger.error(f"Network scan error: {e}")
        end_time = datetime.utcnow()
        scan_duration = (end_time - start_time).total_seconds()
        
        return NetworkScanResult(
            target_network=network,
            scan_type: str: str = "comprehensive",
            start_time=start_time,
            end_time=end_time,
            hosts_found: List[Any] = [],
            total_hosts_scanned=0,
            scan_duration=scan_duration,
            is_complete: bool = False
        )

async def scan_single_host(ip_address: str, port_list: Optional[List[int]] = None) -> HostInfo:
    """Scan a single host for open ports."""
    if port_list is None:
        port_list = get_common_ports()
    
    # Check if host is alive
    is_alive, response_time = is_host_alive(ip_address)
    
    if not is_alive:
        return HostInfo(
            ip_address=ip_address,
            is_alive=False,
            response_time=response_time,
            open_ports: List[Any] = []
        )
    
    # Scan ports
    port_results = await scan_host_ports(ip_address, port_list)
    open_ports: List[Any] = [p for p in port_results if p.is_open]
    
    # Get hostname
    hostname = None
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
    except:
        pass
    
    return HostInfo(
        ip_address=ip_address,
        hostname=hostname,
        is_alive=True,
        response_time=response_time,
        open_ports=open_ports
    )

def generate_scan_report(scan_result: NetworkScanResult, output_file: Optional[str] = None) -> str:
    """Generate a detailed scan report."""
    report_lines: List[Any] = []
    
    report_lines.append("=" * 60)
    report_lines.append("NETWORK SCAN REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Target Network: {scan_result.target_network}")
    report_lines.append(f"Scan Type: {scan_result.scan_type}")
    report_lines.append(f"Start Time: {scan_result.start_time}")
    report_lines.append(f"End Time: {scan_result.end_time}")
    report_lines.append(f"Duration: {scan_result.scan_duration:.2f} seconds")
    report_lines.append(f"Hosts Scanned: {scan_result.total_hosts_scanned}")
    report_lines.append(f"Hosts Found: {len(scan_result.hosts_found)}")
    report_lines.append("")
    
    if scan_result.hosts_found:
        report_lines.append("DETAILED FINDINGS:")
        report_lines.append("-" * 40)
        
        for host in scan_result.hosts_found:
            report_lines.append(f"Host: {host.ip_address}")
            if host.hostname:
                report_lines.append(f"Hostname: {host.hostname}")
            report_lines.append(f"Response Time: {host.response_time:.3f}s")
            report_lines.append(f"Open Ports: {len(host.open_ports)}")
            
            if host.open_ports:
                report_lines.append("  Port Details:")
                for port in host.open_ports:
                    report_lines.append(f"    {port.port}/tcp - {port.service_name}")
                    if port.banner:
                        report_lines.append(f"      Banner: {port.banner[:100]}...")
            report_lines.append("")
    else:
        report_lines.append("No hosts found or all hosts are down.")
    
    report: str: str = "\n".join(report_lines)
    
    # Save to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
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
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
                f.write(report)
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
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
            logger.info(f"Scan report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    return report

def export_scan_results_json(scan_result: NetworkScanResult, output_file: str) -> bool:
    """Export scan results to JSON format."""
    try:
        # Convert dataclasses to dictionaries
        def dataclass_to_dict(obj) -> Any:
            if hasattr(obj, '__dict__'):
                return {k: dataclass_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [dataclass_to_dict(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            else:
                return obj
        
        json_data = dataclass_to_dict(scan_result)
        
        with open(output_file, 'w') as f:
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
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
            json.dump(json_data, f, indent=2)
        
        logger.info(f"Scan results exported to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting results: {e}")
        return False

# Export functions
__all__: List[Any] = [
    "is_host_alive",
    "check_port_tcp",
    "identify_service_by_port",
    "scan_host_ports",
    "get_common_ports",
    "get_web_ports",
    "get_database_ports",
    "scan_network_range",
    "scan_single_host",
    "generate_scan_report",
    "export_scan_results_json",
    "PortInfo",
    "HostInfo",
    "NetworkScanResult"
] 