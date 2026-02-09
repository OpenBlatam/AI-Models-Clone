from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from ..types import (
from typing import Any, List, Dict, Optional
import logging
"""
Types Examples

Demonstrates how to use the Pydantic models and schemas.
"""


# Import types modules
    # Models
    BaseRequest, BaseResult, BaseConfig,
    ScanRequest, ScanResult, ScanConfig, ScanStatus, ScanType,
    Vulnerability, VulnerabilityLevel, VulnerabilityType, VulnerabilityReport,
    NetworkTarget, NetworkPort, NetworkService, NetworkHost, NetworkScan,
    AttackRequest, AttackResult, AttackType, AttackPayload, AttackSession,
    ReportRequest, ReportResult, ReportFormat, ReportLevel, ReportSection,
    EnumerationRequest, EnumerationResult, EnumerationType, ServiceInfo, PortInfo,
    CryptoRequest, CryptoResult, CryptoOperation, HashAlgorithm, EncryptionAlgorithm,
    NetworkRequest, NetworkResult, NetworkOperation,
    FileInfo, ProcessInfo, SystemInfo, LogEntry, ErrorInfo,
    
    # Schemas
    ScanRequestSchema, AttackRequestSchema, EnumerationRequestSchema,
    ReportRequestSchema, CryptoRequestSchema, NetworkRequestSchema,
    ScanResponseSchema, AttackResponseSchema, EnumerationResponseSchema,
    ReportResponseSchema, CryptoResponseSchema, NetworkResponseSchema,
    ScannerConfigSchema, AttackerConfigSchema, ReporterConfigSchema, UtilsConfigSchema,
    TargetValidationSchema, PortValidationSchema, CredentialValidationSchema, PayloadValidationSchema,
    JSONExportSchema, CSVExportSchema, XMLExportSchema, HTMLExportSchema
)

def demonstrate_base_models():
    """Demonstrate base models usage."""
    print("🔧 Base Models Examples")
    print("-" * 30)
    
    # Base Request
    base_request = BaseRequest(
        request_id="req_001",
        source="security_toolkit",
        metadata={"version": "1.0", "user": "admin"}
    )
    print(f"Base Request: {base_request.request_id}")
    print(f"Source: {base_request.source}")
    print(f"Metadata: {base_request.metadata}")
    
    # Base Result
    base_result = BaseResult(
        request_id="req_001",
        success=True,
        duration=1.5,
        metadata={"operations": 10, "errors": 0}
    )
    print(f"Base Result: {base_result.success}")
    print(f"Duration: {base_result.duration}s")
    print(f"Metadata: {base_result.metadata}")
    
    # Base Config
    base_config = BaseConfig(
        name="default_config",
        description="Default configuration for security operations",
        timeout=30.0,
        retries=3,
        max_concurrent=10
    )
    print(f"Config: {base_config.name}")
    print(f"Timeout: {base_config.timeout}s")
    print(f"Max Concurrent: {base_config.max_concurrent}")
    
    return {
        "base_request": base_request,
        "base_result": base_result,
        "base_config": base_config
    }

def demonstrate_scan_models():
    """Demonstrate scan models usage."""
    print("\n🔍 Scan Models Examples")
    print("-" * 30)
    
    # Scan Request
    scan_request = ScanRequest(
        request_id="scan_001",
        scan_type=ScanType.PORT_SCAN,
        targets=["192.168.1.1", "example.com", "10.0.0.1"],
        ports=[21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995],
        scan_config={
            "timeout": 30,
            "retries": 3,
            "service_detection": True,
            "os_detection": False
        }
    )
    print(f"Scan Request: {scan_request.scan_type}")
    print(f"Targets: {len(scan_request.targets)} targets")
    print(f"Ports: {len(scan_request.ports)} ports")
    
    # Scan Result
    scan_result = ScanResult(
        request_id="scan_001",
        success=True,
        duration=45.2,
        scan_type=ScanType.PORT_SCAN,
        targets_scanned=["192.168.1.1", "example.com"],
        results={
            "open_ports": [22, 80, 443],
            "services": {
                "22": "ssh",
                "80": "http",
                "443": "https"
            },
            "scan_time": 45.2
        },
        vulnerabilities_found=3,
        scan_duration=45.2,
        scan_status=ScanStatus.COMPLETED
    )
    print(f"Scan Result: {scan_result.scan_status}")
    print(f"Vulnerabilities: {scan_result.vulnerabilities_found}")
    print(f"Duration: {scan_result.scan_duration}s")
    
    # Scan Config
    scan_config = ScanConfig(
        name="comprehensive_scanner",
        description="Comprehensive network scanner",
        scan_type=ScanType.COMPREHENSIVE_SCAN,
        default_ports=[21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 5432, 6379],
        scan_speed="normal",
        service_detection=True,
        os_detection=True,
        script_scanning=True
    )
    print(f"Scanner Config: {scan_config.name}")
    print(f"Scan Speed: {scan_config.scan_speed}")
    print(f"OS Detection: {scan_config.os_detection}")
    
    return {
        "scan_request": scan_request,
        "scan_result": scan_result,
        "scan_config": scan_config
    }

