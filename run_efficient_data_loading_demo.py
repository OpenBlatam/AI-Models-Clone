#!/usr/bin/env python3
"""
Efficient Data Loading System Demo
==================================

This script demonstrates the efficient data loading system using PyTorch's DataLoader
with optimizations for diffusion models and general ML workloads.

Features demonstrated:
- Multi-process data loading with configurable workers
- Memory-efficient data handling with caching
- Custom datasets for image-text pairs
- Performance monitoring and optimization
- Distributed training support
- Advanced samplers and collate functions
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from functools import partial
import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Import our efficient data loading system
from efficient_data_loading_system import (
    DataConfig,
    ImageTextDataset,
    DiffusionDataset,
    CachedDataset,
    DataLoaderFactory,
    EfficientDataLoader,
    DataLoaderMonitor,
    create_collate_fn,
    image_text_collate_fn,
    profile_data_loading
)


def create_sample_images(num_images: int = 10, size: tuple = (256, 256)) -> List[str]:
    """Create sample images for testing."""
    temp_dir = tempfile.mkdtemp()
    image_paths = []
    
    print(f"Creating {num_images} sample images in {temp_dir}")
    
    for i in range(num_images):
        # Create a simple image with different colors
        color = (i * 25, (i * 37) % 255, (i * 51) % 255)
        image = Image.new('RGB', size, color)
        
        # Add some text to make it more interesting
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        # Try to use a default font, fall back to basic if not available
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"Image {i+1}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Save image
        image_path = os.path.join(temp_dir, f"sample_{i+1}.jpg")
        image.save(image_path, "JPEG", quality=95)
        image_paths.append(image_path)
    
    return image_paths, temp_dir


def create_sample_texts(num_texts: int = 10) -> List[str]:
    """Create sample text descriptions."""
    sample_texts = [
        "A beautiful landscape with mountains and trees",
        "A cute cat playing with a ball of yarn",
        "A modern city skyline at sunset",
        "A delicious plate of pasta with herbs",
        "A vintage car parked on a quiet street",
        "A colorful garden with blooming flowers",
        "A cozy coffee shop interior",
        "A majestic eagle soaring through the sky",
        "A peaceful lake reflecting the mountains",
        "A vibrant street art mural on a wall"
    ]
    
    # Extend if we need more texts
    while len(sample_texts) < num_texts:
        sample_texts.extend(sample_texts[:num_texts - len(sample_texts)])
    
    return sample_texts[:num_texts]


def demo_basic_data_loading():
    """Demonstrate basic data loading functionality."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Data Loading")
    print("="*60)
    
    # Create sample data
    image_paths, temp_dir = create_sample_images(8, (256, 256))
    texts = create_sample_texts(8)
    
    try:
        # Create configuration
        config = DataConfig(
            batch_size=4,
            num_workers=2,
            pin_memory=True,
            persistent_workers=True,
            prefetch_factor=2,
            shuffle=True,
            collate_fn=partial(image_text_collate_fn, image_size=(256, 256))
        )
        
        print(f"Configuration: {config.to_dict()}")
        
        # Create dataset
        dataset = ImageTextDataset(
            image_paths=image_paths,
            texts=texts,
            image_size=(256, 256)
        )
        
        print(f"Dataset created with {len(dataset)} samples")
        
        # Create DataLoader using factory
        dataloader = DataLoaderFactory.create_dataloader(dataset, config)
        
        print(f"DataLoader created with {len(dataloader)} batches")
        
        # Test loading
        print("\nTesting data loading...")
        for i, batch in enumerate(dataloader):
            print(f"Batch {i+1}:")
            print(f"  - Keys: {list(batch.keys())}")
            print(f"  - Image type: {type(batch['image'])}")
            print(f"  - Text: {batch['text']}")
            print(f"  - Image path: {batch['image_path']}")
            
            if i >= 1:  # Only show first 2 batches
                break
        
        # Test with EfficientDataLoader
        print("\nCreating EfficientDataLoader...")
        efficient_loader = EfficientDataLoader(dataset, config)
        
        print(f"EfficientDataLoader stats: {efficient_loader.get_stats()}")
        
        # Test device transfer
        if torch.cuda.is_available():
            print("Testing GPU transfer...")
            for batch in efficient_loader:
                gpu_batch = efficient_loader.to_device(batch)
                print(f"  - GPU batch keys: {list(gpu_batch.keys())}")
                break
        else:
            print("CUDA not available, skipping GPU transfer test")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")


