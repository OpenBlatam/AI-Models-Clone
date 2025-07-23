# Experiment Tracking System

A comprehensive experiment tracking and model checkpointing system for the Key Messages ML Pipeline. This system provides unified interfaces for TensorBoard, Weights & Biases, and MLflow, along with robust checkpointing mechanisms.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Components](#components)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Integration](#integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

## Overview

The experiment tracking system provides:

- **Unified Tracking Interface**: Single API for TensorBoard, Weights & Biases, and MLflow
- **Robust Checkpointing**: Automatic model and training state saving/loading
- **Comprehensive Metrics**: Scalar, histogram, text, and image logging
- **Flexible Strategies**: Configurable checkpointing strategies
- **Production Ready**: Error handling, fallbacks, and validation

## Architecture

```
experiment_tracking/
├── __init__.py              # Main interface and convenience functions
├── tracker.py               # Core tracking classes
├── checkpointing.py         # Checkpoint management system
├── metrics.py               # Metrics tracking and aggregation
├── tests/                   # Comprehensive test suite
│   └── test_experiment_tracking.py
└── README.md               # This documentation
```

### Core Components

1. **ExperimentTracker**: Abstract base class for all trackers
2. **CheckpointManager**: Handles model and training state persistence
3. **MetricsTracker**: Comprehensive metrics logging and aggregation
4. **TrainingMetricsTracker**: Specialized tracker for training workflows

## Installation

### Dependencies

The system supports multiple tracking backends. Install the ones you need:

```bash
# Core dependencies
pip install torch numpy structlog

# TensorBoard (recommended)
pip install tensorboard

# Weights & Biases (optional)
pip install wandb

# MLflow (optional)
pip install mlflow
```

### From Source

```bash
cd agents/backend/onyx/server/features/key_messages/ml
pip install -e .
```

## Quick Start

### Basic Setup

```python
from ml.experiment_tracking import create_tracker, create_checkpoint_manager
from ml.config import get_config

# Load configuration
config = get_config("production")

# Create tracker and checkpoint manager
tracker = create_tracker(config["experiment_tracking"])
checkpoint_manager = create_checkpoint_manager(config["training"]["default"])

# Initialize experiment
tracker.init_experiment("key_messages_training", config=config)
```

### Training Loop Integration

```python
# During training
for epoch in range(num_epochs):
    for batch_idx, (inputs, targets) in enumerate(train_loader):
        # Training step
        loss = model(inputs, targets)
        
        # Log metrics
        tracker.log_metrics({
            "train/loss": loss.item(),
            "train/epoch": epoch,
            "train/step": global_step
        }, step=global_step)
        
        # Save checkpoint
        if checkpoint_manager.should_save_checkpoint(global_step, loss.item()):
            checkpoint_manager.save_checkpoint(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                epoch=epoch,
                step=global_step,
                metrics={"loss": loss.item()}
            )

# Finalize experiment
tracker.finalize_experiment()
```

## Components

### 1. Experiment Trackers

#### TensorBoardTracker

```python
from ml.experiment_tracking import TensorBoardTracker

tracker = TensorBoardTracker(
    log_dir="./logs",
    update_freq=100,
    flush_secs=120
)

tracker.init_experiment("tensorboard_run", config)
tracker.log_metrics({"loss": 0.5}, step=100)
```

#### WandbTracker

```python
from ml.experiment_tracking import WandbTracker

tracker = WandbTracker(
    project="key_messages",
    entity="your_entity",
    tags=["production", "gpt2"]
)

tracker.init_experiment("wandb_run", config)
tracker.log_metrics({"loss": 0.5}, step=100)
```

#### MLflowTracker

```python
from ml.experiment_tracking import MLflowTracker

tracker = MLflowTracker(
    tracking_uri="sqlite:///mlflow.db",
    experiment_name="key_messages",
    log_models=True
)

tracker.init_experiment("mlflow_run", config)
tracker.log_metrics({"loss": 0.5}, step=100)
```

#### CompositeTracker

```python
from ml.experiment_tracking import CompositeTracker

trackers = [
    TensorBoardTracker(log_dir="./logs"),
    WandbTracker(project="key_messages")
]

composite_tracker = CompositeTracker(trackers)
composite_tracker.log_metrics({"loss": 0.5}, step=100)  # Logs to all trackers
```

### 2. Checkpoint Management

#### CheckpointStrategy

```python
from ml.experiment_tracking import CheckpointStrategy

strategy = CheckpointStrategy(
    save_steps=500,
    save_total_limit=5,
    save_best_only=True,
    monitor="val_loss",
    mode="min"
)
```

#### CheckpointManager

```python
from ml.experiment_tracking import CheckpointManager

checkpoint_manager = CheckpointManager(
    checkpoint_dir="./checkpoints",
    strategy=strategy
)

# Save checkpoint
checkpoint_path = checkpoint_manager.save_checkpoint(
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    epoch=epoch,
    step=global_step,
    metrics={"loss": loss.item()}
)

# Load checkpoint
checkpoint = checkpoint_manager.load_checkpoint(checkpoint_path)
model.load_state_dict(checkpoint.model_state)
optimizer.load_state_dict(checkpoint.optimizer_state)
```

### 3. Metrics Tracking

#### MetricsTracker

```python
from ml.experiment_tracking import MetricsTracker

tracker = MetricsTracker(log_frequency=10, window_size=100)

# Log different types of metrics
tracker.log_scalar("loss", 0.5, step=100)
tracker.log_scalars({
    "train_loss": 0.5,
    "val_loss": 0.4,
    "learning_rate": 1e-4
}, step=100)

tracker.log_histogram("gradients", gradients, step=100)
tracker.log_text("generated_text", "Sample text", step=100)
tracker.log_image("attention_weights", attention_weights, step=100)

# Get aggregated metrics
avg_loss = tracker.get_average("loss", window=100)
summary = tracker.get_summary("loss")
```

#### TrainingMetricsTracker

```python
from ml.experiment_tracking import TrainingMetricsTracker

tracker = TrainingMetricsTracker(log_frequency=1)

# Log training step
tracker.log_training_step(
    loss=0.5,
    optimizer=optimizer,
    model=model,
    accuracy=0.9
)

# Log validation step
tracker.log_validation_step(loss=0.3, accuracy=0.95)

# Log epoch
tracker.log_epoch(
    train_metrics={"loss": 0.5, "accuracy": 0.9},
    val_metrics={"loss": 0.3, "accuracy": 0.95}
)
```

## Configuration

### YAML Configuration

```yaml
# config.yaml
experiment_tracking:
  tensorboard:
    enabled: true
    log_dir: "./logs"
    update_freq: 100
    flush_secs: 120
    
  wandb:
    enabled: true
    project: "key_messages"
    entity: "your_entity"
    tags: ["production", "gpt2"]
    notes: "Production training run"
    config_exclude_keys: ["api_key", "secret"]
    
  mlflow:
    enabled: false
    tracking_uri: "sqlite:///mlflow.db"
    experiment_name: "key_messages"
    log_models: true

training:
  default:
    save_steps: 1000
    save_total_limit: 3
    save_best_only: true
    monitor: "val_loss"
    mode: "min"
    checkpoint_dir: "./checkpoints"
```

### Environment-Specific Overrides

```yaml
# environments/development.yaml
experiment_tracking:
  tensorboard:
    enabled: true
    log_dir: "./logs/dev"
    
  wandb:
    enabled: false
    
  mlflow:
    enabled: true
    tracking_uri: "sqlite:///dev_mlflow.db"

training:
  default:
    save_steps: 100
    save_total_limit: 5
```

```yaml
# environments/production.yaml
experiment_tracking:
  tensorboard:
    enabled: true
    log_dir: "./logs/prod"
    
  wandb:
    enabled: true
    project: "key_messages_prod"
    
  mlflow:
    enabled: true
    tracking_uri: "postgresql://user:pass@host:port/mlflow"

training:
  default:
    save_steps: 5000
    save_total_limit: 2
    save_best_only: true
```

## Usage Examples

### 1. Complete Training Workflow

```python
from ml.experiment_tracking import create_tracker, create_checkpoint_manager
from ml.config import get_config

class TrainingManager:
    def __init__(self, config):
        self.tracker = create_tracker(config["experiment_tracking"])
        self.checkpoint_manager = create_checkpoint_manager(config["training"]["default"])
        self.metrics_tracker = TrainingMetricsTracker()
        
    def train(self, model, train_loader, val_loader, num_epochs):
        # Initialize experiment
        self.tracker.init_experiment("training_run", config)
        
        for epoch in range(num_epochs):
            # Training phase
            train_metrics = self._train_epoch(model, train_loader)
            
            # Validation phase
            val_metrics = self._validate_epoch(model, val_loader)
            
            # Log metrics
            self.tracker.log_metrics({
                **train_metrics,
                **val_metrics,
                "epoch": epoch
            }, step=global_step)
            
            # Save checkpoint
            if self.checkpoint_manager.should_save_checkpoint(
                global_step, val_metrics["val_loss"]
            ):
                self.checkpoint_manager.save_checkpoint(
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    epoch=epoch,
                    step=global_step,
                    metrics={**train_metrics, **val_metrics}
                )
        
        # Finalize experiment
        self.tracker.finalize_experiment()
```

### 2. Resuming Training

```python
# Load latest checkpoint
checkpoint = checkpoint_manager.load_latest_checkpoint()

if checkpoint:
    # Restore model and optimizer
    model.load_state_dict(checkpoint.model_state)
    optimizer.load_state_dict(checkpoint.optimizer_state)
    
    # Resume from checkpoint
    start_epoch = checkpoint.epoch + 1
    global_step = checkpoint.step
    
    print(f"Resuming from epoch {start_epoch}, step {global_step}")
else:
    print("Starting fresh training")
```

### 3. Model Evaluation

```python
# Load best checkpoint for evaluation
best_checkpoint = checkpoint_manager.load_best_checkpoint()

if best_checkpoint:
    model.load_state_dict(best_checkpoint.model_state)
    
    # Evaluate model
    eval_metrics = evaluate_model(model, test_loader)
    
    # Log evaluation metrics
    tracker.log_metrics(eval_metrics, step=best_checkpoint.step)
```

### 4. Custom Metrics

```python
# Register custom metrics
def compute_perplexity(model, data_loader):
    # Custom perplexity computation
    return perplexity_value

tracker.register_custom_metric("perplexity", compute_perplexity)

# Use custom metric
tracker.log_custom_metric("perplexity", model, data_loader)
```

## Integration

### With Configuration System

```python
from ml.config import get_config
from ml.experiment_tracking import create_tracker, create_checkpoint_manager

# Load configuration with environment overrides
config = get_config("production")

# Create components from configuration
tracker = create_tracker(config["experiment_tracking"])
checkpoint_manager = create_checkpoint_manager(config["training"]["default"])
```

### With Model Factory

```python
from ml.models import ModelFactory
from ml.experiment_tracking import CheckpointManager

# Load model configuration
model_config = config["models"]["gpt2"]

# Create model
model = ModelFactory.create_model(model_config)

# Load checkpoint if available
checkpoint_manager = CheckpointManager("./checkpoints")
latest_checkpoint = checkpoint_manager.load_latest_checkpoint()

if latest_checkpoint:
    model.load_state_dict(latest_checkpoint.model_state)
```

### With Training Pipeline

```python
from ml.training import TrainingPipeline
from ml.experiment_tracking import TrainingManager

# Create training manager
training_manager = TrainingManager(config)

# Create training pipeline
pipeline = TrainingPipeline(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    training_manager=training_manager
)

# Run training
pipeline.train(num_epochs=10)
```

## Best Practices

### 1. Experiment Organization

- Use descriptive experiment names
- Include model type and hyperparameters in names
- Use tags for easy filtering and organization
- Document experiment purpose in notes

```python
experiment_name = f"gpt2_key_messages_lr{lr}_bs{batch_size}_epochs{num_epochs}"
tags = ["gpt2", "key_messages", "production", f"lr_{lr}"]
notes = "Training GPT-2 model for key message extraction with custom dataset"
```

### 2. Checkpoint Management

- Use meaningful checkpoint strategies
- Monitor validation metrics for best checkpoint selection
- Clean up old checkpoints to save disk space
- Version control checkpoint directories

```python
strategy = CheckpointStrategy(
    save_steps=1000,
    save_total_limit=5,
    save_best_only=True,
    monitor="val_loss",
    mode="min"
)
```

### 3. Metrics Logging

- Log metrics at appropriate frequencies
- Use consistent naming conventions
- Include both training and validation metrics
- Log learning rate and gradient norms

```python
# Consistent naming
tracker.log_metrics({
    "train/loss": train_loss,
    "train/accuracy": train_acc,
    "val/loss": val_loss,
    "val/accuracy": val_acc,
    "train/learning_rate": lr,
    "train/grad_norm": grad_norm
}, step=global_step)
```

### 4. Error Handling

- Always use try-catch blocks for tracking operations
- Implement fallbacks for unavailable tracking services
- Validate configuration before use
- Handle disk space issues gracefully

```python
try:
    tracker.log_metrics(metrics, step=step)
except Exception as e:
    logger.error(f"Failed to log metrics: {e}")
    # Continue training without logging
```

### 5. Performance Optimization

- Use appropriate log frequencies
- Batch metric logging when possible
- Use efficient data structures for aggregation
- Monitor tracking overhead

```python
# Batch logging
if step % log_frequency == 0:
    tracker.log_metrics(batch_metrics, step=step)
```

## Troubleshooting

### Common Issues

#### 1. TensorBoard Not Starting

```bash
# Check if TensorBoard is installed
pip install tensorboard

# Start TensorBoard
tensorboard --logdir=./logs

# Check log directory permissions
ls -la ./logs
```

#### 2. W&B Authentication Issues

```bash
# Login to W&B
wandb login

# Check API key
echo $WANDB_API_KEY

# Test connection
python -c "import wandb; wandb.init(project='test')"
```

#### 3. MLflow Database Issues

```bash
# Check database connection
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Reset database (careful!)
rm mlflow.db
```

#### 4. Checkpoint Loading Errors

```python
# Check checkpoint files
import os
checkpoint_dir = "./checkpoints"
for file in os.listdir(checkpoint_dir):
    print(f"{file}: {os.path.getsize(os.path.join(checkpoint_dir, file))} bytes")

# Validate checkpoint
try:
    checkpoint = checkpoint_manager.load_checkpoint(checkpoint_path)
    print("Checkpoint loaded successfully")
except Exception as e:
    print(f"Checkpoint loading failed: {e}")
```

#### 5. Memory Issues

```python
# Monitor memory usage
import psutil
print(f"Memory usage: {psutil.virtual_memory().percent}%")

# Clear old checkpoints
checkpoint_manager.clear_checkpoints()

# Reduce window size for metrics
tracker = MetricsTracker(window_size=50)
```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## API Reference

### ExperimentTracker

Base class for all experiment trackers.

#### Methods

- `init_experiment(experiment_name, config)`: Initialize experiment
- `log_metrics(metrics, step)`: Log metrics
- `log_config(config)`: Log configuration
- `log_model(model_path, model_name)`: Log model artifacts
- `finalize_experiment()`: Finalize experiment

### CheckpointManager

Manages model and training checkpoints.

#### Methods

- `save_checkpoint(model, optimizer, scheduler, epoch, step, metrics)`: Save checkpoint
- `load_checkpoint(checkpoint_path)`: Load checkpoint
- `load_best_checkpoint()`: Load best checkpoint
- `load_latest_checkpoint()`: Load latest checkpoint
- `should_save_checkpoint(step, metric_value)`: Check if checkpoint should be saved
- `get_checkpoint_info()`: Get checkpoint information
- `clear_checkpoints()`: Clear all checkpoints

### MetricsTracker

Comprehensive metrics tracking system.

#### Methods

- `log_scalar(name, value, step)`: Log scalar metric
- `log_scalars(scalars, step)`: Log multiple scalar metrics
- `log_histogram(name, values, step)`: Log histogram data
- `log_text(name, text, step)`: Log text data
- `log_image(name, image_data, step)`: Log image data
- `get_average(name, window)`: Get average of metric
- `get_latest(name)`: Get latest value of metric
- `get_summary(name)`: Get summary statistics
- `export_metrics()`: Export all metrics
- `import_metrics(data)`: Import metrics data

### TrainingMetricsTracker

Specialized tracker for training workflows.

#### Methods

- `log_training_step(loss, optimizer, model, **kwargs)`: Log training step
- `log_validation_step(loss, **kwargs)`: Log validation step
- `log_epoch(train_metrics, val_metrics)`: Log epoch metrics
- `get_best_metrics()`: Get best metrics achieved

### Configuration

#### experiment_tracking

- `tensorboard`: TensorBoard configuration
- `wandb`: Weights & Biases configuration
- `mlflow`: MLflow configuration

#### training

- `save_steps`: Steps between checkpoints
- `save_total_limit`: Maximum number of checkpoints to keep
- `save_best_only`: Only save best checkpoints
- `monitor`: Metric to monitor for best checkpoint
- `mode`: Optimization mode ("min" or "max")
- `checkpoint_dir`: Checkpoint directory

## Contributing

1. Follow the existing code style
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Test with multiple tracking backends
5. Ensure backward compatibility

## License

This project is part of the Key Messages ML Pipeline and follows the same license terms. 