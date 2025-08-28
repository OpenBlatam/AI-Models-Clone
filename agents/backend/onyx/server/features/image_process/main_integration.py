import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import logging
import argparse
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import time
import json

# Import our custom modules
from advanced_optimization_system import AdvancedOptimizationSystem
from advanced_loss_functions import AdvancedLossFunctions, RadioFrequencyOptimizer
from data_loader_optimized import OptimizedImageDataset, AdvancedAugmentationPipeline, create_optimized_dataloader
from performance_monitor import PerformanceMonitor, TrainingMetricsTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageProcessingModel(nn.Module):
    """
    Advanced image processing model with radio frequency optimization
    """
    
    def __init__(self, 
                 input_channels: int = 3,
                 output_channels: int = 3,
                 base_channels: int = 64,
                 num_blocks: int = 8):
        
        super().__init__()
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.base_channels = base_channels
        
        # Initial convolution
        self.initial_conv = nn.Conv2d(input_channels, base_channels, 3, padding=1)
        
        # Residual blocks
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(base_channels, base_channels) for _ in range(num_blocks)
        ])
        
        # Frequency domain processing
        self.frequency_conv = nn.Conv2d(base_channels, base_channels, 1)
        
        # Output convolution
        self.output_conv = nn.Conv2d(base_channels, output_channels, 3, padding=1)
        
        # Activation
        self.activation = nn.ReLU(inplace=True)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Initial convolution
        x = self.activation(self.initial_conv(x))
        
        # Residual blocks
        for block in self.residual_blocks:
            x = block(x)
        
        # Frequency domain enhancement
        x = self.activation(self.frequency_conv(x))
        
        # Output convolution
        x = self.output_conv(x)
        
        return x

class ResidualBlock(nn.Module):
    """Residual block with skip connection"""
    
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.activation = nn.ReLU(inplace=True)
        
        # Skip connection
        if in_channels != out_channels:
            self.skip_conv = nn.Conv2d(in_channels, out_channels, 1)
        else:
            self.skip_conv = nn.Identity()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.skip_conv(x)
        
        out = self.activation(self.conv1(x))
        out = self.conv2(out)
        
        return self.activation(out + residual)

