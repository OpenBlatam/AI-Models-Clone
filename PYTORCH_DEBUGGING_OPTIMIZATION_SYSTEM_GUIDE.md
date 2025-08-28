# PyTorch Debugging and Optimization System Guide

## Overview

The **PyTorch Debugging and Optimization System** is a comprehensive framework that integrates PyTorch's built-in debugging tools and optimization features for enhanced training monitoring and performance. It provides advanced debugging capabilities, memory profiling, gradient analysis, performance optimization, and intelligent recommendations.

## Features

### Core Features
- **Autograd Anomaly Detection**: Built-in PyTorch autograd debugging with `autograd.detect_anomaly()`
- **Memory Profiling**: Real-time memory usage tracking and optimization suggestions
- **Gradient Debugging**: Comprehensive gradient analysis and visualization
- **Performance Profiling**: PyTorch profiler integration for bottleneck identification
- **Model Debugging**: Parameter and activation tracking for model analysis
- **Optimization Advisor**: Intelligent suggestions for performance improvements

### Advanced Features
- **Context Managers**: Easy-to-use debugging contexts for training steps
- **TensorBoard Integration**: Real-time visualization of debugging metrics
- **Comprehensive Reporting**: Detailed debug reports with JSON export
- **Visualization Tools**: Automatic plotting of debugging metrics
- **Error Handling**: Robust error capture and recovery mechanisms

## Installation

### Prerequisites
```bash
pip install torch torchvision
pip install tensorboard  # For TensorBoard logging
pip install matplotlib   # For visualization
pip install pandas       # For data analysis
pip install psutil       # For system monitoring
pip install numpy        # For numerical operations
```

### Basic Setup
```python
from pytorch_debugging_optimization_system import setup_debugging

# Quick setup
debug_optimizer = setup_debugging(
    detect_anomaly=True,
    memory_tracking=True,
    gradient_tracking=True,
    enable_profiling=False
)
```

## Configuration

### DebugConfig Options

```python
@dataclass
class DebugConfig:
    # Autograd debugging
    detect_anomaly: bool = False                    # Enable autograd anomaly detection
    anomaly_detection_mode: str = "default"         # "default", "warn", "raise"
    
    # Memory debugging
    memory_tracking: bool = True                    # Enable memory tracking
    memory_interval: int = 100                      # Track every N steps
    memory_detailed: bool = False                   # Detailed memory info
    
    # Gradient debugging
    gradient_tracking: bool = True                  # Enable gradient tracking
    gradient_norm_threshold: float = 1.0            # Gradient norm threshold
    gradient_clipping: bool = True                  # Enable gradient clipping
    gradient_clip_norm: float = 1.0                 # Gradient clip norm
    
    # Performance profiling
    enable_profiling: bool = False                  # Enable PyTorch profiler
    profile_memory: bool = True                     # Profile memory usage
    profile_cpu: bool = True                        # Profile CPU operations
    profile_cuda: bool = True                       # Profile CUDA operations
    profile_interval: int = 1000                    # Profile every N steps
    
    # Model debugging
    model_parameter_tracking: bool = True           # Track model parameters
    weight_norm_tracking: bool = True               # Track weight norms
    activation_tracking: bool = False               # Track activations
    
    # Output settings
    debug_dir: str = "debug_logs"                   # Debug output directory
    tensorboard_logging: bool = True                # Enable TensorBoard
    console_output: bool = True                     # Enable console output
    save_debug_info: bool = True                    # Save debug information
    
    # Optimization settings
    enable_optimization_suggestions: bool = True    # Enable optimization suggestions
    optimization_threshold: float = 0.1             # Performance improvement threshold
```

## Usage Examples

### Basic Debugging Setup

```python
from pytorch_debugging_optimization_system import PyTorchDebugOptimizer, DebugConfig

# Create configuration
config = DebugConfig(
    detect_anomaly=True,
    memory_tracking=True,
    gradient_tracking=True,
    enable_profiling=False,
    debug_dir="experiments/debug"
)

# Initialize debug optimizer
debug_optimizer = PyTorchDebugOptimizer(config)

# Example model
model = nn.Sequential(
    nn.Linear(10, 5),
    nn.ReLU(),
    nn.Linear(5, 1)
)
optimizer = optim.Adam(model.parameters())
```

### Training Loop with Debugging

