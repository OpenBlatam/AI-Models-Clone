# Dependency Injection for Shared Resources - Complete Integration

## Overview

This implementation demonstrates how to implement dependency injection for shared resources like network sessions and crypto backends, integrating all the patterns we've discussed:

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

### 1. Dependency Injection Benefits

Dependency injection for shared resources provides several advantages:

- **Resource Management**: Centralized management of shared resources
- **Singleton Pattern**: Ensure single instances of expensive resources
- **Lazy Initialization**: Resources created only when needed
- **Memory Optimization**: Efficient memory usage through caching
- **Testability**: Easy to mock and test with dependency injection

### 2. Core Components

#### SharedResourceConfig
```python
class SharedResourceConfig(BaseModel):
    """Pydantic model for shared resource configuration."""
    
    # Resource identification
    resource_name: constr(strip_whitespace=True)
    resource_type: constr(strip_whitespace=True)
    
    # Resource behavior
    singleton_mode: bool = True
    lazy_initialization: bool = True
    auto_cleanup: bool = True
    
    # Performance settings
    max_connections: conint(gt=0) = 100
    connection_timeout: confloat(gt=0.0) = 30.0
    retry_attempts: conint(ge=0, le=5) = 3
    
    # Security settings
    enable_ssl_verification: bool = True
    encryption_key_size: conint(ge=128, le=4096) = 256
    hash_algorithm: constr(strip_whitespace=True) = "SHA256"
    
    # Logging and monitoring
    enable_resource_logs: bool = True
    track_memory_usage: bool = True
```

#### ResourceCreationResult
```python
class ResourceCreationResult(BaseModel):
    """Pydantic model for resource creation results."""
    
    # Creation status
    is_successful: bool
    resource_name: str
    resource_type: str
    resource_object: Optional[Any]
    
    # Performance metrics
    creation_duration: confloat(ge=0.0)
    memory_usage_before: conint(ge=0)
    memory_usage_after: conint(ge=0)
    memory_increase: conint(ge=0)
    
    # Error information
    error_message: Optional[str]
    error_type: Optional[str]
    stack_trace: Optional[str]
    
    # Resource information
    resource_size: Optional[conint(ge=0)]
    dependencies_created: List[str]
    connection_count: Optional[conint(ge=0)]
    
    # Computed fields
    @computed_field
    @property
    def memory_usage_mb(self) -> float:
        return self.memory_usage_after / (1024 * 1024)
    
    @computed_field
    @property
    def memory_increase_mb(self) -> float:
        return self.memory_increase / (1024 * 1024)
    
    @computed_field
    @property
    def creation_duration_ms(self) -> float:
        return self.creation_duration * 1000
```

## Implementation Patterns

### 1. Abstract Base Class Pattern

```python
class SharedResource(ABC):
    """Abstract base class for shared resources."""
    
    def __init__(self, config: SharedResourceConfig):
        self.config = config
        self._resource_cache: Dict[str, Any] = {}
        self._creation_contexts: Dict[str, ResourceContext] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def create_resource(self, resource_name: str) -> ResourceCreationResult:
        """Create a resource asynchronously."""
        pass
    
    @abstractmethod
    def create_resource_sync(self, resource_name: str) -> ResourceCreationResult:
        """Create a resource synchronously."""
        pass
    
    def get_cached_resource(self, resource_name: str) -> Optional[Any]:
        """Get a cached resource if available."""
        return self._resource_cache.get(resource_name)
    
    def is_resource_created(self, resource_name: str) -> bool:
        """Check if a resource is already created."""
        return resource_name in self._resource_cache
```

### 2. Network Session Resource

