# ML Module for Key Messages Feature

This module provides a complete, modular machine learning pipeline for the key messages feature, including models, data loading, training, and evaluation components.

## 🏗️ Architecture Overview

The ML module is organized into four main components:

```
ml/
├── models.py          # Model architectures and factory
├── data_loader.py     # Data loading and preprocessing
├── training.py        # Training pipeline with advanced features
├── evaluation.py      # Model evaluation and metrics
├── __init__.py        # Module exports and convenience functions
└── tests/             # Comprehensive test suite
    ├── test_models.py
    ├── test_data_loader.py
    ├── test_training.py
    └── test_evaluation.py
```

## 🚀 Quick Start

### 1. Basic Setup

```python
from ml import setup_ml_pipeline

# Quick setup with default configuration
model, data_manager, training_manager, evaluator = setup_ml_pipeline(
    model_type="gpt2",
    data_path="path/to/your/data.csv"
)
```

### 2. Training a Model

```python
# Prepare training
trainer, data_info = training_manager.prepare_training("path/to/data.csv")

# Train model with advanced features
results = trainer.train()
print(f"Training completed. Best validation loss: {results['best_val_loss']}")
```

### 3. Evaluating a Model

```python
# Load test data
test_data = data_manager.load_data("path/to/test_data.csv")
test_dataset = data_manager.create_dataset(test_data)
test_loader = DataLoader(test_dataset, batch_size=32)

# Comprehensive evaluation
evaluation_results = evaluator.run_comprehensive_evaluation(
    test_loader, 
    task_type="generation"
)
```

## 📊 Models

### Available Model Types

1. **GPT2MessageModel**: GPT-2 based text generation
2. **BERTClassifierModel**: BERT-based classification and analysis
3. **CustomTransformerModel**: Custom transformer architecture
4. **ModelEnsemble**: Ensemble of multiple models

### Model Configuration

```python
from ml import ModelConfig, ModelFactory

# Configure model
config = ModelConfig(
    model_name="gpt2",
    max_length=512,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
    device="cuda"
)

# Create model
model = ModelFactory.create_model("gpt2", config)
```

### Using Models

```python
# Text generation
generated_text = model.generate("Your prompt here")
print(f"Generated: {generated_text}")

# Text classification (BERT models)
if hasattr(model, 'classify'):
    classification = model.classify("Text to classify")
    print(f"Classification: {classification}")

# Model ensemble
from ml import ModelEnsemble

ensemble = ModelEnsemble([model1, model2], weights=[0.6, 0.4])
result = ensemble.generate_ensemble("Your prompt")
```

## 📁 Data Loading

### Data Preprocessing Pipeline

```python
from ml import DataManager, DataPreprocessor

# Initialize data manager
data_manager = DataManager({
    'max_length': 512,
    'cache_dir': './cache'
})

# Load and preprocess data
data = data_manager.load_data("path/to/data.csv")

# Create dataset
dataset = data_manager.create_dataset(data, tokenizer=your_tokenizer)

# Get data loaders
train_loader, val_loader, test_loader = data_manager.get_data_loaders(
    dataset, 
    batch_size=32
)
```

### Data Format

The system expects data in the following format:

```csv
original_message,message_type,tone,target_audience,industry,keywords,generated_response,engagement_metrics,quality_score
"Hello world","informational","professional","general","tech","['hello', 'world']","Response 1","{'clicks': 10, 'conversions': 2}",0.8
```

### Text Cleaning

```python
from ml import TextCleaner

cleaner = TextCleaner()

# Clean text
cleaned_text = cleaner.clean_text("Hello @user! Check https://example.com")
# Result: "hello [MENTION]! check [URL]"

# Normalize whitespace
normalized = cleaner.normalize_whitespace("Hello    world!   \n\nTest")
# Result: "Hello world! Test"
```

### Feature Extraction

```python
from ml import FeatureExtractor

extractor = FeatureExtractor()

# Extract text features
features = extractor.extract_text_features("Hello world! This is a test.")
# Returns: length, word_count, sentence_count, avg_word_length, etc.
```

## 🎯 Training

### Training Configuration

```python
from ml import TrainingConfig, TrainingManager

# Configure training
config = TrainingConfig(
    model_type="gpt2",
    batch_size=16,
    learning_rate=1e-4,
    num_epochs=5,
    gradient_accumulation_steps=4,
    use_mixed_precision=True,
    use_tensorboard=True,
    experiment_name="my_experiment"
)

# Initialize training manager
training_manager = TrainingManager(config)
```

