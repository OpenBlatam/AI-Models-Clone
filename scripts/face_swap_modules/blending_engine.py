"""
Blending Engine Module
======================
Módulo para blending avanzado (FFT, Poisson, multi-scale, seamless cloning).
Refactorizado para seguir principios SOLID y DRY.
Usa las mejores librerías disponibles para máxima calidad.
"""

import cv2
import numpy as np
from typing import Optional

from .constants import (
    MASK_BLUR_SMALL, MASK_BLUR_MEDIUM, MASK_BLUR_LARGE,
    DEFAULT_PYRAMID_LEVELS, FFT_COLOR_BLEND_FACTOR,
    ADVANCED_BLEND_FFT_WEIGHT, ADVANCED_BLEND_POISSON_WEIGHT,
    SEAMLESS_DILATE_SIZE
)
from .base import ImageProcessor

# Importar librerías opcionales avanzadas
try:
    from scipy import ndimage, signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from skimage import restoration, filters
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

try:
    import kornia
    KORNIA_AVAILABLE = True
except ImportError:
    KORNIA_AVAILABLE = False

try:
    from .optimizations import fast_mask_blending, is_numba_available
    OPTIMIZATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZATIONS_AVAILABLE = False


class BlendingEngine:
    """
    Motor de blending con múltiples técnicas avanzadas.
    
    Técnicas disponibles:
    - FFT blending (preserva detalles de alta frecuencia)
    - Poisson blending (basado en gradientes)
    - Multi-scale blending (6 niveles)
    - Seamless cloning (OpenCV)
    """
    
    def frequency_domain_blending(self, source: np.ndarray, target: np.ndarray,
                                 mask: np.ndarray) -> np.ndarray:
        """Blending usando análisis de frecuencia (FFT) para preservar detalles."""
        try:
            # Convertir a escala de grises
            source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY).astype(np.float32)
            target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY).astype(np.float32)
            
            # Aplicar FFT
            source_fft = np.fft.fft2(source_gray)
            target_fft = np.fft.fft2(target_gray)
            
            # Separar magnitud y fase
            source_magnitude = np.abs(source_fft)
            source_phase = np.angle(source_fft)
            target_magnitude = np.abs(target_fft)
            target_phase = np.angle(target_fft)
            
            # Crear máscara en dominio de frecuencia
            mask_fft = cv2.resize(mask, (source_gray.shape[1], source_gray.shape[0]))
            mask_fft = cv2.GaussianBlur(mask_fft, MASK_BLUR_LARGE, 0)
            
            # Mezclar magnitudes (preservar detalles de alta frecuencia del source)
            h, w = source_gray.shape
            center_y, center_x = h // 2, w // 2
            y_coords, x_coords = np.ogrid[:h, :w]
            dist_from_center = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            freq_mask = np.clip(dist_from_center / max_dist, 0, 1)  # 0 = baja freq, 1 = alta freq
            
            # Mezclar: alta frecuencia del source, baja frecuencia del target
            blended_magnitude = (source_magnitude * freq_mask * mask_fft + 
                               target_magnitude * (1 - freq_mask * mask_fft))
            
            # Usar fase del target para mejor integración
            blended_phase = target_phase * (1 - mask_fft * 0.3) + source_phase * (mask_fft * 0.3)
            
            # Reconstruir
            blended_fft = blended_magnitude * np.exp(1j * blended_phase)
            result_gray = np.real(np.fft.ifft2(blended_fft))
            result_gray = np.clip(result_gray, 0, 255)
            
            # Convertir de vuelta a BGR y mezclar con colores
            result_gray_bgr = cv2.cvtColor(result_gray.astype(np.uint8), cv2.COLOR_GRAY2BGR)
            mask_3d = ImageProcessor.create_3d_mask(mask)
            result = (result_gray_bgr.astype(np.float32) * mask_3d + 
                     source.astype(np.float32) * (1 - mask_3d * FFT_COLOR_BLEND_FACTOR))
            
            return np.clip(result, 0, 255).astype(np.uint8)
        except Exception:
            return source
    
    def poisson_blending(self, source: np.ndarray, target: np.ndarray,
                        mask: np.ndarray) -> np.ndarray:
        """Poisson blending avanzado usando gradientes."""
        if not SCIPY_AVAILABLE:
            return self.multi_scale_blending(source, target, mask)
        
        try:
            # Convertir a escala de grises para cálculo
            source_gray = ImageProcessor.convert_bgr_to_gray(source).astype(np.float32)
            target_gray = ImageProcessor.convert_bgr_to_gray(target).astype(np.float32)
            
            # Calcular gradientes mejorados
            grad_x_source = cv2.Sobel(source_gray, cv2.CV_32F, 1, 0, ksize=5)
            grad_y_source = cv2.Sobel(source_gray, cv2.CV_32F, 0, 1, ksize=5)
            
            grad_x_target = cv2.Sobel(target_gray, cv2.CV_32F, 1, 0, ksize=5)
            grad_y_target = cv2.Sobel(target_gray, cv2.CV_32F, 0, 1, ksize=5)
            
            # Mezclar gradientes según máscara con múltiples niveles
            mask_blur_1 = ImageProcessor.apply_gaussian_blur(mask, MASK_BLUR_SMALL)
            mask_blur_2 = ImageProcessor.apply_gaussian_blur(mask, MASK_BLUR_MEDIUM)
            
            # Mezclar gradientes
            grad_x = self._blend_gradients(
                grad_x_source, grad_x_target, mask_blur_1, mask_blur_2
            )
            grad_y = self._blend_gradients(
                grad_y_source, grad_y_target, mask_blur_1, mask_blur_2
            )
            
            # Reconstruir desde gradientes (aproximación mejorada)
            result_gray = self._reconstruct_from_gradients(
                target_gray, source_gray, mask, grad_x, grad_y, mask_blur_1
            )
            
            # Convertir de vuelta a BGR
            result = cv2.cvtColor(ImageProcessor.clip_image(result_gray), cv2.COLOR_GRAY2BGR)
            
            # Mezclar con colores originales preservando saturación
            mask_3d = ImageProcessor.create_3d_mask(mask)
            source_lab = ImageProcessor.convert_bgr_to_lab(source)
            result_lab = ImageProcessor.convert_bgr_to_lab(result)
            
            # Preservar canales de color del source
            result_lab[:, :, 1] = source_lab[:, :, 1] * mask + result_lab[:, :, 1] * (1 - mask)
            result_lab[:, :, 2] = source_lab[:, :, 2] * mask + result_lab[:, :, 2] * (1 - mask)
            result = ImageProcessor.convert_lab_to_bgr(result_lab)
            
            return result
        except Exception:
            return self.multi_scale_blending(source, target, mask)
    
    def _blend_gradients(self, source_grad: np.ndarray, target_grad: np.ndarray,
                        mask_blur_1: np.ndarray, mask_blur_2: np.ndarray) -> np.ndarray:
        """Mezcla gradientes con múltiples niveles de blur."""
        grad = (source_grad * mask_blur_1 + target_grad * (1 - mask_blur_1)) * 0.7
        grad += (source_grad * mask_blur_2 + target_grad * (1 - mask_blur_2)) * 0.3
        return grad
    
    def _reconstruct_from_gradients(self, target_gray: np.ndarray, source_gray: np.ndarray,
                                   mask: np.ndarray, grad_x: np.ndarray, grad_y: np.ndarray,
                                   mask_blur: np.ndarray) -> np.ndarray:
        """Reconstruye imagen desde gradientes mezclados."""
        result_gray = target_gray.copy()
        result_gray[mask > 0.5] = source_gray[mask > 0.5]
        
        # Aplicar corrección de gradientes mejorada
        correction = (grad_x + grad_y) * 0.15
        result_gray = result_gray + correction * mask_blur
        
        return result_gray
    
    def multi_scale_blending(self, source: np.ndarray, target: np.ndarray,
                           mask: np.ndarray, levels: int = DEFAULT_PYRAMID_LEVELS) -> np.ndarray:
        """Blending multi-escala con múltiples niveles."""
        try:
            # Crear pirámides
            source_pyramid = [source.astype(np.float32)]
            target_pyramid = [target.astype(np.float32)]
            mask_pyramid = [mask.astype(np.float32)]
            
            # Construir pirámides
            for i in range(levels - 1):
                source_pyramid.append(cv2.pyrDown(source_pyramid[-1]))
                target_pyramid.append(cv2.pyrDown(target_pyramid[-1]))
                mask_pyramid.append(cv2.pyrDown(mask_pyramid[-1]))
            
            # Blending desde arriba hacia abajo
            blended = source_pyramid[-1] * mask_pyramid[-1][:, :, np.newaxis] + \
                     target_pyramid[-1] * (1 - mask_pyramid[-1][:, :, np.newaxis])
            
            # Reconstruir
            for i in range(levels - 2, -1, -1):
                blended = cv2.pyrUp(blended)
                h, w = source_pyramid[i].shape[:2]
                blended = cv2.resize(blended, (w, h))
                
                blended = blended * mask_pyramid[i][:, :, np.newaxis] + \
                         source_pyramid[i] * (1 - mask_pyramid[i][:, :, np.newaxis])
            
            return ImageProcessor.clip_image(blended)
        except Exception:
            # Fallback simple - usar optimización si está disponible
            if OPTIMIZATIONS_AVAILABLE and is_numba_available():
                return fast_mask_blending(source, target, mask)
            else:
                mask_3d = ImageProcessor.create_3d_mask(mask)
                blended = (source.astype(np.float32) * mask_3d + 
                          target.astype(np.float32) * (1 - mask_3d))
                return ImageProcessor.clip_image(blended)
    
    def seamless_cloning(self, source: np.ndarray, target: np.ndarray,
                        mask: np.ndarray) -> Optional[np.ndarray]:
        """Seamless cloning usando OpenCV."""
        try:
            mask_uint8 = ImageProcessor.convert_to_uint8(mask)
            mask_uint8 = cv2.dilate(mask_uint8, 
                                  np.ones((SEAMLESS_DILATE_SIZE, SEAMLESS_DILATE_SIZE), np.uint8), 
                                  iterations=1)
            
            # Calcular centro óptimo
            moments = cv2.moments(mask_uint8)
            if moments["m00"] > 0:
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                center = (center_x, center_y)
            else:
                h, w = mask.shape[:2]
                center = (w // 2, h // 2)
            
            # Intentar múltiples métodos
            methods = [cv2.NORMAL_CLONE, cv2.MIXED_CLONE]
            for method in methods:
                try:
                    return cv2.seamlessClone(source, target, mask_uint8, center, method)
                except Exception:
                    continue
            return None
        except Exception:
            return None
    
    def blend_advanced(self, source: np.ndarray, target: np.ndarray,
                      mask: np.ndarray) -> np.ndarray:
        """
        Blending avanzado combinando múltiples técnicas.
        
        Prioridad:
        1. FFT blending
        2. Poisson blending (si SciPy disponible)
        3. Multi-scale blending
        4. Seamless cloning (como último recurso)
        """
        # Validación de inputs
        if not isinstance(source, np.ndarray) or not isinstance(target, np.ndarray) or not isinstance(mask, np.ndarray):
            raise TypeError("source, target y mask deben ser np.ndarray")
        if source.size == 0 or target.size == 0 or mask.size == 0:
            raise ValueError("source, target y mask no pueden estar vacíos")
        if source.shape[:2] != target.shape[:2] or source.shape[:2] != mask.shape[:2]:
            raise ValueError("source, target y mask deben tener las mismas dimensiones (H, W)")
        
        # Intentar FFT primero
        try:
            blended_freq = self.frequency_domain_blending(source, target, mask)
            
            # Mezclar con Poisson si está disponible
            if SCIPY_AVAILABLE:
                try:
                    blended_poisson = self.poisson_blending(source, target, mask)
                    # Combinar ambos métodos
                    blended = cv2.addWeighted(
                        blended_freq, ADVANCED_BLEND_FFT_WEIGHT, 
                        blended_poisson, ADVANCED_BLEND_POISSON_WEIGHT, 0
                    )
                except Exception:
                    blended = blended_freq
            else:
                blended = blended_freq
            
            return blended
        except Exception:
            # Fallback a multi-scale
            return self._fallback_blending(source, target, mask)
    
    def blend_ultra_advanced(self, source: np.ndarray, target: np.ndarray,
                            mask: np.ndarray) -> np.ndarray:
        """
        Blending ultra-avanzado con ensemble de múltiples técnicas.
        
        Combina:
        1. FFT blending
        2. Poisson blending
        3. Multi-scale blending
        4. Seamless cloning
        5. Mezcla inteligente con pesos adaptativos
        """
        try:
            results = []
            weights = []
            
            # 1. FFT blending
            try:
                fft_result = self.frequency_domain_blending(source, target, mask)
                results.append(fft_result)
                weights.append(0.3)
            except Exception:
                pass
            
            # 2. Poisson blending
            if SCIPY_AVAILABLE:
                try:
                    poisson_result = self.poisson_blending(source, target, mask)
                    results.append(poisson_result)
                    weights.append(0.35)
                except Exception:
                    pass
            
            # 3. Multi-scale blending
            try:
                multi_scale_result = self.multi_scale_blending(source, target, mask)
                results.append(multi_scale_result)
                weights.append(0.25)
            except Exception:
                pass
            
            # 4. Seamless cloning
            try:
                seamless_result = self.seamless_cloning(source, target, mask)
                if seamless_result is not None:
                    results.append(seamless_result)
                    weights.append(0.1)
            except Exception:
                pass
            
            # Si no hay resultados, usar fallback
            if not results:
                return self._fallback_blending(source, target, mask)
            
            # Normalizar pesos
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                weights = [1.0 / len(results)] * len(results)
            
            # Combinar resultados con pesos
            blended = np.zeros_like(results[0], dtype=np.float32)
            for result, weight in zip(results, weights):
                blended += result.astype(np.float32) * weight
            
            return ImageProcessor.clip_image(blended)
            
        except Exception:
            return self._fallback_blending(source, target, mask)
    
    def _fallback_blending(self, source: np.ndarray, target: np.ndarray,
                          mask: np.ndarray) -> np.ndarray:
        """Fallback blending method."""
        if SCIPY_AVAILABLE:
            try:
                return self.poisson_blending(source, target, mask)
            except Exception:
                return self.multi_scale_blending(source, target, mask)
        else:
            return self.multi_scale_blending(source, target, mask)
    
    def blend(self, source: np.ndarray, target: np.ndarray,
             mask: np.ndarray) -> np.ndarray:
        """
        Alias para blend_advanced() para compatibilidad con código legacy.
        
        Args:
            source: Imagen fuente
            target: Imagen objetivo
            mask: Máscara de blending
            
        Returns:
            Imagen con blending aplicado
        """
        return self.blend_advanced(source, target, mask)








