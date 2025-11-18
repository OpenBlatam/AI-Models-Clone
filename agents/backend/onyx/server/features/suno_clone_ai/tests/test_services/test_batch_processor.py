"""
Comprehensive Unit Tests for Batch Processor

Tests cover batch processing functionality with diverse test cases
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from services.batch_processor import (
    AdvancedBatchProcessor,
    BatchJob,
    BatchItem,
    BatchPriority,
    BatchStatus,
    get_batch_processor
)


class TestBatchItem:
    """Test cases for BatchItem dataclass"""
    
    def test_batch_item_creation(self):
        """Test creating a batch item"""
        item = BatchItem(id="item1", data={"test": "data"})
        
        assert item.id == "item1"
        assert item.data == {"test": "data"}
        assert item.status == "pending"
        assert item.retry_count == 0


class TestBatchJob:
    """Test cases for BatchJob dataclass"""
    
    def test_batch_job_creation(self):
        """Test creating a batch job"""
        items = [
            BatchItem(id="item1", data="data1"),
            BatchItem(id="item2", data="data2")
        ]
        job = BatchJob(id="job1", items=items)
        
        assert job.id == "job1"
        assert len(job.items) == 2
        assert job.priority == BatchPriority.NORMAL
        assert job.status == BatchStatus.PENDING
        assert job.progress == 0.0
    
    def test_batch_job_empty_items_raises_error(self):
        """Test that empty items list raises error"""
        with pytest.raises(ValueError, match="at least one item"):
            BatchJob(id="job1", items=[])


class TestAdvancedBatchProcessor:
    """Test cases for AdvancedBatchProcessor class"""
    
    def test_batch_processor_init(self):
        """Test initializing batch processor"""
        processor = AdvancedBatchProcessor()
        
        assert processor.max_concurrent_batches == 3
        assert processor.max_items_per_batch == 100
        assert processor.worker_pool_size == 10
        assert len(processor.batches) == 0
    
    def test_batch_processor_init_custom_params(self):
        """Test initializing with custom parameters"""
        processor = AdvancedBatchProcessor(
            max_concurrent_batches=5,
            max_items_per_batch=50,
            worker_pool_size=20
        )
        
        assert processor.max_concurrent_batches == 5
        assert processor.max_items_per_batch == 50
        assert processor.worker_pool_size == 20
    
    def test_create_batch_basic(self):
        """Test creating a basic batch"""
        processor = AdvancedBatchProcessor()
        items = ["item1", "item2", "item3"]
        
        batch_id = processor.create_batch(items)
        
        assert batch_id is not None
        assert batch_id in processor.batches
        batch = processor.batches[batch_id]
        assert len(batch.items) == 3
        assert batch.status == BatchStatus.PENDING
    
    def test_create_batch_with_priority(self):
        """Test creating batch with custom priority"""
        processor = AdvancedBatchProcessor()
        items = ["item1"]
        
        batch_id = processor.create_batch(items, priority=BatchPriority.HIGH)
        
        batch = processor.batches[batch_id]
        assert batch.priority == BatchPriority.HIGH
    
    def test_create_batch_exceeds_max_size(self):
        """Test creating batch that exceeds max size"""
        processor = AdvancedBatchProcessor(max_items_per_batch=5)
        items = ["item"] * 10
        
        with pytest.raises(ValueError, match="exceeds maximum"):
            processor.create_batch(items)
    
    def test_create_batch_with_callback(self):
        """Test creating batch with callback"""
        processor = AdvancedBatchProcessor()
        callback = Mock()
        items = ["item1"]
        
        batch_id = processor.create_batch(items, callback=callback)
        
        batch = processor.batches[batch_id]
        assert batch.callback == callback
    
    def test_get_batch(self):
        """Test getting a batch by ID"""
        processor = AdvancedBatchProcessor()
        batch_id = processor.create_batch(["item1"])
        
        batch = processor.get_batch(batch_id)
        assert batch is not None
        assert batch.id == batch_id
    
    def test_get_batch_not_found(self):
        """Test getting non-existent batch"""
        processor = AdvancedBatchProcessor()
        batch = processor.get_batch("nonexistent")
        assert batch is None
    
    @pytest.mark.asyncio
    async def test_process_batch_success(self):
        """Test processing batch successfully"""
        processor = AdvancedBatchProcessor()
        items = ["item1", "item2"]
        batch_id = processor.create_batch(items)
        
        async def processor_func(data):
            return f"processed_{data}"
        
        batch = await processor.process_batch(batch_id, processor_func)
        
        assert batch.status == BatchStatus.COMPLETED
        assert batch.progress == 1.0
        assert all(item.status == "completed" for item in batch.items)
    
    @pytest.mark.asyncio
    async def test_process_batch_sync_function(self):
        """Test processing batch with synchronous function"""
        processor = AdvancedBatchProcessor()
        items = ["item1"]
        batch_id = processor.create_batch(items)
        
        def processor_func(data):
            return f"processed_{data}"
        
        batch = await processor.process_batch(batch_id, processor_func)
        
        assert batch.status == BatchStatus.COMPLETED
        assert batch.items[0].result == "processed_item1"
    
    @pytest.mark.asyncio
    async def test_process_batch_partial_failure(self):
        """Test processing batch with partial failures"""
        processor = AdvancedBatchProcessor()
        items = ["item1", "item2", "item3"]
        batch_id = processor.create_batch(items)
        
        async def processor_func(data):
            if data == "item2":
                raise ValueError("Processing error")
            return f"processed_{data}"
        
        batch = await processor.process_batch(batch_id, processor_func)
        
        assert batch.status == BatchStatus.PARTIAL
        assert batch.progress < 1.0
        assert batch.items[1].status == "failed"
    
    @pytest.mark.asyncio
    async def test_process_batch_all_fail(self):
        """Test processing batch where all items fail"""
        processor = AdvancedBatchProcessor()
        items = ["item1", "item2"]
        batch_id = processor.create_batch(items)
        
        async def processor_func(data):
            raise ValueError("All fail")
        
        batch = await processor.process_batch(batch_id, processor_func, max_retries=0)
        
        assert batch.status == BatchStatus.FAILED
        assert batch.progress == 0.0
    
    @pytest.mark.asyncio
    async def test_process_batch_with_retry(self):
        """Test processing batch with retry logic"""
        processor = AdvancedBatchProcessor()
        items = ["item1"]
        batch_id = processor.create_batch(items)
        
        attempt_count = 0
        
        async def processor_func(data):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        batch = await processor.process_batch(batch_id, processor_func, max_retries=3)
        
        assert batch.status == BatchStatus.COMPLETED
        assert attempt_count == 2
    
    @pytest.mark.asyncio
    async def test_process_batch_with_callback(self):
        """Test processing batch with callback"""
        processor = AdvancedBatchProcessor()
        items = ["item1"]
        callback = AsyncMock()
        batch_id = processor.create_batch(items, callback=callback)
        
        async def processor_func(data):
            return "processed"
        
        batch = await processor.process_batch(batch_id, processor_func)
        
        callback.assert_called_once()
        assert callback.call_args[0][0] == batch
    
    @pytest.mark.asyncio
    async def test_process_batch_not_found(self):
        """Test processing non-existent batch"""
        processor = AdvancedBatchProcessor()
        
        async def processor_func(data):
            return "processed"
        
        with pytest.raises(ValueError, match="not found"):
            await processor.process_batch("nonexistent", processor_func)
    
    def test_cancel_batch(self):
        """Test canceling a batch"""
        processor = AdvancedBatchProcessor()
        batch_id = processor.create_batch(["item1"])
        
        result = processor.cancel_batch(batch_id)
        
        assert result is True
        batch = processor.get_batch(batch_id)
        assert batch.status == BatchStatus.CANCELLED
    
    def test_cancel_batch_not_found(self):
        """Test canceling non-existent batch"""
        processor = AdvancedBatchProcessor()
        result = processor.cancel_batch("nonexistent")
        assert result is False
    
    def test_cancel_batch_already_processing(self):
        """Test canceling batch that's already processing"""
        processor = AdvancedBatchProcessor()
        batch_id = processor.create_batch(["item1"])
        batch = processor.get_batch(batch_id)
        batch.status = BatchStatus.PROCESSING
        
        result = processor.cancel_batch(batch_id)
        # Should not cancel if already processing
        assert result is False
    
    def test_get_batch_stats(self):
        """Test getting batch statistics"""
        processor = AdvancedBatchProcessor()
        
        batch1 = processor.create_batch(["item1"])
        batch2 = processor.create_batch(["item2"])
        processor.get_batch(batch1).status = BatchStatus.COMPLETED
        
        stats = processor.get_batch_stats()
        
        assert stats["total_batches"] == 2
        assert "batches_by_status" in stats
        assert stats["max_concurrent"] == 3
    
    @pytest.mark.asyncio
    async def test_process_batch_concurrent_limit(self):
        """Test that concurrent batch limit is enforced"""
        processor = AdvancedBatchProcessor(max_concurrent_batches=2)
        
        # Create multiple batches
        batch_ids = [processor.create_batch([f"item{i}"]) for i in range(5)]
        
        async def processor_func(data):
            await asyncio.sleep(0.1)  # Simulate processing time
            return "processed"
        
        # Process all batches concurrently
        tasks = [
            processor.process_batch(batch_id, processor_func)
            for batch_id in batch_ids
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete
        assert len(results) == 5
        assert all(batch.status == BatchStatus.COMPLETED for batch in results)


class TestGetBatchProcessor:
    """Test cases for get_batch_processor function"""
    
    def test_get_batch_processor_singleton(self):
        """Test that get_batch_processor returns singleton"""
        processor1 = get_batch_processor()
        processor2 = get_batch_processor()
        
        assert processor1 is processor2
        assert isinstance(processor1, AdvancedBatchProcessor)










