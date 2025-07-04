"""
🚀 ULTRA-EXTREME V4 - REFACTOR FINAL
====================================

Ultra-extreme refactor V4 with:
- Clean Architecture ultra-limpia
- Domain-Driven Design ultra-inteligente
- CQRS Pattern ultra-optimizado
- Event Sourcing ultra-avanzado
- Dependency Injection ultra-pura
- SOLID Principles ultra-perfectos
- Advanced Patterns ultra-extremos
- Performance ultra-extrema
- Scalability ultra-ilimitada
- Monitoring ultra-avanzado
"""

__version__ = "4.0.0"
__author__ = "Ultra-Extreme Team"
__description__ = "Ultra-Extreme Refactor V4 - The Final Evolution"

# Core imports
from .core.config.settings import UltraExtremeSettings
from .core.exceptions.base import UltraExtremeException
from .core.interfaces.repositories import Repository
from .core.interfaces.services import Service
from .core.interfaces.cache import CacheService
from .core.interfaces.monitoring import PerformanceMonitor

# Domain imports
from .domain.entities.content import UltraContent
from .domain.entities.optimization import UltraOptimization
from .domain.entities.ai import UltraAI
from .domain.value_objects.content_metadata import ContentMetadata
from .domain.value_objects.optimization_metrics import OptimizationMetrics
from .domain.value_objects.ai_config import AIConfig
from .domain.events.base import DomainEvent
from .domain.events.content import ContentGeneratedEvent, ContentOptimizedEvent
from .domain.events.optimization import OptimizationCompletedEvent
from .domain.events.ai import AIGeneratedEvent

# Application imports
from .application.use_cases.content.generate_content import GenerateContentUseCase
from .application.use_cases.content.optimize_content import OptimizeContentUseCase
from .application.use_cases.content.analyze_content import AnalyzeContentUseCase
from .application.use_cases.optimization.optimize_system import OptimizeSystemUseCase
from .application.use_cases.optimization.optimize_performance import OptimizePerformanceUseCase
from .application.use_cases.optimization.optimize_cache import OptimizeCacheUseCase
from .application.use_cases.ai.generate_ai import GenerateAIUseCase
from .application.use_cases.ai.optimize_ai import OptimizeAIUseCase
from .application.use_cases.ai.analyze_ai import AnalyzeAIUseCase

# Infrastructure imports
from .infrastructure.database.repositories.content_repository import PostgreSQLContentRepository
from .infrastructure.database.repositories.optimization_repository import PostgreSQLOptimizationRepository
from .infrastructure.database.repositories.ai_repository import PostgreSQLAIRepository
from .infrastructure.cache.redis_cache import RedisCacheService
from .infrastructure.cache.memory_cache import MemoryCacheService
from .infrastructure.cache.disk_cache import DiskCacheService
from .infrastructure.cache.predictive_cache import PredictiveCacheService
from .infrastructure.external.openai_service import OpenAIService
from .infrastructure.external.anthropic_service import AnthropicService
from .infrastructure.external.huggingface_service import HuggingFaceService
from .infrastructure.monitoring.prometheus_monitor import PrometheusPerformanceMonitor
from .infrastructure.monitoring.sentry_monitor import SentryMonitor
from .infrastructure.monitoring.health_checker import HealthChecker
from .infrastructure.messaging.event_publisher import EventPublisher
from .infrastructure.messaging.event_subscriber import EventSubscriber
from .infrastructure.messaging.message_queue import MessageQueue
from .infrastructure.ai.openai_service import OpenAIUltraService
from .infrastructure.ai.anthropic_service import AnthropicUltraService
from .infrastructure.ai.huggingface_service import HuggingFaceUltraService
from .infrastructure.ai.local_ai_service import LocalAIUltraService

