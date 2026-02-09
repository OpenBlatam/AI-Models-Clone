"""
🧪 Unit Tests for ADS Optimization System

Tests for the optimization factory, optimizers, and base classes
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

# Import optimization components
from optimization.factory import OptimizationFactory, get_optimization_factory
from optimization.base_optimizer import (
    BaseOptimizer, OptimizationContext, OptimizationStrategy, OptimizationLevel
)
from optimization.performance_optimizer import PerformanceOptimizer
from optimization.profiling_optimizer import ProfilingOptimizer
from optimization.gpu_optimizer import GPUOptimizer


class TestOptimizationContext:
    """Test cases for OptimizationContext."""
    
    def test_context_creation(self):
        """Test optimization context creation."""
        context = OptimizationContext(
            target_entity="ad",
            entity_id="test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD,
            parameters={"test": "value"}
        )
        
        assert context.target_entity == "ad"
        assert context.entity_id == "test-123"
        assert context.optimization_type == OptimizationStrategy.PERFORMANCE
        assert context.level == OptimizationLevel.STANDARD
        assert context.parameters == {"test": "value"}
    
    def test_context_defaults(self):
        """Test optimization context with default values."""
        context = OptimizationContext(
            target_entity="campaign",
            entity_id="campaign-123"
        )
        
        assert context.target_entity == "campaign"
        assert context.entity_id == "campaign-123"
        assert context.optimization_type == OptimizationStrategy.PERFORMANCE
        assert context.level == OptimizationLevel.STANDARD
        assert context.parameters == {}


class TestBaseOptimizer:
    """Test cases for BaseOptimizer."""
    
    def test_base_optimizer_creation(self):
        """Test base optimizer creation."""
        optimizer = BaseOptimizer("Test Optimizer", OptimizationStrategy.PERFORMANCE)
        
        assert optimizer.name == "Test Optimizer"
        assert optimizer.strategy == OptimizationStrategy.PERFORMANCE
        assert optimizer.optimization_history == []
    
    def test_base_optimizer_can_optimize(self):
        """Test base optimizer can_optimize method."""
        optimizer = BaseOptimizer("Test Optimizer", OptimizationStrategy.PERFORMANCE)
        
        # Default implementation should return True
        assert optimizer.can_optimize(Mock()) is True
    
    def test_base_optimizer_get_capabilities(self):
        """Test base optimizer capabilities."""
        optimizer = BaseOptimizer("Test Optimizer", OptimizationStrategy.PERFORMANCE)
        
        capabilities = optimizer.get_optimization_capabilities()
        assert capabilities["name"] == "Test Optimizer"
        assert capabilities["strategy"] == OptimizationStrategy.PERFORMANCE.value


class TestPerformanceOptimizer:
    """Test cases for PerformanceOptimizer."""
    
    def test_performance_optimizer_creation(self):
        """Test performance optimizer creation."""
        optimizer = PerformanceOptimizer("Test Performance Optimizer")
        
        assert optimizer.name == "Test Performance Optimizer"
        assert optimizer.strategy == OptimizationStrategy.PERFORMANCE
        assert len(optimizer.optimization_strategies) == 4  # light, standard, aggressive, extreme
    
    def test_performance_optimizer_can_optimize(self):
        """Test performance optimizer can_optimize method."""
        optimizer = PerformanceOptimizer()
        
        # Test valid context
        context = OptimizationContext(
            target_entity="ad",
            entity_id="test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE
        )
        assert optimizer.can_optimize(context) is True
        
        # Test invalid entity
        context.target_entity = "invalid"
        assert optimizer.can_optimize(context) is False
        
        # Test invalid strategy
        context.target_entity = "ad"
        context.optimization_type = OptimizationStrategy.GPU
        assert optimizer.can_optimize(context) is False
    
    def test_performance_optimizer_capabilities(self):
        """Test performance optimizer capabilities."""
        optimizer = PerformanceOptimizer()
        
        capabilities = optimizer.get_optimization_capabilities()
        assert capabilities["name"] == "Performance Optimizer"
        assert capabilities["strategy"] == OptimizationStrategy.PERFORMANCE.value
        assert "cpu_optimization" in capabilities["optimization_techniques"]
        assert "memory_optimization" in capabilities["optimization_techniques"]
        assert "response_time_optimization" in capabilities["optimization_techniques"]
    
    @pytest.mark.asyncio
    async def test_performance_optimizer_optimize(self):
        """Test performance optimizer optimization execution."""
        optimizer = PerformanceOptimizer()
        
        context = OptimizationContext(
            target_entity="ad",
            entity_id="test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD
        )
        
        result = await optimizer.optimize(context)
        
        assert result is not None
        assert result.strategy == OptimizationStrategy.PERFORMANCE
        assert result.level == OptimizationLevel.STANDARD
        assert result.success is True


class TestProfilingOptimizer:
    """Test cases for ProfilingOptimizer."""
    
    def test_profiling_optimizer_creation(self):
        """Test profiling optimizer creation."""
        optimizer = ProfilingOptimizer("Test Profiling Optimizer")
        
        assert optimizer.name == "Test Profiling Optimizer"
        assert optimizer.strategy == OptimizationStrategy.PERFORMANCE
    
    def test_profiling_optimizer_can_optimize(self):
        """Test profiling optimizer can_optimize method."""
        optimizer = ProfilingOptimizer()
        
        # Should always return True (placeholder implementation)
        context = Mock()
        assert optimizer.can_optimize(context) is True
    
    def test_profiling_optimizer_capabilities(self):
        """Test profiling optimizer capabilities."""
        optimizer = ProfilingOptimizer()
        
        capabilities = optimizer.get_optimization_capabilities()
        assert capabilities["name"] == "Profiling Optimizer"
        assert capabilities["strategy"] == OptimizationStrategy.PERFORMANCE.value
        assert "code_profiling" in capabilities["capabilities"]
        assert "bottleneck_detection" in capabilities["capabilities"]
        assert "performance_analysis" in capabilities["capabilities"]


class TestGPUOptimizer:
    """Test cases for GPUOptimizer."""
    
    def test_gpu_optimizer_creation(self):
        """Test GPU optimizer creation."""
        optimizer = GPUOptimizer("Test GPU Optimizer")
        
        assert optimizer.name == "Test GPU Optimizer"
        assert optimizer.strategy == OptimizationStrategy.GPU
    
    def test_gpu_optimizer_can_optimize(self):
        """Test GPU optimizer can_optimize method."""
        optimizer = GPUOptimizer()
        
        # Should always return True (placeholder implementation)
        context = Mock()
        assert optimizer.can_optimize(context) is True
    
    def test_gpu_optimizer_capabilities(self):
        """Test GPU optimizer capabilities."""
        optimizer = GPUOptimizer()
        
        capabilities = optimizer.get_optimization_capabilities()
        assert capabilities["name"] == "GPU Optimizer"
        assert capabilities["strategy"] == OptimizationStrategy.GPU.value
        assert "gpu_memory_optimization" in capabilities["capabilities"]
        assert "cuda_optimization" in capabilities["capabilities"]
        assert "tensor_optimization" in capabilities["capabilities"]


class TestOptimizationFactory:
    """Test cases for OptimizationFactory."""
    
    def test_factory_creation(self):
        """Test optimization factory creation."""
        factory = OptimizationFactory()
        
        assert factory.registered_optimizers is not None
        assert factory.optimizer_configs is not None
        assert factory.optimizer_instances is not None
    
    def test_factory_default_optimizers(self):
        """Test that default optimizers are registered."""
        factory = OptimizationFactory()
        
        # Check that default optimizers are registered
        assert "performance" in factory.registered_optimizers
        assert "profiling" in factory.registered_optimizers
        assert "gpu" in factory.registered_optimizers
        
        # Check optimizer classes
        assert factory.registered_optimizers["performance"] == PerformanceOptimizer
        assert factory.registered_optimizers["profiling"] == ProfilingOptimizer
        assert factory.registered_optimizers["gpu"] == GPUOptimizer
    
    def test_factory_register_optimizer(self):
        """Test registering a new optimizer."""
        factory = OptimizationFactory()
        
        # Create a mock optimizer
        mock_optimizer = Mock()
        mock_config = {"name": "Mock Optimizer", "capabilities": ["test"]}
        
        # Register the optimizer
        factory.register_optimizer("mock", mock_optimizer, mock_config)
        
        # Verify registration
        assert "mock" in factory.registered_optimizers
        assert factory.registered_optimizers["mock"] == mock_optimizer
        assert factory.optimizer_configs["mock"] == mock_config
    
    def test_factory_create_optimizer(self):
        """Test creating an optimizer instance."""
        factory = OptimizationFactory()
        
        # Create a performance optimizer
        optimizer = factory.create_optimizer("performance")
        
        assert optimizer is not None
        assert isinstance(optimizer, PerformanceOptimizer)
        assert optimizer.name == "Performance Optimizer"
    
    def test_factory_get_or_create_optimizer(self):
        """Test get or create optimizer functionality."""
        factory = OptimizationFactory()
        
        # First call should create new instance
        optimizer1 = factory.get_or_create_optimizer("performance")
        assert optimizer1 is not None
        
        # Second call should return same instance
        optimizer2 = factory.get_or_create_optimizer("performance")
        assert optimizer2 is optimizer1
    
    def test_factory_get_optimal_optimizer(self):
        """Test getting optimal optimizer for context."""
        factory = OptimizationFactory()
        
        context = OptimizationContext(
            target_entity="ad",
            entity_id="test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD
        )
        
        optimal_optimizer = factory.get_optimal_optimizer(context)
        
        assert optimal_optimizer is not None
        assert optimal_optimizer in ["performance", "profiling", "gpu"]
    
    def test_factory_optimization_statistics(self):
        """Test factory optimization statistics."""
        factory = OptimizationFactory()
        
        stats = factory.get_optimization_statistics()
        
        assert "total_optimizers" in stats
        assert "active_instances" in stats
        assert "optimizer_types" in stats
        
        assert stats["total_optimizers"] == 3
        assert "performance" in stats["optimizer_types"]
        assert "profiling" in stats["optimizer_types"]
        assert "gpu" in stats["optimizer_types"]
    
    def test_factory_list_available_optimizers(self):
        """Test listing available optimizers."""
        factory = OptimizationFactory()
        
        optimizers = factory.list_available_optimizers()
        
        assert len(optimizers) == 3
        
        # Check that each optimizer has required info
        for optimizer_info in optimizers:
            assert "type" in optimizer_info
            assert "class_name" in optimizer_info
            assert "config" in optimizer_info
            assert "capabilities" in optimizer_info


class TestOptimizationFactoryIntegration:
    """Integration tests for optimization factory."""
    
    @pytest.mark.asyncio
    async def test_full_optimization_workflow(self):
        """Test complete optimization workflow."""
        factory = get_optimization_factory()
        
        # Create optimization context
        context = OptimizationContext(
            target_entity="ad",
            entity_id="test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD,
            parameters={"test": "value"}
        )
        
        # Get optimal optimizer
        optimal_optimizer_type = factory.get_optimal_optimizer(context)
        assert optimal_optimizer_type is not None
        
        # Execute optimization
        result = await factory.execute_optimization(context, optimal_optimizer_type)
        assert result is not None
        assert result.success is True
    
    def test_factory_singleton_pattern(self):
        """Test that get_optimization_factory returns singleton."""
        factory1 = get_optimization_factory()
        factory2 = get_optimization_factory()
        
        assert factory1 is factory2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

