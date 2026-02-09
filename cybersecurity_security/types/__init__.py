from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .models import (
from .schemas import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Types Module

Provides Pydantic models and schemas for the cybersecurity toolkit.
"""

    # Base Models
    BaseRequest,
    BaseResult,
    BaseConfig,
    
    # Scan Models
    ScanRequest,
    ScanResult,
    ScanConfig,
    ScanStatus,
    ScanType,
    
    # Vulnerability Models
    Vulnerability,
    VulnerabilityLevel,
    VulnerabilityType,
    VulnerabilityReport,
    
    # Network Models
    NetworkTarget,
    NetworkService,
    NetworkPort,
    NetworkHost,
    NetworkScan,
    
    # Attack Models
    AttackRequest,
    AttackResult,
    AttackType,
    AttackPayload,
    AttackSession,
    
    # Report Models
    ReportRequest,
    ReportResult,
    ReportFormat,
    ReportLevel,
    ReportSection,
    
    # Enumeration Models
    EnumerationRequest,
    EnumerationResult,
    EnumerationType,
    ServiceInfo,
    PortInfo,
    
    # Crypto Models
    CryptoRequest,
    CryptoResult,
    CryptoOperation,
    HashAlgorithm,
    EncryptionAlgorithm,
    
    # Network Models
    NetworkRequest,
    NetworkResult,
    NetworkOperation,
    
    # Utility Models
    FileInfo,
    ProcessInfo,
    SystemInfo,
    LogEntry,
    ErrorInfo
)

    # Request Schemas
    ScanRequestSchema,
    AttackRequestSchema,
    EnumerationRequestSchema,
    ReportRequestSchema,
    CryptoRequestSchema,
    NetworkRequestSchema,
    
    # Response Schemas
    ScanResponseSchema,
    AttackResponseSchema,
    EnumerationResponseSchema,
    ReportResponseSchema,
    CryptoResponseSchema,
    NetworkResponseSchema,
    
    # Config Schemas
    ScannerConfigSchema,
    AttackerConfigSchema,
    ReporterConfigSchema,
    UtilsConfigSchema,
    
    # Validation Schemas
    TargetValidationSchema,
    PortValidationSchema,
    CredentialValidationSchema,
    PayloadValidationSchema,
    
    # Export Schemas
    JSONExportSchema,
    CSVExportSchema,
    XMLExportSchema,
    HTMLExportSchema
)

__all__ = [
    # Models
    "BaseRequest",
    "BaseResult", 
    "BaseConfig",
    "ScanRequest",
    "ScanResult",
    "ScanConfig",
    "ScanStatus",
    "ScanType",
    "Vulnerability",
    "VulnerabilityLevel",
    "VulnerabilityType",
    "VulnerabilityReport",
    "NetworkTarget",
    "NetworkService",
    "NetworkPort",
    "NetworkHost",
    "NetworkScan",
    "AttackRequest",
    "AttackResult",
    "AttackType",
    "AttackPayload",
    "AttackSession",
    "ReportRequest",
    "ReportResult",
    "ReportFormat",
    "ReportLevel",
    "ReportSection",
    "EnumerationRequest",
    "EnumerationResult",
    "EnumerationType",
    "ServiceInfo",
    "PortInfo",
    "CryptoRequest",
    "CryptoResult",
    "CryptoOperation",
    "HashAlgorithm",
    "EncryptionAlgorithm",
    "NetworkRequest",
    "NetworkResult",
    "NetworkOperation",
    "FileInfo",
    "ProcessInfo",
    "SystemInfo",
    "LogEntry",
    "ErrorInfo",
    
    # Schemas
    "ScanRequestSchema",
    "AttackRequestSchema",
    "EnumerationRequestSchema",
    "ReportRequestSchema",
    "CryptoRequestSchema",
    "NetworkRequestSchema",
    "ScanResponseSchema",
    "AttackResponseSchema",
    "EnumerationResponseSchema",
    "ReportResponseSchema",
    "CryptoResponseSchema",
    "NetworkResponseSchema",
    "ScannerConfigSchema",
    "AttackerConfigSchema",
    "ReporterConfigSchema",
    "UtilsConfigSchema",
    "TargetValidationSchema",
    "PortValidationSchema",
    "CredentialValidationSchema",
    "PayloadValidationSchema",
    "JSONExportSchema",
    "CSVExportSchema",
    "XMLExportSchema",
    "HTMLExportSchema"
] 