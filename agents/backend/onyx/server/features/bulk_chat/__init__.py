"""
Bulk Chat - Sistema de Chat Continuo Proactivo
===============================================

Sistema de chat tipo ChatGPT que funciona de forma continua y proactiva,
generando respuestas automáticamente hasta que el usuario lo pause.

Características principales:
- Chat continuo y proactivo
- Control de pausa/continuación
- Streaming de respuestas
- Múltiples modelos de IA
- Gestión de sesiones
- Plugins y extensiones
- Métricas y monitoreo
- Cache inteligente
- Rate limiting
- Webhooks
- Exportación de conversaciones
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

# Core components
from .core.chat_engine import ContinuousChatEngine
from .core.chat_session import ChatSession, ChatState, ChatMessage
from .core.session_storage import SessionStorage, JSONSessionStorage
from .core.metrics import MetricsCollector
from .core.response_cache import ResponseCache
from .core.plugins import PluginManager, PluginType, PluginContext
from .core.webhooks import WebhookManager, WebhookEvent
from .core.rate_limiter import RateLimiter, RateLimitConfig
from .core.conversation_analyzer import ConversationAnalyzer
from .core.exporters import ConversationExporter
from .core.templates import TemplateManager
from .core.auth import AuthManager, Role
from .core.health_monitor import HealthMonitor
from .core.task_queue import TaskQueue

# API
from .api.chat_api import create_chat_app

# Utilities
from typing import Optional, Callable, Dict, Any
import logging

__all__ = [
    # Core
    "ContinuousChatEngine",
    "ChatSession",
    "ChatState",
    "ChatMessage",
    # Storage
    "SessionStorage",
    "JSONSessionStorage",
    # Metrics & Monitoring
    "MetricsCollector",
    "HealthMonitor",
    # Cache
    "ResponseCache",
    # Plugins
    "PluginManager",
    "PluginType",
    "PluginContext",
    # Webhooks
    "WebhookManager",
    "WebhookEvent",
    # Rate Limiting
    "RateLimiter",
    "RateLimitConfig",
    # Analysis
    "ConversationAnalyzer",
    # Export
    "ConversationExporter",
    # Templates
    "TemplateManager",
    # Auth
    "AuthManager",
    "Role",
    # Tasks
    "TaskQueue",
    # API
    "create_chat_app",
    # Utilities
    "create_engine",
    "create_session",
    "setup_logging",
]


def create_engine(
    llm_provider: Optional[Callable] = None,
    auto_continue: bool = True,
    response_interval: float = 2.0,
    max_consecutive_responses: int = 100,
    storage_path: Optional[str] = None,
    enable_metrics: bool = True,
    enable_cache: bool = True,
    cache_size: int = 1000,
    cache_ttl: int = 3600,
    **kwargs
) -> ContinuousChatEngine:
    """
    Crear una instancia del motor de chat con configuración por defecto.
    
    Args:
        llm_provider: Función que provee el LLM (opcional)
        auto_continue: Si True, continúa automáticamente después de responder
        response_interval: Intervalo entre respuestas en segundos
        max_consecutive_responses: Máximo de respuestas consecutivas
        storage_path: Ruta para almacenar sesiones (opcional)
        enable_metrics: Habilitar recolección de métricas
        enable_cache: Habilitar cache de respuestas
        cache_size: Tamaño máximo del cache
        cache_ttl: TTL del cache en segundos
        **kwargs: Argumentos adicionales para ContinuousChatEngine
        
    Returns:
        Instancia configurada de ContinuousChatEngine
        
    Example:
        >>> engine = create_engine(
        ...     auto_continue=True,
        ...     response_interval=2.0
        ... )
        >>> session = engine.create_session()
        >>> await engine.start_chat(session.session_id)
    """
    storage = None
    if storage_path:
        storage = JSONSessionStorage(storage_path)
    
    return ContinuousChatEngine(
        llm_provider=llm_provider,
        auto_continue=auto_continue,
        response_interval=response_interval,
        max_consecutive_responses=max_consecutive_responses,
        storage=storage,
        enable_metrics=enable_metrics,
        enable_cache=enable_cache,
        cache_size=cache_size,
        cache_ttl=cache_ttl,
        **kwargs
    )


def create_session(
    user_id: Optional[str] = None,
    auto_continue: bool = True,
    **kwargs
) -> ChatSession:
    """
    Crear una nueva sesión de chat.
    
    Args:
        user_id: ID del usuario (opcional)
        auto_continue: Si True, continúa automáticamente
        **kwargs: Argumentos adicionales para ChatSession
        
    Returns:
        Nueva instancia de ChatSession
        
    Example:
        >>> session = create_session(user_id="user123")
        >>> print(session.session_id)
    """
    return ChatSession(
        user_id=user_id,
        auto_continue=auto_continue,
        **kwargs
    )


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configurar logging para el módulo bulk_chat.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Formato personalizado (opcional)
        log_file: Archivo para logs (opcional)
        
    Returns:
        Logger configurado
        
    Example:
        >>> logger = setup_logging(level="DEBUG", log_file="chat.log")
        >>> logger.info("Chat system initialized")
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(log_file)] if log_file else [])
        ]
    )
    
    return logging.getLogger("bulk_chat")















===============================================

Sistema de chat tipo ChatGPT que funciona de forma continua y proactiva,
generando respuestas automáticamente hasta que el usuario lo pause.

Características principales:
- Chat continuo y proactivo
- Control de pausa/reanudación
- Streaming en tiempo real
- Múltiples sesiones simultáneas
- Integración con múltiples LLMs
- API REST completa
- Persistencia de sesiones
- Sistema de métricas y monitoreo
- Rate limiting y seguridad
- Sistema de plugins extensible
"""

