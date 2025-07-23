"""
Tests for Enumerators Module

Tests DNS, SMB, and SSH enumeration functionality.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from cybersecurity_security.enumerators import (
    # DNS Enumerator
    DNSEnumerationRequest, DNSEnumerationResult, DNSRecordType,
    enumerate_dns_records_async, enumerate_dns_subdomains_async,
    perform_dns_zone_transfer_async, check_dns_brute_force_async,
    
    # SMB Enumerator
    SMBEnumerationRequest, SMBEnumerationResult, SMBShareInfo, SMBShareType,
    enumerate_smb_shares_async, enumerate_smb_users_async,
    check_smb_null_sessions_async, enumerate_smb_policies_async,
    
    # SSH Enumerator
    SSHEnumerationRequest, SSHEnumerationResult, SSHServerInfo, SSHProtocolVersion,
    enumerate_ssh_versions_async, check_ssh_key_exchange_async,
    enumerate_ssh_algorithms_async, perform_ssh_brute_force_async
)

class TestDNSEnumerator:
    """Test suite for DNS enumerator."""
    
    def test_dns_enumeration_request_creation(self):
        """Test DNSEnumerationRequest creation."""
        request = DNSEnumerationRequest(
            target_domain="example.com",
            record_types=[DNSRecordType.A, DNSRecordType.MX],
            nameservers=["8.8.8.8"],
            timeout=10.0
        )
        assert request.target_domain == "example.com"
        assert DNSRecordType.A in request.record_types
        assert DNSRecordType.MX in request.record_types
        assert "8.8.8.8" in request.nameservers
        assert request.timeout == 10.0
    
    def test_dns_enumeration_request_invalid_domain(self):
        """Test DNSEnumerationRequest with invalid domain."""
        with pytest.raises(ValueError, match="Invalid domain format"):
            DNSEnumerationRequest(target_domain="invalid")
    
    def test_dns_enumeration_request_invalid_timeout(self):
        """Test DNSEnumerationRequest with invalid timeout."""
        with pytest.raises(ValueError):
            DNSEnumerationRequest(
                target_domain="example.com",
                timeout=0.5  # Should be >= 1.0
            )
    
    @pytest.mark.asyncio
    async def test_enumerate_dns_records_async(self):
        """Test DNS record enumeration."""
        with patch('dns.resolver.Resolver') as mock_resolver:
            mock_resolver_instance = MagicMock()
            mock_resolver.return_value = mock_resolver_instance
            
            # Mock DNS response
            mock_answer = MagicMock()
            mock_answer.ttl = 300
            mock_answer.__str__ = lambda self: "192.168.1.1"
            
            mock_resolver_instance.resolve.return_value = [mock_answer]
            
            request = DNSEnumerationRequest(
                target_domain="example.com",
                record_types=[DNSRecordType.A],
                timeout=10.0
            )
            
            result = await enumerate_dns_records_async(request)
            
            assert result.target_domain == "example.com"
            assert len(result.records_found) == 1
            assert result.records_found[0].record_type == DNSRecordType.A
            assert result.records_found[0].value == "192.168.1.1"
            assert result.total_queries >= 1
    
    @pytest.mark.asyncio
    async def test_enumerate_dns_subdomains_async(self):
        """Test DNS subdomain enumeration."""
        with patch('socket.gethostbyname') as mock_gethostbyname:
            # Mock successful resolution for some subdomains
            def mock_resolve(hostname):
                if hostname in ["www.example.com", "mail.example.com"]:
                    return "192.168.1.1"
                raise socket.gaierror("Name or service not known")
            
            mock_gethostbyname.side_effect = mock_resolve
            
            request = SubdomainEnumerationRequest(
                target_domain="example.com",
                wordlist=["www", "mail", "ftp", "admin"],
                use_common_wordlist=False
            )
            
            result = await enumerate_dns_subdomains_async(request)
            
            assert result.target_domain == "example.com"
            assert len(result.discovered_subdomains) == 2
            assert "www.example.com" in result.discovered_subdomains
            assert "mail.example.com" in result.discovered_subdomains
            assert result.total_subdomains_checked == 4

class TestSMBEnumerator:
    """Test suite for SMB enumerator."""
    
    def test_smb_enumeration_request_creation(self):
        """Test SMBEnumerationRequest creation."""
        request = SMBEnumerationRequest(
            target_host="192.168.1.1",
            target_port=445,
            username="admin",
            password="password",
            domain="WORKGROUP",
            timeout=10.0
        )
        assert request.target_host == "192.168.1.1"
        assert request.target_port == 445
        assert request.username == "admin"
        assert request.password == "password"
        assert request.domain == "WORKGROUP"
        assert request.timeout == 10.0
    
    def test_smb_enumeration_request_invalid_host(self):
        """Test SMBEnumerationRequest with invalid host."""
        with pytest.raises(ValueError, match="Target host cannot be empty"):
            SMBEnumerationRequest(target_host="")
    
    def test_smb_enumeration_request_invalid_port(self):
        """Test SMBEnumerationRequest with invalid port."""
        with pytest.raises(ValueError):
            SMBEnumerationRequest(
                target_host="192.168.1.1",
                target_port=70000  # Should be <= 65535
            )
    
    @pytest.mark.asyncio
    async def test_enumerate_smb_shares_async(self):
        """Test SMB share enumeration."""
        with patch('socket.create_connection') as mock_connection:
            mock_sock = MagicMock()
            mock_connection.return_value = mock_sock
            
            # Mock SMB response with common shares
            mock_sock.recv.return_value = b'SMB\xff\x72\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00IPC$ADMIN$C$'
            
            request = SMBEnumerationRequest(
                target_host="192.168.1.1",
                target_port=445,
                timeout=10.0
            )
            
            shares = await enumerate_smb_shares_async(request)
            
            assert len(shares) >= 1
            share_names = [share.share_name for share in shares]
            assert "IPC$" in share_names
    
    @pytest.mark.asyncio
    async def test_check_smb_null_sessions_async(self):
        """Test SMB null session checking."""
        with patch('socket.create_connection') as mock_connection:
            mock_sock = MagicMock()
            mock_connection.return_value = mock_sock
            
            # Mock successful null session response
            mock_sock.recv.return_value = b'STATUS_SUCCESS'
            
            request = SMBEnumerationRequest(
                target_host="192.168.1.1",
                target_port=445,
                timeout=10.0
            )
            
            result = await check_smb_null_sessions_async(request)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_enumerate_smb_async(self):
        """Test comprehensive SMB enumeration."""
        with patch('cybersecurity_security.enumerators.smb_enumerator.enumerate_smb_shares_async') as mock_shares:
            mock_shares.return_value = [
                SMBShareInfo(
                    share_name="IPC$",
                    share_type=SMBShareType.IPC,
                    share_comment="Remote IPC",
                    is_accessible=True
                )
            ]
            
            with patch('cybersecurity_security.enumerators.smb_enumerator.enumerate_smb_users_async') as mock_users:
                mock_users.return_value = [
                    SMBUserInfo(
                        username="Administrator",
                        full_name="Administrator",
                        description="Built-in administrator account",
                        is_disabled=False,
                        is_locked=False
                    )
                ]
                
                with patch('cybersecurity_security.enumerators.smb_enumerator.check_smb_null_sessions_async') as mock_null:
                    mock_null.return_value = False
                    
                    with patch('cybersecurity_security.enumerators.smb_enumerator.enumerate_smb_policies_async') as mock_policies:
                        mock_policies.return_value = []
                        
                        request = SMBEnumerationRequest(
                            target_host="192.168.1.1",
                            target_port=445,
                            timeout=10.0
                        )
                        
                        result = await enumerate_smb_async(request)
                        
                        assert result.target_host == "192.168.1.1"
                        assert result.target_port == 445
                        assert len(result.shares_found) == 1
                        assert len(result.users_found) == 1
                        assert result.null_session_allowed is False
                        assert result.total_connections >= 0

class TestSSHEnumerator:
    """Test suite for SSH enumerator."""
    
    def test_ssh_enumeration_request_creation(self):
        """Test SSHEnumerationRequest creation."""
        request = SSHEnumerationRequest(
            target_host="192.168.1.1",
            target_port=22,
            timeout=10.0,
            perform_brute_force=True,
            username_list=["root", "admin"],
            password_list=["password", "123456"]
        )
        assert request.target_host == "192.168.1.1"
        assert request.target_port == 22
        assert request.timeout == 10.0
        assert request.perform_brute_force is True
        assert "root" in request.username_list
        assert "password" in request.password_list
    
    def test_ssh_enumeration_request_invalid_host(self):
        """Test SSHEnumerationRequest with invalid host."""
        with pytest.raises(ValueError, match="Target host cannot be empty"):
            SSHEnumerationRequest(target_host="")
    
    def test_ssh_enumeration_request_invalid_port(self):
        """Test SSHEnumerationRequest with invalid port."""
        with pytest.raises(ValueError):
            SSHEnumerationRequest(
                target_host="192.168.1.1",
                target_port=70000  # Should be <= 65535
            )
    
    @pytest.mark.asyncio
    async def test_enumerate_ssh_versions_async(self):
        """Test SSH version enumeration."""
        with patch('socket.create_connection') as mock_connection:
            mock_sock = MagicMock()
            mock_connection.return_value = mock_sock
            
            # Mock SSH banner response
            mock_sock.recv.return_value = b'SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n'
            
            request = SSHEnumerationRequest(
                target_host="192.168.1.1",
                target_port=22,
                timeout=10.0
            )
            
            server_info = await enumerate_ssh_versions_async(request)
            
            assert server_info.protocol_version == SSHProtocolVersion.SSH2
            assert "OpenSSH" in server_info.software_version
            assert "SSH-2.0-OpenSSH" in server_info.banner
    
    @pytest.mark.asyncio
    async def test_check_ssh_key_exchange_async(self):
        """Test SSH key exchange analysis."""
        with patch('cybersecurity_security.enumerators.ssh_enumerator.enumerate_ssh_versions_async') as mock_version:
            mock_version.return_value = SSHServerInfo(
                protocol_version=SSHProtocolVersion.SSH2,
                software_version="OpenSSH_8.2p1",
                banner="SSH-2.0-OpenSSH_8.2p1",
                key_exchange_algorithms=["curve25519-sha256@libssh.org", "diffie-hellman-group14-sha1"]
            )
            
            request = SSHEnumerationRequest(
                target_host="192.168.1.1",
                target_port=22,
                timeout=10.0
            )
            
            result = await check_ssh_key_exchange_async(request)
            
            assert "supported_algorithms" in result
            assert "weak_algorithms" in result
            assert "strong_algorithms" in result
            assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_enumerate_ssh_algorithms_async(self):
        """Test SSH algorithm enumeration."""
        with patch('cybersecurity_security.enumerators.ssh_enumerator.enumerate_ssh_versions_async') as mock_version:
            mock_version.return_value = SSHServerInfo(
                protocol_version=SSHProtocolVersion.SSH2,
                software_version="OpenSSH_8.2p1",
                banner="SSH-2.0-OpenSSH_8.2p1",
                encryption_algorithms=["aes128-ctr", "aes256-ctr", "3des-cbc"],
                mac_algorithms=["hmac-sha2-256", "hmac-md5"]
            )
            
            request = SSHEnumerationRequest(
                target_host="192.168.1.1",
                target_port=22,
                timeout=10.0
            )
            
            result = await enumerate_ssh_algorithms_async(request)
            
            assert "encryption" in result
            assert "mac" in result
            assert "key_exchange" in result
            assert "host_key" in result
            assert "compression" in result
    
    @pytest.mark.asyncio
    async def test_perform_ssh_brute_force_async(self):
        """Test SSH brute force enumeration."""
        with patch('socket.create_connection') as mock_connection:
            mock_sock = MagicMock()
            mock_connection.return_value = mock_sock
            
            # Mock SSH responses
            mock_sock.recv.return_value = b'SSH-2.0-OpenSSH_8.2p1\r\n'
            
            request = SSHEnumerationRequest(
                target_host="192.168.1.1",
                target_port=22,
                timeout=10.0,
                perform_brute_force=True,
                username_list=["root"],
                password_list=["password"]
            )
            
            results = await perform_ssh_brute_force_async(request)
            
            assert len(results) == 1
            assert results[0].username == "root"
            assert results[0].password == "password"
            assert results[0].authentication_time >= 0
    
    @pytest.mark.asyncio
    async def test_enumerate_ssh_async(self):
        """Test comprehensive SSH enumeration."""
        with patch('cybersecurity_security.enumerators.ssh_enumerator.enumerate_ssh_versions_async') as mock_version:
            mock_version.return_value = SSHServerInfo(
                protocol_version=SSHProtocolVersion.SSH2,
                software_version="OpenSSH_8.2p1",
                banner="SSH-2.0-OpenSSH_8.2p1"
            )
            
            with patch('cybersecurity_security.enumerators.ssh_enumerator.check_ssh_key_exchange_async') as mock_kex:
                mock_kex.return_value = {
                    "supported_algorithms": ["curve25519-sha256@libssh.org"],
                    "weak_algorithms": [],
                    "strong_algorithms": ["curve25519-sha256@libssh.org"],
                    "recommendations": []
                }
                
                with patch('cybersecurity_security.enumerators.ssh_enumerator.enumerate_ssh_algorithms_async') as mock_alg:
                    mock_alg.return_value = {
                        "encryption": {"supported": ["aes128-ctr"], "weak": [], "strong": ["aes128-ctr"]},
                        "mac": {"supported": ["hmac-sha2-256"], "weak": [], "strong": ["hmac-sha2-256"]}
                    }
                    
                    with patch('cybersecurity_security.enumerators.ssh_enumerator.perform_ssh_brute_force_async') as mock_bf:
                        mock_bf.return_value = []
                        
                        request = SSHEnumerationRequest(
                            target_host="192.168.1.1",
                            target_port=22,
                            timeout=10.0
                        )
                        
                        result = await enumerate_ssh_async(request)
                        
                        assert result.target_host == "192.168.1.1"
                        assert result.target_port == 22
                        assert result.server_info.protocol_version == SSHProtocolVersion.SSH2
                        assert len(result.brute_force_results) == 0
                        assert "security_assessment" in result.security_assessment

class TestEnumeratorIntegration:
    """Integration tests for enumerator modules."""
    
    @pytest.mark.asyncio
    async def test_multiple_enumerator_types(self):
        """Test using multiple enumerator types together."""
        # Test DNS enumeration
        dns_request = DNSEnumerationRequest(
            target_domain="example.com",
            record_types=[DNSRecordType.A, DNSRecordType.MX],
            timeout=10.0
        )
        
        # Test SMB enumeration
        smb_request = SMBEnumerationRequest(
            target_host="192.168.1.1",
            target_port=445,
            timeout=10.0
        )
        
        # Test SSH enumeration
        ssh_request = SSHEnumerationRequest(
            target_host="192.168.1.1",
            target_port=22,
            timeout=10.0
        )
        
        # Run all enumerations (with mocked dependencies)
        with patch('dns.resolver.Resolver') as mock_dns:
            mock_dns_instance = MagicMock()
            mock_dns.return_value = mock_dns_instance
            mock_answer = MagicMock()
            mock_answer.ttl = 300
            mock_answer.__str__ = lambda self: "192.168.1.1"
            mock_dns_instance.resolve.return_value = [mock_answer]
            
            with patch('cybersecurity_security.enumerators.smb_enumerator.enumerate_smb_shares_async') as mock_smb:
                mock_smb.return_value = []
                
                with patch('cybersecurity_security.enumerators.ssh_enumerator.enumerate_ssh_versions_async') as mock_ssh:
                    mock_ssh.return_value = SSHServerInfo(
                        protocol_version=SSHProtocolVersion.SSH2,
                        software_version="OpenSSH_8.2p1",
                        banner="SSH-2.0-OpenSSH_8.2p1"
                    )
                    
                    # Execute enumerations
                    dns_result = await enumerate_dns_records_async(dns_request)
                    smb_result = await enumerate_smb_async(smb_request)
                    ssh_result = await enumerate_ssh_async(ssh_request)
                    
                    # Verify results
                    assert dns_result.target_domain == "example.com"
                    assert smb_result.target_host == "192.168.1.1"
                    assert ssh_result.target_host == "192.168.1.1" 