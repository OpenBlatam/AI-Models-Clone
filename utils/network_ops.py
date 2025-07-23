"""
Network Operations Module for Key Messages Feature.

Provides packet crafting, sniffing, and port scanning capabilities using Scapy and python-nmap.
Implements functional programming patterns with RORO interfaces.
"""

import asyncio
import json
import logging
import socket
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum

import structlog
from pydantic import BaseModel, Field, validator

try:
    from scapy.all import (
        ARP, DNS, DNSQR, DNSRR, Ether, ICMP, IP, TCP, UDP, 
        Raw, sr, sr1, srp, sniff, send, srp1, conf
    )
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("Scapy not available. Network operations limited.")

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False
    logging.warning("python-nmap not available. Port scanning limited.")

# Configure structured logging
logger = structlog.get_logger(__name__)

# =============================================================================
# DATA MODELS
# =============================================================================

class PacketType(str, Enum):
    """Packet types for crafting."""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    DNS = "dns"
    ARP = "arp"
    CUSTOM = "custom"

class ScanType(str, Enum):
    """Port scan types."""
    TCP_SYN = "tcp_syn"
    TCP_CONNECT = "tcp_connect"
    UDP = "udp"
    STEALTH = "stealth"
    AGGRESSIVE = "aggressive"

class Protocol(str, Enum):
    """Network protocols."""
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"
    FTP = "ftp"
    SMTP = "smtp"
    DNS = "dns"

@dataclass
class PacketConfig:
    """Configuration for packet crafting."""
    source_ip: str = "192.168.1.100"
    destination_ip: str = "192.168.1.1"
    source_port: int = 12345
    destination_port: int = 80
    protocol: Protocol = Protocol.TCP
    payload: str = ""
    ttl: int = 64
    flags: str = "S"  # SYN flag for TCP
    timeout: int = 3

@dataclass
class ScanConfig:
    """Configuration for port scanning."""
    target_host: str = "localhost"
    port_range: str = "1-1000"
    scan_type: ScanType = ScanType.TCP_SYN
    timeout: int = 5
    verbose: bool = False
    max_retries: int = 3

class PacketResult(BaseModel):
    """Result of packet operation."""
    success: bool = Field(description="Operation success status")
    packet_type: PacketType = Field(description="Type of packet")
    source: str = Field(description="Source address")
    destination: str = Field(description="Destination address")
    protocol: Protocol = Field(description="Network protocol")
    payload_size: int = Field(description="Payload size in bytes")
    response_time: Optional[float] = Field(default=None, description="Response time in seconds")
    response_data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")

class PortScanResult(BaseModel):
    """Result of port scan."""
    host: str = Field(description="Target host")
    port: int = Field(description="Port number")
    state: str = Field(description="Port state (open/closed/filtered)")
    service: Optional[str] = Field(default=None, description="Detected service")
    version: Optional[str] = Field(default=None, description="Service version")
    banner: Optional[str] = Field(default=None, description="Service banner")
    scan_time: float = Field(description="Scan duration in seconds")

class NetworkScanResult(BaseModel):
    """Result of network scan."""
    target: str = Field(description="Target network/host")
    scan_type: ScanType = Field(description="Type of scan performed")
    total_ports: int = Field(description="Total ports scanned")
    open_ports: int = Field(description="Number of open ports")
    closed_ports: int = Field(description="Number of closed ports")
    filtered_ports: int = Field(description="Number of filtered ports")
    scan_duration: float = Field(description="Total scan duration")
    results: List[PortScanResult] = Field(description="Individual port results")
    errors: List[str] = Field(description="Any errors encountered")

# =============================================================================
# PACKET CRAFTING FUNCTIONS
# =============================================================================

