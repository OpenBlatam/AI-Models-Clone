"""
Comprehensive Unit Tests for Dependency Injection

Tests cover dependency injection container with diverse test cases
"""

import pytest
from unittest.mock import Mock

from core.dependency_injection import DependencyContainer, get_container


class TestDependencyContainer:
    """Test cases for DependencyContainer class"""
    
    def test_dependency_container_init(self):
        """Test initializing dependency container"""
        container = DependencyContainer()
        assert len(container._services) == 0
        assert len(container._factories) == 0
        assert len(container._singletons) == 0
    
    def test_register_service_singleton(self):
        """Test registering service as singleton"""
        container = DependencyContainer()
        service = Mock()
        
        container.register("test_service", service, singleton=True)
        
        assert "test_service" in container._singletons
        assert container._singletons["test_service"] == service
    
    def test_register_service_non_singleton(self):
        """Test registering service as non-singleton"""
        container = DependencyContainer()
        service = Mock()
        
        container.register("test_service", service, singleton=False)
        
        assert "test_service" in container._services
        assert container._services["test_service"] == service
    
    def test_register_factory(self):
        """Test registering a factory"""
        container = DependencyContainer()
        factory = Mock(return_value=Mock())
        
        container.register_factory("test_service", factory)
        
        assert "test_service" in container._factories
        assert container._factories["test_service"] == factory
    
    def test_get_singleton_service(self):
        """Test getting singleton service"""
        container = DependencyContainer()
        service = Mock()
        
        container.register("test_service", service, singleton=True)
        
        result = container.get("test_service")
        assert result == service
    
    def test_get_non_singleton_service(self):
        """Test getting non-singleton service"""
        container = DependencyContainer()
        service = Mock()
        
        container.register("test_service", service, singleton=False)
        
        result = container.get("test_service")
        assert result == service
    
    def test_get_service_from_factory(self):
        """Test getting service from factory"""
        container = DependencyContainer()
        mock_service = Mock()
        factory = Mock(return_value=mock_service)
        
        container.register_factory("test_service", factory)
        
        result = container.get("test_service")
        
        assert result == mock_service
        factory.assert_called_once()
    
    def test_get_service_from_factory_cached(self):
        """Test factory-created service is cached"""
        container = DependencyContainer()
        mock_service = Mock()
        factory = Mock(return_value=mock_service)
        
        container.register_factory("test_service", factory)
        
        result1 = container.get("test_service")
        result2 = container.get("test_service")
        
        assert result1 == result2
        factory.assert_called_once()  # Should only be called once
    
    def test_get_service_not_registered(self):
        """Test getting non-registered service"""
        container = DependencyContainer()
        result = container.get("nonexistent")
        assert result is None
    
    def test_resolve_service_by_type(self):
        """Test resolving service by type"""
        class TestService:
            pass
        
        container = DependencyContainer()
        service = TestService()
        
        container.register("TestService", service)
        
        result = container.resolve(TestService)
        assert result == service
        assert isinstance(result, TestService)
    
    def test_resolve_service_by_type_not_found(self):
        """Test resolving service by type when not found"""
        class TestService:
            pass
        
        container = DependencyContainer()
        result = container.resolve(TestService)
        assert result is None
    
    def test_resolve_service_by_type_in_singletons(self):
        """Test resolving service from singletons"""
        class TestService:
            pass
        
        container = DependencyContainer()
        service = TestService()
        
        container.register("test", service, singleton=True)
        
        result = container.resolve(TestService)
        assert result == service
    
    def test_has_service_exists(self):
        """Test checking if service exists"""
        container = DependencyContainer()
        container.register("test_service", Mock())
        
        assert container.has("test_service") is True
    
    def test_has_service_not_exists(self):
        """Test checking if service doesn't exist"""
        container = DependencyContainer()
        assert container.has("nonexistent") is False
    
    def test_has_service_in_factory(self):
        """Test has returns True for factory-registered service"""
        container = DependencyContainer()
        container.register_factory("test_service", Mock)
        
        assert container.has("test_service") is True
    
    def test_clear_container(self):
        """Test clearing container"""
        container = DependencyContainer()
        container.register("service1", Mock())
        container.register("service2", Mock(), singleton=True)
        container.register_factory("service3", Mock)
        
        container.clear()
        
        assert len(container._services) == 0
        assert len(container._singletons) == 0
        assert len(container._factories) == 0


class TestGetContainer:
    """Test cases for get_container function"""
    
    def test_get_container_singleton(self):
        """Test that get_container returns singleton"""
        container1 = get_container()
        container2 = get_container()
        
        assert container1 is container2
        assert isinstance(container1, DependencyContainer)










