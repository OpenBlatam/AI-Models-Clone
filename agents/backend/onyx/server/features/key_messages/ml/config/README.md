# Configuration System for Key Messages ML Pipeline

This directory contains the configuration system for the Key Messages ML Pipeline, providing YAML-based configuration management with environment-specific overrides.

## Overview

The configuration system allows you to:
- Define all hyperparameters and model settings in YAML files
- Use environment-specific overrides (development, staging, production)
- Validate configuration structure and values
- Easily access configuration from any part of the ML pipeline
- Support for different training, data, and evaluation configurations

## Directory Structure

```
config/
├── config.yaml                    # Main configuration file
├── environments/                  # Environment-specific overrides
│   ├── development.yaml          # Development environment settings
│   ├── staging.yaml              # Staging environment settings
│   └── production.yaml           # Production environment settings
├── config_manager.py             # Configuration management logic
├── __init__.py                   # Module exports and convenience functions
├── tests/                        # Configuration tests
│   └── test_config_manager.py    # Configuration manager tests
└── README.md                     # This file
```

## Quick Start

### 1. Basic Configuration Loading

```python
from ml.config import load_config, get_config

# Load configuration with default environment
config = load_config()

# Or specify environment
config = load_config(environment="production")

# Quick access
config = get_config("development")
```

### 2. Accessing Specific Configurations

```python
from ml.config import (
    get_model_config,
    get_training_config,
    get_data_config,
    get_evaluation_config
)

# Get model configuration
model_config = get_model_config("gpt2", environment="production")

# Get training configuration
training_config = get_training_config("production", environment="production")

# Get data configuration
data_config = get_data_config("high_performance", environment="production")

# Get evaluation configuration
eval_config = get_evaluation_config("comprehensive", environment="production")
```

### 3. Using ConfigManager for Advanced Usage

```python
from ml.config import ConfigManager

# Initialize config manager
config_manager = ConfigManager(
    config_dir="config",
    environment="production"
)

# Load configuration
config = config_manager.load_config()

# Get specific configurations
model_config = config_manager.get_model_config("gpt2", config)
training_config = config_manager.get_training_config("production", config)

# Resolve device and dtype
device = config_manager.resolve_device("auto")  # Returns "cuda" or "cpu"
dtype = config_manager.resolve_torch_dtype("auto")  # Returns torch.float16 or torch.float32

# Update configuration
updates = {"training": {"default": {"batch_size": 64}}}
updated_config = config_manager.update_config(updates, config)

# Save configuration
config_manager.save_config(updated_config, "updated_config.yaml")

# Get configuration summary
summary = config_manager.get_config_summary(config)
print(summary)
```

## Configuration Structure

### Main Configuration (`config.yaml`)

The main configuration file contains all settings organized into sections:

