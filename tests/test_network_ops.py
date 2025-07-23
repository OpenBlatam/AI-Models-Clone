"""
Tests for Network Operations Module.

Tests packet crafting, sniffing, and port scanning functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the functions to test
from utils.network_ops import (
    craft_tcp_packet, craft_udp_packet, craft_icmp_packet,
    craft_dns_packet, craft_arp_packet,
    send_packet, sniff_packets,
    scan_single_port, scan_port_range,
    craft_packet_roro, send_packet_roro, sniff_packets_roro, scan_ports_roro,
    PacketConfig, ScanConfig, PacketType, ScanType, Protocol,
    SCAPY_AVAILABLE, NMAP_AVAILABLE
)

# =============================================================================
# TEST DATA
# =============================================================================

@pytest.fixture
def sample_packet_config():
    """Sample packet configuration for testing."""
    return PacketConfig(
        source_ip="192.168.1.100",
        destination_ip="192.168.1.1",
        source_port=12345,
        destination_port=80,
        protocol=Protocol.TCP,
        payload="test payload",
        ttl=64,
        flags="S",
        timeout=3
    )

@pytest.fixture
def sample_scan_config():
    """Sample scan configuration for testing."""
    return ScanConfig(
        target_host="localhost",
        port_range="1-100",
        scan_type=ScanType.TCP_SYN,
        timeout=5,
        verbose=False,
        max_retries=3
    )

# =============================================================================
# PACKET CRAFTING TESTS
# =============================================================================

class TestPacketCrafting:
    """Test packet crafting functionality."""
    
    def test_craft_tcp_packet_success(self, sample_packet_config):
        """Test successful TCP packet crafting."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        packet = craft_tcp_packet(sample_packet_config)
        
        assert packet is not None
        # Add more specific assertions based on Scapy packet structure
    
    def test_craft_tcp_packet_no_scapy(self, sample_packet_config):
        """Test TCP packet crafting when Scapy is not available."""
        with patch('utils.network_ops.SCAPY_AVAILABLE', False):
            packet = craft_tcp_packet(sample_packet_config)
            assert packet is None
    
    def test_craft_udp_packet_success(self, sample_packet_config):
        """Test successful UDP packet crafting."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        sample_packet_config.protocol = Protocol.UDP
        packet = craft_udp_packet(sample_packet_config)
        
        assert packet is not None
    
    def test_craft_icmp_packet_success(self, sample_packet_config):
        """Test successful ICMP packet crafting."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        sample_packet_config.protocol = Protocol.ICMP
        packet = craft_icmp_packet(sample_packet_config)
        
        assert packet is not None
    
    def test_craft_dns_packet_success(self, sample_packet_config):
        """Test successful DNS packet crafting."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        sample_packet_config.payload = "example.com"
        packet = craft_dns_packet(sample_packet_config)
        
        assert packet is not None
    
    def test_craft_arp_packet_success(self, sample_packet_config):
        """Test successful ARP packet crafting."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        packet = craft_arp_packet(sample_packet_config)
        
        assert packet is not None

# =============================================================================
# PACKET OPERATIONS TESTS
# =============================================================================

class TestPacketOperations:
    """Test packet sending and sniffing functionality."""
    
    def test_send_packet_success(self):
        """Test successful packet sending."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        # Mock packet
        mock_packet = Mock()
        mock_packet.__contains__ = lambda x: x in ['IP', 'TCP']
        mock_packet.__getitem__ = lambda x: Mock(src="192.168.1.100", dst="192.168.1.1")
        
        with patch('utils.network_ops.sr1') as mock_sr1:
            mock_sr1.return_value = Mock()
            result = send_packet(mock_packet, timeout=3)
            
            assert result.success is True
            assert result.source == "192.168.1.100"
            assert result.destination == "192.168.1.1"
    
    def test_send_packet_no_scapy(self):
        """Test packet sending when Scapy is not available."""
        with patch('utils.network_ops.SCAPY_AVAILABLE', False):
            result = send_packet(Mock(), timeout=3)
            assert result.success is False
            assert "Scapy not available" in result.error_message
    
    def test_sniff_packets_success(self):
        """Test successful packet sniffing."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        mock_packets = [Mock(), Mock()]
        for packet in mock_packets:
            packet.time = 1234567890.0
            packet.__len__ = lambda: 100
            packet.__contains__ = lambda x: x in ['IP', 'TCP']
            packet.__getitem__ = lambda x: Mock(src="192.168.1.100", dst="192.168.1.1", proto=6)
        
        with patch('utils.network_ops.sniff') as mock_sniff:
            mock_sniff.return_value = mock_packets
            results = sniff_packets(interface="eth0", count=2, timeout=10)
            
            assert len(results) == 2
            assert all("source_ip" in result for result in results)
    
    def test_sniff_packets_no_scapy(self):
        """Test packet sniffing when Scapy is not available."""
        with patch('utils.network_ops.SCAPY_AVAILABLE', False):
            results = sniff_packets(interface="eth0", count=2, timeout=10)
            assert results == []

# =============================================================================
# PORT SCANNING TESTS
# =============================================================================

