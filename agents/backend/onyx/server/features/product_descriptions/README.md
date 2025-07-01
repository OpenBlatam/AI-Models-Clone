# 🛍️ AI Product Description Generator

Advanced AI-powered product description generator using state-of-the-art transformer models and deep learning techniques.

## 🌟 Features

- **🧠 Advanced AI Models**: Uses transformer-based language models for high-quality text generation
- **🎨 Customizable Styles**: Professional, casual, luxury, technical, and creative writing styles
- **🎯 Tone Control**: Friendly, formal, enthusiastic, informative, and persuasive tones
- **🚀 High Performance**: Optimized with mixed precision training and async processing
- **📊 SEO Optimization**: Built-in SEO scoring and keyword optimization
- **🔄 Batch Processing**: Generate descriptions for multiple products simultaneously
- **💾 Smart Caching**: Intelligent caching system for improved performance
- **🌐 REST API**: FastAPI-based web service with comprehensive endpoints
- **🎮 Interactive Interface**: Gradio-based web interface for easy testing
- **📈 Analytics**: Built-in performance tracking and quality metrics

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from product_descriptions import ProductDescriptionGenerator, ProductDescriptionConfig

# Initialize generator
config = ProductDescriptionConfig()
generator = ProductDescriptionGenerator(config)
await generator.initialize()

# Generate description
results = generator.generate(
    product_name="Wireless Bluetooth Headphones",
    features=["noise cancellation", "30-hour battery", "premium leather"],
    category="electronics",
    brand="TechPro",
    style="professional",
    tone="friendly"
)

print(results[0]["description"])
```

### API Service

```python
from product_descriptions.api import ProductDescriptionService

# Start service
service = ProductDescriptionService()
service.run(host="0.0.0.0", port=8000)
```

### Gradio Interface

```python
from product_descriptions.api import create_gradio_app

# Launch interactive interface
app = create_gradio_app()
app.launch(share=True)
```

## 📚 API Documentation

### REST Endpoints

- `POST /generate` - Generate single product description
- `POST /generate/batch` - Generate multiple descriptions
- `POST /generate/preset` - Generate using presets
- `GET /health` - Health check
- `GET /stats` - Service statistics
- `GET /presets` - Available presets

### Example API Request

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "product_name": "Smart Watch",
       "features": ["heart rate monitor", "GPS", "waterproof"],
       "category": "electronics",
       "style": "professional",
       "tone": "enthusiastic"
     }'
```

## ⚙️ Configuration

### Model Configuration

```python
from product_descriptions import ModelConfig

config = ModelConfig(
    model_name="microsoft/DialoGPT-medium",
    max_length=512,
    temperature=0.7,
    device="cuda"  # or "cpu"
)
```

### Generation Presets

- **ecommerce**: Standard e-commerce descriptions
- **luxury**: High-end luxury products
- **technical**: Detailed technical specifications

## 🏗️ Architecture

```
product_descriptions/
├── core/
│   ├── model.py          # Transformer model with enhancements
│   ├── generator.py      # High-level generation orchestrator
│   └── config.py         # Configuration classes
├── api/
│   ├── service.py        # FastAPI web service
│   └── gradio_interface.py # Interactive Gradio interface
├── tests/
│   └── test_*.py         # Unit and integration tests
└── requirements.txt      # Dependencies
```

## 🔬 Technical Details

### Model Architecture

- **Base Model**: Pre-trained transformer (GPT-style)
- **Custom Layers**: Product context encoder, style/tone embeddings
- **Quality Scoring**: Neural network-based quality assessment
- **SEO Optimization**: Automatic keyword density and structure analysis

### Performance Optimizations

- **Mixed Precision Training**: FP16 for faster training
- **Gradient Accumulation**: Handle large batch sizes
- **Async Processing**: Non-blocking generation
- **Intelligent Caching**: LRU cache with configurable size
- **Batch Processing**: Concurrent generation for multiple products

### Generation Parameters

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| temperature | Creativity level | 0.1-2.0 | 0.7 |
| max_length | Maximum tokens | 50-1000 | 300 |
| top_p | Nucleus sampling | 0.1-1.0 | 0.9 |
| top_k | Top-k sampling | 1-100 | 50 |

## 📊 Quality Metrics

- **Quality Score**: Readability, structure, and coherence (0-1)
- **SEO Score**: Keyword optimization and meta description quality (0-1)
- **Word Count**: Number of words in generated description
- **Generation Time**: Processing time in milliseconds

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=product_descriptions

# Run specific test
pytest tests/test_generator.py::test_generate_description
```

## 🐳 Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "product_descriptions.api.service:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Performance Benchmarks

| Metric | Value | Condition |
|--------|-------|-----------|
| Generation Speed | ~2-5 seconds | Single description, GPU |
| Throughput | 50-100 desc/min | Batch processing |
| Cache Hit Rate | 85-95% | After warm-up |
| Memory Usage | 2-4 GB | GPU inference |

## 🛠️ Development

### Setup Development Environment

```bash
git clone <repository>
cd product_descriptions
pip install -r requirements.txt
pip install -e .
```

### Code Style

```bash
black product_descriptions/
flake8 product_descriptions/
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Run tests and linting
5. Submit pull request

## 📞 Support

- Documentation: `/docs` endpoint when service is running
- Issues: GitHub Issues
- Email: support@blatam-academy.com

---

Built with ❤️ by Blatam Academy using PyTorch, Transformers, and FastAPI. 