"""
🧪 Concurrency and Threading Tests for ADS System

Advanced tests for concurrent operations, thread safety,
and parallel processing capabilities.
"""

import pytest
import asyncio
import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
import multiprocessing
from typing import List, Dict, Any
import random

# Import system components
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import (
    AdStatus, AdType, Platform, Budget, TargetingCriteria, AdSchedule, AdMetrics
)
from optimization.factory import get_optimization_factory, OptimizationFactory
from optimization.base_optimizer import OptimizationContext, OptimizationStrategy, OptimizationLevel


class TestConcurrentEntityOperations:
    """Test concurrent operations on domain entities."""
    
    def test_concurrent_ad_creation(self):
        """Test creating ads concurrently from multiple threads."""
        ads_created = []
        lock = threading.Lock()
        
        def create_ad(thread_id):
            """Create an ad in a thread."""
            ad = Ad(
                name=f"Concurrent Ad {thread_id}",
                description=f"Ad created by thread {thread_id}",
                ad_type=AdType.IMAGE,
                platform=Platform.FACEBOOK
            )
            
            with lock:
                ads_created.append(ad)
            
            return ad
        
        # Create ads concurrently
        num_threads = 20
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_ad, i) for i in range(num_threads)]
            results = [future.result() for future in futures]
        
        # Verify all ads were created
        assert len(results) == num_threads
        assert len(ads_created) == num_threads
        
        # Verify all ads have unique IDs
        ad_ids = [ad.id for ad in ads_created]
        assert len(ad_ids) == len(set(ad_ids)), "All ad IDs should be unique"
        
        # Verify ad names are correct
        ad_names = [ad.name for ad in ads_created]
        expected_names = [f"Concurrent Ad {i}" for i in range(num_threads)]
        assert set(ad_names) == set(expected_names)
    
    def test_concurrent_campaign_ad_management(self):
        """Test concurrent campaign and ad operations."""
        campaign = AdCampaign(
            name="Concurrent Campaign",
            objective="Concurrency Testing",
            platform=Platform.FACEBOOK
        )
        
        ads_queue = queue.Queue()
        lock = threading.Lock()
        
        def add_ad_to_campaign(thread_id):
            """Add an ad to campaign from a thread."""
            ad = Ad(
                name=f"Campaign Ad {thread_id}",
                ad_type=AdType.IMAGE,
                platform=Platform.FACEBOOK
            )
            
            with lock:
                campaign.add_ad(ad)
            
            ads_queue.put(ad)
            return ad
        
        # Add ads concurrently
        num_threads = 15
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_ad_to_campaign, i) for i in range(num_threads)]
            results = [future.result() for future in futures]
        
        # Verify all ads were added
        assert len(campaign.ads) == num_threads
        assert ads_queue.qsize() == num_threads
        
        # Verify relationship integrity
        for ad in campaign.ads:
            assert ad.campaign_id == campaign.id
    
    def test_concurrent_status_updates(self):
        """Test concurrent status updates on the same entity."""
        ad = Ad(
            name="Status Update Test Ad",
            ad_type=AdType.IMAGE,
            platform=Platform.FACEBOOK
        )
        
        results = []
        lock = threading.Lock()
        
        def update_status(status):
            """Update ad status from a thread."""
            try:
                ad.status = status
                with lock:
                    results.append((status, ad.status, threading.current_thread().name))
                return True
            except Exception as e:
                with lock:
                    results.append((status, str(e), threading.current_thread().name))
                return False
        
        # Update status concurrently
        statuses = [
            AdStatus.PENDING_REVIEW,
            AdStatus.APPROVED,
            AdStatus.ACTIVE,
            AdStatus.PAUSED
        ]
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(update_status, status) for status in statuses]
            success_results = [future.result() for future in futures]
        
        # Verify final state is consistent
        assert ad.status in statuses
        assert len(results) == 4
        
        # All updates should succeed (last writer wins)
        assert all(success_results)


