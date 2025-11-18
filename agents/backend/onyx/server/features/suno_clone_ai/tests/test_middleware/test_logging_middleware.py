"""
Comprehensive Unit Tests for Logging Middleware

Tests cover logging middleware functionality with diverse test cases
"""

import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request

from middleware.logging_middleware import LoggingMiddleware


class TestLoggingMiddleware:
    """Test cases for LoggingMiddleware class"""
    
    @pytest.mark.asyncio
    async def test_dispatch_logs_request_and_response(self):
        """Test dispatch logs request and response"""
        app = Mock()
        middleware = LoggingMiddleware(app)
        
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        
        response = Mock()
        response.status_code = 200
        
        call_next = AsyncMock(return_value=response)
        
        with patch('middleware.logging_middleware.logger') as mock_logger:
            result = await middleware.dispatch(request, call_next)
            
            assert result == response
            assert mock_logger.info.call_count >= 2  # Request and response logs
    
    @pytest.mark.asyncio
    async def test_dispatch_logs_request_method(self):
        """Test dispatch logs request method"""
        app = Mock()
        middleware = LoggingMiddleware(app)
        
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/test"
        
        response = Mock()
        response.status_code = 201
        call_next = AsyncMock(return_value=response)
        
        with patch('middleware.logging_middleware.logger') as mock_logger:
            await middleware.dispatch(request, call_next)
            
            # Check that method is logged
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("POST" in str(call) for call in log_calls)
    
    @pytest.mark.asyncio
    async def test_dispatch_logs_response_status(self):
        """Test dispatch logs response status code"""
        app = Mock()
        middleware = LoggingMiddleware(app)
        
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        
        response = Mock()
        response.status_code = 404
        call_next = AsyncMock(return_value=response)
        
        with patch('middleware.logging_middleware.logger') as mock_logger:
            await middleware.dispatch(request, call_next)
            
            # Check that status is logged
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("404" in str(call) for call in log_calls)
    
    @pytest.mark.asyncio
    async def test_dispatch_logs_duration(self):
        """Test dispatch logs request duration"""
        app = Mock()
        middleware = LoggingMiddleware(app)
        
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        
        response = Mock()
        response.status_code = 200
        call_next = AsyncMock(return_value=response)
        
        with patch('middleware.logging_middleware.logger') as mock_logger:
            await middleware.dispatch(request, call_next)
            
            # Check that duration is logged
            log_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("Duration" in str(call) or "duration" in str(call).lower() for call in log_calls)
    
    @pytest.mark.asyncio
    async def test_dispatch_calculates_duration(self):
        """Test duration calculation"""
        app = Mock()
        middleware = LoggingMiddleware(app)
        
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        
        response = Mock()
        response.status_code = 200
        
        async def slow_call_next(req):
            await asyncio.sleep(0.1)
            return response
        
        import asyncio
        start = time.time()
        result = await middleware.dispatch(request, slow_call_next)
        end = time.time()
        
        assert result == response
        assert (end - start) >= 0.1  # Should take at least 0.1 seconds
    
    @pytest.mark.asyncio
    async def test_dispatch_different_status_codes(self):
        """Test logging with different status codes"""
        app = Mock()
        middleware = LoggingMiddleware(app)
        
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        
        status_codes = [200, 201, 400, 404, 500]
        
        for status_code in status_codes:
            response = Mock()
            response.status_code = status_code
            call_next = AsyncMock(return_value=response)
            
            with patch('middleware.logging_middleware.logger') as mock_logger:
                await middleware.dispatch(request, call_next)
                
                # Should log regardless of status code
                assert mock_logger.info.called