# Presentation imports
from .presentation.api.v1.content_routes import content_router
from .presentation.api.v1.optimization_routes import optimization_router
from .presentation.api.v1.ai_routes import ai_router
from .presentation.api.health_routes import health_router
from .presentation.middleware.auth_middleware import AuthMiddleware
from .presentation.middleware.rate_limit_middleware import RateLimitMiddleware
from .presentation.middleware.logging_middleware import LoggingMiddleware
from .presentation.middleware.monitoring_middleware import MonitoringMiddleware
from .presentation.serializers.content_serializer import ContentSerializer
from .presentation.serializers.optimization_serializer import OptimizationSerializer
from .presentation.serializers.ai_serializer import AISerializer
from .presentation.validators.content_validator import ContentValidator
from .presentation.validators.optimization_validator import OptimizationValidator
from .presentation.validators.ai_validator import AIValidator
from .presentation.websockets.content_websocket import ContentWebSocket
from .presentation.websockets.optimization_websocket import OptimizationWebSocket
from .presentation.websockets.ai_websocket import AIWebSocket

# Shared imports
from .shared.constants.app_constants import APP_NAME, APP_VERSION, APP_DESCRIPTION
from .shared.constants.error_codes import ErrorCodes
from .shared.constants.status_codes import StatusCodes
from .shared.types.content_types import ContentType, ContentStatus, ContentPriority
from .shared.types.optimization_types import OptimizationType, OptimizationStatus, OptimizationPriority
from .shared.types.ai_types import AIType, AIStatus, AIPriority
from .shared.helpers.content_helper import ContentHelper
from .shared.helpers.optimization_helper import OptimizationHelper
from .shared.helpers.ai_helper import AIHelper
from .shared.decorators.performance_decorator import performance_monitor
from .shared.decorators.cache_decorator import cache_result
from .shared.decorators.monitoring_decorator import monitor_function

# Main application
from .main import UltraExtremeApp

__all__ = [
    # Core
    "UltraExtremeSettings",
    "UltraExtremeException",
    "Repository",
    "Service",
    "CacheService",
    "PerformanceMonitor",
    
    # Domain
    "UltraContent",
    "UltraOptimization",
    "UltraAI",
    "ContentMetadata",
    "OptimizationMetrics",
    "AIConfig",
    "DomainEvent",
    "ContentGeneratedEvent",
    "ContentOptimizedEvent",
    "OptimizationCompletedEvent",
    "AIGeneratedEvent",
    
    # Application
    "GenerateContentUseCase",
    "OptimizeContentUseCase",
    "AnalyzeContentUseCase",
    "OptimizeSystemUseCase",
    "OptimizePerformanceUseCase",
    "OptimizeCacheUseCase",
    "GenerateAIUseCase",
    "OptimizeAIUseCase",
    "AnalyzeAIUseCase",
    
    # Infrastructure
    "PostgreSQLContentRepository",
    "PostgreSQLOptimizationRepository",
    "PostgreSQLAIRepository",
    "RedisCacheService",
    "MemoryCacheService",
    "DiskCacheService",
    "PredictiveCacheService",
    "OpenAIService",
    "AnthropicService",
    "HuggingFaceService",
    "PrometheusPerformanceMonitor",
    "SentryMonitor",
    "HealthChecker",
    "EventPublisher",
    "EventSubscriber",
    "MessageQueue",
    "OpenAIUltraService",
    "AnthropicUltraService",
    "HuggingFaceUltraService",
    "LocalAIUltraService",
    
    # Presentation
    "content_router",
    "optimization_router",
    "ai_router",
    "health_router",
    "AuthMiddleware",
    "RateLimitMiddleware",
    "LoggingMiddleware",
    "MonitoringMiddleware",
    "ContentSerializer",
    "OptimizationSerializer",
    "AISerializer",
    "ContentValidator",
    "OptimizationValidator",
    "AIValidator",
    "ContentWebSocket",
    "OptimizationWebSocket",
    "AIWebSocket",
    
    # Shared
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
    "ErrorCodes",
    "StatusCodes",
    "ContentType",
    "ContentStatus",
    "ContentPriority",
    "OptimizationType",
    "OptimizationStatus",
    "OptimizationPriority",
    "AIType",
    "AIStatus",
    "AIPriority",
    "ContentHelper",
    "OptimizationHelper",
    "AIHelper",
    "performance_monitor",
    "cache_result",
    "monitor_function",
    
    # Main
    "UltraExtremeApp",
] 