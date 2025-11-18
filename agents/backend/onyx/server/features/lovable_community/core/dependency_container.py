"""
Dependency Container

Centralized dependency injection container following Inversion of Control principles.
"""

from typing import Optional, Dict, Any, Callable, TypeVar
from sqlalchemy.orm import Session

T = TypeVar('T')


class DependencyContainer:
    """
    Dependency injection container.
    
    Manages lifecycle and dependencies of application components.
    Follows Singleton pattern for container instance.
    """
    
    _instance: Optional['DependencyContainer'] = None
    _factories: Dict[str, Callable[[], Any]] = {}
    _singletons: Dict[str, Any] = {}
    _db_session: Optional[Session] = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory function for creating instances.
        
        Args:
            name: Dependency name
            factory: Factory function
        """
        self._factories[name] = factory
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton instance.
        
        Args:
            name: Dependency name
            instance: Singleton instance
        """
        self._singletons[name] = instance
    
    def get(self, name: str) -> Any:
        """
        Get dependency by name.
        
        Args:
            name: Dependency name
            
        Returns:
            Dependency instance
            
        Raises:
            KeyError: If dependency not found
        """
        if name in self._singletons:
            return self._singletons[name]
        
        if name in self._factories:
            instance = self._factories[name]()
            if name.endswith('_singleton'):
                self._singletons[name] = instance
            return instance
        
        raise KeyError(f"Dependency '{name}' not found")
    
    def set_db_session(self, session: Session) -> None:
        """Set database session."""
        self._db_session = session
    
    def get_db_session(self) -> Optional[Session]:
        """Get database session."""
        return self._db_session
    
    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._factories.clear()
        self._singletons.clear()
        self._db_session = None


container = DependencyContainer()






