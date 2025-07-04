"""
ULTRA EXTREME V9 - DOMAIN ENTITIES
==================================
Core business entities with clean architecture principles
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import uuid
from enum import Enum

# Base classes
class Entity(ABC):
    """Base entity class"""
    
    def __init__(self, id: str = None):
        self._id = id or str(uuid.uuid4())
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._version = 1
        
    @property
    def id(self) -> str:
        return self._id
        
    @property
    def created_at(self) -> datetime:
        return self._created_at
        
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
        
    @property
    def version(self) -> int:
        return self._version
        
    def update(self):
        """Update entity timestamp and version"""
        self._updated_at = datetime.utcnow()
        self._version += 1
        
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
        
    def __hash__(self):
        return hash(self.id)
        
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class ValueObject(ABC):
    """Base value object class"""
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
        
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))
        
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

# Enums
class OptimizationType(Enum):
    """Optimization types"""
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"
    TRANSLATION = "translation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    REAL_TIME = "real_time"
    BATCH = "batch"

class ModelType(Enum):
    """AI model types"""
    GPT = "gpt"
    BERT = "bert"
    T5 = "t5"
    CUSTOM = "custom"
    QUANTIZED = "quantized"

class ProcessingStatus(Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Value Objects
@dataclass(frozen=True)
class TextContent(ValueObject):
    """Text content value object"""
    content: str
    language: str = "en"
    encoding: str = "utf-8"
    
    def __post_init__(self):
        if not self.content:
            raise ValueError("Content cannot be empty")
        if len(self.content) > 1000000:  # 1MB limit
            raise ValueError("Content too large")

@dataclass(frozen=True)
class ModelConfig(ValueObject):
    """Model configuration value object"""
    model_type: ModelType
    model_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    quantization: bool = False
    gpu_acceleration: bool = True
    
    def __post_init__(self):
        if not self.model_name:
            raise ValueError("Model name cannot be empty")

@dataclass(frozen=True)
class PerformanceMetrics(ValueObject):
    """Performance metrics value object"""
    latency_ms: float
    throughput_rps: float
    memory_usage_mb: float
    gpu_utilization_percent: float = 0.0
    cache_hit_ratio: float = 0.0
    error_rate: float = 0.0
    
    def __post_init__(self):
        if self.latency_ms < 0:
            raise ValueError("Latency cannot be negative")
        if self.throughput_rps < 0:
            raise ValueError("Throughput cannot be negative")
        if self.memory_usage_mb < 0:
            raise ValueError("Memory usage cannot be negative")

@dataclass(frozen=True)
class SecurityConfig(ValueObject):
    """Security configuration value object"""
    encryption_enabled: bool = True
    authentication_required: bool = True
    rate_limiting_enabled: bool = True
    max_requests_per_minute: int = 100
    allowed_origins: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.max_requests_per_minute <= 0:
            raise ValueError("Max requests per minute must be positive")

# Entities
class OptimizationRequest(Entity):
    """Optimization request entity"""
    
    def __init__(
        self,
        text_content: TextContent,
        optimization_type: OptimizationType,
        model_config: ModelConfig,
        security_config: SecurityConfig,
        id: str = None
    ):
        super().__init__(id)
        self._text_content = text_content
        self._optimization_type = optimization_type
        self._model_config = model_config
        self._security_config = security_config
        self._status = ProcessingStatus.PENDING
        self._result = None
        self._error_message = None
        self._performance_metrics = None
        self._processing_start_time = None
        self._processing_end_time = None
        
    @property
    def text_content(self) -> TextContent:
        return self._text_content
        
    @property
    def optimization_type(self) -> OptimizationType:
        return self._optimization_type
        
    @property
    def model_config(self) -> ModelConfig:
        return self._model_config
        
    @property
    def security_config(self) -> SecurityConfig:
        return self._security_config
        
    @property
    def status(self) -> ProcessingStatus:
        return self._status
        
    @property
    def result(self) -> Optional[Dict[str, Any]]:
        return self._result
        
    @property
    def error_message(self) -> Optional[str]:
        return self._error_message
        
    @property
    def performance_metrics(self) -> Optional[PerformanceMetrics]:
        return self._performance_metrics
        
    def start_processing(self):
        """Start processing the request"""
        if self._status != ProcessingStatus.PENDING:
            raise ValueError("Request is not in pending status")
            
        self._status = ProcessingStatus.PROCESSING
        self._processing_start_time = datetime.utcnow()
        self.update()
        
    def complete_processing(self, result: Dict[str, Any], metrics: PerformanceMetrics):
        """Complete processing with result"""
        if self._status != ProcessingStatus.PROCESSING:
            raise ValueError("Request is not in processing status")
            
        self._status = ProcessingStatus.COMPLETED
        self._result = result
        self._performance_metrics = metrics
        self._processing_end_time = datetime.utcnow()
        self.update()
        
    def fail_processing(self, error_message: str):
        """Fail processing with error"""
        if self._status != ProcessingStatus.PROCESSING:
            raise ValueError("Request is not in processing status")
            
        self._status = ProcessingStatus.FAILED
        self._error_message = error_message
        self._processing_end_time = datetime.utcnow()
        self.update()
        
    def cancel_processing(self):
        """Cancel processing"""
        if self._status not in [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]:
            raise ValueError("Request cannot be cancelled")
            
        self._status = ProcessingStatus.CANCELLED
        self._processing_end_time = datetime.utcnow()
        self.update()
        
    @property
    def processing_duration_ms(self) -> Optional[float]:
        """Get processing duration in milliseconds"""
        if self._processing_start_time and self._processing_end_time:
            return (self._processing_end_time - self._processing_start_time).total_seconds() * 1000
        return None
        
    def is_completed(self) -> bool:
        """Check if request is completed"""
        return self._status == ProcessingStatus.COMPLETED
        
    def is_failed(self) -> bool:
        """Check if request failed"""
        return self._status == ProcessingStatus.FAILED
        
    def is_cancelled(self) -> bool:
        """Check if request is cancelled"""
        return self._status == ProcessingStatus.CANCELLED

class AIModel(Entity):
    """AI model entity"""
    
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        version: str,
        performance_metrics: PerformanceMetrics,
        id: str = None
    ):
        super().__init__(id)
        self._name = name
        self._model_config = model_config
        self._version = version
        self._performance_metrics = performance_metrics
        self._is_active = True
        self._load_count = 0
        self._last_used = None
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def model_config(self) -> ModelConfig:
        return self._model_config
        
    @property
    def version(self) -> str:
        return self._version
        
    @property
    def performance_metrics(self) -> PerformanceMetrics:
        return self._performance_metrics
        
    @property
    def is_active(self) -> bool:
        return self._is_active
        
    @property
    def load_count(self) -> int:
        return self._load_count
        
    @property
    def last_used(self) -> Optional[datetime]:
        return self._last_used
        
    def activate(self):
        """Activate the model"""
        self._is_active = True
        self.update()
        
    def deactivate(self):
        """Deactivate the model"""
        self._is_active = False
        self.update()
        
    def increment_load_count(self):
        """Increment load count"""
        self._load_count += 1
        self._last_used = datetime.utcnow()
        self.update()
        
    def update_performance_metrics(self, metrics: PerformanceMetrics):
        """Update performance metrics"""
        self._performance_metrics = metrics
        self.update()

class CacheEntry(Entity):
    """Cache entry entity"""
    
    def __init__(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 3600,
        id: str = None
    ):
        super().__init__(id)
        self._key = key
        self._value = value
        self._ttl_seconds = ttl_seconds
        self._expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self._access_count = 0
        self._last_accessed = datetime.utcnow()
        
    @property
    def key(self) -> str:
        return self._key
        
    @property
    def value(self) -> Any:
        return self._value
        
    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds
        
    @property
    def expires_at(self) -> datetime:
        return self._expires_at
        
    @property
    def access_count(self) -> int:
        return self._access_count
        
    @property
    def last_accessed(self) -> datetime:
        return self._last_accessed
        
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self._expires_at
        
    def access(self):
        """Record cache access"""
        self._access_count += 1
        self._last_accessed = datetime.utcnow()
        self.update()
        
    def extend_ttl(self, additional_seconds: int):
        """Extend TTL"""
        self._ttl_seconds += additional_seconds
        self._expires_at = datetime.utcnow() + timedelta(seconds=self._ttl_seconds)
        self.update()

class SystemMetrics(Entity):
    """System metrics entity"""
    
    def __init__(
        self,
        cpu_usage_percent: float,
        memory_usage_mb: float,
        gpu_usage_percent: float = 0.0,
        gpu_memory_mb: float = 0.0,
        disk_usage_percent: float = 0.0,
        network_io_mbps: float = 0.0,
        id: str = None
    ):
        super().__init__(id)
        self._cpu_usage_percent = cpu_usage_percent
        self._memory_usage_mb = memory_usage_mb
        self._gpu_usage_percent = gpu_usage_percent
        self._gpu_memory_mb = gpu_memory_mb
        self._disk_usage_percent = disk_usage_percent
        self._network_io_mbps = network_io_mbps
        
    @property
    def cpu_usage_percent(self) -> float:
        return self._cpu_usage_percent
        
    @property
    def memory_usage_mb(self) -> float:
        return self._memory_usage_mb
        
    @property
    def gpu_usage_percent(self) -> float:
        return self._gpu_usage_percent
        
    @property
    def gpu_memory_mb(self) -> float:
        return self._gpu_memory_mb
        
    @property
    def disk_usage_percent(self) -> float:
        return self._disk_usage_percent
        
    @property
    def network_io_mbps(self) -> float:
        return self._network_io_mbps
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.created_at.isoformat(),
            "cpu_usage_percent": self._cpu_usage_percent,
            "memory_usage_mb": self._memory_usage_mb,
            "gpu_usage_percent": self._gpu_usage_percent,
            "gpu_memory_mb": self._gpu_memory_mb,
            "disk_usage_percent": self._disk_usage_percent,
            "network_io_mbps": self._network_io_mbps
        }

# Factory for creating entities
class EntityFactory:
    """Factory for creating entities"""
    
    @staticmethod
    def create_optimization_request(
        text_content: TextContent,
        optimization_type: OptimizationType,
        model_config: ModelConfig,
        security_config: SecurityConfig
    ) -> OptimizationRequest:
        """Create optimization request"""
        return OptimizationRequest(
            text_content=text_content,
            optimization_type=optimization_type,
            model_config=model_config,
            security_config=security_config
        )
        
    @staticmethod
    def create_ai_model(
        name: str,
        model_config: ModelConfig,
        version: str,
        performance_metrics: PerformanceMetrics
    ) -> AIModel:
        """Create AI model"""
        return AIModel(
            name=name,
            model_config=model_config,
            version=version,
            performance_metrics=performance_metrics
        )
        
    @staticmethod
    def create_cache_entry(
        key: str,
        value: Any,
        ttl_seconds: int = 3600
    ) -> CacheEntry:
        """Create cache entry"""
        return CacheEntry(
            key=key,
            value=value,
            ttl_seconds=ttl_seconds
        )
        
    @staticmethod
    def create_system_metrics(
        cpu_usage_percent: float,
        memory_usage_mb: float,
        gpu_usage_percent: float = 0.0,
        gpu_memory_mb: float = 0.0,
        disk_usage_percent: float = 0.0,
        network_io_mbps: float = 0.0
    ) -> SystemMetrics:
        """Create system metrics"""
        return SystemMetrics(
            cpu_usage_percent=cpu_usage_percent,
            memory_usage_mb=memory_usage_mb,
            gpu_usage_percent=gpu_usage_percent,
            gpu_memory_mb=gpu_memory_mb,
            disk_usage_percent=disk_usage_percent,
            network_io_mbps=network_io_mbps
        ) 