class TestPortScanning:
    """Test port scanning functionality."""
    
    def test_scan_single_port_success(self):
        """Test successful single port scanning."""
        if not NMAP_AVAILABLE:
            pytest.skip("python-nmap not available")
        
        with patch('utils.network_ops.nmap.PortScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner_class.return_value = mock_scanner
            
            # Mock scan results
            mock_scanner.all_hosts.return_value = ["localhost"]
            mock_scanner.__getitem__.return_value = {
                "tcp": {
                    80: {
                        "state": "open",
                        "name": "http",
                        "version": "1.1",
                        "product": "Apache"
                    }
                }
            }
            
            result = scan_single_port("localhost", 80, "tcp", 5)
            
            assert result.host == "localhost"
            assert result.port == 80
            assert result.state == "open"
            assert result.service == "http"
    
    def test_scan_single_port_no_nmap(self):
        """Test single port scanning when python-nmap is not available."""
        with patch('utils.network_ops.NMAP_AVAILABLE', False):
            result = scan_single_port("localhost", 80, "tcp", 5)
            assert result.state == "unknown"
    
    def test_scan_port_range_success(self):
        """Test successful port range scanning."""
        if not NMAP_AVAILABLE:
            pytest.skip("python-nmap not available")
        
        with patch('utils.network_ops.nmap.PortScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner_class.return_value = mock_scanner
            
            # Mock scan results
            mock_scanner.all_hosts.return_value = ["localhost"]
            mock_scanner.__getitem__.return_value = {
                "tcp": {
                    80: {"state": "open", "name": "http"},
                    443: {"state": "closed", "name": "https"}
                }
            }
            
            result = scan_port_range("localhost", "80-443", ScanType.TCP_SYN, 5)
            
            assert result.target == "localhost"
            assert result.total_ports == 2
            assert result.open_ports == 1
            assert result.closed_ports == 1
    
    def test_scan_port_range_no_nmap(self):
        """Test port range scanning when python-nmap is not available."""
        with patch('utils.network_ops.NMAP_AVAILABLE', False):
            result = scan_port_range("localhost", "80-443", ScanType.TCP_SYN, 5)
            assert result.total_ports == 0
            assert "python-nmap not available" in result.errors

# =============================================================================
# RORO INTERFACE TESTS
# =============================================================================

class TestRoroInterfaces:
    """Test RORO interface functions."""
    
    def test_craft_packet_roro_tcp(self, sample_packet_config):
        """Test TCP packet crafting via RORO interface."""
        request = {
            "packet_type": PacketType.TCP,
            "config": {
                "source_ip": "192.168.1.100",
                "destination_ip": "192.168.1.1",
                "source_port": 12345,
                "destination_port": 80,
                "protocol": Protocol.TCP,
                "payload": "test",
                "ttl": 64,
                "flags": "S",
                "timeout": 3
            }
        }
        
        result = craft_packet_roro(request)
        
        assert "success" in result
        assert result["packet_type"] == PacketType.TCP
    
    def test_send_packet_roro(self):
        """Test packet sending via RORO interface."""
        request = {
            "packet": Mock(),
            "timeout": 3
        }
        
        with patch('utils.network_ops.send_packet') as mock_send:
            mock_send.return_value = Mock(
                success=True,
                packet_type=PacketType.CUSTOM,
                source="192.168.1.100",
                destination="192.168.1.1",
                protocol=Protocol.TCP,
                payload_size=10,
                response_time=0.1,
                response_data={"test": "data"},
                error_message=None
            )
            
            result = send_packet_roro(request)
            
            assert result["success"] is True
            assert result["source"] == "192.168.1.100"
    
    def test_sniff_packets_roro(self):
        """Test packet sniffing via RORO interface."""
        request = {
            "interface": "eth0",
            "count": 5,
            "timeout": 10,
            "filter": "tcp"
        }
        
        with patch('utils.network_ops.sniff_packets') as mock_sniff:
            mock_sniff.return_value = [{"test": "packet"}]
            
            result = sniff_packets_roro(request)
            
            assert result["success"] is True
            assert result["packets_captured"] == 1
            assert result["interface"] == "eth0"
    
    def test_scan_ports_roro_single(self):
        """Test single port scanning via RORO interface."""
        request = {
            "host": "localhost",
            "port_range": "80",
            "scan_type": ScanType.TCP_SYN,
            "timeout": 5
        }
        
        with patch('utils.network_ops.scan_single_port') as mock_scan:
            mock_scan.return_value = Mock(
                host="localhost",
                port=80,
                state="open",
                service="http",
                version="1.1",
                banner="Apache",
                scan_time=0.5
            )
            
            result = scan_ports_roro(request)
            
            assert result["success"] is True
            assert result["host"] == "localhost"
            assert result["port"] == 80
            assert result["state"] == "open"
    
    def test_scan_ports_roro_range(self):
        """Test port range scanning via RORO interface."""
        request = {
            "host": "localhost",
            "port_range": "80-443",
            "scan_type": ScanType.TCP_SYN,
            "timeout": 5
        }
        
        with patch('utils.network_ops.scan_port_range') as mock_scan:
            mock_scan.return_value = Mock(
                target="localhost",
                scan_type=ScanType.TCP_SYN,
                total_ports=2,
                open_ports=1,
                closed_ports=1,
                filtered_ports=0,
                scan_duration=1.0,
                results=[],
                errors=[]
            )
            
            result = scan_ports_roro(request)
            
            assert result["success"] is True
            assert result["target"] == "localhost"
            assert result["total_ports"] == 2

# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for network operations."""
    
    @pytest.mark.asyncio
    async def test_full_packet_workflow(self, sample_packet_config):
        """Test complete packet crafting and sending workflow."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        # Craft packet
        packet = craft_tcp_packet(sample_packet_config)
        assert packet is not None
        
        # Send packet (with mocked response)
        with patch('utils.network_ops.sr1') as mock_sr1:
            mock_sr1.return_value = Mock()
            result = send_packet(packet, timeout=3)
            
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_full_scan_workflow(self):
        """Test complete port scanning workflow."""
        if not NMAP_AVAILABLE:
            pytest.skip("python-nmap not available")
        
        with patch('utils.network_ops.nmap.PortScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner_class.return_value = mock_scanner
            mock_scanner.all_hosts.return_value = ["localhost"]
            mock_scanner.__getitem__.return_value = {
                "tcp": {80: {"state": "open", "name": "http"}}
            }
            
            result = scan_port_range("localhost", "80", ScanType.TCP_SYN, 5)
            
            assert result.target == "localhost"
            assert result.total_ports == 1
            assert result.open_ports == 1

# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test error handling in network operations."""
    
    def test_craft_packet_invalid_config(self):
        """Test packet crafting with invalid configuration."""
        invalid_config = PacketConfig(
            source_ip="invalid-ip",
            destination_ip="invalid-ip",
            source_port=-1,
            destination_port=70000
        )
        
        # Should handle gracefully
        packet = craft_tcp_packet(invalid_config)
        # Result depends on Scapy availability
    
    def test_scan_port_invalid_host(self):
        """Test port scanning with invalid host."""
        if not NMAP_AVAILABLE:
            pytest.skip("python-nmap not available")
        
        with patch('utils.network_ops.nmap.PortScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner_class.return_value = mock_scanner
            mock_scanner.all_hosts.return_value = []
            
            result = scan_single_port("invalid-host", 80, "tcp", 5)
            
            assert result.state == "unknown"
    
    def test_sniff_packets_invalid_interface(self):
        """Test packet sniffing with invalid interface."""
        if not SCAPY_AVAILABLE:
            pytest.skip("Scapy not available")
        
        with patch('utils.network_ops.sniff') as mock_sniff:
            mock_sniff.side_effect = Exception("Invalid interface")
            
            results = sniff_packets(interface="invalid-interface", count=1, timeout=1)
            
            assert results == []

# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Performance tests for network operations."""
    
    def test_packet_crafting_performance(self, sample_packet_config):
        """Test packet crafting performance."""
        import time
        
        start_time = time.time()
        
        for _ in range(100):
            craft_tcp_packet(sample_packet_config)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 packet crafts in reasonable time
        assert duration < 10.0  # 10 seconds max
    
    def test_scan_performance(self):
        """Test port scanning performance."""
        if not NMAP_AVAILABLE:
            pytest.skip("python-nmap not available")
        
        import time
        
        with patch('utils.network_ops.nmap.PortScanner') as mock_scanner_class:
            mock_scanner = Mock()
            mock_scanner_class.return_value = mock_scanner
            mock_scanner.all_hosts.return_value = ["localhost"]
            mock_scanner.__getitem__.return_value = {"tcp": {}}
            
            start_time = time.time()
            result = scan_port_range("localhost", "1-100", ScanType.TCP_SYN, 1)
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Should complete scan in reasonable time
            assert duration < 5.0  # 5 seconds max

# =============================================================================
# SECURITY TESTS
# =============================================================================

class TestSecurity:
    """Security tests for network operations."""
    
    def test_private_ip_validation(self):
        """Test validation of private IP addresses."""
        from utils.network_ops import validate_target_address
        
        # Private IPs should be rejected
        assert not validate_target_address("192.168.1.1")
        assert not validate_target_address("10.0.0.1")
        assert not validate_target_address("172.16.0.1")
        assert not validate_target_address("127.0.0.1")
        assert not validate_target_address("localhost")
        
        # Public IPs should be allowed (for testing)
        assert validate_target_address("8.8.8.8")
        assert validate_target_address("1.1.1.1")
    
    def test_target_sanitization(self):
        """Test target address sanitization."""
        from utils.network_ops import sanitize_target_address
        
        # Test URL sanitization
        assert sanitize_target_address("https://example.com:443/path") == "example.com"
        assert sanitize_target_address("http://192.168.1.1:80/") == "192.168.1.1"
        assert sanitize_target_address("ftp://ftp.example.com:21/files") == "ftp.example.com"
        
        # Test port removal
        assert sanitize_target_address("example.com:8080") == "example.com"
        assert sanitize_target_address("192.168.1.1:22") == "192.168.1.1"

if __name__ == "__main__":
    pytest.main([__file__]) 