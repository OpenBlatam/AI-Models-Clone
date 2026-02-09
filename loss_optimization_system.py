#!/usr/bin/env python3
"""
LOSS FUNCTIONS AND OPTIMIZATION ALGORITHMS SYSTEM
Appropriate loss functions and optimization algorithms for deep learning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
import numpy as np
import math
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Loss Functions
class LossFunctions:
    """Comprehensive collection of loss functions"""
    
    @staticmethod
    def cross_entropy_loss(predictions: torch.Tensor, targets: torch.Tensor, 
                          weight: Optional[torch.Tensor] = None, 
                          label_smoothing: float = 0.0) -> torch.Tensor:
        """Cross Entropy Loss with optional label smoothing"""
        return F.cross_entropy(predictions, targets, weight=weight, 
                              label_smoothing=label_smoothing)
    
    @staticmethod
    def binary_cross_entropy_loss(predictions: torch.Tensor, targets: torch.Tensor,
                                 weight: Optional[torch.Tensor] = None,
                                 pos_weight: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Binary Cross Entropy Loss"""
        return F.binary_cross_entropy_with_logits(predictions, targets, weight=weight, 
                                                 pos_weight=pos_weight)
    
    @staticmethod
    def mse_loss(predictions: torch.Tensor, targets: torch.Tensor, 
                 reduction: str = 'mean') -> torch.Tensor:
        """Mean Squared Error Loss"""
        return F.mse_loss(predictions, targets, reduction=reduction)
    
    @staticmethod
    def mae_loss(predictions: torch.Tensor, targets: torch.Tensor,
                 reduction: str = 'mean') -> torch.Tensor:
        """Mean Absolute Error Loss"""
        return F.l1_loss(predictions, targets, reduction=reduction)
    
    @staticmethod
    def huber_loss(predictions: torch.Tensor, targets: torch.Tensor,
                   delta: float = 1.0, reduction: str = 'mean') -> torch.Tensor:
        """Huber Loss - robust to outliers"""
        return F.huber_loss(predictions, targets, delta=delta, reduction=reduction)
    
    @staticmethod
    def smooth_l1_loss(predictions: torch.Tensor, targets: torch.Tensor,
                       beta: float = 1.0, reduction: str = 'mean') -> torch.Tensor:
        """Smooth L1 Loss - combines MSE and MAE"""
        return F.smooth_l1_loss(predictions, targets, beta=beta, reduction=reduction)
    
    @staticmethod
    def kl_divergence_loss(predictions: torch.Tensor, targets: torch.Tensor,
                          reduction: str = 'mean') -> torch.Tensor:
        """KL Divergence Loss"""
        return F.kl_div(F.log_softmax(predictions, dim=1), targets, reduction=reduction)
    
    @staticmethod
    def cosine_embedding_loss(input1: torch.Tensor, input2: torch.Tensor,
                             targets: torch.Tensor, margin: float = 0.0,
                             reduction: str = 'mean') -> torch.Tensor:
        """Cosine Embedding Loss"""
        return F.cosine_embedding_loss(input1, input2, targets, margin=margin, 
                                     reduction=reduction)
    
    @staticmethod
    def triplet_loss(anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor,
                     margin: float = 1.0, p: int = 2, eps: float = 1e-6) -> torch.Tensor:
        """Triplet Loss for metric learning"""
        pos_dist = torch.norm(anchor - positive, p=p, dim=1)
        neg_dist = torch.norm(anchor - negative, p=p, dim=1)
        loss = torch.clamp(pos_dist - neg_dist + margin, min=0.0)
        return loss.mean()
    
    @staticmethod
    def focal_loss(predictions: torch.Tensor, targets: torch.Tensor,
                   alpha: float = 1.0, gamma: float = 2.0) -> torch.Tensor:
        """Focal Loss for handling class imbalance"""
        ce_loss = F.cross_entropy(predictions, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = alpha * (1 - pt) ** gamma * ce_loss
        return focal_loss.mean()
    
    @staticmethod
    def dice_loss(predictions: torch.Tensor, targets: torch.Tensor,
                  smooth: float = 1e-6) -> torch.Tensor:
        """Dice Loss for segmentation tasks"""
        predictions = torch.sigmoid(predictions)
        intersection = (predictions * targets).sum()
        dice_coeff = (2. * intersection + smooth) / (predictions.sum() + targets.sum() + smooth)
        return 1 - dice_coeff
    
    @staticmethod
    def iou_loss(predictions: torch.Tensor, targets: torch.Tensor,
                 smooth: float = 1e-6) -> torch.Tensor:
        """IoU Loss for segmentation tasks"""
        predictions = torch.sigmoid(predictions)
        intersection = (predictions * targets).sum()
        union = predictions.sum() + targets.sum() - intersection
        iou = (intersection + smooth) / (union + smooth)
        return 1 - iou

# Custom Loss Functions
class CustomLossFunctions:
    """Custom loss functions for specific use cases"""
    
    @staticmethod
    def combined_loss(predictions: torch.Tensor, targets: torch.Tensor,
                     alpha: float = 0.5, beta: float = 0.5) -> torch.Tensor:
        """Combined loss that adapts to the task type"""
        # Check if this is a classification task (targets are integers)
        if targets.dtype in [torch.int32, torch.int64, torch.long]:
            # Classification task - use cross-entropy
            ce_loss = F.cross_entropy(predictions, targets)
            # For classification, we can't use MSE, so we'll use a different combination
            # Use focal loss as the second component
            focal_loss = LossFunctions.focal_loss(predictions, targets)
            return alpha * ce_loss + beta * focal_loss
        else:
            # Regression task - use MSE and MAE
            mse_loss = F.mse_loss(predictions, targets)
            mae_loss = F.l1_loss(predictions, targets)
            return alpha * mse_loss + beta * mae_loss
    
    @staticmethod
    def weighted_mse_loss(predictions: torch.Tensor, targets: torch.Tensor,
                         weights: torch.Tensor) -> torch.Tensor:
        """Weighted MSE Loss"""
        squared_diff = (predictions - targets) ** 2
        weighted_loss = weights * squared_diff
        return weighted_loss.mean()
    
    @staticmethod
    def adaptive_loss(predictions: torch.Tensor, targets: torch.Tensor,
                     threshold: float = 1.0) -> torch.Tensor:
        """Adaptive loss that switches between MSE and MAE"""
        diff = torch.abs(predictions - targets)
        mse_mask = diff < threshold
        mae_mask = diff >= threshold
        
        mse_loss = (diff ** 2 * mse_mask).mean()
        mae_loss = (diff * mae_mask).mean()
        
        return mse_loss + mae_loss
    
    @staticmethod
    def contrastive_loss(features1: torch.Tensor, features2: torch.Tensor,
                        labels: torch.Tensor, margin: float = 1.0) -> torch.Tensor:
        """Contrastive Loss for similarity learning"""
        distance = torch.norm(features1 - features2, dim=1)
        positive_loss = labels * distance ** 2
        negative_loss = (1 - labels) * torch.clamp(margin - distance, min=0) ** 2
        return (positive_loss + negative_loss).mean()

# Optimization Algorithms
class OptimizationAlgorithms:
    """Comprehensive collection of optimization algorithms"""
    
    @staticmethod
    def sgd_optimizer(model: nn.Module, lr: float = 0.01, momentum: float = 0.0,
                      weight_decay: float = 0.0, nesterov: bool = False) -> optim.SGD:
        """Stochastic Gradient Descent"""
        return optim.SGD(model.parameters(), lr=lr, momentum=momentum,
                        weight_decay=weight_decay, nesterov=nesterov)
    
    @staticmethod
    def adam_optimizer(model: nn.Module, lr: float = 0.001, betas: Tuple[float, float] = (0.9, 0.999),
                      eps: float = 1e-8, weight_decay: float = 0.0, amsgrad: bool = False) -> optim.Adam:
        """Adam Optimizer"""
        return optim.Adam(model.parameters(), lr=lr, betas=betas, eps=eps,
                         weight_decay=weight_decay, amsgrad=amsgrad)
    
    @staticmethod
    def adamw_optimizer(model: nn.Module, lr: float = 0.001, betas: Tuple[float, float] = (0.9, 0.999),
                       eps: float = 1e-8, weight_decay: float = 0.01) -> optim.AdamW:
        """AdamW Optimizer with decoupled weight decay"""
        return optim.AdamW(model.parameters(), lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
    
    @staticmethod
    def rmsprop_optimizer(model: nn.Module, lr: float = 0.01, alpha: float = 0.99,
                         eps: float = 1e-8, momentum: float = 0.0, centered: bool = False) -> optim.RMSprop:
        """RMSprop Optimizer"""
        return optim.RMSprop(model.parameters(), lr=lr, alpha=alpha, eps=eps,
                            momentum=momentum, centered=centered)
    
    @staticmethod
    def adagrad_optimizer(model: nn.Module, lr: float = 0.01, lr_decay: float = 0.0,
                         weight_decay: float = 0.0, eps: float = 1e-10) -> optim.Adagrad:
        """Adagrad Optimizer"""
        return optim.Adagrad(model.parameters(), lr=lr, lr_decay=lr_decay,
                            weight_decay=weight_decay, eps=eps)
    
    @staticmethod
    def adadelta_optimizer(model: nn.Module, lr: float = 1.0, rho: float = 0.9,
                          eps: float = 1e-6, weight_decay: float = 0.0) -> optim.Adadelta:
        """Adadelta Optimizer"""
        return optim.Adadelta(model.parameters(), lr=lr, rho=rho, eps=eps, weight_decay=weight_decay)
    
    @staticmethod
    def rmsprop_adam_optimizer(model: nn.Module, lr: float = 0.001, betas: Tuple[float, float] = (0.9, 0.999),
                              eps: float = 1e-8, weight_decay: float = 0.0) -> optim.RAdam:
        """RAdam Optimizer (Rectified Adam)"""
        return optim.RAdam(model.parameters(), lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
    
    @staticmethod
    def lion_optimizer(model: nn.Module, lr: float = 0.0001, betas: Tuple[float, float] = (0.9, 0.99),
                      weight_decay: float = 0.01):
        """Lion Optimizer - Note: Requires torch>=2.0.0"""
        try:
            return optim.Lion(model.parameters(), lr=lr, betas=betas, weight_decay=weight_decay)
        except AttributeError:
            logger.warning("Lion optimizer not available in this PyTorch version, using AdamW instead")
            return optim.AdamW(model.parameters(), lr=lr, betas=betas, weight_decay=weight_decay)

# Learning Rate Schedulers
class LearningRateSchedulers:
    """Comprehensive collection of learning rate schedulers"""
    
    @staticmethod
    def step_scheduler(optimizer: optim.Optimizer, step_size: int, gamma: float = 0.1) -> lr_scheduler.StepLR:
        """Step Learning Rate Scheduler"""
        return lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=gamma)
    
    @staticmethod
    def exponential_scheduler(optimizer: optim.Optimizer, gamma: float) -> lr_scheduler.ExponentialLR:
        """Exponential Learning Rate Scheduler"""
        return lr_scheduler.ExponentialLR(optimizer, gamma=gamma)
    
    @staticmethod
    def cosine_scheduler(optimizer: optim.Optimizer, T_max: int, eta_min: float = 0.0) -> lr_scheduler.CosineAnnealingLR:
        """Cosine Annealing Learning Rate Scheduler"""
        return lr_scheduler.CosineAnnealingLR(optimizer, T_max=T_max, eta_min=eta_min)
    
    @staticmethod
    def cosine_warmup_scheduler(optimizer: optim.Optimizer, warmup_steps: int, max_steps: int) -> lr_scheduler.CosineAnnealingWarmRestarts:
        """Cosine Annealing with Warm Restarts"""
        return lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=warmup_steps, T_mult=2)
    
    @staticmethod
    def reduce_on_plateau_scheduler(optimizer: optim.Optimizer, mode: str = 'min', factor: float = 0.1,
                                  patience: int = 10) -> lr_scheduler.ReduceLROnPlateau:
        """Reduce Learning Rate on Plateau"""
        return lr_scheduler.ReduceLROnPlateau(optimizer, mode=mode, factor=factor,
                                             patience=patience)
    
    @staticmethod
    def one_cycle_scheduler(optimizer: optim.Optimizer, max_lr: float, epochs: int,
                           steps_per_epoch: int) -> lr_scheduler.OneCycleLR:
        """One Cycle Learning Rate Scheduler"""
        return lr_scheduler.OneCycleLR(optimizer, max_lr=max_lr, epochs=epochs,
                                     steps_per_epoch=steps_per_epoch)
    
    @staticmethod
    def linear_warmup_scheduler(optimizer: optim.Optimizer, warmup_steps: int,
                               total_steps: int) -> lr_scheduler.LinearLR:
        """Linear Warmup Scheduler"""
        return lr_scheduler.LinearLR(optimizer, start_factor=0.1, end_factor=1.0,
                                   total_iters=warmup_steps)

# Custom Optimizers
class CustomOptimizers:
    """Custom optimization algorithms"""
    
    class AdaBeliefOptimizer(optim.Optimizer):
        """AdaBelief Optimizer implementation"""
        
        def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-16,
                     weight_decay=0, amsgrad=False, rectify=True):
            if not 0.0 <= lr:
                raise ValueError(f"Invalid learning rate: {lr}")
            if not 0.0 <= eps:
                raise ValueError(f"Invalid epsilon value: {eps}")
            if not 0.0 <= betas[0] < 1.0:
                raise ValueError(f"Invalid beta parameter at index 0: {betas[0]}")
            if not 0.0 <= betas[1] < 1.0:
                raise ValueError(f"Invalid beta parameter at index 1: {betas[1]}")
            if not 0.0 <= weight_decay:
                raise ValueError(f"Invalid weight_decay value: {weight_decay}")
            
            defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, amsgrad=amsgrad)
            super().__init__(params, defaults)
            self.rectify = rectify
        
        def step(self, closure=None):
            loss = None
            if closure is not None:
                loss = closure()
            
            for group in self.param_groups:
                for p in group['params']:
                    if p.grad is None:
                        continue
                    
                    grad = p.grad.data
                    if grad.is_sparse:
                        raise RuntimeError('AdaBelief does not support sparse gradients')
                    
                    state = self.state[p]
                    
                    if len(state) == 0:
                        state['step'] = 0
                        state['exp_avg'] = torch.zeros_like(p.data)
                        state['exp_avg_sq'] = torch.zeros_like(p.data)
                        if group['amsgrad']:
                            state['max_exp_avg_sq'] = torch.zeros_like(p.data)
                    
                    exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                    if group['amsgrad']:
                        max_exp_avg_sq = state['max_exp_avg_sq']
                    beta1, beta2 = group['betas']
                    
                    state['step'] += 1
                    bias_correction1 = 1 - beta1 ** state['step']
                    bias_correction2 = 1 - beta2 ** state['step']
                    
                    if group['weight_decay'] != 0:
                        grad = grad.add(p.data, alpha=group['weight_decay'])
                    
                    exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                    exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
                    
                    if group['amsgrad']:
                        torch.max(max_exp_avg_sq, exp_avg_sq, out=max_exp_avg_sq)
                        denom = max_exp_avg_sq.sqrt().add_(group['eps'])
                    else:
                        denom = exp_avg_sq.sqrt().add_(group['eps'])
                    
                    step_size = group['lr'] / bias_correction1
                    bias_correction2_sqrt = math.sqrt(bias_correction2)
                    
                    if self.rectify:
                        rect = math.sqrt((state['step'] - 1) * (state['step'] - 2))
                        if rect > 0:
                            step_size = step_size * rect / bias_correction2_sqrt
                    
                    p.data.addcdiv_(exp_avg, denom, value=-step_size)
            
            return loss

