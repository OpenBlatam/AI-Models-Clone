"""
Face Swap Ultra Quality - Versión Mejorada
===========================================
Algoritmo avanzado con técnicas profesionales para resultados de alta calidad
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class UltraQualityFaceSwap:
    """Face swap de ultra calidad con técnicas avanzadas."""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detecta la cara más grande con múltiples escalas y métodos."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Mejorar contraste para mejor detección
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray_enhanced = clahe.apply(gray)
        
        # Detectar con múltiples escalas para mejor precisión
        faces = self.face_cascade.detectMultiScale(
            gray_enhanced,
            scaleFactor=1.05,  # Más preciso
            minNeighbors=6,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Si no encuentra, intentar con imagen original
        if len(faces) == 0:
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
        
        if len(faces) > 0:
            # Retornar la cara más grande y centrada
            faces = sorted(faces, key=lambda x: (x[2] * x[3], -abs(x[0] + x[2]//2 - image.shape[1]//2)), reverse=True)
            return tuple(faces[0])
        
        return None
    
    def extract_face_region(self, image: np.ndarray, face_rect: Tuple[int, int, int, int], 
                           expand: float = 0.5) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        """Extrae región de cara con margen expandido y mejoras de calidad."""
        x, y, w, h = face_rect
        
        # Expansión asimétrica (más espacio arriba para cabello)
        expand_w = int(w * expand)
        expand_h_top = int(h * (expand + 0.2))  # Más espacio arriba
        expand_h_bottom = int(h * expand)
        
        x_exp = max(0, x - expand_w)
        y_exp = max(0, y - expand_h_top)
        w_exp = min(image.shape[1] - x_exp, w + 2 * expand_w)
        h_exp = min(image.shape[0] - y_exp, h + expand_h_top + expand_h_bottom)
        
        region = image[y_exp:y_exp+h_exp, x_exp:x_exp+w_exp].copy()
        adjusted_rect = (x - x_exp, y - y_exp, w, h)
        
        # Mejora sutil de la región extraída
        region = cv2.bilateralFilter(region, 3, 30, 30)
        
        return region, adjusted_rect
    
    def create_advanced_mask(self, shape: Tuple[int, int], face_rect: Tuple[int, int, int, int]) -> np.ndarray:
        """Crea máscara avanzada con forma facial natural mejorada."""
        h, w = shape
        mask = np.zeros((h, w), dtype=np.float32)
        
        x, y, face_w, face_h = face_rect
        
        # Crear máscara elíptica más precisa con forma de cara
        center_x = x + face_w // 2
        center_y = y + face_h // 2
        
        # Radio adaptativo basado en el tamaño de la cara
        radius_x = int(face_w * 0.52)
        radius_y = int(face_h * 0.62)
        
        y_coords, x_coords = np.ogrid[:h, :w]
        
        # Máscara elíptica con forma más natural (más ancha abajo)
        # Usar función elíptica modificada para forma de cara
        dx = (x_coords - center_x) / radius_x
        dy = (y_coords - center_y) / radius_y
        
        # Forma más natural: más ancha en la parte inferior
        ellipse_factor = dx**2 + (dy * (1 + 0.2 * np.maximum(0, dy)))**2
        mask[ellipse_factor <= 1] = 1.0
        
        # Suavizado múltiple progresivo para transición ultra suave
        for sigma in [30, 25, 20, 15, 12, 10]:
            mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=sigma, sigmaY=sigma)
        
        # Aplicar curva de suavizado adicional
        mask = np.power(mask, 0.8)  # Hacer transición más gradual
        
        mask = np.clip(mask, 0, 1)
        return mask
    
    def histogram_matching(self, source: np.ndarray, target: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Aplica histogram matching para mejor coincidencia de color."""
        result = source.copy()
        mask_uint8 = (mask * 255).astype(np.uint8)
        
        for i in range(3):  # Para cada canal BGR
            source_channel = source[:, :, i]
            target_channel = target[:, :, i]
            
            # Calcular histogramas solo en la región de la máscara
            source_hist = cv2.calcHist([source_channel], [0], mask_uint8, [256], [0, 256])
            target_hist = cv2.calcHist([target_channel], [0], mask_uint8, [256], [0, 256])
            
            # Normalizar
            source_hist = source_hist / (np.sum(source_hist) + 1e-6)
            target_hist = target_hist / (np.sum(target_hist) + 1e-6)
            
            # Calcular CDFs
            source_cdf = np.cumsum(source_hist)
            target_cdf = np.cumsum(target_hist)
            
            # Crear lookup table
            lookup = np.zeros(256, dtype=np.uint8)
            for j in range(256):
                idx = np.argmin(np.abs(target_cdf - source_cdf[j]))
                lookup[j] = idx
            
            # Aplicar transformación
            result[:, :, i] = cv2.LUT(source_channel, lookup)
        
        return result
    
    def advanced_color_correction(self, source: np.ndarray, target: np.ndarray, 
                                 mask: np.ndarray) -> np.ndarray:
        """Corrección de color ultra avanzada usando múltiples técnicas combinadas."""
        # Método 1: Histogram matching mejorado
        hist_matched = self.histogram_matching(source, target, mask)
        
        # Método 2: Transformación LAB estadística mejorada
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        hist_matched_lab = cv2.cvtColor(hist_matched, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        mask_3d = np.stack([mask] * 3, axis=2)
        
        # Calcular estadísticas en región de cara con ponderación
        mask_weighted = mask ** 1.5  # Enfatizar centro de la cara
        mask_weighted_3d = np.stack([mask_weighted] * 3, axis=2)
        
        source_mean = np.sum(source_lab * mask_weighted_3d, axis=(0, 1)) / (np.sum(mask_weighted) + 1e-6)
        source_std = np.sqrt(np.sum(((source_lab - source_mean) ** 2) * mask_weighted_3d, axis=(0, 1)) / (np.sum(mask_weighted) + 1e-6)) + 1e-6
        
        # Calcular estadísticas del área circundante en target con múltiples anillos
        surrounding_mask = 1 - mask
        # Crear máscara de anillo exterior para mejor análisis del entorno
        ring_mask = cv2.GaussianBlur(surrounding_mask, (201, 201), 0)
        ring_mask = ring_mask * (1 - cv2.GaussianBlur(mask, (101, 101), 0))
        ring_mask_3d = np.stack([ring_mask] * 3, axis=2)
        
        target_mean = np.sum(target_lab * ring_mask_3d, axis=(0, 1)) / (np.sum(ring_mask) + 1e-6)
        target_std = np.sqrt(np.sum(((target_lab - target_mean) ** 2) * ring_mask_3d, axis=(0, 1)) / (np.sum(ring_mask) + 1e-6)) + 1e-6
        
        # Aplicar transformación de color con preservación de contraste
        corrected_lab = hist_matched_lab.copy()
        
        # Preservar contraste local mientras ajustamos color global
        source_contrast = source_std / (source_mean + 1e-6)
        target_contrast = target_std / (target_mean + 1e-6)
        contrast_ratio = np.clip(target_contrast / (source_contrast + 1e-6), 0.8, 1.2)
        
        corrected_lab = (corrected_lab - source_mean) * (target_std / source_std) * contrast_ratio + target_mean
        
        # Ajuste ultra avanzado del canal L (luminosidad) con blending adaptativo multi-nivel
        l_channel = corrected_lab[:, :, 0]
        target_l_channel = target_lab[:, :, 0]
        
        # Crear máscara de blending adaptativa multi-nivel para luminosidad
        l_mask_soft = cv2.GaussianBlur(mask, (51, 51), 0) * 0.6 + 0.4
        l_mask_hard = mask * 0.8 + 0.2
        
        # Blending multi-nivel
        l_blended = (l_channel * l_mask_hard + target_l_channel * (1 - l_mask_hard * 0.5)) * 0.7
        l_blended += (l_channel * l_mask_soft + target_l_channel * (1 - l_mask_soft * 0.3)) * 0.3
        corrected_lab[:, :, 0] = l_blended
        
        # Ajuste fino mejorado de canales A y B con preservación de tono de piel
        a_channel = corrected_lab[:, :, 1]
        b_channel = corrected_lab[:, :, 2]
        target_a = target_lab[:, :, 1]
        target_b = target_lab[:, :, 2]
        
        # Detectar tono de piel (valores típicos en LAB para piel)
        skin_mask = ((a_channel > 120) & (a_channel < 150) & (b_channel > 130) & (b_channel < 170)).astype(np.float32)
        skin_mask = cv2.GaussianBlur(skin_mask, (21, 21), 0)
        
        # Mezclar canales de color con preservación de tono de piel
        color_mask = mask * 0.85
        a_corrected = a_channel * color_mask + target_a * (1 - color_mask * 0.25)
        b_corrected = b_channel * color_mask + target_b * (1 - color_mask * 0.25)
        
        # Preservar tono de piel original donde sea apropiado
        a_final = a_corrected * (1 - skin_mask * 0.2) + a_channel * (skin_mask * 0.2)
        b_final = b_corrected * (1 - skin_mask * 0.2) + b_channel * (skin_mask * 0.2)
        
        corrected_lab[:, :, 1] = a_final
        corrected_lab[:, :, 2] = b_final
        
        corrected_lab = np.clip(corrected_lab, 0, 255)
        corrected = cv2.cvtColor(corrected_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        # Mezclar resultado de histogram matching con corrección LAB mejorada
        final = cv2.addWeighted(corrected, 0.65, hist_matched, 0.35, 0)
        
        # Aplicar corrección de brillo final sutil
        final_lab = cv2.cvtColor(final, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab_final = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Ajuste final de brillo en bordes
        edge_mask = cv2.Canny((mask * 255).astype(np.uint8), 50, 150) / 255.0
        edge_mask = cv2.dilate(edge_mask, np.ones((7, 7), np.uint8), iterations=1)
        edge_mask = cv2.GaussianBlur(edge_mask, (15, 15), 0)
        edge_mask_3d = np.stack([edge_mask] * 3, axis=2)
        
        # Suavizar transición de brillo en bordes
        final_lab[:, :, 0] = final_lab[:, :, 0] * (1 - edge_mask * 0.15) + target_lab_final[:, :, 0] * (edge_mask * 0.15)
        final = cv2.cvtColor(final_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        return final
    
    def poisson_blending_prep(self, source: np.ndarray, target: np.ndarray, 
                             mask: np.ndarray) -> np.ndarray:
        """Prepara para Poisson blending mejorado."""
        # Crear gradientes de la imagen fuente
        source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY).astype(np.float32)
        target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Calcular gradientes
        grad_x_source = cv2.Sobel(source_gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y_source = cv2.Sobel(source_gray, cv2.CV_32F, 0, 1, ksize=3)
        
        grad_x_target = cv2.Sobel(target_gray, cv2.CV_32F, 1, 0, ksize=3)
        grad_y_target = cv2.Sobel(target_gray, cv2.CV_32F, 0, 1, ksize=3)
        
        # Mezclar gradientes según la máscara
        grad_x = grad_x_source * mask + grad_x_target * (1 - mask)
        grad_y = grad_y_source * mask + grad_y_target * (1 - mask)
        
        # Reconstruir imagen desde gradientes (aproximación)
        # Esto es una simplificación del Poisson blending completo
        return grad_x, grad_y
    
    def preserve_skin_texture(self, source: np.ndarray, target: np.ndarray, 
                              mask: np.ndarray) -> np.ndarray:
        """Preserva la textura de la piel del target para mayor realismo."""
        # Convertir a escala de grises para análisis de textura
        source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY).astype(np.float32)
        target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Calcular textura usando filtros de alta frecuencia
        # Aplicar filtro Laplacian para detectar detalles finos
        source_detail = cv2.Laplacian(source_gray, cv2.CV_32F, ksize=3)
        target_detail = cv2.Laplacian(target_gray, cv2.CV_32F, ksize=3)
        
        # Preservar detalles de textura del target en la región de la cara
        # Esto mantiene los poros y textura natural del target
        detail_mask = cv2.GaussianBlur(mask, (15, 15), 0)
        preserved_detail = source_detail * (1 - detail_mask * 0.4) + target_detail * (detail_mask * 0.4)
        
        # Aplicar detalles preservados de vuelta
        kernel = np.array([[0, -1, 0],
                          [-1, 5, -1],
                          [0, -1, 0]])
        detail_enhanced = cv2.filter2D(target_gray, -1, kernel)
        
        # Mezclar textura preservada
        texture_blended = target_gray + preserved_detail * 0.3
        
        return texture_blended
    
    def transfer_illumination(self, source: np.ndarray, target: np.ndarray, 
                             mask: np.ndarray) -> np.ndarray:
        """Transfiere la iluminación del target al source para mayor realismo."""
        # Convertir a LAB
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Analizar iluminación del target (canal L)
        target_l = target_lab[:, :, 0]
        source_l = source_lab[:, :, 0]
        
        # Calcular gradientes de iluminación del target
        grad_x_target = cv2.Sobel(target_l, cv2.CV_32F, 1, 0, ksize=5)
        grad_y_target = cv2.Sobel(target_l, cv2.CV_32F, 0, 1, ksize=5)
        
        # Crear máscara de blending para iluminación
        illum_mask = cv2.GaussianBlur(mask, (101, 101), 0)
        
        # Transferir gradientes de iluminación
        grad_x_source = cv2.Sobel(source_l, cv2.CV_32F, 1, 0, ksize=5)
        grad_y_source = cv2.Sobel(source_l, cv2.CV_32F, 0, 1, ksize=5)
        
        # Mezclar gradientes (preservar iluminación del target en bordes)
        grad_x = grad_x_source * (1 - illum_mask * 0.6) + grad_x_target * (illum_mask * 0.6)
        grad_y = grad_y_source * (1 - illum_mask * 0.6) + grad_y_target * (illum_mask * 0.6)
        
        # Reconstruir canal L desde gradientes (aproximación)
        # Esto es una simplificación, pero ayuda a preservar iluminación
        source_l_transferred = source_l * (1 - illum_mask * 0.3) + target_l * (illum_mask * 0.3)
        
        source_lab[:, :, 0] = source_l_transferred
        result = cv2.cvtColor(source_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        return result
    
    def multi_scale_blending(self, source: np.ndarray, target: np.ndarray, 
                            mask: np.ndarray) -> np.ndarray:
        """Blending multi-escala ultra mejorado para máximo realismo."""
        # Transferir iluminación primero
        source_illum = self.transfer_illumination(source, target, mask)
        
        # Aplicar corrección de color
        source_corrected = self.advanced_color_correction(source_illum, target, mask)
        
        source_f = source_corrected.astype(np.float32)
        target_f = target.astype(np.float32)
        mask_3d = np.stack([mask] * 3, axis=2)
        
        # Blending básico
        blended_basic = source_f * mask_3d + target_f * (1 - mask_3d)
        
        # Blending con máscara suavizada adicional (múltiples niveles)
        mask_smooth1 = cv2.GaussianBlur(mask, (31, 31), 0)
        mask_smooth2 = cv2.GaussianBlur(mask, (61, 61), 0)
        mask_smooth3 = cv2.GaussianBlur(mask, (101, 101), 0)
        
        mask_smooth1_3d = np.stack([mask_smooth1] * 3, axis=2)
        mask_smooth2_3d = np.stack([mask_smooth2] * 3, axis=2)
        mask_smooth3_3d = np.stack([mask_smooth3] * 3, axis=2)
        
        blended_smooth1 = source_f * mask_smooth1_3d + target_f * (1 - mask_smooth1_3d)
        blended_smooth2 = source_f * mask_smooth2_3d + target_f * (1 - mask_smooth2_3d)
        blended_smooth3 = source_f * mask_smooth3_3d + target_f * (1 - mask_smooth3_3d)
        
        # Combinar múltiples niveles de blending
        final = (blended_basic * 0.4 + 
                blended_smooth1 * 0.3 + 
                blended_smooth2 * 0.2 + 
                blended_smooth3 * 0.1)
        
        # Preservar textura de piel del target
        texture_preserved = self.preserve_skin_texture(source_corrected, target, mask)
        texture_preserved_bgr = cv2.cvtColor(texture_preserved.astype(np.uint8), cv2.COLOR_GRAY2BGR).astype(np.float32)
        
        # Mezclar textura preservada sutilmente
        texture_mask = cv2.GaussianBlur(mask, (21, 21), 0)
        texture_mask_3d = np.stack([texture_mask] * 3, axis=2)
        
        # Extraer detalles de textura
        detail_diff = texture_preserved_bgr - target_f
        final = final + detail_diff * texture_mask_3d * 0.15
        
        # Aplicar corrección de bordes mejorada
        edge_mask = cv2.Canny((mask * 255).astype(np.uint8), 30, 100) / 255.0
        edge_mask = cv2.dilate(edge_mask, np.ones((7, 7), np.uint8), iterations=2)
        edge_mask = cv2.GaussianBlur(edge_mask, (21, 21), 0)
        edge_mask_3d = np.stack([edge_mask] * 3, axis=2)
        
        # Suavizar bordes de manera más agresiva
        final = final * (1 - edge_mask_3d * 0.4) + target_f * (edge_mask_3d * 0.4)
        
        # Preservar micro-details del target en la región de transición
        micro_mask = cv2.GaussianBlur(mask, (151, 151), 0)
        micro_mask = (1 - micro_mask) * 0.3  # Solo en área de transición
        micro_mask_3d = np.stack([micro_mask] * 3, axis=2)
        
        # Añadir detalles finos del target
        target_details = target_f - cv2.GaussianBlur(target_f, (5, 5), 0)
        final = final + target_details * micro_mask_3d
        
        final = np.clip(final, 0, 255)
        return final.astype(np.uint8)
    
    def enhance_face_quality(self, face: np.ndarray) -> np.ndarray:
        """Mejora la calidad de la cara extraída."""
        # Reducción de ruido preservando detalles
        face = cv2.bilateralFilter(face, 5, 50, 50)
        
        # Mejora de contraste adaptativo
        lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        face = cv2.merge([l, a, b])
        face = cv2.cvtColor(face, cv2.COLOR_LAB2BGR)
        
        return face
    
    def swap_faces(self, source_image: np.ndarray, target_image: np.ndarray) -> np.ndarray:
        """Intercambia caras con ultra calidad."""
        # Detectar caras
        source_face_rect = self.detect_face(source_image)
        target_face_rect = self.detect_face(target_image)
        
        if source_face_rect is None or target_face_rect is None:
            return target_image
        
        # Extraer regiones expandidas
        source_region, source_adj = self.extract_face_region(source_image, source_face_rect, expand=0.5)
        target_region, target_adj = self.extract_face_region(target_image, target_face_rect, expand=0.5)
        
        # Mejorar calidad de la cara fuente
        source_region = self.enhance_face_quality(source_region)
        
        # Calcular escala para alinear tamaños
        target_w = target_face_rect[2]
        target_h = target_face_rect[3]
        source_w = source_face_rect[2]
        source_h = source_face_rect[3]
        
        scale = max(target_w / source_w, target_h / source_h) * 1.15
        
        new_w = int(source_region.shape[1] * scale)
        new_h = int(source_region.shape[0] * scale)
        
        # Redimensionamiento ultra avanzado con preservación de calidad
        # Usar múltiples pasos para mejor calidad
        if scale > 1.5:
            # Para escalas grandes, hacer en múltiples pasos progresivos
            current_scale = 1.0
            current_img = source_region.copy()
            
            while current_scale < scale:
                next_scale = min(scale / current_scale, 1.5)  # Máximo 1.5x por paso
                next_w = int(current_img.shape[1] * next_scale)
                next_h = int(current_img.shape[0] * next_scale)
                
                # Aplicar sharpening antes de escalar para preservar detalles
                kernel = np.array([[0, -0.25, 0],
                                   [-0.25, 2, -0.25],
                                   [0, -0.25, 0]])
                sharpened = cv2.filter2D(current_img, -1, kernel)
                current_img = cv2.addWeighted(current_img, 0.9, sharpened, 0.1, 0)
                
                current_img = cv2.resize(current_img, (next_w, next_h),
                                        interpolation=cv2.INTER_LANCZOS4)
                current_scale *= next_scale
            
            source_resized = current_img
        elif scale < 0.7:
            # Para reducciones, también usar pasos múltiples
            current_scale = 1.0
            current_img = source_region.copy()
            
            while current_scale > scale:
                next_scale = max(scale / current_scale, 0.7)  # Mínimo 0.7x por paso
                next_w = int(current_img.shape[1] * next_scale)
                next_h = int(current_img.shape[0] * next_scale)
                
                current_img = cv2.resize(current_img, (next_w, next_h),
                                        interpolation=cv2.INTER_LANCZOS4)
                current_scale *= next_scale
            
            source_resized = current_img
        else:
            # Escala normal, usar LANCZOS4 directamente
            source_resized = cv2.resize(source_region, (new_w, new_h), 
                                       interpolation=cv2.INTER_LANCZOS4)
        
        # Ajustar si es muy grande (fallback)
        if new_w > target_region.shape[1] or new_h > target_region.shape[0]:
            scale_factor = min(
                target_region.shape[1] / new_w,
                target_region.shape[0] / new_h
            )
            new_w = int(new_w * scale_factor)
            new_h = int(new_h * scale_factor)
            source_resized = cv2.resize(source_resized, (new_w, new_h),
                                      interpolation=cv2.INTER_LANCZOS4)
        
        # Centrar en la región target
        source_aligned = np.zeros_like(target_region)
        offset_x = (target_region.shape[1] - new_w) // 2
        offset_y = (target_region.shape[0] - new_h) // 2
        
        source_aligned[offset_y:offset_y+new_h, offset_x:offset_x+new_w] = source_resized
        
        # Crear máscara avanzada
        mask_rect = (
            offset_x + int(new_w * 0.1),
            offset_y + int(new_h * 0.1),
            int(new_w * 0.8),
            int(new_h * 0.8)
        )
        
        mask = self.create_advanced_mask(target_region.shape[:2], mask_rect)
        
        # Aplicar corrección de color avanzada
        source_corrected = self.advanced_color_correction(source_aligned, target_region, mask)
        
        # Blending multi-escala
        blended = self.multi_scale_blending(source_corrected, target_region, mask)
        
        # Seamless cloning ultra mejorado para integración perfecta
        try:
            mask_uint8 = (mask * 255).astype(np.uint8)
            
            # Mejorar máscara para seamless cloning
            # Dilatar ligeramente para mejor integración
            mask_dilated = cv2.dilate(mask_uint8, np.ones((5, 5), np.uint8), iterations=1)
            mask_dilated = cv2.GaussianBlur(mask_dilated, (15, 15), 0)
            
            # Calcular centro óptimo (no siempre el centro geométrico)
            moments = cv2.moments(mask_uint8)
            if moments["m00"] != 0:
                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                center = (center_x, center_y)
            else:
                center = (target_region.shape[1] // 2, target_region.shape[0] // 2)
            
            # Probar múltiples métodos de seamless cloning con mejoras
            try:
                # Método NORMAL_CLONE (mejor para caras)
                blended = cv2.seamlessClone(source_corrected, target_region, mask_dilated, 
                                           center, cv2.NORMAL_CLONE)
                
                # Mejorar resultado de seamless cloning
                # Mezclar sutilmente con blending manual para preservar detalles
                blended_f = blended.astype(np.float32)
                manual_blend_f = self.multi_scale_blending(source_corrected, target_region, mask).astype(np.float32)
                
                # Usar seamless cloning como base, pero preservar detalles del blending manual
                detail_mask = cv2.GaussianBlur(mask, (11, 11), 0)
                detail_mask_3d = np.stack([detail_mask] * 3, axis=2)
                
                # Preservar detalles finos del blending manual
                details = manual_blend_f - cv2.GaussianBlur(manual_blend_f, (3, 3), 0)
                blended = blended_f + details * detail_mask_3d * 0.3
                blended = np.clip(blended, 0, 255).astype(np.uint8)
                
            except:
                try:
                    # Fallback a MIXED_CLONE
                    blended = cv2.seamlessClone(source_corrected, target_region, mask_dilated, 
                                               center, cv2.MIXED_CLONE)
                except:
                    # Si falla, usar blending manual mejorado
                    blended = self.multi_scale_blending(source_corrected, target_region, mask)
        except:
            # Fallback final a blending manual
            blended = self.multi_scale_blending(source_corrected, target_region, mask)
        
        # Post-procesamiento final ultra mejorado para máximo realismo
        # Preservar detalles finos antes de procesar
        blended_original = blended.copy()
        blended_blurred = cv2.GaussianBlur(blended, (3, 3), 0)
        fine_details = blended.astype(np.float32) - blended_blurred.astype(np.float32)
        
        # Reducción de ruido preservando detalles (múltiples pasos)
        blended = cv2.bilateralFilter(blended, 7, 60, 60)
        blended = cv2.bilateralFilter(blended, 5, 40, 40)
        
        # Restaurar detalles finos
        blended = blended.astype(np.float32) + fine_details * 0.7
        blended = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Mejora de bordes mejorada con análisis de textura
        lab = cv2.cvtColor(blended, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Ecualización adaptativa mejorada del canal L
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Mejora de saturación adaptativa con preservación de tonos naturales
        a_f = a.astype(np.float32)
        b_f = b.astype(np.float32)
        
        # Detectar y preservar tonos de piel
        skin_tones = ((a_f > 120) & (a_f < 150) & (b_f > 130) & (b_f < 170))
        a = np.where(skin_tones,
                    np.clip(a_f * 1.01, 0, 255),  # Muy sutil en piel
                    np.clip(a_f * 1.03, 0, 255)).astype(np.uint8)
        b = np.where(skin_tones,
                    np.clip(b_f * 1.01, 0, 255),  # Muy sutil en piel
                    np.clip(b_f * 1.03, 0, 255)).astype(np.uint8)
        
        blended = cv2.merge([l, a, b])
        blended = cv2.cvtColor(blended, cv2.COLOR_LAB2BGR)
        
        # Sharpening adaptativo ultra mejorado con preservación de textura natural
        gray = cv2.cvtColor(blended, cv2.COLOR_BGR2GRAY)
        
        # Detectar textura (áreas con variación)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_mask = np.abs(laplacian)
        texture_mask = cv2.GaussianBlur(texture_mask, (5, 5), 0)
        texture_max = texture_mask.max()
        if texture_max > 0:
            texture_mask = np.clip(texture_mask / texture_max, 0, 1)
        else:
            texture_mask = np.zeros_like(texture_mask)
        texture_mask_3d = np.stack([texture_mask] * 3, axis=2)
        
        # Aplicar sharpening más fuerte en áreas con textura, pero preservar suavidad natural
        kernel_strong = np.array([[-0.3, -0.8, -0.3],
                                  [-0.8,  7.2, -0.8],
                                  [-0.3, -0.8, -0.3]]) / 2.0
        kernel_soft = np.array([[0, -0.15, 0],
                                 [-0.15, 1.6, -0.15],
                                 [0, -0.15, 0]])
        
        sharpened_strong = cv2.filter2D(blended, -1, kernel_strong)
        sharpened_soft = cv2.filter2D(blended, -1, kernel_soft)
        
        # Mezclar según textura, pero más conservador
        blended_f = blended.astype(np.float32)
        sharp_strong_f = sharpened_strong.astype(np.float32)
        sharp_soft_f = sharpened_soft.astype(np.float32)
        
        blended = (blended_f * (1 - texture_mask_3d * 0.12) + 
                  sharp_strong_f * (texture_mask_3d * 0.08) + 
                  sharp_soft_f * (texture_mask_3d * 0.04))
        blended = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Preservar coherencia de textura con el target original
        target_region_gray = cv2.cvtColor(target_region, cv2.COLOR_BGR2GRAY).astype(np.float32)
        blended_gray = cv2.cvtColor(blended, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Extraer textura del target
        target_texture = target_region_gray - cv2.GaussianBlur(target_region_gray, (5, 5), 0)
        blended_texture = blended_gray - cv2.GaussianBlur(blended_gray, (5, 5), 0)
        
        # Mezclar texturas sutilmente en área de transición
        transition_mask = cv2.GaussianBlur(1 - mask, (51, 51), 0)
        transition_mask = transition_mask * 0.2  # Solo 20% de mezcla
        
        final_texture = blended_texture * (1 - transition_mask) + target_texture * transition_mask
        blended_gray_final = cv2.GaussianBlur(blended_gray, (5, 5), 0) + final_texture
        
        # Convertir de vuelta a BGR manteniendo canales de color
        blended_lab = cv2.cvtColor(blended, cv2.COLOR_BGR2LAB)
        blended_lab[:, :, 0] = np.clip(blended_gray_final, 0, 255).astype(np.uint8)
        blended = cv2.cvtColor(blended_lab, cv2.COLOR_LAB2BGR)
        
        # Reducción final de ruido muy sutil (preservar textura)
        blended = cv2.bilateralFilter(blended, 3, 20, 20)
        
        # Insertar de vuelta en la imagen original
        result = target_image.copy()
        x_exp = max(0, target_face_rect[0] - int(target_face_rect[2] * 0.5))
        y_exp = max(0, target_face_rect[1] - int(target_face_rect[3] * 0.5))
        
        h_blended, w_blended = blended.shape[:2]
        result[y_exp:y_exp+h_blended, x_exp:x_exp+w_blended] = blended
        
        return result


def batch_ultra_quality_swap():
    """Procesa todas las imágenes con face swap de ultra calidad."""
    from pathlib import Path
    import random
    
    print("=" * 70)
    print("FACE SWAP ULTRA CALIDAD: BUNNY -> 69CAYLIN")
    print("=" * 70)
    
    # Obtener imágenes
    bunny_dirs = [
        "instagram_downloads/bunnyrose.me",
        "instagram_downloads/bunnyrose.uwu",
        "instagram_downloads/bunnyy.rose_"
    ]
    
    all_bunny_faces = []
    for dir_path in bunny_dirs:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            jpg_files = list(dir_obj.glob("*.jpg"))
            all_bunny_faces.extend(jpg_files)
    
    caylin_dir = Path("instagram_downloads/69caylin")
    caylin_images = list(caylin_dir.glob("*.jpg")) if caylin_dir.exists() else []
    
    if len(all_bunny_faces) == 0 or len(caylin_images) == 0:
        print("Error: No se encontraron imagenes suficientes")
        return
    
    print(f"Encontradas {len(all_bunny_faces)} caras de bunny")
    print(f"Encontradas {len(caylin_images)} imagenes de 69caylin")
    
    # Crear carpeta de salida
    output_dir = Path("face_swap_results_bunny_to_69caylin")
    output_dir.mkdir(exist_ok=True)
    
    # Inicializar face swap ultra calidad
    print("\nInicializando face swap de ultra calidad...")
    face_swapper = UltraQualityFaceSwap()
    
    print(f"\nProcesando {len(caylin_images)} imagenes...")
    print("-" * 70)
    
    successful = 0
    failed = 0
    
    for idx, caylin_img_path in enumerate(caylin_images, 1):
        try:
            bunny_face_path = random.choice(all_bunny_faces)
            
            bunny_img = cv2.imread(str(bunny_face_path))
            caylin_img = cv2.imread(str(caylin_img_path))
            
            if bunny_img is None or caylin_img is None:
                failed += 1
                continue
            
            # Face swap ultra calidad
            result = face_swapper.swap_faces(bunny_img, caylin_img)
            
            # Guardar con máxima calidad
            output_filename = f"bunny_face_on_{caylin_img_path.stem}.jpg"
            output_path = output_dir / output_filename
            
            # Guardar con máxima calidad ultra mejorada
            # Usar calidad 100 (máxima) para preservar todos los detalles
            cv2.imwrite(str(output_path), result, 
                       [cv2.IMWRITE_JPEG_QUALITY, 100,
                        cv2.IMWRITE_JPEG_OPTIMIZE, 1])
            
            successful += 1
            if idx % 50 == 0:
                print(f"[{idx}/{len(caylin_images)}] Procesadas...")
            
        except Exception as e:
            print(f"Error en {caylin_img_path.name}: {e}")
            failed += 1
            continue
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print(f"Imagenes procesadas: {successful}")
    print(f"Errores: {failed}")
    print(f"Resultados en: {output_dir.absolute()}")


if __name__ == "__main__":
    batch_ultra_quality_swap()