def craft_tcp_packet(config: PacketConfig) -> Optional[Any]:
    """
    Craft a TCP packet using Scapy.
    
    Args:
        config: Packet configuration
        
    Returns:
        Crafted TCP packet or None if failed
    """
    if not SCAPY_AVAILABLE:
        logger.error("Scapy not available for TCP packet crafting")
        return None
    
    try:
        # Create IP layer
        ip_layer = IP(
            src=config.source_ip,
            dst=config.destination_ip,
            ttl=config.ttl
        )
        
        # Create TCP layer
        tcp_layer = TCP(
            sport=config.source_port,
            dport=config.destination_port,
            flags=config.flags
        )
        
        # Create payload if provided
        payload_layer = Raw(load=config.payload) if config.payload else None
        
        # Combine layers
        if payload_layer:
            packet = ip_layer / tcp_layer / payload_layer
        else:
            packet = ip_layer / tcp_layer
            
        logger.info("TCP packet crafted successfully", 
                   source=config.source_ip, 
                   destination=config.destination_ip,
                   source_port=config.source_port,
                   destination_port=config.destination_port)
        
        return packet
        
    except Exception as e:
        logger.error("Failed to craft TCP packet", error=str(e))
        return None

def craft_udp_packet(config: PacketConfig) -> Optional[Any]:
    """
    Craft a UDP packet using Scapy.
    
    Args:
        config: Packet configuration
        
    Returns:
        Crafted UDP packet or None if failed
    """
    if not SCAPY_AVAILABLE:
        logger.error("Scapy not available for UDP packet crafting")
        return None
    
    try:
        # Create IP layer
        ip_layer = IP(
            src=config.source_ip,
            dst=config.destination_ip,
            ttl=config.ttl
        )
        
        # Create UDP layer
        udp_layer = UDP(
            sport=config.source_port,
            dport=config.destination_port
        )
        
        # Create payload if provided
        payload_layer = Raw(load=config.payload) if config.payload else None
        
        # Combine layers
        if payload_layer:
            packet = ip_layer / udp_layer / payload_layer
        else:
            packet = ip_layer / udp_layer
            
        logger.info("UDP packet crafted successfully", 
                   source=config.source_ip, 
                   destination=config.destination_ip)
        
        return packet
        
    except Exception as e:
        logger.error("Failed to craft UDP packet", error=str(e))
        return None

def craft_icmp_packet(config: PacketConfig) -> Optional[Any]:
    """
    Craft an ICMP packet using Scapy.
    
    Args:
        config: Packet configuration
        
    Returns:
        Crafted ICMP packet or None if failed
    """
    if not SCAPY_AVAILABLE:
        logger.error("Scapy not available for ICMP packet crafting")
        return None
    
    try:
        # Create IP layer
        ip_layer = IP(
            src=config.source_ip,
            dst=config.destination_ip,
            ttl=config.ttl
        )
        
        # Create ICMP layer (ping)
        icmp_layer = ICMP()
        
        # Create payload if provided
        payload_layer = Raw(load=config.payload) if config.payload else None
        
        # Combine layers
        if payload_layer:
            packet = ip_layer / icmp_layer / payload_layer
        else:
            packet = ip_layer / icmp_layer
            
        logger.info("ICMP packet crafted successfully", 
                   source=config.source_ip, 
                   destination=config.destination_ip)
        
        return packet
        
    except Exception as e:
        logger.error("Failed to craft ICMP packet", error=str(e))
        return None

def craft_dns_packet(config: PacketConfig) -> Optional[Any]:
    """
    Craft a DNS query packet using Scapy.
    
    Args:
        config: Packet configuration
        
    Returns:
        Crafted DNS packet or None if failed
    """
    if not SCAPY_AVAILABLE:
        logger.error("Scapy not available for DNS packet crafting")
        return None
    
    try:
        # Create IP layer
        ip_layer = IP(
            src=config.source_ip,
            dst=config.destination_ip,
            ttl=config.ttl
        )
        
        # Create UDP layer for DNS
        udp_layer = UDP(
            sport=config.source_port,
            dport=53  # DNS port
        )
        
        # Create DNS query
        dns_query = DNSQR(qname=config.payload if config.payload else "example.com")
        dns_layer = DNS(qd=dns_query)
        
        # Combine layers
        packet = ip_layer / udp_layer / dns_layer
        
        logger.info("DNS packet crafted successfully", 
                   source=config.source_ip, 
                   destination=config.destination_ip,
                   query=config.payload or "example.com")
        
        return packet
        
    except Exception as e:
        logger.error("Failed to craft DNS packet", error=str(e))
        return None

