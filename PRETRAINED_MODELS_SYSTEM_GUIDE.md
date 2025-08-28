# Pre-trained Models and Tokenizers System - Complete Guide

## 🎯 Overview

This guide provides comprehensive documentation for the Pre-trained Models and Tokenizers System, which includes advanced utilities for working with pre-trained models, tokenizers, fine-tuning, deployment, and optimization for PyTorch models.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Model Loading and Management](#model-loading-and-management)
3. [Tokenizer Utilities](#tokenizer-utilities)
4. [Fine-tuning and Adaptation](#fine-tuning-and-adaptation)
5. [Model Deployment](#model-deployment)
6. [Performance Optimization](#performance-optimization)
7. [Multi-Model Support](#multi-model-support)
8. [Examples and Use Cases](#examples-and-use-cases)

## 🏗️ System Overview

### Core Components

| Component | Description | Key Features |
|-----------|-------------|--------------|
| **Model Manager** | Pre-trained model loading and management | Multiple model types, caching, optimization |
| **Tokenizer Utilities** | Advanced tokenization and preprocessing | Batch processing, dataset creation |
| **Fine-tuning Manager** | Model adaptation and training | HuggingFace Trainer integration |
| **Model Deployment** | Production deployment utilities | Text generation, classification, NER |
| **Model Optimization** | Performance optimization tools | Quantization, profiling, compilation |
| **Multi-Model Support** | Multiple model management | Registry, switching, comparison |

### Key Benefits

- ✅ **Easy Integration**: Seamless HuggingFace transformers integration
- ✅ **Multiple Model Types**: Support for all major model architectures
- ✅ **Advanced Tokenization**: Comprehensive tokenizer utilities
- ✅ **Production Ready**: Deployment and serving capabilities
- ✅ **Performance Optimized**: Built-in optimization tools
- ✅ **Flexible Configuration**: Highly configurable components

## 🏗️ Model Loading and Management

### Available Model Types

#### 1. Causal Language Models
```python
from pretrained_models_system import ModelConfig, ModelType

config = ModelConfig(
    model_name="gpt2",
    model_type=ModelType.CAUSAL_LM,
    use_gradient_checkpointing=True
)
```

**Supported Models:**
- GPT-2, GPT-Neo, GPT-J, GPT-NeoX
- LLaMA, LLaMA-2, Code LLaMA
- Mistral, Mixtral
- Custom causal language models

#### 2. Sequence Classification Models
```python
config = ModelConfig(
    model_name="bert-base-uncased",
    model_type=ModelType.SEQUENCE_CLASSIFICATION,
    use_gradient_checkpointing=True
)
```

**Supported Models:**
- BERT, RoBERTa, DistilBERT
- ALBERT, DeBERTa
- Custom classification models

#### 3. Token Classification Models
```python
config = ModelConfig(
    model_name="bert-base-uncased",
    model_type=ModelType.TOKEN_CLASSIFICATION
)
```

**Supported Models:**
- BERT-based NER models
- Custom token classification models

#### 4. Question Answering Models
```python
config = ModelConfig(
    model_name="bert-base-uncased",
    model_type=ModelType.QUESTION_ANSWERING
)
```

**Supported Models:**
- BERT-based QA models
- Custom question answering models

#### 5. Masked Language Models
```python
config = ModelConfig(
    model_name="bert-base-uncased",
    model_type=ModelType.MASKED_LM
)
```

**Supported Models:**
- BERT, RoBERTa
- Custom masked language models

#### 6. Sequence-to-Sequence Models
```python
config = ModelConfig(
    model_name="t5-base",
    model_type=ModelType.SEQUENCE_TO_SEQUENCE
)
```

**Supported Models:**
- T5, BART, mT5
- Custom seq2seq models

### Model Configuration Options

```python
@dataclass
class ModelConfig:
    model_name: str                    # Model identifier
    model_type: ModelType             # Model type
    cache_dir: Optional[str] = None   # Cache directory
    use_auth_token: Optional[str] = None  # HuggingFace token
    trust_remote_code: bool = False   # Trust remote code
    torch_dtype: Optional[torch.dtype] = None  # Data type
    device_map: Optional[str] = None  # Device mapping
    load_in_8bit: bool = False        # 8-bit quantization
    load_in_4bit: bool = False        # 4-bit quantization
    use_flash_attention: bool = False # Flash attention
    use_gradient_checkpointing: bool = False  # Gradient checkpointing
    max_memory: Optional[Dict[str, str]] = None  # Memory limits
```

### Usage Examples

#### Basic Model Loading
```python
from pretrained_models_system import (
    PreTrainedModelManager, ModelConfig, TokenizerConfig, ModelType
)

# Create configurations
model_config = ModelConfig(
    model_name="gpt2",
    model_type=ModelType.CAUSAL_LM,
    use_gradient_checkpointing=True
)

tokenizer_config = TokenizerConfig(
    tokenizer_name="gpt2",
    padding_side="left",
    truncation_side="left"
)

# Create manager and load model
manager = PreTrainedModelManager(model_config, tokenizer_config)
model = manager.load_model()
tokenizer = manager.load_tokenizer()

print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
print(f"Vocabulary size: {tokenizer.vocab_size}")
```

#### Advanced Model Loading
```python
# Load with optimizations
model_config = ModelConfig(
    model_name="gpt2",
    model_type=ModelType.CAUSAL_LM,
    torch_dtype=torch.float16,  # Use FP16
    device_map="auto",          # Automatic device mapping
    load_in_8bit=True,          # 8-bit quantization
    use_gradient_checkpointing=True
)

manager = PreTrainedModelManager(model_config, tokenizer_config)
model = manager.load_model()
```

#### Model Saving and Loading
```python
# Save model
output_dir = "./saved_model"
manager.save_model(output_dir)

# Load from directory
new_manager = PreTrainedModelManager(model_config, tokenizer_config)
new_manager.load_from_directory(output_dir)
```

## 🔤 Tokenizer Utilities

### Advanced Tokenization Features

#### 1. Single Text Tokenization
```python
from pretrained_models_system import TokenizerUtilities

tokenizer_utils = TokenizerUtilities(tokenizer)

# Basic tokenization
encoding = tokenizer_utils.tokenize_text(
    "Hello, this is a test sentence.",
    max_length=20,
    truncation=True,
    padding=True
)

print(f"Input IDs shape: {encoding['input_ids'].shape}")
print(f"Attention mask shape: {encoding['attention_mask'].shape}")
```

#### 2. Batch Tokenization
```python
texts = [
    "First sentence in the batch.",
    "Second sentence with different length.",
    "Third sentence for testing."
]

batch_encoding = tokenizer_utils.tokenize_batch(
    texts,
    max_length=15,
    truncation=True,
    padding=True
)

print(f"Batch shape: {batch_encoding['input_ids'].shape}")
```

#### 3. Dataset Creation
```python
# Create classification dataset
texts = [
    "This is a positive example.",
    "This is a negative example.",
    "Another positive case.",
    "Yet another negative instance."
]
labels = [1, 0, 1, 0]

dataset = tokenizer_utils.create_dataset(
    texts, 
    labels, 
    max_length=20
)

print(f"Dataset size: {len(dataset)}")
print(f"Features: {dataset.features}")
```

#### 4. Language Model Dataset
```python
# Create dataset for language modeling
lm_dataset = tokenizer_utils.create_language_model_dataset(
    texts,
    max_length=20
)

print(f"LM Dataset size: {len(lm_dataset)}")
```

### Tokenizer Information

#### Vocabulary and Special Tokens
```python
# Get vocabulary size
vocab_size = tokenizer_utils.get_vocab_size()
print(f"Vocabulary size: {vocab_size:,}")

# Get special tokens
special_tokens = tokenizer_utils.get_special_tokens()
print(f"Special tokens: {special_tokens}")
```

#### Encoding and Decoding
```python
# Encode text
text = "Test encoding and decoding."
encoded = tokenizer_utils.encode_text(text)
print(f"Encoded: {encoded}")

# Decode tokens
decoded = tokenizer_utils.decode_tokens(encoded)
print(f"Decoded: {decoded}")
```

## 🎓 Fine-tuning and Adaptation

### Fine-tuning Manager

#### Basic Setup
```python
from pretrained_models_system import FineTuningManager
from transformers import TrainingArguments

# Create fine-tuning manager
fine_tuner = FineTuningManager(model, tokenizer)

# Setup training arguments
training_args = TrainingArguments(
    output_dir="./fine_tuned_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    save_steps=500,
    eval_steps=500,
    evaluation_strategy="steps",
    save_strategy="steps",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
)

fine_tuner.setup_training(training_args)
```

#### Dataset Preparation
```python
# Create training dataset
train_texts = [
    "Positive example one.",
    "Negative example one.",
    "Positive example two.",
    "Negative example two."
]
train_labels = [1, 0, 1, 0]

train_dataset = tokenizer_utils.create_dataset(
    train_texts, 
    train_labels, 
    max_length=20
)

# Create evaluation dataset
eval_texts = [
    "Test positive example.",
    "Test negative example."
]
eval_labels = [1, 0]

eval_dataset = tokenizer_utils.create_dataset(
    eval_texts, 
    eval_labels, 
    max_length=20
)
```

#### Training Process
```python
# Create trainer
trainer = fine_tuner.create_trainer(train_dataset, eval_dataset)

# Start fine-tuning
train_result = fine_tuner.fine_tune(train_dataset, eval_dataset)

print(f"Training completed. Final loss: {train_result.training_loss:.4f}")

# Evaluate model
eval_results = fine_tuner.evaluate(eval_dataset)
print(f"Evaluation results: {eval_results}")

# Save fine-tuned model
fine_tuner.save_model("./fine_tuned_model")
```

### Advanced Fine-tuning Features

#### Custom Data Collator
```python
from transformers import DataCollatorForLanguageModeling

# For language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False  # For causal language modeling
)

trainer = fine_tuner.create_trainer(
    train_dataset, 
    eval_dataset, 
    data_collator=data_collator
)
```

#### Language Model Fine-tuning
```python
# Create language model dataset
lm_texts = [
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning models can learn complex patterns."
]

lm_dataset = tokenizer_utils.create_language_model_dataset(
    lm_texts,
    max_length=50
)

# Fine-tune for language modeling
train_result = fine_tuner.fine_tune(lm_dataset)
```

## 🚀 Model Deployment

### Text Generation

#### Basic Generation
```python
from pretrained_models_system import ModelDeployment

deployment = ModelDeployment(model, tokenizer)

# Generate text
prompt = "The future of artificial intelligence"
generated = deployment.predict(
    prompt,
    max_length=50,
    temperature=0.8,
    do_sample=True
)

print(f"Generated: {generated}")
```

#### Advanced Generation Parameters
```python
# Greedy decoding
greedy_result = deployment.predict(
    prompt,
    max_length=30,
    do_sample=False
)

# Temperature sampling
temp_result = deployment.predict(
    prompt,
    max_length=30,
    temperature=0.5,
    do_sample=True
)

# Top-k sampling
topk_result = deployment.predict(
    prompt,
    max_length=30,
    temperature=1.0,
    do_sample=True,
    top_k=10
)

# Top-p (nucleus) sampling
topp_result = deployment.predict(
    prompt,
    max_length=30,
    temperature=1.0,
    do_sample=True,
    top_p=0.9
)
```

#### Batch Generation
```python
prompts = [
    "The future of AI is",
    "Machine learning can",
    "Deep learning enables"
]

batch_results = deployment.batch_predict(
    prompts,
    max_length=20,
    temperature=0.8
)

for prompt, result in zip(prompts, batch_results):
    print(f"{prompt} -> {result}")
```

### Text Classification

#### Single Text Classification
```python
# For classification models
result = deployment.classify_text(
    "This is a positive example for classification."
)

print(f"Predicted class: {result['predicted_class']}")
print(f"Confidence: {result['confidence']:.4f}")
print(f"Probabilities: {result['probabilities']}")
```

### Named Entity Recognition

#### Entity Extraction
```python
# For NER models
entities = deployment.extract_entities(
    "Apple Inc. was founded by Steve Jobs in Cupertino, California."
)

for entity in entities:
    print(f"Entity: {entity['text']} (Label: {entity['label']})")
    print(f"Position: {entity['start']}-{entity['end']}")
```

### Question Answering

#### QA Model Usage
```python
# For QA models
question = "Who founded Apple Inc.?"
context = "Apple Inc. was founded by Steve Jobs and Steve Wozniak in 1976."

answer = deployment.answer_question(question, context)

print(f"Question: {question}")
print(f"Answer: {answer['answer']}")
print(f"Confidence: {answer['confidence']:.4f}")
```

## ⚡ Performance Optimization

### Model Optimization

#### Basic Optimization
```python
from pretrained_models_system import ModelOptimization

optimizer = ModelOptimization(model)

# Optimize for inference
optimizer.optimize_for_inference()
```

#### Quantization
```python
# 8-bit quantization
optimizer.quantize_model("int8")

# 4-bit quantization (requires bitsandbytes)
optimizer.quantize_model("int4")
```

#### Performance Profiling
```python
# Profile model performance
profile_results = optimizer.profile_model(
    input_shape=(1, 20),
    num_runs=100
)

print(f"Average inference time: {profile_results['avg_inference_time']*1000:.2f} ms")
print(f"Throughput: {profile_results['throughput']:.2f} samples/sec")
print(f"Memory allocated: {profile_results['memory_allocated_mb']:.1f} MB")
print(f"Model parameters: {profile_results['num_parameters']:,}")
```

### Advanced Optimizations

#### Mixed Precision Training
```python
# Enable mixed precision in training arguments
training_args = TrainingArguments(
    output_dir="./model",
    fp16=True,  # Enable mixed precision
    dataloader_pin_memory=True,
    dataloader_num_workers=4
)
```

#### Gradient Checkpointing
```python
# Enable gradient checkpointing
model_config = ModelConfig(
    model_name="gpt2",
    model_type=ModelType.CAUSAL_LM,
    use_gradient_checkpointing=True
)
```

#### Model Compilation
```python
# PyTorch 2.0+ compilation
if hasattr(torch, 'compile'):
    model = torch.compile(model, mode="max-autotune")
```

## 🔄 Multi-Model Support

### Model Registry

#### Managing Multiple Models
```python
# Load multiple models
models = {}

# GPT-2 for text generation
gpt2_config = ModelConfig(
    model_name="gpt2",
    model_type=ModelType.CAUSAL_LM
)
gpt2_manager = PreTrainedModelManager(gpt2_config, TokenizerConfig("gpt2"))
models["gpt2"] = gpt2_manager.load_model()

# BERT for classification
bert_config = ModelConfig(
    model_name="bert-base-uncased",
    model_type=ModelType.SEQUENCE_CLASSIFICATION
)
bert_manager = PreTrainedModelManager(bert_config, TokenizerConfig("bert-base-uncased"))
models["bert"] = bert_manager.load_model()

# Use models
gpt2_model = models["gpt2"]
bert_model = models["bert"]
```

#### Model Comparison
```python
def compare_models(models_dict):
    """Compare multiple models."""
    results = {}
    
    for name, model in models_dict.items():
        num_params = sum(p.numel() for p in model.parameters())
        results[name] = {
            "parameters": num_params,
            "model_type": type(model).__name__
        }
    
    return results

comparison = compare_models(models)
for name, info in comparison.items():
    print(f"{name}: {info['parameters']:,} parameters")
```

## 📝 Examples and Use Cases

### Complete Language Model Pipeline

```python
from pretrained_models_system import (
    PreTrainedModelManager, TokenizerUtilities, FineTuningManager,
    ModelDeployment, ModelOptimization, ModelConfig, TokenizerConfig, ModelType
)

# 1. Load model and tokenizer
model_config = ModelConfig(
    model_name="gpt2",
    model_type=ModelType.CAUSAL_LM,
    use_gradient_checkpointing=True
)

tokenizer_config = TokenizerConfig(
    tokenizer_name="gpt2",
    padding_side="left",
    truncation_side="left"
)

manager = PreTrainedModelManager(model_config, tokenizer_config)
model = manager.load_model()
tokenizer = manager.load_tokenizer()

# 2. Setup tokenizer utilities
tokenizer_utils = TokenizerUtilities(tokenizer)

# 3. Prepare dataset
texts = [
    "The future of artificial intelligence is bright.",
    "Machine learning algorithms can solve complex problems.",
    "Deep learning models are transforming industries."
]

dataset = tokenizer_utils.create_language_model_dataset(texts, max_length=50)

# 4. Fine-tune model
fine_tuner = FineTuningManager(model, tokenizer)

training_args = TrainingArguments(
    output_dir="./fine_tuned_gpt2",
    num_train_epochs=1,
    per_device_train_batch_size=2,
    warmup_steps=10,
    weight_decay=0.01,
    logging_steps=5,
    save_steps=50
)

fine_tuner.setup_training(training_args)
trainer = fine_tuner.create_trainer(dataset)
train_result = fine_tuner.fine_tune(dataset)

# 5. Deploy model
deployment = ModelDeployment(model, tokenizer)

prompt = "The future of AI"
generated = deployment.predict(
    prompt,
    max_length=50,
    temperature=0.8,
    do_sample=True
)

print(f"Generated: {generated}")

# 6. Optimize for production
optimizer = ModelOptimization(model)
optimizer.optimize_for_inference()

profile_results = optimizer.profile_model((1, 20), num_runs=10)
print(f"Optimized inference time: {profile_results['avg_inference_time']*1000:.2f} ms")
```

### Text Classification Pipeline

```python
# Load classification model
model_config = ModelConfig(
    model_name="bert-base-uncased",
    model_type=ModelType.SEQUENCE_CLASSIFICATION
)

tokenizer_config = TokenizerConfig(
    tokenizer_name="bert-base-uncased"
)

manager = PreTrainedModelManager(model_config, tokenizer_config)
model = manager.load_model()
tokenizer = manager.load_tokenizer()

# Prepare classification dataset
texts = [
    "This is a positive review.",
    "This is a negative review.",
    "Great product, highly recommended!",
    "Terrible quality, would not buy again."
]
labels = [1, 0, 1, 0]

tokenizer_utils = TokenizerUtilities(tokenizer)
dataset = tokenizer_utils.create_dataset(texts, labels, max_length=64)

# Fine-tune for classification
fine_tuner = FineTuningManager(model, tokenizer)

training_args = TrainingArguments(
    output_dir="./classification_model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    warmup_steps=50,
    weight_decay=0.01,
    evaluation_strategy="steps",
    eval_steps=50
)

fine_tuner.setup_training(training_args)
trainer = fine_tuner.create_trainer(dataset, dataset)  # Use same dataset for train/eval
train_result = fine_tuner.fine_tune(dataset, dataset)

# Deploy classification model
deployment = ModelDeployment(model, tokenizer)

test_texts = [
    "Amazing product, love it!",
    "Disappointed with the quality.",
    "Good value for money."
]

for text in test_texts:
    result = deployment.classify_text(text)
    print(f"Text: {text}")
    print(f"Prediction: {result['predicted_class']} (Confidence: {result['confidence']:.4f})")
```

### Named Entity Recognition Pipeline

```python
# Load NER model
model_config = ModelConfig(
    model_name="bert-base-uncased",
    model_type=ModelType.TOKEN_CLASSIFICATION
)

tokenizer_config = TokenizerConfig(
    tokenizer_name="bert-base-uncased"
)

manager = PreTrainedModelManager(model_config, tokenizer_config)
model = manager.load_model()
tokenizer = manager.load_tokenizer()

# Deploy NER model
deployment = ModelDeployment(model, tokenizer)

texts = [
    "Apple Inc. was founded by Steve Jobs in Cupertino, California.",
    "Microsoft Corporation is headquartered in Redmond, Washington.",
    "Google LLC was established by Larry Page and Sergey Brin."
]

for text in texts:
    entities = deployment.extract_entities(text)
    print(f"Text: {text}")
    for entity in entities:
        print(f"  Entity: {entity['text']} (Label: {entity['label']})")
    print()
```

## 🎯 Best Practices

### 1. Model Selection

```python
# Choose appropriate model size
model_sizes = {
    "small": "gpt2",           # 124M parameters
    "medium": "gpt2-medium",   # 355M parameters
    "large": "gpt2-large",     # 774M parameters
    "xl": "gpt2-xl"           # 1.5B parameters
}

# Consider your use case
use_case = "text_generation"
if use_case == "text_generation":
    model_name = model_sizes["medium"]  # Good balance
elif use_case == "prototyping":
    model_name = model_sizes["small"]   # Faster iteration
elif use_case == "production":
    model_name = model_sizes["large"]   # Better quality
```

### 2. Memory Management

```python
# Use appropriate optimizations
model_config = ModelConfig(
    model_name="gpt2",
    model_type=ModelType.CAUSAL_LM,
    torch_dtype=torch.float16,          # Use FP16
    device_map="auto",                  # Automatic device mapping
    load_in_8bit=True,                  # 8-bit quantization
    use_gradient_checkpointing=True,    # Gradient checkpointing
    max_memory={"0": "8GB"}            # Memory limits
)
```

### 3. Training Configuration

```python
# Optimize training settings
training_args = TrainingArguments(
    output_dir="./model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,      # Effective batch size = 16
    warmup_steps=100,
    weight_decay=0.01,
    fp16=True,                         # Mixed precision
    dataloader_pin_memory=True,
    dataloader_num_workers=4,
    evaluation_strategy="steps",
    eval_steps=500,
    save_strategy="steps",
    save_steps=500,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss"
)
```

### 4. Production Deployment

```python
# Optimize for production
optimizer = ModelOptimization(model)

# Apply optimizations
optimizer.optimize_for_inference()
optimizer.quantize_model("int8")

# Profile performance
profile_results = optimizer.profile_model((1, 20), num_runs=100)
print(f"Production-ready inference time: {profile_results['avg_inference_time']*1000:.2f} ms")
```

## 🎉 Summary

This Pre-trained Models and Tokenizers System provides:

✅ **Easy Model Loading**: Seamless integration with HuggingFace transformers
✅ **Advanced Tokenization**: Comprehensive tokenizer utilities and preprocessing
✅ **Fine-tuning Support**: Complete fine-tuning pipeline with HuggingFace Trainer
✅ **Model Deployment**: Production-ready deployment utilities
✅ **Performance Optimization**: Built-in optimization and profiling tools
✅ **Multi-Model Support**: Manage and compare multiple models
✅ **Flexible Configuration**: Highly configurable for different use cases
✅ **Production Ready**: Robust implementations with comprehensive error handling

The system is designed to be **easy to use**, **highly configurable**, and **production ready** for all your pre-trained model development needs. 