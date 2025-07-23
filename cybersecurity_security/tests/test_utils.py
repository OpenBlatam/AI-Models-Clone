"""
Tests for Utils Module

Tests crypto helpers and network helpers functionality.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from cybersecurity_security.utils import (
    # Crypto Helpers
    CryptoRequest, CryptoResult, CryptoOperation,
    HashAlgorithm, EncryptionAlgorithm,
    perform_hash_async, perform_encryption_async, perform_decryption_async,
    generate_key_async, verify_signature_async, create_digital_signature_async,
    generate_random_bytes_async, derive_key_from_password_async,
    encrypt_file_async, decrypt_file_async, hash_file_async, verify_file_integrity_async,
    
    # Network Helpers
    NetworkRequest, NetworkResult, NetworkOperation,
    perform_dns_lookup_async, perform_http_request_async, perform_https_request_async,
    check_port_availability_async, resolve_hostname_async, get_network_info_async,
    perform_traceroute_async, check_connectivity_async, get_ssl_certificate_async,
    perform_whois_lookup_async, get_geolocation_async, validate_ip_address,
    validate_domain_name, get_mac_address_async, perform_arp_scan_async
)

class TestCryptoHelpers:
    """Test suite for crypto helpers."""
    
    def test_crypto_request_creation(self):
        """Test CryptoRequest creation."""
        request = CryptoRequest(
            operation=CryptoOperation.HASH,
            data="test data",
            algorithm=HashAlgorithm.SHA256
        )
        assert request.operation == CryptoOperation.HASH
        assert request.data == "test data"
        assert request.algorithm == HashAlgorithm.SHA256
    
    @pytest.mark.asyncio
    async def test_perform_hash_async(self):
        """Test hash operation."""
        test_data = "test data"
        result = await perform_hash_async(test_data, HashAlgorithm.SHA256)
        
        assert result.operation == CryptoOperation.HASH
        assert result.algorithm == HashAlgorithm.SHA256
        assert result.input_data == test_data
        assert result.success is True
        assert len(result.output_data) > 0
    
    @pytest.mark.asyncio
    async def test_perform_hash_async_different_algorithms(self):
        """Test hash operation with different algorithms."""
        test_data = "test data"
        
        algorithms = [
            HashAlgorithm.MD5,
            HashAlgorithm.SHA1,
            HashAlgorithm.SHA256,
            HashAlgorithm.SHA512
        ]
        
        for algorithm in algorithms:
            result = await perform_hash_async(test_data, algorithm)
            assert result.success is True
            assert result.algorithm == algorithm
            assert len(result.output_data) > 0
    
    @pytest.mark.asyncio
    async def test_perform_encryption_async(self):
        """Test encryption operation."""
        test_data = "secret message"
        key = "mysecretkey1234567890123456789012"  # 32 bytes for AES-256
        
        result = await perform_encryption_async(test_data, key, EncryptionAlgorithm.AES_256_GCM)
        
        assert result.operation == CryptoOperation.ENCRYPT
        assert result.algorithm == EncryptionAlgorithm.AES_256_GCM
        assert result.input_data == test_data
        assert result.success is True
        assert len(result.output_data) > 0
    
    @pytest.mark.asyncio
    async def test_perform_decryption_async(self):
        """Test decryption operation."""
        test_data = "secret message"
        key = "mysecretkey1234567890123456789012"  # 32 bytes for AES-256
        
        # First encrypt
        encrypt_result = await perform_encryption_async(test_data, key, EncryptionAlgorithm.AES_256_GCM)
        assert encrypt_result.success is True
        
        # Then decrypt
        decrypt_result = await perform_decryption_async(encrypt_result.output_data, key, EncryptionAlgorithm.AES_256_GCM)
        
        assert decrypt_result.operation == CryptoOperation.DECRYPT
        assert decrypt_result.algorithm == EncryptionAlgorithm.AES_256_GCM
        assert decrypt_result.success is True
        assert decrypt_result.output_data == test_data
    
    @pytest.mark.asyncio
    async def test_generate_key_async(self):
        """Test key generation."""
        result = await generate_key_async(EncryptionAlgorithm.AES_256_GCM)
        
        assert result.operation == CryptoOperation.KEY_GENERATION
        assert result.algorithm == EncryptionAlgorithm.AES_256_GCM
        assert result.success is True
        assert len(result.output_data) > 0
    
    @pytest.mark.asyncio
    async def test_derive_key_from_password_async(self):
        """Test key derivation from password."""
        password = "mysecretpassword"
        salt = "mysalt123"
        
        result = await derive_key_from_password_async(password, salt, iterations=1000)
        
        assert result.operation == CryptoOperation.KEY_DERIVATION
        assert result.success is True
        assert "key" in result.output_data
        assert "salt" in result.output_data
        assert result.output_data["iterations"] == 1000
    
    @pytest.mark.asyncio
    async def test_generate_random_bytes_async(self):
        """Test random bytes generation."""
        result = await generate_random_bytes_async(32)
        
        assert result.operation == CryptoOperation.KEY_GENERATION
        assert result.success is True
        assert len(result.output_data) > 0
    
    @pytest.mark.asyncio
    async def test_create_digital_signature_async(self):
        """Test digital signature creation."""
        test_data = "message to sign"
        
        # Generate RSA key pair
        key_result = await generate_key_async(EncryptionAlgorithm.RSA_2048)
        assert key_result.success is True
        
        private_key = key_result.output_data["private_key"]
        
        # Create signature
        signature_result = await create_digital_signature_async(test_data, private_key)
        
        assert signature_result.operation == CryptoOperation.SIGN
        assert signature_result.algorithm == EncryptionAlgorithm.RSA_2048
        assert signature_result.success is True
        assert len(signature_result.output_data) > 0
    
    @pytest.mark.asyncio
    async def test_verify_signature_async(self):
        """Test signature verification."""
        test_data = "message to sign"
        
        # Generate RSA key pair
        key_result = await generate_key_async(EncryptionAlgorithm.RSA_2048)
        assert key_result.success is True
        
        private_key = key_result.output_data["private_key"]
        public_key = key_result.output_data["public_key"]
        
        # Create signature
        signature_result = await create_digital_signature_async(test_data, private_key)
        assert signature_result.success is True
        
        # Verify signature
        verify_result = await verify_signature_async(test_data, signature_result.output_data, public_key)
        
        assert verify_result.operation == CryptoOperation.VERIFY
        assert verify_result.algorithm == EncryptionAlgorithm.RSA_2048
        assert verify_result.success is True
        assert verify_result.output_data is True

class TestNetworkHelpers:
    """Test suite for network helpers."""
    
    def test_network_request_creation(self):
        """Test NetworkRequest creation."""
        request = NetworkRequest(
            operation=NetworkOperation.DNS_LOOKUP,
            target="example.com",
            timeout=10.0
        )
        assert request.operation == NetworkOperation.DNS_LOOKUP
        assert request.target == "example.com"
        assert request.timeout == 10.0
    
    @pytest.mark.asyncio
    async def test_perform_dns_lookup_async(self):
        """Test DNS lookup."""
        with patch('socket.gethostbyname_ex') as mock_gethostbyname:
            mock_gethostbyname.return_value = ("example.com", [], ["93.184.216.34"])
            
            result = await perform_dns_lookup_async("example.com")
            
            assert result.operation == NetworkOperation.DNS_LOOKUP
            assert result.target == "example.com"
            assert result.success is True
            assert "records" in result.result_data
    
    @pytest.mark.asyncio
    async def test_perform_http_request_async(self):
        """Test HTTP request."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = asyncio.coroutine(lambda: "Hello World")
            mock_response.headers = {"content-type": "text/html"}
            
            mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
            
            result = await perform_http_request_async("http://example.com")
            
            assert result.operation == NetworkOperation.HTTP_REQUEST
            assert result.target == "http://example.com"
            assert result.success is True
            assert result.result_data["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_perform_https_request_async(self):
        """Test HTTPS request."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = asyncio.coroutine(lambda: "Hello World")
            mock_response.headers = {"content-type": "text/html"}
            mock_response.connection = None
            
            mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
            
            result = await perform_https_request_async("https://example.com")
            
            assert result.operation == NetworkOperation.HTTPS_REQUEST
            assert result.target == "https://example.com"
            assert result.success is True
            assert result.result_data["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_check_port_availability_async(self):
        """Test port availability check."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            mock_sock.connect_ex.return_value = 0  # Port is open
            
            result = await check_port_availability_async("localhost", 80)
            
            assert result.operation == NetworkOperation.PORT_CHECK
            assert result.target == "localhost:80"
            assert result.success is True
            assert result.result_data["is_open"] is True
    
    @pytest.mark.asyncio
    async def test_resolve_hostname_async(self):
        """Test hostname resolution."""
        with patch('socket.gethostbyname') as mock_gethostbyname, \
             patch('socket.gethostbyaddr') as mock_gethostbyaddr:
            
            mock_gethostbyname.return_value = "192.168.1.1"
            mock_gethostbyaddr.return_value = ("example.com", [], ["192.168.1.1"])
            
            result = await resolve_hostname_async("example.com")
            
            assert result.operation == NetworkOperation.HOSTNAME_RESOLVE
            assert result.target == "example.com"
            assert result.success is True
            assert result.result_data["ip_address"] == "192.168.1.1"
    
    @pytest.mark.asyncio
    async def test_get_network_info_async(self):
        """Test network info retrieval."""
        with patch('socket.gethostbyname') as mock_gethostbyname:
            mock_gethostbyname.return_value = "192.168.1.1"
            
            result = await get_network_info_async("example.com")
            
            assert result.operation == NetworkOperation.NETWORK_INFO
            assert result.target == "example.com"
            assert result.success is True
            assert "ip_address" in result.result_data
    
    @pytest.mark.asyncio
    async def test_check_connectivity_async(self):
        """Test connectivity check."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            mock_sock.connect_ex.return_value = 0  # Port is open
            
            result = await check_connectivity_async("localhost", 80)
            
            assert result.operation == NetworkOperation.CONNECTIVITY_CHECK
            assert result.target == "localhost:80"
            assert result.success is True
            assert "port_check" in result.result_data
    
    @pytest.mark.asyncio
    async def test_get_ssl_certificate_async(self):
        """Test SSL certificate retrieval."""
        with patch('socket.create_connection') as mock_connect, \
             patch('ssl.create_default_context') as mock_context:
            
            mock_sock = MagicMock()
            mock_ssock = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_sock
            mock_context.return_value.wrap_socket.return_value.__enter__.return_value = mock_ssock
            
            # Mock certificate data
            mock_ssock.getpeercert.return_value = {
                'subject': [('CN', 'example.com')],
                'issuer': [('CN', 'Test CA')],
                'version': 3,
                'serialNumber': '123456789',
                'notBefore': 'Jan 01 00:00:00 2023 GMT',
                'notAfter': 'Jan 01 00:00:00 2024 GMT'
            }
            mock_ssock.cipher.return_value = ('AES256-GCM-SHA384', 'TLSv1.2', 256)
            mock_ssock.version.return_value = 'TLSv1.2'
            
            result = await get_ssl_certificate_async("example.com", 443)
            
            assert result.operation == NetworkOperation.SSL_CERTIFICATE
            assert result.target == "example.com:443"
            assert result.success is True
            assert "subject" in result.result_data
    
    @pytest.mark.asyncio
    async def test_perform_whois_lookup_async(self):
        """Test WHOIS lookup."""
        with patch('whois.whois') as mock_whois:
            mock_whois.return_value = MagicMock(
                domain_name=['example.com'],
                registrar='Test Registrar',
                creation_date='2020-01-01',
                expiration_date='2025-01-01',
                updated_date='2023-01-01',
                name_servers=['ns1.example.com'],
                status=['active'],
                emails=['admin@example.com'],
                dnssec='unsigned'
            )
            
            result = await perform_whois_lookup_async("example.com")
            
            assert result.operation == NetworkOperation.WHOIS_LOOKUP
            assert result.target == "example.com"
            assert result.success is True
            assert "registrar" in result.result_data
    
    @pytest.mark.asyncio
    async def test_get_geolocation_async(self):
        """Test geolocation lookup."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = asyncio.coroutine(lambda: {
                "country": "United States",
                "city": "New York",
                "lat": 40.7128,
                "lon": -74.0060
            })
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await get_geolocation_async("8.8.8.8")
            
            assert result.operation == NetworkOperation.GEOLOCATION
            assert result.target == "8.8.8.8"
            assert result.success is True
            assert "country" in result.result_data
    
    def test_validate_ip_address(self):
        """Test IP address validation."""
        assert validate_ip_address("192.168.1.1") is True
        assert validate_ip_address("2001:db8::1") is True
        assert validate_ip_address("invalid") is False
        assert validate_ip_address("256.256.256.256") is False
    
    def test_validate_domain_name(self):
        """Test domain name validation."""
        assert validate_domain_name("example.com") is True
        assert validate_domain_name("sub.example.com") is True
        assert validate_domain_name("invalid-domain") is False
        assert validate_domain_name("") is False
    
    @pytest.mark.asyncio
    async def test_get_mac_address_async(self):
        """Test MAC address retrieval."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (
                "192.168.1.1 at 00:11:22:33:44:55",
                ""
            )
            mock_popen.return_value = mock_process
            
            result = await get_mac_address_async("192.168.1.1")
            
            assert result.operation == NetworkOperation.ARP_SCAN
            assert result.target == "192.168.1.1"
            assert result.success is True
            assert "mac_address" in result.result_data
    
    @pytest.mark.asyncio
    async def test_perform_arp_scan_async(self):
        """Test ARP scan."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.communicate.return_value = (
                "192.168.1.1 at 00:11:22:33:44:55\n192.168.1.2 at 00:11:22:33:44:56",
                ""
            )
            mock_popen.return_value = mock_process
            
            result = await perform_arp_scan_async("192.168.1.0/24")
            
            assert result.operation == NetworkOperation.ARP_SCAN
            assert result.target == "192.168.1.0/24"
            assert result.success is True
            assert "devices" in result.result_data

