from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
BUFFER_SIZE = 1024

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from cybersecurity_security.network import (
from typing import Any, List, Dict, Optional
import logging
"""
Tests for Network Module

Tests network scanning and security assessment functionality.
"""

    PortScanRequest, PortScanResult, PortRangeScanRequest,
    PortRangeScanResult, scan_port, scan_port_async,
    scan_port_range_async, get_service_name
)

class TestNetwork:
    """Test suite for network module."""
    
    async def test_port_scan_request_creation(self) -> Any:
        """Test PortScanRequest creation with valid data."""
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
    
    async def test_port_scan_request_invalid_host(self) -> Any:
        """Test PortScanRequest with invalid host."""
        with pytest.raises(ValueError, match="Target host cannot be empty"):
            PortScanRequest(
                target_host="",
                port=80
            )
    
    async def test_port_range_scan_request_creation(self) -> Any:
        """Test PortRangeScanRequest creation."""
        request = PortRangeScanRequest(
            target_host="localhost",
            start_port=1,
            end_port=1024,
            max_workers=10,
            timeout=1.0
        )
        assert request.target_host == "localhost"
        assert request.start_port == 1
        assert request.end_port == 1024
        assert request.max_workers == 10
    
    async def test_port_range_scan_request_invalid_range(self) -> Any:
        """Test PortRangeScanRequest with invalid port range."""
        with pytest.raises(ValueError, match="End port must be greater than start port"):
            PortRangeScanRequest(
                target_host="localhost",
                start_port=1024,
                end_port=1
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
        # Mock socket to simulate open port
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
        assert result.error is None
    
    @patch('socket.socket')
    def test_scan_port_closed(self, mock_socket) -> Any:
        """Test scanning a closed port."""
        # Mock socket to simulate closed port
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 1
        mock_socket.return_value = mock_sock
        
        request = PortScanRequest(
            target_host="localhost",
            port=9999,
            timeout=1.0
        )
        result = scan_port(request)
        
        assert result.host == "localhost"
        assert result.port == 9999
        assert result.is_open is False
        assert result.service is None
        assert result.error is None
    
    @patch('socket.socket')
    def test_scan_port_error(self, mock_socket) -> Any:
        """Test scanning port with error."""
        # Mock socket to raise exception
        mock_socket.side_effect = Exception("Connection error")
        
        request = PortScanRequest(
            target_host="localhost",
            port=80,
            timeout=1.0
        )
        result = scan_port(request)
        
        assert result.host == "localhost"
        assert result.port == 80
        assert result.is_open is False
        assert result.error == "Connection error"
    
    @pytest.mark.asyncio
    async def test_scan_port_async(self) -> Any:
        """Test async port scanning."""
        with patch('cybersecurity_security.network.port_scanner.scan_port') as mock_scan:
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
    
    @pytest.mark.asyncio
    async def test_scan_port_range_async(self) -> Any:
        """Test async port range scanning."""
        # Mock individual port scans
        mock_results = [
            PortScanResult(
                host="localhost",
                port=80,
                is_open=True,
                service="HTTP",
                scan_time=1234567890.0
            ),
            PortScanResult(
                host="localhost",
                port=443,
                is_open=True,
                service="HTTPS",
                scan_time=1234567890.0
            ),
            PortScanResult(
                host="localhost",
                port=8080,
                is_open=False,
                service=None,
                scan_time=1234567890.0
            )
        ]
        
        with patch('cybersecurity_security.network.port_scanner.scan_port_async') as mock_scan_async:
            mock_scan_async.side_effect = mock_results
            
            request = PortRangeScanRequest(
                target_host="localhost",
                start_port=80,
                end_port=82,
                max_workers=2,
                timeout=1.0
            )
            result = await scan_port_range_async(request)
            
            assert result.target_host == "localhost"
            assert result.port_range == "80-82"
            assert result.total_ports_scanned == 3
            assert result.open_port_count == 2
            assert len(result.open_ports) == 2
            assert len(result.scan_results) == 3
    
    @pytest.mark.asyncio
    async def test_scan_port_range_async_with_exceptions(self) -> Any:
        """Test async port range scanning with exceptions."""
        # Mock some successful scans and some exceptions
        mock_results = [
            PortScanResult(
                host="localhost",
                port=80,
                is_open=True,
                service="HTTP",
                scan_time=1234567890.0
            ),
            Exception("Connection timeout"),
            PortScanResult(
                host="localhost",
                port=443,
                is_open=False,
                service=None,
                scan_time=1234567890.0
            )
        ]
        
        with patch('cybersecurity_security.network.port_scanner.scan_port_async') as mock_scan_async:
            mock_scan_async.side_effect = mock_results
            
            request = PortRangeScanRequest(
                target_host="localhost",
                start_port=80,
                end_port=82,
                max_workers=2,
                timeout=1.0
            )
            result = await scan_port_range_async(request)
            
            assert result.target_host == "localhost"
            assert result.total_ports_scanned == 2  # Only successful scans
            assert result.open_port_count == 1
            assert len(result.scan_results) == 2
    
    def test_port_scan_result_creation(self) -> Any:
        """Test PortScanResult creation."""
        result = PortScanResult(
            host="localhost",
            port=80,
            is_open=True,
            service="HTTP",
            scan_time=1234567890.0
        )
        assert result.host == "localhost"
        assert result.port == 80
        assert result.is_open is True
        assert result.service == "HTTP"
        assert result.scan_time == 1234567890.0
        assert result.error is None
    
    def test_port_range_scan_result_creation(self) -> Any:
        """Test PortRangeScanResult creation."""
        open_ports = [
            PortScanResult(host="localhost", port=80, is_open=True, service="HTTP", scan_time=1234567890.0)
        ]
        scan_results = [
            PortScanResult(host="localhost", port=80, is_open=True, service="HTTP", scan_time=1234567890.0),
            PortScanResult(host="localhost", port=443, is_open=False, service=None, scan_time=1234567890.0)
        ]
        
        result = PortRangeScanResult(
            target_host="localhost",
            port_range="80-443",
            total_ports_scanned=2,
            open_ports=open_ports,
            open_port_count=1,
            scan_results=scan_results,
            scan_completed_at=1234567890.0
        )
        
        assert result.target_host == "localhost"
        assert result.port_range == "80-443"
        assert result.total_ports_scanned == 2
        assert result.open_port_count == 1
        assert len(result.open_ports) == 1
        assert len(result.scan_results) == 2 