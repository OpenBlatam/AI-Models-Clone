"""
Pydantic Schemas

Validation and serialization schemas for the cybersecurity toolkit.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
import re

from .models import (
    # Base Models
    BaseRequest, BaseResult, BaseConfig,
    
    # Scan Models
    ScanRequest, ScanResult, ScanConfig, ScanStatus, ScanType,
    
    # Vulnerability Models
    Vulnerability, VulnerabilityLevel, VulnerabilityType, VulnerabilityReport,
    
    # Network Models
    NetworkTarget, NetworkPort, NetworkService, NetworkHost, NetworkScan,
    
    # Attack Models
    AttackRequest, AttackResult, AttackType, AttackPayload, AttackSession,
    
    # Report Models
    ReportRequest, ReportResult, ReportFormat, ReportLevel, ReportSection,
    
    # Enumeration Models
    EnumerationRequest, EnumerationResult, EnumerationType, ServiceInfo, PortInfo,
    
    # Crypto Models
    CryptoRequest, CryptoResult, CryptoOperation, HashAlgorithm, EncryptionAlgorithm,
    
    # Network Models
    NetworkRequest, NetworkResult, NetworkOperation,
    
    # Utility Models
    FileInfo, ProcessInfo, SystemInfo, LogEntry, ErrorInfo
)

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ScanRequestSchema(BaseModel):
    """Schema for scan request validation."""
    scan_type: ScanType = Field(..., description="Type of scan to perform")
    targets: List[str] = Field(..., min_items=1, max_items=1000, description="Target hosts/IPs")
    ports: Optional[List[int]] = Field(None, description="Specific ports to scan")
    scan_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Scan configuration")
    
    @validator('targets')
    def validate_targets(cls, v):
        """Validate target format and count."""
        if len(v) > 1000:
            raise ValueError("Maximum 1000 targets allowed")
        
        for target in v:
            if not re.match(r'^[a-zA-Z0-9.-]+$', target) and not cls._is_valid_ip(target):
                raise ValueError(f"Invalid target format: {target}")
        return v
    
    @validator('ports')
    def validate_ports(cls, v):
        """Validate port numbers."""
        if v:
            if len(v) > 65535:
                raise ValueError("Too many ports specified")
            
            for port in v:
                if not 1 <= port <= 65535:
                    raise ValueError(f"Invalid port number: {port}")
        return v
    
    @staticmethod
    def _is_valid_ip(ip_str: str) -> bool:
        """Check if string is valid IP address."""
        try:
            import ipaddress
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    class Config:
        schema_extra = {
            "example": {
                "scan_type": "port_scan",
                "targets": ["192.168.1.1", "example.com"],
                "ports": [80, 443, 22, 21],
                "scan_config": {
                    "timeout": 30,
                    "retries": 3
                }
            }
        }

class AttackRequestSchema(BaseModel):
    """Schema for attack request validation."""
    attack_type: AttackType = Field(..., description="Type of attack to perform")
    target: str = Field(..., description="Attack target")
    payload: Optional[Dict[str, Any]] = Field(None, description="Attack payload")
    credentials: Optional[Dict[str, str]] = Field(None, description="Target credentials")
    attack_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Attack configuration")
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not re.match(r'^[a-zA-Z0-9.-:]+$', v):
            raise ValueError(f"Invalid target format: {v}")
        return v
    
    @validator('credentials')
    def validate_credentials(cls, v):
        """Validate credentials format."""
        if v:
            required_fields = ['username', 'password']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f"Missing required credential field: {field}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "attack_type": "brute_force",
                "target": "192.168.1.1:22",
                "credentials": {
                    "username": "admin",
                    "password": "password123"
                },
                "attack_config": {
                    "timeout": 10,
                    "max_attempts": 100
                }
            }
        }

class EnumerationRequestSchema(BaseModel):
    """Schema for enumeration request validation."""
    enumeration_type: EnumerationType = Field(..., description="Type of enumeration")
    target: str = Field(..., description="Enumeration target")
    ports: Optional[List[int]] = Field(None, description="Ports to enumerate")
    wordlist: Optional[str] = Field(None, description="Wordlist to use")
    enumeration_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Enumeration configuration")
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not re.match(r'^[a-zA-Z0-9.-]+$', v):
            raise ValueError(f"Invalid target format: {v}")
        return v
    
    @validator('ports')
    def validate_ports(cls, v):
        """Validate port numbers."""
        if v:
            for port in v:
                if not 1 <= port <= 65535:
                    raise ValueError(f"Invalid port number: {port}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "enumeration_type": "port_enumeration",
                "target": "192.168.1.1",
                "ports": [21, 22, 23, 25, 80, 443],
                "enumeration_config": {
                    "timeout": 5,
                    "service_detection": True
                }
            }
        }

class ReportRequestSchema(BaseModel):
    """Schema for report request validation."""
    report_format: ReportFormat = Field(..., description="Report format")
    report_level: ReportLevel = Field(default=ReportLevel.DETAILED, description="Report detail level")
    sections: List[ReportSection] = Field(default_factory=list, description="Report sections to include")
    scan_results: List[str] = Field(default_factory=list, description="Scan result IDs to include")
    attack_results: List[str] = Field(default_factory=list, description="Attack result IDs to include")
    custom_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom data for report")
    template: Optional[str] = Field(None, description="Report template to use")
    
    @validator('sections')
    def validate_sections(cls, v):
        """Validate report sections."""
        if not v:
            v = [ReportSection.EXECUTIVE_SUMMARY, ReportSection.FINDINGS, ReportSection.RECOMMENDATIONS]
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "report_format": "html",
                "report_level": "detailed",
                "sections": ["executive_summary", "findings", "recommendations"],
                "scan_results": ["scan_001", "scan_002"],
                "custom_data": {
                    "client_name": "Example Corp",
                    "project_name": "Security Assessment"
                }
            }
        }

class CryptoRequestSchema(BaseModel):
    """Schema for crypto request validation."""
    operation: CryptoOperation = Field(..., description="Cryptographic operation")
    data: Union[str, bytes] = Field(..., description="Data to process")
    algorithm: Optional[Union[HashAlgorithm, EncryptionAlgorithm]] = Field(None, description="Algorithm to use")
    key: Optional[Union[str, bytes]] = Field(None, description="Encryption/decryption key")
    salt: Optional[Union[str, bytes]] = Field(None, description="Salt for key derivation")
    iterations: int = Field(default=100000, ge=1000, le=1000000, description="PBKDF2 iterations")
    
    @validator('data')
    def validate_data(cls, v):
        """Validate data is not empty."""
        if not v:
            raise ValueError("Data cannot be empty")
        return v
    
    @root_validator
    def validate_operation_requirements(cls, values):
        """Validate operation-specific requirements."""
        operation = values.get('operation')
        algorithm = values.get('algorithm')
        key = values.get('key')
        
        if operation in [CryptoOperation.ENCRYPT, CryptoOperation.DECRYPT] and not key:
            raise ValueError(f"Key required for {operation} operation")
        
        if operation in [CryptoOperation.HASH, CryptoOperation.ENCRYPT, CryptoOperation.DECRYPT] and not algorithm:
            raise ValueError(f"Algorithm required for {operation} operation")
        
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "operation": "hash",
                "data": "Hello, World!",
                "algorithm": "sha256"
            }
        }

class NetworkRequestSchema(BaseModel):
    """Schema for network request validation."""
    operation: NetworkOperation = Field(..., description="Network operation")
    target: str = Field(..., description="Target host/URL")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Target port")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Operation timeout")
    retries: int = Field(default=3, ge=1, le=10, description="Number of retries")
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not re.match(r'^[a-zA-Z0-9.-:/]+$', v):
            raise ValueError(f"Invalid target format: {v}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "operation": "dns_lookup",
                "target": "google.com",
                "timeout": 10.0,
                "retries": 3
            }
        }

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ScanResponseSchema(BaseModel):
    """Schema for scan response validation."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Operation success status")
    scan_type: ScanType = Field(..., description="Type of scan performed")
    targets_scanned: List[str] = Field(..., description="Targets that were scanned")
    results: Dict[str, Any] = Field(default_factory=dict, description="Scan results")
    vulnerabilities_found: int = Field(default=0, ge=0, description="Number of vulnerabilities found")
    scan_duration: float = Field(..., ge=0, description="Total scan duration")
    scan_status: ScanStatus = Field(..., description="Final scan status")
    timestamp: datetime = Field(..., description="Response timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "request_id": "scan_001",
                "success": True,
                "scan_type": "port_scan",
                "targets_scanned": ["192.168.1.1"],
                "results": {
                    "open_ports": [80, 443, 22],
                    "services": ["http", "https", "ssh"]
                },
                "vulnerabilities_found": 2,
                "scan_duration": 45.2,
                "scan_status": "completed",
                "timestamp": "2023-01-01T12:00:00Z"
            }
        }

