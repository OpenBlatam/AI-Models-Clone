# Ultra-Optimized Copywriting System

## 🚀 Overview

This is a high-performance copywriting generation system with advanced optimizations, modular architecture, and enterprise-grade features. The system provides AI-powered copywriting generation with real-time optimization, intelligent caching, and comprehensive monitoring.

## 📁 Project Structure

```
copywriting/
├── core/                          # Core system components
│   ├── __init__.py               # Core module exports
│   ├── engine.py                 # Main processing engine
│   ├── models.py                 # Data models and schemas
│   └── services.py               # Business logic services
├── config/                       # Configuration management
│   └── optimized_config.py       # Advanced configuration system
├── versions/                     # Different system versions
│   ├── production/              # Production-ready versions
│   ├── development/             # Development versions
│   └── experimental/            # Experimental features
├── docs/                        # Documentation
│   ├── README.md               # This file
│   ├── API.md                  # API documentation
│   └── DEPLOYMENT.md           # Deployment guide
├── scripts/                     # Utility scripts
│   ├── run_production.py       # Production runner
│   ├── run_development.py      # Development runner
│   └── benchmark.py            # Performance benchmarks
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── examples/                    # Usage examples
├── main.py                      # Main application entry point
└── requirements.txt             # Dependencies
```

## 🏗️ Architecture

### Core Components

1. **CopywritingEngine** (`core/engine.py`)
   - Main processing engine with async capabilities
   - GPU acceleration for ML models
   - Intelligent caching with Redis
   - Batch processing for high throughput
   - Real-time optimization

2. **Data Models** (`core/models.py`)
   - Pydantic-based validation
   - Performance metrics collection
   - Type-safe data structures
   - Serialization optimization

3. **Services** (`core/services.py`)
   - CopywritingService: Core generation logic
   - OptimizationService: Text enhancement
   - CacheService: Intelligent caching

4. **Configuration** (`config/optimized_config.py`)
   - Environment-based settings
   - Performance tuning
   - Security configuration
   - Monitoring setup

## 🚀 Features

### Performance Optimizations
- **Async Processing**: Full async/await support for high concurrency
- **GPU Acceleration**: CUDA support for ML model inference
- **Intelligent Caching**: Redis-based caching with TTL and LRU eviction
- **Batch Processing**: Efficient batch operations for multiple requests
- **Memory Optimization**: Automatic garbage collection and memory management
- **Connection Pooling**: Optimized database and Redis connections

### Advanced Features
- **Real-time Optimization**: Dynamic text optimization based on platform and tone
- **Multi-platform Support**: Instagram, Facebook, Twitter, LinkedIn, Email, Website, Ads, Blog
- **A/B Testing**: Generate multiple variants for testing
- **Sentiment Analysis**: TextBlob integration for sentiment optimization
- **Performance Monitoring**: Prometheus metrics and health checks
- **Rate Limiting**: Configurable rate limiting for API protection

### Security Features
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Protection against abuse
- **CORS Support**: Configurable cross-origin requests
- **Error Handling**: Graceful error handling and logging

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Redis server
- CUDA-compatible GPU (optional, for acceleration)

### Quick Start

1. **Clone and navigate to the project**
```bash
cd agents/backend/onyx/server/features/copywriting
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export ENVIRONMENT=development
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=your-secret-key-here
```

4. **Run the application**
```bash
python main.py
```

## 📖 Usage

### Basic API Usage

#### Generate Copywriting
```python
import requests

# Single request
response = requests.post("http://localhost:8000/api/v1/copywriting/generate", json={
    "product_description": "Premium wireless headphones with noise cancellation",
    "target_platform": "instagram",
    "tone": "inspirational",
    "language": "en",
    "max_variants": 5,
    "call_to_action": "Shop now!"
})

print(response.json())
```

#### Batch Generation
```python
# Multiple requests
requests_data = [
    {
        "product_description": "Product 1",
        "target_platform": "instagram",
        "tone": "professional"
    },
    {
        "product_description": "Product 2", 
        "target_platform": "facebook",
        "tone": "casual"
    }
]

response = requests.post("http://localhost:8000/api/v1/copywriting/batch-generate", 
                        json=requests_data)
```

