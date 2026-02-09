"""
Ultra-Fast Request Batcher
Intelligent request batching and deduplication
"""

import asyncio
import logging
import time
import hashlib
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BatchedRequest:
    """Represents a batched request"""
    key: str
    func: Callable
    args: tuple
    kwargs: dict
    future: asyncio.Future
    timestamp: float


class RequestBatcher:
    """
    Ultra-fast request batcher
    
    Features:
    - Request deduplication
    - Intelligent batching
    - Request coalescing
    - Batch size optimization
    - Time-based batching
    """
    
    def __init__(
        self,
        batch_window: float = 0.01,  # 10ms window
        max_batch_size: int = 50,
        enable_deduplication: bool = True
    ):
        self.batch_window = batch_window
        self.max_batch_size = max_batch_size
        self.enable_deduplication = enable_deduplication
        
        self._batches: Dict[str, deque] = defaultdict(deque)
        self._pending_requests: Dict[str, BatchedRequest] = {}
        self._batch_tasks: Dict[str, asyncio.Task] = {}
        self._dedupe_cache: Dict[str, Tuple[Any, float]] = {}
        self._dedupe_ttl = 1.0  # 1 second deduplication window
        
        logger.info(f"✅ Request batcher initialized (window: {batch_window}s, max_size: {max_batch_size})")
    
    async def batch_request(
        self,
        key: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Batch a request for execution
        
        Args:
            key: Unique key for batching
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        # Check for duplicate requests
        if self.enable_deduplication:
            dedupe_key = self._get_dedupe_key(key, args, kwargs)
            if dedupe_key in self._dedupe_cache:
                result, cached_time = self._dedupe_cache[dedupe_key]
                if time.time() - cached_time < self._dedupe_ttl:
                    logger.debug(f"Request deduplicated: {key}")
                    return result
                else:
                    del self._dedupe_cache[dedupe_key]
        
        # Create future for result
        future = asyncio.Future()
        
        # Create batched request
        request = BatchedRequest(
            key=key,
            func=func,
            args=args,
            kwargs=kwargs,
            future=future,
            timestamp=time.time()
        )
        
        # Add to batch
        self._batches[key].append(request)
        
        # Start batch processing if not already started
        if key not in self._batch_tasks or self._batch_tasks[key].done():
            self._batch_tasks[key] = asyncio.create_task(self._process_batch(key))
        
        # Wait for result
        return await future
    
    async def _process_batch(self, key: str):
        """Process a batch of requests"""
        await asyncio.sleep(self.batch_window)
        
        batch = self._batches[key]
        if not batch:
            return
        
        # Get requests from batch
        requests_to_process: List[BatchedRequest] = []
        while batch and len(requests_to_process) < self.max_batch_size:
            requests_to_process.append(batch.popleft())
        
        # Process requests
        if len(requests_to_process) == 1:
            # Single request - execute directly
            req = requests_to_process[0]
            try:
                result = await req.func(*req.args, **req.kwargs)
                req.future.set_result(result)
                
                # Cache for deduplication
                if self.enable_deduplication:
                    dedupe_key = self._get_dedupe_key(req.key, req.args, req.kwargs)
                    self._dedupe_cache[dedupe_key] = (result, time.time())
            except Exception as e:
                req.future.set_exception(e)
        else:
            # Multiple requests - batch execute
            tasks = [req.func(*req.args, **req.kwargs) for req in requests_to_process]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Set results
            for req, result in zip(requests_to_process, results):
                if isinstance(result, Exception):
                    req.future.set_exception(result)
                else:
                    req.future.set_result(result)
                    
                    # Cache for deduplication
                    if self.enable_deduplication:
                        dedupe_key = self._get_dedupe_key(req.key, req.args, req.kwargs)
                        self._dedupe_cache[dedupe_key] = (result, time.time())
        
        # Cleanup old dedupe cache entries
        self._cleanup_dedupe_cache()
    
    def _get_dedupe_key(self, key: str, args: tuple, kwargs: dict) -> str:
        """Generate deduplication key"""
        import json
        key_data = json.dumps({
            "key": key,
            "args": args,
            "kwargs": kwargs
        }, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _cleanup_dedupe_cache(self):
        """Cleanup expired dedupe cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, cached_time) in self._dedupe_cache.items()
            if current_time - cached_time > self._dedupe_ttl
        ]
        for key in expired_keys:
            del self._dedupe_cache[key]
    
    async def flush(self, key: Optional[str] = None):
        """
        Flush pending batches
        
        Args:
            key: Specific batch key or None for all
        """
        if key:
            if key in self._batch_tasks and not self._batch_tasks[key].done():
                await self._batch_tasks[key]
        else:
            # Flush all
            tasks = [task for task in self._batch_tasks.values() if not task.done()]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)


# Global batcher instance
_batcher: Optional[RequestBatcher] = None


def get_request_batcher() -> RequestBatcher:
    """Get global request batcher instance"""
    global _batcher
    if _batcher is None:
        _batcher = RequestBatcher()
    return _batcher