class AttackResponseSchema(BaseModel):
    """Schema for attack response validation."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Operation success status")
    attack_type: AttackType = Field(..., description="Type of attack performed")
    target: str = Field(..., description="Attack target")
    attack_success: bool = Field(..., description="Attack success status")
    discovered_vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list, description="Discovered vulnerabilities")
    attack_data: Dict[str, Any] = Field(default_factory=dict, description="Attack-specific data")
    timestamp: datetime = Field(..., description="Response timestamp")
    duration: float = Field(..., ge=0, description="Operation duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "request_id": "attack_001",
                "success": True,
                "attack_type": "brute_force",
                "target": "192.168.1.1:22",
                "attack_success": True,
                "discovered_vulnerabilities": [
                    {
                        "type": "weak_credentials",
                        "severity": "high",
                        "description": "Weak SSH password found"
                    }
                ],
                "attack_data": {
                    "attempts": 50,
                    "successful_credentials": {"username": "admin", "password": "admin123"}
                },
                "timestamp": "2023-01-01T12:00:00Z",
                "duration": 120.5
            }
        }

class EnumerationResponseSchema(BaseModel):
    """Schema for enumeration response validation."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Operation success status")
    enumeration_type: EnumerationType = Field(..., description="Type of enumeration performed")
    target: str = Field(..., description="Enumeration target")
    discovered_items: List[Any] = Field(default_factory=list, description="Discovered items")
    ports_found: List[Dict[str, Any]] = Field(default_factory=list, description="Discovered ports")
    services_found: List[Dict[str, Any]] = Field(default_factory=list, description="Discovered services")
    enumeration_data: Dict[str, Any] = Field(default_factory=dict, description="Enumeration-specific data")
    timestamp: datetime = Field(..., description="Response timestamp")
    duration: float = Field(..., ge=0, description="Operation duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "request_id": "enum_001",
                "success": True,
                "enumeration_type": "port_enumeration",
                "target": "192.168.1.1",
                "discovered_items": ["ssh", "http", "https"],
                "ports_found": [
                    {"port": 22, "service": "ssh", "state": "open"},
                    {"port": 80, "service": "http", "state": "open"}
                ],
                "services_found": [
                    {"name": "ssh", "port": 22, "version": "OpenSSH 8.2p1"},
                    {"name": "http", "port": 80, "version": "Apache 2.4.41"}
                ],
                "timestamp": "2023-01-01T12:00:00Z",
                "duration": 30.2
            }
        }

