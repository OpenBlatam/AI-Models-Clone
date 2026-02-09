from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from dataclasses import dataclass

# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum
from datetime import datetime
import ipaddress
import re
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Pydantic Models

Core data models for the cybersecurity toolkit.
"""


# ============================================================================
# BASE MODELS
# ============================================================================

class BaseRequest(BaseModel):
    """Base request model."""
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Request timestamp")
    source: Optional[str] = Field(None, description="Request source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BaseResult(BaseModel):
    """Base result model."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Operation success status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Result timestamp")
    duration: float = Field(..., description="Operation duration in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class BaseConfig(BaseModel):
    """Base configuration model."""
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    enabled: bool = Field(default=True, description="Configuration enabled status")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Operation timeout")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retries")
    max_concurrent: int = Field(default=10, ge=1, le=100, description="Maximum concurrent operations")

# ============================================================================
# SCAN MODELS
# ============================================================================

class ScanStatus(str, Enum):
    """Scan status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ScanType(str, Enum):
    """Scan type enumeration."""
    PORT_SCAN = "port_scan"
    VULNERABILITY_SCAN = "vulnerability_scan"
    NETWORK_SCAN = "network_scan"
    WEB_SCAN = "web_scan"
    SSL_SCAN = "ssl_scan"
    DNS_SCAN = "dns_scan"
    COMPREHENSIVE_SCAN = "comprehensive_scan"

class ScanRequest(BaseRequest):
    """Scan request model."""
    scan_type: ScanType = Field(..., description="Type of scan to perform")
    targets: List[str] = Field(..., min_items=1, description="Target hosts/IPs to scan")
    ports: Optional[List[int]] = Field(None, description="Specific ports to scan")
    scan_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Scan configuration")
    
    @validator('targets')
    def validate_targets(cls, v) -> Optional[Dict[str, Any]]:
        """Validate target format."""
        for target in v:
            if not re.match(r'^[a-zA-Z0-9.-]+$', target) and not cls._is_valid_ip(target):
                raise ValueError(f"Invalid target format: {target}")
        return v
    
    @validator('ports')
    def validate_ports(cls, v) -> bool:
        """Validate port numbers."""
        if v:
            for port in v:
                if not 1 <= port <= 65535:
                    raise ValueError(f"Invalid port number: {port}")
        return v
    
    @staticmethod
    def _is_valid_ip(ip_str: str) -> bool:
        """Check if string is valid IP address."""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

class ScanResult(BaseResult):
    """Scan result model."""
    scan_type: ScanType = Field(..., description="Type of scan performed")
    targets_scanned: List[str] = Field(..., description="Targets that were scanned")
    results: Dict[str, Any] = Field(default_factory=dict, description="Scan results")
    vulnerabilities_found: int = Field(default=0, ge=0, description="Number of vulnerabilities found")
    scan_duration: float = Field(..., description="Total scan duration")
    scan_status: ScanStatus = Field(..., description="Final scan status")

class ScanConfig(BaseConfig):
    """Scan configuration model."""
    scan_type: ScanType = Field(..., description="Scan type")
    default_ports: List[int] = Field(default=[21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995], description="Default ports to scan")
    scan_speed: str = Field(default="normal", regex="^(slow|normal|fast|aggressive)$", description="Scan speed")
    service_detection: bool = Field(default=True, description="Enable service detection")
    os_detection: bool = Field(default=False, description="Enable OS detection")
    script_scanning: bool = Field(default=False, description="Enable script scanning")

# ============================================================================
# VULNERABILITY MODELS
# ============================================================================

class VulnerabilityLevel(str, Enum):
    """Vulnerability severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VulnerabilityType(str, Enum):
    """Vulnerability types."""
    BUFFER_OVERFLOW = "buffer_overflow"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    WEAK_ENCRYPTION = "weak_encryption"
    MISCONFIGURATION = "misconfiguration"
    OUTDATED_SOFTWARE = "outdated_software"
    DEFAULT_CREDENTIALS = "default_credentials"
    OPEN_PORTS = "open_ports"
    SSL_TLS_ISSUES = "ssl_tls_issues"

