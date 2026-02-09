"""
Post Processor Module
=====================
Módulo para post-procesamiento final.
Refactorizado para seguir principios SOLID y DRY.
"""

import cv2
import numpy as np
from typing import Optional

from .base import ImageProcessor
from .constants import (
    DETAIL_FINE_WEIGHT, DETAIL_MEDIUM_WEIGHT, DETAIL_COARSE_WEIGHT,
    SKIN_TONE_A_MIN, SKIN_TONE_A_MAX, SKIN_TONE_B_MIN, SKIN_TONE_B_MAX
)

# Constants específicas de post-processing
BILATERAL_FILTER_SIZES = [(9, 70, 70), (7, 50, 50), (5, 35, 35)]
DETAIL_WEIGHTS = [DETAIL_FINE_WEIGHT, DETAIL_MEDIUM_WEIGHT, DETAIL_COARSE_WEIGHT]
CLAHE_CLIP_LIMIT = 3.0
CLAHE_TILE_SIZE = (8, 8)
SKIN_SATURATION_FACTOR = 1.05
NON_SKIN_SATURATION_FACTOR = 1.12
ARTIFACT_STD_MULTIPLIER = 2.0
ARTIFACT_SMOOTH_FACTOR = 0.3
COHERENCE_THRESHOLD = 0.5
COHERENCE_SMOOTH_FACTOR = 0.3
FINAL_SHARPEN_KERNEL = np.array([[0, -0.1, 0],
                                 [-0.1, 1.4, -0.1],
                                 [0, -0.1, 0]])
FINAL_SHARPEN_WEIGHT = 0.05
FINAL_BASE_WEIGHT = 0.95
FINAL_BILATERAL_SIZE = 3
FINAL_BILATERAL_PARAMS = (20, 20)