def demonstrate_vulnerability_models():
    """Demonstrate vulnerability models usage."""
    print("\n🚨 Vulnerability Models Examples")
    print("-" * 30)
    
    # Create vulnerabilities
    vulnerabilities = [
        Vulnerability(
            id="VULN-001",
            title="SQL Injection in Login Form",
            description="SQL injection vulnerability found in the login form allowing unauthorized access",
            level=VulnerabilityLevel.HIGH,
            type=VulnerabilityType.SQL_INJECTION,
            cve_id="CVE-2023-1234",
            cvss_score=8.5,
            affected_target="192.168.1.1:80",
            port=80,
            service="http",
            evidence="' OR 1=1 --",
            recommendation="Use parameterized queries and input validation",
            references=["https://owasp.org/www-community/attacks/SQL_Injection"]
        ),
        Vulnerability(
            id="VULN-002",
            title="Cross-Site Scripting (XSS)",
            description="Reflected XSS vulnerability in search functionality",
            level=VulnerabilityLevel.MEDIUM,
            type=VulnerabilityType.XSS,
            cve_id="CVE-2023-5678",
            cvss_score=6.1,
            affected_target="192.168.1.1:80",
            port=80,
            service="http",
            evidence="<script>alert('XSS')</script>",
            recommendation="Implement proper input sanitization and output encoding",
            references=["https://owasp.org/www-community/attacks/xss/"]
        ),
        Vulnerability(
            id="VULN-003",
            title="Weak SSH Configuration",
            description="SSH service allows root login and uses weak encryption",
            level=VulnerabilityLevel.MEDIUM,
            type=VulnerabilityType.MISCONFIGURATION,
            cvss_score=5.5,
            affected_target="192.168.1.1:22",
            port=22,
            service="ssh",
            evidence="Root login enabled, weak cipher algorithms",
            recommendation="Disable root login and use strong encryption algorithms"
        )
    ]
    
    for vuln in vulnerabilities:
        print(f"Vulnerability: {vuln.title}")
        print(f"  Level: {vuln.level.value.upper()}")
        print(f"  Type: {vuln.type.value}")
        print(f"  CVSS: {vuln.cvss_score}")
        print(f"  Target: {vuln.affected_target}")
    
    # Vulnerability Report
    vuln_report = VulnerabilityReport(
        report_id="REPORT-001",
        scan_id="SCAN-001",
        target="192.168.1.1",
        vulnerabilities=vulnerabilities
    )
    
    print(f"\nVulnerability Report: {vuln_report.report_id}")
    print(f"Target: {vuln_report.target}")
    print(f"Total Vulnerabilities: {len(vuln_report.vulnerabilities)}")
    print(f"Summary: {vuln_report.summary}")
    print(f"Risk Score: {vuln_report.risk_score}")
    
    return {
        "vulnerabilities": vulnerabilities,
        "vulnerability_report": vuln_report
    }

