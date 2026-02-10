"""
Image Transforms
Modular image transformation utilities
"""

import torch
import torchvision.transforms as transforms
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TransformBuilder:
    """
    Builder for creating transform pipelines
    """
    
    @staticmethod
    def build_train_transforms(
        image_size: int = 224,
        mean: Optional[List[float]] = None,
        std: Optional[List[float]] = None,
        augmentation: Optional[Dict[str, Any]] = None,
    ) -> transforms.Compose:
        """
        Build training transforms
        
        Args:
            image_size: Target image size
            mean: Normalization mean
            std: Normalization std
            augmentation: Augmentation parameters
            
        Returns:
            Composed transforms
        """
        augmentation = augmentation or {}
        
        transform_list = []
        
        # Resize
        if augmentation.get('random_resized_crop', True):
            transform_list.append(
                transforms.RandomResizedCrop(
                    image_size,
                    scale=augmentation.get('scale', (0.08, 1.0))
                )
            )
        else:
            transform_list.append(transforms.Resize((image_size, image_size)))
        
        # Horizontal flip
        if augmentation.get('random_horizontal_flip', True):
            transform_list.append(transforms.RandomHorizontalFlip())
        
        # Color jitter
        if augmentation.get('color_jitter', {}).get('enabled', False):
            transform_list.append(
                transforms.ColorJitter(
                    brightness=augmentation['color_jitter'].get('brightness', 0.2),
                    contrast=augmentation['color_jitter'].get('contrast', 0.2),
                    saturation=augmentation['color_jitter'].get('saturation', 0.2),
                    hue=augmentation['color_jitter'].get('hue', 0.1),
                )
            )
        
        # Random rotation
        if augmentation.get('random_rotation', {}).get('enabled', False):
            transform_list.append(
                transforms.RandomRotation(
                    degrees=augmentation['random_rotation'].get('degrees', 15)
                )
            )
        
        # To tensor
        transform_list.append(transforms.ToTensor())
        
        # Normalize
        mean = mean or [0.485, 0.456, 0.406]
        std = std or [0.229, 0.224, 0.225]
        transform_list.append(transforms.Normalize(mean=mean, std=std))
        
        return transforms.Compose(transform_list)
    
    @staticmethod
    def build_val_transforms(
        image_size: int = 224,
        mean: Optional[List[float]] = None,
        std: Optional[List[float]] = None,
    ) -> transforms.Compose:
        """
        Build validation transforms
        
        Args:
            image_size: Target image size
            mean: Normalization mean
            std: Normalization std
            
        Returns:
            Composed transforms
        """
        mean = mean or [0.485, 0.456, 0.406]
        std = std or [0.229, 0.224, 0.225]
        
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])
    
    @staticmethod
    def build_test_transforms(
        image_size: int = 224,
        mean: Optional[List[float]] = None,
        std: Optional[List[float]] = None,
    ) -> transforms.Compose:
        """
        Build test transforms (same as validation)
        
        Args:
            image_size: Target image size
            mean: Normalization mean
            std: Normalization std
            
        Returns:
            Composed transforms
        """
        return TransformBuilder.build_val_transforms(image_size, mean, std)


class ImageTransforms:
    """
    Image transformation utilities
    """
    
    @staticmethod
    def get_imagenet_transforms(
        image_size: int = 224,
        split: str = 'train',
    ) -> transforms.Compose:
        """
        Get ImageNet-style transforms
        
        Args:
            image_size: Target image size
            split: 'train', 'val', or 'test'
            
        Returns:
            Composed transforms
        """
        if split == 'train':
            return TransformBuilder.build_train_transforms(image_size)
        else:
            return TransformBuilder.build_val_transforms(image_size)
    
    @staticmethod
    def get_custom_transforms(
        config: Dict[str, Any],
    ) -> transforms.Compose:
        """
        Get custom transforms from config
        
        Args:
            config: Transform configuration
            
        Returns:
            Composed transforms
        """
        if config.get('type') == 'train':
            return TransformBuilder.build_train_transforms(
                image_size=config.get('image_size', 224),
                augmentation=config.get('augmentation')
            )
        else:
            return TransformBuilder.build_val_transforms(
                image_size=config.get('image_size', 224)
            )



