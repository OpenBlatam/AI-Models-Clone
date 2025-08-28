from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .port_scanner import (
from .vulnerability_scanner import (
from .web_scanner import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Security Scanners Module

Provides comprehensive security scanning capabilities including port, vulnerability, and web scanners.
"""

    PortScanRequest,
    PortScanResult,
    PortRangeScanRequest,
    PortRangeScanResult,
    scan_port,
    scan_port_async,
    scan_port_range_async,
    get_service_name
)

    VulnerabilityScanRequest,
    VulnerabilityScanResult,
    VulnerabilityType,
    scan_vulnerabilities_async,
    scan_sql_injection,
    scan_xss_vulnerabilities,
    scan_csrf_vulnerabilities,
    scan_file_inclusion_vulnerabilities
)

    WebScanRequest,
    WebScanResult,
    WebVulnerabilityType,
    scan_web_application_async,
    scan_web_directory_enumeration,
    scan_web_robots_txt,
    scan_web_sitemap,
    scan_web_headers,
    scan_web_ssl_certificate
)

__all__ = [
    # Port Scanner
    "PortScanRequest",
    "PortScanResult", 
    "PortRangeScanRequest",
    "PortRangeScanResult",
    "scan_port",
    "scan_port_async",
    "scan_port_range_async",
    "get_service_name",
    
    # Vulnerability Scanner
    "VulnerabilityScanRequest",
    "VulnerabilityScanResult",
    "VulnerabilityType",
    "scan_vulnerabilities_async",
    "scan_sql_injection",
    "scan_xss_vulnerabilities",
    "scan_csrf_vulnerabilities",
    "scan_file_inclusion_vulnerabilities",
    
    # Web Scanner
    "WebScanRequest",
    "WebScanResult",
    "WebVulnerabilityType",
    "scan_web_application_async",
    "scan_web_directory_enumeration",
    "scan_web_robots_txt",
    "scan_web_sitemap",
    "scan_web_headers",
    "scan_web_ssl_certificate"
] 