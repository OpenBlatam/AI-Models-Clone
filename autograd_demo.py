#!/usr/bin/env python3
"""
PYTORCH AUTOGRAD DEMONSTRATION
Simple demonstration of PyTorch's autograd for automatic differentiation
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.autograd as autograd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Custom Autograd Function
class CustomLossFunction(autograd.Function):
    """Custom autograd function for advanced loss computation"""
    
    @staticmethod
    def forward(ctx, predictions: torch.Tensor, targets: torch.Tensor, 
                alpha: torch.Tensor, beta: torch.Tensor) -> torch.Tensor:
        """Forward pass with custom loss computation"""
        ctx.save_for_backward(predictions, targets, alpha, beta)
        
        # Custom loss computation
        mse_loss = F.mse_loss(predictions, targets, reduction='none')
        l1_loss = F.l1_loss(predictions, targets, reduction='none')
        
        # Combined loss with learnable weights
        combined_loss = alpha * mse_loss + beta * l1_loss
        return combined_loss.mean()
    
    @staticmethod
    def backward(ctx, grad_output: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Backward pass with automatic gradient computation"""
        predictions, targets, alpha, beta = ctx.saved_tensors
        
        # Compute gradients for predictions
        grad_predictions = grad_output * (2 * alpha * (predictions - targets) + beta * torch.sign(predictions - targets))
        
        # Compute gradients for targets (negative of predictions gradient)
        grad_targets = -grad_predictions
        
        # Compute gradients for alpha and beta
        grad_alpha = grad_output * F.mse_loss(predictions, targets, reduction='none').mean()
        grad_beta = grad_output * F.l1_loss(predictions, targets, reduction='none').mean()
        
        return grad_predictions, grad_targets, grad_alpha, grad_beta

# Neural Network with Autograd
class AutogradNeuralNetwork(nn.Module):
    """Neural network with custom autograd functions"""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Learnable parameters for custom loss
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(0.5))
        
        # Network layers
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with autograd"""
        # First layer
        h1 = F.relu(self.fc1(x))
        h1 = self.dropout(h1)
        
        # Second layer
        h2 = F.relu(self.fc2(h1))
        h2 = self.dropout(h2)
        
        # Output layer
        output = self.fc3(h2)
        
        return output
    
    def custom_loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Custom loss function using autograd"""
        return CustomLossFunction.apply(predictions, targets, self.alpha, self.beta)

