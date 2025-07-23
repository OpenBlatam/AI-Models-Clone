"""
Validation System

Comprehensive validation for the cybersecurity toolkit.
"""

import re
import ipaddress
from typing import Dict, Any, List, Optional, Union, Callable, Type
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio

from .error_handling import (
    ValidationError, TargetValidationError, PortValidationError,
    CredentialValidationError, PayloadValidationError
)

# ============================================================================
# VALIDATION LEVELS AND MODES
# ============================================================================

class ValidationLevel(str, Enum):
    """Validation levels."""
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"

class ValidationMode(str, Enum):
    """Validation modes."""
    SYNC = "sync"
    ASYNC = "async"
    BATCH = "batch"

# ============================================================================
# VALIDATION RESULT AND CONTEXT
# ============================================================================

@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }

@dataclass
class ValidationContext:
    """Context for validation operations."""
    level: ValidationLevel = ValidationLevel.NORMAL
    mode: ValidationMode = ValidationMode.SYNC
    strict_mode: bool = False
    allow_warnings: bool = True
    custom_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# BASE VALIDATOR
# ============================================================================

class BaseValidator(ABC):
    """Base class for all validators."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        self.context = context or ValidationContext()
    
    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        """Validate a value."""
        pass
    
    async def validate_async(self, value: Any) -> ValidationResult:
        """Validate a value asynchronously."""
        return self.validate(value)
    
    def validate_batch(self, values: List[Any]) -> List[ValidationResult]:
        """Validate multiple values."""
        return [self.validate(value) for value in values]
    
    async def validate_batch_async(self, values: List[Any]) -> List[ValidationResult]:
        """Validate multiple values asynchronously."""
        if self.context.mode == ValidationMode.ASYNC:
            tasks = [self.validate_async(value) for value in values]
            return await asyncio.gather(*tasks)
        else:
            return self.validate_batch(values)

# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, name: str, validator: Callable, error_message: str):
        self.name = name
        self.validator = validator
        self.error_message = error_message
    
    def apply(self, value: Any) -> bool:
        """Apply the validation rule."""
        return self.validator(value)
    
    def get_error_message(self, value: Any) -> str:
        """Get error message for failed validation."""
        return self.error_message.format(value=value)

class FieldValidator:
    """Validator for specific fields."""
    
    def __init__(self, field_name: str, rules: List[ValidationRule]):
        self.field_name = field_name
        self.rules = rules
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate a field value."""
        result = ValidationResult(is_valid=True)
        
        for rule in self.rules:
            if not rule.apply(value):
                result.add_error(f"{self.field_name}: {rule.get_error_message(value)}")
        
        return result

class CustomValidator:
    """Custom validator with user-defined logic."""
    
    def __init__(self, name: str, validation_func: Callable[[Any], bool], 
                 error_message: str):
        self.name = name
        self.validation_func = validation_func
        self.error_message = error_message
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate using custom function."""
        result = ValidationResult(is_valid=True)
        
        if not self.validation_func(value):
            result.add_error(self.error_message.format(value=value))
        
        return result

class CompositeValidator:
    """Combines multiple validators."""
    
    def __init__(self, validators: List[BaseValidator]):
        self.validators = validators
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate using all validators."""
        result = ValidationResult(is_valid=True)
        
        for validator in self.validators:
            validator_result = validator.validate(value)
            
            if not validator_result.is_valid:
                result.errors.extend(validator_result.errors)
                result.is_valid = False
            
            result.warnings.extend(validator_result.warnings)
            result.metadata.update(validator_result.metadata)
        
        return result

# ============================================================================
# SPECIFIC VALIDATORS
# ============================================================================

