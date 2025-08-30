# 🚀 HeyGen AI - Enhanced Deep Learning System

A comprehensive, production-ready deep learning system implementing state-of-the-art transformer models, diffusion models, and training pipelines. Built with PyTorch best practices and designed for scalability and performance.

## ✨ Key Features

### 🧠 **Advanced Transformer Models**
- **Custom Transformer Architecture**: Implemented from scratch with proper attention mechanisms
- **Multi-Head Attention**: Scaled dot-product attention with configurable heads
- **Positional Encoding**: Sinusoidal positional encoding for sequence modeling
- **LoRA Integration**: Low-Rank Adaptation for efficient fine-tuning
- **Mixed Precision Training**: FP16 support for faster training and reduced memory usage

### 🎨 **State-of-the-Art Diffusion Models**
- **Multiple Pipeline Support**: Stable Diffusion, Stable Diffusion XL, ControlNet, Text-to-Video
- **Advanced Schedulers**: DDIM, DDPM, Euler, DPM-Solver
- **Memory Optimization**: Attention slicing, VAE slicing, CPU offloading
- **xFormers Integration**: Memory-efficient attention mechanisms
- **Image Variations & Upscaling**: img2img, inpainting, and upscaling capabilities

### 🏋️ **Professional Training Pipeline**
- **Comprehensive Configuration**: Extensive training parameters and options
- **Experiment Tracking**: Weights & Biases and TensorBoard integration
- **Model Checkpointing**: Automatic saving with best model preservation
- **Early Stopping**: Prevents overfitting with configurable patience
- **Cross-Validation**: K-fold cross-validation support
- **Distributed Training**: Multi-GPU training with Accelerate

### 🌐 **Interactive Gradio Interface**
- **Text Generation**: Multiple model support with parameter tuning
- **Image Generation**: Real-time image creation with style controls
- **Training Interface**: Visual training progress and model management
- **System Monitoring**: Real-time system information and performance metrics
- **Responsive Design**: Modern, user-friendly interface with proper error handling

## 🏗️ Architecture Overview

```
heygen_ai/
├── core/
│   ├── transformer_models_enhanced.py      # Advanced transformer implementations
│   ├── diffusion_models_enhanced.py        # Diffusion model pipelines
│   ├── model_training_enhanced.py          # Training orchestration
│   └── gradio_interface_enhanced.py        # Interactive web interface
├── requirements_enhanced_consolidated.txt   # All dependencies
├── run_enhanced_demo_comprehensive.py      # Comprehensive demo script
└── README_ENHANCED_DEEP_LEARNING.md        # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd heygen_ai

# Install dependencies
pip install -r requirements_enhanced_consolidated.txt

# Verify installation
python -c "import torch; print(f'PyTorch {torch.__version__}')"
```

### 2. Quick Demo

```bash
# Run quick system check
python run_enhanced_demo_comprehensive.py --quick

# Run comprehensive demo
python run_enhanced_demo_comprehensive.py
```

### 3. Launch Gradio Interface

```bash
# Launch the interactive interface
python core/gradio_interface_enhanced.py
```

## 📚 Usage Examples

### Text Generation

```python
from core.transformer_models_enhanced import TransformerManager, TransformerConfig

# Initialize configuration
config = TransformerConfig(
    model_name="gpt2",
    use_fp16=True,
    device="cuda"
)

# Create manager and load model
manager = TransformerManager(config)
manager.load_pretrained_model()

# Generate text
generated_text = manager.generate_text(
    prompt="The future of artificial intelligence is",
    max_length=100,
    temperature=0.7,
    top_p=0.9
)

print(generated_text)
```

### Image Generation

```python
from core.diffusion_models_enhanced import DiffusionPipelineManager, DiffusionConfig

# Initialize configuration
config = DiffusionConfig(
    model_type="stable_diffusion",
    width=512,
    height=512,
    num_inference_steps=50,
    guidance_scale=7.5
)

# Create manager
manager = DiffusionPipelineManager(config)

# Generate images
images = manager.generate_image(
    prompt="A beautiful sunset over mountains, digital art",
    negative_prompt="blurry, low quality",
    num_images=1
)

# Save the first image
images[0].save("generated_image.png")
```

### Model Training

