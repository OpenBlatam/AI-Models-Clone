"""
Quantum Configuration - Ultra-optimized configuration management.
"""

import os
import multiprocessing as mp
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

@dataclass
class QuantumConfig:
    """Quantum-level configuration with AI-powered auto-tuning."""
    
    # Application settings
    APP_NAME: str = "Onyx-Quantum-Refactored"
    VERSION: str = "8.0.0-quantum"
    ENVIRONMENT: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "quantum"))
    DEBUG: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Server quantum settings
    HOST: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    PORT: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    METRICS_PORT: int = field(default_factory=lambda: int(os.getenv("METRICS_PORT", "9090")))
    
    # Quantum performance auto-tuning
    WORKERS: int = field(default_factory=lambda: QuantumConfig._quantum_tune_workers())
    MAX_CONNECTIONS: int = field(default_factory=lambda: min(100000, mp.cpu_count() * 5000))
    BACKLOG: int = 8192
    
    # Quantum memory management
    MAX_MEMORY_MB: int = field(default_factory=lambda: QuantumConfig._quantum_tune_memory())
    GC_THRESHOLD: int = 100
    CACHE_SIZE: int = field(default_factory=lambda: min(100000, QuantumConfig._quantum_tune_memory() // 5))
    
    # Quantum performance settings
    COMPRESSION_LEVEL: int = 1
    HASH_LENGTH: int = 32
    BATCH_SIZE: int = 10000
    
    # Security
    SECRET_KEY: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "quantum-secret-key"))
    API_KEY: Optional[str] = field(default_factory=lambda: os.getenv("API_KEY"))
    CORS_ORIGINS: List[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))
    
    # Database
    DATABASE_URL: Optional[str] = field(default_factory=lambda: os.getenv("DATABASE_URL"))
    REDIS_URL: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))
    
    # Quantum features
    ENABLE_JIT: bool = True
    ENABLE_SIMD: bool = True
    ENABLE_QUANTUM_CACHE: bool = True
    ENABLE_PARALLEL_PROCESSING: bool = True
    ENABLE_METRICS: bool = True
    ENABLE_MONITORING: bool = True
    ENABLE_TRACING: bool = field(default_factory=lambda: os.getenv("ENABLE_TRACING", "false").lower() == "true")
    
    @staticmethod
    def _quantum_tune_workers() -> int:
        """AI-powered worker tuning."""
        cpu_count = mp.cpu_count()
        
        if PSUTIL_AVAILABLE:
            memory_gb = psutil.virtual_memory().total / (1024 ** 3)
            cpu_freq = psutil.cpu_freq().max if psutil.cpu_freq() else 3000
            
            quantum_factor = min(2.0, cpu_freq / 2000)
            memory_factor = min(2.0, memory_gb / 8)
            
            optimal_workers = int(cpu_count * 16 * quantum_factor * memory_factor)
            return min(256, max(1, optimal_workers))
        
        return min(128, max(1, cpu_count * 8))
    
    @staticmethod
    def _quantum_tune_memory() -> int:
        """Quantum memory optimization."""
        if PSUTIL_AVAILABLE:
            total_mb = psutil.virtual_memory().total / (1024 * 1024)
            return int(total_mb * 0.9)
        return 8192
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        configs = {
            "development": {
                "DEBUG": True,
                "WORKERS": 1,
                "ENABLE_METRICS": False,
                "GC_THRESHOLD": 1000
            },
            "testing": {
                "DEBUG": False,
                "WORKERS": 1,
                "CACHE_SIZE": 100,
                "ENABLE_METRICS": False
            },
            "staging": {
                "DEBUG": False,
                "WORKERS": max(1, mp.cpu_count()),
                "ENABLE_METRICS": True
            },
            "quantum": {
                "DEBUG": False,
                "WORKERS": self.WORKERS,
                "ENABLE_METRICS": True,
                "ENABLE_MONITORING": True,
                "ENABLE_QUANTUM_CACHE": True
            }
        }
        
        return configs.get(self.ENVIRONMENT, configs["quantum"])
    
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
    
    def validate(self) -> bool:
        """Validate configuration."""
        if self.PORT < 1 or self.PORT > 65535:
            raise ValueError(f"Invalid port: {self.PORT}")
        
        if self.WORKERS < 1:
            raise ValueError(f"Invalid workers: {self.WORKERS}")
        
        if self.MAX_MEMORY_MB < 512:
            raise ValueError(f"Insufficient memory: {self.MAX_MEMORY_MB}MB")
        
        return True

# Global configuration instance
config = QuantumConfig()
config.apply_environment_config()
config.validate() 