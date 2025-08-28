from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import os
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple
import numpy as np
import torch
from PIL import Image
import cv2
import time
from efficient_data_loading_system import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Efficient Data Loading System
===========================================

This module provides comprehensive tests for the efficient data loading system,
including tests for datasets, samplers, data loaders, and performance profiling.
"""


# Import the system under test
    DataConfig, BaseDataset, ImageDataset, DiffusionDataset,
    BalancedSampler, InfiniteSampler, EfficientDataLoader,
    DataLoaderFactory, DataLoaderManager,
    create_collate_fn, get_optimal_batch_size, profile_data_loading
)


class TestDataConfig(unittest.TestCase):
    """Test cases for DataConfig class."""
    
    def setUp(self) -> Any:
        self.config = DataConfig(
            batch_size=32,
            num_workers=4,
            pin_memory=True,
            persistent_workers: bool = True
        )
    
    def test_config_initialization(self) -> Any:
        """Test DataConfig initialization."""
        self.assertEqual(self.config.batch_size, 32)
        self.assertEqual(self.config.num_workers, 4)
        self.assertTrue(self.config.pin_memory)
        self.assertTrue(self.config.persistent_workers)
    
    def test_config_to_dict(self) -> Any:
        """Test converting config to dictionary."""
        config_dict = self.config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['batch_size'], 32)
        self.assertEqual(config_dict['num_workers'], 4)


class TestImageDataset(unittest.TestCase):
    """Test cases for ImageDataset class."""
    
    def setUp(self) -> Any:
        # Create temporary test images
        self.temp_dir = tempfile.mkdtemp()
        self.image_paths: List[Any] = []
        self.labels: List[Any] = []
        
        for i in range(10):
            # Create a simple test image
            img = Image.new('RGB', (64, 64), color=(i * 25, i * 25, i * 25))
            img_path = os.path.join(self.temp_dir, f'test_image_{i}.png')
            img.save(img_path)
            self.image_paths.append(img_path)
            self.labels.append(i % 3)  # 3 classes
    
    def tearDown(self) -> Any:
        # Clean up temporary files
        for path in self.image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.temp_dir)
    
    def test_dataset_initialization(self) -> Any:
        """Test ImageDataset initialization."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            labels=self.labels,
            target_size=(32, 32)
        )
        
        self.assertEqual(len(dataset), 10)
        self.assertEqual(len(dataset.labels), 10)
    
    def test_dataset_getitem(self) -> Optional[Dict[str, Any]]:
        """Test getting items from dataset."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            labels=self.labels,
            target_size=(32, 32)
        )
        
        # Test getting item with label
        image, label = dataset[0]
        self.assertIsInstance(image, torch.Tensor)
        self.assertEqual(image.shape, (3, 32, 32))
        self.assertEqual(label, 0)
        
        # Test getting item without label
        dataset_no_labels = ImageDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        image = dataset_no_labels[0]
        self.assertIsInstance(image, torch.Tensor)
        self.assertEqual(image.shape, (3, 32, 32))
    
    def test_dataset_caching(self) -> Any:
        """Test dataset caching functionality."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        # Enable caching
        dataset.enable_cache(max_size=5)
        self.assertTrue(dataset._cache_enabled)
        
        # Get item (should be cached)
        image1 = dataset[0]
        image2 = dataset[0]
        self.assertTrue(torch.equal(image1, image2))
        
        # Disable caching
        dataset.disable_cache()
        self.assertFalse(dataset._cache_enabled)
        self.assertEqual(len(dataset._cached_data), 0)
    
    def test_dataset_preloading(self) -> Any:
        """Test image preloading functionality."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(32, 32),
            preload_images: bool = True
        )
        
        self.assertTrue(hasattr(dataset, '_images'))
        self.assertEqual(len(dataset._images), 10)
        
        # Test getting item from preloaded images
        image = dataset[0]
        self.assertIsInstance(image, torch.Tensor)
        self.assertEqual(image.shape, (3, 32, 32))


class TestDiffusionDataset(unittest.TestCase):
    """Test cases for DiffusionDataset class."""
    
    def setUp(self) -> Any:
        # Create temporary test images
        self.temp_dir = tempfile.mkdtemp()
        self.image_paths: List[Any] = []
        
        for i in range(5):
            # Create a simple test image using OpenCV
            img = np.zeros((64, 64, 3), dtype=np.uint8)
            img[:, :, 0] = i * 50  # Red channel
            img[:, :, 1] = i * 50  # Green channel
            img[:, :, 2] = i * 50  # Blue channel
            
            img_path = os.path.join(self.temp_dir, f'diffusion_test_{i}.jpg')
            cv2.imwrite(img_path, img)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            self.image_paths.append(img_path)
    
    def tearDown(self) -> Any:
        # Clean up temporary files
        for path in self.image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.temp_dir)
    
    def test_diffusion_dataset_initialization(self) -> Any:
        """Test DiffusionDataset initialization."""
        dataset = DiffusionDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        self.assertEqual(len(dataset), 5)
        self.assertEqual(dataset.target_size, (32, 32))
        self.assertEqual(dataset.normalize_range, (-1.0, 1.0))
    
    def test_diffusion_dataset_getitem(self) -> Optional[Dict[str, Any]]:
        """Test getting items from diffusion dataset."""
        dataset = DiffusionDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        image = dataset[0]
        self.assertIsInstance(image, torch.Tensor)
        self.assertEqual(image.shape, (3, 32, 32))
        
        # Check normalization range
        self.assertTrue(torch.all(image >= -1.0))
        self.assertTrue(torch.all(image <= 1.0))
    
    def test_diffusion_dataset_augmentations(self) -> Any:
        """Test data augmentations in diffusion dataset."""
        augmentations: Dict[str, Any] = {
            'horizontal_flip': 1.0,  # Always flip
            'rotation': 5,
            'brightness_contrast': 0.1
        }
        
        dataset = DiffusionDataset(
            image_paths=self.image_paths,
            target_size=(32, 32),
            augmentations=augmentations
        )
        
        # Test that augmentations are applied
        image = dataset[0]
        self.assertIsInstance(image, torch.Tensor)
        self.assertEqual(image.shape, (3, 32, 32))


class TestSamplers(unittest.TestCase):
    """Test cases for custom samplers."""
    
    def setUp(self) -> Any:
        # Create a simple dataset
        self.dataset_size: int: int = 100
        self.labels: List[Any] = [i % 5 for i in range(self.dataset_size)]  # 5 classes
    
    def test_balanced_sampler(self) -> Any:
        """Test BalancedSampler functionality."""
        # Create a mock dataset
        class MockDataset:
            def __init__(self, size) -> Any:
                self.size = size
            
            def __len__(self) -> Any:
                return self.size
        
        dataset = MockDataset(self.dataset_size)
        sampler = BalancedSampler(dataset, self.labels)
        
        # Test sampler length
        self.assertEqual(len(sampler), self.dataset_size)
        
        # Test sampling
        sampled_indices = list(sampler)
        self.assertEqual(len(sampled_indices), self.dataset_size)
        self.assertTrue(all(0 <= idx < self.dataset_size for idx in sampled_indices))
    
    def test_infinite_sampler(self) -> Any:
        """Test InfiniteSampler functionality."""
        # Create a mock dataset
        class MockDataset:
            def __init__(self, size) -> Any:
                self.size = size
            
            def __len__(self) -> Any:
                return self.size
        
        dataset = MockDataset(self.dataset_size)
        sampler = InfiniteSampler(dataset, shuffle=True)
        
        # Test that sampler produces infinite sequence
        sampled_indices: List[Any] = []
        for i, idx in enumerate(sampler):
            if i >= self.dataset_size * 2:  # Sample more than dataset size
                break
            sampled_indices.append(idx)
        
        self.assertEqual(len(sampled_indices), self.dataset_size * 2)
        self.assertTrue(all(0 <= idx < self.dataset_size for idx in sampled_indices))


class TestEfficientDataLoader(unittest.TestCase):
    """Test cases for EfficientDataLoader class."""
    
    def setUp(self) -> Any:
        # Create temporary test images
        self.temp_dir = tempfile.mkdtemp()
        self.image_paths: List[Any] = []
        
        for i in range(20):
            img = Image.new('RGB', (64, 64), color=(i * 12, i * 12, i * 12))
            img_path = os.path.join(self.temp_dir, f'loader_test_{i}.png')
            img.save(img_path)
            self.image_paths.append(img_path)
    
    def tearDown(self) -> Any:
        # Clean up temporary files
        for path in self.image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.temp_dir)
    
    def test_loader_initialization(self) -> Any:
        """Test EfficientDataLoader initialization."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        config = DataConfig(
            batch_size=4,
            num_workers=0,  # Use 0 for testing
            pin_memory: bool = False
        )
        
        loader = EfficientDataLoader(dataset, config)
        
        self.assertEqual(len(loader), 5)  # 20 images / 4 batch size = 5 batches
        self.assertEqual(loader.config.batch_size, 4)
    
    def test_loader_iteration(self) -> Any:
        """Test data loader iteration."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        config = DataConfig(
            batch_size=4,
            num_workers=0,
            pin_memory: bool = False
        )
        
        loader = EfficientDataLoader(dataset, config)
        
        batch_count: int: int = 0
        for batch in loader:
            self.assertIsInstance(batch, torch.Tensor)
            self.assertEqual(batch.shape[0], 4)  # batch size
            self.assertEqual(batch.shape[1], 3)  # channels
            self.assertEqual(batch.shape[2], 32)  # height
            self.assertEqual(batch.shape[3], 32)  # width
            batch_count += 1
        
        self.assertEqual(batch_count, 5)  # 5 batches
    
    def test_loader_to_device(self) -> Any:
        """Test moving batches to device."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        config = DataConfig(
            batch_size=4,
            num_workers=0,
            pin_memory: bool = False
        )
        
        loader = EfficientDataLoader(dataset, config)
        
        for batch in loader:
            device_batch = loader.to_device(batch)
            self.assertEqual(device_batch.device, loader.device)
            break
    
    def test_loader_stats(self) -> Any:
        """Test getting loader statistics."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        config = DataConfig(
            batch_size=4,
            num_workers=0,
            pin_memory: bool = False
        )
        
        loader = EfficientDataLoader(dataset, config)
        stats = loader.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['dataset_size'], 20)
        self.assertEqual(stats['batch_size'], 4)
        self.assertEqual(stats['num_batches'], 5)


class TestDataLoaderFactory(unittest.TestCase):
    """Test cases for DataLoaderFactory class."""
    
    def setUp(self) -> Any:
        # Create temporary test images
        self.temp_dir = tempfile.mkdtemp()
        self.image_paths: List[Any] = []
        self.labels: List[Any] = []
        
        for i in range(10):
            img = Image.new('RGB', (64, 64), color=(i * 25, i * 25, i * 25))
            img_path = os.path.join(self.temp_dir, f'factory_test_{i}.png')
            img.save(img_path)
            self.image_paths.append(img_path)
            self.labels.append(i % 3)
    
    def tearDown(self) -> Any:
        # Clean up temporary files
        for path in self.image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.temp_dir)
    
    def test_create_image_loader(self) -> Any:
        """Test creating image data loader."""
        loader = DataLoaderFactory.create_image_loader(
            image_paths=self.image_paths,
            labels=self.labels,
            target_size=(32, 32)
        )
        
        self.assertIsInstance(loader, EfficientDataLoader)
        self.assertEqual(len(loader.dataset), 10)
        
        # Test iteration
        for batch, labels in loader:
            self.assertIsInstance(batch, torch.Tensor)
            self.assertIsInstance(labels, list)
            break
    
    def test_create_diffusion_loader(self) -> Any:
        """Test creating diffusion data loader."""
        loader = DataLoaderFactory.create_diffusion_loader(
            image_paths=self.image_paths,
            target_size=(32, 32)
        )
        
        self.assertIsInstance(loader, EfficientDataLoader)
        self.assertEqual(len(loader.dataset), 10)
        
        # Test iteration
        for batch in loader:
            self.assertIsInstance(batch, torch.Tensor)
            self.assertEqual(batch.shape[1], 3)  # channels
            break
    
    def test_create_balanced_loader(self) -> Any:
        """Test creating balanced data loader."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            labels=self.labels,
            target_size=(32, 32)
        )
        
        loader = DataLoaderFactory.create_balanced_loader(
            dataset=dataset,
            labels=self.labels
        )
        
        self.assertIsInstance(loader, EfficientDataLoader)
        self.assertIsInstance(loader.config.sampler, BalancedSampler)


