# Configuration Management System

A comprehensive configuration management system for AI video generation using YAML files, environment variables, and command-line overrides.

## Features

- **YAML-based configurations** - Human-readable configuration files
- **Configuration validation** - Type checking and validation rules
- **Environment-specific configs** - Different settings for dev/staging/production
- **Configuration inheritance** - Base configs with overrides
- **Command-line interface** - Easy configuration management from CLI
- **Experiment tracking integration** - WandB and TensorBoard support
- **Template system** - Pre-built configurations for common use cases

## Quick Start

### 1. Load Default Configuration

```python
from config import quick_load_config

# Load default diffusion configuration
config = quick_load_config("diffusion_default")
print(f"Model: {config.model.model_name}")
print(f"Frame size: {config.model.frame_size}")
print(f"Training epochs: {config.training.num_epochs}")
```

### 2. Create Custom Configuration

```python
from config import create_custom_config

# Create high-resolution video configuration
config = create_custom_config(
    "diffusion_default",
    {
        "model.frame_size": [512, 512],
        "training.num_epochs": 200,
        "training.batch_size": 2,
        "system.environment": "production"
    },
    "high_res_experiment"
)
```

### 3. Use Configuration Manager

```python
from config import ConfigManager

# Create manager
manager = ConfigManager("configs")

# Create new configuration
config = manager.create_config("my_experiment", "transformer")

# Customize
config.model.frame_size = [384, 384]
config.training.num_epochs = 75

# Save
manager.save_config(config, "my_config.yaml")
```

## Configuration Structure

### Complete Configuration

A complete configuration consists of five main components:

```yaml
name: "experiment_name"
description: "Description of the experiment"
version: "1.0.0"

system:
  # System settings (environment, logging, etc.)
  
model:
  # Model architecture and parameters
  
data:
  # Data loading and preprocessing
  
training:
  # Training parameters and optimization
  
evaluation:
  # Evaluation metrics and settings
```

### System Configuration

```yaml
system:
  environment: "development"  # development, staging, production
  debug: true
  log_level: "INFO"
  base_dir: "."
  config_dir: "configs"
  output_dir: "outputs"
  logs_dir: "logs"
  num_threads: 4
  memory_limit: null
  gpu_memory_fraction: 0.9
  enable_security: true
  max_file_size: 104857600
  allowed_file_types: [".mp4", ".avi", ".mov"]
```

### Model Configuration

```yaml
model:
  model_type: "diffusion"  # diffusion, gan, transformer
  model_name: "diffusion_model"
  version: "1.0.0"
  input_channels: 3
  output_channels: 3
  latent_dim: 512
  hidden_dims: [64, 128, 256, 512]
  num_layers: 4
  dropout_rate: 0.1
  use_batch_norm: true
  activation: "relu"
  frame_size: [256, 256]
  num_frames: 16
  temporal_stride: 1
  fps: 30
  device: "cuda"
  dtype: "float16"
  use_mixed_precision: true
  use_gradient_checkpointing: false
  diffusion_steps: 1000
  noise_schedule: "linear"
  classifier_free_guidance: true
  guidance_scale: 7.5
```

### Data Configuration

```yaml
data:
  data_dir: "data/videos"
  metadata_file: null
  cache_dir: null
  frame_size: [256, 256]
  num_frames: 16
  fps: 30
  channels: 3
  batch_size: 8
  num_workers: 4
  pin_memory: true
  shuffle: true
  drop_last: true
  normalize: true
  normalize_mean: [0.485, 0.456, 0.406]
  normalize_std: [0.229, 0.224, 0.225]
  augment: true
  cache_data: false
  max_cache_size: 1000
  horizontal_flip_prob: 0.5
  vertical_flip_prob: 0.0
  rotation_prob: 0.2
  rotation_degrees: 15.0
  crop_prob: 0.3
  crop_ratio: 0.8
  brightness_jitter: 0.1
  contrast_jitter: 0.1
  saturation_jitter: 0.1
  hue_jitter: 0.05
  train_split: 0.8
  val_split: 0.1
  test_split: 0.1
  random_seed: 42
```

### Training Configuration

