from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
BUFFER_SIZE = 1024

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from cybersecurity_security.attackers import (
from typing import Any, List, Dict, Optional
import logging
"""
Tests for Attackers Module

Tests brute force and exploit functionality.
WARNING: These tests are for authorized security testing only.
"""

    # Brute Forcers
    BruteForceRequest, BruteForceResult, BruteForceType,
    SSHBruteForceRequest, SSHBruteForceResult,
    HTTPBruteForceRequest, HTTPBruteForceResult,
    FTPBruteForceRequest, FTPBruteForceResult,
    perform_ssh_brute_force_async, perform_http_brute_force_async,
    perform_ftp_brute_force_async, perform_generic_brute_force_async,
    
    # Exploiters
    ExploitRequest, ExploitResult, ExploitType,
    BufferOverflowRequest, BufferOverflowResult,
    SQLInjectionExploitRequest, SQLInjectionExploitResult,
    XSSExploitRequest, XSSExploitResult,
    CommandInjectionRequest, CommandInjectionResult,
    perform_buffer_overflow_test_async, perform_sql_injection_exploit_async,
    perform_xss_exploit_async, perform_command_injection_exploit_async,
    perform_generic_exploit_async
)

class TestBruteForcers:
    """Test suite for brute force attackers."""
    
    async def test_brute_force_request_creation(self) -> Any:
        """Test BruteForceRequest creation."""
        request = BruteForceRequest(
            target_host="192.168.1.1",
            target_port=22,
            username_list=["admin", "root"],
            password_list=["password", "123456"],
            attack_type=BruteForceType.SSH,
            max_concurrent_attempts=5,
            timeout=10.0
        )
        assert request.target_host == "192.168.1.1"
        assert request.target_port == 22
        assert "admin" in request.username_list
        assert "password" in request.password_list
        assert request.attack_type == BruteForceType.SSH
    
    async def test_ssh_brute_force_request_creation(self) -> Any:
        """Test SSHBruteForceRequest creation."""
        request = SSHBruteForceRequest(
            target_host="192.168.1.1",
            target_port=22,
            username_list=["admin"],
            password_list=["password"],
            max_concurrent_attempts=3,
            timeout=10.0
        )
        assert request.target_host == "192.168.1.1"
        assert request.target_port == 22
        assert request.max_concurrent_attempts == 3
    
    async def test_http_brute_force_request_creation(self) -> Any:
        """Test HTTPBruteForceRequest creation."""
        request = HTTPBruteForceRequest(
            target_url="http://192.168.1.1",
            username_list=["admin"],
            password_list=["password"],
            auth_type="basic",
            max_concurrent_attempts=10,
            timeout=10.0
        )
        assert request.target_url == "http://192.168.1.1"
        assert request.auth_type == "basic"
        assert request.max_concurrent_attempts == 10
    
    async def test_ftp_brute_force_request_creation(self) -> Any:
        """Test FTPBruteForceRequest creation."""
        request = FTPBruteForceRequest(
            target_host="192.168.1.1",
            target_port=21,
            username_list=["admin"],
            password_list=["password"],
            max_concurrent_attempts=5,
            timeout=10.0
        )
        assert request.target_host == "192.168.1.1"
        assert request.target_port == 21
        assert request.max_concurrent_attempts == 5
    
    @pytest.mark.asyncio
    async def test_ssh_brute_force_async(self) -> Any:
        """Test SSH brute force attack."""
        with patch('paramiko.SSHClient') as mock_ssh:
            mock_ssh_instance = MagicMock()
            mock_ssh.return_value = mock_ssh_instance
            
            # Mock successful connection for one credential
            def mock_connect(host, port, username, password, timeout) -> Any:
                if username == "admin" and password == "password":
                    return None
                raise Exception("Authentication failed")
            
            mock_ssh_instance.connect.side_effect = mock_connect
            
            request = SSHBruteForceRequest(
                target_host="192.168.1.1",
                target_port=22,
                username_list=["admin", "root"],
                password_list=["password", "wrong"],
                max_concurrent_attempts=2,
                timeout=5.0
            )
            
            result = await perform_ssh_brute_force_async(request)
            
            assert result.target_host == "192.168.1.1"
            assert result.target_port == 22
            assert len(result.successful_credentials) == 1
            assert result.successful_credentials[0]["username"] == "admin"
            assert result.successful_credentials[0]["password"] == "password"
    
    @pytest.mark.asyncio
    async async def test_http_brute_force_async(self) -> Any:
        """Test HTTP brute force attack."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.status = 200
            
            # Mock successful authentication for one credential
            def mock_get(url, auth=None, timeout=None) -> Optional[Dict[str, Any]]:
                if auth and auth.login == "admin" and auth.password == "password":
                    mock_response.status = 200
                else:
                    mock_response.status = 401
                return mock_response
            
            mock_session.return_value.__aenter__.return_value.get.side_effect = mock_get
            
            request = HTTPBruteForceRequest(
                target_url="http://192.168.1.1",
                username_list=["admin", "root"],
                password_list=["password", "wrong"],
                auth_type="basic",
                max_concurrent_attempts=2,
                timeout=5.0
            )
            
            result = await perform_http_brute_force_async(request)
            
            assert result.target_url == "http://192.168.1.1"
            assert result.auth_type == "basic"
            assert len(result.successful_credentials) == 1
            assert result.successful_credentials[0]["username"] == "admin"
            assert result.successful_credentials[0]["password"] == "password"
    
    @pytest.mark.asyncio
    async def test_ftp_brute_force_async(self) -> Any:
        """Test FTP brute force attack."""
        with patch('ftplib.FTP') as mock_ftp:
            mock_ftp_instance = MagicMock()
            mock_ftp.return_value = mock_ftp_instance
            
            # Mock successful login for one credential
            def mock_login(username, password) -> Any:
                if username == "admin" and password == "password":
                    return None
                raise Exception("Authentication failed")
            
            mock_ftp_instance.login.side_effect = mock_login
            
            request = FTPBruteForceRequest(
                target_host="192.168.1.1",
                target_port=21,
                username_list=["admin", "root"],
                password_list=["password", "wrong"],
                max_concurrent_attempts=2,
                timeout=5.0
            )
            
            result = await perform_ftp_brute_force_async(request)
            
            assert result.target_host == "192.168.1.1"
            assert result.target_port == 21
            assert len(result.successful_credentials) == 1
            assert result.successful_credentials[0]["username"] == "admin"
            assert result.successful_credentials[0]["password"] == "password"

class TestExploiters:
    """Test suite for exploit attackers."""
    
    async def test_exploit_request_creation(self) -> Any:
        """Test ExploitRequest creation."""
        request = ExploitRequest(
            target_host="192.168.1.1",
            target_port=80,
            exploit_type=ExploitType.SQL_INJECTION,
            payload="' OR 1=1--",
            timeout=10.0
        )
        assert request.target_host == "192.168.1.1"
        assert request.target_port == 80
        assert request.exploit_type == ExploitType.SQL_INJECTION
        assert request.payload == "' OR 1=1--"
    
    async def test_buffer_overflow_request_creation(self) -> Any:
        """Test BufferOverflowRequest creation."""
        request = BufferOverflowRequest(
            target_host="192.168.1.1",
            target_port=9999,
            buffer_size=1024,
            shellcode="\\x90\\x90\\x90",
            timeout=10.0
        )
        assert request.target_host == "192.168.1.1"
        assert request.target_port == 9999
        assert request.buffer_size == 1024
        assert request.shellcode == "\\x90\\x90\\x90"
    
    async def test_sql_injection_exploit_request_creation(self) -> Any:
        """Test SQLInjectionExploitRequest creation."""
        request = SQLInjectionExploitRequest(
            target_url="http://192.168.1.1/vulnerable.php",
            parameter="id",
            injection_type="union",
            payload="' UNION SELECT 1,2,3--",
            timeout=10.0
        )
        assert request.target_url == "http://192.168.1.1/vulnerable.php"
        assert request.parameter == "id"
        assert request.injection_type == "union"
        assert request.payload == "' UNION SELECT 1,2,3--"
    
    async def test_xss_exploit_request_creation(self) -> Any:
        """Test XSSExploitRequest creation."""
        request = XSSExploitRequest(
            target_url="http://192.168.1.1/vulnerable.php",
            parameter="search",
            payload="<script>alert('XSS')</script>",
            xss_type="reflected",
            timeout=10.0
        )
        assert request.target_url == "http://192.168.1.1/vulnerable.php"
        assert request.parameter == "search"
        assert request.payload == "<script>alert('XSS')</script>"
        assert request.xss_type == "reflected"
    
    async def test_command_injection_request_creation(self) -> Any:
        """Test CommandInjectionRequest creation."""
        request = CommandInjectionRequest(
            target_url="http://192.168.1.1/vulnerable.php",
            parameter="cmd",
            payload="ls -la",
            injection_operator=";",
            timeout=10.0
        )
        assert request.target_url == "http://192.168.1.1/vulnerable.php"
        assert request.parameter == "cmd"
        assert request.payload == "ls -la"
        assert request.injection_operator == ";"
    
    @pytest.mark.asyncio
    async def test_buffer_overflow_test_async(self) -> Any:
        """Test buffer overflow exploit."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value = mock_sock
            
            # Mock successful connection and crash
            mock_sock.connect.return_value = None
            mock_sock.send.return_value = None
            mock_sock.recv.side_effect = socket.error("Connection reset")
            
            request = BufferOverflowRequest(
                target_host="192.168.1.1",
                target_port=9999,
                buffer_size=1024,
                timeout=5.0
            )
            
            result = await perform_buffer_overflow_test_async(request)
            
            assert result.target_host == "192.168.1.1"
            assert result.target_port == 9999
            assert result.buffer_size == 1024
            assert result.crash_detected is True
    
    @pytest.mark.asyncio
    async def test_sql_injection_exploit_async(self) -> Any:
        """Test SQL injection exploit."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.text = asyncio.coroutine(lambda: "UNION SELECT 1,2,3")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            request = SQLInjectionExploitRequest(
                target_url="http://192.168.1.1/vulnerable.php",
                parameter="id",
                injection_type="union",
                payload="' UNION SELECT 1,2,3--",
                timeout=5.0
            )
            
            result = await perform_sql_injection_exploit_async(request)
            
            assert result.target_url == "http://192.168.1.1/vulnerable.php"
            assert result.parameter == "id"
            assert result.injection_type == "union"
            assert result.is_successful is True
    
    @pytest.mark.asyncio
    async def test_xss_exploit_async(self) -> Any:
        """Test XSS exploit."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.text = asyncio.coroutine(lambda: "<script>alert('XSS')</script>")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            request = XSSExploitRequest(
                target_url="http://192.168.1.1/vulnerable.php",
                parameter="search",
                payload="<script>alert('XSS')</script>",
                xss_type="reflected",
                timeout=5.0
            )
            
            result = await perform_xss_exploit_async(request)
            
            assert result.target_url == "http://192.168.1.1/vulnerable.php"
            assert result.parameter == "search"
            assert result.payload == "<script>alert('XSS')</script>"
            assert result.is_successful is True
            assert result.payload_reflected is True
    
    @pytest.mark.asyncio
    async def test_command_injection_exploit_async(self) -> Any:
        """Test command injection exploit."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = MagicMock()
            mock_response.text = asyncio.coroutine(lambda: "root:x:0:0:root:/root:/bin/bash")
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            request = CommandInjectionRequest(
                target_url="http://192.168.1.1/vulnerable.php",
                parameter="cmd",
                payload="cat /etc/passwd",
                injection_operator=";",
                timeout=5.0
            )
            
            result = await perform_command_injection_exploit_async(request)
            
            assert result.target_url == "http://192.168.1.1/vulnerable.php"
            assert result.parameter == "cmd"
            assert result.payload == "cat /etc/passwd"
            assert result.injection_operator == ";"
            assert result.is_successful is True

class TestAttackersIntegration:
    """Integration tests for attackers modules."""
    
    @pytest.mark.asyncio
    async def test_multiple_attack_types(self) -> Any:
        """Test using multiple attack types together."""
        # Test SSH brute force
        ssh_request = SSHBruteForceRequest(
            target_host="192.168.1.1",
            target_port=22,
            username_list=["admin"],
            password_list=["password"],
            max_concurrent_attempts=1,
            timeout=5.0
        )
        
        # Test SQL injection exploit
        sql_request = SQLInjectionExploitRequest(
            target_url="http://192.168.1.1/vulnerable.php",
            parameter="id",
            injection_type="union",
            payload="' UNION SELECT 1,2,3--",
            timeout=5.0
        )
        
        # Run all attacks (with mocked dependencies)
        with patch('paramiko.SSHClient') as mock_ssh:
            mock_ssh_instance = MagicMock()
            mock_ssh.return_value = mock_ssh_instance
            mock_ssh_instance.connect.return_value = None
            
            with patch('aiohttp.ClientSession') as mock_session:
                mock_response = MagicMock()
                mock_response.text = asyncio.coroutine(lambda: "UNION SELECT 1,2,3")
                mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
                
                # Execute attacks
                ssh_result = await perform_ssh_brute_force_async(ssh_request)
                sql_result = await perform_sql_injection_exploit_async(sql_request)
                
                # Verify results
                assert ssh_result.target_host == "192.168.1.1"
                assert sql_result.target_url == "http://192.168.1.1/vulnerable.php" 