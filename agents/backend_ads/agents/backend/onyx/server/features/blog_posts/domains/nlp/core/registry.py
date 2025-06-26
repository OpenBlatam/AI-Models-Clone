"""
Registry System for Modular NLP Components.

This module provides a registry system for dynamically registering and managing
NLP analyzers, enhancers, and other components in the modular system.
"""

import logging
from typing import Dict, List, Optional, Type, Any, Callable
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass, field
from datetime import datetime

from .interfaces import (
    IAnalyzer, IEnhancer, IPlugin, AnalysisType, AnalysisResult, AnalysisConfig
)
from .exceptions import (
    AnalyzerNotAvailableException, PluginException, PluginConflictException
)

logger = logging.getLogger(__name__)

@dataclass
class ComponentInfo:
    """Information about a registered component."""
    name: str
    component_type: str  # analyzer, enhancer, plugin
    version: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registration_time: datetime = field(default_factory=datetime.now)
    is_available: bool = True

class ComponentRegistry:
    """Registry for managing NLP components."""
    
    def __init__(self):
        """Initialize the component registry."""
        self._components: Dict[str, Any] = {}
        self._component_info: Dict[str, ComponentInfo] = {}
        self._components_by_type: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._analyzers_by_analysis_type: Dict[AnalysisType, List[str]] = defaultdict(list)
        self._lock = Lock()
        
        # Event callbacks
        self._on_register_callbacks: List[Callable[[str, Any], None]] = []
        self._on_unregister_callbacks: List[Callable[[str], None]] = []
    
    def register_component(
        self,
        name: str,
        component: Any,
        component_type: str,
        version: str = "1.0.0",
        description: str = "",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False
    ) -> bool:
        """
        Register a component in the registry.
        
        Args:
            name: Unique name for the component
            component: The component instance
            component_type: Type of component (analyzer, enhancer, plugin)
            version: Component version
            description: Component description
            dependencies: List of dependencies
            metadata: Additional metadata
            overwrite: Whether to overwrite existing component
            
        Returns:
            True if registration successful
            
        Raises:
            PluginConflictException: If component already exists and overwrite=False
        """
        with self._lock:
            # Check if component already exists
            if name in self._components and not overwrite:
                raise PluginConflictException(
                    name, 
                    "existing", 
                    f"Component '{name}' already registered"
                )
            
            # Validate component based on type
            if not self._validate_component(component, component_type):
                logger.error(f"Invalid component '{name}' of type '{component_type}'")
                return False
            
            # Check availability
            is_available = True
            if hasattr(component, 'is_available'):
                try:
                    is_available = component.is_available()
                except Exception as e:
                    logger.warning(f"Error checking availability for {name}: {e}")
                    is_available = False
            
            # Create component info
            info = ComponentInfo(
                name=name,
                component_type=component_type,
                version=version,
                description=description,
                dependencies=dependencies or [],
                metadata=metadata or {},
                is_available=is_available
            )
            
            # Register component
            self._components[name] = component
            self._component_info[name] = info
            self._components_by_type[component_type][name] = component
            
            # Special handling for analyzers
            if component_type == "analyzer" and isinstance(component, IAnalyzer):
                analysis_type = component.analysis_type
                if name not in self._analyzers_by_analysis_type[analysis_type]:
                    self._analyzers_by_analysis_type[analysis_type].append(name)
            
            # Trigger callbacks
            for callback in self._on_register_callbacks:
                try:
                    callback(name, component)
                except Exception as e:
                    logger.error(f"Error in register callback: {e}")
            
            logger.info(f"Registered {component_type} '{name}' v{version}")
            return True
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a component by name."""
        return self._components.get(name)
    
    def get_component_info(self, name: str) -> Optional[ComponentInfo]:
        """Get component information by name."""
        return self._component_info.get(name)
    
    def get_components_by_type(self, component_type: str) -> Dict[str, Any]:
        """Get all components of a specific type."""
        return self._components_by_type[component_type].copy()
    
    def get_analyzers_by_analysis_type(self, analysis_type: AnalysisType) -> List[IAnalyzer]:
        """Get all analyzers for a specific analysis type."""
        analyzer_names = self._analyzers_by_analysis_type[analysis_type]
        analyzers = []
        
        for name in analyzer_names:
            analyzer = self._components.get(name)
            if analyzer and self._component_info[name].is_available:
                analyzers.append(analyzer)
        
        return analyzers
    
    def get_available_components(self, component_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all available components, optionally filtered by type."""
        available = {}
        
        for name, component in self._components.items():
            info = self._component_info[name]
            if info.is_available:
                if component_type is None or info.component_type == component_type:
                    available[name] = component
        
        return available
    
    def is_component_available(self, name: str) -> bool:
        """Check if a component is available."""
        info = self._component_info.get(name)
        return info is not None and info.is_available
    
    def _validate_component(self, component: Any, component_type: str) -> bool:
        """Validate component based on its type."""
        if component_type == "analyzer":
            return isinstance(component, IAnalyzer)
        elif component_type == "enhancer":
            return isinstance(component, IEnhancer)
        elif component_type == "plugin":
            return isinstance(component, IPlugin)
        else:
            # Unknown type, allow it but log warning
            logger.warning(f"Unknown component type: {component_type}")
            return True

class AnalyzerRegistry(ComponentRegistry):
    """Specialized registry for NLP analyzers."""
    
    def register_analyzer(
        self,
        analyzer: IAnalyzer,
        overwrite: bool = False
    ) -> bool:
        """
        Register an analyzer.
        
        Args:
            analyzer: The analyzer to register
            overwrite: Whether to overwrite existing analyzer
            
        Returns:
            True if registration successful
        """
        return self.register_component(
            name=analyzer.name,
            component=analyzer,
            component_type="analyzer",
            version=analyzer.version,
            description=f"Analyzer for {analyzer.analysis_type.value} analysis",
            overwrite=overwrite
        )
    
    def get_analyzer(self, name: str) -> Optional[IAnalyzer]:
        """Get an analyzer by name."""
        component = self.get_component(name)
        return component if isinstance(component, IAnalyzer) else None
    
    def get_available_analyzers(self) -> List[IAnalyzer]:
        """Get all available analyzers."""
        analyzers = []
        
        for analyzer in self.get_available_components("analyzer").values():
            if isinstance(analyzer, IAnalyzer):
                analyzers.append(analyzer)
        
        return analyzers
    
    def get_analyzers_for_type(self, analysis_type: AnalysisType) -> List[IAnalyzer]:
        """Get all available analyzers for a specific analysis type."""
        return self.get_analyzers_by_analysis_type(analysis_type)

# Global registry instances
_analyzer_registry: Optional[AnalyzerRegistry] = None

def get_analyzer_registry() -> AnalyzerRegistry:
    """Get the global analyzer registry."""
    global _analyzer_registry
    if _analyzer_registry is None:
        _analyzer_registry = AnalyzerRegistry()
    return _analyzer_registry

def reset_registries():
    """Reset all global registries."""
    global _analyzer_registry
    _analyzer_registry = None
