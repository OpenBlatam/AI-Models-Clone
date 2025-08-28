"""
🧪 Integration Tests for Complete ADS System

Tests that verify all components work together correctly
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
from optimization.base_optimizer import OptimizationContext, OptimizationStrategy, OptimizationLevel


class TestCompleteSystemIntegration:
    """Integration tests for the complete ADS system."""
    
    @pytest.fixture
    def sample_campaign(self):
        """Create a sample campaign for testing."""
        targeting = TargetingCriteria(
            age_min=25,
            age_max=45,
            genders=["male", "female"],
            locations=["United States", "Canada"],
            interests=["technology", "business"]
        )
        
        budget = Budget(
            amount=Decimal('1000.00'),
            currency="USD",
            daily_limit=Decimal('100.00'),
            lifetime_limit=Decimal('1000.00')
        )
        
        return AdCampaign(
            name="Integration Test Campaign",
            description="Campaign for integration testing",
            objective="Brand Awareness",
            platform=Platform.FACEBOOK,
            targeting=targeting,
            budget=budget
        )
    
    @pytest.fixture
    def sample_ad(self, sample_campaign):
        """Create a sample ad for testing."""
        targeting = TargetingCriteria(
            age_min=25,
            age_max=45,
            genders=["male", "female"],
            locations=["United States", "Canada"],
            interests=["technology", "business"]
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
            name="Integration Test Ad",
            description="Ad for integration testing",
            ad_type=AdType.IMAGE,
            platform=Platform.FACEBOOK,
            headline="Test Headline",
            body_text="Test body text for integration testing",
            targeting=targeting,
            budget=budget,
            schedule=schedule,
            campaign_id=sample_campaign.id
        )
    
    @pytest.fixture
    def optimization_factory(self):
        """Get the optimization factory."""
        return get_optimization_factory()
    
    def test_campaign_creation_and_management(self, sample_campaign):
        """Test complete campaign creation and management workflow."""
        # Verify campaign creation
        assert sample_campaign.name == "Integration Test Campaign"
        assert sample_campaign.objective == "Brand Awareness"
        assert sample_campaign.platform == Platform.FACEBOOK
        assert sample_campaign.status == AdStatus.DRAFT
        assert sample_campaign.id is not None
        
        # Test campaign targeting
        assert sample_campaign.targeting.age_min == 25
        assert sample_campaign.targeting.age_max == 45
        assert "male" in sample_campaign.targeting.genders
        assert "female" in sample_campaign.targeting.genders
        assert "United States" in sample_campaign.targeting.locations
        assert "technology" in sample_campaign.targeting.interests
        
        # Test campaign budget
        assert sample_campaign.budget.amount == Decimal('1000.00')
        assert sample_campaign.budget.currency == "USD"
        assert sample_campaign.budget.daily_limit == Decimal('100.00')
        assert sample_campaign.budget.lifetime_limit == Decimal('1000.00')
    
    def test_ad_creation_and_lifecycle(self, sample_ad):
        """Test complete ad creation and lifecycle workflow."""
        # Verify ad creation
        assert sample_ad.name == "Integration Test Ad"
        assert sample_ad.ad_type == AdType.IMAGE
        assert sample_ad.platform == Platform.FACEBOOK
        assert sample_ad.status == AdStatus.DRAFT
        assert sample_ad.id is not None
        
        # Test ad targeting
        assert sample_ad.targeting.age_min == 25
        assert sample_ad.targeting.age_max == 45
        assert "male" in sample_ad.targeting.genders
        assert "female" in sample_ad.targeting.genders
        
        # Test ad budget
        assert sample_ad.budget.amount == Decimal('100.00')
        assert sample_ad.budget.currency == "USD"
        assert sample_ad.budget.daily_limit == Decimal('20.00')
        
        # Test ad schedule
        assert sample_ad.schedule is not None
        assert sample_ad.schedule.start_date is not None
        assert sample_ad.schedule.end_date is not None
        assert sample_ad.schedule.is_active() is True
        
        # Test ad lifecycle
        # Set to pending review
        sample_ad.status = AdStatus.PENDING_REVIEW
        
        # Approve
        sample_ad.approve()
        assert sample_ad.status == AdStatus.APPROVED
        
        # Activate
        sample_ad.activate()
        assert sample_ad.status == AdStatus.ACTIVE
        
        # Pause
        sample_ad.pause()
        assert sample_ad.status == AdStatus.PAUSED
    
    def test_campaign_ad_relationship(self, sample_campaign, sample_ad):
        """Test campaign and ad relationship management."""
        # Add ad to campaign
        sample_campaign.add_ad(sample_ad)
        
        # Verify relationship
        assert len(sample_campaign.ads) == 1
        assert sample_ad in sample_campaign.ads
        assert sample_ad.campaign_id == sample_campaign.id
        
        # Test campaign status changes
        sample_campaign.status = AdStatus.ACTIVE
        assert sample_campaign.status == AdStatus.ACTIVE
    
    def test_optimization_system_integration(self, optimization_factory, sample_ad):
        """Test optimization system integration."""
        # Create optimization context
        context = OptimizationContext(
            target_entity="ad",
            entity_id=str(sample_ad.id),
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD,
            parameters={"test": "integration"}
        )
        
        # Get optimal optimizer
        optimal_optimizer = optimization_factory.get_optimal_optimizer(context)
        assert optimal_optimizer is not None
        assert optimal_optimizer in ["performance", "profiling", "gpu"]
        
        # Get optimizer info
        optimizer_info = optimization_factory.get_optimizer_info(optimal_optimizer)
        assert optimizer_info is not None
        assert "type" in optimizer_info
        assert "config" in optimizer_info
        assert "capabilities" in optimizer_info
        
        # Test factory statistics
        stats = optimization_factory.get_optimization_statistics()
        assert stats["total_optimizers"] == 3
        assert "performance" in stats["optimizer_types"]
        assert "profiling" in stats["optimizer_types"]
        assert "gpu" in stats["optimizer_types"]
        
        # Test available optimizers
        available_optimizers = optimization_factory.list_available_optimizers()
        assert len(available_optimizers) == 3
        
        for optimizer_info in available_optimizers:
            assert "type" in optimizer_info
            assert "config" in optimizer_info
            assert "capabilities" in optimizer_info
    
    @pytest.mark.asyncio
    async def test_complete_optimization_workflow(self, optimization_factory, sample_ad):
        """Test complete optimization workflow execution."""
        # Create optimization context
        context = OptimizationContext(
            target_entity="ad",
            entity_id=str(sample_ad.id),
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD
        )
        
        # Execute optimization
        result = await optimization_factory.execute_optimization(context, "performance")
        
        # Verify result
        assert result is not None
        assert result.success is True
        assert result.strategy == OptimizationStrategy.PERFORMANCE
        assert result.level == OptimizationLevel.STANDARD
    
    def test_value_objects_integration(self):
        """Test value objects integration with entities."""
        # Test targeting criteria
        targeting = TargetingCriteria(
            age_min=18,
            age_max=65,
            genders=["male", "female", "other"],
            locations=["Global"],
            interests=["general"]
        )
        
        assert targeting.age_min == 18
        assert targeting.age_max == 65
        assert len(targeting.genders) == 3
        assert "Global" in targeting.locations
        
        # Test budget
        budget = Budget(
            amount=Decimal('5000.00'),
            currency="EUR",
            daily_limit=Decimal('500.00'),
            lifetime_limit=Decimal('5000.00')
        )
        
        assert budget.amount == Decimal('5000.00')
        assert budget.currency == "EUR"
        assert budget.daily_limit == Decimal('500.00')
        
        # Test schedule
        schedule = AdSchedule(
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=90),
            start_time="00:00",
            end_time="23:59",
            days_of_week=[0, 1, 2, 3, 4, 5, 6],  # All days
            timezone="UTC"
        )
        
        assert schedule.start_date is not None
        assert schedule.end_date is not None
        assert schedule.start_time == "00:00"
        assert schedule.end_time == "23:59"
        assert len(schedule.days_of_week) == 7
        assert schedule.is_active() is True
    
    def test_entity_serialization(self, sample_campaign, sample_ad):
        """Test entity serialization to dictionaries."""
        # Test campaign serialization
        campaign_dict = sample_campaign.to_dict()
        
        assert "id" in campaign_dict
        assert "name" in campaign_dict
        assert "objective" in campaign_dict
        assert "platform" in campaign_dict
        assert "targeting" in campaign_dict
        assert "budget" in campaign_dict
        
        # Test ad serialization
        ad_dict = sample_ad.to_dict()
        
        assert "id" in ad_dict
        assert "name" in ad_dict
        assert "ad_type" in ad_dict
        assert "platform" in ad_dict
        assert "status" in ad_dict
        assert "targeting" in ad_dict
        assert "budget" in ad_dict
        assert "schedule" in ad_dict
        assert "metrics" in ad_dict
    
    def test_system_consistency(self, sample_campaign, sample_ad):
        """Test system consistency across components."""
        # Verify that all entities have consistent data types
        assert isinstance(sample_campaign.id, type(sample_ad.id))
        assert isinstance(sample_campaign.name, type(sample_ad.name))
        assert isinstance(sample_campaign.targeting, type(sample_ad.targeting))
        assert isinstance(sample_campaign.budget, type(sample_ad.budget))
        
        # Verify that relationships are properly maintained
        sample_campaign.add_ad(sample_ad)
        
        assert sample_ad.campaign_id == sample_campaign.id
        assert sample_ad in sample_campaign.ads
        
        # Verify that status changes are consistent
        sample_campaign.status = AdStatus.ACTIVE
        sample_ad.status = AdStatus.ACTIVE
        
        assert sample_campaign.status == AdStatus.ACTIVE
        assert sample_ad.status == AdStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, sample_campaign, sample_ad, optimization_factory):
        """Test complete end-to-end workflow."""
        # 1. Campaign setup
        assert sample_campaign.status == AdStatus.DRAFT
        
        # 2. Ad creation and setup
        assert sample_ad.status == AdStatus.DRAFT
        sample_ad.status = AdStatus.PENDING_REVIEW
        sample_ad.approve()
        sample_ad.activate()
        
        # 3. Add ad to campaign
        sample_campaign.add_ad(sample_ad)
        sample_campaign.status = AdStatus.ACTIVE
        
        # 4. Run optimization
        context = OptimizationContext(
            target_entity="ad",
            entity_id=str(sample_ad.id),
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD
        )
        
        result = await optimization_factory.execute_optimization(context, "performance")
        
        # 5. Verify final state
        assert sample_campaign.status == AdStatus.ACTIVE
        assert sample_ad.status == AdStatus.ACTIVE
        assert len(sample_campaign.ads) == 1
        assert result.success is True
        
        # 6. Verify system statistics
        campaign_stats = {
            "total_ads": len(sample_campaign.ads),
            "campaign_status": sample_campaign.status.value,
            "ad_statuses": [ad.status.value for ad in sample_campaign.ads]
        }
        
        assert campaign_stats["total_ads"] == 1
        assert campaign_stats["campaign_status"] == "active"
        assert "active" in campaign_stats["ad_statuses"]


class TestSystemPerformance:
    """Performance tests for the ADS system."""
    
    def test_bulk_entity_creation(self):
        """Test creating many entities efficiently."""
        campaigns = []
        ads = []
        
        # Create 100 campaigns with ads
        for i in range(100):
            campaign = AdCampaign(
                name=f"Bulk Campaign {i}",
                objective=f"Objective {i}",
                platform=Platform.FACEBOOK
            )
            
            for j in range(5):  # 5 ads per campaign
                ad = Ad(
                    name=f"Bulk Ad {i}-{j}",
                    campaign_id=campaign.id
                )
                campaign.add_ad(ad)
                ads.append(ad)
            
            campaigns.append(campaign)
        
        # Verify creation
        assert len(campaigns) == 100
        assert len(ads) == 500
        
        # Verify relationships
        for campaign in campaigns:
            assert len(campaign.ads) == 5
        
        for ad in ads:
            assert ad.campaign_id is not None
    
    def test_optimization_factory_performance(self):
        """Test optimization factory performance with many contexts."""
        factory = get_optimization_factory()
        
        contexts = []
        for i in range(100):
            context = OptimizationContext(
                target_entity="ad",
                entity_id=f"test-{i}",
                optimization_type=OptimizationStrategy.PERFORMANCE,
                level=OptimizationLevel.STANDARD
            )
            contexts.append(context)
        
        # Test getting optimal optimizer for many contexts
        for context in contexts:
            optimal = factory.get_optimal_optimizer(context)
            assert optimal is not None
            assert optimal in ["performance", "profiling", "gpu"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

