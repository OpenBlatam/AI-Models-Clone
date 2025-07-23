#!/usr/bin/env python3
"""
Simple test script for early stopping and learning rate scheduling framework
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

def test_imports():
    """Test that all imports work correctly"""
    try:
        from early_stopping_lr_scheduling import (
            EarlyStoppingConfig, LRSchedulerConfig, TrainingMetrics,
            EarlyStopping, AdvancedLRScheduler, TrainingMonitor, TrainingOptimizer
        )
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_configs():
    """Test configuration classes"""
    try:
        from early_stopping_lr_scheduling import EarlyStoppingConfig, LRSchedulerConfig
        
        # Test early stopping config
        early_stopping_config = EarlyStoppingConfig(
            patience=10,
            monitor="val_loss",
            mode="min"
        )
        print("✓ Early stopping config created")
        
        # Test LR scheduler config
        lr_scheduler_config = LRSchedulerConfig(
            scheduler_type="cosine",
            initial_lr=1e-3,
            T_max=100
        )
        print("✓ LR scheduler config created")
        
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality with a simple model"""
    try:
        from early_stopping_lr_scheduling import (
            EarlyStoppingConfig, LRSchedulerConfig, TrainingOptimizer
        )
        
        # Create simple model
        model = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 2)
        )
        
        # Create optimizer
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()
        
        # Create configurations
        early_stopping_config = EarlyStoppingConfig(
            patience=5,
            monitor="val_loss",
            mode="min",
            verbose=False
        )
        
        lr_scheduler_config = LRSchedulerConfig(
            scheduler_type="cosine",
            initial_lr=1e-3,
            T_max=10,
            verbose=False
        )
        
        # Create training optimizer
        trainer = TrainingOptimizer(
            model=model,
            optimizer=optimizer,
            early_stopping_config=early_stopping_config,
            lr_scheduler_config=lr_scheduler_config
        )
        
        print("✓ Training optimizer created")
        
        # Create simple dataset
        X = torch.randn(100, 10)
        y = torch.randint(0, 2, (100,))
        dataset = TensorDataset(X, y)
        
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        
        # Train for a few epochs
        device = torch.device("cpu")
        model.to(device)
        
        summary = trainer.train(train_loader, val_loader, criterion, device, max_epochs=3)
        
        print("✓ Training completed successfully")
        print(f"  Best validation loss: {summary['early_stopping']['best_score']:.4f}")
        print(f"  Best epoch: {summary['early_stopping']['best_epoch']}")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Testing Early Stopping and Learning Rate Scheduling Framework")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_configs),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  {test_name} failed")
    
    print(f"\n{'=' * 60}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Framework is working correctly.")
    else:
        print("✗ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 