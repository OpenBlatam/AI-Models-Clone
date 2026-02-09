# Training Logging System Guide

## Overview

The Training Logging System is a comprehensive logging framework designed specifically for deep learning training workflows. It provides real-time monitoring, error tracking, metric visualization, and multiple output formats to ensure robust and informative training sessions.

## Features

### Core Features
- **Multi-Output Logging**: Console, file, TensorBoard, and Weights & Biases integration
- **Real-time Monitoring**: Live training progress tracking with customizable intervals
- **Error Handling**: Comprehensive error capture and debugging information
- **Metric Visualization**: Automatic plotting and summary statistics
- **Performance Optimization**: Asynchronous logging for high-throughput scenarios
- **File Management**: Automatic log rotation and backup management

### Advanced Features
- **Exception Capture**: Global exception handling with detailed tracebacks
- **Configuration Management**: JSON-based configuration storage and retrieval
- **CSV Metrics Export**: Structured metric data for external analysis
- **Color-coded Console Output**: Enhanced readability with ANSI color codes
- **Thread-safe Operations**: Safe concurrent logging operations

## Installation

### Prerequisites
```bash
pip install torch torchvision
pip install tensorboard  # For TensorBoard logging
pip install wandb        # For Weights & Biases logging
pip install matplotlib   # For metric plotting
pip install pandas       # For data analysis
pip install seaborn      # For enhanced plotting
```

### Basic Setup
```python
from training_logging_system import setup_logging, LoggingConfig

# Quick setup
logger = setup_logging(
    experiment_name="my_experiment",
    log_dir="logs",
    console_logging=True,
    file_logging=True,
    tensorboard_logging=True
)
```

## Configuration

### LoggingConfig Options

```python
@dataclass
class LoggingConfig:
    # Basic settings
    log_dir: str = "logs"                    # Log directory
    experiment_name: str = "experiment"      # Experiment name
    log_level: str = "INFO"                  # Logging level
    
    # Output settings
    console_logging: bool = True             # Enable console output
    file_logging: bool = True                # Enable file logging
    tensorboard_logging: bool = False        # Enable TensorBoard
    wandb_logging: bool = False              # Enable W&B logging
    
    # File settings
    log_file: str = "training.log"           # Main log file
    metrics_file: str = "metrics.csv"        # Metrics CSV file
    config_file: str = "config.json"         # Config JSON file
    
    # Performance settings
    flush_interval: float = 1.0              # Flush interval (seconds)
    max_log_size: int = 100 * 1024 * 1024   # Max log file size (100MB)
    backup_count: int = 5                    # Number of backup files
    
    # Metrics settings
    log_interval: int = 1                    # Log every N steps
    save_interval: int = 100                 # Save every N steps
    
    # Error handling
    capture_exceptions: bool = True          # Capture uncaught exceptions
    log_traceback: bool = True               # Include tracebacks in logs
```

## Usage Examples

### Basic Logging

```python
from training_logging_system import TrainingLogger, LoggingConfig

# Create configuration
config = LoggingConfig(
    experiment_name="cnn_training",
    log_dir="experiments/cnn",
    console_logging=True,
    file_logging=True,
    tensorboard_logging=True
)

# Initialize logger
logger = TrainingLogger(config)

# Log configuration
logger.log_config({
    "model": "ResNet18",
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100
})

# Training loop
for epoch in range(100):
    for batch_idx, (data, target) in enumerate(train_loader):
        # Training step
        loss = train_step(data, target)
        
        # Log metrics
        if batch_idx % 10 == 0:
            logger.log_metrics({
                "loss": loss.item(),
                "learning_rate": optimizer.param_groups[0]['lr'],
                "epoch": epoch
            }, step=epoch * len(train_loader) + batch_idx)
    
    # Log epoch summary
    logger.log_info(f"Epoch {epoch} completed")
    logger.step()

# Save metrics plot
logger.save_metrics_plot("training_metrics.png")

# Close logger
logger.close()
```

### Advanced Logging with Error Handling

