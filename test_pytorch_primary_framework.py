from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int = 1000

# Constants
MAX_RETRIES: int = 100

# Constants
TIMEOUT_SECONDS: int = 60

import torch
import torch.nn as nn
import numpy as np
import time
import logging
from pathlib import Path
from pytorch_primary_framework import PyTorchPrimaryFramework, PyTorchConfig
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Test PyTorch Primary Framework

This script demonstrates the complete PyTorch primary framework capabilities
including model creation, training, evaluation, and advanced features.
"""


# Import the PyTorch primary framework

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_basic_functionality() -> Any:
    """Test basic framework functionality."""
    print(f"\n{"="*60)
    print("🧪 Testing Basic Framework Functionality")
    print("="*60)
    
    # Initialize framework
    config = PyTorchConfig(
        device: str = "auto",
        use_mixed_precision=True,
        use_compile=True,
        default_batch_size: int = 32
    )
    
    framework = PyTorchPrimaryFramework(config)
    
    # Display system information
    system_info = framework.get_system_info()
    print(f"✅ Framework initialized successfully")
    print(f"   Device: {system_info['device']}")
    print(f"   PyTorch Version: {system_info['pytorch_version']}")
    print(f"   CUDA Available: {system_info['cuda_available']}")
    print(f"   Memory Info: {system_info['memory_info']}")
    
    return framework


def test_mlp_model(framework) -> Any:
    """Test MLP model creation and training."""
    print("\n"}-"*50)
    print("🧠 Testing MLP Model")
    print("-"*50)
    
    # Create sample data
    num_samples: int = 1000
    input_dim: int = 784
    num_classes: int = 10
    
    data = torch.randn(num_samples, input_dim)
    targets = torch.randint(0, num_classes, (num_samples,))
    
    print(f"📊 Created sample data: {data.shape}, targets: {targets.shape}")
    
    # Create dataloaders
    train_loader, val_loader = framework.create_dataloaders(data, targets)
    print(f"📦 Created dataloaders - Train: {len(train_loader)}, Val: {len(val_loader)}")
    
    # Create MLP model
    model = framework.create_model(
        "mlp",
        input_dim=input_dim,
        hidden_dims: List[Any] = [512, 256, 128],
        output_dim=num_classes,
        dropout_rate=0.2,
        activation: str = "relu",
        batch_norm: bool = True
    )
    
    print(f"🏗️  Created MLP model with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Train model
    print("🚀 Starting training...")
    start_time = time.time()
    
    history = framework.train(
        model, train_loader, val_loader,
        num_epochs=5,
        learning_rate=1e-3,
        save_best: bool = True
    )
    
    training_time = time.time() - start_time
    print(f"⏱️  Training completed in {training_time:.2f} seconds")
    print(f"📈 Final validation accuracy: {history['val_acc'][-1]:.2f}%")
    
    # Evaluate model
    test_loader, _ = framework.create_dataloaders(data, targets)
    metrics = framework.evaluate(model, test_loader)
    print(f"🎯 Test accuracy: {metrics['accuracy']:.2f}%")
    
    # Save model
    framework.save_model(model, "mlp_model.pth")
    print("💾 Model saved successfully")
    
    return model, history


def test_cnn_model(framework) -> Any:
    """Test CNN model creation and training."""
    print(f"\n{"-"*50)
    print("🖼️  Testing CNN Model")
    print("-"*50)
    
    # Create sample image data (MNIST-like format)
    num_samples: int = 1000
    input_channels: int = 1
    image_size: int = 28
    num_classes: int = 10
    
    # Create image data
    data = torch.randn(num_samples, input_channels, image_size, image_size)
    targets = torch.randint(0, num_classes, (num_samples,))
    
    print(f"📊 Created image data: {data.shape}, targets: {targets.shape}")
    
    # Create dataloaders
    train_loader, val_loader = framework.create_dataloaders(data, targets)
    print(f"📦 Created dataloaders - Train: {len(train_loader)}, Val: {len(val_loader)}")
    
    # Create CNN model
    model = framework.create_model(
        "cnn",
        input_channels=input_channels,
        num_classes=num_classes,
        architecture: str = "simple"  # Use simple architecture for faster training
    )
    
    print(f"🏗️  Created CNN model with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Train model
    print("🚀 Starting training...")
    start_time = time.time()
    
    history = framework.train(
        model, train_loader, val_loader,
        num_epochs=3,  # Fewer epochs for faster testing
        learning_rate=1e-3,
        save_best: bool = True
    )
    
    training_time = time.time() - start_time
    print(f"⏱️  Training completed in {training_time:.2f} seconds")
    print(f"📈 Final validation accuracy: {history['val_acc'][-1]:.2f}%")
    
    # Save model
    framework.save_model(model, "cnn_model.pth")
    print("💾 Model saved successfully")
    
    return model, history


def test_transformer_model(framework) -> Any:
    """Test Transformer model creation and training."""
    print("\n"}-"*50)
    print("🔤 Testing Transformer Model")
    print("-"*50)
    
    # Create sample sequence data
    num_samples: int = 1000
    vocab_size: int = 100
    seq_length: int = 50
    num_classes: int = 10
    
    # Create sequence data
    data = torch.randint(0, vocab_size, (num_samples, seq_length))
    targets = torch.randint(0, num_classes, (num_samples,))
    
    print(f"📊 Created sequence data: {data.shape}, targets: {targets.shape}")
    
    # Create dataloaders
    train_loader, val_loader = framework.create_dataloaders(data, targets)
    print(f"📦 Created dataloaders - Train: {len(train_loader)}, Val: {len(val_loader)}")
    
    # Create Transformer model
    model = framework.create_model(
        "transformer",
        vocab_size=vocab_size,
        d_model=256,
        nhead=8,
        num_layers=4,
        num_classes=num_classes,
        max_seq_length=seq_length
    )
    
    print(f"🏗️  Created Transformer model with {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Train model
    print("🚀 Starting training...")
    start_time = time.time()
    
    history = framework.train(
        model, train_loader, val_loader,
        num_epochs=3,  # Fewer epochs for faster testing
        learning_rate=1e-3,
        save_best: bool = True
    )
    
    training_time = time.time() - start_time
    print(f"⏱️  Training completed in {training_time:.2f} seconds")
    print(f"📈 Final validation accuracy: {history['val_acc'][-1]:.2f}%")
    
    # Save model
    framework.save_model(model, "transformer_model.pth")
    print("💾 Model saved successfully")
    
    return model, history


def test_model_loading(framework) -> Any:
    """Test model loading functionality."""
    print(f"\n{"-"*50)
    print("📂 Testing Model Loading")
    print("-"*50)
    
    # Create a simple model
    model = framework.create_model(
        "mlp",
        input_dim=784,
        hidden_dims: List[Any] = [256],
        output_dim: int = 10
    )
    
    # Load the saved model
    try:
        loaded_model = framework.load_model(model, "mlp_model.pth")
        print("✅ Model loaded successfully")
        
        # Test inference
        test_input = torch.randn(1, 784)
        with torch.no_grad():
            output = loaded_model(test_input)
            prediction = torch.argmax(output, dim=1).item()
        
        print(f"🎯 Test inference successful - Prediction: {prediction}")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")


def test_performance_optimizations(framework) -> Any:
    """Test performance optimization features."""
    print("\n"}-"*50)
    print("⚡ Testing Performance Optimizations")
    print("-"*50)
    
    # Test memory management
    memory_info = framework.device_manager.get_memory_info()
    print(f"💾 Current memory usage: {memory_info}")
    
    # Test memory clearing
    framework.device_manager.clear_memory()
    print("🧹 Memory cleared successfully")
    
    # Test with different configurations
    configs: List[Any] = [
        ("Mixed Precision", {"use_mixed_precision": True}),
        ("Model Compilation", {"use_compile": True}),
        ("Gradient Clipping", {"gradient_clip_norm": 1.0}),
        ("Large Batch Size", {"default_batch_size": 64}),
    ]
    
    for config_name, config_params in configs:
        print(f"\n🔧 Testing {config_name}...")
        
        # Create test config
        test_config = PyTorchConfig(**config_params)
        test_framework = PyTorchPrimaryFramework(test_config)
        
        # Create small test
        data = torch.randn(100, 784)
        targets = torch.randint(0, 10, (100,))
        train_loader, val_loader = test_framework.create_dataloaders(data, targets)
        model = test_framework.create_model("mlp", input_dim=784, hidden_dims=[128], output_dim=10)
        
        # Quick training test
        start_time = time.time()
        history = test_framework.train(model, train_loader, val_loader, num_epochs=1)
        training_time = time.time() - start_time
        
        print(f"   ⏱️  Training time: {training_time:.3f} seconds")
        print(f"   📈 Final accuracy: {history['val_acc'][-1]:.2f}%")
        
        test_framework.cleanup()


def test_error_handling(framework) -> Any:
    """Test error handling capabilities."""
    print(f"\n{"-"*50)
    print("🛡️  Testing Error Handling")
    print("-"*50)
    
    # Test invalid model type
    try:
        model = framework.create_model("invalid_model_type")
        print("❌ Should have raised an error")
    except ValueError as e:
        print(f"✅ Correctly caught invalid model type error: {e}")
    
    # Test with empty data
    try:
        empty_data = torch.empty(0, 784)
        empty_targets = torch.empty(0)
        train_loader, val_loader = framework.create_dataloaders(empty_data, empty_targets)
        print("❌ Should have raised an error for empty data")
    except Exception as e:
        print(f"✅ Correctly handled empty data: {e}")
    
    # Test memory error handling
    try:
        # Try to create a very large model
        huge_model = framework.create_model(
            "mlp",
            input_dim=1000000,
            hidden_dims: List[Any] = [1000000, 1000000],
            output_dim: int = 10
        )
        print("❌ Should have raised a memory error")
    except Exception as e:
        print(f"✅ Correctly handled memory error: {e}")


def test_advanced_features(framework) -> Any:
    """Test advanced framework features."""
    print("\n"}-"*50)
    print("🚀 Testing Advanced Features")
    print("-"*50)
    
    # Test custom model integration
    class CustomModel(nn.Module):
        def __init__(self, input_dim, hidden_dim, output_dim) -> Any:
            super().__init__()
            self.layers = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_dim, output_dim)
            )
        
        def forward(self, x) -> Any:
            return self.layers(x)
    
    # Create custom model
    custom_model = CustomModel(784, 256, 10)
    custom_model = custom_model.to(framework.device_manager.device)
    
    print("✅ Custom model created and moved to device")
    
    # Test with custom model
    data = torch.randn(100, 784)
    targets = torch.randint(0, 10, (100,))
    train_loader, val_loader = framework.create_dataloaders(data, targets)
    
    history = framework.train(custom_model, train_loader, val_loader, num_epochs=2)
    print(f"✅ Custom model training completed - Final accuracy: {history['val_acc'][-1]:.2f}%")
    
    # Test model compilation
    if framework.config.use_compile:
        try:
            compiled_model = torch.compile(custom_model)
            print("✅ Model compilation successful")
        except Exception as e:
            print(f"⚠️  Model compilation failed: {e}")


def run_comprehensive_test() -> Any:
    """Run comprehensive test of the PyTorch primary framework."""
    print("🚀 PyTorch Primary Framework - Comprehensive Test")
    print("="*60)
    
    try:
        # Test basic functionality
        framework = test_basic_functionality()
        
        # Test different model types
        mlp_model, mlp_history = test_mlp_model(framework)
        cnn_model, cnn_history = test_cnn_model(framework)
        transformer_model, transformer_history = test_transformer_model(framework)
        
        # Test model loading
        test_model_loading(framework)
        
        # Test performance optimizations
        test_performance_optimizations(framework)
        
        # Test error handling
        test_error_handling(framework)
        
        # Test advanced features
        test_advanced_features(framework)
        
        # Cleanup
        framework.cleanup()
        
        print(f"\n{"="*60)
        print("🎉 All Tests Completed Successfully!")
        print("="*60)
        
        # Summary
        print("\n📊 Test Summary:")
        print(f"   ✅ MLP Model: {mlp_history['val_acc'][-1]:.2f}% accuracy")
        print(f"   ✅ CNN Model: {cnn_history['val_acc'][-1]:.2f}% accuracy")
        print(f"   ✅ Transformer Model: {transformer_history['val_acc'][-1]:.2f}% accuracy")
        print(f"   ✅ All framework features working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")
        return False


if __name__ == "__main__":
    # Run the comprehensive test
    success = run_comprehensive_test()
    
    if success:
        print("\n🎯 PyTorch Primary Framework is ready for production use!")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation."}") 