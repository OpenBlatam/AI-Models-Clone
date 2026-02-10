"""
Image transforms and augmentation pipelines
Separated from datasets for modularity
"""

from typing import Optional, Callable, Tuple
import torchvision.transforms as transforms
import logging

logger = logging.getLogger(__name__)

try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    ALBUMENTATIONS_AVAILABLE = True
except ImportError:
    ALBUMENTATIONS_AVAILABLE = False
    logger.warning("albumentations not available, using torchvision transforms")


def get_train_transforms(
    target_size: Tuple[int, int] = (224, 224),
    use_albumentations: bool = True,
    augmentation_strength: str = "medium"  # "light", "medium", "strong"
) -> Callable:
    """
    Get training transforms with augmentation
    
    Args:
        target_size: Target image size (height, width)
        use_albumentations: Whether to use albumentations (more advanced)
        augmentation_strength: Strength of augmentation
        
    Returns:
        Transform function
    """
    if use_albumentations and ALBUMENTATIONS_AVAILABLE:
        return _get_albumentations_train_transforms(target_size, augmentation_strength)
    else:
        return _get_torchvision_train_transforms(target_size)


def get_val_transforms(
    target_size: Tuple[int, int] = (224, 224),
    use_albumentations: bool = True
) -> Callable:
    """Get validation transforms (no augmentation)"""
    if use_albumentations and ALBUMENTATIONS_AVAILABLE:
        return _get_albumentations_val_transforms(target_size)
    else:
        return _get_torchvision_val_transforms(target_size)


def get_test_transforms(
    target_size: Tuple[int, int] = (224, 224),
    use_albumentations: bool = True
) -> Callable:
    """Get test transforms (same as validation)"""
    return get_val_transforms(target_size, use_albumentations)


def _get_albumentations_train_transforms(
    target_size: Tuple[int, int],
    strength: str
) -> Callable:
    """Get albumentations training transforms"""
    height, width = target_size
    
    # Base transforms
    base_transforms = [
        A.Resize(height, width),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2()
    ]
    
    # Augmentation based on strength
    if strength == "light":
        augmentation = [
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.3),
        ]
    elif strength == "medium":
        augmentation = [
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.2),
            A.RandomRotate90(p=0.3),
            A.RandomBrightnessContrast(p=0.4),
            A.RandomGamma(p=0.3),
            A.GaussNoise(p=0.2),
            A.Blur(blur_limit=3, p=0.2),
        ]
    elif strength == "strong":
        augmentation = [
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.3),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.1,
                rotate_limit=15,
                p=0.5
            ),
            A.RandomBrightnessContrast(p=0.5),
            A.RandomGamma(p=0.4),
            A.GaussNoise(p=0.3),
            A.Blur(blur_limit=5, p=0.3),
            A.CLAHE(p=0.3),
            A.RandomShadow(p=0.2),
        ]
    else:
        augmentation = []
    
    transform = A.Compose(augmentation + base_transforms)
    
    def transform_fn(image):
        if hasattr(image, 'numpy'):
            image = image.numpy()
        result = transform(image=image)
        return result['image']
    
    return transform_fn


def _get_albumentations_val_transforms(target_size: Tuple[int, int]) -> Callable:
    """Get albumentations validation transforms"""
    height, width = target_size
    
    transform = A.Compose([
        A.Resize(height, width),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        ToTensorV2()
    ])
    
    def transform_fn(image):
        if hasattr(image, 'numpy'):
            image = image.numpy()
        result = transform(image=image)
        return result['image']
    
    return transform_fn


def _get_torchvision_train_transforms(target_size: Tuple[int, int]) -> transforms.Compose:
    """Get torchvision training transforms"""
    height, width = target_size
    
    return transforms.Compose([
        transforms.Resize((height, width)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
            hue=0.1
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
        transforms.RandomErasing(p=0.1)
    ])


def _get_torchvision_val_transforms(target_size: Tuple[int, int]) -> transforms.Compose:
    """Get torchvision validation transforms"""
    height, width = target_size
    
    return transforms.Compose([
        transforms.Resize((height, width)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


class AugmentationPipeline:
    """
    Configurable augmentation pipeline
    Allows easy customization of augmentation strategies
    """
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (224, 224),
        use_albumentations: bool = True
    ):
        self.target_size = target_size
        self.use_albumentations = use_albumentations and ALBUMENTATIONS_AVAILABLE
    
    def get_train_transforms(self, strength: str = "medium") -> Callable:
        """Get training transforms"""
        return get_train_transforms(
            self.target_size,
            self.use_albumentations,
            strength
        )
    
    def get_val_transforms(self) -> Callable:
        """Get validation transforms"""
        return get_val_transforms(
            self.target_size,
            self.use_albumentations
        )
    
    def get_test_transforms(self) -> Callable:
        """Get test transforms"""
        return get_test_transforms(
            self.target_size,
            self.use_albumentations
        )