```python
from core.model_training_enhanced import ModelTrainer, TrainingConfig

# Initialize configuration
config = TrainingConfig(
    model_name="gpt2",
    batch_size=8,
    learning_rate=5e-5,
    num_epochs=10,
    use_fp16=True
)

# Create trainer (you'll need to provide datasets)
trainer = ModelTrainer(config, model, train_dataset, val_dataset)

# Start training
results = trainer.train()
```

## ⚙️ Configuration

### Transformer Configuration

```python
@dataclass
class TransformerConfig:
    # Model architecture
    model_name: str = "gpt2"
    hidden_size: int = 768
    num_attention_heads: int = 12
    num_hidden_layers: int = 12
    
    # Training settings
    batch_size: int = 8
    learning_rate: float = 5e-5
    use_fp16: bool = True
    
    # LoRA settings
    use_lora: bool = False
    lora_r: int = 16
    lora_alpha: int = 32
```

### Diffusion Configuration

```python
@dataclass
class DiffusionConfig:
    # Model settings
    model_type: str = "stable_diffusion"
    scheduler_type: str = "ddim"
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    
    # Optimization settings
    use_fp16: bool = True
    enable_attention_slicing: bool = True
    enable_xformers_memory_efficient_attention: bool = True
```

### Training Configuration

```python
@dataclass
class TrainingConfig:
    # Model settings
    model_name: str = "gpt2"
    batch_size: int = 8
    learning_rate: float = 5e-5
    num_epochs: int = 10
    
    # Optimization settings
    use_fp16: bool = True
    use_mixed_precision: bool = True
    gradient_accumulation_steps: int = 4
    
    # Checkpointing settings
    save_steps: int = 500
    save_total_limit: int = 3
    checkpoint_dir: str = "./checkpoints"
```

## 🔧 Advanced Features

### Memory Optimization

- **Mixed Precision Training**: Automatic FP16/FP32 switching
- **Gradient Accumulation**: Large effective batch sizes with minimal memory
- **Attention Slicing**: Process attention in chunks to reduce memory usage
- **VAE Slicing**: Process VAE in chunks for image generation
- **CPU Offloading**: Move unused model components to CPU

### Performance Optimization

- **xFormers Integration**: Memory-efficient attention mechanisms
- **Flash Attention**: Optimized attention computation
- **Distributed Training**: Multi-GPU training with Accelerate
- **Model Parallelism**: Split large models across multiple GPUs
- **Data Parallelism**: Process different batches on different GPUs

### Experiment Tracking

- **Weights & Biases**: Comprehensive experiment tracking
- **TensorBoard**: Real-time training visualization
- **Custom Metrics**: Flexible metric collection and logging
- **Model Versioning**: Automatic model versioning and comparison

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=core tests/

# Run specific test file
pytest tests/test_transformer_models.py
```

## 📊 Performance Benchmarks

### Text Generation (GPT-2 Medium)
- **GPU**: RTX 4090
- **Batch Size**: 1
- **Sequence Length**: 100
- **Generation Time**: ~0.5 seconds
- **Memory Usage**: ~2.5 GB

### Image Generation (Stable Diffusion v1.5)
- **GPU**: RTX 4090
- **Resolution**: 512x512
- **Inference Steps**: 50
- **Generation Time**: ~3-5 seconds
- **Memory Usage**: ~4-6 GB

### Training Performance
- **Mixed Precision**: 1.5-2x speedup
- **Gradient Accumulation**: Linear memory scaling
- **Distributed Training**: Near-linear scaling with multiple GPUs

## 🚨 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size
   - Enable attention slicing
   - Use gradient accumulation
   - Enable mixed precision

2. **Model Loading Errors**
   - Check internet connection
   - Verify model names
   - Clear HuggingFace cache

3. **Performance Issues**
   - Enable xFormers
   - Use mixed precision
   - Optimize data loading
   - Profile with torch.profiler

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable PyTorch anomaly detection
torch.autograd.set_detect_anomaly(True)

# Profile specific operations
with torch.profiler.profile() as prof:
    # Your code here
    pass
print(prof.key_averages().table())
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add comprehensive docstrings
- Include unit tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PyTorch Team**: For the excellent deep learning framework
- **Hugging Face**: For transformers and diffusers libraries
- **Stability AI**: For Stable Diffusion models
- **OpenAI**: For GPT models and research

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: This README and inline code docs
- **Examples**: See `run_enhanced_demo_comprehensive.py`

---

**Built with ❤️ for the AI community**

*Last updated: December 2024*
