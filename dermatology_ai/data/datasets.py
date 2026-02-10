"""
Dataset classes for skin analysis
Implements PyTorch Dataset interface
"""

from torch.utils.data import Dataset
from typing import List, Dict, Optional, Callable, Union, Tuple
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class SkinDataset(Dataset):
    """
    PyTorch Dataset for skin images
    Supports multiple label types and transforms
    """
    
    def __init__(
        self,
        images: Union[List[np.ndarray], List[str], List[Image.Image]],
        labels: Optional[Dict[str, List]] = None,
        transform: Optional[Callable] = None,
        target_size: Tuple[int, int] = (224, 224),
        cache_images: bool = False
    ):
        """
        Initialize dataset
        
        Args:
            images: List of images (arrays, paths, or PIL Images)
            labels: Dictionary of label lists (e.g., {'conditions': [...], 'metrics': [...]})
            transform: Optional transform function
            target_size: Target image size (height, width)
            cache_images: Whether to cache images in memory
        """
        self.images = images
        self.labels = labels or {}
        self.transform = transform
        self.target_size = target_size
        self.cache_images = cache_images
        
        # Cache for loaded images
        self._image_cache: Dict[int, Image.Image] = {}
        
        # Validate
        self._validate()
    
    def _validate(self):
        """Validate dataset"""
        if not self.images:
            raise ValueError("Dataset is empty")
        
        # Check label lengths
        for key, values in self.labels.items():
            if len(values) != len(self.images):
                raise ValueError(
                    f"Label '{key}' length ({len(values)}) "
                    f"doesn't match images length ({len(self.images)})"
                )
    
    def __len__(self) -> int:
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Dict[str, any]:
        """Get item by index"""
        # Load image
        image = self._load_image(idx)
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        else:
            # Default transform
            import torchvision.transforms as transforms
            default_transform = transforms.Compose([
                transforms.Resize(self.target_size),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            image = default_transform(image)
        
        # Prepare sample
        sample = {'image': image, 'index': idx}
        
        # Add labels
        for key, values in self.labels.items():
            if idx < len(values):
                import torch
                label = values[idx]
                if not isinstance(label, torch.Tensor):
                    label = torch.tensor(label, dtype=torch.float32)
                sample[key] = label
        
        return sample
    
    def _load_image(self, idx: int) -> Image.Image:
        """Load image by index"""
        # Check cache
        if self.cache_images and idx in self._image_cache:
            return self._image_cache[idx]
        
        image_source = self.images[idx]
        
        # Load based on type
        if isinstance(image_source, str):
            # File path
            image = Image.open(image_source).convert('RGB')
        elif isinstance(image_source, np.ndarray):
            # NumPy array
            if image_source.dtype != np.uint8:
                image_source = (image_source * 255).astype(np.uint8)
            image = Image.fromarray(image_source)
        elif isinstance(image_source, Image.Image):
            # PIL Image
            image = image_source.convert('RGB')
        else:
            raise ValueError(f"Unsupported image type: {type(image_source)}")
        
        # Cache if enabled
        if self.cache_images:
            self._image_cache[idx] = image
        
        return image
    
    def clear_cache(self):
        """Clear image cache"""
        self._image_cache.clear()


class SkinVideoDataset(Dataset):
    """
    Dataset for video sequences
    Samples frames from videos
    """
    
    def __init__(
        self,
        video_paths: List[str],
        labels: Optional[Dict[str, List]] = None,
        num_frames: int = 16,
        transform: Optional[Callable] = None,
        target_size: Tuple[int, int] = (224, 224),
        frame_sampling: str = "uniform"  # "uniform", "random", "first"
    ):
        """
        Initialize video dataset
        
        Args:
            video_paths: List of video file paths
            labels: Dictionary of label lists
            num_frames: Number of frames to sample
            transform: Optional transform function
            target_size: Target frame size
            frame_sampling: Frame sampling strategy
        """
        self.video_paths = video_paths
        self.labels = labels or {}
        self.num_frames = num_frames
        self.transform = transform
        self.target_size = target_size
        self.frame_sampling = frame_sampling
    
    def __len__(self) -> int:
        return len(self.video_paths)
    
    def __getitem__(self, idx: int) -> Dict[str, any]:
        """Get video frames"""
        import cv2
        
        video_path = self.video_paths[idx]
        cap = cv2.VideoCapture(video_path)
        
        # Get total frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames
        frame_indices = self._sample_frames(total_frames)
        
        frames = []
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                frames.append(frame)
        
        cap.release()
        
        # Apply transforms
        if self.transform:
            frames = [self.transform(frame) for frame in frames]
        
        # Stack frames
        import torch
        frames_tensor = torch.stack(frames)  # (num_frames, C, H, W)
        
        # Prepare sample
        sample = {'frames': frames_tensor, 'index': idx}
        
        # Add labels
        for key, values in self.labels.items():
            if idx < len(values):
                label = values[idx]
                if not isinstance(label, torch.Tensor):
                    label = torch.tensor(label, dtype=torch.float32)
                sample[key] = label
        
        return sample
    
    def _sample_frames(self, total_frames: int) -> List[int]:
        """Sample frame indices"""
        if total_frames <= self.num_frames:
            return list(range(total_frames))
        
        if self.frame_sampling == "uniform":
            step = total_frames // self.num_frames
            return [i * step for i in range(self.num_frames)]
        elif self.frame_sampling == "random":
            import random
            return sorted(random.sample(range(total_frames), self.num_frames))
        elif self.frame_sampling == "first":
            return list(range(self.num_frames))
        else:
            raise ValueError(f"Unknown frame_sampling: {self.frame_sampling}")


class MultiTaskDataset(Dataset):
    """
    Dataset for multi-task learning
    Supports different label types for different tasks
    """
    
    def __init__(
        self,
        images: List[Union[np.ndarray, str, Image.Image]],
        task_labels: Dict[str, Dict[str, List]],
        transform: Optional[Callable] = None,
        target_size: Tuple[int, int] = (224, 224)
    ):
        """
        Initialize multi-task dataset
        
        Args:
            images: List of images
            task_labels: Dictionary mapping task names to label dictionaries
                         e.g., {'classification': {'conditions': [...]}, 'regression': {'metrics': [...]}}
            transform: Optional transform
            target_size: Target image size
        """
        self.images = images
        self.task_labels = task_labels
        self.transform = transform
        self.target_size = target_size
    
    def __len__(self) -> int:
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Dict[str, any]:
        """Get item with multi-task labels"""
        # Load image (similar to SkinDataset)
        image_source = self.images[idx]
        
        if isinstance(image_source, str):
            image = Image.open(image_source).convert('RGB')
        elif isinstance(image_source, np.ndarray):
            if image_source.dtype != np.uint8:
                image_source = (image_source * 255).astype(np.uint8)
            image = Image.fromarray(image_source)
        elif isinstance(image_source, Image.Image):
            image = image_source.convert('RGB')
        else:
            raise ValueError(f"Unsupported image type: {type(image_source)}")
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Prepare sample
        sample = {'image': image, 'index': idx}
        
        # Add task labels
        import torch
        for task_name, labels in self.task_labels.items():
            task_sample = {}
            for label_name, values in labels.items():
                if idx < len(values):
                    label = values[idx]
                    if not isinstance(label, torch.Tensor):
                        label = torch.tensor(label, dtype=torch.float32)
                    task_sample[label_name] = label
            sample[task_name] = task_sample
        
        return sample