class TestAsyncConcurrency:
    """Test asynchronous concurrency patterns."""
    
    @pytest.mark.asyncio
    async def test_async_optimization_execution(self):
        """Test concurrent async optimization execution."""
        factory = get_optimization_factory()
        
        async def run_optimization(entity_id: str):
            """Run optimization asynchronously."""
            context = OptimizationContext(
                target_entity="ad",
                entity_id=entity_id,
                optimization_type=OptimizationStrategy.PERFORMANCE,
                level=OptimizationLevel.STANDARD
            )
            
            # Simulate async operation
            await asyncio.sleep(0.1)
            
            optimal_optimizer = factory.get_optimal_optimizer(context)
            optimizer = factory.create_optimizer(optimal_optimizer)
            
            result = await optimizer.optimize(context)
            return result
        
        # Run multiple optimizations concurrently
        num_optimizations = 10
        entity_ids = [f"async-entity-{i}" for i in range(num_optimizations)]
        
        tasks = [run_optimization(entity_id) for entity_id in entity_ids]
        results = await asyncio.gather(*tasks)
        
        # Verify all optimizations completed
        assert len(results) == num_optimizations
        
        # Verify all results are successful
        for result in results:
            assert result is not None
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_async_batch_operations(self):
        """Test async batch operations on entities."""
        async def create_campaign_batch(batch_id: int, batch_size: int):
            """Create a batch of campaigns asynchronously."""
            campaigns = []
            
            for i in range(batch_size):
                # Simulate async work
                await asyncio.sleep(0.01)
                
                campaign = AdCampaign(
                    name=f"Async Batch Campaign {batch_id}-{i}",
                    objective=f"Async Batch Objective {batch_id}",
                    platform=Platform.FACEBOOK
                )
                campaigns.append(campaign)
            
            return campaigns
        
        # Create multiple batches concurrently
        num_batches = 5
        batch_size = 10
        
        tasks = [create_campaign_batch(i, batch_size) for i in range(num_batches)]
        batch_results = await asyncio.gather(*tasks)
        
        # Flatten results
        all_campaigns = []
        for batch in batch_results:
            all_campaigns.extend(batch)
        
        # Verify total count
        assert len(all_campaigns) == num_batches * batch_size
        
        # Verify unique IDs
        campaign_ids = [c.id for c in all_campaigns]
        assert len(campaign_ids) == len(set(campaign_ids))
    
    @pytest.mark.asyncio
    async def test_async_producer_consumer(self):
        """Test async producer-consumer pattern."""
        ad_queue = asyncio.Queue(maxsize=50)
        processed_ads = []
        
        async def producer():
            """Produce ads asynchronously."""
            for i in range(20):
                ad = Ad(
                    name=f"Producer Ad {i}",
                    ad_type=AdType.IMAGE,
                    platform=Platform.FACEBOOK
                )
                await ad_queue.put(ad)
                await asyncio.sleep(0.05)  # Simulate work
            
            # Signal completion
            await ad_queue.put(None)
        
        async def consumer(consumer_id: int):
            """Consume ads asynchronously."""
            while True:
                ad = await ad_queue.get()
                if ad is None:
                    # Put sentinel back for other consumers
                    await ad_queue.put(None)
                    break
                
                # Process ad
                await asyncio.sleep(0.1)  # Simulate processing
                processed_ads.append((consumer_id, ad))
                ad_queue.task_done()
        
        # Start producer and consumers
        num_consumers = 3
        
        producer_task = asyncio.create_task(producer())
        consumer_tasks = [asyncio.create_task(consumer(i)) for i in range(num_consumers)]
        
        # Wait for completion
        await producer_task
        await asyncio.gather(*consumer_tasks)
        
        # Verify all ads were processed
        assert len(processed_ads) == 20
        
        # Verify consumers were balanced
        consumer_counts = {}
        for consumer_id, ad in processed_ads:
            consumer_counts[consumer_id] = consumer_counts.get(consumer_id, 0) + 1
        
        # Each consumer should have processed some ads
        assert len(consumer_counts) == num_consumers
        assert all(count > 0 for count in consumer_counts.values())


