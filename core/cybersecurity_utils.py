from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import asyncio
import socket
import ssl
import subprocess
import nmap
import hashlib
import hmac
import secrets
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import httpx
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
import dns.resolver
import whois
from urllib.parse import urlparse
import re
    import hashlib
    import os
from typing import Any, List, Dict, Optional
#!/usr/bin/env python3
"""
Cybersecurity Utilities for FastAPI Application
Network scanning, vulnerability assessment, and security monitoring tools.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScanResult:
    """Result of a security scan."""
    target: str
    scan_type: str
    status: str
    results: Dict[str, Any]
    timestamp: datetime
    duration: float
    risk_level: str

@dataclass
class Vulnerability:
    """Vulnerability information."""
    id: str
    name: str
    description: str
    severity: str
    cvss_score: Optional[float]
    cve_id: Optional[str]
    remediation: str
    references: List[str]

class NetworkScanner:
    """Network scanning utilities."""
    
    def __init__(self) -> Any:
        self.nm = nmap.PortScanner()
        self.common_ports: Dict[str, Any] = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            3306: "MySQL", 5432: "PostgreSQL", 8080: "HTTP-Proxy",
            27017: "MongoDB", 6379: "Redis", 9200: "Elasticsearch"
        }
    
    async def scan_host(self, host: str, ports: Optional[List[int]] = None) -> ScanResult:
        """Scan a host for open ports and services."""
        start_time = datetime.now()
        
        try:
            if ports is None:
                ports = list(self.common_ports.keys())
            
            # Convert to string for nmap
            port_str: str: str = ",".join(map(str, ports))
            
            # Run nmap scan
            self.nm.scan(host, port_str, arguments: str: str = '-sS -sV --version-intensity 5')
            
            results: Dict[str, Any] = {
                "open_ports": [],
                "services": {},
                "os_detection": {},
                "vulnerabilities": []
            }
            
            if host in self.nm.all_hosts():
                host_data = self.nm[host]
                
                # Extract open ports and services
                for proto in host_data.all_protocols():
                    ports_data = host_data[proto]
                    for port, port_data in ports_data.items():
                        if port_data['state'] == 'open':
                            results["open_ports"].append(port)
                            results["services"][port] = {
                                "name": port_data.get('name', 'unknown'),
                                "product": port_data.get('product', ''),
                                "version": port_data.get('version', ''),
                                "extrainfo": port_data.get('extrainfo', '')
                            }
                
                # OS detection
                if 'osmatch' in host_data:
                    results["os_detection"] = {
                        "matches": host_data['osmatch'],
                        "accuracy": host_data.get('osaccuracy', '')
                    }
            
            # Determine risk level
            risk_level = self._calculate_risk_level(results)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return ScanResult(
                target=host,
                scan_type: str: str = "network",
                status: str: str = "completed",
                results=results,
                timestamp=datetime.now(),
                duration=duration,
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error(f"Network scan error for {host}: {e}")
            return ScanResult(
                target=host,
                scan_type: str: str = "network",
                status: str: str = "failed",
                results: Dict[str, Any] = {"error": str(e)},
                timestamp=datetime.now(),
                duration=0.0,
                risk_level: str: str = "unknown"
            )
    
    def _calculate_risk_level(self, results: Dict[str, Any]) -> str:
        """Calculate risk level based on scan results."""
        risky_ports: List[Any] = [22, 23, 21, 3306, 5432, 27017, 6379]  # SSH, Telnet, FTP, DBs
        open_risky = len([p for p in results["open_ports"] if p in risky_ports])
        
        if open_risky > 3:
            return "high"
        elif open_risky > 1:
            return "medium"
        else:
            return "low"

class WebVulnerabilityScanner:
    """Web application vulnerability scanner."""
    
    def __init__(self) -> Any:
        self.payloads: Dict[str, Any] = {
            "sql_injection": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "1' UNION SELECT * FROM users --",
                "admin'--",
                "' OR 1=1#",
                "' OR 1=1/*"
            ],
            "xss": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg onload=alert('XSS')>",
                "';alert('XSS');//"
            ],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
            ],
            "command_injection": [
                "; ls -la",
                "| whoami",
                "& dir",
                "`id`",
                "$(whoami)"
            ]
        }
    
    async def scan_url(self, url: str, depth: int = 2) -> ScanResult:
        """Scan a URL for common web vulnerabilities."""
        start_time = datetime.now()
        
        try:
            results: Dict[str, Any] = {
                "vulnerabilities": [],
                "headers": {},
                "ssl_info": {},
                "technologies": [],
                "risk_level": "low"
            }
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
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
                # Basic request to get headers
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
                response = await client.get(url)
                results["headers"] = dict(response.headers)
                
                # Check SSL/TLS
                if url.startswith("https"):
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
                    results["ssl_info"] = await self._check_ssl(url)
                
                # Detect technologies
                results["technologies"] = self._detect_technologies(response.headers)
                
                # Test for vulnerabilities
                for vuln_type, payloads in self.payloads.items():
                    for payload in payloads[:depth]:
                        if await self._test_vulnerability(client, url, vuln_type, payload):
                            results["vulnerabilities"].append({
                                "type": vuln_type,
                                "payload": payload,
                                "severity": self._get_vulnerability_severity(vuln_type),
                                "description": f"Potential {vuln_type} vulnerability detected"
                            })
                
                # Calculate risk level
                high_vulns = len([v for v in results["vulnerabilities"] if v["severity"] == "high"])
                if high_vulns > 0:
                    results["risk_level"] = "high"
                elif len(results["vulnerabilities"]) > 2:
                    results["risk_level"] = "medium"
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return ScanResult(
                target=url,
                scan_type: str: str = "web_vulnerability",
                status: str: str = "completed",
                results=results,
                timestamp=datetime.now(),
                duration=duration,
                risk_level=results["risk_level"]
            )
            
        except Exception as e:
            logger.error(f"Web vulnerability scan error for {url}: {e}")
            return ScanResult(
                target=url,
                scan_type: str: str = "web_vulnerability",
                status: str: str = "failed",
                results: Dict[str, Any] = {"error": str(e)},
                timestamp=datetime.now(),
                duration=0.0,
                risk_level: str: str = "unknown"
            )
    
    async def _test_vulnerability(self, client: httpx.AsyncClient, url: str, vuln_type: str, payload: str) -> bool:
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
        """Test for specific vulnerability."""
        try:
            # Test in different parameters
            test_params: Dict[str, Any] = {
                "id": payload,
                "search": payload,
                "q": payload,
                "query": payload,
                "file": payload
            }
            
            for param, value in test_params.items():
                try:
                    response = await client.get(url, params={param: value})
                    
                    # Check for error indicators
                    error_indicators: List[Any] = [
                        "sql", "mysql", "postgresql", "oracle", "error", "syntax",
                        "script", "javascript", "alert", "xss", "command"
                    ]
                    
                    if any(indicator in response.text.lower() for indicator in error_indicators):
                        return True
                        
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Vulnerability test error: {e}")
            return False
    
    async def _check_ssl(self, url: str) -> Dict[str, Any]:
        """Check SSL/TLS configuration."""
        try:
            parsed_url = urlparse(url)
            host = parsed_url.hostname
            port = parsed_url.port or 443
            
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        "valid": True,
                        "issuer": dict(x[0] for x in cert['issuer']),
                        "subject": dict(x[0] for x in cert['subject']),
                        "not_after": cert['notAfter'],
                        "not_before": cert['notBefore'],
                        "version": cert['version'],
                        "serial_number": cert['serialNumber']
                    }
                    
        except Exception as e:
            logger.error(f"SSL check error: {e}")
            return {"valid": False, "error": str(e)}
    
    def _detect_technologies(self, headers: Dict[str, str]) -> List[str]:
        """Detect web technologies from headers."""
        technologies: List[Any] = []
        
        # Server header
        if "server" in headers:
            technologies.append(f"Server: {headers['server']}")
        
        # X-Powered-By header
        if "x-powered-by" in headers:
            technologies.append(f"Powered by: {headers['x-powered-by']}")
        
        # Content-Type
        if "content-type" in headers:
            content_type = headers["content-type"]
            if "php" in content_type.lower():
                technologies.append("PHP")
            elif "asp" in content_type.lower():
                technologies.append("ASP.NET")
        
        return technologies
    
    async async async async def _get_vulnerability_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type."""
        high_severity: List[Any] = ["sql_injection", "command_injection"]
        medium_severity: List[Any] = ["xss", "path_traversal"]
        
        if vuln_type in high_severity:
            return "high"
        elif vuln_type in medium_severity:
            return "medium"
        else:
            return "low"

