"""
Pipelines de datos con streaming
"""

import torch
from torch.utils.data import Dataset, IterableDataset
from typing import Iterator, List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StreamingDataset(IterableDataset):
    """Dataset con streaming para datos grandes"""
    
    def __init__(
        self,
        data_source: Iterator[Dict[str, Any]],
        transform: Optional[Any] = None
    ):
        self.data_source = data_source
        self.transform = transform
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterador de streaming"""
        for item in self.data_source:
            if self.transform:
                item = self.transform(item)
            yield item


class DataStreamer:
    """Streamer de datos optimizado"""
    
    def __init__(
        self,
        dataset: Dataset,
        batch_size: int = 32,
        prefetch_factor: int = 2
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.prefetch_factor = prefetch_factor
    
    def stream_batches(self) -> Iterator[Dict[str, torch.Tensor]]:
        """Stream de batches"""
        batch = []
        
        for item in self.dataset:
            batch.append(item)
            
            if len(batch) >= self.batch_size:
                yield self._collate_batch(batch)
                batch = []
        
        # Último batch
        if batch:
            yield self._collate_batch(batch)
    
    def _collate_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """Colatea batch"""
        collated = {}
        
        for key in batch[0].keys():
            if isinstance(batch[0][key], torch.Tensor):
                collated[key] = torch.stack([item[key] for item in batch])
            else:
                collated[key] = [item[key] for item in batch]
        
        return collated


class ParallelDataLoader:
    """DataLoader paralelo optimizado"""
    
    def __init__(
        self,
        dataset: Dataset,
        batch_size: int = 32,
        num_workers: int = 4,
        pin_memory: bool = True
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
    
    def create_loader(self) -> torch.utils.data.DataLoader:
        """Crea DataLoader optimizado"""
        return torch.utils.data.DataLoader(
            self.dataset,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            prefetch_factor=2 if self.num_workers > 0 else None,
            persistent_workers=True if self.num_workers > 0 else False,
            drop_last=False
        )




