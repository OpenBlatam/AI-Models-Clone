"""
Redis Tests - Onyx Integration
Tests for Redis integration in Onyx.
"""
import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..redis_utils import RedisUtils
from ..redis_config import RedisConfig, get_config
from ..redis_middleware import RedisMiddleware
from ..redis_decorators import RedisDecorators
from fastapi import FastAPI, Request, Response
from starlette.testclient import TestClient

# Test models
class UserModel(BaseModel):
    """Test user model."""
    id: str
    name: str
    email: str
    created_at: datetime = datetime.utcnow()

class TestRedisUtils:
    """Tests for Redis utilities."""
    
    @pytest.fixture
    def redis_utils(self):
        """Create Redis utilities instance."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            db=15,  # Use a separate database for testing
            default_expire=3600
        )
        return RedisUtils(config)
    
    @pytest.fixture
    def test_data(self):
        """Create test data."""
        return {
            "user_1": UserModel(
                id="1",
                name="John Doe",
                email="john@example.com"
            ),
            "user_2": UserModel(
                id="2",
                name="Jane Smith",
                email="jane@example.com"
            )
        }
    
    def test_cache_data(self, redis_utils, test_data):
        """Test caching data."""
        # Cache data
        redis_utils.cache_data(
            data=test_data["user_1"],
            prefix="test",
            identifier="user_1"
        )
        
        # Get cached data
        cached_data = redis_utils.get_cached_data(
            prefix="test",
            identifier="user_1",
            model_class=UserModel
        )
        
        assert cached_data is not None
        assert cached_data.id == test_data["user_1"].id
        assert cached_data.name == test_data["user_1"].name
        assert cached_data.email == test_data["user_1"].email
    
    def test_cache_batch(self, redis_utils, test_data):
        """Test caching batch data."""
        # Cache batch data
        redis_utils.cache_batch(
            data_dict=test_data,
            prefix="test"
        )
        
        # Get cached batch data
        cached_batch = redis_utils.get_cached_batch(
            prefix="test",
            identifiers=["user_1", "user_2"],
            model_class=UserModel
        )
        
        assert len(cached_batch) == 2
        assert cached_batch["user_1"].id == test_data["user_1"].id
        assert cached_batch["user_2"].id == test_data["user_2"].id
    
    def test_delete_batch(self, redis_utils, test_data):
        """Test deleting batch keys."""
        # Cache batch data
        redis_utils.cache_batch(
            data_dict=test_data,
            prefix="test"
        )
        
        # Delete batch keys
        redis_utils.delete_batch(
            prefix="test",
            identifiers=["user_1", "user_2"]
        )
        
        # Get cached batch data
        cached_batch = redis_utils.get_cached_batch(
            prefix="test",
            identifiers=["user_1", "user_2"]
        )
        
        assert len(cached_batch) == 0
    
    def test_scan_keys(self, redis_utils, test_data):
        """Test scanning keys."""
        # Cache data
        redis_utils.cache_data(
            data=test_data["user_1"],
            prefix="test",
            identifier="user_1"
        )
        
        # Scan keys
        keys = redis_utils.scan_keys(
            prefix="test",
            pattern="user_*"
        )
        
        assert len(keys) == 1
        assert keys[0].endswith("user_1")
    
    def test_get_memory_usage(self, redis_utils):
        """Test getting memory usage."""
        memory_usage = redis_utils.get_memory_usage()
        
        assert isinstance(memory_usage, dict)
        assert "used_memory" in memory_usage
        assert "used_memory_peak" in memory_usage
    
    def test_get_stats(self, redis_utils):
        """Test getting Redis stats."""
        stats = redis_utils.get_stats()
        
        assert isinstance(stats, dict)
        assert "clients" in stats
        assert "memory" in stats
        assert "stats" in stats

class TestRedisMiddleware:
    """Tests for Redis middleware."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app."""
        app = FastAPI()
        
        # Add Redis middleware
        app.add_middleware(
            RedisMiddleware,
            config={
                "cache_ttl": 3600,
                "exclude_paths": ["/admin"],
                "include_paths": ["/api"],
                "cache_headers": True
            }
        )
        
        # Add test routes
        @app.get("/api/test")
        async def test_route():
            return {"message": "test"}
        
        @app.get("/admin/test")
        async def admin_route():
            return {"message": "admin"}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_cached_response(self, client):
        """Test cached response."""
        # First request
        response1 = client.get("/api/test")
        assert response1.status_code == 200
        assert response1.json() == {"message": "test"}
        assert "X-Cache" not in response1.headers
        
        # Second request (should be cached)
        response2 = client.get("/api/test")
        assert response2.status_code == 200
        assert response2.json() == {"message": "test"}
        assert response2.headers["X-Cache"] == "HIT"
    
    def test_excluded_path(self, client):
        """Test excluded path."""
        # First request
        response1 = client.get("/admin/test")
        assert response1.status_code == 200
        assert response1.json() == {"message": "admin"}
        assert "X-Cache" not in response1.headers
        
        # Second request (should not be cached)
        response2 = client.get("/admin/test")
        assert response2.status_code == 200
        assert response2.json() == {"message": "admin"}
        assert "X-Cache" not in response2.headers