def demonstrate_network_models():
    """Demonstrate network models usage."""
    print("\n🌐 Network Models Examples")
    print("-" * 30)
    
    # Network Target
    network_target = NetworkTarget(
        host="192.168.1.1",
        ip_address="192.168.1.1",
        hostname="router.local",
        is_alive=True,
        response_time=5.2,
        os_info={
            "os": "Linux",
            "version": "4.19.0",
            "arch": "x86_64"
        }
    )
    print(f"Network Target: {network_target.host}")
    print(f"Hostname: {network_target.hostname}")
    print(f"Alive: {network_target.is_alive}")
    print(f"Response Time: {network_target.response_time}ms")
    
    # Network Ports
    network_ports = [
        NetworkPort(
            port=22,
            protocol="tcp",
            state="open",
            service="ssh",
            version="OpenSSH 8.2p1",
            banner="SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.2"
        ),
        NetworkPort(
            port=80,
            protocol="tcp",
            state="open",
            service="http",
            version="Apache 2.4.41",
            banner="Apache/2.4.41 (Ubuntu)"
        ),
        NetworkPort(
            port=443,
            protocol="tcp",
            state="open",
            service="https",
            version="Apache 2.4.41",
            banner="Apache/2.4.41 (Ubuntu)"
        )
    ]
    
    for port in network_ports:
        print(f"Port {port.port}/{port.protocol}: {port.state} - {port.service}")
        if port.version:
            print(f"  Version: {port.version}")
    
    # Network Services
    network_services = [
        NetworkService(
            name="ssh",
            port=22,
            protocol="tcp",
            version="OpenSSH 8.2p1",
            product="OpenSSH",
            extra_info="Ubuntu-4ubuntu0.2",
            banner="SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.2"
        ),
        NetworkService(
            name="http",
            port=80,
            protocol="tcp",
            version="Apache 2.4.41",
            product="Apache",
            extra_info="(Ubuntu)",
            banner="Apache/2.4.41 (Ubuntu)"
        )
    ]
    
    for service in network_services:
        print(f"Service: {service.name} on port {service.port}")
        print(f"  Product: {service.product}")
        print(f"  Version: {service.version}")
    
    # Network Host
    network_host = NetworkHost(
        target=network_target,
        ports=network_ports,
        services=network_services,
        vulnerabilities=[],
        scan_time=15.3
    )
    
    print(f"\nNetwork Host: {network_host.target.host}")
    print(f"Open Ports: {len(network_host.ports)}")
    print(f"Services: {len(network_host.services)}")
    print(f"Scan Time: {network_host.scan_time}s")
    
    # Network Scan
    network_scan = NetworkScan(
        scan_id="NETWORK_SCAN_001",
        targets=[network_target],
        hosts=[network_host],
        scan_config=ScanConfig(
            name="network_scanner",
            scan_type=ScanType.NETWORK_SCAN
        ),
        start_time=datetime.now(),
        status=ScanStatus.COMPLETED,
        duration=45.2
    )
    
    print(f"\nNetwork Scan: {network_scan.scan_id}")
    print(f"Targets: {len(network_scan.targets)}")
    print(f"Hosts: {len(network_scan.hosts)}")
    print(f"Status: {network_scan.status}")
    print(f"Duration: {network_scan.duration}s")
    
    return {
        "network_target": network_target,
        "network_ports": network_ports,
        "network_services": network_services,
        "network_host": network_host,
        "network_scan": network_scan
    }

def demonstrate_attack_models():
    """Demonstrate attack models usage."""
    print("\n⚔️ Attack Models Examples")
    print("-" * 30)
    
    # Attack Payloads
    attack_payloads = [
        AttackPayload(
            payload_id="PAYLOAD-001",
            payload_type="sql_injection",
            content="' OR 1=1 --",
            encoding="utf-8",
            size=12,
            checksum="abc123def456",
            metadata={"category": "authentication_bypass", "risk": "high"}
        ),
        AttackPayload(
            payload_id="PAYLOAD-002",
            payload_type="xss",
            content="<script>alert('XSS')</script>",
            encoding="utf-8",
            size=32,
            checksum="def456ghi789",
            metadata={"category": "client_side", "risk": "medium"}
        ),
        AttackPayload(
            payload_id="PAYLOAD-003",
            payload_type="brute_force",
            content="admin:password123",
            encoding="utf-8",
            size=20,
            checksum="ghi789jkl012",
            metadata={"category": "credential_attack", "risk": "medium"}
        )
    ]
    
    for payload in attack_payloads:
        print(f"Payload: {payload.payload_type}")
        print(f"  Content: {payload.content}")
        print(f"  Size: {payload.size} bytes")
        print(f"  Risk: {payload.metadata.get('risk', 'unknown')}")
    
    # Attack Session
    attack_session = AttackSession(
        session_id="SESSION-001",
        attack_type=AttackType.BRUTE_FORCE,
        target="192.168.1.1:22",
        attempts=150,
        successful_attempts=1,
        payloads_used=attack_payloads[:1]
    )
    
    print(f"\nAttack Session: {attack_session.session_id}")
    print(f"Type: {attack_session.attack_type}")
    print(f"Target: {attack_session.target}")
    print(f"Attempts: {attack_session.attempts}")
    print(f"Successful: {attack_session.successful_attempts}")
    
    # Attack Request
    attack_request = AttackRequest(
        request_id="ATTACK-001",
        attack_type=AttackType.BRUTE_FORCE,
        target="192.168.1.1:22",
        payload={
            "username": "admin",
            "password_list": ["admin", "password", "123456", "admin123"]
        },
        credentials={
            "username": "admin",
            "password": "admin123"
        },
        attack_config={
            "timeout": 10,
            "max_attempts": 100,
            "rate_limit": 5
        }
    )
    
    print(f"\nAttack Request: {attack_request.request_id}")
    print(f"Type: {attack_request.attack_type}")
    print(f"Target: {attack_request.target}")
    
    # Attack Result
    attack_result = AttackResult(
        request_id="ATTACK-001",
        success=True,
        duration=120.5,
        attack_type=AttackType.BRUTE_FORCE,
        target="192.168.1.1:22",
        attack_success=True,
        payload_used=attack_payloads[2],
        session_info=attack_session,
        discovered_vulnerabilities=[
            Vulnerability(
                id="VULN-ATTACK-001",
                title="Weak SSH Credentials",
                description="SSH service accessible with weak credentials",
                level=VulnerabilityLevel.HIGH,
                type=VulnerabilityType.DEFAULT_CREDENTIALS,
                affected_target="192.168.1.1:22",
                port=22,
                service="ssh",
                evidence="admin:admin123",
                recommendation="Change default credentials and implement strong password policy"
            )
        ],
        attack_data={
            "attempts": 150,
            "successful_credentials": {"username": "admin", "password": "admin123"},
            "time_taken": 120.5,
            "rate": "1.25 attempts/second"
        }
    )
    
    print(f"\nAttack Result: {attack_result.attack_success}")
    print(f"Duration: {attack_result.duration}s")
    print(f"Vulnerabilities Found: {len(attack_result.discovered_vulnerabilities)}")
    
    return {
        "attack_payloads": attack_payloads,
        "attack_session": attack_session,
        "attack_request": attack_request,
        "attack_result": attack_result
    }