class Vulnerability(BaseModel):
    """Vulnerability model."""
    id: str = Field(..., description="Unique vulnerability identifier")
    title: str = Field(..., description="Vulnerability title")
    description: str = Field(..., description="Vulnerability description")
    level: VulnerabilityLevel = Field(..., description="Vulnerability severity level")
    type: VulnerabilityType = Field(..., description="Vulnerability type")
    cve_id: Optional[str] = Field(None, description="CVE identifier")
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="CVSS score")
    affected_target: str = Field(..., description="Affected target")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Affected port")
    service: Optional[str] = Field(None, description="Affected service")
    evidence: Optional[str] = Field(None, description="Evidence of vulnerability")
    recommendation: Optional[str] = Field(None, description="Remediation recommendation")
    discovered_at: datetime = Field(default_factory=datetime.now, description="Discovery timestamp")
    references: List[str] = Field(default_factory=list, description="Reference links")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VulnerabilityReport(BaseModel):
    """Vulnerability report model."""
    report_id: str = Field(..., description="Unique report identifier")
    scan_id: str = Field(..., description="Associated scan identifier")
    target: str = Field(..., description="Target host")
    scan_date: datetime = Field(default_factory=datetime.now, description="Scan date")
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="List of vulnerabilities")
    summary: Dict[str, int] = Field(default_factory=dict, description="Vulnerability summary by level")
    risk_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Overall risk score")
    
    @root_validator
    def calculate_summary(cls, values) -> Any:
        """Calculate vulnerability summary."""
        vulnerabilities = values.get('vulnerabilities', [])
        summary = {}
        for vuln in vulnerabilities:
            level = vuln.level.value
            summary[level] = summary.get(level, 0) + 1
        values['summary'] = summary
        return values
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ============================================================================
# NETWORK MODELS
# ============================================================================

class NetworkTarget(BaseModel):
    """Network target model."""
    host: str = Field(..., description="Target hostname or IP")
    ip_address: Optional[str] = Field(None, description="Resolved IP address")
    hostname: Optional[str] = Field(None, description="Resolved hostname")
    is_alive: bool = Field(default=False, description="Host is alive")
    response_time: Optional[float] = Field(None, description="Response time in milliseconds")
    os_info: Optional[Dict[str, Any]] = Field(None, description="Operating system information")
    
    @validator('host')
    def validate_host(cls, v) -> bool:
        """Validate host format."""
        if not re.match(r'^[a-zA-Z0-9.-]+$', v) and not cls._is_valid_ip(v):
            raise ValueError(f"Invalid host format: {v}")
        return v
    
    @staticmethod
    def _is_valid_ip(ip_str: str) -> bool:
        """Check if string is valid IP address."""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False

class NetworkPort(BaseModel):
    """Network port model."""
    port: int = Field(..., ge=1, le=65535, description="Port number")
    protocol: str = Field(default="tcp", regex="^(tcp|udp)$", description="Protocol")
    state: str = Field(default="closed", regex="^(open|closed|filtered|open|filtered)$", description="Port state")
    service: Optional[str] = Field(None, description="Service name")
    version: Optional[str] = Field(None, description="Service version")
    banner: Optional[str] = Field(None, description="Service banner")
    script_output: Optional[Dict[str, Any]] = Field(None, description="NSE script output")

class NetworkService(BaseModel):
    """Network service model."""
    name: str = Field(..., description="Service name")
    port: int = Field(..., ge=1, le=65535, description="Service port")
    protocol: str = Field(default="tcp", description="Service protocol")
    version: Optional[str] = Field(None, description="Service version")
    product: Optional[str] = Field(None, description="Product name")
    extra_info: Optional[str] = Field(None, description="Additional service information")
    banner: Optional[str] = Field(None, description="Service banner")
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="Service vulnerabilities")

