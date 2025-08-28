import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, Optional, Tuple
import cv2
from scipy import ndimage
from scipy.fft import fft2, ifft2, fftshift, ifftshift

class AdvancedLossFunctions:
    """
    Advanced loss functions for image processing with radio frequency optimization
    """
    
    def __init__(self, device: str = 'auto'):
        self.device = torch.device(device if device != 'auto' else 
                                  ('cuda' if torch.cuda.is_available() else 'cpu'))
        
    def perceptual_loss(self, pred: torch.Tensor, target: torch.Tensor, 
                       feature_extractor: nn.Module) -> torch.Tensor:
        """Perceptual loss using pre-trained feature extractor"""
        pred_features = feature_extractor(pred)
        target_features = feature_extractor(target)
        
        loss = 0.0
        for pred_feat, target_feat in zip(pred_features, target_features):
            loss += F.mse_loss(pred_feat, target_feat)
        
        return loss
    
    def frequency_domain_loss(self, pred: torch.Tensor, target: torch.Tensor, 
                            alpha: float = 0.5) -> torch.Tensor:
        """Loss in frequency domain for better frequency preservation"""
        # Convert to frequency domain
        pred_fft = torch.fft.fft2(pred, dim=(-2, -1))
        target_fft = torch.fft.fft2(target, dim=(-2, -1))
        
        # Magnitude loss
        pred_mag = torch.abs(pred_fft)
        target_mag = torch.abs(target_fft)
        magnitude_loss = F.mse_loss(pred_mag, target_mag)
        
        # Phase loss
        pred_phase = torch.angle(pred_fft)
        target_phase = torch.angle(target_fft)
        phase_loss = F.mse_loss(pred_phase, target_phase)
        
        return alpha * magnitude_loss + (1 - alpha) * phase_loss
    
    def structural_similarity_loss(self, pred: torch.Tensor, target: torch.Tensor,
                                 window_size: int = 11, sigma: float = 1.5) -> torch.Tensor:
        """Structural Similarity Index (SSIM) loss"""
        def gaussian_window(size: int, sigma: float) -> torch.Tensor:
            coords = torch.arange(size, dtype=torch.float32, device=pred.device)
            coords -= size // 2
            g = torch.exp(-(coords ** 2) / (2 * sigma ** 2))
            g /= g.sum()
            return g.unsqueeze(0) * g.unsqueeze(1)
        
        window = gaussian_window(window_size, sigma).unsqueeze(0).unsqueeze(0)
        
        mu1 = F.conv2d(pred, window, padding=window_size//2, groups=pred.size(1))
        mu2 = F.conv2d(target, window, padding=window_size//2, groups=target.size(1))
        
        mu1_sq = mu1.pow(2)
        mu2_sq = mu2.pow(2)
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = F.conv2d(pred * pred, window, padding=window_size//2, groups=pred.size(1)) - mu1_sq
        sigma2_sq = F.conv2d(target * target, window, padding=window_size//2, groups=target.size(1)) - mu2_sq
        sigma12 = F.conv2d(pred * target, window, padding=window_size//2, groups=pred.size(1)) - mu1_mu2
        
        C1 = 0.01 ** 2
        C2 = 0.03 ** 2
        
        ssim = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        
        return 1 - ssim.mean()
    
    def edge_preserving_loss(self, pred: torch.Tensor, target: torch.Tensor,
                           edge_weight: float = 2.0) -> torch.Tensor:
        """Edge-preserving loss using Sobel operators"""
        # Sobel operators
        sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], 
                              dtype=torch.float32, device=pred.device).unsqueeze(0).unsqueeze(0)
        sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], 
                              dtype=torch.float32, device=pred.device).unsqueeze(0).unsqueeze(0)
        
        # Edge detection
        pred_edges_x = F.conv2d(pred, sobel_x.repeat(pred.size(1), 1, 1, 1), 
                                padding=1, groups=pred.size(1))
        pred_edges_y = F.conv2d(pred, sobel_y.repeat(pred.size(1), 1, 1, 1), 
                                padding=1, groups=pred.size(1))
        pred_edges = torch.sqrt(pred_edges_x**2 + pred_edges_y**2)
        
        target_edges_x = F.conv2d(target, sobel_x.repeat(target.size(1), 1, 1, 1), 
                                  padding=1, groups=target.size(1))
        target_edges_y = F.conv2d(target, sobel_y.repeat(target.size(1), 1, 1, 1), 
                                  padding=1, groups=target.size(1))
        target_edges = torch.sqrt(target_edges_x**2 + target_edges_y**2)
        
        # Edge loss
        edge_loss = F.mse_loss(pred_edges, target_edges)
        
        # Regular MSE loss
        mse_loss = F.mse_loss(pred, target)
        
        return mse_loss + edge_weight * edge_loss
    
    def radio_frequency_optimization_loss(self, pred: torch.Tensor, target: torch.Tensor,
                                        frequency_bands: Dict[str, Tuple[float, float]],
                                        band_weights: Optional[Dict[str, float]] = None) -> torch.Tensor:
        """Radio frequency domain optimization loss"""
        if band_weights is None:
            band_weights = {band: 1.0 for band in frequency_bands.keys()}
        
        total_loss = 0.0
        
        for band_name, (low_freq, high_freq) in frequency_bands.items():
            # Create frequency mask
            freq_mask = self._create_frequency_mask(pred.size(-2), pred.size(-1), 
                                                  low_freq, high_freq, pred.device)
            
            # Apply mask to frequency domain
            pred_fft = torch.fft.fft2(pred, dim=(-2, -1))
            target_fft = torch.fft.fft2(target, dim=(-2, -1))
            
            pred_band = pred_fft * freq_mask
            target_band = target_fft * freq_mask
            
            # Band-specific loss
            band_loss = F.mse_loss(torch.abs(pred_band), torch.abs(target_band))
            total_loss += band_weights[band_name] * band_loss
        
        return total_loss
    
    def _create_frequency_mask(self, height: int, width: int, 
                              low_freq: float, high_freq: float, 
                              device: torch.device) -> torch.Tensor:
        """Create frequency domain mask for specific frequency band"""
        # Create frequency coordinates
        fy = torch.fft.fftfreq(height, device=device).unsqueeze(1)
        fx = torch.fft.fftfreq(width, device=device).unsqueeze(0)
        
        # Create 2D frequency grid
        freq_grid = torch.sqrt(fy**2 + fx**2)
        
        # Create band-pass filter
        mask = torch.zeros_like(freq_grid)
        mask[(freq_grid >= low_freq) & (freq_grid <= high_freq)] = 1.0
        
        # Apply smoothing
        mask = torch.from_numpy(ndimage.gaussian_filter(mask.cpu().numpy(), sigma=1.0)).to(device)
        
        return mask
    
    def adaptive_loss(self, pred: torch.Tensor, target: torch.Tensor,
                     loss_weights: Dict[str, float]) -> torch.Tensor:
        """Adaptive loss combining multiple loss functions"""
        total_loss = 0.0
        
        if 'mse' in loss_weights:
            total_loss += loss_weights['mse'] * F.mse_loss(pred, target)
        
        if 'frequency' in loss_weights:
            total_loss += loss_weights['frequency'] * self.frequency_domain_loss(pred, target)
        
        if 'ssim' in loss_weights:
            total_loss += loss_weights['ssim'] * self.structural_similarity_loss(pred, target)
        
        if 'edge' in loss_weights:
            total_loss += loss_weights['edge'] * self.edge_preserving_loss(pred, target)
        
        return total_loss
    
    def contrast_enhancement_loss(self, pred: torch.Tensor, target: torch.Tensor,
                                contrast_weight: float = 1.0) -> torch.Tensor:
        """Contrast enhancement loss"""
        # Calculate local contrast
        kernel = torch.ones(1, 1, 3, 3, device=pred.device) / 9
        
        pred_mean = F.conv2d(pred, kernel.repeat(pred.size(1), 1, 1, 1), 
                             padding=1, groups=pred.size(1))
        target_mean = F.conv2d(target, kernel.repeat(target.size(1), 1, 1, 1), 
                               padding=1, groups=target.size(1))
        
        pred_contrast = torch.abs(pred - pred_mean)
        target_contrast = torch.abs(target - target_mean)
        
        contrast_loss = F.mse_loss(pred_contrast, target_contrast)
        
        return contrast_loss * contrast_weight

class RadioFrequencyOptimizer:
    """
    Radio frequency optimization for image processing
    """
    
    def __init__(self, sample_rate: float = 1.0, device: str = 'auto'):
        self.sample_rate = sample_rate
        self.device = torch.device(device if device != 'auto' else 
                                  ('cuda' if torch.cuda.is_available() else 'cpu'))
        
    def optimize_frequency_response(self, image: torch.Tensor, 
                                  target_response: torch.Tensor,
                                  frequency_weights: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Optimize image frequency response"""
        # Convert to frequency domain
        image_fft = torch.fft.fft2(image, dim=(-2, -1))
        
        # Apply frequency domain optimization
        if frequency_weights is not None:
            optimized_fft = image_fft * frequency_weights
        else:
            # Default optimization: enhance high frequencies
            freq_y = torch.fft.fftfreq(image.size(-2), device=image.device).unsqueeze(1)
            freq_x = torch.fft.fftfreq(image.size(-1), device=image.device).unsqueeze(0)
            freq_magnitude = torch.sqrt(freq_y**2 + freq_x**2)
            
            # High-frequency enhancement
            enhancement = 1.0 + 0.5 * freq_magnitude
            optimized_fft = image_fft * enhancement.unsqueeze(0).unsqueeze(0)
        
        # Convert back to spatial domain
        optimized_image = torch.fft.ifft2(optimized_fft, dim=(-2, -1)).real
        
        return optimized_image
    
    def create_frequency_filter(self, height: int, width: int, 
                               filter_type: str = 'lowpass',
                               cutoff_freq: float = 0.1) -> torch.Tensor:
        """Create frequency domain filter"""
        fy = torch.fft.fftfreq(height, device=self.device).unsqueeze(1)
        fx = torch.fft.fftfreq(width, device=self.device).unsqueeze(0)
        freq_grid = torch.sqrt(fy**2 + fx**2)
        
        if filter_type == 'lowpass':
            filter_mask = torch.exp(-(freq_grid / cutoff_freq)**2)
        elif filter_type == 'highpass':
            filter_mask = 1.0 - torch.exp(-(freq_grid / cutoff_freq)**2)
        elif filter_type == 'bandpass':
            low_cutoff = cutoff_freq * 0.5
            high_cutoff = cutoff_freq * 1.5
            filter_mask = torch.exp(-(freq_grid / high_cutoff)**2) - torch.exp(-(freq_grid / low_cutoff)**2)
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        return filter_mask.unsqueeze(0).unsqueeze(0)

# Example usage
if __name__ == "__main__":
    # Initialize loss functions
    loss_functions = AdvancedLossFunctions()
    rf_optimizer = RadioFrequencyOptimizer()
    
    # Create dummy data
    pred = torch.randn(1, 3, 64, 64)
    target = torch.randn(1, 3, 64, 64)
    
    # Test different loss functions
    mse_loss = F.mse_loss(pred, target)
    freq_loss = loss_functions.frequency_domain_loss(pred, target)
    ssim_loss = loss_functions.structural_similarity_loss(pred, target)
    edge_loss = loss_functions.edge_preserving_loss(pred, target)
    
    print(f"MSE Loss: {mse_loss:.6f}")
    print(f"Frequency Loss: {freq_loss:.6f}")
    print(f"SSIM Loss: {ssim_loss:.6f}")
    print(f"Edge Loss: {edge_loss:.6f}")
    
    # Test adaptive loss
    adaptive_loss = loss_functions.adaptive_loss(pred, target, {
        'mse': 1.0,
        'frequency': 0.5,
        'ssim': 0.3,
        'edge': 0.2
    })
    print(f"Adaptive Loss: {adaptive_loss:.6f}")
    
    # Test radio frequency optimization
    frequency_bands = {
        'low': (0.0, 0.1),
        'mid': (0.1, 0.5),
        'high': (0.5, 1.0)
    }
    
    rf_loss = loss_functions.radio_frequency_optimization_loss(
        pred, target, frequency_bands, {'low': 1.0, 'mid': 1.5, 'high': 2.0}
    )
    print(f"Radio Frequency Loss: {rf_loss:.6f}")


