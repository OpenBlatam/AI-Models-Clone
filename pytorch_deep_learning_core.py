#!/usr/bin/env python3
"""
PyTorch Deep Learning Core System

Comprehensive deep learning implementation using PyTorch with:
- Custom nn.Module architectures
- Automatic differentiation with autograd
- GPU optimization and mixed precision training
- Production-ready model development pipeline
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast, GradScaler
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from dataclasses import dataclass
from pathlib import Path
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check CUDA availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")


@dataclass
class ModelConfig:
    """Configuration for deep learning models.
    
    Attributes:
        input_dim: Input dimension
        hidden_dims: List of hidden layer dimensions
        output_dim: Output dimension
        dropout_rate: Dropout probability
        learning_rate: Learning rate for optimization
        batch_size: Training batch size
        num_epochs: Number of training epochs
        use_mixed_precision: Whether to use mixed precision training
        gradient_clip_norm: Gradient clipping norm value
    """
    
    input_dim: int = 784
    hidden_dims: List[int] = None
    output_dim: int = 10
    dropout_rate: float = 0.2
    learning_rate: float = 1e-3
    batch_size: int = 32
    num_epochs: int = 100
    use_mixed_precision: bool = True
    gradient_clip_norm: float = 1.0
    
    def __post_init__(self):
        """Set default hidden dimensions if not provided."""
        if self.hidden_dims is None:
            self.hidden_dims = [512, 256, 128]


class CustomDataset(Dataset):
    """Custom PyTorch dataset with autograd support.
    
    This dataset provides automatic differentiation capabilities
    and supports various data types and transformations.
    """
    
    def __init__(
        self,
        data: torch.Tensor,
        targets: torch.Tensor,
        transform: Optional[callable] = None
    ):
        """Initialize the custom dataset.
        
        Args:
            data: Input data tensor
            targets: Target labels tensor
            transform: Optional data transformation
        """
        self.data = data
        self.targets = targets
        self.transform = transform
        
        # Ensure tensors require gradients for autograd
        if not self.data.requires_grad:
            self.data.requires_grad_(True)
    
    def __len__(self) -> int:
        """Return the number of samples."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get a sample and its target.
        
        Args:
            idx: Sample index
            
        Returns:
            Tuple of (data, target) with autograd support
        """
        sample = self.data[idx]
        target = self.targets[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample, target


class MultiLayerPerceptron(nn.Module):
    """Custom Multi-Layer Perceptron with autograd integration.
    
    This module demonstrates proper use of PyTorch's autograd system
    for automatic differentiation and gradient computation.
    """
    
    def __init__(self, config: ModelConfig):
        """Initialize the MLP architecture.
        
        Args:
            config: Model configuration
        """
        super().__init__()
        self.config = config
        
        # Build layer architecture
        layers = []
        prev_dim = config.input_dim
        
        for hidden_dim in config.hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(config.dropout_rate),
                nn.BatchNorm1d(hidden_dim)
            ])
            prev_dim = hidden_dim
        
        # Output layer
        layers.append(nn.Linear(prev_dim, config.output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights for better training
        self._initialize_weights()
    
    def _initialize_weights(self) -> None:
        """Initialize network weights using Xavier/Glorot initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.BatchNorm1d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with autograd support.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with gradient tracking
        """
        # Ensure input requires gradients for autograd
        if not x.requires_grad:
            x.requires_grad_(True)
        
        return self.network(x)
    
    def compute_gradients(
        self,
        x: torch.Tensor,
        target: torch.Tensor,
        loss_fn: nn.Module
    ) -> Dict[str, torch.Tensor]:
        """Compute gradients using autograd.
        
        Args:
            x: Input tensor
            target: Target tensor
            loss_fn: Loss function
            
        Returns:
            Dictionary containing gradients and loss
        """
        # Forward pass
        output = self.forward(x)
        
        # Compute loss
        loss = loss_fn(output, target)
        
        # Backward pass with autograd
        loss.backward()
        
        # Collect gradients
        gradients = {}
        for name, param in self.named_parameters():
            if param.grad is not None:
                gradients[name] = param.grad.clone()
        
        return {
            "loss": loss,
            "gradients": gradients,
            "output": output
        }


class ConvolutionalNeuralNetwork(nn.Module):
    """Custom CNN architecture with autograd support.
    
    This module implements a convolutional neural network
    with automatic differentiation capabilities.
    """
    
    def __init__(
        self,
        input_channels: int = 1,
        num_classes: int = 10,
        dropout_rate: float = 0.2
    ):
        """Initialize the CNN architecture.
        
        Args:
            input_channels: Number of input channels
            num_classes: Number of output classes
            dropout_rate: Dropout probability
        """
        super().__init__()
        
        # Convolutional layers with autograd support
        self.conv_layers = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout2d(dropout_rate)
        )
        
        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Linear(128 * 3 * 3, 512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, num_classes)
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self) -> None:
        """Initialize network weights."""
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with autograd support.
        
        Args:
            x: Input tensor of shape (batch_size, channels, height, width)
            
        Returns:
            Output tensor with gradient tracking
        """
        # Ensure input requires gradients
        if not x.requires_grad:
            x.requires_grad_(True)
        
        # Convolutional layers
        x = self.conv_layers(x)
        
        # Flatten for fully connected layers
        x = x.view(x.size(0), -1)
        
        # Fully connected layers
        x = self.fc_layers(x)
        
        return x


