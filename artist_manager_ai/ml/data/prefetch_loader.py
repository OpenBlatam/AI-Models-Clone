"""
Prefetch DataLoader
===================

DataLoader with aggressive prefetching for maximum speed.
"""

import torch
from torch.utils.data import DataLoader
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def create_prefetch_dataloader(
    dataset: torch.utils.data.Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: Optional[int] = None,
    pin_memory: Optional[bool] = None,
    prefetch_factor: int = 4,
    persistent_workers: bool = True,
    drop_last: bool = False
) -> DataLoader:
    """
    Create DataLoader with aggressive prefetching.
    
    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of workers (auto-optimize if None)
        pin_memory: Pin memory (auto-detect if None)
        prefetch_factor: Prefetch factor (higher = more prefetching)
        persistent_workers: Keep workers alive
        drop_last: Drop last incomplete batch
    
    Returns:
        Optimized DataLoader
    """
    # Auto-optimize workers
    if num_workers is None:
        num_workers = min(8, torch.get_num_threads(), (torch.cuda.device_count() * 4) if torch.cuda.is_available() else 4)
    
    # Auto-detect pin_memory
    if pin_memory is None:
        pin_memory = torch.cuda.is_available()
    
    # Create DataLoader with aggressive settings
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
        persistent_workers=persistent_workers if num_workers > 0 else False,
        drop_last=drop_last,
        pin_memory_device="cuda" if pin_memory and torch.cuda.is_available() else None,
        # Additional optimizations
        generator=torch.Generator() if shuffle else None
    )
    
    logger.info(
        f"Prefetch DataLoader created: "
        f"workers={num_workers}, prefetch={prefetch_factor}, "
        f"pin_memory={pin_memory}"
    )
    
    return dataloader


class AsyncDataLoader:
    """Async DataLoader for even faster data loading."""
    
    def __init__(
        self,
        dataloader: DataLoader,
        queue_size: int = 10
    ):
        """
        Initialize async DataLoader.
        
        Args:
            dataloader: Base DataLoader
            queue_size: Queue size for prefetching
        """
        self.dataloader = dataloader
        self.queue_size = queue_size
        self._queue = None
        self._iterator = None
    
    def __iter__(self):
        """Start async iteration."""
        import queue
        import threading
        
        self._queue = queue.Queue(maxsize=self.queue_size)
        self._iterator = iter(self.dataloader)
        self._stop = False
        
        def producer():
            try:
                for batch in self._iterator:
                    if self._stop:
                        break
                    self._queue.put(batch)
                self._queue.put(None)  # Sentinel
            except Exception as e:
                logger.error(f"Producer error: {str(e)}")
                self._queue.put(None)
        
        thread = threading.Thread(target=producer, daemon=True)
        thread.start()
        
        return self
    
    def __next__(self):
        """Get next batch."""
        batch = self._queue.get()
        if batch is None:
            raise StopIteration
        return batch
    
    def __len__(self):
        """Get length."""
        return len(self.dataloader)




