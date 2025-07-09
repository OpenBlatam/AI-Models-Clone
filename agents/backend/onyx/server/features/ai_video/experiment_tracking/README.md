# Experiment Tracking and Model Checkpointing System

A comprehensive experiment tracking and model checkpointing system for AI video generation experiments, supporting WandB, TensorBoard, custom logging, and advanced checkpoint management.

## Features

- **Multi-platform tracking** - WandB, TensorBoard, and custom logging
- **Video-specific metrics** - PSNR, SSIM, LPIPS, FID, Inception Score
- **Advanced checkpointing** - Versioning, compression, metadata tracking
- **Performance monitoring** - GPU/CPU utilization, memory usage, throughput
- **Experiment comparison** - Easy comparison of different experiments
- **Data visualization** - Automatic plotting and analysis
- **Artifact management** - Save and track model outputs, samples, videos
- **Distributed support** - Multi-GPU and multi-node training

## Quick Start

### 1. Basic Experiment Tracking

```python
from experiment_tracking import setup_experiment_tracking

# Set up tracking system
tracker, metrics, checkpoint_mgr = setup_experiment_tracking(
    "my_experiment",
    use_wandb=True,
    use_tensorboard=True
)

# Use in training loop
for step in range(1000):
    loss = train_step(model, batch)
    
    # Log metrics
    tracker.log_metrics({"loss": loss}, step)
    
    # Save checkpoint
    if step % 100 == 0:
        checkpoint_mgr.save_checkpoint(
            model=model,
            optimizer=optimizer,
            metrics={"loss": loss},
            step=step
        )

# Close tracker
tracker.close()
```

### 2. Video-Specific Tracking

```python
from experiment_tracking import create_video_experiment_tracker

# Set up video tracking
tracker, video_metrics, checkpoint_mgr = create_video_experiment_tracker(
    "video_generation",
    use_wandb=True
)

# Log video generation metrics
video_metrics.log_video_metrics(
    psnr=25.5,
    ssim=0.85,
    lpips=0.12,
    generation_time=2.5,
    step=step
)
```

### 3. Performance Monitoring

```python
from experiment_tracking import create_performance_monitor

# Create performance monitor
perf_monitor = create_performance_monitor(metrics)

# Monitor during training
for step in range(1000):
    # Training logic
    loss = train_step(model, batch)
    
    # Check performance every 100 steps
    if step % 100 == 0:
        perf_monitor.check_performance(step)
```

## Components

### Experiment Tracker

The main experiment tracking class that handles logging to multiple platforms.

```python
from experiment_tracking import ExperimentTracker, ExperimentConfig

# Create configuration
config = ExperimentConfig(
    experiment_name="my_experiment",
    project_name="ai_video_generation",
    use_wandb=True,
    use_tensorboard=True,
    log_frequency=100,
    save_frequency=1000
)

# Create tracker
tracker = ExperimentTracker(config)

# Log metrics
tracker.log_metrics({"loss": 0.5, "accuracy": 0.85}, step=100)

# Log configuration
tracker.log_config({"learning_rate": 1e-4, "batch_size": 8})

# Save artifacts
tracker.save_artifact("model.pth", "trained_model", "model")

# Log samples
tracker.log_samples([image1, image2], ["sample1", "sample2"], step=100)

# Log videos
tracker.log_video("output.mp4", "generated_video", step=100)
```

### Metrics Tracker

Dedicated metrics tracking with statistics and visualization.

```python
from experiment_tracking import MetricsTracker, MetricDefinition

# Create metrics tracker
metrics = MetricsTracker()

# Register metrics
metrics.register_metric(MetricDefinition(
    name="loss",
    metric_type="scalar",
    description="Training Loss",
    lower_is_better=True
))

# Log metrics
metrics.log_metrics({"loss": 0.5, "accuracy": 0.85}, step=100, epoch=1)

# Get statistics
stats = metrics.get_metric_statistics("loss")
print(f"Loss stats: {stats}")

# Get moving average
moving_avg = metrics.get_moving_average("loss", window_size=50)

# Export metrics
metrics.export_metrics("metrics.json", "json")

# Plot metrics
metrics.plot_metric("loss", "loss_plot.png")
```

### Video Metrics Tracker

Specialized tracker for video generation metrics.

