"""
Ultra Configuration - Centralized configuration with auto-tuning.
"""

import os
import multiprocessing as mp
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class UltraConfig:
    """Ultra-optimized configuration with intelligent auto-tuning."""
    
    # Application settings
    APP_NAME: str = "Onyx-Ultra"
    VERSION: str = "6.0.0"
    ENVIRONMENT: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "production"))
    DEBUG: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Server settings
    HOST: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    PORT: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    
    # Auto-tuned performance settings
    WORKERS: int = field(default_factory=lambda: UltraConfig._calculate_workers())
    MAX_CONNECTIONS: int = field(default_factory=lambda: min(10000, mp.cpu_count() * 1000))
    BACKLOG: int = 2048
    
    # Memory management
    MAX_MEMORY_MB: int = field(default_factory=lambda: UltraConfig._calculate_max_memory())
    GC_THRESHOLD: int = 1000  # Requests before forced GC
    
    # Performance tuning
    COMPRESSION_LEVEL: int = 1  # Fast compression
    HASH_LENGTH: int = 16
    CACHE_SIZE: int = field(default_factory=lambda: min(10000, UltraConfig._calculate_max_memory() // 10))
    
    # Feature flags
    ENABLE_UVLOOP: bool = True
    ENABLE_JIT: bool = True
    ENABLE_MONITORING: bool = True
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = field(default_factory=lambda: os.getenv("ENABLE_TRACING", "false").lower() == "true")
    
    # Timeouts
    TIMEOUT_KEEP_ALIVE: int = 65
    TIMEOUT_GRACEFUL_SHUTDOWN: int = 30
    REQUEST_TIMEOUT: int = 300
    
    # Database settings
    DATABASE_URL: Optional[str] = field(default_factory=lambda: os.getenv("DATABASE_URL"))
    REDIS_URL: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))
    
    # Security
    SECRET_KEY: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "ultra-secret-key-change-in-production"))
    CORS_ORIGINS: str = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*"))
    
    @staticmethod
    def _calculate_workers() -> int:
        """Calculate optimal number of workers based on system resources."""
        cpu_count = mp.cpu_count()
        
        if PSUTIL_AVAILABLE:
            # Consider available memory
            memory_gb = psutil.virtual_memory().total / (1024 ** 3)
            memory_workers = int(memory_gb / 0.5)  # 512MB per worker
            return min(64, max(1, min(cpu_count * 4, memory_workers)))
        
        return min(64, max(1, cpu_count * 2))
    
    @staticmethod
    def _calculate_max_memory() -> int:
        """Calculate maximum memory usage in MB."""
        if PSUTIL_AVAILABLE:
            total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
            return int(total_memory_mb * 0.8)  # Use 80% of available memory
        
        return 2048  # Default 2GB
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        base_config = {
            "development": {
                "DEBUG": True,
                "WORKERS": 1,
                "ENABLE_METRICS": False,
                "COMPRESSION_LEVEL": 0,
                "LOG_LEVEL": "DEBUG"
            },
            "testing": {
                "DEBUG": False,
                "WORKERS": 1,
                "ENABLE_METRICS": False,
                "CACHE_SIZE": 100,
                "LOG_LEVEL": "WARNING"
            },
            "staging": {
                "DEBUG": False,
                "WORKERS": max(1, mp.cpu_count()),
                "ENABLE_METRICS": True,
                "LOG_LEVEL": "INFO"
            },
            "production": {
                "DEBUG": False,
                "WORKERS": self.WORKERS,
                "ENABLE_METRICS": True,
                "ENABLE_MONITORING": True,
                "LOG_LEVEL": "INFO"
            }
        }
        
        return base_config.get(self.ENVIRONMENT, base_config["production"])
    
    def apply_environment_config(self):
        """Apply environment-specific configuration."""
        env_config = self.get_environment_config()
        
        for key, value in env_config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

# Global configuration instance
config = UltraConfig()
config.apply_environment_config() 