class TransformerModel(nn.Module):
    """Custom Transformer architecture with autograd support.
    
    This module implements a transformer model with
    self-attention mechanisms and automatic differentiation.
    """
    
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        max_seq_length: int = 512
    ):
        """Initialize the Transformer architecture.
        
        Args:
            vocab_size: Size of vocabulary
            d_model: Model dimension
            nhead: Number of attention heads
            num_layers: Number of transformer layers
            dim_feedforward: Feedforward dimension
            dropout: Dropout probability
            max_seq_length: Maximum sequence length
        """
        super().__init__()
        
        self.d_model = d_model
        self.max_seq_length = max_seq_length
        
        # Embedding layers
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(
            torch.randn(max_seq_length, d_model)
        )
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )
        
        # Output projection
        self.output_projection = nn.Linear(d_model, vocab_size)
        
        self._initialize_weights()
    
    def _initialize_weights(self) -> None:
        """Initialize transformer weights."""
        nn.init.normal_(self.embedding.weight, mean=0, std=0.02)
        nn.init.normal_(self.pos_encoding, mean=0, std=0.02)
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass with autograd support.
        
        Args:
            x: Input tensor of shape (batch_size, seq_length)
            mask: Optional attention mask
            
        Returns:
            Output tensor with gradient tracking
        """
        # Ensure input requires gradients
        if not x.requires_grad:
            x.requires_grad_(True)
        
        batch_size, seq_length = x.shape
        
        # Embedding and positional encoding
        x = self.embedding(x) * np.sqrt(self.d_model)
        x = x + self.pos_encoding[:seq_length, :].unsqueeze(0)
        
        # Transformer encoding
        x = self.transformer_encoder(x, src_key_padding_mask=mask)
        
        # Output projection
        x = self.output_projection(x)
        
        return x


class DeepLearningTrainer:
    """Comprehensive deep learning trainer with autograd integration.
    
    This trainer handles model training, validation, and optimization
    with full support for PyTorch's autograd system.
    """
    
    def __init__(
        self,
        model: nn.Module,
        config: ModelConfig,
        device: torch.device = DEVICE
    ):
        """Initialize the trainer.
        
        Args:
            model: PyTorch model
            config: Training configuration
            device: Device for training
        """
        self.model = model.to(device)
        self.config = config
        self.device = device
        
        # Optimizer with autograd support
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=config.learning_rate
        )
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
            verbose=True
        )
        
        # Mixed precision training
        self.scaler = GradScaler() if config.use_mixed_precision else None
        
        # Training history
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }
        
        logger.info(f"Trainer initialized on device: {device}")
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        loss_fn: nn.Module
    ) -> Dict[str, float]:
        """Train for one epoch with autograd.
        
        Args:
            train_loader: Training data loader
            loss_fn: Loss function
            
        Returns:
            Dictionary with training metrics
        """
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass with mixed precision
            if self.config.use_mixed_precision and self.scaler:
                with autocast():
                    output = self.model(data)
                    loss = loss_fn(output, target)
                
                # Backward pass with gradient scaling
                self.scaler.scale(loss).backward()
                
                # Gradient clipping
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip_norm
                )
                
                # Optimizer step with scaling
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                # Standard training without mixed precision
                output = self.model(data)
                loss = loss_fn(output, target)
                
                # Backward pass with autograd
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip_norm
                )
                
                self.optimizer.step()
            
            # Update metrics
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
            
            # Log progress
            if batch_idx % 100 == 0:
                logger.info(
                    f"Batch {batch_idx}/{len(train_loader)}: "
                    f"Loss: {loss.item():.4f}, "
                    f"Acc: {100. * correct / total:.2f}%"
                )
        
        return {
            'loss': total_loss / len(train_loader),
            'accuracy': 100. * correct / total
        }
    
    def validate(
        self,
        val_loader: DataLoader,
        loss_fn: nn.Module
    ) -> Dict[str, float]:
        """Validate the model.
        
        Args:
            val_loader: Validation data loader
            loss_fn: Loss function
            
        Returns:
            Dictionary with validation metrics
        """
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                if self.config.use_mixed_precision and self.scaler:
                    with autocast():
                        output = self.model(data)
                        loss = loss_fn(output, target)
                else:
                    output = self.model(data)
                    loss = loss_fn(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)
        
        return {
            'loss': total_loss / len(val_loader),
            'accuracy': 100. * correct / total
        }
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        loss_fn: nn.Module
    ) -> Dict[str, List[float]]:
        """Complete training loop with autograd.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            loss_fn: Loss function
            
        Returns:
            Training history
        """
        logger.info("Starting training...")
        
        for epoch in range(self.config.num_epochs):
            logger.info(f"Epoch {epoch + 1}/{self.config.num_epochs}")
            
            # Training phase
            train_metrics = self.train_epoch(train_loader, loss_fn)
            
            # Validation phase
            val_metrics = self.validate(val_loader, loss_fn)
            
            # Update learning rate
            self.scheduler.step(val_metrics['loss'])
            
            # Store history
            self.history['train_loss'].append(train_metrics['loss'])
            self.history['train_acc'].append(train_metrics['accuracy'])
            self.history['val_loss'].append(val_metrics['loss'])
            self.history['val_acc'].append(val_metrics['accuracy'])
            
            # Log epoch results
            logger.info(
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.2f}%, "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Val Acc: {val_metrics['accuracy']:.2f}%"
            )
        
        logger.info("Training completed!")
        return self.history
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model.
        
        Args:
            filepath: Path to save the model
        """
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'history': self.history
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load a trained model.
        
        Args:
            filepath: Path to the saved model
        """
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.history = checkpoint['history']
        logger.info(f"Model loaded from {filepath}")


def create_sample_data(
    num_samples: int = 1000,
    input_dim: int = 784,
    num_classes: int = 10
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Create sample data for demonstration.
    
    Args:
        num_samples: Number of samples
        input_dim: Input dimension
        num_classes: Number of classes
        
    Returns:
        Tuple of (data, targets) with autograd support
    """
    # Generate random data
    data = torch.randn(num_samples, input_dim)
    targets = torch.randint(0, num_classes, (num_samples,))
    
    # Enable autograd
    data.requires_grad_(True)
    
    return data, targets


def demonstrate_autograd() -> None:
    """Demonstrate PyTorch's autograd capabilities."""
    logger.info("Demonstrating PyTorch autograd...")
    
    # Create sample data
    data, targets = create_sample_data()
    
    # Create model and configuration
    config = ModelConfig()
    model = MultiLayerPerceptron(config)
    
    # Create dataset and dataloader
    dataset = CustomDataset(data, targets)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Create trainer
    trainer = DeepLearningTrainer(model, config)
    
    # Define loss function
    loss_fn = nn.CrossEntropyLoss()
    
    # Train the model
    history = trainer.train(dataloader, dataloader, loss_fn)
    
    # Save the model
    trainer.save_model("trained_model.pth")
    
    logger.info("Autograd demonstration completed!")


if __name__ == "__main__":
    demonstrate_autograd() 