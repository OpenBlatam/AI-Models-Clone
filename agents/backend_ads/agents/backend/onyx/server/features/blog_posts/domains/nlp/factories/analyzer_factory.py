"""
Analyzer Factory for Modular NLP System.

This module provides factory classes for creating and managing NLP analyzers
dynamically, supporting plugin-based architecture and runtime configuration.
"""

import logging
from typing import Dict, List, Optional, Type, Any, Callable
from abc import ABC, abstractmethod
from enum import Enum

from ..core import (
    IAnalyzer, AnalysisType, AnalysisConfig, get_config,
    AnalyzerNotAvailableException, ConfigurationException,
    get_analyzer_registry
)

logger = logging.getLogger(__name__)

class AnalyzerCreationStrategy(Enum):
    """Strategies for analyzer creation."""
    SINGLETON = "singleton"      # One instance per analyzer type
    FACTORY = "factory"         # New instance for each request
    POOLED = "pooled"          # Pool of reusable instances

class IAnalyzerFactory(ABC):
    """Interface for analyzer factories."""
    
    @abstractmethod
    def create_analyzer(
        self,
        analyzer_type: str,
        config: Optional[AnalysisConfig] = None,
        **kwargs
    ) -> IAnalyzer:
        """Create an analyzer instance."""
        pass
    
    @abstractmethod
    def get_available_types(self) -> List[str]:
        """Get list of available analyzer types."""
        pass
    
    @abstractmethod
    def is_available(self, analyzer_type: str) -> bool:
        """Check if analyzer type is available."""
        pass