class TargetValidator(BaseValidator):
    """Validator for target addresses."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        super().__init__(context)
        self.ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        self.domain_pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
        self.url_pattern = re.compile(r'^https?://[a-zA-Z0-9.-]+')
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate target value."""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(value, str):
            result.add_error("Target must be a string")
            return result
        
        value = value.strip()
        
        # Check if it's an IP address
        if self._is_valid_ip(value):
            result.metadata["type"] = "ip"
            return result
        
        # Check if it's a domain
        if self._is_valid_domain(value):
            result.metadata["type"] = "domain"
            return result
        
        # Check if it's a URL
        if self._is_valid_url(value):
            result.metadata["type"] = "url"
            return result
        
        # Check if it's a network range
        if self._is_valid_network(value):
            result.metadata["type"] = "network"
            return result
        
        result.add_error(f"Invalid target format: {value}")
        return result
    
    def _is_valid_ip(self, value: str) -> bool:
        """Check if value is a valid IP address."""
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    
    def _is_valid_domain(self, value: str) -> bool:
        """Check if value is a valid domain name."""
        return bool(self.domain_pattern.match(value))
    
    def _is_valid_url(self, value: str) -> bool:
        """Check if value is a valid URL."""
        return bool(self.url_pattern.match(value))
    
    def _is_valid_network(self, value: str) -> bool:
        """Check if value is a valid network range."""
        try:
            ipaddress.ip_network(value, strict=False)
            return True
        except ValueError:
            return False

class PortValidator(BaseValidator):
    """Validator for port numbers."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        super().__init__(context)
        self.common_ports = {
            21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 5432, 6379
        }
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate port value."""
        result = ValidationResult(is_valid=True)
        
        # Check if it's an integer
        if not isinstance(value, int):
            result.add_error("Port must be an integer")
            return result
        
        # Check port range
        if not 1 <= value <= 65535:
            result.add_error(f"Port must be between 1 and 65535, got {value}")
            return result
        
        # Add metadata
        result.metadata["port"] = value
        result.metadata["is_common"] = value in self.common_ports
        
        # Add warnings for non-standard ports
        if value not in self.common_ports and self.context.allow_warnings:
            result.add_warning(f"Port {value} is not a commonly used port")
        
        return result
    
    def validate_range(self, start_port: int, end_port: int) -> ValidationResult:
        """Validate port range."""
        result = ValidationResult(is_valid=True)
        
        # Validate start port
        start_result = self.validate(start_port)
        if not start_result.is_valid:
            result.errors.extend(start_result.errors)
            result.is_valid = False
        
        # Validate end port
        end_result = self.validate(end_port)
        if not end_result.is_valid:
            result.errors.extend(end_result.errors)
            result.is_valid = False
        
        # Check range validity
        if result.is_valid and start_port > end_port:
            result.add_error(f"Start port ({start_port}) must be less than end port ({end_port})")
        
        return result

class CredentialValidator(BaseValidator):
    """Validator for credentials."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        super().__init__(context)
        self.min_username_length = 1
        self.max_username_length = 100
        self.min_password_length = 1
        self.max_password_length = 100
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate credential value."""
        result = ValidationResult(is_valid=True)
        
        if isinstance(value, dict):
            return self._validate_credential_dict(value)
        elif isinstance(value, str):
            return self._validate_credential_string(value)
        else:
            result.add_error("Credentials must be a dictionary or string")
            return result
    
    def _validate_credential_dict(self, credentials: Dict[str, Any]) -> ValidationResult:
        """Validate credential dictionary."""
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if "username" not in credentials:
            result.add_error("Username is required")
        
        if "password" not in credentials:
            result.add_error("Password is required")
        
        if not result.is_valid:
            return result
        
        # Validate username
        username = credentials["username"]
        if not isinstance(username, str):
            result.add_error("Username must be a string")
        elif not self.min_username_length <= len(username) <= self.max_username_length:
            result.add_error(f"Username length must be between {self.min_username_length} and {self.max_username_length}")
        
        # Validate password
        password = credentials["password"]
        if not isinstance(password, str):
            result.add_error("Password must be a string")
        elif not self.min_password_length <= len(password) <= self.max_password_length:
            result.add_error(f"Password length must be between {self.min_password_length} and {self.max_password_length}")
        
        # Add metadata
        if result.is_valid:
            result.metadata["username"] = username
            result.metadata["password_length"] = len(password)
            result.metadata["has_domain"] = "domain" in credentials
        
        return result
    
    def _validate_credential_string(self, credentials: str) -> ValidationResult:
        """Validate credential string (format: username:password)."""
        result = ValidationResult(is_valid=True)
        
        if ":" not in credentials:
            result.add_error("Credential string must be in format 'username:password'")
            return result
        
        username, password = credentials.split(":", 1)
        
        # Validate username
        if not self.min_username_length <= len(username) <= self.max_username_length:
            result.add_error(f"Username length must be between {self.min_username_length} and {self.max_username_length}")
        
        # Validate password
        if not self.min_password_length <= len(password) <= self.max_password_length:
            result.add_error(f"Password length must be between {self.min_password_length} and {self.max_password_length}")
        
        # Add metadata
        if result.is_valid:
            result.metadata["username"] = username
            result.metadata["password_length"] = len(password)
        
        return result

