from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Function, Variable
import torch.autograd.profiler as profiler
from typing import List, Tuple, Optional, Dict, Any, Union
import numpy as np
import time
import warnings
from typing import Any, List, Dict, Optional
import logging
import asyncio
#!/usr/bin/env python3
"""
Enhanced Autograd System for PyTorch Models

This module demonstrates advanced usage of PyTorch's autograd system including:
- Custom gradient functions
- Gradient hooks and monitoring
- Automatic differentiation with custom operations
- Gradient clipping and normalization
- Advanced autograd features
- Memory-efficient gradient computation
"""



class CustomGradientFunction(Function):
    """Custom gradient function demonstrating autograd capabilities."""
    
    @staticmethod
    def forward(ctx, input_tensor, scale_factor=1.0) -> Any:
        """Forward pass with custom computation."""
        ctx.scale_factor = scale_factor
        ctx.save_for_backward(input_tensor)
        
        # Custom forward computation
        output = torch.tanh(input_tensor * scale_factor)
        return output
    
    @staticmethod
    def backward(ctx, grad_output) -> Any:
        """Backward pass with custom gradient computation."""
        input_tensor, = ctx.saved_tensors
        scale_factor = ctx.scale_factor
        
        # Custom gradient computation
        tanh_output = torch.tanh(input_tensor * scale_factor)
        grad_input = grad_output * (1 - tanh_output ** 2) * scale_factor
        
        return grad_input, None


class GradientMonitor:
    """Monitor gradients during training for debugging and optimization."""
    
    def __init__(self, model: nn.Module) -> Any:
        
    """__init__ function."""
self.model = model
        self.gradients: Dict[str, Any] = {}
        self.hooks: List[Any] = []
        self.register_hooks()
    
    def register_hooks(self) -> Any:
        """Register gradient hooks for all parameters."""
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                hook = param.register_hook(
                    lambda grad, name=name: self._gradient_hook(grad, name)
                )
                self.hooks.append(hook)
    
    def _gradient_hook(self, grad: torch.Tensor, name: str) -> Any:
        """Hook function to monitor gradients."""
        if grad is not None:
            self.gradients[name] = {
                'grad_norm': grad.norm().item(),
                'grad_mean': grad.mean().item(),
                'grad_std': grad.std().item(),
                'grad_max': grad.max().item(),
                'grad_min': grad.min().item()
            }
    
    def get_gradient_stats(self) -> Dict[str, Dict[str, float]]:
        """Get gradient statistics."""
        return self.gradients.copy()
    
    def check_gradient_health(self) -> Dict[str, Any]:
        """Check gradient health and identify potential issues."""
        stats = self.get_gradient_stats()
        
        issues: List[Any] = []
        total_norm = 0.0
        
        for name, grad_stats in stats.items():
            norm = grad_stats['grad_norm']
            total_norm += norm ** 2
            
            # Check for gradient explosion
            if norm > 10.0:
                issues.append(f"Gradient explosion in {name}: {norm:.4f}")
            
            # Check for gradient vanishing
            if norm < 1e-6:
                issues.append(f"Gradient vanishing in {name}: {norm:.4f}")
            
            # Check for NaN gradients
            if torch.isnan(torch.tensor(grad_stats['grad_mean'])):
                issues.append(f"NaN gradients in {name}")
        
        total_norm = total_norm ** 0.5
        
        return {
            'total_gradient_norm': total_norm,
            'issues': issues,
            'is_healthy': len(issues) == 0
        }
    
    def remove_hooks(self) -> Any:
        """Remove all gradient hooks."""
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()


class AutogradOptimizer:
    """Advanced optimizer with autograd features and gradient monitoring."""
    
    def __init__(
        self,
        model: nn.Module,
        optimizer_class=torch.optim.Adam,
        lr: float = 1e-3,
        gradient_clip_norm: Optional[float] = None,
        gradient_clip_value: Optional[float] = None,
        monitor_gradients: bool: bool = True
    ) -> Any:
        
    """__init__ function."""
