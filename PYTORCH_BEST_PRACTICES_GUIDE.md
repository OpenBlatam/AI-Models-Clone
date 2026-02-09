# 🚀 PyTorch Best Practices Guide for Deep Learning

## Overview

This guide covers comprehensive PyTorch best practices for production-ready deep learning development, incorporating the latest PyTorch features and optimization techniques.

## 🏗️ Core PyTorch Architecture

### 1. **Model Definition Best Practices**

```python
import torch
import torch.nn as nn

class OptimizedModel(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._setup_model()
        self._apply_optimizations()
    
    def _setup_model(self):
        """Setup model architecture with proper initialization."""
        # Use proper weight initialization
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.LayerNorm):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
    
    def _apply_optimizations(self):
        """Apply PyTorch-specific optimizations."""
        if self.config.use_gradient_checkpointing:
            self.gradient_checkpointing_enable()
        
        if self.config.use_channels_last:
            self = self.to(memory_format=torch.channels_last)
        
        if self.config.use_torch_compile and hasattr(torch, 'compile'):
            self = torch.compile(self)
```

### 2. **Configuration Management**

```python
from dataclasses import dataclass

@dataclass
class PyTorchConfig:
    # Model settings
    model_name: str = "gpt2"
    max_length: int = 512
    
    # Training settings
    batch_size: int = 8
    learning_rate: float = 2e-5
    num_epochs: int = 3
    
    # PyTorch optimizations
    use_mixed_precision: bool = True
    use_gradient_clipping: bool = True
    use_torch_compile: bool = False
    use_channels_last: bool = True
    
    # Hardware settings
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    num_gpus: int = torch.cuda.device_count()
```

## ⚡ Performance Optimizations

### 1. **Mixed Precision Training**

```python
from torch.cuda.amp import autocast, GradScaler

class OptimizedTrainer:
    def __init__(self, config):
        self.scaler = GradScaler() if config.use_mixed_precision else None
    
    def train_step(self, batch):
        with autocast() if self.config.use_mixed_precision else nullcontext():
            outputs = self.model(**batch)
            loss = outputs["loss"]
        
        if self.config.use_mixed_precision:
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            loss.backward()
            self.optimizer.step()
```

### 2. **Memory Optimization**

```python
def optimize_memory_usage(config):
    """Apply memory optimization techniques."""
    if torch.cuda.is_available():
        # Enable memory efficient attention
        torch.backends.cuda.enable_flash_sdp(True)
        
        # Enable TF32 for better performance
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        
        # Set memory format
        if config.use_channels_last:
            torch.backends.cudnn.benchmark = True

def memory_tracking_context():
    """Context manager for memory tracking."""
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()
    
    yield
    
    if torch.cuda.is_available():
        peak_memory = torch.cuda.max_memory_allocated() / 1024**3
        logger.info(f"Peak GPU memory: {peak_memory:.2f} GB")
```

### 3. **Gradient Accumulation and Clipping**

```python
def train_with_gradient_accumulation(model, dataloader, config):
    """Train with gradient accumulation."""
    for batch_idx, batch in enumerate(dataloader):
        # Forward pass
        outputs = model(**batch)
        loss = outputs["loss"] / config.gradient_accumulation_steps
        loss.backward()
        
        # Gradient accumulation
        if (batch_idx + 1) % config.gradient_accumulation_steps == 0:
            # Gradient clipping
            if config.use_gradient_clipping:
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), 
                    config.max_grad_norm
                )
            
            # Optimizer step
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)  # More efficient
```

## 🔧 Advanced PyTorch Features

### 1. **Torch Compile (PyTorch 2.0+)**

```python
def compile_model(model, config):
    """Compile model for better performance."""
    if config.use_torch_compile and hasattr(torch, 'compile'):
        try:
            compiled_model = torch.compile(
                model,
                mode="default",  # or "reduce-overhead", "max-autotune"
                fullgraph=True
            )
            logger.info("Model compiled successfully")
            return compiled_model
        except Exception as e:
            logger.warning(f"torch.compile failed: {e}")
            return model
    return model
```

### 2. **Distributed Training**

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel

def setup_distributed_training(config):
    """Setup distributed training."""
    if config.num_gpus > 1:
        try:
            dist.init_process_group(backend=config.ddp_backend)
            model = DistributedDataParallel(model)
            logger.info("Distributed training initialized")
            return True
        except Exception as e:
            logger.warning(f"Distributed training failed: {e}")
            return False
    return False
```

### 3. **Custom CUDA Kernels**

```python
from torch.utils.cpp_extension import load_inline

def create_custom_cuda_kernel():
    """Create custom CUDA kernel for specific operations."""
    cuda_source = """
    extern "C" __global__ void custom_kernel(float* input, float* output, int n) {
        int idx = blockIdx.x * blockDim.x + threadIdx.x;
        if (idx < n) {
            output[idx] = input[idx] * 2.0f;
        }
    }
    """
    
    kernel = load_inline(
        name='custom_kernel',
        cuda_sources=[cuda_source],
        functions=['custom_kernel'],
        verbose=True
    )
    
    return kernel
```

## 📊 Monitoring and Debugging

### 1. **PyTorch Profiler**

```python
from torch.profiler import profile, record_function, ProfilerActivity

