"""
Advanced Enhancements Module
=============================
Módulo para mejoras ultra-avanzadas de calidad.
Técnicas de vanguardia para máximo realismo.
"""

import cv2
import numpy as np
from typing import Optional, Dict, Tuple
from .base import ImageProcessor, LandmarkFormatHandler
from .constants import (
    SHARPNESS_THRESHOLD, CONTRAST_THRESHOLD,
    DETAIL_WEIGHT_FINE, DETAIL_WEIGHT_MEDIUM, DETAIL_WEIGHT_COARSE
)

# Importar librerías avanzadas opcionales
try:
    from skimage import restoration, filters, exposure
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

try:
    import kornia
    KORNIA_AVAILABLE = True
except ImportError:
    KORNIA_AVAILABLE = False


class AdvancedEnhancements:
    """
    Mejoras ultra-avanzadas para máximo realismo.
    
    Funcionalidades organizadas por categorías:
    
    **Color & Lighting:**
    - Intelligent lighting adjustment
    - Intelligent color grading
    - Color harmony optimization
    - Neural style preservation
    - Neural style transfer enhancement
    
    **Texture & Expression:**
    - Advanced skin texture preservation
    - Advanced texture synthesis
    - Advanced expression preservation
    
    **Quality Enhancement:**
    - Perceptual loss optimization
    - Adaptive quality control
    - Dynamic quality adaptation
    - Progressive quality enhancement
    - Perceptual optimization advanced
    
    **Filtering & Sharpening:**
    - Edge-aware filtering
    - Frequency domain enhancement
    - Adaptive sharpening multi-scale
    
    **Attention & Boosting:**
    - Attention-based enhancement
    - Gradient boosting enhancement
    
    **Ensemble & Fusion:**
    - Multi-scale ensemble enhancement
    - Advanced ensemble fusion
    - Multi-scale attention fusion
    - Ensemble learning enhancement
    
    **Advanced Techniques:**
    - Adversarial style enhancement
    - Deep feature matching
    - Feature preserving upsampling
    - Meta-learning enhancement
    - Super-resolution adaptive
    - Region adaptive processing
    - Wavelet transform enhancement
    - Advanced frequency analysis
    - Structural similarity optimization
    - Multi-resolution analysis
    - Guided filter enhancement
    - Advanced edge preservation
    - Advanced artifact reduction
    - Color consistency improvement
    """
    
    def __init__(self):
        """Inicializar el enhancer con instancia de QualityEnhancer para reutilización."""
        self._quality_enhancer = None
    
    def _get_quality_enhancer(self):
        """Obtener instancia de QualityEnhancer (lazy initialization)."""
        if self._quality_enhancer is None:
            from .quality_enhancer import QualityEnhancer
            self._quality_enhancer = QualityEnhancer()
        return self._quality_enhancer
    
    def _calculate_quality_score(self, image: np.ndarray) -> float:
        """
        Calcular score de calidad perceptual de una imagen.
        
        Args:
            image: Imagen a analizar
        
        Returns:
            Score de calidad (0.0-1.0)
        """
        try:
            metrics = self._get_quality_enhancer().perceptual_quality_analysis(image)
            if not metrics:
                return 0.5
            
            sharpness_norm = min(metrics.get('sharpness', 0) / 500.0, 1.0)
            contrast_norm = min(metrics.get('contrast', 0) / 100.0, 1.0)
            texture_norm = min(metrics.get('texture_entropy', 0) / 8.0, 1.0)
            
            return (sharpness_norm * 0.4 + contrast_norm * 0.3 + texture_norm * 0.3)
        except Exception:
            return 0.5
    
    def _normalize_weights(self, weights: list) -> list:
        """
        Normalizar lista de pesos a suma 1.0.
        
        Args:
            weights: Lista de pesos
        
        Returns:
            Lista de pesos normalizados
        """
        total = sum(weights)
        if total > 0:
            return [w / total for w in weights]
        else:
            return [1.0 / len(weights)] * len(weights)
    
    def _blend_with_mask(self, source: np.ndarray, target: np.ndarray,
                         mask: np.ndarray, weight: float = 0.5) -> np.ndarray:
        """
        Mezclar dos imágenes usando una máscara.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de mezcla
            weight: Peso de mezcla
        
        Returns:
            Imagen mezclada
        """
        mask_3d = ImageProcessor.create_3d_mask(mask)
        result = source.astype(np.float32) * (1 - mask_3d * weight) + \
                target.astype(np.float32) * (mask_3d * weight)
        return ImageProcessor.clip_image(result)
    
    def super_resolution_adaptive(self, image: np.ndarray, scale: float = 1.5) -> np.ndarray:
        """
        Super-resolution adaptativa usando múltiples técnicas.
        
        Args:
            image: Imagen a mejorar
            scale: Factor de escala (1.5 = 50% más grande)
        
        Returns:
            Imagen con super-resolution aplicada
        """
        try:
            h, w = image.shape[:2]
            target_h, target_w = int(h * scale), int(w * scale)
            
            # Método 1: Lanczos (alta calidad)
            lanczos = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
            
            # Método 2: Bicubic mejorado
            bicubic = cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
            
            # Método 3: EDSR-like (si disponible)
            if SKIMAGE_AVAILABLE:
                # Usar restoration para mejor calidad
                gray = ImageProcessor.convert_bgr_to_gray(bicubic)
                enhanced = restoration.richardson_lucy(gray, np.ones((3, 3)) / 9, num_iter=5)
                enhanced = ImageProcessor.create_3d_mask(enhanced)
                edsr_like = bicubic.astype(np.float32) * 0.7 + enhanced.astype(np.float32) * 0.3
                edsr_like = ImageProcessor.clip_image(edsr_like)
            else:
                edsr_like = bicubic
            
            # Combinar métodos con pesos adaptativos
            result = (
                lanczos.astype(np.float32) * 0.4 +
                bicubic.astype(np.float32) * 0.3 +
                edsr_like.astype(np.float32) * 0.3
            )
            
            # Aplicar sharpening sutil
            kernel = np.array([[-0.05, -0.1, -0.05],
                              [-0.1,  1.5, -0.1],
                              [-0.05, -0.1, -0.05]])
            sharpened = cv2.filter2D(result, -1, kernel)
            result = result * 0.9 + sharpened * 0.1
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            # Fallback simple
            h, w = image.shape[:2]
            target_h, target_w = int(h * scale), int(w * scale)
            return cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
    
    def preserve_skin_texture_advanced(self, source: np.ndarray, target: np.ndarray,
                                     mask: np.ndarray) -> np.ndarray:
        """
        Preservación avanzada de textura de piel usando análisis multi-escala.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región facial
        
        Returns:
            Imagen con textura de piel preservada
        """
        try:
            # Convertir a LAB para mejor análisis de piel
            source_lab = ImageProcessor.convert_bgr_to_lab(source)
            target_lab = ImageProcessor.convert_bgr_to_lab(target)
            
            # Extraer textura en múltiples escalas
            source_gray = ImageProcessor.convert_bgr_to_gray(source)
            target_gray = ImageProcessor.convert_bgr_to_gray(target)
            
            # Análisis multi-escala de textura
            scales = [3, 5, 7, 9]
            texture_preservation = np.zeros_like(source_gray, dtype=np.float32)
            
            for scale in scales:
                # Extraer textura en esta escala
                source_texture = source_gray.astype(np.float32) - \
                               ImageProcessor.apply_gaussian_blur(source_gray, (scale, scale)).astype(np.float32)
                target_texture = target_gray.astype(np.float32) - \
                               ImageProcessor.apply_gaussian_blur(target_gray, (scale, scale)).astype(np.float32)
                
                # Preservar textura del source en región facial
                weight = 1.0 / len(scales)
                texture_preservation += source_texture * mask * weight
            
            # Aplicar textura preservada
            mask_3d = ImageProcessor.create_3d_mask(mask)
            texture_3d = ImageProcessor.create_3d_mask(texture_preservation)
            
            result = target.astype(np.float32) + texture_3d * mask_3d * 0.3
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def intelligent_lighting_adjustment(self, source: np.ndarray, target: np.ndarray,
                                       mask: np.ndarray) -> np.ndarray:
        """
        Ajuste inteligente de iluminación entre source y target.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región facial
        
        Returns:
            Imagen con iluminación ajustada
        """
        try:
            # Convertir a LAB para análisis de luminosidad
            source_lab = ImageProcessor.convert_bgr_to_lab(source)
            target_lab = ImageProcessor.convert_bgr_to_lab(target)
            
            # Extraer canal L (luminosidad)
            source_l = source_lab[:, :, 0].astype(np.float32)
            target_l = target_lab[:, :, 0].astype(np.float32)
            
            # Calcular estadísticas de iluminación
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (21, 21))
            mask_3d = ImageProcessor.create_3d_mask(mask_blur)
            
            # Media y desviación estándar en región facial
            source_mean = np.mean(source_l[mask > 0.5])
            source_std = np.std(source_l[mask > 0.5])
            target_mean = np.mean(target_l[mask > 0.5])
            target_std = np.std(target_l[mask > 0.5])
            
            # Ajustar luminosidad del source para que coincida con target
            if source_std > 0:
                source_l_adjusted = (source_l - source_mean) * (target_std / source_std) + target_mean
            else:
                source_l_adjusted = source_l
            
            # Aplicar ajuste con transición suave
            result_l = target_l * (1 - mask_blur) + source_l_adjusted * mask_blur
            
            # Reconstruir imagen LAB
            result_lab = target_lab.copy()
            result_lab[:, :, 0] = np.clip(result_l, 0, 255).astype(np.uint8)
            
            # Convertir de vuelta a BGR
            return ImageProcessor.convert_lab_to_bgr(result_lab)
            
        except Exception:
            return target
    
    def preserve_expression_advanced(self, source: np.ndarray, target: np.ndarray,
                                    source_landmarks: np.ndarray, target_landmarks: np.ndarray,
                                    mask: np.ndarray) -> np.ndarray:
        """
        Preservación avanzada de expresiones faciales.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            source_landmarks: Landmarks de source
            target_landmarks: Landmarks de target
            mask: Máscara de la región facial
        
        Returns:
            Imagen con expresión preservada
        """
        try:
            if not LandmarkFormatHandler.is_valid_landmarks(source_landmarks) or \
               not LandmarkFormatHandler.is_valid_landmarks(target_landmarks):
                return target
            
            # Obtener regiones de expresión (boca, ojos)
            source_mouth = LandmarkFormatHandler.get_feature_region(source_landmarks, 'mouth')
            target_mouth = LandmarkFormatHandler.get_feature_region(target_landmarks, 'mouth')
            
            if source_mouth is None or target_mouth is None:
                return target
            
            # Calcular transformación de expresión
            source_mouth_center = np.mean(source_mouth, axis=0)
            target_mouth_center = np.mean(target_mouth, axis=0)
            
            # Crear máscara de expresión (boca y alrededores)
            h, w = target.shape[:2]
            expression_mask = np.zeros((h, w), dtype=np.float32)
            
            # Máscara para boca
            mouth_radius = np.max([np.linalg.norm(p - target_mouth_center) for p in target_mouth]) * 2.0
            y_coords, x_coords = np.ogrid[:h, :w]
            dist = np.sqrt((x_coords - target_mouth_center[0])**2 + 
                          (y_coords - target_mouth_center[1])**2)
            expression_mask = np.clip(1 - dist / mouth_radius, 0, 1) ** 2
            
            # Suavizar máscara
            expression_mask = ImageProcessor.apply_gaussian_blur(expression_mask, (9, 9))
            
            # Aplicar expresión del source
            expression_mask_3d = ImageProcessor.create_3d_mask(expression_mask)
            result = target.astype(np.float32) * (1 - expression_mask_3d * 0.4) + \
                    source.astype(np.float32) * (expression_mask_3d * 0.4)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def edge_aware_filtering(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Edge-aware filtering para mejor integración de bordes.
        
        Args:
            image: Imagen a filtrar
            mask: Máscara de la región
        
        Returns:
            Imagen con edge-aware filtering aplicado
        """
        try:
            # Detectar bordes
            gray = ImageProcessor.convert_bgr_to_gray(image)
            edges = cv2.Canny(gray, 50, 150)
            edges = edges.astype(np.float32) / 255.0
            
            # Crear máscara edge-aware
            edge_mask = 1.0 - edges * 0.5  # Reducir filtrado cerca de bordes
            edge_mask = ImageProcessor.apply_gaussian_blur(edge_mask, (5, 5))
            edge_mask_3d = ImageProcessor.create_3d_mask(edge_mask)
            
            # Aplicar bilateral filter edge-aware
            filtered = ImageProcessor.apply_bilateral_filter(image, 5, 20, 20)
            
            # Mezclar con máscara edge-aware
            result = image.astype(np.float32) * edge_mask_3d + \
                    filtered.astype(np.float32) * (1 - edge_mask_3d)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def frequency_domain_enhancement(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Mejora en dominio de frecuencia usando FFT.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
        
        Returns:
            Imagen mejorada en dominio de frecuencia
        """
        try:
            # Convertir a escala de grises para análisis
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # FFT
            fft = np.fft.fft2(gray.astype(np.float32))
            fft_shift = np.fft.fftshift(fft)
            
            # Crear filtro de alta frecuencia mejorado
            h, w = gray.shape
            center_y, center_x = h // 2, w // 2
            y_coords, x_coords = np.ogrid[:h, :w]
            
            # Distancia desde el centro
            dist = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            
            # Filtro de alta frecuencia (preservar detalles)
            high_freq_filter = np.clip(dist / (max_dist * 0.3), 0, 1)
            
            # Aplicar máscara
            mask_fft = np.fft.fftshift(np.fft.fft2(mask.astype(np.float32)))
            mask_magnitude = np.abs(mask_fft)
            
            # Mejorar alta frecuencia en región facial
            enhanced_magnitude = np.abs(fft_shift) * (1 + high_freq_filter * mask_magnitude * 0.2)
            enhanced_phase = np.angle(fft_shift)
            
            # Reconstruir
            enhanced_fft = enhanced_magnitude * np.exp(1j * enhanced_phase)
            enhanced_fft_shift = np.fft.ifftshift(enhanced_fft)
            enhanced_gray = np.real(np.fft.ifft2(enhanced_fft_shift))
            
            # Aplicar a imagen original
            enhancement = (enhanced_gray - gray.astype(np.float32)) * mask
            enhancement_3d = ImageProcessor.create_3d_mask(enhancement)
            
            result = image.astype(np.float32) + enhancement_3d * 0.3
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def adaptive_quality_control(self, image: np.ndarray, target_quality: float = 0.9) -> np.ndarray:
        """
        Control adaptativo de calidad con iteraciones hasta alcanzar objetivo.
        
        Args:
            image: Imagen a mejorar
            target_quality: Calidad objetivo (0-1)
        
        Returns:
            Imagen con calidad mejorada
        """
        try:
            from .quality_enhancer import QualityEnhancer
            
            quality_enhancer = QualityEnhancer()
            current_quality = 0.0
            iterations = 0
            max_iterations = 5
            result = image.copy()
            
            while current_quality < target_quality and iterations < max_iterations:
                # Analizar calidad actual
                metrics = quality_enhancer.perceptual_quality_analysis(result)
                
                if not metrics:
                    break
                
                # Calcular calidad combinada
                sharpness_norm = min(metrics.get('sharpness', 0) / 500.0, 1.0)
                contrast_norm = min(metrics.get('contrast', 0) / 100.0, 1.0)
                texture_norm = min(metrics.get('texture_entropy', 0) / 8.0, 1.0)
                
                current_quality = (sharpness_norm * 0.4 + contrast_norm * 0.3 + texture_norm * 0.3)
                
                if current_quality >= target_quality:
                    break
                
                # Aplicar mejoras incrementales
                result = quality_enhancer.enhance_perceptual_quality(result)
                
                # Sharpening adaptativo
                if metrics.get('sharpness', 0) < SHARPNESS_THRESHOLD:
                    kernel = np.array([[-0.1, -0.2, -0.1],
                                      [-0.2,  1.8, -0.2],
                                      [-0.1, -0.2, -0.1]])
                    sharpened = cv2.filter2D(result, -1, kernel)
                    result = cv2.addWeighted(result, 0.85, sharpened, 0.15, 0)
                
                # Mejora de contraste
                if metrics.get('contrast', 0) < CONTRAST_THRESHOLD:
                    lab = ImageProcessor.convert_bgr_to_lab(result)
                    l, a, b = cv2.split(lab)
                    l = np.clip(l.astype(np.float32) * 1.08, 0, 255).astype(np.uint8)
                    result = cv2.merge([l, a, b])
                    result = ImageProcessor.convert_lab_to_bgr(result)
                
                iterations += 1
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def multi_scale_ensemble_enhancement(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Ensemble multi-escala combinando múltiples técnicas de mejora.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
        
        Returns:
            Imagen mejorada con ensemble multi-escala
        """
        try:
            # Aplicar múltiples técnicas
            enhanced_1 = self.edge_aware_filtering(image, mask)
            enhanced_2 = self.frequency_domain_enhancement(image, mask)
            enhanced_3 = self.adaptive_quality_control(image, target_quality=0.85)
            
            # Combinar con pesos adaptativos
            result = (
                enhanced_1.astype(np.float32) * 0.35 +
                enhanced_2.astype(np.float32) * 0.35 +
                enhanced_3.astype(np.float32) * 0.30
            )
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def progressive_quality_enhancement(self, image: np.ndarray, steps: int = 3) -> np.ndarray:
        """
        Mejora progresiva de calidad en múltiples pasos.
        
        Args:
            image: Imagen a mejorar
            steps: Número de pasos de mejora
        
        Returns:
            Imagen mejorada progresivamente
        """
        try:
            result = image.copy()
            
            for step in range(steps):
                # Mejora incremental
                improvement_factor = (step + 1) / steps
                
                # Sharpening progresivo
                kernel_strength = 1.0 + improvement_factor * 0.3
                kernel = np.array([[-0.05 * kernel_strength, -0.1 * kernel_strength, -0.05 * kernel_strength],
                                  [-0.1 * kernel_strength, 1.0 + 0.5 * kernel_strength, -0.1 * kernel_strength],
                                  [-0.05 * kernel_strength, -0.1 * kernel_strength, -0.05 * kernel_strength]])
                sharpened = cv2.filter2D(result, -1, kernel)
                result = cv2.addWeighted(result, 0.9, sharpened, 0.1, 0)
                
                # Mejora de contraste progresiva
                lab = ImageProcessor.convert_bgr_to_lab(result)
                l, a, b = cv2.split(lab)
                l = np.clip(l.astype(np.float32) * (1.0 + improvement_factor * 0.05), 0, 255).astype(np.uint8)
                result = cv2.merge([l, a, b])
                result = ImageProcessor.convert_lab_to_bgr(result)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def intelligent_color_grading(self, source: np.ndarray, target: np.ndarray,
                                 mask: np.ndarray) -> np.ndarray:
        """
        Color grading inteligente para mejor integración de colores.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con color grading aplicado
        """
        try:
            # Convertir a LAB
            source_lab = ImageProcessor.convert_bgr_to_lab(source)
            target_lab = ImageProcessor.convert_bgr_to_lab(target)
            
            # Calcular estadísticas de color
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (31, 31))
            
            # Media y desviación estándar de canales A y B
            source_a_mean = np.mean(source_lab[:, :, 1][mask > 0.5])
            source_b_mean = np.mean(source_lab[:, :, 2][mask > 0.5])
            target_a_mean = np.mean(target_lab[:, :, 1][mask > 0.5])
            target_b_mean = np.mean(target_lab[:, :, 2][mask > 0.5])
            
            source_a_std = np.std(source_lab[:, :, 1][mask > 0.5])
            source_b_std = np.std(source_lab[:, :, 2][mask > 0.5])
            target_a_std = np.std(target_lab[:, :, 1][mask > 0.5])
            target_b_std = np.std(target_lab[:, :, 2][mask > 0.5])
            
            # Ajustar colores del source
            result_lab = target_lab.copy()
            source_a = source_lab[:, :, 1].astype(np.float32)
            source_b = source_lab[:, :, 2].astype(np.float32)
            
            if source_a_std > 0 and target_a_std > 0:
                source_a_adjusted = (source_a - source_a_mean) * (target_a_std / source_a_std) + target_a_mean
            else:
                source_a_adjusted = source_a
            
            if source_b_std > 0 and target_b_std > 0:
                source_b_adjusted = (source_b - source_b_mean) * (target_b_std / source_b_std) + target_b_mean
            else:
                source_b_adjusted = source_b
            
            # Aplicar con transición suave
            result_lab[:, :, 1] = (target_lab[:, :, 1].astype(np.float32) * (1 - mask_blur) + 
                                  source_a_adjusted * mask_blur).astype(np.uint8)
            result_lab[:, :, 2] = (target_lab[:, :, 2].astype(np.float32) * (1 - mask_blur) + 
                                  source_b_adjusted * mask_blur).astype(np.uint8)
            
            return ImageProcessor.convert_lab_to_bgr(result_lab)
            
        except Exception:
            return target
    
    def texture_synthesis_advanced(self, source: np.ndarray, target: np.ndarray,
                                  mask: np.ndarray) -> np.ndarray:
        """
        Síntesis avanzada de textura para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con textura sintetizada
        """
        try:
            # Extraer textura en múltiples orientaciones
            source_gray = ImageProcessor.convert_bgr_to_gray(source)
            target_gray = ImageProcessor.convert_bgr_to_gray(target)
            
            # Análisis de textura con filtros direccionales
            # Gradientes en múltiples direcciones
            grad_x = cv2.Sobel(source_gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(source_gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Magnitud y dirección de gradientes
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            direction = np.arctan2(grad_y, grad_x)
            
            # Preservar textura direccional
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (7, 7))
            texture_mask = magnitude * mask_blur
            
            # Aplicar textura sintetizada
            texture_3d = ImageProcessor.create_3d_mask(texture_mask)
            result = target.astype(np.float32) + texture_3d * 0.25
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def perceptual_optimization_advanced(self, image: np.ndarray, mask: np.ndarray,
                                        iterations: int = 3) -> np.ndarray:
        """
        Optimización perceptual avanzada con múltiples iteraciones.
        
        Args:
            image: Imagen a optimizar
            mask: Máscara de la región
            iterations: Número de iteraciones
        
        Returns:
            Imagen optimizada perceptualmente
        """
        try:
            result = image.copy()
            
            for i in range(iterations):
                # Análisis perceptual
                gray = ImageProcessor.convert_bgr_to_gray(result)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                sharpness = laplacian.var()
                
                # Mejora adaptativa según análisis
                if sharpness < SHARPNESS_THRESHOLD:
                    # Sharpening más agresivo
                    kernel = np.array([[-0.15, -0.3, -0.15],
                                      [-0.3,  2.2, -0.3],
                                      [-0.15, -0.3, -0.15]])
                    sharpened = cv2.filter2D(result, -1, kernel)
                    result = cv2.addWeighted(result, 0.8, sharpened, 0.2, 0)
                
                # Mejora de contraste perceptual
                contrast = gray.std()
                if contrast < CONTRAST_THRESHOLD:
                    lab = ImageProcessor.convert_bgr_to_lab(result)
                    l, a, b = cv2.split(lab)
                    l = np.clip(l.astype(np.float32) * 1.1, 0, 255).astype(np.uint8)
                    result = cv2.merge([l, a, b])
                    result = ImageProcessor.convert_lab_to_bgr(result)
                
                # Aplicar máscara para enfocar en región facial
                mask_3d = ImageProcessor.create_3d_mask(mask)
                result = result.astype(np.float32) * mask_3d + \
                        image.astype(np.float32) * (1 - mask_3d * 0.3)
                result = ImageProcessor.clip_image(result)
            
            return result
            
        except Exception:
            return image
    
    def region_adaptive_processing(self, image: np.ndarray, mask: np.ndarray,
                                 region_size: Tuple[int, int] = (128, 128)) -> np.ndarray:
        """
        Procesamiento adaptativo por regiones para mejor calidad.
        
        Args:
            image: Imagen a procesar
            mask: Máscara de la región
            region_size: Tamaño de región para procesamiento
        
        Returns:
            Imagen procesada adaptativamente
        """
        try:
            h, w = image.shape[:2]
            rh, rw = region_size
            result = image.copy().astype(np.float32)
            
            # Procesar por regiones con overlap
            overlap = 32
            step_h = rh - overlap
            step_w = rw - overlap
            
            for y in range(0, h, step_h):
                for x in range(0, w, step_w):
                    # Extraer región
                    y_end = min(y + rh, h)
                    x_end = min(x + rw, w)
                    
                    region = image[y:y_end, x:x_end]
                    region_mask = mask[y:y_end, x:x_end]
                    
                    if np.sum(region_mask) > 0:
                        # Aplicar mejoras a región
                        enhanced_region = self.adaptive_quality_control(region, target_quality=0.88)
                        enhanced_region = self.edge_aware_filtering(enhanced_region, region_mask)
                        
                        # Mezclar con transición suave en bordes
                        blend_mask = ImageProcessor.apply_gaussian_blur(region_mask, (15, 15))
                        blend_mask_3d = ImageProcessor.create_3d_mask(blend_mask)
                        
                        result[y:y_end, x:x_end] = (
                            result[y:y_end, x:x_end] * (1 - blend_mask_3d) +
                            enhanced_region.astype(np.float32) * blend_mask_3d
                        )
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def attention_based_enhancement(self, image: np.ndarray, mask: np.ndarray,
                                   attention_regions: Optional[list] = None) -> np.ndarray:
        """
        Mejora basada en mecanismo de atención para regiones importantes.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región facial
            attention_regions: Lista de regiones de atención [(x, y, w, h), ...]
        
        Returns:
            Imagen mejorada con atención
        """
        try:
            h, w = image.shape[:2]
            attention_map = np.zeros((h, w), dtype=np.float32)
            
            # Crear mapa de atención
            if attention_regions:
                for x, y, rw, rh in attention_regions:
                    y_start = max(0, y)
                    y_end = min(h, y + rh)
                    x_start = max(0, x)
                    x_end = min(w, x + rw)
                    
                    # Gradiente radial para atención
                    center_y, center_x = y + rh // 2, x + rw // 2
                    y_coords, x_coords = np.ogrid[y_start:y_end, x_start:x_end]
                    dist = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
                    max_dist = np.sqrt((rw/2)**2 + (rh/2)**2)
                    region_attention = np.clip(1 - dist / max_dist, 0, 1) ** 2
                    attention_map[y_start:y_end, x_start:x_end] = np.maximum(
                        attention_map[y_start:y_end, x_start:x_end], region_attention
                    )
            else:
                # Usar máscara como atención
                attention_map = mask.copy()
            
            # Combinar con detección de bordes para atención adaptativa
            gray = ImageProcessor.convert_bgr_to_gray(image)
            edges = cv2.Canny(gray, 50, 150)
            edge_attention = (edges.astype(np.float32) / 255.0) * 0.3
            attention_map = np.clip(attention_map + edge_attention, 0, 1)
            attention_map = ImageProcessor.apply_gaussian_blur(attention_map, (9, 9))
            
            # Aplicar mejoras con pesos de atención
            attention_map_3d = ImageProcessor.create_3d_mask(attention_map)
            
            # Sharpening adaptativo según atención
            kernel = np.array([[-0.1, -0.2, -0.1],
                              [-0.2,  2.0, -0.2],
                              [-0.1, -0.2, -0.1]])
            sharpened = cv2.filter2D(image, -1, kernel)
            
            result = image.astype(np.float32) * (1 - attention_map_3d * 0.3) + \
                    sharpened.astype(np.float32) * (attention_map_3d * 0.3)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def gradient_boosting_enhancement(self, image: np.ndarray, mask: np.ndarray,
                                     iterations: int = 3, learning_rate: float = 0.1) -> np.ndarray:
        """
        Mejora con gradient boosting iterativo.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
            iterations: Número de iteraciones
            learning_rate: Tasa de aprendizaje
        
        Returns:
            Imagen mejorada con gradient boosting
        """
        try:
            result = image.copy().astype(np.float32)
            residual = np.zeros_like(result)
            
            for i in range(iterations):
                # Calcular gradiente de mejora
                gray = ImageProcessor.convert_bgr_to_gray(result.astype(np.uint8))
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                
                # Crear mejora basada en gradiente
                enhancement = np.abs(laplacian)
                enhancement = ImageProcessor.apply_gaussian_blur(enhancement, (5, 5))
                if enhancement.max() > 0:
                    enhancement = enhancement / enhancement.max()
                
                # Aplicar mejora con learning rate
                enhancement_3d = ImageProcessor.create_3d_mask(enhancement)
                mask_3d = ImageProcessor.create_3d_mask(mask)
                
                # Residual acumulativo
                residual += enhancement_3d * mask_3d * learning_rate
                
                # Aplicar residual
                result = result + residual * 0.5
                result = ImageProcessor.clip_image(result)
            
            return result.astype(np.uint8)
            
        except Exception:
            return image
    
    def neural_style_preservation(self, source: np.ndarray, target: np.ndarray,
                                 mask: np.ndarray) -> np.ndarray:
        """
        Preservación de estilo neural para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con estilo preservado
        """
        try:
            # Análisis de estilo usando estadísticas de color y textura
            source_lab = ImageProcessor.convert_bgr_to_lab(source)
            target_lab = ImageProcessor.convert_bgr_to_lab(target)
            
            # Calcular estadísticas de estilo (media y varianza)
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (21, 21))
            mask_3d = ImageProcessor.create_3d_mask(mask_blur)
            
            # Preservar estilo del source en región facial
            result_lab = target_lab.copy().astype(np.float32)
            
            for c in range(3):
                source_channel = source_lab[:, :, c].astype(np.float32)
                target_channel = target_lab[:, :, c].astype(np.float32)
                
                # Media y varianza
                source_mean = np.mean(source_channel[mask > 0.5])
                source_std = np.std(source_channel[mask > 0.5])
                target_mean = np.mean(target_channel[mask > 0.5])
                target_std = np.std(target_channel[mask > 0.5])
                
                # Ajustar estilo
                if source_std > 0 and target_std > 0:
                    source_adjusted = (source_channel - source_mean) * (target_std / source_std) + target_mean
                else:
                    source_adjusted = source_channel
                
                # Aplicar con transición suave
                result_lab[:, :, c] = target_channel * (1 - mask_blur) + source_adjusted * mask_blur
            
            result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
            return ImageProcessor.convert_lab_to_bgr(result_lab)
            
        except Exception:
            return target
    
    def adaptive_sharpening_multi_scale(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Sharpening adaptativo multi-escala para mejor detalle.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
        
        Returns:
            Imagen con sharpening adaptativo
        """
        try:
            # Análisis multi-escala
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # Detectar detalles en múltiples escalas
            scales = [3, 5, 7]
            detail_maps = []
            
            for scale in scales:
                blurred = ImageProcessor.apply_gaussian_blur(gray, (scale, scale))
                detail = np.abs(gray.astype(np.float32) - blurred.astype(np.float32))
                detail_maps.append(detail)
            
            # Combinar mapas de detalle
            combined_detail = sum(detail_maps) / len(detail_maps)
            if combined_detail.max() > 0:
                combined_detail = combined_detail / combined_detail.max()
            
            # Aplicar sharpening adaptativo
            detail_mask = combined_detail * mask
            detail_mask = ImageProcessor.apply_gaussian_blur(detail_mask, (5, 5))
            detail_mask_3d = ImageProcessor.create_3d_mask(detail_mask)
            
            # Sharpening con múltiples kernels
            kernel_strong = np.array([[-0.2, -0.4, -0.2],
                                     [-0.4,  2.4, -0.4],
                                     [-0.2, -0.4, -0.2]])
            kernel_medium = np.array([[-0.1, -0.2, -0.1],
                                      [-0.2,  1.6, -0.2],
                                      [-0.1, -0.2, -0.1]])
            
            sharpened_strong = cv2.filter2D(image, -1, kernel_strong)
            sharpened_medium = cv2.filter2D(image, -1, kernel_medium)
            
            # Mezclar según detalle
            result = (
                image.astype(np.float32) * (1 - detail_mask_3d * 0.4) +
                sharpened_medium.astype(np.float32) * (detail_mask_3d * 0.25) +
                sharpened_strong.astype(np.float32) * (detail_mask_3d * 0.15)
            )
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def color_harmony_optimization(self, source: np.ndarray, target: np.ndarray,
                                  mask: np.ndarray) -> np.ndarray:
        """
        Optimización de armonía de color para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con armonía de color optimizada
        """
        try:
            # Convertir a HSV para análisis de color
            source_hsv = cv2.cvtColor(source, cv2.COLOR_BGR2HSV).astype(np.float32)
            target_hsv = cv2.cvtColor(target, cv2.COLOR_BGR2HSV).astype(np.float32)
            
            # Calcular histogramas de color
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (31, 31))
            
            # Ajustar matiz (Hue) para armonía
            source_h = source_hsv[:, :, 0]
            target_h = target_hsv[:, :, 0]
            
            # Calcular diferencia de matiz
            h_diff = target_h - source_h
            h_diff = np.where(h_diff > 180, h_diff - 360, h_diff)
            h_diff = np.where(h_diff < -180, h_diff + 360, h_diff)
            
            # Ajustar matiz del source para armonía
            source_h_adjusted = source_h + h_diff * mask_blur * 0.3
            source_h_adjusted = np.clip(source_h_adjusted, 0, 179)
            
            # Ajustar saturación (S) y valor (V)
            source_s = source_hsv[:, :, 1]
            target_s = target_hsv[:, :, 1]
            source_v = source_hsv[:, :, 2]
            target_v = target_hsv[:, :, 2]
            
            # Ajustar para armonía
            source_s_adjusted = source_s * (1 - mask_blur * 0.2) + target_s * (mask_blur * 0.2)
            source_v_adjusted = source_v * (1 - mask_blur * 0.15) + target_v * (mask_blur * 0.15)
            
            # Reconstruir HSV
            result_hsv = target_hsv.copy()
            result_hsv[:, :, 0] = target_h * (1 - mask_blur) + source_h_adjusted * mask_blur
            result_hsv[:, :, 1] = np.clip(source_s_adjusted, 0, 255)
            result_hsv[:, :, 2] = np.clip(source_v_adjusted, 0, 255)
            
            # Convertir de vuelta a BGR
            result = cv2.cvtColor(result_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def perceptual_loss_optimization(self, source: np.ndarray, target: np.ndarray,
                                     mask: np.ndarray) -> np.ndarray:
        """
        Optimización basada en pérdida perceptual para mejor calidad visual.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen optimizada perceptualmente
        """
        try:
            # Análisis perceptual multi-métrica
            source_gray = ImageProcessor.convert_bgr_to_gray(source)
            target_gray = ImageProcessor.convert_bgr_to_gray(target)
            
            # Calcular pérdida perceptual (diferencia en características visuales)
            # 1. Pérdida de nitidez
            source_laplacian = cv2.Laplacian(source_gray, cv2.CV_64F)
            target_laplacian = cv2.Laplacian(target_gray, cv2.CV_64F)
            sharpness_loss = np.abs(source_laplacian - target_laplacian)
            
            # 2. Pérdida de textura (usando gradientes)
            source_grad_x = cv2.Sobel(source_gray, cv2.CV_64F, 1, 0, ksize=3)
            source_grad_y = cv2.Sobel(source_gray, cv2.CV_64F, 0, 1, ksize=3)
            target_grad_x = cv2.Sobel(target_gray, cv2.CV_64F, 1, 0, ksize=3)
            target_grad_y = cv2.Sobel(target_gray, cv2.CV_64F, 0, 1, ksize=3)
            
            texture_loss = np.sqrt((source_grad_x - target_grad_x)**2 + 
                                  (source_grad_y - target_grad_y)**2)
            
            # Combinar pérdidas
            perceptual_loss = (sharpness_loss * 0.6 + texture_loss * 0.4)
            perceptual_loss = ImageProcessor.apply_gaussian_blur(perceptual_loss, (5, 5))
            if perceptual_loss.max() > 0:
                perceptual_loss = perceptual_loss / perceptual_loss.max()
            
            # Aplicar corrección basada en pérdida perceptual
            loss_mask = perceptual_loss * mask
            loss_mask_3d = ImageProcessor.create_3d_mask(loss_mask)
            
            # Mejorar source para reducir pérdida perceptual
            correction = (target.astype(np.float32) - source.astype(np.float32)) * loss_mask_3d * 0.3
            result = source.astype(np.float32) + correction
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return source
    
    def advanced_ensemble_fusion(self, source: np.ndarray, target: np.ndarray,
                                mask: np.ndarray) -> np.ndarray:
        """
        Fusión avanzada con ensemble de múltiples técnicas.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con fusión avanzada
        """
        try:
            # Aplicar múltiples técnicas
            result_1 = self.intelligent_lighting_adjustment(source, target, mask)
            result_2 = self.intelligent_color_grading(source, target, mask)
            result_3 = self.color_harmony_optimization(source, target, mask)
            result_4 = self.neural_style_preservation(source, target, mask)
            
            # Calcular pesos adaptativos basados en calidad
            qualities = [self._calculate_quality_score(r) for r in [result_1, result_2, result_3, result_4]]
            weights = self._normalize_weights(qualities)
            
            # Fusionar con pesos adaptativos
            result = (
                result_1.astype(np.float32) * weights[0] +
                result_2.astype(np.float32) * weights[1] +
                result_3.astype(np.float32) * weights[2] +
                result_4.astype(np.float32) * weights[3]
            )
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def dynamic_quality_adaptation(self, image: np.ndarray, mask: np.ndarray,
                                  min_quality: float = 0.85, max_quality: float = 0.98) -> np.ndarray:
        """
        Adaptación dinámica de calidad con rango configurable.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
            min_quality: Calidad mínima objetivo
            max_quality: Calidad máxima objetivo
        
        Returns:
            Imagen con calidad adaptada dinámicamente
        """
        try:
            result = image.copy()
            
            # Analizar calidad inicial
            current_quality = self._calculate_quality_score(result)
            
            # Determinar calidad objetivo dinámicamente
            if current_quality < min_quality:
                target_quality = min_quality
            elif current_quality > max_quality:
                target_quality = max_quality
            else:
                # Interpolar entre min y max
                target_quality = min_quality + (max_quality - min_quality) * \
                                ((current_quality - min_quality) / (max_quality - min_quality))
            
            # Aplicar mejoras hasta alcanzar objetivo
            iterations = 0
            max_iterations = 8
            quality_enhancer = self._get_quality_enhancer()
            
            while current_quality < target_quality and iterations < max_iterations:
                # Aplicar mejoras incrementales
                result = quality_enhancer.enhance_perceptual_quality(result)
                result = self.adaptive_sharpening_multi_scale(result, mask)
                
                # Re-analizar
                current_quality = self._calculate_quality_score(result)
                
                if current_quality >= target_quality:
                    break
                
                iterations += 1
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def multi_scale_attention_fusion(self, source: np.ndarray, target: np.ndarray,
                                     mask: np.ndarray) -> np.ndarray:
        """
        Fusión multi-escala con mecanismo de atención avanzado.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con fusión multi-escala y atención
        """
        try:
            # Múltiples escalas
            scales = [0.5, 1.0, 2.0]
            results = []
            
            for scale in scales:
                if scale != 1.0:
                    h, w = source.shape[:2]
                    new_h, new_w = int(h * scale), int(w * scale)
                    source_scaled = cv2.resize(source, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                    target_scaled = cv2.resize(target, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                    mask_scaled = cv2.resize(mask, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                else:
                    source_scaled = source
                    target_scaled = target
                    mask_scaled = mask
                
                # Aplicar técnicas en esta escala
                result_scale = self.intelligent_lighting_adjustment(source_scaled, target_scaled, mask_scaled)
                result_scale = self.color_harmony_optimization(source_scaled, result_scale, mask_scaled)
                
                # Redimensionar de vuelta si es necesario
                if scale != 1.0:
                    result_scale = cv2.resize(result_scale, (target.shape[1], target.shape[0]), 
                                             interpolation=cv2.INTER_LANCZOS4)
                    mask_scaled = cv2.resize(mask_scaled, (target.shape[1], target.shape[0]), 
                                            interpolation=cv2.INTER_LINEAR)
                
                results.append((result_scale, mask_scaled))
            
            # Calcular atención para cada escala
            attention_maps = []
            for result, mask_s in results:
                gray = ImageProcessor.convert_bgr_to_gray(result)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                attention = np.abs(laplacian)
                attention = ImageProcessor.apply_gaussian_blur(attention, (5, 5))
                if attention.max() > 0:
                    attention = attention / attention.max()
                attention_maps.append(attention * mask_s)
            
            # Normalizar mapas de atención
            total_attention = sum(attention_maps)
            if total_attention.max() > 0:
                attention_weights = [am / (total_attention + 1e-6) for am in attention_maps]
            else:
                attention_weights = [np.ones_like(am) / len(attention_maps) for am in attention_maps]
            
            # Fusionar con pesos de atención
            result = np.zeros_like(target, dtype=np.float32)
            for (res, _), weight in zip(results, attention_weights):
                weight_3d = ImageProcessor.create_3d_mask(weight)
                result += res.astype(np.float32) * weight_3d
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def adversarial_style_enhancement(self, source: np.ndarray, target: np.ndarray,
                                    mask: np.ndarray) -> np.ndarray:
        """
        Mejora estilo adversarial para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con mejora estilo adversarial
        """
        try:
            # Análisis de características locales
            source_gray = ImageProcessor.convert_bgr_to_gray(source)
            target_gray = ImageProcessor.convert_bgr_to_gray(target)
            
            # Calcular características locales (gradientes, textura)
            source_grad = cv2.Sobel(source_gray, cv2.CV_64F, 1, 1, ksize=3)
            target_grad = cv2.Sobel(target_gray, cv2.CV_64F, 1, 1, ksize=3)
            
            # Análisis de textura local
            kernel_size = 5
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            
            source_texture = cv2.filter2D(source_gray.astype(np.float32), -1, kernel)
            target_texture = cv2.filter2D(target_gray.astype(np.float32), -1, kernel)
            
            # Calcular diferencia adversarial
            grad_diff = np.abs(source_grad - target_grad)
            texture_diff = np.abs(source_texture - target_texture)
            
            # Combinar diferencias
            adversarial_map = (grad_diff + texture_diff) / 2.0
            adversarial_map = ImageProcessor.apply_gaussian_blur(adversarial_map, (7, 7))
            if adversarial_map.max() > 0:
                adversarial_map = adversarial_map / adversarial_map.max()
            
            # Aplicar corrección adversarial
            adversarial_mask = adversarial_map * mask
            adversarial_mask_3d = ImageProcessor.create_3d_mask(adversarial_mask)
            
            # Mezclar source y target según mapa adversarial
            correction = (target.astype(np.float32) - source.astype(np.float32)) * adversarial_mask_3d * 0.4
            result = source.astype(np.float32) + correction
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return source
    
    def feature_preserving_upsampling(self, image: np.ndarray, mask: np.ndarray,
                                     scale: float = 1.5) -> np.ndarray:
        """
        Upsampling preservando características para mejor detalle.
        
        Args:
            image: Imagen a upsampling
            mask: Máscara de la región
            scale: Factor de escala
        
        Returns:
            Imagen con upsampling preservando características
        """
        try:
            h, w = image.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)
            
            # Upsampling con múltiples métodos
            upsampled_1 = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            upsampled_2 = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            # Extraer características de alta frecuencia
            gray_orig = ImageProcessor.convert_bgr_to_gray(image)
            gray_1 = ImageProcessor.convert_bgr_to_gray(upsampled_1)
            gray_2 = ImageProcessor.convert_bgr_to_gray(upsampled_2)
            
            # Detectar bordes y detalles
            edges_1 = cv2.Canny(gray_1.astype(np.uint8), 50, 150)
            edges_2 = cv2.Canny(gray_2.astype(np.uint8), 50, 150)
            
            # Combinar según calidad de bordes
            edge_quality_1 = np.sum(edges_1 > 0) / (new_h * new_w)
            edge_quality_2 = np.sum(edges_2 > 0) / (new_h * new_w)
            
            if edge_quality_1 > edge_quality_2:
                result = upsampled_1
            else:
                result = upsampled_2
            
            # Aplicar sharpening adaptativo
            gray_result = ImageProcessor.convert_bgr_to_gray(result)
            laplacian = cv2.Laplacian(gray_result, cv2.CV_64F)
            detail_map = np.abs(laplacian)
            detail_map = ImageProcessor.apply_gaussian_blur(detail_map, (3, 3))
            if detail_map.max() > 0:
                detail_map = detail_map / detail_map.max()
            
            # Sharpening selectivo
            kernel = np.array([[-0.1, -0.2, -0.1],
                              [-0.2,  1.8, -0.2],
                              [-0.1, -0.2, -0.1]])
            sharpened = cv2.filter2D(result, -1, kernel)
            
            detail_map_3d = ImageProcessor.create_3d_mask(detail_map)
            result = result.astype(np.float32) * (1 - detail_map_3d * 0.3) + \
                    sharpened.astype(np.float32) * (detail_map_3d * 0.3)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def deep_feature_matching(self, source: np.ndarray, target: np.ndarray,
                             mask: np.ndarray) -> np.ndarray:
        """
        Matching de características profundas para mejor alineación.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con características profundas alineadas
        """
        try:
            # Extraer características multi-nivel
            source_gray = ImageProcessor.convert_bgr_to_gray(source)
            target_gray = ImageProcessor.convert_bgr_to_gray(target)
            
            # Características de nivel 1 (bordes)
            source_edges = cv2.Canny(source_gray.astype(np.uint8), 50, 150)
            target_edges = cv2.Canny(target_gray.astype(np.uint8), 50, 150)
            
            # Características de nivel 2 (textura)
            source_texture = cv2.Laplacian(source_gray, cv2.CV_64F)
            target_texture = cv2.Laplacian(target_gray, cv2.CV_64F)
            
            # Características de nivel 3 (gradientes direccionales)
            source_grad_x = cv2.Sobel(source_gray, cv2.CV_64F, 1, 0, ksize=3)
            source_grad_y = cv2.Sobel(source_gray, cv2.CV_64F, 0, 1, ksize=3)
            target_grad_x = cv2.Sobel(target_gray, cv2.CV_64F, 1, 0, ksize=3)
            target_grad_y = cv2.Sobel(target_gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calcular matching de características
            edge_match = np.abs(source_edges.astype(np.float32) - target_edges.astype(np.float32))
            texture_match = np.abs(source_texture - target_texture)
            grad_match = np.sqrt((source_grad_x - target_grad_x)**2 + 
                                (source_grad_y - target_grad_y)**2)
            
            # Combinar matching
            feature_match = (edge_match * 0.3 + texture_match * 0.4 + grad_match * 0.3)
            feature_match = ImageProcessor.apply_gaussian_blur(feature_match, (5, 5))
            if feature_match.max() > 0:
                feature_match = feature_match / feature_match.max()
            
            # Aplicar corrección basada en matching
            match_mask = (1 - feature_match) * mask
            match_mask = ImageProcessor.apply_gaussian_blur(match_mask, (7, 7))
            match_mask_3d = ImageProcessor.create_3d_mask(match_mask)
            
            # Mezclar según matching
            result = source.astype(np.float32) * (1 - match_mask_3d * 0.5) + \
                    target.astype(np.float32) * (match_mask_3d * 0.5)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return source
    
    def neural_style_transfer_enhancement(self, source: np.ndarray, target: np.ndarray,
                                        mask: np.ndarray, style_weight: float = 0.3) -> np.ndarray:
        """
        Mejora con transferencia de estilo neural para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
            style_weight: Peso del estilo (0.0-1.0)
        
        Returns:
            Imagen con transferencia de estilo neural
        """
        try:
            # Análisis de estilo usando estadísticas de Gram (simplificado)
            source_lab = ImageProcessor.convert_bgr_to_lab(source)
            target_lab = ImageProcessor.convert_bgr_to_lab(target)
            
            # Calcular estadísticas de estilo (media y covarianza)
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (21, 21))
            mask_3d = ImageProcessor.create_3d_mask(mask_blur)
            
            # Estadísticas de estilo del source
            source_mean = np.sum(source_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
            source_std = np.sqrt(np.sum(((source_lab - source_mean) ** 2) * mask_3d, axis=(0, 1)) / 
                               (np.sum(mask) + 1e-6)) + 1e-6
            
            # Estadísticas de estilo del target
            target_mean = np.sum(target_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
            target_std = np.sqrt(np.sum(((target_lab - target_mean) ** 2) * mask_3d, axis=(0, 1)) / 
                               (np.sum(mask) + 1e-6)) + 1e-6
            
            # Transferir estilo
            result_lab = target_lab.copy().astype(np.float32)
            for c in range(3):
                source_channel = source_lab[:, :, c].astype(np.float32)
                target_channel = target_lab[:, :, c].astype(np.float32)
                
                # Normalizar y transferir estilo
                source_normalized = (source_channel - source_mean[c]) / source_std[c]
                target_normalized = (target_channel - target_mean[c]) / target_std[c]
                
                # Aplicar transferencia de estilo
                transferred = source_normalized * target_std[c] + target_mean[c]
                
                # Mezclar según peso de estilo
                result_lab[:, :, c] = target_channel * (1 - mask_blur * style_weight) + \
                                    transferred * (mask_blur * style_weight)
            
            result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
            return ImageProcessor.convert_lab_to_bgr(result_lab)
            
        except Exception:
            return target
    
    def meta_learning_enhancement(self, source: np.ndarray, target: np.ndarray,
                                mask: np.ndarray, strategy: str = "adaptive") -> np.ndarray:
        """
        Mejora con meta-learning para selección inteligente de estrategia.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
            strategy: Estrategia ("adaptive", "quality_focused", "speed_focused")
        
        Returns:
            Imagen mejorada con meta-learning
        """
        try:
            # Analizar características de imagen
            source_gray = ImageProcessor.convert_bgr_to_gray(source)
            target_gray = ImageProcessor.convert_bgr_to_gray(target)
            
            # Calcular métricas de calidad
            source_sharpness = cv2.Laplacian(source_gray, cv2.CV_64F).var()
            target_sharpness = cv2.Laplacian(target_gray, cv2.CV_64F).var()
            
            source_contrast = np.std(source_gray)
            target_contrast = np.std(target_gray)
            
            # Seleccionar estrategia según meta-learning
            if strategy == "adaptive":
                # Aprender automáticamente la mejor estrategia
                if abs(source_sharpness - target_sharpness) > 50:
                    # Alta diferencia de nitidez -> usar sharpening
                    result = self.adaptive_sharpening_multi_scale(target, mask)
                elif abs(source_contrast - target_contrast) > 20:
                    # Alta diferencia de contraste -> usar color grading
                    result = self.intelligent_color_grading(source, target, mask)
                else:
                    # Baja diferencia -> usar blending suave
                    result = self.neural_style_preservation(source, target, mask)
            elif strategy == "quality_focused":
                # Enfoque en calidad máxima
                result = self.intelligent_lighting_adjustment(source, target, mask)
                result = self.color_harmony_optimization(source, result, mask)
                result = self.adaptive_sharpening_multi_scale(result, mask)
            else:  # speed_focused
                # Enfoque en velocidad
                result = self.neural_style_preservation(source, target, mask)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def ensemble_learning_enhancement(self, source: np.ndarray, target: np.ndarray,
                                   mask: np.ndarray, diversity_weight: float = 0.3) -> np.ndarray:
        """
        Mejora con ensemble learning para mejor calidad combinada.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
            diversity_weight: Peso de diversidad (0.0-1.0)
        
        Returns:
            Imagen mejorada con ensemble learning
        """
        try:
            # Aplicar múltiples técnicas diversas
            results = []
            
            # 1. Técnica de iluminación
            result_1 = self.intelligent_lighting_adjustment(source, target, mask)
            results.append(result_1)
            
            # 2. Técnica de color
            result_2 = self.color_harmony_optimization(source, target, mask)
            results.append(result_2)
            
            # 3. Técnica de estilo
            result_3 = self.neural_style_preservation(source, target, mask)
            results.append(result_3)
            
            # 4. Técnica de textura
            result_4 = self.preserve_skin_texture_advanced(source, target, mask)
            results.append(result_4)
            
            # Calcular diversidad entre resultados
            diversities = []
            for i, res1 in enumerate(results):
                for j, res2 in enumerate(results):
                    if i < j:
                        diff = np.mean(np.abs(res1.astype(np.float32) - res2.astype(np.float32)))
                        diversities.append(diff)
            
            avg_diversity = np.mean(diversities) if diversities else 0
            
            # Calcular pesos basados en calidad y diversidad
            weights = []
            for result in results:
                quality = self._calculate_quality_score(result)
                # Combinar calidad con diversidad
                weight = quality * (1 - diversity_weight) + avg_diversity * diversity_weight
                weights.append(weight)
            
            # Normalizar pesos
            weights = self._normalize_weights(weights)
            
            # Fusionar con pesos
            ensemble_result = np.zeros_like(target, dtype=np.float32)
            for result, weight in zip(results, weights):
                ensemble_result += result.astype(np.float32) * weight
            
            return ImageProcessor.clip_image(ensemble_result)
            
        except Exception:
            return target
    
    def guided_filter_enhancement(self, source: np.ndarray, target: np.ndarray,
                                  mask: np.ndarray, radius: int = 5, eps: float = 0.01) -> np.ndarray:
        """
        Mejora usando guided filter para preservación de bordes avanzada.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
            radius: Radio del filtro
            eps: Parámetro de regularización
        
        Returns:
            Imagen mejorada con guided filter
        """
        try:
            # Convertir a escala de grises para guía
            guide = ImageProcessor.convert_bgr_to_gray(target)
            guide = guide.astype(np.float32) / 255.0
            
            # Aplicar guided filter a cada canal
            result = np.zeros_like(target, dtype=np.float32)
            
            for c in range(3):
                source_channel = source[:, :, c].astype(np.float32) / 255.0
                target_channel = target[:, :, c].astype(np.float32) / 255.0
                
                # Calcular estadísticas locales
                mean_guide = cv2.boxFilter(guide, cv2.CV_32F, (radius, radius))
                mean_source = cv2.boxFilter(source_channel, cv2.CV_32F, (radius, radius))
                mean_target = cv2.boxFilter(target_channel, cv2.CV_32F, (radius, radius))
                
                corr_gs = cv2.boxFilter(guide * source_channel, cv2.CV_32F, (radius, radius))
                corr_gt = cv2.boxFilter(guide * target_channel, cv2.CV_32F, (radius, radius))
                var_guide = cv2.boxFilter(guide * guide, cv2.CV_32F, (radius, radius)) - mean_guide * mean_guide
                
                # Calcular coeficientes
                a_source = (corr_gs - mean_guide * mean_source) / (var_guide + eps)
                b_source = mean_source - a_source * mean_guide
                
                a_target = (corr_gt - mean_guide * mean_target) / (var_guide + eps)
                b_target = mean_target - a_target * mean_guide
                
                # Aplicar filtro
                mean_a_source = cv2.boxFilter(a_source, cv2.CV_32F, (radius, radius))
                mean_b_source = cv2.boxFilter(b_source, cv2.CV_32F, (radius, radius))
                filtered_source = mean_a_source * guide + mean_b_source
                
                mean_a_target = cv2.boxFilter(a_target, cv2.CV_32F, (radius, radius))
                mean_b_target = cv2.boxFilter(b_target, cv2.CV_32F, (radius, radius))
                filtered_target = mean_a_target * guide + mean_b_target
                
                # Mezclar según máscara
                mask_blur = ImageProcessor.apply_gaussian_blur(mask, (radius, radius))
                result[:, :, c] = filtered_source * (1 - mask_blur) + filtered_target * mask_blur
            
            result = (result * 255.0).clip(0, 255).astype(np.uint8)
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target
    
    def advanced_edge_preservation(self, source: np.ndarray, target: np.ndarray,
                                  mask: np.ndarray) -> np.ndarray:
        """
        Preservación avanzada de bordes para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con bordes preservados avanzadamente
        """
        try:
            source_gray = ImageProcessor.convert_bgr_to_gray(source)
            target_gray = ImageProcessor.convert_bgr_to_gray(target)
            
            # Detectar bordes con múltiples métodos
            # 1. Canny edges
            source_edges_canny = cv2.Canny(source_gray.astype(np.uint8), 50, 150)
            target_edges_canny = cv2.Canny(target_gray.astype(np.uint8), 50, 150)
            
            # 2. Sobel edges
            source_sobel_x = cv2.Sobel(source_gray, cv2.CV_64F, 1, 0, ksize=3)
            source_sobel_y = cv2.Sobel(source_gray, cv2.CV_64F, 0, 1, ksize=3)
            source_edges_sobel = np.sqrt(source_sobel_x**2 + source_sobel_y**2)
            
            target_sobel_x = cv2.Sobel(target_gray, cv2.CV_64F, 1, 0, ksize=3)
            target_sobel_y = cv2.Sobel(target_gray, cv2.CV_64F, 0, 1, ksize=3)
            target_edges_sobel = np.sqrt(target_sobel_x**2 + target_sobel_y**2)
            
            # 3. Laplacian edges
            source_laplacian = np.abs(cv2.Laplacian(source_gray, cv2.CV_64F))
            target_laplacian = np.abs(cv2.Laplacian(target_gray, cv2.CV_64F))
            
            # Combinar detección de bordes
            source_edges = (source_edges_canny.astype(np.float32) / 255.0 * 0.4 +
                           source_edges_sobel / source_edges_sobel.max() * 0.3 +
                           source_laplacian / source_laplacian.max() * 0.3)
            
            target_edges = (target_edges_canny.astype(np.float32) / 255.0 * 0.4 +
                           target_edges_sobel / target_edges_sobel.max() * 0.3 +
                           target_laplacian / target_laplacian.max() * 0.3)
            
            # Preservar bordes del source en región facial
            edge_mask = source_edges * mask
            edge_mask = ImageProcessor.apply_gaussian_blur(edge_mask, (3, 3))
            edge_mask_3d = ImageProcessor.create_3d_mask(edge_mask)
            
            # Mezclar preservando bordes
            result = target.astype(np.float32) * (1 - edge_mask_3d * 0.5) + \
                    source.astype(np.float32) * (edge_mask_3d * 0.5)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return source
    
    def advanced_artifact_reduction(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Reducción avanzada de artefactos con múltiples técnicas.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
        
        Returns:
            Imagen con artefactos reducidos
        """
        try:
            # Detectar artefactos usando análisis de gradientes
            gray = ImageProcessor.convert_bgr_to_gray(image)
            
            # Análisis de variación local
            kernel_size = 5
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            
            local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            local_var = cv2.filter2D((gray.astype(np.float32) - local_mean)**2, -1, kernel)
            
            # Detectar regiones anómalas (posibles artefactos)
            var_threshold = np.percentile(local_var, 95)
            artifact_mask = (local_var > var_threshold).astype(np.float32)
            artifact_mask = ImageProcessor.apply_gaussian_blur(artifact_mask, (5, 5))
            
            # Aplicar múltiples técnicas de reducción
            # 1. Bilateral filter
            bilateral = ImageProcessor.apply_bilateral_filter(image, 5, 50, 50)
            
            # 2. Median filter
            median = cv2.medianBlur(image, 5)
            
            # 3. Gaussian blur suave
            gaussian = ImageProcessor.apply_gaussian_blur(image, (3, 3))
            
            # Combinar técnicas según tipo de artefacto
            artifact_mask_3d = ImageProcessor.create_3d_mask(artifact_mask * mask)
            
            # Usar bilateral para la mayoría, median para casos extremos
            result = image.astype(np.float32) * (1 - artifact_mask_3d * 0.6) + \
                    bilateral.astype(np.float32) * (artifact_mask_3d * 0.5) + \
                    median.astype(np.float32) * (artifact_mask_3d * 0.1)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return image
    
    def color_consistency_improvement(self, source: np.ndarray, target: np.ndarray,
                                    mask: np.ndarray) -> np.ndarray:
        """
        Mejora de consistencia de color para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
        
        Returns:
            Imagen con consistencia de color mejorada
        """
        try:
            # Convertir a LAB para mejor análisis de color
            source_lab = ImageProcessor.convert_bgr_to_lab(source)
            target_lab = ImageProcessor.convert_bgr_to_lab(target)
            
            # Calcular estadísticas de color en región circundante
            surrounding_mask = 1 - mask
            surrounding_mask = ImageProcessor.apply_gaussian_blur(surrounding_mask, (31, 31))
            surrounding_mask_3d = ImageProcessor.create_3d_mask(surrounding_mask)
            
            # Estadísticas del target en región circundante
            target_mean = np.sum(target_lab * surrounding_mask_3d, axis=(0, 1)) / \
                         (np.sum(surrounding_mask) + 1e-6)
            target_std = np.sqrt(np.sum(((target_lab - target_mean) ** 2) * surrounding_mask_3d, 
                                       axis=(0, 1)) / (np.sum(surrounding_mask) + 1e-6)) + 1e-6
            
            # Estadísticas del source en región facial
            mask_3d = ImageProcessor.create_3d_mask(mask)
            source_mean = np.sum(source_lab * mask_3d, axis=(0, 1)) / (np.sum(mask) + 1e-6)
            source_std = np.sqrt(np.sum(((source_lab - source_mean) ** 2) * mask_3d, 
                                       axis=(0, 1)) / (np.sum(mask) + 1e-6)) + 1e-6
            
            # Ajustar source para consistencia con target
            result_lab = source_lab.copy().astype(np.float32)
            mask_blur = ImageProcessor.apply_gaussian_blur(mask, (21, 21))
            
            for c in range(3):
                source_channel = source_lab[:, :, c].astype(np.float32)
                target_channel = target_lab[:, :, c].astype(np.float32)
                
                # Ajustar para consistencia
                if source_std[c] > 0:
                    adjusted = (source_channel - source_mean[c]) * (target_std[c] / source_std[c]) + target_mean[c]
                else:
                    adjusted = source_channel
                
                # Mezclar con transición suave
                result_lab[:, :, c] = target_channel * (1 - mask_blur) + adjusted * mask_blur
            
            result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
            return ImageProcessor.convert_lab_to_bgr(result_lab)
            
        except Exception:
            return target
    
    def wavelet_transform_enhancement(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Mejora usando transformada wavelet para preservar detalles multi-escala.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
            
        Returns:
            Imagen mejorada con wavelets
        """
        try:
            # Usar FFT como aproximación de wavelet (simplificado)
            gray = ImageProcessor.convert_bgr_to_gray(image)
            fft = np.fft.fft2(gray.astype(np.float32))
            fft_shift = np.fft.fftshift(fft)
            
            # Mejorar alta frecuencia en región facial
            h, w = gray.shape
            center_y, center_x = h // 2, w // 2
            y_coords, x_coords = np.ogrid[:h, :w]
            dist = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            
            # Filtro de alta frecuencia
            high_freq_filter = np.clip(dist / (max_dist * 0.2), 0, 1)
            mask_fft = np.fft.fftshift(np.fft.fft2(mask.astype(np.float32)))
            
            # Mejorar magnitud en alta frecuencia
            magnitude = np.abs(fft_shift)
            phase = np.angle(fft_shift)
            enhanced_magnitude = magnitude * (1 + high_freq_filter * np.abs(mask_fft) * 0.3)
            
            # Reconstruir
            enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_gray = np.real(np.fft.ifft2(np.fft.ifftshift(enhanced_fft)))
            
            # Aplicar mejora
            enhancement = (enhanced_gray - gray.astype(np.float32)) * mask
            enhancement_3d = ImageProcessor.create_3d_mask(enhancement)
            result = image.astype(np.float32) + enhancement_3d * 0.3
            
            return ImageProcessor.clip_image(result)
        except Exception:
            return image
    
    def advanced_frequency_analysis(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Análisis avanzado de frecuencia para mejoras selectivas.
        
        Args:
            image: Imagen a mejorar
            mask: Máscara de la región
            
        Returns:
            Imagen mejorada con análisis de frecuencia
        """
        try:
            gray = ImageProcessor.convert_bgr_to_gray(image)
            fft = np.fft.fft2(gray.astype(np.float32))
            fft_shift = np.fft.fftshift(fft)
            
            h, w = gray.shape
            center_y, center_x = h // 2, w // 2
            y_coords, x_coords = np.ogrid[:h, :w]
            dist = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            
            # Anillos de frecuencia
            inner_radius = max_dist * 0.05
            outer_radius = max_dist * 0.3
            
            # Filtro de anillo
            ring_filter = ((dist >= inner_radius) & (dist <= outer_radius)).astype(np.float32)
            ring_filter = ImageProcessor.apply_gaussian_blur(ring_filter, (5, 5))
            
            # Mejorar anillo de frecuencia
            magnitude = np.abs(fft_shift)
            phase = np.angle(fft_shift)
            enhanced_magnitude = magnitude * (1 + ring_filter * 0.2)
            
            # Reconstruir
            enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_gray = np.real(np.fft.ifft2(np.fft.ifftshift(enhanced_fft)))
            
            # Aplicar con máscara
            enhancement = (enhanced_gray - gray.astype(np.float32)) * mask
            enhancement_3d = ImageProcessor.create_3d_mask(enhancement)
            result = image.astype(np.float32) + enhancement_3d * 0.3
            
            return ImageProcessor.clip_image(result)
        except Exception:
            return image
    
    def structural_similarity_optimization(self, source: np.ndarray, target: np.ndarray,
                                         mask: np.ndarray) -> np.ndarray:
        """
        Optimización basada en SSIM (Structural Similarity Index) para mejor calidad.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
            
        Returns:
            Imagen optimizada con SSIM
        """
        try:
            from .constants import SSIM_C1, SSIM_C2, SSIM_OPTIMIZATION_WEIGHT
            
            source_gray = ImageProcessor.convert_bgr_to_gray(source).astype(np.float32)
            target_gray = ImageProcessor.convert_bgr_to_gray(target).astype(np.float32)
            
            # Calcular SSIM local (simplificado)
            kernel_size = 11
            kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
            
            mu_source = cv2.filter2D(source_gray, -1, kernel)
            mu_target = cv2.filter2D(target_gray, -1, kernel)
            
            sigma_source_sq = cv2.filter2D(source_gray * source_gray, -1, kernel) - mu_source * mu_source
            sigma_target_sq = cv2.filter2D(target_gray * target_gray, -1, kernel) - mu_target * mu_target
            sigma_st = cv2.filter2D(source_gray * target_gray, -1, kernel) - mu_source * mu_target
            
            # SSIM
            ssim = ((2 * mu_source * mu_target + SSIM_C1) * (2 * sigma_st + SSIM_C2)) / \
                   ((mu_source**2 + mu_target**2 + SSIM_C1) * (sigma_source_sq + sigma_target_sq + SSIM_C2))
            
            # Optimizar para mejorar SSIM
            ssim_mask = (1 - ssim) * mask
            ssim_mask = ImageProcessor.apply_gaussian_blur(ssim_mask, (7, 7))
            ssim_mask_3d = ImageProcessor.create_3d_mask(ssim_mask)
            
            # Aplicar corrección
            correction = (target.astype(np.float32) - source.astype(np.float32)) * ssim_mask_3d * SSIM_OPTIMIZATION_WEIGHT
            result = source.astype(np.float32) + correction
            
            return ImageProcessor.clip_image(result)
        except Exception:
            return target
    
    def multi_resolution_analysis(self, source: np.ndarray, target: np.ndarray,
                                 mask: np.ndarray) -> np.ndarray:
        """
        Análisis multi-resolución para mejor integración.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            mask: Máscara de la región
            
        Returns:
            Imagen mejorada con análisis multi-resolución
        """
        try:
            from .constants import MULTI_RESOLUTION_SCALES, MULTI_RESOLUTION_WEIGHTS
            
            results = []
            
            for scale, weight in zip(MULTI_RESOLUTION_SCALES, MULTI_RESOLUTION_WEIGHTS):
                if scale != 1.0:
                    h, w = source.shape[:2]
                    new_h, new_w = int(h * scale), int(w * scale)
                    source_scaled = cv2.resize(source, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                    target_scaled = cv2.resize(target, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                    mask_scaled = cv2.resize(mask, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                else:
                    source_scaled = source
                    target_scaled = target
                    mask_scaled = mask
                
                # Aplicar mejoras en esta escala
                result_scale = self.intelligent_lighting_adjustment(source_scaled, target_scaled, mask_scaled)
                result_scale = self.color_harmony_optimization(source_scaled, result_scale, mask_scaled)
                
                # Redimensionar de vuelta
                if scale != 1.0:
                    result_scale = cv2.resize(result_scale, (target.shape[1], target.shape[0]), 
                                             interpolation=cv2.INTER_LANCZOS4)
                
                results.append((result_scale, weight))
            
            # Combinar resultados
            result = np.zeros_like(target, dtype=np.float32)
            total_weight = sum(w for _, w in results)
            
            for res, weight in results:
                result += res.astype(np.float32) * (weight / total_weight)
            
            return ImageProcessor.clip_image(result)
        except Exception:
            return target
    
    def apply_all_enhancements(self, source: np.ndarray, target: np.ndarray,
                              source_landmarks: np.ndarray, target_landmarks: np.ndarray,
                              mask: np.ndarray) -> np.ndarray:
        """
        Aplicar todas las mejoras avanzadas en secuencia optimizada.
        
        Args:
            source: Imagen fuente
            target: Imagen target
            source_landmarks: Landmarks de source
            target_landmarks: Landmarks de target
            mask: Máscara de la región facial
        
        Returns:
            Imagen con todas las mejoras aplicadas
        """
        try:
            result = target.copy()
            
            # 1. Ajuste de iluminación
            result = self.intelligent_lighting_adjustment(source, result, mask)
            
            # 2. Color grading inteligente
            result = self.intelligent_color_grading(source, result, mask)
            
            # 3. Optimización de armonía de color
            result = self.color_harmony_optimization(source, result, mask)
            
            # 4. Preservación de estilo neural
            result = self.neural_style_preservation(source, result, mask)
            
            # 5. Optimización de pérdida perceptual (NUEVO)
            result = self.perceptual_loss_optimization(source, result, mask)
            
            # 6. Preservación de textura de piel
            result = self.preserve_skin_texture_advanced(source, result, mask)
            
            # 7. Síntesis de textura avanzada
            result = self.texture_synthesis_advanced(source, result, mask)
            
            # 8. Preservación de expresión
            result = self.preserve_expression_advanced(source, result, 
                                                      source_landmarks, target_landmarks, mask)
            
            # 9. Edge-aware filtering
            result = self.edge_aware_filtering(result, mask)
            
            # 10. Frequency domain enhancement
            result = self.frequency_domain_enhancement(result, mask)
            
            # 11. Sharpening adaptativo multi-escala
            result = self.adaptive_sharpening_multi_scale(result, mask)
            
            # 12. Attention-based enhancement
            result = self.attention_based_enhancement(result, mask)
            
            # 13. Gradient boosting enhancement
            result = self.gradient_boosting_enhancement(result, mask, iterations=2)
            
            # 14. Ensemble multi-escala
            result = self.multi_scale_ensemble_enhancement(result, mask)
            
            # 15. Fusión avanzada con ensemble
            result = self.advanced_ensemble_fusion(source, result, mask)
            
            # 16. Fusión multi-escala con atención (NUEVO)
            result = self.multi_scale_attention_fusion(source, result, mask)
            
            # 17. Mejora estilo adversarial (NUEVO)
            result = self.adversarial_style_enhancement(source, result, mask)
            
            # 18. Matching de características profundas
            result = self.deep_feature_matching(source, result, mask)
            
            # 19. Transferencia de estilo neural
            result = self.neural_style_transfer_enhancement(source, result, mask, style_weight=0.25)
            
            # 20. Meta-learning enhancement
            result = self.meta_learning_enhancement(source, result, mask, strategy="adaptive")
            
            # 21. Ensemble learning enhancement
            result = self.ensemble_learning_enhancement(source, result, mask, diversity_weight=0.3)
            
            # 22. Wavelet transform enhancement (si está disponible)
            try:
                result = self.wavelet_transform_enhancement(result, mask)
            except Exception:
                pass
            
            # 23. Advanced frequency analysis
            try:
                result = self.advanced_frequency_analysis(result, mask)
            except Exception:
                pass
            
            # 24. Structural similarity optimization
            try:
                result = self.structural_similarity_optimization(source, result, mask)
            except Exception:
                pass
            
            # 25. Multi-resolution analysis
            try:
                result = self.multi_resolution_analysis(source, result, mask)
            except Exception:
                pass
            
            # 26. Optimización perceptual avanzada
            result = self.perceptual_optimization_advanced(result, mask, iterations=2)
            
            # 27. Adaptación dinámica de calidad
            result = self.dynamic_quality_adaptation(result, mask, min_quality=0.90, max_quality=0.96)
            
            return ImageProcessor.clip_image(result)
            
        except Exception:
            return target