#### Optimize Existing Text
```python
response = requests.post("http://localhost:8000/api/v1/copywriting/optimize", json={
    "text": "Check out our amazing product!",
    "platform": "instagram",
    "tone": "inspirational"
})
```

### Programmatic Usage

```python
from core.engine import CopywritingEngine, EngineConfig
from core.models import CopywritingRequest

# Initialize engine
config = EngineConfig(
    max_workers=4,
    enable_gpu=True,
    enable_caching=True
)
engine = CopywritingEngine(config)
await engine.initialize()

# Create request
request = CopywritingRequest(
    product_description="Luxury smartwatch with health monitoring",
    target_platform="instagram",
    tone="inspirational",
    max_variants=3
)

# Generate copywriting
response = await engine.process_request(request)

# Access results
for variant in response.variants:
    print(f"Content: {variant.content}")
    print(f"Score: {variant.overall_score}")
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/production) | development |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `DATABASE_URL` | Database connection URL | postgresql://localhost/copywriting |
| `SECRET_KEY` | Security secret key | your-secret-key-here |
| `DEFAULT_MODEL` | Default ML model | gpt2 |
| `ENABLE_GPU` | Enable GPU acceleration | true |
| `MAX_WORKERS` | Maximum worker threads | 4 |
| `CACHE_TTL` | Cache time-to-live (seconds) | 3600 |

### Configuration File

Create `config.json` for custom configuration:

```json
{
  "development": {
    "database": {
      "url": "postgresql://localhost/copywriting_dev",
      "pool_size": 10
    },
    "redis": {
      "url": "redis://localhost:6379",
      "pool_size": 5
    },
    "model": {
      "default_model": "gpt2",
      "enable_gpu": true,
      "max_tokens": 512
    },
    "performance": {
      "max_workers": 4,
      "enable_caching": true,
      "cache_ttl": 3600
    }
  }
}
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=core --cov-report=html
```

### Performance Benchmarks
```bash
python scripts/benchmark.py
```

## 📊 Monitoring

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed
```

### Metrics
```bash
# Get system metrics
curl http://localhost:8000/api/v1/copywriting/metrics

# Prometheus metrics (if enabled)
curl http://localhost:8000/metrics
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚀 Deployment

### Production Deployment

1. **Docker Deployment**
```bash
# Build image
docker build -t copywriting-system .

# Run container
docker run -p 8000:8000 copywriting-system
```

2. **Kubernetes Deployment**
```bash
kubectl apply -f deployment/k8s/
```

3. **Environment Setup**
```bash
export ENVIRONMENT=production
export REDIS_URL=redis://your-redis-server:6379
export DATABASE_URL=postgresql://your-db-server/copywriting
export SECRET_KEY=your-production-secret-key
```

### Performance Tuning

1. **GPU Acceleration**
```bash
export CUDA_VISIBLE_DEVICES=0
export ENABLE_GPU=true
```

2. **Caching Optimization**
```bash
export REDIS_URL=redis://your-redis-cluster:6379
export CACHE_TTL=7200
```

3. **Worker Configuration**
```bash
export MAX_WORKERS=8
export MAX_BATCH_SIZE=64
```

## 🔧 Development

### Adding New Features

1. **Create new service**
```python
# core/services/new_service.py
class NewService:
    async def initialize(self):
        pass
    
    async def process(self, data):
        pass
```

2. **Add to engine**
```python
# core/engine.py
self.new_service = NewService()
await self.new_service.initialize()
```

3. **Add API endpoint**
```python
# main.py
@app.post("/api/v1/new-feature")
async def new_feature(request: NewRequest):
    return await engine.new_service.process(request)
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings for all functions
- Write unit tests for new features
- Update documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API docs at `/docs`

## 🔄 Version History

- **v2.0.0**: Complete refactor with ultra-optimizations
- **v1.5.0**: Added batch processing and caching
- **v1.0.0**: Initial release with basic features

---

**Built with ❤️ for high-performance copywriting generation** 