```python
# Training loop with comprehensive debugging
for step in range(100):
    with debug_optimizer.debug_context(step, "training"):
        # Forward pass
        x = torch.randn(32, 10)
        y = torch.randn(32, 1)
        
        output = model(x)
        loss = nn.MSELoss()(output, y)
        
        # Backward pass
        loss.backward()
        
        # Track gradients and parameters
        debug_optimizer.track_gradients(model, step)
        debug_optimizer.track_parameters(model, step)
        
        # Optimizer step
        optimizer.step()
        optimizer.zero_grad()
    
    # Get optimization suggestions periodically
    if step % 10 == 0:
        suggestions = debug_optimizer.get_optimization_suggestions()
        print(f"Step {step} suggestions: {suggestions}")

# Save debug report
debug_optimizer.save_debug_report("training_debug_report.json")

# Close debug optimizer
debug_optimizer.close()
```

### Autograd Anomaly Detection

```python
from pytorch_debugging_optimization_system import AutogradDebugger

# Create autograd debugger
config = DebugConfig(detect_anomaly=True, anomaly_detection_mode="warn")
autograd_debugger = AutogradDebugger(config)

# Use in training
with autograd_debugger.detect_anomaly():
    # Your training code here
    x = torch.randn(2, 2, requires_grad=True)
    y = x * 2
    y.sum().backward()

# Check for anomalies
anomaly_summary = autograd_debugger.get_anomaly_summary()
if anomaly_summary['anomaly_detected']:
    print(f"Detected {anomaly_summary['anomaly_count']} anomalies")
```

### Memory Profiling

```python
from pytorch_debugging_optimization_system import MemoryProfiler

# Create memory profiler
config = DebugConfig(memory_tracking=True, memory_interval=10)
memory_profiler = MemoryProfiler(config)

# Track memory during training
for step in range(100):
    if step % config.memory_interval == 0:
        memory_info = memory_profiler.track_memory(step, "training")
        print(f"Step {step}: CUDA Memory = {memory_info['cuda_allocated']:.2f} GB")
    
    # Training step
    # ... your training code ...

# Get memory summary
memory_summary = memory_profiler.get_memory_summary()
print(f"Peak memory usage: {memory_summary['peak_memory_gb']:.2f} GB")

# Get optimization suggestions
suggestions = memory_profiler.get_memory_optimization_suggestions()
print("Memory optimization suggestions:", suggestions)
```

### Gradient Debugging

```python
from pytorch_debugging_optimization_system import GradientDebugger

# Create gradient debugger
config = DebugConfig(gradient_tracking=True, gradient_clipping=True)
gradient_debugger = GradientDebugger(config)

# Training loop with gradient tracking
for step in range(100):
    # Forward and backward pass
    output = model(x)
    loss = criterion(output, y)
    loss.backward()
    
    # Track gradients
    gradient_info = gradient_debugger.track_gradients(model, step)
    
    # Clip gradients if enabled
    total_norm = gradient_debugger.clip_gradients(model)
    
    # Optimizer step
    optimizer.step()
    optimizer.zero_grad()

# Get gradient summary
gradient_summary = gradient_debugger.get_gradient_summary()
print(f"Gradient anomalies: {gradient_summary['anomaly_count']}")

# Plot gradient norms
gradient_debugger.plot_gradient_norms("gradient_norms.png")
```

### Performance Profiling

```python
from pytorch_debugging_optimization_system import PerformanceProfiler

# Create performance profiler
config = DebugConfig(enable_profiling=True, profile_interval=50)
performance_profiler = PerformanceProfiler(config)

# Training loop with profiling
for step in range(100):
    if step % config.profile_interval == 0:
        with performance_profiler.profile(step):
            # Profiled training step
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
    else:
        # Regular training step
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

# Get performance summary
performance_summary = performance_profiler.get_performance_summary()
print(f"Average step time: {performance_summary['average_time']:.3f}s")

# Identify bottlenecks
bottlenecks = performance_profiler.identify_bottlenecks()
print("Performance bottlenecks:", bottlenecks)
```

### Model Debugging

```python
from pytorch_debugging_optimization_system import ModelDebugger

# Create model debugger
config = DebugConfig(model_parameter_tracking=True, activation_tracking=True)
model_debugger = ModelDebugger(config)

# Track parameters during training
for step in range(100):
    # Track parameters
    parameter_info = model_debugger.track_parameters(model, step)
    
    # Track activations (if enabled)
    if config.activation_tracking:
        activation_info = model_debugger.track_activations(model, x)
    
    # Training step
    # ... your training code ...

# Get model summary
model_summary = model_debugger.get_model_summary()
print(f"Tracked {model_summary['parameter_count']} parameters")
```

