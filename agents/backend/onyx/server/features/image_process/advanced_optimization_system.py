import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
from PIL import Image
import os
import time
import logging
from typing import Optional, Tuple, Dict, Any
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedOptimizationSystem:
    """
    Advanced optimization system with GPU utilization and mixed precision training
    """
    
    def __init__(self, device: str = 'auto'):
        self.device = self._setup_device(device)
        self.scaler = GradScaler()
        self.optimization_config = {
            'mixed_precision': True,
            'gradient_accumulation_steps': 4,
            'max_grad_norm': 1.0,
            'learning_rate': 1e-4,
            'weight_decay': 1e-5,
            'scheduler_patience': 10,
            'scheduler_factor': 0.5
        }
        
        logger.info(f"Initialized AdvancedOptimizationSystem on device: {self.device}")
        if torch.cuda.is_available():
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    def _setup_device(self, device: str) -> torch.device:
        """Setup optimal device with fallbacks"""
        if device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda'
                # Set memory fraction and optimization
                torch.cuda.set_per_process_memory_fraction(0.95)
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
            elif torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        
        return torch.device(device)
    
    def optimize_model(self, model: nn.Module, train_loader: DataLoader, 
                      val_loader: Optional[DataLoader] = None,
                      epochs: int = 100) -> Dict[str, Any]:
        """
        Optimize model with advanced techniques
        """
        model = model.to(self.device)
        
        # Setup optimizer with weight decay
        optimizer = optim.AdamW(
            model.parameters(),
            lr=self.optimization_config['learning_rate'],
            weight_decay=self.optimization_config['weight_decay']
        )
        
        # Setup learning rate scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            patience=self.optimization_config['scheduler_patience'],
            factor=self.optimization_config['scheduler_factor'],
            verbose=True
        )
        
        # Training loop with mixed precision
        best_val_loss = float('inf')
        training_history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rate': []
        }
        
        for epoch in range(epochs):
            # Training phase
            train_loss = self._train_epoch(
                model, train_loader, optimizer, epoch
            )
            
            # Validation phase
            val_loss = None
            if val_loader:
                val_loss = self._validate_epoch(model, val_loader, epoch)
                scheduler.step(val_loss)
                
                # Save best model
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    self._save_checkpoint(model, optimizer, epoch, val_loss)
            
            # Update history
            training_history['train_loss'].append(train_loss)
            if val_loss:
                training_history['val_loss'].append(val_loss)
            training_history['learning_rate'].append(optimizer.param_groups[0]['lr'])
            
            # Memory cleanup
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
                gc.collect()
        
        return training_history
    
    def _train_epoch(self, model: nn.Module, train_loader: DataLoader, 
                     optimizer: optim.Optimizer, epoch: int) -> float:
        """Train for one epoch with mixed precision"""
        model.train()
        total_loss = 0.0
        num_batches = len(train_loader)
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            # Mixed precision forward pass
            with autocast(enabled=self.optimization_config['mixed_precision']):
                output = model(data)
                loss = F.mse_loss(output, target)
                loss = loss / self.optimization_config['gradient_accumulation_steps']
            
            # Backward pass with gradient scaling
            self.scaler.scale(loss).backward()
            
            # Gradient accumulation
            if (batch_idx + 1) % self.optimization_config['gradient_accumulation_steps'] == 0:
                # Unscale gradients and clip
                self.scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), 
                    self.optimization_config['max_grad_norm']
                )
                
                # Optimizer step
                self.scaler.step(optimizer)
                self.scaler.update()
                optimizer.zero_grad()
            
            total_loss += loss.item() * self.optimization_config['gradient_accumulation_steps']
            
            # Progress logging
            if batch_idx % 10 == 0:
                logger.info(f'Epoch {epoch}, Batch {batch_idx}/{num_batches}, '
                          f'Loss: {loss.item():.6f}')
        
        avg_loss = total_loss / num_batches
        logger.info(f'Epoch {epoch} - Average Training Loss: {avg_loss:.6f}')
        return avg_loss
    
    def _validate_epoch(self, model: nn.Module, val_loader: DataLoader, 
                        epoch: int) -> float:
        """Validate for one epoch"""
        model.eval()
        total_loss = 0.0
        num_batches = len(val_loader)
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                with autocast(enabled=self.optimization_config['mixed_precision']):
                    output = model(data)
                    loss = F.mse_loss(output, target)
                
                total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        logger.info(f'Epoch {epoch} - Average Validation Loss: {avg_loss:.6f}')
        return avg_loss
    
    def _save_checkpoint(self, model: nn.Module, optimizer: optim.Optimizer, 
                         epoch: int, val_loss: float):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_loss': val_loss,
            'optimization_config': self.optimization_config
        }
        
        os.makedirs('checkpoints', exist_ok=True)
        torch.save(checkpoint, f'checkpoints/best_model_epoch_{epoch}.pth')
        logger.info(f'Checkpoint saved: epoch {epoch}, val_loss: {val_loss:.6f}')
    
    def load_checkpoint(self, model: nn.Module, checkpoint_path: str) -> int:
        """Load model checkpoint"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        epoch = checkpoint['epoch']
        logger.info(f'Checkpoint loaded from epoch {epoch}')
        return epoch
    
    def profile_memory_usage(self) -> Dict[str, Any]:
        """Profile current memory usage"""
        memory_info = {}
        
        if self.device.type == 'cuda':
            memory_info['gpu_allocated'] = torch.cuda.memory_allocated() / 1e9
            memory_info['gpu_reserved'] = torch.cuda.memory_reserved() / 1e9
            memory_info['gpu_total'] = torch.cuda.get_device_properties(0).total_memory / 1e9
        
        memory_info['cpu_memory'] = torch.cuda.memory_allocated() / 1e9 if self.device.type == 'cuda' else 0
        
        return memory_info
    
    def optimize_batch_size(self, model: nn.Module, sample_data: torch.Tensor,
                           target_memory_usage: float = 0.8) -> int:
        """Find optimal batch size for given memory constraints"""
        model.eval()
        batch_size = 1
        
        while True:
            try:
                test_batch = sample_data.repeat(batch_size, 1, 1, 1).to(self.device)
                
                with torch.no_grad():
                    with autocast(enabled=self.optimization_config['mixed_precision']):
                        _ = model(test_batch)
                
                memory_usage = self.profile_memory_usage()
                current_usage = memory_usage.get('gpu_allocated', 0) / memory_usage.get('gpu_total', 1)
                
                if current_usage > target_memory_usage:
                    break
                
                batch_size *= 2
                
                # Cleanup
                del test_batch
                if self.device.type == 'cuda':
                    torch.cuda.empty_cache()
                
            except RuntimeError as e:
                if "out of memory" in str(e):
                    break
                else:
                    raise e
        
        optimal_batch_size = max(1, batch_size // 2)
        logger.info(f'Optimal batch size: {optimal_batch_size}')
        return optimal_batch_size

# Example usage
if __name__ == "__main__":
    # Create a simple model for demonstration
    class SimpleModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
            self.conv2 = nn.Conv2d(64, 64, 3, padding=1)
            self.conv3 = nn.Conv2d(64, 3, 3, padding=1)
        
        def forward(self, x):
            x = F.relu(self.conv1(x))
            x = F.relu(self.conv2(x))
            x = self.conv3(x)
            return x
    
    # Initialize system
    opt_system = AdvancedOptimizationSystem()
    
    # Create model and dummy data
    model = SimpleModel()
    dummy_data = torch.randn(4, 3, 64, 64)
    dummy_target = torch.randn(4, 3, 64, 64)
    
    # Profile memory and find optimal batch size
    memory_info = opt_system.profile_memory_usage()
    print(f"Memory usage: {memory_info}")
    
    optimal_batch = opt_system.optimize_batch_size(model, dummy_data)
    print(f"Optimal batch size: {optimal_batch}")