```yaml
# Application metadata
app:
  name: "key_messages_ml_pipeline"
  version: "1.0.0"
  description: "Machine learning pipeline for key messages generation and analysis"
  environment: "development"  # development, staging, production

# Model configurations
models:
  gpt2:
    model_name: "gpt2"
    max_length: 512
    temperature: 0.7
    top_p: 0.9
    do_sample: true
    device: "auto"  # auto, cuda, cpu
    torch_dtype: "auto"  # auto, float16, float32
    
  gpt2_medium:
    model_name: "gpt2-medium"
    max_length: 512
    temperature: 0.7
    top_p: 0.9
    do_sample: true
    device: "auto"
    torch_dtype: "auto"
    
  bert_classifier:
    model_name: "bert-base-uncased"
    max_length: 512
    temperature: 1.0
    do_sample: false
    device: "auto"
    torch_dtype: "auto"
    num_labels: 5
    labels: ["negative", "neutral", "positive", "very_positive", "very_negative"]

# Training configurations
training:
  default:
    model_type: "gpt2"
    batch_size: 16
    learning_rate: 1.0e-4
    num_epochs: 5
    warmup_steps: 1000
    max_grad_norm: 1.0
    weight_decay: 0.01
    scheduler_type: "cosine"  # cosine, linear, step
    gradient_accumulation_steps: 4
    use_mixed_precision: true
    fp16: true
    use_wandb: false
    use_tensorboard: true
    experiment_name: "key_messages_baseline"
    save_steps: 1000
    eval_steps: 500
    save_total_limit: 3
    device: "auto"
    
  fast:
    model_type: "gpt2"
    batch_size: 8
    learning_rate: 2.0e-4
    num_epochs: 2
    warmup_steps: 100
    gradient_accumulation_steps: 2
    use_mixed_precision: true
    use_tensorboard: false
    use_wandb: false
    experiment_name: "key_messages_fast"
    save_steps: 500
    eval_steps: 250
    
  production:
    model_type: "gpt2_medium"
    batch_size: 32
    learning_rate: 5.0e-5
    num_epochs: 10
    warmup_steps: 2000
    gradient_accumulation_steps: 8
    use_mixed_precision: true
    use_tensorboard: true
    use_wandb: true
    experiment_name: "key_messages_production"
    save_steps: 2000
    eval_steps: 1000
    save_total_limit: 5

# Data loading configurations
data:
  default:
    max_length: 512
    batch_size: 32
    num_workers: 4
    pin_memory: true
    cache_dir: "./cache"
    train_ratio: 0.7
    val_ratio: 0.15
    test_ratio: 0.15
    
  high_performance:
    max_length: 512
    batch_size: 64
    num_workers: 8
    pin_memory: true
    cache_dir: "./cache"
    prefetch_factor: 2
    persistent_workers: true
    
  memory_efficient:
    max_length: 256
    batch_size: 16
    num_workers: 2
    pin_memory: false
    cache_dir: "./cache"
    
  preprocessing:
    remove_urls: true
    remove_emails: true
    remove_phone_numbers: true
    normalize_whitespace: true
    lowercase: true
    remove_special_chars: true
    keep_punctuation: true
    min_text_length: 10
    max_text_length: 1000
    min_quality_score: 0.0
    max_quality_score: 1.0

# Evaluation configurations
evaluation:
  default:
    batch_size: 32
    num_workers: 4
    device: "auto"
    output_dir: "./evaluation_results"
    save_predictions: true
    save_metrics: true
    generate_plots: true
    generate_report: true
    
  fast:
    batch_size: 16
    num_workers: 2
    device: "auto"
    output_dir: "./evaluation_results_fast"
    save_predictions: false
    save_metrics: true
    generate_plots: false
    generate_report: true
    
  comprehensive:
    batch_size: 64
    num_workers: 8
    device: "auto"
    output_dir: "./evaluation_results_comprehensive"
    save_predictions: true
    save_metrics: true
    generate_plots: true
    generate_report: true
    additional_metrics:
      - "perplexity"
      - "diversity"
      - "coherence"
      - "fluency"

# Model ensemble configurations
ensemble:
  default:
    models:
      - name: "gpt2"
        weight: 0.6
        config: "gpt2"
      - name: "gpt2_medium"
        weight: 0.4
        config: "gpt2_medium"
    method: "weighted_average"  # weighted_average, voting, stacking
    
  large:
    models:
      - name: "gpt2"
        weight: 0.4
        config: "gpt2"
      - name: "gpt2_medium"
        weight: 0.3
        config: "gpt2_medium"
      - name: "gpt2_large"
        weight: 0.3
        config: "gpt2_large"
    method: "weighted_average"

# Experiment tracking configurations
experiment_tracking:
  tensorboard:
    enabled: true
    log_dir: "./logs"
    update_freq: 100  # steps
    flush_secs: 120
    
  wandb:
    enabled: false
    project: "key_messages"
    entity: null
    tags: []
    notes: ""
    config_exclude_keys: []
    
  mlflow:
    enabled: false
    tracking_uri: "sqlite:///mlflow.db"
    experiment_name: "key_messages"
    log_models: true

# Performance optimization configurations
performance:
  gpu:
    device: "auto"  # auto, cuda, cpu
    memory_fraction: 0.9
    allow_growth: true
    mixed_precision: true
    
  memory:
    gradient_checkpointing: false
    gradient_accumulation: true
    batch_size_auto_tune: true
    max_memory_usage: 0.8  # fraction of available memory
    
  data_loading:
    num_workers: "auto"  # auto, or specific number
    pin_memory: true
    prefetch_factor: 2
    persistent_workers: true
    drop_last: false

# Logging configurations
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "structured"  # simple, structured
  handlers:
    console:
      enabled: true
      level: "INFO"
    file:
      enabled: true
      level: "DEBUG"
      filename: "./logs/ml_pipeline.log"
      max_bytes: 10485760  # 10MB
      backup_count: 5
    tensorboard:
      enabled: true
      level: "INFO"
      
  structured:
    include_timestamp: true
    include_process_id: true
    include_thread_id: true
    custom_fields:
      component: "ml_pipeline"
      version: "1.0.0"

# Environment-specific overrides
environments:
  development:
    training:
      default:
        num_epochs: 2
        use_wandb: false
        use_tensorboard: false
    logging:
      level: "DEBUG"
    performance:
      gpu:
        memory_fraction: 0.5
        
  staging:
    training:
      default:
        num_epochs: 5
        use_wandb: true
        use_tensorboard: true
    logging:
      level: "INFO"
    performance:
      gpu:
        memory_fraction: 0.8
        
  production:
    training:
      default:
        num_epochs: 10
        use_wandb: true
        use_tensorboard: true
    logging:
      level: "WARNING"
    performance:
      gpu:
        memory_fraction: 0.9
    security:
      model:
        validate_inputs: true
        sanitize_outputs: true
```