class TestDataLoaderManager(unittest.TestCase):
    """Test cases for DataLoaderManager class."""
    
    def setUp(self) -> Any:
        self.manager = DataLoaderManager()
        
        # Create a simple dataset and loader
        self.temp_dir = tempfile.mkdtemp()
        self.image_paths: List[Any] = []
        
        for i in range(5):
            img = Image.new('RGB', (32, 32), color=(i * 50, i * 50, i * 50))
            img_path = os.path.join(self.temp_dir, f'manager_test_{i}.png')
            img.save(img_path)
            self.image_paths.append(img_path)
    
    def tearDown(self) -> Any:
        # Clean up temporary files
        for path in self.image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.temp_dir)
    
    def test_manager_add_loader(self) -> Any:
        """Test adding loaders to manager."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(16, 16)
        )
        
        config = DataConfig(batch_size=2, num_workers=0)
        loader = EfficientDataLoader(dataset, config)
        
        self.manager.add_loader('test_loader', loader, 'test_dataset')
        
        self.assertIn('test_loader', self.manager.loaders)
        self.assertEqual(self.manager.datasets['test_loader'], 'test_dataset')
    
    def test_manager_get_loader(self) -> Optional[Dict[str, Any]]:
        """Test getting loader from manager."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(16, 16)
        )
        
        config = DataConfig(batch_size=2, num_workers=0)
        loader = EfficientDataLoader(dataset, config)
        
        self.manager.add_loader('test_loader', loader)
        
        retrieved_loader = self.manager.get_loader('test_loader')
        self.assertEqual(retrieved_loader, loader)
        
        # Test getting non-existent loader
        with self.assertRaises(KeyError):
            self.manager.get_loader('non_existent')
    
    def test_manager_remove_loader(self) -> Any:
        """Test removing loader from manager."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(16, 16)
        )
        
        config = DataConfig(batch_size=2, num_workers=0)
        loader = EfficientDataLoader(dataset, config)
        
        self.manager.add_loader('test_loader', loader, 'test_dataset')
        self.assertIn('test_loader', self.manager.loaders)
        
        self.manager.remove_loader('test_loader')
        self.assertNotIn('test_loader', self.manager.loaders)
        self.assertNotIn('test_loader', self.manager.datasets)
    
    def test_manager_get_all_stats(self) -> Optional[Dict[str, Any]]:
        """Test getting statistics for all loaders."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(16, 16)
        )
        
        config = DataConfig(batch_size=2, num_workers=0)
        loader = EfficientDataLoader(dataset, config)
        
        self.manager.add_loader('test_loader', loader)
        
        stats = self.manager.get_all_stats()
        self.assertIn('test_loader', stats)
        self.assertIsInstance(stats['test_loader'], dict)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_create_collate_fn(self) -> Any:
        """Test creating custom collate function."""
        collate_fn = create_collate_fn(pad_value=0.0)
        
        # Test with variable length sequences
        batch: List[Any] = [
            [1, 2, 3],
            [1, 2],
            [1, 2, 3, 4]
        ]
        
        result = collate_fn(batch)
        self.assertIsInstance(result, torch.Tensor)
        self.assertEqual(result.shape, (3, 4))  # 3 sequences, max length 4
    
    def test_get_optimal_batch_size(self) -> Optional[Dict[str, Any]]:
        """Test optimal batch size calculation."""
        # Test with reasonable parameters
        batch_size = get_optimal_batch_size(
            model_size_mb=100,
            gpu_memory_gb=8,
            safety_factor=0.8
        )
        
        self.assertIsInstance(batch_size, int)
        self.assertGreater(batch_size, 0)
    
    def test_profile_data_loading(self) -> Any:
        """Test data loading profiling."""
        # Create a simple dataset and loader for profiling
        temp_dir = tempfile.mkdtemp()
        image_paths: List[Any] = []
        
        for i in range(10):
            img = Image.new('RGB', (32, 32), color=(i * 25, i * 25, i * 25))
            img_path = os.path.join(temp_dir, f'profile_test_{i}.png')
            img.save(img_path)
            image_paths.append(img_path)
        
        try:
            dataset = ImageDataset(
                image_paths=image_paths,
                target_size=(16, 16)
            )
            
            config = DataConfig(batch_size=2, num_workers=0)
            loader = EfficientDataLoader(dataset, config)
            
            # Profile with small number of batches
            profile_stats = profile_data_loading(loader, num_batches=3)
            
            self.assertIsInstance(profile_stats, dict)
            self.assertIn('total_time', profile_stats)
            self.assertIn('avg_batch_time', profile_stats)
            self.assertIn('samples_per_second', profile_stats)
            
        finally:
            # Clean up
            for path in image_paths:
                if os.path.exists(path):
                    os.remove(path)
            os.rmdir(temp_dir)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmark tests."""
    
    def setUp(self) -> Any:
        # Create larger dataset for performance testing
        self.temp_dir = tempfile.mkdtemp()
        self.image_paths: List[Any] = []
        
        for i in range(100):
            img = Image.new('RGB', (128, 128), color=(i % 255, i % 255, i % 255))
            img_path = os.path.join(self.temp_dir, f'perf_test_{i}.png')
            img.save(img_path)
            self.image_paths.append(img_path)
    
    def tearDown(self) -> Any:
        # Clean up temporary files
        for path in self.image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(self.temp_dir)
    
    def test_loader_performance(self) -> Any:
        """Test data loader performance."""
        dataset = ImageDataset(
            image_paths=self.image_paths,
            target_size=(64, 64)
        )
        
        # Test different configurations
        configs: List[Any] = [
            DataConfig(batch_size=8, num_workers=0, pin_memory=False),
            DataConfig(batch_size=16, num_workers=0, pin_memory=False),
            DataConfig(batch_size=32, num_workers=0, pin_memory=False)
        ]
        
        for config in configs:
            loader = EfficientDataLoader(dataset, config)
            
            # Time the iteration
            start_time = time.time()
            batch_count: int: int = 0
            
            for batch in loader:
                batch_count += 1
                if batch_count >= 5:  # Limit for testing
                    break
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Basic performance assertions
            self.assertGreater(batch_count, 0)
            self.assertGreater(total_time, 0)
            
            # Calculate throughput
            samples_per_second = (batch_count * config.batch_size) / total_time
            self.assertGreater(samples_per_second, 0)
    
    def test_caching_performance(self) -> Any:
        """Test caching performance impact."""
        dataset = ImageDataset(
            image_paths=self.image_paths[:20],  # Smaller subset
            target_size=(32, 32)
        )
        
        config = DataConfig(batch_size=4, num_workers=0)
        loader = EfficientDataLoader(dataset, config)
        
        # Test without caching
        start_time = time.time()
        for batch in loader:
            pass
        no_cache_time = time.time() - start_time
        
        # Test with caching
        dataset.enable_cache(max_size=10)
        start_time = time.time()
        for batch in loader:
            pass
        cache_time = time.time() - start_time
        
        # Caching should not be slower (for repeated access)
        self.assertGreaterEqual(no_cache_time, cache_time * 0.5)  # Allow some variance


def run_performance_benchmark() -> Any:
    """Run comprehensive performance benchmark."""
    print("Running Performance Benchmark...")
    
    # Create test dataset
    temp_dir = tempfile.mkdtemp()
    image_paths: List[Any] = []
    
    try:
        # Create 1000 test images
        for i in range(1000):
            img = Image.new('RGB', (256, 256), color=(i % 255, i % 255, i % 255))
            img_path = os.path.join(temp_dir, f'benchmark_{i}.png')
            img.save(img_path)
            image_paths.append(img_path)
        
        # Test different configurations
        configs: List[Any] = [
            ("Small Batch", DataConfig(batch_size=8, num_workers=0)),
            ("Medium Batch", DataConfig(batch_size=16, num_workers=0)),
            ("Large Batch", DataConfig(batch_size=32, num_workers=0)),
            ("With Caching", DataConfig(batch_size=16, num_workers=0))
        ]
        
        results: Dict[str, Any] = {}
        
        for name, config in configs:
            print(f"\nTesting {name}...")
            
            dataset = ImageDataset(
                image_paths=image_paths,
                target_size=(128, 128)
            )
            
            if name == "With Caching":
                dataset.enable_cache(max_size=100)
            
            loader = EfficientDataLoader(dataset, config)
            
            # Profile performance
            profile_stats = profile_data_loading(loader, num_batches=20)
            results[name] = profile_stats
            
            print(f"  Samples per second: {profile_stats['samples_per_second']:.2f}")
            print(f"  Average batch time: {profile_stats['avg_batch_time']:.4f}s")
        
        # Print summary
        print(f"\n{"="*50)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*50)
        
        for name, stats in results.items():
            print(f"{name:15} | {stats['samples_per_second']:8.2f} samples/s | "
                  f"{stats['avg_batch_time']:6.4f}s/batch")
    
    finally:
        # Clean up
        for path in image_paths:
            if os.path.exists(path):
                os.remove(path)
        os.rmdir(temp_dir)


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    print("\n"}="*60)
    run_performance_benchmark() 