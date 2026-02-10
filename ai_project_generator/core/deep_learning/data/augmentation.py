"""
Data Augmentation - Image and Text Augmentation
===============================================

Provides augmentation utilities for:
- Image augmentation (transforms)
- Text augmentation
- Mixup/CutMix for images
"""

import logging
from typing import Dict, Any, Optional, Callable, List
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


def get_image_augmentation(
    augmentation_type: str = 'standard',
    image_size: int = 224,
    mean: Optional[List[float]] = None,
    std: Optional[List[float]] = None
) -> transforms.Compose:
    """
    Get image augmentation pipeline.
    
    Args:
        augmentation_type: Type of augmentation ('standard', 'strong', 'weak', 'none')
        image_size: Target image size
        mean: Normalization mean (defaults to ImageNet)
        std: Normalization std (defaults to ImageNet)
        
    Returns:
        Compose transform
    """
    if mean is None:
        mean = [0.485, 0.456, 0.406]  # ImageNet mean
    if std is None:
        std = [0.229, 0.224, 0.225]  # ImageNet std
    
    if augmentation_type == 'none':
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)
        ])
    
    elif augmentation_type == 'weak':
        return transforms.Compose([
            transforms.Resize((image_size + 32, image_size + 32)),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)
        ])
    
    elif augmentation_type == 'standard':
        return transforms.Compose([
            transforms.RandomResizedCrop(image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
            transforms.RandomErasing(p=0.1)
        ])
    
    elif augmentation_type == 'strong':
        return transforms.Compose([
            transforms.RandomResizedCrop(image_size, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.2),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.15),
            transforms.RandomRotation(degrees=15),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
            transforms.RandomErasing(p=0.2, scale=(0.02, 0.33))
        ])
    
    else:
        raise ValueError(f"Unknown augmentation type: {augmentation_type}")


class Mixup:
    """Mixup augmentation for images."""
    
    def __init__(self, alpha: float = 0.2):
        """
        Initialize Mixup.
        
        Args:
            alpha: Beta distribution parameter
        """
        self.alpha = alpha
    
    def __call__(self, batch: torch.Tensor, labels: torch.Tensor) -> tuple:
        """
        Apply Mixup to batch.
        
        Args:
            batch: Input batch (N, C, H, W)
            labels: Labels (N,)
            
        Returns:
            Mixed batch and labels
        """
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1
        
        batch_size = batch.size(0)
        index = torch.randperm(batch_size).to(batch.device)
        
        mixed_batch = lam * batch + (1 - lam) * batch[index, :]
        y_a, y_b = labels, labels[index]
        
        return mixed_batch, y_a, y_b, lam


class CutMix:
    """CutMix augmentation for images."""
    
    def __init__(self, alpha: float = 1.0):
        """
        Initialize CutMix.
        
        Args:
            alpha: Beta distribution parameter
        """
        self.alpha = alpha
    
    def __call__(self, batch: torch.Tensor, labels: torch.Tensor) -> tuple:
        """
        Apply CutMix to batch.
        
        Args:
            batch: Input batch (N, C, H, W)
            labels: Labels (N,)
            
        Returns:
            Mixed batch and labels
        """
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1
        
        batch_size = batch.size(0)
        index = torch.randperm(batch_size).to(batch.device)
        
        # Generate random bounding box
        W, H = batch.size(3), batch.size(2)
        cut_rat = np.sqrt(1.0 - lam)
        cut_w = int(W * cut_rat)
        cut_h = int(H * cut_rat)
        
        # Random center
        cx = np.random.randint(W)
        cy = np.random.randint(H)
        
        # Clamp bounding box
        bbx1 = np.clip(cx - cut_w // 2, 0, W)
        bby1 = np.clip(cy - cut_h // 2, 0, H)
        bbx2 = np.clip(cx + cut_w // 2, 0, W)
        bby2 = np.clip(cy + cut_h // 2, 0, H)
        
        # Apply CutMix
        batch[:, :, bby1:bby2, bbx1:bbx2] = batch[index, :, bby1:bby2, bbx1:bbx2]
        
        # Adjust lambda to match pixel ratio
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (W * H))
        
        y_a, y_b = labels, labels[index]
        
        return batch, y_a, y_b, lam



