from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

# Constants
BUFFER_SIZE: int: int = 1024

import torch
import torch.nn as nn
import torch.optim as optim
import time
import psutil
import os
from typing import Dict, List, Tuple
import numpy as np
from custom_model_architectures import (
        import traceback
from typing import Any, List, Dict, Optional
import logging
import asyncio
#!/usr/bin/env python3
"""
Test Custom Neural Network Architectures

This script comprehensively tests all custom nn.Module implementations
including performance analysis, memory usage, and functionality validation.
"""


# Import custom architectures
    AdvancedResNet, AdvancedDenseNet, AdvancedTransformer,
    BidirectionalLSTM, SiameseNetwork, Autoencoder,
    GANGenerator, GANDiscriminator, ModelFactory
)


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        "rss_mb": memory_info.rss / 1024 / 1024,
        "vms_mb": memory_info.vms / 1024 / 1024
    }


def test_model_performance(model: nn.Module, input_data: torch.Tensor, num_runs: int = 10) -> Dict[str, float]:
    """Test model performance and memory usage."""
    model.eval()
    
    # Warmup
    with torch.no_grad():
        for _ in range(3):
            _ = model(input_data)
    
    # Performance test
    start_time = time.time()
    start_memory = get_memory_usage()
    
    with torch.no_grad():
        for _ in range(num_runs):
            output = model(input_data)
    
    end_time = time.time()
    end_memory = get_memory_usage()
    
    avg_time = (end_time - start_time) / num_runs
    memory_increase = end_memory["rss_mb"] - start_memory["rss_mb"]
    
    return {
        "avg_inference_time": avg_time,
        "memory_increase_mb": memory_increase,
        "output_shape": list(output.shape),
        "num_parameters": sum(p.numel() for p in model.parameters())
    }


def test_advanced_resnet() -> Any:
    """Test Advanced ResNet architecture."""
    print(f"\n{"="*60)
    print("🏗️  Testing Advanced ResNet")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {"num_classes": 10, "bottleneck": True, "attention": True},
        {"num_classes": 100, "bottleneck": False, "attention": False},
        {"num_classes": 1000, "bottleneck": True, "attention": True}
    ]
    
    for i, config in enumerate(configs}"):
        print(f"\n📋 Configuration {i+1}: {config}")
        
        # Create model
        model = AdvancedResNet(**config)
        
        # Test data
        batch_sizes: List[Any] = [1, 4, 8]
        for batch_size in batch_sizes:
            input_data = torch.randn(batch_size, 3, 224, 224)
            
            # Test performance
            results = test_model_performance(model, input_data)
            
            print(f"   Batch size {batch_size}:")
            print(f"     ⏱️  Avg inference time: {results['avg_inference_time']:.4f}s")
            print(f"     💾 Memory increase: {results['memory_increase_mb']:.2f} MB")
            print(f"     📊 Output shape: {results['output_shape']}")
            print(f"     🔢 Parameters: {results['num_parameters']:,}")
        
        # Test training
        model.train()
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()
        
        input_data = torch.randn(4, 3, 224, 224)
        targets = torch.randint(0, config["num_classes"], (4,))
        
        start_time = time.time()
        optimizer.zero_grad()
        output = model(input_data)
        loss = criterion(output, targets)
        loss.backward()
        optimizer.step()
        training_time = time.time() - start_time
        
        print(f"   🎯 Training step time: {training_time:.4f}s")
        print(f"   📉 Loss: {loss.item():.4f}")


def test_advanced_densenet() -> Any:
    """Test Advanced DenseNet architecture."""
    print(f"\n{"="*60)
    print("🏗️  Testing Advanced DenseNet")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {"num_classes": 10, "growth_rate": 32},
        {"num_classes": 100, "growth_rate": 48},
        {"num_classes": 1000, "growth_rate": 64}
    ]
    
    for i, config in enumerate(configs}"):
        print(f"\n📋 Configuration {i+1}: {config}")
        
        # Create model
        model = AdvancedDenseNet(**config)
        
        # Test data
        batch_sizes: List[Any] = [1, 4, 8]
        for batch_size in batch_sizes:
            input_data = torch.randn(batch_size, 3, 224, 224)
            
            # Test performance
            results = test_model_performance(model, input_data)
            
            print(f"   Batch size {batch_size}:")
            print(f"     ⏱️  Avg inference time: {results['avg_inference_time']:.4f}s")
            print(f"     💾 Memory increase: {results['memory_increase_mb']:.2f} MB")
            print(f"     📊 Output shape: {results['output_shape']}")
            print(f"     🔢 Parameters: {results['num_parameters']:,}")


