"""
Image Enhancer
==============
Mejora de imágenes usando técnicas de IA.
"""

import logging
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional

logger = logging.getLogger(__name__)


class ImageEnhancer:
    """Mejora de imágenes con técnicas de IA."""
    
    def __init__(
        self,
        contrast_factor: float = 1.1,
        saturation_factor: float = 1.15,
        sharpness_radius: int = 1,
        sharpness_percent: int = 150,
        sharpness_threshold: int = 3
    ):
        """
        Inicializar mejorador de imágenes.
        
        Args:
            contrast_factor: Factor de mejora de contraste
            saturation_factor: Factor de mejora de saturación
            sharpness_radius: Radio para filtro de nitidez
            sharpness_percent: Porcentaje de nitidez
            sharpness_threshold: Umbral de nitidez
        """
        self.contrast_factor = contrast_factor
        self.saturation_factor = saturation_factor
        self.sharpness_radius = sharpness_radius
        self.sharpness_percent = sharpness_percent
        self.sharpness_threshold = sharpness_threshold
    
    def enhance(self, image_path: Path) -> Optional[Image.Image]:
        """
        Mejorar imagen usando técnicas de IA.
        
        Args:
            image_path: Ruta a la imagen
        
        Returns:
            Imagen mejorada o None si hay error
        """
        try:
            img = Image.open(image_path)
            
            # Mejorar contraste
            img = self._enhance_contrast(img)
            
            # Mejorar saturación
            img = self._enhance_saturation(img)
            
            # Mejorar nitidez
            img = self._enhance_sharpness(img)
            
            return img
        except Exception as e:
            logger.error(f"Error mejorando imagen {image_path.name}: {e}")
            try:
                return Image.open(image_path)
            except:
                return None
    
    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Mejorar contraste de la imagen."""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(self.contrast_factor)
    
    def _enhance_saturation(self, image: Image.Image) -> Image.Image:
        """Mejorar saturación de la imagen."""
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(self.saturation_factor)
    
    def _enhance_sharpness(self, image: Image.Image) -> Image.Image:
        """Mejorar nitidez de la imagen."""
        return image.filter(
            ImageFilter.UnsharpMask(
                radius=self.sharpness_radius,
                percent=self.sharpness_percent,
                threshold=self.sharpness_threshold
            )
        )







