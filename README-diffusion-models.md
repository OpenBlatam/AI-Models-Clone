# Diffusion Models for Blaze AI

A comprehensive implementation of diffusion models using the Hugging Face Diffusers library, including training, evaluation, and various pipeline types.

## 🚀 Quick Start

### Installation

```bash
# Install core dependencies
pip install -r requirements-diffusion.txt

# For GPU optimization (optional)
pip install xformers flash-attn
```

### Basic Usage

```python
from deployment.scripts.python.diffusion_pipelines_guide import DiffusionPipelineManager, PipelineConfig

# Setup pipeline manager
config = PipelineConfig(
    model_id="runwayml/stable-diffusion-v1-5",
    num_inference_steps=50,
    guidance_scale=7.5
)

pipeline_manager = DiffusionPipelineManager(config)

# Load Stable Diffusion pipeline
pipeline = pipeline_manager.load_stable_diffusion_pipeline()

# Generate image
result = pipeline("A beautiful landscape with mountains")
image = result.images[0]
image.save("generated_image.png")
```

## 📚 Components Overview

### 1. Diffusion Pipelines Guide (`diffusion_pipelines_guide.py`)

Comprehensive guide to using different Hugging Face Diffusers pipelines:

- **StableDiffusionPipeline**: Standard text-to-image generation
- **StableDiffusionXLPipeline**: Higher resolution, better quality
- **StableDiffusionImg2ImgPipeline**: Transform existing images
- **StableDiffusionInpaintPipeline**: Fill in masked areas
- **StableDiffusionControlNetPipeline**: Control generation with conditions
- **StableDiffusionUpscalePipeline**: Increase image resolution

#### Key Features:
- Automatic device detection (CUDA, MPS, CPU)
- Memory optimization (attention slicing, xformers, CPU offload)
- Mixed precision support (fp16, bf16)
- Pipeline comparison and benchmarking
- Comprehensive error handling

#### Example: Using Different Pipelines

```python
from deployment.scripts.python.diffusion_pipelines_guide import (
    DiffusionPipelineManager, PipelineConfig, PipelineUsageExamples
)

# Setup manager
config = PipelineConfig(
    model_id="runwayml/stable-diffusion-v1-5",
    num_inference_steps=30,
    height=512,
    width=512
)

manager = DiffusionPipelineManager(config)

# Load multiple pipelines
manager.load_stable_diffusion_pipeline()
manager.load_img2img_pipeline()
manager.load_inpaint_pipeline()

# Use examples
examples = PipelineUsageExamples(manager)

# Text-to-image
image = examples.text_to_image_example("A beautiful sunset")

# Image-to-image
transformed = examples.img2img_example(image, "Make it more vibrant", strength=0.8)
```

### 2. Diffusion Training and Evaluation (`diffusion_training_evaluation.py`)

Complete framework for training and evaluating diffusion models:

#### Training Features:
- Custom training loops with noise scheduling
- Multiple optimizer support (AdamW, Lion, Adafactor)
- Learning rate schedulers (cosine, linear, exponential)
- Mixed precision training with gradient scaling
- EMA (Exponential Moving Average) support
- Gradient accumulation and clipping
- Comprehensive logging and checkpointing

#### Evaluation Features:
- FID (Fréchet Inception Distance) computation
- LPIPS (Learned Perceptual Image Patch Similarity)
- PSNR (Peak Signal-to-Noise Ratio)
- SSIM (Structural Similarity Index)
- Custom dataset support
- Generated image saving and analysis

#### Example: Training a Diffusion Model

```python
from deployment.scripts.python.diffusion_training_evaluation import (
    DiffusionTrainer, TrainingConfig, DiffusionDataset
)

# Setup training configuration
training_config = TrainingConfig(
    num_epochs=100,
    batch_size=4,
    learning_rate=1e-5,
    use_mixed_precision=True,
    use_ema=True,
    save_every_n_epochs=10
)

# Create trainer
trainer = DiffusionTrainer(
    config=training_config,
    model=your_model,
    tokenizer=your_tokenizer,
    train_dataset=train_dataset,
    val_dataset=val_dataset
)

# Start training
trainer.train()
```

