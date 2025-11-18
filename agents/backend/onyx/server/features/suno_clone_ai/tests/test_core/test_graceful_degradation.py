"""
Comprehensive Unit Tests for Graceful Degradation

Tests cover graceful degradation functionality with diverse test cases
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from core.graceful_degradation import (
    GracefulDegradation,
    ServiceStatus,
    DegradationLevel
)


class TestServiceStatus:
    """Test cases for ServiceStatus dataclass"""
    
    def test_service_status_creation(self):
        """Test creating service status"""
        status = ServiceStatus(
            name="test_service",
            available=True,
            response_time=0.1,
            error_rate=0.0
        )
        assert status.name == "test_service"
        assert status.available is True
        assert status.response_time == 0.1
        assert status.degradation_level == DegradationLevel.NONE


class TestGracefulDegradation:
    """Test cases for GracefulDegradation class"""
    
    def test_graceful_degradation_init(self):
        """Test initializing graceful degradation"""
        degradation = GracefulDegradation()
        assert len(degradation._services) == 0
        assert len(degradation._fallbacks) == 0
    
    def test_register_service(self):
        """Test registering a service"""
        degradation = GracefulDegradation()
        health_check = Mock(return_value=True)
        
        degradation.register_service("test_service", health_check)
        
        assert "test_service" in degradation._services
        assert degradation._services["test_service"].name == "test_service"
    
    def test_register_service_with_fallback(self):
        """Test registering service with fallback"""
        degradation = GracefulDegradation()
        health_check = Mock(return_value=True)
        fallback = Mock(return_value="fallback_result")
        
        degradation.register_service("test_service", health_check, fallback=fallback)
        
        assert "test_service" in degradation._fallbacks
        assert degradation._fallbacks["test_service"] == fallback
    
    def test_set_degradation_strategy(self):
        """Test setting degradation strategy"""
        degradation = GracefulDegradation()
        strategy = Mock()
        
        degradation.set_degradation_strategy(
            "test_service",
            DegradationLevel.MINOR,
            strategy
        )
        
        assert "test_service" in degradation._degradation_strategies
        assert degradation._degradation_strategies["test_service"][DegradationLevel.MINOR] == strategy
    
    @pytest.mark.asyncio
    async def test_check_service_available(self):
        """Test checking available service"""
        degradation = GracefulDegradation()
        health_check = AsyncMock(return_value=True)
        
        degradation.register_service("test_service", health_check)
        
        # Mock the health check execution
        status = await degradation.check_service("test_service")
        
        assert isinstance(status, ServiceStatus)
        assert status.name == "test_service"
    
    @pytest.mark.asyncio
    async def test_check_service_not_registered(self):
        """Test checking non-registered service raises error"""
        degradation = GracefulDegradation()
        
        with pytest.raises(ValueError, match="not registered"):
            await degradation.check_service("nonexistent")
    
    def test_get_service_status(self):
        """Test getting service status"""
        degradation = GracefulDegradation()
        health_check = Mock(return_value=True)
        
        degradation.register_service("test_service", health_check)
        
        status = degradation.get_service_status("test_service")
        
        assert status is not None
        assert status.name == "test_service"
    
    def test_get_service_status_not_registered(self):
        """Test getting status for non-registered service"""
        degradation = GracefulDegradation()
        
        status = degradation.get_service_status("nonexistent")
        assert status is None
    
    def test_get_all_services_status(self):
        """Test getting all services status"""
        degradation = GracefulDegradation()
        degradation.register_service("service1", Mock())
        degradation.register_service("service2", Mock())
        
        all_status = degradation.get_all_services_status()
        
        assert len(all_status) == 2
        assert all(s.name in ["service1", "service2"] for s in all_status)
    
    def test_get_degradation_level(self):
        """Test getting degradation level"""
        degradation = GracefulDegradation()
        health_check = Mock(return_value=True)
        
        degradation.register_service("test_service", health_check)
        degradation._services["test_service"].degradation_level = DegradationLevel.MINOR
        
        level = degradation.get_degradation_level("test_service")
        assert level == DegradationLevel.MINOR
    
    def test_get_degradation_level_not_registered(self):
        """Test getting degradation level for non-registered service"""
        degradation = GracefulDegradation()
        
        level = degradation.get_degradation_level("nonexistent")
        assert level is None










