# NotebookLM AI - Advanced Document Intelligence System

Inspired by Google's NotebookLM, this system provides advanced document intelligence with AI-powered analysis, citation generation, and multi-modal processing.

## 🚀 Features

### Core Capabilities
- **Advanced Document Processing**: NLP analysis, entity extraction, sentiment analysis
- **AI-Powered Response Generation**: Context-aware responses with citations
- **Citation Generation**: Multiple formats (APA, MLA, Chicago, Harvard, IEEE)
- **Multi-Modal Processing**: Text, image, and audio content analysis
- **Notebook Workflow**: Complete document management and conversation tracking
- **Performance Optimization**: GPU acceleration, quantization, and caching

### AI Engines
- **Advanced LLM Engine**: Latest transformer models with optimizations
- **Document Processor**: Comprehensive text analysis and insights
- **Citation Generator**: Automated citation creation and bibliography
- **Response Optimizer**: Quality assessment and improvement
- **Multi-Modal Processor**: Cross-modal content understanding

## 📁 Project Structure

```
notebooklm_ai/
├── core/                    # Domain entities and business logic
│   ├── entities.py         # Core domain models
│   ├── value_objects.py    # Value objects and identifiers
│   └── repositories.py     # Repository interfaces
├── application/            # Application use cases
│   └── use_cases.py       # Business logic implementation
├── infrastructure/         # External services and implementations
│   ├── ai_engines.py      # AI engine implementations
│   ├── database.py        # Database implementations
│   └── external_apis.py   # External API integrations
├── presentation/           # API and user interface
│   ├── api.py             # FastAPI router
│   └── schemas.py         # Pydantic schemas
├── shared/                # Shared utilities and configuration
│   ├── config.py          # Configuration management
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures.py        # Test fixtures
├── docs/                  # Documentation
├── requirements_notebooklm.txt  # Dependencies
├── demo_notebooklm.py     # Comprehensive demo
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- CUDA-compatible GPU (optional, for acceleration)
- 8GB+ RAM recommended

### Quick Start

1. **Clone and navigate to the project:**
```bash
cd agents/backend/onyx/server/features/notebooklm_ai
```

2. **Install dependencies:**
```bash
pip install -r requirements_notebooklm.txt
```

3. **Install spaCy model:**
```bash
python -m spacy download en_core_web_sm
```

4. **Run the demo:**
```bash
python demo_notebooklm.py
```

## 🎯 Usage Examples

### Basic Document Processing

```python
from infrastructure.ai_engines import DocumentProcessor

# Initialize processor
processor = DocumentProcessor()

# Process document
analysis = processor.process_document(
    content="Your document content here...",
    title="Document Title"
)

print(f"Word count: {analysis['word_count']}")
print(f"Sentiment: {analysis['sentiment']}")
print(f"Key points: {analysis['key_points']}")
```

### AI Response Generation

```python
from infrastructure.ai_engines import AdvancedLLMEngine, AIEngineConfig

# Initialize LLM engine
config = AIEngineConfig(
    model_name="microsoft/DialoGPT-medium",
    temperature=0.7
)
engine = AdvancedLLMEngine(config)

# Generate response
response = await engine.generate_response(
    prompt="What is artificial intelligence?",
    context="AI is a branch of computer science..."
)
print(response)
```

### Citation Generation

```python
from infrastructure.ai_engines import CitationGenerator

# Initialize citation generator
generator = CitationGenerator()

# Generate citation
source = {
    "title": "Attention Is All You Need",
    "authors": ["Vaswani, A.", "Shazeer, N."],
    "publication_date": "2017-06-12",
    "publisher": "NeurIPS"
}

citation = generator.generate_citation(source, format="apa")
print(citation)
```

### Complete Notebook Workflow

```python
from core.entities import Notebook, Document, User, DocumentType

# Create user and notebook
user = User(
    id=UserId(),
    username="researcher",
    email="researcher@example.com"
)

notebook = Notebook(
    id=NotebookId(),
    title="Research Notebook",
    user_id=user.id
)

# Add document
document = Document(
    id=DocumentId(),
    title="Research Paper",
    content="Your research content...",
    document_type=DocumentType.PDF
)

notebook.add_document(document)
```

## 🔧 Configuration

### AI Engine Configuration

```python
from infrastructure.ai_engines import AIEngineConfig