class PayloadValidator(BaseValidator):
    """Validator for attack payloads."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        super().__init__(context)
        self.max_payload_size = 1048576  # 1MB
        self.dangerous_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate payload value."""
        result = ValidationResult(is_valid=True)
        
        if isinstance(value, dict):
            return self._validate_payload_dict(value)
        elif isinstance(value, str):
            return self._validate_payload_string(value)
        else:
            result.add_error("Payload must be a dictionary or string")
            return result
    
    def _validate_payload_dict(self, payload: Dict[str, Any]) -> ValidationResult:
        """Validate payload dictionary."""
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if "content" not in payload:
            result.add_error("Payload content is required")
            return result
        
        content = payload["content"]
        if not isinstance(content, str):
            result.add_error("Payload content must be a string")
            return result
        
        # Validate content
        content_result = self._validate_payload_string(content)
        if not content_result.is_valid:
            result.errors.extend(content_result.errors)
            result.is_valid = False
        
        result.warnings.extend(content_result.warnings)
        result.metadata.update(content_result.metadata)
        
        # Validate additional fields
        if "type" in payload:
            result.metadata["payload_type"] = payload["type"]
        
        if "encoding" in payload:
            result.metadata["encoding"] = payload["encoding"]
        
        return result
    
    def _validate_payload_string(self, payload: str) -> ValidationResult:
        """Validate payload string."""
        result = ValidationResult(is_valid=True)
        
        # Check size
        payload_size = len(payload.encode('utf-8'))
        if payload_size > self.max_payload_size:
            result.add_error(f"Payload size ({payload_size} bytes) exceeds maximum ({self.max_payload_size} bytes)")
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                result.add_warning(f"Payload contains potentially dangerous pattern: {pattern}")
        
        # Add metadata
        result.metadata["size"] = payload_size
        result.metadata["length"] = len(payload)
        
        return result

class ConfigValidator(BaseValidator):
    """Validator for configuration objects."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        super().__init__(context)
        self.required_fields = []
        self.optional_fields = []
        self.field_validators = {}
    
    def add_required_field(self, field_name: str, validator: Optional[BaseValidator] = None):
        """Add a required field."""
        self.required_fields.append(field_name)
        if validator:
            self.field_validators[field_name] = validator
    
    def add_optional_field(self, field_name: str, validator: Optional[BaseValidator] = None):
        """Add an optional field."""
        self.optional_fields.append(field_name)
        if validator:
            self.field_validators[field_name] = validator
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate configuration value."""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(value, dict):
            result.add_error("Configuration must be a dictionary")
            return result
        
        # Check required fields
        for field_name in self.required_fields:
            if field_name not in value:
                result.add_error(f"Required field '{field_name}' is missing")
            elif field_name in self.field_validators:
                field_result = self.field_validators[field_name].validate(value[field_name])
                if not field_result.is_valid:
                    result.errors.extend([f"{field_name}: {error}" for error in field_result.errors])
                    result.is_valid = False
                result.warnings.extend([f"{field_name}: {warning}" for warning in field_result.warnings])
        
        # Check optional fields
        for field_name in self.optional_fields:
            if field_name in value and field_name in self.field_validators:
                field_result = self.field_validators[field_name].validate(value[field_name])
                if not field_result.is_valid:
                    result.errors.extend([f"{field_name}: {error}" for error in field_result.errors])
                    result.is_valid = False
                result.warnings.extend([f"{field_name}: {warning}" for warning in field_result.warnings])
        
        return result

