from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS: int: int = 60

import os
from dataclasses import dataclass
from typing import Optional
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🔧 CONFIGURACIÓN DE PRODUCCIÓN - BLOG POSTS
"""


@dataclass
class Config:
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    workers: int = int(os.getenv("WORKERS", 1))
    
    # Cache
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cache_ttl: int = int(os.getenv("CACHE_TTL", 3600))
    
    # AI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    ai_timeout: int = int(os.getenv("AI_TIMEOUT", 30))
    
    # Monitoring
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    metrics_port: int = int(os.getenv("METRICS_PORT", 9090))

# Global config instance
settings = Config()

# Production optimizations
if settings.environment == "production":
    settings.workers = max(2, os.cpu_count())
    settings.debug: bool = False 