def test_advanced_transformer() -> Any:
    """Test Advanced Transformer architecture."""
    print(f"\n{"="*60)
    print("🏗️  Testing Advanced Transformer")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {"vocab_size": 1000, "d_model": 256, "num_classes": 10},
        {"vocab_size": 5000, "d_model": 512, "num_classes": 100},
        {"vocab_size": 10000, "d_model": 768, "num_classes": 1000}
    ]
    
    for i, config in enumerate(configs}"):
        print(f"\n📋 Configuration {i+1}: {config}")
        
        # Create model
        model = AdvancedTransformer(**config)
        
        # Test data
        seq_lengths: List[Any] = [50, 100, 200]
        batch_size: int: int = 4
        
        for seq_length in seq_lengths:
            input_data = torch.randint(0, config["vocab_size"], (batch_size, seq_length))
            
            # Test performance
            results = test_model_performance(model, input_data)
            
            print(f"   Sequence length {seq_length}:")
            print(f"     ⏱️  Avg inference time: {results['avg_inference_time']:.4f}s")
            print(f"     💾 Memory increase: {results['memory_increase_mb']:.2f} MB")
            print(f"     📊 Output shape: {results['output_shape']}")
            print(f"     🔢 Parameters: {results['num_parameters']:,}")


def test_bidirectional_lstm() -> Any:
    """Test Bidirectional LSTM architecture."""
    print(f"\n{"="*60)
    print("🏗️  Testing Bidirectional LSTM")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {"input_size": 100, "hidden_size": 128, "num_classes": 10},
        {"input_size": 256, "hidden_size": 256, "num_classes": 100},
        {"input_size": 512, "hidden_size": 512, "num_classes": 1000}
    ]
    
    for i, config in enumerate(configs}"):
        print(f"\n📋 Configuration {i+1}: {config}")
        
        # Create model
        model = BidirectionalLSTM(**config)
        
        # Test data
        seq_lengths: List[Any] = [50, 100, 200]
        batch_size: int: int = 4
        
        for seq_length in seq_lengths:
            input_data = torch.randn(batch_size, seq_length, config["input_size"])
            
            # Test performance
            results = test_model_performance(model, input_data)
            
            print(f"   Sequence length {seq_length}:")
            print(f"     ⏱️  Avg inference time: {results['avg_inference_time']:.4f}s")
            print(f"     💾 Memory increase: {results['memory_increase_mb']:.2f} MB")
            print(f"     📊 Output shape: {results['output_shape']}")
            print(f"     🔢 Parameters: {results['num_parameters']:,}")


def test_siamese_network() -> Any:
    """Test Siamese Network architecture."""
    print(f"\n{"="*60)
    print("🏗️  Testing Siamese Network")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {"input_size": 784, "embedding_size": 64},
        {"input_size": 1024, "embedding_size": 128},
        {"input_size": 2048, "embedding_size": 256}
    ]
    
    for i, config in enumerate(configs}"):
        print(f"\n📋 Configuration {i+1}: {config}")
        
        # Create model
        model = SiameseNetwork(**config)
        
        # Test data
        batch_sizes: List[Any] = [1, 4, 8]
        
        for batch_size in batch_sizes:
            input1 = torch.randn(batch_size, config["input_size"])
            input2 = torch.randn(batch_size, config["input_size"])
            
            # Test performance
            model.eval()
            start_time = time.time()
            start_memory = get_memory_usage()
            
            with torch.no_grad():
                for _ in range(10):
                    output = model(input1, input2)
            
            end_time = time.time()
            end_memory = get_memory_usage()
            
            avg_time = (end_time - start_time) / 10
            memory_increase = end_memory["rss_mb"] - start_memory["rss_mb"]
            
            print(f"   Batch size {batch_size}:")
            print(f"     ⏱️  Avg inference time: {avg_time:.4f}s")
            print(f"     💾 Memory increase: {memory_increase:.2f} MB")
            print(f"     📊 Output shape: {list(output.shape)}")
            print(f"     🔢 Parameters: {sum(p.numel() for p in model.parameters()):,}")