### Complete Integration Example

```python
from pytorch_debugging_optimization_system import setup_debugging
import torch.nn as nn
import torch.optim as optim

# Setup debugging
debug_optimizer = setup_debugging(
    detect_anomaly=True,
    memory_tracking=True,
    gradient_tracking=True,
    enable_profiling=True,
    debug_dir="experiments/complete_debug"
)

# Model and optimizer
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(128, 10)
)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Training loop with comprehensive debugging
for epoch in range(10):
    for batch_idx, (data, target) in enumerate(train_loader):
        step = epoch * len(train_loader) + batch_idx
        
        with debug_optimizer.debug_context(step, f"epoch_{epoch}"):
            # Forward pass
            output = model(data)
            loss = criterion(output, target)
            
            # Backward pass
            loss.backward()
            
            # Track gradients and parameters
            debug_optimizer.track_gradients(model, step)
            debug_optimizer.track_parameters(model, step)
            
            # Optimizer step
            optimizer.step()
            optimizer.zero_grad()
        
        # Periodic optimization suggestions
        if step % 100 == 0:
            suggestions = debug_optimizer.get_optimization_suggestions()
            if suggestions:
                print(f"Step {step} optimization suggestions:")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
    
    # Save intermediate report
    debug_optimizer.save_debug_report(f"epoch_{epoch}_debug_report.json")

# Final report and cleanup
debug_optimizer.save_debug_report("final_debug_report.json")
debug_optimizer.close()
```

## Component Details

### AutogradDebugger

The `AutogradDebugger` provides PyTorch's built-in autograd anomaly detection:

```python
@contextmanager
def detect_anomaly(self):
    """Context manager for autograd anomaly detection."""
    # Enables autograd.set_detect_anomaly(True)
    # Automatically detects NaN/Inf in gradients
    # Provides detailed error information
```

**Features:**
- Automatic NaN/Inf detection in gradients
- Detailed error tracebacks
- Configurable detection modes (default, warn, raise)
- Context manager for easy integration

### MemoryProfiler

The `MemoryProfiler` tracks memory usage and provides optimization suggestions:

```python
def track_memory(self, step: int, context: str = "") -> Dict[str, Any]:
    """Track memory usage at a specific step."""
    # Tracks system and CUDA memory
    # Monitors peak memory usage
    # Provides memory warnings
    # Suggests optimization strategies
```

**Features:**
- Real-time system and CUDA memory tracking
- Peak memory monitoring
- Memory usage warnings
- Optimization suggestions (gradient checkpointing, mixed precision, etc.)

### GradientDebugger

The `GradientDebugger` provides comprehensive gradient analysis:

```python
def track_gradients(self, model: nn.Module, step: int) -> Dict[str, Any]:
    """Track gradients for all model parameters."""
    # Tracks gradient norms, means, stds
    # Detects gradient anomalies
    # Provides gradient clipping
    # Creates gradient visualizations
```

**Features:**
- Gradient norm tracking for all parameters
- Anomaly detection (NaN, Inf, large norms)
- Automatic gradient clipping
- Gradient visualization plots
- Statistical analysis of gradients

### PerformanceProfiler

The `PerformanceProfiler` integrates PyTorch's profiler for performance analysis:

```python
@contextmanager
def profile(self, step: int):
    """Context manager for performance profiling."""
    # Uses torch.profiler.profile
    # Tracks CPU and CUDA operations
    # Identifies performance bottlenecks
    # Provides optimization recommendations
```

**Features:**
- PyTorch profiler integration
- CPU and CUDA operation tracking
- Bottleneck identification
- Performance optimization suggestions
- Detailed operation timing

### ModelDebugger

The `ModelDebugger` tracks model parameters and activations:

```python
def track_parameters(self, model: nn.Module, step: int) -> Dict[str, Any]:
    """Track model parameters."""
    # Tracks parameter norms, means, stds
    # Monitors parameter changes over time
    # Detects parameter anomalies
    # Provides parameter statistics
```

**Features:**
- Parameter norm tracking
- Weight change monitoring
- Activation tracking (optional)
- Parameter anomaly detection
- Statistical analysis of parameters

### OptimizationAdvisor

The `OptimizationAdvisor` provides intelligent optimization suggestions:

