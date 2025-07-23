#!/usr/bin/env python3
"""
Verification script for the Model Training and Evaluation Framework
"""

def verify_imports():
    """Verify that all required modules can be imported"""
    try:
        import torch
        print(f"✓ PyTorch imported successfully (version: {torch.__version__})")
        
        import torch.nn as nn
        print("✓ torch.nn imported successfully")
        
        from torch.utils.data import DataLoader, Dataset
        print("✓ torch.utils.data imported successfully")
        
        import numpy as np
        print("✓ NumPy imported successfully")
        
        from model_training_evaluation import TrainingConfig
        print("✓ TrainingConfig imported successfully")
        
        from model_training_evaluation import ModelTrainer
        print("✓ ModelTrainer imported successfully")
        
        from model_training_evaluation import ModelEvaluator
        print("✓ ModelEvaluator imported successfully")
        
        from model_training_evaluation import EfficientDataLoader
        print("✓ EfficientDataLoader imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def verify_basic_functionality():
    """Verify basic functionality without training"""
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import Dataset
        
        # Create a simple model
        class SimpleModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(10, 2)
            
            def forward(self, x):
                return self.fc(x)
        
        # Create a simple dataset
        class SimpleDataset(Dataset):
            def __init__(self, num_samples=10):
                self.data = torch.randn(num_samples, 10)
                self.labels = torch.randint(0, 2, (num_samples,))
            
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, idx):
                return {
                    'features': self.data[idx],
                    'labels': self.labels[idx]
                }
        
        # Test configuration creation
        from model_training_evaluation import TrainingConfig
        
        model = SimpleModel()
        train_dataset = SimpleDataset(10)
        val_dataset = SimpleDataset(5)
        
        config = TrainingConfig(
            model=model,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            epochs=1,
            batch_size=4,
            learning_rate=1e-3
        )
        
        print("✓ TrainingConfig created successfully")
        print(f"  - Model parameters: {sum(p.numel() for p in model.parameters()):,}")
        print(f"  - Device: {config.device}")
        print(f"  - Batch size: {config.batch_size}")
        print(f"  - Learning rate: {config.learning_rate}")
        
        # Test data loader creation
        from model_training_evaluation import EfficientDataLoader
        
        data_loader = EfficientDataLoader(config)
        train_loader = data_loader.get_train_loader()
        val_loader = data_loader.get_val_loader()
        
        print("✓ EfficientDataLoader created successfully")
        print(f"  - Train batches: {len(train_loader)}")
        print(f"  - Val batches: {len(val_loader)}")
        
        # Test trainer creation
        from model_training_evaluation import ModelTrainer
        
        trainer = ModelTrainer(config)
        print("✓ ModelTrainer created successfully")
        print(f"  - Device: {trainer.device}")
        print(f"  - Optimizer: {type(trainer.optimizer).__name__}")
        print(f"  - Scheduler: {type(trainer.scheduler).__name__}")
        
        # Test evaluator creation
        from model_training_evaluation import ModelEvaluator
        
        evaluator = ModelEvaluator(model)
        print("✓ ModelEvaluator created successfully")
        print(f"  - Device: {evaluator.device}")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False

def main():
    """Run verification tests"""
    print("=== Model Training and Evaluation Framework Verification ===\n")
    
    # Test imports
    print("1. Testing imports...")
    imports_ok = verify_imports()
    print()
    
    # Test basic functionality
    print("2. Testing basic functionality...")
    functionality_ok = verify_basic_functionality()
    print()
    
    # Summary
    print("=== Verification Summary ===")
    if imports_ok and functionality_ok:
        print("✓ All tests passed! The training framework is ready to use.")
        print("\nKey features available:")
        print("  - TrainingConfig for configuration management")
        print("  - EfficientDataLoader for optimized data loading")
        print("  - ModelTrainer for comprehensive training")
        print("  - ModelEvaluator for model evaluation")
        print("  - Mixed precision training support")
        print("  - Early stopping and checkpointing")
        print("  - Multiple optimizer and scheduler options")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
    
    return imports_ok and functionality_ok

if __name__ == "__main__":
    main() 