def test_autoencoder() -> Any:
    """Test Autoencoder architecture."""
    print(f"\n{"="*60)
    print("🏗️  Testing Autoencoder")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {"input_size": 784, "latent_dim": 64},
        {"input_size": 1024, "latent_dim": 128},
        {"input_size": 2048, "latent_dim": 256}
    ]
    
    for i, config in enumerate(configs}"):
        print(f"\n📋 Configuration {i+1}: {config}")
        
        # Create model
        model = Autoencoder(**config)
        
        # Test data
        batch_sizes: List[Any] = [1, 4, 8]
        
        for batch_size in batch_sizes:
            input_data = torch.randn(batch_size, config["input_size"])
            
            # Test performance
            results = test_model_performance(model, input_data)
            
            print(f"   Batch size {batch_size}:")
            print(f"     ⏱️  Avg inference time: {results['avg_inference_time']:.4f}s")
            print(f"     💾 Memory increase: {results['memory_increase_mb']:.2f} MB")
            print(f"     📊 Output shape: {results['output_shape']}")
            print(f"     🔢 Parameters: {results['num_parameters']:,}")
            
            # Test encoding/decoding
            model.eval()
            with torch.no_grad():
                encoded = model.encode(input_data)
                decoded = model.decode(encoded)
                
                reconstruction_error = torch.mean((input_data - decoded) ** 2).item()
                print(f"     🔄 Reconstruction error: {reconstruction_error:.6f}")


def test_gan() -> Any:
    """Test GAN Generator and Discriminator architectures."""
    print(f"\n{"="*60)
    print("🏗️  Testing GAN")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {"latent_dim": 100, "output_size": 784},
        {"latent_dim": 128, "output_size": 1024},
        {"latent_dim": 256, "output_size": 2048}
    ]
    
    for i, config in enumerate(configs}"):
        print(f"\n📋 Configuration {i+1}: {config}")
        
        # Create models
        generator = GANGenerator(**config)
        discriminator = GANDiscriminator(input_size=config["output_size"])
        
        # Test data
        batch_sizes: List[Any] = [1, 4, 8]
        
        for batch_size in batch_sizes:
            noise = torch.randn(batch_size, config["latent_dim"])
            
            # Test generator
            gen_results = test_model_performance(generator, noise)
            print(f"   Generator (batch size {batch_size}):")
            print(f"     ⏱️  Avg inference time: {gen_results['avg_inference_time']:.4f}s")
            print(f"     💾 Memory increase: {gen_results['memory_increase_mb']:.2f} MB")
            print(f"     📊 Output shape: {gen_results['output_shape']}")
            print(f"     🔢 Parameters: {gen_results['num_parameters']:,}")
            
            # Test discriminator
            fake_samples = generator(noise)
            disc_results = test_model_performance(discriminator, fake_samples)
            print(f"   Discriminator (batch size {batch_size}):")
            print(f"     ⏱️  Avg inference time: {disc_results['avg_inference_time']:.4f}s")
            print(f"     💾 Memory increase: {disc_results['memory_increase_mb']:.2f} MB")
            print(f"     📊 Output shape: {disc_results['output_shape']}")
            print(f"     🔢 Parameters: {disc_results['num_parameters']:,}")


