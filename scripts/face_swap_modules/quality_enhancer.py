"""
Quality Enhancer Module
========================
Módulo para mejora de calidad (perceptual, detalles, características).
Refactorizado para seguir principios SOLID y DRY.
Usa las mejores librerías disponibles para máxima calidad.
"""

import cv2
import numpy as np
from typing import Optional, Dict

from .base import ImageProcessor, LandmarkFormatHandler
from .constants import (
    SHARPNESS_THRESHOLD, CONTRAST_THRESHOLD, UNIFORMITY_THRESHOLD,
    SHARPNESS_BASE_WEIGHT, SHARPNESS_ENHANCE_WEIGHT,
    SHARPNESS_KERNEL_STRONG, SHARPNESS_KERNEL_MEDIUM, SHARPNESS_KERNEL_ADAPTIVE,
    SHARPNESS_WEIGHT_MEDIUM, CONTRAST_MULTIPLIER,
    DETAIL_WEIGHT_FINE, DETAIL_WEIGHT_MEDIUM, DETAIL_WEIGHT_COARSE,
    DETAIL_APPLY_WEIGHT, SHARPNESS_COMPARISON_FACTOR,
    PRESERVE_DETAIL_WEIGHT, FEATURE_ENHANCE_WEIGHT
)

# Importar librerías avanzadas opcionales
try:
    from skimage import filters, restoration
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

try:
    import kornia
    KORNIA_AVAILABLE = True
except ImportError:
    KORNIA_AVAILABLE = False

try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Fallback sin decorador
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from .optimizations import (
        fast_laplacian_variance,
        fast_mask_blending,
        is_numba_available
    )
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False