```python
from experiment_tracking import VideoMetricsTracker

# Create video metrics tracker
video_metrics = VideoMetricsTracker(metrics)

# Log video generation metrics
video_metrics.log_video_metrics(
    psnr=25.5,           # Peak Signal-to-Noise Ratio
    ssim=0.85,           # Structural Similarity Index
    lpips=0.12,          # Learned Perceptual Image Patch Similarity
    fid=15.2,            # Fréchet Inception Distance
    inception_score=8.5, # Inception Score
    generation_time=2.5, # Generation time in seconds
    memory_usage=2048,   # GPU memory usage in MB
    fps=30.0,            # Frames per second
    video_length=64,     # Number of frames
    quality_score=0.92,  # Overall quality score
    step=100,
    epoch=1
)

# Get video quality summary
quality_summary = video_metrics.get_video_quality_summary()
print(f"Video quality: {quality_summary}")
```

### Checkpoint Manager

Advanced checkpoint management with versioning and compression.

```python
from experiment_tracking import CheckpointManager, CheckpointConfig

# Create checkpoint manager
config = CheckpointConfig(
    checkpoint_dir="checkpoints",
    save_frequency=1000,
    max_checkpoints=5,
    use_compression=True,
    primary_metric="val_loss"
)

checkpoint_mgr = CheckpointManager(config)

# Save checkpoint
checkpoint_path = checkpoint_mgr.save_checkpoint(
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    metrics={"loss": 0.5, "val_loss": 0.6},
    epoch=10,
    step=1000,
    config={"learning_rate": 1e-4},
    tags=["best_model", "production"],
    notes="Best model so far"
)

# Load checkpoint
checkpoint_data = checkpoint_mgr.load_checkpoint(
    checkpoint_path,
    model,
    optimizer,
    scheduler,
    device="cuda"
)

# Load best checkpoint
best_data = checkpoint_mgr.load_best_checkpoint(
    model,
    optimizer,
    scheduler,
    device="cuda"
)

# List checkpoints
checkpoints = checkpoint_mgr.list_checkpoints()
for checkpoint in checkpoints:
    print(f"{checkpoint.checkpoint_id}: Step {checkpoint.step}")

# Get checkpoint summary
summary = checkpoint_mgr.get_checkpoint_summary()
print(f"Checkpoint summary: {summary}")
```

### Performance Monitor

Monitor system performance during training.

```python
from experiment_tracking import PerformanceMonitor

# Create performance monitor
perf_monitor = PerformanceMonitor(metrics)

# Monitor during training
for step in range(1000):
    # Training logic
    loss = train_step(model, batch)
    
    # Check performance every 100 steps
    if step % 100 == 0:
        perf_monitor.check_performance(step)
```

## Integration with Training Scripts

### Basic Integration

```python
from experiment_tracking import log_training_step

# Set up tracking
tracker, metrics, checkpoint_mgr = setup_experiment_tracking("my_experiment")

# Training loop
for step in range(1000):
    loss = train_step(model, batch)
    
    # Log training step
    log_training_step(
        tracker=tracker,
        metrics_tracker=metrics,
        checkpoint_manager=checkpoint_mgr,
        model=model,
        optimizer=optimizer,
        loss=loss,
        step=step,
        epoch=step // 100,
        additional_metrics={"accuracy": accuracy},
        save_checkpoint=(step % 100 == 0)
    )
```

### Advanced Integration with Video Generation

```python
from experiment_tracking import create_video_experiment_tracker, log_video_generation

# Set up video tracking
tracker, video_metrics, checkpoint_mgr = create_video_experiment_tracker("video_experiment")

# Training loop
for step in range(1000):
    # Training
    loss = train_step(model, batch)
    
    # Log training step
    log_training_step(
        tracker=tracker,
        metrics_tracker=video_metrics.base_tracker,
        checkpoint_manager=checkpoint_mgr,
        model=model,
        optimizer=optimizer,
        loss=loss,
        step=step
    )
    
    # Generate and evaluate video every 100 steps
    if step % 100 == 0:
        video = generate_video(model, prompt)
        metrics = evaluate_video(video, reference)
        
        # Log video metrics
        log_video_generation(
            video_metrics_tracker=video_metrics,
            psnr=metrics["psnr"],
            ssim=metrics["ssim"],
            lpips=metrics["lpips"],
            generation_time=metrics["time"],
            step=step
        )
```

