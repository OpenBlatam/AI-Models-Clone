# 🚀 Blaze AI Engine System

A high-performance, production-ready AI engine system featuring LLM, Diffusion, and Router engines with advanced capabilities including circuit breakers, load balancing, intelligent caching, and comprehensive monitoring.

## ✨ Features

### 🧠 **LLM Engine**
- **Advanced Model Management**: Automatic device detection, PyTorch 2.0+ compilation, mixed precision
- **Intelligent Caching**: LRU cache with TTL, compression, and memory management
- **Dynamic Batching**: Adaptive batch processing for optimal throughput
- **Quantization Support**: 4-bit and 8-bit quantization for reduced memory usage
- **Multiple Model Types**: Support for causal LM, seq2seq, and encoder models

### 🎨 **Diffusion Engine**
- **Multiple Pipelines**: Text-to-image, image-to-image, and inpainting
- **Memory Optimization**: Attention slicing, VAE slicing, CPU offloading
- **Scheduler Factory**: Support for DPM, Euler, DDIM, LMS, and more
- **Advanced Features**: xFormers integration, model compilation, safety checker
- **Flexible Output**: Customizable dimensions, batch generation, seed control

### 🛣️ **Router Engine**
- **Intelligent Load Balancing**: Multiple strategies (round-robin, least connections, adaptive)
- **Advanced Caching**: TTL-based caching with compression and intelligent eviction
- **Request Batching**: Dynamic batching for optimal throughput
- **Health Monitoring**: Real-time health checks and circuit breaker integration
- **Adaptive Routing**: Performance-based routing decisions

### 🏗️ **System Architecture**
- **Circuit Breaker Pattern**: Automatic failure detection and recovery
- **Async-First Design**: High-performance asynchronous operations
- **Comprehensive Monitoring**: Real-time metrics, health checks, and alerting
- **Structured Logging**: JSON and structured logging with performance tracking
- **Configuration Management**: Centralized configuration with validation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for optimal performance)
- 8GB+ RAM
- 10GB+ free disk space

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd blaze-ai
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
# Install core dependencies
pip install -r requirements.txt

# Install with optional features
pip install -r requirements.txt[full]

# Install development dependencies
pip install -r requirements.txt[dev]
```

4. **Verify installation**
```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
```

### Basic Usage

```python
import asyncio
from engines import get_engine_manager
from core.interfaces import create_development_config

async def main():
    # Initialize the system
    config = create_development_config()
    engine_manager = get_engine_manager(config)
    
    # Wait for engines to initialize
    await asyncio.sleep(5)
    
    # Generate text with LLM
    result = await engine_manager.dispatch("llm", "generate", {
        "prompt": "Explain quantum computing in simple terms:",
        "max_length": 100,
        "temperature": 0.7
    })
    
    print(f"Generated text: {result.text}")
    
    # Generate image with Diffusion
    image_result = await engine_manager.dispatch("diffusion", "generate", {
        "prompt": "A futuristic city skyline at sunset",
        "width": 512,
        "height": 512
    })
    
    print(f"Generated {len(image_result.images)} image(s)")
    
    # Cleanup
    await engine_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Blaze AI System                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   LLM       │  │ Diffusion   │  │   Router    │        │
│  │  Engine     │  │   Engine    │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                 Engine Manager                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Circuit   │  │   Load      │  │   Health    │        │
│  │  Breaker    │  │ Balancing   │  │  Monitor    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                 Core Infrastructure                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Config    │  │  Logging    │  │  Monitoring │        │
│  │ Management  │  │   System    │  │   System    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Engine Architecture

Each engine follows a consistent architecture pattern:

1. **Configuration Layer**: Engine-specific configuration with validation
2. **Core Engine**: Main processing logic and model management
3. **Cache Layer**: Intelligent caching with LRU eviction
4. **Performance Layer**: Optimization, batching, and monitoring
5. **Interface Layer**: Standardized operation interface

## 📚 API Reference

### Engine Manager

The central orchestrator for all engines:

```python
class EngineManager:
    async def dispatch(engine_name: str, operation: str, params: Dict) -> Any
    async def dispatch_batch(requests: List[Dict]) -> List[Any]
    def get_engine_status() -> Dict[str, Any]
    def get_system_metrics() -> Dict[str, Any]
    async def shutdown()
```

### LLM Engine Operations

```python
# Text generation
await engine_manager.dispatch("llm", "generate", {
    "prompt": "Your prompt here",
    "max_length": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50
})

# Batch generation
await engine_manager.dispatch("llm", "generate_batch", {
    "prompts": ["Prompt 1", "Prompt 2"],
    "max_length": 80
})

# Embedding generation
await engine_manager.dispatch("llm", "embed", {
    "text": "Text to embed"
})
```

### Diffusion Engine Operations

```python
# Image generation
await engine_manager.dispatch("diffusion", "generate", {
    "prompt": "A beautiful landscape",
    "width": 512,
    "height": 512,
    "num_images": 1,
    "guidance_scale": 7.5
})

# Image-to-image
await engine_manager.dispatch("diffusion", "img2img", {
    "prompt": "Enhanced version",
    "init_image": image,
    "strength": 0.75
})

# Inpainting
await engine_manager.dispatch("diffusion", "inpaint", {
    "prompt": "Fill the masked area",
    "init_image": image,
    "mask_image": mask
})
```

### Router Engine Operations

```python
# Route single request
await engine_manager.dispatch("router", "route", {
    "operation": "generate",
    "params": {"prompt": "Hello"},
    "engine_preference": "llm"
})

# Route batch requests
await engine_manager.dispatch("router", "route_batch", {
    "requests": [request1, request2]
})

# Get metrics
await engine_manager.dispatch("router", "get_metrics", {})
```