def craft_arp_packet(config: PacketConfig) -> Optional[Any]:
    """
    Craft an ARP packet using Scapy.
    
    Args:
        config: Packet configuration
        
    Returns:
        Crafted ARP packet or None if failed
    """
    if not SCAPY_AVAILABLE:
        logger.error("Scapy not available for ARP packet crafting")
        return None
    
    try:
        # Create Ethernet layer
        ether_layer = Ether(dst="ff:ff:ff:ff:ff:ff")
        
        # Create ARP layer
        arp_layer = ARP(
            op=1,  # who-has
            psrc=config.source_ip,
            pdst=config.destination_ip
        )
        
        # Combine layers
        packet = ether_layer / arp_layer
        
        logger.info("ARP packet crafted successfully", 
                   source=config.source_ip, 
                   destination=config.destination_ip)
        
        return packet
        
    except Exception as e:
        logger.error("Failed to craft ARP packet", error=str(e))
        return None

# =============================================================================
# PACKET SENDING FUNCTIONS
# =============================================================================

def send_packet(packet: Any, timeout: int = 3) -> PacketResult:
    """
    Send a crafted packet and capture response.
    
    Args:
        packet: Crafted packet to send
        timeout: Timeout in seconds
        
    Returns:
        PacketResult with operation details
    """
    if not SCAPY_AVAILABLE:
        return PacketResult(
            success=False,
            packet_type=PacketType.CUSTOM,
            source="",
            destination="",
            protocol=Protocol.TCP,
            payload_size=0,
            error_message="Scapy not available"
        )
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Send packet and wait for response
        response = sr1(packet, timeout=timeout, verbose=False)
        
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time
        
        # Extract packet information
        source = packet[IP].src if IP in packet else ""
        destination = packet[IP].dst if IP in packet else ""
        protocol = Protocol.TCP if TCP in packet else Protocol.UDP if UDP in packet else Protocol.ICMP
        payload_size = len(packet[Raw].load) if Raw in packet else 0
        
        # Process response
        response_data = None
        if response:
            response_data = {
                "source": response[IP].src if IP in response else "",
                "destination": response[IP].dst if IP in response else "",
                "protocol": "tcp" if TCP in response else "udp" if UDP in response else "icmp",
                "payload_size": len(response[Raw].load) if Raw in response else 0
            }
        
        logger.info("Packet sent successfully", 
                   source=source, 
                   destination=destination,
                   response_time=response_time,
                   has_response=response is not None)
        
        return PacketResult(
            success=True,
            packet_type=PacketType.CUSTOM,
            source=source,
            destination=destination,
            protocol=protocol,
            payload_size=payload_size,
            response_time=response_time,
            response_data=response_data
        )
        
    except Exception as e:
        logger.error("Failed to send packet", error=str(e))
        return PacketResult(
            success=False,
            packet_type=PacketType.CUSTOM,
            source="",
            destination="",
            protocol=Protocol.TCP,
            payload_size=0,
            error_message=str(e)
        )

# =============================================================================
# PACKET SNIFFING FUNCTIONS
# =============================================================================