class ReportResponseSchema(BaseModel):
    """Schema for report response validation."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Operation success status")
    report_format: ReportFormat = Field(..., description="Generated report format")
    report_level: ReportLevel = Field(..., description="Report detail level")
    report_content: str = Field(..., description="Report content")
    report_size: int = Field(..., ge=0, description="Report size in bytes")
    sections_included: List[ReportSection] = Field(default_factory=list, description="Sections included in report")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    timestamp: datetime = Field(..., description="Response timestamp")
    duration: float = Field(..., ge=0, description="Operation duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "request_id": "report_001",
                "success": True,
                "report_format": "html",
                "report_level": "detailed",
                "report_content": "<html>...</html>",
                "report_size": 15420,
                "sections_included": ["executive_summary", "findings", "recommendations"],
                "generated_at": "2023-01-01T12:00:00Z",
                "timestamp": "2023-01-01T12:00:00Z",
                "duration": 5.3
            }
        }

class CryptoResponseSchema(BaseModel):
    """Schema for crypto response validation."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Operation success status")
    operation: CryptoOperation = Field(..., description="Cryptographic operation performed")
    algorithm: Optional[Union[HashAlgorithm, EncryptionAlgorithm]] = Field(None, description="Algorithm used")
    input_data: Union[str, bytes] = Field(..., description="Input data")
    output_data: Union[str, bytes] = Field(..., description="Output data")
    operation_duration: float = Field(..., ge=0, description="Operation duration")
    timestamp: datetime = Field(..., description="Response timestamp")
    duration: float = Field(..., ge=0, description="Operation duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "request_id": "crypto_001",
                "success": True,
                "operation": "hash",
                "algorithm": "sha256",
                "input_data": "Hello, World!",
                "output_data": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
                "operation_duration": 0.001,
                "timestamp": "2023-01-01T12:00:00Z",
                "duration": 0.001
            }
        }