```yaml
training:
  num_epochs: 100
  batch_size: 8
  learning_rate: 0.0001
  weight_decay: 0.00001
  gradient_clip: 1.0
  max_grad_norm: 1.0
  optimizer: "adam"  # adam, adamw, sgd, rmsprop
  optimizer_params: {}
  scheduler: "cosine"  # step, cosine, plateau, exponential
  scheduler_params: {}
  loss_type: "mse"  # mse, l1, perceptual, adversarial, combined
  loss_weights: {}
  save_frequency: 10
  eval_frequency: 5
  log_frequency: 100
  early_stopping_patience: 20
  early_stopping_min_delta: 0.0001
  checkpoint_dir: "checkpoints"
  save_best_only: true
  max_checkpoints: 5
  resume_from_checkpoint: null
  use_wandb: false
  use_tensorboard: true
  experiment_name: "ai_video_training"
  project_name: "ai_video"
  use_amp: true
  use_gradient_accumulation: false
  gradient_accumulation_steps: 1
  use_ddp: false
  local_rank: -1
```

### Evaluation Configuration

```yaml
evaluation:
  batch_size: 8
  num_samples: null
  device: "cuda"
  compute_psnr: true
  compute_ssim: true
  compute_lpips: true
  compute_fid: false
  compute_inception_score: false
  save_results: true
  save_videos: false
  output_dir: "evaluation_results"
  save_format: "mp4"  # mp4, gif, frames
  create_plots: true
  plot_samples: 5
  plot_style: "seaborn"  # default, seaborn, ggplot
  use_ensemble: false
  ensemble_size: 3
  compute_uncertainty: false
  num_mc_samples: 10
```

## Available Configurations

### Default Configurations

- **`diffusion_default`** - Standard diffusion model configuration
- **`gan_default`** - GAN-based video generation
- **`transformer_default`** - Transformer-based video generation
- **`high_res_config`** - High-resolution video generation
- **`fast_training_config`** - Fast experimentation setup

### Configuration Types

#### Diffusion Models
- **Model Type**: `diffusion`
- **Use Case**: High-quality video generation
- **Key Parameters**: `diffusion_steps`, `noise_schedule`, `guidance_scale`
- **Best For**: Photorealistic video generation

#### GAN Models
- **Model Type**: `gan`
- **Use Case**: Fast video generation
- **Key Parameters**: `loss_type: "adversarial"`
- **Best For**: Real-time applications

#### Transformer Models
- **Model Type**: `transformer`
- **Use Case**: Long-sequence video generation
- **Key Parameters**: `num_layers`, `activation: "gelu"`
- **Best For**: Long-form video content

## Environment Variables

You can override configuration values using environment variables with the `AI_VIDEO_` prefix:

```bash
# Set environment variables
export AI_VIDEO_MODEL_FRAME_SIZE="512,512"
export AI_VIDEO_TRAINING_BATCH_SIZE="4"
export AI_VIDEO_TRAINING_NUM_EPOCHS="50"
export AI_VIDEO_SYSTEM_ENVIRONMENT="production"
export AI_VIDEO_SYSTEM_DEBUG="false"

# Load configuration with overrides
python -c "
from config import load_config_with_env
config = load_config_with_env('default_configs.yaml', 'diffusion_default')
print(f'Frame size: {config.model.frame_size}')
print(f'Batch size: {config.training.batch_size}')
"
```

## Command-Line Interface

### Basic Usage

```bash
# List available configurations
python config/config_loader.py --list

# Load configuration from template
python config/config_loader.py --template diffusion_default --output my_config.yaml

# Load with overrides
python config/config_loader.py --config my_config.yaml --batch-size 16 --num-epochs 50

# Validate configuration
python config/config_loader.py --config my_config.yaml --validate
```

### Advanced Usage

```bash
# Create high-resolution configuration
python config/config_loader.py \
  --template diffusion_default \
  --model-type diffusion \
  --frame-size "512,512" \
  --batch-size 2 \
  --num-epochs 200 \
  --output high_res_config.yaml

# Production configuration
python config/config_loader.py \
  --template diffusion_default \
  --environment production \
  --device cuda \
  --output production_config.yaml
```

## Integration with Training Scripts

### Basic Integration

```python
from config import quick_load_config
import torch

# Load configuration
config = quick_load_config("diffusion_default")

# Use in training
model = create_model(config.model)
dataloader = create_dataloader(config.data)
optimizer = create_optimizer(model, config.training)

# Training loop
for epoch in range(config.training.num_epochs):
    for batch in dataloader:
        # Training logic
        pass
```

### Advanced Integration with Experiment Tracking

