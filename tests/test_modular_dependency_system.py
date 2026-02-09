"""
Tests for the modular dependency management system.
Tests the new modular architecture with separated concerns.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from core.dependency_manager_modular import (
    DependencyManager, get_dependency_manager, register_service,
    get_service, has_service, start_all_services, stop_all_services
)
from core.dependency_structures import ServiceStatus, ServicePriority, ServiceInfo
from core.service_lifecycle import ServiceLifecycle, LifecycleManager
from core.dependency_resolver import DependencyResolver
from core.health_monitor import HealthMonitor


# ============================================================================
# MODULE: Core Components Testing
# ============================================================================

class TestDependencyStructures:
    """Test the core data structures"""
    
    def test_service_status_enum(self):
        """Test ServiceStatus enum values"""
        assert ServiceStatus.UNKNOWN.value == "unknown"
        assert ServiceStatus.RUNNING.value == "running"
        assert ServiceStatus.ERROR.value == "error"
    
    def test_service_priority_enum(self):
        """Test ServicePriority enum values"""
        assert ServicePriority.CRITICAL.value == 0
        assert ServicePriority.HIGH.value == 1
        assert ServicePriority.NORMAL.value == 2
        assert ServicePriority.LOW.value == 3
    
    def test_service_info_creation(self):
        """Test ServiceInfo creation"""
        info = ServiceInfo(
            name="test-service",
            service_type="test",
            priority=ServicePriority.NORMAL,
            status=ServiceStatus.STOPPED
        )
        assert info.name == "test-service"
        assert info.service_type == "test"
        assert info.priority == ServicePriority.NORMAL
        assert info.status == ServiceStatus.STOPPED


class TestServiceLifecycle:
    """Test the service lifecycle management"""
    
    def test_service_lifecycle_initialization(self):
        """Test ServiceLifecycle initialization"""
        lifecycle = ServiceLifecycle("test", "test_type")
        assert lifecycle.name == "test"
        assert lifecycle.service_type == "test_type"
        assert lifecycle.status == ServiceStatus.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_service_start_stop(self):
        """Test service start and stop"""
        lifecycle = ServiceLifecycle("test", "test_type")
        
        # Start service
        await lifecycle.start()
        assert lifecycle.status == ServiceStatus.RUNNING
        assert lifecycle.start_time is not None
        
        # Stop service
        await lifecycle.stop()
        assert lifecycle.status == ServiceStatus.STOPPED
        assert lifecycle.stop_time is not None


class TestDependencyResolver:
    """Test the dependency resolution system"""
    
    def test_dependency_resolver_initialization(self):
        """Test DependencyResolver initialization"""
        resolver = DependencyResolver()
        assert len(resolver.dependency_graph) == 0
        assert len(resolver.reverse_dependencies) == 0
    
    def test_add_remove_dependency(self):
        """Test adding and removing dependencies"""
        resolver = DependencyResolver()
        
        # Add dependency
        resolver.add_dependency("service_a", "service_b")
        assert "service_b" in resolver.get_dependencies("service_a")
        assert "service_a" in resolver.get_dependents("service_b")
        
        # Remove dependency
        resolver.remove_dependency("service_a", "service_b")
        assert "service_b" not in resolver.get_dependencies("service_a")
        assert "service_a" not in resolver.get_dependents("service_b")
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        resolver = DependencyResolver()
        
        # Create circular dependency: A -> B -> C -> A
        resolver.add_dependency("service_a", "service_b")
        resolver.add_dependency("service_b", "service_c")
        resolver.add_dependency("service_c", "service_a")
        
        cycles = resolver.check_circular_dependencies()
        assert len(cycles) > 0
        assert any("service_a" in cycle for cycle in cycles)


class TestHealthMonitor:
    """Test the health monitoring system"""
    
    def test_health_monitor_initialization(self):
        """Test HealthMonitor initialization"""
        monitor = HealthMonitor()
        assert len(monitor.health_checks) == 0
        assert len(monitor.service_health) == 0
        assert len(monitor.alerts) == 0
    
    def test_add_health_check(self):
        """Test adding health checks"""
        monitor = HealthMonitor()
        
        def mock_check(service_name: str) -> bool:
            return True
        
        monitor.add_health_check("test_service", "basic", mock_check, 30.0, 10.0)
        
        assert "test_service" in monitor.health_checks
        assert len(monitor.health_checks["test_service"]) == 1
        
        check = monitor.health_checks["test_service"][0]
        assert check.service_name == "test_service"
        assert check.check_type == "basic"
        assert check.interval == 30.0
        assert check.timeout == 10.0


# ============================================================================
# MODULE: Integration Testing
# ============================================================================

class TestDependencyManagerIntegration:
    """Test the integrated dependency management system"""
    
    @pytest.fixture
    def dependency_manager(self):
        """Create a DependencyManager instance"""
        return DependencyManager()
    
    def test_dependency_manager_initialization(self, dependency_manager):
        """Test DependencyManager initialization"""
        assert isinstance(dependency_manager.lifecycle_manager, LifecycleManager)
        assert isinstance(dependency_manager.dependency_resolver, DependencyResolver)
        assert isinstance(dependency_manager.health_monitor, HealthMonitor)
        assert len(dependency_manager.service_factories) == 0
        assert len(dependency_manager.service_instances) == 0
        assert dependency_manager.is_running is False
    
    def test_register_service(self, dependency_manager):
        """Test service registration"""
        factory = Mock(return_value="test_instance")
        
        dependency_manager.register_service(
            "test_service",
            "test_type",
            factory,
            ServicePriority.HIGH,
            ["dep1", "dep2"]
        )
        
        assert "test_service" in dependency_manager.service_factories
        assert dependency_manager.service_factories["test_service"] == factory
        
        # Check lifecycle manager
        lifecycle = dependency_manager.lifecycle_manager.get_service("test_service")
        assert lifecycle is not None
        assert lifecycle.name == "test_service"
        assert lifecycle.service_type == "test_type"
        assert lifecycle.priority == ServicePriority.HIGH
        assert "dep1" in lifecycle.dependencies
        assert "dep2" in lifecycle.dependencies
        
        # Check dependency resolver
        deps = dependency_manager.dependency_resolver.get_dependencies("test_service")
        assert "dep1" in deps
        assert "dep2" in deps
        
        # Check health monitor
        health = dependency_manager.health_monitor.get_service_health("test_service")
        assert health is not None
        assert health.service_name == "test_service"
        assert health.status == ServiceStatus.UNKNOWN
    
    def test_unregister_service(self, dependency_manager):
        """Test service unregistration"""
        factory = Mock(return_value="test_instance")
        dependency_manager.register_service("test_service", "test_type", factory)
        
        dependency_manager.unregister_service("test_service")
        
        assert "test_service" not in dependency_manager.service_factories
        assert dependency_manager.lifecycle_manager.get_service("test_service") is None
        assert dependency_manager.health_monitor.get_service_health("test_service") is None
    
    def test_get_service_status(self, dependency_manager):
        """Test getting service status"""
        factory = Mock(return_value="test_instance")
        dependency_manager.register_service("test_service", "test_type", factory)
        
        status = dependency_manager.get_service_status("test_service")
        assert status == ServiceStatus.UNKNOWN
        
        # Test non-existent service
        status = dependency_manager.get_service_status("non_existent")
        assert status is None
    
    def test_get_service_info(self, dependency_manager):
        """Test getting service information"""
        factory = Mock(return_value="test_instance")
        dependency_manager.register_service("test_service", "test_type", factory)
        
        info = dependency_manager.get_service_info("test_service")
        assert isinstance(info, ServiceInfo)
        assert info.name == "test_service"
        assert info.service_type == "test_type"
    
    def test_get_startup_order(self, dependency_manager):
        """Test startup order calculation"""
        # Register services with dependencies
        dependency_manager.register_service("dep1", "type1", Mock())
        dependency_manager.register_service("dep2", "type2", Mock(), dependencies=["dep1"])
        dependency_manager.register_service("main", "type3", Mock(), dependencies=["dep2"])
        
        startup_order = dependency_manager.get_startup_order()
        
        # Check that dependencies come before dependents
        assert startup_order.index("dep1") < startup_order.index("dep2")
        assert startup_order.index("dep2") < startup_order.index("main")
    
    @pytest.mark.asyncio
    async def test_start_all_services(self, dependency_manager):
        """Test starting all services"""
        factory1 = Mock(return_value="instance1")
        factory2 = Mock(return_value="instance2")
        
        dependency_manager.register_service("service1", "type1", factory1)
        dependency_manager.register_service("service2", "type2", factory2)
        
        await dependency_manager.start_all_services()
        
        assert dependency_manager.is_running is True
        assert dependency_manager.service_instances["service1"] == "instance1"
        assert dependency_manager.service_instances["service2"] == "instance2"
        
        # Check lifecycle status
        service1 = dependency_manager.lifecycle_manager.get_service("service1")
        service2 = dependency_manager.lifecycle_manager.get_service("service2")
        assert service1.status == ServiceStatus.RUNNING
        assert service2.status == ServiceStatus.RUNNING
        
        # Check health status
        health1 = dependency_manager.health_monitor.get_service_health("service1")
        health2 = dependency_manager.health_monitor.get_service_health("service2")
        assert health1.status == ServiceStatus.RUNNING
        assert health2.status == ServiceStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_stop_all_services(self, dependency_manager):
        """Test stopping all services"""
        factory = Mock(return_value="instance")
        dependency_manager.register_service("service1", "type1", factory)
        
        await dependency_manager.start_all_services()
        assert dependency_manager.is_running is True
        
        await dependency_manager.stop_all_services()
        
        assert dependency_manager.is_running is False
        assert len(dependency_manager.service_instances) == 0
        
        # Check lifecycle status
        service1 = dependency_manager.lifecycle_manager.get_service("service1")
        assert service1.status == ServiceStatus.STOPPED
        
        # Check health status
        health1 = dependency_manager.health_monitor.get_service_health("service1")
        assert health1.status == ServiceStatus.STOPPED
    
    def test_get_health_summary(self, dependency_manager):
        """Test health summary generation"""
        factory = Mock(return_value="instance")
        dependency_manager.register_service("service1", "type1", factory)
        dependency_manager.register_service("service2", "type2", factory)
        
        # Set different statuses
        service1 = dependency_manager.lifecycle_manager.get_service("service1")
        service2 = dependency_manager.lifecycle_manager.get_service("service2")
        service1.status = ServiceStatus.RUNNING
        service2.status = ServiceStatus.ERROR
        
        health = dependency_manager.get_health_summary()
        
        assert health["total_services"] == 2
        assert health["running_services"] == 1
        assert health["error_services"] == 1
        assert "timestamp" in health
        assert "dependency_health" in health


# ============================================================================
# MODULE: Global Functions Testing
# ============================================================================

class TestGlobalFunctions:
    """Test global convenience functions"""
    
    def test_get_dependency_manager(self):
        """Test get_dependency_manager function"""
        manager = get_dependency_manager()
        assert isinstance(manager, DependencyManager)
    
    def test_register_service(self):
        """Test register_service function"""
        factory = Mock(return_value="test_instance")
        register_service("test", "type", factory, ServicePriority.HIGH, ["dep1"])
        
        manager = get_dependency_manager()
        assert manager.has_service("test")
    
    def test_get_service(self):
        """Test get_service function"""
        factory = Mock(return_value="test_instance")
        register_service("test", "type", factory)
        
        service = get_service("test")
        assert service == "test_instance"
    
    def test_has_service(self):
        """Test has_service function"""
        factory = Mock(return_value="test_instance")
        register_service("test", "type", factory)
        
        exists = has_service("test")
        assert exists is True
        
        exists = has_service("non_existent")
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_start_stop_all_services(self):
        """Test start_all_services and stop_all_services functions"""
        factory = Mock(return_value="test_instance")
        register_service("test", "type", factory)
        
        # Start services
        await start_all_services()
        
        manager = get_dependency_manager()
        assert manager.is_running is True
        
        # Stop services
        await stop_all_services()
        
        assert manager.is_running is False


# ============================================================================
# MODULE: Error Handling Testing
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def dependency_manager(self):
        """Create a DependencyManager instance for error testing"""
        return DependencyManager()
    
    def test_circular_dependency_detection(self, dependency_manager):
        """Test that circular dependencies are detected"""
        dependency_manager.register_service("service_a", "type", Mock(), dependencies=["service_b"])
        dependency_manager.register_service("service_b", "type", Mock(), dependencies=["service_a"])
        
        with pytest.raises(ValueError, match="Circular dependency detected"):
            dependency_manager.get_startup_order()
    
    @pytest.mark.asyncio
    async def test_service_start_failure_handling(self, dependency_manager):
        """Test handling of service start failures"""
        def failing_factory():
            raise Exception("Factory failed")
        
        dependency_manager.register_service("failing_service", "type", failing_factory)
        
        with pytest.raises(Exception, match="Factory failed"):
            await dependency_manager.start_all_services()
        
        # Service should be in error state
        health = dependency_manager.health_monitor.get_service_health("failing_service")
        assert health.status == ServiceStatus.ERROR


# ============================================================================
# MODULE: Performance Testing
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.fixture
    def large_dependency_manager(self):
        """Create a DependencyManager with many services"""
        dm = DependencyManager()
        
        # Register 50 services with simple dependencies
        for i in range(50):
            deps = [f"service_{j}" for j in range(max(0, i-3), i)]
            dm.register_service(f"service_{i}", "type", lambda: f"instance_{i}", dependencies=deps)
        
        return dm
    
    def test_large_service_registration(self, large_dependency_manager):
        """Test registration of many services"""
        assert len(large_dependency_manager.service_factories) == 50
        assert len(large_dependency_manager.lifecycle_manager.services) == 50
    
    def test_startup_order_calculation_performance(self, large_dependency_manager):
        """Test startup order calculation performance"""
        import time
        
        start_time = time.time()
        startup_order = large_dependency_manager.get_startup_order()
        end_time = time.time()
        
        # Should complete in reasonable time (< 0.1 seconds)
        assert end_time - start_time < 0.1
        assert len(startup_order) == 50
    
    def test_health_summary_performance(self, large_dependency_manager):
        """Test health summary generation performance"""
        import time
        
        start_time = time.time()
        health = large_dependency_manager.get_health_summary()
        end_time = time.time()
        
        # Should complete in reasonable time (< 0.05 seconds)
        assert end_time - start_time < 0.05
        assert health["total_services"] == 50
