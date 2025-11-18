"""
Comprehensive Unit Tests for Compression Middleware

Tests cover compression middleware functionality with diverse test cases
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import Request
from starlette.responses import Response

from middleware.compression_middleware import CompressionMiddleware


class TestCompressionMiddleware:
    """Test cases for CompressionMiddleware class"""
    
    def test_compression_middleware_init_defaults(self):
        """Test initializing middleware with defaults"""
        app = Mock()
        middleware = CompressionMiddleware(app)
        
        assert middleware.minimum_size == 500
        assert middleware.compress_level == 6
    
    def test_compression_middleware_init_custom(self):
        """Test initializing middleware with custom parameters"""
        app = Mock()
        middleware = CompressionMiddleware(
            app,
            minimum_size=1000,
            compress_level=9
        )
        
        assert middleware.minimum_size == 1000
        assert middleware.compress_level == 9
    
    @pytest.mark.asyncio
    async def test_dispatch_no_accept_encoding(self):
        """Test dispatch without accept-encoding header"""
        app = Mock()
        middleware = CompressionMiddleware(app)
        
        request = Mock(spec=Request)
        request.headers = {}
        
        response = Mock(spec=Response)
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == response
        # Should not compress
        assert "content-encoding" not in getattr(response, "headers", {})
    
    @pytest.mark.asyncio
    async def test_dispatch_small_response(self):
        """Test dispatch with response smaller than minimum"""
        app = Mock()
        middleware = CompressionMiddleware(app, minimum_size=1000)
        
        request = Mock(spec=Request)
        request.headers = {"accept-encoding": "gzip"}
        
        response = Mock(spec=Response)
        response.body = b"small response"  # Less than 1000 bytes
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == response
        # Should not compress small responses
        assert "content-encoding" not in response.headers
    
    @pytest.mark.asyncio
    @patch('gzip.compress')
    async def test_dispatch_gzip_compression(self, mock_gzip):
        """Test gzip compression"""
        app = Mock()
        middleware = CompressionMiddleware(app, minimum_size=100)
        
        request = Mock(spec=Request)
        request.headers = {"accept-encoding": "gzip"}
        
        large_body = b"x" * 1000
        compressed_body = b"compressed"
        mock_gzip.return_value = compressed_body
        
        response = Mock(spec=Response)
        response.body = large_body
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == response
        assert response.headers.get("content-encoding") == "gzip"
        assert response.headers.get("content-length") == str(len(compressed_body))
        assert "vary" in response.headers
    
    @pytest.mark.asyncio
    @patch('brotli.compress')
    async def test_dispatch_brotli_compression(self, mock_brotli):
        """Test brotli compression (preferred)"""
        app = Mock()
        middleware = CompressionMiddleware(app, minimum_size=100)
        
        request = Mock(spec=Request)
        request.headers = {"accept-encoding": "br, gzip"}
        
        large_body = b"x" * 1000
        compressed_body = b"compressed"
        mock_brotli.return_value = compressed_body
        
        response = Mock(spec=Response)
        response.body = large_body
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        assert result == response
        assert response.headers.get("content-encoding") == "br"
        mock_brotli.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('brotli.compress')
    async def test_dispatch_brotli_not_available_fallback(self, mock_brotli):
        """Test fallback to gzip when brotli not available"""
        app = Mock()
        middleware = CompressionMiddleware(app, minimum_size=100)
        
        request = Mock(spec=Request)
        request.headers = {"accept-encoding": "br, gzip"}
        
        large_body = b"x" * 1000
        mock_brotli.side_effect = ImportError("brotli not available")
        
        with patch('gzip.compress', return_value=b"gzip_compressed") as mock_gzip:
            response = Mock(spec=Response)
            response.body = large_body
            response.headers = {}
            call_next = AsyncMock(return_value=response)
            
            result = await middleware.dispatch(request, call_next)
            
            # Should fallback to gzip
            assert response.headers.get("content-encoding") == "gzip"
            mock_gzip.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('gzip.compress')
    async def test_dispatch_compression_not_beneficial(self, mock_gzip):
        """Test that compression is skipped if not beneficial"""
        app = Mock()
        middleware = CompressionMiddleware(app, minimum_size=100)
        
        request = Mock(spec=Request)
        request.headers = {"accept-encoding": "gzip"}
        
        large_body = b"x" * 1000
        # Compressed size larger than original (shouldn't happen but test it)
        compressed_body = b"x" * 2000
        mock_gzip.return_value = compressed_body
        
        response = Mock(spec=Response)
        response.body = large_body
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        # Should not compress if not beneficial
        # (Implementation checks if compressed < original)
        assert result == response
    
    @pytest.mark.asyncio
    async def test_dispatch_no_body_attribute(self):
        """Test dispatch with response without body attribute"""
        app = Mock()
        middleware = CompressionMiddleware(app)
        
        request = Mock(spec=Request)
        request.headers = {"accept-encoding": "gzip"}
        
        response = Mock(spec=Response)
        # Remove body attribute
        if hasattr(response, 'body'):
            delattr(response, 'body')
        response.headers = {}
        call_next = AsyncMock(return_value=response)
        
        result = await middleware.dispatch(request, call_next)
        
        # Should return response as-is
        assert result == response










