# TruthGPT Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you get started with TruthGPT specifications quickly.

## Prerequisites

- Python 3.10+
- PyTorch 2.0+
- CUDA 11.8+ (for GPU support)

## Installation

```bash
# Clone the repository
git clone https://github.com/truthgpt/truthgpt-spec.git
cd truthgpt-spec

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Examples

### Example 1: Basic Model Creation

```python
from truthgpt import OptimizedModel, Config

# Load configuration
config = Config.from_yaml("specs/config.yaml")

# Create optimized model
model = OptimizedModel(
    config=config,
    optimization_level=5
)

# Run inference
output = model.generate("Hello, world!")
print(output)
```

### Example 2: Hyper-Speed Processing

```python
from truthgpt import LightningProcessor

# Create lightning processor
processor = LightningProcessor()

# Process with microsecond precision
result = processor.process(
    data=input_data,
    precision="microsecond"
)

print(f"Processed in {result['latency']}s")
```

### Example 3: Mixed Precision Training

```python
from truthgpt import TrainingPipeline

# Create training pipeline
pipeline = TrainingPipeline(
    model=model,
    training_data=data_loader,
    optimization_config={
        "mixed_precision": True,
        "gradient_checkpointing": True,
        "dynamic_batching": True
    }
)

# Train model
history = pipeline.train(epochs=10)
```

## Common Use Cases

### 1. Basic Inference

```python
from truthgpt import TruthGPTClient

# Initialize client
client = TruthGPTClient(
    api_key="your-api-key",
    endpoint="https://api.truthgpt.ai/v1"
)

# Run inference
response = client.inference(
    prompt="What is TruthGPT?",
    max_tokens=100,
    temperature=0.7
)

print(response['output'])
```

### 2. Batch Processing

```python
from truthgpt import BatchProcessor

# Create batch processor
processor = BatchProcessor(
    batch_size=32,
    max_wait_time=1.0
)

# Process batch
inputs = [f"Input {i}" for i in range(100)]
outputs = processor.process_batch(inputs)

print(f"Processed {len(outputs)} items")
```

### 3. Production Deployment

```bash
# Docker deployment
docker build -t truthgpt .
docker run -p 8000:8000 truthgpt

# Kubernetes deployment
kubectl apply -f specs/deployment/kubernetes/

# Verify deployment
curl http://localhost:8000/health
```

## Next Steps

1. **Read the Documentation**: Start with `docs/design-rationale.md`
2. **Explore Examples**: Check out `examples/basic_usage.py`
3. **Review Specifications**: Browse `specs/` directory
4. **Join the Community**: Visit our Discord server

## Getting Help

- 📚 [Documentation](https://docs.truthgpt.ai)
- 💬 [Discord](https://discord.gg/truthgpt)
- 🐛 [Issues](https://github.com/truthgpt/truthgpt-spec/issues)
- 📧 [Email](mailto:support@truthgpt.ai)

## Quick Reference

### Configuration Files

- `specs/config.yaml` - Global configuration
- `specs/deployment/docker-compose.yml` - Docker setup
- `specs/deployment/kubernetes/` - Kubernetes manifests

### Key Directories

- `specs/phase0/` - Core specifications
- `specs/api/` - API specifications
- `specs/deployment/` - Deployment guides
- `docs/` - Documentation
- `examples/` - Code examples

### Important Files

- `README.md` - Project overview
- `INDEX.md` - Specification index
- `METRICS.md` - Performance metrics
- `QUICKSTART.md` - This file

---

*Happy coding with TruthGPT! 🎉*



