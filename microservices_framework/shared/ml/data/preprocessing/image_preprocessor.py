"""
Image Preprocessing
Specialized image preprocessing utilities.
"""

from typing import Tuple, Optional
from PIL import Image
import torch
import torchvision.transforms as transforms


class ImagePreprocessor:
    """Image preprocessing pipeline."""
    
    def __init__(self):
        self.transform = transforms.Compose([])
    
    def resize(self, size: Tuple[int, int], interpolation=Image.BILINEAR):
        """Add resize transformation."""
        self.transform.transforms.append(transforms.Resize(size, interpolation))
        return self
    
    def center_crop(self, size: Tuple[int, int]):
        """Add center crop transformation."""
        self.transform.transforms.append(transforms.CenterCrop(size))
        return self
    
    def normalize(self, mean: Tuple[float, ...], std: Tuple[float, ...]):
        """Add normalization."""
        self.transform.transforms.append(transforms.Normalize(mean, std))
        return self
    
    def to_tensor(self):
        """Add to tensor transformation."""
        self.transform.transforms.append(transforms.ToTensor())
        return self
    
    def process(self, image: Image.Image) -> torch.Tensor:
        """Process image."""
        return self.transform(image)


def create_image_preprocessor(
    size: Tuple[int, int] = (224, 224),
    mean: Tuple[float, ...] = (0.485, 0.456, 0.406),
    std: Tuple[float, ...] = (0.229, 0.224, 0.225),
    normalize: bool = True,
) -> ImagePreprocessor:
    """Create a standard image preprocessor."""
    preprocessor = ImagePreprocessor()
    preprocessor.resize(size)
    preprocessor.center_crop(size)
    preprocessor.to_tensor()
    
    if normalize:
        preprocessor.normalize(mean, std)
    
    return preprocessor



