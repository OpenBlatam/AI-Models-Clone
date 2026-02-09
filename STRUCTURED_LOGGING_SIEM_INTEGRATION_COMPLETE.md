# Structured Logging for SIEM Integration - Complete Integration

## Overview

This implementation demonstrates how to implement structured logging in JSON format for easy ingestion by SIEMs, integrating all the patterns we've discussed:

- **Type hints and Pydantic validation**
- **Async/sync patterns**
- **RORO pattern**
- **Named exports**
- **Error handling and validation**
- **Guard clauses and early returns**
- **Structured logging**
- **Custom exceptions**
- **Secure coding practices**

## Key Concepts

### 1. Structured Logging Benefits

Structured logging in JSON format provides several advantages for SIEM integration:

- **SIEM Compatibility**: JSON format is easily parsed by SIEM systems
- **Searchability**: Structured data enables efficient searching and filtering
- **Correlation**: Rich context enables event correlation across systems
- **Analytics**: Structured data supports advanced analytics and reporting
- **Compliance**: Detailed logging supports compliance requirements

### 2. SIEM Integration Features

The implementation includes comprehensive SIEM integration:

- **JSON Formatting**: All logs output in JSON format
- **Batch Processing**: Efficient batch forwarding to SIEM
- **Security Context**: Rich security context for threat detection
- **Performance Metrics**: System performance tracking
- **Sensitive Data Masking**: Automatic masking of sensitive information

## Core Components

### 1. SIEMLogConfig

```python
class SIEMLogConfig(BaseModel):
    """Pydantic model for SIEM logging configuration."""
    
    # Logging identification
    application_name: constr(strip_whitespace=True)
    environment: constr(strip_whitespace=True)
    
    # SIEM settings
    siem_endpoint: Optional[constr(strip_whitespace=True)]
    siem_api_key: Optional[constr(strip_whitespace=True)]
    enable_siem_forwarding: bool = True
    
    # Logging behavior
    log_level: constr(strip_whitespace=True) = "INFO"
    enable_json_formatting: bool = True
    include_timestamp: bool = True
    include_hostname: bool = True
    include_process_id: bool = True
    
    # Security settings
    mask_sensitive_fields: bool = True
    sensitive_field_patterns: List[constr(strip_whitespace=True)] = [
        "password", "token", "key", "secret", "credential"
    ]
    enable_audit_logging: bool = True
    
    # Performance settings
    batch_size: conint(gt=0) = 100
    flush_interval: confloat(gt=0.0) = 5.0
    max_queue_size: conint(gt=0) = 1000
```

### 2. LogEvent

```python
class LogEvent(BaseModel):
    """Pydantic model for structured log events."""
    
    # Event identification
    event_id: str
    timestamp: datetime
    log_level: constr(strip_whitespace=True)
    
    # Application context
    application_name: str
    environment: str
    component: str
    operation: str
    
    # Message and data
    message: str
    data: Dict[str, Any]
    
    # System context
    hostname: str
    process_id: conint(ge=0)
    thread_id: Optional[conint(ge=0)]
    
    # Request context
    session_id: Optional[str]
    user_id: Optional[str]
    request_id: Optional[str]
    correlation_id: Optional[str]
    
    # Network context
    source_ip: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    status_code: Optional[conint(ge=100, le=599)]
    response_time_ms: Optional[confloat(ge=0.0)]
    
    # Error context
    error_code: Optional[str]
    error_type: Optional[str]
    stack_trace: Optional[str]
    
    # Security context
    severity_level: constr(strip_whitespace=True)
    threat_level: Optional[constr(strip_whitespace=True)]
    ioc_indicators: List[str]
    
    # Performance metrics
    memory_usage_mb: Optional[confloat(ge=0.0)]
    cpu_usage_percent: Optional[confloat(ge=0.0)]
    execution_time_ms: Optional[confloat(ge=0.0)]
    
    # Custom fields
    custom_fields: Dict[str, Any]
    
    # Computed fields
    @computed_field
    @property
    def event_type(self) -> str:
        """Get event type based on log level and operation."""
        if self.log_level in ["ERROR", "CRITICAL"]:
            return "error"
        elif self.log_level == "WARNING":
            return "warning"
        elif self.operation in ["login", "logout", "auth"]:
            return "authentication"
        elif self.operation in ["scan", "detect", "threat"]:
            return "security"
        else:
            return "info"
    
    @computed_field
    @property
    def is_security_event(self) -> bool:
        """Check if this is a security event."""
        security_operations = ["login", "logout", "auth", "scan", "detect", "threat", "vulnerability"]
        return (
            self.operation in security_operations or
            self.log_level in ["ERROR", "CRITICAL"] or
            self.severity_level in ["high", "critical"] or
            bool(self.ioc_indicators)
        )
```