class AdvancedImageProcessor:
    """
    Main integration class for advanced image processing
    """
    
    def __init__(self, 
                 config: Dict[str, Any],
                 device: str = 'auto'):
        
        self.config = config
        self.device = self._setup_device(device)
        
        # Initialize components
        self.optimization_system = AdvancedOptimizationSystem(device=self.device)
        self.loss_functions = AdvancedLossFunctions(device=self.device)
        self.rf_optimizer = RadioFrequencyOptimizer(device=self.device)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(
            monitor_interval=config.get('monitor_interval', 2.0),
            save_metrics=config.get('save_metrics', True)
        )
        self.training_tracker = TrainingMetricsTracker(self.performance_monitor)
        
        # Model
        self.model = None
        self.optimizer = None
        self.scheduler = None
        
        logger.info("AdvancedImageProcessor initialized")
    
    def _setup_device(self, device: str) -> torch.device:
        """Setup optimal device"""
        if device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda'
            elif torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        return torch.device(device)
    
    def setup_model(self, 
                   input_channels: int = 3,
                   output_channels: int = 3,
                   base_channels: int = 64,
                   num_blocks: int = 8):
        """Setup the image processing model"""
        
        self.model = ImageProcessingModel(
            input_channels=input_channels,
            output_channels=output_channels,
            base_channels=base_channels,
            num_blocks=num_blocks
        ).to(self.device)
        
        # Setup optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.get('learning_rate', 1e-4),
            weight_decay=self.config.get('weight_decay', 1e-5)
        )
        
        # Setup scheduler
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            patience=self.config.get('scheduler_patience', 10),
            factor=self.config.get('scheduler_factor', 0.5),
            verbose=True
        )
        
        logger.info(f"Model setup complete: {sum(p.numel() for p in self.model.parameters()):,} parameters")
    
    def setup_data(self, 
                   train_image_dir: str,
                   train_target_dir: str,
                   val_image_dir: Optional[str] = None,
                   val_target_dir: Optional[str] = None,
                   image_size: Tuple[int, int] = (256, 256),
                   batch_size: int = 16):
        """Setup training and validation data"""
        
        # Training transforms
        train_transform = AdvancedAugmentationPipeline(
            image_size=image_size,
            use_albumentations=True,
            frequency_preserving=True
        )
        
        # Validation transforms (minimal augmentation)
        val_transform = AdvancedAugmentationPipeline(
            image_size=image_size,
            use_albumentations=False,
            frequency_preserving=True
        )
        
        # Training dataset
        self.train_dataset = OptimizedImageDataset(
            image_dir=train_image_dir,
            target_dir=train_target_dir,
            transform=train_transform,
            cache_size=self.config.get('cache_size', 100),
            preload=self.config.get('preload_data', False)
        )
        
        # Training dataloader
        self.train_loader = create_optimized_dataloader(
            self.train_dataset,
            batch_size=batch_size,
            num_workers=self.config.get('num_workers', 4),
            pin_memory=True
        )
        
        # Validation dataset (if provided)
        if val_image_dir and val_target_dir:
            self.val_dataset = OptimizedImageDataset(
                image_dir=val_image_dir,
                target_dir=val_target_dir,
                transform=val_transform,
                cache_size=self.config.get('cache_size', 50),
                preload=False
            )
            
            self.val_loader = create_optimized_dataloader(
                self.val_dataset,
                batch_size=batch_size,
                num_workers=self.config.get('num_workers', 2),
                pin_memory=True
            )
        else:
            self.val_dataset = None
            self.val_loader = None
        
        logger.info(f"Data setup complete: {len(self.train_dataset)} training samples")
        if self.val_dataset:
            logger.info(f"Validation samples: {len(self.val_dataset)}")
    
    def train(self, 
              epochs: int = 100,
              save_checkpoints: bool = True,
              checkpoint_dir: str = "checkpoints"):
        """Train the model"""
        
        if self.model is None:
            raise ValueError("Model not setup. Call setup_model() first.")
        
        if self.train_loader is None:
            raise ValueError("Training data not setup. Call setup_data() first.")
        
        # Create checkpoint directory
        if save_checkpoints:
            checkpoint_path = Path(checkpoint_dir)
            checkpoint_path.mkdir(exist_ok=True)
        
        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        
        # Training loop
        best_val_loss = float('inf')
        training_history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': []
        }
        
        logger.info(f"Starting training for {epochs} epochs")
        
        for epoch in range(epochs):
            # Start epoch tracking
            self.training_tracker.start_epoch(epoch)
            
            # Training phase
            train_loss = self._train_epoch(epoch)
            
            # Validation phase
            val_loss = None
            if self.val_loader:
                val_loss = self._validate_epoch(epoch)
                self.scheduler.step(val_loss)
                
                # Save best model
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    if save_checkpoints:
                        self._save_checkpoint(epoch, val_loss, checkpoint_dir)
            
            # End epoch tracking
            epoch_metrics = {
                'train_loss': train_loss,
                'val_loss': val_loss if val_loss else train_loss
            }
            self.training_tracker.end_epoch(epoch_metrics)
            
            # Update history
            training_history['train_loss'].append(train_loss)
            if val_loss:
                training_history['val_loss'].append(val_loss)
            training_history['learning_rate'].append(self.optimizer.param_groups[0]['lr'])
            
            # Log progress
            logger.info(f"Epoch {epoch+1}/{epochs} - "
                       f"Train Loss: {train_loss:.6f}, "
                       f"Val Loss: {val_loss:.6f if val_loss else 'N/A'}, "
                       f"LR: {self.optimizer.param_groups[0]['lr']:.2e}")
            
            # Memory cleanup
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
        
        # Stop monitoring
        self.performance_monitor.stop_monitoring()
        
        # Save final metrics
        self.performance_monitor.save_metrics()
        
        logger.info("Training completed")
        return training_history
    
    def _train_epoch(self, epoch: int) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        num_batches = len(self.train_loader)
        
        for batch_idx, (images, targets) in enumerate(self.train_loader):
            images = images.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            outputs = self.model(images)
            
            # Calculate loss
            loss = self._calculate_loss(outputs, targets, images)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), 
                self.config.get('max_grad_norm', 1.0)
            )
            
            # Optimizer step
            self.optimizer.step()
            
            # Log training step
            self.training_tracker.log_training_step(
                step=batch_idx,
                loss=loss.item(),
                learning_rate=self.optimizer.param_groups[0]['lr'],
                batch_size=images.size(0)
            )
            
            total_loss += loss.item()
            
            # Progress logging
            if batch_idx % 10 == 0:
                logger.info(f'Epoch {epoch}, Batch {batch_idx}/{num_batches}, '
                          f'Loss: {loss.item():.6f}')
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def _validate_epoch(self, epoch: int) -> float:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0.0
        num_batches = len(self.val_loader)
        
        with torch.no_grad():
            for batch_idx, (images, targets) in enumerate(self.val_loader):
                images = images.to(self.device)
                targets = targets.to(self.device)
                
                # Forward pass
                outputs = self.model(images)
                
                # Calculate loss
                loss = self._calculate_loss(outputs, targets, images)
                
                # Log validation step
                self.training_tracker.log_validation_step(
                    step=batch_idx,
                    val_loss=loss.item()
                )
                
                total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def _calculate_loss(self, 
                       outputs: torch.Tensor, 
                       targets: torch.Tensor,
                       inputs: torch.Tensor) -> torch.Tensor:
        """Calculate combined loss"""
        
        # Get loss weights from config
        loss_weights = self.config.get('loss_weights', {
            'mse': 1.0,
            'frequency': 0.5,
            'ssim': 0.3,
            'edge': 0.2
        })
        
        # Calculate adaptive loss
        total_loss = self.loss_functions.adaptive_loss(
            outputs, targets, loss_weights
        )
        
        # Add radio frequency optimization loss if enabled
        if self.config.get('use_rf_loss', True):
            frequency_bands = self.config.get('frequency_bands', {
                'low': (0.0, 0.1),
                'mid': (0.1, 0.5),
                'high': (0.5, 1.0)
            })
            
            band_weights = self.config.get('band_weights', {
                'low': 1.0,
                'mid': 1.5,
                'high': 2.0
            })
            
            rf_loss = self.loss_functions.radio_frequency_optimization_loss(
                outputs, targets, frequency_bands, band_weights
            )
            
            total_loss += self.config.get('rf_loss_weight', 0.1) * rf_loss
        
        return total_loss
    
    def _save_checkpoint(self, epoch: int, val_loss: float, checkpoint_dir: str):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'val_loss': val_loss,
            'config': self.config
        }
        
        checkpoint_path = Path(checkpoint_dir) / f"best_model_epoch_{epoch}.pth"
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path: str) -> int:
        """Load model checkpoint"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        if self.model is None:
            self.setup_model()
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        epoch = checkpoint['epoch']
        logger.info(f"Checkpoint loaded from epoch {epoch}")
        return epoch
    
    def process_image(self, image_path: str, output_path: str):
        """Process a single image"""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_checkpoint() first.")
        
        # Load and preprocess image
        from PIL import Image
        import torchvision.transforms as transforms
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Preprocess
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0).to(self.device)
        
        # Process
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
        
        # Postprocess
        output_tensor = output_tensor.squeeze(0).cpu()
        output_tensor = torch.clamp(output_tensor, 0, 1)
        
        # Convert back to PIL
        output_image = transforms.ToPILImage()(output_tensor)
        
        # Save
        output_image.save(output_path)
        logger.info(f"Image processed and saved to {output_path}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'device': str(self.device),
            'model_parameters': sum(p.numel() for p in self.model.parameters()) if self.model else 0,
            'performance_metrics': self.performance_monitor.get_metrics_summary(),
            'training_metrics': self.training_tracker.get_training_summary()
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.performance_monitor:
            self.performance_monitor.stop_monitoring()
            self.performance_monitor.clear_metrics()
            self.performance_monitor.optimize_memory()
        
        if self.train_dataset:
            self.train_dataset.clear_cache()
        
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()

def main():
    """Main training script"""
    parser = argparse.ArgumentParser(description='Advanced Image Processing Training')
    
    # Model configuration
    parser.add_argument('--input_channels', type=int, default=3, help='Input channels')
    parser.add_argument('--output_channels', type=int, default=3, help='Output channels')
    parser.add_argument('--base_channels', type=int, default=64, help='Base channels')
    parser.add_argument('--num_blocks', type=int, default=8, help='Number of residual blocks')
    
    # Training configuration
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=16, help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=1e-5, help='Weight decay')
    
    # Data configuration
    parser.add_argument('--train_image_dir', type=str, required=True, help='Training image directory')
    parser.add_argument('--train_target_dir', type=str, required=True, help='Training target directory')
    parser.add_argument('--val_image_dir', type=str, help='Validation image directory')
    parser.add_argument('--val_target_dir', type=str, help='Validation target directory')
    parser.add_argument('--image_size', type=int, nargs=2, default=[256, 256], help='Image size')
    
    # System configuration
    parser.add_argument('--device', type=str, default='auto', help='Device to use')
    parser.add_argument('--num_workers', type=int, default=4, help='Number of workers')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints', help='Checkpoint directory')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'learning_rate': args.learning_rate,
        'weight_decay': args.weight_decay,
        'scheduler_patience': 10,
        'scheduler_factor': 0.5,
        'max_grad_norm': 1.0,
        'monitor_interval': 2.0,
        'save_metrics': True,
        'cache_size': 100,
        'preload_data': False,
        'num_workers': args.num_workers,
        'loss_weights': {
            'mse': 1.0,
            'frequency': 0.5,
            'ssim': 0.3,
            'edge': 0.2
        },
        'use_rf_loss': True,
        'rf_loss_weight': 0.1,
        'frequency_bands': {
            'low': (0.0, 0.1),
            'mid': (0.1, 0.5),
            'high': (0.5, 1.0)
        },
        'band_weights': {
            'low': 1.0,
            'mid': 1.5,
            'high': 2.0
        }
    }
    
    # Initialize processor
    processor = AdvancedImageProcessor(config, device=args.device)
    
    try:
        # Setup model
        processor.setup_model(
            input_channels=args.input_channels,
            output_channels=args.output_channels,
            base_channels=args.base_channels,
            num_blocks=args.num_blocks
        )
        
        # Setup data
        processor.setup_data(
            train_image_dir=args.train_image_dir,
            train_target_dir=args.train_target_dir,
            val_image_dir=args.val_image_dir,
            val_target_dir=args.val_target_dir,
            image_size=tuple(args.image_size),
            batch_size=args.batch_size
        )
        
        # Train
        history = processor.train(
            epochs=args.epochs,
            save_checkpoints=True,
            checkpoint_dir=args.checkpoint_dir
        )
        
        # Print summary
        summary = processor.get_performance_summary()
        print("\n" + "="*50)
        print("TRAINING SUMMARY")
        print("="*50)
        print(f"Device: {summary['device']}")
        print(f"Model Parameters: {summary['model_parameters']:,}")
        print(f"Final Training Loss: {history['train_loss'][-1]:.6f}")
        if history['val_loss']:
            print(f"Final Validation Loss: {history['val_loss'][-1]:.6f}")
        print("="*50)
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise
    finally:
        processor.cleanup()

if __name__ == "__main__":
    main()