config = AIEngineConfig(
    model_name="microsoft/DialoGPT-medium",  # Model to use
    max_length=2048,                         # Maximum sequence length
    temperature=0.7,                         # Generation temperature
    top_p=0.9,                              # Nucleus sampling
    top_k=50,                               # Top-k sampling
    use_quantization=True,                  # Enable quantization
    use_flash_attention=True,               # Enable flash attention
    device="auto",                          # Device selection
    batch_size=4,                           # Batch size
    max_workers=4                           # Parallel workers
)
```

### Environment Variables

```bash
# AI Model Configuration
NOTEBOOKLM_MODEL_NAME=microsoft/DialoGPT-medium
NOTEBOOKLM_MAX_LENGTH=2048
NOTEBOOKLM_TEMPERATURE=0.7

# Database Configuration
NOTEBOOKLM_DB_URL=postgresql://user:pass@localhost/notebooklm
NOTEBOOKLM_REDIS_URL=redis://localhost:6379

# API Configuration
NOTEBOOKLM_API_HOST=0.0.0.0
NOTEBOOKLM_API_PORT=8000
NOTEBOOKLM_API_WORKERS=4

# Security
NOTEBOOKLM_SECRET_KEY=your-secret-key
NOTEBOOKLM_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📊 Performance Optimization

### GPU Acceleration

The system automatically detects and uses CUDA GPUs when available:

```python
# Check GPU availability
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
print(f"Current device: {torch.cuda.current_device()}")
```

### Quantization

Enable 4-bit quantization for memory efficiency:

```python
config = AIEngineConfig(
    use_quantization=True,  # Enable 4-bit quantization
    device="cuda"
)
```

### Batch Processing

Process multiple documents efficiently:

```python
# Batch document processing
documents = ["doc1", "doc2", "doc3"]
results = processor.batch_process_documents(documents)
```

## 🧪 Testing

### Run All Tests

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest --cov=notebooklm_ai --cov-report=html
```

### Performance Testing

```bash
# Run performance benchmarks
python -m pytest tests/performance/ -v

# Load testing
python tests/load_test.py
```

## 📈 Monitoring and Logging

### Structured Logging

```python
import logging
from shared.utils import setup_logging

# Setup structured logging
logger = setup_logging()

# Log with context
logger.info("Processing document", extra={
    "document_id": doc.id.value,
    "user_id": user.id.value,
    "processing_time": 1.23
})
```

### Metrics Collection

```python
from shared.metrics import MetricsCollector

# Initialize metrics
metrics = MetricsCollector()

# Record metrics
metrics.record_processing_time("document_analysis", 1.23)
metrics.record_accuracy("entity_extraction", 0.85)
```

## 🔒 Security

### Authentication and Authorization

```python
from shared.security import SecurityManager

# Initialize security
security = SecurityManager()

# Verify token
user = security.verify_token(token)

# Check permissions
if security.has_permission(user, "read_document", document_id):
    # Access granted
    pass
```

### Data Encryption

```python
from shared.encryption import EncryptionManager

# Initialize encryption
encryption = EncryptionManager()

# Encrypt sensitive data
encrypted_data = encryption.encrypt(sensitive_data)

# Decrypt data
decrypted_data = encryption.decrypt(encrypted_data)
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_notebooklm.txt .
RUN pip install -r requirements_notebooklm.txt

COPY . .
CMD ["python", "demo_notebooklm.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notebooklm-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: notebooklm-ai
  template:
    metadata:
      labels:
        app: notebooklm-ai
    spec:
      containers:
      - name: notebooklm-ai
        image: notebooklm-ai:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Install development dependencies:**
   ```bash
   pip install -r requirements_dev.txt
   ```
4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```
5. **Submit a pull request**

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Maintain test coverage above 80%

## 📚 Documentation

- [API Reference](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Performance Guide](docs/performance.md)
- [Security Guide](docs/security.md)
- [Deployment Guide](docs/deployment.md)

## 🆘 Support

### Common Issues

1. **CUDA out of memory:**
   - Reduce batch size
   - Enable quantization
   - Use smaller models

2. **Slow processing:**
   - Enable GPU acceleration
   - Increase batch size
   - Use optimized models

3. **Import errors:**
   - Check Python version (3.9+)
   - Install all dependencies
   - Verify spaCy model installation

### Getting Help

- Create an issue on GitHub
- Check the documentation
- Review the demo examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Google's NotebookLM
- Built with Hugging Face Transformers
- Powered by PyTorch and spaCy
- Enhanced with modern AI libraries

---

**NotebookLM AI** - Advanced Document Intelligence for the Modern Age 🚀 