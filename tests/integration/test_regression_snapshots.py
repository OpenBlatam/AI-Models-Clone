"""
🧪 Regression and Snapshot Tests for ADS System

Tests to ensure system behavior remains consistent across versions
and detect unintended changes in outputs.
"""

import pytest
import json
import hashlib
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List
import pickle

# Import system components
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import (
    AdStatus, AdType, Platform, Budget, TargetingCriteria, AdSchedule, AdMetrics
)
from optimization.factory import get_optimization_factory
from optimization.base_optimizer import OptimizationContext, OptimizationStrategy, OptimizationLevel


class TestRegressionSuite:
    """Regression tests to ensure consistent system behavior."""
    
    @pytest.fixture
    def baseline_campaign(self):
        """Baseline campaign for regression testing."""
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
            name="Regression Test Campaign",
            description="Baseline campaign for regression testing",
            objective="Brand Awareness",
            platform=Platform.FACEBOOK,
            targeting=targeting,
            budget=budget
        )
    
    @pytest.fixture
    def baseline_ad(self, baseline_campaign):
        """Baseline ad for regression testing."""
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
            start_date=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            end_date=datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        )
        
        return Ad(
            name="Regression Test Ad",
            description="Baseline ad for regression testing",
            ad_type=AdType.IMAGE,
            platform=Platform.FACEBOOK,
            headline="Regression Test Headline",
            body_text="This is a baseline ad for regression testing purposes.",
            targeting=targeting,
            budget=budget,
            schedule=schedule,
            campaign_id=baseline_campaign.id
        )
    
    def test_campaign_serialization_consistency(self, baseline_campaign):
        """Test that campaign serialization produces consistent output."""
        # Serialize campaign
        campaign_dict = baseline_campaign.to_dict()
        
        # Expected keys should always be present
        expected_keys = {
            'id', 'name', 'description', 'objective', 'platform', 
            'status', 'targeting', 'budget', 'ads', 'created_at', 'updated_at'
        }
        
        assert set(campaign_dict.keys()) >= expected_keys, "Missing expected keys in campaign serialization"
        
        # Check data types
        assert isinstance(campaign_dict['name'], str)
        assert isinstance(campaign_dict['platform'], str)
        assert isinstance(campaign_dict['status'], str)
        assert isinstance(campaign_dict['ads'], list)
        
        # Check budget structure
        if campaign_dict['budget']:
            budget = campaign_dict['budget']
            assert 'amount' in budget
            assert 'currency' in budget
            assert 'daily_limit' in budget
            assert 'lifetime_limit' in budget
    
    def test_ad_serialization_consistency(self, baseline_ad):
        """Test that ad serialization produces consistent output."""
        # Serialize ad
        ad_dict = baseline_ad.to_dict()
        
        # Expected keys should always be present
        expected_keys = {
            'id', 'name', 'description', 'ad_type', 'platform', 'status',
            'headline', 'body_text', 'targeting', 'budget', 'schedule',
            'metrics', 'campaign_id', 'created_at', 'updated_at'
        }
        
        assert set(ad_dict.keys()) >= expected_keys, "Missing expected keys in ad serialization"
        
        # Check data types
        assert isinstance(ad_dict['name'], str)
        assert isinstance(ad_dict['ad_type'], str)
        assert isinstance(ad_dict['platform'], str)
        assert isinstance(ad_dict['status'], str)
        
        # Check schedule structure
        if ad_dict['schedule']:
            schedule = ad_dict['schedule']
            assert 'start_date' in schedule
            assert 'end_date' in schedule
    
    def test_optimization_factory_consistency(self):
        """Test that optimization factory behavior is consistent."""
        factory = get_optimization_factory()
        
        # Test that the same context always returns the same optimizer
        context = OptimizationContext(
            target_entity="ad",
            entity_id="regression-test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD
        )
        
        # Call multiple times and ensure consistency
        results = []
        for _ in range(5):
            optimal = factory.get_optimal_optimizer(context)
            results.append(optimal)
        
        # All results should be the same
        assert all(r == results[0] for r in results), "Optimization factory should return consistent results"
        
        # Test factory statistics consistency
        stats1 = factory.get_optimization_statistics()
        stats2 = factory.get_optimization_statistics()
        
        assert stats1['total_optimizers'] == stats2['total_optimizers']
        assert stats1['optimizer_types'] == stats2['optimizer_types']
    
    def test_ad_lifecycle_regression(self, baseline_ad):
        """Test ad lifecycle for regression."""
        # Record initial state
        initial_status = baseline_ad.status
        assert initial_status == AdStatus.DRAFT
        
        # Test status transitions
        baseline_ad.status = AdStatus.PENDING_REVIEW
        assert baseline_ad.status == AdStatus.PENDING_REVIEW
        
        baseline_ad.approve()
        assert baseline_ad.status == AdStatus.APPROVED
        
        baseline_ad.activate()
        assert baseline_ad.status == AdStatus.ACTIVE
        
        baseline_ad.pause()
        assert baseline_ad.status == AdStatus.PAUSED
        
        baseline_ad.archive()
        assert baseline_ad.status == AdStatus.ARCHIVED
    
    def test_campaign_ad_relationship_regression(self, baseline_campaign, baseline_ad):
        """Test campaign-ad relationship for regression."""
        # Initial state
        assert len(baseline_campaign.ads) == 0
        assert baseline_ad.campaign_id == baseline_campaign.id
        
        # Add ad to campaign
        baseline_campaign.add_ad(baseline_ad)
        
        # Verify relationship
        assert len(baseline_campaign.ads) == 1
        assert baseline_ad in baseline_campaign.ads
        assert baseline_ad.campaign_id == baseline_campaign.id