```python
def analyze_performance(self, ...) -> List[str]:
    """Analyze performance and provide optimization suggestions."""
    # Analyzes memory usage patterns
    # Examines gradient behavior
    # Reviews performance metrics
    # Suggests specific optimizations
```

**Features:**
- Memory optimization suggestions
- Gradient optimization recommendations
- Performance improvement strategies
- Model optimization advice
- Hardware-specific recommendations

## Debug Reports

### Report Structure

The system generates comprehensive debug reports in JSON format:

```json
{
    "config": {
        "detect_anomaly": true,
        "memory_tracking": true,
        "gradient_tracking": true,
        "enable_profiling": false
    },
    "memory_summary": {
        "peak_memory_gb": 2.5,
        "total_tracking_points": 100,
        "memory_warnings": 3,
        "cuda_memory_stats": {
            "mean": 1.8,
            "std": 0.3,
            "min": 1.2,
            "max": 2.5
        }
    },
    "gradient_summary": {
        "total_tracking_points": 100,
        "anomaly_count": 0,
        "parameter_count": 4,
        "parameter_stats": {
            "weight": {
                "mean": 0.15,
                "std": 0.05,
                "min": 0.08,
                "max": 0.25
            }
        }
    },
    "performance_summary": {
        "total_steps": 50,
        "total_time": 25.5,
        "average_time": 0.51,
        "min_time": 0.45,
        "max_time": 0.65
    },
    "model_summary": {
        "parameter_count": 4,
        "tracking_points": 100,
        "parameter_stats": {
            "weight": {
                "mean": 1.2,
                "std": 0.1,
                "min": 1.0,
                "max": 1.4
            }
        }
    },
    "optimization_suggestions": {
        "suggestions_count": 2,
        "suggestions": [
            "High memory variance detected. Consider using gradient checkpointing.",
            "Large model detected. Consider model pruning or quantization."
        ]
    },
    "autograd_anomalies": {
        "anomaly_detected": false,
        "anomaly_count": 0,
        "anomalies": []
    },
    "debug_history": [
        {
            "step": 1,
            "timestamp": 1640995200.0,
            "memory": {
                "system_used": 8.5,
                "cuda_allocated": 1.8
            },
            "autograd_anomalies": {
                "anomaly_detected": false,
                "anomaly_count": 0
            }
        }
    ]
}
```

### Report Analysis

The debug reports provide insights into:

1. **Memory Usage Patterns**: Peak usage, variance, warnings
2. **Gradient Behavior**: Norms, anomalies, parameter statistics
3. **Performance Metrics**: Step times, bottlenecks, profiling data
4. **Model Health**: Parameter changes, activation patterns
5. **Optimization Opportunities**: Specific suggestions for improvement
6. **Anomaly Detection**: Autograd and gradient anomalies

## Visualization

### Automatic Plots

The system automatically generates visualization plots:

```python
# Memory usage over time
# Gradient norms for each parameter
# Performance metrics
# Parameter statistics
debug_optimizer.plot_debug_visualizations()
```

### TensorBoard Integration

Real-time visualization through TensorBoard:

```python
# Gradients are logged as scalars
# Parameters are tracked over time
# Memory usage is visualized
# Performance metrics are displayed
```

## Best Practices

### 1. Selective Debugging

```python
# Enable only necessary debugging features
config = DebugConfig(
    detect_anomaly=True,      # Always enable for production
    memory_tracking=True,     # Enable for memory-constrained environments
    gradient_tracking=True,   # Enable for training stability
    enable_profiling=False,   # Disable for regular training (performance impact)
    activation_tracking=False # Disable unless needed (memory intensive)
)
```

### 2. Performance Considerations

```python
# Use profiling selectively
if step % 100 == 0:  # Profile every 100 steps
    with performance_profiler.profile(step):
        # Training step
        pass

# Memory tracking intervals
if step % 50 == 0:  # Track memory every 50 steps
    memory_profiler.track_memory(step, "training")
```

### 3. Error Handling

```python
try:
    with debug_optimizer.debug_context(step, "training"):
        # Training code
        pass
except Exception as e:
    # Debug information is automatically captured
    debug_optimizer.save_debug_report("error_debug_report.json")
    raise e
```

### 4. Optimization Workflow