```python
import torch
import torch.nn as nn
from training_logging_system import LoggedTrainingLoop, LoggingConfig

# Create configuration with error handling
config = LoggingConfig(
    experiment_name="robust_training",
    capture_exceptions=True,
    log_traceback=True,
    log_interval=5
)

# Mock model and data
model = nn.Linear(10, 1)
dataloader = [(torch.randn(32, 10), torch.randn(32, 1)) for _ in range(10)]
optimizer = torch.optim.Adam(model.parameters())
criterion = nn.MSELoss()

# Create training loop with logging
training_loop = LoggedTrainingLoop(model, config)

# Train with automatic error handling
for epoch in range(5):
    try:
        # Training epoch
        train_metrics = training_loop.train_epoch(
            dataloader, optimizer, criterion, epoch
        )
        
        # Validation
        val_metrics = training_loop.validate(
            dataloader, criterion, epoch
        )
        
        # Log epoch summary
        training_loop.logger.log_metrics({
            **train_metrics,
            **val_metrics
        }, step=epoch)
        
    except Exception as e:
        training_loop.logger.log_error(f"Epoch {epoch} failed: {e}")
        continue

training_loop.close()
```

### Asynchronous Logging for High Performance

```python
from training_logging_system import AsyncLogger, LoggingConfig

# Create configuration for high-performance logging
config = LoggingConfig(
    experiment_name="high_perf_training",
    log_interval=1,
    flush_interval=0.1
)

# Create async logger
async_logger = AsyncLogger(config)

# High-frequency logging (non-blocking)
for step in range(10000):
    # Training computation
    loss = compute_loss()
    
    # Non-blocking metric logging
    async_logger.log_metric("loss", loss, step)
    
    if step % 100 == 0:
        async_logger.log_text(f"Completed {step} steps")

# Close async logger
async_logger.close()
```

### TensorBoard Integration

```python
from training_logging_system import TrainingLogger, LoggingConfig

# Enable TensorBoard logging
config = LoggingConfig(
    experiment_name="tensorboard_demo",
    tensorboard_logging=True,
    tensorboard_dir="runs"
)

logger = TrainingLogger(config)

# Log model graph (if using PyTorch)
if torch is not None:
    model = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 1))
    dummy_input = torch.randn(1, 10)
    
    # Get TensorBoard logger
    tb_logger = next((l for l in logger.loggers if isinstance(l, TensorBoardLogger)), None)
    if tb_logger:
        tb_logger.log_model_graph(model, dummy_input)

# Log metrics to TensorBoard
for step in range(100):
    logger.log_metric("training_loss", 1.0 / (step + 1), step)
    logger.log_metric("validation_loss", 1.0 / (step + 2), step)

logger.close()
```

### Weights & Biases Integration

```python
from training_logging_system import TrainingLogger, LoggingConfig

# Enable W&B logging
config = LoggingConfig(
    experiment_name="wandb_demo",
    wandb_logging=True,
    wandb_project="my_project",
    wandb_entity="my_username"
)

logger = TrainingLogger(config)

# Log model to W&B
if torch is not None:
    model = nn.Linear(10, 1)
    wb_logger = next((l for l in logger.loggers if isinstance(l, WandBLogger)), None)
    if wb_logger:
        wb_logger.log_model(model, "my_model")

# Log metrics to W&B
for step in range(100):
    logger.log_metrics({
        "loss": 1.0 / (step + 1),
        "accuracy": 0.5 + step * 0.005,
        "learning_rate": 0.001
    }, step)

logger.close()
```

## Logger Types

### ConsoleLogger
- **Purpose**: Real-time console output with color coding
- **Features**: ANSI color support, configurable log levels
- **Use Case**: Development and debugging

### FileLogger
- **Purpose**: Persistent file-based logging
- **Features**: Log rotation, CSV metrics export, JSON config storage
- **Use Case**: Production training and long-term storage

### TensorBoardLogger
- **Purpose**: TensorBoard integration for visualization
- **Features**: Scalar plots, histograms, model graphs, images
- **Use Case**: Training visualization and monitoring

### WandBLogger
- **Purpose**: Weights & Biases integration
- **Features**: Experiment tracking, model versioning, collaboration
- **Use Case**: Team collaboration and experiment management

## Error Handling

### Automatic Exception Capture
```python
config = LoggingConfig(capture_exceptions=True, log_traceback=True)
logger = TrainingLogger(config)

# Any uncaught exception will be automatically logged
def risky_function():
    raise ValueError("Something went wrong")

# This will be automatically logged
risky_function()
```

