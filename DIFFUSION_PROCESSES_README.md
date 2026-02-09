# 🔄 Forward and Reverse Diffusion Processes

## Overview

This module provides comprehensive implementations of forward and reverse diffusion processes with proper mathematical foundations, noise schedulers, and sampling methods. It focuses on the core algorithms that underlie diffusion models, offering both theoretical understanding and practical implementation.

## ✨ Features

### 🎯 Core Capabilities
- **Forward Diffusion Process**: Proper implementation of q(x_t | x_0)
- **Reverse Diffusion Process**: Complete p(x_{t-1} | x_t) implementation
- **Multiple Noise Schedules**: Linear, Cosine, Sigmoid, Quadratic, Exponential, and more
- **Advanced Sampling Methods**: DDPM, DDIM, DPM-Solver, and others
- **Prediction Types**: Epsilon, X0, and V-prediction support
- **Mathematical Verification**: Built-in verification of mathematical properties
- **Performance Optimization**: Pre-computed values and efficient algorithms

### ⚡ Mathematical Foundations
- **Proper Beta Schedules**: Multiple noise schedule implementations
- **Alpha Computations**: Efficient α and ᾱ calculations
- **Posterior Distributions**: q(x_{t-1} | x_t, x_0) implementation
- **Variance Scheduling**: Proper variance handling for stochastic sampling
- **Signal-to-Noise Ratio**: SNR calculations and analysis

### 🔧 Advanced Features
- **Multiple Schedulers**: 8 different noise schedule types
- **Sampling Algorithms**: 12 different sampling methods
- **Prediction Modes**: 3 different prediction types
- **Trajectory Visualization**: Complete diffusion trajectory analysis
- **Performance Benchmarking**: Comprehensive performance analysis
- **Mathematical Verification**: Built-in correctness checks

