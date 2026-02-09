"""
Feature Flags
=============

Sistema de feature flags para control de features.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FeatureFlagType(Enum):
    """Tipos de feature flags"""
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    TARGETING = "targeting"


@dataclass
class FeatureFlag:
    """Feature flag individual"""
    name: str
    enabled: bool
    flag_type: FeatureFlagType = FeatureFlagType.BOOLEAN
    percentage: float = 100.0  # Para percentage rollout
    targeting: Dict[str, Any] = None  # Para targeting específico
    metadata: Dict[str, Any] = None


class FeatureFlagManager:
    """
    Gestor de feature flags
    
    Ejemplo:
        flags = FeatureFlagManager()
        
        # Registrar flag
        flags.register("new_feature", FeatureFlag(
            name="new_feature",
            enabled=True,
            flag_type=FeatureFlagType.PERCENTAGE,
            percentage=50.0
        ))
        
        # Verificar flag
        if await flags.is_enabled("new_feature", user_id="123"):
            # Usar nueva feature
            pass
    """
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self._lock = asyncio.Lock()
        self._callbacks: Dict[str, list] = {}
    
    def register(self, flag: FeatureFlag):
        """Registra un feature flag"""
        async def _register():
            async with self._lock:
                self.flags[flag.name] = flag
                logger.info(f"Feature flag registered: {flag.name}")
        
        asyncio.create_task(_register())
    
    async def is_enabled(
        self,
        name: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Verifica si un feature flag está habilitado
        
        Args:
            name: Nombre del flag
            user_id: ID del usuario (para targeting)
            context: Contexto adicional
            
        Returns:
            True si está habilitado
        """
        async with self._lock:
            if name not in self.flags:
                logger.warning(f"Feature flag not found: {name}")
                return False
            
            flag = self.flags[name]
            
            if not flag.enabled:
                return False
            
            # Boolean flag
            if flag.flag_type == FeatureFlagType.BOOLEAN:
                return True
            
            # Percentage rollout
            if flag.flag_type == FeatureFlagType.PERCENTAGE:
                if user_id:
                    # Hash user_id para consistencia
                    import hashlib
                    hash_value = int(
                        hashlib.md5(f"{name}:{user_id}".encode()).hexdigest(),
                        16
                    )
                    percentage = (hash_value % 100) + 1
                    return percentage <= flag.percentage
                return False
            
            # Targeting
            if flag.flag_type == FeatureFlagType.TARGETING:
                if not flag.targeting:
                    return True
                
                # Verificar targeting rules
                if user_id and "user_ids" in flag.targeting:
                    return user_id in flag.targeting["user_ids"]
                
                if context:
                    for key, value in flag.targeting.items():
                        if key in context and context[key] == value:
                            return True
                
                return False
            
            return False
    
    def on_change(self, name: str, callback: Callable):
        """Registra callback para cambios en flag"""
        if name not in self._callbacks:
            self._callbacks[name] = []
        self._callbacks[name].append(callback)
    
    async def update(self, name: str, enabled: bool, **kwargs):
        """Actualiza un feature flag"""
        async with self._lock:
            if name in self.flags:
                flag = self.flags[name]
                flag.enabled = enabled
                flag.__dict__.update(kwargs)
                
                # Ejecutar callbacks
                if name in self._callbacks:
                    for callback in self._callbacks[name]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(flag)
                            else:
                                callback(flag)
                        except Exception as e:
                            logger.error(f"Error in callback: {e}")
    
    def get_all(self) -> Dict[str, FeatureFlag]:
        """Obtiene todos los feature flags"""
        return dict(self.flags)


# Instancia global
default_feature_flags = FeatureFlagManager()




