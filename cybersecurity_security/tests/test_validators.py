from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import pytest
from cybersecurity_security.validators import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Tests for Validators Module

Tests input validation and sanitization functionality.
"""

    ValidationRequest, ValidationRules, ValidationResult,
    validate_and_sanitize_input
)

class TestValidators:
    """Test suite for validators module."""
    
    async def test_validation_request_creation(self) -> Any:
        """Test ValidationRequest creation with valid data."""
        request = ValidationRequest(
            input_text="test input",
            validation_rules=ValidationRules(),
            max_length=100
        )
        assert request.input_text == "test input"
        assert request.max_length == 100
        assert request.validation_rules.length is True
    
    async def test_validation_request_invalid_input(self) -> Any:
        """Test ValidationRequest with invalid input."""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            ValidationRequest(input_text="")
    
    async def test_validation_request_invalid_max_length(self) -> Any:
        """Test ValidationRequest with invalid max_length."""
        with pytest.raises(ValueError):
            ValidationRequest(
                input_text="test",
                max_length=0  # Should be >= 1
            )
    
    def test_safe_input_validation(self) -> Any:
        """Test validation of safe input."""
        request = ValidationRequest(
            input_text="Hello, world!",
            validation_rules=ValidationRules(length=True, pattern=True, xss=True)
        )
        result = validate_and_sanitize_input(request)
        
        assert result.is_safe is True
        assert result.original_input == "Hello, world!"
        assert result.sanitized_input == "Hello, world!"
        assert result.validation_results["length"]["is_valid"] is True
    
    def test_xss_input_validation(self) -> Any:
        """Test validation of XSS input."""
        request = ValidationRequest(
            input_text="<script>alert('xss')</script>",
            validation_rules=ValidationRules(length=True, pattern=True, xss=True)
        )
        result = validate_and_sanitize_input(request)
        
        assert result.is_safe is False
        assert result.original_input == "<script>alert('xss')</script>"
        assert result.sanitized_input == "&lt;script&gt;alert('xss')&lt;/script&gt;"
        assert result.validation_results["xss_sanitization"]["was_sanitized"] is True
    
    def test_sql_injection_validation(self) -> Any:
        """Test validation of SQL injection input."""
        request = ValidationRequest(
            input_text="'; DROP TABLE users; --",
            validation_rules=ValidationRules(length=True, pattern=True, xss=True)
        )
        result = validate_and_sanitize_input(request)
        
        assert result.is_safe is False
        assert "sql_injection" in result.validation_results["pattern"]["violations"]
    
    def test_length_validation(self) -> Any:
        """Test length validation."""
        long_input = "a" * 1001
        request = ValidationRequest(
            input_text=long_input,
            validation_rules=ValidationRules(length=True),
            max_length=1000
        )
        result = validate_and_sanitize_input(request)
        
        assert result.is_safe is False
        assert result.validation_results["length"]["is_valid"] is False
        assert result.validation_results["length"]["actual_length"] == 1001
    
    def test_partial_validation_rules(self) -> Any:
        """Test validation with partial rules enabled."""
        request = ValidationRequest(
            input_text="<script>alert('xss')</script>",
            validation_rules=ValidationRules(length=True, pattern=False, xss=False)
        )
        result = validate_and_sanitize_input(request)
        
        assert result.is_safe is True  # Only length validation is enabled
        assert "length" in result.validation_results
        assert "pattern" not in result.validation_results
        assert "xss_sanitization" not in result.validation_results
    
    def test_path_traversal_validation(self) -> Any:
        """Test validation of path traversal input."""
        request = ValidationRequest(
            input_text="../../../etc/passwd",
            validation_rules=ValidationRules(length=True, pattern=True, xss=True)
        )
        result = validate_and_sanitize_input(request)
        
        assert result.is_safe is False
        assert "path_traversal" in result.validation_results["pattern"]["violations"]
    
    def test_mixed_malicious_input(self) -> Any:
        """Test validation of input with multiple threats."""
        request = ValidationRequest(
            input_text="<script>alert('xss')</script>'; DROP TABLE users; --",
            validation_rules=ValidationRules(length=True, pattern=True, xss=True)
        )
        result = validate_and_sanitize_input(request)
        
        assert result.is_safe is False
        assert len(result.validation_results["pattern"]["violations"]) >= 2
        assert result.validation_results["xss_sanitization"]["was_sanitized"] is True
    
    def test_validation_result_structure(self) -> Any:
        """Test ValidationResult structure."""
        request = ValidationRequest(input_text="test")
        result = validate_and_sanitize_input(request)
        
        assert hasattr(result, 'original_input')
        assert hasattr(result, 'sanitized_input')
        assert hasattr(result, 'validation_results')
        assert hasattr(result, 'is_safe')
        assert hasattr(result, 'validation_timestamp')
        assert isinstance(result.validation_timestamp, str) 