### Manual Error Logging
```python
try:
    # Risky operation
    result = model(data)
except Exception as e:
    logger.log_error(f"Model inference failed: {e}", traceback=traceback.format_exc())
```

### Error Recovery
```python
def safe_training_step(logger, model, data, target):
    try:
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        return loss.item()
    except RuntimeError as e:
        logger.log_error(f"Training step failed: {e}")
        return None
    except Exception as e:
        logger.log_error(f"Unexpected error: {e}")
        return None
```

## Performance Optimization

### Asynchronous Logging
```python
# For high-frequency logging
async_logger = AsyncLogger(config)

# Non-blocking operations
for step in range(10000):
    async_logger.log_metric("loss", loss, step)
    # Training continues without waiting for logging
```

### Batch Logging
```python
# Log multiple metrics at once
logger.log_metrics({
    "loss": loss.item(),
    "accuracy": accuracy,
    "learning_rate": lr,
    "gradient_norm": grad_norm
}, step=current_step)
```

### Conditional Logging
```python
# Only log every N steps
if step % config.log_interval == 0:
    logger.log_metric("loss", loss, step)
```

## File Management

### Log Rotation
```python
config = LoggingConfig(
    max_log_size=50 * 1024 * 1024,  # 50MB
    backup_count=3
)
```

### Directory Structure
```
logs/
├── experiment_name/
│   ├── training.log          # Main log file
│   ├── training.log.1        # Backup files
│   ├── training.log.2
│   ├── metrics.csv           # Metrics data
│   ├── config.json           # Configuration
│   └── runs/                 # TensorBoard logs
│       └── experiment_name/
│           └── events.out.tfevents.*
```

## Metrics and Visualization

### Metric Summary
```python
# Get summary statistics
summary = logger.get_metrics_summary()
print(summary)
# Output:
# {
#     'loss': {'mean': 0.15, 'min': 0.1, 'max': 0.2, 'count': 100},
#     'accuracy': {'mean': 0.85, 'min': 0.8, 'max': 0.9, 'count': 100}
# }
```

### Automatic Plotting
```python
# Save metrics plot
logger.save_metrics_plot("training_metrics.png")
```

### Custom Visualization
```python
import matplotlib.pyplot as plt

# Load metrics from CSV
import pandas as pd
df = pd.read_csv("logs/experiment/metrics.csv")

# Create custom plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Loss plot
loss_data = df[df['metric_name'] == 'loss']
ax1.plot(loss_data['step'], loss_data['value'])
ax1.set_title('Training Loss')
ax1.set_xlabel('Step')
ax1.set_ylabel('Loss')

# Accuracy plot
acc_data = df[df['metric_name'] == 'accuracy']
ax2.plot(acc_data['step'], acc_data['value'])
ax2.set_title('Training Accuracy')
ax2.set_xlabel('Step')
ax2.set_ylabel('Accuracy')

plt.tight_layout()
plt.savefig('custom_metrics.png')
plt.close()
```

## Integration with Training Frameworks

### PyTorch Training Loop
```python
class LoggedTrainer:
    def __init__(self, model, config):
        self.model = model
        self.logger = TrainingLogger(config)
    
    def train(self, train_loader, val_loader, epochs):
        for epoch in range(epochs):
            # Training
            train_loss = self.train_epoch(train_loader, epoch)
            
            # Validation
            val_loss = self.validate(val_loader, epoch)
            
            # Logging
            self.logger.log_metrics({
                'train_loss': train_loss,
                'val_loss': val_loss,
                'epoch': epoch
            }, step=epoch)
    
    def train_epoch(self, loader, epoch):
        self.model.train()
        total_loss = 0
        
        for batch_idx, (data, target) in enumerate(loader):
            try:
                loss = self.training_step(data, target)
                total_loss += loss
                
                if batch_idx % 10 == 0:
                    self.logger.log_metric('batch_loss', loss, 
                                         step=epoch * len(loader) + batch_idx)
            except Exception as e:
                self.logger.log_error(f"Batch {batch_idx} failed: {e}")
                continue
        
        return total_loss / len(loader)
```

