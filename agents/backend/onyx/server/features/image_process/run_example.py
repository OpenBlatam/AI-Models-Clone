#!/usr/bin/env python3
"""
Example script demonstrating the Advanced Image Processing System
"""

import torch
import logging
import os
from pathlib import Path
import tempfile
import shutil

# Import our system components
from main_integration import AdvancedImageProcessor
from advanced_optimization_system import AdvancedOptimizationSystem
from advanced_loss_functions import AdvancedLossFunctions, RadioFrequencyOptimizer
from data_loader_optimized import OptimizedImageDataset, AdvancedAugmentationPipeline
from performance_monitor import PerformanceMonitor, TrainingMetricsTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_dummy_data(num_samples: int = 100, image_size: tuple = (256, 256)):
    """Create dummy training data for demonstration"""
    import numpy as np
    from PIL import Image
    
    # Create directories
    train_dir = Path("dummy_data/train")
    train_target_dir = Path("dummy_data/train_target")
    val_dir = Path("dummy_data/val")
    val_target_dir = Path("dummy_data/val_target")
    
    for dir_path in [train_dir, train_target_dir, val_dir, val_target_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create dummy images
    for i in range(num_samples):
        # Create random image
        img_array = np.random.randint(0, 255, (*image_size, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        # Create target (slightly modified version)
        target_array = np.random.randint(0, 255, (*image_size, 3), dtype=np.uint8)
        target = Image.fromarray(target_array)
        
        # Save to appropriate directories
        if i < int(num_samples * 0.8):  # 80% training
            img.save(train_dir / f"image_{i:04d}.png")
            target.save(train_target_dir / f"image_{i:04d}.png")
        else:  # 20% validation
            img.save(val_dir / f"image_{i:04d}.png")
            target.save(val_target_dir / f"image_{i:04d}.png")
    
    logger.info(f"Created {num_samples} dummy images")
    return str(train_dir), str(train_target_dir), str(val_dir), str(val_target_dir)

def demonstrate_optimization_system():
    """Demonstrate the optimization system"""
    logger.info("="*50)
    logger.info("DEMONSTRATING OPTIMIZATION SYSTEM")
    logger.info("="*50)
    
    # Initialize optimization system
    opt_system = AdvancedOptimizationSystem(device='auto')
    
    # Create dummy model
    model = torch.nn.Sequential(
        torch.nn.Conv2d(3, 64, 3, padding=1),
        torch.nn.ReLU(),
        torch.nn.Conv2d(64, 3, 3, padding=1)
    )
    
    # Profile memory usage
    memory_info = opt_system.profile_memory_usage()
    logger.info(f"Memory usage: {memory_info}")
    
    # Find optimal batch size
    sample_data = torch.randn(1, 3, 64, 64)
    optimal_batch = opt_system.optimize_batch_size(model, sample_data)
    logger.info(f"Optimal batch size: {optimal_batch}")
    
    return opt_system

def demonstrate_loss_functions():
    """Demonstrate advanced loss functions"""
    logger.info("="*50)
    logger.info("DEMONSTRATING LOSS FUNCTIONS")
    logger.info("="*50)
    
    # Initialize loss functions
    loss_functions = AdvancedLossFunctions()
    rf_optimizer = RadioFrequencyOptimizer()
    
    # Create dummy data
    pred = torch.randn(1, 3, 64, 64)
    target = torch.randn(1, 3, 64, 64)
    
    # Test different loss functions
    mse_loss = torch.nn.functional.mse_loss(pred, target)
    freq_loss = loss_functions.frequency_domain_loss(pred, target)
    ssim_loss = loss_functions.structural_similarity_loss(pred, target)
    edge_loss = loss_functions.edge_preserving_loss(pred, target)
    
    logger.info(f"MSE Loss: {mse_loss:.6f}")
    logger.info(f"Frequency Loss: {freq_loss:.6f}")
    logger.info(f"SSIM Loss: {ssim_loss:.6f}")
    logger.info(f"Edge Loss: {edge_loss:.6f}")
    
    # Test adaptive loss
    adaptive_loss = loss_functions.adaptive_loss(pred, target, {
        'mse': 1.0,
        'frequency': 0.5,
        'ssim': 0.3,
        'edge': 0.2
    })
    logger.info(f"Adaptive Loss: {adaptive_loss:.6f}")
    
    # Test radio frequency optimization
    frequency_bands = {
        'low': (0.0, 0.1),
        'mid': (0.1, 0.5),
        'high': (0.5, 1.0)
    }
    
    rf_loss = loss_functions.radio_frequency_optimization_loss(
        pred, target, frequency_bands, {'low': 1.0, 'mid': 1.5, 'high': 2.0}
    )
    logger.info(f"Radio Frequency Loss: {rf_loss:.6f}")
    
    return loss_functions, rf_optimizer

def demonstrate_data_loader():
    """Demonstrate optimized data loader"""
    logger.info("="*50)
    logger.info("DEMONSTRATING DATA LOADER")
    logger.info("="*50)
    
    # Create dummy data first
    train_dir, train_target_dir, val_dir, val_target_dir = create_dummy_data(50)
    
    # Create dataset
    dataset = OptimizedImageDataset(
        image_dir=train_dir,
        target_dir=train_target_dir,
        transform=AdvancedAugmentationPipeline(image_size=(256, 256)),
        cache_size=20,
        preload=False
    )
    
    logger.info(f"Dataset size: {len(dataset)}")
    
    # Test data loading
    sample_image, sample_target = dataset[0]
    logger.info(f"Sample image shape: {sample_image.shape}")
    logger.info(f"Sample target shape: {sample_target.shape}")
    
    # Clear cache
    dataset.clear_cache()
    
    # Cleanup dummy data
    shutil.rmtree("dummy_data")
    
    return dataset

def demonstrate_performance_monitor():
    """Demonstrate performance monitoring"""
    logger.info("="*50)
    logger.info("DEMONSTRATING PERFORMANCE MONITOR")
    logger.info("="*50)
    
    # Initialize monitor
    monitor = PerformanceMonitor(monitor_interval=1.0)
    tracker = TrainingMetricsTracker(monitor)
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Simulate some activity
    import time
    for i in range(5):
        tracker.log_training_step(
            step=i,
            loss=1.0 / (1 + i * 0.1),
            learning_rate=0.001,
            batch_size=32
        )
        time.sleep(1)
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Get summary
    summary = monitor.get_metrics_summary()
    logger.info(f"Performance summary keys: {list(summary.keys())}")
    
    # Cleanup
    monitor.clear_metrics()
    monitor.optimize_memory()
    
    return monitor, tracker

def demonstrate_full_training():
    """Demonstrate full training pipeline"""
    logger.info("="*50)
    logger.info("DEMONSTRATING FULL TRAINING PIPELINE")
    logger.info("="*50)
    
    # Create dummy data
    train_dir, train_target_dir, val_dir, val_target_dir = create_dummy_data(100)
    
    # Configuration
    config = {
        'learning_rate': 1e-4,
        'weight_decay': 1e-5,
        'scheduler_patience': 5,
        'scheduler_factor': 0.5,
        'max_grad_norm': 1.0,
        'monitor_interval': 1.0,
        'save_metrics': True,
        'cache_size': 50,
        'preload_data': False,
        'num_workers': 2,
        'loss_weights': {
            'mse': 1.0,
            'frequency': 0.5,
            'ssim': 0.3,
            'edge': 0.2
        },
        'use_rf_loss': True,
        'rf_loss_weight': 0.1,
        'frequency_bands': {
            'low': (0.0, 0.1),
            'mid': (0.1, 0.5),
            'high': (0.5, 1.0)
        },
        'band_weights': {
            'low': 1.0,
            'mid': 1.5,
            'high': 2.0
        }
    }
    
    # Initialize processor
    processor = AdvancedImageProcessor(config, device='auto')
    
    try:
        # Setup model
        processor.setup_model(
            input_channels=3,
            output_channels=3,
            base_channels=32,  # Smaller for demo
            num_blocks=4
        )
        
        # Setup data
        processor.setup_data(
            train_image_dir=train_dir,
            train_target_dir=train_target_dir,
            val_image_dir=val_dir,
            val_target_dir=val_target_dir,
            image_size=(256, 256),
            batch_size=8
        )
        
        # Train for a few epochs
        history = processor.train(
            epochs=3,
            save_checkpoints=True,
            checkpoint_dir="demo_checkpoints"
        )
        
        # Print summary
        summary = processor.get_performance_summary()
        logger.info(f"Training completed. Device: {summary['device']}")
        logger.info(f"Model parameters: {summary['model_parameters']:,}")
        
        # Test image processing
        test_image_path = os.path.join(train_dir, "image_0000.png")
        output_path = "demo_output.png"
        processor.process_image(test_image_path, output_path)
        logger.info(f"Test image processed and saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Training demonstration failed: {e}")
        raise
    finally:
        processor.cleanup()
        # Cleanup
        shutil.rmtree("dummy_data")
        shutil.rmtree("demo_checkpoints")
        if os.path.exists("demo_output.png"):
            os.remove("demo_output.png")
    
    return processor

def main():
    """Main demonstration function"""
    logger.info("Starting Advanced Image Processing System Demonstration")
    logger.info("="*60)
    
    try:
        # Demonstrate individual components
        opt_system = demonstrate_optimization_system()
        loss_functions, rf_optimizer = demonstrate_loss_functions()
        dataset = demonstrate_data_loader()
        monitor, tracker = demonstrate_performance_monitor()
        
        # Demonstrate full training pipeline
        processor = demonstrate_full_training()
        
        logger.info("="*60)
        logger.info("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        raise

if __name__ == "__main__":
    main()


