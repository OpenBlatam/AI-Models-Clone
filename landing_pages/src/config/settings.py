from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

from pydantic import BaseSettings, Field
from typing import Dict, List, Any, Optional
import os
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🚀 SYSTEM SETTINGS - REFACTORED CONFIGURATION
============================================

Configuraciones principales del sistema ultra-avanzado de landing pages.
Optimizado para performance empresarial y escalabilidad.
"""



class SystemSettings(BaseSettings):
    """
    Configuraciones principales del sistema ultra-avanzado.
    
    Características:
    - Configuración empresarial
    - Variables de entorno automáticas
    - Validación de configuración
    - Hot-reload en desarrollo
    """
    
    # Información del sistema
    SYSTEM_NAME: str = Field(default="Ultra Landing Page System", description="Nombre del sistema")
    VERSION: str = Field(default="3.0.0-REFACTORED", description="Versión del sistema")
    ENVIRONMENT: str = Field(default="production", description="Entorno de ejecución")
    DEBUG: bool = Field(default=False, description="Modo debug")
    
    # Configuración de la aplicación
    HOST: str = Field(default="0.0.0.0", description="Host de la aplicación")
    PORT: int = Field(default=8000, description="Puerto de la aplicación")
    WORKERS: int = Field(default=4, description="Número de workers")
    
    # Base de datos
    DATABASE_URL: str = Field(default="postgresql://user:pass@localhost:5432/landing_pages", description="URL de base de datos")
    DATABASE_POOL_SIZE: int = Field(default=20, description="Tamaño del pool de conexiones")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, description="Overflow máximo del pool")
    
    # Redis/Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="URL de Redis")
    CACHE_TTL_SECONDS: int = Field(default=300, description="TTL del cache en segundos")
    CACHE_MAX_SIZE: int = Field(default=1000, description="Tamaño máximo del cache")
    
    # IA y Machine Learning
    AI_MODEL_ENDPOINTS: Dict[str, str] = Field(
        default_factory=lambda: {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com/v1",
            "huggingface": "https://api-inference.huggingface.co/models"
        },
        description="Endpoints de modelos de IA"
    )
    
    AI_API_KEYS: Dict[str, str] = Field(
        default_factory=dict,
        description="API keys para servicios de IA"
    )
    
    AI_MODEL_CONFIGS: Dict[str, Any] = Field(
        default_factory=lambda: {
            "conversion_predictor": {
                "model": "xgboost",
                "version": "2.1",
                "accuracy_threshold": 94.0
            },
            "content_optimizer": {
                "model": "gpt-4-turbo",
                "max_tokens": 4000,
                "temperature": 0.7
            },
            "sentiment_analyzer": {
                "model": "bert-base-uncased",
                "confidence_threshold": 0.85
            }
        },
        description="Configuraciones de modelos de IA"
    )
    
    # Analytics y Monitoring
    ANALYTICS_ENABLED: bool = Field(default=True, description="Analytics habilitado")
    REAL_TIME_MONITORING: bool = Field(default=True, description="Monitoreo en tiempo real")
    METRICS_RETENTION_DAYS: int = Field(default=90, description="Días de retención de métricas")
    
    ANALYTICS_ENDPOINTS: Dict[str, str] = Field(
        default_factory=lambda: {
            "google_analytics": "https://www.google-analytics.com/mp/collect",
            "facebook_pixel": "https://www.facebook.com/tr",
            "mixpanel": "https://api.mixpanel.com/track"
        },
        description="Endpoints de analytics"
    )
    
    # Performance y Optimización
    MAX_CONCURRENT_REQUESTS: int = Field(default=1000, description="Máximo de requests concurrentes")
    REQUEST_TIMEOUT_SECONDS: int = Field(default=30, description="Timeout de requests")
    RESPONSE_CACHE_SECONDS: int = Field(default=60, description="Cache de respuestas")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=100, description="Límite de requests por minuto")
    RATE_LIMIT_BURST_SIZE: int = Field(default=20, description="Tamaño de burst para rate limiting")
    
    # Seguridad
    SECRET_KEY: str = Field(..., description="Clave secreta del sistema")
    JWT_ALGORITHM: str = Field(default="HS256", description="Algoritmo JWT")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="Expiración JWT en horas")
    
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Orígenes permitidos para CORS"
    )
    
    # Configuración de archivos
    UPLOAD_MAX_SIZE_MB: int = Field(default=10, description="Tamaño máximo de upload en MB")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default_factory=lambda: [".jpg", ".png", ".gif", ".webp", ".svg"],
        description="Tipos de archivo permitidos"
    )
    
    STATIC_FILES_PATH: str = Field(default="static", description="Ruta de archivos estáticos")
    MEDIA_FILES_PATH: str = Field(default="media", description="Ruta de archivos multimedia")
    
    # Integraciones externas
    EXTERNAL_APIS: Dict[str, Dict[str, str]] = Field(
        default_factory=lambda: {
            "stripe": {
                "public_key": "",
                "secret_key": "",
                "webhook_secret": ""
            },
            "sendgrid": {
                "api_key": "",
                "from_email": ""
            },
            "aws": {
                "access_key": "",
                "secret_key": "",
                "region": "us-east-1",
                "s3_bucket": ""
            }
        },
        description="Configuraciones de APIs externas"
    )
    
    # Configuración de logs
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Formato de logs"
    )
    LOG_FILE_PATH: str = Field(default="logs/system.log", description="Ruta del archivo de logs")
    LOG_MAX_SIZE_MB: int = Field(default=100, description="Tamaño máximo de log en MB")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Número de backups de logs")
    
    # Configuración de features
    FEATURES_ENABLED: Dict[str, bool] = Field(
        default_factory=lambda: {
            "ai_prediction": True,
            "real_time_analytics": True,
            "competitor_analysis": True,
            "dynamic_personalization": True,
            "ab_testing": True,
            "continuous_optimization": True,
            "advanced_nlp": True,
            "performance_monitoring": True
        },
        description="Features habilitadas del sistema"
    )
    
    # Configuración de notificaciones
    NOTIFICATIONS_ENABLED: bool = Field(default=True, description="Notificaciones habilitadas")
    EMAIL_NOTIFICATIONS: bool = Field(default=True, description="Notificaciones por email")
    SLACK_NOTIFICATIONS: bool = Field(default=False, description="Notificaciones por Slack")
    
    NOTIFICATION_SETTINGS: Dict[str, Any] = Field(
        default_factory=lambda: {
            "performance_alerts": {
                "enabled": True,
                "threshold_conversion_drop": 10.0,
                "threshold_response_time": 2000
            },
            "system_alerts": {
                "enabled": True,
                "threshold_error_rate": 1.0,
                "threshold_uptime": 99.5
            }
        },
        description="Configuraciones de notificaciones"
    )
    
    # Configuración de backup y recuperación
    BACKUP_ENABLED: bool = Field(default=True, description="Backups habilitados")
    BACKUP_FREQUENCY_HOURS: int = Field(default=6, description="Frecuencia de backup en horas")
    BACKUP_RETENTION_DAYS: int = Field(default=30, description="Días de retención de backups")
    BACKUP_STORAGE_TYPE: str = Field(default="s3", description="Tipo de almacenamiento para backups")
    
    # Configuración de testing
    TESTING_MODE: bool = Field(default=False, description="Modo de testing")
    MOCK_EXTERNAL_APIS: bool = Field(default=False, description="Mockear APIs externas")
    TEST_DATA_ENABLED: bool = Field(default=False, description="Datos de prueba habilitados")
    
    class Config:
        """Configuración de Pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        # Variables de entorno con prefijo
        env_prefix = "ULTRA_LP_"
        
        # Ejemplos de configuración
        schema_extra = {
            "example": {
                "SYSTEM_NAME": "Ultra Landing Page System",
                "VERSION": "3.0.0-REFACTORED",
                "ENVIRONMENT": "production",
                "DEBUG": False,
                "HOST": "0.0.0.0",
                "PORT": 8000,
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/landing_pages",
                "REDIS_URL": "redis://localhost:6379/0",
                "SECRET_KEY": "your-secret-key-here",
                "FEATURES_ENABLED": {
                    "ai_prediction": True,
                    "real_time_analytics": True,
                    "competitor_analysis": True
                }
            }
        }
    
    def is_production(self) -> bool:
        """Verifica si está en modo producción."""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Verifica si está en modo desarrollo."""
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    def get_ai_model_config(self, model_name: str) -> Dict[str, Any]:
        """Obtiene configuración de un modelo de IA específico."""
        return self.AI_MODEL_CONFIGS.get(model_name, {})
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Verifica si una feature está habilitada."""
        return self.FEATURES_ENABLED.get(feature_name, False)
    
    async def get_external_api_config(self, api_name: str) -> Dict[str, str]:
        """Obtiene configuración de una API externa."""
        return self.EXTERNAL_APIS.get(api_name, {})


# Instancia global de configuración
settings = SystemSettings()


# Factory functions para configuraciones específicas
def get_database_config() -> Dict[str, Any]:
    """Obtiene configuración de base de datos."""
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW
    }


def get_cache_config() -> Dict[str, Any]:
    """Obtiene configuración de cache."""
    return {
        "url": settings.REDIS_URL,
        "ttl": settings.CACHE_TTL_SECONDS,
        "max_size": settings.CACHE_MAX_SIZE
    }


def get_ai_config() -> Dict[str, Any]:
    """Obtiene configuración de IA."""
    return {
        "endpoints": settings.AI_MODEL_ENDPOINTS,
        "api_keys": settings.AI_API_KEYS,
        "models": settings.AI_MODEL_CONFIGS
    }


def get_performance_config() -> Dict[str, Any]:
    """Obtiene configuración de performance."""
    return {
        "max_concurrent_requests": settings.MAX_CONCURRENT_REQUESTS,
        "request_timeout": settings.REQUEST_TIMEOUT_SECONDS,
        "response_cache": settings.RESPONSE_CACHE_SECONDS,
        "rate_limit": settings.RATE_LIMIT_REQUESTS_PER_MINUTE
    } 