class NetworkResponseSchema(BaseModel):
    """Schema for network response validation."""
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Operation success status")
    operation: NetworkOperation = Field(..., description="Network operation performed")
    target: str = Field(..., description="Target host/URL")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Operation result data")
    operation_duration: float = Field(..., ge=0, description="Operation duration")
    timestamp: datetime = Field(..., description="Response timestamp")
    duration: float = Field(..., ge=0, description="Operation duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "request_id": "network_001",
                "success": True,
                "operation": "dns_lookup",
                "target": "google.com",
                "result_data": {
                    "domain": "google.com",
                    "records": {
                        "A": ["142.250.190.78"],
                        "AAAA": ["2607:f8b0:4004:c0c::65"]
                    }
                },
                "operation_duration": 0.05,
                "timestamp": "2023-01-01T12:00:00Z",
                "duration": 0.05
            }
        }

# ============================================================================
# CONFIG SCHEMAS
# ============================================================================

class ScannerConfigSchema(BaseModel):
    """Schema for scanner configuration validation."""
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    enabled: bool = Field(default=True, description="Configuration enabled status")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Operation timeout")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retries")
    max_concurrent: int = Field(default=10, ge=1, le=100, description="Maximum concurrent operations")
    default_ports: List[int] = Field(default=[21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995], description="Default ports to scan")
    scan_speed: str = Field(default="normal", regex="^(slow|normal|fast|aggressive)$", description="Scan speed")
    service_detection: bool = Field(default=True, description="Enable service detection")
    os_detection: bool = Field(default=False, description="Enable OS detection")
    script_scanning: bool = Field(default=False, description="Enable script scanning")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "default_scanner",
                "description": "Default scanner configuration",
                "enabled": True,
                "timeout": 30.0,
                "retries": 3,
                "max_concurrent": 10,
                "default_ports": [21, 22, 23, 25, 53, 80, 443],
                "scan_speed": "normal",
                "service_detection": True,
                "os_detection": False,
                "script_scanning": False
            }
        }

class AttackerConfigSchema(BaseModel):
    """Schema for attacker configuration validation."""
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    enabled: bool = Field(default=True, description="Configuration enabled status")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Operation timeout")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retries")
    max_concurrent: int = Field(default=5, ge=1, le=50, description="Maximum concurrent operations")
    max_attempts: int = Field(default=1000, ge=1, le=100000, description="Maximum attack attempts")
    wordlist_path: Optional[str] = Field(None, description="Path to wordlist file")
    payload_directory: Optional[str] = Field(None, description="Directory containing payloads")
    rate_limit: int = Field(default=10, ge=1, le=1000, description="Requests per second")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "default_attacker",
                "description": "Default attacker configuration",
                "enabled": True,
                "timeout": 30.0,
                "retries": 3,
                "max_concurrent": 5,
                "max_attempts": 1000,
                "wordlist_path": "/usr/share/wordlists/rockyou.txt",
                "payload_directory": "/opt/payloads",
                "rate_limit": 10
            }
        }

