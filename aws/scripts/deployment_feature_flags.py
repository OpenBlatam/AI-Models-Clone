#!/usr/bin/env python3
"""
Feature Flags Manager
Manages feature flags for gradual rollouts and A/B testing
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class FeatureFlagType(Enum):
    """Feature flag types"""
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    ENVIRONMENT = "environment"


@dataclass
class FeatureFlag:
    """Feature flag definition"""
    name: str
    enabled: bool = False
    flag_type: FeatureFlagType = FeatureFlagType.BOOLEAN
    percentage: int = 0  # 0-100 for percentage rollout
    user_list: List[str] = None
    environments: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_list is None:
            self.user_list = []
        if self.environments is None:
            self.environments = ['production']
        if self.metadata is None:
            self.metadata = {}


class FeatureFlagsManager:
    """Manages feature flags"""
    
    def __init__(self, flags_file: str = '/var/lib/feature-flags/flags.json'):
        self.flags_file = Path(flags_file)
        self.flags_file.parent.mkdir(parents=True, exist_ok=True)
        self.flags: Dict[str, FeatureFlag] = {}
        self._load_flags()
    
    def _load_flags(self):
        """Load feature flags from file"""
        if self.flags_file.exists():
            try:
                with open(self.flags_file, 'r') as f:
                    data = json.load(f)
                    for flag_data in data.get('flags', []):
                        flag = FeatureFlag(**flag_data)
                        self.flags[flag.name] = flag
            except Exception as e:
                logger.error(f"Failed to load feature flags: {e}")
    
    def _save_flags(self):
        """Save feature flags to file"""
        try:
            data = {
                'flags': [asdict(flag) for flag in self.flags.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.flags_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feature flags: {e}")
    
    def create_flag(
        self,
        name: str,
        enabled: bool = False,
        flag_type: FeatureFlagType = FeatureFlagType.BOOLEAN,
        percentage: int = 0,
        environments: Optional[List[str]] = None
    ) -> FeatureFlag:
        """Create a new feature flag"""
        flag = FeatureFlag(
            name=name,
            enabled=enabled,
            flag_type=flag_type,
            percentage=percentage,
            environments=environments or ['production']
        )
        self.flags[name] = flag
        self._save_flags()
        logger.info(f"Created feature flag: {name}")
        return flag
    
    def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get a feature flag by name"""
        return self.flags.get(name)
    
    def is_enabled(self, name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if a feature flag is enabled"""
        flag = self.flags.get(name)
        if not flag:
            return False
        
        if not flag.enabled:
            return False
        
        # Check environment
        if context and 'environment' in context:
            if context['environment'] not in flag.environments:
                return False
        
        # Check flag type
        if flag.flag_type == FeatureFlagType.BOOLEAN:
            return flag.enabled
        
        elif flag.flag_type == FeatureFlagType.PERCENTAGE:
            if context and 'user_id' in context:
                # Deterministic percentage based on user_id
                import hashlib
                hash_value = int(hashlib.md5(f"{name}_{context['user_id']}".encode()).hexdigest(), 16)
                return (hash_value % 100) < flag.percentage
            return False
        
        elif flag.flag_type == FeatureFlagType.USER_LIST:
            if context and 'user_id' in context:
                return context['user_id'] in flag.user_list
            return False
        
        elif flag.flag_type == FeatureFlagType.ENVIRONMENT:
            if context and 'environment' in context:
                return context['environment'] in flag.environments
            return False
        
        return False
    
    def enable_flag(self, name: str):
        """Enable a feature flag"""
        if name in self.flags:
            self.flags[name].enabled = True
            self._save_flags()
            logger.info(f"Enabled feature flag: {name}")
    
    def disable_flag(self, name: str):
        """Disable a feature flag"""
        if name in self.flags:
            self.flags[name].enabled = False
            self._save_flags()
            logger.info(f"Disabled feature flag: {name}")
    
    def set_percentage(self, name: str, percentage: int):
        """Set percentage rollout for a flag"""
        if name in self.flags:
            self.flags[name].percentage = max(0, min(100, percentage))
            self.flags[name].flag_type = FeatureFlagType.PERCENTAGE
            self._save_flags()
            logger.info(f"Set feature flag {name} to {percentage}%")
    
    def list_flags(self) -> List[FeatureFlag]:
        """List all feature flags"""
        return list(self.flags.values())