self.model = model
        self.optimizer = optimizer_class(model.parameters(), lr=lr)
        self.gradient_clip_norm = gradient_clip_norm
        self.gradient_clip_value = gradient_clip_value
        self.monitor_gradients = monitor_gradients
        
        if monitor_gradients:
            self.gradient_monitor = GradientMonitor(model)
        else:
            self.gradient_monitor = None
    
    def step(self, loss: torch.Tensor) -> Dict[str, Any]:
        """Perform optimization step with gradient monitoring."""
        # Zero gradients
        self.optimizer.zero_grad()
        
        # Backward pass
        loss.backward()
        
        # Get gradient statistics
        gradient_stats: Dict[str, Any] = {}
        if self.gradient_monitor:
            gradient_stats = self.gradient_monitor.get_gradient_stats()
            gradient_health = self.gradient_monitor.check_gradient_health()
            gradient_stats['health'] = gradient_health
        
        # Gradient clipping
        if self.gradient_clip_norm is not None:
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), self.gradient_clip_norm
            )
        
        if self.gradient_clip_value is not None:
            torch.nn.utils.clip_grad_value_(
                self.model.parameters(), self.gradient_clip_value
            )
        
        # Optimizer step
        self.optimizer.step()
        
        return {
            'loss': loss.item(),
            'gradient_stats': gradient_stats
        }
    
    def get_parameter_gradients(self) -> Dict[str, torch.Tensor]:
        """Get gradients for all parameters."""
        gradients: Dict[str, Any] = {}
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                gradients[name] = param.grad.clone()
        return gradients