class ReporterConfigSchema(BaseModel):
    """Schema for reporter configuration validation."""
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    enabled: bool = Field(default=True, description="Configuration enabled status")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Operation timeout")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retries")
    max_concurrent: int = Field(default=5, ge=1, le=50, description="Maximum concurrent operations")
    output_directory: str = Field(default="./reports", description="Output directory for reports")
    template_directory: Optional[str] = Field(None, description="Directory containing report templates")
    default_format: ReportFormat = Field(default=ReportFormat.HTML, description="Default report format")
    include_screenshots: bool = Field(default=True, description="Include screenshots in reports")
    include_logs: bool = Field(default=True, description="Include logs in reports")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "default_reporter",
                "description": "Default reporter configuration",
                "enabled": True,
                "timeout": 30.0,
                "retries": 3,
                "max_concurrent": 5,
                "output_directory": "./reports",
                "template_directory": "./templates",
                "default_format": "html",
                "include_screenshots": True,
                "include_logs": True
            }
        }

class UtilsConfigSchema(BaseModel):
    """Schema for utils configuration validation."""
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    enabled: bool = Field(default=True, description="Configuration enabled status")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Operation timeout")
    retries: int = Field(default=3, ge=0, le=10, description="Number of retries")
    max_concurrent: int = Field(default=10, ge=1, le=100, description="Maximum concurrent operations")
    crypto_timeout: float = Field(default=60.0, ge=1.0, le=600.0, description="Crypto operation timeout")
    network_timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Network operation timeout")
    temp_directory: str = Field(default="/tmp", description="Temporary directory")
    log_level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="Log level")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "default_utils",
                "description": "Default utils configuration",
                "enabled": True,
                "timeout": 30.0,
                "retries": 3,
                "max_concurrent": 10,
                "crypto_timeout": 60.0,
                "network_timeout": 30.0,
                "temp_directory": "/tmp",
                "log_level": "INFO"
            }
        }

# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

class TargetValidationSchema(BaseModel):
    """Schema for target validation."""
    target: str = Field(..., description="Target to validate")
    target_type: str = Field(..., regex="^(ip|domain|url|network)$", description="Target type")
    
    @validator('target')
    def validate_target_format(cls, v, values):
        """Validate target format based on type."""
        target_type = values.get('target_type')
        
        if target_type == 'ip':
            if not cls._is_valid_ip(v):
                raise ValueError(f"Invalid IP address: {v}")
        elif target_type == 'domain':
            if not re.match(r'^[a-zA-Z0-9.-]+$', v):
                raise ValueError(f"Invalid domain format: {v}")
        elif target_type == 'url':
            if not re.match(r'^https?://[a-zA-Z0-9.-]+', v):
                raise ValueError(f"Invalid URL format: {v}")
        elif target_type == 'network':
            if not cls._is_valid_network(v):
                raise ValueError(f"Invalid network format: {v}")
        
        return v
    
    @staticmethod
    def _is_valid_ip(ip_str: str) -> bool:
        """Check if string is valid IP address."""
        try:
            import ipaddress
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _is_valid_network(network_str: str) -> bool:
        """Check if string is valid network."""
        try:
            import ipaddress
            ipaddress.ip_network(network_str, strict=False)
            return True
        except ValueError:
            return False
    
    class Config:
        schema_extra = {
            "example": {
                "target": "192.168.1.1",
                "target_type": "ip"
            }
        }

class PortValidationSchema(BaseModel):
    """Schema for port validation."""
    port: int = Field(..., ge=1, le=65535, description="Port number")
    protocol: str = Field(default="tcp", regex="^(tcp|udp)$", description="Protocol")
    
    class Config:
        schema_extra = {
            "example": {
                "port": 80,
                "protocol": "tcp"
            }
        }

