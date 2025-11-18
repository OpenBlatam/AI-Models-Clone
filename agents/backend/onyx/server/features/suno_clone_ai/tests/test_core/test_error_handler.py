"""
Comprehensive Unit Tests for Error Handler

Tests cover all error handling functions with diverse test cases
"""

import pytest
from fastapi import HTTPException, status

from core.error_handler import ErrorHandler


class TestErrorHandlerGenerationError:
    """Test cases for handle_generation_error function"""
    
    def test_handle_generation_error_cuda_error(self):
        """Test handling CUDA out of memory error"""
        error = RuntimeError("CUDA out of memory")
        http_exception = ErrorHandler.handle_generation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_507_INSUFFICIENT_STORAGE
        assert "GPU memory" in http_exception.detail.lower()
    
    def test_handle_generation_error_out_of_memory(self):
        """Test handling out of memory error"""
        error = RuntimeError("out of memory error occurred")
        http_exception = ErrorHandler.handle_generation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_507_INSUFFICIENT_STORAGE
    
    def test_handle_generation_error_model_not_found(self):
        """Test handling model not found error"""
        error = FileNotFoundError("model not found in path")
        http_exception = ErrorHandler.handle_generation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "model" in http_exception.detail.lower()
    
    def test_handle_generation_error_generic(self):
        """Test handling generic generation error"""
        error = ValueError("Generic error occurred")
        http_exception = ErrorHandler.handle_generation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error generating music" in http_exception.detail.lower()
    
    def test_handle_generation_error_with_context(self):
        """Test error handling with context"""
        error = RuntimeError("Test error")
        context = {"user_id": "123", "song_id": "456"}
        http_exception = ErrorHandler.handle_generation_error(error, context=context)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_handle_generation_error_empty_message(self):
        """Test handling error with empty message"""
        error = Exception("")
        http_exception = ErrorHandler.handle_generation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestErrorHandlerAudioProcessingError:
    """Test cases for handle_audio_processing_error function"""
    
    def test_handle_audio_processing_error_file_not_found(self):
        """Test handling file not found error"""
        error = FileNotFoundError("file not found")
        http_exception = ErrorHandler.handle_audio_processing_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_404_NOT_FOUND
        assert "audio file not found" in http_exception.detail.lower()
    
    def test_handle_audio_processing_error_format_error(self):
        """Test handling format error"""
        error = ValueError("unsupported audio format")
        http_exception = ErrorHandler.handle_audio_processing_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_400_BAD_REQUEST
        assert "unsupported audio format" in http_exception.detail.lower()
    
    def test_handle_audio_processing_error_codec_error(self):
        """Test handling codec error"""
        error = RuntimeError("codec error occurred")
        http_exception = ErrorHandler.handle_audio_processing_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_handle_audio_processing_error_generic(self):
        """Test handling generic audio processing error"""
        error = RuntimeError("Generic processing error")
        http_exception = ErrorHandler.handle_audio_processing_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error processing audio" in http_exception.detail.lower()
    
    def test_handle_audio_processing_error_with_context(self):
        """Test error handling with context"""
        error = ValueError("Test error")
        context = {"file_path": "/path/to/file.wav"}
        http_exception = ErrorHandler.handle_audio_processing_error(error, context=context)
        
        assert isinstance(http_exception, HTTPException)


class TestErrorHandlerValidationError:
    """Test cases for handle_validation_error function"""
    
    def test_handle_validation_error_basic(self):
        """Test handling basic validation error"""
        error = ValueError("Invalid input parameter")
        http_exception = ErrorHandler.handle_validation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exception.detail == "Invalid input parameter"
    
    def test_handle_validation_error_empty_message(self):
        """Test handling validation error with empty message"""
        error = ValueError("")
        http_exception = ErrorHandler.handle_validation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exception.detail == ""
    
    def test_handle_validation_error_with_context(self):
        """Test validation error with context"""
        error = ValueError("Field 'duration' must be positive")
        context = {"field": "duration", "value": -10}
        http_exception = ErrorHandler.handle_validation_error(error, context=context)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.status_code == status.HTTP_400_BAD_REQUEST
        assert "duration" in http_exception.detail.lower()
    
    def test_handle_validation_error_long_message(self):
        """Test handling validation error with long message"""
        long_message = "A" * 1000
        error = ValueError(long_message)
        http_exception = ErrorHandler.handle_validation_error(error)
        
        assert isinstance(http_exception, HTTPException)
        assert http_exception.detail == long_message


class TestErrorHandlerCacheError:
    """Test cases for handle_cache_error function"""
    
    def test_handle_cache_error_returns_none(self):
        """Test cache error returns None (non-critical)"""
        error = ConnectionError("Redis connection failed")
        result = ErrorHandler.handle_cache_error(error)
        
        assert result is None
    
    def test_handle_cache_error_with_context(self):
        """Test cache error with context"""
        error = TimeoutError("Cache timeout")
        context = {"cache_key": "test_key"}
        result = ErrorHandler.handle_cache_error(error, context=context)
        
        assert result is None
    
    def test_handle_cache_error_various_exceptions(self):
        """Test cache error handles various exception types"""
        exceptions = [
            ConnectionError("Connection failed"),
            TimeoutError("Timeout"),
            ValueError("Invalid key"),
            RuntimeError("Cache error")
        ]
        
        for error in exceptions:
            result = ErrorHandler.handle_cache_error(error)
            assert result is None
    
    def test_handle_cache_error_empty_message(self):
        """Test cache error with empty message"""
        error = Exception("")
        result = ErrorHandler.handle_cache_error(error)
        
        assert result is None










