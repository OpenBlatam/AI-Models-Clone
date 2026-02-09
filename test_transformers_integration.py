#!/usr/bin/env python3
"""
🧪 Test Script for Transformers Integration

This script tests the integration of Hugging Face Transformers library
with the Enhanced AI Model Demos System.
"""

import time
import torch
import traceback
from typing import Dict, List, Any

def print_header():
    """Print test header."""
    print("=" * 80)
    print("🧪 Transformers Integration Test Suite")
    print("=" * 80)
    print()

def test_imports():
    """Test if all required packages can be imported."""
    print("📦 Testing package imports...")
    
    packages_to_test = [
        ("transformers", "transformers"),
        ("tokenizers", "tokenizers"),
        ("accelerate", "accelerate"),
        ("peft", "peft"),
        ("safetensors", "safetensors"),
        ("sentencepiece", "sentencepiece"),
        ("protobuf", "google.protobuf"),
        ("nltk", "nltk"),
        ("spacy", "spacy"),
        ("textblob", "textblob")
    ]
    
    failed_imports = []
    
    for package_name, import_name in packages_to_test:
        try:
            __import__(import_name)
            print(f"✅ {package_name} imported successfully")
        except ImportError as e:
            print(f"❌ {package_name} failed to import: {e}")
            failed_imports.append(package_name)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_basic_transformers():
    """Test basic transformers functionality."""
    print("\n🔧 Testing basic transformers functionality...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        
        # Test BERT
        print("Testing BERT model...")
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        model = AutoModel.from_pretrained("bert-base-uncased")
        
        # Test tokenization
        text = "Hello, world! This is a test."
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        # Test inference
        with torch.no_grad():
            outputs = model(**inputs)
        
        print(f"✅ BERT test passed - Output shape: {outputs.last_hidden_state.shape}")
        
        # Test GPT-2
        print("Testing GPT-2 model...")
        gpt_tokenizer = AutoTokenizer.from_pretrained("gpt2")
        gpt_model = AutoModel.from_pretrained("gpt2")
        
        # Add padding token if not present
        if gpt_tokenizer.pad_token is None:
            gpt_tokenizer.pad_token = gpt_tokenizer.eos_token
        
        gpt_inputs = gpt_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad():
            gpt_outputs = gpt_model(**gpt_inputs)
        
        print(f"✅ GPT-2 test passed - Output shape: {gpt_outputs.last_hidden_state.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic transformers test failed: {e}")
        traceback.print_exc()
        return False

def test_pipelines():
    """Test transformers pipelines."""
    print("\n🚀 Testing transformers pipelines...")
    
    try:
        from transformers import pipeline
        
        # Test sentiment analysis
        print("Testing sentiment analysis pipeline...")
        sentiment_analyzer = pipeline("sentiment-analysis")
        sentiment_result = sentiment_analyzer("I love this movie!")
        print(f"✅ Sentiment analysis: {sentiment_result}")
        
        # Test text generation
        print("Testing text generation pipeline...")
        text_generator = pipeline("text-generation", model="gpt2", max_length=50)
        generation_result = text_generator("The future of AI is")
        print(f"✅ Text generation: {generation_result[0]['generated_text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipelines test failed: {e}")
        traceback.print_exc()
        return False

def test_advanced_features():
    """Test advanced transformers features."""
    print("\n🎨 Testing advanced features...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from transformers import TrainingArguments, Trainer
        from datasets import Dataset
        
        # Test model configuration
        print("Testing model configuration...")
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
        
        print(f"✅ Model configured with {model.config.num_labels} labels")
        
        # Test dataset preparation
        print("Testing dataset preparation...")
        data = {
            "text": ["Sample text 1", "Sample text 2", "Sample text 3"],
            "label": [0, 1, 2]
        }
        dataset = Dataset.from_dict(data)
        
        def tokenize_function(examples):
            return tokenizer(examples["text"], padding="max_length", truncation=True)
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        print(f"✅ Dataset prepared with {len(tokenized_dataset)} samples")
        
        # Test training arguments
        print("Testing training arguments...")
        training_args = TrainingArguments(
            output_dir="./test_results",
            num_train_epochs=1,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            warmup_steps=10,
            logging_steps=5,
        )
        print("✅ Training arguments configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        traceback.print_exc()
        return False

def test_peft_integration():
    """Test PEFT (Parameter-Efficient Fine-tuning) integration."""
    print("\n🔬 Testing PEFT integration...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import LoraConfig, get_peft_model, TaskType
        
        # Test LoRA configuration
        print("Testing LoRA configuration...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        
        # Add padding token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["c_attn"]
        )
        
        # Apply LoRA
        peft_model = get_peft_model(model, lora_config)
        peft_model.print_trainable_parameters()
        
        print("✅ PEFT integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ PEFT integration test failed: {e}")
        traceback.print_exc()
        return False

def test_performance_optimization():
    """Test performance optimization features."""
    print("\n⚡ Testing performance optimization...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        import time
        
        # Test model caching
        print("Testing model caching...")
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        model = AutoModel.from_pretrained("distilbert-base-uncased")
        
        # Test batch processing
        print("Testing batch processing...")
        texts = ["Text 1", "Text 2", "Text 3", "Text 4"]
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        
        # Warmup
        with torch.no_grad():
            _ = model(**inputs)
        
        # Benchmark
        start_time = time.time()
        with torch.no_grad():
            for _ in range(10):
                _ = model(**inputs)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"✅ Batch processing: {avg_time*1000:.2f}ms per batch")
        
        # Test GPU memory management
        if torch.cuda.is_available():
            print("Testing GPU memory management...")
            torch.cuda.empty_cache()
            print(f"✅ GPU memory cleared. Current: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance optimization test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🚨 Testing error handling...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        
        # Test invalid model name
        print("Testing invalid model handling...")
        try:
            tokenizer = AutoTokenizer.from_pretrained("invalid-model-name")
            print("❌ Should have failed with invalid model name")
            return False
        except Exception as e:
            print(f"✅ Correctly handled invalid model: {type(e).__name__}")
        
        # Test long text handling
        print("Testing long text handling...")
        tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        long_text = "This is a very long text. " * 1000
        
        try:
            inputs = tokenizer(long_text, return_tensors="pt", max_length=512, truncation=True)
            print(f"✅ Long text handled correctly - Length: {inputs['input_ids'].shape[1]}")
        except Exception as e:
            print(f"❌ Long text handling failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def run_performance_benchmarks():
    """Run performance benchmarks for different models."""
    print("\n📊 Running performance benchmarks...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        import time
        
        models_to_benchmark = [
            "bert-base-uncased",
            "distilbert-base-uncased",
            "gpt2"
        ]
        
        benchmark_results = {}
        
        for model_name in models_to_benchmark:
            print(f"Benchmarking {model_name}...")
            
            try:
                # Load model
                start_time = time.time()
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModel.from_pretrained(model_name)
                load_time = time.time() - start_time
                
                # Prepare input
                text = "This is a test sentence for benchmarking."
                if model_name == "gpt2" and tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                
                # Warmup
                with torch.no_grad():
                    _ = model(**inputs)
                
                # Benchmark inference
                start_time = time.time()
                with torch.no_grad():
                    for _ in range(50):
                        _ = model(**inputs)
                inference_time = time.time() - start_time
                
                avg_inference_time = inference_time / 50
                
                # Memory usage
                if torch.cuda.is_available():
                    memory_mb = torch.cuda.memory_allocated() / 1024**2
                else:
                    memory_mb = 0
                
                benchmark_results[model_name] = {
                    "load_time": load_time,
                    "avg_inference_time": avg_inference_time,
                    "memory_mb": memory_mb
                }
                
                print(f"✅ {model_name}: {avg_inference_time*1000:.2f}ms per inference, {memory_mb:.2f}MB")
                
            except Exception as e:
                print(f"❌ {model_name} benchmark failed: {e}")
                benchmark_results[model_name] = {"error": str(e)}
        
        # Print summary
        print("\n📈 Benchmark Summary:")
        print("-" * 60)
        for model_name, results in benchmark_results.items():
            if "error" in results:
                print(f"{model_name}: ❌ {results['error']}")
            else:
                print(f"{model_name}: {results['avg_inference_time']*1000:.2f}ms, {results['memory_mb']:.2f}MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmarks failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print_header()
    
    # Check if CUDA is available
    if torch.cuda.is_available():
        print(f"🖥️  CUDA available: {torch.cuda.device_count()} GPU(s)")
        print(f"   Primary GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA version: {torch.version.cuda}")
    else:
        print("ℹ️  CUDA not available, using CPU")
    
    print()
    
    # Run tests
    tests = [
        ("Package Imports", test_imports),
        ("Basic Transformers", test_basic_transformers),
        ("Pipelines", test_pipelines),
        ("Advanced Features", test_advanced_features),
        ("PEFT Integration", test_peft_integration),
        ("Performance Optimization", test_performance_optimization),
        ("Error Handling", test_error_handling),
        ("Performance Benchmarks", run_performance_benchmarks)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            traceback.print_exc()
        
        print("-" * 60)
    
    # Print results
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Transformers integration is working perfectly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the output above for details.")
    
    print("\n📚 Next steps:")
    print("1. Check failed tests and resolve any issues")
    print("2. Review the TRANSFORMERS_INTEGRATION_GUIDE.md for detailed usage")
    print("3. Integrate transformers into your enhanced UI demos")
    print("4. Start building NLP applications!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