# Autograd Optimizer
class AutogradOptimizer:
    """Optimizer with custom autograd capabilities"""
    
    def __init__(self, model: nn.Module, learning_rate: float = 0.001):
        self.model = model
        self.learning_rate = learning_rate
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
    def compute_gradients(self, loss: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Compute gradients using autograd"""
        # Clear previous gradients
        self.optimizer.zero_grad()
        
        # Backward pass
        loss.backward()
        
        # Collect gradients
        gradients = {}
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                gradients[name] = param.grad.clone()
        
        return gradients
    
    def apply_gradients(self, gradients: Dict[str, torch.Tensor]):
        """Apply computed gradients"""
        for name, param in self.model.named_parameters():
            if name in gradients:
                param.grad = gradients[name]
        
        self.optimizer.step()
    
    def gradient_clipping(self, max_norm: float = 1.0):
        """Apply gradient clipping"""
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm)
    
    def compute_gradient_norms(self) -> Dict[str, float]:
        """Compute gradient norms for monitoring"""
        norms = {}
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                norms[name] = param.grad.norm().item()
        return norms

# Training Manager
class AutogradTrainingManager:
    """Manager for autograd-based training"""
    
    def __init__(self):
        self.models = {}
        self.optimizers = {}
        self.training_history = {}
        
    def create_model(self, name: str, config: Dict) -> Dict:
        """Create model with autograd capabilities"""
        model = AutogradNeuralNetwork(
            input_size=config.get("input_size", 100),
            hidden_size=config.get("hidden_size", 128),
            output_size=config.get("output_size", 10)
        )
        
        optimizer = AutogradOptimizer(model, config.get("lr", 0.001))
        
        self.models[name] = model
        self.optimizers[name] = optimizer
        
        return {
            "name": name,
            "type": "neural_network",
            "config": config,
            "parameters": sum(p.numel() for p in model.parameters()),
            "autograd_enabled": True
        }
    
    def train_step(self, name: str, data: torch.Tensor, targets: torch.Tensor) -> Dict:
        """Single training step with autograd"""
        if name not in self.models:
            raise ValueError(f"Model {name} not found")
        
        model = self.models[name]
        optimizer = self.optimizers[name]
        
        model.train()
        
        # Forward pass
        predictions = model(data)
        
        # Custom loss computation with autograd
        loss = model.custom_loss(predictions, targets)
        
        # Compute gradients using autograd
        gradients = optimizer.compute_gradients(loss)
        
        # Gradient clipping
        optimizer.gradient_clipping()
        
        # Apply gradients
        optimizer.apply_gradients(gradients)
        
        # Compute gradient norms
        gradient_norms = optimizer.compute_gradient_norms()
        
        return {
            "loss": loss.item(),
            "gradient_norms": gradient_norms,
            "autograd_computed": True,
            "alpha": model.alpha.item(),
            "beta": model.beta.item()
        }

def demonstrate_autograd():
    """Demonstrate PyTorch autograd functionality"""
    logger.info("Starting PyTorch autograd demonstration...")
    
    # Create training manager
    manager = AutogradTrainingManager()
    
    # Create model
    config = {
        "input_size": 10,
        "hidden_size": 64,
        "output_size": 5,
        "lr": 0.001
    }
    
    model_info = manager.create_model("autograd_demo", config)
    logger.info(f"Created model: {model_info}")
    
    # Generate sample data
    batch_size = 32
    input_size = config["input_size"]
    output_size = config["output_size"]
    
    data = torch.randn(batch_size, input_size)
    targets = torch.randn(batch_size, output_size)
    
    logger.info(f"Data shape: {data.shape}")
    logger.info(f"Targets shape: {targets.shape}")
    
    # Training loop
    num_epochs = 10
    training_results = []
    
    for epoch in range(num_epochs):
        result = manager.train_step("autograd_demo", data, targets)
        training_results.append(result)
        
        logger.info(f"Epoch {epoch + 1}/{num_epochs}")
        logger.info(f"  Loss: {result['loss']:.4f}")
        logger.info(f"  Alpha: {result['alpha']:.4f}")
        logger.info(f"  Beta: {result['beta']:.4f}")
        logger.info(f"  Autograd computed: {result['autograd_computed']}")
        
        # Log gradient norms
        for param_name, norm in result['gradient_norms'].items():
            logger.info(f"  {param_name} gradient norm: {norm:.4f}")
    
    logger.info("Autograd demonstration completed!")
    return training_results

def demonstrate_custom_autograd():
    """Demonstrate custom autograd function"""
    logger.info("Demonstrating custom autograd function...")
    
    # Create tensors with requires_grad=True
    x = torch.randn(5, 3, requires_grad=True)
    y = torch.randn(5, 3, requires_grad=True)
    alpha = torch.tensor(1.0, requires_grad=True)
    beta = torch.tensor(0.5, requires_grad=True)
    
    logger.info(f"Input x shape: {x.shape}")
    logger.info(f"Input y shape: {y.shape}")
    logger.info(f"Alpha: {alpha.item()}")
    logger.info(f"Beta: {beta.item()}")
    
    # Apply custom autograd function
    loss = CustomLossFunction.apply(x, y, alpha, beta)
    
    logger.info(f"Custom loss: {loss.item():.4f}")
    
    # Backward pass
    loss.backward()
    
    logger.info(f"Gradient of x: {x.grad}")
    logger.info(f"Gradient of y: {y.grad}")
    logger.info(f"Gradient of alpha: {alpha.grad}")
    logger.info(f"Gradient of beta: {beta.grad}")
    
    logger.info("Custom autograd function demonstration completed!")

def demonstrate_gradient_computation():
    """Demonstrate gradient computation with autograd"""
    logger.info("Demonstrating gradient computation...")
    
    # Create a simple function
    def simple_function(x, y):
        return x**2 + y**3
    
    # Create tensors
    x = torch.tensor(2.0, requires_grad=True)
    y = torch.tensor(3.0, requires_grad=True)
    
    # Compute function value
    z = simple_function(x, y)
    
    logger.info(f"x = {x.item()}")
    logger.info(f"y = {y.item()}")
    logger.info(f"z = x^2 + y^3 = {z.item()}")
    
    # Compute gradients
    z.backward()
    
    logger.info(f"∂z/∂x = 2x = {x.grad.item()}")
    logger.info(f"∂z/∂y = 3y^2 = {y.grad.item()}")
    
    logger.info("Gradient computation demonstration completed!")

def main():
    """Main demonstration function"""
    logger.info("=" * 50)
    logger.info("PYTORCH AUTOGRAD DEMONSTRATION")
    logger.info("=" * 50)
    
    try:
        # Demonstrate basic gradient computation
        demonstrate_gradient_computation()
        logger.info("-" * 30)
        
        # Demonstrate custom autograd function
        demonstrate_custom_autograd()
        logger.info("-" * 30)
        
        # Demonstrate neural network with autograd
        training_results = demonstrate_autograd()
        logger.info("-" * 30)
        
        logger.info("All autograd demonstrations completed successfully!")
        logger.info(f"Training completed with {len(training_results)} epochs")
        
    except Exception as e:
        logger.error(f"Error during autograd demonstration: {e}")
        raise

if __name__ == "__main__":
    main() 