### Environment-Specific Overrides

Environment-specific configuration files allow you to override settings for different environments:

#### Development Environment (`environments/development.yaml`)

```yaml
# Development Environment Configuration
# This file overrides the main config.yaml for development settings

# Override app settings for development
app:
  environment: "development"
  debug: true

# Development-specific model configurations
models:
  gpt2:
    max_length: 256  # Shorter for faster development
    temperature: 0.8
    device: "cpu"  # Use CPU for development
    
  gpt2_medium:
    max_length: 256
    device: "cpu"
    
  gpt2_large:
    max_length: 256
    device: "cpu"

# Development training settings
training:
  default:
    batch_size: 4  # Smaller batch size for development
    learning_rate: 2.0e-4  # Higher learning rate for faster convergence
    num_epochs: 2  # Fewer epochs for quick iteration
    warmup_steps: 50  # Shorter warmup
    gradient_accumulation_steps: 2
    use_mixed_precision: false  # Disable for development
    use_wandb: false  # Disable W&B for development
    use_tensorboard: false  # Disable TensorBoard for development
    experiment_name: "key_messages_dev"
    save_steps: 100  # Save more frequently
    eval_steps: 50
    save_total_limit: 2

# Development data settings
data:
  default:
    batch_size: 8  # Smaller batches
    num_workers: 2  # Fewer workers
    pin_memory: false  # Disable for CPU
    cache_dir: "./cache_dev"
    
  preprocessing:
    min_text_length: 5  # Shorter minimum for development
    max_text_length: 500  # Shorter maximum for development

# Development evaluation settings
evaluation:
  default:
    batch_size: 8
    num_workers: 2
    device: "cpu"
    output_dir: "./evaluation_results_dev"
    save_predictions: false  # Don't save predictions in development
    save_metrics: true
    generate_plots: false  # Disable plots for faster evaluation
    generate_report: true

# Development performance settings
performance:
  gpu:
    device: "cpu"  # Use CPU for development
    memory_fraction: 0.5
    allow_growth: false
    mixed_precision: false
    
  memory:
    gradient_checkpointing: false
    gradient_accumulation: true
    batch_size_auto_tune: false  # Disable auto-tuning for development
    max_memory_usage: 0.5
    
  data_loading:
    num_workers: 2  # Fewer workers for development
    pin_memory: false
    prefetch_factor: 1
    persistent_workers: false
    drop_last: false

# Development logging settings
logging:
  level: "DEBUG"  # More verbose logging for development
  format: "simple"  # Simpler format for development
  handlers:
    console:
      enabled: true
      level: "DEBUG"
    file:
      enabled: true
      level: "DEBUG"
      filename: "./logs/ml_pipeline_dev.log"
      max_bytes: 5242880  # 5MB for development
      backup_count: 3
    tensorboard:
      enabled: false  # Disable TensorBoard for development
      
  structured:
    include_timestamp: true
    include_process_id: true
    include_thread_id: false  # Disable for simpler logs
    custom_fields:
      component: "ml_pipeline"
      version: "1.0.0"
      environment: "development"
```

