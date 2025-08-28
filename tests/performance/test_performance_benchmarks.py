"""
🧪 Performance and Stress Tests for ADS System

Tests to measure system performance under various load conditions
"""

import pytest
import time
import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import statistics
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

# Import system components
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import (
    AdStatus, AdType, Platform, Budget, TargetingCriteria, AdSchedule
)
from optimization.factory import get_optimization_factory
from optimization.base_optimizer import OptimizationContext, OptimizationStrategy, OptimizationLevel


class TestPerformanceBenchmarks:
    """Performance benchmark tests for the ADS system."""
    
    @pytest.fixture
    def large_dataset(self):
        """Create a large dataset for performance testing."""
        campaigns = []
        ads = []
        
        # Create 1000 campaigns with 10 ads each
        for i in range(1000):
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
    
    def test_entity_creation_performance(self, benchmark):
        """Benchmark entity creation performance."""
        def create_entities():
            campaigns = []
            ads = []
            
            for i in range(100):
                campaign = AdCampaign(
                    name=f"Benchmark Campaign {i}",
                    objective=f"Objective {i}",
                    platform=Platform.FACEBOOK
                )
                
                for j in range(5):
                    ad = Ad(
                        name=f"Benchmark Ad {i}-{j}",
                        ad_type=AdType.IMAGE,
                        platform=Platform.FACEBOOK
                    )
                    campaign.add_ad(ad)
                    ads.append(ad)
                
                campaigns.append(campaign)
            
            return len(campaigns), len(ads)
        
        result = benchmark(create_entities)
        assert result[0] == 100
        assert result[1] == 500
    
    def test_entity_serialization_performance(self, benchmark, large_dataset):
        """Benchmark entity serialization performance."""
        campaigns, ads = large_dataset
        
        def serialize_entities():
            campaign_dicts = [campaign.to_dict() for campaign in campaigns[:100]]
            ad_dicts = [ad.to_dict() for ad in ads[:1000]]
            return len(campaign_dicts), len(ad_dicts)
        
        result = benchmark(serialize_entities)
        assert result[0] == 100
        assert result[1] == 1000
    
    def test_optimization_factory_performance(self, benchmark):
        """Benchmark optimization factory performance."""
        factory = get_optimization_factory()
        
        def create_and_optimize_contexts():
            contexts = []
            for i in range(1000):
                context = OptimizationContext(
                    target_entity="ad",
                    entity_id=f"benchmark-{i}",
                    optimization_type=OptimizationStrategy.PERFORMANCE,
                    level=OptimizationLevel.STANDARD
                )
                contexts.append(context)
            
            # Get optimal optimizer for each context
            results = []
            for context in contexts:
                optimal = factory.get_optimal_optimizer(context)
                results.append(optimal)
            
            return len(results)
        
        result = benchmark(create_and_optimize_contexts)
        assert result == 1000
    
    def test_bulk_operations_performance(self, benchmark):
        """Benchmark bulk operations performance."""
        def bulk_operations():
            # Create 500 campaigns
            campaigns = []
            for i in range(500):
                campaign = AdCampaign(
                    name=f"Bulk Campaign {i}",
                    objective=f"Bulk Objective {i}",
                    platform=Platform.FACEBOOK
                )
                campaigns.append(campaign)
            
            # Create 2500 ads
            ads = []
            for i in range(2500):
                ad = Ad(
                    name=f"Bulk Ad {i}",
                    ad_type=AdType.IMAGE,
                    platform=Platform.FACEBOOK
                )
                ads.append(ad)
            
            # Add ads to campaigns (5 ads per campaign)
            for i, campaign in enumerate(campaigns):
                start_idx = i * 5
                end_idx = start_idx + 5
                for j in range(start_idx, min(end_idx, len(ads))):
                    campaign.add_ad(ads[j])
            
            # Verify relationships
            total_ads = sum(len(campaign.ads) for campaign in campaigns)
            return len(campaigns), len(ads), total_ads
        
        result = benchmark(bulk_operations)
        assert result[0] == 500
        assert result[1] == 2500
        assert result[2] == 2500
    
    def test_memory_usage_performance(self):
        """Test memory usage under load."""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        campaigns = []
        ads = []
        
        for i in range(1000):
            campaign = AdCampaign(
                name=f"Memory Campaign {i}",
                objective=f"Memory Objective {i}",
                platform=Platform.FACEBOOK
            )
            
            for j in range(10):
                ad = Ad(
                    name=f"Memory Ad {i}-{j}",
                    description=f"Memory ad description {i}-{j}",
                    ad_type=AdType.IMAGE,
                    platform=Platform.FACEBOOK,
                    headline=f"Memory Headline {i}-{j}",
                    body_text=f"Memory body text {i}-{j} " * 10  # Longer text
                )
                campaign.add_ad(ad)
                ads.append(ad)
            
            campaigns.append(campaign)
        
        # Get memory usage after creation
        gc.collect()  # Force garbage collection
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Calculate memory increase
        memory_increase = peak_memory - initial_memory
        
        # Verify we created the expected number of entities
        assert len(campaigns) == 1000
        assert len(ads) == 10000
        
        # Memory usage should be reasonable (less than 1GB for 10k entities)
        assert memory_increase < 1024  # Less than 1GB
        
        # Clean up
        del campaigns, ads
        gc.collect()
        
        # Verify cleanup
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        assert final_memory < peak_memory


