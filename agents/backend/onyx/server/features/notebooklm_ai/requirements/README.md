# NotebookLM AI - Requirements Management

This directory contains modular requirements files for the NotebookLM AI system, organized by functionality and deployment environment.

## 📁 File Structure

```
requirements/
├── README.md                    # This file
├── base.txt                     # Core utilities and common dependencies
├── ai-ml.txt                    # AI/ML and machine learning dependencies
├── document-processing.txt      # Document parsing and processing
├── web-api.txt                  # FastAPI and web framework dependencies
├── multimedia.txt               # Image, audio, and video processing
├── cloud-deployment.txt         # Cloud services and deployment
├── development.txt              # Testing and development tools
├── requirements.txt             # Complete system (all dependencies)
├── production.txt               # Production deployment (no dev tools)
└── minimal.txt                  # Minimal setup for basic functionality
```

## 🚀 Installation Options

### Complete Installation
Install all dependencies for full NotebookLM AI functionality:
```bash
pip install -r requirements/requirements.txt
```

### Production Installation
Install only production dependencies (excludes development tools):
```bash
pip install -r requirements/production.txt
```

### Minimal Installation
Install only essential dependencies for basic functionality:
```bash
pip install -r requirements/minimal.txt
```

### Modular Installation
Install specific functionality modules:

```bash
# Core utilities only
pip install -r requirements/base.txt

# AI/ML capabilities
pip install -r requirements/ai-ml.txt

# Document processing
pip install -r requirements/document-processing.txt

# Web API framework
pip install -r requirements/web-api.txt

# Multimedia processing
pip install -r requirements/multimedia.txt

# Cloud and deployment
pip install -r requirements/cloud-deployment.txt

# Development tools (for development only)
pip install -r requirements/development.txt
```

## 📋 Dependency Categories

### Base (`base.txt`)
- Core Python utilities (numpy, pandas, etc.)
- HTTP and networking
- Data validation and serialization
- Logging and monitoring

### AI/ML (`ai-ml.txt`)
- PyTorch and transformers
- NLP and text analysis
- Vector databases and embeddings
- AI frameworks and APIs
- Optimization and performance
- Experiment tracking

### Document Processing (`document-processing.txt`)
- PDF, DOCX, and markdown processing
- Document intelligence and parsing
- Citation and reference management
- Web scraping and content extraction

### Web API (`web-api.txt`)
- FastAPI framework
- Database and storage connectors
- Monitoring and observability
- Security and authentication

### Multimedia (`multimedia.txt`)
- Image and computer vision
- Audio processing and speech recognition
- Interactive web interfaces
- Data visualization

### Cloud & Deployment (`cloud-deployment.txt`)
- Cloud service SDKs (AWS, GCP, Azure)
- Containerization and orchestration
- Monitoring and observability

### Development (`development.txt`)
- Testing frameworks
- Code quality tools
- Development utilities

## 🔧 Environment-Specific Configurations

### Development Environment
```bash
pip install -r requirements/requirements.txt
```

### Production Environment
```bash
pip install -r requirements/production.txt
```

### CI/CD Pipeline
```bash
# Install base dependencies
pip install -r requirements/base.txt

# Install specific modules as needed
pip install -r requirements/ai-ml.txt
pip install -r requirements/web-api.txt
```

### Docker Deployment
```dockerfile
# Use production requirements for smaller image size
COPY requirements/production.txt /app/requirements.txt
RUN pip install -r requirements.txt
```

## 📊 Dependency Management

### Version Pinning
All dependencies are pinned to specific versions for reproducibility:
- Format: `package==version`
- Example: `torch==2.1.1`

### Dependency Conflicts
Common conflicts and resolutions:
- `torch` and `torchvision` versions must be compatible
- `transformers` and `tokenizers` versions should match
- CUDA versions for GPU support

### Security Considerations
- Regular updates for security patches
- Use `pip-audit` to check for vulnerabilities
- Monitor dependency advisories

## 🔄 Updating Dependencies

### Automated Updates
```bash
# Update all dependencies to latest compatible versions
pip install --upgrade -r requirements/requirements.txt
```

### Manual Updates
1. Update version numbers in specific requirement files
2. Test compatibility with your application
3. Update this README if adding new categories

### Dependency Locking
Consider using `pip-tools` for dependency locking:
```bash
pip install pip-tools
pip-compile requirements/requirements.txt
```

## 🐛 Troubleshooting

### Common Issues

1. **CUDA Compatibility**
   - Ensure PyTorch version matches your CUDA version
   - Use `torch==2.1.1+cu118` for CUDA 11.8

2. **Memory Issues**
   - Use `faiss-cpu` instead of `faiss-gpu` for CPU-only environments
   - Consider using `torch==2.1.1+cpu` for CPU-only PyTorch

3. **Version Conflicts**
   - Use virtual environments to isolate dependencies
   - Check for conflicting package versions

### Support
For dependency-related issues:
1. Check the specific requirement file for the problematic package
2. Verify version compatibility
3. Consider using the minimal requirements for testing

## 📈 Performance Optimization

### GPU Support
For GPU acceleration, ensure:
- Compatible CUDA version
- GPU-enabled PyTorch installation
- Proper GPU drivers

### Memory Optimization
- Use quantized models when possible
- Enable gradient checkpointing for large models
- Monitor memory usage with `psutil`

### Installation Speed
- Use `pip` with `--no-cache-dir` for fresh installs
- Consider using `conda` for scientific packages
- Use `pip` wheels when available 