def sniff_packets(interface: str = None, count: int = 10, timeout: int = 30, 
                  filter: str = None) -> List[Dict[str, Any]]:
    """
    Sniff network packets using Scapy.
    
    Args:
        interface: Network interface to sniff
        count: Number of packets to capture
        timeout: Sniffing timeout in seconds
        filter: BPF filter string
        
    Returns:
        List of captured packet information
    """
    if not SCAPY_AVAILABLE:
        logger.error("Scapy not available for packet sniffing")
        return []
    
    try:
        logger.info("Starting packet sniffing", 
                   interface=interface, 
                   count=count, 
                   timeout=timeout,
                   filter=filter)
        
        # Sniff packets
        packets = sniff(
            iface=interface,
            count=count,
            timeout=timeout,
            filter=filter,
            store=1
        )
        
        # Process captured packets
        packet_info = []
        for packet in packets:
            info = {
                "timestamp": packet.time,
                "length": len(packet),
                "protocol": "unknown"
            }
            
            # Extract protocol information
            if IP in packet:
                info["source_ip"] = packet[IP].src
                info["destination_ip"] = packet[IP].dst
                info["protocol"] = packet[IP].proto
                
                if TCP in packet:
                    info["source_port"] = packet[TCP].sport
                    info["destination_port"] = packet[TCP].dport
                    info["flags"] = packet[TCP].flags
                elif UDP in packet:
                    info["source_port"] = packet[UDP].sport
                    info["destination_port"] = packet[UDP].dport
                elif ICMP in packet:
                    info["icmp_type"] = packet[ICMP].type
                    info["icmp_code"] = packet[ICMP].code
            
            packet_info.append(info)
        
        logger.info("Packet sniffing completed", 
                   packets_captured=len(packets),
                   packets_processed=len(packet_info))
        
        return packet_info
        
    except Exception as e:
        logger.error("Failed to sniff packets", error=str(e))
        return []

# =============================================================================
# PORT SCANNING FUNCTIONS
# =============================================================================

def scan_single_port(host: str, port: int, protocol: str = "tcp", 
                    timeout: int = 5) -> PortScanResult:
    """
    Scan a single port using python-nmap.
    
    Args:
        host: Target host
        port: Port to scan
        protocol: Protocol (tcp/udp)
        timeout: Scan timeout
        
    Returns:
        PortScanResult with scan details
    """
    if not NMAP_AVAILABLE:
        logger.error("python-nmap not available for port scanning")
        return PortScanResult(
            host=host,
            port=port,
            state="unknown",
            scan_time=0.0
        )
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Create nmap scanner
        nm = nmap.PortScanner()
        
        # Perform scan
        scan_args = f"-sS -p {port} --host-timeout {timeout}s"
        nm.scan(host, arguments=scan_args)
        
        end_time = asyncio.get_event_loop().time()
        scan_time = end_time - start_time
        
        # Extract results
        if host in nm.all_hosts():
            host_data = nm[host]
            if protocol in host_data:
                port_data = host_data[protocol].get(port, {})
                
                state = port_data.get("state", "unknown")
                service = port_data.get("name", None)
                version = port_data.get("version", None)
                banner = port_data.get("product", None)
                
                logger.info("Port scan completed", 
                           host=host, 
                           port=port, 
                           state=state,
                           service=service)
                
                return PortScanResult(
                    host=host,
                    port=port,
                    state=state,
                    service=service,
                    version=version,
                    banner=banner,
                    scan_time=scan_time
                )
        
        logger.warning("Port scan failed to find host", host=host)
        return PortScanResult(
            host=host,
            port=port,
            state="unknown",
            scan_time=scan_time
        )
        
    except Exception as e:
        logger.error("Failed to scan port", host=host, port=port, error=str(e))
        return PortScanResult(
            host=host,
            port=port,
            state="error",
            scan_time=0.0
        )