#### Production Environment (`environments/production.yaml`)

```yaml
# Production Environment Configuration
# This file overrides the main config.yaml for production settings

# Override app settings for production
app:
  environment: "production"
  debug: false

# Production-specific model configurations
models:
  gpt2:
    max_length: 512
    temperature: 0.7
    device: "cuda"  # Use GPU for production
    torch_dtype: "float16"  # Use mixed precision for production
    
  gpt2_medium:
    max_length: 512
    device: "cuda"
    torch_dtype: "float16"
    
  gpt2_large:
    max_length: 512
    device: "cuda"
    torch_dtype: "float16"

# Production training settings
training:
  default:
    batch_size: 32  # Larger batch size for production
    learning_rate: 5.0e-5  # Lower learning rate for stability
    num_epochs: 10  # More epochs for production
    warmup_steps: 2000  # Longer warmup
    gradient_accumulation_steps: 8
    use_mixed_precision: true  # Enable for production
    use_wandb: true  # Enable W&B for production
    use_tensorboard: true  # Enable TensorBoard for production
    experiment_name: "key_messages_production"
    save_steps: 2000  # Save less frequently
    eval_steps: 1000
    save_total_limit: 5

# Production data settings
data:
  default:
    batch_size: 64  # Larger batches
    num_workers: 8  # More workers
    pin_memory: true  # Enable for GPU
    cache_dir: "./cache_prod"
    
  high_performance:
    batch_size: 128
    num_workers: 16
    pin_memory: true
    prefetch_factor: 4
    persistent_workers: true

# Production evaluation settings
evaluation:
  default:
    batch_size: 64
    num_workers: 8
    device: "cuda"
    output_dir: "./evaluation_results_prod"
    save_predictions: true  # Save predictions in production
    save_metrics: true
    generate_plots: true  # Enable plots for production
    generate_report: true
    
  comprehensive:
    batch_size: 128
    num_workers: 16
    device: "cuda"
    output_dir: "./evaluation_results_prod_comprehensive"
    save_predictions: true
    save_metrics: true
    generate_plots: true
    generate_report: true
    additional_metrics:
      - "perplexity"
      - "diversity"
      - "coherence"
      - "fluency"
      - "toxicity"
      - "bias"

# Production performance settings
performance:
  gpu:
    device: "cuda"  # Use GPU for production
    memory_fraction: 0.95  # Use more GPU memory
    allow_growth: false  # Pre-allocate memory
    mixed_precision: true
    
  memory:
    gradient_checkpointing: true  # Enable for large models
    gradient_accumulation: true
    batch_size_auto_tune: true  # Enable auto-tuning for production
    max_memory_usage: 0.9  # Use more memory
    
  data_loading:
    num_workers: 8  # More workers for production
    pin_memory: true
    prefetch_factor: 4
    persistent_workers: true
    drop_last: false

# Production logging settings
logging:
  level: "WARNING"  # Less verbose logging for production
  format: "structured"  # Structured format for production
  handlers:
    console:
      enabled: true
      level: "WARNING"
    file:
      enabled: true
      level: "INFO"
      filename: "./logs/ml_pipeline_prod.log"
      max_bytes: 20971520  # 20MB for production
      backup_count: 10
    tensorboard:
      enabled: true  # Enable TensorBoard for production
      level: "INFO"
      
  structured:
    include_timestamp: true
    include_process_id: true
    include_thread_id: true
    custom_fields:
      component: "ml_pipeline"
      version: "1.0.0"
      environment: "production"

# Production security settings (strict)
security:
  model:
    validate_inputs: true  # Enable for production
    sanitize_outputs: true
    max_input_length: 1000
    max_output_length: 1000
    
  data:
    anonymize_pii: true  # Enable for production
    remove_sensitive_patterns: true
    encryption_enabled: true  # Enable encryption for production
    data_retention_days: 90  # Longer retention for production
    
  api:
    rate_limiting: true  # Enable for production
    max_requests_per_minute: 100
    authentication_required: true
    input_validation: true

# Production experiment tracking (full)
experiment_tracking:
  tensorboard:
    enabled: true  # Enable for production
    log_dir: "./logs_prod"
    update_freq: 50  # More frequent updates
    flush_secs: 30
    
  wandb:
    enabled: true  # Enable for production
    project: "key_messages_production"
    entity: "your_entity"  # Set your W&B entity
    tags: ["production", "key_messages"]
    notes: "Production training run"
    config_exclude_keys: ["security", "deployment"]
    
  mlflow:
    enabled: true  # Enable for production
    tracking_uri: "sqlite:///mlflow_prod.db"
    experiment_name: "key_messages_production"
    log_models: true

# Production ensemble settings (full)
ensemble:
  default:
    models:
      - name: "gpt2"
        weight: 0.4
        config: "gpt2"
      - name: "gpt2_medium"
        weight: 0.4
        config: "gpt2_medium"
      - name: "gpt2_large"
        weight: 0.2
        config: "gpt2_large"
    method: "weighted_average"

# Production deployment settings (full)
deployment:
  serving:
    model_format: "torchscript"  # Optimized format for production
    optimization_level: "O2"  # High optimization for production
    quantization: true  # Enable quantization for production
    dynamic_batching: true
    max_batch_size: 64
    timeout_seconds: 30
    
  container:
    base_image: "pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime"
    python_version: "3.9"
    requirements_file: "requirements_prod.txt"
    health_check_enabled: true
    resource_limits:
      cpu: "8"
      memory: "16Gi"
      gpu: "2"
      
  monitoring:
    enabled: true  # Enable monitoring for production
    metrics_interval: 30  # More frequent monitoring
    health_check_interval: 15
    alerting:
      enabled: true
      cpu_threshold: 80
      memory_threshold: 85
      gpu_threshold: 90
      notification_channels:
        - "email"
        - "slack"
        - "pagerduty"
```

