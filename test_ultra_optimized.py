#!/usr/bin/env python3
"""
Test Script for Ultra-Optimized AI System
========================================

Comprehensive test suite for all ultra-optimized features:
- Deep learning optimizations
- Transformer implementations
- Diffusion model functionality
- Gradio interface components
- Performance monitoring
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import torch
import torch.nn as nn
import numpy as np
from PIL import Image

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestUltraOptimizedSystem(unittest.TestCase):
    """Test suite for ultra-optimized AI system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "outputs")
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        self.log_dir = os.path.join(self.temp_dir, "logs")
        self.model_dir = os.path.join(self.temp_dir, "models")
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Check if CUDA is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Testing on device: {self.device}")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_imports(self):
        """Test that all modules can be imported."""
        try:
            from ultra_optimized_deep_learning import (
                UltraOptimizedTransformerModel, UltraTrainingConfig,
                UltraOptimizedDiffusionModel, UltraOptimizedDataset,
                UltraOptimizedTrainer, UltraOptimizedInference
            )
            print("✓ Deep learning module imports successful")
        except ImportError as e:
            self.fail(f"Failed to import deep learning module: {e}")
        
        try:
            from ultra_optimized_transformers import (
                UltraOptimizedTransformerModel as UltraTransformerModel,
                UltraTransformersConfig, UltraOptimizedTokenizer
            )
            print("✓ Transformers module imports successful")
        except ImportError as e:
            self.fail(f"Failed to import transformers module: {e}")
        
        try:
            from ultra_optimized_diffusion import (
                UltraOptimizedDiffusionPipeline, UltraDiffusionConfig
            )
            print("✓ Diffusion module imports successful")
        except ImportError as e:
            self.fail(f"Failed to import diffusion module: {e}")
        
        try:
            from ultra_optimized_gradio_interface import (
                UltraOptimizedGradioInterface, UltraGradioConfig
            )
            print("✓ Gradio interface module imports successful")
        except ImportError as e:
            self.fail(f"Failed to import gradio interface module: {e}")
    
    def test_deep_learning_config(self):
        """Test deep learning configuration."""
        from ultra_optimized_deep_learning import UltraTrainingConfig
        
        config = UltraTrainingConfig(
            model_name="gpt2",
            batch_size=4,
            learning_rate=2e-5,
            use_mixed_precision=True,
            use_gradient_checkpointing=True,
            device=self.device,
            output_dir=self.output_dir,
            cache_dir=self.cache_dir,
            log_dir=self.log_dir
        )
        
        self.assertEqual(config.model_name, "gpt2")
        self.assertEqual(config.batch_size, 4)
        self.assertEqual(config.learning_rate, 2e-5)
        self.assertTrue(config.use_mixed_precision)
        self.assertTrue(config.use_gradient_checkpointing)
        self.assertEqual(config.device, self.device)
        
        print("✓ Deep learning configuration test passed")
    
    def test_transformers_config(self):
        """Test transformers configuration."""
        from ultra_optimized_transformers import UltraTransformersConfig
        
        config = UltraTransformersConfig(
            model_name="gpt2",
            batch_size=4,
            use_lora=True,
            use_prompt_tuning=False,
            use_mixed_precision=True,
            device=self.device,
            output_dir=self.output_dir,
            cache_dir=self.cache_dir,
            log_dir=self.log_dir
        )
        
        self.assertEqual(config.model_name, "gpt2")
        self.assertEqual(config.batch_size, 4)
        self.assertTrue(config.use_lora)
        self.assertFalse(config.use_prompt_tuning)
        self.assertTrue(config.use_mixed_precision)
        
        print("✓ Transformers configuration test passed")
    
    def test_diffusion_config(self):
        """Test diffusion configuration."""
        from ultra_optimized_diffusion import UltraDiffusionConfig
        
        config = UltraDiffusionConfig(
            model_name="runwayml/stable-diffusion-v1-5",
            num_inference_steps=20,
            guidance_scale=7.5,
            use_mixed_precision=True,
            device=self.device,
            output_dir=self.output_dir,
            cache_dir=self.cache_dir,
            log_dir=self.log_dir
        )
        
        self.assertEqual(config.model_name, "runwayml/stable-diffusion-v1-5")
        self.assertEqual(config.num_inference_steps, 20)
        self.assertEqual(config.guidance_scale, 7.5)
        self.assertTrue(config.use_mixed_precision)
        
        print("✓ Diffusion configuration test passed")
    
    def test_gradio_config(self):
        """Test Gradio interface configuration."""
        from ultra_optimized_gradio_interface import UltraGradioConfig
        
        config = UltraGradioConfig(
            enable_transformers=True,
            enable_diffusion=True,
            enable_llm=True,
            use_caching=True,
            cache_size=50,
            output_dir=self.output_dir,
            cache_dir=self.cache_dir,
            log_dir=self.log_dir
        )
        
        self.assertTrue(config.enable_transformers)
        self.assertTrue(config.enable_diffusion)
        self.assertTrue(config.enable_llm)
        self.assertTrue(config.use_caching)
        self.assertEqual(config.cache_size, 50)
        
        print("✓ Gradio configuration test passed")
    
    def test_attention_mechanism(self):
        """Test attention mechanism implementation."""
        from ultra_optimized_transformers import UltraOptimizedMultiHeadAttention
        
        # Create attention mechanism
        d_model = 256
        num_heads = 8
        attention = UltraOptimizedMultiHeadAttention(d_model, num_heads)
        
        # Test forward pass
        batch_size = 2
        seq_len = 10
        x = torch.randn(batch_size, seq_len, d_model)
        
        output = attention(x, x, x)
        
        self.assertEqual(output.shape, (batch_size, seq_len, d_model))
        self.assertFalse(torch.isnan(output).any())
        self.assertFalse(torch.isinf(output).any())
        
        print("✓ Attention mechanism test passed")
    
    def test_positional_encoding(self):
        """Test positional encoding implementation."""
        from ultra_optimized_transformers import UltraOptimizedPositionalEncoding
        
        # Create positional encoding
        d_model = 256
        max_length = 100
        pos_encoding = UltraOptimizedPositionalEncoding(d_model, max_length)
        
        # Test forward pass
        batch_size = 2
        seq_len = 10
        x = torch.randn(batch_size, seq_len, d_model)
        
        output = pos_encoding(x)
        
        self.assertEqual(output.shape, (batch_size, seq_len, d_model))
        self.assertFalse(torch.isnan(output).any())
        self.assertFalse(torch.isinf(output).any())
        
        print("✓ Positional encoding test passed")
    
    def test_transformer_block(self):
        """Test transformer block implementation."""
        from ultra_optimized_transformers import UltraOptimizedTransformerBlock
        
        # Create transformer block
        d_model = 256
        num_heads = 8
        d_ff = 1024
        block = UltraOptimizedTransformerBlock(d_model, num_heads, d_ff)
        
        # Test forward pass
        batch_size = 2
        seq_len = 10
        x = torch.randn(batch_size, seq_len, d_model)
        
        output = block(x)
        
        self.assertEqual(output.shape, (batch_size, seq_len, d_model))
        self.assertFalse(torch.isnan(output).any())
        self.assertFalse(torch.isinf(output).any())
        
        print("✓ Transformer block test passed")
    
    def test_tokenizer_caching(self):
        """Test tokenizer caching functionality."""
        from ultra_optimized_transformers import UltraOptimizedTokenizer, UltraTransformersConfig
        
        config = UltraTransformersConfig(
            model_name="gpt2",
            cache_dir=self.cache_dir
        )
        
        tokenizer = UltraOptimizedTokenizer("gpt2", config)
        
        # Test single tokenization
        text = "Hello world"
        result1 = tokenizer.tokenize_single(text)
        result2 = tokenizer.tokenize_single(text)
        
        # Results should be identical (cached)
        self.assertTrue(torch.equal(result1["input_ids"], result2["input_ids"]))
        
        # Test batch tokenization
        texts = ["Hello world", "How are you"]
        result3 = tokenizer.tokenize_batch(texts)
        
        self.assertIn("input_ids", result3)
        self.assertIn("attention_mask", result3)
        
        print("✓ Tokenizer caching test passed")
    
    def test_dataset_creation(self):
        """Test dataset creation and DataLoader."""
        from ultra_optimized_deep_learning import UltraOptimizedDataset, create_ultra_optimized_dataloader, UltraTrainingConfig
        from transformers import AutoTokenizer
        
        config = UltraTrainingConfig(
            batch_size=2,
            dataloader_num_workers=0,  # Use 0 for testing
            cache_dir=self.cache_dir
        )
        
        # Create sample data
        texts = ["This is a positive review", "This is a negative review"] * 5
        labels = [1, 0] * 5
        
        # Create tokenizer
        tokenizer = AutoTokenizer.from_pretrained("gpt2", cache_dir=self.cache_dir)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create dataset
        dataset = UltraOptimizedDataset(texts, labels, tokenizer, config.max_length)
        
        self.assertEqual(len(dataset), len(texts))
        
        # Test single item
        item = dataset[0]
        self.assertIn("input_ids", item)
        self.assertIn("attention_mask", item)
        self.assertIn("labels", item)
        
        # Create DataLoader
        dataloader = create_ultra_optimized_dataloader(dataset, config)
        
        # Test batch
        batch = next(iter(dataloader))
        self.assertIn("input_ids", batch)
        self.assertIn("attention_mask", batch)
        self.assertIn("labels", batch)
        
        print("✓ Dataset and DataLoader test passed")
    
    def test_mixed_precision_context(self):
        """Test mixed precision context manager."""
        from ultra_optimized_deep_learning import nullcontext
        from torch.cuda.amp import autocast
        
        # Test nullcontext (when mixed precision is disabled)
        with nullcontext():
            x = torch.randn(2, 3)
            y = torch.randn(2, 3)
            z = x + y
        
        self.assertFalse(torch.isnan(z).any())
        
        # Test autocast (when mixed precision is enabled)
        if torch.cuda.is_available():
            with autocast():
                x = torch.randn(2, 3).cuda()
                y = torch.randn(2, 3).cuda()
                z = x + y
            
            self.assertFalse(torch.isnan(z).any())
        
        print("✓ Mixed precision context test passed")
    
    def test_performance_monitoring(self):
        """Test performance monitoring functionality."""
        from ultra_optimized_main import UltraPerformanceMonitor, UltraMainConfig
        
        config = UltraMainConfig(
            enable_wandb=False,  # Disable for testing
            enable_tensorboard=False,  # Disable for testing
            log_dir=self.log_dir
        )
        
        monitor = UltraPerformanceMonitor(config)
        
        # Test monitoring
        monitor.start_monitoring("test_task")
        
        # Simulate some work
        import time
        time.sleep(0.1)
        
        monitor.end_monitoring({"test_metric": 42})
        
        # Check that metrics were recorded
        self.assertIn("test_task", monitor.metrics)
        self.assertEqual(monitor.metrics["test_task"]["test_metric"], 42)
        
        print("✓ Performance monitoring test passed")
    
    def test_error_handling(self):
        """Test error handling and logging."""
        import structlog
        
        # Configure logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        logger = structlog.get_logger()
        
        # Test structured logging
        try:
            logger.info("Test message", test_param="value")
            print("✓ Structured logging test passed")
        except Exception as e:
            self.fail(f"Structured logging failed: {e}")
    
    def test_system_info(self):
        """Test system information gathering."""
        system_info = {
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
        
        self.assertIsInstance(system_info["torch_version"], str)
        self.assertIsInstance(system_info["cuda_available"], bool)
        self.assertIsInstance(system_info["device_count"], int)
        
        print(f"✓ System info test passed - PyTorch {system_info['torch_version']}, CUDA: {system_info['cuda_available']}")
    
    def test_memory_optimizations(self):
        """Test memory optimization features."""
        if torch.cuda.is_available():
            # Test GPU memory management
            initial_memory = torch.cuda.memory_allocated()
            
            # Allocate some memory
            x = torch.randn(1000, 1000).cuda()
            memory_after_alloc = torch.cuda.memory_allocated()
            
            # Clear cache
            torch.cuda.empty_cache()
            memory_after_clear = torch.cuda.memory_allocated()
            
            # Memory should be freed
            self.assertLessEqual(memory_after_clear, memory_after_alloc)
            
            print("✓ Memory optimization test passed")
        else:
            print("✓ Memory optimization test skipped (no CUDA)")
    
    def test_batch_processing(self):
        """Test batch processing functionality."""
        # Test batch tensor operations
        batch_size = 4
        seq_len = 10
        hidden_size = 256
        
        # Create batch
        batch = torch.randn(batch_size, seq_len, hidden_size)
        
        # Test batch operations
        mean_batch = batch.mean(dim=1)  # Average over sequence length
        max_batch = batch.max(dim=1)[0]  # Max over sequence length
        
        self.assertEqual(mean_batch.shape, (batch_size, hidden_size))
        self.assertEqual(max_batch.shape, (batch_size, hidden_size))
        
        print("✓ Batch processing test passed")
    
    def test_model_initialization(self):
        """Test model initialization with optimizations."""
        from ultra_optimized_deep_learning import UltraOptimizedTransformerModel, UltraTrainingConfig
        from transformers import AutoTokenizer
        
        config = UltraTrainingConfig(
            model_name="gpt2",
            use_mixed_precision=True,
            use_gradient_checkpointing=True,
            device=self.device,
            cache_dir=self.cache_dir
        )
        
        try:
            # Initialize tokenizer
            tokenizer = AutoTokenizer.from_pretrained("gpt2", cache_dir=self.cache_dir)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Initialize model
            model = UltraOptimizedTransformerModel("gpt2", config=config)
            
            # Test forward pass
            inputs = tokenizer("Hello world", return_tensors="pt", truncation=True, max_length=10)
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            self.assertIn("logits", outputs)
            self.assertFalse(torch.isnan(outputs["logits"]).any())
            
            print("✓ Model initialization test passed")
            
        except Exception as e:
            self.fail(f"Model initialization failed: {e}")

def run_performance_benchmark():
    """Run performance benchmark tests."""
    print("\n" + "="*50)
    print("PERFORMANCE BENCHMARK TESTS")
    print("="*50)
    
    # Test tensor operations performance
    if torch.cuda.is_available():
        print("Testing GPU tensor operations...")
        
        # Large matrix multiplication
        size = 2048
        a = torch.randn(size, size).cuda()
        b = torch.randn(size, size).cuda()
        
        start_time = torch.cuda.Event(enable_timing=True)
        end_time = torch.cuda.Event(enable_timing=True)
        
        start_time.record()
        c = torch.matmul(a, b)
        end_time.record()
        
        torch.cuda.synchronize()
        elapsed_time = start_time.elapsed_time(end_time)
        
        print(f"✓ GPU Matrix multiplication ({size}x{size}): {elapsed_time:.2f} ms")
        
        # Memory bandwidth test
        memory_size = 1024 * 1024 * 1024  # 1GB
        x = torch.randn(memory_size // 4, dtype=torch.float32).cuda()
        
        start_time.record()
        y = x * 2.0
        end_time.record()
        
        torch.cuda.synchronize()
        elapsed_time = start_time.elapsed_time(end_time)
        
        bandwidth = (memory_size / 1024 / 1024) / (elapsed_time / 1000)  # GB/s
        print(f"✓ GPU Memory bandwidth: {bandwidth:.2f} GB/s")
    
    # Test CPU operations
    print("Testing CPU tensor operations...")
    
    size = 512
    a = torch.randn(size, size)
    b = torch.randn(size, size)
    
    start_time = torch.cuda.Event(enable_timing=True)
    end_time = torch.cuda.Event(enable_timing=True)
    
    start_time.record()
    c = torch.matmul(a, b)
    end_time.record()
    
    torch.cuda.synchronize()
    elapsed_time = start_time.elapsed_time(end_time)
    
    print(f"✓ CPU Matrix multiplication ({size}x{size}): {elapsed_time:.2f} ms")

def main():
    """Run all tests."""
    print("🚀 Ultra-Optimized AI System Test Suite")
    print("="*50)
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance benchmarks
    run_performance_benchmark()
    
    print("\n" + "="*50)
    print("✅ All tests completed!")
    print("="*50)

if __name__ == "__main__":
    main()


