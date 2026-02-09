"""
Color Corrector Module
======================
Módulo para corrección de color avanzada.
Refactorizado para mejorar mantenibilidad y reducir duplicación.
"""

import cv2
import numpy as np
from typing import Optional
from .base import LandmarkFormatHandler, ImageProcessor
from .constants import (
    HISTOGRAM_WEIGHT, LAB_WEIGHT, MASK_EXPONENT,
    SURROUNDING_MASK_SIZE, LUMINOSITY_BLEND_FACTOR
)

# Importar librerías opcionales
try:
    from skimage import exposure, filters, restoration
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

try:
    from .optimizations import fast_histogram_matching, is_numba_available
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False


class ColorCorrector:
    """
    Corrector de color con múltiples métodos avanzados.
    
    Funcionalidades:
    - Histogram matching optimizado
    - LAB color space matching
    - Adaptive luminosity blending
    - Attention masks
    - Surrounding color analysis
    """
    
    def correct_color_histogram(self, source: np.ndarray, target: np.ndarray,
                               mask: np.ndarray) -> np.ndarray:
        """Corrección de color usando histogram matching (optimizado)."""
        if not SKIMAGE_AVAILABLE:
            return source
        
        try:
            result = source.copy()
            mask_uint8 = (mask * 255).astype(np.uint8)
            
            # Calcular histograma y CDF del target una vez
            target_hist = np.zeros((3, 256))
            target_cdf = np.zeros((3, 256))
            
            for i in range(3):
                target_channel = target[:, :, i]
                hist, _ = np.histogram(target_channel.flatten(), bins=256, range=(0, 256))
                target_hist[i] = hist / (hist.sum() + 1e-10)
                target_cdf[i] = np.cumsum(target_hist[i])
            
            # Usar optimización Numba si está disponible
            if OPTIMIZATIONS_AVAILABLE and is_numba_available():
                for i in range(3):
                    source_channel = source[:, :, i]
                    matched = fast_histogram_matching(
                        source_channel,
                        target_hist[i],
                        target_cdf[i]
                    )
                    result[:, :, i] = np.where(mask_uint8 > 128, matched, source_channel)
            else:
                # Fallback a scikit-image
                for i in range(3):
                    source_channel = source[:, :, i]
                    target_channel = target[:, :, i]
                    
                    matched = exposure.match_histograms(
                        source_channel,
                        target_channel,
                        channel_axis=None
                    )
                    
                    result[:, :, i] = np.where(mask_uint8 > 128, matched, source_channel)
            
            return result
        except:
            return source
    
    def correct_color_lab(self, source: np.ndarray, target: np.ndarray,
                          mask: np.ndarray) -> np.ndarray:
        """Corrección de color usando espacio LAB estadístico."""
        try:
            source_lab = ImageProcessor.convert_bgr_to_lab(source).astype(np.float32)
            target_lab = ImageProcessor.convert_bgr_to_lab(target).astype(np.float32)
            mask_3d = ImageProcessor.create_3d_mask(mask)
            
            # Calculate weighted statistics
            mask_weighted = mask ** MASK_EXPONENT
            mask_weighted_3d = ImageProcessor.create_3d_mask(mask_weighted)
            
            source_mean = self._calculate_weighted_mean(source_lab, mask_weighted_3d, mask_weighted)
            source_std = self._calculate_weighted_std(source_lab, source_mean, mask_weighted_3d, mask_weighted)
            
            # Calculate surrounding area statistics
            surrounding_mask = 1 - mask
            surrounding_mask = ImageProcessor.apply_gaussian_blur(
                surrounding_mask, (SURROUNDING_MASK_SIZE, SURROUNDING_MASK_SIZE)
            )
            surrounding_mask_3d = ImageProcessor.create_3d_mask(surrounding_mask)
            
            target_mean = self._calculate_weighted_mean(target_lab, surrounding_mask_3d, surrounding_mask)
            target_std = self._calculate_weighted_std(target_lab, target_mean, surrounding_mask_3d, surrounding_mask)
            
            # Apply transformation
            corrected_lab = self._apply_lab_transformation(
                source_lab, source_mean, source_std, target_mean, target_std
            )
            
            # Luminosity adjustment with adaptive blending
            corrected_lab = self._blend_luminosity(corrected_lab, target_lab, mask)
            
            result = ImageProcessor.convert_lab_to_bgr(
                ImageProcessor.clip_image(corrected_lab)
            )
            return result
        except Exception:
            return source
    
    def _calculate_weighted_mean(self, image: np.ndarray, mask_3d: np.ndarray, 
                                mask: np.ndarray) -> np.ndarray:
        """Calculate weighted mean of image channels."""
        return np.sum(image * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
    
    def _calculate_weighted_std(self, image: np.ndarray, mean: np.ndarray,
                                mask_3d: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Calculate weighted standard deviation of image channels."""
        variance = np.sum(((image - mean) ** 2) * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
        return np.sqrt(variance) + 1e-6
    
    def _apply_lab_transformation(self, source_lab: np.ndarray, source_mean: np.ndarray,
                                 source_std: np.ndarray, target_mean: np.ndarray,
                                 target_std: np.ndarray) -> np.ndarray:
        """Apply LAB color space transformation."""
        corrected_lab = source_lab.copy()
        corrected_lab = (corrected_lab - source_mean) * (target_std / source_std) + target_mean
        return corrected_lab
    
    def _blend_luminosity(self, corrected_lab: np.ndarray, target_lab: np.ndarray,
                         mask: np.ndarray) -> np.ndarray:
        """Blend luminosity channel adaptively."""
        l_channel = corrected_lab[:, :, 0]
        target_l_channel = target_lab[:, :, 0]
        
        l_mask = cv2.GaussianBlur(mask, (71, 71), 0) * LUMINOSITY_BLEND_FACTOR + 0.3
        l_blended = l_channel * l_mask + target_l_channel * (1 - l_mask * 0.4)
        corrected_lab[:, :, 0] = l_blended
        return corrected_lab
    
    def correct_color_dual(self, source: np.ndarray, target: np.ndarray,
                          mask: np.ndarray) -> np.ndarray:
        """
        Corrección de color dual combinando histogram matching y LAB.
        
        Peso: 40% histogram, 60% LAB
        """
        # Validación de inputs
        if not isinstance(source, np.ndarray) or not isinstance(target, np.ndarray) or not isinstance(mask, np.ndarray):
            raise TypeError("source, target y mask deben ser np.ndarray")
        if source.size == 0 or target.size == 0 or mask.size == 0:
            raise ValueError("source, target y mask no pueden estar vacíos")
        if source.shape[:2] != target.shape[:2] or source.shape[:2] != mask.shape[:2]:
            raise ValueError("source, target y mask deben tener las mismas dimensiones (H, W)")
        
        # Histogram matching (40%)
        result_hist = self.correct_color_histogram(source, target, mask)
        
        # LAB estadístico (60%)
        result_lab = self.correct_color_lab(source, target, mask)
        
        # Combinar ambos métodos
        result = cv2.addWeighted(result_hist, 0.4, result_lab, 0.6, 0)
        return result.astype(np.uint8)
    
    def create_attention_mask(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Crea máscara de atención para enfocar en regiones faciales importantes."""
        h, w = image.shape[:2]
        attention_mask = np.zeros((h, w), dtype=np.float32)
        
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return np.ones((h, w), dtype=np.float32)
        
        try:
            # Get feature regions using utility
            feature_regions = {
                'left_eye': (LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye'), 1.0),
                'right_eye': (LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye'), 1.0),
                'nose': (LandmarkFormatHandler.get_feature_region(landmarks, 'nose'), 0.8),
                'mouth': (LandmarkFormatHandler.get_feature_region(landmarks, 'mouth'), 0.9)
            }
            
            # Create elliptical masks for each region
            for region, weight in feature_regions.values():
                if region is not None and len(region) > 0:
                    center = np.mean(region, axis=0)
                    radius = np.max([np.linalg.norm(p - center) for p in region]) * 1.5
                    
                    y_coords, x_coords = np.ogrid[:h, :w]
                    dist = np.sqrt((x_coords - center[0])**2 + (y_coords - center[1])**2)
                    region_mask = np.clip(1 - dist / radius, 0, 1) ** 2
                    attention_mask = np.maximum(attention_mask, region_mask * weight)
            
            # Smooth and normalize
            attention_mask = ImageProcessor.apply_gaussian_blur(attention_mask, (21, 21))
            attention_mask = np.clip(attention_mask, 0.3, 1.0)
            
        except Exception:
            return np.ones((h, w), dtype=np.float32)
        
        return attention_mask
    
    def correct_color(self, source: np.ndarray, target: np.ndarray,
                     mask: np.ndarray) -> np.ndarray:
        """
        Alias para correct_color_dual() para compatibilidad con código legacy.
        
        Args:
            source: Imagen fuente
            target: Imagen objetivo
            mask: Máscara de blending
            
        Returns:
            Imagen corregida
        """
        return self.correct_color_dual(source, target, mask)