class TestThreadSafety:
    """Test thread safety of system components."""
    
    def test_optimization_factory_thread_safety(self):
        """Test optimization factory thread safety."""
        factory = get_optimization_factory()
        results = []
        lock = threading.Lock()
        
        def access_factory(thread_id: int):
            """Access factory from multiple threads."""
            thread_results = []
            
            for i in range(10):
                context = OptimizationContext(
                    target_entity="ad",
                    entity_id=f"thread-{thread_id}-entity-{i}",
                    optimization_type=OptimizationStrategy.PERFORMANCE,
                    level=OptimizationLevel.STANDARD
                )
                
                # Test various factory operations
                optimal = factory.get_optimal_optimizer(context)
                stats = factory.get_optimization_statistics()
                optimizers = factory.list_available_optimizers()
                
                thread_results.append({
                    'optimal': optimal,
                    'stats': stats,
                    'optimizers_count': len(optimizers)
                })
            
            with lock:
                results.extend(thread_results)
        
        # Access factory from multiple threads
        num_threads = 10
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(access_factory, i) for i in range(num_threads)]
            [future.result() for future in futures]
        
        # Verify results
        assert len(results) == num_threads * 10
        
        # Verify consistency
        stats_values = [r['stats']['total_optimizers'] for r in results]
        assert all(s == stats_values[0] for s in stats_values), "Stats should be consistent"
        
        optimizers_counts = [r['optimizers_count'] for r in results]
        assert all(c == optimizers_counts[0] for c in optimizers_counts), "Optimizer count should be consistent"
    
    def test_entity_creation_thread_safety(self):
        """Test entity creation thread safety."""
        created_entities = []
        lock = threading.Lock()
        
        def create_entities(entity_type: str, count: int):
            """Create entities from a thread."""
            entities = []
            
            for i in range(count):
                if entity_type == "ad":
                    entity = Ad(
                        name=f"Thread Safe Ad {threading.current_thread().ident}-{i}",
                        ad_type=AdType.IMAGE,
                        platform=Platform.FACEBOOK
                    )
                elif entity_type == "campaign":
                    entity = AdCampaign(
                        name=f"Thread Safe Campaign {threading.current_thread().ident}-{i}",
                        objective="Thread Safety Test",
                        platform=Platform.FACEBOOK
                    )
                else:
                    entity = AdGroup(
                        name=f"Thread Safe Group {threading.current_thread().ident}-{i}"
                    )
                
                entities.append(entity)
            
            with lock:
                created_entities.extend(entities)
            
            return entities
        
        # Create entities from multiple threads
        entity_types = ["ad", "campaign", "group"]
        num_threads_per_type = 5
        entities_per_thread = 10
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            
            for entity_type in entity_types:
                for _ in range(num_threads_per_type):
                    future = executor.submit(create_entities, entity_type, entities_per_thread)
                    futures.append(future)
            
            results = [future.result() for future in futures]
        
        # Verify total count
        expected_total = len(entity_types) * num_threads_per_type * entities_per_thread
        assert len(created_entities) == expected_total
        
        # Verify unique IDs
        entity_ids = [e.id for e in created_entities]
        assert len(entity_ids) == len(set(entity_ids)), "All entity IDs should be unique"


class TestParallelProcessing:
    """Test parallel processing with multiprocessing."""
    
    def test_multiprocess_entity_creation(self):
        """Test entity creation across multiple processes."""
        def create_ads_process(process_id: int, num_ads: int):
            """Create ads in a separate process."""
            ads = []
            
            for i in range(num_ads):
                ad = Ad(
                    name=f"Process {process_id} Ad {i}",
                    description=f"Ad created in process {process_id}",
                    ad_type=AdType.IMAGE,
                    platform=Platform.FACEBOOK
                )
                ads.append({
                    'id': str(ad.id),
                    'name': ad.name,
                    'process_id': process_id
                })
            
            return ads
        
        # Create ads across multiple processes
        num_processes = 4
        ads_per_process = 25
        
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = [
                executor.submit(create_ads_process, i, ads_per_process)
                for i in range(num_processes)
            ]
            
            results = [future.result() for future in futures]
        
        # Flatten results
        all_ads = []
        for process_ads in results:
            all_ads.extend(process_ads)
        
        # Verify total count
        assert len(all_ads) == num_processes * ads_per_process
        
        # Verify unique IDs across processes
        ad_ids = [ad['id'] for ad in all_ads]
        assert len(ad_ids) == len(set(ad_ids)), "Ad IDs should be unique across processes"
        
        # Verify process distribution
        process_counts = {}
        for ad in all_ads:
            pid = ad['process_id']
            process_counts[pid] = process_counts.get(pid, 0) + 1
        
        assert len(process_counts) == num_processes
        assert all(count == ads_per_process for count in process_counts.values())
    
    def test_parallel_optimization_workload(self):
        """Test parallel optimization workload."""
        def run_optimization_batch(batch_id: int, batch_size: int):
            """Run optimization batch in a process."""
            factory = OptimizationFactory()  # Each process gets its own factory
            results = []
            
            for i in range(batch_size):
                context = OptimizationContext(
                    target_entity="ad",
                    entity_id=f"batch-{batch_id}-entity-{i}",
                    optimization_type=OptimizationStrategy.PERFORMANCE,
                    level=OptimizationLevel.STANDARD
                )
                
                optimal = factory.get_optimal_optimizer(context)
                results.append({
                    'batch_id': batch_id,
                    'entity_id': context.entity_id,
                    'optimal_optimizer': optimal
                })
            
            return results
        
        # Run optimization batches in parallel
        num_processes = 4
        batch_size = 20
        
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = [
                executor.submit(run_optimization_batch, i, batch_size)
                for i in range(num_processes)
            ]
            
            results = [future.result() for future in futures]
        
        # Flatten results
        all_results = []
        for batch_results in results:
            all_results.extend(batch_results)
        
        # Verify total count
        assert len(all_results) == num_processes * batch_size
        
        # Verify batch distribution
        batch_counts = {}
        for result in all_results:
            bid = result['batch_id']
            batch_counts[bid] = batch_counts.get(bid, 0) + 1
        
        assert len(batch_counts) == num_processes
        assert all(count == batch_size for count in batch_counts.values())


