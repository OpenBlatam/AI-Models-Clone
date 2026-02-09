from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from cybersecurity_security.scanners import (
from typing import Any, List, Dict, Optional
import logging
"""
Tests for Scanners Module

Tests port scanner, vulnerability scanner, and web scanner functionality.
"""

    # Port Scanner
    PortScanRequest, PortScanResult, PortRangeScanRequest, PortRangeScanResult,
    scan_port, scan_port_async, scan_port_range_async, get_service_name,
    
    # Vulnerability Scanner
    VulnerabilityScanRequest, VulnerabilityScanResult, VulnerabilityType,
    scan_vulnerabilities_async, scan_sql_injection, scan_xss_vulnerabilities,
    scan_csrf_vulnerabilities, scan_file_inclusion_vulnerabilities,
    
    # Web Scanner
    WebScanRequest, WebScanResult, WebVulnerabilityType,
    scan_web_application_async, scan_web_directory_enumeration,
    scan_web_robots_txt, scan_web_sitemap, scan_web_headers, scan_web_ssl_certificate
)

class TestPortScanner:
    """Test suite for port scanner."""
    
    async def test_port_scan_request_creation(self) -> Any:
        """Test PortScanRequest creation."""
        request = PortScanRequest(
            target_host="localhost",
            port=80,
            timeout=1.0
        )
        assert request.target_host == "localhost"
        assert request.port == 80
        assert request.timeout == 1.0
    
    async def test_port_scan_request_invalid_port(self) -> Any:
        """Test PortScanRequest with invalid port."""
        with pytest.raises(ValueError):
            PortScanRequest(
                target_host="localhost",
                port=70000  # Should be <= 65535
            )
    
    def test_get_service_name(self) -> Optional[Dict[str, Any]]:
        """Test service name resolution."""
        assert get_service_name(80) == "HTTP"
        assert get_service_name(443) == "HTTPS"
        assert get_service_name(22) == "SSH"
        assert get_service_name(9999) == "Unknown"
    
    @patch('socket.socket')
    def test_scan_port_open(self, mock_socket) -> Any:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        """Test scanning an open port."""
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        request = PortScanRequest(
            target_host="localhost",
            port=80,
            timeout=1.0
        )
        result = scan_port(request)
        
        assert result.host == "localhost"
        assert result.port == 80
        assert result.is_open is True
        assert result.service == "HTTP"
    
    @pytest.mark.asyncio
    async def test_scan_port_async(self) -> Any:
        """Test async port scanning."""
        with patch('cybersecurity_security.scanners.port_scanner.scan_port') as mock_scan:
            mock_scan.return_value = PortScanResult(
                host="localhost",
                port=80,
                is_open=True,
                service="HTTP",
                scan_time=1234567890.0
            )
            
            request = PortScanRequest(
                target_host="localhost",
                port=80,
                timeout=1.0
            )
            result = await scan_port_async(request)
            
            assert result.host == "localhost"
            assert result.port == 80
            assert result.is_open is True
            assert result.service == "HTTP"

class TestVulnerabilityScanner:
    """Test suite for vulnerability scanner."""
    
    async def test_vulnerability_scan_request_creation(self) -> Any:
        """Test VulnerabilityScanRequest creation."""
        request = VulnerabilityScanRequest(
            target_url="http://example.com",
            scan_types=[VulnerabilityType.SQL_INJECTION, VulnerabilityType.XSS],
            max_concurrent_requests=5
        )
        assert request.target_url == "http://example.com"
        assert VulnerabilityType.SQL_INJECTION in request.scan_types
        assert VulnerabilityType.XSS in request.scan_types
        assert request.max_concurrent_requests == 5
    
    async def test_vulnerability_scan_request_invalid_url(self) -> Any:
        """Test VulnerabilityScanRequest with invalid URL."""
        with pytest.raises(ValueError, match="Target URL must start with http:// or https://"):
            VulnerabilityScanRequest(
                target_url="ftp://example.com"
            )
    
    @pytest.mark.asyncio
    async def test_scan_sql_injection(self) -> Any:
        """Test SQL injection scanning."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = asyncio.coroutine(lambda: "mysql_fetch error")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            data = {
                "target_url": "http://example.com",
                "payloads": ["' OR '1'='1"],
                "timeout": 10.0
            }
            
            results = await scan_sql_injection(data)
            
            assert len(results) == 1
            assert results[0].vulnerability_type == VulnerabilityType.SQL_INJECTION
            assert results[0].is_vulnerable is True
            assert results[0].severity == "high"
    
    @pytest.mark.asyncio
    async def test_scan_xss_vulnerabilities(self) -> Any:
        """Test XSS vulnerability scanning."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = asyncio.coroutine(lambda: "<script>alert('XSS')</script>")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            data = {
                "target_url": "http://example.com",
                "payloads": ["<script>alert('XSS')</script>"],
                "timeout": 10.0
            }
            
            results = await scan_xss_vulnerabilities(data)
            
            assert len(results) == 1
            assert results[0].vulnerability_type == VulnerabilityType.XSS
            assert results[0].is_vulnerable is True
            assert results[0].severity == "high"
    
    @pytest.mark.asyncio
    async def test_scan_vulnerabilities_async(self) -> Any:
        """Test comprehensive vulnerability scanning."""
        with patch('cybersecurity_security.scanners.vulnerability_scanner.scan_sql_injection') as mock_sql:
            mock_sql.return_value = []
            
            request = VulnerabilityScanRequest(
                target_url="http://example.com",
                scan_types=[VulnerabilityType.SQL_INJECTION],
                max_concurrent_requests=5
            )
            
            result = await scan_vulnerabilities_async(request)
            
            assert result.target_url == "http://example.com"
            assert VulnerabilityType.SQL_INJECTION in result.scan_types
            assert result.total_tests_performed >= 0
            assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