def demonstrate_report_models():
    """Demonstrate report models usage."""
    print("\n📋 Report Models Examples")
    print("-" * 30)
    
    # Report Request
    report_request = ReportRequest(
        request_id="REPORT-001",
        report_format=ReportFormat.HTML,
        report_level=ReportLevel.DETAILED,
        sections=[
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.METHODOLOGY,
            ReportSection.FINDINGS,
            ReportSection.VULNERABILITIES,
            ReportSection.RECOMMENDATIONS
        ],
        scan_results=["SCAN-001", "SCAN-002"],
        attack_results=["ATTACK-001"],
        custom_data={
            "client_name": "Example Corporation",
            "project_name": "Security Assessment 2023",
            "assessment_date": "2023-12-01",
            "assessor": "Security Team"
        },
        template="corporate_security_report"
    )
    
    print(f"Report Request: {report_request.request_id}")
    print(f"Format: {report_request.report_format}")
    print(f"Level: {report_request.report_level}")
    print(f"Sections: {len(report_request.sections)}")
    print(f"Client: {report_request.custom_data.get('client_name')}")
    
    # Report Result
    report_result = ReportResult(
        request_id="REPORT-001",
        success=True,
        duration=15.3,
        report_format=ReportFormat.HTML,
        report_level=ReportLevel.DETAILED,
        report_content="""
        <html>
        <head><title>Security Assessment Report</title></head>
        <body>
            <h1>Executive Summary</h1>
            <p>Security assessment completed for Example Corporation...</p>
            <h2>Findings</h2>
            <ul>
                <li>3 High severity vulnerabilities</li>
                <li>5 Medium severity vulnerabilities</li>
                <li>2 Low severity vulnerabilities</li>
            </ul>
        </body>
        </html>
        """,
        report_size=15420,
        sections_included=[
            ReportSection.EXECUTIVE_SUMMARY,
            ReportSection.FINDINGS,
            ReportSection.RECOMMENDATIONS
        ]
    )
    
    print(f"\nReport Result: {report_result.success}")
    print(f"Format: {report_result.report_format}")
    print(f"Size: {report_result.report_size} bytes")
    print(f"Sections: {len(report_result.sections_included)}")
    print(f"Generation Time: {report_result.duration}s")
    
    return {
        "report_request": report_request,
        "report_result": report_result
    }

