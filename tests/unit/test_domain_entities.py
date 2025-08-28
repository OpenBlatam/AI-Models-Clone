"""
🧪 Unit Tests for ADS Domain Entities

Tests for the core domain entities: Ad, AdCampaign, AdGroup
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

# Import domain entities
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import (
    AdStatus, AdType, Platform, Budget, TargetingCriteria, 
    AdSchedule, AdMetrics
)


class TestAdEntity:
    """Test cases for the Ad entity."""
    
    def test_ad_creation(self):
        """Test basic ad creation."""
        ad = Ad(
            name="Test Ad",
            description="Test description",
            ad_type=AdType.IMAGE,
            platform=Platform.FACEBOOK
        )
        
        assert ad.name == "Test Ad"
        assert ad.description == "Test description"
        assert ad.ad_type == AdType.IMAGE
        assert ad.platform == Platform.FACEBOOK
        assert ad.status == AdStatus.DRAFT
        assert ad.id is not None
    
    def test_ad_with_schedule(self):
        """Test ad creation with schedule."""
        schedule = AdSchedule(
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        ad = Ad(
            name="Scheduled Ad",
            schedule=schedule
        )
        
        assert ad.schedule is not None
        assert ad.schedule.start_date is not None
        assert ad.schedule.end_date is not None
    
    def test_ad_lifecycle(self):
        """Test ad lifecycle transitions."""
        ad = Ad(name="Lifecycle Test Ad")
        
        # Initial state
        assert ad.status == AdStatus.DRAFT
        
        # Set to pending review
        ad.status = AdStatus.PENDING_REVIEW
        
        # Approve
        ad.approve()
        assert ad.status == AdStatus.APPROVED
        
        # Activate (needs schedule)
        schedule = AdSchedule(
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30)
        )
        ad.schedule = schedule
        ad.activate()
        assert ad.status == AdStatus.ACTIVE
        
        # Pause
        ad.pause()
        assert ad.status == AdStatus.PAUSED
        
        # Archive
        ad.archive()
        assert ad.status == AdStatus.ARCHIVED
    
    def test_ad_validation(self):
        """Test ad validation rules."""
        # Test empty name validation
        with pytest.raises(ValueError, match="Ad name cannot be empty"):
            Ad(name="")
        
        with pytest.raises(ValueError, match="Ad name cannot be empty"):
            Ad(name="   ")
    
    def test_ad_metrics_update(self):
        """Test ad metrics update functionality."""
        ad = Ad(name="Metrics Test Ad")
        
        # Update metrics
        ad.update_metrics(
            impressions=1000,
            clicks=50,
            conversions=5,
            spend=Decimal('100.00')
        )
        
        assert ad.metrics.impressions == 1000
        assert ad.metrics.clicks == 50
        assert ad.metrics.conversions == 5
        assert ad.metrics.spend == Decimal('100.00')
    
    def test_ad_budget_validation(self):
        """Test ad budget validation."""
        budget = Budget(
            amount=Decimal('100.00'),
            currency="USD",
            daily_limit=Decimal('20.00'),
            lifetime_limit=Decimal('100.00')
        )
        
        ad = Ad(
            name="Budget Test Ad",
            budget=budget
        )
        
        # Test budget validation
        assert ad.budget.amount == Decimal('100.00')
        assert ad.budget.currency == "USD"
        assert ad.budget.daily_limit == Decimal('20.00')
        assert ad.budget.lifetime_limit == Decimal('100.00')


class TestAdCampaignEntity:
    """Test cases for the AdCampaign entity."""
    
    def test_campaign_creation(self):
        """Test basic campaign creation."""
        targeting = TargetingCriteria(
            age_min=25,
            age_max=45,
            genders=["male", "female"],
            locations=["United States"],
            interests=["technology"]
        )
        
        budget = Budget(
            amount=Decimal('1000.00'),
            currency="USD"
        )
        
        campaign = AdCampaign(
            name="Test Campaign",
            description="Test campaign description",
            objective="Brand Awareness",
            platform=Platform.FACEBOOK,
            targeting=targeting,
            budget=budget
        )
        
        assert campaign.name == "Test Campaign"
        assert campaign.description == "Test campaign description"
        assert campaign.objective == "Brand Awareness"
        assert campaign.platform == Platform.FACEBOOK
        assert campaign.targeting == targeting
        assert campaign.budget == budget
        assert campaign.id is not None
    
    def test_campaign_add_ad(self):
        """Test adding ads to campaign."""
        campaign = AdCampaign(name="Campaign with Ads")
        ad1 = Ad(name="Ad 1")
        ad2 = Ad(name="Ad 2")
        
        campaign.add_ad(ad1)
        campaign.add_ad(ad2)
        
        assert len(campaign.ads) == 2
        assert ad1 in campaign.ads
        assert ad2 in campaign.ads
    
    def test_campaign_status_management(self):
        """Test campaign status management."""
        campaign = AdCampaign(name="Status Test Campaign")
        
        # Initial status
        assert campaign.status == AdStatus.DRAFT
        
        # Change status
        campaign.status = AdStatus.ACTIVE
        assert campaign.status == AdStatus.ACTIVE
        
        campaign.status = AdStatus.PAUSED
        assert campaign.status == AdStatus.PAUSED


class TestAdGroupEntity:
    """Test cases for the AdGroup entity."""
    
    def test_group_creation(self):
        """Test basic group creation."""
        group = AdGroup(
            name="Test Group",
            description="Test group description"
        )
        
        assert group.name == "Test Group"
        assert group.description == "Test group description"
        assert group.id is not None
    
    def test_group_add_ad(self):
        """Test adding ads to group."""
        group = AdGroup(name="Group with Ads")
        ad1 = Ad(name="Group Ad 1")
        ad2 = Ad(name="Group Ad 2")
        
        group.add_ad(ad1)
        group.add_ad(ad2)
        
        assert len(group.ads) == 2
        assert ad1 in group.ads
        assert ad2 in group.ads


class TestValueObjects:
    """Test cases for value objects."""
    
    def test_targeting_criteria(self):
        """Test targeting criteria validation."""
        targeting = TargetingCriteria(
            age_min=25,
            age_max=45,
            genders=["male", "female"],
            locations=["United States", "Canada"],
            interests=["technology", "business"]
        )
        
        assert targeting.age_min == 25
        assert targeting.age_max == 45
        assert "male" in targeting.genders
        assert "female" in targeting.genders
        assert "United States" in targeting.locations
        assert "technology" in targeting.interests
    
    def test_budget_validation(self):
        """Test budget validation."""
        budget = Budget(
            amount=Decimal('100.00'),
            currency="USD",
            daily_limit=Decimal('20.00'),
            lifetime_limit=Decimal('100.00')
        )
        
        assert budget.amount == Decimal('100.00')
        assert budget.currency == "USD"
        assert budget.daily_limit == Decimal('20.00')
        assert budget.lifetime_limit == Decimal('100.00')
    
    def test_ad_schedule(self):
        """Test ad schedule functionality."""
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=30)
        
        schedule = AdSchedule(
            start_date=start_date,
            end_date=end_date,
            start_time="09:00",
            end_time="17:00",
            days_of_week=[0, 1, 2, 3, 4],  # Monday to Friday
            timezone="UTC"
        )
        
        assert schedule.start_date == start_date
        assert schedule.end_date == end_date
        assert schedule.start_time == "09:00"
        assert schedule.end_time == "17:00"
        assert schedule.days_of_week == [0, 1, 2, 3, 4]
        assert schedule.timezone == "UTC"
    
    def test_ad_metrics_calculations(self):
        """Test ad metrics calculations."""
        metrics = AdMetrics(
            impressions=1000,
            clicks=50,
            conversions=5,
            spend=Decimal('100.00')
        )
        
        # Test calculated properties
        assert metrics.calculated_ctr == Decimal('5.0')  # 5% CTR
        assert metrics.calculated_cpc == Decimal('2.0')  # $2.00 CPC
        assert metrics.calculated_cpm == Decimal('100.0')  # $100.00 CPM
        assert metrics.calculated_conversion_rate == Decimal('10.0')  # 10% conversion rate


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