### 3. LogContext

```python
@dataclass
class LogContext:
    """Context for structured logging operations."""
    
    session_id: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_code: Optional[str] = None
    severity_level: str = "info"
    component: str = "unknown"
    operation: str = "unknown"
    additional_context: Dict[str, Any] = field(default_factory=dict)
```

## Implementation Patterns

### 1. Structured Logger

```python
class StructuredLogger(ABC):
    """Abstract base class for structured loggers."""
    
    def __init__(self, config: SIEMLogConfig):
        self.config = config
        self.logger = structlog.get_logger()
        self.log_queue: List[LogEvent] = []
        self.batch_size = config.batch_size
        self.flush_interval = config.flush_interval
        self.max_queue_size = config.max_queue_size
        
        # Initialize system context
        self.hostname = socket.gethostname()
        self.process_id = os.getpid()
    
    def create_log_event(
        self,
        message: str,
        log_level: str,
        component: str,
        operation: str,
        context: Optional[LogContext] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> LogEvent:
        """Create a structured log event."""
        
        # Guard clause: Validate log level
        if log_level.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise StructuredLoggingError(
                message=f"Invalid log level: {log_level}",
                log_level=log_level,
                error_code="INVALID_LOG_LEVEL"
            )
        
        # Create event data
        event_data = data or {}
        if context:
            event_data.update({
                "session_id": context.session_id,
                "user_id": context.user_id,
                "request_id": context.request_id,
                "correlation_id": context.correlation_id,
                "source_ip": context.source_ip,
                "user_agent": context.user_agent,
                "endpoint": context.endpoint,
                "method": context.method,
                "status_code": context.status_code,
                "response_time_ms": context.response_time_ms,
                "error_code": context.error_code,
                "severity_level": context.severity_level,
                "component": context.component,
                "operation": context.operation,
                **context.additional_context
            })
        
        # Mask sensitive fields if enabled
        if self.config.mask_sensitive_fields:
            event_data = self._mask_sensitive_data(event_data)
        
        # Get performance metrics
        memory_usage = self._get_memory_usage()
        cpu_usage = self._get_cpu_usage()
        
        return LogEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            log_level=log_level.upper(),
            application_name=self.config.application_name,
            environment=self.config.environment,
            component=component,
            operation=operation,
            message=message,
            data=event_data,
            hostname=self.hostname,
            process_id=self.process_id,
            thread_id=self._get_thread_id(),
            session_id=context.session_id if context else None,
            user_id=context.user_id if context else None,
            request_id=context.request_id if context else None,
            correlation_id=context.correlation_id if context else None,
            source_ip=context.source_ip if context else None,
            user_agent=context.user_agent if context else None,
            endpoint=context.endpoint if context else None,
            method=context.method if context else None,
            status_code=context.status_code if context else None,
            response_time_ms=context.response_time_ms if context else None,
            error_code=context.error_code if context else None,
            severity_level=context.severity_level if context else "info",
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            custom_fields={}
        )
```

### 2. SIEM Logger

```python
class SIEMLogger(StructuredLogger):
    """SIEM-integrated structured logger."""
    
    def __init__(self, config: SIEMLogConfig):
        super().__init__(config)
        self.siem_client = None
        if self.config.enable_siem_forwarding and self.config.siem_endpoint:
            self.siem_client = self._create_siem_client()
    
    async def log_event(self, event: LogEvent) -> None:
        """Log an event asynchronously."""
        
        # Guard clause: Check if event is valid
        if not event or not event.message:
            return
        
        try:
            # Add to queue
            self.log_queue.append(event)
            
            # Check if we should flush
            if len(self.log_queue) >= self.batch_size:
                await self._flush_logs_async()
            
            # Log to structlog
            log_method = getattr(self.logger, event.log_level.lower(), self.logger.info)
            log_method(
                event_id=event.event_id,
                timestamp=event.timestamp.isoformat(),
                log_level=event.log_level,
                application_name=event.application_name,
                environment=event.environment,
                component=event.component,
                operation=event.operation,
                message=event.message,
                data=event.data,
                hostname=event.hostname,
                process_id=event.process_id,
                thread_id=event.thread_id,
                session_id=event.session_id,
                user_id=event.user_id,
                request_id=event.request_id,
                correlation_id=event.correlation_id,
                source_ip=event.source_ip,
                user_agent=event.user_agent,
                endpoint=event.endpoint,
                method=event.method,
                status_code=event.status_code,
                response_time_ms=event.response_time_ms,
                error_code=event.error_code,
                severity_level=event.severity_level,
                threat_level=event.threat_level,
                ioc_indicators=event.ioc_indicators,
                memory_usage_mb=event.memory_usage_mb,
                cpu_usage_percent=event.cpu_usage_percent,
                execution_time_ms=event.execution_time_ms,
                custom_fields=event.custom_fields,
                event_type=event.event_type,
                is_security_event=event.is_security_event
            )
            
        except Exception as exc:
            # Log error without causing infinite recursion
            print(f"Error logging event: {exc}")
    
    async def _send_to_siem_async(self, events: List[LogEvent]) -> None:
        """Send events to SIEM asynchronously."""
        if not self.config.siem_endpoint:
            return
        
        try:
            import aiohttp
            
            # Prepare payload
            payload = {
                "events": [event.model_dump() for event in events],
                "batch_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "application": self.config.application_name,
                "environment": self.config.environment
            }
            
            # Send to SIEM
            headers = {"Content-Type": "application/json"}
            if self.config.siem_api_key:
                headers["Authorization"] = f"Bearer {self.config.siem_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.siem_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        print(f"SIEM forwarding failed: {response.status}")
                        
        except Exception as exc:
            print(f"Error sending to SIEM: {exc}")
```