## Configuration

### Experiment Configuration

```python
from experiment_tracking import ExperimentConfig

config = ExperimentConfig(
    # Basic settings
    experiment_name="my_experiment",
    project_name="ai_video_generation",
    run_id="run_001",
    description="Training diffusion model for video generation",
    tags=["diffusion", "video", "research"],
    
    # Tracking tools
    use_wandb=True,
    use_tensorboard=True,
    use_custom_logging=True,
    
    # Logging settings
    log_frequency=100,
    save_frequency=1000,
    eval_frequency=500,
    
    # Checkpoint settings
    checkpoint_dir="checkpoints",
    save_best_only=True,
    max_checkpoints=5,
    checkpoint_metrics=["loss", "val_loss"],
    
    # Artifact settings
    save_artifacts=True,
    artifact_dir="artifacts",
    save_config=True,
    save_samples=True,
    save_model=True
)
```

### Checkpoint Configuration

```python
from experiment_tracking import CheckpointConfig

config = CheckpointConfig(
    # Directory settings
    checkpoint_dir="checkpoints",
    backup_dir="checkpoint_backups",
    
    # Checkpoint settings
    save_frequency=1000,
    save_best_only=True,
    max_checkpoints=5,
    max_backups=10,
    
    # Metrics for best checkpoint selection
    primary_metric="val_loss",
    secondary_metrics=["loss", "accuracy"],
    
    # Compression and optimization
    use_compression=True,
    compression_level=6,
    remove_optimizer_state=False,
    
    # Validation
    validate_checkpoints=True,
    verify_checksum=True,
    
    # Distributed settings
    is_distributed=False,
    local_rank=0,
    world_size=1
)
```

## Metrics and Visualization

### Available Metrics

#### Training Metrics
- `loss` - Training loss
- `val_loss` - Validation loss
- `accuracy` - Model accuracy
- `learning_rate` - Current learning rate
- `gradient_norm` - Gradient norm
- `epoch` - Current epoch

#### Video Quality Metrics
- `psnr` - Peak Signal-to-Noise Ratio
- `ssim` - Structural Similarity Index
- `lpips` - Learned Perceptual Image Patch Similarity
- `fid` - Fréchet Inception Distance
- `inception_score` - Inception Score
- `quality_score` - Overall quality score

#### Performance Metrics
- `gpu_utilization` - GPU utilization percentage
- `gpu_memory_used` - GPU memory usage in MB
- `gpu_memory_total` - Total GPU memory in MB
- `cpu_utilization` - CPU utilization percentage
- `memory_usage` - System memory usage in MB
- `training_time` - Training time in seconds
- `throughput` - Samples per second

### Visualization

```python
# Plot single metric
metrics.plot_metric("loss", "loss_plot.png")

# Plot all metrics
metrics.plot_all_metrics("metric_plots")

# Export metrics for external visualization
metrics.export_metrics("metrics.json", "json")
metrics.export_metrics("metrics.csv", "csv")
```

## Experiment Comparison

### Compare Multiple Experiments

```python
from experiment_tracking import get_experiment_summary

# Run multiple experiments
experiments = []
for lr in [1e-4, 5e-5, 2e-4]:
    tracker, metrics, checkpoint_mgr = setup_experiment_tracking(f"lr_{lr}")
    
    # Training logic
    for step in range(1000):
        loss = train_step(model, batch)
        log_training_step(tracker, metrics, checkpoint_mgr, model, optimizer, loss, step)
    
    # Get summary
    summary = get_experiment_summary(tracker, metrics, checkpoint_mgr)
    experiments.append({"lr": lr, "summary": summary})
    
    tracker.close()

# Compare experiments
for exp in experiments:
    print(f"LR {exp['lr']}: Best loss = {exp['summary']['metrics']['loss']['statistics']['min']:.4f}")
```

### Export and Analyze

```python
from experiment_tracking import export_experiment_data

# Export all experiment data
export_experiment_data(tracker, metrics, checkpoint_mgr, "experiment_exports")

# This creates:
# - experiment_exports/metrics.json
# - experiment_exports/experiment_summary.json
# - experiment_exports/checkpoints.json
```

