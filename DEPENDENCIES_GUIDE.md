# 📦 Dependencies Guide for Enhanced AI Model Demos System

## 🎯 Overview

This guide provides comprehensive information about all dependencies required for the Enhanced AI Model Demos System, which includes:

- **Interactive Gradio Demos**: Web-based interfaces for model inference
- **Performance Optimization**: Memory management, caching, and optimization
- **Multi-GPU Training**: DataParallel and DistributedDataParallel support
- **PyTorch Debugging Tools**: Anomaly detection, gradient monitoring, profiling
- **Code Profiling**: Bottleneck detection and performance analysis
- **Error Handling & Validation**: Comprehensive error management

## 📋 Requirements Files

### 1. **`requirements-enhanced-system.txt`** - Complete System
Contains all dependencies for the full system including development tools.

### 2. **`requirements-production.txt`** - Production Deployment
Minimal dependencies for production deployment.

### 3. **`requirements-development.txt`** - Development Environment
Includes testing, code quality, and development tools.

## 🏗️ Core Dependencies

### **PyTorch Ecosystem**
```bash
torch>=2.2.0          # Core deep learning framework
torchvision>=0.17.0   # Computer vision utilities
torchaudio>=2.2.0     # Audio processing utilities
```

**Purpose**: Core machine learning framework for model creation, training, and inference.

