import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init
import math
from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

class EfficientAttention(nn.Module):
    """Efficient attention mechanism for spatial and channel attention"""
    
    def __init__(self, channels: int, reduction: int = 16):
        super().__init__()
        self.channels = channels
        self.reduction = reduction
        
        # Channel attention
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        
        self.channel_fc = nn.Sequential(
            nn.Conv2d(channels, channels // reduction, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels // reduction, channels, 1, bias=False)
        )
        
        # Spatial attention
        self.spatial_conv = nn.Conv2d(2, 1, kernel_size=7, padding=3, bias=False)
        self.sigmoid = nn.Sigmoid()
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Channel attention
        avg_out = self.channel_fc(self.avg_pool(x))
        max_out = self.channel_fc(self.max_pool(x))
        channel_out = self.sigmoid(avg_out + max_out)
        
        # Apply channel attention
        x = x * channel_out
        
        # Spatial attention
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        spatial_out = torch.cat([avg_out, max_out], dim=1)
        spatial_out = self.sigmoid(self.spatial_conv(spatial_out))
        
        # Apply spatial attention
        x = x * spatial_out
        
        return x

class EfficientResidualBlock(nn.Module):
    """Efficient residual block with depthwise separable convolutions"""
    
    def __init__(self, channels: int, expansion: int = 4):
        super().__init__()
        self.channels = channels
        self.expansion = expansion
        expanded_channels = channels * expansion
        
        # Depthwise separable convolution
        self.depthwise = nn.Conv2d(channels, expanded_channels, 3, padding=1, groups=channels)
        self.pointwise = nn.Conv2d(expanded_channels, channels, 1)
        
        # Batch normalization and activation
        self.bn1 = nn.BatchNorm2d(expanded_channels)
        self.bn2 = nn.BatchNorm2d(channels)
        self.activation = nn.ReLU6(inplace=True)  # ReLU6 for better quantization
        
        # Skip connection
        self.skip_conv = nn.Identity()
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                init.constant_(m.weight, 1)
                init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.skip_conv(x)
        
        # Depthwise convolution
        out = self.depthwise(x)
        out = self.bn1(out)
        out = self.activation(out)
        
        # Pointwise convolution
        out = self.pointwise(out)
        out = self.bn2(out)
        
        # Residual connection
        out = out + residual
        out = self.activation(out)
        
        return out

class MultiScaleBlock(nn.Module):
    """Multi-scale processing block with parallel paths"""
    
    def __init__(self, channels: int, scales: List[int] = [1, 2, 4]):
        super().__init__()
        self.channels = channels
        self.scales = scales
        
        # Parallel processing paths at different scales
        self.paths = nn.ModuleList()
        for scale in scales:
            if scale == 1:
                # Original scale
                path = nn.Sequential(
                    nn.Conv2d(channels, channels, 3, padding=1, bias=False),
                    nn.BatchNorm2d(channels),
                    nn.ReLU(inplace=True)
                )
            else:
                # Downsampled scale
                path = nn.Sequential(
                    nn.AvgPool2d(scale, scale),
                    nn.Conv2d(channels, channels, 3, padding=1, bias=False),
                    nn.BatchNorm2d(channels),
                    nn.ReLU(inplace=True),
                    nn.Upsample(scale_factor=scale, mode='bilinear', align_corners=False)
                )
            self.paths.append(path)
        
        # Feature fusion
        self.fusion = nn.Sequential(
            nn.Conv2d(channels * len(scales), channels, 1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True)
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                init.constant_(m.weight, 1)
                init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Process through different scales
        outputs = []
        for path in self.paths:
            outputs.append(path(x))
        
        # Concatenate and fuse
        out = torch.cat(outputs, dim=1)
        out = self.fusion(out)
        
        return out

class AdaptiveFeatureFusion(nn.Module):
    """Adaptive feature fusion with learnable weights"""
    
    def __init__(self, channels: int, num_features: int = 2):
        super().__init__()
        self.channels = channels
        self.num_features = num_features
        
        # Learnable fusion weights
        self.fusion_weights = nn.Parameter(torch.ones(num_features) / num_features)
        self.softmax = nn.Softmax(dim=0)
        
        # Feature refinement
        self.refinement = nn.Sequential(
            nn.Conv2d(channels, channels, 1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True)
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                init.constant_(m.weight, 1)
                init.constant_(m.bias, 0)
    
    def forward(self, features: List[torch.Tensor]) -> torch.Tensor:
        # Apply learnable weights
        weights = self.softmax(self.fusion_weights)
        
        # Weighted sum of features
        fused = torch.zeros_like(features[0])
        for i, feature in enumerate(features):
            fused += weights[i] * feature
        
        # Refine fused features
        out = self.refinement(fused)
        
        return out

class FrequencyEnhancementBlock(nn.Module):
    """Frequency domain enhancement block"""
    
    def __init__(self, channels: int):
        super().__init__()
        self.channels = channels
        
        # Frequency processing
        self.freq_conv = nn.Conv2d(channels, channels, 1, bias=False)
        self.bn = nn.BatchNorm2d(channels)
        self.activation = nn.ReLU(inplace=True)
        
        # High-frequency enhancement
        self.high_freq_enhance = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True)
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                init.constant_(m.weight, 1)
                init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Frequency domain processing
        freq_out = self.freq_conv(x)
        freq_out = self.bn(freq_out)
        freq_out = self.activation(freq_out)
        
        # High-frequency enhancement
        high_freq_out = self.high_freq_enhance(x)
        
        # Combine frequency and spatial information
        out = freq_out + high_freq_out
        
        return out

class OptimizedImageProcessingModel(nn.Module):
    """Optimized image processing model with advanced architecture"""
    
    def __init__(self,
                 input_channels: int = 3,
                 output_channels: int = 3,
                 base_channels: int = 64,
                 num_blocks: int = 8,
                 use_attention: bool = True,
                 use_multiscale: bool = True,
                 use_frequency: bool = True):
        
        super().__init__()
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        
        # Feature extraction
        self.initial_conv = nn.Sequential(
            nn.Conv2d(input_channels, base_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(base_channels),
            nn.ReLU(inplace=True)
        )
        
        # Multi-scale feature extraction
        if use_multiscale:
            self.multiscale_block = MultiScaleBlock(base_channels)
        else:
            self.multiscale_block = nn.Identity()
        
        # Attention mechanism
        if use_attention:
            self.attention = EfficientAttention(base_channels)
        else:
            self.attention = nn.Identity()
        
        # Efficient residual blocks
        self.residual_blocks = nn.ModuleList([
            EfficientResidualBlock(base_channels) for _ in range(num_blocks)
        ])
        
        # Frequency enhancement
        if use_frequency:
            self.frequency_block = FrequencyEnhancementBlock(base_channels)
        else:
            self.frequency_block = nn.Identity()
        
        # Adaptive feature fusion
        self.feature_fusion = AdaptiveFeatureFusion(base_channels, num_features=3)
        
        # Output processing
        self.output_conv = nn.Sequential(
            nn.Conv2d(base_channels, base_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(base_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(base_channels, output_channels, 3, padding=1, bias=False)
        )
        
        # Final activation
        self.final_activation = nn.Tanh()
        
        self._initialize_weights()
        logger.info(f"Optimized model initialized with {sum(p.numel() for p in self.parameters()):,} parameters")
    
    def _initialize_weights(self):
        """Initialize weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                init.constant_(m.weight, 1)
                init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Initial feature extraction
        features = self.initial_conv(x)
        
        # Multi-scale processing
        multiscale_features = self.multiscale_block(features)
        
        # Attention mechanism
        attended_features = self.attention(features)
        
        # Residual processing
        residual_features = features
        for block in self.residual_blocks:
            residual_features = block(residual_features)
        
        # Frequency enhancement
        frequency_features = self.frequency_block(features)
        
        # Adaptive feature fusion
        fused_features = self.feature_fusion([
            multiscale_features,
            attended_features,
            residual_features,
            frequency_features
        ])
        
        # Output processing
        out = self.output_conv(fused_features)
        out = self.final_activation(out)
        
        return out

class LightweightImageProcessingModel(nn.Module):
    """Lightweight version for mobile/edge deployment"""
    
    def __init__(self,
                 input_channels: int = 3,
                 output_channels: int = 3,
                 base_channels: int = 32,
                 num_blocks: int = 4):
        
        super().__init__()
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.base_channels = base_channels
        self.num_blocks = num_blocks
        
        # Lightweight feature extraction
        self.initial_conv = nn.Sequential(
            nn.Conv2d(input_channels, base_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(base_channels),
            nn.ReLU6(inplace=True)  # ReLU6 for quantization
        )
        
        # Lightweight residual blocks
        self.residual_blocks = nn.ModuleList([
            EfficientResidualBlock(base_channels, expansion=2) for _ in range(num_blocks)
        ])
        
        # Simple output processing
        self.output_conv = nn.Sequential(
            nn.Conv2d(base_channels, base_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(base_channels),
            nn.ReLU6(inplace=True),
            nn.Conv2d(base_channels, output_channels, 3, padding=1, bias=False)
        )
        
        # Final activation
        self.final_activation = nn.Tanh()
        
        self._initialize_weights()
        logger.info(f"Lightweight model initialized with {sum(p.numel() for p in self.parameters()):,} parameters")
    
    def _initialize_weights(self):
        """Initialize weights for better convergence"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                init.constant_(m.weight, 1)
                init.constant_(m.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Initial feature extraction
        features = self.initial_conv(x)
        
        # Residual processing
        for block in self.residual_blocks:
            features = block(features)
        
        # Output processing
        out = self.output_conv(features)
        out = self.final_activation(out)
        
        return out

class ModelOptimizer:
    """Utility class for model optimization"""
    
    @staticmethod
    def optimize_for_inference(model: nn.Module) -> nn.Module:
        """Optimize model for inference"""
        model.eval()
        
        # Fuse batch normalization with convolutions
        model = torch.quantization.fuse_modules(model, [['conv', 'bn', 'relu']])
        
        # Enable optimizations
        if hasattr(torch, 'jit'):
            model = torch.jit.script(model)
        
        return model
    
    @staticmethod
    def quantize_model(model: nn.Module, backend: str = 'fbgemm') -> nn.Module:
        """Quantize model for reduced memory usage"""
        model.eval()
        
        # Prepare for quantization
        model.qconfig = torch.quantization.get_default_qconfig(backend)
        torch.quantization.prepare(model, inplace=True)
        
        # Calibrate with dummy data
        dummy_input = torch.randn(1, 3, 256, 256)
        with torch.no_grad():
            model(dummy_input)
        
        # Convert to quantized model
        quantized_model = torch.quantization.convert(model, inplace=False)
        
        return quantized_model
    
    @staticmethod
    def prune_model(model: nn.Module, pruning_factor: float = 0.3) -> nn.Module:
        """Prune model to reduce parameters"""
        from torch.nn.utils import prune
        
        # Prune convolutional layers
        for name, module in model.named_modules():
            if isinstance(module, nn.Conv2d):
                prune.l1_unstructured(module, name='weight', amount=pruning_factor)
        
        return model
    
    @staticmethod
    def get_model_complexity(model: nn.Module, input_size: Tuple[int, int] = (256, 256)) -> Dict[str, Any]:
        """Calculate model complexity metrics"""
        from thop import profile
        
        dummy_input = torch.randn(1, 3, *input_size)
        
        # Calculate FLOPs and parameters
        flops, params = profile(model, inputs=(dummy_input,), verbose=False)
        
        # Calculate memory usage
        model_size = sum(p.numel() * p.element_size() for p in model.parameters())
        
        return {
            'flops': flops,
            'parameters': params,
            'model_size_mb': model_size / (1024 * 1024),
            'input_size': input_size
        }

def create_optimized_model(config: Dict[str, Any]) -> nn.Module:
    """Factory function to create optimized model based on configuration"""
    
    model_type = config.get('model_type', 'optimized')
    
    if model_type == 'optimized':
        model = OptimizedImageProcessingModel(
            input_channels=config.get('input_channels', 3),
            output_channels=config.get('output_channels', 3),
            base_channels=config.get('base_channels', 64),
            num_blocks=config.get('num_blocks', 8),
            use_attention=config.get('use_attention', True),
            use_multiscale=config.get('use_multiscale', True),
            use_frequency=config.get('use_frequency', True)
        )
    elif model_type == 'lightweight':
        model = LightweightImageProcessingModel(
            input_channels=config.get('input_channels', 3),
            output_channels=config.get('output_channels', 3),
            base_channels=config.get('base_channels', 32),
            num_blocks=config.get('num_blocks', 4)
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return model

def optimize_model_for_deployment(model: nn.Module, 
                                 optimization_level: str = 'medium') -> nn.Module:
    """Optimize model for deployment based on optimization level"""
    
    if optimization_level == 'low':
        # Basic optimization
        model = ModelOptimizer.optimize_for_inference(model)
    
    elif optimization_level == 'medium':
        # Medium optimization
        model = ModelOptimizer.optimize_for_inference(model)
        model = ModelOptimizer.prune_model(model, pruning_factor=0.2)
    
    elif optimization_level == 'high':
        # High optimization
        model = ModelOptimizer.optimize_for_inference(model)
        model = ModelOptimizer.prune_model(model, pruning_factor=0.4)
        model = ModelOptimizer.quantize_model(model)
    
    else:
        raise ValueError(f"Unknown optimization level: {optimization_level}")
    
    return model