class TestRedisDecorators:
    """Tests for Redis decorators."""
    
    @pytest.fixture
    def redis_decorators(self):
        """Create Redis decorators instance."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            db=15,  # Use a separate database for testing
            default_ttl=3600
        )
        return RedisDecorators({"default_ttl": 3600})
    
    @pytest.fixture
    def test_data(self):
        """Create test data."""
        return {
            "user_1": UserModel(
                id="1",
                name="John Doe",
                email="john@example.com"
            ),
            "user_2": UserModel(
                id="2",
                name="Jane Smith",
                email="jane@example.com"
            )
        }
    
    @pytest.mark.asyncio
    async def test_cache_decorator(self, redis_decorators, test_data):
        """Test cache decorator."""
        # Define test function
        @redis_decorators.cache(
            prefix="test",
            ttl=3600
        )
        async def get_user_data(user_id: str) -> Dict[str, Any]:
            return test_data[user_id].model_dump()
        
        # First call
        result1 = await get_user_data("user_1")
        assert result1["id"] == test_data["user_1"].id
        
        # Second call (should be cached)
        result2 = await get_user_data("user_1")
        assert result2["id"] == test_data["user_1"].id
    
    @pytest.mark.asyncio
    async def test_cache_model_decorator(self, redis_decorators, test_data):
        """Test cache model decorator."""
        # Define test function
        @redis_decorators.cache_model(
            prefix="test",
            ttl=3600
        )
        async def get_user_model(user_id: str) -> UserModel:
            return test_data[user_id]
        
        # First call
        result1 = await get_user_model("user_1")
        assert result1.id == test_data["user_1"].id
        
        # Second call (should be cached)
        result2 = await get_user_model("user_1")
        assert result2.id == test_data["user_1"].id
    
    @pytest.mark.asyncio
    async def test_cache_batch_decorator(self, redis_decorators, test_data):
        """Test cache batch decorator."""
        # Define test function
        @redis_decorators.cache_batch(
            prefix="test",
            ttl=3600
        )
        async def get_batch_data(user_ids: List[str]) -> Dict[str, UserModel]:
            return {user_id: test_data[user_id] for user_id in user_ids}
        
        # First call
        result1 = await get_batch_data(["user_1", "user_2"])
        assert len(result1) == 2
        assert result1["user_1"].id == test_data["user_1"].id
        
        # Second call (should be cached)
        result2 = await get_batch_data(["user_1", "user_2"])
        assert len(result2) == 2
        assert result2["user_1"].id == test_data["user_1"].id
    
    @pytest.mark.asyncio
    async def test_invalidate_decorator(self, redis_decorators, test_data):
        """Test invalidate decorator."""
        # Define test functions
        @redis_decorators.cache(
            prefix="test",
            ttl=3600
        )
        async def get_user_data(user_id: str) -> Dict[str, Any]:
            return test_data[user_id].model_dump()
        
        @redis_decorators.invalidate(
            prefix="test"
        )
        async def update_user_data(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
            return data
        
        # Cache data
        result1 = await get_user_data("user_1")
        assert result1["id"] == test_data["user_1"].id
        
        # Invalidate cache
        await update_user_data("user_1", {"id": "1", "name": "Updated"})
        
        # Get fresh data
        result2 = await get_user_data("user_1")
        assert result2["id"] == test_data["user_1"].id 