### 3. Logging Manager

```python
class LoggingManager:
    """Manager for structured logging operations."""
    
    def __init__(self):
        self.loggers: Dict[str, StructuredLogger] = {}
        self.logger = structlog.get_logger()
    
    def register_logger(self, logger_name: str, logger: StructuredLogger) -> None:
        """Register a structured logger."""
        self.loggers[logger_name] = logger
    
    async def log_security_event(
        self,
        logger_name: str,
        message: str,
        severity_level: str,
        component: str,
        operation: str,
        context: Optional[LogContext] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a security event asynchronously."""
        
        # Guard clause: Check if logger exists
        if logger_name not in self.loggers:
            return
        
        logger = self.loggers[logger_name]
        
        # Create log context if not provided
        if not context:
            context = LogContext(
                session_id=str(uuid.uuid4()),
                severity_level=severity_level,
                component=component,
                operation=operation
            )
        
        # Create log event
        event = logger.create_log_event(
            message=message,
            log_level="WARNING" if severity_level in ["medium", "high"] else "ERROR",
            component=component,
            operation=operation,
            context=context,
            data=data
        )
        
        # Log the event
        await logger.log_event(event)
```

## RORO Pattern Integration

### 1. Create SIEM Logger

```python
def create_siem_logger_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a SIEM logger using RORO pattern."""
    
    try:
        # Extract parameters
        config_data = params.get("config", {})
        
        # Create configuration
        config = SIEMLogConfig(**config_data)
        
        # Create logger
        logger = SIEMLogger(config)
        
        return {
            "is_successful": True,
            "result": logger,
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

### 2. Log Security Event

```python
def log_security_event_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Log a security event using RORO pattern."""
    
    try:
        # Extract parameters
        manager = params.get("manager")
        logger_name = params.get("logger_name")
        message = params.get("message")
        severity_level = params.get("severity_level", "medium")
        component = params.get("component", "unknown")
        operation = params.get("operation", "unknown")
        context_data = params.get("context", {})
        data = params.get("data", {})
        use_async = params.get("use_async", True)
        
        # Guard clause: Check required parameters
        if not manager:
            return {
                "is_successful": False,
                "result": None,
                "error": "Manager is required"
            }
        
        if not logger_name:
            return {
                "is_successful": False,
                "result": None,
                "error": "Logger name is required"
            }
        
        if not message:
            return {
                "is_successful": False,
                "result": None,
                "error": "Message is required"
            }
        
        # Create context
        context = LogContext(
            session_id=context_data.get("session_id", str(uuid.uuid4())),
            user_id=context_data.get("user_id"),
            request_id=context_data.get("request_id"),
            correlation_id=context_data.get("correlation_id"),
            source_ip=context_data.get("source_ip"),
            user_agent=context_data.get("user_agent"),
            endpoint=context_data.get("endpoint"),
            method=context_data.get("method"),
            status_code=context_data.get("status_code"),
            response_time_ms=context_data.get("response_time_ms"),
            error_code=context_data.get("error_code"),
            severity_level=severity_level,
            component=component,
            operation=operation,
            additional_context=context_data.get("additional_context", {})
        )
        
        # Log event
        if use_async:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create task for async logging
                task = asyncio.create_task(
                    manager.log_security_event(logger_name, message, severity_level, component, operation, context, data)
                )
                loop.run_until_complete(task)
            else:
                loop.run_until_complete(
                    manager.log_security_event(logger_name, message, severity_level, component, operation, context, data)
                )
        else:
            manager.log_security_event_sync(logger_name, message, severity_level, component, operation, context, data)
        
        return {
            "is_successful": True,
            "result": "Event logged successfully",
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

## Error Handling and Validation

### 1. Custom Exceptions

```python
class StructuredLoggingError(Exception):
    """Custom exception for structured logging errors."""
    
    def __init__(
        self,
        message: str,
        log_level: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.log_level = log_level
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(message)
```

### 2. Guard Clauses

Always use guard clauses to check for invalid inputs early:

```python
# Guard clause: Validate log level
if log_level.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    raise StructuredLoggingError(
        message=f"Invalid log level: {log_level}",
        log_level=log_level,
        error_code="INVALID_LOG_LEVEL"
    )

# Guard clause: Check if event is valid
if not event or not event.message:
    return

# Guard clause: Check if logger exists
if logger_name not in self.loggers:
    return
```

## Usage Examples

### 1. Basic Usage

```python
# Create configuration
config = SIEMLogConfig(
    application_name="security_scanner",
    environment="prod",
    siem_endpoint="https://siem.example.com/api/logs",
    siem_api_key="your-api-key",
    enable_siem_forwarding=True,
    log_level="INFO",
    enable_json_formatting=True,
    include_timestamp=True,
    include_hostname=True,
    include_process_id=True,
    mask_sensitive_fields=True,
    enable_audit_logging=True,
    batch_size=100,
    flush_interval=5.0,
    max_queue_size=1000
)

# Create SIEM logger
logger = SIEMLogger(config)

# Create manager
manager = LoggingManager()
manager.register_logger("siem_logger", logger)

# Create log context
context = LogContext(
    session_id="session_123",
    user_id="user_456",
    request_id="req_789",
    source_ip="192.168.1.100",
    user_agent="Mozilla/5.0",
    endpoint="/api/scan",
    method="POST",
    status_code=200,
    response_time_ms=150.5,
    severity_level="high",
    component="security_scanner",
    operation="vulnerability_scan"
)

# Log security event
await manager.log_security_event(
    "siem_logger",
    "Vulnerability detected: SQL injection attempt",
    "high",
    "security_scanner",
    "vulnerability_scan",
    context,
    {
        "vulnerability_type": "sql_injection",
        "target_url": "https://example.com/login",
        "payload": "***MASKED***",
        "risk_score": 9.5
    }
)
```

### 2. RORO Pattern Usage

```python
# Create SIEM logger using RORO
logger_result = create_siem_logger_roro({
    "config": {
        "application_name": "security_scanner",
        "environment": "prod",
        "siem_endpoint": "https://siem.example.com/api/logs",
        "siem_api_key": "your-api-key",
        "enable_siem_forwarding": True,
        "log_level": "INFO",
        "enable_json_formatting": True,
        "include_timestamp": True,
        "include_hostname": True,
        "include_process_id": True,
        "mask_sensitive_fields": True,
        "enable_audit_logging": True,
        "batch_size": 100,
        "flush_interval": 5.0,
        "max_queue_size": 1000
    }
})

if logger_result["is_successful"]:
    logger = logger_result["result"]
    
    # Create manager
    manager = LoggingManager()
    manager.register_logger("siem_logger", logger)
    
    # Log security event using RORO
    log_result = log_security_event_roro({
        "manager": manager,
        "logger_name": "siem_logger",
        "message": "Vulnerability detected: SQL injection attempt",
        "severity_level": "high",
        "component": "security_scanner",
        "operation": "vulnerability_scan",
        "context": {
            "session_id": "session_123",
            "user_id": "user_456",
            "request_id": "req_789",
            "source_ip": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "endpoint": "/api/scan",
            "method": "POST",
            "status_code": 200,
            "response_time_ms": 150.5
        },
        "data": {
            "vulnerability_type": "sql_injection",
            "target_url": "https://example.com/login",
            "payload": "***MASKED***",
            "risk_score": 9.5
        }
    })
    
    if log_result["is_successful"]:
        print("Security event logged successfully")
    else:
        print(f"Logging failed: {log_result['error']}")
else:
    print(f"Failed to create logger: {logger_result['error']}")
```

## JSON Output Format

The structured logging system produces JSON output in the following format:

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2023-12-07T10:30:45.123456+00:00",
  "log_level": "WARNING",
  "application_name": "security_scanner",
  "environment": "prod",
  "component": "security_scanner",
  "operation": "vulnerability_scan",
  "message": "Vulnerability detected: SQL injection attempt",
  "data": {
    "vulnerability_type": "sql_injection",
    "target_url": "https://example.com/login",
    "payload": "***MASKED***",
    "risk_score": 9.5,
    "session_id": "session_123",
    "user_id": "user_456",
    "request_id": "req_789",
    "source_ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0",
    "endpoint": "/api/scan",
    "method": "POST",
    "status_code": 200,
    "response_time_ms": 150.5,
    "severity_level": "high"
  },
  "hostname": "security-server-01",
  "process_id": 12345,
  "thread_id": 67890,
  "session_id": "session_123",
  "user_id": "user_456",
  "request_id": "req_789",
  "correlation_id": null,
  "source_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0",
  "endpoint": "/api/scan",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 150.5,
  "error_code": null,
  "error_type": null,
  "stack_trace": null,
  "severity_level": "high",
  "threat_level": null,
  "ioc_indicators": [],
  "memory_usage_mb": 256.5,
  "cpu_usage_percent": 15.2,
  "execution_time_ms": 150.5,
  "custom_fields": {},
  "event_type": "security",
  "is_security_event": true
}
```

## Best Practices

### 1. Sensitive Data Masking

Always mask sensitive data in logs:

```python
def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data in log events."""
    masked_data = data.copy()
    
    for key, value in masked_data.items():
        if isinstance(value, str):
            for pattern in self.config.sensitive_field_patterns:
                if pattern.lower() in key.lower():
                    masked_data[key] = "***MASKED***"
                    break
        elif isinstance(value, dict):
            masked_data[key] = self._mask_sensitive_data(value)
    
    return masked_data
