# 🚀 Diffusion Model Training and Evaluation System

A comprehensive system for training and evaluating diffusion models with advanced features, monitoring, and optimization capabilities.

## 🎯 Overview

This system provides a complete solution for training diffusion models with:
- **Flexible Training Configurations**: Multiple training modes and hyperparameter options
- **Advanced Evaluation Metrics**: Comprehensive model assessment with multiple metrics
- **Checkpoint Management**: Intelligent checkpoint saving and restoration
- **Performance Monitoring**: Real-time training metrics and visualization
- **Distributed Training**: Support for multi-GPU training
- **Mixed Precision**: FP16 training for memory efficiency

## 🏗️ System Architecture

```
DiffusionTrainingEvaluationSystem/
├── DiffusionTrainer          # Main training orchestrator
├── DiffusionEvaluator        # Model evaluation and metrics
├── TrainingConfig            # Training configuration management
├── EvaluationConfig          # Evaluation configuration management
├── TrainingMetrics           # Metrics tracking and storage
├── DiffusionDataset          # Base dataset class
├── ImageTextDataset          # Image-text pair dataset
└── Utility Functions         # Helper functions and setup
```

## 🚀 Quick Start

### Basic Training

```python
from core.diffusion_training_evaluation_system import (
    DiffusionTrainer, create_training_config, MockDiffusionModel
)

# Create model and datasets
model = MockDiffusionModel()
train_dataset = YourDataset()
val_dataset = YourValidationDataset()

# Create training configuration
config = create_training_config(
    batch_size=4,
    learning_rate=1e-4,
    num_epochs=100,
    mixed_precision=True
)

# Initialize trainer
trainer = DiffusionTrainer(model, config, train_dataset, val_dataset)

# Start training
training_results = trainer.train()
```

### Basic Evaluation

```python
from core.diffusion_training_evaluation_system import (
    DiffusionEvaluator, create_evaluation_config, EvaluationMetric
)

# Create evaluation configuration
eval_config = create_evaluation_config(
    metrics=[EvaluationMetric.FID, EvaluationMetric.LPIPS, EvaluationMetric.SSIM],
    batch_size=8,
    num_samples=1000
)

# Initialize evaluator
evaluator = DiffusionEvaluator(model, eval_config)

# Run evaluation
evaluation_results = evaluator.evaluate(test_dataset)
```

## ⚙️ Configuration Options

### Training Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | str | "runwayml/stable-diffusion-v1-5" | Model identifier |
| `model_type` | TrainingMode | CONDITIONAL | Training mode |
| `batch_size` | int | 4 | Training batch size |
| `learning_rate` | float | 1e-5 | Initial learning rate |
| `num_epochs` | int | 100 | Total training epochs |
| `gradient_accumulation_steps` | int | 4 | Gradient accumulation steps |
| `max_grad_norm` | float | 1.0 | Maximum gradient norm for clipping |
| `weight_decay` | float | 1e-2 | Weight decay for regularization |
| `mixed_precision` | bool | True | Enable FP16 training |
| `gradient_checkpointing` | bool | True | Enable gradient checkpointing |
| `checkpoint_strategy` | CheckpointStrategy | BEST_METRIC | Checkpoint saving strategy |

### Evaluation Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metrics` | List[EvaluationMetric] | [FID, LPIPS, SSIM] | Evaluation metrics |
| `batch_size` | int | 8 | Evaluation batch size |
| `num_samples` | int | 1000 | Number of samples to evaluate |
| `save_generated_images` | bool | True | Save generated images |
| `save_metrics` | bool | True | Save evaluation results |
| `output_dir` | str | "evaluation_results" | Output directory |

## 🎯 Training Modes

### 1. Unconditional Training
Train models to generate images without any conditioning.

```python
config = create_training_config(
    model_type=TrainingMode.UNCONDITIONAL,
    batch_size=8,
    learning_rate=1e-4
)
```

### 2. Conditional Training
Train models with text or image conditioning (e.g., Stable Diffusion).

```python
config = create_training_config(
    model_type=TrainingMode.CONDITIONAL,
    batch_size=4,
    learning_rate=1e-5
)
```

### 3. Inpainting Training
Train models for image inpainting tasks.

```python
config = create_training_config(
    model_type=TrainingMode.INPAINTING,
    batch_size=2,
    learning_rate=5e-5
)
```

### 4. ControlNet Training
Train models with control signals (e.g., depth maps, edge maps).

```python
config = create_training_config(
    model_type=TrainingMode.CONTROLNET,
    batch_size=2,
    learning_rate=1e-5
)
```

### 5. Refiner Training
Train models for image refinement and enhancement.

```python
config = create_training_config(
    model_type=TrainingMode.REFINER,
    batch_size=4,
    learning_rate=1e-5
)
```

