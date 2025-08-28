# 🚀 Comprehensive AI System

This repository contains a comprehensive AI system that integrates advanced text processing, transformer architectures, fine-tuning techniques, and training capabilities. The system is designed to be modular, extensible, and production-ready.

## 🎯 Features

### 🔤 Text Tokenization & Sequence Handling
- **Multiple Tokenizer Types**: Word-based, Subword (BPE), and HuggingFace tokenizers
- **Sequence Processing**: Padding, truncation, masking, and special token handling
- **Vocabulary Management**: Statistics, coverage analysis, and frequency tracking
- **Batch Processing**: Efficient handling of multiple sequences

### 📊 Data Loading & Preprocessing
- **Flexible Data Loaders**: Support for text, classification, sequence-to-sequence, and masked language modeling tasks
- **Streaming Support**: Memory-efficient processing of large datasets
- **Text Preprocessing**: Lowercase, punctuation removal, number removal, stopword filtering
- **Data Augmentation**: Synonym replacement, random insertion/deletion, word swapping

### 🎯 Fine-tuning Techniques
- **LoRA (Low-Rank Adaptation)**: Efficient fine-tuning with low-rank matrix decomposition
- **P-tuning**: Learnable virtual tokens for prompt-based adaptation
- **Parameter Efficiency**: 90%+ reduction in trainable parameters
- **Performance Preservation**: Maintains model quality while reducing computational cost

### 👁️ Attention Mechanisms & Positional Encodings
- **Multi-Head Attention**: Standard and relative positional attention
- **Local Attention**: Efficient local context processing
- **Cross Attention**: Multi-modal and sequence-to-sequence attention
- **Positional Encodings**: Sinusoidal, learned, and 2D image positional encodings
- **Visualization**: Attention heatmaps and statistical analysis

### 🏋️ Advanced Training System
- **Mixed Precision Training**: FP16 training for memory efficiency
- **Gradient Accumulation**: Support for large effective batch sizes
- **Multiple Optimizers**: AdamW, Adam, SGD with various schedulers
- **Comprehensive Logging**: TensorBoard integration and metric tracking
- **Checkpoint Management**: Automatic saving and loading of training states

### 🎨 Interactive Demos
- **Gradio Interfaces**: User-friendly web interfaces for all components
- **Real-time Visualization**: Attention patterns, training metrics, and model statistics
- **Comprehensive Testing**: Interactive testing of all system capabilities

## 📁 File Structure

```
├── agents/backend/onyx/server/features/image_process/
│   ├── text_tokenization_module.py      # Text tokenization and sequence handling
│   ├── text_data_loader.py              # Data loading and preprocessing
│   ├── lora_finetuning.py               # LoRA fine-tuning implementation
│   ├── ptuning_module.py                # P-tuning implementation
│   ├── advanced_transformer_system.py   # Attention mechanisms and transformer models
│   ├── advanced_training_system.py      # Complete training pipeline
│   ├── finetuning_integration.py        # Fine-tuning integration utilities
│   ├── comprehensive_demo.py            # Comprehensive demo interface
│   └── attention_demo.py                # Attention visualization demo
├── run_comprehensive_demo.py            # Demo launcher
├── requirements.txt                     # Dependencies
└── COMPREHENSIVE_README.md              # This file
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the comprehensive demo**:
   ```bash
   python run_comprehensive_demo.py
   ```

### Basic Usage

#### Text Tokenization
```python
from text_tokenization import WordTokenizer, TokenizerConfig

# Setup tokenizer
config = TokenizerConfig(vocab_size=1000, max_length=128)
tokenizer = WordTokenizer(config)
tokenizer.train(["Hello world!", "This is a test."])

# Tokenize text
tokens = tokenizer.tokenize("Hello world!")
token_ids = tokenizer.encode("Hello world!")
decoded = tokenizer.decode(token_ids)
```

#### Data Loading
```python
from text_data_loader import DataLoaderManager, DataLoaderConfig

# Setup data loader
loader_config = DataLoaderConfig(batch_size=32, max_length=128)
manager = DataLoaderManager(tokenizer, loader_config)

# Create different types of loaders
text_loader = manager.create_text_loader(texts, "text")
classification_loader = manager.create_classification_loader(texts, labels, "classification")
mlm_loader = manager.create_mlm_loader(texts, "mlm")
```

#### Fine-tuning
```python
from lora_finetuning import LoRAFineTuner
from ptuning_module import PTuningFineTuner