### Advanced Training Features

#### Mixed Precision Training
```python
config = TrainingConfig(
    use_mixed_precision=True,
    fp16=True
)
```

#### Gradient Accumulation
```python
config = TrainingConfig(
    gradient_accumulation_steps=4  # Effective batch size = batch_size * 4
)
```

#### Learning Rate Scheduling
```python
config = TrainingConfig(
    scheduler_type="cosine"  # Options: "cosine", "linear", "step"
)
```

#### Experiment Tracking
```python
config = TrainingConfig(
    use_tensorboard=True,
    use_wandb=True,  # Requires Weights & Biases setup
    experiment_name="key_messages_experiment"
)
```

### Training Pipeline

```python
# Complete training pipeline
results = training_manager.train_model("path/to/data.csv")

print(f"Training completed!")
print(f"Best validation loss: {results['training_summary']['best_val_loss']}")
print(f"Model saved to: {results['model_path']}")
```

### Checkpointing

```python
# Save checkpoint
trainer._save_checkpoint("best_model.pt", epoch=5)

# Load checkpoint
trainer.load_checkpoint("path/to/checkpoint.pt")
```

## 📈 Evaluation

### Model Evaluation

```python
from ml import ModelEvaluator, EvaluationManager

# Initialize evaluator
evaluator = ModelEvaluator(model, device="cuda")

# Evaluate model
results = evaluator.evaluate_model(test_loader, task_type="generation")
```

### Task Types

#### 1. Generation Task
```python
results = evaluator.evaluate_model(test_loader, task_type="generation")

# Metrics: BLEU score, text length, coherence, diversity
metrics = results['metrics']
print(f"BLEU Score: {metrics['bleu_score']}")
print(f"Average Length: {metrics['avg_generated_length']}")
```

#### 2. Classification Task
```python
results = evaluator.evaluate_model(test_loader, task_type="classification")

# Metrics: Accuracy, Precision, Recall, F1-score
metrics = results['metrics']
print(f"Accuracy: {metrics['accuracy']}")
print(f"F1 Score: {metrics['f1_score']}")
```

#### 3. Regression Task
```python
results = evaluator.evaluate_model(test_loader, task_type="regression")

# Metrics: MSE, RMSE, MAE, R², Correlation
metrics = results['metrics']
print(f"R² Score: {metrics['r2_score']}")
print(f"RMSE: {metrics['rmse']}")
```

### Comprehensive Evaluation

```python
# Run complete evaluation with reports and visualizations
evaluation_manager = EvaluationManager(model, device="cuda")

results = evaluation_manager.run_comprehensive_evaluation(
    test_loader,
    task_type="generation",
    output_dir="evaluation_results"
)

# Generates:
# - evaluation_results/evaluation_report.md
# - evaluation_results/evaluation_results.json
# - evaluation_results/plots/
```

### Custom Metrics

```python
# Calculate BLEU score
bleu_score = evaluator._calculate_bleu_score(
    generated_texts, 
    reference_texts
)

# Calculate coherence score
coherence_score = evaluator._calculate_coherence_score(texts)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest ml/tests/

# Run specific test file
pytest ml/tests/test_models.py

# Run with coverage
pytest ml/tests/ --cov=ml --cov-report=html
```

### Test Coverage

The test suite covers:
- Model initialization and forward passes
- Data loading and preprocessing
- Training pipeline with various configurations
- Evaluation metrics and edge cases
- Error handling and edge cases

## ⚙️ Configuration

### Default Configurations

```python
from ml import (
    DEFAULT_GPT2_CONFIG,
    DEFAULT_BERT_CONFIG,
    DEFAULT_CUSTOM_CONFIG,
    DEFAULT_DATA_CONFIG,
    DEFAULT_TRAINING_CONFIG
)

# Use default configurations
model = ModelFactory.create_model("gpt2", DEFAULT_GPT2_CONFIG)
data_manager = DataManager(DEFAULT_DATA_CONFIG)
training_manager = TrainingManager(DEFAULT_TRAINING_CONFIG)
```

### Custom Configuration

```python
# Override specific settings
config = TrainingConfig(
    **vars(DEFAULT_TRAINING_CONFIG),
    batch_size=64,
    learning_rate=2e-4,
    num_epochs=10
)
```

## 🔧 Advanced Usage

### Custom Model Architecture