## 📊 Evaluation Metrics

### 1. FID (Fréchet Inception Distance)
Measures the quality and diversity of generated images.

```python
eval_config = create_evaluation_config(
    metrics=[EvaluationMetric.FID],
    fid_features=2048  # Number of features to extract
)
```

### 2. LPIPS (Learned Perceptual Image Patch Similarity)
Measures perceptual similarity between images.

```python
eval_config = create_evaluation_config(
    metrics=[EvaluationMetric.LPIPS],
    lpips_model="alex"  # or "vgg", "squeeze"
)
```

### 3. SSIM (Structural Similarity Index)
Measures structural similarity between images.

```python
eval_config = create_evaluation_config(
    metrics=[EvaluationMetric.SSIM],
    ssim_window_size=11
)
```

### 4. PSNR (Peak Signal-to-Noise Ratio)
Measures image quality in terms of noise.

```python
eval_config = create_evaluation_config(
    metrics=[EvaluationMetric.PSNR]
)
```

### 5. MSE/MAE (Mean Squared/Absolute Error)
Basic pixel-level error metrics.

```python
eval_config = create_evaluation_config(
    metrics=[EvaluationMetric.MSE, EvaluationMetric.MAE]
)
```

## 💾 Checkpoint Management

### Checkpoint Strategies

#### 1. Best Metric Strategy
Save checkpoints based on validation metric improvement.

```python
config = create_training_config(
    checkpoint_strategy=CheckpointStrategy.BEST_METRIC,
    save_total_limit=3
)
```

#### 2. Last N Strategy
Keep the last N checkpoints.

```python
config = create_training_config(
    checkpoint_strategy=CheckpointStrategy.LAST_N,
    save_total_limit=5
)
```

#### 3. Every N Steps Strategy
Save checkpoints every N training steps.

```python
config = create_training_config(
    checkpoint_strategy=CheckpointStrategy.EVERY_N_STEPS,
    save_steps=100
)
```

#### 4. Every N Epochs Strategy
Save checkpoints every N epochs.

```python
config = create_training_config(
    checkpoint_strategy=CheckpointStrategy.EVERY_N_EPOCHS,
    save_steps=10
)
```

### Loading Checkpoints

```python
# Load from specific checkpoint
trainer.load_checkpoint("checkpoints/best_checkpoint.pth")

# Load from latest checkpoint
trainer.load_checkpoint("checkpoints/latest_checkpoint.pth")
```

## 🔧 Advanced Features

### 1. Mixed Precision Training
Enable FP16 training for memory efficiency.

```python
config = create_training_config(
    mixed_precision=True,
    gradient_checkpointing=True
)
```

### 2. Gradient Accumulation
Train with larger effective batch sizes.

```python
config = create_training_config(
    batch_size=2,
    gradient_accumulation_steps=8  # Effective batch size = 16
)
```

### 3. Distributed Training
Train across multiple GPUs.

```python
from core.diffusion_training_evaluation_system import setup_distributed_training

# Setup distributed training
device = setup_distributed_training(local_rank=0, world_size=2)

config = create_training_config(
    distributed=True,
    local_rank=0
)
```

### 4. Custom Loss Functions
Implement custom loss functions for specific tasks.

```python
class CustomLoss(nn.Module):
    def __init__(self):
        super().__init__()
    
    def forward(self, prediction, target):
        # Implement custom loss logic
        return F.mse_loss(prediction, target)

# Use in training
trainer.custom_loss = CustomLoss()
```

## 📈 Monitoring and Visualization

### Training Metrics
The system automatically tracks:
- Training and validation loss
- Learning rate changes
- Gradient norms
- Epoch and step times
- Training progress

### Real-time Monitoring
```python
# Access metrics during training
current_loss = trainer.metrics.get_latest_train_loss()
best_val_loss = trainer.metrics.get_best_val_loss()
training_progress = len(trainer.metrics.train_loss)

# Get training summary
summary = trainer._final_evaluation()
print(f"Training completed in {summary['total_epochs']} epochs")
print(f"Best validation loss: {summary['best_val_loss']:.4f}")
```

### Visualization
The system automatically generates:
- Training curves (loss, learning rate, gradients)
- Evaluation metric comparisons
- Training progress indicators
- Overfitting detection plots

## 🎨 Custom Dataset Integration

### Extending the Base Dataset

