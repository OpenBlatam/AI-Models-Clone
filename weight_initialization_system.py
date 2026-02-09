#!/usr/bin/env python3
"""
WEIGHT INITIALIZATION AND NORMALIZATION SYSTEM
Proper weight initialization and normalization techniques for deep learning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init
import numpy as np
import math
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Weight Initialization Techniques
class WeightInitializer:
    """Comprehensive weight initialization techniques"""
    
    @staticmethod
    def xavier_uniform_init(module: nn.Module, gain: float = 1.0):
        """Xavier/Glorot uniform initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.xavier_uniform_(module.weight, gain=gain)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def xavier_normal_init(module: nn.Module, gain: float = 1.0):
        """Xavier/Glorot normal initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.xavier_normal_(module.weight, gain=gain)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def kaiming_uniform_init(module: nn.Module, mode: str = 'fan_in', nonlinearity: str = 'relu'):
        """Kaiming/He uniform initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.kaiming_uniform_(module.weight, mode=mode, nonlinearity=nonlinearity)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def kaiming_normal_init(module: nn.Module, mode: str = 'fan_in', nonlinearity: str = 'relu'):
        """Kaiming/He normal initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.kaiming_normal_(module.weight, mode=mode, nonlinearity=nonlinearity)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def orthogonal_init(module: nn.Module, gain: float = 1.0):
        """Orthogonal initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.orthogonal_(module.weight, gain=gain)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def sparse_init(module: nn.Module, sparsity: float = 0.1, std: float = 0.01):
        """Sparse initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.sparse_(module.weight, sparsity=sparsity, std=std)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def custom_uniform_init(module: nn.Module, min_val: float = -0.1, max_val: float = 0.1):
        """Custom uniform initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.uniform_(module.weight, min_val, max_val)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def custom_normal_init(module: nn.Module, mean: float = 0.0, std: float = 0.01):
        """Custom normal initialization"""
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
            init.normal_(module.weight, mean, std)
            if module.bias is not None:
                init.zeros_(module.bias)
    
    @staticmethod
    def layer_specific_init(module: nn.Module):
        """Layer-specific initialization based on layer type"""
        if isinstance(module, nn.Linear):
            # Linear layers: Xavier uniform
            init.xavier_uniform_(module.weight)
            if module.bias is not None:
                init.zeros_(module.bias)
        elif isinstance(module, nn.Conv2d):
            # Conv2d layers: Kaiming normal
            init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
            if module.bias is not None:
                init.zeros_(module.bias)
        elif isinstance(module, nn.LSTM):
            # LSTM layers: Orthogonal for weight, zeros for bias
            for name, param in module.named_parameters():
                if 'weight' in name:
                    init.orthogonal_(param)
                elif 'bias' in name:
                    init.zeros_(param)
        elif isinstance(module, nn.Embedding):
            # Embedding layers: Normal initialization
            init.normal_(module.weight, mean=0, std=0.1)

