"""
Utilities module for Key Messages feature.

Provides various utility functions for data processing, validation, and operations.
"""

# Import existing utilities
from .facebook_utils import *

# Import new network operations
try:
    from .network_ops import (
        # Data models
        PacketType, ScanType, Protocol, PacketConfig, ScanConfig,
        PacketResult, PortScanResult, NetworkScanResult,
        
        # Packet crafting
        craft_tcp_packet, craft_udp_packet, craft_icmp_packet,
        craft_dns_packet, craft_arp_packet,
        
        # Packet operations
        send_packet, sniff_packets,
        
        # Port scanning
        scan_single_port, scan_port_range,
        
        # RORO interfaces
        craft_packet_roro, send_packet_roro, sniff_packets_roro, scan_ports_roro,
        
        # Availability flags
        SCAPY_AVAILABLE, NMAP_AVAILABLE
    )
    NETWORK_OPS_AVAILABLE = True
except ImportError as e:
    NETWORK_OPS_AVAILABLE = False
    print(f"Warning: Network operations not available: {e}")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_target_address(target: str) -> bool:
    """
    Validate if a target address is safe for scanning.
    
    Args:
        target: Target address to validate
        
    Returns:
        True if target is safe, False otherwise
    """
    import re
    import socket
    
    # Check for private/reserved IP ranges
    private_patterns = [
        r'^10\.',           # 10.0.0.0/8
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # 172.16.0.0/12
        r'^192\.168\.',     # 192.168.0.0/16
        r'^127\.',          # 127.0.0.0/8 (loopback)
        r'^169\.254\.',     # 169.254.0.0/16 (link-local)
        r'^224\.',          # 224.0.0.0/4 (multicast)
        r'^240\.',          # 240.0.0.0/4 (reserved)
    ]
    
    for pattern in private_patterns:
        if re.match(pattern, target):
            return False
    
    # Check for localhost
    if target.lower() in ['localhost', '127.0.0.1', '::1']:
        return False
    
    return True

def sanitize_target_address(target: str) -> str:
    """
    Sanitize a target address for safe use.
    
    Args:
        target: Target address to sanitize
        
    Returns:
        Sanitized target address
    """
    import re
    
    # Remove any protocol prefixes
    target = re.sub(r'^https?://', '', target)
    target = re.sub(r'^ftp://', '', target)
    
    # Remove port numbers
    target = re.sub(r':\d+$', '', target)
    
    # Remove path components
    target = target.split('/')[0]
    
    return target.strip()

def is_network_operation_safe(operation: str, target: str) -> bool:
    """
    Check if a network operation is safe to perform.
    
    Args:
        operation: Type of network operation
        target: Target address
        
    Returns:
        True if operation is safe, False otherwise
    """
    # Validate target
    if not validate_target_address(target):
        return False
    
    # Check operation type
    safe_operations = [
        'port_scan', 'packet_sniff', 'ping', 'traceroute',
        'dns_query', 'http_request', 'tcp_connect'
    ]
    
    return operation in safe_operations