```python
class NetworkSessionResource(SharedResource):
    """Shared resource for network sessions."""
    
    def __init__(self, config: SharedResourceConfig):
        super().__init__(config)
        self.session_types = {
            "aiohttp": self._create_aiohttp_session,
            "httpx": self._create_httpx_session,
            "requests": self._create_requests_session
        }
    
    async def create_resource(self, resource_name: str) -> ResourceCreationResult:
        """Create a network session resource asynchronously."""
        
        # Guard clause: Check if resource name is valid
        if not resource_name or resource_name not in self.session_types:
            return ResourceCreationResult(
                is_successful=False,
                resource_name=resource_name,
                resource_type="network_session",
                creation_duration=0.0,
                memory_usage_before=0,
                memory_usage_after=0,
                memory_increase=0,
                error_message=f"Invalid network session type: {resource_name}",
                error_type="InvalidResourceError"
            )
        
        # Guard clause: Check if already cached
        if self.is_resource_created(resource_name):
            cached_resource = self.get_cached_resource(resource_name)
            return ResourceCreationResult(
                is_successful=True,
                resource_name=resource_name,
                resource_type="network_session",
                resource_object=cached_resource,
                creation_duration=0.0,
                memory_usage_before=self._get_memory_usage(),
                memory_usage_after=self._get_memory_usage(),
                memory_increase=0,
                dependencies_created=["cached"]
            )
        
        # Start creation context
        context = ResourceContext(resource_name=resource_name, resource_type="network_session")
        self._creation_contexts[resource_name] = context
        
        # Track memory before creation
        if self.config.track_memory_usage:
            context.memory_before = self._get_memory_usage()
        
        start_time = time.time()
        
        try:
            # Create the resource
            session_creator = self.session_types[resource_name]
            resource_object = await session_creator()
            
            # Cache the resource if requested
            if self.config.singleton_mode:
                self._resource_cache[resource_name] = resource_object
            
            # Complete creation context
            context.complete_creation(True)
            
            return ResourceCreationResult(
                is_successful=True,
                resource_name=resource_name,
                resource_type="network_session",
                resource_object=resource_object,
                creation_duration=time.time() - start_time,
                memory_usage_before=context.memory_before or 0,
                memory_usage_after=self._get_memory_usage(),
                memory_increase=(self._get_memory_usage() - (context.memory_before or 0)),
                dependencies_created=context.dependencies_created,
                connection_count=self.config.max_connections
            )
            
        except Exception as exc:
            # Complete creation context with error
            context.complete_creation(False, str(exc))
            
            return ResourceCreationResult(
                is_successful=False,
                resource_name=resource_name,
                resource_type="network_session",
                creation_duration=time.time() - start_time,
                memory_usage_before=context.memory_before or 0,
                memory_usage_after=self._get_memory_usage(),
                memory_increase=(self._get_memory_usage() - (context.memory_before or 0)),
                error_message=str(exc),
                error_type=type(exc).__name__,
                stack_trace=self._get_stack_trace()
            )
```

### 3. Crypto Backend Resource

```python
class CryptoBackendResource(SharedResource):
    """Shared resource for crypto backends."""
    
    def __init__(self, config: SharedResourceConfig):
        super().__init__(config)
        self.crypto_types = {
            "fernet": self._create_fernet_backend,
            "pbkdf2": self._create_pbkdf2_backend,
            "custom": self._create_custom_backend
        }
    
    async def _create_fernet_backend(self) -> Fernet:
        """Create a Fernet crypto backend."""
        # Generate a key
        key = Fernet.generate_key()
        return Fernet(key)
    
    def _create_pbkdf2_backend(self):
        """Create a PBKDF2 crypto backend."""
        # Generate salt
        salt = os.urandom(16)
        
        # Create KDF
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        return {
            "kdf": kdf,
            "salt": salt,
            "algorithm": "PBKDF2"
        }
    
    def _create_custom_backend(self):
        """Create a custom crypto backend."""
        return {
            "algorithm": "custom",
            "key_size": self.config.encryption_key_size,
            "hash_algorithm": self.config.hash_algorithm
        }
```

### 4. Dependency Injection Manager

```python
class DependencyInjectionManager:
    """Manager for dependency injection of shared resources."""
    
    def __init__(self):
        self.resources: Dict[str, SharedResource] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_resource(self, resource_name: str, resource: SharedResource) -> None:
        """Register a shared resource."""
        self.resources[resource_name] = resource
    
    async def create_resource_async(
        self,
        resource_name: str,
        resource_type: str
    ) -> ResourceCreationResult:
        """Create a resource asynchronously using the specified resource manager."""
        
        # Guard clause: Check if resource exists
        if resource_name not in self.resources:
            return ResourceCreationResult(
                is_successful=False,
                resource_name=resource_name,
                resource_type=resource_type,
                creation_duration=0.0,
                memory_usage_before=0,
                memory_usage_after=0,
                memory_increase=0,
                error_message=f"Resource not found: {resource_name}",
                error_type="ResourceNotFoundError"
            )
        
        resource = self.resources[resource_name]
        return await resource.create_resource(resource_type)
```