def demonstrate_enumeration_models():
    """Demonstrate enumeration models usage."""
    print("\n🔍 Enumeration Models Examples")
    print("-" * 30)
    
    # Service Information
    services = [
        ServiceInfo(
            service_name="ssh",
            port=22,
            protocol="tcp",
            version="OpenSSH 8.2p1",
            banner="SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.2",
            fingerprint="SSH-2.0-OpenSSH_8.2p1"
        ),
        ServiceInfo(
            service_name="http",
            port=80,
            protocol="tcp",
            version="Apache 2.4.41",
            banner="Apache/2.4.41 (Ubuntu)",
            fingerprint="Apache/2.4.41"
        ),
        ServiceInfo(
            service_name="https",
            port=443,
            protocol="tcp",
            version="Apache 2.4.41",
            banner="Apache/2.4.41 (Ubuntu)",
            fingerprint="Apache/2.4.41"
        )
    ]
    
    for service in services:
        print(f"Service: {service.service_name} on port {service.port}")
        print(f"  Version: {service.version}")
        print(f"  Banner: {service.banner}")
    
    # Port Information
    port_infos = [
        PortInfo(
            port=22,
            protocol="tcp",
            state="open",
            service=services[0]
        ),
        PortInfo(
            port=80,
            protocol="tcp",
            state="open",
            service=services[1]
        ),
        PortInfo(
            port=443,
            protocol="tcp",
            state="open",
            service=services[2]
        ),
        PortInfo(
            port=25,
            protocol="tcp",
            state="closed"
        )
    ]
    
    for port_info in port_infos:
        status = f"{port_info.state} - {port_info.service.service_name if port_info.service else 'unknown'}"
        print(f"Port {port_info.port}/{port_info.protocol}: {status}")
    
    # Enumeration Request
    enum_request = EnumerationRequest(
        request_id="ENUM-001",
        enumeration_type=EnumerationType.PORT_ENUMERATION,
        target="192.168.1.1",
        ports=[21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995],
        wordlist="/usr/share/wordlists/common.txt",
        enumeration_config={
            "timeout": 5,
            "service_detection": True,
            "version_detection": True,
            "script_scanning": False
        }
    )
    
    print(f"\nEnumeration Request: {enum_request.request_id}")
    print(f"Type: {enum_request.enumeration_type}")
    print(f"Target: {enum_request.target}")
    print(f"Ports: {len(enum_request.ports)}")
    
    # Enumeration Result
    enum_result = EnumerationResult(
        request_id="ENUM-001",
        success=True,
        duration=30.2,
        enumeration_type=EnumerationType.PORT_ENUMERATION,
        target="192.168.1.1",
        discovered_items=["ssh", "http", "https"],
        ports_found=port_infos[:3],
        services_found=services,
        enumeration_data={
            "scan_time": 30.2,
            "open_ports": 3,
            "closed_ports": 8,
            "filtered_ports": 0
        }
    )
    
    print(f"\nEnumeration Result: {enum_result.success}")
    print(f"Duration: {enum_result.duration}s")
    print(f"Discovered Items: {len(enum_result.discovered_items)}")
    print(f"Open Ports: {enum_result.enumeration_data.get('open_ports')}")
    
    return {
        "services": services,
        "port_infos": port_infos,
        "enum_request": enum_request,
        "enum_result": enum_result
    }

def demonstrate_crypto_models():
    """Demonstrate crypto models usage."""
    print("\n🔐 Crypto Models Examples")
    print("-" * 30)
    
    # Crypto Request
    crypto_request = CryptoRequest(
        request_id="CRYPTO-001",
        operation=CryptoOperation.HASH,
        data="Hello, World!",
        algorithm=HashAlgorithm.SHA256
    )
    
    print(f"Crypto Request: {crypto_request.request_id}")
    print(f"Operation: {crypto_request.operation}")
    print(f"Algorithm: {crypto_request.algorithm}")
    print(f"Data: {crypto_request.data}")
    
    # Crypto Result
    crypto_result = CryptoResult(
        request_id="CRYPTO-001",
        success=True,
        duration=0.001,
        operation=CryptoOperation.HASH,
        algorithm=HashAlgorithm.SHA256,
        input_data="Hello, World!",
        output_data="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
        operation_duration=0.001
    )
    
    print(f"\nCrypto Result: {crypto_result.success}")
    print(f"Input: {crypto_result.input_data}")
    print(f"Output: {crypto_result.output_data[:16]}...")
    print(f"Duration: {crypto_result.operation_duration}s")
    
    # Encryption Request
    encrypt_request = CryptoRequest(
        request_id="CRYPTO-002",
        operation=CryptoOperation.ENCRYPT,
        data="Secret message",
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        key="mysecretkey1234567890123456789012"
    )
    
    print(f"\nEncryption Request: {encrypt_request.request_id}")
    print(f"Operation: {encrypt_request.operation}")
    print(f"Algorithm: {encrypt_request.algorithm}")
    
    return {
        "crypto_request": crypto_request,
        "crypto_result": crypto_result,
        "encrypt_request": encrypt_request
    }