class QualityEnhancer:
    """
    Mejora de calidad con análisis perceptual y técnicas avanzadas.
    
    Funcionalidades:
    - Análisis perceptual automático
    - Mejora adaptativa de calidad
    - Preservación de características visuales
    - Mejora de detalles de alta frecuencia
    """
    
    def perceptual_quality_analysis(self, image: np.ndarray) -> Dict[str, float]:
        """Análisis perceptual de calidad de imagen (optimizado)."""
        metrics = {}
        
        try:
            # Convertir a escala de grises
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # 1. Análisis de nitidez (sharpness) - optimizado
            if OPTIMIZATIONS_AVAILABLE and is_numba_available():
                sharpness = fast_laplacian_variance(gray.astype(np.float64))
            else:
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                sharpness = laplacian.var()
            metrics['sharpness'] = float(sharpness)
            
            # 2. Análisis de contraste
            contrast = gray.std()
            metrics['contrast'] = float(contrast)
            
            # 3. Análisis de brillo
            brightness = gray.mean()
            metrics['brightness'] = float(brightness)
            
            # 4. Análisis de textura (entropía)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten()
            hist = hist / (hist.sum() + 1e-6)  # Normalizar
            entropy = -np.sum(hist * np.log(hist + 1e-6))
            metrics['texture_entropy'] = float(entropy)
            
            # 5. Análisis de uniformidad
            uniformity = np.sum(hist ** 2)
            metrics['uniformity'] = float(uniformity)
            
        except:
            pass
        
        return metrics
    
    def enhance_perceptual_quality(self, image: np.ndarray) -> np.ndarray:
        """Mejora perceptual de calidad basada en análisis."""
        try:
            # Analizar calidad perceptual
            metrics = self.perceptual_quality_analysis(image)
            
            if not metrics:
                return image
            
            # Ajustar según métricas
            result = image.copy()
            
            # Mejorar nitidez si es baja
            if metrics.get('sharpness', 0) < SHARPNESS_THRESHOLD:
                sharpened = cv2.filter2D(result, -1, SHARPNESS_KERNEL_STRONG)
                result = cv2.addWeighted(
                    result, SHARPNESS_BASE_WEIGHT, 
                    sharpened, SHARPNESS_ENHANCE_WEIGHT, 0
                )
            
            # Mejorar contraste si es bajo
            if metrics.get('contrast', 0) < CONTRAST_THRESHOLD:
                lab = ImageProcessor.convert_bgr_to_lab(result)
                l, a, b = cv2.split(lab)
                l = np.clip(l.astype(np.float32) * CONTRAST_MULTIPLIER, 0, 255).astype(np.uint8)
                result = cv2.merge([l, a, b])
                result = ImageProcessor.convert_lab_to_bgr(result)
            
            # Mejorar textura si es muy uniforme
            if metrics.get('uniformity', 0) > UNIFORMITY_THRESHOLD:
                # Aplicar filtro de textura sutil
                gray = ImageProcessor.convert_bgr_to_gray(result)
                texture = cv2.Laplacian(gray, cv2.CV_64F)
                texture = np.abs(texture)
                texture = ImageProcessor.apply_gaussian_blur(texture, (5, 5))
                if texture.max() > 0:
                    texture = np.clip(texture / texture.max(), 0, 1)
                    texture_3d = np.stack([texture] * 3, axis=2)
                    # Aplicar sharpening selectivo
                    kernel = np.array([[-0.1, -0.2, -0.1],
                                      [-0.2,  1.2, -0.2],
                                      [-0.1, -0.2, -0.1]])
                    sharpened = cv2.filter2D(result, -1, kernel)
                    result = result.astype(np.float32) * (1 - texture_3d * 0.1) + \
                            sharpened.astype(np.float32) * (texture_3d * 0.1)
                    result = np.clip(result, 0, 255).astype(np.uint8)
            
        except Exception:
            pass
        
        return result
    
    
    def enhance_high_frequency_details(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Mejora de detalles de alta frecuencia preservando textura natural."""
        try:
            # Convertir a escala de grises para análisis
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # Extraer detalles de alta frecuencia usando múltiples kernels
            details_fine = gray.astype(np.float32) - ImageProcessor.apply_gaussian_blur(gray, (3, 3)).astype(np.float32)
            details_medium = gray.astype(np.float32) - ImageProcessor.apply_gaussian_blur(gray, (5, 5)).astype(np.float32)
            details_coarse = gray.astype(np.float32) - ImageProcessor.apply_gaussian_blur(gray, (7, 7)).astype(np.float32)
            
            # Combinar detalles con pesos adaptativos
            combined_details = (
                details_fine * DETAIL_WEIGHT_FINE +
                details_medium * DETAIL_WEIGHT_MEDIUM +
                details_coarse * DETAIL_WEIGHT_COARSE
            )
            
            # Aplicar máscara para enfocar en región facial
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (5, 5))
            combined_details = combined_details * mask_blur
            
            # Aplicar detalles mejorados
            result = image.copy().astype(np.float32)
            for c in range(3):
                result[:, :, c] = np.clip(
                    result[:, :, c] + combined_details * DETAIL_APPLY_WEIGHT,
                    0, 255
                )
            
            return result.astype(np.uint8)
            
        except Exception:
            return image
    
    def enhance_facial_features(self, image: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """Mejora de características faciales específicas (ojos, boca, etc.)."""
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return image
        
        try:
            # Crear máscara de atención usando LandmarkFormatHandler
            h, w = image.shape[:2]
            attention_mask = np.zeros((h, w), dtype=np.float32)
            
            # Obtener regiones usando utilidad
            left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
            right_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye')
            nose = LandmarkFormatHandler.get_feature_region(landmarks, 'nose')
            mouth = LandmarkFormatHandler.get_feature_region(landmarks, 'mouth')
            
            # Crear máscaras para regiones importantes
            for region in [left_eye, right_eye, nose, mouth]:
                if region is not None and len(region) > 0:
                    center = np.mean(region, axis=0)
                    radius = np.max([np.linalg.norm(p - center) for p in region]) * 1.5
                    
                    y_coords, x_coords = np.ogrid[:h, :w]
                    dist = np.sqrt((x_coords - center[0])**2 + (y_coords - center[1])**2)
                    region_mask = np.clip(1 - dist / radius, 0, 1) ** 2
                    attention_mask = np.maximum(attention_mask, region_mask)
            
            attention_mask = ImageProcessor.apply_gaussian_blur(attention_mask, (5, 5))
            
            # Aplicar sharpening selectivo
            gray = ImageProcessor.convert_bgr_to_gray(image)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            detail_mask = np.abs(laplacian)
            detail_mask = ImageProcessor.apply_gaussian_blur(detail_mask, (5, 5))
            if detail_mask.max() > 0:
                detail_mask = np.clip(detail_mask / detail_mask.max(), 0, 1)
            else:
                detail_mask = np.zeros_like(detail_mask)
            
            # Combinar máscaras
            combined_mask = attention_mask * detail_mask
            combined_mask_3d = ImageProcessor.create_3d_mask(combined_mask)
            
            # Sharpening adaptativo
            sharpened = cv2.filter2D(image, -1, SHARPNESS_KERNEL_ADAPTIVE)
            
            image_f = image.astype(np.float32)
            sharpened_f = sharpened.astype(np.float32)
            
            result = image_f * (1 - combined_mask_3d * FEATURE_ENHANCE_WEIGHT) + \
                    sharpened_f * (combined_mask_3d * FEATURE_ENHANCE_WEIGHT)
            return np.clip(result, 0, 255).astype(np.uint8)
            
        except Exception:
            return image
    
    def preserve_visual_features(self, source: np.ndarray, target: np.ndarray,
                                mask: np.ndarray) -> np.ndarray:
        """Preserva características visuales importantes del source."""
        try:
            # Analizar características visuales
            source_metrics = self.perceptual_quality_analysis(source)
            target_metrics = self.perceptual_quality_analysis(target)
            
            if not source_metrics or not target_metrics:
                return source
            
            # Preservar nitidez del source si es mejor
            if source_metrics.get('sharpness', 0) > target_metrics.get('sharpness', 0) * SHARPNESS_COMPARISON_FACTOR:
                return self._apply_source_details(source, mask)
            
        except Exception:
            pass
        
        return source
    
    def _apply_source_details(self, source: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Apply high-frequency details from source image."""
        source_gray = ImageProcessor.convert_bgr_to_gray(source)
        
        source_details = source_gray.astype(np.float32) - \
                        ImageProcessor.apply_gaussian_blur(source_gray, (3, 3)).astype(np.float32)
        
        mask_blur = ImageProcessor.apply_gaussian_blur(mask, (7, 7))
        mask_3d = ImageProcessor.create_3d_mask(mask_blur)
        
        # Aplicar detalles del source
        result = source.astype(np.float32) + \
                ImageProcessor.create_3d_mask(source_details) * mask_3d * PRESERVE_DETAIL_WEIGHT
        return ImageProcessor.clip_image(result)








