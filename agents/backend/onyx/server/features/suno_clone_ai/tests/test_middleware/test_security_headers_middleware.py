"""
Comprehensive Unit Tests for Security Headers Middleware

Tests cover security headers middleware with diverse test cases
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import Request

from middleware.security_headers_middleware import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """Test cases for SecurityHeadersMiddleware class"""
    
    def test_security_headers_middleware_init_defaults(self):
        """Test initializing middleware with defaults"""
        app = Mock()
        middleware = SecurityHeadersMiddleware(app)
        
        assert middleware.strict_transport_security is not None
        assert middleware.content_security_policy is not None
        assert middleware.x_content_type_options == "nosniff"
        assert middleware.x_frame_options == "DENY"
    
    def test_security_headers_middleware_init_custom(self):
        """Test initializing middleware with custom headers"""
        app = Mock()
        middleware = SecurityHeadersMiddleware(
            app,
            x_frame_options="SAMEORIGIN",
            referrer_policy="no-referrer"
        )
        
        assert middleware.x_frame_options == "SAMEORIGIN"
        assert middleware.referrer_policy == "no-referrer"
    
    @pytest.mark.asyncio
    async def test_dispatch_adds_security_headers(self):
        """Test dispatch adds all security headers"""
        app = Mock()
        middleware = SecurityHeadersMiddleware(app)
        
        request = Mock(spec=Request)
        request.headers = {}
        
        response = Mock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == response
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
    
    @pytest.mark.asyncio
    async def test_dispatch_removes_server_header(self):
        """Test dispatch removes server header"""
        app = Mock()
        middleware = SecurityHeadersMiddleware(app)
        
        request = Mock(spec=Request)
        request.headers = {}
        
        response = Mock()
        response.headers = {"server": "nginx/1.18.0"}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert "server" not in response.headers
    
    @pytest.mark.asyncio
    async def test_dispatch_adds_request_id(self):
        """Test dispatch adds X-Request-ID header"""
        app = Mock()
        middleware = SecurityHeadersMiddleware(app)
        
        request = Mock(spec=Request)
        request.headers = {}
        
        response = Mock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] is not None
    
    @pytest.mark.asyncio
    async def test_dispatch_uses_existing_request_id(self):
        """Test dispatch uses existing X-Request-ID if present"""
        app = Mock()
        middleware = SecurityHeadersMiddleware(app)
        
        request = Mock(spec=Request)
        request.headers = {"X-Request-ID": "existing-id-123"}
        
        response = Mock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert response.headers["X-Request-ID"] == "existing-id-123"
    
    @pytest.mark.asyncio
    async def test_dispatch_all_security_headers_present(self):
        """Test all security headers are present in response"""
        app = Mock()
        middleware = SecurityHeadersMiddleware(app)
        
        request = Mock(spec=Request)
        request.headers = {}
        
        response = Mock()
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        await middleware.dispatch(request, call_next)
        
        required_headers = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Permissions-Policy",
            "X-Request-ID"
        ]
        
        for header in required_headers:
            assert header in response.headers, f"Missing header: {header}"










