#!/usr/bin/env python3
"""
Advanced IoC Container - Infrastructure Layer
============================================

Advanced dependency injection container with lifecycle management,
circular dependency resolution, and enterprise-grade features.
"""

import asyncio
import inspect
import logging
import threading
import weakref
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
import time

T = TypeVar('T')


class LifecyclePhase(Enum):
    """Lifecycle phases for managed components."""
    CONSTRUCTING = "constructing"
    CONSTRUCTED = "constructed"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    STARTING = "starting"
    STARTED = "started"
    STOPPING = "stopping"
    STOPPED = "stopped"
    DESTROYING = "destroying"
    DESTROYED = "destroyed"


class Scope(Enum):
    """Dependency injection scopes."""
    SINGLETON = "singleton"
    REQUEST = "request"
    SESSION = "session"
    PROTOTYPE = "prototype"


@dataclass
class ComponentMetadata:
    """Metadata for a registered component."""
    component_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    scope: Scope = Scope.SINGLETON
    lifecycle_aware: bool = False
    async_init: bool = False
    dependencies: List[str] = None
    tags: List[str] = None
    priority: int = 0
    created_at: float = None
    last_accessed: float = None
    access_count: int = 0
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = time.time()


class LifecycleAware(ABC):
    """Interface for components that need lifecycle management."""
    
    @abstractmethod
    async def on_construct(self) -> None:
        """Called after construction."""
        pass
    
    @abstractmethod
    async def on_initialize(self) -> None:
        """Called during initialization."""
        pass
    
    @abstractmethod
    async def on_start(self) -> None:
        """Called when starting."""
        pass
    
    @abstractmethod
    async def on_stop(self) -> None:
        """Called when stopping."""
        pass
    
    @abstractmethod
    async def on_destroy(self) -> None:
        """Called during destruction."""
        pass


class ContainerError(Exception):
    """Base exception for container errors."""
    pass


class CircularDependencyError(ContainerError):
    """Raised when circular dependencies are detected."""
    pass


class ComponentNotFoundError(ContainerError):
    """Raised when a component is not found."""
    pass


class ComponentInitializationError(ContainerError):
    """Raised when component initialization fails."""
    pass


