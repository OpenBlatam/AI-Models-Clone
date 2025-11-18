"""
Comprehensive Unit Tests for Cache Manager

Tests cover cache management functionality with diverse test cases
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.cache_manager import CacheManager, get_cache_manager


class TestCacheManager:
    """Test cases for CacheManager class"""
    
    def test_cache_manager_init_default(self):
        """Test initializing cache manager with default directory"""
        with patch('core.cache_manager.Path.mkdir'):
            manager = CacheManager()
            assert manager is not None
            assert manager.cache is not None
    
    def test_cache_manager_init_custom_dir(self, temp_dir):
        """Test initializing cache manager with custom directory"""
        cache_dir = str(temp_dir / "custom_cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        assert manager is not None
        assert Path(cache_dir).exists()
    
    def test_cache_manager_generate_key_basic(self):
        """Test generating cache key"""
        with patch('core.cache_manager.Path.mkdir'):
            manager = CacheManager()
            key = manager._generate_key("test prompt")
            
            assert isinstance(key, str)
            assert len(key) == 64  # SHA256 produces 64 char hex
    
    def test_cache_manager_generate_key_with_params(self):
        """Test generating cache key with parameters"""
        with patch('core.cache_manager.Path.mkdir'):
            manager = CacheManager()
            key1 = manager._generate_key("test", duration=30, genre="rock")
            key2 = manager._generate_key("test", duration=30, genre="pop")
            
            # Different parameters should produce different keys
            assert key1 != key2
    
    def test_cache_manager_generate_key_deterministic(self):
        """Test that same parameters produce same key"""
        with patch('core.cache_manager.Path.mkdir'):
            manager = CacheManager()
            key1 = manager._generate_key("test", duration=30)
            key2 = manager._generate_key("test", duration=30)
            
            assert key1 == key2
    
    def test_cache_manager_set_and_get(self, temp_dir):
        """Test setting and getting from cache"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        result_data = {"audio": "data", "metadata": {"duration": 30}}
        manager.set("test prompt", result_data, duration=30)
        
        cached = manager.get("test prompt", duration=30)
        assert cached == result_data
    
    def test_cache_manager_get_miss(self, temp_dir):
        """Test getting non-existent key"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        result = manager.get("nonexistent prompt")
        assert result is None
    
    def test_cache_manager_set_with_ttl(self, temp_dir):
        """Test setting cache with TTL"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        manager.set("test", "value", ttl=1)
        result = manager.get("test")
        assert result == "value"
    
    def test_cache_manager_clear(self, temp_dir):
        """Test clearing cache"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        manager.set("test1", "value1")
        manager.set("test2", "value2")
        manager.clear()
        
        assert manager.get("test1") is None
        assert manager.get("test2") is None
    
    def test_cache_manager_stats(self, temp_dir):
        """Test getting cache statistics"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        manager.set("test1", "value1")
        manager.set("test2", "value2")
        
        stats = manager.stats()
        assert isinstance(stats, dict)
        assert "size" in stats
    
    def test_cache_manager_error_handling_get(self, temp_dir):
        """Test error handling in get method"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        # Should not raise, should return None on error
        with patch.object(manager.cache, 'get', side_effect=Exception("Cache error")):
            result = manager.get("test")
            assert result is None
    
    def test_cache_manager_error_handling_set(self, temp_dir):
        """Test error handling in set method"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        # Should not raise on error
        with patch.object(manager.cache, 'set', side_effect=Exception("Cache error")):
            manager.set("test", "value")
            # Should complete without raising
    
    def test_cache_manager_complex_data(self, temp_dir):
        """Test caching complex data structures"""
        cache_dir = str(temp_dir / "cache")
        manager = CacheManager(cache_dir=cache_dir)
        
        complex_data = {
            "audio": [1, 2, 3, 4, 5],
            "metadata": {
                "genre": "rock",
                "duration": 30,
                "instruments": ["guitar", "drums"]
            }
        }
        
        manager.set("complex", complex_data)
        cached = manager.get("complex")
        
        assert cached == complex_data
        assert cached["metadata"]["genre"] == "rock"


class TestGetCacheManager:
    """Test cases for get_cache_manager function"""
    
    def test_get_cache_manager_singleton(self):
        """Test that get_cache_manager returns singleton"""
        with patch('core.cache_manager.Path.mkdir'):
            manager1 = get_cache_manager()
            manager2 = get_cache_manager()
            
            assert manager1 is manager2
            assert isinstance(manager1, CacheManager)
    
    def test_get_cache_manager_multiple_calls(self):
        """Test multiple calls return same instance"""
        with patch('core.cache_manager.Path.mkdir'):
            managers = [get_cache_manager() for _ in range(5)]
            assert all(m is managers[0] for m in managers)