## Environment Variables

The configuration system respects the following environment variables:

- `ML_ENVIRONMENT`: Set the environment (development, staging, production)
- `ML_CONFIG_DIR`: Set the configuration directory path

## Configuration Validation

The configuration system includes comprehensive validation:

### Required Sections
- `app`: Application metadata
- `models`: Model configurations
- `training`: Training configurations
- `data`: Data loading configurations
- `evaluation`: Evaluation configurations

### Required Fields
- `app.name`: Application name
- `app.version`: Application version
- `app.environment`: Environment (development, staging, production)
- Model configurations: `model_name`, `max_length`, `temperature`
- Training configurations: `model_type`, `batch_size`, `learning_rate`, `num_epochs`

### Data Type Validation
- Numeric fields must be numbers
- Boolean fields must be true/false
- Device fields must be valid devices (auto, cuda, cpu)
- Environment must be valid (development, staging, production)

## Integration with ML Pipeline

### Models Module Integration

```python
from ml.config import get_config
from ml.models import ModelFactory, ModelConfig

# Load configuration
config = get_config("production")

# Create model with configuration
model_config_dict = config["models"]["gpt2"]
model_config = ModelConfig(**model_config_dict)
model = ModelFactory.create_model("gpt2", model_config)
```

### Training Module Integration

```python
from ml.config import get_config
from ml.training import TrainingManager, TrainingConfig

# Load configuration
config = get_config("production")

# Create training manager with configuration
training_config_dict = config["training"]["production"]
training_config = TrainingConfig(**training_config_dict)
training_manager = TrainingManager(training_config)
```

### Data Loading Integration

```python
from ml.config import get_config
from ml.data_loader import DataManager, DataConfig

# Load configuration
config = get_config("production")

# Create data manager with configuration
data_config_dict = config["data"]["high_performance"]
data_config = DataConfig(**data_config_dict)
data_manager = DataManager(data_config)
```

