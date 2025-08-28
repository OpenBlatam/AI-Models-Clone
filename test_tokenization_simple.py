#!/usr/bin/env python3
"""
Simplified test file for tokenization and sequence handling components.
This file tests the core tokenization functionality without external dependencies.
"""

import torch
import torch.nn as nn
import numpy as np
import random
import traceback

# Mock imports to avoid dependency issues
class MockDiffusers:
    pass

class MockXFormers:
    pass

# Add mock modules to sys.modules
import sys
sys.modules['diffusers'] = MockDiffusers()
sys.modules['xformers'] = MockXFormers()

# Now import our tokenization components
from ultra_optimized_deep_learning import (
    AdvancedTokenizer, SubwordTokenizer, SequenceProcessor, 
    TextDataset, TextDataLoader
)

def test_advanced_tokenizer():
    """Test AdvancedTokenizer functionality."""
    print("Testing AdvancedTokenizer...")
    
    # Test data
    sample_texts = [
        "This is a sample text for testing tokenization.",
        "Another example with different words and structure.",
        "Short text.",
        "This is a very long text that should be truncated when it exceeds the maximum length allowed by the tokenizer configuration."
    ]
    
    try:
        # Initialize tokenizer
        tokenizer = AdvancedTokenizer(vocab_size=1000, max_length=64)
        tokenizer.build_vocabulary(sample_texts, min_freq=1)
        
        # Test encoding and decoding
        encoded = tokenizer.encode(sample_texts[0], add_special_tokens=True)
        decoded = tokenizer.decode(encoded, skip_special_tokens=True)
        
        print(f"  Original: {sample_texts[0]}")
        print(f"  Encoded: {encoded[:10]}...")  # Show first 10 tokens
        print(f"  Decoded: {decoded}")
        print(f"  Vocabulary size: {len(tokenizer.word2idx)}")
        
        # Test vocabulary info
        vocab_info = tokenizer.get_vocabulary_info()
        print(f"  Vocab info: {vocab_info}")
        
        # Test tensor output
        encoded_tensor = tokenizer.encode(sample_texts[0], add_special_tokens=True, return_tensors='pt')
        print(f"  Tensor shape: {encoded_tensor.shape}")
        
        print("  ✅ AdvancedTokenizer test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ AdvancedTokenizer test failed: {e}")
        traceback.print_exc()
        return False

def test_subword_tokenizer():
    """Test SubwordTokenizer functionality."""
    print("Testing SubwordTokenizer...")
    
    # Test data
    sample_texts = [
        "This is a sample text for testing subword tokenization.",
        "Another example with different words and structure.",
        "Short text for testing."
    ]
    
    try:
        # Initialize subword tokenizer
        subword_tokenizer = SubwordTokenizer(vocab_size=100, max_length=64)
        subword_tokenizer.train(sample_texts)
        
        # Test encoding and decoding
        encoded = subword_tokenizer.encode(sample_texts[0])
        decoded = subword_tokenizer.decode(encoded)
        
        print(f"  Original: {sample_texts[0]}")
        print(f"  Encoded: {encoded[:10]}...")
        print(f"  Decoded: {decoded}")
        print(f"  Vocabulary size: {len(subword_tokenizer.vocab)}")
        
        # Test with tensor input
        encoded_tensor = torch.tensor(encoded)
        decoded_from_tensor = subword_tokenizer.decode(encoded_tensor)
        print(f"  Decoded from tensor: {decoded_from_tensor}")
        
        print("  ✅ SubwordTokenizer test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ SubwordTokenizer test failed: {e}")
        traceback.print_exc()
        return False

def test_sequence_processor():
    """Test SequenceProcessor functionality."""
    print("Testing SequenceProcessor...")
    
    # Test data
    sample_texts = [
        "This is a sample text for testing sequence processing.",
        "Another example with different words and structure.",
        "Short text.",
        "This is a very long text that should be processed correctly by the sequence processor."
    ]
    
    try:
        # Initialize tokenizer and processor
        tokenizer = AdvancedTokenizer(vocab_size=1000, max_length=64)
        tokenizer.build_vocabulary(sample_texts, min_freq=1)
        
        processor = SequenceProcessor(max_length=32, return_tensors='pt')
        
        # Test batch processing
        processed_batch = processor.process_batch(sample_texts, tokenizer)
        
        print(f"  Batch input_ids shape: {processed_batch['input_ids'].shape}")
        print(f"  Batch attention_mask shape: {processed_batch['attention_mask'].shape}")
        
        # Test sliding windows
        long_text = " ".join(sample_texts * 3)  # Create a long text
        windows = processor.create_sliding_windows(long_text, tokenizer, window_size=32, stride=16)
        
        print(f"  Number of sliding windows: {len(windows)}")
        print(f"  First window length: {len(windows[0]) if windows else 0}")
        
        # Test data augmentation
        augmented = processor.apply_data_augmentation(sample_texts[0], 'random')
        print(f"  Original: {sample_texts[0]}")
        print(f"  Augmented: {augmented}")
        
        print("  ✅ SequenceProcessor test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ SequenceProcessor test failed: {e}")
        traceback.print_exc()
        return False

