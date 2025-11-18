"""
Configuration Settings - Configuración del sistema
Maneja todas las configuraciones del modelo de búsqueda IA
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from pathlib import Path

class Settings(BaseSettings):
    """
    Configuración principal del sistema de búsqueda IA
    """
    
    # Configuración de la API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    # Configuración de la base de datos
    database_path: str = Field(default="vector_database.db", env="DATABASE_PATH")
    embeddings_path: str = Field(default="embeddings.pkl", env="EMBEDDINGS_PATH")
    backup_path: str = Field(default="backups", env="BACKUP_PATH")
    
    # Configuración del modelo de IA
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", 
        env="EMBEDDING_MODEL"
    )
    max_query_length: int = Field(default=512, env="MAX_QUERY_LENGTH")
    max_content_length: int = Field(default=100000, env="MAX_CONTENT_LENGTH")
    snippet_length: int = Field(default=200, env="SNIPPET_LENGTH")
    
    # Configuración de búsqueda
    default_search_limit: int = Field(default=10, env="DEFAULT_SEARCH_LIMIT")
    max_search_limit: int = Field(default=100, env="MAX_SEARCH_LIMIT")
    similarity_threshold: float = Field(default=0.1, env="SIMILARITY_THRESHOLD")
    
    # Configuración de TF-IDF
    tfidf_max_features: int = Field(default=10000, env="TFIDF_MAX_FEATURES")
    tfidf_ngram_range: tuple = Field(default=(1, 2), env="TFIDF_NGRAM_RANGE")
    
    # Configuración de búsqueda híbrida
    semantic_weight: float = Field(default=0.7, env="SEMANTIC_WEIGHT")
    keyword_weight: float = Field(default=0.3, env="KEYWORD_WEIGHT")
    
    # Configuración de logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Configuración de CORS
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # Configuración de cache
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hora
    
    # Configuración de seguridad
    api_key_required: bool = Field(default=False, env="API_KEY_REQUIRED")
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # segundos
    
    # Configuración de procesamiento de documentos
    supported_document_types: list = Field(
        default=["text", "markdown", "html", "json", "pdf"], 
        env="SUPPORTED_DOCUMENT_TYPES"
    )
    batch_size: int = Field(default=100, env="BATCH_SIZE")
    
    # Configuración de monitoreo
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._create_directories()
    
    def _create_directories(self):
        """Crear directorios necesarios"""
        directories = [
            os.path.dirname(self.database_path),
            os.path.dirname(self.embeddings_path),
            self.backup_path
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
    
    def get_database_config(self) -> Dict[str, Any]:
        """Obtener configuración de base de datos"""
        return {
            "database_path": self.database_path,
            "embeddings_path": self.embeddings_path,
            "backup_path": self.backup_path
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Obtener configuración del modelo"""
        return {
            "embedding_model": self.embedding_model,
            "max_query_length": self.max_query_length,
            "max_content_length": self.max_content_length,
            "snippet_length": self.snippet_length
        }
    
    def get_search_config(self) -> Dict[str, Any]:
        """Obtener configuración de búsqueda"""
        return {
            "default_search_limit": self.default_search_limit,
            "max_search_limit": self.max_search_limit,
            "similarity_threshold": self.similarity_threshold,
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Obtener configuración de la API"""
        return {
            "host": self.api_host,
            "port": self.api_port,
            "reload": self.api_reload,
            "workers": self.api_workers,
            "cors_origins": self.cors_origins,
            "cors_allow_credentials": self.cors_allow_credentials
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Obtener configuración de seguridad"""
        return {
            "api_key_required": self.api_key_required,
            "api_key": self.api_key,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window": self.rate_limit_window
        }
    
    def validate_config(self) -> bool:
        """Validar configuración"""
        try:
            # Validar puertos
            if not (1 <= self.api_port <= 65535):
                raise ValueError(f"Puerto API inválido: {self.api_port}")
            
            if not (1 <= self.metrics_port <= 65535):
                raise ValueError(f"Puerto de métricas inválido: {self.metrics_port}")
            
            # Validar límites
            if self.max_search_limit < self.default_search_limit:
                raise ValueError("max_search_limit debe ser mayor que default_search_limit")
            
            if not (0 <= self.similarity_threshold <= 1):
                raise ValueError("similarity_threshold debe estar entre 0 y 1")
            
            if not (0 <= self.semantic_weight <= 1):
                raise ValueError("semantic_weight debe estar entre 0 y 1")
            
            if not (0 <= self.keyword_weight <= 1):
                raise ValueError("keyword_weight debe estar entre 0 y 1")
            
            if abs(self.semantic_weight + self.keyword_weight - 1.0) > 0.01:
                raise ValueError("semantic_weight + keyword_weight debe ser aproximadamente 1.0")
            
            # Validar tipos de documentos
            valid_types = ["text", "markdown", "html", "json", "pdf"]
            for doc_type in self.supported_document_types:
                if doc_type not in valid_types:
                    raise ValueError(f"Tipo de documento no válido: {doc_type}")
            
            return True
            
        except Exception as e:
            print(f"Error en validación de configuración: {e}")
            return False

# Instancia global de configuración
settings = Settings()

# Configuraciones específicas por entorno
class DevelopmentSettings(Settings):
    """Configuración para desarrollo"""
    api_reload: bool = True
    log_level: str = "DEBUG"
    enable_metrics: bool = True

class ProductionSettings(Settings):
    """Configuración para producción"""
    api_reload: bool = False
    log_level: str = "INFO"
    enable_metrics: bool = True
    api_key_required: bool = True
    cors_origins: list = ["https://yourdomain.com"]  # Cambiar por dominio real

class TestingSettings(Settings):
    """Configuración para testing"""
    database_path: str = "test_vector_database.db"
    embeddings_path: str = "test_embeddings.pkl"
    log_level: str = "WARNING"
    enable_metrics: bool = False

def get_settings(environment: str = "development") -> Settings:
    """Obtener configuración según el entorno"""
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()



























