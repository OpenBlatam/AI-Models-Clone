"""
Tests for Types Module

Tests Pydantic models and schemas functionality.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from ..types import (
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

class TestBaseModels:
    """Test suite for base models."""
    
    def test_base_request_creation(self):
        """Test BaseRequest creation."""
        request = BaseRequest(
            request_id="test_001",
            source="test_client"
        )
        
        assert request.request_id == "test_001"
        assert request.source == "test_client"
        assert request.timestamp is not None
        assert isinstance(request.metadata, dict)
    
    def test_base_result_creation(self):
        """Test BaseResult creation."""
        result = BaseResult(
            request_id="test_001",
            success=True,
            duration=1.5
        )
        
        assert result.request_id == "test_001"
        assert result.success is True
        assert result.duration == 1.5
        assert result.timestamp is not None
    
    def test_base_config_creation(self):
        """Test BaseConfig creation."""
        config = BaseConfig(
            name="test_config",
            description="Test configuration",
            timeout=60.0,
            retries=5
        )
        
        assert config.name == "test_config"
        assert config.description == "Test configuration"
        assert config.timeout == 60.0
        assert config.retries == 5
        assert config.enabled is True

class TestScanModels:
    """Test suite for scan models."""
    
    def test_scan_request_creation(self):
        """Test ScanRequest creation."""
        request = ScanRequest(
            request_id="scan_001",
            scan_type=ScanType.PORT_SCAN,
            targets=["192.168.1.1", "example.com"],
            ports=[80, 443, 22]
        )
        
        assert request.scan_type == ScanType.PORT_SCAN
        assert request.targets == ["192.168.1.1", "example.com"]
        assert request.ports == [80, 443, 22]
    
    def test_scan_request_validation(self):
        """Test ScanRequest validation."""
        # Valid request
        request = ScanRequest(
            request_id="scan_001",
            scan_type=ScanType.PORT_SCAN,
            targets=["192.168.1.1"]
        )
        assert request is not None
        
        # Invalid target
        with pytest.raises(ValueError, match="Invalid target format"):
            ScanRequest(
                request_id="scan_001",
                scan_type=ScanType.PORT_SCAN,
                targets=["invalid@target"]
            )
        
        # Invalid port
        with pytest.raises(ValueError, match="Invalid port number"):
            ScanRequest(
                request_id="scan_001",
                scan_type=ScanType.PORT_SCAN,
                targets=["192.168.1.1"],
                ports=[70000]
            )
    
    def test_scan_result_creation(self):
        """Test ScanResult creation."""
        result = ScanResult(
            request_id="scan_001",
            success=True,
            duration=45.2,
            scan_type=ScanType.PORT_SCAN,
            targets_scanned=["192.168.1.1"],
            results={"open_ports": [80, 443]},
            vulnerabilities_found=2,
            scan_duration=45.2,
            scan_status=ScanStatus.COMPLETED
        )
        
        assert result.scan_type == ScanType.PORT_SCAN
        assert result.targets_scanned == ["192.168.1.1"]
        assert result.vulnerabilities_found == 2
        assert result.scan_status == ScanStatus.COMPLETED
    
    def test_scan_config_creation(self):
        """Test ScanConfig creation."""
        config = ScanConfig(
            name="port_scanner",
            scan_type=ScanType.PORT_SCAN,
            default_ports=[80, 443, 22],
            scan_speed="fast",
            service_detection=True
        )
        
        assert config.scan_type == ScanType.PORT_SCAN
        assert config.default_ports == [80, 443, 22]
        assert config.scan_speed == "fast"
        assert config.service_detection is True

class TestVulnerabilityModels:
    """Test suite for vulnerability models."""
    
    def test_vulnerability_creation(self):
        """Test Vulnerability creation."""
        vuln = Vulnerability(
            id="VULN-001",
            title="SQL Injection Vulnerability",
            description="SQL injection found in login form",
            level=VulnerabilityLevel.HIGH,
            type=VulnerabilityType.SQL_INJECTION,
            cve_id="CVE-2023-1234",
            cvss_score=8.5,
            affected_target="192.168.1.1:80",
            port=80,
            service="http",
            evidence="' OR 1=1 --",
            recommendation="Use parameterized queries"
        )
        
        assert vuln.id == "VULN-001"
        assert vuln.title == "SQL Injection Vulnerability"
        assert vuln.level == VulnerabilityLevel.HIGH
        assert vuln.type == VulnerabilityType.SQL_INJECTION
        assert vuln.cvss_score == 8.5
    
    def test_vulnerability_report_creation(self):
        """Test VulnerabilityReport creation."""
        vuln1 = Vulnerability(
            id="VULN-001",
            title="SQL Injection",
            description="SQL injection vulnerability",
            level=VulnerabilityLevel.HIGH,
            type=VulnerabilityType.SQL_INJECTION,
            affected_target="192.168.1.1"
        )
        
        vuln2 = Vulnerability(
            id="VULN-002",
            title="XSS Vulnerability",
            description="Cross-site scripting vulnerability",
            level=VulnerabilityLevel.MEDIUM,
            type=VulnerabilityType.XSS,
            affected_target="192.168.1.1"
        )
        
        report = VulnerabilityReport(
            report_id="REPORT-001",
            scan_id="SCAN-001",
            target="192.168.1.1",
            vulnerabilities=[vuln1, vuln2]
        )
        
        assert report.report_id == "REPORT-001"
        assert len(report.vulnerabilities) == 2
        assert report.summary["high"] == 1
        assert report.summary["medium"] == 1

class TestNetworkModels:
    """Test suite for network models."""
    
    def test_network_target_creation(self):
        """Test NetworkTarget creation."""
        target = NetworkTarget(
            host="192.168.1.1",
            ip_address="192.168.1.1",
            is_alive=True,
            response_time=5.2
        )
        
        assert target.host == "192.168.1.1"
        assert target.ip_address == "192.168.1.1"
        assert target.is_alive is True
        assert target.response_time == 5.2
    
    def test_network_port_creation(self):
        """Test NetworkPort creation."""
        port = NetworkPort(
            port=80,
            protocol="tcp",
            state="open",
            service="http",
            version="Apache 2.4.41"
        )
        
        assert port.port == 80
        assert port.protocol == "tcp"
        assert port.state == "open"
        assert port.service == "http"
    
    def test_network_service_creation(self):
        """Test NetworkService creation."""
        service = NetworkService(
            name="http",
            port=80,
            protocol="tcp",
            version="Apache 2.4.41",
            product="Apache",
            banner="Apache/2.4.41 (Ubuntu)"
        )
        
        assert service.name == "http"
        assert service.port == 80
        assert service.protocol == "tcp"
        assert service.product == "Apache"
    
    def test_network_host_creation(self):
        """Test NetworkHost creation."""
        target = NetworkTarget(host="192.168.1.1", is_alive=True)
        port = NetworkPort(port=80, state="open", service="http")
        service = NetworkService(name="http", port=80)
        
        host = NetworkHost(
            target=target,
            ports=[port],
            services=[service],
            scan_time=10.5
        )
        
        assert host.target.host == "192.168.1.1"
        assert len(host.ports) == 1
        assert len(host.services) == 1
        assert host.scan_time == 10.5

class TestAttackModels:
    """Test suite for attack models."""
    
    def test_attack_request_creation(self):
        """Test AttackRequest creation."""
        request = AttackRequest(
            request_id="attack_001",
            attack_type=AttackType.BRUTE_FORCE,
            target="192.168.1.1:22",
            payload={"username": "admin", "password": "password123"},
            credentials={"username": "admin", "password": "password123"}
        )
        
        assert request.attack_type == AttackType.BRUTE_FORCE
        assert request.target == "192.168.1.1:22"
        assert request.payload is not None
        assert request.credentials is not None
    
    def test_attack_payload_creation(self):
        """Test AttackPayload creation."""
        payload = AttackPayload(
            payload_id="PAYLOAD-001",
            payload_type="sql_injection",
            content="' OR 1=1 --",
            encoding="utf-8",
            size=12
        )
        
        assert payload.payload_id == "PAYLOAD-001"
        assert payload.payload_type == "sql_injection"
        assert payload.content == "' OR 1=1 --"
        assert payload.size == 12
    
    def test_attack_session_creation(self):
        """Test AttackSession creation."""
        session = AttackSession(
            session_id="SESSION-001",
            attack_type=AttackType.BRUTE_FORCE,
            target="192.168.1.1:22",
            attempts=50,
            successful_attempts=1
        )
        
        assert session.session_id == "SESSION-001"
        assert session.attack_type == AttackType.BRUTE_FORCE
        assert session.target == "192.168.1.1:22"
        assert session.attempts == 50
        assert session.successful_attempts == 1

class TestReportModels:
    """Test suite for report models."""
    
    def test_report_request_creation(self):
        """Test ReportRequest creation."""
        request = ReportRequest(
            request_id="report_001",
            report_format=ReportFormat.HTML,
            report_level=ReportLevel.DETAILED,
            sections=[ReportSection.EXECUTIVE_SUMMARY, ReportSection.FINDINGS],
            scan_results=["scan_001", "scan_002"]
        )
        
        assert request.report_format == ReportFormat.HTML
        assert request.report_level == ReportLevel.DETAILED
        assert len(request.sections) == 2
        assert len(request.scan_results) == 2
    
    def test_report_result_creation(self):
        """Test ReportResult creation."""
        result = ReportResult(
            request_id="report_001",
            success=True,
            duration=5.3,
            report_format=ReportFormat.HTML,
            report_level=ReportLevel.DETAILED,
            report_content="<html>...</html>",
            report_size=15420,
            sections_included=[ReportSection.EXECUTIVE_SUMMARY, ReportSection.FINDINGS]
        )
        
        assert result.report_format == ReportFormat.HTML
        assert result.report_level == ReportLevel.DETAILED
        assert result.report_content == "<html>...</html>"
        assert result.report_size == 15420

class TestEnumerationModels:
    """Test suite for enumeration models."""
    
    def test_enumeration_request_creation(self):
        """Test EnumerationRequest creation."""
        request = EnumerationRequest(
            request_id="enum_001",
            enumeration_type=EnumerationType.PORT_ENUMERATION,
            target="192.168.1.1",
            ports=[21, 22, 23, 25, 80, 443]
        )
        
        assert request.enumeration_type == EnumerationType.PORT_ENUMERATION
        assert request.target == "192.168.1.1"
        assert request.ports == [21, 22, 23, 25, 80, 443]
    
    def test_service_info_creation(self):
        """Test ServiceInfo creation."""
        service = ServiceInfo(
            service_name="ssh",
            port=22,
            protocol="tcp",
            version="OpenSSH 8.2p1",
            banner="SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.2"
        )
        
        assert service.service_name == "ssh"
        assert service.port == 22
        assert service.protocol == "tcp"
        assert service.version == "OpenSSH 8.2p1"
    
    def test_port_info_creation(self):
        """Test PortInfo creation."""
        service = ServiceInfo(service_name="http", port=80)
        port_info = PortInfo(
            port=80,
            protocol="tcp",
            state="open",
            service=service
        )
        
        assert port_info.port == 80
        assert port_info.protocol == "tcp"
        assert port_info.state == "open"
        assert port_info.service.service_name == "http"

class TestCryptoModels:
    """Test suite for crypto models."""
    
    def test_crypto_request_creation(self):
        """Test CryptoRequest creation."""
        request = CryptoRequest(
            request_id="crypto_001",
            operation=CryptoOperation.HASH,
            data="Hello, World!",
            algorithm=HashAlgorithm.SHA256
        )
        
        assert request.operation == CryptoOperation.HASH
        assert request.data == "Hello, World!"
        assert request.algorithm == HashAlgorithm.SHA256
    
    def test_crypto_result_creation(self):
        """Test CryptoResult creation."""
        result = CryptoResult(
            request_id="crypto_001",
            success=True,
            duration=0.001,
            operation=CryptoOperation.HASH,
            algorithm=HashAlgorithm.SHA256,
            input_data="Hello, World!",
            output_data="a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e",
            operation_duration=0.001
        )
        
        assert result.operation == CryptoOperation.HASH
        assert result.algorithm == HashAlgorithm.SHA256
        assert result.input_data == "Hello, World!"
        assert len(result.output_data) > 0

class TestNetworkModels:
    """Test suite for network models."""
    
    def test_network_request_creation(self):
        """Test NetworkRequest creation."""
        request = NetworkRequest(
            request_id="network_001",
            operation=NetworkOperation.DNS_LOOKUP,
            target="google.com",
            timeout=10.0,
            retries=3
        )
        
        assert request.operation == NetworkOperation.DNS_LOOKUP
        assert request.target == "google.com"
        assert request.timeout == 10.0
        assert request.retries == 3
    
    def test_network_result_creation(self):
        """Test NetworkResult creation."""
        result = NetworkResult(
            request_id="network_001",
            success=True,
            duration=0.05,
            operation=NetworkOperation.DNS_LOOKUP,
            target="google.com",
            result_data={"domain": "google.com", "records": {"A": ["142.250.190.78"]}},
            operation_duration=0.05
        )
        
        assert result.operation == NetworkOperation.DNS_LOOKUP
        assert result.target == "google.com"
        assert "domain" in result.result_data
        assert "records" in result.result_data

class TestUtilityModels:
    """Test suite for utility models."""
    
    def test_file_info_creation(self):
        """Test FileInfo creation."""
        file_info = FileInfo(
            filename="test.txt",
            filepath="/tmp/test.txt",
            size=1024,
            checksum="abc123",
            mime_type="text/plain"
        )
        
        assert file_info.filename == "test.txt"
        assert file_info.filepath == "/tmp/test.txt"
        assert file_info.size == 1024
        assert file_info.checksum == "abc123"
    
    def test_process_info_creation(self):
        """Test ProcessInfo creation."""
        process_info = ProcessInfo(
            pid=1234,
            name="python",
            command="python script.py",
            user="user",
            memory_usage=1024000,
            cpu_usage=5.2
        )
        
        assert process_info.pid == 1234
        assert process_info.name == "python"
        assert process_info.command == "python script.py"
        assert process_info.memory_usage == 1024000
    
    def test_system_info_creation(self):
        """Test SystemInfo creation."""
        system_info = SystemInfo(
            hostname="test-host",
            os_name="Linux",
            os_version="Ubuntu 20.04",
            architecture="x86_64",
            cpu_count=4,
            memory_total=8589934592,
            uptime=3600.0
        )
        
        assert system_info.hostname == "test-host"
        assert system_info.os_name == "Linux"
        assert system_info.cpu_count == 4
        assert system_info.memory_total == 8589934592
    
    def test_log_entry_creation(self):
        """Test LogEntry creation."""
        log_entry = LogEntry(
            level="INFO",
            message="Test log message",
            source="test_module",
            module="test",
            function="test_function",
            line_number=42
        )
        
        assert log_entry.level == "INFO"
        assert log_entry.message == "Test log message"
        assert log_entry.source == "test_module"
        assert log_entry.module == "test"
    
    def test_error_info_creation(self):
        """Test ErrorInfo creation."""
        error_info = ErrorInfo(
            error_id="ERROR-001",
            error_type="ValueError",
            error_message="Invalid input",
            error_code="INVALID_INPUT",
            severity="medium"
        )
        
        assert error_info.error_id == "ERROR-001"
        assert error_info.error_type == "ValueError"
        assert error_info.error_message == "Invalid input"
        assert error_info.severity == "medium"

class TestSchemas:
    """Test suite for schemas."""
    
    def test_scan_request_schema_validation(self):
        """Test ScanRequestSchema validation."""
        # Valid schema
        schema = ScanRequestSchema(
            scan_type=ScanType.PORT_SCAN,
            targets=["192.168.1.1", "example.com"],
            ports=[80, 443, 22]
        )
        assert schema.scan_type == ScanType.PORT_SCAN
        assert len(schema.targets) == 2
        
        # Invalid target
        with pytest.raises(ValueError, match="Invalid target format"):
            ScanRequestSchema(
                scan_type=ScanType.PORT_SCAN,
                targets=["invalid@target"]
            )
    
    def test_attack_request_schema_validation(self):
        """Test AttackRequestSchema validation."""
        schema = AttackRequestSchema(
            attack_type=AttackType.BRUTE_FORCE,
            target="192.168.1.1:22",
            credentials={"username": "admin", "password": "password123"}
        )
        assert schema.attack_type == AttackType.BRUTE_FORCE
        assert schema.target == "192.168.1.1:22"
    
    def test_enumeration_request_schema_validation(self):
        """Test EnumerationRequestSchema validation."""
        schema = EnumerationRequestSchema(
            enumeration_type=EnumerationType.PORT_ENUMERATION,
            target="192.168.1.1",
            ports=[21, 22, 23, 25, 80, 443]
        )
        assert schema.enumeration_type == EnumerationType.PORT_ENUMERATION
        assert schema.target == "192.168.1.1"
    
    def test_report_request_schema_validation(self):
        """Test ReportRequestSchema validation."""
        schema = ReportRequestSchema(
            report_format=ReportFormat.HTML,
            report_level=ReportLevel.DETAILED,
            sections=[ReportSection.EXECUTIVE_SUMMARY, ReportSection.FINDINGS]
        )
        assert schema.report_format == ReportFormat.HTML
        assert schema.report_level == ReportLevel.DETAILED
    
    def test_crypto_request_schema_validation(self):
        """Test CryptoRequestSchema validation."""
        schema = CryptoRequestSchema(
            operation=CryptoOperation.HASH,
            data="Hello, World!",
            algorithm=HashAlgorithm.SHA256
        )
        assert schema.operation == CryptoOperation.HASH
        assert schema.data == "Hello, World!"
    
    def test_network_request_schema_validation(self):
        """Test NetworkRequestSchema validation."""
        schema = NetworkRequestSchema(
            operation=NetworkOperation.DNS_LOOKUP,
            target="google.com",
            timeout=10.0
        )
        assert schema.operation == NetworkOperation.DNS_LOOKUP
        assert schema.target == "google.com"
    
    def test_target_validation_schema(self):
        """Test TargetValidationSchema validation."""
        # Valid IP
        schema = TargetValidationSchema(target="192.168.1.1", target_type="ip")
        assert schema.target == "192.168.1.1"
        
        # Valid domain
        schema = TargetValidationSchema(target="example.com", target_type="domain")
        assert schema.target == "example.com"
        
        # Invalid IP
        with pytest.raises(ValueError, match="Invalid IP address"):
            TargetValidationSchema(target="invalid-ip", target_type="ip")
    
    def test_port_validation_schema(self):
        """Test PortValidationSchema validation."""
        schema = PortValidationSchema(port=80, protocol="tcp")
        assert schema.port == 80
        assert schema.protocol == "tcp"
    
    def test_credential_validation_schema(self):
        """Test CredentialValidationSchema validation."""
        schema = CredentialValidationSchema(
            username="admin",
            password="password123",
            domain="example.com"
        )
        assert schema.username == "admin"
        assert schema.password == "password123"
        assert schema.domain == "example.com"
    
    def test_payload_validation_schema(self):
        """Test PayloadValidationSchema validation."""
        schema = PayloadValidationSchema(
            payload_type="sql_injection",
            content="' OR 1=1 --",
            encoding="utf-8",
            size_limit=1048576
        )
        assert schema.payload_type == "sql_injection"
        assert schema.content == "' OR 1=1 --"
    
    def test_export_schemas(self):
        """Test export schemas."""
        # JSON export
        json_schema = JSONExportSchema(
            data={"key": "value"},
            pretty_print=True,
            include_metadata=True
        )
        assert json_schema.pretty_print is True
        
        # CSV export
        csv_schema = CSVExportSchema(
            data=[{"name": "John", "age": 30}],
            headers=["name", "age"],
            delimiter=",",
            include_headers=True
        )
        assert csv_schema.delimiter == ","
        
        # XML export
        xml_schema = XMLExportSchema(
            data={"user": {"name": "John"}},
            root_element="users",
            pretty_print=True
        )
        assert xml_schema.root_element == "users"
        
        # HTML export
        html_schema = HTMLExportSchema(
            data={"title": "Report", "content": "Hello"},
            title="Security Report",
            include_css=True
        )
        assert html_schema.title == "Security Report"

class TestModelSerialization:
    """Test suite for model serialization."""
    
    def test_model_to_dict(self):
        """Test model serialization to dictionary."""
        request = ScanRequest(
            request_id="scan_001",
            scan_type=ScanType.PORT_SCAN,
            targets=["192.168.1.1"]
        )
        
        data = request.dict()
        assert data["request_id"] == "scan_001"
        assert data["scan_type"] == "port_scan"
        assert data["targets"] == ["192.168.1.1"]
    
    def test_model_to_json(self):
        """Test model serialization to JSON."""
        request = ScanRequest(
            request_id="scan_001",
            scan_type=ScanType.PORT_SCAN,
            targets=["192.168.1.1"]
        )
        
        json_data = request.json()
        assert "scan_001" in json_data
        assert "port_scan" in json_data
    
    def test_model_from_dict(self):
        """Test model creation from dictionary."""
        data = {
            "request_id": "scan_001",
            "scan_type": "port_scan",
            "targets": ["192.168.1.1"]
        }
        
        request = ScanRequest(**data)
        assert request.request_id == "scan_001"
        assert request.scan_type == ScanType.PORT_SCAN

class TestModelValidation:
    """Test suite for model validation."""
    
    def test_required_fields_validation(self):
        """Test required fields validation."""
        with pytest.raises(ValueError):
            ScanRequest(
                request_id="scan_001"
                # Missing required fields
            )
    
    def test_field_type_validation(self):
        """Test field type validation."""
        with pytest.raises(ValueError):
            ScanRequest(
                request_id="scan_001",
                scan_type="invalid_type",  # Should be ScanType enum
                targets=["192.168.1.1"]
            )
    
    def test_field_range_validation(self):
        """Test field range validation."""
        with pytest.raises(ValueError):
            ScanRequest(
                request_id="scan_001",
                scan_type=ScanType.PORT_SCAN,
                targets=["192.168.1.1"],
                ports=[70000]  # Invalid port number
            )
    
    def test_custom_validator(self):
        """Test custom validator functions."""
        # Test target validation
        with pytest.raises(ValueError, match="Invalid target format"):
            ScanRequest(
                request_id="scan_001",
                scan_type=ScanType.PORT_SCAN,
                targets=["invalid@target"]
            )

class TestEnumValues:
    """Test suite for enum values."""
    
    def test_scan_type_enum_values(self):
        """Test ScanType enum values."""
        assert ScanType.PORT_SCAN == "port_scan"
        assert ScanType.VULNERABILITY_SCAN == "vulnerability_scan"
        assert ScanType.NETWORK_SCAN == "network_scan"
        assert ScanType.WEB_SCAN == "web_scan"
        assert ScanType.SSL_SCAN == "ssl_scan"
        assert ScanType.DNS_SCAN == "dns_scan"
        assert ScanType.COMPREHENSIVE_SCAN == "comprehensive_scan"
    
    def test_vulnerability_level_enum_values(self):
        """Test VulnerabilityLevel enum values."""
        assert VulnerabilityLevel.INFO == "info"
        assert VulnerabilityLevel.LOW == "low"
        assert VulnerabilityLevel.MEDIUM == "medium"
        assert VulnerabilityLevel.HIGH == "high"
        assert VulnerabilityLevel.CRITICAL == "critical"
    
    def test_attack_type_enum_values(self):
        """Test AttackType enum values."""
        assert AttackType.BRUTE_FORCE == "brute_force"
        assert AttackType.EXPLOIT == "exploit"
        assert AttackType.DOS == "dos"
        assert AttackType.PHISHING == "phishing"
        assert AttackType.SQL_INJECTION == "sql_injection"
        assert AttackType.XSS == "xss"
    
    def test_report_format_enum_values(self):
        """Test ReportFormat enum values."""
        assert ReportFormat.JSON == "json"
        assert ReportFormat.HTML == "html"
        assert ReportFormat.PDF == "pdf"
        assert ReportFormat.CSV == "csv"
        assert ReportFormat.XML == "xml"
        assert ReportFormat.MARKDOWN == "markdown"
    
    def test_crypto_operation_enum_values(self):
        """Test CryptoOperation enum values."""
        assert CryptoOperation.HASH == "hash"
        assert CryptoOperation.ENCRYPT == "encrypt"
        assert CryptoOperation.DECRYPT == "decrypt"
        assert CryptoOperation.SIGN == "sign"
        assert CryptoOperation.VERIFY == "verify"
        assert CryptoOperation.KEY_GENERATION == "key_generation"
        assert CryptoOperation.KEY_DERIVATION == "key_derivation"
    
    def test_network_operation_enum_values(self):
        """Test NetworkOperation enum values."""
        assert NetworkOperation.DNS_LOOKUP == "dns_lookup"
        assert NetworkOperation.HTTP_REQUEST == "http_request"
        assert NetworkOperation.HTTPS_REQUEST == "https_request"
        assert NetworkOperation.PORT_CHECK == "port_check"
        assert NetworkOperation.HOSTNAME_RESOLVE == "hostname_resolve"
        assert NetworkOperation.NETWORK_INFO == "network_info"
        assert NetworkOperation.TRACEROUTE == "traceroute"
        assert NetworkOperation.CONNECTIVITY_CHECK == "connectivity_check"
        assert NetworkOperation.SSL_CERTIFICATE == "ssl_certificate"
        assert NetworkOperation.WHOIS_LOOKUP == "whois_lookup"
        assert NetworkOperation.GEOLOCATION == "geolocation"
        assert NetworkOperation.ARP_SCAN == "arp_scan" 