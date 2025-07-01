"""
🏭 BLATAM AI FACTORIES MODULE v5.0.0
====================================

Factories modulares para creación limpia:
- 🏗️ Component Factory base
- 🚀 Engine Factory specializations  
- 🔧 Service Factory patterns
- 🎯 AI System Factory
"""

from typing import Dict, Any, Optional, List
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# =============================================================================
# 🏗️ BASE FACTORY
# =============================================================================

class BlatamComponentFactory(ABC):
    """Factory base para componentes Blatam."""
    
    @abstractmethod
    async def create(self, config: Dict[str, Any], **kwargs) -> Any:
        """Crea un componente."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configuración."""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto."""
        pass

# =============================================================================
# 🚀 ENGINE FACTORIES
# =============================================================================

class SpeedEngineFactory(BlatamComponentFactory):
    """Factory para Speed Engine."""
    
    async def create(self, config: Dict[str, Any], **kwargs) -> Any:
        """Crea Speed Engine."""
        # Lazy import to avoid circular dependencies
        try:
            from ..engines.speed import UltraSpeedEngine
            return UltraSpeedEngine(config)
        except ImportError:
            logger.warning("Speed Engine not available")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configuración de Speed Engine."""
        required = ['enable_uvloop', 'cache_size']
        return all(key in config for key in required)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto de Speed Engine."""
        return {
            'enable_uvloop': True,
            'enable_fast_cache': True,
            'enable_lazy_loading': True,
            'cache_size': 10000,
            'max_workers': 8
        }

class NLPEngineFactory(BlatamComponentFactory):
    """Factory para NLP Engine."""
    
    async def create(self, config: Dict[str, Any], **kwargs) -> Any:
        """Crea NLP Engine."""
        try:
            from ..engines.nlp import UltraNLPEngine
            return UltraNLPEngine(config)
        except ImportError:
            logger.warning("NLP Engine not available")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configuración de NLP Engine."""
        required = ['primary_llm', 'embedding_model']
        return all(key in config for key in required)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto de NLP Engine."""
        return {
            'primary_llm': 'gpt-4-turbo-preview',
            'embedding_model': 'text-embedding-3-large',
            'enable_multilingual': True,
            'enable_speech': True
        }

class LangChainEngineFactory(BlatamComponentFactory):
    """Factory para LangChain Engine."""
    
    async def create(self, config: Dict[str, Any], **kwargs) -> Any:
        """Crea LangChain Engine."""
        try:
            from ..engines.langchain import UltraLangChainEngine
            return UltraLangChainEngine(config)
        except ImportError:
            logger.warning("LangChain Engine not available")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configuración de LangChain Engine."""
        required = ['llm_provider', 'llm_model']
        return all(key in config for key in required)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto de LangChain Engine."""
        return {
            'llm_provider': 'openai',
            'llm_model': 'gpt-4-turbo-preview',
            'default_agent_type': 'openai-functions',
            'enable_web_search': True
        }

class EvolutionEngineFactory(BlatamComponentFactory):
    """Factory para Evolution Engine."""
    
    async def create(self, config: Dict[str, Any], **kwargs) -> Any:
        """Crea Evolution Engine."""
        try:
            from ..engines.evolution import SelfEvolvingEngine
            return SelfEvolvingEngine(config)
        except ImportError:
            logger.warning("Evolution Engine not available")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida configuración de Evolution Engine."""
        required = ['optimization_strategy', 'learning_mode']
        return all(key in config for key in required)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto de Evolution Engine."""
        return {
            'optimization_strategy': 'balanced',
            'learning_mode': 'active',
            'enable_self_healing': True,
            'enable_continuous_learning': True
        }

# =============================================================================
# 🎯 AI SYSTEM FACTORY
# =============================================================================

class BlatamAIFactory:
    """Factory principal para sistema Blatam AI."""
    
    def __init__(self):
        self.engine_factories = {
            'speed': SpeedEngineFactory(),
            'nlp': NLPEngineFactory(),
            'langchain': LangChainEngineFactory(),
            'evolution': EvolutionEngineFactory()
        }
    
    async def create_ai_system(
        self,
        architecture: str = "modular",
        enabled_engines: Optional[List[str]] = None,
        custom_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> Any:
        """Crea sistema AI completo."""
        
        if architecture == "modular":
            return await self._create_modular_system(enabled_engines, custom_configs, **kwargs)
        elif architecture == "lightweight":
            return await self._create_lightweight_system(custom_configs, **kwargs)
        elif architecture == "full":
            return await self._create_full_system(custom_configs, **kwargs)
        else:
            raise ValueError(f"Unknown architecture: {architecture}")
    
    async def _create_modular_system(
        self,
        enabled_engines: Optional[List[str]],
        custom_configs: Optional[Dict[str, Dict[str, Any]]],
        **kwargs
    ) -> Any:
        """Crea sistema modular."""
        from ..core import ServiceContainer
        from ..engines.manager import ModularEngineManager
        from .. import ModularBlatamAI
        
        # Create service container
        container = ServiceContainer()
        
        # Create engine manager
        engine_manager = ModularEngineManager()
        
        # Register engine factories
        from ..engines.manager import EngineRegistry, EngineMetadata
        registry = engine_manager.registry
        
        for engine_type, factory in self.engine_factories.items():
            metadata = EngineMetadata(
                name=engine_type,
                engine_type=engine_type,
                capabilities={f"{engine_type}_processing"}
            )
            registry.register_engine(engine_type, factory, metadata, factory.get_default_config())
        
        # Prepare configs
        if enabled_engines is None:
            enabled_engines = ['speed', 'nlp', 'langchain', 'evolution']
        
        configs = {}
        for engine_type in enabled_engines:
            if engine_type in self.engine_factories:
                default_config = self.engine_factories[engine_type].get_default_config()
                custom = custom_configs.get(engine_type, {}) if custom_configs else {}
                configs[engine_type] = {**default_config, **custom}
        
        # Initialize engines
        await engine_manager.initialize_engines(configs, enabled_engines)
        
        # Create AI system
        ai = ModularBlatamAI(container, engine_manager)
        await ai.initialize()
        
        return ai
    
    async def _create_lightweight_system(self, custom_configs, **kwargs):
        """Crea sistema ligero."""
        return await self._create_modular_system(['speed', 'nlp'], custom_configs, **kwargs)
    
    async def _create_full_system(self, custom_configs, **kwargs):
        """Crea sistema completo."""
        return await self._create_modular_system(None, custom_configs, **kwargs)
    
    def get_available_engines(self) -> List[str]:
        """Obtiene motores disponibles."""
        return list(self.engine_factories.keys())
    
    def get_engine_factory(self, engine_type: str) -> Optional[BlatamComponentFactory]:
        """Obtiene factory de motor."""
        return self.engine_factories.get(engine_type)

# =============================================================================
# 🏭 FACTORY FUNCTIONS
# =============================================================================

def create_blatam_ai_factory() -> BlatamAIFactory:
    """Crea factory principal."""
    return BlatamAIFactory()

async def create_ai_with_factory(
    architecture: str = "modular",
    **kwargs
) -> Any:
    """Crea AI usando factory pattern."""
    factory = create_blatam_ai_factory()
    return await factory.create_ai_system(architecture=architecture, **kwargs)

# =============================================================================
# 🌟 EXPORTS
# =============================================================================

__all__ = [
    "BlatamComponentFactory",
    "SpeedEngineFactory",
    "NLPEngineFactory", 
    "LangChainEngineFactory",
    "EvolutionEngineFactory",
    "BlatamAIFactory",
    "create_blatam_ai_factory",
    "create_ai_with_factory"
] 