"""
Pytest Configuration and Fixtures
Shared test utilities and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import Mock, AsyncMock

from core.domain.interfaces import (
    IAnalysisRepository,
    IUserRepository,
    IProductRepository,
    IImageProcessor,
    IAnalysisService,
    IRecommendationService,
    ICacheService,
    IEventPublisher,
)
from core.service_factory import get_service_factory
from core.plugin_system import get_plugin_registry


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_analysis_repository() -> IAnalysisRepository:
    """Mock analysis repository"""
    repo = Mock(spec=IAnalysisRepository)
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_user = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=True)
    return repo


@pytest.fixture
async def mock_user_repository() -> IUserRepository:
    """Mock user repository"""
    repo = Mock(spec=IUserRepository)
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
async def mock_image_processor() -> IImageProcessor:
    """Mock image processor"""
    processor = Mock(spec=IImageProcessor)
    processor.process = AsyncMock(return_value={"metrics": {}})
    processor.validate = AsyncMock(return_value=True)
    return processor


@pytest.fixture
async def mock_cache_service() -> ICacheService:
    """Mock cache service"""
    cache = Mock(spec=ICacheService)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    return cache


@pytest.fixture
async def mock_event_publisher() -> IEventPublisher:
    """Mock event publisher"""
    publisher = Mock(spec=IEventPublisher)
    publisher.publish = AsyncMock(return_value=True)
    return publisher


@pytest.fixture
async def service_factory():
    """Service factory for testing"""
    factory = get_service_factory()
    yield factory
    factory.clear_request_scope()


@pytest.fixture
async def plugin_registry():
    """Plugin registry for testing"""
    registry = get_plugin_registry()
    yield registry
    await registry.shutdown_all()


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing"""
    from core.domain.entities import Analysis, SkinMetrics, Condition, AnalysisStatus, SkinType
    
    metrics = SkinMetrics(
        overall_score=75.0,
        texture_score=80.0,
        hydration_score=70.0,
        elasticity_score=75.0,
        pigmentation_score=80.0,
        pore_size_score=70.0,
        wrinkles_score=75.0,
        redness_score=80.0,
        dark_spots_score=75.0,
    )
    
    conditions = [
        Condition(
            name="acne",
            confidence=0.65,
            severity="moderate",
            description="Mild acne detected"
        )
    ]
    
    return {
        "id": "test-analysis-123",
        "user_id": "test-user-123",
        "metrics": metrics,
        "conditions": conditions,
        "skin_type": SkinType.COMBINATION,
        "status": AnalysisStatus.COMPLETED,
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    from core.domain.entities import User, SkinType
    
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "skin_type": SkinType.COMBINATION,
        "preferences": {},
    }