## ⚙️ Configuration

### Core Configuration

```python
from core.interfaces import CoreConfig

config = CoreConfig(
    system_name="Blaze AI",
    environment="production",
    max_concurrent_requests=100,
    enable_health_checks=True,
    health_check_interval=30.0
)
```

### Engine-Specific Configuration

```python
# LLM Engine
llm_config = {
    "model_name": "gpt2",
    "device": "auto",
    "precision": "float16",
    "enable_amp": True,
    "cache_capacity": 1000,
    "enable_quantization": False
}

# Diffusion Engine
diffusion_config = {
    "model_id": "runwayml/stable-diffusion-v1-5",
    "enable_xformers": True,
    "enable_attention_slicing": True,
    "enable_vae_slicing": True
}

# Router Engine
router_config = {
    "load_balancing_strategy": "adaptive",
    "enable_caching": True,
    "cache_ttl": 1800,
    "enable_health_checks": True
}
```

### Environment Variables

```bash
# System configuration
BLAZE_AI_ENVIRONMENT=production
BLAZE_AI_LOG_LEVEL=INFO
BLAZE_AI_MAX_CONCURRENT_REQUESTS=100

# Model configuration
BLAZE_AI_LLM_MODEL_NAME=gpt2
BLAZE_AI_DIFFUSION_MODEL_ID=runwayml/stable-diffusion-v1-5

# Performance configuration
BLAZE_AI_ENABLE_AMP=true
BLAZE_AI_ENABLE_QUANTIZATION=false
```

## 📊 Monitoring and Observability

### Health Checks

```python
# Get system health
health_status = engine_manager.system_health.get_health_summary()
print(f"Overall status: {health_status['overall_status']}")
print(f"Healthy components: {health_status['healthy_components']}")
```

### Metrics Collection

```python
# Get system metrics
system_metrics = engine_manager.get_system_metrics()
print(f"Total requests: {system_metrics['total_requests']}")
print(f"Success rate: {system_metrics['success_rate']:.2%}")

# Get engine-specific metrics
engine_status = engine_manager.get_engine_status()
for engine_name, status in engine_status.items():
    print(f"{engine_name}: {status['metrics']}")
```

### Performance Monitoring

```python
from utils.logging import get_performance_logger

performance_logger = get_performance_logger()

# Monitor operation performance
with performance_logger.log_operation("custom_operation", context="test"):
    # Your operation here
    result = await some_operation()
    
# Get performance statistics
stats = performance_logger.get_performance_stats()
print(f"Average duration: {stats['average_duration']:.3f}s")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_llm_engine.py
pytest tests/test_diffusion_engine.py
pytest tests/test_router_engine.py

# Run with coverage
pytest --cov=engines --cov=core --cov=utils

# Run performance tests
pytest tests/test_performance.py
```

### Test Structure

```
tests/
├── test_llm_engine.py          # LLM engine tests
├── test_diffusion_engine.py    # Diffusion engine tests
├── test_router_engine.py       # Router engine tests
├── test_core_interfaces.py     # Core interface tests
├── test_utils.py               # Utility tests
├── test_integration.py         # Integration tests
└── test_performance.py         # Performance tests
```

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
```bash
export BLAZE_AI_ENVIRONMENT=production
export BLAZE_AI_LOG_LEVEL=WARNING
export BLAZE_AI_MAX_CONCURRENT_REQUESTS=500
```

2. **Docker Deployment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt[full]

COPY . .
CMD ["python", "demo_advanced_system.py"]
```

3. **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blaze-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: blaze-ai
  template:
    metadata:
      labels:
        app: blaze-ai
    spec:
      containers:
      - name: blaze-ai
        image: blaze-ai:latest
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```

### Performance Tuning

1. **Memory Optimization**
```python
# Enable memory optimizations
config.enable_memory_optimization = True
config.enable_model_cpu_offload = True
config.enable_sequential_cpu_offload = True
```

2. **GPU Optimization**
```python
# Enable GPU optimizations
config.enable_amp = True
config.enable_xformers = True
config.enable_compiled_attention = True
```

3. **Caching Optimization**
```python
# Optimize caching
config.cache_capacity = 10000
config.enable_compression = True
config.enable_log_rotation = True
```

## 🔧 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size
   - Enable attention slicing
   - Use model CPU offloading
   - Enable quantization

2. **Slow Performance**
   - Check GPU utilization
   - Enable PyTorch compilation
   - Optimize cache settings
   - Use appropriate precision

3. **Engine Initialization Failures**
   - Verify model paths
   - Check disk space
   - Validate configuration
   - Review error logs

### Debug Mode

```python
# Enable debug mode
config.debug_mode = True
config.log_level = "DEBUG"

# Enable profiling
config.enable_profiling = True
```

### Log Analysis

```python
from utils.logging import get_log_manager

log_manager = get_log_manager()
logger_stats = log_manager.get_logger_stats()
print(f"Logger statistics: {logger_stats}")
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Install development dependencies**
```bash
pip install -r requirements.txt[dev]
```

4. **Run pre-commit hooks**
```bash
pre-commit install
pre-commit run --all-files
```

5. **Write tests**
```bash
pytest tests/ --cov=engines --cov=core --cov=utils
```

6. **Submit pull request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive docstrings
- Maintain test coverage above 90%
- Use async/await for I/O operations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyTorch Team** for the excellent deep learning framework
- **Hugging Face** for the transformers and diffusers libraries
- **OpenAI** for the GPT models and research
- **Stability AI** for the Stable Diffusion models

## 📞 Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@blaze-ai.com

---

**Made with ❤️ by the Blaze AI Team**
