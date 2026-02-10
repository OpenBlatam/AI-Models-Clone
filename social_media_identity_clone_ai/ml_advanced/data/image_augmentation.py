"""
Data augmentation avanzada para imágenes
"""

import torch
import torchvision.transforms as transforms
from torchvision.transforms import functional as F
from typing import List, Dict, Any, Optional
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AdvancedImageAugmentation:
    """Augmentación avanzada de imágenes"""
    
    def __init__(self):
        self.transforms = []
    
    def add_random_crop(self, size: tuple = (224, 224), scale: tuple = (0.8, 1.0)):
        """Agrega random crop"""
        self.transforms.append(transforms.RandomResizedCrop(size, scale=scale))
        return self
    
    def add_random_flip(self, p: float = 0.5):
        """Agrega random flip"""
        self.transforms.append(transforms.RandomHorizontalFlip(p=p))
        return self
    
    def add_color_jitter(
        self,
        brightness: float = 0.2,
        contrast: float = 0.2,
        saturation: float = 0.2,
        hue: float = 0.1
    ):
        """Agrega color jitter"""
        self.transforms.append(transforms.ColorJitter(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            hue=hue
        ))
        return self
    
    def add_random_rotation(self, degrees: int = 15):
        """Agrega rotación aleatoria"""
        self.transforms.append(transforms.RandomRotation(degrees))
        return self
    
    def add_gaussian_blur(self, kernel_size: int = 3, p: float = 0.5):
        """Agrega blur gaussiano"""
        self.transforms.append(transforms.GaussianBlur(kernel_size, sigma=(0.1, 2.0)))
        return self
    
    def add_random_erasing(self, p: float = 0.5):
        """Agrega random erasing"""
        self.transforms.append(transforms.RandomErasing(p=p))
        return self
    
    def build(self) -> transforms.Compose:
        """Construye pipeline de transformaciones"""
        return transforms.Compose(self.transforms)
    
    def augment_image(self, image: Image.Image) -> Image.Image:
        """Aumenta imagen"""
        transform = self.build()
        return transform(image)


class MixUpImage:
    """MixUp para imágenes"""
    
    def __init__(self, alpha: float = 0.2):
        self.alpha = alpha
    
    def __call__(
        self,
        image1: torch.Tensor,
        image2: torch.Tensor,
        label1: torch.Tensor,
        label2: torch.Tensor
    ) -> tuple:
        """Aplica MixUp"""
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1.0
        
        mixed_image = lam * image1 + (1 - lam) * image2
        mixed_label = lam * label1 + (1 - lam) * label2
        
        return mixed_image, mixed_label, lam


class CutMix:
    """CutMix augmentation"""
    
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
    
    def __call__(
        self,
        image1: torch.Tensor,
        image2: torch.Tensor,
        label1: torch.Tensor,
        label2: torch.Tensor
    ) -> tuple:
        """Aplica CutMix"""
        if self.alpha > 0:
            lam = np.random.beta(self.alpha, self.alpha)
        else:
            lam = 1.0
        
        # Generar bounding box
        W, H = image1.shape[-1], image1.shape[-2]
        cut_rat = np.sqrt(1.0 - lam)
        cut_w = int(W * cut_rat)
        cut_h = int(H * cut_rat)
        
        cx = np.random.randint(W)
        cy = np.random.randint(H)
        
        bbx1 = np.clip(cx - cut_w // 2, 0, W)
        bby1 = np.clip(cy - cut_h // 2, 0, H)
        bbx2 = np.clip(cx + cut_w // 2, 0, W)
        bby2 = np.clip(cy + cut_h // 2, 0, H)
        
        # Aplicar CutMix
        mixed_image = image1.clone()
        mixed_image[:, bby1:bby2, bbx1:bbx2] = image2[:, bby1:bby2, bbx1:bbx2]
        
        # Ajustar lambda
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (W * H))
        mixed_label = lam * label1 + (1 - lam) * label2
        
        return mixed_image, mixed_label, lam