class TestSnapshotTesting:
    """Snapshot testing to detect unintended output changes."""
    
    @pytest.fixture
    def snapshots_dir(self):
        """Directory for storing snapshots."""
        snapshots_path = Path("tests/fixtures/snapshots")
        snapshots_path.mkdir(parents=True, exist_ok=True)
        return snapshots_path
    
    def normalize_for_snapshot(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize data for consistent snapshots."""
        if isinstance(data, dict):
            normalized = {}
            for key, value in data.items():
                if key in ['id', 'created_at', 'updated_at']:
                    # Skip or normalize time-dependent fields
                    if key == 'id':
                        normalized[key] = "<UUID>"
                    else:
                        normalized[key] = "<TIMESTAMP>"
                elif isinstance(value, dict):
                    normalized[key] = self.normalize_for_snapshot(value)
                elif isinstance(value, list):
                    normalized[key] = [self.normalize_for_snapshot(item) if isinstance(item, dict) else item for item in value]
                else:
                    normalized[key] = value
            return normalized
        return data
    
    def save_snapshot(self, name: str, data: Any, snapshots_dir: Path):
        """Save a snapshot to file."""
        snapshot_file = snapshots_dir / f"{name}.json"
        normalized_data = self.normalize_for_snapshot(data)
        
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, indent=2, sort_keys=True, default=str)
        
        return snapshot_file
    
    def load_snapshot(self, name: str, snapshots_dir: Path) -> Any:
        """Load a snapshot from file."""
        snapshot_file = snapshots_dir / f"{name}.json"
        
        if not snapshot_file.exists():
            return None
        
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def assert_matches_snapshot(self, name: str, data: Any, snapshots_dir: Path, update_snapshots: bool = False):
        """Assert that data matches stored snapshot."""
        normalized_data = self.normalize_for_snapshot(data)
        
        if update_snapshots:
            self.save_snapshot(name, normalized_data, snapshots_dir)
            return
        
        stored_snapshot = self.load_snapshot(name, snapshots_dir)
        
        if stored_snapshot is None:
            # First time running, save snapshot
            self.save_snapshot(name, normalized_data, snapshots_dir)
            pytest.skip(f"First time running {name}, snapshot saved")
        
        assert normalized_data == stored_snapshot, f"Current data doesn't match snapshot for {name}"
    
    def test_campaign_serialization_snapshot(self, snapshots_dir):
        """Test campaign serialization against snapshot."""
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
            name="Snapshot Test Campaign",
            description="Campaign for snapshot testing",
            objective="Brand Awareness",
            platform=Platform.FACEBOOK,
            targeting=targeting,
            budget=budget
        )
        
        campaign_dict = campaign.to_dict()
        self.assert_matches_snapshot("campaign_serialization", campaign_dict, snapshots_dir)
    
    def test_ad_serialization_snapshot(self, snapshots_dir):
        """Test ad serialization against snapshot."""
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
            start_date=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            end_date=datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        )
        
        ad = Ad(
            name="Snapshot Test Ad",
            description="Ad for snapshot testing",
            ad_type=AdType.IMAGE,
            platform=Platform.FACEBOOK,
            headline="Snapshot Test Headline",
            body_text="This is a snapshot test ad.",
            targeting=targeting,
            budget=budget,
            schedule=schedule
        )
        
        ad_dict = ad.to_dict()
        self.assert_matches_snapshot("ad_serialization", ad_dict, snapshots_dir)
    
    def test_optimization_factory_snapshot(self, snapshots_dir):
        """Test optimization factory output against snapshot."""
        factory = get_optimization_factory()
        
        # Test factory statistics
        stats = factory.get_optimization_statistics()
        self.assert_matches_snapshot("optimization_factory_stats", stats, snapshots_dir)
        
        # Test available optimizers
        optimizers = factory.list_available_optimizers()
        self.assert_matches_snapshot("optimization_factory_optimizers", optimizers, snapshots_dir)
    
    def test_complex_workflow_snapshot(self, snapshots_dir):
        """Test complex workflow output against snapshot."""
        # Create campaign
        campaign = AdCampaign(
            name="Complex Workflow Campaign",
            objective="Complex Workflow Test",
            platform=Platform.FACEBOOK
        )
        
        # Create ads
        ads = []
        for i in range(3):
            ad = Ad(
                name=f"Complex Workflow Ad {i}",
                ad_type=AdType.IMAGE if i % 2 == 0 else AdType.VIDEO,
                platform=Platform.FACEBOOK
            )
            campaign.add_ad(ad)
            ads.append(ad)
        
        # Create workflow result
        workflow_result = {
            "campaign": campaign.to_dict(),
            "ads": [ad.to_dict() for ad in ads],
            "total_ads": len(ads),
            "campaign_status": campaign.status.value,
            "ad_statuses": [ad.status.value for ad in ads]
        }
        
        self.assert_matches_snapshot("complex_workflow", workflow_result, snapshots_dir)


class TestDataConsistency:
    """Tests to ensure data consistency across operations."""
    
    def test_id_uniqueness(self):
        """Test that entity IDs are always unique."""
        # Create multiple entities
        campaigns = [AdCampaign(name=f"Campaign {i}") for i in range(100)]
        ads = [Ad(name=f"Ad {i}") for i in range(100)]
        groups = [AdGroup(name=f"Group {i}") for i in range(100)]
        
        # Collect all IDs
        campaign_ids = [c.id for c in campaigns]
        ad_ids = [a.id for a in ads]
        group_ids = [g.id for g in groups]
        all_ids = campaign_ids + ad_ids + group_ids
        
        # Assert uniqueness
        assert len(all_ids) == len(set(all_ids)), "All entity IDs must be unique"
        assert len(campaign_ids) == len(set(campaign_ids)), "Campaign IDs must be unique"
        assert len(ad_ids) == len(set(ad_ids)), "Ad IDs must be unique"
        assert len(group_ids) == len(set(group_ids)), "Group IDs must be unique"
    
    def test_timestamp_consistency(self):
        """Test that timestamps are consistent and logical."""
        # Create entity
        ad = Ad(name="Timestamp Test Ad")
        
        # Initial timestamps
        initial_created = ad.created_at
        initial_updated = ad.updated_at
        
        # Should be equal initially
        assert abs((initial_created - initial_updated).total_seconds()) < 1, "Created and updated timestamps should be nearly equal initially"
        
        # Update entity
        import time
        time.sleep(0.1)  # Small delay
        ad.name = "Updated Timestamp Test Ad"
        
        # Updated timestamp should be later
        assert ad.updated_at > initial_updated, "Updated timestamp should be later after modification"
        assert ad.created_at == initial_created, "Created timestamp should not change"
    
    def test_relationship_consistency(self):
        """Test that relationships remain consistent."""
        campaign = AdCampaign(name="Relationship Test Campaign")
        ads = [Ad(name=f"Relationship Test Ad {i}") for i in range(5)]
        
        # Add ads to campaign
        for ad in ads:
            campaign.add_ad(ad)
        
        # Test consistency
        assert len(campaign.ads) == 5, "Campaign should have 5 ads"
        
        for ad in ads:
            assert ad in campaign.ads, "Each ad should be in campaign.ads"
            assert ad.campaign_id == campaign.id, "Each ad should reference campaign ID"
        
        # Test that ad IDs in campaign match actual ads
        campaign_ad_ids = [ad.id for ad in campaign.ads]
        actual_ad_ids = [ad.id for ad in ads]
        assert set(campaign_ad_ids) == set(actual_ad_ids), "Campaign ad IDs should match actual ad IDs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

