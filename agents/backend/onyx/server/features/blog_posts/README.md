# Blatam Academy NLP Training Pipeline

A production-ready, ultra-optimized NLP training pipeline with support for transformers, diffusion models, and comprehensive evaluation.

## 🚀 Features

- **Advanced Training Pipeline**: Mixed precision, gradient accumulation, early stopping, learning rate scheduling
- **Multi-GPU Support**: DataParallel and DistributedDataParallel training
- **Performance Optimization**: GPU acceleration, memory optimization, batch optimization, PyTorch 2.0+ compilation
- **Comprehensive Evaluation**: Multiple metrics, cross-validation, profiling
- **Experiment Tracking**: TensorBoard, Weights & Biases, MLflow integration
- **Modular Architecture**: Separate modules for data loading, models, training, and evaluation
- **Configuration Management**: YAML-based configuration with validation
- **Interactive UI**: Gradio interface for model inference and evaluation

## 📁 Project Structure

```
blog_posts/
├── model_training.py              # Main training pipeline
├── config_loader.py               # Configuration management
├── run_experiment.py              # Experiment runner script
├── gradio_app.py                  # Interactive UI
├── evaluation_metrics.py          # Evaluation metrics
├── early_stopping_lr_scheduling.py # Early stopping and LR scheduling
├── data_splitting_cv.py           # Data splitting and cross-validation
├── efficient_data_loader.py       # Efficient data loading
├── llm_models.py                  # LLM model implementations
├── diffusion_models.py            # Diffusion model implementations
├── production_transformers.py     # Production transformer utilities
├── unified_ai_engine.py           # Unified AI engine
├── configs/                       # Configuration files
│   ├── baseline.yaml
│   └── optimized.yaml
├── requirements_training_evaluation.txt
└── README.md
```

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd blatam-academy/agents/backend/onyx/server/features/blog_posts
```

2. **Install dependencies**
```bash
pip install -r requirements_training_evaluation.txt
```

3. **Verify installation**
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

## 🚀 Quick Start

### 1. Basic Training

```python
from model_training import quick_train_transformer

# Quick training with default settings
result = await quick_train_transformer(
    model_name="distilbert-base-uncased",
    dataset_path="data/sentiment_dataset.csv",
    num_epochs=5
)
```

### 2. Using Configuration Files

```bash
# Run with baseline configuration
python run_experiment.py --config configs/baseline.yaml

# Run with optimized configuration
python run_experiment.py --config configs/optimized.yaml

# Quick experiment
python run_experiment.py --quick --model distilbert-base-uncased --dataset data/sentiment.csv
```

### 3. Interactive UI

```bash
python gradio_app.py
```

## 📊 Configuration

### YAML Configuration Structure

```yaml
# Model settings
model_type: transformer
training_mode: fine_tune
model_name: distilbert-base-uncased

# Training parameters
batch_size: 16
learning_rate: 2e-5
num_epochs: 10
gradient_accumulation_steps: 4

# Performance optimization
enable_amp: true
enable_compilation: true
enable_gradient_checkpointing: true

# Logging
log_to_tensorboard: true
log_to_wandb: false
```

### Configuration Management

```python
from config_loader import load_config_from_yaml, validate_config

# Load and validate configuration
config = load_config_from_yaml("configs/baseline.yaml")
if validate_config(config):
    # Run training
    result = await trainer.train(config)
```

## 🔧 Advanced Features

### 1. Gradient Accumulation

```python
from model_training import gradient_accumulation_train_transformer

# Training with gradient accumulation for large effective batch sizes
result = await gradient_accumulation_train_transformer(
    model_name="distilbert-base-uncased",
    dataset_path="data/dataset.csv",
    gradient_accumulation_steps=8,
    effective_batch_size=256
)
```

### 2. Multi-GPU Training

```python
from model_training import multi_gpu_train_transformer

# Multi-GPU training
result = await multi_gpu_train_transformer(
    model_name="distilbert-base-uncased",
    dataset_path="data/dataset.csv",
    multi_gpu_type="auto"
)
```

### 3. Performance Optimization

```python
from model_training import ultra_optimized_train_transformer

# Ultra-optimized training with all optimizations
result = await ultra_optimized_train_transformer(
    model_name="distilbert-base-uncased",
    dataset_path="data/dataset.csv",
    target_effective_batch_size=512
)
```

### 4. Hyperparameter Optimization

```python
from model_training import quick_hyperparameter_optimization

# Hyperparameter optimization
result = await quick_hyperparameter_optimization(
    model_name="distilbert-base-uncased",
    dataset_path="data/dataset.csv",
    trials=50
)
```

## 📈 Experiment Tracking

### TensorBoard

```bash
# Launch TensorBoard
tensorboard --logdir runs/

# View at http://localhost:6006
```

### Weights & Biases

```python
# Enable wandb logging in config
log_to_wandb: true

# Results will be logged to your wandb dashboard
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest test_evaluation_metrics.py -v
python -m pytest test_early_stopping_lr_scheduling.py -v
python -m pytest test_data_splitting_cv.py -v
```

## 📚 Documentation

- [Training & Evaluation Guide](TRAINING_EVALUATION_GUIDE.md)
- [Evaluation Metrics Guide](EVALUATION_METRICS_GUIDE.md)
- [Early Stopping & LR Scheduling Guide](EARLY_STOPPING_LR_SCHEDULING_GUIDE.md)
- [Data Splitting & CV Guide](DATA_SPLITTING_CV_GUIDE.md)
- [Efficient Data Loading Guide](EFFICIENT_DATA_LOADING_GUIDE.md)

## 🔗 Dependencies

### Core Libraries
- **PyTorch** (>=2.0.0): Deep learning framework
- **Transformers** (>=4.30.0): Hugging Face transformers library
- **Diffusers** (>=0.18.0): Diffusion models
- **Gradio** (>=3.0.0): Interactive UI

### Data Processing
- **NumPy** (>=1.24.0): Numerical computing
- **Pandas** (>=2.0.0): Data manipulation
- **Scikit-learn** (>=1.3.0): Machine learning utilities

### Experiment Tracking
- **TensorBoard** (>=2.13.0): Visualization and logging
- **Weights & Biases** (>=0.15.0): Experiment tracking
- **MLflow** (>=2.5.0): Model lifecycle management

### Performance & Monitoring
- **tqdm** (>=4.65.0): Progress bars
- **psutil** (>=5.9.0): System monitoring
- **GPUtil** (>=1.4.0): GPU monitoring

## 🏗️ Architecture

### Modular Design
- **Data Loading**: Efficient data loading with caching and streaming
- **Models**: Modular model implementations (transformers, diffusion, LLMs)
- **Training**: Comprehensive training pipeline with optimization
- **Evaluation**: Multi-metric evaluation and cross-validation
- **Configuration**: YAML-based configuration management
- **UI**: Gradio-based interactive interface

### Best Practices
- **Version Control**: Git for code and configuration tracking
- **Experiment Tracking**: Comprehensive logging and visualization
- **Performance Optimization**: GPU acceleration, mixed precision, profiling
- **Error Handling**: Robust error handling and debugging
- **Testing**: Comprehensive test suite
- **Documentation**: Detailed guides and examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation guides
- Review the test examples
- Open an issue on GitHub

## 🚀 Roadmap

- [ ] Support for more model architectures
- [ ] Advanced data augmentation techniques
- [ ] Model compression and quantization
- [ ] Distributed training across multiple machines
- [ ] Real-time inference API
- [ ] Model serving with FastAPI
- [ ] Advanced visualization tools
- [ ] Automated hyperparameter tuning
- [ ] Model interpretability tools 