"""
Security Logging and Monitoring

Provides comprehensive security logging and monitoring capabilities.
"""

import json
import structlog
import secrets
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from dataclasses import dataclass, asdict
import asyncio
import aiofiles

class SecurityEvent(BaseModel):
    """Pydantic model for security event."""
    event_type: str = Field(..., description="Type of security event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_ip: str = Field(..., description="Source IP address")
    user_id: Optional[str] = Field(None, description="User identifier")
    severity: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    details: Dict[str, Any] = Field(default_factory=dict)
    event_id: str = Field(default_factory=lambda: secrets.token_hex(8))
    
    @validator('source_ip')
    def validate_ip(cls, v):
        import ipaddress
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError("Invalid IP address format")

class LoggerConfig(BaseModel):
    """Pydantic model for logger configuration."""
    log_level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_format: str = Field(default="json", regex="^(json|console)$")
    log_file_path: Optional[str] = Field(None, description="Path to log file")
    
    @validator('log_file_path')
    def validate_log_file_path(cls, v):
        if v and not v.endswith(('.log', '.json')):
            raise ValueError("Log file must have .log or .json extension")
        return v

class LoggingResult(BaseModel):
    """Pydantic model for logging result."""
    logged: bool
    event_id: str
    event_type: str
    severity: str
    timestamp: datetime
    error_message: Optional[str] = None

class ThreatIndicators(BaseModel):
    """Pydantic model for threat indicators."""
    failed_logins: int = Field(default=0, ge=0)
    suspicious_ips: List[str] = Field(default_factory=list)
    rate_limit_violations: int = Field(default=0, ge=0)
    malicious_requests: int = Field(default=0, ge=0)

class LogAnalysisRequest(BaseModel):
    """Pydantic model for log analysis request."""
    log_file_path: str = Field(..., description="Path to log file")
    analysis_period_hours: int = Field(default=24, ge=1, le=168, description="Analysis period in hours")
    
    @validator('log_file_path')
    def validate_log_file_exists(cls, v):
        import os
        if not os.path.exists(v):
            raise ValueError("Log file does not exist")
        return v

class LogAnalysisResult(BaseModel):
    """Pydantic model for log analysis result."""
    analysis_period_hours: int
    threat_indicators: ThreatIndicators
    risk_score: float
    risk_level: str
    analysis_completed: bool
    analyzed_entries: int = Field(default=0, ge=0)
    error_message: Optional[str] = None

def create_security_logger(data: LoggerConfig) -> Dict[str, Any]:
    """Create security logger (CPU-bound setup)."""
    log_level = data.log_level
    log_format = data.log_format
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger()
    
    return {
        "logger": logger,
        "log_level": log_level,
        "log_format": log_format,
        "log_file_path": data.log_file_path,
        "configured": True
    }

async def log_security_event_async(data: Dict[str, Any]) -> LoggingResult:
    """Log security event asynchronously (I/O-bound)."""
    logger = data.get("logger")
    event = data.get("event")
    
    if not logger or not event:
        return LoggingResult(
            logged=False,
            event_id="",
            event_type="",
            severity="",
            timestamp=datetime.now(timezone.utc),
            error_message="Missing logger or event"
        )
    
    try:
        # Log to structlog (synchronous but fast)
        log_method = getattr(logger, event.severity.lower())
        log_method("Security event", **event.dict())
        
        # Async file logging if configured
        if data.get("log_file_path"):
            await write_event_to_file(event, data["log_file_path"])
        
        return LoggingResult(
            logged=True,
            event_id=event.event_id,
            event_type=event.event_type,
            severity=event.severity,
            timestamp=event.timestamp
        )
    
    except Exception as e:
        return LoggingResult(
            logged=False,
            event_id=event.event_id if event else "",
            event_type=event.event_type if event else "",
            severity=event.severity if event else "",
            timestamp=datetime.now(timezone.utc),
            error_message=str(e)
        )

async def write_event_to_file(event: SecurityEvent, file_path: str) -> None:
    """Write security event to file asynchronously."""
    async with aiofiles.open(file_path, 'a') as f:
        await f.write(json.dumps(event.dict(), default=str) + '\n')

async def analyze_security_logs_async(data: LogAnalysisRequest) -> LogAnalysisResult:
    """Analyze security logs for threats asynchronously (I/O-bound)."""
    log_file_path = data.log_file_path
    analysis_period_hours = data.analysis_period_hours
    
    threat_indicators = ThreatIndicators()
    analyzed_entries = 0
    
    try:
        async with aiofiles.open(log_file_path, 'r') as f:
            async for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    analyzed_entries += 1
                    
                    # Analyze for threats
                    if log_entry.get("event_type") == "login_failed":
                        threat_indicators.failed_logins += 1
                    
                    if log_entry.get("event_type") == "rate_limit_exceeded":
                        threat_indicators.rate_limit_violations += 1
                    
                    if log_entry.get("event_type") == "malicious_request":
                        threat_indicators.malicious_requests += 1
                        ip = log_entry.get("source_ip")
                        if ip and ip not in threat_indicators.suspicious_ips:
                            threat_indicators.suspicious_ips.append(ip)
                
                except json.JSONDecodeError:
                    continue
        
        # Calculate risk score (CPU-bound)
        risk_score = (
            threat_indicators.failed_logins * 0.3 +
            threat_indicators.rate_limit_violations * 0.4 +
            threat_indicators.malicious_requests * 0.5 +
            len(threat_indicators.suspicious_ips) * 0.2
        )
        
        risk_level = "HIGH" if risk_score > 5 else "MEDIUM" if risk_score > 2 else "LOW"
        
        return LogAnalysisResult(
            analysis_period_hours=analysis_period_hours,
            threat_indicators=threat_indicators,
            risk_score=risk_score,
            risk_level=risk_level,
            analysis_completed=True,
            analyzed_entries=analyzed_entries
        )
    
    except FileNotFoundError:
        return LogAnalysisResult(
            analysis_period_hours=analysis_period_hours,
            threat_indicators=threat_indicators,
            risk_score=0.0,
            risk_level="UNKNOWN",
            analysis_completed=False,
            error_message="Log file not found"
        ) 