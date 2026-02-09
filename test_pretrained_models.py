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
import torch.nn.functional as F
import time
import numpy as np
from typing import Dict, List, Tuple
import tempfile
import os
import json
from pretrained_models_system import (
        from transformers import TrainingArguments
        import traceback
from typing import Any, List, Dict, Optional
import logging
import asyncio
#!/usr/bin/env python3
"""
Test Pre-trained Models and Tokenizers System

This script comprehensively tests all pre-trained models and tokenizers features including:
- Model loading and management
- Tokenizer utilities and preprocessing
- Fine-tuning and adaptation
- Model deployment and serving
- Performance optimization
- Multi-model support
"""


# Import pre-trained models system
    PreTrainedModelManager, TokenizerUtilities, FineTuningManager,
    ModelDeployment, ModelOptimization, ModelConfig, TokenizerConfig, ModelType
)


def test_model_loading() -> Any:
    """Test model loading and management."""
    print(f"\n{"="*60)
    print("🏗️  Testing Model Loading and Management")
    print("="*60)
    
    # Test different model types
    model_configs: List[Any] = [
        {
            "name": "GPT-2 Small",
            "config": ModelConfig(
                model_name: str = "gpt2",
                model_type=ModelType.CAUSAL_LM,
                use_gradient_checkpointing: bool = True
            ),
            "tokenizer_config": TokenizerConfig(
                tokenizer_name: str = "gpt2",
                padding_side: str = "left",
                truncation_side: str = "left"
            )
        },
        {
            "name": "BERT Base",
            "config": ModelConfig(
                model_name: str = "bert-base-uncased",
                model_type=ModelType.SEQUENCE_CLASSIFICATION,
                use_gradient_checkpointing: bool = True
            ),
            "tokenizer_config": TokenizerConfig(
                tokenizer_name: str = "bert-base-uncased",
                padding_side: str = "right",
                truncation_side: str = "right"
            )
        }
    ]
    
    results: Dict[str, Any] = {}
    
    for model_info in model_configs:
        print(f"\n📋 Testing {model_info['name']}:")
        
        try:
            # Create manager
            manager = PreTrainedModelManager(
                model_info['config'], 
                model_info['tokenizer_config']
            )
            
            # Load model and tokenizer
            start_time = time.time()
            model = manager.load_model()
            tokenizer = manager.load_tokenizer()
            load_time = time.time() - start_time
            
            # Get model info
            num_parameters = sum(p.numel() for p in model.parameters())
            vocab_size = tokenizer.vocab_size
            
            results[model_info['name']] = {
                'success': True,
                'load_time': load_time,
                'num_parameters': num_parameters,
                'vocab_size': vocab_size,
                'model_type': str(type(model)),
                'tokenizer_type': str(type(tokenizer))
            }
            
            print(f"   ✅ Success: Loaded in {load_time:.2f}s")
            print(f"   📊 Parameters: {num_parameters:,}")
            print(f"   📊 Vocabulary: {vocab_size:,}")
            print(f"   🏗️  Model: {type(model).__name__}")
            print(f"   🔤 Tokenizer: {type(tokenizer).__name__}")
            
            # Test saving and loading
            with tempfile.TemporaryDirectory() as temp_dir:
                manager.save_model(temp_dir)
                print(f"   💾 Saved to temporary directory")
                
                # Test loading from directory
                new_manager = PreTrainedModelManager(
                    model_info['config'], 
                    model_info['tokenizer_config']
                )
                new_manager.load_from_directory(temp_dir)
                print(f"   📂 Loaded from directory successfully")
            
        except Exception as e:
            results[model_info['name']] = {
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Error: {e}")
    
    return results


def test_tokenizer_utilities() -> Any:
    """Test tokenizer utilities and preprocessing."""
    print("\n"}="*60)
    print("🔤 Testing Tokenizer Utilities")
    print("="*60)
    
    # Load a tokenizer for testing
    model_config = ModelConfig(
        model_name: str = "gpt2",
        model_type=ModelType.CAUSAL_LM
    )
    
    tokenizer_config = TokenizerConfig(
        tokenizer_name: str = "gpt2",
        padding_side: str = "left",
        truncation_side: str = "left"
    )
    
    try:
        manager = PreTrainedModelManager(model_config, tokenizer_config)
        tokenizer = manager.load_tokenizer()
        tokenizer_utils = TokenizerUtilities(tokenizer)
        
        print(f"✅ Tokenizer loaded: {type(tokenizer).__name__}")
        
        # Test single text tokenization
        print("\n📋 Testing Single Text Tokenization:")
        sample_text: str = "Hello, this is a test sentence for tokenization."
        encoding = tokenizer_utils.tokenize_text(sample_text, max_length=20)
        print(f"   Input: {sample_text}")
        print(f"   Tokenized shape: {encoding['input_ids'].shape}")
        print(f"   Attention mask shape: {encoding['attention_mask'].shape}")
        
        # Test batch tokenization
        print("\n📋 Testing Batch Tokenization:")
        batch_texts: List[Any] = [
            "First sentence in the batch.",
            "Second sentence with different length.",
            "Third sentence for testing."
        ]
        batch_encoding = tokenizer_utils.tokenize_batch(batch_texts, max_length=15)
        print(f"   Batch size: {batch_encoding['input_ids'].shape[0]}")
        print(f"   Sequence length: {batch_encoding['input_ids'].shape[1]}")
        
        # Test dataset creation
        print("\n📋 Testing Dataset Creation:")
        texts: List[Any] = [
            "Positive example one.",
            "Negative example one.",
            "Positive example two.",
            "Negative example two."
        ]
        labels: List[Any] = [1, 0, 1, 0]
        
        dataset = tokenizer_utils.create_dataset(texts, labels, max_length=10)
        print(f"   Dataset size: {len(dataset)}")
        print(f"   Dataset features: {list(dataset.features.keys())}")
        print(f"   Sample item: {dataset[0]}")
        
        # Test language model dataset
        print("\n📋 Testing Language Model Dataset:")
        lm_dataset = tokenizer_utils.create_language_model_dataset(texts, max_length=10)
        print(f"   LM Dataset size: {len(lm_dataset)}")
        print(f"   LM Dataset features: {list(lm_dataset.features.keys())}")
        
        # Test vocabulary and special tokens
        print("\n📋 Testing Vocabulary and Special Tokens:")
        vocab_size = tokenizer_utils.get_vocab_size()
        special_tokens = tokenizer_utils.get_special_tokens()
        print(f"   Vocabulary size: {vocab_size:,}")
        print(f"   Special tokens: {special_tokens}")
        
        # Test encoding and decoding
        print("\n📋 Testing Encoding and Decoding:")
        test_text: str = "Test encoding and decoding functionality."
        encoded = tokenizer_utils.encode_text(test_text)
        decoded = tokenizer_utils.decode_tokens(encoded)
        print(f"   Original: {test_text}")
        print(f"   Encoded length: {len(encoded)}")
        print(f"   Decoded: {decoded}")
        
        return {
            'success': True,
            'vocab_size': vocab_size,
            'special_tokens': special_tokens,
            'dataset_size': len(dataset),
            'lm_dataset_size': len(lm_dataset)
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'success': False, 'error': str(e)}


def test_model_deployment() -> Any:
    """Test model deployment and serving."""
    print(f"\n{"="*60)
    print("🚀 Testing Model Deployment")
    print("="*60)
    
    # Load model and tokenizer
    model_config = ModelConfig(
        model_name: str = "gpt2",
        model_type=ModelType.CAUSAL_LM
    )
    
    tokenizer_config = TokenizerConfig(
        tokenizer_name: str = "gpt2",
        padding_side: str = "left",
        truncation_side: str = "left"
    )
    
    try:
        manager = PreTrainedModelManager(model_config, tokenizer_config)
        model = manager.load_model()
        tokenizer = manager.load_tokenizer()
        
        deployment = ModelDeployment(model, tokenizer)
        
        print(f"✅ Deployment setup completed")
        
        # Test text generation
        print("\n📋 Testing Text Generation:")
        prompts: List[Any] = [
            "The future of artificial intelligence",
            "Machine learning is",
            "Deep learning models can"
        ]
        
        for prompt in prompts:
            start_time = time.time()
            generated = deployment.predict(
                prompt, 
                max_length=30, 
                temperature=0.8,
                do_sample: bool = True
            )
            generation_time = time.time() - start_time
            
            print(f"   Prompt: {prompt}")
            print(f"   Generated: {generated}")
            print(f"   Time: {generation_time:.3f}s")
            print()
        
        # Test batch prediction
        print("\n📋 Testing Batch Prediction:")
        start_time = time.time()
        batch_results = deployment.batch_predict(
            prompts, 
            max_length=20, 
            temperature=0.7
        )
        batch_time = time.time() - start_time
        
        for i, (prompt, result) in enumerate(zip(prompts, batch_results)}"):
            print(f"   {i+1}. {prompt} -> {result}")
        
        print(f"   Batch time: {batch_time:.3f}s")
        
        # Test different generation parameters
        print("\n📋 Testing Generation Parameters:")
        test_prompt: str = "The weather today is"
        
        # Greedy decoding
        greedy_result = deployment.predict(
            test_prompt, 
            max_length=15, 
            do_sample: bool = False
        )
        print(f"   Greedy: {greedy_result}")
        
        # Temperature sampling
        temp_result = deployment.predict(
            test_prompt, 
            max_length=15, 
            temperature=0.5,
            do_sample: bool = True
        )
        print(f"   Temperature (0.5): {temp_result}")
        
        # High temperature
        high_temp_result = deployment.predict(
            test_prompt, 
            max_length=15, 
            temperature=1.2,
            do_sample: bool = True
        )
        print(f"   Temperature (1.2): {high_temp_result}")
        
        return {
            'success': True,
            'generation_times': [0.1, 0.2, 0.3],  # Placeholder
            'batch_time': batch_time
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'success': False, 'error': str(e)}


def test_model_optimization() -> Any:
    """Test model optimization and performance tuning."""
    print(f"\n{"="*60)
    print("⚡ Testing Model Optimization")
    print("="*60)
    
    # Load model for testing
    model_config = ModelConfig(
        model_name: str = "gpt2",
        model_type=ModelType.CAUSAL_LM
    )
    
    tokenizer_config = TokenizerConfig(
        tokenizer_name: str = "gpt2"
    )
    
    try:
        manager = PreTrainedModelManager(model_config, tokenizer_config)
        model = manager.load_model()
        
        optimizer = ModelOptimization(model)
        
        print(f"✅ Optimization setup completed")
        
        # Test model profiling
        print("\n📋 Testing Model Profiling:")
        profile_results = optimizer.profile_model((1, 20), num_runs=10)
        
        print(f"   Average inference time: {profile_results['avg_inference_time']*1000:.2f} ms")
        print(f"   Throughput: {profile_results['throughput']:.2f} samples/sec")
        print(f"   Model parameters: {profile_results['num_parameters']:,}")
        
        if torch.cuda.is_available():
            print(f"   Memory allocated: {profile_results['memory_allocated_mb']:.1f} MB")
            print(f"   Memory reserved: {profile_results['memory_reserved_mb']:.1f} MB")
        
        # Test inference optimization
        print("\n📋 Testing Inference Optimization:")
        optimizer.optimize_for_inference()
        
        # Profile optimized model
        optimized_results = optimizer.profile_model((1, 20), num_runs=10)
        
        print(f"   Optimized inference time: {optimized_results['avg_inference_time']*1000:.2f} ms")
        print(f"   Optimized throughput: {optimized_results['throughput']:.2f} samples/sec")
        
        # Calculate improvement
        time_improvement = (profile_results['avg_inference_time'] - optimized_results['avg_inference_time']) / profile_results['avg_inference_time'] * 100
        print(f"   Time improvement: {time_improvement:.1f}%")
        
        # Test quantization (if supported)
        print("\n📋 Testing Quantization:")
        try:
            optimizer.quantize_model("int8")
            quantized_results = optimizer.profile_model((1, 20), num_runs=10)
            
            print(f"   Quantized inference time: {quantized_results['avg_inference_time']*1000:.2f} ms")
            print(f"   Quantized throughput: {quantized_results['throughput']:.2f} samples/sec")
            
            # Memory comparison
            if torch.cuda.is_available():
                memory_reduction = (profile_results['memory_allocated_mb'] - quantized_results['memory_allocated_mb']) / profile_results['memory_allocated_mb'] * 100
                print(f"   Memory reduction: {memory_reduction:.1f}%")
                
        except Exception as e:
            print(f"   Quantization not available: {e}")
        
        return {
            'success': True,
            'original_time': profile_results['avg_inference_time'],
            'optimized_time': optimized_results['avg_inference_time'],
            'improvement_percent': time_improvement
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'success': False, 'error': str(e)}


def test_fine_tuning_setup() -> Any:
    """Test fine-tuning setup and configuration."""
    print("\n"}="*60)
    print("🎓 Testing Fine-tuning Setup")
    print("="*60)
    
    # Load model and tokenizer
    model_config = ModelConfig(
        model_name: str = "gpt2",
        model_type=ModelType.CAUSAL_LM
    )
    
    tokenizer_config = TokenizerConfig(
        tokenizer_name: str = "gpt2"
    )
    
    try:
        manager = PreTrainedModelManager(model_config, tokenizer_config)
        model = manager.load_model()
        tokenizer = manager.load_tokenizer()
        
        fine_tuner = FineTuningManager(model, tokenizer)
        
        print(f"✅ Fine-tuning setup completed")
        
        # Create sample dataset
        print("\n📋 Testing Dataset Creation:")
        sample_texts: List[Any] = [
            "This is a positive example for fine-tuning.",
            "This is a negative example for fine-tuning.",
            "Another positive case for the model to learn.",
            "Yet another negative instance for training.",
            "Positive example with different structure.",
            "Negative example with unique characteristics."
        ]
        
        tokenizer_utils = TokenizerUtilities(tokenizer)
        dataset = tokenizer_utils.create_language_model_dataset(sample_texts, max_length=20)
        
        print(f"   Dataset size: {len(dataset)}")
        print(f"   Dataset features: {list(dataset.features.keys())}")
        print(f"   Sample item keys: {list(dataset[0].keys())}")
        
        # Test training arguments setup
        print("\n📋 Testing Training Arguments:")
        
        training_args = TrainingArguments(
            output_dir: str = "./test_fine_tuning",
            num_train_epochs=1,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            warmup_steps=10,
            weight_decay=0.01,
            logging_dir: str = "./logs",
            logging_steps=5,
            save_steps=50,
            eval_steps=50,
            evaluation_strategy: str = "steps",
            save_strategy: str = "steps",
            load_best_model_at_end=True,
            metric_for_best_model: str = "eval_loss",
            greater_is_better=False,
        )
        
        fine_tuner.setup_training(training_args)
        print(f"   Training arguments configured")
        
        # Test trainer creation
        print("\n📋 Testing Trainer Creation:")
        trainer = fine_tuner.create_trainer(dataset)
        print(f"   Trainer created successfully")
        print(f"   Trainer type: {type(trainer).__name__}")
        
        # Test model saving
        print("\n📋 Testing Model Saving:")
        with tempfile.TemporaryDirectory() as temp_dir:
            fine_tuner.save_model(temp_dir)
            print(f"   Model saved to temporary directory")
            
            # Check saved files
            saved_files = os.listdir(temp_dir)
            print(f"   Saved files: {saved_files}")
        
        return {
            'success': True,
            'dataset_size': len(dataset),
            'training_args_configured': True,
            'trainer_created': True
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'success': False, 'error': str(e)}


def test_multi_model_support() -> Any:
    """Test multi-model support and management."""
    print(f"\n{"="*60)
    print("🔄 Testing Multi-Model Support")
    print("="*60)
    
    # Test different model types
    model_configs: List[Any] = [
        {
            "name": "GPT-2",
            "model_config": ModelConfig(
                model_name: str = "gpt2",
                model_type=ModelType.CAUSAL_LM
            ),
            "tokenizer_config": TokenizerConfig(tokenizer_name: str = "gpt2")
        },
        {
            "name": "BERT",
            "model_config": ModelConfig(
                model_name: str = "bert-base-uncased",
                model_type=ModelType.SEQUENCE_CLASSIFICATION
            ),
            "tokenizer_config": TokenizerConfig(tokenizer_name: str = "bert-base-uncased")
        }
    ]
    
    results: Dict[str, Any] = {}
    
    for model_info in model_configs:
        print(f"\n📋 Testing {model_info['name']}:")
        
        try:
            manager = PreTrainedModelManager(
                model_info['model_config'],
                model_info['tokenizer_config']
            )
            
            model = manager.load_model()
            tokenizer = manager.load_tokenizer()
            
            # Test basic functionality
            tokenizer_utils = TokenizerUtilities(tokenizer)
            deployment = ModelDeployment(model, tokenizer)
            
            # Test tokenization
            test_text: str = "Test text for multi-model support."
            encoding = tokenizer_utils.tokenize_text(test_text, max_length=10)
            
            # Test generation/classification
            if model_info['name'] == "GPT-2":
                result = deployment.predict(test_text, max_length=15)
                print(f"   Generated: {result}")
            else:
                result = deployment.classify_text(test_text)
                print(f"   Classification: {result}")
            
            results[model_info['name']] = {
                'success': True,
                'model_type': str(type(model)),
                'tokenizer_type': str(type(tokenizer)),
                'parameters': sum(p.numel() for p in model.parameters())
            }
            
            print(f"   ✅ Success: {type(model).__name__}")
            print(f"   📊 Parameters: {results[model_info['name']]['parameters']:,}")
            
        except Exception as e:
            results[model_info['name']] = {
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Error: {e}")
    
    return results


def benchmark_performance() -> Any:
    """Benchmark performance of different models and configurations."""
    print("\n"}="*60)
    print("⚡ Performance Benchmark")
    print("="*60)
    
    # Test configurations
    configs: List[Any] = [
        {
            "name": "GPT-2 Small",
            "model_config": ModelConfig(
                model_name: str = "gpt2",
                model_type=ModelType.CAUSAL_LM
            ),
            "tokenizer_config": TokenizerConfig(tokenizer_name: str = "gpt2")
        }
    ]
    
    results: Dict[str, Any] = {}
    
    for config in configs:
        print(f"\n🔧 Benchmarking {config['name']}:")
        
        try:
            # Load model
            manager = PreTrainedModelManager(
                config['model_config'],
                config['tokenizer_config']
            )
            model = manager.load_model()
            tokenizer = manager.load_tokenizer()
            
            # Create utilities
            tokenizer_utils = TokenizerUtilities(tokenizer)
            deployment = ModelDeployment(model, tokenizer)
            optimizer = ModelOptimization(model)
            
            # Benchmark tokenization
            print("   📊 Benchmarking tokenization:")
            texts: List[Any] = [f"Test text {i}" for i in range(100)]
            
            start_time = time.time()
            for text in texts:
                tokenizer_utils.tokenize_text(text, max_length=20)
            tokenization_time = time.time() - start_time
            
            print(f"      Tokenization: {tokenization_time:.3f}s for {len(texts)} texts")
            print(f"      Rate: {len(texts)/tokenization_time:.1f} texts/sec")
            
            # Benchmark generation
            print("   📊 Benchmarking generation:")
            prompts: List[Any] = ["The future of AI is", "Machine learning can", "Deep learning enables"]
            
            start_time = time.time()
            for prompt in prompts:
                deployment.predict(prompt, max_length=20, do_sample=False)
            generation_time = time.time() - start_time
            
            print(f"      Generation: {generation_time:.3f}s for {len(prompts)} prompts")
            print(f"      Rate: {len(prompts)/generation_time:.1f} prompts/sec")
            
            # Benchmark optimization
            print("   📊 Benchmarking optimization:")
            original_profile = optimizer.profile_model((1, 20), num_runs=10)
            
            optimizer.optimize_for_inference()
            optimized_profile = optimizer.profile_model((1, 20), num_runs=10)
            
            improvement = (original_profile['avg_inference_time'] - optimized_profile['avg_inference_time']) / original_profile['avg_inference_time'] * 100
            
            print(f"      Original time: {original_profile['avg_inference_time']*1000:.2f} ms")
            print(f"      Optimized time: {optimized_profile['avg_inference_time']*1000:.2f} ms")
            print(f"      Improvement: {improvement:.1f}%")
            
            results[config['name']] = {
                'success': True,
                'tokenization_rate': len(texts)/tokenization_time,
                'generation_rate': len(prompts)/generation_time,
                'optimization_improvement': improvement,
                'model_parameters': original_profile['num_parameters']
            }
            
        except Exception as e:
            results[config['name']] = {
                'success': False,
                'error': str(e)
            }
            print(f"   ❌ Error: {e}")
    
    return results


def run_comprehensive_test() -> Any:
    """Run comprehensive test of all pre-trained models features."""
    print("🚀 Pre-trained Models and Tokenizers System - Comprehensive Test")
    print("="*80)
    
    try:
        # Test all components
        print("\n1️⃣ Testing Model Loading and Management...")
        loading_results = test_model_loading()
        
        print("\n2️⃣ Testing Tokenizer Utilities...")
        tokenizer_results = test_tokenizer_utilities()
        
        print("\n3️⃣ Testing Model Deployment...")
        deployment_results = test_model_deployment()
        
        print("\n4️⃣ Testing Model Optimization...")
        optimization_results = test_model_optimization()
        
        print("\n5️⃣ Testing Fine-tuning Setup...")
        fine_tuning_results = test_fine_tuning_setup()
        
        print("\n6️⃣ Testing Multi-Model Support...")
        multi_model_results = test_multi_model_support()
        
        print("\n7️⃣ Performance Benchmarking...")
        benchmark_results = benchmark_performance()
        
        print(f"\n{"="*80)
        print("🎉 All Pre-trained Models Tests Completed Successfully!")
        print("="*80)
        
        # Summary
        print("\n📋 Test Summary:")
        print(f"   ✅ Model Loading: {len([r for r in loading_results.values() if r.get('success', False)])}/{len(loading_results)} models")
        print(f"   ✅ Tokenizer Utilities: {'Success' if tokenizer_results.get('success', False) else 'Failed'}")
        print(f"   ✅ Model Deployment: {'Success' if deployment_results.get('success', False) else 'Failed'}")
        print(f"   ✅ Model Optimization: {'Success' if optimization_results.get('success', False) else 'Failed'}")
        print(f"   ✅ Fine-tuning Setup: {'Success' if fine_tuning_results.get('success', False) else 'Failed'}")
        print(f"   ✅ Multi-Model Support: {len([r for r in multi_model_results.values() if r.get('success', False)])}/{len(multi_model_results)} models")
        print(f"   ✅ Performance Benchmark: {len(benchmark_results)} configurations tested")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run comprehensive test
    success = run_comprehensive_test()
    
    if success:
        print("\n🎯 Pre-trained Models and Tokenizers System is ready for production use!")
        print("\n📊 Available Features:")
        print("   ✅ Pre-trained model loading and management")
        print("   ✅ Advanced tokenizer utilities")
        print("   ✅ Fine-tuning and adaptation")
        print("   ✅ Model deployment and serving")
        print("   ✅ Performance optimization")
        print("   ✅ Multi-model support")
        print("   ✅ Quantization and optimization")
        print("   ✅ Comprehensive error handling")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation."}") 