def test_text_dataset():
    """Test TextDataset functionality."""
    print("Testing TextDataset...")
    
    # Test data
    sample_texts = [
        "This is a sample text for testing dataset functionality.",
        "Another example with different words and structure.",
        "Short text for testing.",
        "This is a longer text to test the dataset processing capabilities."
    ]
    
    labels = [0, 1, 0, 1]  # Sample labels
    
    try:
        # Initialize tokenizer and processor
        tokenizer = AdvancedTokenizer(vocab_size=1000, max_length=64)
        tokenizer.build_vocabulary(sample_texts, min_freq=1)
        
        processor = SequenceProcessor(max_length=32, return_tensors='pt')
        
        # Create dataset
        dataset = TextDataset(sample_texts, labels, tokenizer, processor, max_length=32)
        
        print(f"  Dataset size: {len(dataset)}")
        
        # Test item access
        sample_item = dataset[0]
        print(f"  Sample item keys: {sample_item.keys()}")
        print(f"  Sample input_ids shape: {sample_item['input_ids'].shape}")
        print(f"  Sample attention_mask shape: {sample_item['attention_mask'].shape}")
        print(f"  Sample labels shape: {sample_item['labels'].shape}")
        
        # Test multiple items
        for i in range(min(3, len(dataset))):
            item = dataset[i]
            print(f"  Item {i}: input_ids shape {item['input_ids'].shape}, label {item['labels'].item()}")
        
        print("  ✅ TextDataset test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ TextDataset test failed: {e}")
        traceback.print_exc()
        return False

def test_text_dataloader():
    """Test TextDataLoader functionality."""
    print("Testing TextDataLoader...")
    
    # Test data
    sample_texts = [
        "This is a sample text for testing dataloader functionality.",
        "Another example with different words and structure.",
        "Short text for testing.",
        "This is a longer text to test the dataloader processing capabilities.",
        "Fifth text for comprehensive testing.",
        "Sixth text to ensure proper batching."
    ]
    
    labels = [0, 1, 0, 1, 0, 1]  # Sample labels
    
    try:
        # Initialize tokenizer and processor
        tokenizer = AdvancedTokenizer(vocab_size=1000, max_length=64)
        tokenizer.build_vocabulary(sample_texts, min_freq=1)
        
        processor = SequenceProcessor(max_length=32, return_tensors='pt')
        
        # Create dataset
        dataset = TextDataset(sample_texts, labels, tokenizer, processor, max_length=32)
        
        # Create data loader
        dataloader = TextDataLoader(dataset, batch_size=2, shuffle=False, num_workers=0)
        
        print(f"  Number of batches: {len(dataloader)}")
        
        # Test batch iteration
        for batch_idx, batch in enumerate(dataloader):
            print(f"  Batch {batch_idx}:")
            print(f"    input_ids shape: {batch['input_ids'].shape}")
            print(f"    attention_mask shape: {batch['attention_mask'].shape}")
            print(f"    labels shape: {batch['labels'].shape}")
            
            # Decode a sample
            sample_text = tokenizer.decode(batch['input_ids'][0].tolist(), skip_special_tokens=True)
            print(f"    Sample decoded text: {sample_text[:50]}...")
            
            if batch_idx >= 1:  # Show only first 2 batches
                break
        
        print("  ✅ TextDataLoader test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ TextDataLoader test failed: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Test integration of all components."""
    print("Testing Integration...")
    
    # Test data
    sample_texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning models require large amounts of data.",
        "Natural language processing enables computers to understand human language.",
        "Transformers have revolutionized the field of NLP."
    ]
    
    labels = [0, 1, 1, 1, 1]  # Binary classification labels
    
    try:
        # Initialize tokenizer
        print("  1. Initializing Advanced Tokenizer...")
        tokenizer = AdvancedTokenizer(vocab_size=1000, max_length=128)
        tokenizer.build_vocabulary(sample_texts, min_freq=1)
        
        print(f"     Vocabulary size: {len(tokenizer.word2idx)}")
        print(f"     Special tokens: {list(tokenizer.special_tokens.values())}")
        
        # Create dataset
        print("  2. Creating Text Dataset...")
        processor = SequenceProcessor(max_length=64, return_tensors='pt')
        dataset = TextDataset(sample_texts, labels, tokenizer, processor, max_length=64)
        
        print(f"     Dataset size: {len(dataset)}")
        print(f"     Sample item structure: {list(dataset[0].keys())}")
        
        # Create data loader
        print("  3. Creating Data Loader...")
        dataloader = TextDataLoader(dataset, batch_size=2, shuffle=True, num_workers=0)
        
        print(f"     Number of batches: {len(dataloader)}")
        
        # Process a few batches
        print("  4. Processing Batches...")
        for batch_idx, batch in enumerate(dataloader):
            print(f"     Batch {batch_idx + 1}:")
            print(f"       Input shape: {batch['input_ids'].shape}")
            print(f"       Attention mask shape: {batch['attention_mask'].shape}")
            print(f"       Labels shape: {batch['labels'].shape}")
            
            # Decode a sample
            sample_text = tokenizer.decode(batch['input_ids'][0].tolist(), skip_special_tokens=True)
            print(f"       Sample decoded text: {sample_text[:50]}...")
            
            if batch_idx >= 1:  # Show only first 2 batches
                break
        
        # Test with a simple model
        print("  5. Testing with Simple Model...")
        vocab_size = len(tokenizer.word2idx)
        embedding_dim = 128
        
        # Simple embedding model
        model = nn.Sequential(
            nn.Embedding(vocab_size, embedding_dim),
            nn.Linear(embedding_dim, 2)  # Binary classification
        )
        
        model.eval()
        with torch.no_grad():
            for batch in dataloader:
                outputs = model(batch['input_ids'])
                print(f"       Model output shape: {outputs.shape}")
                print(f"       Predictions: {torch.softmax(outputs, dim=-1)[0]}")
                break
        
        print("  ✅ Integration test passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tokenization tests."""
    print("="*60)
    print("TOKENIZATION AND SEQUENCE HANDLING TESTS")
    print("="*60)
    
    tests = [
        test_advanced_tokenizer,
        test_subword_tokenizer,
        test_sequence_processor,
        test_text_dataset,
        test_text_dataloader,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tokenization and sequence handling tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    main()