#### Example: Evaluating a Model

```python
from deployment.scripts.python.diffusion_training_evaluation import (
    DiffusionEvaluator, EvaluationConfig
)

# Setup evaluation configuration
eval_config = EvaluationConfig(
    num_eval_samples=100,
    compute_fid=True,
    compute_lpips=True,
    compute_psnr=True,
    compute_ssim=True
)

# Create evaluator
evaluator = DiffusionEvaluator(
    config=eval_config,
    model=your_model,
    tokenizer=your_tokenizer,
    pipeline=your_pipeline
)

# Evaluate model
metrics = evaluator.evaluate_model(test_dataset)
print(f"FID Score: {metrics['fid']:.4f}")
print(f"LPIPS Score: {metrics['lpips']:.4f}")
```

### 3. Noise Schedulers and Sampling Methods (`noise_schedulers_and_sampling.py`)

Comprehensive guide to noise schedulers and sampling techniques:

#### Available Schedulers:
- **DDPM**: Original, highest quality, slowest
- **DDIM**: Fast, high quality, deterministic
- **DPM-Solver**: Fastest, good quality, few steps
- **Euler/Heun**: Balanced, moderate speed/quality
- **UniPC**: Fast generation, high quality

#### Custom Beta Schedules:
- Linear, Cosine, Sigmoid, Quadratic, Exponential

#### Example: Using Different Schedulers

```python
from deployment.scripts.python.noise_schedulers_and_sampling import (
    NoiseSchedulerManager, SchedulerConfig, SamplingMethods
)

# Setup scheduler manager
config = SchedulerConfig(
    num_train_timesteps=1000,
    beta_start=0.0001,
    beta_end=0.02,
    beta_schedule="cosine"
)

manager = NoiseSchedulerManager(config)

# Compare schedulers
comparison = manager.compare_schedulers(num_inference_steps=20)

# Get recommendations
from deployment.scripts.python.noise_schedulers_and_sampling import SchedulerRecommendations

recommendations = SchedulerRecommendations.get_recommendations(
    "fast_generation", 
    {"speed": "fast", "steps": 10}
)
print(f"Recommended schedulers: {recommendations}")
```

## 🔧 Advanced Features

### Memory Optimization

```python
# Enable attention slicing
pipeline.enable_attention_slicing()

# Enable xformers memory efficient attention
pipeline.enable_xformers_memory_efficient_attention()

# Enable model CPU offload
pipeline.enable_model_cpu_offload()

# Use mixed precision
pipeline = pipeline.to(torch.float16)
```

### Custom Training Loops

```python
# Custom noise scheduling
from deployment.scripts.python.noise_schedulers_and_sampling import CustomNoiseSchedulers

betas = CustomNoiseSchedulers.cosine_beta_schedule(
    num_timesteps=1000, 
    s=0.008
)

# Custom loss functions
def custom_loss(noise_pred, noise, timesteps):
    # Implement your custom loss
    base_loss = F.mse_loss(noise_pred, noise)
    # Add additional terms as needed
    return base_loss
```

### Pipeline Comparison

```python
from deployment.scripts.python.diffusion_pipelines_guide import PipelineComparison

comparison = PipelineComparison(pipeline_manager)

# Compare generation speed
speed_results = comparison.compare_generation_speed(
    "A beautiful landscape", 
    num_runs=5
)

# Compare memory usage
memory_results = comparison.compare_memory_usage()

# Print results
comparison.print_comparison_results(speed_results, memory_results)
```

## 📊 Performance Monitoring

### Training Metrics

```python
# Log metrics to WandB
if trainer.use_wandb:
    wandb.log({
        'train_loss': loss.item(),
        'learning_rate': lr_scheduler.get_last_lr()[0],
        'epoch': current_epoch,
        'global_step': global_step
    })

# Save checkpoints
trainer._save_checkpoint(epoch, metrics, is_best=True)
```