def demonstrate_utility_models():
    """Demonstrate utility models usage."""
    print("\n🛠️ Utility Models Examples")
    print("-" * 30)
    
    # File Information
    file_info = FileInfo(
        filename="security_report.pdf",
        filepath="/reports/security_report.pdf",
        size=2048576,
        checksum="sha256:abc123def456ghi789",
        mime_type="application/pdf",
        created_at=datetime.now(),
        modified_at=datetime.now()
    )
    
    print(f"File: {file_info.filename}")
    print(f"Path: {file_info.filepath}")
    print(f"Size: {file_info.size} bytes")
    print(f"Type: {file_info.mime_type}")
    print(f"Checksum: {file_info.checksum}")
    
    # Process Information
    process_info = ProcessInfo(
        pid=1234,
        name="nmap",
        command="nmap -sS -p 1-1000 192.168.1.1",
        user="security",
        memory_usage=52428800,
        cpu_usage=15.5,
        start_time=datetime.now()
    )
    
    print(f"\nProcess: {process_info.name}")
    print(f"PID: {process_info.pid}")
    print(f"Command: {process_info.command}")
    print(f"Memory: {process_info.memory_usage} bytes")
    print(f"CPU: {process_info.cpu_usage}%")
    
    # System Information
    system_info = SystemInfo(
        hostname="security-scanner-01",
        os_name="Ubuntu",
        os_version="20.04.3 LTS",
        architecture="x86_64",
        cpu_count=8,
        memory_total=17179869184,
        uptime=86400.0,
        boot_time=datetime.now()
    )
    
    print(f"\nSystem: {system_info.hostname}")
    print(f"OS: {system_info.os_name} {system_info.os_version}")
    print(f"Architecture: {system_info.architecture}")
    print(f"CPU Cores: {system_info.cpu_count}")
    print(f"Memory: {system_info.memory_total} bytes")
    print(f"Uptime: {system_info.uptime} seconds")
    
    # Log Entry
    log_entry = LogEntry(
        level="INFO",
        message="Port scan completed successfully",
        source="nmap_scanner",
        module="scanners",
        function="port_scan",
        line_number=42,
        context={"target": "192.168.1.1", "ports": "1-1000"}
    )
    
    print(f"\nLog Entry: {log_entry.level}")
    print(f"Message: {log_entry.message}")
    print(f"Source: {log_entry.source}")
    print(f"Module: {log_entry.module}")
    print(f"Function: {log_entry.function}")
    print(f"Line: {log_entry.line_number}")
    
    # Error Information
    error_info = ErrorInfo(
        error_id="ERROR-001",
        error_type="ConnectionError",
        error_message="Failed to connect to target host",
        error_code="CONN_REFUSED",
        severity="high",
        context={"target": "192.168.1.1", "port": 22}
    )
    
    print(f"\nError: {error_info.error_type}")
    print(f"Message: {error_info.error_message}")
    print(f"Code: {error_info.error_code}")
    print(f"Severity: {error_info.severity}")
    
    return {
        "file_info": file_info,
        "process_info": process_info,
        "system_info": system_info,
        "log_entry": log_entry,
        "error_info": error_info
    }

def demonstrate_schemas():
    """Demonstrate schema validation."""
    print("\n📋 Schema Validation Examples")
    print("-" * 30)
    
    # Scan Request Schema
    scan_schema = ScanRequestSchema(
        scan_type=ScanType.PORT_SCAN,
        targets=["192.168.1.1", "example.com"],
        ports=[80, 443, 22, 21],
        scan_config={"timeout": 30, "retries": 3}
    )
    print(f"Scan Schema: {scan_schema.scan_type}")
    print(f"Targets: {len(scan_schema.targets)}")
    
    # Attack Request Schema
    attack_schema = AttackRequestSchema(
        attack_type=AttackType.BRUTE_FORCE,
        target="192.168.1.1:22",
        credentials={"username": "admin", "password": "password123"},
        attack_config={"timeout": 10, "max_attempts": 100}
    )
    print(f"\nAttack Schema: {attack_schema.attack_type}")
    print(f"Target: {attack_schema.target}")
    
    # Target Validation Schema
    target_schema = TargetValidationSchema(
        target="192.168.1.1",
        target_type="ip"
    )
    print(f"\nTarget Schema: {target_schema.target}")
    print(f"Type: {target_schema.target_type}")
    
    # Port Validation Schema
    port_schema = PortValidationSchema(
        port=80,
        protocol="tcp"
    )
    print(f"\nPort Schema: {port_schema.port}/{port_schema.protocol}")
    
    # Credential Validation Schema
    cred_schema = CredentialValidationSchema(
        username="admin",
        password="password123",
        domain="example.com"
    )
    print(f"\nCredential Schema: {cred_schema.username}@{cred_schema.domain}")
    
    # Export Schemas
    json_schema = JSONExportSchema(
        data={"key": "value", "number": 42},
        pretty_print=True,
        include_metadata=True
    )
    print(f"\nJSON Export Schema: {json_schema.pretty_print}")
    
    csv_schema = CSVExportSchema(
        data=[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}],
        headers=["name", "age"],
        delimiter=",",
        include_headers=True
    )
    print(f"CSV Export Schema: {len(csv_schema.data)} rows")
    
    return {
        "scan_schema": scan_schema,
        "attack_schema": attack_schema,
        "target_schema": target_schema,
        "port_schema": port_schema,
        "cred_schema": cred_schema,
        "json_schema": json_schema,
        "csv_schema": csv_schema
    }