# Apply LoRA
lora_tuner = LoRAFineTuner(model, target_modules=["attention"], r=16, alpha=32.0)
lora_tuner.freeze_base_model()

# Apply P-tuning
ptuning_config = {'num_virtual_tokens': 20, 'token_dim': 768}
ptuning_tuner = PTuningFineTuner(model, ptuning_config)
```

#### Training
```python
from advanced_training_system import AdvancedTrainer, TrainingConfig

# Setup training
config = TrainingConfig(
    model_type="transformer",
    vocab_size=1000,
    hidden_size=256,
    num_layers=4,
    batch_size=32,
    learning_rate=1e-4,
    num_epochs=10,
    task_type="language_modeling"
)

# Create trainer and train
trainer = AdvancedTrainer(config)
trainer.setup_tokenizer("word")
trainer.setup_model()
trainer.setup_optimizer()
trainer.setup_data_loaders(train_texts, val_texts)
trainer.train(train_texts, val_texts)
```

## 🔧 Configuration

### Training Configuration
```python
@dataclass
class TrainingConfig:
    # Model configuration
    model_type: str = "transformer"
    vocab_size: int = 50000
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    max_length: int = 512
    dropout: float = 0.1
    
    # Training configuration
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    num_epochs: int = 10
    gradient_accumulation_steps: int = 1
    
    # Optimization
    optimizer: str = "adamw"
    scheduler: str = "cosine"
    mixed_precision: bool = True
    
    # Fine-tuning
    use_lora: bool = False
    lora_r: int = 16
    lora_alpha: float = 32.0
    use_ptuning: bool = False
    num_virtual_tokens: int = 20
```

### Tokenizer Configuration
```python
@dataclass
class TokenizerConfig:
    vocab_size: int = 50000
    max_length: int = 512
    pad_token: str = "<PAD>"
    unk_token: str = "<UNK>"
    bos_token: str = "<BOS>"
    eos_token: str = "<EOS>"
    mask_token: str = "<MASK>"
    do_lower_case: bool = True
    remove_accents: bool = True
    strip_whitespace: bool = True
```

## 📊 Performance Optimization

### GPU Utilization
- Automatic device detection (CUDA, MPS, CPU)
- Mixed precision training (FP16)
- Memory management and optimization
- Gradient accumulation for large batch sizes

### Memory Management
- Automatic memory cleanup
- Efficient data loading with prefetching
- Streaming datasets for large files
- Checkpoint management

### Training Efficiency
- LoRA and P-tuning for parameter-efficient fine-tuning
- Attention optimization with local and sparse attention
- Efficient tokenization and sequence processing
- Comprehensive monitoring and logging

## 🎨 Interactive Demos

### Comprehensive Demo
The main demo (`comprehensive_demo.py`) provides interactive access to all system components:

- **Tokenization Tab**: Test different tokenizer types
- **Data Loading Tab**: Explore various dataset types
- **Preprocessing Tab**: Apply text preprocessing operations
- **Attention Visualization Tab**: Visualize attention patterns
- **Fine-tuning Tab**: Apply LoRA and P-tuning techniques
- **Training Tab**: Configure and run training experiments
- **Vocabulary Analysis Tab**: Analyze vocabulary statistics

### Launch Demo
```bash
python run_comprehensive_demo.py
```

Access the demo at: `http://localhost:7860`

## 🔍 Monitoring & Logging

### Training Metrics
- Loss tracking and visualization
- Learning rate scheduling
- Gradient norms and statistics
- Model performance metrics

### TensorBoard Integration
```python
# Enable TensorBoard logging
config.tensorboard_logging = True

# View logs
tensorboard --logdir runs/
```

### Attention Visualization
```python
from advanced_transformer_system import AttentionVisualizer

visualizer = AttentionVisualizer()
fig = visualizer.plot_attention_heatmap(attention_weights, tokens)
stats = visualizer.analyze_attention_statistics(attention_weights)
```

## 🧪 Testing & Validation

### Unit Tests
```bash
# Run tokenization tests
python -m pytest tests/test_tokenization.py

# Run data loading tests
python -m pytest tests/test_data_loading.py

# Run fine-tuning tests
python -m pytest tests/test_finetuning.py
```

### Integration Tests
```bash
# Run comprehensive integration tests
python -m pytest tests/test_integration.py
```

## 📈 Use Cases

### Text Classification
```python
# Setup classification training
config.task_type = "classification"
trainer = AdvancedTrainer(config)
trainer.setup_data_loaders(texts, labels)
trainer.train(texts, labels)
```