class CredentialValidationSchema(BaseModel):
    """Schema for credential validation."""
    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=1, max_length=100, description="Password")
    domain: Optional[str] = Field(None, description="Domain (for Windows)")
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError("Username contains invalid characters")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "password": "password123",
                "domain": "example.com"
            }
        }

class PayloadValidationSchema(BaseModel):
    """Schema for payload validation."""
    payload_type: str = Field(..., description="Payload type")
    content: str = Field(..., min_length=1, description="Payload content")
    encoding: str = Field(default="utf-8", description="Payload encoding")
    size_limit: int = Field(default=1048576, ge=1, le=10485760, description="Maximum payload size in bytes")
    
    @validator('content')
    def validate_content_size(cls, v, values):
        """Validate payload content size."""
        size_limit = values.get('size_limit', 1048576)
        if len(v.encode('utf-8')) > size_limit:
            raise ValueError(f"Payload content exceeds size limit of {size_limit} bytes")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "payload_type": "sql_injection",
                "content": "' OR 1=1 --",
                "encoding": "utf-8",
                "size_limit": 1048576
            }
        }

# ============================================================================
# EXPORT SCHEMAS
# ============================================================================

class JSONExportSchema(BaseModel):
    """Schema for JSON export validation."""
    data: Dict[str, Any] = Field(..., description="Data to export")
    pretty_print: bool = Field(default=True, description="Pretty print JSON")
    include_metadata: bool = Field(default=True, description="Include metadata")
    compression: bool = Field(default=False, description="Enable compression")
    
    class Config:
        schema_extra = {
            "example": {
                "data": {"key": "value"},
                "pretty_print": True,
                "include_metadata": True,
                "compression": False
            }
        }

class CSVExportSchema(BaseModel):
    """Schema for CSV export validation."""
    data: List[Dict[str, Any]] = Field(..., description="Data to export")
    headers: List[str] = Field(default_factory=list, description="CSV headers")
    delimiter: str = Field(default=",", description="CSV delimiter")
    include_headers: bool = Field(default=True, description="Include headers in CSV")
    encoding: str = Field(default="utf-8", description="File encoding")
    
    @validator('delimiter')
    def validate_delimiter(cls, v):
        """Validate CSV delimiter."""
        if len(v) != 1:
            raise ValueError("Delimiter must be a single character")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "data": [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}],
                "headers": ["name", "age"],
                "delimiter": ",",
                "include_headers": True,
                "encoding": "utf-8"
            }
        }

class XMLExportSchema(BaseModel):
    """Schema for XML export validation."""
    data: Dict[str, Any] = Field(..., description="Data to export")
    root_element: str = Field(default="data", description="Root XML element")
    pretty_print: bool = Field(default=True, description="Pretty print XML")
    encoding: str = Field(default="utf-8", description="File encoding")
    include_declaration: bool = Field(default=True, description="Include XML declaration")
    
    @validator('root_element')
    def validate_root_element(cls, v):
        """Validate root element name."""
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', v):
            raise ValueError("Invalid XML element name")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "data": {"user": {"name": "John", "age": 30}},
                "root_element": "users",
                "pretty_print": True,
                "encoding": "utf-8",
                "include_declaration": True
            }
        }

class HTMLExportSchema(BaseModel):
    """Schema for HTML export validation."""
    data: Dict[str, Any] = Field(..., description="Data to export")
    template: Optional[str] = Field(None, description="HTML template")
    title: str = Field(default="Export", description="HTML page title")
    include_css: bool = Field(default=True, description="Include CSS styling")
    include_js: bool = Field(default=False, description="Include JavaScript")
    encoding: str = Field(default="utf-8", description="File encoding")
    
    class Config:
        schema_extra = {
            "example": {
                "data": {"title": "Report", "content": "Hello World"},
                "template": "<html><body><h1>{title}</h1><p>{content}</p></body></html>",
                "title": "Security Report",
                "include_css": True,
                "include_js": False,
                "encoding": "utf-8"
            }
        } 