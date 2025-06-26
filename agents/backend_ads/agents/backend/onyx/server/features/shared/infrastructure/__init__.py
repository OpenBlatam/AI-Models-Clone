"""
Shared Infrastructure Services
Configuration and deployment management
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development" 
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    version: str = "1.0.0"
    port: int = 8000
    replicas: int = 1

class ConfigurationManager:
    """Configuration management"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_cache: Dict[str, Any] = {}
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_name in self.config_cache:
            return self.config_cache[config_name]
        
        config_file = self.config_dir / f"{config_name}.yaml"
        
        if not config_file.exists():
            config_file = self.config_dir / f"{config_name}.json"
        
        if not config_file.exists():
            logger.warning(f"Configuration file not found: {config_name}")
            return {}
        
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix == '.yaml':
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            self.config_cache[config_name] = config
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration {config_name}: {e}")
            return {}
    
    def get_env_config(self, prefix: str = "BLATAM_") -> Dict[str, str]:
        """Get configuration from environment variables"""
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                env_config[config_key] = value
        
        return env_config

class InfrastructureService:
    """Basic infrastructure management"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.environment = Environment.DEVELOPMENT
    
    def get_status(self) -> Dict[str, Any]:
        """Get infrastructure status"""
        return {
            'environment': self.environment.value,
            'config_manager': 'active',
            'services': []
        }

# Global instance
_infrastructure_instance: Optional[InfrastructureService] = None

def get_infrastructure() -> InfrastructureService:
    """Get infrastructure instance"""
    global _infrastructure_instance
    if _infrastructure_instance is None:
        _infrastructure_instance = InfrastructureService()
    return _infrastructure_instance

def load_config(config_name: str) -> Dict[str, Any]:
    """Load configuration"""
    infrastructure = get_infrastructure()
    return infrastructure.config_manager.load_config(config_name)

__all__ = [
    'Environment',
    'ServiceConfig', 
    'ConfigurationManager',
    'InfrastructureService',
    'get_infrastructure',
    'load_config'
] 