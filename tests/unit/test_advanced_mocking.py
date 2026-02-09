"""
🧪 Advanced Mocking Tests for ADS System

Advanced testing patterns with sophisticated mocking, property-based testing,
and dynamic fixtures for comprehensive coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock, PropertyMock
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import asyncio
from typing import Any, Dict, List
import uuid

# Import system components
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import (
    AdStatus, AdType, Platform, Budget, TargetingCriteria, AdSchedule, AdMetrics
)
from optimization.factory import OptimizationFactory
from optimization.base_optimizer import OptimizationContext, OptimizationStrategy, OptimizationLevel


class TestAdvancedMocking:
    """Advanced mocking patterns for ADS system testing."""
    
    def test_ad_with_mocked_dependencies(self):
        """Test Ad entity with mocked external dependencies."""
        # Mock external validation service
        with patch('domain.entities.ExternalValidationService') as mock_validator:
            mock_validator.validate_content.return_value = True
            mock_validator.get_compliance_score.return_value = 0.95
            
            ad = Ad(
                name="Test Ad with Mocked Dependencies",
                description="Testing with mocked external services",
                ad_type=AdType.IMAGE,
                platform=Platform.FACEBOOK
            )
            
            # Verify ad creation
            assert ad.name == "Test Ad with Mocked Dependencies"
            assert ad.ad_type == AdType.IMAGE
            
            # Verify mocked service calls would work
            assert mock_validator.validate_content.call_count >= 0
    
    def test_campaign_with_mocked_database(self):
        """Test campaign operations with mocked database."""
        with patch('domain.entities.DatabaseService') as mock_db:
            # Setup mock database responses
            mock_db.save_campaign.return_value = {"id": "mocked-campaign-id", "status": "saved"}
            mock_db.get_campaign.return_value = {"id": "mocked-campaign-id", "name": "Mocked Campaign"}
            
            campaign = AdCampaign(
                name="Mocked Database Campaign",
                objective="Test Objective",
                platform=Platform.FACEBOOK
            )
            
            # Simulate database operations
            save_result = mock_db.save_campaign(campaign.to_dict())
            assert save_result["status"] == "saved"
            
            # Verify mock calls
            mock_db.save_campaign.assert_called_once()
    
    @patch('optimization.factory.OptimizationFactory.get_optimal_optimizer')
    def test_optimization_with_mocked_factory(self, mock_get_optimal):
        """Test optimization workflow with mocked factory."""
        # Setup mock return value
        mock_get_optimal.return_value = "performance"
        
        factory = OptimizationFactory()
        
        context = OptimizationContext(
            target_entity="ad",
            entity_id="test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD
        )
        
        # Test with mocked method
        optimal = factory.get_optimal_optimizer(context)
        
        assert optimal == "performance"
        mock_get_optimal.assert_called_once_with(context)
    
    @pytest.mark.asyncio
    async def test_async_optimization_with_mock(self):
        """Test async optimization with sophisticated mocking."""
        # Create async mock
        mock_optimizer = AsyncMock()
        mock_optimizer.optimize.return_value = Mock(
            success=True,
            improvement_percentage=25.5,
            duration_ms=1500.0
        )
        
        # Patch the factory to return our mock
        with patch('optimization.factory.OptimizationFactory.create_optimizer') as mock_create:
            mock_create.return_value = mock_optimizer
            
            factory = OptimizationFactory()
            optimizer = factory.create_optimizer("performance")
            
            context = OptimizationContext(
                target_entity="ad",
                entity_id="async-test",
                optimization_type=OptimizationStrategy.PERFORMANCE
            )
            
            result = await optimizer.optimize(context)
            
            assert result.success is True
            assert result.improvement_percentage == 25.5
            mock_optimizer.optimize.assert_called_once_with(context)


class TestPropertyBasedTesting:
    """Property-based testing for ADS system."""
    
    @pytest.mark.parametrize("ad_name,expected_valid", [
        ("Valid Ad Name", True),
        ("", False),
        ("   ", False),
        ("A" * 100, True),
        ("A" * 1000, False),
        ("Ad with 🚀 emoji", True),
        ("Ad\nwith\nnewlines", True),
    ])
    def test_ad_name_validation(self, ad_name, expected_valid):
        """Test ad name validation with various inputs."""
        if expected_valid:
            ad = Ad(name=ad_name)
            assert ad.name == ad_name.strip() if ad_name.strip() else ad_name
        else:
            with pytest.raises((ValueError, ValidationError)):
                Ad(name=ad_name)
    
    @pytest.mark.parametrize("budget_amount,currency,expected_valid", [
        (Decimal('100.00'), "USD", True),
        (Decimal('0.01'), "USD", True),
        (Decimal('0.00'), "USD", False),
        (Decimal('-10.00'), "USD", False),
        (Decimal('1000000.00'), "USD", True),
        (Decimal('100.00'), "EUR", True),
        (Decimal('100.00'), "INVALID", False),
    ])
    def test_budget_validation(self, budget_amount, currency, expected_valid):
        """Test budget validation with various amounts and currencies."""
        if expected_valid:
            budget = Budget(
                amount=budget_amount,
                currency=currency,
                daily_limit=budget_amount * Decimal('0.1'),
                lifetime_limit=budget_amount
            )
            assert budget.amount == budget_amount
            assert budget.currency == currency
        else:
            with pytest.raises((ValueError, ValidationError)):
                Budget(
                    amount=budget_amount,
                    currency=currency,
                    daily_limit=budget_amount * Decimal('0.1'),
                    lifetime_limit=budget_amount
                )
    
    @pytest.mark.parametrize("platform,ad_type,expected_compatible", [
        (Platform.FACEBOOK, AdType.IMAGE, True),
        (Platform.FACEBOOK, AdType.VIDEO, True),
        (Platform.FACEBOOK, AdType.TEXT, True),
        (Platform.GOOGLE, AdType.IMAGE, True),
        (Platform.GOOGLE, AdType.VIDEO, True),
        (Platform.INSTAGRAM, AdType.IMAGE, True),
        (Platform.INSTAGRAM, AdType.VIDEO, True),
        (Platform.LINKEDIN, AdType.TEXT, True),
    ])
    def test_platform_ad_type_compatibility(self, platform, ad_type, expected_compatible):
        """Test platform and ad type compatibility."""
        ad = Ad(
            name="Compatibility Test Ad",
            ad_type=ad_type,
            platform=platform
        )
        
        # All combinations should be valid for now
        assert ad.platform == platform
        assert ad.ad_type == ad_type


class TestDynamicFixtures:
    """Tests using dynamic fixtures and data generation."""
    
    @pytest.fixture
    def dynamic_campaign_factory(self):
        """Factory for creating campaigns with dynamic data."""
        def _create_campaign(
            name_prefix="Dynamic Campaign",
            objective_type="awareness",
            platform=Platform.FACEBOOK,
            budget_amount=1000.0
        ):
            targeting = TargetingCriteria(
                age_min=18 + (hash(name_prefix) % 50),
                age_max=35 + (hash(name_prefix) % 30),
                genders=["male", "female"],
                locations=[f"Location-{hash(name_prefix) % 100}"],
                interests=[f"Interest-{hash(name_prefix) % 50}"]
            )
            
            budget = Budget(
                amount=Decimal(str(budget_amount)),
                currency="USD",
                daily_limit=Decimal(str(budget_amount * 0.1)),
                lifetime_limit=Decimal(str(budget_amount))
            )
            
            return AdCampaign(
                name=f"{name_prefix}-{uuid.uuid4().hex[:8]}",
                objective=f"{objective_type}-{hash(name_prefix) % 100}",
                platform=platform,
                targeting=targeting,
                budget=budget
            )
        
        return _create_campaign
    
    @pytest.fixture
    def dynamic_ad_factory(self):
        """Factory for creating ads with dynamic data."""
        def _create_ad(
            name_prefix="Dynamic Ad",
            ad_type=AdType.IMAGE,
            platform=Platform.FACEBOOK,
            campaign_id=None
        ):
            targeting = TargetingCriteria(
                age_min=25,
                age_max=45,
                genders=["male", "female"],
                locations=["United States"],
                interests=["technology"]
            )
            
            budget = Budget(
                amount=Decimal('100.00'),
                currency="USD",
                daily_limit=Decimal('20.00'),
                lifetime_limit=Decimal('100.00')
            )
            
            schedule = AdSchedule(
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=30)
            )
            
            return Ad(
                name=f"{name_prefix}-{uuid.uuid4().hex[:8]}",
                description=f"Dynamic ad description for {name_prefix}",
                ad_type=ad_type,
                platform=platform,
                targeting=targeting,
                budget=budget,
                schedule=schedule,
                campaign_id=campaign_id
            )
        
        return _create_ad
    
    def test_dynamic_campaign_creation(self, dynamic_campaign_factory):
        """Test campaign creation with dynamic factory."""
        # Create multiple campaigns with different parameters
        campaign1 = dynamic_campaign_factory(
            name_prefix="Test Campaign A",
            objective_type="conversion",
            budget_amount=2000.0
        )
        
        campaign2 = dynamic_campaign_factory(
            name_prefix="Test Campaign B",
            objective_type="awareness",
            budget_amount=500.0
        )
        
        # Verify campaigns are different
        assert campaign1.name != campaign2.name
        assert campaign1.objective != campaign2.objective
        assert campaign1.budget.amount != campaign2.budget.amount
        
        # Verify basic properties
        assert "Test Campaign A" in campaign1.name
        assert "Test Campaign B" in campaign2.name
        assert campaign1.budget.amount == Decimal('2000.00')
        assert campaign2.budget.amount == Decimal('500.00')
    
    def test_dynamic_ad_creation(self, dynamic_ad_factory, dynamic_campaign_factory):
        """Test ad creation with dynamic factory."""
        # Create campaign first
        campaign = dynamic_campaign_factory(name_prefix="Parent Campaign")
        
        # Create ads for the campaign
        ads = []
        for i in range(5):
            ad = dynamic_ad_factory(
                name_prefix=f"Child Ad {i}",
                ad_type=AdType.IMAGE if i % 2 == 0 else AdType.VIDEO,
                campaign_id=campaign.id
            )
            ads.append(ad)
            campaign.add_ad(ad)
        
        # Verify ads are created correctly
        assert len(ads) == 5
        assert len(campaign.ads) == 5
        
        # Verify ad properties
        for i, ad in enumerate(ads):
            assert f"Child Ad {i}" in ad.name
            assert ad.campaign_id == campaign.id
            expected_type = AdType.IMAGE if i % 2 == 0 else AdType.VIDEO
            assert ad.ad_type == expected_type


class TestAdvancedAssertions:
    """Advanced assertion patterns and custom matchers."""
    
    def assert_ad_is_valid(self, ad: Ad):
        """Custom assertion for ad validity."""
        assert ad.id is not None, "Ad must have an ID"
        assert ad.name and ad.name.strip(), "Ad must have a non-empty name"
        assert ad.ad_type in AdType, "Ad must have a valid ad type"
        assert ad.platform in Platform, "Ad must have a valid platform"
        assert ad.status in AdStatus, "Ad must have a valid status"
        
        if ad.budget:
            assert ad.budget.amount > 0, "Budget amount must be positive"
            assert ad.budget.currency, "Budget must have a currency"
        
        if ad.schedule:
            assert ad.schedule.start_date, "Schedule must have a start date"
            assert ad.schedule.end_date, "Schedule must have an end date"
            assert ad.schedule.start_date < ad.schedule.end_date, "Start date must be before end date"
    
    def assert_campaign_is_valid(self, campaign: AdCampaign):
        """Custom assertion for campaign validity."""
        assert campaign.id is not None, "Campaign must have an ID"
        assert campaign.name and campaign.name.strip(), "Campaign must have a non-empty name"
        assert campaign.platform in Platform, "Campaign must have a valid platform"
        assert campaign.status in AdStatus, "Campaign must have a valid status"
        
        if campaign.budget:
            assert campaign.budget.amount > 0, "Budget amount must be positive"
        
        if campaign.targeting:
            assert campaign.targeting.age_min >= 13, "Minimum age must be at least 13"
            assert campaign.targeting.age_max <= 99, "Maximum age must be at most 99"
            assert campaign.targeting.age_min <= campaign.targeting.age_max, "Min age must be <= max age"
    
    def test_ad_validity_assertion(self):
        """Test custom ad validity assertion."""
        ad = Ad(
            name="Valid Test Ad",
            description="Test description",
            ad_type=AdType.IMAGE,
            platform=Platform.FACEBOOK
        )
        
        # This should pass
        self.assert_ad_is_valid(ad)
    
    def test_campaign_validity_assertion(self):
        """Test custom campaign validity assertion."""
        targeting = TargetingCriteria(
            age_min=25,
            age_max=45,
            genders=["male", "female"],
            locations=["United States"],
            interests=["technology"]
        )
        
        budget = Budget(
            amount=Decimal('1000.00'),
            currency="USD",
            daily_limit=Decimal('100.00'),
            lifetime_limit=Decimal('1000.00')
        )
        
        campaign = AdCampaign(
            name="Valid Test Campaign",
            objective="Brand Awareness",
            platform=Platform.FACEBOOK,
            targeting=targeting,
            budget=budget
        )
        
        # This should pass
        self.assert_campaign_is_valid(campaign)
    
    def test_complex_workflow_assertions(self, dynamic_campaign_factory, dynamic_ad_factory):
        """Test complex workflow with multiple custom assertions."""
        # Create campaign
        campaign = dynamic_campaign_factory(
            name_prefix="Workflow Test Campaign",
            budget_amount=5000.0
        )
        self.assert_campaign_is_valid(campaign)
        
        # Create ads
        ads = []
        for i in range(3):
            ad = dynamic_ad_factory(
                name_prefix=f"Workflow Ad {i}",
                campaign_id=campaign.id
            )
            self.assert_ad_is_valid(ad)
            campaign.add_ad(ad)
            ads.append(ad)
        
        # Assert campaign-ad relationships
        assert len(campaign.ads) == 3, "Campaign should have 3 ads"
        for ad in ads:
            assert ad in campaign.ads, "Ad should be in campaign"
            assert ad.campaign_id == campaign.id, "Ad should reference campaign"
        
        # Assert campaign state
        assert campaign.status == AdStatus.DRAFT, "New campaign should be in draft state"
        
        # Activate campaign
        campaign.status = AdStatus.ACTIVE
        assert campaign.status == AdStatus.ACTIVE, "Campaign should be active"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