class SecurityAnalyzer:
    """Comprehensive security analysis utilities."""
    
    def __init__(self) -> Any:
        self.network_scanner = NetworkScanner()
        self.web_scanner = WebVulnerabilityScanner()
    
    async def comprehensive_scan(self, target: str) -> Dict[str, Any]:
        """Perform comprehensive security scan."""
        results: Dict[str, Any] = {
            "target": target,
            "timestamp": datetime.now(),
            "scans": {},
            "overall_risk": "low",
            "recommendations": []
        }
        
        try:
            # Determine target type
            if target.startswith(("http://", "https://")):
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
                # Web application scan
                web_scan = await self.web_scanner.scan_url(target)
                results["scans"]["web"] = web_scan.__dict__
                
                # Network scan of the host
                parsed_url = urlparse(target)
                network_scan = await self.network_scanner.scan_host(parsed_url.hostname)
                results["scans"]["network"] = network_scan.__dict__
                
            else:
                # Network scan only
                network_scan = await self.network_scanner.scan_host(target)
                results["scans"]["network"] = network_scan.__dict__
            
            # Calculate overall risk
            risk_levels: List[Any] = [scan.risk_level for scan in results["scans"].values()]
            if "high" in risk_levels:
                results["overall_risk"] = "high"
            elif "medium" in risk_levels:
                results["overall_risk"] = "medium"
            
            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results["scans"])
            
        except Exception as e:
            logger.error(f"Comprehensive scan error: {e}")
            results["error"] = str(e)
        
        return results
    
    def _generate_recommendations(self, scans: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on scan results."""
        recommendations: List[Any] = []
        
        for scan_type, scan_data in scans.items():
            if scan_type == "web":
                web_results = scan_data["results"]
                
                # Check for vulnerabilities
                for vuln in web_results.get("vulnerabilities", []):
                    if vuln["type"] == "sql_injection":
                        recommendations.append("Implement parameterized queries and input validation")
                    elif vuln["type"] == "xss":
                        recommendations.append("Implement proper output encoding and CSP headers")
                    elif vuln["type"] == "path_traversal":
                        recommendations.append("Validate and sanitize file paths")
                
                # Check SSL
                ssl_info = web_results.get("ssl_info", {})
                if not ssl_info.get("valid", False):
                    recommendations.append("Enable and properly configure SSL/TLS")
                
                # Check security headers
                headers = web_results.get("headers", {})
                if "X-Frame-Options" not in headers:
                    recommendations.append("Add X-Frame-Options header to prevent clickjacking")
                if "X-Content-Type-Options" not in headers:
                    recommendations.append("Add X-Content-Type-Options header")
            
            elif scan_type == "network":
                network_results = scan_data["results"]
                open_ports = network_results.get("open_ports", [])
                
                # Check for risky services
                risky_services: List[Any] = [22, 23, 21, 3306, 5432]
                open_risky: List[Any] = [p for p in open_ports if p in risky_services]
                
                if open_risky:
                    recommendations.append(f"Close unnecessary ports: {open_risky}")
                    recommendations.append("Use strong authentication for SSH")
                    recommendations.append("Disable Telnet and FTP")
        
        return list(set(recommendations))  # Remove duplicates

class ThreatIntelligence:
    """Threat intelligence and monitoring utilities."""
    
    def __init__(self) -> Any:
        self.malicious_ips = set()
        self.suspicious_patterns: List[Any] = [
            r"union.*select",
            r"script.*alert",
            r"\.\./\.\./",
            r";.*ls",
            r"eval\(",
            r"exec\("
        ]
    
    async async async async def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation using threat intelligence feeds."""
        try:
            # This is a simplified example - in production, use real threat intelligence APIs
            reputation_data: Dict[str, Any] = {
                "ip": ip,
                "reputation": "unknown",
                "threat_score": 0,
                "categories": [],
                "last_seen": None,
                "sources": []
            }
            
            # Check against known malicious patterns
            if ip in self.malicious_ips:
                reputation_data["reputation"] = "malicious"
                reputation_data["threat_score"] = 100
            
            # DNS-based reputation check
            try:
                reverse_dns = socket.gethostbyaddr(ip)[0]
                if any(suspicious in reverse_dns.lower() for suspicious in ["bot", "malware", "spam"]):
                    reputation_data["reputation"] = "suspicious"
                    reputation_data["threat_score"] = 50
            except:
                pass
            
            return reputation_data
            
        except Exception as e:
            logger.error(f"IP reputation check error: {e}")
            return {"ip": ip, "error": str(e)}
    
    def analyze_log_patterns(self, logs: List[str]) -> Dict[str, Any]:
        """Analyze log patterns for security threats."""
        analysis: Dict[str, Any] = {
            "suspicious_activities": [],
            "attack_patterns": [],
            "anomalies": [],
            "risk_score": 0
        }
        
        for log in logs:
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    analysis["suspicious_activities"].append({
                        "pattern": pattern,
                        "log_entry": log
                    })
            
            # Check for brute force attempts
            if "failed login" in log.lower() or "authentication failed" in log.lower():
                analysis["attack_patterns"].append("brute_force")
            
            # Check for unusual access patterns
            if "admin" in log.lower() and "login" in log.lower():
                analysis["anomalies"].append("admin_access")
        
        # Calculate risk score
        analysis["risk_score"] = (
            len(analysis["suspicious_activities"]) * 10 +
            len(analysis["attack_patterns"]) * 20 +
            len(analysis["anomalies"]) * 5
        )
        
        return analysis

# Utility functions
def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure token."""
    return secrets.token_urlsafe(length)

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hash a password with salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use PBKDF2 for password hashing
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    
    return key.hex(), salt

def verify_password_hash(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its hash."""
    computed_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(computed_hash, hashed)

async async async def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove potentially dangerous characters
    dangerous_chars: List[Any] = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')']
    sanitized = input_str
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized

# Example usage
async def main() -> Any:
    """Example usage of cybersecurity utilities."""
    
    # Initialize scanners
    analyzer = SecurityAnalyzer()
    threat_intel = ThreatIntelligence()
    
    # Example targets
    targets: List[Any] = [
        "https://example.com",
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
        "192.168.1.1",
        "google.com"
    ]
    
    for target in targets:
        print(f"\nScanning {target}...")
        
        # Comprehensive scan
        scan_results = await analyzer.comprehensive_scan(target)
        print(f"Overall risk: {scan_results['overall_risk']}")
        print(f"Recommendations: {scan_results['recommendations']}")
        
        # Threat intelligence
        if not target.startswith(("http://", "https://")):
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
            reputation = await threat_intel.check_ip_reputation(target)
            print(f"IP reputation: {reputation['reputation']}")

match __name__:
    case "__main__":
    asyncio.run(main()) 