```python
# 1. Run with full debugging enabled
debug_optimizer = setup_debugging(
    detect_anomaly=True,
    memory_tracking=True,
    gradient_tracking=True,
    enable_profiling=True
)

# 2. Analyze suggestions
suggestions = debug_optimizer.get_optimization_suggestions()

# 3. Implement optimizations
for suggestion in suggestions:
    if "gradient checkpointing" in suggestion:
        # Implement gradient checkpointing
        pass
    elif "mixed precision" in suggestion:
        # Implement mixed precision training
        pass

# 4. Re-run with optimizations
# 5. Compare performance
```

### 5. Production Deployment

```python
# Minimal debugging for production
config = DebugConfig(
    detect_anomaly=True,      # Keep for error detection
    memory_tracking=False,    # Disable for performance
    gradient_tracking=False,  # Disable for performance
    enable_profiling=False,   # Disable for performance
    console_output=False,     # Disable for clean logs
    save_debug_info=True      # Keep for post-analysis
)
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   ```python
   # Enable memory tracking
   config = DebugConfig(memory_tracking=True, memory_interval=10)
   
   # Check suggestions
   suggestions = memory_profiler.get_memory_optimization_suggestions()
   ```

2. **Gradient Explosion**
   ```python
   # Enable gradient tracking and clipping
   config = DebugConfig(
       gradient_tracking=True,
       gradient_clipping=True,
       gradient_clip_norm=1.0
   )
   ```

3. **Slow Training**
   ```python
   # Enable profiling to identify bottlenecks
   config = DebugConfig(enable_profiling=True, profile_interval=100)
   
   # Analyze bottlenecks
   bottlenecks = performance_profiler.identify_bottlenecks()
   ```

4. **Autograd Anomalies**
   ```python
   # Enable anomaly detection
   config = DebugConfig(detect_anomaly=True, anomaly_detection_mode="warn")
   
   # Check anomaly summary
   anomaly_summary = autograd_debugger.get_anomaly_summary()
   ```

### Performance Impact

- **Memory Tracking**: ~1ms per tracking point
- **Gradient Tracking**: ~2ms per step
- **Parameter Tracking**: ~1ms per step
- **Profiling**: ~10-50ms per profiled step
- **Anomaly Detection**: ~5ms per step

### Memory Overhead

- **Debug History**: ~1KB per tracking point
- **Gradient History**: ~2KB per step
- **Parameter History**: ~1KB per step
- **Profiler Data**: ~10-100KB per profiled step

## Integration with Existing Systems

### With Training Logging System

```python
from training_logging_system import TrainingLogger
from pytorch_debugging_optimization_system import PyTorchDebugOptimizer

# Setup both systems
logger = TrainingLogger(logging_config)
debug_optimizer = PyTorchDebugOptimizer(debug_config)

# Use together in training
for step in range(100):
    with debug_optimizer.debug_context(step, "training"):
        # Training step
        loss = train_step()
        
        # Log metrics
        logger.log_metric("loss", loss, step)
        
        # Track debugging info
        debug_optimizer.track_gradients(model, step)
```

### With Custom Training Loops

```python
class DebuggedTrainer:
    def __init__(self, model, config):
        self.model = model
        self.debug_optimizer = PyTorchDebugOptimizer(config)
    
    def train_step(self, data, target, step):
        with self.debug_optimizer.debug_context(step, "training"):
            # Forward pass
            output = self.model(data)
            loss = self.criterion(output, target)
            
            # Backward pass
            loss.backward()
            
            # Track debugging info
            self.debug_optimizer.track_gradients(self.model, step)
            self.debug_optimizer.track_parameters(self.model, step)
            
            # Optimizer step
            self.optimizer.step()
            self.optimizer.zero_grad()
            
            return loss.item()
```

## Conclusion

The PyTorch Debugging and Optimization System provides comprehensive debugging capabilities that integrate seamlessly with PyTorch's built-in tools. It enables:

- **Proactive Debugging**: Early detection of issues before they cause failures
- **Performance Optimization**: Data-driven optimization suggestions
- **Memory Management**: Efficient memory usage monitoring and optimization
- **Training Stability**: Gradient and parameter monitoring for stable training
- **Production Readiness**: Configurable debugging levels for different environments

The system is designed to be:
- **Easy to Use**: Simple setup and integration
- **Comprehensive**: Covers all aspects of training debugging
- **Performant**: Minimal overhead with selective enabling
- **Extensible**: Modular design for custom requirements
- **Production-Ready**: Robust error handling and reporting

This debugging system addresses the critical need for comprehensive training monitoring and optimization in PyTorch-based deep learning workflows. 