class NetworkHost(BaseModel):
    """Network host model."""
    target: NetworkTarget = Field(..., description="Host target information")
    ports: List[NetworkPort] = Field(default_factory=list, description="Open ports")
    services: List[NetworkService] = Field(default_factory=list, description="Running services")
    vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="Host vulnerabilities")
    scan_time: float = Field(..., description="Time taken to scan host")
    last_seen: datetime = Field(default_factory=datetime.now, description="Last scan timestamp")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NetworkScan(BaseModel):
    """Network scan model."""
    scan_id: str = Field(..., description="Unique scan identifier")
    targets: List[NetworkTarget] = Field(..., description="Scanned targets")
    hosts: List[NetworkHost] = Field(default_factory=list, description="Discovered hosts")
    scan_config: ScanConfig = Field(..., description="Scan configuration")
    start_time: datetime = Field(default_factory=datetime.now, description="Scan start time")
    end_time: Optional[datetime] = Field(None, description="Scan end time")
    duration: Optional[float] = Field(None, description="Total scan duration")
    status: ScanStatus = Field(default=ScanStatus.PENDING, description="Scan status")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ============================================================================
# ATTACK MODELS
# ============================================================================

class AttackType(str, Enum):
    """Attack type enumeration."""
    BRUTE_FORCE = "brute_force"
    EXPLOIT = "exploit"
    DOS = "dos"
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    MAN_IN_THE_MIDDLE = "man_in_the_middle"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    BUFFER_OVERFLOW = "buffer_overflow"

class AttackRequest(BaseRequest):
    """Attack request model."""
    attack_type: AttackType = Field(..., description="Type of attack to perform")
    target: str = Field(..., description="Attack target")
    payload: Optional[Dict[str, Any]] = Field(None, description="Attack payload")
    credentials: Optional[Dict[str, str]] = Field(None, description="Target credentials")
    attack_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Attack configuration")
    
    @validator('target')
    def validate_target(cls, v) -> Optional[Dict[str, Any]]:
        """Validate target format."""
        if not re.match(r'^[a-zA-Z0-9.-:]+$', v):
            raise ValueError(f"Invalid target format: {v}")
        return v

class AttackPayload(BaseModel):
    """Attack payload model."""
    payload_id: str = Field(..., description="Unique payload identifier")
    payload_type: str = Field(..., description="Payload type")
    content: str = Field(..., description="Payload content")
    encoding: str = Field(default="utf-8", description="Payload encoding")
    size: int = Field(..., ge=0, description="Payload size in bytes")
    checksum: Optional[str] = Field(None, description="Payload checksum")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Payload metadata")

class AttackSession(BaseModel):
    """Attack session model."""
    session_id: str = Field(..., description="Unique session identifier")
    attack_type: AttackType = Field(..., description="Attack type")
    target: str = Field(..., description="Attack target")
    start_time: datetime = Field(default_factory=datetime.now, description="Session start time")
    end_time: Optional[datetime] = Field(None, description="Session end time")
    status: str = Field(default="active", description="Session status")
    attempts: int = Field(default=0, ge=0, description="Number of attempts")
    successful_attempts: int = Field(default=0, ge=0, description="Successful attempts")
    payloads_used: List[AttackPayload] = Field(default_factory=list, description="Payloads used")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AttackResult(BaseResult):
    """Attack result model."""
    attack_type: AttackType = Field(..., description="Type of attack performed")
    target: str = Field(..., description="Attack target")
    success: bool = Field(..., description="Attack success status")
    payload_used: Optional[AttackPayload] = Field(None, description="Payload used in attack")
    session_info: Optional[AttackSession] = Field(None, description="Attack session information")
    discovered_vulnerabilities: List[Vulnerability] = Field(default_factory=list, description="Discovered vulnerabilities")
    attack_data: Dict[str, Any] = Field(default_factory=dict, description="Attack-specific data")

# ============================================================================
# REPORT MODELS
# ============================================================================

class ReportFormat(str, Enum):
    """Report format enumeration."""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    XML = "xml"
    MARKDOWN = "markdown"

