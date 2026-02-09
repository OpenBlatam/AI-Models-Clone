# Tokenization and Sequence Handling Guide

## Overview

This guide covers the comprehensive implementation of **tokenization and sequence handling** for text data in the ultra-optimized deep learning system. The implementation includes advanced tokenizers, sequence processors, and data handling utilities designed for production-ready NLP applications.

## Table of Contents

1. [Core Components](#core-components)
2. [Advanced Tokenizer](#advanced-tokenizer)
3. [Subword Tokenizer](#subword-tokenizer)
4. [Sequence Processor](#sequence-processor)
5. [Text Dataset](#text-dataset)
6. [Text Data Loader](#text-data-loader)
7. [Best Practices](#best-practices)
8. [Usage Examples](#usage-examples)
9. [Integration Guidelines](#integration-guidelines)
10. [Performance Optimization](#performance-optimization)
11. [Testing and Validation](#testing-and-validation)

## Core Components

### 1. Advanced Tokenizer

A comprehensive word-level tokenizer with vocabulary management and special token handling.

**Key Features:**
- Vocabulary building from text corpus
- Special token management (PAD, UNK, CLS, SEP, MASK, BOS, EOS)
- Configurable padding and truncation strategies
- Tokenization statistics tracking
- Support for multiple output formats (list, tensor, numpy)

**Usage:**
```python
# Initialize tokenizer
tokenizer = AdvancedTokenizer(vocab_size=50000, max_length=512)

# Build vocabulary from corpus
tokenizer.build_vocabulary(texts, min_freq=2)

# Encode text
encoded = tokenizer.encode("Hello world", add_special_tokens=True, return_tensors='pt')

# Decode tokens
decoded = tokenizer.decode(encoded, skip_special_tokens=True)
```

### 2. Subword Tokenizer

Byte Pair Encoding (BPE) implementation for subword tokenization.

**Key Features:**
- BPE algorithm implementation
- Dynamic vocabulary building
- Subword unit merging
- Unknown token handling

**Usage:**
```python
# Initialize subword tokenizer
subword_tokenizer = SubwordTokenizer(vocab_size=30000, min_freq=2)

# Train on corpus
subword_tokenizer.train(texts)

# Encode text
encoded = subword_tokenizer.encode("Hello world")

# Decode tokens
decoded = subword_tokenizer.decode(encoded)
```

### 3. Sequence Processor

Advanced sequence processing for variable-length sequences and batching.

**Key Features:**
- Batch processing with consistent padding
- Sliding window creation for long sequences
- Data augmentation techniques
- Multiple padding and truncation strategies

**Usage:**
```python
# Initialize processor
processor = SequenceProcessor(max_length=512, return_tensors='pt')

# Process batch
processed = processor.process_batch(texts, tokenizer)

# Create sliding windows
windows = processor.create_sliding_windows(long_text, tokenizer, window_size=512, stride=256)

# Apply data augmentation
augmented = processor.apply_data_augmentation(text, augmentation_type='random')
```

### 4. Text Dataset

PyTorch Dataset for text data with advanced preprocessing.

**Key Features:**
- Automatic tokenization and preprocessing
- Label handling for supervised learning
- Data augmentation support
- Memory-efficient processing

**Usage:**
```python
# Create dataset
dataset = TextDataset(
    texts=texts,
    labels=labels,
    tokenizer=tokenizer,
    processor=processor,
    max_length=512,
    augmentation=True
)

# Access items
item = dataset[0]
input_ids = item['input_ids']
attention_mask = item['attention_mask']
labels = item['labels']
```

### 5. Text Data Loader

Advanced data loader with custom collation and batching.

**Key Features:**
- Custom collate function for variable-length sequences
- Efficient batching and padding
- Multi-worker support
- Memory pinning for GPU acceleration

**Usage:**
```python
# Create data loader
dataloader = TextDataLoader(
    dataset=dataset,
    batch_size=32,
    shuffle=True,
    num_workers=4,
    pin_memory=True
)

# Iterate over batches
for batch in dataloader:
    input_ids = batch['input_ids']
    attention_mask = batch['attention_mask']
    labels = batch['labels']
```

## Best Practices

### 1. Vocabulary Management

**Optimal Vocabulary Size:**
- **Small datasets (< 1M tokens):** 5,000 - 10,000 tokens
- **Medium datasets (1M - 10M tokens):** 10,000 - 30,000 tokens
- **Large datasets (> 10M tokens):** 30,000 - 50,000 tokens

**Minimum Frequency:**
```python
# For small datasets
min_freq = 2

# For large datasets
min_freq = 5

# For very large datasets
min_freq = 10
```

### 2. Sequence Length Optimization

**Optimal Sequence Lengths:**
- **Classification tasks:** 128 - 512 tokens
- **Generation tasks:** 512 - 2048 tokens
- **Long document tasks:** 2048 - 8192 tokens

**Memory Considerations:**
```python
# Calculate memory usage
memory_per_sample = sequence_length * embedding_dim * 4  # 4 bytes per float32
batch_memory = memory_per_sample * batch_size
```

### 3. Padding Strategies

**Padding Side Selection:**
```python
# For most tasks (recommended)
padding_side = 'right'

# For specific tasks requiring left padding
padding_side = 'left'
```

**Truncation Strategies:**
```python
# Keep beginning (recommended for classification)
truncation_side = 'right'

# Keep end (for generation tasks)
truncation_side = 'left'
```

### 4. Data Augmentation

**Augmentation Techniques:**
```python
# Random character substitution
augmented = processor.apply_data_augmentation(text, 'random')

# Synonym replacement (custom implementation)
augmented = apply_synonym_replacement(text)

# Back-translation (requires translation model)
augmented = apply_back_translation(text)
```

## Usage Examples

### 1. Text Classification Pipeline

```python
# Setup
tokenizer = AdvancedTokenizer(vocab_size=10000, max_length=256)
tokenizer.build_vocabulary(train_texts, min_freq=2)

processor = SequenceProcessor(max_length=256, return_tensors='pt')
train_dataset = TextDataset(train_texts, train_labels, tokenizer, processor)
train_loader = TextDataLoader(train_dataset, batch_size=32, shuffle=True)

# Training loop
for batch in train_loader:
    input_ids = batch['input_ids'].to(device)
    attention_mask = batch['attention_mask'].to(device)
    labels = batch['labels'].to(device)
    
    outputs = model(input_ids, attention_mask=attention_mask)
    loss = criterion(outputs, labels)
    # ... training steps
```

### 2. Language Model Training

```python
# Setup with sliding windows
tokenizer = AdvancedTokenizer(vocab_size=30000, max_length=1024)
tokenizer.build_vocabulary(corpus_texts, min_freq=3)

processor = SequenceProcessor(max_length=1024)
windows = processor.create_sliding_windows(long_text, tokenizer, window_size=1024, stride=512)

# Create dataset from windows
dataset = TextDataset(windows, tokenizer=tokenizer, processor=processor)
dataloader = TextDataLoader(dataset, batch_size=16, shuffle=True)

# Training loop
for batch in dataloader:
    input_ids = batch['input_ids']
    # ... language model training
```

### 3. Multi-Label Classification

```python
# Setup for multi-label
tokenizer = AdvancedTokenizer(vocab_size=15000, max_length=512)
tokenizer.build_vocabulary(texts, min_freq=2)

processor = SequenceProcessor(max_length=512)
dataset = TextDataset(texts, multi_labels, tokenizer, processor)
dataloader = TextDataLoader(dataset, batch_size=16)

# Training with BCE loss
criterion = nn.BCEWithLogitsLoss()
for batch in dataloader:
    outputs = model(batch['input_ids'])
    loss = criterion(outputs, batch['labels'].float())
```

## Integration Guidelines

### 1. Integration with Existing Models

**Transformer Models:**
```python
class TextClassificationModel(nn.Module):
    def __init__(self, vocab_size, num_classes, hidden_size=768):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.transformer = nn.TransformerEncoder(...)
        self.classifier = nn.Linear(hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask=None):
        embeddings = self.embedding(input_ids)
        if attention_mask is not None:
            # Apply attention mask
            embeddings = embeddings * attention_mask.unsqueeze(-1)
        
        encoded = self.transformer(embeddings)
        pooled = encoded.mean(dim=1)  # Mean pooling
        return self.classifier(pooled)
```

### 2. Integration with Training Pipeline

**Enhanced Trainer Integration:**
```python
class TextTrainer(UltraOptimizedTrainer):
    def __init__(self, model, tokenizer, processor, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.tokenizer = tokenizer
        self.processor = processor
    
    def prepare_batch(self, batch):
        """Custom batch preparation for text data."""
        return {
            'input_ids': batch['input_ids'].to(self.device),
            'attention_mask': batch['attention_mask'].to(self.device),
            'labels': batch['labels'].to(self.device) if 'labels' in batch else None
        }
    
    def train_epoch(self, dataloader):
        for batch in dataloader:
            prepared_batch = self.prepare_batch(batch)
            # ... training logic
```

### 3. Integration with PEFT Methods

**LoRA with Text Models:**
```python
# Setup tokenizer and dataset
tokenizer = AdvancedTokenizer(vocab_size=20000, max_length=512)
tokenizer.build_vocabulary(texts, min_freq=2)

dataset = TextDataset(texts, labels, tokenizer)
dataloader = TextDataLoader(dataset, batch_size=16)

# Apply LoRA to model
lora_config = LoRAConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"]
)

model = PEFTModelWrapper(base_model, lora_config)
trainer = PEFTTrainer(model, dataloader, lora_config)
```

## Performance Optimization

### 1. Memory Optimization

**Gradient Checkpointing:**
```python
# Enable for large models
model.gradient_checkpointing_enable()

# Or use activation checkpointing
from torch.utils.checkpoint import checkpoint
outputs = checkpoint(model, input_ids, attention_mask)
```

**Mixed Precision Training:**
```python
# Enable AMP
scaler = torch.cuda.amp.GradScaler()

with torch.cuda.amp.autocast():
    outputs = model(input_ids, attention_mask)
    loss = criterion(outputs, labels)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### 2. Data Loading Optimization

**Optimal DataLoader Settings:**
```python
dataloader = TextDataLoader(
    dataset,
    batch_size=32,
    num_workers=4,  # Adjust based on CPU cores
    pin_memory=True,  # For GPU training
    persistent_workers=True,  # Keep workers alive
    prefetch_factor=2  # Prefetch batches
)
```

**Caching Strategies:**
```python
# Cache tokenized data
class CachedTextDataset(TextDataset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}
    
    def __getitem__(self, idx):
        if idx not in self.cache:
            self.cache[idx] = super().__getitem__(idx)
        return self.cache[idx]
```

### 3. Batch Size Optimization

**Dynamic Batch Sizing:**
```python
def find_optimal_batch_size(model, dataset, max_memory_gb=8):
    """Find optimal batch size based on available memory."""
    device = next(model.parameters()).device
    max_memory = max_memory_gb * 1024**3  # Convert to bytes
    
    batch_size = 1
    while True:
        try:
            batch = dataset[:batch_size]
            # Test forward pass
            with torch.no_grad():
                _ = model(batch['input_ids'])
            batch_size *= 2
        except RuntimeError:  # Out of memory
            return batch_size // 2
```

## Testing and Validation

### 1. Tokenization Tests

```python
def test_tokenization_consistency():
    """Test that encoding and decoding are consistent."""
    tokenizer = AdvancedTokenizer()
    tokenizer.build_vocabulary(sample_texts)
    
    for text in sample_texts:
        encoded = tokenizer.encode(text)
        decoded = tokenizer.decode(encoded, skip_special_tokens=True)
        
        # Normalize for comparison
        original = text.lower().strip()
        decoded = decoded.lower().strip()
        
        assert original == decoded, f"Mismatch: {original} != {decoded}"
```

### 2. Sequence Processing Tests

```python
def test_sequence_processing():
    """Test sequence processing functionality."""
    processor = SequenceProcessor(max_length=64)
    tokenizer = AdvancedTokenizer(max_length=64)
    tokenizer.build_vocabulary(sample_texts)
    
    # Test batch processing
    processed = processor.process_batch(sample_texts, tokenizer)
    
    assert processed['input_ids'].shape[1] == 64  # Max length
    assert processed['attention_mask'].shape == processed['input_ids'].shape
    
    # Test sliding windows
    long_text = " ".join(sample_texts * 10)
    windows = processor.create_sliding_windows(long_text, tokenizer, window_size=32, stride=16)
    
    assert len(windows) > 0
    assert all(len(window) <= 32 for window in windows)
```

### 3. Dataset Tests

```python
def test_dataset_functionality():
    """Test dataset functionality."""
    dataset = TextDataset(sample_texts, sample_labels, tokenizer, processor)
    
    # Test length
    assert len(dataset) == len(sample_texts)
    
    # Test item access
    item = dataset[0]
    assert 'input_ids' in item
    assert 'attention_mask' in item
    assert 'labels' in item
    
    # Test shapes
    assert item['input_ids'].shape[0] == processor.max_length
    assert item['attention_mask'].shape[0] == processor.max_length
```

### 4. Data Loader Tests

```python
def test_dataloader_functionality():
    """Test data loader functionality."""
    dataloader = TextDataLoader(dataset, batch_size=2, shuffle=False)
    
    # Test iteration
    batch = next(iter(dataloader))
    
    assert 'input_ids' in batch
    assert 'attention_mask' in batch
    assert 'labels' in batch
    
    # Test batch shapes
    assert batch['input_ids'].shape[0] == 2  # Batch size
    assert batch['attention_mask'].shape == batch['input_ids'].shape
```

## Production Deployment

### 1. Model Serving

**FastAPI Integration:**
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TextRequest(BaseModel):
    text: str
    max_length: int = 512

@app.post("/tokenize")
async def tokenize_text(request: TextRequest):
    tokenizer = AdvancedTokenizer(max_length=request.max_length)
    tokenizer.build_vocabulary([request.text])
    
    encoded = tokenizer.encode(request.text, return_tensors='pt')
    return {"tokens": encoded.tolist()}

@app.post("/classify")
async def classify_text(request: TextRequest):
    # Load model and tokenizer
    encoded = tokenizer.encode(request.text, return_tensors='pt')
    with torch.no_grad():
        outputs = model(encoded)
        predictions = torch.softmax(outputs, dim=-1)
    
    return {"predictions": predictions.tolist()}
```

### 2. Batch Processing

**Efficient Batch Processing:**
```python
def process_large_corpus(texts, batch_size=1000):
    """Process large corpus efficiently."""
    tokenizer = AdvancedTokenizer()
    processor = SequenceProcessor()
    
    results = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        # Process batch
        processed = processor.process_batch(batch_texts, tokenizer)
        results.extend(processed['input_ids'])
    
    return results
```

### 3. Monitoring and Logging

**Tokenization Metrics:**
```python
def log_tokenization_metrics(tokenizer, texts):
    """Log tokenization statistics."""
    stats = tokenizer.get_vocabulary_info()
    
    logger.info(f"Vocabulary size: {stats['vocab_size']}")
    logger.info(f"Vocabulary coverage: {stats['stats']['vocab_coverage']:.2%}")
    logger.info(f"Unique tokens: {stats['stats']['unique_tokens']}")
    
    # Log tokenization efficiency
    total_tokens = sum(len(tokenizer.encode(text)) for text in texts)
    avg_tokens = total_tokens / len(texts)
    logger.info(f"Average tokens per text: {avg_tokens:.2f}")
```

## Conclusion

This comprehensive tokenization and sequence handling implementation provides:

1. **Flexible Tokenization:** Support for word-level and subword tokenization
2. **Efficient Processing:** Optimized sequence processing and batching
3. **Production Ready:** Robust error handling and monitoring
4. **Easy Integration:** Seamless integration with existing PyTorch pipelines
5. **Performance Optimized:** Memory-efficient and GPU-accelerated processing

The implementation follows best practices for NLP applications and provides a solid foundation for building production-ready text processing pipelines.

## Next Steps

1. **Custom Tokenizers:** Implement domain-specific tokenization strategies
2. **Advanced Augmentation:** Add more sophisticated data augmentation techniques
3. **Multi-modal Support:** Extend to handle text with other modalities (images, audio)
4. **Distributed Processing:** Add support for distributed tokenization and processing
5. **Real-time Processing:** Implement streaming tokenization for real-time applications