class AutogradEnhancedResNet(nn.Module):
    """ResNet with enhanced autograd features and custom gradient functions."""
    
    def __init__(
        self,
        num_classes: int = 1000,
        block_config: List[int] = [3, 4, 6, 3],
        channels: List[int] = [64, 128, 256, 512],
        bottleneck: bool = True,
        attention: bool = True,
        dropout_rate: float = 0.1,
        use_custom_gradients: bool: bool = False
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        self.num_classes = num_classes
        self.use_custom_gradients = use_custom_gradients
        
        # Initial convolution
        self.conv1 = nn.Conv2d(3, 64, 7, 2, 3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.maxpool = nn.MaxPool2d(3, 2, 1)
        
        # Residual blocks
        self.layer1 = self._make_layer(64, channels[0], block_config[0], 1, bottleneck, attention, dropout_rate)
        self.layer2 = self._make_layer(channels[0], channels[1], block_config[1], 2, bottleneck, attention, dropout_rate)
        self.layer3 = self._make_layer(channels[1], channels[2], block_config[2], 2, bottleneck, attention, dropout_rate)
        self.layer4 = self._make_layer(channels[2], channels[3], block_config[3], 2, bottleneck, attention, dropout_rate)
        
        # Global average pooling and classifier
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(channels[3], num_classes)
        
        # Initialize weights
        self._initialize_weights()
    
    def _make_layer(
        self,
        in_channels: int,
        out_channels: int,
        blocks: int,
        stride: int,
        bottleneck: bool,
        attention: bool,
        dropout_rate: float
    ) -> nn.Sequential:
        layers: List[Any] = []
        layers.append(AutogradResidualBlock(in_channels, out_channels, stride, bottleneck, attention, dropout_rate, self.use_custom_gradients))
        
        for _ in range(1, blocks):
            layers.append(AutogradResidualBlock(out_channels, out_channels, 1, bottleneck, attention, dropout_rate, self.use_custom_gradients))
        
        return nn.Sequential(*layers)
    
    def _initialize_weights(self) -> Any:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode: str: str = 'fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Enable gradient computation profiling
        with profiler.record_function("resnet_forward"):
            x = self.conv1(x)
            x = self.bn1(x)
            x = F.relu(x)
            x = self.maxpool(x)
            
            x = self.layer1(x)
            x = self.layer2(x)
            x = self.layer3(x)
            x = self.layer4(x)
            
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
            x = self.dropout(x)
            x = self.fc(x)
            
            return x
    
    def compute_gradients(self, loss: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Compute gradients with detailed monitoring."""
        self.zero_grad()
        loss.backward()
        
        gradients: Dict[str, Any] = {}
        for name, param in self.named_parameters():
            if param.grad is not None:
                gradients[name] = param.grad.clone()
        
        return gradients
    
    def gradient_norm(self) -> float:
        """Compute total gradient norm."""
        total_norm = 0.0
        for p in self.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        return total_norm ** 0.5


class AutogradResidualBlock(nn.Module):
    """Residual block with enhanced autograd features."""
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        stride: int = 1,
        bottleneck: bool = False,
        attention: bool = False,
        dropout_rate: float = 0.1,
        use_custom_gradients: bool: bool = False
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        self.bottleneck = bottleneck
        self.attention = attention
        self.use_custom_gradients = use_custom_gradients
        
        # Bottleneck design
        if bottleneck:
            mid_channels = out_channels // 4
            self.conv1 = nn.Conv2d(in_channels, mid_channels, 1, bias=False)
            self.bn1 = nn.BatchNorm2d(mid_channels)
            self.conv2 = nn.Conv2d(mid_channels, mid_channels, 3, stride, 1, bias=False)
            self.bn2 = nn.BatchNorm2d(mid_channels)
            self.conv3 = nn.Conv2d(mid_channels, out_channels, 1, bias=False)
            self.bn3 = nn.BatchNorm2d(out_channels)
        else:
            self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
            self.bn1 = nn.BatchNorm2d(out_channels)
            self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
            self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Shortcut connection
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
        
        # Attention mechanism
        if attention:
            self.attention = AutogradSelfAttention2D(out_channels, use_custom_gradients)
        else:
            self.attention = nn.Identity()
        
        # Dropout
        self.dropout = nn.Dropout(dropout_rate)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.shortcut(x)
        
        if self.bottleneck:
            out = F.relu(self.bn1(self.conv1(x)))
            out = F.relu(self.bn2(self.conv2(out)))
            out = self.bn3(self.conv3(out))
        else:
            out = F.relu(self.bn1(self.conv1(x)))
            out = self.bn2(self.conv2(out))
        
        # Apply custom gradient function if enabled
        if self.use_custom_gradients:
            out = CustomGradientFunction.apply(out, 1.0)
        
        out = self.attention(out)
        out = out + residual
        out = F.relu(out)
        out = self.dropout(out)
        
        return out


class AutogradSelfAttention2D(nn.Module):
    """2D Self-attention with enhanced autograd features."""
    
    def __init__(self, channels: int, reduction: int = 8, use_custom_gradients: bool = False) -> Any:
        
    """__init__ function."""
super().__init__()
        self.channels = channels
        self.reduction = reduction
        self.use_custom_gradients = use_custom_gradients
        
        self.query = nn.Conv2d(channels, channels // reduction, 1)
        self.key = nn.Conv2d(channels, channels // reduction, 1)
        self.value = nn.Conv2d(channels, channels, 1)
        self.gamma = nn.Parameter(torch.zeros(1))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, channels, height, width = x.size()
        
        # Generate Q, K, V
        query = self.query(x).view(batch_size, -1, height * width).permute(0, 2, 1)
        key = self.key(x).view(batch_size, -1, height * width)
        value = self.value(x).view(batch_size, -1, height * width)
        
        # Compute attention
        attention = torch.bmm(query, key)
        attention = F.softmax(attention, dim=-1)
        
        # Apply attention
        out = torch.bmm(value, attention.permute(0, 2, 1))
        out = out.view(batch_size, channels, height, width)
        
        # Apply custom gradient function if enabled
        if self.use_custom_gradients:
            out = CustomGradientFunction.apply(out, 0.5)
        
        return self.gamma * out + x


class AutogradTransformer(nn.Module):
    """Transformer with enhanced autograd features."""
    
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        d_ff: int = 2048,
        max_seq_length: int = 512,
        num_classes: int = 10,
        dropout: float = 0.1,
        use_custom_gradients: bool: bool = False
    ) -> Any:
        
    """__init__ function."""
super().__init__()
        
        self.d_model = d_model
        self.use_custom_gradients = use_custom_gradients
        
        # Embedding and positional encoding
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = AutogradPositionalEncoding(d_model, max_seq_length, use_custom_gradients)
        
        # Transformer blocks
        self.transformer_blocks = nn.ModuleList([
            AutogradTransformerBlock(d_model, num_heads, d_ff, dropout, use_custom_gradients)
            for _ in range(num_layers)
        ])
        
        # Output layers
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, num_classes)
        )
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        with profiler.record_function("transformer_forward"):
            # Embedding and positional encoding
            x = self.embedding(x) * math.sqrt(self.d_model)
            x = self.pos_encoding(x.transpose(0, 1)).transpose(0, 1)
            x = self.dropout(x)
            
            # Apply transformer blocks
            for transformer_block in self.transformer_blocks:
                x = transformer_block(x, mask)
            
            x = self.norm(x)
            
            # Global average pooling
            x = x.mean(dim=1)
            
            # Classification
            x = self.classifier(x)
            
            return x


class AutogradPositionalEncoding(nn.Module):
    """Positional encoding with enhanced autograd features."""
    
    def __init__(self, d_model: int, max_len: int = 5000, use_custom_gradients: bool = False) -> Any:
        
    """__init__ function."""
super().__init__()
        self.use_custom_gradients = use_custom_gradients
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.use_custom_gradients:
            return CustomGradientFunction.apply(x + self.pe[:x.size(0), :], 1.0)
        return x + self.pe[:x.size(0), :]


class AutogradTransformerBlock(nn.Module):
    """Transformer block with enhanced autograd features."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1, use_custom_gradients: bool = False) -> Any:
        
    """__init__ function."""
super().__init__()
        self.use_custom_gradients = use_custom_gradients
        
        self.attention = AutogradMultiHeadAttention(d_model, num_heads, dropout, use_custom_gradients)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Self-attention with residual connection
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + ff_output)
        
        return x


class AutogradMultiHeadAttention(nn.Module):
    """Multi-head attention with enhanced autograd features."""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1, use_custom_gradients: bool = False) -> Any:
        
    """__init__ function."""
super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        self.use_custom_gradients = use_custom_gradients
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.d_k)
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        batch_size = query.size(0)
        
        # Linear transformations and reshape
        Q = self.w_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Compute attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        
        # Reshape and apply output projection
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.w_o(context)
        
        # Apply custom gradient function if enabled
        if self.use_custom_gradients:
            output = CustomGradientFunction.apply(output, 0.8)
        
        return output