def demonstrate_serialization():
    """Demonstrate model serialization."""
    print("\n🔄 Serialization Examples")
    print("-" * 30)
    
    # Create a complex model
    scan_request = ScanRequest(
        request_id="SERIAL-001",
        scan_type=ScanType.PORT_SCAN,
        targets=["192.168.1.1", "example.com"],
        ports=[80, 443, 22],
        scan_config={"timeout": 30, "retries": 3}
    )
    
    # Serialize to dictionary
    scan_dict = scan_request.dict()
    print(f"Dictionary Keys: {list(scan_dict.keys())}")
    print(f"Scan Type: {scan_dict['scan_type']}")
    print(f"Targets: {scan_dict['targets']}")
    
    # Serialize to JSON
    scan_json = scan_request.json()
    print(f"\nJSON Length: {len(scan_json)} characters")
    print(f"JSON Preview: {scan_json[:100]}...")
    
    # Deserialize from dictionary
    scan_from_dict = ScanRequest(**scan_dict)
    print(f"\nDeserialized Request ID: {scan_from_dict.request_id}")
    print(f"Deserialized Scan Type: {scan_from_dict.scan_type}")
    
    # Create vulnerability for complex serialization
    vulnerability = Vulnerability(
        id="VULN-SERIAL-001",
        title="Test Vulnerability",
        description="Test vulnerability for serialization",
        level=VulnerabilityLevel.HIGH,
        type=VulnerabilityType.SQL_INJECTION,
        affected_target="192.168.1.1:80",
        port=80,
        service="http"
    )
    
    # Serialize vulnerability
    vuln_dict = vulnerability.dict()
    vuln_json = vulnerability.json()
    
    print(f"\nVulnerability Dictionary: {vuln_dict['id']}")
    print(f"Vulnerability JSON Length: {len(vuln_json)}")
    
    return {
        "scan_dict": scan_dict,
        "scan_json": scan_json,
        "scan_from_dict": scan_from_dict,
        "vuln_dict": vuln_dict,
        "vuln_json": vuln_json
    }

def demonstrate_validation():
    """Demonstrate model validation."""
    print("\n✅ Validation Examples")
    print("-" * 30)
    
    # Valid models
    print("Valid Models:")
    
    valid_scan = ScanRequest(
        request_id="VALID-001",
        scan_type=ScanType.PORT_SCAN,
        targets=["192.168.1.1"]
    )
    print(f"✓ Valid Scan Request: {valid_scan.request_id}")
    
    valid_vuln = Vulnerability(
        id="VULN-VALID-001",
        title="Valid Vulnerability",
        description="This is a valid vulnerability",
        level=VulnerabilityLevel.MEDIUM,
        type=VulnerabilityType.XSS,
        affected_target="192.168.1.1:80"
    )
    print(f"✓ Valid Vulnerability: {valid_vuln.id}")
    
    # Invalid models (should raise exceptions)
    print("\nInvalid Models (Validation Errors):")
    
    try:
        invalid_scan = ScanRequest(
            request_id="INVALID-001",
            scan_type="invalid_type",  # Should be ScanType enum
            targets=["192.168.1.1"]
        )
    except ValueError as e:
        print(f"✗ Invalid Scan Type: {e}")
    
    try:
        invalid_vuln = Vulnerability(
            id="VULN-INVALID-001",
            title="",  # Empty title should fail
            description="Invalid vulnerability",
            level=VulnerabilityLevel.MEDIUM,
            type=VulnerabilityType.XSS,
            affected_target="192.168.1.1:80"
        )
    except ValueError as e:
        print(f"✗ Invalid Vulnerability: {e}")
    
    try:
        invalid_port = NetworkPort(
            port=70000,  # Invalid port number
            protocol="tcp",
            state="open"
        )
    except ValueError as e:
        print(f"✗ Invalid Port: {e}")
    
    return {
        "valid_scan": valid_scan,
        "valid_vuln": valid_vuln
    }