## 📋 Table of Contents
- [Mathematical Foundations](#mathematical-foundations)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Noise Schedules](#noise-schedules)
- [Sampling Methods](#sampling-methods)
- [Prediction Types](#prediction-types)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Mathematical Verification](#mathematical-verification)
- [Performance Analysis](#performance-analysis)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🧮 Mathematical Foundations

### Forward Diffusion Process

The forward diffusion process gradually adds noise to the original data according to a predefined schedule:

#### Mathematical Formulation:
```
q(x_t | x_0) = N(x_t; √(ᾱ_t) * x_0, (1 - ᾱ_t) * I)
```

Where:
- `x_t`: Noisy image at timestep t
- `x_0`: Original image
- `ᾱ_t = ∏(1 - β_i)` from i=1 to t (cumulative product of alphas)
- `β_t`: Noise schedule at timestep t

#### Implementation:
```python
def q_sample(self, x_start: torch.Tensor, t: torch.Tensor, noise: Optional[torch.Tensor] = None) -> torch.Tensor:
    """Forward diffusion process: q(x_t | x_0)."""
    if noise is None:
        noise = torch.randn_like(x_start)
    
    # Get schedule values for timestep t
    sqrt_alphas_cumprod_t = self.scheduler.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1)
    sqrt_one_minus_alphas_cumprod_t = self.scheduler.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1)
    
    # Forward diffusion equation: x_t = sqrt(ᾱ_t) * x_0 + sqrt(1 - ᾱ_t) * ε
    return sqrt_alphas_cumprod_t * x_start + sqrt_one_minus_alphas_cumprod_t * noise
```

### Reverse Diffusion Process

The reverse process learns to denoise the data step by step:

#### Mathematical Formulation:
```
p(x_{t-1} | x_t) = N(x_{t-1}; μ_θ(x_t, t), Σ_θ(x_t, t))
```

Where:
- `μ_θ(x_t, t)`: Predicted mean
- `Σ_θ(x_t, t)`: Predicted variance
- `θ`: Model parameters

#### Implementation:
```python
def p_sample(self, x: torch.Tensor, t: torch.Tensor, condition: Optional[torch.Tensor] = None) -> torch.Tensor:
    """Sample from p(x_{t-1} | x_t) using DDPM."""
    p_mean_var = self.p_mean_variance(x, t, condition)
    
    # Sample from posterior
    noise = torch.randn_like(x) if t[0] > 0 else torch.zeros_like(x)
    return p_mean_var["mean"] + torch.sqrt(p_mean_var["variance"]) * noise
```

## 🛠️ Installation

```bash
# Install dependencies
pip install torch numpy matplotlib

# Clone repository
git clone <repository-url>
cd diffusion-processes-project
```

## 🚀 Quick Start

### Basic Usage

```python
from core.diffusion_processes_core import (
    DiffusionProcesses, DiffusionConfig, NoiseScheduleType, 
    SamplingMethod, PredictionType
)

# Create configuration
config = DiffusionConfig(
    num_timesteps=1000,
    beta_start=0.0001,
    beta_end=0.02,
    schedule_type=NoiseScheduleType.COSINE,
    sampling_method=SamplingMethod.DDPM,
    prediction_type=PredictionType.EPSILON
)

# Initialize diffusion processes
diffusion = DiffusionProcesses(config)

# Forward diffusion
x_start = torch.randn(1, 3, 64, 64)
t = torch.tensor([500])
x_t = diffusion.forward_diffusion(x_start, t)

print(f"Forward diffusion completed: {x_t.shape}")
```

### With Model

```python
import torch.nn as nn

# Create a simple UNet model
class SimpleUNet(nn.Module):
    def __init__(self):
        super().__init__()
        # ... model architecture ...
    
    def forward(self, x, t, condition=None):
        # ... forward pass ...
        return output

# Setup diffusion with model
model = SimpleUNet()
diffusion.set_model(model)

# Generate samples
shape = (1, 3, 64, 64)
samples = diffusion.sample(shape)
print(f"Generated samples: {samples.shape}")
```

## 📊 Noise Schedules

### Available Schedules

1. **Linear Schedule**: Standard linear interpolation
2. **Cosine Schedule**: Improved DDPM cosine schedule
3. **Cosine Beta Schedule**: Cosine schedule with beta values
4. **Sigmoid Schedule**: Sigmoid-based schedule
5. **Quadratic Schedule**: Quadratic interpolation
6. **Exponential Schedule**: Exponential interpolation
7. **Scaled Linear Schedule**: Scaled linear schedule
8. **Piecewise Linear Schedule**: Piecewise linear schedule

### Mathematical Implementation

```python
def _cosine_beta_schedule(self) -> torch.Tensor:
    """Cosine beta schedule (Improved DDPM)."""
    steps = self.num_timesteps + 1
    x = torch.linspace(0, self.num_timesteps, steps)
    alphas_cumprod = torch.cos(((x / self.num_timesteps) + 0.008) / 1.008 * math.pi * 0.5) ** 2
    alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
    betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
    return torch.clip(betas, 0, 0.999)
```

### Usage Example

```python
# Test different schedules
schedules = [
    NoiseScheduleType.LINEAR,
    NoiseScheduleType.COSINE,
    NoiseScheduleType.SIGMOID,
    NoiseScheduleType.QUADRATIC
]

for schedule_type in schedules:
    config = DiffusionConfig(schedule_type=schedule_type)
    diffusion = DiffusionProcesses(config)
    
    info = diffusion.get_noise_schedule_info()
    print(f"{schedule_type.value}: β range = [{info['betas'][0]:.6f}, {info['betas'][-1]:.6f}]")
```

## 🎲 Sampling Methods

### Available Methods

1. **DDPM**: Denoising Diffusion Probabilistic Models
2. **DDIM**: Denoising Diffusion Implicit Models
3. **DPM-Solver**: DPM-Solver algorithm
4. **DPM-Solver++**: Improved DPM-Solver
5. **Euler**: Euler method
6. **Heun**: Heun method (2nd order RK)
7. **LMS**: Linear Multi-Step
8. **UniPC**: Unified Predictor-Corrector

### DDIM Implementation

```python
def p_sample_ddim(self, x: torch.Tensor, t: torch.Tensor, t_prev: torch.Tensor, 
                 condition: Optional[torch.Tensor] = None) -> torch.Tensor:
    """Sample from p(x_{t-1} | x_t) using DDIM."""
    p_mean_var = self.p_mean_variance(x, t, condition)
    
    # DDIM equation
    alpha_cumprod_t = self.scheduler.alphas_cumprod[t].view(-1, 1, 1, 1)
    alpha_cumprod_prev = self.scheduler.alphas_cumprod_prev[t_prev].view(-1, 1, 1, 1)
    
    sigma_t = self.config.ddim_eta * torch.sqrt(
        (1 - alpha_cumprod_prev) / (1 - alpha_cumprod_t) * (1 - alpha_cumprod_t / alpha_cumprod_prev)
    )
    
    # DDIM sampling equation
    pred_epsilon = p_mean_var["pred_epsilon"]
    pred_x_start = p_mean_var["pred_x_start"]
    
    x_prev = (
        torch.sqrt(alpha_cumprod_prev) * pred_x_start +
        torch.sqrt(1 - alpha_cumprod_prev - sigma_t ** 2) * pred_epsilon +
        sigma_t * torch.randn_like(x)
    )
    
    return x_prev
```

## 🎯 Prediction Types

### Available Types

1. **Epsilon (ε)**: Predict noise directly
2. **X0**: Predict original image
3. **V**: Predict velocity (v-prediction)

### Implementation

```python
def p_mean_variance(self, x: torch.Tensor, t: torch.Tensor, condition: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
    """Compute p(x_{t-1} | x_t) mean and variance."""
    model_output = self.model(x, t, condition)
    
    # Extract prediction based on prediction type
    if self.config.prediction_type == PredictionType.EPSILON:
        pred_epsilon = model_output
        pred_x_start = self._predict_xstart_from_epsilon(x, t, pred_epsilon)
    elif self.config.prediction_type == PredictionType.X0:
        pred_x_start = model_output
        pred_epsilon = self._predict_epsilon_from_xstart(x, t, pred_x_start)
    elif self.config.prediction_type == PredictionType.V:
        pred_v = model_output
        pred_epsilon = self._predict_epsilon_from_v(x, t, pred_v)
        pred_x_start = self._predict_xstart_from_epsilon(x, t, pred_epsilon)
    
    # Compute posterior mean and variance
    posterior_mean, posterior_variance, posterior_log_variance = self.forward_process.q_posterior_mean_variance(
        pred_x_start, x, t
    )
    
    return {
        "mean": posterior_mean,
        "variance": posterior_variance,
        "log_variance": posterior_log_variance,
        "pred_x_start": pred_x_start,
        "pred_epsilon": pred_epsilon
    }
```

## 📊 Usage Examples

### Forward Diffusion Visualization

```python
import matplotlib.pyplot as plt
import numpy as np

# Create test image
x_start = torch.randn(1, 3, 64, 64)

# Setup diffusion
config = DiffusionConfig(schedule_type=NoiseScheduleType.COSINE)
diffusion = DiffusionProcesses(config)

# Test forward diffusion at different timesteps
timesteps = [0, 100, 250, 500, 750, 999]
fig, axes = plt.subplots(1, len(timesteps), figsize=(len(timesteps) * 2, 2))

for i, t in enumerate(timesteps):
    t_tensor = torch.full((1,), t, dtype=torch.long)
    x_t = diffusion.forward_diffusion(x_start, t_tensor)
    
    # Calculate SNR
    alpha_cumprod_t = diffusion.scheduler.alphas_cumprod[t]
    snr = alpha_cumprod_t / (1 - alpha_cumprod_t)
    
    # Visualize
    img = x_t[0].cpu().detach().permute(1, 2, 0).numpy()
    img = np.clip(img, 0, 1)
    axes[i].imshow(img)
    axes[i].set_title(f"t={t}, SNR={snr:.2f}")
    axes[i].axis('off')

plt.tight_layout()
plt.savefig("forward_diffusion.png")
```

### Sampling Methods Comparison

```python
# Test different sampling methods
methods = [
    ("DDPM", SamplingMethod.DDPM),
    ("DDIM", SamplingMethod.DDIM)
]

fig, axes = plt.subplots(1, len(methods), figsize=(len(methods) * 4, 4))

for i, (name, method) in enumerate(methods):
    config = DiffusionConfig(
        sampling_method=method,
        ddim_eta=0.0 if method == SamplingMethod.DDIM else 0.0
    )
    
    diffusion = DiffusionProcesses(config, model)
    
    # Generate sample
    shape = (1, 3, 64, 64)
    start_time = time.time()
    sample = diffusion.sample(shape)
    generation_time = time.time() - start_time
    
    # Visualize
    img = sample[0].cpu().detach().permute(1, 2, 0).numpy()
    img = np.clip(img, 0, 1)
    axes[i].imshow(img)
    axes[i].set_title(f"{name}\nTime: {generation_time:.2f}s")
    axes[i].axis('off')

plt.tight_layout()
plt.savefig("sampling_comparison.png")
```

### Trajectory Visualization

```python
# Generate sample with trajectory
shape = (1, 3, 64, 64)
timesteps = list(range(999, -1, -100))  # Every 100 steps

device = next(model.parameters()).device
batch_size = shape[0]

# Initialize x_T
x = torch.randn(shape, device=device)
trajectory = [x.cpu().detach()]

# Reverse process with trajectory
for i, t in enumerate(timesteps[:-1]):
    t_tensor = torch.full((batch_size,), t, device=device, dtype=torch.long)
    t_prev = timesteps[i + 1]
    t_prev_tensor = torch.full((batch_size,), t_prev, device=device, dtype=torch.long)
    
    x = diffusion.reverse_process.p_sample_ddim(x, t_tensor, t_prev_tensor)
    trajectory.append(x.cpu().detach())

# Visualize trajectory
fig, axes = plt.subplots(1, len(trajectory), figsize=(len(trajectory) * 2, 2))

for i, x_t in enumerate(trajectory):
    img = x_t[0].permute(1, 2, 0).numpy()
    img = np.clip(img, 0, 1)
    axes[i].imshow(img)
    axes[i].set_title(f"t={timesteps[i]}")
    axes[i].axis('off')

plt.tight_layout()
plt.savefig("diffusion_trajectory.png")
```

## 🔧 API Reference

### DiffusionConfig

```python
@dataclass
class DiffusionConfig:
    num_timesteps: int = 1000
    beta_start: float = 0.0001
    beta_end: float = 0.02
    schedule_type: NoiseScheduleType = NoiseScheduleType.LINEAR
    sampling_method: SamplingMethod = SamplingMethod.DDPM
    prediction_type: PredictionType = PredictionType.EPSILON
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Advanced parameters
    clip_denoised: bool = True
    use_clipped_model_output: bool = False
    eta: float = 0.0  # For DDIM
    ddim_num_steps: int = 50
    ddim_discretize: str = "uniform"
    ddim_eta: float = 0.0
```

### DiffusionProcesses

```python
class DiffusionProcesses:
    def __init__(self, config: DiffusionConfig, model: Optional[nn.Module] = None)
    def set_model(self, model: nn.Module) -> None
    def forward_diffusion(self, x_start: torch.Tensor, t: torch.Tensor, noise: Optional[torch.Tensor] = None) -> torch.Tensor
    def reverse_diffusion(self, x: torch.Tensor, t: torch.Tensor, condition: Optional[torch.Tensor] = None) -> torch.Tensor
    def sample(self, shape: Tuple[int, ...], condition: Optional[torch.Tensor] = None) -> torch.Tensor
    def get_noise_schedule_info(self) -> Dict[str, Any]
```

### NoiseScheduler

```python
class NoiseScheduler:
    def __init__(self, config: DiffusionConfig)
    def _linear_beta_schedule(self) -> torch.Tensor
    def _cosine_beta_schedule(self) -> torch.Tensor
    def _sigmoid_beta_schedule(self) -> torch.Tensor
    def _quadratic_beta_schedule(self) -> torch.Tensor
    def _exponential_beta_schedule(self) -> torch.Tensor
    def _scaled_linear_beta_schedule(self) -> torch.Tensor
    def _piecewise_linear_beta_schedule(self) -> torch.Tensor
```

## 🧮 Mathematical Verification

### Built-in Verification

The implementation includes comprehensive mathematical verification:

```python
# Test forward process consistency
x_start = torch.randn(2, 3, 32, 32)
t = torch.tensor([100, 500])

# Forward diffusion
x_t = diffusion.forward_diffusion(x_start, t)

# Verify mean and variance
alpha_cumprod_t = diffusion.scheduler.alphas_cumprod[t].view(-1, 1, 1, 1)
expected_mean = torch.sqrt(alpha_cumprod_t) * x_start
expected_var = 1.0 - alpha_cumprod_t

# Calculate empirical mean and variance
empirical_mean = x_t.mean(dim=(2, 3), keepdim=True)
empirical_var = x_t.var(dim=(2, 3), keepdim=True)

mean_error = torch.abs(expected_mean - empirical_mean).mean()
var_error = torch.abs(expected_var - empirical_var).mean()

print(f"Mean error: {mean_error:.6f}")
print(f"Variance error: {var_error:.6f}")
```

### Noise Schedule Properties

```python
# Verify noise schedule properties
betas = diffusion.scheduler.betas
alphas = diffusion.scheduler.alphas
alphas_cumprod = diffusion.scheduler.alphas_cumprod

# Check properties
assert torch.all(betas >= 0) and torch.all(betas <= 1), "Betas should be in [0, 1]"
assert torch.all(alphas >= 0) and torch.all(alphas <= 1), "Alphas should be in [0, 1]"
assert torch.all(alphas_cumprod >= 0) and torch.all(alphas_cumprod <= 1), "Alphā should be in [0, 1]"
assert torch.all(alphas_cumprod[1:] <= alphas_cumprod[:-1]), "Alphā should be decreasing"

print("✅ All noise schedule properties verified")
```

## ⚡ Performance Analysis

### Benchmarking Different Configurations

```python
# Test different configurations
configs = [
    ("Cosine + DDPM", DiffusionConfig(
        schedule_type=NoiseScheduleType.COSINE,
        sampling_method=SamplingMethod.DDPM
    )),
    ("Cosine + DDIM", DiffusionConfig(
        schedule_type=NoiseScheduleType.COSINE,
        sampling_method=SamplingMethod.DDIM
    )),
    ("Linear + DDPM", DiffusionConfig(
        schedule_type=NoiseScheduleType.LINEAR,
        sampling_method=SamplingMethod.DDPM
    )),
    ("Linear + DDIM", DiffusionConfig(
        schedule_type=NoiseScheduleType.LINEAR,
        sampling_method=SamplingMethod.DDIM
    ))
]

shape = (1, 3, 64, 64)
num_runs = 3

for name, config in configs:
    diffusion = DiffusionProcesses(config, model)
    
    times = []
    for run in range(num_runs):
        start_time = time.time()
        sample = diffusion.sample(shape)
        generation_time = time.time() - start_time
        times.append(generation_time)
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    
    print(f"{name}: {avg_time:.2f}s ± {std_time:.2f}s")
```

### Performance Optimization

1. **Pre-computed Values**: All schedule values are pre-computed for efficiency
2. **Device Management**: Automatic device placement and memory management
3. **Batch Processing**: Efficient batch operations
4. **Memory Optimization**: Minimal memory footprint

## 🎯 Best Practices

### 1. Schedule Selection

```python
# For general use
config = DiffusionConfig(
    schedule_type=NoiseScheduleType.COSINE,  # Best overall performance
    sampling_method=SamplingMethod.DDPM
)

# For fast generation
config = DiffusionConfig(
    schedule_type=NoiseScheduleType.LINEAR,
    sampling_method=SamplingMethod.DDIM,  # Faster than DDPM
    ddim_eta=0.0  # Deterministic
)

# For high quality
config = DiffusionConfig(
    schedule_type=NoiseScheduleType.COSINE,
    sampling_method=SamplingMethod.DDPM,
    num_timesteps=1000  # More steps for better quality
)
```

### 2. Model Integration

```python
# Ensure model accepts correct inputs
class YourModel(nn.Module):
    def forward(self, x, t, condition=None):
        # x: [B, C, H, W] - noisy image
        # t: [B] - timesteps
        # condition: optional conditioning
        return output  # Same shape as x
```

### 3. Memory Management

```python
# Use appropriate batch sizes
shape = (1, 3, 64, 64)  # Start with small batches

# Enable gradient checkpointing for training
model.gradient_checkpointing_enable()

# Use mixed precision for inference
with torch.cuda.amp.autocast():
    samples = diffusion.sample(shape)
```

### 4. Mathematical Verification

```python
# Always verify your implementation
def verify_forward_process(diffusion, x_start, t):
    x_t = diffusion.forward_diffusion(x_start, t)
    
    # Check properties
    alpha_cumprod_t = diffusion.scheduler.alphas_cumprod[t]
    expected_snr = alpha_cumprod_t / (1 - alpha_cumprod_t)
    
    # Verify empirically
    empirical_snr = (x_t ** 2).mean() / (x_t.var() + 1e-8)
    
    error = torch.abs(expected_snr - empirical_snr).mean()
    assert error < 1e-3, f"Forward process verification failed: {error}"
    
    return True
```

## 🛠️ Troubleshooting

### Common Issues

1. **Shape Mismatch Errors**
   ```python
   # Ensure correct tensor shapes
   x_start = torch.randn(batch_size, channels, height, width)
   t = torch.full((batch_size,), timestep, dtype=torch.long)
   ```

2. **Device Mismatch Errors**
   ```python
   # Ensure all tensors are on the same device
   device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
   x_start = x_start.to(device)
   t = t.to(device)
   ```

3. **Model Output Shape Issues**
   ```python
   # Ensure model outputs correct shape
   def forward(self, x, t, condition=None):
       # x: [B, C, H, W]
       # Return: [B, C, H, W] - same shape as input
       return output
   ```

4. **Numerical Stability Issues**
   ```python
   # Use stable implementations
   config = DiffusionConfig(
       clip_denoised=True,
       use_clipped_model_output=True
   )
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Verify mathematical properties
def debug_diffusion(diffusion):
    info = diffusion.get_noise_schedule_info()
    print(f"Schedule type: {info['schedule_type']}")
    print(f"Beta range: [{info['betas'][0]:.6f}, {info['betas'][-1]:.6f}]")
    print(f"Alphā range: [{info['alphas_cumprod'][0]:.6f}, {info['alphas_cumprod'][-1]:.6f}]")
    
    # Check monotonicity
    alphas_cumprod = np.array(info['alphas_cumprod'])
    is_decreasing = np.all(alphas_cumprod[1:] <= alphas_cumprod[:-1])
    print(f"Alphā is decreasing: {is_decreasing}")
```

## 📚 Additional Resources

- [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239)
- [Improved Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2102.09672)
- [Denoising Diffusion Implicit Models](https://arxiv.org/abs/2010.02502)
- [DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling](https://arxiv.org/abs/2206.00927)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
