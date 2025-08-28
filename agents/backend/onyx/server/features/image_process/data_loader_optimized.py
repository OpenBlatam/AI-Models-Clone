import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
import numpy as np
from PIL import Image
import os
import cv2
from typing import Dict, List, Tuple, Optional, Any, Union
import albumentations as A
from albumentations.pytorch import ToTensorV2
import random
import logging
from pathlib import Path
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedImageDataset(Dataset):
    """
    Optimized dataset for image processing with advanced augmentation
    """
    
    def __init__(self, 
                 image_dir: str,
                 target_dir: Optional[str] = None,
                 transform: Optional[Any] = None,
                 target_transform: Optional[Any] = None,
                 cache_size: int = 100,
                 preload: bool = False,
                 device: str = 'auto'):
        
        self.image_dir = Path(image_dir)
        self.target_dir = Path(target_dir) if target_dir else None
        self.transform = transform
        self.target_transform = target_transform
        self.cache_size = cache_size
        self.preload = preload
        self.device = self._setup_device(device)
        
        # Get image files
        self.image_files = self._get_image_files()
        logger.info(f"Found {len(self.image_files)} images in {image_dir}")
        
        # Initialize cache
        self.cache = {}
        self.cache_order = []
        
        # Preload if requested
        if self.preload:
            self._preload_data()
    
    def _setup_device(self, device: str) -> torch.device:
        """Setup optimal device"""
        if device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda'
            elif torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        return torch.device(device)
    
    def _get_image_files(self) -> List[Path]:
        """Get list of image files"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(self.image_dir.glob(f"*{ext}"))
            image_files.extend(self.image_dir.glob(f"*{ext.upper()}"))
        
        return sorted(image_files)
    
    def _preload_data(self):
        """Preload data into memory"""
        logger.info("Preloading data into memory...")
        for i, image_file in enumerate(self.image_files):
            if i % 100 == 0:
                logger.info(f"Preloading {i}/{len(self.image_files)}")
            
            try:
                image = self._load_image(image_file)
                target = self._load_target(image_file) if self.target_dir else None
                
                self.cache[str(image_file)] = {
                    'image': image,
                    'target': target,
                    'index': i
                }
                self.cache_order.append(str(image_file))
                
                # Limit cache size
                if len(self.cache) > self.cache_size:
                    oldest = self.cache_order.pop(0)
                    del self.cache[oldest]
                    
            except Exception as e:
                logger.warning(f"Failed to preload {image_file}: {e}")
        
        logger.info(f"Preloaded {len(self.cache)} images")
    
    def _load_image(self, image_path: Path) -> Image.Image:
        """Load image with error handling"""
        try:
            image = Image.open(image_path).convert('RGB')
            return image
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            # Return a blank image as fallback
            return Image.new('RGB', (256, 256), color='black')
    
    def _load_target(self, image_path: Path) -> Optional[Image.Image]:
        """Load target image if available"""
        if not self.target_dir:
            return None
        
        try:
            # Try to find corresponding target file
            target_path = self.target_dir / image_path.name
            if target_path.exists():
                return Image.open(target_path).convert('RGB')
            
            # Try with different extensions
            for ext in ['.png', '.jpg', '.jpeg']:
                target_path = self.target_dir / f"{image_path.stem}{ext}"
                if target_path.exists():
                    return Image.open(target_path).convert('RGB')
            
            return None
        except Exception as e:
            logger.warning(f"Failed to load target for {image_path}: {e}")
            return None
    
    def __len__(self) -> int:
        return len(self.image_files)
    
    def __getitem__(self, idx: int) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        image_path = self.image_files[idx]
        cache_key = str(image_path)
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            image = cached_data['image']
            target = cached_data['target']
        else:
            # Load from disk
            image = self._load_image(image_path)
            target = self._load_target(image_path)
            
            # Add to cache
            if len(self.cache) < self.cache_size:
                self.cache[cache_key] = {
                    'image': image,
                    'target': target,
                    'index': idx
                }
                self.cache_order.append(cache_key)
            else:
                # Replace oldest item
                oldest = self.cache_order.pop(0)
                del self.cache[oldest]
                self.cache[cache_key] = {
                    'image': image,
                    'target': target,
                    'index': idx
                }
                self.cache_order.append(cache_key)
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        if target and self.target_transform:
            target = self.target_transform(target)
        elif target:
            target = TF.to_tensor(target)
        
        if target is not None:
            return image, target
        else:
            return image
    
    def clear_cache(self):
        """Clear memory cache"""
        self.cache.clear()
        self.cache_order.clear()
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
        gc.collect()
        logger.info("Cache cleared")

class AdvancedAugmentationPipeline:
    """
    Advanced augmentation pipeline with radio frequency considerations
    """
    
    def __init__(self, 
                 image_size: Tuple[int, int] = (256, 256),
                 use_albumentations: bool = True,
                 frequency_preserving: bool = True):
        
        self.image_size = image_size
        self.use_albumentations = use_albumentations
        self.frequency_preserving = frequency_preserving
        
        if use_albumentations:
            self._setup_albumentations()
        else:
            self._setup_torchvision()
    
    def _setup_albumentations(self):
        """Setup Albumentations pipeline"""
        self.aug_pipeline = A.Compose([
            A.RandomResizedCrop(
                height=self.image_size[0],
                width=self.image_size[1],
                scale=(0.8, 1.0),
                ratio=(0.75, 1.33)
            ),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.3),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(
                shift_limit=0.1,
                scale_limit=0.2,
                rotate_limit=30,
                p=0.5
            ),
            A.OneOf([
                A.MotionBlur(blur_limit=3, p=0.3),
                A.MedianBlur(blur_limit=3, p=0.3),
                A.Blur(blur_limit=3, p=0.3),
            ], p=0.3),
            A.OneOf([
                A.CLAHE(clip_limit=2, p=0.3),
                A.IAASharpen(p=0.3),
                A.IAAEmboss(p=0.3),
            ], p=0.3),
            A.OneOf([
                A.RandomBrightnessContrast(
                    brightness_limit=0.2,
                    contrast_limit=0.2,
                    p=0.3
                ),
                A.HueSaturationValue(
                    hue_shift_limit=20,
                    sat_shift_limit=30,
                    val_shift_limit=20,
                    p=0.3
                ),
            ], p=0.3),
            A.OneOf([
                A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
                A.ISONoise(color_shift=(0.01, 0.05), p=0.3),
                A.MultiplicativeNoise(multiplier=(0.9, 1.1), p=0.3),
            ], p=0.3),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2()
        ])
    
    def _setup_torchvision(self):
        """Setup TorchVision transforms"""
        self.torchvision_transforms = transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=30),
            transforms.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.1
            ),
            transforms.RandomGrayscale(p=0.1),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def __call__(self, image: Image.Image) -> torch.Tensor:
        """Apply augmentation pipeline"""
        if self.use_albumentations:
            # Convert PIL to numpy for Albumentations
            image_np = np.array(image)
            augmented = self.aug_pipeline(image=image_np)
            return augmented['image']
        else:
            return self.torchvision_transforms(image)

class FrequencyPreservingTransform:
    """
    Transform that preserves frequency characteristics
    """
    
    def __init__(self, 
                 image_size: Tuple[int, int] = (256, 256),
                 frequency_threshold: float = 0.1):
        
        self.image_size = image_size
        self.frequency_threshold = frequency_threshold
    
    def __call__(self, image: Image.Image) -> torch.Tensor:
        """Apply frequency-preserving transform"""
        # Resize image
        image = TF.resize(image, self.image_size)
        
        # Convert to tensor
        image_tensor = TF.to_tensor(image)
        
        # Apply frequency domain processing
        if self.frequency_threshold > 0:
            image_tensor = self._preserve_frequencies(image_tensor)
        
        # Normalize
        image_tensor = TF.normalize(
            image_tensor,
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
        
        return image_tensor
    
    def _preserve_frequencies(self, image_tensor: torch.Tensor) -> torch.Tensor:
        """Preserve important frequency components"""
        # Convert to frequency domain
        fft = torch.fft.fft2(image_tensor, dim=(-2, -1))
        
        # Create frequency mask
        height, width = image_tensor.shape[-2:]
        fy = torch.fft.fftfreq(height, device=image_tensor.device).unsqueeze(1)
        fx = torch.fft.fftfreq(width, device=image_tensor.device).unsqueeze(0)
        freq_grid = torch.sqrt(fy**2 + fx**2)
        
        # Preserve frequencies above threshold
        mask = (freq_grid > self.frequency_threshold).float()
        mask = mask.unsqueeze(0).unsqueeze(0)
        
        # Apply mask
        filtered_fft = fft * mask
        
        # Convert back to spatial domain
        filtered_image = torch.fft.ifft2(filtered_fft, dim=(-2, -1)).real
        
        return filtered_image

def create_optimized_dataloader(dataset: Dataset,
                               batch_size: int = 32,
                               num_workers: int = 4,
                               pin_memory: bool = True,
                               persistent_workers: bool = True,
                               prefetch_factor: int = 2) -> DataLoader:
    """
    Create optimized DataLoader with best practices
    """
    
    # Determine optimal number of workers
    if num_workers == 'auto':
        num_workers = min(8, os.cpu_count())
    
    # Create DataLoader with optimizations
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers and num_workers > 0,
        prefetch_factor=prefetch_factor if num_workers > 0 else 2,
        drop_last=True,
        generator=torch.Generator(device='cpu')
    )
    
    return dataloader

# Example usage
if __name__ == "__main__":
    # Create dataset
    dataset = OptimizedImageDataset(
        image_dir="path/to/images",
        target_dir="path/to/targets",
        transform=AdvancedAugmentationPipeline(image_size=(256, 256)),
        cache_size=50,
        preload=False
    )
    
    # Create dataloader
    dataloader = create_optimized_dataloader(
        dataset,
        batch_size=16,
        num_workers=4,
        pin_memory=True
    )
    
    # Test iteration
    for batch_idx, (images, targets) in enumerate(dataloader):
        print(f"Batch {batch_idx}: {images.shape}, {targets.shape}")
        
        if batch_idx >= 2:  # Just test first few batches
            break
    
    # Clear cache
    dataset.clear_cache()


