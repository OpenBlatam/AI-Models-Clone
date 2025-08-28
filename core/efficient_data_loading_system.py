"""
Efficient Data Loading System using PyTorch's DataLoader
======================================================

This module provides efficient data loading capabilities for deep learning training,
with special optimizations for diffusion models and general ML workloads.

Features:
- Multi-process data loading with configurable workers
- Memory-efficient data handling
- Advanced caching and prefetching
- Custom samplers for balanced training
- Data augmentation pipelines
- Distributed training support
- Progress tracking and monitoring
- Specialized datasets for diffusion models
"""

import os
import pickle
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Iterator
from functools import partial
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import (
    DataLoader, Dataset, Sampler, BatchSampler, 
    RandomSampler, SequentialSampler, WeightedRandomSampler,
    DistributedSampler, SubsetRandomSampler
)
from torch.utils.data.dataloader import _BaseDataLoaderIter
import torch.multiprocessing as mp
from PIL import Image
import cv2
from tqdm import tqdm
import logging
import time
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)


class DataConfig:
    """Configuration class for data loading parameters."""
    
    def __init__(
        self,
        batch_size: int = 32,
        num_workers: int = 4,
        pin_memory: bool = True,
        persistent_workers: bool = True,
        prefetch_factor: int = 2,
        drop_last: bool = False,
        shuffle: bool = True,
        collate_fn: Optional[Callable] = None,
        sampler: Optional[Sampler] = None,
        timeout: int = 0,
        multiprocessing_context: str = 'spawn',
        generator: Optional[torch.Generator] = None,
        **kwargs
    ):
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.persistent_workers = persistent_workers
        self.prefetch_factor = prefetch_factor
        self.drop_last = drop_last
        self.shuffle = shuffle
        self.collate_fn = collate_fn
        self.sampler = sampler
        self.timeout = timeout
        self.multiprocessing_context = multiprocessing_context
        self.generator = generator
        self.kwargs = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'batch_size': self.batch_size,
            'num_workers': self.num_workers,
            'pin_memory': self.pin_memory,
            'persistent_workers': self.persistent_workers,
            'prefetch_factor': self.prefetch_factor,
            'drop_last': self.drop_last,
            'shuffle': self.shuffle,
            'collate_fn': self.collate_fn,
            'sampler': self.sampler,
            'timeout': self.timeout,
            'multiprocessing_context': self.multiprocessing_context,
            'generator': self.generator,
            **self.kwargs
        }


class BaseDataset(Dataset, ABC):
    """Abstract base class for datasets with common functionality."""
    
    def __init__(self, transform: Optional[Callable] = None):
        self.transform = transform
        self._cached_data: Dict[str, Any] = {}
        self._cache_enabled: bool = False
    
    @abstractmethod
    def __len__(self) -> int:
        """Return the number of samples in the dataset."""
        pass
    
    @abstractmethod
    def __getitem__(self, idx: int) -> Optional[Dict[str, Any]]:
        """Get a sample by index."""
        pass
    
    def enable_cache(self, max_size: int = 1000):
        """Enable caching for frequently accessed samples."""
        self._cache_enabled = True
        self._max_cache_size = max_size
    
    def disable_cache(self):
        """Disable caching."""
        self._cache_enabled = False
        self._cached_data.clear()
    
    def _get_cached_item(self, idx: int) -> Optional[Dict[str, Any]]:
        """Get item from cache if available."""
        if not self._cache_enabled:
            return None
        
        if idx in self._cached_data:
            return self._cached_data[idx]
        
        # Load item and cache it
        item = self._load_item(idx)
        
        # Implement LRU cache
        if len(self._cached_data) >= self._max_cache_size:
            # Remove oldest item
            oldest_key = next(iter(self._cached_data))
            del self._cached_data[oldest_key]
        
        self._cached_data[idx] = item
        return item
    
    def _load_item(self, idx: int) -> Dict[str, Any]:
        """Load item from source (to be implemented by subclasses)."""
        raise NotImplementedError