class TestWebScanner:
    """Test suite for web scanner."""
    
    async def test_web_scan_request_creation(self) -> Any:
        """Test WebScanRequest creation."""
        request = WebScanRequest(
            target_url="https://example.com",
            scan_types=[WebVulnerabilityType.DIRECTORY_ENUMERATION],
            common_directories=["admin", "login"],
            max_concurrent_requests=5
        )
        assert request.target_url == "https://example.com"
        assert WebVulnerabilityType.DIRECTORY_ENUMERATION in request.scan_types
        assert "admin" in request.common_directories
        assert request.max_concurrent_requests == 5
    
    async def test_web_scan_request_invalid_url(self) -> Any:
        """Test WebScanRequest with invalid URL."""
        with pytest.raises(ValueError, match="Target URL must start with http:// or https://"):
            WebScanRequest(
                target_url="ftp://example.com"
            )
    
    @pytest.mark.asyncio
    async def test_scan_web_directory_enumeration(self) -> Any:
        """Test web directory enumeration."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = asyncio.coroutine(lambda: "Directory listing")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            data = {
                "target_url": "http://example.com",
                "directories": ["admin"],
                "timeout": 10.0,
                "max_concurrent_requests": 5
            }
            
            results = await scan_web_directory_enumeration(data)
            
            assert len(results) == 1
            assert results[0].vulnerability_type == WebVulnerabilityType.DIRECTORY_ENUMERATION
            assert results[0].is_vulnerable is True
            assert results[0].response_code == 200
    
    @pytest.mark.asyncio
    async def test_scan_web_robots_txt(self) -> Any:
        """Test robots.txt scanning."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = asyncio.coroutine(lambda: "Disallow: /admin\nDisallow: /config")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            data = {
                "target_url": "http://example.com",
                "timeout": 10.0
            }
            
            result = await scan_web_robots_txt(data)
            
            assert result.vulnerability_type == WebVulnerabilityType.ROBOTS_TXT_EXPOSURE
            assert result.is_vulnerable is True
            assert result.response_code == 200
            assert "admin" in result.evidence
    
    @pytest.mark.asyncio
    async def test_scan_web_headers(self) -> Any:
        """Test security headers scanning."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            data = {
                "target_url": "http://example.com",
                "timeout": 10.0
            }
            
            result = await scan_web_headers(data)
            
            assert result.vulnerability_type == WebVulnerabilityType.INSECURE_HEADERS
            assert result.is_vulnerable is False  # Should have good headers
            assert result.response_code == 200
    
    @pytest.mark.asyncio
    async def test_scan_web_application_async(self) -> Any:
        """Test comprehensive web application scanning."""
        with patch('cybersecurity_security.scanners.web_scanner.scan_web_directory_enumeration') as mock_dir:
            mock_dir.return_value = []
            
            request = WebScanRequest(
                target_url="https://example.com",
                scan_types=[WebVulnerabilityType.DIRECTORY_ENUMERATION],
                max_concurrent_requests=5
            )
            
            result = await scan_web_application_async(request)
            
            assert result.target_url == "https://example.com"
            assert WebVulnerabilityType.DIRECTORY_ENUMERATION in result.scan_types
            assert result.total_requests_made >= 0
            assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

class TestScannerIntegration:
    """Integration tests for scanner modules."""
    
    @pytest.mark.asyncio
    async def test_multiple_scanner_types(self) -> Any:
        """Test using multiple scanner types together."""
        # Test port scanning
        port_request = PortRangeScanRequest(
            target_host="localhost",
            start_port=80,
            end_port=81,
            max_workers=2
        )
        
        # Test vulnerability scanning
        vuln_request = VulnerabilityScanRequest(
            target_url="http://localhost",
            scan_types=[VulnerabilityType.SQL_INJECTION],
            max_concurrent_requests=2
        )
        
        # Test web scanning
        web_request = WebScanRequest(
            target_url="http://localhost",
            scan_types=[WebVulnerabilityType.INSECURE_HEADERS],
            max_concurrent_requests=2
        )
        
        # Run all scans (with mocked dependencies)
        with patch('cybersecurity_security.scanners.port_scanner.scan_port_async') as mock_port:
            mock_port.return_value = PortScanResult(
                host="localhost", port=80, is_open=True, service="HTTP", scan_time=1234567890.0
            )
            
            with patch('cybersecurity_security.scanners.vulnerability_scanner.scan_sql_injection') as mock_vuln:
                mock_vuln.return_value = []
                
                with patch('cybersecurity_security.scanners.web_scanner.scan_web_headers') as mock_web:
                    mock_web.return_value = WebVulnerabilityResult(
                        vulnerability_type=WebVulnerabilityType.INSECURE_HEADERS,
                        url="http://localhost",
                        is_vulnerable=False,
                        severity="low"
                    )
                    
                    # Execute scans
                    port_result = await scan_port_range_async(port_request)
                    vuln_result = await scan_vulnerabilities_async(vuln_request)
                    web_result = await scan_web_application_async(web_request)
                    
                    # Verify results
                    assert port_result.target_host == "localhost"
                    assert vuln_result.target_url == "http://localhost"
                    assert web_result.target_url == "http://localhost" 