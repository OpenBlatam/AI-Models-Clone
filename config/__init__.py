"""
ONYX BLOG POST - Configuration Module
====================================

Configuración centralizada para el sistema de blog posts.
Incluye configuración de modelos, prompts, optimización y integración con Onyx.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

from ..models import BlogPostType, BlogPostTone, BlogPostLength, OpenRouterModel

logger = logging.getLogger(__name__)

@dataclass
class OpenRouterConfig:
    """Configuración para OpenRouter"""
    api_key: str = ""
    app_name: str = "onyx-blog-post"
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-4-turbo"
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Rate limiting
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000
    
    # Cost tracking
    enable_cost_tracking: bool = True
    max_cost_per_request: float = 1.0  # USD
    daily_cost_limit: float = 50.0     # USD
    
    def __post_init__(self):
        """Validar configuración"""
        if not self.api_key:
            # Intentar obtener de variables de entorno
            self.api_key = os.getenv("OPENROUTER_API_KEY", "")
            
        if not self.api_key:
            logger.warning("OpenRouter API key not configured")

@dataclass
class OnyxIntegrationConfig:
    """Configuración para integración con Onyx"""
    enable_onyx_integration: bool = True
    onyx_base_url: str = "http://localhost:8080"
    onyx_api_key: str = ""
    
    # Database settings
    use_onyx_database: bool = True
    store_blog_posts: bool = True
    store_metrics: bool = True
    
    # Document set integration
    auto_create_document_sets: bool = True
    default_document_set_name: str = "blog-posts"
    
    # User management
    require_user_authentication: bool = True
    enable_user_quotas: bool = True
    default_user_quota: int = 10  # posts per day
    
    # Persona integration
    use_persona_context: bool = True
    default_persona_id: Optional[str] = None
    
    def __post_init__(self):
        """Validar configuración de Onyx"""
        if not self.onyx_api_key:
            self.onyx_api_key = os.getenv("ONYX_API_KEY", "")

@dataclass
class BlogPostDefaults:
    """Configuración por defecto para blog posts"""
    blog_type: BlogPostType = BlogPostType.TECHNICAL
    tone: BlogPostTone = BlogPostTone.PROFESSIONAL
    length: BlogPostLength = BlogPostLength.MEDIUM
    language: str = "es"
    target_audience: str = "general"
    include_seo: bool = True
    include_images: bool = False
    
    # Quality settings
    min_quality_score: float = 7.0
    require_manual_review: bool = False
    auto_publish: bool = False
    
    # SEO defaults
    max_meta_title_length: int = 60
    max_meta_description_length: int = 160
    min_keywords: int = 3
    max_keywords: int = 10

@dataclass
class ModelConfiguration:
    """Configuración específica por modelo"""
    model: OpenRouterModel
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Configuración específica del modelo
    best_for: List[str] = field(default_factory=list)
    cost_per_1k_tokens: float = 0.0
    max_context_length: int = 4096
    supports_streaming: bool = True
    
    # Configuración de prompts
    system_prompt_template: Optional[str] = None
    user_prompt_template: Optional[str] = None

@dataclass
class CacheConfig:
    """Configuración de cache"""
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hora
    max_cache_size: int = 1000
    
    # Cache levels
    enable_memory_cache: bool = True
    enable_redis_cache: bool = False
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    
    # Cache keys
    cache_key_prefix: str = "onyx_blog_post"
    enable_cache_compression: bool = True

@dataclass
class PerformanceConfig:
    """Configuración de rendimiento"""
    max_concurrent_requests: int = 10
    request_timeout: int = 120
    enable_metrics: bool = True
    
    # Benchmarking
    enable_benchmarking: bool = True
    benchmark_interval: int = 100  # cada 100 requests
    
    # Monitoring
    enable_health_checks: bool = True
    health_check_interval: int = 60  # segundos
    
    # Optimization
    enable_batch_processing: bool = True
    max_batch_size: int = 5

@dataclass
class SecurityConfig:
    """Configuración de seguridad"""
    enable_content_filtering: bool = True
    max_content_length: int = 50000
    blocked_keywords: List[str] = field(default_factory=list)
    
    # Rate limiting per user
    user_rate_limit: int = 100  # requests per hour
    enable_ip_blocking: bool = False
    
    # Input validation
    strict_input_validation: bool = True
    sanitize_inputs: bool = True
    
    # API security
    require_api_key: bool = False
    api_key_header: str = "X-API-Key"

class BlogPostConfiguration:
    """Configuración principal del sistema de blog posts"""
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        environment: str = "development"
    ):
        self.environment = environment
        self.config_file = config_file
        
        # Configuraciones base
        self.openrouter = OpenRouterConfig()
        self.onyx_integration = OnyxIntegrationConfig()
        self.blog_defaults = BlogPostDefaults()
        self.cache = CacheConfig()
        self.performance = PerformanceConfig()
        self.security = SecurityConfig()
        
        # Configuraciones de modelos
        self.model_configs = self._init_model_configs()
        
        # Configuraciones por entorno
        self._apply_environment_config()
        
        # Cargar archivo de configuración si existe
        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)
        
        logger.info(f"BlogPostConfiguration initialized (env: {environment})")
    
    def _init_model_configs(self) -> Dict[str, ModelConfiguration]:
        """Inicializar configuraciones de modelos"""
        return {
            "gpt-4-turbo": ModelConfiguration(
                model=OpenRouterModel.GPT_4_TURBO,
                temperature=0.7,
                max_tokens=4096,
                best_for=["technical", "detailed", "analysis"],
                cost_per_1k_tokens=0.02,
                max_context_length=128000
            ),
            "gpt-4o": ModelConfiguration(
                model=OpenRouterModel.GPT_4O,
                temperature=0.7,
                max_tokens=4096,
                best_for=["general", "creative", "balanced"],
                cost_per_1k_tokens=0.01,
                max_context_length=128000
            ),
            "claude-3-sonnet": ModelConfiguration(
                model=OpenRouterModel.CLAUDE_3_SONNET,
                temperature=0.7,
                max_tokens=4096,
                best_for=["analysis", "reasoning", "academic"],
                cost_per_1k_tokens=0.009,
                max_context_length=200000
            ),
            "claude-3-haiku": ModelConfiguration(
                model=OpenRouterModel.CLAUDE_3_HAIKU,
                temperature=0.7,
                max_tokens=4096,
                best_for=["quick", "simple", "cost_effective"],
                cost_per_1k_tokens=0.00125,
                max_context_length=200000
            ),
            "gemini-pro": ModelConfiguration(
                model=OpenRouterModel.GEMINI_PRO,
                temperature=0.7,
                max_tokens=2048,
                best_for=["factual", "research", "multilingual"],
                cost_per_1k_tokens=0.001,
                max_context_length=30720
            ),
            "mistral-large": ModelConfiguration(
                model=OpenRouterModel.MISTRAL_LARGE,
                temperature=0.7,
                max_tokens=4096,
                best_for=["multilingual", "coding", "european"],
                cost_per_1k_tokens=0.016,
                max_context_length=32000
            ),
            "llama-3-70b": ModelConfiguration(
                model=OpenRouterModel.LLAMA_3_70B,
                temperature=0.7,
                max_tokens=4096,
                best_for=["open_source", "general", "cost_effective"],
                cost_per_1k_tokens=0.0009,
                max_context_length=8192
            ),
            "command-r": ModelConfiguration(
                model=OpenRouterModel.COHERE_COMMAND_R,
                temperature=0.7,
                max_tokens=4096,
                best_for=["business", "professional", "search"],
                cost_per_1k_tokens=0.001,
                max_context_length=128000
            )
        }
    
    def _apply_environment_config(self):
        """Aplicar configuración específica del entorno"""
        if self.environment == "production":
            # Configuración de producción
            self.performance.max_concurrent_requests = 20
            self.cache.cache_ttl = 7200  # 2 horas
            self.security.enable_content_filtering = True
            self.openrouter.max_retries = 5
            self.onyx_integration.require_user_authentication = True
            
        elif self.environment == "staging":
            # Configuración de staging
            self.performance.max_concurrent_requests = 10
            self.cache.cache_ttl = 1800  # 30 minutos
            self.security.enable_content_filtering = True
            self.openrouter.max_retries = 3
            
        else:  # development
            # Configuración de desarrollo
            self.performance.max_concurrent_requests = 5
            self.cache.cache_ttl = 300  # 5 minutos
            self.security.enable_content_filtering = False
            self.openrouter.max_retries = 2
            self.onyx_integration.require_user_authentication = False
    
    def _load_config_file(self, config_file: str):
        """Cargar configuración desde archivo"""
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Aplicar configuraciones del archivo
            self._update_from_dict(config_data)
            logger.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """Actualizar configuración desde diccionario"""
        for section, values in config_dict.items():
            if hasattr(self, section) and isinstance(values, dict):
                config_obj = getattr(self, section)
                for key, value in values.items():
                    if hasattr(config_obj, key):
                        setattr(config_obj, key, value)
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfiguration]:
        """Obtener configuración de un modelo"""
        return self.model_configs.get(model_name)
    
    def get_best_model_for_type(self, blog_type: BlogPostType) -> ModelConfiguration:
        """Obtener el mejor modelo para un tipo de blog"""
        type_str = blog_type.value
        
        for config in self.model_configs.values():
            if type_str in config.best_for:
                return config
        
        # Fallback al modelo por defecto
        return self.model_configs["gpt-4-turbo"]
    
    def validate_config(self) -> List[str]:
        """Validar configuración y retornar errores"""
        errors = []
        
        # Validar OpenRouter
        if not self.openrouter.api_key:
            errors.append("OpenRouter API key is required")
        
        # Validar limits
        if self.performance.max_concurrent_requests <= 0:
            errors.append("max_concurrent_requests must be > 0")
        
        if self.cache.cache_ttl <= 0:
            errors.append("cache_ttl must be > 0")
        
        # Validar costos
        if self.openrouter.max_cost_per_request <= 0:
            errors.append("max_cost_per_request must be > 0")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return {
            "environment": self.environment,
            "openrouter": {
                "app_name": self.openrouter.app_name,
                "base_url": self.openrouter.base_url,
                "default_model": self.openrouter.default_model,
                "timeout": self.openrouter.timeout,
                "max_retries": self.openrouter.max_retries,
                "requests_per_minute": self.openrouter.requests_per_minute,
                "tokens_per_minute": self.openrouter.tokens_per_minute
            },
            "onyx_integration": {
                "enable_onyx_integration": self.onyx_integration.enable_onyx_integration,
                "use_onyx_database": self.onyx_integration.use_onyx_database,
                "store_blog_posts": self.onyx_integration.store_blog_posts,
                "require_user_authentication": self.onyx_integration.require_user_authentication
            },
            "blog_defaults": {
                "blog_type": self.blog_defaults.blog_type.value,
                "tone": self.blog_defaults.tone.value,
                "length": self.blog_defaults.length.display_name,
                "language": self.blog_defaults.language,
                "include_seo": self.blog_defaults.include_seo
            },
            "performance": {
                "max_concurrent_requests": self.performance.max_concurrent_requests,
                "request_timeout": self.performance.request_timeout,
                "enable_benchmarking": self.performance.enable_benchmarking
            },
            "cache": {
                "enable_cache": self.cache.enable_cache,
                "cache_ttl": self.cache.cache_ttl,
                "max_cache_size": self.cache.max_cache_size
            }
        }
    
    def save_config(self, file_path: str):
        """Guardar configuración a archivo"""
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving config to {file_path}: {e}")

# Configuración global singleton
_global_config: Optional[BlogPostConfiguration] = None

def get_config() -> BlogPostConfiguration:
    """Obtener configuración global"""
    global _global_config
    if _global_config is None:
        _global_config = BlogPostConfiguration()
    return _global_config

def set_config(config: BlogPostConfiguration):
    """Establecer configuración global"""
    global _global_config
    _global_config = config

def load_config_from_file(file_path: str, environment: str = "development") -> BlogPostConfiguration:
    """Cargar configuración desde archivo"""
    config = BlogPostConfiguration(config_file=file_path, environment=environment)
    set_config(config)
    return config

def create_default_config() -> BlogPostConfiguration:
    """Crear configuración por defecto"""
    return BlogPostConfiguration()

# Configuraciones predefinidas
DEVELOPMENT_CONFIG = {
    "openrouter": {
        "max_retries": 2,
        "requests_per_minute": 30,
        "tokens_per_minute": 50000
    },
    "performance": {
        "max_concurrent_requests": 3,
        "enable_benchmarking": False
    },
    "cache": {
        "cache_ttl": 300,
        "max_cache_size": 100
    },
    "security": {
        "enable_content_filtering": False,
        "strict_input_validation": False
    }
}

PRODUCTION_CONFIG = {
    "openrouter": {
        "max_retries": 5,
        "requests_per_minute": 100,
        "tokens_per_minute": 200000
    },
    "performance": {
        "max_concurrent_requests": 20,
        "enable_benchmarking": True
    },
    "cache": {
        "cache_ttl": 7200,
        "max_cache_size": 5000
    },
    "security": {
        "enable_content_filtering": True,
        "strict_input_validation": True
    }
}

__all__ = [
    'OpenRouterConfig',
    'OnyxIntegrationConfig',
    'BlogPostDefaults',
    'ModelConfiguration',
    'CacheConfig',
    'PerformanceConfig',
    'SecurityConfig',
    'BlogPostConfiguration',
    'get_config',
    'set_config',
    'load_config_from_file',
    'create_default_config',
    'DEVELOPMENT_CONFIG',
    'PRODUCTION_CONFIG',
] 