class TestStressTests:
    """Stress tests for the ADS system."""
    
    def test_concurrent_entity_creation(self):
        """Test concurrent entity creation under stress."""
        def create_campaign_batch(batch_id):
            campaigns = []
            for i in range(100):
                campaign = AdCampaign(
                    name=f"Concurrent Campaign {batch_id}-{i}",
                    objective=f"Concurrent Objective {batch_id}-{i}",
                    platform=Platform.FACEBOOK
                )
                
                for j in range(5):
                    ad = Ad(
                        name=f"Concurrent Ad {batch_id}-{i}-{j}",
                        ad_type=AdType.IMAGE,
                        platform=Platform.FACEBOOK
                    )
                    campaign.add_ad(ad)
                
                campaigns.append(campaign)
            
            return len(campaigns)
        
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(create_campaign_batch, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # Verify all batches completed successfully
        assert len(results) == 10
        assert all(result == 100 for result in results)
    
    def test_concurrent_optimization_requests(self):
        """Test concurrent optimization requests under stress."""
        factory = get_optimization_factory()
        
        def optimization_request(request_id):
            contexts = []
            for i in range(100):
                context = OptimizationContext(
                    target_entity="ad",
                    entity_id=f"stress-{request_id}-{i}",
                    optimization_type=OptimizationStrategy.PERFORMANCE,
                    level=OptimizationLevel.STANDARD
                )
                contexts.append(context)
            
            # Get optimal optimizer for each context
            results = []
            for context in contexts:
                optimal = factory.get_optimal_optimizer(context)
                results.append(optimal)
            
            return len(results)
        
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(optimization_request, i) for i in range(20)]
            results = [future.result() for future in futures]
        
        # Verify all requests completed successfully
        assert len(results) == 20
        assert all(result == 100 for result in results)
    
    def test_large_scale_relationships(self):
        """Test large-scale relationship management."""
        # Create 1000 campaigns
        campaigns = []
        for i in range(1000):
            campaign = AdCampaign(
                name=f"Large Scale Campaign {i}",
                objective=f"Large Scale Objective {i}",
                platform=Platform.FACEBOOK
            )
            campaigns.append(campaign)
        
        # Create 10000 ads
        ads = []
        for i in range(10000):
            ad = Ad(
                name=f"Large Scale Ad {i}",
                ad_type=AdType.IMAGE,
                platform=Platform.FACEBOOK
            )
            ads.append(ad)
        
        # Distribute ads across campaigns (10 ads per campaign)
        for i, campaign in enumerate(campaigns):
            start_idx = i * 10
            end_idx = start_idx + 10
            for j in range(start_idx, min(end_idx, len(ads))):
                campaign.add_ad(ads[j])
        
        # Verify relationships
        total_ads_in_campaigns = sum(len(campaign.ads) for campaign in campaigns)
        assert total_ads_in_campaigns == 10000
        
        # Verify campaign relationships
        for i, campaign in enumerate(campaigns):
            assert len(campaign.ads) == 10
            for ad in campaign.ads:
                assert ad.campaign_id == campaign.id
    
    def test_memory_pressure_test(self):
        """Test system behavior under memory pressure."""
        import gc
        
        # Create entities in batches to test memory pressure
        batch_size = 1000
        num_batches = 5
        
        all_campaigns = []
        all_ads = []
        
        for batch in range(num_batches):
            # Create batch
            campaigns = []
            ads = []
            
            for i in range(batch_size):
                campaign = AdCampaign(
                    name=f"Memory Pressure Campaign {batch}-{i}",
                    objective=f"Memory Pressure Objective {batch}-{i}",
                    platform=Platform.FACEBOOK
                )
                
                for j in range(10):
                    ad = Ad(
                        name=f"Memory Pressure Ad {batch}-{i}-{j}",
                        description=f"Memory pressure test ad {batch}-{i}-{j} " * 5,
                        ad_type=AdType.IMAGE,
                        platform=Platform.FACEBOOK
                    )
                    campaign.add_ad(ad)
                    ads.append(ad)
                
                campaigns.append(campaign)
            
            all_campaigns.extend(campaigns)
            all_ads.extend(ads)
            
            # Force garbage collection every batch
            gc.collect()
        
        # Verify all entities were created
        assert len(all_campaigns) == batch_size * num_batches
        assert len(all_ads) == batch_size * num_batches * 10
        
        # Test operations on large dataset
        total_ads = sum(len(campaign.ads) for campaign in all_campaigns)
        assert total_ads == batch_size * num_batches * 10
        
        # Clean up
        del all_campaigns, all_ads
        gc.collect()