class AnalyzerFactory(IAnalyzerFactory):
    """
    Main factory for creating NLP analyzers.
    
    Supports multiple creation strategies and automatic dependency checking.
    """
    
    def __init__(self, strategy: AnalyzerCreationStrategy = AnalyzerCreationStrategy.SINGLETON):
        """
        Initialize analyzer factory.
        
        Args:
            strategy: Creation strategy to use
        """
        self._strategy = strategy
        self._analyzer_classes: Dict[str, Type[IAnalyzer]] = {}
        self._analyzer_instances: Dict[str, IAnalyzer] = {}
        self._analyzer_pools: Dict[str, List[IAnalyzer]] = {}
        self._creation_callbacks: List[Callable[[str, IAnalyzer], None]] = []
        
        # Register built-in analyzers
        self._register_builtin_analyzers()
        
        logger.info(f"AnalyzerFactory initialized with {strategy.value} strategy")
    
    def register_analyzer_class(
        self,
        analyzer_type: str,
        analyzer_class: Type[IAnalyzer],
        overwrite: bool = False
    ) -> bool:
        """
        Register an analyzer class.
        
        Args:
            analyzer_type: Unique identifier for the analyzer type
            analyzer_class: Class that implements IAnalyzer
            overwrite: Whether to overwrite existing registration
            
        Returns:
            True if registration successful
        """
        if analyzer_type in self._analyzer_classes and not overwrite:
            logger.warning(f"Analyzer type '{analyzer_type}' already registered")
            return False
        
        # Validate analyzer class
        if not issubclass(analyzer_class, IAnalyzer):
            logger.error(f"Class {analyzer_class} does not implement IAnalyzer")
            return False
        
        self._analyzer_classes[analyzer_type] = analyzer_class
        
        # Clear cached instances if using singleton strategy
        if self._strategy == AnalyzerCreationStrategy.SINGLETON:
            self._analyzer_instances.pop(analyzer_type, None)
        
        logger.info(f"Registered analyzer class: {analyzer_type}")
        return True
    
    def create_analyzer(
        self,
        analyzer_type: str,
        config: Optional[AnalysisConfig] = None,
        **kwargs
    ) -> IAnalyzer:
        """
        Create an analyzer instance.
        
        Args:
            analyzer_type: Type of analyzer to create
            config: Optional configuration
            **kwargs: Additional arguments for analyzer constructor
            
        Returns:
            Analyzer instance
            
        Raises:
            AnalyzerNotAvailableException: If analyzer type is not available
        """
        if analyzer_type not in self._analyzer_classes:
            raise AnalyzerNotAvailableException(
                analyzer_type,
                f"Analyzer type '{analyzer_type}' not registered"
            )
        
        analyzer_class = self._analyzer_classes[analyzer_type]
        
        # Check availability
        if not self._is_analyzer_available(analyzer_class):
            raise AnalyzerNotAvailableException(
                analyzer_type,
                "Dependencies not available"
            )
        
        # Apply creation strategy
        if self._strategy == AnalyzerCreationStrategy.SINGLETON:
            return self._create_singleton(analyzer_type, analyzer_class, config, **kwargs)
        elif self._strategy == AnalyzerCreationStrategy.FACTORY:
            return self._create_instance(analyzer_class, config, **kwargs)
        elif self._strategy == AnalyzerCreationStrategy.POOLED:
            return self._create_pooled(analyzer_type, analyzer_class, config, **kwargs)
        else:
            raise ConfigurationException(f"Unknown creation strategy: {self._strategy}")
    
    def get_available_types(self) -> List[str]:
        """Get list of available analyzer types."""
        available = []
        
        for analyzer_type, analyzer_class in self._analyzer_classes.items():
            if self._is_analyzer_available(analyzer_class):
                available.append(analyzer_type)
        
        return available
    
    def is_available(self, analyzer_type: str) -> bool:
        """Check if analyzer type is available."""
        if analyzer_type not in self._analyzer_classes:
            return False
        
        analyzer_class = self._analyzer_classes[analyzer_type]
        return self._is_analyzer_available(analyzer_class)
    
    def get_analyzer_info(self, analyzer_type: str) -> Optional[Dict[str, Any]]:
        """Get information about an analyzer type."""
        if analyzer_type not in self._analyzer_classes:
            return None
        
        analyzer_class = self._analyzer_classes[analyzer_type]
        
        # Create temporary instance to get info
        try:
            temp_analyzer = analyzer_class()
            return {
                'type': analyzer_type,
                'name': temp_analyzer.name,
                'analysis_type': temp_analyzer.analysis_type.value,
                'version': temp_analyzer.version,
                'description': getattr(temp_analyzer, 'description', ''),
                'dependencies': getattr(temp_analyzer, 'dependencies', []),
                'available': self._is_analyzer_available(analyzer_class)
            }
        except Exception as e:
            logger.error(f"Error getting info for {analyzer_type}: {e}")
            return {
                'type': analyzer_type,
                'available': False,
                'error': str(e)
            }
    
    def add_creation_callback(self, callback: Callable[[str, IAnalyzer], None]):
        """Add callback to be called when analyzer is created."""
        self._creation_callbacks.append(callback)
    
    def clear_cache(self):
        """Clear all cached instances."""
        self._analyzer_instances.clear()
        self._analyzer_pools.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get factory statistics."""
        return {
            'strategy': self._strategy.value,
            'registered_types': len(self._analyzer_classes),
            'available_types': len(self.get_available_types()),
            'singleton_instances': len(self._analyzer_instances),
            'pooled_instances': sum(len(pool) for pool in self._analyzer_pools.values()),
            'registered_analyzers': list(self._analyzer_classes.keys())
        }
    
    def _create_singleton(
        self,
        analyzer_type: str,
        analyzer_class: Type[IAnalyzer],
        config: Optional[AnalysisConfig],
        **kwargs
    ) -> IAnalyzer:
        """Create singleton analyzer instance."""
        if analyzer_type not in self._analyzer_instances:
            self._analyzer_instances[analyzer_type] = self._create_instance(
                analyzer_class, config, **kwargs
            )
            self._trigger_creation_callbacks(analyzer_type, self._analyzer_instances[analyzer_type])
        
        return self._analyzer_instances[analyzer_type]
    
    def _create_pooled(
        self,
        analyzer_type: str,
        analyzer_class: Type[IAnalyzer],
        config: Optional[AnalysisConfig],
        **kwargs
    ) -> IAnalyzer:
        """Create pooled analyzer instance."""
        if analyzer_type not in self._analyzer_pools:
            self._analyzer_pools[analyzer_type] = []
        
        pool = self._analyzer_pools[analyzer_type]
        
        # Try to reuse existing instance from pool
        if pool:
            return pool.pop()
        
        # Create new instance if pool is empty
        analyzer = self._create_instance(analyzer_class, config, **kwargs)
        self._trigger_creation_callbacks(analyzer_type, analyzer)
        return analyzer
    
    def _create_instance(
        self,
        analyzer_class: Type[IAnalyzer],
        config: Optional[AnalysisConfig],
        **kwargs
    ) -> IAnalyzer:
        """Create new analyzer instance."""
        try:
            # Create analyzer instance
            analyzer = analyzer_class(**kwargs)
            
            # Register with global registry
            registry = get_analyzer_registry()
            registry.register_analyzer(analyzer, overwrite=True)
            
            logger.debug(f"Created analyzer instance: {analyzer.name}")
            return analyzer
            
        except Exception as e:
            logger.error(f"Error creating analyzer instance: {e}")
            raise AnalyzerNotAvailableException(
                analyzer_class.__name__,
                f"Failed to create instance: {e}"
            )
    
    def _is_analyzer_available(self, analyzer_class: Type[IAnalyzer]) -> bool:
        """Check if analyzer class is available."""
        try:
            # Create temporary instance to check availability
            temp_analyzer = analyzer_class()
            return temp_analyzer.is_available()
        except Exception as e:
            logger.debug(f"Analyzer {analyzer_class.__name__} not available: {e}")
            return False
    
    def _trigger_creation_callbacks(self, analyzer_type: str, analyzer: IAnalyzer):
        """Trigger creation callbacks."""
        for callback in self._creation_callbacks:
            try:
                callback(analyzer_type, analyzer)
            except Exception as e:
                logger.error(f"Error in creation callback: {e}")
    
    def _register_builtin_analyzers(self):
        """Register built-in analyzer types."""
        try:
            # Import and register Flesch analyzer
            from ..analyzers.readability.flesch_analyzer import FleschReadabilityAnalyzer
            self.register_analyzer_class("flesch_readability", FleschReadabilityAnalyzer)
            
            logger.info("Registered built-in analyzers")
            
        except ImportError as e:
            logger.warning(f"Could not import built-in analyzers: {e}")

class ReadabilityAnalyzerFactory(AnalyzerFactory):
    """Specialized factory for readability analyzers."""
    
    def __init__(self):
        """Initialize readability analyzer factory."""
        super().__init__(AnalyzerCreationStrategy.SINGLETON)
        
        # Register readability-specific analyzers
        self._register_readability_analyzers()
    
    def create_readability_analyzer(
        self,
        metrics: Optional[List[str]] = None,
        target_grade_level: float = 8.0
    ) -> IAnalyzer:
        """
        Create readability analyzer with specific configuration.
        
        Args:
            metrics: List of metrics to calculate (flesch, gunning_fog, etc.)
            target_grade_level: Target reading grade level
            
        Returns:
            Configured readability analyzer
        """
        config = AnalysisConfig(
            parameters={
                'metrics': metrics or ['flesch'],
                'target_grade_level': target_grade_level
            }
        )
        
        # For now, use Flesch analyzer as default
        return self.create_analyzer("flesch_readability", config)
    
    def _register_readability_analyzers(self):
        """Register readability-specific analyzers."""
        # Additional readability analyzers can be registered here
        pass

class SentimentAnalyzerFactory(AnalyzerFactory):
    """Specialized factory for sentiment analyzers."""
    
    def __init__(self):
        """Initialize sentiment analyzer factory."""
        super().__init__(AnalyzerCreationStrategy.SINGLETON)

class SEOAnalyzerFactory(AnalyzerFactory):
    """Specialized factory for SEO analyzers."""
    
    def __init__(self):
        """Initialize SEO analyzer factory."""
        super().__init__(AnalyzerCreationStrategy.SINGLETON)

# Global factory instances
_default_factory: Optional[AnalyzerFactory] = None
_readability_factory: Optional[ReadabilityAnalyzerFactory] = None
_sentiment_factory: Optional[SentimentAnalyzerFactory] = None
_seo_factory: Optional[SEOAnalyzerFactory] = None

def get_analyzer_factory() -> AnalyzerFactory:
    """Get the global analyzer factory."""
    global _default_factory
    if _default_factory is None:
        _default_factory = AnalyzerFactory()
    return _default_factory

def get_readability_factory() -> ReadabilityAnalyzerFactory:
    """Get the readability analyzer factory."""
    global _readability_factory
    if _readability_factory is None:
        _readability_factory = ReadabilityAnalyzerFactory()
    return _readability_factory

def get_sentiment_factory() -> SentimentAnalyzerFactory:
    """Get the sentiment analyzer factory."""
    global _sentiment_factory
    if _sentiment_factory is None:
        _sentiment_factory = SentimentAnalyzerFactory()
    return _sentiment_factory

def get_seo_factory() -> SEOAnalyzerFactory:
    """Get the SEO analyzer factory."""
    global _seo_factory
    if _seo_factory is None:
        _seo_factory = SEOAnalyzerFactory()
    return _seo_factory

def reset_factories():
    """Reset all global factory instances."""
    global _default_factory, _readability_factory, _sentiment_factory, _seo_factory
    _default_factory = None
    _readability_factory = None
    _sentiment_factory = None
    _seo_factory = None 