def scan_port_range(host: str, port_range: str, scan_type: ScanType = ScanType.TCP_SYN,
                   timeout: int = 5) -> NetworkScanResult:
    """
    Scan a range of ports using python-nmap.
    
    Args:
        host: Target host
        port_range: Port range (e.g., "1-1000")
        scan_type: Type of scan to perform
        timeout: Scan timeout per port
        
    Returns:
        NetworkScanResult with scan details
    """
    if not NMAP_AVAILABLE:
        logger.error("python-nmap not available for port range scanning")
        return NetworkScanResult(
            target=host,
            scan_type=scan_type,
            total_ports=0,
            open_ports=0,
            closed_ports=0,
            filtered_ports=0,
            scan_duration=0.0,
            results=[],
            errors=["python-nmap not available"]
        )
    
    try:
        start_time = asyncio.get_event_loop().time()
        
        # Create nmap scanner
        nm = nmap.PortScanner()
        
        # Determine scan arguments based on type
        if scan_type == ScanType.TCP_SYN:
            scan_args = f"-sS -p {port_range} --host-timeout {timeout}s"
        elif scan_type == ScanType.TCP_CONNECT:
            scan_args = f"-sT -p {port_range} --host-timeout {timeout}s"
        elif scan_type == ScanType.UDP:
            scan_args = f"-sU -p {port_range} --host-timeout {timeout}s"
        elif scan_type == ScanType.STEALTH:
            scan_args = f"-sS -p {port_range} --host-timeout {timeout}s --max-retries 1"
        elif scan_type == ScanType.AGGRESSIVE:
            scan_args = f"-sS -p {port_range} --host-timeout {timeout}s --max-retries 3 -T4"
        else:
            scan_args = f"-sS -p {port_range} --host-timeout {timeout}s"
        
        logger.info("Starting port range scan", 
                   host=host, 
                   port_range=port_range, 
                   scan_type=scan_type.value,
                   scan_args=scan_args)
        
        # Perform scan
        nm.scan(host, arguments=scan_args)
        
        end_time = asyncio.get_event_loop().time()
        scan_duration = end_time - start_time
        
        # Process results
        results = []
        open_ports = 0
        closed_ports = 0
        filtered_ports = 0
        
        if host in nm.all_hosts():
            host_data = nm[host]
            
            for protocol in ["tcp", "udp"]:
                if protocol in host_data:
                    for port, port_data in host_data[protocol].items():
                        state = port_data.get("state", "unknown")
                        service = port_data.get("name", None)
                        version = port_data.get("version", None)
                        banner = port_data.get("product", None)
                        
                        result = PortScanResult(
                            host=host,
                            port=port,
                            state=state,
                            service=service,
                            version=version,
                            banner=banner,
                            scan_time=scan_duration
                        )
                        
                        results.append(result)
                        
                        # Count states
                        if state == "open":
                            open_ports += 1
                        elif state == "closed":
                            closed_ports += 1
                        elif state == "filtered":
                            filtered_ports += 1
        
        total_ports = len(results)
        
        logger.info("Port range scan completed", 
                   host=host, 
                   total_ports=total_ports,
                   open_ports=open_ports,
                   closed_ports=closed_ports,
                   filtered_ports=filtered_ports,
                   scan_duration=scan_duration)
        
        return NetworkScanResult(
            target=host,
            scan_type=scan_type,
            total_ports=total_ports,
            open_ports=open_ports,
            closed_ports=closed_ports,
            filtered_ports=filtered_ports,
            scan_duration=scan_duration,
            results=results,
            errors=[]
        )
        
    except Exception as e:
        logger.error("Failed to scan port range", host=host, error=str(e))
        return NetworkScanResult(
            target=host,
            scan_type=scan_type,
            total_ports=0,
            open_ports=0,
            closed_ports=0,
            filtered_ports=0,
            scan_duration=0.0,
            results=[],
            errors=[str(e)]
        )

# =============================================================================
# RORO INTERFACE FUNCTIONS
# =============================================================================

