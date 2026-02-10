"""
Image and video preprocessing utilities
Separated for modularity and reusability
"""

from typing import Union, List, Tuple, Optional
import numpy as np
from PIL import Image
import cv2
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Image preprocessing utilities
    Handles normalization, resizing, format conversion
    """
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (224, 224),
        normalize: bool = True,
        mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
        std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
    ):
        self.target_size = target_size
        self.normalize = normalize
        self.mean = mean
        self.std = std
    
    def preprocess(
        self,
        image: Union[np.ndarray, Image.Image, str]
    ) -> np.ndarray:
        """
        Preprocess image
        
        Args:
            image: Input image (array, PIL Image, or file path)
            
        Returns:
            Preprocessed image as numpy array
        """
        # Load image
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)
            image = Image.fromarray(image)
        
        # Resize
        image = image.resize(self.target_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy
        image_array = np.array(image, dtype=np.float32)
        
        # Normalize
        if self.normalize:
            image_array = image_array / 255.0
            image_array = (image_array - np.array(self.mean)) / np.array(self.std)
        
        return image_array
    
    def preprocess_batch(
        self,
        images: List[Union[np.ndarray, Image.Image, str]]
    ) -> np.ndarray:
        """Preprocess batch of images"""
        return np.array([self.preprocess(img) for img in images])
    
    def enhance_image(
        self,
        image: Union[np.ndarray, Image.Image],
        enhance_type: str = "auto"  # "auto", "brightness", "contrast", "sharpness"
    ) -> np.ndarray:
        """
        Enhance image quality
        
        Args:
            image: Input image
            enhance_type: Type of enhancement
            
        Returns:
            Enhanced image
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        if enhance_type == "auto":
            # Auto-enhance based on image characteristics
            # Convert to numpy for analysis
            img_array = np.array(image)
            
            # Check brightness
            brightness = np.mean(img_array)
            if brightness < 100:
                image = self._enhance_brightness(image)
            
            # Check contrast
            contrast = np.std(img_array)
            if contrast < 30:
                image = self._enhance_contrast(image)
        
        elif enhance_type == "brightness":
            image = self._enhance_brightness(image)
        elif enhance_type == "contrast":
            image = self._enhance_contrast(image)
        elif enhance_type == "sharpness":
            image = self._enhance_sharpness(image)
        
        return np.array(image)
    
    def _enhance_brightness(self, image: Image.Image) -> Image.Image:
        """Enhance image brightness"""
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.2)
    
    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast"""
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.2)
    
    def _enhance_sharpness(self, image: Image.Image) -> Image.Image:
        """Enhance image sharpness"""
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(1.5)


class VideoPreprocessor:
    """
    Video preprocessing utilities
    Handles frame extraction, resizing, sampling
    """
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (224, 224),
        fps: Optional[float] = None
    ):
        self.target_size = target_size
        self.fps = fps
    
    def extract_frames(
        self,
        video_path: str,
        num_frames: Optional[int] = None,
        sampling: str = "uniform"  # "uniform", "random", "all"
    ) -> List[np.ndarray]:
        """
        Extract frames from video
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract (None = all)
            sampling: Frame sampling strategy
            
        Returns:
            List of frame arrays
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if num_frames is None:
            num_frames = total_frames
        
        # Sample frame indices
        if sampling == "uniform":
            step = max(1, total_frames // num_frames)
            frame_indices = [i * step for i in range(min(num_frames, total_frames))]
        elif sampling == "random":
            import random
            frame_indices = sorted(random.sample(range(total_frames), min(num_frames, total_frames)))
        else:  # "all"
            frame_indices = list(range(min(num_frames, total_frames)))
        
        # Extract frames
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, self.target_size)
                frames.append(frame)
        
        cap.release()
        return frames
    
    def preprocess_frames(
        self,
        frames: List[np.ndarray],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Preprocess frames
        
        Args:
            frames: List of frame arrays
            normalize: Whether to normalize
            
        Returns:
            Preprocessed frames as numpy array
        """
        processed = []
        for frame in frames:
            # Resize if needed
            if frame.shape[:2] != self.target_size:
                frame = cv2.resize(frame, self.target_size)
            
            # Normalize
            if normalize:
                frame = frame.astype(np.float32) / 255.0
            
            processed.append(frame)
        
        return np.array(processed)













