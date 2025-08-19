from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

# Constants
BUFFER_SIZE = 1024

import sys
import os
import logging
import torch
import torch.nn.functional as F
from pathlib import Path
from attention_mechanisms_implementation import (
    import time
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Runner script for Attention Mechanisms and Positional Encodings Implementation
Demonstrates various attention mechanisms and positional encoding strategies.
"""


# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

    AttentionConfig, PositionalEncoding, RelativePositionalEncoding,
    RotaryPositionalEncoding, MultiHeadAttention, ScaledDotProductAttention,
    SelfAttention, CrossAttention, AttentionBlock, demonstrate_attention_mechanisms
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_positional_encoding_demo():
    """Demonstrate different positional encoding strategies."""
    print("\n" + "="*60)
    print("POSITIONAL ENCODING DEMONSTRATION")
    print("="*60)
    
    # Test parameters
    d_model = 768
    seq_len = 128
    batch_size = 2
    
    print(f"Testing with d_model={d_model}, seq_len={seq_len}, batch_size={batch_size}")
    
    # 1. Absolute Positional Encoding
    print("\n1. Absolute Positional Encoding:")
    abs_pe = PositionalEncoding(d_model, max_len=512)
    abs_input = torch.randn(seq_len, batch_size, d_model)
    abs_output = abs_pe(abs_input)
    print(f"   Input shape: {abs_input.shape}")
    print(f"   Output shape: {abs_output.shape}")
    print(f"   Positional encoding shape: {abs_pe.pe.shape}")
    
    # 2. Relative Positional Encoding
    print("\n2. Relative Positional Encoding:")
    rel_pe = RelativePositionalEncoding(d_model, max_relative_position=32)
    rel_embeddings = rel_pe(seq_len, torch.device('cpu'))
    print(f"   Sequence length: {seq_len}")
    print(f"   Relative embeddings shape: {rel_embeddings.shape}")
    print(f"   Max relative position: {rel_pe.max_relative_position}")
    
    # 3. Rotary Positional Encoding
    print("\n3. Rotary Positional Encoding:")
    rotary_dim = 64
    rotary_pe = RotaryPositionalEncoding(dim=rotary_dim, max_position_embeddings=512)
    rotary_input = torch.randn(batch_size, seq_len, 12, rotary_dim)  # 12 attention heads
    rotary_output = rotary_pe(rotary_input)
    print(f"   Input shape: {rotary_input.shape}")
    print(f"   Output shape: {rotary_output.shape}")
    print(f"   Rotary dimension: {rotary_dim}")
    
    # Compare positional encoding patterns
    print("\n4. Positional Encoding Comparison:")
    print("   Absolute PE: Sinusoidal pattern with fixed positions")
    print("   Relative PE: Distance-based embeddings for relative positions")
    print("   Rotary PE: Rotation-based encoding for relative positions")

def run_multihead_attention_demo():
    """Demonstrate multi-head attention mechanisms."""
    print("\n" + "="*60)
    print("MULTI-HEAD ATTENTION DEMONSTRATION")
    print("="*60)
    
    # Test different configurations
    configs = [
        {
            "name": "BERT-style (Absolute PE)",
            "config": AttentionConfig(
                hidden_size=768,
                num_attention_heads=12,
                attention_dropout=0.1,
                position_embedding_type="absolute"
            )
        },
        {
            "name": "RoBERTa-style (Relative PE)",
            "config": AttentionConfig(
                hidden_size=768,
                num_attention_heads=12,
                attention_dropout=0.1,
                position_embedding_type="relative",
                relative_attention_max_distance=128
            )
        },
        {
            "name": "GPT-style (Rotary PE)",
            "config": AttentionConfig(
                hidden_size=768,
                num_attention_heads=12,
                attention_dropout=0.1,
                position_embedding_type="rotary",
                rotary_dim=64
            )
        }
    ]
    
    # Test parameters
    batch_size = 2
    seq_len = 128
    
    for i, config_info in enumerate(configs):
        print(f"\n{i+1}. {config_info['name']}:")
        
        try:
            # Create attention mechanism
            attention = MultiHeadAttention(config_info['config'])
            
            # Create sample input
            hidden_states = torch.randn(batch_size, seq_len, config_info['config'].hidden_size)
            attention_mask = torch.ones(batch_size, seq_len)
            position_ids = torch.arange(seq_len).unsqueeze(0).expand(batch_size, -1)
            
            print(f"   Hidden states shape: {hidden_states.shape}")
            print(f"   Attention mask shape: {attention_mask.shape}")
            print(f"   Position IDs shape: {position_ids.shape}")
            
            # Forward pass
            with torch.no_grad():
                outputs = attention(
                    hidden_states,
                    attention_mask=attention_mask,
                    position_ids=position_ids,
                    output_attentions=True
                )
            
            print(f"   Output shape: {outputs[0].shape}")
            if len(outputs) > 1:
                print(f"   Attention weights shape: {outputs[1].shape}")
                print(f"   Attention weights sum: {outputs[1].sum(dim=-1).mean():.4f}")
            
        except Exception as e:
            print(f"   Error: {str(e)}")

def run_scaled_dot_product_attention_demo():
    """Demonstrate scaled dot-product attention."""
    print("\n" + "="*60)
    print("SCALED DOT-PRODUCT ATTENTION DEMONSTRATION")
    print("="*60)
    
    # Test parameters
    d_model = 768
    num_heads = 12
    batch_size = 2
    seq_len = 128
    
    print(f"Testing with d_model={d_model}, num_heads={num_heads}")
    print(f"Batch size={batch_size}, sequence length={seq_len}")
    
    # Create attention mechanism
    attention = ScaledDotProductAttention(d_model, num_heads, dropout=0.1)
    
    # Create sample inputs
    query = torch.randn(batch_size, seq_len, d_model)
    key = torch.randn(batch_size, seq_len, d_model)
    value = torch.randn(batch_size, seq_len, d_model)
    
    print(f"\nInput shapes:")
    print(f"  Query: {query.shape}")
    print(f"  Key: {key.shape}")
    print(f"  Value: {value.shape}")
    
    # Forward pass without mask
    with torch.no_grad():
        output, attention_weights = attention(query, key, value)
    
    print(f"\nOutput shapes:")
    print(f"  Output: {output.shape}")
    print(f"  Attention weights: {attention_weights.shape}")
    
    # Test with mask
    print(f"\nTesting with attention mask:")
    mask = torch.ones(batch_size, seq_len, seq_len)
    mask[:, :, seq_len//2:] = 0  # Mask second half of sequence
    
    with torch.no_grad():
        masked_output, masked_attention_weights = attention(query, key, value, mask)
    
    print(f"  Masked output shape: {masked_output.shape}")
    print(f"  Masked attention weights shape: {masked_attention_weights.shape}")
    
    # Compare attention weights
    print(f"\nAttention weight statistics:")
    print(f"  Without mask - Mean: {attention_weights.mean():.4f}, Std: {attention_weights.std():.4f}")
    print(f"  With mask - Mean: {masked_attention_weights.mean():.4f}, Std: {masked_attention_weights.std():.4f}")

def run_self_attention_demo():
    """Demonstrate self-attention mechanism."""
    print("\n" + "="*60)
    print("SELF-ATTENTION DEMONSTRATION")
    print("="*60)
    
    # Test parameters
    d_model = 768
    num_heads = 12
    batch_size = 2
    seq_len = 128
    
    print(f"Testing with d_model={d_model}, num_heads={num_heads}")
    
    # Create self-attention mechanism
    self_attention = SelfAttention(d_model, num_heads, dropout=0.1)
    
    # Create sample input
    x = torch.randn(batch_size, seq_len, d_model)
    print(f"Input shape: {x.shape}")
    
    # Forward pass without mask
    with torch.no_grad():
        output, attention_weights = self_attention(x)
    
    print(f"Output shape: {output.shape}")
    print(f"Attention weights shape: {attention_weights.shape}")
    
    # Test with causal mask (for autoregressive models)
    print(f"\nTesting with causal mask:")
    causal_mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
    causal_mask = causal_mask.unsqueeze(0).unsqueeze(0)  # Add batch and head dimensions
    
    with torch.no_grad():
        causal_output, causal_attention_weights = self_attention(x, mask=causal_mask)
    
    print(f"Causal output shape: {causal_output.shape}")
    print(f"Causal attention weights shape: {causal_attention_weights.shape}")
    
    # Verify causal masking
    print(f"\nCausal masking verification:")
    print(f"  Upper triangular elements should be zero: {causal_attention_weights[0, 0, 0, 1:].sum():.6f}")

def run_cross_attention_demo():
    """Demonstrate cross-attention mechanism."""
    print("\n" + "="*60)
    print("CROSS-ATTENTION DEMONSTRATION")
    print("="*60)
    
    # Test parameters
    d_model = 768
    num_heads = 12
    batch_size = 2
    encoder_seq_len = 128
    decoder_seq_len = 64
    
    print(f"Testing with d_model={d_model}, num_heads={num_heads}")
    print(f"Encoder sequence length: {encoder_seq_len}")
    print(f"Decoder sequence length: {decoder_seq_len}")
    
    # Create cross-attention mechanism
    cross_attention = CrossAttention(d_model, num_heads, dropout=0.1)
    
    # Create sample inputs (encoder-decoder scenario)
    query = torch.randn(batch_size, decoder_seq_len, d_model)  # Decoder hidden states
    key = torch.randn(batch_size, encoder_seq_len, d_model)    # Encoder hidden states
    value = torch.randn(batch_size, encoder_seq_len, d_model)  # Encoder hidden states
    
    print(f"\nInput shapes:")
    print(f"  Query (decoder): {query.shape}")
    print(f"  Key (encoder): {key.shape}")
    print(f"  Value (encoder): {value.shape}")
    
    # Forward pass
    with torch.no_grad():
        output, attention_weights = cross_attention(query, key, value)
    
    print(f"\nOutput shapes:")
    print(f"  Output: {output.shape}")
    print(f"  Attention weights: {attention_weights.shape}")
    
    # Test with encoder padding mask
    print(f"\nTesting with encoder padding mask:")
    encoder_padding_mask = torch.ones(batch_size, encoder_seq_len)
    encoder_padding_mask[:, encoder_seq_len//2:] = 0  # Mask second half as padding
    
    # Create attention mask from padding mask
    attention_mask = encoder_padding_mask.unsqueeze(1).unsqueeze(2)  # Add head and query dimensions
    attention_mask = attention_mask.expand(-1, num_heads, decoder_seq_len, -1)
    
    with torch.no_grad():
        masked_output, masked_attention_weights = cross_attention(query, key, value, mask=attention_mask)
    
    print(f"Masked output shape: {masked_output.shape}")
    print(f"Masked attention weights shape: {masked_attention_weights.shape}")
    
    # Verify padding masking
    print(f"\nPadding masking verification:")
    print(f"  Attention to padded positions should be zero: {masked_attention_weights[0, 0, 0, encoder_seq_len//2:].sum():.6f}")

def run_attention_block_demo():
    """Demonstrate complete attention block."""
    print("\n" + "="*60)
    print("ATTENTION BLOCK DEMONSTRATION")
    print("="*60)
    
    # Test different configurations
    configs = [
        {
            "name": "Standard Transformer Block",
            "config": AttentionConfig(
                hidden_size=768,
                num_attention_heads=12,
                attention_dropout=0.1,
                position_embedding_type="absolute"
            )
        },
        {
            "name": "Large Model Block",
            "config": AttentionConfig(
                hidden_size=1024,
                num_attention_heads=16,
                attention_dropout=0.1,
                position_embedding_type="rotary",
                rotary_dim=64
            )
        }
    ]
    
    # Test parameters
    batch_size = 2
    seq_len = 128
    
    for i, config_info in enumerate(configs):
        print(f"\n{i+1}. {config_info['name']}:")
        
        try:
            # Create attention block
            attention_block = AttentionBlock(config_info['config'])
            
            # Create sample input
            hidden_states = torch.randn(batch_size, seq_len, config_info['config'].hidden_size)
            attention_mask = torch.ones(batch_size, seq_len)
            position_ids = torch.arange(seq_len).unsqueeze(0).expand(batch_size, -1)
            
            print(f"   Hidden states shape: {hidden_states.shape}")
            print(f"   Hidden size: {config_info['config'].hidden_size}")
            print(f"   Number of heads: {config_info['config'].num_attention_heads}")
            print(f"   Position embedding type: {config_info['config'].position_embedding_type}")
            
            # Forward pass
            with torch.no_grad():
                outputs = attention_block(
                    hidden_states,
                    attention_mask=attention_mask,
                    position_ids=position_ids,
                    output_attentions=True
                )
            
            print(f"   Output shape: {outputs[0].shape}")
            if len(outputs) > 1:
                print(f"   Attention weights shape: {outputs[1].shape}")
            
            # Test gradient flow
            hidden_states.requires_grad_(True)
            outputs = attention_block(
                hidden_states,
                attention_mask=attention_mask,
                position_ids=position_ids
            )
            loss = outputs[0].sum()
            loss.backward()
            
            print(f"   Gradient flow test: {hidden_states.grad is not None}")
            print(f"   Gradient norm: {hidden_states.grad.norm():.4f}")
            
        except Exception as e:
            print(f"   Error: {str(e)}")

def run_performance_benchmark():
    """Run performance benchmarks for attention mechanisms."""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    
    # Test configurations
    configs = [
        {"hidden_size": 768, "num_heads": 12, "seq_len": 128},
        {"hidden_size": 1024, "num_heads": 16, "seq_len": 256},
        {"hidden_size": 1536, "num_heads": 24, "seq_len": 512},
    ]
    
    batch_size = 4
    num_runs = 10
    
    print(f"Benchmarking with batch_size={batch_size}, num_runs={num_runs}")
    
    for config in configs:
        print(f"\nConfiguration: hidden_size={config['hidden_size']}, "
              f"num_heads={config['num_heads']}, seq_len={config['seq_len']}")
        
        # Create attention mechanism
        attention_config = AttentionConfig(
            hidden_size=config['hidden_size'],
            num_attention_heads=config['num_heads'],
            attention_dropout=0.1,
            position_embedding_type="absolute"
        )
        attention = MultiHeadAttention(attention_config)
        
        # Create sample input
        hidden_states = torch.randn(batch_size, config['seq_len'], config['hidden_size'])
        attention_mask = torch.ones(batch_size, config['seq_len'])
        position_ids = torch.arange(config['seq_len']).unsqueeze(0).expand(batch_size, -1)
        
        # Warmup
        for _ in range(3):
            with torch.no_grad():
                _ = attention(hidden_states, attention_mask=attention_mask, position_ids=position_ids)
        
        # Benchmark
        start_time = time.time()
        for _ in range(num_runs):
            with torch.no_grad():
                _ = attention(hidden_states, attention_mask=attention_mask, position_ids=position_ids)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / num_runs
        print(f"  Average forward pass time: {avg_time*1000:.2f} ms")
        
        # Memory usage
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        if torch.cuda.is_available():
            memory_before = torch.cuda.memory_allocated()
            with torch.no_grad():
                _ = attention(hidden_states, attention_mask=attention_mask, position_ids=position_ids)
            memory_after = torch.cuda.memory_allocated()
            memory_used = (memory_after - memory_before) / 1024**2  # MB
            print(f"  GPU memory usage: {memory_used:.2f} MB")

def main():
    """Main demonstration function."""
    print("Attention Mechanisms and Positional Encodings Implementation Demo")
    print("="*60)
    
    try:
        # Run all demonstrations
        run_positional_encoding_demo()
        run_multihead_attention_demo()
        run_scaled_dot_product_attention_demo()
        run_self_attention_demo()
        run_cross_attention_demo()
        run_attention_block_demo()
        run_performance_benchmark()
        
        # Run the comprehensive demonstration
        print("\n" + "="*60)
        print("COMPREHENSIVE DEMONSTRATION")
        print("="*60)
        demonstrate_attention_mechanisms()
        
    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("="*60)
    return 0

if __name__ == "__main__":
    # Set seed for reproducibility
    torch.manual_seed(42)
    
    exit_code = main()
    sys.exit(exit_code) 