## RORO Pattern Integration

### 1. Create Shared Resource

```python
def create_shared_resource_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a shared resource using RORO pattern."""
    
    try:
        # Extract parameters
        resource_type = params.get("resource_type", "network_session")
        config_data = params.get("config", {})
        
        # Create configuration
        config = SharedResourceConfig(**config_data)
        
        # Create appropriate resource
        if resource_type == "network_session":
            resource = NetworkSessionResource(config)
        elif resource_type == "crypto_backend":
            resource = CryptoBackendResource(config)
        else:
            return {
                "is_successful": False,
                "result": None,
                "error": f"Unknown resource type: {resource_type}"
            }
        
        return {
            "is_successful": True,
            "result": resource,
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

### 2. Create Resource

```python
def create_resource_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Create a resource using RORO pattern."""
    
    try:
        # Extract parameters
        resource_manager = params.get("resource_manager")
        resource_name = params.get("resource_name")
        resource_type = params.get("resource_type")
        use_async = params.get("use_async", True)
        
        # Guard clause: Check required parameters
        if not resource_manager:
            return {
                "is_successful": False,
                "result": None,
                "error": "Resource manager is required"
            }
        
        if not resource_name:
            return {
                "is_successful": False,
                "result": None,
                "error": "Resource name is required"
            }
        
        if not resource_type:
            return {
                "is_successful": False,
                "result": None,
                "error": "Resource type is required"
            }
        
        # Create resource
        if use_async and hasattr(resource_manager, 'create_resource'):
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create task for async creation
                task = asyncio.create_task(resource_manager.create_resource(resource_type))
                result = loop.run_until_complete(task)
            else:
                result = loop.run_until_complete(resource_manager.create_resource(resource_type))
        else:
            result = resource_manager.create_resource_sync(resource_type)
        
        return {
            "is_successful": True,
            "result": result,
            "error": None
        }
        
    except Exception as exc:
        return {
            "is_successful": False,
            "result": None,
            "error": str(exc)
        }
```

### 3. Get Resource Info

```python
def get_resource_info_roro(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get resource information using RORO pattern."""
    
    try:
        # Extract parameters
        resource_manager = params.get("resource_manager")
        
        # Guard clause: Check required parameters
        if not resource_manager:
            return {
                "is_successful": False,
                "result": None,
                "error": "Resource manager is required"
            }
        
        resource_info = resource_manager.get_cache_info()
        
        return {
            "is_successful": True,
            "result": resource_info,
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
class DependencyInjectionError(Exception):
    """Custom exception for dependency injection errors."""
    
    def __init__(
        self,
        message: str,
        resource_name: Optional[str] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.resource_name = resource_name
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)
        super().__init__(message)
```

### 2. Resource Context

```python
@dataclass
class ResourceContext:
    """Context for resource management operations."""
    
    resource_name: str
    resource_type: str
    creation_start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    creation_end_time: Optional[datetime] = None
    memory_before: Optional[int] = None
    memory_after: Optional[int] = None
    creation_duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    resource_size: Optional[int] = None
    dependencies_created: List[str] = field(default_factory=list)
    
    def complete_creation(self, success: bool, error_message: Optional[str] = None) -> None:
        """Complete the resource creation operation."""
        self.creation_end_time = datetime.now(timezone.utc)
        self.creation_duration = (self.creation_end_time - self.creation_start_time).total_seconds()
        self.success = success
        self.error_message = error_message
```

## Usage Examples

### 1. Basic Usage

```python
# Create configuration for network session
network_config = SharedResourceConfig(
    resource_name="network_session",
    resource_type="network_session",
    singleton_mode=True,
    lazy_initialization=True,
    max_connections=50,
    connection_timeout=30.0,
    enable_ssl_verification=True
)

# Create network session resource
network_resource = NetworkSessionResource(network_config)

# Create resource asynchronously
result = await network_resource.create_resource("aiohttp")

print(f"Creation successful: {result.is_successful}")
print(f"Creation duration: {result.creation_duration:.3f}s")
print(f"Memory increase: {result.memory_increase_mb:.2f}MB")

if result.is_successful:
    print(f"Resource created: {result.resource_name}")
    print(f"Resource type: {result.resource_type}")
    print(f"Connection count: {result.connection_count}")
else:
    print(f"Creation failed: {result.error_message}")
```

### 2. Using Dependency Injection Manager

```python
# Create manager
manager = DependencyInjectionManager()

# Register resources
network_config = SharedResourceConfig(
    resource_name="network_session",
    resource_type="network_session",
    singleton_mode=True
)
network_resource = NetworkSessionResource(network_config)
manager.register_resource("network", network_resource)

crypto_config = SharedResourceConfig(
    resource_name="crypto_backend",
    resource_type="crypto_backend",
    singleton_mode=True
)
crypto_resource = CryptoBackendResource(crypto_config)
manager.register_resource("crypto", crypto_resource)

# Create resources
network_result = await manager.create_resource_async("network", "aiohttp")
crypto_result = await manager.create_resource_async("crypto", "fernet")

if network_result.is_successful and crypto_result.is_successful:
    network_session = network_result.resource_object
    crypto_backend = crypto_result.resource_object
    # Use the shared resources
else:
    print(f"Failed to create resources")
```

### 3. RORO Pattern Usage

```python
# Create shared resource using RORO
resource_result = create_shared_resource_roro({
    "resource_type": "network_session",
    "config": {
        "resource_name": "network_session",
        "resource_type": "network_session",
        "singleton_mode": True,
        "lazy_initialization": True,
        "max_connections": 50,
        "connection_timeout": 30.0,
        "enable_ssl_verification": True
    }
})

if resource_result["is_successful"]:
    resource_manager = resource_result["result"]
    
    # Create resource using RORO
    create_result = create_resource_roro({
        "resource_manager": resource_manager,
        "resource_name": "aiohttp",
        "resource_type": "aiohttp",
        "use_async": True
    })
    
    if create_result["is_successful"]:
        result = create_result["result"]
        print(f"Resource created successfully: {result.resource_name}")
        print(f"Memory usage: {result.memory_usage_mb:.2f}MB")
        print(f"Connection count: {result.connection_count}")
    else:
        print(f"Creation failed: {create_result['error']}")
else:
    print(f"Failed to create resource manager: {resource_result['error']}")
```

## Performance Monitoring

### 1. Memory Tracking

```python
# Track memory usage during creation
if config.track_memory_usage:
    context.memory_before = self._get_memory_usage()

# After creation
memory_after = self._get_memory_usage()
memory_increase = memory_after - context.memory_before

print(f"Memory before: {context.memory_before / (1024*1024):.2f}MB")
print(f"Memory after: {memory_after / (1024*1024):.2f}MB")
print(f"Memory increase: {memory_increase / (1024*1024):.2f}MB")
```

### 2. Creation Duration Tracking

```python
start_time = time.time()

# Create resource
resource_object = await resource_manager.create_resource("aiohttp")

creation_duration = time.time() - start_time
print(f"Creation duration: {creation_duration:.3f} seconds")
```

### 3. Cache Information

```python
# Get cache information
cache_info = resource_manager.get_cache_info()
print(f"Cached resources: {cache_info['cached_resources']}")
print(f"Cache size: {cache_info['cache_size']}")
print(f"Memory usage: {cache_info['memory_usage_mb']:.2f}MB")
```

## Best Practices

### 1. Guard Clauses

Always use guard clauses to check for invalid inputs early:

```python
# Guard clause: Check if resource name is valid
if not resource_name or resource_name not in self.session_types:
    return ResourceCreationResult(
        is_successful=False,
        resource_name=resource_name,
        resource_type="network_session",
        creation_duration=0.0,
        memory_usage_before=0,
        memory_usage_after=0,
        memory_increase=0,
        error_message=f"Invalid network session type: {resource_name}",
        error_type="InvalidResourceError"
    )

# Guard clause: Check if already cached
if self.is_resource_created(resource_name):
    cached_resource = self.get_cached_resource(resource_name)
    return ResourceCreationResult(
        is_successful=True,
        resource_name=resource_name,
        resource_type="network_session",
        resource_object=cached_resource,
        creation_duration=0.0,
        memory_usage_before=self._get_memory_usage(),
        memory_usage_after=self._get_memory_usage(),
        memory_increase=0,
        dependencies_created=["cached"]
    )
```

### 2. Error Handling

Use comprehensive error handling with custom exceptions:

```python
try:
    # Create the resource
    session_creator = self.session_types[resource_name]
    resource_object = await session_creator()
    
    # Cache the resource if requested
    if self.config.singleton_mode:
        self._resource_cache[resource_name] = resource_object
    
    # Complete creation context
    context.complete_creation(True)
    
    return ResourceCreationResult(...)
    
except Exception as exc:
    # Complete creation context with error
    context.complete_creation(False, str(exc))
    
    return ResourceCreationResult(
        is_successful=False,
        resource_name=resource_name,
        resource_type="network_session",
        creation_duration=time.time() - start_time,
        memory_usage_before=context.memory_before or 0,
        memory_usage_after=self._get_memory_usage(),
        memory_increase=(self._get_memory_usage() - (context.memory_before or 0)),
        error_message=str(exc),
        error_type=type(exc).__name__,
        stack_trace=self._get_stack_trace()
    )
```

### 3. Resource Management

Implement proper resource management:

```python
def clear_cache(self, resource_name: Optional[str] = None) -> None:
    """Clear resource cache."""
    if resource_name:
        self._resource_cache.pop(resource_name, None)
    else:
        self._resource_cache.clear()

def get_cache_info(self) -> Dict[str, Any]:
    """Get information about the resource cache."""
    return {
        "cached_resources": list(self._resource_cache.keys()),
        "cache_size": len(self._resource_cache),
        "memory_usage": self._get_memory_usage(),
        "memory_usage_mb": self._get_memory_usage() / (1024 * 1024)
    }
```

## Integration with Other Patterns

### 1. Type Hints and Pydantic

All components use comprehensive type hints and Pydantic validation:

```python
class SharedResourceConfig(BaseModel):
    """Pydantic model for shared resource configuration."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    resource_name: constr(strip_whitespace=True) = Field(
        description="Name of the shared resource"
    )
    max_connections: conint(gt=0) = Field(
        default=100,
        description="Maximum number of connections for network resources"
    )
    connection_timeout: confloat(gt=0.0) = Field(
        default=30.0,
        description="Connection timeout in seconds"
    )
```

### 2. Async/Sync Patterns

Support both async and sync resource creation:

```python
async def create_resource(self, resource_name: str) -> ResourceCreationResult:
    """Create a resource asynchronously."""
    # Async implementation
    pass

def create_resource_sync(self, resource_name: str) -> ResourceCreationResult:
    """Create a resource synchronously."""
    # Sync implementation
    pass
```

### 3. Named Exports

Use named exports for clear module interface:

```python
__all__ = [
    "SharedResourceConfig",
    "ResourceCreationResult", 
    "SharedResource",
    "NetworkSessionResource",
    "CryptoBackendResource",
    "DependencyInjectionManager",
    "DependencyInjectionError",
    "create_shared_resource_roro",
    "create_resource_roro",
    "get_resource_info_roro"
]
```

## Conclusion

This dependency injection implementation provides a robust, efficient, and production-ready solution for managing shared resources like network sessions and crypto backends. It integrates all the patterns we've discussed:

- **Type safety** with comprehensive type hints and Pydantic validation
- **Performance optimization** with memory tracking and caching
- **Error handling** with custom exceptions and structured logging
- **Async/sync support** for flexible usage patterns
- **RORO pattern** for consistent function interfaces
- **Guard clauses** for early error detection
- **Modular design** with clear separation of concerns

The implementation is ready for production use and can be easily extended to support other types of shared resources beyond network sessions and crypto backends. 