class TestScalabilityTests:
    """Scalability tests for the ADS system."""
    
    def test_linear_scalability(self):
        """Test that system scales linearly with entity count."""
        entity_counts = [100, 500, 1000, 2000]
        creation_times = []
        
        for count in entity_counts:
            start_time = time.time()
            
            # Create entities
            campaigns = []
            for i in range(count):
                campaign = AdCampaign(
                    name=f"Scalability Campaign {i}",
                    objective=f"Scalability Objective {i}",
                    platform=Platform.FACEBOOK
                )
                campaigns.append(campaign)
            
            end_time = time.time()
            creation_times.append(end_time - start_time)
        
        # Verify that creation time increases linearly (with some tolerance)
        for i in range(1, len(creation_times)):
            ratio = creation_times[i] / creation_times[0]
            expected_ratio = entity_counts[i] / entity_counts[0]
            
            # Allow 20% tolerance for non-linear overhead
            tolerance = 0.2
            assert abs(ratio - expected_ratio) <= expected_ratio * tolerance
    
    def test_optimization_factory_scalability(self):
        """Test optimization factory scalability."""
        factory = get_optimization_factory()
        
        request_counts = [100, 500, 1000, 2000]
        response_times = []
        
        for count in request_counts:
            start_time = time.time()
            
            # Create and process contexts
            contexts = []
            for i in range(count):
                context = OptimizationContext(
                    target_entity="ad",
                    entity_id=f"scalability-{i}",
                    optimization_type=OptimizationStrategy.PERFORMANCE,
                    level=OptimizationLevel.STANDARD
                )
                contexts.append(context)
            
            # Process all contexts
            results = []
            for context in contexts:
                optimal = factory.get_optimal_optimizer(context)
                results.append(optimal)
            
            end_time = time.time()
            response_times.append(end_time - start_time)
            
            # Verify results
            assert len(results) == count
            assert all(result in ["performance", "profiling", "gpu"] for result in results)
        
        # Verify that response time increases reasonably with request count
        for i in range(1, len(response_times)):
            ratio = response_times[i] / response_times[0]
            expected_ratio = request_counts[i] / request_counts[0]
            
            # Allow 30% tolerance for non-linear overhead
            tolerance = 0.3
            assert abs(ratio - expected_ratio) <= expected_ratio * tolerance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