class TestConcurrencyPerformance:
    """Test performance characteristics under concurrent load."""
    
    def test_concurrent_load_performance(self):
        """Test system performance under concurrent load."""
        results = []
        lock = threading.Lock()
        
        def simulate_user_workflow(user_id: int):
            """Simulate a user workflow."""
            start_time = time.time()
            
            # Create campaign
            campaign = AdCampaign(
                name=f"User {user_id} Campaign",
                objective="Load Test",
                platform=Platform.FACEBOOK
            )
            
            # Create ads
            ads = []
            for i in range(5):
                ad = Ad(
                    name=f"User {user_id} Ad {i}",
                    ad_type=AdType.IMAGE,
                    platform=Platform.FACEBOOK
                )
                campaign.add_ad(ad)
                ads.append(ad)
            
            # Run optimization
            factory = get_optimization_factory()
            for ad in ads:
                context = OptimizationContext(
                    target_entity="ad",
                    entity_id=str(ad.id),
                    optimization_type=OptimizationStrategy.PERFORMANCE,
                    level=OptimizationLevel.STANDARD
                )
                factory.get_optimal_optimizer(context)
            
            end_time = time.time()
            
            with lock:
                results.append({
                    'user_id': user_id,
                    'duration': end_time - start_time,
                    'campaign_id': str(campaign.id),
                    'ads_count': len(ads)
                })
        
        # Simulate concurrent users
        num_users = 20
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(simulate_user_workflow, i) for i in range(num_users)]
            [future.result() for future in futures]
        total_time = time.time() - start_time
        
        # Verify all workflows completed
        assert len(results) == num_users
        
        # Analyze performance
        durations = [r['duration'] for r in results]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        
        # Performance assertions
        assert total_time < 30, f"Total time should be under 30 seconds, was {total_time}"
        assert avg_duration < 5, f"Average workflow duration should be under 5 seconds, was {avg_duration}"
        assert max_duration < 10, f"Max workflow duration should be under 10 seconds, was {max_duration}"
        
        # Verify system stability
        ads_counts = [r['ads_count'] for r in results]
        assert all(count == 5 for count in ads_counts), "All workflows should create 5 ads"
    
    def test_memory_usage_under_concurrency(self):
        """Test memory usage under concurrent operations."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        def memory_intensive_task(task_id: int):
            """Create entities that consume memory."""
            entities = []
            
            # Create many entities
            for i in range(100):
                campaign = AdCampaign(
                    name=f"Memory Test Campaign {task_id}-{i}",
                    objective="Memory Test",
                    platform=Platform.FACEBOOK
                )
                
                for j in range(10):
                    ad = Ad(
                        name=f"Memory Test Ad {task_id}-{i}-{j}",
                        description="Memory test ad with long description " * 10,
                        ad_type=AdType.IMAGE,
                        platform=Platform.FACEBOOK
                    )
                    campaign.add_ad(ad)
                
                entities.append(campaign)
            
            return len(entities)
        
        # Run memory-intensive tasks concurrently
        num_tasks = 10
        
        with ThreadPoolExecutor(max_workers=num_tasks) as executor:
            futures = [executor.submit(memory_intensive_task, i) for i in range(num_tasks)]
            results = [future.result() for future in futures]
        
        # Force garbage collection
        gc.collect()
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Verify tasks completed successfully
        assert all(result == 100 for result in results)
        
        # Memory usage should be reasonable (under 1GB increase)
        assert memory_increase < 1024, f"Memory increase should be under 1GB, was {memory_increase}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