class ReportLevel(str, Enum):
    """Report detail level."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"

class ReportSection(str, Enum):
    """Report section types."""
    EXECUTIVE_SUMMARY = "executive_summary"
    METHODOLOGY = "methodology"
    FINDINGS = "findings"
    VULNERABILITIES = "vulnerabilities"
    RECOMMENDATIONS = "recommendations"
    APPENDIX = "appendix"

class ReportRequest(BaseRequest):
    """Report request model."""
    report_format: ReportFormat = Field(..., description="Report format")
    report_level: ReportLevel = Field(default=ReportLevel.DETAILED, description="Report detail level")
    sections: List[ReportSection] = Field(default_factory=list, description="Report sections to include")
    scan_results: List[ScanResult] = Field(default_factory=list, description="Scan results to include")
    attack_results: List[AttackResult] = Field(default_factory=list, description="Attack results to include")
    custom_data: Dict[str, Any] = Field(default_factory=dict, description="Custom data for report")
    template: Optional[str] = Field(None, description="Report template to use")

class ReportResult(BaseResult):
    """Report result model."""
    report_format: ReportFormat = Field(..., description="Generated report format")
    report_level: ReportLevel = Field(..., description="Report detail level")
    report_content: str = Field(..., description="Report content")
    report_size: int = Field(..., ge=0, description="Report size in bytes")
    sections_included: List[ReportSection] = Field(default_factory=list, description="Sections included in report")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ============================================================================
# ENUMERATION MODELS
# ============================================================================

class EnumerationType(str, Enum):
    """Enumeration type enumeration."""
    PORT_ENUMERATION = "port_enumeration"
    SERVICE_ENUMERATION = "service_enumeration"
    USER_ENUMERATION = "user_enumeration"
    DIRECTORY_ENUMERATION = "directory_enumeration"
    DNS_ENUMERATION = "dns_enumeration"
    SUBDOMAIN_ENUMERATION = "subdomain_enumeration"

class ServiceInfo(BaseModel):
    """Service information model."""
    service_name: str = Field(..., description="Service name")
    port: int = Field(..., ge=1, le=65535, description="Service port")
    protocol: str = Field(default="tcp", description="Service protocol")
    version: Optional[str] = Field(None, description="Service version")
    banner: Optional[str] = Field(None, description="Service banner")
    fingerprint: Optional[str] = Field(None, description="Service fingerprint")

class PortInfo(BaseModel):
    """Port information model."""
    port: int = Field(..., ge=1, le=65535, description="Port number")
    protocol: str = Field(default="tcp", description="Port protocol")
    state: str = Field(default="closed", description="Port state")
    service: Optional[ServiceInfo] = Field(None, description="Service information")
    last_checked: datetime = Field(default_factory=datetime.now, description="Last check timestamp")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EnumerationRequest(BaseRequest):
    """Enumeration request model."""
    enumeration_type: EnumerationType = Field(..., description="Type of enumeration")
    target: str = Field(..., description="Enumeration target")
    ports: Optional[List[int]] = Field(None, description="Ports to enumerate")
    wordlist: Optional[str] = Field(None, description="Wordlist to use")
    enumeration_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Enumeration configuration")

class EnumerationResult(BaseResult):
    """Enumeration result model."""
    enumeration_type: EnumerationType = Field(..., description="Type of enumeration performed")
    target: str = Field(..., description="Enumeration target")
    discovered_items: List[Any] = Field(default_factory=list, description="Discovered items")
    ports_found: List[PortInfo] = Field(default_factory=list, description="Discovered ports")
    services_found: List[ServiceInfo] = Field(default_factory=list, description="Discovered services")
    enumeration_data: Dict[str, Any] = Field(default_factory=dict, description="Enumeration-specific data")

# ============================================================================
# CRYPTO MODELS (from utils)
# ============================================================================

class CryptoOperation(str, Enum):
    """Cryptographic operation enumeration."""
    HASH = "hash"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    KEY_GENERATION = "key_generation"
    KEY_DERIVATION = "key_derivation"

class HashAlgorithm(str, Enum):
    """Hash algorithm enumeration."""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"
    SHA3_256 = "sha3_256"
    SHA3_512 = "sha3_512"

class EncryptionAlgorithm(str, Enum):
    """Encryption algorithm enumeration."""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    AES_128_GCM = "aes_128_gcm"
    AES_128_CBC = "aes_128_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"

class CryptoRequest(BaseRequest):
    """Crypto request model."""
    operation: CryptoOperation = Field(..., description="Cryptographic operation")
    data: Union[str, bytes] = Field(..., description="Data to process")
    algorithm: Optional[Union[HashAlgorithm, EncryptionAlgorithm]] = Field(None, description="Algorithm to use")
    key: Optional[Union[str, bytes]] = Field(None, description="Encryption/decryption key")
    salt: Optional[Union[str, bytes]] = Field(None, description="Salt for key derivation")
    iterations: int = Field(default=100000, ge=1000, le=1000000, description="PBKDF2 iterations")

class CryptoResult(BaseResult):
    """Crypto result model."""
    operation: CryptoOperation = Field(..., description="Cryptographic operation performed")
    algorithm: Optional[Union[HashAlgorithm, EncryptionAlgorithm]] = Field(None, description="Algorithm used")
    input_data: Union[str, bytes] = Field(..., description="Input data")
    output_data: Union[str, bytes] = Field(..., description="Output data")
    operation_duration: float = Field(..., description="Operation duration")

# ============================================================================
# NETWORK MODELS (from utils)
# ============================================================================

class NetworkOperation(str, Enum):
    """Network operation enumeration."""
    DNS_LOOKUP = "dns_lookup"
    HTTP_REQUEST = "http_request"
    HTTPS_REQUEST = "https_request"
    PORT_CHECK = "port_check"
    HOSTNAME_RESOLVE = "hostname_resolve"
    NETWORK_INFO = "network_info"
    TRACEROUTE = "traceroute"
    CONNECTIVITY_CHECK = "connectivity_check"
    SSL_CERTIFICATE = "ssl_certificate"
    WHOIS_LOOKUP = "whois_lookup"
    GEOLOCATION = "geolocation"
    ARP_SCAN = "arp_scan"

class NetworkRequest(BaseRequest):
    """Network request model."""
    operation: NetworkOperation = Field(..., description="Network operation")
    target: str = Field(..., description="Target host/URL")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Target port")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Operation timeout")
    retries: int = Field(default=3, ge=1, le=10, description="Number of retries")

class NetworkResult(BaseResult):
    """Network result model."""
    operation: NetworkOperation = Field(..., description="Network operation performed")
    target: str = Field(..., description="Target host/URL")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Operation result data")
    operation_duration: float = Field(..., description="Operation duration")

# ============================================================================
# UTILITY MODELS
# ============================================================================

class FileInfo(BaseModel):
    """File information model."""
    filename: str = Field(..., description="File name")
    filepath: str = Field(..., description="File path")
    size: int = Field(..., ge=0, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="File checksum")
    mime_type: Optional[str] = Field(None, description="File MIME type")
    created_at: Optional[datetime] = Field(None, description="File creation time")
    modified_at: Optional[datetime] = Field(None, description="File modification time")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProcessInfo(BaseModel):
    """Process information model."""
    pid: int = Field(..., ge=1, description="Process ID")
    name: str = Field(..., description="Process name")
    command: str = Field(..., description="Process command")
    user: str = Field(..., description="Process user")
    memory_usage: Optional[int] = Field(None, ge=0, description="Memory usage in bytes")
    cpu_usage: Optional[float] = Field(None, ge=0.0, le=100.0, description="CPU usage percentage")
    start_time: Optional[datetime] = Field(None, description="Process start time")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SystemInfo(BaseModel):
    """System information model."""
    hostname: str = Field(..., description="System hostname")
    os_name: str = Field(..., description="Operating system name")
    os_version: str = Field(..., description="Operating system version")
    architecture: str = Field(..., description="System architecture")
    cpu_count: int = Field(..., ge=1, description="Number of CPU cores")
    memory_total: int = Field(..., ge=0, description="Total memory in bytes")
    uptime: float = Field(..., ge=0, description="System uptime in seconds")
    boot_time: Optional[datetime] = Field(None, description="System boot time")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LogEntry(BaseModel):
    """Log entry model."""
    timestamp: datetime = Field(default_factory=datetime.now, description="Log timestamp")
    level: str = Field(..., regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="Log level")
    message: str = Field(..., description="Log message")
    source: str = Field(..., description="Log source")
    module: Optional[str] = Field(None, description="Module name")
    function: Optional[str] = Field(None, description="Function name")
    line_number: Optional[int] = Field(None, ge=1, description="Line number")
    exception: Optional[str] = Field(None, description="Exception information")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorInfo(BaseModel):
    """Error information model."""
    error_id: str = Field(..., description="Unique error identifier")
    error_type: str = Field(..., description="Error type")
    error_message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    severity: str = Field(default="medium", regex="^(low|medium|high|critical)$", description="Error severity")
    
    @dataclass
class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 