**Installation Notes**:
- For CUDA support: Visit [pytorch.org](https://pytorch.org) for platform-specific installation
- For CPU-only: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu`

### **Interactive Web Interface**
```bash
gradio>=4.37.0        # Web-based UI framework
```

**Purpose**: Creates interactive web interfaces for model demos and visualization.

**Features**:
- Real-time model inference
- Interactive data visualization
- Responsive design
- Easy deployment

### **Numerical Computing**
```bash
numpy>=1.24.0         # Numerical computing
pandas>=2.0.0         # Data manipulation
scipy>=1.11.0         # Scientific computing
```

**Purpose**: Data processing, manipulation, and mathematical operations.

### **Visualization**
```bash
plotly>=5.17.0        # Interactive plotting
plotly-express>=0.4.1 # Simplified plotting interface
matplotlib>=3.7.0     # Static plotting (fallback)
seaborn>=0.12.0       # Statistical visualization
```

**Purpose**: Data visualization, performance charts, and interactive plots.

## 🔧 Performance & Monitoring Dependencies

### **System Monitoring**
```bash
psutil>=5.9.0         # System and process monitoring
nvidia-ml-py3>=11.0.0 # GPU monitoring (optional)
memory-profiler>=0.61.0 # Memory usage profiling
```

**Purpose**: Monitor system resources, GPU usage, and memory consumption.

### **Performance Profiling**
```bash
line-profiler>=4.1.0  # Line-by-line profiling
py-spy>=0.3.14        # CPU profiling
```

**Purpose**: Identify performance bottlenecks and optimize code execution.

## 🧪 Development & Testing Dependencies

### **Testing Framework**
```bash
pytest>=7.4.3         # Testing framework
pytest-cov>=4.1.0     # Coverage reporting
pytest-mock>=3.11.1   # Mocking support
pytest-asyncio>=0.21.1 # Async testing support
```

**Purpose**: Comprehensive testing of all system components.

### **Code Quality**
```bash
black>=23.11.0        # Code formatting
flake8>=6.1.0         # Linting
mypy>=1.7.0           # Type checking
ruff>=0.1.0           # Fast Python linter
```

**Purpose**: Maintain code quality, consistency, and catch errors early.

### **Development Tools**
```bash
jupyter>=1.0.0        # Interactive development
ipython>=8.17.0       # Enhanced Python shell
pre-commit>=3.5.0     # Git hooks for quality
```

**Purpose**: Enhanced development experience and workflow automation.

## 🚀 Installation Instructions

### **Quick Start (Production)**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements-production.txt
```

### **Full Development Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements-enhanced-system.txt

# Install development tools
pip install -r requirements-development.txt

# Setup pre-commit hooks
pre-commit install
```

### **GPU Support Setup**
```bash
# 1. Check CUDA compatibility
nvidia-smi

# 2. Install PyTorch with CUDA support
# Visit pytorch.org for your specific CUDA version

# 3. Verify installation
python -c "import torch; print(torch.cuda.is_available())"
```

## 🖥️ Platform-Specific Considerations

### **Windows**
- **Visual C++ Build Tools**: Required for some packages
- **CUDA**: Ensure compatible CUDA version with PyTorch
- **Path Length**: Some packages may have long path issues

**Installation**:
```bash
# Install Visual C++ Build Tools
# Download from Microsoft Visual Studio

# Use shorter paths for virtual environments
python -m venv C:\venv\ai-demos
```

### **macOS**
- **Xcode Command Line Tools**: Required for compilation
- **M1/M2 Chips**: Use compatible PyTorch versions

**Installation**:
```bash
# Install Xcode Command Line Tools
xcode-select --install

# For M1/M2, ensure PyTorch compatibility
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### **Linux**
- **Build Essentials**: Required for compilation
- **CUDA**: Install NVIDIA drivers and CUDA toolkit

**Installation**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel
```

## 🔍 Dependency Categories

### **Essential (Production)**
- `torch`, `torchvision` - Core ML framework
- `gradio` - Web interface
- `numpy` - Numerical computing
- `plotly` - Visualization
- `psutil` - System monitoring

### **Performance (Production)**
- `nvidia-ml-py3` - GPU monitoring
- `memory-profiler` - Memory analysis

### **Development (Development Only)**
- `pytest` - Testing
- `black`, `flake8` - Code quality
- `jupyter` - Interactive development

### **Optional (Enhancement)**
- `tensorboard` - PyTorch profiling
- `wandb` - Experiment tracking
- `matplotlib`, `seaborn` - Additional visualization

### **NLP & Transformers (Production)**
- `transformers` - Hugging Face transformers library
- `tokenizers` - Fast tokenization
- `accelerate` - Training acceleration
- `peft` - Parameter-efficient fine-tuning

### **Diffusion Models & Image Generation (Production)**
- `diffusers` - Hugging Face diffusers library
- `Pillow` - Image processing
- `opencv-python` - Computer vision
- `imageio` - Image I/O and video

## 📊 Version Compatibility

### **Python Version Support**
- **Minimum**: Python 3.8
- **Recommended**: Python 3.9+
- **Latest**: Python 3.11+

### **PyTorch Version Matrix**
| PyTorch | CUDA | Python | Notes |
|---------|------|--------|-------|
| 2.2.0   | 11.8 | 3.8-3.11 | Stable, recommended |
| 2.1.0   | 11.8 | 3.8-3.11 | Good compatibility |
| 2.0.0   | 11.7 | 3.8-3.11 | Legacy support |

### **Gradio Version Support**
- **Minimum**: Gradio 4.0.0
- **Recommended**: Gradio 4.37.0+
- **Latest**: Gradio 4.x.x

## 🚨 Common Issues & Solutions

### **CUDA Installation Issues**
```bash
# Problem: CUDA not found
# Solution: Install compatible CUDA version
# Check: nvidia-smi and torch.version.cuda

# Problem: PyTorch CUDA mismatch
# Solution: Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### **Memory Issues**
```bash
# Problem: Out of memory during training
# Solution: Reduce batch size, enable gradient accumulation
# Check: torch.cuda.memory_allocated()

# Problem: Memory leaks
# Solution: Use memory profiling tools
python -m memory_profiler your_script.py
```

### **Import Errors**
```bash
# Problem: Module not found
# Solution: Check virtual environment activation
which python  # Should point to venv
pip list      # Should show installed packages

# Problem: Version conflicts
# Solution: Use virtual environment and pin versions
pip install --upgrade pip
pip install -r requirements-enhanced-system.txt --force-reinstall
```

## 🔧 Environment Management

### **Virtual Environment Best Practices**
```bash
# Create environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/macOS)
source venv/bin/activate

# Deactivate
deactivate

# Remove environment
rm -rf venv  # Unix/macOS
rmdir /s venv  # Windows
```

### **Dependency Pinning**
```bash
# Generate requirements with exact versions
pip freeze > requirements-pinned.txt

# Install exact versions
pip install -r requirements-pinned.txt

# Update dependencies
pip install --upgrade -r requirements-enhanced-system.txt
```

## 📈 Performance Optimization

### **GPU Memory Management**
```python
# Clear GPU cache
torch.cuda.empty_cache()

# Monitor memory usage
print(f"GPU Memory: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")

# Use mixed precision
from torch.cuda.amp import autocast, GradScaler
```

### **CPU Optimization**
```python
# Use multiple processes
from multiprocessing import Pool

# Profile performance
import cProfile
import pstats
```

## 🧪 Testing Dependencies

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest test_code_profiling.py

# Run with verbose output
pytest -v
```

### **Code Quality Checks**
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Run all quality checks
pre-commit run --all-files
```

## 📚 Additional Resources

### **Official Documentation**
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Gradio Documentation](https://gradio.app/docs/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Plotly Documentation](https://plotly.com/python/)

### **Community Resources**
- [PyTorch Forums](https://discuss.pytorch.org/)
- [Gradio Discord](https://discord.gg/feTf9x3ZSB)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/pytorch)

### **Performance Guides**
- [PyTorch Performance Tuning](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)
- [Memory Management](https://pytorch.org/docs/stable/notes/cuda.html#memory-management)
- [Profiling](https://pytorch.org/tutorials/beginner/profiler.html)

## 🎯 Next Steps

1. **Install Dependencies**: Choose appropriate requirements file
2. **Setup Environment**: Configure virtual environment
3. **Verify Installation**: Run basic tests
4. **Customize Configuration**: Adjust for your specific needs
5. **Start Development**: Begin building your AI model demos

## 🤝 Support

For issues with dependencies:
1. Check this guide for common solutions
2. Verify platform-specific requirements
3. Check package compatibility matrices
4. Consult official documentation
5. Seek community support

---

**Note**: This guide covers the most common scenarios. For specific use cases or advanced configurations, refer to the official documentation of individual packages.