class AdvancedIoCContainer:
    """
    Advanced IoC Container with enterprise-grade features.
    
    Features:
    - Dependency injection with circular dependency resolution
    - Lifecycle management for components
    - Multiple scopes (singleton, request, session, prototype)
    - Async initialization support
    - Component tagging and filtering
    - Performance monitoring
    - Memory management
    """
    
    def __init__(self):
        self._components: Dict[str, ComponentMetadata] = {}
        self._instances: Dict[str, Any] = {}
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}
        self._lifecycle_phases: Dict[str, LifecyclePhase] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
        self._circular_dependency_cache: Dict[str, bool] = {}
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        self._metrics = {
            'total_instances': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'initialization_time': 0.0,
            'memory_usage': 0
        }
    
    def register(
        self,
        component_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable] = None,
        scope: Scope = Scope.SINGLETON,
        tags: Optional[List[str]] = None,
        priority: int = 0
    ) -> 'AdvancedIoCContainer':
        """
        Register a component in the container.
        
        Args:
            component_type: The interface/abstract type
            implementation_type: The concrete implementation
            factory: Factory function for creating instances
            scope: The scope for the component
            tags: Tags for component discovery
            priority: Initialization priority (higher = earlier)
        
        Returns:
            Self for method chaining
        """
        with self._lock:
            component_name = component_type.__name__
            
            # Determine implementation type
            if implementation_type is None:
                implementation_type = component_type
            
            # Analyze dependencies
            dependencies = self._analyze_dependencies(implementation_type)
            
            # Create metadata
            metadata = ComponentMetadata(
                component_type=component_type,
                implementation_type=implementation_type,
                factory=factory,
                scope=scope,
                lifecycle_aware=issubclass(implementation_type, LifecycleAware),
                async_init=self._has_async_init(implementation_type),
                dependencies=dependencies,
                tags=tags or [],
                priority=priority
            )
            
            self._components[component_name] = metadata
            self._dependency_graph[component_name] = dependencies
            
            self._logger.info(f"Registered component: {component_name} (scope: {scope})")
            
            return self
    
    def register_singleton(
        self,
        component_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable] = None,
        tags: Optional[List[str]] = None,
        priority: int = 0
    ) -> 'AdvancedIoCContainer':
        """Register a singleton component."""
        return self.register(component_type, implementation_type, factory, Scope.SINGLETON, tags, priority)
    
    def register_prototype(
        self,
        component_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable] = None,
        tags: Optional[List[str]] = None,
        priority: int = 0
    ) -> 'AdvancedIoCContainer':
        """Register a prototype component."""
        return self.register(component_type, implementation_type, factory, Scope.PROTOTYPE, tags, priority)
    
    async def resolve(self, component_type: Type[T]) -> T:
        """
        Resolve a component instance.
        
        Args:
            component_type: The type to resolve
        
        Returns:
            An instance of the component
        
        Raises:
            ComponentNotFoundError: If component is not registered
            CircularDependencyError: If circular dependencies are detected
            ComponentInitializationError: If initialization fails
        """
        component_name = component_type.__name__
        
        with self._lock:
            if component_name not in self._components:
                raise ComponentNotFoundError(f"Component not registered: {component_name}")
            
            metadata = self._components[component_name]
            
            # Check for circular dependencies
            if self._has_circular_dependency(component_name):
                raise CircularDependencyError(f"Circular dependency detected for: {component_name}")
            
            # Get or create instance based on scope
            if metadata.scope == Scope.SINGLETON:
                instance = await self._get_or_create_singleton(component_name, metadata)
            elif metadata.scope == Scope.PROTOTYPE:
                instance = await self._create_prototype(component_name, metadata)
            elif metadata.scope == Scope.REQUEST:
                instance = await self._get_or_create_scoped(component_name, metadata, "request")
            elif metadata.scope == Scope.SESSION:
                instance = await self._get_or_create_scoped(component_name, metadata, "session")
            else:
                raise ContainerError(f"Unsupported scope: {metadata.scope}")
            
            # Update metrics
            metadata.last_accessed = time.time()
            metadata.access_count += 1
            self._metrics['cache_hits'] += 1
            
            return instance
    
    async def resolve_all(self, component_type: Type[T]) -> List[T]:
        """
        Resolve all components of a given type.
        
        Args:
            component_type: The base type to resolve
        
        Returns:
            List of component instances
        """
        instances = []
        base_type_name = component_type.__name__
        
        with self._lock:
            for component_name, metadata in self._components.items():
                if (metadata.component_type == component_type or 
                    (metadata.implementation_type and issubclass(metadata.implementation_type, component_type))):
                    try:
                        instance = await self.resolve(metadata.component_type)
                        instances.append(instance)
                    except Exception as e:
                        self._logger.warning(f"Failed to resolve {component_name}: {e}")
        
        return instances
    
    def resolve_by_tag(self, tag: str) -> List[Any]:
        """
        Resolve all components with a specific tag.
        
        Args:
            tag: The tag to search for
        
        Returns:
            List of component instances
        """
        instances = []
        
        with self._lock:
            for component_name, metadata in self._components.items():
                if tag in metadata.tags:
                    try:
                        instance = asyncio.create_task(self.resolve(metadata.component_type))
                        instances.append(instance)
                    except Exception as e:
                        self._logger.warning(f"Failed to resolve tagged component {component_name}: {e}")
        
        return instances
    
    async def initialize_all(self) -> None:
        """Initialize all registered components in dependency order."""
        with self._lock:
            # Sort components by priority and dependencies
            sorted_components = self._topological_sort()
            
            self._logger.info(f"Initializing {len(sorted_components)} components...")
            start_time = time.time()
            
            for component_name in sorted_components:
                try:
                    await self._initialize_component(component_name)
                except Exception as e:
                    self._logger.error(f"Failed to initialize {component_name}: {e}")
                    raise ComponentInitializationError(f"Failed to initialize {component_name}: {e}")
            
            initialization_time = time.time() - start_time
            self._metrics['initialization_time'] = initialization_time
            self._logger.info(f"Initialization completed in {initialization_time:.2f}s")
    
    async def shutdown(self) -> None:
        """Shutdown the container and destroy all components."""
        with self._lock:
            self._logger.info("Shutting down container...")
            
            # Destroy components in reverse dependency order
            sorted_components = list(reversed(self._topological_sort()))
            
            for component_name in sorted_components:
                try:
                    await self._destroy_component(component_name)
                except Exception as e:
                    self._logger.error(f"Failed to destroy {component_name}: {e}")
            
            # Clear all instances
            self._instances.clear()
            self._scoped_instances.clear()
            self._lifecycle_phases.clear()
            
            self._logger.info("Container shutdown completed")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get container performance metrics."""
        with self._lock:
            return {
                'total_components': len(self._components),
                'total_instances': len(self._instances),
                'cache_hits': self._metrics['cache_hits'],
                'cache_misses': self._metrics['cache_misses'],
                'initialization_time': self._metrics['initialization_time'],
                'memory_usage': self._calculate_memory_usage(),
                'scopes': {
                    scope.value: len([c for c in self._components.values() if c.scope == scope])
                    for scope in Scope
                }
            }
    
    async def _get_or_create_singleton(self, component_name: str, metadata: ComponentMetadata) -> Any:
        """Get or create a singleton instance."""
        if component_name in self._instances:
            return self._instances[component_name]
        
        instance = await self._create_instance(component_name, metadata)
        self._instances[component_name] = instance
        self._metrics['total_instances'] += 1
        self._metrics['cache_misses'] += 1
        
        return instance
    
    async def _create_prototype(self, component_name: str, metadata: ComponentMetadata) -> Any:
        """Create a new prototype instance."""
        instance = await self._create_instance(component_name, metadata)
        self._metrics['cache_misses'] += 1
        return instance
    
    async def _get_or_create_scoped(self, component_name: str, metadata: ComponentMetadata, scope_id: str) -> Any:
        """Get or create a scoped instance."""
        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}
        
        if component_name in self._scoped_instances[scope_id]:
            return self._scoped_instances[scope_id][component_name]
        
        instance = await self._create_instance(component_name, metadata)
        self._scoped_instances[scope_id][component_name] = instance
        self._metrics['total_instances'] += 1
        self._metrics['cache_misses'] += 1
        
        return instance
    
    async def _create_instance(self, component_name: str, metadata: ComponentMetadata) -> Any:
        """Create a new component instance."""
        self._lifecycle_phases[component_name] = LifecyclePhase.CONSTRUCTING
        
        try:
            # Use factory if provided
            if metadata.factory:
                if asyncio.iscoroutinefunction(metadata.factory):
                    instance = await metadata.factory()
                else:
                    instance = metadata.factory()
            else:
                # Create instance using constructor
                instance = await self._create_instance_from_constructor(component_name, metadata)
            
            self._lifecycle_phases[component_name] = LifecyclePhase.CONSTRUCTED
            
            # Call lifecycle methods if applicable
            if metadata.lifecycle_aware:
                await self._call_lifecycle_method(instance, 'on_construct')
                await self._call_lifecycle_method(instance, 'on_initialize')
                self._lifecycle_phases[component_name] = LifecyclePhase.INITIALIZED
            
            return instance
            
        except Exception as e:
            self._lifecycle_phases[component_name] = LifecyclePhase.DESTROYED
            raise ComponentInitializationError(f"Failed to create instance of {component_name}: {e}")
    
    async def _create_instance_from_constructor(self, component_name: str, metadata: ComponentMetadata) -> Any:
        """Create instance using constructor with dependency injection."""
        constructor = metadata.implementation_type.__init__
        signature = inspect.signature(constructor)
        
        # Resolve constructor parameters
        kwargs = {}
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                try:
                    resolved_value = await self.resolve(param.annotation)
                    kwargs[param_name] = resolved_value
                except Exception as e:
                    self._logger.warning(f"Failed to resolve parameter {param_name} for {component_name}: {e}")
        
        # Create instance
        instance = metadata.implementation_type(**kwargs)
        return instance
    
    async def _initialize_component(self, component_name: str) -> None:
        """Initialize a specific component."""
        if component_name not in self._components:
            return
        
        metadata = self._components[component_name]
        
        # Resolve dependencies first
        for dependency in metadata.dependencies:
            if dependency in self._components:
                await self._initialize_component(dependency)
        
        # Create instance if not exists
        if component_name not in self._instances:
            await self._get_or_create_singleton(component_name, metadata)
        
        # Call lifecycle methods
        if metadata.lifecycle_aware and component_name in self._instances:
            instance = self._instances[component_name]
            await self._call_lifecycle_method(instance, 'on_start')
            self._lifecycle_phases[component_name] = LifecyclePhase.STARTED
    
    async def _destroy_component(self, component_name: str) -> None:
        """Destroy a specific component."""
        if component_name not in self._components:
            return
        
        metadata = self._components[component_name]
        
        # Call lifecycle methods
        if metadata.lifecycle_aware and component_name in self._instances:
            instance = self._instances[component_name]
            self._lifecycle_phases[component_name] = LifecyclePhase.STOPPING
            await self._call_lifecycle_method(instance, 'on_stop')
            await self._call_lifecycle_method(instance, 'on_destroy')
            self._lifecycle_phases[component_name] = LifecyclePhase.DESTROYED
        
        # Remove instance
        if component_name in self._instances:
            del self._instances[component_name]
    
    async def _call_lifecycle_method(self, instance: Any, method_name: str) -> None:
        """Call a lifecycle method on an instance."""
        if hasattr(instance, method_name):
            method = getattr(instance, method_name)
            if asyncio.iscoroutinefunction(method):
                await method()
            else:
                method()
    
    def _analyze_dependencies(self, component_type: Type) -> List[str]:
        """Analyze dependencies of a component type."""
        dependencies = []
        
        # Check constructor parameters
        if hasattr(component_type, '__init__'):
            signature = inspect.signature(component_type.__init__)
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue
                
                if param.annotation != inspect.Parameter.empty:
                    if hasattr(param.annotation, '__name__'):
                        dependencies.append(param.annotation.__name__)
        
        return dependencies
    
    def _has_async_init(self, component_type: Type) -> bool:
        """Check if component has async initialization."""
        if hasattr(component_type, '__init__'):
            return asyncio.iscoroutinefunction(component_type.__init__)
        return False
    
    def _has_circular_dependency(self, component_name: str, visited: Optional[List[str]] = None) -> bool:
        """Check for circular dependencies using DFS."""
        if visited is None:
            visited = []
        
        if component_name in visited:
            return True
        
        if component_name not in self._dependency_graph:
            return False
        
        visited.append(component_name)
        
        for dependency in self._dependency_graph[component_name]:
            if self._has_circular_dependency(dependency, visited.copy()):
                return True
        
        return False
    
    def _topological_sort(self) -> List[str]:
        """Sort components by dependencies using topological sort."""
        # Kahn's algorithm
        in_degree = {component: 0 for component in self._components}
        
        # Calculate in-degrees
        for component, dependencies in self._dependency_graph.items():
            for dependency in dependencies:
                if dependency in in_degree:
                    in_degree[dependency] += 1
        
        # Find components with no dependencies
        queue = [component for component, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort by priority
            queue.sort(key=lambda x: self._components[x].priority, reverse=True)
            component = queue.pop(0)
            result.append(component)
            
            # Reduce in-degree of dependencies
            for dependency in self._dependency_graph.get(component, []):
                if dependency in in_degree:
                    in_degree[dependency] -= 1
                    if in_degree[dependency] == 0:
                        queue.append(dependency)
        
        return result
    
    def _calculate_memory_usage(self) -> int:
        """Calculate approximate memory usage of container."""
        # This is a simplified calculation
        return len(self._instances) * 1024  # 1KB per instance estimate


# Global container instance
container = AdvancedIoCContainer()


# Decorators for easy registration
def singleton(component_type: Type[T], tags: Optional[List[str]] = None, priority: int = 0):
    """Decorator to register a singleton component."""
    def decorator(cls):
        container.register_singleton(component_type, cls, tags=tags, priority=priority)
        return cls
    return decorator


def prototype(component_type: Type[T], tags: Optional[List[str]] = None, priority: int = 0):
    """Decorator to register a prototype component."""
    def decorator(cls):
        container.register_prototype(component_type, cls, tags=tags, priority=priority)
        return cls
    return decorator


def inject(component_type: Type[T]):
    """Decorator to inject a dependency."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            instance = await container.resolve(component_type)
            return await func(instance, *args, **kwargs)
        return wrapper
    return decorator 