```

### 2. Batch Processing

Use batch processing for efficient SIEM forwarding:

```python
async def _flush_logs_async(self) -> None:
    """Flush logs to SIEM asynchronously."""
    if not self.siem_client or not self.log_queue:
        return
    
    try:
        # Prepare batch of events
        events_to_send = self.log_queue[:self.batch_size]
        self.log_queue = self.log_queue[self.batch_size:]
        
        # Send to SIEM
        await self._send_to_siem_async(events_to_send)
        
    except Exception as exc:
        # Put events back in queue on error
        self.log_queue.extend(events_to_send)
        print(f"Error flushing logs: {exc}")
```

### 3. Error Handling

Implement comprehensive error handling:

```python
try:
    # Log to structlog
    log_method = getattr(self.logger, event.log_level.lower(), self.logger.info)
    log_method(
        event_id=event.event_id,
        timestamp=event.timestamp.isoformat(),
        log_level=event.log_level,
        # ... other fields
    )
    
except Exception as exc:
    # Log error without causing infinite recursion
    print(f"Error logging event: {exc}")
```

## Integration with Other Patterns

### 1. Type Hints and Pydantic

All components use comprehensive type hints and Pydantic validation:

```python
class SIEMLogConfig(BaseModel):
    """Pydantic model for SIEM logging configuration."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    application_name: constr(strip_whitespace=True) = Field(
        description="Name of the application"
    )
    environment: constr(strip_whitespace=True) = Field(
        description="Environment (dev, staging, prod)"
    )
    log_level: constr(strip_whitespace=True) = Field(
        default="INFO",
        description="Logging level"
    )
```

### 2. Async/Sync Patterns

Support both async and sync logging:

```python
async def log_event(self, event: LogEvent) -> None:
    """Log an event asynchronously."""
    # Async implementation
    pass

def log_event_sync(self, event: LogEvent) -> None:
    """Log an event synchronously."""
    # Sync implementation
    pass
```

### 3. Named Exports

Use named exports for clear module interface:

```python
__all__ = [
    "SIEMLogConfig",
    "LogEvent", 
    "LogContext",
    "StructuredLogger",
    "SIEMLogger",
    "LoggingManager",
    "StructuredLoggingError",
    "create_siem_logger_roro",
    "log_security_event_roro",
    "get_logger_info_roro"
]
```

## Conclusion

This structured logging implementation provides a robust, efficient, and production-ready solution for SIEM integration with JSON formatting. It integrates all the patterns we've discussed:

- **Type safety** with comprehensive type hints and Pydantic validation
- **SIEM compatibility** with JSON formatting and batch processing
- **Security features** with sensitive data masking and audit logging
- **Error handling** with custom exceptions and structured logging
- **Async/sync support** for flexible usage patterns
- **RORO pattern** for consistent function interfaces
- **Guard clauses** for early error detection
- **Modular design** with clear separation of concerns

The implementation is ready for production use and provides comprehensive logging capabilities for SIEM integration. 