### Evaluation Metrics

```python
# Comprehensive evaluation
metrics = evaluator.evaluate_model(test_dataset)

# Save results
evaluator._save_metrics(metrics)
evaluator._save_generated_images(generated_images)

# Plot results
from deployment.scripts.python.noise_schedulers_and_sampling import SchedulerAnalysis

SchedulerAnalysis.plot_scheduler_comparison(
    comparison_data, 
    save_path="./scheduler_comparison.png"
)
```

## 🎯 Best Practices

### 1. Pipeline Selection

- **For research**: Use DDPM or DDIM with many steps
- **For production**: Use DPM-Solver or DDIM with moderate steps
- **For speed**: Use DPM-Solver variants with few steps
- **For quality**: Use DDPM or DDIM with many steps

### 2. Training Optimization

- Use learning rate 1e-5 to 1e-4 for fine-tuning
- Enable mixed precision for memory efficiency
- Use EMA for stable training
- Implement gradient clipping (1.0 is a good default)
- Use cosine learning rate scheduling with warmup

### 3. Memory Management

- Enable attention slicing for large models
- Use xformers when available
- Enable CPU offload for very large models
- Use gradient accumulation for larger effective batch sizes
- Monitor GPU memory usage

### 4. Evaluation Strategy

- Use FID for overall quality assessment
- Use LPIPS for perceptual similarity
- Use PSNR/SSIM for pixel-level comparison
- Generate multiple samples for robust evaluation
- Save generated images for visual inspection

## 🚨 Troubleshooting

### Common Issues

1. **Out of Memory (OOM)**
   ```python
   # Enable memory optimizations
   pipeline.enable_attention_slicing()
   pipeline.enable_model_cpu_offload()
   
   # Reduce batch size or image size
   config.batch_size = 1
   config.image_size = 256
   ```

2. **Slow Generation**
   ```python
   # Use faster schedulers
   scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
   pipeline.scheduler = scheduler
   
   # Reduce inference steps
   result = pipeline(prompt, num_inference_steps=20)
   ```

3. **Poor Quality**
   ```python
   # Increase inference steps
   result = pipeline(prompt, num_inference_steps=100)
   
   # Adjust guidance scale
   result = pipeline(prompt, guidance_scale=10.0)
   
   # Use better schedulers
   scheduler = DDIMScheduler.from_config(pipeline.scheduler.config)
   ```

### Performance Tips

- Use `torch.compile()` for PyTorch 2.0+ (can improve speed by 20-30%)
- Enable `torch.backends.cudnn.benchmark` for consistent input sizes
- Use `torch.backends.cuda.matmul.allow_tf32` for Ampere+ GPUs
- Profile your pipeline to identify bottlenecks

## 📁 File Structure

```
deployment/scripts/python/
├── diffusion_pipelines_guide.py      # Pipeline usage and comparison
├── diffusion_training_evaluation.py  # Training and evaluation framework
└── noise_schedulers_and_sampling.py  # Noise schedulers and sampling methods

requirements-diffusion.txt             # Dependencies
README-diffusion-models.md            # This file
```

## 🔗 Additional Resources

- [Hugging Face Diffusers Documentation](https://huggingface.co/docs/diffusers/)
- [Stable Diffusion Paper](https://arxiv.org/abs/2112.10752)
- [DDIM Paper](https://arxiv.org/abs/2010.02502)
- [DPM-Solver Paper](https://arxiv.org/abs/2206.00927)

## 🤝 Contributing

When contributing to the diffusion models implementation:

1. Follow PEP 8 style guidelines
2. Use descriptive variable names
3. Add comprehensive docstrings
4. Include error handling
5. Add unit tests for new features
6. Update this README for new functionality

## 📄 License

This implementation is part of the Blaze AI project and follows the same licensing terms.

---

**Happy Diffusion Modeling! 🎨✨**