class TestUtilsIntegration:
    """Integration tests for utils modules."""
    
    @pytest.mark.asyncio
    async def test_crypto_workflow(self):
        """Test complete crypto workflow."""
        # Generate key
        key_result = await generate_key_async(EncryptionAlgorithm.AES_256_GCM)
        assert key_result.success is True
        
        # Encrypt data
        test_data = "secret message"
        encrypt_result = await perform_encryption_async(test_data, key_result.output_data)
        assert encrypt_result.success is True
        
        # Decrypt data
        decrypt_result = await perform_decryption_async(encrypt_result.output_data, key_result.output_data)
        assert decrypt_result.success is True
        assert decrypt_result.output_data == test_data
    
    @pytest.mark.asyncio
    async def test_network_workflow(self):
        """Test complete network workflow."""
        # DNS lookup
        with patch('socket.gethostbyname_ex') as mock_gethostbyname:
            mock_gethostbyname.return_value = ("example.com", [], ["93.184.216.34"])
            
            dns_result = await perform_dns_lookup_async("example.com")
            assert dns_result.success is True
            
            # Get network info
            network_result = await get_network_info_async("example.com")
            assert network_result.success is True
            
            # Check connectivity
            with patch('socket.socket') as mock_socket:
                mock_sock = MagicMock()
                mock_socket.return_value = mock_sock
                mock_sock.connect_ex.return_value = 0
                
                connectivity_result = await check_connectivity_async("example.com", 80)
                assert connectivity_result.success is True
    
    @pytest.mark.asyncio
    async def test_file_crypto_operations(self):
        """Test file crypto operations."""
        test_content = "This is a test file content"
        test_file = "test_file.txt"
        
        # Create test file
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        try:
            # Hash file
            hash_result = await hash_file_async(test_file)
            assert hash_result.success is True
            
            # Encrypt file
            key = "mysecretkey1234567890123456789012"
            encrypt_result = await encrypt_file_async(test_file, key)
            assert encrypt_result.success is True
            
            # Decrypt file
            decrypt_result = await decrypt_file_async(encrypt_result.output_data, key)
            assert decrypt_result.success is True
            
            # Verify file integrity
            verify_result = await verify_file_integrity_async(test_file, hash_result.output_data)
            assert verify_result.success is True
            
        finally:
            # Cleanup
            import os
            if os.path.exists(test_file):
                os.remove(test_file)
            if os.path.exists(f"{test_file}.encrypted"):
                os.remove(f"{test_file}.encrypted")
            if os.path.exists(f"{test_file}.decrypted"):
                os.remove(f"{test_file}.decrypted")
    
    @pytest.mark.asyncio
    async def test_multiple_network_operations(self):
        """Test multiple network operations together."""
        with patch('socket.gethostbyname') as mock_gethostbyname, \
             patch('socket.socket') as mock_socket, \
             patch('aiohttp.ClientSession') as mock_session:
            
            mock_gethostbyname.return_value = "192.168.1.1"
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            mock_sock.connect_ex.return_value = 0
            
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.text = asyncio.coroutine(lambda: "Hello World")
            mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
            
            # Run multiple operations
            results = await asyncio.gather(
                perform_dns_lookup_async("example.com"),
                check_port_availability_async("localhost", 80),
                perform_http_request_async("http://example.com"),
                return_exceptions=True
            )
            
            # Check results
            for result in results:
                if isinstance(result, Exception):
                    continue
                assert result.success is True 