## Best Practices

### 1. Experiment Organization

```python
# Use descriptive experiment names
experiment_name = "diffusion_video_512x512_1000steps"

# Add tags for easy filtering
tags = ["diffusion", "video", "high_res", "research"]

# Include configuration in description
description = f"Training diffusion model with {config['num_steps']} steps"
```

### 2. Checkpoint Management

```python
# Save checkpoints regularly
save_frequency = 1000  # Every 1000 steps

# Keep only the best checkpoints
save_best_only = True
max_checkpoints = 5

# Use compression to save space
use_compression = True
compression_level = 6
```

### 3. Metrics Tracking

```python
# Log comprehensive metrics
metrics = {
    "loss": loss,
    "val_loss": val_loss,
    "learning_rate": current_lr,
    "gradient_norm": grad_norm,
    "epoch": epoch
}

# Log video-specific metrics
video_metrics = {
    "psnr": psnr,
    "ssim": ssim,
    "lpips": lpips,
    "generation_time": gen_time
}
```

### 4. Performance Monitoring

```python
# Monitor performance regularly
if step % 100 == 0:
    perf_monitor.check_performance(step)

# Set up alerts for performance issues
if gpu_memory_used > 0.95 * gpu_memory_total:
    logger.warning("High GPU memory usage detected")
```

### 5. Data Export and Analysis

```python
# Export data regularly
if step % 1000 == 0:
    export_experiment_data(tracker, metrics, checkpoint_mgr, f"exports/step_{step}")

# Create visualizations
metrics.plot_all_metrics("plots")

# Save experiment summary
summary = get_experiment_summary(tracker, metrics, checkpoint_mgr)
with open("experiment_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
```

## Troubleshooting

### Common Issues

1. **WandB not working**
   ```bash
   # Install WandB
   pip install wandb
   
   # Login to WandB
   wandb login
   ```

2. **TensorBoard not showing data**
   ```bash
   # Start TensorBoard
   tensorboard --logdir runs
   
   # Check log directory
   ls runs/
   ```

3. **Checkpoint loading fails**
   ```python
   # Check checkpoint file exists
   import os
   if os.path.exists(checkpoint_path):
       checkpoint_data = checkpoint_mgr.load_checkpoint(checkpoint_path, model, optimizer)
   ```

4. **Memory issues**
   ```python
   # Reduce checkpoint frequency
   save_frequency = 2000
   
   # Use compression
   use_compression = True
   
   # Remove optimizer state
   remove_optimizer_state = True
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check tracker status
print(f"Tracker status: {tracker.get_experiment_summary()}")

# Verify metrics
print(f"Metrics: {metrics.get_metric_summary()}")

# Check checkpoints
print(f"Checkpoints: {checkpoint_mgr.list_checkpoints()}")
```

## Examples

See `example_usage.py` for comprehensive examples covering:

1. Basic experiment tracking
2. Video-specific metrics tracking
3. Performance monitoring
4. Checkpoint management
5. Integration with training loops
6. Experiment comparison and analysis
7. Data export and visualization

Run the examples:

```bash
cd experiment_tracking
python example_usage.py
```

## API Reference

### Core Classes

- `ExperimentTracker` - Main experiment tracking class
- `MetricsTracker` - Metrics tracking and statistics
- `VideoMetricsTracker` - Video-specific metrics
- `CheckpointManager` - Checkpoint management
- `PerformanceMonitor` - Performance monitoring

### Configuration Classes

- `ExperimentConfig` - Experiment tracking configuration
- `CheckpointConfig` - Checkpoint management configuration
- `MetricDefinition` - Metric definition and validation

### Utility Functions

- `setup_experiment_tracking()` - Set up complete tracking system
- `create_video_experiment_tracker()` - Create video-specific tracking
- `log_training_step()` - Log single training step
- `log_video_generation()` - Log video generation metrics
- `get_experiment_summary()` - Get experiment summary
- `export_experiment_data()` - Export experiment data

## Contributing

When adding new features:

1. Add new metric types to `MetricsTracker`
2. Update checkpoint metadata in `CheckpointManager`
3. Add new tracking platforms to `ExperimentTracker`
4. Include examples and documentation
5. Add tests for new functionality

## License

This experiment tracking system is part of the AI Video generation project. 