def demo_caching_system():
    """Demonstrate the caching system."""
    print("\n" + "="*60)
    print("DEMO 2: Caching System")
    print("="*60)
    
    # Create sample data
    image_paths, temp_dir = create_sample_images(6, (128, 128))
    texts = create_sample_texts(6)
    
    try:
        # Create base dataset
        base_dataset = ImageTextDataset(
            image_paths=image_paths,
            texts=texts,
            image_size=(128, 128)
        )
        
        # Create cached dataset
        cached_dataset = CachedDataset(
            base_dataset,
            cache_dir="./demo_cache",
            cache_size=3,
            cache_policy="lru"
        )
        
        print(f"Base dataset: {len(base_dataset)} samples")
        print(f"Cached dataset: {len(cached_dataset)} samples")
        print(f"Cache directory: ./demo_cache")
        print(f"Cache size: 3 items, Policy: LRU")
        
        # Test caching behavior
        config = DataConfig(batch_size=2, num_workers=1, collate_fn=partial(image_text_collate_fn, image_size=(128, 128)))
        dataloader = DataLoader(cached_dataset, batch_size=2, shuffle=False, collate_fn=partial(image_text_collate_fn, image_size=(128, 128)))
        
        print("\nTesting caching behavior...")
        
        # First pass - should cache items
        print("First pass (caching items):")
        for i, batch in enumerate(dataloader):
            print(f"  Batch {i+1}: {batch['image_path']}")
            if i >= 2:  # Show first 3 batches
                break
        
        # Second pass - should use cache
        print("\nSecond pass (using cache):")
        for i, batch in enumerate(dataloader):
            print(f"  Batch {i+1}: {batch['image_path']}")
            if i >= 2:  # Show first 3 batches
                break
        
        # Check cache directory
        cache_files = list(Path("./demo_cache").glob("*.pkl"))
        print(f"\nCache files created: {len(cache_files)}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        if os.path.exists("./demo_cache"):
            shutil.rmtree("./demo_cache")
        print("Cleaned up temporary files")


def demo_diffusion_dataset():
    """Demonstrate the diffusion dataset."""
    print("\n" + "="*60)
    print("DEMO 3: Diffusion Dataset")
    print("="*60)
    
    # Create a temporary directory structure
    temp_dir = tempfile.mkdtemp()
    images_dir = os.path.join(temp_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    try:
        # Create sample images
        image_paths, _ = create_sample_images(6, (512, 512))
        
        # Move images to the images directory
        for i, src_path in enumerate(image_paths):
            dst_path = os.path.join(images_dir, f"diffusion_{i+1}.jpg")
            shutil.copy2(src_path, dst_path)
            
            # Create corresponding text file
            text_file = dst_path.replace('.jpg', '.txt')
            with open(text_file, 'w') as f:
                f.write(f"Diffusion training image {i+1}")
        
        # Create text files for some images
        text_files = [
            "A serene mountain landscape at dawn",
            "An abstract digital art piece",
            "A vintage photograph with warm tones",
            "A modern architectural design",
            "A natural forest scene with sunlight",
            "An artistic interpretation of urban life"
        ]
        
        for i, text in enumerate(text_files):
            text_file = os.path.join(images_dir, f"diffusion_{i+1}.txt")
            with open(text_file, 'w') as f:
                f.write(text)
        
        print(f"Created diffusion dataset structure in {images_dir}")
        print(f"Images: {len(os.listdir(images_dir)) // 2} pairs")
        
        # Create diffusion dataset
        diffusion_dataset = DiffusionDataset(
            data_dir=images_dir,
            image_size=(512, 512),
            cache_enabled=True
        )
        
        print(f"Diffusion dataset loaded: {len(diffusion_dataset)} samples")
        
        # Test loading
        config = DataConfig(batch_size=2, num_workers=1, collate_fn=partial(image_text_collate_fn, image_size=(512, 512)))
        dataloader = DataLoader(diffusion_dataset, batch_size=2, shuffle=False, collate_fn=partial(image_text_collate_fn, image_size=(512, 512)))
        
        print("\nTesting diffusion dataset loading...")
        for i, batch in enumerate(dataloader):
            print(f"Batch {i+1}:")
            print(f"  - Image path: {batch['image_path']}")
            print(f"  - Text: {batch['text']}")
            print(f"  - Image type: {type(batch['image'])}")
            
            if i >= 1:  # Show first 2 batches
                break
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("Cleaned up temporary diffusion dataset")


def demo_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n" + "="*60)
    print("DEMO 4: Performance Monitoring")
    print("="*60)
    
    # Create sample data
    image_paths, temp_dir = create_sample_images(12, (128, 128))
    texts = create_sample_texts(12)
    
    try:
        # Create dataset and loader
        dataset = ImageTextDataset(image_paths, texts, image_size=(128, 128))
        config = DataConfig(batch_size=4, num_workers=2, pin_memory=True, collate_fn=partial(image_text_collate_fn, image_size=(128, 128)))
        efficient_loader = EfficientDataLoader(dataset, config)
        
        print(f"Created loader with {len(efficient_loader)} batches")
        
        # Test performance monitoring
        print("\nTesting performance monitoring...")
        
        with DataLoaderMonitor(efficient_loader) as monitor:
            for i, batch in enumerate(efficient_loader):
                # Monitor this batch
                monitored_batch = monitor.monitor_batch(batch)
                
                # Simulate some processing
                time.sleep(0.01)
                
                if i >= 3:  # Process 4 batches
                    break
        
        # Get monitoring stats
        stats = monitor.get_stats()
        print(f"\nPerformance Statistics:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
        
        # Profile data loading
        print("\nProfiling data loading...")
        profile_stats = profile_data_loading(efficient_loader, num_batches=3)
        
        print(f"Profile Statistics:")
        for key, value in profile_stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("Cleaned up temporary files")


def demo_advanced_features():
    """Demonstrate advanced features."""
    print("\n" + "="*60)
    print("DEMO 5: Advanced Features")
    print("="*60)
    
    # Create sample data
    image_paths, temp_dir = create_sample_images(10, (256, 256))
    texts = create_sample_texts(10)
    
    try:
        # Test different configurations
        configs = [
            ("Standard", DataConfig(batch_size=4, num_workers=2, collate_fn=partial(image_text_collate_fn, image_size=(256, 256)))),
            ("High Performance", DataConfig(
                batch_size=8, 
                num_workers=4, 
                pin_memory=True, 
                persistent_workers=True,
                prefetch_factor=3,
                collate_fn=partial(image_text_collate_fn, image_size=(256, 256))
            )),
            ("Memory Efficient", DataConfig(
                batch_size=2, 
                num_workers=1, 
                pin_memory=False, 
                persistent_workers=False,
                collate_fn=partial(image_text_collate_fn, image_size=(256, 256))
            ))
        ]
        
        for config_name, config in configs:
            print(f"\n{config_name} Configuration:")
            print(f"  - Batch size: {config.batch_size}")
            print(f"  - Workers: {config.num_workers}")
            print(f"  - Pin memory: {config.pin_memory}")
            print(f"  - Persistent workers: {config.persistent_workers}")
            print(f"  - Prefetch factor: {config.prefetch_factor}")
            
            # Create dataset and loader
            dataset = ImageTextDataset(image_paths, texts, image_size=(256, 256))
            dataloader = DataLoaderFactory.create_dataloader(dataset, config)
            
            # Test loading
            start_time = time.time()
            batch_count = 0
            for batch in dataloader:
                batch_count += 1
                if batch_count >= 3:  # Test 3 batches
                    break
            
            load_time = time.time() - start_time
            print(f"  - Loaded {batch_count} batches in {load_time:.4f}s")
            print(f"  - Average time per batch: {load_time/batch_count:.4f}s")
        
        # Test custom collate function
        print(f"\nTesting custom collate function...")
        
        # Create a simple dataset with variable-length sequences
        class SequenceDataset(torch.utils.data.Dataset):
            def __init__(self, sequences):
                self.sequences = sequences
            
            def __len__(self):
                return len(self.sequences)
            
            def __getitem__(self, idx):
                return self.sequences[idx]
        
        # Create sequences of different lengths
        sequences = [
            [1, 2, 3],
            [1, 2, 3, 4, 5],
            [1, 2],
            [1, 2, 3, 4, 5, 6, 7]
        ]
        
        seq_dataset = SequenceDataset(sequences)
        collate_fn = create_collate_fn(pad_value=0)
        
        seq_loader = DataLoader(
            seq_dataset, 
            batch_size=2, 
            collate_fn=collate_fn,
            shuffle=False
        )
        
        print("  - Variable-length sequences:")
        for i, batch in enumerate(seq_loader):
            print(f"    Batch {i+1}: shape {batch.shape}, content {batch.tolist()}")
            if i >= 1:
                break
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("Cleaned up temporary files")


def demo_distributed_support():
    """Demonstrate distributed training support."""
    print("\n" + "="*60)
    print("DEMO 6: Distributed Training Support")
    print("="*60)
    
    # Create sample data
    image_paths, temp_dir = create_sample_images(8, (128, 128))
    texts = create_sample_texts(8)
    
    try:
        dataset = ImageTextDataset(image_paths, texts, image_size=(128, 128))
        
        # Test different distributed scenarios
        scenarios = [
            ("Single GPU", False, 0, 1),
            ("Distributed (2 processes)", True, 0, 2),
            ("Distributed (4 processes)", True, 0, 4)
        ]
        
        for scenario_name, distributed, rank, world_size in scenarios:
            print(f"\n{scenario_name}:")
            
            config = DataConfig(
                batch_size=2,
                num_workers=1,
                shuffle=True,
                collate_fn=partial(image_text_collate_fn, image_size=(128, 128))
            )
            
            try:
                dataloader = DataLoaderFactory.create_dataloader(
                    dataset, config, distributed, rank, world_size
                )
                
                print(f"  - Created DataLoader successfully")
                print(f"  - Number of batches: {len(dataloader)}")
                
                # Test loading (just first batch)
                for batch in dataloader:
                    print(f"  - First batch keys: {list(batch.keys())}")
                    break
                    
            except Exception as e:
                print(f"  - Error: {e}")
        
        print(f"\nNote: Distributed training requires proper setup with torch.distributed")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("Cleaned up temporary files")


def main():
    """Run all demos."""
    print("Efficient Data Loading System Demo")
    print("=" * 60)
    print("This demo showcases the efficient data loading system using PyTorch's DataLoader")
    print("with optimizations for diffusion models and general ML workloads.")
    
    # Check PyTorch version
    print(f"\nPyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
    
    # Run demos
    try:
        demo_basic_data_loading()
        demo_caching_system()
        demo_diffusion_dataset()
        demo_performance_monitoring()
        demo_advanced_features()
        demo_distributed_support()
        
        print("\n" + "="*60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nThe efficient data loading system provides:")
        print("✅ Multi-process data loading with configurable workers")
        print("✅ Memory-efficient data handling with intelligent caching")
        print("✅ Specialized datasets for diffusion models")
        print("✅ Performance monitoring and optimization")
        print("✅ Distributed training support")
        print("✅ Advanced samplers and collate functions")
        print("✅ GPU memory optimization")
        print("✅ Flexible configuration options")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