def get_network_interface_info() -> dict:
    """
    Get information about available network interfaces.
    
    Returns:
        Dictionary with interface information
    """
    import psutil
    
    interfaces = {}
    
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            interfaces[interface] = {
                'addresses': [],
                'status': 'unknown'
            }
            
            for addr in addrs:
                interfaces[interface]['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
        
        # Get interface status
        for interface, stats in psutil.net_if_stats().items():
            if interface in interfaces:
                interfaces[interface]['status'] = 'up' if stats.isup else 'down'
                interfaces[interface]['speed'] = stats.speed
                interfaces[interface]['mtu'] = stats.mtu
                
    except Exception as e:
        print(f"Error getting network interface info: {e}")
    
    return interfaces

def format_network_scan_results(results: dict) -> str:
    """
    Format network scan results for display.
    
    Args:
        results: Network scan results dictionary
        
    Returns:
        Formatted string representation
    """
    if not results.get('success', False):
        return f"Scan failed: {results.get('errors', ['Unknown error'])}"
    
    output = []
    output.append(f"Network Scan Results for {results.get('target', 'Unknown')}")
    output.append("=" * 50)
    
    # Summary
    output.append(f"Scan Type: {results.get('scan_type', 'Unknown')}")
    output.append(f"Total Ports: {results.get('total_ports', 0)}")
    output.append(f"Open Ports: {results.get('open_ports', 0)}")
    output.append(f"Closed Ports: {results.get('closed_ports', 0)}")
    output.append(f"Filtered Ports: {results.get('filtered_ports', 0)}")
    output.append(f"Scan Duration: {results.get('scan_duration', 0):.2f} seconds")
    output.append("")
    
    # Detailed results
    results_list = results.get('results', [])
    if results_list:
        output.append("Port Details:")
        output.append("-" * 30)
        
        for result in results_list:
            state_icon = "🟢" if result.get('state') == 'open' else "🔴"
            output.append(f"{state_icon} Port {result.get('port', 'Unknown')}: {result.get('state', 'Unknown')}")
            
            service = result.get('service')
            if service:
                output.append(f"   Service: {service}")
            
            version = result.get('version')
            if version:
                output.append(f"   Version: {version}")
            
            banner = result.get('banner')
            if banner:
                output.append(f"   Banner: {banner}")
    
    return "\n".join(output)

def create_network_scan_report(results: dict, format: str = 'text') -> str:
    """
    Create a formatted network scan report.
    
    Args:
        results: Network scan results
        format: Output format ('text', 'json', 'html')
        
    Returns:
        Formatted report
    """
    if format == 'json':
        import json
        return json.dumps(results, indent=2)
    
    elif format == 'html':
        html = []
        html.append("<html><head><title>Network Scan Report</title></head><body>")
        html.append(f"<h1>Network Scan Report</h1>")
        html.append(f"<h2>Target: {results.get('target', 'Unknown')}</h2>")
        
        # Summary table
        html.append("<table border='1'>")
        html.append("<tr><th>Metric</th><th>Value</th></tr>")
        html.append(f"<tr><td>Scan Type</td><td>{results.get('scan_type', 'Unknown')}</td></tr>")
        html.append(f"<tr><td>Total Ports</td><td>{results.get('total_ports', 0)}</td></tr>")
        html.append(f"<tr><td>Open Ports</td><td>{results.get('open_ports', 0)}</td></tr>")
        html.append(f"<tr><td>Closed Ports</td><td>{results.get('closed_ports', 0)}</td></tr>")
        html.append(f"<tr><td>Filtered Ports</td><td>{results.get('filtered_ports', 0)}</td></tr>")
        html.append(f"<tr><td>Scan Duration</td><td>{results.get('scan_duration', 0):.2f} seconds</td></tr>")
        html.append("</table>")
        
        # Results table
        results_list = results.get('results', [])
        if results_list:
            html.append("<h3>Port Details</h3>")
            html.append("<table border='1'>")
            html.append("<tr><th>Port</th><th>State</th><th>Service</th><th>Version</th><th>Banner</th></tr>")
            
            for result in results_list:
                state_color = "green" if result.get('state') == 'open' else "red"
                html.append(f"<tr>")
                html.append(f"<td>{result.get('port', 'Unknown')}</td>")
                html.append(f"<td style='color: {state_color}'>{result.get('state', 'Unknown')}</td>")
                html.append(f"<td>{result.get('service', '')}</td>")
                html.append(f"<td>{result.get('version', '')}</td>")
                html.append(f"<td>{result.get('banner', '')}</td>")
                html.append("</tr>")
            
            html.append("</table>")
        
        html.append("</body></html>")
        return "\n".join(html)
    
    else:  # text format
        return format_network_scan_results(results)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Network operations
    "NETWORK_OPS_AVAILABLE",
    
    # Utility functions
    "validate_target_address",
    "sanitize_target_address", 
    "is_network_operation_safe",
    "get_network_interface_info",
    "format_network_scan_results",
    "create_network_scan_report",
    
    # Import network operations if available
    *([] if not NETWORK_OPS_AVAILABLE else [
        "PacketType", "ScanType", "Protocol", "PacketConfig", "ScanConfig",
        "PacketResult", "PortScanResult", "NetworkScanResult",
        "craft_tcp_packet", "craft_udp_packet", "craft_icmp_packet",
        "craft_dns_packet", "craft_arp_packet",
        "send_packet", "sniff_packets",
        "scan_single_port", "scan_port_range",
        "craft_packet_roro", "send_packet_roro", "sniff_packets_roro", "scan_ports_roro",
        "SCAPY_AVAILABLE", "NMAP_AVAILABLE"
    ])
] 