### Language Modeling
```python
# Setup language modeling training
config.task_type = "language_modeling"
trainer = AdvancedTrainer(config)
trainer.setup_data_loaders(texts)
trainer.train(texts)
```

### Sequence-to-Sequence
```python
# Setup sequence-to-sequence training
config.task_type = "seq2seq"
trainer = AdvancedTrainer(config)
trainer.setup_data_loaders(source_texts, target_texts)
trainer.train(source_texts, target_texts)
```

## 🔧 Advanced Features

### Custom Attention Mechanisms
```python
from advanced_transformer_system import AttentionConfig, MultiHeadAttention

# Custom attention configuration
attention_config = AttentionConfig(
    hidden_size=768,
    num_heads=12,
    dropout=0.1,
    use_relative_positions=True,
    local_attention_window=64
)

# Create custom attention layer
attention = MultiHeadAttention(attention_config)
```

### Custom Fine-tuning
```python
# Custom LoRA configuration
lora_config = {
    'r': 32,
    'alpha': 64.0,
    'dropout': 0.1,
    'target_modules': ['attention', 'mlp', 'output']
}

# Apply custom LoRA
fine_tuner = LoRAFineTuner(model, **lora_config)
```

### Custom Data Processing
```python
from text_data_loader import DataPreprocessor

# Custom preprocessing pipeline
preprocessor = DataPreprocessor(tokenizer)
processed_texts = preprocessor.preprocess_texts(
    texts,
    lowercase=True,
    remove_punctuation=True,
    remove_numbers=True,
    remove_stopwords=True
)

# Custom augmentation
augmented_texts = [
    preprocessor.augment_text(
        text,
        synonym_replacement=True,
        random_insertion=True,
        random_deletion=True
    )
    for text in texts
]
```

## 🚀 Deployment

### Production Setup
```python
# Production configuration
config = TrainingConfig(
    model_type="transformer",
    vocab_size=50000,
    hidden_size=768,
    num_layers=12,
    batch_size=64,
    learning_rate=1e-4,
    num_epochs=100,
    mixed_precision=True,
    use_lora=True,
    lora_r=16
)

# Setup production trainer
trainer = AdvancedTrainer(config)
trainer.setup_all_components()
trainer.train(large_dataset)
```

### Model Serving
```python
# Save trained model
trainer.save_checkpoint("production_model.pt")

# Load for inference
trainer.load_checkpoint("production_model.pt")
model = trainer.model
model.eval()

# Inference
with torch.no_grad():
    outputs = model(input_ids, attention_mask)
```

## 📚 API Reference

### Core Classes

#### `AdvancedTrainer`
Main training class that orchestrates all components.

**Methods**:
- `setup_tokenizer(tokenizer_type)`: Setup tokenizer
- `setup_model()`: Setup model architecture
- `setup_optimizer()`: Setup optimizer and scheduler
- `setup_data_loaders(train_texts, val_texts)`: Setup data loaders
- `train(train_texts, val_texts)`: Main training loop
- `evaluate()`: Evaluate on validation set
- `save_checkpoint(filename)`: Save training checkpoint
- `load_checkpoint(filename)`: Load training checkpoint

#### `LoRAFineTuner`
LoRA fine-tuning implementation.

**Methods**:
- `freeze_base_model()`: Freeze base model parameters
- `get_trainable_parameters()`: Get trainable parameters
- `get_parameter_stats()`: Get parameter statistics

#### `PTuningFineTuner`
P-tuning fine-tuning implementation.

**Methods**:
- `add_prompts_to_input(input_embeddings)`: Add learnable prompts
- `extract_prompt_outputs(model_outputs)`: Extract prompt outputs
- `save_prompts(save_path)`: Save prompt embeddings
- `load_prompts(load_path)`: Load prompt embeddings

#### `DataLoaderManager`
Manages multiple data loaders.

**Methods**:
- `create_text_loader(texts, name)`: Create text data loader
- `create_classification_loader(texts, labels, name)`: Create classification loader
- `create_mlm_loader(texts, name)`: Create MLM loader
- `preprocess_and_create_loader(texts, name)`: Preprocess and create loader
- `augment_and_create_loader(texts, name)`: Augment and create loader

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Hugging Face for the Transformers library
- PyTorch team for the deep learning framework
- The research community for attention mechanisms and fine-tuning techniques

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review the demo examples

---

**Happy coding! 🚀**