```python
from ml import BaseMessageModel, ModelConfig

class CustomModel(BaseMessageModel):
    def __init__(self, config):
        super().__init__(config)
        # Add your custom layers here
        self.custom_layer = nn.Linear(768, 1000)
    
    def forward(self, input_ids, attention_mask=None):
        # Implement your forward pass
        return self.custom_layer(input_ids)
    
    def generate(self, prompt, **kwargs):
        # Implement your generation logic
        return f"Custom generated: {prompt}"
    
    def load_model(self, path):
        # Implement model loading
        pass
```

### Custom Data Preprocessing

```python
class CustomPreprocessor(DataPreprocessor):
    def _extract_custom_features(self, data):
        # Add your custom feature extraction
        data['custom_feature'] = data['original_message'].apply(
            lambda x: len(x.split())
        )
        return data
```

### Custom Evaluation Metrics

```python
class CustomEvaluator(ModelEvaluator):
    def _calculate_custom_metric(self, predictions, true_values):
        # Implement your custom metric
        return np.mean(np.abs(predictions - true_values))
```

## 📊 Monitoring and Logging

### TensorBoard Integration

```python
# Training logs are automatically saved
# View with: tensorboard --logdir logs/
```

### Weights & Biases Integration

```python
# Initialize W&B
import wandb
wandb.init(project="key-messages")

# Training metrics are automatically logged
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger(__name__)
logger.info("Training started", epoch=1, batch_size=32)
```

## 🚀 Performance Optimization

### GPU Acceleration

```python
# Automatic GPU detection
config = ModelConfig(device="cuda" if torch.cuda.is_available() else "cpu")
```

### Mixed Precision Training

```python
# Reduces memory usage and speeds up training
config = TrainingConfig(use_mixed_precision=True, fp16=True)
```

### Gradient Accumulation

```python
# Simulate larger batch sizes
config = TrainingConfig(gradient_accumulation_steps=4)
```

### Data Loading Optimization

```python
# Optimize data loading
dataloader = DataLoaderFactory.create_dataloader(
    dataset,
    batch_size=32,
    num_workers=4,
    pin_memory=True
)
```

## 🔍 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```python
   # Reduce batch size or use gradient accumulation
   config = TrainingConfig(batch_size=8, gradient_accumulation_steps=8)
   ```

2. **Slow Data Loading**
   ```python
   # Increase number of workers
   dataloader = DataLoader(dataset, num_workers=8, pin_memory=True)
   ```

3. **Model Not Converging**
   ```python
   # Adjust learning rate and scheduler
   config = TrainingConfig(
       learning_rate=5e-5,
       scheduler_type="cosine",
       warmup_steps=1000
   )
   ```

### Debug Mode

```python
# Enable debug logging
import structlog
structlog.configure(processors=[structlog.dev.ConsoleRenderer()])
```

## 📚 Examples

### Complete Training Example

```python
from ml import setup_ml_pipeline, TrainingConfig

# Setup
config = TrainingConfig(
    model_type="gpt2",
    batch_size=16,
    num_epochs=5,
    use_mixed_precision=True,
    experiment_name="key_messages_v1"
)

model, data_manager, training_manager, evaluator = setup_ml_pipeline(
    model_type="gpt2",
    config=config
)

# Train
results = training_manager.train_model("data/training.csv")

# Evaluate
test_data = data_manager.load_data("data/test.csv")
test_dataset = data_manager.create_dataset(test_data)
test_loader = DataLoader(test_dataset, batch_size=32)

evaluation_results = evaluator.run_comprehensive_evaluation(
    test_loader,
    task_type="generation"
)

print(f"Training completed!")
print(f"Best validation loss: {results['training_summary']['best_val_loss']}")
print(f"Test BLEU score: {evaluation_results['metrics']['bleu_score']}")
```

### Model Ensemble Example

```python
from ml import ModelEnsemble, ModelFactory, ModelConfig

# Create multiple models
config1 = ModelConfig(model_name="gpt2")
config2 = ModelConfig(model_name="gpt2-medium")

model1 = ModelFactory.create_model("gpt2", config1)
model2 = ModelFactory.create_model("gpt2", config2)

# Create ensemble
ensemble = ModelEnsemble([model1, model2], weights=[0.6, 0.4])

# Generate with ensemble
result = ensemble.generate_ensemble("Your prompt here")
print(f"Ensemble result: {result}")
```

## 🤝 Contributing

1. Follow the modular architecture
2. Add comprehensive tests for new features
3. Update documentation
4. Use type hints and docstrings
5. Follow the existing code style

## 📄 License

This module is part of the Key Messages feature and follows the same license as the main project. 