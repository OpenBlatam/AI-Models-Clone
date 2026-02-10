"""
Data loading optimizado con prefetch y caching
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Any, Optional, Callable
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class OptimizedIdentityDataset(Dataset):
    """Dataset optimizado para identidades"""
    
    def __init__(
        self,
        texts: List[str],
        tokenizer: Any,
        max_length: int = 512,
        cache_encodings: bool = True
    ):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.cache_encodings = cache_encodings
        self._cache = {}
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Obtiene item con caching"""
        text = self.texts[idx]
        
        # Cache encodings si está habilitado
        if self.cache_encodings and idx in self._cache:
            return self._cache[idx]
        
        # Tokenizar
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        result = {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten()
        }
        
        # Guardar en cache
        if self.cache_encodings:
            self._cache[idx] = result
        
        return result


def create_optimized_dataloader(
    dataset: Dataset,
    batch_size: int = 8,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True,
    prefetch_factor: int = 2,
    persistent_workers: bool = True
) -> DataLoader:
    """
    Crea DataLoader optimizado
    
    Args:
        dataset: Dataset
        batch_size: Tamaño de batch
        shuffle: Si mezclar
        num_workers: Número de workers
        pin_memory: Pin memory para GPU
        prefetch_factor: Factor de prefetch
        persistent_workers: Mantener workers entre épocas
        
    Returns:
        DataLoader optimizado
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
        persistent_workers=persistent_workers if num_workers > 0 else False,
        drop_last=True  # Para batches consistentes
    )


class DataPrefetcher:
    """Prefetcher para data loading asíncrono"""
    
    def __init__(self, loader: DataLoader, device: str = "cuda"):
        self.loader = loader
        self.device = device
        self.stream = torch.cuda.Stream() if device == "cuda" else None
        self.next_batch = None
        self._prefetch()
    
    def _prefetch(self):
        """Prefetch siguiente batch"""
        try:
            self.next_batch = next(self.iter_loader)
        except StopIteration:
            self.next_batch = None
            return
        
        if self.stream:
            with torch.cuda.stream(self.stream):
                self.next_batch = self._move_to_device(self.next_batch)
    
    def _move_to_device(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Mueve batch a device"""
        return {
            k: v.to(self.device, non_blocking=True) if isinstance(v, torch.Tensor) else v
            for k, v in batch.items()
        }
    
    def __iter__(self):
        self.iter_loader = iter(self.loader)
        self._prefetch()
        return self
    
    def __next__(self):
        if self.next_batch is None:
            raise StopIteration
        
        batch = self.next_batch
        
        if self.stream:
            torch.cuda.current_stream().wait_stream(self.stream)
        
        self._prefetch()
        
        return batch