### Custom Training Loop
```python
def custom_training_loop(model, dataloader, logger):
    model.train()
    
    for step, (data, target) in enumerate(dataloader):
        try:
            # Forward pass
            output = model(data)
            loss = criterion(output, target)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Logging
            if step % logger.config.log_interval == 0:
                logger.log_metrics({
                    'loss': loss.item(),
                    'step': step,
                    'lr': optimizer.param_groups[0]['lr']
                }, step=step)
            
            logger.step()
            
        except Exception as e:
            logger.log_error(f"Step {step} failed: {e}")
            continue
```

## Best Practices

### 1. Configuration Management
```python
# Use meaningful experiment names
config = LoggingConfig(
    experiment_name="resnet18_cifar10_lr0.001_bs32",
    log_dir="experiments/resnet18"
)

# Log configuration at start
logger.log_config({
    "model": "ResNet18",
    "dataset": "CIFAR-10",
    "learning_rate": 0.001,
    "batch_size": 32,
    "optimizer": "Adam",
    "scheduler": "StepLR"
})
```

### 2. Error Handling
```python
# Always wrap training loops in try-except
try:
    for epoch in range(epochs):
        train_epoch()
        validate_epoch()
except KeyboardInterrupt:
    logger.log_info("Training interrupted by user")
    # Save checkpoint
except Exception as e:
    logger.log_error(f"Training failed: {e}")
    # Cleanup and exit gracefully
finally:
    logger.close()
```

### 3. Performance Monitoring
```python
# Log performance metrics
import time

start_time = time.time()
for epoch in range(epochs):
    epoch_start = time.time()
    
    # Training
    train_epoch()
    
    epoch_time = time.time() - epoch_start
    logger.log_metrics({
        'epoch_time': epoch_time,
        'total_time': time.time() - start_time
    }, step=epoch)
```

### 4. Resource Management
```python
# Use context managers for automatic cleanup
from contextlib import contextmanager

@contextmanager
def logged_training(config):
    logger = TrainingLogger(config)
    try:
        yield logger
    finally:
        logger.close()

# Usage
with logged_training(config) as logger:
    # Training code here
    pass
```

### 5. Metric Naming
```python
# Use consistent metric names
logger.log_metrics({
    'train/loss': train_loss,
    'train/accuracy': train_acc,
    'val/loss': val_loss,
    'val/accuracy': val_acc,
    'learning_rate': lr
}, step=step)
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```python
   # Ensure log directory is writable
   import os
   os.makedirs("logs", exist_ok=True)
   ```

2. **Memory Issues**
   ```python
   # Use async logging for high-frequency operations
   config = LoggingConfig(log_interval=10)  # Log less frequently
   async_logger = AsyncLogger(config)
   ```

3. **TensorBoard Not Showing Data**
   ```python
   # Ensure TensorBoard directory exists
   config = LoggingConfig(
       tensorboard_logging=True,
       tensorboard_dir="runs"
   )
   ```

4. **W&B Authentication**
   ```python
   # Set up W&B authentication
   import wandb
   wandb.login()
   ```

### Debug Mode
```python
# Enable debug logging
config = LoggingConfig(log_level="DEBUG")
logger = TrainingLogger(config)

# Debug information will be logged
logger.log_debug("Debug information")
```

## API Reference

### TrainingLogger Methods

- `log_metric(name, value, step=None)`: Log a single metric
- `log_metrics(metrics, step=None)`: Log multiple metrics
- `log_text(text, level="INFO")`: Log text message
- `log_config(config)`: Log configuration
- `log_error(message, traceback=None)`: Log error with optional traceback
- `log_warning(message)`: Log warning message
- `log_info(message)`: Log info message
- `log_debug(message)`: Log debug message
- `step()`: Increment step counter
- `get_metrics_summary()`: Get summary statistics
- `save_metrics_plot(save_path)`: Save metrics plot
- `close()`: Close all loggers

### Configuration Options

See the `LoggingConfig` dataclass for all available configuration options.

## Conclusion

The Training Logging System provides a comprehensive solution for logging deep learning training sessions. With its modular design, multiple output formats, and robust error handling, it ensures that you never lose important training information and can easily debug issues when they arise.

For more advanced usage patterns and integration examples, refer to the test suite and additional documentation. 