class AutogradTrainingManager:
    """Advanced training manager with autograd features."""
    
    def __init__(
        self,
        model: nn.Module,
        optimizer_class=torch.optim.Adam,
        lr: float = 1e-3,
        gradient_clip_norm: Optional[float] = None,
        gradient_clip_value: Optional[float] = None,
        monitor_gradients: bool = True,
        use_mixed_precision: bool: bool = False
    ) -> Any:
        
    """__init__ function."""
self.model = model
        self.optimizer = AutogradOptimizer(
            model, optimizer_class, lr, gradient_clip_norm, gradient_clip_value, monitor_gradients
        )
        self.use_mixed_precision = use_mixed_precision
        
        if use_mixed_precision:
            self.scaler = torch.cuda.amp.GradScaler()
        else:
            self.scaler = None
    
    def train_step(
        self,
        data: torch.Tensor,
        targets: torch.Tensor,
        criterion: nn.Module
    ) -> Dict[str, Any]:
        """Perform a single training step with autograd features."""
        self.model.train()
        
        # Forward pass
        if self.use_mixed_precision:
            with torch.cuda.amp.autocast():
                outputs = self.model(data)
                loss = criterion(outputs, targets)
        else:
            outputs = self.model(data)
            loss = criterion(outputs, targets)
        
        # Backward pass and optimization
        if self.scaler is not None:
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer.optimizer)
            self.scaler.update()
            self.optimizer.optimizer.zero_grad()
        else:
            step_info = self.optimizer.step(loss)
        
        return {
            'loss': loss.item(),
            'outputs': outputs,
            'gradient_stats': self.optimizer.get_parameter_gradients() if self.scaler is None else {}
        }
    
    def validate_step(
        self,
        data: torch.Tensor,
        targets: torch.Tensor,
        criterion: nn.Module
    ) -> Dict[str, Any]:
        """Perform a single validation step."""
        self.model.eval()
        
        with torch.no_grad():
            outputs = self.model(data)
            loss = criterion(outputs, targets)
        
        return {
            'loss': loss.item(),
            'outputs': outputs
        }
    
    def get_gradient_health_report(self) -> Dict[str, Any]:
        """Get comprehensive gradient health report."""
        if self.optimizer.gradient_monitor:
            return self.optimizer.gradient_monitor.check_gradient_health()
        return {'is_healthy': True, 'issues': []}