class ImageTextDataset(BaseDataset):
    """Dataset for image-text pairs commonly used in diffusion models."""
    
    def __init__(
        self,
        image_paths: List[str],
        texts: List[str],
        transform: Optional[Callable] = None,
        max_text_length: int = 77,
        image_size: Tuple[int, int] = (512, 512)
    ):
        super().__init__(transform)
        self.image_paths = image_paths
        self.texts = texts
        self.max_text_length = max_text_length
        self.image_size = image_size
        
        if len(image_paths) != len(texts):
            raise ValueError("Number of image paths must match number of texts")
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        # Check cache first
        cached_item = self._get_cached_item(idx)
        if cached_item:
            return cached_item
        
        # Load image
        image_path = self.image_paths[idx]
        try:
            image = Image.open(image_path).convert('RGB')
            image = image.resize(self.image_size, Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            # Return a placeholder image
            image = Image.new('RGB', self.image_size, color='gray')
        
        # Load text
        text = self.texts[idx] if idx < len(self.texts) else ""
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        item = {
            'image': image,
            'text': text,
            'image_path': image_path,
            'idx': idx
        }
        
        # Cache the item
        if self._cache_enabled:
            self._cached_data[idx] = item
        
        return item
    
    def _load_item(self, idx: int) -> Dict[str, Any]:
        """Load item from source."""
        # Load image
        image_path = self.image_paths[idx]
        try:
            image = Image.open(image_path).convert('RGB')
            image = image.resize(self.image_size, Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            # Return a placeholder image
            image = Image.new('RGB', self.image_size, color='gray')
        
        # Load text
        text = self.texts[idx] if idx < len(self.texts) else ""
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        item = {
            'image': image,
            'text': text,
            'image_path': image_path,
            'idx': idx
        }
        
        return item


class DiffusionDataset(BaseDataset):
    """Specialized dataset for diffusion model training."""
    
    def __init__(
        self,
        data_dir: str,
        transform: Optional[Callable] = None,
        image_size: Tuple[int, int] = (512, 512),
        max_text_length: int = 77,
        cache_enabled: bool = True
    ):
        super().__init__(transform)
        self.data_dir = Path(data_dir)
        self.image_size = image_size
        self.max_text_length = max_text_length
        
        # Find all image files
        self.image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            self.image_files.extend(self.data_dir.glob(ext))
        
        # Load or create text descriptions
        self.texts = self._load_texts()
        
        if cache_enabled:
            self.enable_cache()
        
        logger.info(f"Loaded {len(self.image_files)} images from {data_dir}")
    
    def _load_texts(self) -> List[str]:
        """Load text descriptions for images."""
        texts = []
        for image_file in self.image_files:
            # Try to find corresponding text file
            text_file = image_file.with_suffix('.txt')
            if text_file.exists():
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        text = f.read().strip()
                except Exception as e:
                    logger.warning(f"Error reading text file {text_file}: {e}")
                    text = f"Image {image_file.stem}"
            else:
                text = f"Image {image_file.stem}"
            texts.append(text)
        return texts
    
    def __len__(self) -> int:
        return len(self.image_files)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        # Check cache first
        cached_item = self._get_cached_item(idx)
        if cached_item:
            return cached_item
        
        # Load image
        image_file = self.image_files[idx]
        try:
            image = Image.open(image_file).convert('RGB')
            image = image.resize(self.image_size, Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"Error loading image {image_file}: {e}")
            image = Image.new('RGB', self.image_size, color='gray')
        
        # Get text
        text = self.texts[idx] if idx < len(self.texts) else ""
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        item = {
            'image': image,
            'text': text,
            'image_path': str(image_file),
            'idx': idx
        }
        
        # Cache the item
        if self._cache_enabled:
            self._cached_data[idx] = item
        
        return item
    
    def _load_item(self, idx: int) -> Dict[str, Any]:
        """Load item from source."""
        # Load image
        image_file = self.image_files[idx]
        try:
            image = Image.open(image_file).convert('RGB')
            image = image.resize(self.image_size, Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"Error loading image {image_file}: {e}")
            image = Image.new('RGB', self.image_size, color='gray')
        
        # Get text
        text = self.texts[idx] if idx < len(self.texts) else ""
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        item = {
            'image': image,
            'text': text,
            'image_path': str(image_file),
            'idx': idx
        }
        
        return item


class CachedDataset(Dataset):
    """Dataset wrapper that provides intelligent caching."""
    
    def __init__(
        self,
        dataset: Dataset,
        cache_dir: str = "./cache",
        cache_size: int = 1000,
        cache_policy: str = "lru"
    ):
        self.dataset = dataset
        self.cache_dir = Path(cache_dir)
        self.cache_size = cache_size
        self.cache_policy = cache_policy
        
        # Create cache directory
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize cache
        self._cache: Dict[int, Any] = {}
        self._cache_order: List[int] = []
        
        logger.info(f"Initialized cache with size {cache_size} and policy {cache_policy}")
    
    def __len__(self) -> int:
        return len(self.dataset)
    
    def __getitem__(self, idx: int) -> Any:
        # Check memory cache first
        if idx in self._cache:
            # Update access order for LRU
            if self.cache_policy == "lru":
                self._cache_order.remove(idx)
                self._cache_order.append(idx)
            return self._cache[idx]
        
        # Check disk cache
        cache_file = self.cache_dir / f"item_{idx}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    item = pickle.load(f)
                # Add to memory cache
                self._add_to_cache(idx, item)
                return item
            except Exception as e:
                logger.warning(f"Error loading from disk cache {cache_file}: {e}")
        
        # Load from dataset
        item = self.dataset[idx]
        
        # Cache the item
        self._add_to_cache(idx, item)
        
        # Save to disk cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(item, f)
        except Exception as e:
            logger.warning(f"Error saving to disk cache {cache_file}: {e}")
        
        return item
    
    def _add_to_cache(self, idx: int, item: Any):
        """Add item to memory cache."""
        if len(self._cache) >= self.cache_size:
            # Remove oldest item
            if self.cache_policy == "lru":
                oldest_idx = self._cache_order.pop(0)
                del self._cache[oldest_idx]
            else:  # fifo
                oldest_idx = next(iter(self._cache))
                del self._cache[oldest_idx]
        
        self._cache[idx] = item
        if self.cache_policy == "lru":
            self._cache_order.append(idx)


class DataLoaderFactory:
    """Factory for creating efficient DataLoaders."""
    
    @staticmethod
    def create_dataloader(
        dataset: Dataset,
        config: DataConfig,
        distributed: bool = False,
        rank: int = 0,
        world_size: int = 1
    ) -> DataLoader:
        """Create an optimized DataLoader."""
        
        # Determine optimal number of workers
        optimal_workers = DataLoaderFactory._get_optimal_workers(config.num_workers)
        
        # Create sampler
        sampler = DataLoaderFactory._create_sampler(
            dataset, config, distributed, rank, world_size
        )
        
        # Create DataLoader
        dataloader = DataLoader(
            dataset=dataset,
            batch_size=config.batch_size,
            sampler=sampler,
            num_workers=optimal_workers,
            pin_memory=config.pin_memory and torch.cuda.is_available(),
            persistent_workers=config.persistent_workers and optimal_workers > 0,
            prefetch_factor=config.prefetch_factor if optimal_workers > 0 else 2,
            drop_last=config.drop_last,
            timeout=config.timeout,
            collate_fn=config.collate_fn,
            multiprocessing_context=config.multiprocessing_context,
            generator=config.generator
        )
        
        logger.info(f"Created DataLoader with {optimal_workers} workers")
        return dataloader
    
    @staticmethod
    def _get_optimal_workers(requested_workers: int) -> int:
        """Get optimal number of workers based on system resources."""
        cpu_count = mp.cpu_count()
        gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        
        # Conservative approach: don't use more than 75% of CPU cores
        max_workers = max(1, int(cpu_count * 0.75))
        
        # If GPU is available, ensure we have enough workers to keep it busy
        if gpu_count > 0:
            min_workers = min(2, max_workers)
        else:
            min_workers = 1
        
        optimal_workers = min(requested_workers, max_workers)
        optimal_workers = max(optimal_workers, min_workers)
        
        return optimal_workers
    
    @staticmethod
    def _create_sampler(
        dataset: Dataset,
        config: DataConfig,
        distributed: bool,
        rank: int,
        world_size: int
    ) -> Optional[Sampler]:
        """Create appropriate sampler for the dataset."""
        if distributed:
            return DistributedSampler(
                dataset,
                num_replicas=world_size,
                rank=rank,
                shuffle=config.shuffle
            )
        elif config.sampler:
            return config.sampler
        elif config.shuffle:
            return RandomSampler(dataset, generator=config.generator)
        else:
            return SequentialSampler(dataset)
    
    @staticmethod
    def create_image_loader(
        image_paths: List[str],
        texts: List[str],
        config: DataConfig,
        target_size: Tuple[int, int] = (512, 512),
        **kwargs
    ) -> DataLoader:
        """Create a DataLoader for image-text pairs."""
        dataset = ImageTextDataset(image_paths, texts, image_size=target_size, **kwargs)
        
        # Set custom collate function for image-text pairs
        if config.collate_fn is None:
            config.collate_fn = partial(image_text_collate_fn, image_size=target_size)
        
        return DataLoaderFactory.create_dataloader(dataset, config)
    
    @staticmethod
    def create_diffusion_loader(
        data_dir: str,
        config: DataConfig,
        image_size: Tuple[int, int] = (512, 512),
        **kwargs
    ) -> DataLoader:
        """Create a DataLoader for diffusion model training."""
        dataset = DiffusionDataset(data_dir, image_size=image_size, **kwargs)
        
        # Set custom collate function for diffusion datasets
        if config.collate_fn is None:
            config.collate_fn = partial(image_text_collate_fn, image_size=image_size)
        
        return DataLoaderFactory.create_dataloader(dataset, config)


class EfficientDataLoader:
    """Enhanced DataLoader with performance monitoring and optimization."""
    
    def __init__(
        self,
        dataset: Dataset,
        config: DataConfig,
        device: Optional[torch.device] = None
    ):
        self.dataset = dataset
        self.config = config
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Create DataLoader
        self.dataloader = self._create_dataloader()
        
        # Performance monitoring
        self.load_times = []
        self.batch_sizes = []
    
    def _create_dataloader(self) -> DataLoader:
        """Create optimized DataLoader."""
        # Determine optimal number of workers
        optimal_workers = self._get_optimal_workers()
        
        # Create sampler if not provided
        sampler = self.config.sampler
        if sampler is None and not self.config.shuffle:
            sampler = SequentialSampler(self.dataset)
        elif sampler is None and self.config.shuffle:
            sampler = RandomSampler(self.dataset, generator=self.config.generator)
        
        # Create DataLoader
        return DataLoader(
            dataset=self.dataset,
            batch_size=self.config.batch_size,
            sampler=sampler,
            num_workers=optimal_workers,
            pin_memory=self.config.pin_memory and self.device.type == 'cuda',
            persistent_workers=self.config.persistent_workers and optimal_workers > 0,
            prefetch_factor=self.config.prefetch_factor if optimal_workers > 0 else 2,
            drop_last=self.config.drop_last,
            timeout=self.config.timeout,
            collate_fn=self.config.collate_fn,
            multiprocessing_context=self.config.multiprocessing_context,
            generator=self.config.generator
        )
    
    def _get_optimal_workers(self) -> int:
        """Get optimal number of workers."""
        cpu_count = mp.cpu_count()
        gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        
        # Conservative approach
        max_workers = max(1, int(cpu_count * 0.75))
        
        if gpu_count > 0:
            min_workers = min(2, max_workers)
        else:
            min_workers = 1
        
        optimal_workers = min(self.config.num_workers, max_workers)
        optimal_workers = max(optimal_workers, min_workers)
        
        return optimal_workers
    
    def to_device(self, batch: Any) -> Any:
        """Move batch to device."""
        if isinstance(batch, torch.Tensor):
            return batch.to(self.device)
        elif isinstance(batch, dict):
            return {k: self.to_device(v) for k, v in batch.items()}
        elif isinstance(batch, (list, tuple)):
            return type(batch)(self.to_device(item) for item in batch)
        else:
            return batch
    
    def __iter__(self):
        """Return iterator for the DataLoader."""
        return iter(self.dataloader)
    
    def __len__(self) -> int:
        """Return number of batches."""
        return len(self.dataloader)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        return {
            'dataset_size': len(self.dataset),
            'batch_size': self.config.batch_size,
            'num_workers': self.config.num_workers,
            'num_batches': len(self.dataloader),
            'device': str(self.device),
            'pin_memory': self.config.pin_memory,
            'persistent_workers': self.config.persistent_workers
        }


class DataLoaderMonitor:
    """Monitor DataLoader performance and memory usage."""
    
    def __init__(self, data_loader: EfficientDataLoader):
        self.data_loader = data_loader
        self.start_time = None
        self.batch_times = []
        self.batch_sizes = []
        self.memory_usage = []
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def monitor_batch(self, batch: Any):
        """Monitor a single batch."""
        batch_start = time.time()
        batch_size = self._get_batch_size(batch)
        
        # Move to device
        batch = self.data_loader.to_device(batch)
        
        batch_time = time.time() - batch_start
        self.batch_times.append(batch_time)
        self.batch_sizes.append(batch_size)
        
        # Monitor memory if CUDA is available
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            self.memory_usage.append(memory_allocated)
        
        return batch
    
    def _get_batch_size(self, batch: Any) -> int:
        """Get batch size from batch."""
        if isinstance(batch, torch.Tensor):
            return batch.size(0)
        elif isinstance(batch, dict):
            # Try to get size from first tensor
            for v in batch.values():
                if isinstance(v, torch.Tensor):
                    return v.size(0)
        elif isinstance(batch, (list, tuple)):
            return len(batch)
        return 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        if not self.batch_times:
            return {}
        
        return {
            'total_batches': len(self.batch_times),
            'total_time': sum(self.batch_times),
            'avg_batch_time': np.mean(self.batch_times),
            'std_batch_time': np.std(self.batch_times),
            'min_batch_time': np.min(self.batch_times),
            'max_batch_time': np.max(self.batch_times),
            'avg_batch_size': np.mean(self.batch_sizes),
            'batches_per_second': len(self.batch_times) / sum(self.batch_times),
            'avg_memory_usage_gb': np.mean(self.memory_usage) if self.memory_usage else 0
        }


def create_collate_fn(pad_value: float = 0.0):
    """Create a custom collate function for variable-length sequences."""
    def collate_fn(batch):
        # Find max length
        max_len = max(len(item) for item in batch)
        
        # Pad sequences
        padded_batch = []
        for item in batch:
            if len(item) < max_len:
                padding = [pad_value] * (max_len - len(item))
                padded_batch.append(item + padding)
            else:
                padded_batch.append(item)
        
        return torch.tensor(padded_batch)
    
    return collate_fn


def create_image_text_collate_fn(image_size: tuple = (512, 512)):
    """Create a custom collate function for image-text pairs."""
    def collate_fn(batch):
        # Separate images and texts
        images = []
        texts = []
        image_paths = []
        indices = []
        
        for item in batch:
            # Convert PIL Image to tensor if needed
            if hasattr(item['image'], 'convert'):
                # PIL Image - convert to tensor
                image = item['image'].convert('RGB')
                image = image.resize(image_size, Image.Resampling.LANCZOS)
                image_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255.0
                images.append(image_tensor)
            elif isinstance(item['image'], torch.Tensor):
                # Already a tensor
                images.append(item['image'])
            else:
                # Convert numpy array to tensor
                image_tensor = torch.from_numpy(np.array(item['image'])).permute(2, 0, 1).float() / 255.0
                images.append(image_tensor)
            
            texts.append(item['text'])
            image_paths.append(item['image_path'])
            indices.append(item['idx'])
        
        # Stack images into a batch tensor
        image_batch = torch.stack(images)
        
        return {
            'image': image_batch,
            'text': texts,
            'image_path': image_paths,
            'idx': torch.tensor(indices)
        }
    
    return collate_fn


def image_text_collate_fn(batch, image_size: tuple = (512, 512)):
    """Standalone collate function for image-text pairs that can be pickled."""
    # Separate images and texts
    images = []
    texts = []
    image_paths = []
    indices = []
    
    for item in batch:
        # Convert PIL Image to tensor if needed
        if hasattr(item['image'], 'convert'):
            # PIL Image - convert to tensor
            image = item['image'].convert('RGB')
            image = image.resize(image_size, Image.Resampling.LANCZOS)
            image_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float() / 255.0
            images.append(image_tensor)
        elif isinstance(item['image'], torch.Tensor):
            # Already a tensor
            images.append(item['image'])
        else:
            # Convert numpy array to tensor
            image_tensor = torch.from_numpy(np.array(item['image'])).permute(2, 0, 1).float() / 255.0
            images.append(image_tensor)
        
        texts.append(item['text'])
        image_paths.append(item['image_path'])
        indices.append(item['idx'])
    
    # Stack images into a batch tensor
    image_batch = torch.stack(images)
    
    return {
        'image': image_batch,
        'text': texts,
        'image_path': image_paths,
        'idx': torch.tensor(indices)
    }


async def get_optimal_batch_size(
    model_size_mb: float,
    gpu_memory_gb: float,
    safety_factor: float = 0.8
) -> int:
    """Calculate optimal batch size based on GPU memory."""
    # Rough estimation: 4 bytes per float32, plus overhead
    bytes_per_sample = model_size_mb * 1024 * 1024 * 4
    available_memory = gpu_memory_gb * 1024 * 1024 * 1024 * safety_factor
    
    optimal_batch_size = int(available_memory / bytes_per_sample)
    return max(1, optimal_batch_size)


def profile_data_loading(
    loader: EfficientDataLoader,
    num_batches: int = 10
) -> Dict[str, float]:
    """Profile data loading performance."""
    
    times = []
    batch_sizes = []
    
    start_time = time.time()
    
    for i, batch in enumerate(loader):
        if i >= num_batches:
            break
        
        batch_start = time.time()
        
        # Get batch size from different batch types
        if isinstance(batch, torch.Tensor):
            batch_size = batch.size(0)
        elif isinstance(batch, dict):
            # Try to get size from first tensor in dict
            batch_size = 0
            for v in batch.values():
                if isinstance(v, torch.Tensor):
                    batch_size = v.size(0)
                    break
            if batch_size == 0:
                # Fallback to length if no tensor found
                batch_size = len(batch) if hasattr(batch, '__len__') else 1
        elif isinstance(batch, (list, tuple)):
            batch_size = len(batch)
        else:
            batch_size = 1
        
        # Move to device to simulate real usage
        batch = loader.to_device(batch)
        
        batch_time = time.time() - batch_start
        times.append(batch_time)
        batch_sizes.append(batch_size)
    
    total_time = time.time() - start_time
    
    return {
        'total_time': total_time,
        'avg_batch_time': np.mean(times),
        'std_batch_time': np.std(times),
        'min_batch_time': np.min(times),
        'max_batch_time': np.max(times),
        'avg_batch_size': np.mean(batch_sizes),
        'batches_per_second': num_batches / total_time,
        'samples_per_second': sum(batch_sizes) / total_time
    }


# Example usage and testing
if __name__ == "__main__":
    # Example: Create a simple image dataset
    image_paths = [
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg"
    ]
    
    # Create configuration
    config = DataConfig(
        batch_size=16,
        num_workers=4,
        pin_memory=True,
        persistent_workers=True
    )
    
    # Create data loader
    loader = DataLoaderFactory.create_image_loader(
        image_paths=image_paths,
        texts=["Image 1", "Image 2", "Image 3"],
        config=config,
        target_size=(256, 256)
    )
    
    # Use the loader
    for batch in loader:
        print(f"Batch keys: {batch.keys()}")
        break
    
    # Get statistics
    print(f"Loader created successfully") 