# Normalization Techniques
class NormalizationTechniques:
    """Comprehensive normalization techniques"""
    
    @staticmethod
    def batch_norm_2d(num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        """Batch Normalization for 2D inputs"""
        return nn.BatchNorm2d(num_features, eps=eps, momentum=momentum)
    
    @staticmethod
    def batch_norm_1d(num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        """Batch Normalization for 1D inputs"""
        return nn.BatchNorm1d(num_features, eps=eps, momentum=momentum)
    
    @staticmethod
    def layer_norm(normalized_shape: Union[int, List[int]], eps: float = 1e-5):
        """Layer Normalization"""
        return nn.LayerNorm(normalized_shape, eps=eps)
    
    @staticmethod
    def group_norm(num_groups: int, num_channels: int, eps: float = 1e-5):
        """Group Normalization"""
        return nn.GroupNorm(num_groups, num_channels, eps=eps)
    
    @staticmethod
    def instance_norm_2d(num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        """Instance Normalization for 2D inputs"""
        return nn.InstanceNorm2d(num_features, eps=eps, momentum=momentum)
    
    @staticmethod
    def instance_norm_1d(num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        """Instance Normalization for 1D inputs"""
        return nn.InstanceNorm1d(num_features, eps=eps, momentum=momentum)

# Custom Normalization Layers
class CustomLayerNorm(nn.Module):
    """Custom Layer Normalization with learnable parameters"""
    
    def __init__(self, normalized_shape: Union[int, List[int]], eps: float = 1e-5):
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(normalized_shape))
        self.bias = nn.Parameter(torch.zeros(normalized_shape))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        x_norm = (x - mean) / torch.sqrt(var + self.eps)
        return self.weight * x_norm + self.bias

class AdaptiveNormalization(nn.Module):
    """Adaptive normalization that switches between different techniques"""
    
    def __init__(self, num_features: int, norm_type: str = 'batch'):
        super().__init__()
        self.num_features = num_features
        self.norm_type = norm_type
        
        if norm_type == 'batch':
            self.norm = nn.BatchNorm1d(num_features)
        elif norm_type == 'layer':
            self.norm = nn.LayerNorm(num_features)
        elif norm_type == 'instance':
            self.norm = nn.InstanceNorm1d(num_features)
        else:
            raise ValueError(f"Unknown normalization type: {norm_type}")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.norm(x)

# Neural Network with Proper Initialization and Normalization
class ProperlyInitializedNetwork(nn.Module):
    """Neural network with proper weight initialization and normalization"""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int, 
                 init_method: str = 'xavier_uniform', norm_type: str = 'batch'):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.init_method = init_method
        self.norm_type = norm_type
        
        # Network layers
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        
        # Normalization layers
        if norm_type == 'batch':
            self.norm1 = nn.BatchNorm1d(hidden_size)
            self.norm2 = nn.BatchNorm1d(hidden_size)
        elif norm_type == 'layer':
            self.norm1 = nn.LayerNorm(hidden_size)
            self.norm2 = nn.LayerNorm(hidden_size)
        elif norm_type == 'instance':
            self.norm1 = nn.InstanceNorm1d(hidden_size)
            self.norm2 = nn.InstanceNorm1d(hidden_size)
        else:
            self.norm1 = nn.Identity()
            self.norm2 = nn.Identity()
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights using specified method"""
        init_methods = {
            'xavier_uniform': WeightInitializer.xavier_uniform_init,
            'xavier_normal': WeightInitializer.xavier_normal_init,
            'kaiming_uniform': WeightInitializer.kaiming_uniform_init,
            'kaiming_normal': WeightInitializer.kaiming_normal_init,
            'orthogonal': WeightInitializer.orthogonal_init,
            'sparse': WeightInitializer.sparse_init,
            'custom_uniform': WeightInitializer.custom_uniform_init,
            'custom_normal': WeightInitializer.custom_normal_init,
            'layer_specific': WeightInitializer.layer_specific_init
        }
        
        if self.init_method in init_methods:
            for module in self.modules():
                init_methods[self.init_method](module)
        else:
            logger.warning(f"Unknown initialization method: {self.init_method}")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with normalization"""
        # First layer
        x = self.fc1(x)
        x = self.norm1(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Second layer
        x = self.fc2(x)
        x = self.norm2(x)
        x = F.relu(x)
        x = self.dropout(x)
        
        # Output layer
        x = self.fc3(x)
        
        return x

# CNN with Proper Initialization and Normalization
class ProperlyInitializedCNN(nn.Module):
    """CNN with proper weight initialization and normalization"""
    
    def __init__(self, in_channels: int = 3, num_classes: int = 1000, 
                 init_method: str = 'kaiming_normal', norm_type: str = 'batch'):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes
        self.init_method = init_method
        self.norm_type = norm_type
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        
        # Normalization layers
        if norm_type == 'batch':
            self.norm1 = nn.BatchNorm2d(64)
            self.norm2 = nn.BatchNorm2d(128)
            self.norm3 = nn.BatchNorm2d(256)
            self.norm4 = nn.BatchNorm2d(512)
        elif norm_type == 'instance':
            self.norm1 = nn.InstanceNorm2d(64)
            self.norm2 = nn.InstanceNorm2d(128)
            self.norm3 = nn.InstanceNorm2d(256)
            self.norm4 = nn.InstanceNorm2d(512)
        elif norm_type == 'group':
            self.norm1 = nn.GroupNorm(8, 64)
            self.norm2 = nn.GroupNorm(16, 128)
            self.norm3 = nn.GroupNorm(32, 256)
            self.norm4 = nn.GroupNorm(64, 512)
        else:
            self.norm1 = nn.Identity()
            self.norm2 = nn.Identity()
            self.norm3 = nn.Identity()
            self.norm4 = nn.Identity()
        
        # Pooling and classifier
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(0.5)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights using specified method"""
        init_methods = {
            'xavier_uniform': WeightInitializer.xavier_uniform_init,
            'xavier_normal': WeightInitializer.xavier_normal_init,
            'kaiming_uniform': WeightInitializer.kaiming_uniform_init,
            'kaiming_normal': WeightInitializer.kaiming_normal_init,
            'orthogonal': WeightInitializer.orthogonal_init,
            'sparse': WeightInitializer.sparse_init,
            'custom_uniform': WeightInitializer.custom_uniform_init,
            'custom_normal': WeightInitializer.custom_normal_init,
            'layer_specific': WeightInitializer.layer_specific_init
        }
        
        if self.init_method in init_methods:
            for module in self.modules():
                init_methods[self.init_method](module)
        else:
            logger.warning(f"Unknown initialization method: {self.init_method}")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with normalization"""
        # Convolutional layers with normalization
        x = self.conv1(x)
        x = self.norm1(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        
        x = self.conv2(x)
        x = self.norm2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        
        x = self.conv3(x)
        x = self.norm3(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        
        x = self.conv4(x)
        x = self.norm4(x)
        x = F.relu(x)
        x = self.pool(x)
        
        # Classifier
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.classifier(x)
        
        return x

# Weight Analysis and Monitoring
class WeightAnalyzer:
    """Analyze and monitor weight distributions"""
    
    @staticmethod
    def analyze_weight_distribution(model: nn.Module) -> Dict[str, Dict[str, float]]:
        """Analyze weight distribution for each layer"""
        analysis = {}
        
        for name, module in model.named_modules():
            if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
                weights = module.weight.data
                
                analysis[name] = {
                    'mean': weights.mean().item(),
                    'std': weights.std().item(),
                    'min': weights.min().item(),
                    'max': weights.max().item(),
                    'norm': weights.norm().item(),
                    'sparsity': (weights == 0).float().mean().item()
                }
        
        return analysis
    
    @staticmethod
    def compute_gradient_norms(model: nn.Module) -> Dict[str, float]:
        """Compute gradient norms for each layer"""
        norms = {}
        
        for name, param in model.named_parameters():
            if param.grad is not None:
                norms[name] = param.grad.norm().item()
        
        return norms
    
    @staticmethod
    def check_weight_initialization(model: nn.Module) -> Dict[str, bool]:
        """Check if weights are properly initialized"""
        checks = {}
        
        for name, module in model.named_modules():
            if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d)):
                weights = module.weight.data
                
                # Check for zero weights (except bias)
                zero_weights = (weights == 0).float().mean().item()
                checks[f"{name}_zero_weights"] = zero_weights < 0.1
                
                # Check for reasonable weight range
                weight_range = weights.max().item() - weights.min().item()
                checks[f"{name}_reasonable_range"] = 0.01 < weight_range < 10.0
                
                # Check for NaN or Inf
                has_nan = torch.isnan(weights).any().item()
                has_inf = torch.isinf(weights).any().item()
                checks[f"{name}_finite"] = not (has_nan or has_inf)
        
        return checks

# Training Manager with Initialization and Normalization
class InitializationTrainingManager:
    """Manager for training with proper initialization and normalization"""
    
    def __init__(self):
        self.models = {}
        self.optimizers = {}
        self.analyzers = {}
        
    def create_model(self, name: str, model_type: str, config: Dict) -> Dict:
        """Create model with proper initialization and normalization"""
        if model_type == 'mlp':
            model = ProperlyInitializedNetwork(
                input_size=config.get("input_size", 100),
                hidden_size=config.get("hidden_size", 128),
                output_size=config.get("output_size", 10),
                init_method=config.get("init_method", "xavier_uniform"),
                norm_type=config.get("norm_type", "batch")
            )
        elif model_type == 'cnn':
            model = ProperlyInitializedCNN(
                in_channels=config.get("in_channels", 3),
                num_classes=config.get("num_classes", 1000),
                init_method=config.get("init_method", "kaiming_normal"),
                norm_type=config.get("norm_type", "batch")
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        optimizer = torch.optim.Adam(model.parameters(), lr=config.get("lr", 0.001))
        analyzer = WeightAnalyzer()
        
        self.models[name] = model
        self.optimizers[name] = optimizer
        self.analyzers[name] = analyzer
        
        return {
            "name": name,
            "type": model_type,
            "config": config,
            "parameters": sum(p.numel() for p in model.parameters()),
            "init_method": config.get("init_method", "xavier_uniform"),
            "norm_type": config.get("norm_type", "batch")
        }
    
    def train_step(self, name: str, data: torch.Tensor, targets: torch.Tensor) -> Dict:
        """Single training step with analysis"""
        if name not in self.models:
            raise ValueError(f"Model {name} not found")
        
        model = self.models[name]
        optimizer = self.optimizers[name]
        analyzer = self.analyzers[name]
        
        model.train()
        
        # Forward pass
        predictions = model(data)
        loss = F.cross_entropy(predictions, targets)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Analyze weights and gradients
        weight_analysis = analyzer.analyze_weight_distribution(model)
        gradient_norms = analyzer.compute_gradient_norms(model)
        init_checks = analyzer.check_weight_initialization(model)
        
        return {
            "loss": loss.item(),
            "weight_analysis": weight_analysis,
            "gradient_norms": gradient_norms,
            "init_checks": init_checks
        }

def demonstrate_initialization_techniques():
    """Demonstrate different initialization techniques"""
    logger.info("Demonstrating weight initialization techniques...")
    
    # Create sample data
    batch_size = 32
    input_size = 100
    hidden_size = 128
    output_size = 10
    
    data = torch.randn(batch_size, input_size)
    targets = torch.randint(0, output_size, (batch_size,))
    
    # Test different initialization methods
    init_methods = ['xavier_uniform', 'xavier_normal', 'kaiming_uniform', 
                   'kaiming_normal', 'orthogonal', 'custom_uniform', 'custom_normal']
    
    results = {}
    
    for init_method in init_methods:
        logger.info(f"Testing {init_method} initialization...")
        
        # Create model with specific initialization
        model = ProperlyInitializedNetwork(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=output_size,
            init_method=init_method,
            norm_type='batch'
        )
        
        # Analyze initial weights
        analyzer = WeightAnalyzer()
        weight_analysis = analyzer.analyze_weight_distribution(model)
        init_checks = analyzer.check_weight_initialization(model)
        
        results[init_method] = {
            'weight_analysis': weight_analysis,
            'init_checks': init_checks
        }
        
        logger.info(f"  Weight analysis: {weight_analysis}")
        logger.info(f"  Init checks: {init_checks}")
    
    return results

def demonstrate_normalization_techniques():
    """Demonstrate different normalization techniques"""
    logger.info("Demonstrating normalization techniques...")
    
    # Create sample data
    batch_size = 32
    input_size = 100
    hidden_size = 128
    output_size = 10
    
    data = torch.randn(batch_size, input_size)
    targets = torch.randint(0, output_size, (batch_size,))
    
    # Test different normalization methods
    norm_types = ['batch', 'layer', 'instance']
    
    results = {}
    
    for norm_type in norm_types:
        logger.info(f"Testing {norm_type} normalization...")
        
        # Create model with specific normalization
        model = ProperlyInitializedNetwork(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=output_size,
            init_method='xavier_uniform',
            norm_type=norm_type
        )
        
        # Training manager
        manager = InitializationTrainingManager()
        model_info = manager.create_model(f"test_{norm_type}", "mlp", {
            "input_size": input_size,
            "hidden_size": hidden_size,
            "output_size": output_size,
            "init_method": "xavier_uniform",
            "norm_type": norm_type
        })
        
        # Train for a few steps
        training_results = []
        for step in range(5):
            result = manager.train_step(f"test_{norm_type}", data, targets)
            training_results.append(result)
        
        results[norm_type] = training_results
        
        logger.info(f"  Training completed with {len(training_results)} steps")
        logger.info(f"  Final loss: {training_results[-1]['loss']:.4f}")
    
    return results

def main():
    """Main demonstration function"""
    logger.info("=" * 60)
    logger.info("WEIGHT INITIALIZATION AND NORMALIZATION SYSTEM")
    logger.info("=" * 60)
    
    try:
        # Demonstrate initialization techniques
        init_results = demonstrate_initialization_techniques()
        logger.info("-" * 40)
        
        # Demonstrate normalization techniques
        norm_results = demonstrate_normalization_techniques()
        logger.info("-" * 40)
        
        logger.info("All demonstrations completed successfully!")
        logger.info(f"Initialization methods tested: {len(init_results)}")
        logger.info(f"Normalization methods tested: {len(norm_results)}")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {e}")
        raise

if __name__ == "__main__":
    main() 