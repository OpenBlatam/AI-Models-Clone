"""
Dataset Factory
Centralized dataset creation with proper configuration
"""

from typing import List, Dict, Optional, Callable, Tuple, Union
import numpy as np
from PIL import Image
import logging

from data.datasets import SkinDataset, SkinVideoDataset, MultiTaskDataset
from data.transforms import get_train_transforms, get_val_transforms, get_test_transforms

logger = logging.getLogger(__name__)


class DatasetFactory:
    """
    Factory for creating datasets
    Provides consistent interface for dataset creation
    """
    
    @staticmethod
    def create_skin_dataset(
        images: Union[List[np.ndarray], List[str], List[Image.Image]],
        labels: Optional[Dict[str, List]] = None,
        split: str = "train",  # "train", "val", "test"
        target_size: Tuple[int, int] = (224, 224),
        cache_images: bool = False,
        use_albumentations: bool = True,
        augmentation_strength: str = "medium"
    ) -> SkinDataset:
        """
        Create skin dataset with appropriate transforms
        
        Args:
            images: List of images
            labels: Dictionary of labels
            split: Dataset split ("train", "val", "test")
            target_size: Target image size
            cache_images: Whether to cache images
            use_albumentations: Use albumentations for augmentation
            augmentation_strength: Augmentation strength ("light", "medium", "strong")
            
        Returns:
            SkinDataset instance
        """
        # Get appropriate transforms
        if split == "train":
            transform = get_train_transforms(
                target_size=target_size,
                use_albumentations=use_albumentations,
                augmentation_strength=augmentation_strength
            )
        elif split == "val":
            transform = get_val_transforms(
                target_size=target_size,
                use_albumentations=use_albumentations
            )
        else:  # test
            transform = get_test_transforms(
                target_size=target_size,
                use_albumentations=use_albumentations
            )
        
        return SkinDataset(
            images=images,
            labels=labels,
            transform=transform,
            target_size=target_size,
            cache_images=cache_images
        )
    
    @staticmethod
    def create_video_dataset(
        video_paths: List[str],
        labels: Optional[Dict[str, List]] = None,
        num_frames: int = 16,
        target_size: Tuple[int, int] = (224, 224),
        frame_sampling: str = "uniform"
    ) -> SkinVideoDataset:
        """Create video dataset"""
        transform = get_val_transforms(target_size=target_size)
        
        return SkinVideoDataset(
            video_paths=video_paths,
            labels=labels,
            num_frames=num_frames,
            transform=transform,
            target_size=target_size,
            frame_sampling=frame_sampling
        )
    
    @staticmethod
    def create_multi_task_dataset(
        images: List[Union[np.ndarray, str, Image.Image]],
        task_labels: Dict[str, Dict[str, List]],
        split: str = "train",
        target_size: Tuple[int, int] = (224, 224)
    ) -> MultiTaskDataset:
        """Create multi-task dataset"""
        if split == "train":
            transform = get_train_transforms(target_size=target_size)
        else:
            transform = get_val_transforms(target_size=target_size)
        
        return MultiTaskDataset(
            images=images,
            task_labels=task_labels,
            transform=transform,
            target_size=target_size
        )
    
    @staticmethod
    def create_datasets_from_config(
        config: Dict,
        train_images: List,
        val_images: List,
        test_images: Optional[List] = None,
        train_labels: Optional[Dict] = None,
        val_labels: Optional[Dict] = None,
        test_labels: Optional[Dict] = None
    ) -> Dict[str, SkinDataset]:
        """
        Create multiple datasets from configuration
        
        Args:
            config: Configuration dictionary
            train_images: Training images
            val_images: Validation images
            test_images: Test images (optional)
            train_labels: Training labels
            val_labels: Validation labels
            test_labels: Test labels (optional)
            
        Returns:
            Dictionary of datasets
        """
        data_config = config.get('data', {})
        target_size = tuple(data_config.get('preprocessing', {}).get('target_size', [224, 224]))
        use_albumentations = data_config.get('augmentation', {}).get('use_albumentations', True)
        augmentation_strength = data_config.get('augmentation', {}).get('strength', 'medium')
        cache_images = data_config.get('cache_images', False)
        
        datasets = {}
        
        # Training dataset
        datasets['train'] = DatasetFactory.create_skin_dataset(
            images=train_images,
            labels=train_labels,
            split="train",
            target_size=target_size,
            cache_images=cache_images,
            use_albumentations=use_albumentations,
            augmentation_strength=augmentation_strength
        )
        
        # Validation dataset
        datasets['val'] = DatasetFactory.create_skin_dataset(
            images=val_images,
            labels=val_labels,
            split="val",
            target_size=target_size,
            cache_images=False,
            use_albumentations=use_albumentations
        )
        
        # Test dataset (if provided)
        if test_images:
            datasets['test'] = DatasetFactory.create_skin_dataset(
                images=test_images,
                labels=test_labels,
                split="test",
                target_size=target_size,
                cache_images=False,
                use_albumentations=use_albumentations
            )
        
        return datasets