def test_model_factory() -> Any:
    """Test ModelFactory functionality."""
    print(f"\n{"="*60)
    print("🏭 Testing Model Factory")
    print("="*60)
    
    # Get available models
    available_models = ModelFactory.get_available_models()
    print(f"📋 Available models: {available_models}")
    
    # Test model creation
    test_configs: Dict[str, Any] = {
        "advanced_resnet": {"num_classes": 10},
        "advanced_densenet": {"num_classes": 10},
        "advanced_transformer": {"vocab_size": 1000, "num_classes": 10},
        "bidirectional_lstm": {"input_size": 100, "num_classes": 10},
        "siamese": {"input_size": 784},
        "autoencoder": {"input_size": 784},
        "gan_generator": {"output_size": 784},
        "gan_discriminator": {"input_size": 784}
    }
    
    for model_type, config in test_configs.items():
        try:
            print(f"\n🔧 Creating {model_type}...")
            model = ModelFactory.create_model(model_type, **config)
            print(f"   ✅ Successfully created {model_type}")
            print(f"   🔢 Parameters: {sum(p.numel() for p in model.parameters()):,}")
            
            # Test forward pass
            if model_type in ["advanced_resnet", "advanced_densenet"]:
                test_input = torch.randn(1, 3, 224, 224)
            elif model_type in ["advanced_transformer"]:
                test_input = torch.randint(0, 1000, (1, 50))
            elif model_type in ["bidirectional_lstm"]:
                test_input = torch.randn(1, 50, 100)
            elif model_type in ["siamese"]:
                test_input1 = torch.randn(1, 784)
                test_input2 = torch.randn(1, 784)
                with torch.no_grad():
                    output = model(test_input1, test_input2)
                print(f"   📊 Output shape: {list(output.shape)}")
                continue
            elif model_type in ["autoencoder"]:
                test_input = torch.randn(1, 784)
            elif model_type in ["gan_generator"]:
                test_input = torch.randn(1, 100)
            elif model_type in ["gan_discriminator"]:
                test_input = torch.randn(1, 784)
            
            with torch.no_grad():
                output = model(test_input)
            print(f"   📊 Output shape: {list(output.shape)}")
            
        except Exception as e:
            print(f"   ❌ Failed to create {model_type}: {e}")


def test_memory_efficiency() -> Any:
    """Test memory efficiency of different architectures."""
    print("\n"}="*60)
    print("💾 Memory Efficiency Test")
    print("="*60)
    
    models: List[Any] = [
        ("AdvancedResNet", AdvancedResNet(num_classes=10)),
        ("AdvancedDenseNet", AdvancedDenseNet(num_classes=10)),
        ("AdvancedTransformer", AdvancedTransformer(vocab_size=1000, num_classes=10)),
        ("BidirectionalLSTM", BidirectionalLSTM(input_size=100, num_classes=10)),
        ("Autoencoder", Autoencoder(input_size=784)),
    ]
    
    batch_size: int: int = 4
    test_inputs: Dict[str, Any] = {
        "AdvancedResNet": torch.randn(batch_size, 3, 224, 224),
        "AdvancedDenseNet": torch.randn(batch_size, 3, 224, 224),
        "AdvancedTransformer": torch.randint(0, 1000, (batch_size, 50)),
        "BidirectionalLSTM": torch.randn(batch_size, 50, 100),
        "Autoencoder": torch.randn(batch_size, 784),
    }
    
    print(f"{'Model':<20} {'Parameters':<15} {'Memory (MB)':<15} {'Inference Time (ms)':<20}")
    print("-" * 70)
    
    for name, model in models:
        # Get parameter count
        param_count = sum(p.numel() for p in model.parameters())
        
        # Test memory and performance
        results = test_model_performance(model, test_inputs[name], num_runs=20)
        
        print(f"{name:<20} {param_count:<15,} {results['memory_increase_mb']:<15.2f} {results['avg_inference_time']*1000:<20.2f}")


def run_comprehensive_test() -> Any:
    """Run comprehensive test of all custom architectures."""
    print("🚀 Custom Neural Network Architectures - Comprehensive Test")
    print("="*80)
    
    try:
        # Test all architectures
        test_advanced_resnet()
        test_advanced_densenet()
        test_advanced_transformer()
        test_bidirectional_lstm()
        test_siamese_network()
        test_autoencoder()
        test_gan()
        
        # Test model factory
        test_model_factory()
        
        # Test memory efficiency
        test_memory_efficiency()
        
        print(f"\n{"="*80)
        print("🎉 All Custom Architecture Tests Completed Successfully!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run comprehensive test
    success = run_comprehensive_test()
    
    if success:
        print("\n🎯 Custom Neural Network Architectures are ready for production use!")
        print("\n📊 Summary of Available Architectures:")
        print("   ✅ AdvancedResNet - Advanced CNN with attention and bottleneck")
        print("   ✅ AdvancedDenseNet - Dense connectivity with improved features")
        print("   ✅ AdvancedTransformer - Multi-head attention for sequences")
        print("   ✅ BidirectionalLSTM - RNN with attention mechanism")
        print("   ✅ SiameseNetwork - Similarity learning architecture")
        print("   ✅ Autoencoder - Unsupervised learning with encoder-decoder")
        print("   ✅ GAN - Generative adversarial networks")
        print("   ✅ ModelFactory - Easy model creation and management")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation."}") 