### Evaluation Integration

```python
from ml.config import get_config
from ml.evaluation import EvaluationManager, EvaluationConfig

# Load configuration
config = get_config("production")

# Create evaluation manager with configuration
eval_config_dict = config["evaluation"]["comprehensive"]
eval_config = EvaluationConfig(**eval_config_dict)
eval_manager = EvaluationManager(eval_config)
```

## Advanced Usage

### Custom Configuration Files

You can create custom configuration files for specific experiments:

```python
from ml.config import ConfigManager

# Initialize config manager with custom directory
config_manager = ConfigManager(
    config_dir="custom_configs",
    environment="production"
)

# Load custom configuration
config = config_manager.load_config("experiment_001.yaml")
```

### Dynamic Configuration Updates

```python
from ml.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config()

# Update configuration dynamically
updates = {
    "training": {
        "default": {
            "batch_size": 64,
            "learning_rate": 2.0e-4
        }
    },
    "models": {
        "gpt2": {
            "temperature": 0.8
        }
    }
}

updated_config = config_manager.update_config(updates, config)
```

### Configuration Comparison

```python
from ml.config import ConfigManager

config_manager = ConfigManager()

# Load different configurations
dev_config = config_manager.load_config(environment="development")
prod_config = config_manager.load_config(environment="production")

# Get summaries for comparison
dev_summary = config_manager.get_config_summary(dev_config)
prod_summary = config_manager.get_config_summary(prod_config)

print("Development:", dev_summary)
print("Production:", prod_summary)
```

### Configuration Templates

You can create configuration templates for different scenarios:

```yaml
# templates/fast_training.yaml
training:
  default:
    batch_size: 8
    learning_rate: 2.0e-4
    num_epochs: 2
    use_mixed_precision: false
    use_wandb: false
    use_tensorboard: false

data:
  default:
    batch_size: 16
    num_workers: 2
    pin_memory: false

evaluation:
  default:
    batch_size: 16
    num_workers: 2
    save_predictions: false
    generate_plots: false
```

## Best Practices

### 1. Environment-Specific Settings

- Use environment-specific overrides for different deployment scenarios
- Keep development settings lightweight and fast
- Use production settings for optimal performance and security

### 2. Configuration Organization

- Group related settings together
- Use descriptive names for configuration sections
- Document any non-obvious settings with comments

### 3. Validation

- Always validate configuration before using it
- Use type hints and validation for critical parameters
- Test configuration loading in your CI/CD pipeline

### 4. Security

- Never commit sensitive information to configuration files
- Use environment variables for secrets
- Validate inputs in production environments

### 5. Performance

- Use appropriate batch sizes for your hardware
- Enable mixed precision when possible
- Configure data loading for optimal performance

## Troubleshooting

### Common Issues

1. **Configuration not found**: Check that the configuration file exists and the path is correct
2. **Validation errors**: Ensure all required fields are present and have correct data types
3. **Environment overrides not applied**: Verify that the environment-specific file exists and is properly formatted
4. **Device resolution issues**: Check that PyTorch is properly installed and CUDA is available if using GPU

### Debug Mode

Enable debug logging to see detailed configuration loading information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from ml.config import load_config
config = load_config(environment="development")
```

### Configuration Validation

Test your configuration files:

```python
from ml.config import ConfigManager, ConfigValidationError

try:
    config_manager = ConfigManager()
    config = config_manager.load_config()
    print("Configuration is valid!")
except ConfigValidationError as e:
    print(f"Configuration error: {e.message}")
    print(f"Field: {e.field}")
    print(f"Value: {e.value}")
```

## Contributing

When adding new configuration options:

1. Update the main configuration file with default values
2. Add environment-specific overrides if needed
3. Update the validation logic in `config_manager.py`
4. Add tests for the new configuration options
5. Update this documentation

## Testing

Run the configuration tests:

```bash
cd config/tests
python -m pytest test_config_manager.py -v
```

The tests cover:
- Configuration loading and validation
- Environment-specific overrides
- Configuration updates and saving
- Device and dtype resolution
- Error handling and edge cases 