def profile_model(model, input_data):
    """Profile model performance."""
    with profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        record_shapes=True,
        with_stack=True,
        profile_memory=True
    ) as prof:
        with record_function("model_inference"):
            output = model(input_data)
    
    # Print profiling results
    print(prof.key_averages().table(sort_by="cuda_time_total"))
    
    # Export to Chrome trace
    prof.export_chrome_trace("trace.json")
```

### 2. **Memory Profiling**

```python
def memory_profiling_context():
    """Context manager for memory profiling."""
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()
    
    yield
    
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        cached = torch.cuda.memory_reserved() / 1024**3
        logger.info(f"Memory: {allocated:.2f}GB allocated, {cached:.2f}GB cached")

def log_memory_usage():
    """Log current memory usage."""
    if torch.cuda.is_available():
        memory_info = {
            'allocated': torch.cuda.memory_allocated() / 1024**3,
            'reserved': torch.cuda.memory_reserved() / 1024**3,
            'max_allocated': torch.cuda.max_memory_allocated() / 1024**3
        }
        logger.info("Memory usage", **memory_info)
```

## 🚀 Production Deployment

### 1. **Model Export and Optimization**

```python
def export_model_for_production(model, config):
    """Export model for production deployment."""
    # TorchScript export
    scripted_model = torch.jit.script(model)
    torch.jit.save(scripted_model, "model.pt")
    
    # ONNX export
    import torch.onnx
    dummy_input = torch.randn(1, config.max_length)
    torch.onnx.export(
        model,
        dummy_input,
        "model.onnx",
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # Quantization
    quantized_model = torch.quantization.quantize_dynamic(
        model, {nn.Linear}, dtype=torch.qint8
    )
    torch.save(quantized_model.state_dict(), "quantized_model.pt")
```

### 2. **Model Serving with TorchServe**

```python
# requirements.txt
torchserve
torch-model-archiver
torch-workflow-archiver

# Model archiving
torch-model-archiver --model-name mymodel \
    --version 1.0 \
    --model-file model.py \
    --serialized-file model.pt \
    --export-path model_store

# Start TorchServe
torchserve --start --model-store model_store --models mymodel
```

## 🧪 Testing and Validation

### 1. **Model Testing**

```python
import pytest
import torch

def test_model_forward():
    """Test model forward pass."""
    config = PyTorchConfig()
    model = OptimizedModel(config)
    
    # Test input
    input_data = torch.randint(0, 1000, (2, 10))
    
    # Test forward pass
    with torch.no_grad():
        output = model(input_data)
    
    assert output is not None
    assert output.shape[0] == 2

def test_model_gradients():
    """Test model gradient computation."""
    config = PyTorchConfig()
    model = OptimizedModel(config)
    
    input_data = torch.randint(0, 1000, (2, 10))
    output = model(input_data)
    loss = output.sum()
    loss.backward()
    
    # Check gradients
    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"Gradient missing for {name}"
```

### 2. **Performance Testing**

```python
def benchmark_model(model, input_data, num_runs=100):
    """Benchmark model performance."""
    model.eval()
    
    # Warmup
    with torch.no_grad():
        for _ in range(10):
            _ = model(input_data)
    
    # Benchmark
    torch.cuda.synchronize()
    start_time = time.time()
    
    with torch.no_grad():
        for _ in range(num_runs):
            _ = model(input_data)
    
    torch.cuda.synchronize()
    end_time = time.time()
    
    avg_time = (end_time - start_time) / num_runs
    logger.info(f"Average inference time: {avg_time*1000:.2f} ms")
    
    return avg_time
```

## 📈 Best Practices Summary

### **Do's:**
✅ Use `torch.no_grad()` for inference
✅ Enable mixed precision training with `GradScaler`
✅ Use proper weight initialization
✅ Implement gradient clipping
✅ Use `DataLoader` with `pin_memory=True`
✅ Enable gradient checkpointing for large models
✅ Use `torch.compile()` for PyTorch 2.0+
✅ Profile your models regularly
✅ Implement proper error handling
✅ Use structured logging

### **Don'ts:**
❌ Don't forget to call `optimizer.zero_grad()`
❌ Don't use `torch.no_grad()` during training
❌ Don't ignore memory management
❌ Don't use deprecated PyTorch APIs
❌ Don't forget to validate model outputs
❌ Don't ignore gradient explosion/vanishing
❌ Don't use hardcoded device assignments

## 🔗 Additional Resources

- [PyTorch Official Documentation](https://pytorch.org/docs/)
- [PyTorch Performance Tuning Guide](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)
- [PyTorch Memory Management](https://pytorch.org/docs/stable/notes/cuda.html#memory-management)
- [PyTorch Profiler](https://pytorch.org/tutorials/intermediate/torch_profiler_tutorial.html)
- [PyTorch Distributed Training](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)

## 🎯 Implementation Checklist

- [ ] Configure PyTorch environment with best practices
- [ ] Implement proper model architecture with weight initialization
- [ ] Enable mixed precision training
- [ ] Implement gradient accumulation and clipping
- [ ] Add memory optimization features
- [ ] Implement comprehensive logging and monitoring
- [ ] Add model validation and testing
- [ ] Implement checkpoint saving/loading
- [ ] Add performance profiling
- [ ] Prepare for production deployment

This guide provides a comprehensive foundation for using PyTorch as your primary deep learning framework with production-ready best practices.