def demonstrate_autograd_features() -> Any:
    """Demonstrate various autograd features."""
    print("🚀 PyTorch Autograd Features Demonstration")
    print("=" * 60)
    
    # Create model with autograd features
    model = AutogradEnhancedResNet(
        num_classes=10,
        use_custom_gradients: bool = True
    )
    
    # Create training manager
    training_manager = AutogradTrainingManager(
        model,
        gradient_clip_norm=1.0,
        monitor_gradients=True,
        use_mixed_precision: bool = True
    )
    
    # Create sample data
    batch_size: int: int = 4
    input_data = torch.randn(batch_size, 3, 224, 224, requires_grad=True)
    targets = torch.randint(0, 10, (batch_size,))
    criterion = nn.CrossEntropyLoss()
    
    print(f"📊 Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"📊 Input shape: {input_data.shape}")
    print(f"📊 Target shape: {targets.shape}")
    
    # Demonstrate gradient computation
    print("\n🔍 Gradient Computation Demo:")
    
    # Forward pass
    outputs = model(input_data)
    loss = criterion(outputs, targets)
    
    print(f"   Loss: {loss.item():.4f}")
    print(f"   Output shape: {outputs.shape}")
    
    # Backward pass
    loss.backward()
    
    # Check gradients
    gradient_norm = model.gradient_norm()
    print(f"   Total gradient norm: {gradient_norm:.4f}")
    
    # Get gradient statistics
    gradients = model.compute_gradients(loss)
    print(f"   Number of parameter gradients: {len(gradients)}")
    
    # Demonstrate training step
    print("\n🎯 Training Step Demo:")
    step_info = training_manager.train_step(input_data, targets, criterion)
    print(f"   Training loss: {step_info['loss']:.4f}")
    
    # Get gradient health report
    health_report = training_manager.get_gradient_health_report()
    print(f"   Gradient health: {'✅ Healthy' if health_report['is_healthy'] else '❌ Issues'}")
    
    if not health_report['is_healthy']:
        print("   Issues found:")
        for issue in health_report['issues']:
            print(f"     - {issue}")
    
    # Demonstrate custom gradient function
    print("\n🔧 Custom Gradient Function Demo:")
    x = torch.randn(2, 3, requires_grad=True)
    y = CustomGradientFunction.apply(x, 2.0)
    z = y.sum()
    z.backward()
    
    print(f"   Input: {x}")
    print(f"   Output: {y}")
    print(f"   Input gradients: {x.grad}")
    
    print("\n✅ Autograd demonstration completed!")


def benchmark_autograd_performance() -> Any:
    """Benchmark autograd performance with different configurations."""
    print("\n⚡ Autograd Performance Benchmark")
    print("=" * 60)
    
    # Test configurations
    configs: List[Any] = [
        {"use_custom_gradients": False, "use_mixed_precision": False, "name": "Standard"},
        {"use_custom_gradients": True, "use_mixed_precision": False, "name": "Custom Gradients"},
        {"use_custom_gradients": False, "use_mixed_precision": True, "name": "Mixed Precision"},
        {"use_custom_gradients": True, "use_mixed_precision": True, "name": "Custom + Mixed"}
    ]
    
    batch_size: int: int = 8
    input_data = torch.randn(batch_size, 3, 224, 224)
    targets = torch.randint(0, 10, (batch_size,))
    criterion = nn.CrossEntropyLoss()
    
    results: Dict[str, Any] = {}
    
    for config in configs:
        print(f"\n🔧 Testing {config['name']} configuration:")
        
        # Create model and training manager
        model = AutogradEnhancedResNet(
            num_classes=10,
            use_custom_gradients=config['use_custom_gradients']
        )
        
        training_manager = AutogradTrainingManager(
            model,
            monitor_gradients=False,
            use_mixed_precision=config['use_mixed_precision']
        )
        
        # Warmup
        for _ in range(3):
            _ = training_manager.train_step(input_data, targets, criterion)
        
        # Benchmark
        start_time = time.time()
        for _ in range(10):
            step_info = training_manager.train_step(input_data, targets, criterion)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        results[config['name']] = {
            'avg_time': avg_time,
            'loss': step_info['loss']
        }
        
        print(f"   Average step time: {avg_time*1000:.2f} ms")
        print(f"   Final loss: {step_info['loss']:.4f}")
    
    # Compare results
    print("\n📊 Performance Comparison:")
    print(f"{'Configuration':<20} {'Time (ms)':<12} {'Loss':<10}")
    print("-" * 42)
    
    baseline_time = results['Standard']['avg_time']
    for name, result in results.items():
        speedup = baseline_time / result['avg_time']
        print(f"{name:<20} {result['avg_time']*1000:<12.2f} {result['loss']:<10.4f} ({speedup:.2f}x)")


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_autograd_features()
    benchmark_autograd_performance()
    
    print("\n🎉 Autograd enhanced models are ready for use!")
    print("\n📋 Available Features:")
    print("   ✅ Custom gradient functions")
    print("   ✅ Gradient monitoring and health checks")
    print("   ✅ Advanced autograd optimizers")
    print("   ✅ Mixed precision training")
    print("   ✅ Gradient clipping and normalization")
    print("   ✅ Performance profiling")
    print("   ✅ Memory-efficient gradient computation") 