"""
🧪 Pytest Configuration for ADS System Tests

Configuration file with fixtures and test setup
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Import system components
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import (
    AdStatus, AdType, Platform, Budget, TargetingCriteria, AdSchedule
)
from optimization.factory import get_optimization_factory


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_targeting():
    """Create sample targeting criteria for testing."""
    return TargetingCriteria(
        age_min=25,
        age_max=45,
        genders=["male", "female"],
        locations=["United States", "Canada"],
        interests=["technology", "business", "entrepreneurship"]
    )


@pytest.fixture
def sample_budget():
    """Create sample budget for testing."""
    return Budget(
        amount=Decimal('1000.00'),
        currency="USD",
        daily_limit=Decimal('100.00'),
        lifetime_limit=Decimal('1000.00')
    )


@pytest.fixture
def sample_schedule():
    """Create sample ad schedule for testing."""
    return AdSchedule(
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
        start_time="09:00",
        end_time="17:00",
        days_of_week=[0, 1, 2, 3, 4],  # Monday to Friday
        timezone="UTC"
    )


@pytest.fixture
def sample_campaign(sample_targeting, sample_budget):
    """Create a sample campaign for testing."""
    return AdCampaign(
        name="Test Campaign",
        description="Test campaign description",
        objective="Brand Awareness",
        platform=Platform.FACEBOOK,
        targeting=sample_targeting,
        budget=sample_budget
    )


@pytest.fixture
def sample_ad(sample_targeting, sample_budget, sample_schedule, sample_campaign):
    """Create a sample ad for testing."""
    return Ad(
        name="Test Ad",
        description="Test ad description",
        ad_type=AdType.IMAGE,
        platform=Platform.FACEBOOK,
        headline="Test Headline",
        body_text="Test body text for testing purposes",
        targeting=sample_targeting,
        budget=sample_budget,
        schedule=sample_schedule,
        campaign_id=sample_campaign.id
    )


@pytest.fixture
def sample_ad_group():
    """Create a sample ad group for testing."""
    return AdGroup(
        name="Test Group",
        description="Test group description"
    )


@pytest.fixture
def optimization_factory():
    """Get the optimization factory instance."""
    return get_optimization_factory()


@pytest.fixture
def sample_optimization_context():
    """Create a sample optimization context for testing."""
    from optimization.base_optimizer import OptimizationContext, OptimizationStrategy, OptimizationLevel
    
    return OptimizationContext(
        target_entity="ad",
        entity_id="test-123",
        optimization_type=OptimizationStrategy.PERFORMANCE,
        level=OptimizationLevel.STANDARD,
        parameters={"test": "value"}
    )


@pytest.fixture
def large_dataset():
    """Create a large dataset for performance testing."""
    campaigns = []
    ads = []
    
    # Create 100 campaigns with 10 ads each
    for i in range(100):
        campaign = AdCampaign(
            name=f"Performance Campaign {i}",
            objective=f"Objective {i % 10}",
            platform=Platform.FACEBOOK
        )
        
        for j in range(10):
            ad = Ad(
                name=f"Performance Ad {i}-{j}",
                description=f"Ad description {i}-{j}",
                ad_type=AdType.IMAGE if j % 2 == 0 else AdType.VIDEO,
                platform=Platform.FACEBOOK
            )
            campaign.add_ad(ad)
            ads.append(ad)
        
        campaigns.append(campaign)
    
    return campaigns, ads


@pytest.fixture
def campaign_with_ads(sample_campaign, sample_ad):
    """Create a campaign with ads for testing."""
    sample_campaign.add_ad(sample_ad)
    return sample_campaign


@pytest.fixture
def multiple_campaigns():
    """Create multiple campaigns for testing."""
    campaigns = []
    
    for i in range(5):
        campaign = AdCampaign(
            name=f"Multi Campaign {i}",
            objective=f"Multi Objective {i}",
            platform=Platform.FACEBOOK
        )
        
        # Add 3 ads to each campaign
        for j in range(3):
            ad = Ad(
                name=f"Multi Ad {i}-{j}",
                ad_type=AdType.IMAGE,
                platform=Platform.FACEBOOK
            )
            campaign.add_ad(ad)
        
        campaigns.append(campaign)
    
    return campaigns


@pytest.fixture
def sample_metrics():
    """Create sample ad metrics for testing."""
    from domain.value_objects import AdMetrics
    
    return AdMetrics(
        impressions=1000,
        clicks=50,
        conversions=5,
        spend=Decimal('100.00')
    )


@pytest.fixture
def sample_optimization_result():
    """Create a sample optimization result for testing."""
    from optimization.base_optimizer import OptimizationResult
    
    return OptimizationResult(
        strategy=OptimizationStrategy.PERFORMANCE,
        level=OptimizationLevel.STANDARD,
        success=True,
        metrics_before={"cpu": 80.0, "memory": 75.0},
        metrics_after={"cpu": 65.0, "memory": 60.0},
        improvement_percentage=15.0,
        duration_ms=1500.0,
        details={"optimization_type": "performance", "techniques_applied": ["cpu_optimization"]}
    )


# Test data fixtures
@pytest.fixture
def test_platforms():
    """Return all available platforms for testing."""
    return list(Platform)


@pytest.fixture
def test_ad_types():
    """Return all available ad types for testing."""
    return list(AdType)


@pytest.fixture
def test_ad_statuses():
    """Return all available ad statuses for testing."""
    return list(AdStatus)


@pytest.fixture
def test_optimization_levels():
    """Return all available optimization levels for testing."""
    return list(OptimizationLevel)


@pytest.fixture
def test_optimization_strategies():
    """Return all available optimization strategies for testing."""
    return list(OptimizationStrategy)


# Performance test fixtures
@pytest.fixture
def performance_test_data():
    """Create data for performance testing."""
    campaigns = []
    ads = []
    
    # Create 500 campaigns with 5 ads each
    for i in range(500):
        campaign = AdCampaign(
            name=f"Performance Test Campaign {i}",
            objective=f"Performance Test Objective {i}",
            platform=Platform.FACEBOOK
        )
        
        for j in range(5):
            ad = Ad(
                name=f"Performance Test Ad {i}-{j}",
                ad_type=AdType.IMAGE,
                platform=Platform.FACEBOOK
            )
            campaign.add_ad(ad)
            ads.append(ad)
        
        campaigns.append(campaign)
    
    return campaigns, ads


# Stress test fixtures
@pytest.fixture
def stress_test_data():
    """Create data for stress testing."""
    campaigns = []
    ads = []
    
    # Create 1000 campaigns with 10 ads each
    for i in range(1000):
        campaign = AdCampaign(
            name=f"Stress Test Campaign {i}",
            objective=f"Stress Test Objective {i}",
            platform=Platform.FACEBOOK
        )
        
        for j in range(10):
            ad = Ad(
                name=f"Stress Test Ad {i}-{j}",
                ad_type=AdType.IMAGE,
                platform=Platform.FACEBOOK
            )
            campaign.add_ad(ad)
            ads.append(ad)
        
        campaigns.append(campaign)
    
    return campaigns, ads


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Any cleanup code can go here if needed


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for multiple components"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and benchmark tests"
    )
    config.addinivalue_line(
        "markers", "stress: Stress tests for system robustness"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file paths."""
    for item in items:
        # Add markers based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Add slow marker for tests that might take time
        if any(keyword in item.name for keyword in ["bulk", "large", "concurrent", "stress"]):
            item.add_marker(pytest.mark.slow)