def main():
    """Main function to run all types examples."""
    print("🔧 Cybersecurity Types Toolkit Examples")
    print("=" * 60)
    print("📋 Pydantic models and schemas demonstration")
    print("=" * 60)
    
    try:
        # Run all demonstrations
        results = {}
        
        print("\n🔧 Base Models")
        results["base"] = demonstrate_base_models()
        
        print("\n🔍 Scan Models")
        results["scan"] = demonstrate_scan_models()
        
        print("\n🚨 Vulnerability Models")
        results["vulnerability"] = demonstrate_vulnerability_models()
        
        print("\n🌐 Network Models")
        results["network"] = demonstrate_network_models()
        
        print("\n⚔️ Attack Models")
        results["attack"] = demonstrate_attack_models()
        
        print("\n📋 Report Models")
        results["report"] = demonstrate_report_models()
        
        print("\n🔍 Enumeration Models")
        results["enumeration"] = demonstrate_enumeration_models()
        
        print("\n🔐 Crypto Models")
        results["crypto"] = demonstrate_crypto_models()
        
        print("\n🛠️ Utility Models")
        results["utility"] = demonstrate_utility_models()
        
        print("\n📋 Schema Validation")
        results["schemas"] = demonstrate_schemas()
        
        print("\n🔄 Serialization")
        results["serialization"] = demonstrate_serialization()
        
        print("\n✅ Validation")
        results["validation"] = demonstrate_validation()
        
        print("\n" + "=" * 60)
        print("✅ All types examples completed successfully!")
        
        # Summary
        print("\n📊 Types Summary:")
        print(f"   Base Models: {len(results['base'])} examples")
        print(f"   Scan Models: {len(results['scan'])} examples")
        print(f"   Vulnerability Models: {len(results['vulnerability'])} examples")
        print(f"   Network Models: {len(results['network'])} examples")
        print(f"   Attack Models: {len(results['attack'])} examples")
        print(f"   Report Models: {len(results['report'])} examples")
        print(f"   Enumeration Models: {len(results['enumeration'])} examples")
        print(f"   Crypto Models: {len(results['crypto'])} examples")
        print(f"   Utility Models: {len(results['utility'])} examples")
        print(f"   Schema Validation: {len(results['schemas'])} examples")
        print(f"   Serialization: {len(results['serialization'])} examples")
        print(f"   Validation: {len(results['validation'])} examples")
        
        # Model types summary
        print("\n🏗️ Model Types Demonstrated:")
        print("   • Base Models (Request, Result, Config)")
        print("   • Scan Models (Request, Result, Config, Status, Type)")
        print("   • Vulnerability Models (Vulnerability, Report, Level, Type)")
        print("   • Network Models (Target, Port, Service, Host, Scan)")
        print("   • Attack Models (Request, Result, Type, Payload, Session)")
        print("   • Report Models (Request, Result, Format, Level, Section)")
        print("   • Enumeration Models (Request, Result, Type, Service, Port)")
        print("   • Crypto Models (Request, Result, Operation, Algorithm)")
        print("   • Network Models (Request, Result, Operation)")
        print("   • Utility Models (File, Process, System, Log, Error)")
        
        # Schema types summary
        print("\n📋 Schema Types Demonstrated:")
        print("   • Request Schemas (Scan, Attack, Enumeration, Report, Crypto, Network)")
        print("   • Response Schemas (Scan, Attack, Enumeration, Report, Crypto, Network)")
        print("   • Config Schemas (Scanner, Attacker, Reporter, Utils)")
        print("   • Validation Schemas (Target, Port, Credential, Payload)")
        print("   • Export Schemas (JSON, CSV, XML, HTML)")
        
        # Features summary
        print("\n✨ Features Demonstrated:")
        print("   • Pydantic model validation")
        print("   • Enum type safety")
        print("   • Custom validators")
        print("   • Nested model relationships")
        print("   • Serialization (dict, JSON)")
        print("   • Deserialization")
        print("   • Schema validation")
        print("   • Error handling")
        print("   • Type hints and documentation")
        print("   • Configurable models")
        
        # Use cases summary
        print("\n🎯 Use Cases Demonstrated:")
        print("   • Security scan configuration and results")
        print("   • Vulnerability tracking and reporting")
        print("   • Network reconnaissance data structures")
        print("   • Attack simulation and results")
        print("   • Report generation and formatting")
        print("   • Service enumeration and discovery")
        print("   • Cryptographic operation modeling")
        print("   • System and process information")
        print("   • Logging and error tracking")
        print("   • Data validation and serialization")
        
    except Exception as e:
        print(f"❌ Error running types examples: {e}")
        raise

match __name__:
    case "__main__":
    main() 