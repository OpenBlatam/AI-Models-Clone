# Gradient Clipping and NaN/Inf Handling System Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Gradient Clipping Strategies](#gradient-clipping-strategies)
4. [NaN/Inf Detection and Handling](#naninf-detection-and-handling)
5. [Gradient Monitoring](#gradient-monitoring)
6. [Training Stability Manager](#training-stability-manager)
7. [Factory Pattern](#factory-pattern)
8. [Utility Functions](#utility-functions)
9. [Best Practices](#best-practices)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

## System Overview

The Gradient Clipping and NaN/Inf Handling System provides comprehensive tools for maintaining training stability in deep learning models. It includes various gradient clipping strategies, robust NaN/Inf detection and handling, gradient monitoring, and automatic recovery mechanisms.

### Key Features

- **Multiple Gradient Clipping Strategies**: Norm-based, value-based, adaptive, and layer-wise clipping
- **Comprehensive NaN/Inf Detection**: Automatic detection in gradients, parameters, loss, and outputs
- **Recovery Mechanisms**: Multiple strategies for handling training failures
- **Gradient Monitoring**: Real-time monitoring of gradient health and statistics
- **Training Stability Manager**: Unified interface for all stability features
- **Performance Optimization**: Efficient implementation with minimal overhead
- **Production Ready**: Well-tested with comprehensive error handling

## Core Components

### 1. GradientClipper (Abstract Base Class)

Abstract base class for all gradient clipping strategies:

```python
from gradient_clipping_nan_handling_system import GradientClipper

class CustomClipper(GradientClipper):
    def __init__(self, custom_param: float):
        super().__init__(max_norm=1.0, norm_type=2.0)
        self.custom_param = custom_param
    
    def clip_gradients(self, parameters: List[torch.Tensor]) -> float:
        # Custom clipping logic
        return clip_value
```

### 2. NaNInfHandler

Comprehensive NaN/Inf detection and handling:

```python
from gradient_clipping_nan_handling_system import NaNInfHandler

handler = NaNInfHandler(
    check_gradients=True,
    check_parameters=True,
    check_loss=True,
    check_outputs=True,
    recovery_strategy='skip_batch',
    max_consecutive_failures=5
)
```

### 3. GradientMonitor

Real-time gradient monitoring and statistics:

```python
from gradient_clipping_nan_handling_system import GradientMonitor

monitor = GradientMonitor(
    log_interval=100,
    save_interval=1000,
    save_path='./gradient_stats'
)
```

### 4. TrainingStabilityManager

Unified interface for all stability features:

```python
from gradient_clipping_nan_handling_system import TrainingStabilityManager

manager = TrainingStabilityManager(
    clipper=clipper,
    nan_handler=handler,
    monitor=monitor,
    enable_monitoring=True
)
```

## Gradient Clipping Strategies

### 1. NormClipper (Norm-Based Clipping)

Standard norm-based gradient clipping:

```python
from gradient_clipping_nan_handling_system import NormClipper

clipper = NormClipper(max_norm=1.0, norm_type=2.0)

# Clip gradients
parameters = [p for p in model.parameters() if p.grad is not None]
total_norm = clipper.clip_gradients(parameters)

print(f"Total norm: {total_norm:.4f}")
print(f"Clip ratio: {clipper.get_clip_ratio():.4f}")
```

**Parameters:**
- `max_norm`: Maximum allowed gradient norm
- `norm_type`: Type of norm (2.0 for L2, 1.0 for L1, etc.)

### 2. ValueClipper (Value-Based Clipping)

Clip individual gradient values:

```python
from gradient_clipping_nan_handling_system import ValueClipper

clipper = ValueClipper(max_value=0.5)

# Clip gradients
parameters = [p for p in model.parameters() if p.grad is not None]
clip_ratio = clipper.clip_gradients(parameters)

print(f"Clip ratio: {clip_ratio:.4f}")
```

**Parameters:**
- `max_value`: Maximum absolute value for any gradient element

### 3. AdaptiveClipper (Adaptive Clipping)

Automatically adjust clipping threshold based on training dynamics:

```python
from gradient_clipping_nan_handling_system import AdaptiveClipper

clipper = AdaptiveClipper(
    initial_norm=1.0,
    factor=2.0,
    patience=5,
    min_norm=0.1,
    max_norm=10.0
)

# Clip gradients (threshold adjusts automatically)
parameters = [p for p in model.parameters() if p.grad is not None]
total_norm = clipper.clip_gradients(parameters)

print(f"Current norm threshold: {clipper.current_norm:.4f}")
```

**Parameters:**
- `initial_norm`: Initial clipping threshold
- `factor`: Factor for adjusting threshold
- `patience`: Steps before adjusting threshold
- `min_norm`: Minimum allowed threshold
- `max_norm`: Maximum allowed threshold

### 4. LayerwiseClipper (Layer-Wise Clipping)

Clip gradients layer by layer:

```python
from gradient_clipping_nan_handling_system import LayerwiseClipper

clipper = LayerwiseClipper(max_norm=1.0, norm_type=2.0)

# Clip gradients layer by layer
parameters = [p for p in model.parameters() if p.grad is not None]
total_norm = clipper.clip_gradients(parameters)
```

## NaN/Inf Detection and Handling

### 1. Tensor Checking

```python
from gradient_clipping_nan_handling_system import NaNInfHandler

handler = NaNInfHandler()

# Check individual tensors
tensor = torch.randn(10, 10)
is_valid = handler.check_tensor(tensor, "test_tensor")

# Check for NaN/Inf
tensor_with_nan = torch.randn(10, 10)
tensor_with_nan[0, 0] = float('nan')
is_valid = handler.check_tensor(tensor_with_nan, "tensor_with_nan")
```

### 2. Model Checking

```python
# Check entire model
is_valid = handler.check_model(model)

# Check specific components
is_valid = handler.check_loss(loss)
is_valid = handler.check_outputs(outputs)
```

### 3. Recovery Strategies

```python
# Configure recovery strategy
handler = NaNInfHandler(recovery_strategy='skip_batch')

# Handle failure
success = handler.handle_failure(model, optimizer)

# Available strategies:
# - 'skip_batch': Skip the current batch
# - 'reset_gradients': Reset all gradients
# - 'reduce_lr': Reduce learning rate
# - 'restore_checkpoint': Restore from checkpoint
```

### 4. Failure Statistics

```python
# Get failure statistics
stats = handler.get_failure_stats()

print(f"Total failures: {stats['total_failures']}")
print(f"Consecutive failures: {stats['consecutive_failures']}")
print(f"Recovery actions: {stats['recovery_actions']}")
```

## Gradient Monitoring

### 1. Basic Monitoring

```python
from gradient_clipping_nan_handling_system import GradientMonitor

monitor = GradientMonitor(
    log_interval=100,
    save_interval=1000,
    save_path='./gradient_stats'
)

# Update monitoring
monitor.update(model, loss)
```

### 2. Health Score Calculation

```python
# Calculate gradient health score
health_score = monitor.calculate_health_score(model)

# Health score ranges from 0 to 1
# Higher values indicate healthier gradients
print(f"Gradient health score: {health_score:.4f}")
```

### 3. Statistics Logging

```python
# Log current statistics
monitor.log_statistics()

# Save statistics to file
monitor.save_statistics()
```

### 4. Visualization

```python
# Plot gradient statistics
monitor.plot_statistics(save_path='gradient_analysis.png')
```

## Training Stability Manager

### 1. Basic Usage

```python
from gradient_clipping_nan_handling_system import TrainingStabilityManager

# Create stability manager
manager = TrainingStabilityManager(
    clipper=clipper,
    nan_handler=handler,
    monitor=monitor,
    enable_monitoring=True
)

# Use in training loop
for epoch in range(num_epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        # Forward pass
        output = model(data)
        loss = criterion(output, target)
        
        # Check before backward
        if not manager.before_backward(model, loss):
            continue
        
        # Backward pass
        loss.backward()
        
        # Check after backward
        if not manager.after_backward(model, optimizer):
            continue
        
        # Optimizer step
        optimizer.step()
        optimizer.zero_grad()
        
        # Update monitoring
        manager.after_optimizer_step(model, loss)
```

### 2. Training Statistics

```python
# Get comprehensive training statistics
stats = manager.get_training_stats()

print("Clipper Statistics:")
print(f"Clip ratio: {stats['clipper_stats']['clip_ratio']:.4f}")

print("NaN Handler Statistics:")
print(f"Total failures: {stats['nan_handler_stats']['total_failures']}")

print("Monitor Statistics:")
print(f"Health score: {np.mean(stats['monitor_stats']['health_scores']):.4f}")
```

### 3. Checkpoint Management

```python
# Save checkpoint with stability information
manager.save_checkpoint(
    model, optimizer, epoch=1, step=100, 
    save_path='checkpoint.pth'
)

# Load checkpoint with stability information
epoch, step = manager.load_checkpoint(
    model, optimizer, 'checkpoint.pth'
)
```

### 4. Training Analysis

```python
# Plot comprehensive training analysis
manager.plot_training_analysis(save_path='training_analysis.png')
```

## Factory Pattern

### 1. GradientClippingFactory

```python
from gradient_clipping_nan_handling_system import GradientClippingFactory

# Create different clipping strategies
norm_clipper = GradientClippingFactory.create_norm_clipper(max_norm=1.0)
value_clipper = GradientClippingFactory.create_value_clipper(max_value=0.5)
adaptive_clipper = GradientClippingFactory.create_adaptive_clipper(initial_norm=1.0)
layerwise_clipper = GradientClippingFactory.create_layerwise_clipper(max_norm=1.0)
```

### 2. Stability Manager Factory

```python
from gradient_clipping_nan_handling_system import create_stability_manager

# Create stability manager with specific clipping strategy
manager = create_stability_manager(
    clip_type='adaptive',
    initial_norm=1.0,
    factor=2.0,
    patience=5
)

# Available clip types: 'norm', 'value', 'adaptive', 'layerwise'
```

## Utility Functions

### 1. Model Health Check

```python
from gradient_clipping_nan_handling_system import check_model_health

# Check overall model health
health_stats = check_model_health(model)

print(f"Parameter count: {health_stats['parameter_count']}")
print(f"NaN parameters: {health_stats['nan_parameters']}")
print(f"Inf parameters: {health_stats['inf_parameters']}")
print(f"NaN gradients: {health_stats['nan_gradients']}")
print(f"Inf gradients: {health_stats['inf_gradients']}")
```

### 2. Safe Backward Pass

```python
from gradient_clipping_nan_handling_system import safe_backward

# Perform safe backward pass
success = safe_backward(loss, manager, model, optimizer)

if success:
    print("Backward pass successful")
else:
    print("Backward pass failed, recovery applied")
```

## Best Practices

### 1. Gradient Clipping Selection

#### For Stable Training
```python
# Use norm-based clipping for general stability
clipper = NormClipper(max_norm=1.0)

# Use adaptive clipping for dynamic environments
clipper = AdaptiveClipper(initial_norm=1.0, factor=2.0, patience=5)
```

#### For Specific Problems
```python
# Use value-based clipping for outlier gradients
clipper = ValueClipper(max_value=0.5)

# Use layer-wise clipping for heterogeneous models
clipper = LayerwiseClipper(max_norm=1.0)
```

### 2. NaN/Inf Handling Configuration

```python
# Conservative approach
handler = NaNInfHandler(
    check_gradients=True,
    check_parameters=True,
    check_loss=True,
    check_outputs=True,
    recovery_strategy='skip_batch',
    max_consecutive_failures=3
)

# Aggressive approach
handler = NaNInfHandler(
    recovery_strategy='reduce_lr',
    max_consecutive_failures=10
)
```

### 3. Monitoring Configuration

```python
# Light monitoring
monitor = GradientMonitor(log_interval=1000)

# Detailed monitoring
monitor = GradientMonitor(
    log_interval=100,
    save_interval=1000,
    save_path='./detailed_stats'
)
```

### 4. Training Loop Integration

```python
# Complete training loop with stability management
def train_with_stability(model, train_loader, optimizer, criterion, manager):
    model.train()
    
    for batch_idx, (data, target) in enumerate(train_loader):
        # Forward pass
        output = model(data)
        loss = criterion(output, target)
        
        # Safe backward pass
        success = safe_backward(loss, manager, model, optimizer)
        
        if not success:
            logger.warning(f"Training step {batch_idx} failed")
            continue
        
        # Log progress
        if batch_idx % 100 == 0:
            stats = manager.get_training_stats()
            logger.info(f"Step {batch_idx}: Loss={loss.item():.6f}, "
                       f"Clip Ratio={stats['clipper_stats']['clip_ratio']:.4f}")
```

## Examples

### 1. Basic Training with Stability

```python
import torch
import torch.nn as nn
import torch.optim as optim
from gradient_clipping_nan_handling_system import create_stability_manager

# Create model and optimizer
model = nn.Sequential(
    nn.Linear(784, 512),
    nn.ReLU(),
    nn.Linear(512, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Create stability manager
manager = create_stability_manager(
    clip_type='adaptive',
    initial_norm=1.0,
    factor=2.0,
    patience=5
)

# Training loop
for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        # Forward pass
        output = model(data)
        loss = criterion(output, target)
        
        # Safe backward pass
        success = safe_backward(loss, manager, model, optimizer)
        
        if not success:
            continue
        
        # Log progress
        if batch_idx % 100 == 0:
            stats = manager.get_training_stats()
            print(f"Epoch {epoch}, Batch {batch_idx}: "
                  f"Loss={loss.item():.6f}, "
                  f"Clip Ratio={stats['clipper_stats']['clip_ratio']:.4f}")
    
    # Plot analysis at end of epoch
    manager.plot_training_analysis(f'epoch_{epoch}_analysis.png')
```

### 2. Advanced Training with Custom Recovery

```python
# Custom recovery strategy
class CustomNaNHandler(NaNInfHandler):
    def handle_failure(self, model, optimizer):
        # Custom recovery logic
        if self.consecutive_failures >= 3:
            # Reset model to last good state
            self._reset_model(model)
            return True
        else:
            # Use default strategy
            return super().handle_failure(model, optimizer)
    
    def _reset_model(self, model):
        # Implementation for model reset
        pass

# Use custom handler
handler = CustomNaNHandler(recovery_strategy='skip_batch')
manager = TrainingStabilityManager(nan_handler=handler)
```

### 3. Monitoring and Analysis

```python
# Comprehensive monitoring
monitor = GradientMonitor(
    log_interval=50,
    save_interval=500,
    save_path='./training_stats'
)

manager = TrainingStabilityManager(monitor=monitor)

# Training loop
for epoch in range(num_epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        # ... training code ...
        
        # Update monitoring
        manager.after_optimizer_step(model, loss)
    
    # Analyze epoch
    stats = manager.get_training_stats()
    
    print(f"Epoch {epoch} Summary:")
    print(f"  Average health score: {np.mean(stats['monitor_stats']['health_scores']):.4f}")
    print(f"  Total failures: {stats['nan_handler_stats']['total_failures']}")
    print(f"  Clip ratio: {stats['clipper_stats']['clip_ratio']:.4f}")
    
    # Plot detailed analysis
    manager.plot_training_analysis(f'epoch_{epoch}_detailed.png')
```

### 4. Production Training Loop

```python
def production_training_loop(model, train_loader, optimizer, criterion, manager):
    """Production-ready training loop with comprehensive stability management."""
    
    # Initialize tracking
    epoch_stats = []
    failure_counts = []
    
    for epoch in range(num_epochs):
        epoch_losses = []
        epoch_clips = []
        
        for batch_idx, (data, target) in enumerate(train_loader):
            try:
                # Forward pass
                output = model(data)
                loss = criterion(output, target)
                
                # Check for NaN/Inf in loss
                if not manager.before_backward(model, loss):
                    logger.warning(f"NaN/Inf detected in loss at epoch {epoch}, batch {batch_idx}")
                    continue
                
                # Backward pass
                loss.backward()
                
                # Check for NaN/Inf in gradients
                if not manager.after_backward(model, optimizer):
                    logger.warning(f"NaN/Inf detected in gradients at epoch {epoch}, batch {batch_idx}")
                    continue
                
                # Optimizer step
                optimizer.step()
                optimizer.zero_grad()
                
                # Update monitoring
                manager.after_optimizer_step(model, loss)
                
                # Track statistics
                epoch_losses.append(loss.item())
                stats = manager.get_training_stats()
                epoch_clips.append(stats['clipper_stats']['clip_ratio'])
                
            except Exception as e:
                logger.error(f"Training error at epoch {epoch}, batch {batch_idx}: {e}")
                continue
        
        # Epoch summary
        avg_loss = np.mean(epoch_losses)
        avg_clip_ratio = np.mean(epoch_clips)
        failure_count = manager.nan_handler.failure_count
        
        epoch_stats.append({
            'epoch': epoch,
            'avg_loss': avg_loss,
            'avg_clip_ratio': avg_clip_ratio,
            'failure_count': failure_count
        })
        
        logger.info(f"Epoch {epoch}: Loss={avg_loss:.6f}, "
                   f"Clip Ratio={avg_clip_ratio:.4f}, "
                   f"Failures={failure_count}")
        
        # Save checkpoint
        if epoch % 5 == 0:
            manager.save_checkpoint(
                model, optimizer, epoch, batch_idx,
                f'checkpoint_epoch_{epoch}.pth'
            )
    
    return epoch_stats
```

## Troubleshooting

### Common Issues

1. **High Clip Ratio**
   ```python
   # Reduce learning rate
   for param_group in optimizer.param_groups:
       param_group['lr'] *= 0.5
   
   # Increase clipping threshold
   clipper.max_norm *= 2.0
   ```

2. **Frequent NaN/Inf Failures**
   ```python
   # Check for gradient explosion
   for param in model.parameters():
       if param.grad is not None:
           grad_norm = param.grad.norm()
           if grad_norm > 10.0:
               print(f"Large gradient detected: {grad_norm}")
   
   # Use more aggressive clipping
   clipper = NormClipper(max_norm=0.1)
   ```

3. **Poor Health Scores**
   ```python
   # Check gradient-to-parameter ratios
   for name, param in model.named_parameters():
       if param.grad is not None:
           ratio = param.grad.norm() / param.norm()
           if ratio > 1.0:
               print(f"High gradient ratio in {name}: {ratio}")
   ```

4. **Memory Issues**
   ```python
   # Reduce monitoring frequency
   monitor = GradientMonitor(log_interval=1000, save_interval=10000)
   
   # Use lighter monitoring
   manager = TrainingStabilityManager(enable_monitoring=False)
   ```

### Performance Optimization

1. **Batch Processing**
   ```python
   # Process gradients in batches for large models
   def clip_gradients_batch(parameters, batch_size=1000):
       for i in range(0, len(parameters), batch_size):
           batch = parameters[i:i+batch_size]
           clipper.clip_gradients(batch)
   ```

2. **Selective Monitoring**
   ```python
   # Monitor only critical layers
   critical_layers = ['fc1', 'fc2']
   for name, param in model.named_parameters():
       if any(layer in name for layer in critical_layers):
           # Monitor this parameter
           pass
   ```

3. **Efficient NaN Detection**
   ```python
   # Use torch.isnan() and torch.isinf() for efficiency
   def efficient_nan_check(tensor):
       return torch.isnan(tensor).any() or torch.isinf(tensor).any()
   ```

This comprehensive guide covers all aspects of the Gradient Clipping and NaN/Inf Handling System, from basic usage to advanced techniques. The system ensures training stability across various scenarios and provides robust recovery mechanisms for handling training failures. 