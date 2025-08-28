from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .validators import (
from .crypto import (
from .network import (
from .logging import (
from .web import (
from .intelligence import (
from .testing import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Cybersecurity Security Package

A comprehensive Python cybersecurity toolkit with modular architecture.
"""

    ValidationRequest,
    ValidationResult,
    ValidationRules,
    validate_and_sanitize_input
)

    KeyGenerationRequest,
    KeyGenerationResult,
    EncryptionRequest,
    EncryptionResult,
    generate_secure_key,
    encrypt_data,
    decrypt_data,
    hash_password
)

    PortScanRequest,
    PortScanResult,
    PortRangeScanRequest,
    PortRangeScanResult,
    scan_port,
    scan_port_async,
    scan_port_range_async,
    get_service_name
)

    SecurityEvent,
    LoggerConfig,
    LoggingResult,
    LogAnalysisRequest,
    LogAnalysisResult,
    ThreatIndicators,
    create_security_logger,
    log_security_event_async,
    analyze_security_logs_async
)

    AppConfig,
    JWTConfig,
    UserData,
    TokenData,
    create_secure_fastapi_app,
    create_jwt_authentication
)

    IPReputationRequest,
    IPReputationResult,
    DomainReputationRequest,
    DomainReputationResult,
    check_ip_reputation_async,
    check_domain_reputation_async
)

    SecurityTestRequest,
    SecurityTestResult,
    PenetrationTestRequest,
    PenetrationTestResult,
    run_security_tests_async,
    run_penetration_test_async
)

__version__ = "1.0.0"
__author__ = "Cybersecurity Team"

__all__ = [
    # Validators
    "ValidationRequest",
    "ValidationResult", 
    "ValidationRules",
    "validate_and_sanitize_input",
    
    # Crypto
    "KeyGenerationRequest",
    "KeyGenerationResult",
    "EncryptionRequest",
    "EncryptionResult",
    "generate_secure_key",
    "encrypt_data",
    "decrypt_data",
    "hash_password",
    
    # Network
    "PortScanRequest",
    "PortScanResult",
    "PortRangeScanRequest",
    "PortRangeScanResult",
    "scan_port",
    "scan_port_async",
    "scan_port_range_async",
    "get_service_name",
    
    # Logging
    "SecurityEvent",
    "LoggerConfig",
    "LoggingResult",
    "LogAnalysisRequest",
    "LogAnalysisResult",
    "ThreatIndicators",
    "create_security_logger",
    "log_security_event_async",
    "analyze_security_logs_async",
    
    # Web
    "AppConfig",
    "JWTConfig",
    "UserData",
    "TokenData",
    "create_secure_fastapi_app",
    "create_jwt_authentication",
    
    # Intelligence
    "IPReputationRequest",
    "IPReputationResult",
    "DomainReputationRequest",
    "DomainReputationResult",
    "check_ip_reputation_async",
    "check_domain_reputation_async",
    
    # Testing
    "SecurityTestRequest",
    "SecurityTestResult",
    "PenetrationTestRequest",
    "PenetrationTestResult",
    "run_security_tests_async",
    "run_penetration_test_async"
] 