__version__ = "1.0.0"
__author__ = "Blatam Academy"

# Core components
from .core.chat_engine import ContinuousChatEngine
from .core.chat_session import ChatSession, ChatState, ChatMessage
from .core.session_storage import SessionStorage, JSONSessionStorage

# API
from .api.chat_api import create_chat_app

# Configuration
from .config.chat_config import ChatConfig

# Utilities and helpers
from .core.metrics import MetricsCollector
from .core.response_cache import ResponseCache
from .core.rate_limiter import RateLimiter, RateLimitConfig
from .core.plugins import PluginManager, PluginType, PluginContext
from .core.webhooks import WebhookManager, WebhookEvent

# Advanced features (optional imports)
try:
    from .core.conversation_analyzer import ConversationAnalyzer
    CONVERSATION_ANALYZER_AVAILABLE = True
except ImportError:
    CONVERSATION_ANALYZER_AVAILABLE = False

try:
    from .core.sentiment_analyzer import SentimentAnalyzer, Sentiment, Emotion
    SENTIMENT_ANALYZER_AVAILABLE = True
except ImportError:
    SENTIMENT_ANALYZER_AVAILABLE = False

try:
    from .core.intelligent_cache import IntelligentCache, CacheStrategy
    INTELLIGENT_CACHE_AVAILABLE = True
except ImportError:
    INTELLIGENT_CACHE_AVAILABLE = False

try:
    from .core.health_monitor import HealthMonitor
    HEALTH_MONITOR_AVAILABLE = True
except ImportError:
    HEALTH_MONITOR_AVAILABLE = False

# Helper functions
def create_default_engine(
    llm_provider=None,
    config: Optional[ChatConfig] = None,
    **kwargs
) -> ContinuousChatEngine:
    """
    Crear un motor de chat con configuración por defecto.
    
    Args:
        llm_provider: Función que genera respuestas (opcional)
        config: Configuración personalizada (opcional)
        **kwargs: Argumentos adicionales para ContinuousChatEngine
        
    Returns:
        ContinuousChatEngine configurado
    """
    if config is None:
        config = ChatConfig()
    
    return ContinuousChatEngine(
        llm_provider=llm_provider,
        auto_continue=config.auto_continue,
        response_interval=config.response_interval,
        max_consecutive_responses=config.max_consecutive_responses,
        enable_metrics=config.enable_metrics,
        **kwargs
    )


def create_default_app(
    config: Optional[ChatConfig] = None,
    **kwargs
):
    """
    Crear una aplicación FastAPI con configuración por defecto.
    
    Args:
        config: Configuración personalizada (opcional)
        **kwargs: Argumentos adicionales para create_chat_app
        
    Returns:
        FastAPI app configurada
    """
    if config is None:
        config = ChatConfig()
    
    return create_chat_app(
        host=config.api_host,
        port=config.api_port,
        cors_origins=config.cors_origins,
        **kwargs
    )


# Main exports
__all__ = [
    # Core
    "ContinuousChatEngine",
    "ChatSession",
    "ChatState",
    "ChatMessage",
    
    # API
    "create_chat_app",
    
    # Configuration
    "ChatConfig",
    
    # Utilities
    "MetricsCollector",
    "ResponseCache",
    "RateLimiter",
    "RateLimitConfig",
    "PluginManager",
    "PluginType",
    "PluginContext",
    "WebhookManager",
    "WebhookEvent",
    "SessionStorage",
    "JSONSessionStorage",
    
    # Helpers
    "create_default_engine",
    "create_default_app",
    
    # Version info
    "__version__",
    "__author__",
]

# Conditional exports
if CONVERSATION_ANALYZER_AVAILABLE:
    __all__.extend(["ConversationAnalyzer"])

if SENTIMENT_ANALYZER_AVAILABLE:
    __all__.extend(["SentimentAnalyzer", "Sentiment", "Emotion"])

if INTELLIGENT_CACHE_AVAILABLE:
    __all__.extend(["IntelligentCache", "CacheStrategy"])

if HEALTH_MONITOR_AVAILABLE:
    __all__.extend(["HealthMonitor"])