def craft_packet_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    RORO interface for packet crafting.
    
    Args:
        params: Dictionary containing:
            - packet_type: Type of packet to craft
            - config: PacketConfig or dict with packet configuration
            
    Returns:
        Dictionary with crafted packet and metadata
    """
    packet_type = params.get("packet_type", PacketType.TCP)
    config_data = params.get("config", {})
    
    # Convert dict to PacketConfig if needed
    if isinstance(config_data, dict):
        config = PacketConfig(**config_data)
    else:
        config = config_data
    
    # Craft packet based on type
    packet = None
    if packet_type == PacketType.TCP:
        packet = craft_tcp_packet(config)
    elif packet_type == PacketType.UDP:
        packet = craft_udp_packet(config)
    elif packet_type == PacketType.ICMP:
        packet = craft_icmp_packet(config)
    elif packet_type == PacketType.DNS:
        packet = craft_dns_packet(config)
    elif packet_type == PacketType.ARP:
        packet = craft_arp_packet(config)
    
    return {
        "success": packet is not None,
        "packet_type": packet_type,
        "packet": packet,
        "config": config_data
    }

def send_packet_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    RORO interface for packet sending.
    
    Args:
        params: Dictionary containing:
            - packet: Crafted packet to send
            - timeout: Timeout in seconds
            
    Returns:
        Dictionary with send results
    """
    packet = params.get("packet")
    timeout = params.get("timeout", 3)
    
    result = send_packet(packet, timeout)
    
    return {
        "success": result.success,
        "packet_type": result.packet_type.value,
        "source": result.source,
        "destination": result.destination,
        "protocol": result.protocol.value,
        "payload_size": result.payload_size,
        "response_time": result.response_time,
        "response_data": result.response_data,
        "error_message": result.error_message
    }

def sniff_packets_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    RORO interface for packet sniffing.
    
    Args:
        params: Dictionary containing:
            - interface: Network interface
            - count: Number of packets to capture
            - timeout: Sniffing timeout
            - filter: BPF filter string
            
    Returns:
        Dictionary with sniffed packets
    """
    interface = params.get("interface")
    count = params.get("count", 10)
    timeout = params.get("timeout", 30)
    filter_str = params.get("filter")
    
    packets = sniff_packets(interface, count, timeout, filter_str)
    
    return {
        "success": True,
        "packets_captured": len(packets),
        "packets": packets,
        "interface": interface,
        "count": count,
        "timeout": timeout,
        "filter": filter_str
    }

def scan_ports_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    RORO interface for port scanning.
    
    Args:
        params: Dictionary containing:
            - host: Target host
            - port_range: Port range or single port
            - scan_type: Type of scan
            - timeout: Scan timeout
            
    Returns:
        Dictionary with scan results
    """
    host = params.get("host", "localhost")
    port_range = params.get("port_range", "1-1000")
    scan_type = ScanType(params.get("scan_type", ScanType.TCP_SYN))
    timeout = params.get("timeout", 5)
    
    # Determine if single port or range
    if "-" in str(port_range) or "," in str(port_range):
        result = scan_port_range(host, str(port_range), scan_type, timeout)
        return {
            "success": len(result.errors) == 0,
            "target": result.target,
            "scan_type": result.scan_type.value,
            "total_ports": result.total_ports,
            "open_ports": result.open_ports,
            "closed_ports": result.closed_ports,
            "filtered_ports": result.filtered_ports,
            "scan_duration": result.scan_duration,
            "results": [r.dict() for r in result.results],
            "errors": result.errors
        }
    else:
        port = int(port_range)
        result = scan_single_port(host, port, "tcp", timeout)
        return {
            "success": result.state != "error",
            "host": result.host,
            "port": result.port,
            "state": result.state,
            "service": result.service,
            "version": result.version,
            "banner": result.banner,
            "scan_time": result.scan_time
        }

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data models
    "PacketType", "ScanType", "Protocol", "PacketConfig", "ScanConfig",
    "PacketResult", "PortScanResult", "NetworkScanResult",
    
    # Packet crafting
    "craft_tcp_packet", "craft_udp_packet", "craft_icmp_packet",
    "craft_dns_packet", "craft_arp_packet",
    
    # Packet operations
    "send_packet", "sniff_packets",
    
    # Port scanning
    "scan_single_port", "scan_port_range",
    
    # RORO interfaces
    "craft_packet_roro", "send_packet_roro", "sniff_packets_roro", "scan_ports_roro",
    
    # Availability flags
    "SCAPY_AVAILABLE", "NMAP_AVAILABLE"
] 