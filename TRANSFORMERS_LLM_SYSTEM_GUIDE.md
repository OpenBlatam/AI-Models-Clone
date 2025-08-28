# Transformers and LLMs System - Complete Guide

## 🎯 Overview

This guide provides comprehensive documentation for the Transformers and LLMs System, which includes state-of-the-art transformer architectures, advanced attention mechanisms, LLM components, and training utilities for PyTorch models.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Attention Mechanisms](#attention-mechanisms)
3. [Transformer Architectures](#transformer-architectures)
4. [Positional Encodings](#positional-encodings)
5. [Training and Fine-tuning](#training-and-fine-tuning)
6. [Text Generation](#text-generation)
7. [Advanced Features](#advanced-features)
8. [Performance Optimization](#performance-optimization)
9. [Examples and Use Cases](#examples-and-use-cases)

## 🏗️ System Overview

### Core Components

| Component | Description | Key Features |
|-----------|-------------|--------------|
| **Attention Mechanisms** | Advanced attention implementations | 6+ attention types |
| **Transformer Architectures** | Complete transformer models | 4+ model sizes |
| **Positional Encodings** | Multiple encoding methods | 3+ encoding types |
| **Training Manager** | LLM training orchestration | Optimization, checkpointing |
| **Text Generation** | Advanced generation strategies | Multiple sampling methods |
| **Advanced Features** | State-of-the-art techniques | RoPE, ALiBi, gradient checkpointing |

### Key Benefits

- ✅ **State-of-the-Art**: Latest transformer and LLM techniques
- ✅ **Highly Configurable**: Flexible architecture options
- ✅ **Performance Optimized**: Efficient implementations
- ✅ **Production Ready**: Robust training and inference
- ✅ **Research Friendly**: Easy to extend and experiment

## 🔍 Attention Mechanisms

### Available Attention Types

#### 1. Multi-Head Attention
```python
from transformers_llm_system import AttentionType, TransformerConfig

config = TransformerConfig(
    attention_type=AttentionType.MULTI_HEAD,
    num_attention_heads=12,
    hidden_size=768
)
```

**Features:**
- Standard multi-head attention mechanism
- Configurable number of attention heads
- Support for attention masks and dropout

#### 2. Flash Attention
```python
config = TransformerConfig(
    attention_type=AttentionType.FLASH_ATTENTION,
    use_flash_attention=True,
    num_attention_heads=12
)
```

**Features:**
- Memory-efficient attention computation
- Faster training and inference
- Reduced memory usage for long sequences

#### 3. Linear Attention
```python
config = TransformerConfig(
    attention_type=AttentionType.LINEAR_ATTENTION,
    num_attention_heads=12
)
```

**Features:**
- Linear complexity with sequence length
- Efficient for long sequences
- Maintains attention quality

#### 4. Sparse Attention
```python
config = TransformerConfig(
    attention_type=AttentionType.SPARSE_ATTENTION,
    num_attention_heads=12
)
```

**Features:**
- Computationally efficient attention patterns
- Configurable sparsity patterns
- Good for long sequences

#### 5. Local Attention
```python
config = TransformerConfig(
    attention_type=AttentionType.LOCAL_ATTENTION,
    num_attention_heads=12
)
```

**Features:**
- Local attention windows
- Efficient for long sequences
- Maintains local context

#### 6. Grouped Query Attention
```python
config = TransformerConfig(
    attention_type=AttentionType.GROUPED_QUERY_ATTENTION,
    num_attention_heads=12
)
```

**Features:**
- Shared key-value heads
- Memory efficient
- Good for large models

### Usage Examples

```python
from transformers_llm_system import MultiHeadAttention, TransformerConfig

# Create attention layer
config = TransformerConfig(
    hidden_size=768,
    num_attention_heads=12,
    attention_type=AttentionType.MULTI_HEAD
)

attention = MultiHeadAttention(config)

# Apply attention
hidden_states = torch.randn(2, 64, 768)  # batch_size, seq_len, hidden_size
attention_mask = torch.ones(2, 64)  # Optional attention mask

outputs = attention(
    hidden_states=hidden_states,
    attention_mask=attention_mask
)
```

## 🏗️ Transformer Architectures

### Model Configurations

#### 1. Tiny Model
```python
from transformers_llm_system import create_transformer_config

config = create_transformer_config(
    model_size="tiny",
    vocab_size=1000,
    max_position_embeddings=512
)
# 384 hidden, 6 layers, 6 heads, 1.5M parameters
```

#### 2. Small Model
```python
config = create_transformer_config(
    model_size="small",
    vocab_size=1000,
    max_position_embeddings=1024
)
# 512 hidden, 8 layers, 8 heads, 4M parameters
```

#### 3. Base Model
```python
config = create_transformer_config(
    model_size="base",
    vocab_size=50257,
    max_position_embeddings=2048
)
# 768 hidden, 12 layers, 12 heads, 125M parameters
```

#### 4. Large Model
```python
config = create_transformer_config(
    model_size="large",
    vocab_size=50257,
    max_position_embeddings=2048
)
# 1024 hidden, 24 layers, 16 heads, 355M parameters
```

#### 5. XL Model
```python
config = create_transformer_config(
    model_size="xl",
    vocab_size=50257,
    max_position_embeddings=2048
)
# 1600 hidden, 48 layers, 25 heads, 1.3B parameters
```

### Complete Model Architecture

```python
from transformers_llm_system import TransformerForCausalLM, TransformerConfig

# Create configuration
config = TransformerConfig(
    vocab_size=50257,
    hidden_size=768,
    num_layers=12,
    num_attention_heads=12,
    intermediate_size=3072,
    max_position_embeddings=2048,
    attention_type=AttentionType.MULTI_HEAD,
    use_rope=True,
    activation_function="gelu"
)

# Create model
model = TransformerForCausalLM(config)

print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
```

## 📍 Positional Encodings

### Available Encoding Types

#### 1. Sinusoidal Encoding
```python
from transformers_llm_system import PositionalEncoding

pos_encoding = PositionalEncoding(
    d_model=768,
    max_len=2048,
    encoding_type="sinusoidal",
    dropout=0.1
)
```

**Features:**
- Fixed sinusoidal patterns
- No learnable parameters
- Good generalization to longer sequences

#### 2. Learned Encoding
```python
pos_encoding = PositionalEncoding(
    d_model=768,
    max_len=2048,
    encoding_type="learned",
    dropout=0.1
)
```

**Features:**
- Learnable position embeddings
- Task-specific position patterns
- Limited to training sequence length

#### 3. RoPE (Rotary Position Embedding)
```python
from transformers_llm_system import RotaryPositionEmbedding

rope = RotaryPositionEmbedding(
    dim=768,
    max_position_embeddings=2048
)
```

**Features:**
- Relative position encoding
- Applied during attention computation
- Excellent for long sequences

### Usage Examples

```python
# Apply positional encoding
x = torch.randn(2, 64, 768)  # batch_size, seq_len, hidden_size

# Sinusoidal encoding
pos_encoding = PositionalEncoding(768, encoding_type="sinusoidal")
output = pos_encoding(x)

# RoPE encoding (applied in attention)
rope = RotaryPositionEmbedding(768)
rope_emb = rope(x, seq_len=64)
```

## 🎓 Training and Fine-tuning

### LLM Training Manager

```python
from transformers_llm_system import LLMTrainingManager, TransformerForCausalLM

# Create model
config = create_transformer_config("base", vocab_size=1000)
model = TransformerForCausalLM(config)

# Create training manager
training_manager = LLMTrainingManager(
    model=model,
    learning_rate=1e-4,
    weight_decay=0.01,
    warmup_steps=1000,
    max_steps=10000,
    gradient_clip_norm=1.0,
    use_amp=True  # Mixed precision training
)
```

### Training Loop

```python
# Prepare data
input_ids = torch.randint(0, 1000, (4, 64))  # batch_size, seq_len
labels = torch.randint(0, 1000, (4, 64))

# Training step
for step in range(1000):
    step_metrics = training_manager.train_step(input_ids, labels)
    
    if step % 100 == 0:
        print(f"Step {step}: Loss = {step_metrics['loss']:.4f}")
```

### Checkpointing

```python
# Save checkpoint
training_manager.save_checkpoint("model_checkpoint.pth")

# Load checkpoint
new_training_manager = LLMTrainingManager(model)
new_training_manager.load_checkpoint("model_checkpoint.pth")
```

### Advanced Training Features

#### 1. Mixed Precision Training
```python
training_manager = LLMTrainingManager(
    model=model,
    use_amp=True,  # Enable automatic mixed precision
    learning_rate=1e-4
)
```

#### 2. Gradient Clipping
```python
training_manager = LLMTrainingManager(
    model=model,
    gradient_clip_norm=1.0,  # Clip gradients at norm 1.0
    learning_rate=1e-4
)
```

#### 3. Learning Rate Scheduling
```python
training_manager = LLMTrainingManager(
    model=model,
    warmup_steps=1000,  # Linear warmup
    max_steps=10000,    # Total training steps
    learning_rate=1e-4
)
```

## 🤖 Text Generation

### Generation Strategies

#### 1. Greedy Decoding
```python
generated = model.generate(
    input_ids=input_ids,
    max_length=100,
    do_sample=False,  # Greedy decoding
    pad_token_id=0,
    eos_token_id=1
)
```

#### 2. Temperature Sampling
```python
generated = model.generate(
    input_ids=input_ids,
    max_length=100,
    do_sample=True,
    temperature=0.8,  # Control randomness
    pad_token_id=0,
    eos_token_id=1
)
```

#### 3. Top-K Sampling
```python
generated = model.generate(
    input_ids=input_ids,
    max_length=100,
    do_sample=True,
    top_k=50,  # Sample from top 50 tokens
    temperature=1.0,
    pad_token_id=0,
    eos_token_id=1
)
```

#### 4. Top-P (Nucleus) Sampling
```python
generated = model.generate(
    input_ids=input_ids,
    max_length=100,
    do_sample=True,
    top_p=0.9,  # Sample from tokens with cumulative probability 0.9
    temperature=1.0,
    pad_token_id=0,
    eos_token_id=1
)
```

### Advanced Generation Features

#### 1. Beam Search
```python
# Note: Beam search implementation can be added
generated = model.generate(
    input_ids=input_ids,
    max_length=100,
    num_beams=5,  # Beam search with 5 beams
    pad_token_id=0,
    eos_token_id=1
)
```

#### 2. Repetition Penalty
```python
generated = model.generate(
    input_ids=input_ids,
    max_length=100,
    do_sample=True,
    repetition_penalty=1.2,  # Penalize repeated tokens
    temperature=0.8,
    pad_token_id=0,
    eos_token_id=1
)
```

## 🚀 Advanced Features

### 1. RoPE (Rotary Position Embedding)

```python
config = TransformerConfig(
    use_rope=True,  # Enable RoPE
    hidden_size=768,
    num_attention_heads=12
)

model = TransformerForCausalLM(config)
```

**Benefits:**
- Better handling of long sequences
- Relative position encoding
- Improved attention patterns

### 2. ALiBi (Attention with Linear Biases)

```python
config = TransformerConfig(
    use_alibi=True,  # Enable ALiBi
    use_rope=False,  # Disable RoPE when using ALiBi
    hidden_size=768,
    num_attention_heads=12
)

model = TransformerForCausalLM(config)
```

**Benefits:**
- Extrapolation to longer sequences
- No position embeddings needed
- Efficient computation

### 3. Gradient Checkpointing

```python
config = TransformerConfig(
    gradient_checkpointing=True,  # Enable gradient checkpointing
    hidden_size=768,
    num_layers=12
)

model = TransformerForCausalLM(config)
```

**Benefits:**
- Reduced memory usage during training
- Enables training larger models
- Minimal performance impact

### 4. Flash Attention

```python
config = TransformerConfig(
    attention_type=AttentionType.FLASH_ATTENTION,
    use_flash_attention=True,
    hidden_size=768,
    num_attention_heads=12
)

model = TransformerForCausalLM(config)
```

**Benefits:**
- Memory-efficient attention
- Faster training and inference
- Better scaling with sequence length

## ⚡ Performance Optimization

### 1. Model Compilation

```python
# PyTorch 2.0+ optimization
model = torch.compile(model, mode="max-autotune")
```

### 2. Memory Optimization

```python
# Enable gradient checkpointing for large models
config.gradient_checkpointing = True

# Use appropriate batch sizes
batch_size = 32  # Adjust based on GPU memory

# Mixed precision training
training_manager = LLMTrainingManager(
    model=model,
    use_amp=True
)
```

### 3. Attention Optimization

```python
# Use efficient attention mechanisms
config.attention_type = AttentionType.FLASH_ATTENTION
config.use_flash_attention = True

# Or use linear attention for long sequences
config.attention_type = AttentionType.LINEAR_ATTENTION
```

### 4. Training Optimization

```python
# Optimize training configuration
training_manager = LLMTrainingManager(
    model=model,
    learning_rate=1e-4,
    weight_decay=0.01,
    warmup_steps=1000,
    max_steps=10000,
    gradient_clip_norm=1.0,
    use_amp=True
)
```

## 📝 Examples and Use Cases

### 1. Language Modeling

```python
from transformers_llm_system import (
    TransformerForCausalLM, create_transformer_config, LLMTrainingManager
)

# Create language model
config = create_transformer_config("base", vocab_size=50257)
model = TransformerForCausalLM(config)

# Training
training_manager = LLMTrainingManager(
    model=model,
    learning_rate=1e-4,
    warmup_steps=1000,
    max_steps=10000
)

# Training loop
for step in range(1000):
    input_ids = torch.randint(0, 50257, (4, 64))
    labels = torch.randint(0, 50257, (4, 64))
    
    metrics = training_manager.train_step(input_ids, labels)
    
    if step % 100 == 0:
        print(f"Step {step}: Loss = {metrics['loss']:.4f}")

# Generation
prompt = torch.randint(0, 50257, (1, 10))
generated = model.generate(
    input_ids=prompt,
    max_length=100,
    temperature=0.8,
    do_sample=True
)
```

### 2. Text Classification

```python
# Create transformer for classification
class TransformerForClassification(nn.Module):
    def __init__(self, config, num_classes):
        super().__init__()
        self.transformer = TransformerModel(config)
        self.classifier = nn.Linear(config.hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask=None):
        outputs = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs['last_hidden_state'][:, 0, :]  # Use [CLS] token
        logits = self.classifier(pooled_output)
        return logits

# Usage
config = create_transformer_config("base", vocab_size=10000)
model = TransformerForClassification(config, num_classes=5)
```

### 3. Sequence-to-Sequence

```python
# Create encoder-decoder model
class TransformerSeq2Seq(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.encoder = TransformerModel(config)
        self.decoder = TransformerModel(config)
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
    
    def forward(self, input_ids, decoder_input_ids, attention_mask=None):
        encoder_outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        decoder_outputs = self.decoder(
            input_ids=decoder_input_ids,
            encoder_hidden_states=encoder_outputs['last_hidden_state']
        )
        logits = self.lm_head(decoder_outputs['last_hidden_state'])
        return logits

# Usage
config = create_transformer_config("base", vocab_size=10000)
model = TransformerSeq2Seq(config)
```

### 4. Fine-tuning

```python
# Load pre-trained model
config = create_transformer_config("base", vocab_size=50257)
model = TransformerForCausalLM(config)

# Load pre-trained weights (if available)
# model.load_state_dict(torch.load("pretrained_model.pth"))

# Fine-tune on specific task
training_manager = LLMTrainingManager(
    model=model,
    learning_rate=5e-5,  # Lower learning rate for fine-tuning
    warmup_steps=100,
    max_steps=1000,
    gradient_clip_norm=1.0
)

# Fine-tuning loop
for step in range(1000):
    # Task-specific data
    input_ids = torch.randint(0, 50257, (4, 64))
    labels = torch.randint(0, 50257, (4, 64))
    
    metrics = training_manager.train_step(input_ids, labels)
    
    if step % 100 == 0:
        print(f"Fine-tuning step {step}: Loss = {metrics['loss']:.4f}")
```

## 🎯 Best Practices

### 1. Model Configuration

```python
# Choose appropriate model size
config = create_transformer_config(
    model_size="base",  # Start with base for most tasks
    vocab_size=50000,   # Adjust based on your vocabulary
    max_position_embeddings=2048  # Adjust based on sequence length
)

# Enable advanced features
config.use_rope = True  # Better for long sequences
config.gradient_checkpointing = True  # For memory efficiency
```

### 2. Training Configuration

```python
# Optimize training settings
training_manager = LLMTrainingManager(
    model=model,
    learning_rate=1e-4,  # Standard learning rate
    weight_decay=0.01,   # Regularization
    warmup_steps=1000,   # Linear warmup
    max_steps=10000,     # Total training steps
    gradient_clip_norm=1.0,  # Prevent gradient explosion
    use_amp=True  # Mixed precision for efficiency
)
```

### 3. Generation Configuration

```python
# Choose appropriate generation strategy
generated = model.generate(
    input_ids=input_ids,
    max_length=100,
    do_sample=True,      # Use sampling for creative tasks
    temperature=0.8,     # Control randomness
    top_p=0.9,          # Nucleus sampling
    repetition_penalty=1.1,  # Prevent repetition
    pad_token_id=0,
    eos_token_id=1
)
```

### 4. Performance Optimization

```python
# Enable optimizations
config.use_flash_attention = True  # If available
config.gradient_checkpointing = True  # For large models
config.use_rope = True  # For long sequences

# Use appropriate batch sizes
batch_size = 32  # Adjust based on GPU memory

# Enable mixed precision
training_manager = LLMTrainingManager(
    model=model,
    use_amp=True
)
```

## 🎉 Summary

This Transformers and LLMs System provides:

✅ **Advanced Attention Mechanisms**: 6+ attention types including Flash Attention
✅ **Multiple Transformer Architectures**: 4+ model sizes from tiny to XL
✅ **Flexible Positional Encodings**: 3+ encoding methods including RoPE
✅ **Complete Training Manager**: Optimized training with mixed precision
✅ **Advanced Text Generation**: Multiple sampling strategies
✅ **State-of-the-Art Features**: RoPE, ALiBi, gradient checkpointing
✅ **Performance Optimization**: Memory and speed optimizations
✅ **Production Ready**: Robust implementations with comprehensive testing

The system is designed to be **highly configurable**, **performance optimized**, and **production ready** for all your transformer and LLM development needs. 