class PostProcessor:
    """
    Post-procesador para mejora final de calidad.
    
    Funcionalidades:
    - Post-procesamiento avanzado
    - Reducción de artefactos
    - Mejora de detalles finos
    - Análisis de coherencia espacial
    - Ultra final enhancement (pipeline completo)
    """
    
    def advanced_post_processing(self, image: np.ndarray, target: np.ndarray,
                                mask: np.ndarray) -> np.ndarray:
        """Post-procesamiento ultra avanzado para máxima calidad."""
        try:
            # Preservar detalles finos en múltiples escalas
            image_original = image.copy()
            
            details_fine = image.astype(np.float32) - cv2.GaussianBlur(image, (3, 3), 0).astype(np.float32)
            details_medium = image.astype(np.float32) - cv2.GaussianBlur(image, (5, 5), 0).astype(np.float32)
            details_coarse = image.astype(np.float32) - cv2.GaussianBlur(image, (7, 7), 0).astype(np.float32)
            
            # Reducción de ruido preservando detalles (múltiples pasos)
            image = self._apply_bilateral_filtering(image)
            
            # Restaurar detalles en múltiples escalas
            image = self._restore_multi_scale_details(
                image, details_fine, details_medium, details_coarse
            )
            
            # Mejora de contraste y saturación adaptativa
            image = self._enhance_contrast_and_saturation(image)
            
            return image
        except Exception:
            return image
    
    def _apply_bilateral_filtering(self, image: np.ndarray) -> np.ndarray:
        """Apply multiple bilateral filters to reduce noise."""
        for d, sigma_color, sigma_space in BILATERAL_FILTER_SIZES:
            image = ImageProcessor.apply_bilateral_filter(image, d, sigma_color, sigma_space)
        return image
    
    def _restore_multi_scale_details(self, image: np.ndarray, details_fine: np.ndarray,
                                    details_medium: np.ndarray, 
                                    details_coarse: np.ndarray) -> np.ndarray:
        """Restore multi-scale details to image."""
        image = image.astype(np.float32) + \
               details_fine * DETAIL_WEIGHTS[0] + \
               details_medium * DETAIL_WEIGHTS[1] + \
               details_coarse * DETAIL_WEIGHTS[2]
        return ImageProcessor.clip_image(image)
    
    def _enhance_contrast_and_saturation(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast and saturation with skin tone preservation."""
        lab = ImageProcessor.convert_bgr_to_lab(image)
        l, a, b = cv2.split(lab)
        
        # CLAHE optimizado
        clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_SIZE)
        l = clahe.apply(l)
        
        # Mejora de saturación adaptativa con preservación de tonos de piel
        a_f = a.astype(np.float32)
        b_f = b.astype(np.float32)
        
        # Detectar tonos de piel
        skin_tones = ((a_f > SKIN_TONE_A_MIN) & (a_f < SKIN_TONE_A_MAX) & 
                     (b_f > SKIN_TONE_B_MIN) & (b_f < SKIN_TONE_B_MAX))
        
        # Aumentar saturación más en áreas no-piel
        a_enhanced = np.where(skin_tones, a_f * SKIN_SATURATION_FACTOR, 
                            a_f * NON_SKIN_SATURATION_FACTOR)
        b_enhanced = np.where(skin_tones, b_f * SKIN_SATURATION_FACTOR, 
                            b_f * NON_SKIN_SATURATION_FACTOR)
        
        a = ImageProcessor.clip_image(a_enhanced)
        b = ImageProcessor.clip_image(b_enhanced)
        
        image = cv2.merge([l, a, b])
        return ImageProcessor.convert_lab_to_bgr(image)
    
    def reduce_artifacts_advanced(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Reducción avanzada de artefactos usando múltiples técnicas."""
        try:
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # Detectar artefactos usando análisis de gradientes
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Detectar patrones anómalos (artefactos)
            artifact_mask = self._detect_artifacts(grad_magnitude)
            
            # Aplicar suavizado selectivo en regiones con artefactos
            return self._smooth_artifacts(image, artifact_mask)
        except Exception:
            return image
    
    def _detect_artifacts(self, grad_magnitude: np.ndarray) -> np.ndarray:
        """Detect artifacts using gradient analysis."""
        grad_mean = np.mean(grad_magnitude)
        grad_std = np.std(grad_magnitude)
        artifact_mask = (grad_magnitude > grad_mean + ARTIFACT_STD_MULTIPLIER * grad_std).astype(np.float32)
        return ImageProcessor.apply_gaussian_blur(artifact_mask, (5, 5))
    
    def _smooth_artifacts(self, image: np.ndarray, artifact_mask: np.ndarray) -> np.ndarray:
        """Apply selective smoothing to artifact regions."""
        artifact_mask_3d = ImageProcessor.create_3d_mask(artifact_mask)
        smoothed = ImageProcessor.apply_bilateral_filter(image, 5, 20, 20)
        result = image.astype(np.float32) * (1 - artifact_mask_3d * ARTIFACT_SMOOTH_FACTOR) + \
                smoothed.astype(np.float32) * (artifact_mask_3d * ARTIFACT_SMOOTH_FACTOR)
        return ImageProcessor.clip_image(result)
    
    def enhance_fine_details(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Mejora de detalles finos preservando textura natural."""
        try:
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # Extraer detalles en múltiples escalas
            details_1 = gray.astype(np.float32) - ImageProcessor.apply_gaussian_blur(gray, (3, 3)).astype(np.float32)
            details_2 = gray.astype(np.float32) - ImageProcessor.apply_gaussian_blur(gray, (5, 5)).astype(np.float32)
            details_3 = gray.astype(np.float32) - ImageProcessor.apply_gaussian_blur(gray, (7, 7)).astype(np.float32)
            
            # Combinar detalles con pesos adaptativos
            combined_details = details_1 * 0.5 + details_2 * 0.3 + details_3 * 0.2
            
            # Aplicar máscara
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (5, 5))
            combined_details = combined_details * mask_blur
            
            # Aplicar detalles
            result = image.copy().astype(np.float32)
            for c in range(3):
                result[:, :, c] = result[:, :, c] + combined_details * 0.1
            
            return ImageProcessor.clip_image(result)
        except:
            return image
    
    def final_save_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Mejora final antes de guardar para máxima calidad."""
        # Sharpening final muy sutil
        sharpened = cv2.filter2D(image, -1, FINAL_SHARPEN_KERNEL)
        image = cv2.addWeighted(image, FINAL_BASE_WEIGHT, sharpened, FINAL_SHARPEN_WEIGHT, 0)
        
        # Reducción final de ruido muy sutil
        image = ImageProcessor.apply_bilateral_filter(
            image, FINAL_BILATERAL_SIZE, 
            FINAL_BILATERAL_PARAMS[0], FINAL_BILATERAL_PARAMS[1]
        )
        
        return image
    
    def ultra_final_enhancement(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Mejora ultra-final con todas las técnicas avanzadas.
        
        Combina:
        - Advanced post-processing
        - Artifact reduction
        - Fine detail enhancement
        - Spatial coherence analysis
        - Final save enhancement
        """
        try:
            result = image.copy()
            
            # 1. Post-procesamiento avanzado
            result = self.advanced_post_processing(result, result, mask)
            
            # 2. Reducción avanzada de artefactos
            result = self.reduce_artifacts_advanced(result, mask)
            
            # 3. Mejora de detalles finos
            result = self.enhance_fine_details(result, mask)
            
            # 4. Análisis de coherencia espacial
            result = self.analyze_spatial_coherence(result, mask)
            
            # 5. Mejora final antes de guardar
            result = self.final_save_enhancement(result)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def analyze_spatial_coherence(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Análisis de coherencia espacial para mejor integración."""
        try:
            # Analizar gradientes locales
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # Calcular gradientes en X e Y
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Analizar coherencia local usando varianza de gradientes
            kernel_size = 5
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            local_mean = cv2.filter2D(grad_magnitude, -1, kernel)
            local_var = cv2.filter2D((grad_magnitude - local_mean)**2, -1, kernel)
            
            # Crear máscara de coherencia (baja varianza = alta coherencia)
            coherence = 1.0 / (1.0 + local_var / (local_mean + 1e-6))
            coherence = np.clip(coherence, 0, 1)
            
            # Aplicar suavizado en regiones de baja coherencia
            return self._smooth_low_coherence_regions(image, coherence)
            
        except Exception:
            return image
    
    def _smooth_low_coherence_regions(self, image: np.ndarray, 
                                     coherence: np.ndarray) -> np.ndarray:
        """Apply smoothing to low coherence regions."""
        low_coherence_mask = (coherence < COHERENCE_THRESHOLD).astype(np.float32)
        low_coherence_mask = ImageProcessor.apply_gaussian_blur(low_coherence_mask, (7, 7))
        
        # Aplicar bilateral filter selectivo en regiones de baja coherencia
        result = image.copy()
        if np.sum(low_coherence_mask) > 0:
            smoothed = ImageProcessor.apply_bilateral_filter(image, 5, 20, 20)
            low_coherence_mask_3d = ImageProcessor.create_3d_mask(low_coherence_mask)
            result = (
                result.astype(np.float32) * (1 - low_coherence_mask_3d * COHERENCE_SMOOTH_FACTOR) +
                smoothed.astype(np.float32) * (low_coherence_mask_3d * COHERENCE_SMOOTH_FACTOR)
            )
            return ImageProcessor.clip_image(result)
        
        return image