```python
from config import create_experiment_config
import wandb
import torch.utils.tensorboard as tensorboard

# Create experiment configuration
config = create_experiment_config(
    "my_experiment",
    "diffusion",
    {
        "training.use_wandb": True,
        "training.use_tensorboard": True,
        "training.experiment_name": "diffusion_experiment",
        "training.project_name": "ai_video_research"
    }
)

# Initialize experiment tracking
if config.training.use_wandb:
    wandb.init(
        project=config.training.project_name,
        name=config.training.experiment_name,
        config=config.to_dict()
    )

if config.training.use_tensorboard:
    writer = tensorboard.SummaryWriter(
        log_dir=f'runs/{config.training.experiment_name}'
    )

# Training with logging
for epoch in range(config.training.num_epochs):
    for batch_idx, batch in enumerate(dataloader):
        loss = train_step(model, batch, optimizer)
        
        if batch_idx % config.training.log_frequency == 0:
            if config.training.use_wandb:
                wandb.log({"loss": loss, "epoch": epoch})
            if config.training.use_tensorboard:
                writer.add_scalar("Loss/train", loss, epoch * len(dataloader) + batch_idx)
```

## Validation and Error Handling

### Configuration Validation

```python
from config import validate_and_save_config

# Validate before saving
success = validate_and_save_config(config, "my_config.yaml")
if not success:
    print("Configuration validation failed")

# Manual validation
errors = config.get_validation_errors()
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Common Validation Rules

- **Frame sizes** must be positive integers
- **Batch sizes** must be positive
- **Learning rates** must be positive
- **Split ratios** must sum to 1.0
- **Probabilities** must be between 0 and 1
- **Model types** must be valid options
- **Devices** must be supported

## Best Practices

### 1. Configuration Organization

```
configs/
├── default_configs.yaml          # Default templates
├── experiments/
│   ├── experiment_001.yaml       # Specific experiments
│   ├── experiment_002.yaml
│   └── ...
├── production/
│   ├── production_diffusion.yaml # Production configs
│   └── production_gan.yaml
└── templates/
    ├── high_res_template.yaml    # Custom templates
    └── fast_training_template.yaml
```

### 2. Environment-Specific Configurations

```python
# Development
config = create_custom_config("diffusion_default", {
    "system.environment": "development",
    "system.debug": True,
    "training.num_epochs": 5,
    "training.use_wandb": False
})

# Production
config = create_custom_config("diffusion_default", {
    "system.environment": "production",
    "system.debug": False,
    "training.num_epochs": 200,
    "training.use_wandb": True,
    "training.save_best_only": True
})
```

### 3. Configuration Versioning

```python
# Version your configurations
config.version = "1.1.0"
config.description = "Updated with new hyperparameters"

# Save with version in filename
manager.save_config(config, f"experiment_v{config.version}.yaml")
```

### 4. Configuration Inheritance

```python
# Base configuration
base_config = quick_load_config("diffusion_default")

# Create variations
high_res_config = create_custom_config("diffusion_default", {
    "model.frame_size": [512, 512],
    "training.batch_size": 2
})

fast_config = create_custom_config("diffusion_default", {
    "model.frame_size": [128, 128],
    "training.num_epochs": 10
})
```

## Troubleshooting

### Common Issues

1. **Configuration not found**
   ```bash
   # Check available configurations
   python config/config_loader.py --list
   ```

2. **Validation errors**
   ```python
   # Check specific errors
   errors = config.get_validation_errors()
   for error in errors:
       print(error)
   ```

3. **Environment variables not working**
   ```bash
   # Check environment variables
   env | grep AI_VIDEO_
   ```

4. **File permissions**
   ```bash
   # Ensure write permissions
   chmod 755 configs/
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Load with debug information
config = quick_load_config("diffusion_default")
print(config.to_yaml())
```

## Examples

See `example_usage.py` for comprehensive examples covering:

1. Loading default configurations
2. Creating custom configurations
3. Environment-specific configurations
4. Using the configuration manager
5. Experiment tracking integration
6. Error handling and validation

Run the examples:

```bash
cd config
python example_usage.py
```

## API Reference

### Core Classes

- `CompleteConfig` - Complete configuration object
- `ConfigManager` - Configuration management utilities
- `ConfigLoader` - Configuration loading with overrides
- `CommandLineConfigLoader` - CLI interface

### Utility Functions

- `quick_load_config(name)` - Load default configuration
- `create_custom_config(base, overrides, name)` - Create custom configuration
- `load_config_with_env(file, name)` - Load with environment overrides
- `validate_and_save_config(config, filepath)` - Validate and save

### Configuration Components

- `SystemConfig` - System settings
- `ModelConfig` - Model architecture
- `DataConfig` - Data loading
- `TrainingConfig` - Training parameters
- `EvaluationConfig` - Evaluation settings

## Contributing

When adding new configuration options:

1. Update the appropriate configuration class
2. Add validation rules
3. Update default configurations
4. Add documentation
5. Include examples

## License

This configuration system is part of the AI Video generation project. 