"""
Comprehensive Unit Tests for Connection Pool Manager

Tests cover connection pool management with diverse test cases
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock

from core.connection_pool import ConnectionPoolManager


class TestConnectionPoolManager:
    """Test cases for ConnectionPoolManager class"""
    
    def test_connection_pool_manager_init(self):
        """Test initializing connection pool manager"""
        manager = ConnectionPoolManager()
        assert len(manager._pools) == 0
        assert len(manager._pool_configs) == 0
    
    def test_register_pool(self):
        """Test registering a connection pool"""
        manager = ConnectionPoolManager()
        pool_factory = Mock()
        
        manager.register_pool(
            name="test_pool",
            pool_factory=pool_factory,
            min_size=2,
            max_size=10
        )
        
        assert "test_pool" in manager._pool_configs
        config = manager._pool_configs["test_pool"]
        assert config["min_size"] == 2
        assert config["max_size"] == 10
    
    def test_register_pool_custom_params(self):
        """Test registering pool with custom parameters"""
        manager = ConnectionPoolManager()
        pool_factory = Mock()
        
        manager.register_pool(
            name="custom_pool",
            pool_factory=pool_factory,
            min_size=5,
            max_size=20,
            custom_param="value"
        )
        
        config = manager._pool_configs["custom_pool"]
        assert config["custom_param"] == "value"
    
    @pytest.mark.asyncio
    async def test_get_pool_lazy_init(self):
        """Test lazy initialization of pool"""
        manager = ConnectionPoolManager()
        mock_pool = AsyncMock()
        pool_factory = AsyncMock(return_value=mock_pool)
        
        manager.register_pool(
            name="test_pool",
            pool_factory=pool_factory,
            min_size=2,
            max_size=10
        )
        
        pool = await manager.get_pool("test_pool")
        
        assert pool == mock_pool
        pool_factory.assert_called_once()
        assert "test_pool" in manager._pools
    
    @pytest.mark.asyncio
    async def test_get_pool_not_registered(self):
        """Test getting non-registered pool raises error"""
        manager = ConnectionPoolManager()
        
        with pytest.raises(ValueError, match="not registered"):
            await manager.get_pool("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_pool_reuses_existing(self):
        """Test getting pool reuses existing instance"""
        manager = ConnectionPoolManager()
        mock_pool = AsyncMock()
        pool_factory = AsyncMock(return_value=mock_pool)
        
        manager.register_pool("test_pool", pool_factory, min_size=2, max_size=10)
        
        pool1 = await manager.get_pool("test_pool")
        pool2 = await manager.get_pool("test_pool")
        
        assert pool1 is pool2
        pool_factory.assert_called_once()  # Should only be called once
    
    @pytest.mark.asyncio
    async def test_acquire_with_acquire_method(self):
        """Test acquiring connection from pool with acquire method"""
        manager = ConnectionPoolManager()
        mock_connection = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire = AsyncMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_connection)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
        
        pool_factory = AsyncMock(return_value=mock_pool)
        manager.register_pool("test_pool", pool_factory, min_size=2, max_size=10)
        
        async with manager.acquire("test_pool") as connection:
            assert connection == mock_connection
        
        mock_pool.acquire.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_acquire_without_acquire_method(self):
        """Test acquiring from pool without acquire method"""
        manager = ConnectionPoolManager()
        mock_pool = AsyncMock()
        # Remove acquire method
        del mock_pool.acquire
        
        pool_factory = AsyncMock(return_value=mock_pool)
        manager.register_pool("test_pool", pool_factory, min_size=2, max_size=10)
        
        async with manager.acquire("test_pool") as connection:
            assert connection == mock_pool
    
    @pytest.mark.asyncio
    async def test_close_all(self):
        """Test closing all pools"""
        manager = ConnectionPoolManager()
        mock_pool1 = AsyncMock()
        mock_pool1.close = AsyncMock()
        mock_pool2 = AsyncMock()
        mock_pool2.dispose = AsyncMock()
        
        pool_factory1 = AsyncMock(return_value=mock_pool1)
        pool_factory2 = AsyncMock(return_value=mock_pool2)
        
        manager.register_pool("pool1", pool_factory1, min_size=2, max_size=10)
        manager.register_pool("pool2", pool_factory2, min_size=2, max_size=10)
        
        await manager.get_pool("pool1")
        await manager.get_pool("pool2")
        
        await manager.close_all()
        
        mock_pool1.close.assert_called_once()
        mock_pool2.dispose.assert_called_once()
        assert len(manager._pools) == 0
    
    @pytest.mark.asyncio
    async def test_close_all_handles_errors(self):
        """Test close_all handles errors gracefully"""
        manager = ConnectionPoolManager()
        mock_pool = AsyncMock()
        mock_pool.close = AsyncMock(side_effect=Exception("Close error"))
        
        pool_factory = AsyncMock(return_value=mock_pool)
        manager.register_pool("test_pool", pool_factory, min_size=2, max_size=10)
        
        await manager.get_pool("test_pool")
        
        # Should not raise
        await manager.close_all()
    
    def test_get_pool_stats_not_initialized(self):
        """Test getting stats for non-initialized pool"""
        manager = ConnectionPoolManager()
        manager.register_pool("test_pool", Mock(), min_size=2, max_size=10)
        
        stats = manager.get_pool_stats("test_pool")
        assert "error" in stats
    
    @pytest.mark.asyncio
    async def test_get_pool_stats_initialized(self):
        """Test getting stats for initialized pool"""
        manager = ConnectionPoolManager()
        mock_pool = AsyncMock()
        mock_pool.get_stats = Mock(return_value={"size": 5, "max_size": 10})
        
        pool_factory = AsyncMock(return_value=mock_pool)
        manager.register_pool("test_pool", pool_factory, min_size=2, max_size=10)
        
        await manager.get_pool("test_pool")
        
        stats = manager.get_pool_stats("test_pool")
        assert stats["initialized"] is True
        assert stats["name"] == "test_pool"
    
    @pytest.mark.asyncio
    async def test_multiple_pools_independent(self):
        """Test multiple pools are independent"""
        manager = ConnectionPoolManager()
        
        mock_pool1 = AsyncMock()
        mock_pool2 = AsyncMock()
        
        pool_factory1 = AsyncMock(return_value=mock_pool1)
        pool_factory2 = AsyncMock(return_value=mock_pool2)
        
        manager.register_pool("pool1", pool_factory1, min_size=2, max_size=10)
        manager.register_pool("pool2", pool_factory2, min_size=5, max_size=20)
        
        pool1 = await manager.get_pool("pool1")
        pool2 = await manager.get_pool("pool2")
        
        assert pool1 is not pool2
        assert pool1 == mock_pool1
        assert pool2 == mock_pool2