class NetworkValidator(BaseValidator):
    """Validator for network-related values."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        super().__init__(context)
        self.target_validator = TargetValidator(context)
        self.port_validator = PortValidator(context)
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate network value."""
        result = ValidationResult(is_valid=True)
        
        if isinstance(value, dict):
            return self._validate_network_dict(value)
        elif isinstance(value, str):
            return self._validate_network_string(value)
        else:
            result.add_error("Network value must be a dictionary or string")
            return result
    
    def _validate_network_dict(self, network: Dict[str, Any]) -> ValidationResult:
        """Validate network dictionary."""
        result = ValidationResult(is_valid=True)
        
        # Validate target
        if "target" in network:
            target_result = self.target_validator.validate(network["target"])
            if not target_result.is_valid:
                result.errors.extend([f"target: {error}" for error in target_result.errors])
                result.is_valid = False
            result.metadata.update({"target_" + k: v for k, v in target_result.metadata.items()})
        
        # Validate port
        if "port" in network:
            port_result = self.port_validator.validate(network["port"])
            if not port_result.is_valid:
                result.errors.extend([f"port: {error}" for error in port_result.errors])
                result.is_valid = False
            result.metadata.update({"port_" + k: v for k, v in port_result.metadata.items()})
        
        # Validate timeout
        if "timeout" in network:
            timeout = network["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                result.add_error("Timeout must be a positive number")
            else:
                result.metadata["timeout"] = timeout
        
        return result
    
    def _validate_network_string(self, network: str) -> ValidationResult:
        """Validate network string (format: target:port)."""
        result = ValidationResult(is_valid=True)
        
        if ":" not in network:
            result.add_error("Network string must be in format 'target:port'")
            return result
        
        target, port_str = network.split(":", 1)
        
        # Validate target
        target_result = self.target_validator.validate(target)
        if not target_result.is_valid:
            result.errors.extend([f"target: {error}" for error in target_result.errors])
            result.is_valid = False
        
        # Validate port
        try:
            port = int(port_str)
            port_result = self.port_validator.validate(port)
            if not port_result.is_valid:
                result.errors.extend([f"port: {error}" for error in port_result.errors])
                result.is_valid = False
        except ValueError:
            result.add_error("Port must be a valid integer")
        
        return result

class CryptoValidator(BaseValidator):
    """Validator for cryptographic parameters."""
    
    def __init__(self, context: Optional[ValidationContext] = None):
        super().__init__(context)
        self.valid_algorithms = {
            "md5", "sha1", "sha256", "sha512", "blake2b", "blake2s",
            "aes_256_gcm", "aes_256_cbc", "aes_128_gcm", "aes_128_cbc",
            "chacha20_poly1305", "rsa_2048", "rsa_4096"
        }
        self.valid_operations = {
            "hash", "encrypt", "decrypt", "sign", "verify", 
            "key_generation", "key_derivation"
        }
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate crypto value."""
        result = ValidationResult(is_valid=True)
        
        if isinstance(value, dict):
            return self._validate_crypto_dict(value)
        else:
            result.add_error("Crypto value must be a dictionary")
            return result
    
    def _validate_crypto_dict(self, crypto: Dict[str, Any]) -> ValidationResult:
        """Validate crypto dictionary."""
        result = ValidationResult(is_valid=True)
        
        # Validate operation
        if "operation" in crypto:
            operation = crypto["operation"]
            if operation not in self.valid_operations:
                result.add_error(f"Invalid operation: {operation}")
            else:
                result.metadata["operation"] = operation
        
        # Validate algorithm
        if "algorithm" in crypto:
            algorithm = crypto["algorithm"]
            if algorithm not in self.valid_algorithms:
                result.add_error(f"Invalid algorithm: {algorithm}")
            else:
                result.metadata["algorithm"] = algorithm
        
        # Validate data
        if "data" in crypto:
            data = crypto["data"]
            if not isinstance(data, (str, bytes)):
                result.add_error("Data must be a string or bytes")
            else:
                result.metadata["data_size"] = len(data) if isinstance(data, str) else len(data)
        
        # Validate key
        if "key" in crypto:
            key = crypto["key"]
            if not isinstance(key, (str, bytes)):
                result.add_error("Key must be a string or bytes")
            else:
                result.metadata["key_size"] = len(key) if isinstance(key, str) else len(key)
        
        # Validate iterations
        if "iterations" in crypto:
            iterations = crypto["iterations"]
            if not isinstance(iterations, int) or iterations < 1000:
                result.add_error("Iterations must be an integer >= 1000")
            else:
                result.metadata["iterations"] = iterations
        
        return result

# ============================================================================
# VALIDATION SCHEMA
# ============================================================================

class ValidationSchema:
    """Schema for complex validation rules."""
    
    def __init__(self, name: str):
        self.name = name
        self.field_validators: Dict[str, FieldValidator] = {}
        self.custom_validators: List[CustomValidator] = []
    
    def add_field_validator(self, field_name: str, validator: FieldValidator) -> None:
        """Add a field validator."""
        self.field_validators[field_name] = validator
    
    def add_custom_validator(self, validator: CustomValidator) -> None:
        """Add a custom validator."""
        self.custom_validators.append(validator)
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against schema."""
        result = ValidationResult(is_valid=True)
        
        # Validate fields
        for field_name, validator in self.field_validators.items():
            if field_name in data:
                field_result = validator.validate(data[field_name])
                if not field_result.is_valid:
                    result.errors.extend(field_result.errors)
                    result.is_valid = False
                result.warnings.extend(field_result.warnings)
                result.metadata.update({f"{field_name}_{k}": v for k, v in field_result.metadata.items()})
        
        # Apply custom validators
        for validator in self.custom_validators:
            validator_result = validator.validate(data)
            if not validator_result.is_valid:
                result.errors.extend(validator_result.errors)
                result.is_valid = False
            result.warnings.extend(validator_result.warnings)
            result.metadata.update(validator_result.metadata)
        
        return result

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_target(target: str) -> ValidationResult:
    """Validate a target address."""
    validator = TargetValidator()
    return validator.validate(target)

def validate_port(port: int) -> ValidationResult:
    """Validate a port number."""
    validator = PortValidator()
    return validator.validate(port)

def validate_credentials(credentials: Union[Dict[str, str], str]) -> ValidationResult:
    """Validate credentials."""
    validator = CredentialValidator()
    return validator.validate(credentials)

def validate_payload(payload: Union[Dict[str, Any], str]) -> ValidationResult:
    """Validate a payload."""
    validator = PayloadValidator()
    return validator.validate(payload)

def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """Validate a configuration object."""
    validator = ConfigValidator()
    return validator.validate(config)

def validate_network_target(network: Union[Dict[str, Any], str]) -> ValidationResult:
    """Validate a network target."""
    validator = NetworkValidator()
    return validator.validate(network)

def validate_crypto_params(crypto: Dict[str, Any]) -> ValidationResult:
    """Validate cryptographic parameters."""
    validator = CryptoValidator()
    return validator.validate(crypto) 