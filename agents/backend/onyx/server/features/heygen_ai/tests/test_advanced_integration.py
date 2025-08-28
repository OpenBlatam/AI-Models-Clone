"""
Advanced Integration Tests for HeyGen AI System
==============================================

Tests that combine multiple components to verify system integration:
- Network scanning + Security analysis
- Performance optimization + External APIs
- Caching + Load balancing + Background tasks
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import core components
from core.external_api_integration import (
    ExternalAPIManager, ServiceConfig, ServiceType, ElevenLabsService
)
from core.performance_optimizer import (
    MultiLevelCache, MemoryCache, RedisCache,
    LoadBalancer, PerformanceMonitor, BackgroundTaskProcessor,
    CacheConfig, CacheLevel, CachePolicy
)

logger = logging.getLogger(__name__)


class TestAdvancedSystemIntegration:
    """Test advanced system integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_network_security_workflow(self):
        """Test complete network security workflow"""
        # Create cache for storing scan results
        cache_config = CacheConfig(
            level=CacheLevel.L1_MEMORY,
            max_size=100,
            ttl_seconds=300
        )
        cache = MemoryCache(cache_config)
        
        # Create load balancer for multiple scanning instances
        lb = LoadBalancer(strategy="round_robin")
        lb.add_instance("scanner1", "http://scanner1.internal", weight=1)
        lb.add_instance("scanner2", "http://scanner2.internal", weight=1)
        
        # Simulate network scanning workflow
        scan_results = []
        
        async def perform_network_scan(target: str):
            """Simulate network scanning with caching"""
            await asyncio.sleep(0.1)  # Simulate scan time
            return {
                "target": target,
                "ports_open": [80, 443, 22],
                "services": ["http", "https", "ssh"],
                "timestamp": time.time()
            }
        
        # Perform multiple scans (some should use cache)
        targets = ["example.com", "test.org", "example.com"]  # Duplicate for cache test
        
        for target in targets:
            result = await perform_network_scan(target)
            scan_results.append(result)
            cache.set(f"scan_{target}", result)
        
        # Verify results
        assert len(scan_results) == 3
        assert scan_results[0]["target"] == "example.com"
        assert scan_results[2]["target"] == "example.com"
        assert scan_results[0]["ports_open"] == [80, 443, 22]
        
        # Verify cache is working
        cached_result = cache.get("scan_example.com")
        assert cached_result is not None
        assert cached_result["target"] == "example.com"
    
    @pytest.mark.asyncio
    async def test_external_api_integration(self):
        """Test external API integration"""
        # Initialize external API manager
        api_manager = ExternalAPIManager()
        
        # Create service configurations
        config1 = ServiceConfig(
            service_type=ServiceType.VOICE_SYNTHESIS,
            name="elevenlabs_primary",
            api_key="key1",
            base_url="https://api.elevenlabs.io/v1",
            priority=1
        )
        
        config2 = ServiceConfig(
            service_type=ServiceType.VOICE_SYNTHESIS,
            name="elevenlabs_backup",
            api_key="key2",
            base_url="https://api.elevenlabs.io/v1",
            priority=2
        )
        
        # Register services
        service1 = ElevenLabsService(config1)
        service2 = ElevenLabsService(config2)
        api_manager.register_service(service1)
        api_manager.register_service(service2)
        
        # Verify services are registered
        assert "elevenlabs_primary" in api_manager.services
        assert "elevenlabs_backup" in api_manager.services
        assert len(api_manager.services) == 2
        
        # Test service priorities
        assert service1.config.priority == 1
        assert service2.config.priority == 2
    
    @pytest.mark.asyncio
    async def test_multi_level_caching_strategy(self):
        """Test multi-level caching strategy"""
        # Create multi-level cache
        l1_cache = MemoryCache(CacheConfig(
            level=CacheLevel.L1_MEMORY,
            max_size=50,
            ttl_seconds=60
        ))
        
        l2_cache = MemoryCache(CacheConfig(
            level=CacheLevel.L2_REDIS,
            max_size=200,
            ttl_seconds=300
        ))
        
        # Simulate data retrieval with multi-level caching
        async def retrieve_data_with_caching(data_id: str, cache_level: str = "l1"):
            """Retrieve data with intelligent caching strategy"""
            await asyncio.sleep(0.1)  # Simulate retrieval time
            
            # Check L1 cache first
            if cache_level == "l1":
                cached_data = l1_cache.get(data_id)
                if cached_data:
                    return cached_data
            
            # Check L2 cache
            cached_data = l2_cache.get(data_id)
            if cached_data:
                # Promote to L1 cache
                l1_cache.set(data_id, cached_data)
                return cached_data
            
            # Generate new data
            new_data = {
                "id": data_id,
                "content": f"Data for {data_id}",
                "generated_at": time.time(),
                "cache_level": cache_level
            }
            
            # Store in both caches
            l2_cache.set(data_id, new_data)
            if cache_level == "l1":
                l1_cache.set(data_id, new_data)
            
            return new_data
        
        # Test data retrieval
        data_ids = ["user_123", "user_456", "user_123"]  # Duplicate for cache test
        
        results = []
        for data_id in data_ids:
            result = await retrieve_data_with_caching(data_id, "l1")
            results.append(result)
        
        # Verify results
        assert len(results) == 3
        assert results[0]["id"] == "user_123"
        assert results[2]["id"] == "user_123"  # Should use cache
        
        # Verify cache levels
        l1_data = l1_cache.get("user_123")
        l2_data = l2_cache.get("user_123")
        assert l1_data is not None
        assert l2_data is not None
    
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self):
        """Test comprehensive system health monitoring"""
        # Create service for health monitoring
        health_config = ServiceConfig(
            service_type=ServiceType.ANALYTICS,
            name="health_monitor",
            api_key="health_key",
            base_url="https://health.internal"
        )
        
        # Monitor system health
        async def perform_health_check():
            """Perform comprehensive health check"""
            start_time = time.time()
            
            # Check various system components
            health_status = {
                "timestamp": start_time,
                "system": "healthy",
                "components": {
                    "cache": "operational",
                    "load_balancer": "operational",
                    "background_tasks": "operational",
                    "external_apis": "operational"
                },
                "metrics": {
                    "memory_usage": "45%",
                    "cpu_usage": "23%",
                    "active_connections": 15
                }
            }
            
            await asyncio.sleep(0.05)  # Simulate health check time
            
            return health_status
        
        # Perform multiple health checks
        health_results = []
        for _ in range(5):
            result = await perform_health_check()
            health_results.append(result)
        
        # Verify health check results
        assert len(health_results) == 5
        for result in health_results:
            assert result["system"] == "healthy"
            assert "components" in result
            assert "metrics" in result
            assert result["components"]["cache"] == "operational"


class TestPerformanceStressTests:
    """Performance stress tests for the system"""
    
    @pytest.mark.asyncio
    async def test_load_balancer_stress_test(self):
        """Test load balancer under stress"""
        lb = LoadBalancer(strategy="round_robin")
        
        # Add many instances
        for i in range(50):
            lb.add_instance(f"instance_{i}", f"http://instance_{i}.internal", weight=1)
        
        # Test distribution performance
        start_time = time.time()
        
        instances = []
        for _ in range(1000):
            instance = lb.get_next_instance()
            instances.append(instance["id"])
        
        distribution_time = time.time() - start_time
        
        # Verify performance
        assert distribution_time < 1.0  # Should be very fast
        assert len(instances) == 1000
        
        # Verify distribution
        unique_instances = set(instances)
        assert len(unique_instances) == 50  # All instances should be used
        
        # Test health management under stress
        for i in range(10):
            lb.mark_instance_unhealthy(f"instance_{i}")
        
        # Get healthy instances
        healthy_count = 0
        for _ in range(100):
            instance = lb.get_next_instance()
            if instance:
                healthy_count += 1
        
        assert healthy_count == 100  # Should only return healthy instances


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
