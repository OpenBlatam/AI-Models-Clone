from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import re
import html
from typing import Dict, Any, List, Tuple, Optional, Union
from urllib.parse import quote, unquote
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Input Validation and Sanitization

Provides comprehensive input validation and sanitization for security applications.
"""


class ValidationRules(BaseModel):
    """Pydantic model for validation rules."""
    length: bool = Field(default=True, description="Enable length validation")
    pattern: bool = Field(default=True, description="Enable pattern validation")
    xss: bool = Field(default=True, description="Enable XSS sanitization")
    sql_injection: bool = Field(default=True, description="Enable SQL injection detection")

class ValidationRequest(BaseModel):
    """Pydantic model for validation request."""
    input_text: str = Field(..., description="Text to validate")
    validation_rules: ValidationRules = Field(default_factory=ValidationRules)
    max_length: int = Field(default=1000, ge=1, le=10000, description="Maximum allowed length")
    
    @validator('input_text')
    def validate_input_text(cls, v) -> bool:
        if not v:
            raise ValueError("Input text cannot be empty")
        return v

class ValidationResult(BaseModel):
    """Pydantic model for validation result."""
    original_input: str
    sanitized_input: str
    validation_results: Dict[str, Any]
    is_safe: bool
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow)

def validate_and_sanitize_input(data: ValidationRequest) -> ValidationResult:
    """Validate and sanitize user input with RORO pattern."""
    input_text = data.input_text
    validation_rules = data.validation_rules
    max_length = data.max_length
    
    validation_results: Dict[str, Any] = {}
    sanitized_text = input_text
    
    # Length validation (CPU-bound)
    if validation_rules.length:
        validation_results["length"] = {
            "is_valid": len(input_text) <= max_length,
            "actual_length": len(input_text),
            "max_length": max_length
        }
    
    # Pattern validation (CPU-bound)
    if validation_rules.pattern:
        malicious_patterns = [
            (r'(\'|\")\s*(or|and)\s*\d+\s*=\s*\d+', "sql_injection"),
            (r'<script.*?>.*?</script>', "xss_script"),
            (r'javascript:', "xss_javascript"),
            (r'\.\./', "path_traversal")
        ]
        
        pattern_violations = []
        for pattern, threat_type in malicious_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                pattern_violations.append(threat_type)
        
        validation_results["pattern"] = {
            "is_valid": len(pattern_violations) == 0,
            "violations": pattern_violations
        }
    
    # XSS sanitization (CPU-bound)
    if validation_rules.xss:
        sanitized_text = html.escape(input_text)
        validation_results["xss_sanitization"] = {
            "original": input_text,
            "sanitized": sanitized_text,
            "was_sanitized": input_text != sanitized_text
        }
    
    return ValidationResult(
        original_input=input_text,
        sanitized_input=sanitized_text,
        validation_results=validation_results,
        is_safe=all(result.get("is_valid", True) for result in validation_results.values())
    ) 