# Loss and Optimizer Manager
class LossOptimizerManager:
    """Manager for loss functions and optimization algorithms"""
    
    def __init__(self):
        self.loss_functions = {}
        self.optimizers = {}
        self.schedulers = {}
        self.training_history = {}
    
    def register_loss_function(self, name: str, loss_func: Callable, **kwargs):
        """Register a loss function"""
        self.loss_functions[name] = (loss_func, kwargs)
        logger.info(f"Registered loss function: {name}")
    
    def register_optimizer(self, name: str, optimizer_func: Callable, **kwargs):
        """Register an optimizer"""
        self.optimizers[name] = (optimizer_func, kwargs)
        logger.info(f"Registered optimizer: {name}")
    
    def create_optimizer(self, name: str, model: nn.Module) -> optim.Optimizer:
        """Create optimizer by name"""
        if name not in self.optimizers:
            raise ValueError(f"Optimizer {name} not found")
        
        optimizer_func, kwargs = self.optimizers[name]
        return optimizer_func(model, **kwargs)
    
    def compute_loss(self, name: str, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Compute loss by name"""
        if name not in self.loss_functions:
            raise ValueError(f"Loss function {name} not found")
        
        loss_func, kwargs = self.loss_functions[name]
        return loss_func(predictions, targets, **kwargs)
    
    def train_step(self, model: nn.Module, optimizer: optim.Optimizer, 
                   loss_name: str, data: torch.Tensor, targets: torch.Tensor) -> Dict:
        """Single training step"""
        model.train()
        
        # Forward pass
        predictions = model(data)
        loss = self.compute_loss(loss_name, predictions, targets)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        return {
            "loss": loss.item(),
            "predictions": predictions.detach(),
            "targets": targets
        }
    
    def evaluate_model(self, model: nn.Module, loss_name: str, 
                      data: torch.Tensor, targets: torch.Tensor) -> Dict:
        """Evaluate model performance"""
        model.eval()
        
        with torch.no_grad():
            predictions = model(data)
            loss = self.compute_loss(loss_name, predictions, targets)
            
            # Additional metrics
            if loss_name in ['cross_entropy_loss', 'binary_cross_entropy_loss']:
                accuracy = (predictions.argmax(dim=1) == targets).float().mean().item()
            else:
                accuracy = None
            
            return {
                "loss": loss.item(),
                "accuracy": accuracy,
                "predictions": predictions,
                "targets": targets
            }

# Neural Network for Testing
class TestNetwork(nn.Module):
    """Simple neural network for testing loss functions and optimizers"""
    
    def __init__(self, input_size: int = 100, hidden_size: int = 128, output_size: int = 10):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)
        
        # Initialize weights
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.xavier_uniform_(self.fc3.weight)
        nn.init.zeros_(self.fc1.bias)
        nn.init.zeros_(self.fc2.bias)
        nn.init.zeros_(self.fc3.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

def demonstrate_loss_functions():
    """Demonstrate different loss functions"""
    logger.info("Demonstrating loss functions...")
    
    # Create sample data
    batch_size = 32
    input_size = 100
    output_size = 10
    
    data = torch.randn(batch_size, input_size)
    targets = torch.randint(0, output_size, (batch_size,))
    targets_onehot = F.one_hot(targets, num_classes=output_size).float()
    
    # Create models for different tasks
    classification_model = TestNetwork(input_size, 128, output_size)
    regression_model = nn.Sequential(
        nn.Linear(input_size, 128),
        nn.ReLU(),
        nn.Linear(128, input_size)  # Output same size as input for regression
    )
    
    # Test different loss functions
    loss_tests = [
        ("cross_entropy", LossFunctions.cross_entropy_loss, classification_model, data, targets),
        ("focal", LossFunctions.focal_loss, classification_model, data, targets),
        ("mse", LossFunctions.mse_loss, regression_model, data, torch.randn_like(data)),
        ("mae", LossFunctions.mae_loss, regression_model, data, torch.randn_like(data)),
        ("huber", LossFunctions.huber_loss, regression_model, data, torch.randn_like(data)),
        ("smooth_l1", LossFunctions.smooth_l1_loss, regression_model, data, torch.randn_like(data)),
        ("combined", CustomLossFunctions.combined_loss, regression_model, data, torch.randn_like(data)),
        ("adaptive", CustomLossFunctions.adaptive_loss, regression_model, data, torch.randn_like(data))
    ]
    
    results = {}
    
    for name, loss_func, model, input_data, target_data in loss_tests:
        logger.info(f"Testing {name} loss...")
        
        predictions = model(input_data)
        loss_value = loss_func(predictions, target_data)
        
        results[name] = {
            "loss_value": loss_value.item(),
            "loss_type": name
        }
        
        logger.info(f"  {name} loss: {loss_value.item():.4f}")
    
    return results

def demonstrate_optimizers():
    """Demonstrate different optimization algorithms"""
    logger.info("Demonstrating optimization algorithms...")
    
    # Create sample data
    batch_size = 32
    input_size = 100
    output_size = 10
    
    data = torch.randn(batch_size, input_size)
    targets = torch.randint(0, output_size, (batch_size,))
    
    # Test different optimizers
    optimizer_tests = [
        ("sgd", OptimizationAlgorithms.sgd_optimizer, {"lr": 0.01, "momentum": 0.9}),
        ("adam", OptimizationAlgorithms.adam_optimizer, {"lr": 0.001}),
        ("adamw", OptimizationAlgorithms.adamw_optimizer, {"lr": 0.001, "weight_decay": 0.01}),
        ("rmsprop", OptimizationAlgorithms.rmsprop_optimizer, {"lr": 0.01}),
        ("adagrad", OptimizationAlgorithms.adagrad_optimizer, {"lr": 0.01}),
        ("adadelta", OptimizationAlgorithms.adadelta_optimizer, {"lr": 1.0}),
        ("radam", OptimizationAlgorithms.rmsprop_adam_optimizer, {"lr": 0.001}),
        ("lion", OptimizationAlgorithms.lion_optimizer, {"lr": 0.0001})
    ]
    
    results = {}
    
    for name, optimizer_func, kwargs in optimizer_tests:
        logger.info(f"Testing {name} optimizer...")
        
        # Create fresh model for each optimizer
        model = TestNetwork(input_size, 128, output_size)
        optimizer = optimizer_func(model, **kwargs)
        
        # Train for a few steps
        training_losses = []
        for step in range(10):
            model.train()
            predictions = model(data)
            loss = F.cross_entropy(predictions, targets)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            training_losses.append(loss.item())
        
        results[name] = {
            "initial_loss": training_losses[0],
            "final_loss": training_losses[-1],
            "loss_reduction": training_losses[0] - training_losses[-1],
            "training_curve": training_losses
        }
        
        logger.info(f"  {name}: Initial={training_losses[0]:.4f}, Final={training_losses[-1]:.4f}")
    
    return results

def demonstrate_schedulers():
    """Demonstrate different learning rate schedulers"""
    logger.info("Demonstrating learning rate schedulers...")
    
    # Create sample data
    batch_size = 32
    input_size = 100
    output_size = 10
    
    data = torch.randn(batch_size, input_size)
    targets = torch.randint(0, output_size, (batch_size,))
    
    # Test different schedulers
    scheduler_tests = [
        ("step", LearningRateSchedulers.step_scheduler, {"step_size": 5, "gamma": 0.5}),
        ("exponential", LearningRateSchedulers.exponential_scheduler, {"gamma": 0.95}),
        ("cosine", LearningRateSchedulers.cosine_scheduler, {"T_max": 20, "eta_min": 0.001}),
        ("reduce_on_plateau", LearningRateSchedulers.reduce_on_plateau_scheduler, {"patience": 3}),
        ("one_cycle", LearningRateSchedulers.one_cycle_scheduler, {"max_lr": 0.01, "epochs": 1, "steps_per_epoch": 20})
    ]
    
    results = {}
    
    for name, scheduler_func, kwargs in scheduler_tests:
        logger.info(f"Testing {name} scheduler...")
        
        # Create fresh model and optimizer
        model = TestNetwork(input_size, 128, output_size)
        optimizer = optim.Adam(model.parameters(), lr=0.01)
        scheduler = scheduler_func(optimizer, **kwargs)
        
        # Train and track learning rates
        lr_history = []
        loss_history = []
        
        for step in range(20):
            model.train()
            predictions = model(data)
            loss = F.cross_entropy(predictions, targets)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Step scheduler (except for reduce_on_plateau)
            if name != "reduce_on_plateau":
                scheduler.step()
            else:
                scheduler.step(loss)
            
            lr_history.append(optimizer.param_groups[0]['lr'])
            loss_history.append(loss.item())
        
        results[name] = {
            "initial_lr": lr_history[0],
            "final_lr": lr_history[-1],
            "lr_history": lr_history,
            "loss_history": loss_history
        }
        
        logger.info(f"  {name}: LR {lr_history[0]:.6f} -> {lr_history[-1]:.6f}")
    
    return results

def demonstrate_loss_optimizer_manager():
    """Demonstrate the LossOptimizerManager"""
    logger.info("Demonstrating LossOptimizerManager...")
    
    # Create manager
    manager = LossOptimizerManager()
    
    # Register loss functions
    manager.register_loss_function("cross_entropy", LossFunctions.cross_entropy_loss)
    manager.register_loss_function("focal", LossFunctions.focal_loss, alpha=1.0, gamma=2.0)
    manager.register_loss_function("combined", CustomLossFunctions.combined_loss, alpha=0.7, beta=0.3)
    
    # Register optimizers
    manager.register_optimizer("adam", OptimizationAlgorithms.adam_optimizer, lr=0.001)
    manager.register_optimizer("adamw", OptimizationAlgorithms.adamw_optimizer, lr=0.001, weight_decay=0.01)
    manager.register_optimizer("sgd", OptimizationAlgorithms.sgd_optimizer, lr=0.01, momentum=0.9)
    
    # Create model and data
    model = TestNetwork(100, 128, 10)
    data = torch.randn(32, 100)
    targets = torch.randint(0, 10, (32,))
    
    # Test different combinations
    combinations = [
        ("cross_entropy", "adam"),
        ("focal", "adamw"),
        ("combined", "sgd")
    ]
    
    results = {}
    
    for loss_name, optimizer_name in combinations:
        logger.info(f"Testing {loss_name} + {optimizer_name}...")
        
        # Create fresh model
        model = TestNetwork(100, 128, 10)
        optimizer = manager.create_optimizer(optimizer_name, model)
        
        # Train for a few steps
        training_results = []
        for step in range(5):
            result = manager.train_step(model, optimizer, loss_name, data, targets)
            training_results.append(result)
        
        # Evaluate
        eval_result = manager.evaluate_model(model, loss_name, data, targets)
        
        results[f"{loss_name}_{optimizer_name}"] = {
            "training_losses": [r["loss"] for r in training_results],
            "final_loss": training_results[-1]["loss"],
            "eval_loss": eval_result["loss"],
            "eval_accuracy": eval_result["accuracy"]
        }
        
        logger.info(f"  Final training loss: {training_results[-1]['loss']:.4f}")
        if eval_result["accuracy"] is not None:
            logger.info(f"  Evaluation accuracy: {eval_result['accuracy']:.4f}")
    
    return results

def main():
    """Main demonstration function"""
    logger.info("=" * 60)
    logger.info("LOSS FUNCTIONS AND OPTIMIZATION ALGORITHMS SYSTEM")
    logger.info("=" * 60)
    
    try:
        # Demonstrate loss functions
        loss_results = demonstrate_loss_functions()
        logger.info("-" * 40)
        
        # Demonstrate optimizers
        optimizer_results = demonstrate_optimizers()
        logger.info("-" * 40)
        
        # Demonstrate schedulers
        scheduler_results = demonstrate_schedulers()
        logger.info("-" * 40)
        
        # Demonstrate manager
        manager_results = demonstrate_loss_optimizer_manager()
        logger.info("-" * 40)
        
        logger.info("All demonstrations completed successfully!")
        logger.info(f"Loss functions tested: {len(loss_results)}")
        logger.info(f"Optimizers tested: {len(optimizer_results)}")
        logger.info(f"Schedulers tested: {len(scheduler_results)}")
        logger.info(f"Manager combinations tested: {len(manager_results)}")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {e}")
        raise

if __name__ == "__main__":
    main() 