```python
class YourCustomDataset(DiffusionDataset):
    def __init__(self, data_dir: str, image_size: int = 512):
        super().__init__(data_dir, image_size)
    
    def _load_samples(self) -> List[Dict[str, Any]]:
        # Implement your data loading logic
        samples = []
        # Load your data here
        return samples
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sample = self.samples[idx]
        
        # Load and preprocess your data
        image = self._load_image(sample['image_path'])
        text_tokens = self._tokenize_text(sample['text'])
        
        return {
            'image': image,
            'text_tokens': text_tokens,
            'text': sample['text']
        }
    
    def _load_image(self, image_path: str) -> torch.Tensor:
        # Implement image loading logic
        # Use PIL, torchvision, or your preferred method
        pass
    
    def _tokenize_text(self, text: str) -> torch.Tensor:
        # Implement text tokenization
        # Use your tokenizer (CLIP, T5, etc.)
        pass
```

## 🚀 Performance Optimization

### 1. Memory Optimization
```python
config = create_training_config(
    gradient_checkpointing=True,  # Reduce memory usage
    mixed_precision=True,         # Use FP16
    batch_size=2,                 # Smaller batch size
    gradient_accumulation_steps=8 # Effective batch size = 16
)
```

### 2. Training Speed
```python
config = create_training_config(
    num_workers=4,                # Multiple data loading workers
    pin_memory=True,              # Faster data transfer to GPU
    prefetch_factor=2,            # Prefetch data
    persistent_workers=True        # Keep workers alive between epochs
)
```

### 3. Distributed Training
```python
# Multi-GPU training
config = create_training_config(
    distributed=True,
    local_rank=0,
    world_size=torch.cuda.device_count()
)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Out of Memory (OOM)
```python
# Reduce memory usage
config = create_training_config(
    batch_size=1,                    # Reduce batch size
    gradient_checkpointing=True,     # Enable gradient checkpointing
    mixed_precision=True,            # Use FP16
    gradient_accumulation_steps=16   # Increase accumulation steps
)
```

#### 2. Slow Training
```python
# Optimize for speed
config = create_training_config(
    num_workers=8,                   # Increase workers
    pin_memory=True,                 # Enable pin memory
    prefetch_factor=4,               # Increase prefetch
    persistent_workers=True           # Keep workers alive
)
```

#### 3. Poor Convergence
```python
# Improve convergence
config = create_training_config(
    learning_rate=1e-5,              # Lower learning rate
    weight_decay=1e-3,               # Add regularization
    max_grad_norm=0.5,               # Reduce gradient clipping
    gradient_accumulation_steps=4    # Stable gradients
)
```

### Debug Mode
```python
# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Check model parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters: {total_params:,}")
print(f"Trainable parameters: {trainable_params:,}")
```

## 📚 Examples and Tutorials

### Complete Training Example
See `run_diffusion_training_evaluation_demo.py` for a comprehensive example.

### Custom Training Loop
```python
# Custom training loop with the trainer
trainer = DiffusionTrainer(model, config, train_dataset, val_dataset)

for epoch in range(config.num_epochs):
    # Custom epoch logic
    train_loss = trainer._train_epoch(train_loader, epoch)
    val_loss = trainer._validate_epoch(val_loader, epoch)
    
    # Custom logging
    print(f"Epoch {epoch}: Train={train_loss:.4f}, Val={val_loss:.4f}")
    
    # Custom checkpointing
    if val_loss < best_val_loss:
        trainer._save_checkpoint(epoch, val_loss)
        best_val_loss = val_loss
```

### Evaluation Pipeline
```python
# Comprehensive evaluation pipeline
evaluator = DiffusionEvaluator(model, eval_config)

# Run evaluation
results = evaluator.evaluate(test_dataset)

# Analyze results
for metric, value in results.items():
    if value is not None:
        print(f"{metric.upper()}: {value:.4f}")

# Generate custom visualizations
evaluator._generate_evaluation_plots(results)
```

## 🔮 Future Enhancements

### Planned Features
1. **Advanced Metrics**: CLIP score, CLIP-FID, IS (Inception Score)
2. **Custom Schedulers**: OneCycle, Plateau, Custom learning rate schedules
3. **Advanced Augmentation**: RandAugment, AutoAugment, custom transforms
4. **Model Comparison**: Side-by-side model evaluation
5. **Hyperparameter Tuning**: Integration with Optuna, Ray Tune
6. **Experiment Tracking**: MLflow, Weights & Biases integration
7. **Model Compression**: Quantization, pruning, distillation
8. **Multi-Modal Training**: Support for audio, video, 3D data

### Contributing
Contributions are welcome! Please see the contribution guidelines for:
- Adding new evaluation metrics
- Implementing new training modes
- Optimizing performance
- Adding new features

## 📄 License

This system is part of the comprehensive diffusion models implementation and follows the same licensing terms.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the examples and demos
3. Check the comprehensive documentation
4. Open an issue for bugs or feature requests

---

**🎯 Ready to train and evaluate your diffusion models with professional-grade tools!**
